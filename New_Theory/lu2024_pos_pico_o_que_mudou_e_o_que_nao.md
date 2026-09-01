# Depois da correção do pico: o que mudou no `LU_2024` e o que **não** mudou

**2026-08-16 (06:0x)** · só-leitura · **nada adotado** · store `20be19aabe11`,
censo **144/205**, `form_limited` **1**.

Verificação §4.43 de duas coisas que a correção `db88dcd` poderia ter movido — e
que ninguém checou depois dela.

---

## 1. A pendência **P-8 opção 1** continua válida

O registro de 2026-08-06 (`lu2024_fig18_familia_tab8.md`) mede a família `fig18`
contra a **Tabela 8 impressa** e acha **4 de 5 desviando**, pior `amp2p0`
**+0,0792 em c10**. A recomendação — prereg único com extração de pixel — está
**não executada**, e a mesa marca a **P-8 opção 1** como pendente.

⚠️ **A correção do pico não a invalida, e o motivo é geométrico:** o artefato
estava em **N ≈ 77–84**, ou seja **entre as âncoras c50 e c100**. Ela só poderia
mover o **c100** — e das 5 da família, só **duas** foram tocadas (`amp0p5` e
`amp1p0`), ambas com c100 **já dentro da barra** (−0,0010 e −0,0057).

⇒ **as âncoras que carregam a evidência (c10 e c50) estão intactas.** A medição
de 08-06 se sustenta: a P-8 opção 1 segue aberta, com os mesmos números.

## 2. O piso de digitalização MUDOU — e a consequência é **inerte**

⚠️ Isto ninguém sinalizou: a `fig18_amp1p0` e a `fig20_T22Nm` são **as duas
metades do par do piso de digitalização** do `LU_2024` (são o **mesmo ensaio**
em duas figuras), e a correção tocou **as duas**.

O piso *é* a concordância delas ⇒ ele necessariamente mudou. Medido hoje:

| | valor |
|---|---:|
| piso `LU_2024` (MAE · res.máx · σ) | **0,0047 · 0,0165 · 0,0033** |
| famílias que o produzem | **1**, `δ=1 F=4627`, **n = 2** |
| `limite_sres(LU_2024)` | **0,0250** |

⇒ **a consequência é NULA**: o piso σ (0,0033) está **7,7× abaixo** do limite
global (0,025), então `max(0,025 ; piso)` continua devolvendo o global. Mover o
piso não move o limite enquanto ele estiver aí embaixo.

## 3. Por que registrar um resultado nulo

O hazard era **real**: corrigir as duas metades do par que define o piso é
exatamente o tipo de mudança que desloca um limite em silêncio. Verificá-lo
custou uma medição, e a resposta — *"mudou, e não importa, porque o piso está
7,7× abaixo do global"* — é o que impede a próxima pessoa de refazer a conta.

⚠️ E fica a condição sob a qual isso **deixaria** de ser inerte: se o piso do
`LU_2024` algum dia subir acima de **0,025**, a família `δ=1 F=4627` (n=2) passa
a **decidir** o limite da fonte inteira — e ela tem **duas curvas**, ambas
mexidas por correção de dado neste mês.

## Reprodutibilidade

`rh._pisos_medidos` e `rh.limite_sres` via `T.pisos_medidos` (helpers canônicos);
curvas tocadas lidas de `git show --stat db88dcd`; âncoras da Tabela 8 do
registro de 2026-08-06 — nenhuma reimplementada.
