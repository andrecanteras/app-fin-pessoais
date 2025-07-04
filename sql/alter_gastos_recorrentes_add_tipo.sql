-- Script para adicionar campo tipo na tabela gastos_recorrentes

-- Adicionar campo tipo no esquema de produção
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('financas_pessoais.gastos_recorrentes') AND name = 'tipo')
BEGIN
    ALTER TABLE financas_pessoais.gastos_recorrentes ADD tipo CHAR(1) NOT NULL DEFAULT 'D'
    PRINT 'Campo tipo adicionado ao esquema de produção.'
END

-- Adicionar campo tipo no esquema de desenvolvimento
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('financas_pessoais_dev.gastos_recorrentes') AND name = 'tipo')
BEGIN
    ALTER TABLE financas_pessoais_dev.gastos_recorrentes ADD tipo CHAR(1) NOT NULL DEFAULT 'D'
    PRINT 'Campo tipo adicionado ao esquema de desenvolvimento.'
END

PRINT 'Campo tipo adicionado com sucesso nas tabelas gastos_recorrentes!'