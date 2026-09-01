# Registro de ativação de parâmetros por regime de carregamento — design

**Data:** 2026-07-03
**Autor:** Prof. Leonardo Rosa Ribeiro da Silva (PhD) + Claude Code (brainstorming em duas frentes, consolidado)
**Status:** Design aprovado (sessão principal, 2026-07-03). Antecede o plano de implementação.
**Relacionado:**
- `docs/superpowers/specs/2026-07-02-shared-physics-model-design.md` (Estágio A/B; este registro generaliza o filtro de dano do `SharedCalibrator`)
- `New_Theory/MODEL_LEGITIMACY.md` §4 (identificabilidade — coluna ≈ 0 no Jacobiano ⇔ parâmetro estruturalmente inativo)
- `src/bolt_analysis_studio/calibration/shared_calibrator.py` (consumidor v1)
- `src/bolt_analysis_studio/core/models/element.py:211-213` (`LoadingType AXIAL/TRANSVERSE/COMBINED` — já existe no data layer V1, mapeamento futuro da GUI)
- `docs/superpowers/specs/2026-05-16-bas-v2-frontend-design.md` (frontend V2 herda o registro — consumidor futuro)

---

## 0. Problema e objetivo

Ideia do usuário: **um parâmetro só deve existir (ser pedido, validado ou fitado)
quando o regime de carregamento excita o mecanismo dele.** Exemplo dado: em
carregamento axial puro, o atrito de serviço da flange (`mu_bearing`) não
influencia nada — pedi-lo ao usuário ou oferecê-lo ao otimizador é convite a
overfitting e a "parâmetro sobrando".

Fundamento (MODEL_LEGITIMACY §4): um parâmetro cujo mecanismo não é excitado
tem coluna ≈ 0 no Jacobiano — **estruturalmente não-identificável**. O
`SharedCalibrator` já aplica esse princípio de forma pontual (constantes de
dano só entram se alguma condição tem `damage_active`). Este spec generaliza:
**uma tabela declarativa única** (parâmetro → predicado de ativação) que
calibração, validação e GUI consomem da mesma fonte.

### 0.1 Decisões do brainstorming (consolidação de duas frentes)

O brainstorming correu em duas frentes (sessão principal + subagente que o
usuário abordou diretamente); decisões consolidadas:

| Decisão | Escolha do usuário |
|---|---|
| Onde atua primeiro | **Registro único, consumido só pelo `SharedCalibrator`** (filtro de candidatos). GUI/validação depois, lendo o mesmo registro. |
| Dimensões do regime na tabela | **Completa (C)**: carregamento (axial/cisalhante) + estado da junta (reuso/dano) + térmico (ΔT) + proveniência de F₀. A tabela nasce completa; consumidores adotam as dimensões conforme existirem nos seus dados. |
| Aprovação do design | "Approve as designed" (sessão principal, 2026-07-03) |

Achados do subagente incorporados: `LoadingType` já existe (`element.py:211-213`);
`slip_onset_W` pertence ao conjunto gated por cisalhamento; o conjunto de dano
completo é `c_D, W_ref, k_dmg_mu, k_dmg_wear, D_init`; `mu_bearing` tem **dois
papéis** (aperto: torque→F₀; serviço: resistência ao slip transversal) com
predicados distintos.

---

## 1. `LoadingRegime` — o vocabulário dos predicados

Derivado por condição (na calibração, de `ConditionSpec`; futuramente, de
`LoadingData`/wizard):

```python
@dataclass(frozen=True)
class LoadingRegime:
    has_transverse_slip: bool   # sin(theta)>0 OU delta_amp>0
    has_axial: bool             # cos(theta)>0
    damage_active: bool         # junta reusada/reapertada (D_init/c_D>0)
    delta_T_nonzero: bool = False   # ΔT != 0 (LoadingData.delta_T; calibração hoje: False)
    F0_provenance: str = "nominal"  # nominal | estimated | torque | measured
```

Derivação na calibração: `regime_from_condition(cond: ConditionSpec,
estimated: bool) -> LoadingRegime` — `estimated` vem de `name in
config.estimate_F0`. `delta_T_nonzero` fica `False` (a calibração atual não
tem condições térmicas); a dimensão existe para os consumidores futuros.

## 2. A tabela — `ParameterRule`

```python
@dataclass(frozen=True)
class ParameterRule:
    name: str
    layer: str          # 'physical' | 'damage' | 'state' | 'friction'
    fittable: bool      # candidato do SharedCalibrator?
    active: Callable[[LoadingRegime], bool]
    rationale: str      # uma frase física, exibível em tooltip futuro
```

Tabela inicial (`PARAMETER_REGISTRY`):

| Parâmetro | fittable | Predicado | Racional |
|---|:--:|---|---|
| `emb_depth`, `N_emb` | sim | sempre (carga cíclica) | assentamento ocorre sob qualquer ciclo |
| `C_creep` | sim | sempre | fluência é função do tempo sob carga; **ΔT≠0 promove de opcional a obrigatório nos consumidores de validação** (dimensão térmica) |
| `K_archard` | sim | `has_transverse_slip` | wear do modelo é dirigido por slip transversal |
| `tr_loose_gain` | sim | `has_transverse_slip` | fator 1 transversal do two-factor |
| `c_D`, `k_dmg_wear` | sim | `damage_active` | dano superficial (migra o filtro `_DAMAGE_CONSTANTS`) |
| `W_ref`, `k_dmg_mu`, `D_init` | não (constantes/estado) | `damage_active` | física de dano + estado nomeado |
| `slip_onset_W`, `slip_onset_sharpness` | não (opt-in) | sempre¹ | gate de incubação é alimentado por `W_slip_acc` (slip transversal) |

¹ **Nuance de equação (descoberta no planejamento):** o gate multiplica também
o `dF_0` do loosening **axial**, mas `W_slip_acc` só acumula com slip
transversal — em axial puro com `slip_onset_W>0` o loosening ficaria
permanentemente suprimido. Comportamento atual do engine; o predicado honesto
é "sempre potencialmente ativo", com a nuance registrada no racional da regra
e no changelog do MODEL_LEGITIMACY. Revisitar se o track axial usar incubação.
| `mu_thread`, `mu_bearing` (papel **serviço**) | não | `has_transverse_slip` | resistência ao slip em serviço |
| `mu_thread`, `mu_bearing` (papel **aperto**) | não | `F0_provenance == "torque"` | conversão torque→F₀; com F₀ medido, dispensável até em axial |
| `emb_consumed_frac` | não (estado) | `damage_active` ou junta declarada reusada | estado nomeado de reuso |

Semântica de dataset: um parâmetro é candidato do fit se **alguma** condição o
ativa (`active_candidates(bounds, conditions)`); dataset misto cisalhamento+axial
mantém `K_archard`; dataset 100% axial nunca o oferece.

## 3. Consumidor v1 — `SharedCalibrator.fit_parsimonious`

Substituir o filtro hard-coded:

```python
# antes
cands = [c for c in self.cfg.bounds if c in self.cfg.priors]
if not any(c.damage_active for c in self.cfg.conditions):
    cands = [c for c in cands if c not in _DAMAGE_CONSTANTS]
# depois
cands = active_candidates(self.cfg.bounds, self.cfg.priors, self.cfg.conditions,
                          estimated=set(self.cfg.estimate_F0))
```

**Preservação de comportamento:** para os datasets atuais (4 condições shear,
disp-mode), o conjunto de candidatos é IDÊNTICO ao de hoje — mudança
estrutural, não numérica. O teste de paridade garante isso.

## 4. O teste que fecha o argumento — *registry-truth*

Para cada regra `fittable` com um regime que a DESLIGA: simular uma condição
inerte curta (ex.: axial puro força-controlada para `K_archard`), perturbar o
parâmetro ×2 e **assertar curva de pré-carga idêntica** (diferença ≤ eps de
máquina). Isso pina os predicados às equações reais do engine — o registro não
pode derivar silenciosamente do modelo. (É a versão executável do argumento
"coluna do Jacobiano ≈ 0".)

Testes adicionais: candidatos em dataset axial-only vs misto; paridade do
filtro de dano (comportamento atual preservado, suíte existente verde);
determinismo.

## 5. Fora de escopo v1 (roadmap declarado)

1. **Validação/`.msd`** (próximo consumidor, backend-first): `MSDModel.validate()`
   / `LoadingData` — erro se parâmetro exigido pelo regime falta; **aviso** se
   parâmetro fornecido é inerte ("μ_bearing fornecido, mas carregamento é AXIAL
   puro com F₀ medido — será ignorado"). Spec próprio.
2. **GUI V1 mínima**: cinza + tooltip (racional da regra) nos grupos do
   `PropertyInspector`, mapeando `LoadingType` → `LoadingRegime`. Junto com (1).
3. **Frontend V2** (task #16): herda o registro pronto.
4. **Dimensão térmica ativa**: quando houver condições com ΔT nos dados de
   calibração (hoje a regra existe na tabela mas não dispara).
5. Interação com o **Estágio B**: quando os tuners forem removidos, a tabela
   atualiza os nomes — o registro é dono da lista, não o contrário.

## 6. Critérios de sucesso

1. Dataset axial-only sintético: `K_archard`/`tr_loose_gain` **não aparecem**
   nos candidatos; misto: aparecem.
2. Datasets atuais: candidatos idênticos aos de hoje (paridade; suíte verde).
3. Registry-truth: todo predicado `fittable` comprovado contra o engine.
4. `MODEL_LEGITIMACY.md` ganha nota: não-identificabilidade estrutural tratada
   por construção (registro), com o registry-truth como verificação.
5. Nenhuma mudança no engine; nenhuma mudança de comportamento nos fits atuais.

## 7. Riscos

| Risco | Mitigação |
|---|---|
| Predicado errado (parâmetro ativo marcado inerte) | registry-truth falha alto; regra corrigida com evidência |
| Deriva registro↔engine em mudanças futuras | registry-truth roda na suíte; MODEL_LEGITIMACY exige atualização a cada mudança de modelo |
| Fork de design (duas frentes de brainstorming) | consolidado neste spec (§0.1); subagente instruído a redirecionar para a sessão principal |
