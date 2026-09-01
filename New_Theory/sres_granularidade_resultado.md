# O σ_res exigido é alcançável? — piso de granularidade do dado

**Data:** 2026-07-29 · **Store:** `3546e6745448` · **Script:**
`New_Theory/sres_granularidade.py` (só-leitura) · pré-pipeline.

## A pergunta, e por que ela precede o pipeline

A F7 provou um piso vindo da **repetibilidade** (dado contra dado, entre
réplicas). Existe um segundo piso, independente daquele: a **granularidade** do
próprio dado publicado. O modelo é liso — a saída do engine é uma trajetória
contínua. Se o dado zigue-zagueia entre pontos vizinhos com amplitude `s`, nenhuma
curva lisa passa por todos; ela passa pelo meio, o resíduo alterna, e isso produz
`σ_res ≈ s/2` **no melhor caso**. Se esse piso passar de 0,025, o limite é
inalcançável ali por qualquer modelo, e a curva é *metric-limited*, não
*form-limited*.

Se muitas das 51 violadoras caíssem nessa classe, o pipeline mudaria de alvo.

## Veredicto: NÃO. O σ_res é trabalho de modelo, não artefato de dado

| | curvas de 51 |
|---|--:|
| piso de granularidade **acima** do limite (inalcançável) | **1** (2 %) |
| piso entre metade e o limite (meio orçamento gasto em ruído) | 4 |
| **piso abaixo da metade — o gap é do MODELO** | **46 (90 %)** |

Ruído do dado em todas as 201 curvas com ≥ 5 pontos: mediana **0,0018**, p75
0,0042, p90 0,0121, máx 0,0725. **10 de 201** têm ruído acima de 0,025.

A única inalcançável é `10_Yang_2023…0_45_mm` (ruído 0,0363). As 4 do meio-caminho
são outras três do Yang2023 e a `caccese2009_tapered_45kN_rep2`.

## ⚠️ A primeira versão deste estudo dizia 19, e estava errada

Vale registrar porque o erro é instrutivo e quase foi publicado.

**1º estimador (ingênuo):** σ do dado contra a própria **média móvel de 3**.
Deu **19 de 51 inalcançáveis**, concentradas exatamente nas duas fontes que a
campanha mais penou: `LU_2024` **10/10** e `YANG_2023_IJPEM` **7/7**. Era um
resultado conveniente — explicaria os dois casos difíceis como limite de dado.

**O defeito:** a média móvel conta **curvatura** como rugosidade. Uma curva lisa
de joelho agudo — a forma típica desta biblioteca — já produz resíduo contra a
própria média de 3 pontos, porque a média "corta" a curva. As curvas do LU_2024
são justamente as de decaimento rápido em x log.

**2º estimador (o que vale):** ruído por **segunda diferença com mediana**. Para
ruído iid, `Var(y[i+1] − 2y[i] + y[i−1]) = 6σ²`, logo `σ = |d²|/√6`; a **mediana**
(×1,4826) separa ruído de curvatura, porque no joelho a 2ª diferença é grande mas
são **poucos** pontos, e a mediana os ignora.

| curva | σ_res | ruído (robusto) | média móvel (viesado) |
|---|--:|--:|--:|
| `lu2024_M8_fig18_amp2p0` | 0,1275 | **0,0104** | 0,1032 |
| `lu2024_M8_fig20_T4Nm` | 0,0877 | **0,0072** | 0,0373 |
| `10_Yang_2023…0_50_mm` | 0,1404 | **0,0121** | 0,0692 |

O estimador ingênuo errava por **até 10×** nas curvas de joelho agudo. Os dois
ficaram no script, o ingênuo marcado como não-usar e com o número do viés no
próprio docstring.

## O que isto faz com o plano

1. **A fila de forma é 46, não 22 nem 51.** As 51 violadoras do σ_res menos as 5
   com piso de granularidade relevante. É trabalho de física, e o item 1
   (sensibilidade) já mostrou que **nenhuma alavanca existente** o entrega ⇒ o
   pipeline tem de propor **forma**, e o gate dela deve incluir `Δσ/ΔMAE`.
2. **Fecha uma porta de saída fácil.** A hipótese "o σ_res é artefato de dado
   grosso" está **falsificada com número** — não volta como suposição.
3. **Sobra uma classe de exceção pequena e legítima:** 1 curva inalcançável por
   granularidade + 4 no meio-caminho. Cinco, não dezenove — e são candidatas a um
   3º tipo de prova (piso de granularidade), distinto do piso de repetibilidade da
   F7 e do julgamento humano do S4.
4. **Corrige uma leitura antiga:** o `METRIC_LIMITED` do lint de digitalização
   (88 curvas, degrau entre vizinhos ≥ 0,10) mede o **degrau bruto**, que inclui
   a queda real da curva. Ele continua válido como aviso sobre a régua do
   **res.máx**, mas **não** autoriza dizer que o σ_res dessas curvas é
   inalcançável — este estudo é que responde isso, e responde "não".

## Reprodutibilidade

```bash
py -3.12 New_Theory/sres_granularidade.py   # segundos, só-leitura
```
