import pantalla

pantalla.limpiar()
pantalla.cabecera("NOTAS DE LA CLASE")

notas = []
pantalla.gotoxy(1, 3)
print("Escribe las notas una a una. Deja la línea vacía para acabar.")
while True:
    r = pantalla.pedir("Nota %d: " % (len(notas) + 1)).replace(",", ".")
    if not r:
        break
    try:
        notas.append(float(r) if "." in r else int(r))
    except ValueError:
        pantalla.escribir("Eso no es un número", color="rojo", nueva_linea=True)

if not notas:
    raise SystemExit

pantalla.limpiar()
pantalla.cabecera("%d notas" % len(notas))
ancho, alto = pantalla.histograma(notas, 2, 3, alto=10)
pantalla.estadisticas(notas, ancho + 6, 3)
pantalla.gotoxy(1, alto + 5)
pantalla.tabla_frecuencias(notas)

pantalla.esperar()
pantalla.limpiar()
