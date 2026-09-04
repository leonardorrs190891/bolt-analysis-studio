# Relatório final — Limitações L1–L7 (branch `feature/l1-l7-gaps`)

**Data:** 2026-07-17 · **Branch:** `feature/l1-l7-gaps` (base `d960b4b`, main) · **Autor:** implementação
multi-agente (Tasks 0–11) sob a metodologia MEM (`src/.../docs/METHODOLOGY.md`) · **Fatia:** 8/8 (final)

**Escopo:** fechar as 7 limitações declaradas em `New_Theory/variable_explorer/concept_coverage.html`
(L1–L7) + 1 achado de engine (C2 — bookkeeping viscoso axial), usando a proveniência recém-coletada da
Rodada 5 (36 papers, 33 notas, 336 CSVs, `BAS_V2_papers/F. Rodada 5 (limitacoes 2026-07-16)/`) e a
síntese `Models/CALIBRATION_AND_VALIDATION/curve_library/ANALISE_MODELOS_R5.md`. Spec:
`docs/superpowers/specs/2026-07-16-limitacoes-L1-L7-implementacao-design.md` (decisões D1–D6). Plano:
`docs/superpowers/plans/2026-07-16-limitacoes-L1-L7-implementacao.md` (11 tasks).

---

## 1. Sumário executivo

- **11 tasks / 8 fatias completas**, TDD em cada uma (teste que falha → implementação → PASS + suíte),
  regra da casa respeitada em 100% dos commits: **nenhuma fatia toca `adopted_configs.json` ou
  `joint_calibrations.json`** (D3) — toda capacidade nova nasce **default-inerte** (flag/campo
  `JointMaterial` = 0.0/""/off) e o engine com flags desligadas reproduz o comportamento atual
  **bit-a-bit**.
- **Resultado misto e declarado sem maquiagem:**
  - **L1** (desgaste de flanco ∝ amplitude axial) — **FALSIFICADO** (Gate B1, 2 preregs consecutivos,
    `FAIL2`): a forma existe e foi testada, mas é ~8× rasa demais para o slope medido no Liu2017.
  - **L2** (rigidez de membro k_j(geometria)) — **PASS-inert**: lei física validada como
    **proveniência de geometria**, mas estruturalmente **sem efeito comportamental** nos 8 casos-gate
    (Rousseau/Zhang2006), por uma blindagem numérica específica do PACK adotado (θ=π/2 +
    `k_tr_mode='bending'`).
  - **L3** (acoplamento F_amp↔δ) — capacidade **default-inerte com proveniência** (Murai,
    Measurement-2021, JMP-2021), testada unitariamente (bit-identidade + guarda de caminho de código
    + efeito físico correto), **não calibrada per-rig**.
  - **L4** (conformação a ~1 GPa) — **null de literatura reconfirmado 3×** (Rodadas 4 e 5); nenhuma
    mudança de engine; valor segue dependente do experimento-âncora âncora interna.
  - **L5** (creep) — docstring corrigido (log-t, não Norton-Bailey) + forma saturante **opt-in**
    validada (Alamos), default permanece log-t.
  - **L6** (K_archard/k_wear_spec por par) — tabela de âncoras no `knowledge_base` por
    interface+par, com banda e proveniência (não resolve a não-universalidade, mas a documenta e
    centraliza).
  - **L7** (energia específica de remoção) — **bound informacional** (1,8–10,5 kJ/mm³, Shipway 2021),
    nunca bloqueia, nunca é fitável.
  - **C2** (bookkeeping viscoso axial) — o fix de código **já estava em `main`** (commit `bd9c779`,
    2026-07-07, antes desta branch existir); esta fatia **travou** o resultado em testes absolutos
    (<1 J, medido 0,002–0,084 J) e adicionou o check L7.
  - **22 casos novos wired** (Zhang2018=9, Zhang2019=4, Liu2020=9) como alvo de validação para uma
    futura rodada de fechamento de L1 — o modelo **sobre-prevê** nesses casos hoje (sinal
    consistente com a falsificação do Gate B1, não uma regressão).
- **Painel global (flags off = paridade):** ver §5 — a suíte completa foi re-simulada no worktree
  (199 casos: 180 herdados − 3 âncora interna não-versionados + 22 Rodada 5) e comparada byte-a-byte contra o
  baseline pré-branch.
- **ADOÇÃO REALIZADA NESTA BRANCH: ZERO.** `adopted_configs.json`/`joint_calibrations.json`
  permanecem intocados (verificado por `git diff main` no §8). Toda decisão de ligar qualquer
  capacidade por padrão, ou de integrar a branch ao main, é do professor.

---

## 2. Tabela mestre — fatia por fatia

| # | Fatia | Tasks | Commits | Limitação | Gate / Resultado | Recomendação de adoção | Classe de procedência (MEM/§4.26) |
|---|---|---|---|---|---|---|---|
| 0 | Base de conhecimento | T1 | `0693cdb..85bf873` | (infra p/ L1/L2/L5/L6/L7) | Testes de KB (query por par/interface devolve valor+banda+fonte) — PASS | **Merge seguro.** Camada de dados pura (JSON + funções de leitura); engine nunca lê o KB em runtime (só calibração/gates). Zero risco de trajetória. | mista — ver §3.0 |
| 1 | L3 | T2 | `85bf873..0b55c71` | F_amp↔δ em disp-mode | Bit-identidade off + efeito físico qualitativo correto (unitário) — PASS | **Manter default-inerte.** Falta calibração per-rig de `mu_eff_lo/mu_eff_F0_ref/gross_ceiling_decay` antes de qualquer adoção comportamental — nenhuma feita ainda. | forma (Murai/Measurement-2021/JMP-2021) |
| 2a+2b | L1 | T3+T4 | `0b55c71..dda9b64` | Gate B1 re-executado (prereg) | **FAIL2 — falsificação documentada** (slope ~8× raso demais) | **Não adotar.** Item de pesquisa aberto p/ rodada 6 (forma mais íngreme, ex. expoente >1,5 ou termo adicional); 22 casos novos (T10) ficam como alvo. | forma testada e refutada no nível atual |
| 3+3b | L2 | T5+T6 | `9c3f954..29c3d74` (+ fix `8514a13`, `e0f6baf`) | Gate D5 Rousseau/Zhang | **PASS-inert** (8/8, Δ MAE = 0,0 exato) | **Seguro adotar como proveniência** (`kj_mode="pedersen"` substitui a constante `k_j_init` fixa sem risco numérico nos casos testados) — **mas não fecha** a falsificação de escala-com-espessura sozinho (efeito estruturalmente nulo no PACK atual). Follow-up: confronto axial + campo `E_member` separado. | forma (Pedersen 2008, ranking Rousseau 2024: +24% vs Wileman +45–59%) |
| 4 | L5 | T7 | `374bc4e` (+docfix `ed4e3ec`) | Suíte de creep (JCSR/Caccese/Qin/li2022marstruc) sem regressão | **PASS** | **Manter log-t como default** (já coincide com a regressão do Nah 2014 p/ faiamento — achado, não trabalho novo); saturante disponível como opção per-rig se uma curva mostrar platô claro — decisão do calibrador. | forma (Alamos 2021/2022, 1os princípios) |
| 5 | L7 + C2 | T8 | `cc403a2` | (i) resíduo axial-força; (ii) bound de remoção | (i) **já resolvido em `main` antes desta branch** (commit `bd9c779`), travado em teste absoluto <1 J; (ii) bound sempre presente, nunca bloqueia | **C2: sem ação** (já é comportamento de `main`). **L7: informacional, adotar por default** (não muda trajetória, só relata quando fora da banda 1,8–10,5 kJ/mm³) — achado colateral: com `mu_bearing` default + `k_wear_spec` Zhang (par não-casado), o implied fica 1,71× acima do teto — usar pares casados na calibração. | derivado (Shipway 2021, taxa-dependente) |
| 6 | L4 | T9 | `aa0f8a1` | — (documentação) | Reconfirma null 3× (R4 Fouvry sub-GPa; R5 busca dirigida; R5 digitalização) | **Nenhuma ação de engine.** Valor de `W_conf_ref`/`n` segue dependente do experimento-âncora âncora interna (fretting ~1,2 GPa, medindo `n`) — spec já existe. | contexto (não transfere) |
| 7 | Wiring | T10 | `9e3dd67` | 22 casos novos (Zhang2018/2019 + Liu2020) | Registry/spot-checks — PASS | **Casos entram na suíte de validação** (não em `adopted_configs`); servem de alvo para fechar L1 numa rodada futura. | medido (curvas experimentais digitalizadas) |
| 8 | Este relatório | T11 | *(esta fatia)* | consolidação | Master run + reconciliações | — | — |

Legenda de classe (MEM/§4.26, `ANALISE_MODELOS_R5.md` linha 9): **medido** (valor experimental do par
certo) > **derivado** (calculado de dados do paper) > **forma** (a lei transfere cross-rig, a
constante não) > **contexto** (não transfere de jeito nenhum, só serve de precedente).

---

## 3. Detalhamento por fatia

### 3.0 Fatia 0 — Base de conhecimento (Task 1, commits `0693cdb..85bf873`)

Âncoras R5 em `calibration/knowledge_base.py` + `New_Theory/r5_anchors.json` (nenhuma mudança de
engine): `wear_spec_anchor(interface, pair)`, `mu_thread_anchor(coating)`, `creep_class(pair_class)`,
`removal_energy_bound()`, `kj_law(name)`. Conteúdo seeded:

| Tabela | Entradas | Fonte |
|---|---|---|
| `wear_spec` (k_wear_spec, K/H) | rosca 35CrMo-SCM435 = 8,34e-15 1/Pa; faiamento Q355B-Q235B = 6,7e-12 1/Pa; fretting 52100-52100 = 1e-4 (**"norm-own"**, não 1/Pa) | Zhang 2019 EFA; Li 2025 EngStruct; Warmuth 2015 |
| `mu_thread` por coating | zinco 0,150; DLC 0,126 | Liu 2020 Wear Tabela 2 |
| `creep_class` | faiamento-coating-zinco (α+β·log₁₀t, 4 espessuras) | Nah 2014 |
| `removal_energy_bound` (L7) | 1,8e3–1,05e4 J/mm³ | Shipway 2021 (derivado, taxa-dependente) |
| `kj_laws` | Pedersen 2008 (Eq.31) + Wileman 1991 (A,B por material) | ver §3.3 |

Review clean (sem findings bloqueantes). **1 Minor triado nesta fatia final** (era "triagem no review
final" no ledger do Task 1): o docstring de `wear_spec_anchor` devolve `{"value","band","unit",...}`
de forma genérica (correto), mas os **valores de `unit` NÃO são uniformes entre entradas** — thread e
faying usam `"1/Pa"` (K/H verdadeiro), enquanto fretting|52100-52100 usa `"norm-own"` (convenção
própria do Warmuth 2015, não diretamente K/H em 1/Pa). Um consumidor futuro que assuma "sempre 1/Pa"
sem checar a chave `unit` retornada erraria por esse par especificamente. **Ação tomada:** nenhuma
mudança de código — é um caveat de leitura, registrado aqui para o próximo consumidor (a tabela em si
já expõe a chave `unit` corretamente por entrada; o risco é só de uso descuidado). Suíte re-certificada
118/119 (1 falha pré-existente do main, ver §7).

### 3.1 Fatia 1 — L3: acoplamento F_amp↔δ em disp-mode (Task 2, commits `85bf873..0b55c71`)

Novo idioma em `JointMaterial`: `famp_couple_on` (0=OFF), `mu_eff_lo`, `mu_eff_F0_ref`,
`gross_ceiling_decay` (0=OFF). Com `famp_couple_on>0` em disp-mode, `F_amp` é re-clampado no topo de
`step_cycle` para `min(F_amp, mu_eff(F0)·F0)`, onde `mu_eff` cai com F0 baixo (proveniência Murai/
IJAMT-2023: µ_eff medido 0,46→0,24 com F0 crescente) e o teto pode decair com o dano acumulado
(proveniência JMP/Li&Hao-2021: pico F_S → residual F_R = 70–86%). `tests/test_l3_famp_coupling.py`
(11 testes): fórmula do teto (puro Coulomb / knockdown / saturação / decaimento por dano),
bit-identidade (flag off ⇒ trajetória idêntica), **guarda de caminho de código** (o helper
`famp_gross_slip_ceiling` não é sequer chamado com o flag off — mais forte que "resultado numérico
igual"), efeito físico (F_amp absurdo não piora além do teto), e prova registry-truth (campo é inerte
em força-axial pura, ativo em cisalhamento disp-mode).

Review clean. **Notas de adoção do ledger:** (a) Minor para a onda final —
`famp_couple_on`→`fittable=False` no `ParameterRegistry` (é um switch contínuo mas funciona como
gate, não como alvo de fit contínuo — mesmo idioma de `kj_mode`/`conform_driver`; **triado nesta
fatia**: confirmado no código atual que `famp_couple_on` não é oferecido como fittable, consistente
com o idioma dos demais mode-switches); possivelmente `mu_eff_F0_ref` também. (b) `tr_loose_gain`
(default 2,0) foi calibrado historicamente **sem** este clamp ativo — ligar `famp_couple_on` por
padrão exigiria re-checar essa calibração, não é plug-and-play. (c) **dupla via de dano no teto**: se
`k_dmg_mu` (amplifica o dano na fricção) E `gross_ceiling_decay` (decai o teto com o dano) estiverem
ligados simultaneamente, o dano afeta o teto de gross-slip por **dois caminhos independentes**
(via µ_eff E via decaimento direto) — não é um bug, mas é uma sobreposição de efeito a documentar se
algum dia os dois forem adotados juntos.

### 3.2 Fatia 2a+2b — L1: canal de desgaste de flanco ∝ A_F (Tasks 3+4, commits `0b55c71..dda9b64`,
fix-wave `0705f96`)

**Task 3** (`0b55c71..dac3a0f`): segundo canal independente em `ThreadFrettingLoss` (mesma interface
física — flanco de rosca —, complementar ao `k_thread_fret` legado que é hardcoded linear em F_ax).
Novo idioma: `flank_wear_on` (0=OFF), `k_wear_flank` [1/Pa], `flank_amp_exp` (default 1,0 = linear;
Liu 2020 sugere 1,5–1,6, super-linear). Parametrizado por **pressão** de flanco
`p_flank = F_0/A_s` (não força), só ativo em modo FORÇA (`delta_amp is None` — disp-mode é sempre
transversal nesta convenção do engine). Review clean com **3 Minors**, todos resolvidos na Task 4:
(i) DOF-guard vermelho (teto de graus de liberdade livres <89 batido + comentário desatualizado) —
corrigido; (ii) **convenção de distância de slip 2× vs 4×** — o canal legado usa
`fret_dist = 4·s_flank` (ida+volta ×2, "WearLoss-like"), o canal novo (`flank_wear_axial_term`) usa
convenção 2×; a Task 4 reconciliou usando um **seed efetivo dobrado** no gate
(`seed_used = 2 × anchor = 1,668e-14`, ver `l1_axial_gate_result.json`, chave `seed.convention_factor_2x`)
em vez de mudar a forma já testada; (iii) `flank_wear_on` redundante como fittable (é gate, não
magnitude) — a Task 4 fixou o gate em 1,0 e fitou só `k_wear_flank`/`flank_amp_exp`.

**Task 4** (`dac3a0f..dda9b64`, fix-wave `0705f96`): **Gate B1 re-executado, PREREG explícito**:

```
H0: com flank_wear_on, d(fim)/dA_F no rig Liu2017 tem sinal negativo e ordem 1e-5/N
PASS: slope in [-4.4e-5, -1.1e-5]/N (alvo -2.2e-5/N, tolerância 2x)
FAIL2: 2 preregs consecutivos falhando => falsificação documentada, sem forçar adoção
```

- **Tentativa 1** (`flank_amp_exp` livre): fit por curva-completa (cap 10k ciclos) em 22 curvas
  Liu2017+Liu2016 (rig A) + 4 curvas H.Li2022 (rig B); `k_wear_flank` satura no **limite inferior**
  da busca (o otimizador de MAE quer o canal o mais fraco possível); `flank_amp_exp` fitado = 0,656;
  **slope Liu2017 = −1,218e-6/N** — **fora da banda** (~18× raso demais).
- **Tentativa 2** (`flank_amp_exp=1,5` fixo, herdado do candidato Liu2020): `k_wear_flank` fitado =
  1,676e-14 (rig A) / 1,890e-13 (rig B); **slope Liu2017 = −2,765e-6/N**, slope Liu2016 =
  −1,912e-6/N — ainda **fora da banda** (~8× raso demais).
- **Veredito: FAIL2 — falsificação documentada, sem forçar adoção.** "A forma flanco-elástico ×
  Archard com nível Zhang é ~8× rasa demais para ∂(fim)/∂A_F do Liu2017; o mecanismo real é mais
  íngreme em A_F (cf. Liu2020, expoente 1,5–3,2 dependendo do regime); o canal permanece
  default-inerte como **capacidade validada, NÃO adotada**." Nenhum parâmetro axial entra livre na
  config canônica (`dof_canonical_axial = []`).
- **Achado colateral (side-finding, relevante p/ tabela de adoção):** no rig B (H.Li2022) o fit
  encontrou um **mínimo interior** (não saturado): k_wear_flank = 1,89e-13 (11,3× o seed, 22,7× a
  âncora Zhang) — o canal **melhora o NÍVEL** desse rig especificamente, **MAE 0,268→0,033** — embora
  não separe amplitude (H.Li2022 não varia A_F, só frequência). Isso é sinal legítimo para uma
  calibração **per-rig** futura (não para o gate global, que é sobre a FORMA/slope).
- **No-regression:** trajetória transversal (M16 shear canônico) **bit-idêntica** com
  `flank_wear_on=1` + valores fitados engajados — o canal é gateado OFF por construção
  (`delta_amp is not None` no PACK transversal).
- **Auditoria de reprodutibilidade** (fix-wave, achado do review): o JSON original não continha as
  grades de busca completas (finding "Important" do review); corrigido — as grades foram
  regeneradas deterministicamente (`np.linspace`, sem RNG) e **as 16 comparações** (fitted
  `k_wear_flank`/`flank_amp_exp` + MAEs, rig A e B, 2 tentativas) bateram **exatamente** (`==`, sem
  tolerância) com os valores já commitados — determinismo confirmado, veredicto intacto.

### 3.3 Fatia 3+3b — L2: lei k_j(geometria, material) (Tasks 5+6, commits `9c3f954..29c3d74` + fixes
`8514a13`, `e0f6baf`)

**Task 5** (`9c3f954..8514a13`): `kj_from_geometry(d_mm, L_mm, E_Pa, d_hole_mm, d_washer_mm, mode)`
em `calibration/library_common.py` — `mode="pedersen"` (Eq.31: assíntota
`k_m = E·d·[0,59(β²−α²)·d/L + 0,20(β+α)]`, β,α = razões arruela/furo) primária, `mode="wileman"`
(`k_m/(E·d) = A·e^(B·d/L)`, A,B por material) cross-check. Opt-in no engine: `JointMaterial.kj_mode`
(`""`=atual, default) — se a geometria do run fornecer `d_hole`/`d_washer` (>0), `k_j_init` é
substituído 1× na montagem do analyzer; senão cai silenciosamente no comportamento atual. Também
`phi_load_dep` (0=off): forma elíptica de Grosse 1990 p/ dependência de carga de Φ
(`F_m/F_i = 1−√(2λ−λ²)`, colapso de rigidez perto da separação), 1 parâmetro por-junta, opt-in
separado. Fix `8514a13` (review): sinal `kj_mode_engaged` exposto p/ o gate D5 distinguir "engatou e
não mudou nada" de "nem engatou" (ver mecanismo abaixo); `fittable=False` nos switches
(`famp_couple_on`, `phi_load_dep`) no registry.

**Task 6** (`29c3d74`, fix `e0f6baf`): **Gate D5** ("substituição de proveniência com erro ≤ igual,
não promessa de ganho de MAE") em 8 casos (Rousseau steel/HDPE t10/12/14 + Zhang2006 fig3/fig16), com
o side-arm Wileman documentado (não gateia). **Resultado: PASS-inert** — 8/8 sem regressão, **Δ MAE
= 0,0 EXATO** em todos os 8 casos, apesar de `k_j_init` mudar de fato (4,0e9 N/m fixo → 2,90–3,35e9
via Pedersen, variando com `L_eff`) e `Phi_eff_0` mudar de fato (+0,02 a +0,03 no ciclo-0 — prova de
que a lei engatou substantivamente no estado interno, não é um no-op disfarçado).

**Mecanismo do Δ=0,0 exato** (verificado numericamente, não só por inspeção): em todo caso
`transverse` o runner fixa `theta_load=π/2` exato; em `RotationalLooseningLoss` (único mecanismo que
lê `k_j` via `Phi_eff`/`Phi_ax`), o termo axial `L_ax = Phi_ax·sin(β)·F_ax` com
`F_ax = F_amp·cos(π/2) ≈ F_amp·6,12e-17` (resíduo de ponto-flutuante) — com `L_ax` ~15-17 ordens de
grandeza menor que `L_tr`, `(L_ax)²` cai abaixo da precisão double na soma `hypot(L_ax, L_tr)`:
`L_total` fica **bit-idêntico** independente de `Phi_ax`/`k_j`. **Correção de alcance do review**
(2026-07-17): esse underflow é **condicional à config**, não estrutural para todo caso transversal —
depende ADICIONALMENTE de `k_tr_mode != 'axial_frac'`; o PACK adotado seta `k_tr_mode='bending'`, que
garante o underflow; com o default `'axial_frac'` do engine, `k_j` alimentaria
`resolve_transverse_slip` e moveria a curva (~0,6% no Zhang-fig16, sonda numérica do reviewer). **A
conclusão vale para os 8 casos NO PACK adotado, não para "toda a biblioteca transversal".**

**Ranking de literatura registrado** (não gating): Pedersen 2008 é a forma mais próxima da verdade
(+24%, Rousseau 2024); Wileman 1991 superestima (+45–59%).

**Caveats herdados para follow-up (T11, já citados no ledger):** (i) `JointGeometry.E` é um único
campo usado tanto por `k_b` (parafuso) quanto por `kj_from_geometry` (deveria ser o E do MEMBRO) —
fica em aço (200 GPa) nos 8 casos, **inclusive HDPE**; a lei, do jeito que foi ligada, **não pode
capturar o contraste HDPE-vs-aço (~100× em E)** que motivou a série Rousseau — só captura a
dependência em grip/furo/arruela. Isso significa que **L2 validado como PASS-inert não fecha
sozinho** a falsificação de escala-com-espessura do painel de limitações (que segue como gap
declarado). (ii) confronto axial de `k_j` (casos com `theta != π/2` reais) não foi feito — é onde a
lei passaria a mudar a trajetória de fato. Ambos ficam como follow-ups nomeados, não como trabalho
desta fatia.

### 3.4 Fatia 4 — L5: creep (Task 7, commit `374bc4e` + docfix `ed4e3ec`)

Achado de engine (não específico de nenhum paper): o docstring antigo de `CreepLoss` dizia
"Norton-Bailey simplificado", mas a forma implementada é **log-t / linear em F0 / ilimitada no
tempo** — não é uma lei de potência. Corrigido o docstring (fatia 4 + docfix `ed4e3ec`: "coeficiente
compartilhado, não total" — precisão adicional pedida no review para o calibrador). **Coincidência
feliz documentada**: essa forma log-t já é EXATAMENTE a forma da regressão de relaxação por coating
do Nah 2014 (faiamento zinco inorgânico, `Creep = α+β·log₁₀t`) — o engine já estava certo para esse
par, sem trabalho novo.

Forma saturante **opt-in** (Alamos 2021/2022, creep de contato de 1os princípios):
`creep_mode="saturating"` (default `""` = log-t), `creep_t_c` (constante de tempo, 0=OFF cai no
log-t), `creep_alpha_sat` (expoente de forma, stretched exponential). `δ_max` é derivado do MESMO
`C_creep` já existente ("continuidade dimensional" — o brief pedia literalmente essa leitura; o
review refez a matemática e confirmou que um naive slope-match falharia ~800× na cauda se `δ_max`
fosse escalado por `creep_t_c/t_0` em vez de `C_creep·F_clamp` puro). `tests/test_l5_creep_saturating.py`
(9 testes): forma saturante perde menos na cauda e não colapsa a zero; trajetória monotônica;
bit-identidade tripla (default vs campos explícitos zerados; campos mudando sem o modo ligado;
modo ligado mas `creep_t_c<=0` cai no log-t); contrapositivas (modo+`t_c`>0 muda a trajetória;
`creep_alpha_sat` não é decorativo); registry-truth (`creep_t_c`/`creep_alpha_sat` fittable no mesmo
regime de `C_creep`; `creep_mode` é mode-switch, **omitido** do registro por completo — mesmo idioma
de `kj_mode`/`conform_driver`). Sem regressão nos casos de creep (JCSR/Caccese/Qin/li2022marstruc);
`tests/test_anchor_creep.py` também sem regressão. Review clean; Minors de narrativa anotados no
report da Task 7 (não bloqueantes, sem ação de código pendente).

### 3.5 Fatia 5 — L7 bound + C2 residual viscoso axial (Task 8, commit `cc403a2`)

**C2 — achado importante para a leitura honesta desta fatia:** o fix real (sourcing do amortecimento
viscoso de Rayleigh em `W_ext`, não só em `W_damp_visc`, no modo força axial) **já estava mesclado em
`main`** no commit `bd9c779` ("feat(engine): axial viscous energy source + Fouvry level anchor (Wave
2)", 2026-07-07 — **anterior à criação desta branch**, confirmado via
`git merge-base --is-ancestor bd9c779 d960b4b`). O trabalho real da Task 8 para C2 foi **escrever os
testes que travam esse resultado** dentro do pacote formal desta fatia (como pedia o brief), não
corrigir um bug novo. Medido: resíduo de conservação em modo força-axial puro (5 configs de smoke) =
**0,037 / 0,013 / 0,084 / 0,002 J**, todos `< 1,0 J` (era histórico −242,8 a −11,7 J antes do fix de
`main`). Prova adicional (não só numérica): `V_wear_removed`/`E_wear_removal` (os 2 campos NOVOS desta
fatia, para o bound L7) são **aditivos por construção** — um teste algébrico mostra que
`W_diss_total`/`conservation_residual` não os referenciam, logo não podem reabrir o canal para
NENHUM valor desses 2 campos, não só para o cenário testado.

**L7 — `EnergyBudget.removal_energy_check()`** (capacidade genuinamente nova desta fatia): retorna
sempre `{"implied_J_per_mm3", "in_bound", "bound"}`; `bound` (a banda 1,8–10,5 kJ/mm³ de Shipway 2021,
derivada, taxa-dependente) está sempre presente; `implied_J_per_mm3`/`in_bound` são `None` quando
nenhum volume foi removido ainda (wear inativo) — sem divisão por zero, sem exceção. **Puramente
informacional**: nunca bloqueia a simulação, nunca é fitável, é um hook de aviso de nível de
relatório. Verificado analiticamente (não só "não crashou"): com todos os gates inertes,
`implied = mu_bearing/k_wear_spec/1e9` exatamente (a área de contato cancela na razão
volume-Archard/energia-de-atrito).

**Nota de adoção (achado colateral, ledger):** rodando o check com `mu_bearing` **default** (0,15)
combinado com `k_wear_spec` do **Zhang** (8,34e-15, âncora de ROSCA) — um **par não-casado** (µ de
apoio/bearing com k_wear de flanco de rosca, interfaces diferentes) — o implied fica **17.986
J/mm³, 1,71× acima do teto** de 10.500. Isso não é um bug nem uma falha do bound: é um lembrete de
que `mu`/`k_wear_spec` devem vir do **mesmo par tribológico** na calibração (a tabela L6 do §3.0 já
organiza isso por interface); usar constantes de interfaces diferentes juntas pode produzir uma
energia implícita fisicamente inconsistente. Review clean sem findings.

### 3.6 Fatia 6 — L4: documentação MODEL_LEGITIMACY (Task 9, commit `aa0f8a1`)

Adendo §4.9 (2026-07-17) em `New_Theory/MODEL_LEGITIMACY.md`: **null de literatura reconfirmado 3×**
independentes — (1) R4 Fouvry sub-GPa (Baydoun 2019, 10–175 MPa, 1–2 ordens abaixo da janela de
parafuso; `n_p≈0,5–0,6`, regime-condicional); (2) R5 busca dirigida (Moshkovich 2024 ~1 GPa
auto-limitante e JMPT 2023 conformação-de-metais-com-causalidade-oposta, nenhum transfere); (3) R5
digitalização (Inose 2025 é a única fonte em aço no regime 0,48–1,90 GPa, mas é escala de aspereza —
teto 1,5·H, limiar bilinear ψ≈1,5 —, não energia macroscópica de junta). **Precedentes de forma**
registrados (não valores plug-in): expoente `n_p≈0,5–0,6` p/ `conform_pressure_exp`; teto de
aspereza `1,5·H` como sanity bound p/ `p_ref_conform` (hoje 5e8 Pa); tensão Etsion×Frérot (Etsion:
conformação satura em ~5 ciclos, mas em DESLOCAMENTO; Frérot: rugosidade satura mas a energia
plástica dissipada NUNCA satura — um `W_conf_ref` único em energia pode ser uma idealização).
**Conclusão sem mudança de veredicto:** o valor de `W_conf_ref`/`n` a ~1–1,5 GPa segue dependente do
experimento-âncora âncora interna (fretting ~1,2 GPa, medindo `n`, já spec'd). Cross-referência registrada:
`r5_anchors.json` não tem entrada de L4 (coerente com "forma sim, valor não"); o gate L2 (§3.3)
achou a trajetória transversal cega a `k_j` sob o PACK — por isso a dependência de pressão do
transversal mora na conformação (§4.9), não em `k_j`. Review clean sem findings; fatos checados
contra as apparatus notes da R4/R5.

### 3.7 Fatia 7 — Wiring dos 22 casos novos (Task 10, commit `9e3dd67`)

Zhang 2018 (*Wear*, 9 casos: Fig.2 tests1-4 @20kN + Fig.13 sweep 14/20/26kN + Fig.16 locker on/off),
Zhang 2019 (*EFA*, 4 casos: Fig.4 grupos 1e3/1e4/1e5/2e5 ciclos), Liu 2020 (*Wear*, 9 casos: Fig.5b
sweep de pré-carga 12/18/24kN + Fig.9 sweep de amplitude 0,1–0,4mm + Fig.15 zinco-vs-DLC) — todos
`ValidationCase`s novos via `_R5 = "BAS_V2_papers/F. Rodada 5 (limitacoes 2026-07-16)/digitized_csv"`,
padrão PACK (mesmo idioma de import-time da Rodada 4). Novo campo `ValidationCase.csv_y_scale`
(default 1,0) para o caso Liu2020 (R_F em PERCENTUAL, não fração — `y_scale=0,01`). Zhang2018+2019
são o par **companion** que motivou o alvo do Gate B1: preload loss com **ZERO rotação medida de
porca** (confirmado 2× — Zhang2018 porca prevailing-torque, Zhang2019 porca comum sem trava — mesmo
mecanismo, dupla confirmação experimental). Liu2020 é a curva mais limpa da biblioteca para
`d(afrouxamento)/d(amplitude)` (sweep confound-free de pré-carga × amplitude × revestimento).

`tests/test_r5_cases_wiring.py` (9 testes): contagens exatas por fonte (9/4/9); spot-checks
CSV-grounded (F0/n_cycles/ratio final rastreiam ao último ponto do próprio CSV digitalizado, não a
números hand-typed); conversão percentual→fração do Liu2020 (com sanity de que o CSV bruto é
realmente 0–100, não 0–1, e checagem final < 0,90 — um `/100` esquecido apareceria como >1);
proveniência do contraste de atrito zinco (0,150) vs DLC (0,126); integração no
`ValidationCaseManager` E no registry mestre (`family='transverse'`, `case_class='full_curve'`);
caveat de zero-rotação documentado nas notas de todos os 13 casos Zhang. Review clean.

**Sinal já observado (documentado no ledger, confirmado nesta fatia via master run — §6):**
`final_pred` roda em 0,13–0,31 nesses casos novos, contra `final_data` em 0,83–0,99 — o modelo
**sobre-prevê** o afrouxamento (perde preload rápido demais) no regime de desgaste de rosca puro sem
rotação. Isso é **exatamente** a assinatura da falsificação do Gate B1 (§3.2): o canal de flanco
FALSIFICADO como raso demais em amplitude não é a única lacuna aqui — o **nível** de perda por
desgaste de rosca em regime de baixa amplitude fixa (0,2–0,25mm, sem sweep) também está mal calibrado
nesses rigs específicos. Não é uma regressão (são casos NOVOS, nunca estiveram no baseline) — é o
**alvo declarado de validação para uma rodada futura de fechamento de L1**.

---

## 4. Reconciliações finais (Task 11, Deliverable A)

Três correções pequenas, acumuladas dos reviews de cada fatia, aplicadas nesta última fatia:

1. **Pins de contagem robustos** (`tests/test_validation_registry.py::test_registry_covers_all_cases_with_unique_ids`
   e `tests/test_user_cases.py::test_user_records_and_registry_integration`): o full-checkout
   (todos os CSVs presentes) é **202** = 180 herdados (114 + 64 Rodada 4) + 22 Rodada 5. Dois
   ambientes conhecidos degradam esse número **sem erro** (o `case_registry` classifica como
   `final_ratio` e descarta silenciosamente, spec §3): os **3 CSVs âncora interna não-versionados**
   (`Models/EXPERIMENTAL_ANCORA/reference_curves/*.csv`, gitignored, dado de lab) e a pasta
   **ainda-não-commitada** `BAS_V2_papers/F. Rodada 5 (limitacoes 2026-07-16)/` (o commit de
   wiring `9e3dd67` trouxe só o código Python, não os 336 CSVs/notas — permanece `Untracked` no
   `git status` desta branch). Os dois testes agora **medem** quantas dessas duas lacunas
   conhecidas estão de fato ausentes no ambiente corrente e exigem **exatidão** no resto — o pin
   ainda FALHA se qualquer OUTRA fonte wired for removida por acidente, mas não falha só porque um
   checkout não tem os CSVs âncora interna e/ou a pasta F. No worktree atual (ambos ausentes/presentes
   parcialmente: âncora interna ausente, pasta F presente) o valor esperado computado é 199, batendo com
   `n_registry` medido diretamente.
2. **`case_registry.py` `_SOURCE_NOTES`** — adicionadas as 3 novas fontes → caminhos de nota de
   aparato: `ZHANG_2018` e `ZHANG_2019` → `BAS_V2_papers/F. Rodada 5 (limitacoes 2026-07-16)/apparatus_notes/zhang.md`
   (nota única, cobre os dois papers-companion); `LIU_2020_WEAR` →
   `.../apparatus_notes/liu2020.md`. Mesmo padrão de degradação silenciosa (`note_path=None` sem
   exceção) se a pasta estiver ausente.
3. **Comentário de `csv_y_scale`** em `validation_cases.py` (já existia um comentário multi-linha da
   própria Task 10; reforçado nesta fatia para deixar explícito, sem ambiguidade, o caráter
   **informativo/não-propagado**): o campo é consumido **só** pelo loader em tempo de leitura
   (`_read_digitized_csv`, import-time); `runner.py`/`report_html.py` **não leem este campo** — eles
   re-leem o CSV cru para overlay e se autonormalizam dividindo pelo 1º ponto (`r/r[0]`), o que só
   funciona por acidente porque toda âncora t=0 do dataset é ~1,0 (ou 100,0 no caso Liu2020). Um
   consumidor futuro do CSV cru que não se autonormalize (ou cuja âncora não seja 1,0/100,0)
   precisa aplicar `csv_y_scale` explicitamente — não herda a conversão de graça.

Todas as mudanças foram syntax-checked (`ast.parse`) e a suíte afetada
(`test_validation_registry.py` + `test_user_cases.py` + `test_r5_cases_wiring.py`, 18 testes)
re-executada limpa.

**Nota honesta (não corrigida nesta fatia, fora do mandato de A):** a pasta
`BAS_V2_papers/F. Rodada 5 (limitacoes 2026-07-16)/` permanece **não commitada** nesta branch (git
status: `Untracked`). Diferente da Rodada 4 (`BAS_V2_papers/E. Rodada 4 .../`, cujos 196 arquivos —
incluindo os 176 CSVs, force-added por cima do `*.csv` do `.gitignore` — estão de fato versionados),
a pasta F não foi adicionada a nenhum commit desta branch. Os 22 casos novos e suas notas de aparato
**funcionam neste worktree** (os arquivos existem fisicamente em disco) mas **não sobreviveriam a um
clone fresco do branch** até que alguém rode `git add -f "BAS_V2_papers/F. Rodada 5 (limitacoes 2026-07-16)/"`
— decisão deliberadamente fora do escopo desta reconciliação (o brief pede para os testes
**tolerarem** essa ausência, não para eu commitar dados de terceiros sem instrução explícita).
Recomendo ao professor decidir se/quando versionar essa pasta (mesmo padrão da Rodada 4).

---

## 5. Painel global — master run (`python -m bolt_analysis_studio.validation.report --all`)

Executado em foreground a partir de `C:\bas2l17`, flags off (paridade — toda capacidade nova desta
branch é default-inerte, logo esta é simultaneamente a re-simulação completa E a certificação de
não-regressão de L1/L2/L3/L5/L7/C2 ao mesmo tempo).

| | n | mediana | média | gt_010 | gt_015 |
|---|---:|---:|---:|---:|---:|
| **Baseline** (main, pré-branch, `d960b4b`, ledger #59, 180 casos c/ âncora interna) | 180 | 0,04287 | 0,06589 | 32 | 17 |
| **Worktree (flags off)** — 177 herdados re-simulados | 177 | 0,04197 | 0,06588 | 32 | 17 |
| **Worktree + âncora interna herdados do store** — 180 (equivalente ao baseline) | 180 | **0,04287** | **0,06589** | **32** | **17** |
| **Worktree (flags off)** — 199 (177 + 22 R5) | 199 | 0,04700 | 0,12079 | 54 | 39 |
| **Equivalente full-checkout** — 202 (180 + 22 R5) | 202 | 0,04713 | 0,11998 | 54 | 39 |

**Paridade EXATA certificada:** a linha 180-equivalente reproduz o baseline dígito a dígito
(mediana 0,04287, média 0,06589, >0,10: 32, >0,15: 17) — zero regressão das 8 fatias com flags
off, verificada no conjunto completo, não em amostra. (Os 3 casos âncora interna usam os MAEs herdados do
store canônico — CSVs de referência não-versionados, ausentes do worktree; 2 chaves stale de dev
no store — `ensaio_teste_m12`, `exemplo_m12_sintetico` — foram excluídas por não pertencerem ao
registry.) O aumento de mediana/gt no painel de 199/202 vem INTEIRAMENTE dos 22 casos novos (§6).

**Leitura esperada e por quê:** como todo campo/flag novo desta branch é default 0.0/""/off, e o
`engine_fingerprint` dos 177 casos herdados não muda em nenhuma das 8 fatias (nenhuma altera o
comportamento com flags off), a mediana/gt_010/gt_015 dos 177 casos herdados devem reproduzir
**exatamente** o baseline (mesmo cálculo, apenas 3 casos a menos por ausência de CSV, não por
mudança de comportamento). O painel de 199 inclui os 22 casos novos, que **elevam** a mediana global
(eles têm MAE alto por design — são o alvo declarado de L1, não uma regressão, ver §3.7/§6).

---

## 6. Casos novos (22) — sinal L1 por fonte

| Fonte | n casos | MAE — resumo (master run) | Leitura |
|---|---:|---|---|
| ZHANG_2018 | 9 | mediana **0,602**, faixa [0,331; 0,697] | preload loss por desgaste de flanco, zero rotação medida |
| ZHANG_2019 | 4 | mediana **0,739**, faixa [0,513; 0,754] | companion validado, mesmo mecanismo, porca sem trava |
| LIU_2020_WEAR | 9 | mediana **0,482**, faixa [0,453; 0,570] | sweep confound-free amplitude×preload×coating |

**Sinal qualitativo já confirmado (ledger, T10):** `final_pred` nesses 22 casos corre em 0,13–0,31
contra `final_data` em 0,83–0,99 — o modelo sobre-prevê a perda de preload no regime de desgaste de
rosca em amplitude fixa baixa (0,2–0,25mm). Isto **não é um regressão** (casos nunca estiveram no
baseline) — é a confirmação, num conjunto de dados independente do usado no Gate B1 (que usava
Liu2017/Liu2016/H.Li2022, todos axiais força-controlada), de que a **forma/nível atual do canal de
desgaste de flanco é insuficiente também no regime transversal de baixa amplitude fixa** — reforça,
não contradiz, o veredito FAIL2 do Gate B1.

---

## 7. Suíte final

Suíte completa do CLAUDE.md (18 arquivos, `test_surface_damage.py` .. `test_transfer_validation.py`)
+ os 6 novos arquivos de teste desta branch (`test_knowledge_base_r5.py`,
`test_l1_flank_wear_axial.py`, `test_l2_kj_law.py`, `test_l3_famp_coupling.py`,
`test_l5_creep_saturating.py`, `test_l7_removal_bound_and_viscous.py`) + `test_r5_cases_wiring.py` +
os 2 arquivos reconciliados nesta fatia (`test_validation_registry.py`, `test_user_cases.py`), 27
arquivos/216 testes coletados ao todo:

```
214 passed, 1 skipped, 1 failed in 47.30s
```

A única falha é a **conhecida e pré-existente** `test_transfer_validation.py::
test_inputs_have_provenance_for_every_selected_case` (caso "Liu2025 M16 0.25mm", campo `F_amp_N`,
`prov="literature (Pai&Hess 2002: 0.38-0.49 medido)"` fora da whitelist `{paper, assumed, handbook,
iso}`) — **bit-idêntica** ao estado relatado pelo ledger desde a Task 0 ("suite 115/116, 1 falha
pre-existente do main"), reconfirmada por todas as 10 tasks subsequentes sem variar.

**Achado extra desta fatia (contexto, sem ação necessária):** essa exata falha **já foi corrigida em
`main`** pelo commit `5908c2b` ("fix(tests): whitelist de proveniencia aceita 'literature' (Pai&Hess
F_amp) — falha antiga achada pela Task 0 do L1-L7", 2026-07-17T07:35:53, campanha paralela em
andamento em `main` — ver nota de risco "OneDrive parallel-session hazard" na memória do projeto).
Confirmado via `git merge-base --is-ancestor 5908c2b main` (YES) e `...--is-ancestor 5908c2b HEAD`
(NO, não é ancestral desta branch) — ou seja, o fix chegou em `main` **depois** que esta branch
divergiu (`d960b4b`) e nunca foi trazido para cá (D6/D1: sem rebase intermediário contra um main
quente). **Nenhuma ação necessária agora**: um rebase/merge futuro desta branch para `main` (decisão
do professor) traz o fix automaticamente; não é uma regressão desta branch nem algo que a Task 11
precise corrigir.

---

## 8. Declaração de adoção

**Nenhuma capacidade desta branch foi adotada por padrão.** Verificação:

```
git diff main -- New_Theory/joint_calibrations.json   # vazio (confirmado)
git diff main -- New_Theory/adopted_configs.json      # vazio (confirmado)
```

Todo campo novo em `JointMaterial` nasce no valor neutro (0.0 / "" / off); todo `ParameterRule` novo
segue com predicado restrito ao regime correto (nunca oferecido fora do seu domínio físico); nenhum
gate PASS foi seguido de uma escrita em `adopted_configs.json`/`joint_calibrations.json` — mesmo os
2 PASSes (L2 D5, L5 sem-regressão) permanecem capacidades **disponíveis**, não **ligadas**. A decisão
de integrar esta branch ao `main`, e de ligar qualquer capacidade por padrão em qualquer config
adotada, é do professor — seguindo as regras de promoção por classe de procedência da metodologia MEM
(`src/.../docs/METHODOLOGY.md`).

---

## 9. Riscos, ressalvas e próximos passos

- **L1 permanece um gap real e não-trivial.** A falsificação do Gate B1 (§3.2) + o sinal dos 22
  casos novos (§3.7/§6) convergem: o mecanismo de desgaste de flanco precisa de uma forma mais
  íngreme em amplitude (o expoente testado, até 1,5, ainda erra por ~8×) — não é caso de "tunar
  mais forte", é caso de **forma faltante** ainda (mesma doutrina do roadmap #9 do CLAUDE.md).
- **L2 é proveniência, não solução.** `kj_mode="pedersen"` é seguro de ligar (PASS-inert
  estruturalmente garantido nos 8 casos-gate), mas **não fecha** a falsificação de escala-com-
  espessura do painel de limitações por conta própria — o efeito é estruturalmente nulo no PACK
  atual (θ=π/2 + `k_tr_mode='bending'`). Ligar `kj_mode` por padrão hoje seria adotar uma
  proveniência melhor sem ganho de MAE mensurável — decisão estética/de-integridade-física, não de
  performance.
- **Pasta `BAS_V2_papers/F. Rodada 5 .../` não commitada** (ver §4) — os 22 casos novos dependem
  dela fisicamente; recomendo versionar (force-add, mesmo padrão da Rodada 4) antes de qualquer
  merge para `main`, ou os 22 casos somem silenciosamente num clone fresco.
- **`W_conf_ref`/`n` seguem sem âncora de literatura** (L4, 3ª confirmação do null) — o único
  caminho aberto é o experimento-âncora âncora interna (fretting ~1,2 GPa) já spec'd; não é um item que a
  literatura resolve.
- **Par não-casado no check L7** (§3.5): usar `mu_bearing`/`k_wear_spec` de interfaces diferentes
  juntos produz um "implied" fisicamente inconsistente (1,71× acima do teto) — lembrete para a
  próxima calibração usar pares casados por interface (a tabela L6 já existe para isso).
- **Sobreposição de `dE` se os DOIS canais de flanco forem ligados juntos** (achado da onda final
  de fixes, Task 11, revisão de branch inteira): `k_thread_fret` (legado, convenção
  `fret_dist = 4·s_flank`) e `flank_wear_on` (L1, convenção `slip_dist = 2·s_th`, MESMA fórmula
  elástica `s = F_ax/k_b`) computam o trabalho de atrito (`dE`) cada um com sua PRÓPRIA convenção
  de distância. `tests/test_l1_flank_wear_axial.py::test_both_channels_combine_additively` já
  cobre a soma aditiva de `dF_0`/`dE`/`ds` quando os dois estão ativos — mas ligar os dois
  simultaneamente conta o trabalho de atrito real **~1,5× a mais** (`(4+2)/4`, tomando a convenção
  legada 4× como referência), já que ambos os canais representam o MESMO evento físico de
  micro-slip de flanco. A conservação de energia **fecha mesmo assim** (o `dE` inflado entra
  simetricamente em `W_ext` E no bucket de dissipação `W_diss_wear`, cancelando no resíduo — um
  double-count simétrico, não um vazamento), mas o número ABSOLUTO de calor de atrito reportado
  fica fisicamente inflado quando os dois canais coexistem. **Não co-habilitar os dois canais sem
  revisar essa sobreposição.**
- **O canal L1 não passa pelo `partial_slip_gate`** (achado da onda final de fixes, Task 11):
  dentro de `ThreadFrettingLoss.rate()`, o canal legado `k_thread_fret` é multiplicado por
  `partial_slip_gate(..., "fret", None)` (regime Cattaneo-Mindlin, ativo quando
  `slip_regime_mode="cattaneo_mindlin"`), mas a chamada ao helper `flank_wear_axial_term` (canal
  L1) não passa pelo mesmo gate. É uma assimetria **deliberada** (o canal L1 já é parametrizado
  por pressão de flanco + expoente de amplitude ajustável — um regime de forma diferente do
  regime de slip parcial do canal legado), mas que não estava documentada em lugar nenhum antes
  desta revisão. Registrado aqui para quem for calibrar/adotar os dois canais juntos no futuro.
- **Follow-ups nomeados** (não bloqueiam, ficam para uma rodada futura): confronto axial de `k_j`
  (L2), campo `E_member` separado de `JointGeometry.E` (L2), calibração per-rig de
  `mu_eff_lo`/`mu_eff_F0_ref`/`gross_ceiling_decay` (L3), forma mais íngreme para o desgaste de
  flanco (L1).

---

## 10. Anexo — commits da branch (`main..feature/l1-l7-gaps`)

```
9e3dd67 feat(l1l7): fatia 7 - casos Zhang2018/2019 + Liu2020 wired (F/F0 da pasta F; PACK)
aa0f8a1 docs(l1l7): fatia 6 - L4 null 3x + precedentes de forma no MODEL_LEGITIMACY §4.9
cc403a2 fix(l1l7): fatia 5 - C2 residual viscoso axial zerado + check L7 de energia de remocao (bound 1.8-10.5 kJ/mm3)
ed4e3ec fix(l1l7): fatia 4 - docstring: coeficiente compartilhado, nao total (precisao p/ calibrador)
374bc4e feat(l1l7): fatia 4 - L5 docstring log-t + creep saturante opt-in (forma Alamos; classes no KB)
e0f6baf fix(l1l7): fatia 3b - verdict PASS-inert + root-cause condicional a k_tr_mode=bending (enquadramento honesto p/ adocao)
29c3d74 feat(l1l7): fatia 3b - gate L2 D5 (resultado: PASS Rousseau/Zhang, kj_mode=pedersen zero-refit)
8514a13 fix(l1l7): fatia 3 - sinal kj_mode_engaged p/ gate D5 + registry fittable=False em switches (famp_couple_on, phi_load_dep)
9c3f954 feat(l1l7): fatia 3 - lei k_j(geometria,material) Pedersen-primaria + Wileman + phi elipt. Grosse (opt-in)
0705f96 fix(l1l7): fatia 2b - persistir grades de busca no JSON do gate (auditabilidade) + correcao 11.3x seed vs ancora
555d329 fix(l1l7): corrige baseline Task 0 -- 180 casos (ledger #59), mae_std/maxerr_gt_010/tripe por caso
dda9b64 feat(l1l7): fatia 2b - gate B1 re-executado com canal de flanco (resultado: FAIL slope=-2.8e-6/N, falsificacao documentada) + DOF-guard honesto 89 campos
dac3a0f feat(l1l7): fatia 2a - L1 canal de desgaste de flanco prop. a A_F (forma Zhang, nivel KB Zhang2019; default-inerte)
0b55c71 feat(l1l7): fatia 1 - L3 acoplamento F_amp<=mu_eff(F0)*F0 em disp-mode (default-inerte; proveniencia Murai/Measurement2021/JMP2021)
85bf873 feat(l1l7): fatia 0 - ancoras R5 no knowledge_base (k_wear por interface, mu por coating, classes de creep, bound L7, leis k_j)
0693cdb chore(l1l7): branch + baseline MEM do gate global
b0ee37f docs(l1l7): spec D1-D6 + plano 11 tasks + analise de modelos R5
```

Mais os commits desta fatia final (reconciliações + este relatório + `concept_coverage.html`), ver
`git log --oneline main..feature/l1-l7-gaps` no `task-11-report.md`.

**Fim do relatório.**
