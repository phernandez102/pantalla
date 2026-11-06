import pantalla

PI = pantalla.plano("x + y + z = 3")
SIGMA = pantalla.plano("x - y = 1")
R = pantalla.recta((0, 0, 0), (1, 1, 1))

COSAS = {
    "Dos planos": {"π": PI, "σ": SIGMA},
    "Plano y recta": {"π": PI, "r": R},
    "Tres planos": {"π": PI, "σ": SIGMA, "z = 2": "z = 2"},
    "Un punto y su simétrico": {"π": PI, "P": (2, 2, 2), "P'": pantalla.simetrico((2, 2, 2), PI)},
}

opcion = "Dos planos"
while True:
    pantalla.limpiar()
    pantalla.cabecera("ESPACIO · arrastra el dibujo para girarlo")
    cosas = COSAS[opcion]
    # el dibujo se queda a la derecha del menú y se gira solo mientras el menú espera
    ancho = min(60, max(30, pantalla.ancho() - 42))
    alto = max(10, pantalla.alto() - 11)
    pantalla.dibujar_espacio(cosas, 41, 3, ancho=ancho, alto=alto, girar=True)

    # los puntos son tuplas, para posicion() solo valen planos y rectas
    nombres = [n for n in cosas if not isinstance(cosas[n], tuple)]
    if len(nombres) >= 2:
        texto = pantalla.posicion(*[cosas[n] for n in nombres])
        pantalla.escribir(", ".join(nombres) + ":", 3, 13, color="cian")
        pantalla.escribir(texto, 3, 14, color="cian", negrita=True)
    else:
        texto = round(pantalla.distancia(cosas["P"], PI), 2)
        pantalla.escribir("P está a %s de π" % texto, 3, 13, color="cian")

    opcion = pantalla.menu(list(COSAS) + ["Salir"], titulo="¿Qué miramos?", x=3, y=3, inicial=opcion)
    if opcion in (None, "Salir"):
        break

pantalla.limpiar()
