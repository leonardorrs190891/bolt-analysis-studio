# As 14 suspeitas de digitalização — investigadas (atividade D)

**Data:** 2026-07-29 · **Store:** `3546e6745448` · lint:
`New_Theory/digitalizacao_lint.py` (+ `.md` com a tabela completa).

O lint achou 91 sinalizações, das quais **88 são `METRIC_LIMITED`** (granularidade
do dado contra a régua — não é defeito de leitura, e o estudo de granularidade
mostrou que **não** torna o σ_res inalcançável). Sobram **14 suspeitas reais de
digitalização**, investigadas aqui uma por uma.

## Veredicto: nenhuma explica um caso fora do tripé, mas duas coisas ficam

### 1. Os 11 flags de 1º ponto ≠ 1,0 NÃO chegam à métrica — o mecanismo é outro

Verificado: `metric_data[0] = 1,0000` nas cinco curvas com CSV acima de 1,05
(`bauer2024_M8_fig6_rep3` 1,0747 · `eccles2010_fig8c` 1,0670 ·
`yang2019_varamp_small_to_large` 1,0846 · `yang2021_amp0p5mm` 1,0638 ·
`yang2021_amp0p7mm` 1,0993). **O dado é renormalizado pelo próprio 1º ponto**
antes de a métrica olhar, então minha hipótese inicial — resíduo de −0,10 no
primeiro ponto, sozinho no limite do res.máx — **está errada**.

**Mas o flag não é inócuo, e o mecanismo verdadeiro é pior de detectar:** se o
digitalizador leu o 1º ponto errado, a renormalização por ele desloca a **curva
inteira multiplicativamente**. Um 1º ponto lido 7 % alto (Bauer rep3) puxa os
outros 7 % para baixo — erro que não aparece em nenhum ponto isolado e sim como
viés global, que é justamente o que a perna do MAE mede e o σ_res **não** vê.

⇒ Fica como item de conferência visual (§3b do report daquele caso), não como
defeito provado. Prioridade: `yang2021_amp0p7mm` (+9,9 %) e
`yang2019_varamp_small_to_large` (+8,5 %).

### 2. As duplicatas do CSV fino da fig2 são minhas, são reais, e são pequenas

`liu2025_M16_fig2_single` tem **13 abscissas repetidas** em 134 pontos (x=2 com
y=0,9900 **e** 0,9850; x=5 com 0,9700 e 0,9650…). Foi introduzido hoje, na
re-digitalização fina que eu adotei.

Impacto medido, colapsando as duplicatas pela média dos resíduos: σ_res
**0,02677 → 0,02635** (**−0,00042**). A curva precisa de −0,0018 para passar ⇒
**o dedup não a resgata**. Vale consertar por higiene (uma curva de decaimento
não pode ter dois valores no mesmo ciclo), não pela meta.

### 3. ⚠️ O achado que não estava na lista: 3 aprovações com ≤5 pontos

Investigando os 2 flags de `POUCOS_PONTOS`, apareceu o que importa: **3 das 104
curvas aprovadas no tripé têm a 3ª perna medida sobre menos de 6 pontos.**

| curva | pontos | MAE | res.máx | σ_res |
|---|--:|--:|--:|--:|
| `10_Yang_2023…0_15_mm_below_threshold__7` | **4** | 0,0093 | 0,0241 | 0,0103 |
| `10_Yang_2023…0_18_mm_below_threshold__1` | **5** | 0,0076 | 0,0156 | 0,0087 |
| `zhang19_fig4_1e3cyc_Test1to3` | 5 | — | — | — |

Não é escândalo: o MAE e o res.máx delas são genuinamente pequenos. Mas **σ_res
de 4 pontos não distingue "forma fiel" de sorte** — a estatística não existe
nessa amostra. A leitura honesta da meta passa a ser: **104 no tripé, dos quais 3
têm a 3ª perna sem suporte estatístico.**

Duas saídas, e a escolha é do professor: (a) declarar um mínimo de pontos para a
perna do σ_res ser julgável (com `n < 6` virando "não julgável", como já se faz
com `resid_std = None`); (b) manter e registrar o caveat. A opção (a) tiraria 3 do
tripé — 104 → 101 — e é a mais defensável se o número for para publicação.

## Saldo

Nenhuma das 14 suspeitas explica uma curva fora do tripé. O valor da atividade
foi outro: **corrigiu o mecanismo que eu atribuía ao flag de 1º ponto** (viés
multiplicativo global, não resíduo local), **mediu que o dedup não resgata a
fig2** (−0,0004 contra −0,0018 necessários) e **achou 3 aprovações que a régua
nova concede sobre 4-5 pontos** — este último é o único item com consequência
para o número publicado.
