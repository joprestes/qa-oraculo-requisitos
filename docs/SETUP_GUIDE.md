# 🚀 Guia de Instalação - QA Oráculo

Este guia vai te ajudar a instalar e configurar o QA Oráculo de forma simples e rápida!

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.11 ou superior** ([Download aqui](https://python.org/downloads/))
- **Git** ([Download aqui](https://git-scm.com/downloads))
- **Uma conta Google** (para a API do Gemini)

## 🎯 Instalação Rápida (Recomendada)

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/qa-oraculo.git
cd qa-oraculo/qa-oraculo-requisitos
```

### 2. Execute o script de setup automático

**No Windows:**
```bash
setup.bat
```

**No Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Configure sua API Key do Google
```bash
# Crie o arquivo .env
echo 'GOOGLE_API_KEY="sua_chave_aqui"' > .env
```

**Como obter a API Key:**
1. Acesse [Google AI Studio](https://aistudio.google.com/)
2. Faça login com sua conta Google
3. Clique em "Get API Key"
4. Copie a chave e cole no arquivo `.env`

### 4. Execute o aplicativo
```bash
# Ative o ambiente virtual
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Execute o aplicativo
streamlit run main.py
```

## 🔧 Instalação Manual (Passo a Passo)

Se preferir fazer manualmente ou se o script automático não funcionar:

### 1. Crie o ambiente virtual
```bash
python -m venv .venv
```

### 2. Ative o ambiente virtual

**Linux/Mac:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### 3. Instale as dependências
```bash
# Atualize o pip
python -m pip install --upgrade pip

# Instale as dependências principais
pip install -r requirements.txt

# Instale as dependências de desenvolvimento (opcional)
pip install -r requirements-dev.txt
```

### 4. Configure a API Key
```bash
# Crie o arquivo .env
echo 'GOOGLE_API_KEY="sua_chave_aqui"' > .env
```

### 5. Execute o aplicativo
```bash
streamlit run main.py
```

## 🌐 Acessando o Aplicativo

Após executar `streamlit run main.py`, o aplicativo estará disponível em:

- **URL Local:** http://localhost:8501
- **URL da Rede:** http://seu-ip:8501

## ✅ Verificação da Instalação

Para verificar se tudo está funcionando:

### 1. Teste básico
```bash
python -c "import streamlit, pandas, google.generativeai; print('✅ Todas as dependências OK!')"
```

### 2. Execute os testes
```bash
pytest
```

### 3. Verifique a qualidade do código
```bash
ruff check .
black --check .
```

## 🐛 Solução de Problemas

### Erro: "ModuleNotFoundError"
```bash
# Certifique-se de que o ambiente virtual está ativado
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Reinstale as dependências
pip install -r requirements.txt
```

### Erro: "Streamlit não encontrado"
```bash
# Instale o Streamlit manualmente
pip install streamlit
```

### Erro: "API Key inválida"
1. Verifique se o arquivo `.env` existe
2. Confirme se a API Key está correta
3. Teste a API Key em [Google AI Studio](https://aistudio.google.com/)

### Erro: "Porta 8501 em uso"
```bash
# Use uma porta diferente
streamlit run main.py --server.port 8502
```

## 📚 Próximos Passos

Após a instalação bem-sucedida:

1. **Leia a documentação completa:** [docs/README.md](docs/README.md)
2. **Aprenda sobre exportação Xray:** [docs/XRAY_EXPORT_GUIDE.md](docs/XRAY_EXPORT_GUIDE.md)
3. **Explore as funcionalidades:** Use o aplicativo para analisar uma User Story!

## 🆘 Precisa de Ajuda?

- **Issues:** [GitHub Issues](https://github.com/seu-usuario/qa-oraculo/issues)
- **Documentação:** [docs/](docs/)
- **Email:** seu-email@exemplo.com

## 🎉 Parabéns!

Se você chegou até aqui, o QA Oráculo está instalado e pronto para usar! 

Agora você pode:
- Analisar User Stories com IA
- Gerar cenários de teste automaticamente
- Exportar para suas ferramentas de QA favoritas
- E muito mais!

**Boa sorte com suas análises de qualidade!** 🚀
