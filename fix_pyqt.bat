@echo off
echo Corrigindo instalacao do PyQt6...
echo.

REM Ativar o ambiente virtual
call venv\Scripts\activate.bat

REM Desinstalar versões antigas do PyQt6
echo Desinstalando versoes antigas do PyQt6...
pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip

REM Instalar PySide6 como alternativa ao PyQt6
echo Instalando PySide6 como alternativa...
pip install PySide6==6.5.2

echo.
echo Instalacao concluida!
echo Para executar o aplicativo, use o script run_app.bat
echo.

pause