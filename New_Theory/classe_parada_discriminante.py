"""A razao de inclinacao terminal NAO distingue duas causas opostas — o sinal do
vies terminal distingue. Sonda so-leitura sobre as 7 fontes de `classe_parada`.

## Por que este script existe

`_FONTES_CLASSE_PARADA` foi montada com a **razao de inclinacao terminal**
(dado/modelo no fim da curva). Razao alta foi lida como *"o modelo nao acelera
no fim"* — a forma faltante que a regra de parada encerrou em 2026-08-02.

O `sun_crimp_resultado.md` (2026-08-06) mediu que a razao e' **ambigua**: no SUN
ela vale 25,0 nao porque o modelo deixe de acelerar, mas porque ele **ja
desabou e esta estacionado no `loose_arrest_floor` desde N=167**. Inclinacao
terminal ~0 tem duas causas opostas e a razao da o mesmo numero para as duas.

## O desempate

Sinal do vies no trecho terminal, `mean(modelo - dado)`:

* **> 0** — o modelo RETEM mais que o dado no fim ⇒ faltou acelerar ⇒ membro
  genuino da classe.
* **< 0** — o modelo esta ABAIXO do dado ⇒ desabou cedo ⇒ defeito ESPELHADO,
  e o remedio da classe (acelerar mais) piora. Falso positivo.

## Escolha de janela (trade-off declarado, revisavel)

Terminal = **ultimo terco dos pontos da metrica** (min. 4). Alternativa
considerada: ultimos 20 % do intervalo de ciclos — rejeitada porque a
amostragem das curvas digitalizadas e' fortemente nao-uniforme (as fontes
plotam em log), entao "20 % dos ciclos" pode conter 2 pontos numa curva e 30
noutra. O ultimo quarto sai junto como teste de sensibilidade: se o SINAL
trocar entre as duas janelas, a curva e' marcada `AMBIGUO` em vez de receber
veredicto.

Uso: PYTHONPATH=src py -3.12 New_Theory/classe_parada_discriminante.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation import report_html as rh           # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records   # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "_triagem", ROOT / "New_Theory" / "regra_de_parada_triagem.py")
tri = importlib.util.module_from_spec(_spec)          # type: ignore[arg-type]
_spec.loader.exec_module(tri)                         # type: ignore[union-attr]

STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"


def _terminal(vec_p, vec_d, frac: float):
    """Vies medio no trecho terminal. `frac` = 1/3 ou 1/4 dos pontos."""
    n = len(vec_p)
    k = max(4, int(round(n * frac)))
    if n < 6:
        return None
    k = min(k, n)
    return float(np.mean(vec_p[-k:] - vec_d[-k:]))


def _slope(x, y):
    """Inclinacao por minimos quadrados; None se x for degenerado."""
    if len(x) < 3 or float(np.ptp(x)) <= 0:
        return None
    return float(np.polyfit(x, y, 1)[0])


def main() -> int:
    store = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    pisos = tri.pisos_medidos(store, recs)
    excecoes = set(rh._EXCECOES)

    linhas: list[tuple] = []
    for cid, raw in store.items():
        rec = recs.get(cid)
        if rec is None or not rh.caso_comparavel(rec.source, cid):
            continue
        fonte = rec.source
        if fonte not in tri._FONTES_CLASSE_PARADA:
            continue
        mae, mx, sd = raw.get("mae"), raw.get("maxerr"), raw.get("resid_std")
        if mae is None or mx is None or sd is None:
            continue
        lim_s = rh.limite_sres(fonte, pisos)
        passa = (mae <= rh.META_MAE and mx <= rh.META_MAX and sd <= lim_s)
        if passa or cid in excecoes or cid in rh._DECLARADAS:
            continue                       # so as efetivamente PARADAS

        x = np.asarray(raw.get("metric_x") or [], float)
        p = np.asarray(raw.get("metric_pred") or [], float)
        d = np.asarray(raw.get("metric_data") or [], float)
        if len(p) != len(d) or len(p) < 6 or len(x) != len(p):
            linhas.append((fonte, cid, None, None, None, None, "SEM_VETORES"))
            continue

        b3 = _terminal(p, d, 1 / 3)
        b4 = _terminal(p, d, 1 / 4)
        # razao de inclinacao terminal (|dado| / |modelo|) no ultimo terco
        k = max(4, len(p) // 3)
        sd_ = _slope(x[-k:], d[-k:])
        sp_ = _slope(x[-k:], p[-k:])
        razao = (abs(sd_) / abs(sp_)) if (sd_ is not None and sp_
                                          and abs(sp_) > 1e-12) else None

        if b3 is None or b4 is None:
            verd = "SEM_JANELA"
        elif (b3 > 0) != (b4 > 0):
            verd = "AMBIGUO"
        elif b3 > 0:
            verd = "classe (retem demais)"
        else:
            verd = "ESPELHADO (desabou cedo)"
        linhas.append((fonte, cid, b3, b4, razao, max(mae / rh.META_MAE,
                                                      mx / rh.META_MAX,
                                                      sd / lim_s), verd))

    print("DISCRIMINANTE da classe_parada — sinal do vies terminal")
    print("  vies = mean(modelo - dado);  >0 retem demais (classe)")
    print("                               <0 desabou cedo (ESPELHADO)")
    print()
    hdr = (f"{'fonte':<17}{'curva':<42}{'vies1/3':>9}{'vies1/4':>9}"
           f"{'razao':>8}{'pior':>7}  veredicto")
    print(hdr)
    print("-" * len(hdr))
    cont: dict[str, int] = {}
    por_fonte: dict[str, list[str]] = {}
    for fonte, cid, b3, b4, razao, pior, verd in sorted(linhas):
        f3 = f"{b3:+.4f}" if b3 is not None else "    -   "
        f4 = f"{b4:+.4f}" if b4 is not None else "    -   "
        fr = f"{razao:.2f}" if razao is not None else "   -"
        fp = f"{pior:.2f}x" if pior is not None else "   -"
        print(f"{fonte:<17}{cid:<42}{f3:>9}{f4:>9}{fr:>8}{fp:>7}  {verd}")
        cont[verd] = cont.get(verd, 0) + 1
        por_fonte.setdefault(fonte, []).append(verd)

    print()
    print("Resumo por veredicto:")
    for k2, v in sorted(cont.items(), key=lambda kv: -kv[1]):
        print(f"  {k2:<28} {v:>3}")

    print()
    print("Resumo por FONTE (a classe e' atribuida por fonte — e' aqui que a")
    print("reclassificacao se decide):")
    for fonte in sorted(por_fonte):
        vs = por_fonte[fonte]
        n_cl = sum(1 for v in vs if v.startswith("classe"))
        n_es = sum(1 for v in vs if v.startswith("ESPELHADO"))
        n_am = len(vs) - n_cl - n_es
        if n_cl and not n_es:
            veredicto = "COERENTE com a classe"
        elif n_es and not n_cl:
            veredicto = "*** FALSO POSITIVO (todas espelhadas) ***"
        else:
            veredicto = "MISTA — decidir curva a curva"
        print(f"  {fonte:<18} classe={n_cl} espelhado={n_es} ambiguo={n_am}"
              f"   -> {veredicto}")

    print()
    print("NAO e' adocao: reclassificar camada da triagem exige assinatura")
    print("(charter). Este script produz o NUMERO para a decisao.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
