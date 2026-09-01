# MODEL MATH REFERENCE — DynamicStiffnessAnalyzer

Referência matemática completa e didática do modelo de loosening implementado em
`src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py`.

Este documento cobre **o que está no código hoje** (rev. 2026-06-20), incluindo
o modo displacement-controlled, a variável de estado `surface_damage`, e a
calibração em estágios (`StagedCalibrator`).

---

## 0. Filosofia: por que o modelo é EMPÍRICO-ANALÍTICO

O `DynamicStiffnessAnalyzer` não é nem puro First-Principles nem puro fit
estatístico. Ele é construído em **três camadas**, cada uma com origem
epistemológica diferente:

| Camada | Origem | Pode mudar? | Exemplos |
|---|---|---|---|
| **Analítica pura** | Princípios físicos invariantes (mecânica, termodinâmica) | Não — verdade física | k_b = E·A_s/L_eff (Hooke), helix lead p/(2π), F_slip = µ·F₀ (Coulomb), conservação de energia |
| **Empírico-fenomenológica** | Forma matemática derivada da observação experimental, parâmetros calibrados contra dados | Os **parâmetros** mudam por material/junta; a forma não muda | Embedding Norton-Bailey (1−exp(−N/N_emb)); creep log(t); Greenwood-Williamson k_j(F₀); two-factor Φ anisotrópico |
| **Tunável (calibração)** | Multiplicadores sem significado físico isolado; existem só para absorver discrepâncias estruturais residuais | Sim, por experimento | k_emb_scale, k_creep_scale, k_wear_scale_{ax,tr}, k_loose_scale_{ax,tr}, Phi_{ax,tr}_correction, tr_loose_gain |

**O acoplamento entre mecanismos é o que distingue o modelo de uma soma
ingênua.** Embedding muda F₀, F₀ muda Φ_eff via Greenwood-Williamson, Φ_eff muda
o torque de loosening, loosening muda F₀ de novo. Isso é positive feedback
não-linear e aparece naturalmente pelo fato de **toda mecânica de perda usar F₀
como entrada e atualizar F₀ como saída** no mesmo ciclo.

Os tuners da camada 3 existem como reconhecimento honesto de que mecanismos
físicos compactados em uma única equação inevitavelmente faltam detalhes. Em
vez de esconder isso atrás de "constantes mágicas", deixamos os multiplicadores
explícitos e calibráveis.

---

## 1. Geometria da junta (`JointGeometry`)

Geometria **invariante** da junta + parafuso (não muda durante o ciclo).

```
E         : Módulo de Young               [Pa]    default 200 GPa
A_s       : Área de tensão do parafuso   [m²]    M16 → 157e-6
L_eff     : Comprimento efetivo de aperto [m]    M16 → 0.050
d_2       : Diâmetro de passo             [m]    M16 → 14.701e-3
pitch     : Passo da rosca                [m]    M16 → 2.0e-3
r_bearing : Raio efetivo do bearing       [m]    M16 → 12e-3
A_contact : Área nominal de contato       [m²]   ~1e-4
```

**Quantidades derivadas:**

```
k_b  = E · A_s / L_eff                 [N/m]   Rigidez axial do parafuso
β    = arctan(pitch / (π · d_2))       [rad]   Ângulo da hélice
λ    = pitch / (2π)                    [m/rad] Lead per radian
```

Para M16: k_b = 200e9 · 157e-6 / 0.050 = **6.28e8 N/m** = 628 kN/mm.

---

## 2. Material e contato (`JointMaterial`)

Propriedades **lentamente variáveis** ou fixas por material/condição. Defaults
calibrados (rev. 2026-05-19) para M16 shear ±0.5mm 0.5Hz arruela nova.

### 2.1 Parâmetros físicos

```
mu_thread       : Coef. atrito filete                [-]    0.15
mu_bearing      : Coef. atrito bearing               [-]    0.15
K_archard       : Coef. wear de Archard              [-]    1e-4  (literatura, boundary lub)
hardness        : Dureza do material                 [Pa]   2e9   (aço típico)
k_j_init        : Rigidez inicial do joint (axial)   [N/m]  4e9
alpha_GW        : Expoente Greenwood-Williamson      [-]    0.5
emb_depth       : Profundidade saturada de embedding [m]    30e-6
N_emb           : Ciclos característicos embedding   [-]    50
C_creep         : Coef. de creep Norton-Bailey       [m/Pa/log_decade] 5e-11
t_0             : Tempo de referência creep          [s]    1.0
tr_loose_gain   : Ganho do loosening transversal     [-]    2.0

# Surface damage (reaperto) — INATIVO por default (engine = comportamento antigo)
c_D             : Taxa de crescimento do dano        [-]    0.0
W_ref           : Escala de energia de referência     [J]    1e4
k_dmg_mu        : Acoplamento dano → perda de atrito [-]    0.0
k_dmg_wear      : Acoplamento dano → amplif. de wear [-]    0.0
```

### 2.2 Tuners de calibração (multiplicadores ≈ 1.0 no nominal)

```
k_emb_scale, k_creep_scale         : direção-agnósticos
k_wear_scale_ax, k_wear_scale_tr   : direção-dependentes
k_loose_scale_ax, k_loose_scale_tr : direção-dependentes
Phi_ax_correction, Phi_tr_correction : multiplicadores finais em Φ
k_damage_scale                     : multiplicador da taxa de crescimento do dano
```

Para loading combinado, blend pelo ângulo θ (Mohr-like):

```
val_eff(θ) = val_ax · cos²(θ) + val_tr · sin²(θ)
```

---

## 3. Estado lento (`SlowState`)

Vetor de **memória cumulativa** que evolui ciclo-a-ciclo (slow timescale,
diferente da dinâmica fast dentro de um ciclo):

```
s = (F_0, δ_emb, δ_creep, δ_wear, θ_loose, F_0_init, D)
```

- `F_0` [N] — pré-carga residual atual
- `δ_emb` [m] — embedding cumulativo
- `δ_creep` [m] — creep cumulativo
- `δ_wear` [m] — wear cumulativo
- `θ_loose` [rad] — rotação de loosening cumulativa
- `F_0_init` [N] — pré-carga inicial (referência fixa)
- `D` [-] — **surface_damage** ∈ [0,1] (0=prístino, 1=integridade nula). Inicializado em `D_init` via `DynamicStiffnessAnalyzer(..., initial_damage=...)`. Ver §7.5.

A relação chave entre eles:

```
F_0 = F_0_init − k_b · (δ_emb + δ_creep + δ_wear + λ · θ_loose)
```

Isto é: **toda perda de pré-carga vem da soma dos deslocamentos cumulativos
multiplicada por k_b**.

---

## 4. Constitutivas — funções de `s`

Todas avaliadas a cada ciclo, com `s` atualizado pelo ciclo anterior.

### 4.1 Rigidez do joint (Greenwood-Williamson)

```
k_j_ax(F_0) = k_j_init · (F_0 / F_0_init)^α_GW                    se F_0 > 0
            = 0                                                   se F_0 ≤ 0
```

Com α=0.5, k_j cai pela raiz quadrada da pré-carga relativa. Quando F_0 → 0,
o joint perde rigidez gradualmente. É a **não-linearidade dura** que vincula
loosening à softening.

### 4.2 Φ_eff anisotrópico (two-factor theory)

A razão de rigidez Φ controla quanto da carga externa vai pro estojo vs.
pra junta. Diferenciamos axial vs. transversal porque um joint anisotrópico
tem rigidez tangencial ≠ rigidez axial.

```
                k_b
Φ_raw = ─────────────────                  (Maney/VDI classical)
         k_b + k_j_ax(F_0)

Φ_eff(s, dir) = min(Φ_raw · Phi_dir_correction, 1.0)
```

onde `Phi_dir_correction` é `Phi_ax_correction` para axial, `Phi_tr_correction`
para transversal.

**Comportamento limite:**
- F_0 → F_0_init: k_j ≈ k_j_init, Φ ≈ k_b/(k_b+k_j_init) ≈ 0.14 (junta rígida absorve tudo)
- F_0 → 0: k_j → 0, Φ → 1.0 (toda carga vai pro estojo — loosening runaway)

### 4.3 Carga de separação axial

A força axial necessária pra abrir a junta:

```
F_sep = F_0 / (1 − Φ_eff)
```

Acima de F_sep, Φ_active = 1.0 (junta separada, estojo absorve toda carga).

### 4.4 Atrito de bearing efetivo (modulado por dano)

```
µ_bearing_eff(s) = µ_bearing · max(1 − k_dmg_mu · D, 0)
```

Com `D=0` ou `k_dmg_mu=0` retorna `µ_bearing` exato (backward-compat). Todas as
fórmulas abaixo que usavam `µ_bearing` agora usam `µ_bearing_eff`. `µ_thread`
**não** é modulado (o dano modela a superfície de bearing).

### 4.5 Threshold de slip transversal (Pai-Hess corrigido)

```
F_slip = 0.46 · µ_bearing_eff(s) · F_0
```

O fator 0.46 é a correção de Pai-Hess 2002 sobre Coulomb clássico (que daria
1.0·µ·F_0). Captura redução do slip onset por contato distribuído nos filetes.

### 4.6 Torque de resistência

```
                    µ_thread · F_0 · d_2
T_resist = ─────────────────────── + µ_bearing_eff(s) · F_0 · r_bearing
                  2 · cos(α_flank)
```

α_flank = 30° pra rosca métrica ISO. Soma de resistência do filete + bearing.

---

## 5. Formulação matricial [M], [K(s)], [C(s)]

DOFs: (x, y, θ) — axial, transversal, rotação. Estrutura compatível com
[M]q̈ + [C]q̇ + [K]q = {F} do paradigma BAS.

### 5.1 Matriz de massa [M] (constante)

```
[M] = diag(m_x, m_y, I_θ)
```

### 5.2 Matriz de rigidez [K(s)] — DEPENDE DO ESTADO

```
         ┌                                          ┐
         │ k_b + k_j_ax(F_0)    0          k_b · λ │
[K(s)] = │       0           k_j_tr(s)         0   │
         │      k_b · λ          0        k_b · λ² │
         └                                          ┘
```

- **K[0,0]** (x-x): rigidez axial total
- **K[1,1]** (y-y): rigidez transversal (≈ 0.3 · k_j_init quando stick; 0 quando slip)
- **K[2,2]** (θ-θ): rigidez rotacional via hélice = k_b · λ²
- **K[0,2] = K[2,0] = k_b · λ**: **ACOPLAMENTO HELICOIDAL** — Fator 2 da teoria two-factor

O termo off-diagonal **k_b · λ** é o que faz "rotação → translação axial" e
vice-versa via a hélice. É a base mecânica do mecanismo de loosening rotacional.

Flags `slip_y`, `slip_theta` zeram entradas correspondentes quando há slip
(força vai pra {F} via atrito, não fica em [K]).

### 5.3 Matriz de amortecimento [C(s)] (Rayleigh)

```
[C(s)] = α_R · [M] + β_R · [K(s)]
```

α_R = `rayleigh_alpha` (1/s, default 0.01), β_R = `rayleigh_beta` (s, default 1e-5).

---

## 6. Energias

### 6.1 Energia interna armazenada (pre-tensão pura, F_ext = 0)

```
                  F_0²            F_0²
U_internal(s) = ─────── + ───────────────
                 2·k_b      2·k_j_ax(F_0)
```

Substituindo k_j_ax = k_j_init · (F_0/F_init)^α:

```
U_internal ∝ F_0²·F_0^(−α) = F_0^(2−α)
```

Com α=0.5: U ∝ F_0^1.5. **Não-parabólico** — diferente de uma mola simples.

**Implicação:** quando F_0 cai, a energia liberada NÃO cai linearmente; cai
pela potência (2−α). Isso é a "energia escondida no joint" que alimenta o
loosening de Stage II.

### 6.2 Energia armazenada sob carga externa axial

```
                ┌  F_bolt² /(2·k_b) + F_joint²/(2·k_j)  se F_ext < F_sep
U_loaded(s, F)= ┤
                └  F²/(2·k_b)                          se F_ext ≥ F_sep
```

com `F_bolt = F_0 + Φ·F_ext` e `F_joint = F_0 − (1−Φ)·F_ext`. Loop clássico do
VDI 2230 / diagrama de Junker.

### 6.3 Trabalho externo por ciclo (transversal)

Em regime puramente elástico (no slip), W_ext = 0 (loading + unloading se
cancelam). Quando há slip transversal:

```
W_ext_per_cycle = 4 · µ_bearing · F_0 · slip_amp
```

onde `slip_amp` é a amplitude de slip transverso (definida na seção 8).
Loop de Coulomb rectangular: 4 vezes (área = F × δ_slip por quarto-ciclo).

### 6.4 Energia amortecida viscosa (Rayleigh, modal axial)

```
W_visc_per_cycle ≈ π · ω · c_xx · X²
```

com ω = 2π·f, X = F_ax / k_eff (amplitude quasi-estática), c_xx do (5.3).

---

## 7. Mecanismos de perda — interface plug-in

Todos implementam `LossMechanism.rate(s, geom, mat, F_amp, θ, freq, N, slip_amp_override=None)`
e retornam `{dF_0, dE_dissipated, ds}` por ciclo. São rodados em paralelo
cada step.

### 7.1 EmbeddingLoss (direção-agnóstico)

**Física:** asperezas se esmagam plasticamente nos primeiros ciclos. Stage I
clássico. Domina nos primeiros ~N_emb ciclos.

**Equação (state-based, spec 2026-07-02 §2.4):**

```
δ_emb(N) = δ_∞ · (1 − exp(−N/N_emb))                       (cumulativa)

δ_alvo = k_emb_scale · δ_∞

dδ_emb = (δ_alvo − δ_emb) · (1 − exp(−1/N_emb))              (por ciclo, state-based)

dF_0 = −k_b · dδ_emb

dE_diss = F_0 · dδ_emb                                        (trabalho plástico)
```

O incremento não é mais função direta do relógio de ciclos N (forma antiga,
removida em 2026-07-02) — satura **por estado**: quando δ_emb → δ_alvo,
dδ_emb → 0. Para junta virgem (δ_emb(0)=0) o resultado cumulativo reproduz
exatamente a forma fechada acima, em N inteiro. Estado inicial não-nulo
(arruela/junta reusada): `DynamicStiffnessAnalyzer(..., initial_embedding_frac=f)`
seeda δ_emb(0) = f·δ_alvo, f∈[0,1] (default 0 = comportamento idêntico ao
anterior a esta mudança).

δ_∞ = `emb_depth`. Saturação total: ΔF_emb_total = k_b · emb_depth.
Para M16 com emb_depth=30µm: ΔF_emb_max = 6.28e8 · 30e-6 = **18.8 kN** = 38% de F₀=50kN.
(Default subido de 12µm→30µm em 2026-06-20: a queda inicial íngreme do M16 shear
exigia k_emb_scale=2.66 com 12µm; com 30µm o nova converge pra ~1.1.)

### 7.2 CreepLoss (direção-agnóstico)

**Física:** relaxamento viscoelástico no tempo, modelo Norton-Bailey logarítmico.
Contribui em toda a vida do joint (sem saturação).

**Equação:**

```
δ_creep(t) = C_creep · F_0 · log(t/t_0 + 1)

por ciclo:
dδ_creep = C_creep · F_0 · [log((t_cur + t_0)) − log((t_prev + t_0))] · k_creep_scale

t_cur = N / freq,  t_prev = (N−1) / freq

dF_0 = −k_b · dδ_creep
dE_diss = F_0 · dδ_creep
```

**Acoplamento:** creep depende do F_0 ATUAL, então quando F_0 cai, creep também
cai. Não-linearidade explícita.

### 7.3 WearLoss (direção-dependente)

**Física:** desgaste Archard nas interfaces bearing, dirigido por slip transverso.

**Equação:**

```
slip_dist = 4 · slip_amp                  (ida + volta, 4× a amplitude)

                     K_archard · F_0 · slip_dist
d_wear = k_scale · ──────────────────────────── · (1 + k_dmg_wear · D)
                        H · A_contact

dF_0 = −k_b · d_wear
dE_diss = k_scale · µ_bearing_eff · F_0 · slip_dist      (atrito × distância)
```

k_scale = `direction_blend(θ, k_wear_scale_ax, k_wear_scale_tr)`.

**Amplificação por dano:** `(1 + k_dmg_wear · D)` multiplica APENAS `d_wear`
(material removido), **não** `dE_diss`. A energia dissipada segue sendo o
trabalho de atrito real; a perda extra de pré-carga por remoção de material é
contabilizada via `U_released` (energia elástica liberada pela queda de F_0).
Amplificar `dE_diss` junto **quebra a conservação** (~40% de resíduo) — não fazer.

**Por que dano acopla no wear:** em disp-mode o **wear domina** a perda de
pré-carga (dirigido por `K_archard`, não por µ). Acoplar dano só em µ teria
alavanca fraca; é o wear que precisa ser amplificado pro colapso do reaperto.

**Crucial:** `slip_amp` é resolvido na seção 8 (depende do modo force vs disp).

### 7.4 RotationalLooseningLoss (direção-dependente, two-factor)

**Física:** o coração do modelo. Two-factor: Fator 1 (Φ anisotrópico) × Fator 2
(projeção sin/cos β).

**Equação:**

```
Cálculo de Φ ativo:
   Φ_ax_active = Φ_eff(ax)   se F_ax < F_sep
                = 1.0          se F_ax ≥ F_sep              (junta separou)

   Φ_tr_active = 0.01                                       se F_tr < F_slip (stick)
                = tr_loose_gain · Phi_tr_correction          se F_tr ≥ F_slip (slip)

Forças de loosening:
   L_ax = Φ_ax_active · sin(β) · F_ax           ┐ Two-factor synthesis
   L_tr = Φ_tr_active · cos(β) · F_tr           ┘
   L_total = √(L_ax² + L_tr²)

Torque de loosening:
   T_loose = L_total · d_2 / 2

Critério de ativação:
   se T_loose ≤ T_resist:   sem loosening
   se T_loose >  T_resist:   slip_fraction = (T_loose − T_resist) / T_loose

Per-cycle:
   k_torsional = k_j_init · d_2 / 2
   dθ = k_scale · slip_fraction · (T_loose − T_resist) / k_torsional

   dF_0 = −k_b · λ · dθ                          ← perda via hélice (Fator 2)
   dE_diss = T_resist · dθ                       ← atrito no filete dissipa
```

k_scale = `direction_blend(θ, k_loose_scale_ax, k_loose_scale_tr)`.

### 7.5 SurfaceDamage (estado modulador, não mecanismo paralelo)

**Física:** junta reapertada já tem a superfície danificada do primeiro aperto
(asperezas amassadas, fretting, debris). O dano cresce com a dissipação de slip
e **realimenta positivamente** a perda de pré-carga → captura o colapso runaway
do reaperto/TP7. **Não** é um mecanismo de perda paralelo (não tem `dF_0`
próprio); é uma variável de estado que *modula* os outros.

**Lei de crescimento** (atualizada no `step_cycle`, depois de F_0):

```
W_slip_cycle = dE_wear + dE_loose          (só dissipação de slip; não emb/creep/visc)

dD = k_damage_scale · c_D · (W_slip_cycle / W_ref) · (1 − D)

D ← clamp(D + dD, 0, 1)
```

O fator `(1 − D)` mantém D ≤ 1 (crescimento saturante). Inativo se `c_D=0`.

**Realimentação (dois canais):**
1. **Atrito** (§4.4): `µ_bearing_eff = µ_bearing·(1 − k_dmg_mu·D)` → reduz `T_resist`
   e `F_slip` → mais loosening/slip.
2. **Wear** (§7.3): `d_wear ·= (1 + k_dmg_wear·D)` → mais material removido →
   mais perda de pré-carga. **Canal dominante em disp-mode.**

Ambos formam loop positivo: mais slip → mais D → menos atrito + mais wear →
mais slip. É o runaway de colapso.

**Ordem no ciclo:** os mecanismos leem o `D` de **início de ciclo** (sem
dependência de ordem); D é atualizado **depois** de F_0. Quando F_0 → 0, o slip
cessa, `W_slip_cycle → 0`, e D estabiliza (monotônico não-decrescente).

**Assinatura do reaperto:** `D_init > 0` é um lever disponível, mas na prática a
calibração o leva a 0 — o crescimento de D durante o ciclo já carrega o colapso.
A distinção física do reaperto/reusada acaba sendo **"dano ativo"** (`c_D, k_dmg_*
> 0`) vs nova/sobretorque (dano inativo).

---

## 8. Modos de carregamento — force vs displacement

### 8.1 Force-controlled (legado)

Usuário passa `F_amp` (amplitude de força transversa de pico). Slip é
**derivado da elasticidade local**:

```
F_tr = F_amp · sin(θ)
k_tr_local = max(k_j_init · 0.3, 1.0)

se F_tr > F_slip:
   slip_amp = (F_tr − F_slip) / k_tr_local
senão:
   slip_amp = 0
```

Válido pra ensaio servohidráulico force-controlled. Para Junker (displacement-
controlled), **subestima slip por ~36×**.

### 8.2 Displacement-controlled (Junker)

Usuário passa `delta_amp` (deslocamento transverso imposto, em m). Slip é
**derivado do deslocamento**:

```
δ_slip_onset = F_slip / k_tr_local                  (deslocamento elástico até slip)
slip_amp = max(0, delta_amp − δ_slip_onset)
```

Para M16, F_0=50kN, µ=0.15: δ_slip_onset = 3450/1.2e9 = **2.9 µm**.
Imposto 0.5 mm → slip_amp = 0.5e-3 − 2.9e-6 = **0.497 mm** por ciclo (36× maior).

### 8.3 Função unificada

```python
def resolve_transverse_slip(state, mat, F_amp, theta, delta_amp=None):
    if delta_amp is not None:
        return max(0, delta_amp - F_slip/k_tr)         # disp-controlled
    F_tr = F_amp * sin(theta)
    return (F_tr - F_slip)/k_tr if F_tr > F_slip else 0   # force-controlled
```

Em **disp-mode**, `F_amp` ainda é passado e usado **APENAS no RotationalLooseningLoss**
como drive (T_loose ∝ F_amp). WearLoss e W_ext_per_cycle usam o slip imposto.

---

## 9. Algoritmo `step_cycle` (pseudo-código)

```
INPUT:  F_amp, θ, freq, delta_amp=None
        (state s já existe; mat e geom fixos)

n = cycle_counter + 1

# Step 0: resolve slip
slip_amp_override = resolve_transverse_slip(s, mat, F_amp, θ, delta_amp)
                  if delta_amp is not None else None

# Step 1: energia externa absorvida (slip hysteresis Coulomb)
W_ext_c = W_ext_per_cycle(s, mat, F_amp, θ, delta_amp)
energy.W_ext += W_ext_c

# Step 2: amortecimento viscoso (Rayleigh)
W_visc_c = W_viscous_per_cycle(s, mat, F_amp, θ, freq)
energy.W_damp_visc += W_visc_c

# Step 3: roda cada LossMechanism em paralelo (todos leem o D de inicio de ciclo)
dF_0_total = 0
dF_0_by_mech = {}                              ← para a decomposição (§12)
para cada mech em [EmbeddingLoss, CreepLoss, WearLoss, RotationalLoosening]:
    res = mech.rate(s, geom, mat, F_amp, θ, freq, n,
                    slip_amp_override=slip_amp_override)
    dF_0_total += res['dF_0']
    dF_0_by_mech[mech.name] = res['dF_0']
    dE_diss_total += res['dE_dissipated']
    para cada campo em res['ds']:
        atualiza s.<campo> += res['ds'][campo]

# Step 4: atualiza F_0 e U_stored
prev_U = energy.U_stored
s.F_0 = max(0, s.F_0 + dF_0_total)            ← CHAVE: F_0 atualizado!
energy.U_stored = U_internal(s)

# Step 4.5: atualiza surface_damage D (driver = slip dissipation deste ciclo)
W_slip = per_mech['wear'] + per_mech['rotational_loosening']
se mat.c_D > 0:
    dD = mat.k_damage_scale · mat.c_D · (W_slip / mat.W_ref) · (1 − s.D)
    s.D = clamp(s.D + dD, 0, 1)

# Step 5: snapshot (carrega dF_0_by_mech e D)
return CycleSnapshot(cycle=n, F_0=s.F_0, ..., dF_0_by_mech=dF_0_by_mech, D=s.D)
```

**Note:** o estado é atualizado **DEPOIS** que todos os mecanismos
calculam suas contribuições do ciclo atual. Mecanismos veem o mesmo `s`
(snapshot do início do ciclo, **incluindo D**), suas contribuições somam-se, e
só então F_0 e D mudam. Isso evita order-dependence entre mecanismos.

---

## 10. Acoplamento entre mecanismos

Este é o ponto **mais importante** do modelo e o que o distingue de uma soma
ingênua de mecanismos independentes. Existem três loops de coupling, todos
mediados por `F_0`.

### 10.1 Loop principal (positive feedback)

```
                       ┌─────────────────────────┐
                       │                          │
                       ▼                          │
       F_0 (preload) ────→ k_j_ax(F_0)            │
                                │                  │
                                ▼                  │
                       Φ_eff(F_0) = k_b/(k_b+k_j)  │
                                │                  │
                                ▼                  │
                       T_loose = Φ·F_amp·...       │
                                │                  │
                                ▼                  │
                       dθ_loose = f(T_loose)       │
                                │                  │
                                ▼                  │
                       dF_0 = −k_b·λ·dθ_loose      │
                                │                  │
                                └──────────────────┘
```

À medida que F_0 cai → k_j cai → Φ_eff sobe → T_loose sobe → dθ sobe → F_0
cai mais rápido. Isso é o **runaway de Stage II**.

### 10.2 Loop wear-loosening (cross-mechanism)

```
F_0 ─→ Wear: dδ_wear = K·F_0·slip/(H·A) ──┐
       Loosening: dF_0 += −k_b·λ·dθ_loose ─┤
                  ↓                         │
                  Σ → dF_0_total ──────────┘ → atualiza s.F_0 → ciclo seguinte
```

Wear e loosening competem pela "captura" de F_0. Se a junta está em regime
de wear severo (k_wear_scale_tr alto), F_0 cai por wear → loosening tem
"menos pré-carga pra perder" → loosening contribui menos. E vice-versa.

A calibração de TP4 (reusada) vs TP6 (sobretorque) mostra isso claramente:
- TP4: k_wear_tr=2.22 (alto), k_loose_tr=0.07 (baixo) → wear domina
- TP6: k_wear_tr=0.09 (baixo), k_loose_tr=2.12 (alto) → loosening domina

### 10.3 Loop creep-rigidez

```
F_0 ─→ Creep: dδ_creep = C·F_0·log(t+1) ──→ dF_0 = −k_b·dδ_creep
                                              ↓
                                              F_0 cai
                                              ↓
                                              Próximo ciclo: dδ_creep
                                              calculado com F_0 menor (auto-decay)
```

Creep é auto-suprimido: à medida que F_0 cai, a contribuição do creep também
cai linearmente. Sem feedback positivo — comportamento de "saturação suave".

### 10.4 Embedding NÃO acopla com F_0 dinamicamente

```
dδ_emb = (δ_alvo − δ_emb) · (1 − exp(−1/N_emb))        [δ_alvo = k_emb_scale · δ_∞]
```

Note que F_0 **não aparece**. Embedding acopla à sua PRÓPRIA variável de
estado δ_emb — satura quando δ_emb → δ_alvo — e não ao número de ciclos N
diretamente, nem a F_0. Por isso é Stage I "puro" — para uma junta virgem
satura em ~3·N_emb ciclos independente do que acontece depois. Quando F_0
sobe (ex. reaperto), embedding **NÃO renova** — seria preciso resetar/reduzir
δ_emb diretamente (esta forma não tem mais um "cycle counter" pra resetar).

(Limitação física do modelo atual; em realidade, asperezas amassadas podem
"deformar de novo" se relubrificadas ou se a carga muda direção.)

### 10.5 Tabela resumo do acoplamento

| Mecanismo | Depende de F_0? | Modifica F_0? | Acoplamento positivo? |
|---|---|---|---|
| Embedding | Não (state-based via δ_emb) | Sim (−k_b·dδ_emb) | Não |
| Creep | **Sim** (linearmente) | Sim (−k_b·dδ_creep) | **Auto-supressor** |
| Wear | **Sim** (linearmente em F_0) | Sim (−k_b·d_wear) | Auto-supressor |
| Rotational Loosening | **Sim** (via Φ não-linear) | Sim (−k_b·λ·dθ) | **PARTIALLY POSITIVE** (via Φ→T_loose) |

---

## 11. Conservação de energia

O modelo mantém contabilidade rigorosa de **todas** as fontes e sumidouros de
energia. Verificação por:

```
W_ext_externo_absorvido + U_released_do_reservatório  =  Σ W_dissipado_por_mecanismo

ou em termos de residual:

residual = W_ext + (U_init − U_stored) − (W_visc + W_emb + W_creep + W_fric_y + W_loose)
```

**Deve ser ≈ 0** se o modelo é internamente consistente. Em runs com defaults
calibrados, residual fica em ~0.04% do total — fechado pra todos os fins. Com
dano **brando** continua fechado (<1%). No regime de **colapso agressivo**
(dano alto levando F_0→0) o residual degrada — a energética da remoção de
material por wear amplificado é fenomenológica, não rigorosa. O tuner reporta o
residual como canário; não confie nele no regime de colapso.

Acessível via `analyzer.energy.conservation_residual`.

---

## 12. Calibração — profiles e tuners

### 12.1 Estrutura do `joint_calibrations.json`

```json
{
  "global_settings": { "geometry": "M16...", "loading": "shear..." },
  "profiles": {
    "nova":         {"tuners": {...}, "fit_quality": {"MAE": 0.022, ...}},
    "reusada":      {"tuners": {...}, "fit_quality": {"MAE": 0.026, ...}},
    "sobretorque":  {"tuners": {...}, "fit_quality": {"MAE": 0.007, ...}},
    "reaperto":     {"tuners": {...}, "fit_quality": {"MAE": 0.013, ...}}
  }
}
```

### 12.2 Sequência de calibração mínima recomendada

Especificada em `docs/superpowers/specs/2026-05-17-calibration-experiments.md`:

| Exp | Carga | Calibra |
|---|---|---|
| 1 | Estático (rampa) até F_sep | `k_j_init`, `α_GW` (Greenwood-Williamson) |
| 2 | Estático sustentado (creep hold) | `C_creep` |
| 3 | Cíclico baixa amplitude (sem slip) | `emb_depth`, `N_emb`, `k_emb_scale` |
| 4A/T | Cíclico amplitude crescente (slip onset) | `µ`, `slip_onset_factor`, `Phi_{ax,tr}_correction` |
| 5A/T | Cíclico full (Junker completo) | `k_wear_scale_{ax,tr}`, `k_loose_scale_{ax,tr}` |

### 12.3 Calibração em estágios (`StagedCalibrator`, pacote `calibration/`)

Substitui o fit global único (DE+least_squares sobre um custo escalar) por
**coordenada-descida por estágio com travas**:

```
fit(I)   → trava k_emb_scale
fit(II)  → trava {k_wear_tr, k_loose_tr, Phi_tr_corr, k_damage_scale}
fit(III) → trava k_creep_scale
repete I→II→III por n_passes
```

Cada estágio resolve `least_squares` (bounded, trf) sobre seus tuners, com
**regularização física**: resíduo += `√λ · (p − 1)` por tuner livre → puxa pra
1.0. `λ=0.001` é o ponto certo (tuners interpretáveis, sem saturar); `λ` alto
piora o MAE, `λ≈0` deixa saturar. **"Física em 1º" = perto de 1 + sem saturar,
NÃO mínimo MAE.** Saturação só é problema no bound **superior** (amplificação
patológica); no inferior = "mecanismo desligado", legítimo.

`StageSegmentation` reporta **MAE por segmento**; `MechanismDecomposition` dá o
**share de cada mecanismo por estágio** (via `CycleSnapshot.dF_0_by_mech`).

### 12.4 Profiles atuais (M16 ±0.5mm 0.5Hz, disp-mode, rev. 2026-06-20)

| Perfil | k_emb | k_creep | k_wear_tr | k_loose_tr | Phi_tr | k_dmg | dano | MAE |
|---|---:|---:|---:|---:|---:|---:|:--:|---:|
| **nova** | 1.10 | 0.00 | 0.60 | 1.05 | 1.05 | 1.00 | off | 0.036 |
| reusada | 0.19 | 1.50 | 0.80 | 1.05 | 0.99 | 1.15 | on | 0.031 |
| sobretorque | 0.75 | 0.00 | 0.11 | 0.98 | 0.94 | 1.00 | off | 0.017 |
| reaperto | 1.00 | 1.07 | 1.26 | 1.08 | 1.07 | 1.15 | on | 0.035 |

Starters físicos de dano (perfis com dano): `c_D=2, k_dmg_mu=1, k_dmg_wear=4, W_ref=1e4`.
(`emb_depth` default = 30µm desde 2026-06-20 → todos os `k_emb` ≈ 1 ou 0.)

**Leitura física:**
- Nova: tuners ≈ 1 (incl. `k_emb=1.10` após subir `emb_depth` pra 30µm).
- Reusada: `k_emb=0.19` (arruela reusada já assentada); dano ativo carrega o
  colapso da cauda; tuners de wear/loose ≈ 1.
- Sobretorque: wear baixo (alta pré-carga suprime slip), sem dano.
- **Reaperto: agora fita** (MAE 0.031) com `k_loose=1.08` **livre** — antes
  saturava em 10 e nem assim fitava. O `surface_damage` amplificando o wear é o
  que captura o colapso. (Antes era a limitação conhecida nº 2 do roadmap.)

O fit interpretável (~0.036) é pior em MAE puro que o global antigo (nova 0.022),
mas aquele exigia `Phi_tr=0.10` (longe de 1, pouco físico) — trade-off escolhido.

---

## 13. Referências físicas

| Equação/Conceito | Fonte original | Onde aparece |
|---|---|---|
| F_slip = 0.46·µ·F_0 | Pai & Hess 2002 (JSV 245:5) | §4.5 |
| k_j(F_0) power-law | Greenwood-Williamson 1966 | §4.1 |
| Embedding 1−exp(−N/N_emb) | Norton (clássico fitting) | §7.1 |
| Creep log(t) | Norton-Bailey (steel @ RT) | §7.2 |
| Archard wear V = K·F·s/H | Archard 1953 | §7.3 |
| Wear amplificado por dano (abrasão 3-corpos) | fenomenológico BAS V2 | §7.3, §7.5 |
| Two-factor Φ anisotropic | Spec interno BAS V2 §12 | §4.2, §7.4 |
| Helix coupling k_b·λ | VDI 2230 (translation-rotation) | §5.2 |
| Junker test methodology | DIN 65151 / Junker 1969 | §8.2 |
| Maney/VDI load factor | VDI 2230 Part 1 | §4.2 |
| Energy budget framework | Spec interno BAS V2 §12 | §6, §11 |

---

## 14. Quick reference — variáveis principais

| Símbolo | Unidade | Significado | Local |
|---|---|---|---|
| F_0 | N | Pré-carga residual | `state.F_0` |
| F_0_init | N | Pré-carga inicial | `state.F_0_init` |
| Φ | - | Razão rigidez bolt/(bolt+joint) | `Phi_eff()` |
| k_b | N/m | Rigidez axial do parafuso | `geom.k_b` |
| k_j_ax | N/m | Rigidez axial do joint (não-linear em F_0) | `k_j_ax()` |
| β | rad | Ângulo da hélice | `geom.beta` |
| λ | m/rad | Lead per radian = p/(2π) | `geom.lead_per_radian` |
| d_2 | m | Diâmetro de passo | `geom.d_2` |
| F_slip | N | Threshold transverso (Pai-Hess) | `F_slip_transverse()` |
| F_sep | N | Carga de separação axial | `F_sep_axial()` |
| T_loose | N·m | Torque de loosening | inline in `RotationalLooseningLoss` |
| T_resist | N·m | Torque resistente (atrito filete+bearing) | `T_resistance()` |
| slip_amp | m | Amplitude de slip por ciclo | `resolve_transverse_slip()` |
| Ψ_tr_active | - | Φ_tr efetivo (saturado ou via slip flag) | inline |
| tr_loose_gain | - | Ganho transverso (era hardcoded 0.95) | `mat.tr_loose_gain` |
| D | - | surface_damage ∈ [0,1] | `state.D` |
| µ_bearing_eff | - | atrito bearing modulado por dano | `mu_bearing_eff()` |

---

## 15. Para próximas iterações do modelo (TODO físico)

1. ~~Surface damage state variable~~ ✅ **feito** (2026-06-20, §7.5) — reaperto/TP7 fita.
2. **F_amp coupling em disp-mode** — atualmente F_amp e delta_amp são independentes;
   fisicamente F_amp ≤ µ·F_0 em disp-mode pleno slip. Adicionar resolução
   simultânea seria mais físico.
3. **Embedding renewal on F_0 increase** — atualmente embedding não "ressuscita"
   se a junta é re-apertada; em realidade asperezas podem deformar de novo.
4. **Bilinear pre-separation slope (Stage I axial)** — vide spec §12, joint
   diagram tem inclinação não-zero antes da separação.
5. **CRP coupling (Stage III creep-relaxation-plasticity)** — para temperaturas
   elevadas / tempos muito longos.
6. **Energética rigorosa da remoção de material (wear amplificado)** — hoje a
   amplificação de `d_wear` por dano fecha a conservação via `U_released` no
   regime brando, mas degrada no colapso (§11). Um budget rigoroso de energia
   abrasiva tornaria o residual confiável até F_0→0.
7. ~~Subir `emb_depth` default~~ ✅ **feito** (2026-06-20, 12µm→30µm) — nova
   `k_emb`≈1.1; todos os perfis melhoraram ou ficaram iguais.

---

*Última revisão: 2026-06-20. Implementação em
`src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` e pacote
`src/bolt_analysis_studio/calibration/`.*
