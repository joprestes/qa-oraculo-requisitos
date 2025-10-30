# 📁 Estrutura do Projeto - QA Oráculo

Este documento descreve a organização e estrutura do projeto QA Oráculo.

## 🏗️ Estrutura de Diretórios

```
qa-oraculo-requisitos/
├── 📁 docs/                          # 📚 Documentação completa
│   ├── INDEX.md                      # Índice geral da documentação
│   ├── README.md                     # Documentação técnica
│   ├── SETUP_GUIDE.md                # Guia de instalação
│   ├── DEVELOPER_QUICK_START.md      # Guia para desenvolvedores
│   ├── CHANGELOG.md                  # Histórico de mudanças
│   ├── XRAY_EXPORT_GUIDE.md          # Guia de exportação Xray
│   ├── acessibilidade.md             # Guia de acessibilidade
│   ├── CAMPOS_PERSONALIZADOS_XRAY.md # Campos customizados Xray
│   ├── RESUMO_FINAL_XRAY.md          # Resumo implementação Xray
│   ├── XRAY_IMPLEMENTATION_SUMMARY.md # Resumo técnico Xray
│   └── DOCUMENTACAO_TECNICA.md       # Documentação técnica (legado)
│
├── 📁 qa_core/                       # 🧩 Código principal
│   ├── __init__.py                   # Inicialização do módulo
│   ├── app.py                        # Interface Streamlit
│   ├── graph.py                      # Grafos de IA (LangGraph)
│   ├── database.py                   # Persistência SQLite
│   ├── utils.py                      # Utilitários e exportações
│   ├── pdf_generator.py              # Geração de PDFs
│   ├── a11y.py                       # Recursos de acessibilidade
│   ├── config.py                     # Configurações
│   ├── prompts.py                    # Prompts da IA
│   ├── schemas.py                    # Esquemas de dados
│   └── state_manager.py              # Gerenciamento de estado
│
├── 📁 tests/                         # 🧪 Testes unitários
│   ├── conftest.py                   # Fixtures globais
│   ├── test_app.py                   # Testes da interface
│   ├── test_database.py              # Testes do banco
│   ├── test_graph.py                 # Testes da IA
│   ├── test_utils.py                 # Testes de utilitários
│   ├── test_xray_export.py           # Testes Xray
│   ├── test_a11y.py                  # Testes acessibilidade
│   └── ...                          # Outros testes
│
├── 📁 assets/                        # 🎨 Recursos visuais
│   ├── logo_oraculo.png              # Logo do projeto
│   └── qa_oraculo_cartoon_demo.gif   # Demo animado
│
├── 📄 README.md                      # 📖 README principal
├── 📄 main.py                        # 🚀 Entry point
├── 📄 setup.py                       # Configuração do pacote
├── 📄 pyproject.toml                 # Configuração do projeto
├── 📄 pytest.ini                    # Configuração dos testes
├── 📄 requirements.txt               # Dependências principais
├── 📄 requirements-dev.txt           # Dependências de desenvolvimento
├── 📄 quick-setup.sh                 # Setup automático Linux/Mac
├── 📄 quick-setup.bat                # Setup automático Windows
├── 📄 setup.sh                       # Setup completo Linux/Mac
├── 📄 setup.bat                      # Setup completo Windows
├── 📄 pyrightconfig.json             # Configuração Pyright
├── 📄 qa_oraculo_history.db          # Banco de dados SQLite
└── 📄 LICENSE                        # Licença do projeto
```

## 📚 Organização da Documentação

### 🎯 Por Público-Alvo

| Público | Documentos Principais |
|---------|----------------------|
| **Usuários Novos** | `docs/SETUP_GUIDE.md` |
| **Desenvolvedores** | `docs/DEVELOPER_QUICK_START.md`, `docs/README.md` |
| **QA/Usuários Xray** | `docs/XRAY_EXPORT_GUIDE.md` |
| **Contribuidores** | `docs/DEVELOPER_QUICK_START.md` |

### 📋 Por Categoria

| Categoria | Documentos |
|-----------|------------|
| **Setup/Instalação** | `SETUP_GUIDE.md`, `DEVELOPER_QUICK_START.md` |
| **Técnica** | `README.md`, `DOCUMENTACAO_TECNICA.md` |
| **Funcionalidades** | `XRAY_EXPORT_GUIDE.md`, `acessibilidade.md` |
| **Xray** | `CAMPOS_PERSONALIZADOS_XRAY.md`, `RESUMO_FINAL_XRAY.md`, `XRAY_IMPLEMENTATION_SUMMARY.md` |
| **Projeto** | `CHANGELOG.md`, `INDEX.md` |

## 🎯 Benefícios da Nova Organização

### ✅ **Estrutura Limpa**
- Documentação centralizada em `docs/`
- Código principal em `qa_core/`
- Testes organizados em `tests/`
- Scripts de setup na raiz

### ✅ **Navegação Fácil**
- `docs/INDEX.md` como ponto de entrada
- Documentos categorizados por público-alvo
- Links atualizados no README principal

### ✅ **Manutenção Simplificada**
- Documentação separada do código
- Estrutura consistente
- Fácil localização de arquivos

### ✅ **Onboarding Melhorado**
- Guias específicos para cada tipo de usuário
- Setup automático simplificado
- Documentação progressiva

## 🚀 Como Navegar

### 👤 **Sou novo no projeto**
1. Leia `README.md` (raiz)
2. Siga `docs/SETUP_GUIDE.md`
3. Execute `quick-setup.sh` ou `quick-setup.bat`

### 👨‍💻 **Sou desenvolvedor**
1. Veja `docs/DEVELOPER_QUICK_START.md`
2. Consulte `docs/README.md` para detalhes técnicos
3. Explore `qa_core/` para entender o código

### 🧪 **Sou QA e quero usar Xray**
1. Leia `docs/XRAY_EXPORT_GUIDE.md`
2. Configure campos em `docs/CAMPOS_PERSONALIZADOS_XRAY.md`
3. Teste a exportação

### 📚 **Quero explorar toda documentação**
1. Comece com `docs/INDEX.md`
2. Navegue pelas categorias
3. Use os links internos para aprofundar

---

**Última atualização**: 2025-10-29
