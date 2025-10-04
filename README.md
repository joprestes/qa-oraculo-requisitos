<p align="center">
  <img src="assets/logo_oraculo.png" alt="QA Oráculo Logo" width="200"/>
</p>

<h1 align="center">🔮 QA Oráculo</h1>
<p align="center"><i>Análise de Requisitos com Inteligência Artificial</i></p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg"/>
  <img src="https://img.shields.io/badge/license-MIT-green.svg"/>
  <img src="https://img.shields.io/badge/Streamlit-App-red.svg"/>
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg"/>
</p>

<nav aria-label="Language switcher" style="text-align: right;">
<a href="README-en.md">🇺🇸 English</a> |
<a href="README.md" aria-current="page">🇧🇷 <strong>Português</strong></a>
</nav>

## 🚀 Por que usar o QA Oráculo?

Cansou de **User Stories vagas** e **reuniões intermináveis** para alinhar entendimentos?

O **QA Oráculo** transforma requisitos soltos em **especificações prontas para teste** usando IA de ponta.

👉 Em **minutos**, você terá:
- ✅ Critérios de aceite objetivos  
- ❓ Perguntas inteligentes para o PO  
- 📝 Planos de teste completos e organizados  
- 🧪 Cenários em Gherkin sob demanda  
- 📄 Relatórios exportáveis (.md, .pdf, .xlsx)  

É como ter um **QA Sênior disponível 24/7**, acelerando o planejamento e reduzindo falhas antes mesmo do primeiro bug aparecer.

---

## 📸 Preview da Interface

![alt text](assets/qa_oraculo_cartoon_demo.gif)

---

## 🚀 Principais Funcionalidades

- 💻 **Interface Web Interativa** construída com **Streamlit**.  
- 📝 **Análise Editável e Interativa:** Após a IA gerar a análise inicial, a aplicação apresenta um formulário editável. O usuário pode refinar, corrigir e adicionar informações (critérios de aceite, riscos, etc.) antes de prosseguir, garantindo que o plano de testes final seja baseado em requisitos validados por um humano.  
- 🔍 **Detecção de ambiguidades** e sugestão de perguntas para o PO.  
- ✅ **Geração de Critérios de Aceite** objetivos e verificáveis.  
- 📊 **Tabela de Casos de Teste** interativa e ordenável.  
- 📥 **Múltiplas Opções de Exportação** (`.md`, `.pdf`, Azure e Jira).  
- 📖 **Histórico de Análises:** Visualize e consulte análises anteriores.  
- 🗑️ **Gerenciamento de Histórico:** Agora é possível excluir uma análise específica ou limpar todo o histórico de uma vez, sempre com confirmação para evitar exclusões acidentais.  
- 🏗️ **Código Modular, Otimizado e 100% Testado.**  

---

## 🛠️ Tecnologias Utilizadas

- 🐍 Python 3.11+  
- 🌐 Streamlit (Framework da Interface Web)  
- 🧠 LangGraph & Google Gemini (Orquestração e IA)  
- 📊 Pandas (Manipulação de Dados)  
- 📄 FPDF2 (Geração de Relatórios em PDF)  
- 📈 Openpyxl (Manipulação de arquivos Excel .xlsx)  

---

## ⚙️ Como Executar Localmente

<details>
<summary><b>📌 Pré-requisitos</b></summary>

- Python 3.11+  
- Chave de API do Google (obtenha [aqui](https://console.cloud.google.com))  

</details>

<details>
<summary><b>🚀 Instalação</b></summary>

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
```
</details>

<details>
<summary><b>🔑 Configuração da API</b></summary>

Crie um arquivo `.env` na raiz do projeto:

```env
GOOGLE_API_KEY="sua_chave_de_api_aqui"
```
</details>

<details>
<summary><b>▶️ Executar</b></summary>

```bash
streamlit run app.py
```

🎉 O QA Oráculo abrirá no navegador automaticamente!
</details>

---

### 📋 Como Usar

1. **Insira a User Story:** Cole a US que deseja analisar.  
2. **Inicie a Análise:** Clique em "Analisar User Story" para a IA gerar a análise de qualidade inicial.  
3. **Refine a Análise (Etapa de Colaboração):** A aplicação exibirá um formulário pré-preenchido com a análise da IA. Revise, edite os campos conforme necessário e clique em "Salvar Análise e Continuar".  
4. **Decida o Próximo Passo:** Com a análise refinada e salva, escolha se deseja gerar o plano de testes detalhado ou encerrar.  
5. **Exporte os Resultados:** Utilize os botões de download para obter os artefatos em múltiplos formatos. Para Azure e Jira, preencha os campos customizáveis.  
6. **Gerencie o Histórico:** Consulte análises anteriores e use os botões para excluir individualmente ou limpar todo o histórico (com confirmação).  
7. **Comece de Novo:** Clique em "Realizar Nova Análise" para limpar a tela.  

---

## 🤔 Solução de Problemas

❌ **Erro:** API Key inválida  
✔️ Confirme se o arquivo `.env` está na raiz e se a API “Generative Language” está ativa no Google Cloud.  

❌ **Erro:** comando `streamlit` não encontrado  
✔️ Certifique-se de que o ambiente virtual `venv` está ativado.  

---

## 🧪 Qualidade e Testes

A qualidade deste projeto é garantida por uma suíte de testes unitários robusta, construída com `pytest`, que valida a lógica dos módulos `graph.py`, `utils.py`, `database.py` e `app.py`.

- **Cobertura de Teste**: Os módulos críticos alcançam **alta cobertura** (≥97%).  
- **Execução dos Testes**:  
  ```bash
  pytest
  ```

- **Verificação de Cobertura**:  
  ```bash
  pytest --cov
  ```

- **Novos testes do histórico:**  
  - `tests/test_app_history_delete.py` cobre exclusão individual e total de análises.  
  - `tests/conftest.py` garante que o banco seja limpo automaticamente após a execução da suíte de testes.  

---

## 📌 Roadmap

- [x] Interface web interativa com Streamlit  
- [x] Geração de critérios de aceite e perguntas ao PO  
- [x] Geração de plano de testes completo sob demanda  
- [x] Exportação de relatórios em `.md` e `.pdf`  
- [x] Exportação para Azure DevOps (`.xlsx`)  
- [x] Exportação para Jira Zephyr (`.xlsx`)  
- [x] Refatoração do código para arquitetura modular  
- [x] Implementação de Caching para otimizar chamadas de API  
- [x] Centralização de prompts em arquivos de configuração  
- [x] Implementação de suíte de testes com `pytest` (100% de cobertura nos módulos críticos)  
- [x] Permitir edição interativa da análise inicial pelo usuário  
- [x] Histórico de análises com exclusão individual e total (com confirmação)  
- [ ] Containerizar a aplicação com Docker  

---

## 🤝 Contribuição

Contribuições são muito bem-vindas!  
- Abra uma **issue** para reportar bugs ou sugerir melhorias  
- Envie um **Pull Request** com novas funcionalidades  

⭐ Se este projeto te ajudou, não esqueça de deixar uma **estrela no repositório**!

## 📜 Licença
Este projeto é disponibilizado sob a licença **CC BY-NC 4.0**.  
Uso **somente pessoal** é permitido. Uso comercial é **estritamente proibido**.  
Leia mais em [Creative Commons](https://creativecommons.org/licenses/by-nc/4.0/).

