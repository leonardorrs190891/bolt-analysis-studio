# Pacote `validation` — Status (Plano A CONCLUÍDO)

**Data:** 2026-07-10 · **Plano:** `2026-07-10-validation-package-core.md` ·
**Spec:** `2026-07-10-validation-case-reports-design.md` · **Modo:** inline

## O que foi entregue

Todos os **128 casos de validação documentados e consultáveis**: registry
unificado, runner canônico com **decomposição por mecanismo** (pedido do
professor), cache com fingerprint, reports HTML individuais + documento
mestre, CLI, e o menu V1 "Validation Gallery" gerando via pacote.

| Módulo | Responsabilidade | Testes |
|---|---|---|
| `validation/inputs.py` | Port com paridade de `library_common` (ISO/VDI/geometria/constantes congeladas) + `inputs_for` estendido às fontes axiais + fallback não-métrico (UFU 3/4" UNC) | 6 |
| `validation/case_registry.py` | `CaseRecord` ×128: classe (`full_curve` 120 / `final_ratio` 8), família (103 tr / 13 ax / 6 creep / 6 other), caveats, galeria (78/82), notas de aparato | 4 |
| `validation/runner.py` | `simulate_case`: packs LEGACY/PACK + configs adotadas (shim de tuners legados) + métrica na convenção da campanha; decomposição cumulativa exata (soma == 1−F/F₀) | 5 |
| `validation/store.py` | Cache JSON atômico + staleness por fingerprint + seed da galeria | 2 |
| `validation/report_html.py` | Report por caso (condições de contorno, MSD, curvas, erros, **decomposição empilhada**, constantes com proveniência, caveats) + mestre com pisos e coluna "campanha" | 4+2 |
| `validation/report.py` | CLI `--all/--case/--resume/--cap/--store` com save incremental; `ensure_reports` p/ o menu V1 | (cli) |

**23 testes do pacote + 38 de regressão de domínio, verdes.**
Artefatos: `New_Theory/validation_html/reports/*.html` (128) +
`validation_report.html`; store canônico em
`Models/CALIBRATION_AND_VALIDATION/validation_store.json`.

## Números do batch real (2026-07-10, engine `cfa2ccce7d65`)

- **122/128 simulados ok**; 6 erros honestos (Sandia modal — família `other`,
  carregamento sem proveniência no runner v1).
- **114 com MAE** (8 built-in legados só têm ratio final — comparação pontual).
- **Mediana global 0.181** · por família: **axial 0.031** (nível da campanha
  per-rig), transversal 0.208, creep 0.356.
- Decomposição por mecanismo presente em **todos os 122** simulados.

## Paridade e gap de adoção (achado principal)

O runner reproduz a campanha **bit-a-bit** quando a config adotada é a que a
campanha usou (**24/78** casos da galeria idênticos até o último dígito —
ex. liu2025_M16_amp0p25 MAE 0.08920577095890085). A divergência média
(|ΔMAE| 0.115) nos demais **não é bug** — é **gap de adoção**: a galeria usou
configs experimentais por-curva que nunca foram promovidas ao
`adopted_configs.json`:

1. **Bauer fig8/fig6**: cfg adotada é ANINHADA (per-espectro/per-fig,
   `W_crit` no joelho medido) — a API `suggest_overrides` só consome o nível
   plano. Runner 0.60-0.65 vs campanha 0.03-0.06.
2. **Rousseau HDPE**: campos de harness (`GA_member`, `F_eff` stack-limited)
   são intencionalmente não-traduzidos pela API. Runner 0.16-0.57 vs 0.03-0.14.
3. **Rousseau steel t12/t14**: constantes da campanha (ex. c_bend por-rig)
   fora do bloco adotado.
4. **Creep (Li2022)**: `C_creep` é POR PAR (§4.7) — o valor UFU do shared
   não vale no par Li2022; a campanha usou o re-centrado.

A coluna **"campanha"** no mestre e a linha no report por caso mostram os dois
números lado a lado — o gap fica visível e auditável. **Fechar o gap = promover
configs por-curva ao adopted_configs** (decisão de campanha/professor, não de
software).

## Bugs reais achados pelo batch (corrigidos)

- Best-match de config adotada por 1º token aplicava `LIU_2017_axial` ao
  LIU_2025 (MAE 0.72) → maior prefixo comum + variante HDPE por stem.
- Tuners legados dos configs adotados dropados em silêncio → shim
  `translate_legacy_tuners` na fronteira (mesmo padrão do solver_worker).
- Métrica sem trim 0.10 / alinhamento no 1º ponto → convenção pré-registrada.
- UFU 3/4" UNC fora da tabela ISO → fallback genérico d/p com A_s padrão.

## Limitações honestas

- Runner v1 não parametriza a família `other` (Sandia modal) — report degrada.
- 4 curvas zhang2006 da galeria não têm `ValidationCase` estruturado (lacuna
  de dados; ficam fora dos 128 até serem promovidas a casos).
- Fingerprint cobre constantes (shared + adotadas), **não** mudanças de código
  do engine — um engine novo com os mesmos JSONs não marca o cache como stale.
- Configs adotadas aninhadas (Bauer) não são resolvidas — ver gap acima.

## Handoff — Plano B (GUI V2)

`ValidationController` no padrão dos Planos 2-3: página no `_center` (árvore
fonte→caso + detalhe com plot/métricas/decomposição/staleness), botões
Re-simular caso · Re-simular tudo (QThread) · Abrir report HTML · Gerar geral.
Toda a lógica já está no pacote — o controller é só orquestração
(`all_records`, `ValidationStore`, `simulate_case`, `write_reports`).
Follow-ups de dados: promover zhang2006 a casos; decidir adoção das configs
por-curva (fecha o gap); `library_common` delegar ao pacote (dedup).

## Adendo — report v2 (2026-07-10, mesmo dia)

Pedido do professor: formatacao melhor, erro artigo-vs-software mais claro,
modelo MSD reproduzivel so lendo. Entregue (spec
`2026-07-10-report-v2-design.md`, plano `2026-07-10-report-v2.md`):
residuo ASSINADO com banda +-MAE + narrativa interpretada + MAE por estagio
I/II/III; secao 2 gerada do modelo REAL (`gui_bridge.build_case_model`) com
cadeia SVG, tabela de elementos (id/tipo/k/c/m/material/preload%),
carregamento global, glossario PT de variaveis e passo-a-passo; secoes
numeradas 1-6 + resumo executivo + @media print. 128 regenerados.

## Adendo — report v3 interativo + intake destacado (2026-07-10)

Pedidos do professor: (a) secao de intake CLARA E DESTACADA no software; (b)
profissionalismo nos reports — graficos interativos, indice, interatividade,
recursos. Entregue (spec `2026-07-10-report-v3-interactive-design.md`):
(a) painel destacado no TOPO do modulo Validation (passos 1-copiar prompt /
2-qualquer IA / 3-importar, feedback ao copiar) + Help->copiar prompt;
(b) renderer BASCHART embutido (JS puro, zero deps): tooltip+crosshair,
legenda clicavel, zoom por arrasto, CSV por grafico; TOC lateral com realce,
secoes colapsaveis, barra fixa (MAE/imprimir/tema), noscript; mestre com
filtro instantaneo, ordenacao clicavel e chips. 129 regenerados.
