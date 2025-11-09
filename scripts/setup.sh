#!/usr/bin/env bash
# ===================================================================
# 🧰 QA Oráculo - Setup e Revisão de Qualidade (Linux/Mac)
# -------------------------------------------------------------------
# Este script prepara o ambiente de desenvolvimento e executa
# automaticamente as validações de qualidade antes do push.
# ===================================================================

set -e  # Interrompe se algum comando falhar

echo "=================================================================="
echo "🚀 Iniciando o setup e revisão do ambiente QA Oráculo..."
echo "=================================================================="

# 1️ Criação do ambiente virtual
if [ ! -d ".venv" ]; then
  if [ -d "venv" ]; then
    echo "⚠️  Ambiente virtual legado detectado em ./venv. Utilize 'make clean-venv' para remover ou migre para .venv."
  fi
  echo "📦 Criando ambiente virtual (.venv)..."
  python3 -m venv .venv
else
  echo "📦 Ambiente virtual (.venv) já existe. Pulando criação."
fi

# 2️Ativação do ambiente e instalação de dependências
echo "🔧 Ativando ambiente virtual..."
source .venv/bin/activate

echo "📚 Instalando dependências e ferramentas de qualidade..."
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install black ruff pytest pytest-cov

# 3️ Validação do pyproject.toml
echo "🧩 Validando pyproject.toml..."
python -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('✅ TOML válido!')"

# 4️ Lint e formatação
echo "🎯 Rodando verificações de qualidade (Ruff + Black)..."
ruff check .
black --check .

# 5️ Testes com cobertura
echo "🧪 Executando testes unitários e cobertura..."
pytest --cov --cov-report=term-missing

# 6️ Revisão final de pré-push
echo "🧱 Revisão QA Oráculo antes do push..."
echo "--------------------------------------------------"
python -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('✅ TOML válido!')"
ruff check .
black --check .
pytest --cov --cov-report=term-missing
echo "--------------------------------------------------"
echo "✅ Tudo validado! Pronto para commit e push 🚀"

# 7️ Desativa ambiente virtual
deactivate

echo "=================================================================="
echo "🎉 Setup e revisão concluídos com sucesso!"
echo "👉 Para começar a trabalhar, ative o ambiente com:"
echo "source .venv/bin/activate"
echo "=================================================================="
