import sys
import os
from PyQt5.QtWidgets import QApplication
from dotenv import load_dotenv
from src.views.main_window import MainWindow
from src.database.setup import DatabaseSetup

def main():
    """Função principal para iniciar o aplicativo."""
    print("Iniciando aplicativo com PyQt5...")
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Verificar se o arquivo .env existe
    if not os.path.exists('.env'):
        print("Arquivo .env não encontrado. Crie-o a partir do .env.example")
        print("Copiando .env.example para .env...")
        try:
            with open('.env.example', 'r') as example_file:
                with open('.env', 'w') as env_file:
                    env_file.write(example_file.read())
            print("Arquivo .env criado. Por favor, configure suas credenciais.")
        except Exception as e:
            print(f"Erro ao criar arquivo .env: {e}")
    
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