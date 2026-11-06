"""Geometría del espacio (planos, rectas en 3D) y el visor."""

import io
import os
import re
import unittest
from collections import Counter
from unittest import mock

import pantalla
from pantalla import imagenes, juego, raton, terminal, visor

from test_juego import BaseJuego, EntornoFalso
from test_pantalla import Base


class TestPlano(unittest.TestCase):
    def test_formas(self):
        pi = pantalla.plano("2x - y + z = 3")
        self.assertEqual(pi.general(), "2x - y + z - 3 = 0")
        self.assertEqual(pi.vectorial(), "(x, y, z) = (0, 0, 3) + λ·(1, 0, -2) + μ·(0, 1, 1)")
        self.assertEqual(pi.parametricas(), "x = λ,  y = μ,  z = 3 - 2λ + μ")
        self.assertEqual(pi.punto_normal(), "2x - y + (z - 3) = 0")
        self.assertEqual(tuple(pi.normal), (2, -1, 1))
        self.assertTrue(pi.pasa_por((1, 0, 1)))
        self.assertFalse(pi.pasa_por((0, 0, 0)))

    def test_maneras_de_hacerlo(self):
        self.assertEqual(str(pantalla.plano((1, 0, 0), (0, 1, 0), (0, 0, 1))), "x + y + z - 1 = 0")
        self.assertEqual(pantalla.plano((1, 2, 3), normal=(1, 1, 1)).general(), "x + y + z - 6 = 0")
        self.assertEqual(pantalla.plano((0, 0, 0), vectores=[(1, 0, 0), (0, 1, 0)]).general(), "z = 0")
        self.assertEqual(pantalla.plano("x + y + z = 3"), pantalla.Plano("2x + 2y + 2z - 6 = 0"))
        with self.assertRaises(ValueError):
            pantalla.plano((0, 0, 0), (1, 1, 1), (2, 2, 2))

    def test_ecuaciones_plano(self):
        salida = io.StringIO()
        with mock.patch("sys.stdout", salida):
            pantalla.ecuaciones_plano("2x - y + z = 3")
        texto = salida.getvalue()
        for trozo in ("Vectorial:", "Paramétricas:", "General:       2x - y + z - 3 = 0", "n = (2, -1, 1)"):
            self.assertIn(trozo, texto)


class TestRecta3D(unittest.TestCase):
    def test_formas(self):
        r = pantalla.recta((1, 2, 3), (2, 2, 5))
        self.assertIsInstance(r, pantalla.Recta3D)
        self.assertEqual(r.vectorial(), "(x, y, z) = (1, 2, 3) + t·(1, 0, 2)")
        self.assertEqual(r.parametricas(), "x = 1 + t,  y = 2,  z = 3 + 2t")
        self.assertEqual(r.continua(), "(x - 1)/1 = (y - 2)/0 = (z - 3)/2")
        self.assertEqual(r.implicitas(), "y - 2 = 0,  2x - z + 1 = 0")
        self.assertEqual(tuple(r(2)), (3, 2, 7))

    def test_maneras_de_hacerla(self):
        self.assertEqual(str(pantalla.recta("x + y = 3", "z = 1")), "(x, y, z) = (3, 0, 1) + t·(1, -1, 0)")
        self.assertEqual(str(pantalla.recta("(x-1)/2 = y/3 = (z+1)/(-1)")), "(x, y, z) = (1, 0, -1) + t·(2, 3, -1)")
        perpendicular = pantalla.recta((1, 1, 1), perpendicular=pantalla.plano("x + y + z = 0"))
        self.assertEqual(str(perpendicular), "(x, y, z) = (1, 1, 1) + t·(1, 1, 1)")
        self.assertEqual(pantalla.recta((0, 0, 0), vector=(1, 1, 1)), pantalla.recta((2, 2, 2), (5, 5, 5)))
        # en el plano sigue siendo la de siempre
        self.assertEqual(str(pantalla.recta((1, 3), (2, 5))), "2x - y + 1 = 0")


class TestRelaciones(unittest.TestCase):
    def test_posicion(self):
        r = pantalla.recta((1, 2, 3), (2, 2, 5))
        s = pantalla.recta("x + y = 3", "z = 1")
        self.assertEqual(pantalla.posicion(r, s), "se cruzan")
        self.assertEqual(pantalla.posicion("z = 0", "z = 1"), "paralelos")
        self.assertEqual(pantalla.posicion("x = 0", "y = 0", "z = 0"), "se cortan en un punto")
        self.assertEqual(pantalla.posicion((1, 1, 1), pantalla.plano("x + y + z = 3")), "está en el plano")
        self.assertEqual(pantalla.posicion(pantalla.recta((0, 0, 0), vector=(1, 1, 1)), "x + y + z = 3"),
                         "se cortan")

    def test_interseccion(self):
        self.assertEqual(tuple(pantalla.interseccion("x = 0", "y = 0", "z = 0")), (0, 0, 0))
        corte = pantalla.interseccion(pantalla.recta((0, 0, 0), vector=(1, 1, 1)), pantalla.plano("x + y + z = 3"))
        self.assertEqual(tuple(corte), (1, 1, 1))
        recta = pantalla.interseccion(pantalla.plano("x + y + z = 3"), pantalla.plano("z = 1"))
        self.assertEqual(str(recta), "(x, y, z) = (2, 0, 1) + t·(1, -1, 0)")

    def test_distancias_y_angulos(self):
        self.assertAlmostEqual(pantalla.distancia((0, 0, 0), pantalla.plano("x + y + z = 3")), 3 ** 0.5)
        self.assertEqual(pantalla.distancia((1, 2, 3), (4, 6, 3)), 5)
        self.assertEqual(pantalla.distancia((0, 0, 0), pantalla.recta((1, 0, 0), vector=(0, 1, 0))), 1)
        cruzan = (pantalla.recta((0, 0, 0), vector=(1, 0, 0)), pantalla.recta((0, 1, 1), vector=(0, 1, 0)))
        self.assertEqual(pantalla.distancia(*cruzan), 1)
        self.assertEqual(pantalla.distancia(pantalla.plano("z = 0"), pantalla.plano("z = 2")), 2)
        self.assertEqual(pantalla.angulo(pantalla.plano("z = 0"), pantalla.plano("x = 0")), 90)
        self.assertEqual(pantalla.angulo(pantalla.recta((0, 0, 0), vector=(1, 0, 1)), pantalla.plano("z = 0")), 45)
        self.assertEqual(str(pantalla.perpendicular_comun(*cruzan)), "(x, y, z) = (0, 0, 0) + t·(0, 0, 1)")

    def test_pasos(self):
        salida = io.StringIO()
        with mock.patch("sys.stdout", salida):
            pantalla.distancia((0, 0, 0), pantalla.plano("x + y + z = 3"), pasos=True)
        self.assertIn("= 3 / √3 = √3 ≈ 1.7321", salida.getvalue())

    def test_proyecciones_y_demas(self):
        self.assertEqual(tuple(pantalla.proyeccion((1, 2, 3), pantalla.plano("z = 0"))), (1, 2, 0))
        self.assertEqual(tuple(pantalla.simetrico((1, 2, 3), pantalla.plano("z = 0"))), (1, 2, -3))
        self.assertEqual(tuple(pantalla.simetrico((1, 2, 3), (0, 0, 0))), (-1, -2, -3))
        self.assertEqual(tuple(pantalla.punto_medio((0, 0, 0), (2, 4, 6))), (1, 2, 3))
        self.assertEqual(str(pantalla.plano_mediador((0, 0, 0), (2, 0, 0))), "x - 1 = 0")
        self.assertEqual(pantalla.area_triangulo((0, 0, 0), (1, 0, 0), (0, 1, 0)), 0.5)
        self.assertEqual(pantalla.volumen_tetraedro((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)) * 6, 1)
        self.assertTrue(pantalla.estan_alineados((0, 0, 0), (1, 1, 1), (2, 2, 2)))
        self.assertTrue(pantalla.son_coplanarios((0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)))
        self.assertFalse(pantalla.son_coplanarios((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)))

    def test_punto(self):
        P = pantalla.Punto((1, 2, 3))
        self.assertIsInstance(P + pantalla.Vector((1, 1, 1)), pantalla.Punto)
        self.assertEqual(tuple(P - pantalla.Punto((0, 0, 0))), (1, 2, 3))


ESCENA = {"π": "x + y + z = 3", "σ": "z = 1", "r": pantalla.recta((0, 0, 0), vector=(1, 2, 0)), "P": (2, 1, 3)}


def _sin_colores(texto):
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", texto)


class TestDibujarEspacio(Base):
    ANCHO, ALTO = 80, 40

    def test_con_puntos(self):
        salida = self.captura(pantalla.dibujar_espacio, ESCENA, estilo="puntos")
        self.assertEqual(self.ultimo_resultado, (60, 22 + 8))
        texto = _sin_colores(salida)
        self.assertTrue(any(0x2800 < ord(c) <= 0x28ff for c in texto))
        for trozo in ("π  x + y + z - 3 = 0", "σ  z - 1 = 0", "r corta a π en (1, 2, 0)", "r es paralela a σ", "◆", "●"):
            self.assertIn(trozo, texto)
        # los planos tienen el fondo de su color
        self.assertIn("48;2;", salida)

    def test_coincidentes_y_paralelos(self):
        texto = _sin_colores(self.captura(pantalla.dibujar_espacio, ["x + y + z = 3", "2x + 2y + 2z = 6", "x - y = 0"],
                                          estilo="puntos"))
        self.assertIn("π = σ", texto)
        self.assertIn("π y σ son el mismo plano", texto)
        # no se repite lo de σ con ρ, que es lo mismo que lo de π con ρ
        self.assertEqual(texto.count("se cortan en la recta"), 1)

    def test_leyenda_partida(self):
        texto = _sin_colores(self.captura(pantalla.dibujar_espacio, ESCENA, ancho=40, alto=16, estilo="puntos"))
        for linea in texto.split("\n"):
            self.assertLessEqual(len(linea.rstrip()), 40)
        self.assertIn("(2, 0, 1) +", texto)

    def test_con_imagen(self):
        salida = self.captura(pantalla.dibujar_espacio, ESCENA, estilo="imagen")
        self.assertEqual(self.ultimo_resultado, (60, 22 + 8))
        self.assertIn("\x1bP0;1;0q", salida)
        self.assertIn("\x1b\\", salida)
        self.assertTrue(salida.startswith("\n" * 22 + "\x1b[22A\x1b7\x1bP"))
        self.assertIn("π  x + y + z - 3 = 0", _sin_colores(salida))

    def test_auto_sin_terminal_es_con_puntos(self):
        with mock.patch.dict(visor._capacidad, {"imagenes": None}), \
                mock.patch.dict(os.environ, {"PANTALLA_IMAGENES": "0"}):
            salida = self.captura(pantalla.dibujar_espacio, ESCENA)
        self.assertNotIn("\x1bP", salida)
        with mock.patch.dict(visor._capacidad, {"imagenes": None}), \
                mock.patch.dict(os.environ, {"PANTALLA_IMAGENES": "1"}):
            salida = self.captura(pantalla.dibujar_espacio, ESCENA)
        self.assertIn("\x1bP", salida)

    def test_tamano_y_errores(self):
        texto = _sin_colores(self.captura(pantalla.dibujar_espacio, "x + y + z = 3", tamano=(0, 4), estilo="puntos"))
        self.assertIn("π", texto)
        with self.assertRaises(ValueError):
            pantalla.dibujar_espacio("z = 0", tamano=(4, 0))
        with self.assertRaises(ValueError):
            pantalla.dibujar_espacio("z = 0", estilo="bonito")
        with self.assertRaises(TypeError):
            pantalla.dibujar_espacio([object()])
        with self.assertRaises(ValueError):
            pantalla.dibujar_espacio("z = 0", ancho=5)


class TestAyudaDeAbajo(unittest.TestCase):
    def test_si_no_cabe_se_queda_esc_salir(self):
        self.assertEqual(terminal._ayuda_que_cabe(visor._AYUDA, 200), visor._AYUDA)
        for ancho in (79, 60, 40):
            texto = terminal._ayuda_que_cabe(visor._AYUDA, ancho)
            self.assertLessEqual(len(texto), ancho)
            self.assertTrue(texto.endswith("Esc salir"), texto)
        self.assertEqual(len(terminal._ayuda_que_cabe(visor._AYUDA, 10)), 10)


class TestGirarConRaton(Base):
    ANCHO, ALTO = 100, 40

    def setUp(self):
        super().setUp()
        self.eventos = []
        raton._raton["fuente"] = lambda espera: self.eventos.pop(0) if self.eventos else None
        del terminal._giratorios[:]

    def tearDown(self):
        del terminal._giratorios[:]
        raton._raton["fuente"] = None
        raton._raton["activo"] = False
        super().tearDown()

    def test_se_gira_mientras_esperas_una_tecla(self):
        self.captura(pantalla.dibujar_espacio, ESCENA, 30, 2, ancho=40, alto=16, estilo="puntos", girar=True)
        z = self.ultimo_resultado
        self.assertEqual(tuple(z), (40, z.alto_total))
        self.assertGreater(z.alto_total, 16)
        self.assertIn(z, terminal._giratorios)
        self.eventos = [{"tipo": "clic", "x": 40, "y": 8, "boton": "derecho"},
                        {"tipo": "movimiento", "x": 42, "y": 8, "boton": "derecho"},
                        {"tipo": "movimiento", "x": 45, "y": 9, "boton": "derecho"},
                        {"tipo": "clic", "x": 2, "y": 2, "boton": "izquierdo"},
                        {"tipo": "tecla", "tecla": "q"}]
        with mock.patch("pantalla.teclado._hay_teclado", return_value=True):
            salida = self.captura(pantalla.tecla)
        self.assertEqual(self.ultimo_resultado, "q")
        self.assertEqual((z.giro, z.inclinacion), (35 - 5 * 4, 25 + 8))
        # se pinta una vez para los dos movimientos, en su sitio, sin mover el cursor
        self.assertEqual(salida.count("\x1b7"), 1)
        self.assertTrue(salida.startswith("\x1b7\x1b[2;30H"))
        # el clic de fuera no se lo queda
        self.assertEqual(raton._raton["clics"][-1]["x"], 2)
        pantalla.limpiar()
        self.assertEqual(terminal._giratorios, [])

    def test_si_no_llega_nada_sigue_esperando(self):
        # en linux soltar el botón no da ningún evento y _leer_crudo devuelve None
        self.captura(pantalla.dibujar_espacio, ESCENA, 30, 2, ancho=40, alto=16, estilo="puntos", girar=True)
        self.eventos = [None, None, {"tipo": "tecla", "tecla": "q"}]
        with mock.patch("pantalla.teclado._hay_teclado", return_value=True):
            self.captura(pantalla.tecla)
        self.assertEqual(self.ultimo_resultado, "q")

    def test_con_imagen_borra_las_letras_viejas(self):
        self.captura(pantalla.dibujar_espacio, ESCENA, 1, 1, estilo="imagen", girar=True)
        z = self.ultimo_resultado
        antes = list(z.viejas)
        self.assertTrue(antes)
        salida = self.captura(z.girar, 120, 10)
        self.assertIn("\x1bP0;1;0q", salida)
        self.assertNotEqual(antes, z.viejas)
        z.quitar()
        self.assertNotIn(z, terminal._giratorios)


def _decodificar(sixel):
    """Lo que pinta un Sixel: {(x, y): (r, g, b)} en por ciento."""
    cuerpo = sixel[sixel.index("q") + 1:sixel.rindex("\x1b\\")]
    m = re.match(r'"1;1;(\d+);(\d+)', cuerpo)
    W, H = int(m.group(1)), int(m.group(2))
    paleta, pixeles = {}, {}
    i, x, banda, color = m.end(), 0, 0, 0
    color_re, repetir_re = re.compile(r"#(\d+)(;2;(\d+);(\d+);(\d+))?"), re.compile(r"!(\d+)(.)")
    while i < len(cuerpo):
        c = cuerpo[i]
        if c == "#":
            m = color_re.match(cuerpo, i)
            if m.group(2):
                paleta[int(m.group(1))] = tuple(int(v) for v in m.group(3, 4, 5))
            color, i = int(m.group(1)), m.end()
            continue
        if c in "$-":
            x = 0
            banda += 6 if c == "-" else 0
            i += 1
            continue
        n = 1
        if c == "!":
            m = repetir_re.match(cuerpo, i)
            n, c, i = int(m.group(1)), m.group(2), m.end()
        else:
            i += 1
        bits = ord(c) - 63
        for _ in range(n):
            for dy in range(6):
                if bits >> dy & 1:
                    pixeles[(x, banda + dy)] = paleta[color]
            x += 1
    return W, H, pixeles


class TestImagen(unittest.TestCase):
    def setUp(self):
        cosas = visor._leer_objetos(visor._pares(ESCENA), None)
        lo, hi = visor._tamano_caja(cosas)
        self.g, _ = visor._geometria(cosas, lo, hi, True, True, True)
        self.cam = lambda W, H: visor._Camara(W, H, 35, 25, 1, lo, hi)

    def test_sixel_dice_lo_mismo_que_la_imagen(self):
        img, letras = visor._con_imagen(self.g, 30, 10, 10, 20, self.cam)
        W, H, pixeles = _decodificar(imagenes._sixel(img))
        self.assertEqual((W, H), (300, 200))
        pintados = [(x, y) for y in range(H) for x in range(W) if img.A[y * W + x] >= 10]
        self.assertEqual(set(pintados), set(pixeles))
        # el color que más sale va exacto (en por ciento)
        cuantos = Counter((img.R[y * W + x], img.G[y * W + x], img.B[y * W + x]) for x, y in pintados)
        color = cuantos.most_common(1)[0][0]
        x, y = next(p for p in pintados if (img.R[p[1] * W + p[0]], img.G[p[1] * W + p[0]], img.B[p[1] * W + p[0]]) == color)
        for dado, esperado in zip(pixeles[(x, y)], color):
            self.assertLessEqual(abs(dado * 255 / 100.0 - esperado), 4)
        nombres = "".join(ch for _, _, ch, _ in letras)
        for letra in "xyzπσrP":
            self.assertIn(letra, nombres)

    def test_opaco_pinta_todo(self):
        img, _ = visor._con_imagen(self.g, 12, 4, 10, 20, self.cam, (0, 0, 0))
        W, H, pixeles = _decodificar(imagenes._sixel(img, opaco=True))
        self.assertEqual(len(pixeles), W * H)

    def test_planos_que_se_tapan(self):
        # la recta r (en z = 0) queda debajo de σ (z = 1): por detrás va a trozos
        img, _ = visor._con_imagen(self.g, 60, 22, 10, 20, self.cam)
        rojo = visor._rgb("rojo claro")
        cam = self.cam(600, 440)
        A, B = cam((0.25, 0.5, 0)), cam((0.5, 1.0, 0))
        trozos = []
        for k in range(40):
            t = k / 39.0
            x, y = int(A[0] + (B[0] - A[0]) * t), int(A[1] + (B[1] - A[1]) * t)
            i = y * 600 + x
            trozos.append(abs(img.R[i] - rojo[0]) < 120 and img.G[i] < 140)
        self.assertIn(True, trozos)
        self.assertIn(False, trozos)


class TestPreguntarTerminal(unittest.TestCase):
    def test_lee_lo_que_contesta(self):
        respuesta = "\x1b]11;rgb:1e1e/1e1e/2e2e\x1b\\\x1b[6;18;9t\x1b[?62;4;22c"
        with mock.patch.object(imagenes, "_preguntar_terminal", return_value=respuesta), \
                mock.patch.object(terminal, "_es_terminal", return_value=True), \
                mock.patch.dict(visor._capacidad, {"imagenes": None, "celda": (10, 20)}), \
                mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PANTALLA_IMAGENES", None)
            self.assertTrue(visor._puede_imagenes())
            self.assertEqual(visor._capacidad["celda"], (9, 18))
            self.assertEqual(visor._capacidad["fondo"], (30, 30, 46))

    def test_sin_sixel(self):
        with mock.patch.object(imagenes, "_preguntar_terminal", return_value="\x1b[?1;2c"), \
                mock.patch.object(terminal, "_es_terminal", return_value=True), \
                mock.patch.dict(visor._capacidad, {"imagenes": None}):
            os.environ.pop("PANTALLA_IMAGENES", None)
            self.assertFalse(visor._puede_imagenes())


class TestVerEspacio(BaseJuego):
    def test_con_puntos_y_teclas(self):
        camaras = []
        viejo = visor._Camara.__init__

        def apuntar(cam, W, H, giro, inc, zoom, lo, hi):
            camaras.append((round(giro) % 360, round(inc), round(zoom, 2)))
            viejo(cam, W, H, giro, inc, zoom, lo, hi)
        arrastre = [{"tipo": "clic", "x": 10, "y": 5, "boton": "izquierdo"},
                    {"tipo": "movimiento", "x": 12, "y": 6, "boton": "izquierdo"}]
        with mock.patch.object(visor._Camara, "__init__", apuntar), \
                mock.patch.object(raton, "activar_raton"), mock.patch.object(raton, "desactivar_raton"):
            raton._raton["activo"] = True
            try:
                self.jugar_espacio([[], ["izquierda"], ["+"], ["z"], arrastre, ["esc"]])
            finally:
                raton._raton["activo"] = False
        self.assertEqual(camaras[0], (35, 25, 1.0))
        self.assertIn((40, 25, 1.0), camaras)
        self.assertIn((40, 25, 1.15), camaras)
        self.assertIn((270, 90, 1.15), camaras)
        self.assertEqual(camaras[-1], (262, 90, 1.15))

    def jugar_espacio(self, fotogramas):
        self.entorno = EntornoFalso(fotogramas, (100, 30))
        with mock.patch.object(juego, "_entorno", self.entorno):
            pantalla.ver_espacio(ESCENA, estilo="puntos")

    def test_fuera_de_terminal_lo_dibuja_quieto(self):
        with mock.patch.object(juego._entorno, "es_terminal", return_value=False):
            pantalla.ver_espacio(ESCENA)
        self.assertIn("π  x + y + z - 3 = 0", _sin_colores(self.real.getvalue()))

    def test_con_imagenes(self):
        eventos = [[], [{"tipo": "tecla", "tecla": "derecha"}], [], [{"tipo": "tecla", "tecla": "b"}],
                   [{"tipo": "tecla", "tecla": "esc"}]]

        class Entorno(juego._Entorno):
            def es_terminal(self, salida):
                return True

            def leer(self):
                return eventos.pop(0) if eventos else [{"tipo": "tecla", "tecla": "esc"}]
        with mock.patch.object(juego, "_entorno", Entorno()), \
                mock.patch.object(raton, "activar_raton"), mock.patch.object(raton, "desactivar_raton"), \
                mock.patch("shutil.get_terminal_size", return_value=os.terminal_size((100, 30))):
            pantalla.ver_espacio(ESCENA, estilo="imagen")
        salida = self.real.getvalue()
        self.assertEqual(salida.count("\x1bP0;1;0q"), 2)
        self.assertIn("giro 30°", salida)
        self.assertTrue(salida.endswith("\x1b[?1049l"))

    def test_anadir_cosas(self):
        self.assertIsInstance(visor._leer_nuevo("(1, 2, 3)"), pantalla.Punto)
        self.assertIsInstance(visor._leer_nuevo("x + y = 2"), pantalla.Plano)
        self.assertIsInstance(visor._leer_nuevo("(x - 1)/2 = y = z"), pantalla.Recta3D)


if __name__ == "__main__":
    unittest.main()
