@echo off
:: ===================================================================
:: 🧰 QA Oráculo - Setup Automático do Ambiente (Windows)
:: -------------------------------------------------------------------
:: Este script prepara o ambiente local de desenvolvimento:
:: 1. Cria o ambiente virtual (.venv) se não existir
:: 2. Instala dependências do projeto e ferramentas de qualidade
:: 3. Executa validações automáticas (Black, Ruff, Pytest, TOML)
:: 4. Exibe o status final do setup
:: ===================================================================

ECHO ================================================================
ECHO 🚀 Iniciando o setup do ambiente QA Oráculo...
ECHO ================================================================

:: 1️⃣ Criação do ambiente virtual
IF NOT EXIST .venv (
    ECHO 📦 Criando ambiente virtual (.venv)...
    python -m venv .venv
) ELSE (
    ECHO 📦 Ambiente virtual (.venv) já existe. Pulando criação.
)

:: 2️⃣ Ativação do ambiente
ECHO 🔧 Ativando ambiente virtual...
CALL .\.venv\Scripts\activate

:: 3️⃣ Instalação das dependências
ECHO 📚 Instalando dependências e ferramentas de qualidade...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install black ruff pytest pytest-cov

:: 4️⃣ Validação de sintaxe TOML
ECHO 🧩 Validando pyproject.toml...
python -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('✅ TOML válido!')"

:: 5️⃣ Lint e formatação
ECHO 🎯 Rodando verificações de qualidade (Black + Ruff)...
black --check .
ruff check .

:: 6️⃣ Testes com cobertura
ECHO 🧪 Executando testes unitários com cobertura...
pytest --cov=app --cov=database --cov=graph --cov=pdf_generator --cov=state_manager --cov=utils --cov-report=term-missing

:: 7️⃣ Encerramento
CALL .\.venv\Scripts\deactivate

ECHO ================================================================
ECHO ✅ Setup concluído com sucesso!
ECHO Para começar a trabalhar, ative o ambiente com:
ECHO .\.venv\Scripts\activate
ECHO ================================================================
PAUSE
