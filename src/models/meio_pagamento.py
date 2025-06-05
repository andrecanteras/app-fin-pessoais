from decimal import Decimal
from src.database.db_helper import get_db_connection
from src.models.conta import Conta
from src.models.conta_dimensao import ContaDimensao

class MeioPagamento:
    """Classe para representar um meio de pagamento."""
    
    def __init__(self, id=None, nome=None, descricao=None, conta_id=None, 
                 tipo=None, data_criacao=None, ativo=True):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.conta_id = conta_id
        self.tipo = tipo  # Cartão de Crédito, Cartão de Débito, PIX, Dinheiro, Transferência, etc.
        self.data_criacao = data_criacao
        self.ativo = ativo
        
        # Objeto relacionado
        self._conta = None
    
    @property
    def conta(self):
        """Retorna o objeto Conta relacionado a este meio de pagamento."""
        if self._conta is None and self.conta_id:
            # Primeiro tenta buscar usando a classe Conta (que é a fachada)
            self._conta = Conta.buscar_por_id(self.conta_id)
            # Se não encontrar, tenta buscar diretamente na dimensão
            if self._conta is None:
                conta_dimensao = ContaDimensao.buscar_por_id(self.conta_id)
                if conta_dimensao:
                    # Cria um objeto Conta apenas com os dados da dimensão
                    self._conta = Conta(
                        id=conta_dimensao.id,
                        nome=conta_dimensao.nome,
                        tipo=conta_dimensao.tipo,
                        banco=conta_dimensao.instituicao,
                        agencia=conta_dimensao.agencia,
                        conta_contabil=conta_dimensao.conta_contabil,
                        numero_banco=conta_dimensao.numero_banco,
                        titular=conta_dimensao.titular,
                        nome_gerente=conta_dimensao.nome_gerente,
                        contato_gerente=conta_dimensao.contato_gerente,
                        data_criacao=conta_dimensao.data_criacao,
                        ativo=conta_dimensao.ativo
                    )
        return self._conta
    
    def salvar(self):
        """Salva ou atualiza um meio de pagamento no banco de dados."""
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema  # Obter o esquema atual
            
            # Verificar se a conta_id referencia uma conta_dimensao válida
            if self.conta_id:
                # Verificar se a conta existe na tabela contas_dimensao
                conta_dimensao = ContaDimensao.buscar_por_id(self.conta_id)
                if not conta_dimensao:
                    print(f"Erro: Conta com ID {self.conta_id} não encontrada na tabela contas_dimensao")
                    return False
            
            if self.id is None:
                # Inserir novo meio de pagamento
                cursor.execute(f"""
                    INSERT INTO {schema}.meios_pagamento 
                    (nome, descricao, conta_id, tipo, ativo)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.nome, self.descricao, self.conta_id, self.tipo, self.ativo))
                
                # Obter o ID gerado
                cursor.execute("SELECT @@IDENTITY")
                self.id = cursor.fetchone()[0]
            else:
                # Atualizar meio de pagamento existente
                cursor.execute(f"""
                    UPDATE {schema}.meios_pagamento
                    SET nome = ?, descricao = ?, conta_id = ?, tipo = ?, ativo = ?
                    WHERE id = ?
                """, (self.nome, self.descricao, self.conta_id, self.tipo, self.ativo, self.id))
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Erro ao salvar meio de pagamento: {e}")
            return False
        finally:
            db.close()
    
    def excluir(self):
        """Marca um meio de pagamento como inativo (exclusão lógica)."""
        if self.id is None:
            return False
        
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema  # Obter o esquema atual
            
            cursor.execute(f"UPDATE {schema}.meios_pagamento SET ativo = 0 WHERE id = ?", (self.id,))
            db.commit()
            self.ativo = False
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Erro ao excluir meio de pagamento: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def buscar_por_id(meio_pagamento_id):
        """Busca um meio de pagamento pelo ID."""
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema  # Obter o esquema atual
            
            cursor.execute(f"SELECT * FROM {schema}.meios_pagamento WHERE id = ?", (meio_pagamento_id,))
            row = cursor.fetchone()
            
            if row:
                return MeioPagamento(
                    id=row.id,
                    nome=row.nome,
                    descricao=row.descricao,
                    conta_id=row.conta_id,
                    tipo=row.tipo,
                    data_criacao=row.data_criacao,
                    ativo=row.ativo
                )
            return None
            
        except Exception as e:
            print(f"Erro ao buscar meio de pagamento: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def listar_todos(apenas_ativos=True, conta_id=None):
        """Lista todos os meios de pagamento, opcionalmente filtrando por conta."""
        db = get_db_connection()
        meios_pagamento = []
        
        try:
            cursor = db.get_cursor()
            schema = db.schema  # Obter o esquema atual
            
            query = f"SELECT * FROM {schema}.meios_pagamento WHERE 1=1"
            params = []
            
            if apenas_ativos:
                query += " AND ativo = 1"
            
            if conta_id:
                query += " AND (conta_id = ? OR conta_id IS NULL)"
                params.append(conta_id)
            
            query += " ORDER BY nome"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            for row in rows:
                meio_pagamento = MeioPagamento(
                    id=row.id,
                    nome=row.nome,
                    descricao=row.descricao,
                    conta_id=row.conta_id,
                    tipo=row.tipo,
                    data_criacao=row.data_criacao,
                    ativo=row.ativo
                )
                meios_pagamento.append(meio_pagamento)
            
            return meios_pagamento
            
        except Exception as e:
            print(f"Erro ao listar meios de pagamento: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def listar_por_tipo(tipo, apenas_ativos=True):
        """Lista meios de pagamento por tipo."""
        db = get_db_connection()
        meios_pagamento = []
        
        try:
            cursor = db.get_cursor()
            schema = db.schema  # Obter o esquema atual
            
            query = f"SELECT * FROM {schema}.meios_pagamento WHERE tipo = ?"
            params = [tipo]
            
            if apenas_ativos:
                query += " AND ativo = 1"
            
            query += " ORDER BY nome"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            for row in rows:
                meio_pagamento = MeioPagamento(
                    id=row.id,
                    nome=row.nome,
                    descricao=row.descricao,
                    conta_id=row.conta_id,
                    tipo=row.tipo,
                    data_criacao=row.data_criacao,
                    ativo=row.ativo
                )
                meios_pagamento.append(meio_pagamento)
            
            return meios_pagamento
            
        except Exception as e:
            print(f"Erro ao listar meios de pagamento por tipo: {e}")
            return []
        finally:
            db.close()