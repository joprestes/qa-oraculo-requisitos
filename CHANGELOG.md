# Changelog

Todas as mudanças notáveis deste projeto serão documentadas aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [Unreleased]

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
