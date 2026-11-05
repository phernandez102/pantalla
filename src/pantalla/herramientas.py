"""
Herramientas para cuando estás programando: ver las posiciones de la pantalla.
"""

from .colores import estilo as _estilo_ansi
from .teclado import _activar_modo_teclas, _desactivar_modo_teclas, _modo, tecla
from .terminal import (CSI, _estado, _fin_de_estilo, _mover, _salida, centro, limpiar,
                       mostrar_cursor, ocultar_cursor, tamano)
from .texto import escribir


def regla(color="gris"):
    """Dibuja los números de las columnas arriba y los de las filas a la izquierda.

    Sirve para saber en qué x e y está cada cosa mientras diseñas una pantalla.

        pantalla.limpiar()
        pantalla.regla()
        pantalla.caja(10, 5, 20, 6)   # ¿la caja empieza donde creías?
    """
    ancho_p, alto_p = tamano()
    arriba = ["·"] * ancho_p
    for x in range(5, ancho_p + 1, 5):
        numero = str(x)
        for k, cifra in enumerate(numero):
            sitio = x - len(numero) + k
            if sitio >= 0:
                arriba[sitio] = cifra
    codigo = _estilo_ansi(color)
    trozos = [_mover(1, 1) + codigo + "".join(arriba) + _fin_de_estilo()]
    for y in range(2, alto_p + 1):
        trozos.append(_mover(1, y) + codigo + str(y).rjust(2) + _fin_de_estilo())
    _salida("".join(trozos))


def depurar():
    """Abre una herramienta para ver las posiciones de la pantalla.

    Mueves una cruz con las flechas y te dice en qué x e y está, cuánto mide
    la pantalla y qué tecla has pulsado. Con Enter dejas una marca, para
    apuntar varios sitios. Al salir (Esc) todo vuelve a estar como antes.

        pantalla.depurar()

    También se abre desde la terminal con:  python -m pantalla depurar
    """
    ya_aparte = _estado["pantalla_aparte"]
    ya_teclas = _modo["original"] is not None
    estaba_oculto = _estado["cursor_oculto"]
    if not ya_aparte:
        _salida(CSI + "?1049h")
    ocultar_cursor()
    _activar_modo_teclas()
    x, y = centro()
    ultima = "-"
    con_regla = True
    marcas = []
    try:
        while True:
            ancho_p, alto_p = tamano()
            x = max(1, min(x, ancho_p))
            y = max(1, min(y, alto_p))
            limpiar()
            if con_regla:
                regla()
            linea_h = "".join("─" if i != x else "┼" for i in range(1, ancho_p + 1))
            escribir(linea_h[3:], 4, y, color="gris", tenue=True)
            for fila in range(2, alto_p + 1):
                if fila != y:
                    escribir("│", x, fila, color="gris", tenue=True)
            for mx, my in marcas:
                if 1 <= mx <= ancho_p and 1 <= my <= alto_p:
                    escribir("●", mx, my, color="rojo claro", negrita=True)
            escribir("╋", x, y, color="amarillo", negrita=True)

            info = [
                "x = %d    y = %d" % (x, y),
                "pantalla: %d x %d" % (ancho_p, alto_p),
                "última tecla: %r" % ultima,
                "",
                "pantalla.gotoxy(%d, %d)" % (x, y),
            ]
            if marcas:
                info.append("marcas: " + " ".join("(%d,%d)" % m for m in marcas[-3:]))
            info += ["", "flechas: mover   Enter: marcar", "b: borrar marcas   r: regla", "c: al centro   Esc: salir"]
            ancho_info = max(len(l) for l in info) + 4
            alto_info = len(info) + 2
            ix = ancho_p - ancho_info
            iy = 3
            if x >= ix - 1 and y <= iy + alto_info:
                iy = max(3, alto_p - alto_info)
            from .dibujo import caja

            caja(max(1, ix), iy, ancho_info, alto_info, "redondo", color="cian", titulo="depurar",
                 relleno=True)
            for k, l in enumerate(info):
                if k == 0:
                    escribir(l, max(1, ix) + 2, iy + 1 + k, color="amarillo", negrita=True)
                elif l.startswith("pantalla."):
                    escribir(l, max(1, ix) + 2, iy + 1 + k, color="verde claro")
                else:
                    escribir(l, max(1, ix) + 2, iy + 1 + k, tenue=k >= len(info) - 3)

            t = tecla()
            ultima = t
            if t == "arriba":
                y = y - 1
            elif t == "abajo":
                y = y + 1
            elif t == "izquierda":
                x = x - 1
            elif t == "derecha":
                x = x + 1
            elif t in ("enter", "espacio"):
                if (x, y) in marcas:
                    marcas.remove((x, y))
                else:
                    marcas.append((x, y))
            elif t in ("b", "B"):
                marcas = []
            elif t in ("r", "R"):
                con_regla = not con_regla
            elif t in ("c", "C"):
                x, y = centro()
            elif t in ("esc", "q", "Q"):
                return marcas
    finally:
        if not ya_teclas:
            _desactivar_modo_teclas()
        if not ya_aparte:
            _salida(CSI + "?1049l")
        if not estaba_oculto:
            mostrar_cursor()
