# Prereg — re-atribuição da cauda do LIU_2016: fretting de flanco (L1) no lugar de "creep alto"

**Data:** 2026-07-30 · **Baseline:** store `b6ed722b1c61` · régua D1
(`limite_sres`; LIU_2016 usa o global 0,0250). Gates imutáveis; execução por
delegação (mandato 2026-07-30).

## 0. Cadeia de evidência (tudo medido hoje)

1. `deriva_tardia_probe.py`: cauda do LIU_2016 = **creep 100 %** no modelo,
   entregando só 45–64 % da queda do dado — e o F1 do premeasure provou que
   NENHUM `(C, t_0)` compartilhado conserta sem quebrar as irmãs.
2. **Nota de aparato (o dado manda):** rig axial FORCE-mode (SWJTU, mesma
   família do li2022ti); os autores atribuem a cauda lenta a **fretting wear
   nos filetes** (SEM/EDX; delaminação no 1º filete) e *"no creep language
   anywhere in the paper"*. O modelo carrega a cauda com a lei ERRADA.
3. O engine JÁ tem a forma certa: canal **L1 de flanco**
   (`flank_wear_on`/`k_wear_flank`/`flank_amp_exp`, força-modo apenas,
   rate ∝ p_flank·A_F^exp) — adotado no li2022ti com `flank_amp_exp=1.5`
   (âncora Liu 2020: 1,5–1,6).
4. **Scan analítico da família** (e′ = e + λ·creep_rm − B·(F_ax/10kN)^q·∫r^k dn,
   restrição acervo +0,01, held fora de tudo): ótimo viável em
   **λ=0 · q=1,5 · k=1** — exatamente a forma L1 (p_flank ∝ r¹, expoente
   1,5), **com o creep atual mantido**. 12 não-held fecham o tripé; held
   `m40nm` fecha; held `fig7_run2` (5×10⁶) NÃO fecha em janela cheia.
5. **fig7_run2**: o dado RECUPERA +0,7 pt entre ~2,2–4×10⁶ (inset da Fig. 7;
   atribuição dos autores: debris de wear abrasivo empilhando e escorando a
   junta — terceiro corpo). O engine é monotônico por construção (todo
   mecanismo perde) ⇒ a feição é **out-of-model por física documentada**,
   mesma classe dos trims de fratura. Com trim em 2,2×10⁶ + família:
   **fecha** (sd 0,0194 · mae 0,0375 · mx 0,0653), robusto ao corte
   (2,0/2,2/2,5×10⁶ idênticos no veredicto); sem a família, o mesmo trim NÃO
   fecha (sd 0,0303) — as duas peças são separáveis e ambas necessárias.

## 1. Leitura congelada

* Família: **B = 6,0e-8** por unidade de (F_ax/10 kN)^1,5 por ∫r dn ·
  **λ = 0** (C_creep=1,901e-11 do LIU_2016 fica) · **q = 1,5 fixo por âncora
  KB** (não fitado aqui).
* Config alvo (entry `LIU_2016` apenas; `LIU_2016_mos2` NÃO muda):
  `flank_wear_on=1.0`, `flank_amp_exp=1.5`, `k_wear_flank=K'` (mapa linear
  B↔K por 2 sims em fig7_run1, G1), e `per_case` novo:
  `{"run2": {"trim_n_max": 2200000.0}}` com a procedência de debris acima.
* Split mecânico (identidade do dado): LÊ = {fig7_run1 (réplica-1ª),
  fig9a_m30nm (menor nível da varredura de torque M0=30 N·m)} ·
  HELD = {fig7_run2 (na janela trimada), fig9a_m40nm}.

## 2. Previsões congeladas (σ′ analítico; execução confere)

| curva | papel | σ antes→prev | MAE prev | mx prev |
|---|---|---|--:|--:|
| fig9a_m30nm (fila) | LÊ | 0.0281→**0.0230** | 0.0424 | 0.0697 |
| fig7_run1 (fila) | LÊ | 0.0281→**0.0229** | 0.0406 | 0.0661 |
| fig9a_m40nm (fila) | HELD | 0.0269→**0.0225** | 0.0482 | 0.0743 |
| fig7_run2 @trim 2,2e6 (fila) | HELD | 0.0328→**0.0194** | 0.0375 | 0.0653 |
| fig9a_m35nm | acervo | 0.0207→0.0165 | 0.0418 | 0.0601 |
| fig9a_m45nm | acervo | 0.0175→0.0144 | 0.0447 | 0.0627 |
| fig9a_m50nm | acervo | 0.0160→0.0132 | 0.0366 | 0.0521 |
| af7p5kn | acervo | 0.0077→0.0091 | 0.0123 | 0.0424 |
| af8p75kn | acervo | 0.0101→0.0082 | 0.0220 | 0.0416 |
| af10kn | acervo | 0.0153→0.0103 | 0.0266 | 0.0407 |
| af11p25kn | acervo | 0.0164→0.0115 | 0.0271 | 0.0402 |
| af12p5kn | acervo | 0.0165→0.0148 | 0.0309 | 0.0461 |
| fig13a_dry | acervo | 0.0237→0.0182 | 0.0343 | 0.0569 |
| fig13a_mos2 | acervo | **não muda** (config separada; 1 sim de controle confere Δ=0) |

Previsto: **13/13 da config fecham o tripé** (mos2 já fechava) ⇒ fonte
**14/14**, fila −4.

## 3. Gates (imutáveis; uma execução)

* **G1** linearidade B↔K em fig7_run1 (2 sims): 2ª reproduz B em ±10 %.
* **G2** superposição: σ_sim vs σ_prev ±0,005 por curva; >2 fora ⇒
  INCONCLUSIVO (instrumento).
* **G3** generalização: `veredicto_generalizacao` nas 2 held (m40nm,
  run2@trim), tol +0,01 ⇒ `generaliza=True` exigido.
* **G4** acervo: nenhuma das 13 curvas da config piora >+0,01 em nenhuma
  perna; mos2 (controle) Δσ ≤ 0,001.
* **G5** fila: as 4 fecham o tripé efetivo na sim real (run2 na janela
  trimada declarada).

**PASSA = G1∧G2∧G3∧G4∧G5 ⇒ adotar por delegação** (campos acima na entry
`LIU_2016` + `per_case` run2; procedência: "re-atribuição fretting L1 —
mecanismo dos próprios autores (SEM/EDX), forma KB li2022ti/Liu2020
exp=1,5, B lido do resíduo (L24), held-out 2 curvas; trim run2 por
recuperação de debris (Fig. 7 inset, terceiro corpo, out-of-model
documentado); prereg 2026-07-30") + re-carimbo total + reports + docs no
mesmo push. A publicação de run2 SEMPRE cita as duas janelas.

## 4. Falsificadores

* **F2** G3 reprova ⇒ B lido é sobreajuste das leituras — FALSIFICADO como
  constante per-par.
* **F3** G2 reprova ⇒ INCONCLUSIVO (superposição não descreve o engine
  aqui; o acoplamento F₀→p_flank é mais forte que o assumido).
* **F4** G5 reprova com G3/G4 ok ⇒ PARCIAL; não adota; registra frações.
* O trim de run2 NÃO é gate-dependente: ou a feição de debris está no dado
  (está — inset publicado) ou não; reprovar os gates não o invalida nem o
  valida — ele só entra na adoção se a adoção acontecer.
