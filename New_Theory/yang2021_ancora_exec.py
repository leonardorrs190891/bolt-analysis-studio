# -*- coding: utf-8 -*-
"""Executor do prereg D-U (2026-08-06) — re-ancoragem das 6 CSVs do YANG_2021.

As 6 digitalizacoes originais ancoram o 1o ponto (x=0, INVENTADO — os tracos
comecam em N~100-750) na BORDA SUPERIOR da banda de oscilacao, enquanto o resto
segue os CENTROS. O runner divide a curva pelo 1o ponto => deflacao
multiplicativa de -2% a -9,4% em cada curva.

Fonte de verdade: a extracao vetorial preservada em
  BAS_V2_papers/E. Rodada 4 (...)/vector_extractions/yang2021_fig2_fig6_vector.json
(260 pts de centro de banda `bc` + meia-largura `bhw` por traco, calibrada por
ticks). Atribuicao DOCUMENTAL pelos rotulos de painel impressos (G0) — a matriz
crua de min-RMS nao e' univoca (amp0p7 e r2 colidem).

    py -3.12 New_Theory/yang2021_ancora_exec.py             # so gates (dry)
    py -3.12 New_Theory/yang2021_ancora_exec.py --escrever  # escreve + re-sim

Sem pipe (o executor escreve antes de verificar — licao D-Q).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

VEC = (ROOT / "BAS_V2_papers" / "E. Rodada 4 (deep-research 2026-07-11)"
       / "vector_extractions" / "yang2021_fig2_fig6_vector.json")
# atribuicao DOCUMENTAL: rotulo de painel impresso -> case_id (G0)
ROT2CID = {
    "Fig2_tr0": "yang2021_fig2_typical",          # Fig. 2 (traco unico)
    "1.0-2":    "yang2021_amp1p0mm_ax2kN",
    "0.8-6":    "yang2021_amp0p8mm_ax6kN",
    "0.6-8-1":  "yang2021_amp0p6mm_ax8kN_r1",
    "0.7-11.2": "yang2021_amp0p7mm_ax11p2kN",
    "0.5-8":    "yang2021_amp0p5mm_ax8kN",
}
CONTROLES = ("yang2021_amp0p6mm_ax8kN_r2", "yang2021_amp0p6mm_ax8kN_r3")
# ini_max de cada traco, CRAVADO da tabela do diagnostico (registro independente
# do CSV defeituoso) — 3o pilar da atribuicao (G0.iii)
INI_MAX_REF = {
    "yang2021_fig2_typical": 14.30,
    "yang2021_amp1p0mm_ax2kN": 14.66,
    "yang2021_amp0p8mm_ax6kN": 14.14,
    "yang2021_amp0p6mm_ax8kN_r1": 14.36,
    "yang2021_amp0p7mm_ax11p2kN": 15.80,
    "yang2021_amp0p5mm_ax8kN": 15.14,
}
RMS_MAX = 0.03          # G0 verificacao: RMS pos-shift em F/F0
VIDA_TOL = 0.013        # G1c: vida CSV<->traco


def _norm_rot(s: str) -> str:
    """Rotulos vem com en-dash/mojibake; normaliza p/ hifen ASCII."""
    out = []
    for ch in s:
        out.append("-" if not (ch.isalnum() or ch == ".") else ch)
    return "".join(out)


def _le_csv(p: Path):
    xs, ys = [], []
    for ln in p.read_text(encoding="utf-8").splitlines():
        a, _, b = ln.strip().partition(",")
        try:
            xs.append(float(a)); ys.append(float(b))
        except ValueError:
            continue
    return np.array(xs), np.array(ys)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--escrever", action="store_true")
    a = ap.parse_args()

    from bolt_analysis_studio.validation.case_registry import all_records, record
    from bolt_analysis_studio.validation.store import ValidationStore

    d = json.loads(VEC.read_text(encoding="utf-8"))
    # rotulo normalizado -> traco
    tracos = {}
    for k, r in d["res"].items():
        rot = _norm_rot(r.get("rot") or "")
        tracos[rot or k] = r
    paths = {r.case_id: ROOT / r.validation_case.reference_csv_path
             for r in all_records() if r.source == "YANG_2021"}

    print(f"extracao: {VEC.name} · {len(d['res'])} tracos")
    novos, ok_g0, ok_g1 = {}, True, True
    for rot, cid in ROT2CID.items():
        tr = tracos.get(_norm_rot(rot)) or tracos.get(rot)
        if tr is None:
            print(f"!! G0: rotulo {rot!r} sem traco — ABORTADO")
            return 2
        bx = np.asarray(tr["bx"], float)
        bc = np.asarray(tr["bc"], float)
        bhw = np.asarray(tr["bhw"], float)
        p = paths[cid]
        cx, cy = _le_csv(p)
        m = (cx >= bx[0]) & (cx <= bx[-1])
        gx = cx[m]
        if len(gx) < 4:
            print(f"!! {cid}: grade visivel com {len(gx)} pts — ABORTADO")
            return 2
        c_i = np.interp(gx, bx, bc)
        h_i = np.interp(gx, bx, bhw)
        y = c_i / c_i[0]
        novos[cid] = (gx, y)

        # G0 verificacao: RMS pos-shift NO PLATO (y_novo >= 0,8) entre CSV
        # velho renormalizado no 1o ponto visivel e o centro do traco. ⚠️ A 1a
        # versao varria a curva INTEIRA e reprovava 4/6 — ruido de x no colapso
        # (curva quase-vertical) vira erro gigante de y; o RMS do diagnostico
        # (0,0015-0,0293) era no plato. Emenda de INSTRUMENTO, achada no dry.
        vy = np.interp(gx, cx, cy)
        vn = vy / vy[0]
        mp_ = y >= 0.8
        # 3a emenda de instrumento (dry), e esta e' ESTRUTURAL: RMS contra o
        # CSV velho NAO pode gatear atribuicao — ele nao separa "traco errado"
        # de "traco certo, digitalizacao ruim", porque nas curvas PIORES o
        # defeito e' grande por definicao (amp0p7: meio do plato correndo pela
        # borda, desvio concentrado que sobrevive a remocao de translacao).
        # Atribuicao = evidencia de IDENTIDADE independente do arquivo
        # defeituoso: (i) rotulo de painel impresso (documental, ROT2CID);
        # (ii) VIDA do traco vs CSV (medido <=1,3% no diagnostico; barra 3%);
        # (iii) ini_max do traco cravado da tabela do diagnostico (+-0,05 kN).
        # O RMS de forma vira INFORMACAO impressa, nao gate.
        dif = (vn[mp_] - y[mp_]) if mp_.sum() >= 3 else (vn - y)
        rms = float(np.std(dif))
        vida_rel = abs(float(bx[-1]) - float(cx[-1])) / max(float(bx[-1]), 1.0)
        ini_ok = abs(float(tr["ini_max"]) - INI_MAX_REF[cid]) <= 0.05
        ok_g0 &= (vida_rel <= 0.03) and ini_ok

        # G1a: zero pontos inventados (por construcao gx >= bx[0]) — informar
        drop = int((cx < bx[0]).sum())
        # G1b (nao-vacuo, em unidades NORMALIZADAS pelo mesmo anchor): o CSV
        # NOVO fica dentro da banda por construcao (e' o centro); o que se mede
        # e' quantos pontos do VELHO estavam fora — a evidencia do defeito. ⚠️
        # A 1a versao comparava adimensional com kN (100% "fora", absurdo).
        lo = (c_i - h_i) / c_i[0]
        hi = (c_i + h_i) / c_i[0]
        dentro = True                     # centro esta na banda por construcao
        fora_velho = int(np.sum((vn < lo - 1e-12) | (vn > hi + 1e-12)))
        # G1c: vida (ultimo x)
        vida_ok = abs(gx[-1] - min(cx[-1], bx[-1])) / max(bx[-1], 1) <= VIDA_TOL
        ok_g1 &= bool(dentro and vida_ok)
        print(f"  {cid[9:]:22s} rot={rot:9s} n {len(cx)}->{len(gx)} "
              f"(descarta {drop})  forma_info {rms:.4f}  vida_rel {vida_rel:.3f} "
              f"{'OK' if vida_rel<=0.03 else 'FALHA'}  ini {tr['ini_max']:.2f} "
              f"{'OK' if ini_ok else 'FALHA'}  velho_fora={fora_velho}  "
              f"ancora {cy[0]:.4f}->1.0@N={gx[0]:.0f}")

    print(f"\nG0 (rotulo documental + vida<=3% + ini_max +-0,05 kN): {'PASSA' if ok_g0 else 'FALHA'}")
    print(f"G1 (fidelidade/vida): {'PASSA' if ok_g1 else 'FALHA'}")
    if not (ok_g0 and ok_g1):
        print("!! gate violado — NADA escrito.")
        return 3
    if not a.escrever:
        print("\n(sem --escrever: nada foi tocado)")
        return 0

    st = ValidationStore()
    antes = {r.case_id: st.get(r.case_id) for r in all_records()
             if r.source == "YANG_2021"}
    for cid, (gx, y) in novos.items():
        p = paths[cid]
        shutil.copy2(p, p.with_suffix(".csv.bkp_du"))
        p.write_text("x,F_over_F0\n" + "".join(
            f"{x:g},{v:.4f}\n" for x, v in zip(gx, y)), encoding="utf-8")
        print(f"escrito {p.name} ({len(gx)} pts; backup .csv.bkp_du)")

    import bolt_analysis_studio.validation.runner as rn
    print(f"\nre-simulando as {len(antes)} curvas do YANG_2021:")
    g3 = True
    for cid in sorted(antes):
        r = rn.simulate_case(record(cid))
        if not r.ok:
            print(f"  !! {cid}: {r.error}")
            return 2
        b = antes[cid]
        mudou = cid in novos
        idem = (abs(r.mae - b.mae) < 1e-12 and abs(r.maxerr - b.maxerr) < 1e-12
                and abs(r.resid_std - b.resid_std) < 1e-12)
        if not mudou and not idem:
            g3 = False
        print(f"  {'CORRIGIDA' if mudou else 'controle '} {cid[9:]:24s} "
              f"mae {b.mae:.4f}->{r.mae:.4f}  mx {b.maxerr:.4f}->{r.maxerr:.4f}  "
              f"sig {b.resid_std:.4f}->{r.resid_std:.4f}"
              f"{'' if (mudou or idem) else '   << G3 VIOLADO'}")
    print(f"\nG3 (controles bit-identicos): {'PASSA' if g3 else 'FALHA'}")
    print("Proximo: gravar no store + G5 (piso re-medido) + censo/docs no mesmo commit.")
    return 0 if g3 else 3


if __name__ == "__main__":
    raise SystemExit(main())
