"""
Lo básico de la terminal: mover el cursor, limpiar, tamaño, cursor visible...

Todo funciona con "códigos ANSI": textos especiales que empiezan por el
carácter ESC (\\x1b) y que la terminal entiende como órdenes en vez de como
letras. Por ejemplo, "\\x1b[5;10H" significa "pon el cursor en la fila 5,
columna 10". Si haces print("\\x1b[31mHola") verás "Hola" en rojo.
"""

import atexit
import os
import shutil
import sys
import threading
import time

ESC = "\x1b"
CSI = ESC + "["
RESET = CSI + "0m"

_estado = {
    "usado": False,
    "cursor_oculto": False,
    "pantalla_aparte": False,
    "avisado": False,
    "estilo": "",
}

# dibujos que se giran con el ratón (dibujar_espacio con girar=True)
_giratorios = []


# sin esto el cmd de windows enseña los codigos tal cual, tipo [31m
def _activar_ansi_en_windows():
    if os.name != "nt":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        for numero in (-11, -12):
            manejador = kernel32.GetStdHandle(numero)
            modo = ctypes.c_uint32()
            if kernel32.GetConsoleMode(manejador, ctypes.byref(modo)):
                kernel32.SetConsoleMode(manejador, modo.value | 0x0004)
    except Exception:
        pass


_activar_ansi_en_windows()


def _es_terminal(flujo):
    try:
        return flujo.isatty()
    except (AttributeError, ValueError):
        return False


def _avisar_si_no_es_terminal():
    if _estado["avisado"]:
        return
    _estado["avisado"] = True
    if os.environ.get("PANTALLA_SIN_AVISOS") or _es_terminal(sys.stdout):
        return
    sys.stderr.write(
        "[pantalla] Aviso: esto no parece una terminal de verdad (¿IDLE? ¿Thonny?).\n"
        "           Los colores y gotoxy solo funcionan en una terminal: cmd, PowerShell,\n"
        "           Windows Terminal, la terminal de VS Code o 'Ejecutar en terminal' de Thonny.\n"
    )


_juego = {"tamano": None, "mostrar": None, "teclas": None, "pintar": None}
_cerrojo = threading.RLock()


def _salida(texto):
    if not texto:
        return
    _avisar_si_no_es_terminal()
    _estado["usado"] = True
    with _cerrojo:
        try:
            sys.stdout.write(texto)
        except UnicodeEncodeError:
            codificacion = getattr(sys.stdout, "encoding", None) or "ascii"
            sys.stdout.write(texto.encode(codificacion, "replace").decode(codificacion))
        sys.stdout.flush()


_TEXTO_PRIMERO = ("escribir", "escribir_lento", "centrar", "escribir_derecha", "grande", "arte",
                  "boton", "pedir", "pedir_numero", "confirmar", "esperar")


def _entero(valor, nombre, funcion):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        pista = ""
        if isinstance(valor, str):
            try:
                float(valor.strip())
                pista = (". Es un número entre comillas, o sea un texto: quítale las comillas "
                         "(%s=%s). Si viene de input(), conviértelo con int()"
                         % (nombre, valor.strip()))
            except ValueError:
                if funcion in _TEXTO_PRIMERO:
                    pista = (". ¿Has puesto el texto al final? En %s() primero va el texto y "
                             "luego x, y: pantalla.%s(\"Hola\", 5, 3)" % (funcion, funcion))
        raise TypeError(
            "%s: '%s' tiene que ser un número, pero me has dado %r%s" % (funcion, nombre, valor, pista)
        )
    return int(valor)


def _explicar_global(error, donde):
    """Si a tu función le falta 'global', lo explica en español (si no, devuelve None)."""
    import re

    if not isinstance(error, UnboundLocalError):
        return None
    m = re.search(r"'(\w+)'", str(error))
    variable = m.group(1) if m else "esa_variable"
    return UnboundLocalError(
        "%s: tu función cambia la variable '%s', que está fuera de la función. Para poder "
        "cambiarla, escribe en la primera línea de la función:\n\n    global %s\n"
        % (donde, variable, variable))


def _en_idle():
    return "idlelib" in sys.modules and not _es_terminal(sys.stdout)


def _abrir_en_consola_si_idle():
    """En IDLE (que no es una terminal) vuelve a abrir tu programa en una ventana de cmd.

    Así el que pulsa F5 en IDLE ve su programa funcionando, en vez de letras raras.
    Solo en Windows y si el programa es un archivo. PANTALLA_NO_ABRIR=1 lo desactiva.
    """
    if not _en_idle() or os.environ.get("PANTALLA_NO_ABRIR") or os.name != "nt":
        return False
    principal = sys.modules.get("__main__")
    archivo = getattr(principal, "__file__", None)
    if not archivo or not os.path.isfile(archivo):
        return False
    import subprocess

    python = sys.executable or "python"
    carpeta, nombre = os.path.split(python)
    if nombre.lower() == "pythonw.exe" and os.path.isfile(os.path.join(carpeta, "python.exe")):
        python = os.path.join(carpeta, "python.exe")
    archivo = os.path.abspath(archivo)
    orden = 'cmd /c ""%s" "%s" & echo. & pause"' % (python, archivo)
    try:
        subprocess.Popen(orden, cwd=os.path.dirname(archivo),
                         creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0x10))
    except OSError:
        return False
    sys.stderr.write(
        "[pantalla] IDLE no es una terminal: aquí los colores y las posiciones salen como letras\n"
        "           raras. Por eso he abierto tu programa en una ventana nueva (cmd). Míralo allí.\n"
    )
    return True


def _posicion(x, y, funcion="gotoxy"):
    x = _entero(x, "x", funcion)
    y = _entero(y, "y", funcion)
    if x < 1 or y < 1:
        raise ValueError(
            "%s: las posiciones empiezan en 1 (la esquina de arriba a la izquierda es "
            "x=1, y=1). Me has dado x=%d, y=%d" % (funcion, x, y)
        )
    return x, y


def _mover(x, y):
    return "%s%d;%dH" % (CSI, y, x)


def _ayuda_que_cabe(texto, ancho):
    # si no cabe se van quitando cosas, pero "Esc salir" (la última) se queda
    trozos = texto.split(" · ")
    while len(trozos) > 2 and len(" · ".join(trozos)) > ancho:
        del trozos[-2]
    return " · ".join(trozos)[:max(0, ancho)]


def _fin_de_estilo():
    return RESET + _estado["estilo"]


def gotoxy(x, y):
    """Mueve el cursor a la columna x y la fila y.

    Las posiciones empiezan en 1: gotoxy(1, 1) es la esquina de arriba a la
    izquierda. x va hacia la derecha y y hacia abajo. Si le pasas un número
    con decimales (por ejemplo ancho() / 2) lo redondea hacia abajo.

        pantalla.gotoxy(10, 5)
        print("Estoy en la columna 10, fila 5")
    """
    x, y = _posicion(x, y)
    _salida(_mover(x, y))


ir_a = gotoxy


def limpiar():
    """Borra toda la pantalla y pone el cursor arriba a la izquierda.

    Si antes has puesto un color de fondo con poner_color(fondo="azul"),
    la pantalla entera se queda de ese color.
    """
    del _giratorios[:]
    _salida(CSI + "2J" + _mover(1, 1))


def limpiar_linea(y=None):
    """Borra una línea entera. Sin número, borra la línea donde está el cursor."""
    if y is None:
        _salida("\r" + CSI + "2K")
    else:
        x, y = _posicion(1, y, "limpiar_linea")
        _salida(_mover(1, y) + CSI + "2K")


def tamano():
    """Devuelve (ancho, alto) de la terminal, en columnas y filas."""
    if _juego["tamano"] is not None:
        return _juego["tamano"]
    medida = shutil.get_terminal_size((80, 24))
    return medida.columns, medida.lines


def ancho():
    """Cuántas columnas tiene la terminal (normalmente 80 o más)."""
    return tamano()[0]


def alto():
    """Cuántas filas tiene la terminal (normalmente 24 o más)."""
    return tamano()[1]


def centro():
    """Devuelve (x, y) del centro de la pantalla."""
    a, b = tamano()
    return (a + 1) // 2, (b + 1) // 2


def ocultar_cursor():
    """Esconde el cursor parpadeante (queda más limpio en juegos y menús)."""
    _estado["cursor_oculto"] = True
    _salida(CSI + "?25l")


def mostrar_cursor():
    """Vuelve a mostrar el cursor."""
    _estado["cursor_oculto"] = False
    _salida(CSI + "?25h")


def guardar_posicion():
    """Apunta dónde está el cursor ahora, para volver luego con volver_a_posicion()."""
    _salida(ESC + "7")


def volver_a_posicion():
    """Vuelve a donde estaba el cursor cuando llamaste a guardar_posicion()."""
    _salida(ESC + "8")


def titulo_ventana(texto):
    """Cambia el título de la ventana de la terminal."""
    _salida(ESC + "]0;" + str(texto) + "\x07")


def pitido():
    """Hace 'bip' (si la terminal tiene el sonido activado)."""
    _salida("\x07")


def pausa(segundos):
    """Espera unos segundos sin hacer nada. Vale con decimales: pausa(0.5)."""
    if isinstance(segundos, bool) or not isinstance(segundos, (int, float)) or segundos < 0:
        raise TypeError("pausa: dime cuántos segundos con un número, por ejemplo pausa(2) o "
                        "pausa(0.5). Me has dado %r" % (segundos,))
    if _juego["mostrar"] is not None:
        _juego["mostrar"]()
    sys.stdout.flush()
    # en linux y mac si no, las teclas que pulses mientras salen escritas (^[[A...)
    from .teclado import _activar_modo_teclas, _desactivar_modo_teclas, _modo
    ya_estaba = _modo["original"] is not None
    _activar_modo_teclas()
    try:
        time.sleep(segundos)
    finally:
        if not ya_estaba:
            _desactivar_modo_teclas()


def iniciar(borrar=True, cursor=False, aparte=True, titulo=None):
    """Prepara la terminal para un juego o una aplicación a pantalla completa.

    - borrar: limpia la pantalla.
    - cursor: si es False, esconde el cursor.
    - aparte: usa una "pantalla aparte"; al terminar vuelve a aparecer
      lo que había antes en la terminal, como hacen los programas de verdad.
    - titulo: cambia el título de la ventana.

    También hace que las teclas que pulses no se vean escritas en la pantalla.
    Al acabar llama a terminar() (si se te olvida, se hace solo al cerrar).
    """
    if aparte:
        _estado["pantalla_aparte"] = True
        _salida(CSI + "?1049h")
    if borrar:
        limpiar()
    if not cursor:
        ocultar_cursor()
    if titulo is not None:
        titulo_ventana(titulo)
    from . import teclado

    teclado._activar_modo_teclas()


def terminar():
    """Deja la terminal como estaba: colores normales, cursor visible, etc."""
    from . import raton, teclado

    raton.desactivar_raton()
    teclado._desactivar_modo_teclas()
    _estado["estilo"] = ""
    texto = RESET + CSI + "?25h"
    _estado["cursor_oculto"] = False
    if _estado["pantalla_aparte"]:
        _estado["pantalla_aparte"] = False
        texto = texto + CSI + "?1049l"
    else:
        texto = texto + _mover(1, alto()) + "\n"
    _salida(texto)


def _al_salir():
    if not _estado["usado"] or not _es_terminal(sys.stdout):
        return
    texto = RESET
    if _estado["cursor_oculto"]:
        texto = texto + CSI + "?25h"
    if _estado["pantalla_aparte"]:
        texto = texto + CSI + "?1049l"
    try:
        sys.stdout.write(texto)
        sys.stdout.flush()
    except Exception:
        pass


atexit.register(_al_salir)
