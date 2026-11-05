"""
Letras grandes para títulos y carteles.

La fuente "bloques" mide 5 filas de alto; el dibujo de cada letra está aquí
abajo con #. Las demás fuentes son ficheros FIGlet (.flf) de la carpeta "fuentes".
"""

import unicodedata

from . import _figlet

from .colores import estilo as _estilo_ansi
from .terminal import _fin_de_estilo, _mover, _posicion, _salida, tamano

FUENTE = {
    "A": [" ## ", "#  #", "####", "#  #", "#  #"],
    "B": ["### ", "#  #", "### ", "#  #", "### "],
    "C": [" ###", "#   ", "#   ", "#   ", " ###"],
    "D": ["### ", "#  #", "#  #", "#  #", "### "],
    "E": ["####", "#   ", "### ", "#   ", "####"],
    "F": ["####", "#   ", "### ", "#   ", "#   "],
    "G": [" ###", "#   ", "# ##", "#  #", " ###"],
    "H": ["#  #", "#  #", "####", "#  #", "#  #"],
    "I": ["###", " # ", " # ", " # ", "###"],
    "J": ["  ##", "   #", "   #", "#  #", " ## "],
    "K": ["#  #", "# # ", "##  ", "# # ", "#  #"],
    "L": ["#   ", "#   ", "#   ", "#   ", "####"],
    "M": ["#   #", "## ##", "# # #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #"],
    "Ñ": [" ### ", "#   #", "##  #", "# # #", "#  ##"],
    "O": [" ## ", "#  #", "#  #", "#  #", " ## "],
    "P": ["### ", "#  #", "### ", "#   ", "#   "],
    "Q": [" ## ", "#  #", "#  #", "# ##", " ###"],
    "R": ["### ", "#  #", "### ", "# # ", "#  #"],
    "S": [" ###", "#   ", " ## ", "   #", "### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#  #", "#  #", "#  #", "#  #", " ## "],
    "V": ["#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "# # #", "## ##", "#   #"],
    "X": ["#   #", " # # ", "  #  ", " # # ", "#   #"],
    "Y": ["#   #", " # # ", "  #  ", "  #  ", "  #  "],
    "Z": ["####", "   #", "  # ", " #  ", "####"],
    "0": [" ## ", "# ##", "#  #", "## #", " ## "],
    "1": [" # ", "## ", " # ", " # ", "###"],
    "2": ["### ", "   #", " ## ", "#   ", "####"],
    "3": ["### ", "   #", " ## ", "   #", "### "],
    "4": ["#  #", "#  #", "####", "   #", "   #"],
    "5": ["####", "#   ", "### ", "   #", "### "],
    "6": [" ## ", "#   ", "### ", "#  #", " ## "],
    "7": ["####", "   #", "  # ", " #  ", " #  "],
    "8": [" ## ", "#  #", " ## ", "#  #", " ## "],
    "9": [" ## ", "#  #", " ###", "   #", " ## "],
    " ": ["  ", "  ", "  ", "  ", "  "],
    "!": ["#", "#", "#", " ", "#"],
    "¡": ["#", " ", "#", "#", "#"],
    "?": ["### ", "   #", " ## ", "    ", " #  "],
    "¿": ["  # ", "    ", " ## ", "#   ", " ###"],
    ".": [" ", " ", " ", " ", "#"],
    ",": ["  ", "  ", "  ", " #", "# "],
    ":": [" ", "#", " ", "#", " "],
    "-": ["   ", "   ", "###", "   ", "   "],
    "+": ["   ", " # ", "###", " # ", "   "],
    "=": ["   ", "###", "   ", "###", "   "],
    "(": [" #", "# ", "# ", "# ", " #"],
    ")": ["# ", " #", " #", " #", "# "],
    "/": ["   #", "  # ", " #  ", "#   ", "    "],
    "*": ["     ", " # # ", "  #  ", " # # ", "     "],
    "<": ["  #", " # ", "#  ", " # ", "  #"],
    ">": ["#  ", " # ", "  #", " # ", "#  "],
    "_": ["    ", "    ", "    ", "    ", "####"],
    "'": ["#", "#", " ", " ", " "],
    "#": [" # # ", "#####", " # # ", "#####", " # # "],
}


def _letra(c):
    c = c.upper()
    if c in FUENTE:
        return FUENTE[c]
    sin_tilde = unicodedata.normalize("NFD", c)[0]
    return FUENTE.get(sin_tilde, FUENTE["?"])


def lista_fuentes():
    """Devuelve los nombres de las fuentes que puedes usar en grande() y texto_grande().

        print(pantalla.lista_fuentes())
        pantalla.grande("HOLA", fuente="slant")

    "bloques" es la de siempre (5 filas de █). Las demás son fuentes FIGlet,
    las mismas que usan las webs de "texto a ASCII art".
    """
    return ["bloques"] + _figlet.nombres()


def _cargar_fuente(fuente, funcion):
    if fuente is None or _figlet.normalizar_nombre(fuente) == "bloques":
        return None
    cargada = _figlet.cargar(fuente)
    if cargada is None:
        raise ValueError("%s: no conozco la fuente %r. Fuentes que puedes usar: %s"
                         % (funcion, fuente, ", ".join(lista_fuentes())))
    return cargada


def texto_grande(texto, caracter="█", fuente=None):
    """Devuelve el texto en letras grandes, para usarlo con print().

        print(pantalla.texto_grande("HOLA"))
        print(pantalla.texto_grande("FIN", caracter="#"))
        print(pantalla.texto_grande("Hola", fuente="slant"))

    Sin fuente usa "bloques" (5 filas de alto, hechas con el carácter que digas).
    Con fuente usa una fuente ASCII art; mira cuáles hay con lista_fuentes().
    """
    cargada = _cargar_fuente(fuente, "texto_grande")
    if cargada is not None:
        return "\n".join(_figlet.dibujar(texto, cargada))
    filas = ["", "", "", "", ""]
    for posicion, c in enumerate(str(texto)):
        dibujo = _letra(c)
        for i in range(5):
            if posicion > 0:
                filas[i] = filas[i] + " "
            filas[i] = filas[i] + dibujo[i].replace("#", caracter)
    return "\n".join(f.rstrip() for f in filas)


def grande(texto, x=None, y=None, color=None, fondo=None, caracter="█", fuente=None):
    """Escribe un texto con letras grandes. Sin x lo centra; sin y, también de arriba abajo.

        pantalla.grande("HOLA")
        pantalla.grande("GAME OVER", y=3, color="rojo")
        pantalla.grande("123", 5, 2, caracter="#")
        pantalla.grande("Hola", fuente="ansi_shadow", color="cian")

    Con fuente= eliges una fuente ASCII art (mira cuáles hay con lista_fuentes()).
    """
    lineas = texto_grande(texto, caracter, fuente).split("\n")
    ancho_texto = max(len(l) for l in lineas)
    ancho_p, alto_p = tamano()
    if x is None:
        x = max(1, (ancho_p - ancho_texto) // 2 + 1)
    if y is None:
        y = max(1, (alto_p - len(lineas)) // 2 + 1)
    x, y = _posicion(x, y, "grande")
    codigo = _estilo_ansi(color, fondo)
    trozos = []
    for i, linea in enumerate(lineas):
        if y + i > alto_p:
            break
        linea = linea[: max(0, ancho_p - x + 1)]
        if codigo:
            trozos.append(_mover(x, y + i) + codigo + linea + _fin_de_estilo())
        else:
            trozos.append(_mover(x, y + i) + linea)
    _salida("".join(trozos))
