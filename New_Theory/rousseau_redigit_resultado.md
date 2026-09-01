# D-R — ROUSSEAU_2025 re-digitalizado do vetor: **+2 no tripé**

**2026-08-05** · prereg
`docs/superpowers/specs/2026-08-05-rousseau-redigitalizacao-prereg.md`. Classe
**dado**. Fingerprint **não muda** (`b70276f2fa43`) — o hash cobre `shared` +
configs adotadas, não os CSVs.

Estava bloqueado pela regra de escritor único enquanto o **D-Q** voava; liberado
assim que D-Q e D-S fecharam.

## Atribuição polilinha→curva: objetiva, e ela sozinha denuncia o defeito

As Figs. 4 e 5 são polilinhas vetoriais. A Fig. 4 tem **6** objetos e a Fig. 5
tem **5**, porque as duas plotam **força e rotação em eixos gêmeos**; separei por
critério objetivo no eixo esquerdo (força começa perto do máximo, rotação em ~0):
**3 de força** na Fig. 4 e **2** na Fig. 5 — coerente com o prereg, que já
declarava o Fb do aço 14 mm como **raster**.

A atribuição foi feita por **menor RMS contra a CSV vigente após normalizar cada
série pelo próprio 1º ponto** — nunca a olho:

| curva | polilinha | RMS | 2ª melhor | razão |
|---|---:|---:|---:|---:|
| `hdpe_t10` | #0 (fig4) | 0,0116 | 0,1395 | 11,98× |
| `hdpe_t12` | #1 (fig4) | 0,0133 | 0,1586 | 11,88× |
| `hdpe_t14` | #2 (fig4) | 0,0094 | 0,3687 | 39,16× |
| **`steel_t10`** | #0 (fig5) | **0,0960** | 0,3499 | 3,64× |
| `steel_t12` | #1 (fig5) | 0,0193 | 0,4168 | 21,62× |

Todas inequívocas (razão ≥ 3,6×). E note o que a coluna RMS diz **sem que eu
tenha perguntado**: a `steel_t10` está a **0,0960** contra 0,0094–0,0193 nas
outras quatro — **5× fora**. É evidência independente de que é a CSV **dela** que
não casa o próprio traço, confirmando o achado que motivou o prereg (6 passos
consecutivos idênticos a 4 decimais, σ 5e-5 = uma reta sobre um colapso convexo).

## Gates

* **G1 fidelidade + RETIDÃO** ✅ — o desvio-padrão dos passos na região de
  colapso é **> 0,001** nas cinco saídas (0,0039 a 0,0361). A CSV velha da
  `steel_t10` dava **0,000050**.
* **G3 isolamento** ✅ — as **3** curvas do ROUSSEAU fora de escopo
  (`hdpe_t10_amp0p2`, `steel_t10_amp0p2`, `steel_t14`) saem **bit-idênticas**.
* **G5 declarado** ✅ — o `steel_t14` (Fb raster, 1479×151) **não** foi
  re-digitalizado.
* **G2** ✅ — a métrica pode piorar, e piorou onde tinha de piorar.

## Resultado, contra a predição registrada

| curva | MAE b→a | res.máx a | σ b→a | previsto (mae/mx/σ) | |
|---|---|---:|---|---|---|
| `hdpe_t10` | 0,0919→0,0927 | 0,1786 | 0,0712→0,0691 | 0,1144/0,2028/0,0711 | fora |
| `hdpe_t12` | 0,0527→0,0566 | 0,1133 | 0,0537→**0,0456** | 0,0570/0,1132/0,0534 | fora |
| **`hdpe_t14`** | 0,0440→**0,0413** | **0,0636** | 0,0299→**0,0211** | 0,0378/0,0637/0,0255 | **ENTROU** |
| `steel_t10` | 0,0725→**0,1548** | 0,2702 | 0,0803→0,0994 | 0,1259/0,2396/0,0991 | fora |
| **`steel_t12`** | 0,0451→**0,0104** | **0,0364** | 0,0292→**0,0138** | 0,0312/0,0486/0,0179 | **ENTROU** |

**+2, não +1.** O prereg previa a `steel_t12` entrando e a `hdpe_t14` ficando
**2 % curta** (σ previsto 0,0255 contra limite 0,025); medida, ela veio a
**0,0211** e entrou. Erro máximo da predição por curva: **0,0044 a 0,0306**.

A `steel_t10` — a curva cuja correção motivou tudo — **piora de 0,0725 para
0,1548**. É o preço declarado por escrito antes de medir: *corrigir o referencial
piora o placar*, e o precedente (a própria `hdpe_t10` desta fonte, corrigida em
2026-08-02 saindo de MAE 0,058 para 0,101) manda fazer.

## ⚠️ Escolha de grade, declarada e NÃO tomada

As CSVs novas mantêm a **grade de abscissas antiga** (8–14 pontos em quatro das
cinco), reamostrando o vetor nela — **não** os 391–398 pontos que o paper publica
e que o prereg cita como motivação.

**Motivo de método, não de conveniência:** as estimativas do prereg foram
calculadas **nessa grade** (reusando `metric_pred`/`metric_x` do store e
substituindo `metric_data`). Trocar a grade nesta execução tornaria a **predição
registrada não-testável** — que é o único gate que mede se eu previ certo. E o
próprio prereg avisa que a grade densa *"muda a janela da métrica, a âncora de
alinhamento e o `n_max` do `FLOOR_TRIM`"*.

**Fica DISPONÍVEL e não tomada:** re-amostrar na densidade real do paper é
mudança de outra natureza (muda quantos pontos a métrica pontua, e portanto o
próprio σ_res) e merece **prereg próprio**. Registrado aqui para não se perder.

## Censo

| | antes | depois |
|---|---|---|
| tripé (estrita) | 136/205 | **138/205** |
| indecidíveis "sem piso" | 7 | **5** |
| fila form-limited | 1 | **1** (inalterada) |

As duas que entraram eram do ROUSSEAU — a fonte cujo rótulo *"indecidível: falta
réplica"* eu havia medido estar **vencido** (o paper publica uma corrida por
condição; não é pendência, é impossibilidade). Elas saíram da categoria por
**mérito**, não por reclassificação.

## O que continua fora, e por quê

* `steel_t10` (0,1548) e `hdpe_t10` (0,0927): as duas curvas de **10 mm**, as
  mais finas, onde o colapso é mais violento. `hdpe_t10` mal se moveu
  (0,0919→0,0927) porque já havia sido corrigida em 2026-08-02.
* `steel_t10_amp0p2` (0,0957): fora de escopo desta correção (é da Fig. 6).
* Todas as três seguem **sem piso de repetibilidade obtenível** — o paper publica
  **uma corrida por condição** (medido: varredura de texto por
  *repeat/average/std/scatter/error bar/variability* devolve zero).
