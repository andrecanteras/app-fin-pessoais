# Instruções para Migração do Banco de Dados

Este documento contém instruções para migrar o schema `financas_pessoais` do banco de dados atual (`bdMaterialEscolar`) para um novo banco de dados.

## Arquivos de Migração

1. **migrate_schema_parte1.sql**: Script para criar o schema e tabelas no novo banco de dados
2. **migrate_schema_parte2.sql**: Script para exportar dados do banco atual
3. **migrate_schema_parte3.sql**: Modelo de script para importar dados no novo banco
4. **update_env.py**: Script Python para atualizar o arquivo `.env` com o novo nome do banco de dados

## Passos para Migração

### 1. Criar o Novo Banco de Dados

Primeiro, crie o novo banco de dados no Azure SQL Server:

1. Acesse o [Portal do Azure](https://portal.azure.com)
2. Navegue até o seu servidor SQL (`boizito.database.windows.net`)
3. Clique em "Novo banco de dados"
4. Preencha as informações necessárias e crie o banco de dados

### 2. Criar a Estrutura no Novo Banco

1. Conecte-se ao novo banco de dados
2. Execute o script `migrate_schema_parte1.sql` para criar o schema e as tabelas

```sql
-- Exemplo de como executar o script
USE [seu_novo_banco_de_dados];
GO

-- Execute o conteúdo do arquivo migrate_schema_parte1.sql aqui
```

### 3. Exportar Dados do Banco Atual

1. Conecte-se ao banco de dados atual (`bdMaterialEscolar`)
2. Execute o script `migrate_schema_parte2.sql`
3. Salve os resultados de cada consulta (você pode exportar para CSV ou copiar para um editor de texto)

### 4. Importar Dados no Novo Banco

1. Abra o arquivo `migrate_schema_parte3.sql` em um editor de texto
2. Substitua os valores de exemplo pelos dados reais exportados do banco atual
3. Conecte-se ao novo banco de dados
4. Execute o script modificado para importar os dados

### 5. Atualizar o Arquivo .env

Execute o script Python para atualizar o arquivo `.env` com o novo nome do banco de dados:

```bash
python sql/update_env.py
```

Quando solicitado, digite o nome do novo banco de dados.

### 6. Verificar a Migração

Para verificar se a migração foi bem-sucedida:

1. Conecte-se ao novo banco de dados
2. Execute as seguintes consultas para verificar se os dados foram migrados corretamente:

```sql
-- Verificar tabelas criadas
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'financas_pessoais';

-- Verificar dados migrados (exemplo para categorias)
SELECT COUNT(*) FROM financas_pessoais.categorias;

-- Verificar dados migrados (exemplo para transacoes)
SELECT COUNT(*) FROM financas_pessoais.transacoes;
```

## Alternativa: Exportação/Importação via BCP ou SQL Server Import/Export Wizard

Se você tiver muitos dados ou preferir uma abordagem mais automatizada, considere usar:

1. **BCP (Bulk Copy Program)** para exportar e importar dados
2. **SQL Server Import/Export Wizard** através do SQL Server Management Studio

### Usando o SQL Server Import/Export Wizard:

1. No SQL Server Management Studio, clique com o botão direito no banco de dados de origem
2. Selecione "Tasks" > "Export Data"
3. Siga o assistente para exportar os dados para o novo banco de dados

## Solução de Problemas

Se encontrar problemas durante a migração:

1. **Erro de identidade**: Verifique se IDENTITY_INSERT está ativado ao inserir dados com IDs específicos
2. **Erro de chave estrangeira**: Verifique a ordem de inserção dos dados (tabelas pai antes das tabelas filhas)
3. **Erro de permissão**: Verifique se o usuário tem permissões suficientes no novo banco de dados

## Backup

Antes de iniciar a migração, é recomendável fazer um backup do banco de dados atual:

```sql
BACKUP DATABASE [bdMaterialEscolar] 
TO DISK = 'C:\Backup\bdMaterialEscolar.bak' 
WITH FORMAT, MEDIANAME = 'SQLServerBackups', NAME = 'Full Backup of bdMaterialEscolar';
```