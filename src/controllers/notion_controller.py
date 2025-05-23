from src.services.notion_service import NotionService
from src.models.conta import Conta

class NotionController:
    """Controlador para operações relacionadas à integração com o Notion."""
    
    def __init__(self):
        self.notion_service = NotionService()
    
    def importar_transacoes_cartao(self, database_id=None, conta_id=None):
        """Importa transações de cartão de crédito do Notion.
        
        Args:
            database_id: ID do banco de dados do Notion (opcional, usa o valor do .env se não fornecido)
            conta_id: ID da conta para associar as transações
            
        Returns:
            tuple: (sucesso, mensagem, total_importado)
        """
        try:
            # Validar conta
            if not conta_id:
                return False, "ID da conta não fornecido.", 0
            
            conta = Conta.buscar_por_id(conta_id)
            if not conta:
                return False, f"Conta com ID {conta_id} não encontrada.", 0
            
            # Usar database_id do .env se não fornecido
            if not database_id:
                import os
                database_id = os.getenv('NOTION_CARTAO_DATABASE_ID')
                if not database_id:
                    return False, "ID do banco de dados do Notion não fornecido e não encontrado no .env", 0
            
            # Chamar o serviço para importar as transações
            return self.notion_service.importar_transacoes_cartao(database_id, conta_id)
            
        except Exception as e:
            return False, f"Erro ao importar transações: {str(e)}", 0
    
    def listar_databases_notion(self):
        """Lista os bancos de dados disponíveis no Notion.
        
        Returns:
            list: Lista de bancos de dados ou None em caso de erro
        """
        try:
            # Esta funcionalidade requer implementação adicional na API do Notion
            # A API atual não fornece um endpoint direto para listar todos os databases
            # Seria necessário conhecer os IDs dos databases previamente
            return None, "Funcionalidade não implementada na API atual do Notion."
        except Exception as e:
            return None, f"Erro ao listar bancos de dados: {str(e)}"