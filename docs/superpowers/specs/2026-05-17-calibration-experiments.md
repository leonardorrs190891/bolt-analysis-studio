# Calibração experimental do modelo energético — sequência mínima

**Data:** 2026-05-17
**Autor:** Prof. Leonardo Rosa Ribeiro da Silva (planejamento experimental)
**Status:** Plano. Antecede a implementação de campanha de bancada.
**Relacionado:** `2026-05-16-two-factor-loosening-theory.md` §12 (teoria); `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (código).

---

## 0. Objetivo

Calibrar todas as constantes não-geométricas do modelo `DynamicStiffnessAnalyzer` com o **mínimo de experimentos físicos** distintos. Cinco ensaios, executados em sequência por razões físicas (alguns mecanismos "consomem" estado e contaminam outros), cobrem o conjunto completo de parâmetros.

---

## 1. Constantes a calibrar

A geometria do parafuso (E, A_s, L_eff, d_2, pitch, r_bearing) é conhecida de catálogo/desenho. Existem **dois conjuntos** de constantes a calibrar:

### 1.1. Constantes físicas (universais para o material/par tribológico)

| Símbolo | Significado | Onde aparece no código |
|---------|-------------|------------------------|
| `k_j_init` | Rigidez axial inicial do joint a F_0_nominal | `JointMaterial.k_j_init` |
| `α_GW` | Expoente Greenwood-Williamson, `k_j_ax = k_j_init·(F_0/F_init)^α` | `JointMaterial.alpha_GW` |
| `μ_thread` | Atrito no filete | `JointMaterial.mu_thread` |
| `μ_bearing` | Atrito no bearing (head/nut ↔ flange) | `JointMaterial.mu_bearing` |
| `K_archard` | Coeficiente de Archard adimensional | `JointMaterial.K_archard` |
| `emb_depth` | Embedding plástico assintótico | `JointMaterial.emb_depth` |
| `N_emb` | Constante de tempo do embedding (ciclos) | `JointMaterial.N_emb` |
| `C_creep` | Coeficiente de creep logarítmico | `JointMaterial.C_creep` |

### 1.2. Constantes de ajuste (tuners) — direção-dependentes

O modelo expõe **multiplicadores 1.0-por-default** que o usuário ajusta após calibração contra dados reais. Permitem flexibilidade pra cobrir casos onde a física pura sub- ou super-prediz. **Calibrados separadamente para carregamento axial e transversal (cisalhante).**

| Tuner | Default | Aplicado em | Direção |
|-------|---------|-------------|---------|
| `k_emb_scale` | 1.0 | rate de embedding | agnóstico |
| `k_creep_scale` | 1.0 | rate de creep | agnóstico |
| `k_wear_scale_ax` | 1.0 | rate de wear sob loading axial | axial |
| `k_wear_scale_tr` | 1.0 | rate de wear sob loading transversal | transversal |
| `k_loose_scale_ax` | 1.0 | rate de loosening sob loading axial | axial |
| `k_loose_scale_tr` | 1.0 | rate de loosening sob loading transversal | transversal |
| `Phi_ax_correction` | 1.0 | correção em Φ axial | axial |
| `Phi_tr_correction` | 1.0 | correção em Φ transversal | transversal |

Para loading combinado com ângulo θ entre eixo e direção da carga, o tuner efetivo é blend cosseno-quadrado:
```
k_eff(θ) = k_ax · cos²θ + k_tr · sin²θ      (mesma forma do círculo de Mohr)
```

**Total:** 8 constantes físicas + 8 tuners = 16 parâmetros. Mas 6 dos tuners são opcionais (default 1.0 funciona se a física casa com seu material). Em prática, **calibra-se 8 físicas + ajusta-se 1-3 tuners** para encaixar dados experimentais.

---

## 2. Sequência de experimentos (axial + cisalhante, ordem crítica)

A ordem importa porque alguns mecanismos consomem estado:
- **Embedding** é irreversível — uma vez ativado, não volta. Deve ser caracterizado **antes** de qualquer cycling agressivo.
- **Loosening rotacional** danifica o filete — deve ser **último** em cada track.
- **Creep** é função do tempo e da história de carga — fica **logo após embedding**, antes do danificação.
- **Tracks axial e transversal** podem ser executados em sequência no mesmo sample (com cuidado), ou em samples gêmeos (preferível).

Sequência completa (8 experimentos em 2 tracks + 1 cross-cutting):

```
Cross  Exp 1  (estático multi-F₀ axial)  →  k_j_init, α_GW            (não-destrutivo)
Cross  Exp 2  (hold longo)               →  C_creep                    (direção-agnóstico)
Cross  Exp 3  (sub-slip embedding)       →  emb_depth, N_emb           (direção-agnóstico)

Track AXIAL:
  Exp 4A (axial cycling, F < F_sep)      →  Phi_ax_correction          (valida Fator 1 axial)
  Exp 5A (axial cycling, F > F_sep)      →  K_archard, k_wear_scale_ax,
                                              k_loose_scale_ax           (DESTRUTIVO)

Track TRANSVERSAL (CISALHANTE):
  Exp 4T (slip-onset transversal sweep)  →  μ_bearing, Phi_tr_correction
  Exp 5T (Junker test full transversal)  →  μ_thread, k_wear_scale_tr,
                                              k_loose_scale_tr            (DESTRUTIVO)

Posterior:
  Exp V1-V4 (cargas combinadas, R-factor) →  validação cruzada do modelo
```

**Cross-cutting** (Exp 1-3): independente da direção principal de carga. Calibra constantes universais.

**Track Axial** (Exp 4A-5A): aplica F_ext alinhada ao eixo do parafuso. Calibra tuners "_ax".

**Track Transversal** (Exp 4T-5T): aplica F_ext perpendicular ao eixo (= cisalhante). Calibra tuners "_tr". Esta é a direção do Junker test clássico.

A direção axial **separa** as flanges (F_sep crítico); a transversal **desliza** elas relativas (slip threshold crítico). São dois regimes de falha distintos do modelo two-factor.

---

## 3. Experimento 1 — Carga estática multi-pré-carga

**O que mede:** `k_j_init` e `α_GW` (= a curva k_j(F₀) sobre o intervalo operacional).

### 3.1. Setup

- Bancada com atuador axial (servo-hidráulico ou prensa de parafuso) capaz de aplicar F_ext entre flanges.
- Strain gauge no shank do parafuso (mede ε_bolt).
- LVDT ou capacitive gauge entre as faces das flanges (mede δ_gap).
- Célula de carga em série com o atuador.
- Quatro pré-cargas: F_0 ∈ {25, 50, 75, 100 % do nominal}.
- Lubrificação consistente em todas as repetições.

### 3.2. Procedimento

Para cada F_0:
1. Pré-carregar o parafuso ao valor alvo (torque + verificação por strain gauge).
2. Aplicar F_ext quasi-estaticamente, 0 → 1.5 × F_sep_esperado, em rampa lenta (≥ 30 s).
3. Registrar simultaneamente F_ext, ε_bolt, δ_gap em ~200 pontos.
4. Descarregar ao mesmo ramp rate (verifica histerese = embedding/atrito presente).

### 3.3. Análise

Para cada F_0, plotar `δ_gap vs F_ext` e `ε_bolt vs F_ext`:

```
Pré-separação (F_ext < F_sep):
  slope(δ_gap)   = (1 − Φ)/k_j         → Φ e k_j_local
  slope(ε_bolt)  = Φ / (E·A_s)         → Φ (validação cruzada)

Pós-separação (F_ext ≥ F_sep):
  slope(δ_gap)   = 1/k_b               → valida k_b
  slope(ε_bolt)  = 1/(E·A_s)           → valida A_s

Kink em F_sep    = F₀ / (1 − Φ)       → F₀ se Φ conhecido (validação cruzada da pré-carga aplicada)
```

Com `k_j(F₀)` extraído nos 4 níveis, ajustar lei Greenwood-Williamson:

```
log(k_j) = log(k_j_init) + α_GW · log(F₀ / F_0_nom)
```

Regressão linear no log-log dá α_GW (slope) e k_j_init (intercept).

### 3.4. Critério de aceitação

- Φ extraído de ε_bolt e δ_gap deve coincidir dentro de 5 % (validação cruzada interna).
- Pós-sep slope de δ_gap deve dar k_b dentro de 3 % do valor analítico E·A_s/L_eff.
- Coeficiente de regressão R² do fit log-log para k_j(F₀) > 0.95.

### 3.5. Duração estimada

~30 min por F_0, 4 níveis + repetição = **4 horas**. Pode ser feito em uma manhã.

---

## 4. Experimento 2 — Cycling sub-slip (embedding apenas)

**O que mede:** `emb_depth` (assintota) e `N_emb` (constante de tempo).

### 4.1. Setup

- Mesma bancada do Exp 1, agora com capacidade de cycling transversal de **baixa amplitude**.
- Strain gauge no parafuso (monitora F_0 em tempo real).
- Termopar próximo às interfaces (descartar mudança térmica que confunde com creep).
- F_0 inicial = nominal (mesma referência do Exp 1).

### 4.2. Procedimento

1. Pré-carregar a F_0_nominal, esperar estabilizar 5 min.
2. Aplicar F_tr cíclico com amplitude **abaixo do threshold de slip**: F_tr_amp < 0.46 · μ_estimado · F_0 / 2 (fator de segurança 2 ×).
   - Para F_0 = 50 kN, μ estimado 0.15: F_slip ≈ 3.45 kN → usar F_tr_amp ≤ 1.5 kN.
3. Frequência 1–5 Hz (mantém baixa pra desacoplar de creep dinâmico).
4. Rodar 200–500 ciclos, monitorando F_0(N).
5. Esperar 10 min pós-test pra discriminar creep adicional.

### 4.3. Análise

`F_0(N)` deve seguir:
```
F_0(N) = F_0_init − k_b · δ_emb,∞ · (1 − exp(−N/N_emb))
```

Subtrair a parcela de creep linear (do Exp 3 ou estimativa preliminar) antes do fit. Ajustar duas constantes:

```
δ_emb,∞  = (F_0_init − F_0_∞) / k_b      ← assintota
N_emb    = ciclo onde F_0 cai 63 %·(F_0_init − F_0_∞)   ← time constant
```

### 4.4. Critério de aceitação

- 90 % da queda de F_0 deve ocorrer em N < 200 ciclos (validação de saturação).
- N_emb tipicamente 20–80 ciclos. Fora dessa faixa → ou amplitude alta demais (slip contaminando) ou material atípico.
- Verificação de ausência de slip: medir histerese em F_tr × δ_tr — área < 5 % da loop com slip clara.

### 4.5. Duração

200 ciclos a 5 Hz = 40 s + setup 20 min = **30 min**.

---

## 5. Experimento 3 — Hold longo (creep)

**O que mede:** `C_creep`.

### 5.1. Setup

- Após Exp 2 (embedding já saturado).
- Bolt mantido em pré-carga estática, sem cycling.
- Strain gauge contínuo, datalogger a 0.1 Hz (uma medida por 10 s).
- Temperatura controlada ou monitorada com correção térmica.

### 5.2. Procedimento

1. Estado inicial: F_0 estabilizado pós-Exp 2.
2. Manter por **24–72 horas**.
3. Sem perturbações mecânicas.
4. Registrar F_0(t) continuamente.

### 5.3. Análise

`F_0(t)` segue Norton-Bailey:
```
F_0(t) = F_0_init − k_b · C_creep · F_0_init · log(t/t_0 + 1)
```

Plot `(F_0_init − F_0(t)) / (k_b · F_0_init) vs log(t)` — slope = C_creep.

### 5.4. Critério de aceitação

- Linearidade em log-time R² > 0.90.
- Sem step changes (= eventos não-creep contaminando).
- C_creep tipicamente 1e-12 a 1e-10 (depende da geometria; faixa larga).

### 5.5. Duração

**24 horas mínimo** (72h preferível para boa resolução em log-time).

---

## 6. Experimento 4T — Slip-onset sweep transversal (μ_bearing, Φ_tr_correction)

**O que mede:** `μ_bearing` via Pai-Hess `F_slip = 0.46 · μ · F_0` + ajusta `Phi_tr_correction`.

### 6.1. Setup

- Bancada com cycling transversal, agora com **F_tr crescente**.
- Strain gauge no parafuso (F_0 instantâneo).
- LVDT transversal (δ_tr).
- F_0 = nominal, do estado pós-Exp 3.

### 6.2. Procedimento

1. Iniciar com F_tr_amp = 1 kN (claramente sub-slip).
2. Aumentar F_tr_amp em steps de 0.5 kN a cada 50 ciclos.
3. Para cada step: registrar histerese (loop F_tr × δ_tr).
4. **Onset de slip** = primeiro step onde a histerese deixa de ser elástica (area > 1 % do triangulo elástico de loading).
5. Parar quando F_0 começa a cair perceptivelmente (= já entrou em regime de loosening; Exp 5 lida com isso).

### 6.3. Análise

Identificado F_tr_slip,onset:
```
μ_bearing = F_tr_slip,onset / (0.46 · F_0)
```

Sensibilidade: se μ verdadeiro é 0.15, F_slip = 0.46×0.15×50 = 3.45 kN. Step de 0.5 kN dá precisão ±15 %. Reduzir step para 0.2 kN se mais precisão for necessária.

### 6.4. Critério de aceitação

- Onset de slip claro (transição visível na histerese, não gradual).
- μ_bearing tipicamente 0.08–0.20 para aço-aço sem lubrificação dedicada.

### 6.5. Duração

50 ciclos × ~10 steps = 500 ciclos a 5 Hz = 100 s + análise = **30 min**.

---

## 7. Experimento 5T — Junker test completo transversal (μ_thread, K_archard, k_loose_scale_tr)

**O que mede:** `μ_thread`, `K_archard`, ajusta `k_wear_scale_tr` e `k_loose_scale_tr`, e valida o modelo completo na direção transversal.

### 7.1. Setup

- Padrão DIN 65151 / Junker test.
- F_tr_amp = 5 × F_slip (claramente acima do onset, pra estar em regime full slip).
- Frequência 12.5 Hz (canônico).
- Strain gauge contínuo.
- LVDT transversal.
- Câmera ou marcador opcional para medir rotação da porca (θ_loose direto).

### 7.2. Procedimento

1. Pré-carregar (F_0 = nominal). Setup fresco se possível, ou aceitar histórico do Exp 4.
2. Aplicar cycling 0 → 5000 ciclos (ou até F_0/F_0_init < 0.5).
3. Registrar F_0(N) continuamente, δ_tr a cada ciclo, marca na porca (se disponível) a cada 500 ciclos.

### 7.3. Análise

Duas regiões da curva F_0(N) dão informações distintas:

**Stage I (regime não-rotacional, primeiros ~30 % da queda):**
- Dominado por wear (Archard) + embedding tardio.
- Slope dá `K_archard`:
  ```
  dF_0/dN = −k_b · K_archard · F_0 · slip_amp / (H · A_contact)
  ```

**Stage II (regime rotacional, após Stage I):**
- Dominado por loose rotacional (Fator 2 ativo).
- Slope dá `μ_thread` indiretamente, via balanço T_loose vs T_resist:
  ```
  T_loose(F_0, F_tr) > T_resist(F_0, μ_thread, μ_bearing)
  ```
  Resolvendo para μ_thread com μ_bearing já conhecido (Exp 4):
  ```
  μ_thread = (T_loose / F_0 − μ_bearing · r_bearing) · 2·cos(α_t)/d₂
  ```

**Validação de θ_loose:** se a porca foi marcada, comparar θ_loose medido com `(2π/p) · ΔF_0_loose / k_b` predito.

### 7.4. Critério de aceitação

- Curva F_0(N) deve ter dois estágios visíveis (Stage I quase linear, Stage II superlinear).
- μ_thread extraído deve estar em 0.10–0.20 (faixa típica).
- K_archard em 1e-5 a 1e-3 (faixa típica, depende da rugosidade).
- Predição θ_loose vs medido dentro de 20 %.

### 7.5. Duração

5000 ciclos a 12.5 Hz = 400 s + setup 30 min + análise 1 h = **2 horas**.

---

## 7A. Experimento 4A — Carga axial sub-separação (Phi_ax_correction)

**O que mede:** ajuste fino de `Phi_ax_correction` em regime axial sem separação. Valida a constitutiva `k_j_ax(F_0)` que veio do Exp 1.

### 7A.1. Setup

- Bancada com cycling axial (atuador axial puro, sem componente transversal).
- F_0 nominal, mesmo do Exp 5T se possível usar sample gêmeo.
- Strain gauge no parafuso, LVDT axial entre flanges.

### 7A.2. Procedimento

1. Pré-carregar a F_0_nominal.
2. Aplicar F_axial cíclica com amplitude **abaixo de F_sep** (típico: F_amp = 0.6 · F_sep).
3. Rodar 500 ciclos a 5 Hz.
4. Medir F_0(N) e a histerese F_ax × δ_ax.

### 7A.3. Análise

Em regime sub-separação puro: nenhum loosening rotacional, nenhum slip. F_0 só cai por embedding tardio + creep (já calibrados). Se F_0 cai **mais** que o predito, há contribuição axial extra → ajustar `Phi_ax_correction > 1` ou `k_loose_scale_ax > 1`.

```
ajuste:
  F_0_medido(N) − F_0_predito_emb+creep(N) = "residual"
  Se residual > 0: aumentar Phi_ax_correction até MAE ≤ 5%
  Se residual < 0: o modelo está sobre-predizendo emb/creep (revisar)
```

### 7A.4. Critério de aceitação

- F_0(N) cai < 1% em 500 ciclos (axial sub-sep é estável).
- Phi_ax_correction final entre 0.8 e 1.2 (perto de 1.0; correção pequena).

### 7A.5. Duração

500 ciclos a 5 Hz = 100 s + setup 20 min = **30 min**.

---

## 7B. Experimento 5A — Carga axial acima da separação (k_archard_ax, k_loose_scale_ax)

**O que mede:** rates de wear e loose sob carga axial dinâmica acima de F_sep.

### 7B.1. Setup

- Mesma bancada do 4A.
- Sample novo se possível (axial fadiga é destrutiva no bolt root).

### 7B.2. Procedimento

1. Pré-carregar a F_0_nominal.
2. Aplicar F_axial cyclica com **F_amp > F_sep** (típico: 1.3 · F_sep) — joint vai abrir e fechar a cada ciclo.
3. Rodar 2000–5000 ciclos a 5 Hz.
4. Monitorar F_0(N) e número de aberturas (eventos onde F_joint = 0).

### 7B.3. Análise

Acima de F_sep, em cada ciclo o joint abre completamente. Modos de perda ativos:
- Wear axial (impacto repetido nas asperezas)
- Loose rotacional pelo Fator 2 axial (componente sin β ≈ 0.04)
- Possível fadiga no bolt root (se F_max bolt > yield × 0.7)

```
Stage I axial (primeiros ~10% da queda):
  dF_0/dN dominado por embedding tardio + wear axial
  Ajustar k_wear_scale_ax se MAE > 10% após emb_depth e K_archard fixos

Stage II axial (restante):
  dF_0/dN dominado por loose rotacional axial
  Ajustar k_loose_scale_ax para casar a curva (tipicamente 0.5-5)
```

### 7B.4. Critério de aceitação

- Loose rotacional axial é tipicamente **muito menor** que transversal (Fator 2 axial é 25× menor). F_0 cai ~30-50% em 5000 ciclos vs <10% em transversal puro com mesma F_amp.
- k_loose_scale_ax > 5 sinal de modelo errado — revisar geometria do filete ou ângulo β.

### 7B.5. Duração

5000 ciclos a 5 Hz = 1000 s + setup + análise = **2 horas**.

---

## 8. Tabela-resumo

| Exp | Direção | Mede | Tuner ajustado | Duração | Destrutivo? |
|-----|---------|------|----------------|---------|-------------|
| 1   | qq      | Carga estática multi-F₀                 | (calibra k_j_init, α_GW) | 4 h     | Não  |
| 2   | qq      | Hold longo (creep)                       | k_creep_scale            | 24–72 h | Não  |
| 3   | qq      | Cycling sub-slip (embedding)             | k_emb_scale              | 30 min  | Não* |
| 4T  | transv. | Slip-onset transversal                   | Phi_tr_correction        | 30 min  | Não  |
| 5T  | transv. | Junker test full                         | k_wear_scale_tr, k_loose_scale_tr | 2 h   | **SIM** |
| 4A  | axial   | Cycling axial sub-separação              | Phi_ax_correction        | 30 min  | Não  |
| 5A  | axial   | Cycling axial acima de F_sep             | k_wear_scale_ax, k_loose_scale_ax | 2 h | **SIM** |

\* Não-destrutivo mas consome o embedding (mecanismo irreversível).

**Total:** 2 samples (um para track transversal, um para axial). **Tempo de bancada:** ~6 horas ativas + 24h de hold passivo. **Sequência completa em 2 dias úteis com 2 setups paralelos**, ou 3 dias se sequencial.

**Mínimo absoluto** (se só dispõe de carregamento transversal/Junker): Exp 1, 2, 3, 4T, 5T → calibra 6 das 8 constantes físicas + 2 dos 6 tuners. O track axial pode ser adicionado depois com sample novo.

---

## 9. Validação posterior (não é calibração)

Depois da calibração, validar o modelo com **diferentes condições** usando um sample novo:

### V1 — Diferente pré-carga
Repetir Exp 5 com F_0 = 0.7 × nominal. Predizer F_0(N) com parâmetros já calibrados. MAE < 0.10 vs medido.

### V2 — Carregamento axial (em vez de transverso)
Aplicar F_axial cyclico (acima de F_sep para garantir descolamento). Predizer F_0(N) — espera-se loosening lento dominado por embedding + creep, **sem** loosening rotacional significativo (Fator 2 axial = sin β ≈ 0.04).

### V3 — Locking device (Nord-Lock ou similar)
Mesma config do Exp 5 + Nord-Lock washer. Predizer F_0(N) com `μ_bearing` aumentado pela washer (datasheet). MAE < 0.15 (mais permissivo, locking devices são variáveis).

### V4 — Combinado axial + transverso (R = 0.5)
Loading com componentes axial e transversal balanceadas. Validação do Fator 1 + Fator 2 simultaneamente.

Predição PASS = MAE < 0.10 e RMSE < 0.15 contra medições.

---

## 10. Mapeamento ao código

### 10.1. Constantes físicas

| Constante | Acesso no código | Default atual |
|-----------|------------------|---------------|
| `k_j_init` | `JointMaterial.k_j_init` | 4e9 N/m |
| `α_GW` | `JointMaterial.alpha_GW` | 0.5 |
| `μ_thread` | `JointMaterial.mu_thread` | 0.15 |
| `μ_bearing` | `JointMaterial.mu_bearing` | 0.15 |
| `K_archard` | `JointMaterial.K_archard` | 1e-4 |
| `emb_depth` | `JointMaterial.emb_depth` | 3e-6 m |
| `N_emb` | `JointMaterial.N_emb` | 50 ciclos |
| `C_creep` | `JointMaterial.C_creep` | 2e-12 |

### 10.2. Tuners de ajuste (novos)

| Tuner | Acesso | Default | Calibrado em |
|-------|--------|---------|--------------|
| `k_emb_scale` | `JointMaterial.k_emb_scale` | 1.0 | Exp 3 (re-fit pós-experimento) |
| `k_creep_scale` | `JointMaterial.k_creep_scale` | 1.0 | Exp 2 (re-fit pós-experimento) |
| `k_wear_scale_ax` | `JointMaterial.k_wear_scale_ax` | 1.0 | Exp 5A |
| `k_wear_scale_tr` | `JointMaterial.k_wear_scale_tr` | 1.0 | Exp 5T |
| `k_loose_scale_ax` | `JointMaterial.k_loose_scale_ax` | 1.0 | Exp 5A |
| `k_loose_scale_tr` | `JointMaterial.k_loose_scale_tr` | 1.0 | Exp 5T |
| `Phi_ax_correction` | `JointMaterial.Phi_ax_correction` | 1.0 | Exp 4A |
| `Phi_tr_correction` | `JointMaterial.Phi_tr_correction` | 1.0 | Exp 4T |

Para loading combinado, o modelo usa `direction_blend(θ, val_ax, val_tr)`:
```
k_eff(θ) = val_ax · cos²θ + val_tr · sin²θ        (interpolação de Mohr)
```

Defaults 1.0 = modelo físico puro. Calibração ajusta entre ~0.1 e ~10 para casar dados específicos. Tuners > 10 ou < 0.1 indicam física errada (revisar).

### 10.3. Storage de calibrações

Após calibração, salvar perfil em `core/databases/joint_calibrations.json`:

```json
{
  "steel_10.9_dry_uncoated": {
    "k_j_init": 4.2e9,
    "alpha_GW": 0.58,
    "mu_thread": 0.14,
    "mu_bearing": 0.16,
    "K_archard": 1.3e-4,
    "emb_depth": 4.5e-6,
    "N_emb": 42,
    "C_creep": 1.8e-12,
    "tuners": {
      "k_wear_scale_tr": 1.2,
      "k_loose_scale_tr": 0.85,
      "Phi_tr_correction": 0.95,
      "k_loose_scale_ax": 1.4,
      "Phi_ax_correction": 1.05
    },
    "source": "UFU_2026_calibration_M20",
    "validation_MAE": 0.07
  }
}
```

Cada perfil é carregado por `JointMaterial.from_calibration_profile(name)`. Perfis válidos vêm dos resultados dos experimentos § 3–7B.

---

## 11. Notas de bancada

- **Pré-carga reprodutível:** torque sozinho tem ±30% de incerteza. Usar strain gauge no shank ou load cell axial é mandatório.
- **Termocompensação:** strain gauges são sensíveis a ΔT. Em hold long (Exp 3), ΔT de 5°C pode mascarar creep. Compensar com gauge dummy ou registrar e corrigir.
- **Lubrificação:** atomizar a lubrificação entre exps invalida calibração de μ. Manter limpo ou definir lubrificação consistente.
- **Embedding tardio:** se entre Exp 4 e Exp 5 o sample é remontado, o embedding começa do zero — refazer Exp 2 antes.
- **Ordem da pré-carga:** sempre carregar e descarregar **monotônico** para evitar histerese de Bauschinger no parafuso.

---

## 12. Próximos passos

1. **Esta semana:** revisar bancada UFU pra disponibilidade dos itens listados (atuador transversal? capacidade ≥ 100 kN? data-acquisition ≥ 100 Hz?).
2. **Próxima semana:** scripts Python pra análise pós-experimento (`tests/calibration/fit_exp1_static.py`, etc.) — pode reusar o pixel-extractor do New_Theory adaptando.
3. **2 semanas:** sample preparado (M20 grade 10.9 + flange ASTM A516) e fixture instalada.
4. **3 semanas:** rodar a sequência completa, obter primeiro set de parâmetros calibrados.
5. **4 semanas:** rodar V1–V4 e gerar relatório de validação.

Cada Exp gera um CSV padronizado (`{exp}_{date}_{sample_id}.csv`) que alimenta um pipeline de fit (`calibration/`) que escreve em `joint_calibrations.json`. A pipeline é versionada no git — calibrações ficam reproduzíveis ao longo do tempo.
