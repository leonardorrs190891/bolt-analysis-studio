# Ataque das 9 abertas (2026-08-20, "ataque as 9 abertas em loop") — 1 forma nova, 0 fechamentos: este é o núcleo duro de verdade

**2026-08-20 (08:2x–09:4x)** · mandato: *"ataque as 9 abertas em loop. ao final
atualize o validation report, e refaça o censo"* · sondas sandbox + 1
capacidade nova (TDD 3/3) · **nada adotado** (o ganho da melhor rota piora uma
perna) · censo segue **156/205**.

## O resultado por curva

| # | curva | pior perna | o que o ataque mediu |
|---|---|---:|---|
| 1 | `yang2019_M10_amp0p4_5Hz` | 3,05× | **o maior avanço do dia** — ver §2. Forma nova `gth_accel_p` construída; o pacote lido entrega ±0,014 até N=9000 (90 % da janela) e o modelo ALCANÇA a transição stick→slip em F=0,916 — exatamente onde o dado acelera — mas RE-TRAVA num equilíbrio espúrio (dF=0,000 exato) onde o dado real colapsa sem volta. Ganho não-adotável: mx piora (0,141→0,188). Falta: **histerese de transição** |
| 2-4 | `yang2023 0,30/0,35/0,50` | 2,4–4,8× | ⚠️ meu registro de 19/08 ("0,30 declarada mantida") estava ERRADO — a declaração fora retratada em 07/08 (P-10). Re-medidas: o decay é **EXPONENCIAL** (dF/dN ∝ F, τ=170/250/13) = assinatura do kernel de TORQUE — que **não dispara** nelas (ratchet=0 ⇒ F_fim 0,94–1,17!); o `k_ratchet` vigente (∝slip) tem forma OPOSTA (acelera onde o dado desacelera) — daí os "3 sinais". Sem leitura para o disparo (IJPEM sem rotação publicada) |
| 5 | `yang2021_r1` | 1,07× | sem rota POR CONSTRUÇÃO: modelo determinístico não separa réplicas de inputs idênticos; piso σ do trio (0,0103) não cobre (2,6×) — decidido 08:1x |
| 6-7 | `yang2021_amp0p5/amp1p0` | 1,55×/1,28× | dossiê de 19/08 mantido (dispersão de espécime; sem observável de rotação na fonte) |
| 8 | `liu2025_fig2_single` | 1,08× | rota D_on morta por procedência (joelho medido do espécime = 0,89 da vida) — dossiê de 19/08 |
| 9 | `liu2025_amp0p8` | 1,68× | 8 alavancas 0/8 (dossiê 19/08) |

## §2 — O avanço na yang2019_amp0p4, e a forma que ficou nomeada

O dado re-lido: **PLATÔ até N≈4700 (1,000–1,004 — até sobe!) + aceleração
progressiva** (taxa 11,6× para N-efetivo 3,8× ⇒ p≈2–2,9). Nenhum canal do
engine acelera em stick (o damage não cresce: driver é slip macro — medido
D=0,000 com os starters físicos).

**Capacidade construída:** `gth_accel_p` (default 0 = OFF exato, TDD 3/3 em
`test_gth_accel.py`): pós-onset `d_theta ∝ ((A_gth−A0)/A0)^p`. Leituras da
curva: A0=2009 (onset), k=7,19e-5, p=2,87 (LSQ na INTEGRAL F(N), r²=0,969 —
a derivada com 6 pontos é ruidosa demais, r²=0,60).

**O que o pacote revelou:** com emb=creep=0 (lidos do platô publicado de 4000
ciclos) o modelo segue o dado a ±0,014 até N=9000 e a **transição stick→slip
do engine ocorre em F=0,916·F₀ — o joelho real do dado**. Mas o sistema
re-trava (o slip abre a 4e-8 m em 13 % dos ciclos, o gth desliga por
construção, os macro não pegam o bastão e dF vira 0,000 exato). O dado, com o
travamento físico rompido, colapsa. ⇒ a forma que falta é **histerese da
transição** (uma vez rompido, não re-trava) — candidata de engine para o
próximo arco, com o observável de leitura já identificado (o joelho em
F/F₀=0,92 e a taxa terminal).

## §3 — Leitura estratégica

As 9 são o núcleo duro REAL: 5 têm teto de dado (dispersão de espécime,
resolução) e 4 têm formas nomeadas com precisão de leitura mas sem observável
para as constantes (histerese; disparo do torque). Nenhum fechamento hoje —
e é o resultado certo: as rotas de leitura de ontem fecharam tudo o que tinha
observável publicado. O que resta exige: PDF/observável novo (YANG_2023),
forma de histerese (YANG_2019), ou é irredutível por construção (réplicas).

## Reprodutibilidade

Sondas no scratchpad da sessão (`yang2019_gth_leituras.txt` etc.);
`test_gth_accel.py` 3/3; guardas de censo 7/7; VarSpec do campo novo
(cobertura 119/119).
