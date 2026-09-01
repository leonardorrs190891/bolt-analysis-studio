# Paper-study — ledger de aprendizado por rodada

Protocolo: `.claude/commands/paper-study.md`. Toda rodada LÊ as lições antes e ESCREVE ao final.

## LIÇÕES ACUMULADAS (transferem entre papers — ler PRIMEIRO)

- **L1 (processo)**: config adotada só se reproduz pelo HARNESS DE ORIGEM — labels não
  carregam a config inteira; `%.0e` já enganou uma adoção (GA 1.2e5 lido como 1e5).
- **L2 (settling)**: o dado faz ~metade do assentamento em 10–20 ciclos (N_emb 3–15 per-rig,
  não 50); a DURAÇÃO escala com amplitude (Jiang: 2–5 cyc @1.27mm ↔ 50–100 axial).
- **L3 (µ)**: quando o paper reporta T e F₀ medidos, derive µ por Motosh POR CASO — vira
  input com proveniência (liu2022: dry 0.247/0.225 > oil 0.183/0.168, MAE 0.004–0.022
  zero-refit). µ seco validado em banda [0.14, 0.19] (Qiao/Lu) — 0.20–0.25 aparece em pares
  específicos.
- **L4 (early knee)**: se o reservatório de embedding é pequeno (Rz<4), o joelho inicial é
  RUNNING-IN do wear (K decai ~5×→1 em ~100 cyc; Zhang2019 N^0.53, Eccles 0–50) — não
  adianta mexer em N_emb.
- **L5 (bedding)**: o reservatório fracional é dirigido por SLIP (porca-colada de Jiang);
  o gate atual (fração^q) é suave demais — corta acima do limiar também. Forma pendente:
  gate SATURANTE (Hill, joelho <1) para destravar frac literatura (~60%@τ8 M8).
- **L6 (equifinalidade)**: preload-only sub-restringe o split de mecanismos — sempre que o
  paper tiver θ(N) ou loops, use-os como observável extra (Rousseau: µ=0.20+free_spin
  via MO; energia 7–8× = viscoelástico do membro, forma local pendente).
- **L2b (NUANCE de L2, rodada 1)**: o "n_I" que o paper reporta é o JOELHO OBSERVÁVEL
  (reservatório÷taxa), não o N_emb diretamente — aplicar N_emb=n_I cegamente over-dropa
  (Içmez: mediana 0.039→0.075 REJEITADO). N_emb e tamanho do reservatório são acoplados.
- **L8 (s_crit como âncora de δ_t, rodada 1)**: quando o paper mede o slip crítico
  (Içmez 99µm; Bauer idem), compare com δ_t=F_slip/k_tr do modelo — razão >1 sugere c_bend
  baixo; a correção derivada melhora a mediana (0.039→0.024) mas cria trade entre casos ⇒
  usar como PRIOR de c_bend, adoção só com o trade resolvido.
- **L9 (δ_t ↔ s_crit, rodada 2)**: o take-up δ_t=µF₀/k_tr do modelo VALIDA contra o slip
  crítico medido quando existe (Bauer fig6: δ_t=112µm vs s_crit 76–108µm — c_bend=0.5 ganha
  proveniência independente em M8/8mm). MAS em grips curtos a fração de assentamento
  (k_b·emb/F₀ ~24% no fig6!) mascara a criticalidade no N25 — o joelho S-N do paper não
  aparece no modelo por saturação de settling, não por falta do limiar.
- **L10 (incubação NÃO é joelho de amplitude, rodada 2)**: slip_onset_W atrasa TODAS as
  amplitudes rumo ao teto de settling (razão N25 60/120µm → 1.0) — dose ∝ s é suave demais
  para criar criticalidade; o joelho S-N é o limiar de curso/CM (δ_t), não incubação.
- **L11 (slope de vida, rodada 3)**: a curva D-N de afrouxamento medida (Yang) tem slope
  −5.9 ≈ fadiga (fat_m2=6) — o modelo dá −1.6 (ratchet ∝ slip). O envelope da galeria
  (≤0.6mm) bate; a alta amplitude extrapola 44× lento. FORMA NOMEADA (1ª falsificação):
  driver de crash ∝ potência de tensão (família Su-N aplicada ao afrouxamento). NÃO
  construir até 2ª falsificação nomear igual.
- **L12 (Miner emergente, rodada 3)**: o modelo REPRODUZ o desvio de Miner por sequência
  sem fit (0.92/1.06 vs 0.85–0.91/0.90–1.05 medido, direção certa) — a estrutura
  incubação+dano prevê efeito de ordem; use blocos como validação grátis em papers com
  amplitude variável.
- **L13 (isolamento lê o reservatório, rodada 5)**: a curva PORCA-COLADA (rotação
  bloqueada) lê o emb_load_frac diretamente — Jiang M12: frac=0.25 dá MAE 0.024 zero-refit
  (34% de perda sem rotação = bedding+wear). EQUIFINALIDADE no Zhang (mesmo rig): o fit
  com rotação ativa escolheu frac=0 (crash carriers absorvem o share do settling) — testes
  de isolamento devem PINAR frac antes do fit do crash.
- **L15 (gatilho de crash CONSTRUÍDO, adoção REVERTIDA — refit bauer)**: crash_trigger_frac
  (Hill em F₀/F₀_init) é capacidade validada (3 testes) MAS não net-melhora o fig8: frac=0.55
  piora a mediana MAE (0.098→0.108); frac per-test lido do joelho é MUITO pior (test1→0.195)
  — o gate suprime o DECLÍNIO LENTO que precede o joelho. O joelho não é um limiar único de
  F₀; é declínio-lento+colapso, e um gate único troca um pelo outro. Adoção revertida;
  fig8 fica §4.17 (resíduo estrutural declarado). Caminho futuro: dois canais, não gate único.
- **L14 (joelho tardio = gatilho de criticalidade, rodada 6)**: o estágio-3 do Bauer fig8
  (joelho @70%N: plano 1.00→0.66, depois colapso →0.31) NÃO é fitável por c_bend — o modelo
  é monotônico (cb baixo colapsa desde o início 0.000; cb alto nunca 0.753). O paper nomeia
  o mecanismo: F_V caindo cruza a amplitude crítica (r=Q/µF₀κ →1) e DISPARA runaway. Forma
  faltante: GATILHO de dose/criticalidade (plano até F₀ cruzar limiar, depois positivo). É a
  mesma família do 'erosion-into-gross-slip runaway' (2 falsificações agora: Liu2025 flat-early
  §4.16 + Bauer fig8 knee) ⇒ NOMEIA a forma p/ construir: trigger por r-crossing com F₀.
  **CORREÇÃO DE DESIGN (build tentado no loop, REVERTIDO)**: keyar em r=Q/(µF₀κ) FALHA —
  em disp-mode Q=0.4·F₀ e µF₀ caem juntos ⇒ r é F₀-INDEPENDENTE, o gate nunca dispara. O
  gatilho deve keyar em **F₀/F₀_init cruzando limiar** (ou slip/δ_t com δ_t∝F₀), não em r.
  Forma re-especificada; build = design próprio (TDD com cenário disp-mode), não iteração de loop.
- **L25 (contagem honesta de DOF + sensibilidade condicional ao regime, sec4.42)**: 88 campos
  != 88 DOF — separar classes (44 capabilities inertes=0 DOF; 9 tuners==1; modos/dinamica; ~17
  compartilhadas fitadas 1x; inputs medidos; 2 per-rig). OAT +-20%: a MAIOR sensibilidade
  transversal e' mu (0.067) — um INPUT medido, nao fitado = robustez estrutural; a 2a e'
  tr_loose_gain (0.054) SEM ancora propria => candidata N1 a experimento de procedencia (nao a
  fit). Axial: SO emb+C_creep ativos (resto zero, regime-gated) — 2 mecanismos, 2 caminhos de
  procedencia. Congelaveis exatos (S=0 em todos): k_j_init, alpha_GW, slip_capacity_coeff,
  partial_slip_exp (bypassed pelos modos canonicos). K_archard/hardness so aparecem como K/H =>
  merge estrutural. CAVEAT: sensibilidade e' condicional ao working point (delta_free S=0 no caso
  sub-slip mas decisiva no onset em outras amplitudes) => congelar DENTRO da formulacao canonica,
  nunca remover a forma. Regra: reducao de variaveis = (a) merges estruturais exatos, (b) congelar
  S~0, (c) converter fitado em LIDO (L24), (d) procedencia para os sensiveis-sem-ancora — nessa
  ordem; nunca podar por contagem bruta de campos.
- **L24 (LER a constante da feature do dado, nao do handbook, sec4.40)**: o nivel axial que
  bloqueava (§4.39) e' EMBEDDING (71% da perda), e o handbook VDI Rz<4 (3.5um) super-estima o rig
  Li2022ti 2x vs o data-implicito da QUEDA-INICIAL (7.5% => 1.6um via drop*F0/k_b). emb=1.6um
  (proveniencia da feature de queda-inicial, como floor/W_crit) => MAE 0.064->0.039, baseline casa.
  A galeria over-retem = emb ainda menor; a verdade e' o MEIO (1.6um). Regra: handbook (VDI f_Z por
  classe de rugosidade) vs valor DATA-IMPLICITO divergindo => o data-implicito (lido da feature que
  a constante controla; emb<->queda-inicial) e' mais especifico e ganha. Proveniencia, nao fit.
- **L23 (forma representavel, NIVEL bloqueia — recorrente, sec4.39/#9)**: fretting axial
  freq-dependente (d_fret*=(f_ref/f)^exp) construido (TDD 6/6, default-inert). Reproduz a ORDEM de
  frequencia que o modelo perdia (spread 0.005->0.049, exp=1.0 LIDO do sweep). MAS o MAE-win
  (0.064->0.025) exigiu emb 12x abaixo da banda Rz<4 (over-tuning); ao emb provenance'd o baseline
  over-afrouxa. Mesma tensao nivel-vs-forma do §4.6: a FORMA (freq-ordering) transfere, o NIVEL
  axial per-rig e o gargalo. Regra: separar SEMPRE o gate de FORMA (ordering/spread, level-robusto)
  do gate de NIVEL (MAE absoluto); uma forma pode PASSAR o de forma e o nivel exigir procedencia
  propria — nao confundir "reproduz a fisica" com "baixa o MAE". Padrao da sessao: formas transferem,
  constantes/niveis sao per-rig (§8).
- **L22 (formas se COMPOEM: a que destrava a outra, sec4.37)**: a taxa de loosening graduada
  (graded_scrit: cinematica no excesso de slip sobre s_crit FIXO, amplitude-sensivel, sem runaway)
  foi construida (TDD 7/7, default-inert). Sozinha NAO bate o piso do Karlsen (0.114 vs 0.097,
  constante = data-limited). MAS destrava o espectro (sec4.36): a SINTESE passa — media sub-critica
  nao colapsa, espectro com picos super-criticos SIM (DIFF ate -0.53). Regra: quando um input nao
  morde por causa de um downstream binario (L21), a forma que falta e a LEI DE TAXA graduada; e as
  duas se COMPOEM (nenhuma sozinha faz o efeito). Adocao numa curva real precisa da PROVENIENCIA do
  espectro per-caso (fracao/amplitude dos picos), nao um knob — senao e W_crit per-curva de novo.
- **L21 (input novo so ajuda se o DOWNSTREAM for graduado, sec4.36)**: multi-amplitude (espectro
  estatistico) foi construido (spectrum_schedule, det., TDD 11/11, engine-free, bit-identical off)
  MAS a premissa "reduz os S-shapes" FALSIFICOU: em disp-mode o loosening e runaway-to-zero uma vez
  disparado (s_crit=delta_t cai com F0 => g_gross->1), entao a amplitude afeta o ONSET, nao a
  trajetoria => o espectro so gradua o colapso no regime DANO-controlado. E low-discrepancy nao gera
  scatter de timing (converge). Regra: antes de adicionar um INPUT (espectro, ordem, distribuicao),
  checar se o mecanismo downstream e GRADUADO nesse input — se e binario/runaway, o input nao morde
  e a forma que falta e a LEI DE TAXA (aqui: loosening graduado amplitude-sensivel), nao o input.
- **L20 (o modo de erro dominante pode estar NO PISO, sec4.35)**: auditoria de bias por-janela
  => mid-over-loss em 35/82, concentrado em Karlsen/Yang/Rousseau; over-RETAIN oposto em
  Li2022Ti/Icmez. NAO ha forma unica (correcoes opostas). 3 formas propostas (teto cinematico
  em serie #1, c_bend geometrico #2, drive-stiffness #3) TODAS falsificadas no modo dominante.
  Decisivo: sweep 2D c_bend×arrest acha o minimo EXATO no ponto adotado de Karlsen (0.0968) —
  4 mecanismos adicionados PIORAM (bias e over-loss, todos adicionam perda). A nota de aparato
  nomeia a raiz: Karlsen HV e "near-linear catastrophic back-off, ±1mm" — mismatch de FORMA
  (convexo→arresto vs quase-linear) em amplitude extrema, nao mecanismo faltante. Regra: antes
  de construir forma para um bias sistematico, (a) reconciliar o bias com a config ADOTADA (nao
  o probe bare — L1), (b) checar se a fonte esta no piso (sweep dos knobs existentes), (c) ler
  a nota de aparato (regime/espectro). Se over-loss e over-retain coexistem entre fontes, e
  per-rig/forma-de-regime, nao uma forma global. `loose_kin_ceiling` fica inerte (capability).
- **L19 (CONTINUUM s_crit, sec4.33)**: fig6+fig8 = MESMA fisica de dano via onset CONTINUO
  por gross-slip (dmg_gross_exp), s_crit=delta_t∝F0. Joelho emerge da super-criticalidade
  (fig6 minimo, fig8 forte), constantes de dano COMPARTILHADAS, c_bend per-rig. fig6 rep2/3/4
  0.09/0.10/0.11->0.02/0.02/0.05; fig8 test1 suaviza 0.097->0.121 (trade da unificacao vs
  W_crit per-espectro). Regra: preferir onset FISICO continuo (razao s_a/s_crit) a limiar de
  energia per-caso — e' modelo, distingue por input, transfere.
- **L18 (auto-distincao por s_crit, sec4.32 adendo)**: joelho vs quasi-linear = amplitude
  vs s_crit (paper Bauer: s_crit=99um "abaixo do qual afrouxamento rotacional NAO inicia").
  fig6 70um sub-critico=sem joelho; fig8 picos 150um super-critico=joelho. A MESMA config
  dE_partial deixa D=0 no fig6 AUTOMATICAMENTE (input sub-critico) => modelo auto-distingue
  por amplitude/F0, constantes compartilhadas, SEM chave per-caso. Regra: nao desligar formas
  a mao quando o input ja as desliga fisicamente.
- **L17 (dE_partial FECHA o joelho, sec4.32)**: a forma da dupla falsificacao foi construida
  e RESOLVE o Bauer fig8 — partial-slip energy alimenta o dano no plato => D => mu cai =>
  gross slip => colapso. mediana 0.095->0.069, interp 0.113->0.077 (test1 0.137->0.077).
  W_crit per-espectro lido do joelho. A FORMA resolveu o que a constante nao resolvia (L16).
- **L16 (raiz do joelho = partial-slip energy, sec4.31)**: o joelho estágio-3 (Bauer fig8)
  NÃO é corrigível por constantes — o dano (que o disparia, via literatura) é dirigido por
  W_slip_acc = trabalho de GROSS slip, e o config do platô tem gross slip ZERO ⇒ D nunca
  dispara. A raiz é o `dE` de PARTIAL slip não contabilizado (MESMA forma do §4.25, loops
  Rousseau) — dupla falsificação nomeia dE_partial alimentando W_slip_acc. Forma, não
  constante; merece design (não rush).
- **L7 (contradições são regimes)**: fração Stage-I vs F₀ SOBE no estático e DESCE no axial
  vibrado; reaperto melhora com superfície protegida (óleo) e piora a seco (c_D per-lube
  captura); exponencial nos metais, LOG nos moles/creep.
- **L25 (metrologia — três classes de limite, 2026-07-28)**: curva que não fecha é
  *form-limited* (falta mecanismo), *data-limited* (o dado publicado TERMINA antes do
  fenômeno; assinatura: res.máx no ÚLTIMO ponto = valor de moldura — borda de eixo, fim
  de digitalização, FLOOR_TRIM; ação = dado novo) ou *metric-limited* (colapso
  quase-vertical: res.máx<0,10 exigiria acertar a fratura em ±0,05% da vida; **4 métricas
  automáticas testadas, 4 mortas por gate** — nenhuma distingue rampa de cliff ali; a
  resposta é o trim por julgamento humano, e a regra que o descreve NÃO é automatizável
  — não é invariante à amostragem, Δ_col 27,5× entre digitalizações da mesma curva).
  §4.44–§4.48a.
- **L26 (autoria de gates, 2026-07-28)**: quatro defeitos de gate em quatro preregs
  geraram quatro regras: (i) todo gate carrega a **conta de satisfazibilidade RODADA**
  (não estimada — uma conta de cabeça errou 45×), cobrindo o **pior caso admitido pelo
  ESCOPO** do gate (escopo `X<a` exige verificar `X=a`); (ii) gate mede a **MUDANÇA**,
  nunca o ambiente (git-status numa árvore compartilhada não é gate); (iii) **um gate
  CEGO vale mais que nove no caso de projeto** — o C4 cego matou a banda-v2 cuja
  discriminância era artefato de projeto; (iv) declarar a perda de cegueira POR ESCRITO
  antes de medir é o que obriga a criar o gate cego. §4.45–§4.48.
- **L27 (fratura tem DOIS relógios; o joelho é emergente, 2026-07-28)**: o relógio
  PREDITIVO de fratura (Miner+Goodman, C1 único ancorado) espalha ±36% e é FALSIFICADO
  para adoção quando os trims sentam no joelho (N_D ≈ 0,72–0,80·N_f ⇒ orçamento ≤5%;
  adoção reverteu com +0,111 na amp0p8). O relógio LIDO (N_f input-de-paper POR CURVA,
  mesma coluna dos trim_n_max) torna a rampa NULA na métrica (α ≤ 3e-6) e ADOTA limpo
  (E1 cego 7/7, pior ΔMAE +0,0006) — claim honesta: "prevê a curva DADA a vida". E o
  joelho bilinear da Su–N (m₂≈1,4 quase plano = limiar de afrouxamento; transfere
  cross-size a 5,9% em tensão de raiz) é **EMERGENTE** dos mecanismos de estágio 1-2 —
  implementá-lo via Su-N duplicaria física. §4.49–§4.53.

## FILA (status por fonte/paper)

| # | paper/fonte | dados | status | resíduo/nota |
|---|---|---|---|---|
| 0a | liu2022 (fig5) | 4 curvas + notas | **FEITO** (§4.28/4.29) | running-in adotado; MAEs 0.014–0.019; fig6/7/8 reaperto = rodada própria |
| 0b | lu2024 | 10 curvas + torque-anchor | **FEITO** (§4.19/4.29) | minimax confirmado; early +0.05–0.14 espera gate saturante (L5) |
| 1 | demir2024/Içmez | 8 curvas + nota rica | **PARCIAL** (rodada 1) | L8: s_crit⇒c_bend prior (mediana 0.024 disponível, trade 2 casos); N_emb=12 rejeitado (L2b) |
| 2 | bauer2024 | 9 curvas + s_crit | **FEITO** (r2+dE_partial sec4.32: joelho fechado, mediana 0.069) | δ_t=112µm valida s_crit 76–108 (L9); incubação-joelho rejeitada (L10); fonte nos pisos |
| 3 | yang2019 | 3 curvas + D-N + Miner | **FEITO-parcial** (rodada 3) | Miner PASSA emergente (L12); freq-flat ok; D-N slope falsificado a alta amp (L11) |
| 4 | zhang2006 | 9 curvas (grip+direção) | PARCIAL (§4.22/4.24) | floor∝severidade nomeado (mistos 45/60°) |
| 5 | karlsen2022 | 7 curvas + retention | FEITO (iter 11) | âncora retention_2000cyc não usada |
| 6 | liu2025 | 7 curvas + oscillation | FEITO (iter 12) | amp0p4 0.102; âncora clamp_oscillation não usada |
| 7 | rousseau2025 | 6+6θ+15 loops | PARCIAL (§4.20–4.27) | 3 observáveis; formas local-visc + drive-scaling pendentes |
| 8 | liu2017 axial | 9 curvas | FEITO (§4.18) | ρ-unificação; N_emb axial 50–100 (L2) conferir |
| 9 | li2022ti | 4 curvas + creep | FEITO (§4.13) | axialmin early +0.042 |
| 10 | liu2022 fig6/7/8 (reaperto) | 12 curvas | **FEITO** (rodada 4) | 12/12 <=0.10; renewal=1+galling+c_D per-lube; classe multi-segmento na galeria (82 casos, media 0.0592) |
| 11 | jiang2003/04 | curvas Stage-I + glued-nut | **PARCIAL** (rodada 5) | glued-nut LÊ frac=0.25 (MAE 0.024, L13); sweep de amplitude/λ pendente |
| 12 | eccles2010 | µ-evolução + torque-residual | PENDENTE | sinal-por-par (§4.26); K desaperto nomeado |
| 13+ | demais fontes com curvas em extracted_csv (sase, bhattacharya, hattori, liucai, liu2018...) | tabelas | PENDENTE | triagem por rodada |

## RODADAS

### Rodada 6 — bauer2024 fig8 estágio-3 (2026-07-08, via /loop; falsificação flagada pelo professor)
- **Dado**: joelho @N=609 (70%); 3 estágios 1.00→0.66→0.31; interp maxerr 0.466 @99%.
- **Falsificado**: varredura c_bend×floor×emb×frac — sem config plano-depois-joelho (cb=0.2
  fim 0.753 / cb=0.5 fim 0.000; nada no meio) ⇒ **L14**. O modelo produz criticalidade
  GRADUAL (r cruza 1 suavemente); o dado tem gatilho ABRUPTO.
- **Forma NOMEADA (2ª falsificação, agora construir)**: trigger de runaway por r-crossing —
  plano enquanto Q<µF₀κ, positivo-realimentado quando F₀ cai o suficiente (a hipótese exata
  do paper). Par do slip_onset_W mas no CRASH, não na incubação.
- **Não adotado**: fig8 fica AS-IS (fig8 já ~0.097 por-pontos; o interp expõe o joelho).

### Rodada 5 — jiang2003/04 (2026-07-08, via /loop; compacta)
- **Glued-nut zero-refit**: config Zhang (mesmo rig) com rotação ZERADA + frac varrido:
  frac=0.25 → MAE 0.024 (fim 0.646 vs 0.660) ⇒ **L13** (isolamento lê o reservatório;
  Zhang com frac=0 é equifinalidade — repinar Zhang com frac=0.25 na próxima passada).
- **Pendente na fonte**: sweep λ×amplitude (5 curvas 0.254–1.27mm) + Dataset_4 (preload).

### Rodada 4 — liu2022 reaperto fig6/7/8 (2026-07-08, via /loop)
- **Fechou**: 12/12 fases ≤0.10 (MAEs 0.004–0.034) com constantes JÁ adotadas (µ Motosh L3,
  c_D per-lube L7, galling k=3 §4.11, running-in L4) + k_emb_renew=1.0 (renewal ON vence
  0.027/0.018/0.022 vs 0.030/0.025/0.033 no dry — 1ª validação de sequência do retighten()).
- **Padrão de recuperação**: dry 1.00→0.96→0.92→0.90 (galling acumula) vs oil ~0.99–1.00
  (restaura) — o contraste §4.11 agora em SEQUÊNCIA completa de 4 apertos.
- **Galeria**: +12 casos (classe multi-segmento estreia) → 82 casos, média 0.0592 (−0.0073).
- **Ensina**: as lições compõem — nenhuma constante nova foi fitada nesta rodada; tudo veio
  de L3/L4/L7 + formas existentes. O protocolo está convergindo por ACÚMULO.

### Rodada 3 — yang2019 (2026-07-08, via /loop)
- **(C) Miner blocos: PASS EMERGENTE** — somas 0.92 (h→l) / 1.06 (l→h) vs medido 0.85–0.91 /
  0.90–1.05; direção e magnitude sem fit ⇒ **L12**.
- **(B) freq 5/10/20Hz @1.0mm: PASS** — razão 1.16 vs ~1.1 medida; dwell §4.21 preservado
  (regime: corrosão só em vidas longas — L7).
- **(A) D-N: FALSIFICADO a alta amplitude** — slope modelo −1.6 vs −5.9 medido; N50 bate a
  0.4mm (15318 vs 18000) e diverge 44× a 1.0mm ⇒ **L11** (crash ∝ potência de tensão,
  nomeado, aguarda 2ª falsificação).
- **Status**: yang → FEITO-parcial (galeria fina no envelope; extrapolação de alta amplitude
  documentada como limite).
- **Não adotado**: nenhuma mudança de config (nada a fitar — era confronto de âncoras).

### Rodada 2 — bauer2024 (2026-07-08, protocolo, via /loop)
- **Confronto de âncora (headline)**: varredura de criticalidade N25(s) no config fig6 —
  modelo SEM joelho (N25 37–127 flat através de 4× amplitude) vs S-N medido com joelho em
  76–108µm. Diagnóstico: δ_t do modelo = 112µm ≈ s_crit ✓ (L9 — validação independente de
  c_bend=0.5 em M8), mas o assentamento (24% de F₀ no grip 8mm) satura o N25 e esconde o
  limiar.
- **Testado**: slip_onset_W ∈ {60,150,400} como gerador de joelho → REJEITADO (achata a
  razão para 1.0 em vez de afiar; todas as réplicas fig6 pioram) ⇒ **L10**.
- **L1 reconfirmada**: minha réplica fig6 inline ≠ baseline da galeria (rep1/rep6 já
  divergiam com W=0) — gates de fonte só valem pelo harness de origem.
- **Status**: bauer → FEITO-declarado (fig6 no piso de repeats 0.115; fig8 <0.10; rep5
  0.137 = +0.002 sobre limite, extremo dos 6 repeats).
- **Não adotado**: nenhuma mudança (gates seguraram).

### Rodada 1 — demir2024/Içmez (2026-07-08, protocolo)
- **Auditoria**: 8 casos, mediana 0.039; alvo amp0p4_F17p6_lk13p8 eb +0.045; δ_t modelo
  203–360µm vs s_crit MEDIDO 99µm (2–3.6×).
- **Testado**: (a) N_emb=12 do paper → REJEITADO pelos gates (mediana 0.075, over-drop
  geral) ⇒ **L2b**; (b) c_bend derivado do s_crit → mediana 0.024 disponível MAS 2 casos
  pioram >0.02 ⇒ **L8** (s_crit vira prior; adoção pendente do trade — próxima passada
  nesta fonte investiga QUAIS 2 casos e se um sub-split resolve).
- **Status fila**: Içmez → PARCIAL (config atual mantida; prior L8 registrado).
- **Não adotado**: nenhuma mudança na galeria (gates seguraram — corretamente).

### Rodada 0a — liu2022 fig5 (2026-07-08, pré-protocolo; exemplo do formato)
- **Fechou**: 4 casos zero-refit (µ Motosh L3) 0.017–0.004; refeito com running-in (L4) → 0.014–0.005.
- **Ensinou (→L3, L4)**: µ por caso do próprio paper; early knee = running-in quando emb pequeno.
- **Per-rig**: c_D per-lube (0.5/0.03) segue L7.
- **Nomeado**: rodada própria para reaperto fig6/7/8 (fila #10).

### Rodada 0b — lu2024 refit (2026-07-08, pré-protocolo)
- **Fechou**: nada novo (config §4.19 confirmada minimax em 36 configs; 10/10 sob limites).
- **Ensinou (→L5)**: gate fração^q suave demais; forma saturante nomeada.
- **Relatório**: `lu_report.html` (10 curvas + bias early).
