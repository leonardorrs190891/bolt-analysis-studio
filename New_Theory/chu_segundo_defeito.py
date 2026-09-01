# -*- coding: utf-8 -*-
"""Decomposicao algebrica do residuo: rampa + curvatura + resto (atividade F).

Responde "o que sobra sob a rampa" SEM usar alavanca nenhuma. A rota por alavanca
e' impossivel (medido 2026-07-29): a celula do `graded_scrit` que zera o beta
triplica o MAE, entao o residuo dela e' estrutura da alavanca, nao do modelo.

O residuo `e = pred - dado` e' projetado sobre polinomios do ciclo normalizado
`s in [0,1]`:

    grau 1 -> rampa      (deriva: termo monotono faltando)
    grau 2 -> curvatura  (joelho no lugar errado)
    resto  -> o que nenhuma forma lisa explica

O sigma de cada etapa e' corrigido por graus de liberdade — `sqrt(SS/(n-p))` — sem
o que uma quadratica sobre n=7 (3 dos 7 pontos) sai ~22% viesada para baixo e
"passa" a perna por construcao.

Le do store; NAO simula e NAO escreve nada alem do proprio JSON de saida.

    py -3.12 New_Theory/chu_segundo_defeito.py [--json saida.json]
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation import report_html as rh  # noqa: E402

STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
SAIDA = ROOT / "New_Theory" / "chu_segundo_defeito.json"
R2_DERIVA = 0.70          # o limiar de classe da atividade A
N_MIN = 6                 # sigma_res com menos que isto nao e' julgavel (gate, guarda 5)


def decompor(rec: dict) -> dict | None:
    """Projeta o residuo em rampa e curvatura; devolve sigmas corrigidos por DOF."""
    mp, md, mx = (np.asarray(rec.get(k) or [], float)
                  for k in ("metric_pred", "metric_data", "metric_x"))
    if len(mp) < N_MIN or len(mp) != len(md) or len(mp) != len(mx):
        return None
    e = mp - md
    span = (mx[-1] - mx[0]) or 1.0
    s = (mx - mx[0]) / span
    n = len(e)
    tot = float(np.sum((e - e.mean()) ** 2)) or 1e-18

    def ss(grau: int) -> float:
        return float(np.sum((e - np.polyval(np.polyfit(s, e, grau), s)) ** 2))

    quad = np.polyfit(s, e, 2)
    t = n // 3 or 1
    return dict(
        n=n, sd=float(np.std(e)), e=e.tolist(), s=s.tolist(),
        beta=float(np.polyfit(s, e, 1)[0]),
        curvatura=float(quad[0]),
        # ordem: 'joelho adiantado' = residuo em U = modelo cai cedo demais
        joelho="adiantado" if quad[0] > 0 else "atrasado",
        R2_lin=max(1.0 - ss(1) / tot, 0.0),
        R2_quad=max(1.0 - ss(2) / tot, 0.0),
        sd_lin=float(np.sqrt(ss(1) / max(n - 2, 1))),
        sd_quad=float(np.sqrt(ss(2) / max(n - 3, 1))),
        tercos=[float(np.mean(e[:t])), float(np.mean(e[t:2 * t])), float(np.mean(e[2 * t:]))],
    )


def main() -> int:
    store = json.loads(STORE.read_text(encoding="utf-8"))
    alvo = []
    for cid, rec in store.items():
        if not rec.get("ok"):
            continue
        d = decompor(rec)
        if d and d["sd"] > rh.META_SRES and d["R2_lin"] >= R2_DERIVA:
            alvo.append(dict(d, case=cid))
    alvo.sort(key=lambda d: -d["sd"])

    print("DECOMPOSICAO DO RESIDUO — rampa + curvatura + resto")
    print(f"  store: {next(iter(store.values())).get('engine_fingerprint')} · "
          f"limite da 3a perna: {rh.META_SRES}")
    print(f"  cluster DERIVA (sigma > limite e R2_lin >= {R2_DERIVA}): {len(alvo)} curvas\n")
    print(f"  {'curva':38s} {'n':>3s} {'sigma':>7s} {'-rampa':>7s} {'-curv':>7s} "
          f"{'xlim':>5s} {'curv':>6s} {'joelho':>9s}")
    for d in alvo:
        print(f"  {d['case'][:38]:38s} {d['n']:3d} {d['sd']:7.4f} {d['sd_lin']:7.4f} "
              f"{d['sd_quad']:7.4f} {d['sd_quad'] / rh.META_SRES:5.1f} "
              f"{d['curvatura']:+6.2f} {d['joelho']:>9s}")

    sd = np.array([d["sd"] for d in alvo])
    sl = np.array([d["sd_lin"] for d in alvo])
    sq = np.array([d["sd_quad"] for d in alvo])
    print(f"\n  orcamento da dispersao (mediana): rampa {100 * (1 - np.median(sl / sd)):.0f}% · "
          f"+curvatura {100 * (np.median(sl / sd) - np.median(sq / sd)):.0f}% · "
          f"resto {100 * np.median(sq / sd):.0f}%")
    print(f"  sigma mediano sem rampa+curvatura: {np.median(sq):.4f} = "
          f"{np.median(sq) / rh.META_SRES:.1f}x o limite")
    print(f"  passariam a 3a perna com as DUAS formas capturadas: "
          f"{int(np.sum(sq <= rh.META_SRES))} de {len(alvo)}")

    # --- a curvatura do CHU ordena pela amplitude? (o discriminante da incubacao)
    chu = [d for d in alvo if d["case"].startswith("chu")]
    if chu:
        print("\n  CHU — curvatura vs condicao de ensaio:")
        linhas = []
        for d in chu:
            m = re.search(r"D(\d)p(\d)mm", d["case"])
            f = re.search(r"F0_(\d+)kN", d["case"])
            if not (m and f):
                continue
            linhas.append((float(f"{m.group(1)}.{m.group(2)}"), float(f.group(1)),
                           d["curvatura"], d["sd"], d["case"]))
        for D, F0, a, s_, cid in sorted(linhas):
            print(f"    {cid[:40]:40s} D={D:.1f}mm F0={F0:.0f}kN  a={a:+.2f}  sigma={s_:.4f}")
        if len(linhas) >= 4:
            Dm = np.array([l[0] for l in linhas])
            a = np.abs([l[2] for l in linhas])
            lo, hi = a[Dm <= 0.4], a[Dm >= 0.5]
            if len(lo) and len(hi):
                print(f"    |a| medio D<=0,4mm {lo.mean():.2f} vs D>=0,5mm {hi.mean():.2f} "
                      f"-> razao {lo.mean() / max(hi.mean(), 1e-9):.1f}x")
                print("    CAVEAT: F0 varia so dentro do grupo D=0,4 => correlacao com F0 e'")
                print("    CONFUNDIDA, e dentro do grupo nao ha tendencia (0,94/0,47/0,85).")

    # --- a curvatura e' sistematica por fonte?
    por_fonte: dict[str, list[float]] = defaultdict(list)
    for d in alvo:
        por_fonte[d["case"].split("_")[0][:12]].append(d["curvatura"])
    mistos = [k for k, v in por_fonte.items() if len({x > 0 for x in v}) > 1]
    print(f"\n  fontes com sinal de curvatura MISTO: {mistos or 'nenhuma'} "
          "(misto => a curvatura depende da CONDICAO, nao do par tribologico)")

    dest = Path(sys.argv[sys.argv.index("--json") + 1]) if "--json" in sys.argv else SAIDA
    dest.write_text(json.dumps(alvo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  gravado: {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
