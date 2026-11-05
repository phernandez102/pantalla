import pantalla

pantalla.iniciar()
pantalla.rodear("simple", color="gris", titulo="Mueve la @ con las flechas · q para salir")

x = 10
y = 5
while True:
    pantalla.punto(x, y, "@", color="amarillo")
    pantalla.escribir("x=" + str(x) + " y=" + str(y) + "   ", 3, pantalla.alto())

    t = pantalla.tecla()
    pantalla.punto(x, y, " ")

    if t == "arriba" and y > 2:
        y = y - 1
    elif t == "abajo" and y < pantalla.alto() - 1:
        y = y + 1
    elif t == "izquierda" and x > 2:
        x = x - 1
    elif t == "derecha" and x < pantalla.ancho() - 1:
        x = x + 1
    elif t == "q":
        break

pantalla.terminar()
