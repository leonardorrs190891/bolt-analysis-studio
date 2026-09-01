# As 5 DATA-LIMITED — exceção **provada**, não alegada

**Data:** 2026-07-28 · **Store:** `4f5bedfbace4` (snapshot do HEAD) ·
**Só-leitura: nenhuma simulação, nenhum fit, nada escrito em store nem em
`adopted_configs.json`.**

[`frontier_classes.md`](frontier_classes.md) classificou 5 das 55 curvas fora do
tripé como **DATA-LIMITED**, com a ação *"nada a fazer no modelo: a meta está
abaixo da reprodutibilidade do ensaio"*. Isto **prova** essa afirmação, para as
duas sub-classes, e entrega o número que a decisão §4.1 do
[relatório executivo](../docs/MANUAL_BAS_V2/00-relatorio-executivo.md) precisa
para deixar de ser assinatura sob palavra.

---

## 1. Bauer 2024 fig6 (4 curvas) — prova por **impossibilidade**

A fonte publica **6 réplicas da mesma condição nominal** (M8). Hoje, no store:

| réplica | MAE | maxerr | tripé |
|---|--:|--:|:--:|
| rep1 | 0,043 | 0,126 | ✗ |
| rep2 | 0,042 | 0,086 | ✅ |
| rep3 | 0,034 | 0,070 | ✅ |
| rep4 | 0,078 | 0,171 | ✗ |
| rep5 | 0,049 | 0,112 | ✗ |
| rep6 | 0,076 | 0,130 | ✗ |

### O argumento

Se as réplicas discordam **entre si**, existe um piso para o `maxerr` de
**qualquer** curva de modelo: a curva que minimiza o pior erro contra um conjunto
é a **midrange** ponto-a-ponto, e o erro dela contra a réplica mais distante é
exatamente **metade da dispersão**. Logo:

> `maxerr` do melhor modelo concebível ≥ ½ · max(dispersão entre réplicas)

Não é um argumento sobre o nosso modelo. É sobre **qualquer** modelo, inclusive um
perfeito.

> **Correção de método (2026-07-28, mesmo dia).** A desigualdade acima está certa e
> sustenta *"ao menos um membro necessariamente viola"*. O que **não** se segue dela
> — e este documento usou indevidamente — é tratar *"quantas réplicas a midrange
> satisfaz"* como **teto de passes**: a midrange minimiza o erro **máximo**, não
> maximiza a **contagem**. O teto correto é o tamanho do **maior subconjunto cuja
> dispersão ponto-a-ponto seja ≤ 0,20**, por busca exaustiva. Para **este** grupo os
> dois métodos coincidem em **3 de 6** (o subconjunto viável é `rep2`/`rep3`/`rep4`),
> então **nenhum número desta seção muda** — mas no grupo `fig8` do
> [outro documento](replicate_impossibility_sweep_2026-07-28.md) a diferença foi
> material (0 → 2 de 3). Detalhe e contabilidade corrigida: errata no topo daquele
> documento.

### Medido, na janela pontuada por TODAS as 6 (`N` ∈ [0, 126])

| | valor |
|---|--:|
| **meia-dispersão máxima** | **0,2294** |
| ciclos da grade com meia-dispersão > 0,10 | **94 / 200 (47 %)** |
| par mais distante (janela crua [0,150]) | **0,5613** — rep1 vs rep6 |
| par passa-vs-falha mais distante | **0,3279** — rep2 (✅) vs rep6 (✗) |

A janela é a **pontuada**, não a crua: `metric_x` mostra que 5 das 6 são trimadas
(rep1 em N=126, que é o que fecha a janela), e o teste foi refeito dentro dela
justamente para não inflar o número. Na janela crua [0, 150] a meia-dispersão é
**0,2807**; dentro da pontuada, **0,2294**. **A conclusão é a mesma nas duas.**

### O teto da família: **3 de 6**

Erro da melhor curva possível (midrange) contra cada réplica:

| réplica | maxerr vs midrange | veredicto |
|---|--:|:--:|
| rep2 | 0,0483 | ✅ |
| rep3 | 0,0561 | ✅ |
| rep4 | 0,0574 | ✅ |
| rep5 | 0,2112 | ✗ |
| rep1 | 0,2807 | ✗ |
| rep6 | 0,2807 | ✗ |

**3 de 6.** E o teto não é artefato da midrange: a mediana ponto-a-ponto dá **3**,
e colar exatamente na melhor réplica dá **3**. Nenhuma curva única passa de 3.

**Consequência para a decisão:** o modelo está hoje em **2 de 6**, contra um teto
de **3**. Portanto

- **pelo menos 3 das 6 têm de ser exceção** — por necessidade matemática, sem
  apelo a limitação de modelo;
- há **exatamente 1 curva de folga** entre o estado atual e o máximo teórico.

**Refinamento que o classificador não tinha:** das 4 marcadas DATA-LIMITED, a
**rep4 é recuperável em princípio** (maxerr 0,0574 contra a midrange — passa). As
provadamente inalcançáveis são **rep1, rep5 e rep6**. Ou seja: 3 exceções
necessárias + 1 curva que uma melhoria legítima poderia trazer.

---

## 2. Yang 2023 IJPEM 0,50 mm (1 curva) — resolução mais grossa que a meta

`10_Yang_2023_phenomenological_model__0_50_mm__9` (MAE 0,156 · maxerr 0,274). A
curva digitalizada tem **6 pontos**:

| N | 0 | 2 | 5 | 10 | 20 | 50 |
|---|--:|--:|--:|--:|--:|--:|
| F/F₀ | 1,000 | 0,750 | 0,520 | 0,300 | 0,120 | 0,020 |

Saltos entre pontos **consecutivos do dado**: mediana **0,22**, máximo **0,25**.

> **Em 4 dos 5 intervalos, o passo do próprio dado é maior que a tolerância
> inteira da meta (0,10).**

Entre dois pontos medidos, o dado **não restringe** a curva a menos de ~0,22 —
então um resíduo de 0,10 ali não é informação sobre o modelo, é informação sobre o
espaçamento da amostragem. E o `maxerr` cai em **N = 5**, exatamente no trecho
mais íngreme, onde os intervalos vizinhos valem 0,23 e 0,22.

**Ação correta:** redigitalizar mais fino (se a figura do artigo permitir) ou
aceitar exceção. Ajustar o modelo contra esta curva é ajustar contra o
digitalizador.

---

## 3. O que isto entrega para a decisão §4.1

| curva | classe | status da prova |
|---|---|---|
| `bauer2024_M8_fig6_rep1` | scatter de réplica | **provadamente inalcançável** (0,2807 vs midrange) |
| `bauer2024_M8_fig6_rep6` | scatter de réplica | **provadamente inalcançável** (0,2807) |
| `bauer2024_M8_fig6_rep5` | scatter de réplica | **provadamente inalcançável** (0,2112) |
| `bauer2024_M8_fig6_rep4` | scatter de réplica | **recuperável em princípio** (0,0574) — não é exceção necessária |
| `10_Yang_2023_..._0_50_mm__9` | resolução grossa | **meta abaixo do passo do dado** em 4/5 intervalos |

São **4 exceções com prova** (3 por impossibilidade + 1 por resolução), e **1
curva (rep4) que sai da lista** — ela falha hoje, mas nada prova que precise
falhar.

---

## 4. Caveats

- A prova é sobre **`maxerr`**, que é o gargalo declarado da meta (34 das 55
  violam só o pico). Ela **não** afirma nada sobre o MAE de cada réplica.
- As curvas foram normalizadas por seu **próprio primeiro ponto**, a mesma âncora
  que a métrica usa (`align`). Nenhuma re-interpolação foi feita sobre grade
  amostrada: a leitura é do CSV cru via `load_full_curve`, e a comparação vive
  numa grade densa de 200 pontos dentro da janela comum.
- Parte da dispersão entre réplicas **poderia** vir do digitalizador, não do
  ensaio. Contra isso: a dispersão máxima é **0,56 em F/F₀** entre rep1 e rep6 —
  não há erro de leitura de gráfico dessa magnitude. É scatter de espécime, que é
  precisamente o que réplicas publicadas existem para mostrar.
- O número de espécime-scatter aqui é do **Bauer**; não confundir com o scatter
  do Liu 2025 discutido no prereg da rampa (fonte e valor diferentes).
