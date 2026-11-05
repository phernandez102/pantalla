"""
Leer el teclado: teclas sueltas (flechas incluidas), textos y números.

tecla() devuelve un texto con el nombre de la tecla:
  - letras y números tal cual: "a", "A", "ñ", "7", "?"
  - "arriba", "abajo", "izquierda", "derecha"
  - "enter", "espacio", "esc", "tab", "borrar", "suprimir", "insertar"
  - "inicio", "fin", "repag", "avpag", "f1" ... "f12"
  - "ctrl+a", "alt+x"...
"""

import atexit
import getpass
import os
import re
import sys

try:
    # en linux y mac con esto las flechas funcionan dentro de pedir()
    import readline  # noqa: F401
except ImportError:
    pass

from .colores import estilo as _estilo_ansi
from .terminal import _es_terminal, _estado, _fin_de_estilo, _juego, _salida
from .texto import escribir
from .terminal import mostrar_cursor, ocultar_cursor

_modo = {"original": None}

_ESPECIALES = {
    "\r": "enter",
    "\n": "enter",
    " ": "espacio",
    "\t": "tab",
    "\x7f": "borrar",
    "\x08": "borrar",
    "\x1b": "esc",
}

_WINDOWS = {
    "H": "arriba", "P": "abajo", "K": "izquierda", "M": "derecha",
    "G": "inicio", "O": "fin", "I": "repag", "Q": "avpag",
    "R": "insertar", "S": "suprimir",
    ";": "f1", "<": "f2", "=": "f3", ">": "f4", "?": "f5",
    "@": "f6", "A": "f7", "B": "f8", "C": "f9", "D": "f10",
    "\x85": "f11", "\x86": "f12",
}

_LETRA_FINAL = {
    "A": "arriba", "B": "abajo", "C": "derecha", "D": "izquierda",
    "H": "inicio", "F": "fin", "P": "f1", "Q": "f2", "R": "f3", "S": "f4",
}

_NUMERO_TILDE = {
    "1": "inicio", "2": "insertar", "3": "suprimir", "4": "fin", "5": "repag",
    "6": "avpag", "7": "inicio", "8": "fin", "11": "f1", "12": "f2", "13": "f3",
    "14": "f4", "15": "f5", "17": "f6", "18": "f7", "19": "f8", "20": "f9",
    "21": "f10", "23": "f11", "24": "f12",
}


_SINONIMOS = {
    "intro": "enter", "return": "enter", "entrar": "enter", "\r": "enter", "\n": "enter",
    " ": "espacio", "space": "espacio", "barra espaciadora": "espacio",
    "escape": "esc", "escapar": "esc",
    "up": "arriba", "↑": "arriba", "down": "abajo", "↓": "abajo",
    "left": "izquierda", "←": "izquierda", "izq": "izquierda",
    "right": "derecha", "→": "derecha", "der": "derecha",
    "backspace": "borrar", "retroceso": "borrar", "delete": "suprimir", "supr": "suprimir",
    "tabulador": "tab", "\t": "tab", "home": "inicio", "end": "fin",
    "pageup": "repag", "re pag": "repag", "pagedown": "avpag", "av pag": "avpag",
    "insert": "insertar", "ins": "insertar",
}


def _canon(nombre):
    """El nombre de siempre de una tecla: "Intro" -> "enter", "Flecha arriba" -> "arriba"."""
    import unicodedata

    if len(nombre) <= 1:
        return _SINONIMOS.get(nombre, nombre.lower())
    n = unicodedata.normalize("NFD", nombre.strip().lower())
    n = "".join(c for c in n if unicodedata.category(c) != "Mn").replace("_", " ").replace("-", " ")
    if n.startswith("flecha "):
        n = n[len("flecha "):]
    n = n.replace("tecla ", "", 1) if n.startswith("tecla ") else n
    return _SINONIMOS.get(n, n)


class Tecla(str):
    """El nombre de una tecla ("enter", "a", "arriba"...). Es un texto normal, pero al
    compararlo no le importan las mayúsculas ni el nombre que uses: t == "Intro",
    t == "ENTER" y t == "enter" son lo mismo; t == "A" vale para la a."""

    def __eq__(self, otro):
        if isinstance(otro, str):
            return str.__eq__(self, otro) or _canon(str(self)) == _canon(otro)
        return NotImplemented

    def __ne__(self, otro):
        igual = self.__eq__(otro)
        return igual if igual is NotImplemented else not igual

    __hash__ = str.__hash__


def _como_tecla(nombre):
    return None if nombre is None else Tecla(nombre)


def _traducir_caracter(c):
    if c in _ESPECIALES:
        return _ESPECIALES[c]
    if len(c) == 1 and ord(c) < 32:
        return "ctrl+" + chr(ord(c) + 96)
    return c


def _traducir_windows(leer):
    c = leer()
    if c in ("\x00", "\xe0"):
        return _WINDOWS.get(leer(), "desconocida")
    if c == "\x03":
        raise KeyboardInterrupt
    return _traducir_caracter(c)


def _traducir_unix(datos):
    if datos is None:
        return None
    if datos == b"\x1b":
        return "esc"
    if datos.startswith(b"\x1b[[") and len(datos) == 4:
        return {"A": "f1", "B": "f2", "C": "f3", "D": "f4", "E": "f5"}.get(chr(datos[3]), "desconocida")
    if datos[:2] in (b"\x1b[", b"\x1bO") and len(datos) >= 3:
        final = chr(datos[-1])
        medio = datos[2:-1].decode("ascii", "ignore")
        if final == "~":
            return _NUMERO_TILDE.get(medio.split(";")[0], "desconocida")
        return _LETRA_FINAL.get(final, "desconocida")
    if datos[:1] == b"\x1b" and len(datos) == 2:
        return "alt+" + _traducir_caracter(chr(datos[1]))
    return _traducir_caracter(datos.decode("utf-8", "replace"))


def _hay_teclado():
    return _es_terminal(sys.stdin)


def _activar_modo_teclas():
    if os.name == "nt" or _modo["original"] is not None or not _hay_teclado():
        return
    import termios
    import tty

    fd = sys.stdin.fileno()
    _modo["original"] = termios.tcgetattr(fd)
    tty.setcbreak(fd, termios.TCSANOW)


def _desactivar_modo_teclas():
    if _modo["original"] is None:
        return
    import termios

    try:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _modo["original"])
    except Exception:
        pass
    _modo["original"] = None


atexit.register(_desactivar_modo_teclas)


def _con_teclas(funcion, volver_cursor=False):
    import functools

    @functools.wraps(funcion)
    def envoltorio(*args, **kwargs):
        ya_estaba = _modo["original"] is not None
        _activar_modo_teclas()
        if volver_cursor:
            _salida("\x1b7")
        try:
            return funcion(*args, **kwargs)
        finally:
            if volver_cursor:
                _salida("\x1b8")
            if not ya_estaba:
                _desactivar_modo_teclas()

    return envoltorio


def _ventana(funcion):
    return _con_teclas(funcion, volver_cursor=True)


_teclas_pendientes = []
_ESPERA_SECUENCIA = 0.05


def _bytes_utf8(primero):
    return 2 if primero < 0xE0 else 3 if primero < 0xF0 else 4


def _leer_secuencia_unix(leer, hay_datos):
    datos = leer(1)
    if not datos:
        return b""
    if datos != b"\x1b":
        if datos[0] >= 0xC0:
            datos += leer(_bytes_utf8(datos[0]) - 1)
        return datos
    if not hay_datos(_ESPERA_SECUENCIA):
        return datos
    datos += leer(1)
    if datos[1] >= 0xC0:
        return datos + leer(_bytes_utf8(datos[1]) - 1)
    if datos == b"\x1bO":
        if hay_datos(_ESPERA_SECUENCIA):
            datos += leer(1)
        return datos
    if datos != b"\x1b[":
        return datos
    while hay_datos(_ESPERA_SECUENCIA):
        byte = leer(1)
        if not byte:
            break
        datos += byte
        if datos == b"\x1b[[":
            continue
        if datos == b"\x1b[M":
            for _ in range(3):
                if not hay_datos(_ESPERA_SECUENCIA):
                    break
                datos += leer(1)
            break
        if 0x40 <= byte[0] <= 0x7E:
            break
    return datos


def _es_secuencia_raton(datos):
    return bool(datos) and (datos.startswith(b"\x1b[<") or (datos.startswith(b"\x1b[M") and len(datos) == 6))


def _guardar_tecla_pendiente(nombre):
    if nombre and len(_teclas_pendientes) < 32:
        _teclas_pendientes.append(nombre)


def _leer_bytes_unix(espera):
    import select
    import termios
    import tty

    fd = sys.stdin.fileno()

    def hay_mas(segundos):
        return bool(select.select([fd], [], [], segundos)[0])

    def leer(n):
        return os.read(fd, n)

    ya_estaba = _modo["original"] is not None
    if not ya_estaba:
        viejo = termios.tcgetattr(fd)
        tty.setcbreak(fd, termios.TCSANOW)
    try:
        if not espera and not hay_mas(0):
            return None
        return _leer_secuencia_unix(leer, hay_mas)
    finally:
        if not ya_estaba:
            termios.tcsetattr(fd, termios.TCSADRAIN, viejo)


def tecla():
    """Espera a que pulses una tecla y te dice cuál ha sido (no hace falta Enter).

        t = pantalla.tecla()
        if t == "arriba":
            y = y - 1
        elif t == "q":
            print("Adiós")

    Nombres especiales: "arriba", "abajo", "izquierda", "derecha", "enter",
    "espacio", "esc", "tab", "borrar", "suprimir", "f1"... Las letras salen tal cual.
    Al comparar no importan las mayúsculas: t == "Intro" o t == "A" también valen.
    """
    return _como_tecla(_tecla())


def _tecla():
    sys.stdout.flush()
    if _teclas_pendientes:
        return _teclas_pendientes.pop(0)
    if _juego["mostrar"] is not None:
        _juego["mostrar"]()
    if not _hay_teclado():
        linea = input()
        return linea.strip() or "enter"
    if os.name == "nt":
        import msvcrt

        return _traducir_windows(msvcrt.getwch)
    while True:
        datos = _leer_bytes_unix(True)
        if not _es_secuencia_raton(datos):
            return _traducir_unix(datos)
        from .raton import _guardar_evento_unix
        _guardar_evento_unix(datos)


def tecla_pulsada():
    """Mira si hay una tecla pulsada SIN esperar. Devuelve la tecla o None.

    Es lo que se usa en los juegos, para que las cosas se sigan moviendo
    aunque no pulses nada:

        while True:
            t = pantalla.tecla_pulsada()
            if t == "izquierda":
                x = x - 1
            ...
            pantalla.pausa(0.1)
    """
    return _como_tecla(_tecla_pulsada())


def _tecla_pulsada():
    sys.stdout.flush()
    if _teclas_pendientes:
        return _teclas_pendientes.pop(0)
    if _juego["teclas"] is not None:
        return _juego["teclas"].pop(0) if _juego["teclas"] else None
    if not _hay_teclado():
        return None
    if os.name == "nt":
        import msvcrt

        if not msvcrt.kbhit():
            return None
        return _traducir_windows(msvcrt.getwch)
    _activar_modo_teclas()
    datos = _leer_bytes_unix(False)
    if _es_secuencia_raton(datos):
        from .raton import _guardar_evento_unix
        _guardar_evento_unix(datos)
        return None
    return _traducir_unix(datos)


def vaciar_teclado():
    """Olvida las teclas que se hayan pulsado y no se hayan leído todavía."""
    del _teclas_pendientes[:]
    for _ in range(1000):
        if tecla_pulsada() is None:
            return


def esperar(mensaje="Pulsa una tecla para continuar...", x=None, y=None, color=None):
    """Escribe un mensaje y espera a que pulses una tecla. Devuelve la tecla.

        pantalla.esperar()
        pantalla.esperar("Pulsa cualquier tecla para empezar", 10, 20, color="gris")
    """
    if mensaje:
        escribir(mensaje, x, y, color=color)
    return tecla()


def pedir(pregunta="", x=None, y=None, color=None, color_respuesta=None):
    """Hace una pregunta y devuelve lo que escribas (al pulsar Enter), como input().

        nombre = pantalla.pedir("¿Cómo te llamas? ")
        nombre = pantalla.pedir("Nombre: ", 10, 5, color="cian")

    Devuelve siempre un texto, sin espacios al principio ni al final.
    """
    escribir(pregunta, x, y, color=color)
    if _juego["mostrar"] is not None:
        _juego["mostrar"]()
    estaba_oculto = _estado["cursor_oculto"]
    en_modo_teclas = _modo["original"] is not None
    if estaba_oculto:
        mostrar_cursor()
    if en_modo_teclas:
        _desactivar_modo_teclas()
    if color_respuesta is not None:
        _salida(_estilo_ansi(color_respuesta))
    try:
        respuesta = input()
    finally:
        if color_respuesta is not None:
            _salida(_fin_de_estilo())
        if en_modo_teclas:
            _activar_modo_teclas()
        if estaba_oculto:
            ocultar_cursor()
    respuesta = _CODIGOS_RAROS.sub("", respuesta)
    return respuesta.strip()


_CODIGOS_RAROS = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1bO.|\x1b|[\x00-\x08\x0b-\x1f\x7f]")


def pedir_numero(pregunta="Escribe un número: ", x=None, y=None, minimo=None, maximo=None,
                 decimales=False, color=None):
    """Pide un número y no para hasta que le escribas uno que valga.

        edad = pantalla.pedir_numero("¿Cuántos años tienes? ", minimo=0, maximo=120)
        precio = pantalla.pedir_numero("Precio: ", decimales=True)

    Con decimales=False devuelve un int; con decimales=True, un float (vale 2,5 o 2.5).
    """
    error_anterior = ""
    while True:
        texto = pedir(pregunta, x, y, color=color)
        error = None
        try:
            if decimales:
                numero = float(texto.replace(",", "."))
            else:
                numero = int(texto)
        except ValueError:
            if decimales:
                error = "Eso no es un número. Prueba otra vez."
            else:
                error = "Escribe un número entero (sin decimales). Prueba otra vez."
        else:
            if minimo is not None and numero < minimo:
                error = "Tiene que ser como mínimo %s." % minimo
            elif maximo is not None and numero > maximo:
                error = "Tiene que ser como máximo %s." % maximo

        if y is None:
            if error is None:
                return numero
            escribir(error, color="rojo", nueva_linea=True)
            continue

        columna = (x if x is not None else 1)
        if error_anterior:
            escribir(" " * len(error_anterior), columna, y + 1)
        if error is None:
            escribir("", columna + len(str(pregunta)), y)
            return numero
        escribir(" " * (len(texto) + 2), columna + len(str(pregunta)), y)
        escribir(error, columna, y + 1, color="rojo")
        error_anterior = error


def pedir_contrasena(pregunta="Contraseña: "):
    """Pide un texto sin que se vea lo que escribes (para contraseñas)."""
    sys.stdout.flush()
    return getpass.getpass(pregunta)


@_con_teclas
def confirmar(pregunta="¿Seguro? (s/n) ", x=None, y=None, color=None):
    """Hace una pregunta de sí o no. Devuelve True si pulsas 's' y False si pulsas 'n'.

        if pantalla.confirmar("¿Quieres salir? (s/n) "):
            break
    """
    escribir(pregunta, x, y, color=color)
    while True:
        t = tecla()
        if t in ("s", "S", "y", "Y"):
            escribir("sí", nueva_linea=y is None)
            return True
        if t in ("n", "N", "esc"):
            escribir("no", nueva_linea=y is None)
            return False
