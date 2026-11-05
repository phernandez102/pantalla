"""
Spinners: la ruedecita que gira mientras el programa trabaja (como la librería halo).
"""

import time

import pantalla

pantalla.limpiar()
pantalla.escribir("1) Con with: gira mientras se hace lo de dentro\n", 1, 1, color="cian", negrita=True)

with pantalla.spinner("Descargando el mapa..."):
    time.sleep(1.5)

with pantalla.spinner("Cargando enemigos...", estilo="arco", color="amarillo"):
    time.sleep(1.5)

try:
    with pantalla.spinner("Conectando con el servidor...", estilo="pelota", color="morado"):
        time.sleep(1.5)
        raise ConnectionError("no hay internet")
except ConnectionError:
    pass  # el spinner ya ha puesto ✖ y el error llega aquí igual

print()
pantalla.escribir("2) A mano: cambiando el texto mientras gira\n", color="cian", negrita=True)
s = pantalla.spinner("Paso 1 de 3", estilo="tiburon", color="azul").empezar()
for paso in (2, 3):
    time.sleep(1)
    s.texto = "Paso %d de 3" % paso
time.sleep(1)
s.bien("Los 3 pasos, hechos")
s = pantalla.spinner("Guardando la partida", estilo="estrella").empezar()
time.sleep(1)
s.dejar("★", "¡Nuevo récord!", color="amarillo")  # cualquier símbolo al acabar

print()
pantalla.esperar("Pulsa una tecla para ver todos los estilos (Esc para salir)...", color="gris")

# 3) Todos los estilos a la vez, con jugar() (que se encarga del bucle)
nombres = pantalla.lista_spinners()


def actualizar():
    ancho, alto = pantalla.tamano()
    pantalla.cabecera("pantalla.lista_spinners() · Esc para salir")
    columnas = max(1, ancho // 34)
    for i, nombre in enumerate(nombres):
        x = 2 + (i % columnas) * 34
        y = 3 + i // columnas
        if y >= alto:
            break
        milis, fotogramas = pantalla.spinners.SPINNERS[nombre]
        fotograma = fotogramas[int(pantalla.fotograma() * 50 / milis) % len(fotogramas)]
        pantalla.escribir(fotograma[:12], x, y, color="amarillo")
        pantalla.escribir(nombre, x + 13, y, color="gris")


pantalla.jugar(actualizar, velocidad=20)
