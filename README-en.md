<nav aria-label="Language switcher" style="text-align: right;">
  <a href="README.md" aria-current="page">🇺🇸 <strong>English</strong></a> | 
  <a href="README-pt.md">🇧🇷 Português</a>
</nav>

# 🔮 QA Oracle: Requirements Analysis with AI

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)
![Test Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen.svg)
---

## 🚀 Why QA Oracle?

Tired of **vague User Stories** and endless meetings to "align understandings"?  
**QA Oracle** leverages **cutting-edge AI** to transform loose requirements into **test-ready specifications**.  

In minutes, you will get:  
- ✅ Objective acceptance criteria.  
- ❓ Smart questions for the Product Owner.  
- 📝 Complete and organized test plans.  
- 🧪 Gherkin scenarios on demand.  
- 📄 Exportable reports in PDF with professional formatting.  

It’s like having a **senior QA always available**, speeding up planning and reducing failures even before the first bug appears.  

---
## 📸 Interface Preview

![QA Oracle Demo](assets/qa_oraculo_cartoon_demo.gif)

---

## 🚀 Key Features

-   💻 **Interactive Web Interface** built with **Streamlit**.  
-   🔍 **Ambiguity detection** and suggestion of questions for the PO.  
-   ✅ **Generation of objective and verifiable Acceptance Criteria**.  
-   📝 **Interactive Test Plans** and Gherkin test cases on demand.  
-   ♿ **Accessibility (A11y) focus**, with scenarios based on WCAG guidelines.  
-   📊 **Interactive and sortable Test Case Table**, rendered with **Pandas**.  
-   📥 **Download Reports** in **Markdown** or **professionally formatted PDF**.  

---

## 🛠️ Technologies Used

-   🐍 **Python 3.11+**  
-   🌐 **Streamlit** (Web Interface Framework)  
-   🧠 **LangGraph & Google Gemini** (Orchestration and AI Model)  
-   📊 **Pandas** (Data Manipulation for UI)  
-   🧪 **Unittest & Coverage.py** (Testing and Code Coverage)  
-   📄 **FPDF** (PDF Report Generation)  

---

## ⚙️ How to Run Locally

### Prerequisites
-   Python 3.11+  
-   Google API Key ([get it here](https://aistudio.google.com/app/apikey))  

### Installation
```bash
# Clone the repository
git clone https://github.com/joprestes/qa-oraculo-requisitos.git
cd qa-oraculo-requisitos

# Create and activate the virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .\.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### API Configuration
Create a `.env` file in the project root with the following content:  

```env
GOOGLE_API_KEY="your_api_key_here"
```

### Run
```bash
streamlit run app.py
```

🎉 Done! QA Oracle will open in your browser.  

---

## 🧪 Quality and Testing

Project quality is ensured by a robust unit test suite that validates backend logic.  

- **Test Coverage**: The business logic in `graph.py` module reached **99% line coverage**, ensuring high reliability.  
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
✔️ Ensure that the `.env` file is in the project root and that the “Generative Language” API is active in Google Cloud.  

❌ **Error**: `streamlit` command not found  
✔️ Make sure the `.venv` virtual environment is activated. If necessary, reinstall dependencies.  

---

## 📌 Roadmap

- ✅ Interactive web interface with Streamlit  
- ✅ Generation of acceptance criteria and PO questions  
- ✅ On-demand full test plan generation  
- ✅ Export of reports in PDF format with cover page, colored tables, and elegant footer  
- 🔗 Integration with Jira APIs to create and populate issues  
- 📦 Automatic batch analysis of multiple requirements  

---

## 🤝 Contributing

Your contribution is very welcome!  
- Open an **issue** to report bugs or suggest improvements.  
- Submit a **Pull Request** with new features.  
- ⭐ If this project helped you, give the repository a star!  

---
