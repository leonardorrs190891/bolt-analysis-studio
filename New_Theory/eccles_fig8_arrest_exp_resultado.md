# ECCLES fig8 — as 2 curvas que a retratação devolveu à fila TÊM ROTA: `arrest_approach_exp` por PROTOCOLO fecha as duas

**2026-08-23 (20:2x-21:4x)** · ✅ **ADOTADO** (gates 5/5; o §6 registra o
bloqueio G0 que existiu até 20:25 e a §7 o achado da guarda) · store
`c61366365977` → **`db7de97e682a`** · limite σ da fonte
**0,0565** via `rh.limite_sres` (apertado no mesmo dia pela adoção do item X).

## 0. Como estas 2 curvas voltaram a ser trabalho

A retratação das provas de piso do `fig8a`/`fig8c` (commit `940a2c0` + dedup da
sessão paralela) foi **correta**: o par declarado pelo autor era o **pior dos 6
pares possíveis** da família, então o denominador honesto vem da família de 4 e
aperta para mx **0,1220**. As duas passam a falhar a prova ⇒ saem das exceções e
voltam para a **fila form-limited**, que era ZERO desde 21/08 e agora é **2**.

⚠️ **Isto não é regressão do modelo** — as métricas não mudaram um dígito. É o
instrumento de prova ficando mais rigoroso, e a fila registrando a verdade.

## 1. Diagnóstico: as duas são NÍVEL PURO, e isso as separa da fila anterior

| | `fig8a` | `fig8c` |
|---|---|---|
| pernas (lim 0,05 / 0,10 / 0,0565) | 0,0489 / **0,1320** / 0,0395 | 0,0456 / **0,1463** / 0,0386 |
| perna que manda | **res.máx 1,32×** | **res.máx 1,46×** |
| viés | −0,0489 | −0,0456 |
| **\|viés\|/MAE** | **1,00** | **1,00** |
| sinais do resíduo | `----------` (10/10) | `-----------------------` (23/23) |
| ρ(resíduo, N) | −0,61 | +0,30 |

**Resíduo de sinal único com |viés|/MAE = 1,00 exato nas duas** ⇒ erro de
**NÍVEL**, não de forma — e o modelo está **abaixo** do dado (perde rápido
demais). É a assinatura oposta da `amp0p8` (que fechou como form-limited por
esgotamento com 17 estruturas): aqui o discriminante da própria campanha diz
que **alavanca de nível ainda tem o que dar**.

## 2. A alavanca: `arrest_approach_exp`, e ela é LIVRE

Shell canônico na `fig8a` — de 9 alavancas varridas, as travadas por
procedência (`C_creep`, `k_wear_spec`, `loose_arrest_floor`) ficam de fora e
**a única livre que fecha é o expoente da comporta de arresto**:

| dose | `fig8a` | veredito |
|---|---|---|
| 1,0 (nominal) | 0,0489 / 0,1320 / 0,0395 | — |
| **1,5** | 0,0341 / 0,0797 / 0,0303 | FECHA |
| **2,0** | 0,0243 / 0,0488 / 0,0254 | FECHA |

Física: `arrest_approach_exp` governa **como a taxa de afrouxamento chega ao
auto-travamento**; 1,0 é a comporta original (aproximação linear). Expoente >1
= a junta desacelera mais tarde e mais abruptamente ao encostar no arresto.

## 3. ⛔ No GRUPO INTEIRO as duas doses REPROVAM — e é aqui que a medição salva

| dose no grupo (10 curvas) | fecham | quebram |
|---|---:|---:|
| 1,5 | 1 (`fig8a`) | **1** (`fig7c`: mx 0,0530 → 0,1036) |
| 2,0 | 2 | **4** (`fig3`, `fig7a`, `fig7b`, `fig7c`) |

⇒ saldo de censo **0** e **−2**. Constante compartilhada não serve à fonte —
o padrão que 5 fontes independentes já mostraram.

## 4. A estrutura no que quebra: é PROTOCOLO, e o dado a nomeia

As que fecham são as **duas baselines do protocolo INTERMITENTE** (série
`fig8`); as que quebram são todas das séries `typical`/`constant`
(`fig3`, `fig7a/b/c`). E dentro da própria `fig8`:

**`fig8b` e `fig8d` (as intermitentes COM axial) dão Δ = 0,0000 EXATO** em
todas as doses ⇒ **isolamento estrutural dentro do escopo**: aplicar às 4 da
`fig8` toca **só** as 2 alvo, medido e não presumido.

Escopo por protocolo tem precedente forte no projeto: foi assim que a
retratação LU de 08-14 separou §3.1.3 half-sine de §3.2 manual — e ali, como
aqui, **é o texto do paper que distingue os protocolos** (o próprio rótulo
"intermittent" das curvas).

| escopo `fig8`, dose | fecham | quebram | `fig8a` | `fig8c` |
|---|---:|---:|---|---|
| 1,75 | **2** | **0** | 0,0289/0,0639/0,0271 | 0,0310/0,0869/0,0339 |
| **2,00** | **2** | **0** | 0,0243/0,0488/0,0254 | 0,0287/0,0708/0,0341 |
| 2,25 | **2** | **0** | 0,0218/0,0482/0,0256 | 0,0256/0,0899/0,0351 |
| 2,50 | 1 | 0 | 0,0208/0,0476/0,0274 | (perde a `fig8c`) |

**Região de 3 células**, não fio de navalha. Célula **2,00** pela regra de
**CENTRALIDADE** (precedente D-I/D-AA): é a central das 3 e tem a melhor
pior-perna (**0,71×** contra 0,87× e 0,90×).

## 5. Honestidade sobre a procedência

O expoente **2,0 é FITADO-DECLARADO**, não lido: não há observável publicado
que o ancore. O que a medição sustenta é (a) a **região** de 3 células,
(b) o **escopo** por protocolo com precedente e isolamento Δ=0 medido, e
(c) **1 número para 2 curvas** — razão 2,0 curvas/constante, do lado
*model-like* da própria auditoria de integridade de hoje (que mede a mediana
do projeto e chama <2,0 de fit-like).

⚠️ **Declaro também o que NÃO é pré-registro:** eu vi os números das doses
antes de escolher a célula. A regra de centralidade é do precedente e o
cálculo está acima para ser conferido, mas o mérito de "escolhido às cegas"
esta célula não tem. Os gates do §6 é que estão congelados de fato.

## 6. Por que não está adotado — e o que falta

⛔ **A sessão paralela está com ~200 arquivos em aberto** neste momento
(regeneração do `variable_explorer` inteiro + `report_html.py` +
`validation_cases.py`). Adotar exige re-simular o store, e re-simular agora
usaria **código alheio meio-editado**, produzindo um store que não corresponde
a nenhum commit. É pior que o gotcha "nunca escrever config mid-batch": seria
carimbar um fingerprint sobre árvore instável.

Regra aplicada: **diagnóstico em paralelo, adoção em série.**

Gates congelados para quem executar (prereg
`docs/superpowers/specs/2026-08-23-eccles-fig8-arrest-exp-prereg.md`):

| # | gate | critério |
|---|---|---|
| **G1** | alvo ao dígito | `fig8a` 0,0243/0,0488/0,0254 · `fig8c` 0,0287/0,0708/0,0341 pelo canônico |
| **G2** | as 8 irmãs do ECCLES | `fig8b`/`fig8d` **bit-idênticas**; as 6 fora do escopo **bit-idênticas** |
| **G3** | isolamento | Δ = 0 nas 195 curvas de outras fontes; fingerprint único nos 210 |
| **G4** | censo | tripé 169 → **171/205** · fila form-limited 2 → **0** |
| **G5** | sincronização | docs vivos · triagem · aging · HTML das 2 páginas |

## 7. ⚠️ O QUE A GUARDA PEGOU, e fica declarado

`test_censo_que_repousa_em_piso_de_fonte_nao_cresce_calado` acusou a entrada das
duas — e **com razao**: elas fecham sob o limite **POR FONTE** (0,0565), nao sob
o global de 0,025. Sigma final: `fig8a` **0,0254** (1,02x do global) e `fig8c`
**0,0341** (1,36x).

E' propriedade da **rota**, nao da celula: nenhuma das 4 celulas medidas poe as
duas sob o global (1,75 -> 0,0271/0,0339 · 2,00 -> 0,0254/0,0341 ·
2,25 -> 0,0256/0,0351 · 2,50 -> 0,0274/-).

A regua por fonte e' a **D1, adotada em 2026-07-30**, e o piso do ECCLES foi
**re-medido e APERTADO no mesmo dia** desta adocao (0,0698 -> 0,0565, item X da
sessao paralela) — ou seja, as duas fecham contra o denominador mais rigoroso
que a fonte ja teve, e nao contra um piso frouxo. Ainda assim: quem citar
"171/205" deve saber que 2 dessas curvas repousam no limite por fonte.

## Reprodutibilidade

`py -3.12 New_Theory/ataque_curva.py eccles2010_fig8a_no_axial_baseline1`;
grades por sonda inline com `rn._effective_overrides` embrulhado (idioma do
shell); limite σ SEMPRE de `rh.limite_sres('ECCLES_2010', pisos)`, nunca de
memória.
