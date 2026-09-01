"""
Dynamic Stiffness Analyzer — formulação energética não-linear acoplada.

Implementa §12 do spec `2026-05-16-two-factor-loosening-theory.md`:

  - Vetor de estado lento `s = (F_0, δ_emb, δ_creep, δ_wear, θ_loose)`
  - Matriz [K(s)] reavaliada a cada ciclo (não-linear em F_0)
  - Mecanismos de perda paralelos via interface plug-in `LossMechanism`
  - Contabilidade rigorosa de energia: W_ext + |ΔU| = Σ W_dissipado

Filosofia:
  Tudo é tratado em termos de **energia**:
    - U_armazenada(s): energia elástica em tração no estojo + compressão na junta
    - W_ext: trabalho externo absorvido por ciclo
    - W_amortecida: dissipação viscosa (Rayleigh)
    - W_dissipada: friction × slip + plastic + creep work + wear

  Modelo é **estritamente não-linear**: F_0 → k_j_ax(F_0) → Φ(s) → ΔF_0 →
  F_0_next. Todos os mecanismos estão acoplados via o estado.

  Arquitetura prepara integração futura no BAS:
    - Matrizes [M], [K(s)], [C(s)] em formato numpy 3×3 para DOFs (x, y, θ)
    - Compatível com o paradigma `[M]{q̈} + [C]{q̇} + [K]{q} = {F}` do
      `coupled_loosening_analyzer.py` existente
    - Estado serializável (pode virar campo persistente de MSDModel)
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Tuple

import numpy as np


# ============================================================================
# Constantes físicas
# ============================================================================

E_STEEL = 200e9                # Pa, módulo de Young do aço carbono
G_STEEL = 77e9                 # Pa, módulo de cisalhamento (aço) — torção do shank G·J/L (spec 2026-07-07)
SLIP_ONSET_PAI_HESS = 0.46     # Pre-factor de slip onset (Pai-Hess 2002)
THREAD_FLANK_ANGLE = np.deg2rad(30.0)  # ISO métrica
LOOSE_AMP_REF = 5e-4           # m — escala de referencia p/ loose_amp_exp (PR-21)


# ============================================================================
# Geometria e material
# ============================================================================

@dataclass
class JointGeometry:
    """Geometria invariante da junta + parafuso."""
    E: float = E_STEEL              # Pa
    A_s: float = 200e-6             # m² (área de tensão)
    L_eff: float = 0.060            # m (comprimento efetivo)
    d_2: float = 18.38e-3           # m (diâmetro de passo)
    pitch: float = 2.5e-3           # m
    r_bearing: float = 12e-3        # m (raio efetivo do bearing)
    A_contact: float = 1e-4         # m² (área nominal de contato bearing)
    # L2 (plano L1-L7 task-5, 2026-07-17): diâmetro do furo de folga / diâmetro
    # externo da arruela [m] — só usados por JointMaterial.kj_mode="pedersen"
    # (alpha=d_hole/d_nominal, beta=d_washer/d_nominal da forma de Pedersen).
    # 0.0 (default) = indisponível; kj_mode cai SILENCIOSAMENTE no k_j_init
    # atual quando qualquer um dos dois for 0 (fallback documentado/testado em
    # tests/test_l2_kj_law.py — nenhuma geometria existente na biblioteca os
    # preenche hoje, então o modo permanece opt-in até um caller os fornecer).
    d_hole: float = 0.0             # m
    d_washer: float = 0.0           # m

    @property
    def k_b(self) -> float:
        """Rigidez axial do parafuso [N/m]."""
        return self.E * self.A_s / self.L_eff

    @property
    def beta(self) -> float:
        """Ângulo da hélice [rad]."""
        return np.arctan(self.pitch / (np.pi * self.d_2))

    @property
    def lead_per_radian(self) -> float:
        """p/(2π) — translação axial por radiano de rotação [m/rad]."""
        return self.pitch / (2.0 * np.pi)

    @property
    def d_nominal(self) -> float:
        """Diâmetro NOMINAL do parafuso [m], invertido de d_2/pitch via ISO 724
        (d_2 = d − 0.6495·P ⇒ d = d_2 + 0.6495·P — mesma constante usada em
        todo o resto do repo, e.g. `solver_worker.d2 = d - 0.6495*p`). Esta
        dataclass só guarda d_2/pitch; `kj_from_geometry` (L2) precisa do
        diâmetro nominal, não do de passo."""
        return self.d_2 + 0.6495 * self.pitch


@dataclass
class JointMaterial:
    """Propriedades de material e contato das interfaces.

    Defaults calibrados (rev. 2026-05-18) contra M16 shear ±0.5mm 0.5Hz
    arruela nova (perfil 'nova' do joint_calibrations.json). Com estes
    defaults, os 5 tuners convergem para ~1.0 no fit nova baseline.
    """
    mu_thread: float = 0.15
    mu_bearing: float = 0.15
    # F3 2026-07-21 (prereg F3.2-CHU): µ_bearing(N) MEDIDO como input —
    # tupla de pares (N, µ) (ex. Chu 2026 Fig. 5 digitalizada). Presente ⇒
    # mu_bearing_eff interpola no ciclo e BYPASSA constante+dano (o µ medido
    # já contém a evolução). Vazio (default) = bit-idêntico. Idioma do
    # delta_spectrum: input de medição, NUNCA fittable, flui via per_case.
    mu_bearing_schedule: tuple = ()
    # Archard wear coeff — valor literatura pra boundary-lubricated steel.
    # Pre-displacement-mode era 5e-4 (compensando slip subdimensionado);
    # com slip correto em modo displacement-controlled, 1e-4 eh fisicamente
    # adequado pra boundary lub (K=1e-3 seria fretting severo).
    K_archard: float = 1e-4         # adimensional
    hardness: float = 2e9           # Pa
    # MERGE K/H (sec4.42 proposta (a), 2026-07-09): K_archard e hardness so
    # aparecem como RAZAO K/H no engine (WearLoss E ThreadFrettingLoss) =>
    # nao-identificaveis em separado (equifinalidade exata: dobrar ambos nao
    # muda NADA, bit-a-bit). k_wear_spec = K/H [1/Pa] e o parametro
    # IDENTIFICAVEL canonico. 0.0 (default) => usa K_archard/hardness legados
    # com a aritmetica ORIGINAL (bit-identical, backward-compat p/ .msd e
    # shared block); >0 => sobrepoe os legados nos dois mecanismos.
    k_wear_spec: float = 0.0        # 1/Pa — razao de wear especifica (0 = K/H legado)
    # Fretting de flanco de rosca dirigido pela amplitude de carga AXIAL (spec
    # 2026-07-06): fator geometrico/engajamento (flank-slip frac + area + projecao
    # flanco->axial), O(0.1-1). 0.0 = mecanismo OFF (backward-compat). Fitado
    # per-par ao Liu2017 axial (a "B2" adiada, procedencia = fitted).
    k_thread_fret: float = 0.0
    # DEPENDENCIA DE FREQUENCIA do fretting axial (spec 2026-07-09, sec4.39,
    # roadmap #9). O dado Li2022ti (M10, A_F=10kN, 10/15/20 Hz) mostra que a
    # perda por fretting CRESCE quando a frequencia CAI (10Hz -17.9% / 15Hz
    # -14.1% / 20Hz -8.9%; nota: "wear debris + spalling grows as frequency
    # DROPS") — mais tempo de dwell por ciclo => mais oxidacao/formacao de debris
    # => mais remocao de material por ciclo. Fator (f_ref_fret/freq)^fret_freq_exp
    # sobre d_fret: em f_ref_fret o fator=1; freq menor => fator>1. O expoente e'
    # LIDO do proprio sweep de frequencia (ln(perda_10/perda_20)/ln(20/10)~1.0 =>
    # perda~1/f), nao fitado ao MAE. So afeta o fretting axial (ThreadFrettingLoss,
    # ja gateado por A_F>0). fret_freq_exp=0 (default) => fator=1 (BIT-IDENTICAL,
    # freq-independente como antes). f_ref_fret so lido se exp!=0.
    fret_freq_exp: float = 0.0      # expoente de (f_ref/f); 0 = freq-independente (OFF)
    f_ref_fret: float = 15.0        # Hz — frequencia de referencia (per-rig; so lida se exp!=0)
    # ========================================================
    # L1 (plano L1-L7 task-3, 2026-07-16): canal INDEPENDENTE de desgaste de
    # flanco ~ AMPLITUDE de carga axial A_F, complementar ao k_thread_fret
    # acima (que e' hardcoded LINEAR em F_ax). Falsificacao-alvo
    # (MODEL_LEGITIMACY.md secao 4.6, roadmap #9): d(fim)/d(A_F) ~ 0 no modelo
    # hoje vs -2.216e-5/N no dado Liu2017. Parametrizado por PRESSAO de flanco
    # p_flank=F_0/A_s (nao forca) com expoente de amplitude AJUSTAVEL
    # flank_amp_exp (Liu 2020 sugere 1.5-1.6, super-linear). So atua em modo
    # FORCA (delta_amp is None) — delta_amp SEMPRE representa curso
    # TRANSVERSAL nesta convencao do engine (resolve_transverse_slip ignora
    # theta_load quando delta_amp e' dado), entao o canal nao tem sentido fora
    # do force-mode axial.
    # k_wear_flank [1/Pa]: SEMEADO do KB (kb.wear_spec_anchor("thread",
    # "35CrMo-SCM435") = 8.34e-15, Zhang 2019, EFA doi 10.1016/
    # j.engfailanal.2019.05.001) na CALIBRACAO (Task 4) — o engine NUNCA le o
    # KB (so constantes); aqui e' so o default inerte.
    # flank_amp_exp: default 1.0 (linear, backward-compat da FORMA — so tem
    # efeito com flank_wear_on>0); candidato de literatura 1.5-1.6 (Liu 2020).
    # flank_wear_on=0.0 (default) => canal OFF exato (bit-identical).
    # ========================================================
    flank_wear_on: float = 0.0      # 0 = OFF (bit-identical)
    k_wear_flank: float = 0.0       # 1/Pa — razao de wear especifica do flanco (KB Zhang2019)
    flank_amp_exp: float = 1.0      # expoente de amplitude (Liu2020 candidato: 1.5-1.6)
    # L1 v2 (F4, prereg B1-v3 2026-07-22): limiar de slip do flanco [m].
    # 0.0 = sem limiar (BIT-IDENTICO ao v1); >0 => wear ~ (s-s_crit)+^exp
    # (stick/shakedown abaixo, slope ingreme perto do limiar — resposta a
    # falsificacao T4). Fitavel per-rig junto de k_wear_flank.
    flank_s_crit: float = 0.0       # m
    # L1 v2 — rota TRANSVERSAL do canal de flanco (F4, 2026-07-22): zhang18/
    # zhang19/liu2020 (R5) perdem preload por desgaste de flanco de rosca SEM
    # rotacao, sob excitacao transversal disp-mode (zero rotacao MEDIDA nos 3
    # rigs; apparatus_notes/zhang.md: "gap forming at the worn thread flanks
    # ... not through any rotational back-off"). Mesma fisica do canal axial
    # (k_wear_flank/flank_amp_exp/flank_s_crit), com o slip de flanco = slip
    # transversal resolvido (slip_amp de resolve_transverse_slip). Switch
    # binario como flank_wear_on (fittable=False); 0.0 = OFF exato
    # (bit-identical; o canal L1 segue axial-force-mode-only por default).
    flank_transverse_on: float = 0.0
    # Greenwood-Williamson: k_j_ax(F_0) = k_j_init * (F_0/F_init)^alpha
    k_j_init: float = 4e9           # N/m
    alpha_GW: float = 0.5
    # ========================================================
    # L2 (plano L1-L7 task-5, 2026-07-17; roadmap #10 / MODEL_LEGITIMACY §4.8):
    # lei k_j(geometria, material) — substitui a constante k_j_init FIXA por
    # uma forma FÍSICA que escala com a geometria real do parafuso/grip/furo/
    # arruela (Pedersen 2008 Eq.31, primária; Wileman 1991, cross-check) —
    # fecha a falsificação "k_j fixo não escala com espessura de membro"
    # (Rousseau t10/12/14, MODEL_LEGITIMACY §4.8). kj_mode="" (default) =
    # comportamento atual (k_j_init como dado/fitado, sem mudança).
    # kj_mode="pedersen"|"wileman": no __init__ do analyzer, SE a geometria
    # fornecer d_hole/d_washer (>0, ver JointGeometry), k_j_init é SUBSTITUÍDO
    # 1x por kj_from_geometry(...) (calibration/library_common.py) — daí em
    # diante o resto do engine (k_j_ax GW softening, [K] matrix, k_torsional
    # legacy) usa esse valor físico normalmente, sem mudança de forma. Se a
    # geometria NÃO fornecer furo/arruela (default 0.0 = indisponível), cai
    # SILENCIOSAMENTE no comportamento atual (k_j_init inalterado) —
    # documentado, testado (tests/test_l2_kj_law.py). Mode desconhecido/typo
    # também cai no default (mesmo idioma de k_tr_mode/conform_driver).
    kj_mode: str = ""
    # Dependência de CARGA de Φ via forma ELÍPTICA de Grosse (dissertação
    # 1990, colapso de rigidez ~50x próximo da separação) — 1 parâmetro
    # (deformação/carga crítica de separação, POR-JUNTA — não universal). Só
    # afeta `U_loaded` (o ÚNICO local do engine onde Φ particiona um F_ax_ext
    # explícito entre parafuso/junta; `RotationalLooseningLoss` usa Phi_ax/
    # Phi_tr como GANHOS do torque de afrouxamento — forma diferente, não
    # tocada por este campo). F_m/F_i = 1 − sqrt(max(0, 2·λ−λ²)), λ = F_ax_ext
    # / (phi_load_dep·F_i) [F_i = state.F_0 corrente]. λ=0 (sem carga extra)
    # ⇒ fração=1 (F_joint=F_i, idêntico ao caso linear em F_ax_ext=0); λ→1
    # (carga extra perto do crítico) ⇒ fração→0 (colapso do lado do membro);
    # λ clipado em [0,1] (além do crítico a elipse fechada reapareceria,
    # não-físico). 0.0 (default) = OFF exato, usa a partição LINEAR (1−Φ)
    # atual (backward-compat bit-identical).
    phi_load_dep: float = 0.0
    # ========================================================
    # Embedding (Norton): δ_emb(N) = δ_∞ (1 − exp(−N/N_emb))
    # emb_depth bumped 12e-6 -> 30e-6 m (rev. 2026-06-20): a queda inicial
    # ingreme do M16 shear excede a asintota de 12um; com 30um o nova
    # converge pra k_emb_scale~1.1 (interpretavel) em vez de 2.66, e os
    # outros perfis melhoram (sobretorque 0.036->0.017) sem saturar.
    # ΔF_emb_max = k_b*30um = 18.8 kN ~ 38% de F0=50kN.
    emb_depth: float = 30e-6        # m
    N_emb: float = 50.0             # ciclos
    # RELOGIO DE ASSENTAMENTO DEPENDENTE DE DESLOCAMENTO (2026-08-14, forma
    # assinada; `New_Theory/lei_relogio_embedding_por_deslocamento.md`):
    #
    #     N_emb_eff(delta) = N_emb * (emb_clock_delta_ref / delta_amp)
    #
    # ⚠️ O EXPOENTE E' 1 E NAO E' AJUSTAVEL — ele vem do mecanismo, nao de fit:
    # se o assentamento se esgota apos uma DISTANCIA DE SLIP ACUMULADA S
    # (achatamento de asperezas ate a area real de contato saturar), entao
    # N_emb = S/(slip por ciclo) e slip por ciclo ~ delta, logo N_emb ~ 1/delta.
    # Deixa-lo livre seria transformar uma consequencia em parametro.
    #
    # Medido no CHU_2026 (Junker, deslocamento imposto): delta=1,0mm pede
    # N_emb=400 e delta=0,5mm pede 800 — razao 2 para razao 2, o expoente cai em
    # 1 sozinho. Predicao ZERO-REFIT em delta=0,4 e 0,7mm melhorou 4 de 4 curvas
    # que nao entraram no ajuste (sigma -12 a -27%).
    #
    # ⚠️ IRMA da rho-unificacao (§4.18), NAO substituta: aquela modula o ALVO do
    # embedding pela razao de FORCA (rho = F_ax_amp/F0_init); esta modula o
    # RELOGIO pelo DESLOCAMENTO. So e' necessaria — e so e' identificavel — em
    # rig de deslocamento imposto que varre delta com F_amp FIXO, que e' a
    # assinatura do Junker. Em rig de forca, ou com delta unico, ela apenas
    # re-escala N_emb e NAO e' falsificavel; por isso o default e' OFF e a
    # aplicacao e' per-fonte.
    #
    # 0.0 (default) = OFF EXATO (bit-identico ao comportamento anterior).
    emb_clock_delta_ref: float = 0.0   # m (ex.: 1.0e-3 = referencia a 1,0 mm)
    # Saturacao de embedding dependente da pressao de APERTO (spec 2026-07-08): o
    # assentamento residual cai com F0_init (pre-conformacao no torque). Reescala o
    # asintota por S=min(1,(p_ref_emb/p_init)^exp), p_init=F0_init/A_contact (fixo
    # no run; NUNCA F_0 corrente -> sem feedback). emb_conform_exp=0 => S=1 exato
    # (inerte, bit-identical; p_ref_emb nao lido). Per-rig, como emb_depth/c_bend.
    emb_conform_exp: float = 0.0    # n — expoente de pressao [-] (0 = OFF)
    p_ref_emb: float = 1.5e8        # Pa — pressao de referencia (per-rig; so lida se exp>0)
    # RAMO OPOSTO da linha acima (prereg 2026-08-16-lu2024-embedding-dirigido-
    # por-pressao). O `emb_conform_exp` modela PRE-CONFORMACAO: aperto maior ja
    # achatou mais aspereza no torque, logo sobra MENOS residuo ciclico — e sua
    # consequencia declarada e' "fracional cai mais rapido que 1/F0". Este campo
    # modela a fisica COMPLEMENTAR e de sinal contrario: o achatamento plastico
    # e' DIRIGIDO POR PRESSAO, entao abaixo de uma pressao de referencia o
    # escoamento e' menor e o reservatorio de encaixe e' mais RASO.
    #     S_p = min(1, (p_init / p_ref_emb) ** emb_pressure_exp)
    # Os dois compoem por multiplicacao (fisicas distintas, gates ortogonais) e
    # ambos leem p_init = F_0_init/A_contact — NUNCA o F_0 corrente, senao o
    # encaixe realimentaria o proprio decaimento.
    # O `min(1, .)` e' o que da ISOLAMENTO ESTRUTURAL: toda curva com
    # p >= p_ref fica em S_p = 1.0 EXATO, bit-a-bit, sem depender de tolerancia.
    # emb_pressure_exp <= 0 => 1.0 exato (inerte, backward-compat bit-identico).
    emb_pressure_exp: float = 0.0   # n — expoente de pressao do ramo DIRIGIDO (0 = OFF)
    # Pre-conformacao do reservatorio LENTO (spec 2026-07-08 slow-tail): o que o
    # modelo chama de "creep" nesta classe de junta e' assentamento de interface
    # log-t; o aperto pre-conforma esse reservatorio tambem, com expoente MAIS
    # FRACO que o rapido (escalas mais profundas). Dado Liu2017: perda lenta
    # ABSOLUTA ~F0^-1 => fracional ~F0^-2 => n_slow~2 (vs n_fast~3-4), pinado
    # pela decomposicao lenta (feature independente do fast-drop). Reusa
    # p_ref_emb (ancora). creep_conform_exp=0 => S=1 exato (inerte). Per-rig.
    creep_conform_exp: float = 0.0  # n_slow — expoente do canal lento (0 = OFF)
    # UNIFICACAO rho (estudo de variaveis item 1, spec 2026-07-08): reservatorio
    # de assentamento consumido escala com a AMPLITUDE RELATIVA ciclica
    # rho = F_ax_amp/F_0_init: S_rho = min(1,(rho/rho_ref_emb)^emb_amp_exp).
    # LIDO dos DOIS sweeps do Liu2017 (fast-loss ~ rho^3.4; 5 pares, 4 em +-5%)
    # — a "pre-conformacao por pressao" (emb_conform_exp) era esta variavel em
    # A_F fixo (reducao de variavel: usar UMA das duas por rig). So atua com
    # componente AXIAL (transversal: F_ax~0 => S=1). emb_amp_exp=0 => S=1 exato
    # (inerte). Fisica: shakedown/plasticidade ciclica de asperezas.
    emb_amp_exp: float = 0.0        # q_amp — expoente da amplitude relativa (0 = OFF)
    rho_ref_emb: float = 0.667      # rho de referencia (ancora per-rig; so lida se exp>0)
    # ASSENTAMENTO PROPORCIONAL A CARGA (estudo de variaveis, falsificacao Lu
    # fig20 2026-07-08): o fast-drop fracional do DADO e F0-FLAT (~0.55 com F0
    # 2.1->15 kN, 7x) enquanto reservatorio de profundidade ABSOLUTA preve
    # fracao ~1/F0 (1.39->0.195) — lei de escala falsificada pela varredura.
    # Componente ∝ carga: delta_target += emb_load_frac*F_0_init/k_b => fracao
    # de queda rapida CONSTANTE = emb_load_frac. Fisica: profundidade do leito
    # de asperezas escala com o clamp (o proprio f_Z VDI cresce com a classe de
    # carga); mesma familia da unificacao rho (reservatorio ∝ severidade — aqui
    # a severidade e a propria carga de aperto). 0 = OFF (bit-identical).
    emb_load_frac: float = 0.0      # fracao de F0 consumivel por assentamento ∝ carga
    # Rigidez de CISALHAMENTO do membro em serie com k_tr (item 2, HDPE §4.20):
    # k_member_shear = G_membro*A_shear/t (N/m; o harness computa por-caso do
    # par per-rig G*A). Membro complacente absorve o curso imposto => menos
    # slip na interface (t14 HDPE nao colapsa; so-flexao preve ordem invertida
    # ~1/L^3). 0 = OFF (aco: termo desprezivel — nao setar).
    k_member_shear: float = 0.0     # N/m — 0 = OFF (bit-identical)
    # FATOR DE DWELL do dano (estudo de variaveis, par Yang 5/10Hz 2026-07-08):
    # dD *= (f_ref_dmg/f)^p — fretting-corrosao: dose de oxido por ciclo escala
    # com o tempo de contato (freq menor = mais dano/ciclo). No dado Yang as
    # curvas ~coincidem no TEMPO ate o 5Hz entrar em colapso terminal que o
    # 10Hz nunca alcanca (e amp0p4-5Hz com 2000s tampouco => dose x dwell, nao
    # so tempo). p=0 => 1 exato (inerte). f_ref = ancora per-rig.
    dmg_dwell_exp: float = 0.0      # p — expoente de dwell do dano (0 = OFF)
    f_ref_dmg: float = 10.0         # Hz — frequencia de referencia (ancora)
    # FREE-SPIN pos-arresto (sec4.23): fracao do drive rotacional nao-arrestado
    # que continua como rotacao LIVRE (sem drenar preload) apos o arrest gate
    # fechar. Nomeada pelo confronto theta(N) Rousseau (steel_t10: 3.3x mais
    # theta medido do que a perda explica). Preload BIT-IDENTICO (dF_0 so na
    # parte arrestada); muda apenas theta_loose e dE. 0 = OFF.
    free_spin: float = 0.0          # fracao [0..1] — 0 = OFF (bit-identical)
    # FREE-SPIN CINEMATICO (sec4.56, 2026-08-19): fracao da rotacao RELATIVA
    # porca-parafuso do kernel graded_scrit que NAO drena preload. Fisica: o
    # dreno real por rotacao e' a rigidez de dreno do LACO (serie parafuso +
    # membro + compliances de interface), menor que o k_b puro que a helice do
    # engine usa; o dado publica a lei — Rousseau 2025 Fig. 5 (aco) da dF/dtheta
    # = 920/894 N/deg (t10/t12, r2 0.9997/0.9969) contra k_b*lead = 3278 —
    # constante POR JUNTA no aco. ERRATA 2026-08-19 (mesma noite): o "118/117
    # N/deg do HDPE" da 1a leitura era ARTEFATO da extracao vetorial da fig4
    # (truncada; re-extracao do PDF calibrada por ticks da theta_fim
    # 21,27/12,65/2,16 deg) — o HDPE real da 138/207 N/deg (t10/t12), ou seja
    # VARIA com a espessura; a lei-de-junta so esta demonstrada no aco.
    # LIDA de dois observaveis publicados: free_spin_kin = 1 - (dF/dtheta)_med
    # / (k_b * lead_per_radian). theta_loose e dE ficam com a rotacao TOTAL (o
    # filete atrita na rotacao relativa inteira; dE suprido por W_ext, mesmo
    # padrao do free_spin pos-arresto). SO o ramo graded_scrit le. Clamp
    # [0, 0.999]. 0 = OFF (bit-identical).
    free_spin_kin: float = 0.0
    # Dissipacao VISCOELASTICA do membro (sec4.25): W_m = pi*eta*F_tr^2/k_member
    # por ciclo — polimero lossy dissipa no proprio membro o que a interface nao
    # contabiliza (loops medem 7-8x o modelo). SO energia (F_0 intocado). 0=OFF.
    member_loss_eta: float = 0.0    # fator de perda do membro (por-material)
    # BEDDING SLIP-GATED (sec4.29): gate (slip/(slip+delta_t))^q sobre o
    # reservatorio FRACIONAL emb_load_frac — bedding vibracao-dirigido exige
    # escorregamento (Jiang porca-colada); sub-limiar assenta so a
    # profundidade estatica. 0 = OFF (bit-identical).
    emb_slip_gate: float = 0.0      # expoente q do gate de slip do bedding (0=OFF)
    # GATE DE REGIME DE AMPLITUDE nos relogios de ESTAGIO I (PR-3 2026-08-01,
    # forma B do N95 do LIU_2025 — prereg specs/2026-08-01-s1-amp-gate-pr3):
    # transicao regime-parcial -> gross-slip. Abaixo de dref os relogios de
    # bedding E creep-de-interface quase param (assentamento vibracao-dirigido
    # exige escorregamento macro); acima, taxa plena. Hill NITIDO — o dado
    # (N95 850x de span em 3.2x de amplitude, Fig. 4 D-N) exige expoente
    # efetivo ~11 que nenhum campo existente fornece (candidato A falsificado
    # no G1, 1/6). g = floor + (1-floor)*d^p/(d^p+dref^p) sobre delta_amp;
    # multiplica SO o d_delta de Embedding/Creep (dF_0 e dE derivam dele =>
    # conservacao intacta). delta_amp None (modo forca) => g=1.
    s1_amp_gate_dref: float = 0.0   # amplitude de transicao [m] (0 = OFF exato)
    s1_amp_gate_p: float = 8.0      # nitidez Hill (so lido se dref > 0)
    s1_amp_gate_floor: float = 0.0  # taxa remanescente sub-limiar [0,1)
    # P-9 (2026-08-09, assinada): FREQUENCIA no relogio de Estagio I. Irmao do
    # gate de amplitude acima, no MESMO sitio (`d_delta` do EmbeddingLoss), e com
    # a MESMA lei que o D-V ja assinou para o canal de flanco:
    # `(f_ref/freq)^n`. Fisica: se o assentamento tem componente dependente do
    # TEMPO (consolidacao de asperezas), frequencia maior => menos tempo por
    # ciclo => menos embedding por ciclo.
    # ⚠️ So' e' identificavel onde a FONTE varre frequencia: em fonte
    # mono-frequencia isto apenas re-escala `N_emb` e nao e' falsificavel — por
    # isso o default e' OFF e a aplicacao e' per-fonte.
    s1_freq_exp: float = 0.0        # expoente n (0 = OFF exato, bit-identico)
    s1_freq_ref: float = 1.0        # f_ref [Hz]; em f_ref o fator e' 1 exato
    # RUNNING-IN do wear (sec4.26/4.29): K_eff = K*(1+(k_run-1)*e^{-N/N_run})
    # — wear medido sublinear ~N^0.53 (Zhang2019); V1 tinha K_running_in.
    k_wear_running: float = 1.0     # multiplicador em N=0 (<=1 = OFF)
    N_wear_run: float = 200.0       # ciclos do running-in (so lido se k>1)
    # GATILHO DE CRITICALIDADE do crash (sec4.30, L14; 2 falsificacoes: joelho
    # estagio-3 Bauer fig8 + Liu2025 flat-early). O loosening fica SUPRIMIDO
    # enquanto F_0 esta alto (plato: embedding/wear trazem F_0 ao limiar) e
    # DISPARA runaway quando F_0/F_0_init cruza crash_trigger_frac — reproduz o
    # joelho tardio. Gate Hill: g = r^k/(r^k + (F_0/F_0_init)^k), r=trigger_frac.
    # Keyed em F_0/F_0_init (NAO em Q/muF0k, que e' F0-independente em disp-mode).
    # crash_trigger_frac<=0 => 1.0 exato (inerte, crash gradual atual).
    crash_trigger_frac: float = 0.0        # fracao de F0 do joelho (0 = OFF)
    crash_trigger_sharpness: float = 8.0   # k do gate Hill (so lido se frac>0)
    # ENERGIA DE PARTIAL-SLIP (dE_partial, spec 2026-07-08; dupla falsificacao
    # §4.25 loops + §4.31 joelho Bauer). O anel de micro-slip Cattaneo-Mindlin
    # dissipa energia por ciclo mesmo sem gross slip: dE = k_partial_slip·
    # g_partial·4·mu·F0·delta_t. Alimenta W_slip_acc (dano dispara no plato) +
    # budget de energia (fecha os loops). 0 = OFF exato (bit-identical).
    k_partial_slip: float = 0.0     # coef. da energia de partial-slip (0 = OFF)
    # ONSET FISICO CONTINUO do dano (spec 2026-07-08): gateia dD pela fracao de
    # gross-slip g_gross=slip/(slip+delta_t) ^ dmg_gross_exp — a razao fisica
    # s_a/s_crit (s_crit=delta_t∝F0, cai com F0). Substitui o limiar W_crit por
    # um onset CONTINUO e F0-dependente => fig6/fig8 = mesma fisica, joelho
    # continuo na super-criticalidade. 0 = usa W_crit legado (bit-identical).
    dmg_gross_exp: float = 0.0      # expoente do onset por gross-slip (0 = OFF)
    # Creep LOG-T (assentamento de interface, NAO Norton-Bailey -- ver o
    # docstring de CreepLoss p/ a forma exata + a coincidencia feliz com a
    # regressao de faiamento do Nah 2014, KB creep_class):
    # δ_creep(t) = C_creep · F_0 · ln(t/t_0 + 1).
    # FIX CLARO: 1e-8 era ~200x demais (k_creep_scale=0.006 na primeira calibracao).
    # 5e-11 == 1e-8 x 0.005, valor mais defensavel fisicamente pra creep de
    # aco a temperatura ambiente.
    C_creep: float = 5e-11          # m / log-decade × Pa
    t_0: float = 1.0                # s
    # Forma SATURANTE opt-in (Alamos 2021/2022, creep de contato de 1os
    # principios; plano L1-L7 task-7, 2026-07-17): substitui a lei log-t
    # (ilimitada) por δ_max·(1−exp(−(t/creep_t_c)**creep_alpha_sat)) — ver
    # CreepLoss.rate() p/ a derivacao de δ_max a partir do MESMO C_creep
    # (continuidade dimensional). creep_mode e' mode switch (string), NAO
    # fittable — mesmo idioma de kj_mode/conform_driver/k_tr_mode (mode
    # switches nunca entram no PARAMETER_REGISTRY como fittable=True).
    # "" (default) = log-t atual, bit-identico.
    creep_mode: str = ""            # ""=log-t (default) | "saturating"=Alamos
    creep_t_c: float = 0.0          # s — constante de tempo saturante (0=OFF)
    creep_alpha_sat: float = 1.0    # expoente de forma (stretched exponential)
    # Ganho do loosening transversal: quando F_tr > F_slip,
    # Phi_tr_active = tr_loose_gain * Phi_tr_correction.
    # Antes era hardcoded 0.95 dentro de RotationalLooseningLoss.rate().
    # FIX MODERADO: ~2x do valor original (era 0.95, agora 2.0) — calibracao
    # original saturou em 5x mas isso ja indica amplificacao dinamica
    # significativa em ensaio Junker; valor moderado deixa espaco pro
    # Phi_tr_correction tunear no range [0.5, 3.0].
    tr_loose_gain: float = 2.0
    # Rayleigh damping
    rayleigh_alpha: float = 0.01    # 1/s — proporcional a [M]
    rayleigh_beta: float = 1e-5     # s — proporcional a [K]
    # Effective mass for [M]
    m_x: float = 0.5                # kg
    m_y: float = 0.5
    I_theta: float = 1e-5           # kg·m²

    # ========================================================
    # CALIBRATION TUNERS — constantes de ajuste pos-calibração
    # ========================================================
    # Multiplicadores aplicados sobre os rates físicos. Default
    # 1.0 = usa o modelo físico puro. Ajustar entre 0.1 e 10
    # após calibração contra dados experimentais (per material,
    # per joint, per geometria).
    #
    # ax: aplicado quando loading é axial (F_ext alinhado ao
    #     eixo do parafuso)
    # tr: aplicado quando loading é transverso (perpendicular)
    # Para loading combinado, blend pelo ângulo θ:
    #     k_eff = k_ax · cos²θ + k_tr · sin²θ
    # ========================================================
    # ESTAGIO B (2026-07-09): a camada de TUNERS (k_emb_scale, k_creep_scale,
    # k_wear_scale_ax/tr, k_loose_scale_ax/tr, Phi_ax/tr_correction,
    # k_damage_scale) foi REMOVIDA. Os mecanismos leem so constantes fisicas; a
    # semantica dos tuners foi foldada nelas (emb_depth, C_creep, K_archard/
    # k_wear_spec, tr_loose_gain, c_D) — .msd/payloads legados sao traduzidos
    # por calibration.tuner_shim.translate_legacy_tuners na fronteira de consumo.
    # Renovacao de embedding no re-aperto (spec 2026-07-07): em retighten(),
    # delta_emb <- delta_emb*(1 - k_emb_renew*D). Superficies danificadas expoem
    # capacidade de assentamento fresca ~ D. 0.0 = inerte (re-aperto mantem
    # delta_emb; backward-compat exato). So atua em retighten(), nunca em step_cycle.
    k_emb_renew: float = 0.0
    # Galling de flanco de rosca no re-aperto (spec 2026-07-07): superficie danificada
    # eleva o atrito de rosca VISTO NO APERTO (mu_thread_tighten_eff=mu_thread*(1+k_gall*D))
    # => nut factor sobe => F0 recuperado cai. So atua em tightening_torque (re-aperto),
    # nunca em step_cycle/T_resistance => colapso do reaperto (k_dmg_mu/k_dmg_wear) intacto.
    # Sinal OPOSTO ao k_dmg_mu (flanco de rosca vs face de bearing). 0.0 = inerte.
    k_gall: float = 0.0
    # RELOGIO POR CONTAGEM DE REAPERTOS (D-J 2026-08-05, prereg
    # specs/2026-08-05-liu2022-relogio-por-reaperto). A perda dirigida por SLIP
    # (wear + afrouxamento) e' multiplicada por `(1 + retight_loss_gain) **
    # state.n_retighten`. Fisica: num protocolo que NAO solta o parafuso, a
    # interface segue engajada e progressivamente danificada, logo cada ciclo
    # apos o k-esimo reaperto escorrega mais. Medido no LIU_2022: a perda POR
    # ESTAGIO do dado cresce ~1,8-1,9x por evento nas DUAS cadeias que nao
    # soltam (fig8 seco 1,75x/2,03x; fig7a oleo 1,49x/2,03x) e e' plana ou
    # DECRESCENTE nas duas que soltam (fig6a 1,09/1,17; fig6b 0,75/0,93).
    #
    # NAO age no embedding: assentamento e' conformacao plastica, que DECRESCE
    # com carregamento repetido — crescer nele seria fisica ao contrario. O
    # embedding no reaperto e' tratado por `k_emb_renew`.
    #
    # 0.0 = OFF EXATO (fator 1.0 para qualquer n) e, com n_retighten=0, e'
    # inerte mesmo com ganho>0 — e' isso que protege o estagio VIRGEM por
    # construcao. Difere do `k_gall`, que so age em `tightening_torque` (e e'
    # INERTE onde o F0 por estagio e' lido do dado — medido 2026-08-05).
    retight_loss_gain: float = 0.0
    # QUEDA no 1o reaperto (D-K 2026-08-05). O D-J falsificou a composicao
    # anterior por ALGEBRA: o fator NECESSARIO e' < 1 em todos os estagios
    # reapertados (0,203 / 0,355 / 0,719 no fig8) e CRESCE para 1, mas um
    # multiplicador (1+g)^n tem contradominio [1,inf) e comeca ACIMA de 1.
    # Imagem espelhada da falsificacao de 2026-08-02: gates com (0,1] so
    # sabem atrasar; amplificador com [1,inf) so sabe amplificar. O dado
    # pede operador que ATRAVESSE o 1:
    #     fator(0) = 1 ; fator(n>=1) = base * (1+gain)^(n-1)
    # 1.0 = OFF exato. Fisica: o 1o reaperto assenta a interface (perde
    # MUITO menos) e cada reaperto seguinte a re-danifica (recupera ~g).
    retight_loss_base: float = 1.0
    # SATURACAO DO CANAL DE FLANCO por profundidade restante (D-Q
    # 2026-08-05). Mesma estrutura state-based que o `EmbeddingLoss`
    # recebeu em 2026-07-02: o incremento depende da profundidade que
    # AINDA FALTA, nao do relogio.
    #     d_w *= max(0, 1 - state.delta_thread_fret / flank_fret_depth)
    # Fisica: o fretting de flanco remove material ate a folga acomodar o
    # movimento; entao o contato re-conforma, a area cresce, a pressao cai
    # e o transporte liquido para — o regime de SHAKEDOWN que o docstring
    # de `flank_wear_from_slip` ja cita (Mantyla 2020 / Juoksukangas 2016).
    # Motivacao medida (LI_2022): o dado SATURA e o modelo nao (residuo
    # +0,0466 em 20k, cruza zero em 200k, -0,0441 em 330k; 49,7 % da
    # variancia nos 2 pontos tardios), e `delta_thread_fret` JA era estado
    # acumulado que a lei nunca lia de volta.
    # 0.0 = OFF EXATO (sem fator).
    flank_fret_depth: float = 0.0   # m — profundidade-alvo do fretting de flanco

    # ========================================================
    # SURFACE DAMAGE (reaperto/TP7). Inativo por default
    # (c_D=0, k_dmg_mu=0) => engine reproduz comportamento atual.
    # Perfis reaperto/reusada ligam via calibracao.
    # ========================================================
    c_D: float = 0.0            # taxa de crescimento do dano [-]
    W_ref: float = 1.0e4        # escala de energia de referencia [J]
    k_dmg_mu: float = 0.0       # acoplamento dano->perda de atrito [-]
    k_dmg_wear: float = 0.0     # acoplamento dano->amplificacao de wear [-]
    # AMPLIFICADOR TARDIO AGNOSTICO DE CANAL (PR-3 2026-08-01, prereg
    # specs/2026-08-01-amplificador-tardio-pr3): dF_0_total *= (1+k_dmg_all*D).
    # Motivo de existir: a classe "aceleracao tardia" (7 fontes, 21 curvas —
    # o dado desaba no fim 2x a 225x mais rapido que o modelo) NAO tem
    # mecanismo no engine. Toda a familia de gates Hill (slip_onset,
    # conformation, slip_regime, self_locking, crash_trigger) tem
    # contradominio (0,1] — so ATRASA. O unico amplificador existente
    # (k_dmg_wear) multiplica o WEAR, que esta morto em 4 das 5 fontes da
    # classe (LIU_2025 e' 83% fadiga, JCSR 82% creep). Este multiplica o
    # TOTAL: nao precisa identificar o canal dominante — que MUDA por fonte —
    # e por isso e' robusto onde um amplificador por canal seria fragil.
    # dF_0 SIM, dE NAO (mesmo padrao do k_dmg_wear): a energia dissipada
    # segue sendo o trabalho real e a perda extra de preload vai por
    # U_released; amplificar dE junto quebra a conservacao (~40% de
    # residual, medido em 2026-06). 0.0 = OFF EXATO (bit-identical).
    k_dmg_all: float = 0.0      # acoplamento dano->amplificacao de TODA perda
    # AMPLIFICADOR COM INTERRUPTOR (emenda do mesmo PR-3, 2026-08-01). O
    # k_dmg_all acima FALHOU o gate de classe por PERFIL, nao por magnitude:
    # D cresce gradual (0->0.9) e amplificar a curva INTEIRA destroi o inicio
    # (medido: +53%/+119%/+397% de MAE em CHU/YANG_2019/SUN). O perfil certo
    # ja existia no crash_trigger (interruptor Hill nitido em F_0/F_0_init:
    # ~0 cedo, ~1 tarde) — mas com sinal errado (<=1, so suprime). Esta e' a
    # INTERSECAO das duas medicoes: amplificar (>1) com o interruptor
    # (tardio) em vez do acumulador (gradual).
    #   dF_0_total *= (1 + k_late_amp * g_switch)
    #   g_switch = ft/(ft + (F_0/F_0_init)^k)   <- o MESMO g do crash_trigger
    # Reusa crash_trigger_frac/sharpness (limiar de perda de auto-travamento,
    # significado fisico ja estabelecido). 0.0 = OFF EXATO (bit-identical);
    # exige crash_trigger_frac > 0 (sem limiar nao ha interruptor).
    k_late_amp: float = 0.0     # amplificacao tardia sobre o TOTAL da perda
    # Gate de ONSET do dano (predictive trigger, spec 2026-07-05): D so cresce
    # depois que o trabalho de slip cru acumulado (W_slip_acc, ja gross-slip-
    # gated) cruza W_crit. W_crit=0 => gate transparente (backward-compat).
    W_crit: float = 0.0              # J — dose critica de fretting p/ onset (0 = off)
    dmg_onset_sharpness: float = 4.0  # k do Hill (= slip_onset_sharpness)
    # Regime de slip (spec 2026-07-05): k_tr_mode "axial_frac" (default, atual =
    # 0.3*k_j_init, delta_t~0, tudo gross slip) | "bending" (rigidez de FLEXAO do
    # parafuso c_bend*E*I/L^3 ~ 1e7 -> delta_t~0.3mm, prop F0*L^3/(E*d^4)). Opt-in.
    k_tr_mode: str = "axial_frac"
    c_bend: float = 1.0              # fator de contorno/compliance calibrado aos amplitude
                                     # sweeps (2026-07-05: acc balanceada 67%; so usado em bending)
    # Acoplamento loosening<->regime de slip (spec 2026-07-06): "off" (default,
    # loosening usa o criterio de forca atual = backward-compat) | "gross_fraction"
    # (loosening gateado pela fracao de gross-slip do curso g=slip/(slip+delta_t)).
    # So faz sentido com k_tr_mode="bending"; force-mode (slip None) => 1.0.
    loosening_slip_coupling: str = "off"
    # Rigidez torsional do loosening (spec 2026-07-07, #10 / §4.8): "legacy"
    # (default, k_torsional=k_j_init*d_2/2 ~2e7 -> backward-compat bit-identical) |
    # "bolt_torsion" (fisica: k_torsional=eta_loose*G*J/L_eff, J=pi*d_2^4/32 ~4e3,
    # ~5000x menor -> o runaway T_resist~F_0 que ja existe consegue disparar). So
    # faz sentido com o gate de onset ligado (loosening_slip_coupling=
    # "gross_fraction" + k_tr_mode="bending"), senao dispara em toda junta que escorrega.
    loose_torsion_mode: str = "legacy"
    # Eficiencia de ratcheting / travamento torsional efetivo [-]. So usado em
    # loose_torsion_mode="bolt_torsion" (shank nu eta=1 colapsa rapido demais ~25
    # ciclos; eta~7-15 estica pro colapso observado ~180). Per-par, O(1-10), analogo
    # a tr_loose_gain. Nao lido em "legacy" => default irrelevante p/ compat.
    eta_loose: float = 1.0
    # Arresto do runaway de loosening por nucleo auto-travado (spec 2026-07-07,
    # roadmap #4): F_min = loose_arrest_floor·F_0_init e' o clamp residual que o
    # ratcheting NAO drena (stick core). self_locking_gate=max(0,1-F_min/F_0) gateia
    # d_theta => o runaway vira S-curve com ponto fixo ESTAVEL em F_min. 0.0 = inerte
    # (gate=1, runaway atual, backward-compat). O(0.05-0.10) per-par. Torna o
    # loose_torsion_mode="bolt_torsion" ADOTAVEL (remove o over-collapse do #10).
    loose_arrest_floor: float = 0.0
    # EXPOENTE da aproximacao ao piso de arresto (prereg grupo A, 2026-07-27):
    # g = max(0, 1 - F_min/F_0) ** arrest_approach_exp. O gate ja era suave; o
    # que faltava era o EXPOENTE. exp>1 mata a taxa mais cedo conforme F_0 se
    # aproxima do piso => DESACELERACAO ao plato em vez de aproximacao linear.
    # Redistribui perda do inicio para o fim da curva SEM tocar no nivel (que
    # segue sendo loose_arrest_floor, per-par e lido do dado). Diagnostico que o
    # motivou: New_Theory/kernel_diagnostic_2026-07-27.md — 13 curvas em 4 rigs
    # independentes (Chu2026/Yang2019/Karlsen/Zhang2006) com o MESMO perfil de
    # residuo detrendado (r=0.90-1.00): colapsa cedo demais, trava tarde demais.
    # 1.0 = expressao anterior, BIT-IDENTICA (early-return explicito no gate, sem
    # depender de pow(x,1.0)==x do libm). Adimensional; forma, nao unidade.
    arrest_approach_exp: float = 1.0
    # TAXA RESIDUAL SUB-ARRESTO (prereg 2026-08-15-lei-de-taxa-rotacional).
    # O gate acima ZERA em F_0 -> F_min: o canal rotacional MORRE no piso e o
    # ponto fixo e' absoluto. Medido no ICMEZ_2025 (item Q): o dado ATRAVESSA
    # o piso adotado (0,308) e segue caindo ate 0,223 mantendo ~50% da taxa de
    # meio, enquanto o modelo achata em 0,29 (gate = 0,0000 medido no sitio).
    # O engine so oferecia o binario arresto/runaway (piso=0 => colapso, MAE
    # x5). Este campo poe o MEIO-TERMO: abaixo do limiar o canal retem uma
    # FRACAO da sua propria taxa inicial em vez de morrer, e o piso deixa de
    # ser barreira absoluta para virar joelho.
    #   g = max(loose_arrest_residual * g0, 1 - F_min/F_0),  g0 = g(N=1)
    # Leitura fisica: o nucleo auto-travado de Cattaneo-Mindlin nao e' rigido —
    # cede lentamente sob ciclagem continuada. 0.0 (default) = expressao
    # anterior, BIT-IDENTICA (early-return explicito). Adimensional, [0,1).
    loose_arrest_residual: float = 0.0

    # ========================================================
    # Incubacao do colapso slip-driven (estagio I de Jiang). Os
    # mecanismos dirigidos por slip transverso (wear + loosening
    # rotacional) ficam suprimidos ate o trabalho de slip
    # acumulado (state.W_slip_acc) cruzar slip_onset_W, via um
    # gate Hill de nitidez slip_onset_sharpness. Reproduz o plato
    # inicial (3 estagios: plato -> queda -> saturacao).
    # slip_onset_W=0 => sem incubacao (gate=1, backward-compat).
    # ========================================================
    slip_onset_W: float = 0.0       # J — limiar de slip acumulado p/ onset
    slip_onset_sharpness: float = 4.0  # expoente do gate Hill [-]

    # ========================================================
    # Conformacao dependente de pressao (sobretorque, spec 2026-07-04).
    # W_conf cresce do trabalho de slip cru ponderado por (p/p_ref)^n
    # (p = F_0/A_contact); conformation_gate = W_conf_ref/(W_conf+W_conf_ref)
    # suprime a perda de preload slip-driven (wear + loosening) conforme o
    # contato de alta pressao se conforma. Pressure-gated => inerte em baixa
    # pre-carga. W_conf_ref<=0 => gate=1 (inativo, backward-compat exato).
    # ========================================================
    W_conf_ref: float = 0.0             # J — escala de conformacao (0 = off)
    conform_pressure_exp: float = 1.0   # n — expoente de pressao [-]
    p_ref_conform: float = 5.0e8        # Pa — pressao de contato de referencia
    # driver do conformation_gate (spec §7): "raw" = monotonico (acumula o
    # trabalho de slip cru; default, backward-compat bit-identical); "effective"
    # = auto-limitante (pondera o incremento pelo gate de inicio-de-ciclo =>
    # plateau <1, nao equilibrio verdadeiro c*<1 — cf. MODEL_LEGITIMACY §4.9).
    conform_driver: str = "raw"

    # ========================================================
    # Regime de slip Cattaneo-Mindlin (spec 2026-07-07): lei
    # partial<->gross slip r=Q/(mu*F0*kappa). "off" (default) =>
    # bit-identical. "cattaneo_mindlin" liga DOIS efeitos:
    #  - loosening: g_gross=(slip/(slip+dt))^k afiado (k=1 == fracao
    #    atual), so gross slip afrouxa (Rousseau: fino colapsa, grosso trava);
    #  - wear/fretting: multiplica dF_0 por partial_slip_gate (CM), F0 maior
    #    -> r menor -> menos fretting (Liu2017 slope). PRECEDE loosening_slip_coupling.
    # ========================================================
    slip_regime_mode: str = "off"        # "off" | "cattaneo_mindlin"
    slip_regime_sharpness: float = 1.0   # k em g_gross (1.0 = fracao gross atual)
    slip_capacity_coeff: float = 1.0     # kappa (capacidade) p/ wear/fretting g_partial
    partial_slip_exp: float = 1.5        # m em g_partial (Cattaneo-Mindlin)
    # Acoplamento F_amp<->delta_amp (#4, spec §8): em gross slip a forca
    # transversal de loosening satura no Coulomb mu*F0. False (default) =>
    # backward-compat (F_amp independente). So ativo com slip_regime_mode CM.
    couple_famp_slip: bool = False
    # ACOPLAMENTO GERAL F_amp<=mu_eff(F0)*F0 em disp-mode (L3, roadmap #4,
    # 2026-07-16): fisicamente a amplitude de forca transversal TRANSMITIDA
    # nao pode exceder o teto de Coulomb mu_eff*F0 — acima disso a junta ja
    # esta em gross slip pleno e o excesso de F_amp IMPOSTO nao se traduz em
    # mais forca, so em mais deslocamento relativo (ja contabilizado via
    # delta_amp/resolve_transverse_slip). Diferente de couple_famp_slip (so
    # dentro de RotationalLooseningLoss, so em regime CM): este clamp e
    # GERAL — reatribui F_amp no topo de step_cycle, disp-mode, ANTES de
    # qualquer mecanismo o ler. famp_couple_on=0.0 (default) => guard
    # curto-circuita ANTES de qualquer computo (bit-identical; mesmo idioma
    # continuo de c_D: 0=off, >0 liga).
    # mu_eff = mu_bearing_eff(D) * knockdown(F0):
    #   - knockdown=1.0 se mu_eff_lo==0 (sem procedencia de queda, teto
    #     Coulomb puro mu_bearing_eff*F0);
    #   - senao interpola LINEAR de mu_eff_lo (F0->0) a 1.0 (F0>=
    #     mu_eff_F0_ref) — proveniencia Murai/IJAMT-2023 (mu efetivo cai
    #     0.46->0.24 com F0 crescente) + Measurement-2021 (limiares de
    #     slip-onset proporcionais a F0).
    # gross_ceiling_decay>0 decai o teto com o desgaste acumulado (state.D)
    # — proveniencia JMP-2021 (F_S->F_R degrada com desgaste). So disp-mode
    # (delta_amp dado); NUNCA no axial puro (sem slip transverso, sem teto
    # Coulomb aplicavel).
    famp_couple_on: float = 0.0       # 0.0 = OFF (bit-identical); >0 liga o clamp
    mu_eff_lo: float = 0.0            # knockdown em F0->0 (0 = sem knockdown, so teto)
    mu_eff_F0_ref: float = 0.0        # N — F0 de referencia (so lido se mu_eff_lo>0)
    gross_ceiling_decay: float = 0.0  # acoplamento D->queda do teto (0 = OFF)
    # Ratcheting CINEMATICO do loosening (spec 2026-07-08, modo collapse-missed):
    # rotacao por ciclo proporcional a DISTANCIA de gross-slip (Junker classico:
    # a porca avanca uma fracao do caminho de slip), nao ao excesso de torque.
    # d_theta_kin = gates * k_ratchet * 4*slip/(d_2/2). Da a proporcionalidade
    # com a amplitude que o drive assumido (F_amp) nao tem (diagnostico Lu2024:
    # T_loose/T_resist=1.57 fixo p/ TODA amplitude; dado colapsa ~amp). So em
    # disp-mode (slip derivado do curso) e alem do onset T_loose>T_resist.
    # 0.0 = inerte (bit-identical). Per-par, O(0.005-0.1).
    k_ratchet: float = 0.0
    # Expoente de amplitude do ratchet (spec 2026-07-12, PR-21): d_theta ~
    # slip^loose_amp_exp (via slip*(slip/LOOSE_AMP_REF)^(exp-1)). exp=1.0 =>
    # LINEAR (bit-identical). exp>1 => resposta de amplitude INGREME, reproduz
    # D-N ~delta^-m ingreme (Yang2023 N_L~delta^-3.8; na parte excedente do
    # slip, ~excess^-2.6). Aplicado tambem ao termo graded_scrit. Per-par.
    loose_amp_exp: float = 1.0
    # Take-up transversal FIXO (spec 2026-07-08, forma delta_free): parcela do
    # curso absorvida INDEPENDENTE da pre-carga (folga do furo engajada +
    # compliance da fixacao). slip = max(0, delta - delta_free - F_slip/k_tr).
    # Assinatura no dado: N_falha ~ 1/(delta-delta_0) (Liu2025 delta_0=0.30mm,
    # 4 pares +-3%) e N_falha ~flat vs torque (Lu fig20) — limiar ~F0 nao produz
    # nenhum dos dois. LIDO do dado (onset/regressao), per-rig, limitado pela
    # folga do furo. 0.0 = inerte (bit-identical).
    delta_free: float = 0.0         # m — take-up fixo do curso transversal
    # Forma-PRODUTO do ratchet (spec 2026-07-08): multiplica o termo cinematico
    # por slip_fraction (excesso de torque adimensional) => colapso gradual
    # ACELERANTE (F_0 cai -> excesso cresce; shape back-loaded do Liu2025) com
    # dinamica fracional invariante em F_0_init (N_falha ~flat vs torque — gate
    # de flatness do Lu). False = termo cinematico puro (bit-identical).
    ratchet_torque_coupled: bool = False
    # BLEND CONTINUO DE FASES (spec 2026-07-09, sec4.35): a rotacao de
    # afrouxamento por ciclo e limitada em SERIE por dois efeitos — (a) o excesso
    # de torque [drive de (T_loose-T_resist)] e (b) a DISPONIBILIDADE CINEMATICA
    # de slip (a porca nao pode girar mais que o caminho de gross-slip permite,
    # d_kin = 4*slip/(d_2/2)). A combinacao em serie e a media harmonica
    # d_eff = d_torque*d_kin/(d_torque+d_kin): quando o torque-excess dispara
    # (F_0->0, runaway), d_kin satura o termo => transicao GRADUAL em vez de S
    # abrupto (corrige o mid-over-loss, 35/82 curvas). Forma (dois limitadores em
    # serie), transferivel; loose_kin_ceiling escala a disponibilidade cinematica
    # (O(1), ~caminho de slip por raio). Opt-in; 0.0 => sem teto (bit-identical).
    # So disp-mode (slip do curso). Diferente de k_ratchet (termo ADITIVO): aqui
    # e um TETO SUAVE sobre o drive de torque.
    loose_kin_ceiling: float = 0.0
    # TAXA DE LOOSENING GRADUADA amplitude-sensivel (spec 2026-07-09, sec4.37).
    # loose_rate_mode="torque" (default) = kernel atual (slip_fraction*(T_loose-
    # T_resist)/k_tors), que em disp-mode e RUNAWAY-TO-ZERO uma vez disparado
    # (s_crit=delta_t=mu*F0/k_tr CAI com F0 => g_gross->1): a amplitude decide SE
    # dispara, nao a TRAJETORIA. "graded_scrit" substitui esse kernel por uma taxa
    # CINEMATICA no EXCESSO de slip sobre um s_crit FIXO (nao ~F0):
    #   d_theta = gates * k_loose_graded * max(0, slip - s_crit_loose)/(d_2/2).
    # Amplitude-sensivel (o slip corrente modula a taxa a cada ciclo => um ESPECTRO
    # morde, sec4.36); SEM runaway (s_crit fixo + slip limitado pelo curso delta =>
    # a taxa satura); sub-critico (slip<=s_crit) => zero (plato/nao-inicia do
    # Bauer, s_crit~99um); colapso quase-LINEAR (Karlsen "near-linear catastrophic
    # back-off", sec4.35). s_crit_loose = amplitude critica de slip [m], PER-RIG
    # com proveniencia (Bauer 76-108um; curva amplitude-vs-vida). k_loose_graded =
    # coeficiente de taxa [rad por rad de excesso/raio]. loose_rate_mode="torque"
    # (default) OU k_loose_graded=0 => branch nunca roda (BIT-IDENTICAL). So disp-mode.
    loose_rate_mode: str = "torque"
    s_crit_loose: float = 0.0       # m — amplitude critica de slip (0 = usa mode torque)
    k_loose_graded: float = 0.0     # coef. da taxa graduada (0 = OFF)
    # TAXA FRACIONARIA (P-13 da mesa, executada 2026-08-20): expoente de F no
    # ramo graded — d_theta *= (F_0/F_0_init)^fe. Motivo medido (3 fontes,
    # mapa_das_65_fora P-13; re-medido no YANG_2023 0,30mm): o canal rotacional
    # tem SO dois atratores (runaway-a-zero ou arresto pelo re-travamento do
    # [K(s)]), e o dado desacelera SEM travar — decay ~exponencial
    # (dF/dN ~ F <=> fe=1; sub-exponencial <=> fe>1). fe=0 = OFF EXATO
    # (bit-identical, caminho antigo).
    loose_F_exp: float = 0.0
    # RATCHET DE REGIME DE STICK, amplitude-dirigido com INCUBACAO (gth, spec
    # 2026-08-10, dossie YANG_2019 amp0p4 — 5 falsificacoes de mecanismo
    # mostraram que falta perda sub-slip com onset ingreme em amplitude).
    # Fisica: micro-slip de flanco em regime de STICK macro produz rotacao
    # incremental com dependencia ingreme de amplitude (lei do PR-21/IJPEM,
    # N_L ~ delta^-3.8); o acumulador A_gth carrega a incubacao (o plato do
    # dado). ATIVO SOMENTE em stick (slip_amp <= 1e-9): onde ha gross-slip os
    # canais macro assumem e o termo e 0 EXATO — por isso curvas em regime de
    # slip (as 0.6 do Yang2019) ficam BIT-IDENTICAS sem re-calibracao. dF_0 e
    # dE derivam do MESMO dtheta (helice + filete) => conservacao intacta.
    # gth_k=0 => OFF exato (bit-identical).
    gth_k: float = 0.0              # rad/ciclo na razao=1 (0 = OFF exato)
    gth_q: float = 3.8              # expoente de amplitude (IJPEM N_L~delta^-3.8)
    gth_dref: float = 5e-4          # m — escala de referencia (= LOOSE_AMP_REF)
    gth_A0: float = 0.0             # incubacao [ciclos-eq]; 0 = sem incubacao
    # ACELERACAO PROGRESSIVA do gth (2026-08-20, YANG_2019 amp0p4): pos-onset a
    # taxa cresce com o ACUMULADO — dano de flanco progressivo em stick:
    #   d_theta = gth_k * rq * ((A_gth - A0)/max(A0, 1))^p     [p > 0]
    # Motivo medido: o dado da amp0p4 acelera 11,6x em taxa para 3,8x de
    # N-efetivo pos-onset (p ~ 1,8 no log-log) e NENHUM canal do engine acelera
    # em stick (damage nao cresce: driver e' slip macro). p=0 = OFF EXATO
    # (caminho antigo, taxa constante pos-onset; bit-identical).
    gth_accel_p: float = 0.0
    # HISTERESE DE STICK (2026-08-20, YANG_2019 amp0p4): mu ESTATICO vs
    # CINETICO — uma vez que o slip transversal ABRE pela 1a vez (ruptura do
    # travamento: interlock de asperezas/oxido), o mu de bearing efetivo cai
    # por este fator e NAO volta (latch em SlowState.stick_broken). Motivo
    # medido: o modelo alcanca a transicao stick->slip no joelho real do dado
    # (F=0,916*F0) mas o [K(s)] re-trava (k_tr cai com F mais rapido que
    # mu*F) e o sistema congela em equilibrio espurio onde o dado real
    # colapsa sem volta. 1.0 = OFF EXATO (sem latch, bit-identical).
    mu_kinetic_frac: float = 1.0
    # RUNAWAY DE PORCA SOLTA no ramo graded (2026-08-20, zhang2006_fig3 pela
    # rota robusta — estudo sec7-sec9): TRANSICAO lei-de-potencia -> runaway.
    # Fisica: o auto-travamento residual (torque de atrito ~ F) deixa de
    # segurar o backoff abaixo de uma fracao critica de F0 e a taxa DISPARA —
    # o traco theta digitalizado da Fig. 3 mostra theta 10->42 deg no fim com
    # razao de taxas ~14x, e a lei F^fe LIDA (fe=5,80 do theta = 5,93 do P,
    # duas regressoes independentes) desacelera por construcao: nenhum fe
    # cobre o disparo (res.max trava 1,37x com a lei lida). Ancoras de
    # leitura: r_c = 0,25 (o paper DEFINE o fim do Estagio II em P=25% —
    # exatamente porque dali a porca solta) e gain ~ razao de taxas - 1.
    # Boost Hill multiplicativo sobre d_theta (POS loose_F_exp, PRE dreno):
    #   fator = 1 + gain * fc^k/(fc^k + r^k),  r = F_0/F_0_init
    # Acima do limiar o boost e' ~(fc/r)^k (suave, nao zero — mesmo idioma
    # dos outros Hill do engine); abaixo tende a 1+gain. E' o ESPELHO do
    # crash_trigger_frac (que SUPRIME antes do gatilho): aqui a taxa do meio
    # fica INTACTA e so o fim ganha o disparo. frac=0 OU gain=0 = OFF EXATO
    # (bit-identical, o multiplicador nem e' computado).
    loose_runaway_frac: float = 0.0        # r_c [0..1] (0 = OFF exato)
    loose_runaway_gain: float = 0.0        # ganho maximo extra (0 = OFF exato)
    loose_runaway_sharpness: float = 6.0   # k do Hill (so lido se frac>0)
    # BURST DE RUPTURA (2026-08-21, lu2024_fig14_burst_resultado.md — a 3a
    # instancia da classe transicao-entre-regimes): quando a INCUBACAO abre
    # (o MESMO gate Hill de slip_onset_W — sem estado novo), a energia
    # acumulada no travamento libera num dreno rapido e LIMITADO:
    #   d_theta_burst = g_onset * rate * max(0, F_0 - alvo) / (k_b*lead)
    #   alvo = (1 - frac) * F_0_init
    # Perfil resultante: burst intenso (exponencial em direcao ao alvo) que
    # DESACELERA sozinho — exatamente o platô->burst->cauda das DUAS
    # fig14_long do LU_2024 (ambas drenam ate ~0,50-0,54 F0 no burst: fracao
    # ~fixa, transicao bi-estavel da interface; o kernel da cauda segue sendo
    # o graded). dF e dE derivam do MESMO d_theta (helice + filete) =>
    # conservacao intacta. SO o ramo graded le (escopo minimo, como o
    # runaway). frac=0 OU rate=0 = OFF EXATO (nem computa); exige
    # slip_onset_W > 0 (sem incubacao o gate e' 1 desde N=1 e o "burst"
    # viraria um dreno inicial — nao e' a fisica).
    # PISO DE ARRESTO ANULAVEL POR CARGA AXIAL EXTERNA (C3 do prereg
    # 2026-08-21-eccles-axial-tres-camadas). A fisica e' o achado CENTRAL do
    # Eccles 2010, e a nota de aparato dele a especifica: o piso residual de
    # pre-carga e' ANULADO quando FA o excede -- "the floor is externally
    # imposed and can also DEMAND the state fall BELOW where it would
    # otherwise arrest". O `loose_arrest_floor` implementa um piso
    # AUTO-GERADO; este campo o torna anulavel por uma BC externa:
    #   f_min <- f_min * max(0, 1 - F_ax_ext/(ax_floor_override * F_sep))
    # com F_sep = F_sep_axial(state, geom, mat), que JA EXISTE (usado em
    # U_loaded). Leitura do numero: fracao de F_sep em que o axial anula o
    # piso por inteiro -- UM valor compartilhado pela fonte (G4 do prereg;
    # mais de um por curva vira fit e o item para).
    # 0.0 (default) = OFF EXATO, e com F_ax_ext = 0 o gate e' IDENTICO ao
    # anterior por early-return -- isolamento ESTRUTURAL, nao por default.
    ax_floor_override: float = 0.0
    onset_burst_frac: float = 0.0   # fracao de F0 drenada pelo burst (0 = OFF)
    onset_burst_rate: float = 0.3   # fracao da lacuna por ciclo (so lido se frac>0)
    # GATE PROPRIO do burst (2026-08-21, liu2025_M16_amp0p8 sec6 — anatomia
    # do bloqueio): os 3 gates de estado existentes sao monotonicos E
    # COMPARTILHADOS entre canais, entao um burst gateado pelo `g` do
    # slip_onset so pode abrir onde o WEAR tambem abre (na amp0p8 o
    # slip_onset_W=250k segura o wear ate o fim => o burst nunca ve o miolo).
    # Fisica: a energia de ADESAO/microssolda da interface libera num limiar
    # PROPRIO, distinto do limiar de abrasao (duas escalas de energia do
    # mesmo W_slip_acc). onset_burst_W > 0 => o burst troca o `g`
    # compartilhado por um Hill proprio sobre o MESMO W_slip_acc (mesmo
    # sharpness); 0.0 = usa o `g` compartilhado = BIT-IDENTICO ao
    # comportamento da adocao fig14 (test_onset_burst_gate_proprio).
    onset_burst_W: float = 0.0      # J; limiar proprio do burst (0 = usa o g compartilhado)
    # RELOGIO SIGMOIDE do embedding (2026-08-21, lu2024_fig14_amp0p25_long —
    # stick TOTAL medido, plato de 27-56 ciclos PUBLICADO antes da queda):
    # expoente de Weibull no relogio de Estagio I,
    #   delta_emb(N) = target * (1 - e^{-(N/N_emb)^m})
    # m>1 => plato inicial + joelho + saturacao (a forma sigmoide que o
    # exponencial nao faz); m=1 = forma atual BIT-IDENTICA (early-branch, o
    # ramo novo nem roda). Implementacao STATE-BASED exata: o N implicito e'
    # recuperado da fracao consumida phi=delta/target e o passo e'
    # phi(N_eq+1)-phi(N_eq) — para trajetoria virgem reproduz o closed-form
    # ao bit, e estado inicial nao-nulo (arruela reusada) segue suportado.
    emb_clock_m: float = 1.0

    # ========================================================
    # Fadiga de raiz de rosca -> fratura (cliff), spec 2026-07-08. Miner's rule
    # sobre Su-N bilinear (Yang, cl.10.9 -> proveniencia) + Goodman (F_0 = tensao
    # media, EVOLUI c/ o afrouxamento). D_fatigue>=1 => fratura (F_0 -> residual).
    # fatigue_enabled=False (default) => FatigueLoss inerte (zero exato, bit-identical).
    # ========================================================
    fatigue_enabled: bool = False
    fat_Kt: float = 3.5                 # concentracao de tensao raiz de rosca
    fat_sigma_uts: float = 1040e6       # Pa — UTS (classe 10.9) p/ Goodman
    fat_sigma_knee: float = 50e6        # Pa — joelho da bilinear (Yang)
    fat_C1: float = 5e32                # coef alta tensao
    fat_m1: float = 3.5                 # expoente alta tensao
    fat_C2: float = 5e49                # coef baixa tensao
    fat_m2: float = 6.0                 # expoente baixa tensao
    fat_sigma_endurance: float = 10e6   # Pa — abaixo => vida infinita
    fatigue_residual_frac: float = 0.0  # F_0 residual pos-fratura (0 = fratura total)
    # Descarga em RAMPA (prereg 2026-07-28-ramp-capability, Opcao A/A1 do estudo
    # liu2025_rampAB_resultado.md): perda progressiva de secao no lugar do cliff.
    # Para D_fatigue > fat_ramp_D_on, A_eff/A_s = 1-((D-D_on)/(1-D_on))^q e F_0
    # segue a liberacao serie bolt-junta g=(1-a)(1+rho)/((1-a)+rho). dE por
    # incremento = Delta U_internal (mesma rota do cliff). fat_ramp_D_on=1.0
    # (default) = SEM rampa => caminho do cliff INTOCADO, bit-identico (P0/P2;
    # protege LI_2022_TRIBOINT, adotado com o cliff). Em rampa, D_on tem classe
    # handbook (propagacao = ultimos 10-30% da vida HCF; N_D/N_f medido no Liu
    # 2025 = 0,72-0,80) e fatigue_residual_frac NAO e lido (g(1)=0 => F_0 -> 0).
    fat_ramp_D_on: float = 1.0          # inicio da rampa em D_fatigue (1.0 = OFF)
    fat_ramp_q: float = 5.0             # expoente da rampa (so lido se D_on < 1)
    # Modo da tensao de fadiga (spec 2026-07-12, PR-24). "axial" (default) =
    # sigma_a = Kt*|F_amp|/A_s (tensao axial; correto p/ ensaio axial). "bending"
    # = sigma_a = Kt*E*d_2*slip/L_eff^2 (tensao de FLEXAO do parafuso sob o
    # deslocamento transverso imposto; correto p/ ensaio transversal — a fratura
    # escala com delta, nao com F_amp). So afeta FatigueLoss (fatigue_enabled).
    fat_stress_mode: str = "axial"      # "axial" | "bending"


# ============================================================================
# Estado lento e contabilidade
# ============================================================================

@dataclass
class SlowState:
    """Vetor s — memória cumulativa entre ciclos (slow timescale)."""
    F_0: float                       # N — pré-carga residual
    delta_emb: float = 0.0           # m
    delta_creep: float = 0.0         # m
    delta_wear: float = 0.0          # m
    delta_thread_fret: float = 0.0   # m — profundidade de fretting de flanco (axial)
    theta_loose: float = 0.0         # rad
    F_0_init: float = 0.0            # N — pré-carga inicial (reference)
    D: float = 0.0                   # surface_damage [0,1]
    stick_broken: float = 0.0        # 0/1 — latch da RUPTURA de stick (o
                                     #     slip transversal abriu pela 1a vez;
                                     #     so e' setado com mu_kinetic_frac<1)
    A_gth: float = 0.0               # ciclos-eq — acumulador do ratchet de
                                     #     STICK (gth, spec 2026-08-10):
                                     #     A += (delta/dref)^q por ciclo EM STICK;
                                     #     termo ativo so com A >= gth_A0
    F_ax_ext: float = 0.0            # N — CARGA AXIAL EXTERNA imposta
                                     #     (condicao de contorno de TRACAO,
                                     #     force-controlled, independente do
                                     #     drive transversal). Constante por
                                     #     corrida no modo `constant`; o modo
                                     #     `intermittent` do ECCLES exige um
                                     #     duty que o paper NAO reporta, e por
                                     #     isso fica fora de escopo (prereg
                                     #     2026-08-21-eccles-axial-tres-camadas).
                                     #     0.0 = sem BC externa (valor CERTO das
                                     #     baselines, nao ausencia de dado).
    W_slip_acc: float = 0.0          # J — trabalho de slip transverso acumulado
                                     #     (driver da incubação do loosening)
    W_conf: float = 0.0              # J — trabalho de conformacao acumulado
                                     #     (pressure-weighted; driver do
                                     #      conformation_gate)
    D_fatigue: float = 0.0           # dano de Miner acumulado [0,1] (fratura em 1)
    n_cycle: int = 0                 # contador de ciclos (F3 2026-07-21: indice
                                     #   do mu_bearing_schedule; 0 antes do 1o
                                     #   step_cycle — puramente aditivo)
    n_retighten: int = 0             # eventos de re-aperto ja ocorridos (D-J
                                     #   2026-08-05). 0 = junta virgem, e' o que
                                     #   protege o estagio t0 por CONSTRUCAO:
                                     #   o multiplicador (1+g)^n vale 1 em n=0.
                                     #   Incrementado SO em retighten().

    def copy(self) -> "SlowState":
        return replace(self)

    def as_array(self) -> np.ndarray:
        return np.array([self.F_0, self.delta_emb, self.delta_creep,
                         self.delta_wear, self.theta_loose])


@dataclass
class EnergyBudget:
    """Contabilidade de energia cumulativa desde t=0.

    C2 — bookkeeping do viscoso axial (spec 2026-07-07 #27, revisitado plano
    L1-L7 Task 8): em modo FORÇA axial (theta~0), `W_ext_per_cycle` dá ~0 (sem
    slip transverso), então o amortecimento viscoso de Rayleigh
    (`W_damp_visc`) ficava ÓRFÃO — sem contraparte em `W_ext` — deixando o
    residual de conservação ~ −W_damp_visc (achado histórico −242…−12 J).
    Escolha ADOTADA (menor diff que fecha o canal, entre as duas listadas no
    brief da Task 8): SOURCEAR o viscoso em `W_ext` (`step_cycle` soma
    `W_visc_c`/`W_m` também em `W_ext`, não só em `W_damp_visc`) — em vez de
    excluir o canal viscoso do residual. Racional físico: o atuador
    hidráulico/excitador que impõe o ciclo de carga externo é exatamente quem
    realiza trabalho contra o amortecedor modal (loop elíptico
    força-deslocamento); esse trabalho já entra no sistema pela MESMA
    fronteira externa que `W_ext` contabiliza — não é uma dissipação interna
    adicional sem fonte, então somar é mais correto fisicamente do que
    excluir o canal do residual (que apenas esconderia a energia, não a
    atribuiria). Em transversal (theta=pi/2), W_visc ~ cos²(pi/2) ~ 0, então a
    soma extra não afeta o modo displacement-controlled (residual/W_visc
    medido ~0.02 — ver `tests/test_axial_viscous_conservation.py` e
    `tests/test_l7_removal_bound_and_viscous.py`).

    L7 — energia de remoção (plano L1-L7 Task 8): `V_wear_removed`/
    `E_wear_removal` acumulam, lado a lado, o volume REMOVIDO (Archard:
    bearing via `WearLoss` + flanco via `ThreadFrettingLoss`) e a energia de
    atrito dos MESMOS dois canais — bookkeeping puramente aditivo (não
    realimenta dF_0/estado, não muda trajetória). Consumido por
    `removal_energy_check()` para comparar a energia específica implicada
    (J/mm³) com a banda da literatura.
    """
    W_ext: float = 0.0               # J — trabalho externo cumulativo
    U_stored: float = 0.0            # J — energia elástica armazenada atual
    U_stored_init: float = 0.0       # J — referência inicial
    W_damp_visc: float = 0.0         # J — amortecimento viscoso (Rayleigh)
    W_diss_emb: float = 0.0          # J — plastic embedding
    W_diss_creep: float = 0.0        # J — creep viscoelástico
    W_diss_wear: float = 0.0         # J — Archard
    W_diss_loose: float = 0.0        # J — atrito no filete (rotational)
    W_diss_friction_y: float = 0.0   # J — atrito transversal (slip y)
    W_diss_fracture: float = 0.0     # J — energia liberada em fratura/colapso (cliff, #6)
    # L7 (Task 8): volume removido [m³] (bearing+flanco) e a energia de atrito
    # dos MESMOS canais [J] — 1:1, ver removal_energy_check(). Bookkeeping
    # aditivo puro (default 0.0 = nenhum wear rodou ainda, backward-compat).
    V_wear_removed: float = 0.0      # m³
    E_wear_removal: float = 0.0      # J

    @property
    def W_diss_total(self) -> float:
        """Soma de todas as dissipações."""
        return (self.W_damp_visc + self.W_diss_emb + self.W_diss_creep
                + self.W_diss_wear + self.W_diss_loose + self.W_diss_friction_y
                + self.W_diss_fracture)

    @property
    def U_released(self) -> float:
        """Energia liberada do reservatório (≥ 0 durante loosening)."""
        return self.U_stored_init - self.U_stored

    @property
    def conservation_residual(self) -> float:
        """Deve ser ≈ 0: W_ext + U_released − W_diss_total."""
        return self.W_ext + self.U_released - self.W_diss_total

    def removal_energy_check(self) -> dict:
        """L7 (plano L1-L7 Task 8): sanity check INFORMACIONAL da energia
        específica de remoção de material implicada pelo modelo, contra a
        banda [lo,hi] J/mm³ da literatura (Shipway 2021, derivada,
        taxa-dependente — `New_Theory/r5_anchors.json` chave
        "removal_energy_bound", lida via
        `calibration.knowledge_base.removal_energy_bound()`).

        Retorna sempre `{"implied_J_per_mm3", "in_bound", "bound"}`;
        `bound` é sempre o dict da literatura (lo/hi/unit/source) — não
        depende de wear ter rodado. `implied_J_per_mm3`/`in_bound` são
        `None` quando nenhum volume foi removido ainda (wear inativo,
        `k_wear_spec`/`K_archard`=0, corrida sem slip, ou só ciclos
        transitórios sem wear ativo) — divisão por zero evitada por design,
        não por exceção. NUNCA lança exceção nem altera comportamento: é
        puramente um hook de aviso de nível de relatório — o chamador decide
        o que fazer com `in_bound=False` (fora da banda não impede a
        simulação nem indica um bug per se; é um sinal para revisão).

        Import de `calibration.knowledge_base` é LOCAL (dentro do método, não
        no topo do módulo): `calibration/__init__.py` importa
        `staged_calibrator`/`shared_calibrator`/`server`, que importam ESTE
        módulo (`numerical.dynamic_stiffness_analyzer`) no TOPO deles — um
        import de `calibration` no topo DESTE módulo criaria um ciclo real na
        importação (numerical → calibration → numerical, com o segundo braço
        vendo `numerical` ainda parcialmente inicializado ⇒ ImportError). O
        import local resolve em tempo de CHAMADA (o método só roda depois
        que ambos os módulos já terminaram de carregar), sem esse risco —
        verificado: `calibration.knowledge_base` não importa `numerical` no
        seu topo (só localmente, dentro de `dof_summary()`), então nenhuma
        das duas pontas toca a outra durante a fase de import do módulo.
        """
        from bolt_analysis_studio.calibration import knowledge_base as kb
        bound = kb.removal_energy_bound()
        if self.V_wear_removed <= 0.0:
            return {"implied_J_per_mm3": None, "in_bound": None, "bound": bound}
        V_mm3 = self.V_wear_removed * 1e9   # m³ → mm³
        # tipos NATIVOS (float/bool, nao np.float64/np.bool_): o dict vai p/ o
        # store JSON via CaseResult.l7_check — np.bool_ nao e' serializavel
        implied = float(self.E_wear_removal / V_mm3)
        in_bound = bool(bound["lo"] <= implied <= bound["hi"])
        return {"implied_J_per_mm3": implied, "in_bound": in_bound, "bound": bound}


@dataclass
class CycleSnapshot:
    """Snapshot per-cycle pra diagnóstico/plot."""
    cycle: int
    F_0: float
    delta_U_stored: float
    W_ext_cycle: float
    W_diss_cycle: float
    Phi_eff: float
    slip_fraction: float
    per_mechanism: Dict[str, float]
    dF_0_by_mech: Dict[str, float] = field(default_factory=dict)
    D: float = 0.0


# ============================================================================
# Constitutivas (todas funções de s)
# ============================================================================

def k_j_ax(state: SlowState, mat: JointMaterial) -> float:
    """
    Rigidez axial do joint via Greenwood-Williamson.
    k_j_ax(F_0) = k_j_init · (F_0/F_init)^α
    Quando F_0 → 0, k_j_ax → 0 (junta perde rigidez gradualmente).
    """
    if state.F_0 <= 0 or state.F_0_init <= 0:
        return 0.0
    ratio = state.F_0 / state.F_0_init
    return mat.k_j_init * ratio**mat.alpha_GW


def Phi_eff(state: SlowState, geom: JointGeometry, mat: JointMaterial,
            direction: str = 'axial') -> float:
    """
    Razão de rigidez efetiva. Sobe conforme F_0 cai (joint softens).

    `direction` mantido na assinatura (compat de callers); a antiga correção
    `Phi_ax/tr_correction` foi REMOVIDA no Estágio B (tuner ≡1.0; o ramo de
    loosening absorveu `Phi_tr_correction` em `tr_loose_gain` via shim).
    """
    kj = k_j_ax(state, mat)
    if state.F_0 <= 0:
        return 1.0
    raw = geom.k_b / (geom.k_b + kj)
    return min(raw, 1.0)


def direction_blend(theta_load: float, val_ax: float, val_tr: float) -> float:
    """
    Blend scalar values entre axial e transversal pelo ângulo de carregamento.
    Usado pra interpolar tuners entre as duas direções de calibração.
        k_eff(θ) = k_ax · cos²θ + k_tr · sin²θ
    """
    c2, s2 = np.cos(theta_load)**2, np.sin(theta_load)**2
    return val_ax * c2 + val_tr * s2


def F_sep_axial(state: SlowState, geom: JointGeometry, mat: JointMaterial) -> float:
    """Carga axial que separa a junta."""
    Phi = Phi_eff(state, geom, mat)
    return state.F_0 / max(1 - Phi, 1e-9)


def mu_bearing_eff(state: SlowState, mat: JointMaterial) -> float:
    """Atrito de bearing modulado por surface_damage.

    mu_eff = mu_bearing · (1 − k_dmg_mu·D), com clamp em 0.
    Com D=0 ou k_dmg_mu=0 retorna mu_bearing exato (backward-compat).

    mu_bearing_schedule (F3 2026-07-21, prereg F3.2-CHU): quando presente
    ((N, µ) medidos — ex. Chu 2026 Fig. 5), o µ de bearing é o INTERPOLADO
    do schedule em state.n_cycle e SUBSTITUI a constante + modulação de
    dano (o µ medido já contém a evolução real da interface). Input de
    MEDIÇÃO (idioma delta_spectrum), NUNCA fittable. Schedule vazio
    (default) ⇒ caminho antigo BIT-IDÊNTICO.
    """
    sched = getattr(mat, "mu_bearing_schedule", ()) or ()
    if sched:
        xs = [float(p[0]) for p in sched]
        ys = [float(p[1]) for p in sched]
        return float(np.interp(state.n_cycle, xs, ys))
    factor = 1.0 - mat.k_dmg_mu * state.D
    # HISTERESE DE STICK (2026-08-20): pos-ruptura o mu e' o CINETICO.
    # mu_kinetic_frac=1.0 (default) => fator 1.0 exato (bit-identical).
    if mat.mu_kinetic_frac < 1.0 and state.stick_broken > 0.0:
        factor *= max(mat.mu_kinetic_frac, 0.0)
    return mat.mu_bearing * max(factor, 0.0)


def mu_thread_tighten_eff(state: SlowState, mat: JointMaterial) -> float:
    """Atrito de flanco de rosca VISTO NO APERTO, elevado por galling do dano.

    mu_thread_tighten = mu_thread · (1 + k_gall·D), k_gall ≥ 0 (spec 2026-07-07).
    Rosca danificada (galling/rugosidade) sobe o nut factor no re-aperto ⇒ F0
    recuperado cai. Com k_gall=0 ou D=0 retorna mu_thread exato (backward-compat).
    So usado em tightening_torque (evento de re-aperto), NUNCA em T_resistance (o
    galling no ciclo desaceleraria o loosening — sinal errado p/ a aceleracao dry).
    Sinal OPOSTO ao mu_bearing_eff (interface distinta: flanco de rosca vs bearing).
    """
    return mat.mu_thread * (1.0 + mat.k_gall * max(state.D, 0.0))


def famp_gross_slip_ceiling(state: SlowState, mat: JointMaterial) -> float:
    """Teto de Coulomb p/ a amplitude de forca transversal em disp-mode (L3,
    roadmap #4): fisicamente F_amp nao pode superar mu_eff(F0)*F0 — acima
    disso a junta ja esta em gross slip pleno e o excesso de forca IMPOSTA
    nao se traduz em mais forca TRANSMITIDA, so em mais deslocamento
    relativo (ja contabilizado via delta_amp/resolve_transverse_slip).

    mu_eff = mu_bearing_eff(D) * knockdown(F0):
      - knockdown = 1.0 se mu_eff_lo==0 (sem procedencia de queda, teto
        Coulomb puro mu_bearing_eff*F0);
      - senao interpola LINEAR de mu_eff_lo (F0→0) a 1.0 (F0>=mu_eff_F0_ref)
        — proveniencia Murai/IJAMT-2023 (mu efetivo cai 0.46->0.24 com F0
        crescente) + Measurement-2021 (limiares de slip-onset proporcionais
        a F0).
    gross_ceiling_decay>0 decai o teto com o desgaste acumulado (state.D) —
    proveniencia JMP-2021 (F_S->F_R degrada com desgaste).

    NAO verifica famp_couple_on — o guard fica no site de uso (step_cycle),
    para que o flag OFF curto-circuite ANTES desta funcao ser chamada.
    """
    mu_eff = mu_bearing_eff(state, mat)
    if mat.mu_eff_lo > 0.0 and mat.mu_eff_F0_ref > 0.0:
        k = min(1.0, max(state.F_0, 0.0) / mat.mu_eff_F0_ref)
        mu_eff *= mat.mu_eff_lo + (1.0 - mat.mu_eff_lo) * k
    ceiling = mu_eff * max(state.F_0, 0.0)
    if mat.gross_ceiling_decay > 0.0:
        ceiling *= max(0.0, 1.0 - mat.gross_ceiling_decay * state.D)
    return max(ceiling, 0.0)


def retight_loss_factor(state: SlowState, mat: JointMaterial) -> float:
    """Fator de AMPLIFICACAO da perda por slip apos k eventos de re-aperto.

        fator(0)    = 1                                  (virgem)
        fator(n>=1) = retight_loss_base * (1+gain)^(n-1)

    Contradominio **(0, inf)** — ATRAVESSA o 1, ao contrario tanto da
    familia de GATES (Hill, (0,1], so atrasa) quanto de um amplificador
    puro ([1,inf), so amplifica, falsificado no D-J por algebra). O dado
    pede queda forte no 1o reaperto e recuperacao ~g por evento.
    (nota historica: a familia de GATES tem Hill,
    contradominio (0,1], que so sabe ATRASAR). Foi exatamente essa distincao
    que falsificou a classe "aceleracao tardia" em 2026-08-02 POR CONSTRUCAO:
    nenhum gate pode acelerar. Este fator acelera, e o relogio dele nao e' o
    dano (gradual demais) nem a pre-carga (realimenta o que amplifica) — e' a
    CONTAGEM DE EVENTOS, que e' exogena ao estado continuo.

    Dois modos de inercia, os dois exatos:
      * `retight_loss_gain = 0` -> 1.0 para qualquer n (OFF bit-identico);
      * `n_retighten = 0` -> 1.0 para qualquer ganho (estagio VIRGEM protegido
        por construcao, sem precisar de gate de escopo).
    """
    n = state.n_retighten
    if n <= 0:                                    # estagio VIRGEM: intocado
        return 1.0
    if mat.retight_loss_base == 1.0 and mat.retight_loss_gain <= 0.0:
        return 1.0                                # OFF exato
    base = max(mat.retight_loss_base, 0.0)
    if mat.retight_loss_gain <= 0.0:
        return float(base)
    return float(base * (1.0 + mat.retight_loss_gain) ** (n - 1))


def slip_onset_gate(state: SlowState, mat: JointMaterial) -> float:
    """Gate de incubação do colapso slip-driven (estágio I de Jiang).

    Retorna g ∈ [0,1] que multiplica a perda de pré-carga dos mecanismos
    dirigidos por slip (wear e loosening rotacional). Enquanto o trabalho
    de slip transverso acumulado (``state.W_slip_acc``) é muito menor que
    ``slip_onset_W``, g≈0 (platô do estágio 1, sem backing-off / sem
    remoção macro); perto do limiar g sobe rápido (função de Hill, expoente
    ``slip_onset_sharpness``); acima, g→1 (estágio 2). Com
    ``slip_onset_W <= 0`` retorna 1.0 exato (sem incubação, backward-compat).
    """
    if mat.slip_onset_W <= 0.0:
        return 1.0
    k = max(mat.slip_onset_sharpness, 1e-6)
    x = max(state.W_slip_acc, 0.0) / mat.slip_onset_W
    xk = x ** k
    return float(xk / (xk + 1.0))


def damage_onset_gate(state: SlowState, mat: JointMaterial) -> float:
    """Gate de ONSET do dano (predictive trigger, spec 2026-07-05).

    Espelha ``slip_onset_gate`` mas portao do CRESCIMENTO do dano: g ∈ [0,1)
    que multiplica ``dD``. Enquanto o trabalho de slip cru acumulado
    (``state.W_slip_acc``, ja gross-slip-gated) e < ``W_crit``, g≈0 (D nao
    cresce -> plato); acima, g→1 (D cresce -> colapso). Com ``W_crit <= 0``
    retorna 1.0 exato (gate transparente, guarda o 0/0, backward-compat: dano
    ungated). O regime de slip fica embutido: dD ~ W_slip_cycle (0 em partial
    slip) e W_slip_acc so acumula em gross slip.
    """
    if mat.W_crit <= 0.0:
        return 1.0
    k = max(mat.dmg_onset_sharpness, 1e-6)
    x = max(state.W_slip_acc, 0.0) / mat.W_crit
    xk = x ** k
    return float(xk / (xk + 1.0))


def conformation_gate(state: SlowState, mat: JointMaterial) -> float:
    """Gate de conformacao dependente de pressao (spec 2026-07-04 §4).

    Retorna g in (0,1] que MULTIPLICA a perda de pre-carga slip-driven
    (wear + loosening rotacional). Conforme o trabalho de conformacao
    acumulado (``state.W_conf``, ponderado por pressao) cresce, g -> 0 e o
    afrouxamento slip-driven se arresta (plato do sobretorque). Espelha
    ``slip_onset_gate`` mas FECHANDO (1 -> 0). Com ``W_conf_ref <= 0`` retorna
    1.0 exato (mecanismo inativo, backward-compat).
    """
    if mat.W_conf_ref <= 0.0:
        return 1.0
    return float(mat.W_conf_ref / (max(state.W_conf, 0.0) + mat.W_conf_ref))


def embedding_conformance_factor(state: SlowState, geom: JointGeometry,
                                 mat: JointMaterial) -> float:
    """Saturacao de embedding dependente da pressao de APERTO (spec 2026-07-08).

    O assentamento RESIDUAL (pos-torque, visivel na curva) cai com a pre-carga de
    aperto: torque maior pre-conforma mais asperezas (area real ~ F0/H) => menos
    residuo ciclico. Reescala o asintota de embedding por
        S = min(1, (p_ref_emb / p_init)^emb_conform_exp),  p_init = F0_init/A_contact.
    Keyed em F0_INIT (fixo no run) — NUNCA no F_0 corrente (evitaria feedback de
    runaway) — logo preserva a forma fechada de Norton, so com asintota escalada.
    Absoluto k_b*emb*S CAI com F0 => fracional cai mais rapido que 1/F0 => inclina
    d(final)/dP0 (Liu2017). VDI f_Z TOTAL fica fixo; muda so o split aperto/ciclico.
    emb_conform_exp<=0 => 1.0 exato (inerte, backward-compat bit-identical)."""
    return _conformance_S(state, geom, mat.p_ref_emb, mat.emb_conform_exp)


def embedding_pressure_factor(state: SlowState, geom: JointGeometry,
                              mat: JointMaterial) -> float:
    """Encaixe DIRIGIDO POR PRESSAO — o ramo oposto da pre-conformacao.

    `embedding_conformance_factor` diz que aperto MAIOR ja consumiu aspereza no
    torque, logo sobra menos residuo ciclico (S cai quando p sobe). Esta funcao
    diz a coisa complementar: o achatamento plastico PRECISA de pressao, entao
    abaixo de uma referencia o reservatorio de encaixe e' mais RASO (S cai
    quando p CAI):

        S_p = min(1, (p_init / p_ref_emb) ** emb_pressure_exp),
        p_init = F_0_init / A_contact.

    As duas fisicas coexistem em juntas reais e por isso os fatores MULTIPLICAM
    em vez de se excluirem; cada uma tem seu expoente e as duas sao OFF por
    default. Keyed em F_0_INIT (fixo no run), nunca no F_0 corrente — senao o
    encaixe realimentaria o proprio decaimento e a forma fechada de Norton
    deixaria de valer (so a assintota pode ser reescalada).

    O `min(1, .)` nao e' cosmetico: e' ele que torna o efeito EXATAMENTE nulo
    (bit-a-bit, sem tolerancia) em toda junta com p >= p_ref, o que da
    isolamento estrutural quando a lei e' adotada numa fonte que varre pressao.

    `emb_pressure_exp <= 0` => 1.0 exato (inerte, backward-compat bit-identico).
    """
    if mat.emb_pressure_exp <= 0.0:
        return 1.0
    p_ref = mat.p_ref_emb
    if p_ref <= 0.0:
        return 1.0
    p_init = max(state.F_0_init, 0.0) / max(geom.A_contact, 1e-12)
    if p_init <= 0.0:
        return 1.0
    return min(1.0, (p_init / p_ref) ** mat.emb_pressure_exp)


def creep_conformance_factor(state: SlowState, geom: JointGeometry,
                             mat: JointMaterial) -> float:
    """Pre-conformacao do reservatorio LENTO (spec 2026-07-08 slow-tail).

    Mesma fisica do embedding_conformance_factor aplicada ao canal lento
    (CreepLoss = assentamento de interface log-t nesta classe de junta): o dado
    Liu2017 mostra a perda LENTA absoluta caindo ~F0^-1 (fracional ~F0^-2),
    enquanto o Norton e' fracional-flat — o aperto depleta tambem o reservatorio
    lento, com expoente mais fraco (n_slow~2 vs n_fast~3-4). Reusa p_ref_emb.
    creep_conform_exp<=0 => 1.0 exato (inerte). Keyed em F0_init (sem feedback).
    NB: em rigs onde a perda lenta e' creep de BULK genuino (gaxetas, alta T),
    manter 0 — a reinterpretacao interface-settlement e' por classe de junta."""
    return _conformance_S(state, geom, mat.p_ref_emb, mat.creep_conform_exp)


def settling_amplitude_factor(state: SlowState, mat: JointMaterial,
                              F_amp: float, theta_load: float) -> float:
    """Fator de amplitude relativa do assentamento (estudo de variaveis item 1,
    spec 2026-07-08). S_rho = min(1, (rho/rho_ref)^q), rho = F_ax_amp/F_0_init.

    UNIFICA os dois sweeps do Liu2017 (fast-loss ~ rho^3.4 no A_F-sweep E no
    P0-sweep) — substitui emb_conform_exp no canal axial (reducao de variavel).
    Keyed em F_0_INIT (fixo no run; sem feedback; Norton fechado preservado).
    So atua com componente axial: transversal (F_ax<=1e-6) => 1.0 exato.
    emb_amp_exp<=0 => 1.0 exato (inerte, backward-compat bit-identical)."""
    if mat.emb_amp_exp <= 0.0:
        return 1.0
    F_ax = abs(F_amp * np.cos(theta_load))
    if F_ax <= 1e-6 or state.F_0_init <= 0.0:
        return 1.0
    rho = F_ax / state.F_0_init
    return min(1.0, (rho / max(mat.rho_ref_emb, 1e-9)) ** mat.emb_amp_exp)


def _conformance_S(state: SlowState, geom: JointGeometry,
                   p_ref: float, exp: float) -> float:
    if exp <= 0.0:
        return 1.0
    p_init = max(state.F_0_init, 0.0) / max(geom.A_contact, 1e-12)
    if p_init <= 0.0:
        return 1.0
    return min(1.0, (p_ref / p_init) ** exp)


def self_locking_gate(state: SlowState, mat: JointMaterial,
                      geom: Optional[JointGeometry] = None) -> float:
    """Gate de arresto por nucleo auto-travado (spec 2026-07-07, roadmap #4).

    O ratcheting transversal so drena a pre-carga em EXCESSO de um nucleo
    auto-travado ``F_min = loose_arrest_floor·F_0_init`` (stick core de
    Cattaneo-Mindlin: a zona central de stick restaura o atrito estatico de rosca
    e trava um clamp residual contra o off-torque da helice). ``g = max(0, 1 -
    F_min/F_0)``: quando ``F_0 -> F_min`` o excesso drenavel some e a rotacao para
    ⇒ o runaway (``T_resist ∝ F_0``) vira S-curve com ponto fixo ESTAVEL em F_min.
    Multiplica ``d_theta`` (logo dF_0 e dE juntos, conservacao preservada). Com
    ``loose_arrest_floor <= 0`` retorna 1.0 exato (sem arresto, backward-compat =
    runaway atual). Compoe (ortogonal) com ``loose_torsion_mode``.

    EXPOENTE DE APROXIMACAO (prereg grupo A, 2026-07-27): ``g`` e' elevado a
    ``mat.arrest_approach_exp``. Com o default 1.0 a funcao retorna a expressao
    anterior por EARLY-RETURN explicito — a bit-identidade e' garantida por
    construcao, sem depender de ``pow(x, 1.0) == x`` do libm (G1 do prereg exige
    zero diferenca, nao diferenca pequena). ``exp > 1`` faz a taxa morrer mais
    cedo perto do piso => desaceleracao ao plato.

    TAXA RESIDUAL SUB-ARRESTO (prereg 2026-08-15-lei-de-taxa-rotacional):
    ``loose_arrest_residual > 0`` poe um PISO na propria taxa —
    ``g = max(residual·g0, g_arresto)`` com ``g0 = g(N=1) = 1 - floor`` (forma
    fechada, sem estado) — de modo que abaixo do limiar o canal retem uma
    fracao da taxa inicial em vez de morrer. Motivo medido (item Q): o dado do
    ICMEZ atravessa o piso adotado e segue caindo a ~50% da taxa de meio,
    enquanto o gate zera. 0.0 (default) = expressao anterior, BIT-IDENTICA
    (early-return explicito, sem depender de max(0.0, x) == x).
    """
    if mat.loose_arrest_floor <= 0.0 or state.F_0 <= 0.0:
        return 1.0
    f_min = mat.loose_arrest_floor * max(state.F_0_init, 0.0)
    # ANULACAO DO PISO POR CARGA AXIAL EXTERNA (C3, 2026-08-21). Ramo so' entra
    # com o campo LIGADO **e** BC externa presente **e** geom disponivel: sem os
    # tres, `f_min` fica intocado e o gate e' BIT-IDENTICO ao anterior. Isso
    # cobre de uma vez o default (campo 0) e as 4 baselines do ECCLES
    # (F_ax_ext = 0), sem depender de `x * 1.0 == x`.
    if (mat.ax_floor_override > 0.0 and state.F_ax_ext > 0.0
            and geom is not None and f_min > 0.0):
        _F_sep = F_sep_axial(state, geom, mat)
        _den = mat.ax_floor_override * max(_F_sep, 1e-9)
        f_min *= max(0.0, 1.0 - state.F_ax_ext / _den)
    g = max(0.0, 1.0 - f_min / state.F_0)
    e = mat.arrest_approach_exp
    if e != 1.0:
        g = g ** e
    r = mat.loose_arrest_residual
    if r <= 0.0:                      # default: caminho antigo, bit-identico
        return g
    return max(r * (1.0 - mat.loose_arrest_floor), g)


def F_slip_transverse(state: SlowState, mat: JointMaterial) -> float:
    """Threshold de slip transversal (Pai-Hess), atrito modulado por dano."""
    return SLIP_ONSET_PAI_HESS * mu_bearing_eff(state, mat) * max(state.F_0, 0.0)


def k_tr_transverse(geom: JointGeometry, mat: JointMaterial) -> float:
    """Rigidez transversal de onset de slip (spec 2026-07-05). 'axial_frac'
    (default, backward-compat) = 0.3*k_j_init (~1e9 -> delta_t~0, tudo gross
    slip). 'bending' = flexao do parafuso c_bend*E*I/L_eff^3 (I=pi*d^4/64,
    d~d_2), ~1e7 -> delta_t~0.3mm, prop F0*L^3/(E*d^4) (unifica amplitude +
    pre-carga + rigidez de membro). geom None => axial_frac (bending precisa da
    geometria)."""
    if mat.k_tr_mode == "bending" and geom is not None:
        d = geom.d_2                              # diametro efetivo de flexao
        I = np.pi * d ** 4 / 64.0
        k = max(mat.c_bend * geom.E * I / max(geom.L_eff, 1e-6) ** 3, 1.0)
    else:
        k = max(mat.k_j_init * 0.3, 1.0)
    # CISALHAMENTO DO MEMBRO em serie (item 2 do estudo de variaveis, HDPE
    # 2026-07-08): membro complacente (polimero, G~0.3 GPa) absorve parte do
    # deslocamento imposto em cisalhamento proprio (delta_m = F*t/(G*A)) —
    # mais espesso => menos slip chega a interface (dado Rousseau HDPE: t14
    # NAO colapsa; o modelo so-flexao preve a ordem INVERTIDA, ~1/L^3).
    # k_member_shear = G*A/t computado por-caso pelo harness (per-rig: G*A).
    # 0 = OFF (bit-identical; aco G~80 GPa => termo desprezivel, nao setar).
    if mat.k_member_shear > 0.0:
        k = 1.0 / (1.0 / k + 1.0 / mat.k_member_shear)
    return k


def loosening_slip_gate(state: SlowState, geom: JointGeometry,
                        mat: JointMaterial, slip_amp: Optional[float]) -> float:
    """Gate da fracao de gross-slip para o loosening rotacional (spec 2026-07-06).
    Junker precisa de GROSS slip (ratcheting); em partial slip (stick) o backing-
    off e suprimido. g = slip/(slip+delta_t) = (delta-delta_t)/delta = fracao de
    gross-slip do curso, delta_t = F_slip/k_tr. "off" ou slip_amp None (force-mode)
    => 1.0 (backward-compat).

    slip_regime_mode="cattaneo_mindlin" (spec 2026-07-07) PRECEDE: afia a fracao
    de gross-slip com o expoente slip_regime_sharpness k (k=1 == fracao atual;
    k>1 suprime partial slip => so gross slip profundo afrouxa)."""
    if mat.slip_regime_mode == "cattaneo_mindlin":
        if slip_amp is None:
            return 1.0
        # delta_t consistente com resolve_transverse_slip: take-up fixo + elastico
        delta_t = (mat.delta_free
                   + F_slip_transverse(state, mat) / max(k_tr_transverse(geom, mat), 1e-12))
        frac = slip_amp / max(slip_amp + delta_t, 1e-12)      # = max(0, 1 - 1/r)
        return float(max(frac, 0.0) ** max(mat.slip_regime_sharpness, 1e-6))
    if mat.loosening_slip_coupling == "off" or slip_amp is None:
        return 1.0
    if mat.loosening_slip_coupling == "gross_fraction":
        delta_t = (mat.delta_free
                   + F_slip_transverse(state, mat) / max(k_tr_transverse(geom, mat), 1e-12))
        return slip_amp / max(slip_amp + delta_t, 1e-12)
    return 1.0


def partial_slip_gate(state: SlowState, geom: JointGeometry, mat: JointMaterial,
                      F_amp: float, theta_load: float, channel: str,
                      slip_amp: Optional[float]) -> float:
    """Cattaneo-Mindlin partial-slip energy fraction p/ wear/fretting (spec
    2026-07-07). g = 1-(1-min(r,1))^m, r=Q/(mu*F0*kappa); =1 p/ r>=1. Graduado
    abaixo do onset (partial slip ainda desgasta) => F0 maior -> r menor -> menos
    perda de preload (Liu2017 slope). channel "fret" (Q=F_amp*|cos|, mu_thread) |
    "wear" (Q=F_amp*|sin|, mu_bearing_eff). slip_regime_mode != 'cattaneo_mindlin'
    => 1.0 exato (backward-compat). slip_amp aceito p/ assinatura uniforme."""
    if mat.slip_regime_mode != "cattaneo_mindlin":
        return 1.0
    F0 = max(state.F_0, 0.0)
    if F0 <= 0.0:
        return 1.0
    if channel == "fret":
        Q = abs(F_amp * np.cos(theta_load)); mu = mat.mu_thread
    else:
        Q = abs(F_amp * np.sin(theta_load)); mu = mu_bearing_eff(state, mat)
    cap = mu * F0 * max(mat.slip_capacity_coeff, 1e-9)
    if cap <= 0.0:
        return 1.0
    r = Q / cap
    if r >= 1.0:
        return 1.0
    return float(1.0 - (1.0 - max(r, 0.0)) ** max(mat.partial_slip_exp, 1e-6))


def flank_wear_axial_term(state: SlowState, geom: JointGeometry,
                          mat: JointMaterial, F_amp: float,
                          theta_load: float, freq: float
                          ) -> Tuple[float, float]:
    """Canal L1 (plano L1-L7 task-3, 2026-07-16): desgaste de flanco de rosca
    PROPORCIONAL a amplitude de carga AXIAL A_F — forma independente do
    k_thread_fret legado (que e' hardcoded linear em F_ax; spec 2026-07-06).
    Parametriza por PRESSAO de flanco p_flank=F_0/A_s (nao forca) com
    expoente de amplitude AJUSTAVEL flank_amp_exp (Liu 2020 sugere 1.5-1.6,
    super-linear).

    Falsificacao-alvo (MODEL_LEGITIMACY.md secao 4.6, roadmap #9):
    d(fim)/d(A_F) ~ 0 no modelo hoje vs -2.216e-5/N no dado Liu2017 — este
    canal supre a forma faltante.

    Retorna (d_w, dE): d_w = profundidade de desgaste [m] (fator
    k_wear_flank, tunavel/fitavel), dE = trabalho friccional REAL no flanco
    (mu_thread*F_clamp*slip_dist, SEM o tuner de wear-rate nem o expoente de
    amplitude — mesmo padrao do WearLoss p/ conservacao: a nao-linearidade de
    amplitude so escala dF_0, nao dE).

    NAO verifica flank_wear_on nem o modo forca/axial — o guard fica no site
    de uso (ThreadFrettingLoss.rate), mesmo idioma de famp_gross_slip_ceiling
    (flag OFF curto-circuita ANTES desta funcao ser chamada).

    k_wear_flank [1/Pa] semeado do KB (kb.wear_spec_anchor("thread",
    "35CrMo-SCM435") = 8.34e-15, Zhang 2019, EFA doi 10.1016/
    j.engfailanal.2019.05.001) — a leitura do KB acontece na CALIBRACAO (Task
    4), NUNCA aqui (engine so-constantes).
    """
    F_ax = F_amp * abs(np.cos(theta_load))
    s_th = F_ax / max(geom.k_b, 1.0)               # slip elastico de flanco (k_b = rigidez axial da rosca)
    return flank_wear_from_slip(state, geom, mat, s_th, freq)


def flank_wear_from_slip(state: SlowState, geom: JointGeometry,
                         mat: JointMaterial, s_th: float,
                         freq: float) -> Tuple[float, float]:
    """Nucleo do canal L1 (compartilhado pelas rotas AXIAL e TRANSVERSAL —
    F4 L1v2, 2026-07-22): desgaste de flanco a partir do slip de flanco
    s_th [m], qualquer que seja a excitacao que o produziu (axial: F_ax/k_b;
    transversal: slip_amp resolvido). Extracao MECANICA de
    flank_wear_axial_term — mesmas operacoes de float na mesma ordem
    (bit-identico no caminho axial; testado).

    L1 v2 candidato (c) — F4 do prompt-mestre (prereg B1-v3, 2026-07-22):
    LIMIAR de slip do flanco. Abaixo de flank_s_crit o regime e' stick/
    shakedown (fretting sem transporte liquido de material — Mantyla 2020/
    Juoksukangas 2016); o desgaste e' dirigido pelo EXCESSO s-s_crit.
    Racional da falsificacao T4: power-law puro nao consegue ser fraco no
    NIVEL e forte no SLOPE simultaneamente (o fit saturava k no limite
    inferior); com limiar, d(wear)/dA_F e' maximo perto do limiar (slope
    ingreme) e o canal zera em amplitude baixa. flank_s_crit=0.0 (default)
    => s_eff = s_th EXATO — bit-identico ao canal L1 v1 (default-inerte
    sem flag). dE NAO usa o limiar (atrito dissipa mesmo em stick parcial
    — mesma convencao "dF_0 sim, dE nao" do damage/slip_onset_gate)."""
    F_clamp = max(state.F_0, 0.0)
    s_eff = max(s_th - mat.flank_s_crit, 0.0)
    slip_dist = 2.0 * s_eff                        # ida+volta (convencao do canal L1)
    p_flank = F_clamp / max(geom.A_s, 1e-12)       # pressao de flanco (F_0 / area engajada)
    d_w = mat.k_wear_flank * p_flank * slip_dist ** mat.flank_amp_exp
    if mat.flank_fret_depth > 0.0:
        # SATURACAO por profundidade restante (D-Q). Mesma forma do
        # EmbeddingLoss state-based: o que resta e' que governa o incremento.
        # 0 => OFF exato (guarda acima). Clamp em [0,1]: profundidade
        # consumida acima do alvo zera o transporte, nao o inverte.
        _rest = 1.0 - state.delta_thread_fret / mat.flank_fret_depth
        d_w *= min(max(_rest, 0.0), 1.0)
    if mat.fret_freq_exp != 0.0 and freq > 0.0:
        # mesmo fator de dependencia de frequencia do canal legado (reuso).
        d_w *= (mat.f_ref_fret / freq) ** mat.fret_freq_exp
    dE = mat.mu_thread * F_clamp * (2.0 * s_th)    # slip REAL, sem limiar
    return d_w, dE


def T_resistance(state: SlowState, geom: JointGeometry,
                 mat: JointMaterial) -> float:
    """Torque resistente (atrito filete + bearing, bearing modulado por dano)."""
    F0 = max(state.F_0, 0.0)
    T_thr = mat.mu_thread * F0 * geom.d_2 / (2.0 * np.cos(THREAD_FLANK_ANGLE))
    T_brg = mu_bearing_eff(state, mat) * F0 * geom.r_bearing
    return T_thr + T_brg


def tightening_torque(F0: float, state: SlowState, geom: JointGeometry,
                      mat: JointMaterial) -> float:
    """Torque de aperto (Motosh) para atingir a pre-carga F0 [N] -> T [N.m].

        T = F0 * ( p/2pi + mu_th*d2/(2 cos alpha) + mu_bearing_eff(D)*r_bearing )

    Reusa os termos de atrito de T_resistance + o termo de avanco (lead). Linear
    em F0, entao a pre-carga atingida por um torque T e
    F0 = T / tightening_torque(1.0, state, geom, mat). Reusa mu_bearing_eff(D) e
    mu_thread_tighten_eff(D) (galling): com k_dmg_mu=0 e k_gall=0 (frozen) o
    coeficiente independe de D (recuperacao plana, backward-compat).
    """
    coeff = (geom.lead_per_radian
             + mu_thread_tighten_eff(state, mat) * geom.d_2 / (2.0 * np.cos(THREAD_FLANK_ANGLE))
             + mu_bearing_eff(state, mat) * geom.r_bearing)
    return max(F0, 0.0) * coeff


# ============================================================================
# Matrizes [M], [K(s)], [C(s)]
# ============================================================================

def M_matrix(mat: JointMaterial) -> np.ndarray:
    """[M] 3×3 com DOFs (x, y, θ). Constante."""
    return np.diag([mat.m_x, mat.m_y, mat.I_theta])


def K_matrix(state: SlowState, geom: JointGeometry, mat: JointMaterial,
             slip_y: bool = False, slip_theta: bool = False) -> np.ndarray:
    """
    [K(s)] 3×3 com DOFs (x, y, θ).

    Slip flags removem entradas correspondentes (vão pra {F} via atrito).
    """
    K = np.zeros((3, 3))
    kj_ax = k_j_ax(state, mat)
    kb = geom.k_b

    # x-x: rigidez axial (bolt + joint axial)
    K[0, 0] = kb + kj_ax

    # y-y: stick → rigidez transversal do joint (alta); slip → 0
    if not slip_y:
        # k_j_tr é grande quando stuck — modelado como múltiplo de k_j_ax
        K[1, 1] = mat.k_j_init * 0.3        # fator anisotrópico aproximado
    # senão K[1,1] = 0 (slip transversal: força em {F})

    # θ-θ: stick → rigidez rotacional via thread; slip → 0
    if not slip_theta:
        # Equivalent stiffness via helix (k_b projetado em θ)
        K[2, 2] = kb * geom.lead_per_radian**2
        # x-θ: acoplamento helicoidal (Fator 2, simétrico)
        K[0, 2] = kb * geom.lead_per_radian
        K[2, 0] = K[0, 2]

    return K


def C_matrix(state: SlowState, geom: JointGeometry,
             mat: JointMaterial) -> np.ndarray:
    """[C(s)] = α[M] + β[K(s)] — Rayleigh."""
    M = M_matrix(mat)
    K = K_matrix(state, geom, mat)
    return mat.rayleigh_alpha * M + mat.rayleigh_beta * K


# ============================================================================
# Energias (em função de s)
# ============================================================================

def U_internal(state: SlowState, geom: JointGeometry,
               mat: JointMaterial) -> float:
    """
    Energia elástica armazenada com F_ext=0 (pré-tensão pura):
        U_int(F_0) = F_0²/(2k_b) + F_0²/(2·k_j_ax(F_0))
    Forma não-parabólica: F_0^(2−α) — fonte do runaway.
    """
    if state.F_0 <= 0:
        return 0.0
    kj = k_j_ax(state, mat)
    U_bolt = state.F_0**2 / (2.0 * geom.k_b)
    U_jt = state.F_0**2 / (2.0 * kj) if kj > 0 else 0.0
    return U_bolt + U_jt


def U_loaded(state: SlowState, geom: JointGeometry, mat: JointMaterial,
             F_ax_ext: float) -> float:
    """Energia elástica armazenada com F_ext_axial aplicada.

    `mat.phi_load_dep>0` (L2, spec 2026-07-16 Fatia 3): modula a FRAÇÃO DE
    CARGA DO LADO DO MEMBRO/JUNTA — (1−Φ), o termo que reduz `F_joint` — com a
    forma ELÍPTICA de Grosse (dissertação 1990, per-junta) em vez da reta
    padrão Φ_eff. F_m/F_i = 1 − sqrt(max(0, 2·λ−λ²)), λ = F_ax_ext /
    (phi_load_dep·F_i), F_i = state.F_0 (pré-carga corrente, base local deste
    diagrama de junta). λ=0 (sem carga extra) ⇒ fração=1 (F_joint=F_i, igual
    ao caso linear em F_ax_ext=0); λ→1 (carga extra perto do crítico
    phi_load_dep·F_i) ⇒ fração→0 (colapso do lado do membro). λ é CLIPADO em
    [0,1] — além do crítico a curva fechada (2λ−λ²) desceria de volta
    (não-físico); a fração fica saturada em 0, não reaparece. `F_bolt`
    permanece com a partição LINEAR Φ (o campo só modula o lado do membro,
    não o do parafuso). 0.0 (default) = OFF exato, usa a partição linear
    (1−Φ) atual (backward-compat bit-identical).
    """
    if state.F_0 <= 0:
        return F_ax_ext**2 / (2.0 * geom.k_b) if F_ax_ext > 0 else 0.0
    kj = k_j_ax(state, mat)
    Phi = Phi_eff(state, geom, mat)
    F_sep = F_sep_axial(state, geom, mat)
    if F_ax_ext < F_sep:
        F_bolt = state.F_0 + Phi * F_ax_ext
        if mat.phi_load_dep > 0.0:
            lam = min(max(F_ax_ext / (mat.phi_load_dep * state.F_0), 0.0), 1.0)
            frac_m = 1.0 - np.sqrt(max(0.0, 2.0 * lam - lam**2))
            F_joint = state.F_0 * frac_m
        else:
            F_joint = state.F_0 - (1 - Phi) * F_ax_ext
        return F_bolt**2 / (2 * geom.k_b) + F_joint**2 / (2 * kj)
    else:
        return F_ax_ext**2 / (2.0 * geom.k_b)


def resolve_transverse_slip(state: SlowState, mat: JointMaterial,
                            F_amp: float, theta_load: float,
                            delta_amp: Optional[float] = None,
                            geom: Optional[JointGeometry] = None
                            ) -> float:
    """
    Resolve a amplitude de slip transversal por ciclo.

    - Force-controlled (delta_amp=None): slip = (F_tr - F_slip) / k_j_tr_local
      Usa a elasticidade local pra estimar quanto escorrega.
    - Displacement-controlled (delta_amp dado): slip = max(0, delta - F_slip/k_tr)
      Usa o deslocamento imposto direto, descontando a parte elástica
      pre-onset de slip. Mais fiel ao teste Junker real.

    Returns slip_amp [m] (>= 0). Zero significa stick (sem hysteresis).
    """
    if state.F_0 <= 0:
        return 0.0
    F_slip = F_slip_transverse(state, mat)
    k_tr = k_tr_transverse(geom, mat)
    if delta_amp is not None:
        # Displacement-controlled: slip = δ_imposto − take-up FIXO (delta_free,
        # F0-independente, spec 2026-07-08) − δ_elastico ate o onset (∝F0).
        delta_slip_onset = mat.delta_free + F_slip / k_tr
        return max(0.0, delta_amp - delta_slip_onset)
    # Force-controlled (legado): slip = (F_tr - F_slip) / k_tr_local
    F_tr = F_amp * np.sin(theta_load)
    if F_tr > F_slip:
        return (F_tr - F_slip) / k_tr
    return 0.0


def W_ext_per_cycle(state: SlowState, geom: JointGeometry,
                    mat: JointMaterial, F_amp: float,
                    theta_load: float,
                    delta_amp: Optional[float] = None) -> float:
    """
    Trabalho externo NET por ciclo = area da loop de hysteresis.

    Em regime puramente elástico (no slip), W_ext = 0 (loading + unloading
    cancelam). Quando há slip transversal, há hysteresis = 4·μ·F·δ_slip
    por ciclo. (Slip no filete entra via RotationalLooseningLoss.)

    Em modo displacement-controlled (delta_amp dado), δ_slip vem do
    deslocamento imposto em vez da força.
    """
    if state.F_0 <= 0:
        return 0.0
    slip_amp = resolve_transverse_slip(state, mat, F_amp, theta_load, delta_amp,
                                       geom=geom)
    if slip_amp <= 0:
        return 0.0
    return 4.0 * mu_bearing_eff(state, mat) * state.F_0 * slip_amp


def W_viscous_per_cycle(state: SlowState, geom: JointGeometry,
                        mat: JointMaterial, F_amp: float,
                        theta_load: float, freq: float) -> float:
    """
    Energia amortecida por viscoso (Rayleigh) em um ciclo harmônico.
    Para um modo com freq ω: W = π · ω · c · X²  (Rayleigh + harmônico).
    Approximação simples — modal axial dominante.
    """
    if freq <= 0:
        return 0.0
    omega = 2 * np.pi * freq
    F_ax = F_amp * np.cos(theta_load)
    kj = k_j_ax(state, mat)
    k_eff = geom.k_b + kj if kj > 0 else geom.k_b
    X = F_ax / k_eff   # amplitude de deslocamento quasi-estática
    # Damping axial efetivo via Rayleigh:
    c_axx = mat.rayleigh_alpha * mat.m_x + mat.rayleigh_beta * k_eff
    return np.pi * omega * c_axx * X**2


# ============================================================================
# Mecanismos de perda — interface plug-in
# ============================================================================

class LossMechanism(ABC):
    """Interface plug-in pra um mecanismo de perda de pré-carga."""
    name: str = "abstract"

    @abstractmethod
    def rate(self, state: SlowState, geom: JointGeometry,
             mat: JointMaterial, F_amp: float, theta_load: float,
             freq: float, cycle_N: int,
             slip_amp_override: Optional[float] = None) -> Dict[str, float]:
        """
        Calcula a perda de pré-carga e dissipação de UM ciclo.

        Args:
          state, geom, mat: estado e configuracao da junta.
          F_amp: amplitude de forca [N] (drive do ciclo).
          theta_load: angulo de carregamento [rad] (0=ax, pi/2=tr).
          freq: frequencia [Hz].
          cycle_N: numero do ciclo atual.
          slip_amp_override: (opcional) [m] amplitude de slip transverso
            pre-computada (typically a partir de um delta_amp imposto).
            Quando None, mecanismos que precisam de slip usam o calculo
            elastico-baseado-em-forca.

        Returns dict com chaves:
          dF_0: float — variação na pré-carga (≤ 0)
          dE_dissipated: float — energia dissipada por este mecanismo [J]
          ds: dict[str, float] — incrementos nos demais campos de SlowState
        """
        ...


class EmbeddingLoss(LossMechanism):
    """Embedding plástico das asperezas. Domina nos primeiros ~N_emb ciclos.

    Forma state-based (decaimento geométrico exato, spec 2026-07-02 §2.4):
    o incremento depende da profundidade ainda disponível, não do relógio de
    ciclos. Para junta virgem reproduz EXATAMENTE a forma fechada de Norton
        δ_emb(N) = δ_target·(1 − e^{−N/N_emb}),
    e permite estado inicial não-nulo (arruela reusada, emb_consumed_frac>0).
    δ_target = k_emb_scale·emb_depth preserva a semântica legada do tuner
    (assíntota escalada) até a remoção da camada de tuners (Estágio B).
    """
    name = "embedding"

    def rate(self, state, geom, mat, F_amp, theta_load, freq, cycle_N,
             slip_amp_override=None, delta_amp=None):
        # BEDDING SLIP-GATED (sec4.29, proveniencia dupla: porca COLADA de
        # Jiang isola o bedding como ratcheting SOB ciclos de escorregamento;
        # trade frac<->amp0p25 do sec4.19 apontava o mesmo): o reservatorio
        # FRACIONAL (vibracao-dirigido) e' gateado pela fracao de gross-slip
        # (slip/(slip+delta_t))^q. Sub-limiar (slip~0) => so o reservatorio de
        # profundidade (estatico). emb_slip_gate=0 => 1.0 exato (inerte).
        g_slip = 1.0
        if mat.emb_slip_gate > 0.0 and slip_amp_override is not None:
            dt = (mat.delta_free
                  + F_slip_transverse(state, mat)
                  / max(k_tr_transverse(geom, mat), 1e-12))
            frac = max(slip_amp_override, 0.0) / max(
                max(slip_amp_override, 0.0) + dt, 1e-12)
            g_slip = frac ** mat.emb_slip_gate
        # Estágio B: sem tuner (k_emb_scale removido). O emb_depth JA e' a
        # asintota fisica (a semantica do tuner foi foldada nele pelo shim).
        target = (mat.emb_depth
                  * embedding_conformance_factor(state, geom, mat)
                  # ramo DIRIGIDO POR PRESSAO (prereg 2026-08-16): 1.0 exato
                  # enquanto `emb_pressure_exp` == 0, que e' o default.
                  * embedding_pressure_factor(state, geom, mat)
                  * settling_amplitude_factor(state, mat, F_amp, theta_load)
                  # P-9 v2 (2026-08-09, assinada): gate de FREQUENCIA no ALVO.
                  # ⚠️ NO ALVO, e nao no incremento — e a diferenca foi MEDIDA,
                  # nao estimada. A v1 gateava `d_delta` (seguindo o precedente
                  # do `stage1_amp_gate`) e passou os gates sendo um NO-OP: com
                  # `N_emb`=50 e curvas de 5300 ciclos (106x), a fracao do alvo
                  # atingida e' 1,0000 com e sem gate — o incremento so' muda
                  # QUANDO o canal satura, nao QUANTO. No alvo, a mesma lei e os
                  # mesmos numeros derrubam o vies da curva de 10 Hz em 81 %.
                  # Fisica: o PR-3 poe o gate de AMPLITUDE no incremento de
                  # proposito ("sub-limiar o assentamento fica lento, nao
                  # menor"); para FREQUENCIA o argumento inverte — o mesmo numero
                  # de ciclos a 10 Hz dispoe de METADE do tempo, logo consolida
                  # MENOS, nao "mais devagar".
                  * stage1_freq_gate(mat, freq)
                  + mat.emb_load_frac * g_slip * state.F_0_init
                  / max(geom.k_b, 1e-9))
        remaining = max(target - state.delta_emb, 0.0)
        # RELOGIO DEPENDENTE DE DESLOCAMENTO (2026-08-14): N_emb_eff =
        # N_emb*(delta_ref/delta). Expoente 1 vem do mecanismo (esgotamento por
        # slip acumulado), nao de fit — ver o comentario do campo em
        # JointMaterial. `emb_clock_delta_ref == 0` => n_eff e' `mat.N_emb`
        # BIT-A-BIT (nao ha multiplicacao por 1.0, o ramo nem roda).
        # ⚠️ O guard `max(..., 1e-9)` fica DENTRO do ramo novo, de proposito.
        # Posto fora, ele mudaria tambem o caminho DESLIGADO: com N_emb=0 o
        # original divide por zero (inf/nan) e o guard devolveria um numero
        # limpo. "Default-inerte" tem de valer INCLUSIVE para entrada
        # degenerada — senao a forma opt-in vaza por onde ninguem testa.
        n_eff = mat.N_emb
        if mat.emb_clock_delta_ref > 0.0 and delta_amp:
            n_eff = max(mat.N_emb * (mat.emb_clock_delta_ref
                                     / max(abs(delta_amp), 1e-12)), 1e-9)
        # RELOGIO SIGMOIDE (2026-08-21): Weibull m>1 via N implicito da
        # fracao consumida — plato+joelho+saturacao. m=1 (default) = ramo
        # antigo EXATO (early-branch).
        if mat.emb_clock_m != 1.0 and target > 1e-15:
            _m = max(mat.emb_clock_m, 0.05)
            _phi = min(max(state.delta_emb / target, 0.0), 1.0 - 1e-12)
            _neq = (n_eff * (-np.log(1.0 - _phi)) ** (1.0 / _m)
                    if _phi > 0.0 else 0.0)
            _phi2 = 1.0 - np.exp(-(((_neq + 1.0) / max(n_eff, 1e-9)) ** _m))
            d_delta = max(_phi2 - _phi, 0.0) * target
        else:
            d_delta = remaining * (1.0 - np.exp(-1.0 / n_eff))
        # PR-3 2026-08-01: relogio de estagio I gateado pelo regime de
        # amplitude (dref=0 default => 1.0 exato). Gate no INCREMENTO, nao
        # no alvo — sub-limiar o assentamento fica lento, nao menor.
        d_delta *= stage1_amp_gate(mat, delta_amp)
        # Perda de preload: ΔF_0 = −k_b · Δδ (encurtamento da pilha)
        dF_0 = -geom.k_b * d_delta
        # Trabalho plástico = F_clamp · Δδ
        dE = max(state.F_0, 0.0) * d_delta
        return dict(dF_0=dF_0, dE_dissipated=dE,
                    ds=dict(delta_emb=d_delta))


def stage1_freq_gate(mat, freq):
    """Gate de FREQUENCIA do relogio de Estagio I (P-9, assinada 2026-08-09).

    `(f_ref/freq)^n` sobre o `d_delta` do **EmbeddingLoss** — e SO' dele.
    `s1_freq_exp = 0` (default) => 1.0 exato, engine bit-identico.

    ## Por que so' o embedding

    O `CreepLoss` ja e' TEMPORAL por construcao (`t_cur = cycle_N/freq`, 4
    sitios): 1000 ciclos a 5 Hz nao sao 1000 ciclos a 10 Hz para ele. O
    `EmbeddingLoss` e' puramente CICLICO — `freq` aparece so' na assinatura do
    `rate()`, nunca no corpo. Foi medir essa assimetria que transformou a P-9 de
    "falta frequencia nos relogios de Estagio I" (plural, difuso) em "falta no
    `EmbeddingLoss`" (uma classe, com alvo). Aplicar o gate tambem ao creep
    contaria a frequencia DUAS VEZES.

    ## Procedencia da lei — nao e' nova

    E' a MESMA de `fret_freq_exp`, que o **D-V** assinou para o canal de flanco:
    `d_fret *= (f_ref_fret/freq)**fret_freq_exp` com expoente 1,0 (*"taxa de
    fretting proporcional a 1/f"*), lido do proprio sweep de frequencia do
    Li2022ti, nao fitado ao MAE. Fisica: mais tempo de dwell por ciclo => mais
    consolidacao por ciclo.

    ## ⚠️ So' e' identificavel onde a FONTE varre frequencia

    Em fonte mono-frequencia este fator e' constante e apenas re-escala
    `N_emb` — inseparavel dele, logo NAO falsificavel. Por isso o default e' OFF
    e a aplicacao e' per-fonte: na biblioteca so' o `YANG_2019` varre (5 e
    10 Hz, com um par de mesma amplitude). Com `f_ref` = frequencia de
    calibracao da fonte, o fator vale 1,0 EXATO nas curvas dessa frequencia —
    inercia por construcao, nao por sorte.
    """
    n = float(getattr(mat, "s1_freq_exp", 0.0) or 0.0)
    if n <= 0.0 or not freq or float(freq) <= 0.0:
        return 1.0
    fref = max(float(getattr(mat, "s1_freq_ref", 1.0) or 1.0), 1e-9)
    return (fref / float(freq)) ** n


def stage1_amp_gate(mat, delta_amp):
    """Gate de regime de amplitude dos relogios de ESTAGIO I (PR-3 2026-08-01).

    g = floor + (1-floor) * d^p / (d^p + dref^p), d = delta_amp imposto.
    dref <= 0 (default) OU delta_amp None (modo forca) => 1.0 EXATO (inerte).
    Multiplica so o d_delta de Embedding/Creep — dF_0/dE derivam dele nos
    dois mecanismos, entao a conservacao fica intacta por construcao.
    """
    dref = getattr(mat, "s1_amp_gate_dref", 0.0)
    if dref <= 0.0 or delta_amp is None:
        return 1.0
    d = max(float(delta_amp), 0.0)
    p = max(float(mat.s1_amp_gate_p), 1e-9)
    floor = min(max(float(mat.s1_amp_gate_floor), 0.0), 0.999999)
    dp = d ** p
    return floor + (1.0 - floor) * dp / (dp + dref ** p)


class CreepLoss(LossMechanism):
    """Assentamento de interface LOG-TEMPO — NAO é Norton-Bailey.

    Lei implementada (default, `mat.creep_mode == ""`), log-t e linear em
    F_0, ILIMITADA no tempo:

        δ_creep(t) = C_creep · F_0 · ln(t/t_0 + 1)

    incrementada por ciclo (t_cur, t_prev = cycle_N/freq, (cycle_N−1)/freq;
    o deslocamento de referência `ln(t_0)` cancela na diferença, então o
    incremento é o mesmo escrevendo o fechado como ln(t+t_0) ou ln(t/t_0+1)):

        dδ = C_creep · F_0 · [ln(t_cur + t_0) − ln(t_prev + t_0)]
        dF_0 = −k_b · dδ

    O docstring anterior chamava isso de "Norton-Bailey simplificado" — Norton-
    Bailey é lei de POTÊNCIA em F_0/tensão (creep de BULK do fuste, cf. Jiang
    2024, candidato a um futuro 5º mecanismo p/ junta quente — NÃO é isto).
    Esta é uma lei LOGARÍTMICA no tempo, típica de relaxação/assentamento de
    interface — e por coincidência feliz é a MESMA FORMA da regressão de
    faiamento do Nah 2014 (`Creep = α + β·log₁₀(t)`, KB `creep_class`,
    `New_Theory/r5_anchors.json`): o engine já estava na forma certa para
    faiamento: só o NOME no docstring estava errado, não a física.

    Forma SATURANTE opt-in (Alamos 2021/2022, creep de contato de 1os
    princípios; `mat.creep_mode == "saturating"` E `mat.creep_t_c > 0`,
    senão cai no ramo log-t acima):

        δ_creep(t) = δ_max · (1 − exp[−(t/creep_t_c)**creep_alpha_sat])

    BOUNDED (δ_creep → δ_max quando t → ∞), ao contrário da forma log-t
    (cresce sem limite, ainda que cada vez mais devagar). `δ_max` deriva do
    MESMO `C_creep` (continuidade dimensional) — reusa o MESMO produto
    `C_creep·F_0` que multiplica a variável de crescimento da lei log-t:

        δ_log(t)  = (C_creep·F_0) · ln(t/t_0 + 1)         → δ_max ≡ C_creep·F_0
        δ_sat(t)  = (C_creep·F_0) · (1 − e^{−(t/creep_t_c)^α})

    ou seja, δ_max = C_creep · F_0 (SEM fator extra de creep_t_c/t_0). Isto
    é a taxa da lei log-t por unidade de SEU crescimento em log-tempo
    (`d δ_log/d ln(t/t_0+1) = C_creep·F_0`, uma constante — não há "taxa
    inicial" vs "taxa tardia" nesta variável, ao contrário de d/dt) casada
    com a taxa da forma saturante por unidade de SUA função de forma
    (`d δ_sat/dS = δ_max`, S ∈ [0,1]): as duas leis compartilham o MESMO
    coeficiente/orçamento de comprimento; só a CINÉTICA (como esse
    orçamento é gasto no tempo real) muda — log-t gasta devagar e sem
    limite (∝ ln t, total ILIMITADO); saturante gasta com o MESMO
    coeficiente mas total FINITO (δ_max) — não asymptotam ao mesmo valor.
    NB: NÃO escalar δ_max por `creep_t_c/t_0` (ex.: casar a derivada d/dt
    em t=0 literalmente) — para `creep_t_c >> t_0` isso amplifica δ_max
    por até ~creep_t_c/t_0×, o que faz a curva saturante perder MAIS (não
    menos) no intervalo de teste (10³–10⁵× creep_t_c) e viola o próprio
    propósito da forma (comparado numericamente ao construir este
    mecanismo — ver `tests/test_l5_creep_saturating.py`). `F_0` aqui é o
    F_clamp CORRENTE (não F_0_init) — mesma não-linearidade explícita do
    ramo log-t (δ_max encolhe conforme F_0 cai: não é um alvo fixo desde
    o início, é um teto local que também relaxa). `creep_alpha_sat`
    (stretched exponential) só molda a FORMA da transição, não a escala
    (S(creep_t_c) = 1−1/e independe de α). `creep_mode=""` (default) é
    bit-idêntico ao comportamento anterior.
    """
    name = "creep"

    def rate(self, state, geom, mat, F_amp, theta_load, freq, cycle_N,
             slip_amp_override=None, delta_amp=None):
        if freq <= 0 or cycle_N < 1:
            return dict(dF_0=0.0, dE_dissipated=0.0, ds={})
        t_cur = cycle_N / freq
        t_prev = (cycle_N - 1) / freq
        F_clamp = max(state.F_0, 0.0)
        if mat.creep_mode == "saturating" and mat.creep_t_c > 0.0:
            # Forma Alamos (saturante): δ_max = C_creep·F_clamp (MESMO produto
            # do ramo log-t, SEM fator extra de creep_t_c/t_0 -- ver docstring
            # da classe p/ o porque disso e a derivacao completa).
            delta_max = mat.C_creep * F_clamp
            sat_cur = 1.0 - np.exp(-(t_cur / mat.creep_t_c) ** mat.creep_alpha_sat)
            sat_prev = 1.0 - np.exp(-(t_prev / mat.creep_t_c) ** mat.creep_alpha_sat)
            d_delta = delta_max * (sat_cur - sat_prev)
        else:
            # Incremento logarítmico (default) — coincide com a regressao de
            # faiamento do Nah 2014 (KB creep_class); ver docstring da classe.
            d_delta = (mat.C_creep * F_clamp *
                       (np.log((t_cur + mat.t_0)) - np.log((t_prev + mat.t_0))))
        # Estágio B: sem tuner (k_creep_scale foldado em C_creep pelo shim).
        # Pre-conformacao do reservatorio lento (spec 2026-07-08 slow-tail):
        # aperto maior depleta o assentamento log-t residual (S=1 se exp=0).
        d_delta *= creep_conformance_factor(state, geom, mat)
        # PR-3 2026-08-01: mesmo gate de regime do embedding — creep de
        # INTERFACE tambem e' vibracao-dirigido (dref=0 default => 1.0 exato).
        d_delta *= stage1_amp_gate(mat, delta_amp)
        # creep é função do F_clamp atual — não-linearidade explícita
        dF_0 = -geom.k_b * d_delta
        dE = F_clamp * d_delta
        return dict(dF_0=dF_0, dE_dissipated=dE,
                    ds=dict(delta_creep=d_delta))


class WearLoss(LossMechanism):
    """Desgaste Archard nas interfaces bearing (driven por slip transversal)."""
    name = "wear"

    def rate(self, state, geom, mat, F_amp, theta_load, freq, cycle_N,
             slip_amp_override=None, delta_amp=None):
        F_clamp = max(state.F_0, 0.0)
        if F_clamp <= 0:
            return dict(dF_0=0.0, dE_dissipated=0.0, ds={})
        # Resolve slip amp: usa override se dado (displacement-controlled),
        # senao calcula via elasticidade (force-controlled, legado).
        slip_amp = (slip_amp_override
                    if slip_amp_override is not None
                    else resolve_transverse_slip(state, mat, F_amp, theta_load,
                                                 geom=geom))
        if slip_amp <= 0:
            return dict(dF_0=0.0, dE_dissipated=0.0, ds={})
        # Slip distance por ciclo: 4 × amplitude (ida+volta forward + reverse)
        slip_dist = 4.0 * slip_amp
        # Estágio B: sem tuner direcional de wear (k_wear_scale_ax/tr removidos;
        # magnitude foldada em K_archard/k_wear_spec pelo shim). k_scale ≡ 1.
        k_scale = 1.0
        # Archard: d_wear = K · F_n · s / (H · A), modulado por tuner
        # RUNNING-IN (sec4.26 DIRECAO -> forma, sec4.29): K decai de
        # k_wear_running*K para K com constante N_wear_run — wear medido e'
        # sublinear ~N^0.53 (Zhang2019); o V1 tinha K_running_in/K_steady, o
        # V2 usava K unico. k_wear_running<=1 => 1.0 exato (inerte).
        k_run = 1.0
        if mat.k_wear_running > 1.0 and mat.N_wear_run > 0.0:
            k_run = 1.0 + (mat.k_wear_running - 1.0) * np.exp(
                -cycle_N / mat.N_wear_run)
        # MERGE K/H (sec4.42a): k_wear_spec>0 usa a razao identificavel; 0 =>
        # caminho legado com a aritmetica ORIGINAL (bit-identical).
        if mat.k_wear_spec > 0.0:
            d_wear = (k_run * k_scale * mat.k_wear_spec * F_clamp * slip_dist
                      / max(geom.A_contact, 1e-12))
        else:
            d_wear = k_run * k_scale * mat.K_archard * F_clamp * slip_dist / max(mat.hardness * geom.A_contact, 1.0)
        # Surface damage amplifica o material removido (abrasao 3-corpos,
        # debris). Inativo se k_dmg_wear=0. A energia dissipada (dE) segue
        # sendo o trabalho de atrito real (mu_eff·F·slip); a perda extra de
        # preload por remocao de material e contabilizada via U_released
        # (energia elastica liberada pela queda de F_0).
        d_wear *= (1.0 + mat.k_dmg_wear * state.D)
        # Incubação (estágio I): suprime a remoção macro / perda de pré-carga
        # por wear até o slip acumulado cruzar slip_onset_W. O atrito (dE) NÃO
        # é gateado — o micro-slip ainda dissipa calor e alimenta W_slip_acc
        # (mesmo padrão de "dF_0 sim, dE não" da amplificação por dano).
        # g=1 quando slip_onset_W<=0 (backward-compat exato).
        d_wear *= slip_onset_gate(state, mat)
        # D-J: amplificacao por CONTAGEM DE REAPERTOS. Entra aqui, no mesmo
        # ponto do slip_onset (=> mesma convencao "dF_0 sim, dE nao": o
        # micro-slip segue dissipando calor real e alimentando W_slip_acc).
        # Fator 1.0 exato com ganho=0 OU com n_retighten=0.
        d_wear *= retight_loss_factor(state, mat)
        # Conformacao dependente de pressao (spec 2026-07-04 §4/§5): suprime a
        # perda de preload por wear conforme o contato de alta pressao se
        # conforma. Gate dF_0 (NAO dE — mesmo padrao do slip_onset).
        d_wear *= conformation_gate(state, mat)
        # Regime de slip (spec 2026-07-07): partial-slip CM (F0 maior -> menos wear).
        d_wear *= partial_slip_gate(state, geom, mat, F_amp, theta_load, "wear", slip_amp)
        dF_0 = -geom.k_b * d_wear
        # Friction dissipation (atrito × distância), atrito modulado por dano
        dE = k_scale * mu_bearing_eff(state, mat) * F_clamp * slip_dist
        return dict(dF_0=dF_0, dE_dissipated=dE,
                    ds=dict(delta_wear=d_wear))


class ThreadFrettingLoss(LossMechanism):
    """Fretting/wear de flanco de rosca sob carga AXIAL oscilante (spec 2026-07-06).

    Forma faltante da falsificacao axial (MODEL_LEGITIMACY.md 4.6): perda dirigida
    pela amplitude de carga axial A_F, abaixo do onset de loosening. Archard no
    flanco (mesmo par de material que o bearing => reusa K_archard/hardness),
    dirigido pelo micro-slip de flanco s_flank = F_ax/k_b. Irma do WearLoss.
    dF_0 = -k_b*d_fret  =>  dF_0 ~ -F0*A_F (k_b cancela). Inerte em transversal
    (F_ax = F_amp*|cos theta| = 0 em theta=pi/2) e com k_thread_fret=0 (default).

    ADENDO L1 (plano L1-L7 task-3, 2026-07-16): segundo canal INDEPENDENTE no
    mesmo mecanismo (mesma interface fisica: flanco de rosca), gateado por
    `flank_wear_on` (0=OFF, default). Forma complementar ao k_thread_fret
    (hardcoded linear em F_ax): parametriza por PRESSAO de flanco
    p_flank=F_0/A_s (nao forca) com expoente de amplitude AJUSTAVEL
    flank_amp_exp (Liu 2020 sugere 1.5-1.6, super-linear) via
    `flank_wear_axial_term`. So em modo FORCA (delta_amp is None).
    k_wear_flank semeado do KB (Zhang 2019, thread|35CrMo-SCM435) na
    CALIBRACAO (Task 4), nunca aqui. dE deste canal e' o trabalho friccional
    REAL (sem o tuner/expoente de amplitude) — mesmo padrao do WearLoss p/
    conservacao.
    """
    name = "thread_fretting"

    def rate(self, state, geom, mat, F_amp, theta_load, freq, cycle_N,
             slip_amp_override=None, delta_amp=None):
        F_clamp = max(state.F_0, 0.0)
        F_ax = F_amp * abs(np.cos(theta_load))            # componente axial da amplitude
        dF_0 = 0.0
        dE = 0.0
        d_thread_fret = 0.0
        active = False

        # ---- canal legado k_thread_fret (linear em F_ax, spec 2026-07-06) ----
        # F_ax <= 1e-6 N: carga axial desprezivel (inclui o residuo de FP de
        # cos(pi/2)~6e-17 no transversal) => exatamente inerte (bit-identical).
        if mat.k_thread_fret > 0.0 and F_ax > 1e-6 and F_clamp > 0.0:
            active = True
            s_flank = F_ax / max(geom.k_b, 1.0)               # amplitude de desloc. axial
            fret_dist = 4.0 * s_flank                         # ida+volta, como WearLoss
            # MERGE K/H (sec4.42a): mesma razao identificavel do WearLoss.
            if mat.k_wear_spec > 0.0:
                d_fret = (mat.k_thread_fret * mat.k_wear_spec * F_clamp * fret_dist
                          / max(geom.A_s, 1e-12))
            else:
                d_fret = (mat.k_thread_fret * mat.K_archard * F_clamp * fret_dist
                          / max(mat.hardness * geom.A_s, 1.0))
            # DEPENDENCIA DE FREQUENCIA (sec4.39, #9): freq menor => mais dwell/oxidacao
            # por ciclo => mais fretting. Fator (f_ref/f)^exp; exp=0 => 1.0 (bit-identical).
            if mat.fret_freq_exp != 0.0 and freq > 0.0:
                d_fret *= (mat.f_ref_fret / freq) ** mat.fret_freq_exp
            # Regime de slip (spec 2026-07-07): partial-slip CM no flanco (F0 maior -> menos fret).
            d_fret *= partial_slip_gate(state, geom, mat, F_amp, theta_load, "fret", None)
            dF_0 += -geom.k_b * d_fret
            dE += mat.mu_thread * F_clamp * fret_dist         # trabalho de atrito no flanco
            d_thread_fret += d_fret

        # ---- canal L1 (task-3, 2026-07-16): flank_wear_on, pressao + expoente
        # de amplitude ajustavel (forma independente, ver ADENDO na docstring).
        # So modo FORCA (delta_amp is None — disp-mode e' sempre transversal
        # nesta convencao, resolve_transverse_slip ignora theta_load quando
        # delta_amp e' dado). Guard fica aqui (site de uso), NAO dentro de
        # flank_wear_axial_term — mesmo idioma de famp_gross_slip_ceiling: o
        # flag OFF curto-circuita ANTES da funcao ser chamada (registry-truth).
        if (mat.flank_wear_on > 0.0 and F_ax > 1e-6 and F_clamp > 0.0
                and delta_amp is None):
            active = True
            d_w, dE_l1 = flank_wear_axial_term(state, geom, mat, F_amp,
                                               theta_load, freq)
            dF_0 += -geom.k_b * d_w
            dE += dE_l1
            d_thread_fret += d_w

        # ---- rota TRANSVERSAL do canal L1 (F4 L1v2, 2026-07-22): zhang18/
        # zhang19/liu2020 (R5) — desgaste de flanco de rosca sob slip
        # TRANSVERSAL resolvido, SEM rotacao (zero rotacao medida nos 3
        # rigs). Mesma fisica/nucleo do canal axial (flank_wear_from_slip:
        # k_wear_flank, flank_amp_exp, flank_s_crit), com s_th = slip_amp.
        # Guard no site (registry-truth, mesmo idioma do canal axial):
        # exige flank_wear_on E flank_transverse_on E disp-mode E slip
        # transversal resolvido > 0. flank_transverse_on=0.0 (default) =>
        # rota OFF exata (bit-identical).
        if (mat.flank_wear_on > 0.0 and mat.flank_transverse_on > 0.0
                and delta_amp is not None and slip_amp_override is not None
                and slip_amp_override > 1e-12 and F_clamp > 0.0):
            active = True
            d_w, dE_l1 = flank_wear_from_slip(state, geom, mat,
                                              float(slip_amp_override), freq)
            dF_0 += -geom.k_b * d_w
            dE += dE_l1
            d_thread_fret += d_w

        if not active:
            return dict(dF_0=0.0, dE_dissipated=0.0, ds={})
        return dict(dF_0=dF_0, dE_dissipated=dE,
                    ds=dict(delta_thread_fret=d_thread_fret))


def sun_life(sigma_ar: float, mat: JointMaterial) -> float:
    """Vida de fadiga N_f pela Su-N bilinear (Yang): alta tensao N=C1*s^-m1,
    baixa N=C2*s^-m2; infinita abaixo de fat_sigma_endurance. spec 2026-07-08."""
    s = max(sigma_ar, 1.0)
    if s <= mat.fat_sigma_endurance:
        return float("inf")
    if s >= mat.fat_sigma_knee:
        return mat.fat_C1 * s ** (-mat.fat_m1)
    return mat.fat_C2 * s ** (-mat.fat_m2)


class FatigueLoss(LossMechanism):
    """Fadiga de raiz de rosca -> fratura (cliff), spec 2026-07-08.

    Miner's rule sobre Su-N bilinear (Yang) com correcao Goodman de tensao media:
    sigma_a = Kt*|F_amp|/A_s (amplitude), sigma_m = F_0/A_s (media, EVOLUI c/ o
    afrouxamento), sigma_ar = sigma_a/(1-sigma_m/uts). dD=1/N_f acumula em
    D_fatigue; em D>=1 dispara a fratura: F_0 -> fatigue_residual_frac*F_0_init.
    fatigue_enabled=False (default) => zero exato (bit-identical). Energetica do
    cliff fenomenologica (evento estrutural, dE=0; residual so pica no ciclo de
    fratura). |F_amp| direcao-agnostico (rigs de validacao sao axiais)."""
    name = "fatigue"

    def rate(self, state, geom, mat, F_amp, theta_load, freq, cycle_N,
             slip_amp_override=None, delta_amp=None):
        if (not mat.fatigue_enabled or state.F_0 <= 0.0
                or state.D_fatigue >= 1.0):
            return dict(dF_0=0.0, dE_dissipated=0.0, ds={})
        A_s = max(geom.A_s, 1e-9)
        if mat.fat_stress_mode == "bending" and delta_amp is not None:
            # PR-24: tensao de FLEXAO do parafuso sob o deslocamento transverso
            # IMPOSTO delta (~E*d_2*delta/L_eff^2), nao o slip — o parafuso flexiona
            # pelo delta imposto mesmo abaixo do limiar de slip (curvas below-thresh
            # fraturam tb). Escala com delta => reproduz a D-N (N_D~delta^-m);
            # correto p/ ensaio transversal (vs Kt*F_amp/A_s axial).
            L = max(geom.L_eff, 1e-6)
            sigma_a = mat.fat_Kt * geom.E * geom.d_2 * max(delta_amp, 0.0) / (L * L)
        else:
            sigma_a = mat.fat_Kt * abs(F_amp) / A_s
        sigma_m = max(state.F_0, 0.0) / A_s
        denom = max(1.0 - sigma_m / max(mat.fat_sigma_uts, 1.0), 1e-3)   # Goodman
        sigma_ar = sigma_a / denom
        N_f = sun_life(sigma_ar, mat)
        dD = (1.0 / N_f) if np.isfinite(N_f) and N_f > 0.0 else 0.0
        if mat.fat_ramp_D_on < 1.0:
            # Descarga em RAMPA (prereg 2026-07-28-ramp-capability, Opcao A/A1):
            # perda progressiva de secao — A_eff/A_s = 1-((D-D_on)/(1-D_on))^q;
            # F_0 segue a liberacao serie bolt-junta g=(1-a)(1+rho)/((1-a)+rho)
            # (com k_m ~ 5*k_b, meia secao => F/F0 ~ 0,545; A->0 => F_0 -> 0).
            # dE = Delta U_internal por incremento (mesma rota do cliff) =>
            # residual medido 0,017-0,151 J nos 4 casos da sonda A/B. NAO toca
            # geom/k_b: a Opcao B (k_b dinamico) foi falsificada por medicao
            # (forma identica, conservacao quebrada em ate -20,5 J — §4.50).
            D_on, q = mat.fat_ramp_D_on, mat.fat_ramp_q
            D0 = min(max(state.D_fatigue, 0.0), 1.0)
            D1 = min(D0 + dD, 1.0)
            if D1 <= D_on:
                return dict(dF_0=0.0, dE_dissipated=0.0, ds=dict(D_fatigue=dD))
            rho = k_j_ax(state, mat) / max(geom.k_b, 1e-9)

            def _g(D: float) -> float:
                if D <= D_on:
                    return 1.0
                alpha = min(((D - D_on) / (1.0 - D_on)) ** q, 1.0)
                if alpha >= 1.0:
                    return 0.0
                return ((1.0 - alpha) / ((1.0 - alpha) + rho)) * (1.0 + rho)

            g0, g1 = _g(D0), _g(D1)
            dF_0 = min(max(state.F_0, 0.0) * (g1 / max(g0, 1e-12) - 1.0), 0.0)
            dE = 0.0
            if dF_0 < 0.0:
                U_before = U_internal(state, geom, mat)
                U_after = U_internal(
                    replace(state, F_0=max(state.F_0 + dF_0, 0.0)), geom, mat)
                dE = max(U_before - U_after, 0.0)
            return dict(dF_0=dF_0, dE_dissipated=dE, ds=dict(D_fatigue=dD))
        if state.D_fatigue + dD >= 1.0:                    # fratura (cliff)
            F_res = mat.fatigue_residual_frac * max(state.F_0_init, 0.0)
            dF_0 = -(max(state.F_0, 0.0) - F_res)
            # Energetica do cliff (spec 2026-07-08 #6): a energia elastica liberada
            # pela queda subita de F_0 vira trabalho de fratura (dE), roteada p/
            # W_diss_fracture => a conservacao FECHA no ciclo de fratura (antes o
            # residual picava em ~+U liberado com dE=0).
            U_before = U_internal(state, geom, mat)
            U_after = U_internal(replace(state, F_0=F_res), geom, mat)
            dE = max(U_before - U_after, 0.0)
            return dict(dF_0=dF_0, dE_dissipated=dE, ds=dict(D_fatigue=dD))
        return dict(dF_0=0.0, dE_dissipated=0.0, ds=dict(D_fatigue=dD))


class RotationalLooseningLoss(LossMechanism):
    """
    Loosening rotacional via teoria two-factor (contribuição central).

    L_total = Φ_eff(s) · projeções(β) · F_amp
    T_loose = L_total · d_2/2
    slip_fraction = max(0, 1 − T_resist/T_loose)
    Δθ = slip_fraction · (T_loose−T_resist)/k_torsional
    ΔF_0 = −k_b · (p/2π) · Δθ        ← perda via hélice
    """
    name = "rotational_loosening"

    def rate(self, state, geom, mat, F_amp, theta_load, freq, cycle_N,
             slip_amp_override=None, delta_amp=None):
        if state.F_0 <= 0:
            return dict(dF_0=0.0, dE_dissipated=0.0, ds={})

        # ---- RATCHET DE STICK com incubacao (gth, spec 2026-08-10) ---------
        # Antes dos early-returns de torque/gross-slip: sub-slip por definicao
        # nao depende de torque-excess. So disp-mode; so em STICK — em regime
        # de slip os canais macro assumem (0 exato).
        d_theta_gth = 0.0
        ds_gth = {}
        if (mat.gth_k > 0.0 and delta_amp is not None and float(delta_amp) > 0.0
                and (slip_amp_override is None
                     or float(slip_amp_override) <= 1e-9)):
            _rq = (float(delta_amp) / max(mat.gth_dref, 1e-12)) ** mat.gth_q
            ds_gth["A_gth"] = _rq
            if state.A_gth + _rq >= mat.gth_A0:
                # SEM self_locking_gate, de proposito (medido 2026-08-10: com
                # ele o termo era estrangulado a ~0 em F0 alto — 10x em gth_k
                # movia o MAE em 0,0006). A fisica do mecanismo e' micro-slip
                # de flanco operando APESAR do auto-travamento macro; a
                # protecao contra disparo precoce e' a INCUBACAO (gth_A0), nao
                # o arresto — que segue valendo para o kernel macro.
                d_theta_gth = mat.gth_k * _rq
                # ACELERACAO PROGRESSIVA (2026-08-20, opt-in): pos-onset a
                # taxa cresce com o acumulado — p=0 = OFF exato (bit-ident.).
                if mat.gth_accel_p > 0.0:
                    _exc = max(state.A_gth + _rq - mat.gth_A0, 0.0)
                    d_theta_gth *= (_exc / max(mat.gth_A0, 1.0)) ** mat.gth_accel_p

        def _gth_only():
            if d_theta_gth <= 0.0 and not ds_gth:
                return dict(dF_0=0.0, dE_dissipated=0.0, ds={},
                            _slip_fraction=0.0)
            T_res = T_resistance(state, geom, mat)
            ds = dict(ds_gth)
            if d_theta_gth > 0.0:
                ds["theta_loose"] = d_theta_gth
            # `_dE_gth_ext`: o atrito de micro-slip em STICK e' suprido pelo
            # trabalho externo da vibracao (nao ha slip macro que ja o traga
            # via W_ext_per_cycle). O step_cycle faz W_ext += este valor —
            # mesmo idioma do thread_fretting ("fecha o canal nos dois
            # lados"). Sem isso o residual abria exatamente pelo dE (medido:
            # 0,894 J para 4,2 kN drenados).
            # dE = atrito de filete (T_res·dθ, suprido por W_ext) + o ΔU
            # ELASTICO liberado pela queda de F_0 (F_0·lead·dθ), que em stick
            # tambem dissipa no filete — sem a 2a parcela o residual abria em
            # exatamente ΔU (medido: 0,135 J p/ 4,2 kN drenados).
            # F_0 de PONTO MEDIO (o ΔU e' quadratico; com o F_0 do inicio o
            # residual sobrava ΔF²/2k_b — medido 0,013 J em 4,2 kN)
            _dF = geom.k_b * geom.lead_per_radian * d_theta_gth
            dE_gth = (T_res + (state.F_0 - 0.5 * _dF)
                      * geom.lead_per_radian) * d_theta_gth
            return dict(dF_0=-geom.k_b * geom.lead_per_radian * d_theta_gth,
                        dE_dissipated=dE_gth, ds=ds,
                        _dE_gth_ext=T_res * d_theta_gth,
                        _slip_fraction=0.0)

        # ---- TAXA GRADUADA amplitude-sensivel (sec4.37, opt-in) ----------------
        # Substitui o kernel de torque-runaway por uma taxa CINEMATICA no excesso
        # de slip sobre s_crit FIXO. Amplitude-sensivel, sem runaway, sub-critico
        # => zero. Default loose_rate_mode="torque" => este branch NUNCA roda.
        if (mat.loose_rate_mode == "graded_scrit"
                and slip_amp_override is not None
                and mat.k_loose_graded > 0.0):
            excess = max(0.0, float(slip_amp_override) - mat.s_crit_loose)
            if excess <= 0.0:                              # sub-critico: nao inicia
                return _gth_only()
            g = slip_onset_gate(state, mat)                # incubacao (plato)
            arrest = self_locking_gate(state, mat, geom)         # arresto (piso)
            conf = conformation_gate(state, mat)           # conformacao alta-pressao
            k_scale = 1.0        # Estágio B: sem tuner direcional de loosening
            g_trig = 1.0
            if mat.crash_trigger_frac > 0.0 and state.F_0_init > 0.0:
                r0 = max(state.F_0, 0.0) / state.F_0_init
                kk = mat.crash_trigger_sharpness
                ftt = mat.crash_trigger_frac ** kk
                g_trig = ftt / (ftt + r0 ** kk)
            gate = (g * arrest * conf * g_trig * k_scale
                    * retight_loss_factor(state, mat))   # D-J
            # PR-21 no graded (2026-08-19): a docstring de loose_amp_exp ja
            # prometia "aplicado tambem ao termo graded_scrit" mas so o ramo
            # k_ratchet o lia — medido inerte aqui (theta identico em exp=0.0
            # vs 1.0). Mesma formula do sitio k_ratchet, sobre o EXCESS.
            # exp=1 => fator 1.0 exato (bit-identical); exp=0 => taxa
            # CONSTANTE por ciclo (quantum de avanco, Rousseau theta(N)
            # pos-onset linear r2=0.983).
            eff = excess
            if mat.loose_amp_exp != 1.0 and excess > 0.0:
                eff = excess * (excess / LOOSE_AMP_REF) ** (mat.loose_amp_exp - 1.0)
            d_theta = gate * mat.k_loose_graded * eff / max(geom.d_2 / 2.0, 1e-9)
            # TAXA FRACIONARIA (P-13, 2026-08-20, opt-in): d_theta ~ (F/F0)^fe
            # — fe=1 da decay exponencial (dF/dN ~ F), o meio-termo entre os
            # dois atratores (runaway x arresto). fe=0 = OFF exato.
            if mat.loose_F_exp > 0.0 and state.F_0_init > 0.0:
                d_theta *= (max(state.F_0, 0.0) / state.F_0_init) ** mat.loose_F_exp
            # RUNAWAY DE PORCA SOLTA (2026-08-20, zhang2006_fig3 sec9): boost
            # Hill abaixo da fracao critica r_c — o auto-travamento residual
            # deixa de segurar e a taxa dispara. Acima de r_c o boost e' suave
            # ~(r_c/r)^k; frac=0 OU gain=0 = OFF exato (nem computa).
            if (mat.loose_runaway_frac > 0.0 and mat.loose_runaway_gain > 0.0
                    and state.F_0_init > 0.0):
                _r = max(state.F_0, 0.0) / state.F_0_init
                _kk = mat.loose_runaway_sharpness
                _fck = mat.loose_runaway_frac ** _kk
                d_theta *= 1.0 + mat.loose_runaway_gain * (_fck / (_fck + _r ** _kk))
            # BURST DE RUPTURA (2026-08-21, fig14 do LU): liberacao da energia
            # incubada quando o gate de onset abre — dreno exponencial em
            # direcao ao alvo (1-frac)*F0_init, gateado pelo MESMO Hill `g` da
            # incubacao (ja computado acima). Desacelera sozinho ao chegar.
            # frac=0 OU rate=0 = OFF exato; sem incubacao (g=1 desde N=1) o
            # prereg da adocao exige slip_onset_W > 0.
            if (mat.onset_burst_frac > 0.0 and mat.onset_burst_rate > 0.0
                    and state.F_0_init > 0.0):
                _alvo = (1.0 - mat.onset_burst_frac) * state.F_0_init
                _lac = max(0.0, state.F_0 - _alvo)
                if _lac > 0.0:
                    # GATE PROPRIO (2026-08-21): onset_burst_W>0 troca o `g`
                    # compartilhado por um Hill proprio sobre o MESMO
                    # W_slip_acc — desacopla o limiar de ADESAO (burst) do
                    # limiar de ABRASAO (wear). 0.0 = usa `g` = bit-identico.
                    _gb = g
                    if mat.onset_burst_W > 0.0:
                        _kk = mat.slip_onset_sharpness
                        _wk = max(state.W_slip_acc, 0.0) ** _kk
                        _bk = mat.onset_burst_W ** _kk
                        _gb = _wk / (_wk + _bk) if (_wk + _bk) > 0.0 else 0.0
                    _dfb = _gb * mat.onset_burst_rate * _lac
                    d_theta += _dfb / max(geom.k_b * geom.lead_per_radian, 1e-9)
            T_resist = T_resistance(state, geom, mat)
            # FREE-SPIN CINEMATICO (sec4.56, opt-in): fracao free_spin_kin da
            # rotacao relativa NAO drena — a rigidez de dreno real do laco e'
            # menor que k_b (Rousseau Fig.5: 920 N/deg medido vs 3278 do
            # k_b*lead, r2=0.9997). theta_loose e dE ficam com a rotacao TOTAL
            # (dE suprido por W_ext, padrao do free_spin pos-arresto).
            # fsk=0 => bit-identico.
            fsk = min(max(mat.free_spin_kin, 0.0), 0.999)
            dF_0 = -geom.k_b * geom.lead_per_radian * d_theta * (1.0 - fsk)
            dE = T_resist * d_theta                             # dissipacao no filete
            return dict(dF_0=dF_0, dE_dissipated=dE,
                        ds=dict(theta_loose=d_theta), _slip_fraction=1.0)
        # ------------------------------------------------------------------------

        # Φ direcional com correções pós-calibração
        Phi_ax = Phi_eff(state, geom, mat, direction='axial')
        Phi_tr_base = Phi_eff(state, geom, mat, direction='transverse')

        F_ax = F_amp * np.cos(theta_load)
        F_tr = F_amp * np.sin(theta_load)
        # Acoplamento F_amp<->delta_amp (#4, spec §8): em gross slip a forca
        # transversal de loosening satura no Coulomb mu*F0. Opt-in, so em regime CM.
        if mat.couple_famp_slip and mat.slip_regime_mode == "cattaneo_mindlin":
            F_tr = min(F_tr, mu_bearing_eff(state, mat) * max(state.F_0, 0.0))

        # Fator 1 ativo (axial): salto pra 1 acima de F_sep
        F_sep = F_sep_axial(state, geom, mat)
        Phi_ax_active = Phi_ax if F_ax < F_sep else 1.0

        # Fator 1 ativo (transversal): salto stick→slip threshold
        # tr_loose_gain (default 5.0) reflete amplificacao dinamica em ensaio
        # tipo Junker — antes era hardcoded 0.95, mas calibracao mostrou que
        # o valor real eh ~5x maior. Phi_tr_correction permanece como tuner
        # fino multiplicativo (default 1.0 = baseline calibrada).
        # tr_loose_gain reflete amplificacao dinamica (Junker). Estágio B: a
        # antiga Phi_tr_correction (tuner) foi FOLDADA em tr_loose_gain (produto
        # exato) pelo shim — o engine le so a constante.
        F_slip = F_slip_transverse(state, mat)
        Phi_tr_active = 0.01 if F_tr < F_slip else mat.tr_loose_gain

        # Two-factor synthesis (Fator 2 = projeção sin/cos β)
        L_ax = Phi_ax_active * np.sin(geom.beta) * F_ax
        L_tr = Phi_tr_active * np.cos(geom.beta) * F_tr
        L_total = np.hypot(L_ax, L_tr)

        # Torque versus resistência
        T_loose = L_total * geom.d_2 / 2.0
        T_resist = T_resistance(state, geom, mat)

        if T_loose <= T_resist:
            return _gth_only()

        k_scale = 1.0        # Estágio B: sem tuner direcional de loosening
        slip_fraction = (T_loose - T_resist) / T_loose
        # Incubação (estágio I): suprime o backing-off até o slip acumulado
        # cruzar slip_onset_W. g=1 quando slip_onset_W<=0 (backward-compat).
        g = slip_onset_gate(state, mat)
        # Δθ per cycle — aproximação: motion proporcional ao excesso de torque.
        # k_torsional: "legacy" (default, k_j_init*d_2/2 ~2e7, backward-compat
        # bit-identical) | "bolt_torsion" (rigidez torsional FISICA do shank
        # eta_loose*G*J/L_eff, J=pi*d_2^4/32 ~4e3 => ~5000x menor, deixa o runaway
        # T_resist~F_0 (que ja existe) disparar; grip-dependencia vem do gate de
        # onset gross_fraction + k_tr bending). Spec 2026-07-07 (#10 / §4.8).
        if mat.loose_torsion_mode == "bolt_torsion":
            J = np.pi * geom.d_2 ** 4 / 32.0
            k_torsional = max(mat.eta_loose * G_STEEL * J / max(geom.L_eff, 1e-6), 1.0)
        else:
            k_torsional = mat.k_j_init * geom.d_2 / 2.0
        # g = incubacao (slip_onset); conformation_gate = arresto por
        # conformacao de alta pressao (spec 2026-07-04); g_slip_regime = fracao de
        # gross-slip (spec 2026-07-06, loosening precisa de gross slip). Os tres
        # gateiam d_theta, logo dF_0 E o dE derivado (=T_resist*d_theta).
        g_slip_regime = loosening_slip_gate(state, geom, mat, slip_amp_override)
        # self_locking_gate: arresto por nucleo auto-travado (spec 2026-07-07) — o
        # 4o gate, fecha o runaway em F_min = loose_arrest_floor·F_0_init.
        # FREE-SPIN (sec4.23): o arresto e' separado dos demais gates — ele trava
        # o DRENO de preload, nao necessariamente a rotacao da porca (dado theta
        # Rousseau: steel_t10 mede 3.3x mais theta do que a perda explica).
        arrest = self_locking_gate(state, mat, geom)
        # GATILHO DE CRITICALIDADE (sec4.30/L14): plato enquanto F_0 alto, runaway
        # quando F_0/F_0_init cruza crash_trigger_frac (o joelho lido do dado).
        g_trigger = 1.0
        if mat.crash_trigger_frac > 0.0 and state.F_0_init > 0.0:
            ratio = max(state.F_0, 0.0) / state.F_0_init
            k = mat.crash_trigger_sharpness
            ft = mat.crash_trigger_frac ** k
            g_trigger = ft / (ft + ratio ** k)
        gates_free = (g * conformation_gate(state, mat) * g_slip_regime
                      * g_trigger * k_scale
                      * retight_loss_factor(state, mat))   # D-J
        gates = gates_free * arrest
        d_theta = (gates * slip_fraction * (T_loose - T_resist)
                   / max(k_torsional, 1.0))
        # BLEND CONTINUO (sec4.35): limita d_theta em SERIE pela disponibilidade
        # cinematica de slip. Media harmonica d_eff = d*d_kin/(d+d_kin): quando o
        # torque-excess dispara (runaway, F_0->0), d_kin satura => transicao
        # gradual (fixa o mid-over-loss). loose_kin_ceiling=0 => sem teto
        # (bit-identical). Aplicado ao drive de torque ANTES do termo aditivo
        # k_ratchet (que e cinematico por si).
        if mat.loose_kin_ceiling > 0.0 and slip_amp_override is not None:
            d_kin = (gates * mat.loose_kin_ceiling * 4.0
                     * max(slip_amp_override, 0.0)
                     / max(geom.d_2 / 2.0, 1e-9))
            denom = d_theta + d_kin
            if denom > 1e-30:
                d_theta = d_theta * d_kin / denom
        # Ratcheting CINEMATICO (spec 2026-07-08): rotacao por ciclo prop. a
        # DISTANCIA de gross-slip (4*slip, como WearLoss), convertida em rad no
        # raio de passo. Opt-in k_ratchet>0; so disp-mode (slip do curso); mesmo
        # produto de gates (dF_0 e dE juntos => conservacao preservada). Fixa a
        # cegueira de amplitude do drive (modo collapse-missed, 28/46 curvas).
        if mat.k_ratchet > 0.0 and slip_amp_override is not None:
            _s = max(slip_amp_override, 0.0)
            kin = (gates * mat.k_ratchet * 4.0 * _s / max(geom.d_2 / 2.0, 1e-9))
            # PR-21: expoente de amplitude (d_theta ~ slip^exp). exp=1 => 1.0
            # exato (bit-identical); exp>1 => resposta ingreme (D-N ~delta^-m).
            if mat.loose_amp_exp != 1.0 and _s > 0.0:
                kin *= (_s / LOOSE_AMP_REF) ** (mat.loose_amp_exp - 1.0)
            # Forma-PRODUTO (spec 2026-07-08, apontada pelas DUAS falhas de gate):
            # x slip_fraction (excesso de torque adimensional). Cresce conforme
            # F_0 cai => colapso gradual ACELERANTE (shape do Liu2025, dado
            # back-loaded que falsificou os carriers exponencial E linear); e
            # como slip_fraction depende so de F_0/F_0_init, a dinamica
            # fracional e' invariante de escala de pre-carga => N_falha ~flat
            # vs torque (gate de flatness do Lu, falhado pelo ratchet puro
            # N∝F0). Opt-in ratchet_torque_coupled=False (bit-identical).
            if mat.ratchet_torque_coupled:
                kin *= slip_fraction
            d_theta += kin
        # FREE-SPIN pos-arresto (sec4.23, opt-in): fracao do drive NAO-arrestado
        # que continua como rotacao livre — dF_0 NAO recebe (preload das curvas
        # adotadas fica BIT-IDENTICO); so theta_loose e dE (atrito residual real,
        # suprido por W_ext). free_spin=0 => 0.0 exato (backward-compat).
        d_theta_free = 0.0
        if mat.free_spin > 0.0 and arrest < 1.0 and k_torsional > 1.0:
            drive_free = (gates_free * slip_fraction * (T_loose - T_resist)
                          / max(k_torsional, 1.0))
            if mat.k_ratchet > 0.0 and slip_amp_override is not None:
                kin_f = (gates_free * mat.k_ratchet * 4.0
                         * max(slip_amp_override, 0.0) / max(geom.d_2 / 2.0, 1e-9))
                if mat.ratchet_torque_coupled:
                    kin_f *= slip_fraction
                drive_free += kin_f
            d_theta_free = mat.free_spin * max(drive_free - d_theta, 0.0)
        # Perda de F_0 via hélice (SO a parte arrestada — free-spin nao drena)
        dF_0 = -geom.k_b * geom.lead_per_radian * d_theta
        # Energia dissipada no filete: T_resist · Δθ (total, incl. free-spin)
        dE = T_resist * (d_theta + d_theta_free + d_theta_gth)
        ds_out = dict(theta_loose=d_theta + d_theta_free + d_theta_gth)
        ds_out.update(ds_gth)
        return dict(dF_0=dF_0 - geom.k_b * geom.lead_per_radian * d_theta_gth,
                    dE_dissipated=dE, ds=ds_out,
                    _slip_fraction=slip_fraction)


# ============================================================================
# Analisador principal
# ============================================================================

class DynamicStiffnessAnalyzer:
    """
    Analisador não-linear de junta com [K(s)] dinâmica e contabilidade
    completa de energia. Implementação direta de §12 do spec teórico.

    Uso:
        ana = DynamicStiffnessAnalyzer(geom, mat, F0_initial)
        for n in range(N):
            snap = ana.step_cycle(F_amp, theta_load, freq)
        # ana.history tem CycleSnapshot por ciclo
        # ana.energy tem o balanço cumulativo
        # ana.state.F_0 tem a pré-carga residual

    Verificação de energia:
        residual = ana.energy.conservation_residual
        # ≈ 0 se modelo é internamente consistente
    """

    def __init__(self,
                 geometry: JointGeometry,
                 material: JointMaterial,
                 initial_preload: float,
                 loss_mechanisms: Optional[List[LossMechanism]] = None,
                 initial_damage: float = 0.0,
                 initial_embedding_frac: float = 0.0):
        if not 0.0 <= initial_embedding_frac <= 1.0:
            raise ValueError(
                f"initial_embedding_frac deve estar em [0, 1] "
                f"(recebido {initial_embedding_frac})")
        if not 0.0 <= initial_damage <= 1.0:
            raise ValueError(
                f"initial_damage deve estar em [0, 1] "
                f"(recebido {initial_damage})")
        self.geom = geometry
        self.mat = material
        # L2 (plano L1-L7 task-5, 2026-07-17): substitui k_j_init 1x por
        # kj_from_geometry(...) SE kj_mode ativo E a geometria fornecer
        # furo/arruela (>0); senão cai SILENCIOSAMENTE no k_j_init atual
        # (fallback documentado/testado, tests/test_l2_kj_law.py). Copia
        # LOCAL de `material` (dataclasses.replace) — nunca muta o objeto do
        # chamador; no caminho default (kj_mode=="") `self.mat` permanece o
        # MESMO objeto que `material` (alias, sem cópia) — bit-identidade
        # total, zero overhead. Precisa acontecer ANTES de U_init/
        # embedding_conformance_factor (ambos leem self.mat.k_j_init via
        # k_j_ax), por isso o resto do __init__ abaixo usa self.mat, não
        # material.
        # Fix wave (task-5 review, 2026-07-17, gate-corruption risk): o
        # fallback acima e' silencioso por design, mas isso deixa um
        # consumidor (ex.: gate D5 Task 6) sem forma de saber se a lei
        # REALMENTE engatou ou se caiu no fallback -- `kj_mode_engaged` e' o
        # sinal positivo de engate (True SOMENTE se o replace() abaixo
        # rodar); o fallback em si continua silencioso (sem warning/
        # exception). Ver tests/test_l2_kj_law.py.
        self.kj_mode_engaged: bool = False
        if (self.mat.kj_mode in ("pedersen", "wileman")
                and geometry.d_hole > 0.0 and geometry.d_washer > 0.0):
            from bolt_analysis_studio.calibration.library_common import (
                kj_from_geometry)
            kj_new = kj_from_geometry(
                geometry.d_nominal * 1e3, geometry.L_eff * 1e3, geometry.E,
                geometry.d_hole * 1e3, geometry.d_washer * 1e3,
                mode=self.mat.kj_mode)
            self.mat = replace(material, k_j_init=kj_new)
            self.kj_mode_engaged = True
        self.state = SlowState(F_0=initial_preload,
                               F_0_init=initial_preload,
                               D=initial_damage)
        # seed de embedding ja consumido (reuso), com o mesmo fator de conformacao
        # de aperto (spec 2026-07-08); inerte se initial_embedding_frac=0 ou exp=0.
        self.state.delta_emb = (initial_embedding_frac * self.mat.emb_depth
                                * embedding_conformance_factor(self.state, geometry, self.mat))
        U_init = U_internal(self.state, geometry, self.mat)
        self.energy = EnergyBudget(U_stored=U_init, U_stored_init=U_init)
        self.losses = loss_mechanisms or [
            EmbeddingLoss(),
            CreepLoss(),
            WearLoss(),
            RotationalLooseningLoss(),
            ThreadFrettingLoss(),
            FatigueLoss(),
        ]
        self.history: List[CycleSnapshot] = []
        self._cycle_counter = 0

    # ----- interface matricial (para BAS integration) ----- #

    def M(self) -> np.ndarray:
        return M_matrix(self.mat)

    def K(self, slip_y: bool = False, slip_theta: bool = False) -> np.ndarray:
        return K_matrix(self.state, self.geom, self.mat, slip_y, slip_theta)

    def C(self) -> np.ndarray:
        return C_matrix(self.state, self.geom, self.mat)

    # ----- energias atuais ----- #

    def Phi_eff(self) -> float:
        return Phi_eff(self.state, self.geom, self.mat)

    def U_internal(self) -> float:
        return U_internal(self.state, self.geom, self.mat)

    def U_loaded(self, F_ax_ext: float) -> float:
        return U_loaded(self.state, self.geom, self.mat, F_ax_ext)

    # ----- evolução ----- #

    # Ablation study ONLY (2026-08-28; set by validation/runner._aplica_ablacao,
    # never by a config): when True the loss RATES and the slip resolution see
    # F_0 frozen at F_0_init while the preload itself keeps integrating — the
    # open-loop counterpart of the F_0 feedback that the closed loop below
    # carries (F_0 -> friction capacity mu*F_0 -> slip -> wear/loosening -> F_0).
    # Default False = closed loop, bit-identical: the SAME state object is
    # passed through, no copy is made.
    open_loop_rates: bool = False

    def _rates_state(self):
        if not self.open_loop_rates:
            return self.state
        return replace(self.state, F_0=self.state.F_0_init)

    def step_cycle(self, F_amp: float, theta_load: float,
                   freq: float = 1.0,
                   delta_amp: Optional[float] = None) -> CycleSnapshot:
        """
        Avança um ciclo de carregamento, atualiza estado e energia.

        Args:
            F_amp: Amplitude de forca [N] — drive do loosening rotacional
                (T_loose escala com F_amp). Em modo displacement-controlled
                (delta_amp dado), F_amp ainda controla T_loose mas slip
                vem do delta_amp.
            theta_load: Angulo de carregamento [rad] (0=ax, pi/2=tr).
            freq: Frequencia [Hz].
            delta_amp: (opcional) Deslocamento transverso imposto [m] pela
                amplitude da onda. Em teste Junker (deslocamento-controlado),
                use este modo: slip_amp = max(0, delta - F_slip/k_tr).
                Quando None, slip vem da elasticidade local (force-only).

        Em modo displacement, ambos F_amp e delta_amp tem papel:
            - delta_amp → wear, friction work (W_ext, W_diss_friction_y)
            - F_amp     → drive do loosening rotacional

        L3 (roadmap #4, opt-in via mat.famp_couple_on): fisicamente F_amp
        nao pode superar o teto de Coulomb mu_eff(F0)*F0 em disp-mode —
        acima disso a junta ja esta em gross slip pleno. Default
        (famp_couple_on=0.0) mantem F_amp e delta_amp independentes
        (backward-compat exato).
        """
        self._cycle_counter += 1
        n = self._cycle_counter
        self.state.n_cycle = n        # indice do mu_bearing_schedule (F3)

        # ===== -1) Acoplamento F_amp<=mu_eff(F0)*F0 em disp-mode (L3,
        # roadmap #4, 2026-07-16). Guard curto-circuita ANTES de qualquer
        # computo quando famp_couple_on==0.0 (default) ou em force-mode —
        # nada e chamado, nada muda (bit-identical).
        if delta_amp is not None and self.mat.famp_couple_on > 0.0:
            F_amp = min(F_amp, famp_gross_slip_ceiling(self.state, self.mat))

        # ===== 0) Resolve slip amp se delta_amp foi dado (modo displacement)
        st_rates = self._rates_state()   # == self.state unless open-loop ablation
        slip_amp_override = (resolve_transverse_slip(
                                 st_rates, self.mat,
                                 F_amp, theta_load, delta_amp, geom=self.geom)
                             if delta_amp is not None else None)
        # HISTERESE DE STICK (2026-08-20, opt-in): a 1a abertura do slip e' a
        # RUPTURA do travamento — o latch faz o mu de bearing cair ao cinetico
        # (mu_kinetic_frac) dali em diante. So com mu_kinetic_frac<1 (default
        # 1.0 = nada e' escrito, bit-identical).
        if (self.mat.mu_kinetic_frac < 1.0 and self.state.stick_broken == 0.0
                and slip_amp_override is not None
                and float(slip_amp_override) > 1e-9):
            self.state.stick_broken = 1.0

        # ===== 1) Trabalho externo absorvido neste ciclo
        W_ext_c = W_ext_per_cycle(self.state, self.geom, self.mat,
                                   F_amp, theta_load, delta_amp)
        self.energy.W_ext += W_ext_c

        # ===== 2) Energia amortecida (viscoso linear)
        W_visc_c = W_viscous_per_cycle(self.state, self.geom, self.mat,
                                        F_amp, theta_load, freq)
        self.energy.W_damp_visc += W_visc_c
        # Fonte externa do viscoso (spec 2026-07-07, bookkeeping axial): a carga
        # ciclica externa realiza este trabalho contra o amortecedor (loop
        # eliptico), = W_visc por ciclo. Em modo axial (force-mode) W_ext_per_cycle
        # da' ~0 (sem slip transverso) e o viscoso ficava orfao => residual −W_visc.
        # Em transversal (theta=pi/2) W_visc ~ cos^2(pi/2) ~ 0 => nao afeta disp-mode.
        self.energy.W_ext += W_visc_c

        # ===== 2b) Dissipacao VISCOELASTICA do membro (sec4.25, forma nomeada
        # pelos loops medidos: HDPE dissipa 7-8x o que a interface contabiliza).
        # Loop harmonico de perda: W_m = pi*eta*F_tr_eff^2/k_member por ciclo
        # (eta = fator de perda por-material; polimero lossy). SO energia —
        # nao toca F_0 (preload bit-identico); suprida por W_ext (conservacao,
        # mesmo padrao do viscoso). member_loss_eta=0 => OFF exato.
        if (self.mat.member_loss_eta > 0.0 and self.mat.k_member_shear > 0.0
                and delta_amp is not None):
            F_tr_eff = min(abs(F_amp * np.sin(theta_load)),
                           mu_bearing_eff(self.state, self.mat)
                           * max(self.state.F_0, 0.0))
            W_m = (np.pi * self.mat.member_loss_eta
                   * F_tr_eff ** 2 / self.mat.k_member_shear)
            self.energy.W_damp_visc += W_m
            self.energy.W_ext += W_m

        # ===== 3) Roda cada mecanismo de perda
        per_mech: Dict[str, float] = {}
        dF_0_by_mech: Dict[str, float] = {}
        slip_fraction_cycle = 0.0
        dF_0_total = 0.0
        dE_diss_total = W_visc_c   # damping viscoso já entra na conta

        _F_corrente = self.state.F_0   # dE exato de liberacao (2026-08-31): os
        # mecanismos de PURA LIBERACAO (embedding, creep) contabilizam como
        # dissipacao a liberacao EXATA de energia interna que o seu dF_0
        # produz, avaliada sequencialmente num F local — em vez do 1o ordem
        # F0*d_delta, que deixava de fora a parcela da mola do joint e os
        # termos de 2a ordem e abria residual relativo grande nos orcamentos
        # sub-joule (cauda medida no §5.3 do artigo). dF_0 e trajetoria NAO
        # mudam (dE nao realimenta o estado); wear/loosening/fadiga mantem a
        # convencao propria (trabalho de atrito real / rota de fratura).
        for mech in self.losses:
            res = mech.rate(st_rates, self.geom, self.mat,
                            F_amp, theta_load, freq, n,
                            slip_amp_override=slip_amp_override,
                            delta_amp=delta_amp)
            dF_0_total += res["dF_0"]
            dF_0_by_mech[mech.name] = res["dF_0"]
            dE = res["dE_dissipated"]
            if mech.name in ("embedding", "creep") and res["dF_0"] < 0.0:
                _st_a = replace(self.state, F_0=_F_corrente)
                _st_b = replace(self.state, F_0=max(_F_corrente + res["dF_0"], 0.0))
                dE = U_internal(_st_a, self.geom, self.mat) - U_internal(_st_b, self.geom, self.mat)
            _F_corrente = max(_F_corrente + res["dF_0"], 0.0)
            # gth (stick): dE suprido por W_ext — ver `_dE_gth_ext` no
            # RotationalLooseningLoss (idioma do thread_fretting)
            self.energy.W_ext += res.get("_dE_gth_ext", 0.0)
            dE_diss_total += dE
            per_mech[mech.name] = dE
            # Atualiza demais campos de ds
            for fld, inc in res["ds"].items():
                setattr(self.state, fld, getattr(self.state, fld) + inc)
            # Acumula no bucket específico do EnergyBudget
            if mech.name == "embedding":
                self.energy.W_diss_emb += dE
            elif mech.name == "creep":
                self.energy.W_diss_creep += dE
            elif mech.name == "wear":
                # Wear includes both material removal + friction work
                # We count it as friction (heat-equivalent), not double
                self.energy.W_diss_friction_y += dE
                # L7 (Task 8): bookkeeping de volume removido — mesmo dE
                # (bearing wear, ja acumulado acima), area = geom.A_contact
                # (interface bearing). Aditivo puro, nao le nem altera dF_0.
                self.energy.V_wear_removed += (res["ds"].get("delta_wear", 0.0)
                                               * self.geom.A_contact)
                self.energy.E_wear_removal += dE
            elif mech.name == "rotational_loosening":
                self.energy.W_diss_loose += dE
                slip_fraction_cycle = res.get("_slip_fraction", 0.0)
            elif mech.name == "thread_fretting":
                # Fretting de flanco axial: atrito real de flanco, contado no
                # bucket Archard (W_diss_wear, antes ocioso). E sourced pelo
                # trabalho externo da carga axial ciclica — W_ext += dE, analogo
                # ao W_ext_per_cycle transversal — mantendo o residual balanceado
                # (nao piora a conservacao; fecha o canal nos dois lados).
                self.energy.W_diss_wear += dE
                self.energy.W_ext += dE
                # L7 (Task 8): volume removido no flanco — area = geom.A_s
                # (interface de rosca, mesma convencao de flank_wear_axial_term
                # /d_fret legado). Soma delta_thread_fret (ambos os
                # sub-canais, legado k_thread_fret + L1 flank_wear_on, ja
                # combinados em res["ds"] pelo proprio mecanismo).
                self.energy.V_wear_removed += (res["ds"].get("delta_thread_fret", 0.0)
                                               * self.geom.A_s)
                self.energy.E_wear_removal += dE
            elif mech.name == "fatigue":
                # Fratura (cliff): energia elastica liberada roteada p/ W_diss_fracture
                # (fecha a conservacao no ciclo de fratura, spec 2026-07-08 #6).
                self.energy.W_diss_fracture += dE

        # ===== 3.5) AMPLIFICADOR TARDIO AGNOSTICO DE CANAL (PR-3 2026-08-01)
        # dF_0_total *= (1 + k_dmg_all*D). Aplicado AQUI, depois de todos os
        # mecanismos e ANTES de tocar F_0, exatamente para nao precisar saber
        # QUAL canal domina — o fator multiplica o que quer que eles tenham
        # produzido. `dF_0_by_mech` e' reescalado junto para a decomposicao
        # continuar somando o total (o report checa essa soma).
        # dE NAO e' tocado: a energia dissipada segue sendo o trabalho real e
        # a perda extra de preload fecha por U_released (mesmo padrao do
        # k_dmg_wear; amplificar dE quebraria a conservacao).
        # k_dmg_all=0 (default) => fator 1.0 exato, bit-identical.
        amp = 1.0
        if self.mat.k_dmg_all > 0.0 and self.state.D > 0.0:
            amp *= 1.0 + self.mat.k_dmg_all * self.state.D
        # Emenda: amplificacao TARDIA pelo interruptor (mesmo g do
        # crash_trigger — ~0 enquanto F_0 esta alto, ~1 depois do limiar).
        if (self.mat.k_late_amp > 0.0 and self.mat.crash_trigger_frac > 0.0
                and self.state.F_0_init > 0.0):
            _r = max(self.state.F_0, 0.0) / self.state.F_0_init
            _k = self.mat.crash_trigger_sharpness
            _ft = self.mat.crash_trigger_frac ** _k
            amp *= 1.0 + self.mat.k_late_amp * (_ft / (_ft + _r ** _k))
        if amp != 1.0:
            dF_0_total *= amp
            for _m in dF_0_by_mech:
                dF_0_by_mech[_m] *= amp

        # ===== 4) Atualiza F_0 e U_stored
        prev_U = self.energy.U_stored
        self.state.F_0 = max(0.0, self.state.F_0 + dF_0_total)
        new_U = U_internal(self.state, self.geom, self.mat)
        self.energy.U_stored = new_U
        delta_U = new_U - prev_U

        # ===== 4.5) Atualiza surface_damage D
        # Driver: trabalho de slip deste ciclo (wear + loosening), nao
        # embedding/creep/viscoso. Mecanismos ja usaram o D de inicio de
        # ciclo (sem dependencia de ordem). Inativo se c_D=0.
        W_slip_cycle = (per_mech.get("wear", 0.0)
                        + per_mech.get("rotational_loosening", 0.0))
        # dE_partial (spec 2026-07-08; dupla falsificacao §4.25 loops Rousseau +
        # §4.31 joelho Bauer): energia do anel de micro-slip Cattaneo-Mindlin,
        # presente MESMO sem gross slip (o plato). dE = k_partial_slip·g_partial·
        # 4·mu·F0·delta_t (delta_t = amplitude de micro-slip = F_slip/k_tr). Entra
        # no DRIVER do dano (=> D cresce no plato => dispara o joelho, resolve
        # §4.31) e e' acumulada em W_slip_acc/energia abaixo. 0 => 0.0 exato.
        dE_partial = 0.0
        if (self.mat.k_partial_slip > 0.0
                and self.mat.slip_regime_mode == "cattaneo_mindlin"):
            g_p = partial_slip_gate(self.state, self.geom, self.mat,
                                    F_amp, theta_load, "wear", slip_amp_override)
            delta_t = (F_slip_transverse(self.state, self.mat)
                       / max(k_tr_transverse(self.geom, self.mat), 1e-12))
            dE_partial = (self.mat.k_partial_slip * g_p
                          * 4.0 * mu_bearing_eff(self.state, self.mat)
                          * max(self.state.F_0, 0.0) * max(delta_t, 0.0))
            W_slip_cycle += dE_partial
        if self.mat.c_D > 0.0 and self.mat.W_ref > 0.0:
            # FATOR DE DWELL (estudo de variaveis, Yang 5/10Hz 2026-07-08): a
            # dose de dano por ciclo escala com o TEMPO de contato do slip —
            # fretting-corrosao (oxidacao durante o dwell; menos frequencia =
            # mais oxido por ciclo, Soderberg/Vingsbo). (f_ref/f)^p; p=0 => 1
            # exato (inerte). f_ref = ancora per-rig (freq de referencia).
            dwell = 1.0
            if self.mat.dmg_dwell_exp > 0.0 and freq > 0.0:
                dwell = (self.mat.f_ref_dmg / freq) ** self.mat.dmg_dwell_exp
            # ONSET FISICO CONTINUO (spec 2026-07-08, pedido do professor: fig6
            # e fig8 = MESMA fisica, joelho continuo na super-criticalidade, nao
            # chave per-caso). Em vez do limiar de energia W_crit, o crescimento
            # do dano e' gateado pela FRACAO DE GROSS-SLIP g_gross=slip/(slip+
            # delta_t) — a razao fisica s_a/s_crit (s_crit=delta_t=mu·F0/k_tr,
            # CAI com F0: o "falling F_V" do Bauer). g_gross^p: ~0 no plato (F0
            # alto, sub-critico), ->1 quando F0 cai (super-critico) => joelho cuja
            # NITIDEZ emerge da trajetoria de g_gross (fig6 quase-critico=joelho
            # minimo; fig8 super-critico=joelho forte), constantes compartilhadas.
            # dmg_gross_exp=0 => 1.0 (usa o gate W_crit legado, backward-compat).
            if self.mat.dmg_gross_exp > 0.0:
                g_gross = loosening_slip_gate(self.state, self.geom, self.mat,
                                              slip_amp_override)
                onset = g_gross ** self.mat.dmg_gross_exp
            else:
                onset = damage_onset_gate(self.state, self.mat)
            dD = (self.mat.c_D * dwell          # Estágio B: k_damage_scale foldado em c_D
                  * (W_slip_cycle / self.mat.W_ref) * (1.0 - self.state.D)
                  * onset)
            self.state.D = min(1.0, max(0.0, self.state.D + dD))

        # ===== 4.6) Acumula trabalho de slip transverso (driver da incubacao
        # do loosening). Calculado cru (4·μ·F_0·slip), independente dos tuners
        # de mecanismo, para que o onset do estagio 2 nao se desloque ao ajustar
        # k_wear/k_loose. Lido no proximo ciclo por loosening_gate.
        _slip_acc = (slip_amp_override if slip_amp_override is not None
                     else resolve_transverse_slip(self.state, self.mat,
                                                  F_amp, theta_load,
                                                  geom=self.geom))
        self.state.W_slip_acc += (4.0 * mu_bearing_eff(self.state, self.mat)
                                  * max(self.state.F_0, 0.0)
                                  * max(_slip_acc, 0.0))

        # dE_partial (computado em 4.5) tambem alimenta o acumulador de onset e o
        # budget de energia (§4.25). W_ext sourca (conservacao, como o viscoso).
        if dE_partial > 0.0:
            self.state.W_slip_acc += dE_partial
            self.energy.W_diss_wear += dE_partial
            self.energy.W_ext += dE_partial

        # ===== 4.7) Acumula trabalho de conformacao (pressure-weighted), driver
        # do conformation_gate (spec 2026-07-04). Mesmo slip cru de 4.6,
        # ponderado por (p/p_ref)^n, p = F_0/A_contact. Guardado por
        # W_conf_ref>0 => W_conf fica 0.0 exato quando inativo (backward-compat).
        if self.mat.W_conf_ref > 0.0:
            p = max(self.state.F_0, 0.0) / max(self.geom.A_contact, 1e-12)
            pw = (p / max(self.mat.p_ref_conform, 1e-12)) ** self.mat.conform_pressure_exp
            dW_conf = pw * (
                4.0 * mu_bearing_eff(self.state, self.mat)
                * max(self.state.F_0, 0.0) * max(_slip_acc, 0.0))
            if self.mat.conform_driver == "effective":
                # driver de equilibrio auto-limitante (spec §7): pondera pelo
                # gate de INICIO-de-ciclo (state.W_conf ainda nao foi atualizado
                # neste ciclo) — o mesmo g que os mecanismos viram; c e slip_eff
                # co-determinados, resolvido de forma explicita (consistente com
                # o padrao "le no inicio, atualiza depois" de W_slip_acc/D/F_0).
                dW_conf *= conformation_gate(self.state, self.mat)
            self.state.W_conf += dW_conf

        # ===== 5) Snapshot
        snap = CycleSnapshot(
            cycle=n,
            F_0=self.state.F_0,
            delta_U_stored=delta_U,
            W_ext_cycle=W_ext_c,
            W_diss_cycle=dE_diss_total,
            Phi_eff=Phi_eff(self.state, self.geom, self.mat),
            slip_fraction=slip_fraction_cycle,
            per_mechanism=per_mech,
            dF_0_by_mech=dF_0_by_mech,
            D=self.state.D,
        )
        self.history.append(snap)
        return snap

    def retighten(self, applied_torque: Optional[float] = None,
                  new_F0: Optional[float] = None) -> None:
        """Re-aperto quasi-estatico entre fases de ciclagem (spec 2026-07-07).

        Exatamente UM de:
          applied_torque [N.m]: preve a pre-carga recuperada via Motosh
            (tightening_torque, reusa mu_bearing_eff(D) -> falsify-first).
          new_F0 [N]: pre-carga pos-aperto explicita (override p/ testes/medido).

        Renova delta_emb (damage-coupled, k_emb_renew), zera theta_loose (porca
        girada de volta na direcao de aperto), rebaseia o segmento de energia.
        Persistem: D, delta_creep, delta_wear, delta_thread_fret, W_slip_acc,
        W_conf, F_0_init e o _cycle_counter (relogio do creep -- resetar
        multiplicaria o creep inicial).
        O trabalho discreto do re-aperto fica fora do budget por-ciclo (spec 3.5).
        """
        if (applied_torque is None) == (new_F0 is None):
            raise ValueError("retighten: forneca exatamente um de "
                             "applied_torque ou new_F0")
        if applied_torque is not None:
            coeff = tightening_torque(1.0, self.state, self.geom, self.mat)
            F0 = applied_torque / max(coeff, 1e-12)
        else:
            F0 = float(new_F0)
        if F0 < 0.0:
            raise ValueError(f"retighten: pre-carga negativa (F0={F0})")
        # Renovacao de embedding: capacidade restaurada ~ D (clamp [0, target]).
        target = (self.mat.emb_depth        # Estágio B: k_emb_scale removido
                  * embedding_conformance_factor(self.state, self.geom, self.mat))
        renewed = self.state.delta_emb * (1.0 - self.mat.k_emb_renew * self.state.D)
        self.state.delta_emb = min(max(renewed, 0.0), target)
        # D-J (2026-08-05): contador de eventos de re-aperto. Driver do
        # `retight_loss_gain` (perda por slip cresce a cada reaperto num
        # protocolo que NAO solta o parafuso: a interface segue engajada e
        # progressivamente danificada). Incrementado AQUI e em lugar nenhum
        # mais — e' isso que deixa o estagio virgem (n=0) bit-identico.
        self.state.n_retighten += 1
        # Re-estabelece pre-carga; porca girada de volta => theta_loose -> 0.
        self.state.F_0 = F0
        self.state.theta_loose = 0.0
        # Rebase do segmento de energia (novo baseline no estado pos-aperto).
        U_init = U_internal(self.state, self.geom, self.mat)
        self.energy = EnergyBudget(U_stored=U_init, U_stored_init=U_init)

    # ----- diagnóstico ----- #

    def energy_report(self) -> str:
        """Resumo legivel do balanco energetico cumulativo."""
        e = self.energy
        lines = [
            "=== Energy Budget (cumulativo) ===",
            f"  W_ext (externo absorvido):    {e.W_ext:12.3f} J",
            f"  U_released (do reservatorio): {e.U_released:12.3f} J",
            f"  Total energia entrada:        {e.W_ext + e.U_released:12.3f} J",
            "",
            f"  W_damp_visc (Rayleigh):       {e.W_damp_visc:12.3f} J",
            f"  W_diss_emb (plastic):         {e.W_diss_emb:12.3f} J",
            f"  W_diss_creep:                 {e.W_diss_creep:12.3f} J",
            f"  W_diss_friction_y (wear+slip):{e.W_diss_friction_y:12.3f} J",
            f"  W_diss_loose (thread):        {e.W_diss_loose:12.3f} J",
            f"  Total dissipado:              {e.W_diss_total:12.3f} J",
            "",
            f"  Conservation residual:        {e.conservation_residual:12.3e} J",
            f"  U_stored atual:               {e.U_stored:12.3f} J",
            f"  U_stored inicial:             {e.U_stored_init:12.3f} J",
            "",
            "=== Estado lento final ===",
            f"  F_0:           {self.state.F_0/1e3:.3f} kN  "
            f"(ratio = {self.state.F_0/max(self.state.F_0_init,1):.3f})",
            f"  delta_emb:     {self.state.delta_emb*1e6:.3f} um",
            f"  delta_creep:   {self.state.delta_creep*1e6:.3f} um",
            f"  delta_wear:    {self.state.delta_wear*1e6:.3f} um",
            f"  theta_loose:   {np.rad2deg(self.state.theta_loose):.4f} deg",
            f"  Phi_eff:       {self.Phi_eff():.3f}",
        ]
        return "\n".join(lines)


# ============================================================================
# Demo / smoke test
# ============================================================================

if __name__ == "__main__":
    # Cenário: M20×2.5, pré-carga 50 kN, loading combinado θ=45° @ F_amp=20 kN
    geom = JointGeometry(
        E=200e9, A_s=245e-6, L_eff=0.060,
        d_2=18.38e-3, pitch=2.5e-3,
        r_bearing=12e-3, A_contact=1.2e-4,
    )
    mat = JointMaterial(
        mu_thread=0.15, mu_bearing=0.15,
        k_wear_spec=5e-25, k_j_init=4e9, alpha_GW=0.5,
        emb_depth=3e-6, N_emb=50,
        C_creep=2e-12, t_0=1.0,
        rayleigh_alpha=0.01, rayleigh_beta=1e-5,
        m_x=0.5, m_y=0.5, I_theta=1e-5,
    )

    ana = DynamicStiffnessAnalyzer(geom, mat, initial_preload=50e3)
    print(f"Initial state:")
    print(f"  k_b      = {geom.k_b/1e6:.1f} MN/m")
    print(f"  k_j_ax,0 = {k_j_ax(ana.state, mat)/1e6:.1f} MN/m")
    print(f"  Phi_eff,0 = {ana.Phi_eff():.3f}")
    print(f"  U_int,0  = {ana.U_internal():.3f} J")
    print(f"  beta     = {np.rad2deg(geom.beta):.2f} deg")
    print()

    # Run 2000 cycles at θ=45° (combinado axial+transverso)
    N_TOTAL = 2000
    F_AMP = 20e3
    THETA = np.deg2rad(45)
    FREQ = 12.5  # Hz

    snaps = []
    for n in range(1, N_TOTAL + 1):
        snap = ana.step_cycle(F_AMP, THETA, FREQ)
        snaps.append(snap)
        if n % 400 == 0:
            print(f"  cycle {n:4d}: F_0={snap.F_0/1e3:6.2f} kN, "
                  f"Phi={snap.Phi_eff:.3f}, slip={snap.slip_fraction:.3f}, "
                  f"W_diss/cycle={snap.W_diss_cycle*1e3:.2f} mJ")

    print()
    print(ana.energy_report())

    # Sanity check: matrizes 3x3
    print()
    print("=== Matrizes finais ===")
    print("M =")
    print(ana.M())
    print("K(state) =")
    print(ana.K() / 1e6, " (MN/m units)")
    print("C(state) =")
    print(ana.C())
