<nav aria-label="Language switcher" style="text-align: right;">
  <a href="README-en.md" aria-current="page">🇺🇸 <strong>English</strong></a> | 
  <a href="README.md">🇧🇷 Português</a>
</nav>

# 🔮 QA Oracle: Requirements Analysis with AI

👋 Welcome to **QA Oracle**!  
A senior QA assistant powered by AI that helps you transform User Stories (US) into clear specifications, reducing risks and speeding up test planning.  

---

## ✨ Why use QA Oracle?

- 🔍 **Detects ambiguities** in User Stories before development  
- ❓ **Suggests questions for the PO**, enabling quick alignment  
- ✅ **Generates acceptance criteria** that are simple and verifiable  
- 📝 **Proposes interactive test plans** and Gherkin test cases  
- ♿ **Includes accessibility (A11y) scenarios** by default  

---

## 🚀 Getting Started

Ready to run? Follow these 4 steps:

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-name/qa-oracle-requirements.git
   cd qa-oracle-requirements
   ```

2. **Run the setup**  
   - Windows: `setup.bat`  
   - Mac/Linux: `chmod +x setup.sh && ./setup.sh`

3. **Configure your API Key**  
   Copy `.env.example` → `.env` and add your Google Gemini API key.

4. **Activate the virtual environment**  
   - Windows: `.\.venv\Scriptsctivate`  
   - Mac/Linux: `source .venv/bin/activate`

---

## 🛠️ How to Use

The flow is simple:

1. **Run the script**  
   ```bash
   ./.venv/bin/python app.py
   ```

2. **Step 1:** US analysis → ambiguity, PO questions, and acceptance criteria.  
3. **Step 2:** you decide:  
   - Type `y` → generate test plan + Gherkin cases  
   - Type `n` → exit  

---

## 🧪 Tests

This project uses `unittest` to ensure code quality. To run the test suite:

```bash
./.venv/bin/python -m unittest discover tests/
```

---

## 🤔 Troubleshooting

1. **zsh: permission denied: ./setup.sh**  
   ➡ Grant execution permission:  
   ```bash
   chmod +x setup.sh
   ```

2. **./setup.sh: python: command not found**  
   ➡ On macOS/Linux, use `python3`:  
   ```bash
   python3 -m venv .venv
   ```

3. **ModuleNotFoundError**  
   ➡ Activate the virtual environment and run:  
   ```bash
   ./.venv/bin/python main.py
   ```

4. **error: externally-managed-environment**  
   ➡ Install dependencies using pip from the environment:  
   ```bash
   ./.venv/bin/python -m pip install -r requirements.txt
   ```

---

## 🤝 Contribute

We love contributions!  
- Open an *issue* to suggest improvements  
- Submit a *PR* for new features  

⭐ If this project helped you, don’t forget to give it a star on the repository!

---

📌 This project is still evolving.  
💡 Your feedback is super important — contribute, test, and help shape the future of QA Oracle!
