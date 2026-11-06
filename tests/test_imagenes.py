import base64
import os
import re
import struct
import tempfile
import unittest
import zlib
from unittest import mock

import pantalla
from pantalla import imagenes

from test_pantalla import Base


# 16x16: rojo arriba a la izquierda, azul arriba a la derecha, verde abajo a la izquierda, blanco abajo a la derecha
CUADROS = {(0, 0): (255, 0, 0), (1, 0): (0, 0, 255), (0, 1): (0, 255, 0), (1, 1): (255, 255, 255)}

JPG_444 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAIBAQEBAQIBAQECAgICAgQDAgICAgUEBAMEBgUGBgYFBgYGBwkIBgcJBwYGCAsICQoKCgoKBggLDAsK"
    "DAkKCgr/2wBDAQICAgICAgUDAwUKBwYHCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgr/wAARCAAQABAD"
    "AREAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKB"
    "kaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZ"
    "mqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQF"
    "BgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5"
    "OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX"
    "2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD4vr+Uz/fw+Q6/6qD/AJrz95K/4sz/ACnP2kr/AFQP9rD/2Q==")
JPG_420 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAIBAQEBAQIBAQECAgICAgQDAgICAgUEBAMEBgUGBgYFBgYGBwkIBgcJBwYGCAsICQoKCgoKBggLDAsK"
    "DAkKCgr/2wBDAQICAgICAgUDAwUKBwYHCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgr/wAARCAAQABAD"
    "ASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKB"
    "kaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZ"
    "mqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQF"
    "BgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5"
    "OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX"
    "2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD4vr5Dr95K/aSj6DP0mP8AiHH+sH/CV7f2/wBU/wCX/Jy8n1n/AKczvfn8rW630XEv"
    "0wf+J0fZf8In9lf2Vzf8xP1r2v1q3/UPh+Tk+r/3+bn+zy+9/9k=")
JPG_PROGRESIVO = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAIBAQEBAQIBAQECAgICAgQDAgICAgUEBAMEBgUGBgYFBgYGBwkIBgcJBwYGCAsICQoKCgoKBggLDAsK"
    "DAkKCgr/2wBDAQICAgICAgUDAwUKBwYHCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgr/wgARCAAQABAD"
    "ASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAABwj/xAAVAQEBAAAAAAAAAAAAAAAAAAAAAf/aAAwDAQACEAMQAAABFyG8rST/xAAUEAEAAAAA"
    "AAAAAAAAAAAAAAAg/9oACAEBAAEFAh//xAAhEQABAgQHAAAAAAAAAAAAAAAREhMDBQcUFyEkQUNhg//aAAgBAwEBPwGZVgxoTorW1PI6p3zhgN9k"
    "7DP/xAAfEQAABAcBAAAAAAAAAAAAAAAHERITAAEVFiRCUWL/2gAIAQIBAT8BAwTLcqGKtbW5ETnifY//xAAUEAEAAAAAAAAAAAAAAAAAAAAg/9oA"
    "CAEBAAY/Ah//xAAUEAEAAAAAAAAAAAAAAAAAAAAg/9oACAEBAAE/IR//2gAMAwEAAgADAAAAEAf/xAAVEQEBAAAAAAAAAAAAAAAAAAAA8f/aAAgB"
    "AwEBPxCf1DUf/8QAGREBAAIDAAAAAAAAAAAAAAAAESFBYXHw/9oACAECAQE/EOL95XULY//EABQQAQAAAAAAAAAAAAAAAAAAACD/2gAIAQEAAT8Q"
    "H//Z")
GIF = ("R0lGODdhEAAQAIEAAP///wD/AP8AAAAA/ywAAAAAEAAQAEAIRgAFCBwocIDBgwYDKFyoEIDDhw4JEkSIkCFDiBAlDqR4UGNBjgMsLsT4UGRDkgA8"
       "CgA5QCVLlyBhcjQZACUAmjZxotRJMiAAOw==")


def _color(x, y):
    return CUADROS[(x // 8, y // 8)]


def _pixeles_de(W, H, color):
    return [[color(x, y) for x in range(W)] for y in range(H)]


def _trozo(tipo, datos):
    return struct.pack(">I", len(datos)) + tipo + datos + struct.pack(">I", zlib.crc32(tipo + datos))


def _filtrar(fila, previa, f, bpp):
    # lo contrario de lo que hace el que lo lee, para probar los cinco filtros
    sale = bytearray()
    for i, v in enumerate(fila):
        a = fila[i - bpp] if i >= bpp else 0
        b = previa[i]
        c = previa[i - bpp] if i >= bpp else 0
        if f == 0:
            pred = 0
        elif f == 1:
            pred = a
        elif f == 2:
            pred = b
        elif f == 3:
            pred = (a + b) >> 1
        else:
            p = a + b - c
            pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
            pred = a if pa <= pb and pa <= pc else b if pb <= pc else c
        sale.append((v - pred) & 255)
    return bytes([f]) + bytes(sale)


def _png(pixeles, entrelazado=False, alfa=False):
    H, W = len(pixeles), len(pixeles[0])
    bpp = 4 if alfa else 3

    def filas_de(sub):
        datos, previa = b"", bytes(len(sub[0]) * bpp)
        for k, fila in enumerate(sub):
            crudo = bytes(v for p in fila for v in (p + (200,) if alfa else p))
            datos += _filtrar(crudo, previa, k % 5, bpp)
            previa = crudo
        return datos

    if not entrelazado:
        datos = filas_de(pixeles)
    else:
        datos = b""
        for x0, y0, dx, dy in ((0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4), (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2)):
            sub = [fila[x0::dx] for fila in pixeles[y0::dy]]
            if sub and sub[0]:
                datos += filas_de(sub)
    cab = struct.pack(">IIBBBBB", W, H, 8, 6 if alfa else 2, 0, 0, 1 if entrelazado else 0)
    return b"\x89PNG\r\n\x1a\n" + _trozo(b"IHDR", cab) + _trozo(b"IDAT", zlib.compress(datos)) + _trozo(b"IEND", b"")


def _bmp(pixeles):
    H, W = len(pixeles), len(pixeles[0])
    largo = (W * 3 + 3) // 4 * 4
    cuerpo = b"".join(bytes(v for p in fila for v in p[::-1]).ljust(largo, b"\x00") for fila in reversed(pixeles))
    cab = struct.pack("<IiiHHIIiiII", 40, W, H, 1, 24, 0, len(cuerpo), 2835, 2835, 0, 0)
    return b"BM" + struct.pack("<IHHI", 54 + len(cuerpo), 0, 0, 54) + cab + cuerpo


def _color_en(p, x, y):
    i = y * p.W + x
    return p.R[i], p.G[i], p.B[i]


class TestAbrir(unittest.TestCase):
    def setUp(self):
        self.sin_pillow = mock.patch.object(imagenes, "_con_pillow", return_value=None)
        self.sin_pillow.start()

    def tearDown(self):
        self.sin_pillow.stop()

    def comprobar(self, p, tolerancia=0, W=16, H=16):
        self.assertEqual((p.W, p.H), (W, H))
        for (x, y) in ((1, 1), (12, 2), (3, 13), (14, 14), (6, 6), (9, 9)):
            for a, b in zip(_color_en(p, x * W // 16, y * H // 16), _color(x, y)):
                self.assertLessEqual(abs(a - b), tolerancia, (x, y))

    def test_png_con_todos_los_filtros(self):
        self.comprobar(imagenes._abrir(_png(_pixeles_de(16, 16, _color))))

    def test_png_entrelazado(self):
        p = imagenes._abrir(_png(_pixeles_de(16, 16, _color), entrelazado=True))
        self.comprobar(p)
        # también uno raro que no es múltiplo de 8
        raro = _pixeles_de(13, 7, lambda x, y: (x * 19, y * 30, (x + y) * 7))
        p = imagenes._abrir(_png(raro, entrelazado=True, alfa=True))
        self.assertEqual([_color_en(p, x, y) for y in range(7) for x in range(13)], [c for f in raro for c in f])
        self.assertEqual(set(p.A), {200})

    def test_bmp(self):
        self.comprobar(imagenes._abrir(_bmp(_pixeles_de(16, 16, _color))))

    def test_ppm(self):
        cuerpo = bytes(v for fila in _pixeles_de(16, 16, _color) for p in fila for v in p)
        self.comprobar(imagenes._abrir(b"P6\n# un comentario\n16 16\n255\n" + cuerpo))
        texto = " ".join(str(v) for v in cuerpo)
        self.comprobar(imagenes._abrir(("P3 16 16 255 " + texto).encode()))

    def test_gif(self):
        self.comprobar(imagenes._abrir(base64.b64decode(GIF)))

    def test_jpg(self):
        self.comprobar(imagenes._abrir(base64.b64decode(JPG_444)), tolerancia=12)
        self.comprobar(imagenes._abrir(base64.b64decode(JPG_420)), tolerancia=40)
        # ya pequeño: un píxel por cada bloque de 8
        p = imagenes._abrir(base64.b64decode(JPG_444), minimo=(2, 2))
        self.comprobar(p, tolerancia=12, W=2, H=2)
        self.assertEqual(imagenes._medida_jpeg(base64.b64decode(JPG_444)), (16, 16))

    def test_jpg_progresivo_pide_pillow(self):
        with self.assertRaisesRegex(ValueError, "pillow"):
            imagenes._abrir(base64.b64decode(JPG_PROGRESIVO))

    def test_errores(self):
        with self.assertRaises(FileNotFoundError):
            imagenes._abrir("no_existe_esto.png")
        with self.assertRaisesRegex(ValueError, "no es PNG"):
            imagenes._abrir(b"hola, no soy una imagen")
        with self.assertRaisesRegex(ValueError, "rota"):
            imagenes._abrir(_png(_pixeles_de(16, 16, _color))[:40])
        with self.assertRaises(TypeError):
            imagenes._abrir(42)


class TestEscalar(unittest.TestCase):
    def test_media_de_cada_trozo(self):
        p = imagenes._abrir(_png(_pixeles_de(16, 16, _color)))
        q = imagenes._escalar(p, 2, 2)
        self.assertEqual([_color_en(q, x, y) for y in range(2) for x in range(2)],
                         [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 255)])
        q = imagenes._escalar(p, 1, 1)
        self.assertEqual(_color_en(q, 0, 0), (128, 128, 128))
        q = imagenes._escalar(p, 32, 8)
        self.assertEqual((q.W, q.H), (32, 8))

    def test_transparente_sobre_el_fondo(self):
        p = imagenes._Pixeles(2, 1, b"\xff\xff", b"\x00\x00", b"\x00\x00", b"\xff\x00")
        q = imagenes._sobre_fondo(p, (1, 2, 3))
        self.assertEqual((_color_en(q, 0, 0), _color_en(q, 1, 0)), ((255, 0, 0), (1, 2, 3)))


def _sin_colores(texto):
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", texto)


class TestImagen(Base):
    ANCHO, ALTO = 80, 30

    def setUp(self):
        super().setUp()
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.carpeta.name, "cuadros.png")
        with open(self.ruta, "wb") as f:
            f.write(_png(_pixeles_de(16, 16, _color)))

    def tearDown(self):
        self.carpeta.cleanup()
        super().tearDown()

    def test_con_bloques(self):
        salida = self.captura(pantalla.imagen, self.ruta, estilo="bloques")
        self.assertEqual(self.ultimo_resultado, (16, 8))
        lineas = salida.rstrip("\n").split("\n")
        self.assertEqual(len(lineas), 8)
        self.assertEqual(_sin_colores(lineas[0]), "█" * 16)
        self.assertIn("38;2;255;0;0", lineas[0])
        self.assertIn("38;2;0;0;255", lineas[0])

    def test_tamano(self):
        self.captura(pantalla.imagen, self.ruta, estilo="bloques", ancho=8)
        self.assertEqual(self.ultimo_resultado, (8, 4))
        self.captura(pantalla.imagen, self.ruta, estilo="bloques", alto=2)
        self.assertEqual(self.ultimo_resultado, (4, 2))
        # cabe en los dos y no se deforma
        self.captura(pantalla.imagen, self.ruta, estilo="bloques", ancho=40, alto=5)
        self.assertEqual(self.ultimo_resultado, (10, 5))
        salida = self.pinta(pantalla.imagen, self.ruta, 3, 2, estilo="letras", ancho=8)
        self.assertEqual(self.ultimo_resultado, (8, 4))
        fila = "".join(salida.celdas[1][2:10])
        self.assertTrue(fila.strip())
        self.assertEqual("".join(salida.celdas[1][:2]).strip(), "")

    def test_con_imagen_sixel_y_kitty(self):
        with mock.patch.dict(imagenes._capacidad, {"protocolo": "sixel", "imagenes": True}):
            salida = self.captura(pantalla.imagen, self.ruta, estilo="imagen")
        self.assertIn("\x1bP0;1;0q", salida)
        self.assertEqual(self.ultimo_resultado, (2, 1))
        with mock.patch.dict(imagenes._capacidad, {"protocolo": "kitty", "imagenes": True}):
            salida = self.captura(pantalla.imagen, self.ruta, 1, 1, estilo="imagen", ancho=20)
        self.assertIn("\x1b_Ga=T,f=24,o=z,s=200,v=200,c=20,r=10", salida)
        datos = "".join(re.findall(r"\x1b_G[^;]*;([^\x1b]*)\x1b\\", salida))
        crudo = zlib.decompress(base64.b64decode(datos))
        self.assertEqual(len(crudo), 200 * 200 * 3)
        self.assertEqual(tuple(crudo[:3]), (255, 0, 0))

    def test_kitty_en_trozos(self):
        p = imagenes._Pixeles(64, 64, os.urandom(4096), os.urandom(4096), os.urandom(4096))
        salida = imagenes._kitty(p, ident=5)
        trozos = re.findall(r"\x1b_G([^;]*);", salida)
        self.assertGreater(len(trozos), 2)
        self.assertIn("i=5", trozos[0])
        self.assertTrue(trozos[0].endswith("m=1"))
        self.assertEqual(trozos[-1], "m=0")

    def test_errores(self):
        with self.assertRaises(ValueError):
            pantalla.imagen(self.ruta, estilo="bonito")
        with self.assertRaises(TypeError):
            pantalla.imagen(self.ruta, 3)


class TestDetectar(unittest.TestCase):
    def test_kitty(self):
        respuesta = "\x1b]11;rgb:0000/0000/0000\x1b\\\x1b_Gi=31;OK\x1b\\\x1b[6;20;10t\x1b[?62;22c"
        with mock.patch.object(imagenes, "_preguntar_terminal", return_value=respuesta), \
                mock.patch("pantalla.terminal._es_terminal", return_value=True), \
                mock.patch.dict(imagenes._capacidad, {"imagenes": None, "protocolo": None}), \
                mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PANTALLA_IMAGENES", None)
            self.assertTrue(imagenes._puede_imagenes())
            self.assertEqual(imagenes._capacidad["protocolo"], "kitty")

    def test_forzado(self):
        with mock.patch.dict(imagenes._capacidad, {"imagenes": None, "protocolo": None}), \
                mock.patch.dict(os.environ, {"PANTALLA_IMAGENES": "kitty"}):
            self.assertTrue(imagenes._puede_imagenes())
            self.assertEqual(imagenes._capacidad["protocolo"], "kitty")

    def test_mac_con_pocos_colores(self):
        with mock.patch.dict(os.environ, {"TERM_PROGRAM": "Apple_Terminal", "COLORTERM": ""}):
            self.assertEqual(imagenes._codigo(255, 0, 0, False), "38;5;196")
        with mock.patch.dict(os.environ, {"TERM_PROGRAM": "vscode"}):
            self.assertEqual(imagenes._codigo(255, 0, 0, True), "48;2;255;0;0")


if __name__ == "__main__":
    unittest.main()
