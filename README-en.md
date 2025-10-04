<p align="center">
  <img src="assets/logo_oraculo.png" alt="QA Oráculo Logo" width="200"/>
</p>

<h1 align="center">🔮 QA Oráculo</h1>
<p align="center"><i>Requirements Analysis with Artificial Intelligence</i></p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg"/>
  <img src="https://img.shields.io/badge/license-CC--BY--NC%204.0-orange.svg"/>
  <img src="https://img.shields.io/badge/Streamlit-App-red.svg"/>
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg"/>
</p>

<nav aria-label="Language switcher" style="text-align: right;">
<a href="README-en.md" aria-current="page">🇺🇸 <strong>English</strong></a> |
<a href="README.md">🇧🇷 Português</a>
</nav>

## 🚀 Why use QA Oráculo?

Tired of **vague User Stories** and **endless meetings** to align understanding?

**QA Oráculo** transforms loose requirements into **ready-to-test specifications** using cutting-edge AI.

👉 In just **minutes**, you will have:
- ✅ Clear acceptance criteria  
- ❓ Smart questions for the PO  
- 📝 Complete and organized test plans  
- 🧪 On-demand Gherkin scenarios  
- 📄 Exportable reports (.md, .pdf, .xlsx)  

It's like having a **Senior QA available 24/7**, speeding up planning and reducing failures before the first bug appears.

---

## 📸 Interface Preview

![alt text](assets/qa_oraculo_cartoon_demo.gif)

---

## 🚀 Main Features

- 💻 **Interactive Web Interface** built with **Streamlit**.  
- 📝 **Editable and Interactive Analysis:** After AI generates the initial analysis, the application presents an editable form. The user can refine, correct and add information (acceptance criteria, risks, etc.) before proceeding, ensuring that the final test plan is based on requirements validated by a human.  
- 🔍 **Ambiguity detection** and suggestion of questions for the PO.  
- ✅ **Generation of clear and verifiable Acceptance Criteria**.  
- 📊 **Interactive, sortable Test Case Table**.  
- 📥 **Multiple Export Options** (`.md`, `.pdf`, Azure and Jira).  
- 📖 **Analysis History:** Browse and review previous analyses.  
- 🗑️ **History Management:** Now you can delete a specific analysis or clear the entire history at once, always with confirmation to avoid accidental deletions.  
- 🏗️ **Modular, Optimized and 100% Tested Code.**  

---

## 🛠️ Technologies Used

- 🐍 Python 3.11+  
- 🌐 Streamlit (Web UI Framework)  
- 🧠 LangGraph & Google Gemini (Orchestration and AI)  
- 📊 Pandas (Data manipulation)  
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

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```
</details>

<details>
<summary><b>🔑 API Configuration</b></summary>

Create a `.env` file at the project root:

```env
GOOGLE_API_KEY="your_api_key_here"
```
</details>

<details>
<summary><b>▶️ Run</b></summary>

```bash
streamlit run app.py
```

🎉 QA Oráculo will automatically open in your browser!
</details>

---

### 📋 How to Use

1. **Insert the User Story:** Paste the US you want to analyze.  
2. **Start the Analysis:** Click on "Analyze User Story" to have the AI generate the initial quality analysis.  
3. **Refine the Analysis (Collaboration Step):** The application will display a pre-filled form with the AI analysis. Review, edit fields as needed, and click "Save Analysis and Continue".  
4. **Decide Next Step:** With the refined analysis saved, choose whether to generate the detailed test plan or end the process.  
5. **Export Results:** Use the download buttons to obtain artifacts in multiple formats. For Azure and Jira, fill in the customizable fields.  
6. **Manage History:** Review past analyses and use the buttons to delete individually or clear all history (with confirmation).  
7. **Start Over:** Click "New Analysis" to reset the screen.  

---

## 🤔 Troubleshooting

❌ **Error:** Invalid API Key  
✔️ Make sure the `.env` file is in the root and the "Generative Language" API is active on Google Cloud.  

❌ **Error:** `streamlit` command not found  
✔️ Make sure the virtual environment `venv` is activated.  

---

## 🧪 Quality and Tests

The quality of this project is ensured by a robust suite of unit tests, built with `pytest`, validating the logic of `graph.py`, `utils.py`, `database.py` and `app.py`.

- **Test Coverage**: Critical modules achieve **high coverage** (≥97%).  
- **Run Tests**:  
  ```bash
  pytest
  ```

- **Check Coverage**:  
  ```bash
  pytest --cov
  ```

- **New History Tests:**  
  - `tests/test_app_history_delete.py` covers individual and bulk deletion of analyses.  
  - `tests/conftest.py` ensures the database is automatically cleaned after the test suite execution.  

---

## 📌 Roadmap

- [x] Interactive web interface with Streamlit  
- [x] Generation of acceptance criteria and questions for the PO  
- [x] Generation of full test plan on demand  
- [x] Export of reports in `.md` and `.pdf`  
- [x] Export to Azure DevOps (`.xlsx`)  
- [x] Export to Jira Zephyr (`.xlsx`)  
- [x] Refactor code into modular architecture  
- [x] Implement caching to optimize API calls  
- [x] Centralize prompts in configuration files  
- [x] Implement test suite with `pytest` (100% coverage on critical modules)  
- [x] Allow interactive editing of the initial analysis by the user  
- [x] Analysis history with individual and bulk deletion (with confirmation)  
- [ ] Containerize the application with Docker  

---

## 🤝 Contribution

Contributions are very welcome!  
- Open an **issue** to report bugs or suggest improvements  
- Send a **Pull Request** with new features  

⭐ If this project helped you, don’t forget to leave a **star on the repository**!  

---

## 📜 License

This project is licensed under **CC BY-NC 4.0**.  
Only **personal use** is allowed. Commercial use is **strictly prohibited**.  
Read more at [Creative Commons](https://creativecommons.org/licenses/by-nc/4.0/).
