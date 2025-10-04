# 🔮 QA Oráculo

<p align="center">
  <img src="assets/logo_oraculo.png" alt="Logotipo do QA Oráculo" width="200"/>
</p>

<p align="center">
  <a href="README-en.md" aria-label="Switch to English version of README">🇺🇸 English</a> | 
  <a href="README.md" aria-current="page" aria-label="Versão em Português do README"><strong>🇧🇷 Português</strong></a>
</p>

<p align="center"><i>Análise de Requisitos com Inteligência Artificial</i></p>

---

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

![Demonstração animada do QA Oráculo mostrando a análise interativa](assets/qa_oraculo_cartoon_demo.gif)

---

## 🚀 Principais Funcionalidades

- 💻 **Interface Web Interativa** (Streamlit).  
- 📝 **Análise Editável e Interativa**: refino humano sobre a análise da IA.  
- 🔍 **Detecção de ambiguidades** e sugestão de perguntas para o PO.  
- ✅ **Geração de Critérios de Aceite** verificáveis.  
- 📊 **Tabela de Casos de Teste** interativa.  
- 📥 **Exportação múltipla** (`.md`, `.pdf`, Azure, Jira).  
- 📖 **Histórico de Análises** com exclusão seletiva.  
- 🏗️ **Código Modular, Otimizado e Testado**.  

---

## 🛠️ Tecnologias Utilizadas

- 🐍 Python 3.11+  
- 🌐 Streamlit (interface web)  
- 🧠 LangGraph & Google Gemini (IA)  
- 📊 Pandas  
- 📄 FPDF2 (PDF)  
- 📈 Openpyxl (Excel)  

---

## ⚙️ Como Executar Localmente

### 📌 Pré-requisitos
- Python 3.11+  
- Chave de API do Google ([obter aqui](https://console.cloud.google.com))  

### 🚀 Instalação
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
pip install -r requirements-dev.txt  # Para testes e dev
```

### 🔑 Configuração da API
Crie um arquivo `.env` na raiz:
```env
GOOGLE_API_KEY="sua_chave_de_api_aqui"
```

### ▶️ Executar
```bash
streamlit run app.py
```

🎉 O QA Oráculo abrirá automaticamente no navegador!

---

## 📋 Como Usar

1. **Insira a User Story** no campo indicado.  
2. Clique em **“Analisar User Story”**.  
3. **Revise e edite** a análise gerada pela IA.  
4. Escolha gerar o **plano de testes** ou encerrar.  
5. **Exporte** para `.md`, `.pdf`, `.xlsx`, Azure ou Jira.  
6. Consulte e gerencie o **histórico de análises**.  
7. Clique em **“Nova Análise”** para começar de novo.  

### 🔎 Exemplo prático
**Input:**  
```
Como usuário do app de banco,
quero redefinir minha senha via e-mail,
para recuperar o acesso em caso de esquecimento.
```

**Saída gerada:**  
- Critérios de Aceite:
  - Link de redefinição enviado em menos de 1 minuto.  
  - O link expira em 24h.  
  - Nova senha deve ter mínimo de 8 caracteres, com letras e números.  

- Perguntas ao PO:
  - O link de redefinição expira em quantas horas?  
  - Há limite de tentativas de redefinição por dia?  

- Cenário Gherkin:
  ```gherkin
  Scenario: Redefinir senha com sucesso
    Given que o usuário informou um e-mail válido
    When solicita redefinição de senha
    Then recebe um link de redefinição válido por 24h
  ```

---

## 🤔 Solução de Problemas

❌ **Erro: API Key inválida**  
✔️ Verifique `.env` e se a API “Generative Language” está ativa.  

❌ **Erro: comando `streamlit` não encontrado**  
✔️ Ative o ambiente virtual `venv`.  

---

## 🧪 Testes e Qualidade

- **Cobertura ≥97%** com `pytest`.  
- **Novos testes** garantem histórico limpo e consistente.  

```bash
pytest
pytest --cov
```

Configurações centralizadas em `pyproject.toml`:  
- `black` (linha: 88)  
- `pytest` com cobertura e warnings desabilitados  

---

## 🧰 Setup Automático e Qualidade de Código

O QA Oráculo possui scripts prontos para configurar e validar todo o ambiente de desenvolvimento em poucos minutos.  
Eles garantem que o código local siga os **mesmos padrões de qualidade do CI (GitHub Actions)**.

### ⚙️ Scripts disponíveis

| Sistema | Arquivo | Descrição |
|----------|----------|-----------|
| 🪟 Windows | `setup.bat` | Cria `.venv`, instala dependências e executa Black, Ruff, Pytest e validação TOML. |
| 🐧 Linux / 🍎 macOS | `setup.sh` | Versão equivalente, compatível com shells POSIX. |

---

### ▶️ Execução Rápida

**Windows**
```bash
setup.bat
```

**Linux / Mac**
```bash
chmod +x setup.sh
./setup.sh
```

Esses scripts executam automaticamente:
1. 🧱 Criação do ambiente virtual `.venv`
2. 📦 Instalação das dependências (`requirements.txt`)
3. 🎯 Verificação de formatação com **Black**
4. 🧹 Lint completo com **Ruff**
5. 🧩 Validação da sintaxe do `pyproject.toml`
6. 🧪 Execução dos testes unitários e relatório de cobertura

> 💡 Ao final, o terminal mostrará “✅ Setup concluído com sucesso!” se tudo estiver conforme os padrões do CI.

---

### 🧠 Comandos Individuais (caso prefira rodar manualmente)
| Tarefa | Comando |
|--------|----------|
| Formatar código | `black .` |
| Verificar lint | `ruff check .` |
| Rodar testes com cobertura | `pytest --cov --cov-report=term-missing` |
| Validar TOML | `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('✅ TOML válido!')"` |

---

### 🔄 Integração Contínua (CI)

Cada *push* ou *pull request* na branch `main` executa o workflow de CI:

- ✅ **Black**: garante conformidade com PEP8  
- 🔎 **Ruff**: lint de boas práticas e imports  
- 🧪 **Pytest**: roda todos os testes unitários  
- 📊 **Cobertura mínima exigida**: **90%**

Arquivo: [`/.github/workflows/ci.yml`](.github/workflows/ci.yml)

> 💬 Falhas de lint ou cobertura abaixo do mínimo bloqueiam o merge automático, garantindo a integridade do código.

---

## 📘 Documentação Técnica

Para detalhes técnicos e de contribuição, consulte:  
👉 [`DOCUMENTACAO_TECNICA.md`](DOCUMENTACAO_TECNICA.md)

---

## 📌 Roadmap

- [x] Interface web com Streamlit  
- [x] Exportação para `.md`, `.pdf`, Azure, Jira  
- [x] Histórico com exclusão seletiva  
- [x] Integração contínua (CI) com cobertura mínima 90%  
- [ ] Acessibilidade automática (Pa11y + WCAG 2.1)  
- [ ] Documentação viva (MkDocs + GitHub Pages)  
- [ ] Testes E2E com Playwright  

---

## 🤝 Contribuição

Contribuições são bem-vindas!  
- Abra uma **issue** para bugs ou melhorias.  
- Faça um **Pull Request** com novas features.  

⭐ Se este projeto te ajudou, deixe uma **estrela** no repositório!

---

## 📜 Licença

Este projeto está sob **CC BY-NC 4.0**.  
Uso **pessoal e acadêmico permitido**, uso **comercial proibido**.  

Mais detalhes em [Creative Commons](https://creativecommons.org/licenses/by-nc/4.0/).
