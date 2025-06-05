import os
import pyodbc
from dotenv import load_dotenv, dotenv_values

class DatabaseConnection:
    """Classe para gerenciar a conexão com o banco de dados SQL Server na Azure."""
    
    _instances = {}  # Dicionário para armazenar instâncias por ambiente
    
    def __new__(cls, environment=None):
        """Implementação do padrão Singleton por ambiente."""
        environment = environment or os.getenv('ENVIRONMENT', 'prod')
        
        # Criar uma instância separada para cada ambiente
        if environment not in cls._instances:
            instance = super(DatabaseConnection, cls).__new__(cls)
            instance._connection = None
            instance.environment = environment
            instance.schema = f"financas_pessoais{'_dev' if environment == 'dev' else ''}"
            
            # Carregar variáveis de ambiente
            load_dotenv(override=True)
            
            # Carregar diretamente do arquivo para garantir
            instance.env_values = dotenv_values(".env")
            
            cls._instances[environment] = instance
            
        return cls._instances[environment]
    
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
                print(f"Conexão com o banco de dados estabelecida com sucesso. Usando esquema: {self.schema}")
                
                # Criar o esquema se não existir
                self._ensure_schema_exists()
                
            except pyodbc.Error as e:
                print(f"Erro ao conectar ao banco de dados: {e}")
                raise
        return self._connection
    
    def _ensure_schema_exists(self):
        """Garante que o esquema exista."""
        try:
            cursor = self._connection.cursor()
            cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{self.schema}')
            BEGIN
                EXEC('CREATE SCHEMA {self.schema}')
            END
            """)
            self._connection.commit()
        except Exception as e:
            print(f"Aviso: Não foi possível verificar/criar o esquema: {e}")
    
    def get_cursor(self):
        """Retorna um cursor para executar consultas SQL."""
        connection = self.connect()
        return connection.cursor()
    
    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self._connection:
            self._connection.commit()
            ##NAO FECHAR CONEXAO
            # self._connection.close()
            # self._connection = None
            # print("Conexão com o banco de dados fechada.")
    
    def commit(self):
        """Confirma as alterações no banco de dados."""
        if self._connection:
            self._connection.commit()
    
    def rollback(self):
        """Desfaz as alterações no banco de dados."""
        if self._connection:
            self._connection.rollback()
    
    def execute_query(self, query, params=None):
        """Executa uma consulta SQL."""
        cursor = self.get_cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor