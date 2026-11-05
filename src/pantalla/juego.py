"""
Juegos sin bucles: tú escribes qué pasa en cada momento y pantalla hace el resto.

    import pantalla

    x = 10

    def actualizar(tecla):
        global x
        if tecla == "derecha":
            x = x + 1
        pantalla.escribir("@", x, 5, color="amarillo")

    pantalla.jugar(actualizar)

jugar() llama a tu función muchas veces por segundo (20 si no dices otra cosa).
Cada vez la pantalla empieza vacía: tú dibujas cómo está todo en ese momento con
las funciones de siempre (escribir, caja, punto, grande, arte...) y pantalla
enseña solo lo que ha cambiado, así que no parpadea. Esc acaba el juego.

Para cosas que se mueven, choques y animaciones están los Sprite:

    nave = pantalla.Sprite("/^\\\\", 38, 22, color="verde")
    nave.mover(1, 0)
    if bala.choca(nave): ...
"""

import functools
import inspect
import math
import re
import shutil
import sys
import time
import unicodedata

from . import terminal as _t
from .arte import CODIGOS_COLOR
from .colores import codigo_color
from .terminal import CSI, RESET, _estado, _juego


_NORMAL = ((), None, None)
_VACIA = (" ", _NORMAL)

_SECUENCIA = re.compile(
    r"\x1b\[([0-9;?]*)([ -/]*)([@-~])"
    r"|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)"
    r"|\x1b([78])"
    r"|\x1b(.)"
    r"|([\r\n\x07\x08\x00-\x06\x0b-\x0c\x0e-\x1a\x1c-\x1f])"
)


@functools.lru_cache(maxsize=4096)
def _ancho_letra(c):
    if unicodedata.combining(c) or unicodedata.category(c) in ("Mn", "Me", "Cf"):
        return 0
    return 2 if unicodedata.east_asian_width(c) in ("W", "F") else 1


@functools.lru_cache(maxsize=1024)
def _aplicar_sgr(estilo, parametros):
    atributos, color, fondo = estilo
    atributos = set(atributos)
    numeros = [int(p) if p.isdigit() else 0 for p in parametros.split(";")] if parametros else [0]
    i = 0
    while i < len(numeros):
        n = numeros[i]
        if n == 0:
            atributos, color, fondo = set(), None, None
        elif n in (1, 2, 3, 4, 5, 7, 8, 9):
            atributos.add(n)
        elif n == 22:
            atributos -= {1, 2}
        elif n in (23, 24, 25, 27, 28, 29):
            atributos.discard(n - 20)
        elif 30 <= n <= 37 or 90 <= n <= 97:
            color = str(n)
        elif n == 39:
            color = None
        elif 40 <= n <= 47 or 100 <= n <= 107:
            fondo = str(n)
        elif n == 49:
            fondo = None
        elif n in (38, 48) and i + 1 < len(numeros):
            valor = None
            if numeros[i + 1] == 5 and i + 2 < len(numeros):
                valor = "%d;5;%d" % (n, numeros[i + 2])
                i += 2
            elif numeros[i + 1] == 2 and i + 4 < len(numeros):
                valor = "%d;2;%d;%d;%d" % (n, numeros[i + 2], numeros[i + 3], numeros[i + 4])
                i += 4
            else:
                i += 1
            if valor is not None:
                if n == 38:
                    color = valor
                else:
                    fondo = valor
        i += 1
    return (tuple(sorted(atributos)), color, fondo)


def _estilo_de_ansi(codigo):
    estilo = _NORMAL
    for m in re.finditer(r"\x1b\[([0-9;]*)m", codigo or ""):
        estilo = _aplicar_sgr(estilo, m.group(1))
    return estilo


# pantalla de mentira: lo que se dibuja se apunta aqui y luego solo se manda
# a la terminal lo que ha cambiado, que si no parpadea un monton
class _Lienzo(object):
    """Una pantalla de ancho x alto celdas que entiende los códigos que escribe pantalla."""

    def __init__(self, ancho, alto, al_pasar=None):
        self.ancho = ancho
        self.alto = alto
        self.al_pasar = al_pasar
        self.vaciar()

    def vaciar(self, estilo=_NORMAL):
        self.celdas = [[_VACIA] * self.ancho for _ in range(self.alto)]
        self.x = 1
        self.y = 1
        self.estilo = estilo
        self.guardado = (1, 1, estilo)

    def escribir(self, texto):
        pos = 0
        for m in _SECUENCIA.finditer(texto):
            if m.start() > pos:
                self._letras(texto[pos:m.start()])
            pos = m.end()
            parametros, intermedios, final, guardar, esc_suelto, control = m.groups()
            if final is not None:
                if not intermedios:
                    self._csi(parametros, final)
            elif guardar is not None:
                if guardar == "7":
                    self.guardado = (self.x, self.y, self.estilo)
                else:
                    self.x, self.y, self.estilo = self.guardado
            elif control is not None:
                self._control(control)
            elif esc_suelto is None:
                self._pasar(m.group(0))
        if pos < len(texto):
            self._letras(texto[pos:])

    def _pasar(self, codigo):
        if self.al_pasar is not None:
            self.al_pasar(codigo)

    def _control(self, c):
        if c == "\r":
            self.x = 1
        elif c == "\n":
            self.x = 1
            self._bajar()
        elif c == "\x08":
            self.x = max(1, self.x - 1)
        elif c == "\x07":
            self._pasar(c)

    def _bajar(self):
        if self.y < self.alto:
            self.y += 1
        else:
            del self.celdas[0]
            self.celdas.append([_VACIA] * self.ancho)

    def _celda_borrada(self):
        return (" ", ((), None, self.estilo[2]))

    def _csi(self, parametros, final):
        if parametros.startswith("?"):
            if parametros[1:] != "1049":
                self._pasar(CSI + parametros + final)
            return
        numeros = [int(p) if p.isdigit() else 0 for p in parametros.split(";")] if parametros else []

        def n(i, defecto):
            return numeros[i] if len(numeros) > i and numeros[i] else defecto

        if final == "m":
            self.estilo = _aplicar_sgr(self.estilo, parametros)
        elif final in "Hf":
            self.y = min(max(n(0, 1), 1), self.alto)
            self.x = min(max(n(1, 1), 1), self.ancho)
        elif final == "G":
            self.x = min(max(n(0, 1), 1), self.ancho)
        elif final == "d":
            self.y = min(max(n(0, 1), 1), self.alto)
        elif final == "A":
            self.y = max(1, self.y - n(0, 1))
        elif final == "B":
            self.y = min(self.alto, self.y + n(0, 1))
        elif final == "C":
            self.x = min(self.ancho, self.x + n(0, 1))
        elif final == "D":
            self.x = max(1, self.x - n(0, 1))
        elif final == "J":
            modo = n(0, 0)
            vacia = self._celda_borrada()
            if modo in (2, 3):
                self.celdas = [[vacia] * self.ancho for _ in range(self.alto)]
            elif modo == 0:
                self._borrar_fila(self.y, self.x, self.ancho, vacia)
                for fila in range(self.y + 1, self.alto + 1):
                    self.celdas[fila - 1] = [vacia] * self.ancho
            elif modo == 1:
                for fila in range(1, self.y):
                    self.celdas[fila - 1] = [vacia] * self.ancho
                self._borrar_fila(self.y, 1, self.x, vacia)
        elif final == "K":
            modo = n(0, 0)
            vacia = self._celda_borrada()
            desde, hasta = {0: (self.x, self.ancho), 1: (1, self.x)}.get(modo, (1, self.ancho))
            self._borrar_fila(self.y, desde, hasta, vacia)
        elif final == "X":
            self._borrar_fila(self.y, self.x, min(self.ancho, self.x + n(0, 1) - 1),
                              self._celda_borrada())
        elif final == "s":
            self.guardado = (self.x, self.y, self.estilo)
        elif final == "u":
            self.x, self.y, self.estilo = self.guardado

    def _borrar_fila(self, y, desde, hasta, vacia):
        if 1 <= y <= self.alto:
            fila = self.celdas[y - 1]
            for x in range(max(1, desde), min(self.ancho, hasta) + 1):
                fila[x - 1] = vacia

    def _letras(self, texto):
        for c in texto:
            if c < "̀":
                ancho = 1
            else:
                ancho = _ancho_letra(c)
                if ancho == 0:
                    self._juntar(c)
                    continue
            self.poner(self.x, self.y, c, self.estilo, ancho)
            self.x += ancho

    def _juntar(self, c):
        if 1 <= self.y <= self.alto and 2 <= self.x <= self.ancho + 1:
            fila = self.celdas[self.y - 1]
            i = self.x - 2
            if fila[i][0] == "" and i > 0:
                i -= 1
            fila[i] = (fila[i][0] + c, fila[i][1])

    def poner(self, x, y, c, estilo, ancho=1):
        """Pone una letra en (x, y). Lo que se sale de la pantalla no se ve (no salta de línea)."""
        if not (1 <= y <= self.alto and 1 <= x <= self.ancho):
            return
        fila = self.celdas[y - 1]
        i = x - 1
        if ancho == 2 and x == self.ancho:
            c, ancho = " ", 1
        if fila[i][0] == "" and i > 0:
            fila[i - 1] = (" ", fila[i - 1][1])
        if i + 1 < self.ancho and fila[i + 1][0] == "":
            fila[i + 1] = (" ", fila[i + 1][1])
        fila[i] = (c, estilo)
        if ancho == 2:
            if i + 2 < self.ancho and fila[i + 2][0] == "":
                fila[i + 2] = (" ", fila[i + 2][1])
            fila[i + 1] = ("", estilo)

    def hueco(self, x, y):
        """True si en (x, y) no hay nada dibujado (un espacio sin color de fondo)."""
        if not (1 <= y <= self.alto and 1 <= x <= self.ancho):
            return False
        c, estilo = self.celdas[y - 1][x - 1]
        return c == " " and estilo[2] is None and 7 not in estilo[0]

    def texto(self):
        """Lo que hay en la pantalla, como texto (sin colores). Útil para probar."""
        return "\n".join("".join(c for c, _ in fila).rstrip() for fila in self.celdas)

    def celda(self, x, y):
        return self.celdas[y - 1][x - 1]


class _Captura(object):
    encoding = "utf-8"
    errors = "replace"

    def __init__(self, partida, real):
        self._partida = partida
        self._real = real

    def write(self, texto):
        self._partida.lienzo.escribir(str(texto))
        return len(texto)

    def writelines(self, lineas):
        for l in lineas:
            self.write(l)

    def flush(self):
        pass

    def isatty(self):
        return True

    def fileno(self):
        return self._real.fileno()

    def __getattr__(self, nombre):
        return getattr(self._real, nombre)


class _Pintor(object):
    def __init__(self, escribir_real, fondo=None):
        self.escribir_real = escribir_real
        self.fondo = fondo
        self.antes = None
        self.completo = True
        self.codigos = {}

    def _codigo(self, estilo):
        codigo = self.codigos.get(estilo)
        if codigo is None:
            atributos, color, fondo = estilo
            partes = ["0"] + [str(a) for a in atributos]
            if color:
                partes.append(color)
            if fondo or self.fondo:
                partes.append(fondo or self.fondo)
            codigo = self.codigos[estilo] = CSI + ";".join(partes) + "m"
        return codigo

    def pintar(self, lienzo, ancho_real, alto_real, extra=""):
        ancho = min(lienzo.ancho, ancho_real)
        alto = min(lienzo.alto, alto_real)
        trozos = [extra] if extra else []
        if self.completo or self.antes is None or len(self.antes) != lienzo.alto or \
                (self.antes and len(self.antes[0]) != lienzo.ancho):
            trozos.append(self._codigo(_NORMAL) + CSI + "2J")
            self.antes = [[None] * lienzo.ancho for _ in range(lienzo.alto)]
            self.completo = False
        actual = None
        for y in range(alto):
            nueva = lienzo.celdas[y]
            vieja = self.antes[y]
            if nueva == vieja:
                continue
            x = 0
            while x < ancho:
                if nueva[x] == vieja[x]:
                    x += 1
                    continue
                inicio = x - 1 if (nueva[x][0] == "" and x > 0) else x
                fin = x
                iguales = 0
                j = x + 1
                while j < ancho:
                    if nueva[j] != vieja[j]:
                        fin = j
                        iguales = 0
                    else:
                        iguales += 1
                        # con pocas iguales en medio sale mas barato reescribirlas que mover el cursor
                        if iguales > 4:
                            break
                    j += 1
                if fin + 1 < ancho and nueva[fin + 1][0] == "":
                    fin += 1
                trozos.append("%s%d;%dH" % (CSI, y + 1, inicio + 1))
                for k in range(inicio, fin + 1):
                    c, estilo = nueva[k]
                    if c == "":
                        continue
                    if estilo != actual:
                        trozos.append(self._codigo(estilo))
                        actual = estilo
                    if k + 1 >= ancho and k + 1 < lienzo.ancho and nueva[k + 1][0] == "":
                        c = " "
                    trozos.append(c)
                x = fin + 1
            self.antes[y] = nueva[:]
        if actual is not None or len(trozos) > (1 if extra else 0):
            trozos.append(RESET)
        trozos.append("%s%d;%dH" % (CSI, min(lienzo.y, alto_real), min(lienzo.x, ancho_real)))
        self.escribir_real("".join(trozos))


_VK = {
    "izquierda": 0x25, "arriba": 0x26, "derecha": 0x27, "abajo": 0x28,
    "espacio": 0x20, "enter": 0x0D, "esc": 0x1B, "tab": 0x09, "borrar": 0x08,
    "mayus": 0x10, "ctrl": 0x11, "alt": 0x12, "inicio": 0x24, "fin": 0x23,
    "repag": 0x21, "avpag": 0x22, "suprimir": 0x2E, "insertar": 0x2D,
}
_VK.update({"f%d" % (i + 1): 0x70 + i for i in range(12)})
_VK.update({chr(c).lower(): c for c in range(ord("A"), ord("Z") + 1)})
_VK.update({str(d): 0x30 + d for d in range(10)})

_ALIAS_TECLAS = {
    "left": "izquierda", "right": "derecha", "up": "arriba", "down": "abajo",
    "space": "espacio", " ": "espacio", "escape": "esc", "return": "enter",
    "shift": "mayus", "mayús": "mayus", "mayusculas": "mayus", "control": "ctrl",
    "backspace": "borrar", "home": "inicio", "end": "fin", "delete": "suprimir",
}


def _nombre_tecla(nombre):
    if not isinstance(nombre, str) or not nombre:
        raise TypeError("pulsada: dime el nombre de una tecla, por ejemplo pulsada(\"izquierda\")")
    from .teclado import _canon
    n = nombre.strip().lower() if len(nombre) > 1 else nombre.lower()
    n = _ALIAS_TECLAS.get(n, n)
    return _canon(n)


class _Entorno(object):
    def es_terminal(self, salida):
        return _t._es_terminal(sys.stdin) and _t._es_terminal(salida)

    def tamano(self):
        medida = shutil.get_terminal_size((80, 24))
        return medida.columns, medida.lines

    def ahora(self):
        return time.monotonic()

    def dormir(self, segundos):
        time.sleep(segundos)

    def leer(self):
        """Todo lo que se ha pulsado desde la última vez, sin esperar (lista de eventos)."""
        from . import raton, teclado
        eventos = []
        try:
            for _ in range(200):
                if raton._raton["activo"]:
                    if raton._raton["clics"]:
                        ev = raton._raton["clics"].pop(0)
                    elif teclado._teclas_pendientes:
                        ev = {"tipo": "tecla", "tecla": teclado._teclas_pendientes.pop(0)}
                    else:
                        ev = raton._leer_evento(espera=False)
                else:
                    t = teclado.tecla_pulsada()
                    ev = {"tipo": "tecla", "tecla": t} if t else None
                if ev is None:
                    break
                eventos.append(ev)
        except EOFError:
            pass
        return eventos

    def esperar_evento(self):
        from . import raton
        return raton._leer_evento(espera=True)

    def tecla_abajo(self, nombre):
        """True/False si se sabe si la tecla está apretada ahora mismo; None si no se puede saber."""
        if sys.platform != "win32":
            return None
        vk = _VK.get(nombre)
        if vk is None:
            return None
        try:
            import ctypes
            return bool(ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000)
        except Exception:
            return None


_entorno = _Entorno()


_partida = {"actual": None}
_sprites = []
_relojes = {}


def _pintar_sprites(lienzo):
    vivos = [s for s in _sprites if s.vivo and s.visible]
    fondo = sorted((s for s in vivos if s.capa < 0), key=lambda s: s.capa, reverse=True)
    encima = sorted((s for s in vivos if s.capa >= 0), key=lambda s: s.capa)
    for s in fondo + encima:
        s._pintar_en(lienzo, solo_huecos=s.capa < 0)
        s._pasos += 1


def _vale(resultado):
    return resultado is not None and resultado is not False


def _acepta_tecla(funcion):
    try:
        firma = inspect.signature(funcion)
    except (TypeError, ValueError):
        return True
    for p in firma.parameters.values():
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.VAR_POSITIONAL):
            return True
    return False


class _Partida(object):
    def __init__(self, velocidad, ancho, alto, fondo, salir_con, real):
        self.velocidad = velocidad
        self.ancho_fijo = ancho
        self.alto_fijo = alto
        self.salir_con = _nombre_tecla(salir_con) if salir_con else None
        self.real = real
        self.fotograma = 0
        self.vistas = {}
        self.pintor = _Pintor(self._escribir_real, fondo)
        self.lienzo = None
        self.leyendo = False
        self._medir()

    def _escribir_real(self, texto):
        if texto:
            with _t._cerrojo:
                self.real.write(texto)
                self.real.flush()

    def _medir(self):
        real_ancho, real_alto = _entorno.tamano()
        self.real_tamano = (real_ancho, real_alto)
        ancho = self.ancho_fijo or real_ancho
        alto = self.alto_fijo or real_alto
        if self.lienzo is None or (self.lienzo.ancho, self.lienzo.alto) != (ancho, alto):
            self.lienzo = _Lienzo(ancho, alto, self._escribir_real)
            self.pintor.completo = True
            _juego["tamano"] = (ancho, alto)

    def mostrar(self):
        self.pintar()
        self.pintor.completo = True

    def pintar(self):
        self.pintor.pintar(self.lienzo, self.real_tamano[0], self.real_tamano[1])

    def leer(self, raton_mod):
        fuente = raton_mod._raton["fuente"]
        raton_mod._raton["fuente"] = self.fuente_previa
        _juego["teclas"] = None
        try:
            return _entorno.leer()
        finally:
            raton_mod._raton["fuente"] = fuente

    def fuente_raton(self, espera):
        if not espera:
            return None
        from . import raton
        self.mostrar()
        fuente = raton._raton["fuente"]
        raton._raton["fuente"] = self.fuente_previa
        try:
            return raton._leer_evento(espera=True)
        finally:
            raton._raton["fuente"] = fuente

    def ahora_juego(self):
        return self.fotograma / float(self.velocidad)


def jugar(actualizar, velocidad=20, ancho=None, alto=None, fondo=None, salir_con="esc", raton=False):
    """Hace funcionar un juego: llama a tu función muchas veces por segundo.

        def actualizar(tecla):
            ...mueve cosas según la tecla y dibuja cómo está todo...

        pantalla.jugar(actualizar)

    - tecla: la tecla que se ha pulsado en este momento ("izquierda", "espacio", "a"...)
      o None si no se ha pulsado ninguna. Para saber si una tecla se MANTIENE apretada
      (para moverse suave) usa pantalla.pulsada("izquierda").
    - Cada vez la pantalla empieza vacía: dibuja todo lo que se tenga que ver con las
      funciones de siempre. Los Sprite vivos se dibujan solos, encima de todo (los de
      capa negativa, debajo).
    - Si tu función devuelve algo (return "ganado", return puntos...), el juego acaba
      y jugar() te lo devuelve. Con Esc acaba y devuelve None.
    - velocidad: cuántas veces por segundo (20 va bien; 30 es más suave).
    - ancho, alto: tamaño del juego (sin ellos, el de la terminal).
    - fondo: color de fondo de todo el juego, por ejemplo "azul".
    - salir_con: la tecla que acaba el juego ("esc"); None para que ninguna lo acabe.
    - raton: True para poder usar leer_raton() y posicion_raton() dentro del juego.

    Dentro del juego también valen pausa(), mensaje(), menu() o pedir(): enseñan lo
    dibujado y esperan, como siempre.
    """
    from . import raton as raton_mod
    from . import teclado

    if _partida["actual"] is not None:
        raise RuntimeError("jugar: ya hay un juego en marcha. No llames a jugar() desde dentro "
                           "de tu función actualizar.")
    if not callable(actualizar):
        raise TypeError("jugar: dame el nombre de tu función, sin paréntesis: "
                        "pantalla.jugar(actualizar). Me has dado %r" % (actualizar,))
    if isinstance(velocidad, bool) or not isinstance(velocidad, (int, float)) or velocidad <= 0:
        raise ValueError("jugar: velocidad es cuántas veces por segundo se llama a tu función "
                         "(un número mayor que 0, por ejemplo 20). Me has dado %r" % (velocidad,))
    for nombre, valor in (("ancho", ancho), ("alto", alto)):
        if valor is not None and (isinstance(valor, bool) or not isinstance(valor, int) or valor < 1):
            raise ValueError("jugar: '%s' tiene que ser un número entero mayor que 0. Me has dado %r"
                             % (nombre, valor))
    codigo_fondo = codigo_color(fondo, fondo=True) if fondo is not None else None
    con_tecla = _acepta_tecla(actualizar)
    real = sys.stdout
    if not _entorno.es_terminal(real):
        raise RuntimeError(
            "jugar() necesita una terminal de verdad (cmd, PowerShell, Windows Terminal, la "
            "terminal de VS Code o 'Ejecutar en terminal' de Thonny). En IDLE no se puede jugar.")

    raton_antes = raton_mod._raton["activo"]
    cursor_antes = _estado["cursor_oculto"]
    aparte_antes = _estado["pantalla_aparte"]
    teclas_antes = teclado._modo["original"] is not None
    fuente_antes = raton_mod._raton["fuente"]
    partida = None
    try:
        partida = _Partida(velocidad, ancho, alto, codigo_fondo, salir_con, real)
        partida.fuente_previa = fuente_antes
        if raton:
            raton_mod.activar_raton(hover=True)
        teclado._activar_modo_teclas()
        partida._escribir_real(("" if aparte_antes else CSI + "?1049h") + CSI + "?25l")
        _estado["cursor_oculto"] = True
        _partida["actual"] = partida
        _relojes.clear()
        _juego["mostrar"] = partida.mostrar
        _juego["pintar"] = partida.pintar
        raton_mod._raton["fuente"] = partida.fuente_raton
        sys.stdout = _Captura(partida, real)
        periodo = 1.0 / velocidad
        siguiente = _entorno.ahora()
        while True:
            partida._medir()
            eventos = partida.leer(raton_mod)
            teclas = [e["tecla"] for e in eventos if e.get("tipo") == "tecla" and e.get("tecla")]
            ahora = _entorno.ahora()
            for t in teclas:
                partida.vistas[_nombre_tecla(t)] = ahora
            if partida.salir_con and any(_nombre_tecla(t) == partida.salir_con for t in teclas):
                return None
            raton_mod._raton["clics"][:] = [e for e in eventos if e.get("tipo") == "clic" or (
                e.get("tipo") == "movimiento" and raton_mod._es_arrastre(e))][:20]
            tecla = teclado.Tecla(teclas[0]) if teclas else None
            _juego["teclas"] = teclas[1:]

            partida.lienzo.vaciar(_estilo_de_ansi(_estado["estilo"]))
            try:
                resultado = actualizar(tecla) if con_tecla else actualizar()
            except UnboundLocalError as error:
                explicado = _t._explicar_global(error, "jugar")
                raise explicado from error
            _pintar_sprites(partida.lienzo)
            partida.pintar()
            if _vale(resultado):
                return resultado
            partida.fotograma += 1

            siguiente += periodo
            falta = siguiente - _entorno.ahora()
            if falta > 0:
                _entorno.dormir(falta)
            elif falta < -3 * periodo:
                siguiente = _entorno.ahora()
    except KeyboardInterrupt:
        return None
    finally:
        if isinstance(sys.stdout, _Captura):
            sys.stdout = real
        _juego["mostrar"] = None
        _juego["pintar"] = None
        _juego["teclas"] = None
        _juego["tamano"] = None
        raton_mod._raton["fuente"] = fuente_antes
        del raton_mod._raton["clics"][:]
        _partida["actual"] = None
        del _sprites[:]
        _relojes.clear()
        salida = RESET
        if not cursor_antes:
            salida += CSI + "?25h"
        _estado["cursor_oculto"] = cursor_antes
        if not aparte_antes:
            salida += CSI + "?1049l"
        try:
            real.write(salida)
            real.flush()
        except Exception:
            pass
        if not raton_antes and raton_mod._raton["activo"]:
            raton_mod.desactivar_raton()
        if not teclas_antes:
            teclado._desactivar_modo_teclas()


def pulsada(tecla):
    """Dice si una tecla está apretada AHORA (True o False). Para moverse suave en juegos.

        def actualizar(tecla):
            if pantalla.pulsada("izquierda"):
                nave.mover(-1, 0)

    Nombres: "izquierda", "derecha", "arriba", "abajo", "espacio", "enter", letras ("a")...
    En Windows es exacto. En Linux y Mac la terminal no avisa de cuándo se suelta una
    tecla: cuenta como apretada si ha llegado hace muy poco (al empezar a mantenerla hay
    un saltito, el mismo que ves al dejar una letra pulsada en un editor).
    """
    nombre = _nombre_tecla(tecla)
    partida = _partida["actual"]
    abajo = _entorno.tecla_abajo(nombre)
    if partida is None:
        return bool(abajo)
    visto = partida.vistas.get(nombre)
    if abajo is not None:
        return abajo or (visto is not None and _entorno.ahora() - visto < 1.0 / partida.velocidad)
    if visto is None:
        return False
    return _entorno.ahora() - visto < max(0.16, 2.5 / partida.velocidad)


def cada(segundos, clave=None):
    """Devuelve True una vez cada tantos segundos (y False el resto de veces).

        def actualizar(tecla):
            if pantalla.cada(0.5):
                mover_marcianos()
            if pantalla.cada(2):
                disparar()

    Cada sitio del programa donde escribes cada() lleva su propia cuenta. Si lo usas
    dentro de un for (una cuenta por cada marciano), dale una clave: cada(1, marciano).
    Dentro de jugar() cuenta el tiempo del juego; fuera, el del reloj.
    """
    if isinstance(segundos, bool) or not isinstance(segundos, (int, float)) or segundos <= 0:
        raise ValueError("cada: dime cada cuántos segundos, con un número mayor que 0, por "
                         "ejemplo cada(0.5). Me has dado %r" % (segundos,))
    if clave is None:
        llamada = sys._getframe(1)
        clave = ("sitio", llamada.f_code.co_filename, llamada.f_lineno)
    else:
        try:
            hash(clave)
            clave = ("clave", clave)
        except TypeError:
            clave = ("clave", id(clave))
    partida = _partida["actual"]
    ahora = partida.ahora_juego() if partida is not None else time.monotonic()
    ultimo = _relojes.get(clave)
    if ultimo is None:
        _relojes[clave] = ahora
        return False
    if ahora - ultimo >= segundos - 1e-9:
        siguiente = ultimo + segundos
        _relojes[clave] = siguiente if ahora - siguiente < segundos else ahora
        return True
    return False


def fotograma():
    """Cuántas veces se ha llamado ya a tu función en este juego (0, 1, 2...).

        if pantalla.fotograma() % 10 == 0:   # una de cada 10 veces
            ...
    """
    partida = _partida["actual"]
    return partida.fotograma if partida is not None else 0


def sprites():
    """La lista de Sprite vivos (los que se dibujan solos en jugar())."""
    return [s for s in _sprites if s.vivo]


def _filas(valor, que):
    if isinstance(valor, str):
        if valor.startswith("\n"):
            valor = valor[1:]
        if valor.endswith("\n"):
            valor = valor[:-1]
        return valor.split("\n")
    if isinstance(valor, (list, tuple)) and all(isinstance(f, str) for f in valor):
        return list(valor)
    raise TypeError("Sprite: '%s' tiene que ser un texto (puede tener varias líneas) o una "
                    "lista de textos. Me has dado %r" % (que, valor))


def _codigo_de_color(codigo, por_defecto, que):
    if codigo in (" ", "."):
        return por_defecto
    if codigo not in CODIGOS_COLOR:
        raise ValueError("Sprite: en '%s' hay un código de color que no conozco: %r. Usa uno de "
                         "estos: %s (o un espacio o un punto para el color normal)."
                         % (que, codigo, " ".join(CODIGOS_COLOR)))
    return CODIGOS_COLOR[codigo]


@functools.lru_cache(maxsize=512)
def _estilo_colores(color, fondo):
    from .colores import estilo
    return _estilo_de_ansi(estilo(color, fondo))


def _redondo(v):
    return int(math.floor(v + 0.5))


class Sprite(object):
    """Un dibujo que se mueve: la nave, un marciano, una bala, una pelota...

        nave = pantalla.Sprite("/^\\\\", 38, 22, color="verde")
        marciano = pantalla.Sprite(fotogramas=["/oo\\\\", "\\\\oo/"], x=10, y=3, color="cian")

        nave.mover(1, 0)            # un paso a la derecha
        nave.x = 40                 # o ponerla donde quieras
        if bala.choca(marciano):    # ¿se tocan? (letra a letra, los espacios no cuentan)
            marciano.eliminar()
        if bala.fuera():            # ¿se ha salido de la pantalla?
            bala.eliminar()

    Dentro de jugar() los Sprite vivos se dibujan solos en cada fotograma.
    Fuera de un juego, dibújalo con sprite.dibujar().

    - dibujo: un texto (con varias líneas si quieres) o una lista de textos.
    - fotogramas: varios dibujos para animarlo; cambia de uno a otro cada 'cada' fotogramas.
    - color, fondo: colores de todo el dibujo.
    - colores, fondos: un color por letra, con las letras de arte() (r rojo, v verde...).
    - transparente: True (lo normal) para que los espacios dejen ver lo de detrás.
    - x, y pueden tener decimales (x = x + 0.5 lo mueve a media velocidad).
    - Le puedes apuntar lo que quieras (pelota.dx = 1, marciano.vidas = 3) y usarlo
      dentro de tu función sin tener que poner global.
    - capa: qué va encima cuando dos sprites se pisan (el de capa más alta). Con capa
      negativa es de fondo (estrellas, hierba...): queda detrás de lo que dibujes tú.
    """

    def __init__(self, dibujo=None, x=1, y=1, color=None, fondo=None, colores=None, fondos=None,
                 fotogramas=None, cada=5, transparente=True, capa=0):
        if fotogramas is not None:
            if isinstance(fotogramas, str) or not fotogramas:
                raise TypeError("Sprite: 'fotogramas' es una lista de dibujos, por ejemplo "
                                "fotogramas=[\"o\", \"O\"]")
            self._fotogramas = [_filas(f, "fotogramas") for f in fotogramas]
        elif dibujo is None:
            raise TypeError("Sprite: necesito un dibujo, por ejemplo pantalla.Sprite(\"@\", 10, 5)")
        else:
            self._fotogramas = [_filas(dibujo, "dibujo")]
        for nombre, v in (("x", x), ("y", y)):
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise TypeError("Sprite: '%s' tiene que ser un número. Me has dado %r" % (nombre, v))
        if isinstance(cada, bool) or not isinstance(cada, int) or cada < 1:
            raise ValueError("Sprite: 'cada' son fotogramas (un entero mayor que 0). Me has dado %r"
                             % (cada,))
        if isinstance(capa, bool) or not isinstance(capa, (int, float)):
            raise TypeError("Sprite: 'capa' tiene que ser un número (0 lo normal, más alto = más "
                            "encima, negativo = de fondo). Me has dado %r" % (capa,))
        self.capa = capa
        self.x = x
        self.y = y
        self.color = color
        self.fondo = fondo
        self.colores = None if colores is None else _filas(colores, "colores")
        self.fondos = None if fondos is None else _filas(fondos, "fondos")
        self.cada = cada
        self.transparente = transparente
        self.visible = True
        self.vivo = True
        self._pasos = 0
        self._cache = {}
        self._celdas(0)
        _sprites.append(self)

    @property
    def dibujo(self):
        """El dibujo que se ve ahora. Puedes cambiarlo: nave.dibujo = "*" (una explosión)."""
        return "\n".join(self._fotogramas[self._indice()])

    @dibujo.setter
    def dibujo(self, valor):
        self._fotogramas = [_filas(valor, "dibujo")]
        self._cache = {}

    @property
    def fotogramas(self):
        return ["\n".join(f) for f in self._fotogramas]

    @fotogramas.setter
    def fotogramas(self, valor):
        self._fotogramas = [_filas(f, "fotogramas") for f in valor]
        self._cache = {}

    @property
    def ancho(self):
        return max(len(l) for l in self._fotogramas[self._indice()]) if self._fotogramas else 0

    @property
    def alto(self):
        return len(self._fotogramas[self._indice()])

    def _indice(self):
        return (self._pasos // self.cada) % len(self._fotogramas)

    def _celdas(self, indice=None):
        if indice is None:
            indice = self._indice()
        clave = (indice, self.color, self.fondo, self.transparente,
                 tuple(self.colores or ()), tuple(self.fondos or ()))
        celdas = self._cache.get(clave)
        if celdas is None:
            celdas = []
            cols = self.colores or []
            fons = self.fondos or []
            for dy, linea in enumerate(self._fotogramas[indice]):
                fc = cols[dy] if dy < len(cols) else ""
                ff = fons[dy] if dy < len(fons) else ""
                dx = 0
                for i, c in enumerate(linea):
                    cc = fc[i] if i < len(fc) else " "
                    cf = ff[i] if i < len(ff) else " "
                    ancho = 1 if c < "̀" else (_ancho_letra(c) or 1)
                    if not (self.transparente and c == " " and cf in (" ", ".")):
                        estilo = _estilo_colores(_codigo_de_color(cc, self.color, "colores"),
                                                 _codigo_de_color(cf, self.fondo, "fondos"))
                        celdas.append((dx, dy, c, estilo, ancho))
                    dx += ancho
            self._cache = {clave: celdas}
        return celdas

    def _ocupadas(self):
        x0, y0 = _redondo(self.x), _redondo(self.y)
        sitios = set()
        for dx, dy, _, _, ancho in self._celdas():
            sitios.add((x0 + dx, y0 + dy))
            if ancho == 2:
                sitios.add((x0 + dx + 1, y0 + dy))
        return sitios

    def _caja(self):
        x0, y0 = _redondo(self.x), _redondo(self.y)
        return x0, y0, x0 + self.ancho - 1, y0 + self.alto - 1

    def _pintar_en(self, lienzo, solo_huecos=False):
        x0, y0 = _redondo(self.x), _redondo(self.y)
        for dx, dy, c, estilo, ancho in self._celdas():
            x, y = x0 + dx, y0 + dy
            if solo_huecos and not all(lienzo.hueco(x + i, y) for i in range(ancho)):
                continue
            lienzo.poner(x, y, c, estilo, ancho)

    def mover(self, dx=0, dy=0):
        """Mueve el sprite: mover(1, 0) un paso a la derecha, mover(0, -1) uno hacia arriba."""
        self.x += dx
        self.y += dy
        return self

    def choca(self, otro):
        """¿Toca a otro sprite? Devuelve el sprite con el que choca (o None).

            if bala.choca(marciano): ...
            tocado = bala.choca(marcianos)     # con una lista: dice cuál
            if nave.choca((x, y)): ...         # o con una posición
        """
        if not (self.vivo and self.visible):
            return None
        if isinstance(otro, tuple) and len(otro) == 2 and \
                all(isinstance(v, (int, float)) for v in otro):
            return (_redondo(otro[0]), _redondo(otro[1])) in self._ocupadas()
        if isinstance(otro, Sprite):
            otros = [otro]
        else:
            try:
                otros = list(otro)
            except TypeError:
                raise TypeError("choca: dame otro Sprite, una lista de Sprite o una posición (x, y). "
                                "Me has dado %r" % (otro,))
        mia = self._caja()
        mias = None
        for o in otros:
            if not isinstance(o, Sprite):
                raise TypeError("choca: en la lista hay algo que no es un Sprite: %r" % (o,))
            if o is self or not (o.vivo and o.visible):
                continue
            suya = o._caja()
            if suya[0] > mia[2] or suya[2] < mia[0] or suya[1] > mia[3] or suya[3] < mia[1]:
                continue
            if mias is None:
                mias = self._ocupadas()
            if mias & o._ocupadas():
                return o
        return None

    def fuera(self):
        """True si el sprite se ha salido entero de la pantalla (del juego)."""
        ancho_p, alto_p = _t.tamano()
        x1, y1, x2, y2 = self._caja()
        return x2 < 1 or y2 < 1 or x1 > ancho_p or y1 > alto_p

    def eliminar(self):
        """Lo quita del juego: ya no se dibuja ni choca."""
        self.vivo = False
        if self in _sprites:
            _sprites.remove(self)

    borrar = eliminar

    def dibujar(self):
        """Lo dibuja ahora (fuera de jugar(); dentro se dibuja solo)."""
        partida = _partida["actual"]
        if partida is not None:
            self._pintar_en(partida.lienzo)
            return
        ancho_p, alto_p = _t.tamano()
        x0, y0 = _redondo(self.x), _redondo(self.y)
        trozos = []
        codigos = {}
        for dx, dy, c, estilo, ancho in self._celdas():
            x, y = x0 + dx, y0 + dy
            if 1 <= x and x + ancho - 1 <= ancho_p and 1 <= y <= alto_p:
                if estilo not in codigos:
                    codigos[estilo] = _Pintor(None)._codigo(estilo)
                trozos.append("%s%d;%dH%s%s" % (CSI, y, x, codigos[estilo], c))
        self._pasos += 1
        if trozos:
            _t._salida("".join(trozos) + _t._fin_de_estilo())

    def __repr__(self):
        return "Sprite(%r, x=%r, y=%r%s)" % (self.dibujo, self.x, self.y,
                                             "" if self.vivo else ", eliminado")
