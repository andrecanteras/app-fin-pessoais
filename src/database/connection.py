import os
import pyodbc
from dotenv import load_dotenv, dotenv_values

class DatabaseConnection:
    """Classe para gerenciar a conexão com o banco de dados SQL Server na Azure."""
    
    _instance = None
    
    def __new__(cls):
        """Implementação do padrão Singleton para garantir uma única conexão."""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._connection = None
            
            # Carregar variáveis de ambiente
            load_dotenv(override=True)
            
            # Carregar diretamente do arquivo para garantir
            cls._instance.env_values = dotenv_values(".env")
        return cls._instance
    
    def connect(self):
        """Estabelece uma conexão com o banco de dados."""
        if self._connection is None:
            try:
                # Tentar usar a string de conexão completa se disponível
                conn_str_full = self.env_values.get('SQL_CONNECTION_STRING') or os.getenv('SQL_CONNECTION_STRING')
                
                if conn_str_full:
                    # print("Usando string de conexão completa do arquivo .env")
                    connection_string = conn_str_full
                else:
                    # Preferir valores do arquivo diretamente
                    server = self.env_values.get('DB_SERVER') or os.getenv('DB_SERVER')
                    port = self.env_values.get('DB_PORT') or os.getenv('DB_PORT', '1433')
                    database = self.env_values.get('DB_DATABASE') or os.getenv('DB_DATABASE')
                    username = self.env_values.get('DB_USERNAME') or os.getenv('DB_USERNAME')
                    password = self.env_values.get('DB_PASSWORD') or os.getenv('DB_PASSWORD')
                    driver = self.env_values.get('DB_DRIVER') or os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
                    
                    # Tratar o driver corretamente
                    if not driver.startswith('{'):
                        driver = '{' + driver + '}'
                    
                    connection_string = f'DRIVER={driver};SERVER={server};PORT={port};DATABASE={database};UID={username};PWD={password}'
                    # print("Usando string de conexão construída a partir de variáveis individuais")
                
                self._connection = pyodbc.connect(connection_string)
                # print("Conexão com o banco de dados estabelecida com sucesso.")
            except pyodbc.Error as e:
                print(f"Erro ao conectar ao banco de dados: {e}")
                raise
        return self._connection
    
    def get_cursor(self):
        """Retorna um cursor para executar consultas SQL."""
        connection = self.connect()
        return connection.cursor()
    
    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self._connection:
            self._connection.close()
            self._connection = None
            # print("Conexão com o banco de dados fechada.")
    
    def commit(self):
        """Confirma as alterações no banco de dados."""
        if self._connection:
            self._connection.commit()
    
    def rollback(self):
        """Desfaz as alterações no banco de dados."""
        if self._connection:
            self._connection.rollback()