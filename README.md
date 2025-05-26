# Sistema de Finanças Pessoais

Sistema desktop para gerenciamento de finanças pessoais desenvolvido em Python com PyQt5 e SQL Server.

## Funcionalidades

- Dashboard com resumo financeiro
- Gestão de contas bancárias
- Gestão de categorias com hierarquia
- Gestão de transações (receitas e despesas)
- Integração com banco de dados SQL Server na Azure

## Requisitos

- Python 3.8+
- PyQt5
- SQL Server (Azure)
- ODBC Driver 17 para SQL Server
- Outras dependências listadas em requirements.txt

## Configuração

1. Clone o repositório
2. Crie um ambiente virtual: `python -m venv venv`
3. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instale as dependências: `pip install -r requirements.txt`
5. Copie `.env.example` para `.env` e configure com suas credenciais
6. Execute o aplicativo: `python main.py`

## Gerar Executável

Para gerar um executável standalone:

1. Instale o PyInstaller: `pip install pyinstaller`
2. Execute o script de build: `python build.py`
3. O executável será gerado na pasta `dist/`

## Estrutura do Projeto

```
financas_pessoais/
├── src/
│   ├── database/      # Conexão com banco de dados
│   ├── models/        # Modelos de dados
│   └── views/         # Interface gráfica
├── tests/            # Testes
├── main.py          # Ponto de entrada
└── requirements.txt # Dependências
```

## Contribuindo

1. Crie um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request