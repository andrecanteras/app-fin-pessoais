-- Adicionar coluna titular à tabela conta_dimensao
ALTER TABLE [financas_pessoais].[conta_dimensao]
ADD [titular] [nvarchar](150) NULL;