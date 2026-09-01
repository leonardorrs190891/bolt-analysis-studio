# Pré-registros — F3 varredura sistemática (prompt-mestre, bloco A)

**Executor:** sessão mestre · **Baseline vigente:** store pós-P2.1 (98 violadores) · Gates
escritos ANTES de cada fit — imutáveis. Regras transversais: nenhuma curva regride >0,1;
mediana da fonte não piora >0,005; controles bit-idênticos; adoção per-grupo com `prov`;
forma nova NUNCA (fila do professor). Um prereg por seção, numerados F3.x.

## F3.1-JCSR — níveis per-condição + cinética saturante (autorização F2.2 do prompt-mestre)

**Diagnóstico (agente 2026-07-21):** os 4 violadores rodam SEM grupo adotado (overrides {}),
caindo no C_creep compartilhado UFU (par errado) + t_0=1 s ⇒ joelho no dia 1 e piso errado.
O FAIL do P2.2 era CONFUNDIDO: a grade testou a saturante com C_creep preso ao nível
compartilhado (teto de queda ~1,8% — a grade inteira saturava no teto). Com nível
per-condição, a sonda do diagnóstico dá: galv 0,008/0,021 · stainless 0,016/0,040 ·
plain_sea 0,022/0,055 (tripé FECHA) · outdoor 0,039/0,107 (marginal — rebound real
não-monotônico, out-of-model). Declaro o confundidor aqui por honestidade metodológica —
este prereg é a mesma alavanca F2.2 (autorizada: "adotar creep_mode=saturating só nas
fontes onde o tripé melhorar") com o DOF de nível correto.

**Mudança:** 4 grupos novos — `JCSR_2023_galv_seawater`, `JCSR_2023_plain_seawater`,
`JCSR_2023_stainless_seawater`, `JCSR_2023_outdoor` (NUNCA criar `JCSR_2023_plain`:
empata em score de matching com o grupo indoor no caso plain_indoor). Por grupo:
- `creep_mode="saturating"` (capacidade T7 validada; switch por prereg, nunca fitado);
- `creep_t_c` SEMEADO do onset c da Eq.(2) do próprio paper (galv 7,95 d · plain_sea
  14,65 d · stainless 24,7 d · outdoor 99 d — INPUT-DE-PAPER, em segundos no engine)
  com ajuste fino permitido ±meia década (fitado-this-rig);
- `C_creep` per-condição (fitado-this-rig, rótulo obrigatório "proxy ambiental
  per-par×ambiente" — 18–64× o UFU; aviso do check_input/creep_class ESPERADO e
  documentado, precedente k_wear_flank; NUNCA poolar com pares metálicos limpos);
- `creep_alpha_sat` fitado (grade).

**Gate (imutável):**
- G-JCSR-a: tripé <0,1 em galv_seawater, plain_seawater e stainless_seawater. Outdoor:
  MAE <0,1 obrigatório; se maxerr>0,1 persistir EXCLUSIVAMENTE no trecho de rebound
  não-monotônico (recuperação real de F0, Tabela 2 do paper — nenhum mecanismo do engine
  recupera pré-carga), documentar como candidata a exceção F5 com a prova (não força FAIL
  se os outros 3 fecharem).
- G-JCSR-b: indoor bit-idêntico; mediana da fonte <0,08 (hoje 0,218); nenhuma regressão.
- G-JCSR-c: controles bit-idênticos nas fontes de creep irmãs (2 casos Caccese + 1 Qin +
  1 MarStruc re-simulados; chaves prefixadas por fonte — vazamento imprevisto = FAIL).
- G-JCSR-d: suíte de creep verde (test_l5_creep_saturating).
- Máx. 2 tentativas de fit; FAIL2 → log-t com níveis lidos (fallback do diagnóstico:
  MAE fecha 3/4, maxerr documentado como forma-de-corrosão faltante → fila).

**Custo estimado:** ~100–200 sims de segundos (curvas de 80–150 pontos).

## F3.2-CHU — µ(N) medido como input (Fig. 5 JÁ digitalizada) + floor lido

**Diagnóstico (agente 2026-07-21):** test5/6 JÁ passam; test1 adotado-escopado. Alvos:
test2/4/7/8 (µ(N) da Fig. 5 disponível — 5 CSVs digitalizados em 2026-07-15, o item 5 da
fila está DESATUALIZADO: não há 30 min de digitalização pendentes) + test9 borderline
(floor+emb-Ra1.6 por leitura). test3 → fila (sem µ(N) no paper; resíduo = run-in por
CICLO, kernel-limited). Núcleo confirmado no engine: dano dirigido por W_slip (∝F0)
acumula na direção ERRADA vs o dado (F0 alto ATRASA a subida de µ) — por isso PR-38
sub-dirigiu 7/8. Prescrever o µ medido é o caminho (a) que a fila do professor nomeou
como destravado pela digitalização.

**Mudança (2 partes):**
1. ENCANAMENTO default-inerte: `mu_bearing_schedule` (lista [(N, µ)]) em JointMaterial +
   lookup no step_cycle — schedule vazio ⇒ comportamento BIT-IDÊNTICO (TDD com teste de
   bit-identidade, mesmo idioma do delta_spectrum: input variável no tempo, valores
   MEDIDOS, não é física nova nem fittable; mandato: caminho (a) da fila do professor +
   precedente delta_spectrum + regra transversal "formas novas sempre default-inertes com
   bit-identidade testada").
2. ADOÇÃO per_case: schedules dos CSVs Fig5 para test2/4/7/8 (input-de-paper) + floor
   lido do platô (L24; test4/7/8/9 platô limpo; test2 limite-inferior documentado) +
   emb Ra1.6 (VDI) no test9. c_bend/mu_thread/C_creep do grupo test1 mantidos.

**Gate (imutável):**
- G-CHU-a: tripé <0,1 em test4 (mais provável) e ≥2 de {test2, test7, test8}; os que não
  fecharem: documentar exatamente o resíduo (µ(N) necessário-mas-insuficiente = taxa de
  colapso do kernel) → fila.
- G-CHU-b: bit-identidade com schedule vazio (teste unitário) + zero regressão nos 202
  (o campo novo é default-inerte; controles: test5/6 + test1 + 4 transversais de outras
  fontes bit-idênticos).
- G-CHU-c: suíte-alvo verde. Máx. 2 tentativas; FAIL2 → documenta e fila.
- test3: NÃO tocar (fila, kernel run-in). test9: adotar só se tripé fechar com
  leitura pura (floor+emb); sem fit dedicado.

## F3-LOTE2 — quatro preregs de nível/leitura (gates antes do fit)

**L2a ZHANG-fig16:** C_creep do grupo ZHANG_2006 relido do platô REAL (slope medido
−0,0126/década; leitura vigente 3,08e-11 ~4× forte, contaminada pelo joelho). Grade
C ∈ {0,5, 0,77, 1,0, 1,3}e-11. GATE: fig16 tripé<0,1; fig3 (kernel-fila) MAE não piora
>0,005 — senão grupo per-figura ZHANG_2006_fig16 (precedente Bauer/LIU).

**L2b UFU:** 5A: emb_um lido da queda-zero (0,000) ∈ {0; 0,5; 1} µm; 13A_first: emb_um
∈ {0; 1; 2} × k_ratchet ∈ {0; 3e-5; 1e-4} (dreno linear per-espécime, precedente Karlsen).
GATE: 5A e 13A_first tripé<0,1; 13A_def (0,093) não piora >0,005; classes: lido-do-dado +
fitado-this-rig(ratchet).

**L2c SUN-N1 (grease_crimp):** k_wear_spec per-par-lube lido da planura do platô — grade
log {1,5, 2,2, 2,9, 4,2, 6,0}e-15 no grupo SUN_2025_CRIMP per_case _grease_crimp. GATE:
tripé<0,1 (candidato do agente 2,9e-15 → 0,023/0,089); grease_standard não piora; demais
bit-intocados. NOTA: atualiza a fila item 6 (caso não depende mais da decisão G2).

**L2d SUN-N2 (axial standard ×2):** C_creep per-TOKEN axial+standard (grupos novos
SUN_2025_CRIMP_axial_standard? verificar token matching: casos sun2025efa109235_axial_*_standard)
— grade log {3,3, 4,7, 6,5, 9,0}e-11 (prior faixa per-par §4.7). GATE: tripé<0,1 nos 2
(candidato 6,53e-11 → 0,016/0,035 e 0,054/0,082); axiais crimp ×2 + transversais
bit-intocados (a versão per-PAR foi MEDIDA pelo agente e quebra 3 casos — escopo por token é
obrigatório); prov: proxy do canal axial ausente (L1), revisitar quando L1-v2 aterrissar;
anexa falsificação do flank compartilhado (exp necessário ≈4,5 > banda 1,5-3,2).

**YANG_2023_IJPEM: ZERO fitável** (varredura tri-falsificada: k_ratchet inerte no 0,25;
delta_free binário; loose_amp_exp piora tudo) → 7 casos ficam FILA item 1 com a evidência
nova anexada. Nenhum prereg.

## F3-SECOS (SUN nogrease ×2) — prereg separado (envolve trim/exceção)

Grupo per_case nogrease: tr_loose_gain=0,6 sub-crítico (gate de robustez: tripé passa em
{0,4; 0,6; 0,8}) + k_wear_spec compartilhado lido do slope Estágio II (grade {1,5, 2,5, 4}e-14;
1,25× acima da banda KB — aviso esperado, rotular como F2-P2.1) + emb per-caso L24 (3,0/1,5 µm)
+ TRIM exceção-C na regra "slope local >2× mediano do Estágio II" (std N≤6596; crimp N≤9514;
4 provas do agente: mecanismo declarado no paper (trinca de cisalhamento F→0), changepoint
objetivo 20-67×, concentração da violação pós-onset, insensibilidade a 3 janelas). GATE:
tripé<0,1 na janela nos 2 × 3 gains; greased ×2 + axiais ×4 intocados. Rota alternativa
integral (FatigueLoss ancorada em N_frat) fica ofertada ao professor (item 3).

## (próximas seções conforme a varredura avançar)
