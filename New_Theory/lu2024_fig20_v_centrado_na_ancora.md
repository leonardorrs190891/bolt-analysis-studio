# `lu2024_fig20_T10Nm` — a única da fila, e o erro é um **V centrado na âncora de calibração**

**2026-08-16 (04:0x)** · só-leitura · **nada adotado** · store `20be19aabe11`,
censo **144/205**, `form_limited` **1 → 0** (com esta entrada), 2ª linha **18 → 19**.

---

## 1. Por que ela apareceu agora

A `form_limited` esteve em **ZERO** a sessão inteira. A correção de dado da sessão
B (`db88dcd`, pico espúrio em 6 CSVs do `LU_2024`) removeu o salto que fazia esta
curva cair em `metric_limited_colapso` — o teste do colapso é
`max|Δdado| > 0,25`, e **o pico ERA aquele salto**. Sem ele, a curva atravessa e
chega à **única camada de trabalho legítimo**.

⇒ o defeito de dado estava **escondendo** a curva na camada errada.

## 2. O erro inteiro é UM DEGRAU no primeiro ciclo

| | valor |
|---|---:|
| MAE · res.máx · σ | **5,03×** · 3,15× · 3,00× |
| viés · `\|viés\|/MAE` | **−0,2514** · **1,00** (sinal único) |
| resíduo por terço | −0,229 · −0,286 · −0,236 (plano) |
| maior salto | ciclos **0→1**, Δ **−0,2650**, **u = 0,00** |
| incremento tardio total | **0,00338** ⇒ forma sobre o fim não move a curva |
| canal | **embedding 0,698** do total (rotacional 0,189; wear 0,012) |

⇒ o modelo perde **26,5 % da pré-carga no primeiro ciclo** e o dado não. Não é
taxa nem forma tardia: é **assentamento inicial em excesso**.

## 3. E o erro é ORDENADO PELO TORQUE, com o mínimo na âncora

| T (N·m) | 4 | 10 | 16 | **22** | 28 |
|---|---:|---:|---:|---:|---:|
| MAE | 0,3424 | **0,2514** | 0,1572 | **0,0364** | 0,1008 |
| viés | −0,342 | −0,251 | −0,157 | **−0,036** | −0,090 |
| no tripé | não | não | não | ✅ **sim** | não |

`ρ(torque, MAE)` = **−0,900** · `ρ(torque, viés)` = **+0,900**.

**Os cinco vieses são NEGATIVOS** (o modelo sempre perde mais que o dado) e a
magnitude desenha um **V com mínimo exatamente na T22** — que é **a curva contra
a qual a fonte foi calibrada** (é o mesmo ensaio da `fig18_amp1p0`, publicado em
duas figuras).

⇒ **a constante foi fitada na âncora e não transfere pela série de torque.**

## 4. A forma tem nome, e a capacidade já existe

O mecanismo é direto: o **embedding** carrega 0,698 da perda e, na lei vigente,
**não escala com a pressão de contato**. Torque baixo ⇒ F₀ baixo ⇒ pressão baixa
⇒ o reservatório de encaixe deveria ser **mais raso** — e não é.

⚠️ Isso é **exatamente** o que o campo `emb_pressure_exp` modela, construído pela
sessão B horas antes (`945f363`, default-inerte, **não adotado**):

> *"o achatamento plástico é DIRIGIDO POR PRESSÃO, então abaixo de uma pressão de
> referência o escoamento é menor e o reservatório de encaixe é mais RASO"* —
> `S_p = min(1, (p_init/p_ref_emb) ** emb_pressure_exp)`

E o veredito delas: *"a lei conserta o defeito que nomeou e **NÃO fecha a
curva**"*.

## 5. Nenhuma alavanca fecha — 8 varridas

A melhor (`arrest_approach_exp` = 2) leva σ de 3,00× a **2,67×**, contra os
**67 %** de redução necessários. Quatro das 8 estão **travadas por procedência**
(`N_emb`, `emb_depth`, `loose_arrest_floor`) — e `emb_depth` é input de tabela
VDI, não botão.

## 6. ⚠️ Onde isto fecha o padrão do dia

**Sexta fonte** com a mesma estrutura, e a terceira variável de ordenação:

| fonte | ordenada por | achado |
|---|---|---|
| `LIU_2025` (D-AD) | **amplitude** | `ρ(amp, viés)` = +1,000 exato |
| `ICMEZ_2025` | grip / regime | canal arresta, dado atravessa |
| `ROUSSEAU_2025` | — | ótimos por curva disjuntos |
| `YANG_2021` | — | forma adotada, net zero |
| `SUN_2025_CRIMP` | — | par com formas opostas |
| **`LU_2024` fig20** | **torque (F₀)** | **V centrado na âncora**, ρ = +0,900 |

⇒ em seis fontes independentes: **a forma existe ou é alcançável, e uma constante
compartilhada não serve à própria fonte.** Aqui o eixo é o **F₀**, e o mínimo do
erro cai **na curva usada para calibrar** — a assinatura mais limpa possível de
sobreajuste à âncora.

## Reprodutibilidade

`py -3.12 New_Theory/ataque_curva.py lu2024_M8_fig20_T10Nm`; a série lida do
store via `CaseResult`, correlações por `scipy.stats.spearmanr` sobre os vieses
de `metric_pred − metric_data` — nenhum valor suposto.
