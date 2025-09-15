<nav aria-label="Language switcher" style="text-align: right;">
  <a href="README-en.md" aria-current="page">🇺🇸 <strong>English</strong></a> | 
  <a href="README.md">🇧🇷 Português</a>
</nav>

# 🔮 QA Oracle: AI-Powered Requirements Analysis

An AI-powered analyzer for Software Requirements to identify
ambiguities, contradictions, and risks before development begins. This
project is built with a focus on code quality, testability, and
accessibility.

## ✨ Features

-   **Quality Analysis:** Evaluates the clarity of each requirement,
    pointing out vague terms and suggesting improvements.
-   **Conflict Detection:** Analyzes the entire set of requirements to
    find logical contradictions and overlaps.
-   **Report Generation:** Consolidates all findings into a detailed
    report in Markdown format.

## 🚀 Getting Started

Follow the steps below to set up and run the project on your local
machine.

### Prerequisites

-   [Git](https://git-scm.com/)
-   [Python 3.10+](https://www.python.org/)

### Installation

1.  **Clone the repository:**
    `bash     git clone https://github.com/your-username/qa-oraculo-requisitos.git     cd qa-oraculo-requisitos`

2.  **Run the setup script:** This command will create a virtual
    environment (`.venv`) and install dependencies.

    -   **For Windows:** `setup.bat`
    -   **For Mac/Linux:** `chmod +x setup.sh` then `./setup.sh`

3.  **Set up your API Key:**

    -   Copy the `.env.example` file to a new file named `.env`.
    -   Enter your Google Gemini API key in the `.env` file.

4.  **Activate the Virtual Environment:**

    -   **On Windows:** `.\.venv\Scriptsctivate`
    -   **On Mac or Linux:** `source .venv/bin/activate`

## 🛠️ How to Use

With the environment active, run the main script to see an example
analysis:

``` bash
# Use the explicit path to ensure the correct Python is used
./.venv/bin/python main.py
```

## 🧪 Testing

This project uses Python's built-in **unittest** library to ensure code
quality.\
To run the test suite, execute the following command from the project
root:

``` bash
./.venv/bin/python -m unittest discover tests/
```

## 🤔 Troubleshooting

1.  **zsh: permission denied: ./setup.sh**
    -   Problem: Your system is blocking the script from running for
        security reasons.\

    -   Solution: Grant execution permission (only needs to be done
        once):

        ``` bash
        chmod +x setup.sh
        ```
2.  **./setup.sh: python: command not found**
    -   Problem: The script couldn't find `python`. This is common on
        macOS/Linux, which use `python3`.\
    -   Solution: Change the line `python -m venv .venv` to
        `python3 -m venv .venv` in the `setup.sh` file and run the setup
        again.
3.  **ModuleNotFoundError**
    -   Problem: Libraries are not installed in the virtual environment,
        or the wrong Python interpreter is being used.\

    -   Solution: Ensure the environment is active and run your script
        with the explicit path:

        ``` bash
        ./.venv/bin/python main.py
        ```
4.  **error: externally-managed-environment**
    -   Problem: Your OS is protecting its base Python installation.\

    -   Solution: Always use the explicit path to the environment's pip
        to install dependencies:

        ``` bash
        ./.venv/bin/python -m pip install -r requirements.txt
        ```

------------------------------------------------------------------------

📌 This project is under development.
