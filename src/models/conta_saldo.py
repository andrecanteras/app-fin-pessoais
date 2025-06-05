"""
Classe para representar os dados financeiros de uma conta bancária.
"""
from decimal import Decimal
from src.database.db_helper import get_db_connection

class ContaSaldo:
    """Classe para representar os dados financeiros de uma conta bancária."""
    
    def __init__(self, id=None, conta_dimensao_id=None, saldo_inicial=0.0, 
                 saldo_atual=None, data_criacao=None):
        self.id = id
        self.conta_dimensao_id = conta_dimensao_id
        # Converter para Decimal para garantir consistência
        self.saldo_inicial = Decimal(str(saldo_inicial)) if saldo_inicial is not None else Decimal('0.0')
        self.saldo_atual = Decimal(str(saldo_atual)) if saldo_atual is not None else self.saldo_inicial
        self.data_criacao = data_criacao
    
    def salvar(self):
        """Salva ou atualiza os dados de saldo da conta no banco de dados."""
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema  # Obter o esquema atual
            
            if self.id is None:
                # Inserir novo saldo
                cursor.execute(f"""
                    INSERT INTO {schema}.conta_saldos 
                    (conta_dimensao_id, saldo_inicial, saldo_atual)
                    VALUES (?, ?, ?)
                """, (self.conta_dimensao_id, self.saldo_inicial, self.saldo_atual))
                
                # Obter o ID gerado
                cursor.execute("SELECT @@IDENTITY")
                self.id = cursor.fetchone()[0]
            else:
                # Atualizar saldo existente
                cursor.execute(f"""
                    UPDATE {schema}.conta_saldos
                    SET saldo_inicial = ?, saldo_atual = ?
                    WHERE id = ?
                """, (self.saldo_inicial, self.saldo_atual, self.id))
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Erro ao salvar saldo da conta: {e}")
            return False
        finally:
            db.close()
    
    def atualizar_saldo(self, valor, tipo):
        """Atualiza o saldo da conta com base no tipo de transação."""
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema  # Obter o esquema atual
            
            # Calcular novo saldo
            if tipo == 'R':  # Receita
                novo_saldo = self.saldo_atual + valor
            else:  # Despesa
                novo_saldo = self.saldo_atual - valor
            
            # Atualizar saldo no banco de dados
            cursor.execute(f"""
                UPDATE {schema}.conta_saldos 
                SET saldo_atual = ? 
                WHERE id = ?
            """, (novo_saldo, self.id))
            
            db.commit()
            
            # Atualizar o objeto
            self.saldo_atual = novo_saldo
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Erro ao atualizar saldo: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def buscar_por_id(saldo_id):
        """Busca um saldo de conta pelo ID."""
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema  # Obter o esquema atual
            
            cursor.execute(f"""
                SELECT id, conta_dimensao_id, saldo_inicial, saldo_atual, data_criacao
                FROM {schema}.conta_saldos
                WHERE id = ?
            """, (saldo_id,))
            
            row = cursor.fetchone()
            
            if row:
                return ContaSaldo(
                    id=row.id,
                    conta_dimensao_id=row.conta_dimensao_id,
                    saldo_inicial=row.saldo_inicial,
                    saldo_atual=row.saldo_atual,
                    data_criacao=row.data_criacao
                )
            return None
            
        except Exception as e:
            print(f"Erro ao buscar saldo da conta: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def buscar_por_dimensao_id(dimensao_id):
        """Busca um saldo de conta pelo ID da dimensão."""
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema  # Obter o esquema atual
            
            cursor.execute(f"""
                SELECT id, conta_dimensao_id, saldo_inicial, saldo_atual, data_criacao
                FROM {schema}.conta_saldos
                WHERE conta_dimensao_id = ?
            """, (dimensao_id,))
            
            row = cursor.fetchone()
            
            if row:
                return ContaSaldo(
                    id=row.id,
                    conta_dimensao_id=row.conta_dimensao_id,
                    saldo_inicial=row.saldo_inicial,
                    saldo_atual=row.saldo_atual,
                    data_criacao=row.data_criacao
                )
            return None
            
        except Exception as e:
            print(f"Erro ao buscar saldo da conta: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def obter_saldo_total(apenas_ativas=True):
        """Retorna o saldo total de todas as contas ativas."""
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema  # Obter o esquema atual
            
            query = f"""
                SELECT SUM(s.saldo_atual) 
                FROM {schema}.conta_saldos s
            """
            
            if apenas_ativas:
                query += f"""
                    JOIN {schema}.conta_dimensao d ON s.conta_dimensao_id = d.id
                    WHERE d.ativo = 1
                """
            
            cursor.execute(query)
            row = cursor.fetchone()
            return Decimal(row[0] or 0)
        except Exception as e:
            print(f"Erro ao obter saldo total: {e}")
            return Decimal('0')
        finally:
            db.close()