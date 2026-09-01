# PREREG — `arrest_approach_exp` = 2,0 escopado ao protocolo INTERMITENTE do ECCLES: as 2 curvas que a retratação devolveu à fila fecham

**2026-08-23 (20:4x)** · **gates congelados neste commit** · medição completa em
`New_Theory/eccles_fig8_arrest_exp_resultado.md`.

## 1. O que se adota

| campo | valor | escopo | procedência |
|---|---|---|---|
| `arrest_approach_exp` | **2,0** | `per_case` token `fig8` (as 4 curvas da série intermitente) | **FITADO-DECLARADO** com região de 3 células (1,75–2,25); célula por CENTRALIDADE (precedente D-I/D-AA), melhor pior-perna 0,71× |

Nada mais muda. As 6 curvas das séries `typical`/`constant` **não recebem o
campo** — escopo por PROTOCOLO, que o próprio paper distingue (rótulo
"intermittent"), com o precedente da retratação LU de 08-14.

## 2. Por que o escopo é legítimo e não conveniência

- **Isolamento MEDIDO dentro do escopo**: `fig8b` e `fig8d` (intermitentes com
  axial) dão **Δ = 0,0000 exato** em todas as doses. O escopo cobre 4 curvas e
  move 2 — não há efeito escondido nas outras 2.
- **A alternativa foi medida e REPROVA**: no grupo inteiro, 1,5 fecha 1 e quebra
  1 (saldo 0); 2,0 fecha 2 e quebra 4 (saldo −2). Sem escopo, a adoção é
  negativa — e é por isso que ela existe escopada, não por gosto.
- **Razão 2 curvas por constante**, do lado model-like da auditoria de hoje.

## 3. Diagnóstico que sustenta a classe de alavanca

`|viés|/MAE = 1,00` **exato** nas duas, resíduo de sinal único (10/10 e 23/23
negativos) ⇒ erro de **NÍVEL** com o modelo **abaixo** do dado. É o caso em que
o discriminante da campanha prevê que alavanca de nível funciona — e funcionou.
Distinto da `amp0p8` (form-limited por esgotamento), cujo defeito é curvatura.

## 4. GATES — congelados ANTES da execução

| # | gate | critério |
|---|---|---|
| **G1** | alvo ao dígito pelo canônico | `fig8a` **0,0243/0,0488/0,0254** · `fig8c` **0,0287/0,0708/0,0341** — as duas FECHAM (lim 0,05/0,10/0,0565) |
| **G2** | irmãs da fonte | `fig8b`/`fig8d` bit-idênticas · as 6 fora do escopo bit-idênticas |
| **G3** | isolamento global | Δ = 0 nas 195 de outras fontes · fingerprint único nos 210 |
| **G4** | censo | tripé 169 → **171/205** · fila form-limited 2 → **0** · exceções inalteradas (as 2 já estavam retratadas) |
| **G5** | sincronização no MESMO commit | docs vivos (CLAUDE.md, DECISOES, mapa, censo_por_proposta, relatório executivo) · `parada_baseline.py --gravar` · aging test · HTML das páginas afetadas |

**Gate de bloqueio (G0):** só executar com a árvore da sessão paralela LIMPA —
re-simular sobre `report_html.py`/`validation_cases.py` meio-editados carimbaria
um fingerprint que não corresponde a commit nenhum.

## 5. O que NÃO é pré-registro, declarado

A célula foi escolhida **depois** de ver as doses. A regra (centralidade) é de
precedente e o cálculo está no resultado para conferência, mas esta adoção não
pode reivindicar escolha às cegas. Os gates acima é que estão congelados.

## 6. Achado da execucao que fica declarado

As duas fecham sob o limite **POR FONTE** (0,0565), nao sob o global (0,025):
sigma 0,0254 e 0,0341. A guarda `test_censo_que_repousa_em_piso_de_fonte_nao_
cresce_calado` acusou e as duas entraram no `_DEPENDEM_DE_PISO_DE_FONTE` com a
medicao — nenhuma das 4 celulas as poria sob o global, logo e propriedade da
rota. O piso do ECCLES foi APERTADO no mesmo dia (0,0698 -> 0,0565).

## Estado

**EXECUTADO 2026-08-23 (20:5x-21:4x)** : G0 liberado (arvore limpa as 20:25) · G1 ao digito (0,0243/0,0488/0,0254 e
0,0287/0,0708/0,0341) · G2 as 8 irmas bit-identicas · G3 isolamento EXATO
(so as 2 mudaram nas 210; fingerprint unico `db7de97e682a`) · G4 censo
169 -> **171/205**, fila 2 -> **0** · G5 sincronizado (6 docs, parada,
aging, HTML). Dois consertos na execucao: o `prov` foi escrito dentro do
`cfg` (lugar errado — o lookup le no nivel do NODE) e inflava o passivo de
13 para 21; e eu troquei a DEFINICAO de "com estatuto" ao sincronizar dois
docs, em vez de so o numero.
