@echo off
rem Abre la demo del raton con la libreria de esta carpeta (no hace falta instalarla).
cd /d "%~dp0"
set PYTHONPATH=%~dp0..\src
chcp 65001 >nul
title Demo del raton - pantalla
python 09_raton.py
echo.
pause
