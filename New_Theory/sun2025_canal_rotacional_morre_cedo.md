# `SUN_2025_CRIMP` — a `grease_standard` tem forma nomeada; a `grease_crimp` é **outro defeito**

**2026-08-15 (23:4x)** · só-leitura · **nada adotado** · store `20be19aabe11`,
censo **143/205**, 2ª linha da fila **12 → 13**.

Diagnóstico das 2 abertas do `SUN_2025_CRIMP` pelo shell canônico
(`ataque_curva.py`), contra a mesma barra usada no `ICMEZ`, no `YANG_2021` e no
`ROUSSEAU`.

---

## 1. `grease_standard` — forma NOMEADA

| critério | medido |
|---|---|
| pernas | MAE **2,00×** · res.máx **3,19×** · σ **4,73×** (σ manda) |
| forma | resíduo **TROCA DE SINAL**: +0,027 → −0,079 → **−0,174**; ρ(res,N) **−0,69**; curvatura sub-classe **B** (devagar cedo, rápido tarde) |
| canal | **rotacional domina o total** (ABS **0,655** contra 0,268 do embedding) — **mas 0 % do incremento tardio** |
| ⚠️ capacidade tardia | incremento tardio total **0,00434** ⇒ *"forma sobre o fim NÃO move a curva"* |
| rota | melhor alavanca `tr_loose_gain`=2,058 leva σ 4,73× → **3,20×** (res.máx 0,319 → 0,136); a dose seguinte **explode** (σ 5,91×) |

⇒ **a forma:** o canal rotacional carrega dois terços da perda e **morre antes do
fim**, enquanto o dado segue caindo. É a **mesma estrutura** do `ICMEZ` (canal
arresta, dado atravessa) e do `ROUSSEAU` (rotacional-dominado, falta perda
tardia).

⚠️ Confirmação lateral: `loose_arrest_floor` aparece **TRAVADA** por procedência,
e movê-la para 0,08 **melhora** (σ 4,27×) — o mesmo mecanismo que o `ICMEZ`
nomeou, aqui bloqueado por proveniência.

## 2. `grease_crimp` — **NÃO é o mesmo defeito**

| critério | medido |
|---|---|
| pernas | MAE **0,44×** ✅ · res.máx **0,89×** ✅ · σ **1,21×** ⛔ (só o σ, por 21 %) |
| forma | resíduo **não** troca de sinal; ρ **−0,10** ⇒ **OFFSET**, erro de nível uniforme |
| onde | erro se forma **CEDO** — *"mexer no fim não adianta"* |
| canal | rotacional 0,574 total, **0 % tardio**; embedding **0 %** tardio |

⇒ **par de curvas da mesma fonte, formas opostas**: uma cresce até o fim
trocando de sinal, a outra é offset formado cedo. **Não entram sob o mesmo
nome.**

## 3. A decisão, e por que ela importa

**Só a `grease_standard` entra em `_FORMA_NOMEADA`.** 2ª linha **12 → 13**, não 14.

⚠️ Este é precisamente o ponto onde *"por simetria"* erraria: as duas são da
mesma fonte, ambas abertas, ambas com o rotacional dominante no total — e
mesmo assim o **defeito é outro**. A barra é a **forma medida**, não o
parentesco de fonte.

A `grease_crimp` fica entre as **8 abertas sem forma nomeada**, com o
diagnóstico registrado (offset cedo, σ a 1,21×) para quem a atacar depois.

## Reprodutibilidade

`py -3.12 New_Theory/ataque_curva.py sun2025efa109235_transverse_grease_standard`
e `…_grease_crimp`. O shell usa `rh.limite_sres` e lê a decomposição do store —
não reimplementa regra.
