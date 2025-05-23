import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import Qt
from dotenv import load_dotenv

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
        from src.database.setup import DatabaseSetup
        db_setup = DatabaseSetup()
        db_setup.create_tables()
        print("Banco de dados configurado com sucesso.")
    except Exception as e:
        print(f"Erro ao configurar o banco de dados: {e}")
        print("Continuando mesmo com erro, pois o usuário pode configurar depois")
    
    # Criar uma janela simples para teste
    window = QMainWindow()
    window.setWindowTitle("Finanças Pessoais - Teste")
    window.setMinimumSize(800, 600)
    
    # Widget central e layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Adicionar título
    title_label = QLabel("Aplicativo de Finanças Pessoais")
    title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
    title_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(title_label)
    
    # Adicionar mensagem
    message_label = QLabel("Aplicativo em manutenção. Estamos migrando para PyQt5.")
    message_label.setStyleSheet("font-size: 16px;")
    message_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(message_label)
    
    # Adicionar botão de teste
    test_button = QPushButton("Testar Conexão")
    test_button.setStyleSheet("font-size: 14px; padding: 10px;")
    test_button.clicked.connect(lambda: message_label.setText("Teste de conexão realizado com sucesso!"))
    layout.addWidget(test_button)
    
    # Mostrar a janela
    window.show()
    print("Janela de teste criada com sucesso!")
    
    # Executar o loop de eventos
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()