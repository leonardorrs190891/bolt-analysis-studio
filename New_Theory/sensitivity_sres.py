"""SENSIBILIDADE DAS TRES PERNAS DO TRIPE às alavancas — foco no σ_res.

Item 1 da lista de melhorias (2026-07-29). Por que existe: a régua nova
(res.máx ≤ 0,10 · MAE ≤ 0,05 · σ_res ≤ 0,025) deslocou o gargalo — das 98 fora
do tripé, **93 violam o σ_res**, que mede FORMA do resíduo. Todo o ranking de
alavancas que a campanha usa (`kb.sensitivity`, estudo §4.42) foi medido em
deslocamento da PREDIÇÃO, que é da família do MAE. Começar a otimização com esse
ranking é mirar na régua que não está reprovando.

DIFERENÇAS DELIBERADAS em relação ao estudo §4.42:
 1. mede `Δ|σ_res|`, `Δ|MAE|` e `Δ|res.máx|` — as três réguas, para dar também a
    razão Δσ/ΔMAE, que é o que diz se uma alavanca é de FORMA ou de NÍVEL;
 2. perturba o **config canônico adotado** (via o mesmo `_effective_overrides`
    que o runner usa), não um working point montado à mão — é no canônico que a
    adoção vai mexer;
 3. roda nas curvas que a campanha PRECISA consertar: as recusadas por prova de
    piso (`f7_excecoes_por_prova_de_piso.md` §C), não numa amostra genérica.

SÓ-LEITURA: não escreve store nem `adopted_configs.json`. Saída:
`New_Theory/sensitivity_sres.json`.

Run: py -3.12 New_Theory/sensitivity_sres.py [--quick]   (~15-40 min)
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa
    JointMaterial)
from bolt_analysis_studio.validation import runner as rn  # noqa
from bolt_analysis_studio.validation.case_registry import record  # noqa

QUICK = "--quick" in sys.argv
FATOR = 1.2                     # ±20%, mesma perturbação do estudo §4.42
OUT = ROOT / "New_Theory" / "sensitivity_sres.json"

# Alavancas: as do estudo §4.42, com DUAS correções que o smoke test desta
# varredura obrigou — e as duas são a mesma armadilha (nome que não age):
#   · `mu` NÃO é campo de `JointMaterial` (são `mu_bearing` e `mu_thread`).
#     Perturbá-lo dava Δ = 0 exato e eu teria publicado "µ é inerte", que é
#     falso e é justamente o erro que o item 4 da lista existe para pegar.
#   · `K_archard` está MORTO no working point canônico: o bloco `shared` adota
#     `k_wear_spec = 5e-14`, e o engine ignora a via legada K/H quando ele é > 0
#     (gotcha do CLAUDE.md, agora confirmado por medição). A alavanca de
#     desgaste que age é `k_wear_spec`.
# Lição que vale para a campanha: "Δ = 0" tem DOIS significados — inerte no
# regime, ou nome que nunca chegou ao engine. Só o 2º é bug, e distinguir exige
# conferir o nome contra `__dataclass_fields__` e a via ativa contra o `shared`.
PARAMS = ["mu_bearing", "mu_thread", "emb_depth", "N_emb", "k_wear_spec",
          "k_j_init", "alpha_GW", "C_creep", "tr_loose_gain", "eta_loose",
          "c_bend", "loose_arrest_floor", "W_conf_ref",
          "conform_pressure_exp", "p_ref_conform", "slip_regime_sharpness",
          "slip_capacity_coeff", "partial_slip_exp"]

# As 33 RECUSADAS por prova de piso, ordenadas pela razão valor/piso (a fila de
# prioridade do item 2). Tomo as piores de cada fonte para não medir 6 curvas do
# mesmo rig e chamar de varredura.
ALVOS = [
    "yang2021_fig2_typical",                 # MAE 11,5x o piso
    "liu2020_fig9_zinc_AF0.4mm_P0-18kN",     # MAE 11,6x
    "chu2026ti_D0p4mm_F0_73kN_test8",        # σ 8,0x
    "bauer2024_M12_fig8_test1",              # res.máx 8,6x
    "eccles2010_fig6_annotated_4kN_axial",   # σ 2,4x
    "li2022ti_axial_10Hz_full",              # σ 2,5x (axial)
    "liu2022_fig8_multi_t1",                 # σ 1,5x
    "liu2016wear_fig7_run2_5e6cyc",          # σ 1,3x
    "zhang18_fig13_14kN_preload_vs_cycles",  # σ 1,1x (piso apertado)
    "liu2025_M16_amp0p25",                   # nível: |viés| = MAE
]
if QUICK:
    ALVOS = ALVOS[:3]
    PARAMS = PARAMS[:5]

# ---------------------------------------------------------------- perturbação
_PERT = {"p": None, "f": 1.0}
_orig = rn._effective_overrides


def _patched(rec, base_consts):
    """Aplica a perturbação NO MESMO dict que o runner usaria — assim o working
    point é o canônico adotado, com pack, per_case e geometria inclusos."""
    ov = dict(_orig(rec, base_consts))
    p, f = _PERT["p"], _PERT["f"]
    if p is None or f == 1.0:
        return ov
    cur = ov.get(p)
    if cur is None:
        cur = base_consts.get(p) if isinstance(base_consts, dict) else None
    if cur is None:
        cur = getattr(JointMaterial(), p, None)
    if cur is None or not isinstance(cur, (int, float)) or cur == 0:
        return ov            # inaplicável ou nulo: perturbar 0 não faz nada
    ov[p] = float(cur) * f
    return ov


rn._effective_overrides = _patched


# Teto de ciclos por simulação. Sem ele a varredura não termina: escolhi os
# alvos pela razão valor/piso e dois deles são longos por natureza
# (`liu2016wear_fig7_run2_5e6cyc` = 5e6 ciclos, `li2022ti_axial_10Hz_full`),
# o que daria ~37 simulações longas cada. O teto vale para o NOMINAL e para as
# perturbações igualmente, então o Δ medido continua comparável — é ranking
# local de alavanca, não o MAE de galeria daquele caso (mesmo caveat do estudo
# §4.42, que usa CAP_AX = 100000).
CAP = 100_000


def medir(cid):
    """(mae, maxerr, sigma) do caso no estado corrente de `_PERT`."""
    rec = record(cid)
    if rec is None:
        return None
    r = rn.simulate_case(rec, n_cap=CAP)
    if not r.ok or r.mae is None or r.resid_std is None:
        return None
    return (float(r.mae), float(r.maxerr), float(r.resid_std))


def main():
    print(f"alvos: {len(ALVOS)} · alavancas: {len(PARAMS)} · "
          f"simulações: {len(ALVOS) * (1 + 2 * len(PARAMS))}")
    saida = []
    for cid in ALVOS:
        _PERT.update(p=None, f=1.0)
        base = medir(cid)
        if base is None:
            print(f"  {cid}: NÃO SIMULÁVEL — fora da varredura")
            continue
        print(f"\n{cid}\n  nominal: MAE {base[0]:.4f} · max {base[1]:.4f} "
              f"· σ {base[2]:.4f}")
        linha = {"case": cid, "mae0": base[0], "max0": base[1],
                 "sd0": base[2], "params": {}}
        for p in PARAMS:
            vals = {}
            for lbl, f in (("up", FATOR), ("dn", 1.0 / FATOR)):
                _PERT.update(p=p, f=f)
                try:
                    v = medir(cid)
                except Exception as exc:            # noqa: BLE001
                    print(f"    {p} {lbl}: erro {type(exc).__name__}")
                    v = None
                vals[lbl] = v
            _PERT.update(p=None, f=1.0)
            ds, dm, dx = [], [], []
            for v in vals.values():
                if v is None:
                    continue
                dm.append(abs(v[0] - base[0]))
                dx.append(abs(v[1] - base[1]))
                ds.append(abs(v[2] - base[2]))
            if not ds:
                continue
            S_sd, S_mae, S_max = (sum(ds) / len(ds), sum(dm) / len(dm),
                                  sum(dx) / len(dx))
            linha["params"][p] = {"S_sd": S_sd, "S_mae": S_mae, "S_max": S_max,
                                  "razao_sd_mae": (S_sd / S_mae) if S_mae > 1e-9
                                  else None}
            if S_sd > 1e-6 or S_mae > 1e-6:
                print(f"    {p:22s} Δσ {S_sd:.5f} · ΔMAE {S_mae:.5f} · "
                      f"Δmax {S_max:.5f}"
                      + (f" · Δσ/ΔMAE {S_sd / S_mae:5.2f}"
                         if S_mae > 1e-9 else " · ΔMAE~0"))
        saida.append(linha)
    OUT.write_text(json.dumps(saida, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    # --------- agregado: quem move o σ_res
    agg = {}
    for l in saida:
        for p, s in l["params"].items():
            agg.setdefault(p, {"sd": [], "mae": []})
            agg[p]["sd"].append(s["S_sd"])
            agg[p]["mae"].append(s["S_mae"])
    print("\n" + "=" * 72)
    print("RANKING — quanto cada alavanca move o σ_res (média sobre os casos)")
    print("=" * 72)
    print(f"{'alavanca':24s} {'Δσ_res':>9s} {'ΔMAE':>9s} {'Δσ/ΔMAE':>8s}  classe")
    for p, v in sorted(agg.items(), key=lambda kv: -sum(kv[1]["sd"]) / len(kv[1]["sd"])):
        s = sum(v["sd"]) / len(v["sd"])
        m = sum(v["mae"]) / len(v["mae"])
        r = (s / m) if m > 1e-9 else float("inf")
        cls = ("INERTE" if s < 1e-5 and m < 1e-5 else
               "FORMA (move σ mais que MAE)" if r > 1.15 else
               "NÍVEL (move MAE mais que σ)" if r < 0.85 else "mista")
        print(f"{p:24s} {s:9.5f} {m:9.5f} "
              + (f"{r:8.2f}" if math.isfinite(r) else "     inf")
              + f"  {cls}")
    print(f"\nescrito: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
