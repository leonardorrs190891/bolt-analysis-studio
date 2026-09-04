# Volume 3 — Aplicar o software

> **O que este volume é.** O manual do usuário: instalar, rodar, analisar uma
> junta nova, acrescentar um artigo novo, e regenerar tudo. Comandos **reais**,
> verificados nesta máquina. Onde há armadilha, ela está dita — inclusive quando
> a armadilha é do nosso próprio valor canônico.

---

## 1. Instalação e o interpretador certo

```bash
pip install -e ".[dev]"        # instalação editável + deps de desenvolvimento
```

**Armadilha de ambiente, medida em 2026-07-28.** Nesta máquina, `python` no PATH é
um **Python 3.13 pelado** — sem `pytest`, `numpy`, `matplotlib`, `PyQt6` nem
`scipy`. As dependências do projeto estão no **3.12**. Sintomas típicos:
`ModuleNotFoundError: No module named 'pytest'` num repo que claramente tem
testes, e o Pyright acusando `Import "matplotlib" could not be resolved` em
arquivos que rodam. Use:

```bash
py -3.12 -m pytest tests/ -q          # em vez de `python -m pytest`
py -3.12 run_app.py
```

Confira em uma linha qual interpretador tem o ambiente:

```bash
py -3.12 -c "import numpy, PyQt6, matplotlib, scipy, pytest; print('ambiente OK')"
```

---

## 2. Comandos canônicos

| o que | comando |
|---|---|
| aplicação V1 (7 abas) | `py -3.12 run_app.py` |
| aplicação V2 (chrome Abaqus, 6 módulos) | `py -3.12 run_app.py --v2` |
| só o MSD Model Builder | `py -3.12 run_app.py --builder` |
| servidor de calibração (o tuner HTML) | `py -3.12 -m bolt_analysis_studio.calibration.server` → abrir `http://localhost:8765/` |
| reports de validação (re-simula tudo, ~10 min) | `py -3.12 -m bolt_analysis_studio.validation.report --all` |
| só regerar o HTML (sem re-simular) | `py -3.12 -m bolt_analysis_studio.validation.report` |
| store em paralelo (~4× mais rápido) | `py -3.12 New_Theory/parallel_batch.py --workers 6 --store` |
| explorador de variáveis (~2–4 min) | `py -3.12 New_Theory/build_variable_explorer.py` |
| figuras deste Manual | `py -3.12 scripts/manual_figs.py` |
| gate das figuras deste Manual | `py -3.12 scripts/manual_figs.py --check` |
| suíte completa | `py -3.12 -m pytest tests/ -q --ignore=tests/test_timestep.py --ignore=tests/test_gui.py` |

> O tuner HTML (`New_Theory/calibration_tuner.html`) é **cliente magro**: ele
> POSTa para `/simulate` e não reimplementa o modelo em JS. Abrir o `.html`
> direto (`file://`) **não funciona** — precisa ser servido.

Os dois testes excluídos da suíte são breaks **pré-existentes**, não sua mudança:
`test_timestep` (caminho absoluto hardcoded → erro de coleta) e `test_gui`
(import quebrado desde o fork).

---

## 3. O fluxo completo, tela por tela

```
launch ──> wizard (5 páginas) ──> MSD Builder ──> Solver ──> Results
              │                    (PropertyInspector)         │
              └── preset de junta                              └── decomposição,
                                                                   energia, estágios
```

### 3.1 Launch

`run_app.py` sem flag abre o **V1** (7 abas); com `--v2`, o **chrome V2**
(`gui/chrome/app_window.py`) com os seis módulos do spec na `ModuleBar`:
**Model · Contacts · Loads · Analysis · Results · Report**.

### 3.2 Wizard (5 páginas)

`new_analysis_wizard.py` — do preset de junta até a revisão. Ele **prepende um
`create_ground`** no topo da cadeia; sem o GROUND a validação falha com
*"No ground element defined"*. Se você construir um modelo programaticamente, use
`build_model(AnalysisSpec())`, que devolve um modelo mínimo real (11 elementos,
GROUND incluído).

### 3.3 MSD Builder + PropertyInspector — a fonte única de verdade

Carregamento e atrito moram **aqui**, e em nenhum outro lugar. A aba Solver só
mostra um resumo somente-leitura.

```
inspector_tabs
├─ Tab 0 "Element"   — k/c/m, material, pré-carga, cargas por elemento
├─ Tab 1 "Loading"
│   ├─ "Global"      — tipo de carga, F₀, F_trans/desloc, freq, ciclos, ΔT
│   └─ "Per-Element" — lista somente-leitura, auto-construída
└─ Tab 2 "Contact"
    ├─ "Global"      — atrito (µ, lubrificação, diâmetro, passo, Sy, As, F₀)
    └─ "Per-Element" — grupos de contato/rosca/apoio/junta
```

**Onde as pessoas procuram no lugar errado:** os widgets de atrito
(`mu_initial_spin` etc.) estão em **Contact › Global**, **não** em Loading.

Regra de hierarquia do modelo, que a validação cobra:
- todo `Nut` **precisa** de um `ThreadContact` (`len(ThreadContacts) >= len(Nuts)`);
- componentes **não** carregam tribologia — ela se prende **só** aos contatos;
- atrito e desgaste contribuem **só** para `{F}`, nunca para `[K]` ou `[C]`;
- o acoplamento de hélice é o **único** acoplamento axial-torsional de `[K]`.

### 3.4 Solver

O Run **inteiro** vem de um modelo só. `SolverWorker._compute_v2_history()` roda
o `DynamicStiffnessAnalyzer` ciclo a ciclo e sobrescreve pré-carga **e** os plots
secundários (desgaste, ângulo, taxa, dano, atritos, acumulados por mecanismo) —
não é "pré-carga V2 ao lado de mecanismos V1". Limite: **100 mil ciclos**.

Duas coisas que confundem à primeira vista, ambas corretas:
- **o plot de atrito sai plano** — o atrito V2 é constante (0,15) **exceto**
  quando `surface_damage` está ativo; com dano, `mu_bearing_eff` cai conforme `D`
  cresce;
- **a conformação dependente de pressão vem LIGADA por default** (adoção de
  2026-07-04): `conform_driver="effective"`, `W_conf_ref=7671`, e
  `p_ref_conform` computado do `preload_percent_yield` do config, o que faz a
  comporta depender de `pct/70`. Overrides explícitos em `_v2_tuner_overrides`
  **vencem**; `W_conf_ref=0` desliga.
  > **Caveat de escala, medido:** o `W_conf_ref` é um valor **por par**, calibrado
  > na escala da âncora interna (F₀ ~50 kN ⇒ Δratio ~0,014). Em F₀ alto o trabalho de slip
  > (∝ F₀) enche o `W_conf_ref` fixo e a comporta morde também no nominal
  > (F₀ = 120 kN ⇒ Δ ~0,09). Aproximado fora do par da âncora interna.

### 3.5 Results (módulo V2) — o browser dos casos

Navega os **203** casos do store, re-simula, e tem **"Abrir no Model/Run"** — que
anexa tanto `_v2_tuner_overrides` quanto `_v2_geometry_overrides`. A fidelidade
Run-vs-report está medida: **Δmáx 1,6e-4**.

**Como ler o resultado** (a ordem que evita conclusão errada):

1. **A curva e o erro** — e cuidado com uma sutileza que já produziu quatro
   números discordantes na mesma página: a métrica **não** compara a curva crua.
   Ela **alinha** (divide o modelo pelo próprio valor no 1º ciclo do dado) e
   **trima** (só pontua `N <= trim_n_max`). Os vetores que a métrica realmente
   comparou estão em `metric_x`/`metric_pred`/`metric_data`; **todo consumidor lê
   daí, ninguém reinterpola.**
2. **Os estágios** — patamar / joelho / piso (figura 1 do [Vol. 2](02-explicar-o-modelo.md)).
3. **A decomposição por mecanismo** — as quatro parcelas somam **exatamente**
   `F0·(1−ratio)`. Se um mecanismo domina, é ali que a procedência precisa ser boa.
4. **A energia** — residual de conservação ≈ 0. Se degradou, você está no regime
   de colapso por dano (limitação declarada, [Vol. 1 §6.3](01-entender-o-modelo.md#63-o-que-ainda-não-fecha-medido)).

---

## 4. Analisar uma JUNTA NOVA, passo a passo

### 4.1 Inputs mínimos, e de onde tirar cada um

| input | de onde vem | como obter |
|---|---|---|
| geometria (M, passo, aperto) | do desenho | bases em `core/databases/*.json` |
| `F_0` | do torque de montagem ou medição | se estimado, **marque a procedência** |
| modo de carregamento | do ensaio | deslocamento imposto → passe `delta_amp`; servo-hidráulico → modo força |
| `emb_depth` | **VDI 2230**, tabela f_Z por classe de rugosidade | `library_common.emb_depth_vdi(Rz)` — é **input**, nunca botão de ajuste |
| `mu` | banda medida 0,14–0,19 | default 0,15; fora da banda, o KB avisa |
| preset da bancada | se sua junta se parece com uma fonte já adotada | `kb.suggest_overrides("<FONTE>")` |
| `C_creep` | **por par tribológico** | KB: âncora interna 1,867e-11 · Liu2017 1,45e-11 · 304SS 9,9e-13 |

```python
from bolt_analysis_studio.calibration import knowledge_base as kb

kb.adopted_sources()            # 68 grupos com config validada
kb.suggest_overrides("LIU_2025")  # dict pronto p/ _v2_tuner_overrides
kb.anchor_priors()              # bandas medidas + fonte + veredicto
kb.frozen_params()              # os 4 congelados, com o motivo
kb.lessons()                    # 26 lições L# das campanhas
```

### 4.2 O que os avisos do `check_input` significam

```python
kb.check_input("mu_bearing", 0.35)
# 'mu_bearing=0.35 fora da banda MEDIDA [0.14, 0.19]
#  (qiao2025 (25pts) + lu2024 K-factor, verdict PASSA)'
```

`None` = dentro da banda **ou sem âncora**. Mensagem = fora da banda, **citando a
fonte**. O aviso **nunca bloqueia** — ele obriga a declarar por que você saiu.

**Duas armadilhas reais, verificadas — a primeira já consertada:**

1. **`None` é ambíguo: use `checkable_inputs()`.** A guarda aceita as duas formas
   de nome — o **campo do engine** (`mu_bearing`) e o **prior** (`mu_dry`). Até
   2026-07-28 só a primeira funcionava, e `check_input("mu_dry", 0.35)` devolvia
   `None` **em silêncio** com 0,35 fora da banda [0,14; 0,19]. Consertado. O que
   **permanece** por contrato é a ambiguidade do `None`: ele significa "dentro da
   banda" **ou** "não sei checar isso". Para separar os dois:

   ```python
   if nome in kb.checkable_inputs():
       aviso = kb.check_input(nome, valor)      # None aqui = de fato dentro
   else:
       aviso = None                             # ninguém checou; não finja que sim
   ```

   Checáveis hoje: `mu_dry`/`mu_thread`/`mu_bearing`, `conform_pressure_exp`,
   `fat_sigma_endurance`, `F_amp_ratio` e `k_wear_spec`. Sem guarda: `emb_depth`
   (é **input** de tabela por junta, e por decisão), `N_emb` e `C_creep_por_par`
   — estes dois **têm** procedência medida (faixa per-rig lida e âncora por par),
   só não têm guarda automática. "Não checável" ≠ "sem procedência": a matriz
   completa está em
   [`provenance_matrix.md`](../../New_Theory/provenance_matrix.md).
2. **O nosso próprio valor canônico dispara o aviso — e o motivo é mais preciso
   que o registrado antes.** `k_wear_spec = 5e-14` (bloco `shared`) está fora de
   todas as bandas medidas R5, mas **não** "130× abaixo da única banda". Medido:
   a R5 tem **3** bandas, e só **2 são comparáveis** (a terceira,
   `fretting|52100-52100`, está em `norm-own`, não em `1/Pa` — compará-la é erro
   de unidade). As duas comparáveis **cercam o canônico pelos dois lados**:

   | banda (1/Pa) | intervalo | canônico 5e-14 |
   |---|---|---|
   | `thread\|35CrMo-SCM435` (Zhang 2019) | [4e-15, **2e-14**] | **2,5× acima do teto** |
   | `faying\|Q355B-Q235B` (Li 2025) | [**6,49e-12**, 7e-12] | 130× abaixo do piso |

   As duas distam ~325× entre si, e o engine usa `k_wear_spec` nos **dois**
   canais (`WearLoss` no apoio, `ThreadFrettingLoss` na rosca) — então **nenhum
   valor único pode estar dentro das duas**. Isso **não é bug**: é a limitação
   **L6** (não-universalidade de `K/H` por par) em números exatos, e é argumento
   para **separar a constante por interface**. Se você calibrar desgaste com
   pares **casados**, use a banda da interface que domina; se usar o canônico,
   saiba que ele é o valor do par da âncora interna e que o aviso cita a banda mais
   **distante** das duas.

### 4.3 Como julgar o resultado

A meta é o **tripé por curva**: `MAE < 0,10` **E** `res.máx < 0,10` **E** σ_res
mínimo. Passar só no MAE não conta — e não é teoria: **0** das 55 curvas fora do
tripé falham só pelo MAE, **34** falham só pelo pico.

---

## 5. Acrescentar um PAPER NOVO, fim a fim

### Passo 1 — digitalizar as curvas

CSV em `Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/`
(tabelas de artigo vão em `extracted_csv/`). Duas colunas (`cycle, F_over_F0`) ou
header `x`.

> **`*.csv` é gitignored GLOBAL.** Precisa `git add -f`; `git add <dir>` **pula
> ignorados em silêncio** e produz commit "vazio" sem aviso. Confira com
> `git ls-files`.

Convenções de eixo que **todo** consumidor do CSV cru deve aplicar —
`(x − offset)·scale`, com clamp ≥ 0:
- `csv_x_scale` — eixo em segundos → ciclos (eccles: ×12,5);
- `csv_x_offset` — âncora pré-ciclagem plotada em x=1 (Lu, Karlsen; eixo log);
- casos de **creep** têm eixo x em **minutos** ⇒ `freq = 1/60 Hz`.

### Passo 2 — escrever a `apparatus_note`

Em `curve_library/apparatus_notes/<fonte>.md`: aparato, corpo-de-prova, matriz de
ensaios, caveats de digitalização e o mapeamento para as variáveis V2. Comece
olhando `MSD_BLOCK_COVERAGE.md`. **Sem a nota, o caso não é interpretável depois.**

### Passo 3 — registrar o caso

Em `validation/validation_cases.py`. Os `DIGITIZED_CASES` são construídos **em
import-time lendo os CSVs** (n_ciclos, razão final e pontos vêm do arquivo). Marque:
- carregamento **axial/força** vs **transversal/deslocamento** (amplitude
  transversal 0 ⇒ modo força, **não** `delta_amp`);
- `trim_n_max` onde o fim da curva sai do modelo (fratura por fadiga, p. ex.).

### Passo 4 — simular e medir

```bash
py -3.12 New_Theory/parallel_batch.py --sources MINHA_FONTE --workers 6 --store
py -3.12 -m bolt_analysis_studio.validation.report        # só o HTML
```

### Passo 5 — fit gateado

O gate de passo (PR-37′) exige **três** coisas juntas: procedência das constantes
**+ nenhum caso pior (+0,01) + mediana da fonte −30 % ou ≤ 0,05**. O tripé por
curva é o **objetivo do acompanhamento**, não o gate de cada passo.

Antes de girar qualquer lever: **olhe a decomposição**. Amplificar um canal que
responde por 1 % da perda não move nada — a lição custou uma varredura inteira no
Lu 2024 (`k_wear_running` até 20× com a fração cravada em 28 %, porque o caso é
embedding 54 % + afrouxamento 43 % + creep 2 % + **desgaste 1 %**).

### Passo 6 — adoção

Escreva em `New_Theory/adopted_configs.json`. Armadilhas do formato, todas com
precedente:
- `per_case` `{token: {campo: valor}}` são inputs **por curva**; tokens casam por
  **substring** do `case_id` — `"grease"` casa `"nogrease"`;
- chaves `FONTE_token` splitam por `_`; prefixo mais longo vence, mais tokens
  desempata. **Nunca crie chave que EMPATA em score:**
  `YANG_2019_small_to_large` e `YANG_2019_large_to_small` são **permutações** dos
  mesmos tokens, empataram, e o alfabeticamente primeiro venceu **sempre** — a
  outra virou config morta e o caso rodou com o espectro da direção oposta, **em
  silêncio, passando pelo gate**. Invariante fixada em
  `tests/test_yang2019_varamp_spectrum.py`, que varre o registry inteiro
  procurando empates;
- **desligar desgaste transversal** exige `k_wear_spec=0` **E** `K_archard=0` (só
  `k_wear_spec=0` cai na via **legada** K/H, que não é "sem desgaste");
- excluir um caso = **sem** entry de grupo; um `per_case` "neutro" **não** restaura
  o default;
- listas e dicts (`delta_spectrum`, `d_hole_mm`, `GA_member`, `trim_n_max` como
  dict) **morrem** no `suggest_overrides` — leia do cru.

### Passo 7 — publicar

```bash
py -3.12 -m bolt_analysis_studio.validation.report --all   # store + HTML
py -3.12 New_Theory/build_variable_explorer.py             # explorador + galeria + estudo por fonte
py -3.12 scripts/manual_figs.py                            # figuras deste Manual
py -3.12 scripts/manual_figs.py --check                    # gate: figuras == script + store
```

---

## 6. Reprodutibilidade — regenerar tudo

Ordem que respeita as dependências (cada etapa consome a anterior):

```bash
# 1. store canônico (a fonte de todo número publicado)
py -3.12 New_Theory/parallel_batch.py --workers 6 --store
# 2. reports HTML (mestre + por caso)
py -3.12 -m bolt_analysis_studio.validation.report
# 3. explorador (82 variáveis + 14 conceitos + 28 estudos + galeria + 203 reports)
py -3.12 New_Theory/build_variable_explorer.py
# 4. figuras do Manual + numbers.json
py -3.12 scripts/manual_figs.py
# 5. gate: prova que as figuras SÃO o que o script + o store produzem
py -3.12 scripts/manual_figs.py --check
```

**O gate do passo 5 compara bytes**, e isso só é possível porque a saída é
determinística: `_salva` passa `metadata={"Date": None}` (senão o matplotlib
estampa a data de criação dentro do SVG) **e** escreve com `newline="\n"`
explícito (senão o Windows grava CRLF, o `.gitattributes` guarda LF, e o gate
acusaria 11 de 11 artefatos em qualquer clone novo).

**O `engine_fingerprint` hasheia o bloco `shared` + as configs adotadas — não o
código.** Adotar config muda o fingerprint **legitimamente**; re-simular
re-carimba o store por inteiro. Um store com mais de um fingerprint é um store
remendado, e seus números vêm de gerações mistas de config.

---

## 7. Troubleshooting — armadilhas reais

### Encoding e console (Windows)

- **Sempre `encoding='utf-8'`** em toda I/O de arquivo, ou você colhe
  `charmap codec` errors.
- Prints com `µ`, `±`, `→` quebram o **console** (cp1252). Em scripts, print ASCII.
- Prosa com **crases** nunca via string bash — *command substitution executa*.
  Use o editor.

### Git neste repositório

- Duas sessões no mesmo branch = **corrida de índice** (commits perdidos, medido).
  Um executor por branch; WIP alheio: **staging explícito**, nunca varrer.
- O repo é sincronizado por **OneDrive**: espere arquivos/commits de outra sessão
  aparecendo no meio da tarefa e `fatal: unable to write new index file`
  intermitente. Confira `git log`/`git status` nos marcos; **nunca reverta o que
  você não escreveu**.
- `git status` pode marcar como modificado um arquivo **byte-idêntico** ao HEAD: o
  índice guarda `size`+`mtime`, e com filtro de fim-de-linha o atalho de stat
  erra. `git diff` vazio + hashes iguais = limpo; um `git add` refresca o stat.

### Qt / GUI

- **NUNCA `__new__` numa subclasse de `QObject`** (PyQt6 6.11.0): um `__new__` que
  devolve instância pré-existente **recursiona no nível C e mata o processo**
  (`STATUS_STACK_OVERFLOW`), sem traceback útil. Isso derrubou a GUI **inteira** e
  ficou meses registrado como "1 teste isolado que crasha". Padrão correto: cache
  no getter. Invariantes em `tests/test_app_state_singleton.py`.
- Testes headless usam `QT_QPA_PLATFORM=offscreen` via `tests/conftest.py`. Use
  `widget.isVisibleTo(ancestor)`, **não** `isVisible()` — nada é mostrado offscreen.
- `MSDBuilderWindow.load_from_msd_model` **trava** com modelo falso/malformado —
  proteja reuso programático com `isinstance(model, MSDModel)`.
- `pytest … | tail` **esconde travamentos** (buffer de pipe): escreva num arquivo
  ou use `-v`/`--durations`. Mate um run travado com `taskkill //PID <pid> //F`.

### Dados e store

- **Dicts que vão para o `validation_store.json` só aceitam tipos nativos** —
  `float()`/`bool()` antes de gravar (`np.float64` quebra o `json.dump` no meio do
  batch).
- **Nunca escreva no store canônico em teste ou script.** Passe
  `ValidationStore(path=...)`. O invariante que pega isso está em
  `tests/test_validation_store.py`: o store versionado só pode conter ids que o
  registry conhece — e ele existe porque o vazamento era **invisível** (o registro
  de um caso real sai byte-idêntico, nem o md5 acusa).
- **Os 3 CSVs âncora interna não são versionados.** Clone novo vê **199** casos comparáveis,
  não 202.
- **Registros antigos do store não têm `metric_x`/`metric_pred`/`metric_data`** —
  o report cai no fallback cru. **Re-simule** (`parallel_batch.py --store`).

### Modelo

- `step_cycle(F_amp, theta_load, freq, delta_amp=None)` — com `delta_amp`, o slip
  vem do **deslocamento imposto**; sem ele, da elasticidade local. Junker = passe
  `delta_amp`.
- `WearLoss` é **inerte em modo axial-força**; `fret_freq_exp` é inerte se o canal
  de fretting ≈ 0 no bloco per-rig.
- Sondando o engine: **verifique a direção da monotonicidade com 2 pontos antes de
  qualquer bissecção** (esse bug apareceu 2× numa campanha), e não ancore perto do
  piso — âncora junto ao arresto é **degenerada**.
- Um **leitor de procedência tem domínio declarado**. `emb_depth_from_curve` é
  método **axial**; no transversal a queda inicial é dominada por
  afrouxamento/creep e a leitura mis-atribuiria. *Aplicar um leitor fora do
  domínio não é leitura, é fit com etiqueta.*

---

## 8. Onde ir depois

| quero… | vá para |
|---|---|
| a física e a proveniência | [Vol. 1 — Entender](01-entender-o-modelo.md) |
| explicar a um terceiro | [Vol. 2 — Explicar](02-explicar-o-modelo.md) |
| navegar os 203 casos | [concept_gallery.html](../../New_Theory/variable_explorer/concept_gallery.html) |
| uma variável específica (82 páginas) | [explorador](../../New_Theory/variable_explorer/index.html) |
| o guia de uso interativo | [concept_usage.html](../../New_Theory/variable_explorer/concept_usage.html) |
| as decisões abertas | [`DECISOES_PENDENTES.md`](../../New_Theory/DECISOES_PENDENTES.md) |
