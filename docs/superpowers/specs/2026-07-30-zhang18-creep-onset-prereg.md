# Prereg — creep com onset per-par no ZHANG_2018 (deriva tardia, alvo 1)

**Data:** 2026-07-30 · **Store baseline:** `3546e6745448` · régua **D1**
(limites efetivos por fonte via `limite_sres`). Gates IMUTÁVEIS depois de
escritos. Execução por delegação (mandato 2026-07-30).

## 0. Origem do candidato (cadeia de evidência)

1. O re-run do D2′ com teto único mostrou que o σ_res das curvas longas é
   dependente do comprimento e nomeou o cluster de **deriva tardia**
   (`cm_d2linha_resultado.md`).
2. `deriva_tardia_probe.py` (store, zero sim): o resíduo da cauda é
   **positivo e crescente** (modelo satura, dado segue caindo);
   ZHANG_2018 tem taxa tardia **identicamente nula** porque a config adotada
   zera o creep (`C_creep=0.0`) — o modelo é "embedding e mais nada".
3. A forma **não é nova**: `δ_creep = C·F₀·ln(t/t₀+1)` já está no engine e
   `t_0` é campo per-par ("onset viscoelástico, lível do joelho"). Em ciclos:
   `A·ln((N+N₀)/(n₀+N₀))` com `N₀ = t_0·freq`. Com N₀ pequeno a lei é
   front-loaded; foi provavelmente por isso que o creep foi zerado na adoção
   original — o remédio certo era o onset, não o desligamento.
4. `deriva_tardia_premeasure.py` (analítico, superposição declarada):
   * **LIU_2016 morre no F1** — nenhum (A,N₀) do grid [10, 3·10⁶] mantém as
     irmãs (af*, m45/m50nm) dentro de +0,01. O candidato de constantes
     compartilhadas está FALSIFICADO para essa fonte no premeasure (custo:
     zero sims). A fila-4 do liu2016 permanece form-limited com diagnóstico
     mais fino (a cauda precisa de algo que o creep compartilhado não dá).
   * **ZHANG_2018 viável = livre**: `A = 0.01261`, `N₀ = 562` ciclos.

## 1. Leitura congelada (não re-otimizar na execução)

* `A = 0.01261` (fração de F₀ por unidade de ln), `N₀ = 562` ciclos.
* Split mecânico (`calibration.holdout`, critério de RESOLUÇÃO DO DADO):
  * LÊ: `zhang18_fig2_test4_20kN_5e5cyc` (única com ≥4 pontos além de 200k).
  * HELD (8): fig2 test1/test2/test3, fig13 14/20/26 kN, fig16 com/sem locker.
* Mapa para constantes do engine: `t_0 = N₀/freq` (freq lida do config do
  runner na execução); `C_creep` calibrado por UMA sim de escala em test4 +
  UMA sim de verificação de linearidade (G1). Nada mais muda na config
  (`K_archard=0`, `k_wear_spec=0`, `tr_loose_gain=0`, `N_emb=150`,
  `emb_um=2.0996` ficam).

## 2. Previsões congeladas (analíticas; a execução as confere)

| curva | papel | σ antes | σ prev | MAE prev | mx prev |
|---|---|--:|--:|--:|--:|
| fig2_test4_20kN_5e5cyc | LÊ | 0.0294 | **0.0070** | 0.0254 | 0.0466 |
| fig13_14kN | HELD | 0.0297 | **0.0126** | 0.0295 | 0.0601 |
| fig13_20kN | HELD | 0.0242 | 0.0082 | 0.0225 | 0.0323 |
| fig13_26kN | HELD | 0.0186 | 0.0116 | 0.0288 | 0.0442 |
| fig16_with_locker | HELD | 0.0091 | 0.0185 | 0.0309 | 0.0680 |
| fig16_without_locker | HELD | 0.0263 | **0.0098** | 0.0236 | 0.0445 |
| fig2_test1_20kN_1e3cyc | HELD | 0.0072 | 0.0091 | 0.0225 | 0.0313 |
| fig2_test2_20kN_1e4cyc | HELD | 0.0121 | 0.0105 | 0.0305 | 0.0462 |
| fig2_test3_20kN_1e5cyc | HELD | 0.0244 | 0.0091 | 0.0250 | 0.0471 |

Em negrito: as 3 curvas da fila-26 (form-limited) desta fonte — todas
previstas DENTRO do tripé efetivo (σ ≤ 0.0250 · MAE ≤ 0.05 · mx ≤ 0.10).

## 3. Gates (imutáveis)

* **G1 — linearidade do mapa A→C:** sim de escala com `C_test` e `t_0=N₀/freq`
  em test4 → `A_test` medido do Δcum de creep; `C' = C_test·A/A_test`;
  2ª sim com `C'` tem de reproduzir `A` dentro de ±10 %. Falha ⇒ o canal não
  é linear em C nesta região ⇒ **INCONCLUSIVO** (instrumento, não mecanismo).
* **G2 — superposição válida:** para CADA uma das 9 curvas, σ_sim vs σ_prev
  concordam em ±0,005. Falha em >2 curvas ⇒ **INCONCLUSIVO** (a previsão
  analítica não descreve o engine; nada se conclui do mecanismo).
* **G3 — generalização (o veredito que importa):**
  `veredicto_generalizacao(σ_antes, σ_sim, split, tol=+0,01)` sobre as 8 HELD
  ⇒ `generaliza=True` exigido (mediana não sobe E <metade piora).
* **G4 — acervo:** nenhuma das 9 curvas piora > +0,01 em NENHUMA perna
  (σ, MAE, mx) na simulação real.
* **G5 — fechamento:** as 3 curvas da fila fecham o tripé efetivo na sim
  real. (G3+G4 passando e G5 falhando = adoção ainda assim NEGADA — o
  candidato prometia fechar a fila; registrar como PARCIAL.)

**PASSA = G1∧G2∧G3∧G4∧G5 ⇒ adotar por delegação** (atualiza `ZHANG_2018`:
`C_creep=C'`, `t_0=N₀/freq`, procedência "onset lido do resíduo (L24),
held-out 8 curvas, prereg 2026-07-30"), re-carimbar o store da fonte,
regenerar reports, atualizar fila/docs no MESMO commit.

## 4. Falsificadores declarados

* **F1 (já executado no premeasure):** sem (A,N₀) viável ⇒ morto —
  foi o destino do LIU_2016.
* **F2:** G3 reprova (held não generaliza) ⇒ o número lido em test4 é
  sobreajuste de uma curva — **FALSIFICADO** como constante per-par; conta
  para o requisito (b) da regra de parada.
* **F3:** G2 reprova ⇒ INCONCLUSIVO (não conta para (b)).
* **F4:** G5 reprova com G3/G4 ok ⇒ PARCIAL — melhora sem fechar; não adota,
  registra as frações.

## 5. O que este prereg NÃO cobre

* liu2016 (morto no F1 aqui; a cauda dele exige outro canal — a fonte é um
  estudo de DESGASTE com medições próprias de wear; candidato futuro deve
  ancorar no wear publicado, não no creep).
* li2022ti (canal de fretting 94 %, força axial — outra família).
* Qualquer mudança de forma no engine (nenhuma: só constantes per-par de um
  canal existente).
