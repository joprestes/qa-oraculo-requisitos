@echo off
:: ===================================================================
:: 🧰 QA Oráculo - Setup e Revisão de Qualidade (Windows)
:: -------------------------------------------------------------------
:: Este script prepara o ambiente de desenvolvimento e executa
:: automaticamente as validações de qualidade antes do push.
:: ===================================================================

ECHO ================================================================
ECHO 🚀 Iniciando o setup e revisão do ambiente QA Oráculo...
ECHO ================================================================

:: 1️⃣ Criação do ambiente virtual
IF NOT EXIST .venv (
    ECHO 📦 Criando ambiente virtual (.venv)...
    python -m venv .venv
) ELSE (
    ECHO 📦 Ambiente virtual (.venv) já existe. Pulando criação.
)

:: 2️⃣ Ativação do ambiente e instalação de dependências
ECHO 🔧 Ativando ambiente virtual...
CALL .\.venv\Scripts\activate

ECHO 📚 Instalando dependências e ferramentas de qualidade...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install black ruff pytest pytest-cov

:: 3️⃣ Validação do pyproject.toml
ECHO 🧩 Validando pyproject.toml...
python -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('✅ TOML válido!')"

:: 4️⃣ Lint e formatação
ECHO 🎯 Rodando verificações de qualidade (Ruff + Black)...
ruff check .
black --check .

:: 5️⃣ Testes com cobertura
ECHO 🧪 Executando testes unitários e cobertura...
pytest --cov --cov-report=term-missing --cov-fail-under=95

:: 6️⃣ Revisão final de pré-push
ECHO ================================================================
ECHO 🧱 Revisão QA Oráculo antes do push...
ECHO --------------------------------------------------
python -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('✅ TOML válido!')"
ruff check .
black --check .
pytest --cov --cov-report=term-missing --cov-fail-under=95
ECHO --------------------------------------------------
ECHO ✅ Tudo validado! Pronto para commit e push 🚀
ECHO ================================================================

:: 7️⃣ Desativar ambiente virtual
CALL .\.venv\Scripts\deactivate.bat

ECHO ================================================================
ECHO 🎉 Setup e revisão concluídos com sucesso!
ECHO 👉 Para começar a trabalhar, ative o ambiente com:
ECHO .\.venv\Scripts\activate
ECHO ================================================================
PAUSE
