# HANDOFF — Biblioteca de papers, curvas e dados de calibração (BAS V2)

> Documento auto-contido para retomar o trabalho em outra sessão/prompt.
> Estado em 2026-07-03. Tudo descrito abaixo já está no repo e testado.

---

## 1. Mapa de pastas

```
BAS_V2_papers\                                   ← 67 PDFs (este README + HANDOFF)
├── A. Fontes de alta-resolucao (deep-research)\   ← 9 papers prioritários (TODOS digitalizados)
├── B. Biblioteca local catalogada (...)\          ← 51 papers catalogados (curvas de tabelas em extracted_csv)
├── C. Casos no app\                               ← 2 papers dos case studies embutidos
└── D. Rodada 3 (download institucional)\          ← 5 papers (reaperto, creep, axial×freq, 2 referências)

Models\CALIBRATION_AND_VALIDATION\
├── curve_library\
│   ├── digitized_csv\            ← 108 curvas digitalizadas das FIGURAS (cycle,F_over_F0)
│   │                                manifest: DIGITIZED_CSV_MANIFEST.md
│   ├── extracted_csv\            ← 200 curvas de TABELAS das notas MD
│   │                                manifest: EXTRACTED_CSV_MANIFEST.md
│   ├── apparatus_notes\          ← ★ 16 notas: aparato, corpo-de-prova, matriz de ensaios,
│   │                                ressalvas de digitalização e mapeamento → tuners V2
│   │                                começar por MSD_BLOCK_COVERAGE.md (matriz de lacunas)
│   ├── pdfs_open_access\         ← PDFs open-access, nomes canônicos (liu2025_scirep_M16.pdf...)
│   ├── pdfs_manual_download\     ← PDFs paywall baixados (liu2022_istruc_retightening.pdf...)
│   ├── DOWNLOAD_CHECKLIST.md     ← status de download/digitalização (tudo resolvido)
│   ├── DEEP_RESEARCH_REPORT.md / _R2.md / _R3.md  ← ranking e justificativa das fontes
│   └── CALIBRATION_CURVE_DATABASE.md
├── 01..93_*.md                   ← notas por paper da biblioteca B (com tabelas de curvas)
└── curve_library\digitized_csv\... (ver acima)

src\bolt_analysis_studio\core\validation_cases.py  ← 128 ValidationCases (DIGITIZED_CASES)
```

---

## 2. Papers digitalizados (curvas + aparato) — os 13 principais

| Paper | PDF | DOI | Regime | Curvas | Nota de aparato |
|---|---|---|---|--:|---|
| Liu 2025 Sci Rep — **M16**x120 8.8, F0=60 kN, 0.25–0.8 mm | A/ | 10.1038/s41598-025-02936-6 | transversal disp, 3 estágios | 7 | liu2025_scirep_M16.md |
| Bauer 2024 EFA — M8 (l_K=8, 20 kN) + M12x1.5 (l_K=12, 50 kN), s_crit=99 µm | A/ | 10.1016/j.engfailanal.2024.108404 | transversal disp, colapso | 9 | bauer2024_efa.md |
| Liu 2017 Trib Int — M12x1.75 10.9, axial 30 Hz, P0 15–21 kN, A_F 7.5–12.5 kN | A/ | 10.1016/j.triboint.2017.05.037 | **AXIAL força** | 9 | liu2017_triboint_axial.md |
| Lu 2024 Sensors — M8 8.8, 0.25–2.0 mm, 4–28 N·m, placas aço-níquel | A/ | 10.3390/s24113306 | transversal disp | 10 | lu2024_sensors_M8.md |
| Rousseau 2025 Materials — M12, aço vs HDPE, t=10/12/14, grips 25/29/33 | A/ | 10.3390/ma18020462 | transversal, rigidez de membro | 6 | rousseau2025_materials_M12.md |
| Icmez 2025 EJRND ('demir2024') — M8, fatorial 0.3/0.4 mm × 14.3/17.6 kN × l_K 13.8/19.8 | A/ | 10.56038/ejrnd.v5i1.693 | transversal (DIN 65151) | 8 | demir2024_ejrnd_M8.md |
| Yang 2021 S&V — M8x70 8.8, transversal+axial 90°, ξ_crit=0.075 mm/kN, 10 Hz | A/ | 10.1155/2021/1441122 | **composto** | 6 | yang2021_sv_combined.md |
| Yang 2019 S&V — M10 ~26 kN, 0.4/0.6 mm, 5/10 Hz, amplitude variável | A/ | 10.1155/2019/2036509 | transversal + blocos | 5 | yang2019_sv_M10.md |
| Karlsen 2022 EFA — M30 (353 kN) / M42 (706 kN), HV vs Vibralock, 1 Hz | A/ | 10.1016/j.engfailanal.2022.106590 | transversal, tamanho extremo | 11 | karlsen2022_M30M42.md |
| Sandia 2021 C-Beam — modal ~280 Hz, ~780 N (⚠ diâmetro não reportado) | B/ | 10.1007/978-3-030-47626-7_30 | modal/flexão, micro-slip | 6 | sandia2021_cbeam.md |
| **Z. Liu 2022 Structures — REAPERTO** M12 8.8, T=80 N·m, 0.3 mm, 12.5 Hz | D/ | 10.1016/j.istruc.2022.08.049 | reapertos sucessivos ± óleo | 21 | liu2022_istruc_retightening.md |
| **Y. Li 2022 Marine Struct — CREEP estático** M16 304SS, 5/10/15 kN, Ra sweep | D/ | 10.1016/j.marstruc.2022.103263 | creep, SEM vibração (x = MINUTOS) | 6 | li2022_marstruc_contact_creep.md |
| **H. Li 2022 Trib Int — axial×frequência** M10, A_F=10 kN, 10/15/20 Hz | D/ | 10.1016/j.triboint.2022.107933 | axial força | 4 | li2022_triboint_axial_freq.md |

**+ Yang 2023 IJPEM** (10.1007/s12541-023-00783-x, M6/M8 Junker 0.15–0.65 mm): PDF completo
indisponível (preview deletado) — **substituído** pelas 9 curvas tabuladas em
`extracted_csv/10_Yang_2023_*`; condições e config MSD completa na nota
`Models/CALIBRATION_AND_VALIDATION/10_Yang_2023_phenomenological_model.md`.

**Referência sem curvas** (pasta D): wang2020_aime (FEM-only; taxonomia stick/partial/full-slip,
relação torque-preload M14) e cja2022 review (fontes p/ locking devices).

## 3. Papers catalogados (pasta B, 51 PDFs — curvas de tabelas já em extracted_csv)

Jiang 2003/04 · Junker (via notas) · Nassar/Housari 2006/07/09 · Zhang/Jiang 2006 ·
Yang/Nassar 2011 · Hattori 2010 · Eccles 2010 · Dinger/Friedrich 2011 · Gong/Liu 2018/19 ·
Chen 2017 · Sase/Koga 1996 · Sanclemente/Hess 2007 · Amano 2024 · Du 2022 · Li/Liu 2020 ·
Liu/Cai 2016/17 · Su/Ye 2016 · Eraliev 2021 · Bouzid 1995/2006 · Abid/Nash 2014 ·
Hu/Zhang 2020 · Karlsen/Lemu large-bolt · anti-loosening nuts/washers · sine-on-random ·
3-stage random-vibration strain · time-related preload relaxation · failure behaviour ·
loosening/sliding bolt-nut · preload decrease mechanism · tightening process · double thread ·
jack bolt nuts · clearance/thread fit · friction coefficients · clamped length/direction ·
dynamic shear · math model · cap screws · early stage (app) · new criteria (app) ·
flange/gasket set (creep, thermal, stamina, leakage, deflections) · CFRP/composite set ·
railroad spike FEA · surface texturing · bolt load scatter · torque-preload fusion ·
AI chassis prediction · stainless slip-resistant · large-diameter fatigue.
(Títulos completos = nomes dos arquivos na pasta B; tabelas por nota em
`Models/CALIBRATION_AND_VALIDATION/NN_*.md`; 200 CSVs em `extracted_csv/` c/ manifest.)

---

## 4. Dados disponíveis por curva/caso

- **CSV**: 2 colunas `cycle,F_over_F0` (UTF-8, header). Exceção: `li2022marstruc_creep_*_min.csv`
  → coluna cycle = **minutos** (creep estático).
- **ValidationCases** (`src/.../core/validation_cases.py`, lista `DIGITIZED_CASES`, 117 casos
  + 11 legados = **128**): cada caso tem bolt_size/d/p, F0, %yield, amplitude, freq, n_cycles,
  μ, lubrificação, DOI, `reference_csv_path` e pontos experimentais **lidos do CSV em
  import-time**. Todos sintetizam modelo MSD válido (test_case_study_models passa).
- **Notas de aparato** (`apparatus_notes/*.md`): rig/norma/sensores, specimen (material, E/ν,
  Sy, dims), matriz de ensaios completa, ressalvas de digitalização, seção
  "V2 calibration mapping" (que tuner cada dataset restringe).
- **Lacunas por fonte** (grip, espessuras, μ): `apparatus_notes/MSD_BLOCK_COVERAGE.md`
  com regras de preenchimento (databases ISO do app, grip≈2–3×d, μ via coef. de torque).

## 5. Como usar (calibração V2)

1. **No app**: Case Studies → escolher caso (ex.: `Liu2025 M16 0.40mm`) → **Calibrate**
   (trim de ciclos + tuner `slip_onset_W` + MAE/RMSE ao vivo). O overlay usa
   `reference_csv_path` automaticamente.
2. **Programático**: `StagedCalibrator` (`calibration/staged_calibrator.py`) com o CSV como
   referência; server tuner: `python -m bolt_analysis_studio.calibration.server` → localhost:8765.
3. **Modo de carga**: transversais → `step_cycle(delta_amp=...)`; **axiais**
   (`Liu2017 axial *`, `Li2022 axial *`) e modal (`Sandia2021 *`) → modo força
   (`F_amp`), amplitude transversal = 0 nesses casos.
4. **Trims obrigatórios**: finais com fratura por fadiga são out-of-model —
   Yang2021 (pós-N2), `liu2022_fig8_multi_t4` (>~1200 cyc), `li2022ti_axial_10Hz_full`
   (>3.3e5 cyc), Liu2025 pós-N_D.
5. **Alvos por tuner** (resumo; detalhe nas notas):
   - `k_emb_scale`: quedas iniciais (todos); HDPE Rousseau (embedding puro)
   - `k_creep_scale`: **li2022marstruc creep** (isolado!), caudas Liu2017
   - `k_wear_scale_tr`/`Phi_tr_correction`: sweeps de amplitude (Liu2025, Lu2024, Yang2023)
   - `slip_onset_W`: casos below-threshold (Lu2024 0.25mm, Yang2023 0.18/0.15mm, Sandia,
     Bauer s_crit=99 µm)
   - `surface_damage` (c_D, k_dmg_mu, k_dmg_wear): colapsos (Bauer fig8, Liu2025 0.8mm,
     reaperto Liu2022 fig8)
   - **reaperto/embedding renewal (prioridade #5)**: série liu2022_fig6/7/8 (dry vs oil,
     release-angle vs direct)
   - **trilho axial (prioridade #3)**: liu2017 (9) + li2022ti (4) — perfil axial ainda NÃO fitado
   - acoplamento F_amp↔delta_amp (prioridade #4): yang2021 composto (ξ sweep)

## 6. Pendências opcionais

- Rodar o **fit do perfil axial** (dados prontos, modo força).
- Yang 2023: se o PDF completo (11 pág.) aparecer, re-digitalizar Figs 1–9 em alta fidelidade
  (hoje: curvas aproximadas de tabela).
- Rodada 4 de busca (Scopus institucional, por citação dos 13 papers-base) se quiser
  ampliar além das 308 curvas atuais.
