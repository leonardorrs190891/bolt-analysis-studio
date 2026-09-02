# Manual do BAS V2

**Bolt Analysis Studio V2** — análise de auto-afrouxamento de juntas aparafusadas
por um modelo massa-mola-amortecedor com estado lento e energia fechada.

Desenvolvedores: **Prof. Leonardo Rosa Ribeiro da Silva, PhD** — leorrs@ufu.br · **Neilon de Souza da Silva, PhD** — neilon@petrobras.com.br

---

## Comece por aqui

| se você quer… | leia |
|---|---|
| **entender** o modelo — física, proveniência das constantes, o que já morreu | [Volume 1 — Entender o modelo](01-entender-o-modelo.md) |
| **explicar** o modelo a terceiros — aula, defesa, paper, revisor cético | [Volume 2 — Explicar o modelo](02-explicar-o-modelo.md) |
| **aplicar** o software — instalar, rodar, junta nova, paper novo | [Volume 3 — Aplicar o software](03-aplicar-o-software.md) |
| saber **onde a execução está** — painel por fase, adoções com gate, e o que depende de decisão | [Relatório executivo](00-relatorio-executivo.md) |

**Três minutos, um parágrafo, se é tudo o que você tem:**
[o elevator do Volume 2](02-explicar-o-modelo.md#nível-1--o-parágrafo-elevator).

---

## O estado do modelo, em números reais

Todos do store canônico `validation_store.json`, fingerprint **`4f5bedfbace4`**,
via [`figs/numbers.json`](figs/numbers.json):

| | |
|---|---:|
| curvas de artigo comparáveis | **202** (28 fontes) |
| **no tripé** (`MAE<0,10` **E** `res.máx<0,10`) | **147 (73 %)** |
| fora do tripé | 55 — **34 só pelo pico, 0 só pelo MAE**, 21 por ambos |
| mediana MAE / média | **0,0315** / 0,0445 |
| mediana do resíduo máximo | 0,0623 |
| erros de simulação | **0** |
| fontes fechando 100 % | **13** |
| **constantes fitadas no dataset inteiro** | **3** |

O gargalo é o **resíduo máximo**, não o MAE — esforço medido em MAE médio não move
a meta. Das 55 curvas fora, **19 não pedem física nova** e **36 são *form-limited***
(classificação curva-a-curva: [`frontier_classes.md`](../../New_Theory/frontier_classes.md)).
Ressalva medida: "não pedir física nova" **não** é "fechar de graça" — das 6 de
nível sondadas, ler o piso fecha **1** ([`level_seven_probe.md`](../../New_Theory/level_seven_probe.md)).

---

## As cinco figuras

Geradas do store por [`scripts/manual_figs.py`](../../scripts/manual_figs.py), em
variante clara e escura. Cada uma traz `variaveis`, `como_ler` e — onde couber —
`ressalva` no [`figs/numbers.json`](figs/numbers.json).

| | figura | o que prova |
|---|---|---|
| 1 | [anatomia da curva](figs/fig1_anatomia.svg) | as três fases (patamar/joelho/piso) saem da física |
| 2 | [decomposição por mecanismo](figs/fig2_decomposicao.svg) | a previsão é **atribuível**, e a soma fecha |
| 3 | [painel das 202 curvas](figs/fig3_painel.svg) | o escopo real e o gargalo real, sem seleção |
| 4 | [tornado de sensibilidade](figs/fig4_tornado.svg) | a contagem de liberdade é auditável |
| 5 | [formas × fontes](figs/fig5_formas_fontes.svg) | a tese central, em uma imagem |

**Regenerar e provar:**

```bash
py -3.12 scripts/manual_figs.py            # regera os 10 SVGs + numbers.json
py -3.12 scripts/manual_figs.py --check    # gate: byte-identidade com script+store
```

O gate re-renderiza num diretório temporário e exige os **11 artefatos
byte-idênticos**. Ele existe porque a versão anterior — que só testava existência
— passou sobre um `numbers.json` corrompido e sobre figuras quatro revisões
atrasadas.

---

## Este Manual não duplica nada

Ele é o **fio condutor**. O conteúdo detalhado vive onde sempre viveu, e o Manual
aponta:

| assunto | documento |
|---|---|
| equações completas | [`MODEL_MATH_REFERENCE.md`](../../New_Theory/MODEL_MATH_REFERENCE.md) |
| física vs overfitting (registro vivo) | [`MODEL_LEGITIMACY.md`](../../New_Theory/MODEL_LEGITIMACY.md) |
| metodologia de evolução (MEM) | [`METHODOLOGY.md`](../../src/bolt_analysis_studio/docs/METHODOLOGY.md) |
| limitações L1–L7, fatia por fatia | [`l1l7_final_report.md`](../../New_Theory/l1l7_final_report.md) |
| decisões abertas | [`DECISOES_PENDENTES.md`](../../New_Theory/DECISOES_PENDENTES.md) |
| 14 páginas de fundamentos + 82 variáveis + 28 estudos por fonte + galeria dos 203 casos | [explorador](../../New_Theory/variable_explorer/index.html) |
