<nav aria-label="Language switcher" style="text-align: right;">
  <a href="README-en.md">🇺🇸 English</a> | 
  <a href="README.md" aria-current="page">🇧🇷 <strong>Português</strong></a>
</nav>

# 🔮 QA Oráculo: Análise de Requisitos com IA

Analisador de Requisitos de Software com IA para identificar
ambiguidades, contradições e riscos antes do início do desenvolvimento.
Este projeto é construído com foco em qualidade de código, testabilidade
e acessibilidade.

## ✨ Funcionalidades

-   **Análise de Qualidade:** Avalia a clareza de cada requisito,
    apontando termos vagos e sugerindo melhorias.
-   **Detecção de Conflitos:** Analisa o conjunto de requisitos para
    encontrar contradições lógicas e sobreposições.
-   **Geração de Relatório:** Consolida toda a análise em um relatório
    detalhado em formato Markdown.

## 🚀 Começando (Getting Started)

Siga os passos abaixo para configurar e executar o projeto em sua
máquina local.

### Pré-requisitos

-   [Git](https://git-scm.com/)
-   [Python 3.10+](https://www.python.org/)

### Instalação

1.  **Clone o repositório:**
    `bash     git clone https://github.com/seu-nome/qa-oraculo-requisitos.git     cd qa-oraculo-requisitos`

2.  **Execute o script de setup:** Este comando irá criar um ambiente
    virtual (`.venv`) e instalar as dependências.

    -   **Para Windows:** `setup.bat`
    -   **Para Mac/Linux:** `chmod +x setup.sh` e depois `./setup.sh`

3.  **Configure sua Chave de API:**

    -   Copie o arquivo `.env.example` para um novo arquivo chamado
        `.env`.
    -   Insira sua chave da API do Google Gemini no arquivo `.env`.

4.  **Ative o Ambiente Virtual:**

    -   **No Windows:** `.\.venv\Scriptsctivate`
    -   **No Mac ou Linux:** `source .venv/bin/activate`

## 🛠️ Como Usar

Com o ambiente ativo, execute o script principal para ver uma análise de
exemplo:

``` bash
# Use o caminho explícito para garantir que o Python correto seja usado
./.venv/bin/python main.py
```

## 🧪 Testes

Este projeto utiliza a biblioteca **unittest** do Python para garantir a
qualidade do código.\
Para executar a suíte de testes, rode o seguinte comando na raiz do
projeto:

``` bash
./.venv/bin/python -m unittest discover tests/
```

## 🤔 Solução de Problemas (Troubleshooting)

1.  **zsh: permission denied: ./setup.sh**
    -   Problema: Seu sistema está bloqueando a execução do script por
        segurança.\

    -   Solução: Dê permissão de execução ao script (só precisa ser
        feito uma vez):

        ``` bash
        chmod +x setup.sh
        ```
2.  **./setup.sh: python: command not found**
    -   Problema: O script não encontrou python. Isso é comum no macOS e
        Linux, que usam `python3`.\
    -   Solução: Altere a linha `python -m venv .venv` para
        `python3 -m venv .venv` no arquivo `setup.sh` e execute o setup
        novamente.
3.  **ModuleNotFoundError**
    -   Problema: As bibliotecas não estão instaladas no ambiente
        virtual, ou o interpretador Python errado está sendo usado.\

    -   Solução: Garanta que o ambiente está ativo e execute seu script
        com o caminho explícito:

        ``` bash
        ./.venv/bin/python main.py
        ```
4.  **error: externally-managed-environment**
    -   Problema: Seu SO está protegendo a instalação principal do
        Python.\

    -   Solução: Use o caminho explícito para o pip do ambiente para
        instalar dependências:

        ``` bash
        ./.venv/bin/python -m pip install -r requirements.txt
        ```

------------------------------------------------------------------------

📌 Este projeto está em desenvolvimento.
