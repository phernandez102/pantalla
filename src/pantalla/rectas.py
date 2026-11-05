"""
Rectas en el plano: la recta que pasa por dos puntos (o por un punto con un vector o una pendiente),
con todas sus ecuaciones, dónde se cortan dos rectas y la distancia de un punto a una recta.

    r = pantalla.recta((1, 3), (2, 5))
    print(r)                         # 2x - y + 1 = 0
    print(r.explicita())             # y = 2x + 1
    pantalla.ecuaciones_recta((1, 3), (2, 5))      # todas a la vez
    pantalla.grafica(r, -5, 5)       # como es una función, se puede dibujar
"""

import math
import re
from fractions import Fraction

from .numeros import _a_numero, _bonito, _sacar
from .vectores import Vector, _componentes, _texto_vector


def _numero(n, funcion, que):
    n = _a_numero(n, funcion, que)
    return n if isinstance(n, float) else Fraction(n)


def _punto(P, funcion, que="el punto"):
    if not isinstance(P, (list, tuple)) or len(P) != 2:
        raise TypeError("%s: %s tiene que ser (x, y), con dos números, y me has dado %r" % (funcion, que, P))
    return [_numero(n, funcion, que) for n in P]


def _t(n):
    from .matrices import _texto_numero
    return _texto_numero(_bonito(n))


def _lineal(terminos):
    """[(2, "x"), (-1, "y"), (1, "")] -> "2x - y + 1"."""
    partes = []
    for n, letra in terminos:
        if n == 0:
            continue
        t = _t(abs(n))
        if letra:
            t = (("(%s)" % t) if "/" in t else ("" if t == "1" else t)) + letra
        partes.append((("-" if n < 0 else "") if not partes else (" - " if n < 0 else " + ")) + t)
    return "".join(partes) or "0"


def _menos(letra, n):
    """x - 1, x + 2, x"""
    if n == 0:
        return letra
    return "%s %s %s" % (letra, "-" if n > 0 else "+", _t(abs(n)))


class Recta(object):
    """Una recta del plano. Se hace con dos puntos, con un punto y un vector, o con un punto y la pendiente.

        r = pantalla.Recta((1, 3), (2, 5))                # pasa por (1, 3) y (2, 5)
        r = pantalla.Recta((1, 3), vector=(1, 2))         # por (1, 3) con dirección (1, 2)
        r = pantalla.Recta((0, 1), pendiente=2)           # por (0, 1) con pendiente 2
        r = pantalla.recta("y = 2x + 1")                  # o escrita

        print(r)                  # 2x - y + 1 = 0  (la general)
        r.explicita()             # "y = 2x + 1"
        r.punto_pendiente()       # "y - 3 = 2(x - 1)"
        r.vectorial()             # "(x, y) = (1, 3) + t·(1, 2)"
        r.parametricas()          # "x = 1 + t,  y = 3 + 2t"
        r.continua()              # "(x - 1)/1 = (y - 3)/2"
        r.pendiente, r.ordenada   # 2, 1
        r(4)                      # 9: lo que vale y cuando x = 4
        r.pasa_por((0, 1))        # True
    """

    __slots__ = ("a", "b", "c", "punto", "vector")

    def __init__(self, A, B=None, vector=None, pendiente=None):
        if isinstance(A, str) and B is None and vector is None and pendiente is None:
            otra = _leer_recta(A)
            for k in Recta.__slots__:
                setattr(self, k, getattr(otra, k))
            return
        P = _punto(A, "recta")
        dados = [B is not None, vector is not None, pendiente is not None]
        if sum(dados) != 1:
            raise TypeError("recta: dame un punto y otra cosa: otro punto, vector=(x, y) o pendiente=m. "
                            "Por ejemplo recta((1, 3), (2, 5))")
        if B is not None:
            Q = _punto(B, "recta", "el segundo punto")
            v = [Q[0] - P[0], Q[1] - P[1]]
            if v == [0, 0]:
                raise ValueError("recta: los dos puntos son el mismo, y por un punto pasan infinitas rectas")
        elif vector is not None:
            v = [_numero(n, "recta", "el vector") for n in _componentes(vector, "recta", "el vector")]
            if len(v) != 2:
                raise ValueError("recta: el vector tiene que tener 2 números")
            if all(n == 0 for n in v):
                raise ValueError("recta: el vector (0, 0) no tiene dirección")
        else:
            v = [Fraction(1), _numero(pendiente, "recta", "la pendiente")]
        self._poner(P, v)

    def _poner(self, P, v):
        a, b = v[1], -v[0]
        c = -(a * P[0] + b * P[1])
        a, b, c = _enteros(a, b, c)
        self.a, self.b, self.c = _bonito(a), _bonito(b), _bonito(c)
        self.punto = Vector(P)
        self.vector = Vector(v)

    @property
    def pendiente(self):
        """Lo que sube y cuando x avanza 1. None si la recta es vertical."""
        return None if self.b == 0 else _bonito(Fraction(-self.a) / self.b if _exactos(self) else -self.a / self.b)

    @property
    def ordenada(self):
        """Dónde corta al eje y (la n de y = mx + n). None si la recta es vertical."""
        return None if self.b == 0 else _bonito(Fraction(-self.c) / self.b if _exactos(self) else -self.c / self.b)

    def __call__(self, x):
        if self.b == 0:
            raise ValueError("la recta %s es vertical: no tiene un y para cada x" % self)
        if isinstance(x, float) or not _exactos(self):
            return _bonito((-self.a * float(x) - self.c) / self.b)
        x = _numero(x, "recta", "x")
        return _bonito((-self.a * x - self.c) / Fraction(self.b))

    def pasa_por(self, P):
        """True si el punto P está en la recta."""
        x, y = _punto(P, "pasa_por")
        v = self.a * x + self.b * y + self.c
        return abs(v) < 1e-9 if isinstance(v, float) else v == 0

    def general(self):
        """La ecuación general (o implícita): ax + by + c = 0."""
        return _lineal([(self.a, "x"), (self.b, "y"), (self.c, "")]) + " = 0"

    def explicita(self):
        """y = mx + n (o x = k si es vertical)."""
        if self.b == 0:
            return "x = " + _t(Fraction(-self.c) / self.a if _exactos(self) else -self.c / self.a)
        return "y = " + _lineal([(self.pendiente, "x"), (self.ordenada, "")])

    def punto_pendiente(self):
        """y - y₀ = m(x - x₀). Si es vertical no tiene, y sale x = k."""
        if self.b == 0 or self.a == 0:
            return self.explicita()
        x0, y0 = self.punto
        t = _t(self.pendiente)
        if "/" in t:
            delante = "-(%s)" % t[1:] if t.startswith("-") else "(%s)" % t
        else:
            delante = "-" if t == "-1" else "" if t == "1" else t
        return "%s = %s%s" % (_menos("y", y0), delante, "(%s)" % _menos("x", x0) if x0 != 0 else "x")

    def vectorial(self):
        """(x, y) = (x₀, y₀) + t·(v₁, v₂)."""
        return "(x, y) = %s + t·%s" % (_texto_vector(self.punto), _texto_vector(self.vector))

    def parametricas(self):
        """x = x₀ + t·v₁,  y = y₀ + t·v₂."""
        (x0, y0), (v1, v2) = self.punto, self.vector
        uno = lambda letra, p, v: "%s = %s" % (letra, _lineal([(p, ""), (v, "t")]) if p != 0 else _lineal([(v, "t")]))
        return uno("x", x0, v1) + ",  " + uno("y", y0, v2)

    def continua(self):
        """(x - x₀)/v₁ = (y - y₀)/v₂. Si el vector tiene un 0, no se puede escribir así."""
        (x0, y0), (v1, v2) = self.punto, self.vector
        if v1 == 0 or v2 == 0:
            return "no tiene ecuación continua (el vector %s tiene un 0)" % _texto_vector(self.vector)
        parte = lambda letra, p, v: ("(%s)" % _menos(letra, p) if p != 0 else letra) + "/" + (
            ("(%s)" % _t(v)) if v < 0 or "/" in _t(v) else _t(v))
        return parte("x", x0, v1) + " = " + parte("y", y0, v2)

    def __str__(self):
        return self.general()

    __repr__ = __str__

    def __eq__(self, otra):
        if not isinstance(otra, Recta):
            return NotImplemented
        return posicion_rectas(self, otra) == "coincidentes"

    def __ne__(self, otra):
        r = self.__eq__(otra)
        return r if r is NotImplemented else not r

    __hash__ = None


def _exactos(r):
    return not any(isinstance(n, float) for n in (r.a, r.b, r.c))


def _enteros(a, b, c):
    """Quita fracciones y factores comunes, y deja la x (o la y) en positivo: 4x - 2y + 2 -> 2x - y + 1."""
    if any(isinstance(n, float) for n in (a, b, c)):
        signo = 1 if (a if a != 0 else b) > 0 else -1
        return a * signo, b * signo, c * signo
    a, b, c = Fraction(a), Fraction(b), Fraction(c)
    den = 1
    for n in (a, b, c):
        den = den * n.denominator // math.gcd(den, n.denominator)
    a, b, c = int(a * den), int(b * den), int(c * den)
    g = math.gcd(math.gcd(abs(a), abs(b)), abs(c)) or 1
    a, b, c = a // g, b // g, c // g
    if a < 0 or (a == 0 and b < 0):
        a, b, c = -a, -b, -c
    return a, b, c


_TERMINO = re.compile(r"^([+-]?)(\d+(?:\.\d+)?(?:/\d+)?)?([xy]?)$")


def _lado(texto, original):
    total = {"x": Fraction(0), "y": Fraction(0), "": Fraction(0)}
    terminos = re.findall(r"[+-]?[^+-]+", texto)
    if "".join(terminos) != texto:
        raise ValueError("recta: no entiendo %r" % original)
    for termino in terminos:
        m = _TERMINO.match(termino)
        if not m or (m.group(2) is None and not m.group(3)):
            raise ValueError("recta: no entiendo el trozo %r de %r. Escríbela así: \"y = 2x + 1\" o "
                             "\"2x - y + 1 = 0\"" % (termino, original))
        signo, numero, letra = m.groups()
        n = Fraction(numero) if numero else Fraction(1)
        total[letra] += -n if signo == "-" else n
    return total


def _leer_recta(texto):
    t = texto.replace(" ", "").replace("−", "-").replace(",", ".").replace("*", "").replace("·", "")
    t = re.sub(r"\(([+-]?\d+(?:\.\d+)?/\d+)\)", r"\1", t)
    if t.count("=") != 1:
        raise ValueError("recta: la ecuación tiene que tener un =, como \"y = 2x + 1\" o \"2x - y + 1 = 0\"")
    izq, der = t.split("=")
    if not izq or not der:
        raise ValueError("recta: falta algo a un lado del = en %r" % texto)
    i, d = _lado(izq, texto), _lado(der, texto)
    a, b, c = i["x"] - d["x"], i["y"] - d["y"], i[""] - d[""]
    if a == 0 and b == 0:
        raise ValueError("recta: %r no tiene ni x ni y, así que no es una recta" % texto)
    a, b, c = _enteros(a, b, c)
    # un punto suyo y su vector director (-b, a), mirando a la derecha (o hacia arriba)
    P = [Fraction(0), Fraction(-c, b)] if b != 0 else [Fraction(-c, a), Fraction(0)]
    v = [-b, a]
    if v[0] < 0 or (v[0] == 0 and v[1] < 0):
        v = [b, -a]
    r = Recta.__new__(Recta)
    r._poner(P, [Fraction(n) for n in v])
    return r


def recta(A, B=None, vector=None, pendiente=None):
    """Hace una recta: por dos puntos, por un punto con un vector o con la pendiente, o escrita.

        r = pantalla.recta((1, 3), (2, 5))
        r = pantalla.recta((1, 3), vector=(1, 2))
        r = pantalla.recta((0, 1), pendiente=2)
        r = pantalla.recta("y = 2x + 1")
        r = pantalla.recta("2x - y + 1 = 0")

    Devuelve una Recta: print(r) sale la ecuación general, y tiene r.explicita(), r.vectorial()...
    """
    if isinstance(A, Recta):
        return A
    return Recta(A, B, vector, pendiente)


def ecuaciones_recta(A, B=None, vector=None, pendiente=None, x=None, y=None):
    """Escribe todas las ecuaciones de una recta: vectorial, paramétricas, continua, general,
    explícita y punto-pendiente. Devuelve la Recta.

        pantalla.ecuaciones_recta((1, 3), (2, 5))
        pantalla.ecuaciones_recta(r)                  # o una que ya tengas
    """
    r = recta(A, B, vector, pendiente)
    filas = [("Vectorial", r.vectorial()), ("Paramétricas", r.parametricas()), ("Continua", r.continua()),
             ("General", r.general()), ("Explícita", r.explicita())]
    if r.b != 0:
        filas.append(("Punto-pendiente", r.punto_pendiente()))
    w = max(len(n) for n, _ in filas)
    _sacar(["%s  %s" % ((n + ":").ljust(w + 1), e) for n, e in filas], x, y, "ecuaciones_recta")
    return r


def posicion_rectas(r, s):
    """Cómo están dos rectas: "secantes" (se cortan en un punto), "paralelas" o "coincidentes".

        pantalla.posicion_rectas(pantalla.recta("y = 2x"), pantalla.recta("y = 2x + 1"))   # "paralelas"
    """
    r, s = recta(r), recta(s)
    det = r.a * s.b - r.b * s.a
    if (abs(det) > 1e-9) if isinstance(det, float) else det != 0:
        return "secantes"
    # paralelas o la misma: miramos si un punto de una está en la otra
    return "coincidentes" if s.pasa_por(r.punto) else "paralelas"


def interseccion_rectas(r, s, pasos=False):
    """El punto donde se cortan dos rectas, o None si no se cortan (paralelas) o son la misma.

        pantalla.interseccion_rectas("y = 2x + 1", "x + y = 4")     # (1, 3)
        pantalla.interseccion_rectas(r, s, pasos=True)              # con el sistema
    """
    r, s = recta(r), recta(s)
    posicion = posicion_rectas(r, s)
    punto = None
    if posicion == "secantes":
        det = r.a * s.b - r.b * s.a
        exacto = _exactos(r) and _exactos(s)
        det_ = Fraction(det) if exacto else float(det)
        px = (-r.c * s.b + r.b * s.c) / det_
        py = (-r.a * s.c + r.c * s.a) / det_
        punto = Vector(px, py)
    if pasos:
        lineas = ["{ " + r.general(), "{ " + s.general()]
        if punto is None:
            lineas.append("No se cortan: son %s" % posicion)
        else:
            lineas.append("Se cortan en %s" % _texto_vector(punto))
        _sacar(lineas, None, None, "interseccion_rectas")
    return punto


def distancia_punto_recta(P, r, pasos=False):
    """La distancia (lo más corta) de un punto a una recta: |a·x₀ + b·y₀ + c| / √(a² + b²).

        pantalla.distancia_punto_recta((0, 0), "3x + 4y - 10 = 0")     # 2
        pantalla.distancia_punto_recta((1, 1), r, pasos=True)
    """
    x0, y0 = _punto(P, "distancia_punto_recta")
    r = recta(r)
    arriba = r.a * x0 + r.b * y0 + r.c
    abajo2 = r.a * r.a + r.b * r.b
    exacto = not any(isinstance(n, float) for n in (arriba, abajo2))
    raiz = None
    if exacto:
        n = math.isqrt(int(abajo2))
        raiz = n if n * n == abajo2 else None
    d = _bonito(abs(Fraction(arriba)) / raiz) if raiz else _bonito(abs(float(arriba)) / math.sqrt(abajo2))
    if pasos:
        p = lambda n: "(%s)" % _t(n) if _t(n).startswith("-") or "/" in _t(n) else _t(n)
        linea = "d = |%s·%s + %s·%s + %s| / √(%s² + %s²) = %s / %s" % (
            p(r.a), p(x0), p(r.b), p(y0), p(r.c), p(r.a), p(r.b), _t(abs(arriba)),
            _t(raiz) if raiz else "√" + _t(abajo2))
        linea += (" = " if raiz else " ≈ ") + (_t(d) if raiz else ("%.4f" % d).rstrip("0").rstrip("."))
        _sacar([linea], None, None, "distancia_punto_recta")
    return d


def angulo_rectas(r, s):
    """El ángulo entre dos rectas, en grados (de 0 a 90).

        pantalla.angulo_rectas("y = x", "y = -x")      # 90.0
    """
    r, s = recta(r), recta(s)
    u, v = r.vector, s.vector
    pe = abs(float(u[0] * v[0] + u[1] * v[1]))
    cos = pe / (math.hypot(float(u[0]), float(u[1])) * math.hypot(float(v[0]), float(v[1])))
    return _bonito(math.degrees(math.acos(max(-1.0, min(1.0, cos)))))
