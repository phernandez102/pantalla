"""
Dibujar: cajas, bordes alrededor de la pantalla, líneas, rectángulos y puntos.
"""

from .colores import estilo as _estilo_ansi
from .terminal import _entero, _fin_de_estilo, _mover, _posicion, _salida, tamano

# orden: las 3 de arriba, las 3 del medio, las 3 de abajo, raya horizontal y raya vertical
ESTILOS = {
    "simple": "┌┬┐├┼┤└┴┘─│",
    "doble": "╔╦╗╠╬╣╚╩╝═║",
    "grueso": "┏┳┓┣╋┫┗┻┛━┃",
    "redondo": "╭┬╮├┼┤╰┴╯─│",
    "ascii": "+++++++++-|",
}


def _piezas(estilo, funcion):
    if isinstance(estilo, str):
        if estilo.lower() in ESTILOS:
            return ESTILOS[estilo.lower()]
        if len(estilo) == 1:
            return estilo * 11
    raise ValueError(
        "%s: no conozco el estilo %r. Usa uno de estos: %s, o un solo carácter como '=' o '*'."
        % (funcion, estilo, ", ".join(ESTILOS))
    )


def _poner(x, y, texto, codigo=""):
    ancho_p, alto_p = tamano()
    if y < 1 or y > alto_p or x > ancho_p or not texto:
        return ""
    if x < 1:
        texto = texto[1 - x:]
        x = 1
    texto = texto[: ancho_p - x + 1]
    if not texto:
        return ""
    if codigo:
        return _mover(x, y) + codigo + texto + _fin_de_estilo()
    return _mover(x, y) + texto


def _medida(valor, nombre, funcion, minimo):
    valor = _entero(valor, nombre, funcion)
    if valor < minimo:
        raise ValueError("%s: '%s' tiene que ser al menos %d. Me has dado %d"
                         % (funcion, nombre, minimo, valor))
    return valor


def caja(x=None, y=None, ancho=20, alto=6, estilo="simple", color=None, fondo=None, titulo=None,
         relleno=False):
    """Dibuja una caja (un rectángulo con borde).

    - x, y: la esquina de arriba a la izquierda (sin ellas, la caja sale en el centro).
    - ancho, alto: lo que mide, contando el borde.
    - estilo: "simple", "doble", "grueso", "redondo", "ascii" o un carácter como "*".
    - titulo: un texto que se pone en el borde de arriba.
    - relleno: True para borrar lo que haya dentro (o un carácter para rellenarla con él).

        pantalla.caja(5, 3, 30, 10)
        pantalla.caja(5, 3, 30, 10, estilo="doble", color="cian", titulo="Inventario")
        pantalla.caja(ancho=40, alto=10, titulo="En el centro")
    """
    ancho = _medida(ancho, "ancho", "caja", 2)
    alto = _medida(alto, "alto", "caja", 2)
    ancho_p, alto_p = tamano()
    if x is None:
        x = max(1, (ancho_p - ancho) // 2 + 1)
    if y is None:
        y = max(1, (alto_p - alto) // 2 + 1)
    x, y = _posicion(x, y, "caja")
    p = _piezas(estilo, "caja")
    codigo = _estilo_ansi(color, fondo)
    horizontal = p[9]
    vertical = p[10]

    arriba = p[0] + horizontal * (ancho - 2) + p[2]
    if titulo is not None and ancho >= 6:
        t = " " + str(titulo)[: ancho - 5] + " "
        arriba = p[0] + horizontal + t + horizontal * (ancho - 3 - len(t)) + p[2]
    trozos = [_poner(x, y, arriba, codigo)]

    if relleno is True:
        relleno = " "
    for fila in range(1, alto - 1):
        if relleno:
            dentro = (str(relleno) * (ancho - 2))[: ancho - 2]
            trozos.append(_poner(x, y + fila, vertical + dentro + vertical, codigo))
        else:
            trozos.append(_poner(x, y + fila, vertical, codigo))
            trozos.append(_poner(x + ancho - 1, y + fila, vertical, codigo))
    trozos.append(_poner(x, y + alto - 1, p[6] + horizontal * (ancho - 2) + p[8], codigo))
    _salida("".join(trozos))


def rodear(estilo="doble", color=None, fondo=None, titulo=None):
    """Dibuja un borde alrededor de toda la pantalla.

        pantalla.rodear()                 # borde doble
        pantalla.rodear("=")              # borde hecho con =
        pantalla.rodear("*", color="amarillo", titulo="Mi juego")

    Estilos: "simple", "doble", "grueso", "redondo", "ascii" o cualquier carácter.
    """
    ancho_p, alto_p = tamano()
    caja(1, 1, ancho_p, alto_p, estilo, color, fondo, titulo)


def linea(y, caracter="─", x=1, largo=None, color=None, fondo=None):
    """Dibuja una línea horizontal en la fila y (de lado a lado si no dices el largo).

        pantalla.linea(3)
        pantalla.linea(3, "=", color="azul")
        pantalla.linea(10, "-", x=5, largo=20)
    """
    x, y = _posicion(x, y, "linea")
    if isinstance(caracter, str) and caracter.lower() in ESTILOS:
        caracter = ESTILOS[caracter.lower()][9]
    if largo is None:
        largo = tamano()[0] - x + 1
    largo = _medida(largo, "largo", "linea", 0)
    texto = (str(caracter) * largo)[:largo]
    _salida(_poner(x, y, texto, _estilo_ansi(color, fondo)))


def linea_vertical(x, caracter="│", y=1, largo=None, color=None, fondo=None):
    """Dibuja una línea vertical en la columna x (de arriba abajo si no dices el largo).

        pantalla.linea_vertical(40)
        pantalla.linea_vertical(40, "|", y=3, largo=10, color="gris")
    """
    x, y = _posicion(x, y, "linea_vertical")
    if isinstance(caracter, str) and caracter.lower() in ESTILOS:
        caracter = ESTILOS[caracter.lower()][10]
    if largo is None:
        largo = tamano()[1] - y + 1
    largo = _medida(largo, "largo", "linea_vertical", 0)
    codigo = _estilo_ansi(color, fondo)
    caracter = str(caracter)[:1] or " "
    _salida("".join(_poner(x, y + i, caracter, codigo) for i in range(largo)))


def rellenar(x, y, ancho, alto, caracter=" ", color=None, fondo=None):
    """Rellena un rectángulo con un carácter. Con espacios sirve para borrar una zona.

        pantalla.rellenar(10, 5, 20, 4, fondo="azul")    # un rectángulo azul
        pantalla.rellenar(10, 5, 20, 4)                   # borra esa zona
        pantalla.rellenar(1, 20, 80, 1, "~", color="azul") # agua
    """
    x, y = _posicion(x, y, "rellenar")
    ancho = _medida(ancho, "ancho", "rellenar", 0)
    alto = _medida(alto, "alto", "rellenar", 0)
    codigo = _estilo_ansi(color, fondo)
    fila = (str(caracter) * ancho)[:ancho]
    _salida("".join(_poner(x, y + i, fila, codigo) for i in range(alto)))


def punto(x, y, caracter="█", color=None, fondo=None):
    """Pinta un solo carácter en (x, y). Ideal para juegos.

        pantalla.punto(10, 5)                       # un cuadrado
        pantalla.punto(10, 5, "@", color="amarillo")  # el jugador
        pantalla.punto(10, 5, " ")                  # borrarlo
    """
    x, y = _posicion(x, y, "punto")
    _salida(_poner(x, y, str(caracter)[:1] or " ", _estilo_ansi(color, fondo)))
