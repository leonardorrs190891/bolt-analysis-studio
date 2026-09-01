# -*- coding: utf-8 -*-
"""Sonda da fratura terminal do YANG_2021 — prereg 2026-07-29 (commit a4f00ad).

SO-LEITURA: nada e' escrito no store nem em adopted_configs.json.

O que ela faz, e por que assim:

  As 6 curvas do YANG_2021 terminam em F/F0=0 (fratura) e todas estao TRIMADAS
  logo antes da queda. A receita adotada do LIU_2025 (fadiga + rampa) modela essa
  queda; o que faltava era ancorar `fat_C1` por curva SEM iterar.

  Ancoragem em FORMA FECHADA (prereg §3): Miner e' linear em 1/C1, entao

      D(N) = (1/C1) * SUM_{n<=N} sigma_ar(n)^m1     e   D(N_frat)=1
      =>  C1 = SUM_{n<=N_frat} sigma_ar(n)^m1

  Com a rampa, alpha=1 so em D=1, logo g->0 EXATAMENTE em N_frat: a pre-carga do
  modelo zera no ciclo de fratura MEDIDO. E' leitura da vida, nao ajuste.

  O `sigma_ar` e' colhido INSTRUMENTANDO `sun_life` — o valor que o engine de fato
  usa. Re-derivar a tensao aqui arriscaria divergir da implementacao (e a
  divergencia seria silenciosa).

  Duas passadas bastam: abaixo de `D_on` o ramo da rampa devolve dF_0=0, logo
  sigma_ar nao depende da fadiga nos primeiros D_on do dano; so os ultimos
  (1-D_on) mudam.

    py -3.12 New_Theory/yang2021_fratura_probe.py [--quick] [--json saida.json]
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.numerical import dynamic_stiffness_analyzer as dsa  # noqa: E402
from bolt_analysis_studio.validation import report_html as rh                 # noqa: E402
from bolt_analysis_studio.validation import runner as rn                      # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records, record  # noqa: E402

FONTE = "YANG_2021"
C1_ENORME = 1e35            # nao fratura: serve so p/ colher sigma_ar(n)
TOL_C1 = 0.02               # convergencia da §3
MAX_PASSADAS = 4
TOL_G1 = 0.05               # G1: zero do modelo a <=5% de N_frat

# constantes com procedencia no LIU_2025 adotado (prereg §3)
FAT_BASE = dict(fatigue_enabled=True, fat_stress_mode="bending", fat_Kt=0.588,
                fat_sigma_uts=800e6, fat_sigma_knee=0.0, fat_sigma_endurance=1.0,
                fat_m1=3.12)
# as duas candidatas de forma que o treino (amp0p7mm) deixou empatadas
FORMAS = [(0.85, 8.0), (0.75, 16.0)]
TREINO = "yang2021_amp0p7mm_ax11p2kN"

_EXTRA: dict = {}
_SEM_TRIM = [True]
_SIGMA: list[float] = []


def _instalar_ganchos(janela_cheia: bool = True) -> None:
    """Injeta overrides, desliga o trim e instrumenta `sun_life`.

    O gancho do `sun_life` registra o sigma_ar por chamada — uma chamada por
    ciclo, na ordem dos ciclos, porque FatigueLoss.rate() e' avaliado uma vez
    por `step_cycle`.
    """
    _o, _t, _sl = rn._effective_overrides, rn._trim_n_for, dsa.sun_life

    rn._effective_overrides = lambda rec, base: {**_o(rec, base), **_EXTRA}
    rn._trim_n_for = lambda s, c, b: (None if _SEM_TRIM[0] else _t(s, c, b))
    if janela_cheia:
        # Achado de 2026-07-29: `FLOOR_TRIM = 0.10` e' convencao PRE-REGISTRADA da
        # campanha (runner.py §1) — pontos com ratio < 0,10 saem da metrica E
        # `n_max` passa a ser o ultimo ponto sobrevivente. Consequencia medida: em
        # 43 das 203 curvas (588 pontos, 13 fontes) a fase final do colapso esta
        # fora do escopo por convencao, NAO por trim de fonte; e a simulacao para
        # ANTES de N_frat, o que torna a fratura inobservavel. Para ANCORAR na vida
        # medida a janela tem de alcancar N_frat — por isso o piso cai aqui. A
        # convencao 0,10 continua valendo para as pernas comparaveis ao publicado.
        rn.FLOOR_TRIM = -1.0

    def sun_life_espiao(sigma_ar, mat):
        _SIGMA.append(float(sigma_ar))
        return _sl(sigma_ar, mat)

    dsa.sun_life = sun_life_espiao
    # FatigueLoss resolve `sun_life` pelo modulo, entao o patch acima basta.


def n_frat_medido(rec) -> float:
    """1o ciclo com y<=0,01 no CSV digitalizado = fratura MEDIDA (nunca ajustada)."""
    pts = []
    with open(Path(rec.csv_path), encoding="utf-8") as fh:
        for row in csv.reader(fh):
            try:
                pts.append((float(row[0]), float(row[1])))
            except (ValueError, IndexError):
                continue
    zeros = [x for x, y in pts if y <= 0.01]
    return zeros[0] if zeros else pts[-1][0]


def rodar(cid: str, overrides: dict | None) -> tuple:
    """Uma simulacao. Devolve (result, sigma_ar por ciclo, x do zero do modelo)."""
    _EXTRA.clear()
    _SIGMA.clear()
    if overrides:
        _EXTRA.update(overrides)
    res = rn.simulate_case(record(cid), n_cap=400_000)
    sig = np.array(_SIGMA, float)
    mp = np.asarray(res.metric_pred, float)
    mx = np.asarray(res.metric_x, float)
    abaixo = np.where(mp <= 0.05)[0]
    x_zero = float(mx[abaixo[0]]) if len(abaixo) else float("inf")
    return res, sig, x_zero


def ancorar(cid: str, n_frat: float, forma: tuple) -> dict:
    """Acha o C1 tal que D(N_frat) = 1 — a fratura fecha NO ciclo medido.

    A primeira versao desta funcao iterava o ponto fixo `C1 <- S(C1)` com
    `S = SUM sigma_ar^m1`. Mal posto, e medido: com `C1 = S(1e35) = 3,2574e33` a
    rampa liga nos ultimos (1-D_on) do dano, F_0 cai, `sigma_m` cai, `sigma_ar`
    CAI, a soma vira 3,2081e33 e `D(N_frat) = 0,985 < 1` — a fratura ESTACIONA
    (ratio parou em 0,5115). E' o Goodman vivo se auto-realimentando; o ponto fixo
    de `S` nao e' a raiz de `D = 1`.

    O correto e' a RAIZ de `f(C1) = S(C1)/C1 - 1`. `f` e' monotona DECRESCENTE em
    C1 (mais C1 => menos dano por ciclo), direcao verificada com 2 pontos antes de
    bisseccionar — regra da campanha, o bug apareceu 2x antes.
    """
    D_on, q = forma
    m1 = FAT_BASE["fat_m1"]

    def D_em_nfrat(C1: float) -> tuple[float, object]:
        cfg = {**FAT_BASE, "fat_ramp_D_on": D_on, "fat_ramp_q": q, "fat_C1": C1}
        res, sig, _ = rodar(cid, cfg)
        if not len(sig):
            return float("nan"), res
        n = int(min(round(n_frat), len(sig)))
        return float(np.sum(sig[:n] ** m1)) / C1, res

    # 2 pontos p/ a direcao + bracket
    d_alto, _ = D_em_nfrat(C1_ENORME)                     # C1 enorme => D << 1
    if not np.isfinite(d_alto):
        return dict(erro="sun_life nunca chamado — fadiga nao ligou")
    lo, hi = C1_ENORME, C1_ENORME
    d_lo = d_alto
    for _ in range(40):                                   # desce ate D >= 1
        lo *= 0.5
        d_lo, _ = D_em_nfrat(lo)
        if d_lo >= 1.0:
            break
    if d_lo < 1.0:
        return dict(erro="nao achei C1 com D>=1 (dano nunca fecha)")
    if d_alto >= 1.0:
        return dict(erro="direcao inesperada: D>=1 ja no C1 enorme")
    passos = 0
    for passos in range(1, 31):                           # bisseccao em log
        mid = float(np.sqrt(lo * hi))
        d_mid, _ = D_em_nfrat(mid)
        if d_mid >= 1.0:
            lo = mid
        else:
            hi = mid
        if hi / lo - 1.0 <= 0.002:                        # 0,2% em C1
            break
    C1 = float(np.sqrt(lo * hi))
    res, _, x_zero = rodar(cid, {**FAT_BASE, "fat_ramp_D_on": D_on,
                                 "fat_ramp_q": q, "fat_C1": C1})
    d_final, _ = D_em_nfrat(C1)
    return dict(C1=C1, passadas=passos, D_nfrat=d_final, x_zero=x_zero,
                mae=float(res.mae), mx=float(res.maxerr), sd=float(res.resid_std),
                n=len(res.metric_pred), fim=float(res.metric_pred[-1]),
                erro_n_frat=(abs(x_zero - n_frat) / n_frat
                             if np.isfinite(x_zero) else float("inf")))


def tripe(mae: float, mx: float, sd: float) -> bool:
    return mx <= rh.META_MAX and mae <= rh.META_MAE and sd <= rh.META_SRES


def main() -> int:
    _instalar_ganchos()
    casos = [r for r in all_records() if r.source == FONTE]
    if "--quick" in sys.argv:
        casos = [r for r in casos if r.case_id in (TREINO, "yang2021_amp1p0mm_ax2kN")]
    print(f"SONDA YANG_2021 — fratura terminal (prereg a4f00ad) · {len(casos)} curvas")
    print(f"  regua: res.max<={rh.META_MAX} MAE<={rh.META_MAE} sigma<={rh.META_SRES}")
    print(f"  TREINO (nao conta nos gates): {TREINO}\n")

    saida: dict = {}
    for D_on, q in FORMAS:
        print(f"=== forma COMPARTILHADA D_on={D_on} q={q} ===")
        print(f"  {'curva':28s} {'N_frat':>6s} {'C1':>9s} {'p':>2s} {'x_zero':>7s} "
              f"{'err%':>5s} | {'MAE':>6s} {'res.max':>7s} {'sigma':>6s} tripe | sem fadiga")
        linhas = []
        for rec in casos:
            cid = rec.case_id
            nf = n_frat_medido(rec)
            a = ancorar(cid, nf, (D_on, q))
            if "erro" in a:
                print(f"  {cid[:28]:28s} ERRO: {a['erro']}")
                continue
            base, _, _ = rodar(cid, None)           # curva INTEIRA, sem fadiga
            ok = tripe(a["mae"], a["mx"], a["sd"])
            okb = tripe(float(base.mae), float(base.maxerr), float(base.resid_std))
            print(f"  {cid[:28]:28s} {nf:6.0f} {a['C1']:9.2e} {a['passadas']:2d} "
                  f"{a['x_zero']:7.0f} {100*a['erro_n_frat']:5.1f} | "
                  f"{a['mae']:6.4f} {a['mx']:7.4f} {a['sd']:6.4f} "
                  f"{'PASSA' if ok else '     '} | "
                  f"{base.mae:.4f}/{base.maxerr:.4f}/{base.resid_std:.4f}"
                  f"{' PASSA' if okb else ''}")
            linhas.append(dict(case=cid, treino=(cid == TREINO), n_frat=nf, **a,
                               ok=ok, base_mae=float(base.mae),
                               base_mx=float(base.maxerr),
                               base_sd=float(base.resid_std), base_ok=okb))
        saida[f"D_on={D_on},q={q}"] = linhas
        cegas = [l for l in linhas if not l["treino"]]
        g1 = sum(1 for l in linhas if l["erro_n_frat"] <= TOL_G1)
        g2_melhora = sum(1 for l in cegas if l["mx"] <= l["base_mx"])
        g2_piora = [l["case"] for l in cegas
                    if (l["mae"] - l["base_mae"] > 0.01 or l["mx"] - l["base_mx"] > 0.01
                        or l["sd"] - l["base_sd"] > 0.01)]
        print(f"  G1 anchor <= {100*TOL_G1:.0f}%: {g1}/{len(linhas)}   "
              f"G2 res.max melhora: {g2_melhora}/{len(cegas)}   "
              f"pioram >+0,01: {len(g2_piora)} {g2_piora[:3]}")
        print(f"  G4 passam o tripe na janela INTEIRA: "
              f"{sum(1 for l in linhas if l['ok'])}/{len(linhas)} "
              f"(hoje, trimado: 2/6)\n")

    dest = (Path(sys.argv[sys.argv.index("--json") + 1]) if "--json" in sys.argv
            else ROOT / "New_Theory" / "yang2021_fratura_probe.json")
    dest.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"gravado: {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
