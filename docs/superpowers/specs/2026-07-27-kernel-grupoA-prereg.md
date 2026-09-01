# PRÉ-REGISTRO — kernel de colapso desacelerante, escopado no GRUPO A

> **IMUTÁVEL a partir de agora.** Gates escritos ANTES de qualquer fit. Alterar
> qualquer critério depois de ver resultado invalida o prereg — abra outro.
> Convenção: máximo **2 preregs por candidato**; a segunda falha é falsificação
> documentada (FAIL2), não terceira tentativa.
>
> Escrito 2026-07-27 sobre o store certificado `4f5bedfbace4`, **depois** do
> diagnóstico `New_Theory/kernel_diagnostic_2026-07-27.md`, que corrigiu o escopo
> herdado da fila (ela nomeava Lu2024/Eccles/Chu/Sun; a família coerente é outra).

---

## 0. Escopo — por que ESTAS 13 curvas e não as 26

| fonte | n | MAE | res.máx | assimetria fim−início |
|---|--:|---|---|--:|
| CHU_2026 | 7 | 0,045–0,164 | 0,115–0,464 | **+0,204** |
| YANG_2019 | 4 | 0,052–0,100 | 0,136–0,517 | **+0,157** |
| KARLSEN_2022 | 1 | 0,090 | 0,236 | **+0,199** |
| ZHANG_2006 | 1 | 0,211 | 0,661 | **+0,447** |

Correlação entre os perfis de resíduo **detrendado** (nível removido por curva):
**0,90 a 1,00** em todos os pares. Quatro rigs independentes, bolt sizes e
materiais distintos, **mesmo erro de forma**: o modelo colapsa cedo demais e
depois trava tarde demais.

**Excluídos deliberadamente** (e o motivo medido): LU_2024 (10) tem perfil em
tigela, r = −0,27; SUN grease-standard r = −0,74; ECCLES fig8a/8c têm perfil
**plano** (erro de nível, não de forma). Incluí-los seria misturar formas
anticorrelacionadas — o erro que este prereg existe para não cometer.

---

## 1. A forma proposta (uma constante, não uma família)

O `self_locking_gate` atual já é suave: `g = max(0, 1 − F_min/F₀)`, com
`F_min = loose_arrest_floor·F₀_init`. O que falta não é suavidade — é o
**expoente** dessa aproximação. Proposta mínima:

```
g = max(0, 1 − F_min/F_0) ** arrest_approach_exp
```

- `arrest_approach_exp` (novo campo de `JointMaterial`), **default `1.0` = a
  expressão atual, bit-idêntica**.
- `> 1` ⇒ a taxa morre mais cedo conforme F₀ se aproxima do piso ⇒ **desaceleração
  ao platô** em vez de aproximação linear.
- É **uma constante de forma**, adimensional, sem unidade a ancorar.

**Por que esta forma e não outra:** o perfil medido (negativo cedo → positivo
tarde) diz que o modelo gasta perda demais no início e de menos no fim. Um
expoente na comporta de arresto redistribui exatamente nesse eixo, sem tocar no
nível (que segue sendo o `loose_arrest_floor`, per-par e lido do dado).

---

## 2. Diagnóstico OBRIGATÓRIO já executado

Feito e versionado em `New_Theory/kernel_diagnostic_2026-07-27.md` antes deste
prereg: perfis por quintil, assimetria por fonte, matriz de correlação. É esse
diagnóstico que define o grupo A e exclui os outros 13.

---

## 3. GATES — imutáveis

**G1 — Inércia por construção (não-negociável).** Com `arrest_approach_exp=1.0`,
os **202 casos comparáveis** saem **bit-idênticos** ao store `4f5bedfbace4` em
`mae`, `maxerr`, `resid_std` e `final_pred`. Zero diferença, não "diferença
pequena". O campo é `fittable=False` no registry (switch de forma).

**G2 — Alvo local.** Das 13 curvas do grupo A, **≥8 entram no tripé**
(MAE ≤ 0,10 **E** res.máx ≤ 0,10) e **nenhuma das 13 piora**. Menos que 8 = FAIL.

**G3 — TRANSFERÊNCIA ENTRE RIGS (o gate que justifica a física).** O expoente é
ajustado **somente em CHU_2026** (7 curvas, a maior) e aplicado **sem re-fit** a
YANG_2019, KARLSEN e ZHANG_2006. *Passa* se, nos 3 rigs de fora do ajuste, o
res.máx médio cair **≥30%** em relação ao baseline. **Critério duro herdado do
prereg do Eccles: se o kernel precisar de um valor próprio por fonte, ele não é
uma forma — é um tuner com nome bonito e não deve ser adotado.**

**G4 — Não-regressão global.** Nenhum dos 202 casos piora mais de **+0,01** em
MAE ou res.máx; a mediana global não piora.

**G5 — O resíduo cai onde ele estava.** Para cada curva do grupo A, o perfil
detrendado tem de **achatar**: o |Q1| e o |Q5| do resíduo detrendado caem ≥30%.
Melhorar o MAE sem achatar o perfil = a forma não é a certa, mesmo que o número
melhore.

**G6 — Procedência.** `arrest_approach_exp` entra declarado como
**fitada-this-rig** (classe mais fraca), conta na contagem de DOF e vai no `prov`
do config adotado. Um valor por **grupo A inteiro**, não por fonte (é o G3).

**G7 — Verificação adversarial.** Antes de adotar, ≥3 tentativas independentes de
**refutar** o resultado (ex.: o ganho vem do expoente ou de re-fit implícito do
floor? o G3 passaria com o expoente sorteado? o achatamento do perfil é real ou
artefato da grade?). Maioria refutando = não adota.

---

## 4. Parada

- **1 tentativa** neste prereg. FAIL ⇒ as 13 curvas viram exceção-candidata com
  prova quantitativa (a diferença medida entre aproximação suave e arresto seco),
  ou aguardam um segundo prereg com forma **diferente** (não com outro valor).
- Em qualquer FAIL, statu quo **byte-idêntico**.

---

## 5. NÃO autorizado por este prereg

- Tocar em LU_2024, SUN, ECCLES ou qualquer fonte fora do grupo A.
- Re-fitar `loose_arrest_floor` junto com o expoente (confunde nível e forma —
  e o nível já tem procedência própria).
- Um valor de `arrest_approach_exp` por fonte (é exatamente o que o G3 proíbe).
- Adotar com G3 falhando, ainda que o G2 passe: fechar 13 curvas com um tuner
  per-rig é o resultado que este projeto existe para recusar.

---

# RESULTADO — executado em 2026-07-27 (tentativa única gasta)

> Seção acrescentada APÓS a execução. **Nenhum gate acima foi alterado.**
> Objetivo de fit declarado antes de rodar (lacuna do §3, fechada na execução):
> minimizar a **média do res.máx sobre as 7 curvas do CHU_2026**, em grade fixa
> `m ∈ {1; 1,25; 1,5; 1,75; 2; 2,5; 3; 4}` — sem busca contínua. Escolhido porque
> `MAE ⊆ maxerr` no conjunto inteiro, logo o res.máx é o critério ligante.

## Veredicto: **G2 FAIL · G3 FAIL**

**G3 — transferência (o gate que decide).** Expoente ajustado no CHU (m = 4,0,
borda da grade) aplicado **zero-refit** a Yang2019, Karlsen e Zhang2006:

| | res.máx médio |
|---|--:|
| base (m = 1,0) | 0,2822 |
| transferido (m = 4,0) | **0,3075** |
| variação | **−9,0% (PIOROU)** — exigido: queda ≥ 30% |

**G2 — alvo local.** Dos 13 violadores, **1 entrou** no tripé (exigido ≥ 8) e
**4 pioraram** (`yang2019` ×3 e `karlsen2022_M30_HVtorqued_run14p2`, este de
0,2363 → **0,3776**). O gate exige "nenhuma das 13 piora".

| caso | base | m = 4,0 | |
|---|---|---|---|
| `chu2026ti_D0p3mm_F0_49kN_test1` | 0,066 / 0,115 | **0,027 / 0,035** | ENTROU |
| `karlsen2022_M30_HVtorqued_run14p2` | 0,090 / 0,236 | 0,148 / **0,378** | piorou |
| `yang2019_M10_amp0p6_5Hz` | 0,086 / 0,517 | 0,091 / 0,543 | piorou |
| `yang2019_M10_varamp_small_to_large` | 0,064 / 0,194 | 0,065 / 0,198 | piorou |
| `yang2019_M10_varamp_large_to_small` | 0,052 / 0,136 | 0,053 / 0,142 | piorou |

## O achado estrutural — por que o fit foi degenerado

`self_locking_gate` retorna **1,0 exato** quando `loose_arrest_floor ≤ 0`, e o
expoente eleva justamente esse gate. Medido nas 16 curvas do escopo:

- **8 de 16 têm piso ativo** (`floor = 0,08`, vindo do pack). Nas outras 8 o
  expoente é **exatamente inerte** — `1,0^m = 1,0`.
- **No CHU_2026, apenas `test1` tem piso ativo.** As outras 8 curvas do CHU
  saíram **bit-idênticas** em toda a grade.

Portanto o "ajuste em CHU (7 curvas, a maior fonte)" prescrito pelo §0 foi, na
prática, um **ajuste sobre UMA curva** — e a monotonicidade até a borda da grade
(0,2478 → 0,2365, apenas −4,6% na média de 9) era essa única curva melhorando
69% diluída nas outras oito, não um ótimo.

**O G3 pegou exatamente o que existe para pegar:** um valor que fecha
brilhantemente a curva em que foi ajustado (`test1`: res.máx 0,115 → 0,035) e
que, transferido, **degrada** os rigs de fora. Se o G3 não estivesse escrito, o
resultado do `test1` sozinho pareceria uma vitória.

## Interpretação honesta — o que morreu e o que não morreu

**Morreu:** `arrest_approach_exp` como *a* forma compartilhada do grupo A. FAIL1
registrado; resta **uma** tentativa, e o §4 exige que seja com forma
**diferente**, não com outro valor.

**Não morreu, e é ressalva real:** o teste foi **fraco por construção**, e a
fraqueza estava no meu próprio §0. Escolhi o CHU como âncora do G3 por ser a
maior fonte, sem antes verificar se o mecanismo que o expoente modula estava
sequer **ativo** ali — não estava, em 8 das 9 curvas. Um prereg que ancorasse o
fit num rig com piso ativo (Yang2019, 4 curvas com `floor = 0,08`) testaria a
mesma forma com poder muito maior. **Isso não autoriza refazer esta tentativa**
— o gate está gasto e mudar a âncora depois de ver o resultado é exatamente o
que a imutabilidade proíbe. Fica registrado como **defeito de desenho do
prereg**, para a próxima: *antes de escolher a fonte-âncora do gate de
transferência, verificar que o mecanismo modulado está ativo nela.*

**Consequência para a fila:** as 13 curvas do grupo A seguem form-limited. A
segunda tentativa, se autorizada, deve (a) usar forma diferente e (b) ancorar
num rig onde o mecanismo esteja ativo.

## Statu quo

- Nada adotado. `arrest_approach_exp` fica no engine como **capability
  não-adotada, default `1.0` = bit-idêntica** (mesmo tratamento do
  `flank_s_crit`, PARE da F4): o campo documenta um FAIL medido em vez de apagar
  a evidência.
- Store canônico **não tocado** — a execução rodou inteiramente in-process, sem
  gravar.

**G1 — evidência, com o escopo declarado.** Verificado por três vias, e o que
**não** foi feito também está dito:

1. **Por construção:** `arrest_approach_exp == 1.0` faz `self_locking_gate`
   retornar por *early-return* a expressão anterior, sem passar por `**`. Não
   depende de `pow(x, 1.0) == x` do libm.
2. **Teste unitário** (`test_arrest_approach_exp_inert_at_default`): igualdade
   **exata** (`==`, não `isclose`) em 4 combinações de F₀/F₀_init/floor.
3. **Contra o store certificado, em três amostragens independentes:**
   - **45 casos aleatórios** (semente fixa 20260727, sem viés de comprimento —
     inclui curvas de 240k ciclos);
   - **60 casos de curva mais curta** (12 fontes);
   - **16 curvas do escopo do grupo A**, bit-idênticas na coluna `m = 1,0` da
     própria execução do G3.

   **União: 105 casos distintos de 203 (52%), cobrindo 25 das 29 fontes ×
   4 métricas = 420 comparações, 0 divergências.**

**Não executado:** o batch completo dos 202 num só lote. O G1 está verificado em
**metade da biblioteca, em amostra não-enviesada**, mais a prova por construção —
declarado assim em vez de afirmado como se fosse a suíte inteira.
