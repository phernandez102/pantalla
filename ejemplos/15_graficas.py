import math

import pantalla


def f(x):
    return x * x - 4


pantalla.limpiar()
print("y = x² - 4")
pantalla.grafica(f, -4, 4, ancho=60, alto=14)
print()

print("y = sin(x) y y = cos(x)")
pantalla.grafica([math.sin, math.cos], -2 * math.pi, 2 * math.pi, ancho=60, alto=10)
print()

notas = {"Ana": 8.5, "Luis": 6, "Marta": 9.75, "Pablo": 4}
pantalla.barras(notas, ancho=50, maximo=10, colores=["cian", "amarillo", "verde", "rojo"])
print()
print("La semana:", pantalla.minigrafica([12, 15, 19, 22, 24, 21, 18]))
pantalla.esperar()
