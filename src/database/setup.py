import os
from src.database.connection import DatabaseConnection

class DatabaseSetup:
    """Classe para configurar o banco de dados."""
    
    def __init__(self, environment=None):
        self.environment = environment or os.getenv('ENVIRONMENT', 'prod')
        self.schema = f"financas_pessoais{'_dev' if self.environment == 'dev' else ''}"
        self.db = DatabaseConnection(environment=self.environment)
    
    def create_tables(self):
        """Cria as tabelas no banco de dados se não existirem."""
        try:
            # Criar o esquema se não existir
            self._create_schema()
            
            # Criar tabelas usando o esquema correto
            self._create_categorias_table()
            self._create_conta_dimensao_table()
            self._create_conta_saldos_table()
            self._create_meios_pagamento_table()
            self._create_transacoes_table()
            
            self.db.commit()
            print(f"Tabelas criadas com sucesso no esquema {self.schema}")
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao criar tabelas: {e}")
            return False
    
    def _create_schema(self):
        """Cria o esquema se não existir."""
        query = f"""
        IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{self.schema}')
        BEGIN
            EXEC('CREATE SCHEMA {self.schema}')
        END
        """
        self.db.execute_query(query)
    
    def _create_categorias_table(self):
        """Cria a tabela de categorias."""
        query = f"""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'categorias' AND schema_id = SCHEMA_ID('{self.schema}'))
        BEGIN
            CREATE TABLE {self.schema}.categorias (
                id INT IDENTITY(1,1) PRIMARY KEY,
                nome NVARCHAR(100) NOT NULL,
                tipo CHAR(1) NOT NULL,
                descricao NVARCHAR(255) NULL,
                categoria_pai_id INT NULL,
                nivel INT NOT NULL DEFAULT 1,
                data_criacao DATETIME DEFAULT GETDATE(),
                ativo BIT DEFAULT 1,
                CONSTRAINT FK_{self.schema}_categorias_pai FOREIGN KEY (categoria_pai_id) 
                    REFERENCES {self.schema}.categorias(id)
            )
        END
        """
        self.db.execute_query(query)
    
    def _create_conta_dimensao_table(self):
        """Cria a tabela de dimensão de contas."""
        query = f"""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'conta_dimensao' AND schema_id = SCHEMA_ID('{self.schema}'))
        BEGIN
            CREATE TABLE {self.schema}.conta_dimensao (
                id INT IDENTITY(1,1) NOT NULL,
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
                ativo BIT DEFAULT 1,
                PRIMARY KEY CLUSTERED (id ASC)
            )
        END
        """
        self.db.execute_query(query)
    
    def _create_conta_saldos_table(self):
        """Cria a tabela de saldos de contas."""
        query = f"""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'conta_saldos' AND schema_id = SCHEMA_ID('{self.schema}'))
        BEGIN
            CREATE TABLE {self.schema}.conta_saldos (
                id INT IDENTITY(1,1) NOT NULL,
                conta_dimensao_id INT NOT NULL,
                saldo_inicial DECIMAL(15, 2) DEFAULT 0.00,
                saldo_atual DECIMAL(15, 2) DEFAULT 0.00,
                data_criacao DATETIME DEFAULT GETDATE(),
                PRIMARY KEY CLUSTERED (id ASC),
                CONSTRAINT FK_{self.schema}_conta_saldos_dimensao FOREIGN KEY (conta_dimensao_id) 
                    REFERENCES {self.schema}.conta_dimensao (id)
            )
        END
        """
        self.db.execute_query(query)
    
    def _create_meios_pagamento_table(self):
        """Cria a tabela de meios de pagamento."""
        query = f"""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'meios_pagamento' AND schema_id = SCHEMA_ID('{self.schema}'))
        BEGIN
            CREATE TABLE {self.schema}.meios_pagamento (
                id INT IDENTITY(1,1) PRIMARY KEY,
                nome NVARCHAR(100) NOT NULL,
                tipo NVARCHAR(50) NOT NULL,
                conta_id INT NULL,
                data_criacao DATETIME DEFAULT GETDATE(),
                ativo BIT DEFAULT 1,
                CONSTRAINT FK_{self.schema}_meios_pagamento_conta FOREIGN KEY (conta_id) 
                    REFERENCES {self.schema}.conta_dimensao(id)
            )
        END
        """
        self.db.execute_query(query)
    
    def _create_transacoes_table(self):
        """Cria a tabela de transações."""
        query = f"""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'transacoes' AND schema_id = SCHEMA_ID('{self.schema}'))
        BEGIN
            CREATE TABLE {self.schema}.transacoes (
                id INT IDENTITY(1,1) PRIMARY KEY,
                descricao NVARCHAR(255) NOT NULL,
                valor DECIMAL(15, 2) NOT NULL,
                data_transacao DATE NOT NULL,
                tipo CHAR(1) NOT NULL,
                categoria_id INT NULL,
                conta_id INT NULL,
                meio_pagamento_id INT NULL,
                descricao_pagamento NVARCHAR(255) NULL,
                local_transacao NVARCHAR(255) NULL,
                observacao NVARCHAR(MAX) NULL,
                data_criacao DATETIME DEFAULT GETDATE(),
                ativo BIT DEFAULT 1,
                CONSTRAINT FK_{self.schema}_transacoes_categoria FOREIGN KEY (categoria_id) 
                    REFERENCES {self.schema}.categorias(id),
                CONSTRAINT FK_{self.schema}_transacoes_conta FOREIGN KEY (conta_id) 
                    REFERENCES {self.schema}.conta_dimensao(id),
                CONSTRAINT FK_{self.schema}_transacoes_meio_pagamento FOREIGN KEY (meio_pagamento_id) 
                    REFERENCES {self.schema}.meios_pagamento(id)
            )
        END
        """
        self.db.execute_query(query)