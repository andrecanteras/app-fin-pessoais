-- Script para adicionar a tabela meios_pagamento ao schema financas_pessoais
-- Executar no banco de dados Azure SQL

-- Verificar se a tabela já existe
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'meios_pagamento' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    -- Criar a tabela meios_pagamento
    CREATE TABLE financas_pessoais.meios_pagamento (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(100) NOT NULL,
        descricao NVARCHAR(255),
        conta_id INT,
        tipo NVARCHAR(50) NOT NULL, -- Cartão de Crédito, Cartão de Débito, PIX, Dinheiro, Transferência, etc.
        data_criacao DATETIME DEFAULT GETDATE(),
        ativo BIT DEFAULT 1,
        FOREIGN KEY (conta_id) REFERENCES financas_pessoais.contas(id)
    );
    
    PRINT 'Tabela financas_pessoais.meios_pagamento criada com sucesso.';
    
    -- Inserir alguns meios de pagamento padrão
    INSERT INTO financas_pessoais.meios_pagamento (nome, descricao, tipo, ativo)
    VALUES 
        ('Dinheiro', 'Pagamento em espécie', 'Dinheiro', 1),
        ('PIX', 'Transferência via PIX', 'PIX', 1),
        ('Transferência Bancária', 'Transferência entre contas', 'Transferência', 1);
    
    PRINT 'Meios de pagamento padrão inseridos com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.meios_pagamento já existe.';
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
    AND TABLE_NAME = 'meios_pagamento'
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
    OBJECT_NAME(fk.parent_object_id) = 'meios_pagamento'
    AND OBJECT_SCHEMA_NAME(fk.parent_object_id) = 'financas_pessoais';