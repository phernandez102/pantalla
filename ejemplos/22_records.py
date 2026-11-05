import random

import pantalla

pantalla.limpiar()
pantalla.cabecera("¿CUÁNTO TARDAS?")
pantalla.escribir("Escribe la letra que salga lo más rápido que puedas", 3, 3)
pantalla.cuenta_atras(3, 3, 5)

c = pantalla.cronometro()
for i in range(5):
    letra = random.choice("asdfjklñ")
    while pantalla.pedir("  %s  →  " % letra.upper(), 3, 7 + i).lower() != letra:
        pantalla.escribir("¡Esa no!", 25, 7 + i, color="rojo")
    pantalla.escribir("        ", 25, 7 + i)
tiempo = round(c.parar(), 2)

pantalla.escribir("Has tardado %s" % c, 3, 13, color="cian", negrita=True)
nombre = pantalla.pedir("¿Cómo te llamas? ", 3, 15)

# en los tiempos gana el más pequeño
puesto = pantalla.guardar_record(nombre, tiempo, "tiempos.json", menos_es_mejor=True)
if puesto == 1:
    pantalla.escribir("¡Nuevo récord!", 3, 16, color="amarillo", negrita=True)
elif puesto:
    pantalla.escribir("Has quedado el %d.º" % puesto, 3, 16)

pantalla.tabla_records("tiempos.json", 3, 18)
pantalla.esperar()
pantalla.limpiar()
