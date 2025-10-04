# Changelog

Todas as mudanças notáveis deste projeto serão documentadas aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [Unreleased]

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
