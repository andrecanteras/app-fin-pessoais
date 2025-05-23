# Instruções para Migração do Banco de Dados

Este documento contém instruções para migrar o schema `financas_pessoais` do banco de dados atual (`bdMaterialEscolar`) para um novo banco de dados.

## Arquivos de Migração

1. **migrate_schema.sql**: Script SQL para criar o schema e tabelas no novo banco de dados e migrar os dados.
2. **update_env.py**: Script Python para atualizar o arquivo `.env` com o novo nome do banco de dados.

## Passos para Migração

### 1. Criar o Novo Banco de Dados

Primeiro, crie o novo banco de dados no Azure SQL Server:

1. Acesse o [Portal do Azure](https://portal.azure.com)
2. Navegue até o seu servidor SQL (`boizito.database.windows.net`)
3. Clique em "Novo banco de dados"
4. Preencha as informações necessárias e crie o banco de dados

### 2. Executar o Script de Migração

1. Abra o arquivo `migrate_schema.sql` em um editor de texto
2. Substitua `[NOVO_BANCO]` pelo nome do novo banco de dados que você criou
3. Execute o script no SQL Server Management Studio (SSMS) ou Azure Data Studio

```sql
-- Exemplo de como executar o script
USE [seu_novo_banco_de_dados];
GO

-- Execute o conteúdo do arquivo migrate_schema.sql aqui
```

### 3. Atualizar o Arquivo .env

Execute o script Python para atualizar o arquivo `.env` com o novo nome do banco de dados:

```bash
python sql/update_env.py
```

Quando solicitado, digite o nome do novo banco de dados.

### 4. Verificar a Migração

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

### 5. Atualizar a Aplicação

Após a migração bem-sucedida, a aplicação deve estar configurada para usar o novo banco de dados. O script `update_env.py` já deve ter atualizado o arquivo `.env`, mas verifique se a aplicação está funcionando corretamente.

## Solução de Problemas

Se encontrar problemas durante a migração:

1. **Erro de conexão**: Verifique se as credenciais no arquivo `.env` estão corretas
2. **Erro de permissão**: Verifique se o usuário tem permissões suficientes no novo banco de dados
3. **Erro de chave estrangeira**: Pode ser necessário desativar temporariamente as restrições de chave estrangeira durante a migração

Para qualquer outro problema, verifique os logs de erro e consulte a documentação do SQL Server.

## Backup

Antes de iniciar a migração, é recomendável fazer um backup do banco de dados atual:

```sql
BACKUP DATABASE [bdMaterialEscolar] 
TO DISK = 'C:\Backup\bdMaterialEscolar.bak' 
WITH FORMAT, MEDIANAME = 'SQLServerBackups', NAME = 'Full Backup of bdMaterialEscolar';
```

## Rollback

Se for necessário reverter a migração, você pode simplesmente continuar usando o banco de dados original (`bdMaterialEscolar`) e restaurar o arquivo `.env` para apontar para ele.