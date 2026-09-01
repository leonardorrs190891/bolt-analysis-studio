# -*- coding: utf-8 -*-
"""Executor do prereg D-S (2026-08-05) — corrige as CSVs tapered do CACCESE_2009.

Nove dos 26 pontos da `rep2` tracam a replica ERRADA (a MEDIA, nao a BAIXA), com
erro +0,040 a +0,054. Substituo as DUAS curvas tapered pela polilinha VETORIAL da
Fig. 9, preservando a ancora `(t=0, 1.0)` que as duas ja usam:

    traco 135 (o mais BAIXO, fim 0,6270) -> rep2
    traco 241 (o do MEIO,  fim 0,6805)   -> rep1
    traco 188 (o mais ALTO, fim 0,6828)  -> 3a replica, FORA DE ESCOPO

Por que substituir a curva INTEIRA em vez de remendar os 9 pontos: os 16 pontos
limpos carregam um offset sistematico de -0,004 (o vies do digitalizador). Remendar
so os 9 deixaria degraus de 0,004 nas fronteiras entre ponto corrigido e ponto
mantido; substituir tudo da provenancia UNICA (a extracao vetorial, residuo de
calibracao 2,3e-5) e zero descontinuidade. As duas variantes sao medidas e
comparadas — se discordarem, o gate G1 denuncia.

    py -3.12 New_Theory/caccese_rep2_csv_exec.py            # so os gates (nada escrito)
    py -3.12 New_Theory/caccese_rep2_csv_exec.py --escrever # G1/G4 ok => escreve + re-simula
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
       / "vector_extractions" / "caccese2009_fig9_vector.json")
CSVDIR = (ROOT / "BAS_V2_papers" / "E. Rodada 4 (deep-research 2026-07-11)"
          / "digitized_csv")
# traco vetorial -> case_id
# ⚠️ ESCOPO REDUZIDO PELO PROPRIO GATE (2026-08-05, 2a execucao): a `rep1`
# (traco 241) SAIU do escopo porque **reprovou o G4**. Ela casa a linha certa da
# Tabela 5 (44,7 kN, RMS 0,0051 — a melhor das tres, como esperado), mas a 2a
# melhor alternativa fica a **1,30x** e o gate exige >= 2x. O motivo e' REAL e
# nao e' defeito do gate: os tracos MEDIO e ALTO da Fig. 9 terminam em 0,6805 e
# 0,6828 — **0,0023 de diferenca** —, e o round-trip pela Eq. (2) nao os separa.
# Como a `rep1` (a) muda ZERO pontos acima de 0,02 (max desvio 0,0139), (b) ja
# PASSA o tripe por merito e (c) tem provenancia ambigua entre dois tracos
# quase coincidentes, corrigi-la seria trocar um dado bom por um dado bom de
# procedencia incerta. O gate decidiu; eu nao afrouxei a razao para 1,3.
MAPA = {"135": "caccese2009_tapered_45kN_rep2"}
# medido e registrado, FORA de escopo (a execucao completa esta no resultado):
#   rep1  traco 241 -> 44,7 kN RMS 0,0051 · 2a 0,0067 (razao 1,30x) REPROVA G4
#   rep1  CSV velha vs vetor: max 0,0139 · mediana 0,0035 · offset +0,0008
#   rep1  subidas: 1 na velha (seria 0 na nova) — defeito menor, nao corrigido
FONTE_CIDS = None            # preenchido do registry
# Tabela 5 do paper (lida do PDF, p.11), Eq. (2): Pt/P0 = 1/(1 + K1*t^n).
#   Configuration   D(mm)  P0(kN)  K1     n      alfa(4) alfa(5)  b(5)
#   Tapered C/AL    19.1   44.7    0.112  0.192  0.0530  0.0447   0.945
#   Tapered C/AL    19.1   44.8    0.173  0.165  0.0635  0.0459   0.895
#   Tapered C/AL    19.1   43.9    0.091  0.217  0.0488  0.0420   0.958
# ⚠️ ERRO DE INSTRUMENTO na 1a execucao, corrigido aqui e declarado no prereg:
# usei `n = b(5) - 1` (0,945-1 = -0,055), tomando a coluna **b da Eq. (5)** como
# se fosse o expoente da Eq. (2). Com n NEGATIVO o modelo CRESCE com t —
# direcao errada — e o G4 devolveu RMS ~0,24 nas tres linhas com razao 1,03x,
# isto e' "nenhuma linha explica a curva". O `n` verdadeiro e' a 2a coluna do
# bloco Eq.(2), POSITIVO (0,165-0,217). Ancora de sanidade dada pelo proprio
# paper no texto da Eq. (2) (Fox [18]): K1 = 0,0861 e n = 0,2519 — mesma ordem.
# Licao: gate que reprova TODAS as alternativas com razao ~1 nao esta medindo
# discriminancia, esta denunciando o instrumento.
TAB5 = {"44.7": (0.112, 0.192), "44.8": (0.173, 0.165), "43.9": (0.091, 0.217)}
ESPERADO = {"caccese2009_tapered_45kN_rep2": "44.8",
            "caccese2009_tapered_45kN_rep1": "44.7"}
TOL_FID = 0.005              # G1: |CSV novo - vetor| <= piso de digitalizacao
TOL_RMS = 0.006              # G4: RMS contra a linha da Tabela 5
RAZAO_MIN = 2.0              # G4: a 2a melhor alternativa >= 2x pior


def _eq2(t, K1, n):
    t = np.asarray(t, float)
    out = np.ones_like(t)
    m = t > 0
    out[m] = 1.0 / (1.0 + K1 * t[m] ** n)
    return out


def _le_csv(p: Path):
    xs, ys = [], []
    for i, ln in enumerate(p.read_text(encoding="utf-8").splitlines()):
        if not ln.strip() or i == 0 and not ln[0].isdigit():
            continue
        a, b = ln.split(",")[:2]
        xs.append(float(a)); ys.append(float(b))
    return np.array(xs), np.array(ys)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--escrever", action="store_true")
    a = ap.parse_args()

    d = json.loads(VEC.read_text(encoding="utf-8"))
    grid = np.array(d["grid"], float)
    print(f"extracao vetorial: {VEC.name}  residuo de calibracao "
          f"y={d['calib']['res_y']:.2e}  x={d['calib']['res_x']:.3f} h")

    novos, ok_g1, ok_g4 = {}, True, True
    for traco, cid in MAPA.items():
        vec = np.array(d["vector"][traco], float)
        assert len(vec) == len(grid), f"{traco}: grade incompativel"
        p = CSVDIR / f"{cid}.csv"
        xs, ys = _le_csv(p)
        assert np.allclose(xs, grid), f"{cid}: abscissas divergem da grade"

        # a CSV nova: vetor em t>0, ancora (0, 1.0) preservada
        novo = vec.copy(); novo[0] = 1.0
        novos[cid] = (xs, novo, ys, vec)

        print(f"\n=== {cid}  (traco {traco})")
        # --- G1a: VACUO por construcao, e foi a EXECUCAO que denunciou.
        # A CSV nova E' o vetor, entao "max|CSV_novo - vetor|" da 0,00000
        # EXATO — um gate que nao pode falhar nao e' gate. Substituido no prereg
        # (emenda declarada) pela acuracia do PROPRIO instrumento: o residuo de
        # calibracao da extracao, que e' o que de fato limita a fidelidade.
        res_y = float(d["calib"]["res_y"])
        print(f"  G1a' acuracia do instrumento: residuo de calibracao "
              f"{res_y:.2e} em F/F0 (<= 1e-4) "
              f"{'OK' if res_y <= 1e-4 else 'FALHA'}")
        ok_g1 &= bool(res_y <= 1e-4)
        # informacao, NAO gate: quanto a CSV VELHA se afasta do vetor
        dv = np.abs(ys[1:] - vec[1:])
        print(f"       CSV velha vs vetor: max {dv.max():.4f} · mediana "
              f"{np.median(dv):.4f}  (o piso declarado da campanha e' 0,005;"
              f" acima dele = ponto suspeito)")

        # --- G1b monotonicidade (relaxacao estatica: nao-crescente)
        subidas_v = int(np.sum(np.diff(ys) > 1e-9))
        subidas_n = int(np.sum(np.diff(novo) > 1e-9))
        print(f"  G1b monotonicidade: subidas na CSV VELHA = {subidas_v} · "
              f"na NOVA = {subidas_n} {'OK' if subidas_n == 0 else 'FALHA'}")
        ok_g1 &= subidas_n == 0

        # --- quantos pontos mudam, e quanto
        dd = np.abs(novo - ys)
        cont = int(np.sum(dd > 0.02))
        print(f"  pontos que mudam >0,02: {cont}  (max {dd.max():.4f}); "
              f"offset mediano dos limpos: {np.median((ys - vec)[dd <= 0.02]):+.4f}")

        # --- G4 round-trip contra a Tabela 5
        rms = {}
        for rot, (K1, n) in TAB5.items():
            rms[rot] = float(np.sqrt(np.mean((novo[1:] - _eq2(grid[1:], K1, n)) ** 2)))
        melhor = min(rms, key=rms.get)
        seg = sorted(rms.values())[1]
        print(f"  G4 Tabela 5: " + " · ".join(f"{k} kN {v:.4f}" for k, v in
                                             sorted(rms.items())))
        alvo = ESPERADO[cid]
        bom = (melhor == alvo and rms[melhor] <= TOL_RMS
               and seg >= RAZAO_MIN * rms[melhor])
        print(f"      melhor={melhor} kN (esperado {alvo}) rms={rms[melhor]:.4f} "
              f"2a={seg:.4f} razao={seg/rms[melhor]:.2f}x  {'OK' if bom else 'FALHA'}")
        ok_g4 &= bool(bom)

        # --- variante "remendar so os 9" (robustez declarada no prereg)
        off = float(np.median((ys - vec)[dd <= 0.02]))
        rem = ys.copy(); rem[dd > 0.02] = vec[dd > 0.02] + off
        print(f"  variante remendo-9: difere da substituicao total por no max "
              f"{np.abs(rem - novo).max():.4f} (o offset {off:+.4f})")

    print(f"\nG1 {'PASSA' if ok_g1 else 'FALHA'} · G4 {'PASSA' if ok_g4 else 'FALHA'}")
    if not (ok_g1 and ok_g4):
        print("!! gate violado — NADA escrito.")
        return 3
    if not a.escrever:
        print("\n(sem --escrever: nada foi tocado)")
        return 0

    # ---------------- escrita + re-simulacao
    from bolt_analysis_studio.validation.case_registry import all_records, record
    from bolt_analysis_studio.validation.store import ValidationStore
    import bolt_analysis_studio.validation.runner as rn

    st = ValidationStore()
    antes = {r.case_id: st.get(r.case_id) for r in all_records()
             if r.source == "CACCESE_2009"}
    for cid, (xs, novo, _ys, _v) in novos.items():
        p = CSVDIR / f"{cid}.csv"
        shutil.copy2(p, p.with_suffix(".csv.bkp_ds"))
        p.write_text("x,F_over_F0\n" + "".join(
            f"{x:g},{y:.4f}\n" for x, y in zip(xs, novo)), encoding="utf-8")
        print(f"escrito {p.name} (backup .csv.bkp_ds)")

    print(f"\nre-simulando as {len(antes)} curvas do CACCESE_2009:")
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
        print(f"  {'CORRIGIDA' if mudou else 'intacta  '} {cid[:38]:38s} "
              f"mae {b.mae:.4f}->{r.mae:.4f}  mx {b.maxerr:.4f}->{r.maxerr:.4f}  "
              f"sig {b.resid_std:.4f}->{r.resid_std:.4f}"
              f"{'' if (mudou or idem) else '   << G3 VIOLADO'}")
    print(f"\nG3 (as 5 nao tocadas ficam bit-identicas): "
          f"{'PASSA' if g3 else 'FALHA'}")
    print("\nProximo: gravar no store (parallel_batch --cases ... --store) e "
          "re-medir o piso (G5).")
    return 0 if g3 else 3


if __name__ == "__main__":
    raise SystemExit(main())
