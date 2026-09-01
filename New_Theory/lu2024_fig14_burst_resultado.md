# ATAQUE à `lu2024_M8_fig14_amp1p0_long` — melhora 10× no MAE, e a forma que falta ganhou nome e 2 instâncias

**2026-08-20 (23:0x–23:3x)** · mandato: *"ataque... em loop, validando tudo e
assinando tudo"*. Sondas em sandbox (`BAS_ADOPTED_CONFIGS`); **NADA adotado**
— o fecho não veio e o registro honesto é o produto. Store `245dc93087d1`.

## 1. Anatomia (a pior declarada restante: 0,4802/0,8553/0,2894)

O dado (fig14 = half-sine de MÁQUINA, corrida longa): **platô a 0,96 por 54
ciclos → colapso abrupto (0,958→0,537 em ~5 ciclos, pico 0,14/ciclo) → cauda
desacelerante até 0,003**. O modelo atual despenca imediatamente (0,50 em
x=6) e trava no floor. max|Δdado| na janela = 0,14 < 0,25 ⇒ **pontuável**
(não é metric-limited).

## 2. O arco de sondas (7 rodadas, 4 kernels/composições)

| passo | achado |
|---|---|
| incubação (`slip_onset_W`) | o platô EXISTE a 1,0 mm (slip pleno ⇒ W acumula — diferente do stick da amp0p25) e o onset é ancorável |
| discriminante do dreno do platô | quem drenava 23 % era o **bedding fracional** (`emb_load_frac=0,4` do grupo — calibrado no settling de 36 % do protocolo MANUAL; a fig14 de máquina assenta 3 %). **O item F aparece DENTRO da config**: per_case `emb_load_frac=0` + emb_um≈1 lido do settling ⇒ platô a −0,01 do dado |
| avalanche por ratchet/tr_gain amplificados | EXPLODEM o mx (0,35–0,96) — amplificação uniforme não faz burst-e-cauda |
| kernel graded fe=1,24 (lido da cauda) | **a cauda casa** (res −0,01 no fim) e o onset é regulável por W; melhor célula **(W=310 · k=0,06 · fe=1,24 · sh=40 · frac=0 · emb=1,0): 0,0458/0,2407/0,0665** — MAE FECHA; mx 2,4× e σ 2,7× ficam no BURST |

## 3. O teto — e a forma faltante nomeada

O burst não é potência única de F (fe implícito varia 2,9→0,6 ao longo da
descida): é **LIBERAÇÃO DA ENERGIA INCUBADA na ruptura do travamento** —
burst intenso e limitado, depois taxa desacelerante. Nenhum kernel atual
compõe platô+burst+cauda: amplificar a avalanche vaza o platô (o Hill deixa
passar fração×avalanche) e o graded que acerta a cauda não faz o pico.

**2 instâncias na MESMA fonte** (medido): a irmã `amp0p5_long` tem o mesmo
perfil — platô (0,98 até ~22) → burst (→0,50 em ~20 ciclos) → re-platô
(taxa 0,0015/c) → 2ª descida. E o observável forte: **as duas drenam o burst
até ~0,50–0,54 de F₀** — fração ~fixa liberada, como transição de estado
bi-estável da interface. Observáveis por curva: N_onset (55 vs 25), fundo do
burst (~0,5 F₀), taxa de pico (0,14 vs ~0,08/c).

Parentes conceituais já medidos: o `mu_kinetic_frac` (dormente) dá avalanche
DEMAIS (falsificado no yang2019 — 6 estruturas); o `loose_runaway_*` dispara
abaixo de r_c (o burst daqui começa em F ALTO). A forma candidata é um
**knockdown único de fração lida (~0,5) disparado pelo onset do W**, com o
graded fe assumindo a cauda — 3ª instância da classe transição-entre-regimes
(fig3 runaway · bauer fração-de-espectro · fig14 burst-de-ruptura).

## 4. Estatuto

A curva **segue DECLARADA** (órfã de protocolo — item F). O pacote candidato
(6 números, 3 lidos/ancorados) fica registrado AQUI, não adotado: melhoria
sem fecho em curva declarada não entra no canônico (precedente fig3 foi caso
didático por pedido explícito; esta não tem o mesmo valor de galeria). Se a
mesa quiser a forma burst-de-ruptura no engine, ela se paga nas 2 fig14_long
+ eventual reuso na classe de aceleração tardia.
