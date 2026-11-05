"""
Demo del ratón: botones, zonas que se iluminan y un lienzo para pintar.

Ejecútalo en una terminal de verdad (cmd, PowerShell, Windows Terminal, la de VS Code
o la de Linux/Mac). En Windows puedes hacer doble clic en probar_raton.bat.
"""

import pantalla


def titulo(texto):
    pantalla.limpiar()
    pantalla.rodear("redondo", color="azul", titulo="Demo del ratón")
    pantalla.centrar(texto, 3, color="amarillo", negrita=True)


def elegir_color():
    titulo("pantalla.botones(): haz clic en uno (o flechas + Enter)")
    color = pantalla.botones(["Rojo", "Verde", "Azul", "Volver"], y=8)
    if color is None or color == "Volver":
        return
    pantalla.centrar("Has elegido: " + color, 11, color=color.lower(), negrita=True)
    pantalla.centrar("Pulsa una tecla para volver", 13, color="gris")
    pantalla.tecla()


def contador():
    titulo("pantalla.boton() + pantalla.bucle(): botones con contador")
    cuenta = [0]

    def ensenar():
        pantalla.centrar("     Clics: %d     " % cuenta[0], 6, color="cian", negrita=True)

    def sumar():
        cuenta[0] = cuenta[0] + 1
        ensenar()

    def restar():
        cuenta[0] = cuenta[0] - 1
        ensenar()

    def reiniciar():
        cuenta[0] = 0
        ensenar()

    ensenar()
    x = pantalla.ancho() // 2 - 18
    botones = [
        pantalla.boton("+1", x, 9, fondo="verde", al_clic=sumar),
        pantalla.boton("-1", x + 7, 9, fondo="rojo", al_clic=restar),
        pantalla.boton("Reiniciar", x + 14, 9, al_clic=reiniciar),
        pantalla.boton("Volver", x + 28, 9, fondo="gris", al_clic=lambda: "volver"),
    ]
    pantalla.centrar("Pasa el ratón por encima: se iluminan. Esc también vuelve.", 12, color="gris")
    pantalla.bucle(botones)


def tarjetas():
    titulo("pantalla.zona(): tarjetas que se iluminan al pasar el ratón")
    nombres = ["Fuego", "Agua", "Planta"]
    colores = ["rojo", "azul", "verde"]
    zonas = []
    x0 = pantalla.ancho() // 2 - 24

    def dibujar(i, encendida):
        x = x0 + i * 17
        estilo = "doble" if encendida else "simple"
        color = colores[i] if encendida else "gris"
        pantalla.caja(x, 6, 15, 5, estilo=estilo, color=color, titulo=nombres[i])
        pantalla.escribir(" ¡elígeme! " if encendida else "           ", x + 2, 8, color=colores[i], negrita=True)

    def elegida(i):
        pantalla.centrar("   Has elegido %s   " % nombres[i], 13, color=colores[i], negrita=True)

    for i in range(3):
        dibujar(i, False)
        zonas.append(pantalla.zona(x0 + i * 17, 6, 15, 5,
                                   al_hover=lambda i=i: dibujar(i, True),
                                   al_salir=lambda i=i: dibujar(i, False),
                                   al_clic=lambda i=i: elegida(i)))
    pantalla.centrar("Pasa el ratón por las tarjetas y haz clic. Esc para volver.", 16, color="gris")
    pantalla.bucle(zonas)


def puntos_de_la_linea(x1, y1, x2, y2):
    # Algoritmo de Bresenham: todas las casillas entre dos puntos, para que al mover
    # el ratón deprisa la raya salga seguida y sin huecos.
    puntos = []
    dx, dy = abs(x2 - x1), -abs(y2 - y1)
    paso_x = 1 if x1 < x2 else -1
    paso_y = 1 if y1 < y2 else -1
    error = dx + dy
    while True:
        puntos.append((x1, y1))
        if (x1, y1) == (x2, y2):
            return puntos
        doble = 2 * error
        if doble >= dy:
            error += dy
            x1 += paso_x
        if doble <= dx:
            error += dx
            y1 += paso_y


def pintar():
    titulo("leer_raton(arrastrar=True): arrastra para pintar, botón derecho borra")
    colores = ["rojo", "amarillo", "verde", "cian", "azul", "morado", "blanco"]
    elegido = [0]
    ancho, alto = pantalla.tamano()
    arriba, abajo = 5, alto - 3  # filas donde se puede pintar

    def paleta():
        pantalla.escribir(" Color: ", 3, alto - 1)
        for i, color in enumerate(colores):
            marca = "[██]" if i == elegido[0] else " ██ "
            pantalla.escribir(marca, 11 + i * 4, alto - 1, color=color)
        pantalla.escribir("  ·  B borra todo  ·  Esc vuelve ", 11 + len(colores) * 4, alto - 1, color="gris")

    paleta()
    pantalla.activar_raton()
    pantalla.ocultar_cursor()
    anterior = None  # último punto pintado, para unirlo con el siguiente
    while True:
        clic = pantalla.leer_raton(arrastrar=True)
        while clic:
            x, y, boton = clic
            if y == alto - 1 and not clic.arrastrando:
                i = (x - 11) // 4
                if 0 <= i < len(colores):
                    elegido[0] = i
                    paleta()
                anterior = None
            elif 2 <= x < ancho and arriba <= y <= abajo:
                letra = " " if boton == "derecho" else "█"
                desde = anterior if clic.arrastrando and anterior else (x, y)
                for px, py in puntos_de_la_linea(desde[0], desde[1], x, y):
                    pantalla.punto(px, py, letra, color=colores[elegido[0]])
                anterior = (x, y)
            else:
                anterior = None
            clic = pantalla.leer_raton(arrastrar=True)
        t = pantalla.tecla_pulsada()
        if t == "esc":
            break
        if t in ("b", "B"):
            for fila in range(arriba, abajo + 1):
                pantalla.escribir(" " * (ancho - 2), 2, fila)
        pantalla.pausa(0.01)
    pantalla.desactivar_raton()
    pantalla.mostrar_cursor()


OPCIONES = ["Elegir un color", "Botones con contador", "Tarjetas que se iluminan",
            "Pintar con el ratón", "Salir"]

pantalla.iniciar(titulo="Demo del ratón")
try:
    while True:
        titulo("¿Qué quieres probar? Haz clic (o flechas + Enter, o el número)")
        opcion = pantalla.botones(OPCIONES, horizontal=False, y=6)
        if opcion == "Elegir un color":
            elegir_color()
        elif opcion == "Botones con contador":
            contador()
        elif opcion == "Tarjetas que se iluminan":
            tarjetas()
        elif opcion == "Pintar con el ratón":
            pintar()
        else:
            break
finally:
    pantalla.terminar()

print("¡Adiós!")
