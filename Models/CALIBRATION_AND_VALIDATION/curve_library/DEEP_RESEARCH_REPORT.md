# Banco de Curvas de Calibração para o Modelo Energético de Auto Afrouxamento (V2)

## 1. O que torna uma curva confiável para calibração

Para o motor energético do V2 (`DynamicStiffnessAnalyzer`, modo disp `step_cycle(delta_amp=...)`), uma curva experimental só é útil para calibração quando satisfaz, na prática, cinco critérios:

1. **Eixo Y de pré carga rastreável**: força de aperto F (kN ou N) ou razão F/F0 versus número de ciclos N. Quando o eixo é absoluto, a F0 inicial precisa ser conhecida para normalizar para F/F0 (operação trivial, compatível com o formato CSV de 2 colunas `cycle, F_over_F0` do `New_Theory/`).
2. **Condições de ensaio especificadas e quantitativas**: tamanho do parafuso, amplitude de deslocamento transversal (ou carga axial), frequência, pré carga inicial F0 e contagem de ciclos. Lacunas (tipicamente frequência) viram confundidores.
3. **Modo de carregamento compatível**: deslocamento controlado tipo Junker mapeia diretamente no caminho `delta_amp` do V2; força controlada (servo hidráulico axial) usa o modo força.
4. **Figura digitalizável de verdade**: gráfico quantitativo com eixos legíveis, idealmente vetorial. Não serve curva D-N / S-N (vida em log log), apenas a recessão de pré carga por ciclo.
5. **Fonte acessível**: open access (CC-BY) baixável agora, ou paywall acessível via DOI institucional.

Para o V2 especificamente, a distinção crítica é entre curvas de **duas retas** (queda rápida inicial mais declínio gradual, paradigma que o V2 já reproduz) e curvas de **três estágios** (incubação lenta → afrouxamento intermediário → colapso re acelerado), sendo estas últimas as que alimentam `slip_onset_W` e `surface_damage`, os recursos mais novos e menos restringidos do modelo.

---

## 2. Tabela ranqueada das melhores fontes

Ranking por valor de calibração combinado (cobertura de constantes V2 + qualidade da figura + acessibilidade + presença de três estágios).

| # | Paper (autores, ano, venue) | DOI | OA | Link direto | Figura(s) com a curva | Parafuso | Amplitude | Freq | F0 | Ciclos | 3 estágios? | Constantes V2 calibradas |
|---|---|---|:--:|---|---|---|---|---|---|---|:--:|---|
| 1 | **Yang, Jeong, Lim — A Phenomenological Model for Bolt Loosening… (IJPEM 2023, vol.24, 825-835)** | [10.1007/s12541-023-00783-x](https://doi.org/10.1007/s12541-023-00783-x) | **não** (paywall Springer USD 39,95) | DOI manual; condições no companion OA [PMC11901137](https://pmc.ncbi.nlm.nih.gov/articles/PMC11901137/) | Figs. 1-9 (F/F0 vs N, várias amplitudes M6 e M8) + master curve + lei de potência S-N | M6×1,0 e M8×1,25 | 0,18-0,65 mm (vários graus) | 5 Hz | ~11 kN (M6), ~14,3 kN (M8) | ~1e4-1e5 | **sim** | k_emb_scale, k_wear_scale_tr, slip_onset_W, Phi_tr_correction, k_loose_scale_tr, surface_damage, cross-condition |
| 2 | **Liu et al. — Bolt loosening evaluation… normalized screw root equivalent stress (Sci. Rep. 2025)** | [10.1038/s41598-025-02936-6](https://doi.org/10.1038/s41598-025-02936-6) | **sim** (CC BY-NC-ND) | [PMC PDF 3,4 MB](https://pmc.ncbi.nlm.nih.gov/articles/PMC12218038/) | Fig 2 (curva única fast-slow-fast); **Fig 3 (6 curvas, amplitudes 0,25-0,8 mm)** | **M16×120, 8.8** | 0,25/0,3/0,4/0,5/0,6/0,8 mm | não reportada (só 200 Hz amostragem) | **60 kN** | ≥5000 | **sim** | k_emb_scale, k_wear_scale_tr, slip_onset_W, Phi_tr_correction, surface_damage, cross-condition |
| 3 | **Yang, Yang, Xiao, Jiang, Ma — Competitive Failure of Loosening and Fatigue… Composite Excitation (Shock & Vib. 2021)** | [10.1155/2021/1441122](https://doi.org/10.1155/2021/1441122) | **sim** (CC BY 4.0, GOLD) | [downloads.hindawi.com PDF](https://downloads.hindawi.com/journals/sv/2021/1441122.pdf) | Fig 2 (recessão 3 estágios) + curvas F vs N por grau de pré carga | M8×1,25×70, 8.8 | desloc. transversal + axial (90° fase, ξ_T=-1) | 10 Hz | 7,03/9,37/11,71/14,05 kN | até falha (varia) | **sim** | axial-track, k_emb_scale, k_wear_scale_tr, slip_onset_W, surface_damage, Phi_tr_correction, cross-condition |
| 4 | **Bauer et al. — Method of accumulation of preload loss due to rotational self-loosening (Eng. Failure Anal. 162, 2024, 108404)** | [10.1016/j.engfailanal.2024.108404](https://doi.org/10.1016/j.engfailanal.2024.108404) | **sim** (CC BY-NC-ND) | [TUprints PDF](https://tuprints.ulb.tu-darmstadt.de/bitstreams/202f6597-0bd6-4bd2-bc68-454fc12b8c3f/download) | **Fig 6 (6 curvas M8, 70 µm)**; **Fig 8 (3 curvas M12×1,5, espectro variável, 3 estágios explícito)** | M8 (l_K=8 mm) e M12×1,5 (l_K=12 mm) | M8: 70 µm; M12: 80 µm + picos 150 µm | simbólica (sem valor) | M8: 20 kN; M12: 50 kN | <1000 (bloco de 20 repetido) | **sim** (Fig 8) | slip_onset_W, k_loose_scale_tr, surface_damage, Phi_tr_correction, cross-condition |
| 5 | **Liu et al. — Study on self-loosening of bolted joints excited by dynamic axial load (Tribology Int. 2017)** | [10.1016/j.triboint.2017.05.037](https://doi.org/10.1016/j.triboint.2017.05.037) | **sim** (GREEN/CC-BY) | [HAL univ-evry liu2017.pdf](https://univ-evry.hal.science/hal-02398144) | F de aperto vs ciclos (5 pré cargas × 5 amplitudes; revestimentos PTFE/MoS2/TiN) | aço alta resist. (tamanho a confirmar no PDF) | 5 níveis de amplitude axial | variada (variável de estudo) | 5 níveis | até back-off | **sim** | **axial-track**, slip_onset_W, k_creep_scale, surface_damage, cross-condition |
| 6 | **Yang et al. — Prediction of Pre-Loading Relaxation… Tangential Cyclic Load (Sensors 2024)** | [10.3390/s24113306](https://doi.org/10.3390/s24113306) | **sim** | [MDPI PDF](https://www.mdpi.com/1424-8220/24/11/3306) / [PMC11174751](https://pmc.ncbi.nlm.nih.gov/articles/PMC11174751/) | **Fig 18 (5 curvas, amplitudes 0,25-2,0 mm)**; Fig 20 (5 torques/pré cargas); Fig 15 (4 tipos de parafuso); Tabelas 7-9 | M8, 8.8 e 12.9 | 0,25/0,5/1,0/1,5/2,0 mm | 0,1 / 1,0 / 5,0 Hz | ~11.567 N (22 Nm) | ~50-500 | não (2 estágios) | k_wear_scale_tr, slip_onset_W, Phi_tr_correction, k_emb_scale, cross-condition |
| 7 | **Karlsen & Lemu — Comparative study on loosening of anti-loosening vs standard bolt (Eng. Failure Anal. 2022)** | [10.1016/j.engfailanal.2022.106590](https://doi.org/10.1016/j.engfailanal.2022.106590) | **sim** (CC-BY) | [UiS Brage PDF](https://uis.brage.unit.no/uis-xmlui/bitstream/11250/3059463/1/1-s2.0-S1350630722005647-main.pdf) / [CORE reader](https://core.ac.uk/reader/560366445) | Fig 10 (M30, HV vs Vibralock); Fig 11 (M42) | **M30 e M42, 10.9** | ±1,0 mm (M30), ±1,5 mm (M42) | 1 Hz | 353 kN (70% esc., M30), 706 kN (M42) | HV: 200-400; Vibralock: ~3000 | desconhecido | k_loose_scale_tr, Phi_tr_correction, surface_damage, slip_onset_W, cross-condition |
| 8 | **Demir/Norm Fasteners — Analytical Prediction and Experimental Validation… (EJRND 2024, v5i1)** | [10.56038/ejrnd.v5i1.693](https://doi.org/10.56038/ejrnd.v5i1.693) | **sim** | [PDF orclever](https://www.orclever.com/api/pdf/ejrndv5i1693) | Figs 5a/5b/6a/6b (8 curvas exp. F vs N, fatorial 2×2×2); Fig 3 (F vs ângulo) | M8×1,25, DIN 933/934 | 0,3 e 0,4 mm | não reportada (~12,5 Hz DIN 65151) | 14,3 / 17,6 (/20,9) kN | ~175-200 | não (2 estágios) | k_wear_scale_tr, slip_onset_W, Phi_tr_correction, k_emb_scale, cross-condition |
| 9 | **Yang et al. — Bolt Loosening Life under Variable Amplitude Vibration (Shock & Vib. 2019)** | [10.1155/2019/2036509](https://doi.org/10.1155/2019/2036509) | **sim** (CC-BY) | [Hindawi PDF](https://downloads.hindawi.com/journals/sv/2019/2036509.pdf) | Pré carga residual vs ciclos (5 graus de amplitude) + curva D-N | M10 alta resist. | 5 graus (mm a ler) | ~5-10 Hz | ~26 kN | até limiares % | desconhecido | k_wear_scale_tr, slip_onset_W, Phi_tr_correction, axial-track, cross-condition |
| 10 | **Effect of Clamped Member Material and Thickness… Transverse Loads (Materials 2025)** | [10.3390/ma18020462](https://doi.org/10.3390/ma18020462) | **sim** (CC-BY) | [PMC PDF](https://pmc.ncbi.nlm.nih.gov/articles/PMC11766740/pdf/materials-18-00462.pdf) | Fig 4 (3 curvas HDPE); Fig 5 (3 curvas aço); Fig 6 (HDPE vs aço) | M12×1,75, 8.8 | 0,04-0,5 mm (por Tabela 2) | ~1 Hz (qualitativo) | 4 / 10 / 3,5 kN | ~50-200 | não (2 estágios) | k_emb_scale, slip_onset_W, Phi_tr_correction, cross-condition |

---

## 3. Agrupamento por propósito de calibração

### Estágio I — embedding (`k_emb_scale`)
A queda rápida inicial nos primeiros ~5-10 ciclos. Melhor sinal em membros macios (embedding plástico isolado da rotação):
- **#10 Materials 2025** ([10.3390/ma18020462](https://doi.org/10.3390/ma18020462), OA): Fig 4 HDPE, estágio não rotacional inicial puro = embedding plástico desacoplado.
- **#2 Sci. Rep. 2025** ([10.1038/s41598-025-02936-6](https://doi.org/10.1038/s41598-025-02936-6), OA): queda inicial das curvas Fig 3.
- **#8 EJRND 2024** ([10.56038/ejrnd.v5i1.693](https://doi.org/10.56038/ejrnd.v5i1.693), OA): "rapid initial drop" explícito.

### Estágio II — desgaste transversal (`k_wear_scale_tr`)
Mecanismo dominante no modo disp (dirigido por K_archard). Varreduras de amplitude isolam a taxa de decaimento:
- **#2 Fig 3** (M16, 6 amplitudes, OA) — melhor por ser M16 (ponto de calibração nativo).
- **#6 Sensors 2024 Fig 18** ([10.3390/s24113306](https://doi.org/10.3390/s24113306), OA) — varredura 0,25-2,0 mm com Tabelas 7-9 ancorando a digitalização.
- **#1 IJPEM 2023** (paywall) — master curve fenomenológica multi amplitude.

### `slip_onset_W` — incubação / limiar de slip (3 estágios)
O joelho onde o afrouxamento estagna abaixo de um deslocamento crítico ou re acelera:
- **#6 Sensors 2024**: caso 0,25 mm perde só ~22% e satura (limiar de slip onset explícito) vs 2,0 mm que colapsa.
- **#4 Eng. Fail. Anal. 2024** ([10.1016/j.engfailanal.2024.108404](https://doi.org/10.1016/j.engfailanal.2024.108404), OA): s_crit=99 µm @P_L=50% quantificado — restrição direta de limiar.
- **#2 Sci. Rep. 2025**: ponto de fronteira N_D na curva fast-slow-fast.

### Cauda de creep (`k_creep_scale`)
Relaxação lenta de longa duração, melhor no trilho axial de baixa frequência:
- **#5 Tribology Int. 2017** ([10.1016/j.triboint.2017.05.037](https://doi.org/10.1016/j.triboint.2017.05.037), OA): "preload reduced first slowly due to relaxation mechanisms" = estágio lento de creep/embedding antes do back-off.

### Colapso por surface_damage (`D`)
Re aceleração final / colapso catastrófico (análogo reaperto/TP7):
- **#4 Fig 8**: terceiro estágio explícito "decrease faster... asymptotically approaches a steeper linear course" abaixo de F_V crítico.
- **#3 Shock & Vib. 2021** ([10.1155/2021/1441122](https://doi.org/10.1155/2021/1441122), OA): Estágio III "fatigue fracture" (NT-NE).
- **#7 Eng. Fail. Anal. 2022** ([10.1016/j.engfailanal.2022.106590](https://doi.org/10.1016/j.engfailanal.2022.106590), OA): autores atribuem perda a "immediate reduction of asperities... not creep" — suporte físico direto para D modular atrito sem rotação.

### Rigidez de membro / `Phi_tr_correction`
Sensibilidade anisotrópica do afrouxamento à rigidez do membro/comprimento de aperto:
- **#10 Materials 2025**: matriz material×espessura (juntas mais rígidas afrouxam mais rápido) = combustível para o softening Greenwood-Williamson de [K(s)].
- **#8 EJRND 2024**: fatorial com comprimento de aperto 13,8 vs 19,8 mm.
- **#4 Eng. Fail. Anal. 2024**: dependência não linear explícita de (amplitude − deslocamento crítico).

### Trilho axial (prioridade #3 do CLAUDE.md — atualmente sem dados)
- **#5 Tribology Int. 2017**: o trilho axial puro (5 pré cargas × 5 amplitudes, revestimentos variando µ). **A fonte mais valiosa para preencher a lacuna axial.**
- **#3 Shock & Vib. 2021**: excitação composta tração+cisalhamento (90° fase) — abre o acoplamento F_amp↔delta_amp (prioridade #4).

### Efeito de tamanho / validação cruzada
- M6/M8: #1, #3, #4, #6, #8. M10: #9. M12: #4, #10. **M16: #2** (único no ponto nativo). M30/M42: #7. Faixa de pré carga de 3,5 kN a 706 kN.

---

## 4. Plano priorizado de digitalização (5-8 curvas primeiro)

A ordem maximiza valor por esforço: open access baixável agora + cobertura de constantes não restringidas + presença de três estágios + proximidade do ponto M16.

**1ª prioridade — #2 Sci. Rep. 2025, Fig 3 (6 curvas M16, 0,25-0,8 mm)** — [PMC12218038](https://pmc.ncbi.nlm.nih.gov/articles/PMC12218038/) **(baixar agora)**.
Por quê: único conjunto **M16 três estágios** em open access, exatamente o tamanho da calibração nativa nova/reusada. Família de 6 amplitudes com F0=60 kN fixa restringe simultaneamente k_wear_scale_tr, slip_onset_W, Phi_tr_correction e surface_damage. Normalizar dividindo por 60 kN.

**2ª prioridade — #2 Sci. Rep. 2025, Fig 2 (curva única fast-slow-fast)** — mesma fonte.
Por quê: assinatura de três estágios limpa para validar a segmentação em estágios e o ponto N_D (slip_onset_W). Custo marginal zero (mesmo PDF).

**3ª prioridade — #4 Eng. Fail. Anal. 2024, Fig 8 (3 curvas M12×1,5, espectro variável)** — [TUprints](https://tuprints.ulb.tu-darmstadt.de/bitstreams/202f6597-0bd6-4bd2-bc68-454fc12b8c3f/download) **(baixar agora)**.
Por quê: único terceiro estágio **explicitamente descrito** com limiar crítico quantificado (s_crit=99 µm). Alimenta surface_damage e slip_onset_W com número físico, não só forma de curva.

**4ª prioridade — #4 Eng. Fail. Anal. 2024, Fig 6 (6 curvas M8, 70 µm, F0=20 kN)** — mesma fonte.
Por quê: regime de amplitude constante quase linear, contraponto controlado à Fig 8; segundo diâmetro (M8) para validação cruzada. Custo marginal zero.

**5ª prioridade — #5 Tribology Int. 2017, curvas F de aperto vs ciclos (trilho axial)** — [HAL liu2017.pdf](https://univ-evry.hal.science/hal-02398144) **(baixar manualmente no navegador; hosts bloqueiam fetch automatizado)**.
Por quê: **abre o trilho axial inexistente** (prioridade #3 do CLAUDE.md). slow→fast = creep + slip_onset_W + surface_damage no modo força. Ler tamanho/F0/Hz da tabela de setup ao baixar.

**6ª prioridade — #6 Sensors 2024, Fig 18 (5 curvas, 0,25-2,0 mm)** — [MDPI PDF](https://www.mdpi.com/1424-8220/24/11/3306) **(baixar agora)**.
Por quê: varredura de amplitude mais ampla do banco (0,25 a 2,0 mm) com **Tabelas 7-9 numéricas** para checar a digitalização. Caso 0,25 mm satura (~22%) = âncora direta de slip_onset_W. Normalizar por ~11.567 N.

**7ª prioridade — #10 Materials 2025, Fig 4 (3 curvas HDPE) + Fig 5 (3 curvas aço)** — [PMC11766740](https://pmc.ncbi.nlm.nih.gov/articles/PMC11766740/pdf/materials-18-00462.pdf) **(baixar agora)**.
Por quê: isola embedding plástico (HDPE) de afrouxamento rotacional (aço) na mesma figura — separação limpa de k_emb_scale vs k_loose, e matriz material×espessura para Phi_tr_correction. Normalizar por 4/10/3,5 kN conforme o teste.

**8ª prioridade — #8 EJRND 2024, Figs 5/6 (8 curvas, fatorial 2×2×2)** — [PDF orclever](https://www.orclever.com/api/pdf/ejrndv5i1693) **(baixar agora; figuras vetoriais, qualidade de digitalização excelente)**.
Por quê: fatorial limpo amplitude×pré carga×comprimento de aperto, vetorial, com curvas individualmente separáveis por setas. Validação cruzada M8 controlada de slip_onset_W e Phi_tr_correction.

**Reservar para fase 2 (validação, não fitting primário):**
- **#3 Shock & Vib. 2021** ([downloads.hindawi.com PDF](https://downloads.hindawi.com/journals/sv/2021/1441122.pdf), OA) — excitação composta, valioso para o acoplamento F_amp↔delta_amp (prioridade #4), mas hosts bloqueados (baixar manualmente; rótulos por curva a ler).
- **#7 Eng. Fail. Anal. 2022** ([UiS Brage PDF](https://uis.brage.unit.no/uis-xmlui/bitstream/11250/3059463/1/1-s2.0-S1350630722005647-main.pdf), OA) — efeito de tamanho extremo (M30/M42, 706 kN); ramo HV é colapso catastrófico, não três estágios resolvidos.
- **#9 Shock & Vib. 2019** ([Hindawi PDF](https://downloads.hindawi.com/journals/sv/2019/2036509.pdf), OA) — M10/~26 kN, amplitudes/Hz a confirmar no PDF.
- **#1 IJPEM 2023** — **paywall (DOI manual, USD 39,95)**; baixar via assinatura institucional ([10.1007/s12541-023-00783-x](https://doi.org/10.1007/s12541-023-00783-x)); condições já recuperáveis do companion OA [PMC11901137](https://pmc.ncbi.nlm.nih.gov/articles/PMC11901137/).

---

## 5. Notas de acesso (baixar agora vs DOI manual)

**Open access, baixar agora:** #2 ([PMC12218038](https://pmc.ncbi.nlm.nih.gov/articles/PMC12218038/)), #4 ([TUprints](https://tuprints.ulb.tu-darmstadt.de/bitstreams/202f6597-0bd6-4bd2-bc68-454fc12b8c3f/download)), #6 ([MDPI](https://www.mdpi.com/1424-8220/24/11/3306)/[PMC11174751](https://pmc.ncbi.nlm.nih.gov/articles/PMC11174751/)), #8 ([orclever](https://www.orclever.com/api/pdf/ejrndv5i1693)), #10 ([PMC11766740](https://pmc.ncbi.nlm.nih.gov/articles/PMC11766740/pdf/materials-18-00462.pdf)).

**Open access mas hosts bloqueiam fetch automatizado (baixar manualmente no navegador):** #3 ([downloads.hindawi.com](https://downloads.hindawi.com/journals/sv/2021/1441122.pdf)), #5 ([HAL univ-evry](https://univ-evry.hal.science/hal-02398144)), #7 ([UiS Brage](https://uis.brage.unit.no/uis-xmlui/bitstream/11250/3059463/1/1-s2.0-S1350630722005647-main.pdf) ou [CORE reader](https://core.ac.uk/reader/560366445)), #9 ([Hindawi](https://downloads.hindawi.com/journals/sv/2019/2036509.pdf)).

**Paywall, DOI manual:** #1 ([10.1007/s12541-023-00783-x](https://doi.org/10.1007/s12541-023-00783-x)) — único não OA; condições suplementares no companion OA [10.3390/ma18051069](https://doi.org/10.3390/ma18051069) / [PMC11901137](https://pmc.ncbi.nlm.nih.gov/articles/PMC11901137/).

**Ressalvas transversais a anotar na digitalização:** quase todas as fontes têm eixo Y em força absoluta (normalizar por F0 conhecida); frequência não é reportada numericamente em #2, #4, #5(por grau) e #8 (no modo disp o decaimento de pré carga é largamente insensível à frequência, então é um confundidor menor); nenhuma fonte está no M16 classe 10.9 da calibração nova/reusada exceto #2 (que é 8.8) — todas as demais servem como validação cruzada de tamanho/grau, não como substitutas drop-in dos perfis existentes.