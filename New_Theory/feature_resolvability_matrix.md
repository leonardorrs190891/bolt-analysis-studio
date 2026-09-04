# Matriz de RESOLUBILIDADE de features — a amostragem resolve o que a âncora precisa?

**Gerado por `New_Theory/build_feature_resolvability.py`** (2026-07-30).
Sucessora da matriz de âncoras (D2b): aquela perguntou se a âncora *existe*
na matriz de ensaios; esta pergunta se a **amostragem** da curva resolve a
feature de que a âncora depende. Critérios no docstring do script,
declarados antes de olhar qualquer fonte.

| feature | o que ela ancora | critério de resolução |
|---|---|---|
| queda inicial | `emb` data-implícito (L24) | 2º ponto em N ≤ 1 % do último |
| joelho | `slip_onset_W` (incubação) | 1º ponto < 0,95 ainda ≥ 0,85 |
| platô final | `loose_arrest_floor` | excursão ≤ 0,02 na cauda de 5 % |

| fonte | curvas | fora | canal dominante | queda | joelho | platô | veredicto | motivo |
|---|---:|---:|---|---:|---:|---:|:--:|---|
| `BAUER_2024` | 9 | 9 | rotational_loosening | 1/9 | 9/9 | 3/9 | **CONSTRANGIVEL** | precisa de *joelho*: resolvida em 9/9 |
| `CACCESE_2009` | 7 | 3 | creep | 7/7 | 3/7 | 7/7 | **fora do escopo** | canal creep: ancora nao e' feature de curva |
| `CHU_2026` | 9 | 8 | wear | 0/9 | 8/8 (+1 n/a) | 7/9 | **fora do escopo** | canal wear: ancora nao e' feature de curva |
| `ECCLES_2010` | 10 | 7 | rotational_loosening | 1/10 | 9/10 | 9/10 | **CONSTRANGIVEL** | precisa de *joelho*: resolvida em 9/10 |
| `GRZEJDA_2026` | 2 | 0 | — | 0/2 | — (+2 n/a) | 2/2 | **n/a** | fonte fechada |
| `ICMEZ_2025` | 8 | 5 | rotational_loosening | 4/8 | 8/8 | 1/8 | **CONSTRANGIVEL** | precisa de *joelho*: resolvida em 8/8 |
| `JCSR_2023` | 5 | 4 | creep | 0/5 | 4/4 (+1 n/a) | 5/5 | **fora do escopo** | canal creep: ancora nao e' feature de curva |
| `KARLSEN_2022` | 11 | 6 | rotational_loosening | 0/11 | 9/10 (+1 n/a) | 4/11 | **CONSTRANGIVEL** | precisa de *joelho*: resolvida em 9/10 |
| `LIU_2016` | 14 | 5 | embedding | 14/14 | 11/14 | 14/14 | **CONSTRANGIVEL** | precisa de *queda*: resolvida em 14/14 |
| `LIU_2017_AXIAL` | 9 | 0 | — | 9/9 | 8/8 (+1 n/a) | 9/9 | **n/a** | fonte fechada |
| `LIU_2020_WEAR` | 9 | 1 | embedding | 9/9 | 3/3 (+6 n/a) | 9/9 | **CONSTRANGIVEL** | precisa de *queda*: resolvida em 9/9 |
| `LIU_2022_RETIGHT` | 21 | 3 | embedding | 0/21 | 14/14 (+7 n/a) | 20/21 | **PRECISA DE DADO** | precisa de *queda*: resolvida em 0/21 — minoria |
| `LIU_2025` | 7 | 4 | fatigue | 6/7 | 7/7 | 0/7 | **fora do escopo** | canal fatigue: ancora nao e' feature de curva |
| `LI_2022_MARSTRUC` | 6 | 0 | — | 0/6 | — (+6 n/a) | 6/6 | **n/a** | fonte fechada |
| `LI_2022_TRIBOINT` | 4 | 2 | embedding | 0/4 | 4/4 | 3/4 | **PRECISA DE DADO** | precisa de *queda*: resolvida em 0/4 — minoria |
| `LU_2024` | 10 | 10 | embedding | 0/10 | 0/10 | 9/10 | **PRECISA DE DADO** | precisa de *queda*: resolvida em 0/10 — minoria |
| `QIN_2024` | 3 | 0 | — | 0/3 | 3/3 | 3/3 | **n/a** | fonte fechada |
| `ROUSSEAU_2025` | 6 | 5 | rotational_loosening | 0/6 | 6/6 | 2/6 | **CONSTRANGIVEL** | precisa de *joelho*: resolvida em 6/6 |
| `SUN_2025_CRIMP` | 8 | 2 | rotational_loosening | 5/8 | 7/7 (+1 n/a) | 4/8 | **CONSTRANGIVEL** | precisa de *joelho*: resolvida em 7/7 |
| `SUN_2025_REASSY` | 5 | 0 | — | 5/5 | 5/5 | 5/5 | **n/a** | fonte fechada |
| `ANCORA_INTERNA` | 3 | 3 | rotational_loosening | 3/3 | 3/3 | 2/3 | **CONSTRANGIVEL** | precisa de *joelho*: resolvida em 3/3 |
| `YANG_2019` | 5 | 5 | embedding | 0/5 | 5/5 | 0/5 | **PRECISA DE DADO** | precisa de *queda*: resolvida em 0/5 — minoria |
| `YANG_2021` | 6 | 4 | embedding | 1/6 | 6/6 | 0/6 | **PRECISA DE DADO** | precisa de *queda*: resolvida em 1/6 — minoria |
| `YANG_2023_AME` | 1 | 1 | embedding | 0/1 | 1/1 | 1/1 | **PRECISA DE DADO** | precisa de *queda*: resolvida em 0/1 — minoria |
| `YANG_2023_IJPEM` | 9 | 7 | rotational_loosening | 1/9 | 6/9 | 2/9 | **CONSTRANGIVEL** | precisa de *joelho*: resolvida em 6/9 |
| `ZHANG_2006` | 2 | 1 | creep | 2/2 | 2/2 | 2/2 | **fora do escopo** | canal creep: ancora nao e' feature de curva |
| `ZHANG_2018` | 9 | 3 | embedding | 7/9 | 8/8 (+1 n/a) | 9/9 | **CONSTRANGIVEL** | precisa de *queda*: resolvida em 7/9 |
| `ZHANG_2019` | 4 | 0 | — | 2/4 | 4/4 | 4/4 | **n/a** | fonte fechada |

## Resumo

* **CONSTRANGIVEL**: 11 fontes
* **n/a**: 6 fontes
* **PRECISA DE DADO**: 6 fontes
* **fora do escopo**: 5 fontes

## O pedido de bancada que a matriz produz

As fontes **PRECISA DE DADO** são todas dominadas por *embedding* com a
queda inicial não amostrada — nenhum modelo lê `emb` de uma curva cujo
2º ponto está a >1 % do ensaio. O que destrava cada uma é **amostragem
inicial fina** (pontos em N ≤ 1 % do total), não física nova:

* `LIU_2022_RETIGHT` — queda resolvida em 0/21, 3 de 21 curvas fora
* `LI_2022_TRIBOINT` — queda resolvida em 0/4, 2 de 4 curvas fora
* `LU_2024` — queda resolvida em 0/10, 10 de 10 curvas fora
* `YANG_2019` — queda resolvida em 0/5, 5 de 5 curvas fora
* `YANG_2021` — queda resolvida em 1/6, 4 de 6 curvas fora
* `YANG_2023_AME` — queda resolvida em 0/1, 1 de 1 curvas fora

## Limites declarados desta matriz

* **O critério de platô é conservador em curva esparsa, e há uma medição
  que o contradiz:** ele marca o platô do `YANG_2023_IJPEM` como não
  resolvido (2/9), mas o G5 do prereg do par **mediu** que o piso lido
  daquelas caudas descreve 6 curvas como constante única (lei). Com ~7
  pontos por curva, a janela de cauda tem 2 pontos e a excursão entre
  eles excede 0,02 mesmo numa cauda que está achatando. A tolerância
  **não foi afrouxada depois de ver o resultado** — fica o registro da
  tensão: este critério é um *piso* de confiança, não um veto; onde ele
  reprova, a leitura do platô exige o teste de lei (G5-do-par) antes de
  ser usada.
* Fontes rotacionais precisam de **joelho E platô** (o trio precisou do
  W, o par precisou do piso). O veredicto usa o joelho por ser a âncora
  mais escassa; o platô está na coluna própria.
* Curva que nunca cai abaixo de 0,95 tem joelho **n/a** (nada a
  localizar) — não conta contra a fonte.
* `fora do escopo` ≠ resolvido: são os canais cuja âncora **não é
  feature de curva** (creep = ensaio dedicado; wear = sem prior;
  fatigue = input de paper), herdados da D2b.
