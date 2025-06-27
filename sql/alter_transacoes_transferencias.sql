-- Script para adicionar campos de transferência na tabela transacoes

-- Adicionar campos para transferências no esquema de produção
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('financas_pessoais.transacoes') AND name = 'transferencia_id')
BEGIN
    ALTER TABLE financas_pessoais.transacoes ADD transferencia_id UNIQUEIDENTIFIER NULL
    PRINT 'Campo transferencia_id adicionado ao esquema de produção.'
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('financas_pessoais.transacoes') AND name = 'conta_destino_id')
BEGIN
    ALTER TABLE financas_pessoais.transacoes ADD conta_destino_id INT NULL
    PRINT 'Campo conta_destino_id adicionado ao esquema de produção.'
    
    -- Adicionar constraint de chave estrangeira
    ALTER TABLE financas_pessoais.transacoes
    ADD CONSTRAINT FK_financas_pessoais_transacoes_conta_destino 
    FOREIGN KEY (conta_destino_id) REFERENCES financas_pessoais.conta_dimensao(id)
END

-- Adicionar campos para transferências no esquema de desenvolvimento
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('financas_pessoais_dev.transacoes') AND name = 'transferencia_id')
BEGIN
    ALTER TABLE financas_pessoais_dev.transacoes ADD transferencia_id UNIQUEIDENTIFIER NULL
    PRINT 'Campo transferencia_id adicionado ao esquema de desenvolvimento.'
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('financas_pessoais_dev.transacoes') AND name = 'conta_destino_id')
BEGIN
    ALTER TABLE financas_pessoais_dev.transacoes ADD conta_destino_id INT NULL
    PRINT 'Campo conta_destino_id adicionado ao esquema de desenvolvimento.'
    
    -- Adicionar constraint de chave estrangeira
    ALTER TABLE financas_pessoais_dev.transacoes
    ADD CONSTRAINT FK_financas_pessoais_dev_transacoes_conta_destino 
    FOREIGN KEY (conta_destino_id) REFERENCES financas_pessoais_dev.conta_dimensao(id)
END

PRINT 'Alterações na tabela transacoes concluídas com sucesso!'