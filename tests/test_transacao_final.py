"""
Script para testar as funcionalidades do modelo Transacao.
"""

import os
import sys
import importlib.util

# Verificar se o script está sendo executado diretamente ou através do run_test.py
if __name__ == "__main__":
    # Adicionar o diretório raiz do projeto ao caminho de busca do Python
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, project_root)

from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv, dotenv_values
from src.models.transacao import Transacao
from src.models.conta import Conta
from src.models.categoria import Categoria
from src.models.meio_pagamento import MeioPagamento
from src.database.connection import DatabaseConnection

def clear_screen():
    """Limpa a tela do console."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 50)
    print(f"{title.center(50)}")
    print("=" * 50)

def print_transacao(transacao, detalhada=False):
    """Imprime os detalhes de uma transação."""
    if not transacao:
        print("Transação não encontrada.")
        return
    
    print(f"ID: {transacao.id}")
    print(f"Descrição: {transacao.descricao}")
    print(f"Valor: R$ {float(transacao.valor):.2f}")
    print(f"Data: {transacao.data_transacao.strftime('%d/%m/%Y')}")
    print(f"Tipo: {'Receita' if transacao.tipo == 'R' else 'Despesa'}")
    
    if detalhada:
        # Carregar objetos relacionados
        categoria = transacao.categoria
        conta = transacao.conta
        meio_pagamento = transacao.meio_pagamento
        
        print(f"Categoria: {categoria.nome if categoria else 'N/A'}")
        print(f"Conta: {conta.nome if conta else 'N/A'}")
        print(f"Meio de Pagamento: {meio_pagamento.nome if meio_pagamento else 'N/A'}")
        print(f"Descrição do Pagamento: {transacao.descricao_pagamento or 'N/A'}")
        print(f"Local da Transação: {transacao.local_transacao or 'N/A'}")
        print(f"Observação: {transacao.observacao or 'N/A'}")
        print(f"Data de Criação: {transacao.data_criacao}")
    else:
        print(f"Categoria ID: {transacao.categoria_id or 'N/A'}")
        print(f"Conta ID: {transacao.conta_id or 'N/A'}")
        print(f"Meio de Pagamento ID: {transacao.meio_pagamento_id or 'N/A'}")
    
    print("-" * 50)

def listar_transacoes():
    """Lista todas as transações com opções de filtro."""
    print_header("LISTAR TRANSAÇÕES")
    
    # Opções de filtro
    print("Opções de filtro (deixe em branco para não filtrar):")
    
    # Filtro por data
    data_inicio_str = input("Data inicial (DD/MM/AAAA): ")
    data_fim_str = input("Data final (DD/MM/AAAA): ")
    
    data_inicio = None
    data_fim = None
    
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y").date()
        except ValueError:
            print("Formato de data inválido. Use DD/MM/AAAA.")
            return
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y").date()
        except ValueError:
            print("Formato de data inválido. Use DD/MM/AAAA.")
            return
    
    # Filtro por tipo
    tipo = input("Tipo (R para Receita, D para Despesa, Enter para todos): ").upper()
    if tipo and tipo not in ['R', 'D']:
        print("Tipo inválido. Use R para Receita ou D para Despesa.")
        return
    
    # Filtro por categoria
    categoria_id = None
    categoria_id_str = input("ID da categoria (Enter para todas): ")
    if categoria_id_str:
        try:
            categoria_id = int(categoria_id_str)
            # Verificar se a categoria existe
            categoria = Categoria.buscar_por_id(categoria_id)
            if not categoria:
                print("Categoria não encontrada.")
                return
        except ValueError:
            print("ID inválido.")
            return
    
    # Filtro por conta
    conta_id = None
    conta_id_str = input("ID da conta (Enter para todas): ")
    if conta_id_str:
        try:
            conta_id = int(conta_id_str)
            # Verificar se a conta existe
            conta = Conta.buscar_por_id(conta_id)
            if not conta:
                print("Conta não encontrada.")
                return
        except ValueError:
            print("ID inválido.")
            return
    
    # Filtro por meio de pagamento
    meio_pagamento_id = None
    meio_pagamento_id_str = input("ID do meio de pagamento (Enter para todos): ")
    if meio_pagamento_id_str:
        try:
            meio_pagamento_id = int(meio_pagamento_id_str)
            # Verificar se o meio de pagamento existe
            meio_pagamento = MeioPagamento.buscar_por_id(meio_pagamento_id)
            if not meio_pagamento:
                print("Meio de pagamento não encontrado.")
                return
        except ValueError:
            print("ID inválido.")
            return
    
    # Limite de registros
    limite = None
    limite_str = input("Limite de registros (Enter para todos): ")
    if limite_str:
        try:
            limite = int(limite_str)
            if limite <= 0:
                print("O limite deve ser maior que zero.")
                return
        except ValueError:
            print("Limite inválido.")
            return
    
    # Ordenação
    print("\nOpções de ordenação:")
    print("1. Data (mais recente primeiro)")
    print("2. Data (mais antiga primeiro)")
    print("3. Valor (maior primeiro)")
    print("4. Valor (menor primeiro)")
    print("5. Descrição (A-Z)")
    
    ordenacao_opcao = input("Escolha uma opção (Enter para padrão): ")
    
    ordenacao = "data_transacao DESC"  # Padrão
    
    if ordenacao_opcao == '1':
        ordenacao = "data_transacao DESC"
    elif ordenacao_opcao == '2':
        ordenacao = "data_transacao ASC"
    elif ordenacao_opcao == '3':
        ordenacao = "valor DESC"
    elif ordenacao_opcao == '4':
        ordenacao = "valor ASC"
    elif ordenacao_opcao == '5':
        ordenacao = "descricao ASC"
    
    # Construir filtros
    filtros = {}
    
    if data_inicio:
        filtros['data_inicio'] = data_inicio
    
    if data_fim:
        filtros['data_fim'] = data_fim
    
    if tipo:
        filtros['tipo'] = tipo
    
    if categoria_id:
        filtros['categoria_id'] = categoria_id
    
    if conta_id:
        filtros['conta_id'] = conta_id
    
    if meio_pagamento_id:
        filtros['meio_pagamento_id'] = meio_pagamento_id
    
    if limite:
        filtros['limite'] = limite
    
    filtros['ordenacao'] = ordenacao
    
    # Buscar transações
    transacoes = Transacao.listar_todas(filtros)
    
    if not transacoes:
        print("Nenhuma transação encontrada com os filtros especificados.")
        return
    
    print(f"\nTotal de transações: {len(transacoes)}")
    print("-" * 50)
    
    # Calcular totais
    total_receitas = sum(t.valor for t in transacoes if t.tipo == 'R')
    total_despesas = sum(t.valor for t in transacoes if t.tipo == 'D')
    saldo = total_receitas - total_despesas
    
    # Mostrar transações
    for transacao in transacoes:
        print_transacao(transacao)
    
    print(f"Total de Receitas: R$ {float(total_receitas):.2f}")
    print(f"Total de Despesas: R$ {float(total_despesas):.2f}")
    print(f"Saldo: R$ {float(saldo):.2f}")

def criar_transacao():
    """Cria uma nova transação."""
    print_header("CRIAR NOVA TRANSAÇÃO")
    
    # Obter dados da transação
    descricao = input("Descrição: ")
    
    try:
        valor = Decimal(input("Valor (R$): "))
        if valor <= 0:
            print("O valor deve ser maior que zero.")
            return
    except (ValueError, InvalidOperation):
        print("Valor inválido.")
        return
    
    data_str = input("Data (DD/MM/AAAA) ou Enter para hoje: ")
    if data_str:
        try:
            data_transacao = datetime.strptime(data_str, "%d/%m/%Y").date()
        except ValueError:
            print("Formato de data inválido. Use DD/MM/AAAA.")
            return
    else:
        data_transacao = datetime.now().date()
    
    tipo = input("Tipo (R para Receita, D para Despesa): ").upper()
    if tipo not in ['R', 'D']:
        print("Tipo inválido. Use R para Receita ou D para Despesa.")
        return
    
    # Selecionar categoria
    print("\nSelecione uma categoria:")
    categorias = Categoria.listar_todas(apenas_ativas=True, tipo=tipo)
    
    if not categorias:
        print(f"Nenhuma categoria de {'Receita' if tipo == 'R' else 'Despesa'} encontrada.")
        return
    
    print("\nCategorias disponíveis:")
    for i, categoria in enumerate(categorias, 1):
        print(f"{i}. {categoria.nome}")
    
    try:
        categoria_idx = int(input("\nEscolha uma categoria (número): ")) - 1
        if categoria_idx < 0 or categoria_idx >= len(categorias):
            print("Opção inválida.")
            return
        categoria_id = categorias[categoria_idx].id
    except ValueError:
        print("Opção inválida.")
        return
    
    # Selecionar conta
    print("\nSelecione uma conta:")
    contas = Conta.listar_todas(apenas_ativas=True)
    
    if not contas:
        print("Nenhuma conta encontrada.")
        return
    
    print("\nContas disponíveis:")
    for i, conta in enumerate(contas, 1):
        print(f"{i}. {conta.nome} - Saldo: R$ {float(conta.saldo_atual):.2f}")
    
    try:
        conta_idx = int(input("\nEscolha uma conta (número): ")) - 1
        if conta_idx < 0 or conta_idx >= len(contas):
            print("Opção inválida.")
            return
        conta_id = contas[conta_idx].id
    except ValueError:
        print("Opção inválida.")
        return
    
    # Selecionar meio de pagamento
    print("\nSelecione um meio de pagamento:")
    meios_pagamento = MeioPagamento.listar_todos(apenas_ativos=True, conta_id=conta_id)
    
    if not meios_pagamento:
        print("Nenhum meio de pagamento encontrado.")
        return
    
    print("\nMeios de pagamento disponíveis:")
    for i, meio_pagamento in enumerate(meios_pagamento, 1):
        print(f"{i}. {meio_pagamento.nome} ({meio_pagamento.tipo})")
    
    try:
        meio_pagamento_idx = int(input("\nEscolha um meio de pagamento (número): ")) - 1
        if meio_pagamento_idx < 0 or meio_pagamento_idx >= len(meios_pagamento):
            print("Opção inválida.")
            return
        meio_pagamento_id = meios_pagamento[meio_pagamento_idx].id
    except ValueError:
        print("Opção inválida.")
        return
    
    descricao_pagamento = input("\nDescrição do pagamento (opcional): ")
    local_transacao = input("Local da transação (opcional): ")
    observacao = input("Observação (opcional): ")
    
    # Criar a transação
    transacao = Transacao(
        descricao=descricao,
        valor=valor,
        data_transacao=data_transacao,
        tipo=tipo,
        categoria_id=categoria_id,
        conta_id=conta_id,
        meio_pagamento_id=meio_pagamento_id,
        descricao_pagamento=descricao_pagamento if descricao_pagamento else None,
        local_transacao=local_transacao if local_transacao else None,
        observacao=observacao if observacao else None
    )
    
    # Salvar no banco de dados
    if transacao.salvar():
        print("\nTransação criada com sucesso!")
        print_transacao(transacao, detalhada=True)
        
        # Mostrar o novo saldo da conta
        conta = Conta.buscar_por_id(conta_id)
        if conta:
            print(f"Novo saldo da conta {conta.nome}: R$ {float(conta.saldo_atual):.2f}")
    else:
        print("\nErro ao criar transação.")

def buscar_transacao():
    """Busca uma transação pelo ID."""
    print_header("BUSCAR TRANSAÇÃO")
    
    try:
        transacao_id = int(input("ID da transação: "))
    except ValueError:
        print("ID inválido.")
        return
    
    transacao = Transacao.buscar_por_id(transacao_id)
    
    if transacao:
        print("\nTransação encontrada:")
        print_transacao(transacao, detalhada=True)
    else:
        print("\nTransação não encontrada.")

def atualizar_transacao():
    """Atualiza uma transação existente."""
    print_header("ATUALIZAR TRANSAÇÃO")
    
    try:
        transacao_id = int(input("ID da transação a ser atualizada: "))
    except ValueError:
        print("ID inválido.")
        return
    
    transacao = Transacao.buscar_por_id(transacao_id)
    
    if not transacao:
        print("Transação não encontrada.")
        return
    
    print("\nDados atuais da transação:")
    print_transacao(transacao, detalhada=True)
    
    print("\nDigite os novos dados (deixe em branco para manter o valor atual):")
    
    descricao = input(f"Descrição [{transacao.descricao}]: ")
    
    try:
        valor_str = input(f"Valor [R$ {float(transacao.valor):.2f}]: ")
        valor = Decimal(valor_str) if valor_str else transacao.valor
        if valor <= 0:
            print("O valor deve ser maior que zero.")
            return
    except (ValueError, InvalidOperation):
        print("Valor inválido. Mantendo o valor atual.")
        valor = transacao.valor
    
    data_str = input(f"Data [{transacao.data_transacao.strftime('%d/%m/%Y')}]: ")
    if data_str:
        try:
            data_transacao = datetime.strptime(data_str, "%d/%m/%Y").date()
        except ValueError:
            print("Formato de data inválido. Mantendo a data atual.")
            data_transacao = transacao.data_transacao
    else:
        data_transacao = transacao.data_transacao
    
    tipo_atual = 'Receita' if transacao.tipo == 'R' else 'Despesa'
    tipo_input = input(f"Tipo [{tipo_atual}] (R para Receita, D para Despesa): ").upper()
    tipo = tipo_input if tipo_input in ['R', 'D'] else transacao.tipo
    
    # Atualizar categoria se o tipo mudou ou o usuário quiser
    categoria_id = transacao.categoria_id
    if tipo != transacao.tipo or input("\nDeseja alterar a categoria? (s/n): ").lower() == 's':
        # Selecionar categoria
        print("\nSelecione uma categoria:")
        categorias = Categoria.listar_todas(apenas_ativas=True, tipo=tipo)
        
        if not categorias:
            print(f"Nenhuma categoria de {'Receita' if tipo == 'R' else 'Despesa'} encontrada.")
            return
        
        print("\nCategorias disponíveis:")
        for i, categoria in enumerate(categorias, 1):
            print(f"{i}. {categoria.nome}")
        
        try:
            categoria_idx = int(input("\nEscolha uma categoria (número): ")) - 1
            if categoria_idx < 0 or categoria_idx >= len(categorias):
                print("Opção inválida. Mantendo a categoria atual.")
            else:
                categoria_id = categorias[categoria_idx].id
        except ValueError:
            print("Opção inválida. Mantendo a categoria atual.")
    
    # Atualizar conta se o usuário quiser
    conta_id = transacao.conta_id
    if input("\nDeseja alterar a conta? (s/n): ").lower() == 's':
        # Selecionar conta
        print("\nSelecione uma conta:")
        contas = Conta.listar_todas(apenas_ativas=True)
        
        if not contas:
            print("Nenhuma conta encontrada.")
            return
        
        print("\nContas disponíveis:")
        for i, conta in enumerate(contas, 1):
            print(f"{i}. {conta.nome} - Saldo: R$ {float(conta.saldo_atual):.2f}")
        
        try:
            conta_idx = int(input("\nEscolha uma conta (número): ")) - 1
            if conta_idx < 0 or conta_idx >= len(contas):
                print("Opção inválida. Mantendo a conta atual.")
            else:
                conta_id = contas[conta_idx].id
        except ValueError:
            print("Opção inválida. Mantendo a conta atual.")
    
    # Atualizar meio de pagamento se o usuário quiser
    meio_pagamento_id = transacao.meio_pagamento_id
    if input("\nDeseja alterar o meio de pagamento? (s/n): ").lower() == 's':
        # Selecionar meio de pagamento
        print("\nSelecione um meio de pagamento:")
        meios_pagamento = MeioPagamento.listar_todos(apenas_ativos=True, conta_id=conta_id)
        
        if not meios_pagamento:
            print("Nenhum meio de pagamento encontrado.")
            return
        
        print("\nMeios de pagamento disponíveis:")
        for i, meio_pagamento in enumerate(meios_pagamento, 1):
            print(f"{i}. {meio_pagamento.nome} ({meio_pagamento.tipo})")
        
        try:
            meio_pagamento_idx = int(input("\nEscolha um meio de pagamento (número): ")) - 1
            if meio_pagamento_idx < 0 or meio_pagamento_idx >= len(meios_pagamento):
                print("Opção inválida. Mantendo o meio de pagamento atual.")
            else:
                meio_pagamento_id = meios_pagamento[meio_pagamento_idx].id
        except ValueError:
            print("Opção inválida. Mantendo o meio de pagamento atual.")
    
    descricao_pagamento = input(f"\nDescrição do pagamento [{transacao.descricao_pagamento or 'N/A'}]: ")
    local_transacao = input(f"Local da transação [{transacao.local_transacao or 'N/A'}]: ")
    observacao = input(f"Observação [{transacao.observacao or 'N/A'}]: ")
    
    # Atualizar a transação
    transacao.descricao = descricao if descricao else transacao.descricao
    transacao.valor = valor
    transacao.data_transacao = data_transacao
    transacao.tipo = tipo
    transacao.categoria_id = categoria_id
    transacao.conta_id = conta_id
    transacao.meio_pagamento_id = meio_pagamento_id
    transacao.descricao_pagamento = descricao_pagamento if descricao_pagamento else transacao.descricao_pagamento
    transacao.local_transacao = local_transacao if local_transacao else transacao.local_transacao
    transacao.observacao = observacao if observacao else transacao.observacao
    
    # Salvar as alterações
    if transacao.salvar():
        print("\nTransação atualizada com sucesso!")
        print_transacao(transacao, detalhada=True)
        
        # Mostrar o novo saldo da conta
        conta = Conta.buscar_por_id(conta_id)
        if conta:
            print(f"Novo saldo da conta {conta.nome}: R$ {float(conta.saldo_atual):.2f}")
    else:
        print("\nErro ao atualizar transação.")
        
def excluir_transacao():
    """Exclui uma transação."""
    print_header("EXCLUIR TRANSAÇÃO")
    
    try:
        transacao_id = int(input("ID da transação a ser excluída: "))
    except ValueError:
        print("ID inválido.")
        return
    
    transacao = Transacao.buscar_por_id(transacao_id)
    
    if not transacao:
        print("Transação não encontrada.")
        return
    
    print("\nDados da transação a ser excluída:")
    print_transacao(transacao, detalhada=True)
    
    confirmacao = input("\nTem certeza que deseja excluir esta transação? (s/n): ")
    
    if confirmacao.lower() == 's':
        # Guardar o ID da conta para mostrar o saldo atualizado depois
        conta_id = transacao.conta_id
        
        if transacao.excluir():
            print("\nTransação excluída com sucesso!")
            
            # Mostrar o novo saldo da conta
            if conta_id:
                conta = Conta.buscar_por_id(conta_id)
                if conta:
                    print(f"Novo saldo da conta {conta.nome}: R$ {float(conta.saldo_atual):.2f}")
        else:
            print("\nErro ao excluir transação.")
    else:
        print("\nOperação cancelada.")

def relatorio_por_periodo():
    """Gera um relatório de transações por período."""
    print_header("RELATÓRIO POR PERÍODO")
    
    # Definir período
    print("Selecione o período:")
    print("1. Mês atual")
    print("2. Mês anterior")
    print("3. Últimos 30 dias")
    print("4. Ano atual")
    print("5. Período personalizado")
    
    opcao = input("\nEscolha uma opção: ")
    
    hoje = datetime.now().date()
    data_inicio = None
    data_fim = None
    
    if opcao == '1':  # Mês atual
        data_inicio = hoje.replace(day=1)
        if hoje.month == 12:
            data_fim = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            data_fim = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
        periodo = f"Mês atual ({data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})"
    
    elif opcao == '2':  # Mês anterior
        if hoje.month == 1:
            data_inicio = hoje.replace(year=hoje.year - 1, month=12, day=1)
            data_fim = hoje.replace(day=1) - timedelta(days=1)
        else:
            data_inicio = hoje.replace(month=hoje.month - 1, day=1)
            data_fim = hoje.replace(day=1) - timedelta(days=1)
        periodo = f"Mês anterior ({data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})"
    
    elif opcao == '3':  # Últimos 30 dias
        data_inicio = hoje - timedelta(days=30)
        data_fim = hoje
        periodo = f"Últimos 30 dias ({data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})"
    
    elif opcao == '4':  # Ano atual
        data_inicio = hoje.replace(month=1, day=1)
        data_fim = hoje.replace(month=12, day=31)
        periodo = f"Ano atual ({data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})"
    
    elif opcao == '5':  # Período personalizado
        data_inicio_str = input("Data inicial (DD/MM/AAAA): ")
        data_fim_str = input("Data final (DD/MM/AAAA): ")
        
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y").date()
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y").date()
            
            if data_fim < data_inicio:
                print("A data final deve ser maior ou igual à data inicial.")
                return
            
            periodo = f"Período personalizado ({data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})"
        except ValueError:
            print("Formato de data inválido. Use DD/MM/AAAA.")
            return
    else:
        print("Opção inválida.")
        return
    
    # Construir filtros
    filtros = {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'ordenacao': 'data_transacao ASC'
    }
    
    # Buscar transações
    transacoes = Transacao.listar_todas(filtros)
    
    if not transacoes:
        print(f"Nenhuma transação encontrada no período: {periodo}")
        return
    
    print(f"\nRelatório de Transações - {periodo}")
    print(f"Total de transações: {len(transacoes)}")
    print("-" * 50)
    
    # Calcular totais
    total_receitas = sum(t.valor for t in transacoes if t.tipo == 'R')
    total_despesas = sum(t.valor for t in transacoes if t.tipo == 'D')
    saldo = total_receitas - total_despesas
    
    # Agrupar por categoria
    categorias = {}
    for t in transacoes:
        if t.categoria_id not in categorias:
            categoria = Categoria.buscar_por_id(t.categoria_id)
            if categoria:
                categorias[t.categoria_id] = {
                    'nome': categoria.nome,
                    'tipo': categoria.tipo,
                    'total': 0,
                    'transacoes': []
                }
            else:
                categorias[t.categoria_id] = {
                    'nome': 'Sem categoria',
                    'tipo': t.tipo,
                    'total': 0,
                    'transacoes': []
                }
        
        categorias[t.categoria_id]['total'] += t.valor
        categorias[t.categoria_id]['transacoes'].append(t)
    
    # Mostrar resumo por categoria
    print("\nResumo por Categoria:")
    print("-" * 50)
    
    # Receitas
    print("\nRECEITAS:")
    receitas_por_categoria = {k: v for k, v in categorias.items() if v['tipo'] == 'R'}
    if receitas_por_categoria:
        for cat_id, cat_info in sorted(receitas_por_categoria.items(), key=lambda x: x[1]['total'], reverse=True):
            print(f"{cat_info['nome']}: R$ {float(cat_info['total']):.2f} ({len(cat_info['transacoes'])} transações)")
    else:
        print("Nenhuma receita no período.")
    
    # Despesas
    print("\nDESPESAS:")
    despesas_por_categoria = {k: v for k, v in categorias.items() if v['tipo'] == 'D'}
    if despesas_por_categoria:
        for cat_id, cat_info in sorted(despesas_por_categoria.items(), key=lambda x: x[1]['total'], reverse=True):
            print(f"{cat_info['nome']}: R$ {float(cat_info['total']):.2f} ({len(cat_info['transacoes'])} transações)")
    else:
        print("Nenhuma despesa no período.")
    
    # Mostrar totais
    print("\nTOTAIS:")
    print(f"Total de Receitas: R$ {float(total_receitas):.2f}")
    print(f"Total de Despesas: R$ {float(total_despesas):.2f}")
    print(f"Saldo: R$ {float(saldo):.2f}")
    
    # Perguntar se deseja ver detalhes
    if input("\nDeseja ver detalhes das transações? (s/n): ").lower() == 's':
        print("\nDetalhes das Transações:")
        print("-" * 50)
        
        for transacao in transacoes:
            print_transacao(transacao)
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
        
        # Verificar se a tabela transacoes existe
        try:
            cursor.execute("SELECT COUNT(*) FROM financas_pessoais.transacoes")
            count = cursor.fetchone()[0]
            print(f"Tabela 'financas_pessoais.transacoes' encontrada. Total de registros: {count}")
            
            # Verificar estrutura da tabela
            cursor.execute("""
                SELECT 
                    COLUMN_NAME, 
                    DATA_TYPE, 
                    IS_NULLABLE
                FROM 
                    INFORMATION_SCHEMA.COLUMNS
                WHERE 
                    TABLE_SCHEMA = 'financas_pessoais' 
                    AND TABLE_NAME = 'transacoes'
                ORDER BY 
                    ORDINAL_POSITION
            """)
            
            print("\nEstrutura da tabela 'financas_pessoais.transacoes':")
            print("-" * 50)
            print("Coluna".ljust(25) + "Tipo".ljust(15) + "Nulo?")
            print("-" * 50)
            
            for row in cursor.fetchall():
                print(f"{row.COLUMN_NAME.ljust(25)}{row.DATA_TYPE.ljust(15)}{row.IS_NULLABLE}")
            
        except Exception as e:
            print(f"Erro ao acessar tabela 'financas_pessoais.transacoes': {e}")
            print("A tabela pode não existir ou você não tem permissão para acessá-la.")
        
        db.close()
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")

def menu_principal():
    """Exibe o menu principal e processa a escolha do usuário."""
    while True:
        clear_screen()
        print_header("SISTEMA DE GERENCIAMENTO DE TRANSAÇÕES")
        
        print("1. Listar transações")
        print("2. Criar nova transação")
        print("3. Buscar transação por ID")
        print("4. Atualizar transação")
        print("5. Excluir transação")
        print("6. Relatório por período")
        print("7. Testar conexão com o banco de dados")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == '1':
            listar_transacoes()
        elif opcao == '2':
            criar_transacao()
        elif opcao == '3':
            buscar_transacao()
        elif opcao == '4':
            atualizar_transacao()
        elif opcao == '5':
            excluir_transacao()
        elif opcao == '6':
            relatorio_por_periodo()
        elif opcao == '7':
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