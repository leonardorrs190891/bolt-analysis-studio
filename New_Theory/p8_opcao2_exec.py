# -*- coding: utf-8 -*-
"""EXECUTOR da P-8 opcao 2: escreve as CSVs corrigidas do PAR de digitalizacao.

Prereg: `docs/superpowers/specs/2026-08-09-p8-opcao2-prereg.md` (gates E1-E6).

Constroi exatamente como o premeasure validou: mesmos ciclos da CSV atual, `y`
interpolado da serie extraida da FIGURA, e o **1o ponto vindo da TABELA
impressa** (o c1 de pixel tem residuo declarado que os controles nao explicam).

⚠️ ESCREVE EM DISCO. Faz backup `.bkp_p8` antes. Rode com `--dry` para so' medir.

    py -3.12 New_Theory/p8_opcao2_exec.py [--dry]
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

from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402

# cid -> (json da extracao, chave da serie, valor de c1 na TABELA impressa)
# ⚠️ COPIADO do `ALVOS` de `lu2024_redigit_premeasure.py`, nao reconstruido: a
# 1a versao deste executor inventou nomes de arquivo, chaves e valores de c1, e
# os TRES estavam errados. O premeasure ja carrega a procedencia certa.
ALVOS = {
    "lu2024_M8_fig18_amp1p0": ("lu2024_fig18_extrai.json", "1p0", 0.632),
    "lu2024_M8_fig20_T22Nm": ("lu2024_fig20_extrai.json", "T22Nm", 0.632),
}


def _load(p: Path):
    cyc, rat = [], []
    for ln in p.read_text(encoding="utf-8").splitlines():
        pt = ln.replace(";", ",").split(",")
        if len(pt) < 2:
            continue
        try:
            x, y = float(pt[0]), float(pt[1])
        except ValueError:
            continue          # cabecalho
        cyc.append(x)
        rat.append(y)
    return np.array(cyc), np.array(rat)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    recs = {r.case_id: r for r in all_records()}
    print("P-8 opcao 2 — CSVs corrigidas do PAR de digitalizacao\n")
    print(f"{'curva':<28}{'n':>4}{'|dy| med':>10}{'|dy| max':>10}"
          f"   c10/c50 novo (tabela)")
    ok_e1 = True
    for cid, (jf, key, tab_c1) in ALVOS.items():
        jp = ROOT / "New_Theory" / jf
        if not jp.exists():
            print(f"  FALTA {jf} — rode lu2024_*_extrai.py antes")
            return 2
        d = json.loads(jp.read_text(encoding="utf-8"))
        serie = {float(k): float(v) for k, v in d[key]["serie"].items()}
        fx = np.array(sorted(serie))
        fy = np.array([serie[k] for k in fx])

        rec = recs[cid]
        csv = Path(rec.csv_path)
        cyc, rat = _load(csv)
        case = rec.validation_case
        off = float(getattr(case, "csv_x_offset", 0.0) or 0.0)

        novo = []
        for x in cyc:
            n = x - off
            if n <= 0:
                novo.append(1.0)          # ancora de pre-ciclagem
            elif n <= 1.0:
                novo.append(tab_c1)       # 1o ponto da TABELA
            else:
                novo.append(float(np.interp(n, fx, fy)))
        novo = np.array(novo)
        dy = np.abs(novo - rat)

        # E1: bate a tabela onde a tabela existe
        xn = cyc - off
        chk = []
        for c in (10, 50):
            if c < xn.min() or c > xn.max():
                chk.append("--")
                continue
            chk.append(f"{float(np.interp(c, xn, novo)):.3f}")
        print(f"{cid[-28:]:<28}{len(cyc):>4}{dy.mean():>10.4f}{dy.max():>10.4f}"
              f"   {'/'.join(chk)}")

        if not a.dry:
            bkp = csv.with_suffix(csv.suffix + ".bkp_p8")
            if not bkp.exists():
                shutil.copy2(csv, bkp)
            linhas = ["cycle,F_over_F0"]
            linhas += [f"{x:g},{y:.4f}" for x, y in zip(cyc, novo)]
            csv.write_text("\n".join(linhas) + "\n", encoding="utf-8")
            print(f"    escrito: {csv.name}  (backup {bkp.name})")

    print("\nDRY-RUN (nada escrito)" if a.dry else "\nCSVs ESCRITAS.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
