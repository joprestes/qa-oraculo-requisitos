<!-- markdownlint-disable MD024 -->
# Changelog

Todas as mudanças notáveis deste projeto serão documentadas aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [Unreleased]

## [1.6.1] - 2025-10-29

### Fixed

- **Correção de duplicação de lógica de exportação:**
  - Removida duplicação de código na função `render_main_analysis_page`
  - Lógica de exportação agora centralizada na função `_render_export_section()`
  - Eliminado conflito de merge não resolvido que causava bypass da função de exportação
  - Corrigido teste `test_render_main_analysis_page_exportadores` para verificar chamada da função correta

## [1.6.0] - 2025-10-29

### Added

- **Reorganização completa da estrutura do projeto:**
  - Pasta `.config/` para arquivos de configuração centralizados
  - Pasta `scripts/` para scripts de setup e automação
  - Pasta `data/` para banco de dados e dados persistentes
  - Pasta `templates/` para templates e modelos
  - Arquivo `.gitignore` completo e organizado
  - `Makefile` com comandos de desenvolvimento padronizados

- **Melhorias na qualidade dos testes:**
  - Arquivo `tests/test_constants.py` com dados de teste centralizados
  - Refatoração de valores hardcoded para constantes reutilizáveis
  - Melhoria na manutenibilidade e legibilidade dos testes
  - Padronização de dados de teste entre diferentes arquivos

- **Comandos de desenvolvimento via Makefile:**
  - `make setup` - Setup completo do ambiente
  - `make run` - Executar aplicação
  - `make test` - Executar testes
  - `make lint` - Verificação de linting
  - `make format` - Formatação de código
  - `make dev-check` - Verificação completa de qualidade
  - `make help` - Lista todos os comandos disponíveis

### Changed

- **Estrutura de pastas reorganizada:**
  - `pyproject.toml`, `pytest.ini`, `pyrightconfig.json` → `.config/`
  - Scripts de setup → `scripts/`
  - Banco de dados → `data/`
  - Template de PR → `templates/`

- **Configurações atualizadas:**
  - Caminho do banco de dados atualizado para `data/qa_oraculo_history.db`
  - Criação automática da pasta `data/` se não existir
  - Configurações de pytest apontando para nova estrutura

- **Documentação atualizada:**
  - `PROJECT_STRUCTURE.md` com nova organização
  - `README.md` com comandos de desenvolvimento
  - Links internos atualizados para nova estrutura

### Fixed

- **Problemas de testes corrigidos:**
  - Fallback para `st.columns(5)` em ambientes de teste
  - Correção de problemas de indentação em arquivos de teste
  - Melhoria na robustez dos mocks de colunas
  - Correção de problemas de diretório em testes de a11y

- **Melhorias na robustez:**
  - Tratamento de casos onde `st.columns` retorna menos elementos
  - Criação automática de diretórios necessários
  - Melhoria na compatibilidade com diferentes ambientes de teste

## [1.5.0] - 2025-10-29

### Added

- **Exportação para Xray (Jira Test Management):**
  - Nova função `gerar_csv_xray_from_df()` em `qa_core/utils.py`
  - Interface de configuração com campo "Test Repository Folder" obrigatório
  - Suporte a campos personalizados do Jira (Labels, Component, Fix Version, Priority, Assignee, Test Set)
  - Configuração de campos customizados via formato "Campo=Valor"
  - Botão de download "🧪 Xray (.csv)" na seção de exportações
  - Validação: botão desabilitado se Test Repository Folder não for preenchido
  - CSV compatível com Xray Test Case Importer
  - Preservação de quebras de linha nos cenários Gherkin
  - Codificação UTF-8 para caracteres especiais
  - Test_Type definido automaticamente como "Cucumber"

- **Testes automatizados para Xray:**
  - Arquivo `tests/test_xray_export.py` com 10 casos de teste
  - Cobertura completa da funcionalidade de exportação
  - Validação de estrutura CSV, encoding e campos obrigatórios

- **Documentação Xray:**
  - `XRAY_EXPORT_GUIDE.md` - Guia completo de uso
  - `XRAY_IMPLEMENTATION_SUMMARY.md` - Resumo técnico da implementação
  - `RESUMO_FINAL_XRAY.md` - Documentação final
  - `CAMPOS_PERSONALIZADOS_XRAY.md` - Guia de campos customizados

### Changed

- Interface de exportações expandida com seção dedicada ao Xray
- Validação aprimorada para campos obrigatórios de exportação
- Organização melhorada da seção de downloads

### Added

- **Guia de Setup Simplificado:**
  - `SETUP_GUIDE.md` - Guia completo e didático de instalação
  - `quick-setup.sh` - Script automático para Linux/Mac
  - `quick-setup.bat` - Script automático para Windows
  - `DEVELOPER_QUICK_START.md` - Guia rápido para desenvolvedores
  - Setup interativo com configuração automática da API Key
  - Verificação automática de dependências e instalação
  - Instruções claras passo a passo

### Changed

- README principal atualizado com opções de setup simplificado
- Scripts de setup mais amigáveis e informativos
- Melhor organização da documentação de instalação

### Fixed

- Correção de merge conflicts no arquivo `app.py`
- Resolução de problemas de indentação
- Melhoria na estrutura de configuração de exportações

## [1.4.0] - 2025-01-20

### Added

- **Módulo de Acessibilidade (`a11y.py`):**
  - Estilos CSS WCAG 2.1 Level AA
  - Contraste de cores melhorado (12:1)
  - Foco visível em todos os elementos interativos
  - Suporte a prefers-reduced-motion
  - Helpers acessíveis: `accessible_text_area()`, `accessible_button()`, `announce()`
  - Guia de atalhos de teclado no sidebar
  - Documentação de conformidade WCAG

### Changed

- Interface migrada para tema claro (melhor contraste)
- Todos os campos de entrada agora possuem help text contextual
- Mensagens de status são anunciadas automaticamente por leitores de tela

### Fixed

- Contraste de cores inadequado (era 3.2:1, agora 12:1)
- Foco invisível em botões e campos
- Falta de labels descritivos em formulários

## [1.3.0] - 2025-10-06

### Added

- **Integração Contínua (CI)** completa via GitHub Actions:
  - Execução em Python 3.11, 3.12 e 3.13.
  - Verificações automáticas com **Black** e **Ruff**.
  - Testes unitários com **Pytest** e cobertura mínima de 90%.
  - Gate automático para falha em cobertura abaixo de 90%.
  - Validação de sintaxe do `pyproject.toml`.
- **Scripts automáticos de setup:**
  - `setup.sh` (Linux/Mac) e `setup.bat` (Windows).
  - Criação de `.venv`, instalação de dependências e execução de verificações de qualidade.
- **Documentação técnica completa:**
  - `DOCUMENTACAO_TECNICA.md` (Português)
  - `TECHNICAL_DOCUMENTATION_EN.md` (Inglês)
  - `README-en.md` sincronizado com o `README.md`.
- **Nova seção de qualidade de código e CI** adicionada ao `README.md`.

### Changed

- Padronização total do `pyproject.toml`:
  - Reorganização para `[tool.ruff.lint]` conforme nova versão do Ruff.
  - Ajustes de formatação e consistência.
- Atualização visual e estrutural dos scripts de setup com mensagens, emojis e validações.
- Revisão completa do README (em PT e EN) com foco em onboarding e automação.
- Remoção definitiva de menções à containerização (não faz parte da estratégia do projeto).

### Fixed

- Correção de pequenos warnings do Ruff (`E741`, `PLR2004`, etc.).
- Ajustes de indentação e trailing spaces detectados por Black e Yamllint.
- Correção de chaves TOML inválidas no `pyproject.toml`.

---

## [1.2.0] - 2025-10-04

### Added

- Funcionalidade de **exclusão individual e total** do histórico de análises (com confirmação).
- Novos testes unitários em `tests/test_app_history_delete.py`.
- Fixture global `tests/conftest.py` para limpar banco após os testes.
- Documentação atualizada em **README.md** e **README-en.md** com a nova funcionalidade.

### Changed

- Ajustes na UI para exibir confirmações de exclusão no topo da tela.
- Atualização da licença para **CC BY-NC 4.0** (uso pessoal apenas).

### Fixed

- Correção de `KeyError` em `session_state.pop()` ao cancelar exclusões.
