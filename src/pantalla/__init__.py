"""
pantalla: dibuja en la terminal de forma fácil.

    import pantalla

    pantalla.limpiar()
    pantalla.rodear("=")
    pantalla.centrar("¡Hola!", color="amarillo", negrita=True)
    pantalla.gotoxy(5, 3)
    print("Esto está en la columna 5, fila 3")
    pantalla.esperar()

Las posiciones empiezan en 1: (1, 1) es la esquina de arriba a la izquierda,
x es la columna (hacia la derecha) e y la fila (hacia abajo).

Escribe pantalla.ayuda() para ver todo lo que se puede hacer.
"""

from .arte import CODIGOS_COLOR, arte
from .colores import colorear, lista_colores, poner_color, quitar_color
from .cargas import PantallaDeCarga, pantalla_de_carga
from .componentes import (barra_progreso, cabecera, calculando, cargando, elegir, elegir_varios,
                          formulario, lista_barras, mensaje, menu, pie, tabla)
from .dibujo import ESTILOS, caja, linea, linea_vertical, punto, rellenar, rodear
from .disenos import diseno
from .graficas import barras, grafica, minigrafica
from .herramientas import depurar, regla
from .juego import Sprite, cada, fotograma, jugar, pulsada, sprites
from .letras import grande, lista_fuentes, texto_grande
from .raton import (activar_raton, boton, botones, bucle, desactivar_raton, esperar_clic,
                    leer_raton, posicion_raton, zona)
from .matrices import (clasificar_sistema, determinante, escalonar, identidad, inversa, matriz,
                       multiplicar_matrices, pedir_matriz, potencia_matriz, rango, resolver_sistema,
                       restar_matrices, sumar_matrices, transpuesta, traza)
from .numeros import (Fraccion, calcular, descomponer, divisores, es_primo, escribir_cuenta, factorizar,
                      fraccion, mcd, mcm, pedir_fraccion)
from .spinners import Spinner, lista_spinners, spinner
from .vectores import (Vector, angulo, dibujar_vectores, distancia, modulo, multiplicar_vector, pedir_vector,
                       producto_escalar, producto_mixto, producto_vectorial, proyeccion, restar_vectores,
                       son_independientes, son_paralelos, son_perpendiculares, sumar_vectores, unitario,
                       vector, vector_entre)
from .teclado import (confirmar, esperar, pedir, pedir_contrasena, pedir_numero, tecla,
                      tecla_pulsada, vaciar_teclado)
from .terminal import (alto, ancho, centro, gotoxy, guardar_posicion, iniciar, ir_a, limpiar,
                       limpiar_linea, mostrar_cursor, ocultar_cursor, pausa, pitido, tamano,
                       terminar, titulo_ventana, volver_a_posicion)
from .texto import centrar, escribir, escribir_derecha, escribir_lento

__version__ = "0.5.0"

from .terminal import _abrir_en_consola_si_idle as _abrir

if _abrir():
    raise SystemExit
del _abrir

_GRUPOS = [
    ("Pantalla y cursor", ["limpiar", "limpiar_linea", "gotoxy", "ir_a", "ancho", "alto",
                           "tamano", "centro", "ocultar_cursor", "mostrar_cursor",
                           "guardar_posicion", "volver_a_posicion", "titulo_ventana",
                           "pitido", "pausa", "iniciar", "terminar"]),
    ("Escribir", ["escribir", "centrar", "escribir_derecha", "escribir_lento", "grande",
                  "texto_grande", "lista_fuentes", "cabecera", "pie"]),
    ("Colores", ["colorear", "poner_color", "quitar_color", "lista_colores"]),
    ("Dibujar", ["rodear", "caja", "linea", "linea_vertical", "rellenar", "punto", "arte"]),
    ("Teclado", ["tecla", "tecla_pulsada", "vaciar_teclado", "esperar", "pedir",
                 "pedir_numero", "pedir_contrasena", "confirmar"]),
    ("Cosas ya hechas", ["menu", "elegir", "elegir_varios", "formulario", "mensaje", "tabla"]),
    ("Barras y pantallas de carga", ["barra_progreso", "lista_barras", "pantalla_de_carga", "cargando",
                                     "calculando", "spinner", "lista_spinners"]),
    ("Juegos", ["jugar", "Sprite", "sprites", "cada", "fotograma", "pulsada"]),
    ("Matrices", ["matriz", "pedir_matriz", "sumar_matrices", "restar_matrices", "multiplicar_matrices",
                  "transpuesta", "identidad", "traza", "determinante", "inversa", "rango",
                  "potencia_matriz", "escalonar", "resolver_sistema", "clasificar_sistema"]),
    ("Vectores", ["vector", "Vector", "pedir_vector", "vector_entre", "sumar_vectores", "restar_vectores",
                  "multiplicar_vector", "producto_escalar", "producto_vectorial", "producto_mixto", "modulo",
                  "unitario", "distancia", "angulo", "proyeccion", "son_paralelos", "son_perpendiculares",
                  "son_independientes", "dibujar_vectores"]),
    ("Fracciones y números", ["fraccion", "pedir_fraccion", "calcular", "escribir_cuenta", "mcd", "mcm",
                              "es_primo", "divisores", "factorizar", "descomponer"]),
    ("Gráficas", ["grafica", "barras", "minigrafica"]),
    ("Ratón", ["activar_raton", "desactivar_raton", "esperar_clic", "leer_raton",
               "posicion_raton", "zona", "boton", "botones", "bucle"]),
    ("Diseñar y ver posiciones", ["diseno", "regla", "depurar"]),
]

__all__ = [nombre for _, nombres in _GRUPOS for nombre in nombres] + ["ayuda", "Spinner", "PantallaDeCarga", "Fraccion", "ESTILOS",
                                                                     "CODIGOS_COLOR"]


_PARECIDAS = {
    "borrar": "limpiar", "cls": "limpiar", "clear": "limpiar", "borrar_pantalla": "limpiar",
    "print": "escribir", "imprimir": "escribir", "mostrar": "escribir", "poner": "escribir",
    "texto": "escribir", "input": "pedir", "leer": "pedir", "preguntar": "pedir",
    "sleep": "pausa", "dormir": "pausa", "esperar_segundos": "pausa", "wait": "pausa",
    "color": "poner_color", "colores": "lista_colores", "fuentes": "lista_fuentes",
    "posicion": "gotoxy", "mover": "gotoxy", "cursor": "gotoxy", "goto": "gotoxy",
    "rectangulo": "caja", "cuadro": "caja", "recuadro": "caja", "marco": "rodear", "borde": "rodear",
    "titulo": "cabecera", "letras_grandes": "grande", "teclado": "tecla", "getch": "tecla",
    "clic": "esperar_clic", "click": "esperar_clic", "raton": "activar_raton",
    "juego": "jugar", "bucle_juego": "jugar", "progreso": "barra_progreso", "barra": "barra_progreso",
    "sumar": "sumar_matrices", "suma": "sumar_matrices", "restar": "restar_matrices", "resta": "restar_matrices",
    "multiplicar": "multiplicar_matrices", "producto": "multiplicar_matrices", "det": "determinante",
    "traspuesta": "transpuesta", "inverso": "inversa", "gauss": "escalonar", "sistema": "resolver_sistema",
    "resolver": "resolver_sistema", "ecuaciones": "resolver_sistema", "potencia": "potencia_matriz",
    "fracciones": "fraccion", "dividir": "calcular", "cuenta": "calcular", "operacion": "calcular",
    "maximo_comun_divisor": "mcd", "minimo_comun_multiplo": "mcm", "gcd": "mcd", "lcm": "mcm",
    "primo": "es_primo", "primos": "es_primo", "factores": "factorizar", "descomposicion": "descomponer",
    "dibujar_funcion": "grafica", "funcion": "grafica", "grafico": "grafica", "plot": "grafica",
    "barra_grafica": "barras", "histograma": "barras", "sparkline": "minigrafica",
    "checkbox": "elegir_varios", "marcar": "elegir_varios", "casillas": "elegir_varios",
    "formularios": "formulario", "pedir_datos": "formulario", "pedir_varios": "formulario",
    "loading": "pantalla_de_carga", "pantalla_carga": "pantalla_de_carga", "carga": "pantalla_de_carga",
    "loading_screen": "pantalla_de_carga", "cargar": "pantalla_de_carga", "estilos_barra": "lista_barras",
    "barras_progreso": "lista_barras", "progress": "barra_progreso", "progressbar": "barra_progreso",
    "vectores": "vector", "norma": "modulo", "magnitud": "modulo", "longitud": "modulo", "modulo_vector": "modulo",
    "producto_punto": "producto_escalar", "producto_interno": "producto_escalar", "dot": "producto_escalar",
    "producto_cruz": "producto_vectorial", "cross": "producto_vectorial", "producto_exterior": "producto_vectorial",
    "angulo_vectores": "angulo", "sumar_vector": "sumar_vectores", "restar_vector": "restar_vectores",
    "vector_unitario": "unitario", "normalizar": "unitario", "dibujar_vector": "dibujar_vectores",
    "flechas": "dibujar_vectores", "independientes": "son_independientes", "perpendiculares": "son_perpendiculares",
    "paralelos": "son_paralelos", "ortogonales": "son_perpendiculares",
}


def _normalizar(nombre):
    import unicodedata

    sin_tildes = unicodedata.normalize("NFD", nombre)
    return "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn").lower()


def _buscar(nombre):
    """El nombre de verdad si lo has escrito con tildes, ñ o mayúsculas (tamaño -> tamano)."""
    buscado = _normalizar(nombre)
    for de_verdad in __all__:
        if _normalizar(de_verdad) == buscado:
            return de_verdad
    return None


def __getattr__(nombre):
    if nombre.startswith("_"):
        raise AttributeError("module 'pantalla' has no attribute %r" % nombre)
    de_verdad = _buscar(nombre)
    if de_verdad is not None:
        return globals()[de_verdad]
    import difflib

    parecidas = []
    if _normalizar(nombre) in _PARECIDAS:
        parecidas.append(_PARECIDAS[_normalizar(nombre)])
    for p in difflib.get_close_matches(_normalizar(nombre), __all__, n=3, cutoff=0.6):
        if p not in parecidas:
            parecidas.append(p)
    aviso = "pantalla no tiene ninguna función que se llame '%s'." % nombre
    if parecidas:
        aviso += " ¿Querías decir " + " o ".join("pantalla.%s" % p for p in parecidas[:3]) + "?"
    aviso += " Para ver todas: pantalla.ayuda()"
    raise AttributeError(aviso)


def _primera_linea(nombre):
    return (globals()[nombre].__doc__ or "").strip().split("\n")[0]


def _explicacion(funcion):
    texto = (funcion.__doc__ or "(sin explicación)").strip("\n")
    lineas = texto.split("\n")
    sangria = min([len(l) - len(l.lstrip()) for l in lineas[1:] if l.strip()] or [0])
    return [lineas[0].strip()] + [l[sangria:] for l in lineas[1:]]


def _ayuda_interactiva():
    from .terminal import _estado
    from .teclado import _modo, _activar_modo_teclas, _desactivar_modo_teclas

    ya_aparte = _estado["pantalla_aparte"]
    ya_teclas = _modo["original"] is not None
    if not ya_aparte:
        iniciar(cursor=True)
    else:
        _activar_modo_teclas()
    titulos = [t for t, _ in _GRUPOS]
    resumen = {t: ", ".join(n) for t, n in _GRUPOS}
    seccion = titulos[0]
    elegida = None
    try:
        while True:
            if elegida is None:
                limpiar()
                cabecera("pantalla %s · ayuda" % __version__)
                pie("Elige un tema · Enter entrar · Esc salir")
                seccion = menu(titulos, titulo="Temas", ayudas=resumen, inicial=seccion)
                if seccion is None:
                    return
            nombres = dict(_GRUPOS)[seccion]
            limpiar()
            cabecera("pantalla %s · ayuda · %s" % (__version__, seccion))
            pie("Elige una función y pulsa Enter para ver cómo se usa · Esc volver a los temas")
            elegida = menu(nombres, titulo=seccion, inicial=elegida or 0,
                           ayudas={n: _primera_linea(n) for n in nombres})
            if elegida is None:
                continue
            limpiar()
            cabecera("pantalla." + elegida)
            fila = 3
            for linea_texto in _explicacion(globals()[elegida]):
                if fila >= alto() - 1:
                    break
                es_codigo = linea_texto.startswith("    ")
                escribir(linea_texto, 3, fila, color="verde claro" if es_codigo else None,
                         negrita=fila == 3)
                fila = fila + 1
            pie("Pulsa una tecla para volver a la lista")
            tecla()
    finally:
        if not ya_aparte:
            terminar()
        elif not ya_teclas:
            _desactivar_modo_teclas()


def ayuda(funcion=None):
    """Enseña todas las funciones de pantalla, o la explicación de una.

        pantalla.ayuda()            # en una terminal: un menú para ir mirándolas
        pantalla.ayuda("caja")      # cómo se usa caja
        pantalla.ayuda(pantalla.caja)

    Fuera de una terminal (por ejemplo en IDLE), escribe la lista entera.
    """
    import sys

    from .terminal import _es_terminal

    if funcion is not None:
        if isinstance(funcion, str):
            funcion = _buscar(funcion.strip().replace("pantalla.", "").rstrip("()")) or funcion
            if funcion not in __all__ or funcion in ("ESTILOS", "CODIGOS_COLOR"):
                print("No hay ninguna función que se llame %r. Mira la lista con pantalla.ayuda()" % funcion)
                return
            funcion = globals()[funcion]
        print("pantalla.%s" % funcion.__name__)
        print()
        print("\n".join(_explicacion(funcion)))
        return
    if _es_terminal(sys.stdin) and _es_terminal(sys.stdout):
        _ayuda_interactiva()
        return
    print("pantalla %s · todo lo que puedes usar:" % __version__)
    for titulo, nombres in _GRUPOS:
        print()
        print("  " + titulo.upper())
        for nombre in nombres:
            print("    pantalla.%-18s %s" % (nombre, _primera_linea(nombre)))
    print()
    print("Para ver cómo se usa una: pantalla.ayuda(\"caja\")")
    print("Colores: " + ", ".join(lista_colores()))
    print("Estilos de borde: " + ", ".join(ESTILOS) + ", o un carácter como \"=\"")
    print("Para ver una demostración, escribe en la terminal:  python -m pantalla")
