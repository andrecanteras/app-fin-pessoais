"""
Classe para representar os dados descritivos de uma conta bancária.
"""
from src.database.db_helper import get_db_connection

class ContaDimensao:
    """Classe para representar os dados descritivos de uma conta bancária."""
    
    def __init__(self, id=None, nome=None, tipo=None, instituicao=None, 
                 agencia=None, conta_contabil=None, numero_banco=None,
                 titular=None, nome_gerente=None, contato_gerente=None, 
                 data_criacao=None, ativo=True):
        self.id = id
        self.nome = nome
        self.tipo = tipo
        self.instituicao = instituicao
        self.agencia = agencia
        self.conta_contabil = conta_contabil
        self.numero_banco = numero_banco
        self.titular = titular
        self.nome_gerente = nome_gerente
        self.contato_gerente = contato_gerente
        self.data_criacao = data_criacao
        self.ativo = ativo
    
    def salvar(self):
        """Salva ou atualiza os dados da dimensão da conta no banco de dados."""
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema  # Obter o esquema atual
            
            if self.id is None:
                # Inserir nova dimensão
                cursor.execute(f"""
                    INSERT INTO {schema}.conta_dimensao 
                    (nome, tipo, instituicao, agencia, conta_contabil, numero_banco, 
                     titular, nome_gerente, contato_gerente, ativo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (self.nome, self.tipo, self.instituicao, self.agencia, 
                      self.conta_contabil, self.numero_banco, self.titular,
                      self.nome_gerente, self.contato_gerente, self.ativo))
                
                # Obter o ID gerado
                cursor.execute("SELECT @@IDENTITY")
                self.id = cursor.fetchone()[0]
            else:
                # Atualizar dimensão existente
                cursor.execute(f"""
                    UPDATE {schema}.conta_dimensao
                    SET nome = ?, tipo = ?, instituicao = ?, agencia = ?, 
                        conta_contabil = ?, numero_banco = ?, titular = ?,
                        nome_gerente = ?, contato_gerente = ?, ativo = ?
                    WHERE id = ?
                """, (self.nome, self.tipo, self.instituicao, self.agencia, 
                      self.conta_contabil, self.numero_banco, self.titular,
                      self.nome_gerente, self.contato_gerente, self.ativo, self.id))
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Erro ao salvar dimensão da conta: {e}")
            return False
        finally:
            db.close()
    
    def excluir(self):
        """Marca uma conta como inativa (exclusão lógica)."""
        if self.id is None:
            return False
        
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema  # Obter o esquema atual
            
            cursor.execute(f"""
                UPDATE {schema}.conta_dimensao 
                SET ativo = 0 
                WHERE id = ?
            """, (self.id,))
            
            db.commit()
            self.ativo = False
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Erro ao excluir dimensão da conta: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def buscar_por_id(dimensao_id):
        """Busca uma dimensão de conta pelo ID."""
        db = get_db_connection()
        try:
            cursor = db.get_cursor()
            schema = db.schema  # Obter o esquema atual
            
            cursor.execute(f"""
                SELECT id, nome, tipo, instituicao, agencia, conta_contabil, 
                       numero_banco, titular, nome_gerente, contato_gerente, 
                       data_criacao, ativo
                FROM {schema}.conta_dimensao
                WHERE id = ?
            """, (dimensao_id,))
            
            row = cursor.fetchone()
            
            if row:
                return ContaDimensao(
                    id=row.id,
                    nome=row.nome,
                    tipo=row.tipo,
                    instituicao=getattr(row, 'instituicao', None),
                    agencia=getattr(row, 'agencia', None),
                    conta_contabil=getattr(row, 'conta_contabil', None),
                    numero_banco=getattr(row, 'numero_banco', None),
                    titular=getattr(row, 'titular', None),
                    nome_gerente=getattr(row, 'nome_gerente', None),
                    contato_gerente=getattr(row, 'contato_gerente', None),
                    data_criacao=row.data_criacao,
                    ativo=row.ativo
                )
            return None
            
        except Exception as e:
            print(f"Erro ao buscar dimensão da conta: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def listar_todas(apenas_ativas=True):
        """Lista todas as dimensões de contas."""
        db = get_db_connection()
        dimensoes = []
        
        try:
            cursor = db.get_cursor()
            schema = db.schema  # Obter o esquema atual
            
            query = f"""
                SELECT id, nome, tipo, instituicao, agencia, conta_contabil, 
                       numero_banco, titular, nome_gerente, contato_gerente, 
                       data_criacao, ativo
                FROM {schema}.conta_dimensao
            """
            
            if apenas_ativas:
                query += " WHERE ativo = 1"
            
            query += " ORDER BY nome"
            
            # Tentativa com tratamento de erro e retry
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        dimensao = ContaDimensao(
                            id=row.id,
                            nome=row.nome,
                            tipo=row.tipo,
                            instituicao=getattr(row, 'instituicao', None),
                            agencia=getattr(row, 'agencia', None),
                            conta_contabil=getattr(row, 'conta_contabil', None),
                            numero_banco=getattr(row, 'numero_banco', None),
                            titular=getattr(row, 'titular', None),
                            nome_gerente=getattr(row, 'nome_gerente', None),
                            contato_gerente=getattr(row, 'contato_gerente', None),
                            data_criacao=row.data_criacao,
                            ativo=row.ativo
                        )
                        dimensoes.append(dimensao)
                    
                    break  # Sai do loop se bem-sucedido
                    
                except Exception as e:
                    retry_count += 1
                    print(f"Erro ao listar dimensões de contas (tentativa {retry_count}/{max_retries}): {e}")
                    if retry_count >= max_retries:
                        print("Número máximo de tentativas excedido.")
                        return []
                    
                    # Tentar reconectar antes da próxima tentativa
                    try:
                        db = get_db_connection()
                        cursor = db.get_cursor()
                    except:
                        pass
            
            return dimensoes
            
        except Exception as e:
            print(f"Erro ao listar dimensões de contas: {e}")
            return []
        finally:
            try:
                db.close()
            except:
                pass