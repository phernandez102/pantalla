import random

import pantalla

# Esta pantalla está hecha con el constructor web (plantilla "Ficha de jugador").
# Para cambiarla: pega el texto de diseno() en el constructor ("Abrir un diseño que ya tenías").
FICHA = r'''{"pantalla":1,"ancho":80,"alto":24,"elementos":[{"tipo":"caja","x":3,"y":2,"ancho":36,"alto":10,"estilo":"doble","titulo":"Jugador","color":"verde"},{"tipo":"texto","x":5,"y":4,"texto":"Nombre:","negrita":true},{"tipo":"hueco","x":14,"y":4,"ancho":20,"nombre":"nombre"},{"tipo":"texto","x":5,"y":6,"texto":"Vidas:","negrita":true},{"tipo":"hueco","x":14,"y":6,"ancho":10,"nombre":"vidas"},{"tipo":"texto","x":5,"y":8,"texto":"Nivel:","negrita":true},{"tipo":"hueco","x":14,"y":8,"ancho":5,"nombre":"nivel"},{"tipo":"caja","x":42,"y":2,"ancho":36,"alto":10,"estilo":"redondo","titulo":"Inventario","color":"cian"},{"tipo":"texto","x":44,"y":4,"texto":"- espada\n- poción\n- llave\n- mapa"},{"tipo":"rellenar","x":3,"y":13,"ancho":75,"alto":3,"caracter":" ","fondo":"azul"},{"tipo":"texto","x":5,"y":14,"texto":"Puntos:","color":"blanco","fondo":"azul","negrita":true},{"tipo":"hueco","x":14,"y":14,"ancho":10,"nombre":"puntos"},{"tipo":"linea","x":3,"y":17,"largo":75,"caracter":"─","color":"gris"},{"tipo":"texto","x":3,"y":23,"texto":"Pulsa Esc para salir","color":"gris"}]}'''

pantalla.iniciar()
zonas = pantalla.diseno(FICHA)

nombre = "Ana"
vidas = 3
puntos = 0
nivel = 1

# *zonas["nombre"] es lo mismo que escribir la x y la y del hueco "nombre"
pantalla.escribir(nombre, *zonas["nombre"], color="amarillo")
pantalla.escribir("Pulsa Espacio para ganar puntos", 3, 19)

while True:
    pantalla.escribir(("♥ " * vidas).ljust(10), *zonas["vidas"], color="rojo")
    pantalla.escribir(str(nivel).ljust(5), *zonas["nivel"])
    pantalla.escribir(str(puntos).ljust(10), *zonas["puntos"], color="amarillo", fondo="azul", negrita=True)

    t = pantalla.tecla()
    if t == "esc":
        break
    if t == "espacio":
        puntos = puntos + random.randint(1, 10)
        nivel = puntos // 25 + 1

pantalla.terminar()
print("Has terminado con", puntos, "puntos")
