# Estudo de Variáveis · Item 1 — Assentamento gateado por amplitude (UNIFICAÇÃO ρ = A_F/F₀)

**Data:** 2026-07-08 · **Status:** DESIGN (aguarda aprovação do professor para TDD)
**Origem:** escalada da campanha /converge-model (convergiu iter 6; resíduo A_F com fretting
3× falsificado — o sinal do resíduo é OPOSTO ao fretting: menos amplitude ⇒ MENOS perda).

## 1. A leitura do dado (a variável nomeada pelos números)

Decomposição fast (≤100 cyc) / slow dos DOIS sweeps do Liu2017 (M12, mesmas superfícies):

- P₀-sweep (A_F=10 fixo): fast = 0.168 / 0.090 / 0.053 @ F₀ 15/18/21 kN
- A_F-sweep (F₀=18 fixo): fast = 0.033 / 0.056 / 0.097 / 0.134 @ A_F 7.5/8.75/11.25/12.5 kN

**Lei única:** fast ∝ (A_F/F₀)^q com **q = 3.4** — pares: 3.42, 3.43 (P₀-sweep) e 3.43, 3.07,
2.19* (A_F-sweep; *outlier no ponto 11.25). Cinco leituras independentes, quatro em ±5%.
Consistência cruzada: o ponto compartilhado (F₀=18, A_F=10) interpola exato entre os vizinhos
do A_F-sweep (0.090 entre 0.056 e 0.097). A cauda lenta tem expoente ruidoso (~1.3, faixa
larga — valores 0.015–0.031 no piso da digitização): fora do escopo inicial.

## 2. A mudança de VARIÁVEL (não constante)

**Hoje:** o reservatório de assentamento é amplitude-CEGO e a dependência de F₀ é modelada
como "pré-conformação de aperto" `S_p = (p_ref/p_init)^emb_conform_exp` (duas variáveis:
`emb_conform_exp` + a nova amplitude que o resíduo A_F pedia).

**Proposta:** UMA variável nova — a amplitude relativa cíclica — substitui ambas no eixo axial:

```
rho = F_ax_amp / F_0_init                (adimensional, fixa por run — sem feedback)
S_rho = min(1, (rho / rho_ref)^q_amp)    (fator do reservatório consumível)
delta_target_emb = emb_depth · S_rho     (no canal axial)
```

- `q_amp` ≈ 3.4 (LIDO de 5 pares, 2 sweeps) — física: plasticidade cíclica/shakedown de asperezas.
- `rho_ref` = âncora per-rig (input): ρ no qual o reservatório pleno é consumido (Liu2017:
  ~0.67 = 10/15, o ponto de maior perda observado com S≈1).
- Default `q_amp = 0` ⇒ S=1 exato (inerte, bit-identical). Campo novo + wiring no
  `EmbeddingLoss` via um fator análogo ao `embedding_conformance_factor` (mesmo padrão).

**Ganho de parcimônia (o teste decisivo):** re-rodar o ground-fit axial §4.14a-rev com
S_ρ no lugar de `emb_conform_exp` — expectativa: MAE igual/melhor no P₀-sweep **e** fecha o
resíduo do A_F-sweep (0.033–0.062) com UMA variável a menos. Se confirmar, `emb_conform_exp`
vira caso-particular reinterpretado (a "pressão de aperto" era a amplitude relativa o tempo
todo — em A_F fixo, F₀ maior = ρ menor).

## 3. Gates pré-declarados

- **G1 (unificação):** ground-fit refeito com {emb_cap, N_emb, C_creep, q_amp, exp_slow}
  (mesmo nº de constantes, `emb_conform_exp` removida) ⇒ P₀-sweep MAE ≤ 0.005 do atual (0.0033)
  **e** A_F-sweep médio ≤ 0.02 (hoje 0.035, cases 0.005–0.062).
- **G2 (forma):** resíduo do A_F-sweep sem tendência monotônica em A_F (o gap §4.6 fecha).
- **G3 (não-regressão):** default inerte bit-identical (teste); transversal intocado
  (ρ usa F_ax — em θ=π/2, F_ax≈0 ⇒ S=min(1,0)=... definir S=1 quando ρ=0 p/ compat ✓);
  suite completa verde.
- **G4 (identificabilidade):** q_amp vs emb_cap sem vale degenerado (padrão overfit-battery).

## 4. Fora de escopo (registrado)

Cauda lenta em ρ (expoente ruidoso — só com dado melhor); transversal (settling transversal
não mostrou déficit de amplitude nos fits); interação com `emb_conform_exp` em rigs SEM
sweep de amplitude (manter a variável antiga disponível; adoção por rig com o dado que tiver).
