# Incubação (`slip_onset_W`) — **predição FALSIFICADA**, candidato da F morto como nomeado

**Data:** 2026-07-30 (madrugada) · **Store:** `3546e6745448` · sonda só-leitura
(`New_Theory/incubacao_discriminante.py`, dados em `incubacao_discriminante.json`).
**Nada adotado.** 9 curvas do `CHU_2026` × 4 valores de `slip_onset_W` = 36 células.

A predição foi **escrita antes** e está commitada em `cdeb883`
(`chu_segundo_defeito_resultado.md` §4), o que faz desta uma falsificação
pré-registrada — vale mais que um positivo achado por busca.

---

## 1. A predição, e o que foi medido

**Previsto:** `W_slip_acc += 4·µ·F₀·slip` por ciclo ⇒ o gate demora
`W_onset/(4µF₀·slip)` ciclos para abrir ⇒ em amplitude **pequena** o platô é longo
(morde) e em amplitude **grande** abre no 1º ciclo (inerte). Logo a redução de `|a|`
deve **ordenar pela amplitude**.

**Medido:** redução média de `|a|` = **+32 %** em D ≤ 0,4 mm contra **+47 %** em
D ≥ 0,5 mm. Não ordena pela amplitude, e o desvio é para o **lado oposto** do
previsto.

| curva | D [mm] | \|a\| nominal | \|a\| melhor | redução |
|---|--:|--:|--:|--:|
| `test1` | 0,3 | 0,009 | 0,008 | 13 % |
| `test2` | 0,4 | 0,940 | 0,776 | 18 % |
| `test7` | 0,4 | 0,474 | 0,151 | 68 % |
| `test8` | 0,4 | 0,848 | 0,587 | 31 % |
| `test3` | 0,5 | 0,347 | 0,089 | **75 %** |
| `test9` | 0,5 | 0,017 | 0,020 | −16 % |
| `test4` | 0,7 | 1,086 | 1,089 | −0 % |
| `test5` | 1,0 | 0,079 | 0,000 | **100 %** |
| `test6_repeat` | 1,0 | 0,134 | 0,028 | 79 % |

⇒ **O mecanismo alegado — gate dirigido por trabalho de slip — não é o que age.**
Ele mexe na curvatura, mas não pela via que a física propunha, então usá-lo seria
ajuste com nome de mecanismo.

## 2. O que ele faz de sistemático: piora a DERIVA

**O β aumenta em 34 das 36 células (94 %).** Exemplos: `test8` 0,584 → 0,933 ·
`test7` 0,506 → 0,934 · `test4` 0,181 → 0,708. A incubação **troca curvatura por
deriva** — e a deriva é a componente que já carrega 53 % da dispersão no cluster
DERIVA (atividade F).

⚠️ **Correção de uma leitura minha:** eu disse que *"onde |a| cai mais, as métricas
pioram"*. A correlação entre redução de `|a|` e aumento do MAE é **−0,202** — não
existe troca sistemática curvatura-vs-nível. O que é sistemático é o β (94 %). O
caso que me induziu ao erro foi a `test7` em W alto, que não generaliza.

## 3. Resultado nas pernas: nenhuma curva fecha

9 de 36 células são Pareto (as três pernas melhoram/empatam), mas:

- **4 são da `test1`**, que já passa com 0,0035/0,0082/0,0032 — o ganho é
  0,0035 → 0,0031, **cosmético**;
- **2 são da `test7`** com movimento desprezível (MAE 0,1504 → 0,1491);
- **1 é da `test6_repeat`**, idem (0,0266 → 0,0253);
- **2 são da `test3`** e essas são reais: em `W = 1e3`, MAE **0,1381 → 0,1050**
  (−24 %), res.máx 0,1741 → 0,1407, σ 0,0369 → 0,0330. **Ainda reprova** (MAE 2,1×
  o limite), mas é a única melhora com tamanho.

**Zero curvas passam a fechar o tripé.**

## 4. Consequência para o pipeline

1. **Risque a incubação da lista de candidatos para a curvatura do CHU.** Ela era o
   1º nomeado pela F; morre por falsificação da predição, não por magnitude.
2. **O CHU acumula agora TRÊS candidatos mortos**, cada um por um motivo diferente:
   µ prescrito (inerte em nível de lei, §4.54a) · `graded_scrit` (componente: trata
   a rampa, sobra a curvatura) · incubação (mexe na curvatura pela via errada e
   piora a deriva). Isso **reforça** o veredicto *form-limited* da fonte em vez de
   apenas repeti-lo.
3. **A classe de forma que a F apontou continua de pé, mas sem candidato nomeado.**
   O que a F mediu é que 12 das 16 curvas do cluster DERIVA fecham se rampa +
   curvatura forem capturadas; o que morreu foi o *como*. Os candidatos restantes da
   classe "taxa dependente do estado acumulado" (kernel desacelerante, bifurcação de
   limiar) **nunca foram sondados**.
4. **Lição de método que fica:** uma alavanca que move a grandeza-alvo **não** valida
   o mecanismo alegado. Sem o discriminante (aqui: a ordenação por amplitude), a
   redução de 68 % de `|a|` na `test7` teria passado por confirmação. O custo de
   escrever a predição antes foi ~10 linhas; o benefício foi não adotar uma forma
   errada com número bonito.

## 5. Reprodutibilidade

```bash
py -3.12 New_Theory/incubacao_discriminante.py            # 9 curvas x 4 valores
py -3.12 New_Theory/incubacao_discriminante.py --quick     # grade reduzida
```
