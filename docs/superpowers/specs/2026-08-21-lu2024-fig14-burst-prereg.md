# PREREG — forma `onset_burst_*` no engine + fecho da `fig14_amp1p0_long` (a PIOR declarada do projeto)

**2026-08-21 (07:4x-08:0x)** · **gates congelados neste commit** · continuação
do mandato de ontem 23:08 (*"faça o ataque a esse problema em loop, validando
tudo e assinando tudo"*) — a forma nomeada no registro de ontem
(`lu2024_fig14_burst_resultado.md`) foi construída e fecha a curva-alvo.

## 1. A forma (implementada, TDD 5/5 em `tests/test_onset_burst.py`)

`onset_burst_{frac,rate}` — **liberação da energia incubada** quando o gate
de onset (o MESMO Hill de `slip_onset_W`, sem estado novo) abre:
`d_theta_burst = g·rate·max(0, F₀ − alvo)/(k_b·lead)`, alvo = (1−frac)·F₀_init.
Burst intenso que DESACELERA sozinho ao chegar ao alvo — o platô→burst→cauda
das fig14_long. dF/dE derivam do mesmo dθ (conservação intacta); só o ramo
graded lê; frac=0 OU rate=0 = OFF exato. 2 consertos de setup do próprio
teste registrados no arquivo (baseline colapsando; emb default de 30 µm).

## 2. O pacote da `fig14_amp1p0_long` (0,4802/0,8553/0,2894 — 9,6× o MAE)

| campo | valor | procedência |
|---|---|---|
| `emb_load_frac` | 0 | **LIDO do protocolo**: o bedding fracional do grupo (0,4) foi calibrado no settling de 36 % do protocolo MANUAL; a fig14 de máquina assenta 3 % — o item F dentro da config |
| `emb_um` | 1,0 | lido do settling (−3,2 %) |
| `slip_onset_W` | 360 | ancorado no N_onset ≈ 57 (o platô de 54 ciclos é observável; fase medida em 2 iterações — a realimentação do gate muda o W/ciclo) |
| `slip_onset_sharpness` | 40 | estrutural (o colapso em ~5 ciclos exige Hill quase-degrau) |
| `onset_burst_frac` | **0,62** | **LIDO da inflexão do burst** (o dado desce a ~0,36 e desacelera; a 1ª leitura 0,46 do fundo raso foi corrigida pelo resíduo) |
| `onset_burst_rate` | 0,30 | fitado (região) |
| `k_loose_graded` / `loose_F_exp` | 0,06 / **1,24** | fe **LIDO da cauda** (razão de taxas 7× para F 4,8×); k fitado |
| `loose_arrest_floor` / `k_ratchet` | 0 / 0 | lidos (afrouxa total; kernel trocado) |

Contagem: **3 fitados** (rate, sharpness, k) + 5 lidos/ancorados.
Sandbox: → **0,0136/0,0882/0,0186 — FECHA** (0,27×/0,88×/0,74×); região de
**6 células conexas** (frac 0,60–0,66 × k 0,05–0,06); célula por
centralidade 3/4 + pior perna 0,88×. G2 sandbox: **12 de 13 LU
bit-idênticas** (o token `fig14_amp1p0` não colide com a fig18_amp1p0 ✓).

## 3. A irmã `fig14_amp0p5_long` — atacada, NÃO fecha, custo declarado

Mesma forma com constantes próprias: melhor célula 0,1257→**0,0478/0,1104/
0,0417** (melhora 2,6×; mx 1,1×, σ 1,7×). O perfil dela tem **DOIS regimes
pós-burst** (re-platô ~0,47 por 50 ciclos + 2ª descida) que a forma não faz
— fe alto (re-platô) foi varrido e piora. Segue DECLARADA; o registro
completo vai no resultado. NÃO adotada (melhoria sem fecho).

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo ao dígito | 0,0136/0,0882/0,0186 pelo canônico — FECHA |
| **G2** | as 12 irmãs LU bit-idênticas | |
| **G3** | isolamento Δ=0 fora do LU no re-stamp; fingerprint único nos 210 | |
| **G4** | censo | 166 → **167/205 (81 %)** · declaradas 12 → 11 (retirada K6 da amp1p0_long) |
| **G5** | burocracia da forma | ledger DOF (124→126, teto <127; frac/rate ADOTADOS ficam fora dos dormentes) · VarSpecs ×2 (126/126) · suíte-alvo verde |
| **G6** | sincronização | docs vivos · triagem · aging · HTML |

## Estado

EM EXECUCAO 2026-08-21 (08:0x): adocao + re-stamp na sequencia.
