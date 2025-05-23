-- Script para adicionar a tabela transacoes ao schema financas_pessoais
-- Executar no banco de dados Azure SQL

-- Verificar se a tabela já existe
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'transacoes' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    -- Criar a tabela transacoes
    CREATE TABLE financas_pessoais.transacoes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        descricao NVARCHAR(255) NOT NULL,
        valor DECIMAL(15, 2) NOT NULL,
        data_transacao DATE NOT NULL,
        tipo CHAR(1) NOT NULL CHECK (tipo IN ('R', 'D')), -- R: Receita, D: Despesa
        categoria_id INT,
        conta_id INT,
        observacao NVARCHAR(MAX),
        data_criacao DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (categoria_id) REFERENCES financas_pessoais.categorias(id),
        FOREIGN KEY (conta_id) REFERENCES financas_pessoais.contas(id)
    );
    
    PRINT 'Tabela financas_pessoais.transacoes criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.transacoes já existe.';
END

-- Verificar se a tabela foi criada corretamente
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
    ORDINAL_POSITION;

-- Verificar as chaves estrangeiras
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
WHERE 
    OBJECT_NAME(fk.parent_object_id) = 'transacoes'
    AND OBJECT_SCHEMA_NAME(fk.parent_object_id) = 'financas_pessoais';