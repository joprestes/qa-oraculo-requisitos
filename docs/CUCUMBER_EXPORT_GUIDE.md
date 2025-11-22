# 🥒 Guia: Exportação para Cucumber Studio

## 📋 O que é a Exportação Cucumber?

A **Exportação Cucumber** permite que você baixe todos os seus cenários de teste em um formato que pode ser importado diretamente no **Cucumber Studio** (também conhecido como Hiptest). O arquivo gerado é um **ZIP** contendo vários arquivos `.feature`, um para cada cenário.

### 🎯 Para que serve?

- **Integração com Cucumber**: Usar os cenários gerados pelo QA Oráculo no Cucumber Studio
- **Automação de testes**: Preparar cenários para serem automatizados com Cucumber
- **Documentação viva**: Manter os cenários em formato Gherkin padronizado
- **Colaboração**: Compartilhar cenários com desenvolvedores que usam Cucumber

---

## 🤔 O que é Cucumber?

**Cucumber** é uma ferramenta de automação de testes que usa linguagem natural (Gherkin) para descrever cenários de teste. É muito popular em equipes ágeis.

**Exemplo de arquivo .feature**:
```gherkin
# language: pt
Funcionalidade: Login de usuário

Cenário: Login com credenciais válidas
  Dado que o usuário está na página de login
  Quando ele insere email "usuario@exemplo.com"
  E ele insere senha "senha123"
  Então ele deve ser redirecionado para o dashboard
```

---

## 🚀 Como Usar (Passo a Passo)

### Pré-requisito: Gere um Plano de Testes

Antes de exportar, você precisa ter cenários de teste gerados:

1. Insira uma User Story no QA Oráculo
2. Clique em **"Analisar"**
3. Revise a análise
4. Clique em **"Gerar Plano de Testes"**
5. Aguarde os cenários serem gerados

### Passo 1: Localize o Botão de Exportação

1. Role a página até a seção **"Downloads Disponíveis"**
2. Você verá 4 botões na primeira linha:
   - 📝 Relatório (.md)
   - 📄 Relatório (.pdf)
   - 🥒 **Cucumber (.zip)** ← Este é o que você quer!
   - 📮 Postman (.json)

### Passo 2: Clique para Baixar

1. Clique no botão **"🥒 Cucumber (.zip)"**
2. O navegador iniciará o download automaticamente
3. O arquivo será salvo com um nome como: `user_story_cucumber.zip`

### Passo 3: Extraia o ZIP

1. Vá até a pasta de **Downloads** do seu computador
2. Localize o arquivo `.zip` baixado
3. **Clique com botão direito** → **Extrair tudo** (Windows) ou **Descompactar** (Mac)
4. Uma pasta será criada com vários arquivos `.feature` dentro

### Passo 4: Verifique os Arquivos

Dentro da pasta extraída, você encontrará:

```
📁 user_story_cucumber/
  📄 Login_com_credenciais_válidas.feature
  📄 Login_com_senha_incorreta.feature
  📄 Recuperação_de_senha.feature
  📄 ...
```

Cada arquivo `.feature` contém **um cenário de teste** completo.

---

## 📂 Estrutura do Arquivo .feature

Cada arquivo `.feature` gerado tem a seguinte estrutura:

```gherkin
# language: pt
Funcionalidade: [Título do Cenário]

Cenário: [Nome do Cenário]
  Dado [contexto inicial]
  Quando [ação do usuário]
  Então [resultado esperado]
```

### Exemplo Real

Se você tem um cenário chamado **"Login com credenciais válidas"**, o arquivo `Login_com_credenciais_válidas.feature` conterá:

```gherkin
# language: pt
Funcionalidade: Login com credenciais válidas

Cenário: Login com credenciais válidas
  Dado que o usuário está na página de login
  Quando ele insere credenciais válidas
  Então ele deve ser redirecionado para o dashboard
```

---

## 🔧 Como Importar no Cucumber Studio

### Opção 1: Upload Manual

1. Acesse o **Cucumber Studio** (https://cucumber.io/tools/cucumber-studio/)
2. Faça login na sua conta
3. Vá para o seu projeto
4. Clique em **"Import"** ou **"Importar"**
5. Selecione **"Feature files"** ou **"Arquivos .feature"**
6. Faça upload dos arquivos `.feature` extraídos
7. Confirme a importação

### Opção 2: Integração Git (Avançado)

1. Coloque os arquivos `.feature` na pasta `features/` do seu repositório
2. Faça commit e push
3. O Cucumber Studio sincronizará automaticamente (se configurado)

---

## 💡 Exemplo Prático

### Cenário: Você quer automatizar testes de uma User Story

**Situação**: Você analisou uma User Story de "Cadastro de Usuário" e gerou 5 cenários de teste. Agora quer automatizar esses testes usando Cucumber.

**Passo a passo**:

1. **No QA Oráculo**:
   - Gere o plano de testes
   - Clique em "🥒 Cucumber (.zip)"
   - Baixe o arquivo

2. **No seu computador**:
   - Extraia o ZIP
   - Você terá 5 arquivos `.feature`

3. **No Cucumber Studio**:
   - Importe os 5 arquivos
   - Revise e ajuste se necessário
   - Vincule aos steps de automação

4. **No código de automação**:
   - Os desenvolvedores usarão os arquivos `.feature` como base
   - Criarão os "step definitions" (código que executa cada passo)

**Benefício**: Você economiza horas de trabalho manual escrevendo cenários Gherkin!

---

## ❓ Perguntas Frequentes

### 1. Quantos arquivos .feature são gerados?
**Um arquivo para cada cenário**. Se você tem 10 cenários no plano de testes, terá 10 arquivos `.feature` no ZIP.

### 2. Posso editar os arquivos .feature depois de baixar?
**Sim!** Os arquivos `.feature` são arquivos de texto simples. Você pode abri-los com qualquer editor de texto (Notepad, VS Code, etc.) e editar conforme necessário.

### 3. O que significa "# language: pt"?
Isso indica que o arquivo está em **Português**. O Cucumber entenderá palavras como "Dado", "Quando", "Então" em vez de "Given", "When", "Then".

### 4. Os nomes dos arquivos têm caracteres estranhos?
Não. O QA Oráculo **sanitiza** os nomes automaticamente:
- Remove acentos: "Validação" → "Validacao"
- Remove caracteres especiais: "Login #1" → "Login_1"
- Limita o tamanho a 50 caracteres

### 5. Preciso ter conta no Cucumber Studio?
**Não é obrigatório**. Você pode usar os arquivos `.feature` localmente com Cucumber (ferramenta open-source) sem precisar do Cucumber Studio (versão comercial).

---

## 🎓 Dicas para Iniciantes

### Dica 1: Revise Antes de Importar
Antes de importar no Cucumber Studio, abra alguns arquivos `.feature` e revise. Certifique-se de que os cenários fazem sentido.

### Dica 2: Organize por Funcionalidade
Se você tem muitos cenários, crie pastas para organizá-los:
```
📁 features/
  📁 login/
    📄 login_valido.feature
    📄 login_invalido.feature
  📁 cadastro/
    📄 cadastro_sucesso.feature
    📄 cadastro_erro.feature
```

### Dica 3: Use Controle de Versão
Mantenha os arquivos `.feature` no Git. Assim você tem histórico de mudanças e pode colaborar com o time.

### Dica 4: Aprenda Gherkin
Familiarize-se com a sintaxe Gherkin. É simples e poderosa! Recursos:
- [Documentação oficial do Cucumber](https://cucumber.io/docs/gherkin/)
- [Tutorial de Gherkin em Português](https://cucumber.io/docs/gherkin/reference/)

---

## 🔧 Solução de Problemas

### Problema: "Botão Cucumber está desabilitado"
**Solução**: Você precisa ter cenários gerados. Gere um plano de testes primeiro.

### Problema: "Arquivo ZIP está vazio"
**Solução**: 
1. Verifique se você tem cenários na tabela de plano de testes
2. Tente gerar o plano novamente
3. Se o problema persistir, recarregue a página

### Problema: "Cucumber Studio não reconhece os arquivos"
**Solução**:
1. Verifique se os arquivos têm extensão `.feature`
2. Abra um arquivo e confirme que tem a estrutura Gherkin correta
3. Certifique-se de que está importando como "Feature files"

### Problema: "Nomes de arquivo com caracteres estranhos"
**Solução**: Isso não deveria acontecer, mas se acontecer:
1. Renomeie manualmente os arquivos
2. Use apenas letras, números e underscores (_)
3. Evite espaços e acentos

---

## 📚 Próximos Passos

Agora que você sabe exportar para Cucumber, explore:

- [Exportação Postman](POSTMAN_EXPORT_GUIDE.md) - Exporte para testes de API
- [Exportação em Lote](BATCH_EXPORT_GUIDE.md) - Exporte múltiplas análises
- [Comparação de Análises](COMPARISON_GUIDE.md) - Compare versões de análises

---

**💡 Lembre-se**: Cucumber é uma ferramenta poderosa para **automação de testes**. Use a exportação do QA Oráculo para acelerar seu trabalho!
