# Guia para Configurar GitHub com seu Projeto de Finanças Pessoais

Este guia fornece instruções passo a passo para configurar e gerenciar seu projeto de finanças pessoais no GitHub, seguindo boas práticas de engenharia de software.

## 1. Inicializar o Repositório Git

Primeiro, vamos inicializar um repositório Git no seu projeto:

```bash
# Navegue até a pasta do seu projeto
cd "C:\Users\andre.lopes.canteras\OneDrive - Boizito\Public\Backend\boizito_code\code_copilot_tst\financas_pessoais"

# Inicialize o Git
git init
```

## 2. Criar Arquivos Essenciais para o Repositório

### .gitignore

Crie um arquivo `.gitignore` para evitar que arquivos desnecessários sejam versionados:

```
# Ambiente virtual
venv/
env/
ENV/

# Arquivos Python compilados
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Arquivos de distribuição
dist/
build/
*.egg-info/

# Arquivos de configuração local
.env
.env.local
.env.*.local

# Arquivos de log
*.log
logs/

# Arquivos de banco de dados SQLite
*.sqlite3
*.db

# Arquivos de IDE
.idea/
.vscode/
*.swp
*.swo

# Arquivos do sistema operacional
.DS_Store
Thumbs.db

# Arquivos de cache
.pytest_cache/
.coverage
htmlcov/
```

### README.md

Crie um README.md informativo:

```markdown
# Finanças Pessoais

Um aplicativo de gerenciamento de finanças pessoais desenvolvido em Python com PyQt5 e SQL Server.

## Funcionalidades

- Controle de receitas e despesas
- Gerenciamento de contas bancárias
- Categorização de transações
- Relatórios financeiros
- Metas financeiras

## Requisitos

- Python 3.10+
- PyQt5
- SQL Server (Azure SQL Database)
- ODBC Driver 17 para SQL Server

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/financas-pessoais.git
   cd financas-pessoais
   ```

2. Crie um ambiente virtual:
   ```
   python -m venv venv
   ```

3. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

5. Configure o arquivo `.env` com suas credenciais de banco de dados:
   ```
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais
   ```

6. Execute o aplicativo:
   ```
   python main.py
   ```

## Estrutura do Projeto

```
financas_pessoais/
├── main.py                  # Ponto de entrada do aplicativo
├── requirements.txt         # Dependências do projeto
├── .env.example             # Exemplo de configuração de ambiente
├── src/                     # Código-fonte principal
│   ├── controllers/         # Controladores
│   ├── database/            # Configuração e acesso ao banco de dados
│   ├── models/              # Modelos de dados
│   ├── services/            # Serviços de negócios
│   └── views/               # Interface gráfica
└── tests/                   # Testes automatizados
```

## Desenvolvimento

Este projeto segue as convenções de código PEP 8 e utiliza o Git Flow para gerenciamento de branches.

### Branches

- `main`: Código em produção
- `develop`: Código em desenvolvimento
- `feature/*`: Novas funcionalidades
- `bugfix/*`: Correções de bugs

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
```

### LICENSE

Crie um arquivo LICENSE (usando a licença MIT como exemplo):

```
MIT License

Copyright (c) 2023 Seu Nome

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 3. Configurar o Repositório GitHub

1. Crie um novo repositório no GitHub (sem README, .gitignore ou LICENSE)
2. Adicione o repositório remoto:

```bash
git remote add origin https://github.com/seu-usuario/financas-pessoais.git
```

## 4. Fazer o Primeiro Commit e Push

```bash
# Adicionar todos os arquivos
git add .

# Fazer o primeiro commit
git commit -m "Commit inicial: estrutura básica do projeto"

# Enviar para o GitHub
git push -u origin main
```

## 5. Configurar Integração do VSCode com GitHub

### Extensões Recomendadas para VSCode

1. **GitHub Pull Requests and Issues**: Para gerenciar PRs e issues diretamente do VSCode
2. **GitLens**: Para visualizar histórico de commits e alterações
3. **Git Graph**: Para visualizar o gráfico de commits

### Configurar Autenticação no VSCode

1. Abra a paleta de comandos (Ctrl+Shift+P)
2. Digite "Git: Clone" e selecione
3. Quando solicitado, faça login no GitHub

## 6. Práticas Recomendadas para Engenharia de Software com Git

### Fluxo de Trabalho com Git Flow

1. **Branch Main**: Código estável, pronto para produção
2. **Branch Develop**: Código em desenvolvimento
3. **Feature Branches**: Para novas funcionalidades
   ```bash
   git checkout -b feature/nova-funcionalidade develop
   # Trabalhe na funcionalidade
   git commit -m "Implementa nova funcionalidade"
   git checkout develop
   git merge --no-ff feature/nova-funcionalidade
   ```
4. **Hotfix Branches**: Para correções urgentes
   ```bash
   git checkout -b hotfix/correcao-bug main
   # Corrija o bug
   git commit -m "Corrige bug crítico"
   git checkout main
   git merge --no-ff hotfix/correcao-bug
   git checkout develop
   git merge --no-ff hotfix/correcao-bug
   ```

### Commits Semânticos

Use commits semânticos para melhor organização:

```
feat: adiciona nova funcionalidade
fix: corrige um bug
docs: atualiza documentação
style: formatação de código
refactor: refatoração de código
test: adiciona ou modifica testes
chore: tarefas de manutenção
```

### Pull Requests

1. Crie PRs para cada feature ou bugfix
2. Use templates de PR para padronizar as informações
3. Faça code reviews antes de mesclar

## 7. Integração Contínua (CI)

Configure GitHub Actions para automação:

Crie um arquivo `.github/workflows/python-app.yml`:

```yaml
name: Python Application

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        pip install pytest pytest-cov flake8
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    - name: Test with pytest
      run: |
        pytest --cov=src tests/
```

## 8. Documentação do Projeto

### Wiki do GitHub

Use a Wiki do GitHub para documentação mais detalhada:

1. Guia de Desenvolvimento
2. Arquitetura do Sistema
3. Guia de Contribuição
4. FAQ

### Issues e Projetos

1. Use Issues para rastrear bugs e funcionalidades
2. Configure Projects para gerenciar o backlog e sprints

## 9. Versionamento Semântico

Adote o versionamento semântico (MAJOR.MINOR.PATCH):

1. MAJOR: mudanças incompatíveis
2. MINOR: adições compatíveis
3. PATCH: correções de bugs compatíveis

## 10. Comandos Git Úteis para o Dia a Dia

```bash
# Ver status
git status

# Ver histórico de commits
git log --oneline --graph

# Criar uma nova branch
git checkout -b nome-da-branch

# Atualizar sua branch com a develop
git checkout develop
git pull
git checkout sua-branch
git merge develop

# Desfazer alterações em um arquivo
git checkout -- nome-do-arquivo

# Desfazer o último commit (mantendo as alterações)
git reset --soft HEAD~1

# Stash (guardar alterações temporariamente)
git stash
git stash pop
```

## 11. Usando o VSCode para Git

1. **Source Control View**: Acesse com Ctrl+Shift+G
2. **Staged Changes**: Adicione arquivos ao staging area
3. **Commit**: Escreva a mensagem e clique em ✓
4. **Sync**: Sincronize com o repositório remoto
5. **Timeline**: Veja o histórico de um arquivo específico

## 12. Dicas para Projetos Python no GitHub

1. **Mantenha o requirements.txt atualizado**:
   ```bash
   pip freeze > requirements.txt
   ```

2. **Use ambientes virtuais**:
   ```bash
   python -m venv venv
   ```

3. **Documente seu código**:
   ```python
   def funcao(parametro):
       """
       Descrição da função.
       
       Args:
           parametro: Descrição do parâmetro
           
       Returns:
           Descrição do retorno
       """
       # Implementação
   ```

4. **Escreva testes**:
   ```python
   def test_funcao():
       assert funcao(1) == 2
   ```

## 13. Fluxo de Trabalho Completo - Exemplo Prático

Aqui está um exemplo de fluxo de trabalho completo para adicionar uma nova funcionalidade:

1. **Atualize seu repositório local**:
   ```bash
   git checkout main
   git pull
   git checkout develop
   git pull
   ```

2. **Crie uma branch para a nova funcionalidade**:
   ```bash
   git checkout -b feature/adicionar-relatorio-mensal develop
   ```

3. **Faça as alterações necessárias**:
   - Implemente a funcionalidade
   - Escreva testes
   - Documente o código

4. **Faça commits frequentes e semânticos**:
   ```bash
   git add src/services/relatorio_service.py
   git commit -m "feat: implementa geração de relatório mensal"
   
   git add src/views/relatorio_view.py
   git commit -m "feat: adiciona interface para relatório mensal"
   
   git add tests/test_relatorio_service.py
   git commit -m "test: adiciona testes para relatório mensal"
   ```

5. **Atualize sua branch com as últimas alterações da develop**:
   ```bash
   git checkout develop
   git pull
   git checkout feature/adicionar-relatorio-mensal
   git merge develop
   # Resolva conflitos se necessário
   ```

6. **Envie sua branch para o GitHub**:
   ```bash
   git push -u origin feature/adicionar-relatorio-mensal
   ```

7. **Crie um Pull Request**:
   - Vá para o GitHub
   - Clique em "Compare & pull request"
   - Preencha a descrição do PR
   - Solicite revisores
   - Clique em "Create pull request"

8. **Após aprovação, faça o merge**:
   - No GitHub, clique em "Merge pull request"
   - Ou localmente:
     ```bash
     git checkout develop
     git merge --no-ff feature/adicionar-relatorio-mensal
     git push origin develop
     ```

9. **Limpe as branches**:
   ```bash
   git branch -d feature/adicionar-relatorio-mensal
   git push origin --delete feature/adicionar-relatorio-mensal
   ```

## 14. Resolução de Problemas Comuns

### Conflitos de Merge

1. **Identificar os arquivos com conflito**:
   ```bash
   git status
   ```

2. **Abrir os arquivos e resolver os conflitos**:
   - Procure por marcações como `<<<<<<< HEAD`, `=======`, e `>>>>>>> branch-name`
   - Edite o arquivo para manter o código correto
   - Remova as marcações de conflito

3. **Marcar como resolvido e continuar**:
   ```bash
   git add arquivo-com-conflito
   git commit -m "Resolve conflitos de merge"
   ```

### Reverter Alterações

1. **Reverter um arquivo específico**:
   ```bash
   git checkout -- nome-do-arquivo
   ```

2. **Reverter todas as alterações não commitadas**:
   ```bash
   git reset --hard
   ```

3. **Reverter um commit específico**:
   ```bash
   git revert <hash-do-commit>
   ```

### Recuperar Alterações Perdidas

1. **Ver histórico de referências**:
   ```bash
   git reflog
   ```

2. **Recuperar um estado anterior**:
   ```bash
   git checkout <hash-do-reflog>
   ```

## 15. Melhores Práticas para Colaboração

1. **Comunique-se claramente**:
   - Escreva descrições detalhadas nos PRs
   - Documente decisões importantes

2. **Mantenha os PRs pequenos e focados**:
   - Um PR deve implementar uma única funcionalidade ou correção
   - PRs menores são mais fáceis de revisar

3. **Revise o código com atenção**:
   - Verifique a lógica, não apenas a sintaxe
   - Teste as alterações localmente antes de aprovar

4. **Mantenha o histórico limpo**:
   - Use `git rebase` para organizar commits antes de mesclar
   - Evite commits como "Fix typo" ou "WIP"

5. **Automatize o que for possível**:
   - Use GitHub Actions para testes, linting e build
   - Configure hooks de pre-commit para verificações locais

## 16. Recursos Adicionais

- [Pro Git Book](https://git-scm.com/book/en/v2) - Livro completo sobre Git
- [GitHub Learning Lab](https://lab.github.com/) - Tutoriais interativos
- [Conventional Commits](https://www.conventionalcommits.org/) - Padrão para mensagens de commit
- [Git Flow Cheatsheet](https://danielkummer.github.io/git-flow-cheatsheet/) - Guia rápido para Git Flow
- [GitHub Docs](https://docs.github.com/) - Documentação oficial do GitHub