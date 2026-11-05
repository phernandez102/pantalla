"""Programa de prueba que usan las pruebas de extremo a extremo (e2e) del ratón.

Se ejecuta en una terminal DE VERDAD (consola nueva en Windows, pty en Linux). Va haciendo
pasos y apunta cada resultado en el fichero que se le pasa, una línea JSON por paso:

    1. botones(["Uno", "Dos", "Tres"], 5, 3)      -> el arnés pasa el ratón y hace clic en "Dos"
    2. botones(...) otra vez                     -> el arnés usa flechas + Enter
    3. esperar_clic()                            -> el arnés hace clic derecho en (20, 10)
    4. bucle([boton("Vale", 5, 6, al_clic=...)]) -> el arnés pasa por encima y hace clic
    5. leer_raton() + tecla_pulsada() juntos     -> el arnés manda una tecla y un clic
    6. leer_raton(arrastrar=True)                -> el arnés arrastra con el izquierdo y el
                                                    derecho y luego pulsa "q"
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
os.environ["PANTALLA_SIN_AVISOS"] = "1"

import pantalla  # noqa: E402

fichero = sys.argv[1]


def apuntar(paso, valor):
    with open(fichero, "a", encoding="utf-8") as f:
        f.write(json.dumps({"paso": paso, "valor": valor}) + "\n")


def esperar_turno(paso):
    turno = fichero + ".turno"
    while True:
        try:
            with open(turno, encoding="utf-8") as f:
                if f.read().strip() == str(paso):
                    return
        except OSError:
            pass
        time.sleep(0.02)


try:
    inicio = {"tty": sys.stdin.isatty() and sys.stdout.isatty(), "os": os.name}
    if os.name == "nt":
        import ctypes
        modo = ctypes.c_uint32()
        ctypes.windll.kernel32.GetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-10), ctypes.byref(modo))
        inicio["modo"] = modo.value
    if os.environ.get("PANTALLA_E2E_HISTORIAL"):
        for i in range(120):
            print("línea de historial %d" % i)
    apuntar(0, inicio)
    pantalla.limpiar()
    pantalla.escribir("e2e raton", 1, 1)

    apuntar("listo", 1)
    apuntar(1, pantalla.botones(["Uno", "Dos", "Tres"], 5, 3))

    esperar_turno(2)
    apuntar("listo", 2)
    apuntar(2, pantalla.botones(["Uno", "Dos", "Tres"], 5, 3))

    esperar_turno(3)
    apuntar("listo", 3)
    apuntar(3, list(pantalla.esperar_clic()))

    esperar_turno(4)
    vale = pantalla.boton("Vale", 5, 6, al_clic=lambda: "pulsado")
    apuntar("listo", 4)
    apuntar(4, pantalla.bucle([vale]))

    esperar_turno(5)
    pantalla.activar_raton()
    apuntar("listo", 5)
    vistos = {"clic": None, "tecla": None}
    final = time.time() + 15
    while time.time() < final and (vistos["clic"] is None or vistos["tecla"] is None):
        c = pantalla.leer_raton()
        if c:
            vistos["clic"] = list(c)
        t = pantalla.tecla_pulsada()
        if t:
            vistos["tecla"] = t
        pantalla.pausa(0.02)
    pantalla.desactivar_raton()
    apuntar(5, vistos)

    esperar_turno(6)
    pantalla.activar_raton()
    apuntar("listo", 6)
    puntos = []
    final = time.time() + 15
    while time.time() < final:
        c = pantalla.leer_raton(arrastrar=True)
        while c:
            puntos.append([c[0], c[1], c[2], c.arrastrando])
            c = pantalla.leer_raton(arrastrar=True)
        if pantalla.tecla_pulsada() == "q":
            break
        pantalla.pausa(0.02)
    pantalla.desactivar_raton()
    apuntar(6, puntos)
except BaseException as error:
    apuntar("error", repr(error))
    raise
finally:
    apuntar("fin", True)
