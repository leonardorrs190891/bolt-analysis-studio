# A fila form-limited é **3 curvas**, e as três têm causa DIFERENTE e MEDIDA

**2026-08-05** · sondas só-leitura, store `b072b24fd3a8`. Nada escrito no store,
config ou CSV.

Triagem (`New_Theory/regra_de_parada_triagem.py`, 3ª perna POR FONTE):
tripé **134/205** · fora **71** · das fora: 25 exceção assinada, 15 declarada,
21 classe-de-parada, 7 indecidível (falta réplica) e **3 form-limited** — o único
alvo legítimo.

| curva | MAE | ×lim | res.máx | ×lim | σ_res | ×lim | perna que manda |
|---|---:|---:|---:|---:|---:|---:|---|
| `li2022ti_axialmin_10Hz` | 0,0526 | **1,05** | 0,0779 | 0,78 | 0,0242 | 0,97 | **MAE** |
| `caccese2009_tapered_45kN_rep2` | 0,0292 | 0,58 | 0,0468 | 0,47 | 0,0258 | **1,03** | **σ** |
| `li2022ti_axial_10Hz_full` | 0,0317 | 0,63 | 0,0517 | 0,52 | 0,0365 | **1,46** | **σ** |

## A decomposição que separa as três

`RMSE² = viés² + σ_res²`, e σ_res é **invariante por translação** — então
subtrair o viés mostra o que sobra de FORMA:

| curva | MAE | viés | σ_res | MAE s/ viés | res.máx s/ viés | passaria s/ viés? |
|---|---:|---:|---:|---:|---:|---|
| `axialmin_10Hz` | 0,0526 | **+0,0526** | 0,0242 | **0,0199** | 0,0526 | **SIM (3/3)** |
| `caccese rep2` | 0,0292 | +0,0195 | 0,0258 | 0,0244 | 0,0398 | não (σ) |
| `axial_10Hz_full` | 0,0317 | +0,0058 | 0,0365 | 0,0325 | 0,0499 | não (σ) |

⇒ **as três causas são de classes distintas**, e nenhuma é "o modelo erra a
forma" em geral.

---

## ⚠️ CORREÇÃO à leitura de §1, medida depois de escrevê-la

Escrevi abaixo que a `axialmin_10Hz` é **nível puro** e que "falta ~5,3 % de
perda" — o que sugere um **lever de nível** (uma constante de magnitude). **A
descrição do resíduo está certa; o remédio implicado está ERRADO**, e a medição
que corrige é de uma linha:

| curva | f (Hz) | viés | **perda do DADO** | **perda do MODELO** | razão |
|---|---:|---:|---:|---:|---:|
| `axialmin_10Hz` | 10 | **+0,0526** | 0,1792 | **0,1539** | **0,859** |
| `axialmin_15Hz` | 15 | +0,0271 | 0,1417 | **0,1537** | 1,085 |
| `axialmin_20Hz` | 20 | **−0,0158** | 0,0892 | **0,1535** | **1,721** |
| `axial_10Hz_full` | 10 | +0,0058 | 0,1652 | 0,2093 | 1,267 |

A perda total do MODELO nas três frequências é **0,1539 / 0,1537 / 0,1535** —
espalhamento de **0,03 %**. A do DADO varia **2,0×** (0,0892 → 0,1792).

⇒ **o modelo é praticamente CEGO à frequência nesta janela**, e o "erro de
nível" tem **sinal que troca com f**: falta perda a 10 Hz (+0,053), acerta a
15 Hz (+0,027) e sobra perda a 20 Hz (−0,016).

**Consequência que muda a rota:** uma alavanca de nível *uniforme* fecharia a
10 Hz e **quebraria** a 20 Hz — que hoje **passa**, e passa com σ 0,0248 = 0,99×,
sem folga nenhuma. O que a curva pede não é uma constante, é uma **lei de
frequência**. A campanha já tem candidato medido para ela: a re-atribuição
creep→fretting de flanco, que entregou **0 % → 93 %** da dependência de
frequência e foi recusada por custar uma curva.

**E isso explica o conflito com o D-Q por construção:** a saturação de flanco é
alavanca de **forma sem dependência de frequência**; ela pode consertar o σ da
curva longa, mas **não pode** resolver um déficit de lei de frequência. Não é
azar de parametrização — é o contradomínio da alavanca.

## 1. `li2022ti_axialmin_10Hz` — **NÍVEL PURO** *(no resíduo; ver a correção acima quanto ao remédio)*

Resíduos: `0,0 · +0,0524 · +0,0715 · +0,0776 · +0,0779 · +0,0709 · +0,0645 ·
+0,0489 · +0,0373 · +0,0253`. **Todos positivos**, e o viés é **exatamente o
MAE** (+0,0526) — o modelo retém demais em todos os pontos. σ já está DENTRO
(0,97×). Removido o viés, a curva **passa as três pernas**.

Não é forma. É magnitude: falta ~5,3 % de perda a 10 Hz.

### Mas o "nível errado" é AMBIGUIDADE DO DADO, não só do modelo

As duas curvas de 10 Hz da fonte discordam **entre si** em nível:

* `axialmin_10Hz` (Fig. 8c) normaliza por **12,0 kN** — base validada 3× pelo
  subagente (topos 17,895/14,091/8,876 contra rótulos 17,9/14,1/8,9, e
  F(2e5) = 12,0·(1−queda) a ±0,017 kN).
* `axial_10Hz_full` (Fig. 8a) foi digitalizada com **11,5 kN** (valores da CSV
  são múltiplos exatos de 1/115 ⇒ leitura em 0,1 kN); o pixel do traço dá
  **11,18**.

**4,2 % de discordância de base entre duas figuras do mesmo ensaio nominal.** E
os viéses refletem isso: o modelo está **+0,0526 alto** contra a base 12,0 e
**+0,0058** — praticamente centrado — contra a base 11,5. ⇒ o nível do modelo é
consistente com uma das duas figuras e 5 % alto contra a outra.

O piso do par declarado mede essa discordância: **MAE 0,0315** dado-contra-dado.
O erro do modelo (0,0526) é **1,67×** isso ⇒ **não** coberto pela barra PROVA
(que exige ≤ piso). Há déficit real de modelo, mas ele é da ordem de 0,67× a
própria discordância interna da fonte.

### O F₀ NÃO é o defeito — conferido na nota, não suposto

A nota de aparato (`li2022_triboint_axial_freq.md`) já documenta: *"recommended
preload range 10.21–14.30 kN → **P0 = 12.50 kN** selected"* e *"12.0 kN at N=200;
the torqued P0 was 12.5 kN — the first ~200 cycles' loss is not [plotada]"*. O
registry usa **12 500 N**, coerente com a nota. E a métrica **alinha** no 1º ponto
do dado (`align = 0,632385`, idêntico nas duas curvas de 10 Hz) ⇒ a perda antes de
N=200 não é penalizada e o F₀ de entrada **não** afeta o nível da métrica.

Suspeita levantada e **fechada por leitura da nota que já existia**. Registro de
método: antes de propor correção de input, pergunte à nota de aparato — 27 das 29
fontes têm uma.

---

## 2. `caccese2009_tapered_45kN_rep2` — **DEFEITO DO DADO**, confirmado 2×

Resíduos (26 pontos): `0,0 +0,045 +0,047 **+0,004** +0,046 +0,046 **−0,012
−0,013** +0,043 +0,043 **−0,016 −0,016 −0,017 −0,016 −0,017 −0,020** +0,038
+0,038 +0,037 +0,036 +0,036 +0,035 +0,035 +0,035 +0,035 +0,035`.

O resíduo **troca de sinal em blocos**, saltando ±0,05 — e é isso, e só isso, que
mantém σ em 0,0258 (1,03×): viés só +0,0195, e **removido o viés σ não muda**
(invariância por translação).

**Esta é a assinatura da contaminação, e ela foi lida do RESÍDUO — sem o PDF.**
A investigação independente por extração VETORIAL da Fig. 9
(`caccese_piso_e_dado_resultado.md`, resíduo de calibração 2,3e-5) provou que **9
dos 26 pontos da CSV traçam a réplica ERRADA** (+0,040 a +0,054 em t=50..1000 h),
com duas provas internas: `rep2` é **idêntica ao dígito** à `rep1` em t=900 e
t=1000, e é **não-monótona** num ensaio de relaxação estática.

**Dois instrumentos independentes, mesma conclusão** — o resíduo do modelo e a
polilinha do PDF. Corrigido o dado: σ **0,0258 → 0,0083** (3,1×) e a curva
**passa por mérito**, sem tocar no modelo e sem exceção.

⇒ esta curva **sai da fila por correção de DADO** (D-S), não por forma.

---

## 3. `li2022ti_axial_10Hz_full` — **FORMA (curvatura)**, e é o alvo do D-Q

Resíduos: `0,0 +0,0466 +0,0517 +0,0328 −0,0061 −0,0405 −0,0441` — **cruza zero**
uma vez, monotonicamente. Viés quase nulo (+0,0058); σ 0,0365 = **1,46×**, a
única das três que precisa de redução grande (**31 %**).

Modelo lento no início, rápido no fim: o dado **satura** e o modelo não. É
exatamente o defeito que a saturação de flanco (`flank_fret_depth`, decisão D-Q)
ataca, e a varredura no LI_2022 mede σ 0,0365 → **0,0244** (passa) em
`dep = 3,5e-6`.

### A base NÃO é o defeito desta curva — medido nas três hipóteses

| base assumida | MAE | res.máx | **σ_res** |
|---|---:|---:|---:|
| 11,5 (CSV atual) | 0,0317 | 0,0517 | **0,0365** |
| 12,0 (convenção da Fig. 8c) | 0,0466 | 0,0879 | **0,0371** |
| 11,18 (pixel do traço) | 0,0354 | 0,0680 | **0,0362** |

σ varia **2,5 %** entre as três (0,0362–0,0371) contra os **31 %** que a curva
precisa. ⇒ **nenhuma correção de base fecha esta curva**; a perna que manda é
insensível ao nível. E note que a base 11,5 é a **melhor** das três nas outras
duas pernas: corrigi-la para a convenção documentada **pioraria** MAE
(0,0317→0,0466) e res.máx (0,0517→0,0879) — o padrão já visto em ROUSSEAU e LU.

### As duas curvas de 10 Hz são espécimes DIFERENTES, não o mesmo ensaio 2×

Pergunta deixada aberta pelo subagente (`_CID_NAO_COMPARAVEL` mudaria o
denominador). **Respondida por medição: NÃO.** Em força absoluta:

| N | F_A (base 12,0) | F_B (base 11,5) | dif | rel |
|---|---:|---:|---:|---:|
| 200 | 12,000 | 11,500 | +0,500 | +4,17 % |
| 5 000 | 10,900 | 10,662 | +0,238 | +2,18 % |
| 20 000 | 10,450 | 10,301 | +0,149 | +1,43 % |
| 100 000 | 9,950 | 9,900 | +0,050 | +0,50 % |
| 200 000 | 9,850 | 9,800 | +0,049 | +0,50 % |

Três razões para NÃO tratá-las como duplicata:

1. **Nenhuma atribuição de base faz as trajetórias absolutas coincidirem.** O
   fator de escala ótimo B→A é **1,0234**, não 1,0435 (=12,0/11,5), e sobram
   **0,112 kN** de resíduo de FORMA depois de escalar. Duplicata digitalizada 2×
   coincidiria em toda parte.
2. A convergência é **monótona** (4,2 % → 0,5 %) e plateia no fim — assinatura de
   **dois F₀ distintos sob a MESMA carga imposta** (modo força: a força residual
   é fixada pela carga, não por F₀), não de erro de digitalização.
3. A Fig. 12 plota **3 espécimes** a 10 Hz (vidas 2,87/3,58/4,16 ×10⁵) e a
   Fig. 8(a) corre até fratura em ~4,1e5 ⇒ é o de vida mais longa; a Fig. 8(c)
   para em 2e5 e pode ser qualquer um.

⇒ o **denominador fica em 205** e o par declarado é piso de **repetibilidade
entre espécimes** (σ 0,0083), não de digitalização. *(Corrige o rótulo que
escrevi no `_PARES_REPLICA_DECLARADOS` no commit anterior — lá está "piso de
base/digitalização"; a medição diz espécimes distintos.)*

---

## ⚠️ A fila de 3 é pequena porque **6 falhas reais estão em "indecidível"**

As 7 curvas em `indecidivel_sem_piso` são, medidas:

| fonte | curva | MAE | res.máx | σ_res | ×lim |
|---|---|---:|---:|---:|---:|
| ROUSSEAU_2025 | `hdpe_t10` | 0,0919 | 0,1754 | 0,0712 | **2,85** |
| ROUSSEAU_2025 | `steel_t10` | 0,0725 | 0,1402 | 0,0803 | **3,21** |
| ROUSSEAU_2025 | `hdpe_t12` | 0,0527 | 0,1074 | 0,0537 | 2,15 |
| ROUSSEAU_2025 | `steel_t10_amp0p2` | 0,0957 | 0,1545 | 0,0412 | 1,65 |
| ROUSSEAU_2025 | `hdpe_t14` | 0,0440 | 0,0770 | 0,0299 | 1,20 |
| ROUSSEAU_2025 | `steel_t12` | 0,0451 | 0,0721 | 0,0292 | 1,17 |
| YANG_2023_IJPEM | `0,25 mm` | 0,1664 | 0,4256 | 0,1452 | **5,81** |

O classificador põe uma curva em `indecidivel_sem_piso` quando
`piso is None` — isto é, quando a fonte **não tem par de réplica em condição
repetida**. O rótulo lê-se como *"falta uma medição"*, e para o ROUSSEAU **isso
está VENCIDO**: a investigação de 2026-08-05
(`rousseau_piso_e_dado_resultado.md`) mediu que o paper publica **uma corrida por
condição** — varredura de texto completo por *repeat/average/std/scatter/error
bar/variability/twice/three times* devolve **zero**; a Tabela 2 tem 6 linhas, uma
por (material, espessura); Figs. 4/5/6 têm uma curva por condição e Figs. 7/8 (o
lugar onde barras morariam) têm um marcador por ponto **sem barra**.

⇒ **não é pendência, é impossibilidade**: nenhuma rodada de análise nossa produz
réplica de um paper que não a publicou. O único piso obtenível é de
**digitalização** (a mesma condição em 2 figuras: σ **0,0068**), que a máquina
de `_pisos_medidos` não aceita — ela pareia `case_id` com `case_id` — e que de
todo modo fica **abaixo** de 0,025 ⇒ `limite_sres` não se moveria.

**Leitura honesta:** as 6 do ROUSSEAU são **form-limited**, com erro de σ de
1,17× a 3,21×, e o rótulo "indecidível" as retira da fila sem que ninguém tenha
decidido nada. A fila real de forma é **9**, não 3 — 3 nomeadas + 6 parqueadas.

**Por que NÃO reclassifiquei em código:** as camadas da triagem são as do
`regra_de_parada_proposta.md`, que **aguarda assinatura do professor**, e mover
curva entre camadas muda a leitura dupla publicada. O que a medição autoriza é
**dizer o número** — e está dito aqui. Reclassificar é decisão, não medição.

*(A 7ª, `YANG_2023_IJPEM 0,25 mm`, é caso à parte: as irmãs de 0,30 e 0,35 mm
estão declaradas **data-limited por resolução** (mediana |Δdado| ≥ 0,10, prereg de
2026-08-01) e a de 0,25 mm ficou fora por salto 0,08. Com σ **5,81×** o limite e
res.máx **4,26×**, ela é a pior curva do conjunto e o PDF está declarado
inacessível pelo professor.)*

## Consequência para a fila

| curva | classe | rota | estado |
|---|---|---|---|
| `caccese rep2` | **dado** | D-S (corrigir a CSV) | provado, enfileirado |
| `axial_10Hz_full` | **forma/curvatura** | D-Q (saturação de flanco) | G1 em voo |
| `axialmin_10Hz` | **lei de frequência** | re-atribuição creep→flanco (recusada) | ⚠️ conflito com o D-Q |

⚠️ **O conflito está declarado no prereg do D-Q e a medição o confirma**: a
saturação de flanco tira perda tardia (fecha #3) e a `axialmin_10Hz` precisa de
**mais** perda (#1 piora monotonicamente, MAE 0,0526 → 0,0589). Duas curvas do
MESMO ensaio com demandas OPOSTAS.

**O que a decomposição acrescenta ao conflito:** ele não é irredutível *em
princípio*, porque as demandas são de **eixos ortogonais** — #1 é viés (nível) e
#3 é σ (forma), e uma alavanca de nível não move σ. O que o torna irredutível na
prática é que as duas curvas são **a mesma condição nominal** e o dado delas
discorda em nível por 4,2 % ⇒ qualquer alavanca de nível a 10 Hz move as duas na
mesma direção, e não existe nível que satisfaça as duas bases.

⇒ **a #1 não é fechável por constante enquanto a base da fonte estiver ambígua.**
É item de **decisão**, não de medição: qual das duas figuras dá a base de 10 Hz.
Sem isso, o teto do modelo nesta curva é o próprio piso de 0,0315 do par — e
0,0526 é 1,67× dele.
