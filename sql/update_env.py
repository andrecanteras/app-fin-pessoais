"""
Script para atualizar o arquivo .env com o novo banco de dados
"""
import os
from dotenv import load_dotenv

def update_env_file(new_database_name):
    """
    Atualiza o arquivo .env com o novo nome do banco de dados
    
    Args:
        new_database_name (str): Nome do novo banco de dados
    """
    # Carregar variáveis de ambiente atuais
    load_dotenv()
    
    # Ler o arquivo .env
    with open('.env', 'r') as file:
        env_content = file.read()
    
    # Substituir o nome do banco de dados
    old_db_line = f"DB_DATABASE=bdMaterialEscolar"
    new_db_line = f"DB_DATABASE={new_database_name}"
    updated_content = env_content.replace(old_db_line, new_db_line)
    
    # Atualizar a string de conexão completa
    old_conn_string = "SQL_CONNECTION_STRING=DRIVER={ODBC Driver 17 for SQL Server};SERVER=boizito.database.windows.net;PORT=1433;DATABASE=bdMaterialEscolar;"
    new_conn_string = f"SQL_CONNECTION_STRING=DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=boizito.database.windows.net;PORT=1433;DATABASE={new_database_name};"
    updated_content = updated_content.replace(old_conn_string, new_conn_string)
    
    # Salvar o arquivo .env atualizado
    with open('.env', 'w') as file:
        file.write(updated_content)
    
    print(f"Arquivo .env atualizado com sucesso. Banco de dados alterado para: {new_database_name}")

if __name__ == "__main__":
    # Solicitar o nome do novo banco de dados
    new_db_name = input("Digite o nome do novo banco de dados: ")
    
    if new_db_name.strip():
        update_env_file(new_db_name)
    else:
        print("Nome do banco de dados inválido. Nenhuma alteração foi feita.")