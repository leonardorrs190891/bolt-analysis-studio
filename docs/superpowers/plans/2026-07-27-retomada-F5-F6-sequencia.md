# Sequência de retomada — F5 (certificação) → F6 (Manual)

> Escrita em 2026-07-27 a partir de uma AUDITORIA do estado real (sem executar
> nada: esta sessão não tinha Python nem git no PATH). Continua a execução do
> `docs/superpowers/plans/2026-07-17-PROMPT-MESTRE-execucao-unica.md`, cujo
> ledger é `.superpowers/master-0p1-progress.md` (última linha: 2026-07-22 22:24).
>
> **Nada aqui foi rodado.** O único conserto já aplicado é o S1 (bug YANG_2019),
> descrito abaixo — e ele ainda precisa da validação executável do passo S1.

---

## 0. Estado de partida (medido em 2026-07-27, não estimado)

**Onde parou:** F5 ABERTA — a certificação foi disparada (suíte + HTML mestre
regenerados em 22:36/22:46 de 07-22) e a execução parou no ⛔ PARE de assinatura
da lista de exceções (`New_Theory/f5_excecoes_propostas.md`). F6 nunca começou.

**Censo vigente** (`New_Theory/l1l7_baseline.json`, commit `6960a26`):

| | valor |
|---|---|
| casos comparáveis | 202 |
| **no tripé (MAE<0,1 E maxerr<0,1)** | **147 (73%)** |
| fora do tripé | **55** (21 por MAE, 55 por maxerr) |
| mediana MAE / média | 0,0315 / 0,0446 |

Violadores por fonte (16 fontes; as outras 12 fecham 100%):

| Fonte | n | fora | Fonte | n | fora |
|---|--:|--:|---|--:|--:|
| LU_2024 | 10 | 10 | YANG_2021 | 6 | 2 |
| BAUER_2024 | 9 | 7 | JCSR_2023 | 5 | 2 |
| CHU_2026 | 9 | 7 | ANCORA_INTERNA | 3 | 2 |
| YANG_2023_IJPEM | 9 | 7 | KARLSEN_2022 | 11 | 1 |
| ECCLES_2010 | 10 | 5 | LIU_2016 | 14 | 1 |
| YANG_2019 | 5 | 4 | LIU_2020_WEAR | 9 | 1 |
| ROUSSEAU_2025 | 6 | 3 | SUN_2025_CRIMP | 8 | 1 |
| | | | ZHANG_2006 / YANG_2023_AME | 2 / 1 | 1 / 1 |

**Achados de auditoria que viram trabalho aqui:**

1. **[CONSERTADO, falta validar]** `YANG_2019_small_to_large` era config morta
   por EMPATE de score — ver S1.
2. **[ABERTO]** Store canônico poluído: `ensaio_teste_m12` gravado pela própria
   suíte (`test_user_cases`) às 22:35:59. Store tem 204 registros, o censo conta
   202, o report mestre mostra 203. Registrado como "follow-up" na F0.3 e nunca
   corrigido — ver S2.
3. **[ABERTO]** Store **não re-carimbado**: 12 fingerprints distintos (145 em
   `a8f3d1cace1a` da F1; apenas 1 no corrente `c96caafff8ac`). O `report --all`
   final da F5.1 nunca rodou ⇒ os números da certificação vêm de gerações
   mistas de config — ver S3.
4. **[ABERTO]** Docs vivos desatualizados (F5.2 nunca executada): explorador diz
   **115 curvas**, tem **181 reports para 202 casos** (faltam os 22 R5) e
   **15 páginas `study_*` para 28 fontes** — 13 artigos sem página (Zhang2018,
   Zhang2019, Liu2020_wear, Chu2026, Eccles2010, JCSR2023, Caccese2009,
   Grzejda2026, Liu2016, Qin2024, Sun2025 ×2, Yang2023_AME) — ver S5.
5. **[ABERTO]** F6 não existe: sem `docs/MANUAL_BAS_V2/`, sem `manual.html`,
   sem `scripts/manual_figs.py` — ver S6.
6. **[LATENTE, baixo]** `calibration/server.py:61` faz `float(v)` em todo campo
   não-str ⇒ payload com `mu_bearing_schedule`/`delta_spectrum` (tupla/lista)
   levanta `TypeError`. Só pela via do tuner HTML.

**Meta ("o erro escolhido"):** tripé POR CURVA — `MAE < 0,1` **E**
`maxerr < 0,1`, com σ_res mínimo. A meta da F5 é *100% das comparáveis no tripé,
exceto a lista de exceções assinada*.

---

## Pré-condições (verificar antes de escrever qualquer coisa)

1. **Escritor único.** Nenhuma outra sessão/campanha no mesmo worktree — a
   violação de quiescência já custou um PARE nesta execução (F4, 07-22).
2. **Toolchain no PATH:** `git --version` e `python --version` têm de responder.
   *(Na sessão de auditoria de 07-27 nenhum dos dois existia no shell — sem isso
   nada abaixo roda.)*
3. **Backup do store** antes do primeiro passo que escreve:
   `Copy-Item Models\CALIBRATION_AND_VALIDATION\validation_store.json <backup>`.
4. Staging **por arquivo explícito** (OneDrive + sessões paralelas). Nunca
   `git add -A`.
5. Ledger: **uma linha por passo concluído** em `.superpowers/master-0p1-progress.md`,
   com números. Ao retomar, ler o ledger e continuar do primeiro passo incompleto.

---

## S1 — Validar o conserto do YANG_2019 *(código já aplicado, execução pendente)*

**O bug.** `_adopted_for` (`src/bolt_analysis_studio/validation/runner.py:139`)
pontua `pref*10 + len(extra)` e casa tokens de grupo por **substring** do
case_id. As chaves `YANG_2019_small_to_large` e `YANG_2019_large_to_small` têm
tokens que são permutações um do outro — `{small, to, large}` casa nos **dois**
case_ids ⇒ mesmo `pref`, mesmo `len(extra)`, **empate**. Como
`kb.adopted_sources()` é `sorted()` (`knowledge_base.py:75`) e o teste é `>`
estrito, `large_to_small` vencia **ambos** e `small_to_large` ficava
INALCANÇÁVEL. Efeito físico: o caso small→large rodava com o espectro da outra
direção — **51,4% dos ciclos em 0,8 mm em vez de 97,8% em 0,6 mm**.
É exatamente a armadilha registrada no CLAUDE.md ("NUNCA criar chave que EMPATA
em score"), agora com precedente real.

**O conserto (já no disco).** `New_Theory/adopted_configs.json`: as duas chaves
foram fundidas em **`YANG_2019_varamp`**, com os espectros movidos para
`per_case` — cujos tokens casam por **substring pura, sem split em `_`**
(`runner.py:181`), então discriminam sem empate. Tokens usados:
`varamp_small_to_large` / `varamp_large_to_small`. As constantes fitadas foram
preservadas bit-a-bit (as duas cfg antigas só diferiam no `delta_spectrum`).
Teste novo: `tests/test_yang2019_varamp_spectrum.py`.

**Verificação estática já feita** (reproduzindo a aritmética do runner):
empates nos 202 casos **2 → 0**; resolução alterada em **exatamente 2 casos**;
`large_to_small` recebe config **idêntica** à de antes ⇒ deve sair
**bit-idêntico** (é o controle negativo); só `small_to_large` muda.

**Executar:**

```bash
python -c "import ast; ast.parse(open('tests/test_yang2019_varamp_spectrum.py', encoding='utf-8').read()); print('OK')"
python -m pytest tests/test_yang2019_varamp_spectrum.py -q          # 7 testes
python -m bolt_analysis_studio.validation.report --case yang2019_M10_varamp_large_to_small
python -m bolt_analysis_studio.validation.report --case yang2019_M10_varamp_small_to_large
```

**GATE S1** (os três, escritos antes de rodar):
- (a) **Controle negativo:** `..._large_to_small` sai **bit-idêntico** ao store
  atual (mae 0,0519 / maxerr 0,1364). Se mudar, o conserto tem efeito colateral
  não previsto → **PARE**.
- (b) `..._small_to_large` muda (se não mudar, o `per_case` não está chegando ao
  `delta_spectrum` — depurar `_adopted_overrides`, não "aceitar").
- (c) **Nenhum caso piora mais de +0,01.** Atenção honesta: o gate do PR-42
  ("maxerr 0,212→0,131 / 0,164→0,136") foi medido **com o bug**, então a melhora
  creditada à direção small→large pode encolher ou sumir. Se piorar, isso **não
  é regressão do conserto** — é o número verdadeiro aparecendo. Registrar no
  ledger e no `verdict` da chave; o caso continua na lista de violadores.

Ledger + commit (`New_Theory/adopted_configs.json`,
`tests/test_yang2019_varamp_spectrum.py`, store dos 2 casos).

---

## S2 — Higiene do store: parar a poluição pela suíte

`tests/test_user_cases.py` roda o fluxo de caso de usuário em subprocesso e o
registro `ensaio_teste_m12` acaba **gravado no store canônico**. Consequências:
204 registros num arquivo que deveria ter 202(+1 exemplo), e censos que leem o
store "as is" contam errado.

**Executar:**
1. Isolar a escrita do teste (idioma já existente no repo: sandbox por variável
   de ambiente, como o `BAS_ADOPTED_CONFIGS` de `tests/test_f3_trim.py` — ver se
   há env equivalente para o caminho do store; se não houver, criar um).
2. Remover o registro órfão `ensaio_teste_m12` do store.
3. Decidir explicitamente o que fazer com `exemplo_m12_sintetico` (hoje entra no
   report mestre = 203, mas fica fora do censo = 202). Documentar a escolha.

**GATE S2:** rodar a suíte-alvo **duas vezes seguidas** e o store ficar
**byte-idêntico** (hash MD5 igual) nas duas.

---

## S3 — Re-simulação canônica e re-carimbo uniforme *(fecha a F5.1 de verdade)*

Hoje o store é um mosaico: 12 fingerprints, porque cada adoção da F3/F4
re-rodou só a fonte afetada. O plano-mestre exige `report --all` +
`error_budget` **finais**.

**Executar:**
```bash
python New_Theory/parallel_batch.py --workers 6 --store     # ~4x mais rápido que report --all
python -m bolt_analysis_studio.validation.report            # só o HTML, sem re-simular
python -m bolt_analysis_studio.validation.error_budget      # censo cru
python scripts/l1l7_baseline.py                             # re-pin do baseline
```

**GATE S3** — este é o teste real de que o mosaico era inócuo:
- (a) **Um único `engine_fingerprint`** em 100% dos registros.
- (b) **Zero erros** de simulação (`error`/`ok=false` vazios).
- (c) **Diff contra o baseline atual: só os 2 casos varamp podem mudar.**
  Qualquer outro caso que mude revela uma segunda config divergente escondida
  pelo mosaico → investigar antes de seguir, **não** re-carimbar por cima.
- (d) Censo re-medido publicado no ledger (mediana, média, MAE>0,1, maxerr>0,1,
  n no tripé) — é ele, não o de 07-22, que vai para a assinatura.

---

## S4 — ⛔ PARE: assinatura da lista de exceções (decisão do professor)

Atualizar `New_Theory/f5_excecoes_propostas.md` com o censo do S3 e apresentar.
**Não assinar por ele.** A lista tem hoje ~10 candidatas com prova:

- **Scatter de réplicas:** BAUER_2024 fig6 ×4 e fig8 ×3 (spread entre réplicas
  0,561 e 0,396 — a curva ideal já violaria a meta), liu2025_fig2_single.
- **Trecho out-of-model com trim registrado:** LIU_2025 ×7, YANG_2021 ×6,
  li2022ti_axial_10Hz_full (trim ainda **pendente de aplicar** — conferir se a
  linha "li2022ti_full trim" do ledger F3 realmente entrou no cfg).
- **Forma faltante com máximo in-engine já aplicado:** jcsr2023_stainless_seawater,
  jcsr2023_plain_outdoor, yang2021_amp0p8mm_ax6kN, yang2021_fig2_typical.
- **Atribuição de paper sem changepoint automático:** liu2020_fig9_AF0.4mm (a
  regra de taxa não achou o corte; a prova é a §3.1.2 do paper — a assinatura
  precisa saber disso).

Lembrar: assinar ratifica também os **trims já aplicados na métrica**
(LIU_2025 ×7, YANG_2021 ×6, li2022ti full, SECOS ×2). Negar um trim devolve o
caso à lista.

---

## S5 — F5.2: docs vivos (só depois do S3, para não publicar número velho)

```bash
python New_Theory/build_variable_explorer.py
```
Depois, na mão: `MODEL_LEGITIMACY.md` (§ do estado da meta + § do re-baseline do
gate B1 que o PARE da F4 pediu) e `CLAUDE.md` (roadmap itens 4/9/10; **acrescentar
o precedente REAL do empate de chave — YANG_2019 — ao gotcha que hoje só tem o
exemplo hipotético JCSR**).

**GATE S5:**
- galeria/`concept_coverage.html` mostram o **n real** (não 115);
- `variable_explorer/reports/` tem um report por caso (hoje 181/202);
- as **13 fontes sem página `study_*`** ganham página **ou** o motivo de não
  ganharem fica escrito (ex.: sem `apparatus_note` — hoje são 17 notas para 28
  fontes);
- todo link verificado.

---

## S6 — F6: o Manual (último passo, só após certificar)

`docs/MANUAL_BAS_V2/` (pt-BR) + `manual.html` no explorador, 3 volumes conforme
§6.1–6.3 do prompt-mestre: **entender** (paradigma, energia, a tese
formas-transferem/constantes-não, tabela de constantes com proveniência, L1–L7,
histórico de falsificações), **explicar** (narrativa em 3 níveis, 5 figuras
geradas do store por `scripts/manual_figs.py`, FAQ de objeções com evidência) e
**aplicar** (instalação, fluxo com telas, junta nova passo-a-passo, paper novo
fim-a-fim, reprodutibilidade e troubleshooting).

**GATE S6:** toda afirmação numérica sai do store/ledger real; figuras por
script versionado; links verificados. Fechar com o relatório executivo (§6.4).

---

## S7 — O que NÃO está autorizado (e é o que falta para a meta)

Dos 55 fora do tripé, **~45 são form-limited**: nenhuma constante os fecha, e o
plano reserva explicitamente essas decisões ao professor. Sem elas, a sequência
acima chega a *"100% − exceções"* **apenas se** as exceções forem assinadas
**e** o restante for aceito como fila aberta.

| Forma na fila | casos que fecharia |
|---|---|
| kernel desacelerante (run-in) | ~20 — LU_2024 10, CHU 6, SUN 1, KARLSEN 1, YANG_2019 terminais 3, ZHANG_2006 fig3 1 |
| bifurcação de limiar | 7 — YANG_2023_IJPEM (tri-falsificado: nenhuma constante move) |
| decisão G2 (MAE-only) | ECCLES_2010 5 (receita pr31 pronta, aguarda a decisão) |
| canal estrutural ξ-dependente | 2 — YANG_2021 |
| cliff/rebound de corrosão | 2 — JCSR (o engine não recupera pré-carga) |
| incubação de assentamento | 2 — âncora interna |
| escala de rigidez com espessura de membro | 3 — ROUSSEAU |
| tripla combinação | 1 — YANG_2023_AME |

Continuam também na mesa, da F4: o candidato **(c) `flank_s_crit`**
(NÃO-demonstrado — o slope do Liu2017 já vinha da ρ-unificação adotada) e a
**opção B, termo debris-desacelerante**. As capacidades existem no engine e
estão **default-inertes e não adotadas**; ligá-las exige prereg + gate + palavra
explícita.

**Fora do escopo do plano, para registro:** o universo da meta são as 202 curvas
do registry. A biblioteca tem **347 CSVs** (114 digitalizados + 233 extraídos) e
**122 PDFs**; 28 fontes estão ligadas. "Todos os artigos e curvas" nunca esteve
no escopo desta execução — se for para virar meta, é um plano novo (digitalizar
→ apparatus_note → caso no registry → fit gateado), que é justamente o
procedimento que o volume 3 do Manual (S6) documenta.

---

## Ordem e dependências

```
S1 (valida conserto) ──┐
S2 (higiene store)  ───┼──> S3 (re-sim + re-carimbo) ──> S4 ⛔ assinatura ──> S5 (docs) ──> S6 (Manual)
                                                              │
                                                              └──> S7: decisões de forma (abrem nova rodada F3/F4)
```

S1 e S2 são independentes e podem ir em qualquer ordem; **os dois têm de estar
fechados antes do S3**, senão o re-carimbo congela o store poluído e o número
errado do YANG_2019. S5 depende do S3 (para não publicar censo velho). S6 é o
último por definição do plano-mestre.
