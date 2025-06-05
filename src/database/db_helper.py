"""
Funções auxiliares para acesso ao banco de dados.
"""
import os
from src.database.connection import DatabaseConnection

def get_db_connection():
    """Retorna uma conexão com o banco de dados usando o ambiente atual."""
    environment = os.getenv('ENVIRONMENT', 'prod')
    return DatabaseConnection(environment=environment)