"""
Script para limpar os dados dos ambientes de produção e desenvolvimento.
"""
import os
import pyodbc
from dotenv import load_dotenv

def clean_data(environment="both"):
    """Limpa os dados do ambiente especificado sem excluir as tabelas.
    
    Args:
        environment: "prod", "dev" ou "both" para limpar ambos
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
    
    # Tabelas na ordem inversa para exclusão de dados (para respeitar as chaves estrangeiras)
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
        print(f"Iniciando limpeza de dados...")
        
        for schema in schemas:
            print(f"Limpando dados do schema {schema}...")
            
            # Verificar se o esquema existe
            cursor.execute(f"""
            IF EXISTS (SELECT * FROM sys.schemas WHERE name = '{schema}')
            BEGIN
                SELECT 1
            END
            ELSE
            BEGIN
                SELECT 0
            END
            """)
            schema_exists = cursor.fetchone()[0]
            
            if not schema_exists:
                print(f"Schema {schema} não existe. Criando...")
                cursor.execute(f"CREATE SCHEMA {schema}")
                conn.commit()
                continue
            
            # Limpar dados de todas as tabelas na ordem correta
            for table in delete_order:
                # Verificar se a tabela existe
                cursor.execute(f"""
                IF EXISTS (SELECT * FROM sys.tables WHERE name = '{table}' AND schema_id = SCHEMA_ID('{schema}'))
                BEGIN
                    SELECT 1
                END
                ELSE
                BEGIN
                    SELECT 0
                END
                """)
                table_exists = cursor.fetchone()[0]
                
                if table_exists:
                    print(f"Limpando dados da tabela {schema}.{table}...")
                    try:
                        cursor.execute(f"TRUNCATE TABLE {schema}.{table}")
                        conn.commit()
                    except Exception as e:
                        print(f"Aviso: Não foi possível usar TRUNCATE na tabela {schema}.{table}: {e}")
                        try:
                            cursor.execute(f"DELETE FROM {schema}.{table}")
                            conn.commit()
                        except Exception as e2:
                            print(f"Aviso: Não foi possível limpar dados da tabela {schema}.{table}: {e2}")
                            conn.rollback()
        
        print("Limpeza de dados concluída com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao limpar dados: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Perguntar qual ambiente limpar
    print("Qual ambiente você deseja limpar?")
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
    
    # Confirmar a operação
    confirm = input(f"ATENÇÃO: Esta operação excluirá TODOS os dados do(s) ambiente(s) selecionado(s). Esta ação NÃO PODE ser desfeita!\nDigite 'CONFIRMAR' para continuar: ")
    
    if confirm == "CONFIRMAR":
        clean_data(environment)
    else:
        print("Operação cancelada.")
