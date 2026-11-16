"""
Genera la guía de pantalla para inteligencias artificiales:

    docs/pantalla-ia.md      todo en un Markdown largo (para pegarlo en un chat)
    docs/pantalla-ia.json    lo mismo, ordenado para programas y agentes
    src/pantalla/ia.md       la misma guía dentro del paquete (python -m pantalla ia)

Se ejecuta desde la carpeta del proyecto:

    python scripts/guia_ia.py

Saca las firmas y las explicaciones de las funciones de verdad, así que siempre
está al día con el código. Vuelve a ejecutarlo antes de sacar una versión nueva.
"""

import inspect
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))
os.environ.setdefault("PANTALLA_NO_ABRIR", "1")
os.environ.setdefault("PANTALLA_SIN_AVISOS", "1")

import pantalla  # noqa: E402
from pantalla import disenos  # noqa: E402

VERSION = pantalla.__version__
WEB = "https://phernandez102.github.io/pantalla/"
REPO = "https://github.com/phernandez102/pantalla"
PYPI = "https://pypi.org/project/pantalla/"


def leer(*partes):
    with open(os.path.join(RAIZ, *partes), encoding="utf-8") as f:
        return f.read()


def firma(nombre, objeto):
    try:
        texto = str(inspect.signature(objeto))
        return nombre + texto.replace("(self, ", "(").replace("(self)", "()")
    except (TypeError, ValueError):
        return nombre + "(...)"


def doc(objeto):
    return inspect.getdoc(objeto) or ""


def miembros(clase):
    """Métodos y propiedades públicas de una clase, en el orden en que están escritos."""
    salida = []
    for nombre, valor in vars(clase).items():
        if nombre.startswith("_") and nombre not in ("__init__",):
            continue
        if isinstance(valor, property):
            salida.append({"nombre": nombre, "tipo": "propiedad", "firma": nombre, "doc": doc(valor)})
        elif isinstance(valor, (staticmethod, classmethod)):
            f = valor.__func__
            salida.append({"nombre": nombre, "tipo": "método", "firma": firma(nombre, f), "doc": doc(f)})
        elif inspect.isfunction(valor):
            if nombre == "__init__":
                continue
            salida.append({"nombre": nombre, "tipo": "método", "firma": firma(nombre, valor), "doc": doc(valor)})
    return salida


def datos_api():
    grupos = []
    vistas = set()
    for titulo, nombres in pantalla._GRUPOS:
        cosas = []
        for nombre in nombres:
            obj = getattr(pantalla, nombre)
            vistas.add(nombre)
            cosas.append(ficha(nombre, obj))
        grupos.append({"grupo": titulo, "funciones": cosas})
    otros = []
    for nombre in pantalla.__all__:
        if nombre in vistas or nombre in ("ESTILOS", "CODIGOS_COLOR"):
            continue
        otros.append(ficha(nombre, getattr(pantalla, nombre)))
    if otros:
        grupos.append({"grupo": "Otras clases y ayuda", "funciones": otros})
    return grupos


def ficha(nombre, obj):
    clase = inspect.isclass(obj)
    real = getattr(obj, "__name__", nombre)
    f = {
        "nombre": nombre,
        "tipo": "clase" if clase else "función",
        "firma": "pantalla." + firma(nombre, obj),
        "modulo": getattr(obj, "__module__", "pantalla"),
        "doc": doc(obj),
    }
    if real != nombre:
        f["alias_de"] = real
    if clase:
        f["miembros"] = miembros(obj)
    return f


def ejemplos():
    carpeta = os.path.join(RAIZ, "ejemplos")
    salida = []
    for nombre in sorted(os.listdir(carpeta)):
        if nombre.endswith(".py"):
            salida.append({"archivo": "ejemplos/" + nombre, "codigo": leer("ejemplos", nombre)})
    return salida


# ---------------------------------------------------------------------------
# Lo que no se puede sacar del código: cómo pensar con pantalla
# ---------------------------------------------------------------------------

INSTRUCCIONES_IA = """\
Eres un experto en la librería de Python **pantalla** (versión {v}). Este documento es
tu fuente de verdad: si algo de aquí contradice lo que creías saber, manda este documento.
pantalla NO es curses, ni rich, ni colorama, ni blessed: no mezcles sus APIs.

Cuando ayudes a alguien con pantalla:

1. Escribe siempre `import pantalla` y llama a todo como `pantalla.algo(...)`. No uses
   `from pantalla import *` salvo que la persona lo pida.
2. Usa solo funciones y parámetros que aparezcan en la **Referencia completa de la API**
   de este documento, con sus nombres exactos (en español y sin tildes:
   `tamano`, `diseno`, `pedir_contrasena`; las versiones con tilde también funcionan).
   Si una función no existe, dilo y propón la que sí existe; no te inventes nada.
3. Las coordenadas empiezan en **1**: `(1, 1)` es la esquina de arriba a la izquierda,
   `x` es la columna y `y` la fila. En casi todas las funciones el orden es
   `(texto, x, y)` o `(x, y, ...)`: mira la firma exacta antes de escribirla.
4. pantalla está pensada para **aprender a programar**: el público suele ser alumnado de
   ESO, Bachillerato o FP y su profesorado. Escribe código sencillo, en español, con
   nombres de variables en español, sin clases ni trucos si no hacen falta, y explica
   en español claro. Prefiere `pantalla.jugar()` a un `while True` para juegos.
5. Responde en el idioma de la persona (normalmente español).
"""

MODELO_MENTAL = """\
## Modelo mental

- **La terminal es una cuadrícula de letras.** `x` = columna (crece hacia la derecha),
  `y` = fila (crece hacia abajo). Ambas empiezan en 1. `pantalla.ancho()` y
  `pantalla.alto()` dan el tamaño; `pantalla.centro()` devuelve `(x, y)` del centro.
  Si pasas un número con decimales (por ejemplo `ancho() / 2`) se redondea solo.
- **Funciona con códigos ANSI** (secuencias que empiezan por `\\x1b`) y lee teclas con
  `msvcrt` (Windows) o `termios` (Linux/Mac). No tiene dependencias: solo Python 3.8+.
- **Se mezcla con `print()` e `input()`**. `pantalla.gotoxy(x, y)` mueve el cursor y lo
  siguiente que imprimas sale ahí.
- **Dos formas de programar algo animado:**
  1. *Modo juego* (recomendado): `pantalla.jugar(actualizar)` llama a tu función
     `actualizar(tecla)` muchas veces por segundo (20 por defecto, `velocidad=`). En cada
     llamada dibujas **un fotograma**; la pantalla se borra sola antes y se pinta de golpe
     después, sin parpadeo. Devolver cualquier cosa distinta de `None` acaba el juego y
     `jugar()` devuelve ese valor. Esc también sale. Dentro: `pulsada("izquierda")`
     (tecla mantenida), `cada(1)` (True una vez por segundo), `fotograma()`, `Sprite`.
  2. *A mano*: `pantalla.iniciar()` (pantalla aparte, sin cursor ni eco), un bucle con
     `tecla_pulsada()` (no espera, devuelve `None` si no hay tecla) y `pausa()`, y al
     final `pantalla.terminar()` (deja la terminal como estaba). Usa `try/finally` para
     llamar siempre a `terminar()`.
- **Esperar teclas:** `pantalla.tecla()` espera una tecla sin Enter y devuelve su nombre.
  Nombres especiales: `"arriba"`, `"abajo"`, `"izquierda"`, `"derecha"`, `"enter"`,
  `"espacio"`, `"esc"`, `"tab"`, `"borrar"`, `"suprimir"`, `"f1"`... Las letras salen tal
  cual. Al comparar no importan mayúsculas ni sinónimos: `t == "Intro"`, `t == "ENTER"` y
  `t == "enter"` valen igual, y `t == " "` es el espacio.
- **Componentes interactivos que devuelven valores:** `menu()` devuelve la opción elegida
  (el texto, o la clave si le das un diccionario) o `None` si se pulsa Esc;
  `elegir_varios()` devuelve una lista; `formulario()` un diccionario; `confirmar()` un
  bool; `pedir_numero()` un número validado; `pedir_matriz()`, `pedir_vector()`,
  `pedir_fraccion()` objetos matemáticos.
- **Las funciones de mates** (matrices, vectores, rectas, planos, polinomios, fracciones,
  estadística, bases) trabajan con **fracciones exactas** y casi todas pueden enseñar los
  **pasos** como en el cuaderno (`pasos=True` o similar: mira cada firma). Devuelven
  objetos que se imprimen bonitos con `print()`.
- **Ratón:** `activar_raton()`, después `esperar_clic()` / `leer_raton()`; `boton()`,
  `botones()` y `zona()` crean zonas clicables; `bucle()` es un bucle de eventos con
  botones. En `jugar(..., raton=True)` se usa `leer_raton()` dentro de `actualizar`.
- **Errores en español y con pistas.** Si escribes mal un nombre
  (`pantalla.escribe`), el `AttributeError` sugiere el correcto. Si pasas tipos mal
  (`escribir(5, 3, "hola")`), el `TypeError` explica qué parámetro y cómo arreglarlo.
"""

ENTORNO = """\
## Dónde funciona y variables de entorno

- Terminales: cmd, PowerShell, Windows Terminal, terminal de VS Code, Linux, Mac.
- **IDLE no es una terminal.** En Windows, al ejecutar con F5 desde IDLE, pantalla abre el
  programa en una ventana de cmd y lo ejecuta allí. En Linux/Mac hay que ejecutarlo desde
  la terminal. En Thonny: *Ejecutar → Ejecutar el script actual en terminal*.
- Imágenes (`imagen()`, `ver_modelo()`, visor 3D): con píxeles reales en terminales con
  protocolo kitty o Sixel (Windows Terminal, WezTerm, kitty, Ghostty, iTerm2, foot,
  Konsole, xterm con Sixel); en las demás, con bloques ▀ de colores o braille.

| Variable | Efecto |
|---|---|
| `PANTALLA_NO_ABRIR=1` | No abrir una ventana de cmd al ejecutar desde IDLE en Windows |
| `PANTALLA_IMAGENES=1` / `kitty` / `0` | Forzar imágenes con píxeles, forzar protocolo kitty, o no intentarlo nunca |
| `PANTALLA_SIN_AVISOS=1` | No avisar cuando la salida no es una terminal |

## Línea de comandos

| Orden | Qué hace |
|---|---|
| `pip install pantalla` | Instala la librería |
| `python -m pantalla` | Demostración interactiva de todo (también `pantalla-demo`) |
| `python -m pantalla depurar` | Cruz que se mueve con flechas y dice su `x`, `y` y el `gotoxy` |
| `python -m pantalla ayuda` | Menú de ayuda con todas las funciones |
| `python -m pantalla ia` | Escribe esta misma guía (para pasársela a una IA) |

Desde Python: `pantalla.ayuda()` (menú) y `pantalla.ayuda("caja")` (una función).
"""

ERRORES_TIPICOS = """\
## Errores típicos (y cómo corregirlos)

| Mal | Bien | Por qué |
|---|---|---|
| `pantalla.escribir(5, 3, "hola")` | `pantalla.escribir("hola", 5, 3)` | El texto va primero, luego `x`, `y` |
| `pantalla.gotoxy(0, 0)` | `pantalla.gotoxy(1, 1)` | Las posiciones empiezan en 1 |
| `pantalla.gotoxy(fila, columna)` | `pantalla.gotoxy(columna, fila)` | `x` es la columna, `y` la fila |
| `pantalla.color("rojo")` | `pantalla.poner_color("rojo")` o `color="rojo"` en cada función | No existe `color()` |
| `import curses` / `rich` | `import pantalla` | Son otras librerías |
| `while True:` + `time.sleep` para un juego | `pantalla.jugar(actualizar)` | Sin parpadeo y sin bucle |
| Olvidar `global puntos` dentro de `actualizar` | `global puntos` en la 1.ª línea, o guardar el dato en un `Sprite` (`pelota.dx = 1`) | Las variables se cambian dentro de una función |
| Usar `iniciar()` sin `terminar()` | `try: ... finally: pantalla.terminar()` | Si no, la terminal se queda sin cursor |
| Llamar a `menu()` y no comprobar `None` | `if opcion is None: ...` | Esc devuelve `None` |
| Ejecutar desde IDLE en Linux/Mac | Ejecutar desde la terminal | IDLE no es una terminal |
| `time.sleep(0.5)` | `pantalla.pausa(0.5)` | `pausa` además funciona bien dentro de `jugar()` |
"""

PLANTILLAS = '''\
## Plantillas que funcionan

### Pantalla estática con colores y cajas

```python
import pantalla

pantalla.limpiar()
pantalla.rodear("doble", color="cian", titulo="Mi programa")
pantalla.grande("HOLA", y=3, color="amarillo")
pantalla.caja(5, 10, 30, 5, estilo="redondo", color="verde", titulo="Datos")
pantalla.escribir("Nombre: Ana", 7, 12)
pantalla.esperar()
```

### Menú principal

```python
import pantalla

while True:
    pantalla.limpiar()
    pantalla.cabecera("Mi programa")
    opcion = pantalla.menu(["Jugar", "Opciones", "Salir"], titulo="Menú")
    if opcion is None or opcion == "Salir":
        break
    if opcion == "Jugar":
        pantalla.mensaje("¡A jugar!")
```

### Juego con `jugar()` y `Sprite`

```python
import pantalla

nave = pantalla.Sprite("/^\\\\", 30, 20, color="verde")
puntos = 0

def actualizar(tecla):
    global puntos
    if pantalla.pulsada("izquierda"):
        nave.mover(-1, 0)
    if pantalla.pulsada("derecha"):
        nave.mover(1, 0)
    if pantalla.cada(1):
        puntos = puntos + 1
    pantalla.escribir("Puntos: %d" % puntos, 1, 1, color="amarillo")
    if tecla == "q":
        return puntos

final = pantalla.jugar(actualizar, velocidad=20, ancho=60, alto=22)
print("Has hecho", final, "puntos")
```

### Bucle a mano

```python
import pantalla

pantalla.iniciar()
try:
    x = 1
    while x < pantalla.ancho():
        if pantalla.tecla_pulsada() == "q":
            break
        pantalla.punto(x, 10, " ")
        x = x + 1
        pantalla.punto(x, 10, "►", color="amarillo")
        pantalla.pausa(0.05)
finally:
    pantalla.terminar()
```

### Tarea larga con barra o spinner

```python
import pantalla

with pantalla.spinner("Descargando"):
    hacer_algo_lento()

pantalla.pantalla_de_carga("Preparando el juego", segundos=3)
pantalla.pantalla_de_carga("Cargando", tareas=["Leyendo mapa", cargar_mapa, "Colocando enemigos"])
```

### Mates paso a paso

```python
import pantalla

A = pantalla.matriz([[2, 1], [1, -1]])
print(pantalla.determinante(A))
x, y = pantalla.resolver_sistema([[2, 1], [1, -1]], [5, 1])
pantalla.resolver_sistema([[2, 1, 5], [1, -1, 1]], pasos=True)   # Gauss paso a paso
p = pantalla.polinomio("x^3 - 6x^2 + 11x - 6")
pantalla.factorizar_polinomio(p, pasos=True)
pantalla.grafica(lambda x: x * x - 4, -5, 5)
```
'''


def formato_diseno():
    return """\
## Formato de `pantalla.diseno()` (lo que exporta el constructor web)

El [constructor web]({web}) exporta un JSON que `pantalla.diseno(texto_o_archivo, x=1, y=1, centrado=False)`
dibuja y que devuelve `{{nombre: (x, y)}}` de los elementos con `"nombre"`.

```json
{{
  "pantalla": 1,
  "ancho": 80,
  "alto": 24,
  "elementos": [
    {{"tipo": "rodear", "estilo": "doble", "color": "cian", "titulo": "Mi juego"}},
    {{"tipo": "caja", "x": 3, "y": 3, "ancho": 20, "alto": 5, "estilo": "redondo", "color": "verde", "titulo": "Vidas", "relleno": false}},
    {{"tipo": "texto", "x": 5, "y": 5, "texto": "Hola", "color": "amarillo", "negrita": true, "subrayado": false}},
    {{"tipo": "linea", "x": 1, "y": 10, "largo": 80, "caracter": "─", "color": "gris"}},
    {{"tipo": "linea_vertical", "x": 40, "y": 2, "largo": 20, "caracter": "│"}},
    {{"tipo": "rellenar", "x": 50, "y": 3, "ancho": 10, "alto": 3, "caracter": " ", "fondo": "azul"}},
    {{"tipo": "punto", "x": 60, "y": 12, "caracter": "█", "color": "rojo"}},
    {{"tipo": "grande", "x": 10, "y": 14, "texto": "GO", "fuente": "slant", "caracter": "█", "color": "amarillo"}},
    {{"tipo": "arte", "x": 2, "y": 18, "lineas": ["/\\\\_/\\\\", "( o.o )"], "colores": ["aaaaa", "aRaRa"], "fondos": null, "transparente": true}},
    {{"tipo": "hueco", "x": 70, "y": 2, "nombre": "puntos"}}
  ]
}}
```

Tipos válidos: {tipos}. Todos aceptan `"color"`, `"fondo"` y `"nombre"` (opcional).
""".format(web=WEB, tipos=", ".join("`%s`" % t for t in disenos.TIPOS))


def referencias_rapidas():
    colores = pantalla.lista_colores()
    lineas = ["## Valores válidos", ""]
    lineas.append("**Colores** (para `color=` y `fondo=`; también `\"#ff8800\"` o `(r, g, b)`): " +
                  ", ".join("`%s`" % c for c in colores) + ".")
    lineas.append("")
    lineas.append("**Estilos de texto** (parámetros booleanos en `escribir` y compañía): `negrita`, `tenue`, "
                  "`cursiva`, `subrayado`, `parpadeo`, `tachado`, `invertido`.")
    lineas.append("")
    lineas.append("**Estilos de borde** (`estilo=` en `caja`, `rodear`, `linea`...): " +
                  ", ".join("`%s` (`%s`)" % (k, v) for k, v in pantalla.ESTILOS.items()) +
                  ", o cualquier carácter suelto como `\"=\"` o `\"*\"`.")
    lineas.append("")
    lineas.append("**Códigos de color para `arte(colores=..., fondos=...)`** (una letra por carácter): " +
                  ", ".join("`%s`=%s" % (k, v) for k, v in pantalla.CODIGOS_COLOR.items()) +
                  ". Un espacio o `.` deja el color por defecto.")
    lineas.append("")
    lineas.append("**Fuentes ASCII** (`fuente=` en `grande` y `texto_grande`): " +
                  ", ".join("`%s`" % f for f in pantalla.lista_fuentes()) + ".")
    lineas.append("")
    lineas.append("**Spinners** (`spinner(texto, estilo=...)`): " +
                  ", ".join("`%s`" % s for s in pantalla.lista_spinners()) + ".")
    lineas.append("")
    lineas.append("**Estilos de barra** (`estilo=` en `barra_progreso` y `pantalla_de_carga`): " +
                  ", ".join("`%s`" % b for b in pantalla.lista_barras()) + ".")
    lineas.append("")
    lineas.append("**Temas de `practicar()`**: " + ", ".join("`%s`" % t for t in pantalla.lista_temas()) + ".")
    lineas.append("")
    return "\n".join(lineas)


def nombres_parecidos():
    pares = sorted(pantalla._PARECIDAS.items())
    filas = ["## Nombres que la gente suele escribir y la función de verdad", "",
             "Si alguien pide algo con estos nombres, usa la función de la derecha "
             "(pantalla también lo sugiere en el mensaje de error).", "",
             "| Escriben | Función real |", "|---|---|"]
    for mal, bien in pares:
        filas.append("| `%s` | `pantalla.%s` |" % (mal, bien))
    filas.append("")
    filas.append("Además, cualquier nombre funciona con tildes, ñ o mayúsculas: `pantalla.tamaño()` → "
                 "`tamano`, `pantalla.diseño()` → `diseno`, `pantalla.pedir_contraseña()` → `pedir_contrasena`.")
    filas.append("")
    return "\n".join(filas)


def api_markdown(grupos):
    salida = ["## Referencia completa de la API", "",
              "Todas las funciones y clases públicas de `pantalla %s`, con su firma exacta y su "
              "explicación (sacadas del código fuente)." % VERSION, ""]
    salida.append("### Índice")
    salida.append("")
    for g in grupos:
        salida.append("- **%s**: %s" % (g["grupo"], ", ".join("`%s`" % f["nombre"] for f in g["funciones"])))
    salida.append("")
    for g in grupos:
        salida.append("### %s" % g["grupo"])
        salida.append("")
        for f in g["funciones"]:
            salida.append("#### `%s`" % f["firma"])
            salida.append("")
            if f.get("alias_de"):
                salida.append("*Es otro nombre de `pantalla.%s`.*" % f["alias_de"])
                salida.append("")
            salida.append(f["tipo"].capitalize() + (" · módulo `%s`" % f["modulo"]))
            salida.append("")
            if f["doc"]:
                salida.append(bloque_doc(f["doc"]))
                salida.append("")
            for m in f.get("miembros", []):
                cab = "`.%s`" % m["firma"] if m["tipo"] == "método" else "`.%s` (propiedad)" % m["nombre"]
                texto = m["doc"].split("\n\n")[0].replace("\n", " ") if m["doc"] else ""
                salida.append("- %s%s" % (cab, (": " + texto) if texto else ""))
                resto = m["doc"].split("\n\n", 1)[1] if m["doc"] and "\n\n" in m["doc"] else ""
                if resto:
                    salida.append("")
                    salida.append("  ```")
                    salida.extend("  " + l for l in resto.splitlines())
                    salida.append("  ```")
            if f.get("miembros"):
                salida.append("")
    return "\n".join(salida)


def bloque_doc(texto):
    """Las explicaciones usan sangría de 4 espacios para el código: lo paso a bloques ```python."""
    salida, codigo = [], []

    def soltar():
        if codigo:
            while codigo and not codigo[-1].strip():
                codigo.pop()
            salida.append("```python")
            salida.extend(l[4:] if l.startswith("    ") else l for l in codigo)
            salida.append("```")
            codigo.clear()

    for linea in texto.splitlines():
        if linea.startswith("    ") or (codigo and not linea.strip()):
            codigo.append(linea)
        else:
            soltar()
            salida.append(linea)
    soltar()
    return "\n".join(salida)


def readme_sin_cabecera():
    texto = leer("README.md")
    corte = texto.find("## Instalar")
    texto = texto[corte:] if corte >= 0 else texto
    # cada título baja un nivel (## -> ###), sin tocar los comentarios # de dentro del código
    salida, en_codigo = [], False
    for linea in texto.splitlines():
        if linea.startswith("```"):
            en_codigo = not en_codigo
        elif not en_codigo and linea.startswith("#"):
            linea = "#" + linea
        salida.append(linea)
    return "\n".join(salida)


def construir_markdown(grupos, ejemplos_):
    total = sum(len(g["funciones"]) for g in grupos)
    partes = [
        "# pantalla %s · guía completa para IA" % VERSION,
        "",
        "> Documento para pegar (o adjuntar) en cualquier IA —ChatGPT, Claude, Gemini, Copilot, "
        "Cursor...— para que sepa usar la librería de Python `pantalla` a la perfección. "
        "Generado automáticamente a partir del código fuente de la versión %s." % VERSION,
        "",
        "- Instalar: `pip install pantalla` · Python 3.8+ · sin dependencias · MIT",
        "- PyPI: %s" % PYPI,
        "- Código: %s" % REPO,
        "- Constructor web y documentación visual: %s" % WEB,
        "- %d funciones y clases públicas, %d ejemplos completos." % (total, len(ejemplos_)),
        "",
        "## Instrucciones para la IA",
        "",
        INSTRUCCIONES_IA.format(v=VERSION),
        "## Qué es pantalla",
        "",
        "`pantalla` es \"gotoxy para el siglo XXI\": convierte la terminal en un lienzo para aprender "
        "Python. Con una línea pones texto donde quieras y con colores, dibujas cajas y menús, "
        "escribes títulos con %d fuentes ASCII o conviertes una imagen en arte de caracteres. "
        "Tiene botones que responden al ratón, barras, spinners y pantallas de carga, y un modo "
        "juego sin bucles infinitos ni parpadeos. Para clase de matemáticas trae matrices, vectores, "
        "rectas, geometría en el espacio con visor 3D, polinomios con Ruffini, estadística, "
        "fracciones exactas, sistemas por Gauss, cambios de base y gráficas de funciones, casi todo "
        "con los pasos como en el cuaderno, y `practicar()` para hacer ejercicios autocorregidos. "
        "Todo (funciones, parámetros, mensajes de error) está en español." % len(pantalla.lista_fuentes()),
        "",
        MODELO_MENTAL,
        ENTORNO,
        referencias_rapidas(),
        ERRORES_TIPICOS,
        PLANTILLAS,
        formato_diseno(),
        nombres_parecidos(),
        api_markdown(grupos),
        "",
        "## Manual de uso (README del proyecto)",
        "",
        readme_sin_cabecera(),
        "",
        "## Ejemplos completos",
        "",
        "Programas que vienen en la carpeta `ejemplos/` del repositorio. Todos funcionan tal cual.",
        "",
    ]
    for e in ejemplos_:
        partes.append("### `%s`" % e["archivo"])
        partes.append("")
        partes.append("```python")
        partes.append(e["codigo"].rstrip())
        partes.append("```")
        partes.append("")
    partes.append("---")
    partes.append("")
    partes.append("Fin de la guía de pantalla %s. Si dudas entre dos funciones, consulta su firma en la "
                  "Referencia completa de la API y su ejemplo; si algo no está aquí, pantalla no lo tiene." % VERSION)
    partes.append("")
    return "\n".join(partes)


def construir_json(grupos, ejemplos_):
    return {
        "nombre": "pantalla",
        "version": VERSION,
        "descripcion": "Librería de Python para dibujar en la terminal (gotoxy, colores, cajas, menús, "
                       "fuentes ASCII, ratón, juegos sin bucles) y para mates paso a paso. En español.",
        "instalar": "pip install pantalla",
        "python": ">=3.8",
        "licencia": "MIT",
        "enlaces": {"pypi": PYPI, "codigo": REPO, "web": WEB},
        "instrucciones_para_ia": INSTRUCCIONES_IA.format(v=VERSION),
        "modelo_mental": MODELO_MENTAL,
        "entorno": ENTORNO,
        "errores_tipicos": ERRORES_TIPICOS,
        "plantillas": PLANTILLAS,
        "valores": {
            "colores": pantalla.lista_colores(),
            "colores_extra": "También '#rrggbb' o una tupla (r, g, b).",
            "estilos_texto": ["negrita", "tenue", "cursiva", "subrayado", "parpadeo", "tachado", "invertido"],
            "estilos_borde": pantalla.ESTILOS,
            "codigos_color_arte": pantalla.CODIGOS_COLOR,
            "fuentes": pantalla.lista_fuentes(),
            "spinners": pantalla.lista_spinners(),
            "estilos_barra": pantalla.lista_barras(),
            "temas_practicar": pantalla.lista_temas(),
            "teclas_especiales": ["arriba", "abajo", "izquierda", "derecha", "enter", "espacio", "esc",
                                  "tab", "borrar", "suprimir", "f1", "f2", "f3", "f4", "f5", "f6", "f7",
                                  "f8", "f9", "f10", "f11", "f12"],
            "tipos_diseno": disenos.TIPOS,
        },
        "formato_diseno": formato_diseno(),
        "nombres_parecidos": dict(sorted(pantalla._PARECIDAS.items())),
        "api": grupos,
        "readme": leer("README.md"),
        "ejemplos": ejemplos_,
    }


def escribir_archivo(ruta, texto):
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    print("  %-28s %7.1f KB" % (os.path.relpath(ruta, RAIZ), len(texto.encode("utf-8")) / 1024))


def main():
    grupos = datos_api()
    ejemplos_ = ejemplos()
    md = construir_markdown(grupos, ejemplos_)
    js = json.dumps(construir_json(grupos, ejemplos_), ensure_ascii=False, indent=1)
    print("Guía para IA de pantalla %s:" % VERSION)
    escribir_archivo(os.path.join(RAIZ, "docs", "pantalla-ia.md"), md)
    escribir_archivo(os.path.join(RAIZ, "docs", "pantalla-ia.json"), js + "\n")
    escribir_archivo(os.path.join(RAIZ, "src", "pantalla", "ia.md"), md)


if __name__ == "__main__":
    main()
