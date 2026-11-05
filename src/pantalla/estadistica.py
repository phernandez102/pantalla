"""
Estadística: media, mediana, moda, desviación, cuartiles, la tabla de frecuencias y el histograma.

    notas = [5, 7, 7, 8, 6, 9, 7, 4]
    print(pantalla.media(notas))          # 6.625
    print(pantalla.moda(notas))           # 7
    pantalla.tabla_frecuencias(notas)     # xᵢ, fᵢ, Fᵢ, hᵢ y %
    pantalla.histograma(notas)            # las barras de pie
"""

import math
from fractions import Fraction

from .colores import estilo as _estilo_ansi
from .numeros import _bonito, _sacar
from .terminal import _entero, _fin_de_estilo


def _lista(datos, funcion):
    """Los datos como lista. Vale una lista, una tupla o un dict {valor: veces}."""
    if isinstance(datos, dict):
        lista = []
        for valor, veces in datos.items():
            if isinstance(veces, bool) or not isinstance(veces, int) or veces < 0:
                raise TypeError("%s: en el dict, cada valor tiene que decir cuántas veces sale (un entero), "
                                "y %r tiene %r" % (funcion, valor, veces))
            lista += [valor] * veces
        datos = lista
    elif isinstance(datos, (str, bytes)) or not hasattr(datos, "__iter__"):
        raise TypeError("%s: dame una lista de datos, por ejemplo %s([5, 7, 7, 8])" % (funcion, funcion))
    datos = list(datos)
    if not datos:
        raise ValueError("%s: la lista está vacía" % funcion)
    return datos


def _numeros(datos, funcion):
    datos = _lista(datos, funcion)
    for v in datos:
        if isinstance(v, bool) or not isinstance(v, (int, float, Fraction)):
            raise TypeError("%s: necesito números, y en la lista hay un %r" % (funcion, v))
    return [v if isinstance(v, float) else Fraction(v) for v in datos]


def _numero(v):
    """Lo que devuelven: un entero si lo es; si no, con decimales (6.625, no 53/8)."""
    if isinstance(v, Fraction):
        return int(v) if v.denominator == 1 else _bonito(float(v))
    return _bonito(v)


def media(datos):
    """La media: se suman todos y se divide entre cuántos hay.

        pantalla.media([5, 7, 7, 8])       # 6.75
    """
    ns = _numeros(datos, "media")
    return _numero(sum(ns, Fraction(0)) / len(ns))


def mediana(datos):
    """El de en medio cuando están ordenados (con un número par, la media de los dos del medio).

        pantalla.mediana([5, 9, 7])         # 7
        pantalla.mediana([5, 9, 7, 8])      # 7.5
    """
    ns = sorted(_numeros(datos, "mediana"))
    n = len(ns)
    m = ns[n // 2] if n % 2 else (ns[n // 2 - 1] + ns[n // 2]) / 2
    return _numero(m)


def _contar(datos):
    veces = {}
    for v in datos:
        veces[v] = veces.get(v, 0) + 1
    return veces


def _ordenados(valores):
    """Los números de menor a mayor; si hay textos, en el orden en que salen."""
    if all(isinstance(v, (int, float, Fraction)) and not isinstance(v, bool) for v in valores):
        return sorted(valores)
    return list(valores)


def moda(datos):
    """El que más se repite. Si hay empate, devuelve la lista de los que empatan.

        pantalla.moda([5, 7, 7, 8])                     # 7
        pantalla.moda([1, 1, 2, 2, 3])                  # [1, 2]
        pantalla.moda(["rojo", "azul", "rojo"])        # "rojo" (vale con textos)
    """
    veces = _contar(_lista(datos, "moda"))
    mas = max(veces.values())
    modas = [v for v in _ordenados(list(veces)) if veces[v] == mas]
    modas = [_numero(v) if isinstance(v, Fraction) else v for v in modas]
    return modas[0] if len(modas) == 1 else modas


def varianza(datos, muestra=False):
    """La varianza: la media de lo que se separa cada dato de la media, al cuadrado.

        pantalla.varianza([2, 4, 4, 4, 5, 5, 7, 9])      # 4
        pantalla.varianza(datos, muestra=True)           # dividiendo entre n - 1
    """
    ns = _numeros(datos, "varianza")
    if muestra and len(ns) < 2:
        raise ValueError("varianza: con muestra=True necesito por lo menos 2 datos")
    m = sum(ns, Fraction(0)) / len(ns)
    return _numero(sum(((v - m) ** 2 for v in ns), Fraction(0)) / (len(ns) - (1 if muestra else 0)))


def desviacion(datos, muestra=False):
    """La desviación típica: la raíz de la varianza. Dice lo separados que están los datos.

        pantalla.desviacion([2, 4, 4, 4, 5, 5, 7, 9])    # 2
    """
    v = varianza(datos, muestra)
    r = math.isqrt(v) if isinstance(v, int) else None
    return r if r is not None and r * r == v else _bonito(math.sqrt(v))


def cuartiles(datos):
    """Los tres cuartiles (Q1, Q2, Q3): dejan por debajo el 25 %, el 50 % y el 75 % de los datos.

        pantalla.cuartiles([1, 2, 3, 4, 5, 6, 7, 8])     # (2.5, 4.5, 6.5)

    Se hace como en clase: se mira la posición k·n/4; si sale justa, la media de ese y el siguiente,
    y si no, el siguiente.
    """
    ns = sorted(_numeros(datos, "cuartiles"))
    n = len(ns)
    q = []
    for k in (1, 2, 3):
        pos = Fraction(k * n, 4)
        if pos.denominator == 1:
            i = int(pos)
            q.append(ns[i - 1] if i >= n else (ns[i - 1] + ns[i]) / 2)
        else:
            q.append(ns[math.ceil(pos) - 1])
    return tuple(_numero(v) for v in q)


def _texto(v, decimales=2):
    if isinstance(v, Fraction):
        v = _numero(v)
    if isinstance(v, float):
        if v.is_integer():
            return str(int(v))
        if abs(v) < 1e-3 or abs(v) >= 1e9:
            return "%g" % v
        return ("%.*f" % (decimales, v)).rstrip("0").rstrip(".")
    return str(v)


def _clases(datos, intervalos, funcion):
    """Junta los datos en intervalos iguales. Devuelve [(etiqueta, veces)]."""
    intervalos = _entero(intervalos, "intervalos", funcion)
    if intervalos < 1:
        raise ValueError("%s: intervalos tiene que ser 1 o más" % funcion)
    ns = _numeros(datos, funcion)
    bajo, alto = min(ns), max(ns)
    paso = (alto - bajo) / intervalos if alto > bajo else 1
    if not isinstance(paso, float):
        paso = Fraction(paso)
    clases = []
    for k in range(intervalos):
        a, b = bajo + paso * k, bajo + paso * (k + 1)
        ultimo = k == intervalos - 1
        veces = sum(1 for v in ns if a <= v < b or (ultimo and v == b))
        clases.append(("[%s, %s%s" % (_texto(a), _texto(b), "]" if ultimo else ")"), veces))
    return clases


def _frecuencias(datos, intervalos, funcion):
    if intervalos is not None:
        return _clases(datos, intervalos, funcion)
    veces = _contar(_lista(datos, funcion))
    return [(_texto(v), veces[v]) for v in _ordenados(list(veces))]


def tabla_frecuencias(datos, x=None, y=None, intervalos=None, color=None, color_cabecera="cian"):
    """Dibuja la tabla de frecuencias: cada valor, cuántas veces sale (fᵢ), las acumuladas (Fᵢ),
    la relativa (hᵢ) y el tanto por ciento.

        pantalla.tabla_frecuencias([5, 7, 7, 8, 6, 9, 7, 4])
        pantalla.tabla_frecuencias(alturas, intervalos=5)        # en 5 intervalos iguales
        pantalla.tabla_frecuencias(["rojo", "azul", "rojo"])     # también con textos

    Devuelve un dict con cuántas veces sale cada valor (o cada intervalo).
    """
    clases = _frecuencias(datos, intervalos, "tabla_frecuencias")
    n = sum(v for _, v in clases)
    filas, acumulada = [], 0
    for etiqueta, f in clases:
        acumulada += f
        filas.append([etiqueta, str(f), str(acumulada), _texto(f / n, 3),
                      _texto(100.0 * f / n) + " %"])
    filas.append(["Total", str(n), "", "1", "100 %"])
    # los números a la derecha: se rellenan aquí porque tabla() solo alinea así los int
    anchos = [max(len(f[i]) for f in filas + [["", "fᵢ", "Fᵢ", "hᵢ", "%"]]) for i in range(5)]
    filas = [[f[0]] + [f[i].rjust(anchos[i]) for i in range(1, 5)] for f in filas]
    from .componentes import tabla
    tabla(filas, ["xᵢ" if intervalos is None else "Intervalo", "fᵢ", "Fᵢ", "hᵢ", "%"], x, y,
          color=color, color_cabecera=color_cabecera)
    return {etiqueta: f for etiqueta, f in clases}


_OCTAVOS = " ▁▂▃▄▅▆▇█"


def histograma(datos, x=None, y=None, intervalos=None, alto=10, ancho_barra=3, color="cian", valores=True):
    """Dibuja un histograma: una barra de pie por cada valor (o intervalo), tan alta como las veces que sale.

        pantalla.histograma([5, 7, 7, 8, 6, 9, 7, 4])
        pantalla.histograma(alturas, intervalos=6)                 # junta los datos en 6 intervalos
        pantalla.histograma(["rojo", "azul", "rojo"], color="verde")

    - alto: las filas que ocupa la barra más alta.
    - valores=False: sin el número de encima de cada barra.
    Sin x ni y, se dibuja donde esté el cursor (como un print). Devuelve (ancho, alto).
    """
    alto = _entero(alto, "alto", "histograma")
    ancho_barra = _entero(ancho_barra, "ancho_barra", "histograma")
    if alto < 2 or ancho_barra < 1:
        raise ValueError("histograma: alto tiene que ser por lo menos 2 y ancho_barra por lo menos 1")
    clases = _frecuencias(datos, intervalos, "histograma")
    tope = max(v for _, v in clases)
    w = max([ancho_barra] + [len(e) for e, _ in clases])
    cod, gris, fin = _estilo_ansi(color), _estilo_ansi("gris"), _fin_de_estilo()
    # cada barra es una columna de casillas de abajo arriba, con el número justo encima
    columnas = []
    for _, v in clases:
        o = int(round(v / tope * alto * 8)) if tope else 0
        casillas = [cod + ("█" * ancho_barra).center(w) + fin] * (o // 8)
        if o % 8:
            casillas.append(cod + (_OCTAVOS[o % 8] * ancho_barra).center(w) + fin)
        if valores:
            casillas.append(gris + str(v).center(w) + fin)
        columnas.append(casillas + [" " * w] * (alto + 1 - len(casillas)))
    filas = alto + 1 if valores else alto
    lineas = [" ".join(c[f] for c in columnas).rstrip() for f in range(filas - 1, -1, -1)]
    lineas.append(gris + "─" * (len(clases) * (w + 1) - 1) + fin)
    lineas.append(" ".join(e.center(w) for e, _ in clases).rstrip())
    _sacar(lineas, x, y, "histograma")
    return len(clases) * (w + 1) - 1, len(lineas)


def estadisticas(datos, x=None, y=None, color=None, color_cabecera="cian"):
    """Saca en una tabla todo de una vez: cuántos hay, media, mediana, moda, desviación, cuartiles...

        pantalla.estadisticas([5, 7, 7, 8, 6, 9, 7, 4])

    Devuelve un dict con todo, por si quieres usarlo: r["media"], r["desviacion"]...
    """
    ns = _numeros(datos, "estadisticas")
    q1, q2, q3 = cuartiles(ns)
    r = {"n": len(ns), "media": media(ns), "mediana": mediana(ns), "moda": moda(ns),
         "minimo": _numero(min(ns)), "maximo": _numero(max(ns)), "recorrido": _numero(max(ns) - min(ns)),
         "varianza": varianza(ns), "desviacion": desviacion(ns), "cuartiles": (q1, q2, q3)}
    nombres = [("Datos (n)", "n"), ("Media", "media"), ("Mediana", "mediana"), ("Moda", "moda"),
               ("Mínimo", "minimo"), ("Máximo", "maximo"), ("Recorrido", "recorrido"),
               ("Varianza", "varianza"), ("Desviación típica", "desviacion")]
    filas = []
    for texto, k in nombres:
        v = r[k]
        filas.append([texto, ", ".join(_texto(m, 4) for m in v) if isinstance(v, list) else _texto(v, 4)])
    filas.append(["Cuartiles", "%s, %s, %s" % (_texto(q1, 4), _texto(q2, 4), _texto(q3, 4))])
    ancho = max(len(f[1]) for f in filas)
    from .componentes import tabla
    tabla([[a, b.rjust(ancho)] for a, b in filas], None, x, y, color=color, color_cabecera=color_cabecera)
    return r
