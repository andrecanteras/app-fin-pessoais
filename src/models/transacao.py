from datetime import datetime
from decimal import Decimal
import uuid
from src.database.db_helper import get_db_connection
from src.models.conta import Conta
from src.models.categoria import Categoria
from src.models.meio_pagamento import MeioPagamento

class Transacao:
    """Classe para representar uma transação financeira."""
    
    def __init__(self, id=None, descricao=None, valor=0.0, data_transacao=None, tipo=None, 
                 categoria_id=None, conta_id=None, meio_pagamento_id=None, 
                 descricao_pagamento=None, local_transacao=None, observacao=None, 
                 data_criacao=None, transferencia_id=None, conta_destino_id=None):
        self.id = id
        self.descricao = descricao
        # Converter para Decimal para garantir consistência
        self.valor = Decimal(str(valor)) if valor is not None else Decimal('0.0')
        self.data_transacao = data_transacao if data_transacao else datetime.now().date()
        self.tipo = tipo  # 'R' para Receita, 'D' para Despesa, 'T' para Transferência
        self.categoria_id = categoria_id
        self.conta_id = conta_id
        self.meio_pagamento_id = meio_pagamento_id
        self.descricao_pagamento = descricao_pagamento
        self.local_transacao = local_transacao
        self.observacao = observacao
        self.data_criacao = data_criacao
        self.transferencia_id = transferencia_id
        self.conta_destino_id = conta_destino_id
        
        # Objetos relacionados
        self._categoria = None
        self._conta = None
        self._conta_destino = None
        self._meio_pagamento = None
    
    @property
    def categoria(self):
        """Retorna o objeto Categoria relacionado a esta transação."""
        if self._categoria is None and self.categoria_id:
            self._categoria = Categoria.buscar_por_id(self.categoria_id)
        return self._categoria
    
    @property
    def conta(self):
        """Retorna o objeto Conta relacionado a esta transação."""
        if self._conta is None and self.conta_id:
            self._conta = Conta.buscar_por_id(self.conta_id)
        return self._conta
    
    @property
    def conta_destino(self):
        """Retorna o objeto Conta de destino para transferências."""
        if self._conta_destino is None and self.conta_destino_id:
            self._conta_destino = Conta.buscar_por_id(self.conta_destino_id)
        return self._conta_destino
    
    @property
    def meio_pagamento(self):
        """Retorna o objeto MeioPagamento relacionado a esta transação."""
        if self._meio_pagamento is None and self.meio_pagamento_id:
            self._meio_pagamento = MeioPagamento.buscar_por_id(self.meio_pagamento_id)
        return self._meio_pagamento
    
    def salvar(self):
        """Salva ou atualiza uma transação no banco de dados."""
        db = None
        try:
            db = get_db_connection()
            cursor = db.get_cursor()
            schema = db.schema
            
            # Se for transferência, criar duas transações
            if self.tipo == 'T' and self.conta_destino_id:
                return self._salvar_transferencia(db, cursor, schema)
            
            if self.id is None:
                # Inserir nova transação
                cursor.execute(f"""
                    INSERT INTO {schema}.transacoes 
                    (descricao, valor, data_transacao, tipo, categoria_id, conta_id, 
                    meio_pagamento_id, descricao_pagamento, local_transacao, observacao,
                    transferencia_id, conta_destino_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (self.descricao, self.valor, self.data_transacao, self.tipo, 
                    self.categoria_id, self.conta_id, self.meio_pagamento_id,
                    self.descricao_pagamento, self.local_transacao, self.observacao,
                    self.transferencia_id, self.conta_destino_id))
                
                # Obter o ID gerado
                cursor.execute("SELECT @@IDENTITY")
                self.id = cursor.fetchone()[0]
                
                db.commit()
                
                # Atualizar saldo da conta
                if self.conta_id:
                    try:
                        conta = Conta.buscar_por_id(self.conta_id)
                        if conta:
                            conta.atualizar_saldo(self.valor, self.tipo)
                    except Exception as e:
                        print(f"Aviso: Erro ao atualizar saldo da conta: {e}")
                
                return True
            else:
                # Atualizar transação existente
                original = self._obter_transacao_original(self.id, cursor)
                
                cursor.execute(f"""
                    UPDATE {schema}.transacoes
                    SET descricao = ?, valor = ?, data_transacao = ?, tipo = ?, 
                        categoria_id = ?, conta_id = ?, meio_pagamento_id = ?,
                        descricao_pagamento = ?, local_transacao = ?, observacao = ?,
                        transferencia_id = ?, conta_destino_id = ?
                    WHERE id = ?
                """, (self.descricao, self.valor, self.data_transacao, self.tipo, 
                    self.categoria_id, self.conta_id, self.meio_pagamento_id,
                    self.descricao_pagamento, self.local_transacao, self.observacao,
                    self.transferencia_id, self.conta_destino_id, self.id))
                
                db.commit()
                
                # Atualizar saldos das contas
                try:
                    # Reverter a transação original
                    if original and original['conta_id']:
                        tipo_reverso = 'D' if original['tipo'] == 'R' else 'R'
                        conta_original = Conta.buscar_por_id(original['conta_id'])
                        if conta_original:
                            conta_original.atualizar_saldo(original['valor'], tipo_reverso)
                    
                    # Aplicar a nova transação
                    if self.conta_id:
                        conta = Conta.buscar_por_id(self.conta_id)
                        if conta:
                            conta.atualizar_saldo(self.valor, self.tipo)
                except Exception as e:
                    print(f"Aviso: Erro ao atualizar saldos das contas: {e}")
                
                return True
                
        except Exception as e:
            if db:
                db.rollback()
            print(f"Erro ao salvar transação: {e}")
            return False
        finally:
            if db:
                db.close()
    
    def _salvar_transferencia(self, db, cursor, schema):
        """Salva uma transferência como duas transações vinculadas."""
        try:
            # Gerar ID único para vincular as duas transações
            if not self.transferencia_id:
                self.transferencia_id = str(uuid.uuid4())
            
            # Transação 1: Débito na conta origem
            cursor.execute(f"""
                INSERT INTO {schema}.transacoes 
                (descricao, valor, data_transacao, tipo, categoria_id, conta_id, 
                meio_pagamento_id, descricao_pagamento, local_transacao, observacao,
                transferencia_id, conta_destino_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (f"{self.descricao} (Origem)", self.valor, self.data_transacao, 'D', 
                self.categoria_id, self.conta_id, self.meio_pagamento_id,
                self.descricao_pagamento, self.local_transacao, 
                f"Transferência para conta destino. {self.observacao or ''}".strip(),
                self.transferencia_id, self.conta_destino_id))
            
            # Obter ID da primeira transação
            cursor.execute("SELECT @@IDENTITY")
            transacao_origem_id = cursor.fetchone()[0]
            
            # Transação 2: Crédito na conta destino
            cursor.execute(f"""
                INSERT INTO {schema}.transacoes 
                (descricao, valor, data_transacao, tipo, categoria_id, conta_id, 
                meio_pagamento_id, descricao_pagamento, local_transacao, observacao,
                transferencia_id, conta_destino_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (f"{self.descricao} (Destino)", self.valor, self.data_transacao, 'R', 
                self.categoria_id, self.conta_destino_id, None,
                self.descricao_pagamento, self.local_transacao, 
                f"Transferência da conta origem. {self.observacao or ''}".strip(),
                self.transferencia_id, self.conta_id))
            
            # Obter ID da segunda transação
            cursor.execute("SELECT @@IDENTITY")
            transacao_destino_id = cursor.fetchone()[0]
            
            db.commit()
            
            # Definir o ID da transação principal como a primeira criada
            self.id = transacao_origem_id
            
            # Atualizar saldos das contas
            try:
                # Debitar da conta origem
                conta_origem = Conta.buscar_por_id(self.conta_id)
                if conta_origem:
                    conta_origem.atualizar_saldo(self.valor, 'D')
                
                # Creditar na conta destino
                conta_destino = Conta.buscar_por_id(self.conta_destino_id)
                if conta_destino:
                    conta_destino.atualizar_saldo(self.valor, 'R')
            except Exception as e:
                print(f"Aviso: Erro ao atualizar saldos das contas: {e}")
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Erro ao salvar transferência: {e}")
            return False
    
    def _obter_transacao_original(self, transacao_id, cursor=None):
        """Obtém os dados originais de uma transação."""
        close_connection = False
        db = None
        
        try:
            if cursor is None:
                db = get_db_connection()
                cursor = db.get_cursor()
                close_connection = True
                
            schema = db.schema if db else get_db_connection().schema
            cursor.execute(f"SELECT * FROM {schema}.transacoes WHERE id = ?", (transacao_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'valor': row.valor,
                    'tipo': row.tipo,
                    'conta_id': row.conta_id
                }
            return None
        except Exception as e:
            print(f"Erro ao obter transação original: {e}")
            return None
        finally:
            if close_connection and db:
                db.close()
    
    def excluir(self):
        """Exclui uma transação e atualiza o saldo da conta."""
        if self.id is None:
            return False
        
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema
            
            # Se for uma transferência, excluir ambas as transações
            if self.transferencia_id:
                cursor.execute(f"DELETE FROM {schema}.transacoes WHERE transferencia_id = ?", 
                             (self.transferencia_id,))
            else:
                cursor.execute(f"DELETE FROM {schema}.transacoes WHERE id = ?", (self.id,))
            
            db.commit()
            
            # Reverter o efeito no saldo das contas
            if self.conta_id:
                tipo_reverso = 'D' if self.tipo == 'R' else 'R'
                conta = Conta.buscar_por_id(self.conta_id)
                if conta:
                    conta.atualizar_saldo(self.valor, tipo_reverso)
            
            # Se for transferência, reverter também na conta destino
            if self.conta_destino_id and self.tipo == 'T':
                tipo_reverso = 'R' if self.tipo == 'D' else 'D'
                conta_destino = Conta.buscar_por_id(self.conta_destino_id)
                if conta_destino:
                    conta_destino.atualizar_saldo(self.valor, tipo_reverso)
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Erro ao excluir transação: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def buscar_por_id(transacao_id):
        """Busca uma transação pelo ID."""
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema
            
            cursor.execute(f"SELECT * FROM {schema}.transacoes WHERE id = ?", (transacao_id,))
            row = cursor.fetchone()
            
            if row:
                return Transacao(
                    id=row.id,
                    descricao=row.descricao,
                    valor=row.valor,
                    data_transacao=row.data_transacao,
                    tipo=row.tipo,
                    categoria_id=getattr(row, 'categoria_id', None),
                    conta_id=getattr(row, 'conta_id', None),
                    meio_pagamento_id=getattr(row, 'meio_pagamento_id', None),
                    descricao_pagamento=getattr(row, 'descricao_pagamento', None),
                    local_transacao=getattr(row, 'local_transacao', None),
                    observacao=getattr(row, 'observacao', None),
                    data_criacao=getattr(row, 'data_criacao', None),
                    transferencia_id=getattr(row, 'transferencia_id', None),
                    conta_destino_id=getattr(row, 'conta_destino_id', None)
                )
            return None
            
        except Exception as e:
            print(f"Erro ao buscar transação: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def listar_todas(filtros=None):
        """Lista todas as transações com opções de filtro."""
        db = get_db_connection()
        transacoes = []
        
        try:
            cursor = db.get_cursor()
            schema = db.schema
            
            query = f"SELECT * FROM {schema}.transacoes WHERE 1=1"
            params = []
            
            if filtros:
                if 'data_inicio' in filtros and filtros['data_inicio']:
                    query += " AND data_transacao >= ?"
                    params.append(filtros['data_inicio'])
                
                if 'data_fim' in filtros and filtros['data_fim']:
                    query += " AND data_transacao <= ?"
                    params.append(filtros['data_fim'])
                
                if 'tipo' in filtros and filtros['tipo']:
                    query += " AND tipo = ?"
                    params.append(filtros['tipo'])
                
                if 'categoria_id' in filtros and filtros['categoria_id']:
                    query += " AND categoria_id = ?"
                    params.append(filtros['categoria_id'])
                
                if 'conta_id' in filtros and filtros['conta_id']:
                    query += " AND conta_id = ?"
                    params.append(filtros['conta_id'])
                
                if 'meio_pagamento_id' in filtros and filtros['meio_pagamento_id']:
                    query += " AND meio_pagamento_id = ?"
                    params.append(filtros['meio_pagamento_id'])
                
                if 'local_transacao' in filtros and filtros['local_transacao']:
                    query += " AND local_transacao LIKE ?"
                    params.append(f"%{filtros['local_transacao']}%")
            
            # Ordenação padrão por data mais recente
            ordenacao = "data_transacao DESC"
            if filtros and 'ordenacao' in filtros and filtros['ordenacao']:
                ordenacao = filtros['ordenacao']
            
            query += f" ORDER BY {ordenacao}"
            
            # Limite de registros
            if filtros and 'limite' in filtros and filtros['limite']:
                query += f" OFFSET 0 ROWS FETCH NEXT {filtros['limite']} ROWS ONLY"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            for row in rows:
                transacao = Transacao(
                    id=row.id,
                    descricao=row.descricao,
                    valor=row.valor,
                    data_transacao=row.data_transacao,
                    tipo=row.tipo,
                    categoria_id=getattr(row, 'categoria_id', None),
                    conta_id=getattr(row, 'conta_id', None),
                    meio_pagamento_id=getattr(row, 'meio_pagamento_id', None),
                    descricao_pagamento=getattr(row, 'descricao_pagamento', None),
                    local_transacao=getattr(row, 'local_transacao', None),
                    observacao=getattr(row, 'observacao', None),
                    data_criacao=getattr(row, 'data_criacao', None),
                    transferencia_id=getattr(row, 'transferencia_id', None),
                    conta_destino_id=getattr(row, 'conta_destino_id', None)
                )
                transacoes.append(transacao)
            
            return transacoes
            
        except Exception as e:
            print(f"Erro ao listar transações: {e}")
            return []
        finally:
            db.close()