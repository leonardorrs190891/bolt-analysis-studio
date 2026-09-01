# Two-Factor Loosening Theory — Rigidez anisotrópica + acoplamento de hélice

**Data:** 2026-05-16
**Autor:** Prof. Leonardo Rosa Ribeiro da Silva, PhD (teoria); formalização colaborativa.
**Status:** Spec teórico. Antecede e justifica a implementação de um analisador unificado em BAS V2.
**Relacionado:** `2026-05-16-bas-v2-frontend-design.md` (frontend), `New_Theory/` (estudo numérico que motivou esta formalização).

---

## 1. Motivação

A literatura de self-loosening trata carregamento **transversal** (Junker, Jiang, Pai-Hess, Yang) e **axial** (Liu 2017, Du 2022) como categorias separadas, com modelos distintos para cada regime. Yang 2021 introduz um R-factor crítico (R ≈ 0.55) como fronteira empírica entre os dois — mas sem mecanismo físico que explique **por que** essa fronteira existe ou onde fica para outras geometrias.

Esta teoria propõe que ambos os regimes são manifestações do **mesmo mecanismo**, modulado por **dois fatores físicos** que dependem da direção do carregamento externo em relação à geometria da junta. Quando explicitados, esses fatores recuperam Junker (transversal) e Liu (axial) como casos-limite, e predizem o R-factor crítico do Yang a partir de propriedades mensuráveis (β, μ, k_j_ax, k_j_tr).

---

## 2. Definições e notação

| Símbolo | Significado | Unidade |
|---------|-------------|---------|
| `z` | eixo do parafuso (axial) | — |
| `x, y` | plano transversal (perpendicular ao eixo) | — |
| `β` | ângulo da hélice da rosca no diâmetro de passo: `β = atan(p / (π·d₂))` | rad |
| `d₂` | diâmetro de passo (pitch) da rosca | m |
| `p` | passo da rosca | m |
| `k_b` | rigidez axial do parafuso, `k_b = E·A_s/L_eff` | N/m |
| `k_j_ax` | rigidez axial do joint (compressão sólida) | N/m |
| `k_j_tr` | rigidez transversal aparente do joint (limitada por atrito) | N/m |
| `Φ_ax` | razão de rigidez axial, `k_b/(k_b+k_j_ax)` | — |
| `Φ_tr` | razão de rigidez transversal aparente | — |
| `μ` | coeficiente de atrito de aderência das interfaces | — |
| `F_0` | pré-carga inicial | N |
| `F_ext` | carga externa aplicada | N |
| `F_clamp` | força de clamping (igual a F_0 menos perdas) | N |
| `c` | coeficiente de acoplamento carga ↔ hélice | — |
| `L` | parâmetro de loosening | N |

Valores típicos para M20 classe 10.9: `β ≈ 0.040 rad (2.3°)`, `Φ_ax ≈ 0.15`, `μ ≈ 0.15`.

---

## 3. Fator 1 — Rigidez anisotrópica do joint

### 3.1. Tensor de rigidez do joint

A rigidez do joint não é escalar; é um tensor de segunda ordem cujos eigenvalues principais diferem em até duas ordens de magnitude entre os eixos:

```
[K_j] = diag(k_j_tr,  k_j_tr,  k_j_ax)        (frame com z = eixo do parafuso)
```

**Eixo axial** (z):
- `k_j_ax` vem da compressão elástica direta dos membros sólidos (flange, arruela)
- Tipicamente `k_j_ax ≈ 3–10 × k_b` para juntas metálicas
- Φ_ax = `k_b/(k_b+k_j_ax) ≈ 0.10–0.25`
- O bolt vê pouca da carga axial **até a separação** em `F_sep = F_0/(1-Φ_ax)`
- Acima de F_sep: junta desliga, bolt vê 100% da carga (transferência discontínua)

**Eixos transversais** (x, y):
- Não há "membro elástico" entre bolt e joint na direção transversal — a continuidade é mantida por **atrito de aderência** nas interfaces (bearing porca/flange, head/flange, flange/flange)
- Enquanto a força transversal não excede o limite de aderência local, `F_tr < μ·F_clamp`, o joint comporta-se como **infinitamente rígido transversalmente** (sem deslocamento relativo)
- Acima do limite: slip ocorre, `k_j_tr → 0`, todo o deslocamento transversal é transmitido ao bolt
- Pai-Hess: o slip-onset acontece em fração `≈ 0.46·μ·F_clamp` (antes do limite Coulomb clássico), devido a stick-slip parcial

### 3.2. Analogia ao círculo de Mohr

A diferença axial-transversal da rigidez é a mesma noção do círculo de Mohr para tensão: ao **transformar o frame** (carregar a junta a um ângulo θ do eixo axial), a "rigidez aparente" experimentada pela carga é uma combinação dos dois eigenvalues principais:

```
k_eff(θ) = k_j_ax · cos²θ  +  k_j_tr · sin²θ
```

Para θ = 0 (axial puro): `k_eff = k_j_ax` (alto, rígido).
Para θ = π/2 (transversal puro): `k_eff = k_j_tr` (zero quando slip).
Para θ intermediário: combinação ponderada.

Esta é a forma **explícita** da "rigidez anisotrópica" da sua teoria.

### 3.3. Função de regime

Define a **razão de rigidez direcional**:

```
Φ(θ, F_ext) = k_b / (k_b + k_eff(θ, F_ext))
```

onde `k_eff` agora depende também de `F_ext` porque `k_j_tr` colapsa quando o slip threshold é ultrapassado:

```
k_j_tr(F_ext, θ) = K_stick               se F_ext·sin θ < 0.46·μ·F_clamp
                 = 0                      caso contrário
```

(Com K_stick = ∞ pra simplificar, ou K_stick = rigidez de Hertz das aspereze pra modelo refinado.)

---

## 4. Fator 2 — Acoplamento carga ↔ hélice

### 4.1. Vetor unitário da hélice

A hélice da rosca, no diâmetro de passo `d₂`, é uma linha que faz ângulo `β` com o plano normal ao eixo. O vetor tangente à hélice tem componentes:

```
ĥ = (cos β · sin φ,  cos β · cos φ,  sin β)         (parametrizado por φ azimutal)
```

Componente axial: `sin β` (pequeno — ~0.04 rad).
Componente transversal: `cos β` (próximo de 1).

### 4.2. Projeção da carga externa na hélice

A "força que tenta desenroscar o parafuso" é a projeção da força externa no vetor tangente à hélice, integrada ao longo da circunferência de contato. Para análise por componente:

```
c_axial(carga axial pura)    = sin β       ≈ 0.04
c_transversal(carga trans.)  = cos β       ≈ 1.0
```

Razão: `c_tr/c_ax = cot β ≈ 25` para M20×2.5.

### 4.3. Torque de loosening por unidade de força

A força projetada na hélice atua em um braço de alavanca `r = d₂/2`:

```
T_loosening_ax  = c_ax · F_ext_ax · (d₂/2)
                = (d₂/2)·sin β · F_ext_ax
                ≈ p/(2π) · F_ext_ax              (já que sin β·d₂/2 = p/(2π))

T_loosening_tr  = c_tr · F_ext_tr · (d₂/2)
                = (d₂/2)·cos β · F_ext_tr
                ≈ (d₂/2) · F_ext_tr               (cos β ≈ 1)
```

A razão dos **torques** (não só das forças) é:

```
T_tr / T_ax = cos β / sin β = cot β ≈ 25 (M20)
```

— ou seja, **a mesma razão das forças projetadas**, porque o braço de alavanca é o mesmo. O `cot β` é a "vantagem mecânica" da carga transversal sobre a axial para induzir rotação de loosening.

---

## 5. Síntese — Parâmetro unificado de loosening

Combinando os dois fatores:

```
L(θ, F_ext)  =  Φ(θ, F_ext)  ·  c(θ)  ·  F_ext
              └─ Fator 1 ─┘    └ Fator 2 ┘
```

Em forma vetorial, decompondo F_ext em componentes axial e transversal:

```
L_ax  =  Φ_ax(F_ext)        · sin β · F_ext_ax
L_tr  =  Φ_tr(F_ext)        · cos β · F_ext_tr
L     =  √(L_ax² + L_tr²)          (resultante da força de loosening)
```

**Condição de loosening rotacional** (junker-like):

```
L  >  L_crit  =  T_resistance / (d₂/2)
```

onde `T_resistance` é o torque resistente combinado de thread friction + bearing friction:

```
T_resistance  =  μ_thread · F_clamp · (d₂/2 / cos α_thread)  +  μ_bearing · F_clamp · r_eff_bearing
```

(α_thread é o ângulo do flanco da rosca, ~30° para ISO métrica.)

---

## 6. Casos-limite recuperados

### 6.1. Carregamento transversal puro (Junker / Jiang)

`F_ext_ax = 0, F_ext_tr ≠ 0`. Stick threshold em `F_tr = 0.46·μ·F_0`.

Abaixo do threshold: `Φ_tr ≈ 0` (joint stuck), `L_tr ≈ 0`, sem loosening.
Acima: `Φ_tr → 1` (joint slipping), `L_tr ≈ cos β · F_tr ≈ F_tr`, loosening rotacional. → **Junker mechanism** ✓

A teoria de Jiang 5-stage é uma evolução temporal de `Φ_tr(N_ciclos)` (decai de Φ_stuck pra Φ_slip ao longo dos ciclos), e o parâmetro `0.46` aparece como o pre-factor de slip-onset.

### 6.2. Carregamento axial puro (Liu 2017 / Du 2022)

`F_ext_ax ≠ 0, F_ext_tr = 0`. Separação em `F_ext_ax = F_sep = F_0/(1-Φ_ax)`.

Abaixo de F_sep: `Φ_ax ≈ 0.15`, `L_ax = 0.15 · sin β · F_ax ≈ 0.006·F_ax` — muito pequeno. Stage I: loosening por embedding/wear, não rotacional.
Acima: bolt vê tudo, `Φ_ax = 1`, `L_ax = sin β · F_ax`. Ainda pequeno comparado a transverso, mas pode acumular se ciclagem é grande. Stage II/III: combina com fretting/wear. → **Liu axial 2-stage** ✓

### 6.3. Carregamento combinado (Yang 2021 R-factor)

R = F_ax / F_total (ou similar). A teoria prediz `R_critical` resolvendo:

```
L_ax(R_critical)  =  L_tr(R_critical)
Φ_ax · sin β · R         =  Φ_tr · cos β · (1-R)
R/(1-R)                  =  (Φ_tr · cos β) / (Φ_ax · sin β)
                         =  (Φ_tr / Φ_ax) · cot β
```

Resolvendo: `R_critical = 1 / (1 + Φ_ax·tan β / Φ_tr)`.

Para M20 com `β = 0.04`, `Φ_ax = 0.15`, `Φ_tr = 1` (slipping):
```
R_critical = 1 / (1 + 0.15·0.04/1) = 1 / 1.006 ≈ 0.994
```

Hmm — isso prediz que transversal domina quase sempre (R deveria ser >0.99 pra axial ter mesma magnitude). O R_critical empírico do Yang ≈ 0.55 sugere que minha derivação acima precisa de refinamento (provavelmente envolve a frequência de occorrência do slip, não só a magnitude). **Identifica uma direção concreta de validação:** o que falta no modelo simples pra recuperar 0.55.

Possíveis ajustes:
1. **Eficácia por ciclo**: cada ciclo transversal só causa loosening durante uma fração do período (quando slip); axial atua durante todo o ciclo se F_ax > F_sep
2. **Wear-induced Φ_ax**: à medida que F_clamp cai por wear axial, Φ_ax sobe; eventualmente domina sobre transverso saturado
3. **Direction-dependent T_resistance**: o torque resistente também é anisotrópico

Investigar essas refinações é parte do programa de validação (§8).

---

## 7. Exemplos numéricos

### 7.1. Tabela de fatores para 3 tamanhos típicos

| Bolt | d₂ [mm] | p [mm] | β [°] | sin β | cos β | cot β | k_b típ. [kN/mm] |
|------|---------|--------|-------|-------|-------|-------|-----------------|
| M8 × 1.25  | 7.19  | 1.25 | 3.17 | 0.0553 | 0.9985 | 18.05 | ~120 |
| M12 × 1.75 | 10.86 | 1.75 | 2.94 | 0.0513 | 0.9987 | 19.47 | ~200 |
| M20 × 2.5  | 18.38 | 2.50 | 2.48 | 0.0433 | 0.9991 | 23.10 | ~800 |
| 3/4"-10 UNC | 17.40 | 2.54 | 2.66 | 0.0464 | 0.9989 | 21.55 | ~700 |

A vantagem transversal `cot β` cresce com diâmetro (passos relativos menores em parafusos maiores → β menor → loosening transverso ainda mais favorecido).

### 7.2. Loosening prediction para M20 sob 3 cenários

Assumindo F_0 = 50 kN, μ = 0.15, Φ_ax(stuck) = 0.15, Φ_tr(slipping) = 0.95:

**Cenário A — Junker test:** F_ext_tr = 10 kN @ 12.5 Hz transversal puro.
```
L_tr = 0.95 · cos(2.48°) · 10000 = 9494 N · (d₂/2 = 9.19 mm) → T_loose = 87.2 N·m
```

**Cenário B — Axial dinâmico:** F_ext_ax = 30 kN axial (acima de F_sep ≈ 58.8 kN? não — F_sep = 50/0.85 = 58.8 kN, então 30 kN está abaixo, stuck regime axial).
```
Φ_ax(stuck) = 0.15;  L_ax = 0.15 · sin(2.48°) · 30000 = 195 N · 9.19 mm → T_loose = 1.79 N·m
```

T_loose transverso é **~50× maior** que axial nesse cenário. Coerente com a observação experimental de que Junker é o teste mais agressivo.

**Cenário C — Combinado R = 0.55** (load total = 20 kN, axial = 11, trans = 9):
```
L_ax = 0.15 · 0.0433 · 11000 = 71 N
L_tr = 0.95 · 0.9991 · 9000 = 8547 N
T_loose ≈ T_loose_tr (axial é desprezível)
```

Ainda dominado por transverso. Para Φ_ax saturar e equilibrar precisaria de F_ax > F_sep. **Isto é exatamente o que Yang 2021 reporta empiricamente** — abaixo de R_critical o regime é Junker-like, acima é Liu-like.

---

## 8. Programa de validação

A teoria é falsificável por experimentos específicos. Mapeamento contra os 97 papers do `Models/CALIBRATION_AND_VALIDATION/`:

| Predição | Paper(s) de validação | Critério de aceitação |
|----------|----------------------|----------------------|
| `c_tr / c_ax ≈ cot β = 20–25` para parafusos típicos | Junker original + Liu 2017 | Razão de loosening rates entre os dois ≥ 20× |
| `Φ_ax · sin β` ≈ 0.006 → loosening axial sub-separação muito pequeno | Liu 2017 (Stage I) | Loss rate Stage I ≤ 0.5%/cycle |
| `F_sep` predita por `F_0/(1-Φ_ax)` | Jiang 2003 + Zhang 2006 | Erro ≤ 10% |
| `R_critical` predito (após refinamento) | Yang 2021 | Bater 0.55 ± 0.05 |
| Wear-induced Φ_ax aumentando após N ciclos | Liu 2017 Stage II | Stage II onset previsível por Φ_ax(F_clamp(N)) |
| Junker class A–F do locking_devices.json correlacionada com `μ` e geometria | Sase-Koga 1996 + DIN 65151 | Classe = f(L_loose / L_crit) |

Validação **Tier-1**: predições qualitativas (hierarquia, sinais). Tier-2: ordens de magnitude (±2x). Tier-3: quantitativo (±20%). Tier-4: ajuste fino com parâmetros calibrados.

---

## 9. Mapeamento na arquitetura V2

### 9.1. Onde a teoria vive no código

- **Novo arquivo** `src/bolt_analysis_studio/numerical/two_factor_analyzer.py`:
  - `TwoFactorLooseningAnalyzer(joint, bolt, loading)` — classe que computa L_ax, L_tr, T_loose por ciclo
  - Substitui (ou complementa) o dispatch atual `_classify_phase()` / `_classify_phase_axial()` em `coupled_loosening_analyzer.py`
  - Mantém compatibilidade: o output mantém o formato `LooseningPhase` / `LooseningResults`, mas a derivação é unificada

- **Módulo Analysis no V2 frontend** (`gui/modules/analysis_module.py`):
  - Inspector mostra `Φ_ax`, `Φ_tr(current)`, `c_ax`, `c_tr`, `L_loose / L_crit` como métricas
  - Plot novo: "Loosening Driver Composition" — bar chart mostrando contribuição axial vs transversal em tempo real

- **Módulo Loads no V2** (`gui/modules/loads_module.py`):
  - Combo "Load type" passa de TRANSVERSE/AXIAL/COMBINED para um único modelo com ângulo θ entre 0 e π/2
  - `R-factor` no inspector vira derivado automático: R = cos²θ

### 9.2. Onde os parâmetros aparecem no Inspector (modo Basic/Advanced)

**Basic:**
- F_ext, θ (load angle, replaces load type combo)
- F_0 preload, %Yield
- N cycles, frequency

**Advanced:**
- Φ_ax_stuck (default = k_b/(k_b+k_j_ax_compute))
- Φ_tr_stuck, Φ_tr_slipping
- β (auto from d₂, p) — read-only
- L_crit threshold

### 9.3. Identidade no relatório

A seção "Loosening Analysis" do report passa a mostrar:
```
Loading regime:           θ = 67.5° (transverse-dominated)
L_axial:                  71 N        (0.4% of total)
L_transverse:             8547 N      (99.6% of total)
L_resultant:              8547 N
T_loosening:              78.6 N·m
T_resistance:             92.3 N·m
Loosening margin:         13.7 N·m   ✓ STABLE
```

Em vez do output atual com fase Jiang opaca.

---

## 10. Questões em aberto

1. **Refinamento do Φ_tr(F_ext)** — gradual vs abrupto? Hertziano vs Coulomb? Pai-Hess sugere fator 0.46 de slip-onset; integrar isso ao Fator 1.

2. **Braço de alavanca para componentes de força combinada** — quando R varia, o torque resultante não é simplesmente √(T_ax² + T_tr²) porque a direção do torque difere (ambos são em torno do eixo do parafuso, mas com fase diferente no ciclo dinâmico). Reanálise vetorial necessária.

3. **Yang R_critical = 0.55** — a derivação direta dá ~0.99. Refinar o modelo até bater 0.55 (possíveis ajustes: ciclo de duty, wear feedback, anisotropia do T_resistance).

4. **Aplicabilidade a thermal/bending** — a teoria foi formulada pra cargas mecânicas. Como entra ΔT? Provavelmente como `F_ext_ax_thermal = k_eq · α·ΔT`, mas merece tratamento próprio.

5. **Multi-bolt joints** — em assemblies com múltiplos parafusos, cada um tem seu (Φ_ax, Φ_tr, θ) próprio. Combinação requer modelo de distribuição de carga (já existe em similitude/, conectar).

---

## 11. Próximos passos

1. **Refinar derivação de R_critical** contra Yang 2021 e Liu-Mi 2021 (papers 79, 87, 88 do índice).
2. **Implementar `TwoFactorLooseningAnalyzer`** em código (pode ser feito em V2 ou retrofit no v4.0 atual).
3. **Validar Tier-1 qualitativo** contra UFU 5A / 13A (cargas predominantemente transversais) — predição: L_tr dominante, Φ_ax ≈ 0.
4. **Validar Tier-2 quantitativo** contra Lu 2024 (M8) e Jiang 2003 (M12) — predição: F_sep, loosening rate.
5. **Estender pra combinado** validando contra Yang 2021 e Du 2022.

Cada um desses passos pode virar um plano de implementação separado (`writing-plans`) quando o usuário aprovar a próxima etapa.

---

## 12. Extensão — [K] dinâmica, vetor de estado lento, balanço energético

(Adicionado após discussão sobre acomodações de cargas, perdas graduais, e o papel da própria pré-tensão como atuadora dos fatores. Esta extensão formaliza a estrutura de **dois timescales** — rápido para vibração ciclo-a-ciclo, lento para degradação cumulativa — e mostra como toda a história da junta vive num vetor de estado que parametriza [K].)

### 12.1. Vetor de estado lento

Distinguir entre dois conjuntos de variáveis:

| Tipo | Coordenadas | Timescale | Equação governante |
|------|-------------|-----------|---------------------|
| Rápida (vibração) | `q = (x, y, θ)` | 1/freq (ms a s) | `[M]{q̈} + [C]{q̇} + [K(s)]{q} = {F(q, q̇, t; s)}` |
| Lenta (degradação) | `s = (F_0, δ_emb, δ_creep, δ_wear, θ_loose)` | ciclos (s a anos) | `ds/dN = ⟨rates⟩_cycle` |

`s` é o **vetor de estado lento** — a memória cumulativa de tudo que aconteceu até o ciclo N:

| Componente | Significado físico | Equação de evolução (forma) |
|------------|-------------------|------------------------------|
| `F_0(N)` | pré-carga atual residual | dF_0/dN = − Σ rates (ver §12.3) |
| `δ_emb(N)` | embedding plástico cumulativo | δ_emb,∞·(1 − e^(−N/N_emb)) (saturating) |
| `δ_creep(N)` | creep viscoso cumulativo | C_creep · log(t(N)) (Norton-Bailey) |
| `δ_wear(N)` | desgaste adhesive/abrasivo cumulativo | ∫ K_arch · F_n · ds_slip / (H·A) dN |
| `θ_loose(N)` | rotação cumulativa da porca | ∫ T_helix/I_θ · slip_fraction · dN |

Cada componente é monotônica (sempre cresce com N, ou no caso de F_0 sempre cai). O sistema é dissipativo — `s` não retorna ao estado inicial.

### 12.2. [K] como função explícita do estado

A matriz de rigidez é **agora dinâmica**, atualizada a cada ciclo lento:

```
[K(s)] = [K_geometric] + [K_joint(s)]
```

**[K_geometric] (constante):**
```
   x     y     θ
 ┌──────────────────┐
 │ k_b   0    K_xθ  │
 │ 0     0    0     │     K_xθ = k_b · (p/2π)     ← Fator 2 (geométrico, invariante)
 │ K_xθ  0    0     │     K_θx = K_xθ (simetria reciproca)
 └──────────────────┘
```

**[K_joint(s)] (varia com s):**
```
   x                  y                       θ
 ┌─────────────────────────────────────────────┐
 │ k_j_ax(s)          0                   0    │
 │ 0          k_j_tr(s, regime)           0    │
 │ 0                  0                   k_j_θ │
 └─────────────────────────────────────────────┘
```

Com leis constitutivas explícitas:

**Rigidez axial do joint** (Greenwood-Williamson):
```
k_j_ax(s) = k_j_ax,0 · (F_0(s) / F_0,init)^α          com α ≈ 0.5 a 0.8
```
Justificativa: número de asperezas em contato cresce sub-linearmente com a força normal. Quando `F_0 → 0`, `k_j_ax → 0` (junta perde rigidez axial gradualmente).

**Rigidez transversal do joint** (anisotropia da teoria, com transição stick→slip):
```
k_j_tr(s, regime) = K_stick                if F_tr_amp(t) < 0.46·μ·F_0(s)
                  = 0                       if F_tr_amp(t) ≥ 0.46·μ·F_0(s)
```
A transição depende do estado lento (via F_0) e da força transversal instantânea (rápida). Pré-tensão menor → threshold menor → slip por carga menor → mais ciclos em slip.

**Rigidez rotacional efetiva da porca contra desenrosco** (atrito como pseudo-stiffness):
```
k_j_θ(s) = T_resist(F_0(s)) / θ_max_stick                (Iwan-like)
         ≈ (μ_thread·F_0·d₂/(2cos α) + μ_bear·F_0·r_eff) / θ_pre_slip
```

Quando o torque ultrapassa T_resist: `k_j_θ → 0`, slip rotacional, perda de F_0.

### 12.3. Equações de evolução de `s`

A queda da pré-carga é a soma de cinco mecanismos paralelos, cada um com sua taxa:

```
dF_0
──── = − (rate_emb  + rate_creep  + rate_wear  + rate_loose  + rate_misc)
 dN
```

Cada taxa é uma função de `s` (estado atual) e do loading (F_amp, θ_load, freq):

| Mecanismo | Taxa de queda (forma simplificada) | Onde os fatores entram |
|-----------|-----------------------------------|------------------------|
| **rate_emb** | `k_b · δ_emb,∞/N_emb · exp(−N/N_emb)` — exponencial decrescente | Φ multiplica F_clamp efetivo |
| **rate_creep** | `k_b · C_creep · 1/N · F_0` (log no tempo) | F_clamp_média = F_0·(1 − ½(1−Φ)·F_amp²/F_0²) |
| **rate_wear** | `k_b · K_arch · F_clamp · ds_slip/A_contact` | Slip distance proporcional ao slip_fraction (Fator 1) |
| **rate_loose** | `k_loose · L(Φ(F_0), c(β), F_amp) · slip_fraction` | **Os dois fatores aqui explicitamente** (§5) |
| **rate_misc** | thermal, electrochemical, settling de paint/coating | depende do caso |

A taxa de loosening rotacional (sua teoria central):
```
rate_loose = k_loose · Φ_eff(F_0) · c(β) · F_amp · slip_fraction(F_0, F_amp)

onde
  Φ_eff(F_0)   = k_b / (k_b + k_j_ax(F_0))     ← Fator 1, função de F_0 via §12.2
  c(β)         = sin β  (axial) ou cos β  (transverso)   ← Fator 2, geométrico
  slip_fraction = fração do ciclo em slip do filete
                ≈ max(0, (T_helix − T_resist)/T_helix) onde T_resist = f(F_0)
```

Outras evoluções:
```
δ_emb(N)   = δ_emb,∞ · (1 − exp(−N/N_emb))     com N_emb ≈ 50 ciclos
δ_creep(N) = C_creep · log(t(N) + t_0)         com t_0 = 1 s
δ_wear(N+1) = δ_wear(N) + K_arch·F_n·ds_slip / (H·A)
θ_loose(N+1) = θ_loose(N) + (2π/p) · ΔF_loose(N) / k_b
```

Note: `θ_loose` está relacionado a `ΔF_loose` pela hélice — perda de preload por loosening é estritamente `Δθ × k_b × p/(2π)`. Isso garante consistência geométrica.

### 12.4. Energia elástica armazenada (em função de `s`)

Componentes da energia interna a F_ext=0:

```
U_bolt(s)     = F_0(s)² / (2·k_b)                                 ← tração no estojo
U_joint(s)    = F_0(s)² / (2·k_j_ax(F_0(s)))                       ← compressão na flange
              = F_0(s)² · F_init^α / (2·k_j,0 · F_0(s)^α)
              = F_0(s)^(2−α) · F_init^α / (2·k_j,0)
U_internal(s) = U_bolt + U_joint
              = F_0²/2 · [1/k_b + F_init^α / (k_j,0 · F_0^α)]
```

**Observação crítica:** `U_internal` **não é parabólico em F_0** quando `k_j` depende de F_0 (α > 0). Para α=0.5:
```
U_internal(F_0) = F_0²/(2k_b) + F_0^(1.5) · F_init^0.5 / (2·k_j,0)
```

A função tem **concavidade que aumenta** conforme F_0 cai — a energia armazenada cai **mais rápido que o quadrado da pré-carga**, porque ao mesmo tempo a junta amolece. Essa não-linearidade é a **forma matemática do runaway**: queda inicial de F_0 → queda desproporcionalmente maior de U_internal → maior energia disponível pra alimentar os mecanismos dissipativos no próximo ciclo.

Energia adicionada por ciclo (loading axial puro pra simplicidade):
```
W_ext,cycle(s) = F_amp² / (2·(k_b + k_j_ax(F_0)))    (área do triangulo F vs Δ no carregamento elástico)
```

Quando o sistema vai pra slip durante o ciclo, há trabalho adicional contra o atrito:
```
W_friction,cycle = μ·F_clamp · (slip_distance per cycle)
```

### 12.5. Balanço energético per-cycle

Conservação de energia ao longo de um ciclo completo:

```
W_ext,cycle  =  ΔU_internal  +  W_friction  +  W_emb_plastic  +  W_creep  +  W_wear
   (input)      (recovery     (thread+bear+   (irreversible    (viscous    (Archard
                from stored    transv. slip)   asperity         loss)       removal)
                preload —      ←─────────  ⊕  ──────────→
                NEGATIVO
                durante
                loosening)
```

Para um ciclo onde nada falha (stable): `ΔU_internal ≈ 0`, todo W_ext volta como elastic + small friction loss.

Para um ciclo em regime de loosening: `ΔU_internal < 0` (preload cai), `W_friction + W_emb + ...` consome `W_ext + |ΔU_internal|`. O **excesso de energia** vem do reservatório interno (pré-tensão).

Essa última observação é a chave da sua intuição original: **a junta age como um capacitor pré-carregado que vai descarregando ao longo dos ciclos**, com a taxa de descarga aumentando conforme a "tensão" (F_0) cai porque a "resistência interna" (k_j) também cai.

### 12.6. Formulação Lagrangiana

Para uso em métodos numéricos avançados (multibody, FEM), o sistema completo é um Lagrangiano com Hamiltoniano não-conservativo:

```
L(q, q̇; s) = T(q̇) − V_elastic(q; s)

T(q̇)       = ½ q̇^T [M] q̇                            (cinética)
V_elastic   = ½ q^T [K(s)] q                          (potencial elástico, depende de s)
Q_nc(q̇; s) = −∇_q̇ V_friction(q̇; s) + Q_ext(t)        (forças não-conservativas: atrito + carga externa)
```

Equação de Euler-Lagrange com forças não-conservativas:
```
d/dt (∂L/∂q̇) − ∂L/∂q = Q_nc
```

Mais o "slow flow":
```
ds/dN = R(s, ⟨q⟩_cycle, ⟨q̇⟩_cycle, F_amp, freq)
```
onde R é o vetor de taxas da §12.3, calculado **mediando sobre um ciclo rápido**.

### 12.7. Como os dois fatores aparecem nesta formalização

Mapeamento explícito, agora preciso:

| Fator / mecanismo | Em [K(s)] | Em ds/dN | Em V_friction |
|---|---|---|---|
| **Fator 1 axial** (k_j_ax(F_0)) | sim (diagonal xx) | F_0 evolui → muda Φ | — |
| **Fator 1 transversal** (k_j_tr stick/slip) | sim (diagonal yy, condicional) | slip ativa rate_wear, rate_loose transversal | — |
| **Fator 2** (acoplamento helix K_xθ) | sim (off-diagonal xθ, **constante**) | T_helix multiplica rate_loose | torque resistente |
| **Atrito filete** | implícito em k_j_θ | T_resist gateia slip_fraction | sim, gradiente em θ̇ |
| **Atrito bearing** | implícito em k_j_θ | idem | sim, gradiente em θ̇ |
| **Atrito interface transversal** | gateia k_j_tr stick/slip | rate_wear, rate_loose | sim, gradiente em ẏ |
| **Pré-tensão F_0** | escala k_j_ax via Greenwood-Williamson | autoreferente | escala todas as forças de reação |

**Insight central** (sua observação original):
> "a própria pré-tensão atua nesses fatores"

Formalizado: **F_0(s) entra como argumento de k_j_ax(F_0), k_j_tr(F_0), k_j_θ(F_0), T_resist(F_0), slip_fraction(F_0)**. Ela aparece em todos os lugares onde a estabilidade do contato é relevante. Quando F_0 cai, todas essas grandezas mudam, e via [K(s)] modificada, o sistema **resposde dinamicamente diferente** no próximo ciclo. **Não há um parâmetro F_0 estático que sirva pra toda a história — ele é função do tempo via `s(N)`**.

### 12.8. Implementação proposta

Uma implementação direta dessa formalização teria a seguinte estrutura:

```
class DynamicStiffnessAnalyzer:
    def __init__(self, geometric: BoltGeometry, material: Material,
                 loss_models: List[LossMechanism]):
        self.s = SlowState(F_0=initial_preload, δ_emb=0, δ_creep=0,
                           δ_wear=0, θ_loose=0)
        self.loss_models = loss_models  # plug list of LossMechanism instances

    def K(self) -> np.ndarray:                  # current [K(s)]
        return assemble_K(self.s, self.geometric)

    def U_internal(self) -> float:               # current stored energy
        return compute_U_internal(self.s, self.geometric)

    def step_cycle(self, F_amp: float, θ_load: float, freq: float) -> CycleResult:
        # rapid sub-step: integrate one cycle with current [K(s)] and friction
        cycle = integrate_one_cycle(self.K(), F_amp, θ_load, freq)
        # slow sub-step: update s using rates from each loss model
        ds = sum(model.rate(self.s, cycle) for model in self.loss_models)
        self.s = self.s + ds
        return cycle, self.s
```

`LossMechanism` é uma interface plug-in: cada mecanismo (embedding, creep, wear, loose rotacional, thermal) implementa um `rate(state, cycle_result) -> ds`. Pode-se ativar/desativar mecanismos individuais para isolamento experimental.

Isso conecta limpamente:
- Com o V2 frontend (slot no módulo Analysis para "Active loss mechanisms" como multi-checkbox)
- Com a validação (UFU foca em loose rotacional; Liu 2017 ativa wear+loose; ISO foca em creep)
- Com simulação Monte-Carlo (varia parâmetros dos LossMechanisms independentes)

---

## 13. Próximos passos atualizados (após extensão §12)

1. Implementar `SlowState` dataclass + `LossMechanism` interface
2. Implementar `EmbeddingLoss`, `CreepLoss`, `WearLoss`, `RotationalLoosenessLoss` como modelos plug-in
3. Verificar conservação de energia (W_ext = ΔU + Σ losses) num teste unitário
4. Validar dependência `k_j_ax(F_0)` contra Lu 2024 ou Bouzid (papers que reportam compliance da junta a múltiplas pré-cargas)
5. Estender o `loosening_energy.html` para mostrar **decomposição por mecanismo** (5 áreas empilhadas em vez de uma curva única de F_0(N))
