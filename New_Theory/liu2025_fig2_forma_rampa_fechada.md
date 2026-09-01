# `liu2025_M16_fig2_single` (alvo 2, 1,08×) — a direção EXISTE, e morre por procedência

**2026-08-19** · store `7a60cacb72de`, censo 144/205 · sondas **só-leitura**
(C1 re-ancorado por bisseção a cada célula — lição D-Z, forma e nível juntos) ·
**nada adotado** · sequência de ataque, alvo 2.

## 1. O que fiz de diferente do diagnóstico anterior

`liu2025_par_de_taxas_opostas.md` nomeou o déficit (taxa de fadiga, ρ=+0,97,
90 % do incremento tardio) e varreu as **8 alavancas livres** — mas as `fat_*`
**não são alavancas livres** (não estão em `V2_PARAM_NAMES`) e ficaram fora.
Sondei exatamente elas, com o cuidado que a D-Z ensinou: cada forma `(D_on, q)`
com o **C1 re-bisseccionado** para manter `D(N_frat)=1` na vida do espécime.

**Antes disso, o input foi conferido e está certo:** cada réplica usa `fat_C1`
próprio (fig2: 3,84e32 ancorado na vida 9780; amp0p8: 5,23e32 na vida ~14000).
Não há herança de token errada.

## 2. A varredura — a direção existe, é estreita, e não fecha

| (D_on, q) | C1 ancorado | MAE | res.máx | σ_res | ρ(res,N) |
|---|---:|---:|---:|---:|---:|
| baseline (0,75, 8) | 3,84e32 | 0,0279 | 0,0579 | 0,0270 | +0,97 |
| (0,75, 8) re-ancorado | 3,72e32 | 0,0278 | 0,0577 | 0,0268 | +0,96 |
| **(0,60, 8)** | 3,58e32 | **0,0250** | 0,0575 | **0,0262** | +0,76 |
| (0,50, 4) | 3,14e32 | 0,0512 | **0,3714** | 0,0983 | +0,23 |
| (0,50, 2) | 2,70e32 | 0,0856 | 0,5318 | 0,1625 | −0,02 |
| (0,35, 2) | 2,45e32 | 0,0999 | 0,5703 | 0,1833 | −0,11 |

- Ligar a rampa mais cedo (`D_on` 0,75→0,60) melhora **as três pernas** e
  derruba o ρ — a direção do déficit está certa.
- Mas o melhor ponto ainda dá σ **0,0262 = 1,05×**, e o próximo passo
  (0,60→0,50) **explode** (σ 0,0983, res.máx 0,3714). A janela útil é um fio
  de navalha — e célula de navalha é o que o D-L manda recusar.

## 3. Por que a rota morre: o joelho MEDIDO da fig2 aponta na direção CONTRÁRIA

`D_on` tem procedência handbook: *"N_D (joelho) sempre a 72–80 % da vida"*.
Medi o joelho de cada curva da fonte com **um único critério** (máxima
distância à corda, até N_f):

| curva | N_f | N_D | N_D/N_f |
|---|---:|---:|---:|
| amp0p4 | 76 000 | 66 000 | 0,87 |
| amp0p5 | 38 000 | 33 000 | 0,87 |
| amp0p6 | 23 800 | 20 000 | 0,84 |
| amp0p8 | 14 000 | 11 500 | 0,82 |
| **fig2_single** | 9 780 | 8 729 | **0,89** |

O joelho da fig2 é o **mais tardio** da fonte, não o mais cedo. Adotar
`D_on=0,60` para ela seria mover a constante **contra o dado do próprio
espécime** e contra o handbook, para ganhar 3 % de σ — fit sem procedência,
duas vezes (item D + navalha).

## 4. Achado colateral que ecoa o alvo 1

As "réplicas" da condição 0,8 mm/24 kN morrem em **9 870 e 14 400** ciclos —
**46 % de dispersão de vida**, pior que os 15–25 % do YANG_2021. É a mesma
estrutura do alvo 1: espécimes da mesma condição divergem na cauda, e o piso σ
da condição (0,0149), medido na janela comum, não carrega essa dispersão.

**Duas fontes independentes, o mesmo fenômeno**: a dispersão de VIDA entre
espécimes não aparece no piso de σ, porque o piso é medido onde as curvas ainda
coexistem. Se um dia isso virar régua (piso que reconheça dispersão de vida na
cauda), é decisão do professor — registro a evidência, não proponho a régua.

## 5. Estado da curva

`fig2_single` fica **aberta e sem rota com procedência**: F7 fechada (σ 1,81× o
piso do par), input conferido e certo, forma da rampa fechada por procedência
(§3), alavancas livres já varridas (doc anterior). O déficit nomeado (ρ=+0,97 —
o modelo perde devagar demais **antes** do joelho) continua verdadeiro e sem
alavanca legítima que o alcance.

## 6. Reprodutibilidade

Sonda no scratchpad da sessão (bisseção de C1 por célula em janela cheia,
métrica na janela canônica; `FLOOR_TRIM` restaurado). Joelhos: kneedle sobre o
CSV cru, critério único para as 5 curvas que zeram.
