<nav aria-label="Language switcher" style="text-align: right;">
  <a href="README-en.md" aria-current="page">🇺🇸 **English**</a> | <a href="README.md">🇧🇷 Português</a>
</nav>

# 🔮 QA Oracle: AI-Powered Requirements Analysis

An AI-powered analyzer for Software Requirements to identify ambiguities, contradictions, and risks before development begins. This project is built with a focus on accessibility and a *mobile-first* approach.

## 🚀 Getting Started

Follow the steps below to set up and run the project on your local machine.

### Prerequisites

- [Git](https://git-scm.com/)
- [Python 3.10+](https://www.python.org/)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/qa-oraculo-requisitos.git
    cd qa-oraculo-requisitos
    ```
    > **Note:** Remember to replace `your-username` with your actual GitHub username.

2.  **Run the setup script:**
    -   **For Windows:**
        ```bash
        setup.bat
        ```
    -   **For Mac or Linux:**
        ```bash
        chmod +x setup.sh
        ./setup.sh
        ```

3.  **Activate the Virtual Environment:**
    -   **On Windows:**
        ```bash
        .\.venv\Scriptsctivate
        ```
    -   **On Mac or Linux:**
        ```bash
        source .venv/bin/activate
        ```
    > Your terminal prompt should now start with `(.venv)`.

## 🛠️ How to Use

With the environment active, run the main script using the explicit path to ensure the correct Python is used:

```bash
# For Mac/Linux
./.venv/bin/python main.py

# For Windows
# .\.venv\Scripts\python.exe main.py
```

(This section will be improved as the project progresses.)

## 🤔 Troubleshooting

Solutions to common setup issues.

### 1. zsh: permission denied: ./setup.sh
**Problem:** Your system is blocking the script from running.  
**Solution:** Grant execution permission (only needs to be done once):
```bash
chmod +x setup.sh
```

### 2. ./setup.sh: python: command not found
**Problem:** The script can't find Python using the `python` command, common on macOS/Linux which use `python3`.  
**Solution:**
- Open `setup.sh`.
- Change `python -m venv .venv` to `python3 -m venv .venv`.
- Delete any partial `.venv` folder (`rm -rf .venv`) and run the setup again.

### 3. ModuleNotFoundError: No module named 'google'
**Problem:** Python libraries are not installed in your virtual environment, or the wrong Python interpreter is being used.  
**Solution:**
- Ensure your virtual environment is active (you should see `(.venv)` in your prompt).
- Manually run the installation using the environment's pip:
```bash
./.venv/bin/python -m pip install -r requirements.txt
```
- Always run your script using the explicit path to the environment's Python to avoid this error:
```bash
./.venv/bin/python main.py
```

### 4. error: externally-managed-environment
**Problem:** Your OS is protecting the system's base Python installation.  
**Solution:** Always use the explicit path to the environment's pip to install dependencies:
```bash
./.venv/bin/python -m pip install -r requirements.txt
```


---
This project is under development.