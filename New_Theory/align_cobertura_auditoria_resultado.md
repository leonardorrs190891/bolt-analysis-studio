# O `align` está **exonerado** — mas quantifica uma lacuna de COBERTURA em 11 curvas

**2026-08-12** · só-leitura · **nada adotado** · store `bd74eaf0b11d`, censo **147/205**.

## A premissa testada

`CaseResult.align` divide o modelo pelo seu próprio valor no **1º ciclo do dado** — por decisão
registrada (*"o artigo normaliza F/F₀ = 1 ali e a queda anterior (assentamento) não tem
contraparte medida"*). A auditoria de âncora do `YANG_2021` (08-10) mostrou que esse fator
diferia **10 %** entre réplicas da mesma condição. A pergunta que ficou sem resposta, e que
nunca foi feita em escala de biblioteca:

> **O `align` age como um grau de liberdade oculto? Curvas com correção grande passam mais
> facilmente?**

Ela importa porque `align` **não é constante fitada** — não aparece em `prov`, não entra na
contagem de DOF, e ninguém o gateia. Se comprasse aprovações, seria overfitting invisível.

## ✅ A resposta é NÃO — e o número é claro

| \|align − 1\| | n | no tripé | **taxa** | MAE mediano |
|---|---:|---:|---:|---:|
| **< 2 %** | **182** (89 %) | 135 | **74 %** | 0,0258 |
| 2–5 % | 7 | 2 | 29 % | 0,0745 |
| 5–10 % | 2 | 1 | 50 % | 0,0826 |
| 10–20 % | 3 | 1 | 33 % | 0,0167 |
| **> 20 %** | **11** | 8 | **73 %** | 0,0316 |

* **Mediana da correção: exatamente `0,0000`.** Em 89 % da biblioteca o `align` é **inerte** —
  o modelo vale 1,0 no primeiro ponto do dado sem precisar de normalização.
* As curvas com correção **> 20 %** passam a **73 %**, contra **74 %** das com correção < 2 %.
  **Não há vantagem.** O `align` não compra aprovação.
* As faixas intermediárias têm taxas menores (29 %, 50 %, 33 %) mas **n = 7, 2 e 3** — amostras
  pequenas demais para concluir qualquer coisa, e digo isso em vez de ler tendência em 2 curvas.

## ⚠️ O que a mesma medição revela: uma lacuna de COBERTURA, não de modelo

`ρ(N do 1º ponto, |align − 1|) = **+1,00**` — correlação de posto **perfeita**: quanto mais tarde
a digitalização começa, maior a correção. É mecanicamente esperado (mais decaimento do modelo
antes da âncora), e é justamente por isso que serve de **medida de cobertura**.

Nas 11 curvas com correção > 20 %:

| curva | `align` | correção | 1º ponto |
|---|---:|---:|---:|
| `sun2025…axial_F7.5kN_standard` | 0,6219 | **37,8 %** | N = 1020 |
| `li2022ti_axialmin_10Hz` · `li2022ti_axial_10Hz_full` | 0,6324 | 36,8 % | N = 200 |
| `li2022ti_axialmin_15Hz` · `_20Hz` | 0,635 | 36,4 % | N = 200 |
| `sun2025…axial_F17.5kN_standard` | 0,6518 | 34,8 % | N = 255 |
| `yang2021_fig2_typical` | 0,6904 | 31,0 % | N = 500 |
| `yang2021_amp0p8mm_ax6kN` | 0,6943 | 30,6 % | N = 300 |
| `sun2025…F7.5kN_crimp` | 0,7041 | 29,6 % | N = 2041 |
| `yang2021_amp1p0mm_ax2kN` | 0,7108 | 28,9 % | N = 150 |
| `sun2025…F17.5kN_crimp` | 0,7531 | 24,7 % | N = 102 |

⇒ **nestas 11, entre 25 % e 38 % da perda que o modelo prediz nunca é confrontada com dado.**
Isso **não** é erro do modelo nem do `align` — é o que a digitalização cobre. Mas significa que
o veredito do tripé nessas curvas julga **dois terços a três quartos** do comportamento
predito, e isso não estava escrito em lugar nenhum.

**8 das 11 estão no tripé.** A leitura honesta é: *elas passam no trecho medido*, não *elas
estão certas de ponta a ponta*.

## Por que isto é diferente do achado de âncora do `YANG_2021`

Lá o problema era **comparabilidade entre réplicas** (três curvas da mesma condição normalizadas
em pontos diferentes ⇒ piso inflado 4×) — e a rota de re-ancoragem foi **falsificada** porque só
afrouxava as que já passavam.

Aqui não há proposta de mudar nada: o `align` está correto e é inerte em 89 % da biblioteca. O
que se acrescenta é a **declaração de cobertura** das 11, que hoje passam sem essa ressalva
estar visível.

## O que fica

* Premissa testada e **mecanismo exonerado**: `align` não infla aprovação (73 % vs 74 %).
* **Lacuna declarada:** 11 curvas com 25–38 % da perda predita fora da janela da métrica —
  candidata natural a nota nos reports por caso dessas curvas (custo baixo, não muda número).
* Sugestão de método, sem custo: publicar `align` ao lado das 3 pernas nos reports das curvas
  com correção > 20 %, pela mesma razão que o `σ_res` passou a ser publicado — **o que não é
  mostrado não é auditado**.

## Reprodutibilidade

`align_audit.py` no scratchpad: lê `CaseResult.align` e `metric_x[0]` dos 205 registros do
store, cruza com o veredito canônico do tripé. Segundos, só-leitura.
