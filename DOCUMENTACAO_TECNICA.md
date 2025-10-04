# 🧠 Documentação Técnica – QA Oráculo

Este documento descreve a arquitetura, automações e padrões de qualidade do projeto **QA Oráculo**.

---

## ⚙️ Integração Contínua (CI)

Arquivo: `.github/workflows/ci.yml`

### Etapas principais
1. **Checkout** do repositório  
2. **Setup Python** (3.11 – 3.13)  
3. **Cache do pip**  
4. **Instala dependências e ferramentas de qualidade**  
5. **Lint (Black)** – verificação de formatação  
6. **Lint (Ruff)** – boas práticas e imports  
7. **Testes + cobertura** (`pytest --cov`)  
8. **Gate de cobertura** ≥ 90 %  
9. **Validação do pyproject.toml**

---

## 🧰 Scripts de Setup

### setup.sh (Linux/Mac)
Executa:
1. Criação do ambiente `.venv`
2. Instalação de dependências e ferramentas (Black, Ruff, Pytest)
3. Validação do `pyproject.toml`
4. Execução de lint e testes com cobertura

### setup.bat (Windows)
Fluxo equivalente adaptado para o shell do Windows.

---

## 🧩 Estrutura de Código

```
qa-oraculo/
├── app.py              # Interface Streamlit
├── graph.py            # Fluxos de IA (LangGraph + Gemini)
├── utils.py            # Funções utilitárias
├── pdf_generator.py    # Relatórios PDF
├── database.py         # Persistência local (SQLite)
├── state_manager.py    # Estado de sessão
└── tests/              # Testes unitários
```

---

## 🧪 Testes e Qualidade

- Framework: **Pytest**
- Banco de testes: **SQLite em memória**
- Cobertura mínima exigida: **90 %**
- Execução local:
  ```bash
  pytest --cov --cov-report=term-missing
  ```

---

## 🧱 Convenções de Código

| Área | Ferramenta | Configuração |
|------|-------------|--------------|
| Formatação | `black` | Linha 88 |
| Lint | `ruff` | Regras definidas em `[tool.ruff.lint]` no `pyproject.toml` |
| Testes | `pytest` | Diretório `tests/` |
| Documentação | Google-style docstrings | Todos os módulos públicos |

---

## 🧩 Boas Práticas

1. Rodar `./setup.sh` (ou `setup.bat`) antes de commitar.  
2. Garantir que `ruff check .` e `black --check .` estejam limpos.  
3. Confirmar cobertura ≥ 90 %.  
4. Usar commits semânticos (`feat:`, `fix:`, `ci:`, `docs:` etc.).  

---

## 🧱 Planejamento de Evolução

| Fase | Objetivo |
|------|-----------|
| **Fase 1 (Atual)** | CI completo + validações automáticas (Black, Ruff, Pytest, TOML) |
| **Fase 2** | Acessibilidade automática (Pa11y + WCAG 2.1) |
| **Fase 3** | Documentação viva (MkDocs + GitHub Pages) |
| **Fase 4** | Testes E2E com Playwright |
| **Fase 5 (opcional)** | Integração com pipelines externos (sem containerização) |

---

## ⚙️ Ambiente de Execução

O QA Oráculo **não utiliza containerização**.  
Todo o ambiente é gerenciado via **Python Virtual Environment (.venv)**,  
garantindo isolamento e compatibilidade com o CI.

### Vantagens do modelo venv
- 🧩 Compatível com Windows, Linux e macOS  
- ⚙️ Simples de reproduzir localmente (`setup.sh` / `setup.bat`)  
- 🔄 Idêntico ao ambiente usado no GitHub Actions  
- 💡 Menos sobrecarga e dependências externas  

> 💬 Caso a equipe precise integrar com sistemas externos no futuro, o projeto já está modularizado para suportar isso sem containerização.

---

## 📜 Licença

Uso pessoal e acadêmico permitido sob **CC BY-NC 4.0**.  
Proibido uso comercial.