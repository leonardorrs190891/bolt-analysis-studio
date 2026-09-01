# Report v3 — Profissionalismo e Interatividade — Design

**Data:** 2026-07-10 · **Pedido (professor, verbatim):** "melhore o
profissionalismo nos reports. Quero gráficos interativos, indice nos reports,
mais interatividade e recursos."

## 1. Decisão arquitetural

**JS puro embutido, zero dependência externa.** Os reports devem funcionar em
`file://` (biblioteca local), no artifact (CSP bloqueia CDN) e impressos — e
são 129 arquivos. Logo: um renderer de gráficos próprio (~250 linhas, inline,
uma vez por arquivo), dados embutidos como JSON no HTML. Sem plotly/chart.js.

## 2. Report por caso — features

1. **Índice (TOC)**: navegação lateral fixa (sticky) com as seções 1-6 e
   subseções, realce da seção ativa ao rolar (IntersectionObserver),
   "voltar ao topo". Em telas estreitas/impressão o TOC some.
2. **Gráficos interativos** (renderer inline; os 3 gráficos):
   - *Curva dado vs modelo*: crosshair vertical + tooltip com N, dado, modelo
     e resíduo no ponto mais próximo; legenda clicável (liga/desliga séries);
     **zoom por arrasto** no eixo x + duplo-clique para resetar.
   - *Resíduo assinado*: mesmo tooltip/zoom, banda ±MAE preservada.
   - *Decomposição empilhada*: hover mostra o valor de CADA mecanismo no
     ciclo apontado (+ total).
   - Impressão/no-JS: o renderer roda no load e injeta SVG no DOM (imprime
     normal); `<noscript>` mostra aviso e a tabela de dados continua legível
     nas seções.
3. **Recursos**:
   - Botão **"Baixar dados (CSV)"** por gráfico (data URI: ciclos, dado,
     modelo, resíduo; decomposição por mecanismo).
   - Botão **"Imprimir/PDF"** no cabeçalho.
   - **Seções colapsáveis**: clique no título h2 recolhe/expande (estado
     inicial: tudo aberto; impressão expande tudo).
   - Barra superior fixa com: nome do caso, MAE, toggle de tema (existente),
     imprimir.

## 3. Documento mestre — features

- **Busca/filtro** instantânea por nome de caso/fonte (input no topo).
- **Ordenação clicável** nas colunas das tabelas (caso/família/classe/MAE).
- **Chips de resumo** no topo (nº casos, MAE médio/mediana, nº no piso,
  nº erros) — já computados, viram elementos visuais.
- TOC de fontes (âncoras).

## 4. Implementação

Tudo em `validation/report_html.py`: `_CHART_JS` (renderer único: tipos
`lines` e `stack`), `_PAGE_JS` (TOC ativo, colapso, imprimir), gráficos viram
`<div class="chart" data-chart="{json}">` (JSON com séries/cores/labels;
escapado com `html.escape`), TOC server-side (nav com as seções), CSS novo
(barra fixa, TOC sticky, tooltip). Master: `_MASTER_JS` (filtro + sort).
Estáticos `_svg_curves`/`_svg_residual`/`_svg_decomp` são REMOVIDOS (o
renderer os substitui; o fechamento decomposição==1−ratio continua testado no
runner). Regenerar os 129 + artifact.

## 5. Testes

Report contém: `data-chart` com JSON parseável (séries dado/modelo; stack com
mecanismos), `_CHART_JS` presente 1x, nav TOC com 6 âncoras, botão CSV,
`<noscript>`; master contém input de filtro + `_MASTER_JS` + chips. Colapso/
zoom/tooltip são JS de browser — verificação manual (headless não roda JS);
o teste garante presença e dados corretos.

## 6. Fora de escopo

Zoom no eixo y; comparação lado-a-lado de casos; export PNG (usuário usa
print/PDF); rodar JS em teste (sem browser headless no ambiente).
