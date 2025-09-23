<p align="center">
  <img src="assets/logo_oraculo.png" alt="QA Oracle Logo" width="200"/>
</p>

<h1 align="center">🔮 QA Oracle</h1>
<p align="center"><i>Requirement Analysis powered by Artificial Intelligence</i></p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg"/>
  <img src="https://img.shields.io/badge/license-MIT-green.svg"/>
  <img src="https://img.shields.io/badge/Streamlit-App-red.svg"/>
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg"/>
</p>

<nav aria-label="Language switcher" style="text-align: right;">
<a href="README-en.md" aria-current="page">🇺🇸 <strong>English</strong></a> |
<a href="README.md">🇧🇷 Português</a>
</nav>

## 🚀 Why QA Oracle?

Tired of **vague User Stories** and **endless meetings** to align understanding?  

**QA Oracle** turns raw requirements into **test-ready specifications** using cutting-edge AI.  

👉 In just **minutes**, you get:  
- ✅ Clear and objective acceptance criteria  
- ❓ Smart questions for the PO  
- 📝 Complete and organized test plans  
- 🧪 On-demand Gherkin scenarios  
- 📄 Exportable reports (.md, .pdf, .xlsx)  

It’s like having a **Senior QA available 24/7**, speeding up planning and reducing issues before the first bug appears.  

---

## 📸 Interface Preview

![alt text](assets/qa_oraculo_cartoon_demo.gif)

---

## 🚀 Main Features

| 🔧 Feature | 💡 Description |
|------------|----------------|
| 💻 **Web Interface** | Built with Streamlit, interactive and user-friendly |
| 🔍 **Ambiguity Detection** | Suggests clarifying questions for the PO |
| ✅ **Acceptance Criteria** | Clear, testable, and objective |
| 📝 **Test Plans & Gherkin** | On-demand test cases in Gherkin format |
| 📊 **Interactive Table** | Test cases rendered and sortable with Pandas |
| 📥 **Multiple Export Options** | .md, .pdf, .xlsx (Azure DevOps, Jira Zephyr) |
| 🔄 **Flexible Workflow** | Choose detailed test plan generation or quick analysis |
| 🏗️ **Modular Architecture** | Refactored codebase for easy maintenance and scaling |

---

## 🛠️ Tech Stack

- 🐍 Python 3.11+  
- 🌐 Streamlit (Web Interface Framework)  
- 🧠 LangGraph & Google Gemini (Orchestration and AI Model)  
- 📊 Pandas (Data Handling)  
- 📄 FPDF2 (PDF Report Generation)  
- 📈 Openpyxl (Excel .xlsx handling)  

---

## ⚙️ How to Run Locally

<details>
<summary><b>📌 Requirements</b></summary>

- Python 3.11+  
- Google API Key (get it [here](https://console.cloud.google.com))  

</details>

<details>
<summary><b>🚀 Installation</b></summary>

```bash
# Clone the repository
git clone https://github.com/joprestes/qa-oraculo-requisitos.git
cd qa-oraculo-requisitos

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```
</details>

<details>
<summary><b>🔑 API Setup</b></summary>

Create a `.env` file at the project root with:  

```env
GOOGLE_API_KEY="your_api_key_here"
```
</details>

<details>
<summary><b>▶️ Run</b></summary>

```bash
streamlit run app.py
```

🎉 QA Oracle will open automatically in your browser!
</details>

---

## 📋 How to Use

1. **Insert a User Story** → Paste the User Story to analyze.  
2. **Start Analysis** → Click "Analyze User Story" to generate the initial report.  
3. **Decide Next Step** → Choose between generating a full test plan or finishing with initial analysis.  
4. **Export Results** → Use the download buttons. For Azure/Jira, configure the customizable fields.  
5. **Start Over** → Click "New Analysis" to reset and begin a new cycle.  

---

## 🤔 Troubleshooting

❌ **Error:** Invalid API Key  
✔️ Check if the `.env` file is at the project root and ensure the “Generative Language” API is enabled on Google Cloud.  

❌ **Error:** `streamlit` command not found  
✔️ Make sure the `venv` environment is activated.  

---

## 📌 Roadmap

- [x] Interactive web interface with Streamlit  
- [x] Acceptance criteria & PO questions generation  
- [x] On-demand test plan generation  
- [x] Export to .md and .pdf reports  
- [x] Export to Azure DevOps (.xlsx)  
- [x] Export to Jira Zephyr (.xlsx)  
- [x] Refactored modular codebase  
- [ ] Caching of results to optimize API calls  
- [ ] Implement pytest test suite  
- [ ] Externalize prompts in `config.yaml`  
- [ ] Interactive editing of initial analysis by the user  

---

## 🤝 Contributing

Contributions are always welcome!  
- Open an **issue** to report bugs or suggest improvements  
- Submit a **Pull Request** with new features  

⭐ If this project helped you, don’t forget to give it a **star on GitHub**!
