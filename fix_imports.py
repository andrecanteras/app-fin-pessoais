import os
import sys
import shutil

def main():
    """Script para corrigir os problemas de importação no projeto."""
    print("Corrigindo problemas de importação no projeto...")
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('src/views'):
        print("Erro: Execute este script no diretório raiz do projeto.")
        sys.exit(1)
    
    # Criar diretório de backup se não existir
    if not os.path.exists('backup'):
        os.makedirs('backup')
        print("Diretório de backup criado.")
    
    # Backup do arquivo __init__.py
    init_path = 'src/views/__init__.py'
    if os.path.exists(init_path):
        backup_path = 'backup/__init__.py.bak'
        shutil.copy2(init_path, backup_path)
        print(f"Backup de {init_path} criado em {backup_path}")
        
        # Modificar o arquivo __init__.py
        with open(init_path, 'w') as f:
            f.write("# Arquivo modificado para evitar importações automáticas\n")
            f.write("# que causam problemas com PyQt6\n\n")
            f.write("# Deixe este arquivo vazio para evitar importações circulares\n")
        print(f"Arquivo {init_path} modificado.")
    
    print("\nProblemas de importação corrigidos!")
    print("Agora você pode executar o aplicativo com 'python simple_app.py'")
    print("ou com o script 'run_app_simple.bat'")

if __name__ == "__main__":
    main()