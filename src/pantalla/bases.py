"""
Cambios de base: de decimal a binario (o a la base que quieras) y al revés, paso a paso.

    print(pantalla.a_binario(45))                  # 101101
    pantalla.a_binario(45, pasos=True)             # las divisiones entre 2 y los restos
    print(pantalla.a_decimal("101101"))            # 45
    pantalla.a_decimal("2F", 16, pasos=True)       # 2·16¹ + 15·16⁰ = 32 + 15 = 47
"""

from .colores import estilo as _estilo_ansi
from .numeros import _entero_de, _sacar
from .terminal import _fin_de_estilo


_CIFRAS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_ELEVADOS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_DEBAJO = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
_PREFIJOS = {"0b": 2, "0o": 8, "0x": 16}


def _base(base, funcion):
    base = _entero_de(base, funcion)
    if not 2 <= base <= 36:
        raise ValueError("%s: la base tiene que ir de 2 a 36, y me has dado %d" % (funcion, base))
    return base


def cambiar_base(n, base, pasos=False, x=None, y=None):
    """Pasa un número de decimal a otra base (de 2 a 36). Devuelve el texto con las cifras.

        pantalla.cambiar_base(45, 2)                  # "101101"
        pantalla.cambiar_base(255, 16)                # "FF"
        pantalla.cambiar_base(45, 2, pasos=True)
        # 45 : 2 = 22   resto 1
        # 22 : 2 = 11   resto 0
        # ...
        # 45 = 101101₂   (los restos, de abajo arriba)

    En bases mayores que 10 las cifras siguen con letras: A = 10, B = 11... Con x e y,
    los pasos se dibujan en esa posición.
    """
    n = _entero_de(n, "cambiar_base")
    base = _base(base, "cambiar_base")
    negativo, m = n < 0, abs(n)
    divisiones = []
    while True:
        divisiones.append((m, m // base, m % base))
        m //= base
        if m == 0:
            break
    texto = ("-" if negativo else "") + "".join(_CIFRAS[r] for _, _, r in reversed(divisiones))
    if pasos or x is not None or y is not None:
        a, b = len(str(divisiones[0][0])), len(str(divisiones[0][1]))
        amarillo, fin = _estilo_ansi("amarillo", negrita=True), _fin_de_estilo()
        lineas = []
        for d, c, r in divisiones:
            cifra = " (%s)" % _CIFRAS[r] if r >= 10 else ""
            lineas.append("%s : %d = %s   resto %s%d%s%s" % (str(d).rjust(a), base, str(c).rjust(b),
                                                           amarillo, r, fin, cifra))
        lineas.append("%d = %s%s%s%s   (los restos, de abajo arriba)" % (
            n, amarillo, texto, fin, str(base).translate(_DEBAJO)))
        _sacar(lineas, x, y, "cambiar_base")
    return texto


def a_binario(n, pasos=False, x=None, y=None):
    """Pasa un número a binario (base 2). Devuelve el texto con los ceros y unos.

        pantalla.a_binario(45)                # "101101"
        pantalla.a_binario(45, pasos=True)    # con las divisiones entre 2
    """
    return cambiar_base(n, 2, pasos, x, y)


def a_hexadecimal(n, pasos=False, x=None, y=None):
    """Pasa un número a hexadecimal (base 16, con las cifras 0-9 y A-F).

        pantalla.a_hexadecimal(255)           # "FF"
    """
    return cambiar_base(n, 16, pasos, x, y)


def a_decimal(texto, base=2, pasos=False, x=None, y=None):
    """Pasa un número escrito en otra base a decimal. Devuelve el número.

        pantalla.a_decimal("101101")                 # 45 (en binario si no dices la base)
        pantalla.a_decimal("FF", 16)                 # 255
        pantalla.a_decimal("0x2F")                   # 47 (con 0b, 0o o 0x ya sabe la base)
        pantalla.a_decimal("101101", pasos=True)
        # 101101₂ = 1·2⁵ + 0·2⁴ + 1·2³ + 1·2² + 0·2¹ + 1·2⁰ = 32 + 8 + 4 + 1 = 45
    """
    if isinstance(texto, int) and not isinstance(texto, bool):
        texto = str(texto)
    if not isinstance(texto, str):
        raise TypeError("a_decimal: dame el número como texto, por ejemplo a_decimal(\"101101\")")
    t = texto.strip().replace(" ", "").replace("_", "").upper()
    negativo = t.startswith("-")
    t = t.lstrip("+-")
    if t[:2].lower() in _PREFIJOS:
        base = _PREFIJOS[t[:2].lower()]
        t = t[2:]
    base = _base(base, "a_decimal")
    if not t:
        raise ValueError("a_decimal: está vacío")
    for c in t:
        if c not in _CIFRAS[:base]:
            if c in _CIFRAS:
                raise ValueError("a_decimal: en base %d no existe la cifra %s (solo valen %s)" % (
                    base, c, _CIFRAS[0] + "-" + _CIFRAS[base - 1]))
            raise ValueError("a_decimal: %r no es una cifra" % c)
    valores = [_CIFRAS.index(c) for c in t]
    total = 0
    for v in valores:
        total = total * base + v
    if negativo:
        total = -total
    if pasos or x is not None or y is not None:
        k = len(valores) - 1
        sumandos = ["%d·%d%s" % (v, base, str(k - i).translate(_ELEVADOS)) for i, v in enumerate(valores)]
        valores_ = [str(v * base ** (k - i)) for i, v in enumerate(valores) if v]
        linea = "%s%s = %s" % (t, str(base).translate(_DEBAJO), " + ".join(sumandos))
        if len(valores_) > 1:
            linea += " = " + " + ".join(valores_)
        linea += " = %s%d%s" % (_estilo_ansi("amarillo", negrita=True), abs(total), _fin_de_estilo())
        lineas = [linea]
        if negativo:
            lineas.append("y con el signo: %d" % total)
        _sacar(lineas, x, y, "a_decimal")
    return total
