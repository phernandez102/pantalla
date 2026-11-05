import pantalla

pantalla.limpiar()
pantalla.cabecera("INSCRIPCIÓN AL TORNEO")

datos = pantalla.formulario({"Nombre": "texto", "Edad": "numero", "Contraseña": "contraseña"},
                            titulo="Tus datos")
if datos is None:
    raise SystemExit

juegos = pantalla.elegir_varios(["Ajedrez", "Damas", "Parchís", "Mus", "Dominó"],
                                titulo="¿A qué juegas?", minimo=1)
if juegos is None:
    raise SystemExit

pantalla.limpiar()
pantalla.cabecera("INSCRIPCIÓN AL TORNEO")
texto = "%s, %d años\nJuegas a: %s" % (datos["Nombre"], datos["Edad"], ", ".join(juegos))
pantalla.mensaje(texto, titulo="¡Apuntado!", color_borde="verde")
pantalla.limpiar()
