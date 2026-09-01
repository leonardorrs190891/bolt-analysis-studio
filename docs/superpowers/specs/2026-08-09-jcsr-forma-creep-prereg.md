# Prereg — **JCSR**: re-fit das constantes de FORMA do kernel de creep

**2026-08-09** · pedido direto do professor (*"solve the two cases … 
jcsr2023_galv_seawater; jcsr2023_plain_seawater"*) · gates **IMUTÁVEIS**.

## O que isto é — dito sem enfeite

**Não é física nova.** É **re-fit, numa grade mais fina, de duas constantes já
declaradas como `fitado-this-rig`** no `adopted_configs.json`:

| constante | `prov` registrada |
|---|---|
| `creep_alpha_sat` | *"fitado-this-rig (grade)"* |
| `creep_t_c` | *"seed = onset c da Eq.(2) do paper (input-de-paper) × ajuste fino 1,5–2× (fitado-this-rig)"* |

O kernel saturante em si **já está adotado** (prereg F3.1-JCSR) e o `C_creep`
(o **nível**, proxy ambiental) **não é tocado**. O que muda é só a **forma**.

⚠️ **Por isso os gates carregam CONTROLES.** Re-fit com o censo como objetivo é
exatamente onde o sobreajuste entra, e a proteção é: as outras 3 curvas da fonte
não podem piorar, e nada fora da fonte pode mudar.

## Por que a forma, e não outra coisa

O shell `ataque_curva.py` mediu nas duas: **só o σ viola** (1,87× e 1,48×), MAE
0,78×/0,58×, o erro **se forma nos ciclos 7–15** e o creep faz **toda** a perda
(0,646 e 0,490 absolutos) contribuindo **zero** ao terço final. A `galv` tem
viés **exatamente +0,0000** — nível perfeito, **só a forma** errada.

E as constantes atuais **não estavam no ótimo**: a grade mostra σ caindo 34 % na
`galv` só movendo `t_c`.

## Os valores

| curva | atual (α, t_c) | novo (α, t_c) | σ |
|---|---|---|---|
| `galv_seawater` | 3,0 · 1 373 760 | **3,0 · 1 717 200** (×1,25) | 0,0468 → **0,0154** |
| `plain_seawater` | 3,0 · 2 531 520 | **5,0 · 2 303 683** (×0,91) | 0,0371 → **0,0234** |

Ambos com **região**, não fio de navalha: **6** células fecham na `galv`
(α 2,5–4,0 × t_c 1,15–1,25) e **5** na `plain` (α 5,0–6,0 × 0,88–0,91).

## Gates (congelados)

| # | gate | esperado |
|---|---|---|
| **J1** | as 2 alvo fecham o tripé | MAE ≤0,05 · res.máx ≤0,10 · σ ≤0,0250 |
| **J2** | **controle**: `plain_indoor`, `plain_outdoor`, `stainless_seawater` não pioram | ΔMAE ≤ **+0,01** cada |
| **J3** | **isolamento**: nenhuma curva fora do `JCSR_2023` muda | Δ = 0 exato |
| **J4** | censo | **139 → 141** |
| **J5** | suíte completa | verde |

⚠️ **J2 é o gate que importa.** A `plain_indoor` é quase perfeita
(0,0009/0,0021/0,0010) e é o canário: se um re-fit da forma a degradar, o que
se ganhou nas outras duas foi sobreajuste.

⚠️ **O `α` da `plain` sobe de 3,0 para 5,0** — mudança grande. Ela está
declarada, e o que a sustenta é (a) a constante ser `fitado-this-rig` por
registro, (b) haver **região** e não ponto, e (c) o J2/J3 barrarem custo em
outra curva.

## Rollback

`.bkp_jcsr` no `adopted_configs.json` e no store. Qualquer gate divergente ⇒
restaura e registra.

## Estado

✅ **EXECUTADO em 2026-08-09 (D-Z), gates 5/5** — commit `ca3668b`, resultado em
`New_Theory/jcsr_forma_creep_resultado.md`.

J1 ✅ `galv` 0,0348/0,0526/**0,0154** e `plain` 0,0187/0,0480/**0,0234** ·
J2 ✅ **ΔMAE = +0,0000 nos três controles, bit-idênticos** · J3 ✅ Δ = 0 exato ·
J4 ✅ censo 139 → **141** · J5 ✅ suíte 913/1.

⚠️ Carimbo acrescentado em 2026-08-13, ao auditar que **38 de 45** preregs de agosto não
declaravam estado — o arquivo sozinho não dizia o que estava pendente, que é justamente o
que o cron manda ler.
