from datetime import datetime
from decimal import Decimal
from src.database.connection import DatabaseConnection
from src.models.conta import Conta
from src.models.categoria import Categoria
from src.models.meio_pagamento import MeioPagamento

class Transacao:
    """Classe para representar uma transação financeira."""
    
    def __init__(self, id=None, descricao=None, valor=0.0, data_transacao=None, tipo=None, 
                 categoria_id=None, conta_id=None, meio_pagamento_id=None, 
                 descricao_pagamento=None, local_transacao=None, observacao=None, data_criacao=None):
        self.id = id
        self.descricao = descricao
        # Converter para Decimal para garantir consistência
        self.valor = Decimal(str(valor)) if valor is not None else Decimal('0.0')
        self.data_transacao = data_transacao if data_transacao else datetime.now().date()
        self.tipo = tipo  # 'R' para Receita, 'D' para Despesa
        self.categoria_id = categoria_id
        self.conta_id = conta_id
        self.meio_pagamento_id = meio_pagamento_id
        self.descricao_pagamento = descricao_pagamento
        self.local_transacao = local_transacao
        self.observacao = observacao
        self.data_criacao = data_criacao
        
        # Objetos relacionados
        self._categoria = None
        self._conta = None
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
    def meio_pagamento(self):
        """Retorna o objeto MeioPagamento relacionado a esta transação."""
        if self._meio_pagamento is None and self.meio_pagamento_id:
            self._meio_pagamento = MeioPagamento.buscar_por_id(self.meio_pagamento_id)
        return self._meio_pagamento
    
    def salvar(self):
        """Salva ou atualiza uma transação no banco de dados."""
        # Criar uma nova conexão para a operação principal
        db_transacao = DatabaseConnection()
        
        try:
            cursor = db_transacao.get_cursor()
            
            if self.id is None:
                # Inserir nova transação
                cursor.execute("""
                    INSERT INTO financas_pessoais.transacoes 
                    (descricao, valor, data_transacao, tipo, categoria_id, conta_id, 
                     meio_pagamento_id, descricao_pagamento, local_transacao, observacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (self.descricao, self.valor, self.data_transacao, self.tipo, 
                      self.categoria_id, self.conta_id, self.meio_pagamento_id,
                      self.descricao_pagamento, self.local_transacao, self.observacao))
                
                # Obter o ID gerado
                cursor.execute("SELECT @@IDENTITY")
                self.id = cursor.fetchone()[0]
                
                # Commit imediatamente após a inserção
                db_transacao.commit()
                
                # Atualizar o saldo da conta diretamente
                if self.conta_id:
                    self._atualizar_saldo_conta(self.conta_id, self.valor, self.tipo)
                
                return True
            else:
                # Obter a transação original para reverter o saldo
                original = self._obter_transacao_original(self.id)
                
                # Atualizar transação existente
                cursor.execute("""
                    UPDATE financas_pessoais.transacoes
                    SET descricao = ?, valor = ?, data_transacao = ?, tipo = ?, 
                        categoria_id = ?, conta_id = ?, meio_pagamento_id = ?,
                        descricao_pagamento = ?, local_transacao = ?, observacao = ?
                    WHERE id = ?
                """, (self.descricao, self.valor, self.data_transacao, self.tipo, 
                      self.categoria_id, self.conta_id, self.meio_pagamento_id,
                      self.descricao_pagamento, self.local_transacao, self.observacao, self.id))
                
                # Commit após a atualização
                db_transacao.commit()
                
                # Atualizar o saldo da conta
                if original:
                    # Reverter a transação original
                    if original['conta_id']:
                        # Se era receita, subtrai; se era despesa, adiciona
                        tipo_reverso = 'D' if original['tipo'] == 'R' else 'R'
                        self._atualizar_saldo_conta(original['conta_id'], original['valor'], tipo_reverso)
                    
                    # Aplicar a nova transação
                    if self.conta_id:
                        self._atualizar_saldo_conta(self.conta_id, self.valor, self.tipo)
                
                return True
                
        except Exception as e:
            db_transacao.rollback()
            print(f"Erro ao salvar transação: {e}")
            return False
        finally:
            db_transacao.close()
    
    def _obter_transacao_original(self, transacao_id):
        """Obtém os dados originais de uma transação."""
        db = DatabaseConnection()
        try:
            cursor = db.get_cursor()
            cursor.execute("SELECT * FROM financas_pessoais.transacoes WHERE id = ?", (transacao_id,))
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
            db.close()
    
    def _atualizar_saldo_conta(self, conta_id, valor, tipo):
        """Atualiza o saldo de uma conta."""
        db = DatabaseConnection()
        try:
            cursor = db.get_cursor()
            
            # Obter saldo atual
            cursor.execute("SELECT saldo_atual FROM financas_pessoais.contas WHERE id = ?", (conta_id,))
            row = cursor.fetchone()
            if row:
                saldo_atual = row.saldo_atual
                
                # Calcular novo saldo
                if tipo == 'R':  # Receita
                    novo_saldo = saldo_atual + valor
                else:  # Despesa
                    novo_saldo = saldo_atual - valor
                
                # Atualizar saldo
                cursor.execute("UPDATE financas_pessoais.contas SET saldo_atual = ? WHERE id = ?", 
                             (novo_saldo, conta_id))
                db.commit()
        except Exception as e:
            db.rollback()
            print(f"Erro ao atualizar saldo da conta: {e}")
        finally:
            db.close()
    
    def excluir(self):
        """Exclui uma transação e atualiza o saldo da conta."""
        if self.id is None:
            return False
        
        # Guardar informações da conta antes de qualquer operação
        conta_id = self.conta_id
        tipo = self.tipo
        valor = self.valor
        
        # Criar uma nova conexão para excluir a transação
        db_transacao = DatabaseConnection()
        try:
            cursor = db_transacao.get_cursor()
            cursor.execute("DELETE FROM financas_pessoais.transacoes WHERE id = ?", (self.id,))
            db_transacao.commit()
            
            # Depois reverter o efeito da transação no saldo da conta
            if conta_id:
                # Se era receita, subtrai; se era despesa, adiciona
                tipo_reverso = 'D' if tipo == 'R' else 'R'
                self._atualizar_saldo_conta(conta_id, valor, tipo_reverso)
            
            return True
            
        except Exception as e:
            db_transacao.rollback()
            print(f"Erro ao excluir transação: {e}")
            return False
        finally:
            db_transacao.close()
    
    @staticmethod
    def buscar_por_id(transacao_id):
        """Busca uma transação pelo ID."""
        db = DatabaseConnection()
        try:
            cursor = db.get_cursor()
            cursor.execute("SELECT * FROM financas_pessoais.transacoes WHERE id = ?", (transacao_id,))
            row = cursor.fetchone()
            
            if row:
                # Criar objeto com tratamento de campos que podem não existir
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
                    data_criacao=getattr(row, 'data_criacao', None)
                )
                return transacao
            else:
                return None
            
        except Exception as e:
            print(f"Erro ao buscar transação: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def listar_todas(filtros=None):
        """Lista todas as transações com opções de filtro.
        
        Args:
            filtros: Dicionário com opções de filtro:
                - data_inicio: Data inicial para filtrar
                - data_fim: Data final para filtrar
                - tipo: 'R' para receitas, 'D' para despesas
                - categoria_id: ID da categoria
                - conta_id: ID da conta
                - meio_pagamento_id: ID do meio de pagamento
                - local_transacao: Local da transação
                - ordenacao: Campo para ordenação
                - limite: Limite de registros
        """
        db = DatabaseConnection()
        transacoes = []
        
        try:
            cursor = db.get_cursor()
            query = "SELECT * FROM financas_pessoais.transacoes WHERE 1=1"
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
                    categoria_id=row.categoria_id,
                    conta_id=row.conta_id,
                    meio_pagamento_id=row.meio_pagamento_id,
                    descricao_pagamento=row.descricao_pagamento,
                    local_transacao=row.local_transacao,
                    observacao=row.observacao,
                    data_criacao=row.data_criacao
                )
                transacoes.append(transacao)
            
            return transacoes
            
        except Exception as e:
            print(f"Erro ao listar transações: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def obter_resumo_por_periodo(data_inicio, data_fim):
        """Obtém um resumo das transações em um período específico.
        
        Args:
            data_inicio: Data inicial do período
            data_fim: Data final do período
            
        Returns:
            Dicionário com os totais de receitas, despesas e saldo do período
        """
        db = DatabaseConnection()
        try:
            cursor = db.get_cursor()
            
            # Obter total de receitas
            cursor.execute("""
                SELECT COALESCE(SUM(valor), 0) AS total
                FROM financas_pessoais.transacoes
                WHERE tipo = 'R' AND data_transacao BETWEEN ? AND ?
            """, (data_inicio, data_fim))
            total_receitas = cursor.fetchone().total or Decimal('0.0')
            
            # Obter total de despesas
            cursor.execute("""
                SELECT COALESCE(SUM(valor), 0) AS total
                FROM financas_pessoais.transacoes
                WHERE tipo = 'D' AND data_transacao BETWEEN ? AND ?
            """, (data_inicio, data_fim))
            total_despesas = cursor.fetchone().total or Decimal('0.0')
            
            # Calcular saldo do período
            saldo_periodo = total_receitas - total_despesas
            
            return {
                'total_receitas': total_receitas,
                'total_despesas': total_despesas,
                'saldo_periodo': saldo_periodo
            }
            
        except Exception as e:
            print(f"Erro ao obter resumo por período: {e}")
            return {
                'total_receitas': Decimal('0.0'),
                'total_despesas': Decimal('0.0'),
                'saldo_periodo': Decimal('0.0')
            }
        finally:
            db.close()