# 📁 Estrutura do Projeto QA Oráculo

## 🎯 Visão Geral

Este documento descreve a organização e estrutura do projeto QA Oráculo, um sistema inteligente para análise e geração de planos de teste baseado em IA.

## 📂 Estrutura de Diretórios

```
qa-oraculo-requisitos/
├── 📁 .config/                    # Configurações do projeto
│   ├── pyproject.toml            # Configuração do projeto e ferramentas
│   ├── pytest.ini               # Configuração do pytest
│   └── pyrightconfig.json       # Configuração do Pyright (type checker)
│
├── 📁 .vscode/                   # Configurações do VS Code
│   └── settings.json            # Configurações específicas do workspace
│
├── 📁 assets/                    # Recursos estáticos
│   ├── logo_oraculo.png         # Logo do projeto
│   └── qa_oraculo_cartoon_demo.gif # Demo animado
│
├── 📁 data/                      # Dados persistentes
│   └── qa_oraculo_history.db    # Banco de dados SQLite
│
├── 📁 docs/                      # Documentação
│   ├── INDEX.md                 # Índice geral da documentação
│   ├── README.md                # Documentação técnica
│   ├── SETUP_GUIDE.md           # Guia de instalação
│   ├── DEVELOPER_QUICK_START.md # Guia para desenvolvedores
│   ├── CHANGELOG.md             # Histórico de mudanças
│   ├── acessibilidade.md        # Documentação de acessibilidade
│   ├── CAMPOS_PERSONALIZADOS_XRAY.md # Campos Xray
│   ├── DOCUMENTACAO_TECNICA.md  # Documentação técnica detalhada
│   ├── RESUMO_FINAL_XRAY.md     # Resumo Xray
│   ├── XRAY_EXPORT_GUIDE.md     # Guia de exportação Xray
│   └── XRAY_IMPLEMENTATION_SUMMARY.md # Resumo implementação Xray
│
├── 📁 qa_core/                   # Código principal da aplicação
│   ├── __init__.py              # Inicialização do módulo
│   ├── app.py                   # Aplicação principal Streamlit
│   ├── config.py                # Configurações da aplicação
│   ├── database.py              # Módulo de banco de dados
│   ├── graph.py                 # Lógica de grafos e fluxos
│   ├── pdf_generator.py         # Geração de PDFs
│   ├── prompts.py               # Prompts para IA
│   ├── schemas.py               # Esquemas de dados
│   ├── state_manager.py         # Gerenciamento de estado
│   ├── utils.py                 # Utilitários gerais
│   └── a11y.py                  # Funcionalidades de acessibilidade
│
├── 📁 scripts/                   # Scripts de automação
│   ├── quick-setup.sh           # Setup rápido (Linux/Mac)
│   ├── quick-setup.bat          # Setup rápido (Windows)
│   ├── setup.sh                 # Setup completo (Linux/Mac)
│   └── setup.bat                # Setup completo (Windows)
│
├── 📁 templates/                 # Templates e modelos
│   └── PR_TEMPLATE.md           # Template para Pull Requests
│
├── 📁 tests/                     # Testes automatizados
│   ├── __init__.py              # Inicialização do módulo de testes
│   ├── conftest.py              # Configuração do pytest
│   ├── test_app.py              # Testes da aplicação principal
│   ├── test_app_main.py         # Testes do main.py
│   ├── test_app_history_delete.py # Testes de exclusão de histórico
│   ├── test_app_ensure_bytes.py # Testes de conversão de bytes
│   ├── test_database.py         # Testes do banco de dados
│   ├── test_graph.py            # Testes de grafos
│   ├── test_pdf_generator.py    # Testes de geração de PDF
│   ├── test_state_manager.py    # Testes de gerenciamento de estado
│   ├── test_utils.py            # Testes de utilitários
│   ├── test_a11y.py             # Testes de acessibilidade
│   ├── test_xray_export.py      # Testes de exportação Xray
│   └── tests_schemas.py         # Testes de esquemas
│
├── 📄 .gitignore                # Arquivos ignorados pelo Git
├── 📄 Makefile                  # Comandos de desenvolvimento
├── 📄 LICENSE                   # Licença do projeto
├── 📄 main.py                   # Ponto de entrada da aplicação
├── 📄 PROJECT_STRUCTURE.md      # Este arquivo
├── 📄 README.md                 # Documentação principal
├── 📄 requirements.txt          # Dependências de produção
├── 📄 requirements-dev.txt      # Dependências de desenvolvimento
└── 📄 setup.py                  # Configuração do pacote Python
```

## 🎯 Princípios de Organização

### 📁 **Separação por Responsabilidade**
- **`.config/`**: Todas as configurações centralizadas
- **`qa_core/`**: Lógica de negócio e aplicação
- **`tests/`**: Testes isolados e organizados
- **`docs/`**: Documentação estruturada
- **`scripts/`**: Automação e utilitários
- **`templates/`**: Modelos e templates reutilizáveis

### 🔧 **Configuração Centralizada**
- **`pyproject.toml`**: Configuração principal do projeto
- **`pytest.ini`**: Configuração específica de testes
- **`pyrightconfig.json`**: Configuração de type checking
- **`.vscode/settings.json`**: Configuração do IDE

### 📊 **Dados Organizados**
- **`data/`**: Dados persistentes e banco de dados
- **`assets/`**: Recursos estáticos e mídia
- **`htmlcov/`**: Relatórios de cobertura (gerado automaticamente)

## 🚀 Comandos de Desenvolvimento

### **Setup Inicial**
```bash
# Setup completo
make setup

# Apenas instalação
make install-dev
```

### **Execução**
```bash
# Executar aplicação
make run

# Modo desenvolvimento
make run-dev
```

### **Testes**
```bash
# Todos os testes
make test

# Com cobertura
make test-cov

# Apenas testes rápidos
make test-fast
```

### **Qualidade de Código**
```bash
# Linting
make lint

# Formatação
make format

# Verificação completa
make dev-check
```

### **Limpeza**
```bash
# Limpar arquivos temporários
make clean

# Remover ambiente virtual
make clean-venv
```

## 📋 Convenções de Nomenclatura

### **Arquivos Python**
- **Snake_case**: `database.py`, `state_manager.py`
- **Módulos**: Nomes descritivos e claros
- **Classes**: PascalCase (quando aplicável)

### **Arquivos de Configuração**
- **Kebab-case**: `pyproject.toml`, `pytest.ini`
- **Prefixo ponto**: `.gitignore`, `.vscode/`

### **Documentação**
- **UPPER_CASE**: `README.md`, `CHANGELOG.md`
- **Snake_case**: `setup_guide.md`, `developer_quick_start.md`

## 🔍 Estrutura de Testes

### **Organização por Módulo**
- Cada módulo em `qa_core/` tem testes correspondentes em `tests/`
- Testes de integração em arquivos separados
- Configuração centralizada em `conftest.py`

### **Cobertura**
- Configurada para 90%+ de cobertura
- Relatórios HTML em `htmlcov/`
- Exclusões configuradas em `pyproject.toml`

## 📚 Documentação

### **Estrutura Hierárquica**
- **`INDEX.md`**: Índice geral e navegação
- **`README.md`**: Documentação técnica principal
- **Guias específicos**: Setup, desenvolvimento, Xray, etc.

### **Manutenção**
- Documentação sempre atualizada
- Links internos funcionais
- Exemplos práticos incluídos

## 🎯 Benefícios da Nova Estrutura

### **Para Desenvolvedores**
- ✅ Navegação mais intuitiva
- ✅ Configurações centralizadas
- ✅ Comandos padronizados via Makefile
- ✅ Separação clara de responsabilidades

### **Para Manutenção**
- ✅ Estrutura escalável
- ✅ Configurações organizadas
- ✅ Testes bem estruturados
- ✅ Documentação acessível

### **Para Onboarding**
- ✅ Setup simplificado
- ✅ Guias claros
- ✅ Estrutura previsível
- ✅ Comandos padronizados

---

**Esta estrutura foi projetada para ser escalável, manutenível e fácil de navegar! 🚀**