# -*- coding: utf-8 -*-
"""Sonda das DUAS formas restantes da classe "taxa dependente do estado acumulado".

Prereg 2026-07-30 (commit 4086ca9). SO-LEITURA: nada escrito no store nem em
adopted_configs.json.

  · kernel desacelerante = creep_mode="saturating" + creep_t_c
  · bifurcacao de limiar = slip_regime_mode="cattaneo_mindlin" + slip_capacity_coeff

Populacao: as 18 curvas FORM-LIMITED da triagem (regra_de_parada_triagem.py), nao
as 98 -- 44 daquelas sao excecao assinada e 21 sao metric/data-limited.

Cada candidato e' julgado pelo DISCRIMINANTE do prereg, nao por "a metrica melhorou":

  D1: a melhora tem de se concentrar onde (canal de creep >= 5%) E (residuo tardio
      NEGATIVO), e ser inerte onde o creep ~ 0. O creep saturante perde MENOS tarde,
      entao so pode ajudar quem esta' perdendo demais tarde.
  D2: a melhora tem de ORDENAR pela proximidade do limiar r = F_amp/cap (1o ciclo).
      Longe do limiar (gross slip profundo) tem de ser inerte.

    py -3.12 New_Theory/duas_formas_probe.py [--quick]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.numerical import dynamic_stiffness_analyzer as dsa    # noqa: E402
from bolt_analysis_studio.validation import report_html as rh                  # noqa: E402
from bolt_analysis_studio.validation import runner as rn                       # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records, record  # noqa: E402
from bolt_analysis_studio.validation.runner import CaseResult                  # noqa: E402

STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
MEC = ("embedding", "creep", "wear", "rotational_loosening",
       "thread_fretting", "fatigue")
INERTE = 0.002            # |Delta sigma| abaixo disto = inerte (prereg §3)
_EXTRA: dict = {}


def _ganchos() -> None:
    _o = rn._effective_overrides
    rn._effective_overrides = lambda rec, base: {**_o(rec, base), **_EXTRA}


def fila_form_limited(store: dict) -> list[str]:
    """As 18 da triagem — reusa os MESMOS criterios, nao uma lista fixa."""
    recs = {r.case_id: r for r in all_records()}
    pares = [(recs[c].source, CaseResult.from_dict(store[c]))
             for c in store if c in recs]
    fam = rh._pisos_medidos(pares)["fam"]
    piso: dict[str, list[float]] = {}
    for f in fam:
        piso.setdefault((f[0] or "").split()[0], []).append(f[4])
    piso = {k: float(np.median(v)) for k, v in piso.items()}
    exc = set(rh._EXCECOES)
    out = []
    for cid, r in store.items():
        if not r.get("ok") or cid not in recs or r.get("resid_std") is None:
            continue
        if (r["maxerr"] <= rh.META_MAX and r["mae"] <= rh.META_MAE
                and r["resid_std"] <= rh.META_SRES):
            continue
        if cid in exc:
            continue
        mp = np.asarray(r.get("metric_pred") or [], float)
        md = np.asarray(r.get("metric_data") or [], float)
        if len(mp) < 6:
            continue
        if len(md) > 2 and float(np.max(np.abs(np.diff(md)))) > 0.25:
            continue
        p = piso.get(recs[cid].source)
        if p is None or p > rh.META_SRES:
            continue
        out.append(cid)
    return sorted(out)


def contexto(store: dict, cid: str) -> dict:
    """Os dois preditores dos discriminantes, lidos do STORE (nao re-simulados)."""
    r = store[cid]
    dec = r.get("decomp") or {}
    fin = {m: float((dec.get(m) or [0.0])[-1]) for m in MEC}
    tot = sum(abs(v) for v in fin.values()) or 1e-12
    mp = np.asarray(r["metric_pred"], float)
    md = np.asarray(r["metric_data"], float)
    e = mp - md
    t = max(len(e) // 3, 1)
    return dict(creep_frac=abs(fin["creep"]) / tot,
                e_late=float(np.mean(e[-t:])),
                sd0=float(r["resid_std"]), mae0=float(r["mae"]),
                mx0=float(r["maxerr"]))


_R_ESPIAO: list[float] = []


def _instrumentar_limiar() -> None:
    """Espiao em `partial_slip_gate`: grava o r = Q/cap que o ENGINE calcula.

    A 1a versao do preditor do D2 re-derivava `r = F_amp/(mu*F0)` do
    ValidationCase e devolveu **nan nas 18 curvas da fila** (rigs de
    deslocamento tem `transverse_force_N = 0`), o que zerou o n do
    discriminante e fez o script declarar FALSIFICADO por falha de
    INSTRUMENTO. Ler do engine e' a mesma disciplina do espiao do `sun_life`:
    o valor medido e' o que a lei usa, nao o que eu suponho que ela use.
    """
    _psg = dsa.partial_slip_gate

    def espiao(state, geom, mat, F_amp, theta_load, channel, slip_amp):
        if mat.slip_regime_mode == "cattaneo_mindlin":
            F0 = max(state.F_0, 0.0)
            if F0 > 0.0:
                Q = abs(F_amp * (np.cos(theta_load) if channel == "fret"
                                 else np.sin(theta_load)))
                mu = (mat.mu_thread if channel == "fret"
                      else dsa.mu_bearing_eff(state, mat))
                cap = mu * F0 * max(mat.slip_capacity_coeff, 1e-9)
                if cap > 0.0:
                    _R_ESPIAO.append(float(Q / cap))
        return _psg(state, geom, mat, F_amp, theta_load, channel, slip_amp)

    dsa.partial_slip_gate = espiao


def medir(cid: str, ov: dict | None) -> dict:
    """Uma corrida. Devolve as 3 pernas + o r LIDO do engine (nan se a lei CM
    nao estiver ativa nesta celula)."""
    _EXTRA.clear()
    _R_ESPIAO.clear()
    if ov:
        _EXTRA.update(ov)
    r = rn.simulate_case(record(cid), n_cap=200_000)
    rs = np.array(_R_ESPIAO, float)
    return dict(mae=float(r.mae), mx=float(r.maxerr), sd=float(r.resid_std),
                r_ini=float(rs[0]) if len(rs) else float("nan"),
                r_max=float(rs.max()) if len(rs) else float("nan"),
                cruza=bool(len(rs) and rs.min() < 1.0 <= rs.max()))


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3:
        return float("nan")
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def main() -> int:
    _ganchos()
    _instrumentar_limiar()
    store = json.loads(STORE.read_text(encoding="utf-8"))
    fila = fila_form_limited(store)
    if "--quick" in sys.argv:
        fila = fila[:5]
    print(f"SONDA DAS DUAS FORMAS RESTANTES (prereg 4086ca9) · fila {len(fila)}")
    print(f"  regua: res.max<={rh.META_MAX} MAE<={rh.META_MAE} sigma<={rh.META_SRES}\n")

    GRADES = {
        "kernel desacelerante": [
            dict(creep_mode="saturating", creep_t_c=tc, creep_alpha_sat=a)
            for tc in (1e2, 1e4, 1e6) for a in (0.5, 1.0)],
        "bifurcacao de limiar": [
            dict(slip_regime_mode="cattaneo_mindlin", slip_capacity_coeff=k,
                 partial_slip_exp=p)
            for k in (0.5, 1.0, 2.0) for p in (1.5, 3.0)],
    }
    saida: dict = {}
    for nome, grade in GRADES.items():
        print(f"=== {nome} ===")
        print(f"  {'curva':30s} {'creep%':>6s} {'e_late':>7s} {'r':>6s} "
              f"{'sd0':>7s} {'sd melhor':>9s} {'ganho':>7s} {'fecha':>5s}")
        linhas = []
        for cid in fila:
            ctx = contexto(store, cid)
            cels = [medir(cid, ov) for ov in grade]
            # r LIDO do engine: a celula com kappa=1 e' a referencia do prereg
            # (cap = mu*F0*kappa). Sem a lei CM ativa nao ha r — fica nan, e o
            # D2 declara n=0 em vez de fingir um numero.
            rs = [c["r_ini"] for c in cels if c["r_ini"] == c["r_ini"]]
            r_lim = float(np.median(rs)) if rs else float("nan")
            cruza = any(c["cruza"] for c in cels)
            mel = min(cels, key=lambda d: d["sd"])
            fecha = any(c["mx"] <= rh.META_MAX and c["mae"] <= rh.META_MAE
                        and c["sd"] <= rh.META_SRES for c in cels)
            pior = max(max(c["mae"] - ctx["mae0"], c["mx"] - ctx["mx0"],
                           c["sd"] - ctx["sd0"]) for c in cels)
            ganho = ctx["sd0"] - mel["sd"]
            linhas.append(dict(case=cid, **ctx, r=r_lim, cruza=cruza,
                               sd_melhor=mel["sd"], ganho=ganho,
                               fecha=bool(fecha), pior_delta=pior))
            print(f"  {cid[:30]:30s} {100*ctx['creep_frac']:5.1f}% "
                  f"{ctx['e_late']:+7.4f} {r_lim:6.2f}{'*' if cruza else ' '} "
                  f"{ctx['sd0']:7.4f} {mel['sd']:9.4f} {ganho:+7.4f} "
                  f"{'SIM' if fecha else '':>5s}")
        saida[nome] = linhas

        # --- discriminante do prereg
        g = np.array([l["ganho"] for l in linhas])
        if nome.startswith("kernel"):
            alvo = np.array([(l["creep_frac"] >= 0.05 and l["e_late"] < 0)
                             for l in linhas])
            sem_creep = np.array([l["creep_frac"] < 0.05 for l in linhas])
            m_alvo = float(np.mean(g[alvo])) if alvo.any() else float("nan")
            m_resto = float(np.mean(g[~alvo])) if (~alvo).any() else float("nan")
            dif_pp = 100 * (m_alvo - m_resto)
            inerte_ok = bool(np.all(np.abs(g[sem_creep]) <= INERTE)) \
                if sem_creep.any() else True
            print(f"\n  D1: alvo (creep>=5% E e_late<0) n={int(alvo.sum())} "
                  f"ganho medio {m_alvo:+.4f} · resto {m_resto:+.4f} "
                  f"· diferenca {dif_pp:+.2f} pp")
            print(f"      inerte onde creep<5% (n={int(sem_creep.sum())}): "
                  f"{'SIM' if inerte_ok else 'NAO'}")
            ok = (dif_pp >= 15.0) and inerte_ok
        else:
            r = np.array([l["r"] for l in linhas], float)
            val = np.isfinite(r) & (r > 0)
            rho = spearman(np.abs(np.log(r[val])), g[val])
            longe = val & (r > 5)
            inerte_ok = bool(np.all(np.abs(g[longe]) <= INERTE)) \
                if longe.any() else True
            print(f"\n  D2: Spearman(|log r|, ganho) = {rho:+.3f} "
                  f"(passa se <= -0,50) · n={int(val.sum())}")
            print(f"      inerte em r>5 (n={int(longe.sum())}): "
                  f"{'SIM' if inerte_ok else 'NAO'}")
            ok = (rho <= -0.50) and inerte_ok
        fecha_n = sum(1 for l in linhas if l["fecha"])
        piora = [l["case"] for l in linhas if l["pior_delta"] > 0.01]
        print(f"      G1 curvas que fecham o tripe: {fecha_n}")
        print(f"      G2 pioram >+0,01: {len(piora)} {piora[:3]}")
        ramo = ("PASSA" if (ok and fecha_n >= 1) else
                "COMPONENTE" if ok else
                "INERTE" if float(np.max(np.abs(g))) <= INERTE else
                "FALSIFICADO")
        print(f"      >>> RAMO: {ramo}   (discriminante "
              f"{'acertado' if ok else 'ERRADO'})\n")
        saida[nome + "__veredicto"] = dict(discriminante_ok=bool(ok),
                                           fecha=fecha_n, piora=piora, ramo=ramo)
    dest = ROOT / "New_Theory" / "duas_formas_probe.json"
    dest.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"gravado: {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
