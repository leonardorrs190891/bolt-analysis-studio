# Qual forma falta — assinatura do resíduo nas 51 da fila

**Data:** 2026-07-29 · **Store:** `3546e6745448` · **Script:**
`New_Theory/forma_residuo_classes.py` (só-leitura) · tabela por curva em
`forma_residuo_classes.md` · atividade **A** pré-pipeline.

## Por que existe

O item 1 (sensibilidade) mostrou que **nenhuma alavanca existente** fecha a perna
do σ_res, e o estudo de granularidade mostrou que **não é artefato de dado**. Sobra
"propor forma" — e a pergunta que decide o pipeline é *qual*. Este estudo responde
por dado: lê o resíduo assinado de cada curva da fila e o descreve por
características independentes.

## O achado que orienta o pipeline

**A pergunta operativa não é "onde erra" — é se o resíduo é DERIVA ou ONDULAÇÃO.**
Medido pelo R² do ajuste `e ≈ β·s` (o quanto do resíduo é tendência linear no
progresso normalizado):

| classe | curvas | leitura | fontes principais |
|---|--:|---|---|
| **DERIVA** (R² ≥ 0,7) | **10** | o resíduo é rampa suave ⇒ falta um **termo monótono**, não uma forma nova | CHU_2026 ×4 · LIU_2022_RETIGHT ×2 · LI_2022_TRIBOINT · ANCORA_INTERNA |
| mista (0,3–0,7) | 23 | rampa + ondulação | LU_2024 ×5 · YANG_2023_IJPEM ×4 · LIU_2016 ×4 · ZHANG_2018 ×3 |
| **ONDULADO** (R² < 0,3) | **18** | nenhuma constante remove ⇒ forma faltante de verdade | LU_2024 ×5 · LIU_2025 ×2 · YANG_2019 ×2 · ANCORA_INTERNA ×2 |

**O cluster mais tratável é o do CHU_2026:** 4 curvas com **R² 0,82–0,83** e
**β ≈ +0,58** — quase idênticas. Resíduo positivo crescendo linearmente significa
o modelo terminando **muito acima** do dado: o colapso que o artigo mede não
acontece no modelo, e o descolamento cresce em rampa. É um alvo único para 4
curvas, e a fonte tem 6 na fila.

Outra muito limpa: `10_Yang_2023…0_25_mm` com **R² 0,92** e β +0,41.

## As marginais (cada característica isolada)

| característica | distribuição |
|---|---|
| **onde** o \|resíduo\| é máximo | **FIM 28** · INICIO 20 · MEIO 3 |
| deriva β | β+ 29 · β− 22 |
| lado | **cruza 31** · abaixo 11 · acima 9 |

Duas leituras: o defeito mora **nas pontas** (só 3 de 51 no meio), e a maioria
**cruza** o dado — confirma que o gargalo é dispersão (σ_res), não deslocamento
(que seria o viés, e a F7 já tratou).

## ⚠️ Um dos meus quatro descritores era fraco, e era justo o decisivo

A 1ª versão usava, como discriminador constante-vs-forma, a **média da 2ª
diferença** do resíduo. Ela **cancela** em resíduo que oscila, então "reta"
significava duas coisas opostas — linear de verdade, ou ondulando simétrico. Pela
marginal, 31 de 51 saíam "reta", o que sugeriria erroneamente que dois terços da
fila são erro de constante.

O R² da tendência linear separa de fato: só **10** são deriva. Os dois descritores
ficaram no script, com o fraco documentado como tal.

## O que o pipeline deve fazer com isto

1. **Começar pelo cluster DERIVA (10 curvas)**, e pelo sub-cluster CHU (4, com β e
   R² quase iguais). Um termo monótono novo é ask muito menor que uma forma nova, e
   o gate é direto: `Δσ/ΔMAE` (item 1) mais o β caindo.
2. **Não tratar os 18 ONDULADO com constante.** Para eles o gate de qualquer
   candidato deve exigir queda de σ_res **com R² baixo mantido** — se o candidato
   só endireita a rampa, ele não resolveu esta classe.
3. **Cruzar com o catálogo de formas** já registrado (kernel desacelerante de
   run-in, bifurcação de limiar, canal ξ-dependente, incubação de assentamento,
   `graded_scrit` que já existe default-inerte): a assinatura *FIM · β+ · cruza*
   com R² alto casa com "colapso que não acontece"; *INICIO · β− · infla* (4 do
   LU_2024) casa com "run-in mal modelado". A escolha deixa de ser intuição.

**Caveat honesto:** R² sobre 5–15 pontos é ruidoso, e as classes de fronteira
(0,3 e 0,7) são convenção, não natureza. O que é robusto é a ordenação e o
tamanho relativo dos clusters, não a filiação de uma curva isolada perto do corte.

## Reprodutibilidade

```bash
py -3.12 New_Theory/forma_residuo_classes.py --md   # segundos, só-leitura
```
