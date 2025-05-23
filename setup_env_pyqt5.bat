@echo off
echo Configurando ambiente para Financas Pessoais com PyQt5...
echo.

REM Mudar para o diretório do projeto
cd /d "%~dp0"

REM Verificar se o ambiente virtual existe
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)

REM Ativar o ambiente virtual
call venv\Scripts\activate.bat

REM Verificar ambiente Python
echo Verificando ambiente Python...
where python
python -c "import sys; print('Python executável:', sys.executable)"

REM Atualizar pip
echo Atualizando pip...
python -m pip install --upgrade pip

REM Instalar dependências básicas
echo Instalando dependências básicas...
pip install python-dotenv==1.0.0 pyodbc==4.0.39 pandas==2.0.3 matplotlib==3.7.2 pytest==7.4.0

REM Desinstalar PyQt6 se existir
echo Removendo versões anteriores de PyQt6/PySide6...
pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip PySide6

REM Instalar PyQt5
echo Instalando PyQt5...
pip install PyQt5==5.15.9

REM Verificar instalação
echo.
echo Verificando instalação do PyQt5...
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 instalado com sucesso!')"

REM Listar pacotes instalados
echo.
echo Pacotes instalados no ambiente virtual:
pip list

echo.
echo Ambiente configurado com sucesso!
echo Para ativar o ambiente virtual manualmente, execute: venv\Scripts\activate.bat
echo Para executar o aplicativo, use: run_app.bat
echo.

pause