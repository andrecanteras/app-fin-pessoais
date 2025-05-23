"""
Script para executar os testes do aplicativo de finanças pessoais.
Este script configura o caminho de busca do Python para incluir o diretório raiz do projeto.
"""

import os
import sys
import importlib

# Adicionar o diretório raiz do projeto ao caminho de busca do Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def run_test(test_module):
    """Executa um módulo de teste específico."""
    try:
        # Importar o módulo de teste
        module = importlib.import_module(f"tests.{test_module}")
        
        # Se o módulo tem uma função executar_testes, chamá-la
        if hasattr(module, "executar_testes"):
            module.executar_testes()
        # Se o módulo tem uma função menu_principal, chamá-la
        elif hasattr(module, "menu_principal"):
            module.menu_principal()
        else:
            print(f"O módulo {test_module} não tem uma função executar_testes ou menu_principal.")
    except ImportError as e:
        print(f"Erro ao importar o módulo de teste {test_module}: {e}")
    except Exception as e:
        print(f"Erro ao executar o teste {test_module}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python run_test.py <nome_do_teste>")
        print("Testes disponíveis:")
        print("  test_conta")
        print("  test_categoria")
        print("  test_meio_pagamento")
        print("  test_transacao_updated")
        sys.exit(1)
    
    test_module = sys.argv[1]
    run_test(test_module)