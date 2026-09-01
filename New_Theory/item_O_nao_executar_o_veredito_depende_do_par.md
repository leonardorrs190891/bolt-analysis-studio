# Item **O** — NÃO executar: o veredito de retratação depende de um pareamento **nunca declarado**

**2026-08-15 (19:xx)** · só-leitura · **nada retratado, nada reclassificado** · store
`20be19aabe11`, censo **143/205**, exceções **23**.

---

## 1. O que o item O propunha

Retratar **2 exceções assinadas** — `eccles2010_fig8a_no_axial_baseline1` e
`fig8c_no_axial_baseline2` — porque a prova gravada nelas cita um piso que a **P-15**
declarou inválido:

> `fig8a`: *prova de piso (FORTE): res.máx **0.122/0.257** · σ **0.039/0.083***
> `fig8c`: *prova de piso (FORTE): res.máx **0.145/0.257** · σ **0.039/0.083***

O `0,083` veio de dispersão **entre cargas axiais de 0 a 3,5 kN** — a variável varrida do
paper. A P-15 retratou a `fig7c` por isso; estas duas ficaram de pé sobre o mesmo denominador.

O item afirmava, com número: *"o piso VÁLIDO é 0,1134/0,0443 … as duas falham as duas pernas
(0,1320 e 0,1463 contra barra FORTE 0,0802) e nem na barra PROVA (0,1134) passam."*

## 2. O bloqueio está certo em espécie e **largo demais em escopo**

As **10** curvas do `ECCLES_2010` estão em `_SEM_FAMILIA_MECANICA`, todas com a mesma razão:
*"carga axial ≠ (chave cega: é a variável varrida do ECCLES)"*.

⚠️ Mas **4 delas são `no_axial`** — carga axial **zero** nas quatro. Elas **não diferem** na
variável varrida. A afirmação correta é *"nenhum par ATRAVÉS de cargas axiais diferentes"*; o
que está gravado é *"nenhum par desta fonte"*.

E o desenho já prevê a saída: o docstring de `_pisos_medidos` diz que curvas bloqueadas
*"nunca entram em família automática (**pares declarados continuam possíveis**)"*. A rota
legítima é declarar o par em `_PARES_REPLICA_DECLARADOS`, **não** desbloquear a fonte.

## 3. ⚠️ E aqui o item quebra: o veredito **depende de qual par se declara**

Medido pelo **helper do report** (`_pisos_medidos`, 40 pontos interpolados sobre
`metric_data`), declarando cada um dos 6 pares possíveis da família `no_axial`:

| par declarado | MAE | res.máx | σ | `fig8a` | `fig8c` |
|---|---:|---:|---:|:--:|:--:|
| `fig3_typical` × `fig7a` | 0,0479 | 0,1104 | 0,0212 | ⛔ | ⛔ |
| `fig3_typical` × `fig8a` | 0,0502 | 0,1109 | 0,0585 | ⛔ | ⛔ |
| `fig3_typical` × `fig8c` | 0,0288 | 0,0756 | 0,0353 | ⛔ | ⛔ |
| `fig7a` × `fig8c` | 0,0478 | 0,0640 | 0,0201 | ⛔ | ⛔ |
| `fig7a` × `fig8a` | 0,0556 | **0,1846** | 0,0545 | **PROVA** | **PROVA** |
| **`fig8a` × `fig8c`** | 0,0541 | **0,1866** | **0,0698** | **FORTE** | **PROVA** |

**Seis pareamentos, três vereditos.** Quatro justificariam a retratação; **dois não**.

⇒ **o item O cita `0,1134 / 0,0802`, que bate com a faixa dos pares FRACOS** — não com a
réplica que o **próprio artigo declara**.

## 4. Por que `fig8a` × `fig8c` é o par defensável

O paper nomeia as duas: **`baseline1`** e **`baseline2`**. São, por rótulo do autor, as duas
corridas de referência da mesma condição — que é exatamente a definição de réplica que a
campanha usa nos 4 pares já declarados (`rep1/rep2` do CACCESE, `run1/run2` do LIU_2016…).

As outras duas `no_axial` são de natureza diferente: `fig3_typical` é uma curva **ilustrativa**
("typical") e `fig7a` é a **baseline de outra série**. Pareá-las é uma afirmação mais fraca
que a do autor.

⇒ **declarar o par certo é uma decisão de procedência**, e ela decide o destino de 2 exceções
assinadas.

## 5. ⚠️ E o caso está no fio da navalha

Com o par do artigo, `fig8a` tem `res.máx` = **0,131955** contra barra FORTE **0,131939** —
distância de **1,6 × 10⁻⁵**. A comparação do helper com precisão cheia dá **FORTE OK**; um
piso arredondado na 5ª casa inverte o rótulo FORTE↔PROVA.

Não muda a conclusão (PROVA passa nas duas leituras), mas fica registrado: **o grau da prova
desta curva não é numericamente estável**, e publicá-lo como "FORTE" sem essa ressalva seria
precisão falsa.

## 6. Veredito

⛔ **NÃO EXECUTAR o item O como está.** A retratação repousa num piso derivado de um
pareamento **que nunca foi declarado nem justificado**, e o par que o **artigo** declara dá o
resultado **oposto**.

Isto é a **7ª** vez que a campanha enfrenta validade de piso — e a **1ª em sentido
defensivo**: as seis anteriores retrataram exceções apoiadas em piso inflado; esta impede
retratar exceções que o piso **correto** sustenta.

**O que a decisão do professor precisa escolher** (é procedência, não medição):

| opção | consequência medida |
|---|---|
| **(a)** declarar `fig8a` × `fig8c` como par de réplica | ECCLES ganha piso (σ **0,0698** ⇒ `limite_sres` 0,0250 → **0,0698**); as 2 exceções **sobrevivem** e passam a ter denominador válido |
| **(b)** declarar outro par / nenhum | as 2 exceções ficam sem denominador válido ⇒ retratar (item O como escrito) |

⚠️ A opção **(a) mexe no `limite_sres` da fonte** e portanto **pode mover o censo** — exige
prereg com gates, não é consequência automática desta medição.

## 7. O que NÃO fiz

Não retratei, não declarei par, não toquei `_EXCECOES`, `_SEM_FAMILIA_MECANICA`,
`_PARES_REPLICA_DECLARADOS` nem config. As declarações de par nas sondas foram **temporárias
e revertidas** em `finally`.

## Reprodutibilidade

Sondas inline no corpo do commit; declaram o par em `rh._PARES_REPLICA_DECLARADOS`, chamam
**`rh._pisos_medidos`** (nunca reimplementam o cálculo de piso) e restauram a lista em
`finally`. Erros do modelo lidos do store via `CaseResult`; σ sempre por `rh.sres_para_censo`.
