# Handoff — sessão paralela encerrada em 2026-07-28

> Esta era a **segunda** sessão do dia (a que rodou em paralelo à da métrica /
> rampa de fratura). Ela foi encerrada por decisão do professor; a outra segue.
> Este documento existe para que **nada precise ser reconstruído por leitura de
> `git log`** e para que fique explícito o que **não** se deve confiar.
>
> **Estado de saída, verificado:** nenhum trabalho meu sem commit · nenhum
> processo meu rodando · `validation_store.json` e `adopted_configs.json`
> **nunca escritos por mim** (todos os meus scripts são só-leitura; o store
> aparece modificado no fim porque a **outra** sessão estava com batch de adoção
> em voo).

---

## 1. O que foi entregue, com o commit de cada coisa

| # | entrega | commits |
|---|---|---|
| 1 | **Varredura das 4 classes** dos 55 fora do tripé (item 3 da fila) | `a184701` · `cbbf7e6` · `d44a7c5` · (3ª medição neste commit) |
| 2 | **Sonda das alavancas de nível** nas 7 LEVEL-LIMITED | `cbbf7e6` · `5fe9bfe` |
| 3 | **Reconciliação** com a medição independente da outra sessão | `63dab38` |
| 4 | **Conserto do `/simulate`** com campo sequencial (`mu_bearing_schedule`) | `26c303a` |
| 5 | **Matriz de procedência por constante** (o número da Fase 2) | `e082089` |
| 6 | Sincronização do Manual (3 volumes + README) | `2abc2cb` · este |

Arquivos vivos: `frontier_classes.{py,json,md}` · `level_seven_probe.{py,json,md}`
· `level_seven_reconciliacao.md` · `provenance_matrix.{py,json,md}`.
Todos os scripts são **só-leitura**, **deterministas** (verificado por hash) e
rodam com `py -3.12`.

---

## 2. Os números que ficam (e que substituem os anteriores)

**Censo das 55 fora do tripé — 3ª e última medição:**

| classe | n |
|---|--:|
| FORM-LIMITED | **36** |
| METRIC-LIMITED | **8** |
| LEVEL-LIMITED | **8** |
| DATA-LIMITED | **3** (por nome; **6** por contagem de teto de grupo) |

⇒ **19 das 55 não pedem física nova.** Manual e fila já sincronizados.

**Matriz de procedência (10 constantes do bloco `shared`):** só **3** dispensam
trabalho; **2** não têm procedência nenhuma; **1** é fitada **sem âncora**
(`W_conf_ref`); e **2 têm banda medida e o valor canônico está FORA dela**
(`k_wear_spec`, `N_emb`).

**Sonda de nível:** das 6 curvas de nível sondadas, ler as duas alavancas
disponíveis **fecha 1**, deixa **2 inertes** (Δ = 0 exato — o campo não faz nada
sem o pack correspondente) e **piora 3**.

---

## 3. ⚠ O que NÃO confiar, e o que corrigi de outros documentos

**(a) Correções que fiz em documentos da outra sessão / do Manual.** Todas com o
número medido no lugar:

1. `l7_removal_energy_diagnostic_2026-07-28.md` dizia *"única banda MEDIDA R5"* e
   *"~130× abaixo"* para o `k_wear_spec`. **A R5 tem 3 bandas**, só **2 são
   comparáveis** (a 3ª está em `norm-own`, não `1/Pa` — compará-la é erro de
   unidade), e a mais próxima é a `thread`, onde o canônico está **2,5× ACIMA do
   teto**. As duas comparáveis **cercam o canônico**; como o engine usa a
   constante nos dois canais, **nenhum valor único satisfaz as duas** ⇒ o item
   muda de "re-ancorar" para **separar a constante por interface**.
2. O mesmo doc dizia que "a banda medida empurra para **cima**". São **3 forças e
   duas apontam para baixo** — mover o valor não resolve em direção alguma.
3. Manual `00`/`03`: os dois pontos acima, propagados.
4. Manual `00`/`01`/`02`/`README`: censo das classes (3 vezes, ver §4).

**(b) O que EU errei, e onde está registrado.** Três erratas minhas, todas com a
causa medida:

| errata | o que estava errado | causa |
|---|---|---|
| 1ª | réplicas agrupadas por **nome** (`_repN`) ⇒ perdia `fig8_testN` | apontada pela outra sessão |
| 2ª | **super-atribuía** DATA-LIMITED a todos os membros de grupo disperso | dispersão alta prova que **um** viola, não que todos violem |
| 3ª | teto de grupo dava 4 onde a varredura dá 3 | **grade de interpolação**: 40 pontos sub-resolvem ~1 % (0,19944 vs **0,20134** convergido) |

Também afirmei duas coisas que **não se sustentaram na medição** e que estão
corrigidas nos próprios documentos: *"as 7 de nível são o alvo mais barato"*
(fecha 1 de 6) e *"o `N_emb` é achado novo"* (já estava no Manual como "não
reconciliada"; minha varredura só o reproduziu).

---

## 4. Aberto — e o que cada item custa

**(1) Divergência de NOME no BAUER fig6 — decisão de 1 linha.**
A varredura de réplica nomeia `rep1/rep5/rep6` como exceções necessárias. Medido
por busca exaustiva com grade convergida: existem **3** subconjuntos viáveis de
tamanho 3 — `{rep2,rep3,rep4}` (0,0738), `{rep3,rep4,rep5}` (0,1938),
`{rep3,rep5,rep6}` (0,1909). Como `rep5` e `rep6` aparecem em algum deles, **só
`rep1` é necessária por nome**. A **contagem** (3 de 6 têm de falhar) está certa.
*Ação:* ajustar a redação da varredura para separar contagem de nome. Nada de
física.

**(2) Convenção de janela no teto de grupo — questão aberta de método.**
A dispersão de um subconjunto pode ser medida na janela pontuada por **todos** os
membros (convenção da varredura, que eu adotei) ou na **interseção do
subconjunto**. Não é cosmético: no par `fig8_test2+test3` dá **0,0402** (janela
fixa) contra **0,2815** (janela própria) ⇒ teto **2** contra **1**.
*Argumento que não explorei:* a métrica pontua cada curva na sua **própria**
faixa, o que puxa para a janela própria. *Ação:* decidir a convenção; muda o
número de exceções necessárias.

**(3) `ValidationCase` não tem campo de carga axial nem de rugosidade.**
No ECCLES a carga axial vive só no `notes`/`case_id`; no CHU a rugosidade só no
`case_id`. Consequência medida: a chave de condição **funde as 10 curvas do
Eccles num grupo**, e por isso **não reproduzo** o teto do subgrupo "no-axial"
(que a varredura de réplica calcula e onde ela acha `fig8a_baseline1` como
exceção necessária). *Ação:* campos novos no dataclass, ou uma chave de
subgrupo explícita.

**(4) `k_wear_spec` por interface** — a única mudança que pode pôr o canal de
desgaste **dentro** de procedência medida. Constante nova ⇒ prereg. Ver
`provenance_matrix.md` §3/§6.

**(5) `N_emb` = 50 vs faixa lida [3, 15]** — já estava registrado como "não
reconciliada". O que acrescentei são **duas leituras**, e a 2ª é acionável: o
`N_emb` pode estar absorvendo atraso que pertence à **incubação do assentamento**
(fila item 8, UFU: *"dado plano até N≈38 e o modelo assenta desde o ciclo 1"*).
Diagnóstico só-leitura, sem prereg.

**(6) `checkable_inputs` cobre 2 das 10 constantes compartilhadas** — as outras 8
passam sem verificação, e `check_input` devolve `None` tanto para "dentro da
banda" quanto para "não sei checar". *Ação:* ampliar o set mesmo com banda vazia,
para que a ausência de âncora seja visível.

---

## 5. Lições de coordenação (para quando houver 2 sessões de novo)

1. **A corrida de índice do git ACONTECEU.** Um `git add` meu foi zerado no meio e
   6 arquivos meus entraram no commit da outra sessão. Nada se perdeu **porque os
   dois trabalhos eram só-leitura**; o dano foi uma mensagem de commit. Com
   escrita no store ou no `adopted_configs.json`, seria corrupção silenciosa.
2. **Duplicação total é o modo de falha mais provável, não a corrupção.** As duas
   sessões mediram a MESMA pergunta ("a leitura do nível fecha as
   LEVEL-LIMITED?") no mesmo dia, sem saber uma da outra.
3. **Mas duplicação reconciliada vira ativo.** O confronto por script deu **19 de
   19 números idênticos** — validação independente de um leitor de proveniência
   que nenhuma sessão sozinha poderia dar. E cada lado achou o defeito do outro.
4. **Nada reservava terreno.** Três candidatas minhas de trabalho paralelo
   evaporaram ao medir (índice de notas: o registry já resolve 27/28 · exclusões
   de teste: já consertadas em `e1cf3d9` · veredictos de banda: já no KB). O
   custo não foi das candidatas serem ruins — foi de não haver onde reivindicar.
   **Um `.superpowers/claims.md` (quem pegou o quê, quando, em que arquivos)
   custaria minutos.**
5. **Medir a coisa certa, não a fácil.** Contei nomes de arquivo e concluí que 10
   fontes tinham nota "perdida"; medindo a **resolução real do registry**, 27 de
   28 resolvem. A regra: medir pelo caminho que o software usa, não pelo
   sistema de arquivos.
