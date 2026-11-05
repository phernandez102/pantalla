# Cómo publicar `pantalla` en PyPI

## 0. Antes de nada

1. **Mira si el nombre está libre**: abre <https://pypi.org/project/pantalla/>. Si sale "404 Not Found", está libre (lo estaba el 4 de noviembre de 2026). Si sale una página con otro proyecto, está cogido y tendrás que cambiar `name` en `pyproject.toml` (por ejemplo `pantalla-tic` o `pantalla-facil`). El `import pantalla` puede seguir igual.
2. El autor (`pyproject.toml` y `LICENSE`) y los enlaces de GitHub (`README.md` y `pyproject.toml`) ya están puestos con el usuario `phernandez102`.

## 1. Crear las cuentas

- Cuenta de pruebas: <https://test.pypi.org/account/register/>
- Cuenta de verdad: <https://pypi.org/account/register/>

Son dos cuentas distintas. Las dos te obligan a activar la verificación en dos pasos (con una app como Google Authenticator).

En cada una crea un **token** (Account settings → API tokens → Add API token, con alcance "Entire account" la primera vez). Cópialo: empieza por `pypi-` y solo se ve una vez.

## 2. Instalar las herramientas

```
pip install --upgrade build twine
```

## 3. Probar que todo va

Desde la carpeta del proyecto:

```
python -m unittest discover -s tests
```

Tienen que salir 263 tests y al final `OK`.

## 4. Construir el paquete

```
python -m build
```

Esto crea la carpeta `dist/` con dos archivos: `pantalla-0.3.0.tar.gz` y `pantalla-0.3.0-py3-none-any.whl`.

Comprueba que están bien:

```
python -m twine check dist/*
```

## 5. Subirlo primero a la web de pruebas

```
python -m twine upload --repository testpypi dist/*
```

Cuando pida el usuario escribe `__token__` y como contraseña pega el token de **TestPyPI**.

Pruébalo en otro ordenador (o en un entorno virtual):

```
pip install --index-url https://test.pypi.org/simple/ pantalla
python -m pantalla
```

## 6. Subirlo de verdad

```
python -m twine upload dist/*
```

Usuario `__token__` y el token de **PyPI** (el de verdad). A partir de ahí cualquiera puede hacer:

```
pip install pantalla
```

## 7. Sacar una versión nueva

1. Cambia el número de versión en **dos sitios**: `pyproject.toml` (`version = "0.3.1"`) y `src/pantalla/__init__.py` (`__version__ = "0.3.1"`).
2. Borra la carpeta `dist/` vieja.
3. Repite los pasos 4 y 6.

PyPI no deja subir dos veces la misma versión, ni aunque borres la anterior.

Para no tener que escribir el token cada vez, puedes guardarlo en un archivo `.pypirc` en tu carpeta de usuario:

```ini
[pypi]
username = __token__
password = pypi-XXXXXXXX
```

(No subas nunca ese archivo a GitHub.)


# Cómo poner el constructor web en GitHub Pages

El constructor son dos archivos: `docs/index.html` y `docs/fuentes.js` (las letras ASCII). Tienen que estar juntos en la misma carpeta. No necesita servidor ni instalar nada.

1. Crea un repositorio en GitHub que se llame `pantalla` (público).
2. Sube todos los archivos del proyecto. Lo más fácil sin saber git: en la página del repositorio, *Add file → Upload files* y arrastra todo el contenido de la carpeta (incluida la carpeta `docs`).
   Con git sería:
   ```
   git init
   git add .
   git commit -m "pantalla 0.3.0"
   git branch -M main
   git remote add origin https://github.com/phernandez102/pantalla.git
   git push -u origin main
   ```
3. En el repositorio: **Settings → Pages**. En *Build and deployment* elige:
   - Source: **Deploy from a branch**
   - Branch: **main** y la carpeta **/docs**
   - Pulsa **Save**.
4. Espera un minuto y entra en `https://phernandez102.github.io/pantalla/`. Ahí está el constructor.

Cada vez que cambies `docs/index.html` y lo subas, la web se actualiza sola en un minuto.

Lo que dibuja cada persona en el constructor se guarda en su navegador, así que si recarga la página no lo pierde. No se guarda en ningún servidor.
