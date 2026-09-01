# A chave de família é **cega ao comprimento de aperto** — e 5 pontos de censo do `ICMEZ_2025` repousam nisso

**2026-08-14** · só-leitura · **nada adotado** · store `cb019d75c6c2`, censo **146/205** ·
módulos da sonda **limpos** no HEAD `604c67b` (conferido antes de medir) ·
⚠️ **exige assinatura** (invalidação de piso).

## Como cheguei aqui

O discriminante que derrubou os pares do `LU_2024` hoje (*"o platô aparece sempre do mesmo
lado?"*) só havia sido aplicado aos **7 pares DECLARADOS**. As famílias **automáticas** —
formadas pela chave mecânica `(fonte, δ, F_amp, modo)` — nunca passaram por ele. Passo 4(a)
do protocolo: premissa não testada.

## Primeiro, a boa notícia: as 4 famílias mais assimétricas são INÓCUAS

| família automática | razão `N(<0,90)` | os nomes revelam | `limite_sres` da fonte |
|---|---:|---|---|
| `LIU_2017_AXIAL` δ=0 F=10000 | **33 333×** | `F0_15kN` … `21kN` — **varredura de pré-carga** | **0,0250** = global |
| `ZHANG_2018` δ=0,25 | 531× | `1e3cyc` … `5e5cyc` — varredura de duração | **0,0250** |
| `ZHANG_2019` δ=0,2 | 98× | idem | **0,0250** |
| `LIU_2022_RETIGHT` δ=0,3 | 17× | `t0` … `t4` — estágios de reaperto | **0,0250** |

⇒ **as quatro pareiam não-réplicas, e as quatro não compram censo nenhum.** O limite delas é
o global.

⚠️ **Nuance que explica isso, e que corrige o meu próprio instrumento:** eu meço diferença de
**TAXA** (ciclos até F/F₀ < 0,90); o piso mede **σ da diferença ponto-a-ponto na janela
comum**. Uma família pode ter taxas 33 000× distintas e σ pequeno se a janela comum for
curta. ⇒ **razão alta ≠ piso inflado**; são grandezas diferentes, e só a segunda decide.

⚠️ Registro à parte, porque é ruído de bookkeeping e não de métrica: a chave é **cega ao F₀**
(em modo axial δ=0 e F_amp coincidem), então a varredura de pré-carga do `liu2017` forma uma
"família". O prereg dos pares declarados **previu exatamente isso** — *"roça os degraus de
10 % da varredura de F₀ do liu2017 (**falso-par catastrófico**)"* — e a defesa entrou no
caminho **declarado**, não no **automático**. Inócuo hoje; é dívida latente.

## ⚠️ A má notícia: o `ICMEZ_2025` é cego ao **grip**, e ali há censo

`lk` no nome dos casos = **comprimento de aperto** (`grip_mm` no config): **13,8 mm × 19,8 mm**.
A chave mecânica **não inclui `grip_mm`** ⇒ as 4 famílias do `ICMEZ` pareiam **rigidezes de
junta diferentes**. O desenho do paper é **2×2×2** (amp × F_amp × grip) e a chave colapsa a
dimensão do grip.

| família | n | MAE do piso | res.máx | σ |
|---|---:|---:|---:|---:|
| δ=0,3 F=7040 | 2 | **0,2087** | 0,3001 | 0,0939 |
| δ=0,3 F=5720 | 2 | **0,1756** | 0,2417 | 0,0667 |
| δ=0,4 F=7040 | 2 | 0,1109 | 0,1538 | 0,0338 |
| δ=0,4 F=5720 | 2 | 0,1050 | 0,1461 | 0,0350 |

⚠️ **MAE de piso 0,17–0,21 não é repetibilidade** — é a diferença entre dois comprimentos de
aperto. É a **mesma assinatura** do caso `SUN_2025_CRIMP` que a campanha já bloqueou (*"cujo
'piso' tinha MAE 0,448 porque pareava porca crimp × padrão"*) e do `KARLSEN` (*"pareava
Vibralock × HV"*).

⇒ `limite_sres(ICMEZ_2025)` = **0,0574**, contra o global **0,0250**.

## O custo, medido

Se `grip_mm` entrar na chave, os 8 casos formam **8 grupos de 1 membro** ⇒ **nenhuma família**
⇒ limite volta a 0,0250:

| curva | σ_res | com piso 0,0574 | sem piso (0,0250) |
|---|---:|---|---|
| `amp0p3_F14p3_lk13p8` | 0,0428 | PASSA | **sai** |
| `amp0p3_F14p3_lk19p8` | 0,0343 | PASSA | **sai** |
| `amp0p3_F17p6_lk13p8` | 0,0436 | PASSA | **sai** |
| `amp0p3_F17p6_lk19p8` | 0,0292 | PASSA | **sai** |
| `amp0p4_F17p6_lk13p8` | 0,0357 | PASSA | **sai** |
| `amp0p4_F14p3_lk13p8` | 0,0205 | PASSA | PASSA ✓ |
| `amp0p4_F14p3_lk19p8` | 0,0200 | PASSA | PASSA ✓ |
| `amp0p4_F17p6_lk19p8` | 0,0235 | PASSA | PASSA ✓ |

⇒ **censo 146 → 141.** Cinco pontos, e **3 das 8 sobrevivem por mérito** (σ ≤ 0,025 sem
qualquer piso), o que é o dado útil: a fonte não colapsa, ela encolhe.

## ⚠️ O que ainda NÃO está coberto por guarda

`tests/test_pares_piso_familia.py` vigia `_DEPENDEM_DE_PAR_DECLARADO` — **só pares
declarados**. Medido hoje, **13 curvas passam apenas por causa do piso da fonte**:

| fonte | n | família é réplica de fato? |
|---|---:|---|
| `KARLSEN_2022` | 4 | par **declarado** — já sob guarda |
| **`ICMEZ_2025`** | **5** | ❌ **não** — pareia grip 13,8 × 19,8 |
| `BAUER_2024` | 2 | ✅ sim — `fig6_rep1..rep6`, réplicas de nome |
| `CHU_2026` | 2 | ✅ sim — `test5` × `test6_**repeat**` |

⇒ **9 das 13 repousam em famílias AUTOMÁTICAS, fora do alcance da guarda existente.** Duas
delas são legítimas; **5 não são**.

## Decisão do professor

1. **Bloquear** as 4 famílias do `ICMEZ_2025` (via `_SEM_FAMILIA_MECANICA` ou incluindo
   `grip_mm` na chave) e aceitar **censo 146 → 141**; ou
2. **Manter**, declarando que para este rig o piso mede *"dispersão entre comprimentos de
   aperto"* — o que exige argumentar por que 0,17–0,21 de MAE é repetibilidade; ou
3. **Estender a guarda** primeiro (fazer `test_pares_piso_familia` vigiar também as famílias
   automáticas) e decidir depois, com o conjunto declarado.

Recomendo **(3) e depois (1)**, e explicito o incentivo contrário para que fique visível: a
opção (2) preserva 5 pontos de censo e é a única que não custa nada — **e é também a única
que contradiz três bloqueios que esta campanha já assinou** por exatamente este motivo.

⚠️ **Incluir `grip_mm` na chave é mudança GLOBAL** e pode afetar outras fontes; a rota
cirúrgica é `_SEM_FAMILIA_MECANICA` nos 8 casos do `ICMEZ`, que é o idioma já usado para
`ROUSSEAU`, `SUN` e `KARLSEN`.

> # ✅ EXECUTADO em 2026-08-14 ~12:45 (commit `2335090`, por delegação) — **predição 10/10**
>
> A sessão paralela bloqueou os dois pisos ilegítimos (`ICMEZ` grip + `CHU` δ=0,5).
> **Censo 146 → 140**, exatamente o custo previsto aqui.
>
> **A predição registrada foi conferida curva a curva, e acertou em todos os particulares:**
>
> | previsto | resultado |
> |---|---|
> | **6 sairiam do tripé** (5 `ICMEZ` + `chu…test5`) | ✅ **as 6 saíram** |
> | **4 sobreviveriam por mérito** (3 `ICMEZ` + `chu…test6_repeat`) | ✅ **as 4 sobreviveram** |
> | limite do `CHU` cairia para **0,0296** (só a família legítima) | ✅ **0,0296** ao dígito |
>
> Detalhe fino que também bateu: o `chu…test6_repeat` sobrevive com σ **0,0285** contra
> **0,0296** — margem de **4 %**. Ele vem da família boa e passa por pouco; era o ponto que a
> família ruim mascarava.
>
> As 5 do `ICMEZ` migraram para **`indecidivel_sem_piso`** (que foi 10 → 15): perderam o piso
> e a fonte ficou sem família — que é o estatuto honesto, não "reprovadas".
>
> ⚠️ **O item H seguia a rota mais barata no papel** (*"resolve-se de graça pelo item B"*), e a
> execução escolheu bloquear a família em vez de corrigir o input de rugosidade. As duas
> fecham o piso; só a do item B corrige também a **métrica** das 9 curvas do CHU. **O item B
> continua aberto.**

## 🗺️ O AUDIT DE PISOS FECHOU (2026-08-14 ~11:55) — 4 de 29 fontes, 2 ilegítimas

Em vez de parar nos pisos que compram censo hoje, mapeei **todos**. Só **4 das 29 fontes**
têm piso acima do global 0,025, e cada família foi verificada:

| fonte | limite | famílias | são réplicas de fato? | custo de corrigir |
|---|---:|---:|---|---:|
| `BAUER_2024` | 0,0900 | 2 | ✅ **sim** — `fig6_rep1..rep6` (réplicas de nome) e `fig8_test1/2/3` (notas idênticas; o PR-12e as trata como **ensemble min-max**) | 0 |
| `KARLSEN_2022` | 0,0903 | 1 | ✅ **sim** — par declarado, auditado hoje (razão 1,3×) | 0 |
| **`CHU_2026`** | 0,0507 | 2 | ❌ **a `δ=0,5` não**: pareia `Ra1p6um_test9` (notas: *"Ra=1.6 µm (rugosidade)"*) com `test3`, sem Ra rotulado. A `δ=1,0` **é** legítima (notas: *"**Réplica do test5**"*) | **−1 curva** |
| **`ICMEZ_2025`** | 0,0574 | 4 | ❌ **nenhuma** — todas pareiam `grip_mm` 13,8 × 19,8 | **−5 curvas** |

⇒ **corrigir as duas ilegítimas: censo 146 → 140.**

### ⚠️ O caso `CHU` é uma SEGUNDA consequência de uma dívida já na mesa

O `por_fonte` é a **média** das famílias, então a família ilegítima (σ 0,0718) infla o limite
que julga as curvas da **legítima**: 0,0507 em vez de 0,0296. Efeito medido: o
`chu2026ti_D1p0mm_F0_49kN_test5` (σ **0,0436**) passa hoje e reprovaria — e ele vem da família
*boa*.

E a causa raiz não é nova: **é a dívida de rugosidade do CHU** (item B da fila: *"as 9 no
`RZ_DEFAULT` contra Ra 0,4/1,6 µm do artigo"*). Como o config usa a rugosidade **default nas
duas**, a chave mecânica **não consegue distingui-las** — as duas aparecem como
`rz=Rz10-40`. ⇒ **a dívida de input não só afeta a métrica daquelas curvas: ela corrompe o
piso da fonte inteira.** Corrigir o input do CHU (item B) resolveria isto de graça, como
efeito colateral.

### O que a chave mecânica é cega a — inventário

| parâmetro | fonte onde mordeu | consequência |
|---|---|---|
| `grip_mm` (comprimento de aperto) | **`ICMEZ_2025`** | 5 pontos de censo |
| **rugosidade** (Ra) | **`CHU_2026`** | 1 ponto, via média das famílias |
| `F₀` (pré-carga) | `LIU_2017_AXIAL` (δ=0 ⇒ chave degenerada) | **inócuo** (limite fica no global) |
| duração do ensaio | `ZHANG_2018`, `ZHANG_2019` | inócuo |
| estágio de reaperto | `LIU_2022_RETIGHT` | inócuo |
| espessura, tipo de porca, dispositivo | `ROUSSEAU`, `SUN`, `KARLSEN` | ⛔ **já bloqueados** por assinatura anterior |

⇒ a chave é cega a **seis** parâmetros de primeira ordem; três já foram bloqueados por
decisão, três seguem abertos, e **dois dos três abertos custam censo**.

## ✅ A guarda foi ESTENDIDA (2026-08-14 ~11:35) — a parte que não precisa de assinatura

`tests/test_pares_piso_familia.py::test_censo_que_repousa_em_piso_de_fonte_nao_cresce_calado`
— espelho do teste do par declarado, **um nível acima**: não pergunta *de onde vem* o piso, só
se o censo depende dele. Com isso, as **9 curvas em família automática** entram no radar.

As 13 ficam **declaradas e classificadas** no próprio teste (réplica de fato × não), com o
custo do bloqueio do `ICMEZ` escrito ao lado. **Nenhum veredito muda** — o teste apenas impede
que o conjunto se mova calado, e é por isso que ele não exigiu assinatura.

**Validado por perturbação nas duas direções:** removi uma entrada do `ICMEZ` (simulando um
piso bloqueado sem atualizar a lista) ⇒ falha nomeando `demir2024_amp0p3_F14p3_lk13p8`;
acrescentei uma curva inexistente ⇒ falha nomeando-a como "saíu". Restaurado, passa.

⚠️ **O que a guarda NÃO faz, e é deliberado:** ela não bloqueia o `ICMEZ`. Bloquear muda
veredito de 5 curvas (censo 146 → 141) e isso é **decisão sua**. A guarda só garante que, se
alguém bloquear — ou se uma família nova comprar censo —, o fato apareça em vez de passar.

## Reprodutibilidade

Famílias automáticas reconstruídas com a mesma chave de `report_html._pisos_medidos`;
`limite_sres` pelo helper canônico; `grip_mm` de `config_used` e as notas do
`case_registry` (*"Clamp length 13.8 mm. Junker J160 per DIN 65151"*). Segundos, só-leitura.
