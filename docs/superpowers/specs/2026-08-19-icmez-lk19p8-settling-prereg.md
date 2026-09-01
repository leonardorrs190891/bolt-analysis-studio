# PREREG — ICMEZ lk19,8 ×2: o settling LIDO DO INTERCEPTO fecha as duas — a fonte vai a 8/8

**2026-08-19/20 (22:5x)** · **gates congelados neste commit** · continuação da
fila (as 2 que a rota lk13,8 não fechou, registradas com números no prereg
anterior).

## 1. O diagnóstico que mudou a partição

A 1ª tentativa (floor herdado) piorava; a 2ª (floor 0) melhorava sem fechar. O
resíduo da trajetória nomeou a causa: **o modelo era CÔNCAVO onde o dado é
linear** — os paralelos do GRUPO (29 % de settling front-loaded) não são os da
curva. O dado publica o settling real no **intercepto da reta pós-joelho**
(F(N→0) extrapolado): 1,3 % na F14p3 e 4,5 % na F17p6 — mesma classe de leitura
do intercepto F(θ) da steel_t10.

E a **taxa local é CONSTANTE até o último ponto** nas duas (0,0033 e
0,0020/ciclo, sem desaceleração aproximando 0,354/0,549) ⇒ **sem arresto
observável na janela** ⇒ floor per_case 0 — a decisão da 1ª tentativa ("fim >
0,308 ⇒ herda o floor") lia o NÍVEL onde devia ler a TAXA.

## 2. Pacotes (per_case; tokens únicos por curva)

| campo | F14p3_lk19p8 | F17p6_lk19p8 | origem |
|---|---:|---:|---|
| `free_spin_kin` | 0,9005 | 0,8966 | 1 − slope/(k_b·lead); slopes 127,7/132,7 da Fig. 3 (r≥0,998) |
| `emb_depth` [m] | 5,0e-7 | 2,14e-6 | settling do intercepto × F₀ ÷ k_b |
| `C_creep` | 0,0 | 0,0 | mesma leitura (settling é TODO o não-rotacional observável) |
| `k_loose_graded` | 0,04701 | 0,03378 | bisseção por θ_alvo = (ΔF − settling)/slope = 70,7° / 53,8° |
| `loose_arrest_floor` | 0,0 | 0,0 | taxa constante até o fim ⇒ sem arresto na janela |
| kernel | graded_scrit, s_crit=0, exp=0 | idem | taxa constante lida |

## 3. Sandbox — FECHAM com folga

- F14p3: 0,0438/0,0902/0,0343 → **0,0064/0,0174/0,0073** (0,13×/0,17×/0,29×!)
- F17p6: 0,0353/0,0592/0,0292 → **0,0147/0,0329/0,0119**
- **Banda do settling ±30 % (k re-bisectado): 3/3 nas DUAS** — quase não move.

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | os 2 alvos fecham ao dígito | valores acima pelo canônico |
| **G2** | as outras 6 ICMEZ bit-idênticas | |
| **G3** | isolamento no diferencial do carimbo | |
| **G4** | fingerprint único nos 210 | |
| **G5** | censo 153 → **155/205** · abertas 12 → 10 · **ICMEZ 8/8 = SEGUNDA fonte fechada no dia** | |
| **G6** | sincronização completa | |

## Estado

EXECUTADO 2026-08-19/20 (22:5x): G1/G2 na hora; carimbo consolidado.
