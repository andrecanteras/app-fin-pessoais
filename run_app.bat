@echo off
echo Iniciando o aplicativo Financas Pessoais...
echo.

REM Mudar para o diretório do projeto
cd /d "C:\Users\andre.lopes.canteras\OneDrive - Boizito\Public\Backend\boizito_code\code_copilot_tst\financas_pessoais"

REM Ativar o ambiente virtual
call venv\Scripts\activate.bat

REM Executar o aplicativo
python main.py

REM Manter a janela aberta para ver mensagens de erro
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocorreu um erro ao executar o aplicativo.
    pause
) else (
    REM Desativar o ambiente virtual ao sair
    call venv\Scripts\deactivate.bat
)