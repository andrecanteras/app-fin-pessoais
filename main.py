import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from dotenv import load_dotenv
from src.views.main_window import MainWindow
from src.database.setup import DatabaseSetup

def select_environment():
    """Permite ao usuário selecionar o ambiente."""
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    
    reply = QMessageBox.question(None, 'Ambiente', 
                               'Usar ambiente de desenvolvimento?',
                               QMessageBox.Yes | QMessageBox.No)
    return 'dev' if reply == QMessageBox.Yes else 'prod'

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

def get_icon_path():
    """Retorna o caminho do ícone considerando se está em desenvolvimento ou executável."""
    if getattr(sys, 'frozen', False):
        # Executando como executável
        base_path = sys._MEIPASS
    else:
        # Executando em desenvolvimento
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Procurar por arquivos de ícone
    icon_files = ['icon.ico', 'icon.png', 'app.ico', 'app.png']
    
    for icon_file in icon_files:
        icon_path = os.path.join(base_path, 'assets', icon_file)
        if os.path.exists(icon_path):
            return icon_path
    
    return None

def main():
    """Função principal para iniciar o aplicativo."""
    print("Iniciando aplicativo...")
    
    # Selecionar ambiente
    environment = select_environment()
    os.environ['ENVIRONMENT'] = environment
    print(f"Usando ambiente: {environment}")
    
    # Carregar variáveis de ambiente
    load_env()
    
    # Iniciar a aplicação Qt
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo consistente em diferentes plataformas
    
    # Configurar ícone da aplicação
    icon_path = get_icon_path()
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))
        print(f"Ícone carregado: {icon_path}")
    else:
        print("Nenhum ícone encontrado na pasta assets/")
    
    # Configurar o banco de dados
    try:
        db_setup = DatabaseSetup(environment=environment)
        db_setup.create_tables()
        print("Banco de dados configurado com sucesso.")
    except Exception as e:
        print(f"Erro ao configurar o banco de dados: {e}")
        print("Continuando mesmo com erro, pois o usuário pode configurar depois")
    
    # Criar e mostrar a janela principal
    window = MainWindow(environment=environment)
    window.show()
    
    # Executar o loop de eventos
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()