# Regras do Workspace - QA Oráculo

Este documento define as regras, padrões e convenções que devem ser seguidos por todos os desenvolvedores e agentes trabalhando no projeto QA Oráculo.

## 1. Princípios Gerais

*   **Idioma**: Todo o código, comentários, documentação e mensagens de commit devem ser em **Português Brasileiro (pt-BR)**. Termos técnicos universais (ex: *controller*, *service*, *payload*) podem ser mantidos em inglês.
*   **Clean Code**: O código deve ser legível, simples e autoexplicativo. Funções devem ser pequenas e ter uma única responsabilidade.
*   **SOLID**: Aplique os princípios SOLID onde fizer sentido, especialmente a separação de responsabilidades e injeção de dependências.
*   **KISS (Keep It Simple, Stupid)**: Evite complexidade acidental. A solução mais simples que resolve o problema é geralmente a melhor.
*   **YAGNI (You Aren't Gonna Need It)**: Não implemente funcionalidades pensando no futuro. Implemente apenas o necessário para os requisitos atuais.

## 2. Workflow de Desenvolvimento

*   **Makefile**: Utilize o `Makefile` para todas as tarefas comuns. Não execute comandos complexos manualmente.
    *   `make setup`: Configuração inicial.
    *   `make run`: Executar a aplicação.
    *   `make test`: Rodar testes.
    *   `make lint`: Verificar estilo.
    *   `make format`: Formatar código.
*   **Ambiente Virtual**: Sempre utilize o ambiente virtual (`.venv`). O `Makefile` gerencia isso automaticamente, mas garanta que seu terminal esteja usando o Python correto.
*   **Dependências**:
    *   Adicione dependências de produção em `requirements.txt`.
    *   Adicione dependências de desenvolvimento em `requirements-dev.txt`.
    *   Sempre congele as versões (`pip freeze`) após adicionar novas libs.

## 3. Qualidade de Código

*   **Linting**: O projeto usa **Ruff**. Nenhum erro de lint deve ser ignorado sem uma justificativa forte (use `# noqa` com o código do erro e explicação).
*   **Formatação**: O projeto usa **Black**. Todo código deve ser formatado automaticamente antes do commit.
*   **Type Checking**: Utilize type hints em todas as assinaturas de função. O projeto usa **Pyright** (configurado no VS Code) para verificação estática.

## 4. Testes

*   **Framework**: Pytest.
*   **Padrão AAA**: Organize os testes em Arrange (preparação), Act (ação) e Assert (verificação).
*   **Cobertura**: A meta é manter a cobertura de código acima de **90%**.
*   **Isolamento**: Testes unitários não devem depender de serviços externos (banco de dados real, APIs externas). Use `unittest.mock` ou `pytest-mock`.
*   **Nomenclatura**: `test_funcionalidade_cenario_resultado` (ex: `test_calculo_imposto_valor_negativo_erro`).

## 5. Git e Versionamento

*   **Commits Semânticos**:
    *   `feat:`: Nova funcionalidade.
    *   `fix:`: Correção de bug.
    *   `docs:`: Alterações na documentação.
    *   `style:`: Formatação, falta de ponto e vírgula, etc. (sem alteração de código).
    *   `refactor:`: Refatoração de código (sem alteração de funcionalidade).
    *   `test:`: Adição ou correção de testes.
    *   `chore:`: Atualização de tarefas de build, configs, etc.
*   **Mensagens**: Claras e descritivas, em português.
*   **Branches**: NUNCA faça commits diretos na `main`. Use branches de feature/fix e faça Pull Requests (mesmo que simulados em ambiente local).

## 6. Segurança

*   **Secrets**: NUNCA commite chaves de API, senhas ou tokens. Use variáveis de ambiente e o arquivo `.env` (que deve estar no `.gitignore`).
*   **Validação**: Valide todas as entradas de dados, especialmente as que vêm de usuários ou APIs externas.
*   **Logs**: Não logue informações sensíveis (PII, tokens).

## 7. Estrutura de Arquivos

*   Mantenha a estrutura definida em `PROJECT_STRUCTURE.md`.
*   Novos módulos devem ir para `qa_core/`.
*   Novos testes devem ir para `tests/`.
*   Scripts utilitários em `scripts/`.

## 8. Documentação

*   Mantenha o `README.md` e outros arquivos em `docs/` atualizados.
*   Adicione docstrings (Google Style ou NumPy Style) em todas as funções e classes públicas.
*   Se uma regra mudar, atualize este arquivo (`WORKSPACE_RULES.md`).
