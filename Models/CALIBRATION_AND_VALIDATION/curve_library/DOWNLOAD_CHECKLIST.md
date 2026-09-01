# Checklist de download — o que baixar e em qual pasta

> **STATUS 2026-07-02: 9/10 baixados e 10 papers digitalizados (77 curvas).**
> Todos os itens #1–#9 estão em `pdfs_open_access/` (nomes canônicos) e também em
> `BAS_V2_papers/A. Fontes de alta-resolucao (deep-research)/` (títulos completos).
> Curvas → `digitized_csv/` (ver `DIGITIZED_CSV_MANIFEST.md`); aparato + matriz de
> ensaios de cada paper → `apparatus_notes/<paper>.md`. O Sandia C-Beam (R2) também
> foi digitalizado. **Falta apenas #10 (Yang 2023 IJPEM, Springer — baixar manual)**
> e os candidatos novos da R3 (`DEEP_RESEARCH_REPORT_R3.md`, todos paywalled/bot-blocked).
> **ValidationCases wired (2026-07-02):** as 77 curvas viraram casos em
> `src/.../core/validation_cases.py` (`DIGITIZED_CASES`) com
> `reference_csv_path`, DOI e condições — prontos no Case Studies → Calibrate.
>
> **RODADA 3 INGERIDA (2026-07-03):** 6 papers baixados manualmente →
> `pdfs_manual_download/` + `BAS_V2_papers/D. Rodada 3 (download institucional)/`.
> Digitalizados +31 curvas (liu2022 reaperto ×21, li2022marstruc creep ×6,
> li2022ti axial×freq ×4). wang2020 (FEM-only) e cja2022 (review) = referência, sem curvas.
>
> **#10 Yang 2023 IJPEM — RESOLVIDO POR SUBSTITUIÇÃO (2026-07-03):** o download veio
> como preview de 1 página (deletado). Substituto: as **9 curvas tabuladas** já em
> `extracted_csv/10_Yang_2023_*` (aproximadas, da nota
> `10_Yang_2023_phenomenological_model.md`, que tem condições + config MSD completas)
> foram wired como ValidationCases (`Yang2023 M8/M6 *`). Se um dia o PDF completo
> aparecer, re-digitalizar as Figs 1–9 em alta fidelidade é um upgrade opcional.
> **Total: 108 curvas digitalizadas + 9 substitutas = 128 ValidationCases.**

Lista única e acionável. Baixe cada PDF, salve na **pasta indicada**, depois
digitalize a figura → CSV de 2 colunas `cycle,F_over_F0` em `digitized_csv/`.

**Legenda de pastas (relativas a `curve_library/`):**
- `pdfs_open_access/` → artigos open-access (CC-BY etc.), baixar agora.
- `pdfs_manual_download/` → paywall, baixar via DOI institucional.
- `digitized_csv/` → os CSVs que você gerar a partir das figuras.

> "Manual (navegador)" = é open-access, mas o host bloqueia download automático;
> abra o link no navegador e clique em baixar. Continua indo em `pdfs_open_access/`.

---

## Prioridade 1 — baixar primeiro (montam a base M16 + 3 estágios + axial)

| # | Artigo | Baixar de | → Pasta | Salvar como | Digitalizar | → CSV |
|---|---|---|---|---|---|---|
| 1 | **Liu 2025, Sci. Rep.** — M16, F0=60 kN, 3 estágios | [PMC12218038 (PDF)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12218038/) · DOI [10.1038/s41598-025-02936-6](https://doi.org/10.1038/s41598-025-02936-6) | `pdfs_open_access/` | `liu2025_scirep_M16.pdf` | **Fig 3** (6 curvas, ampl. 0,25-0,8 mm) | `liu2025_M16_amp0p25.csv` … `amp0p8.csv` |
| 2 | **Bauer 2024, Eng. Fail. Anal.** — M8+M12, 3 estágios + s_crit | [TUprints (PDF)](https://tuprints.ulb.tu-darmstadt.de/bitstreams/202f6597-0bd6-4bd2-bc68-454fc12b8c3f/download) · DOI [10.1016/j.engfailanal.2024.108404](https://doi.org/10.1016/j.engfailanal.2024.108404) | `pdfs_open_access/` | `bauer2024_efa.pdf` | **Fig 8** (M12, 3 curvas) e Fig 6 (M8) | `bauer2024_M12_fig8.csv` |
| 3 | **Liu 2017, Tribology Int.** — excitação AXIAL | [HAL univ-evry](https://univ-evry.hal.science/hal-02398144) *(manual)* · DOI [10.1016/j.triboint.2017.05.037](https://doi.org/10.1016/j.triboint.2017.05.037) | `pdfs_open_access/` | `liu2017_triboint_axial.pdf` | F de aperto vs ciclos (5 ampl. × 5 F0) | `liu2017_axial_*.csv` |

## Prioridade 2 — sweeps de amplitude / membro / fatorial

| # | Artigo | Baixar de | → Pasta | Salvar como | Digitalizar | → CSV |
|---|---|---|---|---|---|---|
| 4 | **Lu/Yang 2024, Sensors** — M8, sweep amplitude + tabelas | [MDPI](https://www.mdpi.com/1424-8220/24/11/3306) · [PMC11174751](https://pmc.ncbi.nlm.nih.gov/articles/PMC11174751/) · DOI [10.3390/s24113306](https://doi.org/10.3390/s24113306) | `pdfs_open_access/` | `lu2024_sensors_M8.pdf` | **Fig 18** (5 ampl. 0,25-2,0 mm), Fig 20 (5 torques) | `lu2024_M8_fig18_amp*.csv` |
| 5 | **Rousseau-Bouzid 2025, Materials** — M12, rigidez de membro | [PMC11766740 (PDF)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11766740/pdf/materials-18-00462.pdf) · DOI [10.3390/ma18020462](https://doi.org/10.3390/ma18020462) | `pdfs_open_access/` | `rousseau2025_materials_M12.pdf` | Fig 4 (3 HDPE), Fig 5 (3 aço) | `rousseau2025_steel_t*.csv` |
| 6 | **Demir 2024, EJRND** — M8, fatorial 2×2×2 (vetorial) | [PDF orclever](https://www.orclever.com/api/pdf/ejrndv5i1693) · DOI [10.56038/ejrnd.v5i1.693](https://doi.org/10.56038/ejrnd.v5i1.693) | `pdfs_open_access/` | `demir2024_ejrnd_M8.pdf` | Figs 5a/5b/6a/6b (8 curvas) | `demir2024_*.csv` |

## Prioridade 3 / fase 2 — validação (tamanho, combinado, M10)

| # | Artigo | Baixar de | → Pasta | Salvar como | Digitalizar | → CSV |
|---|---|---|---|---|---|---|
| 7 | **Yang 2021, Shock & Vib.** — axial+transversal combinado, 3 estágios | [Hindawi PDF](https://downloads.hindawi.com/journals/sv/2021/1441122.pdf) *(manual)* · DOI [10.1155/2021/1441122](https://doi.org/10.1155/2021/1441122) | `pdfs_open_access/` | `yang2021_sv_combined.pdf` | Fig 2 (recessão 3 estágios) | `yang2021_*.csv` |
| 8 | **Karlsen-Lemu 2022, Eng. Fail. Anal.** — M30/M42, efeito tamanho | [UiS Brage PDF](https://uis.brage.unit.no/uis-xmlui/bitstream/11250/3059463/1/1-s2.0-S1350630722005647-main.pdf) *(manual)* · DOI [10.1016/j.engfailanal.2022.106590](https://doi.org/10.1016/j.engfailanal.2022.106590) | `pdfs_open_access/` | `karlsen2022_M30M42.pdf` | Fig 10 (M30), Fig 11 (M42) | `karlsen2022_*.csv` |
| 9 | **Yang 2019, Shock & Vib.** — M10, amplitude variável | [Hindawi PDF](https://downloads.hindawi.com/journals/sv/2019/2036509.pdf) *(manual)* · DOI [10.1155/2019/2036509](https://doi.org/10.1155/2019/2036509) | `pdfs_open_access/` | `yang2019_sv_M10.pdf` | pré-carga residual vs ciclos (5 ampl.) | `yang2019_*.csv` |

## Paywall — baixar via DOI institucional

| # | Artigo | Baixar de | → Pasta | Salvar como | Obs |
|---|---|---|---|---|---|
| 10 | **Yang/Jeong/Lim 2023, IJPEM** — M6/M8 fenomenológico, 3 estágios | DOI [10.1007/s12541-023-00783-x](https://doi.org/10.1007/s12541-023-00783-x) (Springer, ~US$40) | `pdfs_manual_download/` | `yang2023_ijpem.pdf` | condições já no companion OA [PMC11901137](https://pmc.ncbi.nlm.nih.gov/articles/PMC11901137/) |

---

## Casos de literatura antigos (originais do app) — paywall, fase opcional

Estão em [`../../../New_Theory/CASE_STUDY_CURVE_SOURCES.md`](../../../New_Theory/CASE_STUDY_CURVE_SOURCES.md).
Vão para `pdfs_manual_download/` (Jiang 2003 `10.1115/1.1586936`, Nassar 2006
`10.1115/1.2349569`, Junker 1969 `10.4271/690055`). Yang 2019 já está acima (#9).

---

## Depois de baixar e digitalizar

1. CSVs em `digitized_csv/` (2 colunas: `cycle,F_over_F0`).
2. Me avise — eu crio o `ValidationCase` apontando `reference_csv_path` para cada CSV
   (e `doi`/`reference`) em `src/.../core/validation_cases.py`.
3. No app: Case Studies → caso → **Calibrate**, com **Trim cycles** + tuner
   **`slip_onset_W`** (3 estágios) + leitura de **MAE/RMSE** ao vivo.

Detalhes/figuras/condições por fonte: [`DEEP_RESEARCH_REPORT.md`](DEEP_RESEARCH_REPORT.md).
Mapa fonte→constante V2: [`CALIBRATION_CURVE_DATABASE.md`](CALIBRATION_CURVE_DATABASE.md).
