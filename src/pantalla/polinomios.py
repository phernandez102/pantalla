"""
Polinomios: escribirlos como en clase, hacer cuentas con ellos, Ruffini, raíces y la ecuación
de segundo grado, todo con fracciones exactas y paso a paso si quieres.

    p = pantalla.polinomio("2x^3 - 3x + 1")
    print(p * p)                                   # 4x⁶ - 12x⁴ + 4x³ + 9x² - 6x + 1
    print(p(2))                                    # 11
    pantalla.ruffini(p, 1, pasos=True)             # la tabla de Ruffini
    pantalla.ecuacion_segundo_grado(1, -5, 6, pasos=True)
"""

import math
import re
from fractions import Fraction

from .colores import estilo as _estilo_ansi
from .matrices import _texto_numero
from .numeros import _a_numero, _bonito, _sacar
from .terminal import _fin_de_estilo


_ELEVADOS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_NORMALES = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


def _exacto(n, funcion, que="el coeficiente"):
    n = _a_numero(n, funcion, que)
    return n if isinstance(n, float) else Fraction(n)


def _texto(n):
    return _texto_numero(_bonito(n))


def _p(n):
    """El número para una cuenta: los negativos y las fracciones entre paréntesis."""
    t = _texto(n)
    return "(%s)" % t if t.startswith("-") or "/" in t else t


class Polinomio(object):
    """Un polinomio, como 2x³ - 3x + 1. Se suma, resta y multiplica con + - *, y p(2) lo evalúa.

        p = pantalla.Polinomio(2, 0, -3, 1)      # los coeficientes, del grado más alto al más bajo
        q = pantalla.polinomio("x^2 - 1")         # o escrito como en clase
        print(p + q)          # 2x³ + x² - 3x
        print(p(2))           # 11
        print(p.grado)        # 3
        pantalla.grafica(p, -2, 2)                # como es una función, se puede dibujar
    """

    __slots__ = ("_c",)

    def __init__(self, *coeficientes):
        if len(coeficientes) == 1 and isinstance(coeficientes[0], str):
            self._c = _leer_polinomio(coeficientes[0])._c
            return
        if len(coeficientes) == 1 and isinstance(coeficientes[0], Polinomio):
            self._c = list(coeficientes[0]._c)
            return
        if len(coeficientes) == 1 and isinstance(coeficientes[0], (list, tuple)):
            coeficientes = coeficientes[0]
        if not coeficientes:
            raise ValueError("Polinomio: dame por lo menos un coeficiente, por ejemplo Polinomio(1, -2)")
        # por dentro se guardan al revés: _c[k] es el que va con x^k
        c = [_exacto(n, "Polinomio") for n in reversed(list(coeficientes))]
        self._c = _limpiar(c)

    @property
    def grado(self):
        """El grado: la potencia más alta de x (el polinomio 0 tiene grado 0)."""
        return len(self._c) - 1

    @property
    def coeficientes(self):
        """Los coeficientes, del grado más alto al más bajo: [2, 0, -3, 1] para 2x³ - 3x + 1."""
        return [_bonito(n) for n in reversed(self._c)]

    def __call__(self, x):
        if isinstance(x, bool) or not isinstance(x, (int, float, Fraction)):
            x = _a_numero(x, "Polinomio", "x")
        if isinstance(x, float) or any(isinstance(n, float) for n in self._c):
            x = float(x)
        total = 0
        for n in reversed(self._c):
            total = total * x + n
        return _bonito(total)

    def __str__(self):
        return _texto_polinomio(self._c)

    __repr__ = __str__

    def __eq__(self, otro):
        try:
            otro = _como_polinomio(otro, "Polinomio")
        except TypeError:
            return NotImplemented
        return self._c == otro._c

    def __ne__(self, otro):
        r = self.__eq__(otro)
        return r if r is NotImplemented else not r

    __hash__ = None

    def __add__(self, otro):
        try:
            otro = _como_polinomio(otro, "Polinomio")
        except TypeError:
            return NotImplemented
        n = max(len(self._c), len(otro._c))
        a, b = self._c + [0] * (n - len(self._c)), otro._c + [0] * (n - len(otro._c))
        return _nuevo([x + y for x, y in zip(a, b)])

    __radd__ = __add__

    def __neg__(self):
        return _nuevo([-n for n in self._c])

    def __pos__(self):
        return self

    def __sub__(self, otro):
        try:
            otro = _como_polinomio(otro, "Polinomio")
        except TypeError:
            return NotImplemented
        return self + (-otro)

    def __rsub__(self, otro):
        return (-self) + otro

    def __mul__(self, otro):
        try:
            otro = _como_polinomio(otro, "Polinomio")
        except TypeError:
            return NotImplemented
        r = [0] * (len(self._c) + len(otro._c) - 1)
        for i, a in enumerate(self._c):
            for j, b in enumerate(otro._c):
                r[i + j] += a * b
        return _nuevo(r)

    __rmul__ = __mul__

    def __truediv__(self, k):
        if isinstance(k, Polinomio):
            raise TypeError("para dividir dos polinomios usa pantalla.dividir_polinomios(p, q) "
                            "(te da el cociente y el resto) o pantalla.ruffini(p, a)")
        k = _exacto(k, "Polinomio", "el número")
        if k == 0:
            raise ZeroDivisionError("Polinomio: no se puede dividir entre 0")
        return _nuevo([n / k for n in self._c])

    def __pow__(self, n):
        if isinstance(n, bool) or not isinstance(n, int) or n < 0:
            raise ValueError("Polinomio: solo sé elevar a un número entero positivo (p ** 2, p ** 3...)")
        r = Polinomio(1)
        for _ in range(n):
            r = r * self
        return r

    def derivada(self):
        """La derivada: 3x² + 2x da 6x + 2."""
        return _nuevo([n * k for k, n in enumerate(self._c)][1:] or [0])


def _limpiar(c):
    c = list(c)
    while len(c) > 1 and (c[-1] == 0 or (isinstance(c[-1], float) and abs(c[-1]) < 1e-12)):
        c.pop()
    return c


def _nuevo(c):
    p = Polinomio.__new__(Polinomio)
    p._c = _limpiar(c)
    return p


def _como_polinomio(p, funcion):
    if isinstance(p, Polinomio):
        return p
    if isinstance(p, str):
        return _leer_polinomio(p, funcion)
    if isinstance(p, (list, tuple)):
        return Polinomio(p)
    if isinstance(p, (int, float, Fraction)) and not isinstance(p, bool):
        return Polinomio(p)
    raise TypeError("%s: necesito un polinomio, como pantalla.polinomio(\"x^2 - 1\") o la lista "
                    "de coeficientes [1, 0, -1], y me has dado %r" % (funcion, p))


def _texto_polinomio(c):
    partes = []
    for k in range(len(c) - 1, -1, -1):
        n = c[k]
        if n == 0 and len(c) > 1:
            continue
        negativo = n < 0
        t = _texto(abs(n))
        if k > 0:
            if t == "1":
                t = ""
            elif "/" in t:
                t = "(%s)" % t
            t += "x" + (str(k).translate(_ELEVADOS) if k > 1 else "")
        if not partes:
            partes.append(("-" if negativo else "") + t)
        else:
            partes.append((" - " if negativo else " + ") + t)
    return "".join(partes) or "0"


_TERMINO = re.compile(r"^([+-]?)(\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?)?(x(?:\^(\d+))?)?$")


def _leer_polinomio(texto, funcion="polinomio"):
    original = texto
    t = str(texto).replace(" ", "").replace("−", "-").replace(",", ".").replace("**", "^")
    t = t.replace("·", "").replace("*", "").replace("X", "x")
    # x² -> x^2
    t = re.sub(r"x([⁰¹²³⁴⁵⁶⁷⁸⁹]+)", lambda m: "x^" + m.group(1).translate(_NORMALES), t)
    # (1/2)x -> 1/2x
    t = re.sub(r"\(([+-]?\d+(?:\.\d+)?/\d+)\)", r"\1", t)
    if not t:
        raise ValueError("%s: está vacío. Escríbelo así: \"2x^3 - 3x + 1\"" % funcion)
    terminos = re.findall(r"[+-]?[^+-]+", t)
    if "".join(terminos) != t:
        raise ValueError("%s: no entiendo %r. Escríbelo así: \"2x^3 - 3x + 1\"" % (funcion, original))
    c = {}
    for termino in terminos:
        m = _TERMINO.match(termino)
        if not m or (m.group(2) is None and m.group(3) is None):
            raise ValueError("%s: no entiendo el trozo %r de %r. Escríbelo así: \"2x^3 - 3x + 1\" "
                             "(la x elevada con ^)" % (funcion, termino, original))
        signo, numero, equis, potencia = m.groups()
        n = Fraction(numero) if numero else Fraction(1)
        if signo == "-":
            n = -n
        k = (int(potencia) if potencia else 1) if equis else 0
        c[k] = c.get(k, 0) + n
    return _nuevo([c.get(k, Fraction(0)) for k in range(max(c) + 1)])


def polinomio(texto):
    """Hace un polinomio a partir de cómo se escribe en clase.

        p = pantalla.polinomio("2x^3 - 3x + 1")
        p = pantalla.polinomio("2x³ - 3x + 1")          # también con los numeritos de arriba
        p = pantalla.polinomio("x**2 + (1/2)x")         # o como en Python
        p = pantalla.polinomio([2, 0, -3, 1])           # o con los coeficientes

    Devuelve un Polinomio, que se suma, resta y multiplica con + - *.
    """
    return _como_polinomio(texto, "polinomio")


def dividir_polinomios(p, q):
    """Divide p entre q. Devuelve (cociente, resto), los dos polinomios.

        c, r = pantalla.dividir_polinomios("x^3 - 1", "x - 1")
        print(c, r)      # x² + x + 1   0
    """
    p, q = _como_polinomio(p, "dividir_polinomios"), _como_polinomio(q, "dividir_polinomios")
    if q._c == [0]:
        raise ZeroDivisionError("dividir_polinomios: no se puede dividir entre el polinomio 0")
    resto = list(p._c)
    cociente = [0] * max(1, len(p._c) - len(q._c) + 1)
    for k in range(len(p._c) - len(q._c), -1, -1):
        factor = resto[k + len(q._c) - 1] / q._c[-1]
        cociente[k] = factor
        for i, n in enumerate(q._c):
            resto[k + i] -= factor * n
    return _nuevo(cociente), _nuevo(resto[:max(1, len(q._c) - 1)])


def _tabla_ruffini(c, a, productos, resultado):
    """Las líneas de la tabla, con los coeficientes del grado más alto al más bajo."""
    textos = [_texto(n) for n in c + productos + resultado]
    w = max(len(t) for t in textos) + 1
    celdas = lambda ns: " ".join(_texto(n).rjust(w) for n in ns)
    ta = _texto(a)
    k = len(ta) + 1
    amarillo, fin = _estilo_ansi("amarillo", negrita=True), _fin_de_estilo()
    largo = len(celdas(c))
    ultima = celdas(resultado[:-1])
    ultima = (ultima + " " if ultima else "") + amarillo + _texto(resultado[-1]).rjust(w) + fin
    return [" " * k + "│ " + celdas(c),
            ta.rjust(k - 1) + " │ " + " " * (w + 1) + celdas(productos),
            "─" * k + "┼" + "─" * (largo + 1),
            " " * k + "│ " + ultima]


def ruffini(p, a, pasos=False, x=None, y=None):
    """Divide el polinomio p entre (x - a) con la regla de Ruffini. Devuelve (cociente, resto).

        c, r = pantalla.ruffini("2x^3 - 3x + 1", 1)     # 2x² + 2x - 1   y   0
        pantalla.ruffini("2x^3 - 3x + 1", 1, pasos=True)
        #   │  2  0 -3  1
        # 1 │     2  2 -1
        # ──┼────────────
        #   │  2  2 -1  0

    Si el resto da 0, a es una raíz del polinomio (y x - a lo divide).
    Con x e y, la tabla se dibuja en esa posición.
    """
    p = _como_polinomio(p, "ruffini")
    a = _exacto(a, "ruffini", "el número a")
    c = list(reversed(p._c))
    productos, resultado = [], [c[0]]
    for n in c[1:]:
        productos.append(resultado[-1] * a)
        resultado.append(n + productos[-1])
    if pasos or x is not None or y is not None:
        lineas = _tabla_ruffini(c, a, productos, resultado)
        lineas.append("Cociente: %s    Resto: %s" % (_texto_polinomio(list(reversed(resultado[:-1])) or [0]),
                                                    _texto(resultado[-1])))
        _sacar(lineas, x, y, "ruffini")
    return _nuevo(list(reversed(resultado[:-1])) or [0]), _bonito(resultado[-1])


def _divisores(n):
    n = abs(n)
    return [d for d in range(1, n + 1) if n % d == 0] if n else [1]


def _candidatas(c):
    """Las raíces racionales que puede tener: divisores del término independiente entre los del principal."""
    mcm_den = 1
    for n in c:
        mcm_den = mcm_den * n.denominator // math.gcd(mcm_den, n.denominator)
    enteros = [int(n * mcm_den) for n in c]
    vistas = set()
    for arriba in _divisores(enteros[-1]):
        for abajo in _divisores(enteros[0]):
            r = Fraction(arriba, abajo)
            for v in (r, -r):
                if v not in vistas:
                    vistas.add(v)
    return sorted(vistas, key=lambda v: (abs(v), v < 0))


def _raices_racionales(p, pasos=False, funcion="raices"):
    """Saca con Ruffini todas las raíces racionales. Devuelve (raices, lo_que_queda)."""
    if any(isinstance(n, float) for n in p._c):
        return [], p
    raices = []
    # las x = 0 se sacan directamente (sacando x factor común)
    while len(p._c) > 1 and p._c[0] == 0:
        raices.append(Fraction(0))
        if pasos:
            _sacar(["x = 0 es raíz: %s = x·(%s)" % (p, _nuevo(p._c[1:]))], None, None, funcion)
        p = _nuevo(p._c[1:])
    while p.grado >= 1:
        c = list(reversed(p._c))
        for r in _candidatas(c):
            cociente, resto = ruffini(p, r)
            if resto == 0:
                if pasos:
                    _sacar(["x = %s es raíz:" % _texto(r)], None, None, funcion)
                    ruffini(p, r, pasos=True)
                raices.append(r)
                p = cociente
                break
        else:
            break
    return raices, p


def _raices_numericas(p):
    """Las raíces reales de lo que queda, a lo bruto (Durand-Kerner)."""
    c = [float(n) for n in p._c]
    n = len(c) - 1
    if n < 1:
        return []
    principal = c[-1]
    mon = [v / principal for v in c]
    z = [complex(0.4, 0.9) ** k for k in range(n)]
    for _ in range(500):
        cambio = 0
        for i in range(n):
            valor = 0
            for v in reversed(mon):
                valor = valor * z[i] + v
            abajo = 1
            for j in range(n):
                if j != i:
                    abajo *= z[i] - z[j]
            if abajo == 0:
                abajo = 1e-12
            nuevo = z[i] - valor / abajo
            cambio = max(cambio, abs(nuevo - z[i]))
            z[i] = nuevo
        if cambio < 1e-14:
            break
    return sorted(w.real for w in z if abs(w.imag) < 1e-7)


def raices(p, pasos=False):
    """Las raíces reales de un polinomio (los x que lo hacen 0), de la más pequeña a la más grande.

        pantalla.raices("x^2 - 5x + 6")          # [2, 3]
        pantalla.raices("x^3 - x^2")             # [0, 0, 1]: el 0 sale dos veces (es doble)
        pantalla.raices("x^2 - 2")               # [-1.414213562373, 1.414213562373]
        pantalla.raices("2x^3 - 3x + 1", pasos=True)   # enseña cada Ruffini

    Las que son fracciones salen exactas. Las demás, con decimales.
    """
    p = _como_polinomio(p, "raices")
    if p.grado == 0:
        if p._c[0] == 0:
            raise ValueError("raices: el polinomio 0 vale 0 para cualquier x, así que tiene infinitas raíces")
        return []
    exactas, resto = _raices_racionales(p, pasos)
    if resto.grado == 2 and not any(isinstance(n, float) for n in resto._c):
        c, b, a = resto._c
        d = b * b - 4 * a * c
        otras = [] if d < 0 else [(-b - math.sqrt(d)) / (2 * a), (-b + math.sqrt(d)) / (2 * a)]
        if pasos and resto.grado == 2:
            _sacar(["Lo que queda, %s, no tiene más raíces que sean fracciones%s" % (
                resto, ": no tiene raíces reales" if d < 0 else "")], None, None, "raices")
    else:
        otras = _raices_numericas(resto) if resto.grado >= 1 else []
    todas = [_bonito(r) for r in exactas] + [_bonito(float(r)) for r in otras]
    return sorted(todas)


def _factor(r):
    """(x - 2), (x + 1/2), x"""
    if r == 0:
        return "x"
    return "(x %s %s)" % ("-" if r > 0 else "+", _texto(abs(r)))


def factorizar_polinomio(p, pasos=False):
    """Escribe el polinomio como producto de factores, sacando las raíces con Ruffini.

        pantalla.factorizar_polinomio("x^3 - 2x^2 - x + 2")    # "(x - 1)·(x + 1)·(x - 2)"
        pantalla.factorizar_polinomio("2x^2 - 2")              # "2·(x - 1)·(x + 1)"
        pantalla.factorizar_polinomio("x^3 - x", pasos=True)   # con cada Ruffini

    Devuelve el texto. Lo que no se puede partir más con fracciones (como x² + 1) se queda entero.
    """
    p = _como_polinomio(p, "factorizar_polinomio")
    if p.grado == 0:
        return _texto(p._c[0])
    if any(isinstance(n, float) for n in p._c):
        raise TypeError("factorizar_polinomio: solo sé con coeficientes enteros o fracciones, no con decimales")
    exactas, resto = _raices_racionales(p, pasos, "factorizar_polinomio")
    principal = resto._c[-1]
    partes = []
    if principal != 1:
        partes.append(_texto(principal))
    vistas = []
    for r in exactas:
        if r not in vistas:
            vistas.append(r)
    for r in vistas:
        veces = exactas.count(r)
        partes.append(_factor(r) + (str(veces).translate(_ELEVADOS) if veces > 1 else ""))
    if resto.grado >= 1:
        partes.append("(%s)" % _nuevo([n / principal for n in resto._c]))
    texto = "·".join(partes)
    if len(partes) == 1 and texto.startswith("("):
        texto = texto[1:-1]
    if texto.startswith("-1·"):
        texto = "-" + texto[3:]
    if pasos:
        _sacar(["%s = %s" % (p, texto)], None, None, "factorizar_polinomio")
    return texto


def _raiz_exacta(d):
    if isinstance(d, Fraction) and d >= 0:
        n, m = math.isqrt(d.numerator), math.isqrt(d.denominator)
        if n * n == d.numerator and m * m == d.denominator:
            return Fraction(n, m)
    return None


def _texto_raiz(d):
    """√8 -> 2√2, √13 -> √13 (con enteros)."""
    if isinstance(d, Fraction) and d.denominator == 1:
        n, fuera, k = d.numerator, 1, 2
        while k * k <= n:
            while n % (k * k) == 0:
                fuera, n = fuera * k, n // (k * k)
            k += 1
        return ("%d√%d" % (fuera, n)) if fuera > 1 else "√%d" % n
    return "√" + _p(d)


def ecuacion_segundo_grado(a, b, c, pasos=False):
    """Resuelve a·x² + b·x + c = 0. Devuelve la lista de soluciones (0, 1 o 2).

        pantalla.ecuacion_segundo_grado(1, -5, 6)               # [3, 2]
        pantalla.ecuacion_segundo_grado(1, -5, 6, pasos=True)
        # x² - 5x + 6 = 0
        # Δ = b² - 4ac = (-5)² - 4·1·6 = 25 - 24 = 1
        # x = (-b ± √Δ) / 2a = (5 ± 1) / 2
        # x₁ = 3    x₂ = 2

    Si el discriminante (Δ) es negativo no hay soluciones y devuelve []. Si da 0, hay una sola.
    """
    a = _exacto(a, "ecuacion_segundo_grado", "a")
    b = _exacto(b, "ecuacion_segundo_grado", "b")
    c = _exacto(c, "ecuacion_segundo_grado", "c")
    if a == 0:
        raise ValueError("ecuacion_segundo_grado: si a = 0 no es de segundo grado. bx + c = 0 se resuelve "
                         "con x = -c / b")
    d = b * b - 4 * a * c
    exacta = _raiz_exacta(d) if not isinstance(d, float) else None
    if d < 0:
        soluciones = []
    elif exacta is not None:
        soluciones = [(-b + exacta) / (2 * a), (-b - exacta) / (2 * a)]
    else:
        r = math.sqrt(d)
        soluciones = [(-b + r) / (2 * a), (-b - r) / (2 * a)]
    if d == 0:
        soluciones = soluciones[:1]
    soluciones = [_bonito(s) for s in soluciones]
    if pasos:
        lineas = [str(_nuevo([c, b, a])) + " = 0",
                  "Δ = b² - 4ac = %s² - 4·%s·%s = %s %s %s = %s" % (
                      _p(b), _p(a), _p(c), _texto(b * b), "+" if 4 * a * c < 0 else "-",
                      _texto(abs(4 * a * c)), _texto(d))]
        menos_b, dos_a = _texto(-b), _texto(2 * a)
        if d < 0:
            lineas.append("Δ es negativo: no tiene soluciones (no hay ninguna raíz de un número negativo)")
        elif d == 0:
            lineas.append("x = -b / 2a = %s / %s = %s    (Δ = 0: una sola solución, doble)" % (
                menos_b, _p(2 * a), _texto(soluciones[0])))
        else:
            raiz = _texto(exacta) if exacta is not None else _texto_raiz(d)
            lineas.append("x = (-b ± √Δ) / 2a = (%s ± %s) / %s" % (menos_b, raiz, _p(2 * a) if dos_a.startswith("-") else dos_a))
            if exacta is not None:
                lineas.append("x₁ = %s    x₂ = %s" % (_texto(soluciones[0]), _texto(soluciones[1])))
            else:
                lineas.append("x₁ ≈ %s    x₂ ≈ %s" % tuple(("%.4f" % s).rstrip("0").rstrip(".") for s in soluciones))
        _sacar(lineas, None, None, "ecuacion_segundo_grado")
    return soluciones
