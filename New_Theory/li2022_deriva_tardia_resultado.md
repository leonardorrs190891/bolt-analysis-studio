# Deriva tardia do LI_2022 — o defeito é ATRIBUIÇÃO DE CANAL, provado por álgebra

**2026-08-05** · ataque à deriva tardia sob o MANDATO PERMANENTE; prereg D-N
(`2026-08-05-li2022-amplitude-por-frequencia`). Fingerprint `e38eed05fa47`.
**NADA FOI ADOTADO.**

## O que eu fui atacar, e o que encontrei

O alvo era a "deriva tardia" — o excesso de σ da `li2022ti_axial_10Hz_full`
concentrado além de 200 k ciclos. Medido ponto a ponto, o defeito **não é falta
de deriva tardia**:

| N | dado | modelo | resíduo |
|---:|---:|---:|---:|
| 20 000 | 0,8957 | 0,9423 | **+0,0466** |
| 50 000 | 0,8696 | 0,9213 | +0,0517 |
| 100 000 | 0,8609 | 0,8937 | +0,0328 |
| 200 000 | 0,8522 | 0,8461 | −0,0061 |
| 300 000 | 0,8435 | 0,8030 | −0,0405 |
| 330 000 | 0,8348 | 0,7907 | **−0,0441** |

**O resíduo troca de sinal em 200 k** e **49,7 % da variância** está nos 2
pontos tardios. O dado cai 6 % em 310 k ciclos; o modelo cai 15 % e **não
desacelera**. O defeito é **falta de saturação**, não falta de perda.

## A leitura do PDF: três coisas distintas que eu vinha misturando

Fui ao PDF (Fig. 8, `li2022_triboint_axial_freq.pdf`) e extraí a figura como
imagem — não confiei em legenda nem em resumo, que é a regra que o erro do
companion do IJPEM ensinou.

**1. A dependência de frequência é de INPUT, e o paper a mede.** A Fig. 8(b)
traz a envoltória do parafuso com valores **anotados**:

| f | F_B,max | F_B,min | oscilação | razão |
|---:|---:|---:|---:|---:|
| 10 Hz | 19,10 | 9,76 | **9,34 kN** | 1,000 |
| 15 Hz | 17,53 | 10,22 | **7,31 kN** | 0,783 |
| 20 Hz | 16,53 | 10,82 | **5,71 kN** | 0,611 |

E os autores escrevem a cadeia causal duas vezes (p5 e p6): *"the higher the
frequency, the smaller the change amplitude of the bolt axial force"* →
*"resulting in aggravation of the fretting wear (...) and increased damage to
the thread surface"*. **O runner entrega `F_amp = 10 000 N` às três**
(`_AXIAL_F_AMP`, um valor por fonte).

**2. O nível da `axial_10Hz_full` é artefato de RESOLUÇÃO.** Ela vem da
Fig. 8(a), eixo **0–24 kN**; a `axialmin_*` vem da Fig. 8(c), eixo
**9,5–12,0 kN** — ~10× mais fino. As duas discordam em **0,0315** no mesmo N
(σ da diferença só 0,0083 ⇒ mesma forma, degrau constante), e 0,0315 é **1,6 %
da altura do eixo da 8a**. A 8c é a **prosa-confirmada** (17,9 % = 0,821).

**3. O Φ do modelo é ~9× pequeno.** A oscilação medida do parafuso é 9,34 kN;
o modelo calcula Φ=0,104 ⇒ 1,04 kN. Depende da convenção de A_F (pico ou
pico-a-pico) e fica como questão separada, **não usada** neste resultado.

## G1 (o gate que decide): o vão APARECEU, mas fora da banda

Só a correção de input, **zero re-fit**:

| razão de perda | base | **corrigido** | dado | previsto `r^1,5` |
|---|---:|---:|---:|---:|
| 20 Hz / 10 Hz | 0,997 | **0,710** | **0,498** | 0,478 |
| 15 Hz / 10 Hz | 0,999 | 0,832 | 0,791 | 0,693 |

Banda declarada: 0,478 ± 0,08. Medido **0,710** ⇒ **G1 REPROVA no número**.

⚠️ **Mas o rótulo do ramo que eu escrevi — *"o input não é a causa"* — é
factualmente ERRADO e não vou aplicá-lo.** O vão apareceu e fechou **57 %** da
lacuna (de 0,997 para 0,710, onde o alvo é 0,498). O que falha é a versão
**forte** da hipótese: que o input sozinho, com o expoente já adotado,
reproduziria o vão.

⚠️ **E o meu desenho tinha um defeito estrutural que eu devia ter previsto:**
escalando **relativo a 10 Hz**, a curva de 10 Hz — a única na fila — **não
muda**. Ela não podia fechar por esta correção, **por construção**. O G4 era
inalcançável no passo 1.

## ⚠️ ERRATA (mesma sessão) — a seção seguinte estava ERRADA

**O que eu afirmei abaixo — "embedding carrega ~76 %, logo a dependência de
frequência é impossível por atribuição" — está ERRADO.** Foi publicado no commit
`2956abf` e é corrigido aqui, com a medição que o desmente.

O erro: comparei a decomposição **cumulativa desde N=0** contra a métrica, que é
**normalizada na janela** (`align`). Três tentativas de conserto falharam por
motivos diferentes (unidade, `argmin` colando no índice 0 de uma grade de
espaçamento 501, e um fator 2,03 sistemático) até eu medir a primitiva.

**O fato que resolve:** `N_emb = 50`, logo `1 − e^(−200/50) = 0,982` ⇒ **o
embedding está 98,2 % completo ANTES de a janela começar.** O modelo perde
**37 % da pré-carga nos primeiros 200 ciclos** (`align = 0,6324`) e a métrica
normaliza isso fora. A grade de exibição (400 pts, espaçamento 501) é grossa
demais para mostrar o transiente — foi ela que me deu "0,8487 em N=200".

### As fatias CORRETAS, dentro da janela da métrica

Perda crua na janela = `align − ratio_cru(fim)`:

| curva | perda crua | embedding | creep | **flanco** | **fr. flanco** |
|---|---:|---:|---:|---:|---:|
| axialmin_10Hz | 0,0973 | 0,0065 | 0,0356 | 0,0553 | **56,8 %** |
| axialmin_15Hz | 0,0977 | 0,0065 | 0,0356 | 0,0556 | **56,9 %** |
| axialmin_20Hz | 0,0978 | 0,0065 | 0,0356 | 0,0558 | **57,0 %** |
| axial_10Hz_full | 0,1324 | 0,0065 | 0,0199 | 0,1061 | **80,1 %** |

**O embedding contribui 6,7 %, não 76 %.** O flanco carrega **57 %** (e 80 % na
curva longa).

### E a álgebra corrigida CONFIRMA a correção de input

| x (fatia do flanco) | razão prevista `(1−x)+x·0,478` |
|---|---|
| **0,568 (medido)** | **0,703** |
| 1,000 | 0,478 |

**Medido com o input corrigido: 0,710.** Contra 0,703 previsto pela fatia real
do flanco — **acerto quase exato**. Ou seja: a correção de input da Fig. 8(b)
age **exatamente** como a fatia do canal prevê, e o G1 reprovou não por o input
estar errado, mas porque eu pedi na banda o que só um flanco de 100 % daria.

### O candidato correto é `creep`→fretting, não `embedding`→fretting

Para ir de 0,710 a 0,498 o flanco precisa ir de **57 % a ~100 %**, e o que
ocupa os outros 36,5 % é o **creep** — não o embedding, que já saiu da janela.

E isso alinha **melhor** com o precedente citado: a adoção do LIU_2016
(2026-07-30) foi literalmente *"re-atribuição da cauda **creep**→fretting L1
pelo mecanismo dos autores"*. É o mesmo movimento, na mesma direção, na mesma
classe de ensaio.

### Lição de método

Três erros seguidos na mesma medição. O que os produziu: **inferir a
composição a partir de arrays de exibição em vez de medir a primitiva**
(`align`, `ratio` cru). A regra: quando a decomposição não fecha com a perda,
o suspeito é a **janela**, não a unidade — e o teste é somar os mecanismos
contra `align − ratio_cru(fim)`, que fecha em 1,000.

## (INCORRETO — mantido como registro) A causa real, provada por ÁLGEBRA

Decomposição medida (perda final por mecanismo):

| curva | embedding | creep | flanco | **fração do flanco** |
|---|---:|---:|---:|---:|
| axialmin_10Hz | **0,3526** | 0,0570 | 0,0553 | **11,9 %** |
| axialmin_15Hz | **0,3526** | 0,0541 | 0,0556 | 12,0 % |
| axialmin_20Hz | **0,3526** | 0,0521 | 0,0558 | 12,1 % |
| axial_10Hz_full | **0,3526** | 0,0601 | 0,1061 | 20,4 % |

**O modelo põe ~76 % da perda em EMBEDDING**, com valor **idêntico (0,3526) nas
quatro** — cego à frequência **e** à janela. O flanco, único canal sensível à
frequência, carrega **12 %**.

A álgebra fecha o caso. Se o flanco escala como `r^1,5` e carrega fração `x`:

```
razão_total = (1 − x) + x·r^1,5
x = 0,121  →  0,937        ← teto com a atribuição atual
x = 1,000  →  0,478        ← o que o dado pede
```

⇒ **Nenhum input e nenhum expoente reproduzem a dependência de frequência
enquanto o embedding domina.** É impossível por **atribuição**, não por
parametrização. (E os 0,710 medidos ficam *abaixo* dos 0,937 do teto porque a
correção de input também mexe no creep e no slip — ou seja, mesmo o teto que
eu calculei é otimista.)

## E a atribuição contradiz o mecanismo MEDIDO pelos autores

A **Fig. 9** do paper é *"SEM photo of bolt thread surface topography at
N = 2×10⁵"* — três micrografias da **superfície da rosca**. O texto atribui a
perda ao *"fretting wear at the contact interface and increased damage to the
**thread surface**"*.

**O paper mede fretting de rosca; o modelo diz assentamento.**

## O candidato que isto nomeia — com precedente exato

**Re-atribuição de canal pelo mecanismo dos AUTORES.** Precedente na própria
campanha: a adoção do **LIU_2016** em 2026-07-30 fez exatamente isso —
*"re-atribuição da cauda creep→fretting L1 pelo mecanismo dos autores"*,
`flank_wear_on=1`, `flank_amp_exp=1,5` KB, `k_wear_flank` lido do resíduo — e
levou a fonte de parcial a **14/14**.

Aqui a re-atribuição é **embedding→fretting**, e ela resolveria as três coisas
de uma vez: (a) libera a dependência de frequência (o canal sensível passa a
dominar), (b) dá saturação tardia se combinada com o estado
`delta_thread_fret` — que **já é acumulado e nunca é lido de volta** (o
`EmbeddingLoss` foi convertido para state-based em 2026-07-02 com exatamente
essa estrutura), e (c) alinha a atribuição do modelo com a evidência de
micrografia do paper.

**Não pré-registro aqui**: é hipótese nova, de escopo maior que este prereg, e
merece o seu próprio — com a correção de input da Fig. 8(b) embutida, porque
ela é procedência de figura e vale independentemente.

## Gates, um a um

| gate | resultado |
|---|---|
| **G0** (10 Hz bit-idêntico) | ✅ mae/σ inalterados |
| **G1** (vão em 0,478 ± 0,08) | ❌ **0,710** — o vão apareceu (57 % da lacuna) mas fora da banda |
| G2 (ordenação estrita) | ✅ 0,1539 > 0,1280 > 0,1093 |
| G3 (isolamento das 4 fontes) | n/a — sem adoção |
| **G4** (10 Hz entra no tripé) | ❌ **inalcançável por construção** (é a referência da escala) |
| G5 (nenhum pior) | ⚠️ 15 Hz piora +0,0069 (sob a tolerância); 20 Hz **melhora forte** (mae 0,0201→**0,0097**, σ 0,0248→**0,0110**) |

**Ramo aplicado: NÃO ADOTA.** Registro do que a medição entrega de graça: o
**20 Hz melhora quase 2×** só com a correção de input, o que é evidência
independente de que a Fig. 8(b) é o input certo — e que o problema restante
está na **atribuição**, não na amplitude.
