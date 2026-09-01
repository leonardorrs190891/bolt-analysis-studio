# Varredura de impossibilidade por réplica — e a CORREÇÃO do meu próprio teto

> ## ⚠ ERRATA (2026-07-28, mesmo dia) — leia antes do resto
>
> **A primeira versão deste documento usou uma métrica de "teto" ERRADA**, e a
> conclusão "**3 exceções novas**" está **corrigida para 1**.
>
> **O erro:** eu tomei *"quantas réplicas a midrange satisfaz"* como teto de passes.
> A midrange minimiza o **erro máximo** contra o grupo — ela **não maximiza a
> contagem** de membros satisfeitos. Uma curva que abraça um sub-agrupamento pode
> satisfazer **mais** membros que a midrange.
>
> **Como foi pego:** por **inconsistência interna**, não por revisão. No grupo
> ECCLES o meu "teto" deu **1** e o modelo de hoje faz **2** — um teto que o modelo
> supera não é teto.
>
> **O teto correto:** uma curva única fica a ≤0,10 de um subconjunto *S* **se e
> somente se** a dispersão ponto-a-ponto **de S** for ≤ **0,20** (a midrange de *S*
> serve). Logo o teto é o tamanho do **maior subconjunto com dispersão ≤ 0,20** —
> busca exaustiva, não um candidato só.
>
> | grupo | meia-disp. do grupo | teto **correto** | o que a midrange dizia | modelo hoje |
> |---|--:|--:|--:|--:|
> | BAUER fig6 (6 reps) | 0,2294 | **3 de 6** | 3 ✓ | 2 |
> | BAUER M12 fig8 (3) | 0,1944 | **2 de 3** | 0 ❌ | 0 |
> | ECCLES no-axial (4) | 0,1181 | **3 de 4** | 1 ❌ | 2 |
> | YANG_2021 (2) | 0,0366 | 2 de 2 ✓ | 2 | 0 |
>
> **O que sobrevive intacto:** a parte rigorosa do argumento —
> *meia-dispersão > 0,10 ⇒ **ao menos um** membro do grupo necessariamente viola*.
> Isso não depende da midrange e vale nos três grupos incompatíveis.
>
> **Contabilidade corrigida das exceções necessárias:**
> · BAUER fig6: teto 3 de 6 ⇒ **3 necessárias** (subconjunto viável = rep2/rep3/rep4
>   ⇒ as necessárias são **rep1, rep5, rep6**) — inalterado;
> · BAUER M12 fig8: teto 2 de 3 ⇒ **1 necessária** (subconjunto viável =
>   test2/test3 ⇒ a necessária é **test1**), **não 3**;
> · ECCLES no-axial: teto 3 de 4 ⇒ **1 necessária** (subconjunto viável =
>   fig3/fig7a/fig8c ⇒ a necessária é **fig8a_baseline1**) — resultado **novo**;
> · YANG_2021: grupo compatível ⇒ **0 necessárias** (classe FORM confirmada).
>
> **Total de exceções com prova: 6** (3 fig6 + 1 fig8_test1 + 1 eccles_fig8a + 1
> curva de resolução grossa do Yang 2023), e **4 recuperáveis em princípio**
> (fig6_rep4, fig8_test2, fig8_test3, eccles_fig8c).
>
> O corpo do documento abaixo **não foi reescrito**; os números de meia-dispersão e
> as exclusões de domínio permanecem válidos. Onde ele diz "teto 0 de 3", leia
> "teto 2 de 3, 1 exceção necessária".

---

**Data:** 2026-07-28 · **Store:** `4f5bedfbace4` (snapshot do HEAD) ·
**Só-leitura: nenhuma simulação, nenhum fit, nada escrito.**

Generaliza o método de [`data_limited_proof_2026-07-28.md`](data_limited_proof_2026-07-28.md):
*quando réplicas da mesma condição discordam entre si, existe um piso para o
`maxerr` de **qualquer** modelo — metade da dispersão entre elas.* A pergunta desta
varredura: **quantas das 55 curvas fora do tripé são inalcançáveis por esse
motivo, e não por falta de forma?**

---

## 1. O passo que quase invalidou a varredura: validação de domínio

Agrupando o registry por condição nominal (amplitude, F₀, frequência, bitola)
saem **31 grupos** com ≥2 curvas, **9 deles contendo curvas fora do tripé** —
~20 curvas. Parecia um achado grande.

**Não é.** A chave de agrupamento **não captura as variáveis que cada fonte varia
de propósito**, então ela **super-agrupa**. Confrontado com os nomes dos casos e
com as `apparatus_notes`:

| grupo | o que a fonte varia | veredicto |
|---|---|---|
| JCSR_2023 (5) | revestimento × ambiente (`galv`/`plain`/`stainless` × `indoor`/`outdoor`/`seawater`) | **variante deliberada** |
| SUN_2025_CRIMP (4) | fatorial 2×2 `grease`×`crimp` | **variante deliberada** |
| ROUSSEAU_2025 (2+2) | espessura do membro (`t10`/`t12`/`t14`) — *o ponto da fonte* | **variante deliberada** |
| LIU_2016 (9) | força axial 7,5→12,5 kN, lubrificação, torque | **variante deliberada** |
| ECCLES_2010 (10) | carga axial 0/1,1/2,7/3,1/3,5 kN, constante vs intermitente | **variante deliberada** |
| CHU_2026 (2) | rugosidade (`Ra1p6um`) | **variante**, e **sem `apparatus_note`** ⇒ não verificável |

> **A regra que isto instancia** — irmã da regra dos leitores de procedência:
> *o argumento de impossibilidade só vale entre réplicas genuínas. Aplicado a
> variantes deliberadas, ele isentaria o modelo de uma distinção que ele deveria
> fazer.* Um grupo cuja replicação não é **documentada** fica de fora: não poder
> verificar é motivo para excluir, não para presumir.

Sobraram **dois** grupos com replicação verificável, ambos do Bauer 2024 — e a
`apparatus_note` da fonte é explícita nos dois casos.

---

## 2. Bauer M8 fig6 (6 réplicas) — confirmado, inclusive pela nota

A `apparatus_note` diz, sem que ninguém tenha pedido:

> *"Fig 6 reps show specimen scatter (start values 0.93–1.08 after normalization
> — tightening scatter); **treat reps as an ensemble**."*

É validação independente da prova de ontem: **meia-dispersão 0,2294** na janela
pontuada por todas (47 % dos ciclos acima de 0,10), **teto 3 de 6**, modelo hoje em
**2 de 6**. Já está no relatório executivo §4.1.

---

## 3. Bauer M12 fig8 (3 réplicas) — **3 exceções novas, teto 0 de 3**

A nota descreve as três como **uma condição só**: M12×1,5, **F_M = 50 kN**,
excitação por espectro **80/150 µm**. E o caveat de digitalização diz o que
importa:

> *"**knee position varies per test** (F_V ≈ 35–40 kN when the collapse
> accelerates)."*

Elas diferem no **resultado**, não no **setup** — assinatura de réplica com
scatter de espécime. A diferença de vocabulário (`test` na fig8 vs `rep` na fig6)
é escolha do digitalizador, não distinção de condição.

**Medido** na janela pontuada por todas (`N` ∈ [26, 835]):

| | valor |
|---|--:|
| meia-dispersão máxima | **0,1944** |
| ciclos com meia-dispersão > 0,10 | **18 %** |
| **teto de passes** | **0 de 3** |
| modelo hoje | **0 de 3** |

**Nenhuma das três pode ser fechada por curva alguma** — o modelo já está no teto.
São **3 exceções necessárias**, provadas.

### 3.1 E aqui aparece um defeito de MÉTODO no classificador

As três réplicas estão hoje classificadas em **três classes diferentes**:

| curva | classe atual | motivo registrado | maxerr vs midrange |
|---|---|---|--:|
| `bauer2024_M12_fig8_test1` | **FORM**-LIMITED | forma | 0,1944 |
| `bauer2024_M12_fig8_test2` | **METRIC**-LIMITED | resgate_horizontal | 0,1944 |
| `bauer2024_M12_fig8_test3` | **LEVEL**-LIMITED | nível | 0,1552 |

**Três repetições do mesmo ensaio não podem exigir três tipos diferentes de
conserto.** O classificador não está errado nos seus próprios termos — ele lê cada
curva isoladamente, e cada uma *parece* pedir uma coisa diferente. O que ele **não
pode ver** é que a irredutibilidade vive na **família**, não na curva.

> **Lição de método:** um classificador por-curva é cego para limite por-família.
> Antes de atribuir classe, checar se a curva tem réplicas — e, se tiver,
> classificar o **conjunto**.

---

## 4. Yang 2021 (2 curvas) — hipótese **REFUTADA**, e isso valida o classificador

Mesma condição nominal (0,8 mm / 6 kN axial; a segunda é a curva "típica" da
Fig 2, com fratura em ~6.000 vs ~5.700 ciclos). Medido:

| | valor |
|---|--:|
| meia-dispersão máxima | **0,0366** |
| ciclos acima de 0,10 | **0 %** |
| **teto de passes** | **2 de 2** |
| modelo hoje | **0 de 2** |

**As duas SÃO alcançáveis** por uma curva única. Logo não são data-limited: o erro
é do modelo, e a classificação **FORM-LIMITED** que o classificador deu às duas
**está confirmada** por um teste independente. Resultado negativo — e é o que dá
crédito aos positivos.

---

## 5. Reclassificação resultante

| classe | antes | depois | delta |
|---|--:|--:|--:|
| LEVEL-LIMITED | 7 | **6** | −1 (`fig8_test3`) |
| METRIC-LIMITED | 7 | **6** | −1 (`fig8_test2`) |
| DATA-LIMITED | 5 | **8** | **+3** |
| FORM-LIMITED | 36 | **35** | −1 (`fig8_test1`) |
| **total fora do tripé** | 55 | 55 | — |

**Exceções com prova sobem de 4 para 7:** as 3 inalcançáveis da fig6
(`rep1`/`rep5`/`rep6`) + a curva de resolução grossa do Yang 2023 + as **3** da
fig8. E `bauer2024_M8_fig6_rep4` continua **fora** da lista (recuperável em
princípio).

### Correção ao meu próprio diagnóstico das LEVEL

[`level_limited_floor_read_2026-07-28.md`](level_limited_floor_read_2026-07-28.md)
analisou 7 curvas, e **uma delas (`bauer2024_M12_fig8_test3`) é provadamente
inalcançável** — não deveria estar no conjunto. Ela era, aliás, uma das 3 com
`plateau=False` que ficaram fora do veredicto de direção. O veredicto daquele doc
("1 fecha de 6, direção acerta 6/6") **não muda de valor**, mas o universo correto
é **6 curvas LEVEL**, não 7.

---

## 6. O resultado mais importante é o negativo

Das ~20 curvas que o agrupamento sugeria, **3** viraram exceção provada. As outras
saíram por **variação deliberada** (a fonte varia algo de propósito) ou por
**replicação não documentada**.

**Consequência para a estratégia:** a fila FORM **não** está inflada por
irredutibilidade escondida. Quem está construindo mecanismo para as ~35
form-limited está, majoritariamente, mirando alvo **alcançável** — o que era a
dúvida que motivou esta varredura. O risco de "construir forma para alvo
impossível" existia e foi **medido como pequeno**: 1 curva das 36.

---

## 7. Caveats

- A prova é sobre **`maxerr`** (o gargalo declarado: 34 das 55 violam só o pico);
  não afirma nada sobre o MAE individual.
- Todas as janelas são as **pontuadas** (`metric_x`), não as cruas, para não
  inflar a dispersão com trecho que a métrica descarta.
- Curvas normalizadas pelo **próprio primeiro ponto** (a âncora que a métrica usa).
- **CHU_2026 e o sub-grupo "no axial" do ECCLES ficaram sem veredicto** por falta
  de `apparatus_note` — são os dois lugares onde a varredura poderia render mais
  se a nota existisse. Hoje são 17 notas para 28 fontes.
- A classificação de réplica-vs-variante veio de nome de caso **+** nota de
  aparato. Onde as duas discordarem, a nota manda.
