import math
import os

import pantalla

pantalla.limpiar()
pantalla.cabecera("IMÁGENES Y MODELOS 3D")

foto = pantalla.pedir("Escribe el nombre de una foto (o pulsa Enter para saltarlo): ", 3, 3)
if foto and os.path.exists(foto):
    pantalla.imagen(foto, 3, 5, ancho=50, alto=16)
    pantalla.esperar(x=3, y=pantalla.alto() - 1)

    # la misma foto, pero en relieve: lo claro sube
    pantalla.ver_modelo(foto, relieve=0.4)
elif foto:
    pantalla.escribir("No encuentro esa foto", 3, 5, color="rojo")
    pantalla.esperar(x=3, y=7)

# un modelo .obj con sus colores (casa.mtl)
pantalla.ver_modelo(os.path.join(os.path.dirname(os.path.abspath(__file__)), "casa.obj"))

# una superficie z = f(x, y): las flechas la giran, + y - acercan, Esc sale
pantalla.ver_modelo(lambda x, y: math.sin(x) * math.cos(y))
pantalla.limpiar()
