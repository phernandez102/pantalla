import random

import pantalla

ANCHO = pantalla.ancho()
ALTO = pantalla.alto()


def comida_nueva(serpiente):
    while True:
        sitio = (random.randint(2, ANCHO - 1), random.randint(4, ALTO - 1))
        if sitio not in serpiente:
            return sitio


pantalla.iniciar(titulo="Serpiente")
pantalla.rodear("doble", color="verde")
pantalla.linea(3, "═", x=2, largo=ANCHO - 2, color="verde")
pantalla.punto(1, 3, "╠", color="verde")
pantalla.punto(ANCHO, 3, "╣", color="verde")

serpiente = [(10, 10), (9, 10), (8, 10)]
direccion = "derecha"
comida = comida_nueva(serpiente)
puntos = 0

pantalla.punto(comida[0], comida[1], "●", color="rojo")
for x, y in serpiente:
    pantalla.punto(x, y, "█", color="verde claro")

while True:
    pantalla.escribir(" Puntos: " + str(puntos) + "   (flechas para moverte, q para salir) ", 3, 2, color="amarillo")

    t = pantalla.tecla_pulsada()
    if t == "q":
        break
    if t == "arriba" and direccion != "abajo":
        direccion = "arriba"
    elif t == "abajo" and direccion != "arriba":
        direccion = "abajo"
    elif t == "izquierda" and direccion != "derecha":
        direccion = "izquierda"
    elif t == "derecha" and direccion != "izquierda":
        direccion = "derecha"

    x, y = serpiente[0]
    if direccion == "arriba":
        y = y - 1
    elif direccion == "abajo":
        y = y + 1
    elif direccion == "izquierda":
        x = x - 1
    else:
        x = x + 1

    if x <= 1 or x >= ANCHO or y <= 3 or y >= ALTO or (x, y) in serpiente:
        pantalla.pitido()
        pantalla.mensaje("¡Has chocado!\nPuntos: " + str(puntos), titulo="Fin", color_borde="rojo")
        break

    serpiente.insert(0, (x, y))
    pantalla.punto(x, y, "█", color="verde claro")

    if (x, y) == comida:
        puntos = puntos + 1
        comida = comida_nueva(serpiente)
        pantalla.punto(comida[0], comida[1], "●", color="rojo")
    else:
        cola = serpiente.pop()
        pantalla.punto(cola[0], cola[1], " ")

    if direccion in ("arriba", "abajo"):
        pantalla.pausa(0.12)
    else:
        pantalla.pausa(0.07)

pantalla.terminar()
print("Has hecho", puntos, "puntos")
