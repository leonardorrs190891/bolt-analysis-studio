# Onde comparar **valor impresso** contra o **store** dá errado — 53 das 210 curvas (25 %)

**2026-08-14 (noite V)** · só-leitura · **nada adotado** · store `c37618c5cc96`, censo
**141/205**. Generalização de um erro próprio, retratado no mesmo dia.

---

## 1. O erro que motivou a medição

O **item J** da mesa nasceu de um round-trip em que comparei o valor **impresso** do artigo
(`N` até `F = 0,9·F₀` = 325) contra `metric_data` do store. Deu **253**, um desvio de −22 %,
e eu concluí que a digitalização estava adiantada. **Era artefato.**

`metric_data` é dividido pelo **próprio 1º valor do dado**. Na `chu…test3` esse valor é
**1,0259**, então o vetor inteiro desce 2,6 % e o cruzamento de 0,90 chega cedo. A CSV crua
dá **327** — **+1 %** contra os 325 impressos.

⇒ o erro não é sobre o CHU. Ele morde em **qualquer** comparação entre um número absoluto
do artigo e o que o store guarda, e só quando o 1º ponto do dado está longe de 1,0.

## 2. A população, medida

Fator `|F₀_bruto − 1|` por curva, lido pelo **carregador canônico**
(`inputs.load_full_curve`: coluna 0 e a **última** — as CSVs UFU têm 3 colunas e as do
`LIU_2020` estão em porcentagem):

| limiar | curvas | % das 210 |
|---|---:|---:|
| > **0,005** (piso de digitalização) | **53** | **25,2 %** |
| > 0,010 | 48 | 22,9 % |
| > 0,020 | 33 | 15,7 % |
| > 0,050 | 19 | 9,0 % |
| > 0,100 | 7 | 3,3 % |

mediana **0,0000** · p90 0,0406 · máx **0,2476**

**⇒ em três quartos das curvas a distinção é inócua; no quarto restante ela excede o ruído
do próprio dado.**

## 3. Onde vive — e o motivo é FÍSICO, não defeito

| fonte | curvas com \|F₀−1\| > 0,02 |
|---|---:|
| `LIU_2022_RETIGHT` | **12** |
| `SUN_2025_CRIMP` | 5 |
| `ECCLES_2010` | 5 |
| `BAUER_2024` | 4 |
| `CHU_2026` | 3 |
| `YANG_2019` · `JCSR_2023` · `YANG_2021` · `LI_2022_MARSTRUC` | 1 cada |

Os piores são os **estágios de reaperto** (`liu2022_fig6a_dry_release_t1/t2/t3`,
`fig7a_oil_direct_t*`, `fig8_multi_t*`, F₀ de **0,79** a 0,92) — a curva do estágio *n*
começa na pré-carga **residual** deixada pelo estágio *n−1*. **Isso é o experimento, não um
erro de digitalização.** O máximo (`sun2025…transverse_nogrease_standard`, F₀ = **0,7524**)
é da mesma natureza.

## 4. A regra que fica

> **Valor absoluto impresso no artigo compara-se à CSV CRUA**
> (`inputs.load_full_curve`), **nunca** a `metric_data`.
> `metric_data` serve para julgar o MODELO contra o dado — os dois passaram pela mesma
> normalização, então a comparação entre eles é legítima. O que não é legítimo é misturar as
> duas convenções.

E há **dois** passos de normalização no pipeline, fáceis de confundir — eu confundi:

* **do DADO**: `metric_data` dividido pelo próprio 1º valor (⇒ `metric_data[0]` = 1,0000
  exato, sempre);
* **do MODELO**: o campo `CaseResult.align`, que divide o *modelo* pelo valor dele no 1º
  ciclo do dado (na `test3` vale **0,99896** — perto de 1 e sem relação com o 1,0259).

## 5. O que isto NÃO diz

Não diz que alguma conclusão da campanha esteja errada. As métricas do tripé comparam
modelo e dado **sob a mesma normalização** e não são afetadas. O que fica exposto é uma
classe de **comparação externa** — artigo × store — que aparece em round-trips de
digitalização, e que agora tem a sua população delimitada em vez de ser descoberta um
engano de cada vez.

## Reprodutibilidade

`audit_align.py` + `chk_align.py` no scratchpad. ~2 min, só-leitura.

⚠️ **Nota de método:** a 1ª versão desta sonda parseava as CSVs à mão e devolvia
`F₀ = 120` (UFU, 3 colunas — peguei a do meio, em kN) e `F₀ = 100` (`LIU_2020`, em
porcentagem). O absurdo denunciou na hora, mas a lição é a de sempre nesta campanha:
**pergunte ao helper**. `load_full_curve` carrega convenções — qual coluna, quais unidades —
que ninguém lembra de cabeça.
