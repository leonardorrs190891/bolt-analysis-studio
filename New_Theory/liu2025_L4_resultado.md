# L4 — gate cross-size do Liu 2025: **FALHA (0 de 5)**. E três correções que ele produziu.

**Data:** 2026-07-28 · **Gate congelado em `223187d`** (escrito no estudo de modelagem
**antes** de a Fig. 4 estar digitalizada — a cegueira era real)
**Critério congelado:** *"o mesmo `(C1, m1)` prevê as vidas M10 dentro de ±25 %"*

---

## 0. Veredicto

**L4: 0 de 5 dentro de ±25 %.** Erros de **−82 % a +249 %**.

Mas o gate produziu três achados que valem mais que o veredicto, **dois deles corrigindo
o estudo que escrevi uma hora antes**.

---

## 1. A Fig. 4 não é o que o estudo supôs — correção nº 1

O estudo de modelagem (§8, gate L4) assumiu que a Fig. 4 traz as **vidas de fratura** por
tamanho. **Não traz.** O artigo declara, na seção *Test results*:

> *"…convert the D–N curve of the loose state **when the clamping force was reduced to 95 %
> of the initial pre-tightening force** into the Su–N curve…"*

⇒ **Fig. 4 é `N` até `F/F₀ = 0,95`**, não até a fratura. Prova geométrica independente: o
eixo x da figura vai de 1 a 10⁵, e as vidas de fratura do M16 (1,4×10⁴ a 3,3×10⁵) **não
caberiam nele**.

**Consequência sobre o estudo:** a §4.1 dele fitou as tensões da Table 2 contra as vidas de
**fratura** e obteve `m = 3,012`, `R²(log) = 0,9894`, anunciando *"com a tensão do artigo a
vida é previsível a ±17 %"*. **Aquele pareamento é inválido** — tensões do critério 95 %
contra vidas de fratura. Com o pareamento correto (Table 2 × Fig. 4):

> **M16: `m = 5,94`, `R²(log) = 0,8484`** — ajuste ruim, e a curva é claramente **curvada**
> (o próprio artigo diz que a Su–N é **bilinear**).

O `R² = 0,9894` de antes era coincidência de duas grandezas que crescem ambas com a
amplitude.

## 2. A digitalização está validada — e pela lição da linha de métrica

`New_Theory/liu2025_fig4_digitize.py`. Dois erros meus na 1ª passada, ambos instrutivos:

**(a) O eixo Y é logarítmico, não linear.** Os ticks de 1,2 / 0,8 / 0,4 estão em
y = 24 / 183 / 454 px — espaçamento **desigual** (159 e 271 px), impossível num eixo linear
com passos iguais. Sob `y = A + B·log₁₀(δ)`, os dois intervalos dão `B` = −903,0 e −900,2
(**concordância 0,3 %**). Corrigido, as amplitudes saem exatas: M16 em
**0,800 / 0,601 / 0,500 / 0,398 / 0,301 / 0,251** — as seis da Fig. 3.

**(b) Validar em `N` era mal-posto.** Comparar o `N` da Fig. 4 com o `N` em que **nossas**
curvas cruzam 0,95 deu razões de **0,26 a 4,55** (desvio 89 %) — e me fez julgar a
digitalização reprovada. Mas o cruzamento de 0,95 cai no **platô**, onde a curva é quase
horizontal: um erro de 0,01 em `r` move `N` por um fator. Invertendo para o eixo bem-posto
— *em que nível `r` nossas curvas estão no ciclo que a Fig. 4 aponta?*:

| δ (mm) | 0,25 | 0,30 | 0,40 | 0,50 | 0,60 | 0,80 |
|---|---:|---:|---:|---:|---:|---:|
| `r` nosso no `N` da Fig. 4 | 0,9558 | 0,9527 | 0,9361 | 0,9363 | 0,9378 | 0,9898 |

**Média 0,9514, desvio 2,0 %.** A digitalização **bate com o critério de 95 % do artigo a
2 %** — dentro do erro de leitura declarado (±0,02 em F/F₀).

> É a mesma lição que as quatro tentativas de métrica produziram, agora mordendo a
> **digitalização**: no platô compara-se **vertical**; no colapso, em **vida**. Eu usei o
> eixo errado e quase descartei um dado bom.

## 3. Por que o L4 falha — e o que sobrevive dele

**Concordância cross-size direta, na mesma tensão de raiz:**

| σ_raiz (MPa) | N (M10) | N (M16, interp) | razão |
|---:|---:|---:|---:|
| 398 | 10 566 | 10 402 | **1,02** |
| 518 | 6 918 | 3 767 | **1,84** |
| 783 | 206 | 46 | **4,51** |

**A normalização do artigo é REAL — mas só no ramo de alto ciclo.** Em σ ≈ 400 MPa as duas
curvas coincidem a **2 %**, o que é notável para rigs de tamanhos diferentes. A partir daí
ela degrada monotonicamente, até **4,5×** em σ ≈ 780 MPa.

Isso é **consistente com o próprio artigo**, que descreve a Su–N como **bilinear com
fronteira alto/baixo ciclo** — a discordância aparece justamente ao cruzar a fronteira.
As inclinações confirmam: **M16 `m` = 5,94 · M10 `m` = 8,07**, e é essa diferença de
inclinação que produz o erro sistemático do L4 (−82 % no ramo baixo, +249 % no alto).

**Portanto:** o L4 falhou porque testou **uma lei de potência única** contra dados que o
próprio artigo declara **bilineares**. O gate estava mal-especificado — **quinto defeito de
autoria de gate**. Mas ele **não é resgatável por reescrita**: mesmo o melhor `(C,m)` único
não cabe em ±25 % quando as inclinações dos dois ramos diferem por 36 %.

## 4. Correção nº 3 — o `fat_m1 = 2,7` ADOTADO não tem a procedência que declara

`LI_2022_TRIBOINT` roda com `fatigue_enabled=True, fat_m1=2.7, fat_C1=2.977e29`, com
procedência registrada *"inclinação D–N Liu2025, PR-24"*.

**Busca no texto integral do artigo: "2.7" não ocorre nenhuma vez.** O artigo não declara
esse expoente. Os expoentes que o dado do artigo de fato sustenta são:

| grandeza | expoente medido |
|---|---:|
| D–N sobre vidas de **fratura** (nossas curvas da Fig. 3) | **2,88–2,94** |
| D–N sobre `N₉₅` (Fig. 4, M16) | **5,82** |
| Su–N sobre `N₉₅` (Table 2 × Fig. 4, M16) | **5,94** |
| Su–N sobre `N₉₅` (M10) | **8,07** |

⚠️ *Ressalva de método:* a extração de texto do PDF não captura números que estejam dentro
de figuras. O que se pode afirmar é que **2,7 não aparece no corpo do texto** e que o valor
**não é rastreável a uma declaração do artigo**. O rótulo de procedência precisa ser
re-checado no PR-24 antes de continuar sendo citado.

**Isto não muda nenhum número de trajetória hoje** (o `fat_m1` do `LI_2022_TRIBOINT` está
calibrado com o `fat_C1` que o acompanha), mas é exatamente a classe de defeito que a
§4.43 existe para pegar: uma constante adotada com procedência que não se sustenta na
fonte citada.

## 5. O que fica

**Não adotar nada.** O L4 falhou, e a rota "constante que transfere entre rigs" — que era o
prêmio do estudo — **está falsificada na forma testada**: a normalização vale a 2 % no alto
ciclo e erra por 4,5× no baixo.

**O que sobrevive, e é útil:**
1. **A Fig. 4 está digitalizada e validada** (`liu2025_fig4_DN.json`): 6 pontos M16 + 5 M10,
   amplitudes exatas, critério confirmado a 2 %. É dado novo na biblioteca.
2. **A normalização cross-size é real no alto ciclo** (razão 1,02 em σ ≈ 400 MPa). Se algum
   dia formos usar a Su–N, é **só no ramo de alto ciclo** que ela transfere.
3. **Três correções de registro** (Fig. 4 ≠ fratura · eixo Y log · `fat_m1=2,7` sem
   procedência) que só apareceram porque o gate foi rodado.

**O que eu recomendaria a seguir — e não farei sem sua palavra:** testar a **Su–N bilinear**
(que é o que o artigo de fato propõe e o que nosso `sun_life` já implementa), com a
fronteira alto/baixo ciclo ajustada nos dados de M16 e testada em M10. Isso exige
**pré-registro novo** — o L4 morreu como escrito, e reescrevê-lo agora, sabendo o resultado,
seria mover a trave.

---

## 6. Reprodutibilidade

```bash
py -3.12 New_Theory/liu2025_fig4_digitize.py     # digitaliza + valida (2 s)
```
Figura extraída do PDF com `pypdf` (`page.images`), página 5, `p05_Im0.jpg`.
Dados: `New_Theory/liu2025_fig4_DN.json`.
