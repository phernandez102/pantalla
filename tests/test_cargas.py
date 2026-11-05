import io
import os
import re
import sys
import unittest
from unittest import mock

os.environ["PANTALLA_SIN_AVISOS"] = "1"

import pantalla
from pantalla import cargas, terminal
from test_pantalla import Base, PantallaVirtual

QUITAR_COLOR = re.compile(r"\x1b\[[0-9;]*m")


class SalidaTerminal(io.StringIO):
    def isatty(self):
        return True


class TestEstilosDeBarra(Base):
    def barra(self, *args, **kwargs):
        return self.pinta(pantalla.barra_progreso, *args, **kwargs).linea(1).rstrip()

    def test_lista(self):
        self.assertEqual(pantalla.lista_barras()[:4], ["bloques", "suave", "linea", "ascii"])
        self.assertIn("circulos", pantalla.lista_barras())

    def test_por_defecto_sigue_igual(self):
        self.assertEqual(self.barra(50, 100, 1, 1, ancho=10), "█████░░░░░  50%")

    def test_cada_estilo_mide_lo_mismo(self):
        for estilo in pantalla.lista_barras():
            for valor in (0, 33, 50, 100):
                linea = self.pinta(pantalla.barra_progreso, valor, 100, 1, 1, ancho=12, estilo=estilo).linea(1)
                self.assertEqual(linea[12:17], " %3d%%" % valor, (estilo, valor))

    def test_caracteres(self):
        self.assertEqual(self.barra(50, 100, 1, 1, ancho=8, estilo="circulos", porcentaje=False), "●●●●○○○○")
        self.assertEqual(self.barra(50, 100, 1, 1, ancho=8, estilo="puntos", porcentaje=False), "⣿⣿⣿⣿⣀⣀⣀⣀")
        self.assertEqual(self.barra(25, 100, 1, 1, ancho=6, estilo="linea", porcentaje=False), "━╸━━━━")

    def test_ascii(self):
        self.assertEqual(self.barra(0, 100, 1, 1, ancho=12, estilo="ascii", porcentaje=False), "[          ]")
        self.assertEqual(self.barra(50, 100, 1, 1, ancho=12, estilo="ascii", porcentaje=False), "[====>     ]")
        self.assertEqual(self.barra(100, 100, 1, 1, ancho=12, estilo="ascii", porcentaje=False), "[==========]")
        with self.assertRaises(ValueError):
            pantalla.barra_progreso(5, 10, 1, 1, ancho=2, estilo="ascii")

    def test_suave_va_por_octavos(self):
        salida = self.captura(pantalla.barra_progreso, 30, 100, 1, 1, ancho=5, estilo="suave", porcentaje=False)
        self.assertEqual(QUITAR_COLOR.sub("", salida)[-5:], "█▌   ")

    def test_lleno_y_vacio_mandan(self):
        self.assertEqual(self.barra(50, 100, 1, 1, ancho=6, estilo="suave", lleno="#", vacio=".",
                                    porcentaje=False), "###...")
        self.assertEqual(self.barra(50, 100, 1, 1, ancho=4, estilo="cuadros", vacio="-",
                                    porcentaje=False), "■■--")

    def test_texto_delante(self):
        self.assertEqual(self.barra(50, 100, 1, 1, ancho=4, texto="Vida"), "Vida ██░░  50%")

    def test_color_final_mezcla(self):
        salida = self.captura(pantalla.barra_progreso, 100, 100, 1, 1, ancho=3, color="rojo", color_final="#0000ff")
        self.assertIn("38;2;197;15;31m", salida)
        self.assertIn("38;2;0;0;255m", salida)
        with self.assertRaises(ValueError) as error:
            pantalla.barra_progreso(5, 10, 1, 1, color=5, color_final="rojo")
        self.assertIn("color_final", str(error.exception))

    def test_estilo_mal_escrito(self):
        with self.assertRaises(ValueError) as error:
            pantalla.barra_progreso(5, 10, estilo="suabe")
        self.assertIn("'suave'", str(error.exception))
        with self.assertRaises(TypeError):
            pantalla.barra_progreso(5, 10, estilo=3)
        self.assertEqual(self.barra(50, 100, 1, 1, ancho=2, estilo="Círculo", porcentaje=False), "●○")

    def test_ayuda_de_nombres(self):
        with self.assertRaises(AttributeError) as error:
            pantalla.loading
        self.assertIn("pantalla_de_carga", str(error.exception))


class TestPantallaDeCargaSinTerminal(Base):
    def test_de_mentira(self):
        salida = self.captura(pantalla.pantalla_de_carga, "Cargando nivel", segundos=0.05)
        self.assertEqual(salida, "Cargando nivel...\n✔ Listo\n")
        self.assertIsNone(self.ultimo_resultado)

    def test_tareas_devuelve_lo_de_las_funciones(self):
        hechas = []

        def leer_mapa():
            hechas.append("mapa")
            return "el mapa"

        salida = self.captura(pantalla.pantalla_de_carga, "Preparando",
                              tareas=["Calentando", ("Mapa", leer_mapa), lambda: 7], segundos=0.05)
        self.assertEqual(self.ultimo_resultado, ["el mapa", 7])
        self.assertEqual(hechas, ["mapa"])
        self.assertIn("  Calentando\n  Mapa\n  Trabajando\n", salida)

    def test_tareas_con_nombre_de_la_funcion(self):
        def colocar_enemigos():
            return 3
        salida = self.captura(pantalla.pantalla_de_carga, tareas=[colocar_enemigos])
        self.assertIn("Colocar enemigos", salida)
        self.assertEqual(self.ultimo_resultado, [3])

    def test_sin_total_tambien_con_segundos_y_tareas(self):
        self.assertEqual(self.captura(pantalla.pantalla_de_carga, "Buscando", segundos=0.05, total=None),
                         "Buscando...\n✔ Listo\n")
        self.captura(pantalla.pantalla_de_carga, tareas=["Uno", lambda: 2], segundos=0.05, total=None)
        self.assertEqual(self.ultimo_resultado, [2])

    def test_solo_textos_devuelve_none(self):
        self.captura(pantalla.pantalla_de_carga, tareas=["Uno", "Dos"], segundos=0.05)
        self.assertIsNone(self.ultimo_resultado)

    def test_un_error_sale_fuera(self):
        def falla():
            raise KeyError("x")
        with self.assertRaises(KeyError):
            self.captura(pantalla.pantalla_de_carga, tareas=[falla])

    def test_con_with(self):
        def usar():
            with pantalla.pantalla_de_carga("Descargando", total=4) as carga:
                carga.avanzar(texto="uno.txt")
                carga.avanzar(10)
                self.assertEqual(carga.valor, 4)
                carga.valor = -3
                self.assertEqual(carga.valor, 0)
                carga.texto = "otro"
            return carga
        salida = self.captura(usar)
        self.assertEqual(salida, "Descargando...\n  uno.txt\n✔ Listo\n")

    def test_errores(self):
        with self.assertRaises(ValueError):
            pantalla.pantalla_de_carga(total=0)
        with self.assertRaises(TypeError):
            pantalla.pantalla_de_carga(total="10")
        with self.assertRaises(ValueError):
            pantalla.pantalla_de_carga(ancho=3)
        with self.assertRaises(ValueError):
            pantalla.pantalla_de_carga(estilo="nada")
        with self.assertRaises(ValueError):
            pantalla.pantalla_de_carga(color="rojoo")
        with self.assertRaises(ValueError):
            pantalla.pantalla_de_carga(tareas=[])
        with self.assertRaises(TypeError):
            pantalla.pantalla_de_carga(tareas=[3])
        with self.assertRaises(TypeError):
            pantalla.pantalla_de_carga(segundos="2")
        with self.assertRaises(ValueError):
            pantalla.pantalla_de_carga(spinner="nada")

    def test_dentro_de_jugar_no(self):
        with mock.patch.dict(terminal._juego, {"pintar": object()}):
            with self.assertRaises(RuntimeError) as error:
                pantalla.pantalla_de_carga()
        self.assertIn("jugar()", str(error.exception))


class TestPantallaDeCargaDibujada(Base):
    ANCHO = 60
    ALTO = 16

    def dibujar(self, carga, valor=None):
        if valor is not None:
            carga._valor = carga._mostrado = valor
        return self.pinta(carga._pintar)

    def test_centrada(self):
        carga = cargas.PantallaDeCarga("Cargando nivel", ancho=20, consejos=["Pulsa P para pausar"])
        carga.texto = "Leyendo el mapa"
        v = self.dibujar(carga, 50)
        filas = v.texto().split("\n")
        y = next(i for i, f in enumerate(filas) if "Cargando nivel" in f)
        self.assertEqual(filas[y].index("Cargando nivel"), (60 - 14) // 2)
        self.assertIn(" 50%", filas[y + 2])
        self.assertEqual(filas[y + 2].index("  50%"), (60 - 25) // 2 + 20)
        self.assertIn("Leyendo el mapa", filas[y + 3])
        self.assertIn("Pulsa P para pausar", filas[y + 6])

    def test_con_fuente_y_marco(self):
        carga = cargas.PantallaDeCarga("Hola", fuente="standard", marco="redondo", ancho=20)
        texto = self.dibujar(carga, 0).texto()
        self.assertIn("╭", texto)
        self.assertIn("╯", texto)
        self.assertIn("|_|", texto)

    def test_letras_grandes_que_no_caben(self):
        carga = cargas.PantallaDeCarga("CARGANDO", fuente="ansi_shadow", ancho=20)
        texto = self.dibujar(carga, 10).texto()
        self.assertIn("CARGANDO", texto)
        self.assertNotIn("██╗", texto)

    def test_sin_saber_cuanto_falta(self):
        carga = cargas.PantallaDeCarga("Buscando", total=None, ancho=20, estilo="bloques", spinner=None)
        carga._inicio = 0
        with mock.patch.object(cargas.time, "time", return_value=cargas._CADA * 3):
            fila = [f for f in self.dibujar(carga).texto().split("\n") if "░" in f][0]
        self.assertEqual(fila.strip(), "░░░████░░░░░░░░░░░░░")
        self.assertNotIn("%", fila)

    def test_de_verdad_en_una_terminal(self):
        real = sys.stdout
        sys.stdout = salida = SalidaTerminal()
        terminal._estado["cursor_oculto"] = False
        try:
            r = pantalla.pantalla_de_carga("Cargando", tareas=["Uno", ("Dos", lambda: 5)], segundos=0.1)
        finally:
            sys.stdout = real
        self.assertEqual(r, [5])
        texto = salida.getvalue()
        self.assertIn("\x1b[?25l", texto)
        self.assertTrue(texto.endswith("\x1b[?25h"), repr(texto[-30:]))
        self.assertIn("✔", texto)
        self.assertIn("100%", texto)
        self.assertEqual(PantallaVirtual(60, 16).procesar(texto).texto().strip(), "")

    def test_borrar_false_la_deja(self):
        real = sys.stdout
        sys.stdout = salida = SalidaTerminal()
        terminal._estado["cursor_oculto"] = False
        try:
            pantalla.pantalla_de_carga("Hecho", segundos=0, borrar=False)
        finally:
            sys.stdout = real
        texto = PantallaVirtual(60, 16).procesar(salida.getvalue()).texto()
        self.assertIn("✔ Listo", texto)
        self.assertIn("100%", texto)


if __name__ == "__main__":
    unittest.main()
