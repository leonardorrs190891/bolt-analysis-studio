I have enough context. The report follows.

# Rodada 2 — Referencias adicionais

Estas tres fontes sao **adicionais** as dez referencias confirmadas na Rodada 1, todas distintas e verificadas adversarialmente (DOIs corrigidos, PDFs baixados/parseados ou full-text extraido). Elas ampliam a cobertura justamente nos vetores que faltavam ao modelo V2: **trilha axial** (next-priority #3 do CLAUDE.md), **excitacao modal/flexao** e um **alvo de colapso de tres estagios em disp-mode** com varias condicoes para validacao cruzada.

---

## 1. Tabela ranqueada

| # | Paper (autores, ano, venue) | DOI | OA | Link direto | Figura(s) digitalizavel(is) | Condicoes (parafuso, amplitude/carga, freq, preload, ciclos/tempo) | 3 estagios? | Constante(s) V2 |
|---|---|---|:--:|---|---|---|:--:|---|
| 1 | **Liu, Ouyang, Feng, Cai, Liu, Zhu (2017)** — "Study on self-loosening of bolted joints excited by dynamic axial load", *Tribology International* 115:432-451 | `10.1016/j.triboint.2017.05.037` | sim (CC-BY, verde) | [HAL hal-02398144](https://univ-evry.hal.science/hal-02398144) — manuscrito [liu2017.pdf](https://univ-evry.hal.science/hal-02398144/file/liu2017.pdf) | **Fig. 5(b)** (sweep de preload 10/15/18 kN), **Fig. 8** (sweep de amplitude); Figs. 30/33/36/39 (revestimentos + overlay FE) | M12x1.75 grau 10.9; excitacao **axial** ~30 Hz; preloads 10/15/18 kN; amplitudes ~2/4/5 kN; milhares de ciclos; forca de aperto em kN | nao (dois estagios) | **axial-track** (primario), `k_emb_scale` (Estagio I), `k_wear_scale_tr` (Estagio II, analogo axial), `surface_damage`/`slip_onset_W` (sweep de amplitude), validacao cruzada forte |
| 2 | **TU Darmstadt (Engng Failure Analysis, 2024)** — "Method of accumulation of preload loss of bolted joints due to rotational self-loosening caused by cyclic, transversal excitation" | `10.1016/j.engfailanal.2024.108404` | sim (CC-BY-NC-ND) | [TUprints PDF](https://tuprints.ulb.tu-darmstadt.de/bitstreams/202f6597-0bd6-4bd2-bc68-454fc12b8c3f/download) | **Fig. 8** (M12x1.5, F_M=50 kN, joelho de tres estagios — melhor curva do paper), **Fig. 6** (6 cursos M8, decaimento quase linear) | Transversal disp-controlled (Junker/DIN 65151); M8 (F_M=20 kN) e M12x1.5 (35/50 kN); amplitude local s_a,E ~70-250 µm (critico ~76-108 µm); afroxa tipicamente <1000 ciclos, run-out 20.000; freq numerica nao no texto | **sim** | `surface_damage` (joelho de colapso, Fig. 8), `k_loose_scale_tr`/`Phi_tr_correction` (Fig. 6 linear), `slip_onset_W` (s_crit), validacao cruzada (20/35/50 kN, M8+M12) |
| 3 | **Sandia / IMAC XXXVIII (2021)** — "Bolt Preload Loss due to Modal Excitation of a C-Beam Structure", *Nonlinear Structures and Systems Vol.1* | `10.1007/978-3-030-47626-7_30` | sim (OSTI, manuscrito aceito SAND2019-12525C) | [OSTI purl/1642845](https://www.osti.gov/servlets/purl/1642845) ([biblio](https://www.osti.gov/biblio/1642845)) | **Fig. 4** (preload [lbf] vs tempo, teste 5 min mode-1), **Fig. 5** (F/F0 normalizado, 4 curvas, 15/30 min) — *Figs. 6-11 sao FEA pura, excluir* | Parafusos SAE grau 9 com extensometro (STRAINSERT, max 22.2 kN), C-beams 4340; excitacao modal ~275-288 Hz (mode-1 flexao = cisalhamento na junta); preload ~170-176 lbf (~780 N); perda ~3% (5 min) a ~5-6% (30 min) | nao | `slip_onset_W` (ancora "sem Estagio II"), `k_emb_scale`+`k_creep_scale` (exponencial-depois-linear), `k_wear_scale_tr`, auto-consistencia 5/15/30 min |

DOI corrigido (#1): o candidato original `10.1016/j.triboint.2017.03.013` esta **errado** (resolve para um paper de liga titanio-oxigenio); o correto, confirmado via Crossref e API do HAL, e `10.1016/j.triboint.2017.05.037`.

---

## 2. Agrupamento por proposito de calibracao (cobertura NOVA)

**Trilha axial (lacuna critica — next-priority #3 do CLAUDE.md):**
- **#1 Liu et al. 2017** ([DOI 10.1016/j.triboint.2017.05.037](https://doi.org/10.1016/j.triboint.2017.05.037)) e a unica fonte das tres rodadas que oferece **forca-de-aperto-vs-ciclos sob excitacao axial pura** (M12, ~30 Hz). Fig. 5(b) e Fig. 8 dao, respectivamente, sweeps independentes de preload e de amplitude — exatamente o que falta para ajustar um perfil axial do `DynamicStiffnessAnalyzer`. O proprio paper descreve um decaimento de **dois estagios** (queda rapida por deformacao plastica ciclica = embedding/plasticidade; cauda lenta por desgaste de fretting entre filetes = wear), mapeando limpo no par `k_emb_scale`(I)+`k_wear_scale_tr`(II).

**Colapso de tres estagios em disp-mode (alvo do `surface_damage` D):**
- **#2 TU Darmstadt 2024** ([TUprints PDF](https://tuprints.ulb.tu-darmstadt.de/bitstreams/202f6597-0bd6-4bd2-bc68-454fc12b8c3f/download)). A **Fig. 8** (M12x1.5, 50 kN, espectro) mostra o joelho lento->acelerado->ingreme — o mesmo formato de colapso reaperto/TP7 que motivou a variavel D. Regime transversal disp-controlled, identico ao Junker que ja calibra os perfis M16 de cisalhamento. **Melhor alvo da rodada** para o mecanismo de dano.

**Flexao / excitacao modal (geometria nova, baixa amplitude):**
- **#3 Sandia 2021** ([OSTI purl/1642845](https://www.osti.gov/servlets/purl/1642845)). Mode-1 (flexao em fase) = carregamento transversal na junta; perda pequena (~3-6%), so Estagios I-II exponencial+linear, **sem rotacao grossa nem colapso** (shaker limitado em forca). Util como ancora de **baixa amplitude / slip-onset** e como teste de auto-consistencia temporal (5/15/30 min).

**Repositorios com dados/PDF abertos (baixar agora):**
- #2 TUprints (CC-BY-NC-ND, PDF completo lido localmente) e #3 OSTI (manuscrito aceito Sandia) sao **OA imediato (baixar agora)**. #1 e CC-BY mas o PDF do HAL esta atras de challenge anti-bot Anubis — **acessivel a humano**, nao a bot; metadados/condicoes confirmados via API HAL, ResearchGate full-text e Crossref/Unpaywall.

**Coberturas que estas fontes NAO adicionam (honestidade):** nenhuma traz **creep/termico** dedicado (caudas de creep continuam sem fonte nova nesta rodada), **locking devices**, **compositos** ou **parafusos grandes** alem de M12. A cauda de creep permanece como lacuna.

---

## 3. As curvas NOVAS que mais agregam sobre a Rodada 1

A Rodada 1 cobriu o regime de cisalhamento M16 ±0.5mm Junker (os quatro perfis nova/reusada/sobretorque/reaperto). As tres curvas abaixo agregam exatamente onde a Rodada 1 era cega:

1. **#1 Liu 2017, Fig. 5(b) — sweep de preload axial (10/15/18 kN).** Maior valor da rodada: abre a **trilha axial** inteira, hoje sem nenhum dado calibrado. Permite ajustar um perfil axial e, com os tres preloads, validar um unico conjunto de parametros em condicoes independentes (preload maior => menos afroxamento). [DOI 10.1016/j.triboint.2017.05.037](https://doi.org/10.1016/j.triboint.2017.05.037) — *OA via HAL (humano), baixar manuscrito*.

2. **#1 Liu 2017, Fig. 8 — sweep de amplitude axial.** Dirige diretamente o driver de dissipacao por slip e o `surface_damage` no regime axial (OM/SEM confirmam desgaste adesivo+abrasivo+delaminacao piorando com a amplitude). Calibra `c_D`/`W_ref` e `slip_onset_W` fora do cisalhamento. *Mesmo PDF*.

3. **#2 TU Darmstadt 2024, Fig. 8 — joelho de tres estagios M12x1.5 (50 kN).** O melhor alvo disponivel para o mecanismo de colapso D em disp-mode, com joelho conhecido em F_V~35-40 kN (a amplitude critica cai abaixo da base do espectro conforme o preload decai). Complementa o reaperto/TP7 M16 com uma segunda evidencia independente de colapso. [TUprints PDF](https://tuprints.ulb.tu-darmstadt.de/bitstreams/202f6597-0bd6-4bd2-bc68-454fc12b8c3f/download) — *OA, baixar agora*.

4. **#2 TU Darmstadt 2024, Fig. 6 — 6 cursos M8 quase lineares (20 kN).** Alvo limpo de taxa de loosening rotacional em disp-mode num **tamanho de parafuso novo (M8)**, validando o escalonamento dos perfis para alem de M16/M12. *Mesmo PDF*.

5. **#3 Sandia 2021, Fig. 5 — F/F0 normalizado, 5/15/30 min.** Ancora de baixa amplitude e **teste de slip-onset (sem Estagio II)**: o modelo deve reproduzir perda <6% sem disparar rotacao grossa. Bom regularizador contra superajuste do mecanismo de loosening. [OSTI purl/1642845](https://www.osti.gov/servlets/purl/1642845) — *OA, baixar agora*.

---

## 4. Notas de acesso (OA vs paywall) e cautelas de digitalizacao

- **#1 Liu 2017** — `10.1016/j.triboint.2017.05.037`. Versao Elsevier paywall; **rota aberta CC-BY = HAL** ([hal-02398144](https://univ-evry.hal.science/hal-02398144)). PDF gated por Anubis para bots; **baixar manualmente no navegador**. Cautelas: teste **axial** 30 Hz, **nao** o regime transversal ±0.5mm dos perfis M16; parafuso **M12** (nao M16) => alimenta a trilha axial nova, nao os perfis de cisalhamento. Confianca **media** (pixels da figura nao puderam ser obtidos por bot; existencia, eixos kN-vs-ciclos, condicoes e formato de dois estagios confirmados via ResearchGate full-text + abstract).
- **#2 TU Darmstadt 2024** — `10.1016/j.engfailanal.2024.108404`. **OA total** (CC-BY-NC-ND, PDF 12 pp lido localmente); tambem SSRN abstract_id=4716219. Cautelas: dados de manchete sao **boundary curves S-N** (amplitude vs ciclos-ate-25%-perda), que **nao** devem ser digitalizadas como F/F0(N); use **apenas Fig. 6 e Fig. 8**. Frequencia numerica nao no texto (so s(t)=s_a·sin(2πf)); metodo puramente fenomenologico (sem decomposicao de mecanismos). F_V em kN normaliza trivialmente por F_M (20/35/50 kN). Confianca **alta**.
- **#3 Sandia 2021** — `10.1007/978-3-030-47626-7_30`. Springer paywall; **OSTI manuscrito aceito = OA** ([purl/1642845](https://www.osti.gov/servlets/purl/1642845)). Cautelas: F/F0 vs **tempo** (nao ciclos, mas freq ~275 Hz conhecida => conversivel); perda muito pequena (~3-6%), preload baixissimo (~780 N), **sem Estagio II/III**; diametro nominal do parafuso **nao informado** (dificulta o modelo MSD); **Figs. 6-11 sao FEA pura — excluir**. Use so Fig. 4 e Fig. 5 como ponto de validacao Estagio-I/slip-onset. Confianca **alta** quanto a acesso/digitalizacao, **fraca** como alvo primario de calibracao nao-linear.

Todas as afirmacoes acima derivam exclusivamente das tres fontes do JSON fornecido; nenhuma fonte foi inventada.