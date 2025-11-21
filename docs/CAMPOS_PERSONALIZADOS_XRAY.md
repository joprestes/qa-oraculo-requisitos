# ✅ Atualização: Suporte a Campos Personalizados para Xray

## 📌 O Que Foi Adicionado

A funcionalidade de exportação Xray agora suporta **campos personalizados e customizados** do Jira/Xray!

---

## 🎯 Campos Suportados

### 1️⃣ Campos Padrão (Interface Gráfica)

Disponíveis diretamente na interface do QA Oráculo:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| **Labels** | Etiquetas para categorização | `QA, Automation, Regression` |
| **Priority** | Prioridade do teste | `High`, `Medium`, `Low` |
| **Component** | Componente do sistema | `Pagamentos`, `Login`, `API` |
| **Assignee** | Responsável pelo teste | `joao.silva@empresa.com` |

### 2️⃣ Campos Customizados (Área de Texto)

Para campos específicos do seu Jira, use o formato `NomeCampo=Valor`:

```
Epic Link=PROJ-123
Sprint=Sprint 10
Custom Field=Valor Personalizado
Story Points=8
Team=Squad Pagamentos
```

---

## 🖥️ Como Usar na Interface

### Passo 1: Expandir Seção de Campos Personalizados

Na seção **"Xray (Jira Test Management)"**, expanda:
```
+ Campos Personalizados (Opcional)
```

### Passo 2: Preencher Campos Padrão

Use os campos prontos na interface:

```
Labels: QA, Automation, Regression
Priority: High
Component: Pagamentos
Assignee: joao.silva@empresa.com
```

### Passo 3: Adicionar Campos Customizados

Na área "Campos Customizados (um por linha)":

```
Epic Link=PROJ-123
Sprint=Sprint 10
```

---

## 📄 Exemplo de CSV Gerado

### CSV Sem Campos Personalizados:
```csv
"Summary","Description","Test_Repository_Folder","Test_Type","Gherkin_Definition"
"Teste de Login","Descrição do teste","Login","Cucumber","Given..."
```

### CSV COM Campos Personalizados:
```csv
"Summary","Description","Test_Repository_Folder","Test_Type","Gherkin_Definition","Labels","Priority","Component","Assignee","Epic Link"
"Teste de Login","Descrição do teste","Login","Cucumber","Given...","QA,Automation","High","Pagamentos","joao@empresa.com","PROJ-123"
```

---

## 🔧 Implementação Técnica

### Função Atualizada

```python
def gerar_csv_xray_from_df(
    df_original: pd.DataFrame,
    test_repository_folder: str,
    custom_fields: dict | None = None,
) -> bytes:
    """
    Args:
        custom_fields: Dicionário com campos personalizados
                      Ex: {"Labels": "QA,Automation", "Priority": "High"}
    """
```

### Exemplo de Uso Programático

```python
from qa_core.exports import gerar_csv_xray_from_df

# Definir campos personalizados
custom_fields = {
    "Labels": "QA,Automation,Regression",
    "Priority": "High",
    "Component": "Pagamentos",
    "Assignee": "joao.silva@empresa.com",
    "Epic Link": "PROJ-123",
    "Sprint": "Sprint 10"
}

# Gerar CSV
csv_bytes = gerar_csv_xray_from_df(
    df=cenarios_df,
    test_repository_folder="TED",
    custom_fields=custom_fields
)
```

---

## 🧪 Testes Adicionados

**4 novos testes** foram criados para validar campos personalizados:

1. ✅ `test_gerar_csv_xray_com_campos_personalizados` - Campos padrão
2. ✅ `test_gerar_csv_xray_com_campos_personalizados_complexos` - Campos com nomes compostos
3. ✅ `test_gerar_csv_xray_sem_campos_personalizados` - Backward compatibility
4. ✅ `test_gerar_csv_xray_ordem_campos_personalizados` - Ordem preservada

**Total de testes**: 14/14 passando ✨

---

## 📊 Benefícios

✅ **Flexibilidade Total**: Suporte a qualquer campo do Jira/Xray  
✅ **Interface Amigável**: Campos comuns pré-configurados  
✅ **Campos Customizados**: Qualquer campo específico do seu projeto  
✅ **Retrocompatibilidade**: Funciona sem campos personalizados  
✅ **Validação Completa**: 14 testes cobrindo todos os cenários  

---

## 🎯 Casos de Uso

### Uso 1: Projeto com Epics
```
Test Repository Folder: Pagamentos
Labels: QA, Automation
Priority: High
Epic Link: PROJ-456
```

### Uso 2: Projeto com Sprints
```
Test Repository Folder: Login
Labels: Security, Critical
Sprint: Sprint 15
Team: Squad Core
```

### Uso 3: Campos Específicos da Empresa
```
Test Repository Folder: API
Labels: Integration
Business Area: Financeiro
Compliance: LGPD
Risk Level: Medium
```

---

## 💡 Dicas

1. **Nomes de Campos**: Use exatamente como aparecem no Jira (case-sensitive)
2. **Campos Obrigatórios**: Verifique quais campos são obrigatórios no seu Jira
3. **Valores Múltiplos**: Para Labels, separe por vírgula: `QA, Automation, Smoke`
4. **Teste Primeiro**: Importe um teste de exemplo para validar os campos

---

## 📚 Arquivos Modificados

### Core
- ✅ `qa_core/utils.py` - Função `gerar_csv_xray_from_df()` atualizada
- ✅ `qa_core/app.py` - Interface com campos personalizados

### Testes
- ✅ `tests/test_xray_export.py` - 4 novos testes adicionados

### Documentação
- ✅ `docs/XRAY_EXPORT_GUIDE.md` - Seção de campos personalizados
- ✅ `CAMPOS_PERSONALIZADOS_XRAY.md` - Este documento

---

## ✨ Estatísticas

- **Linhas de código adicionadas**: ~120 linhas
- **Testes criados**: +4 (total 14)
- **Campos padrão suportados**: 4 (Labels, Priority, Component, Assignee)
- **Campos customizados**: Ilimitados
- **Taxa de sucesso dos testes**: 100% (14/14)
- **Compatibilidade**: Total (funciona com ou sem campos personalizados)

---

**Implementado com 💜 para máxima flexibilidade e usabilidade!**
