# Documentação das Classes Principais do Sistema de Finanças Pessoais

## 1. Módulo de Contas

### Modelo: `Conta`
- **Arquivo**: `src/models/conta.py`
- **Descrição**: Classe fachada que integra dimensão e saldo da conta bancária.
- **Atributos principais**:
  - `id`: Identificador único da conta
  - `nome`: Nome da conta
  - `tipo`: Tipo da conta (Corrente, Poupança, Investimento, etc.)
  - `banco`: Nome da instituição bancária
  - `saldo_inicial`: Saldo inicial da conta
  - `saldo_atual`: Saldo atual da conta
  - `dimensao`: Objeto ContaDimensao associado
  - `saldo`: Objeto ContaSaldo associado

### Modelo: `ContaDimensao`
- **Arquivo**: `src/models/conta_dimensao.py`
- **Descrição**: Armazena os dados descritivos da conta.
- **Atributos principais**:
  - `id`: Identificador único
  - `nome`, `tipo`, `instituicao`, `agencia`, `conta_contabil`
  - `numero_banco`, `titular`, `nome_gerente`, `contato_gerente`
  - `data_criacao`, `ativo`

### Modelo: `ContaSaldo`
- **Arquivo**: `src/models/conta_saldo.py`
- **Descrição**: Gerencia o saldo da conta.
- **Atributos principais**:
  - `id`: Identificador único
  - `conta_dimensao_id`: ID da dimensão associada
  - `saldo_inicial`: Saldo inicial da conta
  - `saldo_atual`: Saldo atual da conta

### Interface: `AccountsView`
- **Arquivo**: `src/views/accounts_view.py`
- **Descrição**: Interface gráfica para gerenciar contas.
- **Funcionalidades**:
  - Listar todas as contas ativas
  - Criar nova conta
  - Editar conta existente
  - Excluir conta (marcando como inativa)
  - Visualizar saldo total

## 2. Módulo de Categorias

### Modelo: `Categoria`
- **Arquivo**: `src/models/categoria.py`
- **Descrição**: Representa categorias de receitas e despesas com suporte a hierarquia.
- **Atributos principais**:
  - `id`: Identificador único
  - `nome`: Nome da categoria
  - `tipo`: Tipo da categoria ('R' para Receita, 'D' para Despesa)
  - `descricao`: Descrição opcional
  - `categoria_pai_id`: ID da categoria pai (para subcategorias)
  - `nivel`: Nível na hierarquia (1 para categorias principais)
  - `data_criacao`, `ativo`
- **Métodos importantes**:
  - `obter_subcategorias()`: Retorna subcategorias de uma categoria
  - `obter_categorias_principais()`: Retorna categorias de nível superior
  - `obter_caminho_hierarquico()`: Retorna o caminho completo da categoria

### Interface: `CategoriesView`
- **Arquivo**: `src/views/categories_view.py`
- **Descrição**: Interface gráfica para gerenciar categorias.
- **Funcionalidades**:
  - Visualizar árvore hierárquica de categorias
  - Criar novas categorias e subcategorias
  - Editar categorias existentes
  - Excluir categorias (marcando como inativas)
  - Filtrar por tipo (Receita/Despesa)

## 3. Módulo de Meios de Pagamento

### Modelo: `MeioPagamento`
- **Arquivo**: `src/models/meio_pagamento.py`
- **Descrição**: Representa meios de pagamento como cartões, PIX, dinheiro, etc.
- **Atributos principais**:
  - `id`: Identificador único
  - `nome`: Nome do meio de pagamento
  - `tipo`: Tipo (Cartão de Crédito, Cartão de Débito, PIX, etc.)
  - `descricao`: Descrição opcional
  - `conta_id`: ID da conta associada (opcional)
  - `data_criacao`, `ativo`
- **Métodos importantes**:
  - `listar_todos()`: Lista todos os meios de pagamento
  - `listar_por_tipo()`: Lista meios de pagamento por tipo

### Interface: `PaymentMethodsView`
- **Arquivo**: `src/views/payment_methods_view.py`
- **Descrição**: Interface gráfica para gerenciar meios de pagamento.
- **Funcionalidades**:
  - Listar todos os meios de pagamento ativos
  - Criar novo meio de pagamento
  - Editar meio de pagamento existente
  - Excluir meio de pagamento (marcando como inativo)
  - Associar meio de pagamento a uma conta bancária

## Conexão com Banco de Dados

### Classe: `DatabaseConnection`
- **Arquivo**: `src/database/connection.py`
- **Descrição**: Gerencia a conexão com o banco de dados SQL Server.
- **Padrão**: Singleton (garante uma única instância de conexão)
- **Métodos importantes**:
  - `connect()`: Estabelece conexão com o banco
  - `get_cursor()`: Retorna um cursor para executar consultas
  - `commit()`, `rollback()`: Gerencia transações
  - `close()`: Fecha a conexão

## Observações Importantes

1. **Tratamento de Conexões**:
   - Nas interfaces gráficas, as operações de banco de dados são realizadas diretamente com uma única conexão por operação
   - Isso evita o problema de "cursor's connection has been closed"

2. **Exclusão Lógica**:
   - Todas as classes implementam exclusão lógica (campo `ativo`)
   - Registros "excluídos" são apenas marcados como inativos (`ativo = 0`)

3. **Relacionamentos**:
   - Meios de Pagamento podem estar associados a Contas
   - Categorias podem ter subcategorias (estrutura hierárquica)

4. **Integração na Interface Principal**:
   - Todas as interfaces são integradas como abas na janela principal (`MainWindow`)
   - Arquivo: `src/views/main_window.py`