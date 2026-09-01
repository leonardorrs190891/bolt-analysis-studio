# ROTAS para as 18 DECLARADAS — mapa medido curva a curva

**2026-08-20 (12:0x–12:5x)** · mandato: *"conseguimos atacar os 12 casos
declarados, individualmente?"* + *"continue, gere rotas"*. O "12" era o censo
de 2026-07-30; hoje são **18** (a retratação LU-protocolo de 08-14 somou 7
órfãs). Todas medidas nesta sessão contra o dado CRU (`load_full_curve`,
nunca `metric_data`) — floors lidos com `arrest_floor_from_curve`, regressões
de expoente em log-log, grades sandbox via `BAS_ADOPTED_CONFIGS`.

Princípio que decidiu (o mesmo dos 16 fechamentos de 08-19/20): **onde há
observável publicado para ler, a curva fecha; onde a rota exigiria fit puro
por curva, ela fica** — e cada linha abaixo diz qual é qual.

## A. EXECUTADAS HOJE (4 ataques, 3 preregs)

| curva | rota | resultado |
|---|---|---|
| `fig20_T28Nm` | floor **0,2414 LIDO** (leitor canônico; terminal PUBLICADO Tabela 9 = 0,234, p.19 "3523 N" — 3,2 % de coincidência, classe da T10) + aexp 1,4 fitado-declarado (região 9 células; regressão tentada deu r² 0,515 = não suporta leitura, registrado) | **FECHA** 0,1008/0,1969/0,0862 → **0,0338/0,0649/0,0181**. Prereg `lu2024-t28-piso-lido`. 1ª órfã de protocolo a sair por mérito |
| `IJPEM 0_45_mm` | o "colapso Δ>0,25" é **passo de amostragem** (x salta 20→50), não parede — o closed-form P-13 cruza os pontos crus a res.máx 0,011; pacote das irmãs (graded + fe/K), região 11/12 células | **FECHA** 0,1042/0,3600/0,1344 → **0,0102/0,0154/0,0115**. Prereg `ijpem-045-055-p13` |
| `IJPEM 0_55_mm` | idem (0,013 no closed-form; 12/12 células) | **MAE+mx fecham** (0,0085/0,0248); σ não-julgável (FLOOR_TRIM come o 6º ponto ⇒ n=5) ⇒ **re-motivada para n<6** como a irmã 0_50 — estatuto certo, censo inalterado |
| `fig18_amp1p5` | **aexp 1,864 REGREDIDO DO DADO** (log-log da taxa vs excesso sobre o floor 0,10 do grupo: slope 1,864, r²=0,685, n=8 — o valor cai DENTRO da região que fecha 1,5–3,0). Floor do grupo intocado. Falsificação preservada: floor lido 0,0176 PIORA (destrava o colapso) — a alavanca era a FORMA da chegada, não o nível | **FECHA** 0,0314/0,0742/0,0353 → **0,0139/0,0393/0,0157**. Prereg `lu2024-amp1p5-aexp-regredido` |

Censo projetado dos 4: tripé 159 → **162** · declaradas 18 → **15**.

## B. ROTA NOMEADA, 2ª ONDA (3 — cada uma com sonda/decisão específica)

**`fig14_amp0p25_long`** — ✅ **FECHOU em 2026-08-21 (prereg
lu2024-amp0p25-emb-lido) com pacote de LEITURA QUASE PURA (zero fitados)**,
e o diagnóstico desta seção estava ERRADO (a 4ª errata do mapa): o "platô de
27-56 ciclos" era da FAMÍLIA (a amp1p0 o tem); a amp0p25 tem **degrau
imediato** (1,0→0,84 em x=16-32) **+ arresto perfeito** (1000 ciclos sem
deriva) — que o exponencial de relógio CURTO faz sem forma nova. Pacote:
emb 6 µm ancorado no platô publicado (0,171·F₀/k_b) + N_emb=30 lido do
degrau + frac=0 do protocolo + creep/ratchet=0 lidos do arresto ⇒
0,1017/0,2314/0,0367 → **0,0077/0,0630/0,0156** (região 12/12). O stick
total medido (0/2080 ciclos) segue verdadeiro — e é exatamente por isso que
o pacote emb-only fecha. A forma Weibull `emb_clock_m` construída no caminho
fica DORMENTE (TDD 4/4) até um platô real exigi-la.

**`fig18_amp0p5`** (0,1324/0,1795/0,0449). Floor lido 0,1441 **piora** o MAE
(medido: 0,1456). ⚠️ **5ª ERRATA do mapa (2026-08-21)**: a "re-digitalização
da família" que esta seção recomendava **já fora executada em 2026-08-13**
(`a9541ec`, "7 CSVs corrigidas, c1 da tabela") — este doc herdou a
recomendação de 08-06 sem verificar o git da CSV. Re-validado em 08-21:
as CSVs vigentes reproduzem a Tabela 8 a ±0,004 (11 âncoras), e o piso do
par amp1p0↔T22 é 0,0030/0,0026. Consequência: **a rota da amp0p5 está
MORTA** — o 0,1324 é contra dado correto; ela é órfã de protocolo genuína,
sem rota restante (floor falsificado, dado validado). Segue DECLARADA.

**`fig20_T16Nm`** — ✅ **FECHOU às 15:5x (prereg lu2024-t16-emb-ancorado), e o
diagnóstico desta seção estava ERRADO**: não era "meio-de-rampa" — o resíduo
da célula floor-lido mostra o mx no **1º CICLO** (excesso de embedding
−0,164) com convergência ao floor dali em diante (−0,005 em c99). Floor
0,195 LIDO (terminal publicado 0,187) + emb_depth 4 µm **ANCORADO no 1º
ciclo** (modelo 0,594 vs 0,588 digitalizado; c1 publicado na Tabela 9) ⇒
0,1572/0,2384/0,0578 → **0,0226/0,0569/0,0249** (margem σ 0,4 % declarada).
A lição: o rótulo de rota envelhece como qualquer número — o resíduo da
célula NOVA tem de ser relido antes de citar o diagnóstico antigo.

## C. SEM ROTA DE MODELO POR CONSTRUÇÃO (8)

- **4× n<6** (`IJPEM 0_15`, `0_18`, `zhang19_fig4` — e `0_50`/`0_55` pós-P-13):
  o modelo JÁ fecha as pernas julgáveis em todas (MAE 0,003–0,024). Reabrem
  **apenas com dado denso** (o PDF da IJPEM é paywall declarado; zhang19 tem
  5 pontos na figura). Nenhum trabalho de modelo muda o n.
- **`fig20_T4Nm`** — escopo do próprio paper (*"does not reach the tightening
  effect"*); melhora de brinde já registrada (0,157), estatuto imutável.
- **`yang2023ame_axial`** (CFRP) — fora de escopo de material por aprovação
  (2026-07-31). Reabre com forma de membro viscoelástico (projeto de engine,
  mesa do professor).
- **`zhang2006_fig3_illus`** — proveniência ("Illustration"). ⚠️ REANALISADA
  em 20/08 (tarde) a pedido do professor com a leitura de 2 ESTÁGIOS do
  próprio paper: erro caiu 6,6× (0,211→0,032/0,088/0,039, MAE+mx fechando),
  o traço θ foi digitalizado (`anchors_csv/zhang2006_fig3_theta_trace.csv`)
  e a lei de taxa foi LIDA (fe=5,80 do θ ≡ 5,93 do P). Não fecha o σ nem
  com leitura plena: **forma faltante "transição lei-de-potência→runaway"**
  comprovada — ver `zhang2006_fig3_estudo_do_caso.md` §7–§9. Segue
  declarada; a forma entra no mapa de candidatas (2ª evidência natural: a
  classe de aceleração tardia da seção D).
- **`IJPEM 0_65`** — resolução (mediana |Δdado| 0,21 ≥ 0,10, guarda P-10
  global). Só dado melhor.

## D. CLASSE DE FORMA FALTANTE — aceleração tardia (3)

`bauer2024_test1` — ✅ **FECHOU às 15:5x** (transição de fração do espectro;
ver prereg bauer-fig8-scrit-especime) · `fig14_amp0p5_long` ·
`fig14_amp1p0_long` — ⚠️ **ATACADAS às 23:0x-23:3x**
(`lu2024_fig14_burst_resultado.md`): a amp1p0 melhorou **10× no MAE**
(0,4802→0,0458, célula com bedding fracional zerado per-protocolo + incubação
W=310 + graded fe=1,24 lido da cauda) e o TETO ficou nomeado com 2 instâncias
na fonte: **burst-de-ruptura** (liberação da energia incubada — as duas
drenam até ~0,50 F₀ no burst e desaceleram; fração ~fixa, transição
bi-estável da interface). Nenhum kernel atual compõe platô+burst+cauda.
Seguem DECLARADAS; a forma candidata (knockdown de fração lida disparado
pelo onset do W) é decisão de mesa e se paga nas 2 + reuso possível na
classe de aceleração tardia.

## Critério de regressão usado hoje (fica de regra da sessão)

Expoente de chegada por regressão log-log no dado cru: **se r² ≥ ~0,65 e o
valor cai dentro da região que fecha ⇒ REGREDIDO (leitura)** — amp1p5
(1,864, r²=0,685) usou. **Se r² < 0,6 ⇒ a regressão NÃO suporta leitura** e o
valor que fechar é **fitado-declarado** com a regressão registrada como
tentativa — T28 (0,863, r²=0,515) declarou. A suspeita de taxa de fundo
(creep) distorcendo o log-log para baixo fica anotada nas duas.
