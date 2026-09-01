# P-7 fica barata: as "órfãs" da reclassificação **não existem** — são quase-acertos de limiar

**2026-08-07** · só-leitura · **nada executado** · preenche a limitação
declarada da P-7.

## O que travava a P-7

A própria P-7 declarava o limite dela:

> *"O veredicto por curva é sobre **nível terminal**, bom para dizer 'o remédio
> da classe não se aplica' e **insuficiente para dizer o que se aplica**."*

Sem saber o que se aplica, executá-la parecia trocar *"parada numa classe
errada"* por *"sem explicação nenhuma"* — e o `mapa_das_65_fora_resultado.md`
tinha acabado de celebrar **zero curvas sem explicação**. Este é o custo que a
P-7 não tinha escrito.

## Primeiro: o custo é real, e menor do que parecia

Das **10 espelhadas**, metade **já tem defeito nomeado** pelo `mapa` — o
classificador testa relógio E1 e bifurcação **antes** de cair em
`classe_parada`:

| defeito medido | curvas |
|---|---:|
| **relógio E1** (P-9) | **5** |
| cai em `classe parada` | **5** |

⇒ remover a classe orfanaria **5**, não 10. E a opção mínima da P-7 (tirar só
`LU_2024` e `SUN_2025_CRIMP`) orfanaria **2**, porque as duas do LU já são P-9.

## Segundo, e é o que resolve: **nenhuma das 5 é órfã de verdade**

| curva | medido | classe |
|---|---|---|
| `chu2026ti_D0p5mm_F0_49kN_test3` | relógio **0,220** ✅ · emb+creep **0,760** | **quase-P-9** — falta **4 pp** no limiar de 0,80 |
| `sun…grease_crimp` | rotacional **66,5 %** · viés terminal **−0,008** | **quase-P-13** — falta **3,5 pp** no limiar de 70 % |
| `sun…grease_standard` | rotacional **68,8 %** · resíduo **troca de sinal** (48 % entre terços) | **quase-P-13 + curvatura** |
| `liu2025_M16_amp0p8` | resíduo troca de sinal, **63 %** entre terços | **curvatura** (classe do `sigma_res_decomposicao_por_estagio.md`) |
| `liu2025_M16_amp0p25` | emb+creep **1,000** · o **dado** nunca cai a 90 % | Estágio I sobre-perde onde o dado quase não move |

**Três das cinco erram o limiar por 1,2 a 4 pontos percentuais.** As outras duas
caem em classes já estabelecidas — curvatura (identificada em 2026-07-29, 63 %
das 84 curvas onde o σ manda) e sobre-perda de Estágio I.

⇒ **executar a P-7 não cria curva sem explicação.** O custo que ela não tinha
escrito é menor que o benefício, e agora está medido.

## ⚠️ O que isto revela sobre os classificadores — vale além da P-7

**Limiar rígido fabrica órfã.** O `classe_parada`, atribuído **por fonte**,
vinha absorvendo em silêncio os quase-acertos dos outros classificadores: uma
curva a 66,5 % de canal rotacional (limiar 70 %) não aparecia como *"quase
bifurcação"* — aparecia como *"classe parada"*, com remédio falsificado.

⇒ o *"zero curvas sem explicação"* do `mapa` era **em parte artefato**: parte da
explicação vinha de um balde cujo critério 43 % da própria população contradiz.

**E há um buraco no teste do relógio.** A `liu2025_M16_amp0p25` escapa porque **o
dado** nunca cai a 90 % ⇒ `nd = None` ⇒ razão `n/a` ⇒ a curva não é testada. Ela
não *passa* no teste; o teste **não roda**. É a mesma classe de defeito que o
`INCONCLUSIVO` do charter existe para evitar, agora num classificador em vez de
num prereg. Um limiar adaptativo (o nível que o dado de fato alcança, em vez de
90 % fixo) fecharia o buraco — **não executado**, é mudança de instrumento.

## ⚡ FECHADO em 2026-08-07 (noite): o corte de 70 % é **arbitrário** ⇒ as órfãs são artefato

`limiar_rotacional_sonda.py`. Publiquei acima que *"limiar rígido fabrica
órfã"*, mas não tinha testado se o **70 %** da bifurcação é degrau natural ou
corte de conveniência. Medida a distribuição da fatia rotacional nas 65 fora:

| faixa | curvas |
|---|---:|
| 0,95–1,00 | 5 |
| 0,80–0,95 | 9 |
| **0,70–0,80** | **4** |
| **0,60–0,70** | **6** |
| 0,10–0,60 | 9 |
| **< 0,10** | **32** |

**Vizinhança imediata do corte:**

| fatia | curva | veredito |
|---:|---|---|
| 0,725 | `eccles2010_fig8b` | **dentro (P-13)** |
| 0,721 | `rousseau_steel_t10_amp0p2` | **dentro** |
| 0,715 | `rousseau_hdpe_t10` | **dentro** |
| 0,700 | `eccles2010_fig8a` | fora |
| 0,688 | `sun…grease_standard` | fora |
| 0,665 | `sun…grease_crimp` | fora |

**1,5 ponto percentual separa "P-13" de "órfã".** Na faixa decisiva (0,55–0,85)
há **13** curvas e a maior lacuna é **0,078** — distribuição **contínua**, sem
degrau. Um corte em 0,65 ou 0,75 moveria 4–6 curvas de lado sem que nada
mecânico mudasse.

⇒ **as 2 órfãs que a opção mínima da P-7 criaria (as duas `SUN`, a 0,665 e
0,688) são artefato do corte, não curvas sem diagnóstico.** Elas são
mecanicamente indistinguíveis das que estão dentro. Isso **remove o último custo
declarado** da opção 1.

⚠️ **E há estrutura real no dado — só que noutro lugar.** A bimodalidade está em
**~0,10**, não em 0,70: **32 das 65** têm o canal rotacional essencialmente
**desligado** (< 10 %) contra 33 com ele ativo. Se algum limiar merece ser
tratado como físico neste eixo, é esse — e ele não é o que o classificador usa.

## ✅ P-7 ASSINADA e EXECUTADA em 2026-08-08 — opção mínima (gates 4/4)

> O professor assinou (*"assine a P-7 e a P-15, e execute"*) e a **opção
> mínima** foi executada: `LU_2024` e `SUN_2025_CRIMP` saíram de
> `_FONTES_CLASSE_PARADA`. Censo intacto (139), fila form-limited **0 → 2**
> (as duas corridas longas do LU), categoria "dado" 1 → 3.
> Resultado em `p7_execucao_resultado.md`.

## ~~O que fica na sua mesa~~ — texto ORIGINAL da proposta (registro, 2026-08-07)

> ⚠️ **Vencido pela execução acima.** A opção 1 foi a escolhida e está feita; os
> números desta tabela são os de 07-08 (a fila era 1 e virou 0 no D-Z, e a
> execução a levou a **2**). Preservado porque registro datado não se reescreve.

A P-7 mantinha as três opções, com o custo medido:

| opção | fila | órfãs criadas | comentário |
|---|---:|---:|---|
| **1 · mínima** (tirar LU + SUN) | 1 → 5 | **2**, ambas **quase-P-13** | as 2 do LU já são P-9 |
| **2 · por curva** | 1 → 11 | **5**, todas com classe nomeada acima | mais honesta; obriga re-derivar o critério (c) |
| **3 · nada** | 1 | 0 | exige publicar que 43 % do balde contradiz o critério |

⚠️ **Não decido por você**, e o motivo é de charter: reclassificar camada de
triagem é estatuto, e as três assinaturas anteriores desse tipo (P-10, P-11,
P-12) foram suas. O que faltava era o número; ele está aí.

## Reprodutibilidade

```bash
py -3.12 New_Theory/classe_parada_discriminante.py    # as 10 espelhadas
```

O cruzamento com o `mapa_das_65_fora.json`, os valores de limiar e o teste de
troca de sinal (média do resíduo por terço + variância entre terços) saem do
store, em segundos.
