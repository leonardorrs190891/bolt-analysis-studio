# ESTUDO DO CASO — `zhang2006_fig3_illus_M12x125_20kN_amp0p35`

**2026-08-20 (13:3x–13:5x)** · pedido do professor: *"faça um estudo do caso"*.
Só-leitura + sondas sandbox (`BAS_ADOPTED_CONFIGS`); nada adotado. Store
`df35fd990380`.

## 1. Identidade e estatuto

| item | valor |
|---|---|
| fonte | ZHANG_2006 (Zhang, Jiang & Lee, *J. Press. Vessel Tech.* 128(3), 2006 — DOI 10.1115/1.2217972) |
| figura | **Fig. 3, rotulada "Illustration of self-loosening process"** |
| condições nominais | rig ANTERIOR dos autores (Jiang 2003/2004): M12×1,25 · 75 mm · P₀ = 20 kN · δ/2 = 0,35 mm · INSTRON, disp-mode |
| dado | 41 pts digitalizados (±0,5 % F/F₀), x = 1→19 700 (log), y = 0,995→**0,012** (afrouxamento total; terminal 0,012→0,028 é **end-hook desenhado** = ruído de célula em P≈0, "kept as drawn") |
| métricas | 0,2110 / 0,6608 / 0,2215 (4,2× / 6,6× / 8,9× — a 3ª pior comparável do store) |
| estatuto | **DECLARADA (proveniência)** desde 2026-07-31 |

## 2. Anatomia do dado — quatro atos

1. **Settling** (N = 1–191): 1,000→0,874, suave. O modelo acompanha (res ±0,03).
2. **Degrau** (N ≈ 200–900): 0,874→0,498 — o processo rotacional dispara.
   O modelo segue quase parado (0,866→0,840): o resíduo abre +0,08→+0,34.
3. **Platô log-linear** (N ≈ 900–10 600): 0,498→0,319, taxa lenta por **uma
   década de ciclos**.
4. **2º colapso** (N = 14 400–15 100 na janela): 0,319→0,136 (o CSV cru segue
   até 0,012).

## 3. Por que o modelo erra — medido, não estimado

- **Classe mecânica instrumentada** (wrapper em `resolve_transverse_slip`):
  **STICK TOTAL — 0 de 30 200 ciclos com slip > 0.** A perda inteira do modelo
  é embedding (0,049) + creep (0,172); wear/rotacional/fretting = 0 exato.
  ⇒ **o canal que a figura ilustra (afrouxamento rotacional) nunca engata.**
- Causa da trava: a config adotada da fonte (`c_bend = 0,05`, saturado no
  piso; `emb_um` 1,58; `C_creep` lidos) foi **lida da fig16 — o caso NULO**
  (Combination I, 40 kN, 0,125 mm, θ≈0, sem afrouxamento), que fecha no tripé
  (0,0124/0,0240/0,0086). O mesmo `c_bend` que acerta o rig em stick trava a
  fig3, que roda a **2,7× o limiar de amplitude** do rig anterior (0,13 mm).

## 4. Sondas de capacidade (sandbox, 9 células — NÃO adotadas)

| sonda | resultado |
|---|---|
| `c_bend` 1,0/5,0/30,0 (destravar slip) | **piora**: 0,2165/0,2595/0,2660 — sem incubação o canal dispara em N=1 e erra o settling |
| + `slip_onset_W` 500/2000/8000 + floor 0 | melhor **0,1489** (W=2000): o degrau MOVE (cruza-0,5 em 656/1657/4186 vs ~894 do dado) mas o cruza-0,9 fica preso em **76** (emb+creep drenam 10 % antes do gate) e o fim vai a **0,000** (runaway) contra 0,136 |

**A forma de 4 atos não é reproduzível pelas formas atuais**: o engine faz
settling→colapso→arresto (ou runaway), mas o dado **desacelera no meio da
vida** (ato 3) e **re-colapsa** no fim (ato 4). Para segurar o ato 3 seria
preciso µ_thread crescendo com P caindo — mecanismo que o paper atribui ao
rig NOVO; o par do rig anterior tem µ ~constante (µ_th ≈ 0,11), o que torna a
desaceleração de meio-vida fisicamente estranha *nas próprias condições
declaradas da figura*.

## 5. A pista da curva-mãe — testada e não confirmada

A nota de aparato registra *"possible overlap with 02_Jiang_2003_2004
extracted curves"*. **Testado por RMS de atribuição** (o instrumento do D-R)
contra as 7 curvas Jiang da biblioteca: nenhum match — são "early stage"
(janelas ≤ 500 ciclos) de amplitudes 0,254–1,27 mm (a 0,35 não existe entre
elas), melhor RMS 0,098 (ruim). **A curva-mãe real da Fig. 3 — se existe no
Jiang 2003/2004 — não está na biblioteca.**

## 6. Veredicto

A declaração de proveniência **se sustenta e sai REFORÇADA** por dois
argumentos novos, ambos medidos:

1. **Não-rastreabilidade**: a curva não casa com nenhum dado do estudo
   anterior disponível; o rótulo "Illustration" + end-hook desenhado + eixo
   idealizado ficam como única proveniência.
2. **Forma anômala**: a desaceleração de meio-vida (ato 3) contradiz a
   dinâmica de runaway do próprio par de atrito declarado — consistente com
   um **desenho didático dos estágios do processo**, cada um esticado para
   legibilidade em eixo log.

**Rota única legítima**: obter o PDF do Jiang 2003/2004 (Papers A/B citados
na nota) e procurar a curva REAL da condição 20 kN/0,35 mm. Se existir: a
curva-mãe entra na biblioteca com proveniência plena e a fig3 vira duplicata
(sai do censo, `_CID_NAO_COMPARAVEL`, precedente fig18_amp1p0≡fig20_T22Nm).
Se não existir: a fig3 permanece declarada — fechá-la exigiria ≥3 constantes
fitadas por curva contra um desenho (bloqueado pelo item D, e sem valor de
validação).

**Subproduto de capacidade** (para o artigo/roadmap): a assinatura
"incubação → colapso → desaceleração de meio-vida → colapso final" é a forma
de µ crescente-com-P-caindo (arresto por atrito) que o engine NÃO tem — o
`mu_kinetic_frac` (dormente) modela a direção OPOSTA (µ cai ao romper). Se
uma fonte com dado REAL exibir o ato 3 (candidata natural: as curvas do rig
NOVO do próprio ZHANG_2006, fig12, e o mecanismo de arresto descrito no
paper), a forma candidata é µ_thread(P) crescente — observável na Fig. 14/15
do paper (µ_th ∝ 1/P medido). Hoje nenhuma curva do censo exige isso.

---

## §7 ERRATA E REANÁLISE (mesma tarde, 13:50–14:1x) — a leitura do professor muda o quadro

O professor apontou (*"a curva claramente tem 2 estágios"*, PDF conferido por
hash = o MESMO da biblioteca) e o TEXTO do paper confirma: *"a typical
self-loosening process... can be divided into **two distinct stages** (Fig.
3). On the first stage, a gradual relaxation of initial preload occurs
**without nut rotation**. Stage II is characterized by the obvious **backoff
of the nut**"* — com demarcação publicada **θ = 0,5°** e término do Estágio
II em **P = 25 %·P₀**. Corrige a minha leitura de "4 atos": tudo após
N≈160 é UM Estágio II rotacional de taxa variável.

**Descoberta ao rasterizar a figura: ela tem DOIS traços — P e θ(N) — e o θ
nunca foi digitalizado.** O θ arranca em N≈200, tem patamar em 2×10³–10⁴ e
dispara junto do colapso final de P. A correlação P↔θ coerente por 4 décadas
**enfraquece o meu argumento de "forma anômala"** (§6.2): a desaceleração de
meio-vida está no θ também — isto se parece com DADO REAL do rig anterior
usado como figura didática. O argumento §6.1 (não-rastreabilidade) fica.

**Regressão com o onset lido**: P-13 closed-form no Estágio II com N₀=160
(lido da demarcação desenhada): fe=5,93 · K=0,0074 · **r²=0,9866** (sem o
onset: 0,9136 — o onset lido MELHORA, confirmando os 2 estágios).

**Arco de sondas no engine (4 eixos varridos, célula final):**

| passo | célula | resultado |
|---|---|---|
| baseline (config da fonte, lida da fig16 NULA) | stick total | 0,2110/0,6608/0,2215 |
| graded fe/K regredidos + c_bend 1,0 | sem incubação | 0,1001/0,3004/0,0966 — cruza-0,5 em 894 = o do dado |
| + slip_onset_W (incubação) | mx no dreno tardio | ~0,075/0,30/0,10 — grade (fe,K) SATURA |
| **discriminante: wear OFF** (`k_wear_spec=0 · K_archard=0`) | o dreno tardio ERA o wear | 0,0569/0,2076/0,0571, mx muda para o penhasco final |
| re-fit (fe,K,W) sem wear | **melhor célula: fe=4,25 · K=0,005 · W=200 · c_bend=1,0** | **0,0317/0,0877/0,0385 — MAE e res.máx FECHAM; σ 1,54× SATURADO** (insensível a fe/K/W/c_bend nos 4 eixos) |

Leituras que sustentam a célula: floor=0 (o dado afrouxa total — leitura),
wear OFF (o Estágio II do paper é *backoff da porca*, não desgaste — leitura
do texto), N_onset≈160 (âncora qualitativa da demarcação desenhada).
**Contagem honesta de fitados: 4 por curva** (c_bend 1,0 · fe 4,25 · K 0,005
· W 200) — a regressão-mãe (fe=5,93) não sobrevive à composição de canais do
engine, então fe/K são fitados, não lidos.

## §8 Veredicto revisado

1. O erro da fig3 caiu **6,6×/7,5×/5,8×** com a leitura de 2 estágios — MAE
   e res.máx FECHAM; o σ satura em 0,0385 (curvatura residual da transição).
2. A curva **continua DECLARADA por proveniência** (o rótulo "Illustration" é
   do paper; a não-rastreabilidade à curva-mãe permanece — o overlap com as
   Jiang extraídas foi testado e não existe) e **não entraria no censo nem
   fechando** (σ 1,54×).
3. **NÃO ADOTADO** (decisão desta sessão, coerente com o item D): 4 fitados
   por curva sem âncora, em curva fora do censo. O per_case candidato fica
   REGISTRADO aqui; adotá-lo como *caso didático fora-do-censo* (o report/
   galeria mostrariam o modelo reproduzindo os 2 estágios canônicos da
   literatura) é opção de MESA — gates prontos: G1 célula ao dígito · G2
   fig16/fig12 bit-idênticas (token `fig3`) · G3 isolamento no re-stamp.
4. **Trabalho de dado que a figura pede**: digitalizar o traço θ(N) (nunca
   foi) — com a demarcação θ=0,5° e o fim em P=25 % ele é o observável que
   transformaria fe/K/W de fitados em lidos/regredidos (a estrutura §4.56
   dos ROUSSEAU). É a rota para a adoção com procedência plena, se a mesa a
   quiser.

---

## §9 A ROTA ROBUSTA EXECUTADA (mesma tarde, 14:0x–14:2x) — o θ digitalizado e as leituras

Mandato: *"faça da maneira mais robusta"*. O traço θ foi digitalizado do
raster embutido (script versionado `digitize_zhang_fig3_theta.py`; tracking
por continuidade; **826/827 colunas**; P validado contra a CSV canônica nas
3 âncoras). CSV em `curve_library/anchors_csv/zhang2006_fig3_theta_trace.csv`
(entrada no ANCHORS_CSV_MANIFEST com a incerteza de escala declarada: a
figura NÃO rotula o eixo θ; âncora única θ(demarcação)=0,5° ⇒ ±30 %).

**As leituras:**

| leitura | valor | procedência |
|---|---|---|
| N_onset | **161** | a linha de demarcação DESENHADA (px 560) — exato |
| dF/dθ | **698 N/deg** (r²=0,982, n=193) | paramétrico P×θ no trecho 300–3000 — a classe dos ROUSSEAU aço (920/894, §4.56); herda ±30 % da escala |
| **lei de taxa** | **dθ/dN ∝ F^fe com fe = 5,80** (r²=0,74) | do traço θ, **INDEPENDENTE da escala** — e CONCORDANTE com a regressão do P puro (5,93, r²=0,99): duas leituras independentes, mesma lei |
| patamar de θ | ~10° antes do disparo; **disparo final 10°→42°** | o 2º regime |

**O veredito da rota robusta:** com fe LIDO (5,80) e K varrido, o MAE fecha
(0,0288) mas o res.máx trava em **1,37×** no penhasco final — o disparo
(θ 10→42°) é um **segundo regime, runaway de porca solta**, que a lei F^fe
não cobre por construção (ela DESACELERA com F caindo; o disparo ACELERA).
O fe=4,25 fitado de §7 "comprava" o fim às custas da fidelidade à lei — com
a lei lida, a lacuna aparece onde ela é: **forma faltante "transição
lei-de-potência → runaway"**, agora comprovada com constantes lidas de dois
traços concordantes. O engine tem cada metade (graded desacelerante; runaway
bolt_torsion) mas são modos EXCLUSIVOS de `loose_rate_mode` — a transição
não é componível hoje.

**Estatuto final:** a curva segue DECLARADA (proveniência) e NÃO fecha o
tripé nem com leitura plena — a declaração está agora sustentada pela
versão mais forte possível do argumento: *não é falta de fit, é forma
faltante medida*. A forma "transição desacelerante→runaway" entra no mapa
de candidatas com dois observáveis (o N do disparo ≈ 1,3–1,5×10⁴ e a razão
de taxas ~14×) — e o candidato natural a segunda evidência é a classe de
aceleração tardia (bauer test1, fig14_long), que tem a MESMA assinatura de
re-aceleração. Se a mesa quiser a forma, ela paga-se em ≥2 fontes.

---

## §10 A FORMA NO ENGINE (15:0x — mandato "forma na engine") e a adoção didática

O professor autorizou a forma no mesmo minuto em que o §9 a provou. Ela
existe: **`loose_runaway_{frac,gain,sharpness}`** — boost Hill
`1 + gain·fc^k/(fc^k + r^k)` sobre `d_theta` do ramo graded, r = F₀/F₀_init.
Física: perda do auto-travamento residual abaixo de r_c. É o **espelho do
`crash_trigger`** (que suprime antes do gatilho): aqui a taxa do meio fica
INTACTA e só o fim dispara. Default frac=0 OU gain=0 = OFF exato
(`tests/test_loose_runaway.py`, 5 invariantes: bit-idêntico, gain-zero OFF,
dispara-abaixo/quase-inerte-acima, monotonia, inerte-no-kernel-torque).

**Com a forma, a célula LIDA PURA fecha MAE e res.máx** (o §9 travava em
1,37× de mx com a lei lida): fe=5,80 (θ) · frac=0,25 (definição do paper) ·
gain=13 (razão de taxas) · sharpness default · W ancorado no onset · wear
OFF (texto) · floor 0 — 2 fitados (c_bend 1,0; K 0,009, dentro da banda
±30 % da escala do θ) ⇒ **0,2110/0,6608/0,2215 → 0,0320/0,0875/0,0390**.
σ 1,56× = piso da curva (6 eixos varridos; sharpness fitado só melhora
0,0390→0,0350 e não fecha — recusado, não vale 1 fitado).

**ADOTADA como caso didático fora-do-censo** (prereg
`2026-08-20-zhang-fig3-runaway`, gates 6/6): a curva SEGUE DECLARADA por
proveniência e o censo fica em 162/205 por construção; o que muda é o
report/galeria — o modelo agora reproduz os 2 estágios canônicos da
literatura com constantes lidas do traço θ. Store `25be50adbc05`,
isolamento exato (só a fig3 no diferencial), fig16 bit-idêntica.
