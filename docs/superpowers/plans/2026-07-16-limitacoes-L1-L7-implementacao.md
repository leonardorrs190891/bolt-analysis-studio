# Limitações L1–L7 — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** fechar as limitações declaradas do modelo (L1 flanco∝A_F, L2 rigidez de membro, L3 F_amp↔δ, L5 creep, L6 k_wear por par, L7 bound de remoção, C2 residual viscoso; L4 documentado) com formas default-inertes + proveniência R5, gateadas contra a suíte de 180 casos.

**Architecture:** feature branch único (`feature/l1-l7-gaps`) com um commit por fatia; cada fatia = TDD + flag default-inerte (bit-identidade off) + gate quantitativo pré-registrado; proveniência centralizada no `knowledge_base`; adoção final = professor (nada em `adopted_configs.json`/`joint_calibrations.json`).

**Tech Stack:** Python 3.14, pytest (via `tests/conftest.py` sys.path — sem editable install), dataclasses, `numpy`; dados R5 em `BAS_V2_papers/F. Rodada 5 (limitacoes 2026-07-16)/{apparatus_notes,digitized_csv}`.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-16-limitacoes-L1-L7-implementacao-design.md` (decisões D1–D6).
- Referência técnica por limitação: `Models/CALIBRATION_AND_VALIDATION/curve_library/ANALISE_MODELOS_R5.md`.
- **Default-inerte obrigatório**: todo campo novo de `JointMaterial` default = inativo; teste de bit-identidade (flag off ⇒ história idêntica à do main).
- **Todo campo fitável novo exige `ParameterRule`** em `calibration/parameter_registry.py` ANTES do fit (`active_candidates` levanta KeyError por design — CLAUDE.md).
- Encoding `utf-8` em todo I/O; `python -c "import ast; ast.parse(open('PATH', encoding='utf-8').read()); print('OK')"` após cada edição.
- Suíte mínima por fatia: a lista de pytest do CLAUDE.md (§ "Calibration package tests") + testes novos da fatia. NUNCA `pytest | tail` antes de commit (memória).
- `git add` **por arquivo explícito** (hazard OneDrive/sessão paralela); **sem push**; não tocar `New_Theory/adopted_configs.json` nem `New_Theory/joint_calibrations.json`.
- Fits/validação longos em FOREGROUND (memória: background colide no adopted_configs).
- Nomes exatos do engine: os blocos de código abaixo seguem o idioma documentado (CLAUDE.md §V2 analyzer); o executor DEVE ler a seção correspondente de `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` antes de cada fatia de engine e ajustar nomes/assinaturas reais mantendo a semântica especificada.

---

### Task 0: Branch + baseline MEM

**Files:**
- Create: `New_Theory/l1l7_baseline.json` (snapshot de métricas)

**Interfaces:**
- Produces: baseline global (mediana MAE, count>0,10, count>0,15, tripé por caso) usado por TODOS os gates.

- [ ] **Step 1: Criar o branch a partir do main atual**

```bash
cd "C:/Users/leo_r/OneDrive/BPL/Analitical/BAS_V2"
git status -s   # conferir que só há WIP conhecido da campanha; NÃO stashear nada alheio
git checkout -b feature/l1-l7-gaps
```

- [ ] **Step 2: Rodar a suíte para confirmar verde antes de tudo**

Run: `python -m pytest tests/test_surface_damage.py tests/test_calibration_segmentation.py tests/test_calibration_decomposition.py tests/test_calibration_profiles.py tests/test_calibration_server.py tests/test_v2_solver_preload.py tests/test_slip_onset_incubation.py tests/test_case_study_models.py tests/test_calibration_trim.py tests/test_v2_calibration.py tests/test_embedding_state_based.py tests/test_shared_block_persistence.py tests/test_shared_calibrator.py tests/test_parameter_registry.py tests/test_library_common.py tests/test_anchor_creep.py tests/test_transfer_validation.py -q`
Expected: tudo PASS (contagem registrada).

- [ ] **Step 3: Gerar o baseline de validação (FOREGROUND)**

Run: `python -m bolt_analysis_studio.validation.report --all`
Depois, extrair métricas para o snapshot:

```python
# scripts/l1l7_baseline.py (criar; pode ser um one-liner de sessão se preferir)
import json, statistics
from bolt_analysis_studio.validation import store  # ajustar ao módulo real do pacote validation
data = store.load()  # ler validation_store.json conforme API existente
maes = [c["mae"] for c in data["cases"].values() if c.get("comparable", True)]
snap = {"n": len(maes), "mediana": statistics.median(maes),
        "gt_010": sum(m > 0.10 for m in maes), "gt_015": sum(m > 0.15 for m in maes)}
json.dump(snap, open("New_Theory/l1l7_baseline.json", "w", encoding="utf-8"), indent=1)
print(snap)
```

Expected: números ≈ estado da campanha (mediana ~0,05, conferir ledger vigente). Anotar no JSON.

- [ ] **Step 4: Commit**

```bash
git add New_Theory/l1l7_baseline.json scripts/l1l7_baseline.py
git commit -m "chore(l1l7): branch + baseline MEM do gate global"
```

---

### Task 1: Fatia 0 — âncoras R5 no knowledge_base

**Files:**
- Create: `New_Theory/r5_anchors.json` (dados de proveniência)
- Modify: `src/bolt_analysis_studio/calibration/knowledge_base.py` (novas queries)
- Test: `tests/test_knowledge_base_r5.py`

**Interfaces:**
- Produces: `kb.wear_spec_anchor(interface: str, pair: str) -> dict` (`{"value","band","unit","source","provenance"}`); `kb.mu_thread_anchor(coating: str) -> dict`; `kb.creep_class(pair_class: str) -> dict`; `kb.removal_energy_bound() -> dict` (`{"lo":1e3,"hi":1.05e4,"unit":"J/mm^3"...}` — 1,8–10,5 kJ/mm³ arredondado a 1–10,5).
- Consumes: nada (dados novos).

- [ ] **Step 1: Escrever `New_Theory/r5_anchors.json`** com o conteúdo (valores da ANALISE_MODELOS_R5):

```json
{
  "wear_spec": {
    "thread|35CrMo-SCM435": {"value": 8.34e-15, "band": [4e-15, 2e-14], "unit": "1/Pa",
      "source": "Zhang 2019 EFA 10.1016/j.engfailanal.2019.05.001", "provenance": "derived-validated"},
    "faying|Q355B-Q235B": {"value": 6.7e-12, "band": [6.49e-12, 7.00e-12], "unit": "1/Pa",
      "source": "Li 2025 EngStruct 10.1016/j.engstruct.2025.121158", "provenance": "composite-validated"},
    "fretting|52100-52100": {"value": 1e-4, "band": [3.2e-5, 2.4e-4], "unit": "norm-own",
      "source": "Warmuth 2015 10.1098/rspa.2014.0291", "provenance": "measured"}
  },
  "mu_thread": {
    "zinc": {"value": 0.150, "source": "Liu 2020 Wear Table 2", "provenance": "measured"},
    "DLC": {"value": 0.126, "source": "Liu 2020 Wear Table 2", "provenance": "measured"}
  },
  "creep_class": {
    "faying-coating-inorganic-zinc": {"model": "alpha+beta*log10(t_h)",
      "rows": {"96um": [1.0e-4, 3.0e-5], "128um": [-1.0e-6, 2.0e-4], "168um": [2.0e-4, 4.0e-5], "226um": [3.0e-4, 4.5e-5]},
      "source": "Nah 2014 10.12989/scs.2014.16.6.703", "provenance": "measured"}
  },
  "removal_energy_bound": {"lo": 1.8e3, "hi": 1.05e4, "unit": "J/mm^3",
    "source": "Shipway 2021 10.1016/j.wear.2021.203826 (derivado; taxa-dependente)", "provenance": "derived"},
  "kj_laws": {
    "pedersen2008": {"eq": "k_m = E*d*(0.59*(beta^2-alpha^2)*d/L + 0.20*(beta+alpha))",
      "source": "10.1007/s00419-007-0142-0", "rank": "closest-to-truth (+24%, Rousseau 2024)"},
    "wileman1991": {"eq": "k_m/(E*d) = A*exp(B*d/L)",
      "AB": {"steel": [0.78715, 0.62873], "aluminum": [0.79670, 0.63816], "copper": [0.79568, 0.63553], "gray_cast_iron": [0.77871, 0.61616], "general": [0.78952, 0.62914]},
      "source": "10.1115/1.2912799", "rank": "+45-59% (superestima)"}
  }
}
```

- [ ] **Step 2: Teste que falha**

```python
# tests/test_knowledge_base_r5.py
from bolt_analysis_studio.calibration import knowledge_base as kb

def test_wear_spec_anchor_thread_pair():
    a = kb.wear_spec_anchor("thread", "35CrMo-SCM435")
    assert abs(a["value"] - 8.34e-15) / 8.34e-15 < 1e-6
    assert a["unit"] == "1/Pa" and "Zhang" in a["source"]

def test_mu_thread_anchor_and_bound():
    assert kb.mu_thread_anchor("DLC")["value"] == 0.126
    b = kb.removal_energy_bound()
    assert b["lo"] < 5e3 < b["hi"]

def test_unknown_pair_raises_loud():
    import pytest
    with pytest.raises(KeyError):
        kb.wear_spec_anchor("thread", "inexistente")
```

- [ ] **Step 3: Rodar e ver falhar** — `python -m pytest tests/test_knowledge_base_r5.py -q` → FAIL (funções não existem).

- [ ] **Step 4: Implementação mínima em `knowledge_base.py`** (seguir o padrão dos leitores existentes — JSONs são a fonte, código só LÊ):

```python
_R5_PATH = _REPO_ROOT / "New_Theory" / "r5_anchors.json"   # usar o mesmo helper de raiz já existente no módulo

def _r5():
    with open(_R5_PATH, encoding="utf-8") as f:
        return json.load(f)

def wear_spec_anchor(interface: str, pair: str) -> dict:
    return dict(_r5()["wear_spec"][f"{interface}|{pair}"])   # KeyError alto por design

def mu_thread_anchor(coating: str) -> dict:
    return dict(_r5()["mu_thread"][coating])

def creep_class(pair_class: str) -> dict:
    return dict(_r5()["creep_class"][pair_class])

def removal_energy_bound() -> dict:
    return dict(_r5()["removal_energy_bound"])
```

- [ ] **Step 5: Rodar até PASS**; rodar também `tests/test_library_common.py tests/test_parameter_registry.py -q` (não podem quebrar).

- [ ] **Step 6: Commit**

```bash
git add New_Theory/r5_anchors.json src/bolt_analysis_studio/calibration/knowledge_base.py tests/test_knowledge_base_r5.py
git commit -m "feat(l1l7): fatia 0 - ancoras R5 no knowledge_base (k_wear por interface, mu por coating, classes de creep, bound L7, leis k_j)"
```

---

### Task 2: Fatia 1 — L3: F_amp ≤ µ_eff(F0)·F0 em disp-mode

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (novos campos `JointMaterial` + clamp no ramo disp-mode de `step_cycle`)
- Modify: `src/bolt_analysis_studio/calibration/parameter_registry.py` (ParameterRules)
- Test: `tests/test_l3_famp_coupling.py`

**Interfaces:**
- Consumes: campos/idioma existentes (`couple_famp_slip` modo já existente; `mu_bearing_eff`; `state.F_0`).
- Produces: campos `JointMaterial`: `famp_couple_on: float = 0.0` (0=off), `mu_eff_lo: float = 0.0` (knockdown desligado se 0), `mu_eff_F0_ref: float = 0.0`, `gross_ceiling_decay: float = 0.0` (opt-in JMP, acopla em `state.D`). Semântica: com `famp_couple_on=1`, no disp-mode `F_amp_eff = min(F_amp, mu_eff*F_0)` onde `mu_eff = mu_bearing_eff * knockdown(F_0)`; `knockdown = 1.0` se `mu_eff_lo==0`, senão interpola de `mu_eff_lo` (F0→0) a 1.0 (F0≥mu_eff_F0_ref) — proveniência Murai 0,46→0,24 e Measurement2021 (2 limiares ∝ F0).

- [ ] **Step 1: Ler o ramo disp-mode de `step_cycle` no analyzer** (localizar onde `delta_amp` é consumido e onde `F_amp` entra na elasticidade local). Anotar nomes reais.

- [ ] **Step 2: Teste que falha (bit-identidade + clamp ativo)**

```python
# tests/test_l3_famp_coupling.py
import copy
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointMaterial)

def _run(mat, n=200, famp=8000.0, delta=0.5e-3):
    an = DynamicStiffnessAnalyzer(material=mat)   # ajustar ao construtor real
    for _ in range(n):
        an.step_cycle(F_amp=famp, theta_load=0.0, freq=5.0, delta_amp=delta)
    return an.state.F_0

def test_bit_identity_flag_off():
    m0, m1 = JointMaterial(), JointMaterial()
    assert _run(m0) == _run(m1)  # campos novos default-inertes não mudam nada

def test_clamp_caps_famp_effect():
    hi = JointMaterial(famp_couple_on=1.0)
    lo = JointMaterial()
    # com clamp ligado e F_amp absurdo, a história NÃO pode piorar além do teto µ·F0
    f_clamped = _run(hi, famp=1e9)
    f_unclamped = _run(lo, famp=1e9)
    assert f_clamped >= f_unclamped  # clamp limita a perda dirigida por F_amp

def test_knockdown_reduces_ceiling_at_low_F0():
    a = JointMaterial(famp_couple_on=1.0, mu_eff_lo=0.5, mu_eff_F0_ref=50e3)
    b = JointMaterial(famp_couple_on=1.0)
    assert _run(a, famp=1e9) != _run(b, famp=1e9)
```

- [ ] **Step 3: Rodar → FAIL** (`TypeError: unexpected keyword famp_couple_on`).

- [ ] **Step 4: Implementar**: campos no dataclass (defaults 0.0) + no ramo disp-mode, antes do uso de `F_amp`:

```python
if mat.famp_couple_on:
    mu_eff = self._mu_bearing_eff()          # helper existente do damage
    if mat.mu_eff_lo > 0.0 and mat.mu_eff_F0_ref > 0.0:
        k = min(1.0, self.state.F_0 / mat.mu_eff_F0_ref)
        mu_eff *= mat.mu_eff_lo + (1.0 - mat.mu_eff_lo) * k
    ceiling = mu_eff * self.state.F_0
    if mat.gross_ceiling_decay > 0.0:
        ceiling *= max(0.0, 1.0 - mat.gross_ceiling_decay * self.state.D)  # JMP: FS->FR com desgaste
    F_amp = min(F_amp, ceiling)
```

- [ ] **Step 5: ParameterRules** para `famp_couple_on/mu_eff_lo/mu_eff_F0_ref/gross_ceiling_decay` (predicado: transverse disp-mode; nunca oferecidos no axial). Rodar `tests/test_parameter_registry.py -q`.

- [ ] **Step 6: Rodar teste novo até PASS + suíte mínima completa.**

- [ ] **Step 7: Commit**

```bash
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py src/bolt_analysis_studio/calibration/parameter_registry.py tests/test_l3_famp_coupling.py
git commit -m "feat(l1l7): fatia 1 - L3 acoplamento F_amp<=mu_eff(F0)*F0 em disp-mode (default-inerte; proveniencia Murai/Measurement2021/JMP2021)"
```

---

### Task 3: Fatia 2a — L1: canal de desgaste de flanco ∝ A_F (engine)

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (`ThreadFrettingLoss` — estender com slip axial de flanco)
- Modify: `src/bolt_analysis_studio/calibration/parameter_registry.py`
- Test: `tests/test_l1_flank_wear_axial.py`

**Interfaces:**
- Consumes: `ThreadFrettingLoss` existente (`k_thread_fret`, `fret_freq_exp` — arco mid-curve, default-inertes); `LossMechanism.rate()` idiom; KB `wear_spec_anchor("thread", ...)`.
- Produces: campos `JointMaterial`: `flank_wear_on: float = 0.0`, `k_wear_flank: float = 0.0` (1/Pa; semear com 8,34e-15 do KB), `flank_amp_exp: float = 1.0` (expoente de amplitude; Liu 2020 sugere 1,5–1,6 como candidato). Semântica: no modo FORÇA axial, slip de flanco por ciclo `s_th = c_geo * A_F / k_thread_axial` (elasticidade de rosca da geometria já disponível no modelo; `c_geo` derivado, não fitável), perda `dF_0 = flank gate * k_wear_flank * p_flank * (s_th)^flank_amp_exp * A_flank * k_b_partition` na forma do canal de wear existente (dF_0 sim, dE = trabalho friccional real — padrão "dF_0 yes, dE no" NÃO se aplica aqui: seguir o padrão do WearLoss existente para conservação).

- [ ] **Step 1: Ler `ThreadFrettingLoss` e o `WearLoss`** no analyzer; anotar como o slip e a partição k_b entram; confirmar onde A_F (F_amp em modo força) está acessível no `rate()`.

- [ ] **Step 2: Teste que falha — a assinatura do gap: ∂(perda final)/∂A_F ≠ 0 no axial**

```python
# tests/test_l1_flank_wear_axial.py
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointMaterial)

def _final_ratio(mat, A_F, n=2000, F0=30e3):
    an = DynamicStiffnessAnalyzer(material=mat)   # configurar F0 pelo caminho real do construtor/preload
    for _ in range(n):
        an.step_cycle(F_amp=A_F, theta_load=0.0, freq=30.0)  # modo força (sem delta_amp)
    return an.state.F_0

def test_bit_identity_off():
    assert _final_ratio(JointMaterial(), 7.5e3) == _final_ratio(JointMaterial(), 12.5e3) or True
    # off: mecanismo não existe; comparar história completa off vs off (igual) — e off deve ser
    # EXATAMENTE o main: sem sensibilidade nova a A_F
    a = _final_ratio(JointMaterial(), 7.5e3)
    b = _final_ratio(JointMaterial(), 12.5e3)
    base_delta = abs(a - b)
    assert base_delta == 0.0 or base_delta < 1e-9  # o gap atual: amplitude-cego

def test_dloss_dAF_nonzero_when_on():
    m = JointMaterial(flank_wear_on=1.0, k_wear_flank=8.34e-15, flank_amp_exp=1.0)
    lo = _final_ratio(m, 7.5e3)
    hi = _final_ratio(m, 12.5e3)
    assert hi < lo  # maior amplitude axial => maior perda (sinal do Liu2017: -2.2e-5/N)

def test_transverse_untouched():
    m = JointMaterial(flank_wear_on=1.0, k_wear_flank=8.34e-15)
    m0 = JointMaterial()
    # em disp-mode transversal puro (A_F=0) o canal precisa ser inerte
    # (usar o harness transversal padrão dos testes existentes de slip_onset como referência)
    ...  # copiar o harness de tests/test_slip_onset_incubation.py e comparar históricos
```

(Completar o 3º teste copiando o harness transversal do teste de slip-onset existente — o
executor tem o arquivo `tests/test_slip_onset_incubation.py` como modelo direto.)

- [ ] **Step 3: FAIL** (campos inexistentes).

- [ ] **Step 4: Implementar** no `ThreadFrettingLoss.rate()` (ou canal irmão), idioma do WearLoss:

```python
if mat.flank_wear_on and F_amp > 0.0 and delta_amp is None:   # só modo força/axial
    k_th = self._thread_axial_stiffness()      # da geometria (helix/thread já no modelo)
    s_th = F_amp / max(k_th, 1e-30)            # slip elastico de flanco por meia-onda
    p_fl = self._flank_pressure()              # F_0 / area de flanco engajada (geometria)
    d_w = mat.k_wear_flank * p_fl * (2.0 * s_th) ** mat.flank_amp_exp * self._n_cycles_factor
    dF_0 = -d_w * self._flank_to_preload()     # particao rigidez (mesmo caminho do wear existente)
    dE = mu_th * p_fl * A_fl * 2.0 * s_th      # trabalho friccional real p/ conservacao
```

Reusar helpers reais equivalentes; NADA de constante mágica fora de `JointMaterial`/geometria.

- [ ] **Step 5: ParameterRules** (`flank_wear_on/k_wear_flank/flank_amp_exp`; predicado: axial força com F_amp>0 — espelho invertido do predicado transversal). PASS em `test_parameter_registry.py`.

- [ ] **Step 6: PASS no teste novo + suíte mínima + teste de conservação existente** (`analyzer.energy.conservation_residual ≈ 0` num run axial com flag on — adicionar assert no teste novo).

- [ ] **Step 7: Commit**

```bash
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py src/bolt_analysis_studio/calibration/parameter_registry.py tests/test_l1_flank_wear_axial.py
git commit -m "feat(l1l7): fatia 2a - L1 canal de desgaste de flanco prop. a A_F (forma Zhang, nivel KB Zhang2019; default-inerte)"
```

---

### Task 4: Fatia 2b — L1: calibração axial per-rig + Gate B1 (prereg)

**Files:**
- Create: `New_Theory/l1_axial_gate.py` (script de fit + gate)
- Create: `New_Theory/l1_axial_gate_result.json`

**Interfaces:**
- Consumes: Task 3 (campos `flank_*`); casos axiais in-library (`Liu2017 axial *`, `Liu2016` da R4 ingestão, `H.Li2022`); `ParameterIdentifier`/`SharedCalibrator` existentes.
- Produces: resultado de gate consumido pela Task 10 (relatório final).

- [ ] **Step 1: PREREG no topo do script (antes de rodar qualquer fit):**

```python
PREREG = {
  "gate": "B1-rerun",
  "H0": "com flank_wear_on, d(fim)/dA_F no rig Liu2017 tem sinal negativo e ordem 1e-5/N",
  "PASS": "slope in [-4.4e-5, -1.1e-5] por curva-completa fit (alvo -2.2e-5/N, tol 2x)",
  "FAIL2": "2 preregs consecutivos falhando => falsificacao documentada, sem forcar adocao",
  "no_regression": "casos transversais: mediana e count>0.10 identicos ao baseline (flag off la)"
}
```

- [ ] **Step 2: Fit per-rig em CURVAS COMPLETAS** (lição 2026-07-08): liberar só `{k_wear_flank, flank_amp_exp}` (registry), demais congelados; rigs Liu2016+Liu2017 juntos (mesmo aparato) e H.Li2022 separado. FOREGROUND.

- [ ] **Step 3: Computar o slope ∂(fim)/∂A_F** na varredura de amplitude do Liu2017 (5 níveis) e do Liu2016 (7,5–12,5 kN) com os parâmetros fitados; gravar `l1_axial_gate_result.json` com slope, MAEs por curva, tripé.

- [ ] **Step 4: Avaliar PASS/FAIL contra o PREREG.** Se FAIL: registrar, ajustar UMA hipótese (ex.: `flank_amp_exp` 1,5 fixo do Liu2020 em vez de livre) e rodar o 2º e último prereg.

- [ ] **Step 5: Commit (resultado, PASS ou FAIL — ambos são conhecimento)**

```bash
git add New_Theory/l1_axial_gate.py New_Theory/l1_axial_gate_result.json
git commit -m "feat(l1l7): fatia 2b - gate B1 re-executado com canal de flanco (resultado: <PASS|FAIL> slope=<valor>)"
```

---

### Task 5: Fatia 3 — L2: lei k_j(geometria, material)

**Files:**
- Modify: `src/bolt_analysis_studio/calibration/library_common.py` (nova função)
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (opt-in `kj_mode` + forma elíptica de Grosse opcional em Φ)
- Test: `tests/test_l2_kj_law.py`

**Interfaces:**
- Consumes: `geometry_for` existente em `library_common` (A_contact real por rig, 2026-07-05); KB `kj_laws`.
- Produces: `kj_from_geometry(d_mm, L_mm, E_Pa, d_hole_mm, d_washer_mm, mode="pedersen") -> float [N/m]`; campos `JointMaterial`: `kj_mode: str = ""` (""=atual), `phi_load_dep: float = 0.0` (0=off; >0 = deformação crítica de separação relativa da forma elíptica de Grosse).

- [ ] **Step 1: Teste que falha (valores analíticos das duas leis)**

```python
# tests/test_l2_kj_law.py
from bolt_analysis_studio.calibration.library_common import kj_from_geometry
import math

def test_wileman_steel_matches_closed_form():
    E, d, L = 206.8e9, 0.012, 0.024   # d/L = 0.5
    k = kj_from_geometry(12, 24, E, 13.0, 24.0, mode="wileman")
    assert abs(k - E * d * 0.78715 * math.exp(0.62873 * 0.5)) / k < 1e-6

def test_pedersen_asymptote():
    E, d, L = 206.8e9, 0.012, 0.024
    alpha, beta = 13.0 / 12.0, 24.0 / 12.0
    exp_k = E * d * (0.59 * (beta**2 - alpha**2) * d / L + 0.20 * (beta + alpha))
    k = kj_from_geometry(12, 24, E, 13.0, 24.0, mode="pedersen")
    assert abs(k - exp_k) / exp_k < 1e-6

def test_pedersen_below_wileman_at_high_dL():
    kw = kj_from_geometry(24, 12, 206.8e9, 26.0, 36.0, mode="wileman")   # d/L=2
    kp = kj_from_geometry(24, 12, 206.8e9, 26.0, 36.0, mode="pedersen")
    assert kp < kw   # Pedersen le ~30% abaixo em d/L=2 (nota pedersen2008)
```

- [ ] **Step 2: FAIL → implementar em `library_common.py`:**

```python
def kj_from_geometry(d_mm, L_mm, E_Pa, d_hole_mm, d_washer_mm, mode="pedersen"):
    d, L = d_mm * 1e-3, L_mm * 1e-3
    if mode == "wileman":
        A, B = 0.78952, 0.62914   # geral; por material via kb.kj_laws quando E casar com tabela
        return E_Pa * d * A * math.exp(B * d / L)
    if mode == "pedersen":
        alpha, beta = d_hole_mm / d_mm, d_washer_mm / d_mm
        return E_Pa * d * (0.59 * (beta**2 - alpha**2) * d / L + 0.20 * (beta + alpha))
    raise ValueError(mode)
```

(Material-específico do Wileman: buscar A,B em `kb._r5()["kj_laws"]["wileman1991"]["AB"]` pelo
material quando fornecido — parâmetro opcional `material: str = "general"`.)

- [ ] **Step 3: Opt-in no engine**: `kj_mode` em `JointMaterial`; na montagem do k_j do analyzer,
se `kj_mode` não-vazio e a geometria do run fornecer furo/arruela, usar `kj_from_geometry`.
`phi_load_dep>0`: modular Φ com `F_m/F_i = 1 − sqrt(max(0, 2λ−λ²))`, `λ = ΔF/(phi_load_dep·F_i)`
(forma elíptica Grosse — documentar que os coeficientes são por-junta). Campo str passa pelo
filtro type-aware de overrides (já existente para `conform_driver`).

- [ ] **Step 4: PASS + bit-identidade (kj_mode="" idem main) + suíte mínima.**

- [ ] **Step 5: Commit**

```bash
git add src/bolt_analysis_studio/calibration/library_common.py src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_l2_kj_law.py
git commit -m "feat(l1l7): fatia 3 - lei k_j(geometria,material) Pedersen-primaria + Wileman + phi elipt. Grosse (opt-in)"
```

---

### Task 6: Fatia 3b — L2: gate Rousseau/Zhang (prereg D5)

**Files:**
- Create: `New_Theory/l2_kj_gate.py`, `New_Theory/l2_kj_gate_result.json`

**Interfaces:**
- Consumes: Task 5; casos `Rousseau2025 steel t10/12/14` + `Zhang2006 clamped-length` da suíte.

- [ ] **Step 1: PREREG:** "com `kj_mode='pedersen'` (sem re-fit de mais nada), erro nos 6 casos
Rousseau steel/HDPE e nos Zhang ≤ estado atual (com capacidades adotadas ligadas); se pior,
a lei fica como proveniência documentada (D5), PASS-doc".

- [ ] **Step 2: Rodar os casos com/sem `kj_mode` via runner canônico** (paridade de config do
report; nunca editar adopted_configs). Gravar comparação por caso (MAE/maxerr/σ_res).

- [ ] **Step 3: Avaliar + commit** (`feat(l1l7): fatia 3b - gate L2 (resultado ...)`).

---

### Task 7: Fatia 4 — L5: docstring + forma saturante opt-in

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (`CreepLoss`)
- Test: `tests/test_l5_creep_saturating.py`

**Interfaces:**
- Produces: docstring corrigido ("log-t, coincide com regressão Nah 2014; NÃO é Norton-Bailey");
campos: `creep_mode: str = ""` (""=log-t atual), `creep_t_c: float = 0.0`, `creep_alpha_sat: float = 1.0`.
Semântica saturante: `δ_creep(t) = δ_max · (1 − exp(−(t/creep_t_c)**creep_alpha_sat))` com
`δ_max` derivado do mesmo `C_creep` (continuidade dimensional) — forma Alamos.

- [ ] **Step 1: Teste que falha**

```python
# tests/test_l5_creep_saturating.py
def test_saturating_bounded_log_unbounded():
    m_sat = JointMaterial(creep_mode="saturating", creep_t_c=1e4)
    m_log = JointMaterial()
    f_sat_10k = _run_hold(m_sat, t=1e4);  f_sat_1M = _run_hold(m_sat, t=1e6)
    f_log_10k = _run_hold(m_log, t=1e4);  f_log_1M = _run_hold(m_log, t=1e6)
    assert (f_sat_10k - f_sat_1M) < (f_log_10k - f_log_1M)   # saturante perde menos na cauda
    assert f_sat_1M > 0
```

(`_run_hold` = harness de creep estático usado em `tests/test_anchor_creep.py` — copiar o padrão.)

- [ ] **Step 2: FAIL → implementar** (ramo em `CreepLoss.rate()`; docstring; ParameterRules p/
`creep_t_c/creep_alpha_sat` com predicado de creep estático). Bit-identidade `creep_mode=""`.

- [ ] **Step 3: PASS + `tests/test_anchor_creep.py` sem regressão. Commit** (`feat(l1l7): fatia 4 - L5 docstring log-t + creep saturante opt-in (forma Alamos; classes no KB)`).

---

### Task 8: Fatia 5 — L7 bound + C2 residual viscoso axial

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (EnergyLedger)
- Test: `tests/test_l7_removal_bound_and_viscous.py`

**Interfaces:**
- Produces: (a) `analyzer.energy.removal_energy_check() -> dict` (`{"implied_J_per_mm3", "in_bound", "bound"}` — usa volume removido acumulado do wear e energia de wear; bound do KB); (b) modo força: `W_damp_visc` passa a ser SOURCED em `W_ext` (obra no ledger, não na física) OU excluído do residual axial — escolher a menor mudança que zere o residual; documentar a escolha no docstring do ledger.

- [ ] **Step 1: Teste que falha**

```python
def test_axial_force_mode_residual_near_zero():
    m = JointMaterial()
    an = _run_axial_force(m, n=5000)   # harness axial força
    assert abs(an.energy.conservation_residual) < 1.0   # era -242..-12 J

def test_removal_energy_check_reports_bound():
    m = JointMaterial(k_wear_spec=8.34e-15)
    an = _run_transverse(m, n=5000)
    chk = an.energy.removal_energy_check()
    assert "implied_J_per_mm3" in chk and chk["bound"]["lo"] < chk["bound"]["hi"]
```

- [ ] **Step 2: FAIL → implementar; conservação transversal INALTERADA (assert extra: residual transversal idem baseline).**

- [ ] **Step 3: PASS + suíte. Commit** (`fix(l1l7): fatia 5 - C2 residual viscoso axial zerado + check L7 de energia de remocao (bound 1.8-10.5 kJ/mm3)`).

---

### Task 9: Fatia 6 — L4: documentação MODEL_LEGITIMACY

**Files:**
- Modify: `New_Theory/MODEL_LEGITIMACY.md` (§4.9 append)

- [ ] **Step 1:** Append: null 3× (R4 Fouvry sub-GPa; R5 busca dirigida; R5 digitalização);
precedentes de forma (n_p≈0,5–0,6; teto de aspereza 1,5·H → sanity de `p_ref`; Etsion satura ~5
ciclos em DESLOCAMENTO vs Frérot energia NÃO satura); valor de `W_conf_ref`/n segue dependente
do experimento âncora âncora interna (~1,2 GPa, medir n). Referenciar `ANALISE_MODELOS_R5.md`.

- [ ] **Step 2: Commit** (`docs(l1l7): fatia 6 - L4 null 3x + precedentes de forma no MODEL_LEGITIMACY §4.9`).

---

### Task 10: Fatia 7 — wiring dos casos Zhang/Liu2020 (+Nah opcional)

**Files:**
- Modify: `src/bolt_analysis_studio/core/validation_cases.py` (fontes `ZHANG_2018`, `ZHANG_2019`, `LIU_2020_WEAR`; loader dos CSVs da pasta F)
- Test: `tests/test_r5_cases_wiring.py`

**Interfaces:**
- Consumes: CSVs `digitized_csv/zhang_*.csv` (F/F0, x=cycles), `liu2020_fig5b/9/15_*.csv`
(y=R_F % → dividir por 100), loader com `x|cycle` + `x_scale` + clamp x≥0 (padrão PR-26).
- Produces: ~16 `ValidationCase`s novos (PACK), aparecem no report mestre.

- [ ] **Step 1: Teste que falha** (contagem + spot-check de um caso: F0, n_cycles, ratio final
dentro do CSV; padrão dos testes de `test_case_study_models.py`).

- [ ] **Step 2: Implementar** seguindo exatamente o padrão da ingestão R4 (import-time, degrade
sem raise se CSV faltar; % → ratio para Liu2020; caveats nas notes dos casos).

- [ ] **Step 3: PASS + `test_case_study_models.py` + report `--case` de 2 casos novos. Commit**
(`feat(l1l7): fatia 7 - casos Zhang2018/2019 + Liu2020 wired (F/F0 da pasta F; PACK)`).

---

### Task 11: Fatia 8 — relatório final, painel e handoff de adoção

**Files:**
- Create: `New_Theory/l1l7_final_report.md`
- Modify: `New_Theory/variable_explorer/concept_coverage.html` (seção de limitações — SÓ no branch)

- [ ] **Step 1:** `python -m bolt_analysis_studio.validation.report --all` (FOREGROUND) no branch
com flags off (paridade) e depois com cada capacidade ligada nos casos-alvo; montar painel
antes/depois por fatia (mediana, >0,10, tripé) + tabela "capacidade → gate → resultado →
recomendação de adoção por classe de procedência (MEM)".

- [ ] **Step 2:** Atualizar `concept_coverage.html`: cada limitação vira "capacidade validada
(flag X)", "bound documentado", ou "dependente do experimento âncora" — com link para o gate.

- [ ] **Step 3: Commit final + resumo para o professor** (sem merge; decisão de integração é dele):

```bash
git add New_Theory/l1l7_final_report.md New_Theory/variable_explorer/concept_coverage.html
git commit -m "docs(l1l7): fatia 8 - relatorio final, painel de gates e handoff de adocao"
git log --oneline main..feature/l1-l7-gaps   # anexar ao resumo
```

---

## Self-review (do plano)

- Cobertura do spec: D1–D6 refletidas (D1 Task 0; D2 ordem Tasks 1–11; D3 Tasks 4/6/11 nunca tocam adopted/joint_calibrations; D4 Task 10; D5 Task 6; D6 todos os commits). L1→T3+T4; L2→T5+T6; L3→T2; L5→T7; L6→T1 (KB); L7+C2→T8; L4→T9; casos→T10; relatório→T11. Sem lacunas.
- Placeholders: os dois "..."/"copiar harness" apontam para arquivos-modelo EXISTENTES e nomeados (`tests/test_slip_onset_incubation.py`, `tests/test_anchor_creep.py`) com instrução concreta — aceitável porque o padrão está no repo, não inventado.
- Consistência de tipos: campos novos todos `float` default 0.0 (exceto `kj_mode`/`creep_mode` str "" — passam pelo filtro type-aware existente de overrides, verificado no CLAUDE.md).
- Aviso global: código de engine segue o idioma DOCUMENTADO; o executor lê a seção real antes (Global Constraints, último item).
