"""Prueba de extremo a extremo del ratón en una terminal REAL de Linux/Mac (una pty).

    python3 tests/e2e/raton_linux.py
    (desde Windows:  wsl -e python3 tests/e2e/raton_linux.py)

Ejecuta escenario_raton.py dentro de una pseudo-terminal y le escribe los mismos bytes que
manda una terminal de verdad (xterm, GNOME Terminal, iTerm...) al mover el ratón, hacer clic
o pulsar flechas. Comprueba lo que devuelve cada función, los colores que se pintan, que el
ratón se activa y se desactiva, que no sale "basura" escrita y que la terminal queda como estaba.
"""

import contextlib
import fcntl
import io
import json
import os
import pty
import struct
import sys
import tempfile
import termios
import threading
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "src"))
os.environ["PANTALLA_SIN_AVISOS"] = "1"

fallos = []
pasados = []


def comprobar(nombre, condicion, detalle=""):
    (pasados if condicion else fallos).append(nombre)
    print(("  OK   " if condicion else "  FALLO ") + nombre + ("" if condicion else "  -> " + repr(detalle)[:300]))


def trozo(texto, x, y, resaltado):
    import pantalla
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        if resaltado:
            pantalla.escribir(" %s " % texto, x, y, color="negro", fondo="amarillo", negrita=True)
        else:
            pantalla.escribir(" %s " % texto, x, y, color="blanco", fondo="azul", negrita=False)
    pantalla.terminal._estado["estilo"] = ""
    return salida.getvalue()


class Terminal:
    def __init__(self, orden, entorno):
        pid, fd = pty.fork()
        if pid == 0:
            os.execvpe(orden[0], orden, entorno)
        self.pid, self.fd = pid, fd
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
        self.salida = b""
        self.cerrojo = threading.Lock()
        threading.Thread(target=self._leer, daemon=True).start()

    def _leer(self):
        while True:
            try:
                datos = os.read(self.fd, 4096)
            except OSError:
                return
            if not datos:
                return
            with self.cerrojo:
                self.salida += datos

    def texto(self):
        with self.cerrojo:
            return self.salida.decode("utf-8", "replace")

    def escribir(self, datos):
        os.write(self.fd, datos)
        time.sleep(0.15)

    def hasta(self, condicion, segundos=5):
        final = time.time() + segundos
        while time.time() < final:
            if condicion(self.texto()):
                return True
            time.sleep(0.03)
        return False


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
            if (r["paso"] == paso) if clave == "paso" else (r["paso"] == clave and r["valor"] == paso):
                return r["valor"]
            if r["paso"] == "error":
                raise RuntimeError("el escenario ha fallado: " + r["valor"])
        time.sleep(0.02)
    raise TimeoutError("no llega el paso %r (%s)" % (paso, clave))


def main():
    carpeta = tempfile.mkdtemp(prefix="pantalla_e2e_")
    fichero = os.path.join(carpeta, "resultado.jsonl")
    turno = fichero + ".turno"
    entorno = dict(os.environ, TERM="xterm-256color", PYTHONIOENCODING="utf-8", LANG="C.UTF-8")
    t = Terminal([sys.executable, os.path.join(AQUI, "escenario_raton.py"), fichero], entorno)
    print("pty abierta, escenario en marcha (pid %d)" % t.pid)

    inicio = esperar(fichero, 0)
    comprobar("el escenario ve una terminal de verdad", inicio["tty"], inicio)

    esperar(fichero, 1, "listo")
    comprobar("1. activa el ratón con hover y SGR",
              t.hasta(lambda s: "\x1b[?1000h" in s and "\x1b[?1003h" in s and "\x1b[?1006h" in s), t.texto()[-200:])
    comprobar("1. dibuja 'Uno' marcado y 'Dos' normal",
              t.hasta(lambda s: trozo("Uno", 5, 3, True) in s and trozo("Dos", 12, 3, False) in s), t.texto()[-300:])
    modo = termios.tcgetattr(t.fd)
    comprobar("1. sin eco ni modo línea mientras hay ratón",
              not modo[3] & termios.ECHO and not modo[3] & termios.ICANON, modo[3])
    antes = len(t.texto())
    t.escribir(b"\x1b[<35;21;3M")
    comprobar("1. al pasar por encima de 'Tres' se marca",
              t.hasta(lambda s: trozo("Tres", 19, 3, True) in s[antes:]), t.texto()[antes:])
    t.escribir(b"\x1b[<0;12;3M\x1b[<0;12;3m")
    comprobar("1. clic en 'Dos' devuelve 'Dos'", esperar(fichero, 1) == "Dos")
    comprobar("1. al acabar desactiva el ratón",
              t.hasta(lambda s: s.rfind("\x1b[?1000l") > s.rfind("\x1b[?1000h")), t.texto()[-200:])
    comprobar("1. no se ha escrito basura del ratón", "<35;21;3M" not in t.texto() and "<0;12;3" not in t.texto())

    with open(turno, "w") as f:
        f.write("2")
    esperar(fichero, 2, "listo")
    time.sleep(0.2)
    antes = len(t.texto())
    t.escribir(b"\x1b[C")
    comprobar("2. flecha derecha marca 'Dos'", t.hasta(lambda s: trozo("Dos", 12, 3, True) in s[antes:]))
    t.escribir(b"\x1b[C")
    t.escribir(b"\r")
    comprobar("2. derecha, derecha, Enter devuelve 'Tres'", esperar(fichero, 2) == "Tres")

    with open(turno, "w") as f:
        f.write("3")
    esperar(fichero, 3, "listo")
    time.sleep(0.2)
    t.escribir(b"a")
    t.escribir(b"\x1b[<2;20;10M\x1b[<2;20;10m")
    valor = esperar(fichero, 3)
    comprobar("3. esperar_clic devuelve (20, 10, 'derecho')", valor == [20, 10, "derecho"], valor)

    with open(turno, "w") as f:
        f.write("4")
    esperar(fichero, 4, "listo")
    comprobar("4. se dibuja el botón normal", t.hasta(lambda s: trozo("Vale", 5, 6, False) in s))
    time.sleep(0.2)
    antes = len(t.texto())
    t.escribir(b"\x1b[<35;7;6M")
    comprobar("4. hover lo marca", t.hasta(lambda s: trozo("Vale", 5, 6, True) in s[antes:]), t.texto()[antes:])
    antes = len(t.texto())
    t.escribir(b"\x1b[<35;30;6M")
    comprobar("4. al salir vuelve a normal", t.hasta(lambda s: trozo("Vale", 5, 6, False) in s[antes:]))
    t.escribir(b"\x1b[<0;7;6M\x1b[<0;7;6m")
    comprobar("4. clic devuelve lo de al_clic", esperar(fichero, 4) == "pulsado")

    with open(turno, "w") as f:
        f.write("5")
    esperar(fichero, 5, "listo")
    time.sleep(0.2)
    t.escribir(b"k")
    t.escribir(b"\x1b[<0;3;9M\x1b[<0;3;9m")
    valor = esperar(fichero, 5, segundos=20)
    comprobar("5. leer_raton ve el clic", valor["clic"] == [3, 9, "izquierdo"], valor)
    comprobar("5. tecla_pulsada ve la tecla", valor["tecla"] == "k", valor)
    comprobar("5. sin eco: no sale '<0;3;9M' escrito", "<0;3;9" not in t.texto())

    with open(turno, "w") as f:
        f.write("6")
    esperar(fichero, 6, "listo")
    comprobar("6. pide a la terminal los arrastres (?1002h)", t.hasta(lambda s: s.rfind("\x1b[?1002h") > s.rfind("\x1b[?1002l")))
    time.sleep(0.2)
    t.escribir(b"\x1b[<0;10;12M")
    t.escribir(b"\x1b[<32;11;12M")
    t.escribir(b"\x1b[<32;14;12M\x1b[<32;14;13M")
    t.escribir(b"\x1b[<0;14;13m\x1b[<35;20;20M")
    t.escribir(b"\x1b[<2;5;5M\x1b[<34;6;5M\x1b[<2;6;5m")
    t.escribir(b"q")
    valor = esperar(fichero, 6, segundos=20)
    comprobar("6. arrastrar da cada casilla con el botón pulsado", valor == [
        [10, 12, "izquierdo", False], [11, 12, "izquierdo", True], [14, 12, "izquierdo", True],
        [14, 13, "izquierdo", True], [5, 5, "derecho", False], [6, 5, "derecho", True]], valor)
    comprobar("6. sin eco del arrastre", "<32;11;12M" not in t.texto())

    esperar(fichero, True, "fin")
    modo_final = termios.tcgetattr(t.fd)
    _, estado = os.waitpid(t.pid, 0)
    comprobar("el escenario acaba bien", os.WIFEXITED(estado) and os.WEXITSTATUS(estado) == 0, estado)
    comprobar("la terminal queda como estaba (eco y modo línea)",
              modo_final[3] & termios.ECHO and modo_final[3] & termios.ICANON, modo_final[3])
    s = t.texto()
    comprobar("el ratón queda desactivado", s.rfind("\x1b[?1000l") > s.rfind("\x1b[?1000h")
              and s.rfind("\x1b[?1003l") > s.rfind("\x1b[?1003h"))

    print()
    print("%d comprobaciones bien, %d mal" % (len(pasados), len(fallos)))
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
