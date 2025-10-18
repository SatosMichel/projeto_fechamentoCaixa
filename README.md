# Sistema de Fechamento de Caixa - Brumake

Projeto em Python/Flask para gerir o fechamento dos 4 caixas da empresa Brumake.

## Visão geral
- Back-end: Flask
- Banco de dados: SQLite
- Front-end: Templates Jinja2 + Bootstrap
- Geração de relatórios: ReportLab

## Estrutura do projeto (resumo)
- `app/` - aplicação Flask (rotas, templates, static)
- `src/` - código de suporte e lógica (database_manager, utilitários)
- `database/` - arquivo SQLite (gerado em runtime)
- `reports/` - relatórios gerados (PDF)

## Requisitos
- Python 3.11+
- Dependências em `requirements.txt` (flask, flask-session, reportlab, pillow, python-dateutil, werkzeug, jinja2)

## Instalação (Windows PowerShell)
1. Criar e ativar venv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

2. Instalar dependências

```powershell
pip install -r requirements.txt
```

3. Rodar a aplicação

```powershell
python main.py
```

4. Acessar no navegador

- http://127.0.0.1:5000

## Usuário master padrão
- Usuário: `SUP`
- Senha: `Miguel2@`

## Observações e recomendações
- O arquivo do banco (`database/brumake_caixa.db`) é gerado automaticamente.
- Recomendo remover do commit a pasta `flask_session/` se contém dados de sessão reais — adicione ao `.gitignore`.
- Para deploy em produção, usar um servidor WSGI (gunicorn/uvicorn) e um proxy reverso (NGINX).

## Próximos passos sugeridos
- Limpar dados sensíveis do repositório (ex.: sessão em disco)
- Adicionar testes automatizados e CI
- Fazer deploy em um ambiente seguro (Docker, servidor cloud)

## Autor
- Brumake Comercial e Serviços Ltda.

---