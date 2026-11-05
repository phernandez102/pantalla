import builtins
import contextlib
import io
import os
import re
import unittest
from unittest import mock

os.environ["PANTALLA_SIN_AVISOS"] = "1"

import pantalla
from pantalla import componentes, herramientas, matrices, teclado
from fractions import Fraction
import json
import tempfile
from pantalla.colores import codigo_color


class PantallaVirtual:
    """Interpreta los códigos ANSI y los pinta en una cuadrícula de texto."""

    PATRON = re.compile(r"\x1b\[([?0-9;]*)([A-Za-z])|\x1b\][^\x07]*\x07|\x1b([78])|(.)", re.S)

    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.borrar()
        self.x = 1
        self.y = 1
        self.guardada = (1, 1)

    def borrar(self):
        self.celdas = [[" "] * self.ancho for _ in range(self.alto)]

    def poner(self, c):
        if 1 <= self.x <= self.ancho and 1 <= self.y <= self.alto:
            self.celdas[self.y - 1][self.x - 1] = c
        self.x += 1

    def procesar(self, texto):
        for m in self.PATRON.finditer(texto):
            params, final, guardar, c = m.group(1), m.group(2), m.group(3), m.group(4)
            if final:
                if final == "H":
                    partes = (params or "1;1").split(";")
                    self.y, self.x = int(partes[0] or 1), int(partes[1] or 1)
                elif final == "G":
                    self.x = int(params or 1)
                elif final == "J" and params == "2":
                    self.borrar()
                elif final == "K":
                    desde = 1 if params == "2" else self.x
                    for i in range(desde, self.ancho + 1):
                        self.celdas[self.y - 1][i - 1] = " "
            elif guardar == "7":
                self.guardada = (self.x, self.y)
            elif guardar == "8":
                self.x, self.y = self.guardada
            elif c is not None:
                if c == "\n":
                    self.y += 1
                    self.x = 1
                elif c == "\r":
                    self.x = 1
                elif c == "\x07":
                    pass
                else:
                    self.poner(c)
        return self

    def linea(self, y):
        return "".join(self.celdas[y - 1])

    def texto(self):
        return "\n".join(self.linea(y) for y in range(1, self.alto + 1))


class Base(unittest.TestCase):
    ANCHO = 40
    ALTO = 12

    def setUp(self):
        self.entorno = mock.patch.dict(os.environ, {"COLUMNS": str(self.ANCHO), "LINES": str(self.ALTO)})
        self.entorno.start()
        pantalla.terminal._estado["estilo"] = ""

    def tearDown(self):
        self.entorno.stop()

    def captura(self, funcion, *args, **kwargs):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            resultado = funcion(*args, **kwargs)
        self.ultimo_resultado = resultado
        return salida.getvalue()

    def pinta(self, funcion, *args, **kwargs):
        return PantallaVirtual(self.ANCHO, self.ALTO).procesar(self.captura(funcion, *args, **kwargs))


class TestCursor(Base):
    def test_gotoxy(self):
        self.assertEqual(self.captura(pantalla.gotoxy, 10, 5), "\x1b[5;10H")

    def test_gotoxy_con_decimales_redondea(self):
        self.assertEqual(self.captura(pantalla.gotoxy, 10.7, 5.2), "\x1b[5;10H")

    def test_gotoxy_empieza_en_1(self):
        with self.assertRaises(ValueError) as error:
            pantalla.gotoxy(0, 5)
        self.assertIn("empiezan en 1", str(error.exception))

    def test_gotoxy_con_texto_da_error_claro(self):
        with self.assertRaises(TypeError) as error:
            pantalla.gotoxy("10", 5)
        self.assertIn("tiene que ser un número", str(error.exception))

    def test_tamano_y_centro(self):
        self.assertEqual(pantalla.tamano(), (40, 12))
        self.assertEqual(pantalla.centro(), (20, 6))

    def test_limpiar(self):
        p = PantallaVirtual(40, 12)
        p.procesar("basura" * 20)
        p.procesar(self.captura(pantalla.limpiar))
        self.assertEqual(p.texto().strip(), "")
        self.assertEqual((p.x, p.y), (1, 1))


class TestColores(Base):
    def test_nombres(self):
        self.assertEqual(codigo_color("rojo"), "31")
        self.assertEqual(codigo_color("rojo", fondo=True), "41")
        self.assertEqual(codigo_color("Rojo Claro"), "91")
        self.assertEqual(codigo_color("rojo_claro"), "91")
        self.assertEqual(codigo_color("marrón"), "38;2;140;80;30")
        self.assertEqual(codigo_color("red"), "31")

    def test_hexadecimal_rgb_y_numero(self):
        self.assertEqual(codigo_color("#ff8800"), "38;2;255;136;0")
        self.assertEqual(codigo_color("#f80"), "38;2;255;136;0")
        self.assertEqual(codigo_color((1, 2, 3), fondo=True), "48;2;1;2;3")
        self.assertEqual(codigo_color(200), "38;5;200")

    def test_sugerencia_si_te_equivocas(self):
        with self.assertRaises(ValueError) as error:
            codigo_color("rojoo")
        self.assertIn("¿Querías decir 'rojo'?", str(error.exception))
        with self.assertRaises(ValueError) as error:
            codigo_color("azul calro")
        self.assertIn("'azul claro'", str(error.exception))

    def test_errores(self):
        with self.assertRaises(ValueError):
            codigo_color("#12345")
        with self.assertRaises(ValueError):
            codigo_color((300, 0, 0))
        with self.assertRaises(TypeError):
            codigo_color(None)

    def test_colorear(self):
        self.assertEqual(pantalla.colorear("hola", "verde", negrita=True), "\x1b[1;32mhola\x1b[0m")
        self.assertEqual(pantalla.colorear("hola"), "hola")

    def test_poner_color_se_mantiene_despues_de_escribir(self):
        salida = self.captura(pantalla.poner_color, "azul")
        salida += self.captura(pantalla.escribir, "x", color="rojo")
        self.assertTrue(salida.endswith("\x1b[0m\x1b[34m"))
        self.captura(pantalla.quitar_color)
        self.assertEqual(pantalla.terminal._estado["estilo"], "")


class TestEscribir(Base):
    def test_en_posicion(self):
        p = self.pinta(pantalla.escribir, "Hola", 5, 3)
        self.assertEqual(p.linea(3)[4:8], "Hola")

    def test_varias_lineas_misma_columna(self):
        p = self.pinta(pantalla.escribir, " /\\\n/  \\", 10, 2)
        self.assertEqual(p.linea(2)[9:12], " /\\")
        self.assertEqual(p.linea(3)[9:13], "/  \\")

    def test_numeros_se_convierten(self):
        p = self.pinta(pantalla.escribir, 42, 1, 1)
        self.assertTrue(p.linea(1).startswith("42"))

    def test_centrar(self):
        p = self.pinta(pantalla.centrar, "HOLA", 2)
        self.assertEqual(p.linea(2).index("HOLA"), 18)

    def test_derecha(self):
        p = self.pinta(pantalla.escribir_derecha, "Vidas: 3", 1)
        self.assertTrue(p.linea(1).endswith("Vidas: 3"))

    def test_lento(self):
        with mock.patch("time.sleep"):
            p = self.pinta(pantalla.escribir_lento, "abc", 2, 2)
        self.assertEqual(p.linea(2)[1:4], "abc")


class TestDibujo(Base):
    def test_rodear_con_igual(self):
        p = self.pinta(pantalla.rodear, "=")
        self.assertEqual(p.linea(1), "=" * 40)
        self.assertEqual(p.linea(12), "=" * 40)
        for y in range(2, 12):
            self.assertEqual(p.linea(y)[0], "=")
            self.assertEqual(p.linea(y)[-1], "=")
            self.assertEqual(p.linea(y)[1:-1].strip(), "")

    def test_rodear_doble_con_titulo(self):
        p = self.pinta(pantalla.rodear, titulo="Juego")
        self.assertTrue(p.linea(1).startswith("╔═ Juego ═"))
        self.assertTrue(p.linea(1).endswith("╗"))
        self.assertEqual(p.linea(12), "╚" + "═" * 38 + "╝")

    def test_caja(self):
        p = self.pinta(pantalla.caja, 3, 2, 6, 4)
        self.assertEqual(p.linea(2)[2:8], "┌────┐")
        self.assertEqual(p.linea(3)[2:8], "│    │")
        self.assertEqual(p.linea(5)[2:8], "└────┘")

    def test_caja_relleno_borra_lo_de_dentro(self):
        p = PantallaVirtual(40, 12).procesar("X" * 40 * 12)
        p.procesar(self.captura(pantalla.caja, 1, 1, 5, 3, relleno=True))
        self.assertEqual(p.linea(2)[:5], "│   │")

    def test_caja_que_se_sale_no_rompe(self):
        p = self.pinta(pantalla.caja, 35, 10, 20, 10, estilo="ascii")
        self.assertEqual(p.linea(10)[34:], "+-----")

    def test_estilo_que_no_existe(self):
        with self.assertRaises(ValueError) as error:
            pantalla.caja(1, 1, 5, 5, estilo="dobel")
        self.assertIn("simple, doble", str(error.exception))

    def test_lineas_rellenar_punto(self):
        p = self.pinta(pantalla.linea, 3, "-")
        self.assertEqual(p.linea(3), "-" * 40)
        p = self.pinta(pantalla.linea_vertical, 5, "|", y=2, largo=3)
        self.assertEqual([p.linea(y)[4] for y in range(1, 6)], [" ", "|", "|", "|", " "])
        p = self.pinta(pantalla.rellenar, 2, 2, 3, 2, "#")
        self.assertEqual(p.linea(2)[:5], " ### ")
        self.assertEqual(p.linea(3)[:5], " ### ")
        p = self.pinta(pantalla.punto, 7, 7, "@")
        self.assertEqual(p.linea(7)[6], "@")


class TestLetras(Base):
    def test_texto_grande(self):
        dibujo = pantalla.texto_grande("HI", "#").split("\n")
        self.assertEqual(len(dibujo), 5)
        self.assertEqual(dibujo[2], "####  #")
        self.assertIn("█", pantalla.texto_grande("A"))

    def test_tildes_y_desconocidos(self):
        self.assertEqual(pantalla.texto_grande("Á"), pantalla.texto_grande("A"))
        self.assertEqual(pantalla.texto_grande("@"), pantalla.texto_grande("?"))

    def test_grande_centrado(self):
        p = self.pinta(pantalla.grande, "HOLA", caracter="#")
        filas = [p.linea(y) for y in range(1, 13) if "#" in p.linea(y)]
        self.assertEqual(len(filas), 5)


class TestFuentes(Base):
    def test_standard(self):
        self.assertEqual(pantalla.texto_grande("Hi!", fuente="standard").split("\n"),
                         [" _   _ _ _", "| | | (_) |", "| |_| | | |", "|  _  | |_|", "|_| |_|_(_)", ""])

    def test_slant(self):
        self.assertEqual(pantalla.texto_grande("Ok", fuente="slant").split("\n"),
                         ["   ____  __", "  / __ \\/ /__", " / / / / //_/", "/ /_/ / ,<", "\\____/_/|_|", ""])

    def test_ansi_shadow_y_nombres_parecidos(self):
        esperado = [" █████╗ ██████╗", "██╔══██╗██╔══██╗", "███████║██████╔╝", "██╔══██║██╔══██╗",
                    "██║  ██║██████╔╝", "╚═╝  ╚═╝╚═════╝", ""]
        for nombre in ("ansi_shadow", "ANSI Shadow", "ansi-shadow"):
            self.assertEqual(pantalla.texto_grande("AB", fuente=nombre).split("\n"), esperado)

    def test_bloques_es_la_de_siempre(self):
        self.assertEqual(pantalla.texto_grande("HI", fuente="bloques"), pantalla.texto_grande("HI"))

    def test_letras_espanolas_y_desconocidas(self):
        self.assertNotEqual(pantalla.texto_grande("ñ", fuente="standard"), pantalla.texto_grande("n", fuente="standard"))
        self.assertEqual(pantalla.texto_grande("ñ", fuente="starwars"), pantalla.texto_grande("n", fuente="starwars"))
        self.assertEqual(pantalla.texto_grande("a€b", fuente="small"), pantalla.texto_grande("ab", fuente="small"))

    def test_varias_lineas(self):
        una = pantalla.texto_grande("A", fuente="small").split("\n")
        self.assertEqual(pantalla.texto_grande("A\nA", fuente="small").split("\n"), una + una)

    def test_lista_fuentes(self):
        fuentes = pantalla.lista_fuentes()
        self.assertEqual(fuentes[0], "bloques")
        self.assertEqual(len(fuentes), 33)
        for nombre in ("standard", "slant", "ansi_shadow", "doom", "3-d"):
            self.assertIn(nombre, fuentes)
        for nombre in fuentes:
            self.assertTrue(pantalla.texto_grande("Hola", fuente=nombre).strip())

    def test_fuente_que_no_existe(self):
        with self.assertRaises(ValueError) as error:
            pantalla.texto_grande("hola", fuente="comic sans")
        self.assertIn("no conozco la fuente", str(error.exception))
        self.assertIn("slant", str(error.exception))

    def test_grande_con_fuente_centra_con_su_alto(self):
        p = self.pinta(pantalla.grande, "Hi", fuente="standard")
        filas = [y for y in range(1, 13) if p.linea(y).strip()]
        self.assertEqual(filas, [4, 5, 6, 7, 8])


class TestArte(Base):
    def test_dibujo_en_posicion_con_tres_comillas(self):
        p = self.pinta(pantalla.arte, "\n/\\_/\\\n(o.o)\n", 3, 2)
        self.assertEqual(p.linea(2)[2:7], "/\\_/\\")
        self.assertEqual(p.linea(3)[2:7], "(o.o)")
        self.assertEqual(p.linea(4).strip(), "")

    def test_transparente(self):
        p = PantallaVirtual(40, 12).procesar("X" * 40 * 12)
        p.procesar(self.captura(pantalla.arte, ["a b"], 1, 1))
        self.assertEqual(p.linea(1)[:3], "aXb")
        p.procesar(self.captura(pantalla.arte, ["a b"], 1, 2, transparente=False))
        self.assertEqual(p.linea(2)[:3], "a b")
        p.procesar(self.captura(pantalla.arte, ["a b"], 1, 3, fondos=[" z "]))
        self.assertEqual(p.linea(3)[:3], "a b")

    def test_colores(self):
        salida = self.captura(pantalla.arte, ["ab"], 1, 1, colores=["rZ"])
        self.assertIn("\x1b[31ma", salida)
        self.assertIn("\x1b[94mb", salida)
        salida = self.captura(pantalla.arte, ["aab"], 1, 1, color="verde", colores=["..r"])
        self.assertIn("\x1b[32maa", salida)
        self.assertEqual(pantalla.CODIGOS_COLOR["x"], "marrón")

    def test_codigo_que_no_existe(self):
        with self.assertRaises(ValueError) as error:
            pantalla.arte(["a"], 1, 1, colores=["?"])
        self.assertIn("código de color", str(error.exception))

    def test_se_recorta_y_se_centra(self):
        p = self.pinta(pantalla.arte, ["123456"], 38, 12)
        self.assertEqual(p.linea(12)[37:], "123")
        p = self.pinta(pantalla.arte, ["####", "####"])
        self.assertEqual(p.linea(6)[18:22], "####")
        self.assertEqual(p.linea(7)[18:22], "####")


class TestTeclas(unittest.TestCase):
    def test_unix(self):
        t = teclado._traducir_unix
        self.assertEqual(t(b"\x1b[A"), "arriba")
        self.assertEqual(t(b"\x1bOB"), "abajo")
        self.assertEqual(t(b"\x1b[1;5C"), "derecha")
        self.assertEqual(t(b"\x1b[3~"), "suprimir")
        self.assertEqual(t(b"\x1b[15~"), "f5")
        self.assertEqual(t(b"\x1bOP"), "f1")
        self.assertEqual(t(b"\x1b[[A"), "f1")
        self.assertEqual(t(b"\x1b"), "esc")
        self.assertEqual(t(b"\x1bx"), "alt+x")
        self.assertEqual(t(b"\n"), "enter")
        self.assertEqual(t(b"\x7f"), "borrar")
        self.assertEqual(t(b" "), "espacio")
        self.assertEqual(t(b"\x01"), "ctrl+a")
        self.assertEqual(t("ñ".encode()), "ñ")
        self.assertEqual(t(b"Q"), "Q")
        self.assertIsNone(t(None))

    def test_windows(self):
        def lector(*teclas):
            cola = list(teclas)
            return lambda: cola.pop(0)

        t = teclado._traducir_windows
        self.assertEqual(t(lector("\xe0", "H")), "arriba")
        self.assertEqual(t(lector("\x00", "P")), "abajo")
        self.assertEqual(t(lector("\xe0", "S")), "suprimir")
        self.assertEqual(t(lector("\x00", ";")), "f1")
        self.assertEqual(t(lector("\xe0", "\x86")), "f12")
        self.assertEqual(t(lector("\r")), "enter")
        self.assertEqual(t(lector("\x08")), "borrar")
        self.assertEqual(t(lector("a")), "a")
        with self.assertRaises(KeyboardInterrupt):
            t(lector("\x03"))


class TestComponentes(Base):
    ANCHO = 50
    ALTO = 16

    def menu_con(self, teclas, *args, **kwargs):
        cola = list(teclas)
        with mock.patch.object(componentes, "tecla", lambda: cola.pop(0)):
            p = self.pinta(pantalla.menu, *args, **kwargs)
        return self.ultimo_resultado, p

    def test_menu_flechas(self):
        r, p = self.menu_con(["abajo", "abajo", "enter"], ["Jugar", "Opciones", "Salir"], titulo="Menú")
        self.assertEqual(r, "Salir")
        texto = p.texto()
        self.assertIn("Menú", texto)
        self.assertIn("▶ 3. Salir", texto)

    def test_menu_esc_numero_y_vuelta(self):
        self.assertIsNone(self.menu_con(["esc"], ["a", "b"])[0])
        self.assertEqual(self.menu_con(["2"], ["a", "b", "c"])[0], "b")
        self.assertEqual(self.menu_con(["arriba", "enter"], ["a", "b", "c"])[0], "c")

    def test_menu_vacio(self):
        with self.assertRaises(ValueError):
            pantalla.menu([])

    def test_mensaje(self):
        with mock.patch.object(componentes, "tecla", lambda: "x"):
            p = self.pinta(pantalla.mensaje, "Hola\nque tal", titulo="Aviso")
        self.assertEqual(self.ultimo_resultado, "x")
        self.assertIn("Aviso", p.texto())
        self.assertIn("que tal", p.texto())
        self.assertIn("Pulsa una tecla", p.texto())

    def test_tabla(self):
        p = self.pinta(pantalla.tabla, [["Ana", 8.5], ["Luis", 10]], ["Nombre", "Nota"], x=1, y=1)
        self.assertEqual(p.linea(1)[:17], "┌────────┬──────┐")
        self.assertEqual(p.linea(2)[:17], "│ Nombre │ Nota │")
        self.assertEqual(p.linea(3)[:17], "├────────┼──────┤")
        self.assertEqual(p.linea(4)[:17], "│ Ana    │  8.5 │")
        self.assertEqual(p.linea(5)[:17], "│ Luis   │   10 │")
        self.assertEqual(p.linea(6)[:17], "└────────┴──────┘")

    def test_tabla_como_print(self):
        salida = self.captura(pantalla.tabla, [[1, 2]], estilo="ascii")
        self.assertEqual(salida, "+---+---+\n| 1 | 2 |\n+---+---+\n")

    def test_barra(self):
        p = self.pinta(pantalla.barra_progreso, 50, 100, 1, 1, ancho=10)
        self.assertEqual(p.linea(1)[:15], "█████░░░░░  50%")

    def test_cargando(self):
        with mock.patch("time.sleep"):
            p = self.pinta(pantalla.cargando, 0, "Guardando", 1, 1)
        self.assertIn("✓ Guardando", p.linea(1))


class TestPedir(Base):
    def test_pedir_numero_repite_hasta_que_vale(self):
        respuestas = iter(["hola", "200", "15"])
        with mock.patch.object(builtins, "input", lambda: next(respuestas)):
            salida = self.captura(pantalla.pedir_numero, "Edad: ", minimo=0, maximo=120)
        self.assertEqual(self.ultimo_resultado, 15)
        self.assertIn("Escribe un número entero", salida)
        self.assertIn("como máximo 120", salida)

    def test_pedir_numero_con_coma(self):
        with mock.patch.object(builtins, "input", lambda: "2,5"):
            self.captura(pantalla.pedir_numero, decimales=True)
        self.assertEqual(self.ultimo_resultado, 2.5)

    def test_pedir_quita_espacios(self):
        with mock.patch.object(builtins, "input", lambda: "  Ana  "):
            self.captura(pantalla.pedir, "Nombre: ", 3, 3)
        self.assertEqual(self.ultimo_resultado, "Ana")

    def test_confirmar(self):
        cola = ["x", "s"]
        with mock.patch.object(teclado, "tecla", lambda: cola.pop(0)):
            self.captura(pantalla.confirmar)
        self.assertTrue(self.ultimo_resultado)
        with mock.patch.object(teclado, "tecla", lambda: "n"):
            self.captura(pantalla.confirmar)
        self.assertFalse(self.ultimo_resultado)


class TestAyuda(Base):
    def test_todo_lo_publico_tiene_explicacion(self):
        for nombre in pantalla.__all__:
            objeto = getattr(pantalla, nombre)
            if callable(objeto):
                self.assertTrue(objeto.__doc__, nombre + " no tiene docstring")

    def test_ayuda(self):
        salida = self.captura(pantalla.ayuda)
        self.assertIn("pantalla.rodear", salida)
        self.assertIn("pantalla.gotoxy(10, 5)", self.captura(pantalla.ayuda, "gotoxy"))
        self.assertIn("No hay ninguna", self.captura(pantalla.ayuda, "volar"))


def con_teclas(modulo, teclas):
    cola = list(teclas)
    return mock.patch.object(modulo, "tecla", lambda: cola.pop(0))


class TestMenusNuevos(Base):
    ANCHO = 80
    ALTO = 24

    def test_ayudas_iconos_e_inicial_con_texto(self):
        with con_teclas(componentes, ["enter"]):
            p = self.pinta(pantalla.menu, ["Jugar", "Salir"], inicial="Salir",
                           ayudas={"Jugar": "Empieza", "Salir": "Cierra el juego"},
                           iconos={"Jugar": "►", "Salir": "×"})
        self.assertEqual(self.ultimo_resultado, "Salir")
        self.assertIn("▶ 2. ×  Salir", p.texto())
        self.assertIn("» Cierra el juego", p.texto())

    def test_ayudas_en_lista(self):
        with con_teclas(componentes, ["abajo", "enter"]):
            p = self.pinta(pantalla.menu, ["a", "b"], ayudas=["primera", "segunda"])
        self.assertIn("» segunda", p.texto())

    def test_ayuda_por_defecto_justo_debajo(self):
        with con_teclas(componentes, ["enter"]):
            p = self.pinta(pantalla.menu, ["a", "b"], ayudas=["primera", "segunda"], x=5, y=3)
        self.assertTrue(p.linea(7).startswith(" " * 4 + "» primera"))
        self.assertIn("↑↓ elegir", p.linea(8))

    def test_ayuda_en_otro_sitio(self):
        with con_teclas(componentes, ["abajo", "enter"]):
            p = self.pinta(pantalla.menu, ["a", "b"], ayudas=["primera", "segunda"], x=5, y=3,
                           ayuda_x=30, ayuda_y=20)
        self.assertEqual(self.ultimo_resultado, "b")
        self.assertEqual(p.linea(20)[29:38], "» segunda")
        self.assertIn("↑↓ elegir", p.linea(7))
        self.assertNotIn("»", p.linea(7))
        self.assertNotIn("»", p.linea(8))

    def test_ayuda_solo_con_x_va_en_la_fila_de_debajo(self):
        with con_teclas(componentes, ["enter"]):
            p = self.pinta(pantalla.menu, ["a", "b"], ayudas=["primera", "segunda"], x=5, y=3,
                           ayuda_x=40)
        self.assertEqual(p.linea(7)[39:48], "» primera")
        self.assertIn("↑↓ elegir", p.linea(8))

    def test_ayuda_en_la_fila_de_la_pista_no_la_pisa(self):
        with con_teclas(componentes, ["enter"]):
            p = self.pinta(pantalla.menu, ["a", "b"], ayudas=["primera", "segunda"], x=5, y=3,
                           ayuda_x=5, ayuda_y=7)
        self.assertIn("» primera", p.linea(7))
        self.assertIn("↑↓ elegir", p.linea(8))

    def test_color_ayuda(self):
        with con_teclas(componentes, ["enter"]):
            salida = self.captura(pantalla.menu, ["a"], ayudas=["hola"], color_ayuda="verde")
        antes = salida[: salida.index("» hola")]
        self.assertTrue(antes[antes.rindex("\x1b["):].startswith("\x1b[32m")
                        or ";32m" in antes[antes.rindex("\x1b["):])
        with con_teclas(componentes, ["enter"]):
            salida = self.captura(pantalla.menu, ["a"], ayudas=["hola"])
        antes = salida[: salida.index("» hola")]
        self.assertIn("33", antes[antes.rindex("\x1b["):])

    def test_ayuda_en_otro_sitio_con_secciones(self):
        secciones = {"Operaciones": ["Sumar", "Restar"], "Otros": ["Ajustes", "Salir"]}
        with con_teclas(componentes, ["enter"]):
            p = self.pinta(pantalla.menu, secciones, ayudas={"Sumar": "Suma dos números"},
                           ayuda_x=2, ayuda_y=23, color_ayuda="cian")
        self.assertEqual(self.ultimo_resultado, "Sumar")
        self.assertTrue(p.linea(23).startswith(" » Suma dos números"))

    def test_ayuda_fuera_de_la_pantalla_da_error_claro(self):
        with con_teclas(componentes, ["enter"]):
            with self.assertRaises(ValueError):
                self.captura(pantalla.menu, ["a"], ayudas=["x"], ayuda_x=0, ayuda_y=3)

    def test_menu_con_scroll(self):
        opciones = ["Opción %d" % i for i in range(1, 41)]
        with con_teclas(componentes, ["arriba", "enter"]):
            p = self.pinta(pantalla.menu, opciones)
        self.assertEqual(self.ultimo_resultado, "Opción 40")
        self.assertIn("▲", p.texto())
        self.assertIn("Opción 40", p.texto())
        self.assertNotIn("Opción 1 ", p.texto())

    def test_menu_secciones(self):
        secciones = {"Operaciones": ["Sumar", "Restar"], "Otros": ["Ajustes", "Salir"]}
        with con_teclas(componentes, ["derecha", "abajo", "enter"]):
            p = self.pinta(pantalla.menu, secciones, ayudas={"Salir": "Adiós"}, titulo="Menú")
        self.assertEqual(self.ultimo_resultado, "Salir")
        texto = p.texto()
        self.assertIn("─ Operaciones ", texto)
        self.assertIn("─ Otros ", texto)
        self.assertIn("» Adiós", texto)
        fila_sumar = [l for l in texto.split("\n") if "Sumar" in l][0]
        self.assertIn("Ajustes", fila_sumar)

    def test_menu_secciones_que_no_cabe_usa_lista(self):
        secciones = {"S%d" % i: ["op%d_%d" % (i, k) for k in range(5)] for i in range(8)}
        with con_teclas(componentes, ["abajo", "enter"]):
            self.pinta(pantalla.menu, secciones)
        self.assertEqual(self.ultimo_resultado, "op0_1")

    def test_elegir(self):
        with con_teclas(componentes, ["derecha", "enter"]):
            p = self.pinta(pantalla.elegir, "¿Por?", ["Fila", "Columna"], 2, 3)
        self.assertEqual(self.ultimo_resultado, "Columna")
        self.assertIn("¿Por?  Fila   Columna", p.linea(3))
        with con_teclas(componentes, ["esc"]):
            self.captura(pantalla.elegir, "x", ["a"])
        self.assertIsNone(self.ultimo_resultado)

    def test_calculando_borra_al_acabar(self):
        with mock.patch("time.sleep"):
            p = self.pinta(pantalla.calculando, segundos=0)
        self.assertEqual(p.texto().strip(), "")

    def test_cabecera_y_pie(self):
        p = self.pinta(pantalla.cabecera, "MATRICES · Suma")
        self.assertTrue(p.linea(1).startswith("═══ MATRICES · Suma ═"))
        p = self.pinta(pantalla.pie, "Esc salir")
        self.assertEqual(p.linea(24).strip(), "Esc salir")

    def test_caja_centrada_y_escribir_centro(self):
        p = self.pinta(pantalla.caja, ancho=10, alto=4)
        self.assertEqual(p.linea(11)[35:45], "┌────────┐")
        p = self.pinta(pantalla.escribir, "HOLA", "centro", 2)
        self.assertEqual(p.linea(2).index("HOLA"), 38)


class TestMatrices(Base):
    def test_dibujar(self):
        p = self.pinta(pantalla.matriz, [[1, 2], [3, 40]], 1, 1, nombre="A")
        self.assertEqual(self.ultimo_resultado, (14, 4))
        self.assertEqual(p.linea(1)[:14], "    ┌        ┐")
        self.assertEqual(p.linea(2)[:14], "A = │ 1   2  │")
        self.assertEqual(p.linea(3)[:14], "    │ 3   40 │")
        self.assertEqual(p.linea(4)[:14], "    └        ┘")

    def test_determinante_fracciones_y_print(self):
        salida = self.captura(pantalla.matriz, [[Fraction(1, 2), 0.25]], det=True)
        self.assertEqual(salida, "│            │\n│ 1/2   0.25 │\n│            │\n")

    def test_errores(self):
        with self.assertRaises(ValueError):
            pantalla.matriz([[1, 2], [3]])
        with self.assertRaises(TypeError):
            pantalla.matriz(5)

    def test_pedir_matriz_tamano_fijo(self):
        teclas = ["1", "enter", "1", "/", "2", "enter", "-", "enter", "borrar", "3", "enter", "4", "enter"]
        with con_teclas(matrices, teclas):
            p = self.pinta(pantalla.pedir_matriz, "A", filas=2, columnas=2)
        self.assertEqual(self.ultimo_resultado, [[1, 0.5], [3, 4]])
        self.assertEqual(p.texto().strip(), "")

    def test_pedir_matriz_cuadrada_con_flechas(self):
        teclas = ["arriba", "enter"] + [str(n) if k % 2 == 0 else "enter" for n in range(1, 10) for k in range(2)]
        with con_teclas(matrices, teclas):
            self.captura(pantalla.pedir_matriz, cuadrada=True, fracciones=True)
        self.assertEqual(self.ultimo_resultado, [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.assertIsInstance(self.ultimo_resultado[0][0], Fraction)

    def test_pedir_matriz_esc(self):
        with con_teclas(matrices, ["esc"]):
            self.captura(pantalla.pedir_matriz)
        self.assertIsNone(self.ultimo_resultado)


class TestDisenoYDepurar(Base):
    DISENO = {"pantalla": 1, "ancho": 20, "alto": 6, "elementos": [
        {"tipo": "rodear", "estilo": "simple"},
        {"tipo": "texto", "x": 3, "y": 2, "texto": "Hola", "nombre": "saludo"},
        {"tipo": "hueco", "x": 3, "y": 4, "ancho": 5, "nombre": "puntos"},
    ]}

    def test_diseno_desde_diccionario_texto_y_archivo(self):
        p = self.pinta(pantalla.diseno, self.DISENO)
        self.assertEqual(self.ultimo_resultado, {"saludo": (3, 2), "puntos": (3, 4)})
        self.assertEqual(p.linea(1)[:20], "┌" + "─" * 18 + "┐")
        self.assertEqual(p.linea(2)[:20], "│ Hola             │")
        self.captura(pantalla.diseno, json.dumps(self.DISENO))
        self.assertEqual(self.ultimo_resultado["puntos"], (3, 4))
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(self.DISENO, f)
        try:
            self.captura(pantalla.diseno, f.name)
            self.assertEqual(self.ultimo_resultado["saludo"], (3, 2))
        finally:
            os.remove(f.name)

    def test_diseno_centrado(self):
        p = self.pinta(pantalla.diseno, self.DISENO, centrado=True)
        self.assertEqual(self.ultimo_resultado["saludo"], (13, 5))
        self.assertTrue(p.linea(4)[10:].startswith("┌"))

    def test_diseno_errores(self):
        with self.assertRaises(ValueError) as e:
            pantalla.diseno('{"pantalla": 1, "elementos": [')
        self.assertIn("no está bien copiado", str(e.exception))
        with self.assertRaises(ValueError):
            pantalla.diseno({"elementos": [{"tipo": "volar"}]})
        with self.assertRaises(FileNotFoundError):
            pantalla.diseno("no_existe.json")

    def test_diseno_con_arte_y_fuente(self):
        diseno = {"pantalla": 1, "ancho": 40, "alto": 12, "elementos": [
            {"tipo": "arte", "x": 2, "y": 2, "lineas": ["a b", "cd"], "colores": ["r  ", "zz"],
             "nombre": "gato"},
            {"tipo": "grande", "x": 1, "y": 5, "texto": "Hi", "fuente": "standard"},
        ]}
        salida = self.captura(pantalla.diseno, diseno)
        p = PantallaVirtual(40, 12).procesar(salida)
        self.assertEqual(self.ultimo_resultado, {"gato": (2, 2)})
        self.assertEqual(p.linea(2)[1:4], "a b")
        self.assertEqual(p.linea(3)[1:3], "cd")
        self.assertIn("\x1b[31ma", salida)
        self.assertEqual(p.linea(5)[:6], " _   _")

    def test_regla(self):
        p = self.pinta(pantalla.regla)
        self.assertTrue(p.linea(1).startswith("····5···10···15···20"))
        self.assertEqual(p.linea(12)[:2], "12")

    def test_depurar_devuelve_marcas(self):
        with con_teclas(herramientas, ["derecha", "derecha", "abajo", "enter", "r", "esc"]):
            p = self.pinta(pantalla.depurar)
        self.assertEqual(self.ultimo_resultado, [(22, 7)])

    def test_ayuda_de_funciones_nuevas(self):
        self.assertIn("pedir_matriz", self.captura(pantalla.ayuda))
        self.assertIn("pantalla.diseno", self.captura(pantalla.ayuda, "diseno"))


if __name__ == "__main__":
    unittest.main()
