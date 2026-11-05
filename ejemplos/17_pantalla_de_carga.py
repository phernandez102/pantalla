import random

import pantalla


def generar_mapa():
    pantalla.pausa(1.2)     # como si tardara de verdad
    return [[random.choice("..,,~^") for _ in range(50)] for _ in range(12)]


def colocar_enemigos():
    pantalla.pausa(0.8)
    return [(random.randint(1, 50), random.randint(1, 12)) for _ in range(6)]


mapa, enemigos = pantalla.pantalla_de_carga(
    "AVENTURA", fuente="ansi_shadow", color="verde", color_final="cian", marco="redondo",
    tareas=[("Generando el mapa", generar_mapa),
            ("Colocando enemigos", colocar_enemigos),
            "Afinando los sonidos"],
    consejos=["Consejo: los enemigos no cruzan el agua (~)",
              "Consejo: las montañas (^) no se pueden pisar"],
)

pantalla.limpiar()
for y, fila in enumerate(mapa, 1):
    pantalla.escribir("".join(fila), 3, y + 1, color="verde")
for x, y in enemigos:
    pantalla.punto(x + 2, y + 1, "E", color="rojo")
pantalla.escribir("Hay %d enemigos escondidos" % len(enemigos), 3, 15, color="amarillo")
pantalla.esperar(x=3, y=17)
pantalla.limpiar()
