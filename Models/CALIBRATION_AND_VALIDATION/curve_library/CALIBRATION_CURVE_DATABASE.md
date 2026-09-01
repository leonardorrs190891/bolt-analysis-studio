# Base de dados de curvas para calibração (V2 DynamicStiffnessAnalyzer)

Curvas F/F₀ vs ciclo (ou T/T₀, % residual axial) de auto-afrouxamento de juntas
aparafusadas, organizadas para **calibrar as constantes do modelo V2** e montar
mais case studies. Foco: curvas digitalizáveis com condições de ensaio conhecidas.

> **Nota honesta:** não consigo salvar PDFs binários automaticamente. Os artigos
> **open-access** abaixo têm link direto (1 clique → "Download PDF"); os
> **paywalled** precisam de download manual via DOI (sua instituição/Sci-Hub/autor).

> **Deep-research (2026-06-22):** ver [`DEEP_RESEARCH_REPORT.md`](DEEP_RESEARCH_REPORT.md)
> — 62 candidatos → 24 lidos a fundo → **10 confirmados** (9 open-access), cada um
> verificado adversarialmente. **Achado principal:** Liu et al. *Sci. Rep.* 2025
> (`10.1038/s41598-025-02936-6`, CC-BY, PMC) tem curvas **M16 8.8, F0=60 kN, 6
> amplitudes 0,25-0,8 mm, ≥5000 ciclos, 3 estágios** — o **ponto de calibração
> nativo M16** dos perfis nova/reusada. Outros novos: Bauer 2024 (TUprints, 3-estágios
> + s_crit=99µm), Yang 2021 (axial+transversal), Liu 2017 (track axial, HAL),
> Karlsen-Lemu 2022 (M30/M42, efeito de tamanho).

> **JÁ TEMOS 200 curvas prontas (sem download):** as notas de
> `CALIBRATION_AND_VALIDATION/*.md` já traziam tabelas F/F₀-vs-ciclo digitalizadas;
> foram extraídas para `extracted_csv/` (200 curvas limpas de 39 papers, +33 em
> `_needs_review/`). Índice em [`EXTRACTED_CSV_MANIFEST.md`](EXTRACTED_CSV_MANIFEST.md).
> Use direto na calibração (`reference_csv_path`). Os downloads abaixo só agregam
> resolução/condições para casos específicos.

## Estrutura de pastas

```
curve_library/
├── CALIBRATION_CURVE_DATABASE.md   ← este arquivo
├── pdfs_open_access/    ← coloque aqui os PDFs OA baixados
├── pdfs_manual_download/← coloque aqui os PDFs paywalled que você baixar
└── digitized_csv/       ← CSVs digitalizados (2 col: cycle,F_over_F0) p/ calibrar
```

## Fluxo: do artigo à calibração

1. Baixe o PDF (links abaixo) → `pdfs_open_access/` ou `pdfs_manual_download/`.
2. Digitalize a figura F/F₀ vs N (WebPlotDigitizer ou `New_Theory/digitize_shear.py`)
   → CSV 2 colunas `cycle,F_over_F0` em `digitized_csv/`.
3. Adicione um `ValidationCase` em `src/.../core/validation_cases.py` apontando
   `reference_csv_path` para o CSV (e `doi`/`reference`).
4. No app: Case Studies → caso → **Calibrate**. Use **Trim cycles** para recortar
   trechos ruins, marque **`slip_onset_W`** se a curva tiver platô inicial, e leia
   o **MAE/RMSE** ao vivo.

---

## Que curva calibra que constante (V2)

| Constante V2 | Feição na curva | Curvas-fonte ideais |
|---|---|---|
| `k_emb_scale` | queda rápida inicial (assentamento, Stage I) | qualquer curva, primeiros ~10 ciclos |
| `k_wear_scale_tr` | inclinação do colapso (Stage II), cresce c/ amplitude | sweep de amplitude (Lu Fig 18; Jiang) |
| `slip_onset_W` | **platô inicial** antes da queda (incubação 3-estágios) | Du 2025 (3 estágios); UFU nova; Junker M16 |
| `k_creep_scale` | cauda lenta / dependência de tempo | térmico/creep (Eraliev; Bouzid gasket) |
| `c_D,k_dmg_*` (dano) | colapso acelerado / parafuso reusado | UFU reaperto; ensaios de reaperto/reuso |
| `Phi_tr_correction`,`tr_loose_gain` | efeito de grip/rigidez do membro | Rousseau-Bouzid (grip, aço×HDPE); Zhang-Jiang (clamped length) |
| validação cross-condição | famílias variando 1 parâmetro | Lu (amplitude/preload/freq); Hattori (3 tamanhos) |

---

## A. Open-access — baixar agora (link direto)

| # | Artigo | DOI | Curvas (figura) | Condições | Calibra | Link |
|---|---|---|---|---|---|---|
| OA1 | **Lu et al. (2024)**, *Prediction of Pre-Loading Relaxation… under Tangential Cyclic Load*, Sensors 24(11):3306 | `10.3390/s24113306` | F/F₀ vs N: **Fig 9** (rugosidade Ra0.8/6.3), **Fig 10** (freq 0.1/1/5 Hz), **Fig 15** (grau 8.8/12.9 + área), **Fig 18** (amplitude 0.25–2.0 mm), **Fig 20** (torque 4–28 Nm) | M8, 8.8/12.9, transv. tangencial; δ 0.25–2.0 mm; 0.1–5 Hz; F₀≈2.1–15 kN; 50–1000 ciclos; 2 estágios (joelho ~5–10 ciclos) | `k_emb`,`k_wear`, dep. amplitude/preload/freq | https://www.mdpi.com/1424-8220/24/11/3306 |
| OA2 | **Du, Qiu, Li (2025)**, *Bolt Loosening under Sine-on-Random Coupling Vibration*, Machines 13(2):80 | `10.3390/machines13020080` | Clamp force vs ciclos/tempo; **3 estágios** (Steady/Transition/Loosen) | M8×1.25, 4 parafusos; sine+random PSD; vários torques | **`slip_onset_W`** (3 estágios) | https://www.mdpi.com/2075-1702/13/2/80 |
| OA3 | **Rousseau & Bouzid (2025)**, *Effect of Clamped Member Material and Thickness…*, Materials 18(2):462 | `10.3390/ma18020462` | Preload vs N para aço×HDPE e várias espessuras/grip | M12, transversal; membros aço e HDPE; grips variados | `Phi_tr`,`tr_loose_gain` (rigidez do membro) | https://doi.org/10.3390/ma18020462 · PDF livre: https://espace2.etsmtl.ca/id/eprint/30523/1/Bouzid-H-2025-30523.pdf |
| OA4 | **Amano (2024)**, *Optimization of anti-loosening bolt (double-thread)…*, Heliyon | (Heliyon, ver página) | Residual axial load vs ciclos (ISO 16130 Junker) | M8/M10; ISO 16130; rating ≥85% | validação ISO 16130; dispositivos de trava | https://www.cell.com/heliyon/fulltext/S2405-8440(24)04662-0 |
| OA5 | **Chen et al. (2017)**, *Self-Loosening… considering the Tightening Process*, Shock and Vibration | `10.1155/2017/2038421` | F/F₀ vs N (FEA+exp); 2 estágios | M12×1.75, transversal | `k_emb`,`k_wear`; efeito do aperto inicial | https://onlinelibrary.wiley.com/doi/10.1155/2017/2038421 |
| OA6 | **Du, Qiu et al. (2022)**, *Random Vibration 3-stage*, Eng. Fail. Anal. 133:105954 | `10.1016/j.engfailanal.2021.105954` | Torque vs tempo; **3 estágios** (PSD threshold) | M8×1.25, 4 parafusos; random puro | **`slip_onset_W`** | (Elsevier; verificar OA institucional) |
| OA7 | **MSc thesis (Jönköping, DiVA)**, *Development of a Simulation Model for Bolt Self-Loosening* | — | Curvas Junker simuladas+exp | Junker transversal | referência de modelagem | https://ju.diva-portal.org/smash/get/diva2:1897198/FULLTEXT01.pdf |
| OA8 | **Sandia — Bolt Preload Loss due to Modal Excitation of a C-Beam (SAND2019-12525C / IMAC 2021)** | `10.1007/978-3-030-47626-7_30` | Fig 4 (preload lbf vs tempo, 5 min); **Fig 5 (F/F₀ normalizado, 4 curvas, 15/30 min)** | SAE Gr.9 com strain-gauge; viga-C em excitação **modal** ~275 Hz (modo 1 = shear, modo 2 = flexão); F0~756 N; perda ~3-6% | k_emb_scale, cross-condition (regime modal/ressonante; tempo→ciclos) | [OSTI PDF](https://www.osti.gov/servlets/purl/1642845) |

> MDPI/Hindawi/Heliyon/DiVA/OSTI = open-access; na página do artigo use o botão **Download PDF**.

> **Rodada 2 de deep-research (2026-06-22):** 66 candidatos → 30 lidos → 3 confirmados,
> mas **2 eram duplicatas** (Liu 2017 e Bauer 2024 reapareceram com DOI errado/typo no
> candidato) e **27 foram rejeitados** pela verificação adversarial. **Única adição nova:
> OA8 Sandia C-Beam.** Conclusão: o sweep web saturou — a base compreensiva é a local
> (`extracted_csv/`, 200 curvas). Relatório: [`DEEP_RESEARCH_REPORT_R2.md`](DEEP_RESEARCH_REPORT_R2.md).
> Correção de DOI confirmada: Liu 2017 = `10.1016/j.triboint.2017.05.037` (M12 10.9, axial, 2 estágios).

## B. Paywalled — download manual (DOI) + nota na biblioteca

Curvas valiosas porém pagas (use DOI via instituição). Já resumidas na biblioteca
`Models/CALIBRATION_AND_VALIDATION/NN_*.md` (coluna = nota correspondente).

| Artigo | DOI | Calibra | Nota lib. |
|---|---|---|---|
| Jiang, Zhang, Lee (2003), ASME J. Mech. Des. 125(3):518 | `10.1115/1.1586936` | `k_wear`, Stage I/II (M12) | `02_Jiang_2003_2004` |
| Zhang & Jiang (2006), J. Press. Vessel Tech. — clamped length | `10.1115/1.2349572` | `Phi_tr` (grip), direção | `03_Zhang_Jiang_2006` |
| Nassar & Housari (2006), J. Press. Vessel Tech. 128(4):590 | `10.1115/1.2349569` | pitch/preload (M8/M10) | `07_Nassar_Housari_2006` |
| Pai & Hess (2002), J. Sound Vib. 253:585 | `10.1006/jsvi.2001.4006` | tipos de slip; `slip_onset` | `83_84_Pai_Hess` |
| Hattori et al. (2010), EPJ Web Conf. — critical slippage | `10.1051/epjconf/20100624005` | slip crítico (M6/M10/M16) | `11_Hattori_2010` |
| Junker (1969), SAE 690055 | `10.4271/690055` | curva Junker canônica | `18_Junker_test` |
| Liu et al. (2017), Tribology Int. 115:432 — axial | `10.1016/j.triboint.2017.06.007` | **track axial** F/F₀ vs N | `72_Liu_Cai` |
| Eraliev et al. (2021), Adv. Mech. Eng. — thermal cycling | `10.1177/16878140211015423` | `k_creep` (térmico) | `12_Eraliev_2021` |
| Bhattacharya et al. (2010), Mech. Mach. Theory 45(8):1215 | `10.1016/j.mechmachtheory.2010.04.001` | escala de tamanho (M4/M5/M6) | `89_Bhattacharya` |

## C. Já digitalizadas (UFU) — prontas

| Caso | Curva | Uso |
|---|---|---|
| UFU 5A / 13A-1ª / 13A-def | `Models/EXPERIMENTAL_UFU/reference_curves/UFU_*_preload_decay.csv` | nova/reusada/sobretorque/reaperto (M16, ±0.5 mm, 0.5 Hz) |
| M16 shear (New_Theory) | `New_Theory/M16_shear_*.csv` (9 curvas) | calibração-base do shear |

---

## Plano de prioridade (montar a base robusta)

1. **OA1 Lu 2024** — digitalizar **Fig 18** (amplitude) e **Fig 20** (preload): dá
   sweeps limpos para `k_wear_scale_tr` e a dependência amplitude/preload (validação
   cross-condição, o teste que falta no `MODEL_LEGITIMACY` §4.3).
2. **OA2 Du 2025** + **OA6 Du 2022** — curvas de **3 estágios** → calibrar e validar
   o novo **`slip_onset_W`** (platô do Stage I) fora da condição UFU.
3. **OA3 Rousseau-Bouzid 2025** — grip/rigidez do membro → `Phi_tr`,`tr_loose_gain`.
4. **B/Liu 2017 (axial)** — abrir o **track axial** (hoje só shear é calibrado).
5. **B/Hattori 2010** — M6/M10/M16 mesmo ensaio → efeito de tamanho.

Cada curva digitalizada vira um `ValidationCase` + alimenta a campanha de
generalização (`docs/.../2026-06-20-generalization-validation-campaign.md`).
