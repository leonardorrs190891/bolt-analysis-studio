# Modelo analítico — constantes físicas compartilhadas + remoção da camada de tuners — design

**Data:** 2026-07-02
**Autor:** Prof. Leonardo Rosa Ribeiro da Silva (PhD) + Claude Code (brainstorming)
**Status:** Design aprovado ("Approve as designed"). Antecede o plano de implementação.
**Relacionado:**
- `New_Theory/MODEL_LEGITIMACY.md` (identificabilidade, parcimônia, protocolo — este spec implementa o §6)
- `New_Theory/MODEL_MATH_REFERENCE.md` (matemática do engine atual)
- `docs/superpowers/specs/2026-06-20-staged-calibration-leverage-design.md` (calibração por estágio + surface_damage)
- `docs/superpowers/specs/2026-05-17-calibration-experiments.md` (Exp 1–5: procedência ideal das constantes)
- `docs/superpowers/specs/2026-06-20-generalization-validation-campaign.md` (varredura paramétrica futura)
- `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (engine V2)
- `src/bolt_analysis_studio/calibration/` (StagedCalibrator, server)

---

## 0. Problema e objetivo

Pedido do usuário: **"reduzir o número de variáveis para que não seja um curve fit,
e sim um modelo analítico de verdade."**

Estado atual (censo, rev. 2026-07-02):

1. O `fit_parsimonious` (2026-06-20) já reduziu os tuners fitados a **≤2 por
   condição** ({k_emb_scale, k_wear_scale_tr}; reaperto = 0). Mas ainda são
   **6 números adimensionais fitados por curva** no dataset M16 shear — cada
   condição tem seu próprio par.
2. A API do engine carrega **~9 tuners multiplicadores** sobre ~14 constantes
   físicas, e vários pares são **perfeitamente degenerados** (nenhum experimento
   consegue separá-los — só o produto entra na física):
   - `k_emb_scale × emb_depth`
   - `k_creep_scale × C_creep`
   - `k_wear_scale_{ax,tr} × K_archard / (hardness · A_contact)`
   - `Phi_tr_correction × tr_loose_gain` (multiplicados diretamente no código)
   - `k_damage_scale` × constantes de dano
3. Os valores dos tuners por condição estão **substituindo inputs físicos que
   faltam**: reusada `k_emb=0.18` = "embedding já consumido por uso prévio"
   (deveria ser estado nomeado, como `D_init`); sobretorque `k_wear=0.045`
   (10× abaixo da nova) — mas a simulação roda o sobretorque com o **mesmo
   F0=50 kN** das outras condições, então o tuner absorve o erro do input.
4. `MODEL_LEGITIMACY.md` §5.1 admite: `emb_depth` e `C_creep` foram
   historicamente ajustados **contra as mesmas curvas** — a separação
   física/tunável existe no design mas não nos dados.

**Objetivo:** reparametrizar para **"uma física, N estados"** — um único conjunto
de constantes físicas do par tribológico, estimado UMA vez sobre TODAS as
condições em conjunto; condições diferem apenas por **estados nomeados e
mensuráveis** (D_init, embedding consumido, F0 real do ensaio). Cada curva vira
**predição do mesmo modelo**, que é a definição operacional de modelo analítico
com parâmetros estimados.

### 0.1 Decisões do brainstorming

| Decisão | Escolha do usuário |
|---|---|
| Escopo | **Física compartilhada + limpeza do engine** (programa completo) |
| Ordem | **Estágio A** (prova científica, sem quebrar API) → **Estágio B** (limpeza breaking, gated pelo resultado do A) |
| Critério de aceitação | **Legitimidade em 1º, MAE honesto** — sem teto rígido; deliverable = modelo compartilhado + tabela de MAE por condição + predição leave-one-condition-out. *(Assumido — pergunta ficou sem resposta; consistente com MODEL_LEGITIMACY §8. Usuário pode impor teto depois.)* |
| Aprovação do design | "Approve as designed" (2026-07-02) |

---

## 1. Evidência que motiva (já produzida no repo)

- **Identificabilidade** (`identifiability_analysis.py`): em uma curva de
  decaimento, só 3/5 direções de tuner são stiff; `JᵀJ` singular; ablação mostra
  que só `k_wear_scale_tr` é necessário. 5 tuners/curva = sobre-parametrização.
- **Parcimônia** (`fit_parsimonious`, tol=0.005): nova/reusada/sobretorque fecham
  com {k_emb, k_wear}; reaperto com **zero** tuners (só D_init + dano).
- **Cross-condição** (`cross_validation.py`): um único set de tuners SEM estados
  nomeados não prediz as outras condições (MAE_pred até 0.287). A hipótese deste
  spec: com **estados nomeados por condição**, um único set de **constantes
  físicas** fecha as 4.
- **Sloppy models** (§4.3): predição pode ser excelente mesmo com parâmetros
  individuais não-identificáveis — reforça fitar POUCAS constantes compartilhadas.

---

## 2. Estágio A — física compartilhada (sem quebrar a API)

### 2.1 Conceito

Fit conjunto: resíduos concatenados sobre **todas as curvas das 4 condições**
(TP3/8/11 + MEAN nova; TP4/5/9/10 + MEAN reusada; TP6; TP7). Parâmetros livres =
**constantes físicas** (não multiplicadores), com bounds e priors de literatura.
Todos os `k_*_scale`/`Phi_*_correction` **congelados ≡ 1.0** (não entram no fit).

### 2.2 Constantes físicas candidatas (fit compartilhado)

| Constante | Default | Bounds | Prior | Nota |
|---|---:|---|---|---|
| `emb_depth` | 30 µm | [5, 80] µm | log, centro no default | Exp 3 futura |
| `N_emb` | 50 | [10, 200] | log | constante de tempo do embedding |
| `K_archard` | 1e-4 | [1e-5, 1e-3] | log | literatura boundary-lub |
| `C_creep` | 5e-11 | [1e-12, 1e-9] | log | esperado ≈ irrelevante em disp-mode |
| `tr_loose_gain` | 2.0 | [0.5, 10] | log | absorve o antigo `Phi_tr_correction` |
| `c_D` ou `k_dmg_wear` | 2.0 / 4.0 | [0.5, 8] | log | no máx. 1–2 do bloco de dano, compartilhadas entre reusada+reaperto |

Forward selection mantida (filosofia do `fit_parsimonious`): parte de TODOS os
defaults de catálogo e só libera uma constante se ela cortar o MAE global > tol.
**Meta: ≤5 números fitados no dataset inteiro** (hoje: 6 por-condição + estrutura).
A regularização pull-to-1 vira **prior de literatura**: resíduo += `√λ·log(p/p_default)`
(log porque as constantes são multiplicativas e variam ordens de magnitude).

### 2.3 Estados nomeados por condição (inputs, não tuners)

| Condição | Estados | Origem |
|---|---|---|
| nova | — | — |
| reusada | `emb_consumed_frac = 1.0`, `D_init = 0.3` | uso prévio consumiu o assentamento; dano inicial |
| sobretorque | `F0_test` = pré-carga real do ensaio TP6 | **input do usuário** (relatório do ensaio) |
| reaperto | `D_init = 0.3` | ciclo prévio + reaperto |

Regras:
- Estados são **inputs fixos** por default (não fitados). `D_init=0.3` mantém o
  valor assumido hoje.
- **Fallback do `F0_test`**: se o valor real do TP6 não estiver disponível,
  `F0_test` é estimado UMA vez no fit — mas reportado como grandeza física em kN,
  com sanity-check `F0_test ≤ 0.9·F_y` (M16 10.9: F_y ≈ 133 kN) e marcado
  `estimated` no JSON. Continua sendo um número mensurável, nunca um botão
  adimensional.
- Se uma condição só fechar com um knob adimensional por-condição → **achado de
  falsificação** (MODEL_LEGITIMACY §7): documenta qual forma de mecanismo está
  errada. Não adicionar tuner.

### 2.4 Embedding vira state-based (mudança aditiva no engine, já no Estágio A)

Necessário para `emb_consumed_frac`. Substituir o incremento cycle-clock

```
dδ = (emb_depth/N_emb)·e^(−N/N_emb)          # atual: função do relógio de ciclos
```

pela forma exata em estado (decaimento geométrico):

```
dδ = (emb_depth − δ_emb)·(1 − e^(−1/N_emb))  # novo: função do estado
```

Propriedades:
- Para junta virgem (δ_emb(0)=0), reproduz **exatamente** a forma fechada de
  Norton `δ(N) = emb_depth·(1−e^(−N/N_emb))` em ciclos inteiros — o incremento
  atual só a aproxima (erro O(1/N_emb)); a forma nova é *mais* fiel. Esperado um
  desvio numérico ~1% vs trajetórias atuais → coberto pela re-calibração no
  mesmo PR.
- `δ_emb(0) = emb_consumed_frac · emb_depth` representa arruela/junta reusada.
- Torna o *embedding renewal* no reaperto representável no futuro (item 5 do
  roadmap) — fora de escopo aqui, mas a forma deixa de bloquear.
- Novo arg opcional `DynamicStiffnessAnalyzer(..., initial_embedding_frac=0.0)`
  — espelha o par existente `initial_damage` (arg) ↔ `D_init` (estado/JSON): o
  nome do estado nomeado na condição/JSON é `emb_consumed_frac` (§2.3), o arg do
  analyzer é `initial_embedding_frac`. Default 0.0 = comportamento atual.

### 2.5 `SharedCalibrator` (novo, `calibration/shared_calibrator.py`)

```python
@dataclass
class ConditionSpec:
    name: str                    # "nova", "reusada", ...
    curves: List[dict]           # [{cycles, ratio}, ...]
    F0_init: float               # pré-carga do ensaio (F0_test entra aqui)
    delta_amp: float
    D_init: float = 0.0
    emb_consumed_frac: float = 0.0
    damage_active: bool = False

@dataclass
class SharedCalibrationConfig:
    geom: JointGeometry
    conditions: List[ConditionSpec]
    bounds: Dict[str, tuple]     # bounds das CONSTANTES FÍSICAS (§2.2)
    priors: Dict[str, float]     # default de literatura por constante
    lambda_reg: float = 0.001
    F_amp: float; theta: float; freq: float; n_cycles: int

class SharedCalibrator:
    def fit(self, free_constants: List[str]) -> dict
    def fit_parsimonious(self, tol=0.005, max_constants=5) -> dict
    def loco(self) -> dict       # leave-one-condition-out: refita sem a condição
                                 # e prediz a retida só com os estados nomeados
```

- Simulação por condição usa `JointMaterial(**constantes)` + estados da condição;
  tuners ficam nos defaults 1.0 (não são tocados).
- `loco()` é o teste de legitimidade: a condição retida é **predita**, não ajustada.

### 2.6 Persistência — bloco `shared` no `joint_calibrations.json` (schema aditivo)

```json
{
  "schema": 2,
  "shared": {
    "calibrated_at": "...",
    "free_constants": ["K_archard", "emb_depth", "tr_loose_gain"],
    "constants": {"K_archard": ..., "emb_depth": ..., ...},
    "conditions": {
      "nova":        {"states": {}, "MAE": ...},
      "reusada":     {"states": {"emb_consumed_frac": 1.0, "D_init": 0.3}, "MAE": ...},
      "sobretorque": {"states": {"F0_test_N": ..., "F0_provenance": "user|estimated"}, "MAE": ...},
      "reaperto":    {"states": {"D_init": 0.3}, "MAE": ...}
    },
    "loco": {"nova": {"MAE_pred": ...}, ...}
  },
  "profiles": { ... }   // bloco atual intocado durante o Estágio A (GUI continua lendo)
}
```

### 2.7 Tooling e relatórios

- `New_Theory/calibrate_shared.py` (espelha `calibrate_4_profiles.py`): roda o
  fit compartilhado + LOCO, salva bloco `shared`, gera
  `New_Theory/calibration_shared.png` (grid 2×2 com MAE por condição + tabela
  fit-vs-LOCO impressa).
- `identifiability_analysis.py` ganha modo `--shared`: espectro de `JᵀJ` sobre as
  constantes físicas do fit conjunto (todas as curvas).
- `MODEL_LEGITIMACY.md` ganha §4.5 (resultado do fit compartilhado) + changelog.

### 2.8 Gate de decisão A→B

Prosseguir para o Estágio B se:
1. Fit compartilhado fecha com **≤5 constantes fitadas** no dataset inteiro;
2. MAE por condição reportado honestamente (referência branda: ≲2× o MAE do fit
   parsimonioso por-condição; sem teto rígido — decisão do usuário);
3. LOCO documentado (predição da condição retida com só os estados nomeados);
4. Residual de conservação de energia inalterado (fora do regime de colapso).

Se falhar → documentar como falsificação (§7 do MODEL_LEGITIMACY), identificar o
mecanismo com forma errada e re-escopar o Estágio B (a limpeza ainda vale, mas o
resultado científico muda).

---

## 3. Estágio B — limpeza do engine (breaking, gated pelo A)

### 3.1 Remoções em `JointMaterial` (9 campos)

`k_emb_scale, k_creep_scale, k_wear_scale_ax, k_wear_scale_tr, k_loose_scale_ax,
k_loose_scale_tr, Phi_ax_correction, Phi_tr_correction, k_damage_scale`.

Os mecanismos passam a ler só as constantes físicas. `Phi_tr_correction` some
dentro de `tr_loose_gain` (produto exato). `k_loose_scale_tr` some — a rigidez
torsional vem de `k_j_init·d_2/2` (identificável pela Exp 1); se o fit
compartilhado não fechar sem ele, isso é falsificação da forma do mecanismo de
loosening, não motivo pra manter o knob.

### 3.2 Direcionalidade

`direction_blend` continua para a FÍSICA (projeção de slip ax/tr), mas o split
ax/tr de TUNERS desaparece. Se dados axiais futuros exigirem anisotropia de
wear, ela entra como UMA razão física nomeada (fora de escopo).

### 3.3 Compatibilidade e migração

- **`.msd` files / `model._v2_tuner_overrides`**: shim de tradução de chaves
  legadas com warning de deprecação —
  `k_emb_scale→emb_depth·=v`, `k_creep_scale→C_creep·=v`,
  `k_wear_scale_tr→K_archard·=v`, `Phi_tr_correction & k_loose_scale_tr→tr_loose_gain·=v`,
  `k_damage_scale→c_D·=v`; chaves `*_ax` ignoradas com warning. Arquivos velhos
  continuam carregando.
- **Server `_material(payload)`**: mesma tradução (já é field-agnostic, filtra
  por `__dataclass_fields__`).
- **`calibration_tuner.html`**: sliders renomeados para as constantes físicas
  (emb_depth [µm], N_emb, K_archard, C_creep, tr_loose_gain, c_D/k_dmg_*,
  slip_onset_W) + estados (D_init, emb_consumed_frac, F0_test).
- **GUI**: grupo "Non-linear V2 tuners" vira "V2 physical constants + states";
  `V2_PARAM_NAMES`/`PRESET_PARAMS` atualizados.
- **`StagedCalibrator`**: reimplementado sobre constantes físicas (segmentação e
  decomposição por mecanismo continuam valendo) ou aposentado em favor do
  `SharedCalibrator` — decidir no plano conforme o que o GUI usa.
- **`joint_calibrations.json`**: schema 2 vira canônico; bloco `profiles`
  (tuners) removido; `profiles.py` atualizado.

### 3.4 Testes

- Novos: equivalência do embedding ODE (trajetória virgem = forma fechada;
  `emb_consumed_frac` reduz o embedding restante), recuperação sintética do
  `SharedCalibrator` (gera dados com constantes conhecidas + ruído → recupera as
  direções stiff), LOCO harness, shim de chaves legadas, server com constantes
  físicas.
- Atualizados: `test_v2_calibration`, `test_staged_calibrator`,
  `test_calibration_server`, `test_calibration_profiles`,
  `test_v2_solver_preload`, `test_slip_onset_incubation`, `test_surface_damage`,
  `test_case_study_models` (todos referenciam tuners hoje).

### 3.5 Documentação (obrigatória, pelo header do MODEL_LEGITIMACY)

`MODEL_MATH_REFERENCE.md` (§ mecanismos, §12 calibração), `MODEL_LEGITIMACY.md`
(tabela §2, §4.5, §5.1 procedência, changelog), `CLAUDE.md` (tabela de perfis →
constantes compartilhadas; gotchas dos campos removidos).

---

## 4. O que NÃO muda

Teoria two-factor (Φ × hélice), Greenwood-Williamson, conservação de energia,
incubação (`slip_onset_W`, opt-in), física do surface_damage (c_D/W_ref/k_dmg_*),
disp-mode/force-mode, engine V1, os 4 mecanismos em paralelo, `CycleSnapshot`/
decomposição.

---

## 5. Critérios de sucesso

1. **≤5 números fitados no dataset inteiro** (vs 6 por-condição hoje), todos
   constantes físicas com unidade/bounds de literatura — zero multiplicadores
   adimensionais fitados.
2. As 4 condições reproduzidas pelo MESMO conjunto de constantes; diferenças só
   por estados nomeados mensuráveis. MAE por condição reportado lado a lado com
   os fits por-condição atuais.
3. LOCO: condição retida predita só com seus estados nomeados; gap fit→predição
   documentado.
4. Residual de conservação ≈ 0 fora do colapso; suíte de física existente verde.
5. Engine sem camada de tuners (pós-B); arquivos `.msd` legados carregam via shim.
6. Falha em fechar alguma condição sem knob por-condição → documentada como
   falsificação com mecanismo apontado (não silenciada com tuner novo).

---

## 6. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Física compartilhada não fecha as 4 condições | Gate A→B (§2.8); resultado vira achado de falsificação documentado — cientificamente valioso de qualquer forma |
| `F0_test` do TP6 desconhecido | Fallback §2.3: estimado uma vez, unidade física, sanity-check contra escoamento, marcado `estimated` |
| Desvio numérico do embedding novo (~1%) | Forma geométrica exata escolhida (§2.4); re-calibração no mesmo PR; teste de equivalência |
| Quebra de GUI/.msd/HTML no Estágio B | Shim de tradução + testes de migração; Estágio B só depois do gate |
| Sobre-ajuste disfarçado (estados virando knobs) | Estados são fixos por default; qualquer estado estimado é reportado com unidade + procedência no JSON |

---

## 7. Perguntas abertas (usuário)

1. **TP6 (sobretorque):** qual foi a pré-carga/torque real do ensaio? (Se não
   houver registro, aplica-se o fallback §2.3.)
2. **TP7 (reaperto):** procedimento de reaperto (torque de re-aperto, nº de
   ciclos antes do reaperto) — refina `D_init` e, futuramente, o renewal.
3. **Teto de MAE:** assumido "legitimidade em 1º, sem teto rígido" (§0.1) —
   confirmar ou impor teto.
