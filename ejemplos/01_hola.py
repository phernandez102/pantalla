import pantalla

pantalla.limpiar()
pantalla.rodear("=")
pantalla.centrar("¡Hola, mundo!", color="amarillo", negrita=True)

pantalla.gotoxy(3, 2)
print("Esto está en la columna 3, fila 2")

pantalla.escribir("Y esto abajo a la derecha", 50, 20, color="cian")

pantalla.esperar("Pulsa una tecla para salir", 3, pantalla.alto() - 1)
pantalla.limpiar()
