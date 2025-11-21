# Guia de Rotação de API Keys

## 📋 Visão Geral

Este guia documenta as melhores práticas para rotação de API keys no QA Oráculo, garantindo segurança e continuidade operacional.

## 🔐 Por que Rotacionar API Keys?

- **Segurança Proativa**: Reduz o risco de exposição prolongada
- **Conformidade**: Atende requisitos de LGPD/GDPR
- **Mitigação de Vazamentos**: Limita o impacto de keys comprometidas
- **Auditoria**: Facilita rastreamento de uso

## 📅 Frequência Recomendada

| Cenário | Frequência |
|---------|-----------|
| **Produção** | A cada 90 dias |
| **Desenvolvimento** | A cada 180 dias |
| **Suspeita de Comprometimento** | Imediatamente |
| **Saída de Colaborador** | Imediatamente |

## 🔄 Processo de Rotação

### 1. Preparação

```bash
# Backup do arquivo .env atual
cp .env .env.backup.$(date +%Y%m%d)

# Verificar qual provedor está em uso
grep LLM_PROVIDER .env
```

### 2. Geração de Nova Key

#### Google Gemini
1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Clique em "Create API Key"
3. Copie a nova key

#### OpenAI
1. Acesse [OpenAI Platform](https://platform.openai.com/api-keys)
2. Clique em "Create new secret key"
3. Copie a nova key (não será exibida novamente!)

#### Azure OpenAI
1. Acesse o Azure Portal
2. Navegue até seu recurso OpenAI
3. Em "Keys and Endpoint", regenere a key

### 3. Atualização no Projeto

```bash
# Edite o arquivo .env
nano .env

# Atualize a variável correspondente:
# Para Google:
GOOGLE_API_KEY="nova_key_aqui"

# Para OpenAI:
OPENAI_API_KEY="nova_key_aqui"

# Para Azure:
AZURE_OPENAI_KEY="nova_key_aqui"
```

### 4. Verificação

```bash
# Teste a aplicação com a nova key
make run

# Ou execute um teste rápido
.venv/bin/python -c "from qa_core.llm import get_llm_client; client = get_llm_client(); print('✅ Key válida!')"
```

### 5. Revogação da Key Antiga

> [!IMPORTANT]
> Só revogue a key antiga APÓS confirmar que a nova está funcionando!

- **Google**: Delete a key antiga no AI Studio
- **OpenAI**: Delete a key antiga no dashboard
- **Azure**: Regenere a segunda key (se aplicável)

### 6. Limpeza

```bash
# Remova o backup após confirmação
rm .env.backup.*

# Verifique que não há keys no histórico do Git
git log --all --full-history -- .env
```

## 🚨 Em Caso de Comprometimento

### Ação Imediata

```bash
# 1. Revogue a key IMEDIATAMENTE no provedor
# 2. Gere uma nova key
# 3. Atualize o .env
# 4. Reinicie a aplicação
# 5. Monitore logs para uso não autorizado
```

### Checklist de Segurança

- [ ] Key antiga revogada no provedor
- [ ] Nova key gerada e testada
- [ ] `.env` atualizado
- [ ] Backup antigo removido
- [ ] Histórico do Git verificado
- [ ] Logs auditados para uso suspeito
- [ ] Equipe notificada (se aplicável)

## 🔍 Auditoria e Monitoramento

### Logs de Uso

O QA Oráculo sanitiza automaticamente API keys nos logs via `SanitizedLogger`:

```python
# Exemplo de log sanitizado
logger.info(f"Chamada LLM com key: {api_key}")
# Output: "Chamada LLM com key: <REDACTED>"
```

### Verificação de Vazamento

```bash
# Verificar se há keys no código
grep -r "sk-" . --exclude-dir=.venv --exclude-dir=.git

# Verificar histórico do Git
git log -p | grep -i "api_key"
```

## 📚 Boas Práticas

### ✅ Faça

- Use variáveis de ambiente (`.env`)
- Rotacione regularmente
- Mantenha `.env` no `.gitignore`
- Use keys diferentes para dev/prod
- Documente rotações em changelog interno

### ❌ Não Faça

- Commitar keys no Git
- Compartilhar keys por email/chat
- Usar a mesma key em múltiplos projetos
- Deixar keys em código hardcoded
- Ignorar alertas de vazamento

## 🛠️ Automação (Opcional)

### Script de Rotação

```bash
#!/bin/bash
# rotate-api-key.sh

echo "🔄 Iniciando rotação de API key..."

# Backup
cp .env .env.backup.$(date +%Y%m%d)

# Solicitar nova key
read -sp "Nova API Key: " NEW_KEY
echo

# Atualizar .env
sed -i.bak "s/GOOGLE_API_KEY=.*/GOOGLE_API_KEY=\"$NEW_KEY\"/" .env

# Testar
if make test; then
    echo "✅ Rotação concluída com sucesso!"
    rm .env.backup.*
else
    echo "❌ Erro! Restaurando backup..."
    mv .env.backup.* .env
fi
```

## 📞 Suporte

Em caso de dúvidas ou problemas:
1. Consulte a [documentação do provedor](docs/LLM_CONFIG_GUIDE.md)
2. Verifique os logs em `qa_core/observability.py`
3. Abra uma issue no repositório

---

**Última atualização**: 2025-11-21  
**Versão**: 1.0
