# A tendência que REPETE: aceleração tardia ausente (7 fontes, 21 curvas)

**2026-08-01** · item (3) da sequência autorizada ("forma só quando a
mesma tendência aparecer em duas fontes independentes"). O critério foi
satisfeito — **por sete fontes, não duas.**

## A medição

Para cada curva da fila, a razão entre a inclinação final do **dado** e a
do **modelo** (últimos 25 % dos pontos). Razão ≫ 1 = o dado desaba no fim
e o modelo achata.

| fonte | n | razão mediana |
|---|--:|---:|
| YANG_2021 | 2 | **224,7** |
| LU_2024 | 2 | **40,0** |
| SUN_2025_CRIMP | 1 | **25,1** |
| YANG_2019 | 4 | **15,6** |
| JCSR_2023 | 2 | **4,2** |
| LIU_2025 | 4 | **2,5** |
| CHU_2026 | 6 | **2,1** |
| CACCESE_2009 | 2 | 1,1 |
| ROUSSEAU_2025 | 6 | 0,9 |
| LIU_2022_RETIGHT | 1 | 0,8 |
| LI_2022_TRIBOINT | 1 | 0,2 |

**21 das 32 curvas da fila** estão em fontes com razão > 2. Nas quatro
piores, o modelo é **15× a 225× lento demais no fim**.

## Por que isto é diferente das tendências que recusei hoje

Espessura (Rousseau), frequência (Li 2022) e índice de reaperto
(Liu 2022) apareceram **cada uma em UMA fonte** ⇒ recusei abrir forma.
Esta aparece em **sete fontes independentes**, com rigs, materiais,
tamanhos de parafuso e modos de carregamento diferentes. É o padrão que o
critério do dia autoriza a atacar.

E ela **conversa com o que já estava medido e arquivado**:

- §4.43+ (2026-07-29): 59,7 % da variância do σ_res está **ENTRE**
  estágios e 63 % dos resíduos **trocam de sinal** ⇒ "o defeito é
  curvatura, não taxa".
- 2026-07-30 (`cm_d2linha_resultado.md`): o cluster liu2016/zhang18/
  li2022ti tem o excesso de σ **inteiro além de 200 k ciclos** ⇒ "deriva
  TARDIA (estágio III), não assentamento".
- Hoje: o dado do YANG_2019 sai de −0,002 para **−1,27** por kciclo
  enquanto o modelo vai de 0 a −0,03.

Três instrumentos independentes (decomposição de variância, janela de
truncamento, inclinação terminal) apontando o **mesmo estágio**.

## O que a forma teria de fazer — e o que já existe

O modelo tem `crash_trigger_frac` (gatilho de criticalidade: suprime o
afrouxamento enquanto F₀ está alto e **dispara runaway** quando
F₀/F₀_init cruza um limiar) — **default 0 = inerte**, e é exatamente a
forma de "joelho tardio". Ela foi construída em §4.30/L14 e nunca foi
adotada em nenhuma fonte.

⇒ **O próximo passo não é inventar forma: é testar a que já existe,
com prereg, contra a classe de 7 fontes.** Se `crash_trigger_frac` fecha
curvas em ≥2 fontes independentes sem piorar nenhuma, é adoção por
classe — o primeiro candidato do dia que não morre no nascimento.

## Ressalva honesta

Razão de inclinação terminal é sensível a poucos pontos e a curvas com
fratura (out-of-model) inflam o numerador — LU_2024 e YANG_2021 têm
cauda de fratura conhecida. Por isso o critério de classe **não** é a
razão sozinha: são as **7 fontes** somadas aos **3 instrumentos
independentes** acima. Um prereg sério deve excluir as curvas com
fratura declarada antes de medir ganho.
