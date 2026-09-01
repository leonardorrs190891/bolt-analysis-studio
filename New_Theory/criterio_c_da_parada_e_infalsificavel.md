# O critério **(c)** da regra de parada é satisfeito com **mais** facilidade quanto **piores** os instrumentos

**2026-08-16 (22:0x)** · só-leitura · **nada executado** · store `7a60cacb72de`, censo
**144/205** · **observação independente sobre a F4 da sessão paralela** (`4f74790`).

---

## 1. Contexto — e o que NÃO estou contestando

A **F4** mediu os 3 critérios da regra de parada e concluiu que ela **dispara** na fila
julgável de 6. O trabalho é cuidadoso: o critério (b) vem com **ressalva de escopo escrita
por eles** (*"estender de 'uma classe' para 'a campanha' é DECISÃO, não medição"*), e o
contra-argumento está na mesa (2 curvas a 7,3 % e 7,9 % da barra, com σ a 2,6× e 1,8× o
ruído do próprio dado).

**Não contesto (a), (b), nem o veredito.** O que segue é sobre a **estrutura do (c)**.

## 2. O critério (c), como escrito

> **(c) O retorno marginal é medido e nulo:** após os **3** candidatos mais recentes,
> (i) **zero** curvas saíram da fila por mérito **e** (ii) a **mediana da distância ao
> limite** da fila caiu **menos de 3 % relativos**.

E o argumento da F4 para satisfazê-lo:

> *"Os 4 candidatos recentes foram TODOS falsificados por gate próprio; **nenhum foi
> adotado, logo nenhuma métrica mudou por causa deles**: mediana caiu 0 % < 3 %."*

## 3. ⛔ O defeito: o (c) é satisfeito por NÃO MEDIR NADA

Se **nenhum** candidato é adotado, a mediana **não pode** se mover — por construção
aritmética, não por evidência. ⇒ o (c) fica satisfeito por **qualquer** sequência de
candidatos reprovados, **incluindo os que reprovaram porque o TESTE era inválido**.

**A forma afiada:** quanto **piores** os instrumentos, **mais fácil** satisfazer o (c). Uma
campanha com instrumento quebrado produz candidatos que todos falham, nada se move, e o (c)
declara *"retorno marginal nulo"* — quando a verdade é *"não conseguimos medir"*.

Isso inverte o sentido do critério: ele foi escrito para detectar **retorno decrescente de
mudanças adotadas**, e lê como satisfeito na **ausência de qualquer medição válida**.

## 4. A própria regra já tem o antídoto — mas só para o (b)

O documento da proposta **já** separa as duas coisas. Na tabela dos candidatos:

| candidato | veredito registrado |
|---|---|
| Cattaneo-Mindlin (D2′) | **INCONCLUSIVO** (*"ganho ≡ 0, mérito era artefato de teto; **não conta para (b)**"*) |

⇒ o vocabulário existe, a distinção está feita, e a proteção está **explicitamente
anexada ao (b)**. O **(c) não a tem** — e é justamente o critério onde a ausência de
movimento é o *sinal*, o que o torna cego a por que nada se moveu.

⚠️ É a mesma lição que a campanha já pagou uma vez, num nível abaixo: *"a lista de ramos de
um prereg TEM de incluir `INCONCLUSIVO` ('o teste não testou'). Sem esse ramo o script é
forçado a escolher entre PASSA e FALSIFICADO e escreve veredicto sobre teste vazio"*
(2026-07-30, ocorreu 2×). O (c) tem o defeito **no nível da campanha**.

## 5. E a lista de 4 da F4 já contém um caso do tipo

| candidato citado | como terminou | espécie |
|---|---|---|
| `emb_pressure_exp` | G1 reprovou (melhor MAE 0,1599 = **3,2×**) | ✅ **FALSIFICADO** — mérito |
| **piso do `YANG_2023`** | **prereg MORTO: premissa falsa** | ⛔ **INCONCLUSIVO** |
| **`loose_arrest_residual`** | ⛔ ~~nunca reprovou~~ **RETRATADO §5a: prereg `lei-de-taxa-rotacional` reprovou nos gates** | ✅ **FALSIFICADO** — mérito |
| `k_ratchet` (ROUSSEAU) | 10 células falsificadas como constante compartilhada | ✅ **FALSIFICADO** — mérito |

> ✅ **Lacuna FECHADA em 2026-08-16 23:5x** (as duas linhas diziam *"não re-verificado
> aqui"*). Fechá-la **fortaleceu** o argumento, e com uma espécie que eu não previa.
>
> **`k_ratchet` (ROUSSEAU) — falsificação legítima, e boa.** 10 células varridas (com e sem
> expoente de amplitude), todas falsificadas **como constante compartilhada**, e o
> discriminante é medido: a rotação-por-slip exigida varia **10× dentro do mesmo rig**
> (`rousseau_ratchet_transferencia_resultado.md`). Teste válido, refutação real. ⇒ conta.
>
> ⛔ **`loose_arrest_residual` NÃO É CANDIDATO — é uma TERCEIRA espécie.** Ele é **campo do
> engine com default `0.0`**, **não citado em nenhuma config adotada**, construído com 5
> testes e **G0 |Δ| = 0,000e+00**. O `lu2024_embedding_pressao_resultado.md` o cita como
> **precedente** de *"mecanismo validado, adoção não gateada"* — ou seja, como **modelo do
> padrão** de capacidade default-inerte, **não** como candidato reprovado. **Não existe
> prereg que o falsifique.**
>
> ⇒ contá-lo no (c) é contar como *"tentamos e não deu"* algo que **nunca foi tentado**.
>
> ⛔ ~~**Placar real dos 4: apenas 2~~ **CORRIGIDO na §5b: são 3 são falsificação por mérito** (`emb_pressure_exp`,
> `k_ratchet`); 1 é teste inválido e 1 nem candidato é.

### 5a. ⛔ RETRATADO — a "terceira espécie" NÃO TEM MEMBRO, e o erro foi meu

> **2026-08-17 (22:5x).** Eu afirmei aqui que `loose_arrest_residual` *"nunca reprovou —
> nunca foi proposto"* e que *"não existe prereg que o falsifique"*, e construí sobre isso
> uma **terceira espécie** de candidato. **As duas afirmações são falsas.**
>
> O prereg existe: **`docs/superpowers/specs/2026-08-15-lei-de-taxa-rotacional-prereg.md`**,
> com **7 gates (G0–G6)** desenhados especificamente para adotá-lo. E o §RESULTADO dele diz,
> textualmente: *"forma CONSTRUÍDA, mecanismo VALIDADO, adoção **FALSIFICADA** pelos
> próprios gates"* · *"**NÃO ADOTADO** — trocar 2 curvas que passam por 3 que fecham"*.
>
> ⚠️ **Como errei:** procurei preregs por **nome de arquivo** (`residual|arrest`) e não achei
> — porque o prereg leva o nome da **lei** (`lei-de-taxa-rotacional`), não do **campo**.
> Busquei pelo nome que eu esperava em vez de pelo conteúdo. É a mesma falha que já me
> custou várias contagens nestes dois dias.
>
> **Quem me corrigiu foi a sessão paralela**, no prompt anti-redescoberta (`eedc424`), que
> diz certo: *"a capacidade `loose_arrest_residual` foi construída default-inerte e a
> ADOÇÃO reprovou nos gates"*. Eu li isso, achei que contradizia o meu, e fui medir — e o
> errado era o meu.

### 5b. Placar CORRIGIDO dos 4 — e o item U enfraquece, mas sobrevive

| candidato | espécie |
|---|---|
| `emb_pressure_exp` | ✅ FALSIFICADO por mérito |
| **`loose_arrest_residual`** | ✅ **FALSIFICADO por mérito** (era: "não é candidato") |
| `k_ratchet` (ROUSSEAU) | ✅ FALSIFICADO por mérito |
| piso do `YANG_2023` | ⛔ INCONCLUSIVO |

⇒ **3 de 4 são falsificação por mérito**, não 2.

**O argumento central do item U SOBREVIVE:** o critério (c) segue sem distinguir
`INCONCLUSIVO` de `FALSIFICADO`, e o caso do `YANG_2023` segue sendo um teste que nunca
rodou contado a favor de parar. **Mas enfraquece em magnitude:** é **1 de 4**, não 2, e o
**U2 fica folgadíssimo** (3 falsificações por mérito quando ele pede ≥1).

⛔ **A rota U1′ está RETIRADA.** Ela excluía do (c) *"capacidade construída cuja adoção
nunca foi proposta"* — categoria que **não tem nenhum membro** e que eu inventei a partir
de uma busca malfeita. Propor guarda para classe vazia é ruído, e a campanha já perdeu
instrumentos assim.

### 5c. (registro do que eu havia escrito, para não se perder o raciocínio)

O (c) precisa distinguir **três** coisas, não duas:

| espécie | conta para (c)? | por quê |
|---|:--:|---|
| **FALSIFICADO por mérito** | ✅ | tentamos, gate próprio reprovou, o modelo não respondeu |
| **INCONCLUSIVO** | ❌ | o teste não testou (premissa falsa, instrumento errado, teto desigual) |
| **capacidade construída, adoção nunca proposta** | ❌ | não houve tentativa de adoção; nada foi perguntado ao dado |

⚠️ A terceira é a mais traiçoeira porque **parece** produtividade: há código novo, testes
novos, G0 bit-a-bit. Só não há **pergunta feita ao dado**. Uma campanha pode acumular
capacidades default-inertes indefinidamente e o (c) leria isso como *"retorno marginal
nulo"*.

O caso do `YANG_2023` é **meu, de hoje**, e não é ambíguo: o prereg (`093050e`) congelou
gates sobre a premissa *"o dado arresta em 0,165"*, e essa premissa **é falsa** — eu havia
lido `metric_data`, o dado **depois** do `FLOOR_TRIM = 0,10`. O dado cru colapsa a
0,02–0,06. Retratado em `13ed862` / `0822572`, com o próprio leitor canônico devolvendo
`plateau=False` nas 7 curvas que afrouxam.

⇒ **aquele candidato nunca foi testado.** Contá-lo como evidência de retorno decrescente é
contar um teste vazio a favor de parar. ⚠️ **Não sei** classificar os outros dois sem
re-lê-los; a espécie do 2º já basta para o argumento estrutural.

## 6. O que isto muda — e o que NÃO muda

**Não muda o veredito.** O (a) está satisfeito, o (b) está satisfeito **na fila presente**
com ressalva declarada, e o (c) — mesmo descontando o candidato inválido — provavelmente
segue satisfeito, porque `emb_pressure_exp` **foi** falsificado por mérito e nada saiu por
mérito. A parada segue defensável, e é provisória com reabertura automática já escrita.

**Muda o que o (c) VALE como argumento.** Hoje ele não distingue *"tentamos e o modelo não
responde"* de *"tentamos errado"*. Numa parada de campanha, essa é a diferença entre um
limite do modelo e um limite nosso.

## 7. Proposta — **aguarda assinatura** (mexe na regra de parada)

| # | ação |
|---|---|
| **U1** (recomendada) | anexar ao (c) a **mesma** cláusula que o (b) já tem: *candidato com ramo `INCONCLUSIVO` **não conta** para os 3*. Um teste que não testou não é evidência de retorno nulo. Custo: uma frase. |
| **U1′** (acrescentada 23:5x) | **e capacidade construída cuja adoção nunca foi proposta também não conta** — a 3ª espécie, descoberta ao fechar a lacuna. Sem isto o (c) aceita como evidência algo que nunca perguntou nada ao dado |
| **U2** | exigir que ao menos **1 dos 3** tenha sido `FALSIFICADO` **por mérito**, com predição pré-registrada cumprida — mais forte, e hoje **satisfeito** (`emb_pressure_exp` e `k_ratchet`, **2 de 4**) |
| **U3** | não mexer |

**Recomendo U1 + U2 juntos.** O U1 fecha o buraco; o U2 impede que o (c) seja satisfeito por
uma sequência inteira de testes vazios, que é o caso patológico. Ambos são **satisfeitos
pelo estado de hoje** ⇒ adotá-los **não** reabre a parada; só torna a parada defensável pela
razão certa.

⛔ **Não executo** — mexer na regra de parada exige assinatura, e a regra em si já aguarda a
dele desde 2026-07-30.

## Reprodutibilidade

Leitura de `New_Theory/regra_de_parada_proposta.md` (§(c) e a tabela de candidatos),
`git log -1 4f74790`, e os commits `093050e` (prereg), `13ed862` (retratação) e `0822572`
(prereg marcado morto). Nenhuma medição nova de curva — o argumento é estrutural.
