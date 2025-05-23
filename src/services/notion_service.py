import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from src.models.transacao import Transacao
from src.models.categoria import Categoria
from src.models.conta import Conta

# Carrega as variáveis de ambiente
load_dotenv()

class NotionService:
    """Serviço para integração com a API do Notion."""
    
    def __init__(self):
        """Inicializa o serviço com as credenciais do Notion."""
        self.token = os.getenv('NOTION_TOKEN')
        self.base_url = "https://api.notion.com/v1"
        self.version = "2022-06-28"  # Versão atual da API do Notion
        
        if not self.token:
            raise ValueError("Token do Notion não encontrado nas variáveis de ambiente.")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": self.version,
            "Content-Type": "application/json"
        }
    
    def obter_database(self, database_id):
        """Obtém informações sobre um banco de dados específico."""
        try:
            url = f"{self.base_url}/databases/{database_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter banco de dados do Notion: {e}")
            return None
    
    def consultar_database(self, database_id, filtros=None):
        """Consulta registros em um banco de dados do Notion com filtros opcionais."""
        try:
            url = f"{self.base_url}/databases/{database_id}/query"
            
            # Preparar payload com filtros, se fornecidos
            payload = {}
            if filtros:
                payload = filtros
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao consultar banco de dados do Notion: {e}")
            return None
    
    def importar_transacoes_cartao(self, database_id, conta_id):
        """Importa transações de cartão de crédito do Notion para o aplicativo.
        
        Args:
            database_id: ID do banco de dados do Notion contendo as transações
            conta_id: ID da conta no aplicativo para associar as transações
            
        Returns:
            tuple: (sucesso, mensagem, total_importado)
        """
        try:
            # Verificar se a conta existe
            conta = Conta.buscar_por_id(conta_id)
            if not conta:
                return False, "Conta não encontrada.", 0
            
            # Consultar todas as transações do banco de dados do Notion
            resultado = self.consultar_database(database_id)
            if not resultado:
                return False, "Não foi possível obter dados do Notion.", 0
            
            # Processar os resultados
            transacoes_importadas = 0
            for item in resultado.get('results', []):
                # Extrair propriedades do item do Notion
                # Nota: Ajuste os nomes das propriedades conforme seu banco de dados no Notion
                properties = item.get('properties', {})
                
                # Extrair dados das propriedades
                try:
                    descricao = self._extrair_texto(properties.get('Descrição', {}))
                    valor = self._extrair_numero(properties.get('Valor', {}))
                    data_str = self._extrair_data(properties.get('Data', {}))
                    categoria_nome = self._extrair_texto(properties.get('Categoria', {}))
                    
                    # Verificar se todos os campos obrigatórios estão presentes
                    if not all([descricao, valor, data_str]):
                        print(f"Dados incompletos para o item: {item.get('id')}")
                        continue
                    
                    # Converter string de data para objeto date
                    data_transacao = datetime.strptime(data_str, "%Y-%m-%d").date()
                    
                    # Buscar ou criar categoria
                    categoria_id = self._obter_categoria_id(categoria_nome)
                    
                    # Criar transação
                    transacao = Transacao(
                        descricao=descricao,
                        valor=valor,
                        data_transacao=data_transacao,
                        tipo='D',  # Assumindo que são despesas de cartão de crédito
                        categoria_id=categoria_id,
                        conta_id=conta_id,
                        observacao=f"Importado do Notion em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    
                    # Salvar transação
                    if transacao.salvar():
                        transacoes_importadas += 1
                    
                except Exception as e:
                    print(f"Erro ao processar item do Notion: {e}")
                    continue
            
            if transacoes_importadas > 0:
                return True, f"{transacoes_importadas} transações importadas com sucesso.", transacoes_importadas
            else:
                return False, "Nenhuma transação foi importada.", 0
                
        except Exception as e:
            print(f"Erro ao importar transações do Notion: {e}")
            return False, f"Erro ao importar transações: {str(e)}", 0
    
    def _extrair_texto(self, propriedade):
        """Extrai texto de uma propriedade do Notion."""
        try:
            if propriedade.get('type') == 'title':
                return propriedade.get('title', [{}])[0].get('plain_text', '')
            elif propriedade.get('type') == 'rich_text':
                rich_text = propriedade.get('rich_text', [])
                if rich_text:
                    return rich_text[0].get('plain_text', '')
            elif propriedade.get('type') == 'select':
                select = propriedade.get('select', {})
                if select:
                    return select.get('name', '')
            return ''
        except Exception:
            return ''
    
    def _extrair_numero(self, propriedade):
        """Extrai número de uma propriedade do Notion."""
        try:
            if propriedade.get('type') == 'number':
                return propriedade.get('number', 0)
            return 0
        except Exception:
            return 0
    
    def _extrair_data(self, propriedade):
        """Extrai data de uma propriedade do Notion."""
        try:
            if propriedade.get('type') == 'date':
                date_obj = propriedade.get('date', {})
                if date_obj:
                    return date_obj.get('start', '')
            return ''
        except Exception:
            return ''
    
    def _obter_categoria_id(self, categoria_nome):
        """Busca uma categoria pelo nome ou cria uma nova."""
        if not categoria_nome:
            return None
        
        # Buscar categorias existentes
        categorias = Categoria.listar_todas()
        for categoria in categorias:
            if categoria.nome.lower() == categoria_nome.lower():
                return categoria.id
        
        # Se não encontrou, criar nova categoria
        nova_categoria = Categoria(
            nome=categoria_nome,
            tipo='D',  # Assumindo que são despesas de cartão de crédito
            descricao=f"Categoria criada automaticamente pela importação do Notion"
        )
        
        if nova_categoria.salvar():
            return nova_categoria.id
        
        return None