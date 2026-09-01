# LI_2022_TRIBOINT — o `±` da Fig. 8(d) existe, e o que ele É não é determinável

**2026-08-05** · investigação só-leitura por subagente delegado, sob o MANDATO
PERMANENTE. Fingerprint `b072b24fd3a8`. **NADA foi alterado** no store/config.

## Pergunta que motivou

A `li2022ti_axial_10Hz_full` reprova só pelo σ (0,0365 contra 0,025) e a
`axialmin_10Hz` reprova por MAE (0,0526). A Fig. 8(d) do paper mostra barras com
`±` — é piso de repetibilidade utilizável?

## 1. Existe dispersão publicada. **O que ela é, não.**

Fig. 8(d) é barra hachurada com *whiskers* de cap duplo. Medido em pixels
(calibração 62,70 px/ponto percentual, validada porque os topos leem
17,895/14,091/8,876 contra rótulos **17,9/14,1/8,9**):

| f | topo (rótulo) | whisker ↑ | whisker ↓ | assimetria |
|---|---|---:|---:|---:|
| 10 Hz | 17,895 (17,9) | +2,464 | −2,464 | **0,000** |
| 15 Hz | 14,091 (14,1) | +1,866 | −1,866 | **0,000** |
| 20 Hz | 8,876 (8,9) | +1,340 | −1,340 | **0,000** |

**O paper não diz o que é.** Legenda (p.5), literal: *"Fig. 8. … and (d) bolt
axial force drop percentage: N = 2 × 10⁵."* — nada. Texto que a discute (p.6):
nada. §2 "Experimental details" e §2.2 "Research methods": zero método
estatístico. Grep no texto completo: **zero** ocorrências de *standard deviation,
error bar, average, mean value, scatter, statistic, confidence, uncertainty,
variability, dispersion*. E o mesmo artigo usa `±` com **outros dois sentidos**,
também indefinidos: Tabela 2 (195,57 ± 1,09 GPa) e picos XPS (724,4 ± 0,2 eV —
tolerância de instrumento).

O que a medição **permite** afirmar: a simetria exata (0,000 pp) **elimina** "os
whiskers são min/máx observados" (isso seria assimétrico em torno da média com
probabilidade ~1 para n=3). Logo é **uma** estatística simétrica de dispersão —
DP, semi-amplitude ou erro padrão — e **o paper não diz qual**. Isso decide o
estatuto (§VEREDICTO).

## 2. Quantas réplicas — 3 contáveis a 10 e 15 Hz; 20 Hz indeterminável

O paper confirma a nota, literal (p.2, §2.1): *"Each group of test parameters is
repeated 3–5 times."* Sem número por condição.

Mas a **Fig. 12 plota espécimes individuais**, não médias: **3 quadrados a
10 Hz, 3 triângulos a 15 Hz, 1 círculo a 20 Hz** (contagem por componentes
conexos), este último com seta de *runout* (*"Unfractured (exceed 10⁷)"*) — e
como todo runout é censurado no mesmo x, 3–5 runouts colapsariam num símbolo ⇒
**n a 20 Hz não é contável**. Calibração validada 2×: o runout cai em 9,99e6 ≈
10⁷ e a vida mais longa a 10 Hz lê 4,16e5 ≈ os ~4,1e5 da fratura na Fig. 8(a).

⚠️ **Não usar o scatter de Sa da Fig. 12 como piso**: Sa = (Fmax−Fmin)/As varia
só **0,21 %** (10 Hz) e 0,69 % (15 Hz) entre espécimes — é **rigidez**, que
repete. A *queda* varia 13 % relativos. Grandezas diferentes. (Vidas:
2,87/3,58/4,16 ×10⁵ a 10 Hz, DP 18 %.)

## 3. Conversão para F/F₀ — exata, fator 1/100

Não precisa de hipótese, porque a base da Fig. 8(d) **é** a normalização da
campanha. Verificado na imagem, painel (c) calibrado:

| f | F(2e5) medido em px | esperado = 12,0·(1−drop/100) | Δ |
|---|---:|---:|---:|
| 10 Hz | 9,850 kN | 9,852 | −0,002 |
| 15 Hz | 10,291 kN | 10,308 | −0,017 |
| 20 Hz | 10,925 kN | 10,932 | −0,007 |

E os endpoints do store (0,8208 / 0,8583 / 0,9108) = 1 − 0,1792/0,1417/0,0892 =
**exatamente as médias da Fig. 8(d)**. Logo `ratio = 1 − drop/100` com base
constante por curva ⇒ **σ(F/F₀) = Δ(pp)/100**:

**10 Hz: 0,821 ± 0,0240** · **15 Hz: 0,859 ± 0,0190** · **20 Hz: 0,911 ± 0,0130**

σ_rep depende da convenção **e de n** (d₂ = 1,693/2,059/2,326 p/ n=3/4/5), 10 Hz:

| leitura | n=3 | n=4 | n=5 |
|---|---:|---:|---:|
| desvio-padrão | 0,0240 | 0,0240 | 0,0240 |
| semi-amplitude → σ=2Δ/d₂ | 0,0284 | 0,0233 | 0,0206 |
| erro padrão → σ=Δ√n | 0,0416 | 0,0480 | 0,0537 |

Faixa total **0,0206 – 0,0537**; a leitura DP (0,0240) fica no meio.

## 4. Dispersão em outras figuras — não existe

Fig. 8(c) é **traço único por frequência** (sem banda, sem sombreado, sem
barras); a ondulação fina do traço de 20 Hz é ruído por-ciclo de UMA corrida, não
banda. Fig. 8(a)/(b) idem. Fig. 12 plota espécimes. ⇒ **a Fig. 8(d) é a única
dispersão de réplica da grandeza de afrouxamento no artigo inteiro.**

## 5. Três achados do lado da campanha

### (a) O piso que a campanha usava era INVÁLIDO — 4ª ocorrência da chave cega

`_pisos_medidos` chaveia família por `(source, delta_mm, F_amp_N, mode)` e
**frequência não está na chave** — sendo ela a variável varrida deste paper. As
4 curvas caíam numa família só e **5 dos 6 pares cruzavam frequências**. Piso
falso: **MAE 0,0413 · máx 0,0590 · σ 0,0117** (reproduzido exato pelo helper do
report antes do conserto).

Mesma classe já retratada/bloqueada para ROUSSEAU (espessura), LU_2024
(amplitude), JCSR_2023 (ambiente), CACCESE_2009 (condição), LI_2022_MARSTRUC
(rugosidade) e QIN_2024 (corrente) — e `li2022ti_*` **não** estava em
`_SEM_FAMILIA_MECANICA`. **Consertado neste commit**: as 4 bloqueadas, o par
legítimo declarado. Efeito medido: piso → **MAE 0,0315 · máx 0,0655 · σ 0,0083**;
`limite_sres` = **0,0250 antes e depois** ⇒ **zero efeito no censo**. É o caso
"inócuo hoje não é correto" que o próprio comentário do código já nomeia para
MARSTRUC/QIN.

### (b) O único par de mesma condição, e o que ele mede de fato

`axialmin_10Hz` (Fig. 8c) × `axial_10Hz_full` (Fig. 8a): **MAE 0,0315 · máx
0,0655 · σ 0,0083** pelo método da campanha. Mas em força **ABSOLUTA** as duas
concordam em N=2e5 (**9,850 vs 9,865 kN**, 0,15 %); o gap de 0,031 é só **base**
— a Fig. 8(c) parte de 12,0 kN e o CSV da Fig. 8(a) de **11,5 kN** (seus valores
são múltiplos exatos de 1/115 ⇒ leitura em 0,1 kN com F(200)=11,5; o pixel do
traço dá 11,18). É a dispersão de aperto documentada (4 %, dentro da banda 4–14 %
da campanha) — **nível, não forma**.

⚠️ **Aberto, não decidido**: 0,15 % em força absoluta é próximo demais para dois
ensaios independentes. As duas podem ser o **mesmo ensaio em duas figuras** —
questão de `_CID_NAO_COMPARAVEL` (precedente LU `fig18_amp1p0` ≡ `fig20_T22Nm`),
que **muda o denominador**. O LU tinha prova de tabela idêntica ao dígito; aqui
não há. Registrado no código para não se perder.

### (c) O resíduo do endpoint já está NO piso; o que reprova é o MEIO da curva

`axialmin_10Hz`: resíduo **+0,0253 em N=2e5 = 1,05× σ_rep(0,0240)** — mas sobe a
**+0,0779 em N=6e4**, e é de lá que vêm MAE e res.máx. **A Fig. 8(d) só reporta
dispersão em N=2e5**, ou seja **nada** sobre a região que reprova. 15 Hz igual
(endpoint 0,63× o piso, máx 0,0486 em 4e4). 20 Hz é o inverso: endpoint 0,0643 =
**4,95×** o piso dele.

## VEREDICTO

**Existe piso utilizável, mas é de NÍVEL no endpoint** — σ ≈ **0,024** em F/F₀ a
10 Hz (0,019 a 15 Hz, 0,013 a 20 Hz), faixa 0,021–0,054 conforme a convenção. É a
primeira repetibilidade genuína desta fonte. **E o que o `±` é não é determinável
do paper** — o que é decisivo, porque o estatuto depende da convenção:

| barra | 3ª perna: `axial_10Hz_full` σ 0,0365 passa? | prova de piso: `axialmin_10Hz` MAE 0,0526? |
|---|---|---|
| par válido 10 Hz (σ 0,0083 / MAE 0,0315) | **NÃO** (limite fica 0,0250) | NÃO (1,67×) |
| Fig8d como DP (0,0240) | NÃO | NÃO (par-a-par 0,0271 → 1,94×) |
| Fig8d como semi-amplitude (0,0206–0,0284) | NÃO | NÃO (0,0233–0,0320) |
| Fig8d como **erro padrão** (0,0416–0,0537) | **SIM** | **SIM se n≥4** (0,0541–0,0606) |

Sob DP ou semi-amplitude **nenhuma das duas muda de estatuto**; só a leitura
"erro padrão da média" viraria as duas — e é a leitura menos provável (barra de
erro padrão em n=3 é convenção de biologia, não de mecânica experimental), além
de ser a que **nos favorece**, o que exige mais evidência, não menos.

**E há um erro de DIMENSÃO no caminho todo**: usar 0,024 (dispersão de **nível**
num ponto) como piso de **σ_res** (dispersão de **forma** do resíduo ao longo da
curva) é exatamente o que o §3 do `piso_repetibilidade_medido.md` adverte — *"a
perna de σ_res e a de MAE têm pisos de natureza diferente"*. O piso de σ_res
**medido** desta fonte é 0,0083 (único par válido) e **não move** a
`axial_10Hz_full`.

## Fila (nenhuma é medição)

* **Decisão do professor**: aceitar a Fig. 8(d) como piso de **MAE/nível** (não de
  σ_res) para esta fonte? Sob qual convenção? A campanha não tem precedente de
  piso lido de barra de erro **de sentido não declarado**.
* Aberto: `axialmin_10Hz` ≡ `axial_10Hz_full` (mesmo ensaio em 2 figuras)? Muda o
  denominador; exige prova do nível da que o LU teve.
* A `axial_10Hz_full` segue **σ-bound** e a `axialmin_10Hz` **MAE-bound** — duas
  curvas do MESMO ensaio com demandas OPOSTAS (menos perda tardia vs mais perda).
  É o limite declarado da adoção D-Q, e nenhuma constante serve às duas.
