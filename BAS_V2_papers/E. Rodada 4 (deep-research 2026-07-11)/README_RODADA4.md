# Rodada 4 — biblioteca de curvas digitalizadas (2026-07-12)

20 PDFs (13 baixados manualmente pelo professor + 7 da varredura de 2026-07-11), um
**estudo/artigo por agente**, cada um com nota de aparato + curvas redigitalizadas via
PyMuPDF (helper `pdf_tools.py`). **19 notas**, **169 CSVs**, **~3602 pontos**.

- Notas: `apparatus_notes/<prefix>.md` — citação+DOI, gap, rig, corpo-de-prova, matriz de
  ensaios, nuances, conclusões, inventário de curvas, mapeamento V2, ressalvas de digitalização.
- Curvas: `digitized_csv/<prefix>_<label>.csv`. Cabeçalho `x,F_over_F0` (curvas de pré-carga)
  ou `x,y` com unidades documentadas na nota (âncoras de desgaste G2). Figuras em `figures/`.
- **NÃO wired** em `validation_cases.py` ainda — esta pasta é staging desta rodada; a ingestão
  no conjunto canônico (`DIGITIZED_CASES`) é follow-up sob revisão do professor.

## Convenção de x
- Ciclos de vibração: `x = número do ciclo`.
- Creep/relaxação estática: `x = tempo em segundos`.
- Reaperto/remontagem: `x = número do aperto/remontagem`.
- Âncoras de fretting (G2): `x,y` = grandeza de desgaste vs energia/pressão (sem F/F0).

## Curvas por artigo

| prefix | artigo | DOI | rig / modo | #csv | tipo |
|---|---|---|---|--:|---|
| liu2016wear | Liu et al. 2016, Wear 346-347 (M12, axial) | 10.1016/j.wear.2015.10.012 | axial **força** 30 Hz | 15 | pré-carga vs ciclos (varredura torque/amp + MoS2/seco + reaperto) |
| yang2023ame | Yang et al. 2023, Adv Mech Eng (CFRP biaxial) | 10.1177/16878132221145342 | biaxial MTS **força** 2 Hz | 6 | pré-carga vs ciclos (transv/axial/biaxial + F0) |
| chu2026ti | Chu et al. 2026, Tribol Int 223 (MJ10) | 10.1016/j.triboint.2026.112193 | Junker **deslocamento** 10 Hz | 10 | pré-carga vs ciclos (D/F0/Ra sweep) |
| sun2025efa109235 | Sun et al. 2025, EFA 169 (crimp GH4169) | 10.1016/j.engfailanal.2024.109235 | transv **desloc** + axial **força** | 8 | pré-carga vs ciclos (crimp vs padrão) |
| sun2025efa110030 | Sun et al. 2025, EFA 182 (remontagem MJ8) | 10.1016/j.engfailanal.2025.110030 | transv **desloc** 12,5 Hz | 10 | 5 F/F0 + 2 torque + 2 µ + 1 fadiga (y documentado) |
| eccles2010 | Eccles et al. 2010, Proc IMechE C 224 | 10.1243/09544062JMES1493 | Junker+axial **desloc** 12,5 Hz | 10 | pré-carga vs tempo (prevailing torque, destacamento) |
| jcsr2023 | Yang, Bai & Ding 2023, JCSR 211 | 10.1016/j.jcsr.2023.108211 | relaxação estática (ambiente) | 6 | pré-carga vs tempo (4 materiais × ambiente) |
| caccese2009 | Caccese et al. 2009, Compos Struct 89 (+DTIC ADA429921) | 10.1016/j.compstruct.2008.07.031 | relaxação estática | 22 | clamp-up vs tempo (4 pares, reaperto, T) |
| qin2024acm | Qin et al. 2024, Appl Compos Mater 31 | 10.1007/s10443-024-10214-3 | relaxação estática térmica | 5 | pré-carga vs tempo (interferência + 25/100/150 °C) |
| lakes2007jemt | Jaglinski et al. 2007, JEMT 129 (aço/Al-Si) | 10.1115/1.2400262 | creep térmico estático | 6 | tensão do parafuso vs tempo (220/240/260 °C) ⚠ |
| alsardia2024 | Alsardia 2024, Acta Polytech Hung 21 | (OA, sem DOI) | reaperto estático (torque) | 4 | pré-carga vs nº do aperto (4 lubrificações) |
| basavahess1998 | Basava & Hess 1998, JSV 210 | 10.1006/jsvi.1997.1330 | **SIMULAÇÃO** RK (axial) | 21 | ⚠ saída de modelo, NÃO experimental |
| baydoun2019wear | Baydoun & Fouvry 2019, Wear 426-427 | 10.1016/j.wear.2018.12.022 | fretting flat-on-flat | 8 | desgaste vs energia/pressão/amp/freq (G2) |
| fouvry2007ti | Fouvry et al. 2007, Tribol Int 40 | 10.1016/j.triboint.2007.02.011 | fretting (coatings+Ti64) | 8 | desgaste vs energia + capacidade χ (G2) |
| fouvry2017ti | Fouvry et al. 2017, Tribol Int 113 | 10.1016/j.triboint.2016.12.049 | fretting Ti64 cyl-on-plane | 10 | α vs potência friccional + tabela (G2+G8) |
| vanpeteghem2011wear | Van Peteghem et al. 2011, Wear 271 | 10.1016/j.wear.2011.01.060 | fretting Ti64 (força normal variável) | 5 | desgaste vs energia/ciclos (G2+G8) |
| arnaud2021ti | Arnaud et al. 2021, Tribol Int 161 | 10.1016/j.triboint.2021.107077 | **modelagem** + validação Ti64 | 9 | α exp vs modelo + perfis de escara (G2) |
| baydoun_arxiv | Baydoun & Fouvry 2020, Tribol Int 147 (=arXiv 2101.12014) | 10.1016/j.triboint.2020.106266 | fretting (oxigenação) | 4 | distância de oxigênio d_O vs f/p/N/amp (G2) |
| grzejda2026mat | Grzejda et al. 2026, Materials 19 | 10.3390/ma19071414 | multi-parafuso cíclico (Instron) | 2 | ⚠ BENCHMARK NULO (F/F0≈1,0) |

## Cobertura por lacuna (G1–G8)

- **G1 axial ∝ A_F**: `liu2016wear` (varredura de amplitude 7,5–12,5 kN @ M0 fixo — **o alvo nº1
  da rodada**, d(perda)/d(A_F) direto num rig irmão do Liu2017), `yang2023ame` (axial isolado +
  biaxial), `sun2025efa109235` (ramo axial 7,5/17,5 kN). `basavahess1998` daria o G1 mas é
  **simulação** (ver ⚠).
- **G2 âncora de pressão (W_conf_ref, n)**: `baydoun2019wear` + `fouvry2007ti` + `fouvry2017ti`
  + `vanpeteghem2011wear` + `arnaud2021ti` + `baydoun_arxiv`. **Síntese honesta:** as pressões de
  contato ficam **abaixo** da janela de parafuso 0,5–1,5 GPa (Baydoun2019 10–175 MPa; Van
  Peteghem 0–525 MPa; Fouvry2017 131–525 MPa; Baydoun2020 25–175 MPa; Arnaud 100–525 MPa com pico
  local ~1,2–1,3 GPa), **exceto os revestimentos duros do Fouvry2007 (>1 GPa)**. Elas dão a
  **forma** do expoente de pressão (Baydoun2019 **n_p≈0,5–0,6**; amplitude n_δg≈0,7–0,8; freq
  n_f≈−0,3; ciclos n_N≈0) e o coeficiente energia-desgaste α (4,4e-5 mm³/J flat-on-flat aço;
  1,1e-4 Ti64; 62,5–6919 µm³/J por par nos coatings — spread >100× confirma "constante por par").
  **NÃO fecham** a âncora de ~1,2 GPa do `W_conf_ref` (§4.9): são precedente de forma, não valor
  plug-in. α·µ ⇒ ~1e-17–1e-15 1/Pa, abaixo do bound atual do `k_wear_spec`.
- **G3 creep por par tribológico**: `jcsr2023` (comum/galv/inox/**GFRP**), `caccese2009` (C/Al,
  C/aço, C/C, Al/Al-controle), `qin2024acm` (CFRP-Ti), `lakes2007jemt` (aço/Al-Si + constantes
  de creep da Tabela 1). Amplia muito além do 304SS UFU.
- **G4 espessura de membro**: nenhum novo (segue só Rousseau t10/12/14). Lacuna aberta.
- **G5 reaperto / renovação de embedding**: `alsardia2024` (20 reapertos × 4 lubrif.),
  `sun2025efa110030` (remontagem MJ8), `caccese2009` (reaperto composto), `lakes2007jemt`
  (pré-condicionamento). Amplia além do Z.Liu2022.
- **G6 temperatura**: `lakes2007jemt` (220/240/260 °C), `qin2024acm` (25/100/150 °C),
  `caccese2009` (ciclagem 62 °C), `jcsr2023` (ambiente/imersão).
- **G7 travamento / lubrificação**: `eccles2010` (prevailing torque + destacamento),
  `sun2025efa109235`/`sun2025efa110030` (porca crimpada), `alsardia2024` (seco/MoS2/óleo),
  `liu2016wear` (MoS2 vs seco).
- **G8 escalas/materiais incomuns**: CFRP (`yang2023ame`, `qin2024acm`, `jcsr2023`),
  Ti-6Al-4V (`fouvry2017ti`, `vanpeteghem2011wear`), GFRP (`jcsr2023`), superligas GH4169/GH159
  (`sun2025efa109235`, `chu2026ti`), Al-Si (`lakes2007jemt`), grande M20 (`jcsr2023`).

## Ressalvas importantes (ler antes de calibrar)

- ⚠ **`basavahess1998` NÃO é experimental** — Figs 2–6 são saída de simulação Runge-Kutta de um
  modelo de parâmetros concentrados (o abstract enganou a verificação da R4). As 21 curvas servem
  só como **mapa de regimes qualitativo**. Achado estrutural: o regime de *aperto* (F/F0 sobe até
  +83%) é uma **inversão de sinal** que os 4 mecanismos atuais do V2 (todos removem pré-carga) não
  reproduzem — capacidade faltante mais fundamental que o item 9 do roadmap.
- ⚠ **`lakes2007jemt`** — as curvas são **tensão do parafuso A QUENTE** (sobe a ~1,5× por expansão
  térmica diferencial antes do creep relaxar), normalizadas ao ponto t=10 s; a "perda ~total" do
  headline é **pós-resfriamento** (não visível nas curvas). O creep é o *declínio a partir do pico
  térmico*, não a razão vs inicial — interpretar antes de usar como C_creep.
- ⚠ **`grzejda2026mat`** — controle negativo: F/F0 ≈ 1,0 (±2%). O modelo deve prever ≈zero perda.
  Só janelas curtas (6–100 ciclos); não garante alto ciclo. A pequena variação é prying
  (redistribuição estrutural multi-parafuso), não afrouxamento.
- **Modo de controle** (crítico p/ o V2): força para `liu2016wear`/`yang2023ame`/`sun*axial`;
  deslocamento (Junker) para `chu2026ti`/`eccles2010`/`sun*transversal`.
- Vários agentes acharam **erros no próprio paper** (legendas trocadas, defeitos de tipografia
  decimal, inconsistências de tabela) — todos documentados nas notas, não corrigidos silenciosamente.
- Âncoras G2 usam header `x,y` (unidades na nota), NÃO `F_over_F0`. `sun2025efa110030` mistura
  F/F0 com torque/µ/fadiga — checar o y por arquivo na nota.

## Não digitalizados / pendências

- Nenhum PDF ficou sem processar. `basavahess1998` reclassificado (simulação).
- **G4 (espessura de membro)** segue sem fonte nova além do Rousseau — alvo de uma próxima rodada.
- Ingestão em `DIGITIZED_CASES` (`validation_cases.py`) + wiring dos modos de controle/tempo:
  follow-up sob decisão do professor.
