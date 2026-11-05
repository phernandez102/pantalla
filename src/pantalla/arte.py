"""
Arte ASCII: dibujos hechos con letras (y con colores, si quieres).
"""

from .colores import estilo as _estilo_ansi
from .dibujo import _poner
from .terminal import _posicion, _salida, tamano

CODIGOS_COLOR = {
    "n": "negro",
    "r": "rojo",
    "v": "verde",
    "a": "amarillo",
    "z": "azul",
    "m": "morado",
    "c": "cian",
    "g": "gris",
    "b": "blanco",
    "R": "rojo claro",
    "V": "verde claro",
    "A": "amarillo claro",
    "Z": "azul claro",
    "M": "morado claro",
    "C": "cian claro",
    "G": "gris claro",
    "o": "naranja",
    "x": "marrón",
    "p": "rosa",
}

_SIN_CODIGO = (" ", ".")


def _filas(valor, nombre):
    if valor is None:
        return []
    if isinstance(valor, str):
        if valor.startswith("\n"):
            valor = valor[1:]
        if valor.endswith("\n"):
            valor = valor[:-1]
        return valor.split("\n")
    if isinstance(valor, (list, tuple)):
        return [str(f) for f in valor]
    raise TypeError("arte: '%s' tiene que ser un texto (con varias líneas) o una lista de textos. "
                    "Me has dado %r" % (nombre, valor))


def _color_de(codigo, por_defecto, nombre):
    if codigo in _SIN_CODIGO:
        return por_defecto
    if codigo not in CODIGOS_COLOR:
        raise ValueError("arte: en '%s' hay un código de color que no conozco: %r. Usa uno de estos: %s "
                         "(o un espacio o un punto para dejar el color normal)."
                         % (nombre, codigo, " ".join(CODIGOS_COLOR)))
    return CODIGOS_COLOR[codigo]


def arte(dibujo, x=None, y=None, color=None, fondo=None, colores=None, fondos=None, transparente=True):
    """Dibuja un arte ASCII (un dibujo hecho con letras) en la pantalla.

        gato = r'''
         /\\_/\\
        ( o.o )
         > ^ <
        '''
        pantalla.arte(gato, 10, 5, color="amarillo")

    - x, y: la esquina de arriba a la izquierda (sin ellas, sale en el centro).
    - colores: otro dibujo del mismo tamaño, pero con una letra de color en cada sitio
      (r rojo, v verde, a amarillo, z azul, m morado, c cian, b blanco, n negro, g gris,
      o naranja, x marrón, p rosa; en mayúscula, la versión "claro"). Un espacio o un
      punto deja el color normal.
    - fondos: igual que colores, pero para el color de fondo.
    - transparente: con True (lo normal) los espacios no borran lo que haya debajo.

        pantalla.arte(["(^_^)", "/| |\\\\"], 5, 5, colores=["aaaaa", "vv vv"])

    Si es un texto, se le quita el salto de línea del principio y el del final,
    así puedes escribirlo con tres comillas como en el ejemplo del gato. Pon una r
    delante de las comillas (r''') para que las barras \\ salgan tal cual.
    """
    lineas = _filas(dibujo, "dibujo")
    cols = _filas(colores, "colores")
    fons = _filas(fondos, "fondos")
    if not lineas:
        return
    ancho_dibujo = max(len(l) for l in lineas)
    ancho_p, alto_p = tamano()
    if x is None:
        x = max(1, (ancho_p - ancho_dibujo) // 2 + 1)
    if y is None:
        y = max(1, (alto_p - len(lineas)) // 2 + 1)
    x, y = _posicion(x, y, "arte")

    estilos = {}
    trozos = []
    for fila, texto in enumerate(lineas):
        if y + fila > alto_p:
            break
        fila_c = cols[fila] if fila < len(cols) else ""
        fila_f = fons[fila] if fila < len(fons) else ""
        inicio = None
        trozo = ""
        clave_trozo = None
        for col, letra in enumerate(texto + " "):
            final = col == len(texto)
            cc = fila_c[col] if col < len(fila_c) else " "
            cf = fila_f[col] if col < len(fila_f) else " "
            saltar = final or (transparente and letra == " " and cf in _SIN_CODIGO)
            clave = None if saltar else (_color_de(cc, color, "colores"), _color_de(cf, fondo, "fondos"))
            if clave != clave_trozo or saltar:
                if trozo:
                    if clave_trozo not in estilos:
                        estilos[clave_trozo] = _estilo_ansi(*clave_trozo)
                    trozos.append(_poner(x + inicio, y + fila, trozo, estilos[clave_trozo]))
                trozo = ""
                clave_trozo = clave
                inicio = col
            if not saltar:
                trozo += letra
    _salida("".join(trozos))
