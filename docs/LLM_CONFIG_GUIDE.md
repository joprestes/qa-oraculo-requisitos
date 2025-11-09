# 🔐 Guia de Configuração de LLMs para QAs

Este guia explica, passo a passo, como configurar e utilizar os modelos de linguagem (LLMs) do QA Oráculo. O público-alvo são QAs que desejam preparar o ambiente rapidamente e entender o funcionamento da camada de IA sem precisar mergulhar no código.

> **Padrão oficial:** O QA Oráculo já vem preparado para usar o **Google Gemini**. Se você não fizer nenhuma alteração, este será o provedor ativo.

---

## ✅ Pré-requisitos

- **Python 3.11+** instalado (confira com `python3 --version`).
- Acesso ao repositório `qa-oraculo/qa-oraculo-requisitos`.
- Conta no **Google AI Studio** para gerar a chave da API (utilizada pelo Gemini).
- Terminal (macOS/Linux) ou Prompt/PowerShell (Windows) com permissões para executar scripts.

---

## 🛠️ Passo a passo de configuração (Google Gemini – padrão)

### 1. Clonar o projeto e entrar na pasta
```bash
git clone https://github.com/seu-usuario/qa-oraculo.git
cd qa-oraculo/qa-oraculo-requisitos
```

### 2. Criar e ativar o ambiente virtual
```bash
python3 -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\activate     # Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Criar o arquivo `.env`
```bash
cat <<'EOF' > .env
LLM_PROVIDER="google"
LLM_MODEL="gemini-2.0-flash-lite-001"
GOOGLE_API_KEY="SUA_CHAVE_DO_GEMINI"
EOF
```

#### Onde encontrar a Google API Key
1. Acesse [https://aistudio.google.com](https://aistudio.google.com).
2. Clique em **Dashboard → API Keys → Create API Key**.
3. Copie a chave e cole no `.env` no campo `GOOGLE_API_KEY`.
4. Guarde essa chave em um cofre de segredos (Vault, 1Password, etc.).

### 5. Executar o QA Oráculo
```bash
streamlit run main.py
```

O navegador abrirá automaticamente em `http://localhost:8501`. Se isso não ocorrer, cole o endereço manualmente.

---

## 🌐 Variáveis por provedor

A arquitetura permite escolher o provedor via `LLM_PROVIDER`. A tabela abaixo lista as variáveis esperadas e o status atual do suporte.

| Provedor (`LLM_PROVIDER`) | Status | Variáveis necessárias | Onde pegar essas informações |
|---------------------------|--------|------------------------|------------------------------|
| `google` (padrão) | ✅ Ativo | `GOOGLE_API_KEY` <br> `LLM_MODEL` (opcional, default Gemini) | **Google AI Studio** (Dashboard → API Keys) |
| `azure` / `azure_openai` | ⚠️ Em preparação | `AZURE_OPENAI_API_KEY` <br> `AZURE_OPENAI_ENDPOINT` <br> `AZURE_OPENAI_DEPLOYMENT` <br> `AZURE_OPENAI_API_VERSION` | **Portal Azure** → Azure OpenAI → `Keys & Endpoint` / `Deployments` |
| `openai` / `gpt` | ⚠️ Em preparação | `OPENAI_API_KEY` <br> `OPENAI_BASE_URL` (opcional) <br> `OPENAI_ORGANIZATION` (opcional) | **OpenAI Platform** → User menu → `View API keys` / Organization settings |

> Mesmo para provedores ainda não suportados, configurar o `.env` com antecedência ajuda a identificar o que falta quando o suporte for liberado.

---

## 🔄 Como alternar entre provedores

### Mantendo o padrão (Google Gemini)
- Verifique se `LLM_PROVIDER="google"` está no `.env`.
- Certifique-se de que `GOOGLE_API_KEY` está preenchida.
- Opcionalmente ajuste `LLM_MODEL` se quiser usar outro modelo Gemini compatível.

### Azure OpenAI (estrutura pronta, integração em desenvolvimento)
```bash
LLM_PROVIDER="azure"
LLM_MODEL="gpt-4o"
AZURE_OPENAI_API_KEY="chave_azure"
AZURE_OPENAI_ENDPOINT="https://sua-instancia.openai.azure.com"
AZURE_OPENAI_DEPLOYMENT="nome-do-deployment"
AZURE_OPENAI_API_VERSION="2024-02-15-preview"
```
- **Onde obter:** Portal Azure → Recurso Azure OpenAI → menu `Keys & Endpoint` (pegar endpoint e chave) e `Deployments` (nome do deployment e versão da API).
- **Status atual:** o QA Oráculo valida se todos os campos foram preenchidos e informa claramente quais variáveis ainda faltam. A chamada ao modelo ainda não está habilitada.

### OpenAI GPT (estrutura pronta, integração em desenvolvimento)
```bash
LLM_PROVIDER="openai"
LLM_MODEL="gpt-4.1"
OPENAI_API_KEY="chave_do_openai"
# OPENAI_BASE_URL="https://api.openai.com/v1"      # opcional
# OPENAI_ORGANIZATION="org_xxxxx"                 # opcional
```
- **Onde obter:** OpenAI Platform → User (canto superior direito) → `View API keys`. Organization ID em `Settings → Organizations`.
- **Status atual:** semelhante ao Azure, o QA Oráculo valida variáveis e informa que a integração será liberada em uma versão futura.

### Alternando rapidamente
1. Edite o `.env` com o provedor desejado.
2. Salve e **reinicie** o Streamlit (`Ctrl+C` para parar, depois `streamlit run main.py`).
3. Se quiser voltar para o padrão, restaure `LLM_PROVIDER="google"` e garanta que `GOOGLE_API_KEY` esteja presente.

---

## 🧠 Como a camada de LLM funciona

1. **Leitura do `.env`**: o projeto carrega `LLM_PROVIDER`, `LLM_MODEL` e chaves específicas conforme a opção escolhida.
2. **Fábrica de provedores**: o QA Oráculo seleciona automaticamente o driver. Google já está implementado; Azure/OpenAI retornam mensagens indicando o que falta.
3. **Chamadas com retry e observabilidade**: toda chamada registra eventos (`model.call.start`, `model.call.success`, `model.call.error`) com **trace IDs** para troubleshooting.
4. **Resultados**: a IA retorna JSONs estruturados com análise, plano de testes e relatórios. Falhas geram mensagens amigáveis e logs detalhados.

---

## 👩‍💻 Fluxo típico para QAs

1. **Cole a User Story** na área indicada.
2. Clique em **"Gerar análise"**.
3. Aguarde o processamento: mensagens de status e logs aparecem na lateral.
4. Revise a análise inicial, perguntas ao PO, critérios de aceite e riscos.
5. Clique em **"Gerar plano de testes"** para receber cenários Gherkin, resumo e priorização.
6. Utilize os botões de **exportação** (Markdown, PDF, Xray, etc.).
7. Consulte o histórico para revisitar análises anteriores.

> Se algo aparentar travar, abra o terminal onde o Streamlit está rodando: os logs do LangGraph mostram o estado de cada nó e os tempos de execução (útil para QA investigar gargalos ou problemas de quota).

---

## 🧯 Troubleshooting rápido

| Sintoma | Possível causa | Solução sugerida |
|---------|----------------|------------------|
| `LLMError: GOOGLE_API_KEY não configurada` | `.env` incompleto ou variável mal escrita | Verifique se `GOOGLE_API_KEY` consta no `.env` e se o arquivo está na raiz do projeto |
| `LLMError: Azure OpenAI requer variáveis...` | Variável obrigatória do Azure ausente | Preencha todas as variáveis listadas na tabela de provedores |
| `LLMError: OpenAI GPT ainda não suportado` | Integração em desenvolvimento | Aguarde a versão correspondente ou acompanhe o roadmap |
| `LLMRateLimitError` | Limite de requisições do Gemini atingido | Aguarde alguns minutos e tente novamente. Para evitar reincidência, alinhe quotas com o time |
| Resposta vazia / relatório em fallback | Instabilidade temporária do provedor | Tente novamente e consulte os logs (`model.call.error`) |
| `streamlit run` não abre navegador | Porta ocupada ou Streamlit em segundo plano | Use `streamlit run main.py --server.port 8502` ou encerre instâncias anteriores |

---

## 📌 Boas práticas para equipes de QA

- **Centralize as chaves** em um cofre seguro e distribua com parcimônia.
- **Defina quotas internas** para evitar estouro dos limites da API durante sprints.
- **Revise sempre** as análises geradas pela IA antes de exportar.
- **Registre feedbacks**: logs estruturados ajudam a reportar problemas com embasamento.

---

## 🆘 Precisa de ajuda?

- Visite o [README](../README.md) para visão geral do projeto.
- Confira o [CHANGELOG](CHANGELOG.md) para novidades.
- Abra uma issue no GitHub (Issues) ou contate o time responsável com o trace ID e prints do erro.

**Bons testes com o QA Oráculo! 💡**
