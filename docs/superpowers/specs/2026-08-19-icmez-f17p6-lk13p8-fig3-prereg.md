# PREREG — `demir2024_amp0p3_F17p6_lk13p8`: a Fig. 3 do ICMEZ é a rigidez de dreno PUBLICADA como caracterização — e o floor do grupo era a barreira

**2026-08-19 (22:0x)** · **gates congelados neste commit** · caso 6 da fila do
mandato 20:47 (casos 1–4 fechados; caso 5 yang2021_amp0p5 registrado sem rota —
dispersão de espécime com réplicas de sinais opostos, sem observável de rotação
na fonte).

## 1. O observável que faltava — publicado de propósito

A Fig. 3 do paper (*"Clamping Load–Angle Relation of the Loosening Tests"*) é a
**caracterização dedicada da rigidez de dreno**: 18 ensaios de desaperto
quase-estático (2 comprimentos × 3 cargas × 3 reps), usada pelos AUTORES como
input do modelo deles (eq. 23, φ*). Extraída HOJE do PDF (vetorial + ticks):

| curva | slope | r |
|---|---:|---|
| lk19,8 · 14,3 kN | −127,7 N/deg | −0,999 |
| lk19,8 · 17,6 kN | −132,7 N/deg | −0,998 |
| lk19,8 · 20,9 kN | −140,4 N/deg | −0,998 |
| **lk13,8 · 17,6 kN (o caso)** | **−143,6 N/deg** | **−0,996** |

A lei-de-junta (§4.56) confirmada em TERCEIRA fonte de leitura: slopes
127–144 N/deg quase independentes da carga, contra `k_b·lead` = 1842 N/deg do
engine ⇒ **fsk = 1 − 143,6/1842 = 0,9220** (lido).

## 2. O pacote (per_case, token `amp0p3_f17p6_lk13p8`)

| campo | valor | origem |
|---|---|---|
| kernel | graded_scrit, s_crit=0 | forma existente |
| `free_spin_kin` | **0,9220** | Fig. 3 (φ* dos autores) |
| `loose_amp_exp` | 0,0 | F(N) quase-linear ⇒ taxa constante |
| `k_loose_graded` | **0,03028** | bisseção por θ_fim DERIVADO = (ΔF−paralelos)/slope = (13010−6108)/143,6 = 48,1° (partição — procedimento validado 3× hoje) |
| `loose_arrest_floor` | **0,0** | o dado (fim 0,260, caindo) ATRAVESSA o floor 0,308 do grupo E o lido 0,2757 (plateau=False) ⇒ regra da barreira: nenhum floor ≥0,26 é legítimo; sem platô observável ⇒ 0 |

O floor 0,308 do grupo fica para as 7 irmãs (per_case não vaza — G2).

## 3. Medições sandbox — FECHA

**0,0422/0,0994/0,0436 → 0,0141/0,0366/0,0175** (0,28×/0,37×/0,70×);
F_fim 0,259 vs 0,260. **Banda da partição (paralelos ±10 % ⇒ θ 43,8–52,3°,
k re-bisectado): 3/3 fecham.**

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo fecha | 0,0141/0,0366/0,0175 ao dígito pelo canônico |
| **G2** | irmãs | as 7 ICMEZ bit-idênticas |
| **G3** | isolamento | Δ=0 fora do ICMEZ no diferencial do carimbo |
| **G4** | fingerprint único nos 210 | |
| **G5** | censo | +1 pela curva (contado sobre o carimbo que incluir as 3 ROUSSEAU: 150 → **151/205**) |
| **G6** | sincronização completa | |

## 5. Predições registradas

1. G1 ao dígito. 2. SÉTIMA curva do dia. 3. As outras 4 ICMEZ abertas têm a
MESMA rota (slopes próprios da Fig. 3; refinar o clustering das tracejadas
14,3/20,9) — preregs em série. 4. A dependência fraca do slope com a carga
(127→140 N/deg para 14,3→20,9 kN) nesta junta zincada M8 contrasta com a forte
do ROUSSEAU (920→333 para 10→3,5 kN) — registrar no §4.56 (a física é a
rigidez de contato; o contraste pode ser µ/acabamento).

## Estado

EXECUTADO 2026-08-19 (22:0x-22:1x): G1/G2 na hora; carimbo consolidado.
