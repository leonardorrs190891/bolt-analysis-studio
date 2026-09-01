# PREREG — `lu2024_M8_fig14_amp0p25_long`: settling em degrau + arresto — pacote de LEITURA quase pura; a 6ª órfã cai

**2026-08-21 (12:5x-13:0x)** · **gates congelados neste commit** · mandato das
12:50 (*"continue"*).

## 1. ERRATA do diagnóstico (a 4ª do mapa em 2 dias)

O mapa de rotas dizia *"stick total + platô de 27-56 ciclos ⇒ precisa forma
sigmoide de estágio I"*. **Errado em duas partes**: o platô de 27-56c era da
FAMÍLIA (a amp1p0 o tem); a amp0p25 tem **degrau imediato** (1,0→0,84 entre
x=16-32) **+ arresto PERFEITO** (0,827-0,829 por 1000 ciclos, deriva ~0,002)
— e o exponencial com relógio CURTO faz exatamente isso. A forma Weibull
(`emb_clock_m`) foi construída no caminho (TDD 4/4, state-based exata,
default bit-idêntico) e fica como CAPACIDADE — **não é usada nesta adoção**
(m=1) e entra DORMENTE no ledger.

## 2. Pacote (per_case `fig14_amp0p25` — token conferido: só ela)

| campo | valor | procedência |
|---|---|---|
| `emb_um` | **6,0** | **ANCORADO no platô publicado**: perda de settling 0,171·F₀ = 1797 N ⇒ δ = 1797/k_b(M8) ≈ 6 µm |
| `N_emb` | **30** | **LIDO do degrau** (a queda acontece entre x=16 e x=32) |
| `emb_load_frac` | 0 | LIDO do protocolo (o bedding 0,4 do grupo é do settling manual — o MESMO achado das irmãs fig14) |
| `C_creep` / `k_ratchet` | 0 / 0 | **LIDOS do arresto**: 1000 ciclos SEM deriva (0,827→0,829) — qualquer taxa >0 é refutada pelo dado |

**Zero fitados** — todos os 5 números têm leitura. Sandbox:
0,1017/0,2314/0,0367 → **0,0077/0,0630/0,0156 — FECHA** (0,15×/0,63×/0,62×).
Região: **12/12 células** (emb 5,0-6,5 × N 22-40); célula por centralidade +
pior perna 0,63×. G2 sandbox: 12 de 13 LU bit-idênticas.

## 3. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo ao dígito | 0,0077/0,0630/0,0156 pelo canônico — FECHA |
| **G2** | irmãs LU bit-idênticas | |
| **G3** | isolamento Δ=0 fora do LU; fingerprint único nos 210 | |
| **G4** | censo | 167 → **168/205 (82 %)** · declaradas 11 → 10 (retirada K6) |
| **G5** | ledger | `emb_clock_m` entra DORMENTE (capacidade sem adoção); teto 126→127 |
| **G6** | sincronização | docs · triagem · aging · HTML · errata no mapa de rotas |

## Estado

EM EXECUCAO 2026-08-21 (13:0x): adocao + re-stamp na sequencia.
