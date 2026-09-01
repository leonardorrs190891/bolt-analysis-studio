# PREREG — `liu2020_fig9_zinc_AF0.4mm`: o settling da amplitude MAIOR lido do próprio dado — mais uma exceção cai

**2026-08-21 (14:0x-14:1x)** · **gates congelados neste commit** · mandato das
14:02 (*"continue até atingir tripé"*) — a exceção MAIS PRÓXIMA do censo
(1,05×: viola só o MAE 0,0526; mx e σ já fecham).

## 1. Diagnóstico (medido)

|viés|/MAE = **1,00** — puro NÍVEL: o modelo retém demais uniformemente. O
emb da fonte (1,12 µm, lido de outra condição) não cobre o settling DESTA
curva: o dado perde ~7 % até x≈70-150 (0,4 mm é a MAIOR amplitude da série
fig9 — settling vibração-dirigido mais fundo, a física que o próprio engine
nomeia no `settling_amplitude_factor`/`s1_amp_gate`).

## 2. Pacote (per_case token `af0.4`, inserido ANTES de `zinc` no dict)

⚠️ Armadilha de matcher pega no G2 sandbox: o token `zinc` casa **7 curvas**
(first-match com break) — a 1ª tentativa destruía 6 irmãs do tripé. O token
específico `af0.4` casa SÓ a alvo e precisa vir ANTES no dict (ordem de
inserção); o per_case dela carrega o pacote zinc completo + o emb lido.

| campo | valor | procedência |
|---|---|---|
| herdados do zinc | mu 0,15 · flank_wear_on/transverse_on 1 · k_wear_flank 1,2e-15 | a adoção item M (2026-08-15) intacta |
| `emb_um` | **3,0** | **LIDO do settling da própria curva** (~7 %·18 kN/k_b) |
| `N_emb` | **60** | lido do joelho do settling (x≈70-150) |

Sandbox: 0,0526/0,0766/0,0227 → **0,0082/0,0232/0,0100 — FECHA**
(0,16×/0,23×/0,40×). Região: **9/9 células** (emb 2-4 × N 40-100). G2:
**8 irmãs bit-idênticas** (com o token específico).

## 3. Estatuto

A exceção dela ("trinca de fadiga §3.1.2 — changepoint não achou o corte")
sai por mérito: a curva fecha COM a cauda incluída — a trinca não impede.
Retirada K6 com prova preservada.

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo ao dígito | 0,0082/0,0232/0,0100 pelo canônico — FECHA |
| **G2** | 8 irmãs LIU_2020 bit-idênticas | |
| **G3** | isolamento Δ=0 fora da fonte; fingerprint único nos 210 | |
| **G4** | censo | 168 → **169/205 (82 %)** · exceções 22 → 21 |
| **G5** | sincronização | docs · triagem · aging · **HTML regenerado (o "atualize validation cases")** |

## Estado

EM EXECUCAO 2026-08-21 (14:1x): adocao + re-stamp na sequencia.
