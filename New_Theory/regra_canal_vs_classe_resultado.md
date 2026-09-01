# A regra que prediz quando uma constante COMPARTILHADA funciona: **canal × homogeneidade de classe**

**2026-08-10** · só-leitura · **nada adotado** · store `d197fc4c491c`, censo 144/205 ·
continuação direta do censo de classes mecânicas (`censo_stick_abertas_resultado.md`).

## O null repetido

Testei a alavanca de **nível do canal rotacional** (`tr_loose_gain`, per-fonte) com controle da
fonte, na classe PARCIAL:

| fonte | curvas | tripé | classe das abertas | ×0,6 | ×1,5 | ×2,5 |
|---|---:|---:|---|---|---|---|
| `SUN_2025_CRIMP` | 8 | 6 | PARCIAL ×2 | 6→**4**, 4 pioram | 6→**4**, 3 pioram | 6→**4**, 4 pioram |
| `ROUSSEAU_2025` | 8 | 4 | PARCIAL ×3 + **GROSS** ×1 | 4→**3**, 5 pioram | 4→**3**, 5 pioram | 4→**3**, 5 pioram |
| `LIU_2025` | 7 | 3 | **STICK ×2** + PARCIAL ×2 | 3→3, 0 pioram | — | — |

**Nenhuma dose ganha em nenhuma das três.** Nas duas primeiras, curvas que passavam **saem**.

⚠️ E na `ROUSSEAU` o sinal é diagnóstico: as 4 abertas têm viés **positivo** (+0,05 a +0,15 =
modelo perde pouco), então ×1,5 e ×2,5 *deveriam* ajudar — e pioram. Mais ganho rotacional não
chega onde o resíduo está.

## As 2 fontes que faltavam (o job bufferizado liberou depois) — e um LIMITE do meu probe

| fonte | curvas | tripé | classe das abertas | viés das abertas | melhor dose |
|---|---:|---:|---|---|---|
| `LU_2024` | 13 | 3 | PARCIAL ×2 | **−**0,126 / −0,480 / −0,060 | ×0,5 e ×0,7: 3→3, **0 saem**, 1 piora |
| `YANG_2023_IJPEM` | 9 | **0** | PARCIAL ×3 + STICK ×1 | +0,166 / +0,047 / **−**0,159 / +0,239 | ×0,7–×3,0: 0→0, **0 pioram, 0 saem** |

Duas leituras novas:

* No `LU_2024` o viés das abertas é **negativo** (modelo perde **demais**), ao contrário da
  `ROUSSEAU` — então *reduzir* o ganho é a direção certa, e ×0,5/×0,7 são de fato
  **inofensivas**. Mas não ganham. (E o `limite_sres` do LU é **0,1715**: a
  `fig14_amp0p5_long` já tem σ **dentro** (0,1235) — ela reprova por MAE 2,5× e res.máx 3,9×,
  não pelo σ.)
* No `YANG_2023_IJPEM` os sinais das 4 abertas são **mistos** (+0,17, +0,05, −0,16, +0,24) —
  não existe direção única de correção, o que barra qualquer constante compartilhada **antes**
  de qualquer medição de canal.

⚠️ **E aqui o limite do meu próprio probe, que eu preciso declarar:** os contadores que
imprimi são **grossos** — "pioram" conta só ΔMAE > +0,01 e "saem" só saída do tripé. Logo
`0 pioram / 0 saem` no `YANG_2023` **não prova inércia**: prova apenas que nada passou dos
limiares. Chamar aquilo de "canal inerte" seria repetir o erro que esta campanha registra três
vezes neste mês. O que está medido é: **nenhuma dose ganhou**, em nenhuma das cinco fontes.

E o `SUN_2025_CRIMP` mostra que o null é **dependente de dose na borda**: ×0,5 não tira
ninguem do tripé (6→6) e ×0,6 tira **dois**. O meu texto anterior ("perde 2 nas três doses")
descrevia as doses que eu havia rodado (0,6/1,5/2,5) e segue correto para elas — mas a
vizinhança é mais áspera do que aquele resumo sugeria.

## ✅ A regra — e ela prediz 7 resultados meus, 4 acertos e 3 nulls

Cruzando com as adoções que **funcionaram** nesta campanha:

| adoção | canal | driver do canal | classe da fonte (abertas) | resultado |
|---|---|---|---|---|
| **D-Z** (JCSR forma) | creep | **tempo** | mista | ✅ 2 fecham |
| **D-AA** (JCSR conjunta) | creep | **tempo** | mista | ✅ 1 fecha |
| **D-AB** (ECCLES `C_creep`) | creep | **tempo** | mista | ✅ 1 fecha |
| **D-AC** (YANG_2019 `k_wear_spec`) | wear | **slip** | **PARCIAL ×4 — homogênea** | ✅ 1 fecha, 0 pioras |
| null: `C_creep` no LIU_2025 | creep | tempo | — | ⛔ (ver abaixo) |
| null: `tr_loose_gain` no SUN / ROUSSEAU | rotacional | **slip** | **mista** | ⛔ |
| null: rugosidade no CHU | embedding | (slip-modulado) | **GROSS ×6** | ⛔ |

**Regra:**

> Uma constante **compartilhada** por uma fonte funciona quando o **driver do canal é
> uniforme entre as curvas dela**.
> * Canal dirigido por **TEMPO** (creep) — o driver é o mesmo em todas as curvas por
>   construção ⇒ constante compartilhada é legítima **independentemente** da classe mecânica.
> * Canal dirigido por **SLIP** (wear, rotacional) — o driver varia de **zero** (STICK) a
>   **δ inteiro** (GROSS) dentro da mesma fonte ⇒ a constante compartilhada só funciona se a
>   fonte for **homogênea de classe**.

Isso explica, sem exceção, por que **as três adoções de creep atravessaram fontes mistas** e por
que a **única adoção de canal de slip** (D-AC) caiu numa fonte cujas abertas são todas PARCIAL.

## ⚠️ E corrige a leitura do meu próprio null do `C_creep` no LIU_2025

Ontem escrevi que o `C_creep` per-fonte falhou no LIU_2025 porque *"as curvas discordam sobre o
valor da constante"* (×0,5 contra ×1,5). Pela regra, creep **deveria** funcionar — o driver é
tempo. O que falha ali não é o creep: é que **creep é 100 % da perda nas duas STICK e um canal
entre quatro nas duas PARCIAL**. A constante não precisa servir a dois *drivers*; precisa servir
a dois **orçamentos de perda**. É uma terceira causa de null, distinta das duas da regra, e vale
nomeá-la:

> **Fonte de classe mista falha até em canal de tempo, quando o canal responde por FRAÇÕES
> muito diferentes da perda total entre as curvas.**

## ✅ CENSO COMPLETO (150 curvas disp-mode) — fecha a limitação declarada, confirma a regra em 5 de 6, e traz **1 contraexemplo**

O job serial terminou. **150 das 205 comparáveis** são disp-mode:

| classe | n | % | **no tripé** |
|---|---:|---:|---|
| **STICK** | 18 | 12 % | **6/18 = 33 %** |
| **GROSS** | 70 | 47 % | **53/70 = 76 %** |
| **PARCIAL** | 62 | 41 % | **32/62 = 52 %** |

⚠️ **A taxa de aprovação depende fortemente da classe:** uma curva em STICK tem
**2,3× menos** chance de passar o tripé que uma em gross slip. Isso não era sabido, e dá ao
"stick" o estatuto de **fator de risco medido**, não de curiosidade.

Homogeneidade por fonte (agora sobre **todas** as curvas, não só as abertas):

| fonte | S / G / P | homog.? | a regra prediz | medido |
|---|---|---|---|---|
| `YANG_2019` | 0/0/**5** | **SIM** | slip funciona | ✅ D-AC fechou, 0 pioras |
| `ROUSSEAU_2025` | 1/1/6 | mista | falha | ✅ falhou |
| `LU_2024` | 2/0/10 | mista | falha | ✅ falhou |
| `LIU_2025` | 2/0/5 | mista | falha | ✅ falhou |
| `YANG_2023_IJPEM` | 3/0/6 | mista | falha | ✅ falhou |
| `CHU_2026` | 0/8/1 | mista | falha | ✅ falhou (rugosidade) |
| **`SUN_2025_CRIMP`** | 0/0/**4** | **SIM** | slip funciona | ⛔ **FALHOU** |

## ⛔ O contraexemplo, e o buraco que ele abre na minha taxonomia

O `SUN_2025_CRIMP` é **homogêneo** (4/4 PARCIAL) e ainda assim o `tr_loose_gain` compartilhado
**tira 2 curvas do tripé**. A regra, como eu a escrevi, previa sucesso.

A causa: a fonte tem **8 curvas, e só 4 são disp-mode**. As outras **4 são modo-força**, onde o
slip vem de `(F_tr − F_slip)/k_tr` e não de `δ − onset` — **outra lei**, com outro driver. A minha
classificação cobria só disp-mode e chamou de "homogênea" uma fonte que mistura **modos de
controle**.

⇒ **Correção da regra:** a homogeneidade exigida é de **driver**, e o driver muda em **dois**
eixos, não um:

1. **modo de controle** (disp-mode × modo-força) — leis de slip distintas;
2. **classe mecânica** dentro do disp-mode (STICK / PARCIAL / GROSS).

Uma fonte só é compartilhável num canal de slip se for homogênea nos **dois**. Isso reduz as
candidatas de 10 para menos — e explica o único furo da regra sem salá-la *post hoc*: o furo foi
achado pela medição que eu rodei **para testar a regra**, e a correção é estrutural, não um
epiciclo.

## ✅ A regra APLICADA às 27 fontes: o espaço de canal-de-slip compartilhável está **EXAURIDO**

Cruzei os dois eixos de homogeneidade (classe mecânica × pureza de modo) com o número de
**abertas** de cada fonte. Resultado, sobre as 27 fontes comparáveis:

| veredito | fontes | abertas cobertas |
|---|---:|---:|
| **classe mista ⇒ barrada** | 13 | **22** (CHU 6 · LIU_2025 4 · ROUSSEAU 4 · YANG_2023 4 · LU 2 + …) |
| **mistura MODOS ⇒ barrada** | 1 (`SUN_2025_CRIMP`, 4 disp de 8) | **2** |
| compartilhável, **0 abertas** — nada a ganhar | 7 (`ICMEZ`, `LIU_2020_WEAR`, `LIU_2022_RETIGHT`, `SUN_REASSY`, `ZHANG_2006/2018/2019`) | 0 |
| **compartilhável COM abertas** | **2**: `YANG_2019` (1) · `YANG_2021` (3) | **4** |

E as duas únicas candidatas estão, na prática, fechadas:

* **`YANG_2019`** (5/5 PARCIAL, modo-puro, 1 aberta) — já explorada pelo **D-AC**, e está sob
  trabalho ativo de outra sessão (8+ rodadas hoje). Escritor único: não é minha.
* **`YANG_2021`** (8/8 STICK, modo-puro, 3 abertas) — e aqui a regra dá **luz verde enganosa**.

## ⚠️ Terceiro furo, pego ao aplicar a regra sistematicamente

Para o `YANG_2021` a regra diz "homogêneo ⇒ compartilhável", mas a classe é **STICK** — onde
**todo canal de slip tem driver zero**. Compartilhar uma constante que multiplica um canal morto
é compartilhar nada. A regra precisa da cláusula:

> **Homogêneo em STICK é compartilhável em princípio e inútil na prática** — o canal
> compartilhado está morto em **todos** os membros. Homogeneidade é condição de
> *transferibilidade*, não de *existência* do canal.

## O que isto diz sobre onde o trabalho restante tem de vir

Com a regra completa (2 eixos + a cláusula do STICK), **nenhuma adoção de canal de slip
compartilhado está disponível hoje**. As 29 abertas se distribuem em:

* **22** barradas por **heterogeneidade** ⇒ rota é `per_case` **com argumento físico** (não
  conveniência métrica) ou forma que **discrimine** entre as classes;
* **3** (`YANG_2021`) em fonte onde o canal está morto ⇒ rota é **forma** (perda sustentada sob
  stick), já especificada em `yang2021_trabalho_profundo_resultado.md`;
* **4** (`YANG_2023_IJPEM`) sem **direção comum** de correção ⇒ rota é **dado**
  (`yang2023_ijpem_sem_direcao_resultado.md`).

⇒ **É por isso que eu não tenho candidato fundado para adotar** — e agora isso é um resultado
medido sobre o espaço de busca, não uma constatação de cansaço.

## Como usar isto antes de gastar uma grade## Como usar isto antes de gastar uma grade## Como usar isto antes de gastar uma grade

1. Medir a **classe mecânica** das curvas da fonte (instrumentar `resolve_transverse_slip` —
   ~1 min por curva).
2. Se a fonte for **mista** e a alavanca candidata for de canal **dirigido por slip**:
   **não gaste a grade** — o compartilhamento está estruturalmente barrado. Vá para `per_case`
   com argumento físico, ou para forma.
3. Se for **homogênea**, a receita D-AB (alavanca + controle da fonte) aplica-se.
4. Canal de **tempo** é a exceção — mas confira a **fração da perda** que ele carrega em cada
   curva antes de assumir que é compartilhável.

## Limitações declaradas

* ~~A classe foi medida só nas 29 abertas~~ **FECHADO** — censo completo das 150 disp-mode
  acima; e foi ele que achou o contraexemplo do `SUN`.
* ~~`LU_2024` ficou fora da varredura por custo~~ **entrou** — o job bufferizado terminou e
  liberou as 5 fontes; está na tabela acima. (Esta linha ficou vencida **dentro do mesmo
  documento** por uma hora: §4.43 vale para o parágrafo ao lado, não só para o roadmap.)
* 3 a 5 doses por fonte, não uma grade — o null é sobre a **direção**, não sobre um ótimo
  fino; e o `SUN` mostra que na borda a vizinhança muda entre ×0,5 e ×0,6.

## Reprodutibilidade

`parcial_diag.py` (lê do store) e `parcial_lev.py` (varre `tr_loose_gain` com controle de
fonte) no scratchpad. ⚠️ Rodar com **`py -3.12 -u`**: a primeira execução ficou 25 min com
arquivo de saída em 0 bytes por buffering de stdout — a armadilha que o `CLAUDE.md` já
registra para `cmd > file`.
