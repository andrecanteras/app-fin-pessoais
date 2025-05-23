"""
Script para testar as funcionalidades do modelo MeioPagamento.
"""

import os
import sys
import importlib.util

# Verificar se o script está sendo executado diretamente ou através do run_test.py
if __name__ == "__main__":
    # Adicionar o diretório raiz do projeto ao caminho de busca do Python
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, project_root)

from dotenv import load_dotenv, dotenv_values
from src.models.meio_pagamento import MeioPagamento
from src.models.conta import Conta
from src.models.conta_dimensao import ContaDimensao
from src.database.connection import DatabaseConnection

def clear_screen():
    """Limpa a tela do console."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 50)
    print(f"{title.center(50)}")
    print("=" * 50)

def print_meio_pagamento(meio_pagamento):
    """Imprime os detalhes de um meio de pagamento."""
    if not meio_pagamento:
        print("Meio de pagamento não encontrado.")
        return
    
    print(f"ID: {meio_pagamento.id}")
    print(f"Nome: {meio_pagamento.nome}")
    print(f"Tipo: {meio_pagamento.tipo}")
    print(f"Descrição: {meio_pagamento.descricao or 'N/A'}")
    
    # Mostrar conta associada, se houver
    if meio_pagamento.conta_id:
        # Tentar buscar a conta diretamente da dimensão
        conta_dimensao = ContaDimensao.buscar_por_id(meio_pagamento.conta_id)
        if conta_dimensao:
            print(f"Conta: {conta_dimensao.nome}")
        else:
            # Tentar usar a propriedade conta do meio de pagamento
            conta = meio_pagamento.conta
            print(f"Conta: {conta.nome if conta else 'N/A'}")
    else:
        print("Conta: N/A")
    
    print(f"Data de Criação: {meio_pagamento.data_criacao}")
    print(f"Ativo: {'Sim' if meio_pagamento.ativo else 'Não'}")
    print("-" * 50)

def listar_meios_pagamento():
    """Lista todos os meios de pagamento."""
    print_header("LISTAR MEIOS DE PAGAMENTO")
    
    # Criar uma única conexão com o banco de dados
    db = DatabaseConnection()
    try:
        cursor = db.get_cursor()
        
        # Buscar todos os meios de pagamento
        cursor.execute("SELECT * FROM financas_pessoais.meios_pagamento ORDER BY nome")
        rows = cursor.fetchall()
        
        if not rows:
            print("Nenhum meio de pagamento encontrado.")
            return
        
        print(f"Total de meios de pagamento: {len(rows)}")
        print("-" * 50)
        
        # Mostrar cada meio de pagamento
        for row in rows:
            print(f"ID: {row.id}")
            print(f"Nome: {row.nome}")
            print(f"Tipo: {row.tipo}")
            print(f"Descrição: {row.descricao or 'N/A'}")
            
            # Mostrar conta associada, se houver
            if row.conta_id:
                cursor.execute("SELECT nome FROM financas_pessoais.conta_dimensao WHERE id = ?", (row.conta_id,))
                conta_row = cursor.fetchone()
                if conta_row:
                    print(f"Conta: {conta_row.nome}")
                else:
                    print("Conta: N/A")
            else:
                print("Conta: N/A")
            
            print(f"Data de Criação: {row.data_criacao}")
            print(f"Ativo: {'Sim' if row.ativo else 'Não'}")
            print("-" * 50)
            
    except Exception as e:
        print(f"\nErro ao listar meios de pagamento: {e}")
    finally:
        db.close()

def criar_meio_pagamento():
    """Cria um novo meio de pagamento."""
    print_header("CRIAR NOVO MEIO DE PAGAMENTO")
    
    nome = input("Nome: ")
    tipo = input("Tipo (Cartão de Crédito, Cartão de Débito, PIX, Dinheiro, etc.): ")
    descricao = input("Descrição (opcional): ")
    
    # Verificar se deseja associar a uma conta
    associar_conta = input("Associar a uma conta? (s/n): ").lower() == 's'
    conta_id = None
    
    # Criar uma única conexão com o banco de dados
    db = DatabaseConnection()
    try:
        cursor = db.get_cursor()
        
        if associar_conta:
            # Listar contas disponíveis diretamente do banco de dados
            cursor.execute("SELECT id, nome FROM financas_pessoais.conta_dimensao WHERE ativo = 1 ORDER BY nome")
            contas_rows = cursor.fetchall()
            
            if not contas_rows:
                print("Nenhuma conta encontrada.")
                return
            
            print("\nContas disponíveis:")
            for i, conta_row in enumerate(contas_rows, 1):
                print(f"{i}. {conta_row.nome}")
            
            try:
                conta_idx = int(input("\nEscolha uma conta (número): ")) - 1
                if conta_idx < 0 or conta_idx >= len(contas_rows):
                    print("Opção inválida.")
                    return
                conta_id = contas_rows[conta_idx].id
            except ValueError:
                print("Opção inválida.")
                return
        
        # Inserir diretamente no banco de dados
        cursor.execute("""
            INSERT INTO financas_pessoais.meios_pagamento 
            (nome, descricao, conta_id, tipo, ativo)
            VALUES (?, ?, ?, ?, ?)
        """, (nome, descricao if descricao else None, conta_id, tipo, 1))
        
        # Obter o ID gerado
        cursor.execute("SELECT @@IDENTITY")
        meio_pagamento_id = cursor.fetchone()[0]
        
        # Confirmar a transação
        db.commit()
        
        print("\nMeio de pagamento criado com sucesso!")
        
        # Buscar o meio de pagamento recém-criado para exibir
        cursor.execute("SELECT * FROM financas_pessoais.meios_pagamento WHERE id = ?", (meio_pagamento_id,))
        row = cursor.fetchone()
        
        print(f"ID: {row.id}")
        print(f"Nome: {row.nome}")
        print(f"Tipo: {row.tipo}")
        print(f"Descrição: {row.descricao or 'N/A'}")
        
        # Mostrar conta associada, se houver
        if row.conta_id:
            cursor.execute("SELECT nome FROM financas_pessoais.conta_dimensao WHERE id = ?", (row.conta_id,))
            conta_row = cursor.fetchone()
            if conta_row:
                print(f"Conta: {conta_row.nome}")
            else:
                print("Conta: N/A")
        else:
            print("Conta: N/A")
        
        print(f"Data de Criação: {row.data_criacao}")
        print(f"Ativo: {'Sim' if row.ativo else 'Não'}")
        print("-" * 50)
        
    except Exception as e:
        db.rollback()
        print(f"\nErro ao criar meio de pagamento: {e}")
    finally:
        db.close()

def buscar_meio_pagamento():
    """Busca um meio de pagamento pelo ID."""
    print_header("BUSCAR MEIO DE PAGAMENTO")
    
    try:
        meio_pagamento_id = int(input("ID do meio de pagamento: "))
    except ValueError:
        print("ID inválido.")
        return
    
    # Criar uma única conexão com o banco de dados
    db = DatabaseConnection()
    try:
        cursor = db.get_cursor()
        
        # Buscar o meio de pagamento
        cursor.execute("SELECT * FROM financas_pessoais.meios_pagamento WHERE id = ?", (meio_pagamento_id,))
        row = cursor.fetchone()
        
        if row:
            print("\nMeio de pagamento encontrado:")
            print(f"ID: {row.id}")
            print(f"Nome: {row.nome}")
            print(f"Tipo: {row.tipo}")
            print(f"Descrição: {row.descricao or 'N/A'}")
            
            # Mostrar conta associada, se houver
            if row.conta_id:
                cursor.execute("SELECT nome FROM financas_pessoais.conta_dimensao WHERE id = ?", (row.conta_id,))
                conta_row = cursor.fetchone()
                if conta_row:
                    print(f"Conta: {conta_row.nome}")
                else:
                    print("Conta: N/A")
            else:
                print("Conta: N/A")
            
            print(f"Data de Criação: {row.data_criacao}")
            print(f"Ativo: {'Sim' if row.ativo else 'Não'}")
            print("-" * 50)
        else:
            print("\nMeio de pagamento não encontrado.")
            
    except Exception as e:
        print(f"\nErro ao buscar meio de pagamento: {e}")
    finally:
        db.close()

def atualizar_meio_pagamento():
    """Atualiza um meio de pagamento existente."""
    print_header("ATUALIZAR MEIO DE PAGAMENTO")
    
    try:
        meio_pagamento_id = int(input("ID do meio de pagamento a ser atualizado: "))
    except ValueError:
        print("ID inválido.")
        return
    
    # Obter os dados do meio de pagamento diretamente do banco de dados
    db = DatabaseConnection()
    try:
        cursor = db.get_cursor()
        cursor.execute("SELECT * FROM financas_pessoais.meios_pagamento WHERE id = ?", (meio_pagamento_id,))
        row = cursor.fetchone()
        
        if not row:
            print("Meio de pagamento não encontrado.")
            return
        
        # Extrair os dados do resultado da consulta
        id_mp = row.id
        nome_mp = row.nome
        tipo_mp = row.tipo
        descricao_mp = row.descricao
        conta_id_mp = row.conta_id
        data_criacao_mp = row.data_criacao
        ativo_mp = row.ativo
        
    except Exception as e:
        print(f"Erro ao buscar meio de pagamento: {e}")
        return
    
    # Mostrar os dados atuais
    print("\nDados atuais do meio de pagamento:")
    print(f"ID: {id_mp}")
    print(f"Nome: {nome_mp}")
    print(f"Tipo: {tipo_mp}")
    print(f"Descrição: {descricao_mp or 'N/A'}")
    
    # Mostrar conta associada, se houver
    if conta_id_mp:
        try:
            cursor.execute("SELECT nome FROM financas_pessoais.conta_dimensao WHERE id = ?", (conta_id_mp,))
            conta_row = cursor.fetchone()
            if conta_row:
                print(f"Conta: {conta_row.nome}")
            else:
                print("Conta: N/A")
        except Exception:
            print("Conta: N/A")
    else:
        print("Conta: N/A")
    
    print(f"Data de Criação: {data_criacao_mp}")
    print(f"Ativo: {'Sim' if ativo_mp else 'Não'}")
    print("-" * 50)
    
    print("\nDigite os novos dados (deixe em branco para manter o valor atual):")
    
    nome = input(f"Nome [{nome_mp}]: ")
    tipo = input(f"Tipo [{tipo_mp}]: ")
    descricao = input(f"Descrição [{descricao_mp or 'N/A'}]: ")
    
    # Verificar se deseja alterar a conta associada
    alterar_conta = input("\nDeseja alterar a conta associada? (s/n): ").lower() == 's'
    conta_id = conta_id_mp
    
    if alterar_conta:
        # Verificar se deseja remover a associação
        remover_associacao = input("Remover associação com conta? (s/n): ").lower() == 's'
        
        if remover_associacao:
            conta_id = None
        else:
            # Listar contas disponíveis diretamente do banco de dados
            try:
                cursor.execute("SELECT id, nome FROM financas_pessoais.conta_dimensao WHERE ativo = 1 ORDER BY nome")
                contas_rows = cursor.fetchall()
                
                if not contas_rows:
                    print("Nenhuma conta encontrada.")
                    return
                
                print("\nContas disponíveis:")
                for i, conta_row in enumerate(contas_rows, 1):
                    print(f"{i}. {conta_row.nome}")
                
                try:
                    conta_idx = int(input("\nEscolha uma conta (número): ")) - 1
                    if conta_idx < 0 or conta_idx >= len(contas_rows):
                        print("Opção inválida. Mantendo a conta atual.")
                    else:
                        conta_id = contas_rows[conta_idx].id
                except ValueError:
                    print("Opção inválida. Mantendo a conta atual.")
            except Exception as e:
                print(f"Erro ao listar contas: {e}")
                return
    
    # Atualizar diretamente no banco de dados
    try:
        cursor.execute("""
            UPDATE financas_pessoais.meios_pagamento
            SET nome = ?, descricao = ?, conta_id = ?, tipo = ?
            WHERE id = ?
        """, (
            nome if nome else nome_mp,
            descricao if descricao else descricao_mp,
            conta_id,
            tipo if tipo else tipo_mp,
            id_mp
        ))
        
        db.commit()
        print("\nMeio de pagamento atualizado com sucesso!")
        
        # Mostrar os dados atualizados
        cursor.execute("SELECT * FROM financas_pessoais.meios_pagamento WHERE id = ?", (id_mp,))
        updated_row = cursor.fetchone()
        
        print(f"ID: {updated_row.id}")
        print(f"Nome: {updated_row.nome}")
        print(f"Tipo: {updated_row.tipo}")
        print(f"Descrição: {updated_row.descricao or 'N/A'}")
        
        # Mostrar conta associada, se houver
        if updated_row.conta_id:
            cursor.execute("SELECT nome FROM financas_pessoais.conta_dimensao WHERE id = ?", (updated_row.conta_id,))
            conta_row = cursor.fetchone()
            if conta_row:
                print(f"Conta: {conta_row.nome}")
            else:
                print("Conta: N/A")
        else:
            print("Conta: N/A")
        
        print(f"Data de Criação: {updated_row.data_criacao}")
        print(f"Ativo: {'Sim' if updated_row.ativo else 'Não'}")
        
    except Exception as e:
        db.rollback()
        print(f"\nErro ao atualizar meio de pagamento: {e}")
    finally:
        db.close()

def excluir_meio_pagamento():
    """Exclui (desativa) um meio de pagamento."""
    print_header("EXCLUIR MEIO DE PAGAMENTO")
    
    try:
        meio_pagamento_id = int(input("ID do meio de pagamento a ser excluído: "))
    except ValueError:
        print("ID inválido.")
        return
    
    # Criar uma única conexão com o banco de dados
    db = DatabaseConnection()
    try:
        cursor = db.get_cursor()
        
        # Buscar o meio de pagamento
        cursor.execute("SELECT * FROM financas_pessoais.meios_pagamento WHERE id = ?", (meio_pagamento_id,))
        row = cursor.fetchone()
        
        if not row:
            print("Meio de pagamento não encontrado.")
            return
        
        # Mostrar os dados do meio de pagamento
        print("\nDados do meio de pagamento a ser excluído:")
        print(f"ID: {row.id}")
        print(f"Nome: {row.nome}")
        print(f"Tipo: {row.tipo}")
        print(f"Descrição: {row.descricao or 'N/A'}")
        
        # Mostrar conta associada, se houver
        if row.conta_id:
            cursor.execute("SELECT nome FROM financas_pessoais.conta_dimensao WHERE id = ?", (row.conta_id,))
            conta_row = cursor.fetchone()
            if conta_row:
                print(f"Conta: {conta_row.nome}")
            else:
                print("Conta: N/A")
        else:
            print("Conta: N/A")
        
        print(f"Data de Criação: {row.data_criacao}")
        print(f"Ativo: {'Sim' if row.ativo else 'Não'}")
        print("-" * 50)
        
        confirmacao = input("\nTem certeza que deseja excluir este meio de pagamento? (s/n): ")
        
        if confirmacao.lower() == 's':
            # Excluir (desativar) o meio de pagamento
            cursor.execute("UPDATE financas_pessoais.meios_pagamento SET ativo = 0 WHERE id = ?", (meio_pagamento_id,))
            db.commit()
            print("\nMeio de pagamento excluído com sucesso!")
        else:
            print("\nOperação cancelada.")
            
    except Exception as e:
        db.rollback()
        print(f"\nErro ao excluir meio de pagamento: {e}")
    finally:
        db.close()

def testar_conexao():
    """Testa a conexão com o banco de dados."""
    print_header("TESTAR CONEXÃO COM O BANCO DE DADOS")
    
    try:
        db = DatabaseConnection()
        cursor = db.get_cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        
        print("Conexão estabelecida com sucesso!")
        print(f"Versão do SQL Server: {version}")
        
        # Verificar se a tabela meios_pagamento existe
        try:
            cursor.execute("SELECT COUNT(*) FROM financas_pessoais.meios_pagamento")
            count = cursor.fetchone()[0]
            print(f"Tabela 'financas_pessoais.meios_pagamento' encontrada. Total de registros: {count}")
        except Exception as e:
            print(f"Erro ao acessar tabela 'financas_pessoais.meios_pagamento': {e}")
            print("A tabela pode não existir ou você não tem permissão para acessá-la.")
        
        db.close()
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")

def menu_principal():
    """Exibe o menu principal e processa a escolha do usuário."""
    while True:
        clear_screen()
        print_header("SISTEMA DE GERENCIAMENTO DE MEIOS DE PAGAMENTO")
        
        print("1. Listar meios de pagamento")
        print("2. Criar novo meio de pagamento")
        print("3. Buscar meio de pagamento por ID")
        print("4. Atualizar meio de pagamento")
        print("5. Excluir meio de pagamento")
        print("6. Testar conexão com o banco de dados")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == '1':
            listar_meios_pagamento()
        elif opcao == '2':
            criar_meio_pagamento()
        elif opcao == '3':
            buscar_meio_pagamento()
        elif opcao == '4':
            atualizar_meio_pagamento()
        elif opcao == '5':
            excluir_meio_pagamento()
        elif opcao == '6':
            testar_conexao()
        elif opcao == '0':
            print("\nSaindo do sistema...")
            break
        else:
            print("\nOpção inválida!")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    # Carregar variáveis de ambiente
    load_dotenv(override=True)
    
    # Carregar diretamente do arquivo para garantir
    env_values = dotenv_values(".env")
    
    # Verificar se as variáveis necessárias estão definidas
    required_vars = ['DB_SERVER', 'DB_DATABASE', 'DB_USERNAME', 'DB_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var) and var not in env_values:
            missing_vars.append(var)
    
    if missing_vars:
        print("ERRO: As seguintes variáveis de ambiente estão faltando:")
        for var in missing_vars:
            print(f"- {var}")
        print("Por favor, configure o arquivo .env com as credenciais do banco de dados.")
        sys.exit(1)
    
    # Iniciar o menu principal
    menu_principal()