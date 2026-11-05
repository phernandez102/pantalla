"""
Gráficas en la terminal: de funciones (y = x²), de barras y mini gráficas de una línea.

    pantalla.grafica(lambda x: x * x, -5, 5)
    pantalla.barras({"Ana": 8.5, "Luis": 6, "Marta": 9.75})
    print(pantalla.minigrafica([1, 5, 2, 8, 3]))     # ▁▅▂█▃
"""

import math
from fractions import Fraction

from .colores import estilo as _estilo_ansi
from .numeros import _sacar
from .terminal import _entero, _fin_de_estilo


_COLORES = ["cian", "amarillo", "verde claro", "morado claro", "rojo claro", "azul claro"]


def _texto_corto(n):
    if isinstance(n, float):
        if n.is_integer() and abs(n) < 1e9:
            return str(int(n))
        if abs(n) >= 1e5 or (abs(n) < 1e-3 and n != 0):
            return "%.2g" % n
        return ("%.2f" % n).rstrip("0").rstrip(".")
    return str(n)


def _valor(funcion, x):
    try:
        y = funcion(x)
    except (ZeroDivisionError, ValueError, OverflowError, TypeError):
        return None
    if isinstance(y, complex) or isinstance(y, bool):
        return None
    try:
        y = float(y)
    except (TypeError, ValueError, OverflowError):
        return None
    if math.isnan(y) or math.isinf(y):
        return None
    return y


def _rango_y(valores, minimo, maximo):
    buenos = sorted(v for serie in valores for v in serie if v is not None)
    if not buenos:
        bajo, alto = -1.0, 1.0
    else:
        bajo, alto = buenos[0], buenos[-1]
        # si hay picos enormes (como en 1/x cerca de 0) no dejamos que aplasten todo lo demas
        k = max(1, len(buenos) // 20)
        if len(buenos) > 10:
            p_bajo, p_alto = buenos[k], buenos[-1 - k]
            hueco = max(p_alto - p_bajo, 1e-9)
            if alto - bajo > 10 * hueco:
                bajo, alto = p_bajo - hueco * 0.5, p_alto + hueco * 0.5
        # si casi toca el 0 (como x² que da 0.02), que llegue al 0 y se vea el eje
        if 0 < bajo < (alto - bajo) * 0.1:
            bajo = 0.0
        elif -(alto - bajo) * 0.1 < alto < 0:
            alto = 0.0
    # que salga -4 y no -3.99 cuando le falta poquito para un numero redondo
    margen = (alto - bajo) * 0.01
    if abs(bajo - round(bajo)) < margen:
        bajo = float(round(bajo))
    if abs(alto - round(alto)) < margen:
        alto = float(round(alto))
    if minimo is not None:
        bajo = float(minimo)
    if maximo is not None:
        alto = float(maximo)
    if alto <= bajo:
        bajo, alto = bajo - 1, bajo + 1
    return bajo, alto


def grafica(funcion, desde=-10, hasta=10, x=None, y=None, ancho=50, alto=15, color=None,
            minimo=None, maximo=None, caracter="•", ejes=True):
    """Dibuja la gráfica de una función, con sus ejes.

        pantalla.grafica(lambda x: x * x, -5, 5)              # y = x² entre x = -5 y x = 5
        pantalla.grafica(math.sin, 0, 2 * math.pi, 3, 2)      # en la columna 3, fila 2

        def f(x):
            return 2 * x + 1
        pantalla.grafica(f)

        pantalla.grafica([math.sin, math.cos], -6, 6)          # varias, cada una de un color
        pantalla.grafica([3, 5, 2, 8, 6, 9])                   # una lista de números: los une

    - minimo, maximo: hasta dónde llega el eje y (si no, se ajusta solo).
    - ancho, alto: lo que ocupa en la pantalla, contando los números de los lados.
    Los puntos donde la función no existe (como 1/x en x = 0) se dejan en blanco.
    Sin x ni y, se dibuja donde esté el cursor (como un print).
    """
    ancho = _entero(ancho, "ancho", "grafica")
    alto = _entero(alto, "alto", "grafica")
    if ancho < 12 or alto < 4:
        raise ValueError("grafica: es muy pequeña. Ponle por lo menos ancho=12 y alto=4")

    if isinstance(funcion, (list, tuple)) and funcion and all(callable(f) for f in funcion):
        funciones = list(funcion)
        datos = None
    elif callable(funcion):
        funciones = [funcion]
        datos = None
    elif isinstance(funcion, (list, tuple)) and funcion:
        datos = []
        for v in funcion:
            if isinstance(v, bool) or not isinstance(v, (int, float, Fraction)):
                raise TypeError("grafica: la lista tiene que ser de números, y hay un %r" % (v,))
            datos.append(float(v))
        funciones = []
    else:
        raise TypeError("grafica: dame una función (por ejemplo lambda x: x * x) o una lista de números")

    if datos is not None:
        desde, hasta = 0, len(datos) - 1
    desde, hasta = float(desde), float(hasta)
    if hasta <= desde:
        raise ValueError("grafica: 'hasta' (%s) tiene que ser mayor que 'desde' (%s)"
                         % (_texto_corto(hasta), _texto_corto(desde)))

    # ponemos de prueba los numeros de la izquierda para saber cuanto sitio dejar
    alto_dibujo = alto - 1
    series = []
    ancho_numeros = 1
    for _ in range(2):
        ancho_dibujo = ancho - ancho_numeros - 1
        xs = [desde + (hasta - desde) * i / max(1, ancho_dibujo - 1) for i in range(ancho_dibujo)]
        if datos is not None:
            serie = []
            for xv in xs:
                pos = xv
                i = int(math.floor(pos))
                t = pos - i
                if i >= len(datos) - 1:
                    serie.append(datos[-1])
                else:
                    serie.append(datos[i] * (1 - t) + datos[i + 1] * t)
            series = [serie]
        else:
            series = [[_valor(f, xv) for xv in xs] for f in funciones]
        bajo, arriba = _rango_y([datos] if datos is not None else series, minimo, maximo)
        etiquetas = [_texto_corto(arriba), _texto_corto(bajo)]
        if bajo < 0 < arriba:
            etiquetas.append("0")
        nuevo = max(len(e) for e in etiquetas)
        if nuevo == ancho_numeros:
            break
        ancho_numeros = nuevo

    def fila_de(v):
        return int(round((arriba - v) / (arriba - bajo) * (alto_dibujo - 1)))

    celdas = [[(" ", None)] * ancho_dibujo for _ in range(alto_dibujo)]
    gris = _estilo_ansi("gris")
    fila_cero = fila_de(0) if bajo <= 0 <= arriba else None
    col_cero = None
    if desde <= 0 <= hasta and datos is None:
        col_cero = int(round(-desde / (hasta - desde) * (ancho_dibujo - 1)))
    if ejes:
        if fila_cero is not None:
            celdas[fila_cero] = [("─", gris)] * ancho_dibujo
        if col_cero is not None:
            for f in range(alto_dibujo):
                celdas[f][col_cero] = ("┼" if f == fila_cero else "│", gris)

    for s, serie in enumerate(series):
        cod = _estilo_ansi(color if (color and len(series) == 1) else _COLORES[s % len(_COLORES)])
        anterior = None
        for c, v in enumerate(serie):
            if v is None or not (bajo - 1e-9 <= v <= arriba + 1e-9):
                anterior = None
                continue
            f = fila_de(v)
            celdas[f][c] = (caracter, cod)
            # si de una columna a la siguiente da un salto, rellenamos para que se vea seguida
            if anterior is not None and abs(f - anterior) > 1:
                paso = 1 if f > anterior else -1
                mitad = (anterior + f) // 2
                for g in range(anterior + paso, f, paso):
                    columna = c - 1 if (g - mitad) * paso <= 0 else c
                    celdas[g][columna] = (caracter, cod)
            anterior = f

    fin = _fin_de_estilo()
    lineas = []
    for f in range(alto_dibujo):
        if f == 0:
            numero = _texto_corto(arriba)
        elif f == alto_dibujo - 1:
            numero = _texto_corto(bajo)
        elif f == fila_cero:
            numero = "0"
        else:
            numero = ""
        partes = [gris + numero.rjust(ancho_numeros) + " " + fin]
        for ch, cod in celdas[f]:
            partes.append(cod + ch + fin if cod else ch)
        lineas.append("".join(partes).rstrip())
    izq, der = _texto_corto(desde), _texto_corto(hasta)
    abajo = " " * (ancho_numeros + 1) + izq
    medio = ""
    if col_cero is not None and 0 not in (desde, hasta):
        pos_cero = ancho_numeros + 1 + col_cero
        if pos_cero > len(abajo) + 1 and pos_cero < ancho - len(der) - 1:
            medio = " " * (pos_cero - len(abajo)) + "0"
    abajo = abajo + medio
    abajo = abajo + der.rjust(ancho - len(abajo))
    lineas.append(gris + abajo + fin)
    _sacar(lineas, x, y, "grafica")
    return ancho, alto


_OCTAVOS = " ▏▎▍▌▋▊▉█"


def barras(datos, x=None, y=None, ancho=40, color="verde", colores=None, valores=True, maximo=None):
    """Dibuja una gráfica de barras tumbadas, cada una con su nombre.

        pantalla.barras({"Ana": 8.5, "Luis": 6, "Marta": 9.75})
        pantalla.barras([("Lunes", 3), ("Martes", 7)], 5, 3, color="cian")
        pantalla.barras([4, 8, 2])                         # sin nombres: 1, 2, 3
        pantalla.barras(notas, colores=["rojo", "amarillo", "verde"])   # un color para cada una

    - ancho: lo que ocupa todo, contando los nombres y los números.
    - maximo: el número que llena la barra entera (si no, el más grande de todos).
    - valores=False: sin el número al final de cada barra.
    Sin x ni y, se dibuja donde esté el cursor (como un print).
    """
    if isinstance(datos, dict):
        pares = list(datos.items())
    else:
        pares = []
        for i, d in enumerate(datos):
            if isinstance(d, (list, tuple)) and len(d) == 2:
                pares.append((d[0], d[1]))
            else:
                pares.append((i + 1, d))
    if not pares:
        raise ValueError("barras: no hay datos que dibujar")
    for nombre, v in pares:
        if isinstance(v, bool) or not isinstance(v, (int, float, Fraction)):
            raise TypeError("barras: el valor de %r tiene que ser un número, y es %r" % (nombre, v))
        if v < 0:
            raise ValueError("barras: el valor de %r es negativo (%s) y las barras solo van de 0 para arriba"
                             % (nombre, v))
    ancho = _entero(ancho, "ancho", "barras")
    nombres = [str(n) for n, _ in pares]
    numeros = [_texto_corto(float(v)) if not isinstance(v, int) else str(v) for _, v in pares]
    ancho_nombre = max(len(n) for n in nombres)
    ancho_numero = max(len(n) for n in numeros) + 1 if valores else 0
    sitio = ancho - ancho_nombre - 1 - ancho_numero
    if sitio < 3:
        raise ValueError("barras: no caben con ancho=%d. Ponle un ancho más grande" % ancho)
    tope = float(maximo) if maximo is not None else max(float(v) for _, v in pares)
    fin = _fin_de_estilo()
    lineas = []
    for i, (nombre, v) in enumerate(pares):
        cod = _estilo_ansi(colores[i % len(colores)] if colores else color)
        octavos = 0 if tope <= 0 else int(round(min(float(v), tope) / tope * sitio * 8))
        barra = "█" * (octavos // 8) + (_OCTAVOS[octavos % 8] if octavos % 8 else "")
        linea = nombres[i].ljust(ancho_nombre) + " " + cod + barra + fin
        if valores:
            linea += " " * (sitio - len(barra) + 1) + _estilo_ansi("gris") + numeros[i].rjust(ancho_numero - 1) + fin
        lineas.append(linea)
    _sacar(lineas, x, y, "barras")
    return ancho, len(lineas)


_ESCALONES = "▁▂▃▄▅▆▇█"


def minigrafica(valores, minimo=None, maximo=None):
    """Devuelve una gráfica pequeñita de una línea, para meterla en un print.

        print("Temperaturas:", pantalla.minigrafica([12, 15, 19, 22, 18, 14]))
        # Temperaturas: ▁▃▆█▅▂
    """
    numeros = []
    for v in valores:
        if isinstance(v, bool) or not isinstance(v, (int, float, Fraction)):
            raise TypeError("minigrafica: la lista tiene que ser de números, y hay un %r" % (v,))
        numeros.append(float(v))
    if not numeros:
        return ""
    bajo = min(numeros) if minimo is None else float(minimo)
    alto = max(numeros) if maximo is None else float(maximo)
    if alto <= bajo:
        return _ESCALONES[3] * len(numeros)
    texto = ""
    for v in numeros:
        v = min(max(v, bajo), alto)
        texto += _ESCALONES[int(round((v - bajo) / (alto - bajo) * (len(_ESCALONES) - 1)))]
    return texto
