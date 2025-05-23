# list_contas.py
# Script simples para listar todas as contas usando o modelo Conta

import os
from dotenv import load_dotenv, dotenv_values
from src.models.conta import Conta
from src.database.connection import DatabaseConnection

def main():
    """Função principal para listar todas as contas."""
    print("=" * 50)
    print("LISTAGEM DE CONTAS".center(50))
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    load_dotenv(override=True)
    env_values = dotenv_values(".env")
    
    # Verificar conexão com o banco de dados
    print("\nTestando conexão com o banco de dados...")
    db = None
    try:
        db = DatabaseConnection()
        cursor = db.get_cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"Conexão estabelecida com sucesso!")
        print(f"Versão do SQL Server: {version}")
        
        # Verificar se o schema financas_pessoais existe
        print("\nVerificando schema financas_pessoais...")
        cursor.execute("SELECT schema_id FROM sys.schemas WHERE name = 'financas_pessoais'")
        schema = cursor.fetchone()
        
        if schema:
            print("Schema financas_pessoais encontrado.")
        else:
            print("Schema financas_pessoais NÃO encontrado!")
            print("Criando schema financas_pessoais...")
            cursor.execute("CREATE SCHEMA financas_pessoais")
            db.commit()
            print("Schema financas_pessoais criado com sucesso.")
        
        # Verificar se a tabela contas existe no schema financas_pessoais
        print("\nVerificando tabela financas_pessoais.contas...")
        cursor.execute("""
            SELECT 
                t.name AS table_name,
                t.create_date,
                t.modify_date
            FROM 
                sys.tables t
            JOIN 
                sys.schemas s ON t.schema_id = s.schema_id
            WHERE 
                s.name = 'financas_pessoais' AND t.name = 'contas'
        """)
        table = cursor.fetchone()
        
        if table:
            print(f"Tabela financas_pessoais.contas encontrada.")
            print(f"Data de criação: {table.create_date}")
            print(f"Data de modificação: {table.modify_date}")
        else:
            print("Tabela financas_pessoais.contas NÃO encontrada!")
            print("Você precisa criar a tabela antes de continuar.")
            print("Execute o script de criação de tabelas ou use o DatabaseSetup.")
        
        # Listar contas diretamente com SQL primeiro
        print("\nListando contas diretamente com SQL (financas_pessoais.contas):")
        cursor.execute("SELECT * FROM financas_pessoais.contas")
        rows = cursor.fetchall()
        
        if rows:
            print(f"Total de contas encontradas via SQL: {len(rows)}")
            
            # Obter nomes das colunas
            columns = [column[0] for column in cursor.description]
            print("-" * 100)
            print(" | ".join(columns))
            print("-" * 100)
            
            # Imprimir resultados
            for row in rows:
                values = [str(value) for value in row]
                print(" | ".join(values))
            
            print("-" * 100)
            
            # Calcular saldo total
            cursor.execute("SELECT SUM(saldo_atual) FROM financas_pessoais.contas WHERE ativo = 1")
            saldo_total = cursor.fetchone()[0] or 0
            print(f"Saldo total via SQL (contas ativas): R$ {saldo_total:.2f}")
        else:
            print("Nenhuma conta encontrada na tabela financas_pessoais.contas via SQL.")
        
        # Agora listar contas usando o modelo Conta
        print("\nListando contas usando o modelo Conta:")
        
        # Importante: Não feche a conexão db aqui, pois vamos usá-la para criar uma instância de Conta
        # que não fechará a conexão ao terminar
        
        # Criar uma instância de Conta com a conexão existente
        conta_temp = Conta()
        conta_temp.db = db  # Usar a mesma conexão
        
        # Executar uma consulta diretamente
        cursor = db.get_cursor()
        cursor.execute("SELECT * FROM contas")
        rows_modelo = cursor.fetchall()
        
        if rows_modelo:
            print(f"Total de contas encontradas via modelo: {len(rows_modelo)}")
            
            # Obter nomes das colunas
            columns = [column[0] for column in cursor.description]
            print("-" * 100)
            print(" | ".join(columns))
            print("-" * 100)
            
            # Imprimir resultados
            for row in rows_modelo:
                values = [str(value) for value in row]
                print(" | ".join(values))
            
            print("-" * 100)
        else:
            print("Nenhuma conta encontrada via modelo.")
        
        # Verificar se as consultas estão usando tabelas diferentes
        print("\nComparando as consultas:")
        print(f"- Consulta SQL direta encontrou: {len(rows)} contas")
        print(f"- Consulta via modelo encontrou: {len(rows_modelo)} contas")
        
        if len(rows) != len(rows_modelo):
            print("\nATENÇÃO: As consultas estão retornando números diferentes de contas!")
            print("Isso indica que o modelo Conta está consultando uma tabela diferente.")
            print("Verifique se o modelo está usando o schema correto (financas_pessoais).")
            
            # Verificar qual tabela o modelo está consultando
            print("\nVerificando qual tabela o modelo está consultando:")
            cursor.execute("SELECT DB_NAME() AS database_name")
            db_name = cursor.fetchone().database_name
            print(f"Banco de dados atual: {db_name}")
            
            # Listar todas as tabelas chamadas 'contas' no banco de dados
            cursor.execute("""
                SELECT 
                    s.name AS schema_name,
                    t.name AS table_name,
                    t.create_date,
                    t.modify_date
                FROM 
                    sys.tables t
                JOIN 
                    sys.schemas s ON t.schema_id = s.schema_id
                WHERE 
                    t.name = 'contas'
                ORDER BY 
                    s.name, t.name
            """)
            tables = cursor.fetchall()
            
            if tables:
                print("Tabelas 'contas' encontradas no banco de dados:")
                for table in tables:
                    print(f"- {table.schema_name}.{table.table_name} (Criada em: {table.create_date})")
            else:
                print("Nenhuma tabela 'contas' encontrada no banco de dados.")
        
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if db:
            db.close()
            print("Conexão com o banco de dados fechada.")
    
    print("\n" + "=" * 50)
    print("FIM DA LISTAGEM".center(50))
    print("=" * 50)

if __name__ == "__main__":
    main()
