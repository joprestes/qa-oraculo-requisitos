# 📝 Guia de Conventional Commits - QA Oráculo

Este guia explica como usar **Conventional Commits** no QA Oráculo para gerar releases automáticas e changelogs estruturados.

## 📋 Índice

- [O que são Conventional Commits?](#o-que-são-conventional-commits)
- [Formato Básico](#formato-básico)
- [Tipos de Commit](#tipos-de-commit)
- [Exemplos Práticos](#exemplos-práticos)
- [Como Aciona Releases](#como-aciona-releases)
- [Boas Práticas](#boas-práticas)
- [Ferramentas](#ferramentas)

---

## 🎯 O que são Conventional Commits?

**Conventional Commits** é uma convenção para mensagens de commit que facilita:

- ✅ Geração automática de changelogs
- 🚀 Versionamento semântico automático
- 📦 Releases automatizadas
- 🔍 Histórico de commits mais legível

---

## 📐 Formato Básico

```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé opcional]
```

### Componentes:

1. **Tipo** (obrigatório): Categoria do commit
2. **Escopo** (opcional): Área afetada (ex: `auth`, `export`, `llm`)
3. **Descrição** (obrigatório): Resumo curto das mudanças
4. **Corpo** (opcional): Explicação detalhada
5. **Rodapé** (opcional): Breaking changes, issues relacionadas

---

## 🏷️ Tipos de Commit

### Tipos que Geram Release

| Tipo | Descrição | Versão | Exemplo |
|------|-----------|--------|---------|
| `feat` | Nova funcionalidade | **MINOR** | 1.0.0 → 1.1.0 |
| `fix` | Correção de bug | **PATCH** | 1.0.0 → 1.0.1 |
| `perf` | Melhoria de performance | **PATCH** | 1.0.0 → 1.0.1 |
| `revert` | Reversão de commit | **PATCH** | 1.0.0 → 1.0.1 |
| `refactor` | Refatoração sem mudança de comportamento | **PATCH** | 1.0.0 → 1.0.1 |

### Tipos que NÃO Geram Release

| Tipo | Descrição | Versão |
|------|-----------|--------|
| `docs` | Apenas documentação | Nenhuma |
| `style` | Formatação, espaços, etc. | Nenhuma |
| `test` | Adição/correção de testes | Nenhuma |
| `chore` | Tarefas de manutenção | Nenhuma |
| `build` | Mudanças no build | Nenhuma |
| `ci` | Mudanças no CI/CD | Nenhuma |

### Breaking Changes (MAJOR)

Qualquer commit com `!` após o tipo ou `BREAKING CHANGE:` no rodapé gera uma **MAJOR** release:

```
feat!: remover suporte a Python 3.10
```

Versão: 1.0.0 → **2.0.0**

---

## 💡 Exemplos Práticos

### ✨ Nova Funcionalidade (feat)

```bash
git commit -m "feat: adicionar exportação para Cucumber Studio"
```

**Resultado**: 1.0.0 → 1.1.0

---

### 🐛 Correção de Bug (fix)

```bash
git commit -m "fix: corrigir erro na validação de User Story vazia"
```

**Resultado**: 1.0.0 → 1.0.1

---

### ⚡ Melhoria de Performance (perf)

```bash
git commit -m "perf: otimizar cache de chamadas LLM"
```

**Resultado**: 1.0.0 → 1.0.1

---

### 📝 Documentação (docs)

```bash
git commit -m "docs: atualizar README com instruções de instalação"
```

**Resultado**: Nenhuma release

---

### ♻️ Refatoração (refactor)

```bash
git commit -m "refactor: extrair lógica de exportação para módulo separado"
```

**Resultado**: 1.0.0 → 1.0.1

---

### 🎨 Estilo (style)

```bash
git commit -m "style: formatar código com Black"
```

**Resultado**: Nenhuma release

---

### ✅ Testes (test)

```bash
git commit -m "test: adicionar testes para provedor Azure OpenAI"
```

**Resultado**: Nenhuma release

---

### 🔧 Manutenção (chore)

```bash
git commit -m "chore: atualizar dependências"
```

**Resultado**: Nenhuma release

---

### 🚨 Breaking Change (MAJOR)

**Opção 1: Com `!`**
```bash
git commit -m "feat!: remover modo escuro da aplicação"
```

**Opção 2: Com rodapé**
```bash
git commit -m "feat: migrar para Python 3.12+

BREAKING CHANGE: Python 3.10 não é mais suportado"
```

**Resultado**: 1.0.0 → **2.0.0**

---

## 🚀 Como Aciona Releases

### Fluxo Automático

1. **Você faz um commit** com conventional commit:
   ```bash
   git commit -m "feat: adicionar indicadores de progresso"
   ```

2. **Push para main** (após merge de PR):
   ```bash
   git push origin main
   ```

3. **Workflow de Release é acionado** automaticamente

4. **Semantic Release analisa** os commits desde a última release

5. **Determina a próxima versão**:
   - `feat` → MINOR (1.0.0 → 1.1.0)
   - `fix` → PATCH (1.0.0 → 1.0.1)
   - `feat!` → MAJOR (1.0.0 → 2.0.0)

6. **Gera changelog** automaticamente em `docs/RELEASE_NOTES.md`

7. **Cria tag e release** no GitHub

8. **Commita changelog** de volta para o repositório

---

## ✅ Boas Práticas

### ✔️ Faça

- ✅ Use verbos no imperativo: "adicionar", "corrigir", "remover"
- ✅ Seja conciso na descrição (máximo 72 caracteres)
- ✅ Use minúsculas na descrição
- ✅ Não termine a descrição com ponto final
- ✅ Use corpo para explicações detalhadas
- ✅ Referencie issues no rodapé: `Closes #123`

### ❌ Evite

- ❌ Mensagens genéricas: "fix bug", "update code"
- ❌ Misturar múltiplos tipos em um commit
- ❌ Commits muito grandes (faça commits atômicos)
- ❌ Usar `feat` para mudanças internas que não afetam usuários

---

## 🛠️ Ferramentas

### Commitizen (Assistente Interativo)

Instale:
```bash
npm install -g commitizen cz-conventional-changelog
```

Use:
```bash
git cz
```

Isso abre um assistente interativo para criar commits!

### Commitlint (Validação)

Instale:
```bash
npm install -g @commitlint/cli @commitlint/config-conventional
```

Configure `.commitlintrc.json`:
```json
{
  "extends": ["@commitlint/config-conventional"]
}
```

Valide:
```bash
echo "feat: nova feature" | commitlint
```

### Husky (Git Hooks)

Valide commits automaticamente antes de commitar:

```bash
npm install -g husky
npx husky install
npx husky add .husky/commit-msg 'npx commitlint --edit $1'
```

---

## 📊 Exemplos Reais do QA Oráculo

### Fase 1: Estabilização

```bash
feat: implementar validação de entrada com Pydantic
fix: corrigir sanitização de logs para remover PII
perf: adicionar índices no banco de dados SQLite
test: aumentar cobertura de testes LLM para 90%
docs: criar guia de rotação de API keys
```

### Fase 2: Expansão

```bash
feat: adicionar exportação para Postman Collections
feat: implementar comparação entre análises
feat: adicionar preview de exportações
fix: corrigir erro ao filtrar histórico por data
refactor: extrair lógica de diff para módulo separado
```

### Fase 3: Escalabilidade

```bash
feat: adicionar métricas Prometheus
feat: implementar testes de performance com pytest-benchmark
feat: adicionar workflow de release automático
ci: configurar job de performance no CI
docs: criar guia de conventional commits
```

---

## 🔍 Verificando Commits

### Ver commits desde a última tag

```bash
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

### Ver apenas commits que geram release

```bash
git log --oneline --grep="^feat" --grep="^fix" --grep="^perf" -E
```

### Ver breaking changes

```bash
git log --oneline --grep="BREAKING CHANGE" --grep="!" -E
```

---

## 📚 Recursos Adicionais

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Semantic Release Documentation](https://semantic-release.gitbook.io/)
- [Commitizen Documentation](https://commitizen-tools.github.io/commitizen/)

---

## 🆘 Troubleshooting

### Commit não gerou release

1. Verifique se o tipo está correto (`feat`, `fix`, etc.)
2. Verifique se não é um tipo que não gera release (`docs`, `chore`)
3. Verifique se o workflow de release foi executado
4. Verifique logs do workflow no GitHub Actions

### Release gerou versão errada

1. Verifique se usou `!` para breaking change
2. Verifique se o tipo está correto
3. Verifique configuração do `.releaserc.json`

### Mensagem de commit foi rejeitada

1. Verifique o formato: `tipo: descrição`
2. Verifique se o tipo é válido
3. Verifique se há espaço após os dois pontos
4. Verifique se a descrição está em minúsculas

---

**Última atualização**: Novembro 2025
