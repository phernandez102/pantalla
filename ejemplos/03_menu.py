import pantalla


def saludar():
    nombre = pantalla.pedir("¿Cómo te llamas? ", 5, 5, color="cian")
    pantalla.mensaje("¡Hola, " + nombre + "!", titulo="Saludo")


def sumar():
    a = pantalla.pedir_numero("Primer número: ", 5, 5)
    b = pantalla.pedir_numero("Segundo número: ", 5, 7)
    pantalla.mensaje(str(a) + " + " + str(b) + " = " + str(a + b), titulo="Resultado")


def tabla_de_multiplicar():
    n = pantalla.pedir_numero("¿Qué tabla quieres? ", 5, 3, minimo=1, maximo=10)
    filas = []
    for i in range(1, 11):
        filas.append([str(n) + " x " + str(i), n * i])
    pantalla.tabla(filas, cabeceras=["Operación", "Resultado"], x=5, y=5)
    pantalla.esperar("Pulsa una tecla", 5, 19, color="gris")


while True:
    pantalla.limpiar()
    pantalla.rodear("redondo", color="azul")
    pantalla.grande("MENU", y=2, color="amarillo")
    opcion = pantalla.menu(["Saludar", "Sumar", "Tabla de multiplicar", "Salir"], titulo="Elige", y=9)
    pantalla.limpiar()
    if opcion == "Saludar":
        saludar()
    elif opcion == "Sumar":
        sumar()
    elif opcion == "Tabla de multiplicar":
        tabla_de_multiplicar()
    else:
        break

print("¡Adiós!")
