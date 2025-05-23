@echo off
echo Corrigindo problemas de compatibilidade do Qt...
echo.

REM Verificar ambiente Python
echo Verificando ambiente Python...
where python
python -c "import sys; print(sys.executable)"

REM Ativar o ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Verificar novamente após ativação
echo Verificando ambiente Python após ativação...
where python
python -c "import sys; print(sys.executable)"

REM Desinstalar versões atuais do PyQt6 e PySide6
echo Desinstalando versoes atuais do PyQt6 e PySide6...
pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip PySide6

REM Fazer downgrade do NumPy para versão 1.x
echo Fazendo downgrade do NumPy para versão 1.x...
pip uninstall -y numpy
pip install numpy==1.24.3

REM Instalar PyQt5 como alternativa mais estável
echo Instalando PyQt5 como alternativa mais estável...
pip install PyQt5==5.15.9

echo.
echo Instalacao concluida!
echo Para executar o aplicativo, use o script run_app.bat
echo.

pause