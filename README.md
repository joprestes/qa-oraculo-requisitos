<nav aria-label="Language switcher" style="text-align: right;">
  <a href="README.md">🇺🇸 English</a> | 
  <a href="README-pt.md" aria-current="page">🇧🇷 <strong>Português</strong></a>
</nav>

# 🔮 QA Oráculo: Análise de Requisitos com IA

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)
![Test Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen.svg)
---

## 🚀 Por que o QA Oráculo?

Cansou de **User Stories vagas** e reuniões intermináveis para “alinhar entendimentos”?  
O **QA Oráculo** usa **IA de ponta** para transformar requisitos soltos em **especificações prontas para teste**.  

Em minutos, você terá:  
- ✅ Critérios de aceite objetivos.  
- ❓ Perguntas inteligentes para o PO.  
- 📝 Planos de teste completos e organizados.  
- 🧪 Cenários em Gherkin sob demanda.  

É como ter um **QA sênior sempre disponível**, acelerando o planejamento e reduzindo falhas antes mesmo do primeiro bug aparecer.  

---
## 📸 Preview da Interface

![QA Oráculo Demo](assets/qa_oraculo_cartoon_demo.gif)

---

## 🚀 Principais Funcionalidades

-   💻 **Interface Web Interativa** construída com **Streamlit**.  
-   🔍 **Detecção de ambiguidades** e sugestão de perguntas para o PO.  
-   ✅ **Geração de Critérios de Aceite** objetivos e verificáveis.  
-   📝 **Planos de Teste interativos** e casos de teste em Gherkin sob demanda.  
-   ♿ **Foco em Acessibilidade (A11y)**, com cenários baseados nas diretrizes da WCAG.  
-   📊 **Tabela de Casos de Teste** interativa e ordenável, renderizada com **Pandas**.  
-   📥 **Download de Relatórios** completos em formato Markdown.  

---

## 🛠️ Tecnologias Utilizadas

-   🐍 **Python 3.11+**  
-   🌐 **Streamlit** (Framework da Interface Web)  
-   🧠 **LangGraph & Google Gemini** (Orquestração e Modelo de IA)  
-   📊 **Pandas** (Manipulação de Dados para a UI)  
-   🧪 **Unittest & Coverage.py** (Testes e Cobertura de Código)  

---

## ⚙️ Como Executar Localmente

### Pré-requisitos
-   Python 3.11+  
-   Chave de API do Google ([obtenha aqui](https://aistudio.google.com/app/apikey))  

### Instalação
```bash
# Clone o repositório
git clone https://github.com/joprestes/qa-oraculo-requisitos.git
cd qa-oraculo-requisitos

# Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .\.venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

### Configuração da API
Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:  

```env
GOOGLE_API_KEY="sua_chave_de_api_aqui"
```

### Execução
```bash
streamlit run app.py
```

🎉 Pronto! O QA Oráculo abrirá no seu navegador.  

---

## 🧪 Qualidade e Testes

A qualidade deste projeto é garantida por uma suíte de testes unitários robusta que valida a lógica do backend.  

- **Cobertura de Teste**: a lógica de negócio no módulo `graph.py` alcançou **99% de cobertura de linha**, garantindo alta confiabilidade.  
- **Execução dos Testes**:  
  ```bash
  python -m unittest discover tests/
  ```
- **Verificação de Cobertura**:  
  ```bash
  coverage run -m unittest discover tests/ && coverage report -m
  ```

---

## 🤔 Solução de Problemas

❌ **Erro**: API Key inválida  
✔️ Confirme que o arquivo `.env` está na raiz do projeto e que a API “Generative Language” está ativa no Google Cloud.  

❌ **Erro**: comando `streamlit` não encontrado  
✔️ Certifique-se de que o ambiente virtual `.venv` está ativado. Se necessário, reinstale as dependências.  

---

## 📌 Roadmap

- ✅ Interface web interativa com Streamlit  
- ✅ Geração de critérios de aceite e perguntas ao PO  
- ✅ Geração de plano de testes completo sob demanda  
- 📄 Exportação de relatórios em formato PDF  
- 🔗 Integração com APIs do Jira para criar e popular issues  
- 📦 Análise automática de múltiplos requisitos em lote  

---

## 🤝 Contribuição

Sua colaboração é muito bem-vinda!  
- Abra uma **issue** para reportar bugs ou sugerir melhorias.  
- Envie um **Pull Request** com novas funcionalidades.  
- ⭐ Se este projeto te ajudou, deixe uma estrela no repositório!  

---
