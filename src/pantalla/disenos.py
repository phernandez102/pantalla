"""
Dibujar una pantalla hecha con el constructor web (el diseño se guarda como texto JSON).
"""

import json
import os

from .arte import arte
from .dibujo import caja, linea, linea_vertical, punto, rellenar
from .letras import grande
from .terminal import _entero, tamano
from .texto import escribir

TIPOS = ["rodear", "caja", "texto", "linea", "linea_vertical", "rellenar", "punto", "grande", "hueco",
         "arte"]


def _leer(fuente):
    if isinstance(fuente, dict):
        return fuente
    if not isinstance(fuente, str):
        raise TypeError("diseno: dame el texto que copiaste del constructor o el nombre de un archivo .json")
    texto = fuente.strip()
    if not texto.startswith("{"):
        if not os.path.exists(texto):
            raise FileNotFoundError("diseno: no encuentro el archivo %r. Comprueba que está en la "
                                    "misma carpeta que tu programa." % fuente)
        with open(texto, encoding="utf-8") as archivo:
            texto = archivo.read()
    try:
        return json.loads(texto)
    except ValueError:
        raise ValueError("diseno: ese diseño no está bien copiado. Vuelve a copiarlo entero desde el "
                         "constructor (desde la primera { hasta la última }).")


def diseno(fuente, x=1, y=1, centrado=False):
    """Dibuja una pantalla diseñada con el constructor web de pantalla.

    En el constructor pulsas "Copiar diseño" y lo pegas así:

        zonas = pantalla.diseno('''{"pantalla": 1, "ancho": 80, ...}''')

    También vale el nombre de un archivo .json descargado del constructor:

        zonas = pantalla.diseno("menu.json")

    Devuelve un diccionario con la posición (x, y) de cada cosa a la que le
    pusiste nombre en el constructor. Así puedes escribir encima desde tu programa:

        pantalla.escribir(puntos, *zonas["puntos"])
        x, y = zonas["vidas"]

    Con centrado=True, el diseño se coloca en el centro de tu terminal.
    """
    datos = _leer(fuente)
    if not isinstance(datos, dict) or "elementos" not in datos:
        raise ValueError("diseno: esto no parece un diseño del constructor (le falta 'elementos').")
    ancho_d = _entero(datos.get("ancho", 80), "ancho", "diseno")
    alto_d = _entero(datos.get("alto", 24), "alto", "diseno")
    if centrado:
        ancho_p, alto_p = tamano()
        x = max(1, (ancho_p - ancho_d) // 2 + 1)
        y = max(1, (alto_p - alto_d) // 2 + 1)
    dx = _entero(x, "x", "diseno") - 1
    dy = _entero(y, "y", "diseno") - 1

    zonas = {}
    for numero, e in enumerate(datos["elementos"]):
        tipo = e.get("tipo")
        if tipo not in TIPOS:
            raise ValueError("diseno: el elemento %d es de un tipo que no conozco: %r" % (numero + 1, tipo))
        ex = e.get("x", 1) + dx
        ey = e.get("y", 1) + dy
        color = e.get("color")
        fondo = e.get("fondo")
        if tipo == "rodear":
            caja(1 + dx, 1 + dy, ancho_d, alto_d, e.get("estilo", "doble"), color, fondo, e.get("titulo"))
            ex, ey = 1 + dx, 1 + dy
        elif tipo == "caja":
            caja(ex, ey, e.get("ancho", 10), e.get("alto", 4), e.get("estilo", "simple"), color, fondo,
                 e.get("titulo"), e.get("relleno", False))
        elif tipo == "texto":
            escribir(e.get("texto", ""), ex, ey, color, fondo, negrita=e.get("negrita", False),
                     subrayado=e.get("subrayado", False))
        elif tipo == "linea":
            linea(ey, e.get("caracter", "─"), ex, e.get("largo", 10), color, fondo)
        elif tipo == "linea_vertical":
            linea_vertical(ex, e.get("caracter", "│"), ey, e.get("largo", 5), color, fondo)
        elif tipo == "rellenar":
            rellenar(ex, ey, e.get("ancho", 10), e.get("alto", 3), e.get("caracter", " "), color, fondo)
        elif tipo == "punto":
            punto(ex, ey, e.get("caracter", "█"), color, fondo)
        elif tipo == "grande":
            grande(e.get("texto", ""), ex, ey, color, fondo, e.get("caracter", "█"), e.get("fuente"))
        elif tipo == "arte":
            arte(e.get("lineas", []), ex, ey, color, fondo, e.get("colores"), e.get("fondos"),
                 e.get("transparente", True))
        if e.get("nombre"):
            zonas[str(e["nombre"])] = (ex, ey)
    return zonas
