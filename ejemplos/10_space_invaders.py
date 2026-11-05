"""
Space Invaders hecho con pantalla.jugar(): no hay ningún while.
Escribes qué pasa en cada momento (la función actualizar) y pantalla hace el resto.

    ← →  moverte        espacio  disparar        Esc  salir
"""

import random

import pantalla

ANCHO, ALTO = 60, 22

nave = pantalla.Sprite("/^\\", ANCHO // 2, ALTO - 1, color="verde")
# estrellas de fondo: con capa negativa quedan detrás de todo lo demás
for _ in range(25):
    pantalla.Sprite("·", random.randint(1, ANCHO), random.randint(2, ALTO - 1), color="gris", capa=-1)
marcianos = []
for fila, color in enumerate(["rojo", "amarillo", "cian", "morado"]):
    for columna in range(8):
        marcianos.append(pantalla.Sprite(fotogramas=["/oo\\", "\\oo/"], cada=8, color=color,
                                         x=6 + columna * 6, y=3 + fila * 2))
balas = []         # las nuestras
balas_malas = []   # las de los marcianos
direccion = 1      # 1 = hacia la derecha, -1 = hacia la izquierda
puntos = 0
vidas = 3
fin = None         # cuando acabe: "¡GANASTE!" o "GAME OVER"


def actualizar(tecla):
    global direccion, puntos, vidas, fin

    if fin:
        pantalla.grande(fin, y=6, color="verde" if vidas else "rojo")
        pantalla.centrar("Puntos: %d   ·   pulsa Enter" % puntos, y=14)
        if tecla == "enter":
            return puntos
        return

    # la nave: se mueve mientras mantienes la flecha y dispara con espacio
    if pantalla.pulsada("izquierda") and nave.x > 1:
        nave.mover(-1, 0)
    if pantalla.pulsada("derecha") and nave.x < ANCHO - 2:
        nave.mover(1, 0)
    if tecla == "espacio" and len(balas) < 3:
        balas.append(pantalla.Sprite("|", nave.x + 1, nave.y - 1, color="amarillo"))

    # los marcianos van de lado a lado y bajan una fila al llegar al borde
    if pantalla.cada(0.4):
        if any(m.x + direccion < 1 or m.x + 3 + direccion > ANCHO for m in marcianos):
            direccion = -direccion
            for m in marcianos:
                m.mover(0, 1)
        else:
            for m in marcianos:
                m.mover(direccion, 0)
    if pantalla.cada(0.7) and marcianos:
        quien = random.choice(marcianos)
        balas_malas.append(pantalla.Sprite("¦", quien.x + 1, quien.y + 1, color="rojo"))

    for bala in balas[:]:
        bala.mover(0, -1)
        tocado = bala.choca(marcianos)
        if tocado:
            tocado.eliminar()
            marcianos.remove(tocado)
            puntos += 10
        if tocado or bala.fuera():
            bala.eliminar()
            balas.remove(bala)

    for bala in balas_malas[:]:
        bala.mover(0, 0.5)
        if bala.choca(nave):
            vidas -= 1
            bala.eliminar()
            balas_malas.remove(bala)
        elif bala.fuera():
            bala.eliminar()
            balas_malas.remove(bala)

    if not marcianos:
        fin = "¡GANASTE!"
    elif vidas == 0 or any(m.y >= nave.y - 1 for m in marcianos):
        fin = "GAME OVER"
        vidas = 0
    if fin:
        for s in pantalla.sprites():
            s.eliminar()

    # lo que no son sprites se dibuja en cada fotograma
    pantalla.escribir("Puntos: %d" % puntos, 2, 1, color="amarillo", negrita=True)
    pantalla.escribir_derecha("Vidas: " + "♥ " * vidas, 1, color="rojo")
    pantalla.linea(ALTO, "─", color="verde")


resultado = pantalla.jugar(actualizar, ancho=ANCHO, alto=ALTO)
print("Has hecho %d puntos. ¡Gracias por jugar!" % (resultado or puntos))
