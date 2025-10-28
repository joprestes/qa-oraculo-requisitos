# Guia de Acessibilidade

Este documento apresenta as diretrizes de acessibilidade adotadas no projeto **QA Oráculo de Requisitos**. O objetivo é garantir que a aplicação seja utilizável por todas as pessoas, independentemente de suas capacidades ou dispositivos assistivos utilizados.

## Objetivos

- Promover a inclusão digital ao oferecer uma experiência consistente para usuários com diferentes necessidades.
- Atender aos requisitos das [Diretrizes de Acessibilidade para Conteúdo Web (WCAG) 2.1](https://www.w3.org/TR/WCAG21/), priorizando os níveis A e AA.
- Estabelecer um processo contínuo de melhoria, com revisões periódicas e automação sempre que possível.

## Princípios Fundamentais

As diretrizes seguem os quatro princípios da WCAG:

1. **Perceptível** – As informações e componentes da interface devem ser apresentados de forma que os usuários possam percebê-los.
2. **Operável** – Componentes e navegação devem ser utilizáveis por teclado e outras tecnologias assistivas.
3. **Compreensível** – O conteúdo deve ser legível e a interface deve se comportar de maneira previsível.
4. **Robusto** – O conteúdo deve ser compatível com diversos agentes de usuário, incluindo leitores de tela e navegadores assistivos.

## Diretrizes Gerais

### Estrutura Semântica

- Utilizar elementos HTML semânticos (por exemplo, `main`, `header`, `nav`, `section`, `article`, `footer`).
- Manter hierarquia correta de títulos (`h1` a `h6`).
- Garantir que listas e tabelas sejam construídas com elementos apropriados (`ul`, `ol`, `table`, `thead`, `tbody`, `th`).

### Navegação e Foco

- Garantir que toda a interface seja operável apenas com teclado (tabulação, setas e atalhos).
- Utilizar indicadores de foco visíveis e com contraste adequado.
- Evitar armadilhas de teclado (componentes que prendam o foco).
- Fornecer "skip links" ou mecanismos equivalentes para saltar conteúdos repetitivos.

### Conteúdo Não Textual

- Oferecer texto alternativo significativo em imagens e ícones (`alt`).
- Fornecer descrições ou legendas para vídeos e transcrições para áudios.
- Garantir que elementos decorativos sejam ocultos de leitores de tela (`aria-hidden="true"`).

### Contraste e Cores

- Respeitar contraste mínimo de 4.5:1 para texto normal e 3:1 para títulos grandes.
- Não utilizar exclusivamente cores para transmitir informações; combinar com ícones, padrões ou texto.
- Oferecer temas de alto contraste quando aplicável.

### Formularios e Componentes Interativos

- Associar rótulos (`label`) aos campos de formulário (`for` / `id`).
- Fornecer instruções claras, mensagens de erro e validações acessíveis.
- Utilizar `aria-live` em mensagens dinâmicas importantes.
- Garantir que componentes personalizados exponham papéis (`role`) e atributos `aria` adequados.

### Conteúdo Dinâmico

- Evitar atualizações automáticas que possam confundir o usuário.
- Garantir que avisos, modais e diálogos tenham foco inicial adequado e possam ser fechados por teclado.
- Utilizar `aria-live` ou `role="status"` para comunicar alterações em tempo real.

## Processo de Desenvolvimento

1. **Planejamento**
   - Definir requisitos de acessibilidade desde a concepção das funcionalidades.
   - Incluir critérios de aceitação relacionados à acessibilidade.

2. **Design**
   - Manter contraste adequado nas paletas de cores.
   - Garantir espaçamento suficiente entre elementos e tamanho mínimo de 44px em áreas clicáveis.
   - Validar fluxos com usuários representando diferentes perfis quando possível.

3. **Implementação**
   - Priorizar componentes reutilizáveis já validados em acessibilidade.
   - Revisar atributos `aria`, ordem de leitura e comportamento de foco.
   - Documentar exceções justificadas e planejar correções futuras.

4. **Testes**
   - Executar testes automatizados quando disponíveis (por exemplo, `axe`, `pa11y`, `lighthouse`).
   - Realizar testes manuais com teclado, leitores de tela (NVDA, VoiceOver) e ferramentas de contraste.
   - Registrar resultados e abrir issues para não conformidades.

## Checklist Rápido

- [ ] Conteúdo acessível via teclado
- [ ] Ordem de tabulação lógica
- [ ] Focus visible
- [ ] Texto alternativo em mídias
- [ ] Contraste mínimo atendido
- [ ] Formularios com labels associados
- [ ] Mensagens de erro compreensíveis
- [ ] Uso correto de landmarks e semântica
- [ ] Componentes dinâmicos com `aria-live` quando necessário
- [ ] Testes com ferramentas automatizadas e manuais realizados

## Ferramentas Recomendadas

- [Deque axe DevTools](https://www.deque.com/axe/devtools/)
- [Pa11y](https://pa11y.org/)
- [Wave Evaluation Tool](https://wave.webaim.org/)
- [Color Contrast Analyzer](https://www.tpgi.com/color-contrast-checker/)
- [NVDA Screen Reader](https://www.nvaccess.org/)
- [VoiceOver (macOS/iOS)](https://www.apple.com/voiceover/info/guide/_1124.html)

## Manutenção Contínua

- Revisar periodicamente o código e o design à medida que novas funcionalidades são adicionadas.
- Manter a equipe atualizada com treinamentos e recursos sobre acessibilidade.
- Monitorar feedback de usuários e priorizar correções relacionadas à acessibilidade.

## Referências

- [WCAG 2.1](https://www.w3.org/TR/WCAG21/)
- [Material Design Accessibility](https://material.io/design/usability/accessibility.html)
- [WAI-ARIA Authoring Practices Guide](https://www.w3.org/TR/wai-aria-practices/)

