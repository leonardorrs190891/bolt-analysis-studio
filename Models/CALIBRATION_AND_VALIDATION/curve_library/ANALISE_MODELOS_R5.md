# Análise de modelos — Rodada 5 vs limitações do BAS V2 (2026-07-16)

Síntese das 33 notas de `BAS_V2_papers/F. Rodada 5.../apparatus_notes/` (36 PDFs, 336 CSVs,
~5.026 pontos) contra as limitações declaradas em `concept_coverage.html`. Para cada limitação:
o que a literatura entrega (forma/constante, com valores), **o que o engine faz hoje de
diferente**, e o veredito. Alimenta o plano de implementação
`docs/superpowers/plans/2026-07-16-limitacoes-L1-L7-implementacao.md`.

Convenção de proveniência (MEM/§4.26): **medido** (valor experimental do par certo) >
**derivado** (calculado de dados do paper) > **forma** (lei transfere, constante não) >
**contexto** (não transfere).

---

## L2 — Rigidez de membro (grip→L_eff→k_b / k_j fixo) — **FECHÁVEL AGORA**

**O que o engine faz hoje:** `k_j` fixo (`k_j_init`) + mapeamento grip→L_eff→k_b que NÃO escala
com espessura (falsificado na varredura Rousseau t10/12/14, §4.8: sobre-predição crescente,
`final_pred−final_data` −0,31/−0,51).

**O que a literatura entrega (7 fontes independentes, hierarquia clara):**

| Fonte | Tipo | Entrega |
|---|---|---|
| **Pedersen 2008** (14 CSVs) | FE+energia, M10 E M20 | **Forma primária**: assíntota `k_m = E·d·[0,59(β²−α²)·d/L + 0,20(β+α)]` (Eq.31) + transição de largura finita (Eqs.33–37, saturação exponencial em `d_a`). β,α = razões arruela/furo. |
| **Rousseau 2024** (17 CSVs) | método (energia, k_bolt separado) | Ranqueia as formas: **Pedersen é a mais próxima da verdade (+24%)**; Wileman +45–59%; critica FE por deslocamento de nó arbitrário. Mesmo grupo do Rousseau 2025 in-library. |
| **Wileman 1991** (6 CSVs) | FE canônico | Cross-check: `k_m/(E·d)=A·e^(B·d/L)` com A,B por material (aço 0,78715/0,62873; Al 0,79670/0,63816; Cu; FoFo). SUPERESTIMA em d/L alto; desvio 6–7% do próprio FE nos extremos. |
| **Haidar 2011** (9 CSVs) | analítico | 3ª forma de referência (cone/energia) p/ triangulação. |
| **Grosse 1990** (6 CSVs, tese 171p) | FE não-linear (contato/separação) | **Dependência de CARGA**: rigidez da junta colapsa **~50×** da pré-carga plena→separação; teoria linear sobre-prediz carga adicional do parafuso **~10×** a 25% de F0. Forma barata: elíptica `F_m/F_i = 1−√(2λ−λ²)` (1 parâmetro por junta: deformação crítica de separação). |
| **An/EngStruct 2019** (13 CSVs) | **experimento** (30 ensaios até fratura) | Única MEDIÇÃO: k_j não-monotônico com a carga; K1 ≈ **~30% do EA/l teórico**; modelo trilinear validado. Caveat: splice de 10–14 parafusos — transfere o paradigma e a razão ~30%, não os valores. |
| **Murai/IJAMT 2023** (18 CSVs) | experimento M8 | **Área de contato da arruela domina** k1 (2,1× de 42→478 mm²); pré-carga fraca (+14%); **k_j estável após o 1º ciclo** (sustenta k_j-constante-por-ciclo); Ra ambíguo. |

**Veredito: FECHA.** Ação no engine: lei `k_j(d, L, material, arruela)` com Pedersen-primária e
Wileman como modo alternativo (ambos default-inertes; o k_j atual permanece o default);
dependência de carga opt-in via forma elíptica de Grosse (afeta Φ). Gate: os 3 casos Rousseau
steel (o expositor do gap) + Zhang2006 clamped-length + sem regressão global (180 casos).
JMST 2025 (stub de 1 pág.) descartado — substituído por Grosse 1990.

---

## L3 — Acoplamento F_amp↔δ (F_amp ≤ µ·F0 em disp-mode) — **FECHÁVEL AGORA**

**O que o engine faz hoje:** F_amp e δ_amp independentes em disp-mode (roadmap #4); µ constante.

**O que a literatura entrega (6 fontes):**

- **Li 2020** (27 CSVs): rig piezo disp-controlado; laços força tangencial–deslocamento + k_tr
  medido; força+pré-carga simultâneas.
- **Li 2022** (14 CSVs): mapeia stick/partial/**gross-slip** vs nível de vibração; laços + Iwan
  discretizado + contato fractal (pressão não-uniforme).
- **Li 2021** (25 CSVs): lei de **softening** da rigidez tangencial (zona de stick contraindo);
  ligada à distribuição 2D de pressão de apoio.
- **JMP/Li & Hao 2021** (12 CSVs): a força de gross-slip **NÃO é µ·F0 constante** — pico FS e
  decaimento exponencial com deslocamento até residual FR = 70–86% do pico (dirigido por
  achatamento/desgaste); backbone Iwan 5-param em forma fechada (Eq.15 + Tabela 3 exatas).
- **Measurement 2021** (8 CSVs): dois limiares medidos ∝ pré-carga — `Fa=0,199·F0−5,3 kN`
  (slip local) e `Fb=0,347·F0−5,9 kN` (slip completo); rigidez cai 9,3× no slip.
- **Murai 2023**: no FE `P1=µ·F0` exato, mas **experimentalmente µ_eff cai 0,46→0,24 com F0**
  ⇒ o teto de Coulomb precisa de knockdown a baixo F0.

**Veredito: FECHA.** Ação: em disp-mode, calcular `F_amp_eff = min(F_amp_in, µ_eff(F0)·F0)` com
µ_eff com knockdown (proveniência Murai/Measurement); opcional decaimento do teto com desgaste
(JMP → acopla com `surface_damage D`). O modo `couple_famp_slip` já existe default-inerte —
esta é a proveniência que faltava para ligá-lo/estendê-lo. Laços digitalizados = alvos de
validação da forma.

---

## L1 — Desgaste de flanco de rosca ∝ amplitude — **FORMA + ESCALA EXPERIMENTAL; nível axial por calibração indireta**

**O que o engine faz hoje:** ∂(afrouxamento final)/∂A_F ≡ 0 no trilho axial (falsificado, Gate B1
§4.6: dado Liu2017 = −2,2e-5/N). Já existem `k_thread_fret`/`fret_freq_exp` default-inertes
(arco mid-curve) — sem proveniência de forma completa até agora.

**O que a literatura entrega:**

- **Zhang 2018+2019** (30 CSVs): a FORMA — afrouxamento por **desgaste de rosca SEM rotação da
  porca** (confirmado 2× ; 2019 com porca comum), curvas F/F0 experimentais + perfis de desgaste
  por filete; `k_wear_spec(rosca 35CrMo/SCM435) = 8,34e-15 Pa⁻¹` com cross-check interno
  `α=(K/H)/µ` exato (µ=0,2). Amplitude fixa (0,2–0,25 mm) — a lei é linear-em-slip.
- **Liu 2020** (9 CSVs): a ESCALA experimental — d(afrouxamento)/d(amplitude) **super-linear**
  (1,2%→16,9% para 0,1→0,4 mm; expoente log-log 1,5–1,6, subindo a ~3,2 na mudança de regime);
  pré-carga mais branda e de sinal oposto; µt por revestimento (zinco 0,150 / DLC 0,126) medido.
  ⚠ cisalhamento transversal, não axial.
- **Oku 2017** (7 CSVs) + **Takazaki 2017** (5) + **Szlosarek 2023** (3): premissa axial (dano de
  raiz/interface ∝ amplitude; slip cresce com σ_a) — fadiga, não F/F0.
- **TribLett 2025** (13 CSVs): mecânica de desgaste de flanco no aperto + distribuição por filete
  `η(x)=sinh(λx)/sinh(λH)` reproduzível; coeficiente Ke NÃO divulgado.
- **Croccolo/Machines 2023**: o dado direto axial (desgaste de flanco vs A_F com F/F0) é
  **ausente na literatura** — gap real, não falha de busca.

**Veredito: implementável AGORA com proveniência mista.** Ação: estender o canal de fretting de
rosca: perda dirigida por slip de flanco, com slip axial ∝ A_F (elasticidade da rosca ⇒
∂/∂A_F ≠ 0 estrutural), forma Zhang (desgaste→perda sem rotação), nível calibrado per-rig nas
curvas axiais in-library (Liu2016/Liu2017/H.Li2022 — rig irmão), validação transversal contra
as curvas Zhang/Liu2020 recém-digitalizadas (candidatas a `ValidationCase`). Gate: o Gate B1
re-executado deve sair de ∂/∂A_F≡0 para a ordem de −2,2e-5/N; sem regressão no transversal.

---

## L5 — C_creep por par — **CLASSES NOVAS + tensão de forma DOCUMENTADA**

**O que o engine faz hoje:** `CreepLoss.rate()` é **logarítmico no tempo / linear em F0 e
ILIMITADO** — apesar do docstring "Norton-Bailey simplificado", não é lei de potência. (Achado
de engine desta rodada — corrigir docstring ou forma.)

**O que a literatura entrega:**

- **Nah 2014** (11 CSVs): relaxação por coating no faiamento (zinco inorgânico 96–226 µm →
  10,9–18,1% @744h; regressão `Creep=α+β·log₁₀t` com α,β tabulados) — **a forma log-t do engine
  é a MESMA do Nah** (coincidência feliz: o engine já está na forma certa para faiamento).
  Classe nova de par (faiamento ≠ rosca/apoio).
- **Alamos 2021+2022** (8 CSVs): forma saturante de 1ºs princípios
  `A* = 1−exp[−(t/t_c)^α]`, `t_c ∝ 1/(a·pⁿ)` — pressão acelera a depleção (mesma ideia do gate
  de conformação). Ti superplástico 10–30 MPa — só a forma transfere.
- **Jiang 2024** (6 CSVs): creep de BULK do fuste (Norton-Bailey; constantes emprestadas de
  dataset a 973 K) — **não é C_creep de contato**; candidato a 5º mecanismo futuro (junta quente).

**Veredito: PARCIAL-fecha.** Ação: (a) corrigir o docstring do `CreepLoss` (é log-t, não NB) e
documentar a coincidência com Nah; (b) forma saturante opt-in (`creep_mode`) com gate contra os
casos de creep (JCSR/Caccese/Qin/Li2022marstruc); (c) KB: classes de par com valores
(304SS UFU 1,867e-11 · faiamento-coating Nah α,β · ambiente JCSR · compósito Caccese ·
CFRP-Ti Qin · aço/Al-Si Lakes). Continua POR PAR (doutrina).

---

## L6 — K_archard/k_wear_spec por par — **FECHA (tabela por interface)**

**O que o engine faz hoje:** `k_wear_spec = K/H` canônico (merge §4.42a), default 0 (via legada);
sem tabela de proveniência por par.

**O que a literatura entrega (bandas por INTERFACE — rosca ≠ apoio/faiamento, ~3 ordens!):**

| Interface / par | k_wear_spec [1/Pa] | Fonte (tipo) |
|---|---|---|
| **Rosca** 35CrMo/SCM435 | **8,34e-15** | Zhang 2019 (derivado, validado em F/F0) |
| **Faiamento** aço estrutural Q355B/Q235B | **6,49–7,00e-12** | Li 2025 (composto K=1,05e-2 lit. + H medido-proxy; validado FE<20%) |
| Fretting 52100 (cilindro-plano) | K≈3,2e-5–2,4e-4 (norm. própria ≡ K/H) | Warmuth 2015 (medido; −50% de 5→200 Hz não-conforme, −32% conforme) |
| Fouvry aço flat-on-flat (R4) | α=4,38e-5 mm³/J (α·µ→~1e-17–1e-15 1/Pa) | Baydoun 2019 (medido, sub-GPa) |
| µ_rosca por coating | zinco 0,150 / DLC 0,126 | Liu 2020 (medido, Tabela 2) |
| Rosca (lei sem número) | `W=Ke(1+µf²)^0,5·A_r·S`, Ke não divulgado | TribLett 2025 (forma) |

**Veredito: FECHA como proveniência.** Ação: tabela de âncoras no `knowledge_base`
(`anchor_priors`/`check_input`) por interface+par, com bandas; spread >100× reconfirma
"constante por par" — nunca universal. O contraste rosca (8e-15) vs faiamento (7e-12) explica
por que um k_wear único não fecha múltiplos rigs.

---

## L4 — Conformação a ~1 GPa (W_conf_ref, n) — **FORMA SIM, VALOR NÃO (3ª confirmação do null)**

- **Inose 2025** (4 CSVs): melhor match de regime — 0,48–1,90 GPa aço; teto de pressão de
  aspereza **1,5·H** (persistência), limiar bilinear ψ≈1,5; cauda top-1% até 4,5·H;
  `A_r = W/(1,5·HV)`. Escala de aspereza (precisaria integração GW p/ virar W_conf_ref).
- **Etsion 2010** (12 CSVs): experimento — conformação **satura em ~5 ciclos** (shakedown);
  ponta de aspereza 3,7–4,3 GPa.
- **Frérot 2023** (5 CSVs): simulação — rugosidade satura (~40 ciclos, expoente ½) mas energia
  plástica **NUNCA satura** ⇒ alerta contra um W_conf_ref de valor único limpo.
- **Moshkovich 2024** (8 CSVs): ~1 GPa auto-limitante (163→88 MPa nominal), A/A0~6–7%.
- **JMPT 2023** (9 CSVs): **NÃO transfere** (conformação de metais, causalidade oposta).
- R4: Baydoun n_p≈0,5–0,6 (sub-GPa).

**Veredito: segue NÃO-ancorável por literatura** (null agora confirmado 3×). Ação: só
documentação — precedente de forma (expoente 0,5–0,6; saturação em poucos ciclos NO
DESLOCAMENTO mas não na energia; teto 1,5·H como sanity bound para p_ref) no
`MODEL_LEGITIMACY.md` §4.9; o valor continua dependente do **experimento âncora UFU**
(fretting ~1,2 GPa medindo n). Nenhuma mudança de engine.

---

## L7 — Energia específica de remoção — **FECHA COMO BOUND, não como constante**

- **Shipway 2021** (8 CSVs): `dV/dt ∝ dE/dt` abaixo de ~1 W; **platô** ~0,6–0,7 mm³/ks acima de
  ~3 W (limite de formação/ejeção de debris). Energia específica retro-derivada:
  **1,8–10,5 kJ/mm³, dependente da taxa/exposição** — não existe constante de material.
- **Warmuth 2015** (8 CSVs): dependência de frequência quantificada (proveniência p/
  `fret_freq_exp`); normalização ≡ k_wear_spec.

**Veredito: FECHA da forma honesta.** Ação: check de sanidade no budget de conservação do
colapso por dano — a energia de remoção implícita do modelo deve cair em ~1–10 kJ/mm³
(bound documentado, warning fora da faixa); não é um parâmetro fitável.

---

## C2 — Bookkeeping viscoso axial — **CÓDIGO (sem papel)**

Termo viscoso de Rayleigh acumula sem contraparte em W_ext no modo axial-força (residual −242 a
−12 J; não afeta F0/MAEs). Correção: sourcing do viscoso via W_ext em força, OU excluir o canal
viscoso do residual axial. Entra como fatia de código no plano.

---

## Achados de engine desta rodada (independentes das limitações)

1. **`CreepLoss` docstring mente**: é log-t ilimitado, não Norton-Bailey (coincide com Nah — bom
   para faiamento; documentar e oferecer saturante opt-in).
2. **µ_eff do slip-onset não é constante**: cai 0,46→0,24 com F0 (Murai) — knockdown necessário
   no teto de Coulomb.
3. **Teto de gross-slip decai com desgaste** (JMP 70–86% do pico) — acopla naturalmente com
   `surface_damage D`.
4. **k_j por ciclo é estável** (Murai: flat após 1º ciclo) — o `[K(s)]` dinâmico do V2 está
   qualitativamente certo (An 2019), mas a dependência dominante é geometria/arruela, não ciclo.
5. **Regime de aperto (F/F0 > 1)** segue sem dado experimental (Basava-Hess é simulação) —
   fora deste plano; tema (a) da rodada 6.

## O que definitivamente NÃO se resolve com esta biblioteca

- **Valor de W_conf_ref/n** na pressão de parafuso → experimento âncora UFU (spec §4.9).
- **∂(desgaste de flanco)/∂A_F axial medido diretamente** → gap real da literatura; nível via
  calibração indireta no trilho axial (acima).
- **J/mm³ constante** → não existe (é taxa-dependente); usar bound.
