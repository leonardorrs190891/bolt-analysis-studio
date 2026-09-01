# -*- coding: utf-8 -*-
"""Sonda SO-LEITURA: as duas curvas de 10 Hz do LI_2022 tem a MESMA trajetoria
absoluta e DIVISORES diferentes?

Motivacao (medida por subagente em 2026-08-05, `li2022_piso_fig8d_resultado.md`):
em forca ABSOLUTA as duas concordam em N=2e5 a **0,15 %** (9,850 vs 9,865 kN),
mas em F/F0 diferem por 0,031 — porque a Fig. 8(c) normaliza por **12,0 kN** e a
digitalizacao da Fig. 8(a) por **11,5 kN** (os valores da CSV sao multiplos
exatos de 1/115). O pixel do traco da 8(a) da **11,18**.

As duas leituras possiveis, e sao FISICAMENTE distintas:
  (A) MESMO ensaio em 2 figuras => a base 11,5 esta ERRADA (deveria ser 12,0) e
      a `axial_10Hz_full` carrega erro de NIVEL de 4,2 %.
  (B) ESPECIMES distintos com F0 11,5 vs 12,0 => 4,2 % e' dispersao de aperto
      (dentro da banda 4-14 % da campanha) e nao ha nada a corrigir. Em modo
      FORCA com a mesma amplitude imposta, perda absoluta parecida e' esperada.

Esta sonda NAO decide (A) vs (B) — ela mede o que cada uma implica para as duas
curvas da fila form-limited, para que a decisao seja informada em vez de
adivinhada. Nada e' escrito.

    py -3.12 New_Theory/li2022_base_10hz_sonda.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

A = "li2022ti_axialmin_10Hz"        # Fig. 8(c), base 12,0 kN
B = "li2022ti_axial_10Hz_full"      # Fig. 8(a), base 11,5 kN
BASE_A, BASE_B = 12.0, 11.5


def _interp(x, y, xs):
    lx = np.log10(np.asarray(x, float))
    return np.interp(np.log10(xs), lx, np.asarray(y, float))


def main() -> int:
    st = ValidationStore()
    ea, eb = st.get(A), st.get(B)
    xa, da, pa = map(np.asarray, (ea.metric_x, ea.metric_data, ea.metric_pred))
    xb, db, pb = map(np.asarray, (eb.metric_x, eb.metric_data, eb.metric_pred))

    print(f"{A}: n={len(xa)} x {xa[0]:.0f}..{xa[-1]:.0f} align={ea.align:.6f}")
    print(f"{B}: n={len(xb)} x {xb[0]:.0f}..{xb[-1]:.0f} align={eb.align:.6f}")
    print(f"align identico? {abs(ea.align - eb.align) < 1e-12}  "
          f"(mesma predicao, mesma ancora)")

    # ---- 1. a trajetoria ABSOLUTA e' a mesma?
    lo, hi = max(xa[0], xb[0]), min(xa[-1], xb[-1])
    g = np.logspace(np.log10(lo), np.log10(hi), 40)
    fa = _interp(xa, da, g) * BASE_A          # kN
    fb = _interp(xb, db, g) * BASE_B          # kN
    dif = fa - fb
    print(f"\n1. FORCA ABSOLUTA na janela comum [{lo:.0f}, {hi:.0f}] (40 pts log)")
    print(f"   |dif| media {np.abs(dif).mean():.4f} kN  max {np.abs(dif).max():.4f} kN"
          f"  rel.media {np.abs(dif/fa).mean()*100:.2f} %")
    print(f"   dif nos extremos: {dif[0]:+.4f} .. {dif[-1]:+.4f} kN")
    print(f"   em N=2e5: {_interp(xa,da,2e5)*BASE_A:.3f} vs "
          f"{_interp(xb,db,2e5)*BASE_B:.3f} kN")
    # razao de escala que melhor casa B em A (um numero, sem forma)
    k = float(np.sum(fa * fb) / np.sum(fb * fb))
    print(f"   fator otimo de escala B->A: {k:.5f}  (12,0/11,5 = "
          f"{BASE_A/BASE_B:.5f})  residuo pos-escala "
          f"{np.abs(fa - k*fb).mean():.4f} kN")

    # ---- 2. o que cada hipotese implica nas 3 reguas
    print("\n2. IMPLICACAO nas 3 reguas (predicao INALTERADA do store)")
    print(f"   {'cenario':44s} {'MAE':>7s} {'mx':>7s} {'sigma':>7s}  tripe")

    def reguas(rot, pred, dado):
        r = np.asarray(pred, float) - np.asarray(dado, float)
        # ddof=0: e' a convencao do STORE (conferido — sd do store casa
        # ddof=0 ao digito nas 4 curvas; com ddof=1 os numeros saem 5-8 %
        # altos e deixam de ser comparaveis ao publicado).
        mae, mx, sd = np.abs(r).mean(), np.abs(r).max(), r.std(ddof=0)
        ok = mae <= 0.05 and mx <= 0.10 and sd <= 0.025
        print(f"   {rot:44s} {mae:7.4f} {mx:7.4f} {sd:7.4f}  "
              f"{'PASSA' if ok else 'reprova'}")
        return mae, mx, sd

    reguas(f"{B} hoje (base 11,5)", pb, db)
    # (A): base verdadeira 12,0 => o dado desce por 11,5/12,0
    reguas(f"{B} sob (A): base 12,0", pb, db * (BASE_B / BASE_A))
    # e a leitura simetrica: se a 8(a) estivesse certa e a 8(c) errada
    reguas(f"{A} hoje (base 12,0)", pa, da)
    reguas(f"{A} sob base 11,5 (leitura oposta)", pa, da * (BASE_A / BASE_B))
    # (A) com o pixel 11,18 medido no traco da 8(a)
    reguas(f"{B} sob base 11,18 (pixel do traco)", pb, db * (BASE_B / 11.18))

    print("\n3. LEITURA")
    print("   sigma_res e' invariante por TRANSLACAO, nao por ESCALA: reescalar o")
    print("   dado por c muda o residuo por (1-c)*dado, que VARIA ao longo da")
    print("   curva => mexe no sigma. E' por isso que erro de base pode reprovar")
    print("   a 3a perna, e nao so a 1a.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
