"""Matrices, fracciones, números y gráficas."""

import math
import re
import unittest
from fractions import Fraction
from unittest import mock

import pantalla
from pantalla import componentes

from test_pantalla import Base, PantallaVirtual, con_teclas


def sin_colores(texto):
    return re.sub(r"\x1b\[[0-9;]*m", "", texto)


class TestCuentasConMatrices(unittest.TestCase):
    A = [[1, 2], [3, 4]]

    def test_sumar_restar(self):
        self.assertEqual(pantalla.sumar_matrices(self.A, [[10, 20], [30, 40]]), [[11, 22], [33, 44]])
        self.assertEqual(pantalla.restar_matrices([[5, 5], [5, 5]], self.A), [[4, 3], [2, 1]])
        with self.assertRaises(ValueError) as e:
            pantalla.sumar_matrices(self.A, [[1, 2, 3]])
        self.assertIn("mismo tamaño", str(e.exception))

    def test_multiplicar(self):
        self.assertEqual(pantalla.multiplicar_matrices(self.A, [[5], [6]]), [[17], [39]])
        self.assertEqual(pantalla.multiplicar_matrices(3, self.A), [[3, 6], [9, 12]])
        self.assertEqual(pantalla.multiplicar_matrices(self.A, 0.5), [[0.5, 1.0], [1.5, 2.0]])
        with self.assertRaises(ValueError) as e:
            pantalla.multiplicar_matrices([[1, 2, 3]], [[1, 2]])
        self.assertIn("columnas de la primera (3)", str(e.exception))

    def test_transpuesta_identidad_traza(self):
        self.assertEqual(pantalla.transpuesta([[1, 2, 3], [4, 5, 6]]), [[1, 4], [2, 5], [3, 6]])
        self.assertEqual(pantalla.identidad(2), [[1, 0], [0, 1]])
        self.assertEqual(pantalla.traza(self.A), 5)
        with self.assertRaises(ValueError):
            pantalla.identidad(0)
        with self.assertRaises(ValueError) as e:
            pantalla.traza([[1, 2, 3]])
        self.assertIn("cuadradas", str(e.exception))

    def test_determinante(self):
        self.assertEqual(pantalla.determinante(self.A), -2)
        self.assertEqual(pantalla.determinante([[2, 0, 1], [1, 3, 2], [1, 1, 2]]), 6)
        self.assertEqual(pantalla.determinante([[1, 2], [2, 4]]), 0)
        self.assertEqual(pantalla.determinante([[0, 1], [1, 0]]), -1)
        self.assertEqual(pantalla.determinante([[Fraction(1, 2), 0], [0, 4]]), 2)

    def test_inversa_exacta(self):
        self.assertEqual(pantalla.inversa([[2, 1], [1, 1]]), [[1, -1], [-1, 2]])
        inv = pantalla.inversa(self.A)
        self.assertEqual(inv, [[-2, 1], [Fraction(3, 2), Fraction(-1, 2)]])
        self.assertEqual(repr(inv), "[[-2, 1], [3/2, -1/2]]")
        self.assertEqual(pantalla.multiplicar_matrices(self.A, inv), pantalla.identidad(2))
        self.assertEqual(pantalla.inversa([[1.0, 2], [3, 4]]), [[-2.0, 1.0], [1.5, -0.5]])
        with self.assertRaises(ValueError) as e:
            pantalla.inversa([[1, 2], [2, 4]])
        self.assertIn("determinante es 0", str(e.exception))

    def test_potencia_y_rango(self):
        self.assertEqual(pantalla.potencia_matriz([[1, 1], [1, 0]], 5), [[8, 5], [5, 3]])
        self.assertEqual(pantalla.potencia_matriz(self.A, 0), [[1, 0], [0, 1]])
        self.assertEqual(pantalla.potencia_matriz([[2, 1], [1, 1]], -1), [[1, -1], [-1, 2]])
        self.assertEqual(pantalla.rango([[1, 2], [2, 4]]), 1)
        self.assertEqual(pantalla.rango([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), 2)
        self.assertEqual(pantalla.rango([[0, 0], [0, 0]]), 0)

    def test_escalonar(self):
        self.assertEqual(pantalla.escalonar([[1, 2, 3], [4, 5, 6], [7, 8, 10]]),
                         [[1, 2, 3], [0, -3, -6], [0, 0, 1]])
        self.assertEqual(pantalla.escalonar([[2, 1], [4, 3]], reducida=True), [[1, 0], [0, 1]])

    def test_sistemas(self):
        self.assertEqual(pantalla.resolver_sistema([[2, 1], [1, -1]], [5, 1]), [2, 1])
        self.assertEqual(pantalla.resolver_sistema([[2, 1, 5], [1, -1, 1]]), [2, 1])
        self.assertEqual(pantalla.resolver_sistema([[1, 2, -1], [2, -1, 3], [3, 1, 1]], [2, 9, 8]), [1, 2, 3])
        self.assertEqual(pantalla.resolver_sistema([[0, 2, 1], [1, 1, 1], [2, 1, -1]], [5, 6, 1]),
                         [Fraction(9, 5), Fraction(4, 5), Fraction(17, 5)])
        self.assertIsNone(pantalla.resolver_sistema([[1, 1], [2, 2]], [1, 3]))
        self.assertEqual(pantalla.clasificar_sistema([[1, 1], [1, -1]], [3, 1]), "compatible determinado")
        self.assertEqual(pantalla.clasificar_sistema([[1, 1], [2, 2]], [1, 2]), "compatible indeterminado")
        self.assertEqual(pantalla.clasificar_sistema([[1, 1, 1], [2, 2, 3]]), "incompatible")
        with self.assertRaises(ValueError):
            pantalla.resolver_sistema([[1, 1], [1, -1]], [1, 2, 3])

    def test_numeros_en_texto_y_errores(self):
        self.assertEqual(pantalla.sumar_matrices([["1/2", "2,5"]], [[Fraction(1, 2), 0.5]]), [[1.0, 3.0]])
        with self.assertRaises(TypeError) as e:
            pantalla.determinante([[1, "hola"], [3, 4]])
        self.assertIn("fila 1, columna 2", str(e.exception))


class TestDibujosDeMatrices(Base):
    ANCHO = 70
    ALTO = 40

    def test_matriz_ampliada(self):
        salida = self.captura(pantalla.matriz, [[1, 2, 5], [3, 4, 6]], ampliada=True)
        self.assertIn("│ 1  2 │ 5 │", salida)

    def test_lo_que_no_cabe_por_abajo_no_se_escribe(self):
        # si no, la terminal lo amontona todo en la última fila
        from pantalla.numeros import _sacar
        lineas = ["uno", "dos", "tres", "cuatro", "cinco"]
        with mock.patch("pantalla.numeros._es_terminal", return_value=True):
            salida = self.captura(_sacar, lineas, 1, self.ALTO - 2, "prueba")
        self.assertIn("\x1b[%d;1Htres" % self.ALTO, salida)
        self.assertNotIn("cuatro", salida)
        # escribiendo a un archivo no se corta nada
        salida = self.captura(_sacar, lineas, 1, self.ALTO - 2, "prueba")
        self.assertIn("\x1b[%d;1Hcinco" % (self.ALTO + 2), salida)

    def test_escalonar_con_pasos(self):
        salida = sin_colores(self.captura(pantalla.escalonar, [[1, 2], [3, 4]], pasos=True))
        self.assertIn("F2 → F2 - 3·F1", salida)
        self.assertEqual(self.ultimo_resultado, [[1, 2], [0, -2]])

    def test_resolver_con_pasos(self):
        salida = sin_colores(self.captura(pantalla.resolver_sistema, [[2, 1], [1, -1]], [5, 1], pasos=True))
        self.assertIn("F1 → (1/2)·F1", salida)
        self.assertIn("Solución: x = 2,  y = 1", salida)
        salida = sin_colores(self.captura(pantalla.resolver_sistema, [[1, 1], [2, 2]], [1, 3], pasos=True))
        self.assertIn("incompatible: no tiene solución", salida)


class TestFracciones(Base):
    def test_fraccion(self):
        self.assertEqual(pantalla.fraccion(3, 4), Fraction(3, 4))
        self.assertEqual(pantalla.fraccion("6/8"), Fraction(3, 4))
        self.assertEqual(pantalla.fraccion("1 1/2"), Fraction(3, 2))
        self.assertEqual(pantalla.fraccion(0.75), Fraction(3, 4))
        self.assertEqual(pantalla.fraccion("0,5"), Fraction(1, 2))
        self.assertIsInstance(pantalla.fraccion(1, 3), pantalla.Fraccion)
        self.assertEqual(repr([pantalla.fraccion(1, 3)]), "[1/3]")
        with self.assertRaises(ZeroDivisionError):
            pantalla.fraccion(1, 0)
        with self.assertRaises(ValueError):
            pantalla.fraccion("tres cuartos")

    def test_calcular(self):
        self.assertEqual(pantalla.calcular("1/2 + 1/3"), Fraction(5, 6))
        self.assertEqual(pantalla.calcular("(2 + 3) * 4"), 20)
        self.assertEqual(pantalla.calcular("3/4 : 1/2"), Fraction(3, 2))
        self.assertEqual(pantalla.calcular("3/4 ÷ 1/2"), Fraction(3, 2))
        self.assertEqual(pantalla.calcular("2^10"), 1024)
        self.assertEqual(pantalla.calcular("2 x 3 · 4"), 24)
        self.assertEqual(pantalla.calcular("0,5 + 1/4"), Fraction(3, 4))
        self.assertIsInstance(pantalla.calcular("1 + 1"), int)
        with self.assertRaises(ZeroDivisionError):
            pantalla.calcular("1/0")
        with self.assertRaises(ValueError):
            pantalla.calcular("import os")
        with self.assertRaises(ValueError):
            pantalla.calcular("2 ^ (1/2)")

    def test_pedir_fraccion(self):
        respuestas = iter(["hola", "1/0", "3/4"])
        with mock.patch("builtins.input", lambda: next(respuestas)):
            salida = self.captura(pantalla.pedir_fraccion, "Fracción: ")
        self.assertEqual(self.ultimo_resultado, Fraction(3, 4))
        self.assertIn("no es una fracción", salida)
        self.assertIn("no puede ser 0", salida)

    def test_escribir_cuenta(self):
        salida = sin_colores(self.captura(pantalla.escribir_cuenta, "1/2 + 1/3"))
        self.assertEqual(salida, "1   1   5\n─ + ─ = ─\n2   3   6\n")
        self.assertEqual(self.ultimo_resultado, (9, 3))
        salida = sin_colores(self.captura(pantalla.escribir_cuenta, "2 + 3 * 4"))
        self.assertEqual(salida, "2 + 3 · 4 = 14\n")
        salida = sin_colores(self.captura(pantalla.escribir_cuenta, "1/2 + 1/3", resultado=False))
        self.assertNotIn("=", salida)
        p = self.pinta(pantalla.escribir_cuenta, pantalla.fraccion(7, 8), 5, 2)
        self.assertEqual([p.linea(k)[4:5] for k in (2, 3, 4)], ["7", "─", "8"])


class TestEnteros(Base):
    def test_mcd_mcm(self):
        self.assertEqual(pantalla.mcd(12, 18), 6)
        self.assertEqual(pantalla.mcd(12, 18, 30), 6)
        self.assertEqual(pantalla.mcd([8, 20]), 4)
        self.assertEqual(pantalla.mcm(4, 6), 12)
        self.assertEqual(pantalla.mcm(2, 3, 4), 12)
        with self.assertRaises(TypeError):
            pantalla.mcd(2.5, 5)

    def test_primos_y_divisores(self):
        self.assertEqual([n for n in range(20) if pantalla.es_primo(n)], [2, 3, 5, 7, 11, 13, 17, 19])
        self.assertEqual(pantalla.divisores(12), [1, 2, 3, 4, 6, 12])
        self.assertEqual(pantalla.divisores(36), [1, 2, 3, 4, 6, 9, 12, 18, 36])
        with self.assertRaises(ValueError):
            pantalla.divisores(0)

    def test_factorizar_y_descomponer(self):
        self.assertEqual(pantalla.factorizar(360), {2: 3, 3: 2, 5: 1})
        self.assertEqual(pantalla.factorizar(97), {97: 1})
        salida = sin_colores(self.captura(pantalla.descomponer, 12))
        self.assertEqual(salida, " 12 │ 2\n  6 │ 2\n  3 │ 3\n  1 │\n 12 = 2² · 3\n")
        self.assertEqual(self.ultimo_resultado, {2: 2, 3: 1})
        with self.assertRaises(ValueError):
            pantalla.factorizar(1)


def es_braille(ch):
    return 0x2800 < ord(ch) <= 0x28ff


class TestGraficas(Base):
    ANCHO = 80
    ALTO = 30

    def test_grafica_parabola(self):
        salida = sin_colores(self.captura(pantalla.grafica, lambda x: x * x, -5, 5, ancho=41, alto=11))
        lineas = salida.rstrip("\n").split("\n")
        self.assertEqual(len(lineas), 11)
        self.assertTrue(lineas[0].startswith("25 ") and es_braille(lineas[0][3]), lineas[0])
        self.assertTrue(es_braille(lineas[0][-1]))
        self.assertTrue(lineas[-2].startswith(" 0 "))
        self.assertTrue(lineas[-1].strip().startswith("-5"))
        self.assertTrue(lineas[-1].endswith("5"))

    def test_grafica_varias_y_huecos(self):
        salida = self.captura(pantalla.grafica, [math.sin, lambda x: 1 / x], -3, 3, ancho=30, alto=8)
        self.assertTrue(any(es_braille(ch) for ch in salida))
        salida = sin_colores(self.captura(pantalla.grafica, [3, 5, 2, 8], ancho=30, alto=8))
        self.assertTrue(salida.startswith("8 "))
        with self.assertRaises(ValueError):
            pantalla.grafica(math.sin, 5, 1)
        with self.assertRaises(TypeError):
            pantalla.grafica("x*x")

    def test_grafica_en_un_sitio(self):
        p = self.pinta(pantalla.grafica, lambda x: x, -1, 1, 10, 5, ancho=20, alto=6)
        self.assertTrue(any(es_braille(ch) for ch in p.linea(5)))
        self.assertEqual(p.linea(4).strip(), "")

    def test_grafica_estilos(self):
        antes = sin_colores(self.captura(pantalla.grafica, lambda x: x * x, -5, 5, ancho=41, alto=11, estilo="puntos"))
        self.assertTrue(antes.startswith("25 •"))
        self.assertFalse(any(es_braille(ch) for ch in antes))
        # con caracter= se dibuja como antes, para no romper programas viejos
        con_x = sin_colores(self.captura(pantalla.grafica, lambda x: x * x, -5, 5, ancho=41, alto=11, caracter="x"))
        self.assertTrue(con_x.startswith("25 x"))
        # el eje sale en su sitio aunque la curva lo pise
        fino = sin_colores(self.captura(pantalla.grafica, lambda x: x * x - 4, -4, 4, ancho=44, alto=12))
        self.assertIn("┼", fino)
        self.assertTrue(fino.splitlines()[8].startswith(" 0 ─"))
        with self.assertRaises(ValueError):
            pantalla.grafica(math.sin, estilo="gordo")

    def test_barras(self):
        salida = sin_colores(self.captura(pantalla.barras, {"Ana": 10, "Luis": 5}, ancho=20))
        self.assertEqual(salida, "Ana  ████████████ 10\nLuis ██████        5\n")
        salida = sin_colores(self.captura(pantalla.barras, [4, 8], ancho=12, valores=False))
        self.assertEqual(salida, "1 █████\n2 ██████████\n")
        with self.assertRaises(ValueError):
            pantalla.barras({"a": -1})

    def test_minigrafica(self):
        self.assertEqual(pantalla.minigrafica([1, 5, 2, 8, 3]), "▁▅▂█▃")
        self.assertEqual(pantalla.minigrafica([]), "")
        self.assertEqual(pantalla.minigrafica([2, 2]), "▄▄")


class TestElegirVariosYFormulario(Base):
    ANCHO = 60
    ALTO = 20

    def test_elegir_varios(self):
        teclas = ["espacio", "abajo", "abajo", "espacio", "enter"]
        with con_teclas(componentes, teclas):
            p = self.pinta(pantalla.elegir_varios, ["Queso", "Tomate", "Jamón"], titulo="Pizza")
        self.assertEqual(self.ultimo_resultado, ["Queso", "Jamón"])
        self.assertIn("[x] Queso", p.texto())

    def test_elegir_varios_minimo_maximo_y_esc(self):
        teclas = ["enter", "espacio", "abajo", "espacio", "enter"]
        with con_teclas(componentes, teclas):
            p = self.pinta(pantalla.elegir_varios, ["a", "b"], minimo=1, maximo=1, marcadas=[])
        self.assertEqual(self.ultimo_resultado, ["a"])
        with con_teclas(componentes, ["esc"]):
            self.captura(pantalla.elegir_varios, ["a"])
        self.assertIsNone(self.ultimo_resultado)

    def test_formulario(self):
        teclas = list("Ana") + ["enter", "1", "x", "borrar", "5", "enter", "s", "e", "enter"]
        with con_teclas(componentes, teclas):
            p = self.pinta(pantalla.formulario, {"Nombre": "texto", "Edad": "numero", "Clave": "contraseña"})
        self.assertEqual(self.ultimo_resultado, {"Nombre": "Ana", "Edad": 15, "Clave": "se"})
        self.assertIn("Formulario", p.texto())

    def test_formulario_valida_y_esc(self):
        teclas = ["enter", "enter", "3", "/", "4", "enter"]
        with con_teclas(componentes, teclas):
            p = self.pinta(pantalla.formulario, {"Fracción": "fraccion"})
        self.assertEqual(self.ultimo_resultado, {"Fracción": Fraction(3, 4)})
        with con_teclas(componentes, ["esc"]):
            self.captura(pantalla.formulario, ["Nombre"])
        self.assertIsNone(self.ultimo_resultado)
        with self.assertRaises(ValueError):
            pantalla.formulario({"Edad": "años"})


if __name__ == "__main__":
    unittest.main()
