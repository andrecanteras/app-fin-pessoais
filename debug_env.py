import os
from dotenv import load_dotenv

def main():
    """Script para depurar as variáveis de ambiente."""
    print("Depurando variáveis de ambiente do arquivo .env")
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Verificar o conteúdo do arquivo .env
    try:
        with open('.env', 'r') as f:
            print("Conteúdo do arquivo .env:")
            print("-" * 50)
            for line in f:
                # Não mostrar a senha
                if "PASSWORD" in line and "=" in line:
                    parts = line.split("=", 1)
                    print(f"{parts[0]}=*****")
                else:
                    print(line.rstrip())
            print("-" * 50)
    except Exception as e:
        print(f"Erro ao ler o arquivo .env: {e}")
    
    # Listar todas as variáveis de ambiente carregadas
    print("\nVariáveis de ambiente carregadas:")
    print("-" * 50)
    env_vars = [
        'DB_SERVER', 'DB_PORT', 'DB_DATABASE', 'DB_USERNAME', 
        'DB_PASSWORD', 'DB_DRIVER', 'SQL_CONNECTION_STRING'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if var == 'DB_PASSWORD' and value:
            print(f"{var}: {'*' * len(value)}")
        elif var == 'SQL_CONNECTION_STRING' and value:
            # Ocultar a senha na string de conexão
            password = os.getenv('DB_PASSWORD', '')
            if password:
                value = value.replace(password, '*****')
            print(f"{var}: {value}")
        else:
            print(f"{var}: {value}")
    
    print("-" * 50)
    
    # Verificar se o python-dotenv está funcionando corretamente
    print("\nTeste de carregamento direto:")
    print("-" * 50)
    
    # Tentar carregar diretamente do arquivo
    try:
        from dotenv import dotenv_values
        config = dotenv_values(".env")
        for key, value in config.items():
            if "PASSWORD" in key.upper():
                print(f"{key}: *****")
            else:
                print(f"{key}: {value}")
    except Exception as e:
        print(f"Erro ao carregar diretamente: {e}")
    
    print("=" * 50)
    print("Depuração concluída!")

if __name__ == "__main__":
    main()