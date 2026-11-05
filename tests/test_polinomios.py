"""Polinomios, Ruffini, raíces y la ecuación de segundo grado."""

import math
import re
import unittest
from fractions import Fraction

import pantalla

from test_pantalla import Base


def sin_colores(texto):
    return re.sub(r"\x1b\[[0-9;]*m", "", texto)


class TestPolinomio(unittest.TestCase):
    def test_escribir_y_leer(self):
        p = pantalla.polinomio("2x^3 - 3x + 1")
        self.assertEqual(str(p), "2x³ - 3x + 1")
        self.assertEqual(p.coeficientes, [2, 0, -3, 1])
        self.assertEqual(p.grado, 3)
        self.assertEqual(pantalla.polinomio("2x³-3x+1"), p)
        self.assertEqual(pantalla.polinomio("x**2 + 2*x"), pantalla.Polinomio(1, 2, 0))
        self.assertEqual(str(pantalla.polinomio("x² + (1/2)x - 3")), "x² + (1/2)x - 3")
        self.assertEqual(str(pantalla.polinomio("-x")), "-x")
        self.assertEqual(str(pantalla.Polinomio(0)), "0")
        self.assertEqual(pantalla.polinomio([1, 0, -1]), pantalla.polinomio("x^2 - 1"))
        with self.assertRaises(ValueError) as e:
            pantalla.polinomio("2y + 1")
        self.assertIn("no entiendo", str(e.exception))
        with self.assertRaises(ValueError):
            pantalla.polinomio("")

    def test_cuentas(self):
        p = pantalla.polinomio("2x^3 - 3x + 1")
        q = pantalla.polinomio("x^2 - 1")
        self.assertEqual(str(p + q), "2x³ + x² - 3x")
        self.assertEqual(str(p - p), "0")
        self.assertEqual(str(p * p), "4x⁶ - 12x⁴ + 4x³ + 9x² - 6x + 1")
        self.assertEqual(q ** 2, q * q)
        self.assertEqual(str(2 * q + 1), "2x² - 1")
        self.assertEqual(str(q / 2), "(1/2)x² - 1/2")
        self.assertEqual(p(2), 11)
        self.assertEqual(p("1/2"), Fraction(-1, 4))
        self.assertEqual(p(1), 0)
        self.assertEqual(p(0.5), -0.25)
        self.assertEqual(str(p.derivada()), "6x² - 3")
        with self.assertRaises(TypeError) as e:
            p / q
        self.assertIn("dividir_polinomios", str(e.exception))

    def test_dividir(self):
        c, r = pantalla.dividir_polinomios("x^3 - 1", "x - 1")
        self.assertEqual((str(c), str(r)), ("x² + x + 1", "0"))
        c, r = pantalla.dividir_polinomios("x^3 + 2x + 5", "x^2 + 1")
        self.assertEqual((str(c), str(r)), ("x", "x + 5"))
        with self.assertRaises(ZeroDivisionError):
            pantalla.dividir_polinomios("x", 0)

    def test_se_puede_dibujar(self):
        p = pantalla.polinomio("x^2 - 4")
        lineas = []
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            pantalla.grafica(p, -3, 3, ancho=30, alto=8)
        self.assertIn("┼", buf.getvalue())


class TestRaices(unittest.TestCase):
    def test_raices(self):
        self.assertEqual(pantalla.raices("x^2 - 5x + 6"), [2, 3])
        self.assertEqual(pantalla.raices("6x^2 - 5x + 1"), [Fraction(1, 3), Fraction(1, 2)])
        self.assertEqual(pantalla.raices("x^3 - x^2"), [0, 0, 1])
        self.assertEqual(pantalla.raices("x^2 + 1"), [])
        r = pantalla.raices("x^2 - 2")
        self.assertAlmostEqual(r[0], -math.sqrt(2))
        self.assertAlmostEqual(pantalla.raices("x^3 - 2")[0], 2 ** (1 / 3))
        self.assertEqual(pantalla.raices("x^4 - 5x^2 + 4"), [-2, -1, 1, 2])
        self.assertEqual(pantalla.raices(7), [])
        with self.assertRaises(ValueError):
            pantalla.raices(0)

    def test_factorizar(self):
        self.assertEqual(pantalla.factorizar_polinomio("x^3 - 2x^2 - x + 2"), "(x - 1)·(x + 1)·(x - 2)")
        self.assertEqual(pantalla.factorizar_polinomio("2x^2 - 2"), "2·(x - 1)·(x + 1)")
        self.assertEqual(pantalla.factorizar_polinomio("4x^2 - 4x + 1"), "4·(x - 1/2)²")
        self.assertEqual(pantalla.factorizar_polinomio("x^4 - 1"), "(x - 1)·(x + 1)·(x² + 1)")
        self.assertEqual(pantalla.factorizar_polinomio("-x^3 + x"), "-x·(x - 1)·(x + 1)")
        self.assertEqual(pantalla.factorizar_polinomio("x^2 + 1"), "x² + 1")


class TestPasos(Base):
    def test_ruffini(self):
        s = sin_colores(self.captura(pantalla.ruffini, "2x^3 - 3x + 1", 1, pasos=True))
        self.assertEqual(s.split("\n")[:4], ["  │   2   0  -3   1", "1 │       2   2  -1",
                                             "──┼────────────────", "  │   2   2  -1   0"])
        self.assertIn("Cociente: 2x² + 2x - 1    Resto: 0", s)
        c, r = self.ultimo_resultado
        self.assertEqual((str(c), r), ("2x² + 2x - 1", 0))
        c, r = pantalla.ruffini("x^2 + 1", 2)
        self.assertEqual((str(c), r), ("x + 2", 5))

    def test_factorizar_con_pasos(self):
        s = sin_colores(self.captura(pantalla.factorizar_polinomio, "x^3 - x", pasos=True))
        self.assertIn("x = 0 es raíz", s)
        self.assertIn("x = 1 es raíz:", s)
        self.assertTrue(s.rstrip().endswith("x³ - x = x·(x - 1)·(x + 1)"), s)

    def test_segundo_grado(self):
        s = self.captura(pantalla.ecuacion_segundo_grado, 1, -5, 6, pasos=True)
        self.assertEqual(s, "x² - 5x + 6 = 0\nΔ = b² - 4ac = (-5)² - 4·1·6 = 25 - 24 = 1\n"
                            "x = (-b ± √Δ) / 2a = (5 ± 1) / 2\nx₁ = 3    x₂ = 2\n")
        self.assertEqual(self.ultimo_resultado, [3, 2])
        s = self.captura(pantalla.ecuacion_segundo_grado, 1, -1, -1, pasos=True)
        self.assertIn("= 1 + 4 = 5", s)
        self.assertIn("(1 ± √5) / 2", s)
        self.assertIn("x₁ ≈ 1.618    x₂ ≈ -0.618", s)
        self.assertIn("no tiene soluciones", self.captura(pantalla.ecuacion_segundo_grado, 1, 0, 1, pasos=True))
        self.assertIn("doble", self.captura(pantalla.ecuacion_segundo_grado, 1, 2, 1, pasos=True))
        self.assertEqual(pantalla.ecuacion_segundo_grado(2, 3, -2), [Fraction(1, 2), -2])
        self.assertEqual(pantalla.ecuacion_segundo_grado(1, 0, 1), [])
        self.assertEqual(pantalla.ecuacion_segundo_grado(1, 2, 1), [-1])
        with self.assertRaises(ValueError) as e:
            pantalla.ecuacion_segundo_grado(0, 2, 1)
        self.assertIn("no es de segundo grado", str(e.exception))


if __name__ == "__main__":
    unittest.main()
