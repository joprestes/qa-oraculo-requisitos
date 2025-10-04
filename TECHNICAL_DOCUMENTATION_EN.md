# 🧠 Technical Documentation – QA Oracle

This document describes the architecture, automations, and quality standards of the **QA Oracle** project.

---

## ⚙️ Continuous Integration (CI)

File: `.github/workflows/ci.yml`

### Main Workflow Steps
1. **Checkout** repository  
2. **Setup Python** (3.11 – 3.13)  
3. **Cache pip**  
4. **Install dependencies and quality tools**  
5. **Lint (Black)** – code formatting validation  
6. **Lint (Ruff)** – best practices and import order check  
7. **Tests + Coverage** (`pytest --cov`)  
8. **Coverage Gate** ≥ 90 %  
9. **Validate `pyproject.toml` syntax**

---

## 🧰 Setup Scripts

### setup.sh (Linux/Mac)
Performs:
1. Creation of the virtual environment `.venv`
2. Installation of dependencies and tools (Black, Ruff, Pytest)
3. Validation of `pyproject.toml`
4. Execution of lint and tests with coverage

### setup.bat (Windows)
Equivalent flow adapted for Windows shell.

---

## 🧩 Project Structure

```
qa-oraculo/
├── app.py              # Streamlit interface
├── graph.py            # AI workflow (LangGraph + Gemini)
├── utils.py            # Utility functions
├── pdf_generator.py    # PDF report generation
├── database.py         # Local persistence (SQLite)
├── state_manager.py    # Session state management
└── tests/              # Unit tests
```

---

## 🧪 Testing and Quality

- Framework: **Pytest**
- Test database: **SQLite in-memory**
- Minimum required coverage: **90 %**
- Run locally:
  ```bash
  pytest --cov --cov-report=term-missing
  ```

---

## 🧱 Code Conventions

| Area | Tool | Configuration |
|------|------|----------------|
| Formatting | `black` | Line length: 88 |
| Lint | `ruff` | Rules in `[tool.ruff.lint]` section of `pyproject.toml` |
| Tests | `pytest` | Tests located in `tests/` |
| Docstrings | Google-style | All public modules |

---

## 🧩 Best Practices

1. Run `./setup.sh` (or `setup.bat`) before committing.  
2. Ensure `ruff check .` and `black --check .` are clean.  
3. Confirm coverage ≥ 90 %.  
4. Use semantic commits (`feat:`, `fix:`, `ci:`, `docs:` etc.).  

---

## 🧱 Evolution Roadmap

| Phase | Goal |
|-------|------|
| **Phase 1 (Current)** | Full CI + automated validations (Black, Ruff, Pytest, TOML) |
| **Phase 2** | Automatic accessibility validation (Pa11y + WCAG 2.1) |
| **Phase 3** | Living documentation (MkDocs + GitHub Pages) |
| **Phase 4** | E2E Tests with Playwright |
| **Phase 5 (optional)** | Integration with external pipelines (no containerization) |

---

## ⚙️ Runtime Environment

QA Oracle **does not use containerization**.  
The entire environment is managed through **Python Virtual Environments (.venv)**,  
ensuring isolation and full compatibility with the CI.

### Advantages of venv model
- 🧩 Works on Windows, Linux, and macOS  
- ⚙️ Easy to reproduce locally (`setup.sh` / `setup.bat`)  
- 🔄 Matches the environment used in GitHub Actions  
- 💡 Minimal overhead and external dependencies  

> 💬 If future integrations are needed, the modular architecture already supports external systems without containerization.

---

## 📜 License

Personal and academic use allowed under **CC BY-NC 4.0**.  
Commercial use is prohibited.
