# CACCESE_2009 — o piso é 10× menor que o publicado, e a `rep2` está ERRADA

**2026-08-05** · investigação só-leitura por subagente delegado, sob o MANDATO
PERMANENTE (regra de VAZÃO: um subagente por fonte, só-leitura). Fingerprint
`b072b24fd3a8`. **NADA foi alterado** — nem CSV, nem config, nem store.

## Pergunta que motivou

A `caccese2009_tapered_45kN_rep2` viola **uma** perna (σ) e o par declarado
rep1↔rep2 media piso σ **0,0234** — abaixo do limite global, logo sem rota F7.
Existe piso maior obtenível (3ª réplica? outra figura?) que justifique exceção?

## Resposta curta

**Não, e a pergunta estava mal-posta.** O piso verdadeiro é **σ 0,002–0,009**
(4 instrumentos independentes) — ainda MENOR. E o 0,0234 publicado é **~87 %
artefato da nossa própria digitalização**: 9 dos 26 pontos da `rep2` traçam a
**curva errada**. Corrigido o dado, a curva **passa por mérito**.

## Método: a Fig. 9 é VETOR, não raster

Polilinhas extraídas com `page.get_drawings()`, calibração nos 9 rótulos de tick
de cada eixo (resíduo **2,3e-5** em F/F₀ e **0,78 h** em t) e **verificação por
redesenho dos vetores sobre a figura renderizada** — caem exatamente sobre as
curvas impressas. Verdade-de-pixel, não leitura a olho.

## 1. O par declarado é VÁLIDO — não é o caso ROUSSEAU

Quatro evidências independentes de que rep1 e rep2 são réplicas da MESMA
condição:

* **Legenda da Fig. 9**: só **duas** entradas (`19.1 mm tapered-head @45 kN`
  vermelho contínuo e `protruding-head @45 kN` tracejado). Os nossos dois CSVs
  saem da MESMA entrada.
* **Tabela 5**: três linhas `Tapered C/AL | 19.1 | 44.7 / 44.8 / 43.9` — mesmo
  diâmetro, espessura, membro e tipo de cabeça; só o P₀ **alcançado** difere
  (2 % de espalhamento).
* **Companion DTIC ADA429921, Tabela 3.18**, literal: *"Equations for ¾" Tapered
  and Non-Tapered Head Bolt Tests When Loaded to 10,000 lbs."*, linhas nomeadas
  **`tapered bolt 1/2/3`** ⇒ três **parafusos distintos**, não reensaio.
* **DTIC §3.7**: *"no reloading was done to any of the tapered vs. non-tapered
  test connections, and all connections were loaded to 10,000 lbs preload."* +
  Apêndice A: mesmo painel 34 de compósito, mesma instrumentação (arruelas de
  19 mm / 289 kN).

⇒ o modo de falha do ROUSSEAU (duas **espessuras** pareadas como réplicas) **não
ocorre aqui**. D, t, membro, cabeça, pré-carga, protocolo e painel são os
mesmos; muda o parafuso/montagem individual — que é exatamente o que
`_PARES_REPLICA_DECLARADOS` existe para cobrir.

**Bônus de procedência — cada traço casa com UMA linha da Tabela 5** (RMS contra
os ajustes Eq. (2)):

| traço vetorial | fim F/F₀ | linha da Tabela 5 | RMS | pior alternativa |
|---|---:|---|---:|---:|
| alta (**NÃO digitalizada**) | 0,6828 | 43,9 kN · K₁ 0,091 · β 0,958 | 0,0036 | 0,0170 |
| média = nosso `rep1` | 0,6805 | 44,7 kN · K₁ 0,112 · β 0,945 | 0,0044 | 0,0106 |
| baixa = nosso `rep2` | 0,6270 | 44,8 kN · K₁ **0,173** · β **0,895** | 0,0040 | 0,0651 |

O `rep2` é o parafuso de **maior relaxação** entre os tapered (K₁ 1,9× o menor);
ordenação confirmada no DTIC 3.19 (β = 0,81 / **0,76** / 0,83).

*(A Fig. 9 plota o DADO, não os ajustes: a 2ª diferença dos traços tem RMS
0,0069 contra **0,00001** de uma Eq. (2) lisa — 700× mais rugoso.)*

## 2. São TRÊS réplicas. Digitalizamos duas.

Três polilinhas vermelhas (drawings #135/#188/#241, 113–118 vértices cada),
contadas na camada vetorial **e** confirmadas visualmente a 20× (fresta branca
separando o par superior). A nota de aparato diz "2 tapered", mas a própria
matriz dela já hesitava ("×2-3 replicates"); Tabela 5 e DTIC 3.18/3.19/3.20
fecham em **três**. ⇒ a 3ª (fim 0,6828) **não está na biblioteca**.

## 3. Dispersão declarada pelo paper: sem barras, mas por réplica

Conferido **na imagem** (8× e 20×, quatro recortes): a Fig. 9 **não tem barras de
erro, `±` nem "average of N"** — plota traços individuais. O que o paper diz:

* *"The protruding-head bolts lie within the range of the tapered-head bolt
  results."*
* *"Although there is a high variability observed from test to test indicated by
  the trendline with an R² value of 0.2."*
* DTIC: *"The individual calculations for β vary from 0.76 to 0.81 in the tapered
  case … demonstrating that there are some variations in quantifying β"* (a prosa
  diverge da própria Tabela 3.19, que traz 0,76–0,83; vale a tabela).

Convertendo pela Eq. (2) `Pt/P0 = 1/(1+K₁t^n)` nas 3 linhas tapered:

| t (h) | 44,7 kN | 44,8 kN | 43,9 kN | faixa | σ(n−1) |
|---|---:|---:|---:|---:|---:|
| 10 | 0,8516 | 0,7981 | 0,8696 | 0,0715 | 0,0372 |
| 100 | 0,7867 | 0,7300 | 0,8018 | 0,0718 | 0,0379 |
| 1000 | 0,7033 | 0,6490 | 0,7105 | 0,0615 | 0,0336 |
| 2000 | 0,6748 | 0,6225 | 0,6786 | 0,0561 | 0,0313 |

Nas três réguas do report (média dos 3 pares, 10–2000 h): **MAE 0,0456 · res.máx
0,0492 · σ 0,0035**. Leitura que importa: **a dispersão do paper é de NÍVEL, não
de forma** — o σ da diferença é 13× menor que o MAE.

## 4. As outras 5 curvas — uma tem réplica não digitalizada

* ✅ **`protruding_45kN`**: a Fig. 9 tem **duas** tracejadas (preta e vinho);
  digitalizamos só a vinho (concorda com o vetor a MAE 0,0044). Tabela 5 confirma
  duas linhas `Prot. C/Al 19.1` (44,8 e 44,5 kN) — a nota de aparato já
  registrava a lacuna, agora medida. Piso do par protruding: **MAE 0,0268 ·
  res.máx 0,0324 · σ 0,0049** (2,6–1996 h) ou σ 0,0025 (10–1990 h).
  Digitalizar a preta cria um **segundo par declarado**.
* ❌ `compblock_34kPa` / `71kPa`: pressões nominais distintas (89 vs 184 kN).
* ❌ `retighten_12p7mm` / `19p1mm`: tamanhos de parafuso diferentes, série de
  reaperto (outra figura, outros espécimes).
* ⚠️ **NÃO RESOLVIDO**: se `retighten_19p1mm_no_retighten` é o **mesmo ensaio**
  que uma das protruding da Fig. 9. Nosso CSV concorda com a tracejada vinho a
  MAE 0,0110 / res.máx 0,0307 — mais perto do que dois ensaios independentes
  costumam ficar (o par protruding difere por 0,0268), mas longe de "mesma
  medição digitalizada 2×". As polilinhas das Figs. 6/7 vêm fragmentadas em 8–26
  pedaços por curva e a extração sem costura devolveu F₀ absurdos; **conclusão
  não forçada**.

## 5. A digitalização está fiel? `rep1` sim. **`rep2` NÃO.**

| CSV | segue | MAE vs vetor | res.máx |
|---|---|---:|---:|
| `rep1` | média | 0,0047 | 0,0139 (viés +0,014 em 25–75 h) |
| `rep2` | baixa | 0,0208 | **0,0544** |

O `rep2` **salta para a curva média/alta** em t = 50, 150, 200, 500, 600, 700,
800, 900, 1000 h — erro **+0,040 a +0,054**. Duas provas cabais, INTERNAS:

1. `rep2` é **idêntico ao dígito** ao `rep1` em t=900 (0,7087) e t=1000
   (0,7081). Duas réplicas independentes não concordam a 4 decimais — o
   digitalizador leu a **mesma** curva duas vezes.
2. `rep2` é **não-monótono** (0,7736 → 0,7955 → 0,7397; 0,6825 → 0,7319) num
   ensaio de relaxação **puramente estático** em que TODOS os traços publicados
   decrescem monotonicamente.

**A nota de aparato erra o mecanismo**: descreve o trecho como *"an interpolated
(not pixel-verified) stretch ≈420–980 h"*, mas interpolar 0,6825@400 →
0,6459@1100 daria trecho **monótono**. Os valores são **cópia de outra réplica**,
deslocada pelo mesmo −0,004 que o `rep2` carrega em toda parte. Uma nota que se
lê como *"dado um pouco mais mole aqui"* é, de fato, *"curva errada aqui"*.

**Digitalização preguiçosa (passo constante) NÃO existe**, e isto foi conferido
em vez de suposto: a cauda do `rep2` (1200→2000) tem razão
passo(1200-1300)/passo(1900-2000) = **1,00** onde uma log daria ~1,5 — **mas o
vetor dá 1,09**. A cauda é reta **de fato**. (`protruding` dá 1,57; o `rep1` tem
trepidação local de ±0,0035 em 1200–1400, ruído de traçado.) Erro de corda da
grade de 26 pts ≤ 0,014 e só no mergulho 0–10 h.

## VEREDICTO

**O piso 0,0234 está ERRADO — e para BAIXO.**

| instrumento | MAE | res.máx | **σ** |
|---|---:|---:|---:|
| CSVs atuais (publicado, n=2) — reproduzido exato | 0,03719 | 0,06762 | **0,02337** |
| vetor PDF, mesmo par (n=2) | 0,0550 | 0,0581 | **0,0015** |
| vetor PDF, mesmo par, grade da métrica c/ t=0 | 0,0537 | 0,0573 | **0,0087** |
| vetor PDF, **3 réplicas** | 0,0414 | 0,0492 | **0,0033** |
| vetor PDF, 3 réplicas, grade da métrica c/ t=0 | 0,0402 | 0,0485 | **0,0076** |
| ajustes Eq. (2) **do próprio paper**, n=3 | 0,0456 | 0,0492 | **0,0035** |
| par **protruding** (mesmo rig, independente) | 0,0268 | 0,0324 | **0,0049** / 0,0025 |

Quatro instrumentos independentes põem o σ deste rig em **0,002–0,009**, não
0,023. O 0,0234 vem do resíduo pulando ±0,05 entre pontos contaminados e limpos
— que é exatamente o que um desvio-padrão-**da-diferença** mede.

**Não existe piso maior obtenível.** E como `limite_sres = max(0,025; piso)`,
todo piso corrigido fica **abaixo** de 0,025 ⇒ o limite do CACCESE permanece
cravado no global **em todos os cenários**, inclusive com a 3ª réplica. A rota
"piso maior ⇒ exceção legítima" está **fechada por medição**.

## Mas a curva não precisa de exceção — precisa do CSV consertado

Re-pontuando a predição **inalterada** (`metric_pred` do store) contra o dado
corrigido:

| | MAE (÷0,05) | res.máx (÷0,10) | σ_res (÷0,025) | tripé |
|---|---|---|---|---|
| `rep2` hoje | 0,0292 (0,58×) | 0,0468 (0,47×) | **0,0258 (1,03×)** | REPROVA |
| `rep2` **corrigido** | 0,0349 (0,70×) | 0,0452 (0,45×) | **0,0083 (0,33×)** | **PASSA** |
| `rep1` hoje | 0,0203 | 0,0260 | 0,0054 | passa |
| `rep1` corrigido | 0,0181 | 0,0227 | 0,0051 | passa |
| modelo vs **3ª réplica** (não digitalizada) | 0,0263 | 0,0296 | 0,0054 | passaria |

Os 3 % que reprovam a `rep2` são **inteiramente** os 9 pontos contaminados: σ_res
cai **3,1×**. Robustez: somando em quadratura ruído de traçado do nível do `rep1`
(±0,004) dá σ ≈ 0,0092 — ainda 0,37× do limite. **A curva passa por mérito, sem
tocar no modelo e sem exceção.**

Contexto que sustenta a leitura: a predição é **bit-idêntica** para `rep1` e
`rep2` (o modelo dá **uma** curva para a condição, fim 0,6578) enquanto as
réplicas terminam em 0,6828/0,6805/**0,6270**. Contra a `rep2` corrigida o viés é
**+0,0349 = todo o MAE** — deslocamento puro de nível, daí o σ minúsculo. É
problema de *contra qual réplica pontuar*, não de forma.

## Consequências já aplicadas neste commit (§4.43 contra nós)

Dois comentários do código estavam **vencidos** — escritos em 2026-08-04, contra
o store **pré-D-H** (o kernel de creep saturante foi adotado nesta mesma fonte no
mesmo dia):

* a retratação da `rep1` cita *"o modelo faz 0,0523"*; o store vigente diz
  **0,0203**, e a curva **passa o tripé por mérito** ⇒ a retratação segue correta
  (o piso citado era inválido) mas ficou **sem consequência**. Se a rota F7 fosse
  reaberta hoje, 0,0203 estaria **abaixo** da barra PROVA 0,0372 — perna
  **coberta**, o oposto do que o comentário diz.
* `_SEM_ROTA_F7_MEDIDO` cita σ **0,0354**; o vigente é **0,02576** — viola por
  3 %, não por 42 %.

Registro de método: **número de RETRATAÇÃO também envelhece.** Quem o lê sem o
fingerprint conclui o oposto do que o store diz.

## Fila (nenhuma é medição)

* **D-S — correção do CSV `rep2`** (prereg próprio; classe *dado*, como o D-R do
  ROUSSEAU). Enfileirado atrás do D-Q pela regra de escritor único.
* Digitalizar a **3ª tapered** e a **protruding preta** ⇒ n=3 no par principal e
  um segundo par declarado. Não muda `limite_sres` (piso < global em todo
  cenário) — muda a **procedência**.
* Corrigir a **nota de aparato**: "2 tapered" → 3, e o mecanismo do trecho
  420–980 h ("interpolado" → "cópia da réplica errada").
* Aberto, não decidido: `retighten_19p1mm` × protruding-vinho podem ser o mesmo
  ensaio (MAE 0,0110) — questão de `_CID_NAO_COMPARAVEL`, sem prova suficiente.
