"""
Ratón: hacer cosas con el ratón en la terminal.

Haz clic en botones, pasa el ratón por encima de cosas para resaltarlas,
y crea zonas interactivas en tu programa.

    import pantalla

    pantalla.limpiar()
    opcion = pantalla.botones(["Jugar", "Salir"], 10, 5)
    if opcion == "Jugar":
        print("¡A jugar!")

Funciona en la mayoría de terminales modernas: Windows Terminal, cmd,
PowerShell, la terminal de VS Code, y las de Linux y Mac.

Fuera de una terminal de verdad (IDLE, Thonny sin terminal...) no hay ratón:
botones() y bucle() te dejan elegir escribiendo el número, y esperar_clic()
devuelve None.
"""

import atexit
import os
import sys

from . import terminal as _t
from .terminal import CSI, _es_terminal, _estado, _salida, mostrar_cursor, ocultar_cursor, tamano
from .texto import escribir

_raton = {
    "activo": False,
    "hover": False,
    "modo_anterior_windows": None,
    "modo_teclas_nuestro": False,
    "posicion": None,
    "clics": [],
    "fuente": None,
}

_ENABLE_MOUSE_INPUT = 0x0010
_ENABLE_QUICK_EDIT_MODE = 0x0040
_ENABLE_EXTENDED_FLAGS = 0x0080
_ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200

_KEY_EVENT = 0x0001
_MOUSE_EVENT = 0x0002
_MOUSE_MOVED = 0x0001
_DOUBLE_CLICK = 0x0002

_TECLAS_WINDOWS = {
    0x26: "arriba", 0x28: "abajo", 0x25: "izquierda", 0x27: "derecha",
    0x0D: "enter", 0x1B: "esc", 0x09: "tab", 0x08: "borrar",
    0x24: "inicio", 0x23: "fin", 0x21: "repag", 0x22: "avpag",
    0x2E: "suprimir", 0x2D: "insertar",
}
_TECLAS_WINDOWS.update({0x70 + i: "f%d" % (i + 1) for i in range(12)})

_BOTON_NOMBRE = {0: "izquierdo", 1: "central", 2: "derecho"}
_MAX_GUARDADOS = 20


def _es_windows():
    return os.name == "nt"


def _hay_terminal():
    if _raton["fuente"] is not None:
        return True
    return _es_terminal(sys.stdin) and _es_terminal(sys.stdout)


def activar_raton(hover=False):
    """Activa el ratón en la terminal. Después puedes usar esperar_clic() y las demás.

        pantalla.activar_raton()            # solo clics
        pantalla.activar_raton(hover=True)  # clics y movimiento (para resaltar cosas)

    Devuelve True si hay ratón y False si no se puede (por ejemplo, en IDLE).
    Cuando acabes, llama a desactivar_raton(). Si se te olvida, se hace solo al cerrar.
    """
    if _raton["activo"]:
        if hover and not _raton["hover"]:
            _raton["hover"] = True
            if not _es_windows():
                _salida(CSI + "?1003h")
        return True
    if not _hay_terminal():
        return False
    _raton["activo"] = True
    _raton["hover"] = bool(hover)
    if _es_windows():
        _activar_raton_windows()
    else:
        from .teclado import _activar_modo_teclas, _modo
        _raton["modo_teclas_nuestro"] = _modo["original"] is None
        _activar_modo_teclas()
        _salida(CSI + "?1000h" + CSI + "?1002h" + (CSI + "?1003h" if hover else "") + CSI + "?1006h")
    return True


def desactivar_raton():
    """Desactiva el ratón. La terminal vuelve a funcionar normal."""
    if not _raton["activo"]:
        return
    _raton["activo"] = False
    if _es_windows():
        _desactivar_raton_windows()
    else:
        _salida((CSI + "?1003l" if _raton["hover"] else "") + CSI + "?1002l" + CSI + "?1006l" + CSI + "?1000l")
        _drenar_unix()
        if _raton["modo_teclas_nuestro"]:
            from .teclado import _desactivar_modo_teclas
            _desactivar_modo_teclas()
        _raton["modo_teclas_nuestro"] = False
    _raton["hover"] = False
    _raton["posicion"] = None
    del _raton["clics"][:]


def _activar_raton_windows():
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        stdin = kernel32.GetStdHandle(-10)
        modo = ctypes.c_uint32()
        if kernel32.GetConsoleMode(stdin, ctypes.byref(modo)):
            _raton["modo_anterior_windows"] = modo.value
            kernel32.SetConsoleMode(stdin, _modo_windows_con_raton(modo.value))
    except Exception:
        pass


def _modo_windows_con_raton(modo):
    nuevo = modo | _ENABLE_MOUSE_INPUT | _ENABLE_EXTENDED_FLAGS
    # con la edicion rapida puesta el clic selecciona texto y no llega al programa
    return nuevo & ~(_ENABLE_QUICK_EDIT_MODE | _ENABLE_VIRTUAL_TERMINAL_INPUT)


def _desactivar_raton_windows():
    if _raton["modo_anterior_windows"] is None:
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        stdin = kernel32.GetStdHandle(-10)
        kernel32.SetConsoleMode(stdin, _raton["modo_anterior_windows"] | _ENABLE_EXTENDED_FLAGS)
    except Exception:
        pass
    _raton["modo_anterior_windows"] = None


def _al_salir_raton():
    if _raton["activo"]:
        try:
            desactivar_raton()
        except Exception:
            pass


atexit.register(_al_salir_raton)


def _evento_raton(codigo, x, y, soltar=False):
    if x < 1 or y < 1 or codigo & (64 | 128):
        return None
    boton = codigo & 3
    if codigo & 32:
        return {"tipo": "movimiento", "x": x, "y": y, "boton": _BOTON_NOMBRE.get(boton)}
    if soltar or boton == 3:
        return None
    return {"tipo": "clic", "x": x, "y": y, "boton": _BOTON_NOMBRE[boton]}


def _decodificar_unix(datos):
    """Traduce los bytes de UNA secuencia (ver teclado._leer_secuencia_unix) a un evento."""
    from .teclado import _traducir_caracter, _traducir_unix

    if not datos:
        return None
    if datos.startswith(b"\x1b[<"):
        final = datos[-1:]
        if final not in (b"M", b"m"):
            return None
        partes = datos[3:-1].split(b";")
        if len(partes) != 3:
            return None
        try:
            codigo, x, y = (int(p) for p in partes)
        except ValueError:
            return None
        return _evento_raton(codigo, x, y, soltar=final == b"m")
    if datos.startswith(b"\x1b[M") and len(datos) == 6:
        return _evento_raton(datos[3] - 32, datos[4] - 32, datos[5] - 32)
    if datos[:1] == b"\x1b":
        return {"tipo": "tecla", "tecla": _traducir_unix(datos)}
    return {"tipo": "tecla", "tecla": _traducir_caracter(datos.decode("utf-8", "replace"))}


def _traducir_registro_windows(registro, origen=(0, 0)):
    """Traduce un INPUT_RECORD de la consola de Windows a un evento (o None si no interesa).

    origen: esquina de arriba a la izquierda de la ventana dentro del búfer de la consola,
    porque Windows da la posición del ratón en el búfer y gotoxy usa la de la ventana.
    """
    from .teclado import _traducir_caracter

    if registro.EventType == _KEY_EVENT:
        ev = registro.Event.KeyEvent
        if not ev.bKeyDown:
            return None
        if ev.wVirtualKeyCode in _TECLAS_WINDOWS:
            return {"tipo": "tecla", "tecla": _TECLAS_WINDOWS[ev.wVirtualKeyCode]}
        if not ev.uChar or ev.uChar == "\x00":
            return None
        if ev.uChar == "\x03":
            raise KeyboardInterrupt
        return {"tipo": "tecla", "tecla": _traducir_caracter(ev.uChar)}

    if registro.EventType == _MOUSE_EVENT:
        ev = registro.Event.MouseEvent
        x = ev.dwMousePosition.X - origen[0] + 1
        y = ev.dwMousePosition.Y - origen[1] + 1
        flags = ev.dwEventFlags
        pulsado = None
        for bit, nombre in ((0x0001, "izquierdo"), (0x0002, "derecho"), (0x0004, "central")):
            if ev.dwButtonState & bit:
                pulsado = nombre
                break
        if flags == _MOUSE_MOVED:
            return {"tipo": "movimiento", "x": x, "y": y, "boton": pulsado}
        if flags in (0, _DOUBLE_CLICK) and pulsado:
            return {"tipo": "clic", "x": x, "y": y, "boton": pulsado}
    return None


_tipos_windows = {}


def _estructuras_windows():
    if _tipos_windows:
        return _tipos_windows
    import ctypes
    import ctypes.wintypes as w

    class COORD(ctypes.Structure):
        _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

    class SMALL_RECT(ctypes.Structure):
        _fields_ = [("Left", ctypes.c_short), ("Top", ctypes.c_short),
                    ("Right", ctypes.c_short), ("Bottom", ctypes.c_short)]

    class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
        _fields_ = [("dwSize", COORD), ("dwCursorPosition", COORD), ("wAttributes", w.WORD),
                    ("srWindow", SMALL_RECT), ("dwMaximumWindowSize", COORD)]

    class KEY_EVENT_RECORD(ctypes.Structure):
        _fields_ = [("bKeyDown", w.BOOL), ("wRepeatCount", w.WORD), ("wVirtualKeyCode", w.WORD),
                    ("wVirtualScanCode", w.WORD), ("uChar", ctypes.c_wchar),
                    ("dwControlKeyState", w.DWORD)]

    class MOUSE_EVENT_RECORD(ctypes.Structure):
        _fields_ = [("dwMousePosition", COORD), ("dwButtonState", w.DWORD),
                    ("dwControlKeyState", w.DWORD), ("dwEventFlags", w.DWORD)]

    class EVENT_UNION(ctypes.Union):
        _fields_ = [("KeyEvent", KEY_EVENT_RECORD), ("MouseEvent", MOUSE_EVENT_RECORD)]

    class INPUT_RECORD(ctypes.Structure):
        _fields_ = [("EventType", w.WORD), ("Event", EVENT_UNION)]

    _tipos_windows.update(COORD=COORD, INPUT_RECORD=INPUT_RECORD, KEY_EVENT_RECORD=KEY_EVENT_RECORD,
                          MOUSE_EVENT_RECORD=MOUSE_EVENT_RECORD,
                          CONSOLE_SCREEN_BUFFER_INFO=CONSOLE_SCREEN_BUFFER_INFO)
    return _tipos_windows


def _origen_ventana_windows(kernel32):
    import ctypes
    info = _estructuras_windows()["CONSOLE_SCREEN_BUFFER_INFO"]()
    if kernel32.GetConsoleScreenBufferInfo(kernel32.GetStdHandle(-11), ctypes.byref(info)):
        return info.srWindow.Left, info.srWindow.Top
    return 0, 0


def _leer_evento_windows(espera=True):
    import ctypes
    import ctypes.wintypes as w

    kernel32 = ctypes.windll.kernel32
    stdin = kernel32.GetStdHandle(-10)
    registro = _estructuras_windows()["INPUT_RECORD"]()
    leidos = w.DWORD()
    pendientes = w.DWORD()

    while True:
        if espera:
            if kernel32.WaitForSingleObject(stdin, 100) != 0:
                continue
        else:
            if not kernel32.GetNumberOfConsoleInputEvents(stdin, ctypes.byref(pendientes)):
                raise EOFError
            if pendientes.value == 0:
                return None
        if not kernel32.ReadConsoleInputW(stdin, ctypes.byref(registro), 1, ctypes.byref(leidos)):
            raise EOFError
        if leidos.value == 0:
            continue
        if registro.EventType == _MOUSE_EVENT:
            evento = _traducir_registro_windows(registro, _origen_ventana_windows(kernel32))
        else:
            evento = _traducir_registro_windows(registro)
        if evento is not None:
            return evento


def _leer_evento_unix(espera=True):
    import select
    import termios
    import tty

    from .teclado import _leer_secuencia_unix, _modo

    fd = sys.stdin.fileno()

    def hay_datos(segundos):
        return bool(select.select([fd], [], [], segundos)[0])

    def leer(n):
        return os.read(fd, n)

    ya_estaba = _modo["original"] is not None
    if not ya_estaba:
        viejo = termios.tcgetattr(fd)
        tty.setcbreak(fd, termios.TCSANOW)
    try:
        if not espera and not hay_datos(0):
            return None
        datos = _leer_secuencia_unix(leer, hay_datos)
        if not datos:
            raise EOFError
        return _decodificar_unix(datos)
    finally:
        if not ya_estaba:
            termios.tcsetattr(fd, termios.TCSADRAIN, viejo)


def _drenar_unix():
    if _raton["fuente"] is not None or not _hay_terminal():
        return
    from .teclado import _guardar_tecla_pendiente
    try:
        for _ in range(100):
            ev = _leer_evento_unix(espera=False)
            if ev is None:
                return
            if ev["tipo"] == "tecla":
                _guardar_tecla_pendiente(ev["tecla"])
    except (OSError, EOFError, ValueError):
        pass


def _guardar_evento_unix(datos):
    _apuntar(_decodificar_unix(datos))


def _es_arrastre(evento):
    return evento["tipo"] == "movimiento" and evento.get("boton") is not None


def _guardar(evento):
    cola = _raton["clics"]
    if len(cola) >= _MAX_GUARDADOS:
        for i, guardado in enumerate(cola):
            if guardado["tipo"] == "movimiento":
                del cola[i]
                break
        else:
            return
    cola.append(evento)


def _apuntar(evento):
    if evento and evento["tipo"] in ("movimiento", "clic"):
        _raton["posicion"] = (evento["x"], evento["y"])
        if evento["tipo"] == "clic" or _es_arrastre(evento):
            _guardar(evento)


def _leer_evento(espera=True):
    """Siguiente evento, o None si espera=False y no hay nada. EOFError si se cierra la entrada."""
    if _raton["fuente"] is not None:
        evento = _raton["fuente"](espera)
    elif _es_windows():
        evento = _leer_evento_windows(espera)
    else:
        evento = _leer_evento_unix(espera)
    if evento and evento["tipo"] in ("movimiento", "clic"):
        _raton["posicion"] = (evento["x"], evento["y"])
    return evento


def _siguiente_evento():
    if _raton["clics"]:
        return _raton["clics"].pop(0)
    return _leer_evento(espera=True)


def _sin_esperar(sirve):
    from .teclado import _guardar_tecla_pendiente
    try:
        for _ in range(200):
            ev = _leer_evento(espera=False)
            if ev is None:
                return None
            if sirve(ev):
                return ev
            if ev["tipo"] == "tecla":
                _guardar_tecla_pendiente(ev["tecla"])
            elif ev["tipo"] == "clic":
                _guardar(ev)
    except EOFError:
        return None
    return None


def _quiero(arrastrar):
    if arrastrar:
        return lambda ev: ev["tipo"] == "clic" or _es_arrastre(ev)
    return lambda ev: ev["tipo"] == "clic"


def _de_la_cola(sirve):
    cola = _raton["clics"]
    while cola:
        ev = cola.pop(0)
        if sirve(ev):
            return ev
    return None


class Clic(tuple):
    """Lo que dan esperar_clic() y leer_raton(): (x, y, boton), y además .arrastrando,
    que es True si llega por mover el ratón con el botón pulsado (y False en un clic)."""
    arrastrando = False


def _como_tupla(evento):
    clic = Clic((evento["x"], evento["y"], evento["boton"]))
    clic.arrastrando = evento["tipo"] == "movimiento"
    return clic


def esperar_clic(arrastrar=False):
    """Espera a que hagas clic con el ratón y te dice dónde y con qué botón.

    Devuelve (x, y, boton). El botón puede ser "izquierdo", "derecho" o "central".
    Las posiciones empiezan en 1, como en gotoxy.

        x, y, boton = pantalla.esperar_clic()
        pantalla.escribir("Has hecho clic en %d, %d" % (x, y), 1, 1)

    Con arrastrar=True también vuelve cuando mueves el ratón con el botón pulsado
    (mira leer_raton()). Si el ratón no estaba activado, lo activa mientras espera.
    Fuera de una terminal de verdad (IDLE) no hay ratón y devuelve None.
    """
    estaba = _raton["activo"]
    if not activar_raton():
        return None
    sirve = _quiero(arrastrar)
    try:
        while True:
            ev = _de_la_cola(sirve) or _leer_evento(espera=True)
            if ev and sirve(ev):
                return _como_tupla(ev)
    except EOFError:
        return None
    finally:
        if not estaba:
            desactivar_raton()


def leer_raton(arrastrar=False):
    """Mira si hay un clic del ratón SIN esperar. Devuelve (x, y, boton) o None.

    Como tecla_pulsada() pero para el ratón. Útil en bucles de juegos:

        pantalla.activar_raton()
        while True:
            clic = pantalla.leer_raton()
            if clic:
                x, y, boton = clic
                pantalla.punto(x, y, "X", color="rojo")
            if pantalla.tecla_pulsada() == "esc":
                break
            pantalla.pausa(0.05)

    Para pintar arrastrando (como un lápiz), usa arrastrar=True: también te da
    (x, y, boton) por cada casilla que pisas con el botón pulsado.

        clic = pantalla.leer_raton(arrastrar=True)
        if clic:
            pantalla.punto(clic[0], clic[1], "█")   # clic.arrastrando: True si es arrastrando

    Necesitas llamar a activar_raton() antes. Las teclas que se pulsen mientras
    tanto no se pierden: te las da tecla_pulsada().
    """
    if not _raton["activo"]:
        return None
    sirve = _quiero(arrastrar)
    ev = _de_la_cola(sirve) or _sin_esperar(sirve)
    return _como_tupla(ev) if ev else None


def posicion_raton():
    """Devuelve (x, y) de dónde está el ratón, o None si todavía no se sabe.

    Necesitas activar_raton(hover=True) para que funcione.

        pantalla.activar_raton(hover=True)
        pos = pantalla.posicion_raton()
        if pos:
            x, y = pos

    Los clics que pasen mientras tanto no se pierden: luego te los da leer_raton().
    """
    if not _raton["activo"] or not _raton["hover"]:
        return None
    _sin_esperar(lambda ev: False)
    return _raton["posicion"]


def zona(x, y, ancho, alto, al_clic=None, al_hover=None, al_salir=None):
    """Crea una zona interactiva (un rectángulo invisible que reacciona al ratón).

        def al_pulsar():
            pantalla.mensaje("¡Pulsado!")

        z = pantalla.zona(10, 5, 20, 3, al_clic=al_pulsar)
        pantalla.bucle([z])

    - al_clic: se llama cuando haces clic dentro.
    - al_hover: se llama cuando el ratón entra.
    - al_salir: se llama cuando el ratón sale.
    """
    return {
        "x": x, "y": y, "ancho": ancho, "alto": alto,
        "al_clic": al_clic, "al_hover": al_hover, "al_salir": al_salir,
        "_dentro": False,
    }


def _en_zona(z, x, y):
    return z["x"] <= x < z["x"] + z["ancho"] and z["y"] <= y < z["y"] + z["alto"]


def boton(texto, x, y, color="blanco", fondo="azul", color_hover="negro",
          fondo_hover="amarillo", al_clic=None):
    """Dibuja un botón que se puede pulsar con el ratón.

        def saludar():
            pantalla.mensaje("¡Hola!")

        btn = pantalla.boton("Pulsar aquí", 10, 5, al_clic=saludar)
        pantalla.bucle([btn])

    El botón cambia de color cuando pasas el ratón por encima.
    Devuelve una zona que puedes usar con bucle().
    """
    etiqueta = " %s " % texto

    def dibujar(resaltado=False):
        c = color_hover if resaltado else color
        f = fondo_hover if resaltado else fondo
        escribir(etiqueta, x, y, color=c, fondo=f, negrita=resaltado)

    dibujar(False)
    z = zona(x, y, len(etiqueta), 1, al_clic=al_clic,
             al_hover=lambda: dibujar(True), al_salir=lambda: dibujar(False))
    z["_dibujar"] = dibujar
    z["_texto"] = str(texto)
    return z


class _ModoTeclas(object):
    def __enter__(self):
        from .teclado import _activar_modo_teclas, _modo
        self.ya_estaba = _modo["original"] is not None
        _activar_modo_teclas()
        self.cursor_oculto = _estado["cursor_oculto"]
        ocultar_cursor()
        return self

    def __exit__(self, *error):
        from .teclado import _desactivar_modo_teclas
        if not self.ya_estaba:
            _desactivar_modo_teclas()
        if not self.cursor_oculto:
            mostrar_cursor()
        return False


def _vale(resultado):
    return resultado is not None and resultado is not False


def _elegir_por_numero(textos):
    for i, texto in enumerate(textos, 1):
        print("  %d) %s" % (i, texto))
    while True:
        try:
            respuesta = input("Escribe el número (Enter para salir): ").strip()
        except EOFError:
            return None
        if not respuesta:
            return None
        if respuesta.isdigit() and 1 <= int(respuesta) <= len(textos):
            return int(respuesta) - 1
        for i, texto in enumerate(textos):
            if respuesta.lower() == texto.lower():
                return i
        print("No hay esa opción.")


def bucle(zonas, al_tecla=None):
    """Bucle de eventos: lee el ratón y el teclado y llama a lo que toque.

    Pásale una lista de zonas (hechas con zona() o boton()). Acaba cuando:
    - al_clic o al_tecla devuelven algo que no sea None ni False (y bucle lo devuelve)
    - se pulsa Esc (si no hay al_tecla)

        btn1 = pantalla.boton("Aceptar", 10, 10, al_clic=lambda: "aceptar")
        btn2 = pantalla.boton("Cancelar", 25, 10, al_clic=lambda: "cancelar")
        eleccion = pantalla.bucle([btn1, btn2])

    Con al_tecla puedes responder al teclado a la vez:

        def mi_tecla(t):
            if t == "q":
                return "salir"
        pantalla.bucle([btn1], al_tecla=mi_tecla)
    """
    try:
        return _bucle(zonas, al_tecla)
    except UnboundLocalError as error:
        raise _t._explicar_global(error, "bucle") from error


def _bucle(zonas, al_tecla):
    from .teclado import _como_tecla

    estaba = _raton["activo"]
    if not activar_raton(hover=True):
        pulsables = [z for z in zonas if z.get("al_clic")]
        textos = [z.get("_texto") or "Zona %d" % (i + 1) for i, z in enumerate(pulsables)]
        while pulsables:
            elegida = _elegir_por_numero(textos)
            if elegida is None:
                return None
            resultado = pulsables[elegida]["al_clic"]()
            if _vale(resultado):
                return resultado
        return None
    try:
        with _ModoTeclas():
            while True:
                ev = _siguiente_evento()
                if ev is None:
                    continue
                if ev["tipo"] == "tecla":
                    if al_tecla:
                        resultado = al_tecla(_como_tecla(ev["tecla"]))
                        if _vale(resultado):
                            return resultado
                    elif ev["tecla"] == "esc":
                        return None
                elif ev["tipo"] == "movimiento":
                    for z in zonas:
                        dentro = _en_zona(z, ev["x"], ev["y"])
                        if dentro and not z.get("_dentro", False):
                            z["_dentro"] = True
                            if z.get("al_hover"):
                                z["al_hover"]()
                        elif not dentro and z.get("_dentro", False):
                            z["_dentro"] = False
                            if z.get("al_salir"):
                                z["al_salir"]()
                elif ev["tipo"] == "clic":
                    for z in zonas:
                        if _en_zona(z, ev["x"], ev["y"]) and z.get("al_clic"):
                            resultado = z["al_clic"]()
                            if _vale(resultado):
                                return resultado
    except EOFError:
        return None
    finally:
        if not estaba:
            desactivar_raton()


def botones(opciones, x=None, y=None, horizontal=True, color="blanco", fondo="azul",
            color_hover="negro", fondo_hover="amarillo", separacion=2):
    """Enseña varios botones y espera a que hagas clic en uno. Devuelve su texto.

        opcion = pantalla.botones(["Jugar", "Opciones", "Salir"], 10, 5)
        if opcion == "Jugar":
            ...

    También vale el teclado: flechas (o Tab) para moverte, Enter para elegir,
    o el número del botón (1, 2, 3...). Esc sale sin elegir (devuelve None).

    - horizontal: True para ponerlos en fila, False para ponerlos en columna.
    - separacion: espacio entre los botones (en columna, filas de separación + 1).
    """
    opciones = [str(o) for o in opciones]
    if not opciones:
        raise ValueError("botones: necesito al menos una opción")

    estaba = _raton["activo"]
    if not activar_raton(hover=True):
        elegida = _elegir_por_numero(opciones)
        return None if elegida is None else opciones[elegida]

    paso = max(1, separacion)
    ancho_p, alto_p = tamano()
    anchos = [len(o) + 2 for o in opciones]
    if x is None:
        if horizontal:
            total = sum(anchos) + separacion * (len(opciones) - 1)
            x = max(1, (ancho_p - total) // 2 + 1)
        else:
            x = max(1, (ancho_p - max(anchos)) // 2 + 1)
    if y is None:
        if horizontal:
            y = max(1, alto_p // 2)
        else:
            y = max(1, (alto_p - (len(opciones) - 1) * paso) // 2 + 1)

    zonas = []
    bx, by = x, y
    for ancho_btn in anchos:
        zonas.append(zona(bx, by, ancho_btn, 1))
        if horizontal:
            bx += ancho_btn + separacion
        else:
            by += paso

    def pintar(elegido):
        for i, z in enumerate(zonas):
            resaltado = i == elegido
            escribir(" %s " % opciones[i], z["x"], z["y"],
                     color=color_hover if resaltado else color,
                     fondo=fondo_hover if resaltado else fondo, negrita=resaltado)

    elegido = 0
    try:
        with _ModoTeclas():
            pintar(elegido)
            while True:
                ev = _siguiente_evento()
                if ev is None:
                    continue
                if ev["tipo"] == "tecla":
                    t = ev["tecla"]
                    if t == "esc":
                        return None
                    if t in ("enter", "espacio"):
                        return opciones[elegido]
                    if t.isdigit() and 1 <= int(t) <= len(opciones):
                        return opciones[int(t) - 1]
                    nuevo = elegido
                    if t in ("derecha", "abajo", "tab"):
                        nuevo = (elegido + 1) % len(opciones)
                    elif t in ("izquierda", "arriba"):
                        nuevo = (elegido - 1) % len(opciones)
                    elif t == "inicio":
                        nuevo = 0
                    elif t == "fin":
                        nuevo = len(opciones) - 1
                    if nuevo != elegido:
                        elegido = nuevo
                        pintar(elegido)
                elif ev["tipo"] == "movimiento":
                    for i, z in enumerate(zonas):
                        if _en_zona(z, ev["x"], ev["y"]) and i != elegido:
                            elegido = i
                            pintar(elegido)
                elif ev["tipo"] == "clic":
                    for i, z in enumerate(zonas):
                        if _en_zona(z, ev["x"], ev["y"]):
                            return opciones[i]
    except EOFError:
        return None
    finally:
        if not estaba:
            desactivar_raton()
