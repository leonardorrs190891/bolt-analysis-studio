# -*- coding: utf-8 -*-
"""Varredura de ANCORAS EM PROSA nos PDFs — o que da' para auditar sem tabela.

## Motivacao (resultado negativo que a motiva)

Varri os 11 PDFs de `pdfs_open_access/` procurando tabelas numericas de
retencao/decaimento: **so' o LU_2024 tem** (Tabelas 7, 8 e 9). O padrao
"auditar CSV contra tabela impressa", que rendeu o bloco do LU nesta campanha,
esta ESGOTADO — nao ha uma segunda fonte onde ele se aplique.

Sobra a rede mais larga: os autores afirmam valores **no texto**
("the loss of pre-loading is only 69.1% after 100 vibration cycles"). Cada
afirmacao dessas e' uma ancora auditavel contra a CSV correspondente.

Este script NAO audita — ele **inventaria**: extrai as frases com numero que
falam de perda/retencao de pre-carga, por fonte, para que o alvo da auditoria
seja escolhido por evidencia e nao por palpite.

    py -3.12 New_Theory/ancoras_prosa_sweep.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDFS = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
        / "pdfs_open_access")

try:
    import fitz
except ImportError:                                        # pragma: no cover
    print("PyMuPDF ausente"); sys.exit(2)

# a frase tem de falar do OBSERVAVEL e trazer numero
CHAVE = re.compile(
    r"(pre-?load|preload|clamp\s*force|residual\s*(?:force|torque)|"
    r"loosening|relaxation|loss of)", re.I)
NUM = re.compile(r"\d+(?:\.\d+)?\s*(?:%|N\b|kN\b|cycles?\b)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    ap.add_argument("--max", type=int, default=6, help="frases por fonte")
    a = ap.parse_args()

    out = {}
    for pdf in sorted(PDFS.glob("*.pdf")):
        try:
            doc = fitz.open(str(pdf))
        except Exception as e:                             # noqa: BLE001
            print(f"{pdf.name}: ERRO {e}")
            continue
        frases = []
        for pi in range(len(doc)):
            txt = " ".join(doc[pi].get_text().split())
            for fr in re.split(r"(?<=[.])\s+", txt):
                if len(fr) < 40 or len(fr) > 320:
                    continue
                if not CHAVE.search(fr):
                    continue
                nums = NUM.findall(fr)
                if len(nums) < 2:          # precisa de valor E de "quando"
                    continue
                frases.append((pi, len(nums), fr))
        frases.sort(key=lambda z: -z[1])
        out[pdf.stem] = [dict(pag=p, n=n, frase=f) for p, n, f in frases]
        print(f"\n=== {pdf.stem}  ({len(frases)} frases com >=2 numeros)")
        for p, n, f in frases[:a.max]:
            print(f"  [pag {p:>2}, {n} nums] "
                  f"{f[:200].encode('ascii', 'replace').decode()}")

    print("\n" + "=" * 70)
    print("resumo (frases ancoraveis por fonte):")
    for k, v in sorted(out.items(), key=lambda z: -len(z[1])):
        print(f"  {k:<34} {len(v):>3}")
    print("\nLEITURA: fonte com muitas frases numericas e' onde a auditoria")
    print("CSV-contra-impresso ainda e' possivel sem tabela. Zero frases =")
    print("o dado so' pode ser conferido contra a propria figura.")
    if a.json:
        a.json.write_text(json.dumps(out, indent=1, ensure_ascii=False),
                          encoding="utf-8")
        print(f"\njson -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
