import pantalla

pantalla.limpiar()
u = pantalla.pedir_vector("u", dimension=2)
v = pantalla.pedir_vector("v", dimension=2)
if u is None or v is None:
    pantalla.limpiar()
    raise SystemExit

pantalla.limpiar()
pantalla.cabecera(f"u = {u}    v = {v}")
ancho, alto = pantalla.dibujar_vectores({"u": u, "v": v, "u+v": u + v}, 2, 3, ancho=44, alto=15)

# las cuentas, con sus pasos, debajo del dibujo
pantalla.gotoxy(1, alto + 4)
pantalla.producto_escalar(u, v, pasos=True)
pantalla.modulo(u, pasos=True)
pantalla.modulo(v, pasos=True, nombre="v")
if abs(u) and abs(v):
    pantalla.angulo(u, v, pasos=True)
if pantalla.son_perpendiculares(u, v):
    pantalla.escribir("¡Son perpendiculares!", color="verde", nueva_linea=True)
elif pantalla.son_paralelos(u, v):
    pantalla.escribir("Son paralelos: uno es el otro por un número", color="amarillo", nueva_linea=True)

pantalla.esperar()
pantalla.limpiar()
