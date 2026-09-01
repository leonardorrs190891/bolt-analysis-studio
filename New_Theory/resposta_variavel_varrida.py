# -*- coding: utf-8 -*-
"""O modelo RESPONDE a variavel que cada fonte varre? (so-leitura, segundos)

Motivacao (2026-08-06, campanha MARGENS fase A'): o LIU_2020 marca 8/9 no
placar por fonte e mesmo assim tem resposta EXATAMENTE ZERO a amplitude — as 3
curvas que passam, passam por coincidencia (a perda real calha de ficar perto
do valor unico que o modelo produz). Placar por fonte NAO detecta isso.

O teste: para cada fonte, agrupa as curvas pela variavel de fato varrida
(`delta_mm` ou `F_amp_N` do `config_used`) DENTRO de mesma janela (`n_max`), e
compara o ESPALHAMENTO da perda total (1o -> ultimo ponto da metrica) entre
dado e modelo.

  dado espalha muito E modelo nao  =>  CEGO (o canal daquela variavel esta
                                       morto ou saturado no config adotado)
  modelo espalha ~como o dado      =>  responde (validacao do instrumento)

⚠️ NAO agrupa por chave mecanica (a `_pisos_medidos`) — aquela e' cega a
variaveis que nao estao na tupla, e foi justamente ela que escondeu o caso.
⚠️ Ausencia de linha NAO e' atestado: fonte com <3 niveis na mesma janela nao
e' coberta. Sub-respostas do LU (torque) e do ROUSSEAU (espessura) foram
achadas por OUTROS caminhos e nao aparecem aqui.

    py -3.12 New_Theory/resposta_variavel_varrida.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation.store import ValidationStore      # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402

CEGO_MOD = 1.3      # espalhamento do modelo abaixo disto = sem resposta
CEGO_DADO = 2.0     # ... e do dado acima disto = havia o que responder


def main() -> int:
    st = ValidationStore()
    por_fonte: dict = {}
    for r in all_records():
        e = st.get(r.case_id)
        if e is None or not e.metric_pred:
            continue
        por_fonte.setdefault(r.source, []).append((e.config_used or {}, e))

    print("RESPOSTA A VARIAVEL VARRIDA (perda total: 1o -> ultimo ponto)")
    print(f"{'fonte':17s} {'var':10s} {'n_max':>8s} {'niv':>3s} "
          f"{'dado':>8s} {'modelo':>8s}  veredito")
    achados = []
    for src in sorted(por_fonte):
        L = por_fonte[src]
        if len(L) < 3:
            continue
        for var in ("delta_mm", "F_amp_N"):
            buck: dict = {}
            for cfg, e in L:
                v = cfg.get(var)
                if v is None:
                    continue
                p = np.asarray(e.metric_pred, float)
                d = np.asarray(e.metric_data, float)
                buck.setdefault((cfg.get("n_max"), float(v)), []).append(
                    (float(d[0] - d[-1]), float(p[0] - p[-1])))
            por_nmax: dict = {}
            for (nm, v), pares in buck.items():
                por_nmax.setdefault(nm, []).append(
                    (v, float(np.mean([x[0] for x in pares])),
                     float(np.mean([x[1] for x in pares]))))
            for nm, tri in sorted(por_nmax.items(), key=lambda kv: str(kv[0])):
                if len(tri) < 3:
                    continue
                tri.sort()
                yd = [t[1] for t in tri]
                ym = [t[2] for t in tri]
                if min(yd) <= 0 or min(ym) <= 0:
                    continue
                rd, rm = max(yd) / min(yd), max(ym) / min(ym)
                if rm < CEGO_MOD and rd > CEGO_DADO:
                    ver = "CEGO"
                    achados.append((src, var, rd, rm))
                elif rd > CEGO_DADO and rm < rd / 2:
                    ver = "fraco"
                    achados.append((src, var, rd, rm))
                else:
                    ver = "responde"
                print(f"{src:17s} {var:10s} {str(nm):>8s} {len(tri):3d} "
                      f"{rd:7.2f}x {rm:7.2f}x  {ver}")
    print(f"\nachados: {len(achados)}")
    for s, v, rd, rm in achados:
        print(f"  {s} / {v}: dado {rd:.2f}x contra modelo {rm:.2f}x "
              f"({100*(rm-1)/max(rd-1,1e-9):.0f} % da resposta)")
    print("\nAusencia de linha != atestado: fonte com <3 niveis na mesma janela")
    print("nao e' coberta por este teste.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
