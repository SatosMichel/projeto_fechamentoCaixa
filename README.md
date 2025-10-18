# Sistema de Fechamento de Caixa - Brumake

## Descrição
# 🏢 Sistema de Fechamento de Caixa - Brumake

Sistema web completo para gerenciamento e fechamento de caixas da empresa Brumake Comercial e Serviços LTDA.
- **Usuário Master**: Controle de acessos e gerenciamento de contas
- **Usuários Avançados**: Acesso completo ao fluxo do programa
- **Usuários Caixa**: Acesso apenas aos lançamentos de seus respectivos caixas

## Estrutura do Projeto
```
Projeto_FechamentoCaixa/
├── src/
│   ├── main.py              # Arquivo principal
│   ├── database_manager.py  # Gerenciamento do banco de dados
│   ├── auth_manager.py      # Sistema de autenticação
│   ├── gui/
│   │   ├── login_window.py  # Tela de login
│   │   ├── master_panel.py  # Painel do usuário master
│   │   ├── cashier_flow.py  # Fluxo do usuário caixa
│   │   └── advanced_panel.py # Painel do usuário avançado
│   └── utils/
│       ├── calculations.py  # Cálculos do sistema
│       └── pdf_generator.py # Geração de relatórios PDF
├── database/
│   └── brumake_caixa.db    # Banco de dados SQLite
├── reports/                 # Relatórios gerados
└── requirements.txt        # Dependências
```

## Como executar
1. Instale as dependências: `pip install -r requirements.txt`
2. Execute o programa: `python src/main.py`

## Funcionalidades
- Sistema de login com níveis de acesso
- Controle de fluxo de trabalho para operadores de caixa
- Cálculos automáticos de sobra/falta
- Geração de relatórios em PDF
- Persistência de sessão para continuidade do trabalho