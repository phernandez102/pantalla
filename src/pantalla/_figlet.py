"""
Motor de fuentes FIGlet (los ficheros .flf de la carpeta "fuentes").

Hace lo mismo que el programa figlet (y que pyfiglet): lee la fuente y junta
las letras "apretándolas" (kerning y smushing) según diga la propia fuente.
"""

import os
import re
import unicodedata

_CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fuentes")

_ALEMANAS = "ÄÖÜäöüß"

_SM_EQUAL = 1
_SM_LOWLINE = 2
_SM_HIERARCHY = 4
_SM_PAIR = 8
_SM_BIGX = 16
_SM_HARDBLANK = 32
_SM_KERN = 64
_SM_SMUSH = 128

_cache = {}


def nombres():
    try:
        ficheros = os.listdir(_CARPETA)
    except OSError:
        return []
    return sorted(f[:-4] for f in ficheros if f.endswith(".flf"))


def normalizar_nombre(nombre):
    return str(nombre).strip().lower().replace(" ", "_")


def buscar(nombre):
    """Devuelve el nombre del fichero (sin .flf) que corresponde a nombre, o None."""
    buscado = normalizar_nombre(nombre)
    todos = nombres()
    if buscado in todos:
        return buscado
    sin_signos = buscado.replace("-", "").replace("_", "")
    for n in todos:
        if n.replace("-", "").replace("_", "") == sin_signos:
            return n
    return None


def _codigo_etiqueta(linea):
    partes = linea.strip().split()
    if not partes:
        return None
    t = partes[0]
    try:
        if t.lower().startswith(("0x", "-0x")):
            return int(t, 16)
        if t.startswith("0") and len(t) > 1:
            return int(t, 8)
        return int(t)
    except ValueError:
        return None


class Fuente(object):
    def __init__(self, texto):
        datos = re.sub("[\u0085  ]", " ", texto).splitlines()
        cabecera = datos.pop(0)
        if not re.match(r"^[tf]lf2.", cabecera):
            raise ValueError("esto no es una fuente FIGlet")
        partes = cabecera[5:].split()
        self.hardblank = partes[0]
        self.alto = int(partes[1])
        antiguo = int(partes[4])
        comentarios = int(partes[5])
        completo = int(partes[7]) if len(partes) > 7 else None
        if completo is None:
            if antiguo == 0:
                completo = _SM_KERN
            elif antiguo < 0:
                completo = 0
            else:
                completo = (antiguo & 31) | _SM_SMUSH
        self.modo = completo
        self.letras = {}
        self.anchos = {}
        del datos[:comentarios]

        def leer_letra():
            fin = None
            ancho = 0
            filas = []
            for _ in range(self.alto):
                linea = datos.pop(0)
                if fin is None:
                    fin = re.compile(re.escape(re.search(r"(.)\s*$", linea).group(1)) + r"{1,2}\s*$")
                linea = fin.sub("", linea)
                ancho = max(ancho, len(linea))
                filas.append(linea)
            return ancho, filas

        def guardar(codigo, ancho, filas, siempre=False):
            if siempre or "".join(filas) != "":
                self.letras[codigo] = filas
                self.anchos[codigo] = ancho

        for codigo in range(32, 127):
            ancho, filas = leer_letra()
            guardar(codigo, ancho, filas, siempre=codigo == 32)

        for letra in _ALEMANAS:
            if len(datos) < self.alto:
                break
            primera = datos[0]
            if not primera.strip():
                break
            if _codigo_etiqueta(primera) is not None:
                marca = primera.rstrip()[-1:]
                siguiente = datos[1] if len(datos) > 1 else ""
                if not siguiente.rstrip().endswith(marca) or len(primera.split()) > 1:
                    break
            ancho, filas = leer_letra()
            guardar(ord(letra), ancho, filas)

        while datos:
            linea = datos.pop(0)
            if not linea.strip():
                continue
            codigo = _codigo_etiqueta(linea)
            if codigo is None or len(datos) < self.alto:
                break
            ancho, filas = leer_letra()
            if codigo >= 0:
                guardar(codigo, ancho, filas)

    def resolver(self, texto):
        """Cambia cada letra por la que hay en la fuente: la misma, o sin tilde, o ninguna."""
        codigos = []
        for c in texto:
            if ord(c) in self.letras:
                codigos.append(ord(c))
                continue
            base = unicodedata.normalize("NFD", c)[0]
            if ord(base) in self.letras:
                codigos.append(ord(base))
        return codigos


def cargar(nombre):
    archivo = buscar(nombre)
    if archivo is None:
        return None
    if archivo not in _cache:
        with open(os.path.join(_CARPETA, archivo + ".flf"), encoding="utf-8", errors="replace") as f:
            _cache[archivo] = Fuente(f.read())
    return _cache[archivo]


class _Constructor(object):
    def __init__(self, fuente):
        self.f = fuente
        self.buffer = [""] * fuente.alto
        self.ancho_actual = 0
        self.ancho_anterior = 0
        self.max_smush = 0

    def juntar(self, izq, der):
        f = self.f
        if izq == " ":
            return der
        if der == " ":
            return izq
        if self.ancho_anterior < 2 or self.ancho_actual < 2:
            return None
        if not f.modo & _SM_SMUSH:
            return None
        if not f.modo & 63:
            if izq == f.hardblank:
                return der
            if der == f.hardblank:
                return izq
            return der
        if f.modo & _SM_HARDBLANK and izq == f.hardblank and der == f.hardblank:
            return izq
        if izq == f.hardblank or der == f.hardblank:
            return None
        if f.modo & _SM_EQUAL and izq == der:
            return izq
        reglas = []
        if f.modo & _SM_LOWLINE:
            reglas.append(("_", "|/\\[]{}()<>"))
        if f.modo & _SM_HIERARCHY:
            reglas += [("|", "/\\[]{}()<>"), ("\\/", "[]{}()<>"), ("[]", "{}()<>"),
                       ("{}", "()<>"), ("()", "<>")]
        for a, b in reglas:
            if izq and der and izq in a and der in b:
                return der
            if izq and der and der in a and izq in b:
                return izq
        if f.modo & _SM_PAIR and (izq + der in ("[]", "{}", "()") or der + izq in ("[]", "{}", "()")):
            return "|"
        if f.modo & _SM_BIGX:
            if izq == "/" and der == "\\":
                return "|"
            if der == "/" and izq == "\\":
                return "Y"
            if izq == ">" and der == "<":
                return "X"
        return None

    def cuanto_apretar(self, letra):
        f = self.f
        if not f.modo & (_SM_SMUSH | _SM_KERN):
            return 0
        maximo = self.ancho_actual
        for fila in range(f.alto):
            izq = self.buffer[fila]
            der = letra[fila]
            borde_izq = max(0, len(izq.rstrip(" ")) - 1)
            if borde_izq < len(izq):
                c1 = izq[borde_izq]
            else:
                borde_izq = 0
                c1 = ""
            borde_der = len(der) - len(der.lstrip(" "))
            if borde_der < len(der):
                c2 = der[borde_der]
            else:
                borde_der = len(der)
                c2 = ""
            cantidad = borde_der + len(izq) - 1 - borde_izq
            if c1 == "" or c1 == " ":
                cantidad += 1
            elif c2 != "" and self.juntar(c1, c2) is not None:
                cantidad += 1
            maximo = min(maximo, cantidad)
        return maximo

    def anadir(self, codigo):
        letra = self.f.letras[codigo]
        self.ancho_actual = self.f.anchos[codigo]
        self.max_smush = self.cuanto_apretar(letra)
        for fila in range(self.f.alto):
            izq = self.buffer[fila]
            der = letra[fila]
            for i in range(self.max_smush):
                indice = len(izq) - self.max_smush + i
                c1 = izq[indice] if 0 <= indice < len(izq) else ""
                c2 = der[i] if i < len(der) else ""
                junto = self.juntar(c1, c2)
                if 0 <= indice < len(izq) and junto is not None:
                    izq = izq[:indice] + junto + izq[indice + 1:]
            self.buffer[fila] = izq + der[self.max_smush:]
        self.ancho_anterior = self.ancho_actual


def dibujar(texto, fuente):
    """Devuelve la lista de líneas del texto dibujado con la fuente (ya cargada)."""
    lineas = []
    for trozo in str(texto).split("\n"):
        actual = _Constructor(fuente)
        for codigo in fuente.resolver(trozo):
            actual.anadir(codigo)
        for fila in actual.buffer:
            lineas.append(fila.replace(fuente.hardblank, " ").rstrip())
    return lineas
