from .connection import DatabaseConnection

class DatabaseSetup:
    """Classe para configurar o banco de dados e criar as tabelas necessárias."""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_tables(self):
        """Cria as tabelas necessárias para o aplicativo."""
        try:
            cursor = self.db.get_cursor()
            
            # Tabela de categorias
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'categorias')
                BEGIN
                    CREATE TABLE categorias (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        nome NVARCHAR(100) NOT NULL,
                        tipo CHAR(1) NOT NULL CHECK (tipo IN ('R', 'D')), -- R: Receita, D: Despesa
                        descricao NVARCHAR(255),
                        data_criacao DATETIME DEFAULT GETDATE(),
                        ativo BIT DEFAULT 1
                    )
                END
            """)
            
            # Tabela de contas
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'contas')
                BEGIN
                    CREATE TABLE contas (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        nome NVARCHAR(100) NOT NULL,
                        tipo NVARCHAR(50) NOT NULL, -- Corrente, Poupança, Investimento, etc.
                        saldo_inicial DECIMAL(15, 2) DEFAULT 0.00,
                        saldo_atual DECIMAL(15, 2) DEFAULT 0.00,
                        instituicao NVARCHAR(100),
                        data_criacao DATETIME DEFAULT GETDATE(),
                        ativo BIT DEFAULT 1
                    )
                END
            """)
            
            # Tabela de transações
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'transacoes')
                BEGIN
                    CREATE TABLE transacoes (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        descricao NVARCHAR(255) NOT NULL,
                        valor DECIMAL(15, 2) NOT NULL,
                        data_transacao DATE NOT NULL,
                        tipo CHAR(1) NOT NULL CHECK (tipo IN ('R', 'D')), -- R: Receita, D: Despesa
                        categoria_id INT,
                        conta_id INT,
                        observacao NVARCHAR(MAX),
                        data_criacao DATETIME DEFAULT GETDATE(),
                        FOREIGN KEY (categoria_id) REFERENCES categorias(id),
                        FOREIGN KEY (conta_id) REFERENCES contas(id)
                    )
                END
            """)
            
            # Tabela de metas financeiras
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'metas')
                BEGIN
                    CREATE TABLE metas (
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
                        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
                    )
                END
            """)
            
            # Inserir algumas categorias padrão
            cursor.execute("""
                IF NOT EXISTS (SELECT TOP 1 * FROM categorias)
                BEGIN
                    INSERT INTO categorias (nome, tipo, descricao)
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
                        ('Outros Gastos', 'D', 'Despesas diversas')
                END
            """)
            
            self.db.commit()
            print("Tabelas criadas com sucesso!")
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao criar tabelas: {e}")
            raise
        finally:
            self.db.close()
    
    def reset_database(self):
        """Remove todas as tabelas e recria o banco de dados (use com cuidado!)."""
        try:
            cursor = self.db.get_cursor()
            
            # Desabilitar verificação de chaves estrangeiras
            cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'")
            
            # Remover todas as tabelas
            cursor.execute("""
                DECLARE @sql NVARCHAR(MAX) = '';
                SELECT @sql += 'DROP TABLE ' + QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME) + ';'
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE';
                EXEC sp_executesql @sql;
            """)
            
            self.db.commit()
            print("Banco de dados resetado com sucesso!")
            
            # Recriar as tabelas
            self.create_tables()
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao resetar banco de dados: {e}")
            raise
        finally:
            self.db.close()