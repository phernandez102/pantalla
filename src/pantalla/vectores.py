"""
Vectores: sumarlos, multiplicarlos, el módulo, el ángulo entre dos, el producto
escalar y el vectorial... y dibujarlos con flechas en unos ejes.

    u = (3, 4)
    print(pantalla.modulo(u))                        # 5
    print(pantalla.producto_escalar(u, (1, 2)))      # 11
    pantalla.producto_escalar(u, (1, 2), pasos=True) # enseña la cuenta
    pantalla.dibujar_vectores({"u": (3, 4), "v": (-2, 1)})

Valen tuplas (3, 4), listas [3, 4] o pantalla.Vector(3, 4). Las cuentas se hacen con
fracciones, como en las matrices: (1/2, 1/3) + (1/2, 1/3) da (1, 2/3) justo.
Lo que devuelven es un Vector: sale como (3, 4) al hacer print y se puede sumar
con +, restar con - y multiplicar por un número con *.
"""

import math
from fractions import Fraction

from .colores import estilo as _estilo_ansi
from .matrices import _lineas_matriz, _texto_numero, determinante, matriz, pedir_matriz, rango
from .numeros import _a_numero, _bonito, _sacar
from .terminal import _entero, _fin_de_estilo


_NOMBRES = ["u", "v", "w", "a", "b", "c", "d", "e"]
_COLORES = ["cian", "amarillo", "verde claro", "morado claro", "rojo claro", "azul claro"]


def _componentes(v, funcion, que="el vector"):
    if isinstance(v, (str, bytes)) or not isinstance(v, (list, tuple)):
        raise TypeError("%s: %s tiene que ser una lista de números, por ejemplo (3, 4), y es %r"
                        % (funcion, que, v))
    if not v:
        raise ValueError("%s: %s está vacío. Ponle por lo menos un número, por ejemplo (3, 4)" % (funcion, que))
    return [_a_numero(n, funcion, "el número %d de %s" % (i + 1, que)) for i, n in enumerate(v)]


def _exactos(funcion, *vectores, que=None):
    """Todos con fracciones o, si alguno tiene decimales, todos con decimales."""
    nombres = que or (["el vector"] if len(vectores) == 1 else
                      ["el %s vector" % o for o in ["primer", "segundo", "tercer", "cuarto"]])
    listas = [_componentes(v, funcion, nombres[i] if i < len(nombres) else "el vector %d" % (i + 1))
              for i, v in enumerate(vectores)]
    decimales = any(isinstance(n, float) for v in listas for n in v)
    tipo = float if decimales else Fraction
    return [[tipo(n) for n in v] for v in listas]


def _misma_dimension(u, v, funcion):
    if len(u) != len(v):
        raise ValueError("%s: el primer vector tiene %d números y el segundo %d. Tienen que tener los mismos"
                         % (funcion, len(u), len(v)))


def _tres(u, funcion):
    if len(u) != 3:
        raise ValueError("%s: solo existe con vectores de 3 números (x, y, z), y este tiene %d"
                         % (funcion, len(u)))


def _cero(n):
    return abs(n) < 1e-10 if isinstance(n, float) else n == 0


def _p(n):
    """El número para una cuenta: los negativos y las fracciones entre paréntesis."""
    t = _texto_numero(_bonito(n))
    return "(%s)" % t if t.startswith("-") or "/" in t else t


def _texto_vector(v):
    return "(" + ", ".join(_texto_numero(_bonito(n)) for n in v) + ")"


class Vector(tuple):
    """Un vector que sale como (3, 4) al hacer print y que se suma con + y se multiplica con *.

        u = pantalla.Vector(3, 4)
        v = pantalla.Vector([1, 2])
        print(u + v)          # (4, 6)
        print(2 * u - v)      # (5, 6)
        print(abs(u))         # 5   (el módulo)
        x, y = u              # se puede separar como una tupla
    """

    __slots__ = ()

    def __new__(cls, *componentes):
        if len(componentes) == 1 and isinstance(componentes[0], (list, tuple)):
            componentes = componentes[0]
        return super().__new__(cls, (_bonito(n) for n in _exactos("Vector", list(componentes))[0]))

    def __repr__(self):
        return _texto_vector(self)

    __str__ = __repr__

    def __add__(self, otro):
        if isinstance(otro, (list, tuple)):
            return sumar_vectores(self, otro)
        return NotImplemented

    def __radd__(self, otro):
        if isinstance(otro, (list, tuple)):
            return sumar_vectores(otro, self)
        return NotImplemented

    def __sub__(self, otro):
        if isinstance(otro, (list, tuple)):
            return restar_vectores(self, otro)
        return NotImplemented

    def __rsub__(self, otro):
        if isinstance(otro, (list, tuple)):
            return restar_vectores(otro, self)
        return NotImplemented

    def __mul__(self, k):
        if isinstance(k, (list, tuple)):
            raise TypeError("para multiplicar dos vectores usa pantalla.producto_escalar(u, v) "
                            "o pantalla.producto_vectorial(u, v)")
        if isinstance(k, (int, float, Fraction)) and not isinstance(k, bool):
            return multiplicar_vector(k, self)
        return NotImplemented

    __rmul__ = __mul__

    def __truediv__(self, k):
        if isinstance(k, (int, float, Fraction)) and not isinstance(k, bool):
            if k == 0:
                raise ZeroDivisionError("Vector: no se puede dividir entre 0")
            return multiplicar_vector(1 / k if isinstance(k, float) else Fraction(1) / Fraction(k), self)
        return NotImplemented

    def __neg__(self):
        return multiplicar_vector(-1, self)

    def __pos__(self):
        return self

    def __abs__(self):
        return modulo(self)

    def __getnewargs__(self):
        return (tuple(self),)


def _devolver(v):
    return Vector([_bonito(n) for n in v])


# --- dibujarlos y pedirlos --------------------------------------------------

def vector(v, x=None, y=None, nombre=None, color=None, color_nombre="cian", vertical=False):
    """Escribe un vector: u = (3, -1, 2). Devuelve (ancho, alto) de lo que ocupa.

        pantalla.vector((3, -1, 2), nombre="u")            # u = (3, -1, 2), donde esté el cursor
        pantalla.vector((3, -1, 2), 5, 3, nombre="u")      # en la columna 5, fila 3
        pantalla.vector((3, -1, 2), nombre="u", vertical=True)   # en columna, con corchetes
    """
    numeros, = _exactos("vector", v)
    if vertical:
        return matriz([[_bonito(n)] for n in numeros], x, y, nombre=nombre, color=color, color_nombre=color_nombre)
    texto = _texto_vector(numeros)
    delante = (str(nombre) + " = ") if nombre else ""
    cod, cod_n, fin = _estilo_ansi(color), _estilo_ansi(color_nombre, negrita=True), _fin_de_estilo()
    linea = (cod_n + delante + fin if delante else "") + (cod + texto + fin if cod else texto)
    _sacar([linea], x, y, "vector")
    return len(delante) + len(texto), 1


def pedir_vector(nombre="u", dimension=None, maximo=6, fracciones=False, titulo=None, color="cian"):
    """Pide un vector en una ventana: primero cuántos números tiene y luego cada uno.

        u = pantalla.pedir_vector()                    # eliges cuántos números
        v = pantalla.pedir_vector("v", dimension=3)    # (x, y, z)

    Devuelve un Vector, o None si pulsas Esc.
    """
    if dimension is not None:
        dimension = _entero(dimension, "dimension", "pedir_vector")
        if dimension < 1:
            raise ValueError("pedir_vector: dimension tiene que ser 1 o más, y me has dado %d" % dimension)
    M = pedir_matriz(nombre, filas=1, columnas=dimension, maximo=maximo, fracciones=fracciones,
                     titulo=titulo or "Vector " + str(nombre), color=color)
    return None if M is None else Vector(M[0])


# --- cuentas ----------------------------------------------------------------

def vector_entre(A, B):
    """El vector que va del punto A al punto B (B - A).

        pantalla.vector_entre((1, 2), (4, 6))      # (3, 4)
    """
    A, B = _exactos("vector_entre", A, B, que=["el punto A", "el punto B"])
    _misma_dimension(A, B, "vector_entre")
    return _devolver([b - a for a, b in zip(A, B)])


def sumar_vectores(u, v):
    """Suma dos vectores número a número.

        pantalla.sumar_vectores((1, 2), (3, 4))     # (4, 6)
    """
    u, v = _exactos("sumar_vectores", u, v)
    _misma_dimension(u, v, "sumar_vectores")
    return _devolver([a + b for a, b in zip(u, v)])


def restar_vectores(u, v):
    """Resta dos vectores (u - v) número a número.

        pantalla.restar_vectores((5, 5), (1, 2))    # (4, 3)
    """
    u, v = _exactos("restar_vectores", u, v)
    _misma_dimension(u, v, "restar_vectores")
    return _devolver([a - b for a, b in zip(u, v)])


def multiplicar_vector(k, u):
    """Multiplica un vector por un número (vale en los dos órdenes).

        pantalla.multiplicar_vector(3, (1, -2))          # (3, -6)
        pantalla.multiplicar_vector((1, -2), "1/2")      # (1/2, -1)
    """
    if isinstance(k, (list, tuple)) and not isinstance(u, (list, tuple)):
        k, u = u, k
    k = _a_numero(k, "multiplicar_vector", "el número")
    v, = _exactos("multiplicar_vector", u)
    if isinstance(k, float) or isinstance(v[0], float):
        k, v = float(k), [float(n) for n in v]
    else:
        k = Fraction(k)
    return _devolver([k * n for n in v])


def producto_escalar(u, v, pasos=False):
    """El producto escalar u · v: multiplica número a número y lo suma todo.

        pantalla.producto_escalar((1, 2, 3), (4, -5, 6))               # 12
        pantalla.producto_escalar((1, 2, 3), (4, -5, 6), pasos=True)
        # u · v = 1·4 + 2·(-5) + 3·6 = 4 - 10 + 18 = 12

    Si da 0, los vectores son perpendiculares.
    """
    u, v = _exactos("producto_escalar", u, v)
    _misma_dimension(u, v, "producto_escalar")
    productos = [a * b for a, b in zip(u, v)]
    total = sum(productos, u[0] * 0)
    if pasos:
        _sacar([_cuenta_escalar(u, v, productos, total)], None, None, "producto_escalar")
    return _bonito(total)


def _cuenta_escalar(u, v, productos, total):
    cuenta = " + ".join("%s·%s" % (_p(a), _p(b)) for a, b in zip(u, v))
    sumandos = ""
    for i, n in enumerate(productos):
        t = _texto_numero(_bonito(n))
        if i == 0:
            sumandos = t
        elif t.startswith("-"):
            sumandos += " - " + t[1:]
        else:
            sumandos += " + " + t
    partes = ["u · v = " + cuenta]
    if len(productos) > 1:
        partes.append(sumandos)
    partes.append(_texto_numero(_bonito(total)))
    return " = ".join(partes)


def _raiz(s):
    """La raíz cuadrada justa si la tiene; si no, un decimal."""
    if isinstance(s, Fraction) and s >= 0:
        n, d = math.isqrt(s.numerator), math.isqrt(s.denominator)
        if n * n == s.numerator and d * d == s.denominator:
            return Fraction(n, d)
    return math.sqrt(s)


def _texto_raiz(s):
    """√8 -> '2√2'. None si no es un entero o no se puede simplificar."""
    if not (isinstance(s, Fraction) and s.denominator == 1 and s > 0):
        return None
    n = s.numerator
    fuera, dentro, k = 1, n, 2
    while k * k <= dentro:
        while dentro % (k * k) == 0:
            fuera, dentro = fuera * k, dentro // (k * k)
        k += 1
    if fuera == 1 or dentro == 1:
        return None
    return "%d√%d" % (fuera, dentro)


def modulo(u, pasos=False, nombre="u"):
    """El módulo (lo que mide) de un vector: la raíz de la suma de los cuadrados.

        pantalla.modulo((3, 4))              # 5
        pantalla.modulo((1, 1))              # 1.414213562373
        pantalla.modulo((2, 2), pasos=True)  # |u| = √(2² + 2²) = √8 = 2√2 ≈ 2.8284
        pantalla.modulo(v, pasos=True, nombre="v")   # |v| = ...
    """
    u, = _exactos("modulo", u)
    s = sum((n * n for n in u), u[0] * 0)
    r = _raiz(s)
    if pasos:
        _sacar([_cuenta_modulo(u, s, r, nombre)], None, None, "modulo")
    return _bonito(r)


def _cuenta_modulo(u, s, r, nombre="u"):
    cuadrados = " + ".join(_p(n) + "²" for n in u)
    partes = ["|%s| = √(%s)" % (nombre, cuadrados), "√" + _p(s)]
    if isinstance(r, Fraction):
        partes.append(_texto_numero(_bonito(r)))
    else:
        simple = _texto_raiz(s)
        if simple:
            partes.append(simple)
        partes[-1] += " ≈ " + ("%.4f" % r).rstrip("0").rstrip(".")
    return " = ".join(partes)


def unitario(u):
    """El vector de la misma dirección que mide 1 (u dividido entre su módulo).

        pantalla.unitario((3, 4))      # (3/5, 4/5)
    """
    v, = _exactos("unitario", u)
    if all(_cero(n) for n in v):
        raise ValueError("unitario: el vector (0, 0...) no tiene dirección, así que no tiene unitario")
    m = _raiz(sum((n * n for n in v), v[0] * 0))
    if isinstance(m, float):
        v = [float(n) for n in v]
    return _devolver([n / m for n in v])


def distancia(A, B):
    """La distancia entre dos puntos: el módulo del vector que va de uno a otro.

        pantalla.distancia((1, 1), (4, 5))     # 5
    """
    return modulo(vector_entre(A, B))


def angulo(u, v, radianes=False, pasos=False):
    """El ángulo entre dos vectores, en grados (o en radianes con radianes=True).

        pantalla.angulo((1, 0), (0, 1))             # 90.0
        pantalla.angulo((1, 0), (1, 1))             # 45.0
        pantalla.angulo((1, 2), (3, 1), pasos=True)
    """
    u, v = _exactos("angulo", u, v)
    _misma_dimension(u, v, "angulo")
    if all(_cero(n) for n in u) or all(_cero(n) for n in v):
        raise ValueError("angulo: con el vector (0, 0...) no hay ángulo, porque no tiene dirección")
    pe = sum((a * b for a, b in zip(u, v)), u[0] * 0)
    su, sv = sum((n * n for n in u), u[0] * 0), sum((n * n for n in v), u[0] * 0)
    cos = float(pe) / math.sqrt(float(su) * float(sv))
    cos = max(-1.0, min(1.0, cos))
    a = math.acos(cos)
    resultado = _bonito(a if radianes else math.degrees(a))
    if pasos:
        mu, mv = _raiz(su), _raiz(sv)
        tm = lambda s, r: _texto_numero(_bonito(r)) if isinstance(r, Fraction) else (_texto_raiz(s) or "√" + _p(s))
        grados = ("%.2f" % math.degrees(a)).rstrip("0").rstrip(".")
        _sacar(["cos α = u · v / (|u|·|v|) = %s / (%s·%s) ≈ %s" % (_texto_numero(_bonito(pe)), tm(su, mu), tm(sv, mv),
                                                              ("%.4f" % cos).rstrip("0").rstrip(".")),
                "α ≈ %s°" % grados], None, None, "angulo")
    return resultado


def producto_vectorial(u, v, pasos=False):
    """El producto vectorial u × v (solo con vectores de 3 números). Sale perpendicular a los dos.

        pantalla.producto_vectorial((1, 0, 0), (0, 1, 0))        # (0, 0, 1)
        pantalla.producto_vectorial((1, 2, 3), (4, 5, 6), pasos=True)
        #         │ i  j  k │
        # u × v = │ 1  2  3 │ = (2·6 - 3·5, 3·4 - 1·6, 1·5 - 2·4) = (-3, 6, -3)
        #         │ 4  5  6 │
    """
    u, v = _exactos("producto_vectorial", u, v)
    _tres(u, "producto_vectorial")
    _tres(v, "producto_vectorial")
    w = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
    if pasos:
        lineas, _, _ = _lineas_matriz([["i", "j", "k"], [_bonito(n) for n in u], [_bonito(n) for n in v]], None, True)
        cuenta = "(%s·%s - %s·%s, %s·%s - %s·%s, %s·%s - %s·%s)" % (
            _p(u[1]), _p(v[2]), _p(u[2]), _p(v[1]), _p(u[2]), _p(v[0]), _p(u[0]), _p(v[2]),
            _p(u[0]), _p(v[1]), _p(u[1]), _p(v[0]))
        delante = "u × v = "
        salida = []
        for k, (izq, dentro, der) in enumerate(lineas):
            caja_ = izq + dentro + der
            if k == 2:
                salida.append(delante + caja_ + " = " + cuenta + " = " + _texto_vector(w))
            elif 1 <= k <= 3:
                salida.append(" " * len(delante) + caja_)
        _sacar(salida, None, None, "producto_vectorial")
    return _devolver(w)


def producto_mixto(u, v, w):
    """El producto mixto [u, v, w] = u · (v × w): el determinante de los tres vectores.

        pantalla.producto_mixto((1, 0, 0), (0, 1, 0), (0, 0, 1))      # 1

    Su valor absoluto es el volumen del paralelepípedo que forman. Si da 0, los tres están en el mismo plano.
    """
    u, v, w = _exactos("producto_mixto", u, v, w)
    for x in (u, v, w):
        _tres(x, "producto_mixto")
    return determinante([u, v, w])


def proyeccion(u, v):
    """La proyección de u sobre v: la "sombra" de u en la dirección de v.

        pantalla.proyeccion((2, 3), (1, 0))       # (2, 0)
    """
    u, v = _exactos("proyeccion", u, v)
    _misma_dimension(u, v, "proyeccion")
    vv = sum((n * n for n in v), v[0] * 0)
    if _cero(vv):
        raise ValueError("proyeccion: no se puede proyectar sobre el vector (0, 0...)")
    k = sum((a * b for a, b in zip(u, v)), u[0] * 0) / vv
    return _devolver([k * n for n in v])


def son_paralelos(u, v):
    """True si u y v tienen la misma dirección (uno es el otro multiplicado por un número).

        pantalla.son_paralelos((1, 2), (3, 6))      # True
    """
    u, v = _exactos("son_paralelos", u, v)
    _misma_dimension(u, v, "son_paralelos")
    return rango([u, v]) <= 1


def son_perpendiculares(u, v):
    """True si u y v forman un ángulo recto (su producto escalar es 0).

        pantalla.son_perpendiculares((1, 2), (-2, 1))   # True
    """
    u, v = _exactos("son_perpendiculares", u, v)
    _misma_dimension(u, v, "son_perpendiculares")
    return _cero(sum((a * b for a, b in zip(u, v)), u[0] * 0))


def son_independientes(*vectores):
    """True si ninguno se puede sacar sumando los otros multiplicados por números.

        pantalla.son_independientes((1, 0), (0, 1))              # True
        pantalla.son_independientes((1, 2, 3), (2, 4, 6))        # False: el segundo es el doble
    """
    if len(vectores) == 1 and isinstance(vectores[0], (list, tuple)) and vectores[0] \
            and all(isinstance(v, (list, tuple)) for v in vectores[0]):
        vectores = tuple(vectores[0])
    if not vectores:
        raise TypeError("son_independientes: dame por lo menos un vector")
    vs = _exactos("son_independientes", *vectores, que=["el vector %d" % (i + 1) for i in range(len(vectores))])
    for i, v in enumerate(vs[1:], 2):
        if len(v) != len(vs[0]):
            raise ValueError("son_independientes: el vector 1 tiene %d números y el vector %d tiene %d. "
                             "Tienen que tener los mismos" % (len(vs[0]), i, len(v)))
    return rango(vs) == len(vs)


# --- dibujar vectores con flechas -------------------------------------------

_FLECHAS = ["→", "↗", "↑", "↖", "←", "↙", "↓", "↘"]


def _limites(valores):
    """Desde dónde hasta dónde va un eje: con un hueco alrededor y en números redondos."""
    bajo, alto = min(valores), max(valores)
    largo = max(alto - bajo, 1)
    paso = 1
    while largo / paso > 10:
        for k in (2, 5, 10):
            if largo / (paso * k) <= 10:
                paso *= k
                break
        else:
            paso *= 10
    # un hueco alrededor para que quepan las flechas y los nombres
    return (int(math.floor(bajo / paso) * paso - paso) if bajo % paso == 0 else int(math.floor(bajo / paso) * paso),
            int(math.ceil(alto / paso) * paso + paso) if alto % paso == 0 else int(math.ceil(alto / paso) * paso))


def _leer_flechas(vectores):
    if isinstance(vectores, dict):
        pares = list(vectores.items())
    else:
        if isinstance(vectores, tuple) and vectores and not isinstance(vectores[0], (list, tuple)):
            vectores = [vectores]
        pares = [(_NOMBRES[i] if i < len(_NOMBRES) else "v%d" % (i + 1), v) for i, v in enumerate(vectores)]
    if not pares:
        raise ValueError("dibujar_vectores: no hay vectores que dibujar")
    flechas = []
    for nombre, v in pares:
        que = "el vector %s" % nombre
        if isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(p, (list, tuple)) for p in v):
            desde, hasta = [[float(n) for n in _componentes(p, "dibujar_vectores", que)] for p in v]
        else:
            desde, hasta = [0.0, 0.0], [float(n) for n in _componentes(v, "dibujar_vectores", que)]
        for p in (desde, hasta):
            if len(p) != 2:
                raise ValueError("dibujar_vectores: solo sé dibujar vectores de 2 números (x, y), y %s tiene %d"
                                 % (que, len(p)))
        flechas.append((str(nombre), desde, hasta))
    return flechas


def dibujar_vectores(vectores, x=None, y=None, ancho=41, alto=17, colores=None, cuadricula=True):
    """Dibuja vectores con flechas en unos ejes, cada uno de un color.

        pantalla.dibujar_vectores({"u": (3, 2), "v": (-1, 4)})
        pantalla.dibujar_vectores([(3, 2), (-1, 4)])                  # se llaman u, v, w...
        pantalla.dibujar_vectores({"u": (3, 2), "v": ((3, 2), (2, 6))})   # v empieza en la punta de u

    Un vector puede ser (x, y), que sale del origen, o ((x0, y0), (x1, y1)): de un punto a otro.
    - ancho, alto: lo que ocupa como mucho, contando los números de los ejes.
    - cuadricula=False: sin los puntitos de cada unidad.
    Sin x ni y, se dibuja donde esté el cursor (como un print). Devuelve (ancho, alto).
    """
    ancho = _entero(ancho, "ancho", "dibujar_vectores")
    alto = _entero(alto, "alto", "dibujar_vectores")
    if ancho < 12 or alto < 6:
        raise ValueError("dibujar_vectores: es muy pequeño. Ponle por lo menos ancho=12 y alto=6")
    flechas = _leer_flechas(vectores)
    xs = [0.0] + [p[0] for _, a, b in flechas for p in (a, b)]
    ys = [0.0] + [p[1] for _, a, b in flechas for p in (a, b)]
    x0, x1 = _limites(xs)
    y0, y1 = _limites(ys)
    ancho_num = max(len(str(y0)), len(str(y1)), 1)
    sitio_x, sitio_y = ancho - ancho_num - 1, alto - 1
    # cada unidad ocupa el doble de columnas que de filas, porque las letras son altas
    escala = min((sitio_x - 1) / (2 * (x1 - x0)), (sitio_y - 1) / (y1 - y0))
    cols = int(round((x1 - x0) * 2 * escala)) + 1
    filas = int(round((y1 - y0) * escala)) + 1

    def celda(px, py):
        return (px - x0) * 2 * escala, (y1 - py) * escala

    gris = _estilo_ansi("gris")
    celdas = [[(" ", None)] * cols for _ in range(filas)]
    cx0, cy0 = [int(round(c)) for c in celda(0, 0)]
    if cuadricula and escala >= 1:
        for gx in range(x0, x1 + 1):
            for gy in range(y0, y1 + 1):
                c, f = [int(round(n)) for n in celda(gx, gy)]
                celdas[f][c] = ("·", gris)
    for c in range(cols):
        celdas[cy0][c] = ("─", gris)
    for f in range(filas):
        celdas[f][cx0] = ("┼" if f == cy0 else "│", gris)

    puntas = []
    for i, (nombre, desde, hasta) in enumerate(flechas):
        color = colores.get(nombre) if isinstance(colores, dict) else (
            colores[i % len(colores)] if colores else _COLORES[i % len(_COLORES)])
        cod = _estilo_ansi(color)
        (ax, ay), (bx, by) = celda(*desde), celda(*hasta)
        # un paso por casilla en la dirección más larga, para que la raya no haga escalones
        ca, fa, cb, fb = [int(round(n)) for n in (ax, ay, bx, by)]
        pasos = max(1, abs(cb - ca), abs(fb - fa))
        camino = []
        for k in range(pasos + 1):
            p = (ca + int(round((cb - ca) * k / pasos)), fa + int(round((fb - fa) * k / pasos)))
            if not camino or camino[-1] != p:
                camino.append(p)
        for i, ((c, f), (c2, f2)) in enumerate(zip(camino, camino[1:])):
            # si sale de los ejes, el ┼ (o la raya del eje) se queda
            if i == 0 and (c == cx0 or f == cy0):
                continue
            dc, df = c2 - c, f2 - f
            ch = "─" if df == 0 else "│" if dc == 0 else "╱" if dc * df < 0 else "╲"
            celdas[f][c] = (ch, cod)
        # la punta, mirando hacia donde va (en la pantalla una fila es el doble de alta)
        ang = math.degrees(math.atan2(-(by - ay) * 2, bx - ax))
        punta = "•" if (bx, by) == (ax, ay) else _FLECHAS[int(round(ang / 45)) % 8]
        puntas.append((camino[-1], punta, cod, nombre, bx - ax))

    for (c, f), punta, cod, _, _ in puntas:
        celdas[f][c] = (punta, cod)
    # el nombre al lado de la punta, donde no pise nada
    for (c, f), _, cod, nombre, dx in puntas:
        n = len(nombre)
        sitios = [(c + 1, f), (c - n, f), (c + 1, f - 1), (c - n, f - 1), (c + 1, f + 1), (c - n, f + 1)]
        if dx < 0:
            sitios[0], sitios[1] = sitios[1], sitios[0]
            sitios[2], sitios[3] = sitios[3], sitios[2]
            sitios[4], sitios[5] = sitios[5], sitios[4]
        for sc, sf in sitios:
            if 0 <= sf < filas and 0 <= sc and sc + n <= cols and \
                    all(celdas[sf][k][0] in " ·─│" for k in range(sc, sc + n)):
                for k, letra in enumerate(nombre):
                    celdas[sf][sc + k] = (letra, cod)
                break

    fin = _fin_de_estilo()
    lineas = []
    for f in range(filas):
        numero = str(y1) if f == 0 else str(y0) if f == filas - 1 else "0" if f == cy0 else ""
        partes = [gris + numero.rjust(ancho_num) + " " + fin]
        for ch, cod in celdas[f]:
            partes.append(cod + ch + fin if cod else ch)
        lineas.append("".join(partes).rstrip())
    izq, der = str(x0), str(x1)
    abajo = " " * (ancho_num + 1) + izq
    pos_cero = ancho_num + 1 + cx0
    if pos_cero > len(abajo) + 1 and pos_cero < ancho_num + 1 + cols - len(der) - 1:
        abajo += " " * (pos_cero - len(abajo)) + "0"
    abajo += der.rjust(ancho_num + 1 + cols - len(abajo))
    lineas.append(gris + abajo + fin)
    _sacar(lineas, x, y, "dibujar_vectores")
    return ancho_num + 1 + cols, filas + 1
