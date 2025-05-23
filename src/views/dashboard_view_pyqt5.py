from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QPushButton, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta
from src.models.conta import Conta
from src.models.transacao import Transacao

class DashboardView(QWidget):
    """Widget para exibir o dashboard com resumo financeiro."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Configura a interface do dashboard."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("Dashboard")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        main_layout.addWidget(title_label)
        
        # Grid para os cards
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        # Card de saldo total
        self.balance_card = self._create_card("Saldo Total", "R$ 0,00")
        grid_layout.addWidget(self.balance_card, 0, 0)
        
        # Card de receitas do mês
        self.income_card = self._create_card("Receitas do Mês", "R$ 0,00")
        grid_layout.addWidget(self.income_card, 0, 1)
        
        # Card de despesas do mês
        self.expense_card = self._create_card("Despesas do Mês", "R$ 0,00")
        grid_layout.addWidget(self.expense_card, 0, 2)
        
        # Card de saldo do mês
        self.month_balance_card = self._create_card("Saldo do Mês", "R$ 0,00")
        grid_layout.addWidget(self.month_balance_card, 1, 0)
        
        # Card de transações recentes
        self.recent_transactions_card = self._create_card("Transações Recentes", "Carregando...")
        grid_layout.addWidget(self.recent_transactions_card, 1, 1, 1, 2)
        
        main_layout.addLayout(grid_layout)
        
        # Botões de ação rápida
        action_layout = QHBoxLayout()
        
        # Botão para adicionar receita
        add_income_btn = QPushButton("+ Receita")
        add_income_btn.clicked.connect(self.add_income)
        action_layout.addWidget(add_income_btn)
        
        # Botão para adicionar despesa
        add_expense_btn = QPushButton("+ Despesa")
        add_expense_btn.clicked.connect(self.add_expense)
        action_layout.addWidget(add_expense_btn)
        
        # Botão para ver relatórios
        view_reports_btn = QPushButton("Ver Relatórios")
        view_reports_btn.clicked.connect(self.view_reports)
        action_layout.addWidget(view_reports_btn)
        
        main_layout.addLayout(action_layout)
        
        # Espaçador
        main_layout.addStretch()
    
    def _create_card(self, title, content):
        """Cria um card para o dashboard."""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setFrameShadow(QFrame.Raised)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Título do card
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Conteúdo do card
        content_label = QLabel(content)
        content_label.setFont(QFont("Arial", 14))
        content_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(content_label)
        
        # Armazenar o label de conteúdo para atualização posterior
        card.content_label = content_label
        
        return card
    
    def load_data(self):
        """Carrega os dados para o dashboard."""
        try:
            # Obter saldo total
            saldo_total = Conta.obter_saldo_total()
            self.balance_card.content_label.setText(f"R$ {saldo_total:,.2f}")
            
            # Obter datas do mês atual
            hoje = datetime.now().date()
            primeiro_dia_mes = hoje.replace(day=1)
            if hoje.month == 12:
                ultimo_dia_mes = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                ultimo_dia_mes = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
            
            # Obter resumo do mês
            resumo = Transacao.obter_resumo_por_periodo(primeiro_dia_mes, ultimo_dia_mes)
            
            # Atualizar cards
            self.income_card.content_label.setText(f"R$ {resumo['total_receitas']:,.2f}")
            self.expense_card.content_label.setText(f"R$ {resumo['total_despesas']:,.2f}")
            self.month_balance_card.content_label.setText(f"R$ {resumo['saldo_periodo']:,.2f}")
            
            # Obter transações recentes
            filtros = {
                'limite': 5,
                'ordenacao': 'data_transacao DESC'
            }
            transacoes_recentes = Transacao.listar_todas(filtros)
            
            if transacoes_recentes:
                # Formatar texto de transações recentes
                texto_transacoes = ""
                for t in transacoes_recentes:
                    tipo = "+" if t.tipo == 'R' else "-"
                    texto_transacoes += f"{t.data_transacao.strftime('%d/%m/%Y')} - {t.descricao}: {tipo}R$ {t.valor:,.2f}\n"
                
                self.recent_transactions_card.content_label.setText(texto_transacoes)
            else:
                self.recent_transactions_card.content_label.setText("Nenhuma transação recente.")
                
        except Exception as e:
            print(f"Erro ao carregar dados do dashboard: {e}")
            self.recent_transactions_card.content_label.setText(f"Erro ao carregar dados: {str(e)}")
    
    def add_income(self):
        """Abre o formulário para adicionar receita."""
        # Esta função será implementada posteriormente
        print("Adicionar receita")
    
    def add_expense(self):
        """Abre o formulário para adicionar despesa."""
        # Esta função será implementada posteriormente
        print("Adicionar despesa")
    
    def view_reports(self):
        """Abre a tela de relatórios."""
        # Esta função será implementada posteriormente
        print("Ver relatórios")