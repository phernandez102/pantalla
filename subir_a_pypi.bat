@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo.
echo  ==============================
echo   Subir pantalla a PyPI
echo  ==============================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo No encuentro Python. Instalalo desde python.org marcando "Add python.exe to PATH".
    goto fin
)

echo [1/5] Instalando build y twine...
python -m pip install --quiet --upgrade build twine
if errorlevel 1 goto error

echo [2/5] Pasando los tests...
set "PYTHONPATH=%~dp0src"
python -m unittest discover -s tests -q
if errorlevel 1 (
    echo.
    echo Hay tests que fallan. No subo nada.
    goto fin
)
set "PYTHONPATH="

echo [3/5] Construyendo el paquete...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
python -m build
if errorlevel 1 goto error
for /d %%d in (src\*.egg-info) do rmdir /s /q "%%d"

echo [4/5] Comprobando el paquete...
python -m twine check dist\*
if errorlevel 1 goto error

echo.
echo [5/5] Subir
if defined DONDE goto token
echo Donde lo subo?
echo    1 = PyPI de verdad   (pypi.org)
echo    2 = TestPyPI         (test.pypi.org, para probar antes)
set "DONDE=1"
set /p "DONDE=Escribe 1 o 2 y pulsa Enter [1]: "

:token
if defined TWINE_PASSWORD goto subir

echo.
echo Pega tu API token (empieza por pypi-). No se vera mientras lo pegas, es normal.
echo En esta ventana se pega con clic derecho.
for /f "usebackq delims=" %%t in (`powershell -NoProfile -Command "$s = Read-Host 'Token' -AsSecureString; [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s))"`) do set "TWINE_PASSWORD=%%t"
if not defined TWINE_PASSWORD (
    echo No has pegado ningun token.
    goto fin
)

:subir
set "TWINE_USERNAME=__token__"

if "%DONDE%"=="2" (
    python -m twine upload --non-interactive --repository testpypi dist\*
) else (
    python -m twine upload --non-interactive dist\*
)
if errorlevel 1 goto error

echo.
if "%DONDE%"=="2" (
    echo Subido a TestPyPI: https://test.pypi.org/project/pantalla/
    echo Para probarlo: pip install --index-url https://test.pypi.org/simple/ pantalla
) else (
    echo Subido! https://pypi.org/project/pantalla/
    echo Ya se puede instalar con: pip install pantalla
)
goto fin

:error
echo.
echo Algo ha fallado. Mira el mensaje de arriba.
echo  - "File already exists": esa version ya esta subida. Sube el numero de version
echo    en pyproject.toml y en src\pantalla\__init__.py y vuelve a probar.
echo  - "403 Forbidden" o "Invalid API Token": el token esta mal o es de la otra web
echo    (el de TestPyPI no vale para PyPI y al reves).

:fin
set "TWINE_PASSWORD="
echo.
pause
