@echo off
:: ===================================================================
:: 🚀 QA Oráculo - Setup Rápido e Simples (Windows)
:: -------------------------------------------------------------------
:: Este script instala o QA Oráculo de forma simples e amigável
:: ===================================================================

setlocal enabledelayedexpansion

:: Banner
echo.
echo ==================================================================
echo 🔮 QA ORÁCULO - SETUP RÁPIDO
echo ==================================================================
echo.

:: Verificar Python
echo 🔧 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado! Instale Python 3.11+ primeiro.
    echo Download: https://python.org/downloads/
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo ✅ Python encontrado: !PYTHON_VERSION!
)

:: Verificar se está na pasta correta
if not exist "main.py" (
    echo ❌ Execute este script na pasta qa-oraculo-requisitos!
    echo Estrutura esperada:
    echo   qa-oraculo/
    echo   └── qa-oraculo-requisitos/
    echo       ├── main.py
    echo       ├── quick-setup.bat
    echo       └── ...
    pause
    exit /b 1
)

:: 1. Criar ambiente virtual
echo 🔧 Criando ambiente virtual...
if not exist ".venv" (
    python -m venv .venv
    echo ✅ Ambiente virtual criado!
) else (
    echo ℹ️  Ambiente virtual já existe. Pulando criação.
)

:: 2. Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call .venv\Scripts\activate
echo ✅ Ambiente virtual ativado!

:: 3. Atualizar pip
echo 🔧 Atualizando pip...
python -m pip install --upgrade pip
echo ✅ Pip atualizado!

:: 4. Instalar dependências
echo 🔧 Instalando dependências principais...
pip install -r requirements.txt
echo ✅ Dependências principais instaladas!

:: 5. Verificar instalação
echo 🔧 Verificando instalação...
python -c "import streamlit; import pandas; import google.generativeai; print('✅ Streamlit:', streamlit.__version__); print('✅ Pandas:', pandas.__version__); print('✅ Google Generative AI: OK'); print('✅ Todas as dependências funcionando!')"

:: 6. Configurar API Key
echo 🔧 Configurando API Key...
if not exist ".env" (
    echo.
    echo ⚠️  Você precisa configurar sua API Key do Google Gemini!
    echo.
    echo Como obter:
    echo 1. Acesse: https://aistudio.google.com/
    echo 2. Faça login com sua conta Google
    echo 3. Clique em 'Get API Key'
    echo 4. Copie a chave
    echo.
    set /p API_KEY="Cole sua API Key aqui: "
    
    if not "!API_KEY!"=="" (
        echo GOOGLE_API_KEY="!API_KEY!" > .env
        echo ✅ API Key configurada!
    ) else (
        echo ⚠️  API Key não configurada. Você pode configurar depois criando o arquivo .env
    )
) else (
    echo ℹ️  Arquivo .env já existe. Pulando configuração.
)

:: 7. Teste final
echo 🔧 Executando teste final...
python -c "import sys; sys.path.insert(0, '.'); from qa_core.app import main; print('✅ Aplicação carregada com sucesso!')"

:: 8. Instruções finais
echo.
echo ==================================================================
echo 🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo ==================================================================
echo.
echo ℹ️  Para executar o QA Oráculo:
echo.
echo 1. Ative o ambiente virtual:
echo    .venv\Scripts\activate
echo.
echo 2. Execute o aplicativo:
echo    streamlit run main.py
echo.
echo 3. Acesse no navegador:
echo    http://localhost:8501
echo.
echo ℹ️  Documentação completa: SETUP_GUIDE.md
echo ℹ️  Guia Xray: docs/XRAY_EXPORT_GUIDE.md
echo.
echo Boa sorte com suas análises de qualidade! 🚀
echo.
pause
