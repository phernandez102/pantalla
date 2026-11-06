import math
import os
import re
import struct
import tempfile
import unittest
from unittest import mock

import pantalla
from pantalla import imagenes, juego, modelos, raton, terminal

from test_imagenes import _color, _pixeles_de, _png
from test_juego import BaseJuego
from test_pantalla import Base

CUBO_OBJ = """# un cubo
mtllib cubo.mtl
v 0 0 0
v 1 0 0
v 1 1 0
v 0 1 0
v 0 0 1
v 1 0 1
v 1 1 1
v 0 1 1
usemtl rojo
f 1 2 3 4
f 5/1 6/2 7/3 8/4
usemtl verde
f 1//1 2//1 6//1 5//1
f -5 -6 -2 -1
f 2 3 7 6
f 1 5 8 4
"""


def _stl_binario(triangulos):
    datos = b"\x00" * 80 + struct.pack("<I", len(triangulos))
    for t in triangulos:
        datos += struct.pack("<3f", 0, 0, 0) + b"".join(struct.pack("<3f", *v) for v in t) + b"\x00\x00"
    return datos


PIRAMIDE = [((0, 0, 1), (1, 0, 0), (0, 1, 0)), ((0, 0, 1), (0, 1, 0), (-1, 0, 0)),
            ((0, 0, 1), (-1, 0, 0), (0, -1, 0)), ((0, 0, 1), (0, -1, 0), (1, 0, 0))]


class TestLeer(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.dir = self.carpeta.name

    def tearDown(self):
        self.carpeta.cleanup()

    def escribir(self, nombre, datos):
        ruta = os.path.join(self.dir, nombre)
        with open(ruta, "wb") as f:
            f.write(datos if isinstance(datos, bytes) else datos.encode())
        return ruta

    def test_obj_con_colores(self):
        self.escribir("cubo.mtl", "newmtl rojo\nKd 1 0 0\nnewmtl verde\nKd 0 1 0\n")
        m = pantalla.modelo(self.escribir("cubo.obj", CUBO_OBJ))
        self.assertEqual(len(m.vertices), 8)
        self.assertEqual(len(m.triangulos), 12)
        self.assertEqual(m.colores[0], (255, 0, 0))
        self.assertEqual(m.colores[-1], (0, 255, 0))
        # centrado y dentro de la caja
        for k in range(3):
            self.assertAlmostEqual(min(v[k] for v in m.vertices), -1)
            self.assertAlmostEqual(max(v[k] for v in m.vertices), 1)
        self.assertAlmostEqual(m.radio, math.sqrt(3))
        self.assertIn("12 triángulos", repr(m))

    def test_stl_binario_y_de_texto(self):
        m = pantalla.modelo(self.escribir("p.stl", _stl_binario(PIRAMIDE)))
        self.assertEqual(len(m.triangulos), 4)
        texto = "solid p\n" + "".join("facet normal 0 0 0\nouter loop\n" + "".join("vertex %g %g %g\n" % v for v in t) +
                                      "endloop\nendfacet\n" for t in PIRAMIDE) + "endsolid p\n"
        m2 = pantalla.modelo(self.escribir("t.stl", texto), color="naranja")
        self.assertEqual(len(m2.triangulos), 4)
        self.assertEqual(m2.vertices, m.vertices)

    def test_imagen_en_relieve(self):
        ruta = self.escribir("cuadros.png", _png(_pixeles_de(16, 16, _color)))
        m = pantalla.modelo(ruta, relieve=0.5)
        self.assertGreater(len(m.triangulos), 100)
        # lo blanco (abajo a la derecha) está más alto que lo azul
        self.assertIn((255, 255, 255), m.colores)
        self.assertIn((0, 0, 255), m.colores)

    def test_superficie(self):
        m = pantalla.modelo(lambda x, y: x * x - y * y)
        self.assertGreater(len(m.triangulos), 1000)
        # con raíces de negativos se queda un trozo sin pintar
        m2 = pantalla.modelo(lambda x, y: math.sqrt(x))
        self.assertLess(len(m2.triangulos), len(m.triangulos))
        with self.assertRaises(ValueError):
            pantalla.modelo(lambda x, y: math.sqrt(-1 - x * x))

    def test_errores(self):
        with self.assertRaises(FileNotFoundError):
            pantalla.modelo(os.path.join(self.dir, "no.obj"))
        with self.assertRaises(TypeError):
            pantalla.modelo(42)
        with self.assertRaises(ValueError):
            pantalla.modelo(self.escribir("vacio.obj", "# nada\n"))
        with self.assertRaises(ValueError):
            pantalla.modelo(self.escribir("cosa.txt", "hola"))
        with self.assertRaises(ValueError):
            pantalla.modelo(lambda x, y: x, rango=(3, 1))


class TestPintar(unittest.TestCase):
    def test_lo_de_cerca_tapa(self):
        # dos cuadrados, el rojo encima (z alto) y el azul debajo: desde arriba se ve el rojo
        v = [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
        t = [(0, 1, 2), (0, 2, 3), (4, 5, 6), (4, 6, 7)]
        m = modelos.Modelo(v, t, [(0, 0, 255)] * 2 + [(255, 0, 0)] * 2)
        img = modelos._pintar(m, 40, 40, 0, 90, 1, (0, 0, 0))
        i = 20 * 40 + 20
        self.assertGreater(img.R[i], 100)
        self.assertEqual(img.B[i], 0)
        self.assertEqual(img.A[i], 255)
        self.assertEqual(img.A[0], 0)
        # desde abajo, el azul
        img = modelos._pintar(m, 40, 40, 0, -90, 1, (0, 0, 0))
        self.assertGreater(img.B[i], 100)

    def test_fino_es_del_mismo_tamano(self):
        m = pantalla.modelo(lambda x, y: x + y)
        img = modelos._pintar(m, 30, 20, 30, 20, 1, (0, 0, 0), fino=2)
        self.assertEqual((img.W, img.H), (30, 20))


def _sin_colores(texto):
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", texto)


class TestDibujarModelo(Base):
    ANCHO, ALTO = 80, 30

    def test_con_bloques(self):
        salida = self.captura(pantalla.dibujar_modelo, lambda x, y: x * y, ancho=30, alto=10, estilo="bloques")
        self.assertEqual(self.ultimo_resultado, (30, 10))
        texto = _sin_colores(salida)
        self.assertTrue(set("▀▄█") & set(texto))
        self.assertIn("38;2;", salida)

    def test_con_imagen(self):
        with mock.patch.dict(imagenes._capacidad, {"protocolo": "sixel", "imagenes": True}):
            salida = self.captura(pantalla.dibujar_modelo, lambda x, y: x * y, 5, 3, ancho=20, alto=6, estilo="imagen")
        self.assertIn("\x1bP0;1;0q\"1;1;200;120", salida)

    def test_girar(self):
        raton._raton["fuente"] = lambda espera: None
        try:
            z = self.captura(pantalla.dibujar_modelo, lambda x, y: x * y, 1, 1, ancho=20, alto=8, estilo="bloques",
                             girar=True) and self.ultimo_resultado
            self.assertIn(z, terminal._giratorios)
            self.assertTrue(z.raton({"tipo": "clic", "x": 5, "y": 5, "boton": "izquierdo"}))
            self.assertTrue(z.raton({"tipo": "movimiento", "x": 7, "y": 5, "boton": "izquierdo"}))
            self.assertTrue(z.sucio)
            salida = self.captura(z.pintar, True)
            self.assertTrue(z.fino_pendiente)
            self.assertIn("\x1b[1;1H", salida)
        finally:
            del terminal._giratorios[:]
            raton._raton["fuente"] = None
            raton._raton["activo"] = False

    def test_errores(self):
        with self.assertRaises(ValueError):
            pantalla.dibujar_modelo(lambda x, y: x, estilo="puntos")
        with self.assertRaises(ValueError):
            pantalla.dibujar_modelo(lambda x, y: x, ancho=2)
        with self.assertRaises(TypeError):
            pantalla.dibujar_modelo(lambda x, y: x, 4)


class TestVerModelo(Base):
    def test_fuera_de_la_terminal_lo_dibuja_quieto(self):
        salida = self.captura(pantalla.ver_modelo, lambda x, y: x * y)
        self.assertIsNone(self.ultimo_resultado)
        self.assertIn("38;2;", salida)


class TestVerModeloEnTerminal(BaseJuego):
    def ver(self, estilo):
        eventos = [[], [{"tipo": "clic", "x": 10, "y": 10, "boton": "derecho"},
                        {"tipo": "movimiento", "x": 14, "y": 11, "boton": "derecho"}],
                   [{"tipo": "tecla", "tecla": "+"}], [{"tipo": "tecla", "tecla": "esc"}]]

        class Entorno(juego._Entorno):
            def es_terminal(self, salida):
                return True

            def leer(self):
                return eventos.pop(0) if eventos else [{"tipo": "tecla", "tecla": "esc"}]
        with mock.patch.object(juego, "_entorno", Entorno()),                 mock.patch.object(raton, "activar_raton"), mock.patch.object(raton, "desactivar_raton"),                 mock.patch("shutil.get_terminal_size", return_value=os.terminal_size((60, 20))),                 mock.patch.dict(imagenes._capacidad, {"protocolo": "kitty", "imagenes": True}):
            pantalla.ver_modelo(lambda x, y: x * y, estilo=estilo, giro=10, inclinacion=20)
        return self.real.getvalue()

    def test_con_imagen(self):
        salida = self.ver("imagen")
        self.assertGreaterEqual(salida.count("_Ga=T"), 3)
        # el arrastre gira 4 grados por columna y 8 por fila
        self.assertIn("giro 354°", salida)
        self.assertTrue(salida.endswith("[?1049l"))

    def test_con_bloques(self):
        salida = self.ver("bloques")
        self.assertIn("▀", salida)
        self.assertNotIn("_G", salida)


if __name__ == "__main__":
    unittest.main()
