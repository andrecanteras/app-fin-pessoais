# Documentação do Banco de Dados - Sistema de Finanças Pessoais

## Visão Geral

Este documento descreve a estrutura do banco de dados utilizado pelo sistema de Finanças Pessoais. O banco de dados está organizado no schema `financas_pessoais` e contém tabelas para gerenciar categorias, contas, transações financeiras, meios de pagamento e metas financeiras.

## Informações de Conexão

- **Servidor:** boizito.database.windows.net
- **Porta:** 1433
- **Driver:** ODBC Driver 17 for SQL Server
- **Schema:** financas_pessoais

## Estrutura do Schema

O banco de dados utiliza um schema dedicado chamado `financas_pessoais` para organizar todas as tabelas relacionadas ao sistema.

## Tabelas

### 1. categorias

Armazena as categorias de receitas e despesas.

| Coluna | Tipo | Nulo | Padrão | Descrição |
|--------|------|------|--------|-----------|
| id | int | Não | IDENTITY | Chave primária |
| nome | nvarchar(100) | Não | | Nome da categoria |
| tipo | char(1) | Não | | Tipo: 'R' (Receita) ou 'D' (Despesa) |
| descricao | nvarchar(255) | Sim | NULL | Descrição da categoria |
| data_criacao | datetime | Sim | GETDATE() | Data de criação do registro |
| ativo | bit | Sim | 1 | Status da categoria (1=ativo, 0=inativo) |
| categoria_pai_id | int | Sim | NULL | Referência à categoria pai (hierarquia) |
| nivel | int | Não | 1 | Nível na hierarquia de categorias |

**Chaves:**
- **PK:** id
- **FK:** categoria_pai_id referencia categorias(id)

### 2. conta_dimensao

Armazena informações detalhadas sobre as contas financeiras.

| Coluna | Tipo | Nulo | Padrão | Descrição |
|--------|------|------|--------|-----------|
| id | int | Não | IDENTITY | Chave primária |
| nome | nvarchar(100) | Não | | Nome da conta |
| tipo | nvarchar(50) | Não | | Tipo da conta (Corrente, Poupança, etc.) |
| instituicao | nvarchar(100) | Sim | NULL | Nome da instituição financeira |
| agencia | nvarchar(20) | Sim | NULL | Número da agência |
| conta_contabil | nvarchar(30) | Sim | NULL | Número da conta contábil |
| numero_banco | nvarchar(10) | Sim | NULL | Código do banco |
| titular | nvarchar(150) | Sim | NULL | Nome do titular da conta |
| nome_gerente | nvarchar(100) | Sim | NULL | Nome do gerente da conta |
| contato_gerente | nvarchar(100) | Sim | NULL | Contato do gerente |
| data_criacao | datetime | Sim | GETDATE() | Data de criação do registro |
| ativo | bit | Sim | 1 | Status da conta (1=ativo, 0=inativo) |

**Chaves:**
- **PK:** id

### 3. conta_saldos

Armazena os saldos das contas financeiras.

| Coluna | Tipo | Nulo | Padrão | Descrição |
|--------|------|------|--------|-----------|
| id | int | Não | IDENTITY | Chave primária |
| conta_dimensao_id | int | Não | | Referência à conta_dimensao |
| saldo_inicial | decimal(15,2) | Sim | 0.00 | Saldo inicial da conta |
| saldo_atual | decimal(15,2) | Sim | 0.00 | Saldo atual da conta |
| data_criacao | datetime | Sim | GETDATE() | Data de criação do registro |

**Chaves:**
- **PK:** id
- **FK:** conta_dimensao_id referencia conta_dimensao(id)

### 4. meios_pagamento

Armazena os meios de pagamento disponíveis.

| Coluna | Tipo | Nulo | Padrão | Descrição |
|--------|------|------|--------|-----------|
| id | int | Não | IDENTITY | Chave primária |
| nome | nvarchar(100) | Não | | Nome do meio de pagamento |
| descricao | nvarchar(255) | Sim | NULL | Descrição do meio de pagamento |
| conta_id | int | Sim | NULL | Referência à conta_dimensao |
| tipo | nvarchar(50) | Não | | Tipo (Cartão de Crédito, PIX, etc.) |
| data_criacao | datetime | Sim | GETDATE() | Data de criação do registro |
| ativo | bit | Sim | 1 | Status do meio de pagamento (1=ativo, 0=inativo) |

**Chaves:**
- **PK:** id
- **FK:** conta_id referencia conta_dimensao(id)

### 5. transacoes

Armazena as transações financeiras.

| Coluna | Tipo | Nulo | Padrão | Descrição |
|--------|------|------|--------|-----------|
| id | int | Não | IDENTITY | Chave primária |
| descricao | nvarchar(255) | Não | | Descrição da transação |
| valor | decimal(15,2) | Não | | Valor da transação |
| data_transacao | date | Não | | Data da transação |
| tipo | char(1) | Não | | Tipo: 'R' (Receita) ou 'D' (Despesa) |
| categoria_id | int | Sim | NULL | Referência à categoria |
| conta_id | int | Sim | NULL | Referência à conta_dimensao |
| observacao | nvarchar(MAX) | Sim | NULL | Observações adicionais |
| data_criacao | datetime | Sim | GETDATE() | Data de criação do registro |
| meio_pagamento_id | int | Sim | NULL | Referência ao meio de pagamento |
| descricao_pagamento | nvarchar(255) | Sim | NULL | Descrição do pagamento |
| local_transacao | nvarchar(255) | Sim | NULL | Local onde ocorreu a transação |

**Chaves:**
- **PK:** id
- **FK:** categoria_id referencia categorias(id)
- **FK:** conta_id referencia conta_dimensao(id)
- **FK:** meio_pagamento_id referencia meios_pagamento(id)

### 6. metas

Armazena as metas financeiras.

| Coluna | Tipo | Nulo | Padrão | Descrição |
|--------|------|------|--------|-----------|
| id | int | Não | IDENTITY | Chave primária |
| nome | nvarchar(100) | Não | | Nome da meta |
| valor_alvo | decimal(15,2) | Não | | Valor alvo da meta |
| valor_atual | decimal(15,2) | Sim | 0.00 | Valor atual acumulado |
| data_inicio | date | Não | | Data de início da meta |
| data_fim | date | Não | | Data de término da meta |
| categoria_id | int | Sim | NULL | Referência à categoria |
| observacao | nvarchar(MAX) | Sim | NULL | Observações adicionais |
| concluida | bit | Sim | 0 | Status de conclusão (1=concluída, 0=pendente) |
| data_criacao | datetime | Sim | GETDATE() | Data de criação do registro |

**Chaves:**
- **PK:** id
- **FK:** categoria_id referencia categorias(id)

## Relacionamentos

O diagrama abaixo representa os relacionamentos entre as tabelas:

```
categorias <---(auto-referência)--- categorias
    ^
    |
    |
    |
metas
    
conta_dimensao <--- conta_saldos
    ^
    |
    |
    |
meios_pagamento
    ^
    |
    |
    |
transacoes ----> categorias
    |
    |
    v
conta_dimensao
```

## Chaves Estrangeiras

| Nome | Tabela | Coluna | Referência |
|------|--------|--------|------------|
| FK_Categoria_CategoriaPai | categorias | categoria_pai_id | categorias(id) |
| FK_conta_saldos_conta_dimensao | conta_saldos | conta_dimensao_id | conta_dimensao(id) |
| FK_meios_pagamento_conta_dimensao | meios_pagamento | conta_id | conta_dimensao(id) |
| FK__metas__categoria__68336F3E | metas | categoria_id | categorias(id) |
| FK__transacoe__categ__618671AF | transacoes | categoria_id | categorias(id) |
| FK_Transacao_MeioPagamento | transacoes | meio_pagamento_id | meios_pagamento(id) |
| FK_transacoes_conta_dimensao | transacoes | conta_id | conta_dimensao(id) |

## Índices

Cada tabela possui um índice primário na coluna `id`. Não há índices adicionais definidos.

## Considerações para Alterações Futuras

### Adicionando Novas Tabelas

Para adicionar uma nova tabela ao schema:

```sql
CREATE TABLE financas_pessoais.nova_tabela (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nome NVARCHAR(100) NOT NULL,
    -- outras colunas
    data_criacao DATETIME DEFAULT GETDATE()
);
```

### Adicionando Novas Colunas

Para adicionar uma nova coluna a uma tabela existente:

```sql
ALTER TABLE financas_pessoais.nome_tabela
ADD nova_coluna TIPO_DADOS NULL;
```

### Adicionando Novas Chaves Estrangeiras

Para adicionar uma nova chave estrangeira:

```sql
ALTER TABLE financas_pessoais.tabela_origem
ADD CONSTRAINT FK_Nome_Constraint
FOREIGN KEY (coluna_origem) REFERENCES financas_pessoais.tabela_destino(coluna_destino);
```

### Modificando Colunas Existentes

Para modificar uma coluna existente:

```sql
ALTER TABLE financas_pessoais.nome_tabela
ALTER COLUMN nome_coluna NOVO_TIPO_DADOS;
```

### Boas Práticas

1. **Backup**: Sempre faça backup do banco de dados antes de realizar alterações estruturais.
2. **Ambiente de Teste**: Teste alterações em um ambiente de desenvolvimento antes de aplicá-las em produção.
3. **Documentação**: Mantenha esta documentação atualizada quando fizer alterações no banco de dados.
4. **Versionamento**: Considere usar scripts de migração versionados para controlar alterações no esquema.
5. **Transações**: Use transações para garantir a integridade dos dados durante alterações complexas.

## Scripts Úteis

### Verificar Estrutura das Tabelas

```sql
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM 
    INFORMATION_SCHEMA.COLUMNS
WHERE 
    TABLE_SCHEMA = 'financas_pessoais'
ORDER BY 
    TABLE_NAME, ORDINAL_POSITION;
```

### Verificar Chaves Estrangeiras

```sql
SELECT 
    fk.name AS FK_Name,
    OBJECT_NAME(fk.parent_object_id) AS TableName,
    COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS ColumnName,
    OBJECT_NAME(fk.referenced_object_id) AS ReferencedTableName,
    COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS ReferencedColumnName
FROM 
    sys.foreign_keys AS fk
INNER JOIN 
    sys.foreign_key_columns AS fkc ON fk.object_id = fkc.constraint_object_id
INNER JOIN
    sys.tables AS t ON fk.parent_object_id = t.object_id
INNER JOIN
    sys.schemas AS s ON t.schema_id = s.schema_id
WHERE 
    s.name = 'financas_pessoais'
ORDER BY
    TableName, FK_Name;
```

### Recalcular Saldos

```sql
-- Exemplo de script para recalcular saldos de contas
UPDATE cs
SET cs.saldo_atual = cs.saldo_inicial + ISNULL(
    (SELECT SUM(CASE WHEN t.tipo = 'R' THEN t.valor ELSE -t.valor END)
     FROM financas_pessoais.transacoes t
     WHERE t.conta_id = cd.id),
    0)
FROM financas_pessoais.conta_saldos cs
JOIN financas_pessoais.conta_dimensao cd ON cs.conta_dimensao_id = cd.id;
```