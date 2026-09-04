# Fontes das curvas dos Case Studies

Lista das publicações de origem de cada case study de validação, para baixar os
artigos e **re-digitalizar as curvas** F/F₀ vs ciclo (workflow `digitize_shear.py`).

**Status:** os 8 casos de literatura **ainda não têm curva digitalizada** (`nocsv`),
hoje rodam só com o modelo sintetizado pela geometria, sem curva experimental de
referência. Os 3 casos âncora interna já têm curva (`Models/EXPERIMENTAL_ANCORA/reference_curves/`).

> Não foi possível baixar os PDFs automaticamente (a maioria é paywalled). Os DOIs/URLs
> abaixo permitem o download manual. Apenas **Yang 2019** é open-access.

## Casos de literatura — precisam de curva (re-digitalizar)

| Case study | Referência | DOI | Acesso | Link |
|---|---|---|---|---|
| Jiang Low Load (M12) | Jiang, Y., Zhang, M., Lee, C. (2003). *Study of the Self-Loosening of Bolted Joints*. ASME J. Mech. Des. 125(3): 518–526 | `10.1115/1.1586936` | Paywall (ASME) | https://asmedigitalcollection.asme.org/mechanicaldesign/article/125/3/518/476008 |
| Jiang High Load (M12) | *idem* (mesma figura, carga maior) | `10.1115/1.1586936` | Paywall (ASME) | https://asmedigitalcollection.asme.org/mechanicaldesign/article/125/3/518/476008 |
| Junker Standard (M16) | DIN 65151 — Aerospace series, vibration test for fasteners | — | Paywall (Beuth) | https://www.beuth.de/en/standard/din-65151/1454029 |
| Nassar Low Friction (M12) | Nassar, S.A., Housari, B.A. (2006). *Effect of Thread Pitch on the Self-Loosening of Threaded Fasteners*. ASME J. Press. Vessel Tech. 128(4): 590–598 | `10.1115/1.2349569` | Paywall (ASME) | https://asmedigitalcollection.asme.org/pressurevesseltech/article/128/4/590/444683 |
| Nassar High Friction (M12) | *idem* (mesmo paper, μ maior) | `10.1115/1.2349569` | Paywall (ASME) | https://asmedigitalcollection.asme.org/pressurevesseltech/article/128/4/590/444683 |
| Yang High Amplitude (M16) | Yang, X. et al. (2019). *Loosening of Bolted Joints under Transverse Vibration*. Shock and Vibration, art. 2036509 | `10.1155/2019/2036509` | **Open access** (Hindawi/Wiley) | https://onlinelibrary.wiley.com/doi/10.1155/2019/2036509 |
| Yang Low Amplitude (M16) | *idem* (mesmo paper, amplitude menor) | `10.1155/2019/2036509` | **Open access** | https://onlinelibrary.wiley.com/doi/10.1155/2019/2036509 |
| Severe Transverse (M16) | Junker, G.H. (1969). *New Criteria for Self-Loosening of Fasteners Under Vibration*. SAE Paper 690055 | `10.4271/690055` | Paywall (SAE) | https://www.sae.org/publications/technical-papers/content/690055/ |

## Casos âncora interna — curva já digitalizada

| Case study | Origem | Curva |
|---|---|---|
| âncora interna 5A (3/4" UNC, Junker) | âncora interna Lab. de Tribologia de Parafusos, trial 5A (2025-03-05) | `Models/EXPERIMENTAL_ANCORA/reference_curves/ancora_interna.csv` |
| âncora interna 13A 1ª (3/4" UNC, interrompido) | âncora interna Lab., trial 13A-1ª (2025-03-19) | `Models/EXPERIMENTAL_ANCORA/reference_curves/ancora_interna*.csv` |
| âncora interna 13A definitivo (3/4" UNC, Junker) | âncora interna Lab., trial 13A-def (2025-04-14) | `Models/EXPERIMENTAL_ANCORA/reference_curves/ancora_interna*.csv` |

## Como re-digitalizar (depois de baixar o PDF)

1. Recorte a figura F/F₀ vs ciclo (ou T/T₀, % preload) do artigo.
2. Use o workflow de `New_Theory/digitize_shear.py` (adaptando a imagem de entrada)
   ou um digitalizador (WebPlotDigitizer) → CSV de 2 colunas `cycle, F_over_F0`.
3. Salve em `Models/CALIBRATION_AND_VALIDATION/` (ou `New_Theory/`), aponte o
   `reference_csv_path` do case em `src/.../core/validation_cases.py`.
4. No app: Case Studies → caso → carrega curva + modelo; calibre com medida de erro
   (MAE/RMSE) e, se a curva tiver platô inicial, marque o tuner `slip_onset_W`.
