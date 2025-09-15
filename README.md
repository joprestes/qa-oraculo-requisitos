<nav aria-label="Language switcher" style="text-align: right;">
  <a href="README-en.md">🇺🇸 English</a> | <a href="README.md" aria-current="page">🇧🇷 **Português**</a>
</nav>

# 🔮 QA Oráculo: Análise de Requisitos com IA

Analisador de Requisitos de Software com IA para identificar ambiguidades, contradições e riscos antes do desenvolvimento. Este projeto foi construído com foco em acessibilidade e uma abordagem *mobile-first*.

## 🚀 Começando (Getting Started)

Siga os passos abaixo para configurar e executar o projeto em sua máquina local.

### Pré-requisitos

- [Git](https://git-scm.com/)
- [Python 3.10+](https://www.python.org/)

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-nome/qa-oraculo-requisitos.git
    cd qa-oraculo-requisitos
    ```

2.  **Execute o script de setup:**
    Este comando irá criar um ambiente virtual isolado (`.venv`) e instalar todas as dependências necessárias.

    -   **Para Windows (execute no CMD ou PowerShell):**
        ```bash
        setup.bat
        ```

    -   **Para Mac ou Linux (execute no Terminal):**
        Primeiro, dê permissão de execução para o script (você só precisa fazer isso uma vez):
        ```bash
        chmod +x setup.sh
        ```
        Agora, execute o script:
        ```bash
        ./setup.sh
        ```

3.  **Ative o Ambiente Virtual:**
    Após o setup, você precisa ativar o ambiente para começar a trabalhar.

    -   **No Windows:**
        ```bash
        .\.venv\Scriptsctivate
        ```

    -   **No Mac ou Linux:**
        ```bash
        source .venv/bin/activate
        ```
    > O seu terminal agora deve mostrar `(.venv)` no início da linha.

## 🛠️ Como Usar

Com o ambiente ativo, execute o script principal usando o caminho explícito para garantir que o Python correto seja usado:

```bash
# Para Mac/Linux
./.venv/bin/python main.py

# Para Windows
# .\.venv\Scripts\python.exe main.py
```

(Esta seção será melhorada conforme o projeto avança)

## 🤔 Solução de Problemas (Troubleshooting)

Aqui estão as soluções para problemas comuns que você pode encontrar.

### 1. zsh: permission denied: ./setup.sh
**Problema:** Seu sistema está bloqueando a execução do script por razões de segurança.  
**Solução:** Dê permissão de execução ao script (só precisa ser feito uma vez):  
```bash
chmod +x setup.sh
```

### 2. ./setup.sh: python: command not found
**Problema:** O script não encontrou sua instalação do Python com o comando `python`. Isso é comum no macOS e Linux, que usam `python3`.  
**Solução:**
- Abra o arquivo `setup.sh`.
- Altere a linha `python -m venv .venv` para `python3 -m venv .venv`.
- Apague a pasta `.venv` que pode ter sido criada parcialmente (`rm -rf .venv`) e execute o setup novamente.

### 3. ModuleNotFoundError: No module named 'google'
**Problema:** As bibliotecas Python não estão instaladas no seu ambiente virtual, ou o interpretador Python errado está sendo usado.  
**Solução:**
- Garanta que seu ambiente virtual está ativo (você deve ver `(.venv)` no terminal).
- Execute a instalação manualmente usando o pip do ambiente:
```bash
./.venv/bin/python -m pip install -r requirements.txt
```
- Sempre execute seu script usando o caminho explícito para o Python do ambiente virtual para evitar este erro:
```bash
./.venv/bin/python main.py
```

### 4. error: externally-managed-environment
**Problema:** Seu Sistema Operacional está protegendo a instalação principal do Python para que não seja modificada.  
**Solução:** Use sempre o caminho explícito para o pip do ambiente virtual para instalar dependências:
```bash
./.venv/bin/python -m pip install -r requirements.txt
```

----

Este projeto está em desenvolvimento.