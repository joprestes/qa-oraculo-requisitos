# 📦 Guia: Exportação em Lote

## 📋 O que é a Exportação em Lote?

A **Exportação em Lote** permite que você baixe **múltiplas análises de uma só vez** em um único arquivo ZIP. Em vez de exportar análise por análise, você seleciona várias e baixa todas juntas.

### 🎯 Para que serve?

- **Economizar tempo**: Exportar 10 análises em 1 clique em vez de 10 cliques
- **Backup**: Fazer backup de todas as suas análises importantes
- **Compartilhamento**: Enviar várias análises para o time de uma vez
- **Documentação**: Criar um pacote completo de documentação de um projeto

---

## 🚀 Como Usar (Passo a Passo)

### Passo 1: Acesse o Histórico

1. Abra o QA Oráculo no navegador
2. No menu lateral (sidebar), clique em **"📖 Histórico"**
3. Você verá uma lista de todas as análises já realizadas

### Passo 2: Ative o Modo de Exportação em Lote

1. Na página de Histórico, procure o checkbox **"📦 Exportação em Lote"**
2. Clique nele para ativar o modo de exportação
3. Uma mensagem azul aparecerá: *"Selecione uma ou mais análises para exportar em lote (ZIP)"*

### Passo 3: Selecione as Análises

1. Ao lado de cada análise no histórico, aparecerá um checkbox **"Exportar #ID"**
2. Clique nos checkboxes das análises que você quer exportar
3. Você pode selecionar **quantas quiser** (1, 5, 10, 50...)
4. As análises selecionadas ficarão marcadas

### Passo 4: Baixe o ZIP

1. Assim que você selecionar pelo menos 1 análise, aparecerá uma seção:
   ```
   📦 Exportação em Lote (X análises selecionadas)
   ```
2. Clique no botão **"📥 Baixar ZIP com X análises"**
3. O navegador iniciará o download automaticamente
4. O arquivo será salvo com um nome como: `qa_oraculo_batch_20251122_114530.zip`

### Passo 5: Extraia e Use

1. Vá até a pasta de **Downloads** do seu computador
2. Localize o arquivo `.zip` baixado
3. **Clique com botão direito** → **Extrair tudo** (Windows) ou **Descompactar** (Mac)
4. Uma pasta será criada com todos os arquivos dentro

---

## 📂 Estrutura do ZIP

O arquivo ZIP contém **2 arquivos para cada análise** selecionada:

```
📁 qa_oraculo_batch_20251122_114530/
  📄 20251120_analise_1.md
  📄 20251120_analise_1.pdf
  📄 20251121_analise_5.md
  📄 20251121_analise_5.pdf
  📄 20251122_analise_10.md
  📄 20251122_analise_10.pdf
```

### Formato dos Nomes de Arquivo

Cada arquivo segue o padrão:
```
{DATA}_analise_{ID}.{EXTENSÃO}
```

**Exemplo**: `20251122_analise_10.md`
- `20251122`: Data da análise (22 de novembro de 2025)
- `analise`: Palavra fixa
- `10`: ID da análise no banco de dados
- `.md` ou `.pdf`: Extensão do arquivo

### Conteúdo dos Arquivos

Cada par de arquivos (`.md` e `.pdf`) contém:

1. **Arquivo Markdown (.md)**:
   - User Story original
   - Relatório de Análise completo
   - Plano de Testes (se gerado)
   - Cenários Gherkin (se gerados)

2. **Arquivo PDF (.pdf)**:
   - Mesma informação do `.md`, mas em formato PDF
   - Pronto para impressão ou apresentação

---

## 💡 Exemplo Prático

### Cenário: Backup Semanal

**Situação**: Toda sexta-feira, você quer fazer backup de todas as análises da semana.

**Passo a passo**:

1. **Segunda-feira**: Você analisa 3 User Stories
2. **Quarta-feira**: Você analisa mais 2 User Stories
3. **Sexta-feira**: Hora do backup!

**Como fazer**:

1. Vá ao Histórico
2. Ative "📦 Exportação em Lote"
3. Selecione as 5 análises da semana
4. Clique em "📥 Baixar ZIP com 5 análises"
5. Salve o ZIP em uma pasta de backup (ex: `Backups/Semana_47_2025/`)

**Benefício**: Você tem um backup completo da semana em 30 segundos!

---

### Cenário: Apresentação para o Cliente

**Situação**: Você precisa apresentar todas as análises de um projeto para o cliente.

**Passo a passo**:

1. Vá ao Histórico
2. Ative "📦 Exportação em Lote"
3. Selecione todas as análises relacionadas ao projeto (ex: 12 análises)
4. Baixe o ZIP
5. Extraia e organize os PDFs em uma pasta
6. Compartilhe a pasta com o cliente

**Benefício**: Cliente recebe documentação completa e profissional em minutos!

---

## ❓ Perguntas Frequentes

### 1. Quantas análises posso exportar de uma vez?
**Não há limite**. Você pode exportar 1, 10, 50, 100... quantas quiser. Mas lembre-se: quanto mais análises, maior o arquivo ZIP.

### 2. O que acontece se eu selecionar muitas análises?
O download pode demorar um pouco mais, mas funcionará. Se você selecionar 100 análises, o ZIP pode ter vários MB de tamanho.

### 3. Posso exportar apenas Markdown ou apenas PDF?
**Não**. A exportação em lote sempre gera **ambos** (`.md` e `.pdf`) para cada análise. Mas você pode deletar os que não quiser depois de extrair.

### 4. As análises precisam ser da mesma User Story?
**Não**. Você pode misturar análises de User Stories diferentes. A exportação em lote não se importa com isso.

### 5. Como desmarco uma análise selecionada?
Basta clicar novamente no checkbox **"Exportar #ID"** da análise. Ela será desmarcada.

### 6. O que significa o número no nome do arquivo ZIP?
É um **timestamp** (carimbo de data/hora) no formato `AAAAMMDD_HHMMSS`:
- `20251122`: 22 de novembro de 2025
- `114530`: 11:45:30 (hora, minuto, segundo)

Isso garante que cada exportação tenha um nome único.

---

## 🎓 Dicas para Iniciantes

### Dica 1: Organize por Projeto
Crie pastas no seu computador para cada projeto:
```
📁 Projetos/
  📁 Projeto_A/
    📁 Backups/
      📄 qa_oraculo_batch_20251115.zip
      📄 qa_oraculo_batch_20251122.zip
  📁 Projeto_B/
    📁 Backups/
      📄 qa_oraculo_batch_20251120.zip
```

### Dica 2: Faça Backups Regulares
Estabeleça uma rotina:
- **Diária**: Se você faz muitas análises
- **Semanal**: Para projetos médios
- **Mensal**: Para projetos pequenos

### Dica 3: Use Controle de Versão
Se você usa Git, adicione os arquivos `.md` ao repositório. Assim você tem histórico de mudanças!

### Dica 4: Compartilhe com Sabedoria
Antes de compartilhar o ZIP com alguém:
1. Extraia e revise os arquivos
2. Remova análises que não são relevantes
3. Crie um ZIP novo apenas com o necessário

### Dica 5: Nomeie os Backups
Renomeie o ZIP para algo mais descritivo:
- ❌ `qa_oraculo_batch_20251122_114530.zip`
- ✅ `Projeto_Login_Semana47_2025.zip`

---

## 🔧 Solução de Problemas

### Problema: "Botão de download não aparece"
**Solução**: Você precisa selecionar pelo menos 1 análise. Marque um checkbox "Exportar #ID".

### Problema: "Download falha ou arquivo está corrompido"
**Solução**:
1. Tente com menos análises (ex: 5 em vez de 50)
2. Verifique sua conexão com a internet
3. Tente em outro navegador (Chrome, Firefox, Edge)
4. Limpe o cache do navegador

### Problema: "ZIP está vazio ou faltam arquivos"
**Solução**:
1. Verifique se as análises selecionadas têm conteúdo (User Story e Relatório)
2. Tente exportar uma análise por vez para identificar qual está com problema
3. Recarregue a página e tente novamente

### Problema: "Não consigo extrair o ZIP"
**Solução**:
1. **Windows**: Use o extrator nativo ou baixe 7-Zip (gratuito)
2. **Mac**: Use o extrator nativo (duplo clique)
3. **Linux**: Use `unzip arquivo.zip` no terminal

### Problema: "Arquivos PDF não abrem"
**Solução**:
1. Instale um leitor de PDF (Adobe Reader, Foxit, etc.)
2. Verifique se o arquivo não está corrompido (tamanho maior que 0 KB)
3. Tente abrir no navegador (arraste o PDF para o Chrome/Firefox)

---

## 🔒 Segurança e Privacidade

### ⚠️ Atenção com Dados Sensíveis

Se suas User Stories contêm informações confidenciais:

1. **Não compartilhe** o ZIP em canais públicos (email pessoal, Slack público, etc.)
2. **Use criptografia**: Crie um ZIP protegido por senha
3. **Delete após uso**: Remova backups antigos que não são mais necessários
4. **Armazene com segurança**: Use serviços seguros (Google Drive com permissões restritas, OneDrive, etc.)

### Como Criar ZIP com Senha (Opcional)

**Windows (7-Zip)**:
1. Clique com botão direito na pasta extraída
2. 7-Zip → Adicionar ao arquivo...
3. Defina uma senha em "Encryption"

**Mac (Terminal)**:
```bash
zip -er arquivo_protegido.zip pasta_extraida/
```

---

## 📚 Próximos Passos

Agora que você sabe fazer exportação em lote, explore:

- [Comparação de Análises](COMPARISON_GUIDE.md) - Compare versões de análises
- [Exportação Cucumber](CUCUMBER_EXPORT_GUIDE.md) - Exporte para Cucumber Studio
- [Exportação Postman](POSTMAN_EXPORT_GUIDE.md) - Exporte para Postman

---

**💡 Lembre-se**: A exportação em lote é perfeita para **backup** e **compartilhamento**. Use-a regularmente para manter suas análises seguras!
