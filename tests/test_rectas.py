"""Rectas en el plano."""

import unittest

import pantalla

from test_pantalla import Base


class TestRecta(unittest.TestCase):
    def test_por_dos_puntos(self):
        r = pantalla.recta((1, 3), (2, 5))
        self.assertEqual(str(r), "2x - y + 1 = 0")
        self.assertEqual(r.explicita(), "y = 2x + 1")
        self.assertEqual(r.punto_pendiente(), "y - 3 = 2(x - 1)")
        self.assertEqual(r.vectorial(), "(x, y) = (1, 3) + t·(1, 2)")
        self.assertEqual(r.parametricas(), "x = 1 + t,  y = 3 + 2t")
        self.assertEqual(r.continua(), "(x - 1)/1 = (y - 3)/2")
        self.assertEqual((r.pendiente, r.ordenada, r(4)), (2, 1, 9))
        self.assertTrue(r.pasa_por((0, 1)))
        self.assertFalse(r.pasa_por((0, 0)))
        with self.assertRaises(ValueError):
            pantalla.recta((1, 1), (1, 1))

    def test_otras_formas(self):
        self.assertEqual(str(pantalla.recta((1, 3), vector=(1, 2))), "2x - y + 1 = 0")
        self.assertEqual(str(pantalla.Recta((0, 1), pendiente="1/2")), "x - 2y + 2 = 0")
        r = pantalla.recta("y = -1/2x + 3")
        self.assertEqual(str(r), "x + 2y - 6 = 0")
        self.assertEqual(r.explicita(), "y = -(1/2)x + 3")
        self.assertEqual(r.vectorial(), "(x, y) = (0, 3) + t·(2, -1)")
        v = pantalla.recta("x = 3")
        self.assertEqual((v.explicita(), v.pendiente), ("x = 3", None))
        self.assertIn("no tiene ecuación continua", v.continua())
        with self.assertRaises(ValueError):
            v(1)
        self.assertEqual(pantalla.recta("y = 5").punto_pendiente(), "y = 5")
        with self.assertRaises(ValueError):
            pantalla.recta("y + 2")
        with self.assertRaises(TypeError):
            pantalla.recta((1, 2))

    def test_dos_rectas(self):
        self.assertEqual(pantalla.posicion_rectas("y = 2x", "y = 2x + 1"), "paralelas")
        self.assertEqual(pantalla.posicion_rectas("y = 2x", "4x - 2y = 0"), "coincidentes")
        self.assertEqual(pantalla.posicion_rectas("y = x", "y = -x"), "secantes")
        self.assertEqual(pantalla.recta("y = 2x"), pantalla.recta("4x - 2y = 0"))
        self.assertEqual(pantalla.interseccion_rectas("y = 2x + 1", "x + y = 4"), (1, 3))
        self.assertIsNone(pantalla.interseccion_rectas("y = 2x", "y = 2x + 1"))
        self.assertEqual(pantalla.angulo_rectas("y = x", "y = -x"), 90)
        self.assertEqual(pantalla.angulo_rectas("y = 0", "y = x"), 45)

    def test_distancia(self):
        self.assertEqual(pantalla.distancia_punto_recta((0, 0), "3x + 4y - 10 = 0"), 2)
        self.assertAlmostEqual(pantalla.distancia_punto_recta((1, 1), "y = x + 1"), 2 ** -0.5)


class TestPasos(Base):
    def test_ecuaciones(self):
        s = self.captura(pantalla.ecuaciones_recta, (1, 3), (2, 5))
        self.assertIn("General:          2x - y + 1 = 0", s)
        self.assertIn("Punto-pendiente:  y - 3 = 2(x - 1)", s)
        self.assertEqual(len(s.strip().split("\n")), 6)
        self.assertIsInstance(self.ultimo_resultado, pantalla.Recta)

    def test_interseccion_y_distancia(self):
        s = self.captura(pantalla.interseccion_rectas, "y = 2x + 1", "x + y = 4", pasos=True)
        self.assertIn("Se cortan en (1, 3)", s)
        s = self.captura(pantalla.distancia_punto_recta, (0, 0), "3x + 4y - 10 = 0", pasos=True)
        self.assertEqual(s, "d = |3·0 + 4·0 + (-10)| / √(3² + 4²) = 10 / 5 = 2\n")


if __name__ == "__main__":
    unittest.main()
