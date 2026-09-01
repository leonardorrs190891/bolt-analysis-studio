# REFERÊNCIA DO MODELO — DynamicStiffnessAnalyzer (BAS V2)

> **Documentação completa e detalhada do engine V2** de auto-afrouxamento de
> juntas aparafusadas. Fonte: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py`.
> Reflete o estado do modelo em 2026-07-09 (pós-Estágio B: a camada de tuners foi
> removida; o engine roda só com constantes físicas). Veredictos de física e
> falsificações: `MODEL_LEGITIMACY.md`. Casos de validação e reports individuais:
> `validation_html/validation_report.html`. (A versão pré-2026-07 está arquivada
> em `MODEL_MATH_REFERENCE_v1_legacy.md`.)

## Índice

0. Filosofia — modelo empírico-analítico de três camadas
1. Geometria da junta (`JointGeometry`)
2. Vetor de estado lento (`SlowState`)
3. Constantes físicas do material/contato (`JointMaterial`)
4. Mecanismos de perda de pré-carga (os 6)
5. Modos de formulação, regimes de slip e gates
6. Capabilities opt-in (default-inert)
7. Balanço de energia e algoritmo `step_cycle`
8. Calibração e graus de liberdade
9. Validação

---

## 0. Filosofia: modelo EMPÍRICO-ANALÍTICO de três camadas

O afrouxamento é a evolução de um **vetor de estado lento** `s` sob ciclagem. A
cada ciclo, uma matriz de rigidez dinâmica `[K(s)]` é reavaliada (softening de
Greenwood-Williamson), e **seis mecanismos de perda em paralelo** drenam a
pré-carga `F_0`. As três camadas:

- **Analítica** — Hooke (rigidez do parafuso `k_b`), Coulomb (atrito), hélice
  (conversão rotação↔preload), conservação de energia rigorosa.
- **Empírica** — leis fenomenológicas de literatura: Norton (embedding),
  Norton-Bailey (creep log-t), Archard (wear), Greenwood-Williamson (softening),
  Cattaneo-Mindlin (partial/gross slip), Su-N/Goodman (fadiga).
- **Constantes físicas com procedência** — cada constante é medida, de handbook,
  lida de uma feature do dado, ou fitada-this-rig, com a procedência **declarada**
  (não há multiplicadores adimensionais livres desde o Estágio B).

**Teoria two-factor** (contribuição central): o afrouxamento rotacional é o
produto de um **Fator 1** anisotrópico (razão de rigidez `Φ_eff`, que sobe
conforme `F_0` cai) e um **Fator 2** de projeção pela hélice (`sin β`/`cos β`) —
o único acoplamento axial-torsional de `[K]`.

**Doutrina de robustez:** capabilities opt-in **default-inert** (bit-idênticas
quando desligadas, ligadas só com falsificação dupla + gate pré-declarado);
constantes per-rig com procedência; falsificações registradas AS-IS; "formas
transferem cross-rig, níveis/constantes são per-rig" (§8 do LEGITIMACY,
reconfirmado 5×).

---

## 1. Geometria da junta (`JointGeometry`)

Descreve a estrutura MSD da junta (dataclass `JointGeometry`). Campos e derivados:

| Símbolo | Campo | Significado | Fórmula/nota |
|---|---|---|---|
| `E` | `E` | Módulo de Young [Pa] | aço `200e9` |
| `A_s` | `A_s` | Área de tensão da rosca [m²] | ISO 724 |
| `L_eff` | `L_eff` | Comprimento efetivo (grip) [m] | ~grip da junta |
| `d_2` | `d_2` | Diâmetro de passo [m] | ISO: `d − 0.6495·p` |
| `p` | `pitch` | Passo [m] | |
| `r_bearing` | `r_bearing` | Raio efetivo de apoio [m] | |
| `A_contact` | `A_contact` | Área nominal de contato bearing [m²] | anel real `π(r_b²−r_furo²)` (§4.9-11g) |
| `k_b` | (prop.) | Rigidez axial do parafuso [N/m] | `k_b = E·A_s/L_eff` |
| `β` | (prop.) | Ângulo de hélice [rad] | `arctan(p/(π·d_2))` |
| `lead_per_radian` | (prop.) | Avanço da hélice [m/rad] | `p/(2π)` |

A **cadeia MSD** física da junta: `GROUND — bolt shank (k_b) — thread contact
(hélice λ, atrito de filete) — bearing (µ, wear) — member(s) — flange`. Toda a
tribologia (atrito, wear) vive nos **contatos**, nunca nos componentes; a hélice
é o único acoplamento axial-torsional de `[K]`.

---

## 2. Vetor de estado lento (`SlowState`)

O estado que evolui ciclo a ciclo (dataclass `SlowState`):

| Campo | Símbolo | Significado | Driver |
|---|---|---|---|
| `F_0` | `F_0` | Pré-carga residual [N] | soma dos `dF_0` dos 6 mecanismos |
| `F_0_init` | `F_{0,init}` | Pré-carga inicial [N] (fixa) | referência (nunca muda no ciclo) |
| `delta_emb` | `δ_emb` | Profundidade de assentamento [m] | EmbeddingLoss |
| `delta_creep` | `δ_creep` | Recalque de creep [m] | CreepLoss |
| `delta_wear` | `δ_wear` | Material removido (bearing) [m] | WearLoss |
| `delta_thread_fret` | `δ_fret` | Fretting de flanco [m] | ThreadFrettingLoss |
| `theta_loose` | `θ_loose` | Rotação acumulada da porca [rad] | RotationalLoosening |
| `D` | `D` | Surface damage ∈ [0,1] | dissipação de slip (modula µ, wear) |
| `D_fatigue` | `D_fat` | Dano de Miner ∈ [0,1] | FatigueLoss |
| `W_slip_acc` | `W_slip` | Trabalho de slip cru acumulado [J] | driver da incubação (`slip_onset`) |
| `W_conf` | `W_conf` | Trabalho de conformação (pressure-weighted) [J] | driver da conformação |

O `F_0` só é atualizado **depois** de todos os mecanismos computarem seu `dF_0`
(sem dependência de ordem); `D` e `W_slip_acc`/`W_conf` são atualizados **após**
`F_0`, e são lidos no **início** do ciclo seguinte (padrão "lê no início, atualiza
depois").

---

## 3. Constantes físicas do material/contato (`JointMaterial`)

Pós-Estágio B, `JointMaterial` contém **só constantes físicas + estados nomeados +
capabilities opt-in** (a antiga camada de 9 tuners adimensionais foi removida). As
constantes físicas nucleares:

| Campo | Default | Unidade | Papel | Procedência |
|---|---|---|---|---|
| `mu_thread` / `mu_bearing` | 0.15 | – | Atrito de rosca / apoio | medido (Motosh de T+F₀) ou assumido |
| `emb_depth` | 30e-6 | m | Assíntota do assentamento (f_Z) | handbook VDI (Rz) OU data-implícito da queda-inicial (L24) |
| `N_emb` | 50 | ciclos | Constante de tempo do assentamento | Estágio A compartilhada |
| `k_wear_spec` | 5e-14* | 1/Pa | **Razão de wear K/H (canônica)** | merge §4.42a; 0 ⇒ via legada `K_archard/hardness` |
| `C_creep` | 1.867e-11 | m·N⁻¹ | Coeficiente de Norton-Bailey | por par tribológico (§4.7) |
| `t_0` | 1.0 | s | Tempo de referência do creep | |
| `tr_loose_gain` | 2.0 | – | Ganho transversal do loosening (Fator 1) | Estágio A (âncora pendente §4.42) |
| `k_j_init` | 4e9 | N/m | Rigidez GW inicial da junta | congelado S≈0 (§4.42c) |
| `alpha_GW` | 0.5 | – | Expoente Greenwood-Williamson | congelado S≈0 |
| `c_bend` | 1.0 | – | Compliance de flexão transversal | **per-rig** (o único knob transversal, §4.35) |
| `loose_arrest_floor` | 0.0 | – | Piso de arresto | lido do fim do dado |

*O bloco `shared` canônico usa `k_wear_spec=5e-14` (= K/H de 1e-4/2e9, migrado
2026-07-09); o default do dataclass é 0.0 (via legada, backward-compat). As
capabilities opt-in (default-inert) estão na §6; os modos (campos string) na §5.

**Merge K/H (§4.42a):** `K_archard` e `hardness` só aparecem como razão K/H no
engine — `(2K,2H)≡(K,H)` bit-a-bit — logo são não-identificáveis em separado;
`k_wear_spec = K/H` [1/Pa] é o parâmetro canônico.

---

## 4. Mecanismos de perda de pré-carga

O engine V2 trata o afrouxamento como a evolução do vetor de estado lento. A cada ciclo, seis mecanismos plug-in (subclasses de `LossMechanism`) são consultados em paralelo via `rate(state, geom, mat, F_amp, theta_load, freq, cycle_N, slip_amp_override) -> {dF_0, dE_dissipated, ds}`. Todos veem o `F_0` de **início de ciclo** (sem dependência de ordem); `F_0` só é atualizado depois de somados todos os `dF_0`.

**Padrão de conversão comum.** Os quatro mecanismos de "profundidade" (embedding, creep, wear, fretting) produzem `Δδ` [m] e o convertem em perda pelo **encurtamento da pilha**: `ΔF_0 = −k_b·Δδ`, `k_b = E·A_s/L_eff`. O afrouxamento rotacional converte rotação em perda via a **hélice** (`lead_per_radian = p/2π`); a fadiga é um **cliff** discreto.

> **Estágio B (2026-07-09):** a antiga camada de tuners (`k_emb_scale`, `k_creep_scale`, `k_wear_scale_*`, `k_loose_scale_*`, `Phi_*_correction`, `k_damage_scale`) foi **REMOVIDA**. Os mecanismos leem **apenas constantes físicas** (`emb_depth`, `C_creep`, `k_wear_spec` [=K/H], `tr_loose_gain`, `c_D`). Payloads/.msd legados são traduzidos na fronteira por `calibration.tuner_shim.translate_legacy_tuners`.

Muitos gates seguem o padrão **"`dF_0` sim, `dE` não"**: suprimem a perda de pré-carga mas não o calor de atrito (`dE`) nem o acúmulo de `W_slip_acc`.

### 4.1 EmbeddingLoss — assentamento plástico das asperezas
Achatamento plástico das rugosidades sob a carga de aperto; domina os primeiros ~`N_emb` ciclos. Forma *state-based* (o incremento depende da profundidade **ainda disponível**). Para junta virgem integra EXATAMENTE `δ_emb(N) = δ_target·(1 − e^{−N/N_emb})`.

- `δ_target = emb_depth·S_conf·S_ρ + emb_load_frac·g_slip·F_{0,init}/k_b`
- `Δδ = max(δ_target − δ_emb, 0)·(1 − e^{−1/N_emb})`
- `ΔF_0 = −k_b·Δδ`, `Δδ_emb = +Δδ`, `dE = F_0·Δδ` → bucket `W_diss_emb`.

Lê `emb_depth`, `N_emb`. Modulado por: `embedding_conformance_factor` (`emb_conform_exp`, `p_ref_emb`), `settling_amplitude_factor` (`emb_amp_exp`, `rho_ref_emb`; ρ=F_ax_amp/F_0_init), `emb_load_frac`, `emb_slip_gate`, `k_emb_renew` (só em `retighten`). Todos default 0 ⇒ S=1, bit-identical.

### 4.2 CreepLoss — creep logarítmico no tempo (Norton-Bailey)
Relaxação viscoelástica log-`t`; taxa ∝ `F_0` corrente. Com `t = cycle_N/freq`:
- `Δδ = C_creep·F_0·[ln(t+t_0) − ln(t−1/f+t_0)]·S_creep`
- `ΔF_0 = −k_b·Δδ`, `dE = F_0·Δδ` → bucket `W_diss_creep`.

Lê `C_creep` (default 5e-11), `t_0`. Modulado por `creep_conformance_factor` (`creep_conform_exp`). `C_creep` é **por par tribológico** (§4.7).

### 4.3 WearLoss — desgaste de Archard no bearing (slip transversal)
Remoção de material na face do bearing por slip transversal. Em disp-mode o wear DOMINA a perda (dirigido por `k_wear_spec`, não por µ). `slip_dist = 4·slip`:
- `d_wear = k_run·k_wear_spec·F_0·slip_dist/A_contact` (ou legado `K_archard·F_0·slip_dist/(H·A_contact)` se `k_wear_spec=0`)
- `d_wear *= (1 + k_dmg_wear·D)·g_onset·g_conf·g_partial`
- `ΔF_0 = −k_b·d_wear`; `dE = µ_bearing_eff·F_0·slip_dist` (trabalho de atrito REAL, **não** amplificado nem gateado) → bucket `W_diss_friction_y`.

A perda extra por remoção de material é balanceada via `U_released` (amplificar `dE` quebraria a conservação, ~40% residual). Modulado por: `k_wear_spec` (merge K/H), running-in (`k_wear_running`/`N_wear_run`; `k_run = 1+(k−1)·e^{−N/N_run}`), dano (`k_dmg_wear`), incubação (`slip_onset_gate`), conformação (`conformation_gate`), partial-slip CM (`partial_slip_gate` canal "wear").

### 4.4 RotationalLooseningLoss — afrouxamento two-factor (mecanismo central)
**Fator 1** = razão de rigidez `Φ_eff(s)` (sobe conforme F_0 cai); **Fator 2** = projeção pela hélice. Kernel de torque (default `loose_rate_mode="torque"`):
- `F_ax = F_amp·cosθ`, `F_tr = F_amp·sinθ`
- `Φ_tr_active = 0.01` se `F_tr < F_slip` senão `tr_loose_gain`; `Φ_ax_active = Φ_eff` se `F_ax < F_sep` senão 1
- `L_total = hypot(Φ_ax·sinβ·F_ax, Φ_tr·cosβ·F_tr)`, `T_loose = L_total·d_2/2`
- `T_resist = µ_th·F_0·d_2/(2cosα) + µ_brg_eff·F_0·r_brg`
- Se `T_loose > T_resist`: `slip_fraction = (T_loose−T_resist)/T_loose`, `Δθ = gates·slip_fraction·(T_loose−T_resist)/k_torsional` (+ ratchet, teto)
- `ΔF_0 = −k_b·(p/2π)·Δθ`, `dE = T_resist·(Δθ+Δθ_free)` → bucket `W_diss_loose`.

`k_torsional = k_j_init·d_2/2` (legacy) ou `η·G·J/L_eff`, `J=π·d_2⁴/32` (`bolt_torsion`). Em disp-mode é **runaway-to-zero** uma vez disparado (`s_crit=δ_t=µF_0/k_tr` cai com F_0). O kernel alternativo `graded_scrit` troca por `Δθ = gates·k_loose_graded·max(0, slip−s_crit_loose)/(d_2/2)` (amplitude-sensível, sem runaway, colapso quase-linear). Lê `tr_loose_gain`. Modulado por: `loose_rate_mode`, `loose_torsion_mode`/`eta_loose`, `loose_kin_ceiling`, `k_ratchet`/`ratchet_torque_coupled`, `free_spin`, `self_locking_gate`/`loose_arrest_floor`, `crash_trigger_frac`, `loosening_slip_gate`, `couple_famp_slip`, incubação, conformação.

### 4.5 ThreadFrettingLoss — fretting de flanco de rosca AXIAL (∝ A_F)
Forma faltante da falsificação axial (§4.6): perda dirigida pela amplitude axial `A_F = F_amp·|cosθ|`. `dF_0 = −k_b·d_fret` e `d_fret ∝ F_0·(F_ax/k_b)` ⇒ `dF_0 ∝ −F_0·A_F` (k_b cancela). Guarda: `k_thread_fret>0`, `F_ax>1e-6`, `F_0>0`; `fret_dist = 4·F_ax/k_b`:
- `d_fret = k_thread_fret·k_wear_spec·F_0·fret_dist/A_s` (denominador `A_s`, não `A_contact`)
- `d_fret *= (f_ref_fret/f)^{fret_freq_exp}·g_partial`
- `ΔF_0 = −k_b·d_fret`; `dE = µ_thread·F_0·fret_dist` → bucket `W_diss_wear` E **`W_ext += dE`** (sourced pela carga axial).

Inerte em transversal (`F_ax≈0` em θ=π/2) e com `k_thread_fret=0`. Modulado por: `fret_freq_exp`/`f_ref_fret` (freq menor ⇒ mais dwell/oxidação, §4.39), partial-slip CM (canal "fret").

### 4.6 FatigueLoss — fadiga de raiz de rosca → fratura (cliff)
Miner sobre Su-N bilinear (Yang cl.10.9) + Goodman; `σ_m = F_0/A_s` evolui com o afrouxamento. Guarda: `fatigue_enabled`, `F_0>0`, `D_fatigue<1`:
- `σ_a = K_t·|F_amp|/A_s`, `σ_ar = σ_a/(1 − σ_m/σ_uts)` (Goodman)
- `N_f = ∞` (σ_ar≤endurance) | `C_1·σ_ar^{−m_1}` (≥knee) | `C_2·σ_ar^{−m_2}` (senão); `ΔD_fat = 1/N_f`
- Se `D_fatigue+ΔD_fat ≥ 1` (fratura): `ΔF_0 = −(F_0 − fatigue_residual_frac·F_0_init)`, senão `dF_0=0`
- `dE = U_internal(F_0) − U_internal(F_res)` (energia elástica liberada) → bucket `W_diss_fracture`.

Inerte por default (`fatigue_enabled=False`). A bilinear Su-N transfere cross-material a ~2.3× (§ fatigue-tail).

### Roteamento de energia (o nome do bucket NÃO casa com o do mecanismo)
| Mecanismo | bucket | `W_ext += dE`? |
|---|---|---|
| embedding | `W_diss_emb` | não |
| creep | `W_diss_creep` | não |
| **wear** | **`W_diss_friction_y`** | não |
| rotational_loosening | `W_diss_loose` | não |
| **thread_fretting** | **`W_diss_wear`** (+ `dE_partial`) | **sim** |
| fatigue | `W_diss_fracture` | não |

O **surface_damage** `D` cresce de `W_slip_cycle = dE_wear + dE_loose (+ dE_partial)`, gateado por dwell (`dmg_dwell_exp`) e onset (`damage_onset_gate` via `W_crit`, OU contínuo `dmg_gross_exp`): `dD = c_D·dwell·(W_slip_cycle/W_ref)·(1−D)·onset`. `W_slip_acc` acumula o slip cru `4·µ_brg_eff·F_0·slip`; `W_conf` o mesmo ponderado por `(p/p_ref_conform)^n`.

---

## 5. Modos de formulação, regimes de slip e gates

Constantes físicas de escala: `E_STEEL=200e9 Pa`, `G_STEEL=77e9 Pa`, `SLIP_ONSET_PAI_HESS=0.46`, `THREAD_FLANK_ANGLE=30°`. Todos os modos são **default-inerte** (o valor default é bit-identical ao motor pré-feature).

### 5.1 Modos de formulação (campos string de `JointMaterial`)

**`k_tr_mode`** — rigidez transversal de onset de slip `k_tr` (define `δ_t = F_slip/k_tr`):
- `"axial_frac"` (default): `k_tr = max(0.3·k_j_init, 1)` ≈ 1.2e9 N/m ⇒ `δ_t≈0` ⇒ quase todo o curso vira gross slip. Backward-compat.
- `"bending"` (requer geom): flexão do parafuso `I = π·d_2⁴/64`, `k_tr = max(c_bend·E·I/L_eff³, 1)` ≈ 1e7 N/m ⇒ `δ_t ~ 0.3mm`, prop. `F_0·L³/(E·d⁴)` (unifica amplitude+preload+rigidez de membro). `c_bend` per-rig.
- Cisalhamento de membro em série (`k_member_shear>0`): `k_tr = 1/(1/k_tr + 1/k_member_shear)`.

**`loose_torsion_mode`** — `k_torsional` no denominador do loosening:
- `"legacy"` (default): `k_torsional = k_j_init·d_2/2` ≈ 3.7e7 N·m/rad. Bit-identical.
- `"bolt_torsion"`: `J = π·d_2⁴/32`, `k_torsional = max(eta_loose·G·J/L_eff, 1)` ≈ 4e3 N·m/rad (~5000× menor) ⇒ o runaway `T_resist∝F_0` dispara. `eta_loose` = eficiência de travamento (O(1-10)). Só com o gate de onset ligado.

**`conform_driver`** — driver do `W_conf` (só se `W_conf_ref>0`). Incremento `dW_conf = (p/p_ref_conform)^{conform_pressure_exp}·(4·µ_brg_eff·F_0·slip)`, `p = F_0/A_contact`:
- `"raw"` (default): `W_conf += dW_conf` (monotônico). Bit-identical.
- `"effective"`: `W_conf += dW_conf·conformation_gate` ⇒ driver **auto-limitante** (plateau <1). É o driver **ADOTADO** no bloco `shared` canônico (resolve o sobretorque, §4.9).

**`slip_regime_mode`** — regime Cattaneo-Mindlin `r = Q/(µ·F_0·κ)`:
- `"off"` (default): gates = 1. Bit-identical.
- `"cattaneo_mindlin"`: liga (1) loosening por fração gross `g = (slip/(slip+δ_t))^{slip_regime_sharpness}`; (2) wear/fretting × `partial_slip_gate` (F_0 maior ⇒ r menor ⇒ menos fretting, slope Liu2017); (3) habilita `k_partial_slip` e `couple_famp_slip`.

**`loose_rate_mode`** — kernel do loosening: `"torque"` (default, runaway) vs `"graded_scrit"` (taxa cinemática no excesso de slip sobre `s_crit` fixo; ver §4.4).

**`loosening_slip_coupling`** — `"off"` (default) vs `"gross_fraction"` (`g = slip/(slip+δ_t)`; Junker exige gross slip; requer `k_tr_mode="bending"`).

### 5.2 Gates e funções constitutivas auxiliares

- **`slip_onset_gate`** (incubação Hill): `g = x^k/(x^k+1)`, `x = W_slip_acc/slip_onset_W`, `k = slip_onset_sharpness`. Suprime `dF_0` slip-driven até `W_slip_acc` cruzar `slip_onset_W` (platô estágio-I de Jiang). `slip_onset_W≤0 ⇒ 1` exato. Gateia `dF_0`, **não** `dE`.
- **`damage_onset_gate`** (W_crit): espelha o slip_onset mas gateia o crescimento `dD`. `W_crit≤0 ⇒ 1`. Usado só quando `dmg_gross_exp=0`.
- **`conformation_gate`** (arresto alta pressão): `g = W_conf_ref/(W_conf + W_conf_ref)` — gate **FECHANDO** (1→0): conforme `W_conf` cresce, a perda slip-driven se arresta (platô do sobretorque). `W_conf_ref≤0 ⇒ 1`.
- **`self_locking_gate`** (arresto/piso): `F_min = loose_arrest_floor·F_0_init`, `g = max(0, 1 − F_min/F_0)` — o ratcheting só drena o excesso sobre um núcleo auto-travado ⇒ runaway vira **S-curve com ponto fixo estável em `F_min`**. `loose_arrest_floor≤0 ⇒ 1`.
- **`loosening_slip_gate`** (fração gross): CM `(slip/(slip+δ_t))^{sharpness}` ou gross_fraction `slip/(slip+δ_t)`, `δ_t = delta_free + F_slip_transverse/k_tr`. Force-mode ⇒ 1.
- **`partial_slip_gate`** (Cattaneo-Mindlin): `r = Q/(µ·F_0·slip_capacity_coeff)`; `r≥1 ⇒ 1`, senão `g = 1 − (1−r)^{partial_slip_exp}`. Canais "fret" (Q=|F_amp·cosθ|, µ=mu_thread) e "wear" (Q=|F_amp·sinθ|, µ=mu_bearing_eff). `slip_regime_mode≠CM ⇒ 1`.
- **`direction_blend`**: `k_eff(θ) = val_ax·cos²θ + val_tr·sin²θ`.
- **`Phi_eff`** (two-factor): `raw = k_b/(k_b + k_j_ax)`, `return min(raw, 1)`; `k_j_ax = k_j_init·(F_0/F_0_init)^{alpha_GW}` (amolece com F_0). **NOTA:** `Phi_*_correction` foi REMOVIDA no Estágio B.
- **`T_resistance`**: `µ_thread·F_0·d_2/(2cos30°) + µ_brg_eff·F_0·r_bearing`; ∝ F_0 ⇒ fonte do runaway.
- **`F_slip_transverse`**: `0.46·µ_brg_eff·max(F_0,0)` (Pai-Hess 2002); define `δ_t = F_slip/k_tr`.
- **`resolve_transverse_slip`**: disp-mode `slip = max(0, delta_amp − delta_free − F_slip/k_tr)`; force-mode `slip = (F_amp·sinθ − F_slip)/k_tr` se exceder, senão 0. 36× mais preciso em disp-mode.
- **`mu_bearing_eff`**: `µ_bearing·max(1 − k_dmg_mu·D, 0)` — superfície danificada perde atrito ⇒ loosening acelera (colapso reaperto/TP7). `D=0` ou `k_dmg_mu=0 ⇒ µ_bearing` exato. Sinal oposto ao galling de flanco no aperto (`µ_thread·(1+k_gall·D)`).

---

## 6. Capabilities opt-in (default-inert)

Além dos 6 mecanismos nucleares, o engine carrega **~44 capabilities opt-in**: formas físicas candidatas que ficam **exatamente inertes** no default (o valor default torna o termo bit-identical ao motor sem a feature, garantido por teste). Cada uma foi construída sob dupla-falsificação + gate pré-declarado, e só se liga com procedência declarada. **Ligar uma NÃO é fitar um tuner** — é suprir uma forma faltante que uma falsificação apontou.

Doutrina (§8 `MODEL_LEGITIMACY.md`, reconfirmada 5×): **"formas transferem cross-rig; níveis/constantes são per-rig."** A forma (o mecanismo, o expoente, o acoplamento) é física e transferível; a constante que a escala é medida/lida-do-dado por rig. Uma capability default-inerte nunca muda uma predição canônica a menos que explicitamente ligada com um número de procedência declarada.

| Família | Constante(s) | Default inerte | Forma quando ligada | Procedência / §LEGITIMACY |
|---|---|---|---|---|
| **Embedding — conformação** | `emb_conform_exp`, `p_ref_emb` | 0 ⇒ S_conf=1 | assíntota ∝ `(p/p_ref)^exp` (mais pressão, mais assentamento) | §4.9 (caso especial de S_ρ) |
| **Embedding — amplitude** | `emb_amp_exp`, `rho_ref_emb` | 0 ⇒ S_ρ=1 | assíntota ∝ `(A_F/F_0/ρ_ref)^exp` | §4.18 (Liu2017 sweep, R²=0.89) |
| **Embedding — carga** | `emb_load_frac` | 0 | fração elástica `g_slip·F_0/k_b` no δ_target | §4.19 (Lu source) |
| **Embedding — renovação** | `k_emb_renew` | 0 | reabre `δ_emb` no `retighten()` (VDI f_Z renovado) | roadmap #5, §4.10 |
| **Wear — running-in** | `k_wear_running`, `N_wear_run` | 1 ⇒ k_run=1 | transiente `k_run=1+(k−1)e^{−N/N_run}` | Archard running-in |
| **Wear — merge K/H** | `k_wear_spec` | 0 ⇒ via K/H legada | `d_wear ∝ k_wear_spec·F_0·slip/A_contact` | §4.42a (canônico) |
| **Fretting axial** | `k_thread_fret` | 0 | perda ∝ A_F (flanco de rosca) | §4.6 (falsificação axial) |
| **Fretting — freq** | `fret_freq_exp`, `f_ref_fret` | 0 ⇒ ×1 | `(f_ref/f)^exp` (dwell/oxidação) | §4.39 (emb∝1/freq, r=−0.99) |
| **Slip-regime CM** | `slip_regime_mode`, `k_partial_slip`, `slip_capacity_coeff`, `partial_slip_exp` | "off" ⇒ gates=1 | Cattaneo-Mindlin partial/gross; slope Liu2017 | §slip-regime (member-stiffness) |
| **Member — cisalhamento** | `k_member_shear` | 0 ⇒ ∞ (série ignora) | `k_tr` em série com cisalhamento de membro | §4.19 (HDPE aberto) |
| **Damage — surface** | `c_D`, `W_ref`, `k_dmg_mu`, `k_dmg_wear` | `c_D=0` ⇒ D não cresce | D modula µ (↓) e amplifica wear (↑) | §4 reaperto/TP7 |
| **Damage — dwell/onset** | `dmg_dwell_exp`, `W_crit`, `dmg_gross_exp` | 0 ⇒ ×1 / onset≡1 | gate de incubação do dano OU contínuo | §4.33 (Bauer joelho) |
| **Loosening — teto cinemático** | `loose_kin_ceiling` | 0 ⇒ sem teto | limita `Δθ` por ciclo (ratchet saturado) | §4.37 |
| **Loosening — ratchet** | `k_ratchet`, `ratchet_torque_coupled` | 0 | termo cinemático ∝ caminho de slip | §4.15 (Lu kinematic) |
| **Loosening — graded s_crit** | `loose_rate_mode`, `s_crit_loose`, `k_loose_graded` | "torque" | taxa no excesso `slip−s_crit` (sem runaway) | §4.37 (colapso quase-linear) |
| **Loosening — arresto** | `loose_arrest_floor` | 0 ⇒ gate=1 | S-curve com ponto fixo `F_min` (auto-travamento) | §4.10 (#10 adotável) |
| **Loosening — bolt torsion** | `loose_torsion_mode`, `eta_loose` | "legacy" | `k_torsional=η·G·J/L_eff` (físico) | member-stiffness |
| **Loosening — free spin** | `free_spin` | 0 | rotação livre pós-slip | Junker |
| **Loosening — crash** | `crash_trigger_frac` | 0 | colapso abrupto sob limiar de F_0 | grip-runaway |
| **Loosening — F_amp↔slip** | `couple_famp_slip` | False | acopla F_amp ao slip em disp-mode | roadmap #4 |
| **Conformação** | `W_conf_ref`, `conform_pressure_exp`, `p_ref_conform`, `conform_driver` | `W_conf_ref=0` ⇒ gate=1 | arresto de alta pressão (sobretorque) | §4.9 ADOTADO |
| **Incubação (Junker st.1)** | `slip_onset_W`, `slip_onset_sharpness` | 0 ⇒ gate=1 | platô estágio-I Hill antes do colapso | §slip-onset |
| **Galling (aperto)** | `k_gall` | 0 | `µ_thread·(1+k_gall·D)` (declínio dry-vs-oil) | §4.11 (per-lube) |
| **Retighten** | `retighten()` API | não chamado | reset de estados nomeados na re-aperto | roadmap #5 |
| **Fadiga** | `fatigue_enabled`, `fatigue_residual_frac`, Su-N params | False | cliff de fratura (Miner+Goodman) | §fatigue-tail |

**FROZEN_S_ZERO (§4.42c):** quatro constantes têm sensibilidade `S≈0` no tornado (não-fittáveis, `active_candidates` levanta `ValueError` se oferecidas ao otimizador): `k_j_init`, `alpha_GW`, `slip_capacity_coeff`, `partial_slip_exp`. Não são inertes (participam da física) mas o dataset não as identifica ⇒ congeladas por procedência.

---

## 7. Balanço de energia e algoritmo `step_cycle`

### 7.1 Conservação de energia
O engine mantém um budget rigoroso (`EnergyAccount`): `W_ext + ΔU_elastic = Σ W_dissipated`. Os buckets: `W_diss_emb`, `W_diss_creep`, `W_diss_friction_y` (wear), `W_diss_loose`, `W_diss_wear` (fretting+partial), `W_diss_fracture`. O residual `conservation_residual = W_ext + ΔU − Σ W_diss` deve ser ≈ 0.

- `ΔU_elastic = U(F_0) − U(F_0_init)`, `U(F) = F²/(2k_b)` (energia elástica armazenada na pilha).
- **Padrão "dF_0 sim, dE não":** os gates suprimem a perda de pré-carga (`dF_0`) mas o calor de atrito (`dE`) continua real — micro-slip dissipa calor mesmo sem afrouxar. Amplificar `dE` junto com `dF_0` quebraria a conservação (~40% residual no wear-damage). A perda extra de pré-carga por remoção de material é balanceada via `U_released`.
- **Caveat axial (§4.6/roadmap #9):** no modo força o canal viscoso de Rayleigh acumula em `W_damp_visc` sem contraparte em `W_ext` (residual −242 a −12 J); **não** realimenta `F_0` nem afeta MAEs, mas o budget axial fica aberto. Regime de colapso de dano: residual degrada (energética de remoção abrasiva é fenomenológica).

### 7.2 Algoritmo `step_cycle(F_amp, theta_load, freq, delta_amp=None)`
Um ciclo do laço lento:

1. **Lê estado de início de ciclo** — `F_0`, `D`, `W_slip_acc`, `W_conf` (padrão "lê no início").
2. **Resolve o slip transversal** — `resolve_transverse_slip`: disp-mode `slip = max(0, δ_amp − δ_free − F_slip/k_tr)`; force-mode derivado de `F_amp·sinθ`. Este é o driver da maioria dos mecanismos.
3. **Consulta os 6 mecanismos em paralelo** — cada um retorna `{dF_0, dE, ds}` vendo o mesmo `F_0` de início (sem dep. de ordem). Aplica os gates (onset, conformação, partial-slip, self-locking).
4. **Soma os dF_0 e atualiza F_0** — `F_0 ← max(F_0 + Σ dF_0, 0)`. Só agora `F_0` muda.
5. **Atualiza os estados de profundidade** — `δ_emb, δ_creep, δ_wear, δ_fret, θ_loose, D_fatigue` pelos `ds`.
6. **Atualiza D e os acumuladores** — `W_slip_acc += 4·µ_eff·F_0·slip`; `W_conf += dW_conf·(gate se effective)`; `D += c_D·dwell·(W_slip_cycle/W_ref)·(1−D)·onset`. Lidos no início do ciclo seguinte.
7. **Fecha o budget de energia** — soma os buckets, atualiza `W_ext`/`ΔU`, expõe `conservation_residual`.
8. **Emite `CycleSnapshot`** — `F_0`, `ratio=F_0/F_0_init`, `dF_0_by_mech` (decomposição), `D`, wear_µm, ângulo, µ_bearing/µ_thread, energias.

O laço externo chama `step_cycle` por ciclo (capado a 100k no Run da GUI; amostrado na grade V1). A **GUI roteia toda a Run por este engine** (`SolverWorker._compute_v2_history`): preload, wear, ângulo, taxa, D, µ e a decomposição por mecanismo vêm todos de UM modelo (os 4 mecanismos somam EXATAMENTE `F_0·(1−ratio)`), com a conformação dependente de pressão ligada por default.

---

## 8. Calibração e graus de liberdade

### 8.1 Estágio A — "uma física, N estados" (canônico)
A calibração canônica (`SharedCalibrator.fit_parsimonious`, bloco `shared` de `joint_calibrations.json`, schema 2) usa **constantes compartilhadas** entre todas as condições, com as condições distinguidas só por **estados nomeados** (`D_init`, `emb_consumed_frac`, `F0_test` com procedência). Seleção parcimoniosa forward (tol=0.005, log-priors), regularização fraca pull-to-1. Headline: **3 números fitados no dataset inteiro** (`W_conf_ref`, `C_creep`, `F0_test[sobretorque]`); `n`/`p_ref` fixos, `emb_depth` mantido como **input**. MAE por condição 0.030–0.074. LOCO ≈ ao fit (generaliza).

### 8.2 Estágio B — remoção da camada de tuners (2026-07-09)
A antiga camada de 9 tuners adimensionais (`k_*_scale`, `Phi_*_correction`, `k_damage_scale`) foi **REMOVIDA** do engine. Payloads/.msd legados são traduzidos na fronteira por `calibration.tuner_shim.translate_legacy_tuners` (folda tuner→constante física, multiplica-nunca-sobrescreve, idempotente). O `StagedCalibrator` e o `handle_calibrate` do servidor foram aposentados (`NotImplementedError`); a via canônica de calibração é o `SharedCalibrator` físico. **Ressalva de procedência (§4.42c, registrada AS-IS):** o fold preserva os números per-rig mas remove a camada de ajuste **antes** de `W_conf_ref`/`k_wear_spec` terem procedência per-par completa — é uma dívida declarada, não resolvida.

### 8.3 Contagem honesta de DOF
88 campos de `JointMaterial` **≠ 88 graus de liberdade**. A decomposição honesta (`knowledge_base.dof_summary()`):
- **~44 capabilities opt-in** — inertes por default (não são DOF a menos que ligadas com procedência).
- **~9 tuners** — REMOVIDOS no Estágio B (0 DOF).
- **~17 constantes compartilhadas** — fitadas UMA vez no dataset inteiro (Estágio A), não por condição.
- **3 inputs** — `emb_depth` (VDI/data-implícito), geometria, carga (não-fittáveis, procedência).
- **2 per-rig** — `c_bend` (único knob transversal) + `F0_test` quando a procedência exige.
- **4 congeladas** (FROZEN_S_ZERO) — S≈0, não-fittáveis.

**Por rig novo:** transversal = **1** constante fitada (`c_bend`); axial = **0** (predição zero-refit, `emb_depth` lido da queda inicial). Este é o sentido de "menos graus de liberdade ⇒ mais robusto": a física é compartilhada, o que varia por rig é uma única constante com procedência declarada.

### 8.4 Estudo de sensibilidade (OAT ±20%)
Ranking `S` (deslocamento médio de F/F₀ por perturbação ±20%, `knowledge_base.sensitivity()`):

| Rank | Parâmetro | S | Natureza |
|---|---|---:|---|
| 1 | `mu_bearing`/`mu_thread` | 0.067 | **input** (Motosh) — robusto |
| 2 | `tr_loose_gain` | 0.054 | constante **sem âncora** ⇒ alvo #1 de procedência |
| 3 | `c_bend` | 0.030 | per-rig (único knob transversal) |
| … | `emb_depth`, `C_creep`, `k_wear_spec` | 0.01–0.03 | input / per-par |
| baixo | `k_j_init`, `alpha_GW`, `slip_capacity_coeff`, `partial_slip_exp` | ≈0 | **congelados** (FROZEN_S_ZERO) |

A robustez vem de: (1) os parâmetros de maior S são **inputs medidos** (µ), não knobs livres; (2) o único knob de fit alto (`tr_loose_gain`) está identificado como alvo de procedência; (3) os de S≈0 são congelados por design.

---

## 9. Validação

A confrontação com a biblioteca (Fase 1, veredicto unificado em `MODEL_LEGITIMACY.md` §8) estabeleceu: **formas/acoplamentos transferem cross-rig; constantes não** (são per-par/rig/junta). Os casos individuais — **condições de contorno + modelo MSD + constantes usadas (com procedência) + curva com erro** — estão documentados em reports ricos gerados por `New_Theory/generate_case_reports.py`:

- **Índice mestre:** `validation_html/validation_report.html` (82 casos, navegação recíproca com o hub e a galeria de afrouxamento).
- **Reports individuais:** `validation_html/reports/<csv>.html` — um por caso, com as condições de contorno estruturadas, a cadeia MSD instanciada, a tabela de constantes com procedência declarada, e a curva artigo-vs-modelo com a banda de erro.
- **Galeria de afrouxamento:** 82 curvas (artigo/modelo/erro), filtrável/ordenável, teto de erro 0.2 (interp máx 0.178, MAE 0.140, mediana 0.049).

Falsificações registradas AS-IS (não escondidas): axial `∂(fim)/∂A_F≡0` (§4.6, apontou o fretting de flanco), `k_j`-scaling (§4.10, apontou o arresto auto-travante), predictive-damage-trigger (F0-dominado), HDPE cross-material. **Piso de scatter medido = limite duro:** o modelo não é empurrado abaixo do scatter experimental do rig.

Para os veredictos de física, identifiability e parcimônia por seção, ver `MODEL_LEGITIMACY.md` (documento vivo, atualizado a cada mudança de modelo).
