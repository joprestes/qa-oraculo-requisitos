<nav aria-label="Language switcher" style="text-align: right;">
  <a href="README-en.md">🇺🇸 English</a> | 
  <a href="README.md" aria-current="page">🇧🇷 <strong>Português</strong></a>
</nav>

# 🔮 QA Oráculo: Análise de Requisitos com IA

👋 Bem-vindo ao **QA Oráculo**!  
Um assistente de QA sênior movido por IA que ajuda você a transformar User Stories (US) em especificações claras, reduzindo riscos e acelerando o planejamento de testes.  

---

## ✨ Por que usar o QA Oráculo?

- 🔍 **Detecta ambiguidades** em User Stories antes do desenvolvimento  
- ❓ **Sugere perguntas para o PO**, facilitando alinhamento rápido  
- ✅ **Gera critérios de aceite** simples e verificáveis  
- 📝 **Propõe planos de teste interativos** e casos em Gherkin  
- ♿ **Inclui cenários de acessibilidade (A11y)** já na base dos testes  

---

## 🚀 Começando

Pronto para rodar? Siga os 4 passos:

1. **Clone o repositório**  
   ```bash
   git clone https://github.com/seu-nome/qa-oraculo-requisitos.git
   cd qa-oraculo-requisitos
   ```

2. **Execute o setup**  
   - Windows: `setup.bat`  
   - Mac/Linux: `chmod +x setup.sh && ./setup.sh`

3. **Configure sua API Key**  
   Copie `.env.example` → `.env` e adicione sua chave do Google Gemini.

4. **Ative o ambiente virtual**  
   - Windows: `.\.venv\Scripts\activate`  
   - Mac/Linux: `source .venv/bin/activate`

---

## 🛠️ Como Usar

O fluxo é simples:

1. **Rode o script**  
   ```bash
   ./.venv/bin/python app.py
   ```

2. **Etapa 1:** análise da US → ambiguidade, perguntas ao PO e critérios de aceite.  
3. **Etapa 2:** você decide:  
   - Digite `s` → gerar plano de testes + casos Gherkin  
   - Digite `n` → encerrar  

---

## 🧪 Testes

Este projeto utiliza `unittest` para garantir a qualidade do código. Para rodar a suíte de testes:

```bash
./.venv/bin/python -m unittest discover tests/
```

---

## 🤔 Solução de Problemas

1. **zsh: permission denied: ./setup.sh**  
   ➡ Dê permissão de execução ao script:  
   ```bash
   chmod +x setup.sh
   ```

2. **./setup.sh: python: command not found**  
   ➡ No macOS/Linux, use `python3`:  
   ```bash
   ➡ No setup.sh, altere a linha python -m venv .venv para python3 -m venv .venv.
   ```

3. **ModuleNotFoundError**  
   ➡ Ative o ambiente virtual e rode:  
   ```bash
   ./.venv/bin/python main.py
   ```

4. **error: externally-managed-environment**  
   ➡ Instale dependências pelo pip do ambiente:  
   ```bash
   ./.venv/bin/python -m pip install -r requirements.txt
   ```

---

## 🤝 Contribua

Adoramos colaborações!  
- Abra uma *issue* para sugerir melhorias  
- Envie um *PR* para novas funcionalidades  

⭐ Se este projeto te ajudou, não esqueça de dar uma estrela no repositório!

---

📌 Este projeto ainda está em evolução.  
💡 Sua opinião é super importante — contribua, teste e ajude a moldar o futuro do QA Oráculo!


------------------------------------------------------------------------