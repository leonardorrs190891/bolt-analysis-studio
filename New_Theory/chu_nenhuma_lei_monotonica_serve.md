# `CHU_2026`: **nenhuma lei de potência única em δ pode servir** — o expoente exigido salta ~5 unidades dentro da fonte

> **Título revisado na mesma sessão.** A 1ª versão dizia *"nenhuma lei monotônica"*, e
> isso era forte demais: parte da inversão cabe no scatter de instalação que os autores
> declaram (~25 %). O argumento robusto é o **salto de expoente**, com margem de mais de
> uma ordem de grandeza sobre o scatter. Ver a errata no §1.

**2026-08-14 (tarde)** · só-leitura · **nada adotado** · store `c37618c5cc96`, censo **141/205** ·
sequela de `lei_relogio_implementada_e_nao_adotada.md` (commit `ba18a72`).

---

## 0. O erro de método que este documento existe para registrar

Passei a tarde falsificando, um a um, candidatos de **lei de amplitude** para esta fonte:
o relógio de assentamento `N_emb ∝ 1/δ`, a potência no alvo `emb_depth(δ)`, a severidade
de wear `k ∝ δ`. Três falsificações honestas, com predição registrada antes de medir.

**Todas as três eram membros de uma classe que a Tabela 1 do próprio artigo já
condenava inteira** — e eu tinha lido essa tabela na mesma sessão, procurando a coluna
`Ra` e parando antes da coluna de ciclos.

> **A regra do charter — *LEIA A PROVA GRAVADA antes de escolher o teste* — não é sobre
> ler o documento. É sobre ler a coluna que decide.**

---

## 1. A prova: a Tabela 1 é NÃO-MONOTÔNICA em δ

Ciclos até `F = 0,9·F₀`, valores **impressos** (F₀ = 49 kN, Ra 0,4 µm, 10 Hz):

| Test | δ (mm) | N até 0,9·F₀ | leitura |
|---|---:|---:|---|
| 1 | 0,3 | **sem queda** (2500 ciclos) | não afrouxa |
| 2 | 0,4 | **278** | |
| 3 | 0,5 | **325** | ⬆ **mais lento** que 0,4 |
| 4 | 0,7 | **406** | ⬆ **mais lento** ainda |
| 5 | 1,0 | **72** | ⬇ colapso |
| 6 | 1,0 | 54 | (réplica; scatter de instalação ~25 %) |

A junta afrouxa **mais rápido a 0,4 mm do que a 0,5 e a 0,7 mm**. A resistência **cresce**
de δ=0,4 a δ=0,7 e só então despenca em δ=1,0.

### ⚠️ ERRATA da 1ª versão deste documento (mesma sessão, ao ler mais uma página)

A 1ª versão apoiava a conclusão na **não-monotonicidade** pura. Isso é **fraco demais**, e
a página de texto do artigo (extraída em `paper_figures/chu_2026__fig3.png`) diz por quê:

* a **prosa dos autores afirma o oposto** — *"a clear trend emerges: larger transverse
  displacements lead to greater preload fluctuation per cycle and faster loosening"*;
* e eles declaram **~25 % de scatter de instalação**, demonstrado pelo próprio par de
  réplicas `test5`/`test6` (72 vs 54 ciclos).

Os desvios 278→325 (**+17 %**) e 325→406 (**+25 %**) **cabem dentro desse scatter**. ⇒ a
inversão em si **não é conclusiva**, e eu a tratei como se fosse.

### O argumento que SOBREVIVE, e é muito mais forte: o expoente muda ~5 ordens

| trecho | razão de δ | razão de N | expoente implícito |
|---|---:|---:|---:|
| 0,4 → 0,7 | 1,75 | 1,46 (**sobe**) | **≈ −1,1** |
| 0,7 → 1,0 | 1,43 | 0,177 (**5,6× mais rápido**) | **≈ +4,9** |

O trecho 0,7→1,0 é um fator **5,6×** — contra 1,25× de scatter declarado. **Real, não
ruído.** E uma potência única ancorada nele prevê `N(0,4) ≈ 6 300` contra **278**
medidos: erro de **23×**.

⇒ **Nenhuma lei de potência única em δ ordena esta fonte**, e a margem contra o scatter é
de mais de uma ordem de grandeza. Não é questão de escolher o expoente certo ou o canal
certo. Isso explica *retroativamente* as três falsificações da tarde e a do item B: os
candidatos não fracassaram por azar de parametrização.

⚠️ Nota de consistência que **fortalece** a leitura: os expoentes exigidos medidos pelo
lado do modelo (via `emb_depth`: **0,19** de δ=0,3→0,5 contra **≥3,6** de 0,5→1,0) e os
lidos do dado (**−1,1** contra **+4,9**) são medições **independentes** — uma no engine,
outra na Tabela 1 — e ambas dizem a mesma coisa: **o expoente salta ~5 unidades dentro
da fonte.**

## ⚠️ E isto tem nome: o pico de fretting fica na TRANSIÇÃO, não no maior slip

O comportamento é a assinatura clássica do mapa de fretting (Vingsbo & Söderberg): a
**taxa de desgaste por ciclo tem máximo no regime misto stick–slip**, perto da transição
para gross slip, e **cai** quando o contato entra em gross slip franco. Amplitude maior
não é monotonicamente pior.

⚠️ **O modelo não vê isso**: instrumentando `resolve_transverse_slip`, as curvas de
δ = 0,4 a 1,0 são **todas GROSS** com `slip/δ` = 0,993–0,998 — praticamente constante. O
engine coloca as cinco no mesmo regime; o dado diz que 0,4 está perto da transição e 1,0
está muito além dela.

---

## 2. Onde a transição REALMENTE está — medido

Instrumentando o driver (não inferindo da decomposição — erro catalogado 3× em
`censo_stick_abertas_resultado.md`):

| curva | δ | `slip/δ` médio | classe |
|---|---:|---:|---|
| `test1` | 0,3 | **0,0008** | **STICK** |
| `test2` · `test7` · `test8` | 0,4 | 0,993–0,995 | GROSS |
| `test3` · `test9` | 0,5 | 0,996–0,997 | GROSS |
| `test4` | 0,7 | 0,998 | GROSS |
| `test5` · `test6` | 1,0 | 0,998 | GROSS |

**A transição stick→gross do MODELO cai entre δ=0,3 e 0,4**, e é **robusta à config**: a
`test1` continua travada ao neutralizar as três constantes da config própria dela
(`loose_arrest_floor`→0, `mu_bearing`→default, `c_bend`→1) — na verdade fica **mais**
travada (`slip/δ` 0,0008 → 0,0000). ⇒ o travamento é por **amplitude**, não por ajuste.

✅ Isto **falsifica a hipótese de transição de regime** como explicação do salto de
`emb_depth`: o salto acontece entre δ=0,5 e 1,0, **inteiramente dentro do gross slip**.

⚠️ **O meu script imprimiu o veredito CONTRÁRIO e eu não o aceitei.** A regra que
escrevi era *diferença de conjuntos* ("as classes dos dois lados diferem?"), e a `test1`
sozinha fazia o conjunto diferir. A pergunta certa é **onde a fronteira cai**. As duas
regras divergem exatamente quando entra um outlier com causa própria — e só deu para
pegar porque os números crus estavam impressos ao lado do veredito.

---

## 3. Item B quantificado: corrigir a rugosidade custa **−2 curvas**

O artigo dá **Ra 0,4 µm** nos Tests 1–8 (fino, classe `Rz<4` ⇒ ~1,6 µm) e **Ra 1,6 µm**
só no Test 9. As **nove** rodam com `emb_um = 11,0` (classe `Rz10-40`) — 7× grosso demais.

Com o valor de tabela (1,6 µm) em todas as Ra 0,4:

| curva | δ | store | com `emb` de tabela |
|---|---:|---|---|
| `test3` | 0,5 | 0,1381/0,1741/0,0369 | **0,0657/0,0984/0,0290** ⬆ muito melhor |
| `test4` | 0,7 | 0,1043/0,2708/0,1255 | 0,1438/0,2419/0,1251 ⬇ |
| `test2` | 0,4 | 0,1543/0,4639/0,1897 | 0,1602/0,5418/0,1914 ⬇ |
| `test5` | 1,0 | 0,0208/0,0395/0,0183 ✅ | 0,0943/0,1728/0,0584 ❌ **sai** |
| `test6` | 1,0 | 0,0279/0,0422/0,0122 ✅ | 0,0678/0,1268/0,0389 ❌ **sai** |

**1 de 8 passa** (contra 3 hoje). ⇒ **item B, opção (a) = −2 curvas**, medido. A célula
de custo dele deixa de ser "VENCIDA" e passa a ter número.

⚠️ E a razão de o item B ter sido lido como *"falsificado"* antes: ele só havia sido
julgado na `test5`. Na `test3` a rugosidade correta é **claramente certa** — o valor que
a curva pede **é o de tabela para o acabamento declarado**, o que é procedência, não fit.

---

## 4. A lei de severidade `k_wear_spec ∝ δ` — a mais forte das três, e ainda assim morta

Em gross slip a 0,998 o **deslizamento já é máximo**; o que pode crescer é a **perda por
unidade de slip**. E expressa nesse canal a dependência exigida é muito mais suave:
**2× para 2× de δ** (expoente 1), contra 15× via `emb_depth`.

O ponto de ancoragem **não foi escolhido**: a `test3` (δ=0,5) já roda no `5e-14` do bloco
`shared`, que é exatamente `1e-13 × 0,5`. Predição zero-refit `k(δ) = 1e-13·δ[mm]`:

| curva | δ | k(δ) | com `emb` tabela + k(δ) | |
|---|---:|---:|---|---|
| `test5` | 1,0 | 1,0e-13 | **0,0130/0,0278/0,0084** | ✅ **fecha** |
| `test6` | 1,0 | 1,0e-13 | 0,0621/0,0879/0,0252 | melhora |
| `test4` | 0,7 | 7,0e-14 | 0,0831/0,2513/0,1026 | melhora |
| `test3` | 0,5 | 5,0e-14 | **idêntica** | (confirma a âncora) |
| `test2`·`7`·`8` | 0,4 | 4,0e-14 | pioram nas 3 | ❌ |

**3 de 3 melhoram acima de δ=0,5; as 3 de δ=0,4 pioram** — e pioram porque a lei manda
*reduzir* o wear lá, enquanto elas querem **mais**. É exatamente a não-monotonicidade da
Tabela 1 aparecendo no ajuste.

Varredura do único número `C` em `k = C·δ`: o melhor é **C = 8,0e-14**, com placar
**3/9 — o mesmo de hoje** —, `test5` e `test6` passando, `test3` a **0,0279/0,1097/0,0290**
(erra **só** o res.máx, por 9,7 %), e `test2/7/8` piorando **+0,04 a +0,05 de MAE**.
⇒ **reprova o gate de não-piora; não adotável.** Mas é a melhor procedência já vista
nesta fonte: rugosidade de tabela + **um** número, contra dois números por condição.

---

## 5. ⛔ RETRATADO (2026-08-14, noite IV) — a `test3` está CERTA; o defeito era da minha medição

> **O §5 abaixo está ERRADO e fica preservado como registro.** A digitalização da `test3`
> não tem defeito: ela reproduz a Tabela 1 em **+1 %** e a ordenação contra a `test2`
> **confere com o artigo**. O item **J** nasceu deste erro e está retratado.
>
> **A causa, medida:** eu computei o round-trip a partir de `metric_x`/`metric_data` do
> store — os vetores **normalizados e trimados da métrica** —, não da CSV crua. O
> `metric_data` é dividido pelo próprio 1º valor do dado (aqui **1,0259**), então tudo
> desce ~2,6 % e o cruzamento de 0,90 chega cedo demais: **253** em vez de **327**.
>
> ⚠️ **Errata da 1ª redação desta errata** (mesma sessão): eu atribuí a normalização ao
> campo `CaseResult.align`. **Errado** — o `align` gravado neste registro vale **0,99896**
> e é o fator do **MODELO** (o `CLAUDE.md` o descreve assim: *"divide o MODELO pelo próprio
> valor no 1º ciclo do dado"*). São **dois passos distintos**, e eu nomeei o outro. Os
> números publicados estavam certos — `metric_data[0]` = **1,0000 exato** contra 1,0259 na
> CSV, razão 0,97476 constante ponto a ponto —; o **nome** é que estava trocado. Corrigir
> um mecanismo publicado importa mesmo quando a conclusão não muda: quem for reproduzir
> procura o campo errado.
> Comparei um valor **impresso cru** contra um vetor **alinhado**. O `CLAUDE.md` documenta
> exatamente isto (*"a métrica do runner NÃO compara a curva crua"*) — apliquei a
> advertência ao modelo e esqueci dela do lado do **dado**.
>
> **Round-trip refeito sobre as CSVs cruas:**
>
> | curva | paper | CSV crua | erro | (alinhado, publicado antes) |
> |---|---:|---:|---:|---:|
> | `test7` | 1050 | **1050** | **−0 %** | 1031 |
> | `test3` | 325 | **327** | **+1 %** | 253 (−22 %) |
> | `test2` | 278 | **272** | **−2 %** | 275 |
> | `test4` | 406 | **397** | **−2 %** | 387 |
> | `test8` | 936 | **915** | **−2 %** | 975 |
> | `test9` | 180 | 233 | +30 % | 188 |
> | `test5` | 72 | 48 | −33 % | 58 |
> | `test6` | 54 | 66 | +22 % | 56 |
>
> **Cinco a ±2 %.** As três discrepantes são as mais **curtas e íngremes** (N de 54 a 233):
> a curva cai de 1,0 a ~0,55 em 340 ciclos, então um erro pequeno em F desloca N muito —
> **geometria, não defeito**.
>
> **Verificação independente, por extração vetorial da própria figura:** re-extraí a `test3`
> da Fig. 2(a) por **pixel calibrado** (moldura x∈[96,955] y∈[6,569]; ticks X 258·419·580·742·904
> ⇒ 161,5 px/500 ciclos com zero em 96,5, batendo com a moldura; ticks Y 58·159·262·364·466
> ⇒ zero em 568, idem). A curva extraída e a nossa CSV concordam a **MAE 0,0034** (viés
> +0,0031, máx 0,0129) — **abaixo do piso de digitalização de 0,005**. A figura dá
> N(0,90) = **327**, idêntico à nossa CSV.
>
> ⚠️ **Detalhe de método que quase me enganou:** a 1ª máscara de azul dava N90 = 327 **antes**
> de as checagens passarem (`F_fim` = 1,0157 onde o visual é 0,41 — contaminação da violeta
> `Test1`). O número que eu esperava apareceu antes da validação. Só com `r<120` o traço
> passou a terminar em N=2008 e F=0,4088, e **o 327 se manteve nas três máscaras**.
>
> ✅ **O §1 deste documento NÃO depende disto** e segue de pé: ele repousa na Tabela 1 do
> artigo, conferida contra o PDF primário.

### (registro, ERRADO) Achado de DADO: a `test3` está 20 % adiantada e isso INVERTE a ordenação

Round-trip do nosso CSV contra a Tabela 1 (N até `F/F₀` = 0,90):

| curva | paper | nosso CSV | erro |
|---|---:|---:|---:|
| `test2` | 278 | 288 | +4 % |
| **`test3`** | **325** | **260** | **−20 %** |
| `test4` | 406 | 406 | −0 % |
| `test5` | 72 | 65 | −9 % |
| `test6` | 54 | 56 | +4 % |
| `test7` | 1050 | 1160 | +10 % |
| `test8` | 936 | 1028 | +10 % |
| `test9` | 180 | 203 | +13 % |
| `test1` | sem queda | sem queda | ✅ |

Sete das nove ficam em ±13 %, o que é razoável para digitalização em eixo log. **A
`test3` é a pior (−20 %)** e o efeito não é só de magnitude: no impresso a `test3` é
**17 % mais lenta** que a `test2` (325 vs 278); no nosso CSV ela é **10 % mais rápida**
(260 vs 288). ⇒ **a ordenação entre as duas está invertida no nosso dado.**

⚠️ Isto é a mesma classe de defeito que as correções **D-W**, **D-U** e **D-S**
encontraram — digitalização que o ajuste depois absorve. **A não-monotonicidade da
Tabela 1 sobrevive à correção** (0,4 seguiria mais rápido que 0,5 e 0,7), então a
conclusão do §1 não depende disto; mas a `test3` é justamente a curva que passei a tarde
perseguindo, e ela pode estar sendo perseguida **contra um alvo 20 % errado**.

**Candidato de dado registrado, não executado:** re-digitalizar a `test3` da Fig. 2a com
alvo de round-trip = 325 ciclos. Precedente de método: D-W e D-R re-digitalizaram por
pixel/polilinha calibrada contra o valor impresso.

---

## 6. O que isto fecha e o que abre

| item | efeito |
|---|---|
| **I** (alvo dependente do deslocamento) | ⛔ **classe inteira falsificada** — não é o expoente nem o canal; é a monotonicidade |
| **B** (rugosidade) | ✅ custo medido: opção (a) = **−2 curvas**; e a correção é **certa** na `test3` |
| **D** (per-condition) | reforçado: cada condição precisa do seu número **porque o dado não é ordenado** |
| **novo** | forma de **regime de fretting** (taxa com máximo na transição) — a única classe compatível com a Tabela 1. **Não proposta**: o engine já tem `K_running_in/K_steady/K_severe` em `WearModelParams`, mas ligá-los é forma nova e o modelo hoje põe as 5 condições **no mesmo regime**, então o discriminante teria de vir antes |
| **dado** | re-digitalizar a `test3` (round-trip −20 %) |

## Reprodutibilidade

`chu_classe_mecanica.py`, `chu_orcamento.py`, `chu_rz_correto.py` no scratchpad; a
varredura de `C` e o round-trip foram inline. Só-leitura, ~60 min.
