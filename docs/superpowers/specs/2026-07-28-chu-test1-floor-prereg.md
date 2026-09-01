# PREREG — piso lido do CHU test1 (loose_arrest_floor por leitura L24)

**Data/congelamento:** 2026-07-28 (commit deste arquivo = hash do congelamento; gates
IMUTÁVEIS depois disto). **Autorização:** fila ("☐ autorizo prereg do `chu…test1`" →
"autorize esses e todos os demais", 2026-07-28). **Baseline:** store `294808504d83`.

## Mudança (uma linha de config, zero engine)

`New_Theory/adopted_configs.json` → `CHU_2026_test1.cfg.per_case.test1` ganha
`loose_arrest_floor: 0.9876` (hoje: só `mu_bearing: 0.1043`). Prov: **lido-do-dado**
pelo leitor L24 `arrest_floor_from_curve` sobre o ratio cru do test1 —
`floor=0.9876, plateau=True` (platô limpo; não é limite-inferior). Não é fit.

## Contas de satisfazibilidade (RODADAS hoje, baseline atual — regra §4.45)

- Controle negativo: re-sim sem mudança = store **bit-exato** (Δ = 0.00e+00 nos 2 números).
- Com o floor lido injetado (`_prefit_overrides`): **0.0035 / 0.0082 — tripé PASS**
  (store: 0.0663/0.1147, viola só o pico).
- Caveat G-A3 declarado: é input POR CASO numa família não-monotônica — defensável
  porque é LEITURA de dado (idioma emb_um per_case), não constante de forma fitada.
- O canal rotacional é ATIVO no test1 (a sonda 7/7 já o media; regra
  `channel_gated_levers` conferida) — a alavanca não é inerte aqui.

## Gates (imutáveis)

- **GT1**: re-sim canônica do test1 pós-config no tripé (MAE ≤ 0,10 E maxerr < 0,10).
- **GT2 (cego)**: as outras 8 curvas CHU **bit-idênticas** na re-sim (o token `test1`
  não casa nenhum outro case_id — verificar por comparação numérica, não por suposição).
- **GT3 (PR-37′ global)**: no re-stamp completo (batch 202 + sintético via método
  direto), **nenhum caso piora +0,01** e **zero curvas mudam de status** exceto o
  test1 (fora→dentro). Fingerprint uniforme no store inteiro.
- **Ramo de falha:** qualquer gate ✗ ⇒ reverter o config (backup antes), documentar
  no §4.55, nada adotado.

## Efeito esperado na meta

CHU_2026: violadoras 7→6 (test1 entra). Meta 147→148/202 no tripé (a confirmar no GT3).
