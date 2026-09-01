# MARGENS fase 1 — ECCLES e CHU: o defeito é REGIONAL, não pontual

**2026-08-06 (noite)** · fase 1 do pipeline MARGENS (nomear o ponto que
reprova) nos alvos sem agente. Só-leitura, store `5916d8be0510`.

## ⚠️ Correção de premissa minha

O charter da fase A diz *"mx = o argmáximo; é pontual por natureza"*. Isso é
verdade **estruturalmente** (o res.máx é um ponto só), mas eu vinha inferindo
daí que o **defeito** é pontual — e nos briefings do BAUER/ECCLES escrevi
"mx-bound = UM ponto decide". **Medido, é falso em 5 de 5.**

| curva | argmáx | 2º | 3º | mx sem o argmáx | defeito |
|---|---|---|---|---|---|
| `eccles_fig8a_baseline1` | −0,1223 @175 | −0,0969 @200 | −0,0577 @150 | 0,0969 → passaria | **região** N=150–200 |
| `eccles_fig8b_axial0p7` | −0,1296 @175 | −0,0750 @150 | +0,0475 @100 | 0,0750 → passaria | região N=150–175 |
| `eccles_fig7d_axial3p1` | −0,0891 @1500 | −0,0882 @1375 | −0,0878 @750 | 0,0882 | **platô inteiro** (750–1500) |
| `eccles_fig8c_baseline2` | −0,1452 @200 | −0,1241 @250 | −0,1042 @300 | 0,1241 → **ainda viola** | região N=200–300 |
| `chu_D0p5_Ra1p6_test9` | −0,1173 @121 | −0,1159 @82 | −0,1066 @163 | 0,1159 → **ainda viola** | região N=82–163 |

Em nenhuma delas existe "o ponto errado": os três maiores resíduos são vizinhos
e da mesma ordem. Consertar dado num ponto não fecha nenhuma — e em duas nem a
perna mx cede.

**Consequência prática:** essas 5 saem da hipótese de conserto barato. A
fidelidade ainda vale a pena medir (uma deriva regional é exatamente o que o
D-W achou na `lu2024_amp1p5`), mas o prognóstico muda: é re-digitalização de
trecho, não correção de ponto.

## Dois achados de anatomia

**1. `eccles_fig8c_baseline2` é NÍVEL PURO** — viés **−0,0431 = −MAE exato**,
**zero cruzamentos**, os 23 resíduos negativos. Mesma assinatura da
`karlsen_run1p2` (em investigação) e das que já renderam conserto de
base/input nesta campanha. É a mais promissora das cinco para auditoria de
input, apesar de não ser a mais próxima.

**2. O sinal é NEGATIVO nas 4 do ECCLES** (viés −0,0195 a −0,0451): o modelo
fica **abaixo** do dado, isto é, **colapsa cedo demais**. Na `fig8b` isso chega
ao extremo: em N=175 o **modelo já está em 0,0000** enquanto o dado ainda
retém 13 %.

⇒ parecia a **mesma família** que o subagente do BAUER nomeou horas atrás
("relógio do colapso terminal", M8 ~9–11 % cedo). **Medi, e a afirmação precisa
ser refinada — ver a seção abaixo.**

## ⚠️ CORREÇÃO da própria frase acima: o relógio erra SÓ NA CAUDA

Medi em que N cada curva cruza `ratio = 0,50` e `0,30`, modelo contra dado
(razão = N_modelo / N_dado; <1 = modelo adiantado):

| fonte | curva | razão @0,50 | razão @0,30 |
|---|---|---:|---:|
| ECCLES | fig3_typical | 1,00 | 0,89 |
| ECCLES | fig7a_no_axial | 1,01 | 0,86 |
| ECCLES | fig7b_1,1 kN | 1,05 | 0,89 |
| ECCLES | fig7c_2,7 kN | 1,13 | 1,05 |
| ECCLES | fig7d_3,1 kN | 1,18 | 1,08 |
| ECCLES | fig8a_baseline1 | 1,01 | 0,93 |
| ECCLES | fig8b_0,7 kN | 1,08 | 1,02 |
| ECCLES | **fig8c_baseline2** | 0,99 | **0,68** |
| ECCLES | **fig6_4 kN** | 0,93 | **1,88** |
| ECCLES | **fig8d_3,5 kN interm.** | **3,83** | **2,77** |
| BAUER | rep1 | 0,92 | 0,91 |
| BAUER | rep2 | 1,06 | 1,00 |
| BAUER | rep4 | 1,13 | 0,87 |
| BAUER | rep5 | 0,98 | 0,93 |
| BAUER | rep6 | 1,23 | 1,08 |
| BAUER | M12_test3 | 1,04 | — |

**O que isto muda:**

1. **O relógio de MEIO DE CURVA está certo nas duas fontes** — razão @0,50 entre
   0,92 e 1,23 em 15 das 16, com mediana ≈1,01. Dizer "o modelo colapsa cedo"
   sem qualificar era impreciso: ele acerta *quando* a junta perde metade.
2. **A divergência é da CAUDA** (@0,30) e sua magnitude varia muito: BAUER
   0,87–1,08 (os 9–11 % que o subagente nomeou), ECCLES 0,68–1,08 nas curvas
   normais. A `fig8c` — a de nível puro — é a pior: **32 % adiantada**.
3. **E há duas com o sinal INVERTIDO**, ambas de carga axial alta: `fig8d`
   (3,5 kN intermitente, **3,83× @0,50** e 2,77× @0,30) e `fig6` (4 kN,
   1,88× @0,30). Nessas o modelo está **muito atrasado**. Dentro da mesma
   fonte, o sinal do erro de relógio **troca com a carga axial** — assinatura
   de sub-resposta à variável varrida, agora com **carga axial** como
   candidata a 5ª ocorrência. ⚠️ Não medido aqui: ambas têm protocolo especial
   ("intermittent"/"annotated"), então pode ser o protocolo e não a carga.
   Precisa do teste de espalhamento com as 7 cargas do ECCLES, agrupadas pela
   variável de fato varrida.

**Portanto**: "duas fontes, mesmo defeito" está **parcialmente errado** como eu
escrevi. O correto é: as duas erram na cauda, com magnitudes diferentes; e o
ECCLES tem, além disso, um regime de carga axial alta onde o erro **inverte** —
o que é outro defeito, não o mesmo.

## Estado

Nenhuma ação executada. As 5 continuam com o estatuto vigente (4 exceções
assinadas + 1 classe_parada). O que muda é a **expectativa**: não são
fechamentos baratos, e a `fig8c` merece auditoria de input pela assinatura de
nível puro.
