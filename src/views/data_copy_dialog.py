"""
Diálogo para copiar dados entre ambientes.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTextEdit, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread
from src.utils.data_copy import DataCopyUtil

class DataCopyWorker(QThread):
    """Thread para executar a cópia de dados em segundo plano."""
    
    def __init__(self, data_copy_util):
        super().__init__()
        self.data_copy_util = data_copy_util
    
    def run(self):
        """Executa a cópia de dados."""
        self.data_copy_util.copy_data_from_prod_to_dev()

class DataCopyDialog(QDialog):
    """Diálogo para copiar dados entre ambientes."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Copiar Dados de PROD para DEV")
        self.setMinimumSize(600, 400)
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QVBoxLayout(self)
        
        # Área de informações
        info_label = QLabel(
            "Esta operação copiará todos os dados do ambiente de produção para o ambiente de desenvolvimento.\n"
            "Isso substituirá todos os dados existentes no ambiente de desenvolvimento.\n\n"
            "Deseja continuar?"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Área de log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminado
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("Iniciar Cópia")
        self.btn_start.clicked.connect(self.start_copy)
        btn_layout.addWidget(self.btn_start)
        
        self.btn_close = QPushButton("Fechar")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # Utilitário de cópia
        self.data_copy_util = DataCopyUtil()
        self.data_copy_util.progress_updated.connect(self.update_progress)
        self.data_copy_util.operation_completed.connect(self.operation_completed)
        
        # Thread de trabalho
        self.worker = None
    
    def start_copy(self):
        """Inicia o processo de cópia de dados."""
        # Confirmar a operação
        reply = QMessageBox.question(
            self, 
            "Confirmar Operação", 
            "Esta operação substituirá todos os dados no ambiente de desenvolvimento. Continuar?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Limpar log
        self.log_text.clear()
        
        # Desabilitar botão de início
        self.btn_start.setEnabled(False)
        
        # Mostrar barra de progresso
        self.progress_bar.setVisible(True)
        
        # Iniciar thread de trabalho
        self.worker = DataCopyWorker(self.data_copy_util)
        self.worker.start()
    
    def update_progress(self, message):
        """Atualiza o log de progresso."""
        self.log_text.append(message)
        # Rolar para o final
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def operation_completed(self, success, message):
        """Chamado quando a operação é concluída."""
        # Esconder barra de progresso
        self.progress_bar.setVisible(False)
        
        # Habilitar botão de início
        self.btn_start.setEnabled(True)
        
        # Mostrar mensagem de conclusão
        if success:
            QMessageBox.information(self, "Sucesso", message)
        else:
            QMessageBox.critical(self, "Erro", message)