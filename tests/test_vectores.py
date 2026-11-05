"""Vectores: las cuentas, el Vector con + y *, los pasos y el dibujo con flechas."""

import copy
import math
import re
import unittest
from fractions import Fraction

import pantalla
from pantalla import matrices

from test_pantalla import Base, con_teclas


def sin_colores(texto):
    return re.sub(r"\x1b\[[0-9;]*m", "", texto)


class TestCuentas(unittest.TestCase):
    def test_sumar_restar_multiplicar(self):
        self.assertEqual(pantalla.sumar_vectores((1, 2), [3, 4]), (4, 6))
        self.assertEqual(pantalla.restar_vectores((5, 5), (1, 2)), (4, 3))
        self.assertEqual(pantalla.multiplicar_vector(3, (1, -2)), (3, -6))
        self.assertEqual(pantalla.multiplicar_vector((1, -2), "1/2"), (Fraction(1, 2), -1))
        self.assertEqual(pantalla.sumar_vectores(("1/2", "1/3"), ("1/2", "1/3")), (1, Fraction(2, 3)))
        self.assertEqual(pantalla.vector_entre((1, 2), (4, 6)), (3, 4))
        with self.assertRaises(ValueError) as e:
            pantalla.sumar_vectores((1, 2), (1, 2, 3))
        self.assertIn("tiene 2 números y el segundo 3", str(e.exception))
        with self.assertRaises(TypeError) as e:
            pantalla.sumar_vectores(5, (1, 2))
        self.assertIn("lista de números", str(e.exception))
        with self.assertRaises(TypeError):
            pantalla.sumar_vectores((1, "hola"), (1, 2))

    def test_decimales(self):
        self.assertEqual(pantalla.sumar_vectores((0.1, 0.2), (0.2, 0.1)), (0.3, 0.3))
        self.assertIsInstance(pantalla.multiplicar_vector(0.5, (1, 2))[0], float)

    def test_producto_escalar_y_perpendiculares(self):
        self.assertEqual(pantalla.producto_escalar((1, 2, 3), (4, -5, 6)), 12)
        self.assertEqual(pantalla.producto_escalar(("1/2", 1), (2, "1/3")), Fraction(4, 3))
        self.assertTrue(pantalla.son_perpendiculares((1, 2), (-2, 1)))
        self.assertFalse(pantalla.son_perpendiculares((1, 2), (2, 1)))

    def test_modulo_unitario_distancia(self):
        self.assertEqual(pantalla.modulo((3, 4)), 5)
        self.assertIsInstance(pantalla.modulo((3, 4)), int)
        self.assertEqual(pantalla.modulo(("3/5", "4/5")), 1)
        self.assertAlmostEqual(pantalla.modulo((1, 1)), math.sqrt(2))
        self.assertEqual(pantalla.unitario((3, 4)), (Fraction(3, 5), Fraction(4, 5)))
        self.assertAlmostEqual(pantalla.unitario((1, 1))[0], math.sqrt(0.5))
        self.assertEqual(pantalla.distancia((1, 1), (4, 5)), 5)
        with self.assertRaises(ValueError):
            pantalla.unitario((0, 0))

    def test_angulo(self):
        self.assertEqual(pantalla.angulo((1, 0), (0, 1)), 90)
        self.assertEqual(pantalla.angulo((1, 0), (1, 1)), 45)
        self.assertEqual(pantalla.angulo((1, 0), (-1, 0)), 180)
        self.assertAlmostEqual(pantalla.angulo((1, 0), (0, 1), radianes=True), math.pi / 2)
        with self.assertRaises(ValueError) as e:
            pantalla.angulo((0, 0), (1, 1))
        self.assertIn("no tiene dirección", str(e.exception))

    def test_vectorial_y_mixto(self):
        self.assertEqual(pantalla.producto_vectorial((1, 0, 0), (0, 1, 0)), (0, 0, 1))
        self.assertEqual(pantalla.producto_vectorial((1, 2, 3), (4, 5, 6)), (-3, 6, -3))
        self.assertEqual(pantalla.producto_mixto((1, 0, 0), (0, 1, 0), (0, 0, 1)), 1)
        self.assertEqual(pantalla.producto_mixto((1, 2, 3), (4, 5, 6), (7, 8, 9)), 0)
        with self.assertRaises(ValueError) as e:
            pantalla.producto_vectorial((1, 2), (3, 4))
        self.assertIn("3 números", str(e.exception))

    def test_proyeccion_paralelos_independientes(self):
        self.assertEqual(pantalla.proyeccion((2, 3), (1, 0)), (2, 0))
        self.assertEqual(pantalla.proyeccion((1, 1), (2, 0)), (1, 0))
        self.assertTrue(pantalla.son_paralelos((1, 2), (3, 6)))
        self.assertTrue(pantalla.son_paralelos((0, 0), (3, 6)))
        self.assertFalse(pantalla.son_paralelos((1, 2), (2, 1)))
        self.assertTrue(pantalla.son_independientes((1, 0), (0, 1)))
        self.assertFalse(pantalla.son_independientes((1, 2, 3), (2, 4, 6)))
        self.assertFalse(pantalla.son_independientes([(1, 0), (0, 1), (1, 1)]))
        with self.assertRaises(ValueError):
            pantalla.proyeccion((1, 2), (0, 0))
        with self.assertRaises(ValueError):
            pantalla.son_independientes((1, 0), (1, 2, 3))


class TestVector(unittest.TestCase):
    def test_operaciones(self):
        u = pantalla.Vector(3, 4)
        v = pantalla.Vector([1, 2])
        self.assertEqual(repr(u), "(3, 4)")
        self.assertEqual(str(pantalla.Vector("1/2", -1)), "(1/2, -1)")
        self.assertEqual(u + v, (4, 6))
        self.assertEqual(u - (1, 1), (2, 3))
        self.assertEqual((1, 1) + u, (4, 5))
        self.assertEqual((5, 5) - u, (2, 1))
        self.assertEqual(2 * u - v, (5, 6))
        self.assertEqual(u * 2, (6, 8))
        self.assertEqual(u / 2, (Fraction(3, 2), 2))
        self.assertEqual(-u, (-3, -4))
        self.assertEqual(abs(u), 5)
        self.assertIsInstance(u + v, pantalla.Vector)
        x, y = u
        self.assertEqual((x, y), (3, 4))
        self.assertEqual(copy.deepcopy(u), u)
        self.assertIsInstance(copy.copy(u), pantalla.Vector)

    def test_errores(self):
        u = pantalla.Vector(3, 4)
        with self.assertRaises(TypeError) as e:
            u * u
        self.assertIn("producto_escalar", str(e.exception))
        with self.assertRaises(ZeroDivisionError):
            u / 0
        with self.assertRaises(ValueError):
            pantalla.Vector()


class TestPasos(Base):
    def test_producto_escalar(self):
        s = self.captura(pantalla.producto_escalar, (1, 2, 3), (4, -5, 6), pasos=True)
        self.assertEqual(sin_colores(s), "u · v = 1·4 + 2·(-5) + 3·6 = 4 - 10 + 18 = 12\n")
        self.assertEqual(self.ultimo_resultado, 12)

    def test_modulo(self):
        self.assertEqual(self.captura(pantalla.modulo, (3, 4), pasos=True), "|u| = √(3² + 4²) = √25 = 5\n")
        self.assertEqual(self.captura(pantalla.modulo, (2, 2), pasos=True), "|u| = √(2² + 2²) = √8 = 2√2 ≈ 2.8284\n")
        self.assertEqual(self.captura(pantalla.modulo, (-1, 1), pasos=True), "|u| = √((-1)² + 1²) = √2 ≈ 1.4142\n")

    def test_angulo(self):
        s = self.captura(pantalla.angulo, (1, 2), (3, 1), pasos=True)
        self.assertEqual(s, "cos α = u · v / (|u|·|v|) = 5 / (√5·√10) ≈ 0.7071\nα ≈ 45°\n")

    def test_vectorial(self):
        s = self.captura(pantalla.producto_vectorial, (1, 2, 3), (4, 5, 6), pasos=True)
        self.assertEqual(s.split("\n")[1], "u × v = │ 1  2  3 │ = (2·6 - 3·5, 3·4 - 1·6, 1·5 - 2·4) = (-3, 6, -3)")
        self.assertEqual(len(s.strip("\n").split("\n")), 3)


class TestDibujar(Base):
    ANCHO = 80
    ALTO = 24

    def test_vector(self):
        self.assertEqual(sin_colores(self.captura(pantalla.vector, (3, -1, 2), nombre="u")), "u = (3, -1, 2)\n")
        self.assertEqual(self.ultimo_resultado, (14, 1))
        p = self.pinta(pantalla.vector, (3, -1), 5, 3)
        self.assertEqual(p.linea(3).strip(), "(3, -1)")
        s = sin_colores(self.captura(pantalla.vector, (3, -1), nombre="u", vertical=True))
        self.assertIn("u = │ 3  │", s)

    def test_dibujar_vectores(self):
        s = sin_colores(self.captura(pantalla.dibujar_vectores, {"u": (3, 2), "v": (-1, 4)}))
        lineas = s.split("\n")
        self.assertTrue(any("↗u" in l for l in lineas), s)
        self.assertTrue(any("v↑" in l for l in lineas), s)
        self.assertTrue(lineas[-2].lstrip().startswith("-2"), s)
        self.assertIn("┼", s)
        ancho, alto = self.ultimo_resultado
        self.assertEqual(alto, len(lineas) - 1)
        self.assertLessEqual(ancho, 41)

    def test_dibujar_desde_un_punto_y_lista(self):
        s = sin_colores(self.captura(pantalla.dibujar_vectores, [(2, 1), ((2, 1), (1, 3))], cuadricula=False))
        self.assertIn("u", s)
        self.assertIn("v", s)
        self.assertNotIn("·", s)
        p = self.pinta(pantalla.dibujar_vectores, [(-4, -4)], 2, 2)
        self.assertIn("↙", p.texto())

    def test_estilos(self):
        fino = sin_colores(self.captura(pantalla.dibujar_vectores, [(5, 0), (3, 2)]))
        self.assertTrue(any(0x2800 < ord(ch) <= 0x28ff for ch in fino), fino)
        self.assertNotIn("╱", fino)
        # una raya por el eje sale recta, en la misma fila que el eje
        fila = [l for l in fino.split("\n") if "┼" in l][0]
        self.assertIn("⠤⠤⠤", fila)
        rayas = sin_colores(self.captura(pantalla.dibujar_vectores, [(5, 0), (3, 2)], estilo="rayas"))
        self.assertFalse(any(0x2800 <= ord(ch) <= 0x28ff for ch in rayas), rayas)
        self.assertIn("╱", rayas)
        # en los bordes no se sale del dibujo
        for v in ([(-34, -31), (-1, 1)], [(5, 1), (-11, 6)], [(-34, -12)]):
            s = sin_colores(self.captura(pantalla.dibujar_vectores, v, ancho=15, alto=9))
            self.assertIn("u", s)
        with self.assertRaises(ValueError) as e:
            pantalla.dibujar_vectores([(1, 2)], estilo="gordo")
        self.assertIn("rayas", str(e.exception))

    def test_vectores_grandes(self):
        s = sin_colores(self.captura(pantalla.dibujar_vectores, [(30, -20), (-15, 40)]))
        self.assertIn("↘", s)
        self.assertIn(" 50", s)

    def test_errores(self):
        with self.assertRaises(ValueError) as e:
            pantalla.dibujar_vectores([(1, 2, 3)])
        self.assertIn("2 números", str(e.exception))
        with self.assertRaises(ValueError):
            pantalla.dibujar_vectores({})
        with self.assertRaises(ValueError):
            pantalla.dibujar_vectores([(1, 2)], ancho=5)

    def test_pedir_vector(self):
        with con_teclas(matrices, ["3", "enter", "-", "1", "enter"]):
            self.captura(pantalla.pedir_vector, "u", dimension=2)
        self.assertEqual(self.ultimo_resultado, (3, -1))
        self.assertIsInstance(self.ultimo_resultado, pantalla.Vector)
        with con_teclas(matrices, ["esc"]):
            self.captura(pantalla.pedir_vector)
        self.assertIsNone(self.ultimo_resultado)

    def test_ayuda_y_parecidas(self):
        self.assertIn("Vectores", dict(pantalla._GRUPOS))
        with self.assertRaises(AttributeError) as e:
            pantalla.producto_punto
        self.assertIn("producto_escalar", str(e.exception))


if __name__ == "__main__":
    unittest.main()
