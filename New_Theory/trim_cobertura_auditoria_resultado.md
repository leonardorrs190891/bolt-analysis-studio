# A janela da métrica pelo **fim**: o trim NÃO compra aprovação — e o meu primeiro número dizia o contrário

**2026-08-12** · só-leitura · **nada adotado** · store `bd74eaf0b11d`, censo **147/205** ·
simétrico do audit do `align` (`align_cobertura_auditoria_resultado.md`, mesmo dia).

## A premissa

A janela da métrica é definida nas duas pontas: o **`align`** normaliza no 1º ponto do dado
(medido hoje: inerte em 89 % da biblioteca, não infla aprovação) e o **fim** é cortado por
`trim_n_max` per-fonte mais o `FLOOR_TRIM = 0,10` global. A ponta final **nunca foi
quantificada** — e a campanha tem histórico contencioso ali (a linha de métrica do `LIU_2025`:
4 tentativas, 4 mortes por gate).

> **Curvas com mais dado excluído no fim passam mais facilmente?**

## ⚠️ Primeiro eu medi errado, e o erro parecia um escândalo

Comparei `metric_x` contra **`r.cycles`** — a grade **simulada** — e obtive:

| exclusão (métrica ERRADA) | n | taxa no tripé |
|---|---:|---:|
| > 30 % | 8 | **100 %** |

*"Quem exclui mais, passa mais"*, com 8 de 8. O que denunciou foi olhar as curvas: **a maioria
delas tinha `trim = None`** — não havia trim nenhum para explicar a exclusão.

A causa: `r.cycles` é a grade **da simulação**, que roda até `n_max`; a razão
`1 − n_métrica/n_simulação` mede *"a simulação passa do último ponto do dado"*, **não** *"o trim
cortou dado"*. Eram grandezas diferentes com o mesmo nome.

## ✅ Medido contra o CSV CRU, o sinal INVERTE

Lendo os 205 CSVs pelo helper canônico (`load_full_curve` + convenção `(x−offset)·scale`),
contando **pontos de dado** descartados após o fim da janela:

| exclusão real no fim | n | **taxa no tripé** | MAE mediano |
|---|---:|---:|---:|
| **0 (nada excluído)** | **127** (62 %) | **84 %** | **0,0205** |
| < 5 % | 19 | 53 % | 0,0316 |
| 5–15 % | 26 | 54 % | 0,0366 |
| 15–30 % | 17 | **35 %** | 0,0665 |
| > 30 % | 16 | 62 % | 0,0374 |

Mediana de exclusão: **0,000** · p75 **7 %** · p90 **21 %** · máx **77 %**.

⇒ **as curvas com ZERO exclusão são as que mais passam (84 %)**, e as trimadas passam a
35–62 %. O trim **não compra aprovação** — as curvas trimadas são as difíceis, que é
justamente por que foram trimadas. A leitura causal correta é a oposta da que o número errado
sugeria.

## As 10 maiores exclusões reais

| curva | excluído | `trim_n_max` | tripé |
|---|---:|---|---|
| `eccles2010_fig8b_axial_0p7kN_intermittent` | **77,1 %** (27 de 35) | **None** | — |
| `liu2025_M16_fig2_single` | 67,2 % (90 de 134) | 8 000 | — |
| `eccles2010_fig8a_no_axial_baseline1` | 58,3 % (14 de 24) | **None** | — |
| `sun2025…nogrease_crimp` | 58,3 % (14 de 24) | 9 514 | ✅ |
| `sun2025…nogrease_standard` | 50,0 % (11 de 22) | 6 596 | ✅ |
| `yang2021_amp0p6mm_ax8kN_r3` | 47,7 % (51 de 107) | 11 800 | ✅ |
| `lu2024_M8_fig18_amp2p0` | 46,2 % (6 de 13) | **None** | ✅ |
| `liu2025_M16_amp0p25` | 44,4 % (8 de 18) | 240 000 | — |
| `yang2021_amp0p6mm_ax8kN_r2` | 43,6 % (44 de 101) | 11 800 | ✅ |
| `liu2025_M16_amp0p3` | 40,0 % (6 de 15) | 180 000 | — |

⚠️ **As `trim = None` com exclusão alta são o `FLOOR_TRIM = 0,10`** — a convenção global que
tira da métrica todo ponto com `ratio < 0,10`. O `CLAUDE.md` já a documenta (43 de 203 curvas,
588 pontos, `ECCLES_2010` com 56); aqui ela aparece medida por curva, e no `fig8b` chega a
**77 % dos pontos**.

## A cobertura combinada, dita de uma vez

Somando os dois audits do dia:

* **início** — 11 curvas com **25–38 %** da perda predita antes do 1º ponto medido (`align`);
* **fim** — 16 curvas com **> 30 %** dos pontos de dado fora da janela;
* e as `yang2021` `r2`/`r3`, que ontem eu usei como referência de réplica, **passam sobre menos
  de 60 % do próprio dado**.

Nenhum desses é erro: são convenções declaradas, cada uma com razão registrada. O que não
existia era o **número**. Agora existe, e a leitura honesta das curvas afetadas é *"passam no
trecho medido"*, não *"reproduzem o ensaio inteiro"*.

## Lição de método (a terceira desta classe em três dias)

Meu primeiro número comparava a janela com a **grade simulada** em vez do **dado** — e produzia
um resultado que se lia como escândalo, na direção oposta da verdade. O que o pegou foi
**olhar as linhas** (as `trim = None` no topo da lista de "mais trimadas" eram uma
contradição interna), não conferir a fórmula.

⇒ **num ranking, a checagem barata é perguntar se os primeiros colocados fazem sentido pelo
motivo alegado.** Se o topo do ranking de "mais trimadas" não tem trim, a grandeza está errada.

## Reprodutibilidade

`trim_audit2.py` no scratchpad (a v1, com a grandeza errada, fica em `trim_audit.py` como
registro do erro). Lê os 205 CSVs por `inputs.load_full_curve`, aplica `(x−offset)·scale` e
compara com `metric_x`. Segundos, só-leitura.
