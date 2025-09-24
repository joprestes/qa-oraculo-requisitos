<p align="center">
  <img src="assets/logo_oraculo.png" alt="QA Oracle Logo" width="200"/>
</p>

<h1 align="center">🔮 QA Oracle</h1>
<p align="center"><i>Requirements Analysis with Artificial Intelligence</i></p>

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

## 🚀 Why use QA Oracle?

Tired of **vague User Stories** and **endless meetings** to align understanding?

**QA Oracle** transforms scattered requirements into **ready-to-test specifications** using cutting-edge AI.

👉 In just **minutes**, you’ll have:
- ✅ Clear acceptance criteria  
- ❓ Smart questions for the PO  
- 📝 Complete and well-structured test plans  
- 🧪 On-demand Gherkin scenarios  
- 📄 Exportable reports (.md, .pdf, .xlsx)  

It’s like having a **Senior QA available 24/7**, accelerating planning and preventing failures even before the first bug appears.

---

## 📸 Interface Preview

![alt text](assets/qa_oraculo_cartoon_demo.gif)

---

## 🚀 Main Features

- 💻 **Interactive Web Interface** built with **Streamlit**.  
- 📝 **Editable and Interactive Analysis:** <!-- NEW --> After the AI generates the initial analysis, the application displays an editable form. The user can refine, correct, and add information (acceptance criteria, risks, etc.) before proceeding, ensuring that the final test plan is based on requirements validated by a human.  
- 🔍 **Ambiguity Detection** and smart questions for the PO.  
- ✅ **Acceptance Criteria Generation** that are clear and verifiable.  
- 📊 **Test Case Table** interactive and sortable.  
- 📥 **Multiple Export Options** (`.md`, `.pdf`, Azure and Jira).  
- 🏗️ **Modular, Optimized, and 100% Tested Code.**  

---

## 🛠️ Technologies Used

- 🐍 Python 3.11+  
- 🌐 Streamlit (Web UI Framework)  
- 🧠 LangGraph & Google Gemini (AI orchestration)  
- 📊 Pandas (Data handling)  
- 📄 FPDF2 (PDF report generation)  
- 📈 Openpyxl (Excel .xlsx file handling)  

---

## ⚙️ How to Run Locally

<details>
<summary><b>📌 Prerequisites</b></summary>

- Python 3.11+  
- Google API Key (get it [here](https://console.cloud.google.com))  

</details>

<details>
<summary><b>🚀 Installation</b></summary>

```bash
# Clone the repository
git clone https://github.com/joprestes/qa-oraculo-requisitos.git
cd qa-oraculo-requisitos

# Create and activate the virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```
</details>

<details>
<summary><b>🔑 API Configuration</b></summary>

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY="your_api_key_here"
```
</details>

<details>
<summary><b>▶️ Run</b></summary>

```bash
streamlit run app.py
```

🎉 QA Oracle will automatically open in your browser!
</details>

---

### 📋 How to Use

1. **Insert the User Story:** Paste the US you want to analyze.  
2. **Start the Analysis:** Click “Analyze User Story” for the AI to generate the initial quality analysis.  
3. **Refine the Analysis (Collaboration Step):** The application will display a pre-filled form with the AI’s analysis. Review, edit the fields as needed, and click “Save Analysis and Continue.”  
4. **Choose Next Step:** With the refined and saved analysis, decide whether to generate a detailed test plan or finish.  
5. **Export Results:** Use the download buttons to get artifacts in multiple formats. For Azure and Jira, fill in the customizable fields.  
6. **Start Again:** Click “Start New Analysis” to clear the screen.  

---

## 🤔 Troubleshooting

❌ **Error:** Invalid API Key  
✔️ Make sure the `.env` file is in the root folder and the “Generative Language” API is enabled in Google Cloud.  

❌ **Error:** `streamlit` command not found  
✔️ Make sure the virtual environment `venv` is activated.  

---

## 🧪 Quality and Testing

The quality of this project is ensured by a robust unit test suite built with `pytest`, validating the logic of the `graph.py` and `utils.py` modules.

- **Test Coverage**: Critical logic modules reached **100% line coverage**, ensuring high reliability and safety for future changes.  
- **Run Tests**:  
  ```bash
  pytest
  ```

- **Coverage Verification**:  
  ```bash
  pytest --cov=graph --cov=utils
  ```

---

## 📌 Roadmap

- [x] Interactive web interface with Streamlit  
- [x] Generation of acceptance criteria and PO questions  
- [x] On-demand complete test plan generation  
- [x] Report export in `.md` and `.pdf`  
- [x] Export to Azure DevOps (`.xlsx`)  
- [x] Export to Jira Zephyr (`.xlsx`)  
- [x] Code refactoring to modular architecture  
- [x] Implement caching to optimize API calls  
- [x] Centralize prompts in configuration files  
- [x] Test suite implementation with `pytest` (100% coverage)  
- [x] Allow interactive editing of initial analysis by user 
- [ ] Add analysis history in session  
- [ ] Containerize application with Docker  

---

## 🤝 Contribution

Contributions are very welcome!  
- Open an **issue** to report bugs or suggest improvements  
- Send a **Pull Request** with new features  

⭐ If this project helped you, don’t forget to leave a **star on the repository**!
