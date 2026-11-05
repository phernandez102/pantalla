"""Prueba de extremo a extremo del ratón en una consola REAL de Windows.

    python tests\\e2e\\raton_windows.py            (consola nueva normal)
    python tests\\e2e\\raton_windows.py --conhost  (forzando la consola clásica conhost.exe)
    python tests\\e2e\\raton_windows.py --conhost --historial  (con la ventana desplazada)

Abre escenario_raton.py en una consola nueva, se engancha a ella (AttachConsole) y le mete
eventos de verdad con WriteConsoleInputW: mover el ratón, clics y teclas. Comprueba lo que se
ve en la pantalla (letras y colores con ReadConsoleOutput...) y lo que devuelve cada función.
"""

import ctypes
import ctypes.wintypes as w
import json
import os
import subprocess
import sys
import tempfile
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "src"))

from pantalla.raton import _estructuras_windows  # noqa: E402

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.CreateFileW.restype = w.HANDLE
T = _estructuras_windows()
INPUT_RECORD, COORD = T["INPUT_RECORD"], T["COORD"]

fallos = []
pasados = []


def comprobar(nombre, condicion, detalle=""):
    (pasados if condicion else fallos).append(nombre + ("" if condicion else "  -> " + str(detalle)))
    print(("  OK   " if condicion else "  FALLO ") + nombre + ("" if condicion else "  -> " + str(detalle)))


def resultados(fichero):
    try:
        with open(fichero, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]
    except OSError:
        return []


def esperar(fichero, paso, clave="paso", segundos=10):
    final = time.time() + segundos
    while time.time() < final:
        for r in resultados(fichero):
            if r["paso"] == paso if clave == "paso" else (r["paso"] == clave and r["valor"] == paso):
                return r["valor"]
            if r["paso"] == "error":
                raise RuntimeError("el escenario ha fallado: " + r["valor"])
        time.sleep(0.02)
    raise TimeoutError("no llega el paso %r (%s)" % (paso, clave))


class Consola:
    def __init__(self):
        GENERIC_RW = 0x80000000 | 0x40000000
        SHARE_RW = 0x1 | 0x2
        self.entrada = k32.CreateFileW("CONIN$", GENERIC_RW, SHARE_RW, None, 3, 0, None)
        self.salida = k32.CreateFileW("CONOUT$", GENERIC_RW, SHARE_RW, None, 3, 0, None)

    def origen(self):
        info = T["CONSOLE_SCREEN_BUFFER_INFO"]()
        k32.GetConsoleScreenBufferInfo(self.salida, ctypes.byref(info))
        return info.srWindow.Left, info.srWindow.Top

    def texto(self, x, y, n):
        izq, arriba = self.origen()
        buf = ctypes.create_unicode_buffer(n)
        leidos = w.DWORD()
        k32.ReadConsoleOutputCharacterW(self.salida, buf, n, COORD(izq + x - 1, arriba + y - 1), ctypes.byref(leidos))
        return buf.value

    def fondos(self, x, y, n):
        izq, arriba = self.origen()
        attrs = (w.WORD * n)()
        leidos = w.DWORD()
        k32.ReadConsoleOutputAttribute(self.salida, attrs, n, COORD(izq + x - 1, arriba + y - 1), ctypes.byref(leidos))
        return {a & 0xF0 for a in attrs}

    def modo(self):
        m = w.DWORD()
        k32.GetConsoleMode(self.entrada, ctypes.byref(m))
        return m.value

    def enviar(self, registros):
        arr = (INPUT_RECORD * len(registros))(*registros)
        escritos = w.DWORD()
        if not k32.WriteConsoleInputW(self.entrada, arr, len(registros), ctypes.byref(escritos)):
            raise OSError(ctypes.get_last_error())

    def raton(self, x, y, botones=0, flags=0):
        izq, arriba = self.origen()
        r = INPUT_RECORD()
        r.EventType = 0x0002
        r.Event.MouseEvent.dwMousePosition.X = izq + x - 1
        r.Event.MouseEvent.dwMousePosition.Y = arriba + y - 1
        r.Event.MouseEvent.dwButtonState = botones
        r.Event.MouseEvent.dwEventFlags = flags
        return r

    def mover(self, x, y):
        self.enviar([self.raton(x, y, 0, 0x1)])

    def clic(self, x, y, boton=0x1):
        self.enviar([self.raton(x, y, 0, 0x1), self.raton(x, y, boton, 0), self.raton(x, y, 0, 0)])

    def tecla(self, vk, char="\x00"):
        regs = []
        for abajo in (True, False):
            r = INPUT_RECORD()
            r.EventType = 0x0001
            r.Event.KeyEvent.bKeyDown = abajo
            r.Event.KeyEvent.wRepeatCount = 1
            r.Event.KeyEvent.wVirtualKeyCode = vk
            r.Event.KeyEvent.uChar = char
            regs.append(r)
        self.enviar(regs)


def hasta(condicion, segundos=5):
    final = time.time() + segundos
    while time.time() < final:
        if condicion():
            return True
        time.sleep(0.03)
    return False


def main():
    usar_conhost = "--conhost" in sys.argv
    historial = "--historial" in sys.argv
    if historial:
        os.environ["PANTALLA_E2E_HISTORIAL"] = "1"
    carpeta = tempfile.mkdtemp(prefix="pantalla_e2e_")
    fichero = os.path.join(carpeta, "resultado.jsonl")
    turno = fichero + ".turno"
    orden = [sys.executable, os.path.join(AQUI, "escenario_raton.py"), fichero]
    if usar_conhost:
        orden = [os.path.join(os.environ["SystemRoot"], "System32", "conhost.exe")] + orden
    hijo = subprocess.Popen(orden, creationflags=subprocess.CREATE_NEW_CONSOLE)
    c = None
    print("Consola %s, escenario en marcha (pid %d)" % ("conhost.exe" if usar_conhost else "nueva", hijo.pid))
    try:
        inicio = esperar(fichero, 0)
        comprobar("el escenario ve una terminal de verdad", inicio["tty"], inicio)
        esperar(fichero, 1, "listo")

        k32.FreeConsole()
        pid = hijo.pid
        if usar_conhost:
            salida = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command",
                 "(Get-CimInstance Win32_Process -Filter 'ParentProcessId=%d').ProcessId" % hijo.pid],
                creationflags=0x08000000, text=True)
            pid = int(salida.split()[0])
        if not k32.AttachConsole(pid):
            raise OSError("AttachConsole falló: %d" % ctypes.get_last_error())
        c = Consola()
        if historial:
            comprobar("0. la ventana está desplazada en el búfer", c.origen()[1] > 0, c.origen())

        comprobar("1. se dibujan los botones", hasta(lambda: c.texto(5, 3, 20) == " Uno    Dos    Tres "),
                  repr(c.texto(5, 3, 20)))
        modo = c.modo()
        comprobar("1. consola con ratón y sin edición rápida", modo & 0x10 and not modo & 0x40, hex(modo))
        marcado, normal = c.fondos(5, 3, 5), c.fondos(12, 3, 5)
        comprobar("1. el primero sale marcado", len(marcado) == 1 and len(normal) == 1 and marcado != normal,
                  (marcado, normal))
        c.mover(21, 3)
        comprobar("1. al pasar por encima de 'Tres' se marca",
                  hasta(lambda: c.fondos(19, 3, 6) == marcado and c.fondos(5, 3, 5) == normal),
                  (c.fondos(19, 3, 6), c.fondos(5, 3, 5)))
        c.clic(12, 3)
        comprobar("1. clic en 'Dos' devuelve 'Dos'", esperar(fichero, 1) == "Dos")

        modo_sin = c.modo()
        comprobar("2. al acabar se quita el ratón y vuelve la edición rápida",
                  not modo_sin & 0x10 and (modo_sin & 0x40) == (inicio.get("modo", modo_sin) & 0x40), hex(modo_sin))
        with open(turno, "w") as f:
            f.write("2")
        esperar(fichero, 2, "listo")
        hasta(lambda: c.fondos(5, 3, 5) == marcado)
        c.tecla(0x27)
        comprobar("2. flecha derecha marca 'Dos'", hasta(lambda: c.fondos(12, 3, 5) == marcado), c.fondos(12, 3, 5))
        c.tecla(0x27)
        c.tecla(0x0D, "\r")
        comprobar("2. derecha, derecha, Enter devuelve 'Tres'", esperar(fichero, 2) == "Tres")

        with open(turno, "w") as f:
            f.write("3")
        esperar(fichero, 3, "listo")
        time.sleep(0.2)
        c.mover(5, 5)
        c.tecla(0x41, "a")
        c.clic(20, 10, 0x2)
        valor = esperar(fichero, 3)
        comprobar("3. esperar_clic devuelve (20, 10, 'derecho')", valor == [20, 10, "derecho"], valor)

        with open(turno, "w") as f:
            f.write("4")
        esperar(fichero, 4, "listo")
        comprobar("4. se dibuja el botón", hasta(lambda: c.texto(5, 6, 6) == " Vale "), repr(c.texto(5, 6, 6)))
        antes = c.fondos(5, 6, 6)
        time.sleep(0.2)
        c.mover(7, 6)
        comprobar("4. hover cambia el color", hasta(lambda: c.fondos(5, 6, 6) != antes), c.fondos(5, 6, 6))
        c.mover(30, 6)
        comprobar("4. al salir vuelve a su color", hasta(lambda: c.fondos(5, 6, 6) == antes), c.fondos(5, 6, 6))
        c.clic(7, 6)
        comprobar("4. clic devuelve lo de al_clic", esperar(fichero, 4) == "pulsado")

        with open(turno, "w") as f:
            f.write("5")
        esperar(fichero, 5, "listo")
        time.sleep(0.2)
        c.tecla(0x4B, "k")
        c.clic(3, 9)
        valor = esperar(fichero, 5, segundos=20)
        comprobar("5. leer_raton ve el clic", valor["clic"] == [3, 9, "izquierdo"], valor)
        comprobar("5. tecla_pulsada ve la tecla", valor["tecla"] == "k", valor)

        with open(turno, "w") as f:
            f.write("6")
        esperar(fichero, 6, "listo")
        time.sleep(0.2)
        c.enviar([c.raton(10, 12, 0, 0x1), c.raton(10, 12, 0x1, 0)])
        c.enviar([c.raton(11, 12, 0x1, 0x1)])
        c.enviar([c.raton(14, 12, 0x1, 0x1), c.raton(14, 13, 0x1, 0x1)])
        c.enviar([c.raton(14, 13, 0, 0), c.raton(20, 20, 0, 0x1)])
        c.enviar([c.raton(5, 5, 0x2, 0), c.raton(6, 5, 0x2, 0x1), c.raton(6, 5, 0, 0)])
        time.sleep(0.3)
        c.tecla(0x51, "q")
        valor = esperar(fichero, 6, segundos=20)
        comprobar("6. arrastrar da cada casilla con el botón pulsado", valor == [
            [10, 12, "izquierdo", False], [11, 12, "izquierdo", True], [14, 12, "izquierdo", True],
            [14, 13, "izquierdo", True], [5, 5, "derecho", False], [6, 5, "derecho", True]], valor)
        esperar(fichero, True, "fin")
    finally:
        if c is not None:
            k32.CloseHandle(c.entrada)
            k32.CloseHandle(c.salida)
        k32.FreeConsole()
        try:
            comprobar("el escenario acaba bien", hijo.wait(10) == 0)
        except subprocess.TimeoutExpired:
            comprobar("el escenario acaba bien", False, "no se cierra")
            hijo.kill()

    print()
    print("%d comprobaciones bien, %d mal" % (len(pasados), len(fallos)))
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
