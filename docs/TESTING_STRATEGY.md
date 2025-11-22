# Estratégia de Testes - QA Oráculo

Este documento descreve a estratégia de testes do projeto QA Oráculo, cobrindo testes unitários, testes de interface (frontend) e verificações manuais.

## 1. Visão Geral

O projeto segue uma pirâmide de testes com forte base em testes unitários e verificações de integração/UI.

- **Ferramenta Principal**: `pytest`
- **Cobertura Mínima Exigida**: 90%
- **Linters**: `ruff`, `black`

## 2. Testes Unitários (Backend & Core)

Os testes unitários validam a lógica de negócios, integrações com LLMs (mockadas) e utilitários.

- **Localização**: `tests/unit/`
- **Como Executar**:
  ```bash
  pytest tests/unit
  ```

### Principais Módulos Testados:
- `qa_core/llm`: Providers e Factory.
- `qa_core/exports.py`: Geração de CSV/Excel (Azure, Xray, TestRail).
- `qa_core/utils.py`: Funções auxiliares.

## 3. Testes de Frontend (Streamlit)

Como o Streamlit é um framework de UI, testamos de duas formas:

### 3.1. Testes Unitários de UI (Mockados)
Validam a lógica de renderização e manipulação de estado (`session_state`) sem abrir o navegador.

- **Localização**: `tests/unit/qa_core/app/`
- **Arquivos Chave**:
  - `test_main_page/test_export_section.py`: Valida botões de download e lógica de exportação.
  - `test_main_page/test_export_previews.py`: Valida a geração de previews (decodificação de bytes, tratamento de erros).
  - `test_history_page.py`: Valida filtros, exclusão e listagem do histórico.

### 3.2. Verificação Manual / Browser
Certos comportamentos visuais devem ser validados manualmente ou via automação de browser.

#### Checklist de Verificação Visual:

**1. Página de Histórico**
- [ ] Acessar "Histórico de Análises" no menu lateral.
- [ ] Verificar se existe **apenas uma** seção de filtros (dentro de um expander "Buscar e Filtrar").
- [ ] Confirmar que **não** existe uma seção duplicada de busca abaixo da lista.
- [ ] Testar filtro por texto e data.

**2. Preview de Exportações**
- [ ] Realizar uma análise (ou usar dados mockados).
- [ ] Expandir "Visualizar Arquivos de Exportação (Preview)".
- [ ] Clicar nas abas (Azure, TestRail, Xray).
- [ ] **Critério de Aceite**: O conteúdo deve ser exibido como texto (CSV) e não apresentar erro de "bytes-like object".
- [ ] **Critério de Aceite**: Se houver erro, deve exibir um alerta amarelo (warning) amigável, não um stack trace.

## 4. Cobertura de Código

Para verificar a cobertura:

```bash
pytest --cov=qa_core --cov-report=term-missing
```

A CI/CD deve falhar se a cobertura for inferior a 90%.

## 5. Comandos Úteis

| Ação | Comando |
|------|---------|
| Rodar todos os testes | `pytest` |
| Rodar apenas testes de UI | `pytest tests/unit/qa_core/app` |
| Verificar cobertura | `pytest --cov=qa_core` |
| Linting | `ruff check . && black .` |
