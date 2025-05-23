"""
Interface gráfica para gestão de meios de pagamento.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                            QMessageBox, QDialog, QFormLayout, QComboBox, 
                            QDialogButtonBox, QHeaderView)
from PyQt5.QtCore import Qt
from src.database.connection import DatabaseConnection

class MeioPagamentoDialog(QDialog):
    """Diálogo para criar ou editar um meio de pagamento."""
    
    def __init__(self, parent=None, meio_pagamento_id=None):
        super().__init__(parent)
        self.meio_pagamento_id = meio_pagamento_id
        self.setWindowTitle("Novo Meio de Pagamento" if meio_pagamento_id is None else "Editar Meio de Pagamento")
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QFormLayout(self)
        
        # Campos do formulário
        self.nome_edit = QLineEdit(self)
        self.tipo_combo = QComboBox(self)
        self.tipo_combo.addItems(["Cartão de Crédito", "Cartão de Débito", "PIX", "Dinheiro", "Transferência", "Outro"])
        self.descricao_edit = QLineEdit(self)
        
        # Combobox para contas
        self.conta_combo = QComboBox(self)
        self.conta_combo.addItem("Nenhuma", None)
        
        # Carregar contas disponíveis
        self.carregar_contas()
        
        # Se estiver editando, carregar dados do meio de pagamento
        if self.meio_pagamento_id:
            self.carregar_dados_meio_pagamento()
        
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
    
    def carregar_contas(self):
        """Carrega as contas disponíveis no combobox."""
        db = DatabaseConnection()
        try:
            cursor = db.get_cursor()
            cursor.execute("SELECT id, nome FROM financas_pessoais.conta_dimensao WHERE ativo = 1 ORDER BY nome")
            contas = cursor.fetchall()
            
            for conta in contas:
                self.conta_combo.addItem(conta.nome, conta.id)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar contas: {e}")
        finally:
            db.close()
    
    def carregar_dados_meio_pagamento(self):
        """Carrega os dados do meio de pagamento para edição."""
        db = DatabaseConnection()
        try:
            cursor = db.get_cursor()
            cursor.execute("SELECT * FROM financas_pessoais.meios_pagamento WHERE id = ?", (self.meio_pagamento_id,))
            row = cursor.fetchone()
            
            if row:
                self.nome_edit.setText(row.nome)
                
                # Selecionar o tipo correto
                index = self.tipo_combo.findText(row.tipo)
                if index >= 0:
                    self.tipo_combo.setCurrentIndex(index)
                
                # Descrição
                if row.descricao:
                    self.descricao_edit.setText(row.descricao)
                
                # Conta associada
                if row.conta_id:
                    index = self.conta_combo.findData(row.conta_id)
                    if index >= 0:
                        self.conta_combo.setCurrentIndex(index)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados do meio de pagamento: {e}")
        finally:
            db.close()
    
    def get_meio_pagamento_data(self):
        """Retorna os dados do meio de pagamento do formulário."""
        nome = self.nome_edit.text().strip()
        tipo = self.tipo_combo.currentText()
        descricao = self.descricao_edit.text().strip() or None
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
        
        # Título
        titulo = QLabel("Meios de Pagamento")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)
        
        # Tabela de meios de pagamento
        self.tabela_meios = QTableWidget(0, 6)  # 6 colunas
        self.tabela_meios.setHorizontalHeaderLabels([
            "ID", "Nome", "Tipo", "Descrição", "Conta Associada", "Banco Associado"
        ])
        
        # Configurar larguras de coluna
        self.tabela_meios.setColumnWidth(0, 40)   # ID
        self.tabela_meios.setColumnWidth(1, 150)  # Nome
        self.tabela_meios.setColumnWidth(2, 120)  # Tipo
        self.tabela_meios.setColumnWidth(3, 180)  # Descrição
        self.tabela_meios.setColumnWidth(4, 150)  # Conta Associada
        self.tabela_meios.setColumnWidth(5, 150)  # Banco Associado
        
        # Configurar comportamento da tabela
        self.tabela_meios.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_meios.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabela_meios)
        
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
        db = DatabaseConnection()
        try:
            cursor = db.get_cursor()
            
            # Consulta SQL para buscar meios de pagamento com nome da conta associada e banco
            query = """
                SELECT mp.id, mp.nome, mp.tipo, mp.descricao, mp.conta_id, mp.ativo,
                       cd.nome as conta_nome, cd.instituicao as banco_nome
                FROM financas_pessoais.meios_pagamento mp
                LEFT JOIN financas_pessoais.conta_dimensao cd ON mp.conta_id = cd.id
                WHERE mp.ativo = 1
                ORDER BY mp.nome
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            self.tabela_meios.setRowCount(0)
            
            for row in rows:
                row_idx = self.tabela_meios.rowCount()
                self.tabela_meios.insertRow(row_idx)
                
                self.tabela_meios.setItem(row_idx, 0, QTableWidgetItem(str(row.id)))
                self.tabela_meios.setItem(row_idx, 1, QTableWidgetItem(row.nome))
                self.tabela_meios.setItem(row_idx, 2, QTableWidgetItem(row.tipo))
                self.tabela_meios.setItem(row_idx, 3, QTableWidgetItem(row.descricao or ""))
                self.tabela_meios.setItem(row_idx, 4, QTableWidgetItem(row.conta_nome or ""))
                self.tabela_meios.setItem(row_idx, 5, QTableWidgetItem(row.banco_nome or ""))
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar meios de pagamento: {e}")
        finally:
            db.close()
        
    def novo_meio_pagamento(self):
        """Abre o diálogo para criar um novo meio de pagamento."""
        dialog = MeioPagamentoDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_meio_pagamento_data()
            
            if not dados['nome']:
                QMessageBox.warning(self, "Erro", "O nome do meio de pagamento é obrigatório.")
                return
            
            # Salvar o novo meio de pagamento diretamente no banco
            db = DatabaseConnection()
            try:
                cursor = db.get_cursor()
                cursor.execute("""
                    INSERT INTO financas_pessoais.meios_pagamento 
                    (nome, tipo, descricao, conta_id, ativo)
                    VALUES (?, ?, ?, ?, 1)
                """, (dados['nome'], dados['tipo'], dados['descricao'], dados['conta_id']))
                
                db.commit()
                self.carregar_meios_pagamento()
                QMessageBox.information(self, "Sucesso", "Meio de pagamento criado com sucesso!")
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erro", f"Erro ao criar meio de pagamento: {e}")
            finally:
                db.close()
    
    def editar_meio_pagamento(self):
        """Abre o diálogo para editar o meio de pagamento selecionado."""
        selected_rows = self.tabela_meios.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um meio de pagamento para editar.")
            return
        
        # Obter o ID do meio de pagamento selecionado
        row = selected_rows[0].row()
        meio_pagamento_id = int(self.tabela_meios.item(row, 0).text())
        
        # Abrir diálogo de edição
        dialog = MeioPagamentoDialog(self, meio_pagamento_id)
        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_meio_pagamento_data()
            
            if not dados['nome']:
                QMessageBox.warning(self, "Erro", "O nome do meio de pagamento é obrigatório.")
                return
            
            # Atualizar o meio de pagamento diretamente no banco
            db = DatabaseConnection()
            try:
                cursor = db.get_cursor()
                cursor.execute("""
                    UPDATE financas_pessoais.meios_pagamento
                    SET nome = ?, tipo = ?, descricao = ?, conta_id = ?
                    WHERE id = ?
                """, (dados['nome'], dados['tipo'], dados['descricao'], dados['conta_id'], meio_pagamento_id))
                
                db.commit()
                self.carregar_meios_pagamento()
                QMessageBox.information(self, "Sucesso", "Meio de pagamento atualizado com sucesso!")
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Erro", f"Erro ao atualizar meio de pagamento: {e}")
            finally:
                db.close()
    
    def excluir_meio_pagamento(self):
        """Exclui (desativa) o meio de pagamento selecionado."""
        selected_rows = self.tabela_meios.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um meio de pagamento para excluir.")
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
        
        # Obter o ID do meio de pagamento selecionado
        row = selected_rows[0].row()
        meio_pagamento_id = int(self.tabela_meios.item(row, 0).text())
        
        # Excluir o meio de pagamento diretamente no banco
        db = DatabaseConnection()
        try:
            cursor = db.get_cursor()
            cursor.execute("UPDATE financas_pessoais.meios_pagamento SET ativo = 0 WHERE id = ?", (meio_pagamento_id,))
            
            db.commit()
            self.carregar_meios_pagamento()
            QMessageBox.information(self, "Sucesso", "Meio de pagamento excluído com sucesso!")
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Erro", f"Erro ao excluir meio de pagamento: {e}")
        finally:
            db.close()