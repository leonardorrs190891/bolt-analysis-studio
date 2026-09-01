# -*- coding: utf-8 -*-
"""Executor do prereg 2026-07-30-liu2016-fretting-flank (G1-G5).

Re-atribuicao da cauda: canal L1 de flanco (flank_wear_on=1, exp=1.5 KB,
k_wear_flank calibrado do B congelado) + trim de debris no fig7_run2
(2.2e6, feicao out-of-model documentada). Leitura CONGELADA: B=6.0e-8,
lam=0 (creep fica), q=1.5. UMA execucao, gates imutaveis.

Com --adotar e PASSA: escreve a config (entry LIU_2016 + per_case run2).
Re-carimbo do store e' do chamador.

Saida: New_Theory/liu2016_fretting_exec.json + prints ASCII.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.report_html as rh   # noqa: E402
import bolt_analysis_studio.validation.runner as rn        # noqa: E402
from bolt_analysis_studio.calibration.holdout import (      # noqa: E402
    HoldoutSplit, veredicto_generalizacao)
from bolt_analysis_studio.validation.case_registry import (  # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

B_FROZEN = 6.0e-8
Q_EXP = 1.5
K_SEED = 2.154434690031884e-13     # k_wear_flank do li2022ti (mesma familia)
CAL = "liu2016wear_fig7_run1_1e6cyc"
RUN2 = "liu2016wear_fig7_run2_5e6cyc"
TRIM_RUN2 = 2_200_000.0
MOS2 = "liu2016wear_fig13a_mos2"
PREV_SD = {
    "liu2016wear_fig9a_m30nm": 0.0230,
    "liu2016wear_fig7_run1_1e6cyc": 0.0229,
    "liu2016wear_fig9a_m40nm": 0.0225,
    "liu2016wear_fig7_run2_5e6cyc": 0.0194,   # na janela trimada
    "liu2016wear_fig9a_m35nm": 0.0165,
    "liu2016wear_fig9a_m45nm": 0.0144,
    "liu2016wear_fig9a_m50nm": 0.0132,
    "liu2016wear_fig11a_af7p5kn": 0.0091,
    "liu2016wear_fig11a_af8p75kn": 0.0082,
    "liu2016wear_fig11a_af10kn": 0.0103,
    "liu2016wear_fig11a_af11p25kn": 0.0115,
    "liu2016wear_fig11a_af12p5kn": 0.0148,
    "liu2016wear_fig13a_dry": 0.0182,
}
FILA = ["liu2016wear_fig9a_m30nm", "liu2016wear_fig9a_m40nm",
        "liu2016wear_fig7_run1_1e6cyc", "liu2016wear_fig7_run2_5e6cyc"]
HELD = ("liu2016wear_fig9a_m40nm", "liu2016wear_fig7_run2_5e6cyc")
TOL_G2, TOL_G4 = 0.005, 0.01

_EXTRA: dict = {}
_orig = rn._effective_overrides
rn._effective_overrides = lambda rec, base: {**_orig(rec, base), **_EXTRA}

# trim_n_max NAO passa pelos overrides — o runner le do cfg ADOTADO via
# kb.adopted_config (_trim_n_for). Para simular o trim do run2 sem escrever
# o arquivo, embrulhamos _trim_n_for (flag de processo, reversivel).
_TRIM_RUN2_ON = {"on": False}
_orig_trim = rn._trim_n_for


def _trim_wrap(source, case_id, bolt):
    if _TRIM_RUN2_ON["on"] and case_id == RUN2:
        return TRIM_RUN2
    return _orig_trim(source, case_id, bolt)


rn._trim_n_for = _trim_wrap


def _sim(cid, K):
    _EXTRA.clear()
    _EXTRA.update({"flank_wear_on": 1.0, "flank_amp_exp": Q_EXP,
                   "k_wear_flank": K})
    _TRIM_RUN2_ON["on"] = True
    try:
        return rn.simulate_case(record(cid))
    finally:
        _EXTRA.clear()
        _TRIM_RUN2_ON["on"] = False


def main() -> int:
    st = ValidationStore()

    # ---- G1: mapa linear B<->k_wear_flank em CAL ---------------------------
    base = st.get(CAL)
    xb = np.asarray(base.metric_x, float)
    pb = np.asarray(base.metric_pred, float)
    dt = np.asarray(base.metric_data, float)
    fax = float(base.to_dict()["config_used"]["F_amp_N"])
    H = np.concatenate([[0.0], np.cumsum(0.5 * (dt[1:] + dt[:-1])
                                         * np.diff(xb))])
    shape = (fax / 1e4) ** Q_EXP * H

    def _B_medido(res):
        d = pb - np.asarray(res.metric_pred, float)
        return float((d @ shape) / (shape @ shape))

    r1 = _sim(CAL, K_SEED)
    B1 = _B_medido(r1)
    K_lin = K_SEED * B_FROZEN / B1
    r2 = _sim(CAL, K_lin)
    B2 = _B_medido(r2)
    g1_ok = abs(B2 - B_FROZEN) <= 0.10 * B_FROZEN
    print(f"G1: K_seed={K_SEED:.3e} -> B1={B1:.3e}; K'={K_lin:.3e} -> "
          f"B2={B2:.3e} (alvo {B_FROZEN:.3e}) "
          f"{'ok' if g1_ok else 'FALHA -> INCONCLUSIVO'}")
    out = {"K_linha": K_lin, "G1": {"B1": B1, "B2": B2, "ok": g1_ok},
           "curvas": {}}
    if not g1_ok:
        _dump(out)
        return 1

    # ---- sims das 13 + controle mos2 ---------------------------------------
    antes_sd, depois_sd = {}, {}
    g2_falhas, g4_pioras = [], []
    for cid in PREV_SD:
        b = st.get(cid)
        # baseline de comparacao: run2 tem de ser comparado NA MESMA janela
        # (config atual + trim, SEM os campos de flanco)
        if cid == RUN2:
            _EXTRA.clear()
            _TRIM_RUN2_ON["on"] = True
            try:
                b = rn.simulate_case(record(cid))
            finally:
                _TRIM_RUN2_ON["on"] = False
        r = r2 if cid == CAL else _sim(cid, K_lin)
        antes_sd[cid] = b.resid_std
        depois_sd[cid] = r.resid_std
        d_g2 = abs(r.resid_std - PREV_SD[cid])
        if d_g2 > TOL_G2:
            g2_falhas.append((cid, PREV_SD[cid], round(r.resid_std, 4)))
        for rot, va, vb in (("mae", b.mae, r.mae), ("mx", b.maxerr, r.maxerr),
                            ("sd", b.resid_std, r.resid_std)):
            if vb > va + TOL_G4:
                g4_pioras.append((cid, rot, round(va, 4), round(vb, 4)))
        out["curvas"][cid] = {
            "antes": {"mae": b.mae, "mx": b.maxerr, "sd": b.resid_std},
            "depois": {"mae": r.mae, "mx": r.maxerr, "sd": r.resid_std},
            "sd_prev": PREV_SD[cid], "d_g2": d_g2}
        print(f"  {cid[:42]:42s} sd {b.resid_std:.4f}->{r.resid_std:.4f} "
              f"(prev {PREV_SD[cid]:.4f}, d={d_g2:.4f}) mae {r.mae:.4f} "
              f"mx {r.maxerr:.4f}")

    # controle mos2: config separada NAO muda => sim sem _EXTRA
    bm = st.get(MOS2)
    rm = rn.simulate_case(record(MOS2))
    d_mos2 = abs(rm.resid_std - bm.resid_std)
    print(f"  {MOS2[:42]:42s} controle dsd={d_mos2:.4f} (exigido <=0.001)")

    g2_ok = len(g2_falhas) <= 2
    g4_ok = (not g4_pioras) and d_mos2 <= 0.001
    split = HoldoutSplit(
        criterio="identidade do dado: replica-1a (run1) le / run2 segura; "
                 "menor nivel de torque (m30nm) le / m40nm segura",
        reads=(CAL, "liu2016wear_fig9a_m30nm"), held=HELD)
    g3 = veredicto_generalizacao(antes_sd, depois_sd, split, tol=TOL_G4)
    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    lim_sd = rh.limite_sres("LIU_2016", rh._pisos_medidos(pares))
    fecha = {cid: (out["curvas"][cid]["depois"]["sd"] <= lim_sd
                   and out["curvas"][cid]["depois"]["mae"] <= rh.META_MAE
                   and out["curvas"][cid]["depois"]["mx"] <= rh.META_MAX)
             for cid in PREV_SD}
    g5_ok = all(fecha[c] for c in FILA)
    out.update({"G2": {"ok": g2_ok, "falhas": g2_falhas},
                "G3": g3, "G4": {"ok": g4_ok, "pioras": g4_pioras,
                                 "d_mos2": d_mos2},
                "G5": {"ok": g5_ok, "lim_sd": lim_sd, "fecha": fecha}})
    passa = g1_ok and g2_ok and g3["generaliza"] and g4_ok and g5_ok
    out["PASSA"] = passa
    print(f"\nG2: {'ok' if g2_ok else 'FALHA'} ({len(g2_falhas)} fora)"
          f" | G3 generaliza: {g3['generaliza']} (held mediana "
          f"{g3['mediana_held_antes']:.4f}->{g3['mediana_held_depois']:.4f})"
          f" | G4: {'ok' if g4_ok else f'FALHA {g4_pioras}'}"
          f" | G5: {'ok' if g5_ok else 'FALHA'};"
          f" fecham {sum(fecha.values())}/13")
    print(f"\n{'PASSA' if passa else 'NAO PASSA'}")

    if passa and "--adotar" in sys.argv:
        cfgp = ROOT / "New_Theory" / "adopted_configs.json"
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        ent = cfg["sources"]["LIU_2016"]
        ent["cfg"]["flank_wear_on"] = 1.0
        ent["cfg"]["flank_amp_exp"] = Q_EXP
        ent["cfg"]["k_wear_flank"] = K_lin
        pc = ent["cfg"].setdefault("per_case", {})
        pc.setdefault("run2", {})["trim_n_max"] = TRIM_RUN2
        prov = ("re-atribuicao fretting L1: mecanismo dos AUTORES (SEM/EDX, "
                "cauda = fretting nos filetes, 'no creep language'); forma KB "
                "li2022ti/Liu2020 exp=1.5; B=6.0e-8 lido do residuo (L24), "
                "held-out 2 curvas generaliza; trim run2@2.2e6 por "
                "recuperacao de debris (Fig.7 inset, terceiro corpo, "
                "out-of-model documentado; publicar sempre as 2 janelas); "
                "prereg 2026-07-30-liu2016-fretting-flank gates 5/5; adotado "
                "por delegacao (mandato 2026-07-30)")
        for k in ("flank_wear_on", "flank_amp_exp", "k_wear_flank"):
            ent.setdefault("prov", {})[k] = prov
        ent["prov"]["per_case.run2.trim_n_max"] = prov
        cfgp.write_text(json.dumps(cfg, ensure_ascii=False, indent=1),
                        encoding="utf-8")
        print("ADOTADO — re-carimbar store INTEIRO + exemplo_m12_sintetico "
              "+ reports.")
    _dump(out)
    return 0 if passa else 1


def _dump(out):
    (ROOT / "New_Theory" / "liu2016_fretting_exec.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
