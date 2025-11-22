# 📊 Guia: Indicadores de Progresso

## 📋 O que são Indicadores de Progresso?

Os **Indicadores de Progresso** são barras visuais que mostram o andamento de operações longas no QA Oráculo. Em vez de apenas ver um "carregando...", você vê exatamente em qual etapa o sistema está e quanto falta para concluir.

### 🎯 Para que servem?

- **Transparência**: Ver exatamente o que está acontecendo
- **Reduzir ansiedade**: Saber que o sistema está funcionando
- **Estimativa de tempo**: Entender quanto tempo falta
- **Feedback visual**: Acompanhar o progresso em tempo real

---

## 🚀 Onde são Usados?

### 1. Exportação em Lote

Quando você exporta múltiplas análises de uma vez, verá:

```
Exportação em lote (1/5)
████████░░░░░░░░░░ 20%
Exportando análise 1/5
```

**Como funciona**:
1. Selecione 2 ou mais análises no histórico
2. Ative "📦 Exportação em Lote"
3. Clique em "📥 Baixar ZIP"
4. Veja a barra de progresso mostrando cada análise sendo exportada

---

## 💡 Exemplo Prático

### Cenário: Exportar 10 Análises

**Antes** (sem indicador):
- Clica em "Baixar ZIP"
- Tela congela
- Não sabe se travou ou está processando
- Espera ansiosamente

**Agora** (com indicador):
- Clica em "Baixar ZIP"
- Vê: "Exportando análise 1/10"
- Barra de progresso: 10%
- Vê: "Exportando análise 2/10"
- Barra de progresso: 20%
- ...
- Vê: "Exportando análise 10/10"
- Barra de progresso: 100%
- Download inicia automaticamente

**Benefício**: Você sabe exatamente o que está acontecendo e quanto tempo falta!

---

## 🎓 Dicas para Iniciantes

### Dica 1: Não Interrompa
Quando vir a barra de progresso, **não feche a aba** ou **recarregue a página**. Deixe o processo terminar.

### Dica 2: Operações Longas
Quanto mais análises você exportar, mais tempo levará. A barra ajuda você a decidir se quer esperar ou fazer outra coisa.

### Dica 3: Progresso Linear
A barra avança de forma linear. Se você tem 10 análises, cada uma representa 10% do progresso.

---

## ❓ Perguntas Frequentes

### 1. A barra travou em 50%, o que fazer?
**Resposta**: Aguarde alguns segundos. Algumas análises podem ter mais dados e demorar mais. Se travar por mais de 2 minutos, recarregue a página.

### 2. Posso fazer outras coisas enquanto a barra carrega?
**Resposta**: Sim, mas **não feche a aba** do QA Oráculo. Você pode abrir outras abas do navegador.

### 3. A barra desapareceu antes de terminar
**Resposta**: Isso pode acontecer se houver um erro. Verifique se apareceu alguma mensagem de erro na tela.

### 4. Quanto tempo leva para exportar?
**Resposta**: Depende da quantidade de análises. Em média:
- 1-5 análises: 5-15 segundos
- 6-10 análises: 15-30 segundos
- 11-20 análises: 30-60 segundos

---

## 🔧 Solução de Problemas

### Problema: Barra não aparece
**Solução**: 
1. Verifique se você selecionou pelo menos 2 análises
2. Recarregue a página e tente novamente
3. Limpe o cache do navegador

### Problema: Barra fica em 0% e não avança
**Solução**:
1. Aguarde 10 segundos
2. Se não avançar, recarregue a página
3. Tente exportar menos análises por vez

### Problema: Erro durante exportação
**Solução**:
1. Veja a mensagem de erro (geralmente em vermelho)
2. Tente exportar as análises uma por uma para identificar qual está com problema
3. Reporte o erro ao time técnico

---

## 🚀 Futuras Melhorias

Em versões futuras, os indicadores de progresso serão adicionados em:
- Análise de User Story
- Geração de Plano de Testes
- Geração de PDF individual

---

**💡 Lembre-se**: Os indicadores de progresso são seus aliados para entender o que está acontecendo. Use-os para ter mais confiança nas operações do sistema!
