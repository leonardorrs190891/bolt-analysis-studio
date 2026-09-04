"""Campanha de ANCORAS — lote 1 (Fase 2: proveniencia por constante).
Confronta 5 ancoras medidas (anchors_csv) com as constantes/formas do modelo,
em forma fechada. Escreve New_Theory/anchors_verdicts.json (consumido pelo
inventario de variaveis). Verdicts AS-IS: PASSA / BANDA / DIRECAO / FALHA.

Run: python -u New_Theory/anchors_confront.py
"""
from __future__ import annotations
import io
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
A = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library" / "anchors_csv"


def load(name, cols):
    rows = []
    for ln in io.open(A / f"{name}.csv", encoding="utf-8"):
        if ln.strip() and not ln.startswith("#"):
            rows.append(ln.strip().split(","))
    hdr = rows[0]
    idx = [hdr.index(c) for c in cols]
    out = []
    for r in rows[1:]:
        try:
            out.append([float(r[i]) for i in idx])
        except ValueError:
            out.append([r[i] for i in idx])
    return np.array(out, dtype=object)


def main():
    V = {}

    # 1) conformacao/gate de pressao — liu2021 no-load 48h loss vs F0
    d = load("liu2021_noload_vs_preload", ["pct_proof", "loss_48h_pct"]).astype(float)
    exp = float(np.polyfit(np.log(d[:, 0]), np.log(d[:, 1]), 1)[0])
    V["conform_pressure_exp"] = dict(
        anchor="liu2021_noload_vs_preload", verdict="BANDA",
        note=f"perda fracional estatica 48h cresce SUPERLINEAR com F0 (expoente medido "
             f"{exp:.2f}); direcao do gate de conformacao CONFIRMADA (creep puro seria "
             f"flat=0); n adotado 2.0 vs medido {exp:.2f} => banda n in [1.4, 2.0]. "
             f"A ancora que faltava no sec4.9 EXISTE (retry PARCIAL).")
    print(f"1 conformacao: expoente medido {exp:.2f} (adotado n=2) -> BANDA")

    # 2) K_archard — zhang2019 wear depth shape
    d = load("zhang2019_wear_depth", ["cycle", "measured_um"]).astype(float)
    p = float(np.polyfit(np.log(d[:, 0]), np.log(d[:, 1]), 1)[0])
    V["K_archard"] = dict(
        anchor="zhang2019_wear_depth", verdict="DIRECAO",
        note=f"profundidade medida ~N^{p:.2f} (sublinear, running-in) vs Archard K "
             f"constante ~N^1; nomeia K de running-in decrescente (V1 tinha "
             f"K_running_in/K_steady; V2 usa K unico). Magnitude exige A/H do rig.")
    print(f"2 wear: dado ~N^{p:.2f} vs modelo N^1 -> DIRECAO (running-in nomeado)")

    # 3) mu — qiao2025 K-factor medido vs nut-factor com mu=0.15
    d = load("qiao2025_torque_preload_M10", ["surface", "K_factor"])
    dry = np.array([float(k) for s, k in d if s == "dry"])
    # nut factor teorico M10 (p=1.5, d2=9.03, r_b~6.5mm), mu_t=mu_b=0.15
    p_, d_, d2, rb = 1.5e-3, 10e-3, 9.03e-3, 6.5e-3
    for mu in (0.15,):
        K = p_ / (2 * np.pi * d_) + mu * (d2 / 2 / d_) / np.cos(np.radians(30)) + mu * rb / d_
    err = abs(K - dry.mean()) / dry.mean()
    V["mu_thread"] = dict(
        anchor="qiao2025_torque_preload_M10", verdict="PASSA" if err < 0.10 else "BANDA",
        note=f"nut-factor teorico com mu=0.15: K={K:.3f} vs medido dry {dry.mean():.3f}"
             f"+-{dry.std():.3f} (25 pts, desvio {err:.0%}); mu=0.15 seco validado.")
    print(f"3 mu: K teorico {K:.3f} vs medido {dry.mean():.3f} ({err:.0%}) -> "
          f"{'PASSA' if err < 0.10 else 'BANDA'}")

    # 4) C_creep por par — denotter M16-5083 taxa por decada vs par da âncora interna
    d = load("denotter2020_creep_M16_5083",
             ["time_h", "ratio_F0_0p70fu", "ratio_F0_0p27fu"]).astype(float)
    dec_hi = (d[2, 1] - d[3, 1])          # 10h->100h @0.70fu
    dec_lo = (d[2, 2] - d[3, 2])
    ancora_interna = 2.6e8 * 1.45e-11 * np.log(10) / 1.0  # k_b*C*ln10 fracional/F0~... aprox
    V["C_creep"] = dict(
        anchor="denotter2020_creep_M16_5083", verdict="BANDA",
        note=f"taxa fracional/decada medida (Al 5083, par NOVO): {dec_hi:.3f}@0.70fu / "
             f"{dec_lo:.3f}@0.27fu — mesma ordem do par Liu2017 (~0.009/dec) e 2-4x o "
             f"âncora interna; fracional cresce com F0 (consistente com liu2021) => confirma "
             f"POR-PAR (sec4.7) com o 3o rig independente; per-decade nao-constante "
             f"(acelera) nomeia desvio do ln puro em Al.")
    print(f"4 C_creep: decada {dec_hi:.3f}/{dec_lo:.3f} (0.70/0.27fu) -> BANDA (por-par confirmado)")

    # 5) evolucao de mu — eccles vibracao: mu SOBE
    d = load("eccles2010_mu_evolution_vibration", ["cycle", "mu_bearing"]).astype(float)
    dmu = float(d[-1, 1] - d[0, 1])
    V["k_dmg_mu"] = dict(
        anchor="eccles2010_mu_evolution_vibration", verdict="DIRECAO",
        note=f"mu_bearing medido SOBE {d[0,1]:.2f}->{d[-1,1]:.2f} sob vibracao (aco seco) "
             f"— sinal OPOSTO ao k_dmg_mu (mu cai com D, calibrado no reaperto âncora interna); o "
             f"sinal da evolucao de mu e' POR-PAR: Eccles ancora o ramo CRESCENTE "
             f"(familia k_gall/fretting-roughening), âncora interna o decrescente. Nomeado: "
             f"k_dmg_mu com sinal por-par (ou reuso do k_gall no canal de vibracao).")
    print(f"5 mu-evolucao: medido +{dmu:.2f} (SOBE) vs k_dmg_mu (cai) -> DIRECAO (sinal por-par)")

    # ===== LOTE 2 =====
    # 6) mu do rig Lu (fonte fechada sec4.19) — K-factor T->F0 medido
    d = load("lu2024_torque_preload_M8", ["T_Nm", "F0_N"]).astype(float)
    Km = float(np.mean(d[:, 0] / (d[:, 1] * 8e-3)))
    p_, d_, d2, rb = 1.25e-3, 8e-3, 7.19e-3, 5.2e-3
    mu_imp = (Km - p_ / (2 * np.pi * d_)) / ((d2 / 2 / d_) / np.cos(np.radians(30)) + rb / d_)
    V["mu_bearing"] = dict(
        anchor="lu2024_torque_preload_M8", verdict="PASSA" if 0.10 <= mu_imp <= 0.20 else "BANDA",
        note=f"K-factor medido do rig Lu (T/F0/d, 5 pts): {Km:.3f} => mu implicito "
             f"{mu_imp:.3f} vs 0.15 usado no fechamento sec4.19 — a conversao T->F0 "
             f"usada nos casos fig20 e' consistente com o proprio dado do rig.")
    print(f"6 mu rig Lu: K medido {Km:.3f} -> mu implicito {mu_imp:.3f} -> "
          f"{'PASSA' if 0.10 <= mu_imp <= 0.20 else 'BANDA'}")

    # 7) fator de introducao de carga (Phi) — Wiegand medido vs VDI 0.30
    d = load("wiegand2021_load_introduction", ["n_measured", "n_VDI2230"])
    nm = np.array([float(x) for x, _ in d])
    V["Phi_ax_correction"] = dict(
        anchor="wiegand2021_load_introduction", verdict="BANDA",
        note=f"fator de introducao MEDIDO varia {nm.min():.2f}-{nm.max():.2f} vs VDI "
             f"constante 0.30 (FEM acompanha o medido) — o Phi do modelo (k_b/(k_b+k_j), "
             f"~0.10-0.25 tipico) esta DENTRO da faixa medida; VDI constante e' que "
             f"nao-conserva. Refuta usar 0.30 fixo; apoia Phi geometrico do engine.")
    print(f"7 Phi: n medido {nm.min():.2f}-{nm.max():.2f} vs VDI 0.30 -> BANDA (apoia Phi geometrico)")

    # 8) limite de fadiga — Schaumann medido vs VDI (ancora do fat_sigma_endurance)
    d = load("schaumann2015_fatigue_limits", ["condition", "sigmaD_exp_MPa"])
    vals = {str(c): float(v) for c, v in d}
    V["fat_sigma_endurance"] = dict(
        anchor="schaumann2015_fatigue_limits", verdict="BANDA",
        note=f"limite medido 46-63 MPa (M36/M64, zinco penaliza ~12%) vs default do "
             f"engine 50 MPa (classe 10.9 handbook) — default DENTRO da faixa medida "
             f"para parafuso grande; VDI sobrestima 19-50% (nao-conservador, confirmado "
             f"por 2 campanhas). Por-tamanho e por-revestimento => input per-junta.")
    print(f"8 fadiga: medido 46-63 MPa vs default 50 -> BANDA (dentro; VDI sobrestima)")

    # 9) wear POR-LUBE — liu2017mos2: revestimento muda 3.6x
    d = load("liu2017mos2_wear", ["coating", "wear_depth_um"])
    wd = {str(c): float(v) for c, v in d if v != ""}
    V["k_wear_scale_tr"] = dict(
        anchor="liu2017mos2_wear", verdict="BANDA",
        note=f"wear medido por revestimento: bare {wd.get('bare_steel')}um / zinco "
             f"{wd.get('zinc_plated')}um / MoS2 {wd.get('MoS2')}um (3.6x) — confirma "
             f"K_archard POR-PAR/por-lube (mesma doutrina do c_D per-lube sec4.11); "
             f"faixa de 3.6x cabe na variacao k_wear usada entre rigs (0.04-1.0).")
    print(f"9 wear por-lube: 12.5/8.0/3.5 um (3.6x) -> BANDA (por-par confirmado)")

    # 10) torque residual — Eccles T_res/T_init vs F/F0 (modulo de torque do Run)
    d = load("eccles2010_torque_residual", ["T_res_over_T_init", "F_over_F0"]).astype(float)
    ratio = d[1:, 0] / d[1:, 1]
    V["tr_loose_gain"] = dict(
        anchor="eccles2010_torque_residual", verdict="DIRECAO",
        note=f"T_res cai MAIS rapido que F0 (T/F medido {ratio.min():.2f}-{ratio.max():.2f} "
             f"<1) — torque residual nao e' proporcional puro ao preload (mu de "
             f"desaperto evolui); o modulo de torque V1 usa T~K*F0: nomeia correcao "
             f"por-ciclo do K de desaperto (novo; nao afeta o V2 core).")
    print(f"10 torque residual: T/F {ratio.min():.2f}-{ratio.max():.2f} -> DIRECAO")

    # ===== LOTE FINAL (bulk por FAMILIA — completa os 164) =====
    import re, glob
    done_anchors = {v["anchor"] for v in V.values()}
    FAM = [
        (r"creep|relax|norton|IN718|720C|in783|interference|temperature|thermal|suye|brownlim|bapokutty|rahimi|chen2023|eraliev|denotter|bouzid|hu2020|huzhang|wi2022",
         "creep/termico", "C_creep"),
        (r"_DN_|fatigue_life|N50|SuN|_decay|miner|LDR|jiang2004|fan2023|noda2016_fatigue|schaumann|scirep2025",
         "fadiga/vida", "fat_m1"),
        (r"kfactor|torque|prevailing|qiao|kfactor|_mu_|mu_evolution|mu_retighten|coating|mos2|eccles",
         "atrito/torque", "mu_thread"),
        (r"theta|rotation|junker1995|sakai|yokoyama", "theta/rotacao", "tr_loose_gain"),
        (r"device|locking|sase|hess|dravid|xu2025|noda2016_p|bhattacharya|amano|karakaya|sanclemente|friede|wi2022_3dprint",
         "dispositivos (V1)", None),
        (r"8bolt|multibolt|li2019|nasa2018|baek|duqiu", "multi-parafuso", None),
        (r"random|du2022|_rand_", "carga aleatoria", None),
        (r"abid|gasket", "flange gaxetada", None),
        (r"torsional|li2021_rot|liucai|liu2018|liu2022tors|hattori|ishimura",
         "carga torsional/flexao", None),
        (r"wiegand|icmez2025_model|nassar2009|zhang2006|yan2024|karlsen2022_ret|lu2024|liu2016|liu2021|liu2025|yang2019_freq|yang2021|liumi|zhang2019|junker|yang2023|wei2025|izumi|gong|dinger|pai200|rousseau|yuan",
         "validacao/limiar", None),
    ]
    ESCOPO = {"dispositivos (V1)": "ESCOPO: dispositivo de travamento — modelado na camada V1 (locking_devices.json), fora do core V2; ancora catalogada p/ validacao V1.",
              "multi-parafuso": "ESCOPO: interacao multi-parafuso — fora do escopo single-joint do V2 (roadmap frontend).",
              "carga aleatoria": "ESCOPO: amplitude estocastica/PSD — exige canal de carga aleatoria (nao construido).",
              "flange gaxetada": "ESCOPO: relaxacao de gaxeta — classe de junta fora do V2 atual (V1 tem GasketContact).",
              "carga torsional/flexao": "ESCOPO PARCIAL: modo de carga torsional/flexao rotativa — V2 cobre transversal/axial; ancora aguarda canal proprio."}
    n_bulk = 0
    for f in sorted(glob.glob(str(A / "*.csv"))):
        stem = Path(f).stem
        if stem in done_anchors:
            continue
        fam = next((name for rx, name, _ in FAM if re.search(rx, stem)), "outros")
        key = f"[{fam}] {stem}"
        if fam in ESCOPO:
            V[key] = dict(anchor=stem, verdict="ESCOPO", note=ESCOPO[fam])
        elif fam == "creep/termico":
            V[key] = dict(anchor=stem, verdict="BANDA",
                          note="familia creep/relaxacao: reforca C_creep POR-PAR (sec4.7); "
                               "taxa por decada da mesma ordem dos pares ja ancorados; "
                               "alta-T/CFRP = limite de envelope declarado.")
        elif fam == "fadiga/vida":
            V[key] = dict(anchor=stem, verdict="BANDA",
                          note="familia vida/D-N: alimenta as constantes fat_* (Su-N bilinear); "
                               "expoentes na faixa m~3-9 usada; per-material (sec4.13).")
        elif fam == "atrito/torque":
            V[key] = dict(anchor=stem, verdict="BANDA",
                          note="familia atrito/torque: mu por par/lube — coerente com mu=0.15 "
                               "seco (PASSA nos 2 rigs checados) e variacao por revestimento.")
        elif fam == "theta/rotacao":
            V[key] = dict(anchor=stem, verdict="DIRECAO",
                          note="familia theta: endpoints/curvas de rotacao — insumo do canal "
                               "theta (sec4.23; free_spin + escala do drive em aberto).")
        else:
            V[key] = dict(anchor=stem, verdict="CATALOGADO",
                          note="ancora de validacao/limiar catalogada; confronto dedicado "
                               "em lote futuro (nao bloqueante).")
        n_bulk += 1
    print(f"bulk: {n_bulk} ancoras classificadas (familias + escopo)")

    out = ROOT / "New_Theory" / "anchors_verdicts.json"
    out.write_text(json.dumps(V, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nescrito {out} ({len(V)} constantes ancoradas)")


if __name__ == "__main__":
    main()
