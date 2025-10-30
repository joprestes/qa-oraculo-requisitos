# 🚀 Developer Quick Start - QA Oráculo

Guia rápido para desenvolvedores que querem contribuir ou entender o projeto.

## ⚡ Setup em 30 segundos

```bash
# Clone e navegue
git clone https://github.com/seu-usuario/qa-oraculo.git
cd qa-oraculo/qa-oraculo-requisitos

# Setup automático
./quick-setup.sh  # Linux/Mac
# ou
quick-setup.bat   # Windows

# Execute
streamlit run main.py
```

## 🏗️ Estrutura do Projeto

```
qa-oraculo-requisitos/
├── qa_core/                 # Código principal
│   ├── app.py              # Interface Streamlit
│   ├── graph.py            # Grafos de IA (LangGraph)
│   ├── database.py         # SQLite + histórico
│   ├── utils.py            # Utilitários + exportações
│   ├── pdf_generator.py    # Geração de PDFs
│   ├── a11y.py            # Acessibilidade
│   └── ...
├── tests/                  # Testes unitários
├── docs/                   # Documentação
├── main.py                 # Entry point
├── quick-setup.sh         # Setup automático
└── requirements.txt        # Dependências
```

## 🧪 Desenvolvimento

### Ambiente de Desenvolvimento
```bash
# Ativar ambiente
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependências de dev
pip install -r requirements-dev.txt

# Executar testes
pytest

# Verificar qualidade
ruff check .
black --check .
```

### Fluxo de Desenvolvimento
1. **Fork** o repositório
2. **Clone** seu fork
3. **Crie** uma branch: `git checkout -b feature/nova-funcionalidade`
4. **Desenvolva** e teste
5. **Commit**: `git commit -m "feat: adiciona nova funcionalidade"`
6. **Push**: `git push origin feature/nova-funcionalidade`
7. **Abra** um Pull Request

## 🔧 Comandos Úteis

### Executar Aplicação
```bash
streamlit run main.py
```

### Executar Testes
```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov

# Teste específico
pytest tests/test_app.py

# Teste com verbose
pytest -v
```

### Qualidade de Código
```bash
# Lint
ruff check .

# Formatação
black .

# Verificar formatação
black --check .
```

### Banco de Dados
```bash
# Reset do banco (desenvolvimento)
rm qa_oraculo_history.db

# Ver histórico
sqlite3 qa_oraculo_history.db ".tables"
```

## 🐛 Debug

### Logs
```bash
# Executar com debug
streamlit run main.py --logger.level debug
```

### Problemas Comuns
1. **Import errors**: Ative o ambiente virtual
2. **API Key**: Verifique o arquivo `.env`
3. **Porta ocupada**: Use `--server.port 8502`

### Estrutura de Testes
```bash
# Executar testes específicos
pytest tests/test_xray_export.py
pytest tests/test_app_history_delete.py
pytest tests/test_utils.py
```

## 📚 Documentação

- **Setup completo**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Documentação técnica**: [docs/README.md](docs/README.md)
- **Guia Xray**: [docs/XRAY_EXPORT_GUIDE.md](docs/XRAY_EXPORT_GUIDE.md)
- **Changelog**: [docs/CHANGELOG.md](docs/CHANGELOG.md)

## 🎯 Contribuindo

### Antes de Contribuir
1. Leia o [CHANGELOG.md](docs/CHANGELOG.md)
2. Execute todos os testes: `pytest`
3. Verifique a qualidade: `ruff check . && black --check .`
4. Teste a aplicação: `streamlit run main.py`

### Padrões de Código
- **Python**: PEP 8 + Black
- **Lint**: Ruff
- **Testes**: Pytest
- **Cobertura**: Mínimo 90%
- **Commits**: Conventional Commits

### Estrutura de Commits
```
feat: adiciona nova funcionalidade
fix: corrige bug na exportação
docs: atualiza documentação
test: adiciona testes para Xray
refactor: reorganiza módulo utils
```

## 🚀 Deploy

### Local
```bash
streamlit run main.py
```

### Produção
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
export GOOGLE_API_KEY="sua_chave"

# Executar
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/qa-oraculo/issues)
- **Documentação**: [docs/](docs/)
- **Email**: seu-email@exemplo.com

---

**Happy Coding!** 🚀
