#!/usr/bin/env bash
# ===================================================================
# 🚀 QA Oráculo - Setup Rápido e Simples
# -------------------------------------------------------------------
# Este script instala o QA Oráculo de forma simples e amigável
# ===================================================================

set -e  # Interrompe se algum comando falhar

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para imprimir com cores
print_step() {
    echo -e "${BLUE}🔧 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Banner
echo -e "${PURPLE}"
echo "=================================================================="
echo "🔮 QA ORÁCULO - SETUP RÁPIDO"
echo "=================================================================="
echo -e "${NC}"

# Verificar Python
print_step "Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python encontrado: $PYTHON_VERSION"
else
    print_error "Python não encontrado! Instale Python 3.11+ primeiro."
    echo "Download: https://python.org/downloads/"
    exit 1
fi

# Verificar se está na pasta correta
if [ ! -f "main.py" ]; then
    print_error "Execute este script na pasta qa-oraculo-requisitos!"
    echo "Estrutura esperada:"
    echo "  qa-oraculo/"
    echo "  └── qa-oraculo-requisitos/"
    echo "      ├── main.py"
    echo "      ├── quick-setup.sh"
    echo "      └── ..."
    exit 1
fi

# 1. Criar ambiente virtual
print_step "Criando ambiente virtual..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    print_success "Ambiente virtual criado!"
else
    print_info "Ambiente virtual já existe. Pulando criação."
fi

# 2. Ativar ambiente virtual
print_step "Ativando ambiente virtual..."
source .venv/bin/activate
print_success "Ambiente virtual ativado!"

# 3. Atualizar pip
print_step "Atualizando pip..."
python -m pip install --upgrade pip
print_success "Pip atualizado!"

# 4. Instalar dependências
print_step "Instalando dependências principais..."
pip install -r requirements.txt
print_success "Dependências principais instaladas!"

# 5. Verificar instalação
print_step "Verificando instalação..."
python -c "
import streamlit
import pandas
import google.generativeai
print('✅ Streamlit:', streamlit.__version__)
print('✅ Pandas:', pandas.__version__)
print('✅ Google Generative AI: OK')
print('✅ Todas as dependências funcionando!')
"

# 6. Configurar API Key
print_step "Configurando API Key..."
if [ ! -f ".env" ]; then
    echo ""
    print_warning "Você precisa configurar sua API Key do Google Gemini!"
    echo ""
    echo "Como obter:"
    echo "1. Acesse: https://aistudio.google.com/"
    echo "2. Faça login com sua conta Google"
    echo "3. Clique em 'Get API Key'"
    echo "4. Copie a chave"
    echo ""
    read -p "Cole sua API Key aqui: " API_KEY
    
    if [ -n "$API_KEY" ]; then
        echo "GOOGLE_API_KEY=\"$API_KEY\"" > .env
        print_success "API Key configurada!"
    else
        print_warning "API Key não configurada. Você pode configurar depois criando o arquivo .env"
    fi
else
    print_info "Arquivo .env já existe. Pulando configuração."
fi

# 7. Teste final
print_step "Executando teste final..."
python -c "
import sys
sys.path.insert(0, '.')
from qa_core.app import main
print('✅ Aplicação carregada com sucesso!')
"

# 8. Instruções finais
echo ""
echo -e "${GREEN}=================================================================="
echo "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "=================================================================="
echo -e "${NC}"
echo ""
print_info "Para executar o QA Oráculo:"
echo ""
echo "1. Ative o ambiente virtual:"
echo "   source .venv/bin/activate"
echo ""
echo "2. Execute o aplicativo:"
echo "   streamlit run main.py"
echo ""
echo "3. Acesse no navegador:"
echo "   http://localhost:8501"
echo ""
print_info "Documentação completa: SETUP_GUIDE.md"
print_info "Guia Xray: docs/XRAY_EXPORT_GUIDE.md"
echo ""
echo -e "${PURPLE}Boa sorte com suas análises de qualidade! 🚀${NC}"
echo ""
