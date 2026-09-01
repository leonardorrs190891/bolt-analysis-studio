"""L1-L7 plano, Task 4 (fatia 2b): Gate B1 re-executado com o canal L1 de
flanco (`flank_wear_on`/`k_wear_flank`/`flank_amp_exp`, landado na Task 3).

PRE-REGISTRO (verbatim, task-4-brief.md, ANTES de rodar qualquer fit):

    PREREG = {
      "gate": "B1-rerun",
      "H0": "com flank_wear_on, d(fim)/dA_F no rig Liu2017 tem sinal negativo e
             ordem 1e-5/N",
      "PASS": "slope in [-4.4e-5, -1.1e-5] por curva-completa fit (alvo
              -2.2e-5/N, tol 2x)",
      "FAIL2": "2 preregs consecutivos falhando => falsificacao documentada,
               sem forcar adocao",
      "no_regression": "casos transversais: mediana e count>0.10 identicos ao
                        baseline (flag off la)",
    }

Interpretacao operacional (controlador, 2026-07-16):
  - flank_wear_on=1.0 FIXO (config, nao fitado); libera SOMENTE
    {k_wear_flank, flank_amp_exp} (tentativa 1). Se o gate FALHAR, tentativa 2
    fixa flank_amp_exp=1.5 (Liu 2020) e libera so k_wear_flank.
  - Rigs: Liu2017 axial (9 curvas, alvo B1) + Liu2016 (14 curvas do R4, mesmo
    aparato/familia M12x1.75 30Hz — exclui a curva 5e6 de cauda
    NAO-MONOTONICA, ver nota abaixo) fitados JUNTOS como "Rig A" (mesma fisica
    L1). H.Li2022 (M10x1.5, varredura de frequencia @ A_F fixo) e' "Rig B"
    separado.
  - Identificabilidade (Rig B nao tem varredura de amplitude -- A_F=10kN fixo
    em toda a familia Li2022 -- entao k_wear_flank e flank_amp_exp sao
    degenerados nesse rig sozinho: d_w=k*p*(2s)^exp com s ~constante entre as
    4 curvas, qualquer exp e' absorvido por um k rescalado). Rig B portanto
    HERDA o flank_amp_exp do Rig A (a unica fonte que separa amplitude) e
    fita SO o k_wear_flank (constante de magnitude POR RIG, mesmo padrao
    "formas transferem, constantes nao" de C_creep/K_archard no resto do
    projeto). Isso tambem barateia o fit de forma honesta (nao arbitraria).
  - Custo computacional: os 1e6 ciclos de Liu2017/Liu2016 tornam um fit
    iterativo ingenuo proibitivo (~30-40min por PASSE completo x dezenas de
    avaliacoes = horas). Medido neste hardware: ~11.2k ciclos/s (force-mode).
    Escolha: FASE DE FIT usa um teto de ciclos reduzido (FIT_CAP_RIGA=1e4,
    ~10x menor que o range pleno) -- justificado empiricamente: a inspecao dos
    dados mostra que a separacao amplitude-dependente (o sinal que
    identifica k_wear_flank/flank_amp_exp) ja esta bem estabelecida por
    N~1e3-1e4 e muda pouco ate 1e6 (Liu2017: spread quase identico em N=1e3 e
    N=1e6). A FASE DE RELATORIO/GATE (que precisa do "fim" real reportado
    pelo paper) roda UMA passada por rig na resolucao PLENA (ate 1e6/5e6/
    3.3e5 conforme o caso) com os parametros ja fitados -- e' essa passada
    que produz o slope do gate e os MAE_post reportados. Busca em GRADE
    determinista 2 estagios (grosseiro+refino, custo fixo conhecido) em vez
    de scipy.least_squares: so 1-2 parametros, custo previsivel, evita
    problemas de escala numerica entre k_wear_flank~1e-14 e flank_amp_exp~1
    (least_squares com passo relativo padrao trata mal um parametro de escala
    1e-14 sem reparametrizacao log — grade em log10(k) e' mais simples e
    igualmente correta para so 1-2 parametros). MAE_pre (seed, pre-fit) e'
    calculado no teto de fit (barato); MAE_post (fitado) na resolucao PLENA.

Run:  python New_Theory/l1_axial_gate.py [--quick]
  --quick: subconjunto de curvas + tetos minusculos (smoke test, ~1-2 min;
           NAO grava JSON cientifico).
Runtime esperado do run completo: ~1.2h (gate passa na tentativa 1) a ~2.2h
(pior caso, precisa da tentativa 2) -- rodar em background.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial,
)
from bolt_analysis_studio.calibration import knowledge_base as kb  # noqa: E402
from library_common import (  # noqa: E402
    emb_depth_vdi, frozen_constants, geometry_for, load_full_curve,
)

# ---------------------------------------------------------------------------
PREREG = {
    "gate": "B1-rerun",
    "H0": "com flank_wear_on, d(fim)/dA_F no rig Liu2017 tem sinal negativo e "
          "ordem 1e-5/N",
    "PASS": "slope in [-4.4e-5, -1.1e-5] por curva-completa fit (alvo "
            "-2.2e-5/N, tol 2x)",
    "FAIL2": "2 preregs consecutivos falhando => falsificacao documentada, "
             "sem forcar adocao",
    "no_regression": "casos transversais: mediana e count>0.10 identicos ao "
                     "baseline (flag off la)",
}
PASS_BAND_PER_N = (-4.4e-5, -1.1e-5)   # (lo, hi); slope e' negativo, lo<hi

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
R4 = "BAS_V2_papers/E. Rodada 4 (deep-research 2026-07-11)/digitized_csv"

# --- Seed de k_wear_flank (KB, Task 4 e' quem LE o KB -- o engine nunca le) -
_ANCHOR = kb.wear_spec_anchor("thread", "35CrMo-SCM435")
SEED_K_WEAR_FLANK_ANCHOR = float(_ANCHOR["value"])       # 8.34e-15 1/Pa, Zhang 2019
# Reconciliacao de convencao (Task-3 review): flank_wear_axial_term usa
# slip_dist=2*s_th ("ida+volta"), enquanto os canais IRMAOS (WearLoss,
# ThreadFrettingLoss legado) usam 4*s_flank. A ancora foi lida p/ a convencao
# "4x"; para a MESMA profundidade fisica com metade da distancia de slip por
# ciclo, o k efetivo desta convencao precisa ser ~2x maior (k*2s ~ k_4x*4s/2
# => k = k_4x*2, aproximadamente, mantendo d_w na mesma ordem de grandeza).
_CONVENTION_FACTOR_2X = 2.0
SEED_K_WEAR_FLANK = SEED_K_WEAR_FLANK_ANCHOR * _CONVENTION_FACTOR_2X

# --- Bounds (log10 do k, para o parametro de 14 ordens de grandeza) ---------
LOG_K_BOUNDS = (-16.0, -11.0)          # k em [1e-16, 1e-11] 1/Pa (~5 decadas em torno do seed)
EXP_BOUNDS = (0.5, 3.0)                # flank_amp_exp (linear=1; Liu2020 super-linear 1.5-1.6)
EXP_FALLBACK = 1.5                     # tentativa 2 (Liu 2020, fixo)

FIT_CAP_RIGA = 10_000                 # ciclos p/ FASE DE FIT do Rig A (barato; ver docstring)
FIT_CAP_RIGB = None                   # Rig B ja e' barato (2e5-3.3e5); sem teto extra

# ---------------------------------------------------------------------------
# Condicoes por rig (nome, csv, F0[N], F_amp[N], base-dict, n_cycles_cap,
# trim_at[opcional], is_af_sweep)
# ---------------------------------------------------------------------------
LIU17_BASE = dict(bolt="M12x1.75", grip_mm=30.0, r_bearing_mm=None,
                  rz="Rz<4", n_if=1, mu=0.15, freq=30.0,
                  prov_rz="handbook (Bolt Science ~1um/interface, retificado; "
                          "verificado 2026-07-07, MODEL_LEGITIMACY 4.6)",
                  prov_grip="assumed (2.5d; banda 24-36mm)")
# Liu2016: mesma familia de rig/aparato (SWJTU/Liverpool) e MESMO fastener
# M12x1.75 (d_2=10.863mm bate exato com a tabela ISO), mas NAO reporta Ra/Rz
# (apparatus_notes/liu2016wear.md: "cannot assign a roughness class from this
# paper alone") e e' um PAR DE MATERIAL DIFERENTE (aco A283D EZP + porca Al
# 7050-T7451 + insert 316L, vs Liu2017 aco-aco 10.9). NAO importamos o Rz<4
# verificado do Liu2017 (seria emprestar uma proveniencia de OUTRO par de
# material) -- usamos o default generico "Rz<10" (mesma convencao "sem dado"
# usada alhures p/ Li2022ti), proveniencia 'assumed'. r_bearing e' MEDIDO
# no paper (De=15.75mm, Tabela 1) -- usamos direto (mais preciso que o
# 0.75*d default). Grip nao reportado no texto disponivel -- emprestado do
# Liu2017 (mesma familia de rig), 'assumed'.
LIU16_BASE = dict(bolt="M12x1.75", grip_mm=30.0, r_bearing_mm=7.875,
                  rz="Rz<10", n_if=1, mu=0.132, freq=30.0,
                  prov_rz="assumed (Ra/Rz nao reportado; par de material "
                          "distinto do Liu2017, nao herda Rz<4 verificado)",
                  prov_grip="assumed (emprestado do Liu2017, mesma familia "
                            "de rig; nao declarado no texto disponivel)",
                  prov_rbearing="paper (De=15.75mm, Tabela 1, r=De/2)")
LI22_BASE = dict(bolt="M10x1.5", grip_mm=25.0, r_bearing_mm=None,
                 rz="Rz<10", n_if=1, mu=0.15, freq=10.0,
                 prov_rz="assumed (banda classe adjacente)",
                 prov_grip="assumed (2.5d; banda 20-30mm)")

RIGA_CONDITIONS = [
    # --- Liu2017 (9 curvas: 5 P0-sweep + 4 AF-sweep; AF-sweep alvo B1) ------
    dict(name="Liu2017 P0=15", csv=f"{DIG}/liu2017_axial_F0_15kN.csv",
         F0=15e3, F_amp=10e3, base=LIU17_BASE, n_cycles=1_000_000, af=False),
    dict(name="Liu2017 P0=16.5", csv=f"{DIG}/liu2017_axial_F0_16p5kN.csv",
         F0=16.5e3, F_amp=10e3, base=LIU17_BASE, n_cycles=1_000_000, af=False),
    dict(name="Liu2017 P0=18 (=AF10)", csv=f"{DIG}/liu2017_axial_F0_18kN.csv",
         F0=18e3, F_amp=10e3, base=LIU17_BASE, n_cycles=1_000_000, af=True,
         af_group="liu2017"),
    dict(name="Liu2017 P0=19.5", csv=f"{DIG}/liu2017_axial_F0_19p5kN.csv",
         F0=19.5e3, F_amp=10e3, base=LIU17_BASE, n_cycles=1_000_000, af=False),
    dict(name="Liu2017 P0=21", csv=f"{DIG}/liu2017_axial_F0_21kN.csv",
         F0=21e3, F_amp=10e3, base=LIU17_BASE, n_cycles=1_000_000, af=False),
    dict(name="Liu2017 AF=7.5", csv=f"{DIG}/liu2017_axial_AF_7p5kN.csv",
         F0=18e3, F_amp=7.5e3, base=LIU17_BASE, n_cycles=1_000_000, af=True,
         af_group="liu2017"),
    dict(name="Liu2017 AF=8.75", csv=f"{DIG}/liu2017_axial_AF_8p75kN.csv",
         F0=18e3, F_amp=8.75e3, base=LIU17_BASE, n_cycles=1_000_000, af=True,
         af_group="liu2017"),
    dict(name="Liu2017 AF=11.25", csv=f"{DIG}/liu2017_axial_AF_11p25kN.csv",
         F0=18e3, F_amp=11.25e3, base=LIU17_BASE, n_cycles=1_000_000, af=True,
         af_group="liu2017"),
    dict(name="Liu2017 AF=12.5", csv=f"{DIG}/liu2017_axial_AF_12p5kN.csv",
         F0=18e3, F_amp=12.5e3, base=LIU17_BASE, n_cycles=1_000_000, af=True,
         af_group="liu2017"),
    # --- Liu2016 (14 curvas do R4; 5e6-cyc excluida, ver nota no topo) ------
    dict(name="Liu2016 M0=30 (F0=14kN)", csv=f"{R4}/liu2016wear_fig9a_m30nm.csv",
         F0=14e3, F_amp=10e3, base=LIU16_BASE, n_cycles=1_000_000, af=False),
    dict(name="Liu2016 M0=35 (F0=16kN)", csv=f"{R4}/liu2016wear_fig9a_m35nm.csv",
         F0=16e3, F_amp=10e3, base=LIU16_BASE, n_cycles=1_000_000, af=False),
    dict(name="Liu2016 M0=40 (F0=18kN)", csv=f"{R4}/liu2016wear_fig9a_m40nm.csv",
         F0=18e3, F_amp=10e3, base=LIU16_BASE, n_cycles=1_000_000, af=False),
    dict(name="Liu2016 M0=45 (F0=20kN)", csv=f"{R4}/liu2016wear_fig9a_m45nm.csv",
         F0=20e3, F_amp=10e3, base=LIU16_BASE, n_cycles=1_000_000, af=False),
    dict(name="Liu2016 M0=50 (F0=22kN)", csv=f"{R4}/liu2016wear_fig9a_m50nm.csv",
         F0=22e3, F_amp=10e3, base=LIU16_BASE, n_cycles=1_000_000, af=False),
    dict(name="Liu2016 AF=7.5", csv=f"{R4}/liu2016wear_fig11a_af7p5kn.csv",
         F0=14e3, F_amp=7.5e3, base=LIU16_BASE, n_cycles=1_000_000, af=True,
         af_group="liu2016"),
    dict(name="Liu2016 AF=8.75", csv=f"{R4}/liu2016wear_fig11a_af8p75kn.csv",
         F0=14e3, F_amp=8.75e3, base=LIU16_BASE, n_cycles=1_000_000, af=True,
         af_group="liu2016"),
    dict(name="Liu2016 AF=10", csv=f"{R4}/liu2016wear_fig11a_af10kn.csv",
         F0=14e3, F_amp=10e3, base=LIU16_BASE, n_cycles=1_000_000, af=True,
         af_group="liu2016"),
    dict(name="Liu2016 AF=11.25", csv=f"{R4}/liu2016wear_fig11a_af11p25kn.csv",
         F0=14e3, F_amp=11.25e3, base=LIU16_BASE, n_cycles=1_000_000, af=True,
         af_group="liu2016"),
    dict(name="Liu2016 AF=12.5", csv=f"{R4}/liu2016wear_fig11a_af12p5kn.csv",
         F0=14e3, F_amp=12.5e3, base=LIU16_BASE, n_cycles=1_000_000, af=True,
         af_group="liu2016"),
    dict(name="Liu2016 dry", csv=f"{R4}/liu2016wear_fig13a_dry.csv",
         F0=14e3, F_amp=10e3, base=LIU16_BASE, n_cycles=1_000_000, af=False),
    dict(name="Liu2016 MoS2", csv=f"{R4}/liu2016wear_fig13a_mos2.csv",
         F0=20e3, F_amp=10e3, base=dict(LIU16_BASE, mu=0.029), n_cycles=1_000_000,
         af=False),
    dict(name="Liu2016 long1e6", csv=f"{R4}/liu2016wear_fig7_run1_1e6cyc.csv",
         F0=14e3, F_amp=10e3, base=LIU16_BASE, n_cycles=1_000_000, af=False),
    # EXCLUIDA: liu2016wear_fig7_run2_5e6cyc.csv -- cauda NAO-MONOTONICA
    # (minimo ~N=2.2-2.3e6, recupera ate ~3.2-4e6, cai de novo) -- o proprio
    # apparatus_notes/liu2016wear.md e validation_cases.py flagram isso como
    # "out-of-model" (debris compactando/expelindo); nenhum mecanismo
    # monotonico do engine reproduz isso. Mesmo tratamento dos rabos de
    # fadiga (Yang2021/Li2022ti/liu2022): fora do escopo do fit.
]

RIGB_CONDITIONS = [
    dict(name="Li2022 10Hz", csv=f"{DIG}/li2022ti_axialmin_10Hz.csv",
         F0=12.5e3, F_amp=10e3, base=dict(LI22_BASE, freq=10.0),
         n_cycles=200_000, af=False),
    dict(name="Li2022 15Hz", csv=f"{DIG}/li2022ti_axialmin_15Hz.csv",
         F0=12.5e3, F_amp=10e3, base=dict(LI22_BASE, freq=15.0),
         n_cycles=200_000, af=False),
    dict(name="Li2022 20Hz", csv=f"{DIG}/li2022ti_axialmin_20Hz.csv",
         F0=12.5e3, F_amp=10e3, base=dict(LI22_BASE, freq=20.0),
         n_cycles=200_000, af=False),
    dict(name="Li2022 10Hz full", csv=f"{DIG}/li2022ti_axial_10Hz_full.csv",
         F0=12.5e3, F_amp=10e3, base=dict(LI22_BASE, freq=10.0),
         n_cycles=330_000, trim_at=330_000, af=False),
    # trim_at=3.3e5: estagio 3 (>3.3e5) e' iniciacao/crescimento de trinca no
    # raiz da rosca (fadiga), fora do escopo do modelo de afrouxamento --
    # mesmo tratamento de outros rabos de fadiga na biblioteca.
]

# sanity: cada af_group deve ter >=3 pontos p/ o polyfit de grau 1 fazer sentido
assert sum(1 for c in RIGA_CONDITIONS if c.get("af_group") == "liu2017") == 5
assert sum(1 for c in RIGA_CONDITIONS if c.get("af_group") == "liu2016") == 5


# ---------------------------------------------------------------------------
# Reparametrizacao (log_k_ref, exp) -> k_wear_flank PARA CONDICIONAMENTO
# NUMERICO DA BUSCA (nao mexe no engine -- flank_wear_axial_term continua
# usando k_wear_flank/flank_amp_exp exatamente como a Task 3 implementou).
#
# Motivacao (achado empirico do smoke test): d_w = k*p_flank*slip_dist**exp
# com slip_dist~1e-5 a 1e-4 m (SI). Como slip_dist << 1, MUDAR SO O EXPOENTE
# (0.5 a 3.0) faz slip_dist**exp variar VARIAS ORDENS DE GRANDEZA p/ o MESMO
# k -- uma grade ingenua em (log_k, exp) com bounds fixos gasta quase todos
# os pontos em regioes "nada acontece" (exp alto) ou "colapso catastrofico"
# (exp baixo), sem nunca visitar a faixa estreita onde os dois parametros
# produzem um efeito fisico razoavel simultaneamente.
#
# Fix: buscar em (log_k_ref, exp) onde k_ref = k_wear_flank NO PONTO DE
# REFERENCIA (slip_dist=slip_ref, i.e. F_amp=10kN -- a amplitude comum ao
# P0-sweep E aos dois AF-sweeps de Liu2017/Liu2016, e a UNICA testada em
# Li2022): k_wear_flank = k_ref * slip_ref**(1-exp). Substituindo de volta,
# d_w NO PONTO DE REFERENCIA = k_ref*p_flank*slip_ref, INDEPENDENTE de exp --
# k_ref carrega so a MAGNITUDE (mesma escala do SEED, que e' definido p/
# exp=1), exp carrega so a FORMA (como o efeito escala p/ AF!=10kN). Isso
# desacopla os dois parametros de busca sem alterar o que o engine recebe.
# ---------------------------------------------------------------------------
def slip_ref_for(bolt: str, grip_mm: float, F_amp_ref: float = 10e3) -> float:
    """slip_dist de referencia [m] (2*F_amp_ref/k_b) NA GEOMETRIA do rig, p/
    a reparametrizacao acima. F_amp_ref=10kN e' a condicao comum ao dataset
    (P0-sweep e ambos AF-sweep de Liu2017/Liu2016; unica amplitude em Li2022)."""
    geom = geometry_for(bolt, grip_mm)
    return 2.0 * F_amp_ref / geom.k_b


def k_wear_flank_from_ref(log_k_ref: float, exp: float, slip_ref: float) -> float:
    return (10.0 ** log_k_ref) * slip_ref ** (1.0 - exp)


# ---------------------------------------------------------------------------
# Simulacao de UMA curva
# ---------------------------------------------------------------------------
def _material(base: dict, consts: dict, k_wear_flank: float,
              flank_amp_exp: float) -> tuple:
    emb_m, _ = emb_depth_vdi(base["rz"], base["n_if"])
    geom = geometry_for(base["bolt"], base["grip_mm"],
                        r_bearing_mm=base.get("r_bearing_mm"))
    mat = JointMaterial(emb_depth=emb_m, mu_thread=base["mu"],
                        mu_bearing=base["mu"], k_thread_fret=0.0,
                        flank_wear_on=1.0, k_wear_flank=k_wear_flank,
                        flank_amp_exp=flank_amp_exp, **consts)
    return geom, mat


def simulate_curve(entry: dict, consts: dict, k_wear_flank: float,
                   flank_amp_exp: float, cap: int | None) -> dict:
    """Roda UMA curva ate min(n_cycles, extensao do CSV, cap) e alinha contra
    o dado (convencao predict_one do calibrate_axial.py: normaliza AMBOS no
    primeiro ponto do dado)."""
    cyc_d, r_d = load_full_curve(entry["csv"])
    trim_at = entry.get("trim_at")
    if trim_at is not None:
        keep = cyc_d <= trim_at
        cyc_d, r_d = cyc_d[keep], r_d[keep]
    n_max = int(min(entry["n_cycles"], cyc_d[-1]))
    if cap is not None:
        n_max = min(n_max, int(cap))
    keep = cyc_d <= n_max
    cyc_d, r_d = cyc_d[keep], r_d[keep]

    geom, mat = _material(entry["base"], consts, k_wear_flank, flank_amp_exp)
    ana = DynamicStiffnessAnalyzer(geom, mat, entry["F0"])
    ratio = np.empty(n_max + 1)
    ratio[0] = 1.0
    freq = entry["base"]["freq"]
    F_amp = entry["F_amp"]
    for n in range(1, n_max + 1):
        ana.step_cycle(F_amp, 0.0, freq)               # AXIAL, force-mode
        ratio[n] = max(ana.state.F_0, 0.0) / entry["F0"]
    sim_N = np.arange(n_max + 1)

    n0 = cyc_d[0]
    r_d_al = r_d / r_d[0]
    sim_at_n0 = np.interp(n0, sim_N, ratio)
    sim_al = ratio / max(sim_at_n0, 1e-9)
    pred = np.interp(cyc_d, sim_N, sim_al)
    mae = float(np.mean(np.abs(pred - r_d_al)))
    return dict(name=entry["name"], F0_N=entry["F0"], F_amp_N=F_amp,
               n_cycles=n_max, MAE=mae, final_data=float(r_d_al[-1]),
               final_pred=float(pred[-1]),
               conservation_residual=float(ana.energy.conservation_residual),
               af_group=entry.get("af_group"))


# ---------------------------------------------------------------------------
# Busca em grade determinista (2 estagios: grosseiro + refino). Busca-se em
# (log_k_ref, exp) [reparametrizado, ver bloco acima] -- k_wear_flank real
# (que entra no engine) e' derivado via k_wear_flank_from_ref antes de cada
# simulacao.
# ---------------------------------------------------------------------------
def _cost(conditions, consts, cap, log_k_ref, exp, slip_ref):
    k = k_wear_flank_from_ref(log_k_ref, exp, slip_ref)
    maes = [simulate_curve(e, consts, k, exp, cap)["MAE"] for e in conditions]
    return float(np.mean(maes))


def _sim_mae_task(args):
    """Worker de processo p/ o modo --workers do fit-only (fix wave da
    task-4 review): UMA simulate_curve -> MAE. Funcao pura dos args
    (engine deterministico, sem RNG), entao paralelizar NAO muda nenhum
    numero -- so o wall time."""
    entry, consts, k, exp, cap = args
    return simulate_curve(entry, consts, k, exp, cap)["MAE"]


def _stage_costs(conditions, consts, cap, pts, slip_ref, pool):
    """Custos de um estagio da grade, nos pontos `pts` [(log_k_ref, exp)],
    na MESMA ordem. pool=None -> caminho serial identico ao original
    (_cost por ponto). pool=ProcessPoolExecutor -> as simulacoes
    (ponto x curva) sao distribuidas, mas cada MAE por ponto e' a MESMA
    media np.mean sobre a MESMA lista ordenada de MAEs por curva que _cost
    computa -- bit-identico ao serial (validado no smoke: serial==parallel
    exato), so' mais rapido. Motivacao: viabilizar o re-run de auditoria
    em janelas foreground de 10 min (fit serial ~16-24 min/rig)."""
    if pool is None:
        return [_cost(conditions, consts, cap, k, e, slip_ref)
                for (k, e) in pts]
    tasks = []
    for (k, e) in pts:
        k_eng = k_wear_flank_from_ref(k, e, slip_ref)
        for entry in conditions:
            tasks.append((entry, consts, k_eng, e, cap))
    maes = list(pool.map(_sim_mae_task, tasks))
    nc = len(conditions)
    return [float(np.mean(maes[i * nc:(i + 1) * nc])) for i in range(len(pts))]


def grid_search_2d(conditions, consts, cap, slip_ref, log_k_bounds, exp_bounds,
                   n_coarse=5, n_refine=5, log=print, pool=None):
    k_lo, k_hi = log_k_bounds
    e_lo, e_hi = exp_bounds
    grid = []

    def _scan(klo, khi, elo, ehi, tag):
        ks = np.linspace(klo, khi, n_coarse)
        es = np.linspace(elo, ehi, n_coarse)
        pts = [(k, e) for k in ks for e in es]   # ordem de varredura original
        costs = _stage_costs(conditions, consts, cap, pts, slip_ref, pool)
        best = None
        for (k, e), c in zip(pts, costs):
            grid.append((tag, float(k), float(e), c))
            if best is None or c < best[2]:
                # cast p/ float PURO (nao numpy.float64 de iterar
                # np.linspace) -- senao json.dumps falha so no final,
                # depois da fase cara (mesma classe de bug do af_slope).
                best = (float(k), float(e), c)
            log(f"    [{tag}] log_k_ref={k:+.3f} exp={e:.3f} -> MAE={c:.4f}")
        return best

    b1 = _scan(k_lo, k_hi, e_lo, e_hi, "coarse")
    dk = (k_hi - k_lo) / (n_coarse - 1)
    de = (e_hi - e_lo) / (n_coarse - 1)
    k_lo2, k_hi2 = max(k_lo, b1[0] - dk), min(k_hi, b1[0] + dk)
    e_lo2, e_hi2 = max(e_lo, b1[1] - de), min(e_hi, b1[1] + de)
    b2 = _scan(k_lo2, k_hi2, e_lo2, e_hi2, "refine")
    best = b2 if b2[2] < b1[2] else b1
    return dict(log_k_ref=best[0], k=k_wear_flank_from_ref(best[0], best[1], slip_ref),
               exp=best[1], mae=best[2], grid=grid,
               saturated_lo=bool(np.isclose(best[0], k_lo, atol=1e-6)),
               saturated_hi=bool(np.isclose(best[0], k_hi, atol=1e-6)))


def grid_search_1d(conditions, consts, cap, slip_ref, log_k_bounds, exp_fixed,
                   n_coarse=9, n_refine=9, log=print, pool=None):
    k_lo, k_hi = log_k_bounds
    grid = []

    def _scan(klo, khi, tag, n):
        ks = np.linspace(klo, khi, n)
        pts = [(k, exp_fixed) for k in ks]
        costs = _stage_costs(conditions, consts, cap, pts, slip_ref, pool)
        best = None
        for (k, _e), c in zip(pts, costs):
            grid.append((tag, float(k), exp_fixed, c))
            if best is None or c < best[1]:
                best = (float(k), c)   # cast: ver nota em grid_search_2d
            log(f"    [{tag}] log_k_ref={k:+.3f} exp={exp_fixed:.3f}(fixo) -> MAE={c:.4f}")
        return best

    b1 = _scan(k_lo, k_hi, "coarse", n_coarse)
    dk = (k_hi - k_lo) / (n_coarse - 1)
    k_lo2, k_hi2 = max(k_lo, b1[0] - dk), min(k_hi, b1[0] + dk)
    b2 = _scan(k_lo2, k_hi2, "refine", n_refine)
    best = b2 if b2[1] < b1[1] else b1
    return dict(log_k_ref=best[0], k=k_wear_flank_from_ref(best[0], exp_fixed, slip_ref),
               exp=exp_fixed, mae=best[1], grid=grid,
               saturated_lo=bool(np.isclose(best[0], k_lo, atol=1e-6)),
               saturated_hi=bool(np.isclose(best[0], k_hi, atol=1e-6)))


# ---------------------------------------------------------------------------
# Slope d(fim)/d(A_F) sobre um af_group, a partir dos resultados JA simulados
# ---------------------------------------------------------------------------
def af_slope(results: list, group: str) -> dict:
    xs = [r["F_amp_N"] for r in results if r.get("af_group") == group]
    yd = [r["final_data"] for r in results if r.get("af_group") == group]
    yp = [r["final_pred"] for r in results if r.get("af_group") == group]
    order = np.argsort(xs)
    # cast de volta p/ float PURO (nao numpy.float64) -- json.dumps nao
    # serializa escalares numpy; np.array(...)[order] preserva o dtype
    # numpy mesmo depois de list(...), o que so falharia tarde (na escrita
    # do JSON final, apos a fase cara), entao o cast explicito e' obrigatorio.
    xs = [float(v) for v in np.array(xs)[order]]
    yd = [float(v) for v in np.array(yd)[order]]
    yp = [float(v) for v in np.array(yp)[order]]
    if len(xs) < 3:
        return dict(n_points=len(xs), data_per_N=float("nan"),
                   model_per_N=float("nan"))
    gd = float(np.polyfit(xs, yd, 1)[0])
    gp = float(np.polyfit(xs, yp, 1)[0])
    return dict(n_points=len(xs), F_amp_N=xs, final_data=yd, final_pred=yp,
               data_per_N=gd, model_per_N=gp,
               data_per_kN=gd * 1e3, model_per_kN=gp * 1e3)


# ---------------------------------------------------------------------------
# no_regression: um caso transversal (M16 shear canonico) tem que ficar
# BIT-IDENTICO com o canal L1 engajado (flag inerte fora do modo forca axial
# puro) -- ja e' registry-truth-tested em test_l1_flank_wear_axial.py; aqui
# repetimos no NIVEL DA TASK com os valores REALMENTE FITADOS, na geometria
# canonica compartilhada (shared block), nao um JointMaterial() sintetico.
# ---------------------------------------------------------------------------
def no_regression_check(k_wear_flank: float, flank_amp_exp: float) -> dict:
    consts, _ = frozen_constants()
    geom = geometry_for("M16x2.0", 50.0)
    F0, F_amp, delta_amp, theta, freq = 50_000.0, 20_000.0, 0.5e-3, np.pi / 2, 0.5
    n_cycles = 600

    def _run(flank_on: float) -> np.ndarray:
        mat = JointMaterial(emb_depth=30e-6, mu_thread=0.15, mu_bearing=0.15,
                            flank_wear_on=flank_on, k_wear_flank=k_wear_flank,
                            flank_amp_exp=flank_amp_exp, **consts)
        ana = DynamicStiffnessAnalyzer(geom, mat, F0)
        out = [1.0]
        for _ in range(n_cycles):
            ana.step_cycle(F_amp, theta, freq, delta_amp=delta_amp)
            out.append(max(ana.state.F_0, 0.0) / F0)
        return np.array(out)

    base = _run(0.0)
    with_flank = _run(1.0)
    identical = bool(np.array_equal(base, with_flank))
    return dict(identical=identical, n_cycles=n_cycles,
               final_ratio_baseline=float(base[-1]),
               final_ratio_with_flank_on=float(with_flank[-1]),
               setup="M16 shear canonico (calibrate_shared geometry: M16x2.0, "
                     "grip 50mm), bloco shared (constantes fisicas), F0=50kN "
                     "F_amp=20kN delta_amp=0.5mm theta=pi/2 freq=0.5Hz",
               note="disp-mode transversal: canal L1 gateado OFF por "
                    "construcao (_axial_forca / delta_amp-is-None guard); "
                    "confirma bit-identidade mesmo com k_wear_flank/"
                    "flank_amp_exp FITADOS engajados (flank_wear_on=1).")


# ---------------------------------------------------------------------------
# Fases de FIT extraidas p/ funcoes (task-4 review, Finding 1): mesmo codigo
# exato usado por run_attempt() (fit completo) E run_attempt_fit_only()
# (re-run de auditoria/determinismo, mais abaixo) -- extracao mecanica, SEM
# mudanca de logica, so' para os dois caminhos compartilharem o mesmo trace.
# ---------------------------------------------------------------------------
def _fit_rig_a(riga, consts, cap_a, slip_ref_A, free_exp, n_coarse, n_refine,
              log=print, pool=None):
    t0 = time.time()
    log(f"-- Rig A (Liu2017+Liu2016, {len(riga)} curvas) fit, cap={cap_a} --")
    if free_exp:
        nc_used, nr_used = n_coarse, n_refine
        fitA = grid_search_2d(riga, consts, cap_a, slip_ref_A, LOG_K_BOUNDS,
                              EXP_BOUNDS, n_coarse=nc_used, n_refine=nr_used,
                              log=log, pool=pool)
    else:
        nc_used, nr_used = 2 * n_coarse - 1, 2 * n_refine - 1
        fitA = grid_search_1d(riga, consts, cap_a, slip_ref_A, LOG_K_BOUNDS,
                              EXP_FALLBACK, n_coarse=nc_used,
                              n_refine=nr_used, log=log, pool=pool)
    dt_fitA = time.time() - t0
    log(f"Rig A fitted: k_wear_flank={fitA['k']:.4g} 1/Pa  "
        f"flank_amp_exp={fitA['exp']:.4g}  MAE(fit-cap)={fitA['mae']:.4f}  "
        f"({dt_fitA:.1f}s, saturated_lo={fitA['saturated_lo']} "
        f"saturated_hi={fitA['saturated_hi']})")

    mae_pre_A = _cost(riga, consts, cap_a, np.log10(SEED_K_WEAR_FLANK), 1.0, slip_ref_A)
    log(f"Rig A seed (k={SEED_K_WEAR_FLANK:.4g}, exp=1.0) MAE(fit-cap)={mae_pre_A:.4f}")
    return fitA, dt_fitA, mae_pre_A, nc_used, nr_used


def _fit_rig_b(rigb, consts, cap_b, slip_ref_B, exp_inherited, log=print,
               pool=None):
    log(f"\n-- Rig B (H.Li2022, {len(rigb)} curvas) fit (exp herdado="
        f"{exp_inherited:.4g}, ver identificabilidade na docstring) --")
    t0 = time.time()
    fitB = grid_search_1d(rigb, consts, cap_b, slip_ref_B, LOG_K_BOUNDS,
                          exp_inherited, n_coarse=9, n_refine=9, log=log,
                          pool=pool)
    dt_fitB = time.time() - t0
    log(f"Rig B fitted: k_wear_flank={fitB['k']:.4g} 1/Pa  "
        f"(exp herdado {fitB['exp']:.4g})  MAE={fitB['mae']:.4f}  ({dt_fitB:.1f}s)")

    mae_pre_B = _cost(rigb, consts, cap_b, np.log10(SEED_K_WEAR_FLANK), 1.0, slip_ref_B)
    return fitB, dt_fitB, mae_pre_B


def _search_grid_payload(fit_result: dict, two_d: bool, cap: int | None,
                         n_coarse: int, n_refine: int) -> dict:
    """Persiste o TRACE de busca em grade determinista (task-4 review,
    Finding 1): todo ponto (log_k_ref, exp, MAE) visitado pelo scan
    grosseiro+refino, mais os bounds -- para o JSON ser evidencia
    auto-contida e auditavel de COMO k_wear_flank/flank_amp_exp foram
    selecionados. grid_search_2d/1d ja computavam e retornavam isso
    (fit_result["grid"]) mas era descartado antes de chegar no JSON final
    (nunca usado em rigA=dict(...)/rigB=dict(...))."""
    return dict(
        log_k_bounds=list(LOG_K_BOUNDS),
        exp_bounds=(list(EXP_BOUNDS) if two_d else None),
        exp_fixed=(None if two_d else fit_result["exp"]),
        fit_cycle_cap=cap,
        n_coarse=n_coarse, n_refine=n_refine,
        n_points=len(fit_result["grid"]),
        points=[dict(stage=tag, log_k_ref=k, exp=e, mae=c)
                for (tag, k, e, c) in fit_result["grid"]],
    )


# ---------------------------------------------------------------------------
# UM "attempt" completo: fita Rig A (livre conforme free_exp), fita Rig B
# (so k, exp herdado do Rig A), relatorio full-res, slopes, gate, no_regression.
# ---------------------------------------------------------------------------
def run_attempt(attempt_no: int, free_exp: bool, quick: bool, log=print) -> dict:
    consts, prov = frozen_constants()
    # quick: usa exatamente as 5 curvas do AF-sweep Liu2017 (exercita o
    # calculo de slope de verdade, nao so um subconjunto sem variacao de
    # amplitude -- a primeira rodada usava riga[:3] = so P0-sweep, sem
    # sinal de amplitude, o que so testava o codigo "sem crash" mas nao a
    # logica do slope/gate).
    riga = ([c for c in RIGA_CONDITIONS if c.get("af_group") == "liu2017"]
            if quick else RIGA_CONDITIONS)
    rigb = RIGB_CONDITIONS[:2] if quick else RIGB_CONDITIONS
    cap_a = 1000 if quick else FIT_CAP_RIGA
    cap_b = 1000 if quick else FIT_CAP_RIGB
    n_coarse = 3 if quick else 5
    n_refine = 3 if quick else 5
    # smoke test: a fase de RELATORIO (full-res) tambem precisa de um teto
    # pequeno em --quick, senao ela roda 1e6 ciclos mesmo no smoke (bug
    # pego na primeira rodada: --quick "completava" em ~9-10min so por causa
    # do relatorio nao-tetado, nao dos 5s do fit).
    report_cap_a = 2000 if quick else None
    report_cap_b = 2000 if quick else None
    # slip_ref por rig (reparametrizacao de busca, ver bloco acima) -- Rig A
    # (Liu2017+Liu2016) compartilha geometria M12x1.75/grip 30mm.
    slip_ref_A = slip_ref_for(LIU17_BASE["bolt"], LIU17_BASE["grip_mm"])
    slip_ref_B = slip_ref_for(LI22_BASE["bolt"], LI22_BASE["grip_mm"])

    log(f"\n{'=' * 70}\nATTEMPT {attempt_no} (free_exp={free_exp}) "
        f"{'[QUICK SMOKE]' if quick else ''}\n{'=' * 70}")

    # ---- Rig A: fit (extraido p/ _fit_rig_a -- ver nota acima) -------------
    fitA, dt_fitA, mae_pre_A, nc_A, nr_A = _fit_rig_a(
        riga, consts, cap_a, slip_ref_A, free_exp, n_coarse, n_refine, log=log)

    # ---- Rig A: report (full resolution, fitted + seed per-curve) ----------
    log("-- Rig A report (resolucao PLENA) --")
    t0 = time.time()
    results_A_post = [simulate_curve(e, consts, fitA["k"], fitA["exp"], report_cap_a)
                      for e in riga]
    results_A_pre = [simulate_curve(e, consts, SEED_K_WEAR_FLANK, 1.0, report_cap_a)
                     for e in riga]
    dt_reportA = time.time() - t0
    for rpost, rpre in zip(results_A_post, results_A_pre):
        rpost["MAE_pre"] = rpre["MAE"]
        rpost["MAE_post"] = rpost.pop("MAE")
    log(f"Rig A report done in {dt_reportA:.1f}s; MAE_post median="
        f"{np.median([r['MAE_post'] for r in results_A_post]):.4f}")

    # ---- diagnostico: af-group (carrega o sinal de amplitude) vs nao-af
    # (P0/M0-sweep + dry/mos2/long1e6, todos em F_amp=10kN -- por construcao
    # da reparametrizacao slip_ref, EXP-INVARIANTES) -- explica se a media
    # igualmente ponderada nas 22 curvas e' dominada pelo subconjunto que nao
    # carrega sinal de amplitude (mais da metade do rig). NAO influencia o
    # fit em si (so' um relatorio pos-hoc dos resultados ja simulados).
    af_maes = [r["MAE_post"] for r in results_A_post if r.get("af_group")]
    nonaf_maes = [r["MAE_post"] for r in results_A_post if not r.get("af_group")]
    diag_af_split = dict(
        n_af_group=len(af_maes), n_non_af_group=len(nonaf_maes),
        mae_post_median_af_group=float(np.median(af_maes)) if af_maes else None,
        mae_post_median_non_af_group=float(np.median(nonaf_maes)) if nonaf_maes else None,
        note="curvas non-af-group tem F_amp=10kN (=slip_ref) -> por "
             "construcao da reparametrizacao (k_wear_flank_from_ref), a "
             "resposta delas a k_ref e' INDEPENDENTE de flank_amp_exp; se "
             "dominarem a media igualmente ponderada das 22 curvas, o fit "
             "fica com pouco poder p/ identificar o expoente (mesma logica "
             "de identificabilidade do Rig B, so' que parcial aqui).")
    log(f"diag af-split: n_af={len(af_maes)} MAE_post_med={diag_af_split['mae_post_median_af_group']}"
        f"  n_non_af={len(nonaf_maes)} MAE_post_med={diag_af_split['mae_post_median_non_af_group']}")

    slope_liu2017 = af_slope(results_A_post, "liu2017")
    slope_liu2016 = af_slope(results_A_post, "liu2016")
    log(f"Liu2017 AF-sweep slope: dado={slope_liu2017['data_per_N']:.3e}/N  "
        f"modelo={slope_liu2017['model_per_N']:.3e}/N")
    log(f"Liu2016 AF-sweep slope: dado={slope_liu2016['data_per_N']:.3e}/N  "
        f"modelo={slope_liu2016['model_per_N']:.3e}/N")

    # ---- Rig B: fit (extraido p/ _fit_rig_b -- ver nota acima) -------------
    fitB, dt_fitB, mae_pre_B = _fit_rig_b(
        rigb, consts, cap_b, slip_ref_B, fitA["exp"], log=log)
    results_B_post = [simulate_curve(e, consts, fitB["k"], fitB["exp"], report_cap_b)
                      for e in rigb]
    results_B_pre = [simulate_curve(e, consts, SEED_K_WEAR_FLANK, 1.0, report_cap_b)
                     for e in rigb]
    for rpost, rpre in zip(results_B_post, results_B_pre):
        rpost["MAE_pre"] = rpre["MAE"]
        rpost["MAE_post"] = rpost.pop("MAE")
    log(f"Rig B report: MAE_post median="
        f"{np.median([r['MAE_post'] for r in results_B_post]):.4f}")

    # ---- gate (Liu2017 apenas, per PREREG H0) ------------------------------
    slope_val = slope_liu2017["model_per_N"]
    lo, hi = PASS_BAND_PER_N
    gate_pass = bool(lo <= slope_val <= hi) if np.isfinite(slope_val) else False
    log(f"\nGATE (Liu2017 model slope {slope_val:.3e}/N in "
        f"[{lo:.2e},{hi:.2e}]): {'PASS' if gate_pass else 'FAIL'}")

    # ---- no_regression ------------------------------------------------------
    nr = no_regression_check(fitA["k"], fitA["exp"])
    log(f"no_regression (transverse untouched): identical={nr['identical']}")

    return dict(
        attempt=attempt_no, free_exp=free_exp,
        seed=dict(anchor=SEED_K_WEAR_FLANK_ANCHOR,
                  convention_factor=_CONVENTION_FACTOR_2X,
                  seed_used=SEED_K_WEAR_FLANK),
        rigA=dict(name="Liu2017+Liu2016 (M12x1.75 axial force-mode, 30Hz)",
                 n_curves=len(riga), fit_cycle_cap=cap_a,
                 fit_runtime_s=dt_fitA, report_runtime_s=dt_reportA,
                 fitted=dict(k_wear_flank=fitA["k"], flank_amp_exp=fitA["exp"]),
                 fit_mae_at_cap=fitA["mae"], seed_mae_at_cap=mae_pre_A,
                 saturated_lo=fitA["saturated_lo"], saturated_hi=fitA["saturated_hi"],
                 curves=results_A_post,
                 diag_af_group_vs_non_af_group=diag_af_split,
                 liu2017_af_sweep_slope=slope_liu2017,
                 liu2016_af_sweep_slope=slope_liu2016),
        rigB=dict(name="H.Li2022 (M10x1.5 axial x freq, force-mode)",
                 n_curves=len(rigb), fit_cycle_cap=cap_b,
                 fit_runtime_s=dt_fitB,
                 fitted=dict(k_wear_flank=fitB["k"],
                             flank_amp_exp=fitB["exp"]),
                 fit_mae=fitB["mae"], seed_mae=mae_pre_B,
                 saturated_lo=fitB["saturated_lo"], saturated_hi=fitB["saturated_hi"],
                 curves=results_B_post,
                 note="sem varredura de amplitude (A_F=10kN fixo em toda a "
                      "familia) -- exp NAO identificavel neste rig sozinho, "
                      "herdado do Rig A; so k_wear_flank e' fitado aqui "
                      "(constante de magnitude POR RIG)."),
        gate=dict(slope_liu2017_per_N=slope_val, PASS_band_per_N=list(PASS_BAND_PER_N),
                 verdict="PASS" if gate_pass else "FAIL"),
        no_regression=nr,
        # Task-4 review Finding 1: persiste o TRACE de busca em grade
        # (pontos + bounds) NO DICT DO ATTEMPT (top-level, irmao de
        # rigA/rigB/gate) -- grid_search_2d/1d ja computam e retornam isso
        # (fitA["grid"]/fitB["grid"]) mas era descartado aqui antes de
        # chegar no JSON. Adicao SOMENTE de auditoria: nao altera fitA/fitB/
        # gate/slope/no_regression em nada.
        grid=dict(rigA=_search_grid_payload(fitA, two_d=free_exp, cap=cap_a,
                                            n_coarse=nc_A, n_refine=nr_A),
                  rigB=_search_grid_payload(fitB, two_d=False, cap=cap_b,
                                            n_coarse=9, n_refine=9)),
    )


def run_attempt_fit_only(attempt_no: int, free_exp: bool, quick: bool = False,
                         log=print, rig: str = "both",
                         exp_inherited: float | None = None,
                         workers: int = 1) -> dict:
    """Re-run SOMENTE da fase de FIT (task-4 review, Finding 1b/1c): chama
    exatamente as mesmas _fit_rig_a/_fit_rig_b que run_attempt() usa (mesmas
    condicoes/cap/bounds/n_coarse/n_refine quando quick=False -- reproduz o
    fit COMPLETO), mas PULA a fase de relatorio full-res (curves/diag/
    slopes), o calculo do gate e o no_regression_check -- nada disso e
    necessario para regenerar+verificar a grade de busca, e o gate/verdict/
    slopes/curves JA COMMITADOS sao REUSADOS verbatim, nao recalculados.
    quick=True usa as mesmas condicoes/tetos reduzidos do smoke test de
    run_attempt (so' para validar o plumbing da CLI barato; NAO e' o re-run
    de auditoria real). Usado via `--fit-only --attempt=N` para (1)
    checar determinismo do k/exp fitado contra o JSON commitado e (2)
    fornecer a grade+bounds a mesclar.

    rig: "both" (default) fita A e depois B (exp de B herdado ao vivo do A,
    como no run completo); "A" fita so o Rig A; "B" fita so o Rig B e exige
    exp_inherited explicito (o chamador passa o exp do Rig A ja VERIFICADO
    contra o JSON commitado -- mesma cadeia de heranca, so que checada no
    meio). O split por rig existe p/ caber em janelas foreground de 10 min.

    workers: >1 liga um ProcessPoolExecutor p/ as simulacoes por curva
    (ver _stage_costs: mesma aritmetica, so' wall time menor). O run
    canonico completo (run_attempt) permanece serial e intocado."""
    if rig not in ("A", "B", "both"):
        raise SystemExit(f"rig must be A|B|both, got {rig!r}")
    if rig == "B" and exp_inherited is None:
        raise SystemExit("--rig=B requires --exp-inherited=<flank_amp_exp "
                         "do Rig A ja verificado contra o JSON commitado>")
    consts, _prov = frozen_constants()
    riga = ([c for c in RIGA_CONDITIONS if c.get("af_group") == "liu2017"]
            if quick else RIGA_CONDITIONS)
    rigb = RIGB_CONDITIONS[:2] if quick else RIGB_CONDITIONS
    cap_a = 1000 if quick else FIT_CAP_RIGA
    cap_b = 1000 if quick else FIT_CAP_RIGB
    n_coarse = 3 if quick else 5
    n_refine = 3 if quick else 5
    slip_ref_A = slip_ref_for(LIU17_BASE["bolt"], LIU17_BASE["grip_mm"])
    slip_ref_B = slip_ref_for(LI22_BASE["bolt"], LI22_BASE["grip_mm"])

    log(f"\n{'=' * 70}\nATTEMPT {attempt_no} (free_exp={free_exp}) "
        f"[FIT-ONLY rig={rig} workers={workers}"
        f"{', QUICK SMOKE' if quick else ''}, fase de relatorio "
        f"pulada]\n{'=' * 70}")

    out = dict(attempt=attempt_no, free_exp=free_exp, quick=quick, rig=rig,
               workers=workers)
    grids = {}
    pool = ProcessPoolExecutor(max_workers=workers) if workers > 1 else None
    try:
        exp_for_b = exp_inherited
        if rig in ("A", "both"):
            fitA, dt_fitA, mae_pre_A, nc_A, nr_A = _fit_rig_a(
                riga, consts, cap_a, slip_ref_A, free_exp, n_coarse, n_refine,
                log=log, pool=pool)
            out["rigA"] = dict(
                fitted=dict(k_wear_flank=fitA["k"], flank_amp_exp=fitA["exp"]),
                fit_mae_at_cap=fitA["mae"], seed_mae_at_cap=mae_pre_A,
                saturated_lo=fitA["saturated_lo"], saturated_hi=fitA["saturated_hi"],
                fit_runtime_s=dt_fitA)
            grids["rigA"] = _search_grid_payload(fitA, two_d=free_exp, cap=cap_a,
                                                 n_coarse=nc_A, n_refine=nr_A)
            exp_for_b = fitA["exp"]
        if rig in ("B", "both"):
            fitB, dt_fitB, mae_pre_B = _fit_rig_b(
                rigb, consts, cap_b, slip_ref_B, exp_for_b, log=log, pool=pool)
            out["rigB"] = dict(
                fitted=dict(k_wear_flank=fitB["k"], flank_amp_exp=fitB["exp"]),
                fit_mae=fitB["mae"], seed_mae=mae_pre_B,
                saturated_lo=fitB["saturated_lo"], saturated_hi=fitB["saturated_hi"],
                fit_runtime_s=dt_fitB, exp_inherited_from=(
                    "rigA fit (live, same-process)" if rig == "both"
                    else f"--exp-inherited={exp_inherited!r} (caller-verified)"))
            grids["rigB"] = _search_grid_payload(fitB, two_d=False, cap=cap_b,
                                                 n_coarse=9, n_refine=9)
    finally:
        if pool is not None:
            pool.shutdown()
    out["grid"] = grids
    return out


def main():
    quick = "--quick" in sys.argv
    fit_only = "--fit-only" in sys.argv
    attempt_arg = next((a.split("=", 1)[1] for a in sys.argv
                        if a.startswith("--attempt=")), None)
    out_arg = next((a.split("=", 1)[1] for a in sys.argv
                    if a.startswith("--out=")), None)
    rig_arg = next((a.split("=", 1)[1] for a in sys.argv
                    if a.startswith("--rig=")), "both")
    exp_inh_arg = next((a.split("=", 1)[1] for a in sys.argv
                        if a.startswith("--exp-inherited=")), None)
    workers_arg = next((a.split("=", 1)[1] for a in sys.argv
                        if a.startswith("--workers=")), "1")
    t_start = time.time()

    def log(msg):
        print(msg, flush=True)

    if fit_only:
        # Task-4 review Finding 1b: entry-point SOMENTE de auditoria.
        # Regenera a grade de busca determinista de UM attempt sem pagar a
        # fase de relatorio full-res (~60min/attempt). NAO escreve/toca
        # l1_axial_gate_result.json -- escreve em --out (ou stdout) para o
        # caller fazer o determinism-check + merge separadamente (ver
        # task-4-report.md, secao "Fix wave"). --rig=A|B + --workers=N
        # existem p/ caber em janelas foreground de 10 min (ver
        # run_attempt_fit_only).
        if attempt_arg not in ("1", "2"):
            raise SystemExit("--fit-only requires --attempt=1 or --attempt=2")
        attempt_no = int(attempt_arg)
        free_exp = (attempt_no == 1)   # espelha o dispatch do run completo abaixo
        exp_inherited = float(exp_inh_arg) if exp_inh_arg is not None else None
        workers = int(workers_arg)
        log(f"[FIT-ONLY] attempt={attempt_no} free_exp={free_exp} quick={quick} "
            f"rig={rig_arg} workers={workers} -- "
            f"report/gate/slope/no_regression NAO recalculados (valores "
            f"commitados sao reusados).")
        result = run_attempt_fit_only(attempt_no, free_exp, quick=quick,
                                      log=log, rig=rig_arg,
                                      exp_inherited=exp_inherited,
                                      workers=workers)
        result["runtime_total_s"] = time.time() - t_start
        payload = json.dumps(result, indent=2, ensure_ascii=False)
        if out_arg:
            out_path = Path(out_arg)
            out_path.write_text(payload, encoding="utf-8")
            log(f"[FIT-ONLY] JSON written: {out_path}")
        else:
            log("[FIT-ONLY] JSON result:\n" + payload)
        return

    log(f"PREREG: {json.dumps(PREREG, ensure_ascii=False, indent=2)}")
    log(f"Seed k_wear_flank: anchor={SEED_K_WEAR_FLANK_ANCHOR:.4g} 1/Pa "
        f"(kb.wear_spec_anchor thread|35CrMo-SCM435, Zhang2019) x "
        f"{_CONVENTION_FACTOR_2X} (2x vs 4x convencao) = {SEED_K_WEAR_FLANK:.4g} 1/Pa")

    attempt1 = run_attempt(1, free_exp=True, quick=quick, log=log)
    attempts = [attempt1]
    final = attempt1
    if attempt1["gate"]["verdict"] == "FAIL":
        log("\nAttempt 1 FALHOU o gate -- rodando Attempt 2 (fallback "
            f"PREREG, flank_amp_exp fixo em {EXP_FALLBACK}, Liu 2020).")
        attempt2 = run_attempt(2, free_exp=False, quick=quick, log=log)
        attempts.append(attempt2)
        final = attempt2

    if final["gate"]["verdict"] == "FAIL" and len(attempts) == 2:
        final_verdict = "FAIL2 (falsificacao documentada, sem forcar adocao)"
    else:
        final_verdict = final["gate"]["verdict"]

    out = dict(
        prereg=PREREG,
        pass_band_per_N=list(PASS_BAND_PER_N),
        seed=dict(anchor_1_per_Pa=SEED_K_WEAR_FLANK_ANCHOR,
                 convention_factor_2x=_CONVENTION_FACTOR_2X,
                 seed_used_1_per_Pa=SEED_K_WEAR_FLANK,
                 anchor_source="kb.wear_spec_anchor('thread','35CrMo-SCM435') "
                               "= Zhang 2019 EFA doi 10.1016/"
                               "j.engfailanal.2019.05.001"),
        provenance_notes=dict(
            liu17_rz=LIU17_BASE["prov_rz"], liu17_grip=LIU17_BASE["prov_grip"],
            liu16_rz=LIU16_BASE["prov_rz"], liu16_grip=LIU16_BASE["prov_grip"],
            liu16_r_bearing=LIU16_BASE["prov_rbearing"],
            li22_rz=LI22_BASE["prov_rz"], li22_grip=LI22_BASE["prov_grip"],
            excluded_curve="liu2016wear_fig7_run2_5e6cyc.csv: cauda "
                           "nao-monotonica (recovery ~N=2.2-4e6), flagrada "
                           "'out-of-model' no proprio apparatus_notes/"
                           "liu2016wear.md e validation_cases.py -- mesmo "
                           "tratamento dos rabos de fadiga (Yang2021 etc.)."),
        fit_method="busca em grade determinista 2 estagios (grosseiro+refino) "
                   "sobre log10(k_wear_flank) [e flank_amp_exp quando livre]; "
                   "custo fixo e conhecido a priori (ver docstring do modulo "
                   "para a justificativa vs scipy.least_squares).",
        fit_cycle_cap_rigA=FIT_CAP_RIGA,
        attempts=[{k: v for k, v in a.items()} for a in attempts],
        final=dict(attempt_used=final["attempt"],
                  free_exp=final["free_exp"],
                  verdict=final_verdict,
                  k_wear_flank_rigA=final["rigA"]["fitted"]["k_wear_flank"],
                  flank_amp_exp_rigA=final["rigA"]["fitted"]["flank_amp_exp"],
                  k_wear_flank_rigB=final["rigB"]["fitted"]["k_wear_flank"],
                  flank_amp_exp_rigB=final["rigB"]["fitted"]["flank_amp_exp"],
                  slope_liu2017_per_N=final["gate"]["slope_liu2017_per_N"],
                  slope_liu2016_per_N=final["rigA"]["liu2016_af_sweep_slope"]["model_per_N"],
                  seed_vs_fitted_ratio_rigA=(final["rigA"]["fitted"]["k_wear_flank"]
                                              / SEED_K_WEAR_FLANK),
                  seed_vs_fitted_ratio_rigB=(final["rigB"]["fitted"]["k_wear_flank"]
                                              / SEED_K_WEAR_FLANK),
                  no_regression_identical=final["no_regression"]["identical"],
                  dof_axial_free=(["k_wear_flank", "flank_amp_exp"]
                                  if final["free_exp"] else ["k_wear_flank"])),
        runtime_total_s=time.time() - t_start,
    )

    log(f"\n{'=' * 70}\nFINAL: attempt={out['final']['attempt_used']} "
        f"verdict={out['final']['verdict']} "
        f"slope_liu2017={out['final']['slope_liu2017_per_N']:.3e}/N\n"
        f"k_wear_flank RigA={out['final']['k_wear_flank_rigA']:.4g} "
        f"RigB={out['final']['k_wear_flank_rigB']:.4g}  "
        f"flank_amp_exp={out['final']['flank_amp_exp_rigA']:.4g}\n"
        f"total runtime: {out['runtime_total_s'] / 60:.1f} min\n{'=' * 70}")

    if quick:
        log("\n--quick: NAO gravando l1_axial_gate_result.json (smoke test).")
        return

    out_path = ROOT / "New_Theory" / "l1_axial_gate_result.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    log(f"JSON: {out_path}")


if __name__ == "__main__":
    main()
