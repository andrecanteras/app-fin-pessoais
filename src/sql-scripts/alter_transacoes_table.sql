-- Script para adicionar novos campos à tabela transacoes
-- Executar no banco de dados Azure SQL

-- Verificar se a tabela transacoes existe
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'transacoes' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    -- Verificar se o campo meio_pagamento_id já existe
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE name = 'meio_pagamento_id' AND object_id = OBJECT_ID('financas_pessoais.transacoes'))
    BEGIN
        -- Adicionar campo meio_pagamento_id
        ALTER TABLE financas_pessoais.transacoes
        ADD meio_pagamento_id INT NULL;
        
        -- Adicionar chave estrangeira para meio_pagamento_id
        ALTER TABLE financas_pessoais.transacoes
        ADD CONSTRAINT FK_Transacao_MeioPagamento
        FOREIGN KEY (meio_pagamento_id) REFERENCES financas_pessoais.meios_pagamento(id);
        
        PRINT 'Campo meio_pagamento_id adicionado à tabela transacoes.';
    END
    ELSE
    BEGIN
        PRINT 'Campo meio_pagamento_id já existe na tabela transacoes.';
    END
    
    -- Verificar se o campo descricao_pagamento já existe
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE name = 'descricao_pagamento' AND object_id = OBJECT_ID('financas_pessoais.transacoes'))
    BEGIN
        -- Adicionar campo descricao_pagamento
        ALTER TABLE financas_pessoais.transacoes
        ADD descricao_pagamento NVARCHAR(255) NULL;
        
        PRINT 'Campo descricao_pagamento adicionado à tabela transacoes.';
    END
    ELSE
    BEGIN
        PRINT 'Campo descricao_pagamento já existe na tabela transacoes.';
    END
    
    -- Verificar se o campo local_transacao já existe
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE name = 'local_transacao' AND object_id = OBJECT_ID('financas_pessoais.transacoes'))
    BEGIN
        -- Adicionar campo local_transacao
        ALTER TABLE financas_pessoais.transacoes
        ADD local_transacao NVARCHAR(255) NULL;
        
        PRINT 'Campo local_transacao adicionado à tabela transacoes.';
    END
    ELSE
    BEGIN
        PRINT 'Campo local_transacao já existe na tabela transacoes.';
    END
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.transacoes não existe.';
END

-- Verificar a estrutura atualizada da tabela
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