# Alavanca de calibração por estágio + variável surface_damage — design

**Data:** 2026-06-20
**Autor:** Prof. Leonardo Rosa Ribeiro da Silva (PhD) + Claude Code (brainstorming)
**Status:** Design aprovado (5 seções). Antecede o plano de implementação.
**Relacionado:**
- `New_Theory/MODEL_MATH_REFERENCE.md` (matemática do engine atual)
- `docs/superpowers/specs/2026-05-17-calibration-experiments.md` (sequência de calibração)
- `docs/superpowers/specs/2026-05-16-two-factor-loosening-theory.md` §12 (teoria [K] dinâmica)
- `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (engine V2)
- `New_Theory/calibrate_4_profiles.py`, `New_Theory/calibration_tuner.html` (tooling atual)

---

## 0. Problema e objetivo

Hoje a calibração do `DynamicStiffnessAnalyzer` joga tudo num **custo escalar único**
(`differential_evolution` + `least_squares` sobre o MAE médio da curva inteira). O
resultado: **não há alavanca para melhorar o ajuste em nenhum recorte** — nem por
faixa de ciclos (estágios da curva), nem por mecanismo físico, nem pela sequência de
experimentos de calibração. O otimizador troca um trecho da curva pelo outro e o
usuário não tem como dizer "este estágio está ruim, corrija só ele".

Além disso, o caso **reaperto (TP7)** colapsa para ~0 até ~500–1000 ciclos — um
*runaway* que o modelo atual não captura: ele satura `k_loose_scale_tr` em 10 e ainda
erra a inclinação.

**Objetivo deste spec (escopo aprovado):**
1. Construir a **alavanca de calibração por estágio** (modo híbrido: otimizador em
   estágios + tuner interativo instrumentado), com **fonte única** do modelo.
2. Adicionar a variável de estado **`surface_damage`** para capturar o reaperto/TP7.

**Fora de escopo (viram specs futuros):** track de calibração axial, acoplamento
`F_amp↔delta_amp` em disp-mode, embedding renewal no reaperto, slope bilinear
pré-separação.

### 0.1 Requisitos levantados (brainstorming)

| Decisão | Escolha do usuário |
|---|---|
| Sentido de "estágio" | **Os três juntos** — faixa de ciclos, mecanismo, e experimento; o gargalo é o custo escalar único |
| Modo de trabalho | **Híbrido** — staged optimizer faz o grosso + tuner interativo com erro/estágio e contribuição/mecanismo ao vivo |
| Escopo | **Calibração + `surface_damage`** |
| Critério de sucesso | **Os três, com física em 1º** — erro/estágio baixo + tuners interpretáveis (perto de 1, sem saturar) + iteração rápida; no empate, tuner crível > 1 decimal de MAE |
| Arquitetura | **A** — núcleo Python (fonte única) + tuner servido por servidor local |

---

## 1. Arquitetura e fonte única

**Princípio:** o `DynamicStiffnessAnalyzer` (Python) passa a ser a **única**
implementação do modelo. A reimplementação JS dentro do `calibration_tuner.html` é
**removida**; o tuner vira cliente fino que pede a curva ao servidor.

### 1.1 Novo pacote

```
src/bolt_analysis_studio/calibration/
  __init__.py
  segmentation.py      # StageSegmentation — partição em janelas de ciclos, MAE por segmento
  decomposition.py     # MechanismDecomposition — atribui dF_0 de cada ciclo a cada mecanismo
  staged_calibrator.py # StagedCalibrator — fit sequencial com travas + regularização física
  profiles.py          # load/save joint_calibrations.json (compartilhado por batch e servidor)
  server.py            # servidor HTTP local que expõe o engine real ao tuner
```

Pacote separado de `numerical/` (que guarda os engines) por ser uma unidade de
responsabilidade distinta: fitting, segmentação, serviço.

### 1.2 Mudanças no engine (`numerical/dynamic_stiffness_analyzer.py`)

- `SlowState` ganha o campo `D` (surface_damage), inicializado em `D_init`.
- `CycleSnapshot` ganha campos **opcionais** `dF_0_by_mech` e `dE_by_mech` (dicts) —
  habilitam a decomposição sem quebrar o que existe.
- `JointMaterial` ganha os parâmetros de dano (§3).

### 1.3 Fluxo de dados

```
                    ┌─────────────────────────────────────────┐
                    │  DynamicStiffnessAnalyzer (FONTE ÚNICA)  │
                    │  + surface_damage  + decomposição/ciclo  │
                    └───────────────┬─────────────────────────┘
                        ┌───────────┴───────────┐
            (batch)     ▼                       ▼   (interativo)
        StagedCalibrator                   server.py (HTTP local)
        calibrate_4_profiles.py  ──escreve──►  joint_calibrations.json
                                                   ▲           │ JSON: curva + erro/segmento
                                          profiles │           ▼ + contribuição/mecanismo + D(N)
                                                   │   calibration_tuner.html (cliente fino)
                                                   └───────────┘  sliders + travas → re-pede ao servidor
```

Ambos os consumidores (batch e tuner) leem/escrevem o mesmo `joint_calibrations.json`
via `profiles.py`. **Zero duplicação de física.**

---

## 2. Motor de calibração em estágios

### 2.1 `StageSegmentation`

Particiona a curva em janelas de ciclos com **fronteiras ajustáveis** (requisito de
primeira classe: parâmetros no batch e fronteiras **arrastáveis** no tuner).

| Estágio | Janela (ciclos) | Mecanismo dominante | Tuners "donos" |
|---|---|---|---|
| **I — assentamento** | 0 – `N_I` (~100) | embedding | `k_emb_scale` |
| **II — afrouxamento** | `N_I` – `N_II` (~100–1000) | loosening + wear + damage | `k_wear_scale_tr`, `k_loose_scale_tr`, `Phi_tr_correction`, `k_damage_scale` |
| **III — relaxação** | `N_II` – `N_end` (~1000–2500) | creep | `k_creep_scale` |

`N_I`, `N_II` são parâmetros, **não** hard-coded. Reporta **MAE por segmento**, não só
global. A partição deve cobrir `[0, N_end]` sem buracos nem overlaps para qualquer
`N_I < N_II`.

**Ressalva física (a expor, não esconder):** a contribuição *por ciclo* do creep decai
~1/t (é maior no início, onde embedding mascara). A alavanca de `k_creep_scale` na
cauda é a do **efeito cumulativo**, não da taxa instantânea — funciona, mas é suave. A
decomposição deixa isso visível.

### 2.2 `MechanismDecomposition`

A cada ciclo o engine já roda cada mecanismo; passamos a registrar `dF_0_by_mech` no
`CycleSnapshot`. A decomposição:
- valida que `Σ dF_0_by_mech == dF_0_total` por ciclo (deve fechar exato — é a mesma soma);
- produz, por segmento, o **share de cada mecanismo** (ex: "Estágio I: embedding 82%;
  Estágio II: loosening 61%");
- alimenta o overlay do tuner: você *vê* quem domina onde antes de mexer.

### 2.3 `StagedCalibrator`

Fit sequencial com travas + regularização física:

```
fit_stage(I):   minimiza  MAE_segI(k_emb_scale)            + λ·Reg(k_emb_scale)
                trava k_emb_scale
fit_stage(II):  minimiza  MAE_segII(k_wear, k_loose,
                                    Phi_tr, k_damage)       + λ·Reg(...)
                trava esses
fit_stage(III): minimiza  MAE_segIII(k_creep)              + λ·Reg(k_creep)
                trava k_creep
→ coordenada-descida: repete I→II→III por 2–3 passes até convergir
  (estágios são levemente acoplados: loosening do II extrapola pra cauda,
   creep do III absorve o resíduo lá)
```

**Regularização física** (a prioridade nº 1 do usuário — o que diferencia de minimizar
MAE puro):

```
Reg(p) = Σ_i [ (p_i − 1)²            ← puxa cada tuner pra perto de 1.0
             + barreira_log(p_i)  ]   ← repele dos bounds (evita saturar em 1e-4 ou 10)
```

`λ` é um knob exposto (default escolhido pra física vencer empates: tuner crível > 1
decimal de MAE). Cada estágio usa `least_squares` (rápido — 1 param no Estágio I, ~4 no
II, 1 no III), com multi-start leve pra robustez. Determinístico por seed.

**Saída:** os tuners por perfil + `D_init` + relatório de MAE por segmento + shares por
mecanismo, gravado no `joint_calibrations.json`.

---

## 3. Variável de estado `surface_damage`

### 3.1 Motivação física

Junta reapertada já tem a superfície danificada do primeiro aperto (asperezas amassadas,
fretting, debris), então a integridade degrada com **realimentação positiva** — o
runaway do TP7. O modelo atual não tem essa variável.

### 3.2 Estado e lei de crescimento

`D ∈ [0,1]` no `SlowState`. D=0 prístino, D=1 integridade nula.

```
dD/dN = k_damage_scale · c_D · (W_diss_cycle / W_ref) · (1 − D)
```

- `c_D`, `W_ref` — taxa e escala de referência (defaults físicos no `JointMaterial`)
- `W_diss_cycle` — energia dissipada no ciclo (majoritariamente trabalho de slip de wear+loosening)
- `(1 − D)` mantém D ≤ 1 (crescimento saturante)
- `k_damage_scale` — o tuner novo (default 1.0, como os demais)

### 3.3 Realimentação (o runaway)

D corrói a resistência ao afrouxamento:

```
mu_eff     = mu_bearing · (1 − k_dmg_mu · D)    ← superfície danificada perde atrito
F_slip_eff = F_slip     · (1 − k_dmg_mu · D)    ← onset de slip cai
```

Menos atrito → menos `T_resist` → mais loosening → mais energia de slip → mais D → … =
**feedback positivo = o colapso**. É exatamente o mecanismo que falta hoje.

### 3.4 A assinatura do reaperto — `D_init`

Junta reapertada *começa* danificada → `D_init > 0`. O perfil "reaperto" é
caracterizado por `D_init` (ex: 0.3) enquanto "nova" tem `D_init = 0`, **sem precisar
saturar `k_loose`**. `D_init` é parâmetro de perfil/estado, não multiplicador.

### 3.5 Encaixe na arquitetura

D **não** é um mecanismo de perda paralelo — ele *modula* os outros. Então D é variável
de slow-state atualizada no `step_cycle` (vê o estado de início de ciclo, como os demais
— sem dependência de ordem), e `T_resist`/`F_slip`/loosening/wear leem o atrito modulado
por D. Isso preserva o balanço `F_0 = F_0_init − k_b·Σδ` e a **conservação de energia**
(D redistribui quanto de loosening/wear ocorre, não cria/destrói energia — residual
deve seguir ≈ 0).

### 3.6 Novos parâmetros

| Tipo | Nome | Default | Papel |
|---|---|---|---|
| Físico (`JointMaterial`) | `c_D` | calibrado | taxa de crescimento do dano |
| Físico (`JointMaterial`) | `W_ref` | calibrado (>0) | escala de normalização da energia |
| Físico (`JointMaterial`) | `k_dmg_mu` | calibrado | acoplamento dano→perda de atrito |
| Tuner (`JointMaterial`) | `k_damage_scale` | 1.0 | multiplicador de calibração |
| Estado/perfil | `D_init` | 0.0 (reaperto>0) | dano inicial |

A decomposição também expõe a **trajetória D(N)** e o fator de amplificação, pra ver o
runaway se formando antes de aceitar o fit.

### 3.7 Candidatas a validar (não fixas)

As formas funcionais exatas são candidatas a validar contra o TP7 com a ferramenta nova:
energia vs distância de slip como driver; coupling em `mu` vs em `Phi_tr`. Começa com as
acima; o tuner deixa testar variações.

---

## 4. Servidor local + protocolo + tuner instrumentado

### 4.1 Servidor (`server.py`)

Stdlib `http.server` (**zero dependências novas**). Serve **o próprio tuner** e a API na
mesma origem (sem CORS). Uso: `python -m bolt_analysis_studio.calibration.server` →
abre `http://localhost:8765/`.

| Método | Rota | Faz |
|---|---|---|
| `GET` | `/` | serve `calibration_tuner.html` |
| `POST` | `/simulate` | roda o engine **real**, devolve curva + decomposição + D(N) + MAE por segmento (hot path, debounced) |
| `GET` | `/profiles` | lê os 4 perfis do `joint_calibrations.json` |
| `POST` | `/calibrate` | roda `StagedCalibrator` (só tuners destravados) → fit por estágio sem sair do tuner |
| `POST` | `/profiles/save` | persiste perfil de volta no JSON via `profiles.py` |

### 4.2 Contrato do `/simulate` (chamada quente)

```
REQUEST  { geom, mat{...tuners + c_D, W_ref, k_dmg_mu},
           loading{F0_init, F_amp, theta, freq, N, delta_amp, D_init},
           segments{N_I, N_II}, reference[[cycle, ratio]...] (opcional) }

RESPONSE { curve{N, ratio},
           decomposition{ embedding[], creep[], wear[], loosening[] },  ← share/ciclo
           damage_trace{N, D},
           segments{ I:{window, mae, dominant, shares},
                     II:{...}, III:{...} },
           energy{conservation_residual},
           separated_at: N | null }
```

### 4.3 Tuner refatorado — a instrumentação

1. **Travas (lock) por slider** — tuner travado fica fora do auto-fit.
2. **Fronteiras `N_I`/`N_II` arrastáveis no gráfico** — linhas verticais que você move;
   segmentos e MAE recalculam na hora (o requisito de janelas ajustáveis).
3. **Badge de MAE por segmento** — Estágio I/II/III, cada um com seu erro, verde/vermelho ao vivo.
4. **Overlay de contribuição por mecanismo** — quem domina cada segmento.
5. **Mini-plot D(N)** — vê o runaway de dano se formar antes de aceitar o fit.
6. **Botão "Auto-fit deste estágio"** — chama `/calibrate` só com os tuners daquele
   estágio destravados → fit em estágios sob demanda. **É aqui que o híbrido acontece:**
   manual + otimizador na mesma tela.
7. **Seletor de perfil + Salvar** (existentes) agora via servidor.
8. **Upload/overlay de CSV de referência** (existente) — dirige o MAE por segmento.

### 4.4 Tratamento de erro no protocolo

- Servidor valida payload (tipos/ranges) → 400 com mensagem clara.
- `F_0→0` (junta solta) → engine corta o loop, devolve curva parcial + `separated_at: N`.
- `conservation_residual` volta sempre; tuner avisa se desviar (canário de bug).

---

## 5. Tratamento de erros, testes e critérios de aceite

### 5.1 Estratégia de testes (TDD — testes antes da implementação)

| Alvo | Teste | Por quê |
|---|---|---|
| **surface_damage** | `D_init=0, c_D=0` ⇒ engine reproduz **exatamente** o comportamento atual (4 perfis dentro da tolerância float) | backward-compat inegociável |
| | `D ∈ [0,1]` sempre; `dD/dN ≥ 0`; residual de energia ≈ 0 com dano ativo | física sã + canário |
| **Decomposição** | `Σ dF_0_by_mech == dF_0_total` por ciclo; shares somam ~100% por segmento | mesma soma, só contabilizada |
| **Segmentação** | partição cobre `[0,N_end]` sem buraco/overlap p/ qualquer `N_I<N_II`; MAE/segmento bate com cálculo manual | janelas ajustáveis corretas |
| **StagedCalibrator** | regressão nos 4 perfis: MAE/segmento ≤ MAE global atual **e nenhum tuner colado no bound**; determinismo; λ>0 puxa tuners pra ~1 | a prioridade física, verificável |
| | **Aceite reaperto:** TP7 fita com MAE ≤ 0.02 via `D_init`, `k_loose` **não saturado** (era 10.0 → <~3) | métrica-título do escopo |
| **Servidor** | `/simulate` == chamada in-process do engine; payload ruim → 400; `/calibrate` com tuner travado não mexe nele | fonte única comprovada |
| **Batch** | `calibrate_4_profiles.py` refatorado reproduz o JSON + PNG 2×2 | nada regride |

### 5.2 Erros em runtime

- Engine: `F_0→0` (loop corta + flag), `W_ref>0` garantido (sem divisão por zero).
- Servidor: try/except nas chamadas → 500 com traceback; validação → 400.
- Tuner: servidor offline → banner claro ("rode `python -m ...calibration.server`") em
  vez de falha silenciosa; debounce nos sliders.
- Perfis I/O: escrita atômica (temp + rename) + `encoding='utf-8'` (gotcha Windows
  charmap) pra não corromper o JSON.

### 5.3 Critérios de aceite (a barra de "pronto", ancorada em física-em-1º)

1. Para cada perfil, o MAE de **cada** segmento (I, II, III) ≤ o MAE global atual
   daquele perfil (referência: nova 0.022, reusada 0.026, sobretorque 0.007,
   reaperto 0.013). Ou seja, nenhum estágio fica pior que a média da curva inteira hoje.
2. **Nenhum tuner saturado nos bounds** em nenhum perfil (reaperto inclusive).
3. Reaperto/TP7 com MAE ≤ 0.02 via `D_init`, não via saturação.
4. Residual de energia < 0.1% em todos os runs, com dano.
5. Backward-compat: `D_init=0, c_D=0` reproduz o engine pré-mudança.
6. Fonte única: zero lógica de modelo em JS; saída do servidor == engine in-process.

---

## 6. Componentes e responsabilidades (resumo)

| Unidade | Responsabilidade | Depende de |
|---|---|---|
| `dynamic_stiffness_analyzer.py` (alterado) | física + surface_damage + decomposição/ciclo | numpy |
| `segmentation.py` | partição em janelas + MAE/segmento | — |
| `decomposition.py` | atribuição dF_0 por mecanismo + shares/segmento | snapshots do engine |
| `staged_calibrator.py` | fit sequencial com travas + regularização física | engine, segmentation, scipy |
| `profiles.py` | load/save atômico do `joint_calibrations.json` | json |
| `server.py` | HTTP local: simulate/calibrate/profiles | engine, staged_calibrator, profiles |
| `calibration_tuner.html` (refatorado) | cliente fino: sliders, travas, janelas arrastáveis, overlays | server.py |
| `calibrate_4_profiles.py` (refatorado) | batch dos 4 perfis via StagedCalibrator | staged_calibrator, profiles |

---

## 7. Notas de implementação / gotchas herdados

- `encoding='utf-8'` em todo I/O (charmap no Windows).
- Sempre `ast.parse` após editar (syntax-check do CLAUDE.md).
- Tuners default 1.0 para mecanismos novos; ajustar defaults físicos no `JointMaterial`,
  não via multiplicadores em runtime (guideline #10).
- Serializar todo campo novo em `to_dict`/`from_dict` com filtro
  `{k:v for k,v in data.items() if k in cls.__dataclass_fields__}` (backward-compat).
- `step_cycle(F_amp, theta, freq, delta_amp=None)` — disp-mode para Junker ±0.5mm.
- CSVs de referência M16: 2 colunas `cycle, F_over_F0`; normalizar se max>1.5.
