"""
Script para verificar se as tabelas conta_dimensao e conta_saldos existem.
"""
from src.database.connection import DatabaseConnection

def check_tables():
    """Verifica se as tabelas conta_dimensao e conta_saldos existem."""
    db = DatabaseConnection()
    try:
        cursor = db.get_cursor()
        
        # Verificar tabela conta_dimensao
        try:
            cursor.execute("SELECT TOP 1 * FROM financas_pessoais.conta_dimensao")
            print("Tabela conta_dimensao já existe")
        except Exception as e:
            print(f"Tabela conta_dimensao não existe: {e}")
        
        # Verificar tabela conta_saldos
        try:
            cursor.execute("SELECT TOP 1 * FROM financas_pessoais.conta_saldos")
            print("Tabela conta_saldos já existe")
        except Exception as e:
            print(f"Tabela conta_saldos não existe: {e}")
            
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_tables()