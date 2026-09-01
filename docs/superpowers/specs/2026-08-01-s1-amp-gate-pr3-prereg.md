# PR-3 — gate de regime de amplitude nos relógios de ESTÁGIO I (forma B do N₉₅)

**2026-08-01** · continuação autorizada ("continue") do Bloco 1; ramo B
declarado no prereg `2026-07-31-liu2025-n95-forma-prereg.md` após o
candidato A (campos existentes) ser falsificado no G1 (1/6; o dado exige
expoente efetivo ~11 de N₉₅ sobre amplitude, o gate de slip existente dá
~2–4). Padrão do repo: forma nasce **default-inerte** (OFF = bit-idêntico),
adoção é gateada e per-rig. Gates escritos ANTES do código.

## A forma

Física: transição regime-parcial → gross-slip. Abaixo de uma amplitude de
transição δ*, os relógios de estágio I (bedding E creep de interface)
quase param — o assentamento vibração-dirigido precisa de escorregamento
macro; acima, correm à taxa plena. O que o dado exige (N₉₅ 850× de span em
3,2× de amplitude) é a NITIDEZ dessa transição, que nenhum campo existente
fornece (medido no G1-A).

Implementação (3 campos novos em `JointMaterial`, TODOS default-OFF):

- `s1_amp_gate_dref` (m; **0.0 = OFF exato**, gate ≡ 1)
- `s1_amp_gate_p` (nitidez Hill; só lido se dref > 0; default 8.0)
- `s1_amp_gate_floor` (taxa remanescente sub-limiar ∈ [0,1); default 0.0)

`g(δ) = floor + (1 − floor) · δ^p / (δ^p + δ*^p)` com δ = `delta_amp`
(modo deslocamento; `delta_amp is None` ⇒ g = 1, modo força intocado).
`g` multiplica **só o incremento `d_delta`** de `EmbeddingLoss` (linha do
reservatório, após o alvo) e de `CreepLoss` (após a conformância) — `dF_0`
e `dE` derivam de `d_delta` nos dois ⇒ conservação preservada por
construção. Nenhum outro mecanismo é tocado (wear/loosening já têm
`slip_onset_W`).

## Gates (imutáveis)

- **G0 (inércia)**: com os defaults, curva bit-idêntica (array-equal) num
  caso com embedding+creep ativos; suíte completa verde sem regressão.
- **G1 (alcance na âncora)**: fitando **≤3 números** (δ*, p, floor) na
  **D-N da Fig. 4 (6 pontos M16)** — e NADA olhando as curvas da fila —,
  o N₉₅ do modelo fica dentro de **3×** do dado em **≥4 das 6** amplitudes
  (candidato A: 0/6; melhor ponta isolada 1,34×).
- **G2 (held-out)**: com os números do G1 congelados, as 4 da fila
  (amp0p25/0p3/0p8/fig2) em janela COMPLETA (sem n_cap): soma dos MAE cai
  ≥20 % e nenhuma piora >+0,01 em qualquer perna.
- **G3 (nenhum caso pior)**: as 7 curvas da fonte com estatuto (incl.
  E2/fadiga) não pioram >+0,01 em nenhuma perna, janela completa. Fora da
  fonte: nada muda (campos per-rig no cfg adotado; engine OFF por default).
- **G4 (procedência)**: δ*/p/floor com origem = fit na D-N do paper
  (6 pontos, dado independente da fila), documentados no cfg (`prov`).
- **G5 (sincronia)**: adoção ⇒ fingerprint muda ⇒ batch re-stamp uniforme
  + `exemplo_m12_sintetico` direto + censo/_VIVAS/docs/páginas/testes no
  mesmo commit. Ramo INCONCLUSIVO/reversão: qualquer gate falha ⇒ rollback
  dos cfg (a forma fica no engine, inerte — igual fat_ramp/graded_scrit).

## Previsão registrada (falsificável)

Com δ* ≈ 0,5–0,6 mm, p ≈ 6–10, floor ≈ 1/100–1/20: N₉₅(0,25) sobe para a
casa de 10⁴ (creep gateado ao floor) e N₉₅(0,8) desce para <60 (gate ≈ 1 +
reservatório atual). Risco declarado: o 0,6 mm (dado 460) senta EXATAMENTE
na transição — é ele que vai decidir p.
