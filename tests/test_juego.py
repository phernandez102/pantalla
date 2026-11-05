import io
import os
import sys
import unittest
from unittest import mock

os.environ["PANTALLA_SIN_AVISOS"] = "1"

import pantalla
from pantalla import juego, raton, teclado, terminal
from pantalla.juego import _Lienzo, _Pintor


class SalidaTerminal(io.StringIO):
    """Como sys.stdout, pero dice que es una terminal."""

    def isatty(self):
        return True


class EntornoFalso(juego._Entorno):
    """La terminal de mentira para jugar(): teclas por fotograma y un reloj que no espera."""

    def __init__(self, fotogramas=(), tamano=(40, 12), abajo=None):
        self.fotogramas = [list(f) for f in fotogramas]
        self._tamano = tamano
        self.t = 0.0
        self.dormido = []
        self.abajo = abajo

    def es_terminal(self, salida):
        return True

    def tamano(self):
        return self._tamano

    def ahora(self):
        return self.t

    def dormir(self, segundos):
        self.dormido.append(segundos)
        self.t += segundos

    def leer(self):
        if not self.fotogramas:
            return []
        eventos = []
        for e in self.fotogramas.pop(0):
            if isinstance(e, str):
                eventos.append({"tipo": "tecla", "tecla": e})
            else:
                eventos.append(e)
        return eventos

    def tecla_abajo(self, nombre):
        if self.abajo is None:
            return None
        return nombre in self.abajo


def teclas(*por_fotograma):
    return [[t] if isinstance(t, str) else list(t or []) for t in por_fotograma]


class BaseJuego(unittest.TestCase):
    def setUp(self):
        self.real = SalidaTerminal()
        self.stdout = sys.stdout
        sys.stdout = self.real
        self.parches = [
            mock.patch.object(teclado, "_activar_modo_teclas"),
            mock.patch.object(teclado, "_desactivar_modo_teclas"),
        ]
        for p in self.parches:
            p.start()
        terminal._estado["estilo"] = ""
        terminal._estado["cursor_oculto"] = False
        terminal._estado["pantalla_aparte"] = False
        del teclado._teclas_pendientes[:]

    def tearDown(self):
        sys.stdout = self.stdout
        for p in self.parches:
            p.stop()
        self.assertIsNone(terminal._juego["tamano"])
        self.assertIsNone(terminal._juego["mostrar"])
        self.assertIsNone(terminal._juego["teclas"])
        self.assertIsNone(terminal._juego["pintar"])
        self.assertIsNone(juego._partida["actual"])
        del juego._sprites[:]

    def jugar(self, actualizar, fotogramas=(), tamano=(40, 12), abajo=None, **opciones):
        self.entorno = EntornoFalso(fotogramas, tamano, abajo)
        with mock.patch.object(juego, "_entorno", self.entorno):
            return pantalla.jugar(actualizar, **opciones)

    def vista(self, ancho=40, alto=12):
        """Lo que se ve en la terminal de verdad después de todo lo escrito."""
        lienzo = _Lienzo(ancho, alto)
        lienzo.escribir(self.real.getvalue())
        return lienzo


class Dibujado(unittest.TestCase):
    """El lienzo entiende todo lo que escriben las funciones de dibujo."""

    ANCHO, ALTO = 40, 12

    def pinta(self, funcion, *args, **kwargs):
        salida = SalidaTerminal()
        viejo = sys.stdout
        sys.stdout = salida
        terminal._juego["tamano"] = (self.ANCHO, self.ALTO)
        terminal._estado["estilo"] = ""
        try:
            funcion(*args, **kwargs)
        finally:
            terminal._juego["tamano"] = None
            sys.stdout = viejo
        lienzo = _Lienzo(self.ANCHO, self.ALTO)
        lienzo.escribir(salida.getvalue())
        return lienzo

    def fila(self, lienzo, y):
        return "".join(c for c, _ in lienzo.celdas[y - 1])

    def test_escribir_con_color_y_varias_lineas(self):
        l = self.pinta(pantalla.escribir, "Hola\nadiós", 5, 3, color="rojo", fondo="azul", negrita=True)
        self.assertEqual(self.fila(l, 3)[4:8], "Hola")
        self.assertEqual(self.fila(l, 4)[4:9], "adiós")
        self.assertEqual(l.celda(5, 3), ("H", ((1,), "31", "44")))
        self.assertEqual(l.celda(9, 3), (" ", juego._NORMAL))

    def test_colores_rgb_y_256(self):
        l = self.pinta(pantalla.escribir, "X", 1, 1, color="naranja", fondo=200)
        self.assertEqual(l.celda(1, 1)[1], ((), "38;2;255;140;0", "48;5;200"))

    def test_centrar_y_derecha(self):
        l = self.pinta(pantalla.centrar, "MITAD", 2)
        self.assertEqual(self.fila(l, 2).strip(), "MITAD")
        self.assertEqual(self.fila(l, 2).index("M"), (40 - 5) // 2)
        l = self.pinta(pantalla.escribir_derecha, "Vidas: 3", 1)
        self.assertTrue(self.fila(l, 1).endswith("Vidas: 3"))

    def test_caja_y_rodear(self):
        l = self.pinta(pantalla.caja, 2, 2, 10, 4, estilo="doble", titulo="Hi", relleno="·")
        self.assertEqual(self.fila(l, 2)[1:11], "╔═ Hi ═══╗")
        self.assertEqual(self.fila(l, 3)[1:11], "║········║")
        self.assertEqual(self.fila(l, 5)[1:11], "╚════════╝")
        l = self.pinta(pantalla.rodear, "simple")
        self.assertEqual(self.fila(l, 1), "┌" + "─" * 38 + "┐")
        self.assertEqual(self.fila(l, 12), "└" + "─" * 38 + "┘")
        self.assertEqual(self.fila(l, 6)[0] + self.fila(l, 6)[-1], "││")

    def test_lineas_rellenar_y_punto(self):
        l = self.pinta(pantalla.linea, 3, "=", x=2, largo=5)
        self.assertEqual(self.fila(l, 3)[:7], " =====" + " ")
        l = self.pinta(pantalla.linea_vertical, 4, "|", y=2, largo=3)
        self.assertEqual([l.celda(4, y)[0] for y in (1, 2, 3, 4, 5)], [" ", "|", "|", "|", " "])
        l = self.pinta(pantalla.rellenar, 3, 3, 4, 2, fondo="verde")
        self.assertEqual(l.celda(3, 3)[1][2], "42")
        self.assertEqual(l.celda(6, 4)[1][2], "42")
        self.assertEqual(l.celda(7, 4)[1][2], None)
        l = self.pinta(pantalla.punto, 40, 12, "♥", color="rojo")
        self.assertEqual(l.celda(40, 12), ("♥", ((), "31", None)))

    def test_grande_arte_y_fuentes(self):
        l = self.pinta(pantalla.grande, "HI", 1, 1)
        self.assertEqual(self.fila(l, 1)[:5], "█  █ ")
        l = self.pinta(pantalla.grande, "Hi", 1, 1, fuente="small")
        self.assertIn("|_|", l.texto())
        l = self.pinta(pantalla.arte, "ab\n c", 3, 4, colores="rv\n .")
        self.assertEqual(l.celda(3, 4), ("a", ((), "31", None)))
        self.assertEqual(l.celda(4, 4), ("b", ((), "32", None)))
        self.assertEqual(l.celda(4, 5)[0], "c")

    def test_componentes_sin_esperar(self):
        l = self.pinta(pantalla.cabecera, "TITULO")
        self.assertIn("TITULO", self.fila(l, 1))
        l = self.pinta(pantalla.pie, "Esc salir")
        self.assertIn("Esc salir", self.fila(l, 12))
        l = self.pinta(pantalla.barra_progreso, 50, 100, 2, 2, ancho=10)
        self.assertEqual(self.fila(l, 2)[1:16], "█████░░░░░  50%")
        l = self.pinta(pantalla.tabla, [["Ana", 9]], ["Nombre", "Nota"], x=1, y=1)
        self.assertIn("Nombre", self.fila(l, 2))
        self.assertIn("Ana", self.fila(l, 4))

    def test_limpiar_con_fondo_y_poner_color(self):
        def dibujo():
            pantalla.escribir("basura", 1, 1)
            pantalla.poner_color(fondo="azul")
            pantalla.limpiar()
            pantalla.escribir("ok", 1, 1)
            pantalla.quitar_color()
        l = self.pinta(dibujo)
        self.assertEqual(self.fila(l, 1)[:3], "ok ")
        self.assertEqual(l.celda(20, 6)[1][2], "44")
        self.assertEqual(l.celda(1, 1)[1][2], "44")

    def test_print_gotoxy_y_limpiar_linea(self):
        def dibujo():
            pantalla.gotoxy(3, 2)
            print("uno")
            print("dos")
            pantalla.escribir("zzzz", 1, 5)
            pantalla.limpiar_linea(5)
        l = self.pinta(dibujo)
        self.assertEqual(self.fila(l, 2)[2:5], "uno")
        self.assertEqual(self.fila(l, 3)[:3], "dos")
        self.assertEqual(self.fila(l, 5).strip(), "")

    def test_guardar_y_volver_posicion(self):
        l = _Lienzo(10, 3)
        l.escribir("\x1b[2;3H\x1b7\x1b[1;1Habc\x1b8X")
        self.assertEqual(l.celda(3, 2)[0], "X")

    def test_escribir_lento(self):
        with mock.patch("time.sleep"):
            l = self.pinta(pantalla.escribir_lento, "abc", 2, 2)
        self.assertEqual(self.fila(l, 2)[1:4], "abc")

    def test_letras_anchas_y_tildes_sueltas(self):
        l = _Lienzo(6, 2)
        l.escribir("漢x")
        self.assertEqual([l.celda(i, 1)[0] for i in (1, 2, 3)], ["漢", "", "x"])
        l.escribir("\x1b[1;2HY")
        self.assertEqual([l.celda(i, 1)[0] for i in (1, 2)], [" ", "Y"])
        l.escribir("\x1b[2;6H漢")
        self.assertEqual(l.celda(6, 2)[0], " ")
        l.escribir("\x1b[2;1Hé")
        self.assertEqual(l.celda(1, 2)[0], "é")

    def test_no_salta_de_linea_y_hace_scroll(self):
        l = _Lienzo(4, 2)
        l.escribir("abcdefg")
        self.assertEqual(l.texto(), "abcd\n")
        l.escribir("\x1b[2;1Hxy\nz")
        self.assertEqual(l.texto(), "xy\nz")

    def test_secuencias_que_pasan_a_la_terminal(self):
        pasadas = []
        l = _Lienzo(10, 3, pasadas.append)
        l.escribir("\x1b[?1000h\x1b]0;Juego\x07\x07\x1b[?1049h\x1b[?25l")
        self.assertEqual(pasadas, ["\x1b[?1000h", "\x1b]0;Juego\x07", "\x07", "\x1b[?25l"])

    def test_borrados(self):
        l = _Lienzo(5, 3)
        l.escribir("aaaaa\x1b[2;1Hbbbbb\x1b[3;1Hccccc")
        l.escribir("\x1b[2;3H\x1b[K")
        self.assertEqual(l.texto(), "aaaaa\nbb\nccccc")
        l.escribir("\x1b[1;3H\x1b[1K")
        self.assertEqual(l.texto().split("\n")[0], "   aa")
        l.escribir("\x1b[3;2H\x1b[2X")
        self.assertEqual(l.texto().split("\n")[2], "c  cc")
        l.escribir("\x1b[2;1H\x1b[J")
        self.assertEqual(l.texto().rstrip(), "   aa")


class TestPintor(unittest.TestCase):
    def test_solo_escribe_lo_que_cambia(self):
        salida = []
        pintor = _Pintor(salida.append)
        l = _Lienzo(20, 5)
        l.escribir("\x1b[2;3Hhola")
        pintor.pintar(l, 20, 5)
        self.assertIn("\x1b[2J", salida[0])
        self.assertIn("hola", salida[0])
        pintor.pintar(l, 20, 5)
        self.assertEqual(salida[1], "\x1b[2;7H")
        l.escribir("\x1b[2;4HO")
        pintor.pintar(l, 20, 5)
        self.assertIn("\x1b[2;4H", salida[2])
        self.assertIn("O", salida[2])
        self.assertNotIn("h", salida[2])
        self.assertNotIn("\x1b[2J", salida[2])
        vista = _Lienzo(20, 5)
        vista.escribir("".join(salida))
        self.assertEqual(vista.texto().strip(), "hOla")

    def test_recorta_a_la_terminal_y_letras_anchas(self):
        salida = []
        l = _Lienzo(10, 3)
        l.escribir("\x1b[1;4H漢字")
        _Pintor(salida.append).pintar(l, 5, 2)
        vista = _Lienzo(5, 2)
        vista.escribir("".join(salida))
        self.assertEqual(vista.texto().split("\n")[0], "   漢")

    def test_fondo_del_juego(self):
        salida = []
        l = _Lienzo(3, 1)
        l.escribir("a")
        _Pintor(salida.append, "44").pintar(l, 3, 1)
        self.assertIn("\x1b[0;44ma", "".join(salida))


class TestJugar(BaseJuego):
    def test_devuelve_lo_que_devuelve_actualizar(self):
        vistas = []

        def actualizar(tecla):
            vistas.append(tecla)
            pantalla.escribir("Puntos: %d" % len(vistas), 1, 1)
            if tecla == "q":
                return "fin"

        r = self.jugar(actualizar, teclas(None, "derecha", "q"))
        self.assertEqual(r, "fin")
        self.assertEqual(vistas, [None, "derecha", "q"])
        self.assertIn("Puntos: 3", self.vista().texto())
        salida = self.real.getvalue()
        self.assertTrue(salida.startswith("\x1b[?1049h\x1b[?25l"))
        self.assertTrue(salida.endswith("\x1b[0m\x1b[?25h\x1b[?1049l"))
        self.assertIs(sys.stdout, self.real)

    def test_cero_es_un_resultado_y_false_sigue(self):
        veces = []

        def actualizar():
            veces.append(1)
            return False if len(veces) < 3 else 0

        self.assertEqual(self.jugar(actualizar), 0)
        self.assertEqual(len(veces), 3)

    def test_esc_acaba(self):
        llamadas = []
        r = self.jugar(lambda t: llamadas.append(t), teclas(None, None, "esc", None))
        self.assertIsNone(r)
        self.assertEqual(llamadas, [None, None])

    def test_salir_con_otra_tecla_o_ninguna(self):
        r = self.jugar(lambda t: "x" if t == "esc" else None, teclas("esc"), salir_con=None)
        self.assertEqual(r, "x")
        r = self.jugar(lambda t: None, teclas(None, "q"), salir_con="q")
        self.assertIsNone(r)

    def test_error_en_actualizar_deja_la_terminal_bien(self):
        def actualizar(tecla):
            if tecla == "x":
                raise ZeroDivisionError("uy")

        with self.assertRaises(ZeroDivisionError):
            self.jugar(actualizar, teclas(None, "x"))
        self.assertIs(sys.stdout, self.real)
        self.assertTrue(self.real.getvalue().endswith("\x1b[?1049l"))
        self.assertFalse(terminal._estado["cursor_oculto"])

    def test_ctrl_c_acaba_sin_error(self):
        def actualizar():
            raise KeyboardInterrupt

        self.assertIsNone(self.jugar(actualizar))
        self.assertIs(sys.stdout, self.real)

    def test_no_parpadea_solo_cambia_lo_que_se_mueve(self):
        x = [1]

        def actualizar(tecla):
            pantalla.rodear("simple")
            pantalla.escribir("@", x[0] + 1, 5)
            x[0] += 1
            if x[0] == 4:
                return True

        self.jugar(actualizar)
        trozos = self.real.getvalue().split("\x1b[?25l", 1)[1]
        self.assertEqual(trozos.count("\x1b[2J"), 1)
        self.assertEqual(trozos.count("┌"), 1)
        self.assertEqual(self.vista().celda(4, 5)[0], "@")
        self.assertEqual(self.vista().celda(3, 5)[0], " ")

    def test_tamano_del_juego_y_fondo(self):
        visto = []

        def actualizar():
            visto.append(pantalla.tamano())
            pantalla.escribir("hola", 1, 1)
            return True

        self.jugar(actualizar, ancho=20, alto=6, fondo="azul")
        self.assertEqual(visto, [(20, 6)])
        self.assertEqual(pantalla.tamano(), terminal.tamano())
        self.assertIn("\x1b[0;44mhola", self.real.getvalue())

    def test_teclas_de_mas_con_tecla_pulsada(self):
        otras = []

        def actualizar(tecla):
            otras.append((tecla, pantalla.tecla_pulsada(), pantalla.tecla_pulsada()))
            return True

        self.jugar(actualizar, [["a", "b"]])
        self.assertEqual(otras, [("a", "b", None)])

    def test_velocidad_espera_lo_justo(self):
        n = [0]

        def actualizar():
            n[0] += 1
            return n[0] == 4 or None

        self.jugar(actualizar, velocidad=10)
        self.assertEqual(len(self.entorno.dormido), 3)
        for s in self.entorno.dormido:
            self.assertAlmostEqual(s, 0.1)

    def test_pausa_y_mensaje_dentro_enseñan_lo_dibujado(self):
        vistas_en_pausa = []

        def actualizar():
            pantalla.escribir("antes de esperar", 1, 1)
            with mock.patch("time.sleep"):
                pantalla.pausa(0.5)
            vistas_en_pausa.append(self.vista().texto())
            return True

        self.jugar(actualizar)
        self.assertIn("antes de esperar", vistas_en_pausa[0])

    def test_tecla_dentro_del_juego_enseña_y_espera(self):
        with mock.patch.object(teclado, "_hay_teclado", return_value=False), \
                mock.patch("builtins.input", return_value="s"):
            def actualizar():
                pantalla.escribir("¿Seguro?", 1, 1)
                return pantalla.tecla()

            self.assertEqual(self.jugar(actualizar), "s")
        self.assertIn("¿Seguro?", self.vista().texto())

    def test_errores_amables(self):
        with self.assertRaises(TypeError):
            pantalla.jugar("actualizar")
        with self.assertRaises(ValueError):
            pantalla.jugar(lambda: None, velocidad=0)
        with self.assertRaises(ValueError):
            pantalla.jugar(lambda: None, ancho=-3)
        with self.assertRaises(ValueError):
            pantalla.jugar(lambda: None, fondo="azulito raro")
        no_terminal = EntornoFalso()
        no_terminal.es_terminal = lambda salida: False
        with mock.patch.object(juego, "_entorno", no_terminal):
            with self.assertRaises(RuntimeError):
                pantalla.jugar(lambda: True)

        def dentro():
            pantalla.jugar(lambda: True)

        with self.assertRaises(RuntimeError):
            self.jugar(dentro)

    def test_raton_dentro_del_juego(self):
        clics = []

        def actualizar():
            clics.append(pantalla.leer_raton())
            if len(clics) == 2:
                return True

        clic = {"tipo": "clic", "x": 5, "y": 3, "boton": "izquierdo"}
        with mock.patch.object(raton, "_hay_terminal", return_value=True), \
                mock.patch.object(raton, "_activar_raton_windows"), \
                mock.patch.object(raton, "_desactivar_raton_windows"), \
                mock.patch.object(raton, "_drenar_unix"):
            self.jugar(actualizar, [[clic], []], raton=True)
        self.assertEqual(clics, [(5, 3, "izquierdo"), None])
        self.assertFalse(raton._raton["activo"])

    def test_arrastrar_dentro_del_juego(self):
        vistos = []

        def actualizar():
            vistos.append([pantalla.leer_raton(arrastrar=True) for _ in range(3)])
            return True

        eventos = [{"tipo": "clic", "x": 5, "y": 3, "boton": "izquierdo"},
                   {"tipo": "movimiento", "x": 6, "y": 3, "boton": "izquierdo"},
                   {"tipo": "movimiento", "x": 9, "y": 9, "boton": None}]
        with mock.patch.object(raton, "_hay_terminal", return_value=True), \
                mock.patch.object(raton, "_activar_raton_windows"), \
                mock.patch.object(raton, "_desactivar_raton_windows"), \
                mock.patch.object(raton, "_drenar_unix"):
            self.jugar(actualizar, [eventos], raton=True)
        clic, arrastre, nada = vistos[0]
        self.assertEqual((clic, clic.arrastrando), ((5, 3, "izquierdo"), False))
        self.assertEqual((arrastre, arrastre.arrastrando), ((6, 3, "izquierdo"), True))
        self.assertIsNone(nada)


class TestSprites(BaseJuego):
    def test_se_dibujan_solos_y_se_mueven(self):
        nave = pantalla.Sprite("/^\\", 5, 10, color="verde")

        def actualizar(tecla):
            if tecla == "derecha":
                nave.mover(1, 0)
            if tecla == "q":
                return True

        self.jugar(actualizar, teclas(None, "derecha", "derecha", "q"))
        v = self.vista()
        self.assertEqual("".join(v.celda(x, 10)[0] for x in range(7, 10)), "/^\\")
        self.assertEqual(v.celda(7, 10)[1], ((), "32", None))
        self.assertEqual(v.celda(5, 10)[0], " ")
        self.assertEqual(pantalla.sprites(), [])

    def test_choca_letra_a_letra(self):
        a = pantalla.Sprite("X X", 1, 1)
        b = pantalla.Sprite("o", 2, 1)
        c = pantalla.Sprite("o", 3, 1)
        self.assertIsNone(a.choca(b))
        self.assertIs(a.choca(c), c)
        self.assertIs(a.choca([b, c]), c)
        self.assertTrue(a.choca((3, 1)))
        self.assertFalse(a.choca((2, 1)))
        c.visible = False
        self.assertIsNone(a.choca(c))
        c.visible = True
        c.eliminar()
        self.assertIsNone(a.choca(c))
        self.assertNotIn(c, pantalla.sprites())
        with self.assertRaises(TypeError):
            a.choca(5)

    def test_decimales_fuera_y_tamano(self):
        s = pantalla.Sprite("ab\ncd", 1.4, 1.6)
        self.assertEqual(s._caja(), (1, 2, 2, 3))
        self.assertEqual((s.ancho, s.alto), (2, 2))
        with mock.patch.object(terminal, "tamano", return_value=(10, 5)):
            self.assertFalse(s.fuera())
            s.x = -5
            self.assertTrue(s.fuera())
            s.x, s.y = 3, 6
            self.assertTrue(s.fuera())

    def test_animacion_por_fotogramas(self):
        s = pantalla.Sprite(fotogramas=["A", "B"], x=1, y=1, cada=2)
        vistos = []

        def actualizar():
            vistos.append(self.vista().celda(1, 1)[0])
            if len(vistos) == 6:
                return True

        self.jugar(actualizar)
        self.assertEqual(vistos, [" ", "A", "A", "B", "B", "A"])
        self.assertEqual(s.dibujo, "B")

    def test_colores_transparente_e_invisible(self):
        pantalla.Sprite("ab", 1, 1, colores="r.")
        pantalla.Sprite("x y", 1, 2, transparente=False, fondo="azul")
        oculto = pantalla.Sprite("Z", 5, 5)
        oculto.visible = False

        def actualizar():
            pantalla.escribir("....", 1, 2)
            return True

        self.jugar(actualizar)
        v = self.vista()
        self.assertEqual(v.celda(1, 1), ("a", ((), "31", None)))
        self.assertEqual(v.celda(2, 1)[1], juego._NORMAL)
        self.assertEqual(v.celda(2, 2), (" ", ((), None, "44")))
        self.assertEqual(v.celda(4, 2)[0], ".")
        self.assertEqual(v.celda(5, 5)[0], " ")

    def test_capas(self):
        pantalla.Sprite("BBB", 1, 1, capa=2)
        pantalla.Sprite("AAAA", 1, 1)
        pantalla.Sprite("....", 1, 2, capa=-1)
        pantalla.Sprite("::::::", 1, 2, capa=-5)
        pantalla.Sprite("#", 1, 3, capa=-1)

        def actualizar():
            pantalla.escribir("xy", 2, 2)
            pantalla.escribir(" ", 1, 3, fondo="rojo")
            return True

        self.jugar(actualizar)
        v = self.vista()
        self.assertEqual("".join(v.celda(x, 1)[0] for x in range(1, 5)), "BBBA")
        self.assertEqual("".join(v.celda(x, 2)[0] for x in range(1, 7)), ".xy.::")
        self.assertEqual(v.celda(1, 3), (" ", ((), None, "41")))
        with self.assertRaises(TypeError):
            pantalla.Sprite("@", capa="encima")

    def test_escribir_lento_dentro_del_juego_se_ve_letra_a_letra(self):
        vistas = []

        def dormir(_):
            vistas.append(self.vista().texto().strip())

        def actualizar():
            pantalla.escribir("Puntos", 1, 1)
            with mock.patch("time.sleep", dormir):
                pantalla.escribir_lento("Hola", 1, 3, velocidad=0.01)
            return True

        self.jugar(actualizar)
        self.assertEqual([v.split("\n")[-1] for v in vistas], ["H", "Ho", "Hol", "Hola"])
        self.assertTrue(all(v.startswith("Puntos") for v in vistas))

    def test_cambiar_el_dibujo(self):
        s = pantalla.Sprite("@", 1, 1)
        s.dibujo = "*\n*"
        self.assertEqual(s.alto, 2)
        s.fotogramas = ["1", "2"]
        self.assertEqual(s.fotogramas, ["1", "2"])
        self.assertIn("Sprite(", repr(s))

    def test_dibujar_fuera_de_un_juego(self):
        s = pantalla.Sprite("ab", -1, 2, color="rojo")
        with mock.patch.object(terminal, "tamano", return_value=(10, 5)):
            s.x = 9
            s.dibujar()
        v = _Lienzo(10, 5)
        v.escribir(self.real.getvalue())
        self.assertEqual(v.celda(9, 2), ("a", ((), "31", None)))
        self.assertEqual(v.celda(10, 2)[0], "b")

    def test_errores(self):
        with self.assertRaises(TypeError):
            pantalla.Sprite()
        with self.assertRaises(TypeError):
            pantalla.Sprite("a", "1", 2)
        with self.assertRaises(ValueError):
            pantalla.Sprite("a", colores="?")
        with self.assertRaises(ValueError):
            pantalla.Sprite("a", cada=0)
        with self.assertRaises(TypeError):
            pantalla.Sprite(fotogramas="ab")


class TestAyudasDelJuego(BaseJuego):
    def test_cada_y_fotograma(self):
        marcas = []

        def actualizar():
            if pantalla.cada(0.5):
                marcas.append(pantalla.fotograma())
            if pantalla.fotograma() == 21:
                return True

        self.jugar(actualizar, velocidad=10)
        self.assertEqual(marcas, [5, 10, 15, 20])
        self.assertEqual(pantalla.fotograma(), 0)

    def test_cada_con_clave_dentro_de_un_for(self):
        disparos = []

        def actualizar():
            for nombre in ("a", "b"):
                if pantalla.cada(1, nombre):
                    disparos.append((pantalla.fotograma(), nombre))
            if pantalla.fotograma() == 10:
                return True

        self.jugar(actualizar, velocidad=5)
        self.assertEqual(disparos, [(5, "a"), (5, "b"), (10, "a"), (10, "b")])

    def test_cada_fuera_del_juego_usa_el_reloj(self):
        with mock.patch("time.monotonic", side_effect=[100.0, 100.5, 101.2, 101.3]):
            resultados = [pantalla.cada(1, "reloj") for _ in range(4)]
        self.assertEqual(resultados, [False, False, True, False])
        with self.assertRaises(ValueError):
            pantalla.cada(0)

    def test_pulsada_en_linux_y_mac(self):
        resultados = []

        def actualizar():
            resultados.append(pantalla.pulsada("izquierda"))
            self.entorno.t += 0.0
            if len(resultados) == 6:
                return True

        self.jugar(actualizar, teclas(None, "izquierda", None, None, None, None), velocidad=20)
        self.assertEqual(resultados, [False, True, True, True, True, False])

    def test_pulsada_en_windows(self):
        resultados = []

        def actualizar():
            resultados.append((pantalla.pulsada("espacio"), pantalla.pulsada("LEFT"), pantalla.pulsada("a")))
            return True

        self.jugar(actualizar, abajo={"espacio", "izquierda"})
        self.assertEqual(resultados, [(True, True, False)])
        with mock.patch.object(juego, "_entorno", EntornoFalso(abajo={"a"})):
            self.assertTrue(pantalla.pulsada("A"))
            self.assertFalse(pantalla.pulsada("b"))
        with self.assertRaises(TypeError):
            pantalla.pulsada(3)


if __name__ == "__main__":
    unittest.main()
