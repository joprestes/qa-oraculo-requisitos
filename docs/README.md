<!-- markdownlint-disable MD033 MD026 MD036 MD031 MD032 MD003 MD040 MD047 -->

# 🔮 QA Oráculo

<p align="center">

  <!-- Linguagem principal -->
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>

  <!-- Framework principal -->
  <img src="https://img.shields.io/badge/streamlit-app-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>

  <!-- Build Status (GitHub Actions) -->
  <img src="https://img.shields.io/github/actions/workflow/status/joprestes/qa-oraculo-requisitos/ci.yml?branch=main&style=for-the-badge&logo=github" alt="Status CI"/>

  <!-- Test Coverage (ajuste manual se necessário) -->
  <img src="https://img.shields.io/badge/coverage-97%25-6E40C9?style=for-the-badge" alt="Cobertura de Testes"/>

  <!-- Licença -->
  <img src="https://img.shields.io/badge/license-CC%20BY--NC%204.0-8A2BE2?style=for-the-badge" alt="Licença CC BY-NC 4.0"/>

  <!-- Code Style -->
  <img src="https://img.shields.io/badge/code_style-black-000000?style=for-the-badge&logo=python&logoColor=white" alt="Black Code Style"/>

</p>

---

## 🚀 Por que usar o QA Oráculo?

Cansou de **User Stories vagas** e **reuniões infinitas** só pra entender o básico?

O **QA Oráculo** transforma requisitos dispersos em **especificações prontas para teste**, com o poder da IA.  
Em poucos minutos, você terá:

✅ Critérios de aceite objetivos e editáveis  
❓ Perguntas inteligentes para o PO  
🧪 Cenários Gherkin prontos para refino  
📄 Relatórios exportáveis (.md, .pdf, .xlsx, Azure, Jira)  

É como ter um **QA Sênior disponível 24/7**, acelerando o planejamento e prevenindo falhas antes mesmo do primeiro bug aparecer.

---

## 🧠 Preview da Interface

<p align="center">
  <img src="assets/qa_oraculo_cartoon_demo.gif" alt="Demonstração da Interface" width="600"/>
</p>

---

## 💎 Principais Funcionalidades

- 💻 **Interface Web Interativa** – construída em Streamlit, simples e responsiva.  
- ✏️ **Edição Inteligente** – refine critérios e cenários Gherkin direto na interface, com salvamento automático.  
- 🔍 **Detecção de Ambiguidades** – a IA sugere perguntas relevantes para o PO.  
- ✅ **Critérios de Aceite Verificáveis** – claros e rastreáveis.  
- 📊 **Plano de Teste Interativo** – expanda, edite e regenere relatórios instantaneamente.  
- 📥 **Exportação Avançada e Configurável**:
  - Formulário dedicado para Azure DevOps e Jira (Area Path, Assigned To, labels etc.)
  - CSV formatado para Azure com passos Gherkin e tratamento automático de prioridade e idioma  
  - CSV compatível com Xray (Jira Test Management) para importação de cenários Cucumber
  - PDF acessível com fonte Unicode, capa e cabeçalho padronizado  
- 📖 **Histórico de Análises Aprimorado** – visualização expandida, exclusão segura e navegação por URL.  
- 🧱 **Código Modular e Testado** – cobertura alta e estrutura limpa.

---

## ♿ Acessibilidade

O QA Oráculo implementa melhorias de acessibilidade baseadas em **WCAG 2.1 Level AA**:

✅ Contraste de cores 12:1 (supera o mínimo de 4.5:1)  
✅ Navegação 100% por teclado (Tab, Enter, Esc)  
✅ Foco visível em todos os elementos interativos  
✅ Mensagens anunciadas automaticamente por leitores de tela  
✅ Suporte a preferências do navegador (reduced-motion, high-contrast)  

### Testado com:

- ✅ NVDA + Chrome (Windows)
- ✅ VoiceOver + Safari (macOS)
- ⚠️ JAWS + Firefox (limitações conhecidas do Streamlit)

### Limitações:

- ARIA labels customizados não são suportados pelo Streamlit
- Alguns componentes nativos não expõem props de acessibilidade
- Conformidade WCAG 2.1 Level AA: **~70%** (parcial)

📄 Veja mais em: [ACESSIBILIDADE.md](./ACESSIBILIDADE.md)
---

## 🛠️ Stack Tecnológica

🐍 **Python 3.11+**  
🌐 **Streamlit** – interface web  
🧠 **LangGraph & Google Gemini** – análise e geração IA  
📊 **Pandas** – manipulação de dados  
📄 **FPDF2** – geração de PDFs acessíveis  
📈 **Openpyxl** – exportação Excel  

---

## ⚙️ Instalação e Execução

### 📌 Pré-requisitos

- Python 3.11+
- Chave de API do Google (serviço *Generative Language* ativo)

### 🧩 Passos

```bash
# Clone o repositório
git clone https://github.com/joprestes/qa-oraculo-requisitos.git
cd qa-oraculo-requisitos

# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# .\venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para testes e desenvolvimento
```

### 🔑 Configuração da API

Crie um arquivo `.env` na raiz do projeto:

```env
GOOGLE_API_KEY="sua_chave_de_api_aqui"
```

### ▶️ Executar

```bash
streamlit run main.py
```

🎉 O QA Oráculo abrirá automaticamente no navegador!

**Nota**: Use `main.py` como entry point (não `qa_core/app.py` diretamente) para evitar erros de importação.

---

## 📋 Como Usar

1. Insira a **User Story** no campo indicado.  
2. Clique em **“Analisar User Story”**.  
3. Revise e edite os **critérios de aceite** e **cenários Gherkin** gerados.  
4. Gere o **plano de testes completo**.  
5. Exporte artefatos (.md, .pdf, Azure, Jira).  
6. Consulte o **histórico interativo** ou inicie uma nova análise.

---

## 🔎 Exemplo Prático

### **Entrada**

```
Como usuário do app de banco,
quero redefinir minha senha via e-mail,
para recuperar o acesso em caso de esquecimento.
```

### **Saída (editável)**

**Critérios de Aceite**
- Link de redefinição enviado em menos de 1 minuto  
- O link expira em 24h  
- Nova senha deve ter pelo menos 8 caracteres com letras e números  

**Perguntas ao PO**
- O link expira em quantas horas?  
- Há limite de tentativas por dia?  

**Cenário Gherkin**
```gherkin
Scenario: Redefinir senha com sucesso
  Given que o usuário informou um e-mail válido
  When solicita redefinição de senha
  Then recebe um link de redefinição válido por 24h
```

---

## 🧪 Testes e Qualidade

Cobertura atual: **≥97%**

```bash
pytest
pytest --cov
```

Lint, formatação e cobertura são validados via **CI** (GitHub Actions).  
Falhas de lint ou cobertura abaixo do mínimo **bloqueiam merges automáticos**, mantendo a qualidade contínua.

---

## ⚙️ Setup Automático

Scripts prontos para preparar o ambiente e validar o código:

| Sistema | Arquivo | Descrição |
|----------|----------|-----------|
| 🪟 Windows | `setup.bat` | Cria `.venv`, instala dependências e executa Black, Ruff, Pytest e validação TOML |
| 🐧 Linux / 🍎 macOS | `setup.sh` | Mesma automação em Shell POSIX |

### ▶️ Execução rápida

```bash
# Linux/Mac
chmod +x setup.sh
./setup.sh

# Windows
setup.bat
```

💡 Ao final:
```
✅ Tudo validado! Pronto para commit e push 🚀
```

---

## 🔄 Integração Contínua (CI)

Cada **push** ou **pull request** executa automaticamente:

✅ Black → formatação PEP8  
🔎 Ruff → lint e boas práticas  
🧪 Pytest → testes unitários  
📊 Cobertura mínima: **90%**

Arquivo: `.github/workflows/ci.yml`

---

## 📘 Documentação e Roadmap

📄 [DOCUMENTACAO_TECNICA.md](./DOCUMENTACAO_TECNICA.md)

**Roadmap:**
- Interface aprimorada  
- Exportação para .md, .pdf, Azure, Jira  
- Documentação viva (MkDocs + GitHub Pages)  
- Testes E2E com Playwright  
- Acessibilidade (Pa11y + WCAG 2.1)

---

## 🤝 Contribuição

Contribuições são muito bem-vindas!  
Abra uma **issue** para bugs ou melhorias, ou envie um **Pull Request** com novas features.

⭐ Se este projeto te ajudou, **deixe uma estrela** no repositório!

---

## 📜 Licença

Licenciado sob **CC BY-NC 4.0**.  
Uso **pessoal e acadêmico** permitido.  
Uso **comercial proibido**.  
Mais detalhes em [Creative Commons](https://creativecommons.org/licenses/by-nc/4.0/).

---

<p align="center">
  <i>Desenvolvido com 💜 por <b>Joelma Prestes Ferreira</b></i>
</p>