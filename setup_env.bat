@echo off
echo Configurando ambiente virtual para o projeto Financas Pessoais...
echo.

cmd "cd C:\Users\andre.lopes.canteras\OneDrive - Boizito\Public\Backend\boizito_code\code_copilot_tst\financas_pessoais"

REM Ativar o ambiente virtual
call venv\Scripts\activate.bat

REM Instalar as dependências
echo Instalando dependências...
pip install -r requirements.txt

echo.
echo Ambiente virtual configurado com sucesso!
echo Para ativar o ambiente virtual manualmente, execute: venv\Scripts\activate.bat
echo Para executar o aplicativo, use: python main.py
echo.

REM Manter a janela aberta
cmd /k