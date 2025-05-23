"""
Interface gráfica para gestão de categorias.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                            QMessageBox, QDialog, QFormLayout, QComboBox, 
                            QDialogButtonBox, QHeaderView, QTextEdit, QTreeWidget,
                            QTreeWidgetItem, QCheckBox, QGroupBox, QRadioButton,
                            QTabWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from src.models.categoria import Categoria

class CategoriaDialog(QDialog):
    """Diálogo para criar ou editar uma categoria."""
    
    def __init__(self, parent=None, categoria=None, categorias_pais=None):
        super().__init__(parent)
        self.categoria = categoria
        self.categorias_pais = categorias_pais or []
        self.setWindowTitle("Nova Categoria" if categoria is None else "Editar Categoria")
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QFormLayout(self)
        
        # Campos do formulário
        self.nome_edit = QLineEdit(self)
        if self.categoria:
            self.nome_edit.setText(self.categoria.nome)
        
        # Tipo (Receita ou Despesa)
        self.tipo_group = QGroupBox("Tipo")
        tipo_layout = QHBoxLayout()
        self.receita_radio = QRadioButton("Receita")
        self.despesa_radio = QRadioButton("Despesa")
        tipo_layout.addWidget(self.receita_radio)
        tipo_layout.addWidget(self.despesa_radio)
        self.tipo_group.setLayout(tipo_layout)
        
        if self.categoria:
            if self.categoria.tipo == 'R':
                self.receita_radio.setChecked(True)
            else:
                self.despesa_radio.setChecked(True)
        else:
            self.despesa_radio.setChecked(True)  # Padrão
        
        # Descrição
        self.descricao_edit = QTextEdit(self)
        self.descricao_edit.setMaximumHeight(80)
        if self.categoria and self.categoria.descricao:
            self.descricao_edit.setText(self.categoria.descricao)
        
        # Categoria pai
        self.tem_pai_check = QCheckBox("Esta é uma subcategoria")
        self.tem_pai_check.stateChanged.connect(self.toggle_categoria_pai)
        
        self.categoria_pai_combo = QComboBox(self)
        self.categoria_pai_combo.setEnabled(False)
        
        # Preencher combo de categorias pais
        self.categoria_pai_combo.addItem("Selecione uma categoria pai", None)
        for cat_pai in self.categorias_pais:
            self.categoria_pai_combo.addItem(cat_pai.nome, cat_pai.id)
        
        # Se for edição e tiver categoria pai, selecionar
        if self.categoria and self.categoria.categoria_pai_id:
            self.tem_pai_check.setChecked(True)
            index = self.categoria_pai_combo.findData(self.categoria.categoria_pai_id)
            if index >= 0:
                self.categoria_pai_combo.setCurrentIndex(index)
        
        # Adicionar campos ao layout
        layout.addRow("Nome:", self.nome_edit)
        layout.addRow(self.tipo_group)
        layout.addRow("Descrição:", self.descricao_edit)
        layout.addRow(self.tem_pai_check)
        layout.addRow("Categoria Pai:", self.categoria_pai_combo)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def toggle_categoria_pai(self, state):
        """Habilita/desabilita o combo de categoria pai."""
        self.categoria_pai_combo.setEnabled(state == Qt.Checked)
        if state != Qt.Checked:
            self.categoria_pai_combo.setCurrentIndex(0)
    
    def get_categoria_data(self):
        """Retorna os dados da categoria do formulário."""
        nome = self.nome_edit.text().strip()
        tipo = 'R' if self.receita_radio.isChecked() else 'D'
        descricao = self.descricao_edit.toPlainText().strip() or None
        
        categoria_pai_id = None
        nivel = 1
        
        if self.tem_pai_check.isChecked():
            categoria_pai_id = self.categoria_pai_combo.currentData()
            if categoria_pai_id:
                # Buscar nível da categoria pai
                for cat_pai in self.categorias_pais:
                    if cat_pai.id == categoria_pai_id:
                        nivel = cat_pai.nivel + 1
                        break
        
        return {
            'nome': nome,
            'tipo': tipo,
            'descricao': descricao,
            'categoria_pai_id': categoria_pai_id,
            'nivel': nivel
        }

class CategoriesView(QWidget):
    """Widget para gestão de categorias."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestão de Categorias")
        self.setup_ui()
        self.carregar_categorias()
        
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
        
        # Checkbox para mostrar apenas ativos
        self.apenas_ativos_check = QCheckBox("Apenas categorias ativas")
        self.apenas_ativos_check.setChecked(True)
        filtros_layout.addWidget(self.apenas_ativos_check)
        
        # Botão para aplicar filtros
        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.clicked.connect(self.carregar_categorias)
        filtros_layout.addWidget(self.btn_filtrar)
        
        filtros_layout.addStretch()
        layout.addLayout(filtros_layout)
        
        # Abas para diferentes visualizações
        self.tabs = QTabWidget()
        
        # Tab 1: Lista de categorias
        self.tab_lista = QWidget()
        tab_lista_layout = QVBoxLayout(self.tab_lista)
        
        # Tabela de categorias
        self.tabela_categorias = QTableWidget(0, 5)
        self.tabela_categorias.setHorizontalHeaderLabels(["ID", "Nome", "Tipo", "Nível", "Categoria Pai"])
        self.tabela_categorias.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela_categorias.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_categorias.setEditTriggers(QTableWidget.NoEditTriggers)
        tab_lista_layout.addWidget(self.tabela_categorias)
        
        self.tabs.addTab(self.tab_lista, "Lista")
        
        # Tab 2: Árvore de categorias
        self.tab_arvore = QWidget()
        tab_arvore_layout = QVBoxLayout(self.tab_arvore)
        
        self.arvore_categorias = QTreeWidget()
        self.arvore_categorias.setHeaderLabels(["Nome", "Tipo", "ID"])
        self.arvore_categorias.setColumnWidth(0, 300)
        tab_arvore_layout.addWidget(self.arvore_categorias)
        
        self.tabs.addTab(self.tab_arvore, "Árvore")
        
        layout.addWidget(self.tabs)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.btn_nova = QPushButton("Nova Categoria")
        self.btn_nova.clicked.connect(self.nova_categoria)
        btn_layout.addWidget(self.btn_nova)
        
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.clicked.connect(self.editar_categoria)
        btn_layout.addWidget(self.btn_editar)
        
        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.clicked.connect(self.excluir_categoria)
        btn_layout.addWidget(self.btn_excluir)
        
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar_categorias)
        btn_layout.addWidget(self.btn_atualizar)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def carregar_categorias(self):
        """Carrega as categorias do banco de dados e exibe na interface."""
        tipo = self.tipo_combo.currentData()
        apenas_ativas = self.apenas_ativos_check.isChecked()
        
        # Carregar todas as categorias para uso interno
        self.todas_categorias = Categoria.listar_todas(apenas_ativas=False)
        
        # Filtrar categorias para exibição
        categorias = Categoria.listar_todas(apenas_ativas=apenas_ativas, tipo=tipo)
        
        # Atualizar tabela
        self.tabela_categorias.setRowCount(0)
        
        for categoria in categorias:
            row = self.tabela_categorias.rowCount()
            self.tabela_categorias.insertRow(row)
            
            self.tabela_categorias.setItem(row, 0, QTableWidgetItem(str(categoria.id)))
            self.tabela_categorias.setItem(row, 1, QTableWidgetItem(categoria.nome))
            self.tabela_categorias.setItem(row, 2, QTableWidgetItem("Receita" if categoria.tipo == 'R' else "Despesa"))
            self.tabela_categorias.setItem(row, 3, QTableWidgetItem(str(categoria.nivel)))
            
            # Buscar nome da categoria pai
            categoria_pai_nome = "N/A"
            if categoria.categoria_pai_id:
                for cat in self.todas_categorias:
                    if cat.id == categoria.categoria_pai_id:
                        categoria_pai_nome = cat.nome
                        break
            
            self.tabela_categorias.setItem(row, 4, QTableWidgetItem(categoria_pai_nome))
        
        # Atualizar árvore
        self.atualizar_arvore_categorias(tipo, apenas_ativas)
    
    def atualizar_arvore_categorias(self, tipo=None, apenas_ativas=True):
        """Atualiza a árvore de categorias."""
        self.arvore_categorias.clear()
        
        # Obter categorias principais
        categorias_principais = Categoria.obter_categorias_principais(
            tipo=tipo, 
            apenas_ativas=apenas_ativas
        )
        
        # Função recursiva para adicionar itens à árvore
        def adicionar_subcategorias(parent_item, categoria_pai_id):
            subcategorias = Categoria.obter_subcategorias(
                categoria_pai_id=categoria_pai_id,
                apenas_ativas=apenas_ativas
            )
            
            # Filtrar por tipo manualmente
            if tipo:
                subcategorias = [s for s in subcategorias if s.tipo == tipo]
            
            for subcategoria in subcategorias:
                item = QTreeWidgetItem(parent_item)
                item.setText(0, subcategoria.nome)
                item.setText(1, "Receita" if subcategoria.tipo == 'R' else "Despesa")
                item.setText(2, str(subcategoria.id))
                item.setData(0, Qt.UserRole, subcategoria.id)
                
                # Adicionar subcategorias recursivamente
                adicionar_subcategorias(item, subcategoria.id)
        
        # Adicionar categorias principais
        for categoria in categorias_principais:
            item = QTreeWidgetItem(self.arvore_categorias)
            item.setText(0, categoria.nome)
            item.setText(1, "Receita" if categoria.tipo == 'R' else "Despesa")
            item.setText(2, str(categoria.id))
            item.setData(0, Qt.UserRole, categoria.id)
            
            # Adicionar subcategorias
            adicionar_subcategorias(item, categoria.id)
        
        # Expandir todos os itens
        self.arvore_categorias.expandAll()
    
    def nova_categoria(self):
        """Abre o diálogo para criar uma nova categoria."""
        # Filtrar categorias pais pelo tipo selecionado
        tipo = self.tipo_combo.currentData()
        categorias_pais = [c for c in self.todas_categorias if not tipo or c.tipo == tipo]
        
        dialog = CategoriaDialog(self, categorias_pais=categorias_pais)
        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_categoria_data()
            
            if not dados['nome']:
                QMessageBox.warning(self, "Erro", "O nome da categoria é obrigatório.")
                return
            
            # Criar e salvar a nova categoria
            categoria = Categoria(
                nome=dados['nome'],
                tipo=dados['tipo'],
                descricao=dados['descricao'],
                categoria_pai_id=dados['categoria_pai_id'],
                nivel=dados['nivel']
            )
            
            if categoria.salvar():
                self.carregar_categorias()
                QMessageBox.information(self, "Sucesso", "Categoria criada com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao criar categoria.")
    
    def editar_categoria(self):
        """Abre o diálogo para editar a categoria selecionada."""
        categoria_id = self.obter_categoria_selecionada_id()
        if not categoria_id:
            QMessageBox.warning(self, "Aviso", "Selecione uma categoria para editar.")
            return
        
        # Buscar a categoria no banco de dados
        categoria = Categoria.buscar_por_id(categoria_id)
        if not categoria:
            QMessageBox.critical(self, "Erro", "Categoria não encontrada.")
            return
        
        # Filtrar categorias pais pelo tipo da categoria selecionada
        categorias_pais = [c for c in self.todas_categorias if c.tipo == categoria.tipo and c.id != categoria.id]
        
        # Abrir diálogo de edição
        dialog = CategoriaDialog(self, categoria, categorias_pais)
        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_categoria_data()
            
            if not dados['nome']:
                QMessageBox.warning(self, "Erro", "O nome da categoria é obrigatório.")
                return
            
            # Atualizar dados da categoria
            categoria.nome = dados['nome']
            categoria.tipo = dados['tipo']
            categoria.descricao = dados['descricao']
            categoria.categoria_pai_id = dados['categoria_pai_id']
            categoria.nivel = dados['nivel']
            
            if categoria.salvar():
                self.carregar_categorias()
                QMessageBox.information(self, "Sucesso", "Categoria atualizada com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao atualizar categoria.")
    
    def excluir_categoria(self):
        """Exclui (desativa) a categoria selecionada."""
        categoria_id = self.obter_categoria_selecionada_id()
        if not categoria_id:
            QMessageBox.warning(self, "Aviso", "Selecione uma categoria para excluir.")
            return
        
        # Buscar a categoria no banco de dados
        categoria = Categoria.buscar_por_id(categoria_id)
        if not categoria:
            QMessageBox.critical(self, "Erro", "Categoria não encontrada.")
            return
        
        # Verificar se tem subcategorias
        subcategorias = Categoria.obter_subcategorias(categoria_id)
        if subcategorias:
            aviso = f"ATENÇÃO: Esta categoria possui {len(subcategorias)} subcategoria(s).\n"
            aviso += "Excluir esta categoria não excluirá suas subcategorias, mas elas ficarão órfãs."
            QMessageBox.warning(self, "Aviso", aviso)
        
        # Confirmar exclusão
        resposta = QMessageBox.question(
            self, 
            "Confirmar Exclusão", 
            "Tem certeza que deseja excluir esta categoria? Esta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.No:
            return
        
        # Excluir a categoria
        if categoria.excluir():
            self.carregar_categorias()
            QMessageBox.information(self, "Sucesso", "Categoria excluída com sucesso!")
        else:
            QMessageBox.critical(self, "Erro", "Erro ao excluir categoria.")
    
    def obter_categoria_selecionada_id(self):
        """Obtém o ID da categoria selecionada na interface atual."""
        if self.tabs.currentIndex() == 0:  # Tab Lista
            selected_rows = self.tabela_categorias.selectedItems()
            if not selected_rows:
                return None
            
            row = selected_rows[0].row()
            return int(self.tabela_categorias.item(row, 0).text())
        else:  # Tab Árvore
            selected_items = self.arvore_categorias.selectedItems()
            if not selected_items:
                return None
            
            return int(selected_items[0].text(2))