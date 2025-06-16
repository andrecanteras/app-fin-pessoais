import os
import pyodbc
import time
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
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Tentar usar a string de conexão completa se disponível
                    conn_str_full = self.env_values.get('SQL_CONNECTION_STRING') or os.getenv('SQL_CONNECTION_STRING')
                    
                    if conn_str_full:
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
                        
                        # Adicionar parâmetros de timeout e conexão
                        connection_string = (
                            f'DRIVER={driver};SERVER={server};PORT={port};DATABASE={database};'
                            f'UID={username};PWD={password};'
                            f'Connection Timeout=30;Connection Retry Count=3;'
                        )
                    
                    self._connection = pyodbc.connect(connection_string)
                    print(f"Conexão com o banco de dados estabelecida com sucesso. Usando esquema: {self.schema}")
                    
                    # Criar o esquema se não existir
                    self._ensure_schema_exists()
                    
                    # Conexão bem-sucedida, sair do loop
                    break
                    
                except pyodbc.Error as e:
                    retry_count += 1
                    print(f"Erro ao conectar ao banco de dados (tentativa {retry_count}/{max_retries}): {e}")
                    
                    if retry_count >= max_retries:
                        print("Número máximo de tentativas excedido.")
                        raise
                    
                    # Esperar antes de tentar novamente (backoff exponencial)
                    wait_time = 2 ** retry_count  # 2, 4, 8 segundos...
                    print(f"Aguardando {wait_time} segundos antes de tentar novamente...")
                    time.sleep(wait_time)
                    
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
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Configurar timeout para consultas
            cursor.execute("SET QUERY_GOVERNOR_COST_LIMIT 0")  # Desativar limite de custo
            cursor.execute("SET LOCK_TIMEOUT 30000")  # 30 segundos de timeout para locks
            
            return cursor
        except pyodbc.Error as e:
            print(f"Erro ao obter cursor: {e}")
            # Tentar reconectar
            self._connection = None
            connection = self.connect()
            return connection.cursor()
    
    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self._connection:
            try:
                self._connection.commit()
            except pyodbc.Error as e:
                print(f"Aviso: Não foi possível fazer commit na conexão: {e}")
                try:
                    self._connection.rollback()
                except:
                    pass
            # Não fechamos a conexão para reutilizá-la (pool de conexões)
            # self._connection.close()
            # self._connection = None
    
    def commit(self):
        """Confirma as alterações no banco de dados."""
        if self._connection:
            try:
                self._connection.commit()
            except pyodbc.Error as e:
                print(f"Erro ao fazer commit: {e}")
                try:
                    self._connection.rollback()
                except:
                    pass
                # Reconectar se a conexão foi perdida
                self._reconnect()
                raise
    
    def rollback(self):
        """Desfaz as alterações no banco de dados."""
        if self._connection:
            try:
                self._connection.rollback()
            except pyodbc.Error as e:
                print(f"Erro ao fazer rollback: {e}")
                # Reconectar se a conexão foi perdida
                self._reconnect()
                
    def _reconnect(self):
        """Tenta reconectar ao banco de dados após uma falha."""
        try:
            print("Tentando reconectar ao banco de dados...")
            self._connection = None
            self.connect()
            print("Reconexão bem-sucedida!")
        except Exception as e:
            print(f"Falha ao reconectar: {e}")
            self._connection = None
    
    def execute_query(self, query, params=None):
        """Executa uma consulta SQL."""
        cursor = self.get_cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor