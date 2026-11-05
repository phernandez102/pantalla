"""
Demostración de todo lo que hace pantalla. Se abre con:  python -m pantalla
Míralo también por dentro: cada parte es un ejemplo de cómo se usa.
"""

import pantalla


def portada():
    pantalla.limpiar()
    pantalla.rodear("doble", color="cian", titulo="pantalla " + pantalla.__version__)
    pantalla.grande("PANTALLA", y=2, color="amarillo")
    pantalla.centrar("Dibuja en la terminal de forma fácil", y=8, color="blanco", negrita=True)


def demo_colores():
    pantalla.limpiar()
    pantalla.rodear("simple", color="gris", titulo="Colores")
    y = 3
    for nombre in pantalla.lista_colores():
        pantalla.escribir(nombre.ljust(16), 4, y)
        pantalla.escribir("  texto  ", 21, y, color=nombre)
        pantalla.escribir("  fondo  ", 32, y, color="negro", fondo=nombre)
        y = y + 1
    pantalla.escribir("negrita", 46, 3, negrita=True)
    pantalla.escribir("tenue", 46, 4, tenue=True)
    pantalla.escribir("cursiva", 46, 5, cursiva=True)
    pantalla.escribir("subrayado", 46, 6, subrayado=True)
    pantalla.escribir("tachado", 46, 7, tachado=True)
    pantalla.escribir("invertido", 46, 8, invertido=True)
    pantalla.escribir("#ff8800 en hexadecimal", 46, 10, color="#ff8800")
    pantalla.escribir("(0, 200, 120) en RGB", 46, 11, color=(0, 200, 120))
    pantalla.esperar("Pulsa una tecla para volver", 4, pantalla.alto() - 1, color="gris")


def demo_cajas():
    pantalla.limpiar()
    x = 3
    for estilo in ["simple", "doble", "grueso", "redondo", "ascii", "*"]:
        pantalla.caja(x, 2, 12, 5, estilo=estilo, titulo=estilo)
        x = x + 13
    pantalla.caja(3, 8, 30, 7, estilo="redondo", color="verde", titulo="Con color")
    pantalla.escribir("Las cajas pueden tener\ntítulo, color y relleno.", 5, 10)
    pantalla.rellenar(36, 8, 20, 7, fondo="azul")
    pantalla.escribir("rellenar()", 41, 11, color="blanco", fondo="azul", negrita=True)
    pantalla.linea(16, "=", color="amarillo")
    pantalla.linea(17, "doble", x=3, largo=40, color="morado")
    for i in range(10):
        pantalla.punto(60 + i * 2, 9 + i % 4, "●", color="rojo claro")
    pantalla.esperar("Pulsa una tecla para volver", 3, pantalla.alto() - 1, color="gris")


def demo_teclas():
    pantalla.limpiar()
    pantalla.rodear("redondo", color="gris", titulo="Teclado")
    pantalla.escribir("Pulsa teclas y te digo cuál es. Esc para salir.", 4, 3, color="amarillo")
    y = 5
    while True:
        t = pantalla.tecla()
        if y > pantalla.alto() - 2:
            pantalla.rellenar(3, 5, pantalla.ancho() - 4, pantalla.alto() - 6)
            y = 5
        pantalla.escribir("pantalla.tecla() devolvió: ", 4, y)
        pantalla.escribir(repr(t), 31, y, color="verde", negrita=True)
        y = y + 1
        if t == "esc":
            return


def demo_mover():
    pantalla.limpiar()
    pantalla.rodear("simple", color="azul", titulo="Mueve la @ con las flechas · Esc salir")
    x, y = pantalla.centro()
    pantalla.ocultar_cursor()
    while True:
        pantalla.punto(x, y, "@", color="amarillo")
        t = pantalla.tecla()
        pantalla.punto(x, y, " ")
        if t == "arriba" and y > 2:
            y = y - 1
        elif t == "abajo" and y < pantalla.alto() - 1:
            y = y + 1
        elif t == "izquierda" and x > 2:
            x = x - 1
        elif t == "derecha" and x < pantalla.ancho() - 1:
            x = x + 1
        elif t == "esc":
            pantalla.mostrar_cursor()
            return


def demo_cosas():
    pantalla.limpiar()
    pantalla.escribir("tabla():", 3, 2, color="amarillo")
    pantalla.tabla([["Ana", 8.5], ["Luis", 6], ["Marta", 9.75]], ["Nombre", "Nota"], x=3, y=3)
    pantalla.escribir("barra_progreso():", 3, 11, color="amarillo")
    pantalla.ocultar_cursor()
    for i in range(101):
        pantalla.barra_progreso(i, 100, 3, 12, ancho=40)
        pantalla.pausa(0.015)
    pantalla.escribir("cargando():", 3, 14, color="amarillo")
    pantalla.cargando(2, "Pensando", 3, 15)
    pantalla.escribir_lento("escribir_lento(): como una máquina de escribir...", 3, 17, velocidad=0.03)
    pantalla.mostrar_cursor()
    pantalla.mensaje("Y esto es mensaje().\nSirve para avisos.", titulo="¡Hola!")


def demo_pedir():
    pantalla.limpiar()
    pantalla.rodear("redondo", color="verde", titulo="Pedir datos")
    nombre = pantalla.pedir("¿Cómo te llamas? ", 4, 3, color="cian")
    edad = pantalla.pedir_numero("¿Cuántos años tienes? ", 4, 5, minimo=0, maximo=120, color="cian")
    pantalla.escribir("¿Te gusta Python? (s/n) ", 4, 8, color="cian")
    gusta = pantalla.confirmar("", 28, 8)
    texto = "Hola, %s. Tienes %d años" % (nombre or "persona misteriosa", edad)
    if gusta:
        texto = texto + "\ny te gusta Python. ¡Bien!"
    else:
        texto = texto + "\ny no te gusta Python... todavía."
    pantalla.mensaje(texto, titulo="Resultado", color_borde="verde")


def demo_menus():
    pantalla.limpiar()
    pantalla.cabecera("Menús")
    pantalla.escribir("1) Un menú normal, con ayuda abajo e iconos:", 3, 3, color="amarillo")
    r = pantalla.menu(["Jugar", "Opciones", "Salir"], titulo="Juego", x=6, y=5,
                      ayudas={"Jugar": "Empieza una partida nueva", "Opciones": "Sonido y dificultad",
                              "Salir": "Vuelve a la demo"},
                      iconos={"Jugar": "►", "Opciones": "*", "Salir": "×"})
    pantalla.escribir("Has elegido: %r" % r, 6, 12, color="verde")
    pantalla.escribir("2) elegir(), en una sola línea:", 3, 14, color="amarillo")
    r = pantalla.elegir("¿Dificultad?", ["Fácil", "Normal", "Difícil"], 6, 16)
    pantalla.escribir("Has elegido: %r" % r, 6, 17, color="verde")
    pantalla.esperar("Pulsa una tecla para ver el menú con secciones", 3, 19, color="gris")
    pantalla.limpiar()
    pantalla.cabecera("Menú con secciones")
    r = pantalla.menu({"Operaciones": ["Sumar", "Restar", "Multiplicar"],
                       "Determinantes": ["Determinante", "Inversa"],
                       "Otros": ["Historial", "Ajustes", "Volver"]},
                      ayudas={"Sumar": "Suma dos matrices del mismo tamaño", "Volver": "Vuelve a la demo"},
                      iconos={"Sumar": "+", "Restar": "-", "Multiplicar": "×", "Determinante": "|A|",
                              "Inversa": "A⁻¹", "Historial": "≡", "Ajustes": "*", "Volver": "←"},
                      titulo="Como en el proyecto de matrices", y=3)
    pantalla.escribir("Has elegido: %r" % r, 3, pantalla.alto() - 2, color="verde")
    pantalla.esperar("  Pulsa una tecla para volver", color="gris")


def demo_fuentes():
    fuentes = pantalla.lista_fuentes()
    i = 0
    texto = "Hola"
    while True:
        pantalla.limpiar()
        pantalla.cabecera("Fuentes ASCII · %d de %d" % (i + 1, len(fuentes)))
        pantalla.escribir('pantalla.grande("%s", fuente="%s")' % (texto, fuentes[i]), 3, 3, color="verde")
        pantalla.grande(texto, x=3, y=5, color="amarillo", fuente=fuentes[i])
        pantalla.pie("← → otra fuente · Enter cambiar el texto · Esc volver")
        t = pantalla.tecla()
        if t == "esc":
            return
        if t in ("derecha", "abajo", "espacio"):
            i = (i + 1) % len(fuentes)
        elif t in ("izquierda", "arriba"):
            i = (i - 1) % len(fuentes)
        elif t == "enter":
            nuevo = pantalla.pedir("Texto: ", 3, pantalla.alto() - 2, color="cian")
            texto = nuevo or texto


def demo_matrices():
    pantalla.limpiar()
    pantalla.cabecera("Matrices")
    A = pantalla.pedir_matriz("A")
    if A is None:
        return
    pantalla.calculando()
    pantalla.cabecera("Matrices")
    pantalla.escribir("pantalla.matriz() la dibuja así:", 3, 3, color="amarillo")
    ancho, alto = pantalla.matriz(A, 3, 5, nombre="A")
    pantalla.matriz(A, 3 + ancho + 4, 5, nombre="|A|", det=True, color="cian")
    pantalla.escribir("Y en Python es esta lista: %r" % (A,), 3, 5 + alto + 1, color="verde")
    fila = 5 + alto + 3
    if len(A) == len(A[0]):
        det = pantalla.determinante(A)
        pantalla.escribir("determinante(A) = %s" % det, 3, fila, color="amarillo")
        if det != 0:
            pantalla.matriz(pantalla.inversa(A), 3, fila + 2, nombre="inversa(A)", color="verde")
    else:
        pantalla.matriz(pantalla.transpuesta(A), 3, fila, nombre="transpuesta(A)", color="verde")
    pantalla.pie("Pulsa una tecla para volver")
    pantalla.tecla()


def demo_fracciones():
    pantalla.limpiar()
    pantalla.cabecera("Fracciones y números")
    pantalla.escribir('pantalla.escribir_cuenta("1/2 + 1/3")', 3, 3, color="gris")
    pantalla.escribir_cuenta("1/2 + 1/3", 3, 5)
    pantalla.escribir_cuenta("3/4 : 1/2", 22, 5)
    pantalla.escribir_cuenta("(2/3 - 1/6) · 4", 40, 5, color="cian")
    pantalla.escribir("pantalla.descomponer(360)", 3, 10, color="gris")
    pantalla.descomponer(360, 3, 12)
    pantalla.escribir("mcd(12, 18) = %d    mcm(4, 6) = %d" % (pantalla.mcd(12, 18), pantalla.mcm(4, 6)),
                      30, 12, color="amarillo")
    pantalla.escribir("divisores(36) = %s" % pantalla.divisores(36), 30, 14)
    primos = " ".join(str(n) for n in range(2, 60) if pantalla.es_primo(n))
    pantalla.escribir("primos: " + primos, 30, 16, color="verde")
    pantalla.pie("Pulsa una tecla para volver")
    pantalla.tecla()


def demo_graficas():
    import math

    pantalla.limpiar()
    pantalla.cabecera("Gráficas")
    ancho = max(30, min(60, pantalla.ancho() - 34))
    pantalla.grafica([math.sin, math.cos], -6.3, 6.3, 2, 3, ancho=ancho, alto=12)
    pantalla.escribir("sin(x) y cos(x)", 6, 16, color="gris")
    pantalla.barras({"Ana": 8.5, "Luis": 6, "Marta": 9.75, "Pablo": 4}, ancho + 5, 4, ancho=28,
                    colores=["cian", "amarillo", "verde", "rojo"])
    pantalla.escribir("Ventas: " + pantalla.minigrafica([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]), ancho + 5, 10,
                      color="verde")
    pantalla.pie("Pulsa una tecla para volver")
    pantalla.tecla()


def demo_vectores():
    pantalla.limpiar()
    pantalla.cabecera("Vectores")
    u, v = pantalla.Vector(3, 2), pantalla.Vector(-1, 3)
    ancho, _ = pantalla.dibujar_vectores({"u": u, "v": v, "u+v": u + v}, 2, 3, ancho=36, alto=17)
    x = ancho + 5
    filas = [
        ("u = %s    v = %s" % (u, v), "cian"),
        ("u + v = %s    2u - v = %s" % (u + v, 2 * u - v), None),
        ("u · v = %s" % pantalla.producto_escalar(u, v), None),
        ("|u| = %s" % round(pantalla.modulo(u), 4), None),
        ("ángulo entre u y v = %s°" % round(pantalla.angulo(u, v), 2), None),
        (f"unitario((3, 4)) = {pantalla.unitario((3, 4))}", None),
        ("", None),
        ("En 3D:", "gris"),
        (f"(1, 2, 3) × (4, 5, 6) = {pantalla.producto_vectorial((1, 2, 3), (4, 5, 6))}", "amarillo"),
        ("son_perpendiculares((1, 2), (-2, 1)) = %s" % pantalla.son_perpendiculares((1, 2), (-2, 1)), "verde"),
        ("son_independientes((1, 2, 3), (2, 4, 6)) = %s" % pantalla.son_independientes((1, 2, 3), (2, 4, 6)),
         "rojo claro"),
    ]
    for i, (texto, color) in enumerate(filas):
        pantalla.escribir(texto, x, 4 + i, color=color)
    pantalla.pie("Pulsa una tecla para volver")
    pantalla.tecla()


def demo_polinomios():
    pantalla.limpiar()
    pantalla.cabecera("Polinomios")
    p = pantalla.polinomio("x^3 - 2x^2 - x + 2")
    pantalla.escribir("p(x) = %s" % p, 3, 3, color="cian", negrita=True)
    pantalla.escribir("Ruffini con x = 1:", 3, 5, color="gris")
    pantalla.ruffini(p, 1, x=3, y=6)
    pantalla.escribir("raíces: %s" % pantalla.raices(p), 3, 12)
    pantalla.escribir("p(x) = %s" % pantalla.factorizar_polinomio(p), 3, 13, color="amarillo")
    pantalla.escribir("x² - 5x + 6 = 0, paso a paso:", 3, 15, color="gris")
    pantalla.gotoxy(1, 16)
    for linea in _capturar(lambda: pantalla.ecuacion_segundo_grado(1, -5, 6, pasos=True)):
        pantalla.escribir("  " + linea, nueva_linea=True)
    pantalla.grafica(p, -2, 3, 48, 3, ancho=min(44, pantalla.ancho() - 50), alto=14, color="verde claro")
    pantalla.pie("Pulsa una tecla para volver")
    pantalla.tecla()


def _capturar(funcion):
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        funcion()
    return buf.getvalue().rstrip().splitlines()


def demo_estadistica():
    pantalla.limpiar()
    pantalla.cabecera("Estadística")
    notas = [5, 7, 7, 8, 6, 9, 7, 4, 6, 7, 8, 5, 10, 6, 7]
    pantalla.escribir("notas = %s" % notas, 3, 3, color="cian")
    pantalla.histograma(notas, 3, 5, alto=8)
    pantalla.estadisticas(notas, 34, 5)
    pantalla.escribir("Cambio de base: 45 = %s₂    255 = %s₁₆" % (pantalla.a_binario(45), pantalla.a_hexadecimal(255)),
                      3, 18, color="gris")
    pantalla.pie("Pulsa una tecla para volver")
    pantalla.tecla()


def demo_practicar():
    pantalla.limpiar()
    pantalla.cabecera("Practicar")
    pantalla.gotoxy(1, 3)
    pantalla.mostrar_cursor()
    pantalla.practicar("tablas", 5)
    pantalla.ocultar_cursor()
    pantalla.pie("Pulsa una tecla para volver")
    pantalla.tecla()


def demo_cargas():
    pantalla.limpiar()
    pantalla.cabecera("Barras y pantallas de carga")
    pantalla.ocultar_cursor()
    colores = ["verde", "cian", "morado claro", "amarillo", "verde claro", "azul claro", "rosa", "naranja",
               "cian claro", "rojo claro"]
    estilos = pantalla.lista_barras()
    for i in range(101):
        for n, estilo in enumerate(estilos):
            pantalla.escribir('estilo="%s"' % estilo, 3, 3 + n, color="gris")
            pantalla.barra_progreso(i, 100, 24, 3 + n, ancho=30, estilo=estilo, color=colores[n])
        pantalla.escribir('color_final="verde"', 3, 4 + len(estilos), color="gris")
        pantalla.barra_progreso(i, 100, 24, 4 + len(estilos), ancho=30, estilo="suave", color="rojo",
                                color_final="verde")
        pantalla.pausa(0.02)
    pantalla.pie("Pulsa una tecla para ver una pantalla de carga")
    pantalla.tecla()
    pantalla.pantalla_de_carga("CARGANDO", fuente="ansi_shadow", color="cian", color_final="morado claro",
                               tareas=["Leyendo el mapa", "Colocando enemigos", "Afinando los sonidos",
                                       "Puliendo los gráficos"], segundos=5, marco="redondo",
                               consejos=["Consejo: pantalla_de_carga() también acepta tus funciones",
                                         "Consejo: con total=None la barra va y viene"])


def main():
    import sys

    if len(sys.argv) > 1 and sys.argv[1] in ("depurar", "debug"):
        pantalla.depurar()
        return
    if len(sys.argv) > 1 and sys.argv[1] == "ayuda":
        pantalla.ayuda()
        return

    secciones = {
        "Lo básico": ["Colores", "Cajas y dibujos", "Fuentes ASCII", "Teclado"],
        "Cosas ya hechas": ["Menús", "Tablas, barras y mensajes", "Pantallas de carga", "Pedir datos"],
        "Mates": ["Matrices", "Vectores", "Polinomios", "Estadística", "Fracciones", "Gráficas"],
        "Más": ["Practicar", "Mover una @", "Ver posiciones", "Salir"],
    }
    ayudas = {
        "Colores": "Todos los colores y estilos de texto",
        "Cajas y dibujos": "caja, rodear, rellenar, linea, punto",
        "Fuentes ASCII": "grande() con las 32 fuentes de lista_fuentes()",
        "Teclado": "Pulsa teclas y mira qué devuelve pantalla.tecla()",
        "Menús": "menu() con ayudas e iconos, elegir() y el menú con secciones",
        "Tablas, barras y mensajes": "tabla, barra_progreso, cargando, mensaje",
        "Pantallas de carga": "Los estilos de barra_progreso() y pantalla_de_carga()",
        "Pedir datos": "pedir, pedir_numero y confirmar",
        "Matrices": "pedir_matriz(), matriz(), determinante() e inversa()",
        "Vectores": "dibujar_vectores(), producto escalar y vectorial, módulo y ángulo",
        "Polinomios": "ruffini(), raices(), factorizar_polinomio() y la ecuación de segundo grado",
        "Estadística": "histograma(), estadisticas(), tabla_frecuencias() y cambios de base",
        "Practicar": "practicar(): 5 multiplicaciones, y te corrige",
        "Fracciones": "escribir_cuenta(), descomponer(), mcd, mcm y primos",
        "Gráficas": "grafica(), barras() y minigrafica()",
        "Mover una @": "Un juego mínimo con las flechas",
        "Ver posiciones": "pantalla.depurar(): mueve una cruz y mira x e y",
        "Salir": "Hasta luego",
    }
    iconos = {
        "Colores": "■", "Cajas y dibujos": "┌┐", "Fuentes ASCII": "A", "Teclado": "Aa", "Menús": "≡",
        "Tablas, barras y mensajes": "▤", "Pedir datos": "?", "Pantallas de carga": "▰▱", "Matrices": "[ ]",
        "Vectores": "↗", "Fracciones": "½", "Gráficas": "~", "Polinomios": "x²", "Estadística": "▃▅",
        "Practicar": "✓",
        "Mover una @": "@", "Ver posiciones": "╋", "Salir": "←",
    }
    pantalla.iniciar(titulo="pantalla · demo")
    try:
        elegida = "Colores"
        while True:
            portada()
            elegida = pantalla.menu(secciones, ayudas=ayudas, iconos=iconos, y=10, inicial=elegida)
            if elegida is None or elegida == "Salir":
                break
            if elegida == "Colores":
                demo_colores()
            elif elegida == "Cajas y dibujos":
                demo_cajas()
            elif elegida == "Fuentes ASCII":
                demo_fuentes()
            elif elegida == "Teclado":
                demo_teclas()
            elif elegida == "Menús":
                demo_menus()
            elif elegida == "Tablas, barras y mensajes":
                demo_cosas()
            elif elegida == "Pantallas de carga":
                demo_cargas()
            elif elegida == "Pedir datos":
                demo_pedir()
            elif elegida == "Matrices":
                demo_matrices()
            elif elegida == "Vectores":
                demo_vectores()
            elif elegida == "Polinomios":
                demo_polinomios()
            elif elegida == "Estadística":
                demo_estadistica()
            elif elegida == "Practicar":
                demo_practicar()
            elif elegida == "Fracciones":
                demo_fracciones()
            elif elegida == "Gráficas":
                demo_graficas()
            elif elegida == "Mover una @":
                demo_mover()
            elif elegida == "Ver posiciones":
                pantalla.depurar()
    finally:
        pantalla.terminar()


if __name__ == "__main__":
    main()
