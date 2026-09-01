# ROUSSEAU_2025 — as 4 abertas são do canal ROTACIONAL, e a rotação-por-slip que elas exigem varia **10× dentro do mesmo rig**

**2026-08-15 (noite)** · store `20be19aabe11` · sondas **só-leitura** (sandbox) ·
**nada adotado** · 10 células de `k_ratchet` (com e sem expoente de amplitude),
todas falsificadas como constante compartilhada.

## 1. A separação é por CANAL, não por material nem por espessura

| curva | estatuto | canal dominante | slip resolvido (1º→fim) | viés |
|---|---|---|---:|---:|
| `steel_t10` | ABERTA | **rotacional 83 %** | 0,023 → 0,043 mm | **+0,155** |
| `steel_t10_amp0p2` | ABERTA | **rotacional 72 %** | 0,191 → 0,198 mm | **+0,096** |
| `hdpe_t10` | ABERTA | **rotacional 72 %** | 0,249 → 0,444 mm | **+0,083** |
| `hdpe_t12` | ABERTA | **rotacional 72 %** | 0,154 → 0,377 mm | **+0,052** |
| `steel_t12` | tripé | rotacional 69 % | 0,008 → 0,023 mm | +0,002 |
| `steel_t14` | tripé | **stick** (emb 50 % + creep 50 %) | 0 | −0,020 |
| `hdpe_t14` | tripé | **stick** (emb 54 % + creep 45 %) | ~0 | −0,041 |
| `hdpe_t10_amp0p2` | tripé | **stick** (emb 59 % + creep 39 %) | ~0 | +0,025 |

**As 4 abertas são as 4 rotacional-dominadas com viés positivo**; as 3 em
**stick** passam. `|viés|/MAE` = 0,90–1,00 nas quatro ⇒ resíduo de sinal único,
**erro de NÍVEL**: falta perda, e ela falta no canal rotacional.

Dado limpo: σ_res é **4,7–14× o ruído** da própria curva ⇒ não é *data-limited*.

## 2. O que a sonda mostrou — e por que ela FALSIFICA a constante compartilhada

`k_ratchet` (rotação ∝ caminho de slip, Junker clássico) varrido no grupo:

| célula | `steel_t10` | `hdpe_t10` | `hdpe_t12` | `steel_amp0p2` | `steel_t12` |
|---|---:|---:|---:|---:|---:|
| **baseline** | 0,1548 | 0,0927 | 0,0566 | 0,0957 | 0,0104 |
| k=0,001 | 0,1088 | 0,2134 | 0,2444 | 0,2217 | 0,0090 |
| k=0,003 | **0,0576** | 0,2999 | 0,3428 | 0,3738 | 0,0210 |
| k=0,005 | 0,0683 | 0,3276 | 0,3711 | 0,4251 | 0,0383 |
| k=0,02 | 0,3172 | 0,3317 | 0,4330 | 0,5009 | 0,2569 |

A `steel_t10` melhora **63 %** (0,155 → 0,058) exatamente onde as outras três
pioram **3–7×** — e já na **menor** dose testada. O ótimo por curva é
**disjunto**: ≈0,003–0,005 para uma, **exatamente 0** para as outras três.

**A razão está medida, não suposta:** o ratchet é linear no caminho de slip, e
os slips do mesmo rig diferem **10×** (0,03 mm na `steel_t10` contra 0,44 mm na
`hdpe_t10`), enquanto o déficit de perda é **comparável** (+0,05 a +0,16). Logo
a rotação-por-unidade-de-slip que o dado exige é ~10× maior na curva de slip
baixo. Nenhuma constante por slip descreve as duas.

## 3. O expoente de amplitude também não resolve — e o motivo é um GOTCHA de engine

Tentativa dirigida (dar mais à curva de slip baixo): `loose_amp_exp < 1`, que a
documentação chama de resposta *sub-linear*. Medido:

| célula | `steel_t10` | `hdpe_t10` | `hdpe_t12` | `steel_amp0p2` |
|---|---:|---:|---:|---:|
| k=0,0005 exp=0,3 | **0,0507** | 0,1772 | 0,2230 | 0,2173 |
| k=0,0003 exp=0,2 | 0,0561 | 0,1307 | 0,1687 | 0,1551 |

Mesmo a célula **construída para o rácio de 10× medido** leva a `steel_t10` a
0,0507 (−67 %) e ainda piora as outras em **40–300 %**.

⚠️ **GOTCHA que isto expõe (vale para qualquer fonte):** o expoente age via
`slip·(slip/LOOSE_AMP_REF)^(exp−1)` com **`LOOSE_AMP_REF` = 5e-4 m = 0,5 mm**.
Quando **todos** os slips do rig estão **ABAIXO** da referência — o caso aqui
(0,03–0,44 mm) — `exp < 1` **AMPLIFICA** em vez de comprimir, e tanto mais
quanto MENOR o slip (fator 7,1× na `steel_t10` contra 1,09× na `hdpe_t10` em
exp=0,3). O parâmetro faz o **oposto** da sua intenção de projeto fora da
janela da referência; quem o usar num rig de slip pequeno tem de saber disso.

## 4. Veredicto

`ROUSSEAU_2025` ×4 = **transfer-limited** (mesma estrutura do `CHU_2026` ×6):
o modelo tem a **forma** (canal rotacional + ratchet cinemático), mas a
**constante não transfere dentro da própria fonte**. Adotar o ótimo por curva
seriam 4 constantes sem procedência — o que a doutrina (item D, ratificado
2026-08-13) proíbe. **Nada adotado; censo intacto em 143/205.**

## 5. Síntese com o achado do ICMEZ (mesma noite): os dois apontam o MESMO canal

| fonte | o que falta | evidência |
|---|---|---|
| `ICMEZ_2025` ×5 | taxa **sustentada sub-arresto** — o canal arresta num piso que o dado atravessa; a alternativa do engine é runaway | gate → **0,0000** medido no sítio; taxa tardia 0,18–0,26 vs 0,48–0,57 do dado |
| `ROUSSEAU_2025` ×4 | **dependência de slip** da rotação-por-slip (10× dentro do rig), inexprimível com a referência fixa de 0,5 mm | 10 células; ótimos disjuntos; sinal do expoente invertido abaixo da referência |

⇒ **a lei de taxa do canal rotacional é a lacuna estrutural que resta na
campanha**: ele sabe arrestar ou colapsar, e escala com o slip por uma
referência que não serve a rigs de slip pequeno. Nove das 21 curvas abertas
(43 %) estão nessas duas classes.

## 6. Reprodutibilidade

Sondas no scratchpad da sessão `3d12ac81` (instrumentação de
`resolve_transverse_slip`; grades de `k_ratchet` × `loose_amp_exp`). Sanidade:
célula vazia reproduz o store ao dígito em todas as rodadas.
