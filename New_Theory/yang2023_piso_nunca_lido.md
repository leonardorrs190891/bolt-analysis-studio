# ✅ DESFECHO 2026-08-20 — as 3 FECHARAM, e a retratação abaixo SOBREVIVE

> **As três curvas do `YANG_2023_IJPEM` fecharam o tripé** na adoção P-13 da sessão
> paralela (`ada1be5` + `3c86e54`): MAE **0,0145 / 0,0203 / 0,0202** contra os
> **0,120 / 0,179 / 0,239** de antes. Censo **158/205**.
>
> ⚠️ **Isto parece contradizer a retratação abaixo — e NÃO contradiz.** Eu havia retirado a
> forma nomeada delas com o argumento de que *"não formam classe: 3 regimes, 3 sinais de
> resíduo"*. Conferi como o fechamento foi feito:
>
> | | |
> |---|---|
> | forma | `loose_F_exp` — **campo NOVO**, default **0 = OFF exato** (teste 8/8, VarSpec 120/120) |
> | onde vive a constante | **`per_case`**: 3 tokens separados (`0_30_mm` e `0_50_mm` no grupo `_m6`; `0_35_mm` no `_m8`) |
> | de onde vem o número | **LSQ da solução fechada da EDO contra o F(N) PUBLICADO** de cada curva, r² **0,9968–0,9999** |
>
> ⇒ **não é constante compartilhada.** O que as três compartilham é uma **FORMA**; os
> expoentes são **por curva, lidos do impresso**. É exatamente a doutrina §8 do repo —
> *formas e acoplamentos transferem cross-rig, constantes não*.
>
> ⇒ o veredito *"não formam classe"* era sobre **constante compartilhada**, e segue válido.
> O que faltava não era classe: era a **forma** que a P-13 nomeou em 3 fontes desde 08-07 —
> o meio-termo entre os dois atratores (runaway ∝ slip × arresto pelo re-travamento do
> `[K(s)]`). **Nada aqui é meu**; registro para que a coincidência de alvo não seja lida
> como contradição.

---

# ⛔ RETRATADO — `YANG_2023_IJPEM`: o piso estava CERTO, e a forma que nomeei não existe

> **RETRATAÇÃO INTEGRAL em 2026-08-16 (13:0x), 4 h depois de escrito.** O documento
> abaixo afirmava que a fonte roda no ramo *runaway* porque **ninguém leu o piso**, e que
> o dado **arresta em 0,165** enquanto o modelo vai a zero. **As duas coisas são falsas.**
>
> ⚠️ **A causa do erro é exatamente a armadilha que a sessão paralela documentou no mesmo
> dia** (`a36675d`, `piso_da_metrica_o_que_ele_esconde.md`): **eu li `metric_data`**, que é
> o dado **DEPOIS do `FLOOR_TRIM` = 0,10**, e chamei o último valor dele de *"piso de
> arresto do dado"*. O dado **cru** continua caindo.
>
> **Medido no CSV cru, as 6 curvas acima do limiar:**
>
> | amp | cauda crua |
> |---|---|
> | 0,30 | 1,0 · 0,88 · 0,80 · 0,62 · 0,42 · 0,22 · **0,06** |
> | 0,35 | 1,0 · 0,90 · 0,84 · 0,72 · 0,56 · 0,38 · 0,15 · **0,05** |
> | 0,45 | 1,0 · 0,88 · 0,78 · 0,62 · 0,36 · 0,16 · **0,05** |
> | 0,50 | 1,0 · 0,75 · 0,52 · 0,30 · 0,12 · **0,02** |
> | 0,55 | 1,0 · 0,82 · 0,66 · 0,44 · 0,18 · **0,05** |
> | 0,65 | 1,0 · 0,78 · 0,58 · 0,36 · 0,16 · **0,03** |
>
> **⚠️ E o leitor canônico JÁ DIZIA ISSO — eu é que não o consultei.**
> `floor_from_curve` (= `arrest_floor_from_curve`) sobre o CSV cru devolve
> **`plateau=False` nas 7 curvas que afrouxam** (0,25 a 0,65 mm) — ou seja, o helper se
> **recusa** a chamar aquilo de platô e rotularia qualquer valor lido ali como *"LIMITE
> INFERIOR — curva termina em queda"*. As duas únicas com `plateau=True` são as
> **abaixo do limiar**, que não afrouxam (piso 0,93). ⇒ **um comando teria matado a
> proposta**, e o comando existia.
>
> ⚠️ **A mesma flag, na direção oposta, achou um defeito REAL:** varrendo os 33
> `loose_arrest_floor` adotados, o `ECCLES_2010_fig7d` carrega piso **0,137** gravado
> como *"assíntota final crua"* sobre uma curva que colapsa a **0,000** — porque a flag
> foi descartada entre ler e adotar. Item **R** da mesa,
> `eccles_piso_nao_sustentado_pelo_dado.md`. **O meu erro produziu a auditoria que achou
> o dele.**
>
> ⇒ **o dado NÃO arresta** — colapsa a 0,02–0,06 em todas. Logo
> `loose_arrest_floor = 0` está **CERTO** para esta fonte, e o modelo indo a 0,000 está
> mais perto do que eu afirmei. **O achado "ninguém leu o piso" CAI.**
>
> **E a forma nomeada cai junto.** Os vieses das 6 são MISTOS em sinal
> (+0,047 · −0,159 · −0,094 · **+0,239** · −0,119 · +0,018), com `ρ(res,N)` de −0,90 a
> +0,70 ⇒ **não há defeito único**. Isso **confirma** o veredito que a sessão paralela já
> publicara em `16300e8` — *"3 regimes, 3 sinais distintos, não é uma classe"* — e que eu
> contrariei.
>
> **Consequência assumida:** as 3 curvas saem de `_FORMA_NOMEADA`; a 2ª linha da fila volta
> de **21 para 18 de 21**. O marco de "21 de 21" era meu e está desfeito.
>
> ⚠️ **O que sobrevive:** a §1 (a fonte é internamente coerente, `ρ(amp, retenção)` =
> −0,745) e a §7 (escopo: 15 fontes com floor no default, importa em 1 — que agora vale
> **zero**, já que a única era esta). O resto é registro do erro.

---

# `YANG_2023_IJPEM` — a fonte roda no ramo *runaway* porque **o piso nunca foi lido**

**2026-08-16 (09:0x)** · só-leitura · **nada adotado** · store `20be19aabe11`,
censo **144/205**, 2ª linha da fila **18 → 21 de 21**.

---

## 1. A fonte é "não verificável" — mas **checável contra si mesma**

O PDF está sob paywall e a digitalização nunca foi conferida contra o impresso.
Isso bloqueia a verificação **externa**, e por isso eu havia escrito (item E) que
nomear uma forma aqui seria *"nomear um defeito que talvez seja do dado"*.

⚠️ **Faltou um teste que não precisa do PDF:** a fonte varre **9 amplitudes**
(0,15–0,65 mm). Digitalização sã produz **ordenação física**. Medido:

`ρ(amplitude, retenção final)` = **−0,745** — amplitude maior afrouxa mais.
⇒ **a digitalização NÃO está embaralhada.**

## 2. O que a coerência revela: um LIMIAR, e um PISO

| amp (mm) | 0,15 | 0,18 | **0,25** | 0,30 | 0,35 | 0,45 | 0,50 | 0,55 | 0,65 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **dado** | 0,925 | 0,930 | **0,520** | 0,220 | 0,150 | 0,160 | 0,120 | 0,180 | 0,160 |
| **modelo** | 0,949 | 0,946 | **0,946** | **0,000** | **0,000** | **0,000** | 0,367 | **0,000** | **0,000** |

O dado tem **transição** entre 0,18 e 0,30 e depois **arresta** — as 6 acima do
limiar ficam em **0,12–0,22**, média **0,165**, com dispersão pequena e sem
tendência.

⚠️ **O modelo é BINÁRIO**: ou quase não afrouxa (0,946) ou **vai a ZERO** — 5 das
9 terminam em **0,000 exato**. Ele não tem o meio-termo.

## 3. A causa, lida do config: o piso é o DEFAULT, não uma leitura

| | valor |
|---|---|
| `loose_arrest_floor` efetivo | **0,0** |
| nos 3 grupos adotados (`_IJPEM`, `_m6`, `_m8`) | `None` — **ninguém setou** |
| `loose_arrest_residual` | `None` |

⇒ o `0,0` é o **default do engine**, e o `CLAUDE.md` já diz o que ele significa:
*"`floor=0` ⇒ **runaway puro** (bifurcação arrest/zero, sem meio)"*.

⇒ **a fonte roda no ramo runaway porque o piso NUNCA FOI LIDO** — não porque
alguém mediu e achou zero.

## 4. A forma nomeada (as 3 abertas, todas acima do limiar)

As 3 sem forma nomeada são **0,30 · 0,35 · 0,50 mm**, todas na região arrestada —
e ficam nomeadas aqui pelo `case_id`, não só pela amplitude:

| `case_id` | amp | dado fim | modelo fim |
|---|---:|---:|---:|
| `10_Yang_2023_phenomenological_model__0_30_mm__8` | 0,30 | 0,220 | **0,000** |
| `10_Yang_2023_phenomenological_model__0_35_mm__3` | 0,35 | 0,150 | **0,000** |
| `10_Yang_2023_phenomenological_model__0_50_mm__9` | 0,50 | 0,120 | 0,367 |

> ⚠️ **Escrever o `case_id` não é formalidade** — na 1ª versão deste documento eu as
> descrevi só por amplitude, e a citação em `_FORMA_NOMEADA` ficou **MUDA**: nada ligava a
> entrada à prova de forma verificável. Peguei isso medindo as 21 citações da lista, e as
> 3 mudas eram as minhas. Mesma classe do problema das exceções sem trio conferível.

> **o dado arresta em ~0,165 e o modelo não arresta em lugar nenhum.** Falta o
> piso de auto-travamento, que nesta fonte é um valor **lível do próprio dado**
> (6 curvas concordantes), não um botão de ajuste.

⚠️ **É o MESMO defeito que o `ICMEZ_2025` nomeou** (*"o engine só oferecia o
binário arresto/runaway"*) e para o qual a sessão B construiu o
`loose_arrest_residual` — só que ali o modelo **arrestava alto demais** e aqui
ele **não arresta**. Extremos opostos da mesma bifurcação.

## 5. A rota existe e é de PROCEDÊNCIA, não de fit

A campanha tem `floor_from_curve` em `calibration/provenance.py` — o leitor que
extrai o piso do platô final do dado, exatamente a disciplina *"ler em vez de
fitar"* (L24). Aplicá-lo aqui é **ler um input que ninguém leu**, não ajustar
uma constante.

⚠️ **Não executo**: adoção de config exige assinatura. Fica como proposta com o
número já medido (**0,165 ± dispersão das 6**).

## 6. O que isto corrige em mim

Meu veredito do item E dizia que a fonte é não-verificável e que nomear forma
nela seria arriscar culpar o modelo por defeito do dado. **A medição inverte o
ônus**: o dado é coerente e graduado, com piso físico consistente em 6 curvas; o
modelo é o binário. ⇒ *"não dá para verificar contra o PDF"* **não** implica
*"não dá para verificar"*.

## Reprodutibilidade

Ordenação e classe por `resolve_transverse_slip` instrumentado; retenções de
`metric_data` no store; `loose_arrest_floor` de `rn._effective_overrides` e
`kb.adopted_config` — nenhum valor suposto.

---

## 7. ⚠️ ESCOPO — medido logo depois, e ele CONTÉM o achado

A conclusão *"ninguém leu o piso"* convida a uma campanha de ler os pisos de
todas as fontes. **Medi antes de propor isso, e o número mata a ideia:**

| | fontes |
|---|---:|
| com `loose_arrest_floor` = 0/None **e** dado que arresta acima de 0,05 | **15** |
| ...em que o **modelo de fato vai a ZERO** | **1** |

A única é o `YANG_2023_IJPEM` (5 das 9 curvas terminam em `0,000` exato). Nas
outras **14** o modelo arresta sozinho — por saturação do embedding, por creep,
pelo que for — e **nunca alcança o piso**. Ali o default é **inerte**.

⇒ *"o piso não foi lido"* é verdade em **15** fontes e **importa em 1**. Uma
campanha de leitura de piso seria **14/15 desperdício**.

⚠️ E há contraprova de que a leitura acontece onde precisa: o `ZHANG_2006` tem
`loose_arrest_floor` = **0,08**, lido, com 1 de 2 curvas no tripé.

**Regra que isto reforça:** constante no default só é defeito **se o caminho de
execução chegar nela**. Antes de propor "ler o input X em N fontes", meça em
quantas o X é alcançado — foi a mesma lição do `c_bend` (inerte sem pack) e do
`loose_arrest_floor` gateado por canal, já registrada nos gotchas.
