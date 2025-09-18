<nav aria-label="Language switcher" style="text-align: right;">
  <a href="README.md" aria-current="page">🇺🇸 <strong>English</strong></a> | 
  <a href="README-pt.md">🇧🇷 Português</a>
</nav>

# 🔮 QA Oracle: AI-Powered Requirements Analysis

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)
![Test Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen.svg)

---

## 🚀 Why QA Oracle?

Tired of **vague User Stories** and endless meetings to “align expectations”?  
**QA Oracle** uses **cutting-edge AI** to turn raw requirements into **test-ready specifications**.  

In just minutes, you’ll get:  
- ✅ Clear acceptance criteria.  
- ❓ Smart questions for the Product Owner.  
- 📝 Structured, ready-to-use test plans.  
- 🧪 On-demand Gherkin scenarios.  

It’s like having a **senior QA always available**, accelerating planning and catching risks before the first bug appears.  

---

## 🚀 Key Features

- 💻 **Interactive Web Interface** built with **Streamlit**.  
- 🔍 **Ambiguity detection** with follow-up questions for the PO.  
- ✅ **Objective Acceptance Criteria** generation.  
- 📝 **Interactive Test Plans** and on-demand Gherkin scenarios.  
- ♿ **Accessibility focus (A11y)** with WCAG-based test scenarios.  
- 📊 **Interactive Test Case Table** sortable via **Pandas**.  
- 📥 **Export Reports** in Markdown format.  

---
## 📸  Interface Preview

![QA Oráculo Demo](assets/qa_oraculo_cartoon_demo.gif)

---

## 🛠️ Tech Stack

- 🐍 **Python 3.11+**  
- 🌐 **Streamlit** (Web UI Framework)  
- 🧠 **LangGraph & Google Gemini** (AI Orchestration and Model)  
- 📊 **Pandas** (Data handling for the UI)  
- 🧪 **Unittest & Coverage.py** (Testing and Coverage)  

---

## ⚙️ Running Locally

### Requirements
- Python 3.11+  
- Google API Key ([get it here](https://aistudio.google.com/app/apikey))  

### Installation
```bash
# Clone the repository
git clone https://github.com/joprestes/qa-oracle-requirements.git
cd qa-oracle-requirements

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .\.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### API Setup
Create a `.env` file at the project root with the following content:  

```env
GOOGLE_API_KEY="your_api_key_here"
```

### Run the App
```bash
streamlit run app.py
```

🎉 Done! QA Oracle will open in your browser.  

---

## 🧪 Quality & Testing

The project is backed by a robust unit test suite validating backend logic.  

- **Test Coverage**: business logic in `graph.py` reached **99% line coverage**, ensuring reliability.  
- **Run Tests**:  
  ```bash
  python -m unittest discover tests/
  ```
- **Check Coverage**:  
  ```bash
  coverage run -m unittest discover tests/ && coverage report -m
  ```

---

## 🤔 Troubleshooting

❌ **Error**: Invalid API Key  
✔️ Make sure `.env` is at the project root and the “Generative Language” API is enabled in Google Cloud.  

❌ **Error**: `streamlit` command not found  
✔️ Ensure your virtual environment `.venv` is activated. Reinstall dependencies if needed.  

---

## 📌 Roadmap

- ✅ Interactive web interface with Streamlit  
- ✅ Acceptance criteria and PO questions generation  
- ✅ On-demand complete test plans  
- 📄 PDF report export  
- 🔗 Jira API integration for issue creation and updates  
- 📦 Batch analysis of multiple requirements  

---

## 🤝 Contributing

Contributions are welcome!  
- Open an **issue** to report bugs or suggest improvements.  
- Send a **Pull Request** with new features.  
- ⭐ If this project helped you, leave a star on the repo!  

---

