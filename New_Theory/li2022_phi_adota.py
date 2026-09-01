# -*- coding: utf-8 -*-
"""Adocao D-P — Phi MEDIDO no LI_2022_TRIBOINT. Procedencia com efeito NULO.

`k_j_init` = 5.29e8 (Phi = 0.4673) contra o default 4e9 (Phi = 0.1039).

Derivado do proprio paper: eq. 2 da a lei da carga
`F = A_F + A_F*sin(2*pi*f*t)` com A_F=10 kN => a carga externa varre 0->20 kN
(pico-a-pico 20 kN); a Fig. 8(b) traz a envoltoria MEDIDA no parafuso a 10 Hz
(19,10 / 9,76 kN) => oscilacao 9,34 kN => Phi = 9,34/20 = 0,467.

*** O EFEITO NA METRICA E NULO, e e isso que se afirma. *** Delta = 0,00e+00
exato nas 4 curvas. Ver prereg 2026-08-05-li2022-phi-medido.

    py -3.12 New_Theory/li2022_phi_adota.py [--dry]
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

CFG = ROOT / "New_Theory" / "adopted_configs.json"
GRUPO = "LI_2022_TRIBOINT"
K_J = 5.29e8

PROV = (
    "Phi MEDIDO (D-P, 2026-08-05). Derivado do proprio paper: a eq. 2 da a lei "
    "da carga F = A_F + A_F*sin(2*pi*f*t) com A_F=10 kN, logo a carga externa "
    "varre 0->20 kN (pico-a-pico 20 kN); a Fig. 8(b) traz a envoltoria MEDIDA "
    "no parafuso a 10 Hz (19,10 / 9,76 kN), logo oscilacao 9,34 kN e "
    "Phi = 9,34/20 = 0,467. Confere ao digito: F_B,max = 9,76 + 0,467*20 = "
    "19,10 kN. k_j = k_b(1-Phi)/Phi = 4,64e8*0,533/0,467 = 5,29e8 N/m (o "
    "default era 4e9, dando Phi=0,104 -- 4,5x pequeno). Plausibilidade: rig "
    "servo-hidraulico com fixture custom (upper/lower clamping ends), e o "
    "caminho de carga inclui o fixture. "
    "*** EFEITO NA METRICA: NULO. *** Delta = 0,00e+00 EXATO nas 4 curvas da "
    "fonte. Phi so entra em L_ax = Phi_ax_active*sin(beta)*F_ax (canal de "
    "afrouxamento rotacional), que carrega 0,000% da perda nestas curvas; e o "
    "slip de FLANCO nao passa por Phi (engine linha 1248: s_th = F_ax/k_b). "
    "Inercia gateada por CANAL, com predicao registrada ANTES da medicao "
    "(li2022_phi_ancora.md) e teste de campo feito para descartar a hipotese "
    "de campo errado (Phi_eff muda 0,10394 -> 0,46727 quando k_j_init muda; "
    "kj_mode default e vazio). ADOTADO POR PROCEDENCIA, NAO POR GANHO. "
    "*** ACOPLAMENTO LATENTE: *** k_torsional no modo legado e k_j_init*d_2/2, "
    "logo esta mudanca o altera 7,6x. Hoje e inocuo (o canal carrega 0), mas se "
    "um trabalho futuro ativar o afrouxamento rotacional nesta fonte, o "
    "k_torsional estara 7,6x diferente do que estava quando qualquer constante "
    "daquele canal foi calibrada.")


def main() -> int:
    d = json.loads(CFG.read_text(encoding="utf-8"))
    node = d["sources"][GRUPO]
    print(f"{GRUPO}: k_j_init ja presente? {'k_j_init' in node['cfg']}")
    print(f"  adotando k_j_init = {K_J:.3e}  (Phi = 4.64e8/(4.64e8+{K_J:.3e}) "
          f"= {4.64e8/(4.64e8+K_J):.4f})")
    if "--dry" in sys.argv:
        print("--dry: nada escrito")
        return 0

    shutil.copy2(CFG, CFG.with_suffix(".json.bkp_dp"))
    node["cfg"]["k_j_init"] = K_J
    node.setdefault("prov", {})["k_j_init"] = PROV
    CFG.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
    print("escrito · backup adopted_configs.json.bkp_dp")

    import importlib
    import bolt_analysis_studio.calibration.knowledge_base as kb
    importlib.reload(kb)
    import bolt_analysis_studio.validation.runner as rn
    importlib.reload(rn)
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        JointMaterial, Phi_eff, SlowState)
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.inputs import inputs_for

    rec = record("li2022ti_axialmin_10Hz")
    kw = rn.material_kwargs_for(rec, inputs_for(rec.validation_case))
    print(f"\nG2: k_j_init que o engine recebe = {kw.get('k_j_init')}")
    g = rn.geometry_for_case(rec.validation_case, 25.0)
    m = JointMaterial(**{k: v for k, v in kw.items()
                         if k in JointMaterial.__dataclass_fields__})
    phi = Phi_eff(SlowState(F_0=12500.0, F_0_init=12500.0), g, m,
                  direction="axial")
    ok2 = abs(phi - 0.467) <= 0.005
    print(f"G2: Phi_eff(axial) = {phi:.5f}  (alvo 0,467 +- 0,005) -> "
          f"{'PASSA' if ok2 else 'REPROVA'}")

    print("\nG1 (efeito nulo) nas 4 curvas da fonte:")
    ruim = []
    for cid in ("li2022ti_axialmin_10Hz", "li2022ti_axialmin_15Hz",
                "li2022ti_axialmin_20Hz", "li2022ti_axial_10Hz_full"):
        r = rn.simulate_case(record(cid))
        if not r.ok:
            print(f"  !! {cid}: {r.error}")
            return 2
        from bolt_analysis_studio.validation.store import ValidationStore
        s = ValidationStore().get(cid)
        dd = max(abs(r.mae - s.mae), abs(r.maxerr - s.maxerr),
                 abs(r.resid_std - s.resid_std))
        flag = "OK" if dd < 1e-12 else "MUDOU"
        if flag != "OK":
            ruim.append((cid, dd))
        print(f"  {flag:6s} {cid:30s} delta_max = {dd:.3e}")
    if ruim or not ok2:
        print("\n!! ABORTAR — G1 ou G2 reprovado. Restaure o backup.")
        return 3
    print("\nADOCAO CONFIRMADA: Phi certo, metrica bit-identica. "
          "Proximo: re-stamp so para uniformizar o fingerprint.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
