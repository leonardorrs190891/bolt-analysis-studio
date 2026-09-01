# -*- coding: utf-8 -*-
"""Adocao D-L — relogio por reaperto no LIU_2022 (3 numeros COMPARTILHADOS).

    retight_loss_base = 0.45   (queda no 1o reaperto: a interface assenta)
    retight_loss_gain = 0.88   (re-dano por evento; g = 1.88)
    k_emb_renew       = 0.65   (renovacao PARCIAL do assentamento)

Aplicados aos DOIS protocolos que NAO soltam o parafuso — `fig8` (seco) e
`fig7a` (oleo) —, com os MESMOS valores. As diferencas entre as lubrificacoes
saem do `c_D` ja adotado (0.5 seco / 0.03 oleo), porque `k_emb_renew` entra
como `delta_emb *= (1 - k_emb_renew*D)`, multiplicando D.

Os tres sao INTERIORES a uniao das grades varridas (base 0.15..0.9,
gain 0.6..1.0, renew 0.0..1.0) — nenhum em fronteira.

`fig7a` precisa de CHAVE NOVA `LIU_2022_RETIGHT_direct`, nomeada pelo
PROTOCOLO e nao pela figura: o token `direct` so ocorre nos 4 cids dela, e o
prefixo `LIU_2022_RETIGHT` e' mais longo que `LIU_2022_RET`, logo vence sem
empate (validado no D-F: 6 doses, controle bit-identico nas 6).

    py -3.12 New_Theory/liu2022_relogio_adota.py [--dry]
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

CFG = ROOT / "New_Theory" / "adopted_configs.json"
BASE, GAIN, RENEW = 0.45, 0.88, 0.65
FIG8 = "LIU_2022_RETIGHT_fig8"
DIRECT = "LIU_2022_RETIGHT_direct"
CIDS = ([f"liu2022_fig8_multi_t{k}" for k in range(5)]
        + [f"liu2022_fig7a_oil_direct_t{k}" for k in range(4)])

PROV = (
    "relogio por CONTAGEM DE REAPERTOS (D-L, 2026-08-05; preregs "
    "2026-08-05-liu2022-relogio-{por-reaperto,composicao-corrigida,"
    "tres-compartilhados}). Perda dirigida por SLIP x base*(1+gain)^(n-1) "
    "para n>=1, e 1.0 exato em n=0 (estagio virgem protegido POR CONSTRUCAO). "
    "Fisica: num protocolo que NAO solta o parafuso a interface segue "
    "engajada; o 1o reaperto a assenta (perde ~2x menos) e cada reaperto "
    "seguinte a re-danifica (~1.9x por evento). Medido no dado: a perda POR "
    "ESTAGIO cresce 1.75x/2.03x (fig8 seco) e 1.49x/2.03x (fig7a oleo), e e' "
    "plana ou DECRESCENTE nos dois protocolos que SOLTAM (fig6a 1.09/1.17; "
    "fig6b 0.75/0.93). OS TRES NUMEROS SAO COMPARTILHADOS entre seco e oleo — "
    "as diferencas por lubrificacao saem do c_D ja adotado, porque "
    "k_emb_renew multiplica D. Gates: G1 transferencia (as DUAS cadeias "
    "melhoram) em 14 de 24 celulas; G2 virgem bit-identico; G3 as 8 curvas "
    "que soltam bit-identicas; G4 zero violacoes; G5 fecham t1, t2 E t4. "
    "Os 3 valores sao INTERIORES a uniao das grades (disciplina "
    "bounds_saturated: a 1a grade saturou em base=0.45 e foi estendida 2x). "
    "FALSIFICACOES no caminho, registradas: k_gall INERTE por construcao "
    "(so age em tightening_torque, e o F0 por estagio e' lido do dado); "
    "amplificador puro (1+g)^n morto por ALGEBRA (contradominio [1,inf), e o "
    "fator necessario e' <1); slip isolado morto por TETO DE AUTORIDADE "
    "(0.460 contra alvo 0.203).")


def main() -> int:
    d = json.loads(CFG.read_text(encoding="utf-8"))
    src = d["sources"]
    if FIG8 not in src:
        print(f"!! grupo ausente: {FIG8}")
        return 2
    novo = {**json.loads(json.dumps(src["LIU_2022_RET"]))}   # base oil
    print(f"{FIG8}: += base/gain/renew")
    print(f"{DIRECT}: chave NOVA (protocolo 'direct'), clonada de LIU_2022_RET")
    print(f"  valores: base={BASE} gain={GAIN} renew={RENEW}")
    if "--dry" in sys.argv:
        print("--dry: nada escrito")
        return 0

    bkp = CFG.with_suffix(".json.bkp_dl")
    shutil.copy2(CFG, bkp)
    for chave, node in ((FIG8, src[FIG8]), (DIRECT, novo)):
        cfg = node["cfg"]
        cfg["retight_loss_base"] = BASE
        cfg["retight_loss_gain"] = GAIN
        cfg["k_emb_renew"] = RENEW
        prov = node.setdefault("prov", {})
        prov["retight_loss_base"] = PROV
        prov["k_emb_renew"] = (
            f"D-L 2026-08-05: 1.0 -> {RENEW}. Renovacao PARCIAL do "
            "assentamento no reaperto sem soltar. Valor COMPARTILHADO com o "
            "grupo do outro protocolo sem-soltar; a diferenca por lubrificacao "
            "vem do c_D (multiplica D nesta mesma expressao).")
    novo["prov"]["grupo"] = (
        "protocolo DIRETO (paper: 'retightened directly to torque', restaura "
        "so 88-90% de F0) — chave nomeada pelo PROTOCOLO, nao pela figura. O "
        "token 'direct' so ocorre nos 4 cids do fig7a; prefixo mais longo que "
        "LIU_2022_RET vence sem empate. Separa-o do fig6b (mesma lubrificacao, "
        "protocolo RELEASE: solta 30-60 graus, restaura ~100%).")
    novo["verdict"] = (
        "D-L 2026-08-05: recebe o relogio por reaperto junto com o fig8. As 4 "
        "curvas estavam no tripe ANTES e seguem, com MAE caindo de "
        "0.0149/0.0130/0.0069/0.0101 para 0.0149/0.0046/0.0028/0.0016 — foi "
        "esta cadeia, de OUTRA lubrificacao, que serviu de teste de "
        "transferencia do G1.")
    src[DIRECT] = novo
    CFG.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nbackup {bkp.name} · adopted_configs.json escrito")

    import importlib
    import bolt_analysis_studio.calibration.knowledge_base as kb
    importlib.reload(kb)
    import bolt_analysis_studio.validation.runner as rn
    importlib.reload(rn)
    from bolt_analysis_studio.validation.case_registry import record

    probe = json.loads((ROOT / "New_Theory" /
                        "liu2022_relogio_ext2_exec.json").read_text(
                            encoding="utf-8"))
    cel = next((g for g in probe["grade"]
                if abs(g["base"] - BASE) < 1e-12 and abs(g["gain"] - GAIN) < 1e-12
                and abs(g["renew"] - RENEW) < 1e-12), None)
    if cel is None:
        print("!! celula ausente no JSON da sonda")
        return 2
    print("\nverificacao (vs sonda):")
    ruim = []
    for cid in CIDS:
        r = rn.simulate_case(record(cid))
        if not r.ok:
            print(f"  !! {cid}: {r.error}")
            return 2
        e = cel["vals"][cid]
        dd = max(abs(r.mae - e["mae"]), abs(r.maxerr - e["mx"]),
                 abs(r.resid_std - e["sd"]))
        flag = "OK" if dd < 1e-9 else "DIVERGE"
        if flag != "OK":
            ruim.append(cid)
        tripe = r.mae <= 0.05 and r.maxerr <= 0.10 and r.resid_std <= 0.025
        print(f"  {flag:8s} {'[tripe]' if tripe else '[ fora]'} {cid:34s} "
              f"mae {r.mae:.4f} mx {r.maxerr:.4f} sig {r.resid_std:.4f}")
    if ruim:
        print("\n!! ABORTAR — nao reproduz a sonda. Restaure o backup.")
        return 3
    print("\nadocao CONFIRMADA ao 1e-9. Proximo: re-stamp uniforme do store.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
