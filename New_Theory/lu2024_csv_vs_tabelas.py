# -*- coding: utf-8 -*-
"""Round-trip de TODAS as CSVs do LU_2024 contra as Tabelas 8 e 9 do paper.

So-leitura, segundos, sem pixel: le as CSVs commitadas, aplica a convencao de
eixo do registry (`csv_x_offset`) e compara com as tabelas impressas.

Por que importa: a sonda de pixel (`lu2024_fig18_extrai.py`) mostrou que a
FIGURA reproduz a Tabela 8 a +-0,002 nas 4 curvas medidas. Logo qualquer
desvio da CSV e' da CSV. Este script poe TODAS na mesma regua — inclusive as
da Fig. 20, que a sonda de pixel ainda nao tocou.

⚠️ A linha 22 N.m da Tabela 9 e' IDENTICA a linha 1,0 mm da Tabela 8
(36,8/57,1/87,9/93,6): sao o MESMO ensaio publicado em duas figuras. Elas
formam o par de piso de DIGITALIZACAO da fonte, entao um erro compartilhado
entre as duas NAO aparece no piso — ele so' aparece contra a tabela.

    py -3.12 New_Theory/lu2024_csv_vs_tabelas.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation.case_registry import all_records   # noqa: E402
from bolt_analysis_studio.validation.inputs import load_full_curve      # noqa: E402

# retencao = 1 - atenuacao/decaimento
TAB8 = {  # Fig. 18, por amplitude (mm)
    "0p25": {1: 0.829, 10: 0.795, 50: 0.782, 100: 0.780},
    "0p5":  {1: 0.638, 10: 0.465, 50: 0.344, 100: 0.126},
    "1p0":  {1: 0.632, 10: 0.429, 50: 0.121, 100: 0.064},
    "1p5":  {1: 0.504, 10: 0.302, 50: 0.079, 100: 0.004},
    "2p0":  {1: 0.498, 10: 0.173, 50: 0.007},
}
TAB9 = {  # Fig. 20, por torque (N.m)
    "T4Nm":  {1: 0.838, 10: 0.453, 50: 0.177, 100: 0.037},
    "T10Nm": {1: 0.638, 10: 0.448, 50: 0.352, 100: 0.309},
    "T16Nm": {1: 0.641, 10: 0.472, 50: 0.242, 100: 0.187},
    "T22Nm": {1: 0.632, 10: 0.429, 50: 0.121, 100: 0.064},
    "T28Nm": {1: 0.617, 10: 0.465, 50: 0.317},
}


def main() -> int:
    recs = {r.case_id: r for r in all_records() if r.source == "LU_2024"}
    print("round-trip CSV -> tabela impressa (delta = CSV - tabela)\n")
    print(f"{'curva':<32}{'off':>5}{'c1':>9}{'c10':>9}{'c50':>9}{'c100':>9}"
          f"   pior")
    linhas = []
    sem_tabela: list[str] = []   # curvas sem tabela APLICAVEL (ver guarda abaixo)
    for cid in sorted(recs):
        rec = recs[cid]
        case = rec.validation_case
        # ⚠️ GUARDA DE FIGURA (2026-08-16). Ate aqui o matcher casava SO pelo
        # token de amplitude, entao `lu2024_M8_fig14_amp0p25_long` recebia a
        # TAB8, que e' a tabela da **Fig. 18**. Isso e' exatamente o cruzamento
        # de protocolos que a RETRATACAO de 2026-08-14 invalidou: a fig14 roda
        # o §3.1.3 (half-sine de maquina a 1 Hz) e a fig18/20 rodam o §3.2
        # (manual) — dito pelo TEXTO do proprio paper. Pareamento invalidado na
        # doutrina, ressuscitado dentro de um script de medicao.
        #
        # Efeito MEDIDO do defeito: as 3 `fig14_*_long` apareciam com deltas de
        # +0,18 a +0,84 e a linha "piores" as nomeava como as campeas — ou seja,
        # o script mandava o leitor cacar um defeito de digitalizacao que NAO
        # EXISTE, numa comparacao que nao tem direito de ser feita.
        #
        # A tabela agora so' se aplica a figura de onde ela foi lida.
        alvo = None
        if "fig18" in cid:
            fonte_tab = TAB8
        elif "fig20" in cid:
            fonte_tab = TAB9
        else:
            sem_tabela.append(cid)
            continue
        for k, v in fonte_tab.items():
            tok = f"_{k}" if k.startswith("T") else f"amp{k}"
            if tok in cid:
                alvo = v
                break
        if alvo is None:
            continue
        try:
            cyc, rat = load_full_curve(rec.csv_path)
        except Exception as e:                                 # noqa: BLE001
            print(f"{cid[:32]:<32}  erro: {e}")
            continue
        off = float(getattr(case, "csv_x_offset", 0.0) or 0.0)
        sc = float(getattr(case, "csv_x_scale", 1.0) or 1.0)
        x = np.maximum((np.asarray(cyc, float) - off) * sc, 0.0)
        y = np.asarray(rat, float)
        ds, cells = [], []
        for c in (1, 10, 50, 100):
            if c not in alvo:
                cells.append("     --")
                continue
            if c < x.min() or c > x.max():
                cells.append("    fora")
                continue
            d = float(np.interp(c, x, y)) - alvo[c]
            ds.append(abs(d))
            cells.append(f"{d:+9.4f}")
        pior = max(ds) if ds else float("nan")
        marca = "**" if pior > 0.02 else ("~" if pior > 0.01 else "ok")
        print(f"{cid[:32]:<32}{off:>5.0f}" + "".join(cells) +
              f"   {pior:.4f} {marca}")
        linhas.append((cid, pior))

    print()
    print("LEITURA: a sonda de pixel ja provou que a FIGURA reproduz a Tabela 8")
    print("a +-0,002 => qualquer desvio aqui e' da CSV, nao do paper.")
    if sem_tabela:
        # A ausencia tem de ser VISIVEL. Curva que sai da tabela em silencio
        # parece "conferida e OK" para quem le so' as linhas impressas — o
        # mesmo defeito das barras por fonte que sumiam quando valiam zero.
        print()
        print(f"SEM TABELA APLICAVEL ({len(sem_tabela)}) — NAO conferidas aqui,")
        print("e isso NAO e' aval. A Tabela 8 e' da Fig. 18 e a 9 e' da Fig. 20;")
        print("a fig14 roda OUTRO PROTOCOLO (§3.1.3 half-sine de maquina a 1 Hz")
        print("contra §3.2 manual), entao nenhuma das duas a descreve. Conferi-la")
        print("contra a Tabela 8 e' o pareamento que a RETRATACAO de 2026-08-14")
        print("invalidou — era o que este script fazia ate 2026-08-16.")
        for c in sem_tabela:
            print(f"   {c}")
    print()
    piores = sorted(linhas, key=lambda z: -z[1])[:5]
    print("piores:", ", ".join(f"{c} {p:.4f}" for c, p in piores))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
