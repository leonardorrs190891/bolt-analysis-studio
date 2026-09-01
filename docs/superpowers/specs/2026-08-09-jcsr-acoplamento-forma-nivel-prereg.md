# Prereg — **JCSR D-AA**: varredura CONJUNTA forma×nível (o que a marginal não podia achar)

**2026-08-09** · continuação do D-Z sob o MANDATO · gates **IMUTÁVEIS**.

## Por que existe este prereg — o erro de método que o D-Z expôs

O `ataque_curva.py` varreu `C_creep` em 0,5–2,0× na `galv_seawater` e **piorou em todas as
doses**; eu escrevi *"a constante está no ótimo"*. Estava — **na forma antiga**.

Depois de adotar a forma nova no D-Z, a **mesma** varredura de `C_creep` dá:

```
galv, C x1,10:   0,0348/0,0526/0,0154  ->  0,0102/0,0249/0,0087   (as 3 pernas juntas)
```

Causa: forma e nível do creep são **acoplados** por construção —
`δ_sat(t) = C_creep·F_0·(1 − e^{−(t/t_c)^α})`, com a assíntota em `C_creep` e a chegada em
α/t_c, e dentro da janela do ensaio as duas se confundem. Varredura **um-de-cada-vez** acha
um ótimo **condicional** e o declara global. Isto já está registrado como gotcha no
`CLAUDE.md`.

⚠️ **Consequência direta:** as duas curvas que eu havia declarado sem rota — `outdoor` e
`stainless_seawater` — nunca foram varridas do jeito certo. Nenhuma das minhas duas
varreduras (α×t_c a `C` fixo; `C` à forma fixa) podia achar um ótimo conjunto.

## As grades — DECLARADAS, já rodadas (só-leitura, nada adotado ainda)

| grade | curva | células | fecham |
|---|---|---:|---:|
| α×t_c a `C` fixo | `outdoor` | 56 | **0** |
| α×t_c a `C` fixo | `stainless` | 56 | **0** |
| conjunta α×t_c×C | `outdoor` | 150 | **0** |
| conjunta α×t_c×C | `stainless` | 150 | **1** ⚠️ na fronteira |
| **conjunta ESTENDIDA** | `stainless` | 180 | **10 — região INTERIOR** |

A 1ª conjunta saturou na fronteira em α (máx 8) e em C (mín 0,70) com **1 célula a 0,97×** —
fio de navalha, que a campanha recusa. A **disciplina de fronteira de grade** (D-L) mandou
estender, e a extensão achou **região**: α ∈ {8, 10, 12} × t_c ∈ {0,80; 0,85} × C ∈
{0,60 … 0,75}, **interior à grade nos dois eixos** que haviam saturado.

## Regra de escolha da célula — DECLARADA ANTES

**A mais CENTRAL da região** (maior número de vizinhos de grade que também fecham),
desempate pela **pior perna**. Precedente: D-I escolheu a mais centrada, **não** a de melhor
MAE, e o D-H registrou como falha do próprio prereg ter omitido a regra de escolha.

Não é escolha por MAE. Se a regra apontar célula diferente da de melhor score, **vale a
regra**.

## Observação de apoio — explicitamente NÃO é o driver

`C_creep` carrega procedência *"PROXY AMBIENTAL per-par×ambiente (corrosão vestida de
creep)"*. Hoje o **stainless** em água do mar carrega o **maior** dos três (1,736e-9 = **2,4×**
o aço-carbono no mesmo ambiente) — inversão contra a própria leitura declarada. A mudança
proposta (×0,65 ⇒ 1,128e-9) **reduz** a inversão; **não a elimina**, e eu não tenho como
afirmar monotonia entre severidade de corrosão e `C_creep` a partir daqui. Fica como
observação, e o driver segue sendo a grade medida com região interior.

## O que muda

| curva | constante | de → para |
|---|---|---|
| `stainless_seawater` | α, t_c, `C_creep` | pela regra de centralidade, na região medida |
| `galv_seawater` | `C_creep` | pela mesma regra, na sua própria região |
| `plain_seawater` | `C_creep` | idem — se e só se a regra achar região melhor |
| `outdoor` | — | **nada**: 0 de 150 células. Segue estrutural. |

## Gates (congelados)

| # | gate | esperado |
|---|---|---|
| **K1** | `stainless_seawater` fecha o tripé | MAE ≤0,05 · res.máx ≤0,10 · σ ≤0,0250 |
| **K2** | `galv`/`plain` seguem fechadas **e não pioram em nenhuma perna** | Δ ≤ 0 nas 3 |
| **K3** | **controle**: `plain_indoor` e `plain_outdoor` | ΔMAE ≤ **+0,01** (esperado bit-idêntico) |
| **K4** | **isolamento**: nada fora do `JCSR_2023` muda | Δ = 0 exato |
| **K5** | censo | **141 → 142** |
| **K6** | suíte completa | verde |

⚠️ **K2 tem `Δ ≤ 0`, mais estrito que o usual `+0,01`.** As duas já estão no tripé; mexer
nelas só se justifica se melhorar. Piorar curva que passa, para ganhar em outra, é o
sobreajuste que este prereg existe para barrar.

⚠️ **Se a `stainless` fechar mas a `galv`/`plain` piorarem, adota-se SÓ a `stainless`.** Os
três grupos de config são independentes (`JCSR_2023_<cond>`), então a separação é estrutural,
não negociada.

## Rollback

`.bkp_daa` no `adopted_configs.json` e no store. Qualquer gate divergente ⇒ restaura e
registra.

## Estado

✅ **EXECUTADO em 2026-08-09 (D-AA), gates 6/6** — commit `921e627`, resultado em
`New_Theory/jcsr_acoplamento_forma_nivel_resultado.md`.

K1 ✅ `stainless` 0,0619/0,1237/0,0739 → **0,0118/0,0304/0,0146** ·
K2 ✅ `galv` Δ = (−0,0247 −0,0277 −0,0067) e `plain` Δ = 0 exato ·
K3 ✅ controles bit-idênticos · K4 ✅ isolamento Δ = 0 · K5 ✅ censo 141 → **142** ·
K6 ✅ suíte 913/1 (após retirar a assinatura redundante da `stainless`, que passou a fechar
por mérito).

⛔ A `plain_seawater` **não** foi adotada: a regra de centralidade apontou `C ×1,05`, que
piora MAE e res.máx para ganhar 0,0005 em σ, e o **K2 exigia Δ ≤ 0 nas três** — regra e
gate discordaram e o **gate congelado mandou**.

⚠️ Carimbo acrescentado em 2026-08-13 (ver nota no prereg irmão).
