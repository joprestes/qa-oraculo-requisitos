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

### Regras Obrigatórias de Branch

*   **NUNCA faça commits diretamente na branch `main`**.
*   **SEMPRE crie uma branch antes de iniciar qualquer alteração**.
*   Nomenclatura de branches:
    *   `feature/nome-da-funcionalidade` para novas funcionalidades
    *   `fix/nome-do-bug` para correções
    *   `refactor/nome-da-refatoracao` para refatorações
    *   `docs/nome-da-documentacao` para documentação

### Commits Semânticos

*   `feat:`: Nova funcionalidade.
*   `fix:`: Correção de bug.
*   `docs:`: Alterações na documentação.
*   `style:`: Formatação, falta de ponto e vírgula, etc. (sem alteração de código).
*   `refactor:`: Refatoração de código (sem alteração de funcionalidade).
*   `test:`: Adição ou correção de testes.
*   `chore:`: Atualização de tarefas de build, configs, etc.

### Fluxo de Trabalho

1. Crie uma branch a partir da `main`: `git checkout -b feature/minha-feature`
2. Faça seus commits na branch criada
3. Abra um Pull Request para a `main`
4. Após aprovação, faça o merge

*   **Mensagens**: Claras e descritivas, em português.

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

## 9. Smoke Test Obrigatório (Frontend)

**ANTES de qualquer commit**, execute o smoke test manual via browser para garantir que a aplicação está funcional.

### Pré-requisitos
1. Inicie a aplicação: `make run` ou `streamlit run main.py`
2. Acesse: `http://localhost:8501`

### Checklist do Smoke Test

#### 9.1 Carregamento Inicial
- [ ] Página principal carrega sem erros
- [ ] Logo e título "QA Oráculo" são exibidos
- [ ] Sidebar está visível e funcional
- [ ] Nenhum erro no console do navegador (F12 → Console)

#### 9.2 Fluxo Principal - Análise de User Story
- [ ] Campo de texto "User Story" está visível e editável
- [ ] Inserir User Story de teste: `Como usuário, quero fazer login para acessar o sistema`
- [ ] Botão "Analisar" está habilitado após inserir texto
- [ ] Clicar em "Analisar" inicia o processamento (spinner visível)
- [ ] Análise é exibida sem erros (critérios de aceite, riscos, perguntas ao PO)

#### 9.3 Fluxo Principal - Plano de Testes
- [ ] Botão "Gerar Plano de Testes" está habilitado após análise
- [ ] Clicar no botão inicia o processamento
- [ ] Plano de testes é exibido com cenários Gherkin
- [ ] Cenários podem ser expandidos/colapsados

#### 9.4 Edição de Cenários
- [ ] Botão "✏️ Editar" funciona em pelo menos um cenário
- [ ] Campo de edição aparece ao clicar
- [ ] Botões "✅ Confirmar" e "❌ Cancelar" funcionam
- [ ] Botão "🗑️ Excluir" exibe confirmação antes de excluir

#### 9.5 Exportações
- [ ] Seção "Opções de Exportação" está visível
- [ ] Botão "📄 Markdown (.md)" faz download
- [ ] Botão "📕 PDF (.pdf)" faz download
- [ ] Botão "☁️ Azure DevOps (.csv)" faz download
- [ ] Botão "📊 Jira Zephyr (.xlsx)" faz download
- [ ] Campo "Test Repository Folder" habilita botão Xray quando preenchido
- [ ] Botão "🧪 Xray (.csv)" faz download (após preencher folder)
- [ ] Botão "🧪 TestRail (.csv)" faz download

#### 9.6 Histórico
- [ ] Navegação para "Histórico" funciona (sidebar ou menu)
- [ ] Análises anteriores são listadas (se houver)
- [ ] Clicar em uma análise exibe os detalhes
- [ ] Botão de exclusão funciona com confirmação

#### 9.7 Acessibilidade Básica
- [ ] Navegação por teclado (Tab) funciona nos elementos principais
- [ ] Foco visível nos elementos interativos
- [ ] Texto legível com contraste adequado

### User Story de Teste Padrão

Use esta User Story para testes:

```
Como gerente de contas, quero validar faturas atrasadas para priorizar cobranças, garantindo pagamentos em dia.

Critérios de Aceite:
- Faturas com mais de 30 dias devem ser destacadas em vermelho
- Sistema deve enviar notificação automática ao cliente
- Relatório deve ser gerado diariamente às 8h
```

### Resultado Esperado

- [ ] **TODOS os itens do checklist devem passar**
- [ ] Se algum item falhar, **NÃO faça o commit**
- [ ] Corrija o problema e execute o smoke test novamente

### Registro do Smoke Test

Ao concluir o smoke test com sucesso, inclua na mensagem de commit:
```
feat: implementa nova funcionalidade X

- Descrição das alterações
- Smoke test: ✅ PASSED
```