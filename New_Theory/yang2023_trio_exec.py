# -*- coding: utf-8 -*-
"""EXECUCAO do prereg do TRIO
specs/2026-07-30-yang2023ijpem-trio-prereg.md

G1 CONGELA:
    delta_free = 122.96 / 129.18 um     (m6 / m8)
    loose_arrest_floor = 0.1025
    slip_onset_W = 12.45 J              (slip_onset_sharpness = default 4)

O PAR (mesma coisa com slip_onset_W = 0) e' recomputado NA MESMA CORRIDA, para
G2/G5 compararem coisas iguais em vez de numeros copiados.
Canonico e store NAO tocados. Prints ASCII.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import bolt_analysis_studio.validation.report_html as R  # noqa: E402
import bolt_analysis_studio.validation.runner as RN  # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

FONTE = "YANG_2023_IJPEM"
# ---- G1 ------------------------------------------------------------------
DF = {11000: 122.96e-6, 14300: 129.18e-6}
PISO = 0.1025
W_ONSET = 12.45
SUB = (0.15, 0.18)
TRANSICAO = 0.25
SATURADAS = (0.30, 0.35, 0.45, 0.50, 0.55, 0.65)
HELD_OUT = (0.50, 0.55, 0.65)      # joelho nao resolvido: nao leram o W
ALVO_G4_035 = 0.1788               # MAE baseline do 0,35


def _f0(rec):
    return int(round(float(rec.validation_case.initial_preload_N)))


def casos():
    return {round(float(RN._loading_for(r)["delta_mm"]), 3): r
            for r in all_records() if r.source == FONTE}


def sim(rec, w_onset):
    orig = RN._effective_overrides

    def patched(r, consts):
        d = dict(orig(r, consts))
        if r.source == FONTE:
            d["delta_free"] = DF[_f0(r)]
            d["loose_arrest_floor"] = PISO
            d["slip_onset_W"] = float(w_onset)
        return d
    RN._effective_overrides = patched
    try:
        return RN.simulate_case(rec)
    finally:
        RN._effective_overrides = orig


def mu_estagio_I(res):
    x = np.asarray(res.metric_x, float)
    rr = np.asarray(res.metric_pred, float) - np.asarray(res.metric_data, float)
    if not len(x) or x.max() <= 0:
        return float("nan")
    m = (x / x.max()) <= 0.10
    return float(rr[m].mean()) if m.sum() else float("nan")


def main() -> int:
    st = ValidationStore()
    cs = casos()
    falhas = []
    par = {a: sim(cs[a], 0.0) for a in sorted(cs)}       # W=0 => o PAR
    trio = {a: sim(cs[a], W_ONSET) for a in sorted(cs)}

    print("=" * 80)
    print("G3 (sub-critico bit-identico) · G4 (0,35 <= 0,1788; nada +0,01; 0,25 isenta)")
    print("=" * 80)
    print(f"{'amp':>5} {'MAE base->par->trio':>28} {'res.max base->par->trio':>30}")
    g3 = g4 = True
    for a in sorted(cs):
        b, p, t = st.get(cs[a].case_id), par[a], trio[a]
        marca = ""
        if a in SUB:
            if not (b.mae == t.mae and b.maxerr == t.maxerr
                    and b.resid_std == t.resid_std):
                g3 = False
                marca = "  <<< G3/F1 REPROVA"
            else:
                marca = "  [bit-identico]"
        elif a == TRANSICAO:
            marca = "  [isenta do G4]"
        else:
            pior = [n for n, va, vb in (("MAE", b.mae, t.mae),
                                        ("max", b.maxerr, t.maxerr),
                                        ("sd", b.resid_std, t.resid_std))
                    if va is not None and vb is not None and vb > va + 0.01]
            if pior:
                g4 = False
                marca = f"  <<< G4 ({','.join(pior)})"
        print(f"{a:5.2f} {b.mae:8.4f}->{p.mae:7.4f}->{t.mae:7.4f} "
              f"   {b.maxerr:8.4f}->{p.maxerr:7.4f}->{t.maxerr:7.4f}{marca}")
    mae035 = trio[0.35].mae
    ok035 = mae035 <= ALVO_G4_035
    if not ok035:
        g4 = False
    print(f"\n  0,35 mm MAE {mae035:.4f} vs alvo <= {ALVO_G4_035:.4f}: "
          f"{'ok' if ok035 else 'REPROVA'}")
    print(f"  G3 {'PASSA' if g3 else 'REPROVA'}   G4 {'PASSA' if g4 else 'REPROVA'}")
    if not g3:
        falhas.append("G3")
    if not g4:
        falhas.append("G4")

    print("\n" + "=" * 80)
    print("G2 — mediana do res.max das 6 saturadas <= 0,2928 (o que o par entregou)")
    print("=" * 80)
    mp = float(np.median([par[a].maxerr for a in SATURADAS]))
    mt = float(np.median([trio[a].maxerr for a in SATURADAS]))
    for a in SATURADAS:
        print(f"  {a:4.2f}  par {par[a].maxerr:.4f} -> trio {trio[a].maxerr:.4f}"
              f"  ({trio[a].maxerr-par[a].maxerr:+.4f})")
    print(f"\n  mediana par {mp:.4f} -> trio {mt:.4f}")
    g2 = mt <= mp + 1e-9
    print(f"  G2 {'PASSA' if g2 else 'REPROVA (F3: a incubacao custa o ganho do par)'}")
    if not g2:
        falhas.append("G2")

    print("\n" + "=" * 80)
    print("G5 — a incubacao consertou o ESTAGIO I do 0,35 mm?")
    print("=" * 80)
    mi_p, mi_t = mu_estagio_I(par[0.35]), mu_estagio_I(trio[0.35])
    print(f"  mu(estagio I) do 0,35:  par {mi_p:+.4f}  ->  trio {mi_t:+.4f}")
    g5 = abs(mi_t) < abs(mi_p)
    print(f"  |mu| caiu? {'sim' if g5 else 'NAO'}")
    print(f"  G5 {'PASSA' if g5 else 'REPROVA (F2: melhorou por compensacao)'}")
    if not g5:
        falhas.append("G5")

    print("\n" + "=" * 80)
    print("F4' — canal rotacional <= F0*(1-piso) nas 9")
    print("=" * 80)
    f4 = True
    for a in sorted(cs):
        F0 = float(cs[a].validation_case.initial_preload_N) / 1e3
        teto = F0 * (1.0 - PISO)
        v = (trio[a].decomp or {}).get("rotational_loosening")
        drenado = abs(float(np.asarray(v, float)[-1])) if v is not None else 0.0
        ok = drenado <= teto * 1.01
        if not ok:
            f4 = False
        print(f"  {a:4.2f}  canal {drenado:7.4f} kN  teto {teto:7.4f} kN  "
              f"{'ok' if ok else 'FALSIFICA <<<'}")
    print(f"  F4' {'ok' if f4 else 'FALSIFICA'}")
    if not f4:
        falhas.append("F4'")

    print("\n" + "=" * 80)
    print("G6 (info) — as 3 HELD-OUT (nao leram o W)")
    print("=" * 80)
    piora = 0
    for a in HELD_OUT:
        dm = trio[a].mae - par[a].mae
        dx = trio[a].maxerr - par[a].maxerr
        if dm > 0.01 or dx > 0.01:
            piora += 1
        print(f"  {a:4.2f}  MAE {par[a].mae:.4f}->{trio[a].mae:.4f} ({dm:+.4f})"
              f"   res.max {par[a].maxerr:.4f}->{trio[a].maxerr:.4f} ({dx:+.4f})")
    print(f"  held-out que pioram >0,01: {piora} de 3"
          f"   {'(F5: W unico nao e lei)' if piora >= 2 else ''}")

    print("\n" + "=" * 80)
    print("G7 — resto do store bit-identico")
    print("=" * 80)
    g7 = True
    recs = {r.case_id: r for r in all_records()}
    for cid in ("liu2016wear_fig9a_m30nm", "zhang18_fig13_14kN_preload_vs_cycles",
                "eccles2010_fig7c_axial_2p7kN_constant", "karlsen2022_M30_HV_run6p2"):
        r = recs.get(cid)
        if r is None:
            continue
        b, n = st.get(cid), sim(r, W_ONSET)
        ident = (b.mae == n.mae and b.maxerr == n.maxerr
                 and b.resid_std == n.resid_std)
        g7 = g7 and ident
        print(f"  {cid[:46]:48} {'bit-identico' if ident else 'MUDOU <<<'}")
    print(f"  G7 {'PASSA' if g7 else 'REPROVA'}")
    if not g7:
        falhas.append("G7")

    print("\n" + "=" * 80)
    print("RESUMO: " + ("TODOS OS GATES BLOQUEANTES PASSAM" if not falhas
                        else "REPROVA em " + ", ".join(falhas)))
    print("=" * 80)
    return 0 if not falhas else 1


if __name__ == "__main__":
    raise SystemExit(main())
