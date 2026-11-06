"""
Imágenes: enseñar fotos y dibujos en la terminal (PNG, JPG, GIF, BMP, PPM).

    pantalla.imagen("gato.png")                  # donde esté el cursor, como un print
    pantalla.imagen("gato.jpg", 5, 2, ancho=40)  # en la columna 5, fila 2, de 40 columnas

Si la terminal sabe pintar imágenes (Windows Terminal, WezTerm, kitty, Ghostty, iTerm2,
foot, Konsole...) sale la foto de verdad. Si no (cmd, la Terminal del Mac...), sale con
medios bloques ▀ de colores, que también se ve bastante bien.

No hace falta instalar nada. Si tienes Pillow (pip install pillow), se usa para abrir
las fotos más rápido y abre más tipos (WEBP, JPG progresivos...).
"""

import base64
import math
import os
import re
import struct
import sys
import time
import zlib
from array import array
from collections import Counter
from itertools import accumulate

from .terminal import _fin_de_estilo, _salida

_FONDO = (12, 12, 12)


class _Pixeles(object):
    """Una imagen ya abierta: un bytearray por canal (rojo, verde, azul y alfa)."""

    def __init__(self, W, H, R, G, B, A=None):
        self.W, self.H = W, H
        self.R, self.G, self.B = bytearray(R), bytearray(G), bytearray(B)
        self.A = bytearray(A) if A is not None else bytearray(b"\xff") * (W * H)


# --- abrir ---------------------------------------------------------------------

def _leer(ruta):
    if isinstance(ruta, (_Pixeles, bytes, bytearray)):
        return ruta
    if not isinstance(ruta, (str, os.PathLike)):
        raise TypeError("imagen: dame el nombre del archivo, como \"gato.png\", y me has dado %r" % (ruta,))
    nombre = os.fspath(ruta)
    try:
        with open(nombre, "rb") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError("imagen: no encuentro el archivo %r" % nombre) from None


def _medida_jpeg(datos):
    """(ancho, alto) de un JPG mirando solo la cabecera (ya girado si es una foto de lado)."""
    if not isinstance(datos, bytes) or datos[:2] != b"\xff\xd8":
        return None
    pos, orientacion = 2, 1
    while pos + 4 < len(datos):
        if datos[pos] != 0xFF:
            return None
        m = datos[pos + 1]
        largo = int.from_bytes(datos[pos + 2:pos + 4], "big")
        if m == 0xE1:
            try:
                orientacion = _orientacion(datos[pos + 4:pos + 2 + largo])
            except (IndexError, ValueError):
                pass
        if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            H, W = struct.unpack(">HH", datos[pos + 5:pos + 9])
            return (H, W) if orientacion in (6, 8) else (W, H)
        pos += 2 + largo
    return None


def _abrir(ruta, minimo=None):
    """Abre una imagen (ruta o bytes). minimo=(w, h): no hace falta más grande que eso (los JPG
    se pueden abrir ya pequeños, que es mucho más rápido)."""
    datos = _leer(ruta)
    if isinstance(datos, _Pixeles):
        return datos
    datos = bytes(datos)
    nombre = repr(os.fspath(ruta)) if isinstance(ruta, (str, os.PathLike)) else "la imagen"
    con_pillow = _con_pillow(datos, minimo)
    if con_pillow is not None:
        return con_pillow
    try:
        if datos[:8] == b"\x89PNG\r\n\x1a\n":
            p = _png(datos)
        elif datos[:2] == b"\xff\xd8":
            p = _jpeg(datos, minimo)
        elif datos[:3] == b"GIF":
            p = _gif(datos)
        elif datos[:2] == b"BM":
            p = _bmp(datos)
        elif datos[:1] == b"P" and datos[1:2] in b"123456":
            p = _ppm(datos)
        else:
            raise ValueError("imagen: %s no es PNG, JPG, GIF, BMP ni PPM (para otros tipos instala Pillow: "
                             "pip install pillow)" % nombre)
    except (IndexError, struct.error, zlib.error, KeyError):
        raise ValueError("imagen: %s está rota o no la sé leer" % nombre) from None
    return p


def _con_pillow(datos, minimo):
    try:
        import io
        from PIL import Image, ImageOps
    except Exception:
        return None
    try:
        im = Image.open(io.BytesIO(datos))
        if minimo and im.format == "JPEG":
            im.draft("RGB", minimo)
        im = ImageOps.exif_transpose(im).convert("RGBA")
    except Exception:
        return None
    r, g, b, a = im.split()
    return _Pixeles(im.width, im.height, r.tobytes(), g.tobytes(), b.tobytes(), a.tobytes())


def _bits(profundidad):
    # cada byte partido en sus valores de 1, 2 o 4 bits
    por = 8 // profundidad
    m = (1 << profundidad) - 1
    return [bytes((b >> (8 - profundidad * (k + 1))) & m for k in range(por)) for b in range(256)]


_TABLAS_BITS = {}


def _desempaquetar(fila, n, profundidad):
    if profundidad == 8:
        return bytes(fila[:n])
    if profundidad not in _TABLAS_BITS:
        _TABLAS_BITS[profundidad] = _bits(profundidad)
    return b"".join(map(_TABLAS_BITS[profundidad].__getitem__, fila))[:n]


_MASCARAS = {}


def _sumar_bytes(a, b):
    # suma byte a byte (módulo 256) de dos tiras iguales, de golpe con enteros grandes
    n = len(a)
    if n not in _MASCARAS:
        _MASCARAS[n] = (int.from_bytes(b"\x7f" * n, "little"), int.from_bytes(b"\x80" * n, "little"))
    m7, m8 = _MASCARAS[n]
    x, y = int.from_bytes(a, "little"), int.from_bytes(b, "little")
    return bytearray((((x & m7) + (y & m7)) ^ ((x ^ y) & m8)).to_bytes(n, "little"))


def _desfiltrar(crudo, pos, W, H, bits_pixel):
    bpp = max(1, bits_pixel // 8)
    largo = (W * bits_pixel + 7) // 8
    previa = bytearray(largo)
    filas = []
    for _ in range(H):
        f = crudo[pos]
        fila = bytearray(crudo[pos + 1:pos + 1 + largo])
        pos += 1 + largo
        if f == 1:
            for c in range(bpp):
                fila[c::bpp] = bytes(accumulate(fila[c::bpp], lambda a, b: (a + b) & 255))
        elif f == 2:
            fila = _sumar_bytes(fila, previa)
        elif f == 3:
            for i in range(largo):
                izq = fila[i - bpp] if i >= bpp else 0
                fila[i] = (fila[i] + ((izq + previa[i]) >> 1)) & 255
        elif f == 4:
            for i in range(largo):
                if i >= bpp:
                    a, c = fila[i - bpp], previa[i - bpp]
                else:
                    a = c = 0
                b = previa[i]
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                if pa <= pb and pa <= pc:
                    pred = a
                elif pb <= pc:
                    pred = b
                else:
                    pred = c
                fila[i] = (fila[i] + pred) & 255
        filas.append(fila)
        previa = fila
    return filas, pos


def _png(datos):
    pos = 8
    idat, plte, trns = [], None, None
    while pos + 8 <= len(datos):
        n = int.from_bytes(datos[pos:pos + 4], "big")
        tipo, cuerpo = datos[pos + 4:pos + 8], datos[pos + 8:pos + 8 + n]
        pos += 12 + n
        if tipo == b"IHDR":
            W, H, prof, ctipo, _, _, entrelazado = struct.unpack(">IIBBBBB", cuerpo[:13])
        elif tipo == b"PLTE":
            plte = cuerpo
        elif tipo == b"tRNS":
            trns = cuerpo
        elif tipo == b"IDAT":
            idat.append(cuerpo)
        elif tipo == b"IEND":
            break
    crudo = zlib.decompress(b"".join(idat))
    canales = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctipo]
    bits_pixel = canales * prof
    if not entrelazado:
        filas, _ = _desfiltrar(crudo, 0, W, H, bits_pixel)
        return _png_a_pixeles(filas, W, H, prof, ctipo, plte, trns)
    p = _Pixeles(W, H, bytes(W * H), bytes(W * H), bytes(W * H), bytes(W * H))
    pos = 0
    # adam7: siete pasadas, cada una con sus filas y columnas
    for x0, y0, dx, dy in ((0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4), (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2)):
        pw, ph = (W - x0 + dx - 1) // dx, (H - y0 + dy - 1) // dy
        if pw <= 0 or ph <= 0:
            continue
        filas, pos = _desfiltrar(crudo, pos, pw, ph, bits_pixel)
        trozo = _png_a_pixeles(filas, pw, ph, prof, ctipo, plte, trns)
        for k in range(ph):
            y = y0 + k * dy
            a, b = y * W + x0, y * W + W
            for canal, sub in ((p.R, trozo.R), (p.G, trozo.G), (p.B, trozo.B), (p.A, trozo.A)):
                canal[a:b:dx] = sub[k * pw:(k + 1) * pw]
    return p


def _png_a_pixeles(filas, W, H, prof, ctipo, plte, trns):
    canales = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctipo]
    if prof == 16:
        datos = b"".join(bytes(f[0::2]) for f in filas)
    elif prof == 8:
        datos = b"".join(bytes(f) for f in filas)
    else:
        datos = b"".join(_desempaquetar(f, W, prof) for f in filas)
    if ctipo == 3:
        tabla = (plte or b"") + bytes(768)
        r, g, b = bytes(tabla[0:768:3]), bytes(tabla[1:768:3]), bytes(tabla[2:768:3])
        alfa = (trns or b"")[:256] + b"\xff" * 256
        return _Pixeles(W, H, datos.translate(r), datos.translate(g), datos.translate(b), datos.translate(alfa[:256]))
    if ctipo in (0, 4):
        gris = datos[0::canales]
        if prof < 8:
            gris = gris.translate(bytes(min(255, v * 255 // ((1 << prof) - 1)) for v in range(256)))
        if ctipo == 4:
            alfa = datos[1::2]
        elif trns and len(trns) >= 2:
            t = int.from_bytes(trns[:2], "big")
            t = t >> 8 if prof == 16 else t * 255 // ((1 << prof) - 1) if prof < 8 else t
            alfa = gris.translate(bytes(0 if v == t else 255 for v in range(256)))
        else:
            alfa = None
        return _Pixeles(W, H, gris, gris, gris, alfa)
    alfa = datos[3::4] if ctipo == 6 else None
    return _Pixeles(W, H, datos[0::canales], datos[1::canales], datos[2::canales], alfa)


def _gif(datos):
    W, H, flags = struct.unpack("<HHB", datos[6:11])
    pos = 13
    paleta = None
    if flags & 0x80:
        n = 3 * (2 << (flags & 7))
        paleta, pos = datos[pos:pos + n], pos + n
    transparente = None
    while pos < len(datos):
        b = datos[pos]
        if b == 0x21:
            etiqueta = datos[pos + 1]
            pos += 2
            if etiqueta == 0xF9 and datos[pos] >= 4 and datos[pos + 1] & 1:
                transparente = datos[pos + 4]
            while datos[pos]:
                pos += datos[pos] + 1
            pos += 1
        elif b == 0x2C:
            x0, y0, w, h, fl = struct.unpack("<HHHHB", datos[pos + 1:pos + 10])
            pos += 10
            local = paleta
            if fl & 0x80:
                n = 3 * (2 << (fl & 7))
                local, pos = datos[pos:pos + n], pos + n
            minimo = datos[pos]
            pos += 1
            trozos = []
            while datos[pos]:
                trozos.append(datos[pos + 1:pos + 1 + datos[pos]])
                pos += datos[pos] + 1
            indices = _lzw(b"".join(trozos), minimo, w * h)
            if fl & 0x40:
                orden = [y for paso, ini in ((8, 0), (8, 4), (4, 2), (2, 1)) for y in range(ini, h, paso)]
                filas = [indices[k * w:(k + 1) * w] for k in range(h)]
                nuevas = [None] * h
                for k, y in enumerate(orden):
                    nuevas[y] = filas[k]
                indices = b"".join(nuevas)
            tabla = (local or b"") + bytes(768)
            alfa = bytearray(b"\xff") * 256
            if transparente is not None:
                alfa[transparente] = 0
            p = _Pixeles(W, H, bytes(W * H), bytes(W * H), bytes(W * H), bytes(W * H))
            for k in range(min(h, H - y0)):
                fila = indices[k * w:(k + 1) * w][:max(0, W - x0)]
                a = (y0 + k) * W + x0
                p.R[a:a + len(fila)] = fila.translate(bytes(tabla[0:768:3]))
                p.G[a:a + len(fila)] = fila.translate(bytes(tabla[1:768:3]))
                p.B[a:a + len(fila)] = fila.translate(bytes(tabla[2:768:3]))
                p.A[a:a + len(fila)] = fila.translate(bytes(alfa))
            return p
        else:
            break
    raise ValueError("imagen: el GIF no tiene ninguna imagen dentro")


def _lzw(datos, minimo, total):
    limpiar, fin = 1 << minimo, (1 << minimo) + 1
    base = [bytes([i]) for i in range(limpiar)] + [b"", b""]
    tabla = list(base)
    tam = minimo + 1
    salida = bytearray()
    previo = None
    p, maximo = 0, len(datos) * 8
    datos = datos + b"\x00\x00\x00"
    while p + tam <= maximo and len(salida) < total:
        codigo = (int.from_bytes(datos[p >> 3:(p >> 3) + 3], "little") >> (p & 7)) & ((1 << tam) - 1)
        p += tam
        if codigo == limpiar:
            tabla = list(base)
            tam = minimo + 1
            previo = None
            continue
        if codigo == fin:
            break
        if previo is None:
            trozo = tabla[codigo]
        elif codigo < len(tabla):
            trozo = tabla[codigo]
            if len(tabla) < 4096:
                tabla.append(previo + trozo[:1])
        else:
            trozo = previo + previo[:1]
            if len(tabla) < 4096:
                tabla.append(trozo)
        salida += trozo
        previo = trozo
        if len(tabla) == (1 << tam) and tam < 12:
            tam += 1
    salida += bytes(max(0, total - len(salida)))
    return bytes(salida[:total])


def _bmp(datos):
    inicio = int.from_bytes(datos[10:14], "little")
    cab = int.from_bytes(datos[14:18], "little")
    if cab == 12:
        W, H = struct.unpack("<HH", datos[18:22])
        bits, compresion = struct.unpack("<H", datos[24:26])[0], 0
    else:
        W, H, _, bits, compresion = struct.unpack("<iiHHI", datos[18:34])
    de_abajo = H > 0
    H = abs(H)
    if compresion not in (0, 3):
        raise ValueError("imagen: los BMP comprimidos no los sé abrir; guárdalo como PNG")
    largo = ((W * bits + 31) // 32) * 4
    filas = [datos[inicio + k * largo:inicio + (k + 1) * largo] for k in range(H)]
    if de_abajo:
        filas.reverse()
    if bits in (24, 32):
        paso = bits // 8
        todo = b"".join(f[:W * paso] for f in filas)
        alfa = todo[3::4] if bits == 32 else None
        if alfa is not None and not any(alfa):
            alfa = None
        return _Pixeles(W, H, todo[2::paso], todo[1::paso], todo[0::paso], alfa)
    if bits in (1, 4, 8):
        n = int.from_bytes(datos[46:50], "little") if cab >= 40 else 0
        n = n or (1 << bits)
        tam = 3 if cab == 12 else 4
        pal = datos[14 + cab:14 + cab + n * tam]
        tabla = [bytes(pal[c:n * tam:tam]) + bytes(256) for c in (2, 1, 0)]
        indices = b"".join(_desempaquetar(f, W, bits) for f in filas)
        return _Pixeles(W, H, *(indices.translate(t[:256]) for t in tabla))
    if bits == 16:
        R, G, B = bytearray(W * H), bytearray(W * H), bytearray(W * H)
        for y, f in enumerate(filas):
            for x in range(W):
                v = f[2 * x] | (f[2 * x + 1] << 8)
                i = y * W + x
                R[i], G[i], B[i] = ((v >> 10) & 31) * 255 // 31, ((v >> 5) & 31) * 255 // 31, (v & 31) * 255 // 31
        return _Pixeles(W, H, R, G, B)
    raise ValueError("imagen: este BMP de %d bits no lo sé abrir" % bits)


def _ppm(datos):
    tipo = datos[1:2]
    trozos, pos = [], 2
    cuantos = 2 if tipo in b"14" else 3
    while len(trozos) < cuantos:
        while datos[pos:pos + 1].isspace():
            pos += 1
        if datos[pos:pos + 1] == b"#":
            pos = datos.index(b"\n", pos)
            continue
        fin = pos
        while not datos[fin:fin + 1].isspace():
            fin += 1
        trozos.append(int(datos[pos:fin]))
        pos = fin
    W, H = trozos[0], trozos[1]
    maximo = trozos[2] if cuantos == 3 else 1
    if tipo in b"123":
        numeros = [int(t) for t in datos[pos:].split()]
    else:
        pos += 1
        cuerpo = datos[pos:]
        if tipo == b"4":
            largo = (W + 7) // 8
            numeros = b"".join(_desempaquetar(cuerpo[k * largo:(k + 1) * largo], W, 1) for k in range(H))
        elif maximo > 255:
            numeros = cuerpo[0::2]
        else:
            numeros = cuerpo
    if tipo in b"14":
        v = bytes(0 if n else 255 for n in numeros[:W * H])
        return _Pixeles(W, H, v, v, v)
    escala = 255.0 / maximo
    if maximo > 255 and tipo in b"56":
        escala = 1.0
    v = bytes(min(255, int(n * escala + 0.5)) for n in numeros)
    if tipo in b"25":
        return _Pixeles(W, H, v[:W * H], v[:W * H], v[:W * H])
    return _Pixeles(W, H, v[0:3 * W * H:3], v[1:3 * W * H:3], v[2:3 * W * H:3])


# --- JPG (el normal, no el progresivo) ---------------------------------------------

_ZIGZAG = [0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5, 12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7,
           14, 21, 28, 35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51, 58, 59, 52, 45, 38, 31, 39, 46,
           53, 60, 61, 54, 47, 55, 62, 63]
_FIN_DATOS = re.compile(rb"\xff[^\x00\xd0-\xd7]")
_REINICIO = re.compile(rb"\xff[\xd0-\xd7]")


def _huffman(cuantos, simbolos):
    # una tabla de 65536 para mirar 16 bits de golpe: (lo que mide el código, el símbolo)
    tabla = [(16, 0)] * 65536
    codigo, k = 0, 0
    for largo in range(1, 17):
        for _ in range(cuantos[largo - 1]):
            a = codigo << (16 - largo)
            b = (codigo + 1) << (16 - largo)
            tabla[a:b] = [(largo, simbolos[k])] * (b - a)
            codigo += 1
            k += 1
        codigo <<= 1
    return tabla


def _idct(n):
    # la IDCT de 8 reducida a n puntos: con los coeficientes bajos sale la imagen ya pequeña
    return [[(math.sqrt(0.5) if u == 0 else 1.0) / 2 * math.cos((2 * x + 1) * u * math.pi / (2 * n)) for u in range(n)]
            for x in range(n)]


def _orientacion(segmento):
    # la de las fotos del móvil: 3 al revés, 6 y 8 de lado
    if segmento[:6] != b"Exif\x00\x00":
        return 1
    t = segmento[6:]
    orden = "little" if t[:2] == b"II" else "big"
    pos = int.from_bytes(t[4:8], orden)
    for k in range(int.from_bytes(t[pos:pos + 2], orden)):
        e = t[pos + 2 + 12 * k:pos + 14 + 12 * k]
        if int.from_bytes(e[0:2], orden) == 0x112:
            return int.from_bytes(e[8:10], orden)
    return 1


def _jpeg(datos, minimo=None):
    pos = 2
    cuant, tablas, comps = {}, {}, []
    reinicio, adobe, orientacion = 0, None, 1
    W = H = 0
    while pos < len(datos):
        if datos[pos] != 0xFF:
            pos += 1
            continue
        m = datos[pos + 1]
        pos += 2
        if m in (0xD8, 0x01, 0xFF) or 0xD0 <= m <= 0xD7:
            if m == 0xFF:
                pos -= 1
            continue
        if m == 0xD9:
            break
        largo = int.from_bytes(datos[pos:pos + 2], "big")
        seg = datos[pos + 2:pos + largo]
        pos += largo
        if m == 0xDB:
            i = 0
            while i < len(seg):
                pq, tq = seg[i] >> 4, seg[i] & 15
                if pq:
                    cuant[tq] = [int.from_bytes(seg[i + 1 + 2 * k:i + 3 + 2 * k], "big") for k in range(64)]
                    i += 129
                else:
                    cuant[tq] = list(seg[i + 1:i + 65])
                    i += 65
        elif m == 0xC4:
            i = 0
            while i < len(seg):
                clase, cual = seg[i] >> 4, seg[i] & 15
                cuantos = list(seg[i + 1:i + 17])
                n = sum(cuantos)
                tablas[(clase, cual)] = _huffman(cuantos, list(seg[i + 17:i + 17 + n]))
                i += 17 + n
        elif m in (0xC0, 0xC1):
            H, W = struct.unpack(">HH", seg[1:5])
            comps = [(seg[6 + 3 * k], seg[7 + 3 * k] >> 4, seg[7 + 3 * k] & 15, seg[8 + 3 * k]) for k in range(seg[5])]
        elif 0xC2 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            raise ValueError("imagen: este JPG es de los progresivos y no lo sé abrir sin Pillow "
                             "(pip install pillow), o guárdalo como PNG")
        elif m == 0xDD:
            reinicio = int.from_bytes(seg[:2], "big")
        elif m == 0xE1 and orientacion == 1:
            try:
                orientacion = _orientacion(seg)
            except (IndexError, ValueError):
                orientacion = 1
        elif m == 0xEE and seg[:5] == b"Adobe":
            adobe = seg[11]
        elif m == 0xDA:
            if not comps:
                raise ValueError("imagen: el JPG no dice cuánto mide")
            fin = _FIN_DATOS.search(datos, pos)
            fin = fin.start() if fin else len(datos)
            de_cada = {seg[1 + 2 * k]: (seg[2 + 2 * k] >> 4, seg[2 + 2 * k] & 15) for k in range(seg[0])}
            if len(de_cada) != len(comps):
                raise ValueError("imagen: este JPG viene por partes y no lo sé abrir sin Pillow (pip install pillow)")
            p = _escaneo(datos[pos:fin], W, H, comps, de_cada, cuant, tablas, reinicio, adobe, minimo)
            return _girar(p, orientacion)
    raise ValueError("imagen: el JPG está vacío")


def _escaneo(datos, W, H, comps, de_cada, cuant, tablas, reinicio, adobe, minimo):
    hmax = max(c[1] for c in comps)
    vmax = max(c[2] for c in comps)
    mx = (W + 8 * hmax - 1) // (8 * hmax)
    my = (H + 8 * vmax - 1) // (8 * vmax)
    # cuántos píxeles por bloque de 8: si la quieres pequeña no hace falta sacarla entera
    n = 8
    if minimo:
        for prueba in (1, 2, 4):
            if W * prueba >= 8 * minimo[0] and H * prueba >= 8 * minimo[1]:
                n = prueba
                break
    A = _idct(n)
    planos, info = [], []
    for cid, h, v, tq in comps:
        ancho_b, alto_b = mx * h, my * v
        planos.append(bytearray(ancho_b * n * alto_b * n))
        dc, ac = de_cada[cid]
        info.append((h, v, cuant[tq], tablas[(0, dc)], tablas[(1, ac)], ancho_b * n))
    segmentos = [s.replace(b"\xff\x00", b"\xff") + b"\x00\x00\x00\x00" for s in _REINICIO.split(datos)]
    zz = _ZIGZAG
    rango = range(n)
    total = mx * my
    mcu = 0
    for seg in segmentos:
        p = 0
        pred = [0] * len(comps)
        cuantos = reinicio or total
        while cuantos and mcu < total:
            cuantos -= 1
            fy, fx = divmod(mcu, mx)
            mcu += 1
            for ci, (h, v, q, tdc, tac, ancho_px) in enumerate(info):
                plano = planos[ci]
                for by in range(v):
                    for bx in range(h):
                        # el DC
                        i = p >> 3
                        largo, s = tdc[((seg[i] << 16 | seg[i + 1] << 8 | seg[i + 2]) >> (8 - (p & 7))) & 0xFFFF]
                        p += largo
                        if s:
                            i = p >> 3
                            val = ((seg[i] << 24 | seg[i + 1] << 16 | seg[i + 2] << 8 | seg[i + 3]) >> (32 - (p & 7) - s)) & ((1 << s) - 1)
                            p += s
                            if val < (1 << (s - 1)):
                                val -= (1 << s) - 1
                            pred[ci] += val
                        coef = [0] * 64
                        coef[0] = pred[ci] * q[0]
                        k = 1
                        while k < 64:
                            i = p >> 3
                            largo, rs = tac[((seg[i] << 16 | seg[i + 1] << 8 | seg[i + 2]) >> (8 - (p & 7))) & 0xFFFF]
                            p += largo
                            s = rs & 15
                            if not s:
                                if rs == 0xF0:
                                    k += 16
                                    continue
                                break
                            k += rs >> 4
                            i = p >> 3
                            val = ((seg[i] << 24 | seg[i + 1] << 16 | seg[i + 2] << 8 | seg[i + 3]) >> (32 - (p & 7) - s)) & ((1 << s) - 1)
                            p += s
                            if val < (1 << (s - 1)):
                                val -= (1 << s) - 1
                            if k < 64:
                                coef[zz[k]] = val * q[k]
                            k += 1
                        x0 = ((fx * h + bx) * n)
                        y0 = ((fy * v + by) * n)
                        if n == 1:
                            plano[y0 * ancho_px + x0] = min(255, max(0, int(coef[0] / 8.0 + 128.5)))
                            continue
                        # la IDCT por filas y luego por columnas, saltando lo que es cero
                        tmp = []
                        for fv in rango:
                            fila = coef[fv * 8:fv * 8 + n]
                            if any(fila):
                                tmp.append((fv, [sum(A[x][u] * fila[u] for u in rango) for x in rango]))
                        for y in rango:
                            Ay = A[y]
                            base = (y0 + y) * ancho_px + x0
                            for x in rango:
                                t = 128.5
                                for fv, fila in tmp:
                                    t += Ay[fv] * fila[x]
                                plano[base + x] = 0 if t < 0 else 255 if t > 255 else int(t)
        # después de cada reinicio, todo vuelve a empezar
    w2, h2 = (W * n + 7) // 8, (H * n + 7) // 8
    canales = []
    for ci, (h, v, _, _, _, ancho_px) in enumerate(info):
        plano = planos[ci]
        fx_, fy_ = hmax // h, vmax // v
        if fx_ == 1 and fy_ == 1:
            canales.append(b"".join(bytes(plano[y * ancho_px:y * ancho_px + w2]) for y in range(h2)))
        else:
            cols = [x // fx_ for x in range(w2)]
            canales.append(b"".join(bytes(map(plano[(y // fy_) * ancho_px:(y // fy_ + 1) * ancho_px].__getitem__, cols))
                                    for y in range(h2)))
    if len(canales) == 1:
        return _Pixeles(w2, h2, canales[0], canales[0], canales[0])
    if len(canales) != 3:
        raise ValueError("imagen: los JPG en CMYK no los sé abrir sin Pillow (pip install pillow)")
    if adobe == 0:
        return _Pixeles(w2, h2, *canales)
    return _de_ycbcr(w2, h2, *canales)


def _de_ycbcr(W, H, Y, Cb, Cr):
    import operator
    off = 300
    tope = bytes(0 if v < off else 255 if v > off + 255 else v - off for v in range(off * 2 + 600))
    rr = [int(round(1.402 * (c - 128))) + off for c in range(256)]
    gb = [int(round(-0.344136 * (c - 128))) + off for c in range(256)]
    gr = [int(round(-0.714136 * (c - 128))) for c in range(256)]
    bb = [int(round(1.772 * (c - 128))) + off for c in range(256)]
    suma = operator.add
    R = bytes(map(tope.__getitem__, map(suma, Y, map(rr.__getitem__, Cr))))
    G = bytes(map(tope.__getitem__, map(suma, map(suma, Y, map(gb.__getitem__, Cb)), map(gr.__getitem__, Cr))))
    B = bytes(map(tope.__getitem__, map(suma, Y, map(bb.__getitem__, Cb))))
    return _Pixeles(W, H, R, G, B)


def _girar(p, orientacion):
    if orientacion == 3:
        return _Pixeles(p.W, p.H, p.R[::-1], p.G[::-1], p.B[::-1], p.A[::-1])
    if orientacion not in (6, 8):
        return p
    W, H = p.W, p.H
    # 6: girada a la derecha; 8: a la izquierda
    if orientacion == 6:
        orden = [(H - 1 - y) * W + x for x in range(W) for y in range(H)]
    else:
        orden = [y * W + (W - 1 - x) for x in range(W) for y in range(H)]
    return _Pixeles(H, W, *(bytes(map(c.__getitem__, orden)) for c in (p.R, p.G, p.B, p.A)))


# --- cambiar de tamaño ------------------------------------------------------------

def _escalar(p, W2, H2):
    """La imagen a W2 x H2, haciendo la media de varios puntos de cada trozo (así no salen dientes)."""
    W2, H2 = max(1, int(W2)), max(1, int(H2))
    if (W2, H2) == (p.W, p.H):
        return p
    sx, sy = p.W / float(W2), p.H / float(H2)
    tope = 4 if W2 * H2 <= 80000 else 2
    kx = max(1, min(tope, int(math.ceil(sx - 1e-9))))
    ky = max(1, min(tope, int(math.ceil(sy - 1e-9))))
    columnas = [[min(p.W - 1, int((x + (j + 0.5) / kx) * sx)) for x in range(W2)] for j in range(kx)]
    filas = [[min(p.H - 1, int((y + (i + 0.5) / ky) * sy)) for y in range(H2)] for i in range(ky)]
    n = kx * ky
    N = W2 * H2
    media = bytes(min(255, (s + n // 2) // n) for s in range(255 * n + 1))
    W = p.W
    salida = []
    for canal in (p.R, p.G, p.B, p.A):
        total = 0
        for i in range(ky):
            for j in range(kx):
                cols = columnas[j]
                muestra = b"".join(bytes(map(canal[f * W:(f + 1) * W].__getitem__, cols)) for f in filas[i])
                if n == 1:
                    total = muestra
                    break
                # cada valor en 16 bits para sumarlos todos de golpe
                ancho = bytearray(2 * N)
                ancho[0::2] = muestra
                total += int.from_bytes(ancho, sys.byteorder)
        if n == 1:
            salida.append(total)
            continue
        sumas = array("H")
        sumas.frombytes(total.to_bytes(2 * N, sys.byteorder))
        salida.append(bytes(map(media.__getitem__, sumas)))
    return _Pixeles(W2, H2, *salida)


def _sobre_fondo(p, fondo):
    """Lo transparente se pone del color del fondo (así al hacer medias no salen bordes raros)."""
    if min(p.A, default=255) == 255:
        return p
    N = p.W * p.H
    hay = int.from_bytes(p.A.translate(bytes([0] * 16 + [255] * 240)), "little")
    todo = int.from_bytes(b"\xff" * N, "little")
    canales = []
    for c, f in zip((p.R, p.G, p.B), fondo):
        v = (int.from_bytes(c, "little") & hay) | (int.from_bytes(bytes([f]) * N, "little") & (todo ^ hay))
        canales.append(v.to_bytes(N, "little"))
    return _Pixeles(p.W, p.H, canales[0], canales[1], canales[2], p.A)


# --- saber qué sabe hacer la terminal ---------------------------------------------

_capacidad = {"imagenes": None, "protocolo": None, "celda": (10, 20), "fondo": _FONDO}


def _preguntar_terminal(pregunta, final):
    """Escribe una pregunta a la terminal y lee la respuesta hasta que encaja con final (o lo que llegue)."""
    salida = sys.stdout
    if sys.platform == "win32":
        import ctypes
        import msvcrt
        k = ctypes.windll.kernel32
        entrada = k.GetStdHandle(-10)
        modo = ctypes.c_uint32()
        if not k.GetConsoleMode(entrada, ctypes.byref(modo)):
            return ""
        k.SetConsoleMode(entrada, (modo.value | 0x200) & ~0x6)
        try:
            while msvcrt.kbhit():
                msvcrt.getwch()
            salida.write(pregunta)
            salida.flush()
            respuesta, fin = "", time.time() + 0.4
            while time.time() < fin:
                if msvcrt.kbhit():
                    c = msvcrt.getwch()
                    respuesta += c
                    if final.search(respuesta):
                        break
                else:
                    time.sleep(0.005)
            return respuesta
        finally:
            k.SetConsoleMode(entrada, modo.value)
    import select
    import termios
    import tty
    fd = sys.stdin.fileno()
    antes = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        salida.write(pregunta)
        salida.flush()
        respuesta, fin = "", time.time() + 0.4
        while time.time() < fin:
            listo, _, _ = select.select([fd], [], [], max(0.0, fin - time.time()))
            if not listo:
                break
            c = os.read(fd, 1).decode("latin-1")
            respuesta += c
            if final.search(respuesta):
                break
        return respuesta
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, antes)


_PREGUNTA = ("\x1b]11;?\x1b\\"                                       # el color del fondo
             "\x1b_Gi=31,s=1,v=1,a=q,t=d,f=24;AAAA\x1b\\"            # ¿sabes lo de kitty?
             "\x1b[16t"                                              # lo que mide cada letra
             "\x1b[c")                                               # qué eres (esta la contestan todas)


def _puede_imagenes():
    """True si la terminal sabe pintar imágenes (Sixel o las de kitty). Se pregunta una vez y se guarda."""
    if _capacidad["imagenes"] is not None:
        return _capacidad["imagenes"]
    forzado = os.environ.get("PANTALLA_IMAGENES")
    if forzado is not None:
        forzado = forzado.strip().lower()
        si = forzado not in ("0", "no", "false", "")
        _capacidad["protocolo"] = ("kitty" if forzado == "kitty" else "sixel") if si else None
        _capacidad["imagenes"] = si
        return si
    from . import juego
    from .terminal import _es_terminal
    protocolo = None
    try:
        if _es_terminal(sys.stdin) and _es_terminal(sys.stdout) and juego._partida["actual"] is None:
            r = _preguntar_terminal(_PREGUNTA, re.compile(r"\x1b\[\?[\d;]*c"))
            m = re.search(r"\x1b\[\?([\d;]+)c", r)
            if "\x1b_Gi=31;OK" in r:
                protocolo = "kitty"
            elif m and "4" in m.group(1).split(";")[1:]:
                protocolo = "sixel"
            m = re.search(r"\x1b\[6;(\d+);(\d+)t", r)
            if m and int(m.group(1)) > 4 and int(m.group(2)) > 2:
                _capacidad["celda"] = (int(m.group(2)), int(m.group(1)))
            else:
                _celda_por_ventana()
            m = re.search(r"\]11;rgb:([0-9a-fA-F]+)/([0-9a-fA-F]+)/([0-9a-fA-F]+)", r)
            if m:
                _capacidad["fondo"] = tuple(int(int(h, 16) * 255.0 / (16 ** len(h) - 1) + 0.5) for h in m.groups())
    except Exception:
        protocolo = None
    _capacidad["protocolo"] = protocolo
    _capacidad["imagenes"] = protocolo is not None
    return _capacidad["imagenes"]


def _celda_por_ventana():
    # si no contesta a 16t, en Linux y Mac la ventana dice lo que mide en píxeles
    if sys.platform == "win32":
        return
    try:
        import fcntl
        import termios
        filas, cols, w, h = struct.unpack("HHHH", fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, bytes(8)))
        if cols and filas and w > cols * 3 and h > filas * 5:
            _capacidad["celda"] = (w // cols, h // filas)
    except Exception:
        pass


# --- pintar -----------------------------------------------------------------------

def _sixel(img, opaco=False):
    """La imagen en Sixel: los colores en una paleta y luego de seis en seis filas.

    Todo con bytes y translate (que va en C), porque píxel a píxel en Python es muy lento.
    Con opaco=True también se pinta el fondo (si no, lo que no tiene nada se queda transparente).
    """
    W, H = img.W, img.H
    n = W * H
    if opaco:
        vacio = bytes(256)
    else:
        vacio = bytes([1 if a < 10 else 0 for a in range(256)])
    hueco = img.A.translate(vacio)
    # cada píxel como un número de 4 bytes (rojo, verde, azul, vacío) para contarlos de golpe
    quitar = bytes([v >> 2 for v in range(256)])
    mezcla = bytearray(4 * n)
    mezcla[0::4] = img.R.translate(quitar)
    mezcla[1::4] = img.G.translate(quitar)
    mezcla[2::4] = img.B.translate(quitar)
    mezcla[3::4] = hueco
    claves = array("I")
    claves.frombytes(bytes(mezcla))
    cuantos = Counter(claves)
    # caben 255 colores: los que más salen van tal cual y los raros (los bordes suavizados) se
    # parecen a uno más basto, que también va en la paleta
    llenos = [k for k, _ in cuantos.most_common() if not k.to_bytes(4, sys.byteorder)[3]]
    tabla = dict.fromkeys(cuantos, 255)
    paleta = []
    exactos = min(len(llenos), 96)
    while True:
        bastos = {}
        for k in llenos[exactos:]:
            b = k.to_bytes(4, sys.byteorder)
            bastos.setdefault((b[0] >> 3, b[1] >> 3, b[2] >> 3), []).append(k)
        if exactos + len(bastos) <= 255 or exactos == 0:
            break
        exactos = max(0, 255 - len(bastos) - 10)
    for k in llenos[:exactos]:
        b = k.to_bytes(4, sys.byteorder)
        tabla[k] = len(paleta)
        paleta.append(((b[0] << 2) + 2, (b[1] << 2) + 2, (b[2] << 2) + 2))
    for (r, g, b), ks in list(bastos.items())[:255 - len(paleta)]:
        for k in ks:
            tabla[k] = len(paleta)
        paleta.append(((r << 5) + 16, (g << 5) + 16, (b << 5) + 16))
    indices = bytes(map(tabla.__getitem__, claves))
    partes = ['\x1bP0;1;0q"1;1;%d;%d' % (W, H)]
    for k, (r, g, b) in enumerate(paleta):
        partes.append("#%d;2;%d;%d;%d" % (k, min(100, r * 100 // 255), min(100, g * 100 // 255), min(100, b * 100 // 255)))
    repetir = re.compile(r"(.)\1{3,}")
    corto = lambda m: "!%d%s" % (len(m.group(0)), m.group(1))
    tablas = [[None] * 256 for _ in range(6)]
    for banda in range(0, H, 6):
        filas = [indices[y * W:(y + 1) * W] for y in range(banda, min(H, banda + 6))]
        hay = [set(f) for f in filas]
        presentes = set().union(*hay)
        presentes.discard(255)
        trozos = []
        for k in sorted(presentes):
            total = 0
            for dy, f in enumerate(filas):
                if k not in hay[dy]:
                    continue
                t = tablas[dy][k]
                if t is None:
                    t = bytearray(256)
                    t[k] = 1 << dy
                    t = tablas[dy][k] = bytes(t)
                total |= int.from_bytes(f.translate(t), "big")
            texto = total.to_bytes(W, "big").rstrip(b"\x00").translate(_A_SIXEL).decode("ascii")
            trozos.append("#%d%s" % (k, repetir.sub(corto, texto)))
        partes.append("$".join(trozos) + "-")
    partes.append("\x1b\\")
    return "".join(partes)


_A_SIXEL = bytes(range(63, 127)) + bytes(192)


def _kitty(img, opaco=False, ident=None, debajo=False):
    """La imagen con el protocolo de kitty (también WezTerm, Ghostty, Konsole...): los píxeles
    tal cual, comprimidos y en base64, en trozos de 4096. Con el mismo ident se cambia la de antes."""
    W, H = img.W, img.H
    if opaco or min(img.A, default=255) == 255:
        crudo, formato = bytearray(3 * W * H), 24
        crudo[0::3], crudo[1::3], crudo[2::3] = img.R, img.G, img.B
    else:
        crudo, formato = bytearray(4 * W * H), 32
        crudo[0::4], crudo[1::4], crudo[2::4], crudo[3::4] = img.R, img.G, img.B, img.A
    datos = base64.standard_b64encode(zlib.compress(bytes(crudo), 6)).decode("ascii")
    cw, ch = _capacidad["celda"]
    cab = "a=T,f=%d,o=z,s=%d,v=%d,c=%d,r=%d,C=1,q=2" % (formato, W, H, max(1, (W + cw - 1) // cw), max(1, (H + ch - 1) // ch))
    if ident is not None:
        cab += ",i=%d" % ident
    if debajo:
        cab += ",z=-1"
    trozos = [datos[i:i + 4096] for i in range(0, len(datos), 4096)] or [""]
    return "".join("\x1b_G" + (cab + "," if k == 0 else "") + "m=%d;" % (k < len(trozos) - 1) + t + "\x1b\\"
                   for k, t in enumerate(trozos))


def _pixeles(img, opaco=False, ident=None, debajo=False):
    """La imagen como la sepa pintar la terminal (kitty o Sixel)."""
    if _capacidad["protocolo"] == "kitty":
        return _kitty(img, opaco, ident, debajo)
    return _sixel(img, opaco)


def _color_256(r, g, b):
    # para las terminales sin millones de colores (la Terminal del Mac antigua)
    if abs(r - g) < 10 and abs(g - b) < 10:
        if r < 8:
            return 16
        if r > 238:
            return 231
        return 232 + (r - 8) * 24 // 231
    return 16 + 36 * ((r * 5 + 127) // 255) + 6 * ((g * 5 + 127) // 255) + ((b * 5 + 127) // 255)


def _codigo(r, g, b, fondo):
    if _pocos_colores():
        return ("48;5;%d" if fondo else "38;5;%d") % _color_256(r, g, b)
    return ("48;2;%d;%d;%d" if fondo else "38;2;%d;%d;%d") % (r, g, b)


def _pocos_colores():
    return os.environ.get("TERM_PROGRAM") == "Apple_Terminal" and os.environ.get("COLORTERM") not in ("truecolor", "24bit")


def _a_bloques(p, cols, filas):
    """Medios bloques: cada letra son dos píxeles, el de arriba (▀ con su color) y el de abajo (el fondo)."""
    W = p.W
    R, G, B, A = p.R, p.G, p.B, p.A
    fin = _fin_de_estilo()
    lineas = []
    for f in range(filas):
        trozos, antes = [], None
        for c in range(cols):
            i, j = 2 * f * W + c, (2 * f + 1) * W + c
            arriba = A[i] >= 128
            abajo = 2 * f + 1 < p.H and A[j] >= 128
            if arriba and abajo:
                ca, cb = (R[i], G[i], B[i]), (R[j], G[j], B[j])
                if ca == cb:
                    estilo, letra = (ca, None), "█"
                else:
                    estilo, letra = (ca, cb), "▀"
            elif arriba:
                estilo, letra = ((R[i], G[i], B[i]), None), "▀"
            elif abajo:
                estilo, letra = ((R[j], G[j], B[j]), None), "▄"
            else:
                estilo, letra = None, " "
            if estilo != antes:
                if antes is not None:
                    trozos.append(fin)
                if estilo is not None:
                    cod = _codigo(*estilo[0], fondo=False)
                    if estilo[1] is not None:
                        cod += ";" + _codigo(*estilo[1], fondo=True)
                    trozos.append("\x1b[" + cod + "m")
                antes = estilo
            trozos.append(letra)
        if antes is not None:
            trozos.append(fin)
        lineas.append("".join(trozos).rstrip(" ") if antes is None else "".join(trozos))
    return lineas


_RAMPA = " .:-=+*#%@"


def _a_letras(p, cols, filas, color=True):
    """Letras más o menos llenas según lo clara que sea cada parte (y de su color)."""
    fin = _fin_de_estilo()
    luces = [(0.2126 * r + 0.7152 * g + 0.0722 * b) for r, g, b in zip(p.R, p.G, p.B)]
    # se estira el contraste: si no, una foto normal sale casi toda con las mismas dos letras
    orden = sorted(l for l, a in zip(luces, p.A) if a >= 128) or [0, 255]
    bajo, alto = orden[len(orden) // 50], orden[-1 - len(orden) // 50]
    escala = 1.0 / max(1.0, alto - bajo)
    lineas = []
    for f in range(filas):
        trozos, antes = [], None
        for c in range(cols):
            i = f * p.W + c
            if p.A[i] < 128:
                letra, estilo = " ", None
            else:
                r, g, b = p.R[i], p.G[i], p.B[i]
                luz = min(1.0, max(0.0, (luces[i] - bajo) * escala))
                letra = _RAMPA[min(len(_RAMPA) - 1, int(luz * len(_RAMPA)))]
                if color and letra != " ":
                    # el color más vivo, que la forma ya la da la letra
                    m = max(r, g, b, 1)
                    estilo = (min(255, r * 255 // m), min(255, g * 255 // m), min(255, b * 255 // m))
                else:
                    estilo = None
            if estilo != antes:
                if antes is not None:
                    trozos.append(fin)
                if estilo is not None:
                    trozos.append("\x1b[" + _codigo(*estilo, fondo=False) + "m")
                antes = estilo
            trozos.append(letra)
        if antes is not None:
            trozos.append(fin)
        lineas.append("".join(trozos).rstrip(" "))
    return lineas


def _tamano_en_celdas(medida, ancho, alto, estilo, x, funcion):
    from .terminal import _entero, tamano
    cw, ch = _capacidad["celda"]
    tw, th = tamano()
    libre_w = max(4, tw - (x or 1) + 1)
    libre_h = max(2, th - 1)
    W, H = medida
    if estilo == "imagen":
        natural = (W / float(cw), H / float(ch))
    elif estilo == "bloques":
        natural = (float(W), H / 2.0)
    else:
        natural = (float(W), H * cw / float(ch))
    # filas por cada columna, para que no se deforme
    proporcion = (H / float(W)) * (cw / float(ch))
    if ancho is not None:
        ancho = _entero(ancho, "ancho", funcion)
    if alto is not None:
        alto = _entero(alto, "alto", funcion)
    if ancho is None and alto is None:
        ancho = min(natural[0], libre_w)
        if ancho * proporcion > libre_h:
            ancho = libre_h / proporcion
    elif ancho is None:
        ancho = alto / proporcion
    elif alto is not None and ancho * proporcion > alto:
        ancho = alto / proporcion
    ancho = max(1, int(round(ancho)))
    alto = max(1, int(round(ancho * proporcion)))
    return ancho, alto


def imagen(ruta, x=None, y=None, ancho=None, alto=None, estilo="auto"):
    """Enseña una foto o un dibujo (PNG, JPG, GIF, BMP o PPM) en la terminal.

        pantalla.imagen("gato.png")                     # donde esté el cursor, como un print
        pantalla.imagen("gato.jpg", 5, 2, ancho=40)     # en (5, 2), de 40 columnas de ancho
        pantalla.imagen("logo.png", estilo="bloques")   # siempre con medios bloques ▀

    - ancho, alto: lo que ocupa, en columnas y filas (sin ninguno, lo que quepa sin
      hacerla más grande de lo que es). Nunca se deforma: se hace caber en los dos.
    - estilo: "auto" la pinta de verdad si tu terminal sabe (Windows Terminal, WezTerm, kitty,
      iTerm2...) y si no con "bloques" (medios bloques ▀ de colores, vale en casi todas).
      "letras" la hace con letras . : - = + * # % @ de colores, como el arte ASCII de siempre.
    Devuelve (ancho, alto): lo que ha ocupado, en columnas y filas.
    """
    if estilo not in ("auto", "imagen", "bloques", "letras"):
        raise ValueError("imagen: estilo puede ser \"auto\", \"imagen\", \"bloques\" o \"letras\", y me has dado %r" % (estilo,))
    if estilo == "auto":
        estilo = "imagen" if _puede_imagenes() else "bloques"
    if x is not None and y is None:
        raise TypeError("imagen: si me das x también necesito y")
    cw, ch = _capacidad["celda"]
    datos = _leer(ruta)
    # de los JPG basta con la cabecera para saber lo que miden, y luego se abren ya pequeños
    medida = _medida_jpeg(datos)
    p = None if medida else _abrir(datos)
    cols, filas = _tamano_en_celdas(medida or (p.W, p.H), ancho, alto, estilo, x, "imagen")
    if estilo == "imagen":
        W2, H2 = cols * cw, filas * ch
    elif estilo == "bloques":
        W2, H2 = cols, filas * 2
    else:
        W2, H2 = cols, filas
    if p is None:
        p = _abrir(datos, minimo=(W2, H2))
    fondo = _capacidad["fondo"]
    p = _escalar(_sobre_fondo(p, fondo), W2, H2)
    from .numeros import _sacar
    from .terminal import _mover, _posicion
    if estilo == "imagen":
        datos = _pixeles(p)
        if x is None:
            _salida("\n" * filas + "\x1b[%dA" % filas + "\x1b7" + datos + "\x1b8\x1b[%dB" % filas)
        else:
            x, y = _posicion(x, y, "imagen")
            _salida("\x1b7" + _mover(x, y) + datos + "\x1b8")
        sys.stdout.flush()
        return cols, filas
    lineas = _a_bloques(p, cols, filas) if estilo == "bloques" else _a_letras(p, cols, filas)
    _sacar(lineas, x, y, "imagen")
    return cols, filas
