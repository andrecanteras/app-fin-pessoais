-- Script para criar o schema e tabelas no novo banco de dados
-- Autor: Amazon Q
-- Data: Gerado automaticamente

-- Parte 1: Criar o schema no novo banco de dados
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'financas_pessoais')
BEGIN
    EXEC('CREATE SCHEMA financas_pessoais');
    PRINT 'Schema financas_pessoais criado com sucesso no novo banco.';
END
ELSE
BEGIN
    PRINT 'Schema financas_pessoais já existe no novo banco.';
END

-- Parte 2: Criar tabelas no novo banco de dados

-- Tabela categorias
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'categorias' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    CREATE TABLE financas_pessoais.categorias (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(100) NOT NULL,
        tipo CHAR(1) NOT NULL CHECK (tipo IN ('R', 'D')), -- R: Receita, D: Despesa
        descricao NVARCHAR(255),
        data_criacao DATETIME DEFAULT GETDATE(),
        ativo BIT DEFAULT 1,
        categoria_pai_id INT NULL,
        nivel INT NOT NULL DEFAULT 1
    );
    PRINT 'Tabela financas_pessoais.categorias criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.categorias já existe.';
END

-- Tabela conta_dimensao
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'conta_dimensao' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    CREATE TABLE financas_pessoais.conta_dimensao (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(100) NOT NULL,
        tipo NVARCHAR(50) NOT NULL,
        instituicao NVARCHAR(100) NULL,
        agencia NVARCHAR(20) NULL,
        conta_contabil NVARCHAR(30) NULL,
        numero_banco NVARCHAR(10) NULL,
        titular NVARCHAR(150) NULL,
        nome_gerente NVARCHAR(100) NULL,
        contato_gerente NVARCHAR(100) NULL,
        data_criacao DATETIME DEFAULT GETDATE(),
        ativo BIT DEFAULT 1
    );
    PRINT 'Tabela financas_pessoais.conta_dimensao criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.conta_dimensao já existe.';
END

-- Tabela conta_saldos
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'conta_saldos' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    CREATE TABLE financas_pessoais.conta_saldos (
        id INT IDENTITY(1,1) PRIMARY KEY,
        conta_dimensao_id INT NOT NULL,
        saldo_inicial DECIMAL(15, 2) DEFAULT 0.00,
        saldo_atual DECIMAL(15, 2) DEFAULT 0.00,
        data_criacao DATETIME DEFAULT GETDATE()
    );
    PRINT 'Tabela financas_pessoais.conta_saldos criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.conta_saldos já existe.';
END

-- Tabela meios_pagamento
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'meios_pagamento' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    CREATE TABLE financas_pessoais.meios_pagamento (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(100) NOT NULL,
        descricao NVARCHAR(255),
        conta_id INT,
        tipo NVARCHAR(50) NOT NULL,
        data_criacao DATETIME DEFAULT GETDATE(),
        ativo BIT DEFAULT 1
    );
    PRINT 'Tabela financas_pessoais.meios_pagamento criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.meios_pagamento já existe.';
END

-- Tabela transacoes
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'transacoes' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    CREATE TABLE financas_pessoais.transacoes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        descricao NVARCHAR(255) NOT NULL,
        valor DECIMAL(15, 2) NOT NULL,
        data_transacao DATE NOT NULL,
        tipo CHAR(1) NOT NULL CHECK (tipo IN ('R', 'D')),
        categoria_id INT,
        conta_id INT,
        observacao NVARCHAR(MAX),
        data_criacao DATETIME DEFAULT GETDATE(),
        meio_pagamento_id INT NULL,
        descricao_pagamento NVARCHAR(255) NULL,
        local_transacao NVARCHAR(255) NULL
    );
    PRINT 'Tabela financas_pessoais.transacoes criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.transacoes já existe.';
END

-- Tabela metas
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'metas' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    CREATE TABLE financas_pessoais.metas (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(100) NOT NULL,
        valor_alvo DECIMAL(15, 2) NOT NULL,
        valor_atual DECIMAL(15, 2) DEFAULT 0.00,
        data_inicio DATE NOT NULL,
        data_fim DATE NOT NULL,
        categoria_id INT,
        observacao NVARCHAR(MAX),
        concluida BIT DEFAULT 0,
        data_criacao DATETIME DEFAULT GETDATE()
    );
    PRINT 'Tabela financas_pessoais.metas criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.metas já existe.';
END

-- Parte 3: Adicionar chaves estrangeiras

-- Adicionar chave estrangeira para auto-referência em categorias
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'categorias' AND schema_id = SCHEMA_ID('financas_pessoais'))
    AND NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Categoria_CategoriaPai' AND parent_object_id = OBJECT_ID('financas_pessoais.categorias'))
BEGIN
    ALTER TABLE financas_pessoais.categorias
    ADD CONSTRAINT FK_Categoria_CategoriaPai
    FOREIGN KEY (categoria_pai_id) REFERENCES financas_pessoais.categorias(id);
    PRINT 'Chave estrangeira FK_Categoria_CategoriaPai adicionada.';
END

-- Adicionar chave estrangeira para conta_saldos
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'conta_saldos' AND schema_id = SCHEMA_ID('financas_pessoais'))
    AND NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_conta_saldos_conta_dimensao' AND parent_object_id = OBJECT_ID('financas_pessoais.conta_saldos'))
BEGIN
    ALTER TABLE financas_pessoais.conta_saldos
    ADD CONSTRAINT FK_conta_saldos_conta_dimensao
    FOREIGN KEY (conta_dimensao_id) REFERENCES financas_pessoais.conta_dimensao(id);
    PRINT 'Chave estrangeira FK_conta_saldos_conta_dimensao adicionada.';
END

-- Adicionar FK para meios_pagamento
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'meios_pagamento' AND schema_id = SCHEMA_ID('financas_pessoais'))
    AND EXISTS (SELECT * FROM sys.tables WHERE name = 'conta_dimensao' AND schema_id = SCHEMA_ID('financas_pessoais'))
    AND NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_meios_pagamento_conta_dimensao' AND parent_object_id = OBJECT_ID('financas_pessoais.meios_pagamento'))
BEGIN
    ALTER TABLE financas_pessoais.meios_pagamento
    ADD CONSTRAINT FK_meios_pagamento_conta_dimensao
    FOREIGN KEY (conta_id) REFERENCES financas_pessoais.conta_dimensao(id);
    PRINT 'Chave estrangeira FK_meios_pagamento_conta_dimensao adicionada.';
END

-- Adicionar FKs para transacoes
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'transacoes' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    -- FK para categorias
    IF EXISTS (SELECT * FROM sys.tables WHERE name = 'categorias' AND schema_id = SCHEMA_ID('financas_pessoais'))
        AND NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK__transacoe__categ__618671AF' AND parent_object_id = OBJECT_ID('financas_pessoais.transacoes'))
    BEGIN
        ALTER TABLE financas_pessoais.transacoes
        ADD CONSTRAINT FK__transacoe__categ__618671AF
        FOREIGN KEY (categoria_id) REFERENCES financas_pessoais.categorias(id);
        PRINT 'Chave estrangeira FK__transacoe__categ__618671AF adicionada.';
    END

    -- FK para conta_dimensao
    IF EXISTS (SELECT * FROM sys.tables WHERE name = 'conta_dimensao' AND schema_id = SCHEMA_ID('financas_pessoais'))
        AND NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_transacoes_conta_dimensao' AND parent_object_id = OBJECT_ID('financas_pessoais.transacoes'))
    BEGIN
        ALTER TABLE financas_pessoais.transacoes
        ADD CONSTRAINT FK_transacoes_conta_dimensao
        FOREIGN KEY (conta_id) REFERENCES financas_pessoais.conta_dimensao(id);
        PRINT 'Chave estrangeira FK_transacoes_conta_dimensao adicionada.';
    END

    -- FK para meios_pagamento
    IF EXISTS (SELECT * FROM sys.tables WHERE name = 'meios_pagamento' AND schema_id = SCHEMA_ID('financas_pessoais'))
        AND NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Transacao_MeioPagamento' AND parent_object_id = OBJECT_ID('financas_pessoais.transacoes'))
    BEGIN
        ALTER TABLE financas_pessoais.transacoes
        ADD CONSTRAINT FK_Transacao_MeioPagamento
        FOREIGN KEY (meio_pagamento_id) REFERENCES financas_pessoais.meios_pagamento(id);
        PRINT 'Chave estrangeira FK_Transacao_MeioPagamento adicionada.';
    END
END

-- Adicionar FK para metas
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'metas' AND schema_id = SCHEMA_ID('financas_pessoais'))
    AND EXISTS (SELECT * FROM sys.tables WHERE name = 'categorias' AND schema_id = SCHEMA_ID('financas_pessoais'))
    AND NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK__metas__categoria__68336F3E' AND parent_object_id = OBJECT_ID('financas_pessoais.metas'))
BEGIN
    ALTER TABLE financas_pessoais.metas
    ADD CONSTRAINT FK__metas__categoria__68336F3E
    FOREIGN KEY (categoria_id) REFERENCES financas_pessoais.categorias(id);
    PRINT 'Chave estrangeira FK__metas__categoria__68336F3E adicionada.';
END

PRINT 'Estrutura do banco de dados criada com sucesso!';