# Stage B — remoção da camada de tuners: scoping & assessment

**Data:** 2026-07-07
**Autor:** Claude Code (scoping, a pedido do Prof. Leonardo Rosa Ribeiro da Silva)
**Status:** SCOPING / ASSESSMENT — **não é endorsement**. A execução do Estágio B é
GATED pela decisão explícita do professor. Este documento mapeia o trabalho
concreto para essa decisão ser informada.
**Antecede:** o plano de implementação (a ser escrito só depois do "go").
**Fontes lidas:**
- `docs/superpowers/specs/2026-07-02-shared-physics-model-design.md` (§3 = o plano do Estágio B)
- `New_Theory/MODEL_LEGITIMACY.md` §4.5 (gate A→B), §4.6–4.10, §8 (veredicto honesto)
- `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (engine + tuners)
- `src/bolt_analysis_studio/calibration/{profiles,staged_calibrator,shared_calibrator,server,parameter_registry}.py`
- `src/bolt_analysis_studio/core/solver_worker.py`, `gui/main_window.py`, `numerical/parameter_identifier.py`
- `New_Theory/joint_calibrations.json`, `New_Theory/calibration_tuner.html`, `New_Theory/transfer_validation.py`

---

## 0. TL;DR — veredicto de prontidão

**CONDICIONAL, tendendo a "não agora".** A parte *científica* do Estágio B (provar
que os tuners são redundantes) já está **feita e mergeada** — é o bloco `shared`
(§4.5): 2 números fitados reproduzem as 4 condições, LOCO ≈ fit. Isso significa que
o Estágio B é uma limpeza de **engenharia** (breaking change de API), não uma
aposta científica.

Porém:
- **A limpeza breaking captura pouco valor novo** hoje: nenhum caminho da GUI lê o
  bloco `profiles` do JSON (achado, §3) — os tuners não estão "poluindo" o produto
  do usuário como o spec assumiu; eles vivem em `_v2_tuner_overrides` (parkados de
  uma calibração viva) e na infra de calibração/HTML.
- **Duas condições ainda não fecham** só com física compartilhada: sobretorque
  (MAE 0.138, falsificação estrutural — a **conformação** resolve isso mas vive no
  `shared`, ainda não é a mesma coisa que remover tuners) e, cross-rig, as
  constantes **não transferem** (§4.8, 46 curvas). O `k_wear_scale_tr` por-condição
  ainda está **substituindo procedência de constante que falta** (§4.8, §8).
- Remover a camada agora **congela** a resposta a essas lacunas numa reparametrização
  breaking, antes de a Fase 2 ("prover procedência por constante") ter maturado.

Recomendação: **adiar o Estágio B até a Fase 2 dar procedência a ≥1 constante
por-par (ex.: a âncora de `W_conf_ref`, ainda um null decisivo — §4.9)**, OU executar
uma **fatia mínima e não-breaking** agora (shim + tuner→constante no HTML/server,
mantendo os campos `k_*_scale` como aliases deprecados). O breaking-total do §3.1
(deletar os 9 campos) é o menos urgente e o mais arriscado dos passos.

---

## 1. O que "remover a camada de tuners" significa concretamente

### 1.1 Os 9 campos e onde cada um é consumido (engine)

Todos em `JointMaterial` (`dynamic_stiffness_analyzer.py:144–168`). Usos **completos**
no engine (grep exaustivo):

| Campo | Definição | Consumido em | Papel |
|---|---|---|---|
| `k_emb_scale` | :144 | `EmbeddingLoss.rate` :668 (`target = k_emb_scale·emb_depth`); `__init__` seeding :899; `retighten` :1111 | escala a **assíntota** do embedding |
| `k_creep_scale` | :150 | `CreepLoss.rate` :693 (`d_delta *= k_creep_scale`) | escala o creep |
| `k_wear_scale_ax` | :151 | `WearLoss.rate` :722 via `direction_blend` | wear axial |
| `k_wear_scale_tr` | :152 | `WearLoss.rate` :722–723 via `direction_blend`; escala **`d_wear` (dF_0) E `dE`** :725/:744 | wear transversal |
| `k_loose_scale_ax` | :153 | `RotationalLooseningLoss.rate` :831 via `direction_blend` | loosening axial |
| `k_loose_scale_tr` | :154 | idem :831–832 → multiplica `d_theta` :845 (linear) | loosening transversal |
| `Phi_ax_correction` | :156 | `Phi_eff` :318 | correção Φ axial |
| `Phi_tr_correction` | :157 | `Phi_eff` :318 **e** `RotationalLooseningLoss` :814 (`tr_loose_gain·Phi_tr_correction`) | correção Φ transversal |
| `k_damage_scale` | :168 | growth de `D` :1032 (`dD = k_damage_scale·c_D·…`) | escala o dano |

`direction_blend(θ, ax, tr)` (`:311`) = `ax·cos²θ + tr·sin²θ`. Em shear puro (θ=π/2)
só o termo `tr` sobrevive.

### 1.2 O que substitui cada tuner (§3.1 do spec)

Os mecanismos passam a ler **só a constante física**. Mapa canônico:

| Tuner removido | Absorvido por | Exatidão do fold (trajetória de ratio) |
|---|---|---|
| `k_emb_scale` | `emb_depth` (mesma expressão em :668/:899/:1111) | **EXATO** em dF_0 **e** dE |
| `k_creep_scale` | `C_creep` (`d_delta ∝ C_creep·k_creep_scale`) | **EXATO** em dF_0 e dE |
| `k_wear_scale_tr` | `K_archard` (só entra em `d_wear` :725) | **EXATO em dF_0** (ratio); **não** em `dE` :744 (dE usa `mu_bearing_eff`, não `K_archard`) → redistribui energia de atrito |
| `Phi_tr_correction` | `tr_loose_gain` (produto direto :814) | **EXATO** no caminho de loosening; **porém** `Phi_tr_correction` também entra em `Phi_eff` :318 (diagnóstico/matriz) — esse ramo se perde |
| `k_loose_scale_tr` | `tr_loose_gain` (spec §3.3) | **NÃO-exato**: `k_loose_scale_tr` é linear em `d_theta` :845; `tr_loose_gain` entra em `T_loose` → `slip_fraction` (não-linear). Equivalentes só se `T_resist≪T_loose`. |
| `k_damage_scale` | `c_D` (produto direto :1032) | **EXATO** |
| `k_wear_scale_ax`, `k_loose_scale_ax`, `Phi_ax_correction` | — (sem eixo axial calibrado) | **PERDIDOS** (spec §3.2: anisotropia ax/tr de tuner desaparece; se dados axiais exigirem, entra como *uma razão física nomeada*) |

**Ponto crítico de projeto:** na prática os perfis canônicos
(`joint_calibrations.json`) só liberam `{k_emb_scale, k_wear_scale_tr}` — todos os
outros ficam em 1.0. Os dois folds que importam de fato são **exatos na trajetória
de ratio** (`emb_depth`, `K_archard`). Os folds problemáticos (`k_loose_scale_tr`
não-exato; `Phi_eff` perdido; dE do wear redistribuído) só mordem para arquivos
`.msd` **legados** que setaram esses knobs à mão — o dataset de calibração nunca os
moveu. Isso **de-risca** o Estágio B substancialmente e deve ser dito ao professor.

### 1.3 Nota sobre campos "físicos-mas-tuner" que **NÃO** são removidos

`tr_loose_gain` (:121), `c_D`/`k_dmg_wear`/`W_ref` (:164–167), `slip_onset_W` (:195),
`W_conf_ref`/`conform_*` (:206–213), `k_emb_renew` (:149), `k_thread_fret` (:96),
`k_tr_mode`/`c_bend` (:177–178) **permanecem** — são constantes físicas / seletores
de forma, não a camada de multiplicadores adimensionais. `k_damage_scale` é a exceção
que sai (é um multiplicador puro sobre `c_D`).

---

## 2. Shim de compat `.msd` (o item de menor risco e maior retorno)

### 2.1 Onde os overrides vivem e fluem hoje

- Persistência: `model._v2_tuner_overrides` (dict de nomes completos de campo, ex.
  `k_emb_scale`). Escrito em `main_window.py:4916–4920` (`_apply_staged`, a partir de
  uma calibração viva do `StagedCalibrator`, **não** do JSON).
- Consumo no Run: `solver_worker.py:1024–1036` — filtra por
  `JointMaterial.__dataclass_fields__`, **type-aware** (str passa, numérico → float),
  e aplica sobre os defaults (`:1059`, `JointMaterial(**{**conf_defaults, **tuners})`).
- Consumo na calibração/HTML: `server.py:_material` (:45–55) filtra igual;
  `calibration_tuner.html` manda os tuners no payload (:370–373, :581–582).

### 2.2 Desenho do shim (tradução chave-legada → constante física)

Um único helper puro (proposta: `calibration/tuner_shim.py`, `translate_legacy_tuners(d: dict) -> dict`),
chamado nos **dois** pontos de entrada (`solver_worker` e `server._material`), com
`warnings.warn(DeprecationWarning)` por chave traduzida:

```
k_emb_scale        →  emb_depth      *= v      # exato
k_creep_scale      →  C_creep        *= v      # exato
k_wear_scale_tr    →  K_archard      *= v      # dF_0-exato (ratio); dE redistribui
Phi_tr_correction  →  tr_loose_gain  *= v      # exato p/ loosening; perde ramo Phi_eff
k_loose_scale_tr   →  tr_loose_gain  *= v      # aproximado (linear vs não-linear)
k_damage_scale     →  c_D            *= v      # exato
k_*_scale_ax / Phi_ax_correction     ignorados com warning  # sem eixo axial calibrado
```

**Requisitos do shim (o que o plano precisa cravar):**
1. **Composição multiplicativa correta:** se um `.msd` legado carregar `emb_depth`
   E `k_emb_scale`, o shim deve multiplicar, não sobrescrever. Como `_v2_tuner_overrides`
   é aplicado *sobre defaults*, o shim precisa rodar **antes** do merge e computar
   `emb_depth_final = emb_depth_base · Π(k_emb_scale)`.
2. **`k_wear_scale_tr → K_archard` toca também `ThreadFrettingLoss`** (:771 usa
   `K_archard`). Inerte por default (`k_thread_fret=0`), mas se ambos estiverem
   setados, o fretting axial passa a escalar junto. Documentar; provavelmente aceitar.
3. **Idempotência + ordem:** rodar uma vez, no ponto de entrada; nunca reintroduzir
   o campo legado no dict resultante (senão `__dataclass_fields__` já não o tem
   pós-remoção e ele seria descartado silenciosamente — o warning é o que evita a
   perda silenciosa).
4. **Cobertura de leitura de `.msd`:** confirmar que `project_io`/`from_dict`
   preserva `_v2_tuner_overrides` como está (é dict dinâmico, não campo de dataclass);
   o shim é aplicado no **consumo**, não na desserialização, para não reescrever
   arquivos do usuário.

### 2.3 O tuner HTML e o server já são meio-caminho

`calibration_tuner.html` **já** expõe sliders físicos (`emb_depth [µm]` :236,
`C_creep ×1e-12` :242, `N_emb`) **ao lado** dos tuners (`k_emb_scale (I)` etc.,
marcados `locked`, :265–292). Ou seja, a UI de calibração já fala "constantes
físicas"; o Estágio B remove os sliders `k_*` locked e renomeia o grupo. `server.py`
é field-agnostic (`:45–55`), então aceita constantes físicas sem mudança estrutural
— só o shim para chaves legadas de payloads salvos.

---

## 3. A "troca de fonte-de-verdade da GUI" — achado que re-escopa o §3.3

O spec (§2.6, §3.3) e o CLAUDE.md afirmam "o bloco `profiles` é o que a GUI lê" e o
Estágio B faz "o bloco `shared` virar o que a GUI lê". **Isto está impreciso e o
scoping precisa corrigir:**

**Nenhum código da GUI lê `joint_calibrations.json`.** Grep exaustivo de consumidores
do arquivo (todos os `.py`): só `New_Theory/*.py` (scripts de calibração +
`library_common` + `identifiability_analysis` + `sobretorque_f0bound`), `tests/*`,
`calibration/server.py` (serve `/profiles` ao HTML) e `calibration/profiles.py` (o
próprio I/O). `main_window.py` só menciona `_v2_tuner_overrides` (parkado de uma
calibração viva, :4916); os matches de "profiles"/"shared" em `msd_builder.py`/
`splash.py` são incidentais.

Portanto a "troca de fonte-de-verdade" real é, concretamente:

| Superfície | Estado hoje | Estágio B |
|---|---|---|
| **Run da GUI** (`solver_worker._compute_v2_history`, :1017–1059) | `JointMaterial` defaults hardcoded + `conf_defaults` + aplica `_v2_tuner_overrides` | ler as `constants` do bloco `shared` como baseline; `_v2_tuner_overrides` passam pelo shim |
| **Tuner HTML/server** | `/profiles` serve o bloco `profiles` (tuners) | servir `shared.constants`; remover sliders `k_*` locked (§2.3) |
| **Diálogo de calibração** (`_apply_staged` → `PRESET_PARAMS`) | `StagedCalibrator` (tuners) → `jm.*` targets (:4913–4920) | `SharedCalibrator` (constantes) ou `StagedCalibrator` reescrito sobre constantes (spec §3.3 deixa em aberto) |
| **`parameter_identifier`** (`PRESET_PARAMS` :280–313, `V2_PARAM_NAMES` :316) | 6 factories `jm_k_*_param` / `jm_phi_tr_param` alvejam `jm.k_*_scale` | renomear factories/targets para as constantes; `simulate_v2_curve` (:125) já aceita qualquer campo |
| **`joint_calibrations.json`** | `profiles` (tuners) + `shared` (constantes) coexistem | remover `profiles`; `shared` vira canônico; `profiles.py` perde `upsert_profile`/`upsert_profiles_bundle` |

**Bom para o professor:** como a GUI não depende do JSON, a "troca" é menos assustadora
do que o spec sugere — o Run só precisa apontar seu baseline para `shared.constants`
(hoje ele já injeta `conf_defaults` com `W_conf_ref=7671`, que **veio** do `shared`;
a diferença é lê-lo em vez de hardcodá-lo).

**Nota de manutenção (encontrada):** `parameter_registry.py` **não referencia nenhum
tuner** — seus candidatos já são as constantes físicas. Não precisa mudar para a
remoção de tuners (já está "Stage-B-shaped").

---

## 4. Superfície de re-validação exigida

### 4.1 Suítes de teste que referenciam os campos removidos

Grep dos 9 tuners nos testes → **53 ocorrências em 14 arquivos**. Todos precisam ser
atualizados ou aposentados (spec §3.4). Contagem por arquivo:

| Teste | Refs | Ação provável |
|---|---:|---|
| `test_calibration_profiles.py` | 8 | remover asserts de `profiles`/tuners; manter `shared` I/O |
| `test_staged_calibrator.py` | 6 | reescrever sobre constantes ou aposentar |
| `test_calibration_server.py` | 6 | payload com constantes + shim |
| `test_v2_solver_preload.py` | 6 | baseline `shared` no Run |
| `test_pressure_conformation.py` | 6 | provavelmente inalterado (usa `W_conf_ref` etc.) |
| `test_shared_calibrator.py` | 5 | núcleo — deve ficar verde sem mudança |
| `test_calibration_segmentation.py` | 4 | segmentação; decidir se sobrevive |
| `test_conformation_fit.py`, `test_embedding_state_based.py` | 3 cada | conformação/embedding — reescrever seeding sem `k_emb_scale` |
| `test_shared_block_persistence.py` | 2 | manter (é o formato canônico) |
| `test_library_common.py`, `test_retightening.py`, `test_slip_onset_incubation.py`, `test_surface_damage.py` | 1 cada | ajustes pontuais |

Suíte canônica a rodar (CLAUDE.md "Calibration package tests"): os ~24 arquivos
listados lá + `test_conformation_fit`, `test_pressure_conformation`, `test_retightening`
(não estão na lista do CLAUDE.md mas tocam os campos — **atualizar a lista** no mesmo PR).

### 4.2 Testes novos (spec §3.4)

- Equivalência do embedding ODE (trajetória virgem = forma fechada; `emb_consumed_frac`
  reduz o restante) — **já existe** `test_embedding_state_based.py`; estender.
- Recuperação sintética do `SharedCalibrator` (dados gerados com constantes conhecidas
  + ruído → recupera direções stiff).
- Harness LOCO.
- **Shim de chaves legadas** (novo — o item mais importante): asserta que um `.msd`
  com `{k_emb_scale, k_wear_scale_tr}` produz **exatamente** a mesma curva de ratio
  que o modelo pré-B com esses tuners. É o teste que garante que arquivos de usuário
  não quebram.
- Server com constantes físicas.

### 4.3 Re-validação numérica (os 4 perfis + a varredura de 46)

1. **4 perfis** (`calibrate_shared.py`): re-rodar o fit compartilhado; confirmar que
   MAE por condição casa com §4.5 (global 0.0509 no canônico atual do JSON;
   0.0796 na tabela §4.5 pré-conformação — **conferir qual é o baseline** antes de
   declarar regressão). A remoção de tuner **não deve mexer** nesses números (o
   `shared` já roda com tuners≡1.0).
2. **Equivalência pré/pós-B nos perfis com tuner:** rodar `nova`/`reusada` com o shim
   traduzindo `{k_emb_scale, k_wear_scale_tr}` e confirmar curva idêntica (à
   tolerância de FP) à do engine pré-B. Este é o critério de aceitação operacional.
3. **Varredura de 46 curvas** (`transfer_validation.py`, `DIGITIZED_CASES`, ~2–5 min):
   é **zero-refit** e roda com `JointMaterial` de constantes físicas — não usa a
   camada de tuners. Deve dar **bit-identical** antes/depois da remoção (só valida que
   nada regrediu na física). Baseline a bater: mediana MAE 0.2196, vence no-loss 34/46
   (§4.8).
4. **Conservação de energia:** residual ≈ 0 fora do colapso. **Atenção ao fold do
   `k_wear_scale_tr → K_archard`:** ele redistribui `dE` de atrito (§1.2). O residual
   deve continuar ≈0 (o balanço é internamente consistente), mas o número reportado de
   `W_diss_friction_y` muda para arquivos legados — cobrir num teste de conservação, não
   como igualdade de dE.

---

## 5. Riscos e sequenciamento

### 5.1 O que quebra

| Risco | Severidade | Mitigação |
|---|---|---|
| `.msd` legados com tuners deixam de carregar/rodar igual | **Alta** (é o produto do usuário) | Shim (§2) + teste de equivalência (§4.2); a maioria só usa `{k_emb, k_wear}` → folds exatos em ratio |
| `k_loose_scale_tr`/`Phi_eff`/dE não-exatos no fold | Baixa | Só afeta `.msd` que setaram esses knobs à mão (canônico nunca move); documentar no warning |
| Anisotropia ax/tr perdida | Baixa hoje, **média** se o trilho axial avançar | Adiar remoção dos `*_ax` até haver forma axial (item 9 do roadmap); ou mantê-los como no-op deprecado |
| `profiles` block removido quebra scripts `New_Theory` que ainda o leem | Média | `calibrate_4_profiles.py` (:129) e o `/profiles` do server; migrar ou manter leitura tolerante |
| GUI diálogo de calibração (`_apply_staged`) alvo de `jm.k_*` some | Média | Reescrever `PRESET_PARAMS`/targets no mesmo PR (parameter_identifier :280–316) |
| 53 refs de teste + 14 arquivos | Média (volume) | Mecânico, mas é o grosso do esforço |

### 5.2 Ordenação recomendada (se executar)

1. **Shim + testes de equivalência** (não-breaking; entrega segurança de migração isolada).
2. **Run/HTML/server lêem `shared.constants`** como baseline (troca de fonte-de-verdade,
   ainda com os campos `k_*` presentes como aliases 1.0).
3. **Diálogo de calibração + `parameter_identifier`** migram alvos para constantes.
4. **Só então** deletar os 9 campos de `JointMaterial` (breaking real) + atualizar os
   14 testes + remover `profiles` do JSON + docs (§3.5).

Fazer 1–3 primeiro deixa o passo 4 (o breaking) reversível e pequeno. Se o professor
quiser valor incremental sem breaking, **1–2 já entregam** "a GUI roda a física
compartilhada" sem tocar a API.

---

## 6. Assessment honesto — esforço/impacto e prontidão

### 6.1 Esforço (ordem de grandeza)

- Shim + equivalência: **pequeno** (1 helper + ~3 testes).
- Troca de fonte-de-verdade (Run/HTML/server): **pequeno-médio** (o Run já injeta
  `conf_defaults` que vieram do `shared`; é ler em vez de hardcodar).
- Migração do diálogo + `parameter_identifier`: **médio** (targets + `PRESET_PARAMS`
  + `V2_PARAM_NAMES` + `_apply_staged`).
- Deleção dos 9 campos + 14 testes + docs: **médio-alto por volume**, baixo por
  dificuldade (mecânico), mas **irreversível** e alto blast-radius.
- Total: **médio**. Não é um refactor de semanas, mas o breaking-total tem cauda longa
  de testes e docs.

### 6.2 Impacto

- **Científico: ~zero incremental.** A prova de que os tuners são redundantes **já
  está mergeada** (bloco `shared`, §4.5; reforçada por §4.7 — sob prior ancorado, o
  Estágio A fecha as 4 com **zero constantes de mecanismo fitadas**, sobra só o estado
  `F0_test`). Deletar os campos não torna o modelo "mais analítico" — ele já é, no
  `shared`. Torna o **engine** mais limpo (remove degenerescência de API), o que tem
  valor de manutenção, não de legitimidade.
- **Produto: baixo hoje.** A GUI não lê o JSON de tuners; o usuário não vê a camada.

### 6.3 As ressalvas do Estágio A tornam o B prematuro?

**Parcialmente sim.** Os resíduos são reais e apontam para "falta forma/procedência",
não "sobra tuner":

- **Sobretorque (§4.5/§4.9):** falsificação **estrutural** — MAE 0.138, 18.9× o fit
  por-condição, com `F0_test` **cravado no bound** mesmo elevado ao teto de sanidade
  (132.8 kN). A **conformação dependente de pressão** (driver `effective`) resolve isso
  e **foi adotada no bloco `shared`** — mas ela vive nas constantes de conformação
  (`W_conf_ref` etc.), que **não** são a camada de tuners. Ou seja: o buraco do
  sobretorque já não é "o `k_wear=0.045` está mascarando" — está resolvido por forma
  física. Isso *favorece* o B. **Porém** `W_conf_ref` é **per-par, sem âncora
  independente** (§4.9 strand 3, "null decisivo — nenhum dado da lib isola a
  constante") — remover a camada de tuners agora **congela** um `W_conf_ref` da escala
  UFU como se fosse universal (o caveat de escala já documentado em `solver_worker.py:1047–1051`).

- **Transferência cross-rig (§4.8, 46 curvas):** as constantes de wear/loosening **não
  transferem** entre rigs (mediana MAE 0.22; perde para 1-param local em 37/46; três
  modos de falha estruturados). O `k_wear_scale_tr` por-condição é, hoje, o lugar onde
  a **magnitude por-rig** é absorvida. Remover o tuner sem dar **procedência** ao
  `K_archard` por-par (tabela/âncora/medição — a Fase 2) só move o problema: o modelo
  fica sem o botão E sem a procedência. O §8 é explícito: "o programa migra de *fitar
  menos* para *prover procedência por constante*".

- **Formas faltantes ainda em aberto:** mecanismo ∝ A_F (axial, §4.6 Gate B1 FALHOU),
  escala rigidez-de-membro (§4.8 modo 3, Rousseau), embedding renewal (§4.10, validação
  zero-refit **bloqueada** por precisar de re-calibração por-rig). Remover `*_ax` agora
  fecha porta que o item 9 do roadmap vai querer aberta.

### 6.4 Veredicto

**CONDICIONAL.** O Estágio B é **cientificamente seguro** (a redundância dos tuners está
provada) e **tecnicamente de-riscado** (folds canônicos exatos, GUI não depende do
JSON, shim cobre legados). Mas é **de baixo valor incremental agora** e **prematuro no
ponto certo**: as constantes que os tuners por-condição absorvem ainda **não têm
procedência por-par** (Fase 2 em aberto — `W_conf_ref` sem âncora, `K_archard`/`C_creep`
por-par), e formas axiais faltantes ainda vão querer a anisotropia `*_ax`.

**Caminho recomendado ao professor:**
- **Agora (se quiser progresso):** executar só a **fatia não-breaking** — passos 1–2
  do §5.2 (shim + Run/HTML lêem `shared.constants`), mantendo os `k_*_scale` como
  aliases deprecados (default 1.0, no-op). Entrega "a GUI roda a física compartilhada"
  sem quebrar nada e sem congelar decisões da Fase 2.
- **Deletar os 9 campos (passo 4, breaking):** adiar até a Fase 2 dar **procedência a
  ≥1 constante por-par** (esp. `W_conf_ref` — hoje um null decisivo) e até a decisão
  sobre a forma axial (∝ A_F), para não ter que reintroduzir o eixo ax logo depois.
- Alternativamente, se o objetivo é puramente **higiene de engenharia** e o professor
  aceita re-abrir a API quando o axial amadurecer, o B completo é executável em esforço
  médio seguindo o sequenciamento do §5.2 — mas isso é uma escolha de manutenção, não
  um ganho de legitimidade.

**A decisão é do usuário.** Este documento registra o escopo e o custo/benefício; não
dispara a execução.
