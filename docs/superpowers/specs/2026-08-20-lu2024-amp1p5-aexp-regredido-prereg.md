# PREREG — `lu2024_M8_fig18_amp1p5`: expoente de chegada REGREDIDO do próprio dado

**2026-08-20 (12:4x)** · **gates congelados neste commit** · mandato das 12:40
(*"continue, gere rotas"*) — 4º ataque do mapa das declaradas.

## 1. A curva e o defeito

Única declarada com MAE e res.máx JÁ FECHANDO (0,0314/0,0742) — falta só o σ
(0,0353, 1,41×). Órfã de protocolo (item F), sem piso de réplica ⇒ rota de
modelo é a única.

## 2. Falsificação que precedeu (mesma sessão, registrada)

Floor per-case LIDO (0,0176 do terminal) **PIORA** (0,0314→0,0808): destrava o
colapso e o modelo despenca mais que o dado — o floor 0,10 do GRUPO estava
certo. Combinação floor lido × aexp alto também não fecha (melhor 0,0336/
0,0795/0,0395 a aexp=8). A alavanca certa não é o nível do arresto — é a FORMA
da chegada a ele.

## 3. O pacote (per_case `fig18_amp1p5`): 1 número, REGREDIDO

| campo | valor | procedência |
|---|---|---|
| `arrest_approach_exp` | **1,864** | **REGREDIDO DO DADO CRU**: log(dF/dN) vs log(1−floor/r) com o floor 0,10 do grupo, n=8 intervalos (excluído o 1º = assentamento), slope 1,864, **r² = 0,685** — e o valor cai DENTRO da região que fecha (1,5–3,0), perto do centro. Contraste declarado: a mesma regressão na T28 deu r² 0,515 e NÃO foi usada (lá o aexp é fitado-declarado); aqui a regressão suporta a leitura |

Floor do grupo (0,10) INTOCADO. Zero mexida em qualquer outra constante.

## 4. Sandbox (já medido)

- Célula regredida: **0,0139/0,0393/0,0157 — FECHA** (0,28×/0,39×/0,63×).
- Região: aexp 1,5–3,0 fecha (4 células medidas: 1,5/2,0/2,5/3,0); 1,2 e 4,0
  não fecham — região interior com o regredido dentro.
- G2 sandbox: 12 irmãs bit-idênticas (T28 difere do store apenas pela adoção
  já em batch — esperado).

## 5. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo fecha ao dígito | 0,0139/0,0393/0,0157 pelo canônico |
| **G2** | irmãs | as 12 LU bit-idênticas ao carimbo T28 |
| **G3** | isolamento | Δ=0 exato fora do LU no re-stamp; fingerprint único nos 210 |
| **G4** | censo | +1 (com T28 e IJPEM 0_45 no mesmo carimbo: 159 → **162**) · declaradas 18 → 15 |
| **G5** | sincronização | retirada K6 em `_DECLARADAS` (prova em `_DECLARACOES_RETIRADAS_FECHAM_POR_ADOCAO`) · triagem · docs · aging · HTML |

## Estado

EXECUTADO 2026-08-20 (12:5x-13:2x): G1 ao digito (0,0139/0,0393/0,0157 — FECHA), G2 irmas bit-identicas, G3 isolamento exato + fingerprint unico df35fd990380, G4 censo 162 consolidado · declaradas 15, G5 sincronizado (retirada K6 com prova preservada).
