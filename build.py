"""
Script para criar o executável do sistema de finanças pessoais.
"""
import PyInstaller.__main__
import os
import shutil
import time

def clean_build_dirs():
    """Limpa diretórios de build manualmente."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                print(f"Limpando diretório: {dir_name}")
                shutil.rmtree(dir_name)
                time.sleep(0.5)  # Pequena pausa
            except PermissionError:
                print(f"Aviso: Não foi possível limpar {dir_name}. Continuando...")
            except Exception as e:
                print(f"Erro ao limpar {dir_name}: {e}")

# Limpar diretórios antes de começar
clean_build_dirs()

# Verificar se existe ícone
icon_path = None
icon_files = ['assets/icon.ico', 'assets/icon.png', 'assets/app.ico', 'assets/app.png']

for icon_file in icon_files:
    if os.path.exists(icon_file):
        icon_path = icon_file
        break

# Parâmetros base do PyInstaller
params = [
    'main.py',
    '--name=Financas_Pessoais',
    '--windowed',
    '--onefile',
    '--add-data=.env;.',
    '--add-data=assets;assets',  # Incluir pasta assets
    '--hidden-import=PyQt5',
    '--hidden-import=pyodbc',
    '--noconfirm',
]

# Adicionar ícone se encontrado
if icon_path:
    params.append(f'--icon={icon_path}')
    print(f"Usando ícone: {icon_path}")
else:
    print("Nenhum ícone encontrado. Executável será criado sem ícone.")

# Executar PyInstaller
try:
    PyInstaller.__main__.run(params)
    print("\nBuild concluído com sucesso!")
    print("Executável disponível em: dist/Financas_Pessoais.exe")
except Exception as e:
    print(f"Erro durante o build: {e}")
    print("Tentando novamente sem limpeza automática...")
    
    # Remover --clean e tentar novamente
    if '--clean' in params:
        params.remove('--clean')
    
    try:
        PyInstaller.__main__.run(params)
        print("\nBuild concluído com sucesso!")
        print("Executável disponível em: dist/Financas_Pessoais.exe")
    except Exception as e2:
        print(f"Erro persistente: {e2}")
        print("Tente executar o comando manualmente ou fechar todos os programas que possam estar usando os arquivos.")