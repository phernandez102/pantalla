# Cambios

## 0.4.0

- Matrices: `sumar_matrices()`, `restar_matrices()`, `multiplicar_matrices()`, `transpuesta()`, `identidad()`, `traza()`, `determinante()`, `inversa()`, `rango()` y `potencia_matriz()`. Todo con fracciones exactas.
- Gauss: `escalonar()` (con `pasos=True` enseña cada operación y con `reducida=True` hace Gauss-Jordan), `resolver_sistema()` y `clasificar_sistema()`.
- `matriz(..., ampliada=True)` pinta la raya de la matriz ampliada.
- Fracciones: `fraccion()`, `pedir_fraccion()`, `calcular()` y `escribir_cuenta()`, que dibuja la cuenta como en el cuaderno.
- Números: `mcd()`, `mcm()`, `es_primo()`, `divisores()`, `factorizar()` y `descomponer()`.
- Gráficas: `grafica()` para funciones (una o varias), `barras()` y `minigrafica()`.
- `elegir_varios()` para marcar varias opciones y `formulario()` para pedir varias cosas a la vez.
- `barra_progreso()` con `estilo=` (bloques, suave, linea, ascii, puntos, cuadros, circulos, rombos, flechas y rayas), `color_final=` para que cambie de color y `texto=` delante. `lista_barras()` dice cuáles hay.
- `pantalla_de_carga()`: título (también en letras grandes), barra, el paso que se está haciendo y consejos. Vale de mentira con `segundos=`, con una lista de `tareas` o con `with` para moverla tú. Con `total=None` la barra va y viene.
- En `pantalla.ayuda()` las barras, las cargas y los spinners tienen su propio apartado.
- La demo (`python -m pantalla`) tiene apartados de fracciones, gráficas y pantallas de carga, y la de matrices hace más cosas.
- En el constructor web las barras tienen estilo y color final.
- En la documentación web hay un buscador (`/` o Ctrl+K) y una barra que al bajar se queda como pastilla, con un botón para volver arriba. Las gráficas, `barras()`, `minigrafica()`, `mcd()` y `descomponer()` tienen deslizadores y se dibujan en directo.
- Ejemplos nuevos: 13 a 17.

## 0.3.1

- El paquete ya solo lleva la librería (antes iban también la web y otros archivos que no hacían falta).
- README con capturas.

## 0.3.0

- Letras ASCII: `grande()` y `texto_grande()` con `fuente=` (32 fuentes FIGlet). `lista_fuentes()` dice cuáles hay.
- `arte()` para dibujar arte ASCII con un color por letra.
- Ratón: `activar_raton()`, `esperar_clic()`, `leer_raton()`, `posicion_raton()`, `zona()`, `boton()`, `botones()` y `bucle()`. Con `arrastrar=True` se puede pintar como con un lápiz.
- Spinners: `spinner()` y `lista_spinners()`, con `bien()`, `mal()`, `aviso()` e `info()` al acabar.
- Juegos sin bucles: `jugar()`, `Sprite` (con `capa=`), `sprites()`, `cada()`, `fotograma()` y `pulsada()`.
- `menu()`: la línea de ayuda se puede mover con `ayuda_x`, `ayuda_y` y `color_ayuda`.
- `diseno()` entiende el arte y las fuentes del constructor web.
- Para los que empiezan:
  - en IDLE (Windows) el programa se abre solo en una ventana de cmd;
  - los nombres valen con tildes y ñ (`tamaño()`, `diseño()`);
  - si escribes mal una función te dice cuál querías;
  - las teclas se comparan sin mirar mayúsculas (`tecla == "Intro"`);
  - si se te olvida `global` en un juego te dice qué poner.
- Arreglado: escribir desde dos hilos a la vez mezclaba letras.
- Arreglado: con la salida mandada a un archivo en Windows, `caja()` daba error.
- Probado en Python 3.8, 3.11, 3.13 y 3.14, en Windows y en Linux.
- Las fuentes vienen de pyfiglet y los spinners de cli-spinners (los créditos están en el README).

## 0.2.0

- `menu()` con `ayudas`, `iconos`, secciones (con un diccionario) y scroll.
- Nuevas: `elegir()`, `calculando()`, `cabecera()`, `pie()`, `matriz()`, `pedir_matriz()`, `regla()`, `depurar()`, `diseno()` y `ayuda()`.
- Constructor web en `docs/index.html`.
- Arreglado: al escribir muy rápido en un menú se perdían teclas.

## 0.1.0

- Primera versión.
