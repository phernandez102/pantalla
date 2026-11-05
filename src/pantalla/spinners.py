"""
Spinners: la ruedecita que da vueltas mientras tu programa hace algo (como halo).

    with pantalla.spinner("Descargando..."):
        descargar()                  # al acabar sale "✔ Descargando..."

    s = pantalla.spinner("Cargando", estilo="arco", color="amarillo").empezar()
    ...
    s.texto = "Casi está"
    s.bien("¡Hecho!")                # o s.mal("Ha fallado"), s.aviso(...), s.info(...)
"""

import sys
import threading
import unicodedata

from . import terminal as _t
from .colores import estilo as _estilo_ansi
from .terminal import CSI, ESC, _estado

SPINNERS = {
    "dots": (80, ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]),
    "dots2": (80, ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]),
    "dots3": (80, ["⠋", "⠙", "⠚", "⠞", "⠖", "⠦", "⠴", "⠲", "⠳", "⠓"]),
    "dots4": (80, ["⠄", "⠆", "⠇", "⠋", "⠙", "⠸", "⠰", "⠠", "⠰", "⠸", "⠙", "⠋", "⠇", "⠆"]),
    "dots5": (80, ["⠋", "⠙", "⠚", "⠒", "⠂", "⠂", "⠒", "⠲", "⠴", "⠦", "⠖", "⠒", "⠐", "⠐", "⠒",
                   "⠓", "⠋"]),
    "dots6": (80, ["⠁", "⠉", "⠙", "⠚", "⠒", "⠂", "⠂", "⠒", "⠲", "⠴", "⠤", "⠄", "⠄", "⠤", "⠴",
                   "⠲", "⠒", "⠂", "⠂", "⠒", "⠚", "⠙", "⠉", "⠁"]),
    "dots7": (80, ["⠈", "⠉", "⠋", "⠓", "⠒", "⠐", "⠐", "⠒", "⠖", "⠦", "⠤", "⠠", "⠠", "⠤", "⠦",
                   "⠖", "⠒", "⠐", "⠐", "⠒", "⠓", "⠋", "⠉", "⠈"]),
    "dots8": (80, ["⠁", "⠁", "⠉", "⠙", "⠚", "⠒", "⠂", "⠂", "⠒", "⠲", "⠴", "⠤", "⠄", "⠄", "⠤",
                   "⠠", "⠠", "⠤", "⠦", "⠖", "⠒", "⠐", "⠐", "⠒", "⠓", "⠋", "⠉", "⠈", "⠈"]),
    "dots9": (80, ["⢹", "⢺", "⢼", "⣸", "⣇", "⡧", "⡗", "⡏"]),
    "dots10": (80, ["⢄", "⢂", "⢁", "⡁", "⡈", "⡐", "⡠"]),
    "dots11": (100, ["⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈"]),
    "dots12": (80, ["⢀⠀", "⡀⠀", "⠄⠀", "⢂⠀", "⡂⠀", "⠅⠀", "⢃⠀", "⡃⠀", "⠍⠀", "⢋⠀", "⡋⠀", "⠍⠁",
                    "⢋⠁", "⡋⠁", "⠍⠉", "⠋⠉", "⠋⠉", "⠉⠙", "⠉⠙", "⠉⠩", "⠈⢙", "⠈⡙", "⢈⠩", "⡀⢙",
                    "⠄⡙", "⢂⠩", "⡂⢘", "⠅⡘", "⢃⠨", "⡃⢐", "⠍⡐", "⢋⠠", "⡋⢀", "⠍⡁", "⢋⠁", "⡋⠁",
                    "⠍⠉", "⠋⠉", "⠋⠉", "⠉⠙", "⠉⠙", "⠉⠩", "⠈⢙", "⠈⡙", "⠈⠩", "⠀⢙", "⠀⡙", "⠀⠩",
                    "⠀⢘", "⠀⡘", "⠀⠨", "⠀⢐", "⠀⡐", "⠀⠠", "⠀⢀", "⠀⡀"]),
    "sand": (80, ["⠁", "⠂", "⠄", "⡀", "⡈", "⡐", "⡠", "⣀", "⣁", "⣂", "⣄", "⣌", "⣔", "⣤", "⣥",
                  "⣦", "⣮", "⣶", "⣷", "⣿", "⡿", "⠿", "⢟", "⠟", "⡛", "⠛", "⠫", "⢋", "⠋", "⠍",
                  "⡉", "⠉", "⠑", "⠡", "⢁"]),
    "line": (130, ["-", "\\", "|", "/"]),
    "line2": (100, ["⠂", "-", "–", "—", "–", "-"]),
    "pipe": (100, ["┤", "┘", "┴", "└", "├", "┌", "┬", "┐"]),
    "simpleDots": (400, [".  ", ".. ", "...", "   "]),
    "simpleDotsScrolling": (200, [".  ", ".. ", "...", " ..", "  .", "   "]),
    "star": (70, ["✶", "✸", "✹", "✺", "✹", "✷"]),
    "star2": (80, ["+", "x", "*"]),
    "flip": (70, ["_", "_", "_", "-", "`", "`", "'", "´", "-", "_", "_", "_"]),
    # el original es ☱☲☴ pero en python 3.14 esos ocupan 2 de ancho y se descuadra
    "hamburger": (100, ["⠉", "⠒", "⠤"]),
    "growVertical": (120, ["▁", "▃", "▄", "▅", "▆", "▇", "▆", "▅", "▄", "▃"]),
    "growHorizontal": (120, ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "▊", "▋", "▌", "▍", "▎"]),
    "balloon": (140, [" ", ".", "o", "O", "@", "*", " "]),
    "balloon2": (120, [".", "o", "O", "°", "O", "o", "."]),
    "noise": (100, ["▓", "▒", "░"]),
    "bounce": (120, ["⠁", "⠂", "⠄", "⠂"]),
    "boxBounce": (120, ["▖", "▘", "▝", "▗"]),
    "boxBounce2": (100, ["▌", "▀", "▐", "▄"]),
    "triangle": (50, ["◢", "◣", "◤", "◥"]),
    "arc": (100, ["◜", "◠", "◝", "◞", "◡", "◟"]),
    "circle": (120, ["◡", "⊙", "◠"]),
    "squareCorners": (180, ["◰", "◳", "◲", "◱"]),
    "circleQuarters": (120, ["◴", "◷", "◶", "◵"]),
    "circleHalves": (50, ["◐", "◓", "◑", "◒"]),
    "squish": (100, ["╫", "╪"]),
    "toggle": (250, ["⊶", "⊷"]),
    "toggle2": (80, ["▫", "▪"]),
    "toggle3": (120, ["□", "■"]),
    "toggle4": (100, ["■", "□", "▪", "▫"]),
    "toggle5": (100, ["▮", "▯"]),
    "toggle7": (80, ["⦾", "⦿"]),
    "toggle8": (100, ["◍", "◌"]),
    "toggle9": (100, ["◉", "◎"]),
    "toggle11": (50, ["⧇", "⧆"]),
    "toggle12": (120, ["☗", "☖"]),
    "toggle13": (80, ["=", "*", "-"]),
    "arrow": (100, ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"]),
    "arrow3": (120, ["▹▹▹▹▹", "▸▹▹▹▹", "▹▸▹▹▹", "▹▹▸▹▹", "▹▹▹▸▹", "▹▹▹▹▸"]),
    "bouncingBar": (80, ["[    ]", "[=   ]", "[==  ]", "[=== ]", "[====]", "[ ===]", "[  ==]",
                         "[   =]", "[    ]", "[   =]", "[  ==]", "[ ===]", "[====]", "[=== ]",
                         "[==  ]", "[=   ]"]),
    "bouncingBall": (80, ["( ●    )", "(  ●   )", "(   ●  )", "(    ● )", "(     ●)",
                          "(    ● )", "(   ●  )", "(  ●   )", "( ●    )", "(●     )"]),
    "pong": (80, ["▐⠂       ▌", "▐⠈       ▌", "▐ ⠂      ▌", "▐ ⠠      ▌", "▐  ⡀     ▌",
                  "▐  ⠠     ▌", "▐   ⠂    ▌", "▐   ⠈    ▌", "▐    ⠂   ▌", "▐    ⠠   ▌",
                  "▐     ⡀  ▌", "▐     ⠠  ▌", "▐      ⠂ ▌", "▐      ⠈ ▌", "▐       ⠂▌",
                  "▐       ⠠▌", "▐       ⡀▌", "▐      ⠠ ▌", "▐      ⠂ ▌", "▐     ⠈  ▌",
                  "▐     ⠂  ▌", "▐    ⠠   ▌", "▐    ⡀   ▌", "▐   ⠠    ▌", "▐   ⠂    ▌",
                  "▐  ⠈     ▌", "▐  ⠂     ▌", "▐ ⠠      ▌", "▐ ⡀      ▌", "▐⠠       ▌"]),
    "shark": (120, ["▐|\\____________▌", "▐_|\\___________▌", "▐__|\\__________▌",
                    "▐___|\\_________▌", "▐____|\\________▌", "▐_____|\\_______▌",
                    "▐______|\\______▌", "▐_______|\\_____▌", "▐________|\\____▌",
                    "▐_________|\\___▌", "▐__________|\\__▌", "▐___________|\\_▌",
                    "▐____________|\\▌", "▐____________/|▌", "▐___________/|_▌",
                    "▐__________/|__▌", "▐_________/|___▌", "▐________/|____▌",
                    "▐_______/|_____▌", "▐______/|______▌", "▐_____/|_______▌",
                    "▐____/|________▌", "▐___/|_________▌", "▐__/|__________▌",
                    "▐_/|___________▌", "▐/|____________▌"]),
    "dqpb": (100, ["d", "q", "p", "b"]),
    "aesthetic": (80, ["▰▱▱▱▱▱▱", "▰▰▱▱▱▱▱", "▰▰▰▱▱▱▱", "▰▰▰▰▱▱▱", "▰▰▰▰▰▱▱", "▰▰▰▰▰▰▱",
                       "▰▰▰▰▰▰▰", "▰▱▱▱▱▱▱"]),
    "binary": (80, ["010010", "001100", "100101", "111010", "111101", "010111", "101011",
                    "111000", "110011", "110101"]),
    "point": (125, ["∙∙∙", "●∙∙", "∙●∙", "∙∙●", "∙∙∙"]),
    "layer": (150, ["-", "=", "≡"]),
    "betaWave": (80, ["ρββββββ", "βρβββββ", "ββρββββ", "βββρβββ", "ββββρββ", "βββββρβ",
                      "ββββββρ"]),
}

_ESPANOL = {
    "puntos": "dots", "puntos2": "dots2", "braille": "dots2", "arena": "sand",
    "linea": "line", "tubo": "pipe", "puntitos": "simpleDots", "estrella": "star",
    "crecer": "growVertical", "barra_creciente": "growHorizontal", "globo": "balloon",
    "ruido": "noise", "rebote": "bounce", "triangulo": "triangle", "arco": "arc",
    "circulo": "circle", "cuartos": "circleQuarters", "medio_circulo": "circleHalves",
    "interruptor": "toggle", "flecha": "arrow", "flechas": "arrow3",
    "barra_rebote": "bouncingBar", "pelota": "bouncingBall", "tiburon": "shark",
    "estetico": "aesthetic", "barra": "aesthetic", "binario": "binary", "capas": "layer",
    "onda": "betaWave",
}

_SIMBOLOS = {
    "bien": ("✔", "verde"),
    "mal": ("✖", "rojo"),
    "aviso": ("⚠", "amarillo"),
    "info": ("ℹ", "azul"),
}


def _clave(nombre):
    sin_tildes = unicodedata.normalize("NFD", nombre.lower())
    return "".join(c for c in sin_tildes if c.isalnum() and unicodedata.category(c) != "Mn")


_POR_CLAVE = {_clave(n): n for n in SPINNERS}
_POR_CLAVE.update({_clave(n): v for n, v in _ESPANOL.items()})


def _buscar_estilo(estilo):
    if isinstance(estilo, (list, tuple)):
        fotogramas = [str(f) for f in estilo]
        if not fotogramas:
            raise ValueError("spinner: la lista de fotogramas está vacía")
        return 100, fotogramas
    if isinstance(estilo, str):
        nombre = _POR_CLAVE.get(_clave(estilo))
        if nombre is not None:
            return SPINNERS[nombre]
        import difflib
        parecido = difflib.get_close_matches(_clave(estilo), list(_POR_CLAVE), n=1)
        mensaje = "spinner: no conozco el estilo %r." % estilo
        if parecido:
            mensaje += " ¿Querías decir %r?" % _POR_CLAVE[parecido[0]]
        raise ValueError(mensaje + " Mira todos con pantalla.lista_spinners().")
    raise TypeError("spinner: el estilo es un nombre (\"dots\", \"arco\"...) o una lista de "
                    "fotogramas. Me has dado %r" % (estilo,))


def lista_spinners():
    """Devuelve los nombres de todos los estilos de spinner.

        for nombre in pantalla.lista_spinners():
            print(nombre)

    También valen en español: "puntos", "linea", "arco", "circulo", "estrella",
    "flecha", "pelota", "tiburon", "barra", "binario"...
    """
    return sorted(SPINNERS)


class Spinner(object):
    """Un spinner. Créalo con pantalla.spinner(...); mira su ayuda."""

    def __init__(self, texto="", estilo="dots", color="cian", color_texto=None, x=None, y=None,
                 intervalo=None):
        milis, fotogramas = _buscar_estilo(estilo)
        _estilo_ansi(color)
        _estilo_ansi(color_texto)
        if (x is None) != (y is None):
            raise TypeError("spinner: dame x e y juntos (o ninguno, para que salga donde está el cursor)")
        if x is not None:
            x, y = _t._posicion(x, y, "spinner")
        self.texto = str(texto)
        self.fotogramas = fotogramas
        self.intervalo = (intervalo if intervalo is not None else milis / 1000.0)
        self.color = color
        self.color_texto = color_texto
        self.x = x
        self.y = y
        self._hilo = None
        self._parar = threading.Event()
        self._paso = 0
        self._largo = 0
        self._cursor_antes = False
        self._animado = False

    def empezar(self):
        """Empieza a girar (en segundo plano: tu programa sigue). Devuelve el spinner."""
        if self._hilo is not None:
            return self
        self._animado = _t._es_terminal(sys.stdout)
        if not self._animado:
            _t._salida(self.texto + "...\n")
            self._hilo = False
            return self
        self._cursor_antes = _estado["cursor_oculto"]
        _t.ocultar_cursor()
        self._parar.clear()
        self._pintar()
        self._hilo = threading.Thread(target=self._girar, name="pantalla-spinner")
        self._hilo.daemon = True
        self._hilo.start()
        return self

    @property
    def girando(self):
        """True mientras el spinner está dando vueltas."""
        return bool(self._hilo)

    def _girar(self):
        while not self._parar.wait(self.intervalo):
            self._paso += 1
            self._pintar()

    def _linea(self, simbolo, color_simbolo):
        texto = self.texto
        if self.x is None:
            ancho = _t.tamano()[0]
            texto = texto[: max(0, ancho - len(simbolo) - 2)]
        trozo = _estilo_ansi(color_simbolo) + simbolo + _t.RESET if color_simbolo else simbolo
        if texto:
            codigo = _estilo_ansi(self.color_texto)
            trozo += " " + (codigo + texto + _t.RESET if codigo else texto)
        return trozo, len(simbolo) + (1 + len(texto) if texto else 0)

    def _escribir(self, trozo, largo, final=False):
        if self.x is None:
            _t._salida("\r" + CSI + "2K" + trozo + _t._estado["estilo"] + ("\n" if final else ""))
        else:
            relleno = " " * max(0, self._largo - largo)
            _t._salida(ESC + "7" + _t._mover(self.x, self.y) + trozo + relleno + ESC + "8")
        self._largo = largo

    def _pintar(self):
        fotograma = self.fotogramas[self._paso % len(self.fotogramas)]
        trozo, largo = self._linea(fotograma, self.color)
        self._escribir(trozo, largo)

    def _detener(self):
        if self._hilo:
            self._parar.set()
            if self._hilo is not threading.current_thread():
                self._hilo.join()
        hilo, self._hilo = self._hilo, None
        return hilo

    def _acabar(self, simbolo, color, texto):
        if texto is not None:
            self.texto = str(texto)
        hilo = self._detener()
        if hilo is None:
            return self
        if not self._animado:
            if simbolo:
                trozo, _ = self._linea(simbolo, None)
                _t._salida(trozo + "\n")
            return self
        if simbolo:
            trozo, largo = self._linea(simbolo, color)
            self._escribir(trozo, largo, final=True)
        elif self.x is None:
            _t._salida("\r" + CSI + "2K")
        else:
            _t._salida(ESC + "7" + _t._mover(self.x, self.y) + " " * self._largo + ESC + "8")
        if not self._cursor_antes:
            _t.mostrar_cursor()
        return self

    def parar(self):
        """Lo para y lo borra (no deja nada escrito)."""
        return self._acabar(None, None, None)

    def bien(self, texto=None):
        """Lo para y deja '✔ texto' en verde."""
        return self._acabar(*(_SIMBOLOS["bien"] + (texto,)))

    def mal(self, texto=None):
        """Lo para y deja '✖ texto' en rojo."""
        return self._acabar(*(_SIMBOLOS["mal"] + (texto,)))

    def aviso(self, texto=None):
        """Lo para y deja '⚠ texto' en amarillo."""
        return self._acabar(*(_SIMBOLOS["aviso"] + (texto,)))

    def info(self, texto=None):
        """Lo para y deja 'ℹ texto' en azul."""
        return self._acabar(*(_SIMBOLOS["info"] + (texto,)))

    def dejar(self, simbolo, texto=None, color=None):
        """Lo para y deja tu símbolo: s.dejar("★", "¡Récord!", color="amarillo")."""
        return self._acabar(str(simbolo), color, texto)

    def __enter__(self):
        return self.empezar()

    def __exit__(self, tipo, valor, traza):
        if tipo is None:
            self.bien()
        else:
            self.mal()
        return False


def spinner(texto="", estilo="dots", color="cian", color_texto=None, x=None, y=None,
            intervalo=None):
    """Un spinner (la ruedecita de "cargando") que gira mientras tu programa trabaja.

    Lo más fácil, con with: gira mientras se hace lo de dentro y al acabar deja
    "✔ texto" (o "✖ texto" si hay un error):

        with pantalla.spinner("Descargando..."):
            descargar()

    O a mano:

        s = pantalla.spinner("Cargando", estilo="arco", color="amarillo")
        s.empezar()
        ...
        s.texto = "Casi está..."      # cambia el texto mientras gira
        s.bien("¡Cargado!")           # también: s.mal(...), s.aviso(...), s.info(...), s.parar()

    - estilo: "dots", "line", "arc", "star", "bouncingBall", "shark"... (o en español:
      "puntos", "linea", "arco", "estrella", "pelota", "tiburon"...). Mira todos con
      pantalla.lista_spinners(). También vale una lista tuya: estilo=["◐", "◓", "◑", "◒"].
    - x, y: para que gire en un sitio fijo de la pantalla (sin ellos, donde esté el cursor).
    - intervalo: segundos entre fotograma y fotograma (cada estilo tiene el suyo).

    Mientras gira, mejor no escribas con print() en la misma línea.
    """
    return Spinner(texto, estilo, color, color_texto, x, y, intervalo)
