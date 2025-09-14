#!/bin/bash
# Este script automatiza a criação do ambiente virtual e a instalação das dependências.

# Para o script se houver algum erro
set -e

echo "----------------------------------------------------"
echo "Iniciando o setup do ambiente para QA Oráculo..."
echo "----------------------------------------------------"

# Verifica se o ambiente virtual já existe para não recriá-lo
if [ ! -d ".venv" ]; then
    echo "1. Criando ambiente virtual (.venv)..."
    python3 -m venv .venv
else
    echo "1. Ambiente virtual (.venv) já existe. Pulando a criação."
fi

echo "2. Ativando o ambiente virtual e instalando dependências..."

# Ativa o ambiente, instala as dependências do requirements.txt e desativa
# No Mac/Linux, podemos ativar e executar comandos em sequência
source .venv/bin/activate

# Aqui vamos instalar as bibliotecas. 
 pip install -r requirements.txt

deactivate

echo "----------------------------------------------------"
echo "✅ Setup concluído com sucesso!"
echo ""
echo "👉 Para começar a trabalhar, ative o ambiente virtual com o comando:"
echo "source .venv/bin/activate"
echo "----------------------------------------------------"