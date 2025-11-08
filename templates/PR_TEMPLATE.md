# 🚀 Resumo da Pull Request

- Descreva em 2–3 frases o objetivo e o impacto principal da mudança.
- Destaque qualquer decisão relevante para o time de QA que dará suporte ao código.

## ✨ Detalhes da Implementação

- **Contexto**: explique o problema ou oportunidade.
- **Solução**: descreva os principais pontos da implementação (componentes tocados, fluxos afetados).
- **Notas para QA**: informações importantes para suporte, rollback ou monitoramento.

## 🧪 Testes Realizados

- `pytest --cov`
- `ruff check .`
- `black --check .`
- Outros (descreva comandos, cenários manuais, capturas se aplicável)

## 📚 Documentação

- [ ] Atualizei a documentação relevante (`README`, `docs/*`, guias internos).
- [ ] Não foi necessário atualizar documentação (explique brevemente):

## ✅ Checklist de Qualidade

- [ ] Cobertura de testes ≥ 90% (validada no CI e localmente).
- [ ] Layout revisado em viewport mobile (Mobile First).
- [ ] Checklist de acessibilidade cumprido (`docs/ACESSIBILIDADE.md`).
- [ ] Comentários adicionados/ajustados são didáticos e explicam o “porquê”.
- [ ] Padrões arquiteturais respeitados (responsabilidades bem definidas).
- [ ] `make dev-check` (ou comandos equivalentes) executado sem erros.

Se algum item não puder ser marcado, explique na seção de detalhes para alinharmos um plano de ação.
