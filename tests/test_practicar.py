"""practicar(), los récords, el cronómetro y la cuenta atrás."""

import builtins
import os
import random
import re
import shutil
import tempfile
import time
import unittest
from unittest import mock

import pantalla
from pantalla import ejercicios as modulo_practicar
from pantalla import records

from test_pantalla import Base


def sin_colores(texto):
    return re.sub(r"\x1b\[[0-9;]*m", "", texto)


def con_respuestas(*respuestas):
    r = iter(respuestas)
    return mock.patch.object(builtins, "input", lambda: next(r))


class TestPracticar(Base):
    def test_todo_bien(self):
        with con_respuestas("12", "18", "81"):
            s = sin_colores(self.captura(pantalla.practicar, "tablas", 3, semilla=1))
        self.assertEqual(self.ultimo_resultado, 3)
        self.assertIn("1) 4 × 3 =", s)
        self.assertIn("Has acertado 3 de 3", s)
        self.assertIn("Nota: 10", s)

    def test_fallos_y_salir(self):
        with con_respuestas("1", "hola", "18", "salir"):
            s = sin_colores(self.captura(pantalla.practicar, "tablas", 5, semilla=1))
        self.assertEqual(self.ultimo_resultado, 1)
        self.assertIn("No, era 12. 4 × 3 = 12", s)
        self.assertIn("Eso no lo entiendo", s)
        self.assertIn("Has acertado 1 de 2", s)

    def test_elegir_tema(self):
        with con_respuestas("99", "1", "salir"):
            s = sin_colores(self.captura(pantalla.practicar))
        self.assertIn("Tablas de multiplicar", s)
        self.assertIn("Escribe un número del 1 al", s)

    def test_todos_los_temas(self):
        self.assertIn("fracciones", pantalla.lista_temas())
        r = random.Random(0)
        for tema, (_, generar) in modulo_practicar._TEMAS.items():
            for nivel in (1, 2, 3):
                for _ in range(20):
                    pregunta, solucion, explicacion = generar(r, nivel)
                    self.assertTrue(pregunta and explicacion, tema)
                    # la solución se tiene que poder escribir y dar por buena
                    self.assertTrue(modulo_practicar._bien(modulo_practicar._texto_solucion(solucion), solucion),
                                    (tema, pregunta, solucion))

    def test_respuestas(self):
        bien = modulo_practicar._bien
        self.assertTrue(bien("0,5", pantalla.fraccion(1, 2)))
        self.assertTrue(bien("2/4", pantalla.fraccion(1, 2)))
        self.assertTrue(bien("sí", True))
        self.assertFalse(bien("si", False))
        self.assertTrue(bien("0101", "bin:101"))
        self.assertIsNone(bien("dos", 2))

    def test_errores(self):
        with self.assertRaises(ValueError) as e:
            pantalla.practicar("fraciones")
        self.assertIn("fracciones", str(e.exception))
        with self.assertRaises(ValueError):
            pantalla.practicar("tablas", nivel=4)


class TestRecords(Base):
    def setUp(self):
        super().setUp()
        self.carpeta = tempfile.mkdtemp()
        self.archivo = os.path.join(self.carpeta, "records.json")

    def tearDown(self):
        shutil.rmtree(self.carpeta, ignore_errors=True)
        super().tearDown()

    def test_guardar_y_leer(self):
        self.assertIsNone(pantalla.mejor_record(self.archivo))
        self.assertEqual(pantalla.guardar_record("Ana", 120, self.archivo), 1)
        self.assertEqual(pantalla.guardar_record("Luis", 200, self.archivo), 1)
        self.assertEqual(pantalla.guardar_record("Eva", 120, self.archivo), 3)
        self.assertIsNone(pantalla.guardar_record("Bob", 5, self.archivo, cuantos=3))
        self.assertEqual(pantalla.leer_records(self.archivo), [("Luis", 200), ("Ana", 120), ("Eva", 120)])
        self.assertEqual(pantalla.mejor_record(self.archivo), 200)
        with self.assertRaises(TypeError):
            pantalla.guardar_record("Ana", "mucho", self.archivo)

    def test_menos_es_mejor_y_archivo_roto(self):
        t = os.path.join(self.carpeta, "tiempos.json")
        pantalla.guardar_record("A", 34.5, t, menos_es_mejor=True)
        self.assertEqual(pantalla.guardar_record("B", 20.1, t, menos_es_mejor=True), 1)
        self.assertEqual(pantalla.leer_records(t), [("B", 20.1), ("A", 34.5)])
        with open(self.archivo, "w") as f:
            f.write("esto no es json")
        self.assertEqual(pantalla.leer_records(self.archivo), [])

    def test_tabla(self):
        pantalla.guardar_record("Ana", 120, self.archivo)
        s = sin_colores(self.captura(pantalla.tabla_records, self.archivo))
        self.assertIn("│ 1 │ Ana    │    120 │", s)
        s = self.captura(pantalla.tabla_records, os.path.join(self.carpeta, "no.json"))
        self.assertIn("Todavía no hay récords", sin_colores(s))

    def test_ruta_junto_al_programa(self):
        with mock.patch.object(records.sys, "argv", [os.path.join(self.carpeta, "juego.py")]):
            self.assertEqual(records._ruta("r.json"), os.path.join(self.carpeta, "r.json"))


class TestTiempo(Base):
    def test_cronometro(self):
        ahora = [100.0]
        with mock.patch.object(records.time, "time", lambda: ahora[0]):
            c = pantalla.cronometro()
            ahora[0] = 112.34
            self.assertAlmostEqual(c.segundos, 12.34)
            self.assertEqual(str(c), "00:12.3")
            c.parar()
            ahora[0] = 200
            self.assertAlmostEqual(c.segundos, 12.34)
            self.assertFalse(c.en_marcha)
            c.empezar()
            ahora[0] = 201
            self.assertAlmostEqual(c.segundos, 13.34)
            c.reiniciar()
            self.assertEqual(c.texto(decimas=False), "00:00")
        lento = pantalla.Cronometro(empezar=False)
        lento._acumulado = 3725.25
        self.assertEqual(lento.texto(), "1:02:05.2")

    def test_cuenta_atras(self):
        with mock.patch.object(time, "sleep") as dormir:
            s = sin_colores(self.captura(pantalla.cuenta_atras, 3))
        self.assertEqual(dormir.call_count, 3)
        self.assertIn("¡Ya!", s)
        with self.assertRaises(TypeError):
            pantalla.cuenta_atras("tres")


if __name__ == "__main__":
    unittest.main()
