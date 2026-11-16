# pantalla 1.1.0 · guía completa para IA

> Documento para pegar (o adjuntar) en cualquier IA —ChatGPT, Claude, Gemini, Copilot, Cursor...— para que sepa usar la librería de Python `pantalla` a la perfección. Generado automáticamente a partir del código fuente de la versión 1.1.0.

- Instalar: `pip install pantalla` · Python 3.8+ · sin dependencias · MIT
- PyPI: https://pypi.org/project/pantalla/
- Código: https://github.com/phernandez102/pantalla
- Constructor web y documentación visual: https://phernandez102.github.io/pantalla/
- 188 funciones y clases públicas, 24 ejemplos completos.

## Instrucciones para la IA

Eres un experto en la librería de Python **pantalla** (versión 1.1.0). Este documento es
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

## Qué es pantalla

`pantalla` es "gotoxy para el siglo XXI": convierte la terminal en un lienzo para aprender Python. Con una línea pones texto donde quieras y con colores, dibujas cajas y menús, escribes títulos con 33 fuentes ASCII o conviertes una imagen en arte de caracteres. Tiene botones que responden al ratón, barras, spinners y pantallas de carga, y un modo juego sin bucles infinitos ni parpadeos. Para clase de matemáticas trae matrices, vectores, rectas, geometría en el espacio con visor 3D, polinomios con Ruffini, estadística, fracciones exactas, sistemas por Gauss, cambios de base y gráficas de funciones, casi todo con los pasos como en el cuaderno, y `practicar()` para hacer ejercicios autocorregidos. Todo (funciones, parámetros, mensajes de error) está en español.

## Modelo mental

- **La terminal es una cuadrícula de letras.** `x` = columna (crece hacia la derecha),
  `y` = fila (crece hacia abajo). Ambas empiezan en 1. `pantalla.ancho()` y
  `pantalla.alto()` dan el tamaño; `pantalla.centro()` devuelve `(x, y)` del centro.
  Si pasas un número con decimales (por ejemplo `ancho() / 2`) se redondea solo.
- **Funciona con códigos ANSI** (secuencias que empiezan por `\x1b`) y lee teclas con
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

## Valores válidos

**Colores** (para `color=` y `fondo=`; también `"#ff8800"` o `(r, g, b)`): `negro`, `rojo`, `verde`, `amarillo`, `azul`, `morado`, `cian`, `gris claro`, `gris`, `rojo claro`, `verde claro`, `amarillo claro`, `azul claro`, `morado claro`, `cian claro`, `blanco`, `naranja`, `marrón`, `rosa`.

**Estilos de texto** (parámetros booleanos en `escribir` y compañía): `negrita`, `tenue`, `cursiva`, `subrayado`, `parpadeo`, `tachado`, `invertido`.

**Estilos de borde** (`estilo=` en `caja`, `rodear`, `linea`...): `simple` (`┌┬┐├┼┤└┴┘─│`), `doble` (`╔╦╗╠╬╣╚╩╝═║`), `grueso` (`┏┳┓┣╋┫┗┻┛━┃`), `redondo` (`╭┬╮├┼┤╰┴╯─│`), `ascii` (`+++++++++-|`), o cualquier carácter suelto como `"="` o `"*"`.

**Códigos de color para `arte(colores=..., fondos=...)`** (una letra por carácter): `n`=negro, `r`=rojo, `v`=verde, `a`=amarillo, `z`=azul, `m`=morado, `c`=cian, `g`=gris, `b`=blanco, `R`=rojo claro, `V`=verde claro, `A`=amarillo claro, `Z`=azul claro, `M`=morado claro, `C`=cian claro, `G`=gris claro, `o`=naranja, `x`=marrón, `p`=rosa. Un espacio o `.` deja el color por defecto.

**Fuentes ASCII** (`fuente=` en `grande` y `texto_grande`): `bloques`, `3-d`, `ansi_regular`, `ansi_shadow`, `banner3`, `big`, `big_money-ne`, `block`, `bloody`, `calvin_s`, `colossal`, `cyberlarge`, `delta_corps_priest_1`, `doom`, `dos_rebel`, `electronic`, `epic`, `graffiti`, `isometric1`, `larry3d`, `mini`, `ogre`, `puffy`, `rectangles`, `script`, `shadow`, `slant`, `small`, `smslant`, `speed`, `standard`, `starwars`, `sub-zero`.

**Spinners** (`spinner(texto, estilo=...)`): `aesthetic`, `arc`, `arrow`, `arrow3`, `balloon`, `balloon2`, `betaWave`, `binary`, `bounce`, `bouncingBall`, `bouncingBar`, `boxBounce`, `boxBounce2`, `circle`, `circleHalves`, `circleQuarters`, `dots`, `dots10`, `dots11`, `dots12`, `dots2`, `dots3`, `dots4`, `dots5`, `dots6`, `dots7`, `dots8`, `dots9`, `dqpb`, `flip`, `growHorizontal`, `growVertical`, `hamburger`, `layer`, `line`, `line2`, `noise`, `pipe`, `point`, `pong`, `sand`, `shark`, `simpleDots`, `simpleDotsScrolling`, `squareCorners`, `squish`, `star`, `star2`, `toggle`, `toggle11`, `toggle12`, `toggle13`, `toggle2`, `toggle3`, `toggle4`, `toggle5`, `toggle7`, `toggle8`, `toggle9`, `triangle`.

**Estilos de barra** (`estilo=` en `barra_progreso` y `pantalla_de_carga`): `bloques`, `suave`, `linea`, `ascii`, `puntos`, `cuadros`, `circulos`, `rombos`, `flechas`, `rayas`.

**Temas de `practicar()`**: `tablas`, `sumas`, `divisiones`, `fracciones`, `potencias`, `raices`, `ecuaciones`, `mcd`, `primos`, `binario`, `porcentajes`, `vectores`.

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

nave = pantalla.Sprite("/^\\", 30, 20, color="verde")
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

## Formato de `pantalla.diseno()` (lo que exporta el constructor web)

El [constructor web](https://phernandez102.github.io/pantalla/) exporta un JSON que `pantalla.diseno(texto_o_archivo, x=1, y=1, centrado=False)`
dibuja y que devuelve `{nombre: (x, y)}` de los elementos con `"nombre"`.

```json
{
  "pantalla": 1,
  "ancho": 80,
  "alto": 24,
  "elementos": [
    {"tipo": "rodear", "estilo": "doble", "color": "cian", "titulo": "Mi juego"},
    {"tipo": "caja", "x": 3, "y": 3, "ancho": 20, "alto": 5, "estilo": "redondo", "color": "verde", "titulo": "Vidas", "relleno": false},
    {"tipo": "texto", "x": 5, "y": 5, "texto": "Hola", "color": "amarillo", "negrita": true, "subrayado": false},
    {"tipo": "linea", "x": 1, "y": 10, "largo": 80, "caracter": "─", "color": "gris"},
    {"tipo": "linea_vertical", "x": 40, "y": 2, "largo": 20, "caracter": "│"},
    {"tipo": "rellenar", "x": 50, "y": 3, "ancho": 10, "alto": 3, "caracter": " ", "fondo": "azul"},
    {"tipo": "punto", "x": 60, "y": 12, "caracter": "█", "color": "rojo"},
    {"tipo": "grande", "x": 10, "y": 14, "texto": "GO", "fuente": "slant", "caracter": "█", "color": "amarillo"},
    {"tipo": "arte", "x": 2, "y": 18, "lineas": ["/\\_/\\", "( o.o )"], "colores": ["aaaaa", "aRaRa"], "fondos": null, "transparente": true},
    {"tipo": "hueco", "x": 70, "y": 2, "nombre": "puntos"}
  ]
}
```

Tipos válidos: `rodear`, `caja`, `texto`, `linea`, `linea_vertical`, `rellenar`, `punto`, `grande`, `hueco`, `arte`. Todos aceptan `"color"`, `"fondo"` y `"nombre"` (opcional).

## Nombres que la gente suele escribir y la función de verdad

Si alguien pide algo con estos nombres, usa la función de la derecha (pantalla también lo sugiere en el mensaje de error).

| Escriben | Función real |
|---|---|
| `3d` | `pantalla.ver_espacio` |
| `alineados` | `pantalla.estan_alineados` |
| `angulo_planos` | `pantalla.angulo` |
| `angulo_vectores` | `pantalla.angulo` |
| `area` | `pantalla.area_triangulo` |
| `average` | `pantalla.media` |
| `barra` | `pantalla.barra_progreso` |
| `barra_grafica` | `pantalla.barras` |
| `barras_progreso` | `pantalla.lista_barras` |
| `base` | `pantalla.cambiar_base` |
| `binario` | `pantalla.a_binario` |
| `borde` | `pantalla.rodear` |
| `borrar` | `pantalla.limpiar` |
| `borrar_pantalla` | `pantalla.limpiar` |
| `bucle_juego` | `pantalla.jugar` |
| `cambio_de_base` | `pantalla.cambiar_base` |
| `carga` | `pantalla.pantalla_de_carga` |
| `cargar` | `pantalla.pantalla_de_carga` |
| `cargar_modelo` | `pantalla.modelo` |
| `casillas` | `pantalla.elegir_varios` |
| `ceros` | `pantalla.raices` |
| `checkbox` | `pantalla.elegir_varios` |
| `clear` | `pantalla.limpiar` |
| `clic` | `pantalla.esperar_clic` |
| `click` | `pantalla.esperar_clic` |
| `cls` | `pantalla.limpiar` |
| `color` | `pantalla.poner_color` |
| `colores` | `pantalla.lista_colores` |
| `coplanarios` | `pantalla.son_coplanarios` |
| `corte` | `pantalla.interseccion_rectas` |
| `corte_planos` | `pantalla.interseccion` |
| `countdown` | `pantalla.cuenta_atras` |
| `cross` | `pantalla.producto_vectorial` |
| `cuadratica` | `pantalla.ecuacion_segundo_grado` |
| `cuadro` | `pantalla.caja` |
| `cuartil` | `pantalla.cuartiles` |
| `cuenta` | `pantalla.calcular` |
| `cursor` | `pantalla.gotoxy` |
| `decimal` | `pantalla.a_decimal` |
| `descomposicion` | `pantalla.descomponer` |
| `desviacion_estandar` | `pantalla.desviacion` |
| `desviacion_tipica` | `pantalla.desviacion` |
| `det` | `pantalla.determinante` |
| `dibujar_3d` | `pantalla.dibujar_espacio` |
| `dibujar_funcion` | `pantalla.grafica` |
| `dibujar_plano` | `pantalla.dibujar_espacio` |
| `dibujar_vector` | `pantalla.dibujar_vectores` |
| `dibujo_3d` | `pantalla.ver_modelo` |
| `discriminante` | `pantalla.ecuacion_segundo_grado` |
| `distancia_punto_plano` | `pantalla.distancia` |
| `distancia_recta` | `pantalla.distancia_punto_recta` |
| `distancia_rectas` | `pantalla.distancia` |
| `dividir` | `pantalla.calcular` |
| `dividir_polinomio` | `pantalla.dividir_polinomios` |
| `division_polinomios` | `pantalla.dividir_polinomios` |
| `dormir` | `pantalla.pausa` |
| `dot` | `pantalla.producto_escalar` |
| `ecuacion_cuadratica` | `pantalla.ecuacion_segundo_grado` |
| `ecuacion_plano` | `pantalla.ecuaciones_plano` |
| `ecuacion_recta` | `pantalla.ecuaciones_recta` |
| `ecuaciones` | `pantalla.resolver_sistema` |
| `espacio` | `pantalla.ver_espacio` |
| `esperar_segundos` | `pantalla.pausa` |
| `estadistica` | `pantalla.estadisticas` |
| `estilos_barra` | `pantalla.lista_barras` |
| `examen` | `pantalla.practicar` |
| `factores` | `pantalla.factorizar` |
| `factorizar_polinomios` | `pantalla.factorizar_polinomio` |
| `flechas` | `pantalla.dibujar_vectores` |
| `formularios` | `pantalla.formulario` |
| `foto` | `pantalla.imagen` |
| `fracciones` | `pantalla.fraccion` |
| `frecuencias` | `pantalla.tabla_frecuencias` |
| `fuentes` | `pantalla.lista_fuentes` |
| `funcion` | `pantalla.grafica` |
| `gauss` | `pantalla.escalonar` |
| `gcd` | `pantalla.mcd` |
| `getch` | `pantalla.tecla` |
| `goto` | `pantalla.gotoxy` |
| `grafico` | `pantalla.grafica` |
| `hex` | `pantalla.a_hexadecimal` |
| `hexadecimal` | `pantalla.a_hexadecimal` |
| `highscore` | `pantalla.guardar_record` |
| `imprimir` | `pantalla.escribir` |
| `independientes` | `pantalla.son_independientes` |
| `input` | `pantalla.pedir` |
| `interseccion` | `pantalla.interseccion_rectas` |
| `interseccion_planos` | `pantalla.interseccion` |
| `inverso` | `pantalla.inversa` |
| `juego` | `pantalla.jugar` |
| `lcm` | `pantalla.mcm` |
| `leer` | `pantalla.pedir` |
| `letras_grandes` | `pantalla.grande` |
| `loading` | `pantalla.pantalla_de_carga` |
| `loading_screen` | `pantalla.pantalla_de_carga` |
| `longitud` | `pantalla.modulo` |
| `magnitud` | `pantalla.modulo` |
| `marcar` | `pantalla.elegir_varios` |
| `marco` | `pantalla.rodear` |
| `maximo_comun_divisor` | `pantalla.mcd` |
| `mean` | `pantalla.media` |
| `media_aritmetica` | `pantalla.media` |
| `mediador` | `pantalla.plano_mediador` |
| `median` | `pantalla.mediana` |
| `minimo_comun_multiplo` | `pantalla.mcm` |
| `mode` | `pantalla.moda` |
| `modulo_vector` | `pantalla.modulo` |
| `mostrar` | `pantalla.escribir` |
| `mostrar_imagen` | `pantalla.imagen` |
| `mover` | `pantalla.gotoxy` |
| `multiplicar` | `pantalla.multiplicar_matrices` |
| `norma` | `pantalla.modulo` |
| `normalizar` | `pantalla.unitario` |
| `operacion` | `pantalla.calcular` |
| `ortogonales` | `pantalla.son_perpendiculares` |
| `pantalla_carga` | `pantalla.pantalla_de_carga` |
| `paralelos` | `pantalla.son_paralelos` |
| `pedir_datos` | `pantalla.formulario` |
| `pedir_varios` | `pantalla.formulario` |
| `perpendicular` | `pantalla.perpendicular_comun` |
| `perpendiculares` | `pantalla.son_perpendiculares` |
| `planos` | `pantalla.plano` |
| `plot` | `pantalla.grafica` |
| `polinomios` | `pantalla.polinomio` |
| `poner` | `pantalla.escribir` |
| `posicion` | `pantalla.gotoxy` |
| `posicion_planos` | `pantalla.posicion` |
| `posicion_relativa` | `pantalla.posicion` |
| `potencia` | `pantalla.potencia_matriz` |
| `preguntar` | `pantalla.pedir` |
| `primo` | `pantalla.es_primo` |
| `primos` | `pantalla.es_primo` |
| `print` | `pantalla.escribir` |
| `producto` | `pantalla.multiplicar_matrices` |
| `producto_cruz` | `pantalla.producto_vectorial` |
| `producto_exterior` | `pantalla.producto_vectorial` |
| `producto_interno` | `pantalla.producto_escalar` |
| `producto_punto` | `pantalla.producto_escalar` |
| `progreso` | `pantalla.barra_progreso` |
| `progress` | `pantalla.barra_progreso` |
| `progressbar` | `pantalla.barra_progreso` |
| `promedio` | `pantalla.media` |
| `proyeccion_ortogonal` | `pantalla.proyeccion` |
| `proyectar` | `pantalla.proyeccion` |
| `punto_medio_segmento` | `pantalla.punto_medio` |
| `puntuacion` | `pantalla.guardar_record` |
| `puntuaciones` | `pantalla.leer_records` |
| `quiz` | `pantalla.practicar` |
| `raiz` | `pantalla.raices` |
| `raton` | `pantalla.activar_raton` |
| `record` | `pantalla.guardar_record` |
| `records` | `pantalla.leer_records` |
| `recta3d` | `pantalla.Recta3D` |
| `rectangulo` | `pantalla.caja` |
| `rectas` | `pantalla.recta` |
| `recuadro` | `pantalla.caja` |
| `reflejar` | `pantalla.simetrico` |
| `reloj` | `pantalla.cronometro` |
| `resolver` | `pantalla.resolver_sistema` |
| `resta` | `pantalla.restar_matrices` |
| `restar` | `pantalla.restar_matrices` |
| `restar_vector` | `pantalla.restar_vectores` |
| `resumen` | `pantalla.estadisticas` |
| `segundo_grado` | `pantalla.ecuacion_segundo_grado` |
| `simetria` | `pantalla.simetrico` |
| `simetrico_punto` | `pantalla.simetrico` |
| `sistema` | `pantalla.resolver_sistema` |
| `sleep` | `pantalla.pausa` |
| `soluciones` | `pantalla.raices` |
| `sparkline` | `pantalla.minigrafica` |
| `std` | `pantalla.desviacion` |
| `suma` | `pantalla.sumar_matrices` |
| `sumar` | `pantalla.sumar_matrices` |
| `sumar_vector` | `pantalla.sumar_vectores` |
| `tabla_de_frecuencias` | `pantalla.tabla_frecuencias` |
| `teclado` | `pantalla.tecla` |
| `temas` | `pantalla.lista_temas` |
| `temporizador` | `pantalla.cronometro` |
| `tetraedro` | `pantalla.volumen_tetraedro` |
| `texto` | `pantalla.escribir` |
| `tiempo` | `pantalla.cronometro` |
| `timer` | `pantalla.cronometro` |
| `titulo` | `pantalla.cabecera` |
| `traspuesta` | `pantalla.transpuesta` |
| `triangulo` | `pantalla.area_triangulo` |
| `vector_unitario` | `pantalla.unitario` |
| `vectores` | `pantalla.vector` |
| `ver_3d` | `pantalla.ver_espacio` |
| `ver_imagen` | `pantalla.imagen` |
| `ver_plano` | `pantalla.ver_espacio` |
| `visor` | `pantalla.ver_espacio` |
| `volumen` | `pantalla.volumen_tetraedro` |
| `wait` | `pantalla.pausa` |

Además, cualquier nombre funciona con tildes, ñ o mayúsculas: `pantalla.tamaño()` → `tamano`, `pantalla.diseño()` → `diseno`, `pantalla.pedir_contraseña()` → `pedir_contrasena`.

## Referencia completa de la API

Todas las funciones y clases públicas de `pantalla 1.1.0`, con su firma exacta y su explicación (sacadas del código fuente).

### Índice

- **Pantalla y cursor**: `limpiar`, `limpiar_linea`, `gotoxy`, `ir_a`, `ancho`, `alto`, `tamano`, `centro`, `ocultar_cursor`, `mostrar_cursor`, `guardar_posicion`, `volver_a_posicion`, `titulo_ventana`, `pitido`, `pausa`, `iniciar`, `terminar`
- **Escribir**: `escribir`, `centrar`, `escribir_derecha`, `escribir_lento`, `grande`, `texto_grande`, `lista_fuentes`, `cabecera`, `pie`
- **Colores**: `colorear`, `poner_color`, `quitar_color`, `lista_colores`
- **Dibujar**: `rodear`, `caja`, `linea`, `linea_vertical`, `rellenar`, `punto`, `arte`
- **Teclado**: `tecla`, `tecla_pulsada`, `vaciar_teclado`, `esperar`, `pedir`, `pedir_numero`, `pedir_contrasena`, `confirmar`
- **Cosas ya hechas**: `menu`, `elegir`, `elegir_varios`, `formulario`, `mensaje`, `tabla`
- **Barras y pantallas de carga**: `barra_progreso`, `lista_barras`, `pantalla_de_carga`, `cargando`, `calculando`, `spinner`, `lista_spinners`
- **Juegos**: `jugar`, `Sprite`, `sprites`, `cada`, `fotograma`, `pulsada`
- **Récords y tiempo**: `guardar_record`, `leer_records`, `mejor_record`, `tabla_records`, `cronometro`, `Cronometro`, `cuenta_atras`
- **Matrices**: `matriz`, `pedir_matriz`, `sumar_matrices`, `restar_matrices`, `multiplicar_matrices`, `transpuesta`, `identidad`, `traza`, `determinante`, `inversa`, `rango`, `potencia_matriz`, `escalonar`, `resolver_sistema`, `clasificar_sistema`
- **Vectores**: `vector`, `Vector`, `pedir_vector`, `vector_entre`, `sumar_vectores`, `restar_vectores`, `multiplicar_vector`, `producto_escalar`, `producto_vectorial`, `producto_mixto`, `modulo`, `unitario`, `distancia`, `angulo`, `proyeccion`, `son_paralelos`, `son_perpendiculares`, `son_independientes`, `dibujar_vectores`
- **Rectas**: `recta`, `Recta`, `ecuaciones_recta`, `posicion_rectas`, `interseccion_rectas`, `distancia_punto_recta`, `angulo_rectas`
- **Espacio (3D)**: `ver_espacio`, `dibujar_espacio`, `plano`, `Plano`, `Recta3D`, `Punto`, `ecuaciones_plano`, `posicion`, `interseccion`, `distancia`, `angulo`, `proyeccion`, `simetrico`, `perpendicular_comun`, `punto_medio`, `plano_mediador`, `area_triangulo`, `volumen_tetraedro`, `estan_alineados`, `son_coplanarios`
- **Polinomios**: `polinomio`, `Polinomio`, `ruffini`, `dividir_polinomios`, `raices`, `factorizar_polinomio`, `ecuacion_segundo_grado`
- **Fracciones y números**: `fraccion`, `pedir_fraccion`, `calcular`, `escribir_cuenta`, `mcd`, `mcm`, `es_primo`, `divisores`, `factorizar`, `descomponer`, `cambiar_base`, `a_binario`, `a_hexadecimal`, `a_decimal`
- **Estadística**: `media`, `mediana`, `moda`, `varianza`, `desviacion`, `cuartiles`, `tabla_frecuencias`, `histograma`, `estadisticas`
- **Imágenes y modelos 3D**: `imagen`, `ver_modelo`, `dibujar_modelo`, `modelo`, `Modelo`
- **Gráficas**: `grafica`, `barras`, `minigrafica`
- **Practicar**: `practicar`, `lista_temas`
- **Ratón**: `activar_raton`, `desactivar_raton`, `esperar_clic`, `leer_raton`, `posicion_raton`, `zona`, `boton`, `botones`, `bucle`
- **Diseñar y ver posiciones**: `diseno`, `regla`, `depurar`
- **Otras clases y ayuda**: `ayuda`, `Spinner`, `PantallaDeCarga`, `Fraccion`

### Pantalla y cursor

#### `pantalla.limpiar()`

Función · módulo `pantalla.terminal`

Borra toda la pantalla y pone el cursor arriba a la izquierda.

Si antes has puesto un color de fondo con poner_color(fondo="azul"),
la pantalla entera se queda de ese color.

#### `pantalla.limpiar_linea(y=None)`

Función · módulo `pantalla.terminal`

Borra una línea entera. Sin número, borra la línea donde está el cursor.

#### `pantalla.gotoxy(x, y)`

Función · módulo `pantalla.terminal`

Mueve el cursor a la columna x y la fila y.

Las posiciones empiezan en 1: gotoxy(1, 1) es la esquina de arriba a la
izquierda. x va hacia la derecha y y hacia abajo. Si le pasas un número
con decimales (por ejemplo ancho() / 2) lo redondea hacia abajo.

```python
pantalla.gotoxy(10, 5)
print("Estoy en la columna 10, fila 5")
```

#### `pantalla.ir_a(x, y)`

*Es otro nombre de `pantalla.gotoxy`.*

Función · módulo `pantalla.terminal`

Mueve el cursor a la columna x y la fila y.

Las posiciones empiezan en 1: gotoxy(1, 1) es la esquina de arriba a la
izquierda. x va hacia la derecha y y hacia abajo. Si le pasas un número
con decimales (por ejemplo ancho() / 2) lo redondea hacia abajo.

```python
pantalla.gotoxy(10, 5)
print("Estoy en la columna 10, fila 5")
```

#### `pantalla.ancho()`

Función · módulo `pantalla.terminal`

Cuántas columnas tiene la terminal (normalmente 80 o más).

#### `pantalla.alto()`

Función · módulo `pantalla.terminal`

Cuántas filas tiene la terminal (normalmente 24 o más).

#### `pantalla.tamano()`

Función · módulo `pantalla.terminal`

Devuelve (ancho, alto) de la terminal, en columnas y filas.

#### `pantalla.centro()`

Función · módulo `pantalla.terminal`

Devuelve (x, y) del centro de la pantalla.

#### `pantalla.ocultar_cursor()`

Función · módulo `pantalla.terminal`

Esconde el cursor parpadeante (queda más limpio en juegos y menús).

#### `pantalla.mostrar_cursor()`

Función · módulo `pantalla.terminal`

Vuelve a mostrar el cursor.

#### `pantalla.guardar_posicion()`

Función · módulo `pantalla.terminal`

Apunta dónde está el cursor ahora, para volver luego con volver_a_posicion().

#### `pantalla.volver_a_posicion()`

Función · módulo `pantalla.terminal`

Vuelve a donde estaba el cursor cuando llamaste a guardar_posicion().

#### `pantalla.titulo_ventana(texto)`

Función · módulo `pantalla.terminal`

Cambia el título de la ventana de la terminal.

#### `pantalla.pitido()`

Función · módulo `pantalla.terminal`

Hace 'bip' (si la terminal tiene el sonido activado).

#### `pantalla.pausa(segundos)`

Función · módulo `pantalla.terminal`

Espera unos segundos sin hacer nada. Vale con decimales: pausa(0.5).

#### `pantalla.iniciar(borrar=True, cursor=False, aparte=True, titulo=None)`

Función · módulo `pantalla.terminal`

Prepara la terminal para un juego o una aplicación a pantalla completa.

- borrar: limpia la pantalla.
- cursor: si es False, esconde el cursor.
- aparte: usa una "pantalla aparte"; al terminar vuelve a aparecer
  lo que había antes en la terminal, como hacen los programas de verdad.
- titulo: cambia el título de la ventana.

También hace que las teclas que pulses no se vean escritas en la pantalla.
Al acabar llama a terminar() (si se te olvida, se hace solo al cerrar).

#### `pantalla.terminar()`

Función · módulo `pantalla.terminal`

Deja la terminal como estaba: colores normales, cursor visible, etc.

### Escribir

#### `pantalla.escribir(texto='', x=None, y=None, color=None, fondo=None, negrita=False, tenue=False, cursiva=False, subrayado=False, parpadeo=False, invertido=False, tachado=False, nueva_linea=False)`

Función · módulo `pantalla.texto`

Escribe un texto, si quieres en una posición y con color.

```python
pantalla.escribir("Hola")                      # donde esté el cursor
pantalla.escribir("Hola", 10, 5)               # columna 10, fila 5
pantalla.escribir("Hola", 10, 5, color="rojo", negrita=True)
pantalla.escribir("Puntos: " + str(puntos), 1, 1, color="amarillo", fondo="azul")
```
Si el texto tiene varias líneas (con \n), cada línea empieza en la misma
columna x, así que sirve para dibujos hechos con letras.
A diferencia de print(), no salta de línea al final (usa nueva_linea=True).
Con x="centro" lo centra de lado a lado (y con y="centro", de arriba abajo).

#### `pantalla.centrar(texto, y=None, color=None, fondo=None, negrita=False, tenue=False, cursiva=False, subrayado=False, parpadeo=False, invertido=False, tachado=False)`

Función · módulo `pantalla.texto`

Escribe un texto centrado. Sin y, también lo centra de arriba abajo.

pantalla.centrar("GAME OVER", color="rojo", negrita=True)
pantalla.centrar("Pulsa una tecla", y=20)

#### `pantalla.escribir_derecha(texto, y, margen=0, color=None, fondo=None, negrita=False, tenue=False, cursiva=False, subrayado=False, parpadeo=False, invertido=False, tachado=False)`

Función · módulo `pantalla.texto`

Escribe un texto pegado al borde derecho de la pantalla, en la fila y.

pantalla.escribir_derecha("Vidas: 3", 1)

#### `pantalla.escribir_lento(texto, x=None, y=None, velocidad=0.04, color=None, fondo=None, negrita=False, tenue=False, cursiva=False, subrayado=False, parpadeo=False, invertido=False, tachado=False)`

Función · módulo `pantalla.texto`

Escribe el texto letra a letra, como en una máquina de escribir.

velocidad son los segundos entre letra y letra (más pequeño = más rápido).

```python
pantalla.escribir_lento("Había una vez...", 5, 3, velocidad=0.08)
```

#### `pantalla.grande(texto, x=None, y=None, color=None, fondo=None, caracter='█', fuente=None)`

Función · módulo `pantalla.letras`

Escribe un texto con letras grandes. Sin x lo centra; sin y, también de arriba abajo.

```python
pantalla.grande("HOLA")
pantalla.grande("GAME OVER", y=3, color="rojo")
pantalla.grande("123", 5, 2, caracter="#")
pantalla.grande("Hola", fuente="ansi_shadow", color="cian")
```
Con fuente= eliges una fuente ASCII art (mira cuáles hay con lista_fuentes()).

#### `pantalla.texto_grande(texto, caracter='█', fuente=None)`

Función · módulo `pantalla.letras`

Devuelve el texto en letras grandes, para usarlo con print().

```python
print(pantalla.texto_grande("HOLA"))
print(pantalla.texto_grande("FIN", caracter="#"))
print(pantalla.texto_grande("Hola", fuente="slant"))
```
Sin fuente usa "bloques" (5 filas de alto, hechas con el carácter que digas).
Con fuente usa una fuente ASCII art; mira cuáles hay con lista_fuentes().

#### `pantalla.lista_fuentes()`

Función · módulo `pantalla.letras`

Devuelve los nombres de las fuentes que puedes usar en grande() y texto_grande().

```python
print(pantalla.lista_fuentes())
pantalla.grande("HOLA", fuente="slant")
```
"bloques" es la de siempre (5 filas de █). Las demás son fuentes FIGlet,
las mismas que usan las webs de "texto a ASCII art".

#### `pantalla.cabecera(titulo, color='cian', caracter='═')`

Función · módulo `pantalla.componentes`

Pone una barra con un título en la primera fila de la pantalla.

pantalla.cabecera("MATRICES · Suma")

#### `pantalla.pie(texto, color='gris')`

Función · módulo `pantalla.componentes`

Escribe un texto en la última fila (por ejemplo, qué teclas se pueden pulsar).

pantalla.pie("↑↓ moverse   Enter elegir   Esc salir")

### Colores

#### `pantalla.colorear(texto, color=None, fondo=None, negrita=False, tenue=False, cursiva=False, subrayado=False, parpadeo=False, invertido=False, tachado=False)`

Función · módulo `pantalla.colores`

Devuelve el texto con color, para usarlo con print().

print("Esto es", pantalla.colorear("importante", "rojo", negrita=True))

#### `pantalla.poner_color(color=None, fondo=None, negrita=False, tenue=False, cursiva=False, subrayado=False, parpadeo=False, invertido=False, tachado=False)`

Función · módulo `pantalla.colores`

Cambia el color de todo lo que escribas a partir de ahora (también con print).

pantalla.poner_color("verde")
print("Esto sale en verde")
pantalla.quitar_color()

#### `pantalla.quitar_color()`

Función · módulo `pantalla.colores`

Vuelve al color normal de la terminal.

#### `pantalla.lista_colores()`

Función · módulo `pantalla.colores`

Devuelve la lista con los nombres de los colores que se pueden usar.

### Dibujar

#### `pantalla.rodear(estilo='doble', color=None, fondo=None, titulo=None)`

Función · módulo `pantalla.dibujo`

Dibuja un borde alrededor de toda la pantalla.

```python
pantalla.rodear()                 # borde doble
pantalla.rodear("=")              # borde hecho con =
pantalla.rodear("*", color="amarillo", titulo="Mi juego")
```
Estilos: "simple", "doble", "grueso", "redondo", "ascii" o cualquier carácter.

#### `pantalla.caja(x=None, y=None, ancho=20, alto=6, estilo='simple', color=None, fondo=None, titulo=None, relleno=False)`

Función · módulo `pantalla.dibujo`

Dibuja una caja (un rectángulo con borde).

- x, y: la esquina de arriba a la izquierda (sin ellas, la caja sale en el centro).
- ancho, alto: lo que mide, contando el borde.
- estilo: "simple", "doble", "grueso", "redondo", "ascii" o un carácter como "*".
- titulo: un texto que se pone en el borde de arriba.
- relleno: True para borrar lo que haya dentro (o un carácter para rellenarla con él).

```python
pantalla.caja(5, 3, 30, 10)
pantalla.caja(5, 3, 30, 10, estilo="doble", color="cian", titulo="Inventario")
pantalla.caja(ancho=40, alto=10, titulo="En el centro")
```

#### `pantalla.linea(y, caracter='─', x=1, largo=None, color=None, fondo=None)`

Función · módulo `pantalla.dibujo`

Dibuja una línea horizontal en la fila y (de lado a lado si no dices el largo).

pantalla.linea(3)
pantalla.linea(3, "=", color="azul")
pantalla.linea(10, "-", x=5, largo=20)

#### `pantalla.linea_vertical(x, caracter='│', y=1, largo=None, color=None, fondo=None)`

Función · módulo `pantalla.dibujo`

Dibuja una línea vertical en la columna x (de arriba abajo si no dices el largo).

pantalla.linea_vertical(40)
pantalla.linea_vertical(40, "|", y=3, largo=10, color="gris")

#### `pantalla.rellenar(x, y, ancho, alto, caracter=' ', color=None, fondo=None)`

Función · módulo `pantalla.dibujo`

Rellena un rectángulo con un carácter. Con espacios sirve para borrar una zona.

pantalla.rellenar(10, 5, 20, 4, fondo="azul")    # un rectángulo azul
pantalla.rellenar(10, 5, 20, 4)                   # borra esa zona
pantalla.rellenar(1, 20, 80, 1, "~", color="azul") # agua

#### `pantalla.punto(x, y, caracter='█', color=None, fondo=None)`

Función · módulo `pantalla.dibujo`

Pinta un solo carácter en (x, y). Ideal para juegos.

pantalla.punto(10, 5)                       # un cuadrado
pantalla.punto(10, 5, "@", color="amarillo")  # el jugador
pantalla.punto(10, 5, " ")                  # borrarlo

#### `pantalla.arte(dibujo, x=None, y=None, color=None, fondo=None, colores=None, fondos=None, transparente=True)`

Función · módulo `pantalla.arte`

Dibuja un arte ASCII (un dibujo hecho con letras) en la pantalla.

```python
gato = r'''
 /\_/\
( o.o )
 > ^ <
'''
pantalla.arte(gato, 10, 5, color="amarillo")
```
- x, y: la esquina de arriba a la izquierda (sin ellas, sale en el centro).
- colores: otro dibujo del mismo tamaño, pero con una letra de color en cada sitio
  (r rojo, v verde, a amarillo, z azul, m morado, c cian, b blanco, n negro, g gris,
  o naranja, x marrón, p rosa; en mayúscula, la versión "claro"). Un espacio o un
  punto deja el color normal.
- fondos: igual que colores, pero para el color de fondo.
- transparente: con True (lo normal) los espacios no borran lo que haya debajo.

```python
pantalla.arte(["(^_^)", "/| |\\"], 5, 5, colores=["aaaaa", "vv vv"])
```
Si es un texto, se le quita el salto de línea del principio y el del final,
así puedes escribirlo con tres comillas como en el ejemplo del gato. Pon una r
delante de las comillas (r''') para que las barras \ salgan tal cual.

### Teclado

#### `pantalla.tecla()`

Función · módulo `pantalla.teclado`

Espera a que pulses una tecla y te dice cuál ha sido (no hace falta Enter).

```python
t = pantalla.tecla()
if t == "arriba":
    y = y - 1
elif t == "q":
    print("Adiós")
```
Nombres especiales: "arriba", "abajo", "izquierda", "derecha", "enter",
"espacio", "esc", "tab", "borrar", "suprimir", "f1"... Las letras salen tal cual.
Al comparar no importan las mayúsculas: t == "Intro" o t == "A" también valen.

#### `pantalla.tecla_pulsada()`

Función · módulo `pantalla.teclado`

Mira si hay una tecla pulsada SIN esperar. Devuelve la tecla o None.

Es lo que se usa en los juegos, para que las cosas se sigan moviendo
aunque no pulses nada:

```python
while True:
    t = pantalla.tecla_pulsada()
    if t == "izquierda":
        x = x - 1
    ...
    pantalla.pausa(0.1)
```

#### `pantalla.vaciar_teclado()`

Función · módulo `pantalla.teclado`

Olvida las teclas que se hayan pulsado y no se hayan leído todavía.

#### `pantalla.esperar(mensaje='Pulsa una tecla para continuar...', x=None, y=None, color=None)`

Función · módulo `pantalla.teclado`

Escribe un mensaje y espera a que pulses una tecla. Devuelve la tecla.

pantalla.esperar()
pantalla.esperar("Pulsa cualquier tecla para empezar", 10, 20, color="gris")

#### `pantalla.pedir(pregunta='', x=None, y=None, color=None, color_respuesta=None)`

Función · módulo `pantalla.teclado`

Hace una pregunta y devuelve lo que escribas (al pulsar Enter), como input().

```python
nombre = pantalla.pedir("¿Cómo te llamas? ")
nombre = pantalla.pedir("Nombre: ", 10, 5, color="cian")
```
Devuelve siempre un texto, sin espacios al principio ni al final.

#### `pantalla.pedir_numero(pregunta='Escribe un número: ', x=None, y=None, minimo=None, maximo=None, decimales=False, color=None)`

Función · módulo `pantalla.teclado`

Pide un número y no para hasta que le escribas uno que valga.

```python
edad = pantalla.pedir_numero("¿Cuántos años tienes? ", minimo=0, maximo=120)
precio = pantalla.pedir_numero("Precio: ", decimales=True)
```
Con decimales=False devuelve un int; con decimales=True, un float (vale 2,5 o 2.5).

#### `pantalla.pedir_contrasena(pregunta='Contraseña: ')`

Función · módulo `pantalla.teclado`

Pide un texto sin que se vea lo que escribes (para contraseñas).

#### `pantalla.confirmar(pregunta='¿Seguro? (s/n) ', x=None, y=None, color=None)`

Función · módulo `pantalla.teclado`

Hace una pregunta de sí o no. Devuelve True si pulsas 's' y False si pulsas 'n'.

if pantalla.confirmar("¿Quieres salir? (s/n) "):
```python
break
```

### Cosas ya hechas

#### `pantalla.menu(opciones, titulo=None, x=None, y=None, color=None, color_seleccion='amarillo', estilo='redondo', inicial=0, ayudas=None, iconos=None, ayuda_x=None, ayuda_y=None, color_ayuda=None)`

Función · módulo `pantalla.componentes`

Enseña un menú en una caja y deja elegir con las flechas y Enter.

Devuelve el texto de la opción elegida, o None si pulsas Esc.
También puedes pulsar el número de la opción.

```python
opcion = pantalla.menu(["Jugar", "Opciones", "Salir"], titulo="Menú")
if opcion == "Jugar":
    ...
```
- ayudas: una explicación de cada opción, que sale debajo al pasar por ella.
- ayuda_x, ayuda_y: dónde poner esa explicación, si no la quieres justo debajo.
- color_ayuda: el color de la explicación (si no, el de color_seleccion).
- iconos: un dibujito o símbolo para cada opción.
- inicial: la opción que sale marcada al empezar (su texto o su número).

```python
pantalla.menu(["Jugar", "Salir"],
              ayudas={"Jugar": "Empieza una partida", "Salir": "Cierra el juego"},
              iconos={"Jugar": "►", "Salir": "×"})

AYUDA = {"Jugar": "Empieza una partida", "Salir": "Cierra el juego"}
pantalla.menu(["Jugar", "Salir"], ayudas=AYUDA, ayuda_x=3, ayuda_y=pantalla.alto() - 2)
```
Si en vez de una lista le das un diccionario, hace un menú con secciones en cajas
(como el de un programa de verdad) y te mueves con las cuatro flechas:

```python
pantalla.menu({"Operaciones": ["Sumar", "Restar"],
               "Otros": ["Ajustes", "Salir"]})
```
Sin x ni y, el menú sale en el centro de la pantalla.

#### `pantalla.elegir(pregunta, opciones, x=None, y=None, inicial=0, color=None, color_seleccion='amarillo')`

Función · módulo `pantalla.componentes`

Hace una pregunta con las opciones en fila; se elige con ← → y Enter.

```python
r = pantalla.elegir("¿Desarrollar por?", ["Fila", "Columna"])
dificultad = pantalla.elegir("Dificultad:", ["Fácil", "Normal", "Difícil"], 5, 10)
```
Devuelve el texto de la opción elegida, o None si pulsas Esc.

#### `pantalla.elegir_varios(opciones, titulo=None, x=None, y=None, marcadas=None, color=None, color_seleccion='amarillo', estilo='redondo', minimo=0, maximo=None)`

Función · módulo `pantalla.componentes`

Una lista para marcar varias opciones: ↑↓ para moverte, Espacio para marcar y Enter para acabar.

```python
extras = pantalla.elegir_varios(["Queso", "Tomate", "Jamón", "Piña"], titulo="Ingredientes")
# ['Queso', 'Jamón']

pantalla.elegir_varios(opciones, marcadas=["Queso"])     # que salgan ya marcadas
pantalla.elegir_varios(opciones, minimo=1, maximo=2)     # que elijan una o dos
```
Devuelve la lista de las opciones marcadas (en el mismo orden), o None si pulsas Esc.
Sin x ni y, sale en el centro de la pantalla.

#### `pantalla.formulario(campos, titulo='Formulario', x=None, y=None, color='cian', ancho_campo=20)`

Función · módulo `pantalla.componentes`

Pide varias cosas a la vez, cada una en su casilla, dentro de una caja.

```python
datos = pantalla.formulario(["Nombre", "Apellidos", "Ciudad"])
print(datos["Nombre"])

datos = pantalla.formulario({"Nombre": "texto", "Edad": "numero",
                             "Altura": "decimal", "Clave": "contraseña"})
```
Tipos que valen: "texto", "numero" (entero), "decimal", "fraccion" y "contraseña".
Te mueves con ↑↓ (o Tab) y con Enter pasas a la siguiente; en la última, Enter acaba.
Devuelve un diccionario con lo que se ha escrito en cada casilla, o None si pulsas Esc.

#### `pantalla.mensaje(texto, titulo='Aviso', color=None, color_borde='cian', estilo='doble', esperar_tecla=True)`

Función · módulo `pantalla.componentes`

Saca una ventanita en el centro con un mensaje y espera a que pulses una tecla.

```python
pantalla.mensaje("¡Has ganado!", titulo="Enhorabuena", color_borde="verde")
pantalla.mensaje("No hay más vidas\nPuntos: 120", titulo="Fin")
```
Devuelve la tecla pulsada.

#### `pantalla.tabla(filas, cabeceras=None, x=None, y=None, estilo='simple', color=None, color_cabecera='cian')`

Función · módulo `pantalla.componentes`

Dibuja una tabla con bordes.

```python
notas = [["Ana", 8.5], ["Luis", 6], ["Marta", 9.75]]
pantalla.tabla(notas, cabeceras=["Nombre", "Nota"])
pantalla.tabla(notas, ["Nombre", "Nota"], x=5, y=3, estilo="doble")
```
Sin x ni y, se escribe donde esté el cursor (como un print).
Los números se alinean a la derecha y los textos a la izquierda.

### Barras y pantallas de carga

#### `pantalla.barra_progreso(valor, total=100, x=None, y=None, ancho=30, color='verde', porcentaje=True, lleno=None, vacio=None, estilo='bloques', color_final=None, texto=None)`

Función · módulo `pantalla.componentes`

Dibuja una barra de progreso. Llámala otra vez con otro valor para que avance.

```python
for i in range(101):
    pantalla.barra_progreso(i, 100, 10, 5)
    pantalla.pausa(0.02)

pantalla.barra_progreso(40, 100, 10, 5, estilo="suave", color="cian")
pantalla.barra_progreso(vida, 100, 2, 1, color="rojo", color_final="verde", texto="Vida")
```
- estilo: "bloques" ███░░░, "suave" (avanza de octavo en octavo), "linea" ━━━╺──,
  "ascii" [===>  ], "puntos" ⣿⣿⣀⣀, "cuadros" ■■□□, "circulos" ●●○○, "rombos" ◆◆◇◇,
  "flechas" ▰▰▱▱ y "rayas" ▮▮▯▯. Están todos en pantalla.lista_barras().
- color_final: la barra va cambiando de color hasta este (de rojo a verde, por ejemplo).
- lleno, vacio: tus propios caracteres (mandan sobre los del estilo).
- texto: un nombre que se escribe delante de la barra.
Sin x ni y, la dibuja en la línea donde esté el cursor (y la va sobrescribiendo).

#### `pantalla.lista_barras()`

Función · módulo `pantalla.componentes`

Devuelve los nombres de los estilos de barra_progreso() y pantalla_de_carga().

for estilo in pantalla.lista_barras():
```python
print(estilo)
```

#### `pantalla.pantalla_de_carga(titulo='Cargando', segundos=None, tareas=None, total=100, estilo='suave', color='cian', color_final=None, ancho=40, fuente=None, spinner='dots', consejos=None, marco=None, color_titulo=None, borrar=True)`

Función · módulo `pantalla.cargas`

Una pantalla de carga como la de los juegos, con la barra en el centro.

Hay tres formas de usarla, de la más fácil a la más completa:

1. De mentira, para que quede bonito: carga durante unos segundos y se va.

```python
pantalla.pantalla_de_carga("Cargando nivel 1", segundos=3)
```
2. Con tareas: va haciendo cada una y la barra avanza sola.
   Un texto es un paso de mentira, una función se llama de verdad.

```python
pantalla.pantalla_de_carga("Preparando", tareas=["Cargando mapa", "Colocando enemigos"], segundos=2)
mapa, sonidos = pantalla.pantalla_de_carga("Cargando", tareas=[("Mapa", leer_mapa),
                                                               ("Sonidos", leer_sonidos)])
```
3. Tú mueves la barra, con with:

```python
with pantalla.pantalla_de_carga("Descargando", total=len(archivos)) as carga:
    for archivo in archivos:
        carga.avanzar(texto=archivo)     # o carga.valor = 7
        descargar(archivo)
```
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

#### `pantalla.cargando(segundos=2, texto='Cargando', x=None, y=None, color='amarillo')`

Función · módulo `pantalla.componentes`

Enseña una animación de "Cargando..." durante unos segundos.

pantalla.cargando(3, "Guardando partida")

#### `pantalla.calculando(texto='Calculando', segundos=0.8, color='amarillo', color_borde='cian')`

Función · módulo `pantalla.componentes`

Saca una ventanita en el centro con "Calculando..." y los puntitos moviéndose.

Al acabar la borra. Queda bien antes de enseñar un resultado:

```python
pantalla.calculando()
pantalla.calculando("Pensando", segundos=2)
```

#### `pantalla.spinner(texto='', estilo='dots', color='cian', color_texto=None, x=None, y=None, intervalo=None)`

Función · módulo `pantalla.spinners`

Un spinner (la ruedecita de "cargando") que gira mientras tu programa trabaja.

Lo más fácil, con with: gira mientras se hace lo de dentro y al acabar deja
"✔ texto" (o "✖ texto" si hay un error):

```python
with pantalla.spinner("Descargando..."):
    descargar()
```
O a mano:

```python
s = pantalla.spinner("Cargando", estilo="arco", color="amarillo")
s.empezar()
...
s.texto = "Casi está..."      # cambia el texto mientras gira
s.bien("¡Cargado!")           # también: s.mal(...), s.aviso(...), s.info(...), s.parar()
```
- estilo: "dots", "line", "arc", "star", "bouncingBall", "shark"... (o en español:
  "puntos", "linea", "arco", "estrella", "pelota", "tiburon"...). Mira todos con
  pantalla.lista_spinners(). También vale una lista tuya: estilo=["◐", "◓", "◑", "◒"].
- x, y: para que gire en un sitio fijo de la pantalla (sin ellos, donde esté el cursor).
- intervalo: segundos entre fotograma y fotograma (cada estilo tiene el suyo).

Mientras gira, mejor no escribas con print() en la misma línea.

#### `pantalla.lista_spinners()`

Función · módulo `pantalla.spinners`

Devuelve los nombres de todos los estilos de spinner.

```python
for nombre in pantalla.lista_spinners():
    print(nombre)
```
También valen en español: "puntos", "linea", "arco", "circulo", "estrella",
"flecha", "pelota", "tiburon", "barra", "binario"...

### Juegos

#### `pantalla.jugar(actualizar, velocidad=20, ancho=None, alto=None, fondo=None, salir_con='esc', raton=False)`

Función · módulo `pantalla.juego`

Hace funcionar un juego: llama a tu función muchas veces por segundo.

```python
def actualizar(tecla):
    ...mueve cosas según la tecla y dibuja cómo está todo...

pantalla.jugar(actualizar)
```
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

#### `pantalla.Sprite(dibujo=None, x=1, y=1, color=None, fondo=None, colores=None, fondos=None, fotogramas=None, cada=5, transparente=True, capa=0)`

Clase · módulo `pantalla.juego`

Un dibujo que se mueve: la nave, un marciano, una bala, una pelota...

```python
nave = pantalla.Sprite("/^\\", 38, 22, color="verde")
marciano = pantalla.Sprite(fotogramas=["/oo\\", "\\oo/"], x=10, y=3, color="cian")

nave.mover(1, 0)            # un paso a la derecha
nave.x = 40                 # o ponerla donde quieras
if bala.choca(marciano):    # ¿se tocan? (letra a letra, los espacios no cuentan)
    marciano.eliminar()
if bala.fuera():            # ¿se ha salido de la pantalla?
    bala.eliminar()
```
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

- `.dibujo` (propiedad): El dibujo que se ve ahora. Puedes cambiarlo: nave.dibujo = "*" (una explosión).
- `.fotogramas` (propiedad)
- `.ancho` (propiedad)
- `.alto` (propiedad)
- `.mover(dx=0, dy=0)`: Mueve el sprite: mover(1, 0) un paso a la derecha, mover(0, -1) uno hacia arriba.
- `.choca(otro)`: ¿Toca a otro sprite? Devuelve el sprite con el que choca (o None).

  ```
  if bala.choca(marciano): ...
  tocado = bala.choca(marcianos)     # con una lista: dice cuál
  if nave.choca((x, y)): ...         # o con una posición
  ```
- `.fuera()`: True si el sprite se ha salido entero de la pantalla (del juego).
- `.eliminar()`: Lo quita del juego: ya no se dibuja ni choca.
- `.borrar()`: Lo quita del juego: ya no se dibuja ni choca.
- `.dibujar()`: Lo dibuja ahora (fuera de jugar(); dentro se dibuja solo).

#### `pantalla.sprites()`

Función · módulo `pantalla.juego`

La lista de Sprite vivos (los que se dibujan solos en jugar()).

#### `pantalla.cada(segundos, clave=None)`

Función · módulo `pantalla.juego`

Devuelve True una vez cada tantos segundos (y False el resto de veces).

```python
def actualizar(tecla):
    if pantalla.cada(0.5):
        mover_marcianos()
    if pantalla.cada(2):
        disparar()
```
Cada sitio del programa donde escribes cada() lleva su propia cuenta. Si lo usas
dentro de un for (una cuenta por cada marciano), dale una clave: cada(1, marciano).
Dentro de jugar() cuenta el tiempo del juego; fuera, el del reloj.

#### `pantalla.fotograma()`

Función · módulo `pantalla.juego`

Cuántas veces se ha llamado ya a tu función en este juego (0, 1, 2...).

if pantalla.fotograma() % 10 == 0:   # una de cada 10 veces
```python
...
```

#### `pantalla.pulsada(tecla)`

Función · módulo `pantalla.juego`

Dice si una tecla está apretada AHORA (True o False). Para moverse suave en juegos.

```python
def actualizar(tecla):
    if pantalla.pulsada("izquierda"):
        nave.mover(-1, 0)
```
Nombres: "izquierda", "derecha", "arriba", "abajo", "espacio", "enter", letras ("a")...
En Windows es exacto. En Linux y Mac la terminal no avisa de cuándo se suelta una
tecla: cuenta como apretada si ha llegado hace muy poco (al empezar a mantenerla hay
un saltito, el mismo que ves al dejar una letra pulsada en un editor).

### Récords y tiempo

#### `pantalla.guardar_record(nombre, puntos, archivo='records.json', menos_es_mejor=False, cuantos=10)`

Función · módulo `pantalla.records`

Guarda una puntuación en un archivo y devuelve en qué puesto ha quedado (1 es el mejor).
Si no entra entre los mejores, devuelve None.

```python
puesto = pantalla.guardar_record("Ana", 120)
if puesto == 1:
    print("¡Nuevo récord!")
pantalla.guardar_record("Luis", 34.5, "tiempos.json", menos_es_mejor=True)   # tiempos: gana el menor
```
- cuantos: cuántos récords se guardan como mucho.
El archivo se crea en la carpeta de tu programa.

#### `pantalla.leer_records(archivo='records.json')`

Función · módulo `pantalla.records`

Los récords guardados, del mejor al peor, como una lista de (nombre, puntos).

for nombre, puntos in pantalla.leer_records():
```python
print(nombre, puntos)
```

#### `pantalla.mejor_record(archivo='records.json')`

Función · módulo `pantalla.records`

La mejor puntuación guardada, o None si todavía no hay ninguna.

print("Récord:", pantalla.mejor_record())

#### `pantalla.tabla_records(archivo='records.json', x=None, y=None, color=None, color_cabecera='amarillo')`

Función · módulo `pantalla.records`

Dibuja la tabla de récords: puesto, nombre, puntos y fecha.

pantalla.tabla_records()
pantalla.tabla_records("tiempos.json", 10, 5)

#### `pantalla.cronometro()`

Función · módulo `pantalla.records`

Pone en marcha un cronómetro y lo devuelve.

c = pantalla.cronometro()
pantalla.pedir("Pulsa Enter cuando quieras... ")
print("Has tardado", c)            # Has tardado 00:03.2

#### `pantalla.Cronometro(empezar=True)`

Clase · módulo `pantalla.records`

Un cronómetro. Empieza a contar al crearlo.

c = pantalla.Cronometro()       # o pantalla.cronometro()
...
print(c.segundos)               # 12.34
print(c)                        # 00:12.3
c.parar()                       # se queda quieto
c.empezar()                     # sigue contando desde donde iba
c.reiniciar()                   # vuelve a 0 y sigue contando

- `.segundos` (propiedad): Los segundos que lleva contados.
- `.en_marcha` (propiedad): True si está contando.
- `.empezar()`: Empieza a contar (o sigue, si estaba parado).
- `.parar()`: Para el cronómetro. Devuelve los segundos que lleva.
- `.reiniciar()`: Vuelve a 0 y sigue contando.
- `.texto(decimas=True)`: El tiempo como en un reloj: 01:23.4 (o 01:23 con decimas=False). Con horas, 1:02:03.

#### `pantalla.cuenta_atras(segundos=3, x=None, y=None, color='amarillo', final='¡Ya!', grande=False)`

Función · módulo `pantalla.records`

Una cuenta atrás: 3, 2, 1, ¡Ya!, un número cada segundo.

```python
pantalla.cuenta_atras()                    # donde esté el cursor
pantalla.cuenta_atras(5, 10, 3)            # en la columna 10, fila 3
pantalla.cuenta_atras(3, grande=True)      # con letras grandes, en el centro
```
final: lo que sale al acabar ("" para nada).

### Matrices

#### `pantalla.matriz(M, x=None, y=None, nombre=None, color=None, color_nombre='cian', det=False, ampliada=False)`

Función · módulo `pantalla.matrices`

Dibuja una matriz con sus corchetes. Devuelve (ancho, alto) de lo que ocupa.

```python
A = [[1, 2], [3, 4]]
pantalla.matriz(A)                          # donde esté el cursor, como un print
pantalla.matriz(A, 5, 3, nombre="A")        # en la columna 5, fila 3, con "A ="
pantalla.matriz(A, 5, 3, det=True)          # con barras, como un determinante
pantalla.matriz([[1, 2, 5], [3, 4, 6]], ampliada=True)   # con una raya antes de la última columna
```
Vale con números enteros, decimales y fracciones (pantalla.fraccion("1/2")).

#### `pantalla.pedir_matriz(nombre='A', filas=None, columnas=None, cuadrada=False, maximo=6, fracciones=False, titulo=None, color='cian')`

Función · módulo `pantalla.matrices`

Pide una matriz en una ventana: primero el tamaño con las flechas y luego cada número.

```python
A = pantalla.pedir_matriz()                         # eliges el tamaño tú
B = pantalla.pedir_matriz("B", filas=2, columnas=3)  # tamaño fijo
C = pantalla.pedir_matriz("C", cuadrada=True)         # filas = columnas
```
Devuelve una lista de filas, por ejemplo [[1, 2], [3, 4]], o None si pulsas Esc.
Se pueden escribir enteros, decimales (2.5 o 2,5) y fracciones (1/2).
Con fracciones=True devuelve Fraction en vez de decimales.

#### `pantalla.sumar_matrices(A, B)`

Función · módulo `pantalla.matrices`

Suma dos matrices del mismo tamaño, número a número.

C = pantalla.sumar_matrices([[1, 2], [3, 4]], [[10, 20], [30, 40]])
# [[11, 22], [33, 44]]

#### `pantalla.restar_matrices(A, B)`

Función · módulo `pantalla.matrices`

Resta dos matrices del mismo tamaño (A - B), número a número.

C = pantalla.restar_matrices([[5, 5], [5, 5]], [[1, 2], [3, 4]])
# [[4, 3], [2, 1]]

#### `pantalla.multiplicar_matrices(A, B)`

Función · módulo `pantalla.matrices`

Multiplica dos matrices (A · B), o una matriz por un número.

```python
C = pantalla.multiplicar_matrices([[1, 2], [3, 4]], [[5], [6]])   # [[17], [39]]
D = pantalla.multiplicar_matrices(3, [[1, 2], [3, 4]])            # [[3, 6], [9, 12]]
```
Para multiplicar dos matrices, las columnas de la primera tienen que ser
tantas como las filas de la segunda. Ojo: A · B no suele dar lo mismo que B · A.

#### `pantalla.transpuesta(A)`

Función · módulo `pantalla.matrices`

Cambia las filas por las columnas.

pantalla.transpuesta([[1, 2, 3], [4, 5, 6]])    # [[1, 4], [2, 5], [3, 6]]

#### `pantalla.identidad(n)`

Función · módulo `pantalla.matrices`

La matriz identidad de n x n: unos en la diagonal y ceros en el resto.

pantalla.identidad(3)     # [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

#### `pantalla.traza(A)`

Función · módulo `pantalla.matrices`

Suma los números de la diagonal (solo matrices cuadradas).

pantalla.traza([[1, 2], [3, 4]])     # 5

#### `pantalla.determinante(A)`

Función · módulo `pantalla.matrices`

El determinante de una matriz cuadrada.

```python
pantalla.determinante([[1, 2], [3, 4]])                    # -2
pantalla.determinante([[2, 0, 1], [1, 3, 2], [1, 1, 2]])   # 6
```
Si es 0, la matriz no tiene inversa.

#### `pantalla.inversa(A)`

Función · módulo `pantalla.matrices`

La matriz inversa (la que multiplicada por A da la identidad).

```python
pantalla.inversa([[2, 1], [1, 1]])     # [[1, -1], [-1, 2]]
pantalla.inversa([[1, 2], [3, 4]])     # [[-2, 1], [3/2, -1/2]]
```
Solo existe si la matriz es cuadrada y su determinante no es 0.

#### `pantalla.rango(A)`

Función · módulo `pantalla.matrices`

El rango de una matriz: cuántas filas quedan que no son todo ceros al escalonarla.

pantalla.rango([[1, 2], [2, 4]])     # 1  (la segunda fila es el doble de la primera)

#### `pantalla.potencia_matriz(A, n)`

Función · módulo `pantalla.matrices`

Multiplica una matriz cuadrada por sí misma n veces (A elevado a n).

pantalla.potencia_matriz([[1, 1], [1, 0]], 5)    # [[8, 5], [5, 3]]
pantalla.potencia_matriz(A, 0)                  # la identidad
pantalla.potencia_matriz(A, -1)                 # la inversa

#### `pantalla.escalonar(A, pasos=False, reducida=False, ampliada=False)`

Función · módulo `pantalla.matrices`

Hace el método de Gauss: deja ceros por debajo de la diagonal.

```python
E = pantalla.escalonar([[1, 2, 3], [4, 5, 6], [7, 8, 10]])
pantalla.escalonar(A, pasos=True)        # enseña cada paso: F2 → F2 - 4·F1 ...
pantalla.escalonar(A, reducida=True)     # Gauss-Jordan: unos en la diagonal y ceros arriba también
pantalla.escalonar(Ab, pasos=True, ampliada=True)   # con la raya de la matriz ampliada
```
Devuelve la matriz escalonada.

#### `pantalla.resolver_sistema(A, b=None, pasos=False)`

Función · módulo `pantalla.matrices`

Resuelve un sistema de ecuaciones lineales por Gauss.

```python
# 2x + y = 5
#  x - y = 1
x, y = pantalla.resolver_sistema([[2, 1], [1, -1]], [5, 1])     # 2, 1
pantalla.resolver_sistema([[2, 1, 5], [1, -1, 1]], pasos=True)  # con la ampliada, paso a paso
```
Devuelve la lista con el valor de cada incógnita. Si el sistema no tiene una
única solución devuelve None (pantalla.clasificar_sistema() te dice por qué).
Con pasos=True enseña cada paso de Gauss y la solución.

#### `pantalla.clasificar_sistema(A, b=None)`

Función · módulo `pantalla.matrices`

Dice cómo es un sistema de ecuaciones (por el teorema de Rouché-Frobenius).

```python
# x + y = 3
# x - y = 1
pantalla.clasificar_sistema([[1, 1], [1, -1]], [3, 1])    # "compatible determinado"
```
Devuelve "compatible determinado" (una solución), "compatible indeterminado"
(infinitas soluciones) o "incompatible" (ninguna). Sin b, la última columna
de A son los resultados (la matriz ampliada).

### Vectores

#### `pantalla.vector(v, x=None, y=None, nombre=None, color=None, color_nombre='cian', vertical=False)`

Función · módulo `pantalla.vectores`

Escribe un vector: u = (3, -1, 2). Devuelve (ancho, alto) de lo que ocupa.

pantalla.vector((3, -1, 2), nombre="u")            # u = (3, -1, 2), donde esté el cursor
pantalla.vector((3, -1, 2), 5, 3, nombre="u")      # en la columna 5, fila 3
pantalla.vector((3, -1, 2), nombre="u", vertical=True)   # en columna, con corchetes

#### `pantalla.Vector(*componentes)`

Clase · módulo `pantalla.vectores`

Un vector que sale como (3, 4) al hacer print y que se suma con + y se multiplica con *.

u = pantalla.Vector(3, 4)
v = pantalla.Vector([1, 2])
print(u + v)          # (4, 6)
print(2 * u - v)      # (5, 6)
print(abs(u))         # 5   (el módulo)
x, y = u              # se puede separar como una tupla

#### `pantalla.pedir_vector(nombre='u', dimension=None, maximo=6, fracciones=False, titulo=None, color='cian')`

Función · módulo `pantalla.vectores`

Pide un vector en una ventana: primero cuántos números tiene y luego cada uno.

```python
u = pantalla.pedir_vector()                    # eliges cuántos números
v = pantalla.pedir_vector("v", dimension=3)    # (x, y, z)
```
Devuelve un Vector, o None si pulsas Esc.

#### `pantalla.vector_entre(A, B)`

Función · módulo `pantalla.vectores`

El vector que va del punto A al punto B (B - A).

pantalla.vector_entre((1, 2), (4, 6))      # (3, 4)

#### `pantalla.sumar_vectores(u, v)`

Función · módulo `pantalla.vectores`

Suma dos vectores número a número.

pantalla.sumar_vectores((1, 2), (3, 4))     # (4, 6)

#### `pantalla.restar_vectores(u, v)`

Función · módulo `pantalla.vectores`

Resta dos vectores (u - v) número a número.

pantalla.restar_vectores((5, 5), (1, 2))    # (4, 3)

#### `pantalla.multiplicar_vector(k, u)`

Función · módulo `pantalla.vectores`

Multiplica un vector por un número (vale en los dos órdenes).

pantalla.multiplicar_vector(3, (1, -2))          # (3, -6)
pantalla.multiplicar_vector((1, -2), "1/2")      # (1/2, -1)

#### `pantalla.producto_escalar(u, v, pasos=False)`

Función · módulo `pantalla.vectores`

El producto escalar u · v: multiplica número a número y lo suma todo.

```python
pantalla.producto_escalar((1, 2, 3), (4, -5, 6))               # 12
pantalla.producto_escalar((1, 2, 3), (4, -5, 6), pasos=True)
# u · v = 1·4 + 2·(-5) + 3·6 = 4 - 10 + 18 = 12
```
Si da 0, los vectores son perpendiculares.

#### `pantalla.producto_vectorial(u, v, pasos=False)`

Función · módulo `pantalla.vectores`

El producto vectorial u × v (solo con vectores de 3 números). Sale perpendicular a los dos.

pantalla.producto_vectorial((1, 0, 0), (0, 1, 0))        # (0, 0, 1)
pantalla.producto_vectorial((1, 2, 3), (4, 5, 6), pasos=True)
#         │ i  j  k │
# u × v = │ 1  2  3 │ = (2·6 - 3·5, 3·4 - 1·6, 1·5 - 2·4) = (-3, 6, -3)
#         │ 4  5  6 │

#### `pantalla.producto_mixto(u, v, w)`

Función · módulo `pantalla.vectores`

El producto mixto [u, v, w] = u · (v × w): el determinante de los tres vectores.

```python
pantalla.producto_mixto((1, 0, 0), (0, 1, 0), (0, 0, 1))      # 1
```
Su valor absoluto es el volumen del paralelepípedo que forman. Si da 0, los tres están en el mismo plano.

#### `pantalla.modulo(u, pasos=False, nombre='u')`

Función · módulo `pantalla.vectores`

El módulo (lo que mide) de un vector: la raíz de la suma de los cuadrados.

pantalla.modulo((3, 4))              # 5
pantalla.modulo((1, 1))              # 1.414213562373
pantalla.modulo((2, 2), pasos=True)  # |u| = √(2² + 2²) = √8 = 2√2 ≈ 2.8284
pantalla.modulo(v, pasos=True, nombre="v")   # |v| = ...

#### `pantalla.unitario(u)`

Función · módulo `pantalla.vectores`

El vector de la misma dirección que mide 1 (u dividido entre su módulo).

pantalla.unitario((3, 4))      # (3/5, 4/5)

#### `pantalla.distancia(A, B, pasos=False)`

Función · módulo `pantalla.espacio`

La distancia (la más corta) entre dos cosas: puntos, rectas o planos.

```python
pantalla.distancia((1, 1), (4, 5))              # dos puntos: 5
pantalla.distancia((1, 2, 3), pi)               # de un punto a un plano
pantalla.distancia((1, 2, 3), r)                # de un punto a una recta
pantalla.distancia(r, s)                        # dos rectas (si se cruzan, con el producto mixto)
pantalla.distancia(r, pi)  /  (pi, sigma)       # 0 si se cortan; si son paralelos, la de verdad
pantalla.distancia((0, 0, 0), pi, pasos=True)   # con la fórmula y los números puestos
```
Sale exacta si se puede (5, 1/3) y si no con decimales.

#### `pantalla.angulo(u, v, radianes=False, pasos=False)`

Función · módulo `pantalla.espacio`

El ángulo entre dos vectores, dos rectas, dos planos o una recta y un plano (en grados).

```python
pantalla.angulo((1, 0), (0, 1))           # dos vectores: 90.0
pantalla.angulo(r, s)                     # dos rectas: de 0 a 90
pantalla.angulo(r, pi)                    # una recta y un plano (con el seno)
pantalla.angulo(pi, sigma)                # dos planos (con sus vectores normales)
pantalla.angulo(r, pi, pasos=True)
```
radianes=True para que salga en radianes.

#### `pantalla.proyeccion(a, sobre, pasos=False)`

Función · módulo `pantalla.espacio`

La proyección ortogonal (la "sombra" que cae en perpendicular).

```python
pantalla.proyeccion((1, 2, 3), pi)       # el punto de pi más cerca de (1, 2, 3)
pantalla.proyeccion((1, 2, 3), r)        # el punto de r más cerca
pantalla.proyeccion(r, pi)               # la recta que es la sombra de r en pi
pantalla.proyeccion((2, 3), (1, 0))      # dos vectores: la sombra de u sobre v, (2, 0)
pantalla.proyeccion(P, pi, pasos=True)
```
Con dos vectores hace lo de siempre; con un punto o una recta y un plano (o una recta), da el punto o la recta.

#### `pantalla.son_paralelos(u, v)`

Función · módulo `pantalla.vectores`

True si u y v tienen la misma dirección (uno es el otro multiplicado por un número).

pantalla.son_paralelos((1, 2), (3, 6))      # True

#### `pantalla.son_perpendiculares(u, v)`

Función · módulo `pantalla.vectores`

True si u y v forman un ángulo recto (su producto escalar es 0).

pantalla.son_perpendiculares((1, 2), (-2, 1))   # True

#### `pantalla.son_independientes(*vectores)`

Función · módulo `pantalla.vectores`

True si ninguno se puede sacar sumando los otros multiplicados por números.

pantalla.son_independientes((1, 0), (0, 1))              # True
pantalla.son_independientes((1, 2, 3), (2, 4, 6))        # False: el segundo es el doble

#### `pantalla.dibujar_vectores(vectores, x=None, y=None, ancho=41, alto=17, colores=None, cuadricula=True, estilo='fino')`

Función · módulo `pantalla.vectores`

Dibuja vectores con flechas en unos ejes, cada uno de un color.

```python
pantalla.dibujar_vectores({"u": (3, 2), "v": (-1, 4)})
pantalla.dibujar_vectores([(3, 2), (-1, 4)])                  # se llaman u, v, w...
pantalla.dibujar_vectores({"u": (3, 2), "v": ((3, 2), (2, 6))})   # v empieza en la punta de u
```
Un vector puede ser (x, y), que sale del origen, o ((x0, y0), (x1, y1)): de un punto a otro.
- ancho, alto: lo que ocupa como mucho, contando los números de los ejes.
- cuadricula=False: sin los puntitos de cada unidad.
- estilo="fino" hace las rayas con puntitos braille (⠁⠂⠄⡀), que dejan 8 puntos por letra
  y salen casi rectas. estilo="rayas" las hace con ╱ ╲ │ ─, por si tu terminal no tiene braille.
Sin x ni y, se dibuja donde esté el cursor (como un print). Devuelve (ancho, alto).

### Rectas

#### `pantalla.recta(A, B=None, vector=None, pendiente=None, perpendicular=None, paralela=None)`

Función · módulo `pantalla.rectas`

Hace una recta: por dos puntos, por un punto con un vector o con la pendiente, o escrita.

```python
r = pantalla.recta((1, 3), (2, 5))
r = pantalla.recta((1, 3), vector=(1, 2))
r = pantalla.recta((0, 1), pendiente=2)
r = pantalla.recta("y = 2x + 1")
r = pantalla.recta("2x - y + 1 = 0")
r = pantalla.recta((1, 1), perpendicular="y = 2x")     # por (1, 1) y perpendicular a otra
r = pantalla.recta((1, 1), paralela="y = 2x")
```
Con puntos de tres números (x, y, z) es una recta del espacio:

```python
r = pantalla.recta((1, 2, 3), (2, 2, 5))
r = pantalla.recta((1, 2, 3), vector=(1, 0, 2))
r = pantalla.recta("(x - 1)/2 = (y + 1)/3 = z")       # en continua
r = pantalla.recta("x + y = 3", "z = 1")              # donde se cortan dos planos
r = pantalla.recta((1, 2, 3), perpendicular=pi)       # perpendicular a un plano
```
Devuelve una Recta: print(r) sale la ecuación general (en el espacio, la vectorial),
y tiene r.vectorial(), r.parametricas(), r.continua()...

#### `pantalla.Recta(A, B=None, vector=None, pendiente=None)`

Clase · módulo `pantalla.rectas`

Una recta del plano. Se hace con dos puntos, con un punto y un vector, o con un punto y la pendiente.

r = pantalla.Recta((1, 3), (2, 5))                # pasa por (1, 3) y (2, 5)
r = pantalla.Recta((1, 3), vector=(1, 2))         # por (1, 3) con dirección (1, 2)
r = pantalla.Recta((0, 1), pendiente=2)           # por (0, 1) con pendiente 2
r = pantalla.recta("y = 2x + 1")                  # o escrita

print(r)                  # 2x - y + 1 = 0  (la general)
r.explicita()             # "y = 2x + 1"
r.punto_pendiente()       # "y - 3 = 2(x - 1)"
r.vectorial()             # "(x, y) = (1, 3) + t·(1, 2)"
r.parametricas()          # "x = 1 + t,  y = 3 + 2t"
r.continua()              # "(x - 1)/1 = (y - 3)/2"
r.pendiente, r.ordenada   # 2, 1
r(4)                      # 9: lo que vale y cuando x = 4
r.pasa_por((0, 1))        # True

- `.pendiente` (propiedad): Lo que sube y cuando x avanza 1. None si la recta es vertical.
- `.ordenada` (propiedad): Dónde corta al eje y (la n de y = mx + n). None si la recta es vertical.
- `.pasa_por(P)`: True si el punto P está en la recta.
- `.general()`: La ecuación general (o implícita): ax + by + c = 0.
- `.explicita()`: y = mx + n (o x = k si es vertical).
- `.punto_pendiente()`: y - y₀ = m(x - x₀). Si es vertical no tiene, y sale x = k.
- `.vectorial()`: (x, y) = (x₀, y₀) + t·(v₁, v₂).
- `.parametricas()`: x = x₀ + t·v₁,  y = y₀ + t·v₂.
- `.continua()`: (x - x₀)/v₁ = (y - y₀)/v₂. Si el vector tiene un 0, no se puede escribir así.

#### `pantalla.ecuaciones_recta(A, B=None, vector=None, pendiente=None, x=None, y=None)`

Función · módulo `pantalla.rectas`

Escribe todas las ecuaciones de una recta: vectorial, paramétricas, continua, general,
explícita y punto-pendiente. Devuelve la Recta.

```python
pantalla.ecuaciones_recta((1, 3), (2, 5))
pantalla.ecuaciones_recta(r)                  # o una que ya tengas
pantalla.ecuaciones_recta((1, 2, 3), (2, 2, 5))   # del espacio: vectorial, paramétricas, continua e implícitas
```

#### `pantalla.posicion_rectas(r, s)`

Función · módulo `pantalla.rectas`

Cómo están dos rectas: "secantes" (se cortan en un punto), "paralelas" o "coincidentes".

pantalla.posicion_rectas(pantalla.recta("y = 2x"), pantalla.recta("y = 2x + 1"))   # "paralelas"

#### `pantalla.interseccion_rectas(r, s, pasos=False)`

Función · módulo `pantalla.rectas`

El punto donde se cortan dos rectas, o None si no se cortan (paralelas) o son la misma.

pantalla.interseccion_rectas("y = 2x + 1", "x + y = 4")     # (1, 3)
pantalla.interseccion_rectas(r, s, pasos=True)              # con el sistema

#### `pantalla.distancia_punto_recta(P, r, pasos=False)`

Función · módulo `pantalla.rectas`

La distancia (lo más corta) de un punto a una recta: |a·x₀ + b·y₀ + c| / √(a² + b²).

pantalla.distancia_punto_recta((0, 0), "3x + 4y - 10 = 0")     # 2
pantalla.distancia_punto_recta((1, 1), r, pasos=True)

#### `pantalla.angulo_rectas(r, s)`

Función · módulo `pantalla.rectas`

El ángulo entre dos rectas, en grados (de 0 a 90).

pantalla.angulo_rectas("y = x", "y = -x")      # 90.0

### Espacio (3D)

#### `pantalla.ver_espacio(objetos=None, giro=35, inclinacion=25, tamano=None, caja=True, ejes=True, cortes=True, colores=None, girar=False, estilo='auto')`

Función · módulo `pantalla.visor`

Enseña planos, rectas y puntos en 3D a pantalla completa, para girarlos con el ratón.

```python
pi = pantalla.plano("x + y + z = 3")
r = pantalla.recta((0, 0, 0), vector=(1, 1, 1))
pantalla.ver_espacio({"π": pi, "r": r})
pantalla.ver_espacio()          # vacío: con la n vas añadiendo cosas escritas
```
Arrastra con el ratón (o usa las flechas) para girarlo, + y - para acercar o alejar,
x, y, z para mirarlo desde cada eje, espacio para que gire solo, c quita la caja,
r vuelve a como estaba y Esc sale. Con la n escribes un plano ("x + y = 2"), una recta
("(x - 1)/2 = y = z") o un punto ("(1, 2, 3)") y se añade; la b borra lo último que añadiste.
A la derecha (o debajo) están las ecuaciones y dónde se corta cada cosa.
Lo que vale en objetos y en estilo es lo mismo que en dibujar_espacio(). Fuera de una
terminal (IDLE) lo dibuja quieto, como dibujar_espacio().

#### `pantalla.dibujar_espacio(objetos, x=None, y=None, ancho=60, alto=22, giro=35, inclinacion=25, zoom=1, tamano=None, caja=True, ejes=True, cortes=True, leyenda=True, colores=None, estilo='auto', girar=False)`

Función · módulo `pantalla.visor`

Dibuja planos, rectas, puntos y vectores del espacio, en 3D y dentro de una caja.

```python
pi = pantalla.plano("x + y + z = 3")
r = pantalla.recta((0, 0, 0), vector=(1, 1, 1))
pantalla.dibujar_espacio({"π": pi, "r": r, "P": (1, 1, 1)})
pantalla.dibujar_espacio(["x + y + z = 3", "z = 0"])       # también escritos
pantalla.dibujar_espacio(pi, tamano=(0, 4))                 # solo la parte positiva, como en el libro
```
Valen planos, rectas, puntos (x, y, z), Vectores (flechas desde el origen), parejas de puntos
((x0, y0, z0), (x1, y1, z1)) para una flecha de uno a otro, y listas de 3 o más puntos (un triángulo...).
- estilo: "auto" lo dibuja de verdad (planos rellenos y transparentes) si tu terminal sabe pintar
  imágenes, como Windows Terminal, y si no con puntitos. "puntos" siempre con puntitos braille.
- giro, inclinacion: desde dónde se mira, en grados (giro alrededor del eje z, e inclinacion
  lo alto que está el ojo: 90 es mirar desde arriba).
- zoom: 2 lo ve el doble de grande.
- tamano: hasta dónde llega la caja: 5 es de -5 a 5, y (0, 4) es de 0 a 4 en los tres ejes.
- cortes=True marca con ◆ dónde se cortan las cosas y con una raya blanca dónde se cortan dos planos.
- leyenda=True escribe debajo cada cosa con su ecuación y lo que pasa entre ellas.
- ancho, alto: lo que ocupa el dibujo (la leyenda va debajo).
- girar=True: se puede girar arrastrándolo con el ratón (con cualquier botón) mientras tu
  programa espera algo: un menu(), tecla(), esperar_clic(), bucle()... Así puedes tener, por
  ejemplo, un menú a la izquierda y el dibujo a la derecha. limpiar() lo quita.
Sin x ni y, se dibuja donde esté el cursor (como un print). Devuelve (ancho, alto); con
girar=True devuelve el dibujo, que también vale como (ancho, alto) y tiene .girar(giro, inclinacion)
y .quitar().
Para verlo a pantalla completa y girarlo con el ratón, usa pantalla.ver_espacio().

#### `pantalla.plano(A, B=None, C=None, normal=None, vectores=None, perpendicular=None, paralelo=None)`

Función · módulo `pantalla.espacio`

Hace un plano: escrito, por tres puntos, por un punto y el vector normal, por un punto y dos
vectores, o con rectas.

```python
pi = pantalla.plano("2x - y + z = 3")
pi = pantalla.plano((1, 0, 0), (0, 1, 0), (0, 0, 1))
pi = pantalla.plano((1, 2, 3), normal=(2, -1, 1))
pi = pantalla.plano((1, 2, 3), vectores=[(1, 0, 0), (0, 1, 1)])
pi = pantalla.plano(r, (1, 0, 0))          # una recta y un punto
pi = pantalla.plano(r, s)                  # dos rectas que se cortan o son paralelas
pi = pantalla.plano(r, paralelo=s)         # contiene a r y es paralelo a s
pi = pantalla.plano(P, perpendicular=r)    # por P y perpendicular a r
pi = pantalla.plano(P, paralelo=sigma)     # por P y paralelo a sigma
```
Devuelve un Plano: print(pi) sale la ecuación general, y tiene pi.vectorial(), pi.parametricas()...

#### `pantalla.Plano(A, B=None, C=None, normal=None, vectores=None, perpendicular=None, paralelo=None)`

Clase · módulo `pantalla.espacio`

Un plano del espacio: ax + by + cz + d = 0.

pi = pantalla.plano("2x - y + z = 3")                     # escrito
pi = pantalla.plano((1, 0, 0), (0, 1, 0), (0, 0, 1))      # por tres puntos
pi = pantalla.plano((1, 2, 3), normal=(2, -1, 1))         # por un punto, con el vector normal
pi = pantalla.plano((1, 2, 3), vectores=[(1, 0, 0), (0, 1, 1)])   # un punto y dos vectores
pi = pantalla.plano(r, (1, 0, 0))                         # una recta y un punto fuera de ella
pi = pantalla.plano(r, s)                                 # dos rectas que se cortan o son paralelas
pi = pantalla.plano(r, paralelo=s)                        # contiene a r y es paralelo a s
pi = pantalla.plano(r, perpendicular=sigma)               # contiene a r y es perpendicular a sigma
pi = pantalla.plano(P, perpendicular=r)                   # por P y perpendicular a la recta r
pi = pantalla.plano(P, paralelo=sigma)                    # por P y paralelo al plano sigma

print(pi)                 # 2x - y + z - 3 = 0   (la general)
pi.vectorial()            # "(x, y, z) = (0, 0, 3) + λ·(1, 0, -2) + μ·(0, 1, 1)"
pi.parametricas()         # "x = λ,  y = μ,  z = 3 - 2λ + μ"
pi.punto_normal()         # "2x - y + (z - 3) = 0": con el vector normal y el punto
pi.segmentaria()          # "x/(3/2) + y/(-3) + z/3 = 1": dónde corta a los ejes
pi.normal                 # (2, -1, 1)
pi.pasa_por((1, 0, 1))    # True

- `.normal` (propiedad): El vector normal (perpendicular al plano): (a, b, c).
- `.pasa_por(P)`: True si el punto P está en el plano.
- `.contiene(r)`: True si la recta r está entera dentro del plano.
- `.general()`: La ecuación general (o implícita): ax + by + cz + d = 0.
- `.segmentaria()`: x/a + y/b + z/c = 1, con los puntos donde corta a los ejes (si los corta a los tres).
- `.vectorial()`: (x, y, z) = P + λ·u + μ·v.
- `.parametricas()`: x = x₀ + λu₁ + μv₁,  y = ...,  z = ...
- `.punto_normal()`: a(x - x₀) + b(y - y₀) + c(z - z₀) = 0, con el punto y el vector normal.

#### `pantalla.Recta3D(A, B=None, vector=None, perpendicular=None, paralela=None)`

Clase · módulo `pantalla.espacio`

Una recta del espacio: un punto por el que pasa y un vector que dice hacia dónde va.

r = pantalla.recta((1, 2, 3), (2, 2, 5))              # por dos puntos
r = pantalla.recta((1, 2, 3), vector=(1, 0, 2))       # por un punto con un vector
r = pantalla.recta("(x - 1)/1 = (y - 2)/0 = (z - 3)/2")   # en continua
r = pantalla.recta("x + y = 3", "z = 1")              # donde se cortan dos planos
r = pantalla.recta(P, perpendicular=pi)               # por P y perpendicular al plano pi
r = pantalla.recta(P, paralela=s)                     # por P y paralela a la recta s

print(r)                # (x, y, z) = (1, 2, 3) + t·(1, 0, 2)
r.parametricas()        # "x = 1 + t,  y = 2,  z = 3 + 2t"
r.continua()            # "(x - 1)/1 = (y - 2)/0 = (z - 3)/2"
r.implicitas()          # "y - 2 = 0,  2x - z + 1 = 0"  (dos planos que se cortan en ella)
r.punto, r.vector       # (1, 2, 3), (1, 0, 2)
r(2)                    # el punto que sale con t = 2: (3, 2, 7)
r.pasa_por((2, 2, 5))   # True

- `.pasa_por(P)`: True si el punto P está en la recta.
- `.vectorial()`: (x, y, z) = (x₀, y₀, z₀) + t·(v₁, v₂, v₃).
- `.parametricas()`: x = x₀ + t·v₁,  y = y₀ + t·v₂,  z = z₀ + t·v₃.
- `.continua()`: (x - x₀)/v₁ = (y - y₀)/v₂ = (z - z₀)/v₃. Si el vector tiene un 0, se pone /0 (es una forma de escribirla).
- `.planos()`: Dos planos que se cortan en esta recta (sus implícitas), sacados de la continua.
- `.implicitas()`: Las dos ecuaciones (de dos planos) que la forman: "y - 2 = 0,  2x - z + 1 = 0".

#### `pantalla.Punto(*componentes)`

Clase · módulo `pantalla.espacio`

Un punto. Sale como (1, 2, 3), igual que un Vector, pero al dibujarlo es un punto y no una flecha.

```python
P = pantalla.Punto(1, 2, 3)
Q = P + (1, 0, 0)       # otro punto: (2, 2, 3)
v = Q - P               # restar dos puntos da el Vector que va de uno a otro: (1, 0, 0)
```
Lo que devuelven interseccion(), proyeccion(), simetrico() o punto_medio() son puntos.

#### `pantalla.ecuaciones_plano(A, B=None, C=None, normal=None, vectores=None, perpendicular=None, paralelo=None, x=None, y=None)`

Función · módulo `pantalla.espacio`

Escribe todas las ecuaciones de un plano: vectorial, paramétricas, general, con el vector normal
y la segmentaria (x/a + y/b + z/c = 1, si corta a los tres ejes). Devuelve el Plano.

```python
pantalla.ecuaciones_plano((1, 0, 0), (0, 1, 0), (0, 0, 1))
pantalla.ecuaciones_plano(pi)                 # o uno que ya tengas
```

#### `pantalla.posicion(a, b, c=None, pasos=False)`

Función · módulo `pantalla.espacio`

Cómo están dos cosas del espacio una respecto a la otra (o tres planos).

```python
pantalla.posicion(r, s)        # "coincidentes", "paralelas", "se cortan" o "se cruzan"
pantalla.posicion(r, pi)       # "contenida", "paralela" o "se cortan"
pantalla.posicion(pi, sigma)   # "coincidentes", "paralelos" o "se cortan"
pantalla.posicion(P, pi)       # "está en el plano" o "no está en el plano"
pantalla.posicion(P, r)        # "está en la recta" o "no está en la recta"
pantalla.posicion(pi, sigma, rho)     # tres planos: "se cortan en un punto", "se cortan en una recta"...
pantalla.posicion(r, s, pasos=True)   # con los rangos, como en clase
```
Valen rectas y planos de pantalla.recta() y pantalla.plano(), o escritos: "x + y + z = 3".

#### `pantalla.interseccion(a, b, c=None, pasos=False)`

Función · módulo `pantalla.espacio`

Dónde se cortan: el punto, la recta (si son dos planos) o None si no se cortan.

```python
pantalla.interseccion(r, pi)            # recta y plano: un punto (1, 1, 1)
pantalla.interseccion(pi, sigma)        # dos planos: una recta
pantalla.interseccion(r, s)             # dos rectas: un punto, o None si son paralelas o se cruzan
pantalla.interseccion(pi, sigma, rho)   # tres planos: un punto (o una recta)
pantalla.interseccion(r, pi, pasos=True)   # metiendo las paramétricas en el plano
```
Si una cosa está dentro de la otra (una recta en un plano), devuelve la de dentro.

#### `pantalla.distancia(A, B, pasos=False)`

Función · módulo `pantalla.espacio`

La distancia (la más corta) entre dos cosas: puntos, rectas o planos.

```python
pantalla.distancia((1, 1), (4, 5))              # dos puntos: 5
pantalla.distancia((1, 2, 3), pi)               # de un punto a un plano
pantalla.distancia((1, 2, 3), r)                # de un punto a una recta
pantalla.distancia(r, s)                        # dos rectas (si se cruzan, con el producto mixto)
pantalla.distancia(r, pi)  /  (pi, sigma)       # 0 si se cortan; si son paralelos, la de verdad
pantalla.distancia((0, 0, 0), pi, pasos=True)   # con la fórmula y los números puestos
```
Sale exacta si se puede (5, 1/3) y si no con decimales.

#### `pantalla.angulo(u, v, radianes=False, pasos=False)`

Función · módulo `pantalla.espacio`

El ángulo entre dos vectores, dos rectas, dos planos o una recta y un plano (en grados).

```python
pantalla.angulo((1, 0), (0, 1))           # dos vectores: 90.0
pantalla.angulo(r, s)                     # dos rectas: de 0 a 90
pantalla.angulo(r, pi)                    # una recta y un plano (con el seno)
pantalla.angulo(pi, sigma)                # dos planos (con sus vectores normales)
pantalla.angulo(r, pi, pasos=True)
```
radianes=True para que salga en radianes.

#### `pantalla.proyeccion(a, sobre, pasos=False)`

Función · módulo `pantalla.espacio`

La proyección ortogonal (la "sombra" que cae en perpendicular).

```python
pantalla.proyeccion((1, 2, 3), pi)       # el punto de pi más cerca de (1, 2, 3)
pantalla.proyeccion((1, 2, 3), r)        # el punto de r más cerca
pantalla.proyeccion(r, pi)               # la recta que es la sombra de r en pi
pantalla.proyeccion((2, 3), (1, 0))      # dos vectores: la sombra de u sobre v, (2, 0)
pantalla.proyeccion(P, pi, pasos=True)
```
Con dos vectores hace lo de siempre; con un punto o una recta y un plano (o una recta), da el punto o la recta.

#### `pantalla.simetrico(a, respecto, pasos=False)`

Función · módulo `pantalla.espacio`

El simétrico de un punto respecto de un punto, una recta o un plano (como en un espejo).

pantalla.simetrico((1, 2, 3), (0, 0, 0))     # (-1, -2, -3)
pantalla.simetrico((1, 2, 3), pi)            # al otro lado del plano, a la misma distancia
pantalla.simetrico((1, 2, 3), r)
pantalla.simetrico(r, pi)                    # también rectas y planos: se hace con sus puntos
pantalla.simetrico(P, pi, pasos=True)        # M es el punto medio: P' = 2M - P

#### `pantalla.perpendicular_comun(r, s, pasos=False)`

Función · módulo `pantalla.espacio`

La recta que corta a r y a s y es perpendicular a las dos.

```python
pantalla.perpendicular_comun(r, s)
pantalla.perpendicular_comun(r, s, pasos=True)    # con los dos puntos donde las toca
```
Si r y s son paralelas hay infinitas y devuelve None.

#### `pantalla.punto_medio(A, B)`

Función · módulo `pantalla.espacio`

El punto que está justo en medio de A y B.

pantalla.punto_medio((1, 2, 3), (3, 4, 5))     # (2, 3, 4)

#### `pantalla.plano_mediador(A, B)`

Función · módulo `pantalla.espacio`

El plano de los puntos que están a la misma distancia de A y de B (pasa por el medio y es perpendicular a AB).

pantalla.plano_mediador((0, 0, 0), (2, 0, 0))     # x - 1 = 0

#### `pantalla.area_triangulo(A, B, C, pasos=False)`

Función · módulo `pantalla.espacio`

El área del triángulo ABC: la mitad del módulo de AB × AC (vale en el plano y en el espacio).

pantalla.area_triangulo((0, 0, 0), (2, 0, 0), (0, 2, 0))     # 2
pantalla.area_triangulo(A, B, C, pasos=True)

#### `pantalla.volumen_tetraedro(A, B, C, D, pasos=False)`

Función · módulo `pantalla.espacio`

El volumen del tetraedro ABCD: |[AB, AC, AD]| / 6 (el producto mixto entre 6).

pantalla.volumen_tetraedro((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))     # 1/6

#### `pantalla.estan_alineados(*puntos)`

Función · módulo `pantalla.espacio`

True si todos los puntos están en la misma recta.

pantalla.estan_alineados((0, 0, 0), (1, 1, 1), (2, 2, 2))     # True

#### `pantalla.son_coplanarios(*puntos)`

Función · módulo `pantalla.espacio`

True si todos los puntos están en el mismo plano.

pantalla.son_coplanarios((0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0))     # True

### Polinomios

#### `pantalla.polinomio(texto)`

Función · módulo `pantalla.polinomios`

Hace un polinomio a partir de cómo se escribe en clase.

```python
p = pantalla.polinomio("2x^3 - 3x + 1")
p = pantalla.polinomio("2x³ - 3x + 1")          # también con los numeritos de arriba
p = pantalla.polinomio("x**2 + (1/2)x")         # o como en Python
p = pantalla.polinomio([2, 0, -3, 1])           # o con los coeficientes
```
Devuelve un Polinomio, que se suma, resta y multiplica con + - *.

#### `pantalla.Polinomio(*coeficientes)`

Clase · módulo `pantalla.polinomios`

Un polinomio, como 2x³ - 3x + 1. Se suma, resta y multiplica con + - *, y p(2) lo evalúa.

p = pantalla.Polinomio(2, 0, -3, 1)      # los coeficientes, del grado más alto al más bajo
q = pantalla.polinomio("x^2 - 1")         # o escrito como en clase
print(p + q)          # 2x³ + x² - 3x
print(p(2))           # 11
print(p.grado)        # 3
pantalla.grafica(p, -2, 2)                # como es una función, se puede dibujar

- `.grado` (propiedad): El grado: la potencia más alta de x (el polinomio 0 tiene grado 0).
- `.coeficientes` (propiedad): Los coeficientes, del grado más alto al más bajo: [2, 0, -3, 1] para 2x³ - 3x + 1.
- `.derivada()`: La derivada: 3x² + 2x da 6x + 2.

#### `pantalla.ruffini(p, a, pasos=False, x=None, y=None)`

Función · módulo `pantalla.polinomios`

Divide el polinomio p entre (x - a) con la regla de Ruffini. Devuelve (cociente, resto).

```python
c, r = pantalla.ruffini("2x^3 - 3x + 1", 1)     # 2x² + 2x - 1   y   0
pantalla.ruffini("2x^3 - 3x + 1", 1, pasos=True)
#   │  2  0 -3  1
# 1 │     2  2 -1
# ──┼────────────
#   │  2  2 -1  0
```
Si el resto da 0, a es una raíz del polinomio (y x - a lo divide).
Con x e y, la tabla se dibuja en esa posición.

#### `pantalla.dividir_polinomios(p, q)`

Función · módulo `pantalla.polinomios`

Divide p entre q. Devuelve (cociente, resto), los dos polinomios.

c, r = pantalla.dividir_polinomios("x^3 - 1", "x - 1")
print(c, r)      # x² + x + 1   0

#### `pantalla.raices(p, pasos=False)`

Función · módulo `pantalla.polinomios`

Las raíces reales de un polinomio (los x que lo hacen 0), de la más pequeña a la más grande.

```python
pantalla.raices("x^2 - 5x + 6")          # [2, 3]
pantalla.raices("x^3 - x^2")             # [0, 0, 1]: el 0 sale dos veces (es doble)
pantalla.raices("x^2 - 2")               # [-1.414213562373, 1.414213562373]
pantalla.raices("2x^3 - 3x + 1", pasos=True)   # enseña cada Ruffini
```
Las que son fracciones salen exactas. Las demás, con decimales.

#### `pantalla.factorizar_polinomio(p, pasos=False)`

Función · módulo `pantalla.polinomios`

Escribe el polinomio como producto de factores, sacando las raíces con Ruffini.

```python
pantalla.factorizar_polinomio("x^3 - 2x^2 - x + 2")    # "(x - 1)·(x + 1)·(x - 2)"
pantalla.factorizar_polinomio("2x^2 - 2")              # "2·(x - 1)·(x + 1)"
pantalla.factorizar_polinomio("x^3 - x", pasos=True)   # con cada Ruffini
```
Devuelve el texto. Lo que no se puede partir más con fracciones (como x² + 1) se queda entero.

#### `pantalla.ecuacion_segundo_grado(a, b, c, pasos=False)`

Función · módulo `pantalla.polinomios`

Resuelve a·x² + b·x + c = 0. Devuelve la lista de soluciones (0, 1 o 2).

```python
pantalla.ecuacion_segundo_grado(1, -5, 6)               # [3, 2]
pantalla.ecuacion_segundo_grado(1, -5, 6, pasos=True)
# x² - 5x + 6 = 0
# Δ = b² - 4ac = (-5)² - 4·1·6 = 25 - 24 = 1
# x = (-b ± √Δ) / 2a = (5 ± 1) / 2
# x₁ = 3    x₂ = 2
```
Si el discriminante (Δ) es negativo no hay soluciones y devuelve []. Si da 0, hay una sola.

### Fracciones y números

#### `pantalla.fraccion(numerador, denominador=None)`

Función · módulo `pantalla.numeros`

Hace una fracción, ya simplificada. Con ella las cuentas salen exactas.

```python
f = pantalla.fraccion(3, 4)          # 3/4
f = pantalla.fraccion("3/4")         # lo mismo
f = pantalla.fraccion("1 1/2")       # uno y medio: 3/2
f = pantalla.fraccion(0.75)          # 3/4
print(f + pantalla.fraccion(1, 4))   # 1
print(f.numerator, f.denominator)    # 3 4
```
Se puede sumar, restar, multiplicar y dividir con números normales.

#### `pantalla.pedir_fraccion(pregunta='Escribe una fracción: ', x=None, y=None, color=None)`

Función · módulo `pantalla.numeros`

Pide una fracción (vale 3/4, -2, 0,5 o 1 1/2) y no para hasta que le escribas una que valga.

f = pantalla.pedir_fraccion("Primera fracción: ")
g = pantalla.pedir_fraccion("Segunda fracción: ")
print("La suma es", f + g)

#### `pantalla.calcular(cuenta)`

Función · módulo `pantalla.numeros`

Hace una cuenta escrita como texto, con fracciones exactas.

```python
pantalla.calcular("1/2 + 1/3")          # 5/6
pantalla.calcular("(2 + 3) * 4")        # 20
pantalla.calcular("3/4 : 1/2")          # 3/2   (: y ÷ también dividen)
pantalla.calcular("2^10")               # 1024  (^ es elevar)
pantalla.calcular("0,5 + 1/4")          # 3/4
```
Devuelve un número entero si la cuenta da justa y una fracción si no.
Solo hace sumas, restas, multiplicaciones, divisiones y potencias.

#### `pantalla.escribir_cuenta(cuenta, x=None, y=None, color=None, color_resultado='amarillo', resultado=True)`

Función · módulo `pantalla.numeros`

Dibuja una cuenta con las fracciones en vertical, como en el cuaderno, y su resultado.

```python
pantalla.escribir_cuenta("1/2 + 1/3")              # sale  1   1   5
                                                  #      ─ + ─ = ─
                                                  #      2   3   6
pantalla.escribir_cuenta("3/4 · 2/5", 10, 4)
pantalla.escribir_cuenta("1/2 + 1/3", resultado=False)   # sin el = 5/6
pantalla.escribir_cuenta(pantalla.fraccion(7, 8))        # una fracción sola
```
Si la cuenta ya tiene un =, no la resuelve: la dibuja tal cual.
Sin x ni y, se escribe donde esté el cursor (como un print). Devuelve (ancho, alto).

#### `pantalla.mcd(*numeros)`

Función · módulo `pantalla.numeros`

El máximo común divisor: el número más grande que divide a todos.

pantalla.mcd(12, 18)          # 6
pantalla.mcd(12, 18, 30)      # 6
pantalla.mcd([8, 20])         # 4

#### `pantalla.mcm(*numeros)`

Función · módulo `pantalla.numeros`

El mínimo común múltiplo: el número más pequeño que es múltiplo de todos.

pantalla.mcm(4, 6)            # 12
pantalla.mcm(2, 3, 4)         # 12

#### `pantalla.es_primo(n)`

Función · módulo `pantalla.numeros`

True si el número es primo (solo se puede dividir entre 1 y entre sí mismo).

pantalla.es_primo(7)          # True
pantalla.es_primo(9)          # False

#### `pantalla.divisores(n)`

Función · módulo `pantalla.numeros`

Todos los divisores de un número, de menor a mayor.

pantalla.divisores(12)        # [1, 2, 3, 4, 6, 12]

#### `pantalla.factorizar(n)`

Función · módulo `pantalla.numeros`

Descompone un número en factores primos. Devuelve {primo: cuántas veces}.

```python
pantalla.factorizar(360)      # {2: 3, 3: 2, 5: 1}   porque 360 = 2³ · 3² · 5
```
Para verlo dibujado con la rayita, usa pantalla.descomponer(360).

#### `pantalla.descomponer(n, x=None, y=None, color=None, color_primos='amarillo')`

Función · módulo `pantalla.numeros`

Dibuja la descomposición en factores primos con la rayita, como en clase.

```python
pantalla.descomponer(360)       #  360 │ 2
                                #  180 │ 2
                                #   90 │ 2
                                #   45 │ 3
                                #   15 │ 3
                                #    5 │ 5
                                #    1 │
                                #  360 = 2³ · 3² · 5
```
Devuelve lo mismo que factorizar(): {2: 3, 3: 2, 5: 1}.
Sin x ni y, se escribe donde esté el cursor (como un print).

#### `pantalla.cambiar_base(n, base, pasos=False, x=None, y=None)`

Función · módulo `pantalla.bases`

Pasa un número de decimal a otra base (de 2 a 36). Devuelve el texto con las cifras.

```python
pantalla.cambiar_base(45, 2)                  # "101101"
pantalla.cambiar_base(255, 16)                # "FF"
pantalla.cambiar_base(45, 2, pasos=True)
# 45 : 2 = 22   resto 1
# 22 : 2 = 11   resto 0
# ...
# 45 = 101101₂   (los restos, de abajo arriba)
```
En bases mayores que 10 las cifras siguen con letras: A = 10, B = 11... Con x e y,
los pasos se dibujan en esa posición.

#### `pantalla.a_binario(n, pasos=False, x=None, y=None)`

Función · módulo `pantalla.bases`

Pasa un número a binario (base 2). Devuelve el texto con los ceros y unos.

pantalla.a_binario(45)                # "101101"
pantalla.a_binario(45, pasos=True)    # con las divisiones entre 2

#### `pantalla.a_hexadecimal(n, pasos=False, x=None, y=None)`

Función · módulo `pantalla.bases`

Pasa un número a hexadecimal (base 16, con las cifras 0-9 y A-F).

pantalla.a_hexadecimal(255)           # "FF"

#### `pantalla.a_decimal(texto, base=2, pasos=False, x=None, y=None)`

Función · módulo `pantalla.bases`

Pasa un número escrito en otra base a decimal. Devuelve el número.

pantalla.a_decimal("101101")                 # 45 (en binario si no dices la base)
pantalla.a_decimal("FF", 16)                 # 255
pantalla.a_decimal("0x2F")                   # 47 (con 0b, 0o o 0x ya sabe la base)
pantalla.a_decimal("101101", pasos=True)
# 101101₂ = 1·2⁵ + 0·2⁴ + 1·2³ + 1·2² + 0·2¹ + 1·2⁰ = 32 + 8 + 4 + 1 = 45

### Estadística

#### `pantalla.media(datos)`

Función · módulo `pantalla.estadistica`

La media: se suman todos y se divide entre cuántos hay.

pantalla.media([5, 7, 7, 8])       # 6.75

#### `pantalla.mediana(datos)`

Función · módulo `pantalla.estadistica`

El de en medio cuando están ordenados (con un número par, la media de los dos del medio).

pantalla.mediana([5, 9, 7])         # 7
pantalla.mediana([5, 9, 7, 8])      # 7.5

#### `pantalla.moda(datos)`

Función · módulo `pantalla.estadistica`

El que más se repite. Si hay empate, devuelve la lista de los que empatan.

pantalla.moda([5, 7, 7, 8])                     # 7
pantalla.moda([1, 1, 2, 2, 3])                  # [1, 2]
pantalla.moda(["rojo", "azul", "rojo"])        # "rojo" (vale con textos)

#### `pantalla.varianza(datos, muestra=False)`

Función · módulo `pantalla.estadistica`

La varianza: la media de lo que se separa cada dato de la media, al cuadrado.

pantalla.varianza([2, 4, 4, 4, 5, 5, 7, 9])      # 4
pantalla.varianza(datos, muestra=True)           # dividiendo entre n - 1

#### `pantalla.desviacion(datos, muestra=False)`

Función · módulo `pantalla.estadistica`

La desviación típica: la raíz de la varianza. Dice lo separados que están los datos.

pantalla.desviacion([2, 4, 4, 4, 5, 5, 7, 9])    # 2

#### `pantalla.cuartiles(datos)`

Función · módulo `pantalla.estadistica`

Los tres cuartiles (Q1, Q2, Q3): dejan por debajo el 25 %, el 50 % y el 75 % de los datos.

```python
pantalla.cuartiles([1, 2, 3, 4, 5, 6, 7, 8])     # (2.5, 4.5, 6.5)
```
Se hace como en clase: se mira la posición k·n/4; si sale justa, la media de ese y el siguiente,
y si no, el siguiente.

#### `pantalla.tabla_frecuencias(datos, x=None, y=None, intervalos=None, color=None, color_cabecera='cian')`

Función · módulo `pantalla.estadistica`

Dibuja la tabla de frecuencias: cada valor, cuántas veces sale (fᵢ), las acumuladas (Fᵢ),
la relativa (hᵢ) y el tanto por ciento.

```python
pantalla.tabla_frecuencias([5, 7, 7, 8, 6, 9, 7, 4])
pantalla.tabla_frecuencias(alturas, intervalos=5)        # en 5 intervalos iguales
pantalla.tabla_frecuencias(["rojo", "azul", "rojo"])     # también con textos
```
Devuelve un dict con cuántas veces sale cada valor (o cada intervalo).

#### `pantalla.histograma(datos, x=None, y=None, intervalos=None, alto=10, ancho_barra=3, color='cian', valores=True)`

Función · módulo `pantalla.estadistica`

Dibuja un histograma: una barra de pie por cada valor (o intervalo), tan alta como las veces que sale.

```python
pantalla.histograma([5, 7, 7, 8, 6, 9, 7, 4])
pantalla.histograma(alturas, intervalos=6)                 # junta los datos en 6 intervalos
pantalla.histograma(["rojo", "azul", "rojo"], color="verde")
```
- alto: las filas que ocupa la barra más alta.
- valores=False: sin el número de encima de cada barra.
Sin x ni y, se dibuja donde esté el cursor (como un print). Devuelve (ancho, alto).

#### `pantalla.estadisticas(datos, x=None, y=None, color=None, color_cabecera='cian')`

Función · módulo `pantalla.estadistica`

Saca en una tabla todo de una vez: cuántos hay, media, mediana, moda, desviación, cuartiles...

```python
pantalla.estadisticas([5, 7, 7, 8, 6, 9, 7, 4])
```
Devuelve un dict con todo, por si quieres usarlo: r["media"], r["desviacion"]...

### Imágenes y modelos 3D

#### `pantalla.imagen(ruta, x=None, y=None, ancho=None, alto=None, estilo='auto')`

Función · módulo `pantalla.imagenes`

Enseña una foto o un dibujo (PNG, JPG, GIF, BMP o PPM) en la terminal.

```python
pantalla.imagen("gato.png")                     # donde esté el cursor, como un print
pantalla.imagen("gato.jpg", 5, 2, ancho=40)     # en (5, 2), de 40 columnas de ancho
pantalla.imagen("logo.png", estilo="bloques")   # siempre con medios bloques ▀
```
- ancho, alto: lo que ocupa, en columnas y filas (sin ninguno, lo que quepa sin
  hacerla más grande de lo que es). Nunca se deforma: se hace caber en los dos.
- estilo: "auto" la pinta de verdad si tu terminal sabe (Windows Terminal, WezTerm, kitty,
  iTerm2...) y si no con "bloques" (medios bloques ▀ de colores, vale en casi todas).
  "letras" la hace con letras . : - = + * # % @ de colores, como el arte ASCII de siempre.
Devuelve (ancho, alto): lo que ha ocupado, en columnas y filas.

#### `pantalla.ver_modelo(cosa, giro=None, inclinacion=None, color='cian claro', estilo='auto', girar=False, relieve=0.25)`

Función · módulo `pantalla.modelos`

Enseña un modelo 3D a pantalla completa para girarlo con el ratón (o las flechas).

```python
pantalla.ver_modelo("tetera.obj")
pantalla.ver_modelo("foto.jpg", relieve=0.4)        # la foto en relieve
pantalla.ver_modelo(lambda x, y: math.sin(x) * math.cos(y))
```
Arrastra para girarlo, + y - para acercar o alejar, espacio para que gire solo, r para
volver a como estaba y Esc para salir. Lo que vale como modelo es lo mismo que en
pantalla.modelo(). Fuera de una terminal (IDLE) lo dibuja quieto.

#### `pantalla.dibujar_modelo(cosa, x=None, y=None, ancho=60, alto=22, giro=None, inclinacion=None, zoom=1, color='cian claro', estilo='auto', girar=False, relieve=0.25)`

Función · módulo `pantalla.modelos`

Dibuja un modelo 3D quieto (como un print, o en x, y).

```python
pantalla.dibujar_modelo("tetera.obj")
pantalla.dibujar_modelo(lambda x, y: x**2 + y**2, 40, 2, ancho=50, alto=20)
pantalla.dibujar_modelo("pieza.stl", 40, 2, girar=True)   # y luego se gira con el ratón
```
Lo que vale como modelo es lo mismo que en pantalla.modelo(): un .obj, un .stl, una imagen
(en relieve) o una función f(x, y). giro e inclinacion son desde dónde se mira, en grados.
estilo: "auto" con píxeles si la terminal sabe y si no con medios bloques ▀; "bloques" siempre así.
Con girar=True se puede girar arrastrándolo mientras tu programa espera algo (un menu(), tecla(),
esperar_clic()...), como en dibujar_espacio(). Devuelve (ancho, alto).

#### `pantalla.modelo(cosa, color='cian claro', relieve=0.25, rango=(-3, 3))`

Función · módulo `pantalla.modelos`

Lee un modelo 3D. Vale:

```python
pantalla.modelo("tetera.obj")              # un archivo OBJ (con sus colores si tiene .mtl)
pantalla.modelo("pieza.stl")               # un STL, de los de las impresoras 3D
pantalla.modelo("foto.png", relieve=0.4)   # una imagen en relieve (relieve: lo que sube)
pantalla.modelo(lambda x, y: x * y)        # la superficie z = f(x, y), con x e y en rango
```
color es el de las caras (si el archivo no trae los suyos). Devuelve un Modelo.

#### `pantalla.Modelo(vertices, triangulos, colores, nombre='modelo')`

Clase · módulo `pantalla.modelos`

Un modelo 3D ya leído: vértices, triángulos y el color de cada triángulo.

Lo da pantalla.modelo("tetera.obj") y vale en ver_modelo() y dibujar_modelo().
Tiene .vertices, .triangulos y .nombre; print(m) dice cuántos tiene.

### Gráficas

#### `pantalla.grafica(funcion, desde=-10, hasta=10, x=None, y=None, ancho=50, alto=15, color=None, minimo=None, maximo=None, caracter=None, ejes=True, estilo='fino')`

Función · módulo `pantalla.graficas`

Dibuja la gráfica de una función, con sus ejes.

```python
pantalla.grafica(lambda x: x * x, -5, 5)              # y = x² entre x = -5 y x = 5
pantalla.grafica(math.sin, 0, 2 * math.pi, 3, 2)      # en la columna 3, fila 2

def f(x):
    return 2 * x + 1
pantalla.grafica(f)

pantalla.grafica([math.sin, math.cos], -6, 6)          # varias, cada una de un color
pantalla.grafica([3, 5, 2, 8, 6, 9])                   # una lista de números: los une
```
- minimo, maximo: hasta dónde llega el eje y (si no, se ajusta solo).
- ancho, alto: lo que ocupa en la pantalla, contando los números de los lados.
- estilo="fino" dibuja con puntitos braille (2x4 por letra), así la curva sale suave.
  estilo="puntos" la hace con • (o con el caracter que le digas), como en las versiones de antes.
Los puntos donde la función no existe (como 1/x en x = 0) se dejan en blanco.
Sin x ni y, se dibuja donde esté el cursor (como un print).

#### `pantalla.barras(datos, x=None, y=None, ancho=40, color='verde', colores=None, valores=True, maximo=None)`

Función · módulo `pantalla.graficas`

Dibuja una gráfica de barras tumbadas, cada una con su nombre.

```python
pantalla.barras({"Ana": 8.5, "Luis": 6, "Marta": 9.75})
pantalla.barras([("Lunes", 3), ("Martes", 7)], 5, 3, color="cian")
pantalla.barras([4, 8, 2])                         # sin nombres: 1, 2, 3
pantalla.barras(notas, colores=["rojo", "amarillo", "verde"])   # un color para cada una
```
- ancho: lo que ocupa todo, contando los nombres y los números.
- maximo: el número que llena la barra entera (si no, el más grande de todos).
- valores=False: sin el número al final de cada barra.
Sin x ni y, se dibuja donde esté el cursor (como un print).

#### `pantalla.minigrafica(valores, minimo=None, maximo=None)`

Función · módulo `pantalla.graficas`

Devuelve una gráfica pequeñita de una línea, para meterla en un print.

print("Temperaturas:", pantalla.minigrafica([12, 15, 19, 22, 18, 14]))
# Temperaturas: ▁▃▆█▅▂

### Practicar

#### `pantalla.practicar(tema=None, preguntas=5, nivel=1, semilla=None)`

Función · módulo `pantalla.ejercicios`

Te pone ejercicios del tema que digas, corrige cada respuesta y al final te da la nota.

```python
pantalla.practicar("tablas")
pantalla.practicar("fracciones", 10, nivel=2)
pantalla.practicar()                          # te pregunta el tema
```
Temas: tablas, sumas, divisiones, fracciones, potencias, raices, ecuaciones, mcd, primos,
binario, porcentajes y vectores (pantalla.lista_temas() te los da).
- nivel: 1, 2 o 3 (más difícil).
- semilla: un número para que salgan siempre los mismos ejercicios.
Escribe "salir" para acabar antes. Devuelve cuántas has acertado.

#### `pantalla.lista_temas()`

Función · módulo `pantalla.ejercicios`

Los temas que hay para practicar().

print(pantalla.lista_temas())     # ['tablas', 'sumas', 'divisiones', 'fracciones', ...]

### Ratón

#### `pantalla.activar_raton(hover=False)`

Función · módulo `pantalla.raton`

Activa el ratón en la terminal. Después puedes usar esperar_clic() y las demás.

```python
pantalla.activar_raton()            # solo clics
pantalla.activar_raton(hover=True)  # clics y movimiento (para resaltar cosas)
```
Devuelve True si hay ratón y False si no se puede (por ejemplo, en IDLE).
Cuando acabes, llama a desactivar_raton(). Si se te olvida, se hace solo al cerrar.

#### `pantalla.desactivar_raton()`

Función · módulo `pantalla.raton`

Desactiva el ratón. La terminal vuelve a funcionar normal.

#### `pantalla.esperar_clic(arrastrar=False)`

Función · módulo `pantalla.raton`

Espera a que hagas clic con el ratón y te dice dónde y con qué botón.

Devuelve (x, y, boton). El botón puede ser "izquierdo", "derecho" o "central".
Las posiciones empiezan en 1, como en gotoxy.

```python
x, y, boton = pantalla.esperar_clic()
pantalla.escribir("Has hecho clic en %d, %d" % (x, y), 1, 1)
```
Con arrastrar=True también vuelve cuando mueves el ratón con el botón pulsado
(mira leer_raton()). Si el ratón no estaba activado, lo activa mientras espera.
Fuera de una terminal de verdad (IDLE) no hay ratón y devuelve None.

#### `pantalla.leer_raton(arrastrar=False)`

Función · módulo `pantalla.raton`

Mira si hay un clic del ratón SIN esperar. Devuelve (x, y, boton) o None.

Como tecla_pulsada() pero para el ratón. Útil en bucles de juegos:

```python
pantalla.activar_raton()
while True:
    clic = pantalla.leer_raton()
    if clic:
        x, y, boton = clic
        pantalla.punto(x, y, "X", color="rojo")
    if pantalla.tecla_pulsada() == "esc":
        break
    pantalla.pausa(0.05)
```
Para pintar arrastrando (como un lápiz), usa arrastrar=True: también te da
(x, y, boton) por cada casilla que pisas con el botón pulsado.

```python
clic = pantalla.leer_raton(arrastrar=True)
if clic:
    pantalla.punto(clic[0], clic[1], "█")   # clic.arrastrando: True si es arrastrando
```
Necesitas llamar a activar_raton() antes. Las teclas que se pulsen mientras
tanto no se pierden: te las da tecla_pulsada().

#### `pantalla.posicion_raton()`

Función · módulo `pantalla.raton`

Devuelve (x, y) de dónde está el ratón, o None si todavía no se sabe.

Necesitas activar_raton(hover=True) para que funcione.

```python
pantalla.activar_raton(hover=True)
pos = pantalla.posicion_raton()
if pos:
    x, y = pos
```
Los clics que pasen mientras tanto no se pierden: luego te los da leer_raton().

#### `pantalla.zona(x, y, ancho, alto, al_clic=None, al_hover=None, al_salir=None)`

Función · módulo `pantalla.raton`

Crea una zona interactiva (un rectángulo invisible que reacciona al ratón).

```python
def al_pulsar():
    pantalla.mensaje("¡Pulsado!")

z = pantalla.zona(10, 5, 20, 3, al_clic=al_pulsar)
pantalla.bucle([z])
```
- al_clic: se llama cuando haces clic dentro.
- al_hover: se llama cuando el ratón entra.
- al_salir: se llama cuando el ratón sale.

#### `pantalla.boton(texto, x, y, color='blanco', fondo='azul', color_hover='negro', fondo_hover='amarillo', al_clic=None)`

Función · módulo `pantalla.raton`

Dibuja un botón que se puede pulsar con el ratón.

```python
def saludar():
    pantalla.mensaje("¡Hola!")

btn = pantalla.boton("Pulsar aquí", 10, 5, al_clic=saludar)
pantalla.bucle([btn])
```
El botón cambia de color cuando pasas el ratón por encima.
Devuelve una zona que puedes usar con bucle().

#### `pantalla.botones(opciones, x=None, y=None, horizontal=True, color='blanco', fondo='azul', color_hover='negro', fondo_hover='amarillo', separacion=2)`

Función · módulo `pantalla.raton`

Enseña varios botones y espera a que hagas clic en uno. Devuelve su texto.

```python
opcion = pantalla.botones(["Jugar", "Opciones", "Salir"], 10, 5)
if opcion == "Jugar":
    ...
```
También vale el teclado: flechas (o Tab) para moverte, Enter para elegir,
o el número del botón (1, 2, 3...). Esc sale sin elegir (devuelve None).

- horizontal: True para ponerlos en fila, False para ponerlos en columna.
- separacion: espacio entre los botones (en columna, filas de separación + 1).

#### `pantalla.bucle(zonas, al_tecla=None)`

Función · módulo `pantalla.raton`

Bucle de eventos: lee el ratón y el teclado y llama a lo que toque.

Pásale una lista de zonas (hechas con zona() o boton()). Acaba cuando:
- al_clic o al_tecla devuelven algo que no sea None ni False (y bucle lo devuelve)
- se pulsa Esc (si no hay al_tecla)

```python
btn1 = pantalla.boton("Aceptar", 10, 10, al_clic=lambda: "aceptar")
btn2 = pantalla.boton("Cancelar", 25, 10, al_clic=lambda: "cancelar")
eleccion = pantalla.bucle([btn1, btn2])
```
Con al_tecla puedes responder al teclado a la vez:

```python
def mi_tecla(t):
    if t == "q":
        return "salir"
pantalla.bucle([btn1], al_tecla=mi_tecla)
```

### Diseñar y ver posiciones

#### `pantalla.diseno(fuente, x=1, y=1, centrado=False)`

Función · módulo `pantalla.disenos`

Dibuja una pantalla diseñada con el constructor web de pantalla.

En el constructor pulsas "Copiar diseño" y lo pegas así:

```python
zonas = pantalla.diseno('''{"pantalla": 1, "ancho": 80, ...}''')
```
También vale el nombre de un archivo .json descargado del constructor:

```python
zonas = pantalla.diseno("menu.json")
```
Devuelve un diccionario con la posición (x, y) de cada cosa a la que le
pusiste nombre en el constructor. Así puedes escribir encima desde tu programa:

```python
pantalla.escribir(puntos, *zonas["puntos"])
x, y = zonas["vidas"]
```
Con centrado=True, el diseño se coloca en el centro de tu terminal.

#### `pantalla.regla(color='gris')`

Función · módulo `pantalla.herramientas`

Dibuja los números de las columnas arriba y los de las filas a la izquierda.

Sirve para saber en qué x e y está cada cosa mientras diseñas una pantalla.

```python
pantalla.limpiar()
pantalla.regla()
pantalla.caja(10, 5, 20, 6)   # ¿la caja empieza donde creías?
```

#### `pantalla.depurar()`

Función · módulo `pantalla.herramientas`

Abre una herramienta para ver las posiciones de la pantalla.

Mueves una cruz con las flechas y te dice en qué x e y está, cuánto mide
la pantalla y qué tecla has pulsado. Con Enter dejas una marca, para
apuntar varios sitios. Al salir (Esc) todo vuelve a estar como antes.

```python
pantalla.depurar()
```
También se abre desde la terminal con:  python -m pantalla depurar

### Otras clases y ayuda

#### `pantalla.ayuda(funcion=None)`

Función · módulo `pantalla`

Enseña todas las funciones de pantalla, o la explicación de una.

```python
pantalla.ayuda()            # en una terminal: un menú para ir mirándolas
pantalla.ayuda("caja")      # cómo se usa caja
pantalla.ayuda(pantalla.caja)
```
Fuera de una terminal (por ejemplo en IDLE), escribe la lista entera.

#### `pantalla.Spinner(texto='', estilo='dots', color='cian', color_texto=None, x=None, y=None, intervalo=None)`

Clase · módulo `pantalla.spinners`

Un spinner. Créalo con pantalla.spinner(...); mira su ayuda.

- `.empezar()`: Empieza a girar (en segundo plano: tu programa sigue). Devuelve el spinner.
- `.girando` (propiedad): True mientras el spinner está dando vueltas.
- `.parar()`: Lo para y lo borra (no deja nada escrito).
- `.bien(texto=None)`: Lo para y deja '✔ texto' en verde.
- `.mal(texto=None)`: Lo para y deja '✖ texto' en rojo.
- `.aviso(texto=None)`: Lo para y deja '⚠ texto' en amarillo.
- `.info(texto=None)`: Lo para y deja 'ℹ texto' en azul.
- `.dejar(simbolo, texto=None, color=None)`: Lo para y deja tu símbolo: s.dejar("★", "¡Récord!", color="amarillo").

#### `pantalla.PantallaDeCarga(titulo='Cargando', total=100, estilo='suave', color='cian', color_final=None, ancho=40, fuente=None, spinner='dots', consejos=None, marco=None, color_titulo=None, borrar=True)`

Clase · módulo `pantalla.cargas`

Una pantalla de carga. Créala con pantalla.pantalla_de_carga(...); mira su ayuda.

- `.valor` (propiedad): Por dónde va (de 0 a total).
- `.avanzar(cuanto=1, texto=None)`: Avanza la barra (1 si no dices cuánto) y, si quieres, cambia el texto de debajo.

  ```
  carga.avanzar()
  carga.avanzar(10, "Cargando sonidos")
  ```
- `.poner_texto(texto)`: Cambia lo que pone debajo de la barra (también vale carga.texto = "...").
- `.empezar()`: Saca la pantalla de carga. pantalla_de_carga() ya lo hace sola.
- `.terminar(texto='Listo')`: Llena la barra, enseña "✔ Listo" un momento y la quita (con borrar=False la deja).
- `.parar()`: La quita sin llenar la barra.

#### `pantalla.Fraccion(numerator=0, denominator=None, *, _normalize=True)`

Clase · módulo `pantalla.numeros`

Una fracción que al hacer print sale como 3/4 (y no como Fraction(3, 4)).


## Manual de uso (README del proyecto)

### Instalar

```
pip install pantalla
```

Para ver todo lo que hace, abre una demostración:

```
python -m pantalla
```

Y desde Python, `pantalla.ayuda()` abre un menú con todas las funciones: eliges una con las flechas y te enseña cómo se usa. `pantalla.ayuda("caja")` te lo dice directamente de una.

### Dónde funciona

En cualquier terminal de verdad: **cmd**, **PowerShell**, **Windows Terminal**, la terminal de **VS Code**, la de Linux o la de Mac.

Las fotos de `imagen()` y los dibujos 3D salen con píxeles de verdad en las terminales que saben pintar imágenes: **Windows Terminal**, **WezTerm**, **kitty**, **Ghostty**, **iTerm2**, **foot**, **Konsole** o **xterm** con Sixel. En **cmd**, la **Terminal del Mac** y las demás salen con bloques ▀ de colores o con puntitos braille, sin que tengas que cambiar nada. Si tu terminal sí sabe y no sale, pon `PANTALLA_IMAGENES=1` (o `kitty`); con `PANTALLA_IMAGENES=0` no lo intenta nunca.

**IDLE** no es una terminal. En Windows, si pulsas F5 en IDLE, pantalla abre tu programa en una ventana de cmd y lo ejecuta allí (si no quieres que lo haga, pon la variable de entorno `PANTALLA_NO_ABRIR=1`). En Linux y Mac, ejecútalo desde la terminal. En **Thonny**, usa *Ejecutar → Ejecutar el script actual en terminal*.

### Cómo funcionan las posiciones

La pantalla es una cuadrícula de letras. `x` es la columna (hacia la derecha) e `y` la fila (hacia abajo). **Las dos empiezan en 1**: la esquina de arriba a la izquierda es `(1, 1)`.

```
(1,1) ──────────── x ───────────▶ (80,1)
  │
  │       pantalla.gotoxy(10, 3)
  y                 ▼
  │                 aquí
  ▼
(1,24)                            (80,24)
```

`pantalla.ancho()` y `pantalla.alto()` te dicen cuánto mide la tuya. Si haces cuentas como `pantalla.ancho() / 2` y te sale un número con decimales, no pasa nada: se redondea solo.

**¿No sabes en qué posición está algo?** Escribe en la terminal `python -m pantalla depurar`: sale una cruz que mueves con las flechas y te dice su `x` y su `y` (y el `gotoxy` que tienes que escribir). Dentro de tu programa, `pantalla.regla()` pinta los números de las columnas y las filas en los bordes.

### Todo lo que hay

[Pantalla y cursor](https://github.com/phernandez102/pantalla#pantalla-y-cursor) · [Escribir](https://github.com/phernandez102/pantalla#escribir) · [Colores](https://github.com/phernandez102/pantalla#colores) · [Dibujar](https://github.com/phernandez102/pantalla#dibujar) · [Teclado](https://github.com/phernandez102/pantalla#teclado) · [Cosas ya hechas](https://github.com/phernandez102/pantalla#cosas-ya-hechas) · [Barras y pantallas de carga](https://github.com/phernandez102/pantalla#barras-y-pantallas-de-carga) · [Ratón](https://github.com/phernandez102/pantalla#ratón) · [Matrices](https://github.com/phernandez102/pantalla#matrices) · [Vectores](https://github.com/phernandez102/pantalla#vectores) · [Rectas](https://github.com/phernandez102/pantalla#rectas) · [Polinomios](https://github.com/phernandez102/pantalla#polinomios) · [Fracciones y números](https://github.com/phernandez102/pantalla#fracciones-y-números) · [Estadística](https://github.com/phernandez102/pantalla#estadística) · [Gráficas](https://github.com/phernandez102/pantalla#gráficas) · [Practicar](https://github.com/phernandez102/pantalla#practicar) · [Récords y tiempo](https://github.com/phernandez102/pantalla#récords-y-tiempo)

`pantalla.ayuda()` abre un menú con todas, y si escribes mal un nombre el error te dice cuál querías.

#### Pantalla y cursor

| Función | Qué hace |
|---|---|
| `limpiar()` | Borra la pantalla |
| `limpiar_linea(y)` | Borra una línea |
| `gotoxy(x, y)` | Mueve el cursor (también se llama `ir_a`) |
| `ancho()`, `alto()`, `tamano()` | Lo que mide la terminal |
| `centro()` | Devuelve `(x, y)` del centro |
| `ocultar_cursor()`, `mostrar_cursor()` | Esconde o enseña el cursor |
| `guardar_posicion()`, `volver_a_posicion()` | Apunta dónde está el cursor y vuelve luego |
| `titulo_ventana("Mi juego")` | Cambia el título de la ventana |
| `pitido()` | Bip |
| `pausa(0.5)` | Espera medio segundo |
| `iniciar()`, `terminar()` | Prepara la terminal para un juego y la deja como estaba |
| `regla()` | Pinta los números de columnas y filas, para ver posiciones |
| `depurar()` | Herramienta para ver posiciones moviendo una cruz con las flechas |

#### Escribir

```python
pantalla.escribir("Hola", 10, 5)                                  # columna 10, fila 5
pantalla.escribir("Peligro", 10, 6, color="rojo", negrita=True)
pantalla.escribir("Puntos: 120", 1, 1, color="negro", fondo="amarillo")
pantalla.escribir("Centrado", "centro", 5)                         # centrado en la fila 5
pantalla.centrar("GAME OVER", color="rojo")                        # en el centro de la pantalla
pantalla.centrar("Pulsa una tecla", y=20)                          # centrado en la fila 20
pantalla.escribir_derecha("Vidas: 3", 1)                           # pegado a la derecha
pantalla.escribir_lento("Había una vez...", 5, 3, velocidad=0.08)  # letra a letra
pantalla.grande("HOLA", color="amarillo")                          # letras gigantes
print(pantalla.texto_grande("FIN"))                                # letras gigantes con print
pantalla.cabecera("MATRICES · Suma")                               # barra con título arriba
pantalla.pie("↑↓ moverse   Enter elegir   Esc salir")              # texto en la última fila
```

Si el texto tiene varias líneas (con `\n`), todas empiezan en la misma columna, así que puedes hacer dibujos:

```python
pantalla.escribir(" /\\_/\\\n( o.o )\n > ^ <", 30, 10, color="naranja")
```

Estilos que puedes poner a cualquier texto: `negrita`, `tenue`, `cursiva`, `subrayado`, `parpadeo`, `invertido` y `tachado`.

##### Fuentes ASCII art

`grande()` y `texto_grande()` tienen `fuente=`, con 32 fuentes FIGlet (las mismas de las webs de "texto a ASCII art"). Sin fuente usa `"bloques"`, la de siempre.

```python
pantalla.grande("Hola", fuente="slant", color="cian")
print(pantalla.texto_grande("Hola", fuente="standard"))
print(pantalla.lista_fuentes())     # ['bloques', '3-d', 'ansi_regular', 'ansi_shadow', ...]
```

```
    __  __      __            _   _       _
   / / / /___  / /___ _      | | | | ___ | | __ _
  / /_/ / __ \/ / __ `/      | |_| |/ _ \| |/ _` |
 / __  / /_/ / / /_/ /       |  _  | (_) | | (_| |
/_/ /_/\____/_/\__,_/        |_| |_|\___/|_|\__,_|
   fuente="slant"            fuente="standard"

 █████╗ ███╗   ██╗███████╗██╗
██╔══██╗████╗  ██║██╔════╝██║
███████║██╔██╗ ██║███████╗██║
██╔══██║██║╚██╗██║╚════██║██║
██║  ██║██║ ╚████║███████║██║
╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝
        fuente="ansi_shadow"
```

El nombre vale en mayúsculas o con espacios (`"ANSI Shadow"`). Si una letra no está en la fuente se usa la misma sin tilde (á → a), y si tampoco está, se salta.

#### Colores

Los colores se escriben en español, con o sin tildes y mayúsculas:

`negro`, `rojo`, `verde`, `amarillo`, `azul`, `morado`, `cian`, `gris claro`, `gris`, `rojo claro`, `verde claro`, `amarillo claro`, `azul claro`, `morado claro`, `cian claro`, `blanco`, `naranja`, `marrón`, `rosa`.

También valen en hexadecimal (`"#ff8800"`), en RGB (`(255, 136, 0)`) o con un número del 0 al 255.

```python
print("Esto es", pantalla.colorear("importante", "rojo", negrita=True))

pantalla.poner_color("verde")        # a partir de aquí todo sale en verde, también con print
print("Verde")
pantalla.quitar_color()              # vuelta a lo normal

pantalla.poner_color(fondo="azul")
pantalla.limpiar()                   # ¡toda la pantalla azul!
```

#### Dibujar

```python
pantalla.rodear()                                    # borde alrededor de toda la pantalla
pantalla.rodear("=")                                 # con =
pantalla.rodear("*", color="amarillo", titulo="Mi juego")

pantalla.caja(5, 3, 30, 10)                          # x, y, ancho, alto
pantalla.caja(5, 3, 30, 10, estilo="doble", color="cian", titulo="Inventario")
pantalla.caja(5, 3, 30, 10, relleno=True)            # borra lo que haya dentro
pantalla.caja(ancho=40, alto=8, titulo="Aviso")      # sin x ni y: en el centro

pantalla.linea(12)                                   # línea horizontal en la fila 12
pantalla.linea(12, "-", x=5, largo=20, color="gris")
pantalla.linea_vertical(40)                          # línea vertical en la columna 40
pantalla.rellenar(10, 5, 20, 4, fondo="azul")        # un rectángulo de color
pantalla.rellenar(10, 5, 20, 4)                      # borra esa zona
pantalla.punto(10, 5, "@", color="amarillo")         # un solo carácter
```

Estilos de borde: `"simple"` ┌─┐, `"doble"` ╔═╗, `"grueso"` ┏━┓, `"redondo"` ╭─╮, `"ascii"` +-+ o cualquier carácter, como `"="` o `"#"`.

##### Arte ASCII (con colores)

`arte()` dibuja un dibujo hecho con letras. Los espacios son transparentes (no borran lo de debajo):

```python
gato = r'''
 /\_/\
( o.o )
 > ^ <
'''
pantalla.arte(gato, 10, 5, color="amarillo")
```

Para darle color a cada letra, pásale otro dibujo del mismo tamaño con una letra de color en cada sitio:

```python
pantalla.arte(["(^_^)", "/| |\\"], 5, 5,
              colores=["aaaaa",
                       "vv vv"])
```

Códigos: `r` rojo, `v` verde, `a` amarillo, `z` azul, `m` morado, `c` cian, `b` blanco, `n` negro, `g` gris, `o` naranja, `x` marrón, `p` rosa; en mayúscula la versión "claro" (`R` rojo claro, `G` gris claro...). Un espacio o un punto deja el color normal. `fondos=` funciona igual para el fondo. Con `transparente=False` los espacios sí borran. Están en `pantalla.CODIGOS_COLOR`.

El constructor web convierte imágenes en arte ASCII y te da el código de `arte()` ya hecho.

#### Teclado

```python
t = pantalla.tecla()            # espera a que pulses una tecla (sin Enter)
if t == "arriba":
    ...

nombre = pantalla.pedir("¿Cómo te llamas? ")                          # como input()
nombre = pantalla.pedir("Nombre: ", 10, 5, color="cian")              # en una posición
edad = pantalla.pedir_numero("Edad: ", minimo=0, maximo=120)          # insiste hasta que sea un número
precio = pantalla.pedir_numero("Precio: ", decimales=True)            # vale 2,5 y 2.5
clave = pantalla.pedir_contrasena()                                   # no se ve lo que escribes
if pantalla.confirmar("¿Quieres salir? (s/n) "):                      # True o False
    ...
pantalla.esperar()                                                    # "Pulsa una tecla para continuar..."
```

`tecla()` devuelve las letras tal cual (`"a"`, `"A"`, `"ñ"`, `"7"`) y estos nombres para las especiales:

`"arriba"`, `"abajo"`, `"izquierda"`, `"derecha"`, `"enter"`, `"espacio"`, `"esc"`, `"tab"`, `"borrar"`, `"suprimir"`, `"insertar"`, `"inicio"`, `"fin"`, `"repag"`, `"avpag"`, `"f1"` … `"f12"`, `"ctrl+a"` … y `"alt+x"` …

#### Cosas ya hechas

```python
opcion = pantalla.menu(["Jugar", "Opciones", "Salir"], titulo="Menú")   # con flechas y Enter
if opcion == "Jugar":
    ...

pantalla.mensaje("¡Has ganado!", titulo="Enhorabuena", color_borde="verde")
dificultad = pantalla.elegir("Dificultad:", ["Fácil", "Normal", "Difícil"])   # opciones en fila, con ← →

pantalla.tabla([["Ana", 8.5], ["Luis", 6]], cabeceras=["Nombre", "Nota"])

juegos = pantalla.elegir_varios(["Ajedrez", "Damas", "Parchís"], titulo="¿A qué juegas?")   # se marcan con Espacio
datos = pantalla.formulario({"Nombre": "texto", "Edad": "numero", "Contraseña": "contraseña"})
print(datos["Nombre"], datos["Edad"])
```

- `menu()` devuelve el texto de la opción elegida (o `None` si pulsas Esc). También se puede elegir pulsando el número. Si hay más opciones de las que caben, el menú hace scroll.
- `elegir_varios()` devuelve la lista de lo que has marcado y `formulario()` un diccionario con lo que has escrito en cada casilla (los dos `None` si pulsas Esc).
- En el formulario cada casilla puede ser `"texto"`, `"numero"`, `"decimal"`, `"fraccion"` o `"contraseña"`.

##### Menús con ayuda, iconos y secciones

```python
opcion = pantalla.menu(
    ["Jugar", "Opciones", "Salir"],
    ayudas={"Jugar": "Empieza una partida nueva", "Salir": "Cierra el juego"},   # sale debajo
    iconos={"Jugar": "►", "Opciones": "*", "Salir": "×"},
)

# la explicación también puede ir en otro sitio, por ejemplo abajo del todo:
AYUDA = {"Jugar": "Empieza una partida nueva", "Salir": "Cierra el juego"}
opcion = pantalla.menu(["Jugar", "Salir"], ayudas=AYUDA,
                       ayuda_x=3, ayuda_y=pantalla.alto() - 2, color_ayuda="cian")
```

Si le das un **diccionario** en vez de una lista, hace un menú con cada sección en su caja y en columnas, como el de un programa de verdad. Te mueves con las cuatro flechas:

```python
opcion = pantalla.menu({
    "Operaciones": ["Sumar", "Restar", "Multiplicar"],
    "Determinantes": ["Determinante", "Inversa"],
    "Otros": ["Historial", "Ajustes", "Salir"],
}, ayudas={"Sumar": "Suma dos matrices del mismo tamaño"})
```

#### Barras y pantallas de carga

<table>
<tr>
<td valign="top" width="42%"><img src="https://raw.githubusercontent.com/phernandez102/pantalla/main/.github/img/barras.svg" alt="Los diez estilos de barra_progreso() y una barra con color_final"></td>
<td valign="top" width="58%"><img src="https://raw.githubusercontent.com/phernandez102/pantalla/main/.github/img/carga.svg" alt="Una pantalla de carga con el título en letras grandes, la barra, el paso que está haciendo y un consejo"></td>
</tr>
<tr>
<td align="center"><sub><code>barra_progreso(estilo=...)</code></sub></td>
<td align="center"><sub><code>pantalla_de_carga()</code></sub></td>
</tr>
</table>

`barra_progreso()` dibuja una barra en un sitio. Para que avance, la vuelves a llamar con otro valor:

```python
for i in range(101):
    pantalla.barra_progreso(i, 100, 10, 5)        # valor, total, columna, fila
    pantalla.pausa(0.02)

pantalla.barra_progreso(40, 100, 10, 7, estilo="suave", color="cian")
pantalla.barra_progreso(vida, 100, 2, 1, color="rojo", color_final="verde", texto="Vida")
```

Los estilos son los de la imagen: `"bloques"` (el normal), `"suave"`, `"linea"`, `"ascii"`, `"puntos"`, `"cuadros"`, `"circulos"`, `"rombos"`, `"flechas"` y `"rayas"`. Dos detalles:

- `"suave"` avanza de octavo en octavo de casilla, así que se mueve sin saltos aunque la barra sea corta.
- `"ascii"` (`[=====>    ]`) solo usa letras normales: sale bien en cualquier terminal, también en las antiguas.

Y más opciones:

- `color_final=`: la barra va cambiando de `color` a este, casilla a casilla. Vale con nombres, `"#rrggbb"` o `(r, g, b)`.
- `lleno=` y `vacio=`: tus propios caracteres, que mandan sobre los del estilo.
- `texto=`: un nombre delante de la barra. `porcentaje=False` quita el número.
- Sin x ni y, la barra sale donde esté el cursor, y cada llamada la sobrescribe en la misma línea.
- `pantalla.lista_barras()` te da todos los estilos.

##### Pantallas de carga

`pantalla_de_carga()` limpia la terminal y pone en el centro un título, la barra, lo que se está haciendo y, si quieres, consejos que van cambiando. Al acabar enseña ✔ Listo y la borra. Hay tres formas de usarla, de la más fácil a la más completa:

```python
# 1. de mentira: tarda 3 segundos y se va (queda bien antes de empezar un juego)
pantalla.pantalla_de_carga("Cargando nivel 1", segundos=3)

# 2. con tareas: un texto es un paso de mentira y una función se llama de verdad
mapa, enemigos = pantalla.pantalla_de_carga("Preparando", tareas=[
    ("Leyendo el mapa", leer_mapa),
    ("Colocando enemigos", colocar_enemigos),
    "Afinando los sonidos",
])

# 3. tú mueves la barra, con with
with pantalla.pantalla_de_carga("Descargando", total=len(archivos)) as carga:
    for archivo in archivos:
        carga.avanzar(texto=archivo)       # suma 1 y cambia el texto de debajo
        descargar(archivo)
```

Con tareas devuelve lo que devuelvan tus funciones, en el mismo orden. Con `with`, además de `avanzar()` puedes poner `carga.valor = 7` o `carga.texto = "Casi está"`.

Para dejarla a tu gusto:

```python
pantalla.pantalla_de_carga(
    "NIVEL 2", segundos=4,
    fuente="ansi_shadow",                    # el título en letras grandes
    estilo="suave", color="cian", color_final="morado claro",
    consejos=["Consejo: los asteroides grandes se parten en dos", "Pulsa P para pausar"],
    marco="redondo",                         # un borde alrededor
)
```

- `total=None`: para cuando no sabes cuánto falta. Un trozo de barra va y viene.
- `spinner=`: la ruedecita de al lado del texto. Vale cualquier estilo de `lista_spinners()`, o `None` para quitarla.
- `borrar=False`: la deja en la pantalla al acabar.
- Los consejos cambian cada 4 segundos. Si las letras grandes no caben en la terminal, pone el título normal.
- La animación va en un hilo aparte, así que sigue moviéndose aunque tu función tarde. Úsala antes de `jugar()`, no dentro: dentro de un juego, dibuja una `barra_progreso()` en cada fotograma.
- En IDLE, sin terminal de verdad, escribe los pasos uno debajo de otro.

##### Spinners (la ruedecita que gira mientras trabajas)

Como la librería [halo](https://github.com/manrajgrover/halo): gira sola mientras tu programa sigue.

```python
with pantalla.spinner("Descargando..."):       # al acabar pone ✔ (o ✖ si hay un error)
    descargar_todo()

s = pantalla.spinner("Paso 1", estilo="arco", color="amarillo").empezar()
s.texto = "Paso 2"                             # cambia el texto mientras gira
s.bien("Hecho")                                # ✔ Hecho   (también mal(), aviso(), info(), parar())

pantalla.spinner("Guardando", x=10, y=5)       # en un sitio fijo de la pantalla
pantalla.lista_spinners()                      # los ~60 estilos: "dots", "line", "arc", "pelota", "tiburon"...
```

Sin terminal de verdad (IDLE) no gira: escribe el texto una vez y luego el final.

Y dos más sencillas, que esperan un rato y siguen:

```python
pantalla.cargando(3, "Guardando partida")    # "Cargando..." en la línea donde estés, durante 3 segundos
pantalla.calculando()                        # ventanita de "Calculando..." en el centro
```

#### Ratón

```python
pantalla.activar_raton(hover=True)             # hover=True: también se entera de cuándo mueves el ratón

opcion = pantalla.botones(["Jugar", "Opciones", "Salir"])   # botones que se pulsan con clic (o flechas + Enter)

x, y, boton = pantalla.esperar_clic()          # espera un clic; boton es "izquierdo", "derecho" o "central"
clic = pantalla.leer_raton()                   # como tecla_pulsada(): None si no hay clic
pos = pantalla.posicion_raton()                # (x, y) de dónde está el ratón

aceptar = pantalla.boton("Aceptar", 10, 10, al_clic=lambda: "ok")     # cambia de color al pasar por encima
cancelar = pantalla.boton("Cancelar", 22, 10, al_clic=lambda: "no")
zona = pantalla.zona(5, 3, 20, 4, al_clic=lambda: "zona")             # un rectángulo invisible que se puede pulsar
resultado = pantalla.bucle([aceptar, cancelar, zona])                 # espera hasta que algo devuelva un valor (o Esc)

pantalla.desactivar_raton()
```

Funciona en Windows (cmd, PowerShell, Windows Terminal) y en las terminales de Linux y Mac.

#### Matrices

```python
A = pantalla.pedir_matriz("A")                        # eliges el tamaño con las flechas y rellenas cada hueco
B = pantalla.pedir_matriz("B", filas=2, columnas=3)   # tamaño fijo
C = pantalla.pedir_matriz("C", cuadrada=True)         # filas y columnas suben a la vez

pantalla.matriz(A)                          # la dibuja con corchetes, como un print
pantalla.matriz(A, 5, 3, nombre="A")        # en la columna 5, fila 3, con "A ="
pantalla.matriz(A, 5, 3, det=True)          # con barras, como un determinante
```

`pedir_matriz()` acepta enteros, decimales (`2.5` o `2,5`) y fracciones (`1/2`). Devuelve una lista de filas, por ejemplo `[[1, 2], [3, 4]]`. Con `fracciones=True` devuelve `Fraction` en vez de decimales.

Las cuentas se hacen con fracciones exactas, así que la inversa sale `1/3` y no `0.3333333`:

```python
A = [[2, 1], [1, -1]]

pantalla.sumar_matrices(A, B)       # también restar_matrices()
pantalla.multiplicar_matrices(A, B) # o un número por una matriz: multiplicar_matrices(2, A)
pantalla.transpuesta(A)
pantalla.potencia_matriz(A, 3)      # A·A·A
pantalla.identidad(3)
pantalla.traza(A)                   # 1
pantalla.determinante(A)            # -3
pantalla.inversa(A)                 # [[1/3, 1/3], [1/3, -2/3]]
pantalla.rango(A)                   # 2
```

Si la matriz no tiene inversa, el error te dice por qué: `inversa: esta matriz no tiene inversa porque su determinante es 0`.

##### Gauss y sistemas de ecuaciones

```python
pantalla.escalonar(A, pasos=True)                 # enseña cada paso: F2 → F2 - 2·F1
pantalla.escalonar(A, reducida=True)              # Gauss-Jordan

# 2x + y = 5
#  x - y = 1
pantalla.resolver_sistema([[2, 1], [1, -1]], [5, 1], pasos=True)   # Solución: x = 2,  y = 1
pantalla.clasificar_sistema([[1, 1], [2, 2]], [3, 6])              # "compatible indeterminado"
pantalla.matriz([[2, 1, 5], [1, -1, 1]], ampliada=True)           # con la raya antes de la última columna
```

`resolver_sistema()` devuelve la lista con las soluciones, o `None` si el sistema no tiene una sola solución (con `pasos=True` te dice si es porque no tiene ninguna o porque tiene infinitas). En vez de `b` le puedes dar directamente la matriz ampliada.

#### Vectores

<p align="center"><img src="https://raw.githubusercontent.com/phernandez102/pantalla/main/.github/img/vectores.svg" alt="Dos vectores y su suma dibujados con flechas, con el producto escalar, el módulo y el ángulo" width="720"></p>

```python
u = pantalla.Vector(3, 2)
v = pantalla.Vector(-1, 3)

print(u + v)          # (2, 5)
print(2 * u - v)      # (7, 1)
print(u / 2)          # (3/2, 1)
print(abs(u))         # el módulo: 3.605551275464

pantalla.dibujar_vectores({"u": u, "v": v, "u+v": u + v})      # con flechas, cada uno de un color
pantalla.dibujar_vectores({"u": u, "v": ((3, 2), (2, 5))})      # v empieza en la punta de u
pantalla.dibujar_vectores([u, v], estilo="rayas")              # con ╱ ╲ │ ─ en vez de braille
u = pantalla.pedir_vector("u", dimension=3)                     # como pedir_matriz, pero en una fila
```

Las rayas se hacen con puntitos braille (`⠁⠂⠄⡀`): cada letra tiene 2×4 puntos, así que salen casi rectas aunque vayan torcidas. Si tu terminal no tiene esa letra, `estilo="rayas"` las dibuja como antes.

Un `Vector` es una tupla, así que vale para todo lo que acepta una tupla (`x, y = u`, `u[0]`, `len(u)`). Las funciones también aceptan tuplas y listas normales, y las cuentas van con fracciones exactas como las matrices. Para meterlo en un texto usa un f-string: `f"u = {u}"`.

```python
pantalla.producto_escalar((1, 2, 3), (4, -5, 6))     # 12
pantalla.producto_vectorial((1, 2, 3), (4, 5, 6))    # (-3, 6, -3), solo en 3D
pantalla.producto_mixto((1, 0, 0), (0, 1, 0), (0, 0, 1))   # 1, el determinante de los tres
pantalla.modulo((3, 4))                              # 5 (si la raíz no es exacta, un decimal)
pantalla.unitario((3, 4))                            # (3/5, 4/5)
pantalla.angulo((1, 0), (1, 1))                      # 45.0, en grados (radianes=True si los quieres así)
pantalla.distancia((1, 1), (4, 5))                   # 5
pantalla.vector_entre((1, 2), (4, 6))                # el vector AB: (3, 4)
pantalla.proyeccion((2, 3), (1, 0))                  # (2, 0)

pantalla.son_perpendiculares((1, 2), (-2, 1))        # True
pantalla.son_paralelos((1, 2), (3, 6))               # True
pantalla.son_independientes((1, 0, 0), (0, 1, 0), (1, 1, 0))   # False
```

Con `pasos=True` escriben la cuenta entera, como se haría en el cuaderno:

```text
u · v = 1·4 + 2·(-5) + 3·6 = 4 - 10 + 18 = 12
|u| = √(2² + 2²) = √8 = 2√2 ≈ 2.8284
cos α = u · v / (|u|·|v|) = 5 / (√5·√10) ≈ 0.7071
α ≈ 45°
        │ i  j  k │
u × v = │ 1  2  3 │ = (2·6 - 3·5, 3·4 - 1·6, 1·5 - 2·4) = (-3, 6, -3)
        │ 4  5  6 │
```

#### Rectas

```python
r = pantalla.recta((1, 3), (2, 5))           # por dos puntos
r = pantalla.recta((1, 3), vector=(1, 2))    # por un punto y un vector
r = pantalla.recta((0, 1), pendiente="1/2")  # por un punto y la pendiente
r = pantalla.recta("y = 2x + 1")             # escrita, también "2x - y + 1 = 0" o "x = 3"

print(r)                     # 2x - y + 1 = 0
r.explicita()                # y = 2x + 1
r.punto_pendiente()          # y - 3 = 2(x - 1)
r.vectorial()                # (x, y) = (1, 3) + t·(1, 2)
r.parametricas()             # x = 1 + t,  y = 3 + 2t
r.continua()                 # (x - 1)/1 = (y - 3)/2
r.pendiente, r.ordenada      # 2, 1
r(4)                         # 9, la y cuando x = 4 (así se puede pasar a grafica())
r.pasa_por((0, 1))           # True
```

`pantalla.ecuaciones_recta((1, 3), (2, 5))` escribe todas las ecuaciones una debajo de otra. Para dos rectas:

```python
pantalla.posicion_rectas("y = 2x", "y = 2x + 1")             # "paralelas" (o "secantes", "coincidentes")
pantalla.interseccion_rectas("y = 2x + 1", "x + y = 4")      # (1, 3)
pantalla.angulo_rectas("y = x", "y = -x")                    # 90.0
pantalla.distancia_punto_recta((0, 0), "3x + 4y - 10 = 0", pasos=True)
# d = |3·0 + 4·0 + (-10)| / √(3² + 4²) = 10 / 5 = 2
```

#### Espacio (3D)

Planos, rectas y puntos del espacio, como en 2.º de bachillerato. Todo sale con fracciones exactas.

```python
pi = pantalla.plano((1, 0, 2), (0, 3, 0), (1, 1, 1))     # por tres puntos
pi = pantalla.plano((1, 2, 3), normal=(1, 1, 1))         # por un punto y el vector normal
pi = pantalla.plano("x/3 + y/3 + z/3 = 1")               # escrito

print(pi)                   # x + y + z - 3 = 0
pi.segmentaria()            # x/3 + y/3 + z/3 = 1
pi.vectorial()              # (x, y, z) = (0, 0, 3) + λ·(1, 0, -1) + μ·(0, 1, -1)

r = pantalla.recta((1, 2, 3), (2, 2, 5))                 # con puntos de tres números es del espacio
r = pantalla.recta("(x - 1)/2 = y = z + 1")              # continua
r = pantalla.recta("x + y = 3", "z = 1")                 # donde se cortan dos planos
r.parametricas(), r.continua(), r.implicitas()
```

`ecuaciones_plano()` y `ecuaciones_recta()` escriben todas las ecuaciones. Y para hacer cosas con ellos:

```python
pantalla.posicion("x + y + z = 3", "x - y = 1", "z = 2", pasos=True)   # con los rangos (Rouché)
pantalla.interseccion("x + y + z = 3", "x - y = 1", "z = 2")           # (1, 0, 2)
pantalla.distancia((1, 2, 3), "2x - y + 2z = 1", pasos=True)           # punto-plano, recta-recta...
pantalla.angulo(r, "z = 0", pasos=True)
pantalla.proyeccion((1, 2, 3), "x + y + z = 0")
pantalla.simetrico((1, 2, 3), "x + y + z = 0")
pantalla.perpendicular_comun(r, s)
pantalla.area_triangulo((1, 0, 0), (0, 2, 0), (0, 0, 3), pasos=True)
pantalla.volumen_tetraedro((0, 0, 0), (1, 0, 0), (0, 2, 0), (0, 0, 3))
```

Y verlos en 3D:

```python
pantalla.ver_espacio({"π": pi, "r": r, "P": (1, 1, 1)})      # a pantalla completa, se gira con el ratón
pantalla.dibujar_espacio(["x + y + z = 3", "z = 1"])         # quieto, como un print
pantalla.dibujar_espacio(pi, 40, 2, girar=True)              # en su sitio, y se gira con el ratón
```

En las terminales que pintan imágenes (Windows Terminal, WezTerm, kitty, iTerm2...) los planos salen rellenos y transparentes, y lo que está detrás va con rayitas. En las demás, o con `estilo="puntos"`, con puntitos braille. Con `girar=True` el dibujo se queda en la pantalla y se puede girar arrastrándolo mientras tu programa espera otra cosa (un `menu()`, `tecla()`, `esperar_clic()`...): así puedes tener un menú a un lado y el 3D al otro.

#### Imágenes y modelos 3D

```python
pantalla.imagen("gato.jpg")                      # donde esté el cursor, como un print
pantalla.imagen("gato.jpg", 5, 2, ancho=40)      # en (5, 2), de 40 columnas
pantalla.imagen("logo.png", estilo="letras")     # con . : - = + * # % @ de colores
```

Abre PNG, JPG, GIF, BMP y PPM sin instalar nada (con Pillow abre también WEBP y los JPG progresivos, y más rápido). Si la terminal sabe pintar imágenes sale la foto de verdad; si no, con medios bloques ▀ de colores.

```python
pantalla.ver_modelo("tetera.obj")                     # un modelo 3D (.obj o .stl), para girarlo
pantalla.ver_modelo("cara.jpg", relieve=0.4)          # una foto en relieve: lo claro sube
pantalla.ver_modelo(lambda x, y: x**2 - y**2)         # la superficie z = f(x, y)
pantalla.dibujar_modelo("pieza.stl", 40, 2, girar=True)
m = pantalla.modelo("tetera.obj")                     # leerlo una vez y usarlo muchas
```

#### Polinomios

<p align="center"><img src="https://raw.githubusercontent.com/phernandez102/pantalla/main/.github/img/polinomios.svg" alt="Ruffini de x³ - 2x² - x + 2, su factorización, la ecuación de segundo grado paso a paso y la gráfica" width="760"></p>

```python
p = pantalla.polinomio("2x^3 - 3x + 1")      # también "2x³ - 3x + 1" o Polinomio(2, 0, -3, 1)
print(p)                 # 2x³ - 3x + 1
p(2)                     # 11
p.grado                  # 3
p.derivada()             # 6x² - 3
p * p, p + 1, p ** 2     # se suman, restan y multiplican como números

pantalla.dividir_polinomios("x^3 + 2x + 5", "x^2 + 1")       # (x, x + 5): cociente y resto
pantalla.ruffini(p, 1, pasos=True)                            # la tabla de Ruffini
pantalla.raices("x^3 - 2x^2 - x + 2")                        # [-1, 1, 2]
pantalla.factorizar_polinomio("2x^2 - 2")                    # 2·(x - 1)·(x + 1)
pantalla.ecuacion_segundo_grado(1, -5, 6, pasos=True)        # [3, 2]
```

Con `pasos=True`:

```text
  │   2   0  -3   1                 x² - 5x + 6 = 0
1 │       2   2  -1                 Δ = b² - 4ac = (-5)² - 4·1·6 = 25 - 24 = 1
──┼────────────────                 x = (-b ± √Δ) / 2a = (5 ± 1) / 2
  │   2   2  -1   0                 x₁ = 3    x₂ = 2
Cociente: 2x² + 2x - 1    Resto: 0
```

`factorizar_polinomio(p, pasos=True)` va probando raíces y hace un Ruffini por cada una. Las raíces que no son fracciones salen con decimales.

#### Fracciones y números

<p align="center"><img src="https://raw.githubusercontent.com/phernandez102/pantalla/main/.github/img/mates.svg" alt="Cuentas con fracciones, una matriz con su inversa y la descomposición de 360" width="640"></p>

```python
f = pantalla.fraccion("3/4")                       # también fraccion(3, 4) o fraccion("0,75")
print(f + pantalla.fraccion("1/6"))                # 11/12
f = pantalla.pedir_fraccion("Dime una fracción: ")  # insiste hasta que lo sea

pantalla.calcular("3/4 + 1/6")                     # 11/12, también valen ÷, : y ^
pantalla.escribir_cuenta("1/2 + 1/3", 5, 3)        # la dibuja como en el cuaderno, con el resultado
```

Y para trabajar con enteros:

```python
pantalla.mcd(12, 18)        # 6
pantalla.mcm(4, 6)          # 12
pantalla.es_primo(97)       # True
pantalla.divisores(12)      # [1, 2, 3, 4, 6, 12]
pantalla.factorizar(360)    # {2: 3, 3: 2, 5: 1}
pantalla.descomponer(360)   # la tabla de dividir entre primos y 360 = 2³ · 3² · 5
```

##### Cambios de base

```python
pantalla.a_binario(45)             # "101101"
pantalla.a_hexadecimal(255)        # "FF"
pantalla.cambiar_base(100, 3)      # "10201", cualquier base del 2 al 36
pantalla.a_decimal("101101")       # 45 (también "ff", 16 o "0x2F")

pantalla.a_binario(45, pasos=True)
pantalla.a_decimal("101101", pasos=True)
```

```text
45 : 2 = 22   resto 1
22 : 2 = 11   resto 0
11 : 2 =  5   resto 1
 5 : 2 =  2   resto 1
 2 : 2 =  1   resto 0
 1 : 2 =  0   resto 1
45 = 101101₂   (los restos, de abajo arriba)

101101₂ = 1·2⁵ + 0·2⁴ + 1·2³ + 1·2² + 0·2¹ + 1·2⁰ = 32 + 8 + 4 + 1 = 45
```

#### Estadística

<p align="center"><img src="https://raw.githubusercontent.com/phernandez102/pantalla/main/.github/img/estadistica.svg" alt="Histograma de unas notas y la tabla con media, mediana, moda y desviación típica" width="620"></p>

```python
notas = [5, 7, 7, 8, 6, 9, 7, 4]

pantalla.media(notas)          # 6.625
pantalla.mediana(notas)        # 7
pantalla.moda(notas)           # 7 (si empatan, una lista)
pantalla.varianza(notas)       # 2.234375 (muestra=True para dividir entre n - 1)
pantalla.desviacion(notas)     # 1.4947...
pantalla.cuartiles(notas)      # (5.5, 7, 7.5)

pantalla.tabla_frecuencias(notas)               # xᵢ, fᵢ, Fᵢ, hᵢ y %
pantalla.tabla_frecuencias(alturas, intervalos=5)
pantalla.histograma(notas, 2, 3, alto=10)
pantalla.estadisticas(notas)                    # todo lo anterior en una tabla
```

Los datos también pueden ir contados: `{"rojo": 4, "azul": 2}` o `{5: 3, 6: 1}`.


#### Gráficas

<p align="center"><img src="https://raw.githubusercontent.com/phernandez102/pantalla/main/.github/img/graficas.svg" alt="Seno y coseno, una gráfica de barras y una minigráfica" width="720"></p>

```python
import math

def f(x):
    return x * x - 4

pantalla.grafica(f, -4, 4)                                 # y = x² - 4, de x = -4 a x = 4
pantalla.grafica([math.sin, math.cos], -6.3, 6.3)          # varias a la vez, cada una de un color
pantalla.grafica(f, -4, 4, 10, 3, ancho=40, alto=12)       # en la columna 10, fila 3

pantalla.barras({"Ana": 8.5, "Luis": 6, "Marta": 9.75}, maximo=10)
print("Esta semana:", pantalla.minigrafica([3, 1, 4, 1, 5, 9, 2, 6]))   # ▃▁▄▁▅█▂▅
```

Si la función falla en algún punto (como `1/x` en el 0), ese punto se deja en blanco y sigue.

La línea se dibuja con puntitos braille, como las flechas de los vectores, y queda fina y seguida. Con `estilo="puntos"` sale con `•`, y con `caracter="*"` con la letra que quieras.

#### Practicar

```python
pantalla.practicar("tablas")                       # 5 multiplicaciones
pantalla.practicar("fracciones", 10, nivel=2)      # nivel 1, 2 o 3
pantalla.practicar()                               # te deja elegir el tema
```

Pone el ejercicio, espera la respuesta y te dice si está bien o cuál era (y por qué). Al final sale la nota:

```text
1) 4 × 3 = 12
   ¡Bien! ✓
2) 7 × 8 = 54
   No, era 56. 7 × 8 = 56
...
Has acertado 4 de 5  ★★★★☆  Nota: 8
```

Temas: tablas, sumas, divisiones, fracciones, potencias, raices, ecuaciones, mcd, primos, binario, porcentajes y vectores. Escribe `salir` para acabar antes. Devuelve cuántas has acertado.

#### Récords y tiempo

```python
puesto = pantalla.guardar_record("Ana", 120)       # 1 si es el mejor, None si no entra
pantalla.guardar_record("Luis", 34.5, "tiempos.json", menos_es_mejor=True)
pantalla.leer_records()                            # [("Ana", 120), ...]
pantalla.mejor_record()                            # 120
pantalla.tabla_records(x=10, y=5)                  # la tabla con puesto, nombre, puntos y fecha

c = pantalla.cronometro()
...
c.parar()
print("Has tardado", c)                            # Has tardado 00:12.3
pantalla.cuenta_atras(3)                           # 3, 2, 1, ¡Ya!
```

Los récords se guardan en un archivo `records.json` en la carpeta de tu programa, así que siguen ahí al volver a abrirlo.

### Hacer un juego

Con `pantalla.jugar()` no hace falta ningún `while`: escribes una función que dibuja **un momento** del juego y `jugar()` la llama 20 veces por segundo (o las que digas con `velocidad=`). Todo lo que dibujas sale de golpe, sin parpadeos, y al acabar la terminal queda como estaba.

```python
import pantalla

nave = pantalla.Sprite("/^\\", 30, 20, color="verde")    # un dibujo que se mueve: se pinta solo

def actualizar(tecla):                 # tecla: la que se acaba de pulsar, o None
    if pantalla.pulsada("izquierda"):  # True mientras la mantienes pulsada
        nave.mover(-1, 0)
    if pantalla.pulsada("derecha"):
        nave.mover(1, 0)
    if pantalla.cada(1):               # True una vez cada segundo
        ...
    pantalla.escribir("Fotograma %d" % pantalla.fotograma(), 1, 1)
    if tecla == "q":
        return "adiós"                 # devolver algo acaba el juego

resultado = pantalla.jugar(actualizar, velocidad=20, ancho=60, alto=22)   # Esc también sale
```

- Dentro de `actualizar` vale **todo** lo de pantalla (`escribir`, `caja`, `grande`, `print`...). Se borra solo antes de cada fotograma.
- `Sprite(dibujo, x, y, color=, colores=, fotogramas=[...], cada=5, capa=0)`: `mover()`, `choca(otro o lista)`, `fuera()`, `eliminar()`. `pantalla.sprites()` da los que hay.
- `capa=`: si dos sprites se pisan, se ve el de capa más alta. Con capa negativa el sprite es de fondo (estrellas, hierba...) y queda detrás de lo que dibujes tú.
- `escribir_lento()` dentro del juego se ve letra a letra (el juego espera mientras escribe, como con `pausa()`).
- Para guardar cosas que cambian (puntos, vidas...) tienes dos opciones. Una es poner `global puntos` en la primera línea de `actualizar`. La otra es apuntarlas en un sprite: `pelota.dx = 1`, y así no hace falta `global`. Lo puedes ver en `ejemplos/12_pelota.py`.
- `jugar(..., raton=True)` para usar `leer_raton()` dentro; `fondo="azul"` pinta el fondo.
- En Linux y Mac, `pulsada()` depende de la repetición del teclado (hay un pequeño retraso al empezar a mantener una tecla). En Windows va perfecta.

Mira `ejemplos/10_space_invaders.py` (un Space Invaders en ~90 líneas, doble clic en `jugar_space_invaders.bat` en Windows) y `ejemplos/12_pelota.py` (lo mínimo).

Si prefieres hacerlo a mano, `tecla_pulsada()` mira si hay una tecla pulsada **sin esperar**, y si no hay devuelve `None`:

```python
import pantalla

pantalla.iniciar()               # pantalla aparte, sin cursor y sin que se vean las teclas
x = 1
while x < pantalla.ancho():
    t = pantalla.tecla_pulsada()
    if t == "q":
        break
    pantalla.punto(x, 10, " ")
    x = x + 1
    pantalla.punto(x, 10, "►", color="amarillo")
    pantalla.pausa(0.05)
pantalla.terminar()              # todo como estaba
```

En la carpeta `ejemplos` hay una **serpiente** completa con poco más de 60 líneas.

### El constructor web

Es una página donde dibujas la pantalla con el ratón: cajas, textos, líneas, letras grandes, colores... Mientras pasas el ratón te dice la `x` y la `y` de cada sitio, y abajo te va escribiendo el código.

<p align="center">
  <a href="https://phernandez102.github.io/pantalla/"><b>Ábrelo en phernandez102.github.io/pantalla</b></a>
</p>

<table>
<tr>
<td><img src="https://raw.githubusercontent.com/phernandez102/pantalla/main/.github/img/constructor.png" alt="El constructor: herramientas a la izquierda, la terminal en el centro y las capas a la derecha"></td>
<td><img src="https://raw.githubusercontent.com/phernandez102/pantalla/main/.github/img/docs.png" alt="La documentación visual: cada función con un ejemplo que se dibuja en vivo"></td>
</tr>
<tr>
<td align="center"><sub>El constructor</sub></td>
<td align="center"><sub>La documentación visual, con ejemplos en vivo</sub></td>
</tr>
</table>

Te da el código de dos formas:

1. **Código Python**: un programa normal con una línea por cada cosa (`pantalla.caja(...)`, `pantalla.escribir(...)`...). Es el mejor para aprender.
2. **Para `pantalla.diseno()`**: todo el dibujo en una sola línea. Así lo puedes volver a abrir en el constructor, cambiarlo y pegarlo otra vez.

```python
import pantalla

pantalla.limpiar()
zonas = pantalla.diseno(r'''{"pantalla": 1, "ancho": 80, "alto": 24, "elementos": [...]}''')

x, y = zonas["puntos"]                # dónde está el hueco "puntos" que dibujaste
pantalla.escribir(120, x, y, color="amarillo")
```

En el constructor puedes ponerle **nombre** a cualquier cosa, y hay una herramienta de **huecos con nombre**: sitios que dejas libres para que tu programa escriba encima (los puntos, el nombre del jugador...). `pantalla.diseno()` te devuelve dónde está cada uno.

También vale guardar el diseño en un archivo `mi_pantalla.json` y hacer `pantalla.diseno("mi_pantalla.json")`. Con `centrado=True` se coloca en el centro de la terminal, aunque sea más grande que el diseño.

En la misma web está la **documentación**: cada función con un ejemplo que se dibuja como en la terminal. Arriba tienes un buscador (pulsa `/` o Ctrl+K) que también entiende palabras en inglés como `loading` o `input`. En las gráficas, `barras()`, `mcd()` o `descomponer()` mueves los deslizadores y el dibujo cambia al momento. Salen las mismas cuentas que en Python, así que lo que ves es lo que te va a salir.

### Guía para IA

¿Usas ChatGPT, Claude, Gemini o Copilot para programar? Dale la guía de pantalla y sabrá usarla sin inventarse funciones: trae cómo funciona la librería, la firma exacta y la explicación de cada función, los colores, fuentes y estilos que valen, los errores típicos, este manual y todos los ejemplos.

- Descárgala de la web, en **[Guía para IA](https://phernandez102.github.io/pantalla/#ia)** (en `.md` para pegarla en el chat o en `.json` para agentes y programas).
- O sácala de la librería que tienes instalada, de tu misma versión:

```
python -m pantalla ia > pantalla-ia.md
```

### Ejemplos

En la carpeta `ejemplos` del repositorio hay programas cortos, del más fácil al más difícil:

1. `01_hola.py`: lo mínimo
2. `02_cajas_y_colores.py`: cajas, colores y rectángulos
3. `03_menu.py`: un programa con menú y varias opciones
4. `04_mover.py`: mover una @ con las flechas
5. `05_serpiente.py`: el juego de la serpiente
6. `06_notas_con_print.py`: mezclar `print` normal con `pedir_numero` y `tabla`
7. `07_matrices.py`: pedir dos matrices con las flechas y sumarlas
8. `08_diseno.py`: usar una pantalla hecha con el constructor web
9. `09_raton.py`: botones y clics con el ratón
10. `10_space_invaders.py`: un Space Invaders con `jugar()` y `Sprite`, sin ningún `while`
11. `11_spinners.py`: spinners que giran mientras el programa trabaja
12. `12_pelota.py`: el juego más pequeño posible, una pelota que rebota
13. `13_fracciones.py`: pedir dos fracciones y hacer la cuenta como en el cuaderno
14. `14_sistemas.py`: resolver un sistema de ecuaciones por Gauss, paso a paso
15. `15_graficas.py`: dibujar funciones y gráficas de barras
16. `16_formulario.py`: un formulario y una lista para marcar varias cosas
17. `17_pantalla_de_carga.py`: una pantalla de carga que prepara un mapa de verdad antes de enseñarlo
18. `18_vectores.py`: pedir dos vectores, dibujarlos con flechas y sacar el ángulo entre ellos
19. `19_polinomios.py`: escribir un polinomio, factorizarlo con Ruffini y dibujarlo
20. `20_estadistica.py`: meter las notas de la clase y sacar el histograma y la tabla de frecuencias
21. `21_practicar.py`: hacer 10 ejercicios del tema que elijas
22. `22_records.py`: un juego de rapidez con cuenta atrás, cronómetro y tabla de récords
23. `23_espacio.py`: un menú de planos y rectas a un lado y el dibujo 3D al otro, que se gira con el ratón
24. `24_modelos.py`: una foto en la terminal, una casita `.obj` con sus colores (`casa.obj` y `casa.mtl`) y una superficie 3D para girarla

### Si algo falla

Los errores te dicen en español qué ha pasado y cómo arreglarlo:

```
>>> pantalla.escribe("hola")
AttributeError: pantalla no tiene ninguna función que se llame 'escribe'. ¿Querías decir pantalla.escribir...?

>>> pantalla.escribir(5, 3, "hola")
TypeError: escribir: 'y' tiene que ser un número, pero me has dado 'hola'. ¿Has puesto el texto al final? ...

>>> pantalla.gotoxy("5", 3)
TypeError: gotoxy: 'x' tiene que ser un número, pero me has dado '5'. Es un número entre comillas...
```

- Puedes escribir los nombres con tildes y ñ: `pantalla.tamaño()`, `pantalla.diseño()`, `pantalla.pedir_contraseña()`.
- Al comparar teclas no importan las mayúsculas ni el nombre: `tecla == "Intro"`, `tecla == "ENTER"` y `tecla == "enter"` valen igual, y `tecla == " "` es el espacio.
- Si en un juego se te olvida `global`, el error te dice qué línea tienes que poner.

### ¿Cómo funciona por dentro?

Con **códigos ANSI**: textos especiales que empiezan por el carácter ESC (`\x1b`) y que la terminal entiende como órdenes en vez de como letras. Por ejemplo:

```python
print("\x1b[31mHola")     # Hola en rojo
print("\x1b[5;10H*")      # un * en la fila 5, columna 10
```

`pantalla` solo te ahorra tener que acordarte de todos esos códigos. Si tienes curiosidad, el código está escrito para que se entienda: empieza por `terminal.py`.

Para leer teclas sueltas usa `msvcrt` en Windows y `termios` en Linux y Mac, que vienen con Python.

### Licencia

MIT: puedes usarla, copiarla y cambiarla como quieras.

Incluye trabajo de otros, con sus propias licencias:

- **Fuentes FIGlet** (`src/pantalla/fuentes/*.flf`): vienen de [pyfiglet](https://github.com/pwaller/pyfiglet) (MIT). Cada fuente es de su autor y conserva su licencia y sus créditos en las primeras líneas del archivo. Solo se han quitado los caracteres que no se usan.
- **Animaciones de los spinners**: de [cli-spinners](https://github.com/sindresorhus/cli-spinners) (MIT, © Sindre Sorhus).

## Ejemplos completos

Programas que vienen en la carpeta `ejemplos/` del repositorio. Todos funcionan tal cual.

### `ejemplos/01_hola.py`

```python
import pantalla

pantalla.limpiar()
pantalla.rodear("=")
pantalla.centrar("¡Hola, mundo!", color="amarillo", negrita=True)

pantalla.gotoxy(3, 2)
print("Esto está en la columna 3, fila 2")

pantalla.escribir("Y esto abajo a la derecha", 50, 20, color="cian")

pantalla.esperar("Pulsa una tecla para salir", 3, pantalla.alto() - 1)
pantalla.limpiar()
```

### `ejemplos/02_cajas_y_colores.py`

```python
import pantalla

pantalla.limpiar()

pantalla.caja(2, 2, 30, 8, estilo="doble", color="verde", titulo="Jugador")
pantalla.escribir("Nombre: Ana", 4, 4)
pantalla.escribir("Vidas:  ", 4, 5)
pantalla.escribir("♥ ♥ ♥", 12, 5, color="rojo")
pantalla.escribir("Nivel:  7", 4, 6)

pantalla.caja(35, 2, 30, 8, estilo="redondo", color="cian", titulo="Inventario")
cosas = ["espada", "poción", "llave", "mapa"]
for i in range(len(cosas)):
    pantalla.escribir("- " + cosas[i], 37, 4 + i)

pantalla.rellenar(2, 11, 63, 3, fondo="azul")
pantalla.escribir("Un rectángulo azul con texto encima", 15, 12, color="blanco", fondo="azul", negrita=True)

print()
print()
print("También se puede usar con print:", pantalla.colorear("en rojo", "rojo"), "y", pantalla.colorear("en verde", "verde"))

pantalla.esperar()
```

### `ejemplos/03_menu.py`

```python
import pantalla


def saludar():
    nombre = pantalla.pedir("¿Cómo te llamas? ", 5, 5, color="cian")
    pantalla.mensaje("¡Hola, " + nombre + "!", titulo="Saludo")


def sumar():
    a = pantalla.pedir_numero("Primer número: ", 5, 5)
    b = pantalla.pedir_numero("Segundo número: ", 5, 7)
    pantalla.mensaje(str(a) + " + " + str(b) + " = " + str(a + b), titulo="Resultado")


def tabla_de_multiplicar():
    n = pantalla.pedir_numero("¿Qué tabla quieres? ", 5, 3, minimo=1, maximo=10)
    filas = []
    for i in range(1, 11):
        filas.append([str(n) + " x " + str(i), n * i])
    pantalla.tabla(filas, cabeceras=["Operación", "Resultado"], x=5, y=5)
    pantalla.esperar("Pulsa una tecla", 5, 19, color="gris")


while True:
    pantalla.limpiar()
    pantalla.rodear("redondo", color="azul")
    pantalla.grande("MENU", y=2, color="amarillo")
    opcion = pantalla.menu(["Saludar", "Sumar", "Tabla de multiplicar", "Salir"], titulo="Elige", y=9)
    pantalla.limpiar()
    if opcion == "Saludar":
        saludar()
    elif opcion == "Sumar":
        sumar()
    elif opcion == "Tabla de multiplicar":
        tabla_de_multiplicar()
    else:
        break

print("¡Adiós!")
```

### `ejemplos/04_mover.py`

```python
import pantalla

pantalla.iniciar()
pantalla.rodear("simple", color="gris", titulo="Mueve la @ con las flechas · q para salir")

x = 10
y = 5
while True:
    pantalla.punto(x, y, "@", color="amarillo")
    pantalla.escribir("x=" + str(x) + " y=" + str(y) + "   ", 3, pantalla.alto())

    t = pantalla.tecla()
    pantalla.punto(x, y, " ")

    if t == "arriba" and y > 2:
        y = y - 1
    elif t == "abajo" and y < pantalla.alto() - 1:
        y = y + 1
    elif t == "izquierda" and x > 2:
        x = x - 1
    elif t == "derecha" and x < pantalla.ancho() - 1:
        x = x + 1
    elif t == "q":
        break

pantalla.terminar()
```

### `ejemplos/05_serpiente.py`

```python
import random

import pantalla

ANCHO = pantalla.ancho()
ALTO = pantalla.alto()


def comida_nueva(serpiente):
    while True:
        sitio = (random.randint(2, ANCHO - 1), random.randint(4, ALTO - 1))
        if sitio not in serpiente:
            return sitio


pantalla.iniciar(titulo="Serpiente")
pantalla.rodear("doble", color="verde")
pantalla.linea(3, "═", x=2, largo=ANCHO - 2, color="verde")
pantalla.punto(1, 3, "╠", color="verde")
pantalla.punto(ANCHO, 3, "╣", color="verde")

serpiente = [(10, 10), (9, 10), (8, 10)]
direccion = "derecha"
comida = comida_nueva(serpiente)
puntos = 0

pantalla.punto(comida[0], comida[1], "●", color="rojo")
for x, y in serpiente:
    pantalla.punto(x, y, "█", color="verde claro")

while True:
    pantalla.escribir(" Puntos: " + str(puntos) + "   (flechas para moverte, q para salir) ", 3, 2, color="amarillo")

    t = pantalla.tecla_pulsada()
    if t == "q":
        break
    if t == "arriba" and direccion != "abajo":
        direccion = "arriba"
    elif t == "abajo" and direccion != "arriba":
        direccion = "abajo"
    elif t == "izquierda" and direccion != "derecha":
        direccion = "izquierda"
    elif t == "derecha" and direccion != "izquierda":
        direccion = "derecha"

    x, y = serpiente[0]
    if direccion == "arriba":
        y = y - 1
    elif direccion == "abajo":
        y = y + 1
    elif direccion == "izquierda":
        x = x - 1
    else:
        x = x + 1

    if x <= 1 or x >= ANCHO or y <= 3 or y >= ALTO or (x, y) in serpiente:
        pantalla.pitido()
        pantalla.mensaje("¡Has chocado!\nPuntos: " + str(puntos), titulo="Fin", color_borde="rojo")
        break

    serpiente.insert(0, (x, y))
    pantalla.punto(x, y, "█", color="verde claro")

    if (x, y) == comida:
        puntos = puntos + 1
        comida = comida_nueva(serpiente)
        pantalla.punto(comida[0], comida[1], "●", color="rojo")
    else:
        cola = serpiente.pop()
        pantalla.punto(cola[0], cola[1], " ")

    if direccion in ("arriba", "abajo"):
        pantalla.pausa(0.12)
    else:
        pantalla.pausa(0.07)

pantalla.terminar()
print("Has hecho", puntos, "puntos")
```

### `ejemplos/06_notas_con_print.py`

```python
import pantalla

print(pantalla.texto_grande("NOTAS"))
print()

alumnos = []
while True:
    nombre = pantalla.pedir("Nombre del alumno (Enter para acabar): ")
    if nombre == "":
        break
    nota = pantalla.pedir_numero("Nota de " + nombre + ": ", minimo=0, maximo=10, decimales=True)
    alumnos.append([nombre, nota])

if len(alumnos) == 0:
    print("No has metido a nadie.")
else:
    print()
    pantalla.tabla(alumnos, cabeceras=["Alumno", "Nota"])
    media = sum(a[1] for a in alumnos) / len(alumnos)
    if media >= 5:
        print("Media:", pantalla.colorear(round(media, 2), "verde", negrita=True))
    else:
        print("Media:", pantalla.colorear(round(media, 2), "rojo", negrita=True))
```

### `ejemplos/07_matrices.py`

```python
import pantalla

pantalla.limpiar()
pantalla.cabecera("MATRICES · Suma")

A = pantalla.pedir_matriz("A")
if A is None:
    raise SystemExit

# B tiene que ser del mismo tamaño que A para poder sumarlas
B = pantalla.pedir_matriz("B", filas=len(A), columnas=len(A[0]))
if B is None:
    raise SystemExit

C = []
for i in range(len(A)):
    fila = []
    for j in range(len(A[0])):
        fila.append(A[i][j] + B[i][j])
    C.append(fila)

pantalla.calculando()
pantalla.cabecera("MATRICES · Suma")
ancho_a, alto_a = pantalla.matriz(A, 3, 4, nombre="A")
ancho_b, alto_b = pantalla.matriz(B, 3 + ancho_a + 3, 4, nombre="B")
pantalla.matriz(C, 3 + ancho_a + 3 + ancho_b + 3, 4, nombre="A + B", color="verde")
pantalla.pie("Pulsa cualquier tecla para salir")
pantalla.tecla()
pantalla.limpiar()
```

### `ejemplos/08_diseno.py`

```python
import random

import pantalla

# Esta pantalla está hecha con el constructor web (plantilla "Ficha de jugador").
# Para cambiarla: pega el texto de diseno() en el constructor ("Abrir un diseño que ya tenías").
FICHA = r'''{"pantalla":1,"ancho":80,"alto":24,"elementos":[{"tipo":"caja","x":3,"y":2,"ancho":36,"alto":10,"estilo":"doble","titulo":"Jugador","color":"verde"},{"tipo":"texto","x":5,"y":4,"texto":"Nombre:","negrita":true},{"tipo":"hueco","x":14,"y":4,"ancho":20,"nombre":"nombre"},{"tipo":"texto","x":5,"y":6,"texto":"Vidas:","negrita":true},{"tipo":"hueco","x":14,"y":6,"ancho":10,"nombre":"vidas"},{"tipo":"texto","x":5,"y":8,"texto":"Nivel:","negrita":true},{"tipo":"hueco","x":14,"y":8,"ancho":5,"nombre":"nivel"},{"tipo":"caja","x":42,"y":2,"ancho":36,"alto":10,"estilo":"redondo","titulo":"Inventario","color":"cian"},{"tipo":"texto","x":44,"y":4,"texto":"- espada\n- poción\n- llave\n- mapa"},{"tipo":"rellenar","x":3,"y":13,"ancho":75,"alto":3,"caracter":" ","fondo":"azul"},{"tipo":"texto","x":5,"y":14,"texto":"Puntos:","color":"blanco","fondo":"azul","negrita":true},{"tipo":"hueco","x":14,"y":14,"ancho":10,"nombre":"puntos"},{"tipo":"linea","x":3,"y":17,"largo":75,"caracter":"─","color":"gris"},{"tipo":"texto","x":3,"y":23,"texto":"Pulsa Esc para salir","color":"gris"}]}'''

pantalla.iniciar()
zonas = pantalla.diseno(FICHA)

nombre = "Ana"
vidas = 3
puntos = 0
nivel = 1

# *zonas["nombre"] es lo mismo que escribir la x y la y del hueco "nombre"
pantalla.escribir(nombre, *zonas["nombre"], color="amarillo")
pantalla.escribir("Pulsa Espacio para ganar puntos", 3, 19)

while True:
    pantalla.escribir(("♥ " * vidas).ljust(10), *zonas["vidas"], color="rojo")
    pantalla.escribir(str(nivel).ljust(5), *zonas["nivel"])
    pantalla.escribir(str(puntos).ljust(10), *zonas["puntos"], color="amarillo", fondo="azul", negrita=True)

    t = pantalla.tecla()
    if t == "esc":
        break
    if t == "espacio":
        puntos = puntos + random.randint(1, 10)
        nivel = puntos // 25 + 1

pantalla.terminar()
print("Has terminado con", puntos, "puntos")
```

### `ejemplos/09_raton.py`

```python
"""
Demo del ratón: botones, zonas que se iluminan y un lienzo para pintar.

Ejecútalo en una terminal de verdad (cmd, PowerShell, Windows Terminal, la de VS Code
o la de Linux/Mac). En Windows puedes hacer doble clic en probar_raton.bat.
"""

import pantalla


def titulo(texto):
    pantalla.limpiar()
    pantalla.rodear("redondo", color="azul", titulo="Demo del ratón")
    pantalla.centrar(texto, 3, color="amarillo", negrita=True)


def elegir_color():
    titulo("pantalla.botones(): haz clic en uno (o flechas + Enter)")
    color = pantalla.botones(["Rojo", "Verde", "Azul", "Volver"], y=8)
    if color is None or color == "Volver":
        return
    pantalla.centrar("Has elegido: " + color, 11, color=color.lower(), negrita=True)
    pantalla.centrar("Pulsa una tecla para volver", 13, color="gris")
    pantalla.tecla()


def contador():
    titulo("pantalla.boton() + pantalla.bucle(): botones con contador")
    cuenta = [0]

    def ensenar():
        pantalla.centrar("     Clics: %d     " % cuenta[0], 6, color="cian", negrita=True)

    def sumar():
        cuenta[0] = cuenta[0] + 1
        ensenar()

    def restar():
        cuenta[0] = cuenta[0] - 1
        ensenar()

    def reiniciar():
        cuenta[0] = 0
        ensenar()

    ensenar()
    x = pantalla.ancho() // 2 - 18
    botones = [
        pantalla.boton("+1", x, 9, fondo="verde", al_clic=sumar),
        pantalla.boton("-1", x + 7, 9, fondo="rojo", al_clic=restar),
        pantalla.boton("Reiniciar", x + 14, 9, al_clic=reiniciar),
        pantalla.boton("Volver", x + 28, 9, fondo="gris", al_clic=lambda: "volver"),
    ]
    pantalla.centrar("Pasa el ratón por encima: se iluminan. Esc también vuelve.", 12, color="gris")
    pantalla.bucle(botones)


def tarjetas():
    titulo("pantalla.zona(): tarjetas que se iluminan al pasar el ratón")
    nombres = ["Fuego", "Agua", "Planta"]
    colores = ["rojo", "azul", "verde"]
    zonas = []
    x0 = pantalla.ancho() // 2 - 24

    def dibujar(i, encendida):
        x = x0 + i * 17
        estilo = "doble" if encendida else "simple"
        color = colores[i] if encendida else "gris"
        pantalla.caja(x, 6, 15, 5, estilo=estilo, color=color, titulo=nombres[i])
        pantalla.escribir(" ¡elígeme! " if encendida else "           ", x + 2, 8, color=colores[i], negrita=True)

    def elegida(i):
        pantalla.centrar("   Has elegido %s   " % nombres[i], 13, color=colores[i], negrita=True)

    for i in range(3):
        dibujar(i, False)
        zonas.append(pantalla.zona(x0 + i * 17, 6, 15, 5,
                                   al_hover=lambda i=i: dibujar(i, True),
                                   al_salir=lambda i=i: dibujar(i, False),
                                   al_clic=lambda i=i: elegida(i)))
    pantalla.centrar("Pasa el ratón por las tarjetas y haz clic. Esc para volver.", 16, color="gris")
    pantalla.bucle(zonas)


def puntos_de_la_linea(x1, y1, x2, y2):
    # Algoritmo de Bresenham: todas las casillas entre dos puntos, para que al mover
    # el ratón deprisa la raya salga seguida y sin huecos.
    puntos = []
    dx, dy = abs(x2 - x1), -abs(y2 - y1)
    paso_x = 1 if x1 < x2 else -1
    paso_y = 1 if y1 < y2 else -1
    error = dx + dy
    while True:
        puntos.append((x1, y1))
        if (x1, y1) == (x2, y2):
            return puntos
        doble = 2 * error
        if doble >= dy:
            error += dy
            x1 += paso_x
        if doble <= dx:
            error += dx
            y1 += paso_y


def pintar():
    titulo("leer_raton(arrastrar=True): arrastra para pintar, botón derecho borra")
    colores = ["rojo", "amarillo", "verde", "cian", "azul", "morado", "blanco"]
    elegido = [0]
    ancho, alto = pantalla.tamano()
    arriba, abajo = 5, alto - 3  # filas donde se puede pintar

    def paleta():
        pantalla.escribir(" Color: ", 3, alto - 1)
        for i, color in enumerate(colores):
            marca = "[██]" if i == elegido[0] else " ██ "
            pantalla.escribir(marca, 11 + i * 4, alto - 1, color=color)
        pantalla.escribir("  ·  B borra todo  ·  Esc vuelve ", 11 + len(colores) * 4, alto - 1, color="gris")

    paleta()
    pantalla.activar_raton()
    pantalla.ocultar_cursor()
    anterior = None  # último punto pintado, para unirlo con el siguiente
    while True:
        clic = pantalla.leer_raton(arrastrar=True)
        while clic:
            x, y, boton = clic
            if y == alto - 1 and not clic.arrastrando:
                i = (x - 11) // 4
                if 0 <= i < len(colores):
                    elegido[0] = i
                    paleta()
                anterior = None
            elif 2 <= x < ancho and arriba <= y <= abajo:
                letra = " " if boton == "derecho" else "█"
                desde = anterior if clic.arrastrando and anterior else (x, y)
                for px, py in puntos_de_la_linea(desde[0], desde[1], x, y):
                    pantalla.punto(px, py, letra, color=colores[elegido[0]])
                anterior = (x, y)
            else:
                anterior = None
            clic = pantalla.leer_raton(arrastrar=True)
        t = pantalla.tecla_pulsada()
        if t == "esc":
            break
        if t in ("b", "B"):
            for fila in range(arriba, abajo + 1):
                pantalla.escribir(" " * (ancho - 2), 2, fila)
        pantalla.pausa(0.01)
    pantalla.desactivar_raton()
    pantalla.mostrar_cursor()


OPCIONES = ["Elegir un color", "Botones con contador", "Tarjetas que se iluminan",
            "Pintar con el ratón", "Salir"]

pantalla.iniciar(titulo="Demo del ratón")
try:
    while True:
        titulo("¿Qué quieres probar? Haz clic (o flechas + Enter, o el número)")
        opcion = pantalla.botones(OPCIONES, horizontal=False, y=6)
        if opcion == "Elegir un color":
            elegir_color()
        elif opcion == "Botones con contador":
            contador()
        elif opcion == "Tarjetas que se iluminan":
            tarjetas()
        elif opcion == "Pintar con el ratón":
            pintar()
        else:
            break
finally:
    pantalla.terminar()

print("¡Adiós!")
```

### `ejemplos/10_space_invaders.py`

```python
"""
Space Invaders hecho con pantalla.jugar(): no hay ningún while.
Escribes qué pasa en cada momento (la función actualizar) y pantalla hace el resto.

    ← →  moverte        espacio  disparar        Esc  salir
"""

import random

import pantalla

ANCHO, ALTO = 60, 22

nave = pantalla.Sprite("/^\\", ANCHO // 2, ALTO - 1, color="verde")
# estrellas de fondo: con capa negativa quedan detrás de todo lo demás
for _ in range(25):
    pantalla.Sprite("·", random.randint(1, ANCHO), random.randint(2, ALTO - 1), color="gris", capa=-1)
marcianos = []
for fila, color in enumerate(["rojo", "amarillo", "cian", "morado"]):
    for columna in range(8):
        marcianos.append(pantalla.Sprite(fotogramas=["/oo\\", "\\oo/"], cada=8, color=color,
                                         x=6 + columna * 6, y=3 + fila * 2))
balas = []         # las nuestras
balas_malas = []   # las de los marcianos
direccion = 1      # 1 = hacia la derecha, -1 = hacia la izquierda
puntos = 0
vidas = 3
fin = None         # cuando acabe: "¡GANASTE!" o "GAME OVER"


def actualizar(tecla):
    global direccion, puntos, vidas, fin

    if fin:
        pantalla.grande(fin, y=6, color="verde" if vidas else "rojo")
        pantalla.centrar("Puntos: %d   ·   pulsa Enter" % puntos, y=14)
        if tecla == "enter":
            return puntos
        return

    # la nave: se mueve mientras mantienes la flecha y dispara con espacio
    if pantalla.pulsada("izquierda") and nave.x > 1:
        nave.mover(-1, 0)
    if pantalla.pulsada("derecha") and nave.x < ANCHO - 2:
        nave.mover(1, 0)
    if tecla == "espacio" and len(balas) < 3:
        balas.append(pantalla.Sprite("|", nave.x + 1, nave.y - 1, color="amarillo"))

    # los marcianos van de lado a lado y bajan una fila al llegar al borde
    if pantalla.cada(0.4):
        if any(m.x + direccion < 1 or m.x + 3 + direccion > ANCHO for m in marcianos):
            direccion = -direccion
            for m in marcianos:
                m.mover(0, 1)
        else:
            for m in marcianos:
                m.mover(direccion, 0)
    if pantalla.cada(0.7) and marcianos:
        quien = random.choice(marcianos)
        balas_malas.append(pantalla.Sprite("¦", quien.x + 1, quien.y + 1, color="rojo"))

    for bala in balas[:]:
        bala.mover(0, -1)
        tocado = bala.choca(marcianos)
        if tocado:
            tocado.eliminar()
            marcianos.remove(tocado)
            puntos += 10
        if tocado or bala.fuera():
            bala.eliminar()
            balas.remove(bala)

    for bala in balas_malas[:]:
        bala.mover(0, 0.5)
        if bala.choca(nave):
            vidas -= 1
            bala.eliminar()
            balas_malas.remove(bala)
        elif bala.fuera():
            bala.eliminar()
            balas_malas.remove(bala)

    if not marcianos:
        fin = "¡GANASTE!"
    elif vidas == 0 or any(m.y >= nave.y - 1 for m in marcianos):
        fin = "GAME OVER"
        vidas = 0
    if fin:
        for s in pantalla.sprites():
            s.eliminar()

    # lo que no son sprites se dibuja en cada fotograma
    pantalla.escribir("Puntos: %d" % puntos, 2, 1, color="amarillo", negrita=True)
    pantalla.escribir_derecha("Vidas: " + "♥ " * vidas, 1, color="rojo")
    pantalla.linea(ALTO, "─", color="verde")


resultado = pantalla.jugar(actualizar, ancho=ANCHO, alto=ALTO)
print("Has hecho %d puntos. ¡Gracias por jugar!" % (resultado or puntos))
```

### `ejemplos/11_spinners.py`

```python
"""
Spinners: la ruedecita que gira mientras el programa trabaja (como la librería halo).
"""

import time

import pantalla

pantalla.limpiar()
pantalla.escribir("1) Con with: gira mientras se hace lo de dentro\n", 1, 1, color="cian", negrita=True)

with pantalla.spinner("Descargando el mapa..."):
    time.sleep(1.5)

with pantalla.spinner("Cargando enemigos...", estilo="arco", color="amarillo"):
    time.sleep(1.5)

try:
    with pantalla.spinner("Conectando con el servidor...", estilo="pelota", color="morado"):
        time.sleep(1.5)
        raise ConnectionError("no hay internet")
except ConnectionError:
    pass  # el spinner ya ha puesto ✖ y el error llega aquí igual

print()
pantalla.escribir("2) A mano: cambiando el texto mientras gira\n", color="cian", negrita=True)
s = pantalla.spinner("Paso 1 de 3", estilo="tiburon", color="azul").empezar()
for paso in (2, 3):
    time.sleep(1)
    s.texto = "Paso %d de 3" % paso
time.sleep(1)
s.bien("Los 3 pasos, hechos")
s = pantalla.spinner("Guardando la partida", estilo="estrella").empezar()
time.sleep(1)
s.dejar("★", "¡Nuevo récord!", color="amarillo")  # cualquier símbolo al acabar

print()
pantalla.esperar("Pulsa una tecla para ver todos los estilos (Esc para salir)...", color="gris")

# 3) Todos los estilos a la vez, con jugar() (que se encarga del bucle)
nombres = pantalla.lista_spinners()


def actualizar():
    ancho, alto = pantalla.tamano()
    pantalla.cabecera("pantalla.lista_spinners() · Esc para salir")
    columnas = max(1, ancho // 34)
    for i, nombre in enumerate(nombres):
        x = 2 + (i % columnas) * 34
        y = 3 + i // columnas
        if y >= alto:
            break
        milis, fotogramas = pantalla.spinners.SPINNERS[nombre]
        fotograma = fotogramas[int(pantalla.fotograma() * 50 / milis) % len(fotogramas)]
        pantalla.escribir(fotograma[:12], x, y, color="amarillo")
        pantalla.escribir(nombre, x + 13, y, color="gris")


pantalla.jugar(actualizar, velocidad=20)
```

### `ejemplos/12_pelota.py`

```python
"""Lo mínimo para un juego: una pelota que rebota. Esc para salir."""

import pantalla

pelota = pantalla.Sprite("●", 10, 5, color="amarillo")
pelota.dx = 1   # a un Sprite le puedes apuntar lo que quieras: cuánto se mueve de lado...
pelota.dy = 1   # ...y cuánto hacia abajo en cada fotograma


def actualizar():
    ancho, alto = pantalla.tamano()
    pelota.mover(pelota.dx, pelota.dy)
    if pelota.x <= 2 or pelota.x >= ancho - 1:
        pelota.dx = -pelota.dx   # rebota de lado
    if pelota.y <= 2 or pelota.y >= alto - 1:
        pelota.dy = -pelota.dy   # rebota arriba o abajo
    pantalla.rodear("redondo", color="azul", titulo="Pelota · Esc para salir")


pantalla.jugar(actualizar)
```

### `ejemplos/13_fracciones.py`

```python
import pantalla

pantalla.limpiar()
pantalla.cabecera("FRACCIONES")

a = pantalla.pedir_fraccion("Primera fracción: ", 3, 3)
b = pantalla.pedir_fraccion("Segunda fracción: ", 3, 5)

operacion = pantalla.elegir("¿Qué hago?", ["Sumar", "Restar", "Multiplicar", "Dividir"], 3, 7)
if operacion is None:
    raise SystemExit

signo = {"Sumar": "+", "Restar": "-", "Multiplicar": "·", "Dividir": ":"}[operacion]
if operacion == "Dividir" and b == 0:
    pantalla.escribir("No se puede dividir entre 0", 3, 10, color="rojo")
else:
    # escribir_cuenta la dibuja como en el cuaderno y pone el resultado
    pantalla.escribir_cuenta("%s %s %s" % (a, signo, b), 5, 10, color_resultado="verde")

pantalla.pie("Pulsa cualquier tecla para salir")
pantalla.tecla()
pantalla.limpiar()
```

### `ejemplos/14_sistemas.py`

```python
import pantalla

pantalla.limpiar()
pantalla.cabecera("SISTEMAS DE ECUACIONES")
pantalla.escribir("Escribe la matriz ampliada: los coeficientes y, en la última", 3, 3, color="gris")
pantalla.escribir("columna, los resultados.", 3, 4, color="gris")
pantalla.escribir("Por ejemplo, 2x + y = 5 y x - y = 1 es  [2  1 | 5]  y  [1  -1 | 1]", 3, 6, color="gris")
pantalla.esperar("Pulsa una tecla para empezar", 3, 8, color="amarillo")

pantalla.limpiar()
pantalla.cabecera("SISTEMAS DE ECUACIONES")
ampliada = pantalla.pedir_matriz("Ab", maximo=5)
if ampliada is None:
    raise SystemExit

pantalla.limpiar()
print("Así queda la matriz ampliada:")
pantalla.matriz(ampliada, ampliada=True)
print()
print("El sistema es", pantalla.clasificar_sistema(ampliada))
print()

pantalla.resolver_sistema(ampliada, pasos=True)
pantalla.esperar()
```

### `ejemplos/15_graficas.py`

```python
import math

import pantalla


def f(x):
    return x * x - 4


pantalla.limpiar()
print("y = x² - 4")
pantalla.grafica(f, -4, 4, ancho=60, alto=14)
print()

print("y = sin(x) y y = cos(x)")
pantalla.grafica([math.sin, math.cos], -2 * math.pi, 2 * math.pi, ancho=60, alto=10)
print()

notas = {"Ana": 8.5, "Luis": 6, "Marta": 9.75, "Pablo": 4}
pantalla.barras(notas, ancho=50, maximo=10, colores=["cian", "amarillo", "verde", "rojo"])
print()
print("La semana:", pantalla.minigrafica([12, 15, 19, 22, 24, 21, 18]))
pantalla.esperar()
```

### `ejemplos/16_formulario.py`

```python
import pantalla

pantalla.limpiar()
pantalla.cabecera("INSCRIPCIÓN AL TORNEO")

datos = pantalla.formulario({"Nombre": "texto", "Edad": "numero", "Contraseña": "contraseña"},
                            titulo="Tus datos")
if datos is None:
    raise SystemExit

juegos = pantalla.elegir_varios(["Ajedrez", "Damas", "Parchís", "Mus", "Dominó"],
                                titulo="¿A qué juegas?", minimo=1)
if juegos is None:
    raise SystemExit

pantalla.limpiar()
pantalla.cabecera("INSCRIPCIÓN AL TORNEO")
texto = "%s, %d años\nJuegas a: %s" % (datos["Nombre"], datos["Edad"], ", ".join(juegos))
pantalla.mensaje(texto, titulo="¡Apuntado!", color_borde="verde")
pantalla.limpiar()
```

### `ejemplos/17_pantalla_de_carga.py`

```python
import random

import pantalla


def generar_mapa():
    pantalla.pausa(1.2)     # como si tardara de verdad
    return [[random.choice("..,,~^") for _ in range(50)] for _ in range(12)]


def colocar_enemigos():
    pantalla.pausa(0.8)
    return [(random.randint(1, 50), random.randint(1, 12)) for _ in range(6)]


mapa, enemigos = pantalla.pantalla_de_carga(
    "AVENTURA", fuente="ansi_shadow", color="verde", color_final="cian", marco="redondo",
    tareas=[("Generando el mapa", generar_mapa),
            ("Colocando enemigos", colocar_enemigos),
            "Afinando los sonidos"],
    consejos=["Consejo: los enemigos no cruzan el agua (~)",
              "Consejo: las montañas (^) no se pueden pisar"],
)

pantalla.limpiar()
for y, fila in enumerate(mapa, 1):
    pantalla.escribir("".join(fila), 3, y + 1, color="verde")
for x, y in enemigos:
    pantalla.punto(x + 2, y + 1, "E", color="rojo")
pantalla.escribir("Hay %d enemigos escondidos" % len(enemigos), 3, 15, color="amarillo")
pantalla.esperar(x=3, y=17)
pantalla.limpiar()
```

### `ejemplos/18_vectores.py`

```python
import pantalla

pantalla.limpiar()
u = pantalla.pedir_vector("u", dimension=2)
v = pantalla.pedir_vector("v", dimension=2)
if u is None or v is None:
    pantalla.limpiar()
    raise SystemExit

pantalla.limpiar()
pantalla.cabecera(f"u = {u}    v = {v}")
ancho, alto = pantalla.dibujar_vectores({"u": u, "v": v, "u+v": u + v}, 2, 3, ancho=44, alto=15)

# las cuentas, con sus pasos, debajo del dibujo
pantalla.gotoxy(1, alto + 4)
pantalla.producto_escalar(u, v, pasos=True)
pantalla.modulo(u, pasos=True)
pantalla.modulo(v, pasos=True, nombre="v")
if abs(u) and abs(v):
    pantalla.angulo(u, v, pasos=True)
if pantalla.son_perpendiculares(u, v):
    pantalla.escribir("¡Son perpendiculares!", color="verde", nueva_linea=True)
elif pantalla.son_paralelos(u, v):
    pantalla.escribir("Son paralelos: uno es el otro por un número", color="amarillo", nueva_linea=True)

pantalla.esperar()
pantalla.limpiar()
```

### `ejemplos/19_polinomios.py`

```python
import pantalla

pantalla.limpiar()
pantalla.cabecera("POLINOMIOS")

texto = pantalla.pedir("Escribe un polinomio (por ejemplo x^3 - 2x^2 - x + 2): ", 2, 3)
try:
    p = pantalla.polinomio(texto)
except ValueError as e:
    pantalla.mensaje(str(e), titulo="Ups", color_borde="rojo")
    raise SystemExit

pantalla.gotoxy(1, 5)
print("p(x) =", p)
print()
# factorizar_polinomio busca las raíces con Ruffini y enseña cada paso
pantalla.factorizar_polinomio(p, pasos=True)

if p.grado == 2:
    a, b, c = p.coeficientes
    print()
    pantalla.ecuacion_segundo_grado(a, b, c, pasos=True)

pantalla.esperar()
pantalla.limpiar()
pantalla.cabecera("y = %s" % p)
pantalla.grafica(p, -5, 5, 3, 3, color="verde claro")
pantalla.esperar()
pantalla.limpiar()
```

### `ejemplos/20_estadistica.py`

```python
import pantalla

pantalla.limpiar()
pantalla.cabecera("NOTAS DE LA CLASE")

notas = []
pantalla.gotoxy(1, 3)
print("Escribe las notas una a una. Deja la línea vacía para acabar.")
while True:
    r = pantalla.pedir("Nota %d: " % (len(notas) + 1)).replace(",", ".")
    if not r:
        break
    try:
        notas.append(float(r) if "." in r else int(r))
    except ValueError:
        pantalla.escribir("Eso no es un número", color="rojo", nueva_linea=True)

if not notas:
    raise SystemExit

pantalla.limpiar()
pantalla.cabecera("%d notas" % len(notas))
ancho, alto = pantalla.histograma(notas, 2, 3, alto=10)
pantalla.estadisticas(notas, ancho + 6, 3)
pantalla.gotoxy(1, alto + 5)
pantalla.tabla_frecuencias(notas)

pantalla.esperar()
pantalla.limpiar()
```

### `ejemplos/21_practicar.py`

```python
import pantalla

pantalla.limpiar()
pantalla.cabecera("A PRACTICAR")
pantalla.gotoxy(1, 3)

# sin tema te deja elegir de la lista
aciertos = pantalla.practicar(preguntas=10)

if aciertos == 10:
    pantalla.mensaje("¡Todas bien!", titulo="Perfecto", color_borde="verde")
else:
    pantalla.esperar()
```

### `ejemplos/22_records.py`

```python
import random

import pantalla

pantalla.limpiar()
pantalla.cabecera("¿CUÁNTO TARDAS?")
pantalla.escribir("Escribe la letra que salga lo más rápido que puedas", 3, 3)
pantalla.cuenta_atras(3, 3, 5)

c = pantalla.cronometro()
for i in range(5):
    letra = random.choice("asdfjklñ")
    while pantalla.pedir("  %s  →  " % letra.upper(), 3, 7 + i).lower() != letra:
        pantalla.escribir("¡Esa no!", 25, 7 + i, color="rojo")
    pantalla.escribir("        ", 25, 7 + i)
tiempo = round(c.parar(), 2)

pantalla.escribir("Has tardado %s" % c, 3, 13, color="cian", negrita=True)
nombre = pantalla.pedir("¿Cómo te llamas? ", 3, 15)

# en los tiempos gana el más pequeño
puesto = pantalla.guardar_record(nombre, tiempo, "tiempos.json", menos_es_mejor=True)
if puesto == 1:
    pantalla.escribir("¡Nuevo récord!", 3, 16, color="amarillo", negrita=True)
elif puesto:
    pantalla.escribir("Has quedado el %d.º" % puesto, 3, 16)

pantalla.tabla_records("tiempos.json", 3, 18)
pantalla.esperar()
pantalla.limpiar()
```

### `ejemplos/23_espacio.py`

```python
import pantalla

PI = pantalla.plano("x + y + z = 3")
SIGMA = pantalla.plano("x - y = 1")
R = pantalla.recta((0, 0, 0), (1, 1, 1))

COSAS = {
    "Dos planos": {"π": PI, "σ": SIGMA},
    "Plano y recta": {"π": PI, "r": R},
    "Tres planos": {"π": PI, "σ": SIGMA, "z = 2": "z = 2"},
    "Un punto y su simétrico": {"π": PI, "P": (2, 2, 2), "P'": pantalla.simetrico((2, 2, 2), PI)},
}

opcion = "Dos planos"
while True:
    pantalla.limpiar()
    pantalla.cabecera("ESPACIO · arrastra el dibujo para girarlo")
    cosas = COSAS[opcion]
    # el dibujo se queda a la derecha del menú y se gira solo mientras el menú espera
    ancho = min(60, max(30, pantalla.ancho() - 42))
    alto = max(10, pantalla.alto() - 11)
    pantalla.dibujar_espacio(cosas, 41, 3, ancho=ancho, alto=alto, girar=True)

    # los puntos son tuplas, para posicion() solo valen planos y rectas
    nombres = [n for n in cosas if not isinstance(cosas[n], tuple)]
    if len(nombres) >= 2:
        texto = pantalla.posicion(*[cosas[n] for n in nombres])
        pantalla.escribir(", ".join(nombres) + ":", 3, 13, color="cian")
        pantalla.escribir(texto, 3, 14, color="cian", negrita=True)
    else:
        texto = round(pantalla.distancia(cosas["P"], PI), 2)
        pantalla.escribir("P está a %s de π" % texto, 3, 13, color="cian")

    opcion = pantalla.menu(list(COSAS) + ["Salir"], titulo="¿Qué miramos?", x=3, y=3, inicial=opcion)
    if opcion in (None, "Salir"):
        break

pantalla.limpiar()
```

### `ejemplos/24_modelos.py`

```python
import math
import os

import pantalla

pantalla.limpiar()
pantalla.cabecera("IMÁGENES Y MODELOS 3D")

foto = pantalla.pedir("Escribe el nombre de una foto (o pulsa Enter para saltarlo): ", 3, 3)
if foto and os.path.exists(foto):
    pantalla.imagen(foto, 3, 5, ancho=50, alto=16)
    pantalla.esperar(x=3, y=pantalla.alto() - 1)

    # la misma foto, pero en relieve: lo claro sube
    pantalla.ver_modelo(foto, relieve=0.4)
elif foto:
    pantalla.escribir("No encuentro esa foto", 3, 5, color="rojo")
    pantalla.esperar(x=3, y=7)

# un modelo .obj con sus colores (casa.mtl)
pantalla.ver_modelo(os.path.join(os.path.dirname(os.path.abspath(__file__)), "casa.obj"))

# una superficie z = f(x, y): las flechas la giran, + y - acercan, Esc sale
pantalla.ver_modelo(lambda x, y: math.sin(x) * math.cos(y))
pantalla.limpiar()
```

---

Fin de la guía de pantalla 1.1.0. Si dudas entre dos funciones, consulta su firma en la Referencia completa de la API y su ejemplo; si algo no está aquí, pantalla no lo tiene.
