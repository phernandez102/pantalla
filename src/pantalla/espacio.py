"""
Geometría en el espacio, la de 2º de bachillerato: puntos, rectas y planos en 3D con
todas sus ecuaciones, cómo están unos respecto a otros, dónde se cortan, distancias,
ángulos, proyecciones y simétricos. Con pasos=True escriben la cuenta.

    pi = pantalla.plano("x + y + z = 3")
    r = pantalla.recta((0, 0, 0), vector=(1, 1, 1))
    print(pantalla.posicion(r, pi))              # se cortan
    print(pantalla.interseccion(r, pi))          # (1, 1, 1)
    pantalla.distancia((0, 0, 0), pi, pasos=True)
    pantalla.ver_espacio({"π": pi, "r": r})      # para verlos y girarlos con el ratón

Las cuentas van con fracciones, como en los vectores y las matrices.
"""

import math
import re
from fractions import Fraction

from . import rectas as _rectas
from . import vectores as _vectores
from .matrices import _texto_numero, matriz, rango
from .numeros import _a_numero, _bonito, _sacar
from .vectores import Vector, _cero, _p, _texto_vector


class Punto(Vector):
    """Un punto. Sale como (1, 2, 3), igual que un Vector, pero al dibujarlo es un punto y no una flecha.

        P = pantalla.Punto(1, 2, 3)
        Q = P + (1, 0, 0)       # otro punto: (2, 2, 3)
        v = Q - P               # restar dos puntos da el Vector que va de uno a otro: (1, 0, 0)

    Lo que devuelven interseccion(), proyeccion(), simetrico() o punto_medio() son puntos.
    """

    __slots__ = ()

    def __add__(self, otro):
        r = Vector.__add__(self, otro)
        return r if r is NotImplemented else Punto(r)

    def __radd__(self, otro):
        r = Vector.__radd__(self, otro)
        return r if r is NotImplemented else Punto(r)

    def __sub__(self, otro):
        r = Vector.__sub__(self, otro)
        if r is NotImplemented or isinstance(otro, Punto):
            return r
        return Punto(r)

    def __mul__(self, k):
        r = Vector.__mul__(self, k)
        return r if r is NotImplemented else Punto(r)

    __rmul__ = __mul__

    def __truediv__(self, k):
        r = Vector.__truediv__(self, k)
        return r if r is NotImplemented else Punto(r)

    def __neg__(self):
        return Punto(Vector.__neg__(self))


# --- números y vectores por dentro ------------------------------------------

def _numero(n, funcion, que):
    n = _a_numero(n, funcion, que)
    return n if isinstance(n, float) else Fraction(n)


def _tres(P, funcion, que="el punto"):
    if isinstance(P, (str, bytes)) or not isinstance(P, (list, tuple)) or len(P) != 3:
        if isinstance(P, (list, tuple)) and len(P) == 2 and not isinstance(P, str):
            raise ValueError("%s: %s tiene 2 números, y en el espacio hacen falta 3: (x, y, z)" % (funcion, que))
        raise TypeError("%s: %s tiene que ser (x, y, z), con tres números, y me has dado %r" % (funcion, que, P))
    return [_numero(n, funcion, que) for n in P]


def _direccion(v, funcion, que="el vector"):
    v = _tres(v, funcion, que)
    if _nulo(v):
        raise ValueError("%s: %s (0, 0, 0) no tiene dirección" % (funcion, que))
    return v


def _resta(a, b):
    return [x - y for x, y in zip(a, b)]


def _suma(a, b):
    return [x + y for x, y in zip(a, b)]


def _por(k, a):
    return [k * x for x in a]


def _pe(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _px(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _nulo(v):
    return all(_cero(n) for n in v)


def _lista(v):
    return [n if isinstance(n, float) else Fraction(n) for n in v]


def _dividir(a, b):
    if isinstance(a, float) or isinstance(b, float):
        return float(a) / float(b)
    return Fraction(a) / Fraction(b)


def _enteros(numeros):
    """Quita fracciones y factores comunes, y deja en positivo el primero que no es 0: (2, -4, 2/3) -> (3, -6, 1)."""
    if any(isinstance(n, float) for n in numeros):
        primero = next((n for n in numeros if not _cero(n)), 1)
        return [n if primero > 0 else -n for n in numeros]
    numeros = [Fraction(n) for n in numeros]
    den = 1
    for n in numeros:
        den = den * n.denominator // math.gcd(den, n.denominator)
    enteros = [int(n * den) for n in numeros]
    g = 0
    for n in enteros:
        g = math.gcd(g, abs(n))
    g = g or 1
    enteros = [n // g for n in enteros]
    primero = next((n for n in enteros if n != 0), 1)
    return [Fraction(-n if primero < 0 else n) for n in enteros]


def _t(n):
    return _texto_numero(_bonito(n))


def _tv(v):
    return _texto_vector(v)


def _decimal(x):
    return ("%.4f" % x).rstrip("0").rstrip(".")


def _cuadrados(n):
    """n = fuera² · dentro, con dentro sin cuadrados: 72 -> (6, 2)."""
    fuera, dentro, k = 1, n, 2
    while k * k <= dentro:
        while dentro % (k * k) == 0:
            fuera, dentro = fuera * k, dentro // (k * k)
        k += 1
    return fuera, dentro


def _raiz_texto(N):
    """La raíz de N escrita lo más sencilla posible: 4 -> 2, 8 -> 2√2, 3/2 -> √6/2. None si N es un decimal."""
    if not isinstance(N, (int, Fraction)) or N < 0:
        return None
    N = Fraction(N)
    if N == 0:
        return "0"
    fuera, dentro = _cuadrados(N.numerator * N.denominator)
    den = N.denominator
    g = math.gcd(fuera, den)
    fuera, den = fuera // g, den // g
    texto = ("" if fuera == 1 and dentro != 1 else str(fuera)) + ("√%d" % dentro if dentro != 1 else "")
    return texto if den == 1 else texto + "/" + str(den)


def _raiz(N):
    """La raíz justa si la tiene; si no, un decimal."""
    if isinstance(N, (int, Fraction)) and N >= 0:
        N = Fraction(N)
        n, d = math.isqrt(N.numerator), math.isqrt(N.denominator)
        if n * n == N.numerator and d * d == N.denominator:
            return Fraction(n, d)
    return math.sqrt(N)


def _igual_raiz(N, valor):
    """' = 2√2 ≈ 2.8284', ' = 5' o ' ≈ 1.7321' para terminar una cuenta."""
    if isinstance(valor, Fraction):
        return " = " + _t(valor)
    texto = _raiz_texto(N)
    return (" = " + texto if texto else "") + " ≈ " + _decimal(valor)


def _modulo_texto(s):
    """|v| escrito desde la suma de los cuadrados: 9 -> 3, 8 -> 2√2, 6 -> √6."""
    texto = _raiz_texto(s)
    return texto if texto is not None else _decimal(math.sqrt(s))


# --- leer lo que escriben ----------------------------------------------------

# 2x, -y, 3/2, x/3 (como en la segmentaria), 2z/5
_TERMINO = re.compile(r"^([+-]?)(\d+(?:\.\d+)?(?:/\d+)?)?([a-zλμ]?)(?:/(\d+(?:\.\d+)?))?$")


def _limpio(texto):
    t = texto.replace(" ", "").replace("−", "-").replace("*", "").replace("·", "")
    t = re.sub(r"\(([+-]?\d+(?:\.\d+)?/\d+)\)", r"\1", t)
    # x/(-2) es -x/2 (sale en la segmentaria)
    cambia = lambda m: ("+" if m.group(1) == "-" else "-") + m.group(2) + "/" + m.group(3)
    t = re.sub(r"([+-]?)(\d*(?:\.\d+)?[a-zλμ])/\(-(\d+(?:\.\d+)?)\)", cambia, t)
    t = re.sub(r"/\(\+?(\d+(?:\.\d+)?)\)", r"/\1", t)
    return t[1:] if t.startswith("+") else t.replace("=+", "=")


def _lado(texto, original, funcion, letras):
    total = dict((l, Fraction(0)) for l in letras + [""])
    terminos = re.findall(r"[+-]?[^+-]+", texto)
    if not texto or "".join(terminos) != texto:
        raise ValueError("%s: no entiendo %r" % (funcion, original))
    for termino in terminos:
        m = _TERMINO.match(termino)
        if not m or (m.group(2) is None and not m.group(3)) or m.group(3) not in total or (m.group(4) and not m.group(3)):
            raise ValueError("%s: no entiendo el trozo %r de %r" % (funcion, termino, original))
        signo, numero, letra, abajo = m.groups()
        n = Fraction(numero) if numero else Fraction(1)
        if abajo:
            if Fraction(abajo) == 0:
                raise ValueError("%s: en %r se divide entre 0" % (funcion, original))
            n /= Fraction(abajo)
        total[letra] += -n if signo == "-" else n
    return total


def _ecuacion(texto, funcion, letras=("x", "y", "z")):
    """'2x - y = 3' -> {x: 2, y: -1, z: 0, '': -3} (todo pasado al lado izquierdo)."""
    t = _limpio(texto).replace(",", ".")
    if t.count("=") != 1:
        raise ValueError("%s: la ecuación tiene que tener un =, como \"2x - y + z = 3\"" % funcion)
    izq, der = t.split("=")
    if not izq or not der:
        raise ValueError("%s: falta algo a un lado del = en %r" % (funcion, texto))
    i, d = _lado(izq, texto, funcion, list(letras)), _lado(der, texto, funcion, list(letras))
    return dict((k, i[k] - d[k]) for k in i)


def _leer_plano(texto):
    e = _ecuacion(texto, "plano")
    if e["x"] == 0 and e["y"] == 0 and e["z"] == 0:
        raise ValueError("plano: %r no tiene ni x, ni y, ni z, así que no es un plano" % texto)
    return _plano_general(e["x"], e["y"], e["z"], e[""])


def _quitar_parentesis(t):
    while t.startswith("(") and t.endswith(")") and _parentesis_bien(t[1:-1]):
        t = t[1:-1]
    return t


def _parentesis_bien(t):
    n = 0
    for c in t:
        n += 1 if c == "(" else -1 if c == ")" else 0
        if n < 0:
            return False
    return n == 0


def _leer_continua(texto):
    """'(x - 1)/2 = (y + 1)/3 = z' -> punto (1, -1, 0) y vector (2, 3, 1)."""
    partes = _limpio(texto).replace(",", ".").split("=")
    if len(partes) != 3 or not all(partes):
        raise ValueError("recta: la continua tiene que tener dos =, como \"(x - 1)/2 = (y + 1)/3 = z/1\"")
    punto, vector = {}, {}
    for parte in partes:
        arriba, abajo = parte, "1"
        nivel = 0
        for i in range(len(parte) - 1, -1, -1):
            c = parte[i]
            nivel += 1 if c == ")" else -1 if c == "(" else 0
            if c == "/" and nivel == 0 and re.search("[xyz]", parte[:i]):
                arriba, abajo = parte[:i], parte[i + 1:]
                break
        arriba, abajo = _quitar_parentesis(arriba), _quitar_parentesis(abajo)
        try:
            den = Fraction(abajo)
        except (ValueError, ZeroDivisionError):
            raise ValueError("recta: no entiendo el denominador %r de %r" % (abajo, texto))
        e = _lado(arriba, texto, "recta", ["x", "y", "z"])
        letras = [l for l in "xyz" if e[l] != 0]
        if len(letras) != 1:
            raise ValueError("recta: en la continua cada trozo lleva una letra (x, y o z), y %r no" % parte)
        l = letras[0]
        if l in punto:
            raise ValueError("recta: la %s sale dos veces en %r" % (l, texto))
        # a·l + b = den·t  ->  l = -b/a + (den/a)·t
        punto[l], vector[l] = -e[""] / e[l], den / e[l]
    return [punto[l] for l in "xyz"], [vector[l] for l in "xyz"]


def _leer_parametricas(texto):
    trozos = [p for p in re.split(r"[;,\n]", texto.replace("{", "")) if p.strip()]
    punto, vector = {}, {}
    for trozo in trozos:
        t = _limpio(trozo)
        if t.count("=") != 1:
            raise ValueError("recta: no entiendo %r" % trozo.strip())
        izq, der = t.split("=")
        if izq not in ("x", "y", "z"):
            raise ValueError("recta: en las paramétricas cada trozo empieza por x =, y = o z =, y %r no" % trozo.strip())
        letra = next((l for l in "tλμks" if l in der), "t")
        e = _lado(der, texto, "recta", [letra])
        punto[izq], vector[izq] = e[""], e[letra]
    if sorted(punto) != ["x", "y", "z"]:
        raise ValueError("recta: en las paramétricas tienen que estar x, y y z")
    return [punto[l] for l in "xyz"], [vector[l] for l in "xyz"]


def _leer_vectorial(texto):
    numeros = []
    for trozo in re.findall(r"\(([^()]*)\)", texto):
        partes = [p.strip() for p in trozo.split(",")]
        if len(partes) != 3:
            continue
        try:
            numeros.append([_numero(p, "recta", "el punto") for p in partes])
        except (TypeError, ValueError):
            continue
    if len(numeros) != 2:
        raise ValueError("recta: no entiendo %r. Escríbela así: \"(x, y, z) = (1, 2, 3) + t·(1, 0, 2)\"" % texto)
    return numeros


def _leer_recta(texto):
    t = texto.strip()
    if t.count("=") >= 3:
        P, v = _leer_parametricas(t)
    elif t.count("=") == 2:
        P, v = _leer_continua(t)
    else:
        P, v = _leer_vectorial(t)
    if _nulo(v):
        raise ValueError("recta: el vector de %r es (0, 0, 0) y no tiene dirección" % texto)
    return Recta3D(P, vector=v)


def _es_texto_recta(texto):
    t = _limpio(texto)
    if t.count("=") != 1:
        return True
    return bool(re.search(r"[tλ]", t))


def _leer(texto, funcion):
    """Un plano o una recta escritos: decide qué es por cómo está escrito."""
    if not isinstance(texto, str):
        return texto
    if _es_texto_recta(texto):
        return _leer_recta(texto)
    if "z" not in texto:
        return _rectas.recta(texto)
    return _leer_plano(texto)


def _como_plano(x):
    if isinstance(x, Plano):
        return x
    if isinstance(x, str) and not _es_texto_recta(x) and "z" in x:
        return _leer_plano(x)
    return None


# --- rectas -------------------------------------------------------------------

class Recta3D(object):
    """Una recta del espacio: un punto por el que pasa y un vector que dice hacia dónde va.

        r = pantalla.recta((1, 2, 3), (2, 2, 5))              # por dos puntos
        r = pantalla.recta((1, 2, 3), vector=(1, 0, 2))       # por un punto con un vector
        r = pantalla.recta("(x - 1)/1 = (y - 2)/0 = (z - 3)/2")   # en continua
        r = pantalla.recta("x + y = 3", "z = 1")              # donde se cortan dos planos
        r = pantalla.recta(P, perpendicular=pi)               # por P y perpendicular al plano pi
        r = pantalla.recta(P, paralela=s)                     # por P y paralela a la recta s

        print(r)                # (x, y, z) = (1, 2, 3) + t·(1, 0, 2)
        r.parametricas()        # "x = 1 + t,  y = 2,  z = 3 + 2t"
        r.continua()            # "(x - 1)/1 = (y - 2)/0 = (z - 3)/2"
        r.implicitas()          # "y - 2 = 0,  2x - z + 1 = 0"  (dos planos que se cortan en ella)
        r.punto, r.vector       # (1, 2, 3), (1, 0, 2)
        r(2)                    # el punto que sale con t = 2: (3, 2, 7)
        r.pasa_por((2, 2, 5))   # True
    """

    __slots__ = ("punto", "vector")

    def __init__(self, A, B=None, vector=None, perpendicular=None, paralela=None):
        if isinstance(A, str) and isinstance(B, str):
            pi, sigma = _leer_plano(A), _leer_plano(B)
        else:
            pi, sigma = _como_plano(A), _como_plano(B)
        if pi is not None:
            if sigma is None:
                raise TypeError("recta: con un plano solo no hay recta. Dame dos planos: recta(pi, sigma)")
            r = _corte_planos(pi, sigma)
            if not isinstance(r, Recta3D):
                raise ValueError("recta: los planos %s y %s no se cortan en una recta: son %s"
                                 % (pi, sigma, "coincidentes" if r is not None else "paralelos"))
            self.punto, self.vector = r.punto, r.vector
            return
        if isinstance(A, str) and B is None and vector is None and perpendicular is None and paralela is None:
            r = _leer_recta(A)
            self.punto, self.vector = r.punto, r.vector
            return
        P = _tres(A, "recta")
        dados = [B is not None, vector is not None, perpendicular is not None, paralela is not None]
        if sum(dados) != 1:
            raise TypeError("recta: dame un punto y otra cosa: otro punto, vector=(x, y, z), "
                            "perpendicular=un plano o paralela=una recta. Por ejemplo recta((1, 2, 3), (2, 2, 5))")
        if B is not None:
            Q = _tres(B, "recta", "el segundo punto")
            v = _resta(Q, P)
            if _nulo(v):
                raise ValueError("recta: los dos puntos son el mismo, y por un punto pasan infinitas rectas")
        elif vector is not None:
            v = _direccion(vector, "recta")
        elif perpendicular is not None:
            otro = _leer(perpendicular, "recta")
            if isinstance(otro, Plano):
                v = list(otro.normal)
            elif isinstance(otro, Recta3D):
                pie = _pie_en_recta(P, otro)
                v = _resta(pie, P)
                if _nulo(v):
                    raise ValueError("recta: el punto está en la recta, así que hay infinitas perpendiculares "
                                     "que pasan por él")
            else:
                raise TypeError("recta: perpendicular= tiene que ser un plano o una recta del espacio")
        else:
            otra = _leer(paralela, "recta")
            if not isinstance(otra, Recta3D):
                raise TypeError("recta: paralela= tiene que ser una recta del espacio. Paralelas a un plano "
                                "por un punto hay infinitas")
            v = list(otra.vector)
        self.punto, self.vector = Punto(P), Vector(v)

    def _P(self):
        return _lista(self.punto)

    def _v(self):
        return _lista(self.vector)

    def __call__(self, t):
        t = _numero(t, "recta", "t")
        return Punto(_suma(self._P(), _por(t, self._v())))

    def pasa_por(self, P):
        """True si el punto P está en la recta."""
        P = _tres(P, "pasa_por")
        return _nulo(_px(_resta(P, self._P()), self._v()))

    def vectorial(self):
        """(x, y, z) = (x₀, y₀, z₀) + t·(v₁, v₂, v₃)."""
        return "(x, y, z) = %s + t·%s" % (_tv(self.punto), _tv(self.vector))

    def parametricas(self):
        """x = x₀ + t·v₁,  y = y₀ + t·v₂,  z = z₀ + t·v₃."""
        uno = lambda letra, p, v: "%s = %s" % (letra, _rectas._lineal([(p, ""), (v, "t")]))
        return ",  ".join(uno(l, p, v) for l, p, v in zip("xyz", self.punto, self.vector))

    def continua(self):
        """(x - x₀)/v₁ = (y - y₀)/v₂ = (z - z₀)/v₃. Si el vector tiene un 0, se pone /0 (es una forma de escribirla)."""
        def parte(letra, p, v):
            arriba = "(%s)" % _rectas._menos(letra, p) if p != 0 else letra
            t = _t(v)
            return arriba + "/" + ("(%s)" % t if v < 0 or "/" in t else t)
        return " = ".join(parte(l, p, v) for l, p, v in zip("xyz", self.punto, self.vector))

    def planos(self):
        """Dos planos que se cortan en esta recta (sus implícitas), sacados de la continua."""
        (x0, y0, z0), (v1, v2, v3) = self._P(), self._v()
        # de (x - x0)/v1 = (y - y0)/v2 sale v2·x - v1·y + ... = 0, y lo mismo con las otras parejas
        ecuaciones = [(v2, -v1, 0, v1 * y0 - v2 * x0), (0, v3, -v2, v2 * z0 - v3 * y0), (v3, 0, -v1, v1 * z0 - v3 * x0)]
        ecuaciones = [e for e in ecuaciones if not _nulo(e[:3])]
        for i in range(len(ecuaciones)):
            for j in range(i + 1, len(ecuaciones)):
                if not _nulo(_px(ecuaciones[i][:3], ecuaciones[j][:3])):
                    return _plano_general(*ecuaciones[i]), _plano_general(*ecuaciones[j])
        raise ValueError("recta: no he podido sacar las implícitas")

    def implicitas(self):
        """Las dos ecuaciones (de dos planos) que la forman: "y - 2 = 0,  2x - z + 1 = 0"."""
        a, b = self.planos()
        return a.general() + ",  " + b.general()

    def __str__(self):
        return self.vectorial()

    __repr__ = __str__

    def __eq__(self, otra):
        if not isinstance(otra, Recta3D):
            return NotImplemented
        return posicion(self, otra) == "coincidentes"

    def __ne__(self, otra):
        r = self.__eq__(otra)
        return r if r is NotImplemented else not r

    __hash__ = None


# --- planos -------------------------------------------------------------------

def _plano_general(a, b, c, d):
    """El plano ax + by + cz + d = 0 con un punto suyo y dos vectores, como se sacan en clase:
    se despeja la letra que tenga un 1 (o la más sencilla) y las otras dos son λ y μ."""
    a, b, c, d = _enteros([a, b, c, d])
    n = [a, b, c]
    orden = [2, 1, 0]
    candidatos = [k for k in orden if not _cero(n[k])]
    unos = [k for k in candidatos if abs(n[k]) == 1]
    k = unos[0] if unos else min(candidatos, key=lambda i: (abs(n[i]), orden.index(i)))
    libres = [i for i in range(3) if i != k]
    P = [Fraction(0)] * 3
    P[k] = _dividir(-d, n[k])
    vectores = []
    for j in libres:
        w = [Fraction(0)] * 3
        if abs(n[k]) == 1:
            w[j], w[k] = Fraction(1), _dividir(-n[j], n[k])
        else:
            w[j], w[k] = abs(n[k]), -n[j] if n[k] > 0 else n[j]
        vectores.append(w)
    p = Plano.__new__(Plano)
    p._poner(P, n, vectores[0], vectores[1])
    return p


class Plano(object):
    """Un plano del espacio: ax + by + cz + d = 0.

        pi = pantalla.plano("2x - y + z = 3")                     # escrito
        pi = pantalla.plano((1, 0, 0), (0, 1, 0), (0, 0, 1))      # por tres puntos
        pi = pantalla.plano((1, 2, 3), normal=(2, -1, 1))         # por un punto, con el vector normal
        pi = pantalla.plano((1, 2, 3), vectores=[(1, 0, 0), (0, 1, 1)])   # un punto y dos vectores
        pi = pantalla.plano(r, (1, 0, 0))                         # una recta y un punto fuera de ella
        pi = pantalla.plano(r, s)                                 # dos rectas que se cortan o son paralelas
        pi = pantalla.plano(r, paralelo=s)                        # contiene a r y es paralelo a s
        pi = pantalla.plano(r, perpendicular=sigma)               # contiene a r y es perpendicular a sigma
        pi = pantalla.plano(P, perpendicular=r)                   # por P y perpendicular a la recta r
        pi = pantalla.plano(P, paralelo=sigma)                    # por P y paralelo al plano sigma

        print(pi)                 # 2x - y + z - 3 = 0   (la general)
        pi.vectorial()            # "(x, y, z) = (0, 0, 3) + λ·(1, 0, -2) + μ·(0, 1, 1)"
        pi.parametricas()         # "x = λ,  y = μ,  z = 3 - 2λ + μ"
        pi.punto_normal()         # "2x - y + (z - 3) = 0": con el vector normal y el punto
        pi.segmentaria()          # "x/(3/2) + y/(-3) + z/3 = 1": dónde corta a los ejes
        pi.normal                 # (2, -1, 1)
        pi.pasa_por((1, 0, 1))    # True
    """

    __slots__ = ("a", "b", "c", "d", "punto", "u", "v")

    def __init__(self, A, B=None, C=None, normal=None, vectores=None, perpendicular=None, paralelo=None):
        if isinstance(A, str) and all(x is None for x in (B, C, normal, vectores, perpendicular, paralelo)):
            self._copiar(_leer_plano(A))
            return
        A = _leer(A, "plano")
        if isinstance(B, str):
            B = _leer(B, "plano")
        if isinstance(A, Plano) and B is None and C is None and all(
                x is None for x in (normal, vectores, perpendicular, paralelo)):
            self._copiar(A)
            return
        if isinstance(B, Recta3D) and not isinstance(A, Recta3D):
            A, B = B, A
        if isinstance(A, Recta3D):
            self._con_recta(A, B, C, normal, vectores, perpendicular, paralelo)
            return
        P = _tres(A, "plano")
        if isinstance(B, Vector) and not isinstance(B, Punto) and isinstance(C, Vector) and not isinstance(C, Punto):
            vectores, B, C = (B, C), None, None
        dados = [B is not None or C is not None, normal is not None, vectores is not None,
                 perpendicular is not None, paralelo is not None]
        if sum(dados) != 1:
            raise TypeError("plano: dame tres puntos, o un punto y otra cosa: normal=(a, b, c), vectores=[u, v], "
                            "perpendicular=una recta o paralelo=un plano. Por ejemplo plano((1, 0, 0), (0, 1, 0), (0, 0, 1))")
        if B is not None or C is not None:
            if B is None or C is None:
                raise TypeError("plano: con dos puntos no basta, por dos puntos pasan infinitos planos. Dame tres")
            Q, R = _tres(B, "plano", "el segundo punto"), _tres(C, "plano", "el tercer punto")
            u, v = _resta(Q, P), _resta(R, P)
            n = _px(u, v)
            if _nulo(n):
                raise ValueError("plano: los tres puntos están en línea recta, así que por ellos pasan infinitos planos")
            self._poner(P, n, u, v)
        elif normal is not None:
            self._poner(P, _direccion(normal, "plano", "el vector normal"))
        elif vectores is not None:
            if not isinstance(vectores, (list, tuple)) or len(vectores) != 2:
                raise TypeError("plano: vectores= son dos vectores, por ejemplo vectores=[(1, 0, 0), (0, 1, 1)]")
            u = _direccion(vectores[0], "plano", "el primer vector")
            v = _direccion(vectores[1], "plano", "el segundo vector")
            n = _px(u, v)
            if _nulo(n):
                raise ValueError("plano: los dos vectores son paralelos y con ellos no sale un plano")
            self._poner(P, n, u, v)
        elif perpendicular is not None:
            r = _leer(perpendicular, "plano")
            if isinstance(r, Plano):
                raise ValueError("plano: por un punto hay infinitos planos perpendiculares a un plano. "
                                 "Usa plano(r, perpendicular=pi) con una recta r")
            if not isinstance(r, Recta3D):
                raise TypeError("plano: perpendicular= tiene que ser una recta del espacio")
            self._poner(P, r._v())
        else:
            otro = _leer(paralelo, "plano")
            if not isinstance(otro, Plano):
                raise TypeError("plano: paralelo= tiene que ser un plano. Para un plano paralelo a una recta usa "
                                "plano(r, paralelo=s), con una recta r que esté dentro")
            self._poner(P, list(otro.normal))

    def _con_recta(self, r, B, C, normal, vectores, perpendicular, paralelo):
        if C is not None or normal is not None or vectores is not None:
            raise TypeError("plano: con una recta dame otra cosa: un punto, otra recta, paralelo= o perpendicular=")
        P, u = r._P(), r._v()
        if paralelo is not None:
            s = _leer(paralelo, "plano")
            if not isinstance(s, Recta3D):
                raise TypeError("plano: paralelo= tiene que ser una recta")
            n = _px(u, s._v())
            if _nulo(n):
                raise ValueError("plano: las dos rectas son paralelas, así que hay infinitos planos así")
            self._poner(P, n, u, s._v())
        elif perpendicular is not None:
            sigma = _leer(perpendicular, "plano")
            if not isinstance(sigma, Plano):
                raise TypeError("plano: perpendicular= tiene que ser un plano")
            n = _px(u, list(sigma.normal))
            if _nulo(n):
                raise ValueError("plano: la recta es perpendicular al plano, así que hay infinitos planos así")
            self._poner(P, n, u, list(sigma.normal))
        elif isinstance(B, Recta3D):
            Q, v = B._P(), B._v()
            n = _px(u, v)
            if _nulo(n):
                w = _resta(Q, P)
                n = _px(u, w)
                if _nulo(n):
                    raise ValueError("plano: las dos rectas son la misma, y hay infinitos planos que la contienen")
                self._poner(P, n, u, w)
            else:
                if not _cero(_pe(_resta(Q, P), n)):
                    raise ValueError("plano: las rectas se cruzan (ni se cortan ni son paralelas), "
                                     "así que no hay ningún plano que tenga a las dos")
                self._poner(P, n, u, v)
        elif B is not None:
            Q = _tres(B, "plano", "el punto")
            w = _resta(Q, P)
            n = _px(u, w)
            if _nulo(n):
                raise ValueError("plano: el punto está en la recta, y hay infinitos planos que los contienen")
            self._poner(P, n, u, w)
        else:
            raise TypeError("plano: con una recta sola hay infinitos planos. Dame también un punto u otra recta")

    def _copiar(self, otro):
        for k in Plano.__slots__:
            setattr(self, k, getattr(otro, k))

    def _poner(self, P, n, u=None, v=None):
        P = _lista(P)
        a, b, c = _enteros(n)
        a, b, c, d = _enteros([a, b, c, -(a * P[0] + b * P[1] + c * P[2])])
        self.a, self.b, self.c, self.d = _bonito(a), _bonito(b), _bonito(c), _bonito(d)
        if u is None:
            otro = _plano_general(a, b, c, d)
            self.punto, self.u, self.v = Punto(P), otro.u, otro.v
        else:
            self.punto, self.u, self.v = Punto(P), Vector(u), Vector(v)

    @property
    def normal(self):
        """El vector normal (perpendicular al plano): (a, b, c)."""
        return Vector(self.a, self.b, self.c)

    def _n(self):
        return _lista([self.a, self.b, self.c])

    def _P(self):
        return _lista(self.punto)

    def _u(self):
        return _lista(self.u)

    def _w(self):
        return _lista(self.v)

    def _valor(self, P):
        return _pe(self._n(), P) + self.d

    def pasa_por(self, P):
        """True si el punto P está en el plano."""
        return _cero(self._valor(_tres(P, "pasa_por")))

    def contiene(self, r):
        """True si la recta r está entera dentro del plano."""
        r = recta(r)
        return self.pasa_por(r.punto) and _cero(_pe(self._n(), r._v()))

    def general(self):
        """La ecuación general (o implícita): ax + by + cz + d = 0."""
        return _rectas._lineal([(self.a, "x"), (self.b, "y"), (self.c, "z"), (self.d, "")]) + " = 0"

    def segmentaria(self):
        """x/a + y/b + z/c = 1, con los puntos donde corta a los ejes (si los corta a los tres)."""
        if any(_cero(n) for n in (self.a, self.b, self.c, self.d)):
            return "no tiene ecuación segmentaria (%s)" % (
                "pasa por el origen" if _cero(self.d) else "es paralelo a algún eje")
        partes = []
        for letra, n in zip("xyz", (self.a, self.b, self.c)):
            corte = _bonito(_dividir(-self.d, n))
            t = _t(corte)
            partes.append("%s/%s" % (letra, "(%s)" % t if "/" in t or t.startswith("-") else t))
        return " + ".join(partes) + " = 1"

    def vectorial(self):
        """(x, y, z) = P + λ·u + μ·v."""
        return "(x, y, z) = %s + λ·%s + μ·%s" % (_tv(self.punto), _tv(self.u), _tv(self.v))

    def parametricas(self):
        """x = x₀ + λu₁ + μv₁,  y = ...,  z = ..."""
        return ",  ".join("%s = %s" % (l, _rectas._lineal([(p, ""), (a, "λ"), (b, "μ")]))
                          for l, p, a, b in zip("xyz", self.punto, self.u, self.v))

    def punto_normal(self):
        """a(x - x₀) + b(y - y₀) + c(z - z₀) = 0, con el punto y el vector normal."""
        partes = []
        for letra, n, p in zip("xyz", self.normal, self.punto):
            if n == 0:
                continue
            dentro = _rectas._menos(letra, p)
            t = _t(abs(n))
            pieza = ("" if t == "1" else ("(%s)" % t if "/" in t else t)) + ("(%s)" % dentro if p != 0 else letra)
            if not partes:
                partes.append(("-" if n < 0 else "") + pieza)
            else:
                partes.append((" - " if n < 0 else " + ") + pieza)
        return "".join(partes) + " = 0"

    def __str__(self):
        return self.general()

    __repr__ = __str__

    def __eq__(self, otro):
        if not isinstance(otro, Plano):
            return NotImplemented
        return posicion(self, otro) == "coincidentes"

    def __ne__(self, otro):
        r = self.__eq__(otro)
        return r if r is NotImplemented else not r

    __hash__ = None


def plano(A, B=None, C=None, normal=None, vectores=None, perpendicular=None, paralelo=None):
    """Hace un plano: escrito, por tres puntos, por un punto y el vector normal, por un punto y dos
    vectores, o con rectas.

        pi = pantalla.plano("2x - y + z = 3")
        pi = pantalla.plano((1, 0, 0), (0, 1, 0), (0, 0, 1))
        pi = pantalla.plano((1, 2, 3), normal=(2, -1, 1))
        pi = pantalla.plano((1, 2, 3), vectores=[(1, 0, 0), (0, 1, 1)])
        pi = pantalla.plano(r, (1, 0, 0))          # una recta y un punto
        pi = pantalla.plano(r, s)                  # dos rectas que se cortan o son paralelas
        pi = pantalla.plano(r, paralelo=s)         # contiene a r y es paralelo a s
        pi = pantalla.plano(P, perpendicular=r)    # por P y perpendicular a r
        pi = pantalla.plano(P, paralelo=sigma)     # por P y paralelo a sigma

    Devuelve un Plano: print(pi) sale la ecuación general, y tiene pi.vectorial(), pi.parametricas()...
    """
    if isinstance(A, Plano) and all(x is None for x in (B, C, normal, vectores, perpendicular, paralelo)):
        return A
    return Plano(A, B, C, normal, vectores, perpendicular, paralelo)


def recta(A, B=None, vector=None, perpendicular=None, paralela=None):
    """La recta del espacio (para el plano mira pantalla.recta, que hace las dos)."""
    if isinstance(A, Recta3D) and B is None and vector is None and perpendicular is None and paralela is None:
        return A
    if isinstance(A, str) and B is None and vector is None and perpendicular is None and paralela is None:
        r = _leer(A, "recta")
        if isinstance(r, Plano):
            raise ValueError("recta: %r es un plano (tiene un = y x, y, z). Para una recta del espacio "
                             "escribe dos planos: recta(\"x + y = 1\", \"z = 2\") o la continua" % A)
        return r
    return Recta3D(A, B, vector, perpendicular, paralela)


def _es_3d(A, B=None, vector=None, perpendicular=None, paralela=None):
    for x in (A, B, vector, perpendicular, paralela):
        if isinstance(x, (Plano, Recta3D)):
            return True
        if isinstance(x, (list, tuple)) and len(x) == 3:
            return True
    if isinstance(A, str):
        if isinstance(B, str):
            return True
        return _es_texto_recta(A) or "z" in A
    return False


# --- de qué tipo es cada cosa -------------------------------------------------

def _cosa(x, funcion, que):
    """('punto' | 'recta' | 'plano' | 'recta2d', el objeto)"""
    if isinstance(x, str):
        x = _leer(x, funcion)
    if isinstance(x, Plano):
        return "plano", x
    if isinstance(x, Recta3D):
        return "recta", x
    if isinstance(x, _rectas.Recta):
        return "recta2d", x
    if isinstance(x, (list, tuple)) and len(x) in (2, 3) and not any(isinstance(n, (list, tuple)) for n in x):
        return "punto", [_numero(n, funcion, que) for n in x]
    raise TypeError("%s: %s tiene que ser un punto (x, y, z), una recta o un plano, y me has dado %r" % (funcion, que, x))


def _es_del_espacio(x):
    if isinstance(x, (Plano, Recta3D)):
        return True
    if isinstance(x, (list, tuple)):
        return len(x) == 3
    return isinstance(x, str) and ("z" in x or _es_texto_recta(x))


def _leer_con(x, espacio):
    """Un texto como "x = 3" es una recta en el plano, pero si lo de al lado es del espacio es un plano."""
    if isinstance(x, str) and espacio and not _es_texto_recta(x):
        return _leer_plano(x)
    return _leer(x, "")


def _dos(a, b, funcion):
    espacio = _es_del_espacio(a) or _es_del_espacio(b)
    a, b = _leer_con(a, espacio), _leer_con(b, espacio)
    ta, a = _cosa(a, funcion, "lo primero")
    tb, b = _cosa(b, funcion, "lo segundo")
    for t, x in ((ta, a), (tb, b)):
        if t == "punto" and len(x) == 2 and "recta2d" not in (ta, tb) and (ta, tb) != ("punto", "punto"):
            raise ValueError("%s: el punto %s tiene 2 números, y en el espacio hacen falta 3: (x, y, z)" % (funcion, _tv(x)))
    if "recta2d" in (ta, tb) and ({ta, tb} - {"recta2d", "punto"}):
        raise TypeError("%s: no puedo mezclar una recta del plano (x, y) con cosas del espacio (x, y, z)" % funcion)
    return ta, a, tb, b


# --- posición -------------------------------------------------------------------

def _pos_rectas(r, s):
    u, v, w = r._v(), s._v(), _resta(s._P(), r._P())
    r1, r2 = rango([u, v]), rango([u, v, w])
    return {(1, 1): "coincidentes", (1, 2): "paralelas", (2, 2): "se cortan", (2, 3): "se cruzan"}[(r1, r2)], (r1, r2)


def _pos_recta_plano(r, pi):
    vn = _pe(r._v(), pi._n())
    if not _cero(vn):
        return "se cortan", vn
    return ("contenida" if pi.pasa_por(r.punto) else "paralela"), vn


def _pos_planos(pi, sigma):
    if not _nulo(_px(pi._n(), sigma._n())):
        return "se cortan"
    return "coincidentes" if sigma.pasa_por(pi.punto) else "paralelos"


def _filas(planos):
    return [[p.a, p.b, p.c, -p.d] for p in planos]


def _pos_tres(planos):
    M = _filas(planos)
    rm, ra = rango([f[:3] for f in M]), rango(M)
    pares = [(i, j) for i in range(3) for j in range(i + 1, 3)]
    tipos = [_pos_planos(planos[i], planos[j]) for i, j in pares]
    if rm == 3:
        texto = "se cortan en un punto"
    elif rm == 2 and ra == 3:
        texto = "dos son paralelos y el otro los corta" if "paralelos" in tipos else "se cortan dos a dos"
    elif rm == 2:
        texto = "dos coinciden y el otro los corta" if "coincidentes" in tipos else "se cortan en una recta"
    elif ra == 2:
        texto = "dos coinciden y el otro es paralelo" if "coincidentes" in tipos else "paralelos"
    else:
        texto = "coincidentes"
    return texto, rm, ra


def posicion(a, b, c=None, pasos=False):
    """Cómo están dos cosas del espacio una respecto a la otra (o tres planos).

        pantalla.posicion(r, s)        # "coincidentes", "paralelas", "se cortan" o "se cruzan"
        pantalla.posicion(r, pi)       # "contenida", "paralela" o "se cortan"
        pantalla.posicion(pi, sigma)   # "coincidentes", "paralelos" o "se cortan"
        pantalla.posicion(P, pi)       # "está en el plano" o "no está en el plano"
        pantalla.posicion(P, r)        # "está en la recta" o "no está en la recta"
        pantalla.posicion(pi, sigma, rho)     # tres planos: "se cortan en un punto", "se cortan en una recta"...
        pantalla.posicion(r, s, pasos=True)   # con los rangos, como en clase

    Valen rectas y planos de pantalla.recta() y pantalla.plano(), o escritos: "x + y + z = 3".
    """
    if c is not None:
        planos = [plano(x) if not isinstance(x, Plano) else x for x in (a, b, c)]
        texto, rm, ra = _pos_tres(planos)
        if pasos:
            matriz(_filas(planos), nombre="M*", ampliada=True)
            _sacar(["rango(M) = %d,  rango(M*) = %d" % (rm, ra), "Los tres planos: " + texto], None, None, "posicion")
        return texto
    ta, a, tb, b = _dos(a, b, "posicion")
    if ta == "recta2d" and tb == "recta2d":
        return _rectas.posicion_rectas(a, b)
    if ta != "punto" and tb == "punto" or (ta == "plano" and tb == "recta"):
        ta, a, tb, b = tb, b, ta, a
    lineas = []
    if ta == "punto" and tb == "punto":
        texto = "el mismo punto" if len(a) == len(b) and _nulo(_resta(a, b)) else "distintos"
    elif ta == "punto" and tb in ("recta", "recta2d"):
        dentro = b.pasa_por(a)
        texto = "está en la recta" if dentro else "no está en la recta"
        if pasos and tb == "recta":
            w = _resta(a, b._P())
            lineas = ["AP = P - A = %s - %s = %s" % (_tv(a), _tv(b.punto), _tv(w)),
                      "AP × v = %s × %s = %s" % (_tv(w), _tv(b.vector), _tv(_px(w, b._v()))),
                      ("Es (0, 0, 0): son paralelos, así que P está en la recta" if dentro else
                       "No es (0, 0, 0): P no está en la recta")]
    elif ta == "punto" and tb == "plano":
        valor = b._valor(a)
        texto = "está en el plano" if _cero(valor) else "no está en el plano"
        if pasos:
            lineas = ["Sustituyo P%s en %s:" % (_tv(a), b.general()),
                      "%s = %s" % (_sustituido(b, a), _t(valor)),
                      ("Da 0, así que P está en el plano" if _cero(valor) else "No da 0, así que P no está en el plano")]
    elif ta == "recta" and tb == "recta":
        texto, (r1, r2) = _pos_rectas(a, b)
        if pasos:
            w = _resta(b._P(), a._P())
            lineas = ["u = %s,  v = %s,  AB = B - A = %s" % (_tv(a.vector), _tv(b.vector), _tv(w)),
                      "rango(u, v) = %d,  rango(u, v, AB) = %d" % (r1, r2),
                      "Las rectas " + ("son " if texto in ("coincidentes", "paralelas") else "") + texto]
    elif ta == "recta" and tb == "plano":
        texto, vn = _pos_recta_plano(a, b)
        if pasos:
            lineas = ["v · n = %s · %s = %s" % (_tv(a.vector), _tv(b.normal), _t(vn))]
            if texto == "se cortan":
                lineas.append("No da 0: la recta corta al plano en un punto")
            else:
                lineas.append("Da 0: la recta es paralela al plano o está dentro")
                lineas.append("El punto %s de la recta %s en el plano: la recta %s" % (
                    _tv(a.punto), "está" if texto == "contenida" else "no está",
                    "está contenida en el plano" if texto == "contenida" else "es paralela al plano"))
    else:
        texto = _pos_planos(a, b)
        if pasos:
            M = _filas([a, b])
            rm, ra = rango([f[:3] for f in M]), rango(M)
            matriz(M, nombre="M*", ampliada=True)
            lineas = ["rango(M) = %d,  rango(M*) = %d" % (rm, ra),
                      "Los planos " + ("son " if texto != "se cortan" else "") + texto +
                      (" en una recta" if texto == "se cortan" else "")]
    if lineas:
        _sacar(lineas, None, None, "posicion")
    return texto


def _sustituido(pi, P):
    """2·1 + (-1)·2 + 1·3 - 3"""
    partes = []
    for n, x in zip(pi._n(), P):
        if _cero(n):
            continue
        partes.append("%s·%s" % (_p(n), _p(x)))
    texto = " + ".join(partes) if partes else "0"
    if not _cero(pi.d):
        texto += (" - " if pi.d < 0 else " + ") + _t(abs(pi.d))
    return texto


# --- dónde se cortan ----------------------------------------------------------

def _corte_recta_plano(r, pi):
    """(punto, t) o (None, None) si no se cortan, o (r, None) si está dentro."""
    vn = _pe(r._v(), pi._n())
    k = pi._valor(r._P())
    if _cero(vn):
        return (r if _cero(k) else None), None
    t = _dividir(-k, vn)
    return Punto(_suma(r._P(), _por(t, r._v()))), t


def _resolver2(a1, b1, c1, a2, b2, c2):
    """a1·x + b1·y = c1, a2·x + b2·y = c2 -> (x, y), o None."""
    det = a1 * b2 - a2 * b1
    if _cero(det):
        return None
    return _dividir(c1 * b2 - c2 * b1, det), _dividir(a1 * c2 - a2 * c1, det)


def _corte_planos(pi, sigma):
    n1, n2 = pi._n(), sigma._n()
    v = _px(n1, n2)
    if _nulo(v):
        return pi if sigma.pasa_por(pi.punto) else None
    # una letra vale 0 y se resuelven las otras dos (primero z = 0, luego y = 0, luego x = 0)
    for cero in (2, 1, 0):
        i, j = [k for k in range(3) if k != cero]
        sol = _resolver2(n1[i], n1[j], -pi.d, n2[i], n2[j], -sigma.d)
        if sol is not None:
            P = [Fraction(0)] * 3
            P[i], P[j] = sol
            return Recta3D(P, vector=_enteros(v))
    raise ValueError("interseccion: no he podido cortar los planos")


def _corte_rectas(r, s):
    """(punto, t, s) si se cortan."""
    u, v, w = r._v(), s._v(), _resta(s._P(), r._P())
    # t·u - k·v = w, con dos de las tres ecuaciones
    for i, j in ((0, 1), (0, 2), (1, 2)):
        sol = _resolver2(u[i], -v[i], w[i], u[j], -v[j], w[j])
        if sol is not None:
            t, k = sol
            return Punto(_suma(r._P(), _por(t, u))), t, k
    return None, None, None


def _cuenta_sustitucion(r, pi):
    """Las paramétricas de r metidas en el plano: 2(1 + t) - (2t) + (3 + t) - 3 = 0."""
    partes = []
    for n, p, v in zip(pi._n(), r._P(), r._v()):
        if _cero(n):
            continue
        dentro = _rectas._lineal([(p, ""), (v, "t")])
        t = _t(abs(n))
        if t == "1":
            pieza = "(%s)" % dentro if (" " in dentro or dentro.startswith("-")) and partes else dentro
            if not partes and " " in dentro:
                pieza = "(%s)" % dentro
        else:
            pieza = ("(%s)" % t if "/" in t else t) + "(%s)" % dentro
        if not partes:
            partes.append(("-" if n < 0 else "") + pieza)
        else:
            partes.append((" - " if n < 0 else " + ") + pieza)
    texto = "".join(partes)
    if not _cero(pi.d):
        texto += (" - " if pi.d < 0 else " + ") + _t(abs(pi.d))
    return texto + " = 0"


def _cuenta_corte(r, pi, t):
    simple = _rectas._lineal([(_pe(r._v(), pi._n()), "t"), (pi._valor(r._P()), "")]) + " = 0"
    return "%s  →  %s  →  t = %s" % (_cuenta_sustitucion(r, pi), simple, _t(t))


def interseccion(a, b, c=None, pasos=False):
    """Dónde se cortan: el punto, la recta (si son dos planos) o None si no se cortan.

        pantalla.interseccion(r, pi)            # recta y plano: un punto (1, 1, 1)
        pantalla.interseccion(pi, sigma)        # dos planos: una recta
        pantalla.interseccion(r, s)             # dos rectas: un punto, o None si son paralelas o se cruzan
        pantalla.interseccion(pi, sigma, rho)   # tres planos: un punto (o una recta)
        pantalla.interseccion(r, pi, pasos=True)   # metiendo las paramétricas en el plano

    Si una cosa está dentro de la otra (una recta en un plano), devuelve la de dentro.
    """
    if c is not None:
        planos = [plano(x) if not isinstance(x, Plano) else x for x in (a, b, c)]
        texto, rm, ra = _pos_tres(planos)
        res = None
        if rm == 3:
            M = _filas(planos)
            from .matrices import resolver_sistema
            res = Punto(resolver_sistema([f[:3] for f in M], [f[3] for f in M]))
        elif rm == 2 and ra == 2:
            for i, j in ((0, 1), (0, 2), (1, 2)):
                corte = _corte_planos(planos[i], planos[j])
                if isinstance(corte, Recta3D):
                    res = corte
                    break
        elif rm == 1 and ra == 1:
            res = planos[0]
        if pasos:
            lineas = ["{ " + p.general() for p in planos]
            lineas.append("Los tres planos: " + texto)
            if isinstance(res, Punto):
                lineas.append("Se cortan en " + _tv(res))
            elif isinstance(res, Recta3D):
                lineas.append("Se cortan en la recta " + str(res))
            _sacar(lineas, None, None, "interseccion")
        return res
    ta, a, tb, b = _dos(a, b, "interseccion")
    if ta == "recta2d" and tb == "recta2d":
        return _rectas.interseccion_rectas(a, b, pasos=pasos)
    if ta != "punto" and tb == "punto" or (ta == "plano" and tb == "recta"):
        ta, a, tb, b = tb, b, ta, a
    lineas = []
    if ta == "punto":
        dentro = (_nulo(_resta(a, b)) if tb == "punto" else b.pasa_por(a))
        res = Punto(a) if dentro else None
        if pasos:
            lineas = ["El punto %s %s" % (_tv(a), "está dentro" if dentro else "no está, así que no se cortan")]
    elif ta == "recta" and tb == "plano":
        res, t = _corte_recta_plano(a, b)
        if pasos:
            vn, k = _pe(a._v(), b._n()), b._valor(a._P())
            lineas = ["Meto las paramétricas de la recta (%s) en el plano:" % a.parametricas(),
                      _cuenta_sustitucion(a, b),
                      _rectas._lineal([(vn, "t"), (k, "")]) + " = 0"]
            if t is not None:
                lineas.append("t = " + _t(t))
                lineas.append("Se cortan en %s" % _tv(res))
            elif res is None:
                lineas.append("No hay ningún t que valga: la recta es paralela al plano y no se cortan")
            else:
                lineas.append("Vale cualquier t: la recta está dentro del plano")
    elif ta == "recta" and tb == "recta":
        tipo, _ = _pos_rectas(a, b)
        res = None
        if tipo == "coincidentes":
            res = a
        elif tipo == "se cortan":
            res, t, k = _corte_rectas(a, b)
        if pasos:
            lineas = ["%s + t·%s = %s + s·%s" % (_tv(a.punto), _tv(a.vector), _tv(b.punto), _tv(b.vector))]
            if tipo == "se cortan":
                lineas.append("t = %s,  s = %s" % (_t(t), _t(k)))
                lineas.append("Se cortan en %s" % _tv(res))
            else:
                lineas.append("Las rectas %s: %s" % (tipo, "son la misma" if tipo == "coincidentes" else "no se cortan"))
    else:
        res = _corte_planos(a, b)
        if pasos:
            lineas = ["{ " + a.general(), "{ " + b.general()]
            if isinstance(res, Recta3D):
                lineas.append("n₁ × n₂ = %s × %s = %s" % (_tv(a.normal), _tv(b.normal), _tv(_px(a._n(), b._n()))))
                lineas.append("Un punto que cumple las dos: %s" % _tv(res.punto))
                lineas.append("Se cortan en la recta " + str(res))
            else:
                lineas.append("Los planos son %s" % ("coincidentes" if res is not None else "paralelos: no se cortan"))
    if lineas:
        _sacar(lineas, None, None, "interseccion")
    return res


# --- proyecciones y simétricos ----------------------------------------------

def _pie_en_plano(P, pi):
    n = pi._n()
    t = _dividir(-pi._valor(P), _pe(n, n))
    return _suma(P, _por(t, n)), t


def _pie_en_recta(P, r):
    v = r._v()
    t = _dividir(_pe(_resta(P, r._P()), v), _pe(v, v))
    return _suma(r._P(), _por(t, v))


def proyeccion(a, sobre, pasos=False):
    """La proyección ortogonal (la "sombra" que cae en perpendicular).

        pantalla.proyeccion((1, 2, 3), pi)       # el punto de pi más cerca de (1, 2, 3)
        pantalla.proyeccion((1, 2, 3), r)        # el punto de r más cerca
        pantalla.proyeccion(r, pi)               # la recta que es la sombra de r en pi
        pantalla.proyeccion((2, 3), (1, 0))      # dos vectores: la sombra de u sobre v, (2, 0)
        pantalla.proyeccion(P, pi, pasos=True)

    Con dos vectores hace lo de siempre; con un punto o una recta y un plano (o una recta), da el punto o la recta.
    """
    if not isinstance(sobre, (Plano, Recta3D, str)) and not isinstance(a, (Plano, Recta3D, str)):
        return _vectores.proyeccion(a, sobre)
    ta, a, tb, b = _dos(a, sobre, "proyeccion")
    lineas = []
    if tb == "punto":
        raise TypeError("proyeccion: se proyecta sobre una recta o un plano, no sobre un punto")
    if ta == "plano":
        raise TypeError("proyeccion: un plano no se proyecta. Proyecta un punto o una recta")
    if ta == "punto" and tb == "plano":
        pie, t = _pie_en_plano(a, b)
        res = Punto(pie)
        if pasos:
            r = Recta3D(a, vector=b._n())
            lineas = ["La recta perpendicular al plano que pasa por P: " + str(r),
                      _cuenta_corte(r, b, t),
                      "La proyección es " + _tv(res)]
    elif ta == "punto" and tb == "recta":
        res = Punto(_pie_en_recta(a, b))
        if pasos:
            sigma = Plano(a, normal=b._v())
            _, t = _corte_recta_plano(b, sigma)
            lineas = ["El plano perpendicular a la recta que pasa por P: " + sigma.general(),
                      _cuenta_corte(b, sigma, t),
                      "La proyección es " + _tv(res)]
    elif ta == "recta" and tb == "plano":
        n = b._n()
        if _nulo(_px(a._v(), n)):
            res = Punto(_pie_en_plano(a._P(), b)[0])
            if pasos:
                lineas = ["La recta es perpendicular al plano: su sombra es un punto, " + _tv(res)]
        else:
            sigma = Plano(a, perpendicular=b)
            res = _corte_planos(b, sigma)
            if isinstance(res, Recta3D):
                pie = _pie_en_plano(a._P(), b)[0]
                res = Recta3D(pie, vector=res._v())
            if pasos:
                lineas = ["El plano que contiene a la recta y es perpendicular a π: " + sigma.general(),
                          "Donde corta a π: " + str(res)]
    else:
        raise TypeError("proyeccion: una recta se proyecta sobre un plano, no sobre otra recta")
    if lineas:
        _sacar(lineas, None, None, "proyeccion")
    return res


def simetrico(a, respecto, pasos=False):
    """El simétrico de un punto respecto de un punto, una recta o un plano (como en un espejo).

        pantalla.simetrico((1, 2, 3), (0, 0, 0))     # (-1, -2, -3)
        pantalla.simetrico((1, 2, 3), pi)            # al otro lado del plano, a la misma distancia
        pantalla.simetrico((1, 2, 3), r)
        pantalla.simetrico(r, pi)                    # también rectas y planos: se hace con sus puntos
        pantalla.simetrico(P, pi, pasos=True)        # M es el punto medio: P' = 2M - P
    """
    ta, a, tb, b = _dos(a, respecto, "simetrico")
    if ta == "recta":
        return recta(simetrico(a._P(), b), simetrico(_suma(a._P(), a._v()), b))
    if ta == "plano":
        P = a._P()
        return Plano(simetrico(P, b), simetrico(_suma(P, a._u()), b), simetrico(_suma(P, a._w()), b))
    if tb == "punto":
        M = b
    elif tb == "plano":
        M = _pie_en_plano(a, b)[0]
    elif tb == "recta":
        M = _pie_en_recta(a, b)
    else:
        raise TypeError("simetrico: no sé hacer el simétrico respecto de eso")
    res = Punto(_resta(_por(2, M), a))
    if pasos:
        lineas = []
        if tb != "punto":
            lineas.append("M = la proyección de P %s = %s" % ("en el plano" if tb == "plano" else "en la recta", _tv(M)))
        lineas.append("P' = 2M - P = 2·%s - %s = %s" % (_tv(M), _tv(a), _tv(res)))
        _sacar(lineas, None, None, "simetrico")
    return res


# --- distancias ----------------------------------------------------------------

def _d_punto_plano(P, pi, lineas):
    arriba = pi._valor(P)
    n = pi._n()
    s = _pe(n, n)
    N = _dividir(arriba * arriba, s)
    d = _raiz(N)
    if lineas is not None:
        lineas.append("d = |%s| / √(%s) = %s / %s%s" % (
            _sustituido(pi, P), " + ".join(_p(x) + "²" for x in n), _t(abs(arriba)), _modulo_texto(s),
            _igual_raiz(N, d)))
    return d


def _d_punto_recta(P, r, lineas):
    w = _resta(P, r._P())
    c = _px(w, r._v())
    s1, s2 = _pe(c, c), _pe(r._v(), r._v())
    N = _dividir(s1, s2)
    d = _raiz(N)
    if lineas is not None:
        lineas.append("AP = P - A = %s,  AP × v = %s" % (_tv(w), _tv(c)))
        lineas.append("d = |AP × v| / |v| = %s / %s%s" % (_modulo_texto(s1), _modulo_texto(s2), _igual_raiz(N, d)))
    return d


def _d_cruzan(r, s, lineas):
    w = _resta(s._P(), r._P())
    uv = _px(r._v(), s._v())
    mixto = _pe(w, uv)
    s2 = _pe(uv, uv)
    N = _dividir(mixto * mixto, s2)
    d = _raiz(N)
    if lineas is not None:
        lineas.append("AB = %s,  u × v = %s" % (_tv(w), _tv(uv)))
        lineas.append("d = |[AB, u, v]| / |u × v| = %s / %s%s" % (_t(abs(mixto)), _modulo_texto(s2), _igual_raiz(N, d)))
    return d


def distancia(A, B, pasos=False):
    """La distancia (la más corta) entre dos cosas: puntos, rectas o planos.

        pantalla.distancia((1, 1), (4, 5))              # dos puntos: 5
        pantalla.distancia((1, 2, 3), pi)               # de un punto a un plano
        pantalla.distancia((1, 2, 3), r)                # de un punto a una recta
        pantalla.distancia(r, s)                        # dos rectas (si se cruzan, con el producto mixto)
        pantalla.distancia(r, pi)  /  (pi, sigma)       # 0 si se cortan; si son paralelos, la de verdad
        pantalla.distancia((0, 0, 0), pi, pasos=True)   # con la fórmula y los números puestos

    Sale exacta si se puede (5, 1/3) y si no con decimales.
    """
    ta, a, tb, b = _dos(A, B, "distancia")
    if ta == "punto" and tb == "punto":
        if len(a) != len(b):
            raise ValueError("distancia: el primer punto tiene %d números y el segundo %d" % (len(a), len(b)))
        w = _resta(b, a)
        d = _vectores.modulo(w)
        if pasos:
            s = sum((x * x for x in w), w[0] * 0)
            _sacar(["d(A, B) = |AB| = √(%s) = %s%s" % (" + ".join(_p(x) + "²" for x in w), "√" + _p(s), _igual_raiz(s, _raiz(s)))],
                   None, None, "distancia")
        return d
    if "recta2d" in (ta, tb):
        if ta == "recta2d" and tb == "recta2d":
            if _rectas.posicion_rectas(a, b) == "secantes":
                return 0
            return _rectas.distancia_punto_recta(b.punto, a, pasos=pasos)
        P, r = (a, b) if ta == "punto" else (b, a)
        return _rectas.distancia_punto_recta(P, r, pasos=pasos)
    if ta != "punto" and tb == "punto" or (ta == "plano" and tb == "recta"):
        ta, a, tb, b = tb, b, ta, a
    lineas = [] if pasos else None
    if ta == "punto" and tb == "plano":
        d = _d_punto_plano(a, b, lineas)
    elif ta == "punto" and tb == "recta":
        d = _d_punto_recta(a, b, lineas)
    elif ta == "recta" and tb == "recta":
        tipo, _ = _pos_rectas(a, b)
        if tipo in ("coincidentes", "se cortan"):
            d = 0
            if pasos:
                lineas.append("Las rectas %s, así que la distancia es 0" % ("son la misma" if tipo == "coincidentes" else "se cortan"))
        elif tipo == "paralelas":
            if pasos:
                lineas.append("Son paralelas: es la distancia de un punto de una, %s, a la otra" % _tv(b.punto))
            d = _d_punto_recta(b._P(), a, lineas)
        else:
            if pasos:
                lineas.append("Se cruzan:")
            d = _d_cruzan(a, b, lineas)
    elif ta == "recta" and tb == "plano":
        tipo, _ = _pos_recta_plano(a, b)
        if tipo == "paralela":
            if pasos:
                lineas.append("La recta es paralela al plano: es la distancia de su punto %s al plano" % _tv(a.punto))
            d = _d_punto_plano(a._P(), b, lineas)
        else:
            d = 0
            if pasos:
                lineas.append("La recta %s, así que la distancia es 0" % (
                    "corta al plano" if tipo == "se cortan" else "está dentro del plano"))
    else:
        tipo = _pos_planos(a, b)
        if tipo == "paralelos":
            if pasos:
                lineas.append("Son paralelos: es la distancia de un punto de uno, %s, al otro" % _tv(b.punto))
            d = _d_punto_plano(b._P(), a, lineas)
        else:
            d = 0
            if pasos:
                lineas.append("Los planos %s, así que la distancia es 0" % (
                    "se cortan" if tipo == "se cortan" else "son el mismo"))
    if pasos:
        _sacar(lineas, None, None, "distancia")
    return _bonito(d)


# --- ángulos ---------------------------------------------------------------

def angulo(u, v, radianes=False, pasos=False):
    """El ángulo entre dos vectores, dos rectas, dos planos o una recta y un plano (en grados).

        pantalla.angulo((1, 0), (0, 1))           # dos vectores: 90.0
        pantalla.angulo(r, s)                     # dos rectas: de 0 a 90
        pantalla.angulo(r, pi)                    # una recta y un plano (con el seno)
        pantalla.angulo(pi, sigma)                # dos planos (con sus vectores normales)
        pantalla.angulo(r, pi, pasos=True)

    radianes=True para que salga en radianes.
    """
    cosas = (Plano, Recta3D, _rectas.Recta, str)
    if not isinstance(u, cosas) and not isinstance(v, cosas):
        return _vectores.angulo(u, v, radianes=radianes, pasos=pasos)

    espacio = _es_del_espacio(u) or _es_del_espacio(v)

    def direccion(x):
        if isinstance(x, str):
            x = _leer_con(x, espacio)
        if isinstance(x, _rectas.Recta):
            return _a_3d(x)
        if isinstance(x, (Plano, Recta3D)):
            return x
        if isinstance(x, (list, tuple)) and len(x) == 2:
            x = list(x) + [0]
        return Recta3D((0, 0, 0), vector=x)
    a, b = direccion(u), direccion(v)
    if isinstance(a, Plano) and isinstance(b, Recta3D):
        a, b = b, a
    seno = isinstance(a, Recta3D) and isinstance(b, Plano)
    x = a._v() if isinstance(a, Recta3D) else a._n()
    y = b._v() if isinstance(b, Recta3D) else b._n()
    pe = _pe(x, y)
    sx, sy = _pe(x, x), _pe(y, y)
    valor = max(-1.0, min(1.0, abs(float(pe)) / math.sqrt(float(sx) * float(sy))))
    ang = math.asin(valor) if seno else math.acos(valor)
    V = _dividir(pe * pe, sx * sy)
    if pasos:
        nx, ny = ("v", "n") if seno else ("u", "v") if isinstance(a, Recta3D) else ("n₁", "n₂")
        quien = "sen" if seno else "cos"
        _sacar(["%s α = |%s · %s| / (|%s|·|%s|) = %s / (%s·%s)%s" % (
            quien, nx, ny, nx, ny, _t(abs(pe)), _modulo_texto(sx), _modulo_texto(sy), _igual_raiz(V, _raiz(V))),
                "α ≈ %s°" % ("%.2f" % math.degrees(ang)).rstrip("0").rstrip(".")], None, None, "angulo")
    return _bonito(ang if radianes else math.degrees(ang))


# --- más cosas de clase ----------------------------------------------------

def perpendicular_comun(r, s, pasos=False):
    """La recta que corta a r y a s y es perpendicular a las dos.

        pantalla.perpendicular_comun(r, s)
        pantalla.perpendicular_comun(r, s, pasos=True)    # con los dos puntos donde las toca

    Si r y s son paralelas hay infinitas y devuelve None.
    """
    r, s = recta(r), recta(s)
    u, v, w = r._v(), s._v(), _resta(s._P(), r._P())
    uv = _px(u, v)
    if _nulo(uv):
        if pasos:
            _sacar(["Las rectas son paralelas: hay infinitas perpendiculares comunes"], None, None, "perpendicular_comun")
        return None
    # A + t·u y B + k·v con el vector que los une perpendicular a u y a v
    t, k = _resolver2(_pe(u, u), -_pe(u, v), _pe(w, u), _pe(u, v), -_pe(v, v), _pe(w, v))
    A, B = _suma(r._P(), _por(t, u)), _suma(s._P(), _por(k, v))
    res = Recta3D(A, vector=_enteros(uv))
    if pasos:
        _sacar(["u × v = %s  (la dirección de la perpendicular común)" % _tv(uv),
                "Toca a r en %s (t = %s) y a s en %s (s = %s)" % (_tv(A), _t(t), _tv(B), _t(k)),
                str(res)], None, None, "perpendicular_comun")
    return res


def punto_medio(A, B):
    """El punto que está justo en medio de A y B.

        pantalla.punto_medio((1, 2, 3), (3, 4, 5))     # (2, 3, 4)
    """
    _, a, _, b = _dos(A, B, "punto_medio")
    if not isinstance(a, list) or not isinstance(b, list) or len(a) != len(b):
        raise TypeError("punto_medio: dame dos puntos con los mismos números")
    return Punto([(x + y) / 2 for x, y in zip(a, b)])


def plano_mediador(A, B):
    """El plano de los puntos que están a la misma distancia de A y de B (pasa por el medio y es perpendicular a AB).

        pantalla.plano_mediador((0, 0, 0), (2, 0, 0))     # x - 1 = 0
    """
    a, b = _tres(A, "plano_mediador", "el punto A"), _tres(B, "plano_mediador", "el punto B")
    if _nulo(_resta(b, a)):
        raise ValueError("plano_mediador: los dos puntos son el mismo")
    return Plano(punto_medio(a, b), normal=_resta(b, a))


def _a_3d(r):
    """Una recta del plano metida en el espacio (con z = 0), para hacer las cuentas igual."""
    return Recta3D(list(r.punto) + [0], vector=list(r.vector) + [0])


def _tres_o_dos(P, funcion, que):
    if isinstance(P, (list, tuple)) and len(P) == 2:
        return [_numero(n, funcion, que) for n in P] + [Fraction(0)]
    return _tres(P, funcion, que)


def area_triangulo(A, B, C, pasos=False):
    """El área del triángulo ABC: la mitad del módulo de AB × AC (vale en el plano y en el espacio).

        pantalla.area_triangulo((0, 0, 0), (2, 0, 0), (0, 2, 0))     # 2
        pantalla.area_triangulo(A, B, C, pasos=True)
    """
    a, b, c = (_tres_o_dos(P, "area_triangulo", q) for P, q in ((A, "el punto A"), (B, "el punto B"), (C, "el punto C")))
    u, v = _resta(b, a), _resta(c, a)
    w = _px(u, v)
    s = _pe(w, w)
    N = _dividir(s, 4)
    area = _raiz(N)
    if pasos:
        _sacar(["AB = %s,  AC = %s,  AB × AC = %s" % (_tv(u), _tv(v), _tv(w)),
                "Área = |AB × AC| / 2 = %s / 2%s" % (_modulo_texto(s), _igual_raiz(N, area))], None, None, "area_triangulo")
    return _bonito(area)


def volumen_tetraedro(A, B, C, D, pasos=False):
    """El volumen del tetraedro ABCD: |[AB, AC, AD]| / 6 (el producto mixto entre 6).

        pantalla.volumen_tetraedro((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))     # 1/6
    """
    a, b, c, d = (_tres(P, "volumen_tetraedro", q) for P, q in
                  ((A, "el punto A"), (B, "el punto B"), (C, "el punto C"), (D, "el punto D")))
    u, v, w = _resta(b, a), _resta(c, a), _resta(d, a)
    mixto = _pe(u, _px(v, w))
    vol = _dividir(abs(mixto), 6)
    if pasos:
        _sacar(["AB = %s,  AC = %s,  AD = %s" % (_tv(u), _tv(v), _tv(w)),
                "[AB, AC, AD] = %s" % _t(mixto),
                "Volumen = |[AB, AC, AD]| / 6 = %s / 6 = %s" % (_t(abs(mixto)), _t(vol))], None, None, "volumen_tetraedro")
    return _bonito(vol)


def estan_alineados(*puntos):
    """True si todos los puntos están en la misma recta.

        pantalla.estan_alineados((0, 0, 0), (1, 1, 1), (2, 2, 2))     # True
    """
    if len(puntos) == 1 and isinstance(puntos[0], (list, tuple)) and all(isinstance(p, (list, tuple)) for p in puntos[0]):
        puntos = tuple(puntos[0])
    ps = [_tres_o_dos(p, "estan_alineados", "el punto %d" % (i + 1)) for i, p in enumerate(puntos)]
    if len(ps) < 2:
        raise TypeError("estan_alineados: dame por lo menos dos puntos")
    return rango([_resta(p, ps[0]) for p in ps[1:]]) <= 1


def son_coplanarios(*puntos):
    """True si todos los puntos están en el mismo plano.

        pantalla.son_coplanarios((0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0))     # True
    """
    if len(puntos) == 1 and isinstance(puntos[0], (list, tuple)) and all(isinstance(p, (list, tuple)) for p in puntos[0]):
        puntos = tuple(puntos[0])
    ps = [_tres(p, "son_coplanarios", "el punto %d" % (i + 1)) for i, p in enumerate(puntos)]
    if len(ps) < 3:
        raise TypeError("son_coplanarios: dame por lo menos tres puntos")
    return rango([_resta(p, ps[0]) for p in ps[1:]]) <= 2


def ecuaciones_plano(A, B=None, C=None, normal=None, vectores=None, perpendicular=None, paralelo=None, x=None, y=None):
    """Escribe todas las ecuaciones de un plano: vectorial, paramétricas, general, con el vector normal
    y la segmentaria (x/a + y/b + z/c = 1, si corta a los tres ejes). Devuelve el Plano.

        pantalla.ecuaciones_plano((1, 0, 0), (0, 1, 0), (0, 0, 1))
        pantalla.ecuaciones_plano(pi)                 # o uno que ya tengas
    """
    pi = plano(A, B, C, normal, vectores, perpendicular, paralelo)
    filas = [("Vectorial", pi.vectorial()), ("Paramétricas", pi.parametricas()),
             ("General", pi.general()), ("Normal", "n = %s,  %s" % (_tv(pi.normal), pi.punto_normal()))]
    if not pi.segmentaria().startswith("no "):
        filas.append(("Segmentaria", pi.segmentaria()))
    w = max(len(n) for n, _ in filas)
    _sacar(["%s  %s" % ((n + ":").ljust(w + 1), e) for n, e in filas], x, y, "ecuaciones_plano")
    return pi


def _ecuaciones_recta3d(r, x, y):
    filas = [("Vectorial", r.vectorial()), ("Paramétricas", r.parametricas()), ("Continua", r.continua()),
             ("Implícitas", r.implicitas())]
    w = max(len(n) for n, _ in filas)
    _sacar(["%s  %s" % ((n + ":").ljust(w + 1), e) for n, e in filas], x, y, "ecuaciones_recta")
    return r
