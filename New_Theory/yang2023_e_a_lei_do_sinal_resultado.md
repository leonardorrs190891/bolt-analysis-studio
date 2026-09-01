# YANG_2023 não é uma classe — e a "lei do sinal por regime" que ela sugeria é FALSA na campanha

**2026-08-15 (noite)** · store `20be19aabe11` · só-leitura · **nada adotado**.

## 1. YANG_2023_IJPEM: 3 abertas, 3 regimes, 3 sinais — não formam classe

| curva | parafuso | δ | estatuto | MAE | stick % | terços (ini/meio/fim) | fim dado |
|---|---|---:|---|---:|---:|---|---:|
| 0,30 | M6 | 0,30 | ABERTA | 0,1200 | 13 % | +0,042/+0,155/**−0,056** | 0,220 |
| 0,35 | M8 | 0,35 | ABERTA | 0,1788 | 68 % | +0,023/**−0,326**/−0,265 | 0,150 |
| 0,50 | M6 | 0,50 | ABERTA | 0,2386 | **0 %** | +0,098/**+0,375**/+0,247 | 0,120 |

Três situações distintas: a 0,35 perde **demais**, a 0,50 perde **de menos** (o
dado colapsa a 0,12 e o modelo não segue), a 0,30 troca de sinal no meio.
⇒ **não é uma classe**; cada uma exige diagnóstico próprio. (A 0,50 tem n=5 ⇒
σ não julgável pela regra assinada; MAE 4,8×.)

## 2. O que a varredura M8 sugeria — e a medição que a derruba

Ordenando as 6 curvas M8 por amplitude, o sinal do resíduo **vira com o
regime**: 100 % stick (δ=0,18/0,25) ⇒ modelo perde de **menos** (+0,016/+0,367
no fim); 68→11 % stick (δ=0,35…0,65) ⇒ perde de **mais** (−0,16 a −0,33).
Hipótese tentadora: *"os canais de stick (embedding/creep) sub-produzem e os de
slip (wear/rotacional) super-produzem"* — uma lei da campanha inteira.

**Testada nas 205 comparáveis** (fração do canal de slip na decomposição do
store × viés):

| faixa de canal-de-slip | n | viés médio | % com viés > 0 |
|---|---:|---:|---:|
| stick puro (<5 %) | 72 | −0,0130 | 35 % |
| quase-stick (5–30 %) | 29 | +0,0079 | 72 % |
| misto (30–70 %) | 63 | −0,0213 | 32 % |
| slip-dominado (>70 %) | 41 | +0,0131 | 59 % |

**Correlação(fração de slip, viés) = +0,050** (Spearman +0,053) ⇒ **nula**.
Sem tendência monotônica; nenhuma faixa tem sinal consistente.

Restringindo às **68 que falham** o tripé, a correlação sobe para +0,183 (ainda
fraca) e o sinal é o **OPOSTO** da hipótese: stick puro **−0,056** (perde
demais) contra slip-dominado **+0,018** (perde de menos).

⇒ **a hipótese está falsificada, e no sentido contrário.** O `YANG_2021` (100 %
stick, abertas com viés **positivo**) e o `YANG_2023` M8 (stick com viés
positivo) são casos particulares, não instâncias de uma lei.

## 3. O que isto corrige na síntese das três fontes

O dossiê de 21:1x dizia que ICMEZ, ROUSSEAU e YANG_2021 têm "a mesma
estrutura". **A estrutura é a mesma** — *a forma existe e uma constante
compartilhada não serve à própria fonte* — mas a **direção não é**: não há
sinal comum de viés, nem por regime nem por fonte. Qualquer forma nova terá de
ser justificada **por fonte**, com o seu próprio discriminante medido; a
tentação de unificar as três num único mecanismo está **medida e recusada**.

## 4. Reprodutibilidade

Instrumentação de `resolve_transverse_slip` (YANG_2023, 9 curvas) e leitura da
decomposição gravada no store para as 205 (custo zero, sem re-simular).
