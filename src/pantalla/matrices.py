"""
Matrices: dibujarlas con sus corchetes, pedirlas con las flechas casilla a casilla
y hacer cuentas con ellas (sumar, multiplicar, determinante, inversa, Gauss...).

Las cuentas se hacen con fracciones, así que no salen cosas como 0.30000000000000004:
la inversa de [[2, 1], [1, 1]] da [[1, -1], [-1, 2]] justos, y si sale algo con
decimales sale como fracción (1/3). Si alguno de los números que das tiene
decimales (2.5), las cuentas se hacen con decimales.
"""

from fractions import Fraction

from .colores import estilo as _estilo_ansi
from .dibujo import caja, rellenar
from .numeros import _a_numero, _bonito
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


def _lineas_matriz(M, nombre, det, ancho_celda=None, ampliada=False):
    filas = len(M)
    textos = [[_texto_numero(n) for n in fila] for fila in M]
    if ancho_celda is None:
        ancho_celda = max(len(t) for fila in textos for t in fila) + 2
    columnas = len(M[0])
    ampliada = ampliada and columnas > 1
    hueco = " " * (columnas * ancho_celda + (1 if ampliada else 0))
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
            celdas = [t.center(ancho_celda) for t in textos[k - 1]]
            if ampliada:
                celdas.insert(columnas - 1, "│")
            dentro = "".join(celdas)
        elif ampliada:
            dentro = " " * ((columnas - 1) * ancho_celda) + "│" + " " * ancho_celda
        else:
            dentro = hueco
        lineas.append([izq, dentro, der])
    delante = ""
    if nombre:
        delante = str(nombre) + " = "
    return lineas, delante, ancho_celda


def matriz(M, x=None, y=None, nombre=None, color=None, color_nombre="cian", det=False,
           ampliada=False):
    """Dibuja una matriz con sus corchetes. Devuelve (ancho, alto) de lo que ocupa.

        A = [[1, 2], [3, 4]]
        pantalla.matriz(A)                          # donde esté el cursor, como un print
        pantalla.matriz(A, 5, 3, nombre="A")        # en la columna 5, fila 3, con "A ="
        pantalla.matriz(A, 5, 3, det=True)          # con barras, como un determinante
        pantalla.matriz([[1, 2, 5], [3, 4, 6]], ampliada=True)   # con una raya antes de la última columna

    Vale con números enteros, decimales y fracciones (pantalla.fraccion("1/2")).
    """
    M = _comprobar_matriz(M, "matriz")
    lineas, delante, ancho_celda = _lineas_matriz(M, nombre, det, ampliada=ampliada)
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


# --- cuentas con matrices -------------------------------------------------

def _tam(M):
    return "%dx%d" % (len(M), len(M[0]))


def _es_numero(valor):
    return isinstance(valor, (int, float, Fraction)) and not isinstance(valor, bool)


def _numeros_matriz(M, funcion):
    filas = _comprobar_matriz(M, funcion)
    return [[_a_numero(n, funcion, "el número de la fila %d, columna %d" % (i + 1, j + 1))
             for j, n in enumerate(fila)] for i, fila in enumerate(filas)]


def _exactas(funcion, *matrices):
    """Todas con fracciones o, si alguna tiene decimales, todas con decimales."""
    matrices = [_numeros_matriz(M, funcion) for M in matrices]
    decimales = any(isinstance(n, float) for M in matrices for f in M for n in f)
    tipo = float if decimales else Fraction
    return [[[tipo(n) for n in f] for f in M] for M in matrices]


def _cero(n):
    return abs(n) < 1e-10 if isinstance(n, float) else n == 0


def _devolver(M):
    return [[_bonito(n) for n in f] for f in M]


def _cuadrada(M, funcion):
    if len(M) != len(M[0]):
        raise ValueError("%s: solo se puede con matrices cuadradas (con tantas filas como columnas), "
                         "y esta es de %s" % (funcion, _tam(M)))


def _mismo_tamano(A, B, funcion, para):
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        raise ValueError("%s: la primera matriz es de %s y la segunda de %s. Para %s tienen que ser "
                         "del mismo tamaño" % (funcion, _tam(A), _tam(B), para))


def sumar_matrices(A, B):
    """Suma dos matrices del mismo tamaño, número a número.

        C = pantalla.sumar_matrices([[1, 2], [3, 4]], [[10, 20], [30, 40]])
        # [[11, 22], [33, 44]]
    """
    A, B = _exactas("sumar_matrices", A, B)
    _mismo_tamano(A, B, "sumar_matrices", "sumarlas")
    return _devolver([[a + b for a, b in zip(fa, fb)] for fa, fb in zip(A, B)])


def restar_matrices(A, B):
    """Resta dos matrices del mismo tamaño (A - B), número a número.

        C = pantalla.restar_matrices([[5, 5], [5, 5]], [[1, 2], [3, 4]])
        # [[4, 3], [2, 1]]
    """
    A, B = _exactas("restar_matrices", A, B)
    _mismo_tamano(A, B, "restar_matrices", "restarlas")
    return _devolver([[a - b for a, b in zip(fa, fb)] for fa, fb in zip(A, B)])


def multiplicar_matrices(A, B):
    """Multiplica dos matrices (A · B), o una matriz por un número.

        C = pantalla.multiplicar_matrices([[1, 2], [3, 4]], [[5], [6]])   # [[17], [39]]
        D = pantalla.multiplicar_matrices(3, [[1, 2], [3, 4]])            # [[3, 6], [9, 12]]

    Para multiplicar dos matrices, las columnas de la primera tienen que ser
    tantas como las filas de la segunda. Ojo: A · B no suele dar lo mismo que B · A.
    """
    if _es_numero(A) or _es_numero(B):
        k, M = (A, B) if _es_numero(A) else (B, A)
        M, = _exactas("multiplicar_matrices", M)
        k = float(k) if isinstance(M[0][0], float) or isinstance(k, float) else Fraction(k)
        return _devolver([[k * n for n in f] for f in M])
    A, B = _exactas("multiplicar_matrices", A, B)
    if len(A[0]) != len(B):
        raise ValueError("multiplicar_matrices: la primera matriz es de %s y la segunda de %s. Para "
                         "multiplicarlas, las columnas de la primera (%d) tienen que ser tantas como las "
                         "filas de la segunda (%d)" % (_tam(A), _tam(B), len(A[0]), len(B)))
    return _devolver(_por(A, B))


def _por(A, B):
    return [[sum((A[i][k] * B[k][j] for k in range(len(B))), A[0][0] * 0)
             for j in range(len(B[0]))] for i in range(len(A))]


def transpuesta(A):
    """Cambia las filas por las columnas.

        pantalla.transpuesta([[1, 2, 3], [4, 5, 6]])    # [[1, 4], [2, 5], [3, 6]]
    """
    M, = _exactas("transpuesta", A)
    return _devolver([list(col) for col in zip(*M)])


def identidad(n):
    """La matriz identidad de n x n: unos en la diagonal y ceros en el resto.

        pantalla.identidad(3)     # [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    """
    n = _entero(n, "n", "identidad")
    if n < 1:
        raise ValueError("identidad: n tiene que ser 1 o más, y me has dado %d" % n)
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def traza(A):
    """Suma los números de la diagonal (solo matrices cuadradas).

        pantalla.traza([[1, 2], [3, 4]])     # 5
    """
    M, = _exactas("traza", A)
    _cuadrada(M, "traza")
    return _bonito(sum((M[i][i] for i in range(len(M))), M[0][0] * 0))


def _pivote(M, fila, col):
    candidatas = [r for r in range(fila, len(M)) if not _cero(M[r][col])]
    if not candidatas:
        return None
    if isinstance(M[fila][col], float):
        # con decimales se coge el mas grande, que si no se acumulan errores
        return max(candidatas, key=lambda r: abs(M[r][col]))
    return candidatas[0]


def determinante(A):
    """El determinante de una matriz cuadrada.

        pantalla.determinante([[1, 2], [3, 4]])                    # -2
        pantalla.determinante([[2, 0, 1], [1, 3, 2], [1, 1, 2]])   # 6

    Si es 0, la matriz no tiene inversa.
    """
    M, = _exactas("determinante", A)
    _cuadrada(M, "determinante")
    n = len(M)
    det = M[0][0] * 0 + 1
    for c in range(n):
        p = _pivote(M, c, c)
        if p is None:
            return _bonito(det * 0)
        if p != c:
            M[c], M[p] = M[p], M[c]
            det = -det
        det = det * M[c][c]
        for r in range(c + 1, n):
            k = M[r][c] / M[c][c]
            M[r] = [a - k * b for a, b in zip(M[r], M[c])]
    return _bonito(det)


def _texto_factor(k):
    t = _texto_numero(_bonito(k))
    return "(%s)" % t if "/" in t or "." in t else t


def _gauss(M, reducida, columnas=None):
    """Hace Gauss sobre M (la cambia). Devuelve la lista de pasos: (qué se ha hecho, cómo queda)."""
    pasos = []
    filas = len(M)
    columnas = len(M[0]) if columnas is None else columnas
    fila = 0
    for col in range(columnas):
        if fila >= filas:
            break
        p = _pivote(M, fila, col)
        if p is None:
            continue
        if p != fila:
            M[fila], M[p] = M[p], M[fila]
            pasos.append(("F%d ↔ F%d" % (fila + 1, p + 1), [f[:] for f in M]))
        if reducida and M[fila][col] != 1:
            k = 1 / M[fila][col]
            M[fila] = [k * n for n in M[fila]]
            pasos.append(("F%d → %s·F%d" % (fila + 1, _texto_factor(k), fila + 1), [f[:] for f in M]))
        hechas = []
        for r in range(filas):
            if r == fila or (r < fila and not reducida) or _cero(M[r][col]):
                continue
            k = M[r][col] / M[fila][col]
            M[r] = [a - k * b for a, b in zip(M[r], M[fila])]
            M[r][col] = M[r][col] * 0
            signo = "-" if k > 0 else "+"
            factor = "" if abs(k) == 1 else _texto_factor(abs(k)) + "·"
            hechas.append("F%d → F%d %s %sF%d" % (r + 1, r + 1, signo, factor, fila + 1))
        if hechas:
            pasos.append(("\n".join(hechas), [f[:] for f in M]))
        fila += 1
    return pasos


def _rango_de(M):
    return sum(1 for f in M if any(not _cero(n) for n in f))


def _ver_pasos(inicio, pasos, ampliada=False):
    todas = []
    cod = _estilo_ansi("amarillo")

    def dibujo(M, texto):
        lineas, _, _ = _lineas_matriz(_devolver(M), None, False, ampliada=ampliada)
        # si en un paso se cambian varias filas, cada cambio va en su linea
        textos = texto.split("\n") if texto else []
        primera = max(0, 1 + (len(M) - 1) // 2 - (len(textos) - 1) // 2)
        for k, (izq, dentro, der) in enumerate(lineas):
            linea = izq + dentro + der
            if 0 <= k - primera < len(textos):
                linea += "   " + cod + textos[k - primera] + _fin_de_estilo()
            todas.append(linea)

    dibujo(inicio, "")
    for texto, M in pasos:
        dibujo(M, texto)
    _salida("\n".join(todas) + "\n")


def escalonar(A, pasos=False, reducida=False, ampliada=False):
    """Hace el método de Gauss: deja ceros por debajo de la diagonal.

        E = pantalla.escalonar([[1, 2, 3], [4, 5, 6], [7, 8, 10]])
        pantalla.escalonar(A, pasos=True)        # enseña cada paso: F2 → F2 - 4·F1 ...
        pantalla.escalonar(A, reducida=True)     # Gauss-Jordan: unos en la diagonal y ceros arriba también
        pantalla.escalonar(Ab, pasos=True, ampliada=True)   # con la raya de la matriz ampliada

    Devuelve la matriz escalonada.
    """
    M, = _exactas("escalonar", A)
    inicio = [f[:] for f in M]
    lista = _gauss(M, reducida)
    if pasos:
        _ver_pasos(inicio, lista, ampliada)
    return _devolver(M)


def rango(A):
    """El rango de una matriz: cuántas filas quedan que no son todo ceros al escalonarla.

        pantalla.rango([[1, 2], [2, 4]])     # 1  (la segunda fila es el doble de la primera)
    """
    M, = _exactas("rango", A)
    _gauss(M, False)
    return _rango_de(M)


def inversa(A):
    """La matriz inversa (la que multiplicada por A da la identidad).

        pantalla.inversa([[2, 1], [1, 1]])     # [[1, -1], [-1, 2]]
        pantalla.inversa([[1, 2], [3, 4]])     # [[-2, 1], [3/2, -1/2]]

    Solo existe si la matriz es cuadrada y su determinante no es 0.
    """
    M, = _exactas("inversa", A)
    _cuadrada(M, "inversa")
    n = len(M)
    uno = M[0][0] * 0 + 1
    grande = [f + [uno if i == j else uno * 0 for j in range(n)] for i, f in enumerate(M)]
    _gauss(grande, True, columnas=n)
    if _rango_de([f[:n] for f in grande]) < n:
        raise ValueError("inversa: esta matriz no tiene inversa porque su determinante es 0")
    return _devolver([f[n:] for f in grande])


def potencia_matriz(A, n):
    """Multiplica una matriz cuadrada por sí misma n veces (A elevado a n).

        pantalla.potencia_matriz([[1, 1], [1, 0]], 5)    # [[8, 5], [5, 3]]
        pantalla.potencia_matriz(A, 0)                  # la identidad
        pantalla.potencia_matriz(A, -1)                 # la inversa
    """
    M, = _exactas("potencia_matriz", A)
    _cuadrada(M, "potencia_matriz")
    n = _entero(n, "n", "potencia_matriz")
    if n < 0:
        M, = _exactas("potencia_matriz", inversa(M))
        n = -n
    uno = M[0][0] * 0 + 1
    resultado = [[uno if i == j else uno * 0 for j in range(len(M))] for i in range(len(M))]
    base = M
    while n:
        if n % 2:
            resultado = _por(resultado, base)
        base = _por(base, base)
        n //= 2
    return _devolver(resultado)


def _ampliada(A, b, funcion):
    if b is None:
        M, = _exactas(funcion, A)
        if len(M[0]) < 2:
            raise ValueError("%s: si no me das b, la matriz tiene que llevar los resultados en la última "
                             "columna (la matriz ampliada)" % funcion)
        return M
    if _es_numero(b):
        b = [b]
    M, B = _exactas(funcion, A, b)
    if len(B) == 1 and len(B[0]) == len(M) and len(M) > 1:
        B = [[n] for n in B[0]]
    if len(B) != len(M) or len(B[0]) != 1:
        raise ValueError("%s: A tiene %d filas (ecuaciones), así que b tiene que tener %d números, uno por "
                         "ecuación" % (funcion, len(M), len(M)))
    return [f + fb for f, fb in zip(M, B)]


def _tipo_sistema(M):
    incognitas = len(M[0]) - 1
    escalonada = [f[:] for f in M]
    _gauss(escalonada, False)
    rango_a = _rango_de([f[:-1] for f in escalonada])
    rango_ab = _rango_de(escalonada)
    if rango_a != rango_ab:
        return "incompatible"
    if rango_a == incognitas:
        return "compatible determinado"
    return "compatible indeterminado"


def clasificar_sistema(A, b=None):
    """Dice cómo es un sistema de ecuaciones (por el teorema de Rouché-Frobenius).

        # x + y = 3
        # x - y = 1
        pantalla.clasificar_sistema([[1, 1], [1, -1]], [3, 1])    # "compatible determinado"

    Devuelve "compatible determinado" (una solución), "compatible indeterminado"
    (infinitas soluciones) o "incompatible" (ninguna). Sin b, la última columna
    de A son los resultados (la matriz ampliada).
    """
    return _tipo_sistema(_ampliada(A, b, "clasificar_sistema"))


def resolver_sistema(A, b=None, pasos=False):
    """Resuelve un sistema de ecuaciones lineales por Gauss.

        # 2x + y = 5
        #  x - y = 1
        x, y = pantalla.resolver_sistema([[2, 1], [1, -1]], [5, 1])     # 2, 1
        pantalla.resolver_sistema([[2, 1, 5], [1, -1, 1]], pasos=True)  # con la ampliada, paso a paso

    Devuelve la lista con el valor de cada incógnita. Si el sistema no tiene una
    única solución devuelve None (pantalla.clasificar_sistema() te dice por qué).
    Con pasos=True enseña cada paso de Gauss y la solución.
    """
    M = _ampliada(A, b, "resolver_sistema")
    tipo = _tipo_sistema(M)
    inicio = [f[:] for f in M]
    lista = _gauss(M, True, columnas=len(M[0]) - 1)
    incognitas = len(M[0]) - 1
    solucion = None
    if tipo == "compatible determinado":
        solucion = [_bonito(M[i][-1]) for i in range(incognitas)]
    if pasos:
        _ver_pasos(inicio, lista, ampliada=True)
        if solucion is None:
            explica = {"incompatible": "no tiene solución",
                       "compatible indeterminado": "tiene infinitas soluciones"}[tipo]
            texto = "Sistema %s: %s" % (tipo, explica)
        else:
            nombres = "xyz" if incognitas <= 3 else None
            partes = ["%s = %s" % (nombres[i] if nombres else "x%d" % (i + 1), _texto_numero(v))
                      for i, v in enumerate(solucion)]
            texto = "Solución: " + ",  ".join(partes)
        color = "verde" if solucion is not None else "rojo"
        _salida(_estilo_ansi(color, negrita=True) + texto + _fin_de_estilo() + "\n")
    return solucion
