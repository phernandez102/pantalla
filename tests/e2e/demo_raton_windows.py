"""Recorre ejemplos/09_raton.py en una consola REAL de Windows con clics y teclas de verdad.

    python tests\\e2e\\demo_raton_windows.py         (lanza python 09_raton.py)
    python tests\\e2e\\demo_raton_windows.py --bat   (lanza ejemplos\\probar_raton.bat, como el doble clic)

Va enseñando la pantalla en cada paso (para ver que se dibuja bien) y comprueba que cada
parte de la demo responde: tarjetas con hover y clic, contador con botones, elegir color
con el teclado, pintar con clic izquierdo/derecho y salir.
"""

import ctypes
import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, AQUI)
import raton_windows as rw  # noqa: E402

k32 = rw.k32


def filas(c, n=24, ancho=90):
    return [c.texto(1, y, ancho) for y in range(1, n + 1)]


def buscar(c, texto):
    for y, linea in enumerate(filas(c, 30, 100), 1):
        x = linea.find(texto)
        if x >= 0:
            return x + 1, y
    return None


def hasta_ver(c, texto, segundos=8):
    final = time.time() + segundos
    while time.time() < final:
        p = buscar(c, texto)
        if p:
            return p
        time.sleep(0.05)
    volcar(c, "no aparece %r" % texto)
    raise TimeoutError("no aparece %r" % texto)


def volcar(c, titulo):
    print("----- " + titulo)
    for linea in filas(c):
        print("|" + linea.rstrip())


def hijos(pid):
    salida = subprocess.check_output(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_Process -Filter 'ParentProcessId=%d').ProcessId" % pid],
        creationflags=0x08000000, text=True)
    return [int(p) for p in salida.split()]


def main():
    con_bat = "--bat" in sys.argv
    entorno = dict(os.environ, PYTHONPATH=os.path.join(RAIZ, "src"), PYTHONIOENCODING="utf-8")
    conhost = os.path.join(os.environ["SystemRoot"], "System32", "conhost.exe")
    if con_bat:
        orden = [conhost, "cmd.exe", "/c", os.path.join(RAIZ, "ejemplos", "probar_raton.bat")]
        entorno.pop("PYTHONPATH")
    else:
        orden = [conhost, sys.executable, "09_raton.py"]
    hijo = subprocess.Popen(orden, cwd=os.path.join(RAIZ, "ejemplos"), env=entorno,
                            creationflags=subprocess.CREATE_NEW_CONSOLE)
    hechos = []
    c = None
    try:
        final = time.time() + 10
        while time.time() < final and not hijos(hijo.pid):
            time.sleep(0.2)
        time.sleep(1.0)
        k32.FreeConsole()
        if not k32.AttachConsole(hijos(hijo.pid)[0]):
            raise OSError("AttachConsole: %d" % ctypes.get_last_error())
        c = rw.Consola()

        hasta_ver(c, "Pintar con el ratón")
        volcar(c, "menú principal")

        x, y = hasta_ver(c, "Tarjetas que se iluminan")
        c.mover(x + 2, y)
        time.sleep(0.3)
        c.clic(x + 2, y)
        fx, fy = hasta_ver(c, "Agua")
        c.mover(fx, fy + 2)
        hasta_ver(c, "elígeme")
        volcar(c, "tarjetas con el ratón encima de Agua")
        c.clic(fx, fy + 2)
        hasta_ver(c, "Has elegido Agua")
        hechos.append("tarjetas: hover + clic")
        c.tecla(0x1B)

        x, y = hasta_ver(c, "Botones con contador")
        c.clic(x + 2, y)
        hasta_ver(c, "Clics: 0")
        bx, by = buscar(c, " +1 ")
        c.clic(bx + 1, by)
        c.clic(bx + 1, by)
        hasta_ver(c, "Clics: 2")
        mx, my = buscar(c, " -1 ")
        c.clic(mx + 1, my)
        hasta_ver(c, "Clics: 1")
        volcar(c, "contador después de +1 +1 -1")
        hechos.append("contador: +1 +1 -1 = 1")
        vx, vy = buscar(c, " Volver ")
        c.clic(vx + 2, vy)

        hasta_ver(c, "Elegir un color")
        c.tecla(0x31, "1")
        hasta_ver(c, " Verde ")
        c.tecla(0x27)
        c.tecla(0x0D, "\r")
        hasta_ver(c, "Has elegido: Verde")
        hechos.append("botones con número + flechas + Enter: Verde")
        c.tecla(0x20, " ")

        x, y = hasta_ver(c, "Pintar con el ratón")
        c.clic(x + 2, y)
        hasta_ver(c, "Esc vuelve")
        c.enviar([c.raton(20, 10, 0, 0x1), c.raton(20, 10, 0x1, 0)])
        time.sleep(0.15)
        c.enviar([c.raton(29, 10, 0x1, 0x1)])
        time.sleep(0.15)
        c.enviar([c.raton(35, 14, 0x1, 0x1)])
        time.sleep(0.15)
        c.enviar([c.raton(35, 14, 0, 0)])
        time.sleep(0.5)
        raya = c.texto(20, 10, 10)
        diagonal = [c.texto(x, y, 1) for x, y in ((31, 11), (32, 12), (33, 13), (35, 14))]
        if raya != "█" * 10 or diagonal != ["█"] * 4:
            volcar(c, "raya mal")
            raise AssertionError("la raya arrastrando tiene huecos: %r %r" % (raya, diagonal))
        hechos.append("pintar arrastrando deprisa: raya seguida sin huecos")
        c.enviar([c.raton(22, 10, 0x2, 0), c.raton(25, 10, 0x2, 0x1), c.raton(25, 10, 0, 0)])
        time.sleep(0.4)
        if c.texto(20, 10, 10) != "██    ████":
            volcar(c, "borrado mal")
            raise AssertionError("el derecho no ha borrado: %r" % c.texto(20, 10, 10))
        hechos.append("botón derecho arrastrando borra")
        px, py = buscar(c, "Color:")
        c.clic(px + 8 + 2 * 4 + 1, py)
        time.sleep(0.3)
        c.clic(40, 8)
        time.sleep(0.3)
        k32_attr = (rw.w.WORD * 1)()
        leidos = rw.w.DWORD()
        izq, arriba = c.origen()
        k32.ReadConsoleOutputAttribute(c.salida, k32_attr, 1, rw.COORD(izq + 39, arriba + 7), ctypes.byref(leidos))
        verde = k32_attr[0] & 0x0F
        k32.ReadConsoleOutputAttribute(c.salida, k32_attr, 1, rw.COORD(izq + 19, arriba + 9), ctypes.byref(leidos))
        rojo = k32_attr[0] & 0x0F
        if c.texto(40, 8, 1) != "█" or verde == rojo:
            raise AssertionError("la paleta no cambia el color: %r %s %s" % (c.texto(40, 8, 1), verde, rojo))
        volcar(c, "lienzo: raya rápida, trozo borrado y un punto verde")
        hechos.append("paleta: el punto nuevo sale con otro color")
        c.tecla(0x1B)

        x, y = hasta_ver(c, "Salir")
        c.clic(x + 1, y)
        if con_bat:
            time.sleep(1.0)
            c.tecla(0x20, " ")
    finally:
        if c is not None:
            k32.CloseHandle(c.entrada)
            k32.CloseHandle(c.salida)
        k32.FreeConsole()
    codigo = hijo.wait(15)
    hechos.append("sale con código %d" % codigo)
    print()
    print("\n".join("  OK   " + h for h in hechos))
    return codigo


if __name__ == "__main__":
    sys.exit(main())
