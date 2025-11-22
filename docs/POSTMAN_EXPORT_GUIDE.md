# 📮 Guia: Exportação para Postman Collection

## 📋 O que é a Exportação Postman?

A **Exportação Postman** permite que você baixe todos os seus cenários de teste em formato **JSON**, pronto para ser importado no **Postman**. Cada cenário vira uma requisição HTTP que você pode usar para testar APIs.

### 🎯 Para que serve?

- **Testes de API**: Transformar cenários de teste em requisições HTTP
- **Documentação de API**: Usar os cenários como exemplos de uso da API
- **Automação**: Criar testes automatizados de API no Postman
- **Colaboração**: Compartilhar cenários com desenvolvedores backend

---

## 🤔 O que é Postman?

**Postman** é uma ferramenta muito popular para testar APIs (Application Programming Interfaces). Com ele, você pode:
- Enviar requisições HTTP (GET, POST, PUT, DELETE, etc.)
- Ver as respostas da API
- Criar coleções de testes
- Automatizar testes de API

**Exemplo de uso**: Testar se a API de login está funcionando corretamente.

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
   - 🥒 Cucumber (.zip)
   - 📮 **Postman (.json)** ← Este é o que você quer!

### Passo 2: Clique para Baixar

1. Clique no botão **"📮 Postman (.json)"**
2. O navegador iniciará o download automaticamente
3. O arquivo será salvo com um nome como: `user_story_postman.json`

### Passo 3: Abra o Postman

1. Se você ainda não tem o Postman instalado:
   - Acesse https://www.postman.com/downloads/
   - Baixe e instale a versão gratuita
   - Crie uma conta (é grátis)

2. Abra o Postman no seu computador

### Passo 4: Importe a Collection

1. No Postman, clique em **"Import"** (canto superior esquerdo)
2. Clique em **"Upload Files"** ou arraste o arquivo `.json` baixado
3. Clique em **"Import"** para confirmar
4. Uma nova **Collection** aparecerá na barra lateral esquerda

### Passo 5: Explore os Cenários

1. Na barra lateral, expanda a Collection importada
2. Você verá uma lista de **requests** (requisições)
3. Cada request corresponde a um cenário de teste do QA Oráculo

---

## 📂 Estrutura da Collection

A Collection importada tem a seguinte estrutura:

```
📁 QA Oráculo - Test Scenarios
  📄 Login com credenciais válidas
  📄 Login com senha incorreta
  📄 Recuperação de senha
  📄 ...
```

### Detalhes de Cada Request

Cada request contém:

1. **Nome**: O título do cenário (ex: "Login com credenciais válidas")
2. **Método**: POST (padrão para todos)
3. **URL**: `https://api.exemplo.com/endpoint` (você precisa ajustar)
4. **Body**: Os steps Gherkin do cenário em formato JSON

**Exemplo de Body**:
```json
{
  "cenario": "Login com credenciais válidas",
  "steps": {
    "dado": "que o usuário está na página de login",
    "quando": "ele insere credenciais válidas",
    "entao": "ele deve ser redirecionado para o dashboard"
  }
}
```

---

## 🔧 Como Usar no Postman

### Passo 1: Configure a URL Base

1. Clique na **Collection** (não em um request específico)
2. Vá para a aba **"Variables"**
3. Crie uma variável chamada `base_url`
4. Defina o valor como a URL da sua API (ex: `https://api.seuapp.com`)

### Passo 2: Ajuste os Endpoints

Para cada request:

1. Clique no request
2. Na URL, substitua `https://api.exemplo.com/endpoint` pela URL real
3. Exemplo: `{{base_url}}/auth/login` (usa a variável criada)

### Passo 3: Ajuste o Body

1. Vá para a aba **"Body"**
2. Ajuste o JSON para o formato esperado pela sua API
3. Exemplo:
   ```json
   {
     "email": "usuario@exemplo.com",
     "password": "senha123"
   }
   ```

### Passo 4: Execute o Request

1. Clique no botão **"Send"**
2. Veja a resposta da API na parte inferior
3. Verifique se o status é 200 (sucesso) ou outro esperado

---

## 💡 Exemplo Prático

### Cenário: Testar API de Login

**Situação**: Você tem uma User Story de "Login de Usuário" e quer testar a API de login.

**Passo a passo**:

1. **No QA Oráculo**:
   - Gere cenários de teste para a User Story de login
   - Clique em "📮 Postman (.json)"
   - Baixe o arquivo

2. **No Postman**:
   - Importe o arquivo JSON
   - Você terá requests como:
     - "Login com credenciais válidas"
     - "Login com senha incorreta"
     - "Login com email inválido"

3. **Configure os Requests**:
   - Request "Login com credenciais válidas":
     - URL: `{{base_url}}/auth/login`
     - Body:
       ```json
       {
         "email": "usuario@teste.com",
         "password": "senha123"
       }
       ```
   
4. **Execute e Valide**:
   - Clique em "Send"
   - Verifique se a resposta é 200 OK
   - Verifique se retorna um token de autenticação

**Benefício**: Você tem testes de API prontos em minutos, em vez de criar manualmente!

---

## ❓ Perguntas Frequentes

### 1. Quantos requests são criados?
**Um request para cada cenário**. Se você tem 8 cenários no plano de testes, terá 8 requests na Collection.

### 2. Preciso ajustar os requests depois de importar?
**Sim**. O QA Oráculo gera a estrutura base, mas você precisa:
- Definir as URLs corretas
- Ajustar o body para o formato da sua API
- Adicionar headers se necessário (ex: Authorization)

### 3. Posso usar para APIs REST?
**Sim!** A exportação é ideal para APIs REST. Você pode ajustar o método HTTP (GET, POST, PUT, DELETE) conforme necessário.

### 4. O que é uma Collection no Postman?
Uma **Collection** é um grupo de requests relacionados. É como uma pasta que organiza seus testes de API.

### 5. Preciso pagar pelo Postman?
**Não**. A versão gratuita do Postman é suficiente para usar as Collections exportadas.

---

## 🎓 Dicas para Iniciantes

### Dica 1: Use Variáveis
Crie variáveis para valores que se repetem:
- `{{base_url}}`: URL base da API
- `{{token}}`: Token de autenticação
- `{{user_id}}`: ID do usuário de teste

### Dica 2: Organize por Pastas
Se você tem muitos requests, crie pastas dentro da Collection:
```
📁 QA Oráculo - Test Scenarios
  📁 Autenticação
    📄 Login válido
    📄 Login inválido
  📁 Usuários
    📄 Criar usuário
    📄 Atualizar usuário
```

### Dica 3: Adicione Testes Automatizados
No Postman, você pode adicionar scripts para validar automaticamente as respostas:

```javascript
// Na aba "Tests" do request
pm.test("Status code é 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Retorna um token", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.token).to.exist;
});
```

### Dica 4: Compartilhe com o Time
Exporte a Collection ajustada e compartilhe com desenvolvedores e outros QAs. Assim todos usam os mesmos testes!

---

## 🔧 Solução de Problemas

### Problema: "Botão Postman está desabilitado"
**Solução**: Você precisa ter cenários gerados. Gere um plano de testes primeiro.

### Problema: "Erro ao importar no Postman"
**Solução**:
1. Verifique se o arquivo tem extensão `.json`
2. Abra o arquivo em um editor de texto e confirme que é um JSON válido
3. Tente importar novamente usando "Upload Files" em vez de arrastar

### Problema: "Requests não funcionam"
**Solução**:
1. Verifique se a URL está correta
2. Confirme que a API está rodando (teste com curl ou navegador)
3. Verifique se você precisa de autenticação (token, API key, etc.)
4. Confira se o body está no formato esperado pela API

### Problema: "Collection está vazia"
**Solução**:
1. Verifique se você tinha cenários no plano de testes
2. Baixe o arquivo novamente
3. Tente importar em outro workspace do Postman

---

## 📚 Recursos Adicionais

### Aprenda Mais sobre Postman
- [Documentação oficial do Postman](https://learning.postman.com/)
- [Tutorial de Postman em Português](https://www.youtube.com/results?search_query=postman+tutorial+português)
- [Postman Learning Center](https://learning.postman.com/docs/getting-started/introduction/)

### Aprenda Mais sobre APIs
- [O que é uma API REST?](https://www.redhat.com/pt-br/topics/api/what-is-a-rest-api)
- [HTTP Methods (GET, POST, etc.)](https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Methods)

---

## 📚 Próximos Passos

Agora que você sabe exportar para Postman, explore:

- [Exportação Cucumber](CUCUMBER_EXPORT_GUIDE.md) - Exporte para automação com Cucumber
- [Exportação em Lote](BATCH_EXPORT_GUIDE.md) - Exporte múltiplas análises
- [Comparação de Análises](COMPARISON_GUIDE.md) - Compare versões de análises

---

**💡 Lembre-se**: Postman é essencial para **testes de API**. Use a exportação do QA Oráculo para criar testes rapidamente e com qualidade!
