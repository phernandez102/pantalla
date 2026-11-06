"""
Ver cosas del espacio: planos, rectas, puntos y vectores en 3D dentro de una caja,
y girarlos con el ratón o con las flechas.

    pi = pantalla.plano("x + y + z = 3")
    r = pantalla.recta((0, 0, 0), vector=(1, 1, 1))
    pantalla.dibujar_espacio({"π": pi, "r": r})       # un dibujo quieto, como un print
    pantalla.ver_espacio({"π": pi, "r": r})           # a pantalla completa, para girarlo

En las terminales que saben pintar imágenes (Windows Terminal, WezTerm, la de VS Code con
las imágenes activadas...) sale como un dibujo de verdad: los planos rellenos y
transparentes y las rectas lisas. En las demás, o con estilo="puntos", se dibuja con
puntitos braille y los planos con el fondo de color.
"""

import math
import re
import sys
import time

from .colores import _RGB, _normalizar, _ALIAS
from .colores import estilo as _estilo_ansi
from .imagenes import _FONDO, _capacidad, _pixeles, _preguntar_terminal, _puede_imagenes
from .espacio import Plano, Punto, Recta3D, _leer_con, _pos_planos, _pos_recta_plano, _pos_rectas
from .espacio import _corte_planos, _corte_recta_plano, _corte_rectas, _tv
from .numeros import _a_numero, _sacar
from .terminal import _ayuda_que_cabe, _entero, _fin_de_estilo, _salida
from .vectores import Vector


_BRAILLE = [[0x01, 0x02, 0x04, 0x40], [0x08, 0x10, 0x20, 0x80]]
_FLECHAS = ["→", "↗", "↑", "↖", "←", "↙", "↓", "↘"]

_NOMBRES = {"plano": ["π", "σ", "ρ", "α", "β", "γ"], "recta": ["r", "s", "t", "l", "m", "n"],
            "punto": ["P", "Q", "R", "A", "B", "C", "D"], "vector": ["u", "v", "w", "a", "b"],
            "poligono": ["T", "T2", "T3", "T4"]}
_COLORES = {"plano": ["cian claro", "morado claro", "amarillo", "verde claro", "azul claro"],
            "recta": ["rojo claro", "verde claro", "naranja", "rosa", "azul claro"],
            "punto": ["amarillo claro", "blanco", "verde claro", "rosa", "cian claro"],
            "vector": ["verde claro", "rojo claro", "naranja", "cian claro"],
            "poligono": ["rosa", "naranja", "verde claro"]}

# cómo se ve cada color en el dibujo de verdad (los de la terminal, un poco más vivos)
_RGB_DIBUJO = {"negro": (12, 12, 12), "rojo": (205, 49, 49), "verde": (13, 188, 121), "amarillo": (229, 192, 123),
               "azul": (36, 114, 200), "morado": (188, 63, 188), "cian": (17, 168, 205), "grisclaro": (190, 190, 190),
               "gris": (118, 118, 118), "rojoclaro": (255, 95, 109), "verdeclaro": (110, 227, 110),
               "amarilloclaro": (255, 230, 109), "azulclaro": (97, 175, 239), "moradoclaro": (198, 120, 221),
               "cianclaro": (64, 214, 230), "blanco": (242, 242, 242)}

# lo que tapa a qué: si dos cosas caen en el mismo sitio, se ve la más importante
_CAJA, _EJES, _REJILLA, _BORDE, _CORTE, _LINEA = 0, 1, 2, 3, 4, 5


def _redondo(x):
    return int(math.floor(x + 0.5))


def _float3(P):
    return [float(n) for n in P]


def _rgb(color):
    if isinstance(color, (tuple, list)) and len(color) == 3:
        return tuple(int(c) for c in color)
    texto = str(color).strip()
    if texto.startswith("#"):
        h = texto[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    n = _normalizar(texto)
    n = _ALIAS.get(n, n)
    if n in _RGB_DIBUJO:
        return _RGB_DIBUJO[n]
    if n in _RGB:
        return _RGB[n]
    return (200, 200, 200)


def _hex(color):
    return "#%02x%02x%02x" % _rgb(color)


def _exacta(lineas):
    """La leyenda con los colores exactos del dibujo (en las terminales que pintan imágenes)."""
    return [[(t, None if c is None else _hex(c), f) for t, c, f in l] for l in lineas]


# --- lo que te dan ------------------------------------------------------------

def _pares(objetos):
    """[(nombre o None, cosa), ...] con lo que te den: un diccionario, una lista o una cosa sola."""
    if objetos is None:
        return []
    if isinstance(objetos, dict):
        return list(objetos.items())
    if isinstance(objetos, (Plano, Recta3D, str)) or (isinstance(objetos, (list, tuple)) and objetos and
                                                      not isinstance(objetos[0], (list, tuple, Plano, Recta3D, str))):
        return [(None, objetos)]
    return [(None, o) for o in objetos]


def _nombre_libre(tipo, usados):
    for n in _NOMBRES[tipo]:
        if n not in usados:
            return n
    k = 2
    while "%s%d" % (_NOMBRES[tipo][0], k) in usados:
        k += 1
    return "%s%d" % (_NOMBRES[tipo][0], k)


def _leer_objetos(pares, colores):
    cosas, usados = [], {}
    tomados = set(str(n) for n, _ in pares if n is not None)
    for nombre, o in pares:
        if isinstance(o, str):
            o = _leer_nuevo(o)
        if isinstance(o, Plano):
            tipo, datos = "plano", o
        elif isinstance(o, Recta3D):
            tipo, datos = "recta", o
        elif isinstance(o, Vector) and not isinstance(o, Punto) and len(o) == 3:
            tipo, datos = "vector", ([0.0, 0.0, 0.0], _float3(o))
        elif isinstance(o, (list, tuple)) and len(o) == 3 and not any(isinstance(n, (list, tuple)) for n in o):
            tipo, datos = "punto", _float3([_a_numero(n, "dibujar_espacio", "el punto") for n in o])
        elif isinstance(o, (list, tuple)) and len(o) == 2 and all(isinstance(p, (list, tuple)) and len(p) == 3 for p in o):
            tipo, datos = "vector", (_float3(o[0]), _float3(o[1]))
        elif isinstance(o, (list, tuple)) and len(o) >= 3 and all(isinstance(p, (list, tuple)) and len(p) == 3 for p in o):
            tipo, datos = "poligono", [_float3(p) for p in o]
        else:
            raise TypeError("dibujar_espacio: no sé dibujar %r. Valen planos, rectas, puntos (x, y, z), "
                            "Vectores y listas de puntos (un triángulo)" % (o,))
        k = usados.get(tipo, 0)
        usados[tipo] = k + 1
        if nombre is None:
            nombre = _nombre_libre(tipo, tomados)
        nombre = str(nombre)
        tomados.add(nombre)
        paleta = _COLORES[tipo]
        color = paleta[k % len(paleta)]
        propio = colores.get(nombre) if isinstance(colores, dict) else (
            colores[len(cosas) % len(colores)] if colores else None)
        cosas.append({"tipo": tipo, "nombre": nombre, "datos": datos, "color": propio or color})
    return cosas


def _bonito_numero(x):
    return str(int(x)) if float(x).is_integer() else ("%.2f" % x).rstrip("0").rstrip(".")


def _tamano_caja(cosas):
    m = 0.0
    for c in cosas:
        t, d = c["tipo"], c["datos"]
        if t == "punto":
            m = max([m] + [abs(n) for n in d])
        elif t in ("vector", "poligono"):
            m = max([m] + [abs(n) for p in d for n in p])
        elif t in ("recta", "plano"):
            m = max([m] + [abs(float(n)) for n in d.punto])
    L = max(4, int(math.ceil(m * 1.15)))
    return -float(L), float(L)


def _leer_tamano(tamano, cosas, funcion):
    if tamano is None:
        return _tamano_caja(cosas)
    if isinstance(tamano, (list, tuple)):
        if len(tamano) != 2:
            raise ValueError("%s: tamano es un número (la caja va de -tamano a tamano) o dos, "
                             "como (0, 5)" % funcion)
        lo, hi = (_numero(t, "tamano", funcion) for t in tamano)
    else:
        hi = _numero(tamano, "tamano", funcion)
        lo = -hi
    if hi <= lo:
        raise ValueError("%s: la caja tiene que ir de un número a otro más grande, y me has dado %r" % (funcion, tamano))
    return lo, hi


# --- la geometría: lo que hay que dibujar -------------------------------------

def _recortar(P, v, lo, hi):
    """El trozo de la recta P + t·v que queda dentro de la caja (o None)."""
    t0, t1 = -1e18, 1e18
    for i in range(3):
        if abs(v[i]) < 1e-12:
            if P[i] < lo - 1e-9 or P[i] > hi + 1e-9:
                return None
            continue
        a, b = (lo - P[i]) / v[i], (hi - P[i]) / v[i]
        t0, t1 = max(t0, min(a, b)), min(t1, max(a, b))
    if t0 > t1 + 1e-12:
        return None
    return [P[i] + t0 * v[i] for i in range(3)], [P[i] + t1 * v[i] for i in range(3)]


def _esquinas(lo, hi):
    return [[x, y, z] for x in (lo, hi) for y in (lo, hi) for z in (lo, hi)]


def _aristas(lo, hi):
    e = _esquinas(lo, hi)
    return [(e[i], e[j]) for i in range(8) for j in range(i + 1, 8)
            if sum(1 for k in range(3) if e[i][k] != e[j][k]) == 1]


def _poligono_plano(n, d, lo, hi):
    """Los puntos donde el plano corta las aristas de la caja, en orden (un polígono)."""
    puntos = []
    tol = 1e-9 * (hi - lo + 1)

    def meter(p):
        for q in puntos:
            if abs(p[0] - q[0]) + abs(p[1] - q[1]) + abs(p[2] - q[2]) < tol:
                return
        puntos.append(p)
    for A, B in _aristas(lo, hi):
        fa = n[0] * A[0] + n[1] * A[1] + n[2] * A[2] + d
        fb = n[0] * B[0] + n[1] * B[1] + n[2] * B[2] + d
        if abs(fa) < 1e-12:
            meter(A)
        if abs(fb) < 1e-12:
            meter(B)
        if fa * fb < 0 and abs(fa) >= 1e-12 and abs(fb) >= 1e-12:
            t = fa / (fa - fb)
            meter([A[k] + (B[k] - A[k]) * t for k in range(3)])
    if len(puntos) < 3:
        return []
    c = [sum(p[k] for p in puntos) / len(puntos) for k in range(3)]
    m = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
    nn = [x / m for x in n]
    otro = [1.0, 0.0, 0.0] if abs(nn[0]) < 0.9 else [0.0, 1.0, 0.0]
    e1 = [nn[1] * otro[2] - nn[2] * otro[1], nn[2] * otro[0] - nn[0] * otro[2], nn[0] * otro[1] - nn[1] * otro[0]]
    e2 = [nn[1] * e1[2] - nn[2] * e1[1], nn[2] * e1[0] - nn[0] * e1[2], nn[0] * e1[1] - nn[1] * e1[0]]

    def ang(p):
        w = [p[k] - c[k] for k in range(3)]
        return math.atan2(w[0] * e2[0] + w[1] * e2[1] + w[2] * e2[2], w[0] * e1[0] + w[1] * e1[1] + w[2] * e1[2])
    puntos.sort(key=ang)
    return puntos


def _paso_rejilla(lado):
    x = lado / 4.0
    k = 1.0
    while True:
        for m in (1, 2, 5):
            if m * k >= x - 1e-9:
                return m * k
        k *= 10


def _iguales(cosas):
    """{j: i} para cada plano o recta j que es el mismo que otro de antes, i."""
    igual = {}
    for j, c in enumerate(cosas):
        for i in range(j):
            if i in igual or cosas[i]["tipo"] != c["tipo"]:
                continue
            if c["tipo"] == "plano" and _pos_planos(cosas[i]["datos"], c["datos"]) == "coincidentes":
                igual[j] = i
                break
            if c["tipo"] == "recta" and _pos_rectas(cosas[i]["datos"], c["datos"])[0] == "coincidentes":
                igual[j] = i
                break
    return igual


def _relaciones(cosas):
    """Lo que pasa entre cada pareja: dónde se cortan, si son paralelas..."""
    lineas, cortes, rectas_corte = [], [], []
    igual = _iguales(cosas)
    for i in range(len(cosas)):
        for j in range(i + 1, len(cosas)):
            if (i in igual or j in igual) and igual.get(j) != i:
                continue
            a, b = cosas[i], cosas[j]
            if a["tipo"] == "plano" and b["tipo"] == "recta":
                a, b = b, a
            ta, tb = a["tipo"], b["tipo"]
            na, nb = a["nombre"], b["nombre"]
            if ta == "recta" and tb == "plano":
                tipo, _ = _pos_recta_plano(a["datos"], b["datos"])
                if tipo == "se cortan":
                    P, _ = _corte_recta_plano(a["datos"], b["datos"])
                    cortes.append(_float3(P))
                    lineas.append("%s corta a %s en %s" % (na, nb, _tv(P)))
                else:
                    lineas.append("%s %s %s" % (na, "está dentro de" if tipo == "contenida" else "es paralela a", nb))
            elif ta == "recta" and tb == "recta":
                tipo, _ = _pos_rectas(a["datos"], b["datos"])
                if tipo == "se cortan":
                    P, _, _ = _corte_rectas(a["datos"], b["datos"])
                    cortes.append(_float3(P))
                    lineas.append("%s y %s se cortan en %s" % (na, nb, _tv(P)))
                else:
                    lineas.append("%s y %s %s" % (na, nb, {"coincidentes": "son la misma recta",
                                                           "paralelas": "son paralelas",
                                                           "se cruzan": "se cruzan (no se tocan)"}[tipo]))
            elif ta == "plano" and tb == "plano":
                tipo = _pos_planos(a["datos"], b["datos"])
                if tipo == "se cortan":
                    r = _corte_planos(a["datos"], b["datos"])
                    rectas_corte.append((r, i, j))
                    lineas.append("%s y %s se cortan en la recta %s" % (na, nb, r))
                else:
                    lineas.append("%s y %s %s" % (na, nb, "son el mismo plano" if tipo == "coincidentes" else "son paralelos"))
            elif ta == "punto" and tb in ("plano", "recta"):
                if b["datos"].pasa_por(a["datos"]):
                    lineas.append("%s está en %s" % (na, nb))
            elif tb == "punto" and ta in ("plano", "recta"):
                if a["datos"].pasa_por(b["datos"]):
                    lineas.append("%s está en %s" % (nb, na))
    return lineas, cortes, rectas_corte


def _geometria(cosas, lo, hi, caja, ejes, cortes):
    """Todo lo que hay que dibujar, en 3D, sin decir todavía cómo."""
    g = {"rayas": [], "caras": [], "discos": [], "pies": [], "rombos": [], "puntas": [], "nombres": [], "ejes": []}
    lado = hi - lo

    def raya(A, B, color, capa, estilo="lisa", propios=()):
        g["rayas"].append((A, B, color, capa, estilo, frozenset(propios)))
    if caja:
        for A, B in _aristas(lo, hi):
            raya(A, B, "gris", _CAJA, "puntos")
    if ejes:
        O = [min(max(0.0, lo), hi)] * 3
        extra = lado * 0.09
        for k, letra in enumerate("xyz"):
            fin = list(O)
            fin[k] = hi + extra
            raya(O, fin, "gris claro", _EJES)
            if lo < O[k]:
                atras = list(O)
                atras[k] = lo
                raya(O, atras, "gris", _EJES, "puntos")
            g["puntas"].append((list(O), fin, "gris claro", _EJES))
            sitio = list(O)
            sitio[k] = hi + extra * 1.9
            g["ejes"].append((sitio, letra))

    relaciones, puntos_corte, rectas_corte = _relaciones(cosas) if cortes else ([], [], [])
    # si dos planos (o dos rectas) son el mismo, se dibuja uno y el otro a rayas encima
    igual = _iguales(cosas)
    juntos = {}
    for j, i in sorted(igual.items()):
        juntos.setdefault(i, []).append(j)

    def nombre_de(i):
        texto, colores_ = cosas[i]["nombre"], [cosas[i]["color"]] * len(cosas[i]["nombre"])
        for j in juntos.get(i, []):
            texto += " = " + cosas[j]["nombre"]
            colores_ += ["gris claro"] * 3 + [cosas[j]["color"]] * len(cosas[j]["nombre"])
        return texto, colores_
    paso = _paso_rejilla(lado)
    for j, c in enumerate(cosas):
        if c["tipo"] != "plano":
            continue
        d = c["datos"]
        n, dd = [float(d.a), float(d.b), float(d.c)], float(d.d)
        poli = _poligono_plano(n, dd, lo, hi)
        if not poli:
            continue
        if j in igual:
            for k in range(len(poli)):
                raya(poli[k], poli[(k + 1) % len(poli)], c["color"], _BORDE + 0.5, "guiones", [j, igual[j]])
            continue
        g["caras"].append((poli, c["color"], j))
        for eje in sorted(range(3), key=lambda i: (abs(n[i]), i))[:2]:
            k = math.ceil(lo / paso) * paso
            while k < hi - 1e-9:
                if k > lo + 1e-9:
                    cruces = []
                    for i in range(len(poli)):
                        A, B = poli[i], poli[(i + 1) % len(poli)]
                        fa, fb = A[eje] - k, B[eje] - k
                        if (fa < 0) != (fb < 0) and abs(fa - fb) > 1e-12:
                            s = fa / (fa - fb)
                            cruces.append([A[m] + (B[m] - A[m]) * s for m in range(3)])
                    if len(cruces) >= 2:
                        raya(cruces[0], cruces[1], c["color"], _REJILLA, "fina", [j])
                k += paso
        for i in range(len(poli)):
            raya(poli[i], poli[(i + 1) % len(poli)], c["color"], _BORDE, "lisa", [j] + juntos.get(j, []))
        texto, colores_ = nombre_de(j)
        g["nombres"].append(("plano", poli, texto, colores_))
    for r, i, j in rectas_corte:
        trozo = _recortar(_float3(r.punto), _float3(r.vector), lo, hi)
        if trozo:
            raya(trozo[0], trozo[1], "blanco", _CORTE, "lisa", [i, j])
    for j, c in enumerate(cosas):
        t, d, color = c["tipo"], c["datos"], c["color"]
        if t == "recta":
            trozo = _recortar(_float3(d.punto), _float3(d.vector), lo, hi)
            if trozo and j in igual:
                raya(trozo[0], trozo[1], color, _LINEA + 0.5, "gruesa_guiones")
            elif trozo:
                raya(trozo[0], trozo[1], color, _LINEA, "gruesa")
                texto, colores_ = nombre_de(j)
                g["nombres"].append(("recta", trozo, texto, colores_))
        elif t == "vector":
            A, B = d
            raya(A, B, color, _LINEA, "gruesa")
            g["puntas"].append((A, B, color, _LINEA))
            g["nombres"].append(("vector", (A, B), c["nombre"], color))
        elif t == "poligono":
            for i in range(len(d)):
                raya(d[i], d[(i + 1) % len(d)], color, _LINEA, "gruesa")
            centro = [sum(p[k] for p in d) / len(d) for k in range(3)]
            g["nombres"].append(("poligono", centro, c["nombre"], color))
        elif t == "punto":
            # como en el libro: baja hasta el suelo (z = 0) y desde ahí va a los ejes x e y
            if lo <= 0 <= hi:
                pie = [d[0], d[1], 0.0]
                if abs(d[2]) > 1e-9:
                    raya(d, pie, color, _REJILLA, "guia")
                if abs(d[0]) > 1e-9 and abs(d[1]) > 1e-9:
                    raya(pie, [d[0], 0.0, 0.0], color, _REJILLA, "guia")
                    raya(pie, [0.0, d[1], 0.0], color, _REJILLA, "guia")
                if abs(d[2]) > 1e-9 and (abs(d[0]) > 1e-9 or abs(d[1]) > 1e-9):
                    g["pies"].append((pie, color))
            g["discos"].append((d, color))
            nombre = "%s(%s)" % (c["nombre"], ", ".join(_bonito_numero(n) for n in d))
            g["nombres"].append(("punto", d, nombre, color))
    for P in puntos_corte:
        if all(lo - 1e-9 <= x <= hi + 1e-9 for x in P):
            g["rombos"].append(P)
    return g, relaciones


class _Camara(object):
    def __init__(self, W, H, giro, inclinacion, zoom, lo, hi):
        th, ph = math.radians(giro), math.radians(inclinacion)
        self.r = [-math.sin(th), math.cos(th), 0.0]
        self.u = [-math.sin(ph) * math.cos(th), -math.sin(ph) * math.sin(th), math.cos(ph)]
        self.d = [math.cos(ph) * math.cos(th), math.cos(ph) * math.sin(th), math.sin(ph)]
        self.c = (lo + hi) / 2.0
        self.s = zoom * min(W, H) / ((hi - lo) * math.sqrt(3) * 1.02)
        self.cx, self.cy = W / 2.0, H / 2.0

    def __call__(self, P):
        x, y, z = P[0] - self.c, P[1] - self.c, P[2] - self.c
        return (self.cx + self.s * (x * self.r[0] + y * self.r[1] + z * self.r[2]),
                self.cy - self.s * (x * self.u[0] + y * self.u[1] + z * self.u[2]),
                x * self.d[0] + y * self.d[1] + z * self.d[2])


def _sitio_nombre(tipo, datos, cam):
    """En qué punto (de la pantalla) se pone el nombre de cada cosa."""
    if tipo == "plano":
        mejor = max(datos, key=lambda p: cam(p)[0] - cam(p)[1] * 0.5)
        return cam(mejor)[:2], True
    if tipo == "recta":
        a, b = cam(datos[0]), cam(datos[1])
        return (b[:2] if (b[0], -b[1]) >= (a[0], -a[1]) else a[:2]), True
    if tipo == "vector":
        a, b = cam(datos[0]), cam(datos[1])
        return b[:2], b[0] >= a[0]
    return cam(datos)[:2], True


# --- con puntitos braille -----------------------------------------------------

class _Braille(object):
    def __init__(self, cols, filas):
        self.cols, self.filas = cols, filas
        self.W, self.H = cols * 2, filas * 4
        self.capas = [None] * (cols * filas)
        self.letras = {}
        self.fondo = [None] * (cols * filas)

    def punto(self, px, py, color, prio, prof):
        if px < 0 or py < 0 or px >= self.W or py >= self.H:
            return
        i = (py >> 2) * self.cols + (px >> 1)
        bit = _BRAILLE[px & 1][py & 3]
        capas = self.capas[i]
        if capas is None:
            self.capas[i] = [[color, prio, prof, bit]]
            return
        for capa in capas:
            if capa[0] == color:
                capa[3] |= bit
                if prio > capa[1] or (prio == capa[1] and prof > capa[2]):
                    capa[1], capa[2] = prio, prof
                return
        capas.append([color, prio, prof, bit])

    def arriba(self, i):
        capas = self.capas[i]
        if not capas:
            return None
        mejor = capas[0]
        for capa in capas[1:]:
            if capa[1] > mejor[1] or (capa[1] == mejor[1] and capa[2] > mejor[2]):
                mejor = capa
        return mejor

    def raya(self, a, b, color, prio, patron):
        ax, ay, az = a
        bx, by, bz = b
        n = max(1, int(math.ceil(max(abs(bx - ax), abs(by - ay)))))
        for k in range(n + 1):
            if patron and k % (patron[0] + patron[1]) >= patron[0]:
                continue
            t = k / float(n)
            self.punto(_redondo(ax + (bx - ax) * t), _redondo(ay + (by - ay) * t), color, prio, az + (bz - az) * t)

    def letra(self, c, f, ch, color, prio):
        if 0 <= c < self.cols and 0 <= f < self.filas:
            antes = self.letras.get((c, f))
            if antes is None or antes[2] <= prio:
                self.letras[(c, f)] = (ch, color, prio)

    def libre(self, c, f, n):
        if f < 0 or f >= self.filas or c < 0 or c + n > self.cols:
            return False
        for k in range(c, c + n):
            capa = self.arriba(f * self.cols + k)
            if (k, f) in self.letras or (capa is not None and capa[1] >= _BORDE):
                return False
        return True


def _sitios(c, f, n, derecha):
    sitios = [(c + 1, f), (c - n, f), (c + 1, f - 1), (c - n, f - 1), (c + 1, f + 1), (c - n, f + 1), (c, f - 1)]
    if not derecha:
        sitios[0], sitios[1] = sitios[1], sitios[0]
    return sitios


def _con_braille(g, cols, filas, cam, relleno):
    lz = _Braille(cols, filas)
    patrones = {"lisa": None, "gruesa": None, "fina": None, "puntos": (1, 2), "guiones": (3, 3),
                "gruesa_guiones": (3, 3), "guia": (1, 2)}
    if relleno:
        # el fondo de cada letra que cae dentro de un plano, del color del plano y oscuro
        for poli, color, _ in g["caras"]:
            pts = [cam(p) for p in poli]
            r, gg, b = _rgb(color)
            for f in range(filas):
                yc = f * 4 + 2.0
                xs = []
                for i in range(len(pts)):
                    (x1, y1, _), (x2, y2, _) = pts[i], pts[(i + 1) % len(pts)]
                    if (y1 <= yc < y2) or (y2 <= yc < y1):
                        xs.append(x1 + (yc - y1) * (x2 - x1) / (y2 - y1))
                if len(xs) < 2:
                    continue
                c0, c1 = int(math.ceil(min(xs) / 2.0 - 0.5)), int(math.ceil(max(xs) / 2.0 - 0.5))
                for c in range(max(0, c0), min(cols, c1)):
                    i = f * cols + c
                    antes = lz.fondo[i]
                    nuevo = (r * 0.22, gg * 0.22, b * 0.22)
                    lz.fondo[i] = nuevo if antes is None else (antes[0] + nuevo[0], antes[1] + nuevo[1], antes[2] + nuevo[2])
    for A, B, color, capa, estilo, _ in g["rayas"]:
        lz.raya(cam(A), cam(B), color, capa, patrones[estilo])

    def celda(P):
        px, py, _ = cam(P)
        return _redondo(px) >> 1, _redondo(py) >> 2
    for P, letra in g["ejes"]:
        c, f = celda(P)
        lz.letra(min(max(c, 0), cols - 1), min(max(f, 0), filas - 1), letra, "blanco", 6)
    for A, B, color, capa in g["puntas"]:
        if capa != _LINEA:
            continue
        (ax, ay, _), (bx, by, _) = cam(A), cam(B)
        c, f = celda(B)
        if (_redondo(ax), _redondo(ay)) == (_redondo(bx), _redondo(by)):
            punta = "•"
        else:
            punta = _FLECHAS[_redondo(math.degrees(math.atan2(-(by - ay), bx - ax)) / 45) % 8]
        lz.letra(c, f, punta, color, 6)
    for P in g["rombos"]:
        c, f = celda(P)
        lz.letra(c, f, "◆", "blanco", 6)
    for P, color in g["discos"]:
        c, f = celda(P)
        lz.letra(c, f, "●", color, 6)
    for tipo, datos, texto, color in g["nombres"]:
        (px, py), derecha = _sitio_nombre(tipo, datos, cam)
        c, f = _redondo(px) >> 1, _redondo(py) >> 2
        if tipo == "poligono":
            c -= 1
        colores_ = color if isinstance(color, list) else [color] * len(texto)
        for sc, sf in _sitios(c, f, len(texto), derecha):
            if lz.libre(sc, sf, len(texto)):
                for k, ch in enumerate(texto):
                    lz.letra(sc + k, sf, ch, colores_[k], 7)
                break

    filas_ = []
    for f in range(filas):
        fila = []
        for c in range(cols):
            i = f * cols + c
            fondo = lz.fondo[i]
            if fondo is not None:
                fondo = "#%02x%02x%02x" % tuple(min(255, int(v)) for v in fondo)
            if (c, f) in lz.letras:
                ch, color, _ = lz.letras[(c, f)]
                fila.append((ch, color, fondo))
            elif lz.capas[i]:
                capa = lz.arriba(i)
                fila.append((chr(0x2800 | capa[3]), capa[0], fondo))
            else:
                fila.append((" ", None, fondo))
        filas_.append(fila)
    return filas_


# --- dibujo de verdad (para las terminales que pintan imágenes) -----------------

_ESTILOS_RAYA = {
    # ancho en píxeles (de una letra de 10), opacidad y guiones (trozo, hueco) en píxeles
    "lisa": (1.7, 0.95, None), "gruesa": (2.6, 1.0, None), "fina": (1.0, 0.45, None), "puntos": (1.0, 0.5, (2, 4)),
    "guiones": (1.9, 1.0, (8, 8)), "gruesa_guiones": (2.8, 1.0, (10, 10)), "guia": (1.3, 0.9, (4, 4)),
}
_ALFA_PLANO = 0.30


class _Imagen(object):
    def __init__(self, W, H, cam, caras, escala, fondo=_FONDO):
        self.W, self.H = W, H
        self.cam = cam
        self.escala = escala
        self.fondo = fondo
        n = W * H
        # cada canal en un bytearray: así rellenar trozos y pasarlo a Sixel va rápido
        self.R = bytearray([fondo[0]]) * n
        self.G = bytearray([fondo[1]]) * n
        self.B = bytearray([fondo[2]]) * n
        self.A = bytearray(n)
        self.planos = []
        for poli, color, indice in caras:
            pts = [cam(p) for p in poli]
            self.planos.append(self._preparar(pts, _rgb(color), indice))

    def _preparar(self, pts, rgb, indice):
        # la profundidad en la pantalla es z = a·x + b·y + c (es un plano y la proyección es paralela)
        mejor, coef = 0.0, None
        p0 = pts[0]
        for i in range(1, len(pts)):
            for j in range(i + 1, len(pts)):
                p1, p2 = pts[i], pts[j]
                det = (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p2[0] - p0[0]) * (p1[1] - p0[1])
                if abs(det) > abs(mejor):
                    mejor = det
                    a = ((p1[2] - p0[2]) * (p2[1] - p0[1]) - (p2[2] - p0[2]) * (p1[1] - p0[1])) / det
                    b = ((p1[0] - p0[0]) * (p2[2] - p0[2]) - (p2[0] - p0[0]) * (p1[2] - p0[2])) / det
                    coef = (a, b, p0[2] - a * p0[0] - b * p0[1])
        tramos = {}
        if coef is not None and abs(mejor) > 1.0:
            ys = [p[1] for p in pts]
            for y in range(max(0, int(math.floor(min(ys)))), min(self.H, int(math.ceil(max(ys))) + 1)):
                yc = y + 0.5
                xs = []
                for i in range(len(pts)):
                    (x1, y1, _), (x2, y2, _) = pts[i], pts[(i + 1) % len(pts)]
                    if (y1 <= yc < y2) or (y2 <= yc < y1):
                        xs.append(x1 + (yc - y1) * (x2 - x1) / (y2 - y1))
                if len(xs) >= 2:
                    x0 = max(0, int(math.ceil(min(xs) - 0.5)))
                    x1_ = min(self.W, int(math.ceil(max(xs) - 0.5)))
                    if x1_ > x0:
                        tramos[y] = (x0, x1_)
        return {"coef": coef, "tramos": tramos, "rgb": rgb, "indice": indice}

    def rellenar(self):
        """Los planos, transparentes: en cada sitio se mezclan del más lejano al más cercano."""
        for y in range(self.H):
            activos = [p for p in self.planos if y in p["tramos"]]
            if not activos:
                continue
            yc = y + 0.5
            cortes = set()
            for p in activos:
                cortes.update(p["tramos"][y])
            for i in range(len(activos)):
                for j in range(i + 1, len(activos)):
                    a1, b1, c1 = activos[i]["coef"]
                    a2, b2, c2 = activos[j]["coef"]
                    if abs(a1 - a2) > 1e-12:
                        x = -((b1 - b2) * yc + (c1 - c2)) / (a1 - a2)
                        if 0 < x < self.W:
                            cortes.add(int(math.ceil(x - 0.5)))
            cortes = sorted(cortes)
            fila = y * self.W
            for k in range(len(cortes) - 1):
                xa, xb = cortes[k], cortes[k + 1]
                if xb <= xa:
                    continue
                xm = (xa + xb) / 2.0
                encima = [p for p in activos if p["tramos"][y][0] <= xa and xb <= p["tramos"][y][1]]
                if not encima:
                    continue
                encima.sort(key=lambda p: p["coef"][0] * xm + p["coef"][1] * yc + p["coef"][2])
                r, g, b, a = float(self.fondo[0]), float(self.fondo[1]), float(self.fondo[2]), 0.0
                for p in encima:
                    pr, pg, pb = p["rgb"]
                    r, g, b = r + (pr - r) * _ALFA_PLANO, g + (pg - g) * _ALFA_PLANO, b + (pb - b) * _ALFA_PLANO
                    a = a + (1 - a) * _ALFA_PLANO
                n = xb - xa
                self.R[fila + xa:fila + xb] = bytes([int(r + 0.5)]) * n
                self.G[fila + xa:fila + xb] = bytes([int(g + 0.5)]) * n
                self.B[fila + xa:fila + xb] = bytes([int(b + 0.5)]) * n
                self.A[fila + xa:fila + xb] = bytes([int(a * 255 + 0.5)]) * n

    def tapado(self, x, y, z, propios):
        """Cuánto se ve de algo que está en (x, y) a la profundidad z: menos si hay planos delante."""
        f = 1.0
        for p in self.planos:
            if p["indice"] in propios:
                continue
            t = p["tramos"].get(y)
            if t is None or not (t[0] <= x < t[1]):
                continue
            a, b, c = p["coef"]
            if a * (x + 0.5) + b * (y + 0.5) + c > z + 1e-6:
                f *= 1 - _ALFA_PLANO * 1.6
        return f

    def pintar(self, x, y, rgb, alfa):
        if alfa <= 0.003 or x < 0 or y < 0 or x >= self.W or y >= self.H:
            return
        i = y * self.W + x
        if alfa > 1:
            alfa = 1.0
        R, G, B, A = self.R, self.G, self.B, self.A
        R[i] = int(R[i] + (rgb[0] - R[i]) * alfa + 0.5)
        G[i] = int(G[i] + (rgb[1] - G[i]) * alfa + 0.5)
        B[i] = int(B[i] + (rgb[2] - B[i]) * alfa + 0.5)
        A[i] = int(A[i] + (255 - A[i]) * alfa + 0.5)

    def raya(self, A, B, color, estilo, propios):
        ancho, opacidad, guion = _ESTILOS_RAYA[estilo]
        ancho *= self.escala
        rgb = _rgb(color)
        ax, ay, az = self.cam(A)
        bx, by, bz = self.cam(B)
        dx, dy = bx - ax, by - ay
        largo = math.hypot(dx, dy)
        if largo < 1e-9:
            return
        ux, uy = dx / largo, dy / largo
        r = ancho / 2.0
        if guion:
            guion = (guion[0] * self.escala, guion[1] * self.escala)
        oculta, guia = estilo.startswith("gruesa"), estilo == "guia"
        W, H = self.W, self.H
        # los píxeles por donde pasa: se recorre la dirección más larga y, en cada paso, los de alrededor
        if abs(dx) >= abs(dy):
            m, ext = dy / dx, (r + 1.0) * math.hypot(1.0, dy / dx)
            x0, x1 = max(0, int(math.floor(min(ax, bx) - r))), min(W - 1, int(math.ceil(max(ax, bx) + r)))
            sitios = [(x, y) for x in range(x0, x1 + 1) for yl in (ay + (x + 0.5 - ax) * m,)
                      for y in range(max(0, int(yl - ext)), min(H, int(yl + ext) + 2))]
        else:
            m, ext = dx / dy, (r + 1.0) * math.hypot(1.0, dx / dy)
            y0, y1 = max(0, int(math.floor(min(ay, by) - r))), min(H - 1, int(math.ceil(max(ay, by) + r)))
            sitios = [(x, y) for y in range(y0, y1 + 1) for xl in (ax + (y + 0.5 - ay) * m,)
                      for x in range(max(0, int(xl - ext)), min(W, int(xl + ext) + 2))]
        delante = [(p["tramos"], p["coef"]) for p in self.planos if p["indice"] not in propios]
        trozo, periodo = (guion[0], guion[0] + guion[1]) if guion else (0, 0)
        e = self.escala
        R, G, B, Al = self.R, self.G, self.B, self.A
        cr, cg, cb = rgb
        r5, dz = r + 0.5, bz - az
        for x, y in sitios:
            wx, wy = x + 0.5 - ax, y + 0.5 - ay
            s = wx * ux + wy * uy
            cob = r5 - abs(wx * uy - wy * ux)
            if s < 0:
                cob = min(cob, r5 + s)
            elif s > largo:
                cob = min(cob, r5 - s + largo)
            if cob <= 0 or (periodo and s % periodo >= trozo):
                continue
            f = 1.0
            if delante:
                z = az + dz * min(max(s / largo, 0.0), 1.0) + 1e-6
                for tramos, (pa, pb, pc) in delante:
                    t = tramos.get(y)
                    if t is not None and t[0] <= x < t[1] and pa * (x + 0.5) + pb * (y + 0.5) + pc > z:
                        f *= 1 - _ALFA_PLANO * 1.6
                if oculta and f < 0.999:
                    # lo que queda detrás de un plano, a trozos (como en dibujo técnico)
                    if s % (9 * e) >= 5.5 * e:
                        continue
                    f = max(f, 0.6)
                elif guia:
                    f = max(f, 0.65)
            alfa = (cob if cob < 1 else 1.0) * opacidad * f
            if alfa <= 0.003:
                continue
            i = y * W + x
            R[i] = int(R[i] + (cr - R[i]) * alfa + 0.5)
            G[i] = int(G[i] + (cg - G[i]) * alfa + 0.5)
            B[i] = int(B[i] + (cb - B[i]) * alfa + 0.5)
            Al[i] = int(Al[i] + (255 - Al[i]) * alfa + 0.5)

    def disco(self, P, rgb, radio, borde=True):
        cx, cy, z = self.cam(P)
        R = radio * self.escala
        f = self.tapado(int(cx), int(cy), z, ())
        for y in range(int(math.floor(cy - R - 2)), int(math.ceil(cy + R + 2)) + 1):
            for x in range(int(math.floor(cx - R - 2)), int(math.ceil(cx + R + 2)) + 1):
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if borde:
                    self.pintar(x, y, self.fondo, min(1.0, max(0.0, R + 1.8 - d)) * 0.9)
                self.pintar(x, y, rgb, min(1.0, max(0.0, R + 0.5 - d)) * max(f, 0.55))

    def rombo(self, P, rgb, radio):
        cx, cy, _ = self.cam(P)
        R = radio * self.escala
        for y in range(int(math.floor(cy - R - 2)), int(math.ceil(cy + R + 2)) + 1):
            for x in range(int(math.floor(cx - R - 2)), int(math.ceil(cx + R + 2)) + 1):
                d = (abs(x + 0.5 - cx) + abs(y + 0.5 - cy)) / math.sqrt(2)
                self.pintar(x, y, self.fondo, min(1.0, max(0.0, R / math.sqrt(2) + 1.6 - d)) * 0.9)
                self.pintar(x, y, rgb, min(1.0, max(0.0, R / math.sqrt(2) + 0.5 - d)))

    def punta(self, A, B, color, largo, ancho):
        ax, ay, _ = self.cam(A)
        bx, by, bz = self.cam(B)
        d = math.hypot(bx - ax, by - ay)
        if d < 1e-9:
            return
        ux, uy = (bx - ax) / d, (by - ay) / d
        largo, ancho = largo * self.escala, ancho * self.escala
        base = (bx - ux * largo, by - uy * largo)
        tri = [(bx + ux * 1.5, by + uy * 1.5), (base[0] - uy * ancho, base[1] + ux * ancho),
               (base[0] + uy * ancho, base[1] - ux * ancho)]
        rgb = _rgb(color)
        xs, ys = [p[0] for p in tri], [p[1] for p in tri]
        aristas = []
        for i in range(3):
            (x1, y1), (x2, y2) = tri[i], tri[(i + 1) % 3]
            ln = math.hypot(x2 - x1, y2 - y1)
            aristas.append((x1, y1, (x2 - x1) / ln, (y2 - y1) / ln))
        signo = 1 if ((tri[1][0] - tri[0][0]) * (tri[2][1] - tri[0][1]) - (tri[2][0] - tri[0][0]) * (tri[1][1] - tri[0][1])) > 0 else -1
        for y in range(int(math.floor(min(ys))) - 1, int(math.ceil(max(ys))) + 1):
            for x in range(int(math.floor(min(xs))) - 1, int(math.ceil(max(xs))) + 1):
                m = min(signo * ((x + 0.5 - x1) * uy_ - (y + 0.5 - y1) * ux_) * -1 for x1, y1, ux_, uy_ in aristas)
                if m > -0.5:
                    self.pintar(x, y, rgb, min(1.0, m + 0.5) * self.tapado(x, y, bz, ()))

    def ocupado(self, c, f, cw, ch):
        """Cuánto hay pintado en una letra (de 0 a 1)."""
        total, n = 0.0, 0
        for y in range(int(f * ch), min(self.H, int((f + 1) * ch)), 2):
            fila = y * self.W
            for x in range(int(c * cw), min(self.W, int((c + 1) * cw)), 2):
                total += self.A[fila + x]
                n += 1
        return total / 255.0 / n if n else 1.0


def _con_imagen(g, cols, filas, cw, ch, cam_de, fondo=_FONDO):
    W, H = int(cols * cw), int(filas * ch)
    cam = cam_de(W, H)
    img = _Imagen(W, H, cam, g["caras"], cw / 10.0, fondo)
    img.rellenar()
    for A, B, color, capa, estilo, propios in sorted(g["rayas"], key=lambda r: r[3]):
        img.raya(A, B, color, estilo, propios)
    for A, B, color, capa in g["puntas"]:
        img.punta(A, B, color, 11 if capa == _LINEA else 8, 4.5 if capa == _LINEA else 3.2)
    for P in g["rombos"]:
        img.rombo(P, (255, 255, 255), 5.5)
    for P, color in g["pies"]:
        img.disco(P, _rgb(color), 1.8, borde=False)
    for P, color in g["discos"]:
        img.disco(P, _rgb(color), 4.2)
    letras = []
    ocupadas = set()

    def poner(c, f, texto, color):
        colores_ = color if isinstance(color, list) else [color] * len(texto)
        for k, chx in enumerate(texto):
            letras.append((c + k, f, chx, colores_[k]))
            ocupadas.add((c + k, f))
    for P, letra in g["ejes"]:
        px, py, _ = cam(P)
        c, f = min(max(int(px // cw), 0), cols - 1), min(max(int(py // ch), 0), filas - 1)
        poner(c, f, letra, "blanco")
    for tipo, datos, texto, color in g["nombres"]:
        (px, py), derecha = _sitio_nombre(tipo, datos, cam)
        c, f = int(px // cw), int(py // ch)
        if tipo == "poligono":
            c -= 1
        mejor = None
        for sc, sf in _sitios(c, f, len(texto), derecha):
            if sf < 0 or sf >= filas or sc < 0 or sc + len(texto) > cols:
                continue
            if any((sc + k, sf) in ocupadas for k in range(len(texto))):
                continue
            o = max(img.ocupado(sc + k, sf, cw, ch) for k in range(len(texto)))
            if mejor is None or o < mejor[0] - 0.05:
                mejor = (o, sc, sf)
            if o < 0.15:
                break
        if mejor is not None:
            poner(mejor[1], mejor[2], texto, color)
    return img, letras


# --- dibujar ------------------------------------------------------------------

def _texto_de(c):
    t, d = c["tipo"], c["datos"]
    if t == "plano":
        return d.general()
    if t == "recta":
        return str(d)
    if t == "punto":
        return "(" + ", ".join(_bonito_numero(n) for n in d) + ")"
    if t == "vector":
        A, B = d
        w = [B[k] - A[k] for k in range(3)]
        return "(" + ", ".join(_bonito_numero(n) for n in w) + ")"
    return ", ".join("(" + ", ".join(_bonito_numero(n) for n in p) + ")" for p in d)


def _partir(texto, ancho, sangria):
    """Parte un texto largo en trozos que quepan, por los espacios."""
    trozos = []
    while len(texto) > ancho:
        corte = texto.rfind(" ", sangria + 1, ancho + 1)
        if corte <= sangria:
            corte = ancho
        trozos.append(texto[:corte].rstrip())
        texto = " " * sangria + texto[corte:].lstrip()
    trozos.append(texto)
    return trozos


def _leyenda(cosas, relaciones, ancho):
    lineas = []
    ancho = max(12, ancho)
    for c in cosas:
        marca = {"plano": "▰", "recta": "━", "punto": "●", "vector": "→", "poligono": "△"}[c["tipo"]]
        texto = "%s %s  %s" % (marca, c["nombre"], _texto_de(c))
        for t in _partir(texto, ancho, 4 + len(c["nombre"])):
            lineas.append([(t, c["color"], None)])
    for r in relaciones:
        for t in _partir("· " + r, ancho, 4):
            lineas.append([(t, "gris claro", None)])
    return lineas


def _a_texto(trozos):
    fin = _fin_de_estilo()
    partes = []
    actual, grupo = None, []
    for ch, color, fondo in trozos:
        estilo = (color, fondo)
        if estilo != actual and grupo:
            cod = _estilo_ansi(actual[0], fondo=actual[1]) if actual != (None, None) else ""
            partes.append(cod + "".join(grupo) + fin if cod else "".join(grupo))
            grupo = []
        actual = estilo
        grupo.append(ch)
    if grupo:
        cod = _estilo_ansi(actual[0], fondo=actual[1]) if actual != (None, None) else ""
        partes.append(cod + "".join(grupo) + fin if cod else "".join(grupo))
    texto = "".join(partes)
    return texto.rstrip() if actual is None or actual[1] is None else texto


def _numero(valor, nombre, funcion):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError("%s: %s tiene que ser un número, y me has dado %r" % (funcion, nombre, valor))
    return float(valor)


def _estilo(estilo, funcion):
    if estilo not in ("auto", "imagen", "puntos"):
        raise ValueError("%s: estilo puede ser \"auto\", \"imagen\" o \"puntos\", y me has dado %r" % (funcion, estilo))
    if estilo == "auto":
        return "imagen" if _puede_imagenes() else "puntos"
    return estilo


def _imagen_en(img, letras, x, y, filas):
    """La imagen y los nombres encima. Con x e y en ese sitio; sin ellos, donde esté el cursor."""
    fin = _fin_de_estilo()
    if x is None and y is None:
        textos = "".join("\x1b8" + ("\x1b[%dB" % f if f else "") + ("\x1b[%dC" % c if c else "") +
                         _estilo_ansi(_hex(color)) + ch + fin for c, f, ch, color in letras)
        _salida("\n" * filas + "\x1b[%dA" % filas + "\x1b7" + _pixeles(img, debajo=True) + textos + "\x1b8\x1b[%dB" % filas)
    else:
        from .terminal import _mover, _posicion
        x, y = _posicion(1 if x is None else x, y, "dibujar_espacio")
        _salida(_mover(x, y) + _pixeles(img, debajo=True) + "".join(_mover(x + c, y + f) + _estilo_ansi(_hex(color)) + ch + fin
                                                     for c, f, ch, color in letras))


class _Giratorio(object):
    cuantos = 0
    """Un dibujo de dibujar_espacio(girar=True): se queda en la pantalla y se gira arrastrándolo.

    Mientras el programa espera algo (tecla(), menu(), esperar_clic(), bucle()...), los clics
    y arrastres que caen encima se los queda él y se vuelve a pintar girado."""

    def __init__(self, x, y, ancho, alto, giro, inclinacion, pintar):
        self.x, self.y, self.ancho, self.alto = x, y, ancho, alto
        self.alto_total = alto
        self.giro, self.inclinacion = giro, inclinacion
        self._pintar = pintar
        self.ancla = None
        self.sucio = False
        self.fino_pendiente = False
        self.cuando = 0.0
        self.viejas = []
        _Giratorio.cuantos += 1
        self.ident = 100 + _Giratorio.cuantos

    def dentro(self, x, y):
        return self.x <= x < self.x + self.ancho and self.y <= y < self.y + self.alto

    def raton(self, ev):
        if ev["tipo"] == "clic":
            if not self.dentro(ev["x"], ev["y"]):
                self.ancla = None
                return False
            self.ancla = (ev["x"], ev["y"])
            return True
        if ev["tipo"] != "movimiento":
            return False
        if self.ancla is None or ev.get("boton") is None:
            self.ancla = None
            return False
        dx, dy = ev["x"] - self.ancla[0], ev["y"] - self.ancla[1]
        if dx or dy:
            self.giro = (self.giro - dx * 4 + 180) % 360 - 180
            self.inclinacion = max(-90.0, min(90.0, self.inclinacion + dy * 8))
            self.ancla = (ev["x"], ev["y"])
            self.sucio = True
        return True

    def girar(self, giro=None, inclinacion=None):
        """Lo pone mirando desde otro sitio y lo vuelve a pintar."""
        if giro is not None:
            self.giro = _numero(giro, "giro", "girar")
        if inclinacion is not None:
            self.inclinacion = max(-90.0, min(90.0, _numero(inclinacion, "inclinacion", "girar")))
        self.pintar()

    def pintar(self, rapido=False):
        """Lo vuelve a pintar (rapido=True mientras se arrastra: luego se repinta mejor)."""
        self.sucio = False
        self.fino_pendiente = rapido
        self.cuando = time.time()
        _salida("\x1b7" + self._pintar(self, rapido) + "\x1b8")
        sys.stdout.flush()

    def quitar(self):
        """Deja de girarse con el ratón (el dibujo se queda donde está)."""
        from .terminal import _giratorios
        if self in _giratorios:
            _giratorios.remove(self)

    def __iter__(self):
        # para que siga valiendo ancho, alto = dibujar_espacio(...)
        return iter((self.ancho, self.alto_total))

    def __repr__(self):
        return "<dibujo 3D en (%d, %d), giro %g°, inclinación %g°>" % (self.x, self.y, self.giro, self.inclinacion)


_SIN_COLOR = re.compile(r"\x1b\[[\d;]*m")


def _cursor_ahora():
    """(x, y) del cursor, preguntándoselo a la terminal; None si no contesta."""
    try:
        r = _preguntar_terminal("\x1b[6n", re.compile(r"\x1b\[\d+;\d+R"))
    except Exception:
        return None
    m = re.search(r"\x1b\[(\d+);(\d+)R", r or "")
    return (int(m.group(2)), int(m.group(1))) if m else None


def dibujar_espacio(objetos, x=None, y=None, ancho=60, alto=22, giro=35, inclinacion=25, zoom=1,
                    tamano=None, caja=True, ejes=True, cortes=True, leyenda=True, colores=None, estilo="auto",
                    girar=False):
    """Dibuja planos, rectas, puntos y vectores del espacio, en 3D y dentro de una caja.

        pi = pantalla.plano("x + y + z = 3")
        r = pantalla.recta((0, 0, 0), vector=(1, 1, 1))
        pantalla.dibujar_espacio({"π": pi, "r": r, "P": (1, 1, 1)})
        pantalla.dibujar_espacio(["x + y + z = 3", "z = 0"])       # también escritos
        pantalla.dibujar_espacio(pi, tamano=(0, 4))                 # solo la parte positiva, como en el libro

    Valen planos, rectas, puntos (x, y, z), Vectores (flechas desde el origen), parejas de puntos
    ((x0, y0, z0), (x1, y1, z1)) para una flecha de uno a otro, y listas de 3 o más puntos (un triángulo...).
    - estilo: "auto" lo dibuja de verdad (planos rellenos y transparentes) si tu terminal sabe pintar
      imágenes, como Windows Terminal, y si no con puntitos. "puntos" siempre con puntitos braille.
    - giro, inclinacion: desde dónde se mira, en grados (giro alrededor del eje z, e inclinacion
      lo alto que está el ojo: 90 es mirar desde arriba).
    - zoom: 2 lo ve el doble de grande.
    - tamano: hasta dónde llega la caja: 5 es de -5 a 5, y (0, 4) es de 0 a 4 en los tres ejes.
    - cortes=True marca con ◆ dónde se cortan las cosas y con una raya blanca dónde se cortan dos planos.
    - leyenda=True escribe debajo cada cosa con su ecuación y lo que pasa entre ellas.
    - ancho, alto: lo que ocupa el dibujo (la leyenda va debajo).
    - girar=True: se puede girar arrastrándolo con el ratón (con cualquier botón) mientras tu
      programa espera algo: un menu(), tecla(), esperar_clic(), bucle()... Así puedes tener, por
      ejemplo, un menú a la izquierda y el dibujo a la derecha. limpiar() lo quita.
    Sin x ni y, se dibuja donde esté el cursor (como un print). Devuelve (ancho, alto); con
    girar=True devuelve el dibujo, que también vale como (ancho, alto) y tiene .girar(giro, inclinacion)
    y .quitar().
    Para verlo a pantalla completa y girarlo con el ratón, usa pantalla.ver_espacio().
    """
    ancho = _entero(ancho, "ancho", "dibujar_espacio")
    alto = _entero(alto, "alto", "dibujar_espacio")
    if ancho < 16 or alto < 8:
        raise ValueError("dibujar_espacio: es muy pequeño. Ponle por lo menos ancho=16 y alto=8")
    giro = _numero(giro, "giro", "dibujar_espacio")
    inclinacion = max(-90.0, min(90.0, _numero(inclinacion, "inclinacion", "dibujar_espacio")))
    zoom = _numero(zoom, "zoom", "dibujar_espacio")
    if zoom <= 0:
        raise ValueError("dibujar_espacio: zoom tiene que ser mayor que 0")
    cosas = _leer_objetos(_pares(objetos), colores)
    lo, hi = _leer_tamano(tamano, cosas, "dibujar_espacio")
    estilo = _estilo(estilo, "dibujar_espacio")
    g, relaciones = _geometria(cosas, lo, hi, caja, ejes, cortes)
    ley = _leyenda(cosas, relaciones, ancho) if leyenda else []
    ley = [_a_texto(l) for l in (_exacta(ley) if estilo == "imagen" else ley)]
    if girar:
        return _giratorio(g, ley, x, y, ancho, alto, giro, inclinacion, zoom, lo, hi, estilo)
    if estilo == "imagen":
        cw, ch = _capacidad["celda"]
        img, letras = _con_imagen(g, ancho, alto, cw, ch, lambda W, H: _Camara(W, H, giro, inclinacion, zoom, lo, hi),
                                  _capacidad["fondo"])
        _imagen_en(img, letras, x, y, alto)
        if ley:
            _sacar(ley, x, None if y is None else y + alto, "dibujar_espacio")
        return ancho, alto + len(ley)
    cam = _Camara(ancho * 2, alto * 4, giro, inclinacion, zoom, lo, hi)
    lineas = [_a_texto(f) for f in _con_braille(g, ancho, alto, cam, True)] + ley
    _sacar(lineas, x, y, "dibujar_espacio")
    return ancho, len(lineas)


def _giratorio(g, ley, x, y, ancho, alto, giro, inclinacion, zoom, lo, hi, estilo):
    from .raton import activar_raton
    from .terminal import _giratorios, _mover, _posicion

    def pintar(z, rapido=False):
        if estilo == "imagen":
            cw, ch = _capacidad["celda"]
            img, letras = _con_imagen(g, ancho, alto, cw, ch,
                                      lambda W, H: _Camara(W, H, z.giro, z.inclinacion, zoom, lo, hi), _capacidad["fondo"])
            # las letras viejas no las tapa la imagen: se borran antes
            nuevas = [(c, f) for c, f, _, _ in letras]
            borrar = "".join(_mover(z.x + c, z.y + f) + " " for c, f in z.viejas if (c, f) not in nuevas)
            z.viejas = nuevas
            fin = _fin_de_estilo()
            return (borrar + _mover(z.x, z.y) + _pixeles(img, opaco=True, ident=z.ident, debajo=True) +
                    "".join(_mover(z.x + c, z.y + f) + _estilo_ansi(_hex(color)) + t + fin for c, f, t, color in letras))
        cam = _Camara(ancho * 2, alto * 4, z.giro, z.inclinacion, zoom, lo, hi)
        trozos = []
        for k, fila in enumerate(_con_braille(g, ancho, alto, cam, True)):
            t = _a_texto(fila)
            trozos.append(_mover(z.x, z.y + k) + t + " " * max(0, ancho - len(_SIN_COLOR.sub("", t))))
        return "".join(trozos)

    if x is None and y is None:
        # donde esté el cursor: se deja sitio y se mira en qué fila ha quedado
        _salida("\n" * (alto + len(ley)))
        sys.stdout.flush()
        ahora = _cursor_ahora()
        if ahora is None:
            raise ValueError("dibujar_espacio: con girar=True dime dónde va, con x e y")
        x, y = 1, max(1, ahora[1] - alto - len(ley))
        abajo = ahora
    else:
        x, y = _posicion(1 if x is None else x, y, "dibujar_espacio")
        abajo = None
    z = _Giratorio(x, y, ancho, alto, giro, inclinacion, pintar)
    z.alto_total = alto + len(ley)
    _salida(pintar(z))
    if ley:
        _sacar(ley, x, y + alto, "dibujar_espacio")
    if abajo is not None:
        _salida(_mover(*abajo))
    sys.stdout.flush()
    _giratorios.append(z)
    activar_raton()
    return z


_AYUDA = "arrastra o ←↑→↓ girar · +/- zoom · x y z vistas · espacio gira solo · n añadir · b borrar · Esc salir"


def ver_espacio(objetos=None, giro=35, inclinacion=25, tamano=None, caja=True, ejes=True, cortes=True,
                colores=None, girar=False, estilo="auto"):
    """Enseña planos, rectas y puntos en 3D a pantalla completa, para girarlos con el ratón.

        pi = pantalla.plano("x + y + z = 3")
        r = pantalla.recta((0, 0, 0), vector=(1, 1, 1))
        pantalla.ver_espacio({"π": pi, "r": r})
        pantalla.ver_espacio()          # vacío: con la n vas añadiendo cosas escritas

    Arrastra con el ratón (o usa las flechas) para girarlo, + y - para acercar o alejar,
    x, y, z para mirarlo desde cada eje, espacio para que gire solo, c quita la caja,
    r vuelve a como estaba y Esc sale. Con la n escribes un plano ("x + y = 2"), una recta
    ("(x - 1)/2 = y = z") o un punto ("(1, 2, 3)") y se añade; la b borra lo último que añadiste.
    A la derecha (o debajo) están las ecuaciones y dónde se corta cada cosa.
    Lo que vale en objetos y en estilo es lo mismo que en dibujar_espacio(). Fuera de una
    terminal (IDLE) lo dibuja quieto, como dibujar_espacio().
    """
    from . import juego, raton, teclado
    from .componentes import mensaje

    dadas = _pares(objetos)
    _leer_objetos(dadas, colores)
    inicio = (_numero(giro, "giro", "ver_espacio"), _numero(inclinacion, "inclinacion", "ver_espacio"))
    if not juego._entorno.es_terminal(sys.stdout):
        dibujar_espacio(objetos, giro=giro, inclinacion=inclinacion, tamano=tamano, caja=caja, ejes=ejes,
                        cortes=cortes, colores=colores, estilo="puntos")
        return None
    estilo = _estilo(estilo, "ver_espacio")
    est = {"giro": inicio[0], "inc": inicio[1], "zoom": 1.0, "auto": bool(girar), "caja": bool(caja),
           "ejes": bool(ejes), "ancla": None, "extra": [], "salir": False}

    def preparar():
        return _leer_objetos(dadas + est["extra"], colores)

    def sitio(W, H, cosas):
        rel = _relaciones(cosas)[0] if cortes else []
        derecha = W >= 100
        ancho_ley = min(46, W // 3) if derecha else W
        ley = _leyenda(cosas, rel, ancho_ley - 1)
        if estilo == "imagen":
            ley = _exacta(ley)
        cols = W - ancho_ley - 1 if derecha else W
        filas = H - 2 if derecha else max(8, H - 2 - min(len(ley), H // 3))
        if derecha:
            ley = [(cols + 2, 2 + k, _a_texto(l)) for k, l in enumerate(ley[:filas])]
        else:
            ley = [(1, 2 + filas + k, _a_texto(l)) for k, l in enumerate(ley[:H - 2 - filas])]
        return cols, filas, ley

    def teclas(tecla):
        if tecla == "izquierda":
            est["giro"] += 5
        elif tecla == "derecha":
            est["giro"] -= 5
        elif tecla == "arriba":
            est["inc"] += 5
        elif tecla == "abajo":
            est["inc"] -= 5
        elif tecla in ("+", "="):
            est["zoom"] = min(6.0, est["zoom"] * 1.15)
        elif tecla == "-":
            est["zoom"] = max(0.3, est["zoom"] / 1.15)
        elif tecla == "x":
            est["giro"], est["inc"] = 0.0, 0.0
        elif tecla == "y":
            est["giro"], est["inc"] = 90.0, 0.0
        elif tecla == "z":
            est["giro"], est["inc"] = -90.0, 90.0
        elif tecla == "r":
            est["giro"], est["inc"], est["zoom"] = inicio[0], inicio[1], 1.0
        elif tecla == "c":
            est["caja"] = not est["caja"]
        elif tecla == "e":
            est["ejes"] = not est["ejes"]
        elif tecla == "espacio":
            est["auto"] = not est["auto"]
        elif tecla == "b":
            if est["extra"]:
                est["extra"].pop()
        elif tecla in ("esc", "q"):
            est["salir"] = True

    def arrastrar(x, y, arrastrando):
        if not arrastrando or est["ancla"] is None:
            est["ancla"] = (x, y)
            return
        dx, dy = x - est["ancla"][0], y - est["ancla"][1]
        est["giro"] -= dx * 4
        est["inc"] += dy * 8
        est["ancla"] = (x, y)
        est["auto"] = False

    def anadir(pedir_en):
        texto = pedir_en()
        if texto and texto.strip():
            try:
                est["extra"].append((None, _leer_nuevo(texto.strip())))
            except (TypeError, ValueError) as error:
                mensaje(str(error), titulo="No lo entiendo", color_borde="rojo claro")

    def cabecera(W):
        cab = " pantalla · espacio   giro %d°  inclinación %d°  zoom %s" % (
            _redondo(est["giro"]) % 360, _redondo(est["inc"]), _bonito_numero(round(est["zoom"], 2)))
        return _estilo_ansi("negro", fondo="cian") + cab.ljust(W)[:W] + _fin_de_estilo()

    def normalizar():
        if est["auto"]:
            est["giro"] -= 2
        est["inc"] = max(-90.0, min(90.0, est["inc"]))
        est["giro"] = est["giro"] % 360

    if estilo == "puntos":
        cache = {"clave": None}

        def actualizar(tecla):
            while True:
                c = raton.leer_raton(arrastrar=True)
                if not c:
                    break
                arrastrar(c[0], c[1], c.arrastrando)
            if tecla == "n":
                anadir(lambda: teclado.pedir("Escribe un plano, una recta o un punto (Enter vacío para no añadir): ",
                                             1, juego._juego["tamano"][1]))
            else:
                teclas(tecla)
            if est["salir"]:
                return "fin"
            normalizar()
            W, H = juego._juego["tamano"]
            clave = (est["giro"], est["inc"], est["zoom"], est["caja"], est["ejes"], W, H, len(est["extra"]))
            if clave != cache["clave"]:
                cosas = preparar()
                lo, hi = _leer_tamano(tamano, cosas, "ver_espacio")
                cols, filas, ley = sitio(W, H, cosas)
                g, _ = _geometria(cosas, lo, hi, est["caja"], est["ejes"], cortes)
                cam = _Camara(cols * 2, filas * 4, est["giro"], est["inc"], est["zoom"], lo, hi)
                cache["clave"] = clave
                cache["lineas"] = [_a_texto(f) for f in _con_braille(g, cols, filas, cam, True)]
                cache["ley"] = ley
            _sacar([cabecera(W)], 1, 1, "ver_espacio")
            _sacar(cache["lineas"], 1, 2, "ver_espacio")
            for xx, yy, texto in cache["ley"]:
                _sacar([texto], xx, yy, "ver_espacio")
            _sacar([_estilo_ansi("gris claro") + _ayuda_que_cabe(_AYUDA, W) + _fin_de_estilo()], 1, H, "ver_espacio")

        juego.jugar(actualizar, velocidad=20, raton=True, salir_con=None)
        return None
    _ver_con_imagenes(est, preparar, sitio, teclas, arrastrar, anadir, cabecera, normalizar, tamano, cortes)
    return None


def _ver_con_imagenes(est, preparar, sitio, teclas, arrastrar, anadir, cabecera, normalizar, tamano, cortes):
    """El bucle de ver_espacio() pintando imágenes: solo se vuelve a pintar cuando algo cambia."""
    import shutil
    from . import juego, raton, teclado
    from .terminal import CSI, _estado

    real = sys.stdout
    raton_antes = raton._raton["activo"]
    teclas_antes = teclado._modo["original"] is not None
    escribir = lambda t: (real.write(t), real.flush())
    cw, ch = _capacidad["celda"]
    giros_antes = _estado.get("sin_giros", False)
    _estado["sin_giros"] = True
    try:
        raton.activar_raton()
        teclado._activar_modo_teclas()
        escribir(CSI + "?1049h" + CSI + "?25l" + CSI + "2J")
        antes = None
        viejas, filas_ley = [], []
        ultima = 0.0
        while not est["salir"]:
            eventos = juego._entorno.leer()
            for e in eventos:
                if e.get("tipo") == "tecla":
                    if e.get("tecla") == "n":
                        W, H = shutil.get_terminal_size((80, 24))

                        def pedir_abajo():
                            escribir(CSI + "%d;1H" % H + CSI + "2K" + CSI + "?25h")
                            try:
                                return teclado.pedir("Escribe un plano, una recta o un punto (Enter vacío para no añadir): ")
                            finally:
                                escribir(CSI + "?25l")
                        anadir(pedir_abajo)
                        antes = None
                    else:
                        teclas(e.get("tecla"))
                elif e.get("tipo") in ("clic", "movimiento") and (e.get("tipo") == "clic" or e.get("boton")):
                    arrastrar(e["x"], e["y"], e.get("tipo") == "movimiento")
            normalizar()
            W, H = shutil.get_terminal_size((80, 24))
            clave = (est["giro"], est["inc"], est["zoom"], est["caja"], est["ejes"], W, H, len(est["extra"]))
            if clave != antes:
                cosas = preparar()
                lo, hi = _leer_tamano(tamano, cosas, "ver_espacio")
                cols, filas, ley = sitio(W, H, cosas)
                g, _ = _geometria(cosas, lo, hi, est["caja"], est["ejes"], cortes)
                img, letras = _con_imagen(g, cols, filas, cw, ch,
                                          lambda w, h: _Camara(w, h, est["giro"], est["inc"], est["zoom"], lo, hi),
                                          _capacidad["fondo"])
                fin = _fin_de_estilo()
                # si cambia el tamaño se borra todo; si no, solo las letras de antes (la imagen tapa lo demás)
                trozos = [CSI + "2J"] if antes is None or antes[5:7] != (W, H) else []
                for c, f in viejas:
                    trozos.append(CSI + "%d;%dH " % (2 + f, 1 + c))
                for yy in filas_ley:
                    trozos.append(CSI + "%d;%dH" % (yy, 1 if yy > filas + 1 else cols + 2) + CSI + "K")
                trozos += [CSI + "H" + cabecera(W), CSI + "2;1H" + "\x1b7" + _pixeles(img, opaco=True, ident=7, debajo=True)]
                for c, f, chx, color in letras:
                    trozos.append(CSI + "%d;%dH" % (2 + f, 1 + c) + _estilo_ansi(_hex(color)) + chx + fin)
                for xx, yy, texto in ley:
                    trozos.append(CSI + "%d;%dH" % (yy, xx) + CSI + "K" + texto)
                trozos.append(CSI + "%d;1H" % H + _estilo_ansi("gris claro") + _ayuda_que_cabe(_AYUDA, W - 1) + fin)
                escribir("".join(trozos))
                viejas = [(c, f) for c, f, _, _ in letras]
                filas_ley = [yy for _, yy, _ in ley]
                antes = clave
                ultima = time.time()
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


def _leer_nuevo(texto):
    t = texto.strip()
    if t.startswith("(") and t.count("=") == 0 and t.count("(") == 1:
        numeros = [p for p in t.strip("()").split(",")]
        if len(numeros) == 3:
            return Punto([_a_numero(n.strip(), "ver_espacio", "el punto") for n in numeros])
    return _leer_con(t, True)
