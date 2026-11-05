"""
Cosas ya hechas: menús con flechas, ventanas de mensaje, tablas,
barras de progreso y la animación de "cargando".
"""

import sys
import time

from .colores import estilo as _estilo_ansi
from .dibujo import _piezas, caja
from .teclado import _con_teclas, _ventana, tecla
from .dibujo import rellenar
from .terminal import (CSI, ESC, _entero, _estado, _fin_de_estilo, _mover, _posicion, _salida,
                       mostrar_cursor, ocultar_cursor, tamano)
from .texto import escribir


def _centrar_caja(x, y, ancho, alto):
    ancho_p, alto_p = tamano()
    if x is None:
        x = max(1, (ancho_p - ancho) // 2 + 1)
    if y is None:
        y = max(1, (alto_p - alto) // 2 + 1)
    return x, y


def _ayuda_de(ayudas, opcion, indice):
    if not ayudas:
        return ""
    if isinstance(ayudas, dict):
        return str(ayudas.get(opcion, ""))
    if 0 <= indice < len(ayudas):
        return str(ayudas[indice])
    return ""


def _recortar(texto, largo):
    if largo <= 0:
        return ""
    if len(texto) <= largo:
        return texto
    return texto[: largo - 1] + "…"


def _sitio_ayuda(ayuda_x, ayuda_y, x, fila_debajo):
    ax = x if ayuda_x is None else ayuda_x
    ay = fila_debajo if ayuda_y is None else ayuda_y
    return _posicion(ax, ay, "menu (ayuda_x, ayuda_y)")


def _indice_inicial(inicial, opciones):
    if isinstance(inicial, str):
        if inicial in opciones:
            return opciones.index(inicial)
        return 0
    return max(0, min(int(inicial), len(opciones) - 1))


@_ventana
def menu(opciones, titulo=None, x=None, y=None, color=None, color_seleccion="amarillo",
         estilo="redondo", inicial=0, ayudas=None, iconos=None, ayuda_x=None, ayuda_y=None,
         color_ayuda=None):
    """Enseña un menú en una caja y deja elegir con las flechas y Enter.

    Devuelve el texto de la opción elegida, o None si pulsas Esc.
    También puedes pulsar el número de la opción.

        opcion = pantalla.menu(["Jugar", "Opciones", "Salir"], titulo="Menú")
        if opcion == "Jugar":
            ...

    - ayudas: una explicación de cada opción, que sale debajo al pasar por ella.
    - ayuda_x, ayuda_y: dónde poner esa explicación, si no la quieres justo debajo.
    - color_ayuda: el color de la explicación (si no, el de color_seleccion).
    - iconos: un dibujito o símbolo para cada opción.
    - inicial: la opción que sale marcada al empezar (su texto o su número).

        pantalla.menu(["Jugar", "Salir"],
                      ayudas={"Jugar": "Empieza una partida", "Salir": "Cierra el juego"},
                      iconos={"Jugar": "►", "Salir": "×"})

        AYUDA = {"Jugar": "Empieza una partida", "Salir": "Cierra el juego"}
        pantalla.menu(["Jugar", "Salir"], ayudas=AYUDA, ayuda_x=3, ayuda_y=pantalla.alto() - 2)

    Si en vez de una lista le das un diccionario, hace un menú con secciones en cajas
    (como el de un programa de verdad) y te mueves con las cuatro flechas:

        pantalla.menu({"Operaciones": ["Sumar", "Restar"],
                       "Otros": ["Ajustes", "Salir"]})

    Sin x ni y, el menú sale en el centro de la pantalla.
    """
    if isinstance(opciones, dict):
        return _menu_secciones(opciones, titulo, x, y, color, color_seleccion, estilo,
                               inicial, ayudas, iconos, ayuda_x, ayuda_y, color_ayuda)
    opciones = [str(o) for o in opciones]
    if color_ayuda is None:
        color_ayuda = color_seleccion
    ayuda_debajo = bool(ayudas) and ayuda_y is None
    if not opciones:
        raise ValueError("menu: necesito al menos una opción")
    numeros = len(opciones) <= 9
    ancho_icono = 0
    if iconos:
        ancho_icono = max(len(str(iconos.get(o, ""))) for o in opciones)
    textos = []
    for i, o in enumerate(opciones):
        t = o
        if ancho_icono:
            t = str(iconos.get(o, "")).center(ancho_icono) + "  " + t
        if numeros:
            t = "%d. %s" % (i + 1, t)
        textos.append(t)
    ancho_caja = max(len(t) for t in textos) + 6
    if titulo is not None:
        ancho_caja = max(ancho_caja, len(str(titulo)) + 8)
    ancho_p, alto_p = tamano()
    extra = 2 if ayuda_debajo else 1
    visibles = max(1, min(len(opciones), alto_p - 2 - extra))
    alto_caja = visibles + 2
    largo_ayuda = 0
    if ayudas:
        largo_ayuda = max(len(_ayuda_de(ayudas, o, i)) for i, o in enumerate(opciones)) + 2
    x, y = _centrar_caja(x, y, ancho_caja, alto_caja + extra)
    x, y = _posicion(x, y, "menu")
    ax, ay = _sitio_ayuda(ayuda_x, ayuda_y, x, y + alto_caja)
    largo_ayuda = min(largo_ayuda, ancho_p - ax + 1)

    estaba_oculto = _estado["cursor_oculto"]
    ocultar_cursor()
    seleccion = _indice_inicial(inicial, opciones)
    primera = 0
    caja(x, y, ancho_caja, alto_caja, estilo, color=color, titulo=titulo, relleno=True)
    lado = _piezas(estilo, "menu")[10]
    fila_pista = y + alto_caja + (1 if ayuda_debajo else 0)
    if ayudas and ay == fila_pista:
        fila_pista = fila_pista + 1
    if fila_pista <= alto_p:
        escribir("↑↓ elegir · Enter aceptar · Esc salir"[: max(0, ancho_p - x)], x, fila_pista, tenue=True)
    try:
        while True:
            if seleccion < primera:
                primera = seleccion
            elif seleccion >= primera + visibles:
                primera = seleccion - visibles + 1
            for fila in range(visibles):
                i = primera + fila
                t = textos[i]
                if i == seleccion:
                    escribir((" ▶ " + t).ljust(ancho_caja - 2), x + 1, y + 1 + fila,
                             color="negro", fondo=color_seleccion, negrita=True)
                else:
                    escribir(("   " + t).ljust(ancho_caja - 2), x + 1, y + 1 + fila, color=color)
            if visibles < len(opciones):
                escribir("▲" if primera > 0 else lado, x + ancho_caja - 1, y + 1, color=color)
                escribir("▼" if primera + visibles < len(opciones) else lado, x + ancho_caja - 1,
                         y + visibles, color=color)
            if ayudas and ay <= alto_p and largo_ayuda > 0:
                texto = _recortar("» " + _ayuda_de(ayudas, opciones[seleccion], seleccion), largo_ayuda)
                escribir(texto.ljust(largo_ayuda), ax, ay, color=color_ayuda)
            t = tecla()
            if t in ("arriba", "w", "W"):
                seleccion = (seleccion - 1) % len(opciones)
            elif t in ("abajo", "s", "S", "tab"):
                seleccion = (seleccion + 1) % len(opciones)
            elif t in ("enter", "espacio"):
                return opciones[seleccion]
            elif t == "esc":
                return None
            elif numeros and t.isdigit() and 1 <= int(t) <= len(opciones):
                return opciones[int(t) - 1]
    finally:
        if not estaba_oculto:
            mostrar_cursor()


@_con_teclas
def _menu_secciones(secciones, titulo, x, y, color, color_seleccion, estilo, inicial, ayudas, iconos,
                    ayuda_x=None, ayuda_y=None, color_ayuda=None):
    if color_ayuda is None:
        color_ayuda = color_seleccion
    ayuda_debajo = bool(ayudas) and ayuda_y is None
    nombres = [str(s) for s in secciones]
    grupos = [[str(o) for o in secciones[s]] for s in secciones]
    todas = [o for grupo in grupos for o in grupo]
    if not todas:
        raise ValueError("menu: necesito al menos una opción")
    ancho_icono = 0
    if iconos:
        ancho_icono = max(len(str(iconos.get(o, ""))) for o in todas)

    def etiqueta(o):
        if ancho_icono:
            return str(iconos.get(o, "")).center(ancho_icono) + "  " + o
        return o

    ancho_p, alto_p = tamano()
    ancho_col = max([len(etiqueta(o)) + 6 for o in todas] + [len(n) + 8 for n in nombres] + [20])
    columnas = 2 if len(grupos) > 1 and ancho_col * 2 + 2 <= ancho_p else 1

    reparto = [[] for _ in range(columnas)]
    alturas = [0] * columnas
    for i, grupo in enumerate(grupos):
        c = alturas.index(min(alturas))
        reparto[c].append(i)
        alturas[c] = alturas[c] + len(grupo) + 2

    largo_ayuda = 0
    if ayudas:
        largo_ayuda = max(len(_ayuda_de(ayudas, o, i)) for i, o in enumerate(todas)) + 2
    ancho_bloque = columnas * ancho_col + (columnas - 1) * 2
    arriba = 2 if titulo is not None else 0
    abajo = 2 if ayuda_debajo else 1
    if max(alturas) + arriba + abajo > alto_p:
        return menu(todas, titulo, x, y, color, color_seleccion, estilo, inicial, ayudas, iconos,
                    ayuda_x, ayuda_y, color_ayuda)
    x, y = _centrar_caja(x, y, ancho_bloque, max(alturas) + arriba + abajo)
    x, y = _posicion(x, y, "menu")
    ax, ay = _sitio_ayuda(ayuda_x, ayuda_y, x, y + arriba + max(alturas))
    largo_ayuda = min(largo_ayuda, ancho_p - ax + 1)

    estaba_oculto = _estado["cursor_oculto"]
    ocultar_cursor()
    if titulo is not None:
        escribir(str(titulo), x + max(0, (ancho_bloque - len(str(titulo))) // 2), y,
                 color=color_seleccion, negrita=True)

    sitios = []
    for c in range(columnas):
        xx = x + c * (ancho_col + 2)
        yy = y + arriba
        for i in reparto[c]:
            caja(xx, yy, ancho_col, len(grupos[i]) + 2, estilo, color=color, titulo=nombres[i],
                 relleno=True)
            for k, o in enumerate(grupos[i]):
                sitios.append((o, c, xx + 1, yy + 1 + k))
            yy = yy + len(grupos[i]) + 2
    orden = [o for o in todas]
    sitios.sort(key=lambda s: orden.index(s[0]))

    fila_pista = y + arriba + max(alturas) + (1 if ayuda_debajo else 0)
    if ayudas and ay == fila_pista:
        fila_pista = fila_pista + 1
    if fila_pista <= alto_p:
        pista = "↑↓ moverse · ←→ cambiar de columna · Enter aceptar · Esc salir"
        if columnas == 1:
            pista = "↑↓ moverse · Enter aceptar · Esc salir"
        escribir(pista[: max(0, ancho_p - x)], x, fila_pista, tenue=True)

    actual = _indice_inicial(inicial, todas)
    try:
        while True:
            for i, (o, c, xx, yy) in enumerate(sitios):
                if i == actual:
                    escribir((" ▶ " + etiqueta(o)).ljust(ancho_col - 2), xx, yy,
                             color="negro", fondo=color_seleccion, negrita=True)
                else:
                    escribir(("   " + etiqueta(o)).ljust(ancho_col - 2), xx, yy, color=color)
            if ayudas and ay <= alto_p and largo_ayuda > 0:
                texto = _recortar("» " + _ayuda_de(ayudas, todas[actual], actual), largo_ayuda)
                escribir(texto.ljust(largo_ayuda), ax, ay, color=color_ayuda)
            t = tecla()
            yo = sitios[actual]
            misma = [i for i, s in enumerate(sitios) if s[1] == yo[1]]
            otra = [i for i, s in enumerate(sitios) if s[1] != yo[1]]
            if t in ("arriba", "w", "W"):
                actual = misma[(misma.index(actual) - 1) % len(misma)]
            elif t in ("abajo", "s", "S", "tab"):
                actual = misma[(misma.index(actual) + 1) % len(misma)]
            elif t in ("izquierda", "derecha", "a", "A", "d", "D") and otra:
                actual = min(otra, key=lambda i: abs(sitios[i][3] - yo[3]))
            elif t in ("enter", "espacio"):
                return todas[actual]
            elif t == "esc":
                return None
    finally:
        if not estaba_oculto:
            mostrar_cursor()


@_con_teclas
def elegir(pregunta, opciones, x=None, y=None, inicial=0, color=None, color_seleccion="amarillo"):
    """Hace una pregunta con las opciones en fila; se elige con ← → y Enter.

        r = pantalla.elegir("¿Desarrollar por?", ["Fila", "Columna"])
        dificultad = pantalla.elegir("Dificultad:", ["Fácil", "Normal", "Difícil"], 5, 10)

    Devuelve el texto de la opción elegida, o None si pulsas Esc.
    """
    opciones = [str(o) for o in opciones]
    if not opciones:
        raise ValueError("elegir: necesito al menos una opción")
    seleccion = _indice_inicial(inicial, opciones)
    sin_sitio = x is None and y is None
    if sin_sitio:
        _salida(ESC + "7")
    estaba_oculto = _estado["cursor_oculto"]
    ocultar_cursor()
    try:
        while True:
            if sin_sitio:
                _salida(ESC + "8")
                escribir(str(pregunta) + " ", color=color)
            else:
                escribir(str(pregunta) + " ", x, y, color=color)
            for i, o in enumerate(opciones):
                if i == seleccion:
                    escribir(" " + o + " ", color="negro", fondo=color_seleccion, negrita=True)
                else:
                    escribir(" " + o + " ")
                escribir(" ")
            t = tecla()
            if t in ("izquierda", "a", "A", "arriba"):
                seleccion = (seleccion - 1) % len(opciones)
            elif t in ("derecha", "d", "D", "abajo", "tab"):
                seleccion = (seleccion + 1) % len(opciones)
            elif t in ("enter", "espacio"):
                if sin_sitio:
                    escribir("", nueva_linea=True)
                return opciones[seleccion]
            elif t == "esc":
                if sin_sitio:
                    escribir("", nueva_linea=True)
                return None
            elif t.isdigit() and 1 <= int(t) <= len(opciones):
                seleccion = int(t) - 1
    finally:
        if not estaba_oculto:
            mostrar_cursor()


@_ventana
def mensaje(texto, titulo="Aviso", color=None, color_borde="cian", estilo="doble",
            esperar_tecla=True):
    """Saca una ventanita en el centro con un mensaje y espera a que pulses una tecla.

        pantalla.mensaje("¡Has ganado!", titulo="Enhorabuena", color_borde="verde")
        pantalla.mensaje("No hay más vidas\\nPuntos: 120", titulo="Fin")

    Devuelve la tecla pulsada.
    """
    lineas = str(texto).split("\n")
    pie = "Pulsa una tecla"
    ancho_caja = max([len(l) for l in lineas] + [len(pie), len(str(titulo)) + 4]) + 6
    alto_caja = len(lineas) + 4 + (1 if esperar_tecla else 0)
    x, y = _centrar_caja(None, None, ancho_caja, alto_caja)
    caja(x, y, ancho_caja, alto_caja, estilo, color=color_borde, titulo=titulo, relleno=True)
    for i, linea in enumerate(lineas):
        escribir(linea, x + (ancho_caja - len(linea)) // 2, y + 2 + i, color=color)
    if esperar_tecla:
        escribir(pie, x + (ancho_caja - len(pie)) // 2, y + alto_caja - 2, tenue=True)
        estaba_oculto = _estado["cursor_oculto"]
        ocultar_cursor()
        try:
            return tecla()
        finally:
            if not estaba_oculto:
                mostrar_cursor()
    return None


# estilo: (lleno, vacío). los que no tienen letras se pintan aparte
ESTILOS_BARRA = {
    "bloques": ("█", "░"),
    "suave": None,
    "linea": None,
    "ascii": None,
    "puntos": ("⣿", "⣀"),
    "cuadros": ("■", "□"),
    "circulos": ("●", "○"),
    "rombos": ("◆", "◇"),
    "flechas": ("▰", "▱"),
    "rayas": ("▮", "▯"),
}
_OCTAVOS = "▏▎▍▌▋▊▉"
_FONDO_VACIO = 236


def lista_barras():
    """Devuelve los nombres de los estilos de barra_progreso() y pantalla_de_carga().

        for estilo in pantalla.lista_barras():
            print(estilo)
    """
    return list(ESTILOS_BARRA)


def _estilo_barra(estilo, funcion):
    from .colores import _normalizar
    if not isinstance(estilo, str):
        raise TypeError("%s: el estilo es un nombre, como \"suave\" o \"ascii\". Me has dado %r"
                        % (funcion, estilo))
    nombre = _normalizar(estilo)
    nombre = {"linea": "linea", "circulo": "circulos", "cuadro": "cuadros", "punto": "puntos",
              "rombo": "rombos", "flecha": "flechas", "raya": "rayas", "bloque": "bloques"}.get(nombre, nombre)
    if nombre not in ESTILOS_BARRA:
        import difflib
        parecido = difflib.get_close_matches(nombre, list(ESTILOS_BARRA), n=1)
        mensaje = "%s: no conozco el estilo de barra %r." % (funcion, estilo)
        if parecido:
            mensaje += " ¿Querías decir %r?" % parecido[0]
        raise ValueError(mensaje + " Hay estos: " + ", ".join(ESTILOS_BARRA))
    return nombre


def _colores_barra(color, color_final, ancho):
    """Un código de color para cada casilla (si hay color_final, va cambiando poco a poco)."""
    if color_final is None:
        return [_estilo_ansi(color)] * ancho
    from .colores import _mezclar, _rgb
    a, b = _rgb(color), _rgb(color_final)
    if a is None or b is None:
        raise ValueError("color_final: para mezclar colores usa nombres, '#rrggbb' o (r, g, b), no números")
    return [_estilo_ansi(_mezclar(a, b, i / float(max(1, ancho - 1)))) for i in range(ancho)]


def _pintar_barra(fraccion, ancho, estilo="bloques", color="verde", color_final=None, lleno=None,
                  vacio=None, funcion="barra_progreso", trozo=None):
    """Devuelve la barra ya con colores. trozo=(desde, largo) pinta solo un trozo lleno (para la que rebota)."""
    estilo = _estilo_barra(estilo, funcion)
    fin = _fin_de_estilo()
    gris = _estilo_ansi("gris")
    cods = _colores_barra(color, color_final, ancho)
    if trozo is None:
        llenas = set(range(int(round(fraccion * ancho))))
    else:
        llenas = set(range(trozo[0], trozo[0] + trozo[1]))
    if lleno is not None or vacio is not None:
        if ESTILOS_BARRA[estilo] is None:
            estilo = "bloques"
        lleno = ESTILOS_BARRA[estilo][0] if lleno is None else str(lleno)
        vacio = ESTILOS_BARRA[estilo][1] if vacio is None else str(vacio)
    if estilo == "ascii" and lleno is None:
        dentro = ancho - 2
        if dentro < 1:
            raise ValueError("%s: con el estilo \"ascii\" el ancho tiene que ser 3 o más" % funcion)
        if trozo is None:
            n = int(round(fraccion * dentro))
            letras = "=" * n if n >= dentro else ("=" * max(0, n - 1) + (">" if n else "")).ljust(dentro)
        else:
            desde = min(trozo[0], max(0, dentro - trozo[1]))
            letras = "".join("=" if desde <= i < desde + trozo[1] else " " for i in range(dentro))
        return gris + "[" + fin + cods[0] + letras + fin + gris + "]" + fin
    casillas = []
    if estilo == "suave" and lleno is None:
        fondo = _estilo_ansi(fondo=_FONDO_VACIO)
        octavos = int(round(fraccion * ancho * 8)) if trozo is None else None
        for i in range(ancho):
            if trozo is not None:
                casillas.append((cods[i], "█") if i in llenas else (fondo, " "))
            elif octavos >= (i + 1) * 8:
                casillas.append((cods[i], "█"))
            elif octavos > i * 8:
                casillas.append((_mezcla_fondo(cods[i]), _OCTAVOS[octavos - i * 8 - 1]))
            else:
                casillas.append((fondo, " "))
    elif estilo == "linea" and lleno is None:
        medios = int(round(fraccion * ancho * 2)) if trozo is None else None
        for i in range(ancho):
            if trozo is not None:
                casillas.append((cods[i] if i in llenas else gris, "━"))
            elif medios >= (i + 1) * 2:
                casillas.append((cods[i], "━"))
            elif medios > i * 2:
                casillas.append((cods[i], "╸"))
            else:
                casillas.append((gris, "━"))
    else:
        if lleno is None:
            lleno, vacio = ESTILOS_BARRA[estilo]
        for i in range(ancho):
            casillas.append((cods[i], lleno) if i in llenas else (gris, vacio))
    # junta las casillas seguidas del mismo color
    texto, anterior = "", None
    for cod, letra in casillas:
        if cod != anterior:
            texto += (fin if anterior else "") + cod
            anterior = cod
        texto += letra
    return texto + (fin if anterior else "")


def _mezcla_fondo(codigo):
    # el color de la barra por delante y el gris oscuro por detrás, en un solo código
    fondo = _estilo_ansi(fondo=_FONDO_VACIO)
    if not codigo:
        return fondo
    return codigo[:-1] + ";" + fondo[2:]


def barra_progreso(valor, total=100, x=None, y=None, ancho=30, color="verde",
                   porcentaje=True, lleno=None, vacio=None, estilo="bloques", color_final=None,
                   texto=None):
    """Dibuja una barra de progreso. Llámala otra vez con otro valor para que avance.

        for i in range(101):
            pantalla.barra_progreso(i, 100, 10, 5)
            pantalla.pausa(0.02)

        pantalla.barra_progreso(40, 100, 10, 5, estilo="suave", color="cian")
        pantalla.barra_progreso(vida, 100, 2, 1, color="rojo", color_final="verde", texto="Vida")

    - estilo: "bloques" ███░░░, "suave" (avanza de octavo en octavo), "linea" ━━━╺──,
      "ascii" [===>  ], "puntos" ⣿⣿⣀⣀, "cuadros" ■■□□, "circulos" ●●○○, "rombos" ◆◆◇◇,
      "flechas" ▰▰▱▱ y "rayas" ▮▮▯▯. Están todos en pantalla.lista_barras().
    - color_final: la barra va cambiando de color hasta este (de rojo a verde, por ejemplo).
    - lleno, vacio: tus propios caracteres (mandan sobre los del estilo).
    - texto: un nombre que se escribe delante de la barra.
    Sin x ni y, la dibuja en la línea donde esté el cursor (y la va sobrescribiendo).
    """
    ancho = _entero(ancho, "ancho", "barra_progreso")
    if ancho < 1:
        raise ValueError("barra_progreso: el ancho tiene que ser 1 o más")
    if total == 0:
        fraccion = 1.0
    else:
        fraccion = max(0.0, min(1.0, float(valor) / float(total)))
    barra = _pintar_barra(fraccion, ancho, estilo, color, color_final, lleno, vacio)
    if texto is not None:
        barra = str(texto) + " " + barra
    if porcentaje:
        barra = barra + " %3d%%" % int(round(fraccion * 100))
    if x is None and y is None:
        _salida("\r" + barra)
    else:
        if x is None:
            x = 1
        if y is None:
            _salida("\r" + CSI + "%dG" % _entero(x, "x", "barra_progreso") + barra)
        else:
            x, y = _posicion(x, y, "barra_progreso")
            _salida(_mover(x, y) + barra)


def cargando(segundos=2, texto="Cargando", x=None, y=None, color="amarillo"):
    """Enseña una animación de "Cargando..." durante unos segundos.

        pantalla.cargando(3, "Guardando partida")
    """
    vueltas = "|/-\\"
    inicio = time.time()
    paso = 0
    estaba_oculto = _estado["cursor_oculto"]
    ocultar_cursor()
    try:
        while time.time() - inicio < segundos:
            puntos = "." * (paso // 3 % 4)
            frase = "%s %s%s" % (vueltas[paso % 4], texto, puntos)
            if x is None and y is None:
                _salida("\r" + CSI + "2K")
                escribir(frase, color=color)
            else:
                escribir(frase.ljust(len(texto) + 6), x, y, color=color)
            sys.stdout.flush()
            time.sleep(0.1)
            paso = paso + 1
        final = "✓ " + texto
        if x is None and y is None:
            _salida("\r" + CSI + "2K")
            escribir(final, color="verde", nueva_linea=True)
        else:
            escribir(final.ljust(len(texto) + 6), x, y, color="verde")
    finally:
        if not estaba_oculto:
            mostrar_cursor()


def tabla(filas, cabeceras=None, x=None, y=None, estilo="simple", color=None,
          color_cabecera="cian"):
    """Dibuja una tabla con bordes.

        notas = [["Ana", 8.5], ["Luis", 6], ["Marta", 9.75]]
        pantalla.tabla(notas, cabeceras=["Nombre", "Nota"])
        pantalla.tabla(notas, ["Nombre", "Nota"], x=5, y=3, estilo="doble")

    Sin x ni y, se escribe donde esté el cursor (como un print).
    Los números se alinean a la derecha y los textos a la izquierda.
    """
    datos = []
    for fila in filas:
        if isinstance(fila, (str, int, float)):
            fila = [fila]
        datos.append(list(fila))
    if cabeceras is not None:
        cabeceras = [str(c) for c in cabeceras]
    columnas = max([len(f) for f in datos] + [len(cabeceras) if cabeceras else 0])
    if columnas == 0:
        raise ValueError("tabla: no hay nada que enseñar")
    for fila in datos:
        while len(fila) < columnas:
            fila.append("")
    if cabeceras is not None:
        while len(cabeceras) < columnas:
            cabeceras.append("")

    anchos = [0] * columnas
    for fila in datos + ([cabeceras] if cabeceras else []):
        for i, valor in enumerate(fila):
            anchos[i] = max(anchos[i], len(str(valor)))

    p = _piezas(estilo, "tabla")
    borde = _estilo_ansi(color)
    cab = _estilo_ansi(color_cabecera, negrita=True)

    def b(texto):
        if borde:
            return borde + texto + _fin_de_estilo()
        return texto

    def separador(izq, medio, der):
        return b(izq + medio.join(p[9] * (a + 2) for a in anchos) + der)

    def fila_texto(valores, codigo=""):
        trozos = []
        for i, valor in enumerate(valores):
            if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                celda = str(valor).rjust(anchos[i])
            else:
                celda = str(valor).ljust(anchos[i])
            if codigo:
                celda = codigo + celda + _fin_de_estilo()
            trozos.append(" " + celda + " ")
        return b(p[10]) + b(p[10]).join(trozos) + b(p[10])

    lineas = [separador(p[0], p[1], p[2])]
    if cabeceras is not None:
        lineas.append(fila_texto(cabeceras, cab))
        lineas.append(separador(p[3], p[4], p[5]))
    for fila in datos:
        lineas.append(fila_texto(fila))
    lineas.append(separador(p[6], p[7], p[8]))

    if x is None and y is None:
        _salida("\n".join(lineas) + "\n")
    else:
        if x is None:
            x = 1
        if y is None:
            raise TypeError("tabla: si me das x también necesito y")
        x, y = _posicion(x, y, "tabla")
        _salida("".join(_mover(x, y + i) + l for i, l in enumerate(lineas)))


@_ventana
def calculando(texto="Calculando", segundos=0.8, color="amarillo", color_borde="cian"):
    """Saca una ventanita en el centro con "Calculando..." y los puntitos moviéndose.

    Al acabar la borra. Queda bien antes de enseñar un resultado:

        pantalla.calculando()
        pantalla.calculando("Pensando", segundos=2)
    """
    texto = str(texto)
    ancho_caja = len(texto) + 10
    x, y = _centrar_caja(None, None, ancho_caja, 3)
    estaba_oculto = _estado["cursor_oculto"]
    ocultar_cursor()
    try:
        caja(x, y, ancho_caja, 3, "redondo", color=color_borde, relleno=True)
        inicio = time.time()
        paso = 0
        while True:
            escribir((texto + "." * (paso % 4)).ljust(len(texto) + 3), x + 3, y + 1,
                     color=color, negrita=True)
            if time.time() - inicio >= segundos:
                break
            time.sleep(0.15)
            paso = paso + 1
    finally:
        rellenar(x, y, ancho_caja, 3)
        if not estaba_oculto:
            mostrar_cursor()


def cabecera(titulo, color="cian", caracter="═"):
    """Pone una barra con un título en la primera fila de la pantalla.

        pantalla.cabecera("MATRICES · Suma")
    """
    ancho_p = tamano()[0]
    linea = (str(caracter) * ancho_p)[:ancho_p]
    escribir(linea, 1, 1, color=color)
    escribir(" " + str(titulo) + " ", 4, 1, color=color, negrita=True)


def pie(texto, color="gris"):
    """Escribe un texto en la última fila (por ejemplo, qué teclas se pueden pulsar).

        pantalla.pie("↑↓ moverse   Enter elegir   Esc salir")
    """
    ancho_p, alto_p = tamano()
    _salida(_mover(1, alto_p) + CSI + "2K")
    escribir(str(texto)[: ancho_p - 2], 2, alto_p, color=color)


@_ventana
def elegir_varios(opciones, titulo=None, x=None, y=None, marcadas=None, color=None,
                  color_seleccion="amarillo", estilo="redondo", minimo=0, maximo=None):
    """Una lista para marcar varias opciones: ↑↓ para moverte, Espacio para marcar y Enter para acabar.

        extras = pantalla.elegir_varios(["Queso", "Tomate", "Jamón", "Piña"], titulo="Ingredientes")
        # ['Queso', 'Jamón']

        pantalla.elegir_varios(opciones, marcadas=["Queso"])     # que salgan ya marcadas
        pantalla.elegir_varios(opciones, minimo=1, maximo=2)     # que elijan una o dos

    Devuelve la lista de las opciones marcadas (en el mismo orden), o None si pulsas Esc.
    Sin x ni y, sale en el centro de la pantalla.
    """
    opciones = [str(o) for o in opciones]
    if not opciones:
        raise ValueError("elegir_varios: necesito al menos una opción")
    marcadas = [str(m) for m in (marcadas or [])]
    marcado = [o in marcadas for o in opciones]
    ancho_caja = max(len(o) for o in opciones) + 10
    if titulo is not None:
        ancho_caja = max(ancho_caja, len(str(titulo)) + 8)
    ancho_p, alto_p = tamano()
    visibles = max(1, min(len(opciones), alto_p - 4))
    alto_caja = visibles + 2
    x, y = _centrar_caja(x, y, ancho_caja, alto_caja + 2)
    x, y = _posicion(x, y, "elegir_varios")
    estaba_oculto = _estado["cursor_oculto"]
    ocultar_cursor()
    caja(x, y, ancho_caja, alto_caja, estilo, color=color, titulo=titulo, relleno=True)
    pista = "↑↓ · Espacio marcar · Enter aceptar · Esc salir"
    if y + alto_caja <= alto_p:
        escribir(pista[: max(0, ancho_p - x)], x, y + alto_caja, tenue=True)
    seleccion = 0
    primera = 0
    aviso = ""
    try:
        while True:
            if seleccion < primera:
                primera = seleccion
            elif seleccion >= primera + visibles:
                primera = seleccion - visibles + 1
            for fila in range(visibles):
                i = primera + fila
                t = " %s %s " % ("[x]" if marcado[i] else "[ ]", opciones[i])
                if i == seleccion:
                    escribir(("▶" + t).ljust(ancho_caja - 2), x + 1, y + 1 + fila,
                             color="negro", fondo=color_seleccion, negrita=True)
                else:
                    escribir((" " + t).ljust(ancho_caja - 2), x + 1, y + 1 + fila,
                             color="verde" if marcado[i] else color)
            if y + alto_caja + 1 <= alto_p:
                escribir(aviso.ljust(len(pista))[: max(0, ancho_p - x)], x, y + alto_caja + 1, color="rojo")
            t = tecla()
            aviso = ""
            if t in ("arriba", "w", "W"):
                seleccion = (seleccion - 1) % len(opciones)
            elif t in ("abajo", "s", "S", "tab"):
                seleccion = (seleccion + 1) % len(opciones)
            elif t in ("espacio", "x", "X"):
                if not marcado[seleccion] and maximo is not None and sum(marcado) >= maximo:
                    aviso = "Como mucho puedes marcar %d" % maximo
                else:
                    marcado[seleccion] = not marcado[seleccion]
            elif t == "enter":
                if sum(marcado) < minimo:
                    aviso = "Tienes que marcar por lo menos %d" % minimo
                    continue
                return [o for o, m in zip(opciones, marcado) if m]
            elif t == "esc":
                return None
    finally:
        if not estaba_oculto:
            mostrar_cursor()


_TIPOS_CAMPO = {"texto": "texto", "numero": "numero", "número": "numero", "entero": "numero",
                "decimal": "decimal", "fraccion": "fraccion", "fracción": "fraccion",
                "contraseña": "contrasena", "contrasena": "contrasena"}


def _convertir_campo(texto, tipo):
    """Devuelve (valor, error)."""
    from .numeros import Fraccion, _leer_fraccion

    if tipo in ("texto", "contrasena"):
        return texto, None
    if not texto.strip():
        return None, "Este hay que rellenarlo"
    if tipo == "numero":
        try:
            return int(texto.strip()), None
        except ValueError:
            return None, "Tiene que ser un número entero"
    if tipo == "decimal":
        try:
            return float(texto.strip().replace(",", ".")), None
        except ValueError:
            return None, "Tiene que ser un número"
    try:
        return Fraccion(_leer_fraccion(texto)), None
    except (ValueError, ZeroDivisionError):
        return None, "Tiene que ser una fracción, como 3/4"


@_ventana
def formulario(campos, titulo="Formulario", x=None, y=None, color="cian", ancho_campo=20):
    """Pide varias cosas a la vez, cada una en su casilla, dentro de una caja.

        datos = pantalla.formulario(["Nombre", "Apellidos", "Ciudad"])
        print(datos["Nombre"])

        datos = pantalla.formulario({"Nombre": "texto", "Edad": "numero",
                                     "Altura": "decimal", "Clave": "contraseña"})

    Tipos que valen: "texto", "numero" (entero), "decimal", "fraccion" y "contraseña".
    Te mueves con ↑↓ (o Tab) y con Enter pasas a la siguiente; en la última, Enter acaba.
    Devuelve un diccionario con lo que se ha escrito en cada casilla, o None si pulsas Esc.
    """
    if isinstance(campos, dict):
        pares = [(str(k), str(v)) for k, v in campos.items()]
    else:
        pares = [(str(c), "texto") for c in campos]
    if not pares:
        raise ValueError("formulario: necesito al menos un campo")
    tipos = []
    for nombre, tipo in pares:
        canon = _TIPOS_CAMPO.get(tipo.strip().lower())
        if canon is None:
            raise ValueError("formulario: no conozco el tipo %r (del campo %r). Usa uno de estos: texto, "
                             "numero, decimal, fraccion, contraseña" % (tipo, nombre))
        tipos.append(canon)
    nombres = [n for n, _ in pares]
    ancho_campo = _entero(ancho_campo, "ancho_campo", "formulario")
    ancho_nombre = max(len(n) for n in nombres) + 1
    ancho_caja = max(ancho_nombre + ancho_campo + 6, len(str(titulo)) + 8)
    alto_caja = len(nombres) * 2 + 1
    ancho_p, alto_p = tamano()
    x, y = _centrar_caja(x, y, ancho_caja, alto_caja + 2)
    x, y = _posicion(x, y, "formulario")
    textos = [""] * len(nombres)
    actual = 0
    aviso = ""
    estaba_oculto = _estado["cursor_oculto"]
    ocultar_cursor()
    caja(x, y, ancho_caja, alto_caja, "redondo", color=color, titulo=titulo, relleno=True)
    pista = "↑↓ casilla · Enter siguiente · Esc salir"
    if y + alto_caja <= alto_p:
        escribir(pista[: max(0, ancho_p - x)], x, y + alto_caja, tenue=True)
    try:
        while True:
            for i, nombre in enumerate(nombres):
                fila = y + 1 + i * 2
                escribir((nombre + ":").ljust(ancho_nombre), x + 2, fila, negrita=i == actual)
                ver = "●" * len(textos[i]) if tipos[i] == "contrasena" else textos[i]
                if i == actual:
                    ver = (ver + "_")[-ancho_campo:]
                    escribir(ver.ljust(ancho_campo), x + 3 + ancho_nombre, fila, color="negro",
                             fondo="amarillo")
                else:
                    escribir(ver[:ancho_campo].ljust(ancho_campo), x + 3 + ancho_nombre, fila,
                             fondo="gris")
            if y + alto_caja + 1 <= alto_p:
                escribir(aviso.ljust(len(pista))[: max(0, ancho_p - x)], x, y + alto_caja + 1, color="rojo")
            t = tecla()
            aviso = ""
            if t == "esc":
                return None
            if t == "arriba":
                actual = (actual - 1) % len(nombres)
            elif t in ("abajo", "tab"):
                actual = (actual + 1) % len(nombres)
            elif t == "borrar":
                textos[actual] = textos[actual][:-1]
            elif t == "enter":
                if actual < len(nombres) - 1:
                    actual += 1
                    continue
                resultado = {}
                for i, nombre in enumerate(nombres):
                    valor, error = _convertir_campo(textos[i], tipos[i])
                    if error:
                        actual = i
                        aviso = "%s: %s" % (nombre, error)
                        break
                    resultado[nombre] = valor
                else:
                    return resultado
            elif t == "espacio":
                textos[actual] += " "
            elif len(t) == 1 and t.isprintable():
                textos[actual] += str(t)
    finally:
        if not estaba_oculto:
            mostrar_cursor()
