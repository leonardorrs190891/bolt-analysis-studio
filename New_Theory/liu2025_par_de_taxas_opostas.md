# `LIU_2025` — as 2 abertas têm **erros de taxa OPOSTOS**, e a rampa de fratura já está ligada nas duas

> ## 📍 CENSO CANÔNICO das estruturas falsificadas na `amp0p8`: **17** (2026-08-23)
>
> ⚠️ **ERRATA DUPLA, e a causa dos dois erros é a mesma: eu publiquei um número
> que era SOMA DE PARCIAIS EM PROSA em vez de contagem de uma lista.** A
> auditoria `integridade_modelo_ou_fit.md` (23/08) citou **15** — leu o parcial
> da §6, que não se declarava parcial; e o **16** que eu havia publicado na
> declaração também estava baixo, porque herdava o *"8 constantes"* do registro
> de 16/08 quando o shell canônico varre **9** alavancas (medido:
> `C_creep · creep_conform_exp · t_0 · N_emb · emb_depth · K_archard ·
> tr_loose_gain · loose_arrest_floor · arrest_approach_exp`). Nenhuma das duas
> leituras foi descuidada — **o número não era recomputável**, e é isso que a
> lista abaixo conserta (§4.43: número publicado carrega como se recomputa).
>
> **Constantes isoladas** (shell canônico, cada uma varrida em 2–4 doses):
> 1. `C_creep` · 2. `creep_conform_exp` · 3. `t_0` · 4. `N_emb` ·
> 5. `emb_depth` · 6. `K_archard` · 7. `tr_loose_gain` ·
> 8. `loose_arrest_floor` · 9. `arrest_approach_exp`
>
> **Formas e composições** (grade própria, células medidas entre parênteses):
> 10. forma da rampa de fratura `fat_ramp_D_on × q` (28 — teto σ 0,0283 = 1,13×) ·
> 11. `t_0` composto com a rampa no ótimo (18 — quebra o mx) ·
> 12. damage com starters físicos, `W_ref` 1e4 (6 — explode a 0,11–0,16) ·
> 13. damage em dinâmica lenta, `W_ref` 1e5–1e6 (6 — queda tardia, não no miolo) ·
> 14. wear + onset rebaixado, `K_archard × slip_onset_W` (14 — explode) ·
> 15. `graded_scrit` em qualquer `k_loose_graded` (9 — a explosão não depende de k) ·
> 16. `onset_burst` com gate compartilhado (21 — Δ=0 exato ou explode) ·
> 17. `onset_burst` com **gate PRÓPRIO**, a forma desenhada para a anatomia dela
>     (12 — sino real, σ 0,0507→0,0271, e ainda assim não fecha)
>
> Quem citar este número cita **17** e pode recontá-lo na lista. Os parciais das
> §5/§6 abaixo ficam como registro do que se sabia em cada momento, agora
> marcados como **acumulados até aquela seção**.

> ✅ **RE-VERIFICADO em 2026-08-20 contra o store `245dc93087d1`, censo 166/205** (o doc
> foi medido no `20be19aabe11`, censo 143). As pernas voltaram **iguais** — `amp0p8`
> **1,68×** no σ, `fig2_single` **1,08×** —, e a oposição que dá título ao doc foi
> **confirmada por um segundo instrumento independente**: o discriminante assinado
> `classe_parada_discriminante.py` mede viés terminal `mean(modelo − dado)` de
> **−0,0192** na `amp0p8` (desabou cedo) contra **+0,0542** na `fig2_single` (retém
> demais), estável nas duas janelas.
>
> ⚠️ **E isso tem consequência de ESTATUTO, não só de diagnóstico:** o sinal negativo põe
> a `amp0p8` como **falso positivo** da camada `classe_parada`, cujo remédio (*acelerar
> mais*) a **piora**. Proposta com gates congelados em
> `docs/superpowers/specs/2026-08-20-classe-parada-curva-a-curva-prereg.md`.
>
> ⚠️ **Errata de leitura, minha, registrada para não se repetir:** ao reler este doc eu
> quase usei o **ρ(resíduo, N)** daqui como discriminante da classe. ρ responde *"taxa ×
> offset"*; o discriminante assinado é **sinal do viés terminal**, que responde *"retém ×
> desabou"*. Ler o contrato do instrumento **inverteu** o meu veredito provisório sobre
> qual das duas era o falso positivo.

**2026-08-16 (00:5x)** · só-leitura · **nada adotado** · store `20be19aabe11`,
censo **143/205**, 2ª linha da fila **14 → 16**.

Diagnóstico pelo shell canônico (`ataque_curva.py`), contra a mesma barra do
`ICMEZ`, `YANG_2021`, `ROUSSEAU` e `SUN`.

---

## 1. Uma hipótese minha, falsificada em 30 segundos

Vendo **fadiga a 43–90 %** do incremento tardio, supus que a **rampa de fratura**
(`fat_ramp_D_on`, default-inerte) estivesse **desligada** — o que seria a forma
nomeada óbvia.

⛔ **Falso.** Nas duas curvas: `fat_ramp_D_on = 0,75` · `fat_ramp_q = 8,0` — a
rampa **está ligada**. Mesmo padrão do `YANG_2021`: **a forma existe, e lhe falta
a dependência que separa as curvas.**

## 2. As duas são OPOSTAS

| | `amp0p8` | `fig2_single` |
|---|---|---|
| pernas | MAE 0,79× · mx 0,86× · **σ 1,68×** | MAE 0,56× · mx 0,58× · **σ 1,08×** |
| `ρ(resíduo, N)` | **−0,52** | **+0,97** |
| curvatura | **B** — devagar cedo, rápido tarde | **A** — rápido cedo, devagar tarde |
| resíduo por terço | +0,036 · +0,063 · **−0,019** | −0,008 · +0,023 · **+0,055** |
| onde se forma | **meio/fim** (maior salto em u = 0,97) | **cedo** (u = 0,00) |
| incremento tardio | **0,466** — wear 47 % + fatigue 43 % | fatigue **90 %** |
| leitura | forma sobre o fim; 8 alavancas varridas, **nenhuma fecha** | **RAMPA**: déficit de **TAXA**, o erro **acumula** — alavanca de nível não conserta |

⇒ **mesma fonte, dois erros de taxa em direções opostas.** Uma perde rápido
demais cedo; a outra, devagar demais o tempo todo.

## 3. Por que as duas entram, e o que cada uma nomeia

**`fig2_single`** — o `ρ = +0,97` é a assinatura canônica de **déficit de taxa**
(o discriminante da própria campanha), num regime cujo incremento tardio é
**90 % fadiga**. Nomeia o mecanismo (taxa de fadiga) e o tipo de déficit (taxa,
não nível). Falha **só o σ, por 8 %**.

**`amp0p8`** — as **8 alavancas livres** foram varridas e **nenhuma fecha**: as
duas que melhoram o σ (`emb_depth` 6,5e-6 → 1,37×; `C_creep` 1,95e-11 → 1,53×)
**quebram o res.máx** (1,20× e 1,42×). Nomeia os canais (wear 47 % + fatigue
43 %) e a região (u = 0,97), e descarta a rota por constante.

## 4. ⚠️ O padrão que se repete em TODAS as fontes atacadas hoje

| fonte | par | veredito |
|---|---|---|
| `SUN_2025_CRIMP` | `standard` × `crimp` | sub-classe B × **offset cedo** |
| `LIU_2025` | `amp0p8` × `fig2_single` | sub-classe B × **sub-classe A** |
| `YANG_2021` | 8 curvas | forma adotada, **net zero** |
| `ROUSSEAU_2025` | 4 abertas | ótimos por curva **disjuntos** |
| `ICMEZ_2025` | 5 abertas | canal arresta, dado atravessa |

⇒ **em cinco fontes independentes, a mesma estrutura**: a forma existe (ou é
alcançável), e **uma constante compartilhada não serve à própria fonte** — as
curvas irmãs pedem direções opostas. Isso não é falta de mecanismo; é falta de
**dependência** dentro dos mecanismos que já existem.

## 5. 2026-08-21 — a FORMA da rampa de fratura foi varrida e tem TETO: 1,13×

A única forma in-engine que faltava varrer para a `amp0p8` era a própria rampa
(`fat_ramp_D_on`/`fat_ramp_q`, hoje 0,75/8,0 handbook). Varrida em **28 células**
(D_on 0,60–0,90 × q 3–20, incl. FORA da banda N_D=72–80 % do paper), com dois
achados:

1. **A direção que ajuda é a OPOSTA do meu palpite**: eu li a troca de sinal do
   resíduo como "colapso tardio+abrupto demais" e a grade mostrou que
   antecipar/suavizar (D_on↓, q↓) só PIORA — o que melhora é **atrasar** o
   onset (D_on↑). Com isso o resíduo vira TODO positivo com **corcova no meio**
   (+0,036/+0,063/+0,032; mx +0,0863 em x=5000): o defeito restante é o MIOLO
   (o modelo retém demais em u≈0,2–0,6), não o fim.
2. **Teto de autoridade da forma**: σ mínimo **0,0283** (D_on=0,86/q=9, fora da
   banda) e **0,0286** dentro da banda (0,80/12) contra limite 0,025 —
   **1,13×, NUNCA fecha**, com mae/mx folgados. Composições também falsificadas:
   `t_0` 0,3–0,5 quebra o mx quando a rampa está certa (só ajudava compensando a
   rampa errada); o canal de **damage** com starters físicos (c_D 1–4 ×
   k_dmg_wear 2–4, W_ref 1e4) EXPLODE a curva (σ 0,107–0,156) e c_D não
   diferencia (D satura — o W_slip desta curva ≫ W_ref). A dinâmica LENTA
   (W_ref 1e5–1e6 × k_dmg_wear 1–2, 6 células) também falsificada: melhor σ
   0,0411, pior que a rampa sozinha — o D acumula com o slip e adiciona queda
   TARDIA, nunca no miolo. Direção estruturalmente errada para esta corcova.

⇒ censo **ACUMULADO ATÉ ESTA SEÇÃO** (não o final — ver o canônico no topo,
que é **17**): **11**, sendo 8 constantes
(§3) + forma da rampa + t_0-composto + damage-starters. O σ excedente mora na
**taxa do miolo** (wear/damage progressivo que os kernels atuais não fazem sem
quebrar o resto). Segue **form-limited legítima** — única curva da fila; fechar
exige forma NOVA de taxa dependente do estado no canal de wear, que é decisão
de mesa, não de constante.

## 6. 2026-08-21 (16:2x-16:4x) — o "continue" mandou tentar TUDO in-engine: 4 vias a mais, todas falsificadas, e a ANATOMIA do bloqueio ficou nomeada

Sob o "continue" das 16:21, as composições restantes foram varridas ANTES de
desenhar forma nova. Todas morrem, e a última morte explica as outras:

1. **wear+onset (K_archard × slip_onset_W, 14 células)**: qualquer K>0
   explode (0,13–0,50) — e W_onset MAIOR piora, porque o gate Hill 0→1 é
   **monotônico**: o canal que ele destrava entra tarde e **nunca sai**. A
   corcova exige contribuição em **SINO** (sobe no miolo, desce antes do fim).
2. **graded_scrit em qualquer k (9 células, k 5e-4–2e-3)**: a explosão **não
   depende de k** (0,2515 em k=5e-4 ≈ 0,2547 do modo torque) ⇒ quem explode
   não é o graded — é o **wear via `k_wear_spec` HERDADO do shared** (5e-14):
   o `K_archard=0` do grupo não o desliga (gotcha documentado), e o
   `slip_onset_W=250000` do grupo existe exatamente para SEGURAR esse canal
   até o fim do ensaio. Baixar o onset para o miolo = abrir o wear com slip
   de 0,8 mm = brutal.
3. **onset_burst (o sino que o engine JÁ tem, 2ª instância natural da fig14)**:
   **bloqueado por construção nesta curva** — o burst é gateado pelo MESMO
   Hill `g` da incubação (engine L2410), então abri-lo no miolo abre o wear
   junto (item 2). Δ=0,0000 em 21 células com o gate em 250k; explosão
   idêntica com onset baixo. Não é defeito do burst: é acoplamento de gate
   compartilhado.
4. **Erro meu no caminho, 4ª instância da classe campo-silencioso**: sondei
   `loose_rate_mode='graded'` (o valor é **'graded_scrit'**) e
   `graded_scrit_k` (o campo é **`k_loose_graded`**) — ambos filtrados em
   silêncio, 15 células de sonda inválida até o teste de campo
   (`JointMaterial.__dataclass_fields__`) e a leitura do engine (L2355)
   denunciarem. Regra que fica: **modo e campo se leem do engine, nunca da
   memória** — o grep custa 10 s e a sonda cega custou 3 rodadas.

**Anatomia final do bloqueio** (o que qualquer forma futura tem de resolver):
o miolo precisa de +0,06 de perda que o fim NÃO recebe; os três gates de
estado existentes (slip_onset, damage, graded) são monotônicos e
compartilhados entre canais ⇒ tudo que abre no miolo continua aberto no fim
(quebra mx/σ) e arrasta o wear junto (explode). A forma nova precisa de
**pool finito com gate PRÓPRIO** (sino desacoplado do gate de wear) — é o
item 8 da mesa (`DECISOES_PENDENTES.md`), decisão (a)/(b) do professor.
Censo **ACUMULADO ATÉ ESTA SEÇÃO**: 15 pela contagem de então — e foi este
parcial que a auditoria de 23/08 citou como se fosse o total. O canônico é o
do topo, **17** (o "8 constantes" desta cadeia eram **9**).

## 7. 2026-08-21 (16:5x-17:1x) — a forma da anatomia FOI CONSTRUÍDA, sondada, e o veredito é honesto: o sino ajuda e NÃO fecha

`onset_burst_W` (gate PRÓPRIO do burst; +1 campo, 127→128, dormente no
ledger; `test_onset_burst_gate_proprio` 4/4 — 0.0 default = usa o `g`
compartilhado = bit-idêntico à adoção fig14, e o corolário central é
testado: mudar o gate do burst NÃO move o canal de wear). Duas armadilhas
de execução ficaram registradas no caminho:

- **o return sub-crítico vem ANTES do burst** (engine: `excess<=0 →
  _gth_only()`), mas não era ele (slip resolvido 0,49 mm, medido por
  instrumentação — 28 800 chamadas, 0 % zeros);
- **o pool é definido do F₀_INIT**: com frac=0,05 o alvo é 0,95·F₀_init e o
  embedding inicial já pôs o modelo ABAIXO disso quando o gate abre ⇒
  `_lac=0` para sempre, burst OFF **aritmético** (na fig14 do LU frac=0,62
  escondia isso). O frac tem de mirar o NÍVEL do miolo.

Sonda com pool dimensionado (frac 0,12–0,20 × W 3–8e4 × rate 0,0005–0,01,
sobre graded_scrit k≈0): **o sino é real** — σ 0,0507→**0,0271** (a maior
redução de σ que esta curva já viu em qualquer estrutura) — **e o preço
mata**: o dreno quebra o mx (0,1095 na melhor célula, até 0,22 nas outras)
e a entrada no ramo graded_scrit já custa +0,014 de σ/mae vs o kernel
torque do grupo. Melhor célula completa: 0,0514/0,1095/0,0271 contra
limites 0,05/0,10/0,025 — **as 3 pernas violadas por pouco, nenhuma
fechada**, com **6 números fitados sem procedência numa curva só**
(k_loose_graded, W_burst, frac, rate, D_on, q). A regra do projeto corta
aqui: *onde a rota exigiria fit puro por curva, ela fica*.

**Estatuto final**: a `amp0p8` fica **form-limited com o censo de
falsificações mais completo do projeto (**17** estruturas — lista enumerada no
topo)**; a capacidade
`onset_burst_W` fica DORMENTE no engine com esta sonda como 1ª evidência
direcional (o sino reduz σ 1,9× onde nada mais reduzia) aguardando uma 2ª
instância com procedência de leitura — ou a decisão (b) do item 8 da mesa.

## Reprodutibilidade

`py -3.12 New_Theory/ataque_curva.py liu2025_M16_amp0p8` e `…_fig2_single`; o
estado da rampa lido de `rn._effective_overrides`, não suposto. Grades da §5:
sonda inline com `rn._effective_overrides` embrulhado (idioma do shell),
2026-08-21 15:3x, store `c61366365977`.
