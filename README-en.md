# 🔮 QA Oracle

<p align="center">
  <img src="assets/logo_oraculo.png" alt="QA Oracle Logo" width="200"/>
</p>

<p align="center">
  <a href="README-en.md" aria-current="page" aria-label="English version of README"><strong>🇺🇸 English</strong></a> | 
  <a href="README.md" aria-label="Switch to Portuguese version of README">🇧🇷 Portuguese</a>
</p>

<p align="center"><i>Requirements Analysis powered by Artificial Intelligence</i></p>

---

## 🚀 Why use QA Oracle?

Tired of **vague user stories** and endless meetings to clarify requirements?  

**QA Oracle** transforms loosely written stories into **test-ready specifications** using cutting-edge AI.

👉 In just a few minutes, you’ll get:
- ✅ Objective acceptance criteria  
- ❓ Smart questions for the PO  
- 🧪 Complete and organized test plans  
- 🧠 Gherkin test scenarios on demand  
- 📄 Exportable reports (.md, .pdf, .xlsx)  

It’s like having a **Senior QA available 24/7**, accelerating planning and reducing bugs before they even appear.

---

## 📸 Interface Preview

![Animated demonstration of QA Oracle showing interactive analysis](assets/qa_oraculo_cartoon_demo.gif)

---

## 🚀 Key Features

- 💻 **Interactive Web Interface** (Streamlit)  
- 📝 **Editable AI Analysis** – human refinement over AI output  
- 🔍 **Ambiguity detection** and question suggestions for the PO  
- ✅ **Verifiable Acceptance Criteria generation**  
- 📊 **Interactive Test Case Table**  
- 📥 **Multi-format export** (`.md`, `.pdf`, Azure, Jira)  
- 📖 **Analysis History** with selective deletion  
- 🏗️ **Modular, Optimized and Tested Code**  

---

## 🛠️ Technologies Used

- 🐍 Python 3.11+  
- 🌐 Streamlit (web interface)  
- 🧠 LangGraph & Google Gemini (AI)  
- 📊 Pandas  
- 📄 FPDF2 (PDF)  
- 📈 Openpyxl (Excel)  

---

## ⚙️ Running Locally

### 📌 Prerequisites
- Python 3.11+  
- Google API Key ([get it here](https://console.cloud.google.com))  

### 🚀 Installation
```bash
# Clone the repository
git clone https://github.com/joprestes/qa-oraculo-requisitos.git
cd qa-oraculo-requisitos

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For testing and dev
```

### 🔑 API Configuration
Create a `.env` file at the root:
```env
GOOGLE_API_KEY="your_api_key_here"
```

### ▶️ Run
```bash
streamlit run app.py
```

🎉 QA Oracle will open automatically in your browser!

---

## 📋 How to Use

1. **Insert your User Story** in the provided field.  
2. Click **“Analyze User Story”**.  
3. **Review and edit** the AI-generated analysis.  
4. Choose to **generate the test plan** or finish.  
5. **Export** to `.md`, `.pdf`, `.xlsx`, Azure or Jira.  
6. Review and manage your **analysis history**.  
7. Click **“New Analysis”** to start over.  

### 🔎 Practical Example
**Input:**  
```
As a banking app user,
I want to reset my password via email,
so I can regain access if I forget it.
```

**Output:**  
- Acceptance Criteria:
  - Reset link sent in less than 1 minute.  
  - The link expires in 24 hours.  
  - New password must have at least 8 characters, including letters and numbers.  

- Questions to the PO:
  - How long should the reset link remain valid?  
  - Is there a limit to password reset attempts per day?  

- Gherkin Scenario:
  ```gherkin
  Scenario: Successfully reset password
    Given the user provides a valid email
    When requests a password reset
    Then receives a valid reset link that expires in 24h
  ```

---

## 🤔 Troubleshooting

❌ **Error: Invalid API Key**  
✔️ Check your `.env` file and ensure the “Generative Language” API is enabled.  

❌ **Error: `streamlit` command not found**  
✔️ Activate your virtual environment (`venv`).  

---

## 🧪 Testing and Quality

- **Coverage ≥97%** with `pytest`.  
- **New tests** ensure a clean and consistent analysis history.  

```bash
pytest
pytest --cov
```

Centralized configuration in `pyproject.toml`:  
- `black` (line length: 88)  
- `pytest` with coverage and warnings disabled  

---

## 🧰 Automatic Setup and Code Quality

QA Oracle includes scripts to automatically configure and validate your development environment in minutes.  
They ensure your local code follows the **same quality standards as the CI (GitHub Actions)**.

### ⚙️ Available Scripts

| System | File | Description |
|---------|-------|-------------|
| 🪟 Windows | `setup.bat` | Creates `.venv`, installs dependencies, runs Black, Ruff, Pytest, and TOML validation. |
| 🐧 Linux / 🍎 macOS | `setup.sh` | Equivalent version, compatible with POSIX shells. |

---

### ▶️ Quick Start

**Windows**
```bash
setup.bat
```

**Linux / Mac**
```bash
chmod +x setup.sh
./setup.sh
```

These scripts automatically execute:
1. 🧱 Create virtual environment `.venv`
2. 📦 Install dependencies (`requirements.txt`)
3. 🎯 Format check with **Black**
4. 🧹 Lint with **Ruff**
5. 🧩 Validate `pyproject.toml` syntax
6. 🧪 Run unit tests and coverage report

> 💡 The terminal will display “✅ Setup completed successfully!” when everything matches the CI standards.

---

### 🧠 Individual Commands
| Task | Command |
|------|----------|
| Format code | `black .` |
| Check lint | `ruff check .` |
| Run tests with coverage | `pytest --cov --cov-report=term-missing` |
| Validate TOML | `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('✅ Valid TOML!')"` |

---

### 🔄 Continuous Integration (CI)

Each *push* or *pull request* to the `main` branch runs the CI workflow:

- ✅ **Black**: ensures PEP8 compliance  
- 🔎 **Ruff**: enforces good practices and import order  
- 🧪 **Pytest**: runs all unit tests  
- 📊 **Minimum required coverage**: **90%**

File: [`/.github/workflows/ci.yml`](.github/workflows/ci.yml)

> 💬 Any lint or coverage failures will block merging, maintaining repository integrity.

---

## 📘 Technical Documentation

For deeper technical details, contribution guide, and CI configuration:  
👉 [`TECHNICAL_DOCUMENTATION_EN.md`](TECHNICAL_DOCUMENTATION_EN.md)

---

## 📌 Roadmap

- [x] Web interface with Streamlit  
- [x] Export to `.md`, `.pdf`, Azure, Jira  
- [x] Analysis history with selective deletion  
- [x] Continuous Integration (CI) with 90% coverage threshold  
- [ ] Automated Accessibility Validation (Pa11y + WCAG 2.1)  
- [ ] Living documentation (MkDocs + GitHub Pages)  
- [ ] E2E Tests with Playwright  

---

## 🤝 Contributing

Contributions are welcome!  
- Open an **issue** for bugs or enhancements.  
- Submit a **Pull Request** with your improvements.  

⭐ If you found this project helpful, give it a **star**!

---

## 📜 License

This project is licensed under **CC BY-NC 4.0**.  
**Personal and academic use allowed**, **commercial use prohibited**.  

More details at [Creative Commons](https://creativecommons.org/licenses/by-nc/4.0/).
