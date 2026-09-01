# PREREG — `yang2023ame_axial` (CFRP): o embedment LENTO dos próprios autores — a declaração de escopo cai

**2026-08-20 (18:1x-18:2x)** · **gates congelados neste commit** · mandato das
18:14: *"ataque yang2023ame_axial"* — a curva estava DECLARADA fora de escopo
de material (CFRP) por aprovação do professor em 2026-07-31; o mandato de
ataque supersede e a condição de reabertura é reavaliada.

## 1. O diagnóstico da declaração estava INVERTIDO

A declaração dizia *"o modelo não tem relaxação viscoelástica de matriz
polimérica; MAE 7,7×"*. Medido: o dado CFRP **quase não perde** (10 % em 1100
ciclos, suave, overshoot inicial +0,9 %) — é o MODELO que despenca 45 % por
embedding default (a fonte não tinha grupo adotado; rodava emb 11 µm genérico
com relógio instantâneo). O erro era de INPUT/constante, não de forma
faltante.

## 2. A física é a dos AUTORES, e a forma JÁ EXISTE no engine

A nota de aparato (G8): *"bolt-head embedment into the composite surface
[é] the dominant, almost exclusive, preload-loss mechanism"* (S22 do CFRP:
YC = 23 MPa; porca travante suprime rotação). O embedment de matriz polimérica
é PROGRESSIVO — no engine, o `EmbeddingLoss` state-based com relógio lento
(`N_emb` ≫ janela). Regressão do closed-form no cru:
`r = 1 − A·(1−e^{−N/τ})` com r²=0,92, resid_max 0,0174 (inclui o overshoot,
que nenhuma forma monotônica pega); **(A, τ) degeneram na janela de 1100
ciclos — só a TAXA A/τ = 8×10⁻⁵/ciclo identifica** (log-creep fita igual,
r²=0,91; a forma escolhida é a NOMEADA pelos autores).

## 3. Pacote (grupo novo `YANG_2023_AME`, MÍNIMO — regra D-AB)

`pack:"" · emb_um=32 · N_emb=17000`. Grade 3×3: **6 de 9 células fecham**
(a crista da degenerescência); célula por centralidade (3/3 vizinhos) +
pior perna (0,57×). Contagem: 2 fitados com degenerescência DECLARADA
(efetivamente 1 = a taxa regredida).

Sandbox: 0,3875/0,4654/0,1139 → **0,0285/0,0388/0,0103 — FECHA** (0,57×/0,39×/0,41×).

## 4. Estatuto — declarado ANTES

Fechando pelo canônico, a declaração de escopo SAI (K6, prova preservada) com
a nota honesta: **o escopo cai PARA ESTA JANELA/CARGA** — 1 curva, 1100
ciclos, embedment dominante; a extrapolação viscoelástica de longo prazo
segue não-validada (o alvo A satura no bound = o dado não contém a
saturação). A fonte YANG_2023_AME entra no censo com 1/1.

## 5. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo ao dígito | 0,0285/0,0388/0,0103 pelo canônico |
| **G2** | isolamento | Δ=0 exato fora da fonte no re-stamp (o grupo novo casa só o cid `yang2023ame_axial`); fingerprint único nos 210 |
| **G3** | censo | 165 → **166/205 (81 %)** · declaradas 13 → 12 |
| **G4** | sincronização | retirada K6 · triagem · docs vivos · aging · HTML |

## Estado

EXECUTADO 2026-08-20 (18:2x-18:5x): G1 ao digito (0,0285/0,0388/0,0103 — FECHA), G2 isolamento exato (so a curva no diferencial) fingerprint 245dc93087d1 nos 210, G3 censo 165->166/205 (81%) · declaradas 13->12 · fontes 100% 15->16, G4 sincronizado (retirada K6 com o estatuto honesto: escopo cai para esta janela/carga).
