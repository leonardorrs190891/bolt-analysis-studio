# Report de Validação v2 — Design (formatação + erro claro + MSD reproduzível)

**Data:** 2026-07-10 · **Status:** aprovado pelo professor (erro = resíduo assinado)

## 1. Pedido (verbatim do professor)

"Melhore a formatação do report. Gostaria que ficasse mais claro o erro entre
o artigo e nosso software. Gostaria que se mostrasse o modelo MSD (igual se
prepara) com elementos e a descrição de variáveis, para que apenas lendo o
relatório possa se refazer o modelo no software."

## 2. Requisitos

1. **Erro claro** — painel dedicado de **resíduo assinado** (modelo − artigo
   vs ciclos, linha zero, banda sombreada ±MAE) sob o gráfico principal;
   métricas interpretadas em texto ("MAE 0.089 = em média o modelo erra 8,9
   pontos percentuais de F/F₀"; erro máximo com o ciclo; erro no ponto
   final; direção dominante sobre/sub-predição); **MAE por estágio**
   (I assentamento / II perda principal / III cauda — janelas 0-10% / 10-70% /
   70-100% dos ciclos) quando há curva completa.
2. **Modelo MSD reproduzível** — seção gerada do modelo REAL
   (`gui_bridge.build_case_model(rec)`, o mesmo do "Abrir no Model/Run"):
   - diagrama SVG da cadeia de elementos na ordem (caixas tipo+nome+id,
     conexões série), como no builder;
   - tabela de elementos: id, tipo, nome, k [N/m], c [N·s/m], m [kg],
     material, preload % yield;
   - tabela de carregamento global (campos do PropertyInspector: tipo, modo
     de controle, F₀, amplitude δ/F_amp, frequência, n ciclos, µ);
   - **glossário de variáveis** em PT (símbolo → descrição + unidade) cobrindo
     TODO símbolo exibido no report (geometria, elementos, carregamento e
     constantes V2 dos overrides);
   - passo-a-passo "Para refazer no software" (via módulo Validation →
     Abrir no Model/Run, e manualmente via wizard + inspector).
   - Família `other` (sem carregamento parametrizado): a seção degrada para a
     descrição textual atual + aviso.
3. **Formatação** — seções numeradas 1-6 (condições · modelo MSD · resultado
   e erro · decomposição · constantes · caveats), cabeçalho com resumo
   executivo (MAE grande + família/classe + veredito em uma linha), tabelas
   com `<thead>`, impressão-amigável (`@media print`: fundo claro, sem
   quebras dentro de tabelas/plots).

## 3. Arquitetura

Tudo em `validation/report_html.py` (novas funções privadas: `_svg_residual`,
`_msd_section(rec)`, `_glossary_rows(used_symbols)`, `_stage_maes(cd, rd, pred)`)
+ reuso de `gui_bridge.build_case_model` (lazy import p/ manter o gerador
utilizável sem GUI — fallback textual se o import falhar). O runner **não
muda** (o resíduo é recomputado dos pontos `data_points(rec)` vs
`result.cycles/ratio` — mesmos dados já presentes). Regenerar os 128 +
atualizar o artifact do liu2025 na entrega.

## 4. Testes

- Resíduo: HTML contém o painel (marcador `residual`), banda ±MAE e texto de
  interpretação; sinal correto num resultado sintético (modelo acima do dado
  → resíduo positivo).
- MSD: tabela com ≥1 elemento GROUND + k numérico; carregamento com F₀ do
  caso; glossário cobre os símbolos exibidos (spot-check k_b, C_creep, δ);
  família `other` degrada sem exceção.
- Formatação: seções numeradas presentes; `@media print` no CSS; 128 reports
  gerados sem exceção (teste existente continua).

## 5. Fora de escopo

Mudanças no runner/store/GUI; master report (ganha só o que herda do CSS);
imagens raster (tudo SVG inline, self-contained).
