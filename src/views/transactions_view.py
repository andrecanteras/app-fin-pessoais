"""
Interface gráfica para gestão de transações financeiras.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                            QMessageBox, QDialog, QFormLayout, QComboBox, 
                            QDialogButtonBox, QHeaderView, QDateEdit, QTextEdit,
                            QTabWidget, QGroupBox, QRadioButton)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QLocale
from PyQt5.QtGui import QDoubleValidator
from decimal import Decimal
from datetime import datetime, date
from src.models.transacao import Transacao
from src.models.conta import Conta
from src.models.categoria import Categoria
from src.models.meio_pagamento import MeioPagamento

class TransacaoDialog(QDialog):
    """Diálogo para criar ou editar uma transação."""
    
    def __init__(self, parent=None, transacao=None):
        super().__init__(parent)
        self.transacao = transacao
        self.setWindowTitle("Nova Transação" if transacao is None else "Editar Transação")
        # Configurar localização para Brasil (vírgula como separador decimal)
        self.locale = QLocale(QLocale.Portuguese, QLocale.Brazil)
        QLocale.setDefault(self.locale)
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QFormLayout(self)
        
        # Campos do formulário
        self.descricao_edit = QLineEdit(self)
        if self.transacao:
            self.descricao_edit.setText(self.transacao.descricao)
        
        # Tipo (Receita ou Despesa)
        self.tipo_group = QGroupBox("Tipo")
        tipo_layout = QHBoxLayout()
        self.receita_radio = QRadioButton("Receita")
        self.despesa_radio = QRadioButton("Despesa")
        tipo_layout.addWidget(self.receita_radio)
        tipo_layout.addWidget(self.despesa_radio)
        self.tipo_group.setLayout(tipo_layout)
        
        if self.transacao:
            if self.transacao.tipo == 'R':
                self.receita_radio.setChecked(True)
            else:
                self.despesa_radio.setChecked(True)
        else:
            self.despesa_radio.setChecked(True)  # Padrão
        
        # Conectar mudança de tipo para atualizar categorias
        self.receita_radio.toggled.connect(self.atualizar_categorias)
        self.despesa_radio.toggled.connect(self.atualizar_categorias)
        
        # Valor
        self.valor_edit = QLineEdit(self)
        validator = QDoubleValidator(0, 1000000, 2)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.valor_edit.setValidator(validator)
        # Configurar para usar vírgula como separador decimal
        if self.transacao:
            self.valor_edit.setText(str(self.transacao.valor).replace('.', ','))
        else:
            self.valor_edit.setText("0,00")
        
        # Data
        self.data_edit = QDateEdit(self)
        self.data_edit.setCalendarPopup(True)
        if self.transacao and self.transacao.data_transacao:
            self.data_edit.setDate(QDate(
                self.transacao.data_transacao.year,
                self.transacao.data_transacao.month,
                self.transacao.data_transacao.day
            ))
        else:
            self.data_edit.setDate(QDate.currentDate())
        
        # Categoria
        self.categoria_combo = QComboBox(self)
        
        # Conta
        self.conta_combo = QComboBox(self)
        self.carregar_contas()
        if self.transacao and self.transacao.conta_id:
            index = self.conta_combo.findData(self.transacao.conta_id)
            if index >= 0:
                self.conta_combo.setCurrentIndex(index)
        
        # Meio de Pagamento
        self.meio_pagamento_combo = QComboBox(self)
        self.conta_combo.currentIndexChanged.connect(self.atualizar_meios_pagamento)
        
        # Atualizar meios de pagamento iniciais
        self.atualizar_meios_pagamento()
        
        if self.transacao and self.transacao.meio_pagamento_id:
            index = self.meio_pagamento_combo.findData(self.transacao.meio_pagamento_id)
            if index >= 0:
                self.meio_pagamento_combo.setCurrentIndex(index)
        
        # Descrição do Pagamento
        self.descricao_pagamento_edit = QLineEdit(self)
        if self.transacao and self.transacao.descricao_pagamento:
            self.descricao_pagamento_edit.setText(self.transacao.descricao_pagamento)
        
        # Local da Transação
        self.local_transacao_edit = QLineEdit(self)
        if self.transacao and self.transacao.local_transacao:
            self.local_transacao_edit.setText(self.transacao.local_transacao)
        
        # Observação
        self.observacao_edit = QTextEdit(self)
        self.observacao_edit.setMaximumHeight(80)
        if self.transacao and self.transacao.observacao:
            self.observacao_edit.setText(self.transacao.observacao)
        
        # Carregar categorias iniciais
        self.atualizar_categorias()
        
        # Se for edição, selecionar categoria
        if self.transacao and self.transacao.categoria_id:
            index = self.categoria_combo.findData(self.transacao.categoria_id)
            if index >= 0:
                self.categoria_combo.setCurrentIndex(index)
        
        # Adicionar campos ao layout
        layout.addRow("Descrição:", self.descricao_edit)
        layout.addRow(self.tipo_group)
        layout.addRow("Valor (R$):", self.valor_edit)
        layout.addRow("Data:", self.data_edit)
        layout.addRow("Categoria:", self.categoria_combo)
        layout.addRow("Conta:", self.conta_combo)
        layout.addRow("Meio de Pagamento:", self.meio_pagamento_combo)
        layout.addRow("Descrição do Pagamento:", self.descricao_pagamento_edit)
        layout.addRow("Local da Transação:", self.local_transacao_edit)
        layout.addRow("Observação:", self.observacao_edit)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def carregar_contas(self):
        """Carrega as contas disponíveis."""
        self.conta_combo.clear()
        contas = Conta.listar_todas(apenas_ativas=True)
        
        for conta in contas:
            self.conta_combo.addItem(f"{conta.nome} (R$ {float(conta.saldo_atual):.2f})", conta.id)
    
    def atualizar_meios_pagamento(self):
        """Atualiza os meios de pagamento disponíveis para a conta selecionada."""
        self.meio_pagamento_combo.clear()
        conta_id = self.conta_combo.currentData()
        
        if conta_id:
            meios_pagamento = MeioPagamento.listar_todos(apenas_ativos=True, conta_id=conta_id)
            
            for meio in meios_pagamento:
                self.meio_pagamento_combo.addItem(f"{meio.nome} ({meio.tipo})", meio.id)
    
    def atualizar_categorias(self):
        """Atualiza as categorias disponíveis com base no tipo selecionado."""
        self.categoria_combo.clear()
        tipo = 'R' if self.receita_radio.isChecked() else 'D'
        
        categorias = Categoria.listar_todas(apenas_ativas=True, tipo=tipo)
        
        # Organizar categorias por hierarquia
        categorias_principais = [c for c in categorias if not c.categoria_pai_id]
        
        for cat in categorias_principais:
            self.categoria_combo.addItem(cat.nome, cat.id)
            
            # Adicionar subcategorias com indentação
            subcategorias = [c for c in categorias if c.categoria_pai_id == cat.id]
            for subcat in subcategorias:
                self.categoria_combo.addItem(f"  └─ {subcat.nome}", subcat.id)
    
    def get_transacao_data(self):
        """Retorna os dados da transação do formulário."""
        descricao = self.descricao_edit.text().strip()
        tipo = 'R' if self.receita_radio.isChecked() else 'D'
        
        try:
            # Substituir vírgula por ponto para conversão para Decimal
            valor_texto = self.valor_edit.text().replace(',', '.')
            valor = Decimal(valor_texto)
            if valor <= 0:
                QMessageBox.warning(self, "Valor inválido", "O valor deve ser maior que zero.")
                valor = Decimal('0')
        except:
            QMessageBox.warning(self, "Valor inválido", "Por favor, insira um valor numérico válido.")
            valor = Decimal('0')
        
        data_transacao = self.data_edit.date().toPyDate()
        categoria_id = self.categoria_combo.currentData()
        conta_id = self.conta_combo.currentData()
        meio_pagamento_id = self.meio_pagamento_combo.currentData()
        descricao_pagamento = self.descricao_pagamento_edit.text().strip() or None
        local_transacao = self.local_transacao_edit.text().strip() or None
        observacao = self.observacao_edit.toPlainText().strip() or None
        
        return {
            'descricao': descricao,
            'tipo': tipo,
            'valor': valor,
            'data_transacao': data_transacao,
            'categoria_id': categoria_id,
            'conta_id': conta_id,
            'meio_pagamento_id': meio_pagamento_id,
            'descricao_pagamento': descricao_pagamento,
            'local_transacao': local_transacao,
            'observacao': observacao
        }

class TransactionsView(QWidget):
    """Widget para gestão de transações."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestão de Transações")
        self.setup_ui()
        self.carregar_transacoes()
        
    def setup_ui(self):
        """Configura a interface do widget."""
        layout = QVBoxLayout(self)
        
        # Área de filtros
        filtros_layout = QHBoxLayout()
        
        # Filtro por tipo
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItem("Todos os tipos", None)
        self.tipo_combo.addItem("Receitas", "R")
        self.tipo_combo.addItem("Despesas", "D")
        filtros_layout.addWidget(QLabel("Tipo:"))
        filtros_layout.addWidget(self.tipo_combo)
        
        # Filtro por data
        self.data_inicio_edit = QDateEdit()
        self.data_inicio_edit.setCalendarPopup(True)
        self.data_inicio_edit.setDate(QDate.currentDate().addMonths(-1))
        
        self.data_fim_edit = QDateEdit()
        self.data_fim_edit.setCalendarPopup(True)
        self.data_fim_edit.setDate(QDate.currentDate())
        
        filtros_layout.addWidget(QLabel("De:"))
        filtros_layout.addWidget(self.data_inicio_edit)
        filtros_layout.addWidget(QLabel("Até:"))
        filtros_layout.addWidget(self.data_fim_edit)
        
        # Botão para aplicar filtros
        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.clicked.connect(self.carregar_transacoes)
        filtros_layout.addWidget(self.btn_filtrar)
        
        filtros_layout.addStretch()
        layout.addLayout(filtros_layout)
        
        # Tabela de transações
        self.tabela_transacoes = QTableWidget(0, 8)
        self.tabela_transacoes.setHorizontalHeaderLabels([
            "ID", "Data", "Descrição", "Tipo", "Categoria", "Conta", "Meio de Pagamento", "Valor"
        ])
        
        # Configurar larguras de coluna
        self.tabela_transacoes.setColumnWidth(0, 40)   # ID
        self.tabela_transacoes.setColumnWidth(1, 100)  # Data
        self.tabela_transacoes.setColumnWidth(2, 200)  # Descrição
        self.tabela_transacoes.setColumnWidth(3, 80)   # Tipo
        self.tabela_transacoes.setColumnWidth(4, 150)  # Categoria
        self.tabela_transacoes.setColumnWidth(5, 150)  # Conta
        self.tabela_transacoes.setColumnWidth(6, 150)  # Meio de Pagamento
        self.tabela_transacoes.setColumnWidth(7, 100)  # Valor
        
        # Configurar comportamento da tabela
        self.tabela_transacoes.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_transacoes.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabela_transacoes)
        
        # Área de resumo
        resumo_layout = QHBoxLayout()
        
        self.total_receitas_label = QLabel("Receitas: R$ 0,00")
        self.total_despesas_label = QLabel("Despesas: R$ 0,00")
        self.saldo_periodo_label = QLabel("Saldo: R$ 0,00")
        
        resumo_layout.addWidget(self.total_receitas_label)
        resumo_layout.addWidget(self.total_despesas_label)
        resumo_layout.addWidget(self.saldo_periodo_label)
        resumo_layout.addStretch()
        
        layout.addLayout(resumo_layout)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.btn_nova = QPushButton("Nova Transação")
        self.btn_nova.clicked.connect(self.nova_transacao)
        btn_layout.addWidget(self.btn_nova)
        
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.clicked.connect(self.editar_transacao)
        btn_layout.addWidget(self.btn_editar)
        
        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.clicked.connect(self.excluir_transacao)
        btn_layout.addWidget(self.btn_excluir)
        
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar_transacoes)
        btn_layout.addWidget(self.btn_atualizar)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def carregar_transacoes(self):
        """Carrega as transações do banco de dados e exibe na tabela."""
        # Construir filtros
        filtros = {}
        
        # Filtro por tipo
        tipo = self.tipo_combo.currentData()
        if tipo:
            filtros['tipo'] = tipo
        
        # Filtro por data
        data_inicio = self.data_inicio_edit.date().toPyDate()
        data_fim = self.data_fim_edit.date().toPyDate()
        filtros['data_inicio'] = data_inicio
        filtros['data_fim'] = data_fim
        
        # Ordenação
        filtros['ordenacao'] = "data_transacao DESC"
        
        # Buscar transações
        transacoes = Transacao.listar_todas(filtros)
        
        # Limpar tabela
        self.tabela_transacoes.setRowCount(0)
        
        # Variáveis para calcular totais
        total_receitas = Decimal('0')
        total_despesas = Decimal('0')
        
        # Carregar dados na tabela
        for transacao in transacoes:
            row = self.tabela_transacoes.rowCount()
            self.tabela_transacoes.insertRow(row)
            
            # Formatar data
            data_str = transacao.data_transacao.strftime("%d/%m/%Y")
            
            # Obter nome da categoria
            categoria_nome = "N/A"
            if transacao.categoria:
                categoria_nome = transacao.categoria.nome
            
            # Obter nome da conta
            conta_nome = "N/A"
            if transacao.conta:
                conta_nome = transacao.conta.nome
            
            # Obter nome do meio de pagamento
            meio_pagamento_nome = "N/A"
            if transacao.meio_pagamento:
                meio_pagamento_nome = transacao.meio_pagamento.nome
            
            # Atualizar totais
            if transacao.tipo == 'R':
                total_receitas += transacao.valor
            else:
                total_despesas += transacao.valor
            
            # Adicionar dados à tabela
            self.tabela_transacoes.setItem(row, 0, QTableWidgetItem(str(transacao.id)))
            self.tabela_transacoes.setItem(row, 1, QTableWidgetItem(data_str))
            self.tabela_transacoes.setItem(row, 2, QTableWidgetItem(transacao.descricao))
            self.tabela_transacoes.setItem(row, 3, QTableWidgetItem("Receita" if transacao.tipo == 'R' else "Despesa"))
            self.tabela_transacoes.setItem(row, 4, QTableWidgetItem(categoria_nome))
            self.tabela_transacoes.setItem(row, 5, QTableWidgetItem(conta_nome))
            self.tabela_transacoes.setItem(row, 6, QTableWidgetItem(meio_pagamento_nome))
            
            # Formatar valor com 2 casas decimais usando vírgula como separador
            valor_str = f"R$ {float(transacao.valor):.2f}".replace('.', ',')
            valor_item = QTableWidgetItem(valor_str)
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Colorir valor conforme o tipo
            if transacao.tipo == 'R':
                valor_item.setForeground(Qt.darkGreen)
            else:
                valor_item.setForeground(Qt.darkRed)
                
            self.tabela_transacoes.setItem(row, 7, valor_item)
        
        # Atualizar resumo
        saldo_periodo = total_receitas - total_despesas
        
        self.total_receitas_label.setText(f"Receitas: R$ {float(total_receitas):.2f}".replace('.', ','))
        self.total_despesas_label.setText(f"Despesas: R$ {float(total_despesas):.2f}".replace('.', ','))
        self.saldo_periodo_label.setText(f"Saldo: R$ {float(saldo_periodo):.2f}".replace('.', ','))
        
        # Colorir saldo conforme o valor
        if saldo_periodo >= 0:
            self.saldo_periodo_label.setStyleSheet("color: darkgreen;")
        else:
            self.saldo_periodo_label.setStyleSheet("color: darkred;")
    
    def nova_transacao(self):
        """Abre o diálogo para criar uma nova transação."""
        dialog = TransacaoDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_transacao_data()
            
            if not dados['descricao']:
                QMessageBox.warning(self, "Erro", "A descrição da transação é obrigatória.")
                return
            
            if dados['valor'] <= 0:
                QMessageBox.warning(self, "Erro", "O valor deve ser maior que zero.")
                return
            
            # Criar e salvar a nova transação
            transacao = Transacao(
                descricao=dados['descricao'],
                valor=dados['valor'],
                data_transacao=dados['data_transacao'],
                tipo=dados['tipo'],
                categoria_id=dados['categoria_id'],
                conta_id=dados['conta_id'],
                meio_pagamento_id=dados['meio_pagamento_id'],
                descricao_pagamento=dados['descricao_pagamento'],
                local_transacao=dados['local_transacao'],
                observacao=dados['observacao']
            )
            
            if transacao.salvar():
                self.carregar_transacoes()
                QMessageBox.information(self, "Sucesso", "Transação criada com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao criar transação.")
    
    def editar_transacao(self):
        """Abre o diálogo para editar a transação selecionada."""
        selected_rows = self.tabela_transacoes.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione uma transação para editar.")
            return
        
        # Obter o ID da transação selecionada
        row = selected_rows[0].row()
        transacao_id = int(self.tabela_transacoes.item(row, 0).text())
        
        # Buscar a transação no banco de dados
        transacao = Transacao.buscar_por_id(transacao_id)
        if not transacao:
            QMessageBox.critical(self, "Erro", "Transação não encontrada.")
            return
        
        # Abrir diálogo de edição
        dialog = TransacaoDialog(self, transacao)
        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_transacao_data()
            
            if not dados['descricao']:
                QMessageBox.warning(self, "Erro", "A descrição da transação é obrigatória.")
                return
            
            if dados['valor'] <= 0:
                QMessageBox.warning(self, "Erro", "O valor deve ser maior que zero.")
                return
            
            # Atualizar dados da transação
            transacao.descricao = dados['descricao']
            transacao.valor = dados['valor']
            transacao.data_transacao = dados['data_transacao']
            transacao.tipo = dados['tipo']
            transacao.categoria_id = dados['categoria_id']
            transacao.conta_id = dados['conta_id']
            transacao.meio_pagamento_id = dados['meio_pagamento_id']
            transacao.descricao_pagamento = dados['descricao_pagamento']
            transacao.local_transacao = dados['local_transacao']
            transacao.observacao = dados['observacao']
            
            if transacao.salvar():
                self.carregar_transacoes()
                QMessageBox.information(self, "Sucesso", "Transação atualizada com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao atualizar transação.")
    
    def excluir_transacao(self):
        """Exclui a transação selecionada."""
        selected_rows = self.tabela_transacoes.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione uma transação para excluir.")
            return
        
        # Confirmar exclusão
        resposta = QMessageBox.question(
            self, 
            "Confirmar Exclusão", 
            "Tem certeza que deseja excluir esta transação? Esta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.No:
            return
        
        # Obter o ID da transação selecionada
        row = selected_rows[0].row()
        transacao_id = int(self.tabela_transacoes.item(row, 0).text())
        
        # Buscar a transação no banco de dados
        transacao = Transacao.buscar_por_id(transacao_id)
        if not transacao:
            QMessageBox.critical(self, "Erro", "Transação não encontrada.")
            return
        
        # Excluir a transação
        if transacao.excluir():
            self.carregar_transacoes()
            QMessageBox.information(self, "Sucesso", "Transação excluída com sucesso!")
        else:
            QMessageBox.critical(self, "Erro", "Erro ao excluir transação.")