"""
Script para recriar as tabelas nos ambientes de produção e desenvolvimento.
"""
import os
import pyodbc
from dotenv import load_dotenv

def create_tables(environment="both"):
    """Recria as tabelas no ambiente especificado.
    
    Args:
        environment: "prod", "dev" ou "both" para ambos
    """
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurações de conexão
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_DATABASE')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    # Esquemas
    schemas = []
    if environment == "prod" or environment == "both":
        schemas.append("financas_pessoais")
    if environment == "dev" or environment == "both":
        schemas.append("financas_pessoais_dev")
    
    # Conectar ao banco de dados
    connection_string = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    try:
        print(f"Iniciando criação de tabelas...")
        
        for schema in schemas:
            print(f"Criando tabelas no schema {schema}...")
            
            # Verificar se o esquema existe
            cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{schema}')
            BEGIN
                EXEC('CREATE SCHEMA {schema}')
            END
            """)
            conn.commit()
            
            # Criar tabela categorias
            print(f"Criando tabela {schema}.categorias...")
            cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'categorias' AND schema_id = SCHEMA_ID('{schema}'))
            BEGIN
                CREATE TABLE {schema}.categorias (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nome NVARCHAR(100) NOT NULL,
                    tipo CHAR(1) NOT NULL,
                    descricao NVARCHAR(255) NULL,
                    categoria_pai_id INT NULL,
                    nivel INT NOT NULL DEFAULT 1,
                    data_criacao DATETIME DEFAULT GETDATE(),
                    ativo BIT DEFAULT 1
                )
            END
            """)
            conn.commit()
            
            # Criar tabela conta_dimensao
            print(f"Criando tabela {schema}.conta_dimensao...")
            cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'conta_dimensao' AND schema_id = SCHEMA_ID('{schema}'))
            BEGIN
                CREATE TABLE {schema}.conta_dimensao (
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
            """)
            conn.commit()
            
            # Criar tabela conta_saldos
            print(f"Criando tabela {schema}.conta_saldos...")
            cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'conta_saldos' AND schema_id = SCHEMA_ID('{schema}'))
            BEGIN
                CREATE TABLE {schema}.conta_saldos (
                    id INT IDENTITY(1,1) NOT NULL,
                    conta_dimensao_id INT NOT NULL,
                    saldo_inicial DECIMAL(15, 2) DEFAULT 0.00,
                    saldo_atual DECIMAL(15, 2) DEFAULT 0.00,
                    data_criacao DATETIME DEFAULT GETDATE(),
                    PRIMARY KEY CLUSTERED (id ASC)
                )
            END
            """)
            conn.commit()
            
            # Criar tabela meios_pagamento
            print(f"Criando tabela {schema}.meios_pagamento...")
            cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'meios_pagamento' AND schema_id = SCHEMA_ID('{schema}'))
            BEGIN
                CREATE TABLE {schema}.meios_pagamento (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nome NVARCHAR(100) NOT NULL,
                    tipo NVARCHAR(50) NOT NULL,
                    descricao NVARCHAR(255) NULL,
                    conta_id INT NULL,
                    data_criacao DATETIME DEFAULT GETDATE(),
                    ativo BIT DEFAULT 1
                )
            END
            """)
            conn.commit()
            
            # Criar tabela transacoes
            print(f"Criando tabela {schema}.transacoes...")
            cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'transacoes' AND schema_id = SCHEMA_ID('{schema}'))
            BEGIN
                CREATE TABLE {schema}.transacoes (
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
                    ativo BIT DEFAULT 1
                )
            END
            """)
            conn.commit()
            
            # Adicionar restrições de chave estrangeira
            print(f"Adicionando restrições de chave estrangeira...")
            
            # Restrição para categorias (auto-referência)
            cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_{schema}_categorias_pai')
            BEGIN
                ALTER TABLE {schema}.categorias
                ADD CONSTRAINT FK_{schema}_categorias_pai 
                FOREIGN KEY (categoria_pai_id) REFERENCES {schema}.categorias(id)
            END
            """)
            conn.commit()
            
            # Restrição para conta_saldos
            cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_{schema}_conta_saldos_dimensao')
            BEGIN
                ALTER TABLE {schema}.conta_saldos
                ADD CONSTRAINT FK_{schema}_conta_saldos_dimensao 
                FOREIGN KEY (conta_dimensao_id) REFERENCES {schema}.conta_dimensao(id)
            END
            """)
            conn.commit()
            
            # Restrição para meios_pagamento
            cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_{schema}_meios_pagamento_conta')
            BEGIN
                ALTER TABLE {schema}.meios_pagamento
                ADD CONSTRAINT FK_{schema}_meios_pagamento_conta 
                FOREIGN KEY (conta_id) REFERENCES {schema}.conta_dimensao(id)
            END
            """)
            conn.commit()
            
            # Restrições para transacoes
            cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_{schema}_transacoes_categoria')
            BEGIN
                ALTER TABLE {schema}.transacoes
                ADD CONSTRAINT FK_{schema}_transacoes_categoria 
                FOREIGN KEY (categoria_id) REFERENCES {schema}.categorias(id)
            END
            """)
            conn.commit()
            
            cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_{schema}_transacoes_conta')
            BEGIN
                ALTER TABLE {schema}.transacoes
                ADD CONSTRAINT FK_{schema}_transacoes_conta 
                FOREIGN KEY (conta_id) REFERENCES {schema}.conta_dimensao(id)
            END
            """)
            conn.commit()
            
            cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_{schema}_transacoes_meio_pagamento')
            BEGIN
                ALTER TABLE {schema}.transacoes
                ADD CONSTRAINT FK_{schema}_transacoes_meio_pagamento 
                FOREIGN KEY (meio_pagamento_id) REFERENCES {schema}.meios_pagamento(id)
            END
            """)
            conn.commit()
        
        print("Criação de tabelas concluída com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao criar tabelas: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Perguntar qual ambiente criar
    print("Em qual ambiente você deseja criar as tabelas?")
    print("1. Apenas Produção")
    print("2. Apenas Desenvolvimento")
    print("3. Ambos (Produção e Desenvolvimento)")
    
    choice = input("Escolha (1-3): ")
    
    if choice == "1":
        environment = "prod"
    elif choice == "2":
        environment = "dev"
    else:
        environment = "both"
    
    create_tables(environment)
