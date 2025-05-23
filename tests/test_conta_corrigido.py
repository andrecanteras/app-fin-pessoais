"""
Script para testar as funcionalidades do modelo Conta sem interface gráfica.
Este script permite testar as operações CRUD (Create, Read, Update, Delete) do modelo Conta.
"""

import os
import sys
import importlib.util

# Verificar se o script está sendo executado diretamente
if __name__ == "__main__":
    # Adicionar o diretório raiz do projeto ao caminho de busca do Python
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, project_root)

from dotenv import load_dotenv, dotenv_values
from src.models.conta import Conta
from src.database.connection import DatabaseConnection
from decimal import Decimal

def clear_screen():
    """Limpa a tela do console."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 50)
    print(f"{title.center(50)}")
    print("=" * 50)

def print_conta(conta):
    """Imprime os detalhes de uma conta."""
    if not conta:
        print("Conta não encontrada.")
        return
    
    print(f"ID: {conta.id}")
    print(f"Nome: {conta.nome}")
    print(f"Tipo: {conta.tipo}")
    print(f"Instituição: {conta.banco or 'N/A'}")
    print(f"Agência: {conta.agencia or 'N/A'}")
    print(f"Conta Contábil: {conta.conta_contabil or 'N/A'}")
    print(f"Número do Banco: {conta.numero_banco or 'N/A'}")
    print(f"Titular: {conta.titular or 'N/A'}")
    print(f"Nome do Gerente: {conta.nome_gerente or 'N/A'}")
    print(f"Contato do Gerente: {conta.contato_gerente or 'N/A'}")
    print(f"Saldo Inicial: R$ {float(conta.saldo_inicial):.2f}")
    print(f"Saldo Atual: R$ {float(conta.saldo_atual):.2f}")
    print(f"Data de Criação: {conta.data_criacao}")
    print(f"Ativo: {'Sim' if conta.ativo else 'Não'}")
    print("-" * 50)

def listar_contas():
    """Lista todas as contas cadastradas."""
    print_header("LISTAR CONTAS")
    
    contas = Conta.listar_todas(apenas_ativas=False)
    
    if not contas:
        print("Nenhuma conta cadastrada.")
        return
    
    print(f"Total de contas: {len(contas)}")
    print("-" * 50)
    
    for conta in contas:
        print_conta(conta)
    
    saldo_total = Conta.obter_saldo_total()
    print(f"Saldo total (contas ativas): R$ {float(saldo_total):.2f}")

def criar_conta():
    """Cria uma nova conta."""
    print_header("CRIAR NOVA CONTA")
    
    nome = input("Nome da conta: ")
    tipo = input("Tipo (Corrente, Poupança, Investimento, etc.): ")
    
    try:
        saldo_inicial = Decimal(input("Saldo inicial (R$): "))
    except (ValueError, Decimal.InvalidOperation):
        print("Valor inválido. Usando 0.00 como padrão.")
        saldo_inicial = Decimal('0.0')
    
    instituicao = input("Instituição financeira (opcional): ")
    agencia = input("Agência (opcional): ")
    conta_contabil = input("Conta Contábil (opcional): ")
    numero_banco = input("Número do Banco (opcional): ")
    titular = input("Titular (opcional): ")
    nome_gerente = input("Nome do Gerente (opcional): ")
    contato_gerente = input("Contato do Gerente (opcional): ")
    
    # Criar a conta
    conta = Conta(
        nome=nome,
        tipo=tipo,
        saldo_inicial=saldo_inicial,
        saldo_atual=saldo_inicial,
        banco=instituicao if instituicao else None,
        agencia=agencia if agencia else None,
        conta_contabil=conta_contabil if conta_contabil else None,
        numero_banco=numero_banco if numero_banco else None,
        titular=titular if titular else None,
        nome_gerente=nome_gerente if nome_gerente else None,
        contato_gerente=contato_gerente if contato_gerente else None
    )
    
    # Salvar no banco de dados
    if conta.salvar():
        print("\nConta criada com sucesso!")
        print_conta(conta)
    else:
        print("\nErro ao criar conta.")

def buscar_conta():
    """Busca uma conta pelo ID."""
    print_header("BUSCAR CONTA")
    
    try:
        conta_id = int(input("ID da conta: "))
    except ValueError:
        print("ID inválido.")
        return
    
    conta = Conta.buscar_por_id(conta_id)
    
    if conta:
        print("\nConta encontrada:")
        print_conta(conta)
    else:
        print("\nConta não encontrada.")

def atualizar_conta():
    """Atualiza uma conta existente."""
    print_header("ATUALIZAR CONTA")
    
    try:
        conta_id = int(input("ID da conta a ser atualizada: "))
    except ValueError:
        print("ID inválido.")
        return
    
    conta = Conta.buscar_por_id(conta_id)
    
    if not conta:
        print("Conta não encontrada.")
        return
    
    print("\nDados atuais da conta:")
    print_conta(conta)
    
    print("\nDigite os novos dados (deixe em branco para manter o valor atual):")
    
    nome = input(f"Nome [{conta.nome}]: ")
    tipo = input(f"Tipo [{conta.tipo}]: ")
    instituicao = input(f"Instituição [{conta.banco or 'N/A'}]: ")
    agencia = input(f"Agência [{conta.agencia or 'N/A'}]: ")
    conta_contabil = input(f"Conta Contábil [{conta.conta_contabil or 'N/A'}]: ")
    numero_banco = input(f"Número do Banco [{conta.numero_banco or 'N/A'}]: ")
    titular = input(f"Titular [{conta.titular or 'N/A'}]: ")
    nome_gerente = input(f"Nome do Gerente [{conta.nome_gerente or 'N/A'}]: ")
    contato_gerente = input(f"Contato do Gerente [{conta.contato_gerente or 'N/A'}]: ")
    
    try:
        saldo_inicial_str = input(f"Saldo inicial [R$ {float(conta.saldo_inicial):.2f}]: ")
        saldo_inicial = Decimal(saldo_inicial_str) if saldo_inicial_str else conta.saldo_inicial
    except (ValueError, Decimal.InvalidOperation):
        print("Valor inválido. Mantendo o valor atual.")
        saldo_inicial = conta.saldo_inicial
    
    # Atualizar os dados da conta
    conta.nome = nome if nome else conta.nome
    conta.tipo = tipo if tipo else conta.tipo
    conta.banco = instituicao if instituicao else conta.banco
    conta.agencia = agencia if agencia else conta.agencia
    conta.conta_contabil = conta_contabil if conta_contabil else conta.conta_contabil
    conta.numero_banco = numero_banco if numero_banco else conta.numero_banco
    conta.titular = titular if titular else conta.titular
    conta.nome_gerente = nome_gerente if nome_gerente else conta.nome_gerente
    conta.contato_gerente = contato_gerente if contato_gerente else conta.contato_gerente
    
    # Se o saldo inicial mudou, ajustar o saldo atual proporcionalmente
    if saldo_inicial != conta.saldo_inicial:
        diferenca = saldo_inicial - conta.saldo_inicial
        conta.saldo_atual += diferenca
        conta.saldo_inicial = saldo_inicial
    
    # Salvar as alterações
    if conta.salvar():
        print("\nConta atualizada com sucesso!")
        print_conta(conta)
    else:
        print("\nErro ao atualizar conta.")

def excluir_conta():
    """Exclui (desativa) uma conta."""
    print_header("EXCLUIR CONTA")
    
    try:
        conta_id = int(input("ID da conta a ser excluída: "))
    except ValueError:
        print("ID inválido.")
        return
    
    conta = Conta.buscar_por_id(conta_id)
    
    if not conta:
        print("Conta não encontrada.")
        return
    
    print("\nDados da conta a ser excluída:")
    print_conta(conta)
    
    confirmacao = input("\nTem certeza que deseja excluir esta conta? (s/n): ")
    
    if confirmacao.lower() == 's':
        if conta.excluir():
            print("\nConta excluída com sucesso!")
        else:
            print("\nErro ao excluir conta.")
    else:
        print("\nOperação cancelada.")

def simular_transacao():
    """Simula uma transação (receita ou despesa) em uma conta."""
    print_header("SIMULAR TRANSAÇÃO")
    
    try:
        conta_id = int(input("ID da conta: "))
    except ValueError:
        print("ID inválido.")
        return
    
    conta = Conta.buscar_por_id(conta_id)
    
    if not conta:
        print("Conta não encontrada.")
        return
    
    print("\nDados da conta:")
    print_conta(conta)
    
    tipo = input("\nTipo de transação (R para Receita, D para Despesa): ").upper()
    
    if tipo not in ['R', 'D']:
        print("Tipo inválido. Use R para Receita ou D para Despesa.")
        return
    
    try:
        valor = Decimal(input("Valor da transação (R$): "))
        if valor <= Decimal('0'):
            print("O valor deve ser maior que zero.")
            return
    except (ValueError, Decimal.InvalidOperation):
        print("Valor inválido.")
        return
    
    # Atualizar o saldo
    if conta.atualizar_saldo(valor, tipo):
        print("\nTransação realizada com sucesso!")
        print(f"Tipo: {'Receita' if tipo == 'R' else 'Despesa'}")
        print(f"Valor: R$ {float(valor):.2f}")
        print(f"Novo saldo: R$ {float(conta.saldo_atual):.2f}")
    else:
        print("\nErro ao realizar transação.")

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
        
        # Verificar se as tabelas existem
        try:
            cursor.execute("SELECT COUNT(*) FROM financas_pessoais.conta_dimensao")
            count_dimensao = cursor.fetchone()[0]
            print(f"Tabela 'financas_pessoais.conta_dimensao' encontrada. Total de registros: {count_dimensao}")
            
            cursor.execute("SELECT COUNT(*) FROM financas_pessoais.conta_saldos")
            count_saldos = cursor.fetchone()[0]
            print(f"Tabela 'financas_pessoais.conta_saldos' encontrada. Total de registros: {count_saldos}")
        except Exception as e:
            print(f"Erro ao acessar tabelas: {e}")
            print("As tabelas podem não existir ou você não tem permissão para acessá-las.")
        
        db.close()
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")

def executar_consulta_sql():
    """Executa uma consulta SQL diretamente no banco de dados."""
    print_header("EXECUTAR CONSULTA SQL")
    
    # Consulta SQL
    sql = input("Digite a consulta SQL (ou deixe em branco para usar a consulta padrão): ")
    if not sql:
        sql = """
        SELECT d.*, s.saldo_inicial, s.saldo_atual 
        FROM financas_pessoais.conta_dimensao d
        JOIN financas_pessoais.conta_saldos s ON d.id = s.conta_dimensao_id
        """
    
    db = DatabaseConnection()
    try:
        cursor = db.get_cursor()
        print(f"Executando consulta: {sql}")
        cursor.execute(sql)
        
        rows = cursor.fetchall()
        if not rows:
            print("Nenhum resultado encontrado.")
            return
        
        # Obter nomes das colunas
        columns = [column[0] for column in cursor.description]
        print("-" * 100)
        print(" | ".join(columns))
        print("-" * 100)
        
        # Imprimir resultados
        for row in rows:
            values = [str(value) for value in row]
            print(" | ".join(values))
        
        print("-" * 100)
        print(f"Total de registros: {len(rows)}")
        
    except Exception as e:
        print(f"Erro ao executar consulta: {e}")
    finally:
        db.close()

def menu_principal():
    """Exibe o menu principal e processa a escolha do usuário."""
    while True:
        clear_screen()
        print_header("SISTEMA DE GERENCIAMENTO DE CONTAS")
        
        print("1. Listar todas as contas")
        print("2. Criar nova conta")
        print("3. Buscar conta por ID")
        print("4. Atualizar conta")
        print("5. Excluir conta")
        print("6. Simular transação")
        print("7. Testar conexão com o banco de dados")
        print("8. Executar consulta SQL")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == '1':
            listar_contas()
        elif opcao == '2':
            criar_conta()
        elif opcao == '3':
            buscar_conta()
        elif opcao == '4':
            atualizar_conta()
        elif opcao == '5':
            excluir_conta()
        elif opcao == '6':
            simular_transacao()
        elif opcao == '7':
            testar_conexao()
        elif opcao == '8':
            executar_consulta_sql()
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