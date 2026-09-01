# LU_2024 — pico espúrio em 6 CSVs: uma regressão minha, dois artefatos herdados, e três coisas que o defeito estava escondendo

**2026-08-16 (madrugada)** · prereg `2026-08-16-lu2024-pico-espurio` (gates
congelados antes de medir) · store `20be19aabe11` **intocado** (correção é de
DADO; o fingerprint hasheia o bloco `shared` + configs adotadas, não CSVs) ·
censo **143 → 144/205**.

## 1. O defeito, e de quem é

A adoção dado-only `a9541ec` (2026-08-13, **minha**) re-digitalizou 7 CSVs do
`LU_2024` e **corrompeu o `y` de 5 pontos** em 4 delas — a pré-carga sobe e
volta a cair no ciclo seguinte, o que num ensaio Junker contínuo sem reaperto
não existe:

| curva | N | antes → pico → depois | res.máx antes | onde estava o res.máx |
|---|---:|---|---:|---|
| `fig20_T10Nm` | 85 | 0,329 → **0,896** → 0,310 | 0,802 | **no pico** |
| `fig20_T16Nm` | 85 | 0,200 → **0,537** → 0,190 | 0,442 | **no pico** |
| `fig20_T28Nm` | 82 | 0,273 → **0,369** → 0,250 | 0,270 | **no pico** |
| `fig18_amp0p5` | 78 e 85 | 0,276 → **0,457** → **0,407** → 0,159 | 0,180 | fora |

⚠️ **Por que meu gate não pegou:** o G1 daquela adoção conferia as âncoras das
Tabelas 8/9 em **c1/c10/c50/c100**, e o artefato cai **entre c50 e c100**.
Round-trip em 4 pontos não vê pico entre âncoras. Curva de decaimento de
pré-carga é **monótona** — a checagem que faltava não era de âncora, era de
**monotonicidade**.

## 2. Três coisas que o prereg dizia e a execução corrigiu

### 2.1 A premissa da regra de reparo era falsa; a regra sobrevive por outro motivo

O prereg justificava *descartar* dizendo que "o valor verdadeiro não é
observável ali". **Falso, medido:** os `.bkp_luD` (pré-adoção) têm valor em
**exatamente o mesmo x** nas quatro, e ele é monótono (`T10Nm` x=85 → 0,327,
entre 0,329 e 0,310). Eu não *inseri* pontos: **corrompi o `y` de pontos
existentes**. O x-grid é idêntico nos dois lados; a única diferença de grade é
um ponto novo em x=2 em duas curvas (adensamento no penhasco, sem relação).

**A regra fica de pé por um motivo que a própria medição dá:** as duas passadas
têm calibrações diferentes, com viés sistemático de **+0,006** em todos os
pontos vizinhos. Enxertar o `y` antigo na curva nova misturaria duas
calibrações **num ponto só, em silêncio**. Descartar nunca inventa dado.
Recuperar de verdade exige **re-digitalizar a coluna** — prereg próprio.

### 2.2 O artefato da `fig18_amp0p5` tem DOIS pontos, e quem obriga o 2º é o gate

Removido o x=78, o x=85 passou a satisfazer o mesmo critério: os dois pontos
corrompidos **se mascaravam mutuamente** enquanto vizinhos. O G1 pede *zero*
picos, então iterar não é mover a trave — é o que ele literalmente exige.

### 2.3 O G1 é escopado à FONTE, e puxou 2 curvas que não são minhas

`fig18_amp1p0` e `fig20_T22Nm` disparam o critério em **x=80** (0,085 →
**0,352** → 0,072) e são **idênticas ao `.bkp_luD`** ⇒ o artefato **precede**
`a9541ec`. Entraram porque o gate diz *"nenhuma curva do `LU_2024`"*, e três
fatos sustentam repará-las sob a mesma regra: (a) impossibilidade física;
(b) as duas são o **mesmo ensaio em 2 figuras** (Tabela 8@1,0 mm ≡ Tabela
9@22 N·m) e trazem o artefato no mesmo x com o mesmo valor (0,352/0,353) — duas
digitalizações independentes travaram na **mesma curva errada**, que é
exatamente a oclusão que o texto original supunha; (c) repará-las **juntas**
preserva o piso de digitalização do par (MAE 0,0043 → **0,0044**, σ 0,0045 →
**0,0044**, medido) — reparar uma só o corromperia.

## 3. Gates

| # | gate | resultado |
|---|---|---|
| **G1** | nenhuma curva do `LU_2024` mantém pico | **0** (era 6 curvas, 7 pontos) |
| **G2** | âncoras preservadas | **0,000000** de deslocamento nas 6 — ver nota abaixo |
| **G3** | cirurgia mínima | linhas sobreviventes **bit-idênticas** ao backup nas 6 |
| **G4** | isolamento | fingerprint **único** `20be19aabe11` nos 210; nada fora do `LU` re-simulado |
| **G5** | censo não encolhe | **143 → 144** |
| **G6** | guarda permanente | `tests/test_curvas_sem_pico_espurio.py`, 7 testes |

⚠️ **O G2 foi executado numa forma MAIS APERTADA que a escrita, porque a
escrita era insatisfazível.** O texto pedia "âncoras das Tabelas 8/9 batendo a
±0,005 nas 7 re-digitalizadas" — mas `lu2024_fig18_familia_tab8.md` (2026-08-06)
já media desvios de até **+0,0792** em c10 na `amp2p0`, então nenhuma execução
poderia passar. O que o gate *quer* testar é se **o reparo move âncora**, e isso
se mede antes-vs-depois: deu **zero em todas**, o que é mais forte do que ±0,005.

⚠️ **Predição registrada, conferida nos 4 números:** `T10Nm` res.máx
0,802 → **0,3146** (previa ~0,31), σ 0,155 → **0,0749** (previa ~0,075), MAE
**0,2514** (previa ~0,25) e **não fecha** — o defeito de forma dela (perder
demais em F₀ baixo) é independente do artefato, como declarado.

## 4. A guarda (G6) não pode usar o critério de vizinhos

Medido: no critério `y[i] > vizinhos + 0,01`, o artefato de 2 pontos da
`fig18_amp0p5` dá salto de **0,050** — o segundo ponto corrompido *sustenta* o
primeiro. Uma guarda com piso absoluto em 0,05 teria deixado passar **exatamente
a regressão que ela existe para pegar**. Evidência local é cega a defeito
correlacionado.

A estatística é global: `max(y − mínimo corrente)`, normalizada pela escala da
curva (a biblioteca tem curvas em fração e em porcento). Separação medida sobre
as 210:

| população | valor |
|---|---:|
| mediana das 210 | **0,0000** (a maioria é exatamente monótona) |
| pior legítimo não isento (`jcsr2023_plain_outdoor`) | **0,083** |
| **barra** | **0,10** |
| artefato herdado (2 curvas) | 0,393 · 0,399 |
| a regressão `a9541ec` (4 curvas) | 0,146 · 0,261 · 0,485 · **0,612** |

Margem assimétrica e declarada: 1,2× acima do pior legítimo, **3,9× abaixo** do
artefato mais brando. Isenção: **uma** curva (`eccles…fig8d…intermittent`,
0,429) — protocolo que retira e re-aplica carga, onde a recuperação é física.
Isenção **nomeada com razão escrita**, com teste que a proíbe de virar
whitelist. **Validada por perturbação:** restaurado o CSV da regressão, a guarda
falha nomeando a curva; restaurado o reparo, o arquivo volta com **SHA
idêntico**.

## 5. O que o defeito estava escondendo — três consequências, nenhuma cosmética

**(a) Uma curva estava DECLARADA em cima do artefato.** A `fig20_T22Nm` era
"órfã de protocolo" (item F) **e** contava como *metric-limited por colapso
quase-vertical*, porque o pico fazia o dado cair **0,28** entre pontos vizinhos
— acima do limiar de 0,25 do classificador. O "colapso" era o artefato. Sem
ele a curva **fecha por mérito** (0,0364 / 0,0735 / 0,0212) e a camada
`metric_limited_colapso` foi de 1 para **0**. Declaração **retirada** com prova
preservada (`_DECLARACOES_RETIRADAS_PICO_ESPURIO`), como manda o precedente K6:
enquanto ficasse, o `declarado_total` a contaria 2×. Quem denunciou foi a
guarda-espelho `test_medicoes_cruzadas`.

**(b) A "fila form-limited ZERO" de 2026-08-15 era artefato do mesmo tipo.** A
`fig20_T10Nm` saía da fila pelo mesmo mecanismo (queda de 0,586 entre pontos ⇒
colapso falso). Hoje ela é a **única** curva form-limited do projeto — e é fila
legítima, com as três pernas violadas (5,03× · 3,15× · 3,00×).

**(c) Dois instrumentos de censo discordavam, e só agora dava para ver.** Com a
`T10Nm` de volta à fila, `censo_por_proposta.py` publicava **0 abertas** contra
**1 form-limited** da triagem canônica — sobre a mesma curva. Causa: os dois
chamavam `_pisos_medidos`, mas com **populações diferentes** — o script
filtrava por `caso_comparavel`, e a `fig18_amp1p0` está fora do censo
**exatamente por ser a réplica** que dá o piso do `LU_2024`. Sem ela: piso
`None` ⇒ a curva caía em `indecidivel_sem_piso` (tem estatuto!) em vez de
`form_limited` (fila de trabalho). Corrigido para a população inteira, que é o
que `report_html` usa nas duas linhas que julgam.

> **Lição, irmã da que aquele arquivo já carregava:** chamar o mesmo helper
> **não basta** — a POPULAÇÃO passada a ele faz parte da regra. Dois
> instrumentos podem usar a função canônica e ainda assim discordar.

## 6. Subproduto: cinco células vencidas na tabela executiva, todas sem âncora

Ao sincronizar o censo, medi **toda** a tabela "leitura estratégica VIGENTE" do
relatório executivo, não só as células que a guarda vigia. As quatro ancoradas
estavam certas ou falharam alto no mesmo dia; as **cinco sem âncora estavam
todas vencidas**: `resolvidos` **155 → 167** (defasagem de 12), só-res.máx
4 → 7, só-σ_res 10 → 13, mais-de-uma 42 → 39, 3-maiores-fontes 36 % (26 de 73)
→ **41 % (25 de 61)**. As cinco ganharam âncora em `_VIVAS` (+5 chaves em
`_censo`), e a nova de `resolvidos` foi validada por perturbação.

⇒ **número sem âncora não fica velho devagar; fica velho em silêncio, ao lado
de vizinhos vigiados que parecem avalizá-lo.**

## 7. Reprodutibilidade

```bash
py -3.12 New_Theory/parallel_batch.py --sources LU_2024 --workers 6 --store
PYTHONPATH=src py -3.12 -m bolt_analysis_studio.validation.report
py -3.12 -m pytest tests/test_curvas_sem_pico_espurio.py \
    tests/test_meta_numeros_nao_envelhecem.py tests/test_medicoes_cruzadas.py \
    tests/test_instrumentos_de_censo_concordam.py -q
py -3.12 New_Theory/regra_de_parada_triagem.py
```

Backups: `*.csv.bkp_pico` (estado pré-reparo) e `*.csv.bkp_luD` (pré-`a9541ec`)
em `Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/`.
