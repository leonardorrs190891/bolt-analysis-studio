# Explorador Interativo de Variáveis — Design

**Data:** 2026-07-12 · **Pedido (professor, verbatim):** "quero na documentação
um documento interativo com uma curva padrão, as variáveis que usamos e um slider
onde posso mudar o valor da variável e ver sua influência na curva. uma página por
variável contendo inclusive referências de literatura"

## 0. Objetivo

Um documento didático interativo: para **cada variável** do modelo V2
(`JointMaterial`), uma página com a **curva-padrão** de afrouxamento (F/F₀ vs
ciclo), um **slider** que muda o valor da variável e **reforma a curva ao vivo**,
o **texto de física**, a **equação** governante e as **referências de literatura**.
Público: laboratório UFU + leitores externos. Complementa (não substitui) o
inventário estático `New_Theory/validation_html/variables.html` e o tuner
server-backed `New_Theory/calibration_tuner.html`.

## 1. Decisões (confirmadas com o professor)

| Eixo | Decisão |
|---|---|
| Escopo | **Todos os 80 campos** de `JointMaterial` (contagem real; a estimativa inicial de "~40" estava errada) |
| Geração das curvas | **Estático, pré-computado pelo engine real** (`handle_simulate`) — nenhuma física em JS |
| Layout | **Um arquivo HTML por campo** (80 páginas) + um `index.html` |
| Campos-companheiro | Campos que só dão forma a um primário (`p_ref_conform`, `*_sharpness`, expoentes, as 8 const. da S-N) **têm sua própria página**, num contexto onde o primário está ativo, com **cross-link** ("só age quando [[primário]] > 0") |
| Referências | **Auto do sistema de proveniência** (`knowledge_base`) **+ curadoria** |
| Auto-contido | **Cada arquivo 100% standalone** — CSS+JS+dados inline (fonte única no gerador) |
| Idioma | **Bilíngue PT/EN** com toggle (localStorage, como o toggle de tema) |

## 2. Princípio arquitetural

**Engine real = fonte única.** O gerador Python reusa `calibration.server.handle_simulate`
(função pura, sem sockets — a mesma que alimenta o tuner e a galeria de validação).
Nada da física é reimplementado em JS (proibido por CLAUDE.md). O JS só desenha
curvas já calculadas e embutidas como JSON.

**Zero dependência externa.** Alinha com a convenção de casa (report v3,
`2026-07-10-report-v3-interactive-design.md`): renderer de gráfico próprio inline
(~150–250 linhas), dados embutidos, funciona em `file://` e impresso, sem CDN.

## 3. O problema central — sliders vivos

Dos ~40 campos, **a maioria não move a curva no baseline nova** porque:

- **(a) default `0`/`OFF`, ativa só com companheiro:** `k_dmg_mu`/`k_dmg_wear`
  precisam de `c_D>0`; `eta_loose` só em `loose_torsion_mode="bolt_torsion"`
  (+ `loosening_slip_coupling="gross_fraction"` + `k_tr_mode="bending"`);
  `p_ref_emb` só se `emb_conform_exp>0`; `rho_ref_emb` só se `emb_amp_exp>0`;
  `fret_freq_exp`/`f_ref_fret` precisam de `k_thread_fret>0`; `slip_onset_sharpness`
  só se `slip_onset_W>0`; `crash_trigger_sharpness` só se `crash_trigger_frac>0`;
  `N_wear_run` só se `k_wear_running>1`; `dmg_onset_sharpness` só se `W_crit>0`.
- **(b) regime de carga específico:** `k_thread_fret`, `fret_freq_exp`, `f_ref_fret`
  e a componente axial de `emb_amp_exp`/`rho_ref_emb` só valem no modo **axial**;
  `creep_conform_exp` no canal **lento**; `member_loss_eta`/`k_member_shear` em
  membro **complacente** (polímero).

**Solução — contexto de demonstração por variável.** Cada variável declara na
tabela `VARIABLE_SPECS` um **baseline de carga** + os **overrides-companheiros
mínimos** que a deixam viva, de modo que o slider **visivelmente** reforme a curva.

*Alternativa rejeitada:* baseline fixo único → metade dos sliders morta (documento
enganoso).

**Honestidade sobre influência nula.** Onde o efeito for genuinamente desprezível
na curva quase-estática (ex.: `m_x`, `m_y`, `I_theta`, `rayleigh_alpha`,
`rayleigh_beta`), a página **diz isso** ("parâmetro de solver/inércia — efeito
negligível no afrouxamento") em vez de fingir efeito. Combina com a cultura de
falsificação do projeto. Essas variáveis recebem `negligible=True` (isenta do teste
de slider-vivo).

## 4. Baselines (curva-padrão)

Três contextos de carga, puxados **verbatim** de casos canônicos existentes (não
inventar números):

1. **`transverse`** — UFU nova M16 shear ±0.5 mm 0.5 Hz, disp-mode
   (`F0_init`, `delta_amp`, `freq`, `theta`, `F_amp`, `N`, `D_init` copiados do
   `ValidationCase` nova / default do tuner). **É a curva-padrão principal** — a
   maioria das variáveis usa este contexto.
2. **`axial`** — Liu2017 (modo força, `delta_amp=0`), para as variáveis de fretting
   axial e componente axial de settling.
3. **`creep`** — Li2022 (eixo em minutos, `freq=1/60`), para `C_creep`/`t_0` e o
   canal lento.

Material baseline = `default_v2_params()` (constantes físicas canônicas). Geom =
M16 da `library_common`.

## 5. Gerador — `New_Theory/build_variable_explorer.py`

Fluxo:

1. Importa `handle_simulate`, `JointMaterial`, `knowledge_base`
   (`anchor_priors`, `lessons`, `check_input`), `default_v2_params`, e o helper de
   geometria M16.
2. Define os 3 baselines (§4) como dicts de payload.
3. Define **`VARIABLE_SPECS`** — lista, uma entrada por campo documentado:
   ```
   VarSpec(
     name,                 # campo do JointMaterial (validado contra __dataclass_fields__)
     symbol, unit, group,  # ex.: "δ_∞", "m", "embedding"
     category,             # "physical" | "form" | "numerical" | "mode"
     sweep,                # (lo, hi, n, scale='lin'|'log')  OU  choices=[...] p/ modes
     context,              # baseline-id + overrides-companheiros ({} p/ os que já são vivos)
     physics_pt, physics_en,   # 1-2 parágrafos cada
     equation,             # string (MODEL_MATH_REFERENCE)
     anchor_key,           # chave em anchor_priors() (ou None)
     lessons,              # ["L20", ...] do ledger
     refs,                 # citações curadas [(cita_pt, cita_en, papel/arquivo)]
     related=[],           # nomes de campos p/ cross-link (companheiro -> primário)
     negligible=False,
   )
   ```
   Toda `name` validada contra `JointMaterial.__dataclass_fields__` no import
   (erro alto se divergir — disciplina do projeto). Campos-enum (`k_tr_mode`,
   `loosening_slip_coupling`, `loose_torsion_mode`, `conform_driver`) usam
   `choices` em vez de `sweep` → seletor discreto, uma curva por opção.
4. Para cada spec: monta o payload do contexto, varre a variável na grade (~15–20
   pontos, ou as `choices`), chama `handle_simulate` por valor → coleta
   `[{value, N[], ratio[]}]` + a curva-default destacada + métricas (F₀ final,
   ciclo de separação se houver).
5. Renderiza cada `var_<name>.html` do template (CSS+JS+dados inline) e o
   `index.html`.

Saída: **`New_Theory/variable_explorer/`** = `index.html` + `var_<name>.html`
(×80). Runtime estimado 80 vars × ~18 sims × ~2500 ciclos ≈ 1–2 min (one-shot).

Campos-companheiro (ex.: `p_ref_conform`) recebem no `context` os overrides que
ligam o primário (ex.: `W_conf_ref>0`, `conform_driver="effective"`) para que o
slider mova a curva, e uma entrada `related=["W_conf_ref"]` que vira cross-link.

## 6. Página de variável (`var_<name>.html`) — conteúdo

- **Cabeçalho:** nome do campo, símbolo, unidade, grupo, categoria, valor default,
  faixa do slider. Toggle PT/EN + toggle tema (claro/escuro, localStorage).
- **Gráfico + controle:** plotter canvas vanilla inline — eixos (ciclo × F/F₀),
  grade, a **curva do valor atual** (destaque), a **curva-default** (linha de
  referência), e "fantasmas" translúcidos de todas as varreduras ao fundo.
  Slider (contínuo, faz snap na grade pré-computada) **ou** seletor de opções
  (modes). Leitura ao vivo do valor + F₀ final. Aviso de proveniência via
  `check_input` quando o valor sai da banda medida.
- **Física** (PT/EN): o que é, o que faz mecanicamente, o que o slider mostra.
- **Equação** governante.
- **Referências:** banda medida + fonte + verdict da âncora (quando houver, de
  `anchor_priors`), L# do ledger (`lessons`), citações de papers curadas
  (`apparatus_notes/`, specs, `BAS_V2_papers/`).
- **Navegação:** ⟵ índice · ⟶ próxima variável.

## 7. Índice (`index.html`)

Lista agrupada por mecanismo (embedding, creep, wear, loosening, damage, friction,
conformation, fretting, numérico), cada variável com gancho de uma linha + sua
categoria (constante física / forma opt-in / numérico / modo). Descreve a
curva-padrão compartilhada e os 3 baselines. Toggle PT/EN + tema.

## 8. Testes — `tests/test_variable_explorer.py`

- **registry-truth:** toda `name` em `VARIABLE_SPECS` ∈ `JointMaterial.__dataclass_fields__`.
- **cobertura:** **todos os 80 campos** de `JointMaterial` aparecem em
  `VARIABLE_SPECS`, sem exceção (o teste falha se faltar qualquer um).
- **slider-vivo:** para cada variável não-`negligible`, as curvas varridas **não**
  são todas idênticas (pega regressão de "slider morto"). As `negligible=True` são
  isentas mas devem *de fato* ser ~planas (teste inverso opcional).
- **integração:** `handle_simulate` no contexto de cada variável retorna curva com
  `ratio[0]==1.0` e `ratio` finito ≤ 1 (monotonia não exigida — colapsos existem).
- **smoke de render:** gerador roda num subconjunto (2–3 vars) e emite HTML
  parseável (html.parser sem erro; contém o JSON de dados e o `<canvas>`).

## 9. Entregáveis

- `New_Theory/build_variable_explorer.py` (gerador + `VARIABLE_SPECS`)
- `New_Theory/variable_explorer/` (`index.html` + `var_*.html`)
- `tests/test_variable_explorer.py`
- Entrada na tabela de docs do `CLAUDE.md` (comando de geração + propósito)

## 10. Fora de escopo (YAGNI)

- Sem servidor/ao-vivo (é doc estático).
- Sem edição de múltiplas variáveis simultâneas (uma por página).
- Sem persistência de estado além dos toggles de idioma/tema.
- Sem re-fit/calibração (só demonstração de influência).
