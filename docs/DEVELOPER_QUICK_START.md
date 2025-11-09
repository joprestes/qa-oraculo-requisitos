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

```text
qa-oraculo-requisitos/
├── qa_core/                 # Código principal
│   ├── app.py              # Interface Streamlit
│   ├── graph.py            # Grafos de IA (LangGraph)
│   ├── database.py         # SQLite + histórico
│   ├── utils.py            # Utilitários + exportações
│   ├── pdf_generator.py    # Geração de PDFs
│   ├── a11y.py            # Acessibilidade
│   ├── observability.py    # Logs estruturados e trace_id de execução
│   └── ...
├── tests/                  # Testes unitários
├── docs/                   # Documentação
├── main.py                 # Entry point
├── quick-setup.sh         # Setup automático
└── requirements.txt        # Dependências
```

## 🧭 Princípios Obrigatórios

Sempre valide suas contribuições contra estas regras do projeto:

- **Cobertura mínima de 90%** em `pytest --cov` (PRs falham abaixo disso).
- **Acessibilidade primeiro**: todos os componentes devem seguir o checklist WCAG 2.1 AA descrito em `docs/ACESSIBILIDADE.md`.
- **Mobile First**: desenhe fluxos iniciando em resoluções menores e valide em ≤768 px antes de desktop.
- **Boa Arquitetura**: separe responsabilidades (UI, serviços, persistência) e prefira componentes reutilizáveis.
- **Comentários didáticos**: explique o “porquê” e como o QA pode manter o código.

Use o template de PR para confirmar cada item e peça revisão quando algo não puder ser atendido.

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
4. **Implemente** guiando-se pelos princípios acima
5. **Valide**: `make dev-check` ou os comandos individuais (lint, testes, cobertura)
6. **Commit**: `git commit -m "feat: adiciona nova funcionalidade"`
7. **Push**: `git push origin feature/nova-funcionalidade`
8. **Abra** um Pull Request e preencha o checklist

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
# Executar com log detalhado no Streamlit
streamlit run main.py --logger.level debug

# Ou rodar via Python puro (útil para pipelines)
python -m qa_core.app
```

### Observabilidade LangGraph

- Cada execução gera um `trace_id` (UUID) disponível no dicionário de estado.
- O helper `qa_core.observability.log_graph_event` emite logs JSON com:
  - `event`: ex. `node.start`, `model.call.success`.
  - `trace_id` e `node` para correlação.
  - `data`: métricas como duração em ms, retries, erros e tamanho do contexto.
- Os logs aparecem no console padrão; redirecione para arquivo se preferir:

  ```bash
  streamlit run main.py 2>&1 | tee observability.log
  ```

- Integrações com Loki, Datadog, ELK ou OpenTelemetry podem consumir esses mesmos logs estruturados.

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

```text
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
