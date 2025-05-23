"""
Interface gráfica para gestão de contas bancárias.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                            QMessageBox, QDialog, QFormLayout, QComboBox, 
                            QDialogButtonBox, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDoubleValidator
from decimal import Decimal
from src.models.conta import Conta

class ContaDialog(QDialog):
    """Diálogo para criar ou editar uma conta."""
    
    def __init__(self, parent=None, conta=None):
        super().__init__(parent)
        self.conta = conta
        self.setWindowTitle("Nova Conta" if conta is None else "Editar Conta")
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QFormLayout(self)
        
        # Campos do formulário
        self.nome_edit = QLineEdit(self)
        if self.conta:
            self.nome_edit.setText(self.conta.nome)
        
        self.tipo_combo = QComboBox(self)
        self.tipo_combo.addItems(["Corrente", "Poupança", "Investimento", "Carteira", "Outro"])
        if self.conta:
            index = self.tipo_combo.findText(self.conta.tipo)
            if index >= 0:
                self.tipo_combo.setCurrentIndex(index)
        
        self.instituicao_edit = QLineEdit(self)
        if self.conta and self.conta.banco:
            self.instituicao_edit.setText(self.conta.banco)
        
        self.agencia_edit = QLineEdit(self)
        if self.conta and self.conta.agencia:
            self.agencia_edit.setText(self.conta.agencia)
        
        self.conta_contabil_edit = QLineEdit(self)
        if self.conta and self.conta.conta_contabil:
            self.conta_contabil_edit.setText(self.conta.conta_contabil)
        
        self.numero_banco_edit = QLineEdit(self)
        if self.conta and self.conta.numero_banco:
            self.numero_banco_edit.setText(self.conta.numero_banco)
        
        self.titular_edit = QLineEdit(self)
        if self.conta and self.conta.titular:
            self.titular_edit.setText(self.conta.titular)
        
        self.nome_gerente_edit = QLineEdit(self)
        if self.conta and self.conta.nome_gerente:
            self.nome_gerente_edit.setText(self.conta.nome_gerente)
        
        self.contato_gerente_edit = QLineEdit(self)
        if self.conta and self.conta.contato_gerente:
            self.contato_gerente_edit.setText(self.conta.contato_gerente)
        
        self.saldo_inicial_edit = QLineEdit(self)
        self.saldo_inicial_edit.setValidator(QDoubleValidator(0, 1000000, 2))
        if self.conta:
            self.saldo_inicial_edit.setText(str(self.conta.saldo_inicial))
            # Desabilitar edição do saldo inicial se a conta já existe
            self.saldo_inicial_edit.setEnabled(False)
        else:
            self.saldo_inicial_edit.setText("0.00")
        
        # Adicionar campos ao layout
        layout.addRow("Nome:", self.nome_edit)
        layout.addRow("Tipo:", self.tipo_combo)
        layout.addRow("Instituição:", self.instituicao_edit)
        layout.addRow("Agência:", self.agencia_edit)
        layout.addRow("Conta Contábil:", self.conta_contabil_edit)
        layout.addRow("Número do Banco:", self.numero_banco_edit)
        layout.addRow("Titular:", self.titular_edit)
        layout.addRow("Nome do Gerente:", self.nome_gerente_edit)
        layout.addRow("Contato do Gerente:", self.contato_gerente_edit)
        layout.addRow("Saldo Inicial (R$):", self.saldo_inicial_edit)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
        
    def get_conta_data(self):
        """Retorna os dados da conta do formulário."""
        nome = self.nome_edit.text().strip()
        tipo = self.tipo_combo.currentText()
        instituicao = self.instituicao_edit.text().strip() or None
        agencia = self.agencia_edit.text().strip() or None
        conta_contabil = self.conta_contabil_edit.text().strip() or None
        numero_banco = self.numero_banco_edit.text().strip() or None
        titular = self.titular_edit.text().strip() or None
        nome_gerente = self.nome_gerente_edit.text().strip() or None
        contato_gerente = self.contato_gerente_edit.text().strip() or None
        
        try:
            saldo_inicial = Decimal(self.saldo_inicial_edit.text())
        except:
            saldo_inicial = Decimal('0')
            
        return {
            'nome': nome,
            'tipo': tipo,
            'banco': instituicao,
            'agencia': agencia,
            'conta_contabil': conta_contabil,
            'numero_banco': numero_banco,
            'titular': titular,
            'nome_gerente': nome_gerente,
            'contato_gerente': contato_gerente,
            'saldo_inicial': saldo_inicial
        }

class AccountsView(QWidget):
    """Widget para gestão de contas bancárias."""
    
    # Sinal emitido quando o saldo total é atualizado
    saldo_atualizado = pyqtSignal(Decimal)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestão de Contas")
        self.setup_ui()
        self.carregar_contas()
        
    def setup_ui(self):
        """Configura a interface do widget."""
        layout = QVBoxLayout(self)
        
        # Área de informações
        info_layout = QHBoxLayout()
        self.total_label = QLabel("Saldo Total: R$ 0,00")
        info_layout.addWidget(self.total_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # Tabela de contas
        self.tabela_contas = QTableWidget(0, 10)  # 10 colunas para mostrar todos os campos
        self.tabela_contas.setHorizontalHeaderLabels([
            "ID", "Nome", "Tipo", "Instituição", "Agência", "Conta Contábil", 
            "Número Banco", "Titular", "Nome Gerente", "Saldo Atual"
        ])
        
        # Configurar larguras de coluna
        self.tabela_contas.setColumnWidth(0, 40)  # ID
        self.tabela_contas.setColumnWidth(1, 150)  # Nome
        self.tabela_contas.setColumnWidth(2, 100)  # Tipo
        self.tabela_contas.setColumnWidth(3, 150)  # Instituição
        self.tabela_contas.setColumnWidth(4, 80)   # Agência
        self.tabela_contas.setColumnWidth(5, 120)  # Conta Contábil
        self.tabela_contas.setColumnWidth(6, 100)  # Número Banco
        self.tabela_contas.setColumnWidth(7, 150)  # Titular
        self.tabela_contas.setColumnWidth(8, 150)  # Nome Gerente
        self.tabela_contas.setColumnWidth(9, 100)  # Saldo Atual
        
        # Permitir rolagem horizontal
        self.tabela_contas.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Configurar comportamento da tabela
        self.tabela_contas.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_contas.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabela_contas)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.btn_nova = QPushButton("Nova Conta")
        self.btn_nova.clicked.connect(self.nova_conta)
        btn_layout.addWidget(self.btn_nova)
        
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.clicked.connect(self.editar_conta)
        btn_layout.addWidget(self.btn_editar)
        
        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.clicked.connect(self.excluir_conta)
        btn_layout.addWidget(self.btn_excluir)
        
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar_contas)
        btn_layout.addWidget(self.btn_atualizar)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def carregar_contas(self):
        """Carrega as contas do banco de dados e exibe na tabela."""
        contas = Conta.listar_todas(apenas_ativas=True)
        
        self.tabela_contas.setRowCount(0)
        
        for conta in contas:
            row = self.tabela_contas.rowCount()
            self.tabela_contas.insertRow(row)
            
            self.tabela_contas.setItem(row, 0, QTableWidgetItem(str(conta.id)))
            self.tabela_contas.setItem(row, 1, QTableWidgetItem(conta.nome))
            self.tabela_contas.setItem(row, 2, QTableWidgetItem(conta.tipo))
            self.tabela_contas.setItem(row, 3, QTableWidgetItem(conta.banco or ""))
            self.tabela_contas.setItem(row, 4, QTableWidgetItem(conta.agencia or ""))
            self.tabela_contas.setItem(row, 5, QTableWidgetItem(conta.conta_contabil or ""))
            self.tabela_contas.setItem(row, 6, QTableWidgetItem(conta.numero_banco or ""))
            self.tabela_contas.setItem(row, 7, QTableWidgetItem(conta.titular or ""))
            self.tabela_contas.setItem(row, 8, QTableWidgetItem(conta.nome_gerente or ""))
            
            # Formatar saldo com 2 casas decimais
            saldo_item = QTableWidgetItem(f"R$ {float(conta.saldo_atual):.2f}")
            saldo_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela_contas.setItem(row, 9, saldo_item)
        
        # Atualizar saldo total
        saldo_total = Conta.obter_saldo_total()
        self.total_label.setText(f"Saldo Total: R$ {float(saldo_total):.2f}")
        self.saldo_atualizado.emit(saldo_total)
        
    def nova_conta(self):
        """Abre o diálogo para criar uma nova conta."""
        dialog = ContaDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_conta_data()
            
            if not dados['nome']:
                QMessageBox.warning(self, "Erro", "O nome da conta é obrigatório.")
                return
            
            # Criar e salvar a nova conta
            conta = Conta(
                nome=dados['nome'],
                tipo=dados['tipo'],
                saldo_inicial=dados['saldo_inicial'],
                saldo_atual=dados['saldo_inicial'],
                banco=dados['banco'],
                agencia=dados['agencia'],
                conta_contabil=dados['conta_contabil'],
                numero_banco=dados['numero_banco'],
                titular=dados['titular'],
                nome_gerente=dados['nome_gerente'],
                contato_gerente=dados['contato_gerente']
            )
            
            if conta.salvar():
                self.carregar_contas()
                QMessageBox.information(self, "Sucesso", "Conta criada com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao criar conta.")
    
    def editar_conta(self):
        """Abre o diálogo para editar a conta selecionada."""
        selected_rows = self.tabela_contas.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione uma conta para editar.")
            return
        
        # Obter o ID da conta selecionada
        row = selected_rows[0].row()
        conta_id = int(self.tabela_contas.item(row, 0).text())
        
        # Buscar a conta no banco de dados
        conta = Conta.buscar_por_id(conta_id)
        if not conta:
            QMessageBox.critical(self, "Erro", "Conta não encontrada.")
            return
        
        # Abrir diálogo de edição
        dialog = ContaDialog(self, conta)
        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_conta_data()
            
            if not dados['nome']:
                QMessageBox.warning(self, "Erro", "O nome da conta é obrigatório.")
                return
            
            # Atualizar dados da conta
            conta.nome = dados['nome']
            conta.tipo = dados['tipo']
            conta.banco = dados['banco']
            conta.agencia = dados['agencia']
            conta.conta_contabil = dados['conta_contabil']
            conta.numero_banco = dados['numero_banco']
            conta.titular = dados['titular']
            conta.nome_gerente = dados['nome_gerente']
            conta.contato_gerente = dados['contato_gerente']
            
            if conta.salvar():
                self.carregar_contas()
                QMessageBox.information(self, "Sucesso", "Conta atualizada com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao atualizar conta.")
    
    def excluir_conta(self):
        """Exclui (desativa) a conta selecionada."""
        selected_rows = self.tabela_contas.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione uma conta para excluir.")
            return
        
        # Confirmar exclusão
        resposta = QMessageBox.question(
            self, 
            "Confirmar Exclusão", 
            "Tem certeza que deseja excluir esta conta? Esta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.No:
            return
        
        # Obter o ID da conta selecionada
        row = selected_rows[0].row()
        conta_id = int(self.tabela_contas.item(row, 0).text())
        
        # Buscar a conta no banco de dados
        conta = Conta.buscar_por_id(conta_id)
        if not conta:
            QMessageBox.critical(self, "Erro", "Conta não encontrada.")
            return
        
        # Excluir a conta
        if conta.excluir():
            self.carregar_contas()
            QMessageBox.information(self, "Sucesso", "Conta excluída com sucesso!")
        else:
            QMessageBox.critical(self, "Erro", "Erro ao excluir conta.")