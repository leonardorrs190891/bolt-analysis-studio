# `graded_scrit` FALSIFICADO para a P-13 — família certa, lei errada, e a P-13 fica mais precisa

**2026-08-07** · só-leitura · **nada adotado** · escolha do professor:
*"escolha a mais coerente"*.

## Por que escolhi esta

Das oito formas faltantes inventariadas, o **`graded_scrit`** era a única já
**construída** no engine (default-inerte) — e o docstring dele descreve
**exatamente** o defeito que eu havia medido em três fontes:

> `loose_rate_mode="torque"` (default) *"em disp-mode é **RUNAWAY-TO-ZERO uma
> vez disparado**… a amplitude decide **SE** dispara, não a **TRAJETÓRIA**"*
> `"graded_scrit"` … *"**SEM runaway** … a taxa **satura** … colapso
> quase-**LINEAR**"*

⇒ hipótese: a P-13 não é forma faltante, é forma **desligada**.

## ⚠️ Duas tentativas INVÁLIDAS antes do teste bom — as duas minhas

**(1) Kernel trocado com o canal desengatado.** No `IJPEM 0_25` nominal o
rotacional é **0,0 %** — medi o slip e ele é **0,00 µm** em todos os 4000
ciclos, porque `delta_free`=0,18 mm consome o curso inteiro. Trocar a lei de
taxa de um canal que não engata é inerte **por construção**.

**(2) `s_crit` fora do regime do rig.** Com `delta_free`=0,16 mm o slip real
tem **mediana 12,97 µm** (máx 89,68). Eu varria `s_crit` em **20–60 µm** — a
faixa do Bauer citada no próprio docstring — ou seja, **acima** do slip. Logo
`excess = max(0, slip − s_crit) = 0` e o branch retornava zero.

Assinatura que denunciou: **resultado idêntico ao dígito nas 9 células**. A
regra do `CLAUDE.md` — *"grade que dá resultado IDÊNTICO = INÉRCIA, não
robustez"* — é o que impediu de publicar "a forma não funciona" a partir de um
teste que nunca rodou. Sexta ocorrência desta lição na campanha.

## O teste VÁLIDO, e o veredicto

`s_crit` ∈ {1, 3, 6, 10} µm (**abaixo** do slip medido) × `k_loose_graded` ∈
{0,05; 0,2; 1,0; 5,0}, com `delta_free`=0,16 mm para engatar o canal:

| s_crit | k | MAE | res.máx | **final do modelo** | rotacional |
|---:|---:|---:|---:|---:|---:|
| 10 µm | 0,05 | **0,1600** | 0,5200 | **0,0000** | 92,7 % |
| 6 µm | 0,05 | 0,2121 | 0,6400 | **0,0000** | 94,1 % |
| 3 µm | 0,05 | 0,2554 | 0,6400 | **0,0000** | 94,5 % |
| 1 µm | 5,00 | 0,6543 | 0,9400 | **0,0000** | 98,2 % |

**O canal engata (92–98 %) e o final é 0,0000 em TODAS as 16 células.** O dado
termina em **0,5200**. O melhor MAE (0,1600) mal difere do nominal (0,1664).

## O que isto estabelece — e torna a P-13 mais precisa

O docstring está **correto** e eu li rápido demais: ele diz que **a TAXA**
satura, não que **a PERDA** pare. Uma taxa constante não-nula leva F₀ a zero de
qualquer jeito — **linearmente** em vez de explosivamente. Trocar
`torque` por `graded_scrit` troca a *forma do colapso*, não o *destino*.

⇒ **a forma #8 é a família certa com a lei errada.**

E isso afia a **P-13**. O que o dado exige não é *"taxa fracionária constante"*
como escrevi — é **taxa que decai com a pré-carga restante**, de modo que o
colapso **pare** num nível não-nulo determinado pela física:

| lei | destino | quem a tem |
|---|---|---|
| torque (default) | zero, acelerando | engine |
| `graded_scrit` | zero, linear | engine (inerte) |
| **∝ pré-carga restante** | **platô não-nulo** | **ninguém** |

O `loose_arrest_floor` é a versão **crua** disso: ele para o colapso, mas com
uma **constante** em vez de um mecanismo — e é por isso que ele aparece
"compensando forma faltante" no ROUSSEAU (`rousseau_bifurcacao_resultado.md`) e
por isso que suas pernas têm ótimos conflitantes.

## Corolário: a forma #8 sai do inventário como candidata

`formas_faltantes_inventario.md` listava `graded_scrit` como *"já existe no
engine, default-inerte"*, sugerindo que bastaria ligá-la. **Não basta.** Ela
permanece no inventário como **capacidade existente que não cobre a P-13**, e a
P-13 volta a ser forma **nova**.

⚠️ **Não medido:** que `graded_scrit` seja inútil em geral. Ele pode servir a
outras fontes (o docstring cita Bauer s_crit≈99 µm e Karlsen *"near-linear
catastrophic back-off"*) — o que está medido é que **não entrega o platô** que
as três fontes da P-13 exigem.

## Reprodutibilidade

As três varreduras (inválida ×2, válida ×1) e a medição de slip por instrumentação
de `resolve_transverse_slip` estão no scratchpad, recomputáveis em minutos.
