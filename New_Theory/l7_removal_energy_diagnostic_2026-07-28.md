# Diagnóstico L7 — a energia específica de remoção, medida e reenquadrada

**Data:** 2026-07-28 · **Store:** `4f5bedfbace4` (snapshot do HEAD, não o arquivo em
disco — outra sessão está reescrevendo o store para acrescentar campos da métrica
de banda) · **Sem fit, sem alteração de engine, sem escrita em store ou config.**

Atende o item 2 de "o que ficou aberto" do
[relatório executivo](../docs/MANUAL_BAS_V2/00-relatorio-executivo.md) e o item 6
do roadmap do `CLAUDE.md`. O check L7 (`EnergyBudget.removal_energy_check`,
informacional, prereg F1) compara a energia específica de remoção implicada pelo
canal de desgaste com a banda **1 800 – 10 500 J/mm³** (Shipway 2021,
proveniência *derivada*, taxa-dependente). Ele **nunca bloqueia** e **nunca é
fitável**.

---

## 1. O que o store diz

| | |
|---|---:|
| registros com `l7_check` | 203 |
| sem energia implicada (desgaste ≈ 0) | 93 |
| **com valor** | **110** |
| dentro da banda | 46 |
| **acima do teto** (>10 500) | **60** — mediana **6,6e4** (≈6× o teto) |
| **abaixo do piso** (<1 800) | **4** |
| pior caso | **1,269e6** J/mm³ (`yang2019_M10_amp0p4_5Hz`) ≈ 120× o teto |

Os **quatro** casos abaixo do piso são **todos Karlsen**, os maiores parafusos da
biblioteca:

| caso | implied |
|---|---:|
| `karlsen2022_M42_HV_run21p0` | 951 |
| `karlsen2022_M42_HV_run20p0` | 1 018 |
| `karlsen2022_M30_HV_run1p2` | 1 656 |
| `karlsen2022_M30_HV_run6p2` | 1 662 |

E a distribuição por fonte é quase pura — cada fonte fica inteira de um lado:

| fonte | acima | abaixo | dentro |
|---|--:|--:|--:|
| liu2022 | **21** | 0 | 0 |
| demir2024 | 8 | 0 | 0 |
| eccles2010 | 8 | 0 | 2 |
| liu2025 | 5 | 0 | 0 |
| yang2019 | 5 | 0 | 0 |
| sun2025efa110030 | 5 | 0 | 0 |
| li2022ti | 4 | 0 | 0 |
| âncora interna | 3 | 0 | 0 |
| karlsen2022 | 0 | **4** | 3 |
| sun2025efa109235 | 1 | 0 | 3 |

---

## 2. O reenquadramento — é ~um número por bancada, não 64 casos

Esta é a medição que muda o tamanho do problema:

| | valor |
|---|---:|
| **η² da FONTE sobre `log10(implied)`** | **0,910** |
| dispersão mediana **dentro** da fonte | **0,08 década** (≈20 %) |
| fontes com dispersão interna exatamente **0,00** | âncora interna, li2022ti, lu2024, e outras |
| maior dispersão interna | 0,58 década (sun2025efa109235) |

**91 % da variância é "qual bancada".** Dentro de uma bancada o valor quase não
se move — nem entre amplitudes, nem entre frequências, nem entre curvas. Ou seja:
a energia implicada é **propriedade fixa da configuração do rig**, não da condição
de carregamento.

Consequência prática: os **60 casos** acima do teto são, na verdade, **~9
configurações de rig** energeticamente implausíveis. O item 6 do roadmap deixa de
ser "64 curvas erradas" e passa a ser "9 configurações a explicar" — um problema
uma ordem de grandeza menor.

---

## 3. O conserto barato está REFUTADO

A hipótese óbvia — *"o `k_wear_spec` está pequeno demais; suba e o implied cai"* —
não sobrevive à medição. Em 105 casos com `k_wear_spec` numérico > 0:

| teste | valor | o que a física pura preveria |
|---|---:|---|
| Pearson de `log10(implied)` vs `log10(k_wear_spec)` | **−0,405** | −1,0 |
| **Spearman (rank)** | **−0,089** | −1,0 |
| inclinação do ajuste log-log | **−0,538** | −1,0 |

Se o implied fosse governado pela constante (`V ∝ k_wear_spec·W` ⇒
`implied = W/V ∝ 1/k_wear_spec`), o rank-ordenamento seria quase perfeito. O
Spearman ≈ **−0,09** diz que **`k_wear_spec` não ordena o implied**. O sinal está
certo e a magnitude não: há mais coisa no denominador (carga, amplitude de slip,
as comportas) do que a constante.

**Duas razões independentes para não subir a constante globalmente:**

1. **Não resolveria** — a constante não ranqueia o efeito (acima).
2. **Quebraria o outro lado** — Karlsen já está **abaixo** do piso. Subir o
   `k_wear_spec` remove mais volume por unidade de trabalho, o que **baixa** o
   implied e afunda os 4 casos de Karlsen mais fundo ainda.

Ou seja: a violação tem **dois sentidos**, e nenhuma constante única serve para
os dois. É a assinatura da **L6** (`k_wear_spec = K/H` é **por par tribológico**),
agora com número.

*Nota de honestidade sobre este parágrafo:* a primeira leitura desta análise
afirmou "correlação decisiva" a partir das **medianas por fonte**, que de fato
formam uma escada convincente (liu2022 3e-15 → 7,8e4; âncora interna 7,5e-15 → 2,0e4;
Karlsen no canônico 5e-14 → 1 662). A escada existe, mas **não** sobrevive ao
rank-ordenamento caso-a-caso. Medianas por grupo com poucos valores distintos
enganam; o Spearman foi o que desfez o engano.

---

## 4. A tensão que isto expõe entre dois gates

Três valores de `k_wear_spec`, três origens, ~**2 000×** de distância entre as
pontas:

| valor | origem | classe |
|---|---|---|
| ~**3e-15** | fits per-rig das campanhas (liu2022, demir2024, eccles2010, sun2025) | fitado |
| **5e-14** | bloco `shared` canônico (par da âncora interna) | fitado |
| **4e-15 – 2e-14** | banda **MEDIDA** R5 `thread\|35CrMo-SCM435` (Zhang 2019) | medido |
| **6,49e-12 – 7e-12** | banda **MEDIDA** R5 `faying\|Q355B-Q235B` (Li 2025) | medido |

> **CORRIGIDO em 2026-07-28 pela matriz de procedência**
> ([`provenance_matrix.md`](provenance_matrix.md) §3). Este parágrafo dizia
> *"única banda MEDIDA R5"* e *"o canônico está ~130× abaixo da banda medida"*.
> As duas coisas estavam erradas:
>
> 1. **A R5 tem 3 bandas, não 1** — e a terceira (`fretting|52100-52100`,
>    Warmuth 2015) está em **`norm-own`**, não em `1/Pa`: compará-la ao canônico
>    é **erro de unidade** (daria "×6e8", número sem significado).
> 2. **A banda mais próxima é a `thread`, não a `faying`** — e o canônico está
>    **2,5× ACIMA do teto** dela, não abaixo do piso. A direção do argumento
>    **inverte** conforme a interface.
>
> **E o que sobra é mais forte que o erro:** as duas bandas comparáveis distam
> ~**325×** entre si e **cercam o canônico pelos dois lados**. O engine usa
> `k_wear_spec` no `WearLoss` (apoio) **e** no `ThreadFrettingLoss` (rosca), logo
> **nenhum valor único pode estar dentro das duas**. O item deixa de ser
> "re-ancorar o valor" e passa a ser **separar a constante por interface** —
> `k_wear_spec_faying` / `k_wear_spec_thread`, cada um com a sua banda.

**O que puxa cada lado — e a correção acima muda isto.** O tripé (ajuste da curva
de pré-carga) empurra `k_wear_spec` para **baixo**; a banda L7 e a banda R5
**`faying`** empurram para **cima**; mas a banda R5 **`thread`** empurra para
**baixo** (o canônico já está 2,5× acima do teto dela). Não são "dois lados": são
**três forças, e duas delas apontam para baixo**. Hoje o tripé ganha, porque ele é
gate e o L7 é informacional — escolha declarada, não descuido. O que a correção
acrescenta é que **mover o valor não resolve em nenhuma direção**: subir viola a
banda de rosca, descer piora o custo por volume. É a separação por interface que
resolve, e é por isso que este item mudou de classe.

---

## 5. O que testaria isto de verdade (não executado)

Um prereg honesto precisa de alvo declarado **antes**, e o alvo aqui não pode ser
o MAE — seria fitar de novo. Sugestão:

1. **Alvo:** para uma bancada com par tribológico conhecido (candidato natural:
   as fontes de aço estrutural, onde a banda R5 `faying|Q355B-Q235B` se aplica),
   fixar `k_wear_spec` **na banda medida** e declarar antes que o implied deve
   cair dentro de 1 800–10 500.
2. **Predição falsificável:** se a forma estiver certa e só a constante estiver
   errada, o implied entra na banda **e** o MAE daquela fonte piora de forma
   *previsível* (o desgaste passa a remover mais). Se o MAE piorar de forma que
   nenhuma outra constante com procedência recupere, a **forma** do canal de
   desgaste é o problema — que é a conclusão que o item 6 propõe e que ninguém
   mediu ainda.
3. **Controle obrigatório:** rodar o mesmo passo em Karlsen, que está do lado
   oposto. Uma mudança que conserte os 60 e afunde os 4 confirma "por par"; uma
   que conserte os dois lados falsificaria "por par" e apontaria para forma.

---

## 6. Caveats

- A banda 1 800–10 500 J/mm³ tem proveniência **derivada** e é
  **taxa-dependente** (Shipway 2021). Ela não é um limite duro de física; é a
  faixa em que medições de desgaste abrasivo/adesivo caem. Um caso fora dela é
  **suspeito**, não provado errado.
- Os **93 casos sem valor** (desgaste ≈ 0) não são aprovações: o check
  simplesmente não tem denominador. Onde o desgaste é inerte, o L7 é silencioso.
- Este documento **não** altera nenhuma trajetória: nenhum store, config, engine
  ou gate foi tocado. Os números saem do snapshot `4f5bedfbace4` do HEAD.
