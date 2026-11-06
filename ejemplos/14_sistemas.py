import pantalla

pantalla.limpiar()
pantalla.cabecera("SISTEMAS DE ECUACIONES")
pantalla.escribir("Escribe la matriz ampliada: los coeficientes y, en la última", 3, 3, color="gris")
pantalla.escribir("columna, los resultados.", 3, 4, color="gris")
pantalla.escribir("Por ejemplo, 2x + y = 5 y x - y = 1 es  [2  1 | 5]  y  [1  -1 | 1]", 3, 6, color="gris")
pantalla.esperar("Pulsa una tecla para empezar", 3, 8, color="amarillo")

pantalla.limpiar()
pantalla.cabecera("SISTEMAS DE ECUACIONES")
ampliada = pantalla.pedir_matriz("Ab", maximo=5)
if ampliada is None:
    raise SystemExit

pantalla.limpiar()
print("Así queda la matriz ampliada:")
pantalla.matriz(ampliada, ampliada=True)
print()
print("El sistema es", pantalla.clasificar_sistema(ampliada))
print()

pantalla.resolver_sistema(ampliada, pasos=True)
pantalla.esperar()
