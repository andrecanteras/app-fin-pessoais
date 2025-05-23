"""
Script para testar diretamente a criação de transações no banco de dados.
"""

import os
import sys
import importlib.util

# Adicionar o diretório raiz do projeto ao caminho de busca do Python
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv, dotenv_values
from src.database.connection import DatabaseConnection

def print_header(title):
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 50)
    print(f"{title.center(50)}")
    print("=" * 50)

def criar_transacao_direta():
    """Cria uma transação diretamente no banco de dados."""
    print_header("CRIAR TRANSAÇÃO DIRETAMENTE NO BANCO")
    
    db = DatabaseConnection()
    try:
        cursor = db.get_cursor()
        
        # Obter uma categoria
        cursor.execute("SELECT TOP 1 id FROM financas_pessoais.categorias WHERE tipo = 'R' AND ativo = 1")
        row = cursor.fetchone()
        if not row:
            print("Nenhuma categoria encontrada.")
            return False
        categoria_id = row.id
        
        # Obter uma conta
        cursor.execute("SELECT TOP 1 id, nome, saldo_atual FROM financas_pessoais.contas WHERE ativo = 1")
        row = cursor.fetchone()
        if not row:
            print("Nenhuma conta encontrada.")
            return False
        conta_id = row.id
        conta_nome = row.nome
        saldo_atual = row.saldo_atual
        
        # Obter um meio de pagamento
        cursor.execute("SELECT TOP 1 id FROM financas_pessoais.meios_pagamento WHERE ativo = 1")
        row = cursor.fetchone()
        if not row:
            print("Nenhum meio de pagamento encontrado.")
            return False
        meio_pagamento_id = row.id
        
        # Dados da transação
        descricao = "Transação de teste direta"
        valor = Decimal("100.00")
        data_transacao = datetime.now().date()
        tipo = "R"  # Receita
        descricao_pagamento = "TESTE DIRETO"
        local_transacao = "Teste Direto"
        observacao = "Transação criada diretamente no banco"
        
        # Inserir transação
        cursor.execute("""
            INSERT INTO financas_pessoais.transacoes 
            (descricao, valor, data_transacao, tipo, categoria_id, conta_id, 
             meio_pagamento_id, descricao_pagamento, local_transacao, observacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (descricao, valor, data_transacao, tipo, 
              categoria_id, conta_id, meio_pagamento_id,
              descricao_pagamento, local_transacao, observacao))
        
        # Obter o ID gerado
        cursor.execute("SELECT @@IDENTITY")
        transacao_id = cursor.fetchone()[0]
        
        # Atualizar o saldo da conta
        novo_saldo = saldo_atual + valor if tipo == 'R' else saldo_atual - valor
        cursor.execute("UPDATE financas_pessoais.contas SET saldo_atual = ? WHERE id = ?", 
                      (novo_saldo, conta_id))
        
        # Commit das alterações
        db.commit()
        
        print(f"Transação criada com sucesso! ID: {transacao_id}")
        print(f"Conta: {conta_nome}")
        print(f"Saldo anterior: R$ {float(saldo_atual):.2f}")
        print(f"Novo saldo: R$ {float(novo_saldo):.2f}")
        
        # Verificar se a transação foi realmente criada
        cursor.execute("SELECT * FROM financas_pessoais.transacoes WHERE id = ?", (transacao_id,))
        row = cursor.fetchone()
        if row:
            print(f"Verificação: Transação ID={transacao_id} encontrada no banco de dados.")
            
            # Mostrar detalhes da transação
            print("\nDetalhes da transação:")
            print(f"ID: {row.id}")
            print(f"Descrição: {row.descricao}")
            print(f"Valor: R$ {float(row.valor):.2f}")
            print(f"Data: {row.data_transacao.strftime('%d/%m/%Y')}")
            print(f"Tipo: {'Receita' if row.tipo == 'R' else 'Despesa'}")
            print(f"Categoria ID: {row.categoria_id}")
            print(f"Conta ID: {row.conta_id}")
            print(f"Meio de Pagamento ID: {row.meio_pagamento_id}")
            print(f"Descrição do Pagamento: {row.descricao_pagamento}")
            print(f"Local da Transação: {row.local_transacao}")
            print(f"Observação: {row.observacao}")
            print(f"Data de Criação: {row.data_criacao}")
            
            return transacao_id
        else:
            print(f"ERRO: Transação ID={transacao_id} não encontrada no banco de dados após inserção direta.")
            return None
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao criar transação diretamente: {e}")
        return None
    finally:
        db.close()

def excluir_transacao_direta(transacao_id):
    """Exclui uma transação diretamente do banco de dados."""
    print_header(f"EXCLUIR TRANSAÇÃO ID={transacao_id} DIRETAMENTE")
    
    # Primeiro, obter informações da transação
    db_info = DatabaseConnection()
    try:
        cursor_info = db_info.get_cursor()
        
        # Obter informações da transação
        cursor_info.execute("SELECT * FROM financas_pessoais.transacoes WHERE id = ?", (transacao_id,))
        row = cursor_info.fetchone()
        if not row:
            print(f"Transação ID={transacao_id} não encontrada.")
            return False
        
        # Guardar os dados necessários
        conta_id = row.conta_id
        tipo = row.tipo
        valor = row.valor
        
        # Se tiver conta associada, obter informações da conta
        conta_nome = None
        saldo_atual = None
        
        if conta_id:
            cursor_info.execute("SELECT saldo_atual, nome FROM financas_pessoais.contas WHERE id = ?", (conta_id,))
            conta_row = cursor_info.fetchone()
            if conta_row:
                saldo_atual = conta_row.saldo_atual
                conta_nome = conta_row.nome
    except Exception as e:
        print(f"Erro ao obter informações da transação: {e}")
        return False
    finally:
        db_info.close()
    
    # Agora, atualizar o saldo da conta e excluir a transação
    db_update = DatabaseConnection()
    try:
        cursor_update = db_update.get_cursor()
        
        # Reverter o efeito da transação no saldo da conta
        if conta_id and saldo_atual is not None:
            # Se era receita, subtrai; se era despesa, adiciona
            novo_saldo = saldo_atual - valor if tipo == 'R' else saldo_atual + valor
            
            # Atualizar saldo da conta
            cursor_update.execute("UPDATE financas_pessoais.contas SET saldo_atual = ? WHERE id = ?", 
                          (novo_saldo, conta_id))
            
            print(f"Saldo da conta {conta_nome} atualizado:")
            print(f"Saldo anterior: R$ {float(saldo_atual):.2f}")
            print(f"Novo saldo: R$ {float(novo_saldo):.2f}")
        
        # Excluir a transação
        cursor_update.execute("DELETE FROM financas_pessoais.transacoes WHERE id = ?", (transacao_id,))
        
        # Commit das alterações
        db_update.commit()
        
        print(f"Transação ID={transacao_id} excluída com sucesso!")
        return True
        
    except Exception as e:
        db_update.rollback()
        print(f"Erro ao excluir transação diretamente: {e}")
        return False
    finally:
        db_update.close()

def executar_testes():
    """Executa os testes diretos no banco de dados."""
    print_header("TESTE DIRETO DE TRANSAÇÕES")
    
    # Criar transação diretamente
    transacao_id = criar_transacao_direta()
    if not transacao_id:
        print("Falha ao criar transação diretamente. Abortando testes.")
        return
    
    # Excluir transação diretamente
    if not excluir_transacao_direta(transacao_id):
        print("Falha ao excluir transação diretamente.")
    
    print("\n===== TESTES CONCLUÍDOS =====")

if __name__ == "__main__":
    # Carregar variáveis de ambiente
    load_dotenv(override=True)
    
    # Executar testes
    executar_testes()