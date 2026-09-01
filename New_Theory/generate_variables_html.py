"""Inventario HTML de TODAS as variaveis do modelo V2 (pedido do professor,
estudo de variaveis 2026-07-08). Gerado por INTROSPECCAO das dataclasses do
engine (JointMaterial, SlowState, JointGeometry, EnergyBudget) => sempre fiel
ao codigo. Descricoes/categorias curadas por campo.

Run: python New_Theory/generate_variables_html.py
Saida: New_Theory/validation_html/variables.html
"""
from __future__ import annotations
import dataclasses
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    JointMaterial, SlowState, JointGeometry, EnergyBudget)

# categoria, descricao, classe-de-proveniencia por campo (curado)
M = {
    # fase 1 — assentamento
    "emb_depth": ("Fase 1 · Assentamento", "profundidade total de embedding (VDI f_Z / Bolt Science por classe Rz)", "input per-junta (handbook)"),
    "N_emb": ("Fase 1 · Assentamento", "constante de ciclos do assentamento (forma exponencial exata)", "per-rig"),
    "k_emb_scale": ("Fase 1 · Assentamento", "tuner legado da assintota (Estagio B remove)", "tuner (=1)"),
    "emb_conform_exp": ("Fase 1 · Assentamento", "pre-conformacao pela PRESSAO de aperto: S=(p_ref/p_init)^n (reservatorio rapido)", "per-rig · opt-in"),
    "p_ref_emb": ("Fase 1 · Assentamento", "pressao de referencia da pre-conformacao (ancora = p do menor F0)", "input (ancora)"),
    "k_emb_renew": ("Fase 1 · Assentamento", "renovacao do embedding no re-aperto (retighten)", "per-par · opt-in"),
    "emb_amp_exp": ("Fase 1 · Assentamento", "UNIFICACAO rho (item 1): reservatorio ∝ (rho/rho_ref)^q, rho=F_ax/F0_init — lido dos 2 sweeps Liu2017 (q~3.4)", "per-rig · opt-in (LIDO)"),
    "rho_ref_emb": ("Fase 1 · Assentamento", "amplitude relativa de referencia (rho de reservatorio pleno)", "input (ancora)"),
    "emb_load_frac": ("Fase 1 · Assentamento", "reservatorio ∝ CARGA: delta_alvo += frac*F0/k_b => fast-drop fracional F0-flat (falsificacao Lu fig20, §4.19)", "per-rig (LIDO do fast-drop)"),
    # fase 1b — incubacao
    "slip_onset_W": ("Fase 1b · Incubacao", "limiar de trabalho de slip acumulado (gate Hill) — comprimento do plato inicial", "per-rig · opt-in"),
    "slip_onset_sharpness": ("Fase 1b · Incubacao", "nitidez do gate Hill de incubacao", "fixo (4)"),
    # creep / cauda lenta
    "C_creep": ("Cauda lenta · Creep", "coeficiente Norton-Bailey log-t — POR PAR tribologico (§4.7)", "per-par"),
    "t_0": ("Cauda lenta · Creep", "tempo de referencia do log", "fixo"),
    "k_creep_scale": ("Cauda lenta · Creep", "tuner legado do creep", "tuner (=1)"),
    "creep_conform_exp": ("Cauda lenta · Creep", "pre-conformacao do reservatorio LENTO: S=(p_ref/p_init)^n_slow", "per-rig · opt-in"),
    # wear
    "K_archard": ("Fase 2 · Wear", "coeficiente de Archard (ancora Fouvry: alpha*mu*H)", "per-par (ordem anc.)"),
    "hardness": ("Fase 2 · Wear", "dureza do material do par (Archard)", "material"),
    "k_wear_scale_ax": ("Fase 2 · Wear", "tuner direcional axial do wear", "tuner (=1)"),
    "k_wear_scale_tr": ("Fase 2 · Wear", "tuner direcional transversal do wear", "per-rig (§4.8)"),
    "k_thread_fret": ("Fase 2 · Fretting", "fretting de flanco axial ∝ A_F (opt-in; 3x falsificado como fix do gap A_F)", "per-par · opt-in"),
    # loosening
    "tr_loose_gain": ("Fase 2 · Loosening", "ganho dinamico transversal do two-factor", "calibrado (Estagio A)"),
    "Phi_ax_correction": ("Fase 2 · Loosening", "correcao fina de Phi axial", "tuner (=1)"),
    "Phi_tr_correction": ("Fase 2 · Loosening", "correcao fina de Phi transversal", "tuner (=1)"),
    "k_loose_scale_ax": ("Fase 2 · Loosening", "tuner axial do loosening", "tuner (=1)"),
    "k_loose_scale_tr": ("Fase 2 · Loosening", "tuner transversal do loosening", "tuner (=1)"),
    "loose_torsion_mode": ("Fase 2 · Loosening", "rigidez torsional: legacy (k_j*d2/2) | bolt_torsion (eta*G*J/L — runaway fisico)", "modo · opt-in"),
    "eta_loose": ("Fase 2 · Loosening", "eficiencia de ratcheting do shank (so bolt_torsion)", "per-par"),
    "k_ratchet": ("Fase 2 · Loosening", "ratcheting CINEMATICO: rotacao ∝ caminho de gross-slip (amp-proporcional)", "per-rig · opt-in"),
    "ratchet_torque_coupled": ("Fase 2 · Loosening", "forma-produto: ratchet x slip_fraction (acelerante; rejeitada nos 2 alvos)", "modo · opt-in"),
    "k_member_shear": ("Limiar de curso", "cisalhamento do MEMBRO em serie com k_tr (=G*A/t; polimero absorve o curso — HDPE §4.20)", "per-caso (G*A per-rig) · opt-in"),
    # limiar de curso
    "k_tr_mode": ("Limiar de curso", "rigidez transversal de onset: axial_frac | bending (flexao c*E*I/L^3)", "modo · opt-in"),
    "c_bend": ("Limiar de curso", "fator de compliance da flexao/stack transversal", "per-rig (bracketavel)"),
    "delta_free": ("Limiar de curso", "take-up FIXO do curso (folga+fixacao, F0-independente): slip=max(0, d - d0 - F_slip/k_tr)", "per-rig (LIDO do dado)"),
    "slip_regime_mode": ("Limiar de curso", "lei Cattaneo-Mindlin partial<->gross (off | cattaneo_mindlin)", "modo · opt-in"),
    "slip_regime_sharpness": ("Limiar de curso", "expoente k do g_gross (k=1 = fracao atual)", "per-rig"),
    "slip_capacity_coeff": ("Limiar de curso", "kappa da razao r=Q/(mu*F0*kappa) p/ wear/fret", "per-par"),
    "partial_slip_exp": ("Limiar de curso", "expoente m do g_partial (CM)", "fixo (1.5)"),
    "couple_famp_slip": ("Limiar de curso", "cap Coulomb F_tr<=mu*F0 em gross slip (#4)", "modo · opt-in"),
    # arresto
    "loose_arrest_floor": ("Fase 3 · Arresto", "nucleo auto-travado: F_min = floor*F0_init (platô — LIDO do dado)", "per-rig · opt-in"),
    # dano / lubrificacao
    "c_D": ("Dano superficial", "taxa de crescimento do dano (PER-LUBE: dry~0.5, oil~0.03)", "per-lube"),
    "W_ref": ("Dano superficial", "escala de trabalho do crescimento de D", "per-par"),
    "k_dmg_mu": ("Dano superficial", "dano reduz mu_bearing: mu_eff=mu*(1-k*D)", "per-par"),
    "k_dmg_wear": ("Dano superficial", "dano amplifica wear (colapso reaperto/TP7)", "per-par"),
    "k_damage_scale": ("Dano superficial", "tuner do dano", "tuner (=1)"),
    "W_crit": ("Dano superficial", "gate de onset do dano (dose critica de slip)", "per-rig · opt-in"),
    "dmg_onset_sharpness": ("Dano superficial", "nitidez do gate de onset do dano", "fixo (4)"),
    "dmg_dwell_exp": ("Dano superficial", "fator de DWELL: dD *= (f_ref/f)^p — fretting-corrosao, dose de oxido ∝ tempo de contato (par Yang 5/10Hz, §4.21)", "per-rig · opt-in (LIDO do par de freq)"),
    "f_ref_dmg": ("Dano superficial", "frequencia de referencia do dwell (ancora per-rig)", "input (ancora)"),
    "k_gall": ("Dano superficial", "galling no RE-aperto: mu_thread_tighten=(1+k*D) (declinio da recuperacao dry)", "per-par · opt-in"),
    # conformacao (sobretorque)
    "W_conf_ref": ("Conformacao (sobretorque)", "escala de conformacao pressure-gated (per-par UFU; ancora FALHOU)", "per-par"),
    "conform_pressure_exp": ("Conformacao (sobretorque)", "expoente de pressao n", "calibrado"),
    "p_ref_conform": ("Conformacao (sobretorque)", "pressao de referencia", "input"),
    "conform_driver": ("Conformacao (sobretorque)", "driver raw | effective (auto-limitante)", "modo"),
    # fadiga
    "fatigue_enabled": ("Fadiga -> fratura", "liga o FatigueLoss (cliff em Miner D>=1)", "modo · opt-in"),
    "fat_Kt": ("Fadiga -> fratura", "concentracao de tensao raiz de rosca", "handbook (3.5)"),
    "fat_sigma_uts": ("Fadiga -> fratura", "UTS p/ correcao Goodman (media evolui com F0)", "material"),
    "fat_sigma_knee": ("Fadiga -> fratura", "joelho da Su-N bilinear", "per-material"),
    "fat_C1": ("Fadiga -> fratura", "coef. alta tensao da Su-N", "per-material"),
    "fat_m1": ("Fadiga -> fratura", "expoente alta tensao", "per-material"),
    "fat_C2": ("Fadiga -> fratura", "coef. baixa tensao", "per-material"),
    "fat_m2": ("Fadiga -> fratura", "expoente baixa tensao", "per-material"),
    "fat_sigma_endurance": ("Fadiga -> fratura", "limite de fadiga (vida infinita abaixo)", "per-material"),
    "fatigue_residual_frac": ("Fadiga -> fratura", "F0 residual pos-fratura", "fixo (0)"),
    # rigidez / matrizes / massa
    "k_j_init": ("Rigidez da junta", "rigidez axial inicial do membro (Greenwood-Williamson)", "per-junta (material do membro)"),
    "alpha_GW": ("Rigidez da junta", "expoente GW do amolecimento k_j(F0)", "empirico"),
    "m_x": ("Dinamica", "massa modal x", "input"),
    "m_y": ("Dinamica", "massa modal y", "input"),
    "I_theta": ("Dinamica", "inercia rotacional", "input"),
    "rayleigh_alpha": ("Dinamica", "amortecimento Rayleigh ∝[M]", "input"),
    "rayleigh_beta": ("Dinamica", "amortecimento Rayleigh ∝[K]", "input"),
    "mu_thread": ("Atrito", "atrito de flanco de rosca", "per-par/lube"),
    "mu_bearing": ("Atrito", "atrito do apoio da cabeca (modulado por D)", "per-par/lube"),
}
S = {
    "F_0": "pre-carga residual [N] — a variavel central",
    "F_0_init": "pre-carga inicial (referencia p/ floors, conformancia, fracoes)",
    "delta_emb": "assentamento consumido [m] (estado — permite junta reusada)",
    "delta_creep": "deslocamento de creep acumulado [m]",
    "delta_wear": "profundidade de wear acumulada [m]",
    "delta_thread_fret": "profundidade de fretting de flanco [m]",
    "theta_loose": "rotacao de afrouxamento acumulada [rad] (helice -> dF0)",
    "D": "dano superficial [0,1] (modula mu e wear; per-lube via c_D)",
    "D_fatigue": "dano de Miner acumulado [0,1] (fratura em 1)",
    "W_slip_acc": "trabalho de slip transversal acumulado [J] (driver da incubacao)",
    "W_conf": "trabalho de conformacao pressure-weighted [J] (driver do gate de sobretorque)",
}
G = {
    "E": "modulo de Young do parafuso", "A_s": "area de tensao", "L_eff": "grip efetivo",
    "d_2": "diametro de passo", "pitch": "passo da rosca",
    "r_bearing": "raio efetivo do apoio", "A_contact": "area real do anel de apoio (per-rig, 11g)",
}
E = {
    "W_ext": "trabalho externo acumulado", "U_stored": "energia elastica armazenada",
    "U_stored_init": "referencia inicial", "W_damp_visc": "dissipacao viscosa (Rayleigh)",
    "W_diss_emb": "dissipacao do embedding", "W_diss_creep": "dissipacao do creep",
    "W_diss_wear": "dissipacao Archard/fretting", "W_diss_loose": "atrito no filete",
    "W_diss_friction_y": "atrito transversal", "W_diss_fracture": "energia liberada na fratura (cliff)",
}

# --- ANALISE DIMENSIONAL (pedido do professor, 2026-07-08) -------------------
# unidade + formula dimensional [M L T] por campo. "—" = adimensional (puro).
U = {
    "emb_depth": ("m", "L"), "N_emb": ("ciclos", "—"), "k_emb_scale": ("—", "—"),
    "emb_conform_exp": ("—", "—"), "p_ref_emb": ("Pa", "M L⁻¹T⁻²"), "k_emb_renew": ("—", "—"),
    "emb_amp_exp": ("—", "—"), "rho_ref_emb": ("—", "—"), "emb_load_frac": ("—", "—"), "k_member_shear": ("N/m", "M T⁻²"),
    "slip_onset_W": ("J", "M L²T⁻²"), "slip_onset_sharpness": ("—", "—"),
    "C_creep": ("m/N", "M⁻¹T²"), "t_0": ("s", "T"), "k_creep_scale": ("—", "—"),
    "creep_conform_exp": ("—", "—"),
    "K_archard": ("—", "—"), "hardness": ("Pa", "M L⁻¹T⁻²"),
    "k_wear_scale_ax": ("—", "—"), "k_wear_scale_tr": ("—", "—"), "k_thread_fret": ("—", "—"),
    "tr_loose_gain": ("—", "—"), "Phi_ax_correction": ("—", "—"), "Phi_tr_correction": ("—", "—"),
    "k_loose_scale_ax": ("—", "—"), "k_loose_scale_tr": ("—", "—"),
    "loose_torsion_mode": ("modo", "—"), "eta_loose": ("—", "—"), "k_ratchet": ("—", "—"),
    "ratchet_torque_coupled": ("bool", "—"),
    "k_tr_mode": ("modo", "—"), "c_bend": ("—", "—"), "delta_free": ("m", "L"),
    "slip_regime_mode": ("modo", "—"), "slip_regime_sharpness": ("—", "—"),
    "slip_capacity_coeff": ("—", "—"), "partial_slip_exp": ("—", "—"),
    "couple_famp_slip": ("bool", "—"), "loose_arrest_floor": ("—", "—"),
    "c_D": ("1/ciclo", "—"), "W_ref": ("J", "M L²T⁻²"), "k_dmg_mu": ("—", "—"),
    "k_dmg_wear": ("—", "—"), "k_damage_scale": ("—", "—"), "W_crit": ("J", "M L²T⁻²"),
    "dmg_onset_sharpness": ("—", "—"), "k_gall": ("—", "—"), "dmg_dwell_exp": ("—", "—"), "f_ref_dmg": ("Hz", "T⁻¹"),
    "W_conf_ref": ("J", "M L²T⁻²"), "conform_pressure_exp": ("—", "—"),
    "p_ref_conform": ("Pa", "M L⁻¹T⁻²"), "conform_driver": ("modo", "—"),
    "fatigue_enabled": ("bool", "—"), "fat_Kt": ("—", "—"),
    "fat_sigma_uts": ("Pa", "M L⁻¹T⁻²"), "fat_sigma_knee": ("Pa", "M L⁻¹T⁻²"),
    "fat_C1": ("ciclos·Pa^m1", "⚠ dep. de m1"), "fat_m1": ("—", "—"),
    "fat_C2": ("ciclos·Pa^m2", "⚠ dep. de m2"), "fat_m2": ("—", "—"),
    "fat_sigma_endurance": ("Pa", "M L⁻¹T⁻²"), "fatigue_residual_frac": ("—", "—"),
    "k_j_init": ("N/m", "M T⁻²"), "alpha_GW": ("—", "—"),
    "m_x": ("kg", "M"), "m_y": ("kg", "M"), "I_theta": ("kg·m²", "M L²"),
    "rayleigh_alpha": ("1/s", "T⁻¹"), "rayleigh_beta": ("s", "T"),
    "mu_thread": ("—", "—"), "mu_bearing": ("—", "—"),
}
US = {"F_0": ("N", "M L T⁻²"), "F_0_init": ("N", "M L T⁻²"),
      "delta_emb": ("m", "L"), "delta_creep": ("m", "L"), "delta_wear": ("m", "L"),
      "delta_thread_fret": ("m", "L"), "theta_loose": ("rad", "—"),
      "D": ("—", "—"), "D_fatigue": ("—", "—"),
      "W_slip_acc": ("J", "M L²T⁻²"), "W_conf": ("J", "M L²T⁻²")}
UG = {"E": ("Pa", "M L⁻¹T⁻²"), "A_s": ("m²", "L²"), "L_eff": ("m", "L"),
      "d_2": ("m", "L"), "pitch": ("m", "L"), "r_bearing": ("m", "L"),
      "A_contact": ("m²", "L²")}
UE = {k: ("J", "M L²T⁻²") for k in E}

# grupos adimensionais Pi — a espinha dorsal do modelo (toda fisica de fase e
# governada por um destes; as variaveis dimensionais so poem ESCALA)
PI_GROUPS = [
    ("ρ = F_ax/F₀_init", "amplitude relativa cíclica — governa o reservatório de assentamento (S_ρ=(ρ/ρ_ref)^3.4; UNIFICA os 2 sweeps Liu2017 — item 1)"),
    ("r = Q/(μ·F₀·κ)", "razão carga/capacidade Cattaneo-Mindlin — regime partial↔gross slip"),
    ("δ_g/(δ_g+δ_t)", "fração de gross-slip do curso (gate do loosening); δ_t = δ₀ + F_slip/k_tr"),
    ("1 − T_res/T_loose", "excesso de torque adimensional — motor do runaway torque-excesso"),
    ("Φ = k_b/(k_b+k_j)", "fator de carga da junta (k_j(F₀) via Greenwood-Williamson)"),
    ("tan β = p/(π·d₂)", "ângulo de hélice — O acoplamento axial↔torsional"),
    ("N/N_emb", "relógio adimensional do assentamento (forma exponencial exata)"),
    ("Π_creep = k_b·C_creep", "número de creep — fração de F₀ perdida por unidade ln(t)"),
    ("S_p = (p_ref/p_init)^n", "pré-conformação por pressão (reinterpretada pelo item 1: caso A_F-fixo de S_ρ)"),
    ("W/W_onset · W/W_ref · W/W_crit · W/W_conf_ref", "doses de trabalho adimensionais (gates Hill: incubação, dano, onset, conformação)"),
    ("floor = F_min/F₀_init", "platô de arresto como fração da pré-carga inicial"),
    ("D, D_fatigue ∈ [0,1]", "danos adimensionais (superfície; Miner)"),
    ("σ_a/(1−σ_m/σ_uts) / σ_knee", "razões de tensão da fadiga (Goodman + Su-N bilinear)"),
    ("μ, K_archard, k_ratchet, η, c_bend, α_GW, expoentes", "constantes adimensionais puras — o que DEVE transferir cross-rig (§8)"),
]
# consistencia dimensional das equacoes de cada mecanismo (verificada a mao)
EQ_CHECK = [
    ("dF₀ = −k_b·Δδ  (emb / creep / wear / fret)", "[N/m]·[m] = [N]", "✓"),
    ("dF₀ = −k_b·(p/2π)·Δθ  (hélice)", "[N/m]·[m/rad]·[rad] = [N]", "✓"),
    ("Δθ = frac·ΔT/k_tors  (torque-excesso)", "[—]·[N·m]/[N·m/rad] = [rad]", "✓"),
    ("Δθ = k_ratchet·4·slip/(d₂/2)  (cinemático)", "[—]·[m]/[m] = [rad ≡ —]", "✓"),
    ("d_wear = K·F_N·4s/(H·A)  (Archard)", "[—][N][m]/([Pa][m²]) = [m]", "✓"),
    ("δ_creep = C_creep·F₀·Δln(t/t₀+1)", "[m/N][N][—] = [m]", "✓"),
    ("dE = μ·F_N·4s  ·  dE = F₀·Δδ", "[N][m] = [J]", "✓"),
    ("dE_loose = T_res·Δθ", "[N·m][rad] = [J]", "✓"),
    ("W_visc = π·ω·c·X²  (Rayleigh)", "[1/s][N·s/m][m²] = [J]", "✓"),
    ("k_tr = c_bend·E·I/L³  (flexão)", "[—][Pa][m⁴]/[m³] = [N/m]", "✓"),
    ("k_tors = η·G·J/L", "[—][Pa][m⁴]/[m] = [N·m/rad]", "✓"),
    ("dD = c_D·(W/W_ref)·(1−D)·g", "[1/ciclo][—][—][—] = [1/ciclo]", "✓"),
    ("N_f = C1·σ^−m1  (Su-N)", "[ciclos·Pa^m1][Pa^−m1] = [ciclos]",
     "⚠ C1/C2 carregam dimensão dependente do expoente (prática S-N padrão; "
     "recomendação Estágio B: N_f = N_ref·(σ/σ_ref)^−m, adimensional)"),
]

# --- NAO LINEARIDADES (pedido do professor, 2026-07-08) ----------------------
# classificacao de cada forma por TIPO de nao linearidade, ordem local
# (derivada logaritmica / expoente), sinal de realimentacao no F0 e consequencia.
NL_ROWS = [
    ("Embedding: dδ/dN = (δ_alvo−δ)/N_emb", "relaxação de 1ª ordem — LINEAR no estado",
     "1 (exp. saturante)", "− (reservatório finito)",
     "a única forma quase-linear; fase 1 identificável por N_emb; alvo carrega as não linearidades paramétricas (S_ρ, S_p)"),
    ("S_ρ = (ρ/ρ_ref)^q, q=2.375", "lei de potência (escala)", "q = 2.375", "0 (ρ fixo no run)",
     "sensibilidade = expoente: +10% em ρ ⇒ +24% no reservatório; é o que os 2 sweeps Liu2017 medem"),
    ("Creep: δ = C·F₀·ln(t/t₀+1)", "sublinear no tempo (taxa ∝ 1/t)", "decrescente", "− fraco (taxa ∝ F₀)",
     "cauda log-década; nunca satura mas auto-atenua; quase-linear em F₀ ⇒ Π_creep = k_b·C identificável"),
    ("Conformâncias: S = (p_ref/p)^n, n=2–3.6", "lei de potência", "n = 2.0–3.6 (per-rig)", "0 (keyed em F₀_init)",
     "separação por pré-carga; caso A_F-fixo de S_ρ no canal rápido (§4.18)"),
    ("GW: k_j = k_j,0·(F₀/F_init)^0.5", "lei de potência no ESTADO", "0.5", "paramétrica (entra em Φ)",
     "[K(s)] dinâmico: Φ desloca conforme F₀ cai — não linearidade lenta→rápida"),
    ("Wear (Archard): d = K·F_N·4s/(H·A)", "LINEAR em F e s", "1", "+ leve (slip cresce quando F₀ cai)",
     "o carrier mais estável do modelo — por isso domina disp-mode e aceita âncora (Fouvry)"),
    ("Gates Hill: g = W^4/(W^4+W_ref^4)", "sigmoide (quase-chave)", "máx no limiar (k=4)", "chaveia fases",
     "cria o platô de incubação e o onset de dano; sensibilidade →extrema no limiar ⇒ scatter perto do onset é FÍSICO (pisos Lu/Bauer)"),
    ("Coulomb/take-up: slip = max(0, δ−δ₀−F/k_tr)", "kink (não-suave)", "descontinuidade na derivada", "—",
     "limiar de curso; define regime por caso; bracketável do próprio dado (amp que colapsa / não colapsa)"),
    ("Cattaneo-Mindlin: r = Q/(μF₀κ), g ∝ r^1.5", "potência + realimentação", "1.5", "+ (F₀↓ ⇒ r↑ ⇒ mais gross-slip)",
     "erosão-para-gross-slip: colapso ATRASADO de platô (runaway lento)"),
    ("Torque-excesso: dθ ∝ max(0, T_l−T_r)/k_tors", "kink + realimentação positiva", "super-exponencial além do onset", "+ forte (T_r ∝ F₀)",
     "o runaway clássico (regime Rousseau/Karlsen); sem arresto vai a zero"),
    ("Ratchet cinemático: dθ = k·4·slip/(d₂/2)", "linear no slip", "1", "+ fraco (via slip(F₀))",
     "regime Lu: colapso ∝ caminho de escorregamento, amplitude-proporcional"),
    ("Arrest: g = max(0, 1−F_min/F₀)", "kink estabilizador", "—", "− (ponto fixo ESTÁVEL em F_min)",
     "transforma o runaway em S-curve; platô final LIDO do dado (floor≈platô)"),
    ("Dano: dD = c_D·(W/W_ref)·(1−D)·g", "logístico + realimentação positiva", "sigmoide em N", "+ (D→μ↓→slip↑→W↑), limitado por (1−D)",
     "colapso sigmoide do reaperto/TP7; o (1−D) impede divergência"),
    ("Fadiga: N_f = C·σ^−m, m = 3.5/6.0 + Miner", "potência ALTÍSSIMA + salto", "m = 3.5–6 (a maior do modelo)", "+ via σ_m(F₀) (Goodman)",
     "cliff: D_f≥1 ⇒ fratura = DESCONTINUIDADE; scatter de vida amplificado ×m — por isso métrica de vida (fator-2), não MAE"),
    ("Hélice: dF₀ = −k_b·(p/2π)·dθ", "BILINEAR (θ̇ depende de F₀; F₀ de θ)", "produto de estados", "fecha o laço",
     "o acoplamento axial↔torsional central — torna o sistema dinâmico, não somatório de perdas"),
    ("Conformação sobretorque (W_conf, driver effective)", "sigmoide auto-limitante", "n=2 no gate", "− (gate fecha com o próprio W)",
     "inércia no nominal, mordida no sobretorque; per-par (escala UFU)"),
]
# resumo por CLASSE (a visao agrupada; a tabela NL_ROWS da o detalhe por forma)
NL_CLASSES = [
    ("Linear no estado",
     "Embedding (relaxação de 1ª ordem), wear Archard, ratchet cinemático",
     "ordem 1",
     "os 'carriers' estáveis — por isso embedding e wear aceitam fit/âncora com facilidade"),
    ("Sublinear",
     "Creep log-t (taxa ∝ 1/t)",
     "ordem decrescente",
     "auto-atenua; nunca satura; quase-linear em F₀"),
    ("Leis de potência",
     "S_ρ (q=2.375) · conformâncias (n=2–3.6) · GW k_j∝F₀^0.5 · CM r^1.5 · fadiga σ^−m (m=3.5–6, a maior)",
     "= expoente",
     "sensibilidade multiplicada pelo expoente: 10% de erro em ρ ⇒ 24% no reservatório; 10% em σ ⇒ 35–60% em N_f"),
    ("Sigmoides (Hill, k=4)",
     "incubação · onset de dano · conformação",
     "máx no limiar",
     "quase-chaves: criam a ESTRUTURA DE FASES (platô→colapso); sensibilidade diverge no limiar"),
    ("Kinks (não-suaves)",
     "Coulomb/take-up δ₀ · onset de torque · clamps min/max · arrest floor",
     "descontinuidade na derivada",
     "definem fronteiras de regime — por isso são bracketáveis do dado"),
    ("Realimentações",
     "<b>+</b> torque-excesso (T_res∝F₀ cai⇒acelera) · CM-capacidade (F₀↓⇒r↑) · dano (D→μ↓→slip↑→W↑) &nbsp;|&nbsp; "
     "<b>−</b> reservatórios finitos · creep∝F₀ · arrest (ponto fixo estável)",
     "runaway vs S-curve",
     "o coração dinâmico: platô = feedbacks negativos vencem; colapso = positivos vencem"),
    ("Descontinuidade",
     "cliff de fadiga (Miner D_f=1 ⇒ fratura)",
     "salto",
     "a não linearidade mais forte do modelo"),
    ("Bilinear (produto de estados)",
     "hélice: dF₀ = −k_b·(p/2π)·dθ com θ̇ dependente de F₀",
     "produto θ×F₀",
     "fecha o laço e torna tudo um SISTEMA acoplado, não um somatório de perdas"),
]

NL_NOTES = [
    ("Separação temporal = quasi-linearização", "as não linearidades DOMINAM em janelas distintas "
     "(assentamento → incubação → crash → arresto). Em cada fase um termo manda e os outros são "
     "quase constantes ⇒ o fit por fase/descida por coordenadas converge e as constantes são "
     "identificáveis — a arquitetura de fases é uma linearização por janelas."),
    ("Dois atratores + separatriz", "feedbacks negativos (embedding, creep, arrest, conformação) "
     "vs positivos (torque-excesso, CM-capacidade, dano, fadiga). Platô e colapso são ATRATORES; "
     "a fronteira (limiar de curso / dose de incubação) é uma separatriz — perto dela, pequenas "
     "variações de parâmetro trocam o desfecho qualitativo. O modo de erro collapse-missed (§4.15) "
     "era exatamente esta faca-de-dois-gumes; finais não-monotônicos do Lu fig20 são o dado "
     "sentado NA separatriz."),
    ("Sensibilidade = expoente (derivada log)", "potências propagam erro multiplicado pelo expoente: "
     "10% em ρ ⇒ 24% (q=2.375); 10% em σ ⇒ 35–60% em N_f (m=3.5–6); nos gates Hill (k=4) a "
     "sensibilidade diverge no limiar. Consequência: pisos de scatter medidos são LIMITE FÍSICO, "
     "não preguiça de fit."),
    ("Superposição FALHA (dependência de caminho)", "os estados são integrais irreversíveis "
     "(W_slip_acc, W_conf, D, D_fatigue, δ's) — a mesma dose em ordem diferente dá estado diferente "
     "(incubação, reaperto/renewal). Nunca calibrar mecanismos em dados somados; curva completa, "
     "na ordem, sempre."),
    ("Formas fechadas só nas classes brandas", "exponencial saturante (embedding), log (creep) e "
     "potências têm surrogates analíticos (ground-fit); realimentações + gates exigem o ENGINE "
     "por-ciclo — a regra do 1e6 existe porque runaway lento não aparece em smoke curto."),
    ("O invariante que segura tudo", "a conservação de energia (W_ext + ΔU = ΣW_diss) vale em "
     "QUALQUER regime não linear — é o teste estrutural que não depende de linearização."),
]

CSS = """body{margin:0;background:#e8eaed;color:#1a1e24;font-family:'Segoe UI',sans-serif;line-height:1.5}
.wrap{max-width:1000px;margin:0 auto;padding:24px 20px 60px}
h1{font-size:20px;margin:4px 0} h2{font-size:14px;margin:22px 0 6px;color:#2f6690}
table{border-collapse:collapse;width:100%;font-size:12px;background:#f8f9fa;border:1px solid #c9ced5;border-radius:8px}
td,th{padding:5px 8px;border-bottom:1px solid #dfe3e7;text-align:left;vertical-align:top}
th{font-family:Consolas,monospace;font-size:10.5px;text-transform:uppercase;color:#5c6570}
code{font-family:Consolas,monospace;font-size:11.5px;color:#2f6690}
.prov{font-family:Consolas,monospace;font-size:10.5px;color:#5c6570}
.sub{font-family:Consolas,monospace;font-size:11px;color:#5c6570}"""


def main():
    rows_by_cat = {}
    for f in dataclasses.fields(JointMaterial):
        cat, desc, prov = M.get(f.name, ("(sem categoria)", "", ""))
        default = f.default if f.default is not dataclasses.MISSING else ""
        unit, dim = U.get(f.name, ("", ""))
        rows_by_cat.setdefault(cat, []).append(
            f"<tr><td><code>{f.name}</code></td><td>{desc}</td>"
            f"<td><code>{default}</code></td><td class='prov'>{unit}</td>"
            f"<td class='prov'>{dim}</td><td class='prov'>{prov}</td></tr>")
    order = ["Fase 1 · Assentamento", "Fase 1b · Incubacao", "Cauda lenta · Creep",
             "Fase 2 · Wear", "Fase 2 · Fretting", "Fase 2 · Loosening",
             "Limiar de curso", "Fase 3 · Arresto", "Dano superficial",
             "Conformacao (sobretorque)", "Fadiga -> fratura", "Rigidez da junta",
             "Atrito", "Dinamica", "(sem categoria)"]
    parts = []
    n_total = len(dataclasses.fields(JointMaterial))
    for cat in order:
        if cat not in rows_by_cat:
            continue
        parts.append(f"<h2>{cat} ({len(rows_by_cat[cat])})</h2>"
                     f"<table><tr><th>variavel</th><th>o que e</th><th>default</th>"
                     f"<th>unid.</th><th>dim [M·L·T]</th>"
                     f"<th>classe de proveniencia</th></tr>{''.join(rows_by_cat[cat])}</table>")

    def simple(dc, desc, udict):
        rows = "".join(
            f"<tr><td><code>{f.name}</code></td><td>{desc.get(f.name,'')}</td>"
            f"<td><code>{f.default if f.default is not dataclasses.MISSING else ''}</code></td>"
            f"<td class='prov'>{udict.get(f.name, ('', ''))[0]}</td>"
            f"<td class='prov'>{udict.get(f.name, ('', ''))[1]}</td></tr>"
            for f in dataclasses.fields(dc))
        return (f"<table><tr><th>variavel</th><th>o que e</th><th>default</th>"
                f"<th>unid.</th><th>dim [M·L·T]</th></tr>{rows}</table>")

    # ancoras de proveniencia (Fase 2): New_Theory/anchors_verdicts.json
    import json as _json
    anc_path = ROOT / "New_Theory" / "anchors_verdicts.json"
    anc_rows = ""
    if anc_path.exists():
        anc = _json.loads(anc_path.read_text(encoding="utf-8"))
        for const, v in anc.items():
            anc_rows += (f"<tr><td><code>{const}</code></td><td><b>{v['verdict']}</b></td>"
                         f"<td><code>{v['anchor']}</code></td><td>{v['note']}</td></tr>")
    pi_rows = "".join(f"<tr><td><code>{g}</code></td><td>{d}</td></tr>"
                      for g, d in PI_GROUPS)
    eq_rows = "".join(f"<tr><td><code>{e}</code></td><td class='prov'>{d}</td><td>{s}</td></tr>"
                      for e, d, s in EQ_CHECK)
    nl_rows = "".join(
        f"<tr><td><code>{f_}</code></td><td>{cl}</td><td class='prov'>{o}</td>"
        f"<td class='prov'>{fb}</td><td>{cq}</td></tr>"
        for f_, cl, o, fb, cq in NL_ROWS)
    nl_cls = "".join(
        f"<tr><td><b>{c}</b></td><td>{fs}</td><td class='prov'>{o}</td><td>{b}</td></tr>"
        for c, fs, o, b in NL_CLASSES)
    nl_notes = "".join(f"<tr><td><b>{t}</b></td><td>{d}</td></tr>" for t, d in NL_NOTES)

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BAS V2 — variaveis do modelo</title><style>{CSS}</style></head><body><div class="wrap">
<p class="sub"><a href="index.html">&larr; index</a> · <a href="dashboard.html">painel</a></p>
<h1>Variaveis do modelo V2 — inventario completo (gerado do codigo)</h1>
<p class="sub">JointMaterial: {n_total} campos · SlowState: {len(dataclasses.fields(SlowState))} estados ·
JointGeometry: {len(dataclasses.fields(JointGeometry))} · EnergyBudget: {len(dataclasses.fields(EnergyBudget))} ·
organizado pela ARQUITETURA DE FASES · classes: input/handbook · per-rig · per-par · per-lube ·
per-material · tuner(=1, Estagio B remove) · modo opt-in (default-inert)</p>
{''.join(parts)}
<h2>Âncoras de proveniência (Fase 2 — campanha em curso)</h2>
<p class="sub">cada constante confrontada com sua tabela MEDIDA do database (anchors_csv);
verdicts: PASSA (valor validado) · BANDA (faixa medida) · DIREÇÃO (sinal/forma nomeados) · FALHA.
Gerado de New_Theory/anchors_verdicts.json (harness anchors_confront.py).</p>
<table><tr><th>constante</th><th>verdict</th><th>âncora</th><th>nota</th></tr>{anc_rows}</table>
<h2>Grupos adimensionais Π — a espinha dorsal do modelo ({len(PI_GROUPS)})</h2>
<p class="sub">toda a física de fase é governada por um grupo Π; as variáveis dimensionais
(F₀, δ's, W's, k's) só põem ESCALA. Consequência do §8 (MODEL_LEGITIMACY): o que transfere
cross-rig são os grupos/formas; as escalas dimensionais são por par/rig/junta.</p>
<table><tr><th>grupo Π</th><th>significado físico</th></tr>{pi_rows}</table>
<h2>Consistência dimensional das equações ({len(EQ_CHECK)})</h2>
<table><tr><th>equação</th><th>dimensões</th><th>status</th></tr>{eq_rows}</table>
<h2>Não linearidades — onde vivem</h2>
<p class="sub"><b>Dentro de um ciclo o modelo é essencialmente linear</b> (Hooke, [K] constante
no ciclo) com UMA exceção: o atrito de Coulomb (stick-slip, um kink). <b>Toda a não linearidade
relevante vive na dinâmica LENTA</b> — o vetor de estado s evoluindo ciclo a ciclo: um sistema
dinâmico não linear autônomo em s, não um somatório de perdas. Ordem local = derivada
logarítmica (expoente). Realimentação: sinal do laço fechado em F₀ (− estabiliza / + runaway).</p>
<h3>Resumo por classe ({len(NL_CLASSES)})</h3>
<table><tr><th>classe</th><th>formas</th><th>ordem</th><th>comportamento</th></tr>{nl_cls}</table>
<h3>Detalhe por forma ({len(NL_ROWS)})</h3>
<table><tr><th>forma</th><th>tipo</th><th>ordem local</th><th>realim.</th><th>consequência</th></tr>{nl_rows}</table>
<h3>Consequências estruturais</h3>
<table>{nl_notes}</table>
<h2>SlowState — vetor de estado lento s ({len(dataclasses.fields(SlowState))})</h2>{simple(SlowState, S, US)}
<h2>JointGeometry ({len(dataclasses.fields(JointGeometry))})</h2>{simple(JointGeometry, G, UG)}
<h2>EnergyBudget — contabilidade de energia ({len(dataclasses.fields(EnergyBudget))})</h2>{simple(EnergyBudget, E, UE)}
<p class="sub">gerado por New_Theory/generate_variables_html.py (introspeccao das dataclasses) ·
estudo de variaveis 2026-07-08 · <b>item 1 CONCLUÍDO (§4.18)</b>: unificação ρ adotada —
S_ρ=(ρ/ρ_ref)^2.375 substitui emb_conform_exp no trilho axial (A_F-sweep zero-extra-fit
0.035→0.017, P₀ bit-idêntico, 1 variável a menos; resíduo remanescente nomeia o canal lento) ·
análise dimensional 2026-07-08: 1 inconsistência formal encontrada (fat_C1/C2, prática S-N padrão — nota Estágio B)</p>
</div></body></html>"""
    out = ROOT / "New_Theory" / "validation_html" / "variables.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({n_total} JointMaterial fields)")


if __name__ == "__main__":
    main()
