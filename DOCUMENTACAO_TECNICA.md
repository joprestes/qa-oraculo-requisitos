# 🧠 Documentação Técnica – QA Oráculo

[![CI](https://github.com/joprestes/qa-oraculo-requisitos/actions/workflows/ci.yml/badge.svg)](https://github.com/joprestes/qa-oraculo-requisitos/actions/workflows/ci.yml)  
[![Coverage](https://img.shields.io/badge/Coverage-97%25-brightgreen)](https://github.com/joprestes/qa-oraculo-requisitos)

## 📚 Sumário

- [⚙️ Integração Contínua (CI)](#-integração-contínua-ci)
- [🧰 Scripts de Setup](#-scripts-de-setup)
- [🧩 Estrutura de Código](#-estrutura-de-código)
- [🏗 Arquitetura Interna](#-arquitetura-interna)
- [🧪 Testes e Qualidade](#-testes-e-qualidade)
- [🧱 Convenções de Código](#-convenções-de-código)
- [🧩 Boas Práticas](#-boas-práticas)
- [🧱 Planejamento de Evolução](#-planejamento-de-evolução)
- [⚙️ Ambiente de Execução](#-ambiente-de-execução)
- [🔒 Segurança e Privacidade](#-segurança-e-privacidade)
- [💡 Créditos Técnicos](#-créditos-técnicos)
- [📆 Histórico de Versões](#-histórico-de-versões)

---

## ⚙️ Integração Contínua (CI)

Arquivo: `.github/workflows/ci.yml`

### Etapas
1. Checkout do repositório  
2. Setup Python (3.11–3.13)  
3. Cache do pip  
4. Instala dependências e ferramentas de qualidade  
5. Lint (Black) e Ruff  
6. Testes e cobertura (`pytest --cov`)  
7. Gate de cobertura ≥ 90 %  
8. Validação do `pyproject.toml`

---

## 🧰 Scripts de Setup

### setup.sh (Linux/Mac)
- Criação de `.venv`
- Instalação de dependências
- Lint, formatação e testes automáticos
- Validação de `pyproject.toml`

### setup.bat (Windows)
Fluxo equivalente para o shell do Windows.

---

## 🧩 Estrutura de Código

```text
qa-oraculo/
├── app.py              # Interface Streamlit
├── graph.py            # Fluxos de IA (LangGraph + Gemini)
├── utils.py            # Funções auxiliares
├── pdf_generator.py    # Geração de relatórios PDF
├── database.py         # Persistência (SQLite)
├── state_manager.py    # Estado da sessão
└── tests/              # Testes unitários
```

---

## 🏗 Arquitetura Interna

```mermaid
graph LR
  UI[app.py] --> AI[graph.py (LangGraph + Gemini)]
  AI --> DB[database.py (SQLite)]
  AI --> PDF[pdf_generator.py]
  UI --> STATE[state_manager.py]
```

- `graph.py`: centraliza o fluxo de raciocínio da IA.  
- `app.py`: camada de interface e entrada de dados.  
- `database.py`: persistência local e caching leve.  
- `pdf_generator.py`: exportação de relatórios.  

---

## 🧪 Testes e Qualidade

- Framework: **Pytest**  
- Banco de testes: **SQLite in-memory**  
- Cobertura mínima: **90 % (meta: 97 %)**  
- Execução:
  ```bash
  pytest --cov --cov-report=term-missing
  ```

---

## 🧱 Convenções de Código

| Área | Ferramenta | Observação |
|------|-------------|------------|
| Formatação | Black | Configuração no `pyproject.toml` |
| Lint | Ruff | Regras de estilo e imports |
| Testes | Pytest | Diretório `tests/` |
| Docstrings | Google Style | Padrão uniforme para APIs públicas |

---

## 🧩 Boas Práticas

1. Rodar `setup.sh` (ou `.bat`) antes do commit.  
2. Garantir lint limpo (`ruff check .`, `black --check .`).  
3. Cobertura mínima ≥ 90 %.  
4. Commits semânticos (`feat:`, `fix:`, `docs:`, `ci:`).  

---

## 🧱 Planejamento de Evolução

| Fase | Objetivo | Critério de Conclusão |
|------|-----------|--------------------------|
| Fase 1 | CI completo + validações automáticas | Build verde |
| Fase 2 | Acessibilidade (Pa11y + WCAG 2.1) | ≥ 95 % conformidade |
| Fase 3 | Documentação viva (MkDocs + Pages) | Publicação automática |
| Fase 4 | Testes E2E (Playwright) | Execução via CI |
| Fase 5 | Integração externa (sem container) | Compatibilidade validada |

---

## ⚙️ Ambiente de Execução

- Base em **Python Virtual Environment (.venv)**  
- Compatível com Windows, Linux, macOS  
- CI usa o mesmo ambiente (`setup.sh` idêntico ao pipeline)

---

## 🔒 Segurança e Privacidade

- As **User Stories** não são armazenadas fora do ambiente local.  
- As chamadas à API Gemini utilizam chave segura via `.env`.  
- Nenhum dado sensível é persistido permanentemente.  

---

## 💡 Créditos Técnicos

- 🧠 **IA:** [LangGraph](https://github.com/langchain-ai/langgraph) + [Google Gemini](https://deepmind.google/technologies/gemini/)  
- 🖥 **Interface:** [Streamlit](https://streamlit.io)  
- 🧩 **Infraestrutura:** GitHub Actions, Ruff, Black, Pytest  
- ✨ **Autor e Mantenedor:** [Jo Prestes](https://github.com/joprestes)

---

## 📆 Histórico de Versões

| Versão | Data | Alterações |
|--------|------|-------------|
| **1.3.0** | Outubro/2025 | Novo diagrama, seção de segurança e créditos técnicos |
| **1.2.0** | Jul/2025 | Melhorias de setup e estrutura |
| **1.0.0** | Abr/2025 | Primeira versão técnica documentada |
