import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTabWidget, QMessageBox, QStatusBar, QAction
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from src.views.dashboard_view_pyqt5 import DashboardView
from src.views.accounts_view import AccountsView
from src.models.conta import Conta

class MainWindow(QMainWindow):
    """Janela principal do aplicativo de finanças pessoais."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Finanças Pessoais")
        self.setMinimumSize(1000, 600)
        
        # Configurar a barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Bem-vindo ao Gerenciador de Finanças Pessoais")
        
        # Configurar o menu
        self.setup_menu()
        
        # Configurar o widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Adicionar o cabeçalho
        self.setup_header()
        
        # Adicionar as abas
        self.setup_tabs()
        
        # Adicionar o rodapé
        self.setup_footer()
        
        # Atualizar o saldo total
        self.update_balance()
    
    def setup_menu(self):
        """Configura a barra de menu."""
        menu_bar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menu_bar.addMenu("&Arquivo")
        
        # Ação para importar do Notion
        import_notion_action = QAction("Importar do &Notion", self)
        import_notion_action.setStatusTip("Importar transações do Notion")
        import_notion_action.triggered.connect(self.import_from_notion)
        file_menu.addAction(import_notion_action)
        
        # Separador
        file_menu.addSeparator()
        
        # Ação para sair
        exit_action = QAction("&Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Sair do aplicativo")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Relatórios
        reports_menu = menu_bar.addMenu("&Relatórios")
        
        # Ação para relatório de fluxo de caixa
        cash_flow_action = QAction("Fluxo de &Caixa", self)
        cash_flow_action.setStatusTip("Gerar relatório de fluxo de caixa")
        cash_flow_action.triggered.connect(self.show_cash_flow_report)
        reports_menu.addAction(cash_flow_action)
        
        # Ação para relatório por categoria
        category_report_action = QAction("Gastos por &Categoria", self)
        category_report_action.setStatusTip("Gerar relatório de gastos por categoria")
        category_report_action.triggered.connect(self.show_category_report)
        reports_menu.addAction(category_report_action)
        
        # Menu Ajuda
        help_menu = menu_bar.addMenu("A&juda")
        
        # Ação para sobre
        about_action = QAction("&Sobre", self)
        about_action.setStatusTip("Sobre o aplicativo")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_header(self):
        """Configura o cabeçalho da aplicação."""
        header_layout = QHBoxLayout()
        
        # Título
        title_label = QLabel("Gerenciador de Finanças Pessoais")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Espaçador
        header_layout.addStretch()
        
        # Resumo financeiro
        self.balance_label = QLabel("Saldo Total: R$ 0,00")
        self.balance_label.setStyleSheet("font-size: 16px;")
        header_layout.addWidget(self.balance_label)
        
        self.main_layout.addLayout(header_layout)
    
    def setup_tabs(self):
        """Configura as abas da aplicação."""
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Aba de Dashboard
        self.dashboard_tab = DashboardView()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        
        # Aba de Transações (será implementada posteriormente)
        self.transactions_tab = QWidget()
        self.tabs.addTab(self.transactions_tab, "Transações")
        
        # Aba de Contas
        self.accounts_tab = AccountsView()
        self.tabs.addTab(self.accounts_tab, "Contas")
        
        # Aba de Categorias (será implementada posteriormente)
        self.categories_tab = QWidget()
        self.tabs.addTab(self.categories_tab, "Categorias")
        
        # Aba de Relatórios (será implementada posteriormente)
        self.reports_tab = QWidget()
        self.tabs.addTab(self.reports_tab, "Relatórios")
        
        self.main_layout.addWidget(self.tabs)
    
    def setup_footer(self):
        """Configura o rodapé da aplicação."""
        footer_layout = QHBoxLayout()
        
        # Informações do aplicativo
        app_info_label = QLabel("Finanças Pessoais v1.0")
        footer_layout.addWidget(app_info_label)
        
        # Espaçador
        footer_layout.addStretch()
        
        # Botão de ajuda
        help_button = QPushButton("Ajuda")
        help_button.clicked.connect(self.show_help)
        footer_layout.addWidget(help_button)
        
        self.main_layout.addLayout(footer_layout)
    
    def update_balance(self):
        """Atualiza o saldo total exibido no cabeçalho."""
        saldo_total = Conta.obter_saldo_total()
        self.balance_label.setText(f"Saldo Total: R$ {saldo_total:.2f}")
    
    def on_tab_changed(self, index):
        """Chamado quando o usuário muda de aba."""
        # Atualizar o saldo total quando mudar para a aba de Dashboard ou Contas
        if index == 0 or index == 2:  # Dashboard ou Contas
            self.update_balance()
            
            # Se for a aba de Dashboard, atualizar os dados
            if index == 0 and hasattr(self.dashboard_tab, 'load_data'):
                self.dashboard_tab.load_data()
            
            # Se for a aba de Contas, atualizar os dados
            if index == 2:
                self.accounts_tab.load_data()
    
    def import_from_notion(self):
        """Importa transações do Notion."""
        QMessageBox.information(
            self,
            "Importar do Notion",
            "Funcionalidade de importação do Notion será implementada em breve."
        )
    
    def show_cash_flow_report(self):
        """Mostra o relatório de fluxo de caixa."""
        QMessageBox.information(
            self,
            "Relatório de Fluxo de Caixa",
            "Funcionalidade de relatório de fluxo de caixa será implementada em breve."
        )
    
    def show_category_report(self):
        """Mostra o relatório por categoria."""
        QMessageBox.information(
            self,
            "Relatório por Categoria",
            "Funcionalidade de relatório por categoria será implementada em breve."
        )
    
    def show_about(self):
        """Mostra informações sobre o aplicativo."""
        QMessageBox.about(
            self,
            "Sobre",
            "Gerenciador de Finanças Pessoais v1.0\n\n"
            "Um aplicativo para controle de finanças pessoais com integração ao SQL Server na Azure e Notion."
        )
    
    def show_help(self):
        """Mostra a ajuda do aplicativo."""
        QMessageBox.information(
            self,
            "Ajuda",
            "Para obter ajuda sobre como usar o aplicativo, consulte a documentação."
        )