@echo off
echo Convertendo projeto para PyQt5...
echo.

REM Mudar para o diretório do projeto
cd /d "%~dp0"

REM Ativar o ambiente virtual
call venv\Scripts\activate.bat

REM Verificar ambiente Python
echo Verificando ambiente Python...
where python
python -c "import sys; print('Python executável:', sys.executable)"

REM Criar backup dos arquivos originais
echo Criando backup dos arquivos originais...
if not exist backup mkdir backup
if not exist backup\src mkdir backup\src
if not exist backup\src\views mkdir backup\src\views

copy main.py backup\main.py
copy src\views\main_window.py backup\src\views\main_window.py
copy src\views\dashboard_view.py backup\src\views\dashboard_view.py

echo Backup concluído!
echo.

echo Conversão concluída!
echo Agora você pode executar o aplicativo com PyQt5 usando run_app.bat
echo.

pause