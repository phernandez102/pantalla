# Cambios

## 1.0.0

- Geometría del espacio (2.º de bachillerato): `plano()` y `Plano` (por tres puntos, punto y normal, punto y dos vectores, o escrito), con la ecuación general, vectorial, paramétricas y segmentaria. `recta()` con puntos de tres números da una `Recta3D`, también escrita en continua, paramétricas o como corte de dos planos.
- `posicion()` de dos rectas, recta y plano, dos o tres planos, con `pasos=True` enseña los rangos (Rouché). `interseccion()`, `distancia()` (también entre rectas que se cruzan), `angulo()`, `proyeccion()`, `simetrico()`, `perpendicular_comun()`, `punto_medio()`, `plano_mediador()`, `area_triangulo()`, `volumen_tetraedro()`, `estan_alineados()` y `son_coplanarios()`.
- `ver_espacio()` enseña planos, rectas y puntos en 3D a pantalla completa y se gira con el ratón. `dibujar_espacio()` lo dibuja quieto. En las terminales que pintan imágenes (Sixel o el de kitty) los planos salen rellenos y transparentes, lo de detrás con rayitas, los planos iguales con su borde a trozos y los puntos con unas guías hasta el suelo. Con `estilo="puntos"`, con braille.
- `girar=True` en `dibujar_espacio()` y `dibujar_modelo()`: el dibujo se queda en su sitio y se gira arrastrándolo con el ratón mientras el programa espera un `menu()`, `tecla()`, `esperar_clic()`, `bucle()`... `limpiar()` lo quita.
- `imagen()`: fotos y dibujos (PNG, JPG, GIF, BMP, PPM) en la terminal sin instalar nada. Con Pillow abre más tipos. Sale de verdad en Windows Terminal, WezTerm, kitty, Ghostty, iTerm2, foot o Konsole, y con medios bloques ▀ de colores en cmd y la Terminal del Mac. También `estilo="letras"`.
- `ver_modelo()`, `dibujar_modelo()` y `modelo()`: modelos 3D `.obj` (con sus colores del `.mtl`) y `.stl`, fotos en relieve y superficies `z = f(x, y)`, con las caras iluminadas.
- Se sabe pintar imágenes con el protocolo de kitty además de con Sixel. Se pregunta a la terminal una sola vez.
- En el constructor web, el conversor de imágenes tiene dos formas nuevas: "Cuartos ▖▞▟", que prueba en cada letra cómo repartir sus cuatro trocitos en dos colores, y "Letras por su forma", que elige la letra que más se parece a ese trozo de la foto (no solo por lo clara que es). Con colores hace tramado, y la foto se encoge mejor.
- En la documentación web hay apartados de espacio e imágenes y modelos 3D, que se giran arrastrándolos.
- Ejemplos nuevos: 23 y 24, con una casita `casa.obj` para probar los modelos.
- En Linux y Mac, las teclas que pulsas durante una `pausa()` o una `cuenta_atras()` ya no salen escritas en la pantalla (`^[[A`...).
- `mensaje()` parte las líneas largas para que la ventana quepa en la pantalla.
- Las ayudas de abajo de `menu()`, `pedir_matriz()`, `ver_espacio()` y `ver_modelo()` quitan cosas si no caben, pero siempre dejan "Esc salir".
- Lo que se escribe en varias líneas (leyendas, pasos de las cuentas...) ya no se amontona en la última fila cuando no cabe por abajo.

## 0.6.0

- Polinomios: `Polinomio` y `polinomio("2x^3 - 3x + 1")`, que se suman, restan, multiplican, se evalúan con `p(2)` y tienen `derivada()`. `dividir_polinomios()`, `ruffini()` (con `pasos=True` dibuja la tabla), `raices()` y `factorizar_polinomio()`, que con `pasos=True` hace un Ruffini por cada raíz.
- `ecuacion_segundo_grado(a, b, c, pasos=True)` escribe el discriminante y la fórmula con los números puestos.
- Rectas: `Recta` y `recta()` por dos puntos, punto y vector, punto y pendiente o escrita (`"y = 2x + 1"`). Saca la ecuación general, explícita, punto-pendiente, vectorial, paramétricas y continua. `ecuaciones_recta()`, `posicion_rectas()`, `interseccion_rectas()`, `angulo_rectas()` y `distancia_punto_recta()`.
- Estadística: `media()`, `mediana()`, `moda()`, `varianza()`, `desviacion()`, `cuartiles()`, `tabla_frecuencias()` (también por intervalos), `histograma()` y `estadisticas()`.
- Cambios de base: `cambiar_base()`, `a_binario()`, `a_hexadecimal()` y `a_decimal()`, con `pasos=True` las divisiones entre la base o la suma de potencias.
- `practicar()`: ejercicios de tablas, sumas, divisiones, fracciones, potencias, raíces, ecuaciones, mcd, primos, binario, porcentajes y vectores, en tres niveles. Corrige cada respuesta y al final pone la nota.
- Para los juegos: `guardar_record()`, `leer_records()`, `mejor_record()` y `tabla_records()` guardan las puntuaciones en un archivo. `cronometro()` y `cuenta_atras()`.
- `grafica()` dibuja la línea con puntitos braille y sale mucho más fina. Con `estilo="puntos"` sale como antes.
- La demo tiene un apartado de mates con polinomios, estadística y practicar.
- En la documentación web están todas las funciones nuevas, y las de polinomios, rectas, estadística y bases tienen deslizadores.
- Ejemplos nuevos: 19 a 22.

## 0.5.0

- Vectores: `Vector` (una tupla que suma, resta y se multiplica por un número con `+`, `-`, `*` y `/`), `vector()` para escribirlo y `pedir_vector()` para pedirlo con las flechas.
- Cuentas: `sumar_vectores()`, `restar_vectores()`, `multiplicar_vector()`, `vector_entre()`, `producto_escalar()`, `producto_vectorial()`, `producto_mixto()`, `modulo()`, `unitario()`, `distancia()`, `angulo()` y `proyeccion()`. Con fracciones exactas, y el módulo sale exacto cuando la raíz lo es.
- `producto_escalar()`, `modulo()`, `angulo()` y `producto_vectorial()` con `pasos=True` escriben la cuenta entera (`|u| = √8 = 2√2 ≈ 2.8284`).
- `son_paralelos()`, `son_perpendiculares()` y `son_independientes()`.
- `dibujar_vectores()` los pinta con flechas en unos ejes, desde el origen o de un punto a otro. Las rayas van con puntitos braille para que salgan rectas, o con `estilo="rayas"` con ╱ ╲ │ ─.
- La demo tiene un apartado de vectores, y en la documentación web se pueden mover con deslizadores.
- Ejemplo nuevo: 18.

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
