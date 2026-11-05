"""
Escribir texto en la pantalla: en una posición, centrado, a la derecha o letra a letra.
"""

import sys
import time

from .colores import estilo
from .terminal import CSI, _entero, _fin_de_estilo, _juego, _mover, _posicion, _salida, tamano


def _ir(x, y, funcion):
    if x is None and y is None:
        return ""
    if y is None:
        x = _entero(x, "x", funcion)
        if x < 1:
            raise ValueError("%s: x empieza en 1. Me has dado x=%d" % (funcion, x))
        return "%s%dG" % (CSI, x)
    if x is None:
        x = 1
    x, y = _posicion(x, y, funcion)
    return _mover(x, y)


def _componer(texto, x, y, codigo, funcion):
    lineas = str(texto).split("\n")
    trozos = [_ir(x, y, funcion)]
    for numero, linea in enumerate(lineas):
        if numero > 0:
            if y is not None:
                trozos.append(_ir(x if x is not None else 1, y + numero, funcion))
            else:
                trozos.append("\n")
                if x is not None:
                    trozos.append(_ir(x, None, funcion))
        if codigo and linea:
            trozos.append(codigo + linea + _fin_de_estilo())
        else:
            trozos.append(linea)
    return "".join(trozos)


def escribir(texto="", x=None, y=None, color=None, fondo=None, negrita=False, tenue=False,
             cursiva=False, subrayado=False, parpadeo=False, invertido=False, tachado=False,
             nueva_linea=False):
    """Escribe un texto, si quieres en una posición y con color.

        pantalla.escribir("Hola")                      # donde esté el cursor
        pantalla.escribir("Hola", 10, 5)               # columna 10, fila 5
        pantalla.escribir("Hola", 10, 5, color="rojo", negrita=True)
        pantalla.escribir("Puntos: " + str(puntos), 1, 1, color="amarillo", fondo="azul")

    Si el texto tiene varias líneas (con \\n), cada línea empieza en la misma
    columna x, así que sirve para dibujos hechos con letras.
    A diferencia de print(), no salta de línea al final (usa nueva_linea=True).
    Con x="centro" lo centra de lado a lado (y con y="centro", de arriba abajo).
    """
    if x == "centro" or y == "centro":
        lineas = str(texto).split("\n")
        ancho_p, alto_p = tamano()
        if y == "centro" or y is None:
            y = max(1, (alto_p - len(lineas)) // 2 + 1)
        if x == "centro":
            for numero, linea in enumerate(lineas):
                escribir(linea, max(1, (ancho_p - len(linea)) // 2 + 1), y + numero, color, fondo,
                         negrita, tenue, cursiva, subrayado, parpadeo, invertido, tachado)
            if nueva_linea:
                _salida("\n")
            return
    codigo = estilo(color, fondo, negrita, tenue, cursiva, subrayado, parpadeo, invertido, tachado)
    salida = _componer(texto, x, y, codigo, "escribir")
    if nueva_linea:
        salida = salida + "\n"
    _salida(salida)


def centrar(texto, y=None, color=None, fondo=None, negrita=False, tenue=False, cursiva=False,
            subrayado=False, parpadeo=False, invertido=False, tachado=False):
    """Escribe un texto centrado. Sin y, también lo centra de arriba abajo.

        pantalla.centrar("GAME OVER", color="rojo", negrita=True)
        pantalla.centrar("Pulsa una tecla", y=20)
    """
    lineas = str(texto).split("\n")
    ancho_p, alto_p = tamano()
    if y is None:
        y = max(1, (alto_p - len(lineas)) // 2 + 1)
    for numero, linea in enumerate(lineas):
        x = max(1, (ancho_p - len(linea)) // 2 + 1)
        escribir(linea, x, y + numero, color, fondo, negrita, tenue, cursiva, subrayado,
                 parpadeo, invertido, tachado)


def escribir_derecha(texto, y, margen=0, color=None, fondo=None, negrita=False, tenue=False,
                     cursiva=False, subrayado=False, parpadeo=False, invertido=False,
                     tachado=False):
    """Escribe un texto pegado al borde derecho de la pantalla, en la fila y.

        pantalla.escribir_derecha("Vidas: 3", 1)
    """
    texto = str(texto)
    x = max(1, tamano()[0] - len(texto) - margen + 1)
    escribir(texto, x, y, color, fondo, negrita, tenue, cursiva, subrayado, parpadeo,
             invertido, tachado)


def escribir_lento(texto, x=None, y=None, velocidad=0.04, color=None, fondo=None,
                   negrita=False, tenue=False, cursiva=False, subrayado=False,
                   parpadeo=False, invertido=False, tachado=False):
    """Escribe el texto letra a letra, como en una máquina de escribir.

    velocidad son los segundos entre letra y letra (más pequeño = más rápido).

        pantalla.escribir_lento("Había una vez...", 5, 3, velocidad=0.08)
    """
    codigo = estilo(color, fondo, negrita, tenue, cursiva, subrayado, parpadeo, invertido, tachado)
    _salida(_ir(x, y, "escribir_lento"))
    lineas = str(texto).split("\n")
    for numero, linea in enumerate(lineas):
        if numero > 0:
            if y is not None:
                _salida(_ir(x if x is not None else 1, y + numero, "escribir_lento"))
            else:
                _salida("\n" + (_ir(x, None, "escribir_lento") if x is not None else ""))
        for letra in linea:
            if codigo:
                _salida(codigo + letra + _fin_de_estilo())
            else:
                _salida(letra)
            if _juego["pintar"] is not None:
                _juego["pintar"]()
            sys.stdout.flush()
            time.sleep(velocidad)
