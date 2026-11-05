"""
Matrices: dibujarlas con sus corchetes y pedirlas con las flechas, casilla a casilla.
"""

from fractions import Fraction

from .colores import estilo as _estilo_ansi
from .dibujo import caja, rellenar
from .teclado import _ventana, tecla
from .terminal import (_entero, _estado, _fin_de_estilo, _mover, _posicion, _salida,
                       mostrar_cursor, ocultar_cursor, tamano)
from .texto import escribir


def _texto_numero(n):
    if n is None:
        return "■"
    if isinstance(n, Fraction):
        if n.denominator == 1:
            return str(n.numerator)
        return "%d/%d" % (n.numerator, n.denominator)
    if isinstance(n, float):
        if n.is_integer():
            return str(int(n))
        return ("%.4f" % n).rstrip("0").rstrip(".")
    return str(n)


def _comprobar_matriz(M, funcion):
    if not isinstance(M, (list, tuple)) or not M:
        raise TypeError("%s: una matriz es una lista de filas, por ejemplo [[1, 2], [3, 4]]" % funcion)
    filas = []
    for fila in M:
        if not isinstance(fila, (list, tuple)):
            fila = [fila]
        filas.append(list(fila))
    largo = len(filas[0])
    for i, fila in enumerate(filas):
        if len(fila) != largo or largo == 0:
            raise ValueError("%s: todas las filas tienen que tener los mismos números. La fila 1 tiene "
                             "%d y la fila %d tiene %d" % (funcion, largo, i + 1, len(fila)))
    return filas


def _lineas_matriz(M, nombre, det, ancho_celda=None):
    filas = len(M)
    textos = [[_texto_numero(n) for n in fila] for fila in M]
    if ancho_celda is None:
        ancho_celda = max(len(t) for fila in textos for t in fila) + 2
    columnas = len(M[0])
    hueco = " " * (columnas * ancho_celda)
    lineas = []
    for k in range(filas + 2):
        if det:
            izq, der = "│", "│"
        elif k == 0:
            izq, der = "┌", "┐"
        elif k == filas + 1:
            izq, der = "└", "┘"
        else:
            izq, der = "│", "│"
        if 1 <= k <= filas:
            dentro = "".join(t.center(ancho_celda) for t in textos[k - 1])
        else:
            dentro = hueco
        lineas.append([izq, dentro, der])
    delante = ""
    if nombre:
        delante = str(nombre) + " = "
    return lineas, delante, ancho_celda


def matriz(M, x=None, y=None, nombre=None, color=None, color_nombre="cian", det=False):
    """Dibuja una matriz con sus corchetes. Devuelve (ancho, alto) de lo que ocupa.

        A = [[1, 2], [3, 4]]
        pantalla.matriz(A)                          # donde esté el cursor, como un print
        pantalla.matriz(A, 5, 3, nombre="A")        # en la columna 5, fila 3, con "A ="
        pantalla.matriz(A, 5, 3, det=True)          # con barras, como un determinante

    Vale con números enteros, decimales y fracciones (from fractions import Fraction).
    """
    M = _comprobar_matriz(M, "matriz")
    lineas, delante, ancho_celda = _lineas_matriz(M, nombre, det)
    codigo = _estilo_ansi(color)
    codigo_nombre = _estilo_ansi(color_nombre, negrita=True)
    medio = 1 + (len(M) - 1) // 2
    textos = []
    for k, (izq, dentro, der) in enumerate(lineas):
        if delante:
            if k == medio:
                parte = codigo_nombre + delante + _fin_de_estilo()
            else:
                parte = " " * len(delante)
        else:
            parte = ""
        cuerpo = izq + dentro + der
        if codigo:
            cuerpo = codigo + cuerpo + _fin_de_estilo()
        textos.append(parte + cuerpo)
    ancho = len(delante) + len(lineas[0][1]) + 2
    alto = len(lineas)
    if x is None and y is None:
        _salida("\n".join(textos) + "\n")
    else:
        if x is None:
            x = 1
        if y is None:
            raise TypeError("matriz: si me das x también necesito y")
        x, y = _posicion(x, y, "matriz")
        _salida("".join(_mover(x, y + k) + t for k, t in enumerate(textos)))
    return ancho, alto


def _convertir(texto, fracciones):
    texto = texto.strip().replace(",", ".")
    if not texto:
        return None
    try:
        n = Fraction(texto)
    except (ValueError, ZeroDivisionError):
        return None
    if fracciones:
        return n
    if n.denominator == 1:
        return int(n)
    return float(n)


@_ventana
def pedir_matriz(nombre="A", filas=None, columnas=None, cuadrada=False, maximo=6,
                 fracciones=False, titulo=None, color="cian"):
    """Pide una matriz en una ventana: primero el tamaño con las flechas y luego cada número.

        A = pantalla.pedir_matriz()                         # eliges el tamaño tú
        B = pantalla.pedir_matriz("B", filas=2, columnas=3)  # tamaño fijo
        C = pantalla.pedir_matriz("C", cuadrada=True)         # filas = columnas

    Devuelve una lista de filas, por ejemplo [[1, 2], [3, 4]], o None si pulsas Esc.
    Se pueden escribir enteros, decimales (2.5 o 2,5) y fracciones (1/2).
    Con fracciones=True devuelve Fraction en vez de decimales.
    """
    maximo = _entero(maximo, "maximo", "pedir_matriz")
    nombre = str(nombre)
    if cuadrada and filas is not None:
        columnas = filas
    elif cuadrada and columnas is not None:
        filas = columnas
    f = filas or 2
    c = columnas or 2
    fija_f = filas is not None
    fija_c = columnas is not None

    ancho_p, alto_p = tamano()
    ancho_v = min(ancho_p, max(46, len(nombre) + 3 + maximo * 9 + 6))
    alto_v = min(alto_p, maximo + 10)
    vx = max(1, (ancho_p - ancho_v) // 2 + 1)
    vy = max(1, (alto_p - alto_v) // 2 + 1)
    if titulo is None:
        titulo = "Matriz " + nombre

    def fondo_ventana(instrucciones):
        caja(vx, vy, ancho_v, alto_v, "redondo", color=color, titulo=titulo, relleno=True)
        escribir(instrucciones, vx + 2, vy + 1, color="amarillo")

    def dibujar(M, sel, ancho_celda=None):
        lineas, delante, ancho_celda = _lineas_matriz(M, nombre, False, ancho_celda)
        w = len(delante) + len(lineas[0][1]) + 2
        mx = vx + max(1, (ancho_v - w) // 2)
        my = vy + 3
        medio = 1 + (len(M) - 1) // 2
        for k, (izq, dentro, der) in enumerate(lineas):
            if k == medio:
                escribir(delante, mx, my + k, color=color, negrita=True)
            escribir(izq, mx + len(delante), my + k)
            escribir(der, mx + len(delante) + len(dentro) + 1, my + k)
        for i, fila in enumerate(M):
            for j, n in enumerate(fila):
                t = _texto_numero(n).center(ancho_celda)
                cx = mx + len(delante) + 1 + j * ancho_celda
                if sel == (i, j):
                    escribir(t, cx, my + 1 + i, color="negro", fondo="amarillo", negrita=True)
                elif n is None:
                    escribir(t, cx, my + 1 + i, tenue=True)
                else:
                    escribir(t, cx, my + 1 + i)

    estaba_oculto = _estado["cursor_oculto"]
    ocultar_cursor()
    abajo = vy + alto_v - 2
    try:
        campo = 1 if fija_f else 0
        while not (fija_f and fija_c):
            fondo_ventana("Elige el tamaño de " + nombre + " y pulsa Enter")
            dibujar([[None] * c for _ in range(f)], None)
            if cuadrada:
                escribir(" Tamaño: %d x %d  ↑↓ " % (f, c), vx + 2, abajo - 1, color="negro", fondo="amarillo")
            else:
                a1 = {"color": "negro", "fondo": "amarillo"} if campo == 0 else {}
                a2 = {"color": "negro", "fondo": "amarillo"} if campo == 1 else {}
                escribir(" Filas: %d %s" % (f, "(fija)" if fija_f else "↑↓ "), vx + 2, abajo - 1, **a1)
                escribir(" Columnas: %d %s" % (c, "(fija)" if fija_c else "↑↓ "), vx + 20, abajo - 1, **a2)
            escribir("↑↓ cambiar · ←→ filas o columnas · Enter seguir · Esc salir"[: ancho_v - 4],
                     vx + 2, abajo, tenue=True)
            t = tecla()
            cambio = 0
            if t in ("arriba", "w", "W", "+"):
                cambio = 1
            elif t in ("abajo", "s", "S", "-"):
                cambio = -1
            elif t in ("izquierda", "derecha", "tab", "a", "A", "d", "D"):
                if not fija_f and not fija_c:
                    campo = 1 - campo
            elif t == "enter":
                break
            elif t == "esc":
                return None
            if cambio:
                if cuadrada:
                    f = max(1, min(maximo, f + cambio))
                    c = f
                elif campo == 0 and not fija_f:
                    f = max(1, min(maximo, f + cambio))
                elif campo == 1 and not fija_c:
                    c = max(1, min(maximo, c + cambio))

        M = [[None] * c for _ in range(f)]
        i = 0
        j = 0
        escrito = ""
        error = ""
        while True:
            ver = [fila[:] for fila in M]
            if escrito:
                ver[i][j] = escrito
            fondo_ventana("Escribe cada número y pulsa Enter")
            dibujar(ver, (i, j))
            escribir("%s%d%d = %s_" % (nombre[0].lower(), i + 1, j + 1, escrito), vx + 2, abajo - 2,
                     negrita=True)
            if error:
                escribir(error, vx + 2, abajo - 1, color="rojo")
            else:
                escribir("Vale: 3   -2   1/2   0.5", vx + 2, abajo - 1, tenue=True)
            escribir("Enter siguiente · flechas moverse · Esc salir", vx + 2, abajo, tenue=True)
            t = tecla()
            if t == "enter":
                if escrito:
                    valor = _convertir(escrito, fracciones)
                    if valor is None:
                        error = "Eso no es un número"
                        continue
                    M[i][j] = valor
                    escrito = ""
                elif M[i][j] is None:
                    error = "Escribe un número primero"
                    continue
                error = ""
                j = j + 1
                if j == c:
                    j = 0
                    i = i + 1
                if i == f:
                    falta = None
                    for a in range(f):
                        for b in range(c):
                            if M[a][b] is None and falta is None:
                                falta = (a, b)
                    if falta is None:
                        return M
                    i, j = falta
                    error = "Te falta este"
            elif t == "esc":
                return None
            elif t == "borrar":
                escrito = escrito[:-1]
            elif t in ("arriba", "abajo", "izquierda", "derecha", "tab"):
                escrito = ""
                if t == "arriba":
                    i = (i - 1) % f
                elif t == "abajo":
                    i = (i + 1) % f
                elif t == "izquierda":
                    j = (j - 1) % c
                else:
                    j = (j + 1) % c
            elif len(t) == 1 and t in "0123456789-/.," and len(escrito) < 9:
                escrito = escrito + t
    finally:
        rellenar(vx, vy, ancho_v, alto_v)
        if not estaba_oculto:
            mostrar_cursor()
