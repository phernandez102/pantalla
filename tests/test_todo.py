import glob
import io
import os
import re
import unittest
from unittest import mock

os.environ["PANTALLA_SIN_AVISOS"] = "1"

import pantalla
from pantalla import teclado, terminal

from test_pantalla import Base, PantallaVirtual


class TestPantallaYCursor(Base):
    def test_limpiar_linea(self):
        self.assertEqual(self.captura(pantalla.limpiar_linea), "\r\x1b[2K")
        self.assertEqual(self.captura(pantalla.limpiar_linea, 4), "\x1b[4;1H\x1b[2K")
        v = PantallaVirtual(self.ANCHO, self.ALTO)
        v.procesar(self.captura(pantalla.escribir, "basura", 3, 4))
        v.procesar(self.captura(pantalla.limpiar_linea, 4))
        self.assertEqual(v.linea(4).strip(), "")
        with self.assertRaises(ValueError):
            pantalla.limpiar_linea(0)

    def test_ir_a_es_gotoxy(self):
        self.assertEqual(self.captura(pantalla.ir_a, 7, 3), self.captura(pantalla.gotoxy, 7, 3))

    def test_cursor(self):
        self.assertEqual(self.captura(pantalla.ocultar_cursor), "\x1b[?25l")
        self.assertTrue(terminal._estado["cursor_oculto"])
        self.assertEqual(self.captura(pantalla.mostrar_cursor), "\x1b[?25h")
        self.assertFalse(terminal._estado["cursor_oculto"])

    def test_guardar_y_volver(self):
        salida = self.captura(lambda: (pantalla.gotoxy(5, 5), pantalla.guardar_posicion(),
                                       pantalla.gotoxy(1, 1), pantalla.volver_a_posicion(),
                                       print("X", end="")))
        self.assertIn("\x1b7", salida)
        self.assertIn("\x1b8", salida)
        self.assertEqual(PantallaVirtual(self.ANCHO, self.ALTO).procesar(salida).linea(5)[4], "X")

    def test_titulo_ventana_y_pitido(self):
        self.assertEqual(self.captura(pantalla.titulo_ventana, "Mi juego"), "\x1b]0;Mi juego\x07")
        self.assertEqual(self.captura(pantalla.pitido), "\x07")

    def test_pausa(self):
        with mock.patch("time.sleep") as dormir:
            pantalla.pausa(0.25)
        dormir.assert_called_once_with(0.25)

    def test_iniciar_y_terminar(self):
        with mock.patch.object(teclado, "_activar_modo_teclas") as act, \
                mock.patch.object(teclado, "_desactivar_modo_teclas") as des:
            salida = self.captura(pantalla.iniciar, titulo="Juego")
            self.assertIn("\x1b[?1049h", salida)
            self.assertIn("\x1b[2J", salida)
            self.assertIn("\x1b[?25l", salida)
            self.assertIn("\x1b]0;Juego\x07", salida)
            act.assert_called_once_with()
            salida = self.captura(pantalla.terminar)
            self.assertIn("\x1b[?1049l", salida)
            self.assertIn("\x1b[?25h", salida)
            self.assertIn("\x1b[0m", salida)
            des.assert_called()
        self.assertFalse(terminal._estado["pantalla_aparte"])

    def test_iniciar_sin_pantalla_aparte(self):
        with mock.patch.object(teclado, "_activar_modo_teclas"), \
                mock.patch.object(teclado, "_desactivar_modo_teclas"):
            salida = self.captura(pantalla.iniciar, aparte=False, cursor=True, borrar=False)
            self.assertNotIn("1049", salida)
            self.assertNotIn("?25l", salida)
            self.captura(pantalla.terminar)


class TestColoresYEstilos(Base):
    def test_lista_colores(self):
        colores = pantalla.lista_colores()
        for nombre in ("rojo", "verde", "azul", "amarillo", "blanco", "negro", "naranja", "rosa"):
            self.assertIn(nombre, colores)
        for nombre in colores:
            salida = self.captura(pantalla.escribir, "x", 1, 1, color=nombre)
            self.assertIn("\x1b[", salida, nombre)

    def test_estilos_de_borde(self):
        self.assertIn("simple", pantalla.ESTILOS)
        for nombre in pantalla.ESTILOS:
            v = self.pinta(pantalla.caja, 1, 1, 6, 3, estilo=nombre)
            self.assertNotEqual(v.linea(1)[0], " ", nombre)
            self.assertEqual(v.linea(2)[1:5], "    ", nombre)


class TestTecladoQueFaltaba(Base):
    def setUp(self):
        super().setUp()
        del teclado._teclas_pendientes[:]

    def test_tecla_pulsada_sin_teclado(self):
        with mock.patch.object(teclado, "_hay_teclado", return_value=False):
            self.assertIsNone(pantalla.tecla_pulsada())

    def test_vaciar_teclado(self):
        pendientes = ["a", "b", None]
        teclado._teclas_pendientes.extend(["x"])
        with mock.patch.object(teclado, "tecla_pulsada", side_effect=pendientes) as tp:
            pantalla.vaciar_teclado()
        self.assertEqual(tp.call_count, 3)
        self.assertEqual(teclado._teclas_pendientes, [])

    def test_esperar(self):
        with mock.patch.object(teclado, "tecla", return_value="enter"):
            salida = self.captura(pantalla.esperar, "Pulsa algo", 2, 3)
        self.assertEqual(self.ultimo_resultado, "enter")
        self.assertEqual(PantallaVirtual(self.ANCHO, self.ALTO).procesar(salida).linea(3)[1:11], "Pulsa algo")

    def test_pedir_contrasena(self):
        with mock.patch("getpass.getpass", return_value="secreto") as gp:
            self.assertEqual(pantalla.pedir_contrasena("Clave: "), "secreto")
        gp.assert_called_once_with("Clave: ")


class TestTodoTieneTest(unittest.TestCase):
    def test_cada_funcion_publica_sale_en_algun_test(self):
        carpeta = os.path.dirname(os.path.abspath(__file__))
        textos = []
        for ruta in glob.glob(os.path.join(carpeta, "test_*.py")) + glob.glob(os.path.join(carpeta, "e2e", "*.py")):
            with io.open(ruta, encoding="utf-8") as f:
                textos.append(f.read())
        todo = "\n".join(textos)
        sin_test = [n for n in pantalla.__all__ if not re.search(r"\b%s\b" % re.escape(n), todo)]
        self.assertEqual(sin_test, [], "Funciones públicas sin ningún test: %s" % sin_test)

    def test_todo_lo_publico_existe_y_tiene_explicacion(self):
        for nombre in pantalla.__all__:
            self.assertTrue(hasattr(pantalla, nombre), nombre)
            objeto = getattr(pantalla, nombre)
            if callable(objeto):
                self.assertTrue((objeto.__doc__ or "").strip(), "%s no tiene docstring" % nombre)


if __name__ == "__main__":
    unittest.main()
