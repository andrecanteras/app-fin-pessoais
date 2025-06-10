# src/models/gasto_recorrente.py
from datetime import datetime, date
from decimal import Decimal
from src.database.db_helper import get_db_connection
from src.models.categoria import Categoria
from src.models.conta import Conta
from src.models.meio_pagamento import MeioPagamento
from src.models.transacao import Transacao

class GastoRecorrente:
    """Classe para representar um gasto recorrente."""
    
    def __init__(self, id=None, nome=None, valor=0.0, dia_vencimento=1, 
                 periodicidade="Mensal", categoria_id=None, conta_id=None, 
                 meio_pagamento_id=None, data_inicio=None, data_fim=None,
                 gerar_transacao=False, observacao=None, ativo=True, data_criacao=None):
        self.id = id
        self.nome = nome
        self.valor = Decimal(str(valor)) if valor is not None else Decimal('0.0')
        self.dia_vencimento = dia_vencimento
        self.periodicidade = periodicidade
        self.categoria_id = categoria_id
        self.conta_id = conta_id
        self.meio_pagamento_id = meio_pagamento_id
        self.data_inicio = data_inicio if data_inicio else date.today()
        self.data_fim = data_fim
        self.gerar_transacao = gerar_transacao
        self.observacao = observacao
        self.ativo = ativo
        self.data_criacao = data_criacao
        
        # Objetos relacionados
        self._categoria = None
        self._conta = None
        self._meio_pagamento = None
    
    # Propriedades para objetos relacionados
    @property
    def categoria(self):
        if self._categoria is None and self.categoria_id:
            self._categoria = Categoria.buscar_por_id(self.categoria_id)
        return self._categoria
    
    @property
    def conta(self):
        if self._conta is None and self.conta_id:
            self._conta = Conta.buscar_por_id(self.conta_id)
        return self._conta
    
    @property
    def meio_pagamento(self):
        if self._meio_pagamento is None and self.meio_pagamento_id:
            self._meio_pagamento = MeioPagamento.buscar_por_id(self.meio_pagamento_id)
        return self._meio_pagamento
    
    def salvar(self):
        """Salva ou atualiza um gasto recorrente no banco de dados."""
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema
            
            if self.id is None:
                # Inserir novo gasto recorrente
                cursor.execute(f"""
                    INSERT INTO {schema}.gastos_recorrentes 
                    (nome, valor, dia_vencimento, periodicidade, categoria_id, 
                     conta_id, meio_pagamento_id, data_inicio, data_fim, 
                     gerar_transacao, observacao, ativo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (self.nome, self.valor, self.dia_vencimento, self.periodicidade, 
                      self.categoria_id, self.conta_id, self.meio_pagamento_id, 
                      self.data_inicio, self.data_fim, self.gerar_transacao, 
                      self.observacao, self.ativo))
                
                # Obter o ID gerado
                cursor.execute("SELECT @@IDENTITY")
                self.id = cursor.fetchone()[0]
                
                # Gerar registros de pagamento para os próximos meses
                self._gerar_registros_pagamento()
            else:
                # Atualizar gasto recorrente existente
                cursor.execute(f"""
                    UPDATE {schema}.gastos_recorrentes
                    SET nome = ?, valor = ?, dia_vencimento = ?, periodicidade = ?, 
                        categoria_id = ?, conta_id = ?, meio_pagamento_id = ?, 
                        data_inicio = ?, data_fim = ?, gerar_transacao = ?, 
                        observacao = ?, ativo = ?
                    WHERE id = ?
                """, (self.nome, self.valor, self.dia_vencimento, self.periodicidade, 
                      self.categoria_id, self.conta_id, self.meio_pagamento_id, 
                      self.data_inicio, self.data_fim, self.gerar_transacao, 
                      self.observacao, self.ativo, self.id))
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Erro ao salvar gasto recorrente: {e}")
            return False
    
    def _gerar_registros_pagamento(self):
        """Gera registros de pagamento para os próximos meses."""
        if not self.id:
            return
        
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema
            
            # Gerar registros para os próximos 12 meses
            hoje = date.today()
            ano_atual = hoje.year
            mes_atual = hoje.month
            
            for i in range(12):
                mes = (mes_atual + i - 1) % 12 + 1  # 1-12
                ano = ano_atual + (mes_atual + i - 1) // 12
                
                # Verificar se já existe registro para este mês/ano
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {schema}.pagamentos_recorrentes
                    WHERE gasto_recorrente_id = ? AND ano = ? AND mes = ?
                """, (self.id, ano, mes))
                
                if cursor.fetchone()[0] == 0:
                    # Criar novo registro de pagamento
                    cursor.execute(f"""
                        INSERT INTO {schema}.pagamentos_recorrentes
                        (gasto_recorrente_id, ano, mes, data_pagamento, valor_pago)
                        VALUES (?, ?, ?, NULL, NULL)
                    """, (self.id, ano, mes))
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            print(f"Erro ao gerar registros de pagamento: {e}")
    
    def marcar_como_pago(self, ano, mes, data_pagamento=None, valor_pago=None, gerar_transacao=False):
        """Marca um pagamento como realizado para um mês específico."""
        if not self.id:
            return False
        
        if data_pagamento is None:
            data_pagamento = date.today()
        
        if valor_pago is None:
            valor_pago = self.valor
        
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema
            transacao_id = None
            
            # Se solicitado, gerar uma transação
            if gerar_transacao and self.conta_id:
                transacao = Transacao(
                    descricao=f"Pagamento de {self.nome}",
                    valor=valor_pago,
                    data_transacao=data_pagamento,
                    tipo='D',  # Despesa
                    categoria_id=self.categoria_id,
                    conta_id=self.conta_id,
                    meio_pagamento_id=self.meio_pagamento_id,
                    descricao_pagamento=f"Pagamento recorrente - {self.nome}",
                    observacao=f"Pagamento automático de gasto recorrente: {self.nome}"
                )
                
                if transacao.salvar():
                    transacao_id = transacao.id
            
            # Verificar se já existe registro para este mês/ano
            cursor.execute(f"""
                SELECT id FROM {schema}.pagamentos_recorrentes
                WHERE gasto_recorrente_id = ? AND ano = ? AND mes = ?
            """, (self.id, ano, mes))
            
            row = cursor.fetchone()
            if row:
                # Atualizar registro existente
                cursor.execute(f"""
                    UPDATE {schema}.pagamentos_recorrentes
                    SET data_pagamento = ?, valor_pago = ?, transacao_id = ?
                    WHERE id = ?
                """, (data_pagamento, valor_pago, transacao_id, row.id))
            else:
                # Inserir novo registro
                cursor.execute(f"""
                    INSERT INTO {schema}.pagamentos_recorrentes
                    (gasto_recorrente_id, ano, mes, data_pagamento, valor_pago, transacao_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (self.id, ano, mes, data_pagamento, valor_pago, transacao_id))
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Erro ao marcar pagamento como realizado: {e}")
            return False
    
    def verificar_pagamento(self, ano, mes):
        """Verifica se o pagamento para um mês específico já foi realizado."""
        if not self.id:
            return None
        
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema
            
            cursor.execute(f"""
                SELECT id, data_pagamento, valor_pago, transacao_id
                FROM {schema}.pagamentos_recorrentes
                WHERE gasto_recorrente_id = ? AND ano = ? AND mes = ?
            """, (self.id, ano, mes))
            
            row = cursor.fetchone()
            if row:
                return {
                    'pago': row.data_pagamento is not None,
                    'data_pagamento': row.data_pagamento,
                    'valor_pago': row.valor_pago,
                    'transacao_id': row.transacao_id,
                    'pagamento_id': row.id
                }
            return {'pago': False}
            
        except Exception as e:
            print(f"Erro ao verificar pagamento: {e}")
            return {'pago': False, 'erro': str(e)}
    
    @staticmethod
    def buscar_por_id(gasto_id):
        """Busca um gasto recorrente pelo ID."""
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema
            
            cursor.execute(f"""
                SELECT * FROM {schema}.gastos_recorrentes
                WHERE id = ?
            """, (gasto_id,))
            
            row = cursor.fetchone()
            if row:
                return GastoRecorrente(
                    id=row.id,
                    nome=row.nome,
                    valor=row.valor,
                    dia_vencimento=row.dia_vencimento,
                    periodicidade=row.periodicidade,
                    categoria_id=row.categoria_id,
                    conta_id=row.conta_id,
                    meio_pagamento_id=row.meio_pagamento_id,
                    data_inicio=row.data_inicio,
                    data_fim=row.data_fim,
                    gerar_transacao=row.gerar_transacao,
                    observacao=row.observacao,
                    ativo=row.ativo,
                    data_criacao=row.data_criacao
                )
            return None
            
        except Exception as e:
            print(f"Erro ao buscar gasto recorrente: {e}")
            return None
    
    @staticmethod
    def listar_todos(apenas_ativos=True):
        """Lista todos os gastos recorrentes."""
        db = get_db_connection()
        gastos = []
        
        try:
            cursor = db.get_cursor()
            schema = db.schema
            
            query = f"SELECT * FROM {schema}.gastos_recorrentes"
            if apenas_ativos:
                query += " WHERE ativo = 1"
            query += " ORDER BY nome"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                gasto = GastoRecorrente(
                    id=row.id,
                    nome=row.nome,
                    valor=row.valor,
                    dia_vencimento=row.dia_vencimento,
                    periodicidade=row.periodicidade,
                    categoria_id=row.categoria_id,
                    conta_id=row.conta_id,
                    meio_pagamento_id=row.meio_pagamento_id,
                    data_inicio=row.data_inicio,
                    data_fim=row.data_fim,
                    gerar_transacao=row.gerar_transacao,
                    observacao=row.observacao,
                    ativo=row.ativo,
                    data_criacao=row.data_criacao
                )
                gastos.append(gasto)
            
            return gastos
            
        except Exception as e:
            print(f"Erro ao listar gastos recorrentes: {e}")
            return []
    
    @staticmethod
    def listar_pagamentos_pendentes(ano=None, mes=None):
        """Lista todos os pagamentos pendentes para um mês específico."""
        if ano is None or mes is None:
            hoje = date.today()
            ano = hoje.year
            mes = hoje.month
        
        db = get_db_connection()
        pendentes = []
        
        try:
            cursor = db.get_cursor()
            schema = db.schema
            
            cursor.execute(f"""
                SELECT g.*, p.id as pagamento_id, p.data_pagamento
                FROM {schema}.gastos_recorrentes g
                LEFT JOIN {schema}.pagamentos_recorrentes p 
                    ON g.id = p.gasto_recorrente_id AND p.ano = ? AND p.mes = ?
                WHERE g.ativo = 1
                  AND (p.data_pagamento IS NULL OR p.id IS NULL)
                  AND (g.data_inicio <= DATEFROMPARTS(?, ?, 28))
                  AND (g.data_fim IS NULL OR g.data_fim >= DATEFROMPARTS(?, ?, 1))
                ORDER BY g.dia_vencimento
            """, (ano, mes, ano, mes, ano, mes))
            
            rows = cursor.fetchall()
            
            for row in rows:
                gasto = GastoRecorrente(
                    id=row.id,
                    nome=row.nome,
                    valor=row.valor,
                    dia_vencimento=row.dia_vencimento,
                    periodicidade=row.periodicidade,
                    categoria_id=row.categoria_id,
                    conta_id=row.conta_id,
                    meio_pagamento_id=row.meio_pagamento_id,
                    data_inicio=row.data_inicio,
                    data_fim=row.data_fim,
                    gerar_transacao=row.gerar_transacao,
                    observacao=row.observacao,
                    ativo=row.ativo,
                    data_criacao=row.data_criacao
                )
                pendentes.append({
                    'gasto': gasto,
                    'pagamento_id': getattr(row, 'pagamento_id', None),
                    'data_vencimento': date(ano, mes, min(row.dia_vencimento, 28))
                })
            
            return pendentes
            
        except Exception as e:
            print(f"Erro ao listar pagamentos pendentes: {e}")
            return []