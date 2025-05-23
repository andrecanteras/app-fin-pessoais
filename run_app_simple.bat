@echo off
echo Iniciando o aplicativo Financas Pessoais (versão simples)...
echo.

REM Mudar para o diretório do projeto
cd /d "%~dp0"

REM Ativar o ambiente virtual
call venv\Scripts\activate.bat

REM Verificar ambiente Python
echo Verificando ambiente Python...
where python
python -c "import sys; print('Python executável:', sys.executable)"

REM Executar o aplicativo simples
python -c "import sys; from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel; app = QApplication(sys.argv); window = QMainWindow(); window.setWindowTitle('Teste PyQt5'); window.setGeometry(100, 100, 400, 200); label = QLabel('PyQt5 está funcionando!', window); label.setGeometry(100, 80, 200, 40); window.show(); sys.exit(app.exec_())"

REM Desativar o ambiente virtual ao sair
call venv\Scripts\deactivate.bat