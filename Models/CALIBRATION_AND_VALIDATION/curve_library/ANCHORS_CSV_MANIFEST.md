# Manifest — anchors_csv (tabelas de dados extraidas dos .md da biblioteca)

**164 CSVs** extraidos das tabelas numericas dos arquivos `.md` de `Models/CALIBRATION_AND_VALIDATION/`
que ainda nao tinham CSV utilizavel (ou cuja versao auto-extraida em `extracted_csv/_needs_review/` estava
em formato errado — aquelas versoes foram refeitas LIMPAS aqui e estao marcadas nos blocos).
Diferente de `extracted_csv/` (curvas ciclo x F/F0 que viram ValidationCases em import-time) e de
`digitized_csv/` (curvas digitalizadas das figuras), esta pasta guarda **tabelas-ancora**: limiares,
curvas D-N, torque-preload, mu vs ciclos, theta vs ciclos, relaxacao termica/creep, loops de histerese,
DOE, mapas de modo de falha, constantes de creep com proveniencia etc. **Nao** sao consumidas
automaticamente por nenhum codigo (nenhum import as le) — mover um CSV para `extracted_csv/` exige
registrar o caso de validacao correspondente.

**Convencoes:**
- 1a linha de cada CSV: comentario `# fonte: <arquivo .md>:<linhas>`.
- Numeros copiados EXATAMENTE do .md; separadores de milhar removidos (`11,120` -> `11120`).
- Marcadores `~` (aproximado), `>` (censurado/nao atingiu), `<` (limite superior) movidos para a coluna
  `flag` (`approx`, `gt*`, `lt`) ou anotados no bloco — o numero na coluna e o do .md sem o marcador.
- Celula vazia = valor ausente no .md (`—`).
- `quality=`: **measured** (dado experimental, em geral digitalizado de figura pelo autor das notas .md —
  precisao de leitura de figura), **FEA** (resultado numerico), **representative** (valores representativos
  reconstruidos no .md a partir de tendencias do paper, ou constantes fitadas), **measured+model/measured+FEA**
  (tabela mista com colunas medidas e colunas de modelo, identificadas nos nomes das colunas).
- Datas/quantis: gerado 2026-07-08 a partir dos .md; qualquer divergencia com o paper original deve ser
  resolvida contra o PDF (BAS_V2_papers/).

**Contagem por qualidade:** FEA: 5, measured: 134, measured+FEA: 3, measured+model: 12, representative: 10.

---

### pai2002_ftr_ratio_vs_F0.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/23_Pai_Hess_2002_cap_screw_inserts.md:158-166`
- **O que e:** Forca transversal minima p/ afrouxamento rotacional (Processo IV) vs preload — 3/8"-16 UNC SHCS em insert, 100 Hz
- **Unidades/colunas:** F0_N, Ftr_min_N em N; ratio adimensional (Ftr/F0 NAO e constante: 0.378->0.489)
- **Qualidade:** measured | **Pontos:** 5

### pai2002_hysteresis_loop_5560N.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/23_Pai_Hess_2002_cap_screw_inserts.md:182-196`
- **O que e:** Loop de histerese forca transversal x deslocamento (ramos loading/unloading), F0=5560 N, excitacao 25g
- **Unidades/colunas:** disp em mm; forcas em N
- **Qualidade:** measured | **Pontos:** 7

### pai2003_fcrit_thread.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/83_84_Pai_Hess_2002_2003_thread_multibolt.md:35-45`
- **O que e:** Forca de cisalhamento critica p/ afrouxamento rotacional — rosca grossa (5/16-18 UNC) vs fina (5/16-24 UNF), por % proof
- **Unidades/colunas:** preload em % do proof; F_crit em N; digitalizada das Figs 4 e 7 (APPROXIMATE no .md)
- **Qualidade:** measured | **Pontos:** 3

### izumi_ftr_slip_fraction_FEA.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/16_Izumi_Sakai_Japanese_studies.md:58-79`
- **O que e:** Fracao de escorregamento na rosca e na cabeca vs forca transversal normalizada (FEA ANSYS M10, F0=40 kN, mu=0.15) — rosca desliza completamente em ~1.0 mu.F0, cabeca em ~1.4 mu.F0
- **Unidades/colunas:** F_trans normalizada por mu*F0; fracoes adimensionais 0-1
- **Qualidade:** FEA | **Pontos:** 11

### gong_hysteresis_params_FEA.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/20_Gong_Liu_2018_2019_FEA_factors.md:306-312`
- **O que e:** Parametros do loop de histerese Iwan (modelo modificado, fitado a FEA M12): rigidez tangente, forca de breakaway, shape n, razao residual R — por interface (rosca/cabeca)
- **Unidades/colunas:** K_T em N/mm; F_s simbolico (expressao); n e R adimensionais
- **Qualidade:** FEA | **Pontos:** 4
- **Nota:** Linha F_s e simbolica (formula), copiada como texto do .md.

### gong_lambda_cr_FEA.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/20_Gong_Liu_2018_2019_FEA_factors.md:259-286`
- **O que e:** Limiar adimensional de afrouxamento Lambda_cr = F_trans/(mu*F0) por configuracao (l/d e folga) — M12 FEA; loosening inicia quando Lambda > Lambda_cr
- **Unidades/colunas:** l_over_d e Lambda_cr adimensionais; clearance em % de d
- **Qualidade:** FEA | **Pontos:** 5

### dinger_fcrit_FEA.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/14_Dinger_Friedrich_2011_FEA.md:153-160`
- **O que e:** Forca transversal critica p/ slip completo na rosca vs na cabeca, por mu (M10, F0=40 kN, ABAQUS) — rosca controla sempre
- **Unidades/colunas:** mu adimensional; forcas em kN
- **Qualidade:** FEA | **Pontos:** 4

### dinger_eta_slip_vs_force_FEA.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/14_Dinger_Friedrich_2011_FEA.md:101-149`
- **O que e:** Parametro de estado de contato eta_n = A_slip/A_total vs forca transversal (M10, F0=40 kN, mu=0.10) — rosca atinge eta=1 em 10 kN, cabeca em 15 kN
- **Unidades/colunas:** F_trans em kN; eta_n adimensional 0-1; formato longo (surface = thread|bearing)
- **Qualidade:** FEA | **Pontos:** 14

### liu2025_clamp_oscillation_vs_amp.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/curve_library/apparatus_notes/liu2025_scirep_M16.md:30-42`
- **O que e:** Matriz Fig 3 Liu2025 SciRep M16x120 8.8 (F0=60 kN): amplitude imposta vs ciclos ate o fim (fratura/saida do plot) e amplitude de oscilacao do clamp-force
- **Unidades/colunas:** amplitude em mm; cycles_to_end em ciclos (todos ~ no .md); clamp_osc em kN
- **Qualidade:** measured | **Pontos:** 6
- **Nota:** Curvas F/F0 correspondentes ja digitalizadas em digitized_csv/liu2025_M16_amp*.csv; esta tabela e o resumo por amplitude.

### rousseau2025_loop_steel_t12.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/25_Rousseau_Bouzid_2025_material_thickness.md:162-174`
- **O que e:** Loop de histerese F_tr x deslocamento medido — aco AISI 1045 t=12 mm, ciclo 5 (F~21 kN), M12 +/-0.5 mm
- **Unidades/colunas:** disp em mm; forcas em kN
- **Qualidade:** measured | **Pontos:** 7

### rousseau2025_loop_hdpe_t12.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/25_Rousseau_Bouzid_2025_material_thickness.md:176-188`
- **O que e:** Loop de histerese F_tr x deslocamento medido — HDPE t=12 mm, ciclo 5 (F~17 kN), M12 +/-0.5 mm; loop mais estreito (menor rigidez transversal)
- **Unidades/colunas:** disp em mm; forcas em kN
- **Qualidade:** measured | **Pontos:** 7

### friede_M20_grip_cycles.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/18_Junker_test_locking_devices.md:223-231`
- **O que e:** Friede & Lange 2009: efeito do comprimento de aperto (l/d) nos ciclos ate 50% de perda — M20 sem travamento, +/-0.5 mm
- **Unidades/colunas:** l/d adimensional; N50 em ciclos (todos ~ no .md; ultimo e '5000+' = limite inferior, quase-endurance)
- **Qualidade:** measured | **Pontos:** 5
- **Nota:** Refeita LIMPA — a versao em extracted_csv/_needs_review mapeou l/d para F_over_F0 (formato errado).

### yang2011_theta_by_preload.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/06_Yang_Nassar_2011_cap_screw.md:101-135`
- **O que e:** Rotacao da porca vs ciclos por nivel de preload (5/16"-24 UNF SHCS, delta=0.71 mm, mu=0.10, 7 Hz) — colunas theta das tabelas Dataset 1 (digitalizadas da Fig 5)
- **Unidades/colunas:** F0 em N; theta em graus
- **Qualidade:** measured | **Pontos:** 20

### yang2011_theta_rate_F11120.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/06_Yang_Nassar_2011_cap_screw.md:229-243`
- **O que e:** Rotacao da porca e taxa de afrouxamento dtheta/dN vs ciclos (F0=11120 N, delta=0.71 mm, mu=0.10) — pico da taxa em 20-50 ciclos
- **Unidades/colunas:** theta em graus; taxa em graus/ciclo (vazio no ciclo 0, '—' no .md)
- **Qualidade:** measured | **Pontos:** 7

### rousseau2025_theta_by_config.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/25_Rousseau_Bouzid_2025_material_thickness.md:64-139`
- **O que e:** Rotacao da porca vs ciclos p/ as 6 configuracoes (aco/HDPE x t=10/12/14 mm), M12 +/-0.5 mm 5 Hz — colunas theta_nut das tabelas Dataset 1-2 (F/F0 ja em digitized_csv/rousseau2025_*)
- **Unidades/colunas:** t em mm; theta em graus
- **Qualidade:** measured | **Pontos:** 43

### lu2024_torque_preload_M8.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/01_Lu_2024_M8_tangential_parametric.md:59-69`
- **O que e:** Relacao torque de aperto -> preload inicial medido, M8 zincado seco (K~0.238)
- **Unidades/colunas:** T em N.m; F0 em N; pct em % do proof
- **Qualidade:** measured | **Pontos:** 5

### jiang2004_DN_M12.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/02_Jiang_2003_2004_M12_early_stage.md:166-183`
- **O que e:** Curva D-N (amplitude vs vida de afrouxamento) M12, F0=25 kN — ciclos ate 10% e ate 50% de F0; endurance ~0.25-0.30 mm
- **Unidades/colunas:** delta em mm; N em ciclos (valores ~ no .md); linha 0.254 = nao afrouxou (campos vazios)
- **Qualidade:** measured | **Pontos:** 8

### zhang2006_N50_vs_grip.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/03_Zhang_Jiang_2006_clamped_length.md:115-121`
- **O que e:** Ciclos ate 50% de perda vs razao l/d (comprimento de aperto), M12 delta=0.46 mm F0=25 kN
- **Unidades/colunas:** l/d adimensional; N50 em ciclos (todos ~ no .md)
- **Qualidade:** measured | **Pontos:** 4
- **Nota:** Refeita limpa — versao _needs_review em formato errado.

### sakai2011_axial_rotation.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/16_Izumi_Sakai_Japanese_studies.md:148-160`
- **O que e:** Sakai 2011: rotacao da porca apos 500 ciclos vs forca axial pulsante (M16, F0=35 kN) — limiar de afrouxamento axial em F_ax/F0~0.80 (quase separacao)
- **Unidades/colunas:** F_axial em kN; theta em graus apos 500 ciclos
- **Qualidade:** representative | **Pontos:** 7
- **Nota:** Proveniencia nao marcada no .md (sem tag APPROXIMATE/medido) — tratar como representativa do paper D (Sakai 2011). Refeita limpa da versao _needs_review.

### hattori2010_Scr_vs_F0_M16.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/11_Hattori_2010_critical_slippage.md:64-88`
- **O que e:** Escorregamento critico S_cr (deslocamento p/ slip completo da cabeca) vs preload, M16 classe 4.8 — S_cr cresce ~linear com F0
- **Unidades/colunas:** F0 em kN; S_cr em mm; S_cr/d adimensional
- **Qualidade:** measured | **Pontos:** 5

### hattori2010_loosening_speed_M16.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/11_Hattori_2010_critical_slippage.md:91-108`
- **O que e:** Velocidade de afrouxamento (N/ciclo apos onset do Estagio II) vs amplitude de deslocamento, M16 F0=25 kN — cresce ~(S/S_cr - 1)^2
- **Unidades/colunas:** delta em mm; speed em N/ciclo (~ no .md); S/S_cr adimensional
- **Qualidade:** measured | **Pontos:** 9
- **Nota:** Refeita limpa — versao _needs_review em formato errado.

### hattori2010_Scr_cross_size.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/11_Hattori_2010_critical_slippage.md:130-143`
- **O que e:** Comparacao cross-size do escorregamento critico normalizado (M6/M10/M16) — S_cr/d ~constante 0.020-0.030 p/ dado F0/Fs (relacao de similitude)
- **Unidades/colunas:** F0 em kN; F0/Fs e S_cr/d adimensionais; S_cr em mm
- **Qualidade:** measured | **Pontos:** 6

### hattori2010_reaction_torques_M16.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/11_Hattori_2010_critical_slippage.md:111-126`
- **O que e:** Decomposicao dos torques de reacao (rosca vs cabeca) por fase do ciclo de deslocamento (M16, F0=25 kN, S=0.6 mm) — torque de afrouxamento positivo so na reversao
- **Unidades/colunas:** torques em N.m; sinal + = resistindo, - = assistindo (convencao do .md)
- **Qualidade:** representative | **Pontos:** 6
- **Nota:** Digitalizada da Fig 4; o .md nao explicita se e medicao ou FEA — marcada representative.

### eraliev2021_thermal_cycle_preload.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/12_Eraliev_2021_thermal_cycling.md:48-69`
- **O que e:** Preload no pico de temperatura e apos resfriamento, por ciclo termico (aco-aco, F0=5 kN, sem carga mecanica) — perda satura apos ~5 ciclos
- **Unidades/colunas:** forcas em N (picos ~ no .md); ratio adimensional; loss em N/ciclo
- **Qualidade:** measured | **Pontos:** 11
- **Nota:** F_peak marcado ~ no .md (aprox.). Digitalizada das Figs 5-7.

### eraliev2021_preload_vs_temp_cycle1.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/12_Eraliev_2021_thermal_cycling.md:71-93`
- **O que e:** Preload vs temperatura DENTRO do 1o ciclo termico (ramo aquecimento + resfriamento) — histerese termica: retorna a 25C com 10% de perda (embedding a quente)
- **Unidades/colunas:** T em C; F em N
- **Qualidade:** measured | **Pontos:** 15

### yang2021_failure_mode_map.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/13_Yang_2021_combined_loading.md:139-165`
- **O que e:** Mapa de modo de falha afrouxamento vs fadiga — razao critica xi = delta/F_axial (M8 classe 8.8); xi_cr ~0.075 mm/kN
- **Unidades/colunas:** delta em mm; F_axial em kN; xi em mm/kN (inf = sem axial); vida em ciclos (~ no .md)
- **Qualidade:** measured | **Pontos:** 6
- **Nota:** Vidas com ~ no .md; linha 1 xi=infinito (sem carga axial).

### eccles2010_mu_retightening.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/17_Eccles_2010_tribological.md:39-56`
- **O que e:** Evolucao do atrito e do preload alcancado em reapertos repetidos a T=25 N.m (M8 zincado 10.9) — mu dobra e preload cai 50% em 10 reapertos
- **Unidades/colunas:** mu_total adimensional; F em kN; pct em % do preload virgem
- **Qualidade:** measured | **Pontos:** 8
- **Nota:** Anchor direto p/ reaperto/galling (k_gall, retighten()). Versao em extracted_csv perdia a coluna mu.

### eccles2010_mu_evolution_vibration.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/17_Eccles_2010_tribological.md:67-98`
- **O que e:** Evolucao de mu_thread e mu_bearing DURANTE afrouxamento por vibracao (M8 zincado, F0=22 kN, DIN 25201-4): fase 1 mu sobe (0-50 cyc), fase 2 mu cai (50-500)
- **Unidades/colunas:** mu adimensionais; F em kN; ratio adimensional
- **Qualidade:** measured | **Pontos:** 8
- **Nota:** Fase 3 (linhas '500+' e '1000+' do .md, mu 0.08/0.07 e 0.06/0.05) excluida por rotulo de ciclo nao-numerico e conflito com a linha 500 da fase 2.

### eccles2010_coating_comparison.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/17_Eccles_2010_tribological.md:102-114`
- **O que e:** Efeito do revestimento: mu inicial vs ciclos ate 50% e 80% de perda (M8 10.9, ~70% proof) — menor atrito = afrouxamento mais rapido
- **Unidades/colunas:** mu adimensional; N em ciclos (todos ~ no .md)
- **Qualidade:** measured | **Pontos:** 7

### eccles2010_prevailing_torque_nylon.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/17_Eccles_2010_tribological.md:118-131`
- **O que e:** Degradacao do torque prevalecente da porca nylon (DIN 985 M8) junto com o decaimento F/F0 — perde ~88% do prevailing em 2000 ciclos
- **Unidades/colunas:** ratio adimensional; torque em N.m
- **Qualidade:** measured | **Pontos:** 7

### eccles2010_prevailing_torque_allmetal.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/17_Eccles_2010_tribological.md:133-142`
- **O que e:** Degradacao do torque prevalecente da porca all-metal (DIN 6925 M8) junto com o decaimento F/F0
- **Unidades/colunas:** ratio adimensional; torque em N.m
- **Qualidade:** measured | **Pontos:** 7

### eccles2010_torque_residual.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/17_Eccles_2010_tribological.md:158-171`
- **O que e:** Metodo do torque residual de Eccles: T_residual/T_inicial vs F/F0 ao longo dos ciclos — auditoria de afrouxamento por torque
- **Unidades/colunas:** razoes adimensionais
- **Qualidade:** measured | **Pontos:** 4
- **Nota:** Versao em extracted_csv guardou so a coluna de torque rotulada como F_over_F0 — refeita com as duas colunas.

### nasa2018_cupcone_positions.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/19_Sandia_NASA_reports.md:72-83`
- **O que e:** NASA TP-2018-219787: perda de preload por posicao de parafuso (junta cup-cone 6 parafusos, vibracao randomica de qualificacao) — 2 parafusos perderam 50%
- **Unidades/colunas:** valores em % do preload inicial (~ no .md)
- **Qualidade:** measured | **Pontos:** 6

### junker1995_thread_movement.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/19_Sandia_NASA_reports.md:120-139`
- **O que e:** Junker & Wallace (NASA CR-195390, 1/2"-13 UNC): movimento relativo da rosca por ciclo e perda de preload por ciclo vs amplitude transversal (medicao optica)
- **Unidades/colunas:** delta em mm; theta em graus/ciclo; dF em N/ciclo; flag lt = valor '<' (limite superior), approx = '~'
- **Qualidade:** measured | **Pontos:** 6
- **Nota:** Refeita limpa da versao _needs_review.

### sanclemente2007_doe_runs.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/24_Sanclemente_Hess_2007_DOE_factorial.md:62-85`
- **O que e:** DOE fatorial 2^6 completo (16 runs, EXATO da Table 2 do paper): perda de preload apos 500 ciclos por combinacao diametro/pitch/preload/material/folga/lubrificacao
- **Unidades/colunas:** loss em % de F0; fatores categoricos (1/4in = 1/4", 1/2in = 1/2")
- **Qualidade:** measured | **Pontos:** 16
- **Nota:** O .md marca [From Table 2 in paper — EXACT values]. ANOVA e main-effects sao derivados destes 16 runs (nao extraidos).

### yang2019_DN_M10.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/09_Yang_2019_M10_variable_amplitude.md:119-132`
- **O que e:** Curva D-N M10 (F0=26 kN): vida N_L ate 10% de F0 vs amplitude; limiar de endurance ~0.30 mm
- **Unidades/colunas:** delta em mm; N_L em ciclos; flag gt = '>' (nao atingiu), approx = '~'
- **Qualidade:** measured | **Pontos:** 8
- **Nota:** Colunas log10 do .md sao derivadas — nao copiadas.

### yang2019_freq_independence.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/09_Yang_2019_M10_variable_amplitude.md:153-162`
- **O que e:** Verificacao de independencia de frequencia: ciclos ate 50% de perda a delta=0.6 mm p/ 5-20 Hz (sem efeito)
- **Unidades/colunas:** freq em Hz; N50 em ciclos (todos ~ no .md)
- **Qualidade:** measured | **Pontos:** 4

### yang2019_miner_blocks.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/09_Yang_2019_M10_variable_amplitude.md:166-186`
- **O que e:** Carregamento em dois blocos (validacao de Miner p/ afrouxamento): high_to_low = 0.8->0.6 mm, low_to_high = 0.6->0.8 mm; soma de Miner D=0.85-1.05
- **Unidades/colunas:** n em ciclos; fracoes e soma adimensionais
- **Qualidade:** measured | **Pontos:** 6
- **Nota:** n2 marcado ~ no .md.

### yang2023_DN_M8_M6.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/10_Yang_2023_phenomenological_model.md:159-181`
- **O que e:** Curvas D-N de vida de afrouxamento (N_L ate 10% F0) p/ M8 (F0=14.3 kN) e M6 (F0=8.5 kN)
- **Unidades/colunas:** delta em mm; N_L em ciclos; flag gt_threshold = '>' (limiar)
- **Qualidade:** measured | **Pontos:** 11
- **Nota:** Fits do .md: N_L=C*delta^-m com C~10.5/m~3.8 (M8), C~5.2/m~3.5 (M6).

### yangjeong2025_DN_M6_M8.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/26_Yang_Jeong_2025_variable_amplitude_multibolt.md:61-97`
- **O que e:** Curvas D-N (vida ate 20% de perda) M6 (F0=11 kN) e M8 (F0=14.3 kN), 10 Hz
- **Unidades/colunas:** delta em mm; N_L em ciclos; flag gt = '>100000'
- **Qualidade:** measured | **Pontos:** 15
- **Nota:** Regressao do .md: log10(NL)=A-m*log10(delta); M6 A=1.48 m=6.82 R2=0.987 th~0.30; M8 A=1.78 m=7.15 R2=0.991 th~0.35.

### yangjeong2025_miner_blocks.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/26_Yang_Jeong_2025_variable_amplitude_multibolt.md:139-162`
- **O que e:** Blocos de amplitude variavel (2 blocos, troca a 50% da vida): detalhe por bloco — seq 1-2 = M8, seq 3 = M6
- **Unidades/colunas:** delta em mm; N e n em ciclos; fracoes adimensionais
- **Qualidade:** measured | **Pontos:** 6

### yangjeong2025_LDR_summary.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/26_Yang_Jeong_2025_variable_amplitude_multibolt.md:164-175`
- **O que e:** Validacao da regra linear de dano (Miner/LDR) p/ afrouxamento: D experimental por sequencia (media 0.993, sd 0.062)
- **Unidades/colunas:** D adimensional; erro em %
- **Qualidade:** measured | **Pontos:** 6

### yangjeong2025_multibolt_NL.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/26_Yang_Jeong_2025_variable_amplitude_multibolt.md:179-190`
- **O que e:** Validacao multi-parafuso (4x M8, carga excentrica): delta por parafuso via FEA -> N_L previsto pela D-N vs N_L experimental (previsoes +/-20%, conservadoras)
- **Unidades/colunas:** delta em mm (FEA); N em ciclos; flag gt_exp = experimental '>30000'
- **Qualidade:** measured+FEA | **Pontos:** 4

### karlsen2022_retention_2000cyc.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/29_Karlsen_Lemu_2022_large_bolt_M20_M42.md:147-157`
- **O que e:** Resumo de retencao a 2000 ciclos: standard HV vs Bondura (body-fit) p/ M20/M30/M42 e amplitudes
- **Unidades/colunas:** delta em mm; ratios adimensionais; improvement = fator do .md
- **Qualidade:** measured | **Pontos:** 5

### nechache2007_gasket_norton.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/30_Nechache_Bouzid_2007_creep_flange_joints.md:32-38`
- **O que e:** Propriedades de creep Norton de gaxetas (lei epsilon_dot = A*sigma^n*exp(-Q/RT)) — proveniencia p/ C_creep por par (gaxeta)
- **Unidades/colunas:** A em 1/s/MPa^n; Q em kJ/mol; faixa de temperatura em C
- **Qualidade:** representative | **Pontos:** 3
- **Nota:** Constantes de literatura compiladas no .md (nao curva medida) — quality=representative.

### nechache2007_B7_norton.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/30_Nechache_Bouzid_2007_creep_flange_joints.md:40-47`
- **O que e:** Propriedades de creep Norton do parafuso SA-193 B7 por temperatura — proveniencia p/ creep de parafuso a quente
- **Unidades/colunas:** T em C; A em 1/s/MPa^n; n adimensional
- **Qualidade:** representative | **Pontos:** 4

### denotter2020_creep_M16_5083.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/31_den_Otter_Maljaars_2020_stainless_steel_aluminum.md:64-103`
- **O que e:** Creep estatico (BoltSafe, 2500 h) M16 A4 em aluminio 5083 — efeito do nivel de preload (0.70/0.50/0.27 f_u)
- **Unidades/colunas:** tempo em horas; ratios F/F0 adimensionais; digitalizada da Fig 5
- **Qualidade:** measured | **Pontos:** 7
- **Nota:** Anchor de creep por par (SS/aluminio) — cf. secao 4.7 MODEL_LEGITIMACY (C_creep por par).

### denotter2020_creep_M16_materials.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/31_den_Otter_Maljaars_2020_stainless_steel_aluminum.md:105-119`
- **O que e:** Creep estatico M16 a 70% f_u: comparacao de ligas de aluminio (5083/5454 nao-tratavel vs 6061-T6 endurecida) — 6061 ~40% menos creep
- **Unidades/colunas:** tempo em horas; ratios adimensionais
- **Qualidade:** measured | **Pontos:** 7

### denotter2020_creep_M16_vs_M24.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/31_den_Otter_Maljaars_2020_stainless_steel_aluminum.md:121-131`
- **O que e:** Creep estatico em 5083: M16 vs M24 a 70% f_u — M24 retem ligeiramente mais (menor pressao de contato)
- **Unidades/colunas:** tempo em horas; ratios adimensionais
- **Qualidade:** measured | **Pontos:** 4

### sase1996_devices_7types.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/32_Sase_Koga_1996_anti_loosening_nuts_7types.md:52-66`
- **O que e:** Comparacao de 7 dispositivos anti-afrouxamento (deslocamento forcado +/-0.5 mm, 10.9, F0=40.6 kN) — porca dupla e U-nut efetivas; nylon/metal insert inefetivas
- **Unidades/colunas:** ratios F/F0 adimensionais; digitalizada da Fig 4
- **Qualidade:** measured | **Pontos:** 7
- **Nota:** A versao 32_...__Device_Configurations__1.csv em extracted_csv esta corrompida (3000,1.0000 repetido).

### sase1996_amplitude_standard_nut.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/32_Sase_Koga_1996_anti_loosening_nuts_7types.md:81-90`
- **O que e:** Porca padrao 10.9: efeito da amplitude (+/-0.3 a +/-1.0 mm)
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 5

### sase1996_grade_4p8_vs_10p9.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/32_Sase_Koga_1996_anti_loosening_nuts_7types.md:93-104`
- **O que e:** Porca padrao +/-0.5 mm: classe 4.8 (F0=16.8 kN) vs 10.9 (F0=40.6 kN) — nivel ABSOLUTO de preload domina
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 5

### sase1996_shaking_30g.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/32_Sase_Koga_1996_anti_loosening_nuts_7types.md:107-117`
- **O que e:** Shaking de alta aceleracao (30 g, 200 Hz): 4 dispositivos vs tempo
- **Unidades/colunas:** tempo em minutos; ratios adimensionais
- **Qualidade:** measured | **Pontos:** 6

### duqiu2025_sor_loading_types.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/33_Du_Qiu_2025_sine_on_random_vibration.md:54-107`
- **O que e:** Comparacao seno puro vs random puro vs SOR (sine-on-random), F0=25 kN/parafuso — acoplamento SOR afrouxa 2.5x mais rapido
- **Unidades/colunas:** tempo em minutos; ratios adimensionais; celula vazia = tempo nao reportado p/ a condicao
- **Qualidade:** measured | **Pontos:** 8
- **Nota:** Rotulos de estagio (Steady/Transition/Loosen) do .md nao copiados — ver duqiu2025_sor_transition_times.csv.

### duqiu2025_sor_transition_times.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/33_Du_Qiu_2025_sine_on_random_vibration.md:109-126`
- **O que e:** Tempos p/ entrar nos estagios Transition e Loosen por condicao (criterio 3 estagios por dF/dt)
- **Unidades/colunas:** tempos em minutos; flag gt_loosen = '>240'
- **Qualidade:** measured | **Pontos:** 4

### duqiu2025_sor_bolt_variation.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/33_Du_Qiu_2025_sine_on_random_vibration.md:130-142`
- **O que e:** Variacao entre parafusos na montagem de 4 (condicao C, 120 min): mais longe do CG = mais afrouxamento (~6% spread)
- **Unidades/colunas:** ratio adimensional
- **Qualidade:** measured | **Pontos:** 4

### duqiu2025_sor_equiv_amplitude.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/33_Du_Qiu_2025_sine_on_random_vibration.md:145-160`
- **O que e:** Modelo de superposicao SOR: amplitude equivalente delta_eq = sqrt(delta_sine^2 + 3*sigma_random^2) -> N_L previsto vs medido (~10% erro)
- **Unidades/colunas:** deltas/sigma em mm; N em ciclos; erro em %
- **Qualidade:** measured+model | **Pontos:** 2

### amano2024_backlash_vs_retention.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/34_Amano_2024_double_thread_bolt_ISO16130.md:125-138`
- **O que e:** DTB-IIC M12 (parafuso rosca dupla): retencao a 2000 ciclos e torque prevalecente vs folga axial (backlash) — Rating-1 exige backlash <= 0.03 mm
- **Unidades/colunas:** backlash em mm; ratio adimensional; torque em N.m
- **Qualidade:** measured | **Pontos:** 6
- **Nota:** Refeita limpa da versao _needs_review.

### zhang2019_wear_exp_vs_fea.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/35_36_37_38_wear_material_rotational_direction.md:20-32`
- **O que e:** Zhang 2019 (UMESHMOTION): decaimento medido vs FEA com desgaste vs FEA sem desgaste (M10, F0=30 kN, +/-0.5 mm) — sem desgaste superprediz retencao em 27%
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured+FEA | **Pontos:** 5

### zhang2019_wear_depth.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/35_36_37_38_wear_material_rotational_direction.md:34-41`
- **O que e:** Profundidade de desgaste no flanco do 1o filete: medida (SEM) vs FEA — anchor direto p/ K_archard (k_wear=3.5e-7 mm3/N.mm usado no paper)
- **Unidades/colunas:** profundidades em micrometros
- **Qualidade:** measured+FEA | **Pontos:** 3

### bhattacharya2010_M12_devices.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/35_36_37_38_wear_material_rotational_direction.md:71-84`
- **O que e:** Bhattacharya 2010 (M12 10.9, 12600 oscilacoes 23.3 Hz): retencao final por dispositivo anti-afrouxamento
- **Unidades/colunas:** ratio adimensional
- **Qualidade:** measured | **Pontos:** 7

### bhattacharya2010_M12_materials.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/35_36_37_38_wear_material_rotational_direction.md:85-96`
- **O que e:** Bhattacharya 2010: comparacao de materiais de parafuso M12 sem dispositivo (baixo carbono vs alta resistencia vs inox) a mesma fracao de proof
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 5

### li2021_rotational_freq.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/35_36_37_38_wear_material_rotational_direction.md:120-133`
- **O que e:** Li 2021 (vibracao ROTACIONAL, M10, F0=25 kN, theta=1.0 grau): efeito da frequencia 5/10/20 Hz — freq importa mais que no transversal
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 6

### li2021_rotational_amplitude.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/35_36_37_38_wear_material_rotational_direction.md:135-142`
- **O que e:** Li 2021: efeito da amplitude rotacional (0.5-2.0 graus, F0=25 kN, 10 Hz)
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 4

### yan2024_load_direction.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/35_36_37_38_wear_material_rotational_direction.md:177-188`
- **O que e:** Yan 2024 (dispositivo multi-direcional, M10, F0=25 kN, delta=0.5 mm): decaimento por angulo de carga 0 (axial) a 90 graus (transversal)
- **Unidades/colunas:** ratios adimensionais; colunas por angulo em graus a partir do eixo do parafuso
- **Qualidade:** measured | **Pontos:** 5

### yan2024_N50_by_direction.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/35_36_37_38_wear_material_rotational_direction.md:189-206`
- **O que e:** Yan 2024: ciclos ate 50% de perda vs direcao — N50 ~ N90/sin^2(alpha)
- **Unidades/colunas:** angulo em graus; N50 em ciclos; flag gt = '>'
- **Qualidade:** measured | **Pontos:** 7

### hess2018_locking_moments.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/39_40_41_42_locking_AI_deepsea_3Dprint.md:22-34`
- **O que e:** Hess 2018 (ESMATS/NASA, 0.250-28 UNJF A-286, F0=8.9 kN): momento de travamento medido (media e desvio) p/ 6 dispositivos aeroespaciais
- **Unidades/colunas:** torques em N.m
- **Qualidade:** measured | **Pontos:** 6
- **Nota:** Anchor p/ locking_devices.json (momento de travamento requerido T_pitch-T_friction ~0.5-0.9 N.m p/ esse parafuso).

### karakaya2023_taguchi_L16.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/39_40_41_42_locking_AI_deepsea_3Dprint.md:85-107`
- **O que e:** Karakaya 2023 (chassi automotivo M10): DOE Taguchi L16 — perda a 10000 ciclos por (F0, delta, freq); coluna NN = previsao da rede neural
- **Unidades/colunas:** F0 em kN; delta em mm; f em Hz; perdas em % de F0
- **Qualidade:** measured+model | **Pontos:** 16

### wi2022_3dprint_thermal.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/39_40_41_42_locking_AI_deepsea_3Dprint.md:191-205`
- **O que e:** Wi 2022: parafusos M12 impressos em 3D (ABS-2/PLA/nylon-vidro) sob ciclagem termica 10-80C vs aco (ref) — PLA perde 46% em 50 ciclos
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 6

### hess2023_jackbolt_vs_hex.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/43_44_45_46_jackbolt_washer_doublenut_pitch.md:28-40`
- **O que e:** Hess 2023: porca heavy hex vs porca jack bolt (multi-jackbolt tensioner), 3/4"-10 UNC, F0=44.5 kN, +/-0.635 mm 12.5 Hz
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 6

### hess2023_jackbolt_preload_effect.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/43_44_45_46_jackbolt_washer_doublenut_pitch.md:41-50`
- **O que e:** Hess 2023: retencao da porca jack bolt a 1000 ciclos vs preload (22.2-89.0 kN)
- **Unidades/colunas:** F0 em kN; ratio adimensional
- **Qualidade:** measured | **Pontos:** 4
- **Nota:** Refeita limpa da versao _needs_review.

### hess2023_jackbolt_secondary.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/43_44_45_46_jackbolt_washer_doublenut_pitch.md:52-60`
- **O que e:** Hess 2023: travamento secundario adicional na porca jack bolt (lockwire/adesivo/set screws soldados)
- **Unidades/colunas:** retencao em % de F0 a 1000 ciclos
- **Qualidade:** measured | **Pontos:** 4

### dravid2023_washer_fullthread.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/43_44_45_46_jackbolt_washer_doublenut_pitch.md:85-96`
- **O que e:** Dravid 2023 (M12 8.8, +/-0.5 mm 10 Hz): parafuso todo-rosca — sem arruela vs arruela plana vs arruela de pressao (plana vence)
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 5

### dravid2023_washer_plainshank.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/43_44_45_46_jackbolt_washer_doublenut_pitch.md:97-106`
- **O que e:** Dravid 2023: parafuso com haste lisa — sem arruela vs plana vs pressao (haste lisa > todo-rosca em ~25%)
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 5

### dravid2023_undertightening.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/43_44_45_46_jackbolt_washer_doublenut_pitch.md:107-115`
- **O que e:** Dravid 2023: efeito do sub-aperto (80/90/100% do alvo 49 kN), haste lisa + arruela plana
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 4

### xu2025_odn_torque_ratio.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/43_44_45_46_jackbolt_washer_doublenut_pitch.md:158-171`
- **O que e:** Xu 2025 (porca dupla M12 10.9, 2T=80 N.m, +/-0.65 mm): efeito da razao de torque slave/main — otimo em 0.5T/1.5T
- **Unidades/colunas:** ratios adimensionais; colunas = razao torque slave/main
- **Qualidade:** measured | **Pontos:** 6

### xu2025_single_vs_doublenut.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/43_44_45_46_jackbolt_washer_doublenut_pitch.md:173-187`
- **O que e:** Xu 2025: porca simples vs porca dupla comum (ODN) vs flat-slave (FODN), ambas no otimo 0.5T/1.5T
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 5

### noda2016_pitch_difference.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/43_44_45_46_jackbolt_washer_doublenut_pitch.md:210-221`
- **O que e:** Noda 2016 (M10 SCM435, F0=35 kN, +/-0.5 mm): retencao vs diferenca de passo proposital bolt-nut (Dp=0 a 0.020 mm)
- **Unidades/colunas:** ratios adimensionais; colunas por Dp em mm
- **Qualidade:** measured | **Pontos:** 5

### noda2016_prevailing_torque.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/43_44_45_46_jackbolt_washer_doublenut_pitch.md:222-231`
- **O que e:** Noda 2016: torque prevalecente gerado pela diferenca de passo (a F0=35 kN)
- **Unidades/colunas:** Dp em mm; torque em N.m
- **Qualidade:** measured | **Pontos:** 5

### noda2016_fatigue_life.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/43_44_45_46_jackbolt_washer_doublenut_pitch.md:232-239`
- **O que e:** Noda 2016: melhoria de vida em fadiga com diferenca de passo (redistribui carga entre filetes; Kt 4.2->3.1)
- **Unidades/colunas:** vida em milhares de ciclos; improvement = fator
- **Qualidade:** measured | **Pontos:** 3

### brownlim2017_385C_relaxation.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/47_48_49_50_hightemp_B7_B16_IN718_IN783.md:41-87`
- **O que e:** Brown & Lim 2017 (ASME PVP, flange NPS4 cl.300): relaxacao do bolt load a 385C — B7 vs B16 vs B8M (B8M SOBE ~8% por CTE diferencial)
- **Unidades/colunas:** tempo em horas; ratios F/F0 adimensionais (B7/B16: F0=120 kN; B8M: F0=45 kN)
- **Qualidade:** measured | **Pontos:** 9

### brownlim2017_temp_ramp.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/47_48_49_50_hightemp_B7_B16_IN718_IN783.md:98-106`
- **O que e:** Brown & Lim 2017: efeito da rampa de temperatura (20->385C) no bolt load por grau de parafuso
- **Unidades/colunas:** T em C; ratios adimensionais
- **Qualidade:** measured | **Pontos:** 5

### bapokutty2012_IN718_relaxation.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/47_48_49_50_hightemp_B7_B16_IN718_IN783.md:140-154`
- **O que e:** Bapokutty 2012: relaxacao de tensao IN718 (strain fixo 1.0%) a 550/650/750C por 24 h — a 750C gamma'' dissolve e relaxacao acelera
- **Unidades/colunas:** tempo em horas; sigma/sigma0 adimensional
- **Qualidade:** measured | **Pontos:** 8

### rahimi2017_IN718_720C.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/47_48_49_50_hightemp_B7_B16_IN718_IN783.md:186-200`
- **O que e:** Rahimi 2017 (Strathclyde/Rolls-Royce): relaxacao IN718 a 720C por nivel de tensao inicial (300/500/800 MPa) — modelo hiperbolico com sigma_inf/sigma0 ~0.35
- **Unidades/colunas:** tempo em horas; sigma/sigma0 adimensional
- **Qualidade:** measured | **Pontos:** 8
- **Nota:** Params do modelo hiperbolico no .md: sigma_inf/sigma0=0.35+/-0.05, tau=5.2 h, n=0.45 (720C).

### in783_relax_0p15strain.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/47_48_49_50_hightemp_B7_B16_IN718_IN783.md:237-248`
- **O que e:** INCONEL 783 (creep NEGATIVO): evolucao de tensao a 0.15% strain por temperatura — a 482C a tensao SOBE +6% (precipitacao beta, contracao volumetrica)
- **Unidades/colunas:** tempo em horas; sigma/sigma0 adimensional
- **Qualidade:** measured | **Pontos:** 5

### liu2016_retighten_axial.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/51_52_53_54_axial_fatiguewear_noload_energy.md:57-70`
- **O que e:** Liu 2016 (Wear; M10 8.8 EZP, excitacao axial 12.5 kN): preload alcancado e retencao apos 5000 ciclos por ciclo de reaperto — estabiliza apos ~3 reapertos
- **Unidades/colunas:** forcas em kN; loss em % (perda no bloco de 5000 ciclos de vibracao)
- **Qualidade:** measured | **Pontos:** 8
- **Nota:** Anchor direto p/ embedding renewal / retighten() (roadmap #5). Cabecalho do .md diz 'Loss per vib. cycle (%)' mas os valores sao a perda percentual do bloco de 5000 ciclos.

### liu2016_retighten_kfactor.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/51_52_53_54_axial_fatiguewear_noload_energy.md:74-85`
- **O que e:** Liu 2016: torque constante 30 N.m -> preload alcancado cai e K-factor sobe com reuso (dano superficial)
- **Unidades/colunas:** T em N.m; F0 em kN; K adimensional
- **Qualidade:** measured | **Pontos:** 5

### liu2016_retighten_Ra.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/51_52_53_54_axial_fatiguewear_noload_energy.md:88-97`
- **O que e:** Liu 2016 (SEM): rugosidade Ra da superficie da rosca por ciclo de reaperto — dano progressivo (0.8 -> 3.2 um)
- **Unidades/colunas:** Ra em micrometros; retighten_cycle 0 = novo
- **Qualidade:** measured | **Pontos:** 5

### fan2023_loosening_vs_amplitude.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/51_52_53_54_axial_fatiguewear_noload_energy.md:125-134`
- **O que e:** Fan 2023 (M10 10.9, F0=35 kN, 10 Hz): grau de afrouxamento a 10000 ciclos vs amplitude (0.3-1.1 mm)
- **Unidades/colunas:** delta em mm; ratio adimensional; loosening em %
- **Qualidade:** measured | **Pontos:** 5
- **Nota:** Refeita limpa da versao _needs_review.

### fan2023_fatigue_life_stats.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/51_52_53_54_axial_fatiguewear_noload_energy.md:167-181`
- **O que e:** Fan 2023: estatistica de vida em fadiga a delta=1.1 mm (5 amostras) — distribuicao normal confirmada (Shapiro-Wilk p=0.82)
- **Unidades/colunas:** vida em ciclos ate fratura; media 3486, desvio 487, COV 14.0% (do .md)
- **Qualidade:** measured | **Pontos:** 5

### liu2021_noload_relaxation.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/51_52_53_54_axial_fatiguewear_noload_energy.md:214-229`
- **O que e:** Liu 2021 (M16 10.9, F0=120 kN, SEM CARGA EXTERNA): relaxacao pos-aperto por 48 h — 8.8% de perda so de recuperacao elastica + fluxo plastico
- **Unidades/colunas:** time_label do .md; time_s convertido (10s/1min/5min/30min/1h/6h/24h/48h); ratio adimensional
- **Qualidade:** measured | **Pontos:** 9
- **Nota:** Anchor p/ conformacao/settling sem vibracao (relaxacao de curto prazo pos-aperto).

### liu2021_noload_vs_preload.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/51_52_53_54_axial_fatiguewear_noload_energy.md:243-253`
- **O que e:** Liu 2021: perda em 48 h (sem carga externa) vs nivel de preload — aperto a 90% proof relaxa ~5x mais que a 30%
- **Unidades/colunas:** F0 em kN; pct em % do proof; loss em % de F0
- **Qualidade:** measured | **Pontos:** 5
- **Nota:** Anchor DIRETO p/ conformacao dependente de pressao (gate p/p_ref — sec 4.9 MODEL_LEGITIMACY): perda cresce superlinear com o preload.

### icmez2025_model_vs_exp.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/51_52_53_54_axial_fatiguewear_noload_energy.md:297-309`
- **O que e:** Icmez 2025 (modelo energia-equilibrio, M10 8.8, F0=25 kN, +/-0.5 mm): experimento vs modelo analitico fechado
- **Unidades/colunas:** ratios adimensionais; erro em %
- **Qualidade:** measured+model | **Pontos:** 6

### qiao2025_torque_preload_M10.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/55_56_57_58_GPR_Iwan_reliability_arclock.md:24-64`
- **O que e:** Qiao 2025 (120 apertos, M10 8.8, ultrassonico): torque->preload com MEDIA e DESVIO por superficie (dry/oiled/MoS2) + K-factor
- **Unidades/colunas:** T em N.m; F em kN; K adimensional; scatter cresce com o torque
- **Qualidade:** measured | **Pontos:** 25
- **Nota:** Melhor anchor torque-preload com incerteza da biblioteca.

### yuan2024_iwan_hysteresis.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/55_56_57_58_GPR_Iwan_reliability_arclock.md:141-172`
- **O que e:** Yuan 2024 (M8 10.9, F0=15 kN, 0.3 mm 50 Hz): loops de histerese medidos em 3 instantes (ciclo 100/5000/10000) — area e rigidez caem com a degradacao do preload
- **Unidades/colunas:** disp em mm; forcas em kN; cycle_snapshot = ciclo do loop
- **Qualidade:** measured | **Pontos:** 15

### yuan2024_stiffness_damping.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/55_56_57_58_GPR_Iwan_reliability_arclock.md:174-183`
- **O que e:** Yuan 2024: evolucao da rigidez efetiva e amortecimento equivalente com o preload — base do Iwan variante no tempo
- **Unidades/colunas:** k em kN/mm; c em kN.s/mm; F em kN
- **Qualidade:** measured | **Pontos:** 5
- **Nota:** Refeita com todas as colunas — versao em extracted_csv era 2-colunas com semantica perdida.

### li2019_interaction_coeffs.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/63_64_65_66_thermal_interaction_CFRP_cycling.md:99-116`
- **O que e:** Li 2019 (4 parafusos M10 quadrado, strain gauge): coeficientes de interacao elastica alpha_ij (apertar j relaxa i em alpha*Fj) — adjacente 0.045, diagonal 0.025
- **Unidades/colunas:** alpha adimensional
- **Qualidade:** measured | **Pontos:** 12

### li2019_seq_4bolt.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/63_64_65_66_thermal_interaction_CFRP_cycling.md:118-147`
- **O que e:** Li 2019: preload residual apos aperto sequencial 4 parafusos — sequencias A (circular), B (cruz), C (compensada com sobre-aperto) — compensacao reduz erro p/ ~1-2%
- **Unidades/colunas:** forcas em kN; erro em % do alvo 35 kN; tighten_order = ordem de aperto na sequencia
- **Qualidade:** measured | **Pontos:** 12
- **Nota:** Sequencias A/B: applied = alvo (35 kN); sequencia C: applied = sobre-aperto compensado.

### li2019_8bolt_scatter.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/63_64_65_66_thermal_interaction_CFRP_cycling.md:149-157`
- **O que e:** Li 2019: padrao circular de 8 parafusos — media/desvio/scatter maximo por estrategia de aperto
- **Unidades/colunas:** forcas em kN; scatter em %
- **Qualidade:** measured | **Pontos:** 4

### hu2020_interference_23C.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/63_64_65_66_thermal_interaction_CFRP_cycling.md:183-196`
- **O que e:** Hu 2020 (CFRP + Hi-Lok Ti, 23C, 1000 h): relaxacao viscoelastica vs interferencia do furo (0-1.5%) — interferencia CONSTRANGE o fluxo e melhora retencao
- **Unidades/colunas:** tempo em horas; ratios adimensionais; colunas por interferencia em % do diametro
- **Qualidade:** measured | **Pontos:** 5

### hu2020_temperature_1p0fit.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/63_64_65_66_thermal_interaction_CFRP_cycling.md:197-208`
- **O que e:** Hu 2020 (CFRP, interferencia 1.0%): relaxacao vs temperatura (23-177C) — perto do Tg (177C) perde 41% em 1000 h
- **Unidades/colunas:** tempo em horas; ratios adimensionais
- **Qualidade:** measured | **Pontos:** 5
- **Nota:** Params Prony do .md (T800S/3900-2, 23C) nao copiados (fit): E1/E0=0.030 tau=0.5h; 0.025/10h; 0.020/200h; 0.015/5000h; Einf/E0=0.910.

### liu2017mos2_coating.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/67_68_69_70_MoS2_complex_random_neutron.md:23-36`
- **O que e:** Liu 2017 (excitacao AXIAL 10 kN, F0=20 kN, M10 8.8): comparacao de revestimentos ate 200k ciclos — MoS2 retem 0.80 vs aco nu 0.48
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 7

### liu2017mos2_ranking_200k.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/67_68_69_70_MoS2_complex_random_neutron.md:37-44`
- **O que e:** Liu 2017: ranking a 200k ciclos com razao torque de soltura/aperto por revestimento
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 4

### liu2017mos2_amplitude.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/67_68_69_70_MoS2_complex_random_neutron.md:47-58`
- **O que e:** Liu 2017 (MoS2): efeito da amplitude axial 5-12.5 kN — a 12.5 kN (F_ax/F0=0.625) ha separacao parcial e 34% de perda
- **Unidades/colunas:** ratios adimensionais; colunas por amplitude axial em kN
- **Qualidade:** measured | **Pontos:** 5

### liu2017mos2_torque.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/67_68_69_70_MoS2_complex_random_neutron.md:61-69`
- **O que e:** Liu 2017: torque de aperto necessario p/ F0=20 kN e K-factor por revestimento — MoS2 reduz torque em ~40%
- **Unidades/colunas:** T em N.m; K adimensional; reducao em % vs aco nu
- **Qualidade:** measured | **Pontos:** 4

### liu2017mos2_wear.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/67_68_69_70_MoS2_complex_random_neutron.md:70-79`
- **O que e:** Liu 2017 (SEM/EDX apos 200k ciclos): profundidade de desgaste da rosca e integridade do revestimento
- **Unidades/colunas:** wear em micrometros; integridade em % (vazio = N/A p/ aco nu)
- **Qualidade:** measured | **Pontos:** 4

### baek2019_typeA.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/67_68_69_70_MoS2_complex_random_neutron.md:109-120`
- **O que e:** Baek 2019 (bracket simples 2 parafusos M8, base excitation): decaimento por nivel de aceleracao 5-20g
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 5

### baek2019_typeC.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/67_68_69_70_MoS2_complex_random_neutron.md:121-132`
- **O que e:** Baek 2019 (multi-bracket 6 parafusos, parafuso do topo = mais longe da excitacao): decaimento por nivel 5-20g
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 5

### baek2019_forces.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/67_68_69_70_MoS2_complex_random_neutron.md:133-144`
- **O que e:** Baek 2019: forca de afrouxamento primaria vs secundaria por posicao — p/ parafusos longe da fonte, a forca SECUNDARIA (propagada pela estrutura) domina
- **Unidades/colunas:** forcas em kN; ratio = primaria/secundaria
- **Qualidade:** measured | **Pontos:** 5

### scirep2025_rand_DN.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/67_68_69_70_MoS2_complex_random_neutron.md:169-188`
- **O que e:** Sci.Rep. 2025 (M16x120 8.8, F0=60 kN, random EN 61373): curva D-N com amplitude EQUIVALENTE (delta_eq) — vida ate 20% de perda
- **Unidades/colunas:** delta_eq em mm; N_L em ciclos; flag gt = '>'
- **Qualidade:** measured | **Pontos:** 8
- **Nota:** Mesma familia M16/60kN do liu2025_scirep (apparatus_notes) — provavelmente o mesmo grupo/paper; criterios diferentes (20% loss vs fratura). Regressao: log10(NL)=2.18-7.85*log10(delta_eq), R2=0.993.

### scirep2025_rand_SuN.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/67_68_69_70_MoS2_complex_random_neutron.md:190-201`
- **O que e:** Sci.Rep. 2025: curva Su-N (tensao normalizada na raiz do 1o filete = sigma_bending/sigma_preload vs vida)
- **Unidades/colunas:** Su adimensional; N_L em ciclos; flag gt = '>'
- **Qualidade:** measured | **Pontos:** 7

### scirep2025_rand_decay.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/67_68_69_70_MoS2_complex_random_neutron.md:202-218`
- **O que e:** Sci.Rep. 2025: decaimento sob vibracao randomica RMS 15 m/s2 por 12 h
- **Unidades/colunas:** tempo em horas; ratio adimensional
- **Qualidade:** measured | **Pontos:** 9
- **Nota:** Fit duplo-exponencial do .md: a1=0.12 b1=2.5/h a2=0.15 b2=0.15/h c=0.73.

### chen2023_IN718_neutron.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/67_68_69_70_MoS2_complex_random_neutron.md:244-260`
- **O que e:** Chen 2023 (difracao de neutrons in-situ, ENGIN-X): relaxacao macroscopica IN718 a 718C, sigma0~500 MPa, 20 h
- **Unidades/colunas:** tempo em horas; sigma/sigma0 adimensional
- **Qualidade:** measured | **Pontos:** 10
- **Nota:** Strains de rede por plano cristalografico (Dataset 2 do .md) nao extraidos — fora do escopo do BAS.

### wiegand2021_bolt_force_vs_load.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/71_Wiegand_2021_VDI_validation_index.md:29-46`
- **O que e:** Wiegand 2021: forca no parafuso vs carga de trabalho axial (F0=50 kN, flange metal-metal) — MEDIDO vs VDI 2230 vs EN 1591-1 vs FEM; VDI superprediz em cargas baixas
- **Unidades/colunas:** forcas em kN
- **Qualidade:** measured+model | **Pontos:** 11

### wiegand2021_load_introduction.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/71_Wiegand_2021_VDI_validation_index.md:47-57`
- **O que e:** Wiegand 2021: fator de introducao de carga n = dF_bolt/dF_W por faixa — MEDIDO varia 0.15->0.63 (VDI assume 0.30 constante)
- **Unidades/colunas:** faixa de F_W em kN; n adimensional
- **Qualidade:** measured+model | **Pontos:** 5
- **Nota:** Validacao direta do Phi_load VDI 2230 usado no BAS.

### wiegand2021_clamp_separation.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/71_Wiegand_2021_VDI_validation_index.md:59-70`
- **O que e:** Wiegand 2021: carga de separacao do clamp medida vs prevista por VDI (VDI superestima 4-14%, conservador)
- **Unidades/colunas:** forcas em kN; erro em %
- **Qualidade:** measured+model | **Pontos:** 5

### wiegand2021_eccentric_forces.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/71_Wiegand_2021_VDI_validation_index.md:71-81`
- **O que e:** Wiegand 2021: distribuicao de forca no grupo de 4 parafusos sob carga excentrica F_W=30 kN — VDI superprediz lado tracionado em 6-9%
- **Unidades/colunas:** forcas em kN
- **Qualidade:** measured+model | **Pontos:** 4

### liucai2016_axial_coating.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/72_Liu_Cai_2016_2017_axial_dynamic.md:71-86`
- **O que e:** Liu/Cai (axial 2.0 kN, F0=20 kN): efeito de revestimento bare vs MoS2 vs Cr2O3 — MoS2 reduz fretting Estagio II em ~40%
- **Unidades/colunas:** ratios adimensionais; digitalizada da Fig 8
- **Qualidade:** measured | **Pontos:** 7

### liucai2016_axial_preload.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/72_Liu_Cai_2016_2017_axial_dynamic.md:87-100`
- **O que e:** Liu/Cai (axial 2.0 kN, aco nu): efeito do preload 10-25 kN — maior F0 reduz a fracao de perda do Estagio I
- **Unidades/colunas:** ratios adimensionais; digitalizada da Fig 7
- **Qualidade:** measured | **Pontos:** 5

### liu2018_torsional_preload.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/74_76_77_78_torsional_loosening_Liu_group.md:74-85`
- **O que e:** Liu 2018 (excitacao TORSIONAL, M12 8.8, amplitude 2.0 graus, 1 Hz, seco): efeito do preload 10/20/30 kN
- **Unidades/colunas:** ratios adimensionais; digitalizada da Fig 8
- **Qualidade:** measured | **Pontos:** 5

### liu2018_torsional_freq.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/74_76_77_78_torsional_loosening_Liu_group.md:86-99`
- **O que e:** Liu 2018 (torsional, F0=20 kN, 2.0 graus): frequencia 0.5/1/2 Hz — efeito desprezivel (consistente com transversal)
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 5

### liu2022tors_wear_coupling.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/74_76_77_78_torsional_loosening_Liu_group.md:150-166`
- **O que e:** Liu 2022 (torsional longa duracao, F0=20 kN, 2.0 graus, 1 Hz): medido vs modelo mu-constante vs modelo acoplado a desgaste — mu-constante diverge apos ~1000 ciclos
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured+model | **Pontos:** 6

### liu2022tors_wear_mu.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/74_76_77_78_torsional_loosening_Liu_group.md:167-175`
- **O que e:** Liu 2022: profundidade de desgaste acumulada E mu_thread MEDIDO vs ciclos — acoplamento desgaste->atrito->afrouxamento (mu cai 0.180->0.103)
- **Unidades/colunas:** wear em micrometros; mu adimensional
- **Qualidade:** measured | **Pontos:** 5
- **Nota:** Anchor duplo p/ K_archard + acoplamento damage->mu (k_dmg_mu).

### yang2021R_xi_critical.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/79_Yang_2021_composite_excitation_Rfactor.md:29-43`
- **O que e:** Yang 2021 (R-factor): razao critica xi = delta/F_axial que separa afrouxamento de fadiga, em funcao de R_axial — R=-1 (reverso) e o mais suscetivel
- **Unidades/colunas:** xi em mm/kN; digitalizada da Fig 6
- **Qualidade:** measured | **Pontos:** 5
- **Nota:** Fit do .md: xi_cr(R) ~= 0.075*(1+0.47*R).

### yang2021R_decay_by_R.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/79_Yang_2021_composite_excitation_Rfactor.md:45-58`
- **O que e:** Yang 2021: decaimento por R_axial (F0=70% proof, xi=0.10 mm/kN) — R=-1 afrouxa >3x mais rapido que R=0.5
- **Unidades/colunas:** ratios adimensionais; digitalizada da Fig 8
- **Qualidade:** measured | **Pontos:** 6

### yang2021R_N50_map.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/79_Yang_2021_composite_excitation_Rfactor.md:60-69`
- **O que e:** Yang 2021: ciclos ate 50% de perda por R_axial e nivel de preload (dados de contorno da Fig 10)
- **Unidades/colunas:** preload em % proof; N50 em ciclos
- **Qualidade:** measured | **Pontos:** 3

### du2022_random_strain.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/80_Du_2022_random_vibration_3stage.md:33-70`
- **O que e:** Du 2022 (M8, random): amplitude de strain normalizada (indicador SHM dos 3 estagios) + F/F0 estimado, por nivel de PSD — formato longo
- **Unidades/colunas:** PSD em g2/Hz; strain normalizado (atual/inicial); ratio_est = F/F0 estimado no .md (vazio p/ PSD 0.10)
- **Qualidade:** measured | **Pontos:** 18
- **Nota:** Criterio SHM do .md: <1.10 estavel; 1.10-1.50 transicao; >=1.50 loosen.

### du2022_random_time_to_loosen.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/80_Du_2022_random_vibration_3stage.md:71-80`
- **O que e:** Du 2022: ciclos/tempo ate entrar no estagio Loosen vs torque de aperto (PSD=0.20 g2/Hz)
- **Unidades/colunas:** T em N.m; F0 em kN; ciclos e tempo (~ no .md; tempo a 100 Hz dominante)
- **Qualidade:** measured | **Pontos:** 3

### du2022_random_threshold_psd.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/80_Du_2022_random_vibration_3stage.md:81-88`
- **O que e:** Du 2022: PSD limiar abaixo do qual so ocorre o estagio Steady, por torque de aperto
- **Unidades/colunas:** T em N.m; PSD em g2/Hz
- **Qualidade:** measured | **Pontos:** 3

### ishimura2010_bending_decay.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/81_82_bending_loosening.md:26-46`
- **O que e:** Ishimura/Sawa 2010: decaimento sob momento fletor ciclico em flange — 3 niveis M/M_slip (0.5/0.8/1.2); mecanismo distinto do Junker (tilt da cabeca)
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** representative | **Pontos:** 7
- **Nota:** O .md marca REPRESENTATIVE (tendencias do paper + FEM; curvas exatas exigem o paper) — nao usar como dado duro.

### yokoyama2012_rotary_bending.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/81_82_bending_loosening.md:75-92`
- **O que e:** Yokoyama 2012: rotacao da porca e F/F0 sob flexao rotativa (disco-eixo, M10 8.8) — mecanismo spring-back torsional via helice
- **Unidades/colunas:** theta em graus; ratio estimado
- **Qualidade:** representative | **Pontos:** 7
- **Nota:** REPRESENTATIVE no .md. Refeita com as 2 colunas — versao em extracted_csv perdeu a coluna theta.

### yokoyama2012_rotary_vs_junker.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/81_82_bending_loosening.md:93-102`
- **O que e:** Yokoyama 2012: flexao rotativa vs Junker transversal com a MESMA amplitude de forca lateral — rotativa afrouxa bem mais rapido
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** representative | **Pontos:** 5

### bouzid1995_swsg_ambient.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/85_86_Bouzid_1995_2006_gasket_creep.md:29-46`
- **O que e:** Bouzid 1995 (ultrassonico): relaxacao do bolt load com gaxeta spiral-wound (SWSG) a temperatura ambiente, 168 h — perda ~17%
- **Unidades/colunas:** tempo em horas; ratio adimensional
- **Qualidade:** measured | **Pontos:** 10
- **Nota:** Fit log do .md: F/F0 = 1 - 0.060*ln(1+t/0.1h).

### bouzid1995_graphite_ambient.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/85_86_Bouzid_1995_2006_gasket_creep.md:48-61`
- **O que e:** Bouzid 1995: relaxacao com gaxeta de grafite flexivel a ambiente — ~21% em 168 h (mais compliance de creep que SWSG)
- **Unidades/colunas:** tempo em horas; ratio adimensional
- **Qualidade:** measured | **Pontos:** 6

### bouzid1995_swsg_temperature.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/85_86_Bouzid_1995_2006_gasket_creep.md:63-75`
- **O que e:** Bouzid 1995: efeito da temperatura na perda com SWSG (24 h e 168 h) — cada +50C ~dobra a taxa de creep
- **Unidades/colunas:** T em C; ratios adimensionais
- **Qualidade:** measured | **Pontos:** 4

### bouzid1995_thermal_cycles.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/85_86_Bouzid_1995_2006_gasket_creep.md:76-88`
- **O que e:** Bouzid 1995: ciclos termicos startup/shutdown (ambiente<->200C): F/F0 no pico e apos resfriar — ratchet de creep por ciclo
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 4
- **Nota:** Refeita com as 2 colunas — a versao em extracted_csv (Dataset_4) e 2-colunas com semantica ambigua.

### bouzid2006_8bolt_interaction.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/85_86_Bouzid_1995_2006_gasket_creep.md:116-128`
- **O que e:** Bouzid & Nechache 2006: interacao elastica no flange de 8 parafusos (padrao estrela sequencial) — bolt 1 perde ~10% so por interacao; 3 passes reduzem scatter
- **Unidades/colunas:** valores = fracao do preload alvo (vazio = parafuso ainda nao apertado)
- **Qualidade:** measured | **Pontos:** 5

### bouzid2006_interaction_creep.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/85_86_Bouzid_1995_2006_gasket_creep.md:130-142`
- **O que e:** Bouzid & Nechache 2006: interacao elastica + creep combinados (8 parafusos, gaxeta aramida 3 mm) — creep 24h tira mais 30% mesmo apos 3 passes
- **Unidades/colunas:** mean = fracao do alvo; scatter = +/- fracao
- **Qualidade:** measured | **Pontos:** 4

### bouzid2006_gasket_comparison.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/85_86_Bouzid_1995_2006_gasket_creep.md:143-153`
- **O que e:** Bouzid & Nechache 2006: comparacao de materiais de gaxeta — bolt load apos 24 h e 168 h (single-pass, ambiente)
- **Unidades/colunas:** espessura em mm; ratios adimensionais
- **Qualidade:** measured | **Pontos:** 4

### bouzid2006_norton_bailey.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/85_86_Bouzid_1995_2006_gasket_creep.md:154-163`
- **O que e:** Parametros Norton-Bailey fitados pelo grupo Bouzid (epsilon_creep = C1*sigma^n*t^m) por gaxeta — proveniencia p/ NortonBaileyCreepModel do BAS
- **Unidades/colunas:** C1 em unidades do fit do paper; n e m adimensionais
- **Qualidade:** representative | **Pontos:** 4
- **Nota:** Constantes fitadas (nao curva medida) — quality=representative.

### liumi2021_failure_mode_map.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/87_Liu_Mi_2021_competitive_failure_Rfactor.md:29-43`
- **O que e:** Liu & Mi 2021: mapa de modo de falha (afrouxamento vs fadiga) por R e nivel de preload — fronteira R_critical ~0.55 na amplitude media
- **Unidades/colunas:** celulas = modo dominante (texto); preload em % proof
- **Qualidade:** measured | **Pontos:** 5
- **Nota:** Derivada da fronteira da Fig 8 (APPROXIMATE no .md). Base do warning R_factor>0.5 do BAS.

### liumi2021_decay_by_R.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/87_Liu_Mi_2021_competitive_failure_Rfactor.md:45-58`
- **O que e:** Liu & Mi 2021: decaimento por R (50% proof, amplitude media) — R=0.7 retem >95% (fadiga domina antes de afrouxar)
- **Unidades/colunas:** ratios adimensionais; digitalizada da Fig 10
- **Qualidade:** measured | **Pontos:** 6

### liumi2021_N_vs_amplitude.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/87_Liu_Mi_2021_competitive_failure_Rfactor.md:60-77`
- **O que e:** Liu & Mi 2021: vida por amplitude transversal (niveis low/medium/high do paper) — N50 p/ afrouxamento (R=0.1) vs N de iniciacao de trinca (R=0.9)
- **Unidades/colunas:** N em ciclos; flag gt = '>100000'
- **Qualidade:** measured | **Pontos:** 3

### abid2014_pressure_cycles.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/88_Abid_Nash_2014_dynamic_gasket_flange.md:27-43`
- **O que e:** Abid & Nash 2014 (flange NPS4 cl.300 gaxetado, pressao interna harmonica 5 Hz a 100% design): bolt load e tensao da gaxeta vs ciclos de pressao — drift ~3%/100 ciclos
- **Unidades/colunas:** ratios adimensionais; digitalizada da Fig 6
- **Qualidade:** measured | **Pontos:** 6

### abid2014_freq_effect.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/88_Abid_Nash_2014_dynamic_gasket_flange.md:44-56`
- **O que e:** Abid & Nash 2014: efeito da frequencia (1-10 Hz, 300 ciclos) — maior freq = maior oscilacao dinamica do bolt load e mais drift
- **Unidades/colunas:** f em Hz; ratio adimensional; dF_osc = amplitude de oscilacao +/-dF/F0
- **Qualidade:** measured | **Pontos:** 4
- **Nota:** Refeita com a coluna de oscilacao — a versao em extracted_csv so tem o ratio.

### abid2014_harmonic_vs_step.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/88_Abid_Nash_2014_dynamic_gasket_flange.md:57-70`
- **O que e:** Abid & Nash 2014: pressao harmonica vs transiente step (mesmo pico) — harmonica perde ~2.5x mais (ratchet de micro-creep da gaxeta)
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 5

### abid2014_gasket_stress_radial.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/88_Abid_Nash_2014_dynamic_gasket_flange.md:71-82`
- **O que e:** Abid & Nash 2014 (filme de pressao): distribuicao radial da tensao da gaxeta antes/apos 500 ciclos — raio interno relaxa mais rapido (risco de vazamento)
- **Unidades/colunas:** tensoes em MPa; change em %
- **Qualidade:** measured | **Pontos:** 3

### bhattacharya2010_small_M4M5M6.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/89_Bhattacharya_2010_small_bolts_M4_M5.md:30-46`
- **O que e:** Bhattacharya 2010 (parafusos pequenos): M4/M5/M6 a 70% proof, mesma amplitude proporcional delta/d~0.03 — vida escala ~d^1.8
- **Unidades/colunas:** ratios adimensionais; digitalizada das Figs 3-5
- **Qualidade:** measured | **Pontos:** 7

### bhattacharya2010_small_M5_washers.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/89_Bhattacharya_2010_small_bolts_M4_M5.md:48-66`
- **O que e:** Bhattacharya 2010: M5 70% proof — sem arruela vs plana vs pressao; arruela plana e inutil, pressao da ~30% de vida extra
- **Unidades/colunas:** ratios adimensionais; digitalizada da Fig 7
- **Qualidade:** measured | **Pontos:** 7

### bhattacharya2010_delta_critical.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/89_Bhattacharya_2010_small_bolts_M4_M5.md:67-83`
- **O que e:** Bhattacharya 2010: amplitude critica de deslocamento (abaixo da qual NAO afrouxa) por tamanho M4-M12, sem arruela vs c/ pressao — lei delta_cr ~ 0.0095*d^0.82
- **Unidades/colunas:** deltas em mm; M8-M12 = referencia do .md
- **Qualidade:** measured | **Pontos:** 6
- **Nota:** Anchor p/ slip_onset (limiar de amplitude) e escala com d.

### wei2025_cfrp_vs_steel.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/90_91_CFRP_loosening_Wei_Yang.md:52-64`
- **O que e:** Wei 2025: CFRP vs aco sob flexao vibratoria (mesmo parafuso/amplitude, sem rotacao da porca) — CFRP perde muito mais no Estagio I (embedding 18% vs 5-10%)
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** representative | **Pontos:** 6
- **Nota:** REPRESENTATIVE no .md (baseada nos valores 18%+5% reportados). Curva CFRP isolada ja em extracted_csv (90_91__Preload_Decay__1.csv).

### yang2023cfrp_decomposition.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/90_91_CFRP_loosening_Wei_Yang.md:92-106`
- **O que e:** Yang 2023 (CFRP sem rotacao, Table 2 do paper): decomposicao da perda por mecanismo x material da arruela — embedding domina (45-71%), rotacao so 2-5%
- **Unidades/colunas:** valores em % da perda total
- **Qualidade:** measured | **Pontos:** 4
- **Nota:** Equivalente experimental da decomposicao por mecanismo do V2 (dF_0_by_mech) p/ CFRP.

### yang2023cfrp_biaxial.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/90_91_CFRP_loosening_Wei_Yang.md:107-122`
- **O que e:** Yang 2023 (CFRP, arruela de aco, F0=15 kN): transversal vs axial vs COMBINADO — combinado perde ~15% mais que transversal (compliance fora-do-plano)
- **Unidades/colunas:** ratios adimensionais; digitalizada da Fig 5
- **Qualidade:** measured | **Pontos:** 7

### yang2023cfrp_washers.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/90_91_CFRP_loosening_Wei_Yang.md:123-132`
- **O que e:** Yang 2023 (CFRP): efeito do material da arruela — arruela CFRP (modulo casado) melhora ~7%; aluminio piora
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured | **Pontos:** 3
- **Nota:** Refeita limpa da versao _needs_review.

### suye2016_cfrp_temp.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/92_Su_Ye_2016_CFRP_viscoelastic.md:76-88`
- **O que e:** Su & Ye 2016 (CFRP viscoelastico, F0=50% proof): efeito da temperatura na relaxacao — taxa ~dobra a cada 18-22C sub-Tg
- **Unidades/colunas:** T em C; ratios adimensionais
- **Qualidade:** measured | **Pontos:** 4
- **Nota:** Refeita limpa da versao _needs_review.

### suye2016_creep_fit_params.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/92_Su_Ye_2016_CFRP_viscoelastic.md:89-101`
- **O que e:** Su & Ye 2016 (Table 3 do paper): parametros do fit logaritmico dF/F0 = A*ln(1+t/tau) por temperatura — proveniencia p/ C_r CFRP no BAS
- **Unidades/colunas:** A adimensional; tau em ciclos
- **Qualidade:** representative | **Pontos:** 4
- **Nota:** Parametros fitados do paper (nao curva) — quality=representative.

### huzhang2020_thermal_cycles.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/93_Hu_Zhang_2020_CFRP_thermal_preload.md:29-47`
- **O que e:** Hu & Zhang 2020 (CFRP, ciclo termico 25<->100C, sem carga mecanica): perda por ciclo — rapida nos 3 primeiros (acomodacao CTE) depois assintotica
- **Unidades/colunas:** ratio adimensional; loss em %/ciclo
- **Qualidade:** measured | **Pontos:** 8

### huzhang2020_deltaT_scaling.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/93_Hu_Zhang_2020_CFRP_thermal_preload.md:48-59`
- **O que e:** Hu & Zhang 2020: efeito da faixa de temperatura (50 ciclos termicos) — perda escala ~dT^1.8
- **Unidades/colunas:** dT em C; ratio adimensional
- **Qualidade:** measured | **Pontos:** 3
- **Nota:** Refeita limpa da versao _needs_review.

### huzhang2020_thermal_mech.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/93_Hu_Zhang_2020_CFRP_thermal_preload.md:60-74`
- **O que e:** Hu & Zhang 2020: termico + mecanico combinado e SUPER-ADITIVO (~40% mais que a soma) — tracao mecanica descarrega a interface durante o aquecimento
- **Unidades/colunas:** ratios adimensionais; dT=75C, 50% axial
- **Qualidade:** measured | **Pontos:** 6

### schaumann2009_SN_M36.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/96_Schaumann_2009_2015_large_bolt_VDI.md:31-44`
- **O que e:** Schaumann & Marten 2009: S-N M36 10.9 R=0.1 — vida experimental vs prevista por VDI 2230 (VDI nao-conservador p/ parafusos grandes)
- **Unidades/colunas:** sigma_a em MPa; vidas em ciclos
- **Qualidade:** measured+model | **Pontos:** 3
- **Nota:** Linha de run-out do .md (80 MPa, 2e6 ciclos; limites de fadiga VDI 75 vs exp 63 MPa, razao 1.19) nao cabe no esquema — registrada aqui. Refeita da versao _needs_review.

### schaumann2009_size_effect.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/96_Schaumann_2009_2015_large_bolt_VDI.md:46-61`
- **O que e:** Schaumann 2009: limite de fadiga vs diametro (M12-M42) experimental vs VDI 2230 — sobre-estimativa do VDI cresce com o diametro (3%->26%)
- **Unidades/colunas:** tensoes em MPa; overestimate em %; M42 = extrapolado
- **Qualidade:** measured+model | **Pontos:** 7

### schaumann2015_fatigue_limits.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/96_Schaumann_2009_2015_large_bolt_VDI.md:77-89`
- **O que e:** Schaumann 2015 (M36/M64 offshore): limite de fadiga a 2e6 ciclos — nu vs zincado, experimental vs VDI (zincado M64: VDI superestima 50%)
- **Unidades/colunas:** tensoes em MPa; overestimate em %
- **Qualidade:** measured+model | **Pontos:** 4

### schaumann2015_zinc_penalty.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/96_Schaumann_2009_2015_large_bolt_VDI.md:90-102`
- **O que e:** Schaumann 2015: penalidade do revestimento de zinco no limite de fadiga por diametro (~-10 a -13%, nao coberto pelo VDI)
- **Unidades/colunas:** tensoes em MPa; penalty em %
- **Qualidade:** measured | **Pontos:** 4

### nassar2009_model_vs_exp.csv
- **Fonte:** `Models/CALIBRATION_AND_VALIDATION/05_Nassar_Yang_2009_math_model.md:106-131`
- **O que e:** Nassar & Yang 2009: curva medida vs modelo analitico nao-linear (5/16"-24 UNF, F0=11120 N, 0.71 mm, 7 Hz) — modelo dentro de 5-10%
- **Unidades/colunas:** ratios adimensionais
- **Qualidade:** measured+model | **Pontos:** 7
- **Nota:** Refeita com as 2 colunas — versao em extracted_csv so tem uma. Tabelas parametricas do modelo (preload/amplitude/atrito) NAO extraidas (previsao pura).



### rousseau2025_steel_t10_rotation_deg.csv · rousseau2025_steel_t12_rotation_deg.csv
- **Fonte:** Fig. 5 (eixo secundario, "bolt-nut relative rotation") do Rousseau & Bouzid 2025 — digitalizados 2026-08-19 da extracao vetorial `BAS_V2_papers/E. Rodada 4 (deep-research 2026-07-11)/vector_extractions/rousseau2025_fig4_fig5_vector.json`
- **O que e:** rotacao RELATIVA parafuso-porca vs ciclo, aco t=10/t=12 mm (M12, F0=10,25 kN, 0,05 mm)
- **Calibracao:** y do JSON em unidades do eixo esquerdo (0,9867 N/unit, lido da polilinha de pre-carga vs CSV canonico); conversao pela equivalencia dos eixos (12000 N-span = 14 deg-span). Validacao: theta_fim t10 10,92 vs 10,97 da leitura manual (sec4.27 MODEL_LEGITIMACY); t12 4,36 vs 4,23.
- **Unidades/colunas:** cycle; rotation_deg
- **Qualidade:** digitized-vector | **Pontos:** 183 cada
- **Uso:** leituras da adocao `per_case.steel_t10` (preregs 2026-08-19-rousseau-t10-{ratchet-lido,taxa-regredida}): dF/dtheta = 919,7/893,6 N/deg (r2 0,9997/0,9969) => free_spin_kin; a taxa observada => k/W_onset/sharpness/floor/aexp (LSQ r2=0,891).
- ⚠️ **ERRATA (mesma noite):** a extracao vetorial e' VALIDA na fig5 e CORROMPIDA na fig4 (polilinhas truncadas — rot t12 dava 23,2 vs ~12,5 impresso). Os tracos do HDPE foram RE-EXTRAIDOS direto do PDF (atributo dashes + ticks absolutos): theta_fim 21,27/12,65/2,16 deg; dF/dtheta 138/207 N/deg (VARIA com espessura — a lei-de-junta so vale no aco). Ver rousseau_t10_ratchet_lido_resultado.md sec8.


### rousseau2025_hdpe_t{10,12,14}_rotation_deg.csv
- **Fonte:** Fig. 4 (eixo secundario) do Rousseau & Bouzid 2025 — RE-EXTRAIDOS 2026-08-19 (noite) DIRETO do PDF (o vector JSON da Rodada 4 esta CORROMPIDO para a fig4; ver errata em rousseau_t10_ratchet_lido_resultado.md sec8)
- **O que e:** rotacao RELATIVA parafuso-porca vs ciclo, HDPE t=10/12/14 mm (M12, F0=4 kN)
- **Calibracao:** ABSOLUTA pelos ticks de texto da pagina (0 deg @ y=209.75; 3.66 pt/deg; 0.455 pt/ciclo); rotacao separada da pre-carga pelo ATRIBUTO dashes do path. Validacao: theta_fim 21.27/12.65/2.16 deg vs impresso ~21/~12.5/~2; zeros 0.10/0.00/0.04.
- **Unidades/colunas:** cycle; rotation_deg
- **Qualidade:** digitized-pdf-ticks | **Pontos:** ~400 cada
- **Uso:** rota de leitura das 2 abertas do HDPE (dF/dtheta 138/207 N/deg — POR CURVA no HDPE; fsk lido por curva). Prereg proprio quando atacadas.


### zhang2006_fig3_theta_trace.csv
- **Fonte:** Fig. 3 do Zhang/Jiang/Lee 2006 (JPVT 128(3), DOI 10.1115/1.2217972) — os DOIS tracos (P e theta) digitalizados 2026-08-20 do raster embutido (xref 11, 995x541 px) por column-wise bright-run tracing com TRACKING por continuidade (script versionado: New_Theory/digitize_zhang_fig3_theta.py)
- **O que e:** pre-carga P/P0 E rotacao porca-parafuso theta vs ciclo, do rig ANTERIOR dos autores (M12x1.25, 75 mm, zinc, P0=20 kN, delta/2=0,35 mm) — a figura e rotulada "Illustration of self-loosening process" (curva DECLARADA por proveniencia no censo; este trace e ANCORA DE LEITURA, nao curva de validacao)
- **Calibracao:** x LOG 10^0@px135..10^4@px905 (192,5 px/dec); y 0%@py411..100%@py13. Demarcacao Stage I/II desenhada @px560 => N_onset=161. ESCALA de theta: a figura NAO rotula o eixo theta; ancora unica = theta(demarcacao)=0,5 deg (texto do paper) => 1% do eixo P = 0,568 deg, INCERTEZA ~±30% (2 px). A coluna theta_pct_eixoP fica em % do eixo P (escala-neutra); o fe da lei de taxa INDEPENDE da escala.
- **Unidades/colunas:** N; P_frac; theta_pct_eixoP
- **Qualidade:** digitized-raster-tracking | **Pontos:** 826 (P) / 827 (theta)
- **Validacao:** P bate a CSV canonica da fig3 nas ancoras (N=1: 99,9%; N=158: 88,7%; N=1e4: 32,4%)
- **Uso (leituras, estudo zhang2006_fig3_estudo_do_caso.md §9):** dF/dtheta = 698 N/deg (r2=0,982, trecho 300-3000 — classe ROUSSEAU aco §4.56); LEI DE TAXA dtheta/dN ~ F^fe com fe=5,80 (r2=0,74), CONCORDANTE com a regressao independente do P puro (5,93, r2=0,99); onset N=161. NAO fecha o tripe: o DISPARO final (theta 10->42 deg) e um 2o regime (runaway de porca solta) que a lei F^fe nao cobre — forma faltante "transicao lei-de-potencia->runaway" comprovada com constantes lidas.
