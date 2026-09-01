# PRÉ-REGISTRO — TRIO `delta_free` + `loose_arrest_floor` + `slip_onset_W`

**Escrito em 2026-07-30, ANTES de medir o resultado.** Gates IMUTÁVEIS.
Store de base: `3546e6745448` · censo 104/202.

Sucede o prereg do PAR (`…-par-deltafree-arresto-prereg.md`), cuja execução
(`New_Theory/yang2023_par_resultado.md`) deu G2/G3/G5/G7 PASSA, **G4 REPROVA**
(0,35 mm) e **F4 FALSIFICA por erro meu de especificação**.

## 0. Por que não é "só corrigir o F4"

O pedido era corrigir o F4. Corrigir **apenas** o F4 e re-rodar produziria **os
mesmos números** — os valores congelados não mudam — e o G4 reprovaria de novo em
0,35 mm. Seria uma execução com resultado conhecido de antemão. Então este prereg
faz as duas coisas: **corrige o F4** e ataca a causa do G4, que a execução do par
diagnosticou.

**A causa, medida:** no 0,35 mm a média do resíduo por estágio foi
`I −0,006 · II −0,470 · III −0,150` → `I −0,165 · II −0,374 · III −0,065`.
Os estágios II e III **melhoraram**; o **estágio I piorou 27×**. O `delta_free`
corrigido faz o slip começar no **ciclo 1**, e o dado tem **atraso** antes do
colapso. Falta a incubação.

O engine já tem a forma: `slip_onset_W` (gate de Hill sobre a perda dirigida por
slip, default 0 = sem incubação, bit-idêntico). A condição documentada de opt-in é
*"quando o dado mostra platô"* — e mostra.

---

## 1. Os três valores

| parâmetro | valor | procedência |
|---|---:|---|
| `delta_free` (m6 / m8) | 122,96 / 129,18 µm | média geométrica da janela; **já provado** cinematicamente (v2: G2/G3) |
| `loose_arrest_floor` | 0,1025 | mediana do platô final medido (`kb.floor_from_curve`); **já testado como lei** (par: G5, 5 de 6) |
| **`slip_onset_W`** | **12,45 J** | **novo — ver §2** |

`slip_onset_sharpness` fica no **default 4**, declarado e não ajustado.

## 2. Como `slip_onset_W` é lido — e o critério que exclui curvas é de AMOSTRAGEM

O joelho do dado é o 1º ponto amostrado abaixo de 0,95. O trabalho de slip
acumulado até ali (`state.W_slip_acc`, com o `delta_free` e o piso já congelados)
é o candidato a `slip_onset_W`.

**Critério de resolubilidade, declarado antes e por argumento de amostragem:**
se o 1º ponto abaixo de 0,95 **já está abaixo de 0,85**, o joelho ocorreu *entre
amostras* e o seu N é desconhecido por um fator — aquela curva **não pode** ler o
limiar. Isto não é escolha por resultado: é a resolução do dado.

| δ | N do joelho | ratio ali | W (J) | uso |
|---:|---:|---:|---:|---|
| 0,25 | 50 | 0,940 | 19,95 | **lê** |
| 0,30 | 10 | 0,880 | 7,28 | **lê** |
| 0,35 | 10 | 0,900 | 13,53 | **lê** |
| 0,45 | 5 | 0,880 | 11,37 | **lê** |
| 0,50 | 2 | 0,750 | 4,45 | **HELD-OUT** |
| 0,55 | 5 | 0,820 | 15,25 | **HELD-OUT** |
| 0,65 | 2 | 0,780 | 8,17 | **HELD-OUT** |

```
slip_onset_W = mediana das 4 resolvíveis = 12.45 J
```

Espalhamento das 4: **2,7×** — declarado como a incerteza do limiar. Sobre as 7 o
espalhamento seria 4,5×, e o excesso vem inteiro das 3 mal amostradas: é por isso
que o critério existe, e ele foi escrito **antes** de eu ver o efeito no erro.

**As 3 held-out não entram na leitura** e por isso servem de **teste de
generalização real** (G6): se um único W lido de 4 curvas também descreve 3 que
não o informaram, é lei.

⚠️ **Dependência declarada:** `W_slip_acc` depende do `delta_free` (o slip entra
no trabalho). A leitura acima só vale com os valores congelados no §1; trocar o
`delta_free` obriga a reler o W.

---

## 3. GATES (imutáveis)

**G1 — CONGELADOS.** Os três valores do §1, nas 9 curvas. Nenhum per-curva.

**G2 — O RAMO SATURADO NÃO REGRIDE.** Mediana do res.máx das 6 (δ ≥ 0,30) tem de
ficar **≤ 0,2928**, que é o que o par já entregou. A incubação não pode custar o
ganho do par.

**G3 — SUB-CRÍTICO BIT-IDÊNTICO.** 0,15 e 0,18 com os mesmos dígitos de hoje.

**G4 — O 0,35 mm DEIXA DE REGREDIR (é o gate que motivou este prereg).**
MAE do 0,35 tem de ficar **≤ 0,1788** (o baseline de hoje). E, como antes,
nenhuma das 7 pior que +0,01 — com a **transição (0,25 mm) isenta**, pela mesma
razão aritmética já declarada no par (piso único 0,1025 contra piso próprio 0,58).

**G5 — INCUBAÇÃO NO LUGAR CERTO.** No 0,35 mm, a média do resíduo do **estágio I**
tem de melhorar em módulo em relação ao par (|−0,165| → menor). Existe porque
G4 podia passar por compensação em outro estágio; este gate exige que o conserto
aconteça **onde o defeito está**.

**F4 — CORRIGIDO (era o pedido).** A versão antiga — *"nenhuma curva termina
abaixo do piso"* — estava errada: `self_locking_gate` é `g = max(0, 1−F_min/F_0)`
e **multiplica `d_theta`**, logo arresta **só o canal rotacional**; wear, creep e
embedding seguem drenando e o `ratio` total pode passar abaixo do piso. A versão
correta:

> **F4′** — a perda acumulada **do canal `rotational_loosening`** não pode exceder
> `F₀·(1 − loose_arrest_floor)` em nenhuma das 9 curvas (tolerância 1 %). É o
> canal que o gate arresta, e é só sobre ele que o piso faz uma promessa.

**G6 — GENERALIZAÇÃO (informacional forte, não bloqueante).** Nas **3 held-out**
(0,50 · 0,55 · 0,65), reportar res.máx e MAE contra o par. Não bloqueia porque
elas têm joelho mal amostrado e o próprio dado é ruim ali — mas se elas piorarem,
o W único não é lei, e isso vai escrito no resultado.

**G7 — RESTO DO STORE BIT-IDÊNTICO.**

## 4. Expectativa declarada

* 0,35 mm melhora em MAE **e** no estágio I — é a hipótese;
* as 6 saturadas não perdem o ganho do par;
* a **transição (0,25 mm) continua errada**: a incubação atrasa o colapso dela, o
  que ajuda o começo, mas o patamar segue em ~0,10 contra 0,520 medido;
* **a fonte provavelmente ainda não entra no tripé.** A mais próxima (0,65 mm)
  está a 2,45× e violando MAE por 0,0032 e σ_res por 0,036.

## 5. Falsificadores

* **F1** — G3 falha ⇒ acoplamento fora do canal de slip.
* **F2** — G4 passa mas G5 falha ⇒ o MAE melhorou por compensação, não por
  conserto; a incubação não é o mecanismo.
* **F3** — G2 falha ⇒ a incubação custa o ganho do par: os dois efeitos competem
  e o trio não é aditivo.
* **F4′** — ver §3.
* **F5** — as 3 held-out pioram ⇒ `slip_onset_W` único não é lei; o limiar é
  per-amplitude, e aí é forma nova.

## 6. Decisão

⛔ **NÃO ASSINADO**. A execução mede os gates; a adoção é do professor.
