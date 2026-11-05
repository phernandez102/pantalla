"""
Números y fracciones: fracciones que se escriben "1/2", cuentas exactas, MCD y mcm,
números primos y la descomposición en factores primos de toda la vida.

    f = pantalla.fraccion("3/4")
    print(f + pantalla.fraccion(1, 4))          # 1
    print(pantalla.calcular("1/2 + 1/3"))       # 5/6
    pantalla.escribir_cuenta("1/2 + 1/3")       # la dibuja con las fracciones en vertical
    pantalla.descomponer(360)                   # 360 | 2, 180 | 2, ...
"""

import ast
import operator
import re
from fractions import Fraction

from .colores import estilo as _estilo_ansi
from .terminal import _fin_de_estilo, _mover, _posicion, _salida
from .texto import escribir


class Fraccion(Fraction):
    """Una fracción que al hacer print sale como 3/4 (y no como Fraction(3, 4))."""

    __slots__ = ()

    def __repr__(self):
        return str(self)


def _bonito(n):
    """Lo que devuelven las cuentas: 3 en vez de 3/1, 1/2 como Fraccion, y los decimales limpios."""
    if isinstance(n, bool):
        return n
    if isinstance(n, Fraction):
        if n.denominator == 1:
            return int(n.numerator)
        return Fraccion(n)
    if isinstance(n, float):
        if abs(n) < 1e-12:
            return 0.0
        return round(n, 12)
    return n


def _a_numero(valor, funcion, que="el número"):
    """Convierte lo que te den (3, 2.5, '1/2', '2,5') en un número para hacer cuentas."""
    if isinstance(valor, bool):
        raise TypeError("%s: %s tiene que ser un número, pero me has dado %r" % (funcion, que, valor))
    if isinstance(valor, (int, Fraction)):
        return valor
    if isinstance(valor, float):
        if valor != valor or valor in (float("inf"), float("-inf")):
            raise ValueError("%s: %s no puede ser %r" % (funcion, que, valor))
        return valor
    if isinstance(valor, str):
        try:
            return _leer_fraccion(valor)
        except (ValueError, ZeroDivisionError):
            pass
    raise TypeError("%s: %s tiene que ser un número, pero me has dado %r" % (funcion, que, valor))


def _leer_fraccion(texto):
    """'3/4', '-2', '0,5', '1 1/2' (uno y medio) -> Fraction. Da ValueError si no se entiende."""
    texto = str(texto).strip().replace(",", ".").replace("−", "-")
    m = re.match(r"^([+-]?)(\d+)\s+(\d+)\s*/\s*(\d+)$", texto)
    if m:
        signo, entero, num, den = m.groups()
        if int(den) == 0:
            raise ZeroDivisionError("el denominador no puede ser 0")
        n = int(entero) + Fraction(int(num), int(den))
        return -n if signo == "-" else n
    texto = re.sub(r"\s*/\s*", "/", texto)
    if not texto:
        raise ValueError("está vacío")
    return Fraction(texto)


def fraccion(numerador, denominador=None):
    """Hace una fracción, ya simplificada. Con ella las cuentas salen exactas.

        f = pantalla.fraccion(3, 4)          # 3/4
        f = pantalla.fraccion("3/4")         # lo mismo
        f = pantalla.fraccion("1 1/2")       # uno y medio: 3/2
        f = pantalla.fraccion(0.75)          # 3/4
        print(f + pantalla.fraccion(1, 4))   # 1
        print(f.numerator, f.denominator)    # 3 4

    Se puede sumar, restar, multiplicar y dividir con números normales.
    """
    try:
        if denominador is None:
            if isinstance(numerador, float):
                return Fraccion(str(numerador))
            n = _a_numero(numerador, "fraccion")
            return Fraccion(str(n)) if isinstance(n, float) else Fraccion(n)
        a = _a_numero(numerador, "fraccion", "el numerador")
        b = _a_numero(denominador, "fraccion", "el denominador")
        if isinstance(a, float):
            a = Fraction(str(a))
        if isinstance(b, float):
            b = Fraction(str(b))
        if b == 0:
            raise ZeroDivisionError("fraccion: el denominador no puede ser 0")
        return Fraccion(Fraction(a) / Fraction(b))
    except TypeError:
        if isinstance(numerador, str) and denominador is None:
            raise ValueError("fraccion: no entiendo %r. Escríbela así: '3/4', '-2/5' o '1 1/2'" % numerador)
        raise


def pedir_fraccion(pregunta="Escribe una fracción: ", x=None, y=None, color=None):
    """Pide una fracción (vale 3/4, -2, 0,5 o 1 1/2) y no para hasta que le escribas una que valga.

        f = pantalla.pedir_fraccion("Primera fracción: ")
        g = pantalla.pedir_fraccion("Segunda fracción: ")
        print("La suma es", f + g)
    """
    from .teclado import pedir

    error_anterior = ""
    while True:
        texto = pedir(pregunta, x, y, color=color)
        error = None
        try:
            valor = Fraccion(_leer_fraccion(texto))
        except ZeroDivisionError:
            error = "El denominador no puede ser 0. Prueba otra vez."
        except ValueError:
            error = "Eso no es una fracción. Escríbela así: 3/4. Prueba otra vez."
        if y is None:
            if error is None:
                return valor
            escribir(error, color="rojo", nueva_linea=True)
            continue
        columna = x if x is not None else 1
        if error_anterior:
            escribir(" " * len(error_anterior), columna, y + 1)
        if error is None:
            return valor
        escribir(" " * (len(texto) + 2), columna + len(str(pregunta)), y)
        escribir(error, columna, y + 1, color="rojo")
        error_anterior = error


# --- calcular -------------------------------------------------------------

_OPERACIONES = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
}


def _preparar_cuenta(texto):
    t = str(texto).replace("·", "*").replace("×", "*").replace("−", "-").replace("[", "(").replace("]", ")")
    t = re.sub(r"(?<=\d),(?=\d)", ".", t)
    # 3/4 : 1/2 -> (3/4) / (1/2), que una fraccion escrita va junta como en el cuaderno
    t = re.sub(r"(?<![\^*.\d])(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)(?![.\d])", r"(\1/\2)", t)
    t = t.replace("÷", "/").replace(":", "/").replace("^", "**")
    # 2x3 o 2 x 3 tambien es multiplicar
    t = re.sub(r"(?<=[\d)\s])[xX](?=[\s\d(])", "*", t)
    return t


def _evaluar(nodo, texto):
    if isinstance(nodo, ast.Expression):
        return _evaluar(nodo.body, texto)
    if isinstance(nodo, ast.Constant) and isinstance(nodo.value, (int, float)) and not isinstance(nodo.value, bool):
        return Fraction(str(nodo.value)) if isinstance(nodo.value, float) else Fraction(nodo.value)
    if isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, (ast.USub, ast.UAdd)):
        v = _evaluar(nodo.operand, texto)
        return -v if isinstance(nodo.op, ast.USub) else v
    if isinstance(nodo, ast.BinOp):
        a = _evaluar(nodo.left, texto)
        b = _evaluar(nodo.right, texto)
        if isinstance(nodo.op, ast.Pow):
            if not isinstance(b, Fraction) or b.denominator != 1:
                raise ValueError("calcular: en %r el exponente tiene que ser un número entero" % texto)
            if abs(b) > 1000:
                raise ValueError("calcular: el exponente %s es demasiado grande" % b)
            if a == 0 and b < 0:
                raise ZeroDivisionError("calcular: en %r hay una división entre 0" % texto)
            return a ** int(b)
        if type(nodo.op) in _OPERACIONES:
            if isinstance(nodo.op, ast.Div) and b == 0:
                raise ZeroDivisionError("calcular: en %r hay una división entre 0" % texto)
            return _OPERACIONES[type(nodo.op)](a, b)
    raise ValueError("calcular: no entiendo %r. Escribe una cuenta como '1/2 + 3/4' o '(2 + 3) * 4'" % texto)


def calcular(cuenta):
    """Hace una cuenta escrita como texto, con fracciones exactas.

        pantalla.calcular("1/2 + 1/3")          # 5/6
        pantalla.calcular("(2 + 3) * 4")        # 20
        pantalla.calcular("3/4 : 1/2")          # 3/2   (: y ÷ también dividen)
        pantalla.calcular("2^10")               # 1024  (^ es elevar)
        pantalla.calcular("0,5 + 1/4")          # 3/4

    Devuelve un número entero si la cuenta da justa y una fracción si no.
    Solo hace sumas, restas, multiplicaciones, divisiones y potencias.
    """
    texto = str(cuenta)
    try:
        arbol = ast.parse(_preparar_cuenta(texto).strip(), mode="eval")
    except SyntaxError:
        raise ValueError("calcular: no entiendo %r. Escribe una cuenta como '1/2 + 3/4' o '(2 + 3) * 4'" % texto)
    return _bonito(_evaluar(arbol, texto))


# --- escribir_cuenta ------------------------------------------------------

_TROZOS = re.compile(r"\s*(\d+(?:[.,]\d+)?\s*/\s*\d+(?:[.,]\d+)?|\d+(?:[.,]\d+)?|\*\*|[-+*/·×÷:=()^xX\[\]]|[^\s\d]+)")
_BONITOS = {"*": "·", "**": "^", "/": ":", "x": "·", "X": "·", "×": "·", "÷": ":"}


def _piezas_cuenta(texto):
    piezas = []
    pos = 0
    texto = texto.strip()
    while pos < len(texto):
        m = _TROZOS.match(texto, pos)
        if not m or m.end() == pos:
            break
        t = m.group(1)
        pos = m.end()
        if "/" in t and t not in ("/",):
            num, den = [p.strip() for p in t.split("/")]
            piezas.append(("fraccion", num, den))
        elif t in ("+", "-", "=", "·", "*", "**", "/", "÷", ":", "×", "x", "X", "^"):
            piezas.append(("signo", _BONITOS.get(t, t)))
        else:
            piezas.append(("texto", t))
    return piezas


def _piezas_resultado(valor):
    if isinstance(valor, Fraction) and valor.denominator != 1:
        piezas = []
        if valor < 0:
            piezas.append(("texto", "-"))
        piezas.append(("fraccion", str(abs(valor.numerator)), str(valor.denominator)))
        return piezas
    return [("texto", str(valor))]


def escribir_cuenta(cuenta, x=None, y=None, color=None, color_resultado="amarillo", resultado=True):
    """Dibuja una cuenta con las fracciones en vertical, como en el cuaderno, y su resultado.

        pantalla.escribir_cuenta("1/2 + 1/3")              # sale  1   1   5
                                                          #      ─ + ─ = ─
                                                          #      2   3   6
        pantalla.escribir_cuenta("3/4 · 2/5", 10, 4)
        pantalla.escribir_cuenta("1/2 + 1/3", resultado=False)   # sin el = 5/6
        pantalla.escribir_cuenta(pantalla.fraccion(7, 8))        # una fracción sola

    Si la cuenta ya tiene un =, no la resuelve: la dibuja tal cual.
    Sin x ni y, se escribe donde esté el cursor (como un print). Devuelve (ancho, alto).
    """
    texto = str(cuenta)
    piezas = _piezas_cuenta(texto)
    if not piezas:
        raise ValueError("escribir_cuenta: no hay ninguna cuenta que escribir")
    final = []
    if resultado and not any(p == ("signo", "=") for p in piezas) and len(piezas) > 1:
        valor = calcular(texto)
        final = [("signo", "=")] + _piezas_resultado(Fraction(valor) if not isinstance(valor, float) else valor)
    alto = 3 if any(p[0] == "fraccion" for p in piezas + final) else 1
    medio = alto // 2
    codigo = _estilo_ansi(color)
    codigo_res = _estilo_ansi(color_resultado, negrita=True)
    # cada pieza es un bloque de 'alto' filas; luego se pegan una detras de otra
    bloques = []
    for i, p in enumerate(piezas + final):
        cod = codigo_res if i > len(piezas) else codigo
        if p[0] == "fraccion":
            w = max(len(p[1]), len(p[2]))
            filas = [p[1].center(w), "─" * w, p[2].center(w)]
        else:
            t = p[1]
            if p[0] == "signo" and not (i == 0 and t == "-"):
                t = " %s " % t
            filas = [" " * len(t)] * alto
            filas[medio] = t
        bloques.append((filas, cod))

    fin = _fin_de_estilo()
    lineas = []
    for k in range(alto):
        linea = "".join(cod + f[k] + fin if cod and f[k].strip() else f[k] for f, cod in bloques)
        lineas.append(linea.rstrip())
    ancho = sum(len(f[0]) for f, _ in bloques)
    _sacar(lineas, x, y, "escribir_cuenta")
    return ancho, alto


def _sacar(lineas, x, y, funcion):
    """Escribe varias líneas: donde esté el cursor (como un print) o a partir de (x, y)."""
    if x is None and y is None:
        _salida("\n".join(lineas) + "\n")
        return
    if x is None:
        x = 1
    if y is None:
        raise TypeError("%s: si me das x también necesito y" % funcion)
    x, y = _posicion(x, y, funcion)
    _salida("".join(_mover(x, y + k) + l for k, l in enumerate(lineas)))


# --- enteros: mcd, mcm, primos --------------------------------------------

def _entero_de(valor, funcion):
    if isinstance(valor, bool) or not isinstance(valor, (int, float, Fraction)):
        raise TypeError("%s: necesito números enteros, pero me has dado %r" % (funcion, valor))
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    if isinstance(valor, Fraction) and valor.denominator == 1:
        valor = int(valor)
    if not isinstance(valor, int):
        raise TypeError("%s: necesito números enteros (sin decimales), pero me has dado %s" % (funcion, valor))
    return valor


def _numeros(numeros, funcion):
    if len(numeros) == 1 and isinstance(numeros[0], (list, tuple, set)):
        numeros = list(numeros[0])
    if not numeros:
        raise TypeError("%s: dame al menos un número, por ejemplo %s(12, 18)" % (funcion, funcion))
    return [_entero_de(n, funcion) for n in numeros]


def mcd(*numeros):
    """El máximo común divisor: el número más grande que divide a todos.

        pantalla.mcd(12, 18)          # 6
        pantalla.mcd(12, 18, 30)      # 6
        pantalla.mcd([8, 20])         # 4
    """
    resultado = 0
    for n in _numeros(numeros, "mcd"):
        a, b = abs(resultado), abs(n)
        while b:
            a, b = b, a % b
        resultado = a
    return resultado


def mcm(*numeros):
    """El mínimo común múltiplo: el número más pequeño que es múltiplo de todos.

        pantalla.mcm(4, 6)            # 12
        pantalla.mcm(2, 3, 4)         # 12
    """
    resultado = 1
    for n in _numeros(numeros, "mcm"):
        if n == 0:
            return 0
        resultado = abs(resultado * n) // mcd(resultado, n)
    return resultado


def es_primo(n):
    """True si el número es primo (solo se puede dividir entre 1 y entre sí mismo).

        pantalla.es_primo(7)          # True
        pantalla.es_primo(9)          # False
    """
    n = _entero_de(n, "es_primo")
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def divisores(n):
    """Todos los divisores de un número, de menor a mayor.

        pantalla.divisores(12)        # [1, 2, 3, 4, 6, 12]
    """
    n = _entero_de(n, "divisores")
    if n == 0:
        raise ValueError("divisores: el 0 se puede dividir entre todos los números, no tiene una lista")
    n = abs(n)
    pequenos, grandes = [], []
    d = 1
    while d * d <= n:
        if n % d == 0:
            pequenos.append(d)
            if d != n // d:
                grandes.append(n // d)
        d += 1
    return pequenos + grandes[::-1]


def factorizar(n):
    """Descompone un número en factores primos. Devuelve {primo: cuántas veces}.

        pantalla.factorizar(360)      # {2: 3, 3: 2, 5: 1}   porque 360 = 2³ · 3² · 5

    Para verlo dibujado con la rayita, usa pantalla.descomponer(360).
    """
    return dict(_factores(_entero_de(n, "factorizar"), "factorizar"))


def _factores(n, funcion):
    if n < 2:
        raise ValueError("%s: necesito un número entero mayor que 1, y me has dado %d" % (funcion, n))
    factores = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            if factores and factores[-1][0] == d:
                factores[-1][1] += 1
            else:
                factores.append([d, 1])
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        if factores and factores[-1][0] == n:
            factores[-1][1] += 1
        else:
            factores.append([n, 1])
    return [(p, e) for p, e in factores]


_ELEVADOS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def _potencias(factores):
    return " · ".join(str(p) + (str(e).translate(_ELEVADOS) if e > 1 else "") for p, e in factores)


def descomponer(n, x=None, y=None, color=None, color_primos="amarillo"):
    """Dibuja la descomposición en factores primos con la rayita, como en clase.

        pantalla.descomponer(360)       #  360 │ 2
                                        #  180 │ 2
                                        #   90 │ 2
                                        #   45 │ 3
                                        #   15 │ 3
                                        #    5 │ 5
                                        #    1 │
                                        #  360 = 2³ · 3² · 5

    Devuelve lo mismo que factorizar(): {2: 3, 3: 2, 5: 1}.
    Sin x ni y, se escribe donde esté el cursor (como un print).
    """
    n = _entero_de(n, "descomponer")
    factores = _factores(n, "descomponer")
    divisiones = []
    resto = n
    for p, e in factores:
        for _ in range(e):
            divisiones.append((resto, p))
            resto //= p
    divisiones.append((1, None))
    ancho_n = len(str(n))
    codigo = _estilo_ansi(color)
    codigo_p = _estilo_ansi(color_primos, negrita=True)
    fin = _fin_de_estilo()

    def pintar(texto, cod):
        return cod + texto + fin if cod else texto

    lineas = []
    for numero, primo in divisiones:
        linea = pintar(str(numero).rjust(ancho_n + 1) + " │", codigo)
        if primo is not None:
            linea += " " + pintar(str(primo), codigo_p)
        lineas.append(linea)
    lineas.append(pintar(" %d = " % n, codigo) + pintar(_potencias(factores), codigo_p))
    _sacar(lineas, x, y, "descomponer")
    return dict(factores)
