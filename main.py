import sys
import os
from PyQt5.QtWidgets import QApplication
from dotenv import load_dotenv
from src.views.main_window import MainWindow
from src.database.setup import DatabaseSetup

def load_env():
    """Carrega variáveis de ambiente considerando se está em desenvolvimento ou executável."""
    if getattr(sys, 'frozen', False):
        # Executando como executável
        base_path = sys._MEIPASS
    else:
        # Executando em desenvolvimento
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    env_path = os.path.join(base_path, '.env')
    load_dotenv(env_path)

def main():
    """Função principal para iniciar o aplicativo."""
    print("Iniciando aplicativo...")
    
    # Carregar variáveis de ambiente
    load_env()
    
    # Iniciar a aplicação Qt
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo consistente em diferentes plataformas
    
    # Configurar o banco de dados
    try:
        db_setup = DatabaseSetup()
        db_setup.create_tables()
        print("Banco de dados configurado com sucesso.")
    except Exception as e:
        print(f"Erro ao configurar o banco de dados: {e}")
        print("Continuando mesmo com erro, pois o usuário pode configurar depois")
    
    # Criar e mostrar a janela principal
    window = MainWindow()
    window.show()
    
    # Executar o loop de eventos
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()