@echo off
REM Inicia el servidor FastAPI (Uvicorn) en modo desarrollo
REM Ejecuta este script desde la raíz del proyecto.

REM Ir al directorio del script (raíz del proyecto)
pushd %~dp0

echo Iniciando Uvicorn en http://127.0.0.1:8000 ...
py -3.12 -m uvicorn main:app --reload
IF ERRORLEVEL 1 (
	echo Error al iniciar Uvicorn. Asegurate de haber ejecutado setup_env.bat y que Python 3.12 este instalado.
	popd
	pause
	exit /b 1
)

popd
