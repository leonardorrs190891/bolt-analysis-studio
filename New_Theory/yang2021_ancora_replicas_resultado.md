# A âncora das réplicas do `YANG_2021`: o scatter é **artefato em até 4×** — e a rota que eu propus está **FALSIFICADA**

**2026-08-10** · só-leitura · **nada adotado** · store `bd74eaf0b11d`, censo 147/205 ·
continuação imediata da adoção **D-AD**, cujo doc apontou esta rota como *"candidato natural para
a próxima rodada"*.

## A assimetria, medida

As 3 réplicas da condição 0,6 mm / 8 kN são digitalizadas de figuras diferentes e **começam em
ciclos diferentes**. O `align` canônico normaliza cada curva **no seu próprio primeiro ponto** —
por decisão registrada (*"o artigo normaliza F/F₀=1 ali e a queda anterior não tem contraparte
medida"*). Consequência medida:

| réplica | 1º ponto | último | n | **`align`** |
|---|---:|---:|---:|---:|
| `r1` | **N = 500** | 11 800 | 9 | **0,8744** |
| `r2` | N = 18 | 11 750 | 57 | 0,9628 |
| `r3` | N = 20 | 11 750 | 56 | 0,9596 |

⇒ **o mesmo modelo é dividido por 0,874 contra a `r1` e por ~0,96 contra as irmãs — 10 % de
normalização diferente**, para três medições da mesma condição.

E o motivo é grande, não marginal:

| réplica | perda até N=500 | fração da queda TOTAL |
|---|---:|---:|
| `r2` | 0,0539 | **59 %** |
| `r3` | 0,0660 | **57 %** |

**A `r1` renormaliza fora ~58 % da queda** que as irmãs medem.

## ✅ O que isto de fato estabelece: o piso de réplica desta família está INFLADO

Re-ancorando as três na janela comum (N ≥ 500), o desacordo **dado-vs-dado** colapsa:

| par | piso cru (vigente) | re-ancorado | redução |
|---|---:|---:|---:|
| `r1` × `r2` | 0,0344 | **0,0203** | −41 % |
| `r1` × `r3` | 0,0521 | **0,0129** | **−75 %** |
| `r2` × `r3` | 0,0190 | **0,0075** | −61 % |

⇒ **até 4× de inflação.** Boa parte do "scatter de réplicas" desta família é a **âncora**, não a
bancada. Isto importa para além desta fonte: qualquer prova de exceção **F7 por piso** que use
esta família está usando uma barra generosa demais — e a campanha já retratou 5 exceções por
piso inválido (ROUSSEAU, CACCESE).

## ⛔ E a rota que eu propus está FALSIFICADA

O doc do D-AD terminou dizendo: *"candidato natural para a próxima rodada: alinhar as janelas das
3 réplicas antes de re-escolher a dose"*. Medido:

| | vigente | re-ancorado N ≥ 500 |
|---|---|---|
| **`r1`** | 0,0167/0,0813/**0,0268** | **0,0167/0,0813/0,0268 — IDÊNTICO** |
| `r2` ✅ | 0,0483/0,0587/0,0103 | 0,0152/0,0231/0,0070 ✅ |
| `r3` ✅ | 0,0285/0,0387/0,0073 | 0,0094/0,0153/0,0065 ✅ |

**Re-ancorar é no-op para a `r1`** — a janela dela já começa em 500, logo o seu primeiro ponto já
*é* a âncora. E melhora **só** as duas que **já passavam**, descartando 57–59 % da queda que elas
cobrem.

⇒ **a mudança de âncora não destrava nada e afrouxa a métrica onde ela era mais exigente.**
Recusada. Não é conserto de dado nem de comparabilidade: é tornar o teste mais fácil nas curvas
em que ele estava difícil.

## Onde a `r1` fica, com número

`0,0167 / 0,0813 / 0,0268` contra limites `0,05 / 0,10 / 0,025` ⇒ **reprova só no σ, por 7 %**.
É a curva mais próxima de fechar na biblioteca.

E as rotas conhecidas estão medidas e fechadas:

* **piso F7** — o MAE do modelo (0,0167) é **menor** que o piso re-ancorado `r1`×`r2` (0,0203),
  mas a perna violada é o **σ**, e os pisos de σ da família ficam bem abaixo de 0,025 ⇒ sem
  cobertura;
* **dose maior de `gth`** — `2,5e-7` fecha a `r1` mas **tira a `r2`** (D-AD, medido);
* **âncora comum** — no-op para a `r1` (acima).

## O que fica

1. **Achado reutilizável:** quando réplicas de uma condição têm **janelas de digitalização
   diferentes**, o piso de réplica calculado no cru **mistura scatter físico com diferença de
   âncora**. Medir o piso **na janela comum, re-ancorado** é o número honesto — e aqui ele é até
   **4× menor**. Vale re-medir os pisos das outras famílias com janelas desiguais antes de
   qualquer nova prova F7.
2. **Rota falsificada com número**, registrada como tal para não ser re-proposta.
3. A `r1` segue na fila da **P-14**, agora com as três rotas conhecidas explicitamente fechadas.

## Reprodutibilidade

Sondas só-leitura sobre `metric_x`/`metric_pred`/`metric_data` do store; re-ancoragem =
dividir cada vetor pelo seu valor no 1º ponto da janela comum. Segundos.
