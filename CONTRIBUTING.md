# 🤝 Guia de Contribuição - QA Oráculo

Obrigado por considerar contribuir para o **QA Oráculo**! Este guia vai te ajudar a começar.

---

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Posso Contribuir?](#como-posso-contribuir)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Workflow de Desenvolvimento](#workflow-de-desenvolvimento)
- [Padrões de Código](#padrões-de-código)
- [Padrões de Testes](#padrões-de-testes)
- [Processo de Pull Request](#processo-de-pull-request)
- [Reportando Bugs](#reportando-bugs)
- [Sugerindo Melhorias](#sugerindo-melhorias)

---

## 📜 Código de Conduta

Este projeto segue princípios de respeito, colaboração e inclusão. Esperamos que todos os contribuidores:

- Sejam respeitosos e construtivos
- Aceitem feedback de forma positiva
- Foquem no que é melhor para a comunidade
- Demonstrem empatia com outros membros

---

## 🚀 Como Posso Contribuir?

### Tipos de Contribuição

- 🐛 **Reportar bugs** - Encontrou um problema? Nos avise!
- ✨ **Sugerir features** - Tem uma ideia? Compartilhe!
- 📝 **Melhorar documentação** - Sempre há espaço para clareza
- 🧪 **Adicionar testes** - Mais cobertura é sempre bem-vinda
- 💻 **Implementar features** - Escolha uma issue e mãos à obra!

---

## ⚙️ Configuração do Ambiente

### Pré-requisitos

- Python 3.11 ou superior
- Git
- Conta no GitHub

### Setup Rápido

```bash
# 1. Fork o repositório no GitHub
# 2. Clone seu fork
git clone https://github.com/SEU-USUARIO/qa-oraculo-requisitos.git
cd qa-oraculo-requisitos

# 3. Adicione o repositório original como upstream
git remote add upstream https://github.com/joprestes/qa-oraculo-requisitos.git

# 4. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 5. Instale dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 6. Configure o provedor LLM
cp .env.example .env
# Edite .env com suas credenciais

# 7. Verifique que tudo está funcionando
make test
make dev-check
```

### Comandos Úteis

```bash
make help          # Lista todos os comandos disponíveis
make run           # Executa a aplicação
make test          # Executa testes
make test-cov      # Testes com cobertura
make lint          # Verifica qualidade do código
make format        # Formata código automaticamente
make dev-check     # Verificação completa (lint + testes)
```

---

## 🔄 Workflow de Desenvolvimento

### 1. Sincronize com o Repositório Original

```bash
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

### 2. Crie uma Branch para sua Feature

Use nomenclatura descritiva seguindo o padrão:

```bash
# Features
git checkout -b feat/nome-da-feature

# Correções de bugs
git checkout -b fix/nome-do-bug

# Documentação
git checkout -b docs/nome-da-doc

# Refatoração
git checkout -b refactor/nome-do-refactor

# Testes
git checkout -b test/nome-do-teste
```

### 3. Desenvolva e Teste

```bash
# Faça suas mudanças
# ...

# Execute os testes
make test

# Verifique a qualidade
make dev-check
```

### 4. Commit suas Mudanças

Seguimos o padrão **Conventional Commits**:

```bash
# Formato
<tipo>: <descrição curta>

<corpo opcional>

<rodapé opcional>
```

**Tipos de commit:**
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `style:` - Formatação (sem mudança de lógica)
- `refactor:` - Refatoração de código
- `test:` - Adição ou correção de testes
- `chore:` - Tarefas de manutenção

**Exemplos:**

```bash
git commit -m "feat: adiciona exportação para Cucumber Studio"

git commit -m "fix: corrige validação de User Story vazia"

git commit -m "docs: atualiza guia de instalação com Python 3.13"

git commit -m "test: adiciona testes para validação Pydantic"
```

Veja mais detalhes em [`docs/CONVENTIONAL_COMMITS_GUIDE.md`](docs/CONVENTIONAL_COMMITS_GUIDE.md).

### 5. Push e Pull Request

```bash
# Push para seu fork
git push origin feat/nome-da-feature

# Abra um Pull Request no GitHub
# Use o template fornecido
```

---

## 📏 Padrões de Código

### Princípios

- ✅ **Clean Code** - Código limpo e legível
- ✅ **Clean Architecture** - Separação de responsabilidades
- ✅ **KISS** - Keep It Simple, Stupid
- ✅ **DRY** - Don't Repeat Yourself
- ✅ **YAGNI** - You Aren't Gonna Need It

### Regras Obrigatórias

#### Idioma
- Código, comentários e documentação em **português brasileiro**
- Termos técnicos em inglês quando apropriado (ex: `get`, `set`, `controller`)

#### Formatação
- **Black** para formatação automática
- **Ruff** para linting
- Linha máxima: 88 caracteres (padrão Black)

#### Nomenclatura
```python
# Classes: PascalCase
class UserStoryAnalyzer:
    pass

# Funções e variáveis: snake_case
def analisar_user_story(texto: str) -> dict:
    resultado_analise = {}
    return resultado_analise

# Constantes: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
```

#### Docstrings
```python
def gerar_plano_testes(analise: dict) -> list:
    """
    Gera plano de testes a partir da análise de User Story.
    
    Args:
        analise: Dicionário com resultado da análise
        
    Returns:
        Lista de casos de teste estruturados
        
    Raises:
        ValueError: Se análise estiver vazia ou inválida
    """
    pass
```

#### Type Hints
```python
# Sempre use type hints
def processar_dados(entrada: str, opcoes: dict[str, Any]) -> list[dict]:
    pass

# Para tipos complexos
from typing import Optional, Union

def buscar_analise(id: int) -> Optional[dict]:
    pass
```

#### Tratamento de Erros
```python
# ✅ Bom - Tratamento explícito
try:
    resultado = processar_user_story(texto)
except ValidationError as e:
    logger.error(f"Validação falhou: {e}")
    raise
except Exception as e:
    logger.error(f"Erro inesperado: {e}")
    raise

# ❌ Ruim - Silenciar erros
try:
    resultado = processar_user_story(texto)
except:
    pass  # NUNCA faça isso!
```

#### Sem Código Comentado
```python
# ❌ Ruim
# def funcao_antiga():
#     return "não usar mais"

# ✅ Bom - Se não usa, delete!
```

#### Sem Valores Mágicos
```python
# ❌ Ruim
if len(texto) > 500:
    truncar(texto)

# ✅ Bom
MAX_USER_STORY_LENGTH = 500

if len(texto) > MAX_USER_STORY_LENGTH:
    truncar(texto)
```

---

## 🧪 Padrões de Testes

### Estrutura AAA

Todos os testes devem seguir o padrão **Arrange-Act-Assert**:

```python
def test_deve_validar_user_story_vazia():
    # Arrange (Preparar)
    user_story = ""
    validador = UserStoryValidator()
    
    # Act (Executar)
    resultado = validador.validar(user_story)
    
    # Assert (Verificar)
    assert resultado.valido is False
    assert "vazia" in resultado.mensagem_erro.lower()
```

### Nomenclatura de Testes

```python
# Formato: deve_<resultado>_quando_<condição>
def test_deve_retornar_erro_quando_user_story_vazia():
    pass

def test_deve_gerar_plano_quando_analise_valida():
    pass

def test_deve_exportar_pdf_quando_formato_especificado():
    pass
```

### Isolamento

```python
# ✅ Bom - Testes isolados
def test_criar_analise():
    # Cada teste cria seus próprios dados
    analise = criar_analise_teste()
    assert analise.id is not None

def test_excluir_analise():
    # Não depende do teste anterior
    analise = criar_analise_teste()
    excluir_analise(analise.id)
    assert buscar_analise(analise.id) is None
```

### Mocks

```python
from unittest.mock import Mock, patch

def test_chamada_llm_com_retry():
    # Mock de dependências externas
    with patch('qa_core.llm.GoogleClient') as mock_client:
        mock_client.return_value.generate.return_value = "resposta"
        
        resultado = analisar_com_llm("texto")
        
        assert resultado == "resposta"
        mock_client.return_value.generate.assert_called_once()
```

### Cobertura

- **Meta mínima**: 90% de cobertura
- Execute: `make test-cov`
- Verifique relatório em `htmlcov/index.html`

---

## 🔍 Processo de Pull Request

### Checklist Antes de Abrir PR

- [ ] Código segue os padrões do projeto
- [ ] Testes adicionados/atualizados
- [ ] Todos os testes passando (`make test`)
- [ ] Linters limpos (`make lint`)
- [ ] Cobertura >= 90% (`make test-cov`)
- [ ] Documentação atualizada (se necessário)
- [ ] Commits seguem Conventional Commits
- [ ] Branch atualizada com `main`

### Template de PR

```markdown
## 📝 Descrição

Breve descrição do que foi implementado/corrigido.

## 🎯 Tipo de Mudança

- [ ] 🐛 Bug fix
- [ ] ✨ Nova feature
- [ ] 📝 Documentação
- [ ] 🎨 Refatoração
- [ ] 🧪 Testes

## ✅ Checklist

- [ ] Testes passando
- [ ] Linters limpos
- [ ] Cobertura >= 90%
- [ ] Documentação atualizada

## 📸 Screenshots (se aplicável)

## 🔗 Issues Relacionadas

Closes #123
```

### Processo de Review

1. **Automático**: CI/CD executa testes e linters
2. **Manual**: Revisor analisa código e testa localmente
3. **Feedback**: Discussão e ajustes se necessário
4. **Aprovação**: Merge quando tudo estiver OK

---

## 🐛 Reportando Bugs

### Antes de Reportar

- Verifique se o bug já foi reportado nas [Issues](https://github.com/joprestes/qa-oraculo-requisitos/issues)
- Tente reproduzir em ambiente limpo
- Colete informações relevantes

### Template de Bug Report

```markdown
## 🐛 Descrição do Bug

Descrição clara e concisa do problema.

## 📋 Passos para Reproduzir

1. Vá para '...'
2. Clique em '...'
3. Veja o erro

## ✅ Comportamento Esperado

O que deveria acontecer.

## ❌ Comportamento Atual

O que está acontecendo.

## 🖥️ Ambiente

- OS: [ex: macOS 14.0]
- Python: [ex: 3.11.5]
- Versão QA Oráculo: [ex: 1.0.0]

## 📸 Screenshots

Se aplicável.

## 📝 Logs

```
Cole logs relevantes aqui
```
```

---

## 💡 Sugerindo Melhorias

### Template de Feature Request

```markdown
## ✨ Descrição da Feature

Descrição clara da funcionalidade desejada.

## 🎯 Problema que Resolve

Qual problema esta feature resolve?

## 💭 Solução Proposta

Como você imagina que funcione?

## 🔄 Alternativas Consideradas

Outras abordagens que você pensou?

## 📊 Impacto

- Usuários beneficiados: [ex: todos, apenas admins]
- Complexidade estimada: [baixa/média/alta]
```

---

## 📚 Recursos Adicionais

- [Documentação Completa](docs/README.md)
- [Guia de Setup](docs/SETUP_GUIDE.md)
- [Guia para Desenvolvedores](docs/DEVELOPER_QUICK_START.md)
- [Conventional Commits](docs/CONVENTIONAL_COMMITS_GUIDE.md)
- [Roadmap do Projeto](docs/ROADMAP.md)

---

## 🙏 Agradecimentos

Obrigado por contribuir para tornar o QA Oráculo ainda melhor! Cada contribuição, por menor que seja, é muito valiosa. 💜

---

## 📞 Contato

Dúvidas? Entre em contato:
- **Issues**: [GitHub Issues](https://github.com/joprestes/qa-oraculo-requisitos/issues)
- **Discussões**: [GitHub Discussions](https://github.com/joprestes/qa-oraculo-requisitos/discussions)

---

**Última atualização**: Novembro 2025
