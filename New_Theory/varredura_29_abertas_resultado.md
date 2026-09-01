# A receita do D-AB varrida nas 29 abertas: **5 candidatas**, e o controle da fonte mata 3

**2026-08-09 (noite)** · só-leitura · **nada adotado** · store `9696038085e0`, censo 143/205.

## O que foi feito

A adoção **D-AB** provou dois pontos que valem para toda a fila: (a) sondar com a **base
efetiva** — e não com os *overrides* — revela alavancas que o instrumento cego nunca tocou; e
(b) a escolha da alavanca é do **controle da fonte**, não da curva-alvo. Esta varredura aplica
a receita às **29 abertas** de uma vez.

Passo 1: para cada aberta, 6 alavancas × 2–4 doses, base efetiva, procurando qualquer dose que
feche o tripé. Passo 2: para quem fechou, medir o custo em **todas** as irmãs da fonte.

## Passo 1 — 5 de 29 têm alavanca livre que fecha

| curva | fonte | alavanca | dose | antes → depois |
|---|---|---|---|---|
| `liu2025_M16_amp0p25` | LIU_2025 | `C_creep` | 6,5e-12 (×0,5) | 0,0757/0,0945/0,0267 → 0,0458/0,0553/0,0160 |
| `liu2025_M16_amp0p3` | LIU_2025 | `C_creep` | 6,5e-12 (×0,5) | 0,0645/0,0865/0,0249 → 0,0360/0,0511/0,0183 |
| `liu2025_M16_fig2_single` | LIU_2025 | `C_creep` | 1,95e-11 (**×1,5**) | 0,0276/0,0571/0,0268 → 0,0176/0,0332/0,0178 |
| `yang2019_M10_amp0p6_10Hz` | YANG_2019 | `k_wear_spec` | 1,5e-13 (×3) | 0,0310/0,0665/0,0351 → 0,0292/0,0443/0,0228 |
| `chu2026ti_D0p5mm…test9` | CHU_2026 | `N_emb` | 100 (×2) | 0,0449/0,1173/0,0547 → 0,0406/0,0988/0,0483 |

Nenhuma delas aparecia sob o shell cego.

## Passo 2 — o controle da fonte reprova 3 e aprova 2

| candidato | fonte | tripé | pioram >+0,01 | veredito |
|---|---|---|---|---|
| `C_creep`=6,5e-12 (amp0p25 / amp0p3) | LIU_2025 (7) | 3 → 4 | **2** | ⛔ **1 SAI** (`amp0p6`) |
| `C_creep`=1,95e-11 (fig2_single) | LIU_2025 (7) | 3 → **2** | **5** | ⛔ **2 SAEM** |
| `k_wear_spec`=1,5e-13 | YANG_2019 (5) | 0 → **1** | **0** | ✅ **ADOTÁVEL** |
| `tr_loose_gain`=2,6 | YANG_2019 (5) | 0 → **1** | **0** | ✅ **ADOTÁVEL** |
| `N_emb`=100 | CHU_2026 (9) | 3 → **4** | **0** | ✅ **ADOTÁVEL** |

## ⛔ O LIU_2025 não admite `C_creep` per-fonte — e o motivo é uma contradição interna

As três curvas pedem **direções opostas**: `amp0p25` e `amp0p3` fecham com `C_creep` **×0,5**;
a `fig2_single` fecha com **×1,5** (e falha em ×0,5 e ×0,75). Uma constante per-fonte tem de
escolher um lado, e cada lado cobra:

* **×0,5** — a `amp0p6` **sai do tripé** e a `amp0p8` piora **+0,0844**;
* **×1,5** — `amp0p4` e `amp0p5` **saem**, e 5 curvas pioram (a própria `amp0p25` +0,0288).

⇒ **falsificação da rota "um `C_creep` para o LIU_2025"**, com número. As curvas da fonte
discordam sobre o valor da constante, e isso é informação sobre a fonte, não sobre a dose: a
`fig2_single` tem amplitude **não reportada no artigo** (errata viva do §4.48b), então ela pode
simplesmente não pertencer à mesma família de amplitude das outras. Rota que sobra: `per_case`
— que é adoção de outra natureza e precisa de argumento próprio, não de conveniência métrica.

## ✅ Os 2 adotáveis, e o que falta em cada um

**`chu2026ti_D0p5mm_F0_49kN_Ra1p6um_test9` · `N_emb`=100** — CHU_2026 vai de 3 para 4 no
tripé, **zero** curvas piorando em 9. Alavanca única, sem ambiguidade de escolha.

**`yang2019_M10_amp0p6_10Hz`** — fecha por **duas** alavancas independentes, ambas com custo
zero na fonte: `k_wear_spec`×3 (0,0292/0,0443/0,0228) e `tr_loose_gain`×1,3
(0,0296/0,0443/0,0214). ⚠️ **A escolha precisa de regra declarada antes**, como no D-AA — e
aqui há um dado que pesa: o `YANG_2019` tem **0 de 5** curvas no tripé hoje, então esta seria a
primeira da fonte, e a constante escolhida passa a governar as outras 4. Escolher pela curva
que fecha seria repetir o erro que o D-AB pegou.

## O que isto diz sobre a fila

Das 29 abertas, **24 não têm nenhuma alavanca livre de dose única que feche** — nem com a base
efetiva. Para essas, o veredito *"candidata a forma"* sobrevive ao conserto do instrumento, e
agora com a lista do que foi sondado por trás (6 alavancas × 2–4 doses), que é o que faltava
para o veredito valer.

## Reprodutibilidade

Varredura + controle no scratchpad (`varredura29.py`, `ctrl5.py`); saída
`varredura29.json`. ~40 min no total, só-leitura.
