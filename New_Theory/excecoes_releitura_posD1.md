# Releitura das 44 exceções assinadas — pós-D1 (2026-07-30)

**Medido no store `3546e6745448` com o D1 adotado** (limite efetivo da 3ª perna
= `max(0,025; piso medido da fonte)`). Gerado na adoção; a retirada da §A foi **assinada e executada em 2026-07-30** (commit próprio, G4 do prereg do D1).

## A. 19 assinaturas que viraram REGRA — ✅ RETIRADAS (assinado 2026-07-30)

Assinatura do professor em sessão ("retire as 19 assinaturas"). Executada no
mesmo dia: as 19 saíram de `_F7_EXCECOES` para `_EXCECOES_RETIRADAS_D1`
(registro em código, provas preservadas; NÃO consumida pelo censo). Exceções
ativas: **25** (16 F5 + 9 F7). Se o D1 for revertido, esta lista volta à F7 no
mesmo commit — o guard de `test_medicoes_cruzadas` prende os dois lados.

Estas curvas agora **passam no tripé por mérito** — a exceção 'por prova de
piso' virou exatamente o que ela alegava: o piso da fonte. Manter a assinatura
não é errado, mas é contabilidade dupla; a proposta é retirá-las e deixar o
`limite_sres` carregar a prova.

| fonte | curva | piso σ da fonte |
|---|---|---:|
| `BAUER_2024` | `bauer2024_M8_fig6_rep2` | 0.0900 |
| `BAUER_2024` | `bauer2024_M8_fig6_rep3` | 0.0900 |
| `CHU_2026` | `chu2026ti_D1p0mm_F0_49kN_test5` | 0.0507 |
| `CHU_2026` | `chu2026ti_D1p0mm_F0_49kN_test6_repeat` | 0.0507 |
| `ECCLES_2010` | `eccles2010_fig7c_axial_2p7kN_constant` | 0.0828 |
| `ICMEZ_2025` | `demir2024_amp0p3_F14p3_lk13p8` | 0.0574 |
| `ICMEZ_2025` | `demir2024_amp0p3_F14p3_lk19p8` | 0.0574 |
| `ICMEZ_2025` | `demir2024_amp0p3_F17p6_lk13p8` | 0.0574 |
| `ICMEZ_2025` | `demir2024_amp0p3_F17p6_lk19p8` | 0.0574 |
| `ICMEZ_2025` | `demir2024_amp0p4_F17p6_lk13p8` | 0.0574 |
| `JCSR_2023` | `jcsr2023_galv_seawater` | 0.2214 |
| `JCSR_2023` | `jcsr2023_plain_seawater` | 0.2214 |
| `KARLSEN_2022` | `karlsen2022_M30_HV_run2p2` | 0.1742 |
| `KARLSEN_2022` | `karlsen2022_M30_HV_run6p2` | 0.1742 |
| `KARLSEN_2022` | `karlsen2022_M30_HV_run7p1` | 0.1742 |
| `KARLSEN_2022` | `karlsen2022_M42_HV_run21p0` | 0.1742 |
| `ROUSSEAU_2025` | `rousseau2025_hdpe_t14` | 0.1859 |
| `ROUSSEAU_2025` | `rousseau2025_steel_t12` | 0.1859 |
| `SUN_2025_CRIMP` | `sun2025efa109235_transverse_grease_crimp` | 0.0663 |

## Leitura que protege as provas antigas

Entre as 25 que restam, a perna que manda é **res.máx 15 · MAE 8 · σ_res 2**.
Isto é bom sinal para as assinaturas: elas foram julgadas na régua de 2 pernas,
cujas provas falavam do **pico** ("a curva ideal já violaria a meta") — e é o
pico que segue reprovando a maioria. As **2** que hoje são seguradas pelo σ_res
(e as 8 do MAE) merecem releitura da prova; as 15 do res.máx estão provadas na
perna certa.

## B. 25 assinaturas AINDA NECESSÁRIAS

Continuam fora mesmo com o limite por fonte. Coluna final = a perna que manda
HOJE; conferir se a prova assinada fala da perna certa é a releitura que o
professor pediu que ficasse na fila.

| sev | manda | fonte | curva | prova assinada (resumo) |
|---:|:--:|---|---|---|
| 4.67× | mx | `ECCLES_2010` | `eccles2010_fig6_annotated_4kN_axial` | sobreposição axial (G-B1 FAIL: receita PR-31 levou o res.máx de 0.467 a 1.028) — o engine  |
| 3.97× | mx | `BAUER_2024` | `bauer2024_M12_fig8_test1` | scatter de réplicas (desvio-à-mediana 0.349) |
| 2.67× | mae | `ECCLES_2010` | `eccles2010_fig8d_axial_3p5kN_intermittent` | sobreposição axial (G-B1 FAIL: res.máx 0.252 -> 0.400 com a receita) |
| 2.42× | sd | `YANG_2021` | `yang2021_fig2_typical` | canal estrutural ξ-dependente confundido |
| 2.36× | mx | `KARLSEN_2022` | `karlsen2022_M30_HVtorqued_run14p2` | prova de piso (FORTE): res.máx 0.236/0.540 · MAE 0.090/0.235 · σ 0.085/0.174 |
| 2.21× | sd | `YANG_2021` | `yang2021_amp0p8mm_ax6kN` | canal estrutural ξ-dependente confundido |
| 1.88× | mx | `ROUSSEAU_2025` | `rousseau2025_steel_t10` | prova de piso (FORTE): res.máx 0.188/0.546 · MAE 0.087/0.206 · σ 0.098/0.186 |
| 1.80× | mx | `BAUER_2024` | `bauer2024_M12_fig8_test2` | scatter de réplicas (desvio-à-mediana 0.349) |
| 1.71× | mx | `BAUER_2024` | `bauer2024_M8_fig6_rep4` | scatter de réplicas (desvio-à-mediana 0.328) |
| 1.53× | mx | `ROUSSEAU_2025` | `rousseau2025_hdpe_t10` | prova de piso (FORTE): res.máx 0.153/0.546 · MAE 0.058/0.206 · σ 0.057/0.186 |
| 1.51× | mae | `BAUER_2024` | `bauer2024_M8_fig6_rep6` | scatter de réplicas (desvio-à-mediana 0.328) |
| 1.46× | mae | `LIU_2020_WEAR` | `liu2020_fig9_zinc_AF0.4mm_P0-18kN` | trinca de fadiga atribuída pelo paper (§3.1.2) — a regra automática de changepoint NÃO ach |
| 1.45× | mx | `ECCLES_2010` | `eccles2010_fig8c_no_axial_baseline2` | prova de piso (FORTE): res.máx 0.145/0.257 · σ 0.039/0.083 |
| 1.38× | mx | `ROUSSEAU_2025` | `rousseau2025_hdpe_t12` | prova de piso (FORTE): res.máx 0.138/0.546 · MAE 0.064/0.206 · σ 0.056/0.186 |
| 1.34× | mae | `ECCLES_2010` | `eccles2010_fig7d_axial_3p1kN_constant` | sobreposição axial — PASSA no tripé por ARTEFATO: o FLOOR_TRIM corta os 4 pontos da cauda  |
| 1.31× | mx | `JCSR_2023` | `jcsr2023_plain_outdoor` | cliff/rebound de corrosão (forma faltante) |
| 1.30× | mx | `ECCLES_2010` | `eccles2010_fig8b_axial_0p7kN_intermittent` | sobreposição axial — e o FLOOR_TRIM corta 27 dos 35 pontos, logo o MAE 0.044 é pontuado so |
| 1.26× | mx | `BAUER_2024` | `bauer2024_M8_fig6_rep1` | scatter de réplicas (desvio-à-mediana 0.328) |
| 1.24× | mae | `JCSR_2023` | `jcsr2023_stainless_seawater` | cliff/rebound de corrosão (forma faltante) |
| 1.22× | mx | `ECCLES_2010` | `eccles2010_fig8a_no_axial_baseline1` | prova de piso (FORTE): res.máx 0.122/0.257 · σ 0.039/0.083 |
| 1.21× | mae | `KARLSEN_2022` | `karlsen2022_M30_HV_run1p2` | prova de piso (FORTE): MAE 0.060/0.235 · σ 0.031/0.174 |
| 1.20× | mx | `BAUER_2024` | `bauer2024_M12_fig8_test3` | scatter de réplicas (desvio-à-mediana 0.349) |
| 1.12× | mx | `BAUER_2024` | `bauer2024_M8_fig6_rep5` | scatter de réplicas (desvio-à-mediana 0.328) |
| 1.05× | mae | `CACCESE_2009` | `caccese2009_tapered_45kN_rep1` | prova de piso (FORTE): MAE 0.052/0.121 |
| 1.01× | mae | `LIU_2016` | `liu2016wear_fig9a_m45nm` | prova de piso (FORTE): MAE 0.050/0.102 |
