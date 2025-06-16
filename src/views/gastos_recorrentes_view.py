# src/views/gastos_recorrentes_view.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                            QMessageBox, QDialog, QFormLayout, QComboBox, 
                            QDialogButtonBox, QHeaderView, QTextEdit, QDateEdit,
                            QSpinBox, QCheckBox, QCalendarWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QLocale
from PyQt5.QtGui import QColor, QDoubleValidator
from datetime import date, datetime
from decimal import Decimal
from src.models.gasto_recorrente import GastoRecorrente
from src.models.categoria import Categoria
from src.models.conta import Conta
from src.models.meio_pagamento import MeioPagamento

class GastoRecorrenteDialog(QDialog):
    """Diálogo para criar ou editar um gasto recorrente."""
    
    def __init__(self, parent=None, gasto=None):
        super().__init__(parent)
        self.gasto = gasto
        self.setWindowTitle("Novo Gasto Recorrente" if gasto is None else "Editar Gasto Recorrente")
        self.setMinimumWidth(500)
        # Configurar localização para Brasil (vírgula como separador decimal)
        self.locale = QLocale(QLocale.Portuguese, QLocale.Brazil)
        QLocale.setDefault(self.locale)
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QFormLayout(self)
        
        # Campos do formulário
        self.nome_edit = QLineEdit(self)
        if self.gasto:
            self.nome_edit.setText(self.gasto.nome)
        
        self.valor_edit = QLineEdit(self)
        validator = QDoubleValidator(0, 1000000, 2)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.valor_edit.setValidator(validator)
        if self.gasto:
            self.valor_edit.setText(str(self.gasto.valor).replace('.', ','))
        else:
            self.valor_edit.setText("0,00")
        
        self.dia_vencimento_spin = QSpinBox(self)
        self.dia_vencimento_spin.setRange(1, 31)
        if self.gasto:
            self.dia_vencimento_spin.setValue(self.gasto.dia_vencimento)
        else:
            self.dia_vencimento_spin.setValue(1)
        
        self.periodicidade_combo = QComboBox(self)
        self.periodicidade_combo.addItems(["Mensal", "Bimestral", "Trimestral", "Semestral", "Anual"])
        if self.gasto and self.gasto.periodicidade:
            index = self.periodicidade_combo.findText(self.gasto.periodicidade)
            if index >= 0:
                self.periodicidade_combo.setCurrentIndex(index)
        
        self.categoria_combo = QComboBox(self)
        self.categoria_combo.addItem("Nenhuma", None)
        
        # Carregar categorias
        categorias = Categoria.listar_todas(apenas_ativas=True)
        for categoria in categorias:
            self.categoria_combo.addItem(f"{categoria.nome}", categoria.id)
        
        # Se for edição, selecionar a categoria
        if self.gasto and self.gasto.categoria_id:
            index = self.categoria_combo.findData(self.gasto.categoria_id)
            if index >= 0:
                self.categoria_combo.setCurrentIndex(index)
        
        self.conta_combo = QComboBox(self)
        self.conta_combo.addItem("Nenhuma", None)
        
        # Carregar contas
        contas = Conta.listar_todas(apenas_ativas=True)
        for conta in contas:
            self.conta_combo.addItem(f"{conta.nome} ({conta.tipo})", conta.id)
        
        # Se for edição, selecionar a conta
        if self.gasto and self.gasto.conta_id:
            index = self.conta_combo.findData(self.gasto.conta_id)
            if index >= 0:
                self.conta_combo.setCurrentIndex(index)
        
        self.meio_pagamento_combo = QComboBox(self)
        self.meio_pagamento_combo.addItem("Nenhum", None)
        
        # Carregar meios de pagamento
        meios_pagamento = MeioPagamento.listar_todos(apenas_ativos=True)
        for meio in meios_pagamento:
            self.meio_pagamento_combo.addItem(f"{meio.nome}", meio.id)
        
        # Se for edição, selecionar o meio de pagamento
        if self.gasto and self.gasto.meio_pagamento_id:
            index = self.meio_pagamento_combo.findData(self.gasto.meio_pagamento_id)
            if index >= 0:
                self.meio_pagamento_combo.setCurrentIndex(index)
        
        self.data_inicio_edit = QDateEdit(self)
        self.data_inicio_edit.setCalendarPopup(True)
        self.data_inicio_edit.setDate(QDate.currentDate() if not self.gasto or not self.gasto.data_inicio else QDate(self.gasto.data_inicio.year, self.gasto.data_inicio.month, self.gasto.data_inicio.day))
        
        self.data_fim_edit = QDateEdit(self)
        self.data_fim_edit.setCalendarPopup(True)
        self.data_fim_edit.setDate(QDate.currentDate().addYears(1))
        self.data_fim_edit.setEnabled(False)  # Desabilitado por padrão
        
        self.data_fim_check = QCheckBox("Definir data de término")
        self.data_fim_check.setChecked(False)
        self.data_fim_check.stateChanged.connect(self.toggle_data_fim)
        
        if self.gasto and self.gasto.data_fim:
            self.data_fim_check.setChecked(True)
            self.data_fim_edit.setDate(QDate(self.gasto.data_fim.year, self.gasto.data_fim.month, self.gasto.data_fim.day))
        
        self.gerar_transacao_check = QCheckBox("Gerar transação automaticamente")
        if self.gasto:
            self.gerar_transacao_check.setChecked(self.gasto.gerar_transacao)
        
        self.observacao_edit = QTextEdit(self)
        self.observacao_edit.setMaximumHeight(80)
        if self.gasto and self.gasto.observacao:
            self.observacao_edit.setText(self.gasto.observacao)
        
        # Adicionar campos ao layout
        layout.addRow("Nome:", self.nome_edit)
        layout.addRow("Valor:", self.valor_edit)
        layout.addRow("Dia de Vencimento:", self.dia_vencimento_spin)
        layout.addRow("Periodicidade:", self.periodicidade_combo)
        layout.addRow("Categoria:", self.categoria_combo)
        layout.addRow("Conta:", self.conta_combo)
        layout.addRow("Meio de Pagamento:", self.meio_pagamento_combo)
        layout.addRow("Data de Início:", self.data_inicio_edit)
        layout.addRow(self.data_fim_check)
        layout.addRow("Data de Término:", self.data_fim_edit)
        layout.addRow(self.gerar_transacao_check)
        layout.addRow("Observação:", self.observacao_edit)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def toggle_data_fim(self, state):
        """Habilita/desabilita o campo de data de término."""
        self.data_fim_edit.setEnabled(state == Qt.Checked)
    
    def get_gasto_recorrente_data(self):
        """Retorna os dados do gasto recorrente do formulário."""
        nome = self.nome_edit.text().strip()
        
        try:
            # Substituir vírgula por ponto para conversão para Decimal
            valor_texto = self.valor_edit.text().strip().replace(',', '.')
            valor = Decimal(valor_texto)
            if valor <= 0:
                QMessageBox.warning(self, "Valor inválido", "O valor deve ser maior que zero.")
                valor = Decimal('0.0')
        except:
            QMessageBox.warning(self, "Valor inválido", "Por favor, insira um valor numérico válido.")
            valor = Decimal('0.0')
        
        dia_vencimento = self.dia_vencimento_spin.value()
        periodicidade = self.periodicidade_combo.currentText()
        categoria_id = self.categoria_combo.currentData()
        conta_id = self.conta_combo.currentData()
        meio_pagamento_id = self.meio_pagamento_combo.currentData()
        
        data_inicio = self.data_inicio_edit.date().toPyDate()
        data_fim = self.data_fim_edit.date().toPyDate() if self.data_fim_check.isChecked() else None
        
        gerar_transacao = self.gerar_transacao_check.isChecked()
        observacao = self.observacao_edit.toPlainText().strip() or None
        
        return {
            'nome': nome,
            'valor': valor,
            'dia_vencimento': dia_vencimento,
            'periodicidade': periodicidade,
            'categoria_id': categoria_id,
            'conta_id': conta_id,
            'meio_pagamento_id': meio_pagamento_id,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'gerar_transacao': gerar_transacao,
            'observacao': observacao
        }

class PagamentoDialog(QDialog):
    """Diálogo para marcar um pagamento como realizado."""
    
    def __init__(self, parent=None, gasto=None, ano=None, mes=None):
        super().__init__(parent)
        self.gasto = gasto
        self.ano = ano or date.today().year
        self.mes = mes or date.today().month
        self.setWindowTitle(f"Registrar Pagamento - {gasto.nome}")
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QFormLayout(self)
        
        # Informações do gasto
        info_label = QLabel(f"<b>{self.gasto.nome}</b><br>Valor: R$ {str(self.gasto.valor).replace('.', ',')}<br>Vencimento: Dia {self.gasto.dia_vencimento}")
        layout.addRow(info_label)
        
        # Campos do formulário
        self.data_pagamento_edit = QDateEdit(self)
        self.data_pagamento_edit.setCalendarPopup(True)
        self.data_pagamento_edit.setDate(QDate.currentDate())
        
        self.valor_pago_edit = QLineEdit(self)
        validator = QDoubleValidator(0, 1000000, 2)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.valor_pago_edit.setValidator(validator)
        self.valor_pago_edit.setText(str(self.gasto.valor).replace('.', ','))
        
        self.gerar_transacao_check = QCheckBox("Gerar transação")
        self.gerar_transacao_check.setChecked(self.gasto.gerar_transacao)
        
        # Adicionar campos ao layout
        layout.addRow("Data do Pagamento:", self.data_pagamento_edit)
        layout.addRow("Valor Pago:", self.valor_pago_edit)
        layout.addRow(self.gerar_transacao_check)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_pagamento_data(self):
        """Retorna os dados do pagamento do formulário."""
        data_pagamento = self.data_pagamento_edit.date().toPyDate()
        
        try:
            # Substituir vírgula por ponto para conversão para Decimal
            valor_texto = self.valor_pago_edit.text().strip().replace(',', '.')
            valor_pago = Decimal(valor_texto)
            if valor_pago <= 0:
                QMessageBox.warning(self, "Valor inválido", "O valor deve ser maior que zero.")
                valor_pago = self.gasto.valor
        except:
            QMessageBox.warning(self, "Valor inválido", "Por favor, insira um valor numérico válido.")
            valor_pago = self.gasto.valor
        
        gerar_transacao = self.gerar_transacao_check.isChecked()
        
        return {
            'data_pagamento': data_pagamento,
            'valor_pago': valor_pago,
            'gerar_transacao': gerar_transacao
        }

class GastosRecorrentesView(QWidget):
    """Widget para gestão de gastos recorrentes."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestão de Gastos Recorrentes")
        self.setup_ui()
        self.carregar_gastos()
        
    def setup_ui(self):
        """Configura a interface do widget."""
        layout = QVBoxLayout(self)
        
        # Área de filtros
        filtros_layout = QHBoxLayout()
        
        # Filtro por mês/ano
        self.mes_combo = QComboBox()
        self.mes_combo.addItems(["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
        self.mes_combo.setCurrentIndex(date.today().month - 1)
        
        self.ano_spin = QSpinBox()
        self.ano_spin.setRange(2000, 2100)
        self.ano_spin.setValue(date.today().year)
        
        filtros_layout.addWidget(QLabel("Mês:"))
        filtros_layout.addWidget(self.mes_combo)
        filtros_layout.addWidget(QLabel("Ano:"))
        filtros_layout.addWidget(self.ano_spin)
        
        # Botão para aplicar filtros
        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.clicked.connect(self.carregar_gastos)
        filtros_layout.addWidget(self.btn_filtrar)
        
        # Checkbox para mostrar apenas pendentes
        self.apenas_pendentes_check = QCheckBox("Apenas pendentes")
        self.apenas_pendentes_check.setChecked(True)
        filtros_layout.addWidget(self.apenas_pendentes_check)
        
        filtros_layout.addStretch()
        layout.addLayout(filtros_layout)
        
        # Tabela de gastos recorrentes
        self.tabela_gastos = QTableWidget(0, 7)
        self.tabela_gastos.setHorizontalHeaderLabels(["ID", "Nome", "Valor", "Vencimento", "Categoria", "Status", "Ações"])
        self.tabela_gastos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela_gastos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_gastos.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabela_gastos)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.btn_novo = QPushButton("Novo Gasto Recorrente")
        self.btn_novo.clicked.connect(self.novo_gasto)
        btn_layout.addWidget(self.btn_novo)
        
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.clicked.connect(self.editar_gasto)
        btn_layout.addWidget(self.btn_editar)
        
        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.clicked.connect(self.excluir_gasto)
        btn_layout.addWidget(self.btn_excluir)
        
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar_gastos)
        btn_layout.addWidget(self.btn_atualizar)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def carregar_gastos(self):
        """Carrega os gastos recorrentes do banco de dados e exibe na tabela."""
        # Obter mês e ano selecionados
        mes = self.mes_combo.currentIndex() + 1
        ano = self.ano_spin.value()
        apenas_pendentes = self.apenas_pendentes_check.isChecked()
        
        # Limpar tabela
        self.tabela_gastos.setRowCount(0)
        
        # Buscar todos os gastos recorrentes
        gastos = GastoRecorrente.listar_todos(apenas_ativos=True)
        
        for gasto in gastos:
            # Verificar se o gasto está ativo para o mês/ano selecionado
            if gasto.data_inicio and date(ano, mes, 1) < gasto.data_inicio:
                continue
            
            if gasto.data_fim and date(ano, mes, 28) > gasto.data_fim:
                continue
            
            # Verificar status de pagamento
            status_pagamento = gasto.verificar_pagamento(ano, mes)
            
            # Se apenas pendentes e já está pago, pular
            if apenas_pendentes and status_pagamento.get('pago', False):
                continue
            
            row = self.tabela_gastos.rowCount()
            self.tabela_gastos.insertRow(row)
            
            # ID
            self.tabela_gastos.setItem(row, 0, QTableWidgetItem(str(gasto.id)))
            
            # Nome
            self.tabela_gastos.setItem(row, 1, QTableWidgetItem(gasto.nome))
            
            # Valor
            self.tabela_gastos.setItem(row, 2, QTableWidgetItem(f"R$ {gasto.valor:.2f}".replace('.', ',')))
            
            # Vencimento
            self.tabela_gastos.setItem(row, 3, QTableWidgetItem(f"Dia {gasto.dia_vencimento}"))
            
            # Categoria
            categoria_nome = gasto.categoria.nome if gasto.categoria else "N/A"
            self.tabela_gastos.setItem(row, 4, QTableWidgetItem(categoria_nome))
            
            # Status
            status_text = "Pago" if status_pagamento.get('pago', False) else "Pendente"
            status_item = QTableWidgetItem(status_text)
            if status_pagamento.get('pago', False):
                status_item.setBackground(QColor(200, 255, 200))  # Verde claro
            else:
                # Verificar se está vencido
                hoje = date.today()
                if ano < hoje.year or (ano == hoje.year and mes < hoje.month) or (ano == hoje.year and mes == hoje.month and gasto.dia_vencimento < hoje.day):
                    status_item.setBackground(QColor(255, 200, 200))  # Vermelho claro
            
            self.tabela_gastos.setItem(row, 5, status_item)
            
            # Botão de ação para marcar como pago
            if not status_pagamento.get('pago', False):
                btn_pagar = QPushButton("Pagar")
                btn_pagar.setProperty("gasto_id", gasto.id)
                btn_pagar.setProperty("ano", ano)
                btn_pagar.setProperty("mes", mes)
                btn_pagar.clicked.connect(self.marcar_como_pago)
                self.tabela_gastos.setCellWidget(row, 6, btn_pagar)
    
    def novo_gasto(self):
        """Abre o diálogo para criar um novo gasto recorrente."""
        dialog = GastoRecorrenteDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_gasto_recorrente_data()
            
            if not dados['nome']:
                QMessageBox.warning(self, "Erro", "O nome do gasto recorrente é obrigatório.")
                return
            
            # Criar e salvar o novo gasto recorrente
            gasto = GastoRecorrente(
                nome=dados['nome'],
                valor=dados['valor'],
                dia_vencimento=dados['dia_vencimento'],
                periodicidade=dados['periodicidade'],
                categoria_id=dados['categoria_id'],
                conta_id=dados['conta_id'],
                meio_pagamento_id=dados['meio_pagamento_id'],
                data_inicio=dados['data_inicio'],
                data_fim=dados['data_fim'],
                gerar_transacao=dados['gerar_transacao'],
                observacao=dados['observacao']
            )
            
            if gasto.salvar():
                self.carregar_gastos()
                QMessageBox.information(self, "Sucesso", "Gasto recorrente criado com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao criar gasto recorrente.")
    
    def editar_gasto(self):
        """Abre o diálogo para editar o gasto recorrente selecionado."""
        selected_rows = self.tabela_gastos.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um gasto recorrente para editar.")
            return
        
        # Obter o ID do gasto recorrente selecionado
        row = selected_rows[0].row()
        gasto_id = int(self.tabela_gastos.item(row, 0).text())
        
        # Buscar o gasto recorrente no banco de dados
        gasto = GastoRecorrente.buscar_por_id(gasto_id)
        if not gasto:
            QMessageBox.critical(self, "Erro", "Gasto recorrente não encontrado.")
            return
        
        # Abrir diálogo de edição
        dialog = GastoRecorrenteDialog(self, gasto)
        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_gasto_recorrente_data()
            
            if not dados['nome']:
                QMessageBox.warning(self, "Erro", "O nome do gasto recorrente é obrigatório.")
                return
            
            # Atualizar dados do gasto recorrente
            gasto.nome = dados['nome']
            gasto.valor = dados['valor']
            gasto.dia_vencimento = dados['dia_vencimento']
            gasto.periodicidade = dados['periodicidade']
            gasto.categoria_id = dados['categoria_id']
            gasto.conta_id = dados['conta_id']
            gasto.meio_pagamento_id = dados['meio_pagamento_id']
            gasto.data_inicio = dados['data_inicio']
            gasto.data_fim = dados['data_fim']
            gasto.gerar_transacao = dados['gerar_transacao']
            gasto.observacao = dados['observacao']
            
            if gasto.salvar():
                self.carregar_gastos()
                QMessageBox.information(self, "Sucesso", "Gasto recorrente atualizado com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao atualizar gasto recorrente.")
    
    def excluir_gasto(self):
        """Exclui (desativa) o gasto recorrente selecionado."""
        selected_rows = self.tabela_gastos.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um gasto recorrente para excluir.")
            return
        
        # Obter o ID do gasto recorrente selecionado
        row = selected_rows[0].row()
        gasto_id = int(self.tabela_gastos.item(row, 0).text())
        
        # Buscar o gasto recorrente no banco de dados
        gasto = GastoRecorrente.buscar_por_id(gasto_id)
        if not gasto:
            QMessageBox.critical(self, "Erro", "Gasto recorrente não encontrado.")
            return
        
        # Confirmar exclusão
        resposta = QMessageBox.question(
            self, 
            "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir o gasto recorrente '{gasto.nome}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.No:
            return
        
        # Desativar o gasto recorrente
        gasto.ativo = False
        if gasto.salvar():
            self.carregar_gastos()
            QMessageBox.information(self, "Sucesso", "Gasto recorrente excluído com sucesso!")
        else:
            QMessageBox.critical(self, "Erro", "Erro ao excluir gasto recorrente.")
    
    def marcar_como_pago(self):
        """Marca um gasto recorrente como pago para o mês atual."""
        # Obter o botão que foi clicado
        btn = self.sender()
        gasto_id = btn.property("gasto_id")
        ano = btn.property("ano")
        mes = btn.property("mes")
        
        # Buscar o gasto recorrente no banco de dados
        gasto = GastoRecorrente.buscar_por_id(gasto_id)
        if not gasto:
            QMessageBox.critical(self, "Erro", "Gasto recorrente não encontrado.")
            return
        
        # Abrir diálogo para registrar pagamento
        dialog = PagamentoDialog(self, gasto, ano, mes)
        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_pagamento_data()
            
            # Marcar como pago
            if gasto.marcar_como_pago(ano, mes, dados['data_pagamento'], dados['valor_pago'], dados['gerar_transacao']):
                self.carregar_gastos()
                QMessageBox.information(self, "Sucesso", "Pagamento registrado com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao registrar pagamento.")