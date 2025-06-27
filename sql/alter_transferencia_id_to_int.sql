-- Script para alterar o campo transferencia_id de UNIQUEIDENTIFIER para INT

-- Alterar no esquema de produção
IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('financas_pessoais.transacoes') AND name = 'transferencia_id')
BEGIN
    -- Remover a coluna existente
    ALTER TABLE financas_pessoais.transacoes DROP COLUMN transferencia_id
    PRINT 'Campo transferencia_id (UNIQUEIDENTIFIER) removido do esquema de produção.'
    
    -- Adicionar nova coluna como INT
    ALTER TABLE financas_pessoais.transacoes ADD transferencia_id INT NULL
    PRINT 'Campo transferencia_id (INT) adicionado ao esquema de produção.'
END

-- Alterar no esquema de desenvolvimento
IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('financas_pessoais_dev.transacoes') AND name = 'transferencia_id')
BEGIN
    -- Remover a coluna existente
    ALTER TABLE financas_pessoais_dev.transacoes DROP COLUMN transferencia_id
    PRINT 'Campo transferencia_id (UNIQUEIDENTIFIER) removido do esquema de desenvolvimento.'
    
    -- Adicionar nova coluna como INT
    ALTER TABLE financas_pessoais_dev.transacoes ADD transferencia_id INT NULL
    PRINT 'Campo transferencia_id (INT) adicionado ao esquema de desenvolvimento.'
END

PRINT 'Alteração do campo transferencia_id concluída com sucesso!'