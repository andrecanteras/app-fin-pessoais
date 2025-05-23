import os
import sys
import pyodbc
from dotenv import load_dotenv, dotenv_values
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget, QTextEdit, QMessageBox

class DatabaseConnectionTester(QMainWindow):
    """Janela para testar a conexão com o banco de dados."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Teste de Conexão com Banco de Dados")
        self.setMinimumSize(600, 400)
        
        # Widget central e layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Adicionar título
        title_label = QLabel("Teste de Conexão com Banco de Dados")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Área de log
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        
        # Botão de teste
        test_button = QPushButton("Testar Conexão")
        test_button.setStyleSheet("font-size: 14px; padding: 10px;")
        test_button.clicked.connect(self.test_connection)
        layout.addWidget(test_button)
        
        # Carregar variáveis de ambiente
        load_dotenv(override=True)
        self.log("Variáveis de ambiente carregadas.")
        
        # Carregar diretamente do arquivo para garantir
        self.env_values = dotenv_values(".env")
        
        # Verificar se as variáveis necessárias estão definidas
        self.check_env_vars()
    
    def log(self, message):
        """Adiciona uma mensagem à área de log."""
        self.log_area.append(message)
    
    def check_env_vars(self):
        """Verifica se as variáveis de ambiente necessárias estão definidas."""
        required_vars = ['DB_SERVER', 'DB_DATABASE', 'DB_USERNAME', 'DB_PASSWORD']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var) and var not in self.env_values:
                missing_vars.append(var)
        
        if missing_vars:
            self.log("AVISO: As seguintes variáveis de ambiente estão faltando:")
            for var in missing_vars:
                self.log(f"- {var}")
            self.log("Por favor, configure o arquivo .env com as credenciais do banco de dados.")
        else:
            self.log("Todas as variáveis de ambiente necessárias estão definidas.")
            
            # Mostrar valores das variáveis (ocultando a senha)
            self.log("\nValores das variáveis de ambiente:")
            
            # Preferir valores do arquivo diretamente
            server = self.env_values.get('DB_SERVER') or os.getenv('DB_SERVER')
            database = self.env_values.get('DB_DATABASE') or os.getenv('DB_DATABASE')
            username = self.env_values.get('DB_USERNAME') or os.getenv('DB_USERNAME')
            password = self.env_values.get('DB_PASSWORD') or os.getenv('DB_PASSWORD')
            driver = self.env_values.get('DB_DRIVER') or os.getenv('DB_DRIVER')
            
            self.log(f"DB_SERVER: {server}")
            self.log(f"DB_DATABASE: {database}")
            self.log(f"DB_USERNAME: {username}")
            self.log(f"DB_PASSWORD: {'*' * len(password or '')}")
            self.log(f"DB_DRIVER: {driver}")
    
    def test_connection(self):
        """Testa a conexão com o banco de dados."""
        self.log("\n--- Iniciando teste de conexão ---")
        
        # Preferir valores do arquivo diretamente
        server = self.env_values.get('DB_SERVER') or os.getenv('DB_SERVER')
        port = self.env_values.get('DB_PORT') or os.getenv('DB_PORT', '1433')
        database = self.env_values.get('DB_DATABASE') or os.getenv('DB_DATABASE')
        username = self.env_values.get('DB_USERNAME') or os.getenv('DB_USERNAME')
        password = self.env_values.get('DB_PASSWORD') or os.getenv('DB_PASSWORD')
        driver = self.env_values.get('DB_DRIVER') or os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        conn_str_full = self.env_values.get('SQL_CONNECTION_STRING') or os.getenv('SQL_CONNECTION_STRING')
        
        # Verificar se todas as variáveis estão definidas
        if not all([server, database, username, password]):
            self.log("Erro: Algumas variáveis de ambiente estão faltando.")
            self.log("Por favor, configure o arquivo .env com as credenciais do banco de dados.")
            return
        
        # Construir string de conexão
        if conn_str_full:
            self.log("Usando string de conexão completa do arquivo .env")
            conn_str = conn_str_full
            self.log(f"String de conexão: {conn_str.replace(password or '', '*****')}")
        else:
            # Tratar o driver corretamente
            if not driver.startswith('{'):
                driver = '{' + driver + '}'
            
            conn_str = f'DRIVER={driver};SERVER={server};PORT={port};DATABASE={database};UID={username};PWD={password}'
            self.log(f"String de conexão construída a partir de variáveis individuais:")
            self.log(f"DRIVER={driver};SERVER={server};PORT={port};DATABASE={database};UID={username};PWD={'*****'}")
        
        try:
            # Tentar conectar ao banco de dados
            self.log("Tentando conectar ao banco de dados...")
            conn = pyodbc.connect(conn_str)
            self.log("Conexão estabelecida com sucesso!")
            
            # Testar uma consulta simples
            self.log("Executando consulta de teste...")
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            row = cursor.fetchone()
            self.log(f"Versão do SQL Server: {row[0]}")
            
            # Verificar tabelas existentes
            self.log("\nTabelas existentes no banco de dados:")
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            tables = cursor.fetchall()
            if tables:
                for table in tables:
                    self.log(f"- {table[0]}")
            else:
                self.log("Nenhuma tabela encontrada no banco de dados.")
            
            # Fechar conexão
            conn.close()
            self.log("\nConexão fechada.")
            
            # Mostrar mensagem de sucesso
            QMessageBox.information(
                self,
                "Teste de Conexão",
                "Conexão com o banco de dados estabelecida com sucesso!"
            )
            
        except Exception as e:
            self.log(f"Erro ao conectar ao banco de dados: {e}")
            
            # Mostrar mensagem de erro
            QMessageBox.critical(
                self,
                "Erro de Conexão",
                f"Não foi possível conectar ao banco de dados.\n\nErro: {e}"
            )
        
        self.log("--- Teste de conexão concluído ---")

def main():
    """Função principal para iniciar o aplicativo de teste."""
    app = QApplication(sys.argv)
    window = DatabaseConnectionTester()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()