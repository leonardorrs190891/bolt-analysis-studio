# PREREG — ICMEZ série lk13,8: as DUAS restantes do comprimento curto fecham pela mesma rota da Fig. 3

**2026-08-19 (22:2x)** · **gates congelados neste commit** · continuação do caso
6 da fila (mesma rota, leituras POR CURVA da Fig. 3, medidas EM SÉRIE).

## 1. Leituras por curva

| curva | slope Fig. 3 | fsk | paralelos | θ_alvo | k (bisseção) | floor |
|---|---:|---:|---:|---:|---:|---|
| `amp0p3_F14p3_lk13p8` | −137,8 (r=0,997, RANSAC declarado) | 0,9252 | 5944 N | 36,8° | 0,02644 | 0 (dado 0,228 atravessa 0,308) |
| `amp0p4_F17p6_lk13p8` | −143,6 (r=0,996) | 0,9220 | 6122 N | 52,4° | 0,03305 | 0 (dado 0,223 atravessa) |

## 2. Sandbox — FECHAM

- `amp0p3_F14p3_lk13p8`: 0,0411/0,0859/0,0428 → **0,0130/0,0379/0,0162**; banda da partição 2/3 (par×1,1 raspa σ 0,0253).
- `amp0p4_F17p6_lk13p8`: 0,0313/0,0793/0,0357 → **0,0319/0,0579/0,0178**; banda 3/3.

## 3. As DUAS lk19,8 NÃO fecham pela rota — registrado com números

- `amp0p3_F14p3_lk19p8`: 0,0899/0,1765/0,0625 (PIOROU — o floor herdado 0,308 com
  fim 0,354 distorce a trajetória quando o θ_alvo força k alto).
- `amp0p3_F17p6_lk19p8`: 0,0389/0,0818/0,0334 (σ 1,34× — piora leve).
⇒ ficam ABERTAS; a forma delas (desaceleração terminal × floor) exige leitura
própria — próximo ciclo, prereg próprio.

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | os 2 alvos fecham ao dígito | valores acima pelo canônico |
| **G2** | irmãs | as outras 6 ICMEZ bit-idênticas (incl. as 2 lk19,8 NÃO adotadas e o caso 6 já gravado) |
| **G3** | isolamento | Δ=0 fora do ICMEZ no diferencial do carimbo |
| **G4** | fingerprint único nos 210 | |
| **G5** | censo | 150 → **153/205** (caso 6 + estas 2) · abertas 15 → 12 · ICMEZ 3/8 → 6/8 |
| **G6** | sincronização completa | |

## Estado

EXECUTADO 2026-08-19 (22:2x-22:3x): G1/G2 na hora; carimbo consolidado com o caso 6.
