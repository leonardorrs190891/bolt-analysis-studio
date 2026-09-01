# ⛔ F4 PARE — IMPASSE REGISTRADO (2026-07-22 ~21:45)

**NENHUM merge/adoção até decisão do professor.** Registrado pela sessão-mestre retomada
pós-limite (a que commitou fc52769/1dd09a5/429c272/f051195/745bf27). Este arquivo está no
worktree porque o guard de background-session bloqueia escrita no ledger do checkout main
(.superpowers/master-0p1-progress.md) — transcrever para lá na próxima janela com permissão.

## 1. Quiescência violada — duas sessões-mestre em paralelo no MESMO worktree

- Commits **4b0982a** (20:34, "G4-a ★PASS★ + liu2020 9/9 bloco A per-rig") e **2bded80**
  (20:57, "zhang18/19 13/13 — BLOCO B FECHADO") são da **outra** sessão; a entrada
  "F4 GATE B1-v3 G4-a ★PASS★" no ledger mestre do main também (o "linter externo" que ela
  menciona era esta sessão editando parameter_registry).
- Esta sessão produziu: fix do sandbox (fc52769), **rota TRANSVERSAL do flanco**
  default-inerte TDD (1dd09a5), **prereg-2 imutável** (429c272, ANTES dos fits), script do
  painel (f051195), script G4-c (745bf27), e os resultados `f4_r5_panel_result.json` +
  `f4_r5_run.log` (não-commitados no momento do registro).

## 2. Duas linhas de evidência INCOMPATÍVEIS fechando os mesmos 22 casos R5

| | (A) esta sessão — prereg-2 | (B) sessão paralela — "bloco A per-rig" |
|---|---|---|
| Forma | rota transversal do flanco (nova, default-inerte, TDD) | nenhuma (canais existentes) |
| tr_loose_gain | **0 = leitura** (zero rotação MEDIDA nos 3 papers) | 0,1 **fitado** |
| emb | **lido L24** (Estágio I paper-stated): 1,07–2,10 µm | **fitado**: 0,10–0,25 µm (≪ leitura) |
| bearing wear | k_wear_spec=0 (leitura SEM/EDX: desgaste no flanco) | k_wear_spec=1e-16 fitado |
| DOF fitados | 5 p/ 22 curvas | ~6–9 p/ 22 curvas (grade estendida pós-FAIL2) |
| Resultado | 22/22 tripé (med 0,014; pior maxerr 0,077; 12 out-of-fit) | 22/22 tripé |
| Registro | prereg imutável ANTES do fit; resultado ficou não-commitado | commits de PASS; reinterpretação declarada pós-FAIL2 |

## 3. Voto adversarial 1/3 = REFUTADO (regra: ≥3 votos antes de adoção)

Achado central **verificado por esta sessão nos próprios dados** (`f4_b1v3_result.json`):
**30/30 células da busca B1-v3 passam a banda de slope — inclusive as 6 células fr=0
(= v1 puro, sem limiar)**. O slope do Liu2017 vem da **ρ-unificação já adotada** no cfg
canônico LIU_2017_axial (emb_amp_exp=2,375, §4.18, adotada 2026-07-08), não do candidato.
A falsificação T4 rodou com baseline genérico (frozen_constants sem o cfg adotado) ≠
baseline canônico ⇒ **o gap axial L1 já estava fechado no canônico e o gate B1 nunca foi
re-baselinado antes da F4**. No transversal o limiar também é dispensável (células
sc_crit=0 passam 4/4 no zinc; a vencedora ganha só por mediana 0,0146 vs 0,0157).

## 4. Propostas à decisão do professor (não assinadas)

1. **Matar UMA sessão** e reafirmar o escritor único (CERCA do plano-mestre).
2. **Candidato (c) flank_s_crit: NÃO demonstrado** — manter o campo (default 0,
   bit-idêntico) como capacidade não-adotada; registrar FAIL de discriminância.
3. **Resultado defensável para adoção** = rota transversal do flanco + receitas por
   leitura do prereg-2, com **s_crit=0** por parcimônia (re-run barato do painel com
   sc=0 confirma 22/22 antes de adotar).
4. **MODEL_LEGITIMACY**: novo § com o re-baseline do gate B1 (slope axial coberto pela
   ρ-unificação canônica; falsificações devem ser re-checadas contra o canônico vigente,
   não contra baseline genérico).
5. Votos adversariais 2–3 + controles G4-c estavam em curso; anexar ao relatório.

## 5. Adendos pós-registro

- **G4-c: PASS (2026-07-22 ~21:55)** — 8/8 controles **bit-idênticos** (`==` em
  mae/maxerr/final_pred) entre o engine pré-F4 (main @5ec349c) e o engine F4 (worktree),
  mesmos adopted_configs: liu2017_axial_F0_{15,21}kN, li2022ti_axialmin_10Hz +
  li2022ti_axial_10Hz_full (com per-rig F2/trim F3), liu2016wear_fig9a_m30nm,
  liu2025_M16_amp{0p3,0p6}, sun2025 nogrease_standard. Artefatos:
  `New_Theory/f4_g4c_{pre,f4}.json`. Fecha a perna do G4-c que o voto 1 apontou como
  incompleta: as formas novas da F4 são rigorosamente default-inertes fora das fontes
  tocadas.
- **Voto adversarial 2 (numérico): SUSTENTADO (fecho formal)** — nenhum bug que fabrique
  os gates; TODOS os números re-derivados bit-a-bit (busca, painel, full-res da célula
  vencedora); bit-identidade real vs engine pré-commit 6/6 cenários; sandbox sem race
  (leitura por chamada, prova empírica no mesmo processo); conservação residual/W_ext=
  7,3e-8; zero dupla-contagem (decomposição fecha 1−ratio exato); trim 0,4mm no-op;
  matching de tokens fig16 verificado no runtime; assinatura ON/OFF do limiar entre
  células = resultado gerado por máquina, não editado. Mesmo caveat de ATRIBUIÇÃO
  (G4-a pouco discriminante; célula vencedora é canto de grade). Caveats técnicos novos
  a constar em qualquer adoção: (i) convenção de slip 2× (canal L1) vs 4× (WearLoss) —
  herdada do v1, absorvida no k; (ii) critério full-res mae_f0<0,026 é ~0,0005 mais
  frouxo que o texto do prereg (sem efeito material); (iii) leitor emb_depth_from_early_
  drop declara doutrina AXIAL e foi usado em rigs transversais (justificado pela
  rotação-zero, tensão a registrar); (iv) a rota transversal NÃO passa pelos gates
  partial_slip/conformation/slip_onset que o WearLoss sofre — assimetria absorvida no k.
- **Voto adversarial 3 (físico): REFUTADO como demonstração do mecanismo** — com sondas
  próprias e independentes: (i) G4-a vácuo re-verificado por simulação (canal OFF → slope
  −1,784e-5 idêntico ao vencedor); (ii) **TESTE PLACEBO no painel R5: canal morto
  (k=1e-18) → 21/22 ainda passam o tripé** — as LEITURAS carregam o painel; o mecanismo
  só é exigido pela curva 0,4mm (cauda de trinca out-of-model); (iii) canal CEGO a
  preload (P0-sweep validado pelo embedding lido, não pelo candidato; SEM do paper diz que
  o efeito de preload É de desgaste); (iv) forma do Estágio II qualitativamente errada
  (taxa ~constante vs dado log-linear DESACELERANTE por debris; ~14× a taxa do dado na
  borda da janela — fecha a janela, não extrapola); (v) s_crit não é limiar físico
  (110 µm de "stick" sob 99 µm de deslizamento bruto; 3 tratamentos distintos nos 3 rigs
  — a forma não transfere); (vi) k_z18 2,25× ABAIXO da banda KB do mesmo par ancorado
  (rigs-companheiros exigem k 5,6× distintos); (vii) DOF efetivos ~12-13 p/ ~14 condições
  independentes. SOBREVIVE: rota transversal como capability default-inerte; as leituras
  (legítimas, paper-based); e a constatação de que a física que falta para o Estágio II é
  um termo debris-PROTETOR (taxa decrescente no desgaste acumulado — já nomeado nas
  apparatus_notes), não um limiar.

## 6. Placar final da verificação adversarial (regra ≥3 votos): 2 REFUTADO + 1 números-OK

Síntese consolidada: **os números são reais e reproduzíveis; a ATRIBUIÇÃO ao candidato (c)
não se sustenta em nenhum dos dois gates; e o fecho dos 22 R5 é carregado pelas LEITURAS
(placebo 21/22)**. Isso ATUALIZA a proposta 3 do §4: a opção mais parcimoniosa agora é
adotar SÓ as receitas por leitura per-fonte (21/22 no tripé com canal morto) + tratar a
0,4mm como exceção-C com prova quantitativa (cauda de trinca; atenção: a regra da taxa NÃO
achou changepoint — a exceção precisa de outra prova, ex. a atribuição explícita do paper
§3.1.2) OU adotar leituras + um termo de desgaste de flanco com DESACELERAÇÃO por debris
(física nova pequena, prereg novo, = candidato (b) invertido). Ambas exigem decisão do
professor; a rota transversal + s_crit permanecem no engine como capabilities
default-inertes não-adotadas em qualquer cenário.
