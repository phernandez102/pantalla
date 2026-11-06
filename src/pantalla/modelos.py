"""
Modelos 3D: ver figuras de verdad (OBJ o STL), fotos en relieve y superficies z = f(x, y).

    pantalla.ver_modelo("tetera.obj")                  # a pantalla completa, para girarla
    pantalla.ver_modelo("pieza.stl", color="naranja")
    pantalla.ver_modelo("cara.jpg")                    # la foto en relieve: lo claro sale hacia arriba
    pantalla.ver_modelo(lambda x, y: x**2 - y**2)      # una silla de montar
    pantalla.dibujar_modelo("tetera.obj", 40, 2, girar=True)   # quieta, donde quieras

Se pinta con caras rellenas e iluminadas. En las terminales que saben pintar imágenes
(Windows Terminal, WezTerm, kitty, iTerm2...) sale con todos los píxeles; en las demás
(cmd, la Terminal del Mac...) con medios bloques ▀ de colores.
"""

import math
import os
import struct
import sys
import time

from .imagenes import _Pixeles, _a_bloques, _abrir, _capacidad, _escalar, _pixeles, _puede_imagenes
from .terminal import _entero, _fin_de_estilo, _salida

_FORMATOS_IMAGEN = (".png", ".jpg", ".jpeg", ".jfif", ".gif", ".bmp", ".ppm", ".pgm", ".pbm", ".webp")


class Modelo(object):
    """Un modelo 3D ya leído: vértices, triángulos y el color de cada triángulo.

    Lo da pantalla.modelo("tetera.obj") y vale en ver_modelo() y dibujar_modelo().
    Tiene .vertices, .triangulos y .nombre; print(m) dice cuántos tiene."""

    def __init__(self, vertices, triangulos, colores, nombre="modelo"):
        self.vertices = vertices
        self.triangulos = triangulos
        self.colores = colores
        self.nombre = nombre
        self._normalizar()

    def _normalizar(self):
        # centrado en el origen y que quepa en la caja de -1 a 1
        if not self.vertices:
            raise ValueError("modelo: %s no tiene ningún punto" % self.nombre)
        lo = [min(v[k] for v in self.vertices) for k in range(3)]
        hi = [max(v[k] for v in self.vertices) for k in range(3)]
        c = [(a + b) / 2.0 for a, b in zip(lo, hi)]
        s = max(max(b - a for a, b in zip(lo, hi)) / 2.0, 1e-12)
        self.vertices = [((v[0] - c[0]) / s, (v[1] - c[1]) / s, (v[2] - c[2]) / s) for v in self.vertices]
        # lo que mide la bola que lo envuelve: así se ve igual de grande lo gires como lo gires
        self.radio = max(math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) for v in self.vertices) or 1.0
        self.normales = []
        V = self.vertices
        for a, b, c_ in self.triangulos:
            u = [V[b][k] - V[a][k] for k in range(3)]
            w = [V[c_][k] - V[a][k] for k in range(3)]
            n = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0])
            m = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
            self.normales.append((n[0] / m, n[1] / m, n[2] / m))

    def __repr__(self):
        return "<modelo %s: %d puntos y %d triángulos>" % (self.nombre, len(self.vertices), len(self.triangulos))


# --- leer --------------------------------------------------------------------------

def _rgb(color):
    from .visor import _rgb as rgb
    return rgb(color)


def _leer_obj(texto, ruta, color):
    vertices, triangulos, colores = [], [], []
    materiales, actual = {}, _rgb(color)
    for linea in texto.splitlines():
        partes = linea.split()
        if not partes or partes[0].startswith("#"):
            continue
        if partes[0] == "v" and len(partes) >= 4:
            x, y, z = (float(t) for t in partes[1:4])
            # en los OBJ lo de arriba es la y; aquí es la z
            vertices.append((x, -z, y))
        elif partes[0] == "f" and len(partes) >= 4:
            n = len(vertices)
            idx = []
            for t in partes[1:]:
                i = int(t.split("/")[0])
                idx.append(i - 1 if i > 0 else n + i)
            for k in range(1, len(idx) - 1):
                triangulos.append((idx[0], idx[k], idx[k + 1]))
                colores.append(actual)
        elif partes[0] == "mtllib" and ruta:
            materiales.update(_leer_mtl(os.path.join(os.path.dirname(ruta), " ".join(partes[1:]))))
        elif partes[0] == "usemtl":
            actual = materiales.get(" ".join(partes[1:]), _rgb(color))
    return vertices, triangulos, colores


def _leer_mtl(ruta):
    materiales, nombre = {}, None
    try:
        with open(ruta, encoding="utf-8", errors="replace") as f:
            for linea in f:
                partes = linea.split()
                if len(partes) >= 2 and partes[0] == "newmtl":
                    nombre = " ".join(partes[1:])
                elif len(partes) >= 4 and partes[0] == "Kd" and nombre is not None:
                    materiales[nombre] = tuple(max(0, min(255, int(float(t) * 255 + 0.5))) for t in partes[1:4])
    except OSError:
        pass
    return materiales


def _leer_stl(datos, color):
    vertices, triangulos = [], []
    n = struct.unpack("<I", datos[80:84])[0] if len(datos) >= 84 else -1
    if len(datos) == 84 + 50 * n:
        for k in range(n):
            v = struct.unpack("<9f", datos[84 + 50 * k + 12:84 + 50 * k + 48])
            base = len(vertices)
            vertices += [v[0:3], v[3:6], v[6:9]]
            triangulos.append((base, base + 1, base + 2))
    else:
        actual = []
        for linea in datos.decode("latin-1").splitlines():
            partes = linea.split()
            if partes and partes[0] == "vertex":
                actual.append(tuple(float(t) for t in partes[1:4]))
                if len(actual) == 3:
                    base = len(vertices)
                    vertices += actual
                    triangulos.append((base, base + 1, base + 2))
                    actual = []
    return vertices, triangulos, [_rgb(color)] * len(triangulos)


def _relieve(ruta, altura, lado=72):
    """Una foto como un terreno: cada trozo sube según lo claro que sea, y con su color."""
    p = _abrir(ruta, minimo=(lado, lado))
    if p.W >= p.H:
        cols, filas = lado, max(2, int(round(lado * p.H / float(p.W))))
    else:
        cols, filas = max(2, int(round(lado * p.W / float(p.H)))), lado
    p = _escalar(p, cols, filas)
    vertices, triangulos, colores = [], [], []
    escala = 2.0 / max(cols - 1, filas - 1)
    for f in range(filas):
        for c in range(cols):
            i = f * cols + c
            luz = (0.2126 * p.R[i] + 0.7152 * p.G[i] + 0.0722 * p.B[i]) / 255.0
            vertices.append(((c - (cols - 1) / 2.0) * escala, ((filas - 1) / 2.0 - f) * escala, luz * altura * 2))
    for f in range(filas - 1):
        for c in range(cols - 1):
            a, b = f * cols + c, f * cols + c + 1
            d, e = a + cols, b + cols
            i = f * cols + c
            if p.A[i] < 128:
                continue
            color = (p.R[i], p.G[i], p.B[i])
            triangulos += [(a, d, b), (b, d, e)]
            colores += [color, color]
    return vertices, triangulos, colores


_GRADIENTE = [(40, 70, 200), (30, 170, 220), (60, 200, 120), (230, 210, 70), (230, 80, 60)]


def _de_gradiente(t):
    t = min(1.0, max(0.0, t)) * (len(_GRADIENTE) - 1)
    k = min(len(_GRADIENTE) - 2, int(t))
    a, b = _GRADIENTE[k], _GRADIENTE[k + 1]
    t -= k
    return tuple(int(a[j] + (b[j] - a[j]) * t) for j in range(3))


def _superficie(f, rango, n=44):
    """z = f(x, y) en una rejilla; lo que no se puede calcular (raíces de negativos...) se queda sin pintar."""
    lo, hi = rango
    vals = []
    for j in range(n + 1):
        y = lo + (hi - lo) * j / float(n)
        fila = []
        for i in range(n + 1):
            x = lo + (hi - lo) * i / float(n)
            try:
                z = f(x, y)
                z = float(z) if not isinstance(z, complex) else None
                if z is not None and (math.isnan(z) or math.isinf(z)):
                    z = None
            except (ArithmeticError, ValueError, TypeError):
                z = None
            fila.append(z)
        vals.append(fila)
    todos = [z for fila in vals for z in fila if z is not None]
    if not todos:
        raise ValueError("ver_modelo: la función no da ningún número entre %g y %g" % (lo, hi))
    zmin, zmax = min(todos), max(todos)
    lado = float(hi - lo)
    # con la misma escala que x e y si cabe; si sube mucho, se aplasta para que quepa
    escala = 2.0 / lado if zmax - zmin <= lado else 2.0 / (zmax - zmin)
    zc = (zmin + zmax) / 2.0
    vertices, indice = [], {}
    for j in range(n + 1):
        for i in range(n + 1):
            z = vals[j][i]
            if z is not None:
                indice[(i, j)] = len(vertices)
                vertices.append((lo + lado * i / n, lo + lado * j / n, zc + (z - zc) * escala * lado / 2.0))
    triangulos, colores = [], []
    for j in range(n):
        for i in range(n):
            esquinas = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            if not all(e in indice for e in esquinas):
                continue
            a, b, c, d = (indice[e] for e in esquinas)
            medio = sum(vals[e[1]][e[0]] for e in esquinas) / 4.0
            color = _de_gradiente((medio - zmin) / (zmax - zmin) if zmax > zmin else 0.5)
            triangulos += [(a, b, c), (a, c, d)]
            colores += [color, color]
    # la caja va de lo a hi en x e y; en z se centra
    return vertices, triangulos, colores


def modelo(cosa, color="cian claro", relieve=0.25, rango=(-3, 3)):
    """Lee un modelo 3D. Vale:

        pantalla.modelo("tetera.obj")              # un archivo OBJ (con sus colores si tiene .mtl)
        pantalla.modelo("pieza.stl")               # un STL, de los de las impresoras 3D
        pantalla.modelo("foto.png", relieve=0.4)   # una imagen en relieve (relieve: lo que sube)
        pantalla.modelo(lambda x, y: x * y)        # la superficie z = f(x, y), con x e y en rango

    color es el de las caras (si el archivo no trae los suyos). Devuelve un Modelo.
    """
    if isinstance(cosa, Modelo):
        return cosa
    if callable(cosa):
        try:
            lo, hi = (float(v) for v in rango)
        except (TypeError, ValueError):
            raise TypeError("modelo: rango tiene que ser (desde, hasta), como (-3, 3)") from None
        if hi <= lo:
            raise ValueError("modelo: en rango el segundo número tiene que ser mayor que el primero")
        v, t, c = _superficie(cosa, (lo, hi))
        return Modelo(v, t, c, getattr(cosa, "__name__", "superficie").replace("<lambda>", "superficie"))
    if not isinstance(cosa, (str, os.PathLike)):
        raise TypeError("modelo: dame el nombre de un archivo (.obj, .stl o una imagen) o una función f(x, y), "
                        "y me has dado %r" % (cosa,))
    ruta = os.fspath(cosa)
    nombre = os.path.basename(ruta)
    extension = os.path.splitext(ruta)[1].lower()
    if extension in _FORMATOS_IMAGEN:
        v, t, c = _relieve(ruta, float(relieve))
        return Modelo(v, t, c, nombre)
    try:
        with open(ruta, "rb") as f:
            datos = f.read()
    except FileNotFoundError:
        raise FileNotFoundError("modelo: no encuentro el archivo %r" % ruta) from None
    try:
        if extension == ".stl" or datos[:5] == b"solid":
            v, t, c = _leer_stl(datos, color)
        elif extension == ".obj":
            v, t, c = _leer_obj(datos.decode("utf-8", "replace"), ruta, color)
        else:
            raise ValueError("modelo: %s no es .obj, .stl ni una imagen" % nombre)
    except (ValueError, IndexError, struct.error) as error:
        if str(error).startswith("modelo:"):
            raise
        raise ValueError("modelo: %s está roto o no lo sé leer" % nombre) from None
    if not t:
        raise ValueError("modelo: %s no tiene ningún triángulo" % nombre)
    return Modelo(v, t, c, nombre)


# --- pintar ------------------------------------------------------------------------

def _pintar(m, W, H, giro, inclinacion, zoom, fondo, fino=1):
    """El modelo en una imagen W x H: los triángulos de lejos a cerca, cada uno con su luz."""
    from .visor import _Camara
    W2, H2 = W * fino, H * fino
    cam = _Camara(W2, H2, giro, inclinacion, zoom, -1.0, 1.0)
    cam.s = zoom * min(W2, H2) / (2.08 * m.radio)
    P = [cam(v) for v in m.vertices]
    # la luz viene de arriba a la izquierda de donde miras, y gira contigo
    L = [0.6 * cam.d[k] + 0.55 * cam.u[k] - 0.35 * cam.r[k] for k in range(3)]
    ml = math.sqrt(sum(c * c for c in L))
    L = [c / ml for c in L]
    caras = sorted((P[a][2] + P[b][2] + P[c][2], k) for k, (a, b, c) in enumerate(m.triangulos))
    img = _Pixeles(W2, H2, bytes([fondo[0]]) * (W2 * H2), bytes([fondo[1]]) * (W2 * H2),
                   bytes([fondo[2]]) * (W2 * H2), bytes(W2 * H2))
    R, G, B, A = img.R, img.G, img.B, img.A
    lleno = b"\xff" * W2
    filas = {}
    tri, nor, col = m.triangulos, m.normales, m.colores
    for _, k in caras:
        a, b, c = tri[k]
        n = nor[k]
        luz = abs(n[0] * L[0] + n[1] * L[1] + n[2] * L[2])
        nivel = int((0.28 + 0.72 * luz) * 40)
        clave = (col[k], nivel)
        f = filas.get(clave)
        if f is None:
            r, g, b_ = col[k]
            t = nivel / 40.0
            f = filas[clave] = (bytes([min(255, int(r * t))]) * W2, bytes([min(255, int(g * t))]) * W2,
                                bytes([min(255, int(b_ * t))]) * W2)
        fr, fg, fb = f
        (x0, y0, _), (x1, y1, _), (x2, y2, _) = sorted((P[a], P[b], P[c]), key=lambda q: q[1])
        ya = max(0, int(math.ceil(y0 - 0.5)))
        yb = min(H2 - 1, int(math.floor(y2 - 0.5)))
        if yb < ya or y2 - y0 < 1e-9:
            continue
        d02 = (x2 - x0) / (y2 - y0)
        d01 = (x1 - x0) / (y1 - y0) if y1 > y0 else 0.0
        d12 = (x2 - x1) / (y2 - y1) if y2 > y1 else 0.0
        for y in range(ya, yb + 1):
            yc = y + 0.5
            xa = x0 + d02 * (yc - y0)
            xb = x0 + d01 * (yc - y0) if yc < y1 else x1 + d12 * (yc - y1)
            if xa > xb:
                xa, xb = xb, xa
            i0 = max(0, int(math.ceil(xa - 0.5)))
            i1 = min(W2, int(math.floor(xb - 0.5)) + 1)
            if i1 > i0:
                base = y * W2
                n_ = i1 - i0
                R[base + i0:base + i1] = fr[:n_]
                G[base + i0:base + i1] = fg[:n_]
                B[base + i0:base + i1] = fb[:n_]
                A[base + i0:base + i1] = lleno[:n_]
    if fino > 1:
        img = _escalar(img, W, H)
    return img


def _estilo(estilo, funcion):
    if estilo not in ("auto", "imagen", "bloques"):
        raise ValueError("%s: estilo puede ser \"auto\", \"imagen\" o \"bloques\", y me has dado %r" % (funcion, estilo))
    if estilo == "auto":
        return "imagen" if _puede_imagenes() else "bloques"
    return estilo


def _vista(m, giro, inclinacion):
    # desde dónde se mira al principio: las fotos de frente y un poco desde arriba
    if giro is None:
        giro = -90 if m.nombre.lower().endswith(_FORMATOS_IMAGEN) else -55
    if inclinacion is None:
        inclinacion = 50 if m.nombre.lower().endswith(_FORMATOS_IMAGEN) else 22
    return float(giro), float(inclinacion)


def _texto_bloques(m, cols, filas, giro, inclinacion, zoom, fino=2):
    img = _pintar(m, cols, filas * 2, giro, inclinacion, zoom, _capacidad["fondo"], fino)
    return _a_bloques(img, cols, filas)


def dibujar_modelo(cosa, x=None, y=None, ancho=60, alto=22, giro=None, inclinacion=None, zoom=1, color="cian claro",
                   estilo="auto", girar=False, relieve=0.25):
    """Dibuja un modelo 3D quieto (como un print, o en x, y).

        pantalla.dibujar_modelo("tetera.obj")
        pantalla.dibujar_modelo(lambda x, y: x**2 + y**2, 40, 2, ancho=50, alto=20)
        pantalla.dibujar_modelo("pieza.stl", 40, 2, girar=True)   # y luego se gira con el ratón

    Lo que vale como modelo es lo mismo que en pantalla.modelo(): un .obj, un .stl, una imagen
    (en relieve) o una función f(x, y). giro e inclinacion son desde dónde se mira, en grados.
    estilo: "auto" con píxeles si la terminal sabe y si no con medios bloques ▀; "bloques" siempre así.
    Con girar=True se puede girar arrastrándolo mientras tu programa espera algo (un menu(), tecla(),
    esperar_clic()...), como en dibujar_espacio(). Devuelve (ancho, alto).
    """
    from .numeros import _sacar
    from .visor import _numero
    m = modelo(cosa, color=color, relieve=relieve)
    ancho = _entero(ancho, "ancho", "dibujar_modelo")
    alto = _entero(alto, "alto", "dibujar_modelo")
    if ancho < 4 or alto < 2:
        raise ValueError("dibujar_modelo: es muy pequeño. Ponle por lo menos ancho=4 y alto=2")
    giro, inclinacion = _vista(m, giro, inclinacion)
    giro = _numero(giro, "giro", "dibujar_modelo")
    inclinacion = max(-90.0, min(90.0, _numero(inclinacion, "inclinacion", "dibujar_modelo")))
    zoom = _numero(zoom, "zoom", "dibujar_modelo")
    if zoom <= 0:
        raise ValueError("dibujar_modelo: zoom tiene que ser mayor que 0")
    if x is not None and y is None:
        raise TypeError("dibujar_modelo: si me das x también necesito y")
    estilo = _estilo(estilo, "dibujar_modelo")
    if girar:
        return _giratorio(m, x, y, ancho, alto, giro, inclinacion, zoom, estilo)
    if estilo == "imagen":
        cw, ch = _capacidad["celda"]
        img = _pintar(m, ancho * cw, alto * ch, giro, inclinacion, zoom, _capacidad["fondo"], 2)
        datos = _pixeles(img)
        if x is None:
            _salida("\n" * alto + "\x1b[%dA" % alto + "\x1b7" + datos + "\x1b8\x1b[%dB" % alto)
        else:
            from .terminal import _mover, _posicion
            x, y = _posicion(x, y, "dibujar_modelo")
            _salida("\x1b7" + _mover(x, y) + datos + "\x1b8")
        sys.stdout.flush()
        return ancho, alto
    _sacar(_texto_bloques(m, ancho, alto, giro, inclinacion, zoom), x, y, "dibujar_modelo")
    return ancho, alto


def _giratorio(m, x, y, ancho, alto, giro, inclinacion, zoom, estilo):
    from .raton import activar_raton
    from .terminal import _giratorios, _mover, _posicion
    from .visor import _SIN_COLOR, _Giratorio, _cursor_ahora

    def pintar(z, rapido=False):
        # mientras se arrastra va más rápido; quieto, más fino
        fino = 1 if rapido else 2
        if estilo == "imagen":
            cw, ch = _capacidad["celda"]
            img = _pintar(m, ancho * cw, alto * ch, z.giro, z.inclinacion, zoom, _capacidad["fondo"], fino)
            return _mover(z.x, z.y) + _pixeles(img, opaco=True, ident=z.ident)
        lineas = _texto_bloques(m, ancho, alto, z.giro, z.inclinacion, zoom, fino)
        return "".join(_mover(z.x, z.y + k) + l + " " * max(0, ancho - len(_SIN_COLOR.sub("", l)))
                       for k, l in enumerate(lineas))

    if x is None:
        _salida("\n" * alto)
        sys.stdout.flush()
        ahora = _cursor_ahora()
        if ahora is None:
            raise ValueError("dibujar_modelo: con girar=True dime dónde va, con x e y")
        x, y, abajo = 1, max(1, ahora[1] - alto), ahora
    else:
        x, y = _posicion(x, y, "dibujar_modelo")
        abajo = None
    z = _Giratorio(x, y, ancho, alto, giro, inclinacion, pintar)
    _salida(pintar(z))
    if abajo is not None:
        _salida(_mover(*abajo))
    sys.stdout.flush()
    _giratorios.append(z)
    activar_raton()
    return z


_AYUDA = "arrastra o ←↑→↓ girar · +/- zoom · espacio gira solo · r como al principio · Esc salir"


def ver_modelo(cosa, giro=None, inclinacion=None, color="cian claro", estilo="auto", girar=False, relieve=0.25):
    """Enseña un modelo 3D a pantalla completa para girarlo con el ratón (o las flechas).

        pantalla.ver_modelo("tetera.obj")
        pantalla.ver_modelo("foto.jpg", relieve=0.4)        # la foto en relieve
        pantalla.ver_modelo(lambda x, y: math.sin(x) * math.cos(y))

    Arrastra para girarlo, + y - para acercar o alejar, espacio para que gire solo, r para
    volver a como estaba y Esc para salir. Lo que vale como modelo es lo mismo que en
    pantalla.modelo(). Fuera de una terminal (IDLE) lo dibuja quieto.
    """
    from . import juego, raton, teclado
    from .terminal import CSI, _estado
    from .terminal import _ayuda_que_cabe
    from .visor import _numero
    import shutil

    m = modelo(cosa, color=color, relieve=relieve)
    giro, inclinacion = _vista(m, giro, inclinacion)
    inicio = (_numero(giro, "giro", "ver_modelo"), _numero(inclinacion, "inclinacion", "ver_modelo"))
    if not juego._entorno.es_terminal(sys.stdout):
        dibujar_modelo(m, giro=giro, inclinacion=inclinacion, estilo="bloques")
        return None
    estilo = _estilo(estilo, "ver_modelo")
    est = {"giro": inicio[0], "inc": inicio[1], "zoom": 1.0, "auto": bool(girar), "ancla": None, "salir": False}
    real = sys.stdout
    escribir = lambda t: (real.write(t), real.flush())
    raton_antes = raton._raton["activo"]
    teclas_antes = teclado._modo["original"] is not None
    giros_antes = _estado.get("sin_giros", False)
    _estado["sin_giros"] = True
    fin = _fin_de_estilo()
    try:
        raton.activar_raton()
        teclado._activar_modo_teclas()
        escribir(CSI + "?1049h" + CSI + "?25l" + CSI + "2J")
        antes, fino_hecho, ultima = None, False, 0.0
        while not est["salir"]:
            for e in juego._entorno.leer():
                t = e.get("tecla")
                if e.get("tipo") == "tecla":
                    if t == "izquierda":
                        est["giro"] += 6
                    elif t == "derecha":
                        est["giro"] -= 6
                    elif t == "arriba":
                        est["inc"] += 6
                    elif t == "abajo":
                        est["inc"] -= 6
                    elif t in ("+", "="):
                        est["zoom"] = min(6.0, est["zoom"] * 1.15)
                    elif t == "-":
                        est["zoom"] = max(0.3, est["zoom"] / 1.15)
                    elif t == "espacio":
                        est["auto"] = not est["auto"]
                    elif t == "r":
                        est["giro"], est["inc"], est["zoom"] = inicio[0], inicio[1], 1.0
                    elif t in ("esc", "q"):
                        est["salir"] = True
                elif e.get("tipo") == "clic":
                    est["ancla"] = (e["x"], e["y"])
                elif e.get("tipo") == "movimiento" and e.get("boton"):
                    if est["ancla"] is not None:
                        est["giro"] -= (e["x"] - est["ancla"][0]) * 4
                        est["inc"] += (e["y"] - est["ancla"][1]) * 8
                        est["auto"] = False
                    est["ancla"] = (e["x"], e["y"])
            if est["auto"]:
                est["giro"] -= 3
            est["inc"] = max(-90.0, min(90.0, est["inc"]))
            est["giro"] %= 360
            W, H = shutil.get_terminal_size((80, 24))
            clave = (est["giro"], est["inc"], est["zoom"], W, H)
            quieto = time.time() - ultima > 0.25
            if clave != antes or (quieto and not fino_hecho):
                fino = 2 if clave == antes else 1
                filas = max(2, H - 2)
                cab = " pantalla · %s   %d triángulos   giro %d°  inclinación %d°" % (
                    m.nombre, len(m.triangulos), int(round(est["giro"])) % 360, int(round(est["inc"])))
                trozos = [CSI + "2J"] if antes is None or antes[3:] != (W, H) else []
                trozos.append(CSI + "H" + "\x1b[30;46m" + cab.ljust(W)[:W] + fin)
                if estilo == "imagen":
                    cw, ch = _capacidad["celda"]
                    img = _pintar(m, W * cw, filas * ch, est["giro"], est["inc"], est["zoom"], _capacidad["fondo"], fino)
                    trozos.append(CSI + "2;1H" + _pixeles(img, opaco=True, ident=8))
                else:
                    lineas = _texto_bloques(m, W, filas, est["giro"], est["inc"], est["zoom"], fino)
                    trozos += [CSI + "%d;1H" % (2 + k) + l + CSI + "K" for k, l in enumerate(lineas)]
                trozos.append(CSI + "%d;1H" % H + "\x1b[37m" + _ayuda_que_cabe(_AYUDA, W - 1) + fin)
                escribir("".join(trozos))
                if clave != antes:
                    ultima = time.time()
                fino_hecho = fino == 2
                antes = clave
            else:
                time.sleep(0.02 if time.time() - ultima < 2 else 0.05)
    except KeyboardInterrupt:
        pass
    finally:
        _estado["sin_giros"] = giros_antes
        escribir(CSI + "2J" + CSI + "?25h" + CSI + "?1049l")
        _estado["cursor_oculto"] = False
        if not raton_antes:
            raton.desactivar_raton()
        if not teclas_antes:
            teclado._desactivar_modo_teclas()
    return None
