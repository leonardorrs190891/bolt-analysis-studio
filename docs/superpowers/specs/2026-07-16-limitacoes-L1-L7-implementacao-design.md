# Design — Implementação das limitações L1–L7 no BAS V2 (2026-07-16)

**Objetivo:** fechar os gaps declarados em `New_Theory/variable_explorer/concept_coverage.html`
usando a proveniência da Rodada 5 (36 papers, 33 notas, 336 CSVs em `BAS_V2_papers/F...`),
integrando ao ciclo de otimização/validação do main **sem colidir com a campanha ativa**.

**Base técnica:** `Models/CALIBRATION_AND_VALIDATION/curve_library/ANALISE_MODELOS_R5.md`
(síntese por limitação, com valores e vereditos). Ler antes deste doc.

---

## 1. Decisões estabelecidas (instruções do professor nesta sessão)

1. Solucionar **todos** os gaps do concept_coverage com a proveniência coletada.
2. O main está com a campanha contínua de otimização/validação → trabalhar em **feature branch**;
   integração ao main é decisão do professor (regras de promoção MEM por classe de procedência).
3. Metodologia MEM (`docs/.../METHODOLOGY.md`): baseline → orçamento de erro → alavancas por
   legitimidade → guard-rails → parada → adoção.
4. Formas novas **default-inertes** (regra da casa) — o engine com flags desligadas reproduz o
   comportamento atual bit-a-bit.
5. Validação: suíte completa (180 casos), tripé por curva **MAE/maxerr/σ_res** nos gates.

## 2. Decisões tomadas em aberto (sinalizadas para override do professor)

| # | Decisão | Alternativa rejeitada | Racional |
|---|---|---|---|
| D1 | **Branch único** `feature/l1-l7-gaps`, commits por fatia | branch-por-fatia | fatias têm dependência fraca (KB→formas); rebase múltiplo contra main quente custa mais que vale; commits atômicos por fatia preservam bisect |
| D2 | Ordem por alavancagem×risco: KB → L3 → L1 → L2 → L5 → L7+C2 → L4(doc) → wiring | ordem numérica L1..L7 | L3/L1 atacam falsificações ativas (B1, roadmap #4/#9); L2 é proveniência-primeiro (ver D5) |
| D3 | `adopted_configs.json` e `joint_calibrations.json` **intocados** | adotar direto | são da campanha/professor; este branch entrega CAPACIDADES validadas + números de gate; adoção = prereg da campanha depois |
| D4 | Casos novos wired: Zhang 2018/2019 + Liu 2020 (F/F0) como PACK (padrão PR-26); Nah 2014 opcional (relaxação, x=horas) | wired nenhum | são as únicas curvas F/F0 novas da R5; viram alvo do gate L1 |
| D5 | Gate L2 = **substituição de proveniência com erro ≤ igual** (não promessa de ganho de MAE) | prometer ganho | o erro Rousseau já foi fechado pela capacidade Cattaneo-Mindlin (2026-07-07, opt-in); a lei física k_j(geom) dá a mesma resposta COM proveniência — se der pior, a lei fica documentada e o CM permanece |
| D6 | Sem push; staging **explícito por arquivo** (hazard OneDrive/sessão paralela) | — | memória do projeto |

## 3. Abordagens consideradas

- **A (escolhida): branch único com fatias sequenciais gateadas.** Cada fatia = TDD + flag
  default-inerte + gate quantitativo + relatório. Integração final por PR/merge quando o
  professor decidir.
- **B: branch por fatia.** Isolamento máximo, mas 7 rebases contra um main que recebe commits
  diários da campanha; overhead > benefício (fatias quase não se tocam em arquivo).
- **C: direto no main via preregs da campanha.** Rejeitado pela instrução (main ocupado) e por
  misturar o ciclo exploratório da campanha com formas novas de engine.

## 4. Arquitetura das fatias

Contrato comum a TODAS: (i) teste primeiro; (ii) flag/campo `JointMaterial` default-inerte com
teste de bit-identidade (flag off ⇒ história idêntica); (iii) `ParameterRule` no
`parameter_registry` para todo campo fitável novo (senão `active_candidates` explode — by design);
(iv) gate quantitativo declarado ANTES de rodar (prereg); (v) `ast.parse` + suíte pytest do
CLAUDE.md; (vi) encoding utf-8.

### Fatia 0 — Proveniência no knowledge_base (sem engine)
Âncoras R5 em `calibration/knowledge_base.py`/dados: tabela `k_wear_spec` por **interface+par**
(rosca 35CrMo/SCM435 8,34e-15 · faiamento Q355B/Q235B 6,5–7,0e-12 · bandas Fouvry/Warmuth),
µ_rosca por coating (zinco 0,150/DLC 0,126), classes de `C_creep` (Nah α,β por espessura; âncora interna;
JCSR; Caccese; Qin; Lakes), constantes k_j (Pedersen Eq.31; Wileman A,B por material), bound L7
(1–10 kJ/mm³). `anchor_priors`/`check_input` passam a avisar fora-da-banda por interface.
**Gate:** testes de KB (query por par/interface devolve valor+proveniência+banda).

### Fatia 1 — L3: acoplamento F_amp↔δ (roadmap #4)
Em disp-mode, `F_amp_eff = min(F_amp_in, µ_eff(F0)·F0)`; µ_eff com knockdown em F0 baixo
(forma: 2 limiares Measurement2021 `Fa=0,199·F0−5,3`/`Fb=0,347·F0−5,9` reescalados por
geometria; Murai 0,46→0,24). Opt-in adicional: decaimento do teto de gross-slip com desgaste
(JMP: FS→FR=70–86%) acoplado ao `surface_damage D`. Estende o modo `couple_famp_slip` existente.
**Gate:** bit-identidade off; com flag on, sem regressão global (mediana/`>0.10`-count não pioram)
e coerência qualitativa nos casos força-mode com F_amp reportado.

### Fatia 2 — L1: perda por desgaste de flanco ∝ A_F (roadmap #9)
Estender `ThreadFrettingLoss`: slip de flanco axial `s_th ∝ A_F/k_rosca` (elasticidade da rosca ⇒
∂/∂A_F ≠ 0 estrutural), canal desgaste→perda **sem rotação** (forma Zhang 2018/2019), nível
`k_wear_spec` de rosca semeado do KB (8,34e-15) e calibrado **per-rig** no trilho axial
(Liu2016/Liu2017/H.Li2022 — fit em curvas completas, lição 2026-07-08). Escala super-linear de
amplitude do Liu 2020 (expoente 1,5–1,6) como forma candidata do expoente de slip.
**Gate (prereg):** Gate-B1 re-executado sai de ∂(fim)/∂A_F≡0 para ordem −2,2e-5/N (sinal e
ordem de grandeza; alvo ±2×); casos Zhang/Liu2020 recém-wired com MAE ≤ 0,10 mediano; ZERO
regressão no transversal (não excitado ⇒ registry não oferece o parâmetro lá).

### Fatia 3 — L2: lei k_j(geometria, material)
`library_common`/geometry: `k_j_from_geometry(d, L, E, d_furo, d_arruela, mode)` com
`mode="pedersen"` (Eq.31 + transição de largura) primário e `"wileman"` (A,B por material)
cross-check; opt-in de dependência de carga via forma elíptica de Grosse (1 parâmetro:
deformação crítica de separação) afetando Φ. Default = comportamento atual.
**Gate:** conforme D5 — Rousseau steel t10/12/14 + Zhang2006 clamped-length com erro ≤ estado
atual (com CM ligado onde adotado) E proveniência física substituindo o ajuste; sem regressão
global. Registrar o confronto Pedersen-vs-Wileman (24% vs 45–59%) no relatório.

### Fatia 4 — L5: creep — docstring + forma saturante opt-in + classes
(a) Corrigir docstring do `CreepLoss` (é log-t, não Norton-Bailey) e documentar a coincidência
com a regressão do Nah (forma certa para faiamento). (b) `creep_mode="saturating"` opt-in:
`Δ=Δ_max·(1−exp[−(t/t_c)^α])` (forma Alamos; `t_c` sensível a pressão — consistente com o gate
de conformação). (c) Classes de par no KB (Fatia 0).
**Gate:** bit-identidade; casos de creep (JCSR/Caccese/Qin/li2022marstruc/Lakes-interpretado)
sem regressão; saturante vs log-t comparados no relatório (adoção fica com o professor).

### Fatia 5 — L7 bound + C2 viscoso (código)
(a) Check de sanidade no budget do colapso: energia de remoção implícita ∈ ~1–10 kJ/mm³
(warning no relatório de energia, não-fatal). (b) C2: sourcing do termo viscoso de Rayleigh via
`W_ext` no modo axial-força OU exclusão do canal viscoso do residual axial (escolher pelo menor
diff; testar conservação).
**Gate:** residual axial ≈ 0 nos casos força-mode (era −242…−12 J); residual transversal
inalterado; teste de conservação novo.

### Fatia 6 — L4: documentação (sem engine)
`MODEL_LEGITIMACY.md` §4.9 append: null 3× confirmado; precedentes de forma (n_p≈0,5–0,6
sub-GPa; teto de aspereza 1,5·H como sanity de `p_ref`; saturação em deslocamento ~5 ciclos vs
energia que não satura — Etsion×Frérot); valor segue dependente do experimento âncora âncora interna.

### Fatia 7 — Wiring de casos novos (D4)
Zhang 2018 (Tests1-4, 3 preloads, locker on/off) + Zhang 2019 (4 grupos) + Liu 2020 (3 preloads
× 4 amplitudes × 2 coatings) como `ValidationCase`s PACK (loader x|cycle, x_scale; padrão
PR-26); Nah 2014 opcional (x=horas via freq). Aparecem no report mestre com coluna campanha.

### Fatia 8 — Relatório final + handoff
Re-run `validation.report --all` no branch; painel antes/depois por fatia (mediana, >0,10,
tripé); tabela "capacidade → gate → resultado → recomendação de adoção por classe de
procedência"; atualização do `concept_coverage.html` (seção de limitações) SÓ no branch.

## 5. Riscos e guard-rails

- **Colisão com a campanha:** nunca tocar `adopted_configs.json`/`joint_calibrations.json`;
  staging explícito; rebase só no fim; fits longos em FOREGROUND (memória: background colide).
- **Regressão silenciosa:** teste de bit-identidade por flag; suíte completa por fatia; painel
  comparativo automático.
- **Falso fechamento (L2):** D5 explícito — se a lei física der pior que o CM adotado, ela entra
  como proveniência documentada, não como substituição.
- **Custo:** fatias 1–3 são as caras (engine+fit); 0/4/5/6 são baratas. Parada MEM se um gate
  falhar 2 preregs seguidos → vira falsificação documentada (como B1), não força a adoção.

## 6. Critério de sucesso global

Todas as fatias com gate PASS ou falsificação documentada; concept_coverage sem item "aberto"
sem dono (cada limitação → capacidade validada, bound documentado, ou experimento/tema de
rodada 6 nomeado); zero regressão na mediana global e no count >0,10 com flags off; decisão de
adoção por fatia entregue ao professor em tabela única.
