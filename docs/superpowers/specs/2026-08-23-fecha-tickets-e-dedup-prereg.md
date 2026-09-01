# PREREG — fecha os 3 tickets + DEDUP de par declarado (resolve o que ficou aberto)

**Assinado pelo professor em 2026-08-23** (*"resolva o que tá aberto"*, sobre os itens
deixados abertos pela adoção do ITEM X). Gates **IMUTÁVEIS** a partir desta linha.

**Baseline congelado:** `git HEAD 4ff9f06` · censo `_censo()` = **tripé 169/205**,
`declarado_total` **201**, `fora_aberta` **4** · suíte **1129 passed / 1 skipped** ·
piso `ECCLES_2010` = (0,0507 · 0,1543 · **0,0565**).

---

## 1. O que muda — quatro coisas, e uma delas é conserto de defeito MEU

**(a) `frequency_Hz` entra em `_CAMPOS_VARRIDOS`.** Medido: quebra **zero** pares
existentes (225 → 225). É parâmetro **ajustado**, não alcançado — duas réplicas na mesma
frequência nominal têm o mesmo valor.

**(b) Dois rótulos novos em `_varredura_por_curva`:**
- `KARLSEN_2022` → **dispositivo de travamento** (`hv` / `hvtorqued` / `vibralock` /
  `vibralock_torqued`), lido do `case_id`. ⚠️ Alternância com o token **longo primeiro**,
  pelo trap de substring que já custou o regex do SUN.
- `LI_2022_MARSTRUC` → **pré-carga NOMINAL** (`preload_5kN` / `10kN` / `15kN`).

**(c) As 14 curvas dos 3 tickets saem do bloqueio** ⇒ `_SEM_FAMILIA_MECANICA` fica com
**zero** entradas ativas (os 81 motivos permanecem escritos: são procedência).

**(d) ⚠️ DEDUP DE PAR DECLARADO — conserto de defeito que EU introduzi em `940a2c0`.**
O par declarado entra em `grupos` sob chave própria `(src, "DECL", rótulo, None)`. Quando a
chave automática **também** agrupa os dois membros, **o mesmo par conta duas vezes**. Antes
do ITEM X isso não acontecia (as curvas estavam bloqueadas); depois dele, **3 de 5** pares
declarados ficaram duplicados, e com (a)–(c) seriam **4 de 5**. O conserto: pular a entrada
declarada quando a chave já faz o par — é o que a própria docstring do mecanismo diz que ele
é para (*"réplicas … que a chave mecânica **nunca casaria**"*).

## 2. ⛔ `initial_preload_N` NÃO entra na chave — FALSIFICADO

Era a rota óbvia para `LI_2022_MARSTRUC` (5/10/15 kN) e `KARLSEN` (11 valores distintos).
**Está errada, e o próprio repositório diz por quê:** o `_PARES_REPLICA_DECLARADOS` existe
para *"réplicas cujo F₀ **ALCANÇADO** difere (aperto nunca repete: 4–14 % nos pares do
LU)"*. Ou seja **toda réplica real tem F₀ diferente** ⇒ pôr F₀ na chave destruiria
pareamento legítimo em todo o projeto.

E ele nem resolveria o KARLSEN: `M42_HV_run21p0` e `M42_vibralock_torqued_run29p0` têm
**F₀ idêntico (685 kN)** e diferem no **travamento**. Daí o rótulo, não o número.

⇒ Regra que fica: **na chave entram grandezas AJUSTADAS (nominais), nunca ALCANÇADAS.**
`frequency_Hz` é ajustada; `initial_preload_N` é alcançada.

## 3. Gates — congelados

| # | gate | reprova se |
|---|---|---|
| **G1** | **Exatamente 2 exceções são retratadas** — as 2 prova-de-piso do `ECCLES` — com prova **preservada** em bloco de retratação. As outras **19** ficam intactas. | qualquer outra se move, ou a prova é apagada em vez de preservada |
| **G2** | **Censo: tripé segue 169.** `declarado_total` **201 → 199** e `fora_aberta` **4 → 6** — custo DECLARADO, medido antes de executar. | o tripé muda, ou o custo difere do previsto |
| **G3** | **Nenhum `limite_sres` AFROUXA.** Só o `ECCLES` se move: **0,0565 → 0,0432** (aperta). | algum limite sobe |
| **G4** | **Zero pares declarados duplicados** pela chave automática, depois do dedup. | sobra algum |
| **G5** | **Os 3 tickets não produzem família espúria**, e os pareamentos corretos do ITEM X seguem. | alguma família espúria sobra, ou um pareamento correto se desfaz |
| **G6′** | **Toda mudança de piso é ATRIBUÍVEL** — a um campo de `_CAMPOS_VARRIDOS` que a fonte de fato varre, ou ao dedup. *(este é o gate corrigido que o ITEM X deveria ter tido: o G6 antigo exigia piso bit-idêntico e por isso proibia a chave de agir, contradizendo o próprio prereg.)* | alguma mudança fica sem atribuição nomeada |
| **G7** | **`_SEM_FAMILIA_MECANICA` ativo = 0** e os **81 motivos preservados**. | motivo apagado, ou sobra bloqueio ativo |
| **G8** | **Suíte sem regressão** (≥ 1129 passed, 0 failed). | falha nova |
| **G9** | **`initial_preload_N` NÃO está na chave**, e a falsificação da §2 fica escrita. | entra na chave |

**Ramo `INCONCLUSIVO`:** se a mudança de piso do ECCLES não puder ser atribuída
separadamente ao dedup e à chave, nada é adotado.

## 4. Predições REGISTRADAS antes de executar

**P1 — só UMA fonte muda de piso:**
`ECCLES_2010` (0,0507 · 0,1543 · 0,0565) → (**0,0474 · 0,1220 · 0,0432**). Nenhuma outra,
**incluindo as 3 dos tickets** (elas já tiravam piso de par declarado, e o par sobrevive
via chave automática com os mesmos membros).

**P2 — pares declarados 5 → 1** (o dedup remove 4: CACCESE, ECCLES, LIU_2016 e o TRIBOINT
que (a)–(c) passam a fazer).

**P3 — as 2 provas de piso do ECCLES FALHAM e são retratadas:**

| curva | MAE | res.máx | σ | veredito |
|---|---|---|---|---|
| `fig8a` | 0,0489 / 0,0474 **FALHA** | 0,1320 / 0,1220 **FALHA** | 0,0395 / 0,0432 PROVA | **FALHA** |
| `fig8c` | 0,0456 / 0,0474 PROVA | 0,1463 / 0,1220 **FALHA** | 0,0386 / 0,0432 PROVA | **FALHA** |

**P4 — censo:** tripé **169** (intacto), `declarado_total` **199**, `fora_aberta` **6**.

**P5 — `frequency_Hz` quebra zero pares** existentes (225 → 225).

**P6 — a família de 4 do ECCLES é LEGÍTIMA, e isso foi MEDIDO, não assumido.** Os 6 pares
dado-contra-dado dentro dela:

| par | MAE | res.máx | σ |
|---|---:|---:|---:|
| fig3 × fig7a | 0,0479 | 0,1104 | 0,0214 |
| fig3 × fig8a | 0,0502 | 0,1109 | 0,0592 |
| fig3 × fig8c | 0,0288 | 0,0756 | 0,0357 |
| fig7a × fig8a | 0,0556 | 0,1846 | 0,0552 |
| fig7a × fig8c | 0,0478 | 0,0640 | 0,0203 |
| **fig8a × fig8c (o declarado)** | 0,0541 | **0,1866** | **0,0707** |

⚠️ **O par declarado pelo autor é o PIOR dos seis** — máximo em res.máx *e* em σ. Nenhum
par é outlier (MAE 0,029–0,056; mx 0,064–0,187; σ 0,020–0,071) ⇒ `fig3` e `fig7a`
concordam com os baselines tanto quanto os baselines concordam entre si. É por isso que
contar o par declarado **duas vezes** inflava o piso a 0,1543, e é por isso que as 2
exceções perdem a prova: **elas repousavam no par mais frouxo, pesado em dobro.**

## 5. O custo, dito sem eufemismo

Duas exceções assinadas caem, e o número publicado **piora**: `declarado_total` 201 → 199.
A alternativa seria manter um piso que eu sei estar inflado por contagem dupla, para
proteger duas exceções que dependem exatamente dessa inflação. Precedentes de retratação
por base inválida neste projeto: ROUSSEAU (piso inválido), CACCESE (piso inválido), LU
(protocolo cruzado). **O rigor vale contra nós.**

## 6. Rollback

`git revert`. Sem engine, sem config adotado, sem store, sem fingerprint — o piso é
recomputado na geração do report.
