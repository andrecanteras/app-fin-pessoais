"""
Utilitário para copiar dados do ambiente de produção para o ambiente de desenvolvimento.
"""
import os
import pyodbc
from dotenv import load_dotenv
from PyQt5.QtCore import QObject, pyqtSignal

class DataCopyUtil(QObject):
    """Classe para copiar dados entre ambientes."""
    
    # Sinais para comunicação com a interface
    progress_updated = pyqtSignal(str)
    operation_completed = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
    
    def create_tables_in_dev(self, conn, cursor, dev_schema):
        """Cria as tabelas no esquema de desenvolvimento."""
        self.progress_updated.emit("Criando tabelas no esquema de desenvolvimento...")
        
        # Criar tabela categorias
        self.progress_updated.emit("Criando tabela categorias...")
        cursor.execute(f"""
        CREATE TABLE {dev_schema}.categorias (
            id INT IDENTITY(1,1) PRIMARY KEY,
            nome NVARCHAR(100) NOT NULL,
            tipo CHAR(1) NOT NULL,
            descricao NVARCHAR(255) NULL,
            categoria_pai_id INT NULL,
            nivel INT NOT NULL DEFAULT 1,
            data_criacao DATETIME DEFAULT GETDATE(),
            ativo BIT DEFAULT 1
        )
        """)
        conn.commit()
        
        # Adicionar a restrição de chave estrangeira para categoria_pai_id
        cursor.execute(f"""
        ALTER TABLE {dev_schema}.categorias
        ADD CONSTRAINT FK_{dev_schema}_categorias_pai 
        FOREIGN KEY (categoria_pai_id) REFERENCES {dev_schema}.categorias(id)
        """)
        conn.commit()
        
        # Criar tabela conta_dimensao
        self.progress_updated.emit("Criando tabela conta_dimensao...")
        cursor.execute(f"""
        CREATE TABLE {dev_schema}.conta_dimensao (
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
        """)
        conn.commit()
        
        # Criar tabela conta_saldos
        self.progress_updated.emit("Criando tabela conta_saldos...")
        cursor.execute(f"""
        CREATE TABLE {dev_schema}.conta_saldos (
            id INT IDENTITY(1,1) NOT NULL,
            conta_dimensao_id INT NOT NULL,
            saldo_inicial DECIMAL(15, 2) DEFAULT 0.00,
            saldo_atual DECIMAL(15, 2) DEFAULT 0.00,
            data_criacao DATETIME DEFAULT GETDATE(),
            PRIMARY KEY CLUSTERED (id ASC),
            CONSTRAINT FK_{dev_schema}_conta_saldos_dimensao FOREIGN KEY (conta_dimensao_id) 
                REFERENCES {dev_schema}.conta_dimensao (id)
        )
        """)
        conn.commit()
        
        # Criar tabela meios_pagamento
        self.progress_updated.emit("Criando tabela meios_pagamento...")
        cursor.execute(f"""
        CREATE TABLE {dev_schema}.meios_pagamento (
            id INT IDENTITY(1,1) PRIMARY KEY,
            nome NVARCHAR(100) NOT NULL,
            tipo NVARCHAR(50) NOT NULL,
            descricao NVARCHAR(255) NULL,
            conta_id INT NULL,
            data_criacao DATETIME DEFAULT GETDATE(),
            ativo BIT DEFAULT 1,
            CONSTRAINT FK_{dev_schema}_meios_pagamento_conta FOREIGN KEY (conta_id) 
                REFERENCES {dev_schema}.conta_dimensao(id)
        )
        """)
        conn.commit()
        
        # Criar tabela transacoes
        self.progress_updated.emit("Criando tabela transacoes...")
        cursor.execute(f"""
        CREATE TABLE {dev_schema}.transacoes (
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
            CONSTRAINT FK_{dev_schema}_transacoes_categoria FOREIGN KEY (categoria_id) 
                REFERENCES {dev_schema}.categorias(id),
            CONSTRAINT FK_{dev_schema}_transacoes_conta FOREIGN KEY (conta_id) 
                REFERENCES {dev_schema}.conta_dimensao(id),
            CONSTRAINT FK_{dev_schema}_transacoes_meio_pagamento FOREIGN KEY (meio_pagamento_id) 
                REFERENCES {dev_schema}.meios_pagamento(id)
        )
        """)
        conn.commit()
    
    def copy_data_from_prod_to_dev(self):
        """Copia todos os dados do esquema de produção para o esquema de desenvolvimento."""
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Configurações de conexão
        server = os.getenv('DB_SERVER')
        database = os.getenv('DB_DATABASE')
        username = os.getenv('DB_USERNAME')
        password = os.getenv('DB_PASSWORD')
        driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        
        # Esquemas
        prod_schema = "financas_pessoais"
        dev_schema = "financas_pessoais_dev"
        
        # Tabelas a serem copiadas (na ordem correta para respeitar as chaves estrangeiras)
        tables = [
            "categorias",
            "conta_dimensao",
            "conta_saldos",
            "meios_pagamento",
            "transacoes"
        ]
        
        # Tabelas na ordem inversa para exclusão (para respeitar as chaves estrangeiras)
        delete_order = [
            "transacoes",
            "meios_pagamento",
            "conta_saldos",
            "conta_dimensao",
            "categorias"
        ]
        
        # Conectar ao banco de dados
        connection_string = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        try:
            self.progress_updated.emit("Iniciando cópia de dados de PROD para DEV...")
            
            # Verificar se o esquema de desenvolvimento existe
            cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{dev_schema}')
            BEGIN
                EXEC('CREATE SCHEMA {dev_schema}')
            END
            """)
            conn.commit()
            self.progress_updated.emit(f"Esquema {dev_schema} verificado.")
            
            # Primeiro, excluir tabelas na ordem inversa para respeitar as chaves estrangeiras
            self.progress_updated.emit("Removendo tabelas existentes...")
            for table in delete_order:
                self.progress_updated.emit(f"Verificando tabela {table}...")
                
                cursor.execute(f"""
                IF EXISTS (SELECT * FROM sys.tables WHERE name = '{table}' AND schema_id = SCHEMA_ID('{dev_schema}'))
                BEGIN
                    DROP TABLE {dev_schema}.{table}
                END
                """)
                conn.commit()
            
            # Criar as tabelas no esquema de desenvolvimento
            self.create_tables_in_dev(conn, cursor, dev_schema)
            
            # Finalmente, copiar os dados na ordem correta
            for table in tables:
                self.progress_updated.emit(f"Copiando dados para tabela {table}...")
                
                # Obter colunas da tabela
                cursor.execute(f"""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = '{prod_schema}' AND TABLE_NAME = '{table}'
                ORDER BY ORDINAL_POSITION
                """)
                columns = [row.COLUMN_NAME for row in cursor.fetchall()]
                columns_str = ', '.join(columns)
                
                # Copiar dados com IDENTITY_INSERT explicitamente ON
                try:
                    # Verificar se a tabela tem coluna de identidade
                    cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM sys.identity_columns 
                    WHERE object_id = OBJECT_ID('{dev_schema}.{table}')
                    """)
                    has_identity = cursor.fetchone()[0] > 0
                    
                    if has_identity:
                        # Desativar verificação de identidade para permitir inserção com IDs específicos
                        cursor.execute(f"SET IDENTITY_INSERT {dev_schema}.{table} ON")
                    
                    # Copiar dados com lista de colunas explícita
                    cursor.execute(f"""
                    INSERT INTO {dev_schema}.{table} ({columns_str})
                    SELECT {columns_str} FROM {prod_schema}.{table}
                    """)
                    
                    if has_identity:
                        # Reativar verificação de identidade
                        cursor.execute(f"SET IDENTITY_INSERT {dev_schema}.{table} OFF")
                    
                    conn.commit()
                except Exception as e:
                    self.progress_updated.emit(f"Erro ao copiar dados da tabela {table}: {e}")
                    conn.rollback()
                    raise
                
                # Verificar contagem de registros
                cursor.execute(f"""
                DECLARE @prod_count INT, @dev_count INT
                
                SELECT @prod_count = COUNT(*) FROM {prod_schema}.{table}
                SELECT @dev_count = COUNT(*) FROM {dev_schema}.{table}
                
                SELECT 
                    '{table}' AS [Tabela],
                    @prod_count AS [Registros em Produção],
                    @dev_count AS [Registros em Desenvolvimento],
                    CASE WHEN @prod_count = @dev_count THEN 'OK' ELSE 'ERRO' END AS [Status]
                """)
                
                result = cursor.fetchone()
                self.progress_updated.emit(f"Tabela: {result[0]}, Prod: {result[1]}, Dev: {result[2]}, Status: {result[3]}")
            
            self.operation_completed.emit(True, "Cópia de dados concluída com sucesso!")
            
        except Exception as e:
            conn.rollback()
            error_msg = f"Erro ao copiar dados: {e}"
            self.progress_updated.emit(error_msg)
            self.operation_completed.emit(False, error_msg)
        finally:
            conn.close()