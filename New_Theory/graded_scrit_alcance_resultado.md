# `graded_scrit` — sonda de alcance (atividade B pré-pipeline)

**Data:** 2026-07-29 · **Store:** `3546e6745448` · **Script:**
`New_Theory/graded_scrit_alcance.py` · dados: `graded_scrit_alcance.json`.
**PROBE, não adoção** — nada escrito no store nem em `adopted_configs.json`.

## Veredicto em três linhas

1. **A capacidade faz o que promete:** remove a rampa do resíduo. O |β| cai
   **76–98 %** nas 4 curvas do cluster DERIVA (o melhor: 0,576 → **0,010**).
2. **Mas não fecha nenhuma curva:** **0 de 72** células (6 curvas × 12 pares
   s_crit×k) passam o tripé. *(A frase original continuava "depois de tirar a rampa, o
   σ_res ainda é 4–6× o limite" — **retratada**: ela vinha do erro de célula da §
   marcada com ⚠️ abaixo. Algebricamente o que sobra na `test2` é 0,0229, dentro do
   limite. O "0 de 72" segue válido — nenhuma célula desta alavanca fecha o tripé.)*
3. **A assinatura da atividade A tem poder PREDITIVO** — e isso é o achado
   metodológico que sobrevive a este estudo.

## O que foi varrido

`loose_rate_mode="graded_scrit"` com `s_crit_loose ∈ {50, 100, 200} µm` (banda de
procedência Bauer 76–108 µm) × `k_loose_graded ∈ {1e-4 … 1e-1}` (sem procedência,
por isso varrido por décadas). 6 curvas: as 4 do cluster **DERIVA** (assinatura
casa com a promessa de "colapso quase-linear") + 2 dos alvos **originais** da
capacidade (Yang2019, Yang2023-IJPEM), que a atividade A classificou como
ONDULADO/mista e que servem de controle.

## A predição da atividade A se confirmou

| curva | classe (atividade A) | \|β\| nominal → melhor | σ_res | Pareto |
|---|---|---|--:|--:|
| `chu2026ti_D0p4mm_F0_49kN_test2` | DERIVA | 0,576 → **0,010** | 0,190 → 0,111 | **6/12** |
| `chu2026ti_D0p4mm_F0_73kN_test8` | DERIVA | 0,584 → 0,121 | 0,192 → 0,164 | **4/12** |
| `chu2026ti_D0p7mm_F0_49kN_test4` | DERIVA | 0,181 → 0,043 | 0,126 → 0,106 | 0/12 |
| `chu2026ti_D0p4mm_F0_61kN_test7` | DERIVA | 0,506 → 0,287 | 0,167 → 0,125 | 0/12 |
| `yang2019_M10_amp0p4_5Hz` | ONDULADO (alvo original) | 0,115 → 0,092 | 0,077 → 0,069 | 0/12 |
| `10_Yang_2023…0_50_mm` | mista (alvo original) | 0,181 → **0,370** | 0,140 → **0,177** | 0/12 |

**Pareto** = células que melhoram as **três** pernas simultaneamente: **10 de 72,
todas no cluster DERIVA** (6 em test2, 4 em test8), zero fora dele.

A leitura: a capacidade ajuda onde a assinatura previu que ajudaria, é fraca no
alvo ONDULADO, e **piora** o caso mista — β dobra e σ_res sobe. Ou seja, a
classificação por assinatura de resíduo não é descritiva: ela **prediz** onde um
candidato de forma vai morder. É o que justifica usá-la para escolher candidatos
em vez de tentar todos.

## ⚠️ Uma verificação interna que estava ERRADA — corrigida em 2026-07-29 (atividade F)

> **O texto original desta seção misturava duas células diferentes da varredura e a
> conclusão que ele tirava está retratada.** Fica registrado aqui, com o conserto,
> porque o erro é instrutivo: ele passou por parecer aritmeticamente coerente.
>
> O que a seção afirmava: *"Medido na célula que zerou o β: 0,111 (59 % do original)"*,
> e daí *"sobra σ_res ≈ 0,11 ⇒ há um segundo defeito e ele domina"*.
>
> **O erro:** o β ≈ 0 vem da célula `(50 µm, 1e-2)`, que tem σ_res = **0,2018** (pior
> que o nominal) **e MAE 0,4573** — o triplo do nominal. O σ_res = 0,1112 vem de outra
> célula, `(200 µm, 1e-2)`, cujo β é −0,085 e cujo MAE é 0,326. Peguei o β de uma e o
> σ de outra.
>
> **O achado que o erro escondia é maior que ele:** *nenhuma* célula remove a rampa
> sem destruir o nível — as que endireitam o resíduo pagam com MAE 2–3×. Ou seja **não
> existe estado do modelo em que a rampa saia e o resto fique intacto**, e a pergunta
> "o que sobra?" não é respondível por alavanca. Ela é respondível por álgebra.
>
> **A resposta correta** (`chu_segundo_defeito_resultado.md`, decomposição do resíduo
> nominal em rampa + curvatura, com σ corrigido por graus de liberdade): o que sobra na
> `test2` é **0,0229**, não 0,11 — e isso **cabe no limite** de 0,025. Rampa + termo
> quadrático explicam **99 %** da variância. No cluster DERIVA inteiro (16 curvas):
> 53 % rampa + 16 % curvatura + 31 % resto, e **12 das 16 passariam a 3ª perna** se as
> duas formas fossem capturadas.
>
> A leitura muda de *"sobra um defeito que domina e não sabemos qual é"* para **"sobram
> duas formas nomeáveis, a segunda é lisa (joelho no lugar errado) e ordena pela
> amplitude"** — o que aponta a incubação (`slip_onset_W`, presente no engine e
> desligada) como candidato com teste discriminante escrito.

## O que o pipeline deve fazer com isto

1. **`graded_scrit` é COMPONENTE, não candidato.** Ela trata a rampa; a rampa é
   ~40–60 % da dispersão nas curvas do CHU. Um prereg que a proponha sozinha
   falharia o gate — e agora se sabe disso **antes** de escrever o prereg.
2. ~~**O alvo real do CHU é o defeito que sobra.** A próxima medição útil é
   caracterizar o resíduo *depois* de remover a rampa (rodar a célula Pareto e
   reclassificar pela atividade A)~~ ✅ **EXECUTADO em 2026-07-29 — e a receita aqui
   proposta não funciona.** Rodar a célula Pareto mede a estrutura que a alavanca
   introduz, porque nenhuma célula remove a rampa sem triplicar o MAE. A caracterização
   correta é **algébrica** (projeção em rampa + curvatura sobre o resíduo nominal):
   `chu_segundo_defeito_resultado.md`. Veredicto: o defeito remanescente é **curvatura
   lisa** (joelho adiantado), ordena pela **amplitude** (9,9× entre D=0,4 e D≥0,5 mm), e
   o candidato nomeado é a **incubação** `slip_onset_W`, já no engine e desligada.
3. **Não usar a capacidade nos alvos originais sem re-medir.** No `Yang2023 0,50`
   ela piora as três pernas. Se a proposta de 2026-07-28 ("limiar graduado" para
   Yang2019+Yang2023) ainda estiver na fila, esta medição a contradiz para o
   Yang2023 e a torna marginal para o Yang2019 (σ −0,008).
4. **`k_loose_graded` continua sem procedência.** Mesmo que fechasse, adotá-la
   exigiria âncora — o melhor k varia 1e-3…1e-1 entre curvas da MESMA fonte, o
   que é sinal de constante por-curva, não de física compartilhada.

## Reprodutibilidade

```bash
py -3.12 New_Theory/graded_scrit_alcance.py            # ~15 min, 78 simulações
py -3.12 New_Theory/graded_scrit_alcance.py --quick     # smoke
```
