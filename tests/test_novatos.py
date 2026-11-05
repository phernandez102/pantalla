"""Los errores típicos de quien empieza: que pantalla le diga en español qué ha pasado."""

import io
import os
import sys
import unittest
from unittest import mock

import pantalla
from pantalla import terminal

from test_juego import BaseJuego


class NombresParecidos(unittest.TestCase):
    def test_con_tildes_ñ_y_mayusculas_tambien_vale(self):
        self.assertIs(getattr(pantalla, "tamaño"), pantalla.tamano)
        self.assertIs(getattr(pantalla, "diseño"), pantalla.diseno)
        self.assertIs(getattr(pantalla, "pedir_contraseña"), pantalla.pedir_contrasena)
        self.assertIs(getattr(pantalla, "menú"), pantalla.menu)
        self.assertIs(getattr(pantalla, "posición_ratón"), pantalla.posicion_raton)
        self.assertIs(pantalla.Escribir, pantalla.escribir)
        self.assertIs(pantalla.sprite, pantalla.Sprite)
        from pantalla import tamaño  # noqa: F401  (también con from ... import)

    def test_si_no_existe_sugiere_en_español(self):
        with self.assertRaises(AttributeError) as e:
            pantalla.escribe("hola")
        self.assertIn("pantalla.escribir", str(e.exception))
        self.assertIn("pantalla.ayuda()", str(e.exception))
        with self.assertRaises(AttributeError) as e:
            pantalla.borrar()
        self.assertIn("pantalla.limpiar", str(e.exception))
        with self.assertRaises(AttributeError) as e:
            pantalla.sleep(1)
        self.assertIn("pantalla.pausa", str(e.exception))
        with self.assertRaises(AttributeError):
            pantalla.cosa_que_no_se_parece_a_nada_xyz
        with self.assertRaises(AttributeError):
            pantalla._privada

    def test_ayuda_entiende_tildes(self):
        salida = io.StringIO()
        with mock.patch("sys.stdout", salida):
            pantalla.ayuda("tamaño")
            pantalla.ayuda("pantalla.caja()")
        self.assertIn("pantalla.tamano", salida.getvalue())
        self.assertIn("pantalla.caja", salida.getvalue())


class ErroresAmables(unittest.TestCase):
    def test_texto_al_final(self):
        with self.assertRaises(TypeError) as e:
            pantalla.escribir(5, 3, "hola")
        self.assertIn("primero va el texto", str(e.exception))

    def test_numero_entre_comillas(self):
        with self.assertRaises(TypeError) as e:
            pantalla.gotoxy("5", 3)
        self.assertIn("quítale las comillas", str(e.exception))
        self.assertIn("int()", str(e.exception))

    def test_pausa_con_texto(self):
        with self.assertRaises(TypeError) as e:
            pantalla.pausa("2")
        self.assertIn("pausa(2)", str(e.exception))
        with self.assertRaises(TypeError):
            pantalla.pausa(-1)

    def test_salida_que_no_entiende_unicode_no_rompe(self):
        crudo = io.BytesIO()
        salida = io.TextIOWrapper(crudo, encoding="cp1252")
        with mock.patch("sys.stdout", salida), mock.patch.dict(os.environ, {"PANTALLA_SIN_AVISOS": "1"}):
            pantalla.caja(1, 1, 6, 3)
        salida.flush()
        self.assertIn(b"?", crudo.getvalue())


class TeclasConOtrosNombres(BaseJuego):
    def test_tecla_entiende_mayusculas_y_sinonimos(self):
        from pantalla import teclado

        with mock.patch.object(teclado, "_tecla", return_value="enter"):
            t = pantalla.tecla()
        for igual in ("enter", "Enter", "ENTER", "Intro", "intro", "return", "\n"):
            self.assertTrue(t == igual, igual)
            self.assertFalse(t != igual, igual)
        self.assertTrue(t in ("Intro", "Esc"))
        self.assertFalse(t == "esc")
        self.assertEqual(str(t), "enter")
        self.assertEqual({"enter": 1}[t], 1)
        with mock.patch.object(teclado, "_tecla", return_value="espacio"):
            self.assertTrue(pantalla.tecla() == " ")
        with mock.patch.object(teclado, "_tecla", return_value="arriba"):
            t = pantalla.tecla()
            self.assertTrue(t == "Flecha arriba" and t == "up" and t == "↑")
        with mock.patch.object(teclado, "_tecla", return_value="A"):
            self.assertTrue(pantalla.tecla() == "a")
        with mock.patch.object(teclado, "_tecla", return_value="ñ"):
            self.assertFalse(pantalla.tecla() == "n")
        with mock.patch.object(teclado, "_tecla_pulsada", return_value=None):
            self.assertIsNone(pantalla.tecla_pulsada())

    def test_en_jugar_y_pulsada(self):
        vistas = []

        def actualizar(tecla):
            vistas.append(tecla == "Intro")
            if pantalla.pulsada("Intro"):
                return "ok"

        self.assertEqual(self.jugar(actualizar, [["enter"]]), "ok")
        self.assertEqual(vistas, [True])


class FaltaGlobal(BaseJuego):
    def test_jugar_con_un_global_olvidado_de_verdad(self):
        codigo = (
            "vidas = 3\n"
            "def actualizar():\n"
            "    vidas = vidas - 1\n"
        )
        espacio = {}
        exec(codigo, espacio)
        with self.assertRaises(UnboundLocalError) as e:
            self.jugar(espacio["actualizar"])
        self.assertIn("global vidas", str(e.exception))

    def test_otros_errores_no_se_tocan(self):
        def actualizar():
            raise ZeroDivisionError("x")

        with self.assertRaises(ZeroDivisionError):
            self.jugar(actualizar)


class EnIdle(unittest.TestCase):
    def setUp(self):
        self.idle = mock.patch.dict(sys.modules, {"idlelib": mock.Mock()})
        self.idle.start()

    def tearDown(self):
        self.idle.stop()

    def _abrir(self, archivo, nt=True, entorno=None):
        principal = mock.Mock(__file__=archivo)
        with mock.patch.object(terminal, "_es_terminal", return_value=False), \
                mock.patch.object(terminal.os, "name", "nt" if nt else "posix"), \
                mock.patch.dict(sys.modules, {"__main__": principal}), \
                mock.patch.dict(os.environ, entorno or {}), \
                mock.patch("subprocess.Popen") as popen, \
                mock.patch("sys.stderr", io.StringIO()) as error:
            abierto = terminal._abrir_en_consola_si_idle()
        return abierto, popen, error.getvalue()

    def test_abre_tu_programa_en_cmd(self):
        abierto, popen, aviso = self._abrir(os.path.abspath(__file__))
        self.assertTrue(abierto)
        orden = popen.call_args[0][0]
        self.assertTrue(orden.startswith('cmd /c ""'))
        self.assertIn(os.path.abspath(__file__), orden)
        self.assertIn("pause", orden)
        self.assertNotIn("pythonw.exe", orden.lower())
        self.assertIn("ventana nueva", aviso)

    def test_no_abre_si_no_hay_archivo_o_no_es_windows_o_no_quieres(self):
        self.assertFalse(self._abrir(None)[0])
        self.assertFalse(self._abrir("no_existe_esto.py")[0])
        self.assertFalse(self._abrir(os.path.abspath(__file__), nt=False)[0])
        self.assertFalse(self._abrir(os.path.abspath(__file__),
                                     entorno={"PANTALLA_NO_ABRIR": "1"})[0])

    def test_fuera_de_idle_no_hace_nada(self):
        self.idle.stop()
        try:
            self.assertFalse(terminal._abrir_en_consola_si_idle())
        finally:
            self.idle.start()


if __name__ == "__main__":
    unittest.main()
