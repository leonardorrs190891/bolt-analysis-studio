# Matriz de cobertura de ANCORAS — a otimizacao principal e' calibravel onde?

**Gerado por `New_Theory/build_anchor_coverage.py`** (2026-07-29). Cada linha
e' uma fonte do censo; a coluna final diz se o LIMIAR da forma que aquela
fonte precisa tem ancora com procedencia, ou se calibrar ali seria **fit**.

Critérios declarados ANTES de medir — ver o docstring do script. Resumo:

* afrouxamento -> `s_crit_loose` exige **varredura de amplitude no mesmo rig**
  (>=3 amplitudes = FORTE; 2 = FRACO; 1 = NAO). `FORTE` (sem sufixo) marca
  que existe curva **sub-critica** na varredura, logo o limiar esta DENTRO
  dela e nao extrapolado.
* embedding -> prior `N_emb` **e** queda inicial resolvida no dado
  (2o ponto em N <= 1% do ultimo N).
* creep -> `C_creep` e' **por par** com ICs disjuntos: exige ensaio estatico
  dedicado, nao ha ancora na biblioteca.
* wear -> **nao ha** prior de ancora; a banda de Shipway e' check (L7).

| fonte | curvas | fora | canal dominante das fora | n amp | n F0 | nota aparato | piso σ | ancora | motivo |
|---|---:|---:|---|---:|---:|:--:|---:|:--:|---|
| `BAUER_2024` | 9 | 9 | rotational_loosening | 2 | 2 | sim | 0.0900 | **FRACO** | 2 amplitudes: da direcao, nao o valor do limiar |
| `CACCESE_2009` | 7 | 3 | creep | 0 | 4 | sim | 0.0270 | **PRECISA ENSAIO** | C_creep e' POR PAR (ICs disjuntos, sec4.7) — exige creep estatico do mesmo par |
| `CHU_2026` | 9 | 8 | wear | 5 | 3 | sim | 0.0507 | **NAO** | sem prior de ancora; banda de Shipway e' CHECK informacional, nao limiar |
| `ECCLES_2010` | 10 | 7 | rotational_loosening | 1 | 1 | sim | 0.0828 | **NAO** | 1 amplitude(s) — limiar seria FITADO |
| `GRZEJDA_2026` | 2 | 0 | — | 0 | 1 | sim | 0.0009 | **n/a** | fonte fechada — nao precisa de forma nova |
| `ICMEZ_2025` | 8 | 5 | rotational_loosening | 2 | 2 | sim | 0.0574 | **FRACO** | 2 amplitudes: da direcao, nao o valor do limiar |
| `JCSR_2023` | 5 | 4 | creep | 0 | 1 | sim | 0.2214 | **PRECISA ENSAIO** | C_creep e' POR PAR (ICs disjuntos, sec4.7) — exige creep estatico do mesmo par |
| `KARLSEN_2022` | 11 | 6 | rotational_loosening | 2 | 9 | sim | 0.1742 | **FRACO** | 2 amplitudes: da direcao, nao o valor do limiar |
| `LIU_2016` | 14 | 5 | embedding | 0 | 5 | sim | 0.0176 | **FORTE** | prior N_emb + queda inicial resolvida em 14/14 curvas |
| `LIU_2017_AXIAL` | 9 | 0 | — | 0 | 5 | sim | 0.0120 | **n/a** | fonte fechada — nao precisa de forma nova |
| `LIU_2020_WEAR` | 9 | 1 | embedding | 4 | 4 | sim | 0.0018 | **FORTE** | prior N_emb + queda inicial resolvida em 9/9 curvas |
| `LIU_2022_RETIGHT` | 21 | 3 | embedding | 1 | 4 | sim | 0.0125 | **NAO** | queda inicial NAO resolvida no dado (0 de 21 curvas com 2o ponto <=1% do N) |
| `LIU_2025` | 7 | 4 | fatigue | 6 | 1 | sim | 0.0149 | **INPUT DE PAPER** | N_f por curva do artigo (rota E2 adotada, sec4.53) — nao precisa de limiar calibrado |
| `LI_2022_MARSTRUC` | 6 | 0 | — | 0 | 3 | sim | 0.0023 | **n/a** | fonte fechada — nao precisa de forma nova |
| `LI_2022_TRIBOINT` | 4 | 2 | embedding | 0 | 1 | sim | 0.0117 | **NAO** | queda inicial NAO resolvida no dado (0 de 4 curvas com 2o ponto <=1% do N) |
| `LU_2024` | 10 | 10 | embedding | 5 | 6 | sim | — | **NAO** | queda inicial NAO resolvida no dado (0 de 10 curvas com 2o ponto <=1% do N) |
| `QIN_2024` | 3 | 0 | — | 0 | 3 | sim | 0.0019 | **n/a** | fonte fechada — nao precisa de forma nova |
| `ROUSSEAU_2025` | 6 | 5 | rotational_loosening | 3 | 3 | sim | 0.1859 | **FORTE-** | 3 amplitudes distintas |
| `SUN_2025_CRIMP` | 8 | 2 | rotational_loosening | 1 | 1 | sim | 0.0663 | **NAO** | 1 amplitude(s) — limiar seria FITADO |
| `SUN_2025_REASSY` | 5 | 0 | — | 1 | 1 | sim | 0.0120 | **n/a** | fonte fechada — nao precisa de forma nova |
| `ANCORA_INTERNA` | 3 | 3 | rotational_loosening | 1 | 3 | **NAO** | — | **NAO** | 1 amplitude(s) — limiar seria FITADO |
| `YANG_2019` | 5 | 5 | embedding | 3 | 5 | sim | — | **NAO** | queda inicial NAO resolvida no dado (0 de 5 curvas com 2o ponto <=1% do N) |
| `YANG_2021` | 6 | 4 | embedding | 5 | 1 | sim | 0.0155 | **FRACO** | queda inicial resolvida em so 1/6 curvas — ancora de minoria, nao da fonte |
| `YANG_2023_AME` | 1 | 1 | embedding | 0 | 1 | sim | — | **NAO** | queda inicial NAO resolvida no dado (0 de 1 curvas com 2o ponto <=1% do N) |
| `YANG_2023_IJPEM` | 9 | 7 | rotational_loosening | 9 | 2 | sim | — | **FORTE** | 9 amplitudes distintas + curva sub-critica na varredura |
| `ZHANG_2006` | 2 | 1 | creep | 2 | 2 | sim | — | **PRECISA ENSAIO** | C_creep e' POR PAR (ICs disjuntos, sec4.7) — exige creep estatico do mesmo par |
| `ZHANG_2018` | 9 | 3 | embedding | 1 | 3 | sim | 0.0056 | **FORTE** | prior N_emb + queda inicial resolvida em 7/9 curvas |
| `ZHANG_2019` | 4 | 0 | — | 1 | 1 | sim | 0.0063 | **n/a** | fonte fechada — nao precisa de forma nova |

## Resumo

* **NAO**: 9 fontes
* **n/a**: 6 fontes
* **FRACO**: 4 fontes
* **FORTE**: 4 fontes
* **PRECISA ENSAIO**: 3 fontes
* **INPUT DE PAPER**: 1 fontes
* **FORTE-**: 1 fontes

## A leitura — e ela é desconfortável

Das **22** fontes que precisam de forma nova, só **5** têm âncora sólida (FORTE/FORTE-). **9** são **NÃO ancoráveis**: calibrar o limiar ali seria *fit*, não procedência — e é exatamente a parede em que a adoção do LIU_2025 bateu (relógio ±36 % contra ≤5 % exigido).

**Ordem de ataque que a matriz sugere** (âncora sólida × curvas fora):

1. **`YANG_2023_IJPEM`** — 7 curvas fora, canal *rotational_loosening*, âncora **FORTE** (9 amplitudes distintas + curva sub-critica na varredura)
1. **`ROUSSEAU_2025`** — 5 curvas fora, canal *rotational_loosening*, âncora **FORTE-** (3 amplitudes distintas)
1. **`LIU_2016`** — 5 curvas fora, canal *embedding*, âncora **FORTE** (prior N_emb + queda inicial resolvida em 14/14 curvas)
1. **`ZHANG_2018`** — 3 curvas fora, canal *embedding*, âncora **FORTE** (prior N_emb + queda inicial resolvida em 7/9 curvas)
1. **`LIU_2020_WEAR`** — 1 curvas fora, canal *embedding*, âncora **FORTE** (prior N_emb + queda inicial resolvida em 9/9 curvas)

**O incômodo:** as duas piores fontes do conjunto **não** estão nessa lista. O `LU_2024` (10/10 fora) é dominado por embedding e a queda inicial **não está resolvida** em nenhuma das 10 curvas; o `ECCLES_2010` (7 fora) tem **uma única amplitude**, logo o limiar seria fitado. Nas duas, nenhuma forma pode ser calibrada com procedência a partir do que a biblioteca tem — o que falta é **dado**, não modelo.

**Consequência de método:** a otimização principal não é uma campanha sobre as 98 curvas fora. É uma campanha sobre as fontes com âncora, com **transferência zero-refit** para as demais — que é o teste que de fato distingue forma de ajuste. Onde a transferência falhar e não houver âncora, a saída honesta é exceção com prova ou pedido de dado, não calibração.
