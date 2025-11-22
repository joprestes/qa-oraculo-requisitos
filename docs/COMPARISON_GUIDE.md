# 🔄 Guia: Comparação entre Análises

## 📋 O que é a Comparação de Análises?

A **Comparação de Análises** permite que você compare duas análises de User Stories lado a lado, visualizando exatamente o que mudou entre elas. É como usar um "antes e depois" para entender a evolução de uma User Story.

### 🎯 Para que serve?

- **Acompanhar evolução**: Ver como uma User Story foi refinada ao longo do tempo
- **Identificar mudanças**: Descobrir rapidamente o que foi adicionado, removido ou alterado
- **Revisar refinamentos**: Validar se as alterações feitas melhoraram a qualidade da análise
- **Documentar decisões**: Registrar por que certas mudanças foram feitas

---

## 🚀 Como Usar (Passo a Passo)

### Passo 1: Acesse o Histórico

1. Abra o QA Oráculo no navegador
2. No menu lateral (sidebar), clique em **"📖 Histórico"**
3. Você verá uma lista de todas as análises já realizadas

### Passo 2: Ative o Modo de Comparação

1. Na página de Histórico, procure o checkbox **"🔄 Modo de Comparação"**
2. Clique nele para ativar o modo de comparação
3. Uma mensagem azul aparecerá: *"Selecione exatamente 2 análises abaixo para comparar"*

### Passo 3: Selecione as Análises

1. Ao lado de cada análise no histórico, aparecerá um checkbox **"Comparar #ID"**
2. Clique no checkbox da **primeira análise** que você quer comparar
3. Clique no checkbox da **segunda análise** que você quer comparar
4. ⚠️ **Importante**: Você deve selecionar exatamente 2 análises. Se selecionar mais, aparecerá um aviso

### Passo 4: Visualize a Comparação

Assim que você selecionar 2 análises, a comparação aparecerá automaticamente abaixo:

#### 📊 Visualização Lado a Lado

A tela será dividida em duas colunas:

- **Coluna Esquerda**: Análise #1 (primeira selecionada)
- **Coluna Direita**: Análise #2 (segunda selecionada)

Cada coluna mostra:
- 📅 **Data** da análise
- 📝 **User Story** original
- 📄 **Relatório de Análise** gerado pela IA

#### 🔍 Abas de Diferenças (Diff)

Logo abaixo da visualização lado a lado, você verá **abas** para ver as diferenças:

1. **Aba "Diff - User Story"**:
   - Mostra exatamente o que mudou na User Story
   - **Verde**: Texto adicionado
   - **Vermelho**: Texto removido
   - **Amarelo**: Texto modificado

2. **Aba "Diff - Relatório"**:
   - Mostra exatamente o que mudou no Relatório de Análise
   - Mesma lógica de cores (verde = adição, vermelho = remoção)

---

## 💡 Exemplo Prático

### Cenário: Você refiniu uma User Story

**Situação**: Você analisou uma User Story na segunda-feira, recebeu feedback do PO, ajustou a User Story e analisou novamente na quarta-feira.

**Como comparar**:

1. Vá ao Histórico
2. Ative "🔄 Modo de Comparação"
3. Selecione a análise de **segunda-feira** (versão antiga)
4. Selecione a análise de **quarta-feira** (versão nova)
5. Veja lado a lado:
   - O que você mudou na User Story
   - Como a análise da IA mudou com base nas suas alterações

**Benefício**: Você pode documentar e justificar as mudanças feitas, mostrando ao time que a nova versão está mais completa.

---

## ❓ Perguntas Frequentes

### 1. Posso comparar mais de 2 análises?
**Não**. O sistema permite apenas comparar 2 análises por vez. Se você tentar selecionar mais, aparecerá um aviso: *"⚠️ Selecione apenas 2 análises para comparar"*.

### 2. Preciso selecionar análises da mesma User Story?
**Não é obrigatório**, mas faz mais sentido. Você pode comparar análises de User Stories diferentes, mas a comparação será mais útil se forem versões da mesma história.

### 3. Como desativo o Modo de Comparação?
Basta **desmarcar** o checkbox "🔄 Modo de Comparação". A comparação desaparecerá e você voltará à visualização normal do histórico.

### 4. As cores no diff significam o quê?
- 🟢 **Verde**: Texto que foi **adicionado** na segunda análise
- 🔴 **Vermelho**: Texto que foi **removido** (estava na primeira, não está na segunda)
- 🟡 **Amarelo**: Texto que foi **modificado**

### 5. Posso exportar a comparação?
Atualmente, não. A comparação é apenas para visualização. Mas você pode fazer um **print da tela** (screenshot) para documentar.

---

## 🎓 Dicas para Iniciantes

### Dica 1: Use para Aprender
Se você é novo em análise de requisitos, compare análises de User Stories semelhantes para entender padrões e boas práticas.

### Dica 2: Documente Mudanças
Antes de apresentar uma análise refinada ao time, use a comparação para criar uma lista de "o que mudou e por quê".

### Dica 3: Valide com o PO
Mostre a comparação ao Product Owner para validar se as mudanças estão alinhadas com a visão dele.

### Dica 4: Organize seu Histórico
Dê nomes descritivos às suas User Stories para facilitar a identificação na hora de comparar.

---

## 🔧 Solução de Problemas

### Problema: "Não consigo selecionar a segunda análise"
**Solução**: Verifique se você já selecionou 2 análises. Se sim, desmarque uma delas antes de selecionar outra.

### Problema: "A comparação não aparece"
**Solução**: 
1. Confirme que você selecionou **exatamente 2** análises
2. Role a página para baixo - a comparação aparece abaixo da lista de análises
3. Tente desmarcar e marcar novamente as análises

### Problema: "O diff está difícil de ler"
**Solução**: 
1. Aumente o zoom do navegador (Ctrl/Cmd + "+")
2. Use a aba específica (User Story ou Relatório) em vez de tentar ler tudo junto
3. Foque em uma mudança por vez

---

## 📚 Próximos Passos

Agora que você sabe comparar análises, explore outras funcionalidades:

- [Exportação em Lote](BATCH_EXPORT_GUIDE.md) - Exporte múltiplas análises de uma vez
- [Exportação Cucumber](CUCUMBER_EXPORT_GUIDE.md) - Exporte cenários para Cucumber Studio
- [Exportação Postman](POSTMAN_EXPORT_GUIDE.md) - Exporte cenários para Postman

---

**💡 Lembre-se**: A comparação é uma ferramenta poderosa para **aprender** e **melhorar** suas análises. Use-a sempre que refinar uma User Story!
