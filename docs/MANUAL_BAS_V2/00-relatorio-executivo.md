# Relatório executivo — execução mestre até a F6

> Para o Prof. Leonardo. Fecha o §6.4 do
> [prompt-mestre](../superpowers/plans/2026-07-17-PROMPT-MESTRE-execucao-unica.md).
> Fonte de cada linha: o ledger `.superpowers/master-0p1-progress.md` e o store
> canônico `validation_store.json` (fingerprint **`4f5bedfbace4`**). Nada aqui é
> estimado.
>
> **Uma coisa continua esperando você, e eu não a assinei:** a lista de exceções
> da F5 (S4). Ver §4.

---

## 1. Onde o modelo está

| | valor | fonte |
|---|---:|---|
| curvas de artigo comparáveis | **202** (28 fontes) | store |
| **no tripé** (`MAE<0,10` **E** `res.máx<0,10`) | **140 — 68 %** | store |
| fora do tripé | **55** | store |
| — só pelo resíduo máximo | **34** | store |
| — só pelo MAE | **0** | store |
| — pelos dois | 21 | store |
| mediana MAE / média | **0,0315** / 0,0445 | store |
| mediana do resíduo máximo | 0,0623 | store |
| erros de simulação | **0** | store |
| fingerprints distintos no store | **1** | store |
| fontes fechando 100 % | **13** de 28 | store |
| constantes fitadas no dataset inteiro | **3** | `shared.free_constants` + `F0_test` |

> ### ⚠️ A tabela acima e o parágrafo abaixo estão na régua de DUAS pernas
>
> Os números desta seção foram certificados em 2026-07-27 contra
> `MAE ≤ 0,10 E res.máx ≤ 0,10` (fingerprint `4f5bedfbace4`). Em **2026-07-29** a
> meta passou a ter **três pernas** — `res.máx ≤ 0,10` **E** `MAE ≤ 0,05` **E**
> `σ_res ≤ 0,025` — e a leitura estratégica **inverteu**. O registro certificado
> fica como está; a leitura vigente é a do quadro seguinte.

**A leitura estratégica de 2026-07-27, hoje VENCIDA:** *"`MAE ⊆ maxerr`. Nenhuma
curva viola só o MAE. Portanto esforço medido em MAE médio não move a meta — só
encurtar o pior ponto de cada curva move. 44 % do que falta está em três fontes
(LU_2024 10/10 fora, BAUER_2024 7/9, CHU_2026 7/9)."*

**Por que ela caiu — é aritmética, não regressão do modelo:** a inclusão
`MAE ⊆ maxerr` só valia porque os dois limites eram **iguais**. Como
`MAE ≤ res.máx` para qualquer curva, com ambos em 0,10 violar o MAE obrigava a
violar o pico, logo ninguém caía só pelo MAE. Com `MAE ≤ 0,05` **contra**
`res.máx ≤ 0,10` a inclusão deixa de valer — e o corolário de método morre com
ela.

**A leitura estratégica VIGENTE (re-medida em 2026-08-01, fingerprint
`63722b266dc0`, 205 curvas comparáveis — ANCORA_INTERNA **fora do projeto** (professor,
2026-08-01; dados preservados, sem rodada pendente);
+2 réplicas YANG_2021 no tripé por mérito; **regra n<6 assinada em
2026-08-01**: σ_res com menos de 6 pontos é não-julgável ⇒ 3 curvas saíram do
tripé para declaradas — com **D1 adotado**: o limite da 3ª perna é POR FONTE,
`max(0,025; piso medido)` — abaixo do piso da própria fonte, "reprovado" mediria
o dado, não o modelo. A conta está publicada no painel "Qual perna é o gargalo"
do report mestre):**

| leitura | hoje (censo 205, 01/08 pós-recuperação ROUSSEAU) | 29/07 (global) | era (2 pernas) |
|---|---|---|---|
| curvas no tripé | **171** de 205 (83 %) | 104 | 147 de 202 (73 %) |
| **resolvidos** (tripé + exceções necessárias) | **190** de 205 | 148 | 164 |
| violam **só** o MAE | **0** | 5 | 0 |
| violam **só** o resíduo máximo | **3** | 0 | 34 |
| violam **só** o σ_res | **9** | 30 | — |
| violam mais de uma perna | **22** | 63 | 21 |
| σ_res **não-julgável** (n<6, regra 2026-08-01) | **6** | — | — |
| **perna que MANDA** (maior múltiplo do limite) | **σ_res 23 · MAE 5 · res.máx 6** | 87 · 9 · 2 | — |
| fontes fechando 100 % | **17** de 27 | 6 | 13 de 28 † |
| 3 maiores fontes, share do que falta | **50 %** (18 de 36) | 28 % | 44 % |

⚠️ **Cinco células desta tabela estavam VENCIDAS e não eram vigiadas** (medido
2026-08-16, ao sincronizar o censo 143→144): *resolvidos* dizia **155** contra
**167** medidos — uma defasagem de 12 —, e *só res.máx* / *só σ_res* / *mais de
uma* / *3 maiores fontes* também tinham deslizado. As que a guarda de
envelhecimento ancora (tripé, só-o-MAE, perna que manda, fontes 100 %) estavam
certas ou falharam alto no mesmo dia. É a lição do §4.43 medida **dentro da
própria tabela que a publica**: número sem âncora não fica velho devagar — ele
fica velho *em silêncio*, ao lado de vizinhos vigiados que parecem avalizá-lo.
Todas as células passaram a ter âncora em `_VIVAS`.

⚠️ **Re-medidos em 2026-08-15 contra o store `85e8104420b0`** (adoção do canal de
flanco no `LIU_2020_WEAR`, item M). A adoção explica **+1 em "só o MAE"** e
**−1 em "mais de uma"** — a `liu2020_fig9_zinc_AF0.4mm` passou a reprovar
**apenas** o MAE (res.máx 0,1339→0,0766 e σ 0,0345→0,0227 entraram). **As outras
três células já estavam vencidas antes**, e o motivo é estrutural: a lista
`_VIVAS` de `test_meta_numeros_nao_envelhecem` ancora **uma** célula desta tabela
de oito linhas, então só ela era verificada — as demais derivaram em silêncio
por várias adoções. Ancorar a linha inteira é candidato de guarda.

⚠️ **E a "perna que MANDA" eu quebrei e desfiz:** troquei 47 por 41 recomputando
com implementação própria — o canônico `_censo()` diz **47** e o documento estava
**certo**. A diferença 47−41 é exatamente as **6** curvas `n<6` não-julgáveis,
que `_perna_manda` conta e a minha conta descartava. É a terceira vez na sessão
que reimplementar a regra em vez de chamar o helper produziu número plausível e
errado; aqui chegou a me fazer "corrigir" um número correto.

✅ **O que sustenta as quatro células restantes** (2 · 4 · 10 · 42) é um validador
grátis que a linha antiga **falhava**: elas têm de somar `fora`.
2+4+10+42+6 = **64** = fora. A linha anterior somava 1+8+7+46+6 = **68**.

† **Discrepância PRÉ-EXISTENTE, não introduzida aqui:** para a régua de duas
pernas este relatório registra **13** fontes fechando 100 %, enquanto
`MODEL_LEGITIMACY.md` §8 e o `CLAUDE.md` registram **12**. Não reconciliei — os
dois números vêm de gerações diferentes do store e nenhum dos dois é a leitura
vigente. O número de hoje (**6**) foi medido agora, no `3546e6745448`.

⇒ **o gargalo DEIXOU de ser majoritariamente σ_res (manda 37 % das 67: σ 25 · MAE 18 · mx 24)** —
o D1 mostrou que o "89 %" da régua global era em boa parte **régua**, não
modelo (cobrar 0,025 de fontes cujo piso medido é 2–9× isso media o
experimento). ⚠️ **Retratação de 31/07**: um "rebalanceamento do gargalo"
publicado de manhã (σ28·MAE16·mx26) era artefato de um piso INVÁLIDO do
LU_2024 (par cruzado 0,5×1,0 mm — a fig20 roda a 1,0 mm; erro de input do
registry corrigido, exceção T22 retratada; o par verdadeiro amp1p0↔T22 é o
MESMO teste em 2 figuras e mede só digitalização, σ 0,0192). As fig20
re-simuladas com o drive real pioram — plano de recuperação com as âncoras
novas do paper em `lu2024_plano_melhoria.md`. (As duas
adoções de 30/07 — ZHANG_2018 creep-com-onset e LIU_2016 fretting L1,
`zhang18_creep_onset_resultado.md` / `liu2016_fretting_resultado.md` —
tiraram as duas fontes inteiras da conta: 9/9 e 14/14 no tripé.) Piores fontes
pós-D1: LU_2024 **10/10** fora, BAUER_2024 **7/9**, YANG_2023_IJPEM **7/9**,
CHU_2026 **6/9**, ECCLES_2010 **6/10**.

⚠️ **Ressalva que o leitor precisa ter junto:** o limite do σ_res é **ambição
declarada**, não folga — 0,025 contra o **piso de repetibilidade medido de
0,0283** (≈12 % abaixo dele, 30 famílias de réplica). E uma varredura de
sensibilidade das 18 alavancas do modelo **não fechou essa perna em nenhuma**.
Portanto a queda de 147→104 **não mede piora do modelo**: mede a entrada de uma
régua mais exigente que a dispersão do próprio experimento — e foi exatamente por
isso que o **D1** (piso por fonte) foi adotado em 2026-07-30, devolvendo 20
curvas cuja reprovação media o dado: 104→124. O global 0,025 permanece para toda
fonte com piso abaixo dele; ver a caixa da régua no topo do `CLAUDE.md`.

---

## 2. Painel por fase

| fase | estado | o que entregou |
|---|---|---|
| **F0** — integração L1–L7 | **concluída** | merge `166a761` (--no-ff, zero conflitos); suíte no main **695 passed / 1 skipped**; store re-carimbado (`ae2d7e0`); 58 cópias de leitura adotadas sem descarte (MD5 arquivo-a-arquivo) |
| **F0.5** | **pendência manual** | registrada no ledger |
| **F1** — gates de leitura | **concluída** | 3 itens adotados (`0ea29af` código + `e519c25` adoção/store); check L7 gravado nos 203 registros; 1ª rodada do gate teve bug **no checador**, corrigido e registrado |
| **F2** — canal de flanco per-rig | **concluída** | P2.1 **adotado** (`d745998`, LI_2022_TRIBOINT); P2.2 **FAIL documentado**; P2.3 N/A |
| **F3** — polimento por fonte | **concluída** | JCSR (`611959a`), LIU_2025 (`3bf5774`), YANG_2021 (`a2fd9af`), ICMEZ (`93fc5fc`); mecanismo de trim + convenção "cauda de fratura → trim registrado" |
| **F4** — formas candidatas | **PARE → Opção A** | `flank_s_crit` **NÃO-DEMONSTRADO**; Opção A adotada por sua ordem "continue" (`6960a26`): só leituras promovidas, **nenhuma forma nova adotada** |
| **F5** — certificação | **números certificados; encerramento aguarda S4** | S1 · S2 · S3 · S5 concluídas; **S4 preparado, não assinado** |
| **F6** — o Manual | **entregue nesta rodada** | 3 volumes + hub no explorador + 5 figuras com gate de byte-identidade |

### Retomada de 2026-07-28 (esta rodada)

| # | o que | commit |
|---|---|---|
| 1 | **P0: a GUI inteira estava morta** — `__new__` de singleton em subclasse de `QObject` (PyQt6 6.11.0) matava o processo; `run_app.py` e `--v2` não abriam, 4 arquivos de teste morriam. O registro anterior dizia "1 teste isolado" | `651f64f` |
| 2 | **higiene do store** — a suíte gravava `ensaio_teste_m12` no arquivo versionado (204→203) | `dd23a5e` |
| 3 | **as 5 figuras do Manual** + gate (C) de byte-identidade | `549ed0f` |
| 4 | **o gate quase nasceu quebrado** — matplotlib gravava CRLF onde o `.gitattributes` guarda LF; falharia em todo clone novo | `05e62a5` |
| 5 | ledger da janela do crash das 08:05 | `5309709` |

---

## 3. Adoções realizadas — cada uma com seu gate

| adoção | gate que a autorizou | onde vive |
|---|---|---|
| **conformação dependente de pressão** (driver `effective`) | resolve a falsificação do sobretorque: MAE 0,138 → **0,030**; 3 fortalecimentos (robustez fit-n, driver de equilíbrio, procedência) | `shared` (hash `21ed6a7`→`13b26d2`) |
| **ρ-unificação** (`emb_amp_exp=2,375`) | §4.18 — embedding passa a depender da amplitude | `shared` |
| **receita LIU_2022_RETIGHT** (reaperto) | fonte 0,2492 → ~0,016 em 21/21 curvas, **zero fit novo** | `adopted_configs` + cadeia `retight` no runner |
| **canal de flanco per-rig** (LI_2022_TRIBOINT) | F2 P2.1 | `adopted_configs` |
| **saturante per-condição** (JCSR) | F3.1, 4 grupos novos | `adopted_configs` |
| **`C_creep` per-par** (LIU_2025 1,3e-11) | PASS 7/7 pós-trim | `adopted_configs` |
| **emb como leitura de paper** (YANG_2021 3,85 µm) | PASS t1, leitura pura | `adopted_configs` |
| **re-grid min-max** (ICMEZ) | 8/8; alvos 0,101→0,086 e 0,118→0,099 | `adopted_configs` |
| **check L7 informacional** | nunca bloqueia, nunca é fitável | engine, nos 203 registros |
| **`k_member_shear`** (PR-14) | forma viva; t14 em stick permanente explica o não-colapso | engine |

**Adoções vindas da branch L1–L7: zero.** Toda capacidade dela nasceu
default-inerte com bit-identidade testada.

---

## 4. ⛔ O que depende de você

### 4.1 A lista de exceções da F5 (S4) — **não assinei**

`New_Theory/f5_excecoes_propostas.md` está preparado. A F5 fecha como
*"100 % − exceções"* **apenas se** as exceções forem assinadas **e** o restante
for aceito como fila aberta.

> **RE-BASELINE (2026-07-28, mesmo dia): este parágrafo dizia "~10
> exceções-candidatas e ~45 form-limited", e o número está VENCIDO.** A varredura
> curva-a-curva ([`frontier_classes.md`](../../New_Theory/frontier_classes.md),
> só-leitura no store `4f5bedfbace4`) achou **quatro** classes, não uma:

| classe | n | o que fecha | custo |
|---|--:|---|---|
| **LEVEL-LIMITED** | **8** | ler o nível — **medido: fecha 1 das 6 sondadas** | leitura, mas o piso **não** é a alavanca |
| **METRIC-LIMITED** | **8** | decidir a convenção (isentar do `FLOOR_TRIM` / mudar o eixo) | decisão sua |
| **DATA-LIMITED** | **3** | nada no modelo — a meta está sob a reprodutibilidade do ensaio | dado novo ou exceção |
| **FORM-LIMITED** | **36** | construir mecanismo | prereg + gate, 1 por vez |

> **Estes números são a 3ª e última medição do dia, e as duas anteriores estão
> registradas como errata** em [`frontier_classes.md`](../../New_Theory/frontier_classes.md)
> §6 e §6b. A 2ª (que publicou 35/6/8/6 aqui) **super-atribuía DATA-LIMITED**:
> marcava todos os membros de um grupo de réplica com dispersão > 0,10, quando
> dispersão alta prova que **ao menos um** membro viola, não que todos violem.
> Corrigido por **teto de grupo** (busca exaustiva do maior subconjunto com
> dispersão ≤ 0,20): só entra quem não cabe em **nenhum** subconjunto máximo.
> A causa da 1ª tentativa desse cálculo ter contradito a varredura de réplica era
> a **grade de interpolação** — 40 pontos sub-resolvem a dispersão em ~1 %, o que
> bastava para virar um teste de limiar em 0,20 (medido: 0,19944 com n=40 contra
> 0,20134 convergido). Grade agora em 800 pontos.

> **A varredura de impossibilidade por réplica**
> ([`replicate_impossibility_sweep_2026-07-28.md`](../../New_Theory/replicate_impossibility_sweep_2026-07-28.md)):
> as **3 réplicas do Bauer M12 fig8** (mesma condição — 50 kN, espectro 80/150 µm;
> a nota de aparato diz *"knee position varies per test"*) têm **teto 2 de 3**
> (corrigido de "0 de 3" — ver §4.1) ⇒ **1 exceção provada**, não 3. Elas estavam
> classificadas em **três classes diferentes**
> (FORM · METRIC · LEVEL), o que expõe um defeito de método: *um classificador
> por-curva é cego para limite por-família.* Controle negativo no mesmo teste: as 2
> curvas do **Yang 2021 são alcançáveis** (teto 2 de 2) ⇒ a classe FORM delas está
> **confirmada** por teste independente.

**19 das 55 não pedem física nova.** As **3** DATA são as exceções necessárias
**por nome** (`bauer fig6_rep1`, `bauer fig8_test1`, e 1 curva de resolução
grossa do Yang 2023). **Por contagem**, somando os tetos de grupo, as exceções
necessárias são **6** — o mesmo total da varredura de réplica; a diferença é que
teto 3 de 6 diz *"3 curvas do fig6 têm de falhar"* sem dizer **quais**, porque
existem 3 subconjuntos viáveis de tamanho 3 e `rep5`/`rep6` aparecem em algum
deles. Só `rep1` está em nenhum.

**Duas ressalvas que vêm com o número, e são do próprio documento-fonte:**
1. ~~**LEVEL-LIMITED é condição necessária, não prova.**~~ **A ressalva foi
   MEDIDA no mesmo dia, e o resultado é negativo**
   ([`level_seven_probe.md`](../../New_Theory/level_seven_probe.md) +
   [`level_limited_floor_read_2026-07-28.md`](../../New_Theory/level_limited_floor_read_2026-07-28.md),
   reconciliadas em
   [`level_seven_reconciliacao.md`](../../New_Theory/level_seven_reconciliacao.md)).
   `sobra < 0,10` diz que o erro *é* de nível — mas as **duas** alavancas de nível
   que a campanha sabe **ler** do dado (`loose_arrest_floor` do platô,
   `emb_depth` da queda-inicial) foram sondadas nas 7 então classificadas, com
   controle negativo bit-a-bit e sem escrever no store:

   | desfecho | n | |
   |---|--:|---|
   | **FECHA** | 1 | `chu…D0p3mm…test1`: maxerr 0,1147 → **0,0082** |
   | MELHORA, não fecha | 1 | `lu2024_T22Nm`: 0,1248 → 0,1166 |
   | **INERTE** (Δ = 0 exato) | 2 | `liu2016`, `liu2020` — **sem pack no cfg** |
   | **PIORA** | 3 | `eccles fig8a`, `rousseau hdpe_t12`, `bauer test3`¹ |

   ¹ o `bauer test3` foi depois reclassificado para DATA-LIMITED (é réplica da
   fig8) ⇒ das **6** curvas de nível de fato, **1 fecha**.

   **Então a ação prescrita para esta classe está morta como estava escrita.** O
   diagnóstico continua válido (o erro *é* de nível); o que caiu foi a alavanca.
   A pergunta que sobra é precisa: *que constante governa o nível quando o piso de
   arresto não é a resposta?* — e os candidatos saem da doutrina "ler em vez de
   fitar" (`emb_depth` é **input** por junta; `tr_loose_gain` é forma
   compartilhada ⇒ mexer per-rig é **fit**, não leitura).

   Três achados do caminho, que valem além destas curvas:
   - **um pré-teste de direção prevê 7 dos 7 desfechos sem simular nada** — se o
     valor lido não move a retenção para o lado que o `res.médio` exige, a sonda
     piora. Com um passo anterior: **conferir se a alavanca está viva** no cfg
     daquele caso (senão atribui a "direção errada" o que é campo morto);
   - **`loose_arrest_floor` é INERTE sem pack na entry** — Δ = 0 **exato** nas 2
     curvas sem `loose_torsion_mode`, e nunca inerte nas 5 com pack (7/7). O
     gotcha do `CLAUDE.md` passa de advertência a fato medido;
   - **o leitor do piso e a métrica discordam sobre onde a curva acaba**:
     `arrest_floor_from_curve` faz a média dos últimos 5 % do ratio **cru**, e a
     métrica pontua só o trecho `≥ 0,10`. Mesma classe dos erros de instrumentação
     de 07-27.

   **E o preço cai no pior lugar:** o `liu2016wear_fig7_run2_5e6cyc` é a curva
   **mais perto de fechar entre as 55** — viola por **+0,0035** — e a alavanca
   mais barata é **inerte justamente nela**.
2. **METRIC-LIMITED é definida contra a convenção vigente** ⇒ pela regra §4.43, se
   a métrica canônica mudar, a classificação vira suspeita e tem de ser re-rodada.
   Há um prereg de métrica com gates congelados em outra sessão; estes números
   **não são evidência** para aqueles gates.

#### As **8** DATA-LIMITED estão **provadas** — e a lista perde uma curva

[`data_limited_proof_2026-07-28.md`](../../New_Theory/data_limited_proof_2026-07-28.md)
(só-leitura). A prova **não é sobre o nosso modelo**, é sobre **qualquer** modelo:
o Bauer publica **6 réplicas da mesma condição nominal**, e quando réplicas
discordam entre si, a curva que minimiza o pior erro é a *midrange* ponto-a-ponto
— cujo erro contra a réplica mais distante é **metade da dispersão**. Medido
dentro da janela pontuada por **todas** as 6 (`N` ∈ [0, 126]):

| | |
|---|--:|
| meia-dispersão máxima | **0,2294** (2,3× a meta) |
| ciclos com meia-dispersão > 0,10 | **94 / 200 (47 %)** |
| par mais distante | **0,5613** (rep1 vs rep6) |
| **teto da família** | **3 de 6** (midrange, mediana e "colar na melhor réplica" dão os três 3) |
| onde o modelo está hoje | **2 de 6** |

⇒ **pelo menos 3 das 6 têm de ser exceção por necessidade matemática**, e há
**exatamente 1 curva de folga** até o máximo teórico.

**Refinamento que muda a lista:** das 4 marcadas DATA-LIMITED, a **`rep4` é
recuperável em princípio** (0,0574 contra a midrange — passa). As provadamente
inalcançáveis são **`rep1`, `rep5`, `rep6`**. A 5ª curva
(`Yang 0,50 mm`) tem **6 pontos**, com saltos consecutivos do próprio dado de
**0,22 medianos / 0,25 máximos** — em **4 dos 5 intervalos** o passo do dado é
maior que a tolerância inteira da meta; ali o resíduo informa sobre o
espaçamento da amostragem, não sobre o modelo.

**Para assinar: 6 exceções com prova** — e este número foi **corrigido de 7 no
mesmo dia**, por erro meu de método (errata no topo do
[doc da varredura](../../New_Theory/replicate_impossibility_sweep_2026-07-28.md)):
eu usei *"quantas réplicas a midrange satisfaz"* como teto de passes, e a midrange
minimiza o erro **máximo**, não maximiza a **contagem**. O teto rigoroso é o maior
subconjunto com dispersão ≤ 0,20.

| grupo | teto rigoroso | hoje | **necessárias** | recuperáveis |
|---|--:|--:|---|---|
| BAUER fig6 (6 reps) | 3 de 6 | 2 | **rep1 · rep5 · rep6** | `rep4` |
| BAUER M12 fig8 (3) | **2 de 3** | 0 | **test1** | `test2` · `test3` |
| ECCLES no-axial (4) | 3 de 4 | 2 | **fig8a_baseline1** | `fig8c_baseline2` |
| Yang 2023 0,50 mm | — (resolução) | — | **a curva** | — |

**6 necessárias · 4 recuperáveis em princípio.** O que sobrevive intacto do
argumento é a parte rigorosa: *meia-dispersão > 0,10 ⇒ ao menos um membro do grupo
necessariamente viola* — e ela vale nos três grupos incompatíveis.

### 4.2 A fila de formas (as **36**, e o que cada forma fecharia)

> A tabela abaixo foi montada **antes** da classificação em 4 classes e conta os
> casos pela forma candidata, não pela classe. Onde ela soma mais que **36**, a
> diferença está nas curvas que a varredura reclassificou como LEVEL/METRIC/DATA
> — vale a classificação, que é a medida mais recente.

| forma na fila | fecharia |
|---|---|
| kernel desacelerante (run-in) | ~20 — LU_2024 10, CHU 6, SUN 1, KARLSEN 1, YANG_2019 3, ZHANG_2006 1 |
| bifurcação de limiar | 7 — YANG_2023_IJPEM (tri-falsificado) |
| decisão G2 (MAE-only) | ECCLES_2010 5 — receita pr31 pronta, aguarda decisão |
| canal estrutural ξ-dependente | 2 — YANG_2021 |
| cliff/rebound de corrosão | 2 — JCSR (o engine não recupera pré-carga) |
| incubação de assentamento | 2 — âncora interna |
| escala de rigidez com espessura | 3 — ROUSSEAU |
| tripla combinação | 1 — YANG_2023_AME |

Ligar qualquer uma exige prereg + gate + **sua palavra explícita**.

### 4.3 Decisões pontuais registradas e abertas

- **LU_2024 / `N_emb`** — o candidato acerta o alvo pré-declarado na mosca
  (fração no 2º ponto 47 % = valor do dado; MAE mediano −32 %, 7/10 melhoram,
  T16Nm **entra** no tripé) mas **falha o gate PR-37′ em duas cláusulas**
  (mediana −25 % onde se exige −30 %; **1 caso pior**, T4Nm +0,026). A regressão é
  coerente e pré-medida: o T4Nm é a única curva em que o modelo já perdia demais
  cedo. Saídas honestas: (a) `per_case` no T4Nm com justificativa pré-medida;
  (b) aceitar o gate como falho. **É sua decisão** — é ela que separa (a) de
  "abrir exceção para o caso inconveniente".
- **L3 (`F_amp ↔ δ_amp`)** — capacidade construída e **default-inerte**; falta
  calibração per-rig antes de qualquer adoção comportamental.
- **Prereg Rousseau** — dois problemas distintos, não um: `steel_t10` é arresto
  **terminal**; `hdpe_t10/t12` é **tempo de joelho** com amplitudes por espécime
  (0,5 / 0,49 / 0,38 mm), o que pode tornar a fonte irredutível a uma forma única.

---

## 5. Falsificações — o registro que dá crédito ao resto

| candidato | como morreu |
|---|---|
| canal de flanco ∝ A_F (L1) | Gate B1 **FAIL2** — slope ~8× raso demais |
| canal de rotação θ(N) | **equifinalidade** (§4.23) |
| nível de energia por ciclo | nível falsificado, **estrutura correta** (§4.25) |
| gatilho de criticalidade (Bauer fig8) | falsifica o crash gradual (§4.30) |
| 3 formas de erro de mid-curva | **todas** falsificadas; a fonte-líder estava no piso (§4.35) |
| espectro multi-amplitude | premissa falsificada — e a falsificação **nomeou a forma real** (§4.36) |
| `flank_s_crit` | **não-discriminância**: 30/30 células passavam, inclusive as 6 **sem** o candidato |
| `arrest_approach_exp` | G2 FAIL / G3 FAIL (prereg grupo A) |
| `W_conf_ref` ancorável na biblioteca | **null decisivo** (§4.9) |

**Uma falsificação venceu e ninguém notou por 24 dias.** O gate B1 falhou em
03/07; a ρ-unificação foi adotada em 08/07 e tornou o embedding dependente da
amplitude; o gate nunca foi re-medido. Re-medido em 27/07: o modelo entrega
**77,7 %** da sensibilidade `∂(fim)/∂A_F`, não 0 %. Foi partir desse texto vencido
que matou o `flank_s_crit`. Daí a regra §4.43 — *toda falsificação carrega o
fingerprint contra o qual foi medida e vira suspeita quando o fingerprint muda* —
que, aplicada aos 11 itens do roadmap, achou **sete** vencidos ou já feitos.

---

## 6. O que ficou aberto, nomeado

1. **Experimento-âncora de `W_conf_ref`** — a constante é fitada e **não tem
   âncora independente**; a Fase 3 tentou e deu null decisivo. Spec do
   experimento existe (fretting ~1,2 GPa, medindo `n`); **não executado**.
2. ~~**Energia de remoção fora da banda física**~~ — **DIAGNOSTICADO E
   REENQUADRADO em 2026-07-28**: [`l7_removal_energy_diagnostic_2026-07-28.md`](../../New_Theory/l7_removal_energy_diagnostic_2026-07-28.md).
   Dos 110 casos com valor, **60 acima** do teto (mediana 6× o teto) e **4
   abaixo** — os 4 são **todos Karlsen** (M30/M42). A medição que muda o tamanho
   do problema: **η² da FONTE sobre `log10(implied)` = 0,910** com dispersão
   interna mediana de **0,08 década** ⇒ é praticamente **um número por bancada**,
   então "64 curvas" são **~9 configurações de rig**. E o conserto barato está
   **refutado**: subir `k_wear_spec` globalmente não resolve (Spearman **−0,089**
   contra −1 previsto pela física, inclinação log-log −0,54) e **afundaria** os 4
   casos de Karlsen, que já estão abaixo do piso. Violação em **dois sentidos** =
   assinatura da **L6** (constante por par), com número. Segue aberto o passo
   que testaria de fato (prereg proposto no §5 do diagnóstico, não executado).
3. **Orçamento de energia axial** — termo viscoso de Rayleigh sem contraparte em
   `W_ext` (residual −242,8 a −11,7 J). Não afeta MAE nem `F_0`; o balanço não fecha.
4. **`N_emb`: 50 no canônico vs banda medida 3–15 per-rig** — a divergência está
   registrada e **não reconciliada**.
5. **`k_wear_spec` canônico (5e-14) fora de todas as bandas medidas R5** — a
   limitação **L6** em forma concreta: o KB documenta a não-universalidade de
   K/H por par, não a resolve. **Achado desta rodada**, ao verificar o
   `check_input` para o Volume 3. **[PRECISADO em 2026-07-28 pela matriz de
   procedência](../../New_Theory/provenance_matrix.md): não é "130× abaixo da
   única banda".** A R5 tem **3** bandas e só **2 são comparáveis** (a terceira
   está em `norm-own`, não em `1/Pa`). As duas comparáveis **cercam o canônico**:
   `thread|35CrMo-SCM435` [4e-15, **2e-14**] ⇒ o canônico está **2,5× ACIMA** do
   teto; `faying|Q355B-Q235B` [**6,49e-12**, 7e-12] ⇒ 130× abaixo do piso. Como
   o engine usa a constante nos **dois** canais (apoio e rosca), **nenhum valor
   único pode estar dentro das duas** — o que transforma o item de "re-ancorar"
   em **separar a constante por interface**.
6. ~~**Armadilha do `check_input`**~~ — **CONSERTADO em 2026-07-28.** A guarda
   passou a aceitar as duas formas de nome (campo do engine **e** prior), e
   ganhou **`checkable_inputs()`** para desambiguar o `None` — que continua
   significando "dentro da banda" **ou** "não sei checar", e sem o set um
   parâmetro parecia ter passado por uma guarda que nunca rodou. Ganho colateral:
   `mu_dry` e `F_amp_ratio` eram **inalcançáveis** pelo nome do prior e agora
   avisam. 3 testes novos em `tests/test_anchor_priors.py`.
7. **Nome do hub** — o spec pedia `manual.html`; a página real é
   `concept_manual.html`, porque o explorador escreve toda página de Fundamentos
   com esse prefixo (o nome está fixo no laço de escrita **e** na navegação
   anterior/próxima). Criei `manual.html` como alias para quem digitar o nome do
   spec.

---

## 7. O Manual

| volume | conteúdo |
|---|---|
| [1 — Entender](01-entender-o-modelo.md) | paradigma, energia, a tese, **tabela de todas as constantes com proveniência**, L1–L7, falsificações |
| [2 — Explicar](02-explicar-o-modelo.md) | narrativa em 3 níveis, as 5 figuras com o que cada uma prova, FAQ de objeções com evidência, glossário |
| [3 — Aplicar](03-aplicar-o-software.md) | instalar, fluxo tela a tela, junta nova, paper novo fim-a-fim, reprodutibilidade, armadilhas |
| [hub no explorador](../../New_Theory/variable_explorer/concept_manual.html) | primeira trilha da landing "comece por aqui" |

**Gate da F6, cumprido e verificável:**

- **todo número sai do store/ledger** — o censo do Manual foi recomputado do
  store, independentemente do `numbers.json`, e bate;
- **figuras por script versionado** — `scripts/manual_figs.py --check`
  re-renderiza num temporário e exige os **11 artefatos byte-idênticos**; testado
  com dentes (restaurando o estado defasado real, acusou 11/11 e retornou 1);
- **links verificados** — **81** links relativos nos 5 arquivos do Manual e
  **191** hrefs/srcs no hub e no índice do explorador, **zero quebrados**,
  incluindo âncoras internas.

> Nota de honestidade sobre esta última linha: ela dizia "75 links nos 4
> arquivos" — o número medido **antes** de este relatório existir e ser linkado do
> README. Corrigido para o valor que o gate mede agora. Um relatório que
> autodeclara verificação é o pior lugar do repositório para um número solto.
