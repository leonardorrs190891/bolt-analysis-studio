# Rodada 4 — deep-research (2026-07-11)

Varredura dirigida às lacunas de calibração G1–G8 (axial ∝ A_F, âncora de pressão
W_conf_ref/n, creep por par, espessura de membro, reaperto, temperatura, locking/lube,
escalas/materiais incomuns), com lista de exclusão dos ~75 papers já ingeridos.

> **STATUS 2026-07-12 — TODOS baixados e DIGITALIZADOS.** Os 13 pendentes foram baixados
> manualmente pelo professor (+ os 7 já em disco). Um agente por artigo redigitalizou as
> curvas: **19 notas, 169 CSVs, ~3602 pontos** em `BAS_V2_papers/E. Rodada 4 (deep-research
> 2026-07-11)/{apparatus_notes,digitized_csv,figures}/`. Manifesto completo + cobertura por
> lacuna + ressalvas: **`E. Rodada 4.../README_RODADA4.md`**. Reclassificações: `basavahess1998`
> é SIMULAÇÃO (não experimental); `grzejda2026mat` é benchmark NULO; as âncoras Fouvry (G2)
> ficam sub-GPa exceto coatings do Fouvry2007 — dão a FORMA do expoente de pressão (n_p≈0,5–0,6),
> não fecham a âncora de ~1,2 GPa do W_conf_ref. Ingestão em `validation_cases.py` = follow-up.

**Nota de execução:** o workflow (102 agentes) completou busca + fetch, mas o limite
mensal de gasto da org matou 49 dos ~78 verificadores e a síntese final — a triagem
abaixo foi feita manualmente a partir do journal (20 fontes com claims extraídos;
8 claims verificados 3-0/2-1 antes do corte). Consequência: para os itens paywalled,
"contém curvas experimentais" está confirmado no nível do abstract, mas nº de figuras
e matriz de ensaio ficam para confirmar no PDF.

## Baixados nesta rodada → `BAS_V2_papers/E. Rodada 4 (deep-research 2026-07-11)/`

| # | Paper | DOI / fonte | Lacuna | Por que vale |
|---|---|---|---|---|
| 1 | **Baydoun & Fouvry 2019**, "Fretting wear rate evolution of a flat-on-flat low alloyed steel contact: a weighted friction energy formulation", *Wear* 426–427:676–693 | [10.1016/j.wear.2018.12.022](https://doi.org/10.1016/j.wear.2018.12.022) (PDF do autor via HAL/Wayback) | **G2 (melhor âncora)** | Flat-on-flat 35NCD16 com **pressão quase-constante controlada** + varredura de pressão/amplitude/frequência/duração; formulação energia-ponderada → proveniência para expoente de pressão do gate de conformação. Ressalva: transição abrasivo→adesivo ⇒ expoente condicionado ao regime. |
| 2 | **Arnaud, Baydoun & Fouvry 2021**, "Modeling adhesive and abrasive wear phenomena in fretting interfaces", *Tribology Int* 161:107077 | [10.1016/j.triboint.2021.107077](https://doi.org/10.1016/j.triboint.2021.107077) (HAL via Wayback) | G2 (lead) | Coeficientes de desgaste energético separados por regime (adesivo vs abrasivo) dirigidos por oxigenação do contato — base física candidata para gate dependente de pressão. Modelagem (sem curvas F/F0). |
| 3 | **Baydoun et al.**, companion arXiv [2101.12014](https://arxiv.org/abs/2101.12014) | arXiv OA | G2 (lead) | Companion OA que cita e estende o item 1 (confirma pressão constante do flat-on-flat). |
| 4 | **Pelletier, Caccese & Berube**, "Influence of stress relaxation on clamp-up force in hybrid composite/metal bolted joints" — **relatório DTIC ADA429921** (companion OA do paper *Composite Structures* 89(2):285–293, 2009) | [10.1016/j.compstruct.2008.07.031](https://doi.org/10.1016/j.compstruct.2008.07.031) (journal, paywall) | **G3+G5+G6+G8** | Relaxação de clamp-up ≥3 meses (regimes primário+secundário) em par compósito–metal, **com sequências de reaperto** e efeitos térmicos; 3 formas funcionais ajustadas. O relatório DTIC (35 MB, escaneado) contém o programa experimental completo. |
| 5 | **(grupo Lakes/UW-Madison) 2007**, "Study of bolt load loss in bolted aluminum joints", *J. Eng. Mater. Technol.* 129:48–54 | [10.1115/1.2400262](https://doi.org/10.1115/1.2400262) (PDF do autor, silver.neep.wisc.edu) | **G6+G3+G5** | Tensão do parafuso in-situ (strain gage) por 1 semana a 220/240/260 °C, aço sobre Al-Si fundido (Figs 5–9); Tabela 1 = constantes de compliance de creep por temperatura (proveniência estilo C_creep por par); embedding ~10 % nos primeiros minutos + protocolo de reaperto. |
| 6 | **Alsardia 2024**, "Bolt preload variations during repeated tightenings", *Acta Polytechnica Hungarica* 21(2):133–150 | OA no journal (acta.uni-obuda.hu) | **G5+G7** | 20 reapertos × 4 lubrificações (as-is/dry/MoS2/oiled), M8×40 10.9, 20 N·m, 1600 medições (ISO 16047): as-is 22,8→15,7 kN; MoS2 −44,7 %; **oiled SOBE ~20 % e estabiliza** — âncora direta para `k_emb_renew` + atrito por lube. Estático (não é Junker). |
| 7 | **Grzejda, Parus & Kwiatkowski 2026**, "Behaviour of a preloaded asymmetric multi-bolted connection under cyclic loads", *Materials* 19:1414 | [10.3390/ma19071414](https://doi.org/10.3390/ma19071414) (MDPI OA) | benchmark **nulo** | **Atenção: resultado nulo** — 9 variantes cíclicas (Instron 8850, 22 kN, 10/20 kN amplitude) SEM perda de preload (±2 %). Não é curva de decaimento; vale como **controle negativo** (o modelo deve prever ~zero perda nessas condições). |

## Download manual (paywall ou bloqueio anti-bot) — ranqueado

| # | Paper | DOI | Lacuna | Rota | Por que vale |
|---|---|---|---|---|---|
| 1 | **Liu et al. 2016**, "Experimental and numerical studies of bolted joints subjected to axial excitation", *Wear* 346–347:66–77 | [10.1016/j.wear.2015.10.012](https://doi.org/10.1016/j.wear.2015.10.012) | **G1+G7 (alvo nº 1)** | institucional (Elsevier); espelho RG publication/284084916 | Mesmo grupo/rig do Liu2017 in-library, paper ANTERIOR e distinto: decaimento de clamp force axial com varredura de **torque × amplitude** + contraste MoS2 vs seco — estende d(afrouxamento)/d(A_F) num rig que já calibramos. |
| 2 | **Yang, An, Chen & Zou 2023**, "Preload loss of CFRP bolted joint without rotation under transverse and axial loading", *Adv. Mech. Eng.* 15(1) | [10.1177/16878132221145342](https://doi.org/10.1177/16878132221145342) | **G1(parcial)+G8** | **OA gold (CC-BY)** — SAGE bloqueia bot; baixar no navegador (gratuito) | Rig biaxial (2 atuadores MTS), CFRP 48 plies–aço, jet nut MJ6 (SEM rotação): curvas em tempo real Fig 3a–c + varredura de F0 (Fig 5, 6/8/10 kN); decomposição embedment 26,9–59,3 % por modo de carga — transversal vs axial vs biaxial no MESMO rig. |
| 3 | **Sun et al. 2025**, "The influence of the repeated assembly of the crimping self-locking nut...", *Eng. Fail. Anal.* :110030 | [10.1016/j.engfailanal.2025.110030](https://doi.org/10.1016/j.engfailanal.2025.110030) | **G5+G7** | **preprint SSRN [5347913](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5347913)** (gratuito no navegador) ou institucional | Reapertos cíclicos de porca auto-frenante MJ8 prateada: óxido de prata SOBE o atrito e mantém preload, microtrincas degradam fadiga — dado de reaperto por-lube além do Z.Liu2022. Confirmar no PDF se há curvas F/F0 (parte é FEM). |
| 4 | **Eccles, Sherrington & Arnell 2010**, "Towards an understanding of the loosening characteristics of prevailing torque nuts", *Proc IMechE C* 224(2):483–495 | [10.1243/09544062JMES1493](https://doi.org/10.1243/09544062JMES1493) | **G7+G5-adj** | institucional (SAGE); repositório UCLan eprint 6368 = **401 restrito**; resumo de 2 pág. em boltscience.com | Junker modificado com macacos hidráulicos: transversal + axial constante/intermitente, porcas nylon-insert novas vs reusadas, **limiar quantitativo de destacamento** (axial > preload residual) — forma falsificável para o rotation-onset/colapso. |
| 5 | **"Loss of preload of unprotected bolted joints considering environmental effects: a comparative study"**, *J. Constr. Steel Res.* 211:108211 (2023) | [10.1016/j.jcsr.2023.108211](https://doi.org/10.1016/j.jcsr.2023.108211) | **G3+G6+G8** | **CC-BY híbrido** — ScienceDirect bloqueia bot; navegador (gratuito) | 4 materiais de parafuso (comum/galvanizado/inox/**GFRP**) × 3 ambientes (indoor/outdoor/imersão em água do mar), clamp force contínua vs tempo + modelo com termo de settling inicial — creep por par + ambiente. |
| 6 | **Chu, Liu, Qin & Yuan 2026**, "Tribological characterization of loosening mechanisms in bolt-fastened structures under transverse vibrations", *Tribology Int* 223:112193 | [10.1016/j.triboint.2026.112193](https://doi.org/10.1016/j.triboint.2026.112193) | transversal core (s_crit) | institucional | Experimentos + FEM: limiar crítico de deslocamento transversal dependente de F0 e atrito (estilo s_crit do Bauer2024); preload governa via evolução de μ/desgaste (acopla com o D do surface_damage). |
| 7 | **Sun et al. 2025**, "Anti-loosening and fatigue performance of bolted joints with crimping self-locking nuts", *Eng. Fail. Anal.* 169:109235 | [10.1016/j.engfailanal.2024.109235](https://doi.org/10.1016/j.engfailanal.2024.109235) | G7 | institucional | Junker M8/M10/M12 porca crimpada vs padrão (série de tamanho num rig); ramo axial é S-N (fadiga), não decaimento. |
| 8 | **"The investigation of preload relaxation behavior of CFRP bolted joints under thermal-oxygen environment"**, *Appl. Compos. Mater.* (2024) | [10.1007/s10443-024-10214-3](https://doi.org/10.1007/s10443-024-10214-3) | G3+G6+G8 | institucional (Springer) | Relaxação CFRP 25→150 °C (retenção 95,0→79,8 %) + varredura de interferência; modelo + experimento. |
| 9 | **Basava & Hess 1998**, "Bolted joint clamping force variation due to axial vibration", *J. Sound Vib.* 210(2):255–265 | [10.1006/jsvi.1997.1330](https://doi.org/10.1006/jsvi.1997.1330) | G1 (parcial) | institucional | Axial com varredura de nível×preload; clamp force pode ficar estável, CAIR ou **SUBIR** — restrição de sinal que o mecanismo ∝ A_F deve respeitar. Transientes curtos (não N ciclos longos). |
| 10 | Fouvry leads G2 restantes: *Tribology Int* 40:1428 (2007, capacidade energética χ) [10.1016/j.triboint.2007.02.011]; *Wear* 271:1535 (2011, força normal variável Ti64) [10.1016/j.wear.2011.01.060]; *Tribology Int* 113:460 (2017, Ti64 potência friccional) [10.1016/j.triboint.2016.12.049] | — | G2 (leads) | institucional | Complementos da âncora Baydoun2019: capacidade energética por par, história de pressão, expoente de potência friccional (Ti64 = G8). |

Leads menores (não priorizados): estudo torsional do grupo Liu/Zhu (RG 329654266, modo
de carga não modelado); hal-02119945 (Rafik/AMDEM, JCM2018, HAL bloqueado por Anubis);
"Theoretical and experimental study on the damage behavior of bolted joints under cyclic
loads", *Structures* (2024, PII S2352012424016382 — confirmar curvas antes de baixar).

## Sobreposição com rodadas anteriores

- "Time–temperature-dependent response... bolted composite joints" (2018, RG 322431887)
  **já era o item 6 da R3** — segue pendente de download manual (G3+G6).
- O item JCSR desta rodada é DISTINTO do excluído "Preload loss of stainless steel bolts
  in aluminium plated slip resistant connections" (mesmo journal, paper diferente).

## Verificação pendente (cortada pelo limite de gasto)

Confirmar no PDF, ao baixar manualmente: nº de figuras/curvas e matriz completa de
Liu2016-Wear, Chu2026, Sun2025×2, Eccles2010 (o abstract confirma experimento, não a
digitalizabilidade); se o Sun2025-reaperto tem curvas F/F0 por reaperto ou só métricas
de locking; resolução das figuras do Basava&Hess (1998).
