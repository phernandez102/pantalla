"""Lo mínimo para un juego: una pelota que rebota. Esc para salir."""

import pantalla

pelota = pantalla.Sprite("●", 10, 5, color="amarillo")
pelota.dx = 1   # a un Sprite le puedes apuntar lo que quieras: cuánto se mueve de lado...
pelota.dy = 1   # ...y cuánto hacia abajo en cada fotograma


def actualizar():
    ancho, alto = pantalla.tamano()
    pelota.mover(pelota.dx, pelota.dy)
    if pelota.x <= 2 or pelota.x >= ancho - 1:
        pelota.dx = -pelota.dx   # rebota de lado
    if pelota.y <= 2 or pelota.y >= alto - 1:
        pelota.dy = -pelota.dy   # rebota arriba o abajo
    pantalla.rodear("redondo", color="azul", titulo="Pelota · Esc para salir")


pantalla.jugar(actualizar)
