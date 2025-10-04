#!/usr/bin/env bash
# ===================================================================
# 🧰 QA Oráculo - Setup Automático do Ambiente (Linux/Mac)
# -------------------------------------------------------------------
# Este script prepara o ambiente de desenvolvimento:
# 1. Cria o ambiente virtual (.venv)
# 2. Instala dependências e ferramentas de qualidade
# 3. Valida a sintaxe do pyproject.toml
# 4. Roda Black, Ruff e Pytest com cobertura
# 5. Exibe o status final
# ===================================================================

set -e  # Interrompe o script em caso de erro

echo "=================================================================="
echo "🚀 Iniciando o setup do ambiente QA Oráculo..."
echo "=================================================================="

# 1️⃣ Criação do ambiente virtual
if [ ! -d ".venv" ]; then
  echo "📦 Criando ambiente virtual (.venv)..."
  python3 -m venv .venv
else
  echo "📦 Ambiente virtual (.venv) já existe. Pulando criação."
fi

# 2️⃣ Ativação do ambiente e instalação de dependências
echo "🔧 Ativando ambiente virtual..."
source .venv/bin/activate

echo "📚 Instalando dependências e ferramentas de qualidade..."
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install black ruff pytest pytest-cov

# 3️⃣ Validação do pyproject.toml
echo "🧩 Validando pyproject.toml..."
python -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('✅ TOML válido!')"

# 4️⃣ Lint e formatação
echo "🎯 Rodando verificações de qualidade (Black + Ruff)..."
black --check .
ruff check .

# 5️⃣ Testes com cobertura
echo "🧪 Executando testes unitários com cobertura..."
pytest --cov=app --cov=database --cov=graph --cov=pdf_generator --cov=state_manager --cov=utils --cov-report=term-missing

# 6️⃣ Finalização
deactivate
echo "=================================================================="
echo "✅ Setup concluído com sucesso!"
echo ""
echo "👉 Para começar a trabalhar, ative o ambiente virtual com o comando:"
echo "source .venv/bin/activate"
echo "=================================================================="
