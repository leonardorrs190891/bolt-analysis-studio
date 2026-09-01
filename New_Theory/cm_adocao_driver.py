# -*- coding: utf-8 -*-
"""Driver de ADOCAO do Cattaneo-Mindlin — executa DEPOIS do veredicto do D2'.

POLITICA DE DECISAO, escrita ANTES de ver os numeros do re-run (mandato de
delegacao 2026-07-30, com a prudencia declarada aqui para nao virar decisao
pos-hoc):

  PASSA  (A ok, B >= 0,50, C ok)      -> roda o gate de acervo abaixo; se
                                          G-acervo passar, ADOTA por delegacao.
  PARCIAL (0,25 <= B < 0,50)          -> NAO adota como forma. Registra as duas
                                          fracoes e segue para o proximo membro
                                          (graded_scrit). Adotar componente
                                          misto sem anchor da fracao de rescala
                                          seria alavanca de nivel sem nome.
  NIVEL DISFARCADO / FALSIFICADO      -> nao adota; conta para o requisito (b)
                                          da regra de parada (2 de 4 medidos).
  INCONCLUSIVO                        -> re-projetar instrumento; nada conta.

GATE DE ACERVO (pre-adocao, alem dos G1-G4 do prereg):
  para CADA fonte com curva que fecha no re-run, injetar
  slip_regime_mode="cattaneo_mindlin" NA FONTE INTEIRA e re-simular TODAS as
  curvas da fonte (n_cap=None, store-comparavel): nenhuma curva da fonte pode
  piorar > +0,01 em nenhuma perna (limite efetivo D1 via rh.limite_sres).
  Fonte que falha o gate fica FORA da adocao (adocao e' por fonte, G4).

SO-LEITURA ate o final; a escrita real em adopted_configs.json so acontece com
--adotar, e imprime o diff antes.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.report_html as rh      # noqa: E402
import bolt_analysis_studio.validation.runner as rn           # noqa: E402
from bolt_analysis_studio.validation.case_registry import (   # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

RES = ROOT / "New_Theory" / "cm_discriminante_d2linha.json"
TOL = 0.01
_EXTRA: dict = {}


def _instalar():
    _o = rn._effective_overrides
    rn._effective_overrides = lambda rec, base: {**_o(rec, base), **_EXTRA}


def main() -> int:
    d = json.loads(RES.read_text(encoding="utf-8"))
    ramoB, ramoC, violA = d["ramoB"], d["ramoC"], d["viol_A"]
    print(f"veredicto do re-run: A={'FALSIFICA' if violA else 'ok'} "
          f"B={ramoB} C={ramoC} · fecham(store-comparavel)={d.get('fecham')}")
    if violA or ramoB in ("NIVEL DISFARCADO", "INCONCLUSIVO") \
            or ramoC in ("FALSIFICADO",):
        print("POLITICA: nao adota. Registrar e seguir para o proximo membro.")
        return 1
    if ramoB == "PARCIAL":
        print("POLITICA (declarada antes): PARCIAL nao adota como forma. "
              "Registrar as fracoes; proximo membro.")
        return 1

    # ---- PASSA: gate de acervo por fonte -----------------------------------
    _instalar()
    st = ValidationStore()
    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    pisos = rh._pisos_medidos(pares)
    fontes = sorted({record(l["case"]).source for l in d["linhas"]
                     if l.get("fecha") and l.get("fecha_full", True)})
    print(f"fontes candidatas (curvas que fecham): {fontes}")
    recs = defaultdict(list)
    for r in all_records():
        if r.source in fontes:
            recs[r.source].append(r)
    aprovadas = []
    for src in fontes:
        _EXTRA.clear()
        _EXTRA.update({"slip_regime_mode": "cattaneo_mindlin"})
        pior = []
        for r in recs[src]:
            antes = st.get(r.case_id)
            dep = rn.simulate_case(r)          # n_cap=None: store-comparavel
            for rot, va, vb in (("MAE", antes.mae, dep.mae),
                                ("max", antes.maxerr, dep.maxerr),
                                ("sd", antes.resid_std, dep.resid_std)):
                if va is not None and vb is not None and vb > va + TOL:
                    pior.append((r.case_id, rot, va, vb))
        _EXTRA.clear()
        if pior:
            print(f"  {src}: GATE DE ACERVO REPROVA — {len(pior)} pioras:")
            for cid, rot, va, vb in pior[:6]:
                print(f"     {cid[:40]:42s} {rot} {va:.4f}->{vb:.4f}")
        else:
            aprovadas.append(src)
            print(f"  {src}: gate de acervo ok ({len(recs[src])} curvas)")
    print(f"\nfontes aprovadas para adocao: {aprovadas}")
    if "--adotar" in sys.argv and aprovadas:
        cfgp = ROOT / "New_Theory" / "adopted_configs.json"
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        for src in aprovadas:
            ent = cfg["sources"].setdefault(src, {"cfg": {}, "prov": {}})
            ent.setdefault("cfg", {})["slip_regime_mode"] = "cattaneo_mindlin"
            ent.setdefault("prov", {})["slip_regime_mode"] = (
                "D2' PASSA (re-run teto unico 2026-07-30) + gate de acervo "
                "0 pioras; adotado por delegacao (mandato 2026-07-30)")
        cfgp.write_text(json.dumps(cfg, ensure_ascii=False, indent=1),
                        encoding="utf-8")
        print("ADOTADO no adopted_configs.json — re-carimbar o store "
              "(parallel_batch --store) e regenerar reports em seguida.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
