# 📘 Guia de Exportação para Xray (Jira Test Management)

## 📌 Visão Geral

O QA Oráculo agora suporta exportação de cenários de teste no formato CSV compatível com **Xray Test Case Importer**. Esta funcionalidade permite que você importe cenários Gherkin gerados automaticamente diretamente para o Jira Xray.

## 🎯 Formato do Arquivo CSV

O arquivo CSV gerado segue a especificação oficial do Xray com as seguintes colunas:

| Coluna | Descrição | Origem no QA Oráculo |
|--------|-----------|---------------------|
| **Summary** | Nome da atividade de teste | Campo `titulo` do cenário |
| **Description** | Descrição do teste | Combinação de `criterio_de_aceitacao_relacionado` e `justificativa_acessibilidade` |
| **Test_Repository_Folder** | Diretório no Xray onde o teste será salvo | Configurado pelo usuário na interface |
| **Test_Type** | Tipo de teste | Sempre "Cucumber" para cenários Gherkin |
| **Gherkin_Definition** | Cenário de teste completo | Campo `cenario` do caso de teste |

## 🚀 Como Usar

### 1. Gerar Plano de Testes no QA Oráculo

1. Insira sua User Story
2. Analise e refine os critérios de aceite
3. Gere o Plano de Testes completo

### 2. Configurar Exportação Xray

Na seção **"Opções de Exportação para Ferramentas Externas"**, expanda o accordion e:

1. Role até a seção **"Xray (Jira Test Management)"**
2. Preencha o campo **"Test Repository Folder"** com o nome do diretório no Xray
   - Exemplo: `TED`, `Pagamentos`, `Login`
   - ⚠️ **Importante**: Este diretório **deve existir previamente** no Xray

### 3. Fazer Download do CSV

1. Clique no botão **"🧪 Xray (.csv)"** na seção de Downloads
2. O arquivo será baixado com o nome baseado na User Story + timestamp
3. O arquivo estará pronto para importação no Xray

## 📋 Exemplo de Arquivo Gerado

```csv
"Summary","Description","Test_Repository_Folder","Test_Type","Gherkin_Definition"
"Solicitar TED sem enviar dados obrigatórios","Critério de Aceitação: Sistema deve validar campos obrigatórios | Justificativa de Acessibilidade: Mensagens de erro acessíveis via leitores de tela","TED","Cucumber","Given que possuo conta PJ
When solicito uma transferencia sem enviar <dados>
Then devo obter mensagem de erro e status code 400
Examples:
| dados           |
| data_pagamento  |
| valor_pagamento |"
```

## 🔧 Importar no Xray

### Pré-requisitos

- ✅ O diretório especificado em `Test_Repository_Folder` deve existir no Xray
- ✅ Você deve ter permissões para importar testes no projeto
- ✅ O arquivo CSV deve estar codificado em UTF-8

### Passos de Importação

1. **Acesse o Xray Test Case Importer**
   - No Jira, vá em **Apps** → **Xray** → **Test Case Importer**

2. **Selecione o Formato CSV**
   - Na tela inicial, selecione a opção **CSV**

3. **Faça Upload do Arquivo**
   - Clique em "Escolher arquivo" e selecione o CSV exportado
   - Clique em **"Next"**

4. **Selecione o Projeto**
   - Escolha o projeto/squad de destino
   - Clique em **"Next"**

5. **Mapeie os Campos**
   - O Xray detectará automaticamente os campos
   - Confirme o mapeamento:
     - `Summary` → Resumo
     - `Description` → Descrição
     - `Test_Type` → Test Type
     - `Gherkin_Definition` → Gherkin Definition
     - `Test_Repository_Folder` → Test Repository Folder

6. **Inicie a Importação**
   - Clique em **"Import"**
   - Aguarde a conclusão do processo
   - Verifique os testes no Testing Board

## ⚠️ Considerações Importantes

### Validações Realizadas

✅ Todos os campos são validados antes da exportação  
✅ Cenários Gherkin são preservados com quebras de linha  
✅ Codificação UTF-8 garante suporte a caracteres especiais  
✅ Campos vazios recebem valores padrão apropriados  

### Limitações Conhecidas

- O diretório em `Test_Repository_Folder` **deve ser criado previamente** no Xray
- Não é possível criar diretórios durante a importação
- A importação pode falhar se o formato Gherkin contiver erros de sintaxe

## 🐛 Resolução de Problemas

| Problema | Causa Provável | Solução |
|----------|---------------|---------|
| Erro: "Test_Repository_Folder não existe" | Diretório não foi criado no Xray | Crie o diretório no Xray antes da importação |
| Erro de encoding | Arquivo não está em UTF-8 | O QA Oráculo gera em UTF-8 automaticamente - verifique se o arquivo não foi modificado |
| Cenário não importado corretamente | Sintaxe Gherkin inválida | Revise o cenário no QA Oráculo antes de exportar |
| Botão de download desabilitado | Campo `Test_Repository_Folder` não foi preenchido | Preencha o campo nas opções de exportação |

## 📚 Referências

- [Documentação Oficial do Xray](https://docs.getxray.app/)
- [Xray Test Case Importer Guide](https://docs.getxray.app/display/XRAY/Importing+Tests)
- [Especificação Gherkin](https://cucumber.io/docs/gherkin/)

## 🎉 Benefícios da Integração

✅ **Economia de tempo**: Importação em lote de cenários  
✅ **Rastreabilidade**: Cenários vinculados aos critérios de aceite  
✅ **Padronização**: Formato Gherkin consistente  
✅ **Acessibilidade**: Justificativas de acessibilidade incluídas na descrição  
✅ **Automação**: Reduz trabalho manual e erros de digitação  

---

**Desenvolvido com 💜 para a comunidade QA**
