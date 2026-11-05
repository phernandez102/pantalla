"""Estadística y cambios de base."""

import re
import unittest

import pantalla

from test_pantalla import Base


def sin_colores(texto):
    return re.sub(r"\x1b\[[0-9;]*m", "", texto)


NOTAS = [5, 7, 7, 8, 6, 9, 7, 4]


class TestCuentas(unittest.TestCase):
    def test_media_mediana_moda(self):
        self.assertEqual(pantalla.media(NOTAS), 6.625)
        self.assertEqual(pantalla.media([2, 4]), 3)
        self.assertIsInstance(pantalla.media([2, 4]), int)
        self.assertEqual(pantalla.media({3: 2, 5: 2}), 4)
        self.assertEqual(pantalla.mediana([5, 9, 7]), 7)
        self.assertEqual(pantalla.mediana([5, 9, 7, 8]), 7.5)
        self.assertEqual(pantalla.moda(NOTAS), 7)
        self.assertEqual(pantalla.moda([1, 1, 2, 2, 3]), [1, 2])
        self.assertEqual(pantalla.moda(["rojo", "azul", "rojo"]), "rojo")
        with self.assertRaises(ValueError):
            pantalla.media([])
        with self.assertRaises(TypeError) as e:
            pantalla.media([1, "dos"])
        self.assertIn("'dos'", str(e.exception))

    def test_dispersion(self):
        datos = [2, 4, 4, 4, 5, 5, 7, 9]
        self.assertEqual(pantalla.varianza(datos), 4)
        self.assertEqual(pantalla.desviacion(datos), 2)
        self.assertAlmostEqual(pantalla.varianza(datos, muestra=True), 32 / 7)
        self.assertAlmostEqual(pantalla.desviacion(NOTAS), 1.494782592888)
        self.assertEqual(pantalla.cuartiles([1, 2, 3, 4, 5, 6, 7, 8]), (2.5, 4.5, 6.5))
        self.assertEqual(pantalla.cuartiles([1, 2, 3, 4, 5, 6, 7]), (2, 4, 6))


class TestDibujos(Base):
    ANCHO = 80
    ALTO = 30

    def test_tabla_frecuencias(self):
        s = sin_colores(self.captura(pantalla.tabla_frecuencias, NOTAS))
        self.assertIn("│ 7     │  3 │  6 │ 0.375 │ 37.5 % │", s)
        self.assertIn("│ Total │  8 │    │     1 │  100 % │", s)
        self.assertEqual(self.ultimo_resultado["7"], 3)
        s = sin_colores(self.captura(pantalla.tabla_frecuencias, [1, 2, 3, 4], intervalos=2))
        self.assertIn("[1, 2.5)", s)
        self.assertIn("[2.5, 4]", s)
        s = sin_colores(self.captura(pantalla.tabla_frecuencias, ["rojo", "azul", "rojo"]))
        self.assertIn("rojo", s)

    def test_histograma(self):
        s = sin_colores(self.captura(pantalla.histograma, NOTAS, alto=6))
        lineas = s.rstrip("\n").split("\n")
        self.assertEqual(lineas[-1], " 4   5   6   7   8   9")
        self.assertTrue(lineas[-2].startswith("───"))
        self.assertEqual(lineas[0].strip(), "3")
        self.assertIn("██", lineas[1])
        self.assertEqual(self.ultimo_resultado, (23, 9))
        s = sin_colores(self.captura(pantalla.histograma, [1, 2, 3, 4], intervalos=2, valores=False))
        self.assertIn("[1, 2.5)", s)
        with self.assertRaises(ValueError):
            pantalla.histograma(NOTAS, alto=1)

    def test_estadisticas(self):
        s = sin_colores(self.captura(pantalla.estadisticas, NOTAS))
        self.assertIn("│ Media             │       6.625 │", s)
        self.assertIn("5.5, 7, 7.5", s)
        r = self.ultimo_resultado
        self.assertEqual((r["n"], r["moda"], r["recorrido"]), (8, 7, 5))


class TestBases(Base):
    def test_cambiar(self):
        self.assertEqual(pantalla.a_binario(45), "101101")
        self.assertEqual(pantalla.a_hexadecimal(255), "FF")
        self.assertEqual(pantalla.cambiar_base(35, 36), "Z")
        self.assertEqual(pantalla.cambiar_base(0, 2), "0")
        self.assertEqual(pantalla.cambiar_base(-10, 2), "-1010")
        with self.assertRaises(ValueError):
            pantalla.cambiar_base(5, 1)

    def test_a_decimal(self):
        self.assertEqual(pantalla.a_decimal("101101"), 45)
        self.assertEqual(pantalla.a_decimal("ff", 16), 255)
        self.assertEqual(pantalla.a_decimal("0x2F"), 47)
        self.assertEqual(pantalla.a_decimal("-101"), -5)
        with self.assertRaises(ValueError) as e:
            pantalla.a_decimal("102")
        self.assertIn("no existe la cifra 2", str(e.exception))

    def test_pasos(self):
        s = sin_colores(self.captura(pantalla.a_binario, 45, pasos=True))
        self.assertEqual(s.split("\n")[0], "45 : 2 = 22   resto 1")
        self.assertIn("45 = 101101₂", s)
        s = sin_colores(self.captura(pantalla.a_hexadecimal, 2024, pasos=True))
        self.assertIn("resto 14 (E)", s)
        s = sin_colores(self.captura(pantalla.a_decimal, "101101", pasos=True))
        self.assertEqual(s, "101101₂ = 1·2⁵ + 0·2⁴ + 1·2³ + 1·2² + 0·2¹ + 1·2⁰ = 32 + 8 + 4 + 1 = 45\n")


if __name__ == "__main__":
    unittest.main()
