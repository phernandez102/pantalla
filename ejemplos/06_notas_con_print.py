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
