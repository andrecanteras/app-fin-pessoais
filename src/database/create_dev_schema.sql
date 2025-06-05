-- Script para criar o esquema de desenvolvimento
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'financas_pessoais_dev')
BEGIN
    EXEC('CREATE SCHEMA financas_pessoais_dev')
    PRINT 'Esquema financas_pessoais_dev criado com sucesso.'
END
ELSE
BEGIN
    PRINT 'Esquema financas_pessoais_dev já existe.'
END