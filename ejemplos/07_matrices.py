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
