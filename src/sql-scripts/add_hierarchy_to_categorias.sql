-- Script para adicionar suporte a hierarquia na tabela categorias
-- Executar no banco de dados Azure SQL

-- Adicionar campo categoria_pai_id
ALTER TABLE financas_pessoais.categorias
ADD categoria_pai_id INT NULL;

-- Adicionar campo nivel
ALTER TABLE financas_pessoais.categorias
ADD nivel INT NOT NULL DEFAULT 1;

-- Adicionar chave estrangeira para auto-referência
ALTER TABLE financas_pessoais.categorias
ADD CONSTRAINT FK_Categoria_CategoriaPai
FOREIGN KEY (categoria_pai_id) REFERENCES financas_pessoais.categorias(id);

-- Verificar se os campos foram adicionados corretamente
SELECT 
    COLUMN_NAME, 
    DATA_TYPE, 
    IS_NULLABLE
FROM 
    INFORMATION_SCHEMA.COLUMNS
WHERE 
    TABLE_SCHEMA = 'financas_pessoais' 
    AND TABLE_NAME = 'categorias'
ORDER BY 
    ORDINAL_POSITION;

-- Verificar se a chave estrangeira foi adicionada corretamente
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
    OBJECT_NAME(fk.parent_object_id) = 'categorias'
    AND OBJECT_SCHEMA_NAME(fk.parent_object_id) = 'financas_pessoais';
