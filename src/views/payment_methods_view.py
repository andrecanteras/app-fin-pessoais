"""
Interface gráfica para gestão de meios de pagamento.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                            QMessageBox, QDialog, QFormLayout, QComboBox, 
                            QDialogButtonBox, QHeaderView, QTextEdit, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
from src.models.meio_pagamento import MeioPagamento
from src.models.conta import Conta

class MeioPagamentoDialog(QDialog):
    """Diálogo para criar ou editar um meio de pagamento."""
    
    def __init__(self, parent=None, meio_pagamento=None):
        super().__init__(parent)
        self.meio_pagamento = meio_pagamento
        self.setWindowTitle("Novo Meio de Pagamento" if meio_pagamento is None else "Editar Meio de Pagamento")
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QFormLayout(self)
        
        # Campos do formulário
        self.nome_edit = QLineEdit(self)
        if self.meio_pagamento:
            self.nome_edit.setText(self.meio_pagamento.nome)
        
        self.tipo_combo = QComboBox(self)
        self.tipo_combo.addItems(["Cartão de Crédito", "Cartão de Débito", "Dinheiro", "PIX", "Transferência", "Outro"])
        if self.meio_pagamento and self.meio_pagamento.tipo:
            index = self.tipo_combo.findText(self.meio_pagamento.tipo)
            if index >= 0:
                self.tipo_combo.setCurrentIndex(index)
        
        self.descricao_edit = QTextEdit(self)
        self.descricao_edit.setMaximumHeight(80)
        if self.meio_pagamento and self.meio_pagamento.descricao:
            self.descricao_edit.setText(self.meio_pagamento.descricao)
        
        self.conta_combo = QComboBox(self)
        self.conta_combo.addItem("Nenhuma", None)
        
        # Carregar contas
        contas = Conta.listar_todas(apenas_ativas=True)
        for conta in contas:
            self.conta_combo.addItem(f"{conta.nome} ({conta.tipo})", conta.id)
        
        # Se for edição, selecionar a conta
        if self.meio_pagamento and self.meio_pagamento.conta_id:
            index = self.conta_combo.findData(self.meio_pagamento.conta_id)
            if index >= 0:
                self.conta_combo.setCurrentIndex(index)
        
        # Adicionar campos ao layout
        layout.addRow("Nome:", self.nome_edit)
        layout.addRow("Tipo:", self.tipo_combo)
        layout.addRow("Descrição:", self.descricao_edit)
        layout.addRow("Conta Associada:", self.conta_combo)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
        
    def get_meio_pagamento_data(self):
        """Retorna os dados do meio de pagamento do formulário."""
        nome = self.nome_edit.text().strip()
        tipo = self.tipo_combo.currentText()
        descricao = self.descricao_edit.toPlainText().strip() or None
        conta_id = self.conta_combo.currentData()
        
        return {
            'nome': nome,
            'tipo': tipo,
            'descricao': descricao,
            'conta_id': conta_id
        }

class PaymentMethodsView(QWidget):
    """Widget para gestão de meios de pagamento."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestão de Meios de Pagamento")
        self.setup_ui()
        self.carregar_meios_pagamento()
        
    def setup_ui(self):
        """Configura a interface do widget."""
        layout = QVBoxLayout(self)
        
        # Área de filtros
        filtros_layout = QHBoxLayout()
        
        # Filtro por tipo
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItem("Todos os tipos", None)
        self.tipo_combo.addItems(["Cartão de Crédito", "Cartão de Débito", "Dinheiro", "PIX", "Transferência", "Outro"])
        filtros_layout.addWidget(QLabel("Tipo:"))
        filtros_layout.addWidget(self.tipo_combo)
        
        # Filtro por conta
        self.conta_combo = QComboBox()
        self.conta_combo.addItem("Todas as contas", None)
        
        # Carregar contas
        contas = Conta.listar_todas(apenas_ativas=True)
        for conta in contas:
            self.conta_combo.addItem(f"{conta.nome} ({conta.tipo})", conta.id)
        
        filtros_layout.addWidget(QLabel("Conta:"))
        filtros_layout.addWidget(self.conta_combo)
        
        # Checkbox para mostrar apenas ativos
        self.apenas_ativos_check = QCheckBox("Apenas meios de pagamento ativos")
        self.apenas_ativos_check.setChecked(True)
        filtros_layout.addWidget(self.apenas_ativos_check)
        
        # Botão para aplicar filtros
        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.clicked.connect(self.carregar_meios_pagamento)
        filtros_layout.addWidget(self.btn_filtrar)
        
        filtros_layout.addStretch()
        layout.addLayout(filtros_layout)
        
        # Tabela de meios de pagamento
        self.tabela_meios_pagamento = QTableWidget(0, 5)
        self.tabela_meios_pagamento.setHorizontalHeaderLabels(["ID", "Nome", "Tipo", "Conta", "Ativo"])
        self.tabela_meios_pagamento.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela_meios_pagamento.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_meios_pagamento.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabela_meios_pagamento)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.btn_novo = QPushButton("Novo Meio de Pagamento")
        self.btn_novo.clicked.connect(self.novo_meio_pagamento)
        btn_layout.addWidget(self.btn_novo)
        
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.clicked.connect(self.editar_meio_pagamento)
        btn_layout.addWidget(self.btn_editar)
        
        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.clicked.connect(self.excluir_meio_pagamento)
        btn_layout.addWidget(self.btn_excluir)
        
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar_meios_pagamento)
        btn_layout.addWidget(self.btn_atualizar)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def carregar_meios_pagamento(self):
        """Carrega os meios de pagamento do banco de dados e exibe na tabela."""
        tipo = self.tipo_combo.currentText() if self.tipo_combo.currentIndex() > 0 else None
        conta_id = self.conta_combo.currentData()
        apenas_ativos = self.apenas_ativos_check.isChecked()
        
        # Buscar meios de pagamento
        if tipo:
            meios_pagamento = MeioPagamento.listar_por_tipo(tipo, apenas_ativos)
        else:
            meios_pagamento = MeioPagamento.listar_todos(apenas_ativos, conta_id)
        
        # Limpar tabela
        self.tabela_meios_pagamento.setRowCount(0)
        
        # Preencher tabela
        for meio in meios_pagamento:
            row = self.tabela_meios_pagamento.rowCount()
            self.tabela_meios_pagamento.insertRow(row)
            
            self.tabela_meios_pagamento.setItem(row, 0, QTableWidgetItem(str(meio.id)))
            self.tabela_meios_pagamento.setItem(row, 1, QTableWidgetItem(meio.nome))
            self.tabela_meios_pagamento.setItem(row, 2, QTableWidgetItem(meio.tipo))
            
            # Nome da conta
            conta_nome = "N/A"
            if meio.conta:
                conta_nome = meio.conta.nome
            self.tabela_meios_pagamento.setItem(row, 3, QTableWidgetItem(conta_nome))
            
            # Status
            self.tabela_meios_pagamento.setItem(row, 4, QTableWidgetItem("Sim" if meio.ativo else "Não"))
    
    def novo_meio_pagamento(self):
        """Abre o diálogo para criar um novo meio de pagamento."""
        dialog = MeioPagamentoDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_meio_pagamento_data()
            
            if not dados['nome']:
                QMessageBox.warning(self, "Erro", "O nome do meio de pagamento é obrigatório.")
                return
            
            # Criar e salvar o novo meio de pagamento
            meio_pagamento = MeioPagamento(
                nome=dados['nome'],
                tipo=dados['tipo'],
                descricao=dados['descricao'],
                conta_id=dados['conta_id']
            )
            
            if meio_pagamento.salvar():
                self.carregar_meios_pagamento()
                QMessageBox.information(self, "Sucesso", "Meio de pagamento criado com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao criar meio de pagamento.")
    
    def editar_meio_pagamento(self):
        """Abre o diálogo para editar o meio de pagamento selecionado."""
        selected_rows = self.tabela_meios_pagamento.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um meio de pagamento para editar.")
            return
        
        # Obter o ID do meio de pagamento selecionado
        row = selected_rows[0].row()
        meio_pagamento_id = int(self.tabela_meios_pagamento.item(row, 0).text())
        
        # Buscar o meio de pagamento no banco de dados
        meio_pagamento = MeioPagamento.buscar_por_id(meio_pagamento_id)
        if not meio_pagamento:
            QMessageBox.critical(self, "Erro", "Meio de pagamento não encontrado.")
            return
        
        # Abrir diálogo de edição
        dialog = MeioPagamentoDialog(self, meio_pagamento)
        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_meio_pagamento_data()
            
            if not dados['nome']:
                QMessageBox.warning(self, "Erro", "O nome do meio de pagamento é obrigatório.")
                return
            
            # Atualizar dados do meio de pagamento
            meio_pagamento.nome = dados['nome']
            meio_pagamento.tipo = dados['tipo']
            meio_pagamento.descricao = dados['descricao']
            meio_pagamento.conta_id = dados['conta_id']
            
            if meio_pagamento.salvar():
                self.carregar_meios_pagamento()
                QMessageBox.information(self, "Sucesso", "Meio de pagamento atualizado com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao atualizar meio de pagamento.")
    
    def excluir_meio_pagamento(self):
        """Exclui (desativa) o meio de pagamento selecionado."""
        selected_rows = self.tabela_meios_pagamento.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um meio de pagamento para excluir.")
            return
        
        # Obter o ID do meio de pagamento selecionado
        row = selected_rows[0].row()
        meio_pagamento_id = int(self.tabela_meios_pagamento.item(row, 0).text())
        
        # Buscar o meio de pagamento no banco de dados
        meio_pagamento = MeioPagamento.buscar_por_id(meio_pagamento_id)
        if not meio_pagamento:
            QMessageBox.critical(self, "Erro", "Meio de pagamento não encontrado.")
            return
        
        # Confirmar exclusão
        resposta = QMessageBox.question(
            self, 
            "Confirmar Exclusão", 
            "Tem certeza que deseja excluir este meio de pagamento? Esta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.No:
            return
        
        # Excluir o meio de pagamento
        if meio_pagamento.excluir():
            self.carregar_meios_pagamento()
            QMessageBox.information(self, "Sucesso", "Meio de pagamento excluído com sucesso!")
        else:
            QMessageBox.critical(self, "Erro", "Erro ao excluir meio de pagamento.")