"""
Ejercicios para practicar: te pone cuentas al azar, corrige lo que escribes y te dice la nota.

    pantalla.practicar("tablas")                 # 5 multiplicaciones
    pantalla.practicar("fracciones", 10)         # 10 cuentas con fracciones
    pantalla.practicar("ecuaciones", nivel=2)    # un poco más difíciles
    pantalla.practicar()                         # te deja elegir el tema
"""

import random
from fractions import Fraction

from .numeros import _leer_fraccion
from .texto import escribir


def _f(n):
    n = Fraction(n)
    return str(n.numerator) if n.denominator == 1 else "%d/%d" % (n.numerator, n.denominator)


def _tablas(r, nivel):
    hasta = {1: 9, 2: 12, 3: 25}[nivel]
    a, b = r.randint(2, hasta), r.randint(2, hasta if nivel < 3 else 12)
    return "%d × %d" % (a, b), a * b, "%d × %d = %d" % (a, b, a * b)


def _sumas(r, nivel):
    hasta = {1: 20, 2: 100, 3: 1000}[nivel]
    a, b = r.randint(1, hasta), r.randint(1, hasta)
    if r.random() < 0.5:
        return "%d + %d" % (a, b), a + b, "%d + %d = %d" % (a, b, a + b)
    a, b = max(a, b), min(a, b)
    return "%d - %d" % (a, b), a - b, "%d - %d = %d" % (a, b, a - b)


def _divisiones(r, nivel):
    b = r.randint(2, {1: 9, 2: 12, 3: 25}[nivel])
    q = r.randint(2, {1: 10, 2: 20, 3: 50}[nivel])
    return "%d : %d" % (b * q, b), q, "%d : %d = %d, porque %d × %d = %d" % (b * q, b, q, q, b, b * q)


def _fracciones(r, nivel):
    dens = {1: [2, 3, 4, 5, 6], 2: list(range(2, 10)), 3: list(range(2, 13))}[nivel]
    def una():
        while True:
            d = r.choice(dens)
            f = Fraction(r.randint(1, d + (2 if nivel > 1 else -1)), d)
            if f.denominator > 1:
                return f
    a, b = una(), una()
    ops = "+-" if nivel == 1 else "+-·:"
    op = r.choice(ops)
    fa = "%d/%d" % (a.numerator, a.denominator)
    fb = "%d/%d" % (b.numerator, b.denominator)
    if op in "+-":
        resultado = a + b if op == "+" else a - b
        m = a.denominator * b.denominator // _mcd(a.denominator, b.denominator)
        na, nb = a.numerator * (m // a.denominator), b.numerator * (m // b.denominator)
        pasos = "%s %s %s = %d/%d %s %d/%d = %s" % (fa, op, fb, na, m, op, nb, m, _f(resultado))
    elif op == "·":
        resultado = a * b
        pasos = "%s · %s = %d/%d" % (fa, fb, a.numerator * b.numerator, a.denominator * b.denominator)
    else:
        resultado = a / b
        pasos = "%s : %s = %s · %d/%d = %d/%d" % (fa, fb, fa, b.denominator, b.numerator,
                                                a.numerator * b.denominator, a.denominator * b.numerator)
    if not pasos.endswith(" = " + _f(resultado)) and not pasos.endswith(" " + _f(resultado)):
        pasos += " = %s (simplificando)" % _f(resultado)
    return "%s %s %s" % (fa, op, fb), resultado, pasos


def _mcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _potencias(r, nivel):
    base = r.randint(2, {1: 5, 2: 10, 3: 15}[nivel])
    exp = r.randint(2, 3 if base > 5 else {1: 3, 2: 4, 3: 5}[nivel])
    return "%d^%d" % (base, exp), base ** exp, "%d^%d = %s = %d" % (base, exp, " · ".join([str(base)] * exp),
                                                                     base ** exp)


def _raices(r, nivel):
    n = r.randint(2, {1: 10, 2: 15, 3: 30}[nivel])
    return "√%d" % (n * n), n, "√%d = %d, porque %d · %d = %d" % (n * n, n, n, n, n * n)


def _ecuaciones(r, nivel):
    x = r.randint(-9 if nivel > 1 else 1, 9)
    a = r.choice([k for k in range(-6 if nivel > 1 else 2, 7) if k not in (0, 1)])
    b = r.randint(-15, 15)
    if nivel < 3:
        c = a * x + b
        pregunta = "%s = %d" % (_lineal(a, b), c)
        pasos = "%s → %s = %d → x = %d / %d = %d" % (pregunta, _lineal(a, 0), c - b, c - b, a, x)
        return pregunta + "   →   x =", x, pasos
    d = r.choice([k for k in range(-5, 6) if k != a])
    e = a * x + b - d * x
    pregunta = "%s = %s" % (_lineal(a, b), _lineal(d, e))
    pasos = "%s → %s = %d → x = %d" % (pregunta, _lineal(a - d, 0), e - b, x)
    return pregunta + "   →   x =", x, pasos


def _lineal(a, b):
    t = {1: "x", -1: "-x"}.get(a, "%dx" % a)
    if b:
        t += " %s %d" % ("+" if b > 0 else "-", abs(b))
    return t


def _mcd_tema(r, nivel):
    g = r.randint(2, {1: 6, 2: 12, 3: 20}[nivel])
    a, b = g * r.randint(1, 9), g * r.randint(1, 9)
    while a == b:
        b = g * r.randint(1, 9)
    m = _mcd(a, b)
    return "mcd(%d, %d)" % (a, b), m, "mcd(%d, %d) = %d: es el más grande que divide a los dos" % (a, b, m)


def _primos(r, nivel):
    hasta = {1: 30, 2: 100, 3: 300}[nivel]
    n = r.randint(2, hasta)
    divisor = next((d for d in range(2, int(n ** 0.5) + 1) if n % d == 0), None)
    explicacion = ("%d es primo: solo se puede dividir entre 1 y entre %d" % (n, n) if divisor is None
                   else "%d no es primo: %d = %d × %d" % (n, n, divisor, n // divisor))
    return "¿%d es primo? (sí/no)" % n, divisor is None, explicacion


def _binario(r, nivel):
    n = r.randint(2, {1: 15, 2: 63, 3: 255}[nivel])
    b = bin(n)[2:]
    if nivel > 1 and r.random() < 0.5:
        return "%s en decimal" % b, n, "%s = %s = %d" % (b, " + ".join(
            str(2 ** k) for k, c in enumerate(reversed(b)) if c == "1"), n)
    return "%d en binario" % n, "bin:" + b, "%d = %s en binario (los restos de dividir entre 2, de abajo arriba)" % (n, b)


def _porcentajes(r, nivel):
    p = r.choice({1: [10, 20, 25, 50, 75], 2: [5, 10, 15, 20, 25, 30, 40, 60, 75], 3: list(range(5, 100, 5))}[nivel])
    total = r.choice([k for k in range(20, 1001, 20) if k * p % 100 == 0])
    return "el %d %% de %d" % (p, total), Fraction(total * p, 100), "%d %% de %d = %d · %d / 100 = %s" % (
        p, total, total, p, _f(Fraction(total * p, 100)))


def _vectores(r, nivel):
    hasta = {1: 5, 2: 9, 3: 12}[nivel]
    u = [r.randint(-hasta, hasta) for _ in range(2 if nivel < 3 else 3)]
    v = [r.randint(-hasta, hasta) for _ in range(len(u))]
    pe = sum(a * b for a, b in zip(u, v))
    t = lambda w: "(" + ", ".join(map(str, w)) + ")"
    p = lambda n: "(%d)" % n if n < 0 else str(n)
    return "%s · %s" % (t(u), t(v)), pe, "%s · %s = %s = %d" % (t(u), t(v), " + ".join(
        "%s·%s" % (p(a), p(b)) for a, b in zip(u, v)), pe)


_TEMAS = {
    "tablas": ("Tablas de multiplicar", _tablas),
    "sumas": ("Sumas y restas", _sumas),
    "divisiones": ("Divisiones exactas", _divisiones),
    "fracciones": ("Fracciones", _fracciones),
    "potencias": ("Potencias", _potencias),
    "raices": ("Raíces cuadradas", _raices),
    "ecuaciones": ("Ecuaciones de primer grado", _ecuaciones),
    "mcd": ("Máximo común divisor", _mcd_tema),
    "primos": ("¿Es primo?", _primos),
    "binario": ("Binario", _binario),
    "porcentajes": ("Porcentajes", _porcentajes),
    "vectores": ("Producto escalar", _vectores),
}


def lista_temas():
    """Los temas que hay para practicar().

        print(pantalla.lista_temas())     # ['tablas', 'sumas', 'divisiones', 'fracciones', ...]
    """
    return list(_TEMAS)


def _bien(respuesta, solucion):
    r = respuesta.strip().lower().replace(" ", "")
    if isinstance(solucion, bool):
        if r in ("si", "sí", "s", "yes", "y"):
            return solucion is True
        if r in ("no", "n"):
            return solucion is False
        return None
    if isinstance(solucion, str) and solucion.startswith("bin:"):
        if not r or any(c not in "01" for c in r):
            return None
        return r.lstrip("0") == solucion[4:].lstrip("0")
    try:
        return _leer_fraccion(r) == Fraction(solucion)
    except (ValueError, ZeroDivisionError):
        return None


def _texto_solucion(solucion):
    if isinstance(solucion, bool):
        return "sí" if solucion else "no"
    if isinstance(solucion, str):
        return solucion[4:]
    return _f(solucion)


def practicar(tema=None, preguntas=5, nivel=1, semilla=None):
    """Te pone ejercicios del tema que digas, corrige cada respuesta y al final te da la nota.

        pantalla.practicar("tablas")
        pantalla.practicar("fracciones", 10, nivel=2)
        pantalla.practicar()                          # te pregunta el tema

    Temas: tablas, sumas, divisiones, fracciones, potencias, raices, ecuaciones, mcd, primos,
    binario, porcentajes y vectores (pantalla.lista_temas() te los da).
    - nivel: 1, 2 o 3 (más difícil).
    - semilla: un número para que salgan siempre los mismos ejercicios.
    Escribe "salir" para acabar antes. Devuelve cuántas has acertado.
    """
    from .teclado import pedir

    if tema is None:
        nombres = list(_TEMAS)
        for i, n in enumerate(nombres, 1):
            escribir("%2d. %s" % (i, _TEMAS[n][0]), nueva_linea=True)
        while tema is None:
            r = pedir("¿Qué quieres practicar? (el número): ")
            if r.lower() == "salir":
                return 0
            if r.isdigit() and 1 <= int(r) <= len(nombres):
                tema = nombres[int(r) - 1]
            elif r.lower() in _TEMAS:
                tema = r.lower()
            else:
                escribir("Escribe un número del 1 al %d" % len(nombres), color="rojo", nueva_linea=True)
    clave = str(tema).lower().replace("í", "i")
    if clave not in _TEMAS:
        from difflib import get_close_matches
        parecido = get_close_matches(clave, list(_TEMAS), 1)
        raise ValueError("practicar: no tengo el tema %r.%s Hay: %s" % (
            tema, " ¿Querías decir %r?" % parecido[0] if parecido else "", ", ".join(_TEMAS)))
    if nivel not in (1, 2, 3):
        raise ValueError("practicar: el nivel puede ser 1, 2 o 3, y me has dado %r" % (nivel,))
    titulo, generar = _TEMAS[clave]
    r = random.Random(semilla)
    escribir("── %s · %d preguntas · escribe \"salir\" para acabar ──" % (titulo, preguntas), color="cian",
             negrita=True, nueva_linea=True)
    aciertos = hechas = 0
    for i in range(1, preguntas + 1):
        pregunta, solucion, explicacion = generar(r, nivel)
        if not pregunta.startswith("¿") and not pregunta.endswith("="):
            pregunta += " ="
        while True:
            respuesta = pedir("%d) %s" % (i, pregunta if pregunta.endswith(" ") else pregunta + " "))
            if respuesta.lower() == "salir":
                break
            bien = _bien(respuesta, solucion)
            if bien is None:
                escribir("   Eso no lo entiendo. Escribe solo el resultado (por ejemplo 7, -3 o 5/6)",
                         color="gris", nueva_linea=True)
                continue
            break
        if respuesta.lower() == "salir":
            break
        hechas += 1
        if bien:
            aciertos += 1
            escribir("   ¡Bien! ✓", color="verde claro", nueva_linea=True)
        else:
            escribir("   No, era %s. " % _texto_solucion(solucion), color="rojo claro")
            escribir(explicacion, color="gris", nueva_linea=True)
    if hechas:
        nota = 10 * aciertos / hechas
        estrellas = int(round(aciertos / hechas * 5))
        color = "verde claro" if nota >= 5 else "rojo claro"
        escribir("Has acertado %d de %d  %s  " % (aciertos, hechas, "★" * estrellas + "☆" * (5 - estrellas)),
                 color=color, negrita=True)
        escribir("Nota: %s" % ("%.1f" % nota).rstrip("0").rstrip("."), color="gris", nueva_linea=True)
    return aciertos
