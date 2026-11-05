import pantalla

pantalla.limpiar()
pantalla.cabecera("POLINOMIOS")

texto = pantalla.pedir("Escribe un polinomio (por ejemplo x^3 - 2x^2 - x + 2): ", 2, 3)
try:
    p = pantalla.polinomio(texto)
except ValueError as e:
    pantalla.mensaje(str(e), titulo="Ups", color_borde="rojo")
    raise SystemExit

pantalla.gotoxy(1, 5)
print("p(x) =", p)
print()
# factorizar_polinomio busca las raíces con Ruffini y enseña cada paso
pantalla.factorizar_polinomio(p, pasos=True)

if p.grado == 2:
    a, b, c = p.coeficientes
    print()
    pantalla.ecuacion_segundo_grado(a, b, c, pasos=True)

pantalla.esperar()
pantalla.limpiar()
pantalla.cabecera("y = %s" % p)
pantalla.grafica(p, -5, 5, 3, 3, color="verde claro")
pantalla.esperar()
pantalla.limpiar()
