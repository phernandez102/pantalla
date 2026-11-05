import os
import types
import unittest
from unittest import mock

os.environ["PANTALLA_SIN_AVISOS"] = "1"

import pantalla
from pantalla import raton, teclado

from test_pantalla import Base, PantallaVirtual


def clic(x, y, boton="izquierdo"):
    return {"tipo": "clic", "x": x, "y": y, "boton": boton}


def mov(x, y, boton=None):
    return {"tipo": "movimiento", "x": x, "y": y, "boton": boton}


def tecla(nombre):
    return {"tipo": "tecla", "tecla": nombre}


class Eventos:
    """Fuente de eventos de mentira: los da en orden. Si se acaban y hay que esperar, EOFError."""

    def __init__(self, eventos):
        self.eventos = list(eventos)
        self.pedidos = 0

    def __call__(self, espera):
        self.pedidos += 1
        if self.eventos:
            ev = self.eventos.pop(0)
            if isinstance(ev, BaseException):
                raise ev
            return ev
        if espera:
            raise EOFError
        return None


class BaseRaton(Base):
    def setUp(self):
        super().setUp()
        self._reiniciar()
        parche = mock.patch.object(raton, "_es_windows", return_value=False)
        parche.start()
        self.addCleanup(parche.stop)
        self.addCleanup(self._reiniciar)

    def _reiniciar(self):
        raton._raton.update(activo=False, hover=False, posicion=None, fuente=None,
                            modo_anterior_windows=None, modo_teclas_nuestro=False)
        del raton._raton["clics"][:]
        del teclado._teclas_pendientes[:]
        pantalla.terminal._estado["cursor_oculto"] = False

    def con_eventos(self, *eventos):
        fuente = Eventos(eventos)
        raton._raton["fuente"] = fuente
        return fuente

    def resaltado(self, texto, x, y, color="negro", fondo="amarillo"):
        return self.captura(pantalla.escribir, " %s " % texto, x, y, color=color, fondo=fondo, negrita=True)

    def normal(self, texto, x, y, color="blanco", fondo="azul"):
        return self.captura(pantalla.escribir, " %s " % texto, x, y, color=color, fondo=fondo, negrita=False)


class TestDecodificarUnix(unittest.TestCase):
    def d(self, datos):
        return raton._decodificar_unix(datos)

    def test_clic_sgr(self):
        self.assertEqual(self.d(b"\x1b[<0;10;5M"), clic(10, 5))
        self.assertEqual(self.d(b"\x1b[<1;10;5M"), clic(10, 5, "central"))
        self.assertEqual(self.d(b"\x1b[<2;10;5M"), clic(10, 5, "derecho"))

    def test_soltar_no_es_clic(self):
        for codigo in (0, 1, 2):
            self.assertIsNone(self.d(b"\x1b[<%d;10;5m" % codigo))

    def test_modificadores_no_cambian_el_boton(self):
        for extra in (4, 8, 16, 4 + 8 + 16):
            self.assertEqual(self.d(b"\x1b[<%d;3;4M" % extra), clic(3, 4))
            self.assertEqual(self.d(b"\x1b[<%d;3;4M" % (extra + 2)), clic(3, 4, "derecho"))

    def test_movimiento_sin_boton(self):
        for codigo in (35, 35 + 4, 35 + 16):
            self.assertEqual(self.d(b"\x1b[<%d;7;8M" % codigo), mov(7, 8))

    def test_arrastrar_es_movimiento_con_boton(self):
        self.assertEqual(self.d(b"\x1b[<32;7;8M"), mov(7, 8, "izquierdo"))
        self.assertEqual(self.d(b"\x1b[<33;7;8M"), mov(7, 8, "central"))
        self.assertEqual(self.d(b"\x1b[<34;7;8M"), mov(7, 8, "derecho"))
        self.assertEqual(self.d(b"\x1b[<%d;7;8M" % (32 + 16)), mov(7, 8, "izquierdo"))
        self.assertEqual(self.d(b"\x1b[M" + bytes([64, 32 + 7, 32 + 8])), mov(7, 8, "izquierdo"))

    def test_rueda_y_botones_extra_se_ignoran(self):
        for codigo in (64, 65, 66, 67, 64 + 16, 128, 129):
            self.assertIsNone(self.d(b"\x1b[<%d;7;8M" % codigo))

    def test_boton_3_es_soltar_y_no_clic(self):
        self.assertIsNone(self.d(b"\x1b[<3;7;8M"))

    def test_coordenadas_grandes(self):
        self.assertEqual(self.d(b"\x1b[<0;300;250M"), clic(300, 250))

    def test_secuencias_rotas(self):
        for datos in (b"\x1b[<0;10M", b"\x1b[<a;b;cM", b"\x1b[<0;0;5M", b"\x1b[<0;5;0M",
                      b"\x1b[<0;10;5", b"\x1b[<0;1;2;3M", b""):
            self.assertIsNone(self.d(datos), datos)

    def test_protocolo_antiguo_x10(self):
        self.assertEqual(self.d(b"\x1b[M" + bytes([32, 32 + 10, 32 + 5])), clic(10, 5))
        self.assertEqual(self.d(b"\x1b[M" + bytes([34, 32 + 10, 32 + 5])), clic(10, 5, "derecho"))
        self.assertIsNone(self.d(b"\x1b[M" + bytes([35, 32 + 10, 32 + 5])))
        self.assertEqual(self.d(b"\x1b[M" + bytes([67, 32 + 1, 32 + 2])), mov(1, 2))
        self.assertIsNone(self.d(b"\x1b[M" + bytes([96, 33, 33])))

    def test_teclas_con_los_mismos_nombres_que_tecla(self):
        casos = {
            b"\x1b[A": "arriba", b"\x1b[B": "abajo", b"\x1b[C": "derecha", b"\x1b[D": "izquierda",
            b"\x1bOA": "arriba", b"\x1b[1;5C": "derecha", b"\x1bOP": "f1", b"\x1b[15~": "f5",
            b"\x1b[24~": "f12", b"\x1b[[A": "f1", b"\x1b[3~": "suprimir", b"\x1b[H": "inicio",
            b"\x1b[F": "fin", b"\x1b[5~": "repag", b"\x1b[6~": "avpag", b"\x1b": "esc",
            b"\x1bx": "alt+x", b"a": "a", b"Z": "Z", b"7": "7", "ñ".encode(): "ñ", "€".encode(): "€",
            b"\r": "enter", b"\n": "enter", b" ": "espacio", b"\t": "tab", b"\x7f": "borrar",
            b"\x01": "ctrl+a",
        }
        for datos, nombre in casos.items():
            self.assertEqual(self.d(datos), tecla(nombre), datos)
            if datos[:1] == b"\x1b":
                self.assertEqual(teclado._traducir_unix(datos), nombre)


class Flujo:
    """Entrada de mentira para _leer_secuencia_unix. En las posiciones de 'cortes' los datos
    tardan más de lo que se espera (como si llegaran por partes muy separadas)."""

    def __init__(self, datos, cortes=()):
        self.datos = datos
        self.pos = 0
        self.cortes = set(cortes)

    def leer(self, n):
        trozo = self.datos[self.pos:self.pos + n]
        self.pos += len(trozo)
        return trozo

    def hay_datos(self, segundos):
        if self.pos in self.cortes:
            self.cortes.discard(self.pos)
            return False
        return self.pos < len(self.datos)

    def todas(self):
        salida = []
        while True:
            s = teclado._leer_secuencia_unix(self.leer, self.hay_datos)
            if not s:
                return salida
            salida.append(s)


class TestLeerSecuenciaUnix(unittest.TestCase):
    def test_secuencias_seguidas_se_separan_bien(self):
        datos = b"\x1b[<35;4;5M\x1b[Aa\x1b[<0;4;5M\x1b[<0;4;5m\xc3\xb1\x1bOP\x1b[15~\x1b[[A"
        self.assertEqual(Flujo(datos).todas(), [b"\x1b[<35;4;5M", b"\x1b[A", b"a", b"\x1b[<0;4;5M",
                                                 b"\x1b[<0;4;5m", "ñ".encode(), b"\x1bOP",
                                                 b"\x1b[15~", b"\x1b[[A"])

    def test_utf8_de_2_3_y_4_bytes(self):
        datos = "ñ€😀".encode()
        self.assertEqual(Flujo(datos).todas(), ["ñ".encode(), "€".encode(), "😀".encode()])

    def test_alt_con_letra_con_tilde(self):
        self.assertEqual(Flujo("\x1bñ".encode()).todas(), ["\x1bñ".encode()])

    def test_esc_solo(self):
        self.assertEqual(Flujo(b"\x1b").todas(), [b"\x1b"])

    def test_esc_y_luego_tecla_tarde_son_dos_teclas(self):
        self.assertEqual(Flujo(b"\x1bq", cortes=[1]).todas(), [b"\x1b", b"q"])

    def test_raton_x10_lleva_3_bytes_detras(self):
        datos = b"\x1b[M !!" + b"\x1b[M#!!"
        self.assertEqual(Flujo(datos).todas(), [b"\x1b[M !!", b"\x1b[M#!!"])

    def test_secuencia_cortada_no_se_queda_colgada(self):
        self.assertEqual(Flujo(b"\x1b[<0;4").todas(), [b"\x1b[<0;4"])

    def test_fin_de_entrada(self):
        self.assertEqual(teclado._leer_secuencia_unix(Flujo(b"").leer, Flujo(b"").hay_datos), b"")


try:
    _W = raton._estructuras_windows()
except Exception:
    _W = None


@unittest.skipIf(_W is None, "sin ctypes.wintypes")
class TestRegistrosWindows(unittest.TestCase):
    def registro_tecla(self, vk=0, char="\x00", abajo=True):
        r = _W["INPUT_RECORD"]()
        r.EventType = 0x0001
        r.Event.KeyEvent.bKeyDown = abajo
        r.Event.KeyEvent.wVirtualKeyCode = vk
        r.Event.KeyEvent.uChar = char
        r.Event.KeyEvent.wRepeatCount = 1
        return r

    def registro_raton(self, x, y, botones=0, flags=0):
        r = _W["INPUT_RECORD"]()
        r.EventType = 0x0002
        r.Event.MouseEvent.dwMousePosition.X = x
        r.Event.MouseEvent.dwMousePosition.Y = y
        r.Event.MouseEvent.dwButtonState = botones
        r.Event.MouseEvent.dwEventFlags = flags
        return r

    def t(self, registro, origen=(0, 0)):
        return raton._traducir_registro_windows(registro, origen)

    @unittest.skipUnless(os.name == "nt", "en Linux wchar_t ocupa 4 bytes: los tamaños solo cuentan en Windows")
    def test_tamanos_como_en_windows_h(self):
        import ctypes
        self.assertEqual(ctypes.sizeof(_W["KEY_EVENT_RECORD"]), 16)
        self.assertEqual(ctypes.sizeof(_W["MOUSE_EVENT_RECORD"]), 16)
        self.assertEqual(ctypes.sizeof(_W["INPUT_RECORD"]), 20)
        self.assertEqual(_W["KEY_EVENT_RECORD"].uChar.offset, 10)
        self.assertEqual(_W["INPUT_RECORD"].Event.offset, 4)
        self.assertEqual(ctypes.sizeof(_W["CONSOLE_SCREEN_BUFFER_INFO"]), 22)

    def test_teclas_especiales(self):
        casos = {0x26: "arriba", 0x28: "abajo", 0x25: "izquierda", 0x27: "derecha", 0x0D: "enter",
                 0x1B: "esc", 0x09: "tab", 0x08: "borrar", 0x24: "inicio", 0x23: "fin",
                 0x21: "repag", 0x22: "avpag", 0x2E: "suprimir", 0x2D: "insertar",
                 0x70: "f1", 0x7B: "f12"}
        for vk, nombre in casos.items():
            self.assertEqual(self.t(self.registro_tecla(vk)), tecla(nombre))

    def test_mismos_nombres_que_tecla_en_windows(self):
        nombres_tecla = set(teclado._WINDOWS.values()) | set(teclado._ESPECIALES.values())
        for nombre in raton._TECLAS_WINDOWS.values():
            self.assertIn(nombre, nombres_tecla)

    def test_letras_y_caracteres(self):
        self.assertEqual(self.t(self.registro_tecla(0x41, "a")), tecla("a"))
        self.assertEqual(self.t(self.registro_tecla(0xC0, "ñ")), tecla("ñ"))
        self.assertEqual(self.t(self.registro_tecla(0x20, " ")), tecla("espacio"))
        self.assertEqual(self.t(self.registro_tecla(0x41, "\x01")), tecla("ctrl+a"))

    def test_soltar_tecla_y_teclas_sin_letra_no_cuentan(self):
        self.assertIsNone(self.t(self.registro_tecla(0x41, "a", abajo=False)))
        self.assertIsNone(self.t(self.registro_tecla(0x10)))
        self.assertIsNone(self.t(self.registro_tecla(0x11)))

    def test_ctrl_c(self):
        with self.assertRaises(KeyboardInterrupt):
            self.t(self.registro_tecla(0x43, "\x03"))

    def test_clics(self):
        self.assertEqual(self.t(self.registro_raton(9, 4, 0x1)), clic(10, 5))
        self.assertEqual(self.t(self.registro_raton(9, 4, 0x2)), clic(10, 5, "derecho"))
        self.assertEqual(self.t(self.registro_raton(9, 4, 0x4)), clic(10, 5, "central"))

    def test_doble_clic_cuenta_y_soltar_no(self):
        self.assertEqual(self.t(self.registro_raton(0, 0, 0x1, 0x2)), clic(1, 1))
        self.assertIsNone(self.t(self.registro_raton(0, 0, 0, 0)))

    def test_movimiento_y_rueda(self):
        self.assertEqual(self.t(self.registro_raton(2, 3, 0, 0x1)), mov(3, 4))
        self.assertEqual(self.t(self.registro_raton(2, 3, 0x1, 0x1)), mov(3, 4, "izquierdo"))
        self.assertEqual(self.t(self.registro_raton(2, 3, 0x2, 0x1)), mov(3, 4, "derecho"))
        self.assertEqual(self.t(self.registro_raton(2, 3, 0x4, 0x1)), mov(3, 4, "central"))
        self.assertIsNone(self.t(self.registro_raton(2, 3, 0x780000, 0x4)))
        self.assertIsNone(self.t(self.registro_raton(2, 3, 0x780000, 0x8)))

    def test_posicion_relativa_a_la_ventana(self):
        self.assertEqual(self.t(self.registro_raton(9, 79, 0x1), origen=(0, 75)), clic(10, 5))

    def test_otros_eventos(self):
        r = _W["INPUT_RECORD"]()
        r.EventType = 0x0010
        self.assertIsNone(self.t(r))

    def test_modo_de_consola(self):
        nuevo = raton._modo_windows_con_raton(0x01F7)
        self.assertTrue(nuevo & 0x0010)
        self.assertTrue(nuevo & 0x0080)
        self.assertFalse(nuevo & 0x0040)
        self.assertFalse(nuevo & 0x0200)
        self.assertEqual(nuevo & 0x0007, 0x0007)


class TestActivar(BaseRaton):
    def test_activar_y_desactivar_unix(self):
        self.con_eventos()
        salida = self.captura(pantalla.activar_raton)
        self.assertTrue(self.ultimo_resultado)
        self.assertEqual(salida, "\x1b[?1000h\x1b[?1002h\x1b[?1006h")
        salida = self.captura(pantalla.desactivar_raton)
        self.assertEqual(salida, "\x1b[?1002l\x1b[?1006l\x1b[?1000l")
        self.assertFalse(raton._raton["activo"])

    def test_hover(self):
        self.con_eventos()
        self.assertEqual(self.captura(pantalla.activar_raton, hover=True), "\x1b[?1000h\x1b[?1002h\x1b[?1003h\x1b[?1006h")
        self.assertEqual(self.captura(pantalla.desactivar_raton), "\x1b[?1003l\x1b[?1002l\x1b[?1006l\x1b[?1000l")

    def test_pedir_hover_despues(self):
        self.con_eventos()
        self.captura(pantalla.activar_raton)
        self.assertEqual(self.captura(pantalla.activar_raton, hover=True), "\x1b[?1003h")
        self.assertEqual(self.captura(pantalla.activar_raton, hover=True), "")
        self.assertTrue(raton._raton["hover"])

    def test_desactivar_sin_activar_no_hace_nada(self):
        self.assertEqual(self.captura(pantalla.desactivar_raton), "")

    def test_sin_terminal_no_se_activa(self):
        with mock.patch.object(raton, "_hay_terminal", return_value=False):
            self.assertEqual(self.captura(pantalla.activar_raton), "")
            self.assertFalse(self.ultimo_resultado)
        self.assertFalse(raton._raton["activo"])

    def test_windows_no_escribe_codigos(self):
        self.con_eventos()
        with mock.patch.object(raton, "_es_windows", return_value=True), \
                mock.patch.object(raton, "_activar_raton_windows") as act, \
                mock.patch.object(raton, "_desactivar_raton_windows") as des:
            self.assertEqual(self.captura(pantalla.activar_raton, hover=True), "")
            self.assertEqual(self.captura(pantalla.desactivar_raton), "")
        act.assert_called_once_with()
        des.assert_called_once_with()

    def test_terminar_desactiva_el_raton(self):
        self.con_eventos()
        self.captura(pantalla.activar_raton)
        salida = self.captura(pantalla.terminar)
        self.assertIn("\x1b[?1000l", salida)
        self.assertFalse(raton._raton["activo"])

    def test_al_salir_del_programa(self):
        self.con_eventos()
        self.captura(pantalla.activar_raton)
        self.assertIn("\x1b[?1000l", self.captura(raton._al_salir_raton))


class TestBotones(BaseRaton):

    def elige(self, *eventos, **kwargs):
        self.fuente = self.con_eventos(*eventos)
        opciones = kwargs.pop("opciones", ["Sí", "No", "Quizás"])
        kwargs.setdefault("x", 5)
        kwargs.setdefault("y", 3)
        self.salida = self.captura(pantalla.botones, opciones, **kwargs)
        return self.ultimo_resultado

    def test_dibuja_los_botones_con_el_primero_marcado(self):
        self.elige(tecla("esc"))
        v = PantallaVirtual(self.ANCHO, self.ALTO).procesar(self.salida)
        self.assertEqual(v.linea(3)[4:24], " Sí    No    Quizás ")
        self.assertIn(self.resaltado("Sí", 5, 3), self.salida)
        self.assertIn(self.normal("No", 11, 3), self.salida)

    def test_clic(self):
        self.assertEqual(self.elige(clic(12, 3)), "No")
        self.assertEqual(self.elige(clic(5, 3)), "Sí")
        self.assertEqual(self.elige(clic(24, 3)), "Quizás")

    def test_clic_en_el_hueco_o_fuera_no_cuenta(self):
        self.assertEqual(self.elige(clic(9, 3), clic(15, 3), clic(12, 4), clic(25, 3), clic(12, 3)), "No")
        self.assertIsNone(self.elige(clic(9, 3)))

    def test_pasar_por_encima_resalta(self):
        self.elige(mov(18, 3), tecla("esc"))
        self.assertIn(self.resaltado("Quizás", 17, 3), self.salida)
        despues = self.salida.split(self.resaltado("Quizás", 17, 3))[1]
        self.assertNotIn(self.resaltado("Sí", 5, 3), despues)

    def test_raton_y_teclado_a_la_vez(self):
        self.assertEqual(self.elige(mov(12, 3), tecla("derecha"), tecla("enter")), "Quizás")
        self.assertEqual(self.elige(mov(18, 3), tecla("izquierda"), tecla("espacio")), "No")

    def test_flechas_dan_la_vuelta(self):
        self.assertEqual(self.elige(tecla("izquierda"), tecla("enter")), "Quizás")
        self.assertEqual(self.elige(tecla("abajo"), tecla("abajo"), tecla("abajo"), tecla("enter")), "Sí")
        self.assertEqual(self.elige(tecla("tab"), tecla("enter")), "No")
        self.assertEqual(self.elige(tecla("fin"), tecla("enter")), "Quizás")
        self.assertEqual(self.elige(tecla("fin"), tecla("inicio"), tecla("enter")), "Sí")

    def test_numeros(self):
        self.assertEqual(self.elige(tecla("2")), "No")
        self.assertEqual(self.elige(tecla("9"), tecla("3")), "Quizás")

    def test_esc_y_fin_de_entrada(self):
        self.assertIsNone(self.elige(tecla("esc")))
        self.assertIsNone(self.elige())

    def test_otras_teclas_y_botones_del_raton(self):
        self.assertEqual(self.elige(tecla("q"), tecla("f1"), clic(12, 3, "derecho")), "No")

    def test_en_columna(self):
        self.assertEqual(self.elige(clic(6, 5), horizontal=False), "No")
        self.assertEqual(self.elige(clic(6, 7), horizontal=False), "Quizás")
        self.assertEqual(self.elige(clic(6, 4), clic(6, 3), horizontal=False), "Sí")
        self.assertEqual(self.elige(clic(6, 6), horizontal=False, separacion=3), "No")

    def test_centrados(self):
        self.assertEqual(self.elige(clic(11, 6), x=None, y=None), "Sí")
        self.assertEqual(self.elige(clic(30, 6), x=None, y=None), "Quizás")
        self.assertIsNone(self.elige(clic(31, 6), x=None, y=None))

    def test_desactiva_el_raton_y_enseña_el_cursor_al_acabar(self):
        self.elige(clic(12, 3))
        self.assertFalse(raton._raton["activo"])
        self.assertTrue(self.salida.startswith("\x1b[?1000h\x1b[?1002h\x1b[?1003h\x1b[?1006h"))
        self.assertTrue(self.salida.endswith("\x1b[?1003l\x1b[?1002l\x1b[?1006l\x1b[?1000l"))
        self.assertIn("\x1b[?25l", self.salida)
        self.assertIn("\x1b[?25h", self.salida)
        self.assertFalse(pantalla.terminal._estado["cursor_oculto"])

    def test_si_ya_estaba_activado_lo_deja(self):
        self.con_eventos()
        self.captura(pantalla.activar_raton)
        self.elige(clic(12, 3))
        self.assertTrue(raton._raton["activo"])
        self.assertTrue(raton._raton["hover"])

    def test_si_algo_explota_deja_la_terminal_bien(self):
        self.con_eventos(mov(5, 3), RuntimeError("fallo"))
        with self.assertRaises(RuntimeError):
            self.captura(pantalla.botones, ["A"], 5, 3)
        self.assertFalse(raton._raton["activo"])
        self.assertFalse(pantalla.terminal._estado["cursor_oculto"])

    def test_ctrl_c_deja_la_terminal_bien(self):
        self.con_eventos(KeyboardInterrupt())
        with self.assertRaises(KeyboardInterrupt):
            self.captura(pantalla.botones, ["A"], 5, 3)
        self.assertFalse(raton._raton["activo"])

    def test_sin_opciones(self):
        with self.assertRaises(ValueError):
            pantalla.botones([])

    def test_sin_terminal_se_elige_con_el_numero(self):
        with mock.patch.object(raton, "_hay_terminal", return_value=False):
            with mock.patch("builtins.input", side_effect=["7", "abc", "2"]):
                salida = self.captura(pantalla.botones, ["Sí", "No"])
            self.assertEqual(self.ultimo_resultado, "No")
            self.assertIn("1) Sí", salida)
            self.assertIn("No hay esa opción", salida)
            with mock.patch("builtins.input", side_effect=["sí"]):
                self.captura(pantalla.botones, ["Sí", "No"])
                self.assertEqual(self.ultimo_resultado, "Sí")
            with mock.patch("builtins.input", side_effect=[""]):
                self.captura(pantalla.botones, ["Sí", "No"])
                self.assertIsNone(self.ultimo_resultado)
            with mock.patch("builtins.input", side_effect=EOFError):
                self.captura(pantalla.botones, ["Sí", "No"])
                self.assertIsNone(self.ultimo_resultado)


class TestBucle(BaseRaton):
    def test_boton_se_dibuja_y_es_una_zona(self):
        salida = self.captura(pantalla.boton, "Hola", 3, 2)
        z = self.ultimo_resultado
        self.assertEqual(salida, self.normal("Hola", 3, 2))
        self.assertEqual((z["x"], z["y"], z["ancho"], z["alto"]), (3, 2, 6, 1))
        self.assertEqual(PantallaVirtual(40, 12).procesar(salida).linea(2)[2:8], " Hola ")

    def test_hover_entra_y_sale_una_sola_vez(self):
        llamadas = []
        z = pantalla.zona(10, 5, 4, 2, al_hover=lambda: llamadas.append("entra"),
                          al_salir=lambda: llamadas.append("sale"))
        self.con_eventos(mov(1, 1), mov(10, 5), mov(13, 6), mov(11, 5), mov(14, 5), mov(13, 7),
                         mov(12, 6), tecla("esc"))
        self.captura(pantalla.bucle, [z])
        self.assertEqual(llamadas, ["entra", "sale", "entra"])

    def test_boton_cambia_de_color_con_el_raton(self):
        salida_btn = self.captura(pantalla.boton, "OK", 3, 2)
        btn = self.ultimo_resultado
        self.con_eventos(mov(4, 2), mov(20, 2), tecla("esc"))
        salida = self.captura(pantalla.bucle, [btn])
        resaltado = self.resaltado("OK", 3, 2)
        self.assertIn(resaltado, salida)
        self.assertTrue(salida.index(resaltado) < salida.rindex(salida_btn))

    def test_clic_devuelve_lo_que_devuelve_al_clic(self):
        a = pantalla.zona(1, 1, 3, 1, al_clic=lambda: "a")
        b = pantalla.zona(5, 1, 3, 1, al_clic=lambda: "b")
        self.con_eventos(clic(6, 1))
        self.captura(pantalla.bucle, [a, b])
        self.assertEqual(self.ultimo_resultado, "b")

    def test_al_clic_que_devuelve_none_sigue(self):
        cuenta = []
        a = pantalla.zona(1, 1, 3, 1, al_clic=lambda: cuenta.append(1))
        b = pantalla.zona(5, 1, 3, 1, al_clic=lambda: "fin")
        self.con_eventos(clic(1, 1), clic(2, 1), clic(4, 1), clic(5, 1))
        self.captura(pantalla.bucle, [a, b])
        self.assertEqual((len(cuenta), self.ultimo_resultado), (2, "fin"))

    def test_cero_y_texto_vacio_tambien_acaban(self):
        for valor in (0, "", []):
            a = pantalla.zona(1, 1, 3, 1, al_clic=lambda v=valor: v)
            self.con_eventos(clic(1, 1))
            self.captura(pantalla.bucle, [a])
            self.assertEqual(self.ultimo_resultado, valor)

    def test_false_no_acaba(self):
        a = pantalla.zona(1, 1, 3, 1, al_clic=lambda: False)
        self.con_eventos(clic(1, 1))
        self.captura(pantalla.bucle, [a])
        self.assertIsNone(self.ultimo_resultado)

    def test_esc_sin_al_tecla(self):
        self.con_eventos(tecla("a"), tecla("esc"), clic(1, 1))
        self.captura(pantalla.bucle, [pantalla.zona(1, 1, 3, 1, al_clic=lambda: "no")])
        self.assertIsNone(self.ultimo_resultado)

    def test_al_tecla(self):
        vistas = []

        def mi_tecla(t):
            vistas.append(t)
            return "salir" if t == "q" else None

        self.con_eventos(tecla("esc"), tecla("x"), tecla("q"), tecla("z"))
        self.captura(pantalla.bucle, [], al_tecla=mi_tecla)
        self.assertEqual((vistas, self.ultimo_resultado), (["esc", "x", "q"], "salir"))

    def test_zonas_encima_se_llaman_las_dos(self):
        vistas = []
        a = pantalla.zona(1, 1, 5, 5, al_clic=lambda: vistas.append("a"))
        b = pantalla.zona(3, 3, 5, 5, al_clic=lambda: vistas.append("b"))
        self.con_eventos(clic(4, 4))
        self.captura(pantalla.bucle, [a, b])
        self.assertEqual(vistas, ["a", "b"])

    def test_limites_de_la_zona(self):
        z = pantalla.zona(10, 5, 4, 2)
        dentro = [(10, 5), (13, 5), (10, 6), (13, 6)]
        fuera = [(9, 5), (14, 5), (10, 4), (10, 7)]
        self.assertTrue(all(raton._en_zona(z, x, y) for x, y in dentro))
        self.assertFalse(any(raton._en_zona(z, x, y) for x, y in fuera))

    def test_activa_el_hover_y_luego_lo_apaga(self):
        self.con_eventos()
        salida = self.captura(pantalla.bucle, [])
        self.assertTrue(salida.startswith("\x1b[?1000h\x1b[?1002h\x1b[?1003h\x1b[?1006h"))
        self.assertFalse(raton._raton["activo"])

    def test_excepcion_en_al_clic_deja_todo_bien(self):
        def explota():
            raise ZeroDivisionError

        self.con_eventos(clic(1, 1))
        with self.assertRaises(ZeroDivisionError):
            self.captura(pantalla.bucle, [pantalla.zona(1, 1, 2, 1, al_clic=explota)])
        self.assertFalse(raton._raton["activo"])
        self.assertFalse(pantalla.terminal._estado["cursor_oculto"])

    def test_sin_terminal_se_elige_con_el_numero(self):
        self.captura(pantalla.boton, "Uno", 1, 1, al_clic=lambda: None)
        a = self.ultimo_resultado
        b = pantalla.zona(1, 3, 3, 1, al_clic=lambda: "dos")
        with mock.patch.object(raton, "_hay_terminal", return_value=False), \
                mock.patch("builtins.input", side_effect=["1", "2"]):
            salida = self.captura(pantalla.bucle, [a, b, pantalla.zona(1, 5, 1, 1)])
        self.assertEqual(self.ultimo_resultado, "dos")
        self.assertIn("1) Uno", salida)
        self.assertIn("2) Zona 2", salida)


class TestLeer(BaseRaton):
    def test_esperar_clic(self):
        self.con_eventos(mov(1, 1), tecla("a"), clic(7, 8, "derecho"))
        salida = self.captura(pantalla.esperar_clic)
        self.assertEqual(self.ultimo_resultado, (7, 8, "derecho"))
        self.assertEqual(salida, "\x1b[?1000h\x1b[?1002h\x1b[?1006h\x1b[?1002l\x1b[?1006l\x1b[?1000l")

    def test_esperar_clic_sin_terminal_o_sin_entrada(self):
        with mock.patch.object(raton, "_hay_terminal", return_value=False):
            self.assertIsNone(pantalla.esperar_clic())
        self.con_eventos()
        self.captura(pantalla.esperar_clic)
        self.assertIsNone(self.ultimo_resultado)

    def test_esperar_clic_deja_el_raton_como_estaba(self):
        self.con_eventos(clic(1, 1))
        self.captura(pantalla.activar_raton)
        self.captura(pantalla.esperar_clic)
        self.assertTrue(raton._raton["activo"])

    def test_leer_raton_sin_activar(self):
        self.con_eventos(clic(1, 1))
        self.assertIsNone(pantalla.leer_raton())

    def test_leer_raton_no_espera_y_guarda_las_teclas(self):
        self.con_eventos(tecla("x"), mov(3, 3), clic(4, 5), clic(6, 7))
        self.captura(pantalla.activar_raton)
        self.assertEqual(pantalla.leer_raton(), (4, 5, "izquierdo"))
        self.assertEqual(pantalla.leer_raton(), (6, 7, "izquierdo"))
        self.assertIsNone(pantalla.leer_raton())
        self.assertEqual(pantalla.tecla_pulsada(), "x")
        self.assertEqual(teclado._teclas_pendientes, [])

    def test_posicion_raton(self):
        self.con_eventos(mov(3, 4), clic(5, 5), mov(7, 8))
        self.captura(pantalla.activar_raton)
        self.assertIsNone(pantalla.posicion_raton())
        self.captura(pantalla.activar_raton, hover=True)
        self.assertEqual(pantalla.posicion_raton(), (7, 8))
        self.assertEqual(pantalla.posicion_raton(), (7, 8))
        self.assertEqual(pantalla.leer_raton(), (5, 5, "izquierdo"))

    def test_clics_guardados_tienen_limite(self):
        self.con_eventos(*[clic(1, i + 1) for i in range(30)])
        self.captura(pantalla.activar_raton, hover=True)
        pantalla.posicion_raton()
        self.assertEqual(len(raton._raton["clics"]), raton._MAX_GUARDADOS)

    def test_leer_raton_sin_arrastrar_ignora_los_arrastres(self):
        self.con_eventos(clic(1, 1), mov(2, 1, "izquierdo"), mov(3, 1, "izquierdo"), clic(9, 9))
        self.captura(pantalla.activar_raton)
        self.assertEqual(pantalla.leer_raton(), (1, 1, "izquierdo"))
        self.assertEqual(pantalla.leer_raton(), (9, 9, "izquierdo"))

    def test_leer_raton_arrastrando(self):
        self.con_eventos(mov(1, 1), clic(1, 1), mov(2, 1, "izquierdo"), mov(4, 2, "izquierdo"),
                         mov(9, 9), clic(5, 5, "derecho"), mov(6, 5, "derecho"))
        self.captura(pantalla.activar_raton)
        vistos = []
        while True:
            c = pantalla.leer_raton(arrastrar=True)
            if c is None:
                break
            vistos.append((tuple(c), c.arrastrando))
        self.assertEqual(vistos, [((1, 1, "izquierdo"), False), ((2, 1, "izquierdo"), True),
                                  ((4, 2, "izquierdo"), True), ((5, 5, "derecho"), False),
                                  ((6, 5, "derecho"), True)])

    def test_se_desempaqueta_como_siempre(self):
        self.con_eventos(mov(3, 4, "izquierdo"))
        self.captura(pantalla.activar_raton)
        x, y, boton = pantalla.leer_raton(arrastrar=True)
        self.assertEqual((x, y, boton), (3, 4, "izquierdo"))
        self.assertIsInstance(pantalla.leer_raton(), type(None))

    def test_esperar_clic_arrastrando(self):
        self.con_eventos(mov(1, 1), mov(2, 2, "izquierdo"))
        self.captura(pantalla.esperar_clic, arrastrar=True)
        self.assertEqual(self.ultimo_resultado, (2, 2, "izquierdo"))
        self.assertTrue(self.ultimo_resultado.arrastrando)
        self.con_eventos(mov(2, 2, "izquierdo"), clic(3, 3))
        self.captura(pantalla.esperar_clic)
        self.assertEqual(self.ultimo_resultado, (3, 3, "izquierdo"))
        self.assertFalse(self.ultimo_resultado.arrastrando)

    def test_arrastres_leidos_por_tecla_no_se_pierden(self):
        self.con_eventos()
        self.captura(pantalla.activar_raton)
        raton._guardar_evento_unix(b"\x1b[<0;1;1M")
        raton._guardar_evento_unix(b"\x1b[<32;2;1M")
        raton._guardar_evento_unix(b"\x1b[<35;5;5M")
        self.assertEqual(pantalla.leer_raton(arrastrar=True), (1, 1, "izquierdo"))
        self.assertEqual(pantalla.leer_raton(arrastrar=True), (2, 1, "izquierdo"))
        self.assertIsNone(pantalla.leer_raton(arrastrar=True))

    def test_cola_llena_tira_antes_un_arrastre_que_un_clic(self):
        self.con_eventos()
        self.captura(pantalla.activar_raton)
        for i in range(raton._MAX_GUARDADOS - 1):
            raton._guardar(mov(i + 1, 1, "izquierdo"))
        raton._guardar(clic(1, 2))
        raton._guardar(clic(1, 3))
        cola = raton._raton["clics"]
        self.assertEqual(len(cola), raton._MAX_GUARDADOS)
        self.assertEqual([e["tipo"] for e in cola].count("clic"), 2)
        self.assertEqual(cola[0], mov(2, 1, "izquierdo"))

    def test_desactivar_olvida_lo_guardado(self):
        self.con_eventos(clic(1, 1))
        self.captura(pantalla.activar_raton, hover=True)
        pantalla.posicion_raton()
        self.captura(pantalla.desactivar_raton)
        self.assertEqual((raton._raton["clics"], raton._raton["posicion"]), ([], None))


class TestTeclaConRatonActivo(BaseRaton):
    def setUp(self):
        super().setUp()
        for nombre, valor in (("_hay_teclado", lambda: True), ("_activar_modo_teclas", lambda: None),
                              ("os", types.SimpleNamespace(name="posix"))):
            parche = mock.patch.object(teclado, nombre, valor)
            parche.start()
            self.addCleanup(parche.stop)

    def test_tecla_salta_los_eventos_del_raton_y_guarda_el_clic(self):
        with mock.patch.object(teclado, "_leer_bytes_unix",
                               side_effect=[b"\x1b[<35;2;2M", b"\x1b[<0;4;5M", b"\x1b[<0;4;5m", b"\x1b[A"]):
            self.assertEqual(pantalla.tecla(), "arriba")
        self.assertEqual(raton._raton["clics"], [clic(4, 5)])
        self.assertEqual(raton._raton["posicion"], (4, 5))

    def test_tecla_pulsada_no_devuelve_basura_del_raton(self):
        with mock.patch.object(teclado, "_leer_bytes_unix", side_effect=[b"\x1b[<0;9;9M", b"a", None]):
            self.assertIsNone(pantalla.tecla_pulsada())
            self.assertEqual(pantalla.tecla_pulsada(), "a")
            self.assertIsNone(pantalla.tecla_pulsada())
        self.assertEqual(raton._raton["clics"], [clic(9, 9)])

    def test_teclas_pendientes_primero_y_vaciar(self):
        teclado._teclas_pendientes.extend(["b", "c"])
        self.assertEqual(pantalla.tecla(), "b")
        with mock.patch.object(teclado, "_leer_bytes_unix", return_value=None):
            pantalla.vaciar_teclado()
        self.assertEqual(teclado._teclas_pendientes, [])


if __name__ == "__main__":
    unittest.main()
