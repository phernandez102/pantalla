import pantalla

pantalla.limpiar()
pantalla.cabecera("FRACCIONES")

a = pantalla.pedir_fraccion("Primera fracción: ", 3, 3)
b = pantalla.pedir_fraccion("Segunda fracción: ", 3, 5)

operacion = pantalla.elegir("¿Qué hago?", ["Sumar", "Restar", "Multiplicar", "Dividir"], 3, 7)
if operacion is None:
    raise SystemExit

signo = {"Sumar": "+", "Restar": "-", "Multiplicar": "·", "Dividir": ":"}[operacion]
if operacion == "Dividir" and b == 0:
    pantalla.escribir("No se puede dividir entre 0", 3, 10, color="rojo")
else:
    # escribir_cuenta la dibuja como en el cuaderno y pone el resultado
    pantalla.escribir_cuenta("%s %s %s" % (a, signo, b), 5, 10, color_resultado="verde")

pantalla.pie("Pulsa cualquier tecla para salir")
pantalla.tecla()
pantalla.limpiar()
