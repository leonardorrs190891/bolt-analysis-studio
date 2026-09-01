# PREREG — `rousseau2025_hdpe_t10`: partição + θ bisectado — a fonte ROUSSEAU vai a 8/8

**2026-08-19 (21:5x)** · **gates congelados neste commit** · caso 4 da fila do
mandato 20:47 · casos 1–3 fechados hoje (steel_t10, hdpe_t12, amp0p2).

## 1. Leituras (traço θ da Fig. 4 re-extraído/validado; procedimento das irmãs)

| leitura | valor | origem |
|---|---|---|
| θ_fim | **21,27°** | re-extração por ticks (impresso ~21) |
| ruído do dado | σ=0,0134 vs média móvel(7) | CSV 165 pts oscilante — 54 % do limite σ; teto de qualidade declarado |
| paralelos | 886 N (emb+creep+wear do grupo HDPE) | decomposição do baseline |
| **partição** | dreno_rot = (2932−886)/21,27 = **96,2 N/deg** | procedimento validado (t12, amp0p2) |
| `free_spin_kin` | **0,9707** | 1 − 96,2/3278 |
| `k_loose_graded` | **0,02094** | bisseção por θ_fim=21,27 (o floor 0,2 do grupo gateia — a bisseção absorve) |
| `loose_amp_exp` | 0,0 | θ(N) linear r²=0,975 |
| `s_crit_loose` | 0,0 | rotação arranca cedo |

Pacote no per_case do `ROUSSEAU_HDPE`, token `hdpe_t10` — ⚠️ substring de
`hdpe_t10_amp0p2` (tripé)! Mesma blindagem first-match: entrada
`"hdpe_t10_amp0p2": {}` ANTES do pacote; o teste-guarda cobre.

## 2. Medições sandbox — FECHA

**0,0927/—/0,0691 → 0,0315/0,0630/0,0224** (0,63×/0,63×/0,90×); F_fim 0,274 vs
0,267; θ exato. Banda da partição (±10 % dos paralelos): centro e metade
inferior fecham (0,9695 dá 0,0184/0,0543/0,0196; 0,9719 raspa fora no σ por
5 %) — declarado: 2 de 3 células da banda.

## 3. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo fecha | 0,0315/0,0630/0,0224 ao dígito pelo canônico |
| **G2** | irmãs | as 7 bit-idênticas (incl. hdpe_t10_amp0p2 pela entrada-vazia) |
| **G3** | isolamento | vs store commitado `3bb2ca3c9128`: mudam EXATAMENTE t12, amp0p2 e hdpe_t10 (as 3 adoções do carimbo; errata Δ=0) |
| **G4** | fingerprint único nos 210 | |
| **G5** | censo | 147 → **150/205** · abertas 18 → 15 · **ROUSSEAU 8/8 = fonte FECHADA** |
| **G6** | sincronização completa | |

## 4. Predições registradas

1. G1 ao dígito. 2. Censo **150/205 (73 %)** — SEXTA curva do dia; a fonte
ROUSSEAU fecha 8/8 (era 4/8 de manhã). 3. σ=0,0224 contra ruído-do-dado 0,0134
⇒ o modelo está a 1,7× do teto físico do dado — margem honesta. 4. Próximos da
fila: yang2021_amp0p5, demir (ICMEZ), yang2019_amp0p4, yang2023-0,30 (declarada).

## Estado

EXECUTADO 2026-08-19 (21:5x): G1/G2 na hora; carimbo único com as 3 adoções.
