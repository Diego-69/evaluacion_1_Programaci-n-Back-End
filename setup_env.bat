@echo off
REM Instala/actualiza dependencias del proyecto usando Python 3.12 (sin venv)
REM Ejecuta este script desde la raíz del proyecto.

echo ===============================
echo   Preparando entorno (Windows)
echo ===============================

REM Ir al directorio del script (raíz del proyecto)
pushd %~dp0

echo.
echo Actualizando pip...
py -3.12 -m pip install --upgrade pip
IF ERRORLEVEL 1 (
	echo Error actualizando pip. Verifica que Python 3.12 esté instalado y accesible con ^"py -3.12^".
	popd
	pause
	exit /b 1
)

echo.
echo Instalando dependencias del proyecto...
py -3.12 -m pip install --no-cache-dir -r requirements.txt
IF ERRORLEVEL 1 (
	echo Error instalando dependencias. Revisa el archivo requirements.txt.
	popd
	pause
	exit /b 1
)

echo.
echo Listo. Puedes iniciar el servidor con run_dev.bat
popd
pause
