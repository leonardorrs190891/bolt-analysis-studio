# -*- coding: utf-8 -*-
"""D2' — discriminante do Cattaneo-Mindlin. Prereg 2026-07-30 (commit 92d4048).

SO-LEITURA: nada escrito no store nem em adopted_configs.json.

O D2 anterior foi retirado por falha de INSTRUMENTO: espionava
`partial_slip_gate`, que NAO e' chamado em 5 das 7 curvas que fecham o tripe. O
`slip_regime_mode="cattaneo_mindlin"` age em DOIS sitios:

  · partial_slip_gate   -> wear/fretting,   g = 1-(1-r)^m,  r = Q/(mu*F0*kappa)
  · loosening_slip_gate -> afrouxamento,    g = frac^k,     frac = max(0, 1-1/r)

Medicao do G4 (2026-07-30) fechou a identificacao: as 6 celulas de (kappa, m) dao
resultado IDENTICO (7 fecham, 0 pioram, soma de ganho +0,0458 igual ao digito) =>
kappa e m sao INERTES nesta fila, e o botao vivo e' `slip_regime_sharpness` (k),
do segundo sitio.

Tres testes (prereg §4):
  A ATRIBUICAO   — falsifica se alguma curva melhora com AMBOS os gates em g==1.
  B GATE CONGELADO (decisivo) — congela o gate na sua MEDIA temporal (mesma media,
    sem migracao). Se a melhora sobrevive, o CM e' RESCALA CONSTANTE de canal
    (alavanca de nivel disfarcada), nao bifurcacao. Comparacao INTRA-curva, imune
    ao defeito de spread que matou o D2.
  C ORDENACAO   — Delta_g = g(fim) - g(inicio), medido por curva. Guarda: <4
    valores distintos ou nan em >1/3 => INCONCLUSIVO, e NAO conta como falsificacao.

RE-EXECUCAO 2026-07-30 (pendencia do handoff: "re-rode o D2' com o teto
corrigido"). A 1a execucao estava CONTAMINADA por dois defeitos de regua:
  1. TETO DESIGUAL NAS DUAS PONTAS: sd0 vinha do STORE (simulacao completa,
     ate 5.000.000 de ciclos) e o lado CM rodava com n_cap=200_000 => em 10 das
     18 curvas o "ganho" misturava truncamento com mecanismo. Agora o baseline
     e' RE-SIMULADO no mesmo teto (N_CAP unico nas duas pontas) e o sd0 do
     store fica so como coluna de referencia (a contaminacao vira visivel).
  2. REGUA PRE-D1: `fecha` julgava por META_SRES global; desde a adocao do D1 o
     limite efetivo e' por fonte (rh.limite_sres) — mesma licao do e0d42ab.
Curva TRUNCADA (n_max > N_CAP) que fecha no teto ganha confirmacao FULL-LENGTH
em fase separada: "fecha" so' e' afirmado store-comparavel se fechar tambem sem
teto; senao e' reportado como fecha@cap, nunca somado ao merito.

    py -3.12 New_Theory/cm_discriminante_d2linha.py [--quick]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.numerical import dynamic_stiffness_analyzer as dsa   # noqa: E402
from bolt_analysis_studio.validation import report_html as rh                  # noqa: E402
from bolt_analysis_studio.validation import runner as rn                       # noqa: E402
from bolt_analysis_studio.validation.case_registry import record               # noqa: E402

PROBE_JSON = ROOT / "New_Theory" / "duas_formas_probe.json"
MELHORA = 0.002          # |Delta sigma| acima disto conta como movimento
SPREAD_MIN = 4           # valores distintos minimos p/ o teste C valer
# TETO UNICO nas duas pontas (o conserto): baseline e CM rodam AMBOS com este
# n_cap. O valor e' o mesmo 200k da 1a execucao — o defeito nunca foi o numero,
# foi o baseline vir do store (sem teto) enquanto o CM rodava com ele.
N_CAP = 200_000
_EXTRA: dict = {}
# trajetorias por sitio, na ordem das chamadas (1 por ciclo por mecanismo)
_G: dict[str, list[float]] = {"loose": [], "wear": []}
_CONGELA: dict[str, float] = {}     # sitio -> valor constante (controle B)


def _instalar() -> None:
    _o = rn._effective_overrides
    rn._effective_overrides = lambda rec, base: {**_o(rec, base), **_EXTRA}
    _lsg, _psg = dsa.loosening_slip_gate, dsa.partial_slip_gate

    def loose_spy(state, geom, mat, slip_amp):
        g = _lsg(state, geom, mat, slip_amp)
        if mat.slip_regime_mode == "cattaneo_mindlin":
            _G["loose"].append(float(g))
            if "loose" in _CONGELA:
                return _CONGELA["loose"]
        return g

    def wear_spy(state, geom, mat, F_amp, theta_load, channel, slip_amp):
        g = _psg(state, geom, mat, F_amp, theta_load, channel, slip_amp)
        if mat.slip_regime_mode == "cattaneo_mindlin":
            _G["wear"].append(float(g))
            if "wear" in _CONGELA:
                return _CONGELA["wear"]
        return g

    dsa.loosening_slip_gate = loose_spy
    dsa.partial_slip_gate = wear_spy


def rodar(cid: str, ov: dict | None, congela: dict | None = None,
          n_cap: int | None = N_CAP) -> dict:
    _EXTRA.clear()
    _CONGELA.clear()
    for k in _G:
        _G[k].clear()
    if ov:
        _EXTRA.update(ov)
    if congela:
        _CONGELA.update(congela)
    r = rn.simulate_case(record(cid), n_cap=n_cap)
    out = dict(mae=float(r.mae), mx=float(r.maxerr), sd=float(r.resid_std))
    for sitio, v in _G.items():
        a = np.array(v, float)
        out[sitio] = dict(
            n=len(a),
            g_ini=float(a[0]) if len(a) else float("nan"),
            g_fim=float(a[-1]) if len(a) else float("nan"),
            g_med=float(a.mean()) if len(a) else float("nan"),
            gated=bool(len(a) and float(a.min()) < 0.999))
    return out


def spearman(x, y) -> float:
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3:
        return float("nan")
    return float(np.corrcoef(np.argsort(np.argsort(x)).astype(float),
                             np.argsort(np.argsort(y)).astype(float))[0, 1])


def main() -> int:
    _instalar()
    dados = json.loads(PROBE_JSON.read_text(encoding="utf-8"))["bifurcacao de limiar"]
    if "--quick" in sys.argv:
        dados = dados[:6]
    CM = dict(slip_regime_mode="cattaneo_mindlin")   # kappa/m inertes (G4 medido)
    # limite EFETIVO por fonte (D1) — mesma licao do e0d42ab: rh.limite_sres,
    # nunca META_SRES cru
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.inputs import load_full_curve, repo_root
    from bolt_analysis_studio.validation.store import ValidationStore
    _st = ValidationStore()
    _pares = [(r.source, _st.get(r.case_id)) for r in all_records()
              if _st.get(r.case_id) is not None]
    _pisos = rh._pisos_medidos(_pares)

    def _lim(cid: str) -> float:
        return rh.limite_sres(record(cid).source, _pisos)

    def _nmax(cid: str) -> int:
        rec = record(cid)
        cx, _ = load_full_curve(rec.csv_path.relative_to(repo_root()).as_posix())
        return int(np.asarray(cx, float).max())

    print(f"D2' RE-EXECUCAO com teto unico (prereg 92d4048) · fila {len(dados)}")
    print(f"  N_CAP={N_CAP:,} nas DUAS pontas (baseline re-simulado; o sd0 do")
    print(f"  store fica so como referencia) · regua D1 (limite_sres por fonte)")
    print(f"  · movimento minimo {MELHORA}\n")
    print(f"  {'curva':30s} {'sd0store':>8s} {'sd0@cap':>8s} {'sd CM':>7s} "
          f"{'ganho':>8s} | {'sitio':>6s} {'dg':>6s} | {'congel':>7s} "
          f"{'fmigr':>6s} | trunc")
    linhas = []
    for l in dados:
        cid, sd0_store = l["case"], l["sd0"]
        truncada = _nmax(cid) > N_CAP
        base = rodar(cid, None)              # MESMO teto do lado CM
        sd0 = base["sd"]
        cm = rodar(cid, CM)
        ganho = sd0 - cm["sd"]
        # qual sitio AGE: o que foi chamado com g<1
        sitio = ("loose" if cm["loose"]["gated"] else
                 "wear" if cm["wear"]["gated"] else "nenhum")
        dg = (cm[sitio]["g_fim"] - cm[sitio]["g_ini"]) if sitio != "nenhum" \
            else float("nan")
        # --- Teste B: congela o gate do sitio que age na sua media temporal
        frac_migr = float("nan")
        sd_cong = float("nan")
        if sitio != "nenhum" and abs(ganho) > MELHORA:
            cong = rodar(cid, CM, congela={sitio: cm[sitio]["g_med"]})
            sd_cong = cong["sd"]
            g_cong = sd0 - sd_cong
            frac_migr = (ganho - g_cong) / ganho if abs(ganho) > 1e-12 else float("nan")
        linhas.append(dict(case=cid, sd0_store=sd0_store, sd0=sd0,
                           sd_cm=cm["sd"], ganho=ganho, truncada=truncada,
                           sitio=sitio, g_ini=cm[sitio]["g_ini"] if sitio != "nenhum"
                           else float("nan"),
                           g_fim=cm[sitio]["g_fim"] if sitio != "nenhum"
                           else float("nan"), dg=dg, sd_cong=sd_cong,
                           frac_migr=frac_migr,
                           mae=cm["mae"], mx=cm["mx"], lim_sd=_lim(cid),
                           fecha=bool(cm["mx"] <= rh.META_MAX and cm["mae"] <= rh.META_MAE
                                      and cm["sd"] <= _lim(cid))))
        print(f"  {cid[:30]:30s} {sd0_store:8.4f} {sd0:8.4f} {cm['sd']:7.4f} "
              f"{ganho:+8.4f} | {sitio:>6s} {dg:+6.3f} | {sd_cong:7.4f} "
              f"{frac_migr:6.2f} | {'SIM' if truncada else '-'}")

    # ---------------------------------------------------------------- Teste A
    viol_A = [l["case"] for l in linhas
              if abs(l["ganho"]) > MELHORA and l["sitio"] == "nenhum"]
    print(f"\n  A ATRIBUICAO: curvas que se movem com AMBOS os gates em g==1: "
          f"{len(viol_A)} {viol_A[:3]}")
    print(f"     {'FALSIFICA' if viol_A else 'ok'}")

    # ---------------------------------------------------------------- Teste B
    fr = np.array([l["frac_migr"] for l in linhas], float)
    fr = fr[np.isfinite(fr)]
    if len(fr):
        med = float(np.median(fr))
        ramoB = ("PASSA" if med >= 0.50 else
                 "PARCIAL" if med >= 0.25 else "NIVEL DISFARCADO")
        print(f"\n  B GATE CONGELADO: fracao do ganho que vem da MIGRACAO — "
              f"mediana {med:+.2f} (n={len(fr)})")
        print(f"     por curva: {', '.join(f'{x:+.2f}' for x in fr)}")
        print(f"     >>> {ramoB}  (>=0,50 passa · <0,25 e' rescala constante)")
    else:
        med, ramoB = float("nan"), "INCONCLUSIVO"
        print("\n  B GATE CONGELADO: nenhuma curva se moveu o suficiente -> "
              "INCONCLUSIVO")

    # ---------------------------------------------------------------- Teste C
    dgs = np.array([l["dg"] for l in linhas], float)
    gan = np.array([l["ganho"] for l in linhas], float)
    val = np.isfinite(dgs)
    distintos = len(set(np.round(dgs[val], 6)))
    frac_nan = 1.0 - val.mean()
    print(f"\n  C ORDENACAO: spread do preditor -> {distintos} valores distintos, "
          f"nan em {100*frac_nan:.0f}% da fila")
    if distintos < SPREAD_MIN or frac_nan > 1 / 3:
        ramoC = "INCONCLUSIVO"
        print(f"     >>> INCONCLUSIVO (guarda do prereg: <{SPREAD_MIN} distintos "
              "ou nan em >1/3). NAO conta como falsificacao.")
    else:
        rho = spearman(dgs[val], gan[val])
        inertes = [l["case"] for l in linhas
                   if np.isfinite(l["dg"]) and abs(l["dg"]) <= 0.02
                   and abs(l["ganho"]) > MELHORA]
        ramoC = ("PASSA" if (rho >= 0.50 and not inertes) else
                 "FALSIFICADO" if rho <= -0.30 or abs(rho) < 0.30 else "PARCIAL")
        print(f"     Spearman(dg, ganho) = {rho:+.3f} (passa >= +0,50) · "
              f"movem com dg<=0,02: {len(inertes)}")
        print(f"     >>> {ramoC}")

    # --------------- contaminacao da 1a execucao, agora VISIVEL --------------
    tr = [l for l in linhas if l["truncada"]]
    if tr:
        dmax = max(abs(l["sd0_store"] - l["sd0"]) for l in tr)
        print(f"\n  CONTAMINACAO (1a execucao): |sd0_store - sd0@cap| nas "
              f"{len(tr)} truncadas — max {dmax:.4f}")
        for l in sorted(tr, key=lambda z: -abs(z["sd0_store"] - z["sd0"]))[:5]:
            print(f"     {l['case'][:38]:40s} {l['sd0_store']:.4f} -> "
                  f"{l['sd0']:.4f}  ({l['sd0']-l['sd0_store']:+.4f})")

    # --------------- G1 com confirmacao FULL-LENGTH nas truncadas ------------
    n_fecha_cap = sum(1 for l in linhas if l["fecha"])
    confirmar = [l for l in linhas if l["fecha"] and l["truncada"]]
    print(f"\n  G1 fecham no teto: {n_fecha_cap} "
          f"({len(confirmar)} truncadas -> confirmacao full-length)")
    for l in confirmar:
        full = rodar(l["case"], CM, n_cap=None)
        l["fecha_full"] = bool(full["mx"] <= rh.META_MAX
                               and full["mae"] <= rh.META_MAE
                               and full["sd"] <= l["lim_sd"])
        l["sd_cm_full"] = full["sd"]
        print(f"     {l['case'][:38]:40s} sd@cap {l['sd_cm']:.4f} -> "
              f"full {full['sd']:.4f}  fecha_full={l['fecha_full']}")
    n_fecha = sum(1 for l in linhas
                  if l["fecha"] and l.get("fecha_full", True))
    print(f"  G1 STORE-COMPARAVEL (fecha no teto E no full quando truncada): "
          f"{n_fecha}")
    print(f"\n  VEREDICTO: A={'FALSIFICA' if viol_A else 'ok'} · B={ramoB} · C={ramoC}")
    dest = ROOT / "New_Theory" / "cm_discriminante_d2linha.json"
    dest.write_text(json.dumps(dict(meta=dict(n_cap=N_CAP,
                                              teto_unico=True, regua="D1",
                                              reexecucao="2026-07-30"),
                                    linhas=linhas, B_mediana=med, ramoB=ramoB,
                                    ramoC=ramoC, viol_A=viol_A,
                                    fecham_cap=n_fecha_cap, fecham=n_fecha),
                               ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  gravado: {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
