-- Arquivo: sql/create_gastos_recorrentes_tables.sql

-- Criar tabela de gastos recorrentes
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'gastos_recorrentes' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    CREATE TABLE financas_pessoais.gastos_recorrentes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(100) NOT NULL,
        valor DECIMAL(15, 2) NOT NULL,
        dia_vencimento INT NOT NULL,
        periodicidade NVARCHAR(20) NOT NULL, -- 'Mensal', 'Trimestral', 'Anual', etc.
        categoria_id INT NULL,
        conta_id INT NULL,
        meio_pagamento_id INT NULL,
        data_inicio DATE NOT NULL,
        data_fim DATE NULL,
        gerar_transacao BIT DEFAULT 0,
        observacao NVARCHAR(MAX) NULL,
        ativo BIT DEFAULT 1,
        data_criacao DATETIME DEFAULT GETDATE(),
        CONSTRAINT FK_financas_pessoais_gastos_recorrentes_categoria FOREIGN KEY (categoria_id) 
            REFERENCES financas_pessoais.categorias(id),
        CONSTRAINT FK_financas_pessoais_gastos_recorrentes_conta FOREIGN KEY (conta_id) 
            REFERENCES financas_pessoais.conta_dimensao(id),
        CONSTRAINT FK_financas_pessoais_gastos_recorrentes_meio_pagamento FOREIGN KEY (meio_pagamento_id) 
            REFERENCES financas_pessoais.meios_pagamento(id)
    )
    PRINT 'Tabela financas_pessoais.gastos_recorrentes criada com sucesso.'
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.gastos_recorrentes já existe.'
END

-- Criar tabela de pagamentos recorrentes
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'pagamentos_recorrentes' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    CREATE TABLE financas_pessoais.pagamentos_recorrentes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        gasto_recorrente_id INT NOT NULL,
        ano INT NOT NULL,
        mes INT NOT NULL,
        data_pagamento DATE NULL, -- NULL significa não pago
        valor_pago DECIMAL(15, 2) NULL,
        transacao_id INT NULL, -- Referência à transação gerada (para integração futura)
        observacao NVARCHAR(MAX) NULL,
        data_criacao DATETIME DEFAULT GETDATE(),
        CONSTRAINT FK_financas_pessoais_pagamentos_recorrentes_gasto FOREIGN KEY (gasto_recorrente_id) 
            REFERENCES financas_pessoais.gastos_recorrentes(id),
        CONSTRAINT FK_financas_pessoais_pagamentos_recorrentes_transacao FOREIGN KEY (transacao_id) 
            REFERENCES financas_pessoais.transacoes(id),
        CONSTRAINT UQ_financas_pessoais_pagamentos_recorrentes_periodo UNIQUE (gasto_recorrente_id, ano, mes)
    )
    PRINT 'Tabela financas_pessoais.pagamentos_recorrentes criada com sucesso.'
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.pagamentos_recorrentes já existe.'
END

-- Criar tabela de gastos recorrentes no ambiente de desenvolvimento
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'gastos_recorrentes' AND schema_id = SCHEMA_ID('financas_pessoais_dev'))
BEGIN
    CREATE TABLE financas_pessoais_dev.gastos_recorrentes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(100) NOT NULL,
        valor DECIMAL(15, 2) NOT NULL,
        dia_vencimento INT NOT NULL,
        periodicidade NVARCHAR(20) NOT NULL, -- 'Mensal', 'Trimestral', 'Anual', etc.
        categoria_id INT NULL,
        conta_id INT NULL,
        meio_pagamento_id INT NULL,
        data_inicio DATE NOT NULL,
        data_fim DATE NULL,
        gerar_transacao BIT DEFAULT 0,
        observacao NVARCHAR(MAX) NULL,
        ativo BIT DEFAULT 1,
        data_criacao DATETIME DEFAULT GETDATE(),
        CONSTRAINT FK_financas_pessoais_dev_gastos_recorrentes_categoria FOREIGN KEY (categoria_id) 
            REFERENCES financas_pessoais_dev.categorias(id),
        CONSTRAINT FK_financas_pessoais_dev_gastos_recorrentes_conta FOREIGN KEY (conta_id) 
            REFERENCES financas_pessoais_dev.conta_dimensao(id),
        CONSTRAINT FK_financas_pessoais_dev_gastos_recorrentes_meio_pagamento FOREIGN KEY (meio_pagamento_id) 
            REFERENCES financas_pessoais_dev.meios_pagamento(id)
    )
    PRINT 'Tabela financas_pessoais_dev.gastos_recorrentes criada com sucesso.'
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais_dev.gastos_recorrentes já existe.'
END

-- Criar tabela de pagamentos recorrentes no ambiente de desenvolvimento
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'pagamentos_recorrentes' AND schema_id = SCHEMA_ID('financas_pessoais_dev'))
BEGIN
    CREATE TABLE financas_pessoais_dev.pagamentos_recorrentes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        gasto_recorrente_id INT NOT NULL,
        ano INT NOT NULL,
        mes INT NOT NULL,
        data_pagamento DATE NULL, -- NULL significa não pago
        valor_pago DECIMAL(15, 2) NULL,
        transacao_id INT NULL, -- Referência à transação gerada (para integração futura)
        observacao NVARCHAR(MAX) NULL,
        data_criacao DATETIME DEFAULT GETDATE(),
        CONSTRAINT FK_financas_pessoais_dev_pagamentos_recorrentes_gasto FOREIGN KEY (gasto_recorrente_id) 
            REFERENCES financas_pessoais_dev.gastos_recorrentes(id),
        CONSTRAINT FK_financas_pessoais_dev_pagamentos_recorrentes_transacao FOREIGN KEY (transacao_id) 
            REFERENCES financas_pessoais_dev.transacoes(id),
        CONSTRAINT UQ_financas_pessoais_dev_pagamentos_recorrentes_periodo UNIQUE (gasto_recorrente_id, ano, mes)
    )
    PRINT 'Tabela financas_pessoais_dev.pagamentos_recorrentes criada com sucesso.'
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais_dev.pagamentos_recorrentes já existe.'
END
