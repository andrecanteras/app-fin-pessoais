"""
Classe fachada para representar uma conta bancária completa.
"""
from decimal import Decimal
from src.models.conta_dimensao import ContaDimensao
from src.models.conta_saldo import ContaSaldo

class Conta:
    """Classe fachada para representar uma conta bancária completa."""
    
    def __init__(self, id=None, nome=None, tipo=None, saldo_inicial=0.0, saldo_atual=None, 
                 banco=None, agencia=None, conta_contabil=None, numero_banco=None,
                 titular=None, nome_gerente=None, contato_gerente=None, data_criacao=None, 
                 ativo=True, dimensao_id=None, saldo_id=None):
        
        # Inicializar a dimensão
        self.dimensao = ContaDimensao(
            id=dimensao_id or id,
            nome=nome,
            tipo=tipo,
            instituicao=banco,
            agencia=agencia,
            conta_contabil=conta_contabil,
            numero_banco=numero_banco,
            titular=titular,
            nome_gerente=nome_gerente,
            contato_gerente=contato_gerente,
            data_criacao=data_criacao,
            ativo=ativo
        )
        
        # Inicializar o saldo
        self.saldo = ContaSaldo(
            id=saldo_id,
            conta_dimensao_id=dimensao_id or id,
            saldo_inicial=saldo_inicial,
            saldo_atual=saldo_atual,
            data_criacao=data_criacao
        )
        
        # Manter atributos para compatibilidade com código existente
        self.id = self.dimensao.id
        self.nome = self.dimensao.nome
        self.tipo = self.dimensao.tipo
        self.banco = self.dimensao.instituicao
        self.agencia = self.dimensao.agencia
        self.conta_contabil = self.dimensao.conta_contabil
        self.numero_banco = self.dimensao.numero_banco
        self.titular = self.dimensao.titular
        self.nome_gerente = self.dimensao.nome_gerente
        self.contato_gerente = self.dimensao.contato_gerente
        self.data_criacao = self.dimensao.data_criacao
        self.ativo = self.dimensao.ativo
        self.saldo_inicial = self.saldo.saldo_inicial
        self.saldo_atual = self.saldo.saldo_atual
    
    def _sincronizar_atributos(self):
        """Sincroniza os atributos da fachada com os objetos internos."""
        # Sincronizar dimensão -> fachada
        self.id = self.dimensao.id
        self.nome = self.dimensao.nome
        self.tipo = self.dimensao.tipo
        self.banco = self.dimensao.instituicao
        self.agencia = self.dimensao.agencia
        self.conta_contabil = self.dimensao.conta_contabil
        self.numero_banco = self.dimensao.numero_banco
        self.titular = self.dimensao.titular
        self.nome_gerente = self.dimensao.nome_gerente
        self.contato_gerente = self.dimensao.contato_gerente
        self.data_criacao = self.dimensao.data_criacao
        self.ativo = self.dimensao.ativo
        
        # Sincronizar saldo
        self.saldo_inicial = self.saldo.saldo_inicial
        self.saldo_atual = self.saldo.saldo_atual
        
        # Garantir que o ID da dimensão esteja correto no saldo
        if self.dimensao.id and not self.saldo.conta_dimensao_id:
            self.saldo.conta_dimensao_id = self.dimensao.id
    
    def salvar(self):
        """Salva ou atualiza a conta completa no banco de dados."""
        # Sincronizar atributos da fachada para os objetos internos
        self.dimensao.nome = self.nome
        self.dimensao.tipo = self.tipo
        self.dimensao.instituicao = self.banco
        self.dimensao.agencia = self.agencia
        self.dimensao.conta_contabil = self.conta_contabil
        self.dimensao.numero_banco = self.numero_banco
        self.dimensao.titular = self.titular
        self.dimensao.nome_gerente = self.nome_gerente
        self.dimensao.contato_gerente = self.contato_gerente
        
        # Primeiro salvar a dimensão
        if not self.dimensao.salvar():
            return False
        
        # Atualizar o ID da dimensão no saldo
        self.saldo.conta_dimensao_id = self.dimensao.id
        
        # Depois salvar o saldo
        if not self.saldo.salvar():
            return False
        
        # Sincronizar os atributos
        self._sincronizar_atributos()
        return True
    
    def atualizar_saldo(self, valor, tipo):
        """Atualiza o saldo da conta com base no tipo de transação."""
        resultado = self.saldo.atualizar_saldo(valor, tipo)
        if resultado:
            self.saldo_atual = self.saldo.saldo_atual
        return resultado
    
    def excluir(self):
        """Marca uma conta como inativa (exclusão lógica)."""
        resultado = self.dimensao.excluir()
        if resultado:
            self.ativo = False
        return resultado
    
    @staticmethod
    def buscar_por_id(conta_id):
        """Busca uma conta completa pelo ID."""
        # Buscar a dimensão
        dimensao = ContaDimensao.buscar_por_id(conta_id)
        if not dimensao:
            return None
        
        # Buscar o saldo
        saldo = ContaSaldo.buscar_por_dimensao_id(dimensao.id)
        if not saldo:
            return None
        
        # Criar e retornar a conta completa
        return Conta(
            id=dimensao.id,
            dimensao_id=dimensao.id,
            saldo_id=saldo.id,
            nome=dimensao.nome,
            tipo=dimensao.tipo,
            banco=dimensao.instituicao,
            agencia=dimensao.agencia,
            conta_contabil=dimensao.conta_contabil,
            numero_banco=dimensao.numero_banco,
            titular=dimensao.titular,
            nome_gerente=dimensao.nome_gerente,
            contato_gerente=dimensao.contato_gerente,
            saldo_inicial=saldo.saldo_inicial,
            saldo_atual=saldo.saldo_atual,
            data_criacao=dimensao.data_criacao,
            ativo=dimensao.ativo
        )
    
    @staticmethod
    def listar_todas(apenas_ativas=True):
        """Lista todas as contas completas."""
        contas = []
        
        # Buscar todas as dimensões
        dimensoes = ContaDimensao.listar_todas(apenas_ativas)
        
        for dimensao in dimensoes:
            # Buscar o saldo correspondente
            saldo = ContaSaldo.buscar_por_dimensao_id(dimensao.id)
            if saldo:
                # Criar a conta completa
                conta = Conta(
                    id=dimensao.id,
                    dimensao_id=dimensao.id,
                    saldo_id=saldo.id,
                    nome=dimensao.nome,
                    tipo=dimensao.tipo,
                    banco=dimensao.instituicao,
                    agencia=dimensao.agencia,
                    conta_contabil=dimensao.conta_contabil,
                    numero_banco=dimensao.numero_banco,
                    titular=dimensao.titular,
                    nome_gerente=dimensao.nome_gerente,
                    contato_gerente=dimensao.contato_gerente,
                    saldo_inicial=saldo.saldo_inicial,
                    saldo_atual=saldo.saldo_atual,
                    data_criacao=dimensao.data_criacao,
                    ativo=dimensao.ativo
                )
                contas.append(conta)
        
        return contas
    
    @staticmethod
    def obter_saldo_total():
        """Retorna o saldo total de todas as contas ativas."""
        return ContaSaldo.obter_saldo_total(apenas_ativas=True)