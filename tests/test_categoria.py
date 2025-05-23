"""
Script para testar as funcionalidades do modelo Categoria com hierarquia.
Este script permite testar as operações CRUD e hierarquia de categorias.
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
from src.models.categoria import Categoria
from src.database.connection import DatabaseConnection

def clear_screen():
    """Limpa a tela do console."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 50)
    print(f"{title.center(50)}")
    print("=" * 50)

def print_categoria(categoria, mostrar_caminho=False):
    """Imprime os detalhes de uma categoria."""
    if not categoria:
        print("Categoria não encontrada.")
        return
    
    print(f"ID: {categoria.id}")
    print(f"Nome: {categoria.nome}")
    print(f"Tipo: {'Receita' if categoria.tipo == 'R' else 'Despesa'}")
    print(f"Descrição: {categoria.descricao or 'N/A'}")
    print(f"Categoria Pai ID: {categoria.categoria_pai_id or 'N/A'}")
    print(f"Nível: {categoria.nivel}")
    print(f"Data de Criação: {categoria.data_criacao}")
    print(f"Ativo: {'Sim' if categoria.ativo else 'Não'}")
    
    if mostrar_caminho:
        caminho = Categoria.obter_caminho_hierarquico(categoria.id)
        print(f"Caminho: {' > '.join(caminho)}")
    
    print("-" * 50)

def listar_categorias():
    """Lista todas as categorias cadastradas."""
    print_header("LISTAR CATEGORIAS")
    
    tipo = input("Filtrar por tipo (R para Receita, D para Despesa, Enter para todos): ").upper()
    if tipo and tipo not in ['R', 'D']:
        print("Tipo inválido. Use R para Receita ou D para Despesa.")
        return
    
    apenas_ativas = input("Mostrar apenas categorias ativas? (s/n): ").lower() == 's'
    
    categorias = Categoria.listar_todas(apenas_ativas=apenas_ativas, tipo=tipo if tipo else None)
    
    if not categorias:
        print("Nenhuma categoria encontrada.")
        return
    
    print(f"Total de categorias: {len(categorias)}")
    print("-" * 50)
    
    for categoria in categorias:
        print_categoria(categoria)

def listar_categorias_principais():
    """Lista as categorias principais (sem categoria pai)."""
    print_header("LISTAR CATEGORIAS PRINCIPAIS")
    
    tipo = input("Filtrar por tipo (R para Receita, D para Despesa, Enter para todos): ").upper()
    if tipo and tipo not in ['R', 'D']:
        print("Tipo inválido. Use R para Receita ou D para Despesa.")
        return
    
    apenas_ativas = input("Mostrar apenas categorias ativas? (s/n): ").lower() == 's'
    
    categorias = Categoria.obter_categorias_principais(
        tipo=tipo if tipo else None, 
        apenas_ativas=apenas_ativas
    )
    
    if not categorias:
        print("Nenhuma categoria principal encontrada.")
        return
    
    print(f"Total de categorias principais: {len(categorias)}")
    print("-" * 50)
    
    for categoria in categorias:
        print_categoria(categoria)

def listar_subcategorias():
    """Lista as subcategorias de uma categoria específica."""
    print_header("LISTAR SUBCATEGORIAS")
    
    try:
        categoria_pai_id = int(input("ID da categoria pai: "))
    except ValueError:
        print("ID inválido.")
        return
    
    categoria_pai = Categoria.buscar_por_id(categoria_pai_id)
    if not categoria_pai:
        print("Categoria pai não encontrada.")
        return
    
    print("\nCategoria pai:")
    print_categoria(categoria_pai)
    
    apenas_ativas = input("Mostrar apenas subcategorias ativas? (s/n): ").lower() == 's'
    
    subcategorias = Categoria.obter_subcategorias(
        categoria_pai_id=categoria_pai_id,
        apenas_ativas=apenas_ativas
    )
    
    if not subcategorias:
        print("Nenhuma subcategoria encontrada.")
        return
    
    print(f"Total de subcategorias: {len(subcategorias)}")
    print("-" * 50)
    
    for subcategoria in subcategorias:
        print_categoria(subcategoria)

def criar_categoria():
    """Cria uma nova categoria."""
    print_header("CRIAR NOVA CATEGORIA")
    
    nome = input("Nome da categoria: ")
    
    tipo = input("Tipo (R para Receita, D para Despesa): ").upper()
    if tipo not in ['R', 'D']:
        print("Tipo inválido. Use R para Receita ou D para Despesa.")
        return
    
    descricao = input("Descrição (opcional): ")
    
    tem_pai = input("Esta é uma subcategoria? (s/n): ").lower() == 's'
    categoria_pai_id = None
    nivel = 1
    
    if tem_pai:
        try:
            categoria_pai_id = int(input("ID da categoria pai: "))
            categoria_pai = Categoria.buscar_por_id(categoria_pai_id)
            if not categoria_pai:
                print("Categoria pai não encontrada.")
                return
            nivel = categoria_pai.nivel + 1
        except ValueError:
            print("ID inválido.")
            return
    
    # Criar a categoria
    categoria = Categoria(
        nome=nome,
        tipo=tipo,
        descricao=descricao if descricao else None,
        categoria_pai_id=categoria_pai_id,
        nivel=nivel
    )
    
    # Salvar no banco de dados
    if categoria.salvar():
        print("\nCategoria criada com sucesso!")
        print_categoria(categoria, mostrar_caminho=True)
    else:
        print("\nErro ao criar categoria.")

def buscar_categoria():
    """Busca uma categoria pelo ID."""
    print_header("BUSCAR CATEGORIA")
    
    try:
        categoria_id = int(input("ID da categoria: "))
    except ValueError:
        print("ID inválido.")
        return
    
    categoria = Categoria.buscar_por_id(categoria_id)
    
    if categoria:
        print("\nCategoria encontrada:")
        print_categoria(categoria, mostrar_caminho=True)
    else:
        print("\nCategoria não encontrada.")

def atualizar_categoria():
    """Atualiza uma categoria existente."""
    print_header("ATUALIZAR CATEGORIA")
    
    try:
        categoria_id = int(input("ID da categoria a ser atualizada: "))
    except ValueError:
        print("ID inválido.")
        return
    
    categoria = Categoria.buscar_por_id(categoria_id)
    
    if not categoria:
        print("Categoria não encontrada.")
        return
    
    print("\nDados atuais da categoria:")
    print_categoria(categoria)
    
    print("\nDigite os novos dados (deixe em branco para manter o valor atual):")
    
    nome = input(f"Nome [{categoria.nome}]: ")
    
    tipo_atual = 'Receita' if categoria.tipo == 'R' else 'Despesa'
    tipo_input = input(f"Tipo [{tipo_atual}] (R para Receita, D para Despesa): ").upper()
    tipo = tipo_input if tipo_input in ['R', 'D'] else categoria.tipo
    
    descricao = input(f"Descrição [{categoria.descricao or 'N/A'}]: ")
    
    mudar_pai = input("Deseja alterar a categoria pai? (s/n): ").lower() == 's'
    categoria_pai_id = categoria.categoria_pai_id
    nivel = categoria.nivel
    
    if mudar_pai:
        tem_pai = input("Esta é uma subcategoria? (s/n): ").lower() == 's'
        
        if tem_pai:
            try:
                categoria_pai_id = int(input("ID da nova categoria pai: "))
                categoria_pai = Categoria.buscar_por_id(categoria_pai_id)
                if not categoria_pai:
                    print("Categoria pai não encontrada.")
                    return
                nivel = categoria_pai.nivel + 1
            except ValueError:
                print("ID inválido.")
                return
        else:
            categoria_pai_id = None
            nivel = 1
    
    # Atualizar os dados da categoria
    categoria.nome = nome if nome else categoria.nome
    categoria.tipo = tipo
    categoria.descricao = descricao if descricao else categoria.descricao
    categoria.categoria_pai_id = categoria_pai_id
    categoria.nivel = nivel
    
    # Salvar as alterações
    if categoria.salvar():
        print("\nCategoria atualizada com sucesso!")
        print_categoria(categoria, mostrar_caminho=True)
    else:
        print("\nErro ao atualizar categoria.")

def excluir_categoria():
    """Exclui (desativa) uma categoria."""
    print_header("EXCLUIR CATEGORIA")
    
    try:
        categoria_id = int(input("ID da categoria a ser excluída: "))
    except ValueError:
        print("ID inválido.")
        return
    
    categoria = Categoria.buscar_por_id(categoria_id)
    
    if not categoria:
        print("Categoria não encontrada.")
        return
    
    print("\nDados da categoria a ser excluída:")
    print_categoria(categoria)
    
    # Verificar se tem subcategorias
    subcategorias = Categoria.obter_subcategorias(categoria_id)
    if subcategorias:
        print(f"\nATENÇÃO: Esta categoria possui {len(subcategorias)} subcategoria(s).")
        print("Excluir esta categoria não excluirá suas subcategorias, mas elas ficarão órfãs.")
    
    confirmacao = input("\nTem certeza que deseja excluir esta categoria? (s/n): ")
    
    if confirmacao.lower() == 's':
        if categoria.excluir():
            print("\nCategoria excluída com sucesso!")
        else:
            print("\nErro ao excluir categoria.")
    else:
        print("\nOperação cancelada.")

def mostrar_arvore_categorias():
    """Mostra a árvore hierárquica de categorias."""
    print_header("ÁRVORE DE CATEGORIAS")
    
    tipo = input("Filtrar por tipo (R para Receita, D para Despesa, Enter para todos): ").upper()
    if tipo and tipo not in ['R', 'D']:
        print("Tipo inválido. Use R para Receita ou D para Despesa.")
        return
    
    apenas_ativas = input("Mostrar apenas categorias ativas? (s/n): ").lower() == 's'
    
    # Obter categorias principais
    categorias_principais = Categoria.obter_categorias_principais(
        tipo=tipo if tipo else None, 
        apenas_ativas=apenas_ativas
    )
    
    if not categorias_principais:
        print("Nenhuma categoria encontrada.")
        return
    
    # Função recursiva para mostrar a árvore
    def mostrar_subcategorias(categoria_pai_id, nivel=0):
        subcategorias = Categoria.obter_subcategorias(
            categoria_pai_id=categoria_pai_id,
            apenas_ativas=apenas_ativas
        )
        
        # Filtrar por tipo manualmente, já que o método não aceita esse parâmetro
        if tipo:
            subcategorias = [s for s in subcategorias if s.tipo == tipo]
        
        for subcategoria in subcategorias:
            print("  " * nivel + "└─ " + subcategoria.nome)
            mostrar_subcategorias(subcategoria.id, nivel + 1)
    
    # Mostrar a árvore
    for categoria in categorias_principais:
        print(categoria.nome)
        mostrar_subcategorias(categoria.id, 1)

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
        
        # Verificar se a tabela categorias existe
        try:
            cursor.execute("SELECT COUNT(*) FROM financas_pessoais.categorias")
            count = cursor.fetchone()[0]
            print(f"Tabela 'financas_pessoais.categorias' encontrada. Total de registros: {count}")
        except Exception as e:
            print(f"Erro ao acessar tabela 'financas_pessoais.categorias': {e}")
            print("A tabela pode não existir ou você não tem permissão para acessá-la.")
        
        db.close()
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")

def menu_principal():
    """Exibe o menu principal e processa a escolha do usuário."""
    while True:
        clear_screen()
        print_header("SISTEMA DE GERENCIAMENTO DE CATEGORIAS")
        
        print("1. Listar todas as categorias")
        print("2. Listar categorias principais")
        print("3. Listar subcategorias")
        print("4. Mostrar árvore de categorias")
        print("5. Criar nova categoria")
        print("6. Buscar categoria por ID")
        print("7. Atualizar categoria")
        print("8. Excluir categoria")
        print("9. Testar conexão com o banco de dados")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == '1':
            listar_categorias()
        elif opcao == '2':
            listar_categorias_principais()
        elif opcao == '3':
            listar_subcategorias()
        elif opcao == '4':
            mostrar_arvore_categorias()
        elif opcao == '5':
            criar_categoria()
        elif opcao == '6':
            buscar_categoria()
        elif opcao == '7':
            atualizar_categoria()
        elif opcao == '8':
            excluir_categoria()
        elif opcao == '9':
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