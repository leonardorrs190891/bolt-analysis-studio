# BAS_V2_papers — biblioteca de papers do V2

Atualizado 2026-07-02. **62 PDFs** organizados em 3 pastas + material derivado no repo.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `A. Fontes de alta-resolucao (deep-research)/` | **9 papers prioritários** do deep-research (rodadas 1–2) — todos baixados e **todos digitalizados** (curvas + aparato) |
| `B. Biblioteca local catalogada (titulo + link + curvas extraidas)/` | 51 papers da biblioteca de validação (96-paper library); curvas de tabelas já em `extracted_csv/` (200 curvas) |
| `C. Casos no app/` | 2 papers dos case studies embutidos no app |
| `D. Rodada 3 (download institucional)/` | **5 papers** via acesso institucional (2026-07-03): reaperto (Structures 2022), creep de contato (Marine Structures 2022), axial×frequência (Tribology Int 2022), + 2 referências (AIME 2020 FEM, CJA review). Yang 2023 IJPEM veio como preview de 1 pág → deletado e **substituído** pelas curvas tabuladas de `extracted_csv/10_Yang_2023_*` |

## O que foi extraído de cada paper prioritário (2026-07-02)

Curvas digitalizadas (**77 CSVs**, formato `cycle,F_over_F0`):
`Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/` — manifest em `DIGITIZED_CSV_MANIFEST.md`.
Aparato, corpo-de-prova, matriz de ensaios, ressalvas de digitalização e mapeamento
para os tuners V2: `Models/CALIBRATION_AND_VALIDATION/curve_library/apparatus_notes/<paper>.md`.

| Paper (pasta A, salvo indicação) | DOI | Regime | Curvas |
|---|---|---|--:|
| Liu 2025 Sci Rep (M16! 8.8, F0=60 kN, 0.25–0.8 mm) | 10.1038/s41598-025-02936-6 | transversal disp, 3 estágios | 7 |
| Bauer 2024 EFA (M8 20 kN + M12×1.5 50 kN, s_crit=99 µm) | 10.1016/j.engfailanal.2024.108404 | transversal disp, colapso 3 estágios | 9 |
| Liu 2017 Tribology Int (M12×1.75, 30 Hz, 10⁶ ciclos) | 10.1016/j.triboint.2017.05.037 | **AXIAL força** (abre o trilho axial) | 9 |
| Lu 2024 Sensors (M8 8.8, 0.25–2.0 mm, 4–28 N·m) | 10.3390/s24113306 | transversal disp | 10 |
| Rousseau 2025 Materials (M12, aço vs HDPE, t=10/12/14) | 10.3390/ma18020462 | transversal disp, rigidez de membro | 6 |
| Demir 2024 EJRND (M8, fatorial 2×2×2) | 10.56038/ejrnd.v5i1.693 | transversal disp (DIN 65151) | 8 |
| Yang 2021 S&V (M8, transversal+axial 90°, ξ crítico) | 10.1155/2021/1441122 | **composto** (acopla F_amp↔delta_amp) | 6 |
| Yang 2019 S&V (M10, ~26 kN, amplitude variável) | 10.1155/2019/2036509 | transversal disp + blocos variáveis | 5 |
| Karlsen 2022 EFA (M30/M42, 353/706 kN, HV vs Vibralock) | 10.1016/j.engfailanal.2022.106590 | transversal, efeito de tamanho extremo | 11 |
| Sandia 2021 C-Beam (pasta B; ~780 N, modo 1 ~280 Hz) | 10.1007/978-3-030-47626-7_30 | modal/flexão, baixa amplitude | 6 |
| Z. Liu 2022 Structures (pasta D; M12, T=80 N·m, reapertos sucessivos) | 10.1016/j.istruc.2022.08.049 | **reaperto/retightening** (prioridade #5) | 21 |
| Y. Li 2022 Marine Structures (pasta D; M16 304SS, 5/10/15 kN, Ra sweep) | 10.1016/j.marstruc.2022.103263 | **creep estático** (eixo x em minutos!) + parâmetros Burgers p/ MSD | 6 |
| H. Li 2022 Tribology Int (pasta D; M10, A_F=10 kN, 10/15/20 Hz) | 10.1016/j.triboint.2022.107933 | axial × frequência | 4 |

## Falta baixar

Nada obrigatório. **Yang 2023 IJPEM** (10.1007/s12541-023-00783-x): o download veio como
preview de 1 página (deletado) — **substituído** pelas 9 curvas tabuladas já em
`extracted_csv/10_Yang_2023_*` (wired como `Yang2023 M8/M6 *`; condições + config MSD na
nota `10_Yang_2023_phenomenological_model.md`). Upgrade opcional: se o PDF completo
aparecer, re-digitalizar Figs 1–9 em alta fidelidade.

Todos os itens da R3 foram ingeridos em 2026-07-03 (pasta D; 31 curvas novas).
Lista completa com justificativas: `Models/CALIBRATION_AND_VALIDATION/curve_library/DEEP_RESEARCH_REPORT_R3.md`.

## Como usar na calibração

**Já wired (2026-07-02):** as 77 curvas são `ValidationCase`s registrados em
`src/bolt_analysis_studio/core/validation_cases.py` (`DIGITIZED_CASES`), cada um com
`reference_csv_path`, DOI, condições (F0, amplitude, frequência) e pontos experimentais
lidos do próprio CSV. Aparecem no app em Case Studies (nomes `Liu2025 ...`, `Bauer2024 ...`,
`Liu2017 axial ...`, etc.) — carregue o caso e use **Calibrate** com trim + `slip_onset_W`.
Atenção: os casos `Liu2017 axial *` e `Sandia2021 *` são de excitação axial/modal
(amplitude transversal = 0 no caso) — usar modo força do V2, não `delta_amp`.
