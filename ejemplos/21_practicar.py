import pantalla

pantalla.limpiar()
pantalla.cabecera("A PRACTICAR")
pantalla.gotoxy(1, 3)

# sin tema te deja elegir de la lista
aciertos = pantalla.practicar(preguntas=10)

if aciertos == 10:
    pantalla.mensaje("¡Todas bien!", titulo="Perfecto", color_borde="verde")
else:
    pantalla.esperar()
