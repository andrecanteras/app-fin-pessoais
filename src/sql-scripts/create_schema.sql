-- create_schema.sql
-- Script para criar o schema financas_pessoais

-- Verificar se o schema já existe
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'financas_pessoais')
BEGIN
    -- Criar o schema
    EXEC('CREATE SCHEMA financas_pessoais');
    PRINT 'Schema financas_pessoais criado com sucesso.';
END
ELSE
BEGIN
    PRINT 'Schema financas_pessoais já existe.';
END
