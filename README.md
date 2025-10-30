# 🔮 QA Oráculo

Ferramenta de análise inteligente de User Stories com geração automática de planos de teste e cenários Gherkin.

## 🚀 Quick Start

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar API Key
echo 'GOOGLE_API_KEY="sua_chave_aqui"' > .env

# Executar aplicação
streamlit run main.py
```

**⚠️ IMPORTANTE**: Use `streamlit run main.py` (não `qa_core/app.py`)

## 📚 Documentação Completa

Veja a documentação completa em: **[docs/README.md](docs/README.md)**

## ✨ Funcionalidades

- 🤖 Análise IA de User Stories
- ✏️ Edição interativa de critérios de aceite
- 🧪 Geração de cenários Gherkin
- 📥 Exportação para:
  - Markdown (.md)
  - PDF (.pdf)
  - Azure DevOps (.csv)
  - Jira Zephyr (.xlsx)
  - **Xray Test Management (.csv)** 🆕
- 📖 Histórico de análises

## 🆕 Novidade: Exportação Xray

Exporte seus cenários Cucumber direto para o Xray (Jira Test Management):

- ✅ CSV compatível com Xray Test Case Importer
- ✅ Suporte a campos personalizados (Labels, Priority, Component, etc.)
- ✅ Campos customizados ilimitados
- ✅ Test Repository Folder configurável

Veja o guia completo: [docs/XRAY_EXPORT_GUIDE.md](docs/XRAY_EXPORT_GUIDE.md)

## 🧪 Testes

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov
```

## 📄 Licença

CC BY-NC 4.0 - Uso pessoal e acadêmico permitido.

---

**Desenvolvido com 💜 por Joelma Prestes Ferreira**
