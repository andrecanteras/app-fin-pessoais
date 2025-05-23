-- Criar tabela conta_dimensao com colunas adicionais
CREATE TABLE [financas_pessoais].[conta_dimensao](
    [id] [int] IDENTITY(1,1) NOT NULL,
    [nome] [nvarchar](100) NOT NULL,
    [tipo] [nvarchar](50) NOT NULL,
    [instituicao] [nvarchar](100) NULL,
    [agencia] [nvarchar](20) NULL,
    [conta_contabil] [nvarchar](30) NULL,
    [numero_banco] [nvarchar](10) NULL,
    [titular] [nvarchar](150) NULL,
    [nome_gerente] [nvarchar](100) NULL,
    [contato_gerente] [nvarchar](100) NULL,
    [data_criacao] [datetime] DEFAULT (getdate()),
    [ativo] [bit] DEFAULT ((1)),
    PRIMARY KEY CLUSTERED ([id] ASC)
);

-- Criar tabela conta_saldos
CREATE TABLE [financas_pessoais].[conta_saldos](
    [id] [int] IDENTITY(1,1) NOT NULL,
    [conta_dimensao_id] [int] NOT NULL,
    [saldo_inicial] [decimal](15, 2) DEFAULT ((0.00)),
    [saldo_atual] [decimal](15, 2) DEFAULT ((0.00)),
    [data_criacao] [datetime] DEFAULT (getdate()),
    PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_conta_saldos_conta_dimensao] FOREIGN KEY ([conta_dimensao_id]) 
    REFERENCES [financas_pessoais].[conta_dimensao] ([id])
);

-- Script para migrar dados da tabela contas existente
INSERT INTO [financas_pessoais].[conta_dimensao] (nome, tipo, instituicao, data_criacao, ativo)
SELECT nome, tipo, instituicao, data_criacao, ativo FROM [financas_pessoais].[contas];

-- Inserir registros na tabela conta_saldos
INSERT INTO [financas_pessoais].[conta_saldos] (conta_dimensao_id, saldo_inicial, saldo_atual, data_criacao)
SELECT id, saldo_inicial, saldo_atual, data_criacao FROM [financas_pessoais].[contas];