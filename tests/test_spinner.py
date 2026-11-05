import io
import os
import sys
import threading
import time
import unicodedata
import unittest
from unittest import mock

os.environ["PANTALLA_SIN_AVISOS"] = "1"

import pantalla
from pantalla import spinners as modulo, terminal
from pantalla.juego import _Lienzo


class SalidaTerminal(io.StringIO):
    def isatty(self):
        return True


class BaseSpinner(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        terminal._estado["cursor_oculto"] = False
        terminal._estado["estilo"] = ""

    def tearDown(self):
        sys.stdout = self.stdout

    def salida(self, terminal_de_verdad=True):
        sys.stdout = SalidaTerminal() if terminal_de_verdad else io.StringIO()
        return sys.stdout


class TestEstilos(unittest.TestCase):
    def test_lista_spinners(self):
        nombres = pantalla.lista_spinners()
        self.assertEqual(nombres, sorted(nombres))
        for n in ("dots", "line", "arc", "circle", "star", "bouncingBar", "bouncingBall", "pong",
                  "shark", "aesthetic", "binary", "growVertical", "toggle", "arrow3", "simpleDots"):
            self.assertIn(n, nombres)
        self.assertGreaterEqual(len(nombres), 50)

    def test_todo_de_ancho_uno_y_sin_emojis(self):
        for nombre, (milis, fotogramas) in modulo.SPINNERS.items():
            self.assertTrue(20 <= milis <= 1000, nombre)
            self.assertTrue(fotogramas, nombre)
            largos = set()
            for f in fotogramas:
                for c in f:
                    self.assertNotIn(unicodedata.east_asian_width(c), ("W", "F"), (nombre, c))
                    self.assertLess(ord(c), 0x1F000, (nombre, c))
                    self.assertNotEqual(unicodedata.category(c), "Mn", (nombre, c))
                largos.add(len(f))
            self.assertEqual(len(largos), 1, "%s: todos los fotogramas miden lo mismo" % nombre)

    def test_nombres_en_espanol_y_errores(self):
        self.assertEqual(pantalla.spinner("x", estilo="arco").fotogramas, modulo.SPINNERS["arc"][1])
        self.assertEqual(pantalla.spinner("x", estilo="Tiburón").fotogramas, modulo.SPINNERS["shark"][1])
        self.assertEqual(pantalla.spinner("x", estilo="bouncing_ball").fotogramas,
                         modulo.SPINNERS["bouncingBall"][1])
        s = pantalla.spinner("x", estilo=["a", "b"], intervalo=0.5)
        self.assertEqual((s.fotogramas, s.intervalo), (["a", "b"], 0.5))
        with self.assertRaises(ValueError) as error:
            pantalla.spinner("x", estilo="dotz")
        self.assertIn("dots", str(error.exception))
        with self.assertRaises(TypeError):
            pantalla.spinner("x", estilo=3)
        with self.assertRaises(ValueError):
            pantalla.spinner("x", color="colorinchi")
        with self.assertRaises(TypeError):
            pantalla.spinner("x", x=3)
        with self.assertRaises(ValueError):
            pantalla.spinner("x", x=0, y=1)
        self.assertIsInstance(pantalla.spinner("x"), pantalla.Spinner)


class TestSinTerminal(BaseSpinner):
    def test_escribe_una_vez_sin_animar(self):
        out = self.salida(terminal_de_verdad=False)
        s = pantalla.spinner("Descargando").empezar()
        self.assertFalse(s.girando)
        time.sleep(0.05)
        s.bien("Hecho")
        s.bien("otra vez no")
        self.assertEqual(out.getvalue(), "Descargando...\n✔ Hecho\n")

    def test_parar_sin_terminal_no_escribe_mas(self):
        out = self.salida(terminal_de_verdad=False)
        with pantalla.spinner("Algo") as s:
            pass
        self.assertEqual(out.getvalue(), "Algo...\n✔ Algo\n")
        out.truncate(0)
        out.seek(0)
        pantalla.spinner("Nada").empezar().parar()
        self.assertEqual(out.getvalue(), "Nada...\n")


class TestAnimado(BaseSpinner):
    def test_gira_en_segundo_plano_y_acaba_bien(self):
        out = self.salida()
        s = pantalla.spinner("Cargando", estilo="line", intervalo=0.01)
        self.assertIs(s.empezar(), s)
        self.assertIs(s.empezar(), s)
        self.assertTrue(s.girando)
        time.sleep(0.12)
        s.texto = "Casi"
        time.sleep(0.05)
        hilo = s._hilo
        s.bien("Listo")
        self.assertFalse(hilo.is_alive())
        self.assertFalse(s.girando)
        texto = out.getvalue()
        self.assertTrue(texto.startswith("\x1b[?25l"))
        for f in ("-", "\\", "|", "/"):
            self.assertIn(f + "\x1b[0m Cargando", texto)
        self.assertIn(" Casi", texto)
        self.assertTrue(texto.endswith("✔\x1b[0m Listo\n\x1b[?25h"))
        self.assertIn("\x1b[32m✔", texto)
        self.assertFalse(terminal._estado["cursor_oculto"])
        l = _Lienzo(40, 3)
        l.escribir(texto)
        self.assertEqual(l.texto().split("\n")[0], "✔ Listo")

    def test_with_y_errores(self):
        out = self.salida()
        with self.assertRaises(ZeroDivisionError):
            with pantalla.spinner("Dividiendo", intervalo=0.01):
                1 / 0
        self.assertIn("\x1b[31m✖\x1b[0m Dividiendo\n", out.getvalue())
        with pantalla.spinner("Bien", intervalo=0.01):
            pass
        self.assertIn("✔\x1b[0m Bien\n", out.getvalue())

    def test_otros_finales(self):
        for metodo, simbolo in (("mal", "✖"), ("aviso", "⚠"), ("info", "ℹ")):
            out = self.salida()
            s = pantalla.spinner("t", intervalo=0.01).empezar()
            getattr(s, metodo)("fin")
            self.assertIn(simbolo + "\x1b[0m fin\n", out.getvalue())
        out = self.salida()
        pantalla.spinner("t", intervalo=0.01).empezar().dejar("★", "Récord", color="amarillo")
        self.assertIn("\x1b[33m★\x1b[0m Récord\n", out.getvalue())
        out = self.salida()
        pantalla.spinner("t", intervalo=0.01).empezar().parar()
        self.assertTrue(out.getvalue().endswith("\r\x1b[2K\x1b[?25h"))

    def test_en_un_sitio_fijo_no_mueve_el_cursor(self):
        out = self.salida()
        s = pantalla.spinner("Guardando", estilo="dots", x=5, y=3, intervalo=0.01).empezar()
        time.sleep(0.05)
        s.texto = "G"
        time.sleep(0.05)
        s.bien()
        texto = out.getvalue()
        self.assertIn("\x1b7\x1b[3;5H", texto)
        self.assertNotIn("\r", texto)
        l = _Lienzo(30, 4)
        l.escribir("\x1b[1;1H" + texto)
        self.assertEqual(l.texto().split("\n")[2][4:7], "✔ G")
        self.assertEqual((l.x, l.y), (1, 1))

    def test_recorta_el_texto_al_ancho(self):
        out = self.salida()
        with mock.patch.object(terminal, "tamano", return_value=(12, 5)):
            s = pantalla.spinner("x" * 50, estilo="line", intervalo=0.01).empezar()
            s.parar()
        self.assertNotIn("x" * 10, out.getvalue())

    def test_las_salidas_de_dos_hilos_no_se_mezclan(self):
        class Lenta(SalidaTerminal):
            def write(self, texto):
                for c in texto:
                    super(Lenta, self).write(c)
                    time.sleep(0)
                return len(texto)

        out = Lenta()
        sys.stdout = out

        def escribir(letra):
            for _ in range(30):
                terminal._salida(letra * 20)

        hilos = [threading.Thread(target=escribir, args=(l,)) for l in "AB"]
        for h in hilos:
            h.start()
        for h in hilos:
            h.join()
        texto = out.getvalue()
        trozos = [texto[i:i + 20] for i in range(0, len(texto), 20)]
        self.assertTrue(all(t in ("A" * 20, "B" * 20) for t in trozos))


if __name__ == "__main__":
    unittest.main()
