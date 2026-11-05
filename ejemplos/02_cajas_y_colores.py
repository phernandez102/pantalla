import pantalla

pantalla.limpiar()

pantalla.caja(2, 2, 30, 8, estilo="doble", color="verde", titulo="Jugador")
pantalla.escribir("Nombre: Ana", 4, 4)
pantalla.escribir("Vidas:  ", 4, 5)
pantalla.escribir("♥ ♥ ♥", 12, 5, color="rojo")
pantalla.escribir("Nivel:  7", 4, 6)

pantalla.caja(35, 2, 30, 8, estilo="redondo", color="cian", titulo="Inventario")
cosas = ["espada", "poción", "llave", "mapa"]
for i in range(len(cosas)):
    pantalla.escribir("- " + cosas[i], 37, 4 + i)

pantalla.rellenar(2, 11, 63, 3, fondo="azul")
pantalla.escribir("Un rectángulo azul con texto encima", 15, 12, color="blanco", fondo="azul", negrita=True)

print()
print()
print("También se puede usar con print:", pantalla.colorear("en rojo", "rojo"), "y", pantalla.colorear("en verde", "verde"))

pantalla.esperar()
