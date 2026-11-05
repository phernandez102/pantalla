"""
Pantallas de carga como las de los juegos: un título, una barra en el centro,
lo que se está haciendo debajo y consejos que van cambiando.
"""

import random
import sys
import threading
import time

from . import terminal as _t
from .colores import estilo as _estilo_ansi
from .componentes import _pintar_barra
from .dibujo import _piezas
from .spinners import _buscar_estilo
from .terminal import CSI, _entero, _estado, _fin_de_estilo, _juego, _mover, tamano

_CADA = 0.05
_CAMBIO_CONSEJO = 4.0


def _nombre_de(funcion):
    nombre = getattr(funcion, "__name__", "") or "Trabajando"
    if nombre == "<lambda>":
        return "Trabajando"
    nombre = nombre.replace("_", " ").strip()
    return nombre[:1].upper() + nombre[1:]


class PantallaDeCarga(object):
    """Una pantalla de carga. Créala con pantalla.pantalla_de_carga(...); mira su ayuda."""

    def __init__(self, titulo="Cargando", total=100, estilo="suave", color="cian", color_final=None,
                 ancho=40, fuente=None, spinner="dots", consejos=None, marco=None, color_titulo=None,
                 borrar=True):
        f = "pantalla_de_carga"
        if total is not None:
            if isinstance(total, bool) or not isinstance(total, (int, float)):
                raise TypeError("%s: total tiene que ser un número (o None si no sabes cuánto falta)" % f)
            if total <= 0:
                raise ValueError("%s: total tiene que ser mayor que 0" % f)
        self.ancho = _entero(ancho, "ancho", f)
        if self.ancho < 5:
            raise ValueError("%s: el ancho de la barra tiene que ser 5 o más" % f)
        # así salta ya el error si el estilo o los colores están mal
        _pintar_barra(0.5, self.ancho, estilo, color, color_final, funcion=f)
        _estilo_ansi(color_titulo)
        self.titulo = str(titulo)
        self.total = total
        self.estilo = estilo
        self.color = color
        self.color_final = color_final
        self.color_titulo = color_titulo
        self.borrar = borrar
        if fuente is not None:
            from .letras import texto_grande
            lineas = texto_grande(self.titulo, fuente=fuente).split("\n")
            while lineas and not lineas[-1].strip():
                lineas.pop()
            self._titulo = lineas or [self.titulo]
        else:
            self._titulo = [self.titulo]
        if spinner:
            self._milis, self._giro = _buscar_estilo(spinner)
        else:
            self._milis, self._giro = 100, [""]
        if consejos is None:
            consejos = []
        elif isinstance(consejos, str):
            consejos = [consejos]
        self.consejos = [str(c) for c in consejos]
        if marco is not None:
            _piezas(marco, f)
        self.marco = marco
        self.texto = ""
        self._valor = 0
        self._mostrado = 0.0
        self._consejo = random.randrange(len(self.consejos)) if self.consejos else 0
        self._inicio = 0.0
        self._ultimo_consejo = 0.0
        self._hilo = None
        self._parar = threading.Event()
        self._animado = False
        self._tamano = None
        self._final = None
        self._cursor_antes = False

    # --- lo que usas tú ---

    @property
    def valor(self):
        """Por dónde va (de 0 a total)."""
        return self._valor

    @valor.setter
    def valor(self, nuevo):
        if isinstance(nuevo, bool) or not isinstance(nuevo, (int, float)):
            raise TypeError("pantalla_de_carga: el valor tiene que ser un número, y es %r" % (nuevo,))
        tope = self.total if self.total is not None else 0
        self._valor = max(0, min(tope, nuevo))

    def avanzar(self, cuanto=1, texto=None):
        """Avanza la barra (1 si no dices cuánto) y, si quieres, cambia el texto de debajo.

            carga.avanzar()
            carga.avanzar(10, "Cargando sonidos")
        """
        if texto is not None:
            self.poner_texto(texto)
        if self.total is not None:
            self.valor = self._valor + cuanto
        return self

    def poner_texto(self, texto):
        """Cambia lo que pone debajo de la barra (también vale carga.texto = "...")."""
        texto = str(texto)
        if texto != self.texto and self._hilo is False and texto:
            _t._salida("  " + texto + "\n")
        self.texto = texto
        return self

    def empezar(self):
        """Saca la pantalla de carga. pantalla_de_carga() ya lo hace sola."""
        if self._hilo is not None:
            return self
        if _juego["pintar"] is not None:
            raise RuntimeError("pantalla_de_carga: no se puede usar dentro de jugar(). Ponla antes, "
                               "o dibuja una barra_progreso() en cada fotograma")
        self._animado = _t._es_terminal(sys.stdout)
        self._inicio = self._ultimo_consejo = time.time()
        if not self._animado:
            _t._salida(self.titulo + "...\n")
            self._hilo = False
            return self
        self._cursor_antes = _estado["cursor_oculto"]
        _t.ocultar_cursor()
        self._parar.clear()
        self._pintar()
        self._hilo = threading.Thread(target=self._girar, name="pantalla-carga")
        self._hilo.daemon = True
        self._hilo.start()
        return self

    def terminar(self, texto="Listo"):
        """Llena la barra, enseña "✔ Listo" un momento y la quita (con borrar=False la deja)."""
        if self.total is not None:
            self._valor = self.total
        if self._hilo is None:
            return self
        if self._hilo is False:
            self._hilo = None
            _t._salida("✔ " + str(texto) + "\n")
            return self
        hasta = time.time() + 0.6
        while self.total is not None and self._mostrado < self.total and time.time() < hasta:
            time.sleep(_CADA)
        self._mostrado = self.total if self.total is not None else 1
        self._final = str(texto)
        self._detener()
        self._pintar()
        time.sleep(0.35)
        self._quitar()
        return self

    def parar(self):
        """La quita sin llenar la barra."""
        hilo = self._detener()
        if hilo:
            self._quitar()
        return self

    def __enter__(self):
        return self.empezar()

    def __exit__(self, tipo, valor, traza):
        if tipo is None:
            self.terminar()
        else:
            self.parar()
        return False

    # --- por dentro ---

    def _detener(self):
        hilo, self._hilo = self._hilo, None
        if hilo:
            self._parar.set()
            if hilo is not threading.current_thread():
                hilo.join()
        return hilo

    def _quitar(self):
        if self.borrar:
            _t.limpiar()
        if not self._cursor_antes:
            _t.mostrar_cursor()

    def _girar(self):
        while not self._parar.wait(_CADA):
            if self.total is not None:
                falta = self._valor - self._mostrado
                if abs(falta) < self.total * 0.002:
                    self._mostrado = float(self._valor)
                else:
                    self._mostrado += falta * 0.25
            if self.consejos and time.time() - self._ultimo_consejo >= _CAMBIO_CONSEJO:
                self._ultimo_consejo = time.time()
                self._consejo = (self._consejo + 1) % len(self.consejos)
            self._pintar()

    def _lineas(self, ancho_p, alto_p):
        """Calcula qué va en cada sitio: lista de (x, y, texto con colores)."""
        pct = 5 if self.total is not None else 0
        ancho = max(3, min(self.ancho, ancho_p - 4 - pct))
        trozo = None
        if self.total is None:
            if self._final is not None:
                fraccion = 1.0
            else:
                fraccion = 0.0
                largo = max(2, ancho // 5)
                vuelta = max(1, ancho - largo)
                paso = int((time.time() - self._inicio) / _CADA) % (2 * vuelta)
                trozo = (paso if paso < vuelta else 2 * vuelta - paso, largo)
        else:
            fraccion = max(0.0, min(1.0, self._mostrado / float(self.total)))
        barra = _pintar_barra(fraccion, ancho, self.estilo, self.color, self.color_final,
                              funcion="pantalla_de_carga", trozo=trozo)
        if pct:
            barra += " %3d%%" % int(round(fraccion * 100))
        bloque = ancho + pct
        titulo = self._titulo
        if max(len(l) for l in titulo) > ancho_p - 6:
            # las letras grandes no caben: mejor el título normal
            titulo = [self.titulo[: max(1, ancho_p - 2)]]
        ancho_titulo = max(len(l) for l in titulo)
        alto = len(titulo) + 3 + (3 if self.consejos else 0)
        y0 = max(1, (alto_p - alto) // 2 + 1)
        xb = max(1, (ancho_p - bloque) // 2 + 1)
        xt = max(1, (ancho_p - ancho_titulo) // 2 + 1)
        fin = _fin_de_estilo()
        cod_t = _estilo_ansi(self.color_titulo or self.color, negrita=True)
        cosas = [(xt, y0 + i, cod_t + l + fin) for i, l in enumerate(titulo)]
        yb = y0 + len(titulo) + 1
        cosas.append((xb, yb, barra))
        if self._final is not None:
            debajo = _estilo_ansi("verde") + "✔" + fin + " " + self._final
            largo = 2 + len(self._final)
        else:
            giro = self._giro[int((time.time() - self._inicio) * 1000 / self._milis) % len(self._giro)]
            texto = self.texto[: max(0, bloque - len(giro) - 1)]
            debajo = _estilo_ansi(self.color) + giro + fin + (" " + texto if giro else texto)
            largo = len(giro) + (1 if giro else 0) + len(texto)
        cosas.append((xb, yb + 1, debajo + " " * max(0, bloque - largo)))
        if self.consejos:
            todos = max(len(c) for c in self.consejos)
            consejo = self.consejos[self._consejo][: ancho_p - 2]
            hueco = max(1, (ancho_p - todos) // 2 + 1)
            x = max(1, (ancho_p - len(consejo)) // 2 + 1)
            linea = " " * (x - hueco) + _estilo_ansi("gris") + consejo + fin
            cosas.append((hueco, yb + 4, linea + " " * max(0, todos - len(consejo) - (x - hueco))))
        caja_marco = None
        if self.marco is not None:
            izq = max(1, min(xb, xt, hueco if self.consejos else xb) - 3)
            der = min(ancho_p, max(xb + bloque, xt + ancho_titulo,
                                   (hueco + todos) if self.consejos else 0) + 2)
            caja_marco = (izq, max(1, y0 - 1), der - izq + 1, min(alto_p - max(1, y0 - 1) + 1, alto + 2))
        return cosas, caja_marco

    def _pintar(self):
        ancho_p, alto_p = tamano()
        cosas, caja_marco = self._lineas(ancho_p, alto_p)
        trozos = []
        if self._tamano != (ancho_p, alto_p):
            self._tamano = (ancho_p, alto_p)
            trozos.append(CSI + "2J")
            if caja_marco is not None:
                trozos.append(self._texto_marco(*caja_marco))
        for x, y, texto in cosas:
            if 1 <= y <= alto_p:
                trozos.append(_mover(x, y) + texto)
        _t._salida("".join(trozos))

    def _texto_marco(self, x, y, ancho, alto):
        p = _piezas(self.marco, "pantalla_de_carga")
        cod = _estilo_ansi(self.color_titulo or self.color)
        fin = _fin_de_estilo()
        filas = [p[0] + p[9] * (ancho - 2) + p[2]]
        filas += [p[10] + " " * (ancho - 2) + p[10]] * (alto - 2)
        filas.append(p[6] + p[9] * (ancho - 2) + p[8])
        return "".join(_mover(x, y + i) + cod + f + fin for i, f in enumerate(filas))


def _curva_de_mentira(segundos):
    # unos cuantos parones al azar para que parezca que carga de verdad
    marcas = sorted(random.uniform(0.1, 0.9) for _ in range(3))
    tiempos = [0.0] + [m * segundos for m in marcas] + [float(segundos)]
    valores = [0.0] + sorted(random.uniform(0.15, 0.95) for _ in range(3)) + [1.0]

    def valor(t):
        for i in range(1, len(tiempos)):
            if t <= tiempos[i]:
                tramo = tiempos[i] - tiempos[i - 1] or 1
                return valores[i - 1] + (valores[i] - valores[i - 1]) * (t - tiempos[i - 1]) / tramo
        return 1.0
    return valor


def pantalla_de_carga(titulo="Cargando", segundos=None, tareas=None, total=100, estilo="suave",
                      color="cian", color_final=None, ancho=40, fuente=None, spinner="dots",
                      consejos=None, marco=None, color_titulo=None, borrar=True):
    """Una pantalla de carga como la de los juegos, con la barra en el centro.

    Hay tres formas de usarla, de la más fácil a la más completa:

    1. De mentira, para que quede bonito: carga durante unos segundos y se va.

        pantalla.pantalla_de_carga("Cargando nivel 1", segundos=3)

    2. Con tareas: va haciendo cada una y la barra avanza sola.
       Un texto es un paso de mentira, una función se llama de verdad.

        pantalla.pantalla_de_carga("Preparando", tareas=["Cargando mapa", "Colocando enemigos"], segundos=2)
        mapa, sonidos = pantalla.pantalla_de_carga("Cargando", tareas=[("Mapa", leer_mapa),
                                                                       ("Sonidos", leer_sonidos)])

    3. Tú mueves la barra, con with:

        with pantalla.pantalla_de_carga("Descargando", total=len(archivos)) as carga:
            for archivo in archivos:
                carga.avanzar(texto=archivo)     # o carga.valor = 7
                descargar(archivo)

    - estilo: el de la barra ("suave", "bloques", "linea", "ascii", "puntos"...). Mira pantalla.lista_barras().
    - color, color_final: el color de la barra (con color_final va cambiando de uno a otro).
    - fuente: el título en letras grandes, con una fuente de pantalla.lista_fuentes().
    - spinner: el estilo de la ruedecita de al lado del texto (None para quitarla).
    - consejos: una lista de frases que van cambiando abajo, cada 4 segundos.
    - marco: un borde alrededor ("redondo", "doble"...).
    - total=None: para cuando no sabes cuánto falta; la barra va y viene.
    - borrar=False: deja la pantalla como ha quedado al acabar.

    Las formas 1 y 2 esperan a que acabe; la 2 devuelve lo que devuelvan tus funciones.
    La 3 devuelve la pantalla de carga: carga.avanzar(), carga.valor, carga.texto y carga.terminar().
    """
    if tareas is None and segundos is None:
        return PantallaDeCarga(titulo, total, estilo, color, color_final, ancho, fuente, spinner,
                               consejos, marco, color_titulo, borrar).empezar()
    if segundos is not None:
        if isinstance(segundos, bool) or not isinstance(segundos, (int, float)) or segundos < 0:
            raise TypeError("pantalla_de_carga: segundos tiene que ser un número de 0 para arriba")
    if tareas is not None:
        if isinstance(tareas, str) or callable(tareas):
            tareas = [tareas]
        lista = []
        for t in tareas:
            if isinstance(t, (list, tuple)) and len(t) == 2 and callable(t[1]):
                lista.append((str(t[0]), t[1]))
            elif callable(t):
                lista.append((_nombre_de(t), t))
            elif isinstance(t, str):
                lista.append((t, None))
            else:
                raise TypeError("pantalla_de_carga: cada tarea es un texto, una función o "
                                "(\"texto\", funcion). Esta no: %r" % (t,))
        if not lista:
            raise ValueError("pantalla_de_carga: la lista de tareas está vacía")
    else:
        lista = None
    carga = PantallaDeCarga(titulo, total, estilo, color, color_final, ancho, fuente, spinner,
                            consejos, marco, color_titulo, borrar)
    carga.empezar()
    try:
        if lista is None:
            curva = _curva_de_mentira(segundos)
            inicio = time.time()
            while True:
                t = time.time() - inicio
                if total is not None:
                    carga.valor = total * curva(t)
                if t >= segundos:
                    break
                time.sleep(min(_CADA, max(0.0, segundos - t)))
            carga.terminar()
            return None
        resultados = []
        de_mentira = sum(1 for _, f in lista if f is None)
        cada_una = (segundos if segundos is not None else 0.6 * de_mentira) / float(max(1, de_mentira))
        for i, (texto, funcion) in enumerate(lista):
            carga.poner_texto(texto)
            tope = total if total is not None else 0
            antes = tope * i / float(len(lista))
            despues = tope * (i + 1) / float(len(lista))
            if funcion is None:
                inicio = time.time()
                while time.time() - inicio < cada_una:
                    parte = (time.time() - inicio) / cada_una
                    carga.valor = antes + (despues - antes) * parte
                    time.sleep(_CADA)
                resultados.append(None)
            else:
                resultados.append(funcion())
            carga.valor = despues
        carga.terminar()
    except BaseException:
        carga.parar()
        raise
    if all(f is None for _, f in lista):
        return None
    return [r for (_, f), r in zip(lista, resultados) if f is not None]
