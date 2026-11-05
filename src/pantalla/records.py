"""
Récords y tiempo, para los juegos: guardar las mejores puntuaciones en un archivo,
un cronómetro y una cuenta atrás.

    pos = pantalla.guardar_record("Ana", 120)          # 1 si es el mejor
    pantalla.tabla_records()                           # la tabla con los 10 mejores
    c = pantalla.cronometro()
    ...
    print(c)                                           # 00:12.3
    pantalla.cuenta_atras(3)                           # 3, 2, 1, ¡Ya!
"""

import datetime
import json
import os
import sys
import time

from .texto import escribir


def _ruta(archivo):
    """El archivo va en la carpeta de tu programa, no en la de donde abriste la terminal."""
    archivo = str(archivo)
    if os.path.isabs(archivo):
        return archivo
    programa = sys.argv[0] if sys.argv and sys.argv[0] not in ("", "-c") else ""
    carpeta = os.path.dirname(os.path.abspath(programa)) if programa else os.getcwd()
    return os.path.join(carpeta, archivo)


def _leer(archivo):
    ruta = _ruta(archivo)
    if not os.path.exists(ruta):
        return {"menos_es_mejor": False, "records": []}
    try:
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
        if isinstance(datos, dict) and isinstance(datos.get("records"), list):
            return datos
    except (OSError, ValueError):
        pass
    # si el archivo está roto, mejor empezar de cero que hacer fallar el juego
    return {"menos_es_mejor": False, "records": []}


def _ordenar(records, menos_es_mejor):
    return sorted(records, key=lambda r: r["puntos"], reverse=not menos_es_mejor)


def guardar_record(nombre, puntos, archivo="records.json", menos_es_mejor=False, cuantos=10):
    """Guarda una puntuación en un archivo y devuelve en qué puesto ha quedado (1 es el mejor).
    Si no entra entre los mejores, devuelve None.

        puesto = pantalla.guardar_record("Ana", 120)
        if puesto == 1:
            print("¡Nuevo récord!")
        pantalla.guardar_record("Luis", 34.5, "tiempos.json", menos_es_mejor=True)   # tiempos: gana el menor

    - cuantos: cuántos récords se guardan como mucho.
    El archivo se crea en la carpeta de tu programa.
    """
    if isinstance(puntos, bool) or not isinstance(puntos, (int, float)):
        raise TypeError("guardar_record: los puntos tienen que ser un número, y me has dado %r" % (puntos,))
    datos = _leer(archivo)
    datos["menos_es_mejor"] = bool(menos_es_mejor)
    nuevo = {"nombre": str(nombre), "puntos": puntos, "fecha": datetime.date.today().isoformat()}
    records = _ordenar(datos["records"] + [nuevo], menos_es_mejor)
    # si empata, el que ya estaba se queda delante
    records = [r for r in records if r is not nuevo]
    puesto = next((i for i, r in enumerate(records)
                   if (puntos < r["puntos"] if menos_es_mejor else puntos > r["puntos"])), len(records))
    records.insert(puesto, nuevo)
    datos["records"] = records[:cuantos]
    with open(_ruta(archivo), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    return puesto + 1 if puesto < cuantos else None


def leer_records(archivo="records.json"):
    """Los récords guardados, del mejor al peor, como una lista de (nombre, puntos).

        for nombre, puntos in pantalla.leer_records():
            print(nombre, puntos)
    """
    datos = _leer(archivo)
    return [(r["nombre"], r["puntos"]) for r in _ordenar(datos["records"], datos.get("menos_es_mejor"))]


def mejor_record(archivo="records.json"):
    """La mejor puntuación guardada, o None si todavía no hay ninguna.

        print("Récord:", pantalla.mejor_record())
    """
    records = leer_records(archivo)
    return records[0][1] if records else None


def tabla_records(archivo="records.json", x=None, y=None, color=None, color_cabecera="amarillo"):
    """Dibuja la tabla de récords: puesto, nombre, puntos y fecha.

        pantalla.tabla_records()
        pantalla.tabla_records("tiempos.json", 10, 5)
    """
    from .componentes import tabla

    datos = _leer(archivo)
    records = _ordenar(datos["records"], datos.get("menos_es_mejor"))
    if not records:
        escribir("Todavía no hay récords", x, y, color="gris", nueva_linea=x is None and y is None)
        return []
    filas = [[i, r["nombre"], r["puntos"], r.get("fecha", "")] for i, r in enumerate(records, 1)]
    tabla(filas, ["#", "Nombre", "Puntos", "Fecha"], x, y, color=color, color_cabecera=color_cabecera)
    return [(r["nombre"], r["puntos"]) for r in records]


class Cronometro(object):
    """Un cronómetro. Empieza a contar al crearlo.

        c = pantalla.Cronometro()       # o pantalla.cronometro()
        ...
        print(c.segundos)               # 12.34
        print(c)                        # 00:12.3
        c.parar()                       # se queda quieto
        c.empezar()                     # sigue contando desde donde iba
        c.reiniciar()                   # vuelve a 0 y sigue contando
    """

    def __init__(self, empezar=True):
        self._acumulado = 0.0
        self._desde = time.time() if empezar else None

    @property
    def segundos(self):
        """Los segundos que lleva contados."""
        return self._acumulado + (time.time() - self._desde if self._desde is not None else 0.0)

    @property
    def en_marcha(self):
        """True si está contando."""
        return self._desde is not None

    def empezar(self):
        """Empieza a contar (o sigue, si estaba parado)."""
        if self._desde is None:
            self._desde = time.time()
        return self

    def parar(self):
        """Para el cronómetro. Devuelve los segundos que lleva."""
        if self._desde is not None:
            self._acumulado += time.time() - self._desde
            self._desde = None
        return self._acumulado

    def reiniciar(self):
        """Vuelve a 0 y sigue contando."""
        self._acumulado = 0.0
        self._desde = time.time()
        return self

    def texto(self, decimas=True):
        """El tiempo como en un reloj: 01:23.4 (o 01:23 con decimas=False). Con horas, 1:02:03."""
        s = self.segundos
        if decimas:
            s = round(s, 1)
        h, resto = divmod(s, 3600)
        m, seg = divmod(resto, 60)
        t = ("%04.1f" % seg) if decimas else "%02d" % int(seg)
        return ("%d:%02d:%s" % (h, m, t)) if h else "%02d:%s" % (m, t)

    def __str__(self):
        return self.texto()

    def __repr__(self):
        return "Cronometro(%s)" % self.texto()


def cronometro():
    """Pone en marcha un cronómetro y lo devuelve.

        c = pantalla.cronometro()
        pantalla.pedir("Pulsa Enter cuando quieras... ")
        print("Has tardado", c)            # Has tardado 00:03.2
    """
    return Cronometro()


def cuenta_atras(segundos=3, x=None, y=None, color="amarillo", final="¡Ya!", grande=False):
    """Una cuenta atrás: 3, 2, 1, ¡Ya!, un número cada segundo.

        pantalla.cuenta_atras()                    # donde esté el cursor
        pantalla.cuenta_atras(5, 10, 3)            # en la columna 10, fila 3
        pantalla.cuenta_atras(3, grande=True)      # con letras grandes, en el centro

    final: lo que sale al acabar ("" para nada).
    """
    from .terminal import pausa

    if isinstance(segundos, bool) or not isinstance(segundos, int) or segundos < 0:
        raise TypeError("cuenta_atras: dime cuántos segundos con un número entero, por ejemplo cuenta_atras(3)")
    textos = [str(n) for n in range(segundos, 0, -1)] + ([final] if final else [])
    ancho = max([len(t) for t in textos] + [1])
    if grande:
        from .letras import grande as letras_grandes
        from .terminal import limpiar
        for i, t in enumerate(textos):
            limpiar()
            letras_grandes(t, x, y, color=color)
            if i < segundos:
                pausa(1)
        return
    for i, t in enumerate(textos):
        if x is None and y is None:
            escribir("\r" + t.ljust(ancho), color=color, negrita=True)
        else:
            escribir(t.ljust(ancho), x, y, color=color, negrita=True)
        if i < segundos:
            pausa(1)
    if x is None and y is None:
        escribir("", nueva_linea=True)
