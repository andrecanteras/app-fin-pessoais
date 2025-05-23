-- create_tables.sql
-- Script para criar as tabelas no schema financas_pessoais

-- Verificar e criar tabela de categorias
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'categorias' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    CREATE TABLE financas_pessoais.categorias (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(100) NOT NULL,
        tipo CHAR(1) NOT NULL CHECK (tipo IN ('R', 'D')), -- R: Receita, D: Despesa
        descricao NVARCHAR(255),
        data_criacao DATETIME DEFAULT GETDATE(),
        ativo BIT DEFAULT 1
    );
    PRINT 'Tabela financas_pessoais.categorias criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.categorias já existe.';
END

-- Verificar e criar tabela de contas
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'contas' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    CREATE TABLE financas_pessoais.contas (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(100) NOT NULL,
        tipo NVARCHAR(50) NOT NULL, -- Corrente, Poupança, Investimento, etc.
        saldo_inicial DECIMAL(15, 2) DEFAULT 0.00,
        saldo_atual DECIMAL(15, 2) DEFAULT 0.00,
        instituicao NVARCHAR(100),
        data_criacao DATETIME DEFAULT GETDATE(),
        ativo BIT DEFAULT 1
    );
    PRINT 'Tabela financas_pessoais.contas criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.contas já existe.';
END

-- Verificar e criar tabela de transações
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'transacoes' AND schema_id = SCHEMA_ID('financas_pessoais'))
BEGIN
    CREATE TABLE financas_pessoais.transacoes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        descricao NVARCHAR(255) NOT NULL,
        valor DECIMAL(15, 2) NOT NULL,
        data_transacao DATE NOT NULL,
        tipo CHAR(1) NOT NULL CHECK (tipo IN ('R', 'D')), -- R: Receita, D: Despesa
        categoria_id INT,
        conta_id INT,
        observacao NVARCHAR(MAX),
        data_criacao DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (categoria_id) REFERENCES financas_pessoais.categorias(id),
        FOREIGN KEY (conta_id) REFERENCES financas_pessoais.contas(id)
    );
    PRINT 'Tabela financas_pessoais.transacoes criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.transacoes já existe.';
END

-- Verificar e criar tabela de metas financeiras
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
        data_criacao DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (categoria_id) REFERENCES financas_pessoais.categorias(id)
    );
    PRINT 'Tabela financas_pessoais.metas criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela financas_pessoais.metas já existe.';
END

-- Inserir categorias padrão se a tabela estiver vazia
IF NOT EXISTS (SELECT TOP 1 * FROM financas_pessoais.categorias)
BEGIN
    INSERT INTO financas_pessoais.categorias (nome, tipo, descricao)
    VALUES 
        ('Salário', 'R', 'Rendimentos de trabalho'),
        ('Investimentos', 'R', 'Rendimentos de investimentos'),
        ('Outros Rendimentos', 'R', 'Outras fontes de receita'),
        ('Alimentação', 'D', 'Gastos com alimentação'),
        ('Moradia', 'D', 'Aluguel, condomínio, etc.'),
        ('Transporte', 'D', 'Combustível, transporte público, etc.'),
        ('Saúde', 'D', 'Plano de saúde, medicamentos, etc.'),
        ('Educação', 'D', 'Cursos, mensalidades, etc.'),
        ('Lazer', 'D', 'Entretenimento, viagens, etc.'),
        ('Outros Gastos', 'D', 'Despesas diversas');
    
    PRINT 'Categorias padrão inseridas com sucesso.';
END
ELSE
BEGIN
    PRINT 'Categorias já existem, nenhuma categoria padrão foi inserida.';
END
