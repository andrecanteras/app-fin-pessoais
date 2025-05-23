import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget

def main():
    """Aplicativo simples para testar o PyQt5."""
    app = QApplication(sys.argv)
    
    # Criar janela principal
    window = QMainWindow()
    window.setWindowTitle("Teste PyQt5")
    window.setGeometry(100, 100, 400, 200)
    
    # Widget central e layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Adicionar label
    label = QLabel("PyQt5 está funcionando!")
    label.setStyleSheet("font-size: 16px; font-weight: bold;")
    layout.addWidget(label)
    
    # Adicionar botão
    button = QPushButton("Clique Aqui")
    button.clicked.connect(lambda: label.setText("Botão clicado!"))
    layout.addWidget(button)
    
    # Mostrar janela
    window.show()
    
    # Executar loop de eventos
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()