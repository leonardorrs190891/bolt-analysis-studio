# Pré-registro — F2 Onda B (adoções comportamentais per-rig, prompt-mestre)

**Data:** 2026-07-21 · **Executor:** sessão mestre · **Baseline vigente:** re-pin F0.4
(store ae2d7e0 + F1; 202 casos, mediana 0,04713) · **Ordem:** P2.1 → P2.2 → P2.3 (alavancagem).
Gates escritos ANTES de qualquer fit/config — imutáveis. Regra transversal da campanha em
todos: **nenhuma curva regride >0,1 e a mediana da fonte não piora >0,005**; fit sempre em
curva completa (short-smoke mente); adoção por-fonte com `prov`, nunca global.

## P2.1 — Canal de flanco per-rig no H.Li2022 (`LI_2022_TRIBOINT`)

**Baseline dos 4 casos-alvo (F0.4):** axialmin_10Hz 0,0886/0,1119 · axialmin_15Hz
0,0588/0,0750 · axialmin_20Hz 0,0178/0,0239 · axial_10Hz_full 0,1180/0,4053 (mae/maxerr).

**Mudança:** `flank_wear_on=1.0` como config da fonte (switch NUNCA fitado — regra) +
`k_wear_flank` fitado per-rig em curva completa (partida: 1,89e-13 do gate T4; `flank_amp_exp`
mantido no default salvo se o fit em curva completa exigir — se exigir, registrar). Nota de
proveniência: 1,89e-13 está ~9× ACIMA da banda KB `thread|35CrMo-SCM435` [4e-15, 2e-14] —
o aviso do `check_input` é esperado e documenta-se como fitado-this-rig (o canal de flanco
representa desgaste de flanco sob A_F, não o thread-wear transversal da âncora; anotar no prov).

**Gate (imutável):**
- G2.1a. Os 4 casos do alvo com **tripé <0,1** — para `axial_10Hz_full`, a cauda de fratura é
  out-of-model: se maxerr>0,1 vier EXCLUSIVAMENTE do trecho pós-fratura, aplicar a convenção de
  trim REGISTRADA (FLOOR_TRIM/trim de fratura já existente) e reavaliar; se após o trim ainda
  violar, o caso é candidato a exceção F5 (não força a adoção a FAIL sozinho SE os outros 3
  passarem e o full melhorar ≥50% do gap; registrar exatamente o que ocorreu).
- G2.1b. Zero regressão >0,1 em QUALQUER curva de LI_2022_TRIBOINT e mediana da fonte não
  piora >0,005.
- G2.1c. Transversais intocados por construção (canal só modo força axial) — verificar com
  re-sim de 6 casos-controle transversais (paridade exata).
- G2.1d. Suíte-alvo verde (test_l1_flank_wear_axial em particular).
- FAIL (2 tentativas de fit no máx.) → não adota, documenta no ledger, casos ficam para F3/F4.

## P2.2 — Creep saturante vs log-t por fonte de creep

**Fontes de creep e baselines (F0.4):** JCSR_2023 (galv_seawater 0,3115/0,4277 ·
plain_outdoor 0,2182/0,3370 · plain_seawater 0,1849/0,2743 · stainless_seawater 0,2792/0,4133 ·
plain_indoor 0,0009/0,0021) · CACCESE (7 casos, todos ≤0,0523/0,0890) · QIN_2024 (3, ≤0,0099/
0,0159) · LI_2022_MARSTRUC (6, ≤0,0079/0,0105) · NAH_2014 (curvas na pasta F; se não wired
como casos, fica fora deste prereg — registrar).

**Mudança:** por fonte, confrontar `creep_mode="saturating"` (fit per-fonte de `creep_t_c` e
`creep_alpha_sat` em curva completa; `C_creep` mantido — per-par, §4.7) contra o log-t vigente.
**Adotar SOMENTE nas fontes onde o tripé melhorar** (expectativa honesta: Caccese/Qin/MarStruc
já estão no piso → log-t fica; JCSR é o único candidato com gap — e o rótulo MEM lá é 'forma'
3/5, então o saturante pode NÃO fechar: FAIL documentado manda p/ F3).

**Gate (imutável) por fonte:** tripé melhora (mediana da fonte cai E nenhum caso piora >0,1 E
count de violadores da fonte não sobe) → adota `creep_mode+creep_t_c+creep_alpha_sat` no cfg
da fonte com prov fitado-this-rig; senão mantém log-t. Suíte de creep verde
(test_l5_creep_saturating). Máx. 2 preregs de fit por fonte.

## P2.3 — Clamp L3 (`famp_couple_on=1`) + re-fit conjunto de `tr_loose_gain`

**Escopo (critério, não lista):** fontes TRANSVERSAIS em modo FORÇA com F_amp registrado no
registry/inputs (candidatas conhecidas: SANDIA_2021; confirmar por varredura do registry na
abertura — a lista exata entra no ledger ANTES do fit).

**Mudança:** `famp_couple_on=1` como config por-fonte + re-fit conjunto de `tr_loose_gain`
(nota T2: o gain vigente foi calibrado com F_amp SEM clamp) e, se o fit exigir,
`mu_eff_lo`/`mu_eff_F0_ref`/`gross_ceiling_decay` per-rig (cada um vira prov fitado-this-rig).
Cuidados documentados (T2/T3): não co-habilitar canais de rosca legado+L1 (sobreposição de dE
~1,5×); dupla via de dano no teto (k_dmg_mu × gross_ceiling_decay) — se ambos ativos na fonte,
registrar a interação antes de fitar.

**Gate (imutável):** tripé melhora nas fontes-alvo (mesma regra por fonte de P2.2); zero
regressão nas demais transversais (re-sim de controle 6 casos); suíte-alvo verde
(test_l3_famp_coupling). FAIL2 → documenta e segue para F3.

## Registro

Cada prereg fechado (PASS ou FAIL) = linha no ledger mestre com números antes/depois + commit
com arquivos explícitos (configs + store parcial da fonte + reports afetados regenerados).
