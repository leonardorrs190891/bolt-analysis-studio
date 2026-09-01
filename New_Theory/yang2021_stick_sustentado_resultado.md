# YANG_2021 — a fonte INTEIRA está em stick permanente, e a desculpa de scatter para a `r1` NÃO se sustenta

**2026-08-15 (noite)** · store `20be19aabe11` · sondas **só-leitura** ·
**nada adotado** · executa o critério que a assinatura de 19:57 exigia para o
**item E** (*"as 3 abertas só entram na classe depois de medida a classe
mecânica delas"*).

## 1. Classe mecânica: 8 de 8 em STICK

Instrumentando `resolve_transverse_slip` nas 8 curvas: **slip = 0 em 100 % dos
ciclos** em todas. Canais vivos: **embedding 54–83 % + creep 10–28 %**
(rotacional ≤10 %). ⇒ nenhuma alavanca de slip alcança esta fonte — regra de
classe da campanha.

## 2. As 3 abertas têm a assinatura das 2 JÁ assinadas

Resíduo médio por terço (`pred − dado`; **+** = modelo retém demais):

| curva | estatuto | início | meio | **fim** | σ/ruído |
|---|---|---:|---:|---:|---:|
| `amp0p5mm_ax8kN` | ABERTA | −0,005 | +0,019 | **+0,082** | 17,4 |
| `amp1p0mm_ax2kN` | ABERTA | +0,005 | +0,017 | **+0,074** | 8,8 |
| `amp0p6mm_ax8kN_r1` | ABERTA | +0,001 | −0,002 | **+0,045** | 8,3 |
| `amp0p8mm_ax6kN` | **EXC** (assinada) | +0,016 | +0,037 | **+0,122** | 8,9 |
| `fig2_typical` | **EXC** (assinada) | +0,001 | +0,016 | **+0,104** | 18,2 |
| as 3 no tripé | — | −0,011…−0,038 | −0,026…−0,055 | −0,007…−0,052 | 3,7–6,7 |

Mesma forma nas 5: resíduo ~0 no início e **crescendo até o fim** — o dado
segue perdendo pré-carga **sob stick** e o modelo não acompanha. Dado limpo
(σ_res é **8–17×** o ruído da própria curva).

## 3. A rota existe nesta fonte — e ela TROCA, não ganha

A forma de stick (`gth`) **já está adotada aqui** (`gth_k = 1,5e-7`). Varrida:

| célula | tripé | alvo fecham | protegidas |
|---|---:|---:|---:|
| baseline (1,5e-7) | 3/8 | 0/3 | 3/3 |
| **5e-7** | **3/8** | **2/3** | **1/3** |
| 2e-6 · 1e-5 · 2e-6+q2,5 · 2e-6+A0 | 0/8 | 0/3 | 0/3 |

Em `5e-7` fecham 2 abertas **e quebram 2 protegidas** — **net zero**. Acima
disso, colapso (MAE ×5 a ×22). 6 células.

## 4. ⚠️ A desculpa que estava disponível — e que a medição RECUSA

A `r1` falha só o σ, por **7 %** (0,0268 vs 0,0250), e tem **duas réplicas
irmãs** (`r2`, `r3`) da MESMA condição — o cenário clássico de *scatter*. Se a
discordância entre réplicas fosse da ordem do erro do modelo, a curva seria
exceção F5 por prova de piso. **Medido (dado × dado, janela comum):**

| par | MAE | **σ** |
|---|---:|---:|
| r1 × r2 | 0,0328 | **0,0129** |
| r1 × r3 | 0,0523 | **0,0099** |
| r2 × r3 | 0,0173 | 0,0049 |
| **modelo × r1** | 0,0167 | **0,0268** |

⇒ o modelo está **2,1× FORA** da discordância que as próprias réplicas têm
entre si. **A `r1` NÃO é scatter-bound** — o erro de forma é real e maior que a
dispersão do dado. (Curiosidade que reforça: o modelo tem o **melhor MAE** com
a `r1` das três — está centrado nela em NÍVEL e errado em FORMA; com `r2`/`r3`
é o inverso.)

## 5. Veredicto

As 3 abertas do `YANG_2021` são **form-limited com a forma nomeada**: *perda
sustentada sob stick com a FORMA certa* — a de nível já existe (`gth`) e a
fonte prova que uma constante não serve às suas próprias réplicas.
**NÃO assinadas como exceção**, pelo mesmo critério dos itens Q e R: exceção é
para curva sem rota, e aqui a rota está nomeada. Censo **inalterado (143/205)**.

## 6. Síntese: TRÊS fontes, o mesmo padrão

| fonte | classe | forma existente | por que não fecha |
|---|---|---|---|
| `ICMEZ_2025` ×5 | gross × parcial | taxa residual sub-arresto (construída hoje) | os 2 grips estão em **regimes de slip diferentes**; constante escalar move os dois |
| `ROUSSEAU_2025` ×4 | rotacional | `k_ratchet` | rotação-por-slip exigida varia **10×** dentro do rig |
| `YANG_2021` ×3 | stick | `gth` | fecha 2 e quebra 2 **réplicas da mesma condição** |

⇒ em três fontes independentes o obstáculo tem a **mesma estrutura**: a forma
existe, e **uma constante compartilhada não serve à própria fonte**. Isso é
uma afirmação sobre a **lei de taxa** (como o mecanismo escala com regime,
slip e história), não sobre magnitudes.

## 7. Reprodutibilidade

Sondas no scratchpad da sessão `3d12ac81` (instrumentação de
`resolve_transverse_slip`; varredura `gth`; comparação réplica × réplica por
interpolação na janela comum). Sanidade: célula vazia reproduz o store.
