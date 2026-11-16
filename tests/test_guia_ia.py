import io
import json
import os
import sys
import unittest
from unittest import mock

import pantalla
from pantalla import __main__ as demo

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIA = os.path.join(RAIZ, "src", "pantalla", "ia.md")


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read()


class TestGuiaIA(unittest.TestCase):
    def test_esta_al_dia(self):
        texto = leer(GUIA)
        self.assertIn("# pantalla %s · guía completa para IA" % pantalla.__version__, texto,
                      "La guía es de otra versión: ejecuta python scripts/guia_ia.py")
        for nombre in pantalla.__all__:
            if nombre in ("ESTILOS", "CODIGOS_COLOR"):
                continue
            self.assertIn("`pantalla.%s(" % nombre, texto, "Falta %s: ejecuta python scripts/guia_ia.py" % nombre)

    def test_web_igual_que_paquete(self):
        web = os.path.join(RAIZ, "docs", "pantalla-ia.md")
        if os.path.exists(web):
            self.assertEqual(leer(web), leer(GUIA))
        js = os.path.join(RAIZ, "docs", "pantalla-ia.json")
        if os.path.exists(js):
            datos = json.loads(leer(js))
            self.assertEqual(datos["version"], pantalla.__version__)

    def test_python_m_pantalla_ia(self):
        salida = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
        with mock.patch.object(sys, "stdout", salida):
            demo.guia_ia()
        salida.flush()
        self.assertEqual(salida.buffer.getvalue().decode("utf-8"), leer(GUIA))


if __name__ == "__main__":
    unittest.main()
