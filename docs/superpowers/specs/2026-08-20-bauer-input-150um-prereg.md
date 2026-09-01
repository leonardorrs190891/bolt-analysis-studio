# PREREG — correção de INPUT no BAUER fig8: pico do espectro 155 → 150 µm (o número do paper) + re-fit dos per_case sob o input certo

**2026-08-20 (23:0x)** · **gates congelados neste commit** · mandato das 22:56
(*"continue"*) — executando a correção que o adendo §6 do prereg
`bauer-fig8-scrit-especime` registrou como pendente.

## 1. O erro de input e o que ele escondia

O paper (p.8): *"a displacement amplitude of sa,E = 80 µm for 18 cycles
followed by two cycles with **sa,E,peak = 150 µm**"*. O `delta_spectrum`
adotado carregava **155 µm** (erro de 3 % no pico). Medido: a correção pura
**derruba as duas fechadas** (test1 mx 0,072→0,148; test2 0,042→0,104) — os
per_case fitados ontem absorviam o erro, a classe exata do "fit antigo
absorvia o input errado" da fig20 do LU. A disciplina: corrige-se o input E
re-fitam-se as constantes sob o input certo — nunca se mantém o input errado
porque o fit gosta dele.

## 2. Pacote

| item | valor | nota |
|---|---|---|
| `delta_spectrum` (grupo) | `[[18, 8e-5], [2, 1.5e-4]]` | INPUT do paper |
| per_case `test1` | s_crit **13 µm** · k **0,070** | região **7/9** na grade fina; centralidade 4/4; 0,0272/0,0630/0,0303 — FECHA |
| per_case `test2` | s_crit **28 µm** · k **0,065** | região **6/9**; pior perna 0,40×; 0,0148/0,0396/0,0184 — FECHA |
| `test3` | INTOCADO (sem per_case) | piora 0,0241→0,0385 de MAE sob o input certo — **custo declarado**; a exceção de scatter (desvio-à-mediana 0,349) segue cobrindo com folga |

Nota de leitura: o k de test1/test2 ficou 0,070/0,065 — ainda mais próximo
entre si que antes (0,070/0,060), coerente com o *"gradients of all tests
are still similar"* dos autores.

## 3. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | test1 ao dígito | 0,0272/0,0630/0,0303 pelo canônico — FECHA |
| **G2** | test2 ao dígito | 0,0148/0,0396/0,0184 pelo canônico — FECHA |
| **G3** | test3 | 0,0385/0,2104/0,0433 pelo canônico (piora declarada, prova de scatter cobre) |
| **G4** | fig6 ×6 + resto | bit-idênticos; isolamento Δ=0 fora do BAUER no re-stamp; fingerprint único |
| **G5** | censo | **166/205 INALTERADO** (test1/test2 seguem no tripé com células re-lidas) |
| **G6** | sincronização | prov do grupo atualizado · docs · aging · HTML |

## Estado

EXECUTADO 2026-08-20 (23:0x-23:3x): G1 test1 ao digito (0,0272/0,0630/0,0303 — FECHA), G2 test2 ao digito (0,0148/0,0396/0,0184 — FECHA), G3 test3 ao digito (0,0385/0,2104/0,0433 — piora declarada, prova de scatter cobre), G4 isolamento exato (so as 3 do BAUER no diferencial) fingerprint unico 89b1899f18c1 nos 210, G5 censo 166/205 INALTERADO, G6 sincronizado (parada re-medida, HTML regenerado, guardas 58/58).
