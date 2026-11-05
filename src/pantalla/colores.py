"""
Colores y estilos de texto (negrita, subrayado...).

Los colores se escriben en español: "rojo", "azul claro", "naranja"...
También valen colores en hexadecimal ("#ff8800") o en RGB ((255, 136, 0)).
"""

import difflib
import unicodedata

from .terminal import CSI, RESET, _estado, _fin_de_estilo, _salida

_BASICOS = {
    "negro": 30,
    "rojo": 31,
    "verde": 32,
    "amarillo": 33,
    "azul": 34,
    "morado": 35,
    "cian": 36,
    "grisclaro": 37,
    "gris": 90,
    "rojoclaro": 91,
    "verdeclaro": 92,
    "amarilloclaro": 93,
    "azulclaro": 94,
    "moradoclaro": 95,
    "cianclaro": 96,
    "blanco": 97,
}

_RGB = {
    "naranja": (255, 140, 0),
    "marron": (140, 80, 30),
    "rosa": (255, 105, 180),
}

_ALIAS = {
    "magenta": "morado",
    "violeta": "morado",
    "lila": "moradoclaro",
    "celeste": "cianclaro",
    "turquesa": "cian",
    "black": "negro",
    "red": "rojo",
    "green": "verde",
    "yellow": "amarillo",
    "blue": "azul",
    "purple": "morado",
    "cyan": "cian",
    "white": "blanco",
    "gray": "gris",
    "grey": "gris",
    "orange": "naranja",
    "pink": "rosa",
    "brown": "marron",
}

_NOMBRES_BONITOS = [
    "negro", "rojo", "verde", "amarillo", "azul", "morado", "cian", "gris claro",
    "gris", "rojo claro", "verde claro", "amarillo claro", "azul claro",
    "morado claro", "cian claro", "blanco", "naranja", "marrón", "rosa",
]


def _normalizar(nombre):
    nombre = unicodedata.normalize("NFD", nombre.lower())
    nombre = "".join(c for c in nombre if unicodedata.category(c) != "Mn")
    for quitar in (" ", "_", "-"):
        nombre = nombre.replace(quitar, "")
    return nombre


def _error_color(color):
    todos = list(_BASICOS) + list(_RGB) + list(_ALIAS)
    parecidos = difflib.get_close_matches(_normalizar(color), todos, n=1)
    mensaje = "No conozco el color %r." % color
    if parecidos:
        sugerido = _ALIAS.get(parecidos[0], parecidos[0])
        for bonito in _NOMBRES_BONITOS:
            if _normalizar(bonito) == sugerido:
                sugerido = bonito
        mensaje = mensaje + " ¿Querías decir %r?" % sugerido
    mensaje = mensaje + " Colores que puedes usar: " + ", ".join(_NOMBRES_BONITOS)
    mensaje = mensaje + ", o uno en hexadecimal como '#ff8800'."
    return ValueError(mensaje)


def codigo_color(color, fondo=False):
    """Traduce un color a su código ANSI (lo usan las demás funciones por dentro)."""
    rgb = None
    if isinstance(color, str):
        texto = color.strip()
        if texto.startswith("#"):
            cifras = texto[1:]
            if len(cifras) == 3:
                cifras = "".join(c * 2 for c in cifras)
            try:
                if len(cifras) != 6:
                    raise ValueError
                rgb = (int(cifras[0:2], 16), int(cifras[2:4], 16), int(cifras[4:6], 16))
            except ValueError:
                raise ValueError(
                    "El color %r no está bien escrito. En hexadecimal se escribe así: "
                    "'#ff8800' (o corto: '#f80')." % color
                )
        else:
            nombre = _normalizar(texto)
            nombre = _ALIAS.get(nombre, nombre)
            if nombre in _BASICOS:
                numero = _BASICOS[nombre]
                if fondo:
                    numero = numero + 10
                return str(numero)
            if nombre not in _RGB:
                raise _error_color(color)
            rgb = _RGB[nombre]
    elif isinstance(color, (tuple, list)) and len(color) == 3:
        for parte in color:
            if isinstance(parte, bool) or not isinstance(parte, int) or not 0 <= parte <= 255:
                raise ValueError(
                    "Un color RGB son tres números enteros del 0 al 255, por ejemplo "
                    "(255, 136, 0). Me has dado %r" % (color,)
                )
        rgb = tuple(color)
    elif isinstance(color, int) and not isinstance(color, bool):
        if not 0 <= color <= 255:
            raise ValueError("Los colores con número van del 0 al 255. Me has dado %d" % color)
        return ("48;5;%d" if fondo else "38;5;%d") % color
    else:
        raise TypeError(
            "Un color tiene que ser un nombre ('rojo'), un hexadecimal ('#ff8800') "
            "o un RGB ((255, 136, 0)). Me has dado %r" % (color,)
        )
    return "%d;2;%d;%d;%d" % ((48 if fondo else 38,) + rgb)


def estilo(color=None, fondo=None, negrita=False, tenue=False, cursiva=False,
           subrayado=False, parpadeo=False, invertido=False, tachado=False):
    """Devuelve el código ANSI de un estilo (lo usan las demás funciones por dentro)."""
    codigos = []
    if negrita:
        codigos.append("1")
    if tenue:
        codigos.append("2")
    if cursiva:
        codigos.append("3")
    if subrayado:
        codigos.append("4")
    if parpadeo:
        codigos.append("5")
    if invertido:
        codigos.append("7")
    if tachado:
        codigos.append("9")
    if color is not None:
        codigos.append(codigo_color(color))
    if fondo is not None:
        codigos.append(codigo_color(fondo, fondo=True))
    if not codigos:
        return ""
    return CSI + ";".join(codigos) + "m"


def colorear(texto, color=None, fondo=None, negrita=False, tenue=False, cursiva=False,
             subrayado=False, parpadeo=False, invertido=False, tachado=False):
    """Devuelve el texto con color, para usarlo con print().

        print("Esto es", pantalla.colorear("importante", "rojo", negrita=True))
    """
    codigo = estilo(color, fondo, negrita, tenue, cursiva, subrayado, parpadeo, invertido, tachado)
    if not codigo:
        return str(texto)
    return codigo + str(texto) + _fin_de_estilo()


def poner_color(color=None, fondo=None, negrita=False, tenue=False, cursiva=False,
                subrayado=False, parpadeo=False, invertido=False, tachado=False):
    """Cambia el color de todo lo que escribas a partir de ahora (también con print).

        pantalla.poner_color("verde")
        print("Esto sale en verde")
        pantalla.quitar_color()
    """
    codigo = estilo(color, fondo, negrita, tenue, cursiva, subrayado, parpadeo, invertido, tachado)
    _estado["estilo"] = codigo
    _salida(RESET + codigo)


def quitar_color():
    """Vuelve al color normal de la terminal."""
    _estado["estilo"] = ""
    _salida(RESET)


def lista_colores():
    """Devuelve la lista con los nombres de los colores que se pueden usar."""
    return list(_NOMBRES_BONITOS)
