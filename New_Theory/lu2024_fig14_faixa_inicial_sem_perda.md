# `lu2024_fig14` — a faixa inicial **sem perda de pretensão** é REAL, e o modelo a destrói no ciclo 1

**2026-08-20 (14:0x)** · pedido do professor · só-leitura · **nada adotado** · store
`df35fd990380`, censo **162/205**. Paper: Lu, Zhu, Li, Li, Wang, Li, *Sensors* **2024**,
24, 3306 (`sensors-24-03306.pdf`).

---

## 0. ⛔ ERRATA MAIOR (15:2x) — a faixa inicial é REAL mas responde por ~4 % do erro

> **Este documento inteiro atribuiu a não-convergência à faixa inicial. Isso está
> QUANTITATIVAMENTE ERRADO, e o erro é meu.** Medi onde o resíduo mora:
>
> | curva | \|res\| em N≤5 | \|res\| em N>30 | **contribuição de N≤5** | **de N>30** |
> |---|---:|---:|---:|---:|
> | 0,25 mm | 0,1839 (n=6) | 0,0905 (n=258) | **3,8 %** | **79,5 %** |
> | 1,00 mm | 0,3610 (n=6) | 0,4421 (n=65) | **4,7 %** | **62,3 %** |
>
> ⇒ **a faixa inicial contribui ~4 %.** O erro vive em **N>30**, com 62–80 % do total.
>
> **Duas afirmações que eu confundi, e é a raiz de tudo abaixo:**
> · *"o modelo erra na faixa inicial"* — **VERDADE**, e feio: 0,6191 contra 0,9991 no ciclo 1.
> · *"por isso não converge"* — **FALSO**: são **6 pontos de 96–289**. Consertar a faixa
> perfeitamente reduz o MAE em ~4 %.
>
> ⚠️ **E isto explica retroativamente a §5d:** a varredura de `N_emb` não fechava nada porque
> **apontava para 4 % do problema**. O candidato não morreu só por ótimos disjuntos — morreu
> por **alvo errado**.
>
> ⚠️ **O "patamar de 24–56 ciclos" também cai** (§5e): a **N@0,99** é **3 / 4 / 3 ciclos** nas
> três — igual. Os 24/27/56 vinham do limiar 0,95 sobre dado esparso; os valores repetidos
> (27, 27, 27, 56, 56) denunciam que o cruzamento cai no mesmo x amostrado. **A faixa real é
> ~3–4 ciclos e NÃO depende da amplitude.**
>
> **O que sobrevive deste documento:** o ponto de partida do professor (o modelo destrói no
> ciclo 1 uma faixa que o dado preserva) é **um defeito real e nomeado**, com constante
> identificada (`N_emb` = 0,5, 86 % do assentamento no ciclo 1); a resolução do W3; e a
> inércia estrutural do `emb_amp_exp`. **A atribuição da não-convergência, não.**
>
> ⇒ **A pergunta certa passa a ser: o que erra em N>30?** Não medi isso ainda, e não
> especulo aqui.

## 0a. ✅ O QUE ERRA EM N>30 — medido, e são TRÊS defeitos diferentes (15:3x)

O professor pediu esforço nesta frente. Medido, e o resultado **corrige a §0 para uma das
curvas**.

### Estrutura do resíduo em N>30

| amp | n | viés | \|viés\|/MAE | ρ(res,N) | modelo acima do dado |
|---:|---:|---:|---:|---:|---:|
| 0,25 | 258 | −0,0905 | **1,00** | −0,83 | **0 de 258** |
| 0,50 | 109 | −0,0685 | **1,00** | −0,42 | **0 de 109** |
| 1,00 | 65 | −0,4421 | **1,00** | **+0,88** | **0 de 65** |

⇒ **o modelo está abaixo do dado em 100 % dos pontos das três**, com `|viés|/MAE` = **1,00**
exato: resíduo de sinal único. **O modelo sempre perde demais.**

### O teste que separa: alinhar em N=30 e ver o que sobra

| amp | MAE(N>30) | após alinhar | **resta** | leitura |
|---:|---:|---:|---:|---|
| 0,25 | 0,0905 | **0,0046** | **5 %** | **offset propagado** |
| 0,50 | 0,0685 | 0,0702 | **102 %** | **taxa/forma** — alinhar PIORA |
| 1,00 | 0,4421 | 0,3623 | **82 %** | **taxa**, com 18 % de offset |

### ⛔ Isto CORRIGE a §0 para a amp 0,25

Na `amp 0,25` o dado é **plano** (0,834 → 0,827 → 0,828) e o modelo é **plano** (0,746 →
0,738 → 0,734): **os dois estacionam, e o modelo só está 0,09 abaixo.** O resíduo por terço é
−0,088 / −0,090 / −0,094, praticamente constante.

⇒ **para essa curva a faixa inicial É a causa**: 95 % do erro de N>30 é a perda precoce
excedente **propagada**. Meu "4 %" da §0 mediu **onde o resíduo está**, não **o que o causa** —
e para uma curva plana essas duas coisas divergem por construção.

⚠️ **Mas não vale para as outras duas:** alinhar a `0,50` a **piora** (102 %) e a `1,00` só
melhora 18 %. Nelas o erro **nasce depois**.

### O retrato da `amp 1,00`, que é a pior

No 1º terço de N>30 o **dado está em 0,959** e o **modelo em 0,146**: o modelo já colapsou
enquanto o ensaio ainda está intacto. `ρ = +0,88` ⇒ o resíduo **encolhe** com N (−0,813 →
−0,093), porque o dado desce até encontrar o modelo no chão. **Não é offset nem nível: é o
relógio do colapso, adiantado por um fator grande.**

### ⇒ Três defeitos, três alavancas distintas

| amp | defeito | onde atacar |
|---:|---|---|
| 0,25 | **offset** herdado da fase inicial | relógio de assentamento (`N_emb`) — e o sweep leva o MAE a **0,0563**, contra limite 0,05: **1,13×**, perto |
| 0,50 | **taxa** no meio da curva | nem offset nem `N_emb`; não identificado |
| 1,00 | **relógio de colapso** muito adiantado | canal que dispara o colapso, não o assentamento |

⚠️ ⇒ **a fonte não tem UM defeito.** Tratar as três como uma classe foi o erro estrutural
deste documento desde o início — e é o mesmo padrão que o `YANG_2023` ensinou (3 regimes, 3
sinais, não formam classe).

## 0b. ✅ DIAGNÓSTICO DO CANAL (15:4x) — é o rotacional, e há DOIS travamentos empilhados

Pedido do professor. ⚠️ **Primeiro, um defeito de instrumento meu:** eu lia
`r.mech_decomp`, que **não existe** — o atributo é **`r.decomp`**. `getattr` devolvia `None`
em silêncio, e foi por isso que eu escrevi "a decomposição veio vazia" mais acima. Com o
nome certo:

### Decomposição por canal (cumulativa)

| amp | canal dominante | % | 50 % dele em | 2º canal | % |
|---:|---|---:|---:|---|---:|
| 0,25 | **embedding** | **86,2** | N=2 | creep | 13,8 |
| 0,50 | **rotational_loosening** | **60,6** | **N=79** | embedding | 34,5 |
| 1,00 | **rotational_loosening** | **48,7** | **N=20** | embedding | 47,4 |

⇒ na `0,25` os canais de slip são **todos zero** (stick permanente) — o defeito é 100 %
assentamento, como a §0a já indicava pelo alinhamento.
⇒ nas duas que falham o dominante é o **rotacional**, e o relógio dele corre **4× mais
rápido** para 2× de amplitude (N=79 → N=20).

### Travamento 1 — o canal é BIFURCADO, não gradual

Varredura de `tr_loose_gain` (constante de taxa do canal):

| gain | MAE 0,5 mm | MAE 1,0 mm | MAE 0,25 mm | fração rotacional |
|---:|---:|---:|---:|---:|
| 2,0 (adotado) | 0,1257 | 0,4802 | 0,1017 | 60,6 / 48,7 % |
| 1,0 | **0,1211** | **0,4385** | 0,1017 | 57,6 / 48,0 % |
| 0,5 | 0,2608 | **0,3464** | 0,1017 | **−0,0 / −0,0 %** |
| 0,25 · 0,1 · 0,03 | 0,2608 | 0,3464 | 0,1017 | −0,0 % |

⇒ **abaixo de 0,5 o canal DESLIGA** (fração −0,0 %) e tudo congela — os quatro últimos
valores são **idênticos**. Não é saturação suave: é **bifurcação**. O canal rotacional **ou
dispara e vai ao piso, ou não dispara**. É a mesma bifurcação arrest/runaway que o
`CLAUDE.md` documenta em `self_locking_gate`, aqui medida por varredura.

⇒ e as duas curvas querem **direções opostas**: de 2,0 para 0,5 a `0,5 mm` **piora**
(0,126 → 0,261) e a `1,0 mm` **melhora** (0,480 → 0,346). **Nenhum valor único serve.**

⇒ a `0,25 mm` é **insensível em todos os gains** (0,1017 exato), confirmando embedding puro.

### Travamento 2 — o piso adotado de 0,1 é o TETO DA PERDA

| gain | ratio final do modelo | ratio final do dado |
|---:|---:|---:|
| 2,0 | 0,0973 / 0,0966 | **0,0047 / 0,0029** |
| 1,0 | 0,1261 / 0,0991 | idem |
| 0,5 | 0,6087 / 0,5036 | idem |

⇒ com o canal ligado o modelo **para em ~0,10** — porque `loose_arrest_floor` = **0,1** no
grupo adotado. O dado vai a **0,0047 e 0,0029**, ou seja **20–33× mais baixo**.

⚠️ **Nenhum `tr_loose_gain` alcança o dado**, por construção: o piso impede a descida. O
`gain` só escolhe **quando** o modelo chega a 0,10 — nunca **até onde** desce.

### ⇒ O diagnóstico, em uma frase

> O canal do colapso é o **rotacional**; ele é **bifurcado** (liga-ou-nada) e está **limitado
> por um piso de 0,1** que o dado atravessa por 20–33×. As duas curvas que falham pedem
> **relógios opostos**, então o defeito não é o valor de uma constante — é que **o piso e a
> bifurcação, juntos, tornam a cauda inalcançável**.

⚠️ **E isto conecta ao item R desta mesma mesa**, por outro caminho: lá o `loose_arrest_floor`
do `ECCLES` estava **acima** do que o dado sustenta e *segurava o modelo de pé*; aqui o do
`LU` está **acima do que o dado atinge** e *impede o modelo de cair*. **Mesma constante, mesmo
tipo de defeito, duas fontes.**

⚠️ **Não proponho mexer no piso do `LU`.** O `loose_arrest_floor` = 0,1 é override **adotado**,
e mudá-lo é adoção. Além disso a §5a-b mostrou que a folga ⌀10/⌀8 dá razão física para
*algum* auto-travamento nesta bancada — o que está errado é o **valor**, e ele precisa de
procedência, não de fit. **Fica na mesa.**

### O CONTROLE que decide: a leitura L24 do cru, por curva

| amp | L24 do CSV cru | `plateau` | piso adotado | razao |
|---:|---:|:--:|---:|---|
| 0,25 | **0,8284** | **True** | 0,1 | **8x BAIXO** |
| 0,50 | 0,0111 | False | 0,1 | 9x alto |
| 1,00 | **0,0075** | False | 0,1 | **13x alto** |

=> **o MESMO piso de 0,1 e 13x ALTO para a de 1,0 mm e 8x BAIXO para a de 0,25 mm.**
As tres arrestam em niveis completamente diferentes (0,828 / 0,011 / 0,008), e um valor
unico nao pode servir as tres — o que fecha o diagnostico: **nao e constante mal
ajustada, e constante ERRADA POR CONSTRUCAO nesta fonte.**

(Nota: a `0,25` tem `plateau=True` em 0,828 — ela ARRESTA DE VERDADE, alto. As outras
duas dao `plateau=False`, ou seja **nao arrestam**: colapsam. Sao regimes distintos.)

## 0c. ⛔ PISO LIDO DO CRU: rota FALSIFICADA (15:4x) — e corrige a minha própria §0b

A §0b terminou insinuando rota: se o piso de 0,1 é *"13× alto para uma e 8× baixo para
outra"*, um piso **por curva lido do cru** (procedência L24, *"ler em vez de fitar"*) deveria
ajudar. **Medi antes de propor. Não ajuda.**

| amp | piso 0,1 (adotado) | piso L24 do cru | MAE 0,1 | MAE L24 | efeito |
|---:|---:|---:|---:|---:|---|
| 0,25 | 0,1 | 0,8284 | 0,1017 | **0,1017** | **INERTE** (idêntico) |
| 0,50 | 0,1 | 0,0111 | 0,1257 | **0,1848** | **piora 47 %** |
| 1,00 | 0,1 | 0,0075 | 0,4802 | **0,5670** | **piora 18 %** |

### Por que, e o que isso corrige em mim

**Baixar o piso deixa o modelo cair MAIS FUNDO — mas ele já caía CEDO DEMAIS.** O piso nunca
foi o problema: era o **relógio**. Afrouxar o teto de uma queda prematura só a torna mais
prematura.

⚠️ **E o caso da `0,25` desmonta metade do meu enquadramento:** trocar o piso de 0,1 para
0,8284 dá resultado **idêntico ao dígito**, porque o modelo **para em 0,74 e nunca chega ao
piso**. Chamar o piso de *"8× baixo"* era aritmeticamente certo e **operacionalmente vazio** —
uma constante que o modelo não alcança não é apertada nem folgada, é **inerte**.

⇒ ou seja: o piso é **inerte onde eu disse "baixo"** e **nocivo onde eu disse "alto"**. A
frase da §0b (*"constante errada por construção"*) fica de pé como **descrição do valor**, mas
**não** como indicação de rota.

### ⇒ As DUAS constantes do canal estão medidas, e nenhuma é rota

| constante | comportamento medido | serve? |
|---|---|:--:|
| `tr_loose_gain` | **bifurcado**: desliga abaixo de 0,5; as duas curvas querem direções opostas | ⛔ |
| `loose_arrest_floor` | inerte na que arresta; **piora** nas duas que colapsam | ⛔ |

⇒ **o defeito não é de constante nesta fonte.** É estrutural: o canal rotacional **liga-ou-
nada** e, ligado, tem relógio errado em ambas as direções — rápido demais na `1,0` e (pelo
sinal do resíduo) devagar demais na `0,5` no trecho médio.

⚠️ **Não proponho forma nova aqui.** Já assinei uma hoje que perdeu o objeto ao ser medida
(§0/§5e), e o padrão a evitar é exatamente este: nomear forma a partir de duas constantes que
falharam. O que ficou **medido e reutilizável** é o retrato: *canal rotacional bifurcado, com
piso que veda a cauda, em fonte de folga ⌀10/⌀8*.

## 1. O defeito, medido

A hipótese do professor era que a não-convergência vem de **o modelo não prever a faixa
inicial sem perda de pretensão**. ⚠️ **O DEFEITO está confirmado; a NÃO-CONVERGÊNCIA não —
ver a errata da §0**, que mede a faixa inicial em ~4 % do erro. O que segue é o defeito
pontual, que é real e grande:

| amp (mm) | dado @N=1 | modelo @N=1 | dado sai de 0,95 | modelo sai de 0,95 | MAE | res.máx |
|---:|---:|---:|---:|---:|---:|---:|
| 0,25 | **0,9992** | 0,7957 | N=**24** | N=1 | 0,1017 | 0,2314 |
| 0,50 | **0,9993** | 0,7295 | N=**27** | N=1 | 0,1257 | 0,3936 |
| 1,00 | **0,9991** | 0,6191 | N=**56** | N=1 | **0,4802** | **0,8553** |

⇒ o dado perde **~0,08 % no ciclo 1**, e essa perda é **constante nas três amplitudes**.
O modelo perde **20 % / 27 % / 38 %** — e a perda **cresce com a amplitude**.

⛔ ~~E o patamar do dado ALONGA com a amplitude (24 → 27 → 56), a assinatura mais
informativa do conjunto.~~ **RETRATADO na §5a:** corrigido o eixo x (que a §5 mede como
1,04× / 1,22× / 1,42× longo), os patamares são **23 → 22 → 39** — as duas menores **iguais**.
Metade do "alongamento" era o defeito de digitalização da §5 entrando pela porta de trás.

## 2. São DOIS defeitos, não um — e o canal difere por amplitude

Instrumentando `resolve_transverse_slip`:

| amp | slip resolvido | leitura |
|---:|---|---|
| 0,25 mm | **0 em 120 de 120 ciclos** | **stick permanente** |
| 1,00 mm | **0,709 mm já no ciclo 1** (71 % do δ) | **gross slip imediato, zero stick** |

⇒ **em amp 1,0** o modelo entra em gross slip no ciclo 1 contra 56 ciclos de patamar medido:
falta a **fase de stick**.
⇒ **em amp 0,25** o modelo está em stick permanente **e mesmo assim** cai 24 % em 3 ciclos
(1,0000 → 0,7614 em N=3 → 0,7453 em N=80). Com slip = 0, só embedding e creep podem mover
isso.

### 2a. A constante responsável tem nome e valor: `N_emb = 0,5`

O embedding do engine é `δ_emb(N) = δ_target·(1 − e^{−N/N_emb})`. Com **`N_emb = 0,5`**
(override adotado nesta fonte, com `emb_depth` = 8 µm):

| N | fração do assentamento consumida |
|---:|---:|
| 1 | **86 %** |
| 2 | **98 %** |
| 3 | **99,8 %** |

⇒ o modelo está configurado para **consumir o assentamento inteiro em meio ciclo**.
Contra um patamar medido de 24–56 ciclos, isso é um relógio **~50–110× rápido**.

## 3. ⚠️ O paper parece contradizer o professor — e a contradição RESOLVE por PROTOCOLO

O texto do paper diz o **oposto** de patamar:

> *"Taking **5–10 cycles** of cyclic loading as a boundary, the pre-loading relaxation is
> divided into two stages. The **first stage is a stage of rapid decrease** in bolt
> pre-loading, and the second stage is the slow decrease process."*

e dá a física:

> *"The first stage is caused by **excessive local stress caused by the steel plate extrusion
> bolt** and excessive pressure on the annular support surface of the fastener head. At the
> same time, the **material yields and undergoes plastic deformation**."*

⚠️ Lido isolado, isso **valida a forma do nosso modelo** (queda rápida e depois declínio
lento) e refutaria o patamar. **Mas essa prosa não é da Fig. 14.**

**A resolução é a mesma distinção de protocolo que a retratação de 2026-08-14 estabeleceu e
que o `CLAUDE.md` registra:**

| figura | seção | protocolo |
|---|---|---|
| **Fig. 13–14** | §3.1.3 | **máquina, half-sine, 1 Hz** |
| Fig. 18–21 | §3.2 | **controle MANUAL** (*"manual control of a universal testing machine"*) |

A prosa dos *"5–10 ciclos"* e da *"plastic deformation"* está no fecho do §3.2 e nas
conclusões — descreve o protocolo **manual**. A Fig. 14 é **half-sine de máquina**.
⇒ **o professor está certo, e a razão é de protocolo:** o patamar existe **no half-sine**.

## 4. Por que o half-sine tem patamar — o paper entrega o mecanismo

> *"the hole diameter of the nickel steel plate is **10 mm**, the bolt diameter is **8 mm**,
> and there is an **unavoidable gap** between the two… The change in displacement will have
> **repeated impacts on the center gap**"*
>
> *"The existence of a **gap** between the nickel steel plate and the bolt leads to
> **instability in the displacement when the plate returns to the initial position**… This
> fluctuation is **unavoidable** because the gap between the two cannot be eliminated."*

⇒ **folga radial de 1 mm** (furo 10, parafuso 8) — **exatamente a escala das amplitudes
ensaiadas** (0,25 / 0,5 / 1,0 mm). E o half-sine move a placa **0 → +δ → 0**, num só sentido.

⇒ **o parafuso não pode agir como pino:** com 1 mm de folga e δ ≤ 1,0 mm, o fuste
praticamente não bate na parede do furo, então a carga transversal é transmitida **só por
atrito** na interface das placas. Enquanto o atrito segura, **não há slip no assento e não
há perda**. O patamar é compatível com uma **fase de stick**.

⛔ ~~E o alongamento dele com a amplitude é consistente com mais folga consumida antes do
contato.~~ **FALSIFICADO na §5a(b):** `δ/folga ≤ 1` nas TRÊS ⇒ o fuste **nunca** alcança a
parede do furo, então não há contato a ser esperado e **consumo de folga não pode encerrar
o patamar**. A folga explica **por que o parafuso não é pino** — isso sobrevive —, e nada
além disso.

⚠️ **Nosso modelo não tem nenhuma representação disso.** Medido: `d_hole_mm` = `None` no
grupo adotado, e **`JointMaterial` não tem NENHUM campo** de folga/clearance/backlash
(busca por `clear|gap|hole|slack|backlash` → conjunto **vazio**). O engine recebe
`delta_amp = 1,0 mm` **direto** como driver de slip.

## 5. ⚠️ Um segundo achado, que NÃO era a pergunta: o eixo x da CSV corre LONGO

| amp | CSV vai a N= | paper imprime | razão |
|---:|---:|---:|---:|
| 1,00 | **185** | **130** (*"at 73 cycles the bolt had loosened"*) | **1,42×** |
| 0,50 | **610** | **500** | 1,22× |
| 0,25 | **1040** | **1000** | 1,04× |

⛔ ~~Fica registrado como pendência de digitalização.~~ **RESOLVIDO na §5b:** medida a
própria figura, ela vai a **1072 / 704 / 297 s** — ou seja, **a FIGURA excede a prosa nas
três**, e a CSV fica ENTRE as duas. O conflito é **prosa × figura, dentro do paper**;
a CSV está adequada e não há re-digitalização a fazer.

✅ **Mas o NÍVEL está validado, e isso é o que sustenta a §1:** a CSV da 0,25 mm termina em
**0,8293**, e o paper diz *"**10 539 N** of pre-loading remained, with a loss of only
**15 %**"* ⇒ **0,85**. Concordam a **1,7 %**.

⇒ **como a mesma digitalização acerta o ponto final a 1,7 %, o patamar inicial é DADO REAL**
— não artefato de extração. É esse controle que impede de descartar a §1 como erro de CSV.

## 5a. ⛔ ERRATA (mesma sessão, 14:1x) — METADE do "alongamento" era ARTEFATO, e isso
inverte a minha recomendação

> Eu publiquei acima que *"o patamar ALONGA com a amplitude (24 → 27 → 56)"* e usei isso
> como a assinatura mais informativa, explicando-a por *"mais folga consumida antes do
> contato"*. **Testei as duas coisas antes de propor rota, e as duas caem.**

### (a) O alongamento não sobrevive à correção do eixo x — que eu mesmo tinha medido

| amp | N@0,95 bruto | fator do paper | **N@0,95 corrigido** |
|---:|---:|---:|---:|
| 0,25 | 24 | 1000/1040 = 0,962 | **23,1** |
| 0,50 | 27 | 500/610 = 0,820 | **22,1** |
| 1,00 | 56 | 130/185 = 0,703 | **39,4** |

⛔ **ESTA TABELA ESTÁ MORTA — ver §5b.** Ela multiplica por `prosa/CSV`, e a §5b mediu que
a **prosa é que discorda da figura**. Sem premissa, sem correção: o patamar vigente é o
bruto, **24 → 27 → 56**. O texto abaixo fica como registro do raciocínio.

⇒ ~~**23 → 22 → 39**, não 24 → 27 → 56.~~ As duas amplitudes menores dariam patamar
**essencialmente IGUAL** (23,1 e 22,1), e só a de 1,0 mm é maior. ⚠️ O fator de correção é
justamente o **maior onde eu vi o maior alongamento** (0,703 em amp 1,0 contra 0,962 em
0,25) — ou seja, o efeito que eu chamei de assinatura estava **contaminado pelo defeito de
digitalização que eu havia acabado de registrar na §5**, e não liguei os dois.

### (b) Consumo de folga está FALSIFICADO como o que encerra o patamar

| amp (mm) | folga radial | δ / folga | o fuste toca a parede? |
|---:|---:|---:|:--:|
| 0,25 | 1,00 | 0,25 | **não** |
| 0,50 | 1,00 | 0,50 | **não** |
| 1,00 | 1,00 | 1,00 | só no extremo |

⇒ **em nenhuma das três o fuste alcança a parede do furo** (δ/folga ≤ 1). Se não há contato
a ser esperado, **consumo de folga não pode ser o que termina o patamar** — e era isso que
eu tinha escrito. A folga segue explicando **por que o parafuso não é pino** (a carga vai
por atrito, §4), mas **não** o fim do patamar.

### (b-bis) ⚠️ A minha própria correção é CONDICIONAL — li a legenda em vez da PROVA GRAVADA

> **14:2x.** Fui verificar a §5 no PDF e me convenci, pela **legenda**, de que a Fig. 14
> não plota pretensão: *"Waveform curve under half sine wave control. (a) Half sine wave
> **displacement** control. (b) **Displacement** change rule."* Cheguei a levantar dúvida de
> procedência das 3 CSVs. **A dúvida está errada, e a nota de aparato já respondia:**
>
> > *"**Fig. 14a digitalizada** (`New_Theory/digitize_lu2024_fig14.py`, auto-calibração por
> > ticks + **round-trip contra as âncoras da prosa: fim do 0,25 mm lê 10511 vs 10539 N**):
> > 3 corridas LONGAS a 22 N·m — repetições independentes das condições da fig18 com
> > **janelas 3–10×**… F0 da fig14 = pico digitalizado por curva (prosa: 12398/12285/12696;
> > picos lidos 2–4 % acima)."*
>
> ⇒ a Fig. 14a **carrega traço de força**, a legenda é que é abreviada; e a digitalização
> tem **round-trip a 0,27 %** no ponto final e F0 a 2–4 % dos três valores da prosa.
> **As CSVs são legítimas e validadas.** Violei a regra *"LEIA A PROVA GRAVADA antes de
> escolher o teste"* — a prova estava em `apparatus_notes/lu2024_sensors_M8.md`.
>
> ⚠️ **E isso enfraquece a minha correção (a):** para "corrigir" o patamar eu multipliquei
> por `paper/CSV`, o que **assume que a prosa está certa e a CSV errada**. A nota registra
> as extensões (~1040/610/185) como **deliberadas** — *"janelas 3–10×"* — e **não** as
> reconcilia com os 1000/500/130 da prosa. ⇒ o conflito da §5 **existe e segue aberto**, mas
> **qual lado está errado NÃO está estabelecido**.
>
> **Portanto a correção (a) é CONDICIONAL:** *se* a prosa fixar os ciclos, os patamares são
> 23/22/39; se a CSV estiver certa, são 24/27/56 e o alongamento volta. **As duas leituras
> estão na mesa**, e é isso que o W3 tem de resolver **antes** de qualquer ajuste de `N_emb`.

### (c) ⇒ A recomendação se INVERTE: W1 passa a ser a rota indicada

Um patamar de **~22–23 ciclos quase independente da amplitude** nas duas condições menores
é exatamente a assinatura de um **relógio de assentamento** — que é o que o `N_emb`
controla —, e **não** de um mecanismo dirigido por slip ou folga.

⚠️ **A minha advertência contra o W1** (*"conserta o número sem a física, e não explicaria
por que o patamar alonga"*) **caiu com o alongamento**: ela pedia que o W1 explicasse um
efeito que, corrigido, é menor e não-monótono. **O W1 é a rota fisicamente indicada**, e a
procedência dele é o próprio patamar medido (`N_emb` da ordem de 8–12 em vez de 0,5, a
aferir por ajuste ao patamar).

⚠️ **O que fica ABERTO e honesto:** a de 1,0 mm segue com patamar **1,7× maior** que as
outras duas mesmo corrigida (39 contra ~22). Isso não é explicado por relógio único, e é a
única parte do alongamento que resistiu. Não invento mecanismo para ela aqui.

⚠️ **E o W3 sobe de prioridade**: ele deixou de ser "pendência colateral" e passou a ser
**pré-requisito** — foi o eixo x errado que produziu a assinatura falsa. Qualquer ajuste de
`N_emb` feito antes de corrigir o eixo estaria fitando um patamar de comprimento errado.

## 5b. ✅ W3 RESOLVIDO (14:3x) — a FIGURA excede a prosa, e a CSV fica NO MEIO

Medido na própria Fig. 14a, com o **mapeamento do script** (não o meu chute) e o **critério
de run contíguo ≥ 2 px** que o script usa para separar curva de resíduo:

```
x0 = 302 px  (t = 0) · dx = 1,1720 px/s · borda direita = 1202 s
```

⚠️ O controle que valida a calibração é o **comentário do próprio script** — *"o tick
extremo pode COINCIDIR com a moldura (aqui **t=1200 == borda direita**)"* — e a medição dá
**1202 s**. Bate.

| curva | **FIGURA** | CSV adotada | prosa |
|---|---:|---:|---:|
| preta (0,25 mm) | **1072 s** | 1040 | 1000 |
| vermelha (0,5 mm) | **704 s** | 610 | 500 |
| azul (1,0 mm) | **297 s** | 185 | 130 |

⇒ **a figura excede a prosa nas TRÊS**, e a CSV fica **entre** as duas. A 1 Hz, s = ciclos
exatamente (paper: *"the vibration frequency is 1 Hz"*), então a unidade não explica nada.

### O que isso decide

**1. A CSV NÃO deve ser "corrigida" para a prosa.** Ela está **mais perto da figura** do que
a prosa está. Encurtá-la para 1000/500/130 a afastaria do que está plotado.

**2. ⛔ Portanto a minha §5a(a) CAI — pela segunda vez, e agora por medição direta.** Eu
havia "corrigido" os patamares multiplicando por `prosa/CSV` (0,962 / 0,820 / 0,703),
assumindo prosa certa. **A premissa é falsa.** Os fatores honestos, contra a FIGURA, são
**1040/1072 = 0,970 · 610/704 = 0,867 · 185/297 = 0,623** — e vão na direção de a CSV estar
**curta**, não longa.

⇒ **o alongamento do patamar VOLTA** e é a leitura vigente: **24 → 27 → 56** (dado bruto),
porque não há razão medida para reescalar a CSV.

**3. O conflito real é PROSA × FIGURA, dentro do paper** — não CSV × paper. O paper diz
*"the total number of cycles… was 130"* e plota ~297 s na mesma condição. Isso é
inconsistência **da fonte**, e a leitura mais natural é que a prosa reporta os ciclos
**úteis/planejados** (ela mesma diz *"at 73 cycles the bolt had loosened and had no
tightening effect"*) enquanto a figura mostra o **registro completo**, cauda morta inclusa.
⚠️ Isto é **interpretação**, não medição — fica marcado como tal.

**4. ⇒ NÃO há re-digitalização a fazer.** O W3 se fecha com *"a CSV está adequada; quem
discorda de si mesmo é o paper"*. A pendência da §5 deixa de ser defeito nosso e passa a
ser **caveat da fonte**, a registrar na nota de aparato.

## 5c. ✅ O RESÍDUO tem forma NOMEADA, e a alavanca que pareceria servir é INERTE aqui

Com o eixo resolvido (§5b), o patamar a explicar é o **bruto: 24 / 27 / 56 ciclos** — ou
seja, **cresce com a amplitude transversal**. Um `N_emb` único não produz isso. Fui ver se o
engine já tinha alavanca.

**Tem — e não serve.** O `emb_amp_exp` (ρ-unificação, §4.18) faz o assentamento depender da
amplitude, mas é dirigido por `rho = F_ax / state.F_0_init` (engine L1293), com
`S_rho = min(1, (rho/rho_ref_emb)^emb_amp_exp)`. E o comentário do próprio engine declara o
escopo: *"componente **AXIAL** (transversal: `F_ax~0` ⇒ `S=1`)"*.

⚠️ **Medido nesta fonte:** `transverse_displacement_mm` = 0,25 / 1,0 e **nenhuma** amplitude
axial (`force_amplitude_N` ausente) ⇒ fonte **transversal-pura**. Logo:

| estado | efeito |
|---|---|
| `emb_amp_exp = 0` (adotado) | `S_rho` = 1,0 **exato** — ramo inerte |
| `emb_amp_exp > 0` com `F_ax = 0` | `(0/0,667)^q = 0` ⇒ **zera** o assentamento, não o retarda |

⇒ **a alavanca é estruturalmente inerte aqui, e ligá-la faria o oposto do necessário.** É a
mesma classe de inércia que a sessão paralela documentou para o `F_amp` no `YANG_2021`
(*"estruturalmente inerte em fonte transversal-pura"*).

### ⇒ FORMA FALTANTE, nomeada com precisão

> **O engine não tem mecanismo pelo qual a amplitude TRANSVERSAL module o RELÓGIO de
> assentamento.** Existe um para a amplitude **axial** (`emb_amp_exp`), e ele não alcança
> fonte transversal.

Isso separa limpo o que o W1 pode e não pode fazer:

| o que | W1 (`N_emb` per-fonte) |
|---|---|
| **nível** da faixa inicial (0,08 % medido contra 20–38 % do modelo) | ✅ alcança |
| **comprimento** médio do patamar (~24–56 contra 0,5 ciclo) | ✅ alcança |
| **tendência** com a amplitude (24 → 27 → 56) | ⛔ **não alcança** — exige forma nova |

⚠️ ⇒ **a advertência que eu havia retirado às 14:1x volta a valer**, agora com a causa
medida em vez de suposta: o W1 conserta a maior parte do erro e deixa um **resíduo de
tendência declarado**, que nenhuma constante existente cobre.

## 5d. ⛔ W1 FALSIFICADO como constante compartilhada (15:1x) — os ótimos são DISJUNTOS

Antes de escrever o prereg do W1, varri `N_emb` só-leitura. A grade inicial (0,5–30) era
**monótona até a borda**, então a **disciplina D-L** mandou estender — e a extensão matou o
candidato.

**Ótimo de cada curva, medido na grade 0,5 … 800:**

| amp (mm) | `N_emb` ótimo | MAE ali | MAE em `N_emb`=0,5 | forma da curva de MAE |
|---:|---:|---:|---:|---|
| 0,25 | **800** (fronteira) | 0,0563 | 0,1017 | monótona decrescente |
| 0,50 | **30** (INTERIOR) | 0,0830 | 0,1257 | mínimo real; **piora** depois |
| 1,00 | **800** (fronteira) | 0,2333 | 0,4802 | monótona decrescente |

⇒ **os três ótimos são DISJUNTOS.** A de 0,5 mm tem mínimo interior em **30** e vai a
**0,166 em 800** — **3× pior** que no seu ótimo. As outras duas só melhoram até a borda.

⚠️ **E o critério de soma engana:** a soma de MAE cai monotonicamente (0,708 → 0,457) e
escolheria `N_emb` = 800 — **degradando a curva do meio em 100 %** enquanto a de 1,0 mm
arrasta o total. Adotar por soma seria comprar uma curva com outra.

### Por que isto FECHA o W1 em vez de só reduzi-lo

**Nenhuma constante compartilhada serve às três**, e `N_emb` **per-curva** seria fit por
curva sem procedência — exatamente o que o **item D** da doutrina proíbe e o que o
precedente **D-I** condena (*"fitar um membro contra as irmãs"*).

⚠️ **E o teto é baixo mesmo no melhor caso:** no ótimo individual de cada uma, os MAEs são
**0,056 / 0,083 / 0,233** — ou seja **1,1× / 1,7× / 4,7×** o limite. **Nenhuma das três
fecha**, nem com liberdade total no relógio.

⚠️ **O `res.máx` da pior nem se move:** 0,8553 → 0,8595 de `N_emb` 0,5 a 30. O relógio de
assentamento **não toca o erro dominante** da `amp1p0`.

### ⇒ Confirmação INDEPENDENTE da forma faltante

A §5c nomeou a forma por **inspeção do engine** (o `emb_amp_exp` é axial e inerte aqui).
Esta varredura chega ao **mesmo lugar por outro caminho**: os ótimos de `N_emb` **crescem
com a amplitude de forma não-monótona** (800 / 30 / 800), o que é a assinatura de que
**falta um grau de liberdade ligado à amplitude transversal** — não de que o relógio esteja
mal ajustado.

⇒ **duas rotas independentes, mesmo veredito.** É o requisito (a) da regra de parada
(*"classe identificada por ≥2 instrumentos independentes"*) satisfeito para esta forma.

## 5e. ⛔ O "patamar de 24–56 ciclos" é ARTEFATO DE LIMIAR — a faixa real é ~3 ciclos

O comprimento do patamar que este documento usou (24 / 27 / 56) veio do limiar **0,95**.
Medindo o mesmo dado cru em vários limiares:

| amp (mm) | N@0,99 | N@0,98 | N@0,95 | N@0,90 |
|---:|---:|---:|---:|---:|
| 0,25 | **3** | 5 | 24 | 27 |
| 0,50 | **4** | 27 | 27 | 27 |
| 1,00 | **3** | 3 | 56 | 56 |

⇒ **na `N@0,99` as três dão 3 / 4 / 3 — praticamente IGUAIS.** Toda a "dependência com a
amplitude" mora entre 0,98 e 0,95.

⚠️ **E ali o dado não sustenta leitura nenhuma:** a `N@0,98` vai **5 → 27 → 3**, violentamente
não-monótona. Os valores **repetem** (27, 27, 27, 56, 56) porque as curvas têm poucos pontos
nessa região e o cruzamento cai no **mesmo x amostrado**. É resolução de digitalização, não
física.

⇒ **A faixa inicial real é de ~3–4 ciclos e NÃO depende da amplitude.** Isso é consistente
com o único ponto que sempre foi robusto — `r(N=1)` = 0,9991/0,9993/0,9992, também
independente da amplitude.

### O que isto encerra

| afirmação | estado |
|---|---|
| o dado tem faixa inicial sem perda | ✅ **sobrevive** (3–4 ciclos, ~0,08 % em N=1) |
| o modelo a destrói no ciclo 1 | ✅ **sobrevive** (`N_emb`=0,5 ⇒ 86 % em N=1) |
| ~~o patamar alonga com a amplitude~~ | ⛔ **artefato de limiar + amostragem** |
| ~~folga explica o alongamento~~ | ⛔ falsificado (§5a-b) |
| ~~falta forma de amplitude transversal no relógio~~ | ⛔ **sem alvo** — não há tendência a explicar |
| ~~a faixa inicial causa a não-convergência~~ | ⛔ **~4 % do erro** (§0) |

⚠️ ⇒ **a "forma faltante" da §5c perde o objeto.** Ela existia para explicar uma tendência
que **não é real**. O `emb_amp_exp` segue estruturalmente inerte em fonte transversal — isso
é fato de engine e continua verdadeiro —, mas **não há defeito medido que ele deixaria de
cobrir aqui**.

## 6. O que isto propõe — e o que NÃO faço

**Forma faltante nomeada:** *transmissão por folga* — o deslocamento **imposto na placa**
não é o deslocamento que o **parafuso** vê. Hoje o engine iguala os dois.

| # | rota | custo | o que afirma |
|---|---|---|---|
| **W1** | relógio de assentamento honesto nesta fonte: `N_emb` de 0,5 para a escala medida do patamar (24–56 ciclos) | baixo (1 constante, procedência = o próprio patamar) | trata o **sintoma** em amp 0,25, onde o canal é embedding |
| **W2** | **forma nova**: folga `d_hole − d_bolt` reduzindo o δ efetivo antes de virar driver de slip | médio, **default-inerte** | trata a **causa** nas três, e é o que o paper descreve |
| **W3** | re-digitalizar a Fig. 14 contra os 130/500/1000 ciclos impressos | médio | resolve a §5, **não** a §1 |

⛔ **Não executo nenhuma.** W2 é **forma nova de engine** e W1 muda config adotada — as duas
exigem assinatura. W3 é dado, e mexeria numa fonte com adoções recentes da sessão paralela.

⚠️ **E registro o risco de W1 isolada:** ela conserta o número sem a física. O paper diz que
a folga *"cannot be eliminated"* e que ela desestabiliza o retorno da placa — se a causa é
folga, esticar `N_emb` é ajustar o relógio do canal errado, e não explicaria por que o
patamar **alonga** com a amplitude.

## Reprodutibilidade

```bash
# metricas e patamar
PYTHONPATH=src py -3.12 New_Theory/regra_de_parada_triagem.py
# slip resolvido: wrapper em dsa.resolve_transverse_slip (sonda inline no commit)
# paper: PyMuPDF sobre sensors-24-03306.pdf (25 pp)
```

Usa `load_full_curve` (CSV **cru**), `CaseResult.from_dict`, `rn._effective_overrides` e
`rn._adopted_for` — nenhuma reimplementa regra. ⚠️ O patamar foi lido do **cru**, nunca de
`metric_data` (que é pós-`FLOOR_TRIM`).
