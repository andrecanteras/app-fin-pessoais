"""
Script para recalcular e equalizar os saldos das contas.
Este script recalcula o saldo atual de cada conta com base no saldo inicial
e todas as transações registradas no banco de dados.
"""

import os
import sys
from decimal import Decimal
from dotenv import load_dotenv, dotenv_values

# Adicionar o diretório raiz do projeto ao caminho de busca do Python
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.database.connection import DatabaseConnection
from src.models.conta import Conta

def print_header(title):
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 50)
    print(f"{title.center(50)}")
    print("=" * 50)

def recalcular_saldos():
    """Recalcula o saldo atual de todas as contas com base nas transações."""
    print_header("RECALCULANDO SALDOS DAS CONTAS")
    
    db = DatabaseConnection()
    try:
        cursor = db.get_cursor()
        
        # Buscar todas as contas
        cursor.execute("SELECT id, nome FROM financas_pessoais.conta_dimensao WHERE ativo = 1")
        contas = cursor.fetchall()
        
        if not contas:
            print("Nenhuma conta encontrada.")
            return
        
        for conta_row in contas:
            conta_id = conta_row.id
            conta_nome = conta_row.nome
            
            print(f"\nProcessando conta: {conta_nome} (ID: {conta_id})")
            
            # Buscar saldo inicial
            cursor.execute("""
                SELECT saldo_inicial, saldo_atual 
                FROM financas_pessoais.conta_saldos 
                WHERE conta_dimensao_id = ?
            """, (conta_id,))
            
            saldo_row = cursor.fetchone()
            if not saldo_row:
                print(f"  Erro: Registro de saldo não encontrado para a conta {conta_nome}")
                continue
            
            saldo_inicial = saldo_row.saldo_inicial
            saldo_atual_antigo = saldo_row.saldo_atual
            
            print(f"  Saldo inicial: R$ {float(saldo_inicial):.2f}")
            print(f"  Saldo atual registrado: R$ {float(saldo_atual_antigo):.2f}")
            
            # Buscar todas as transações da conta
            cursor.execute("""
                SELECT tipo, valor 
                FROM financas_pessoais.transacoes 
                WHERE conta_id = ?
                ORDER BY data_transacao, id
            """, (conta_id,))
            
            transacoes = cursor.fetchall()
            
            # Recalcular o saldo
            saldo_calculado = Decimal(saldo_inicial)
            
            for transacao in transacoes:
                if transacao.tipo == 'R':  # Receita
                    saldo_calculado += Decimal(transacao.valor)
                else:  # Despesa
                    saldo_calculado -= Decimal(transacao.valor)
            
            print(f"  Saldo recalculado: R$ {float(saldo_calculado):.2f}")
            
            # Verificar se há diferença
            diferenca = saldo_calculado - saldo_atual_antigo
            
            if diferenca != 0:
                print(f"  Diferença encontrada: R$ {float(diferenca):.2f}")
                
                # Atualizar o saldo
                cursor.execute("""
                    UPDATE financas_pessoais.conta_saldos 
                    SET saldo_atual = ? 
                    WHERE conta_dimensao_id = ?
                """, (saldo_calculado, conta_id))
                
                db.commit()
                print(f"  Saldo atualizado com sucesso!")
            else:
                print(f"  Saldo já está correto.")
        
        print("\nProcesso de recálculo de saldos concluído!")
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao recalcular saldos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Carregar variáveis de ambiente
    load_dotenv(override=True)
    
    # Verificar se as variáveis necessárias estão definidas
    required_vars = ['DB_SERVER', 'DB_DATABASE', 'DB_USERNAME', 'DB_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("ERRO: As seguintes variáveis de ambiente estão faltando:")
        for var in missing_vars:
            print(f"- {var}")
        print("Por favor, configure o arquivo .env com as credenciais do banco de dados.")
        sys.exit(1)
    
    # Executar o recálculo de saldos
    recalcular_saldos()
