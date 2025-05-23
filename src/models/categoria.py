from src.database.connection import DatabaseConnection

class Categoria:
    """Classe para representar uma categoria de receita ou despesa com suporte a hierarquia."""
    
    def __init__(self, id=None, nome=None, tipo=None, descricao=None, 
                 categoria_pai_id=None, nivel=1, data_criacao=None, ativo=True):
        self.id = id
        self.nome = nome
        self.tipo = tipo  # 'R' para Receita, 'D' para Despesa
        self.descricao = descricao
        self.categoria_pai_id = categoria_pai_id  # ID da categoria pai (se for subcategoria)
        self.nivel = nivel  # Nível na hierarquia (1 para categorias principais)
        self.data_criacao = data_criacao
        self.ativo = ativo
        self.db = DatabaseConnection()
    
    def salvar(self):
        """Salva ou atualiza uma categoria no banco de dados."""
        try:
            cursor = self.db.get_cursor()
            
            if self.id is None:
                # Inserir nova categoria
                cursor.execute("""
                    INSERT INTO financas_pessoais.categorias 
                    (nome, tipo, descricao, categoria_pai_id, nivel, ativo)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (self.nome, self.tipo, self.descricao, 
                      self.categoria_pai_id, self.nivel, self.ativo))
                
                # Obter o ID gerado
                cursor.execute("SELECT @@IDENTITY")
                self.id = cursor.fetchone()[0]
            else:
                # Atualizar categoria existente
                cursor.execute("""
                    UPDATE financas_pessoais.categorias
                    SET nome = ?, tipo = ?, descricao = ?, 
                        categoria_pai_id = ?, nivel = ?, ativo = ?
                    WHERE id = ?
                """, (self.nome, self.tipo, self.descricao, 
                      self.categoria_pai_id, self.nivel, self.ativo, self.id))
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao salvar categoria: {e}")
            return False
    
    def excluir(self):
        """Marca uma categoria como inativa (exclusão lógica)."""
        if self.id is None:
            return False
        
        try:
            cursor = self.db.get_cursor()
            cursor.execute("UPDATE financas_pessoais.categorias SET ativo = 0 WHERE id = ?", (self.id,))
            self.db.commit()
            self.ativo = False
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao excluir categoria: {e}")
            return False
    
    @staticmethod
    def buscar_por_id(categoria_id):
        """Busca uma categoria pelo ID."""
        db = DatabaseConnection()
        try:
            cursor = db.get_cursor()
            cursor.execute("SELECT * FROM financas_pessoais.categorias WHERE id = ?", (categoria_id,))
            row = cursor.fetchone()
            
            if row:
                return Categoria(
                    id=row.id,
                    nome=row.nome,
                    tipo=row.tipo,
                    descricao=row.descricao,
                    categoria_pai_id=row.categoria_pai_id,
                    nivel=row.nivel,
                    data_criacao=row.data_criacao,
                    ativo=row.ativo
                )
            return None
            
        except Exception as e:
            print(f"Erro ao buscar categoria: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def listar_todas(apenas_ativas=True, tipo=None):
        """Lista todas as categorias, opcionalmente filtrando por tipo."""
        db = DatabaseConnection()
        categorias = []
        
        try:
            cursor = db.get_cursor()
            query = "SELECT * FROM financas_pessoais.categorias WHERE 1=1"
            params = []
            
            if apenas_ativas:
                query += " AND ativo = 1"
            
            if tipo:
                query += " AND tipo = ?"
                params.append(tipo)
            
            query += " ORDER BY nome"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            for row in rows:
                categoria = Categoria(
                    id=row.id,
                    nome=row.nome,
                    tipo=row.tipo,
                    descricao=row.descricao,
                    categoria_pai_id=row.categoria_pai_id,
                    nivel=row.nivel,
                    data_criacao=row.data_criacao,
                    ativo=row.ativo
                )
                categorias.append(categoria)
            
            return categorias
            
        except Exception as e:
            print(f"Erro ao listar categorias: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def obter_subcategorias(categoria_pai_id, apenas_ativas=True):
        """Obtém todas as subcategorias de uma categoria específica."""
        db = DatabaseConnection()
        categorias = []
        
        try:
            cursor = db.get_cursor()
            query = """
                SELECT * FROM financas_pessoais.categorias 
                WHERE categoria_pai_id = ?
            """
            params = [categoria_pai_id]
            
            if apenas_ativas:
                query += " AND ativo = 1"
            
            query += " ORDER BY nome"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            for row in rows:
                categoria = Categoria(
                    id=row.id,
                    nome=row.nome,
                    tipo=row.tipo,
                    descricao=row.descricao,
                    categoria_pai_id=row.categoria_pai_id,
                    nivel=row.nivel,
                    data_criacao=row.data_criacao,
                    ativo=row.ativo
                )
                categorias.append(categoria)
            
            return categorias
            
        except Exception as e:
            print(f"Erro ao listar subcategorias: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def obter_categorias_principais(tipo=None, apenas_ativas=True):
        """Obtém todas as categorias de nível superior (sem categoria pai)."""
        db = DatabaseConnection()
        categorias = []
        
        try:
            cursor = db.get_cursor()
            query = """
                SELECT * FROM financas_pessoais.categorias 
                WHERE categoria_pai_id IS NULL
            """
            params = []
            
            if tipo:
                query += " AND tipo = ?"
                params.append(tipo)
            
            if apenas_ativas:
                query += " AND ativo = 1"
            
            query += " ORDER BY nome"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            for row in rows:
                categoria = Categoria(
                    id=row.id,
                    nome=row.nome,
                    tipo=row.tipo,
                    descricao=row.descricao,
                    categoria_pai_id=row.categoria_pai_id,
                    nivel=row.nivel,
                    data_criacao=row.data_criacao,
                    ativo=row.ativo
                )
                categorias.append(categoria)
            
            return categorias
            
        except Exception as e:
            print(f"Erro ao listar categorias principais: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def obter_caminho_hierarquico(categoria_id):
        """Obtém o caminho hierárquico completo de uma categoria (ex: 'Alimentação > Restaurantes > Fast Food')."""
        db = DatabaseConnection()
        caminho = []
        
        try:
            # Função recursiva para obter categorias pai
            def obter_categoria_e_pais(cat_id):
                if not cat_id:
                    return []
                
                cursor = db.get_cursor()
                cursor.execute("SELECT * FROM financas_pessoais.categorias WHERE id = ?", (cat_id,))
                row = cursor.fetchone()
                
                if not row:
                    return []
                
                categoria = Categoria(
                    id=row.id,
                    nome=row.nome,
                    tipo=row.tipo,
                    descricao=row.descricao,
                    categoria_pai_id=row.categoria_pai_id,
                    nivel=row.nivel,
                    data_criacao=row.data_criacao,
                    ativo=row.ativo
                )
                
                # Obter categorias pai recursivamente
                pais = obter_categoria_e_pais(categoria.categoria_pai_id)
                return pais + [categoria]
            
            # Obter o caminho completo
            categorias = obter_categoria_e_pais(categoria_id)
            caminho = [categoria.nome for categoria in categorias]
            
            return caminho
            
        except Exception as e:
            print(f"Erro ao obter caminho hierárquico: {e}")
            return []
        finally:
            db.close()