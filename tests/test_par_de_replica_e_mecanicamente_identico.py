# -*- coding: utf-8 -*-
"""Um par de RÉPLICA declarado tem de ser mecanicamente a MESMA junta.

## Por que este arquivo existe

O piso de repetibilidade por fonte (D1, adotado 2026-07-30) define o limite da
3ª perna. Ele é medido em **pares de réplica**, e um par inválido não mede
repetibilidade — mede a diferença entre duas juntas diferentes, o que **infla o
piso** e afrouxa a barra da fonte inteira.

Isso não é hipotético: a campanha já **invalidou seis pareamentos**, cada um
depois de ter sido usado para assinar exceção —

* `ROUSSEAU_2025` (2026-08-04): par aço `t10`↔`t12`, **espessuras** diferentes;
  3 exceções FORTE retratadas.
* `CACCESE_2009` (2026-08-04): chave mecânica cega juntava as 7 condições da
  fonte; 1 exceção retratada.
* `LU_2024` (2026-07-31): par cruzava **0,5 × 1,0 mm** de amplitude.
* `LU_2024` (2026-08-14): pares cruzavam **protocolos** (§3.1.3 × §3.2);
  5 exceções F7 retratadas.
* `ICMEZ_2025` (2026-08-14): pareava **grip 13,8 × 19,8 mm** nas 4 famílias.
* `CHU_2026` (2026-08-14): pareava **Ra 1,6 × 0,4 µm** via config default.

Toda vez o defeito foi o mesmo: **duas juntas fisicamente distintas tratadas
como réplicas**. Este teste transforma essa lição em invariante.

## O que ele exige, e por que ESTES campos

Medido nos 5 pares declarados vigentes (2026-08-16): `grip_mm`, `bolt_size`,
`rz`, `mu`, `mode`, `frequency_hz` e o drive (`delta_mm`) são **idênticos em
5/5**. São a geometria, a tribologia e o acionamento — o que define *qual junta
é* e *como ela é excitada*.

⚠️ **A CARGA fica de fora, de propósito.** O par `karlsen2022_M30_HV_run2p2` ×
`run7p1` difere em F₀ (**333 × 312 kN**, 6,7 %) e a razão declarada diz isso
com todas as letras: *"mesma condição nominal, F₀ alcançado 333 × 313 kN"*.
Réplica de ensaio tensionado **tem** dispersão de pré-carga alcançada — e essa
dispersão é parte do que o piso mede. Exigir F₀ idêntico proibiria o par certo.
O que se exige é que a diferença seja **pequena** (≤ 10 %, contra os 6,7 %
medidos): acima disso não é dispersão de aperto, é outra condição.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
STORE = RAIZ / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"

# Geometria + tribologia + acionamento: o que define QUAL junta é.
IDENTICOS_CFG = ("grip_mm", "rz", "mu", "mode", "delta_mm")
IDENTICOS_CASE = ("bolt_size", "frequency_hz")
# Carga: pode variar por dispersão de aperto, mas pouco.
TOL_CARGA = 0.10


def _store() -> dict:
    d = json.loads(STORE.read_text(encoding="utf-8"))
    return d.get("cases", d)


def _pares():
    import bolt_analysis_studio.validation.report_html as rh
    return list(rh._PARES_REPLICA_DECLARADOS)


def _cfg(store, cid, campo):
    return (store.get(cid, {}).get("config_used") or {}).get(campo)


def _case(cid, campo):
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = {r.case_id: r for r in all_records()}
    return getattr(recs[cid].validation_case, campo, None)


def test_par_declarado_e_a_mesma_junta():
    """Geometria, tribologia e drive idênticos nos dois lados do par."""
    store = _store()
    ruins = []
    for a, b, why in _pares():
        for campo in IDENTICOS_CFG:
            va, vb = _cfg(store, a, campo), _cfg(store, b, campo)
            if va != vb:
                ruins.append(f"{a} x {b}: {campo} {va!r} != {vb!r}")
        for campo in IDENTICOS_CASE:
            va, vb = _case(a, campo), _case(b, campo)
            if va != vb:
                ruins.append(f"{a} x {b}: {campo} {va!r} != {vb!r}")
    assert not ruins, (
        "par de RÉPLICA que não é a mesma junta — isto infla o piso da fonte e "
        "afrouxa a 3ª perna para todas as curvas dela:\n  " + "\n  ".join(ruins))


def test_carga_pode_variar_mas_pouco():
    """Dispersão de aperto é esperada; condição diferente, não.

    Sem este teste, "mesma condição nominal" viraria porta para parear cargas
    arbitrariamente distintas — que foi exatamente o defeito do par
    `fig18_amp0p5`×`fig20_T22Nm` (0,5 × 1,0 mm), retratado em 2026-07-31.
    """
    store = _store()
    ruins = []
    for a, b, why in _pares():
        for campo in ("F_amp_N",):
            va, vb = _cfg(store, a, campo), _cfg(store, b, campo)
            if not (isinstance(va, (int, float)) and isinstance(vb, (int, float))):
                continue
            if max(va, vb) <= 0:
                continue
            rel = abs(va - vb) / max(abs(va), abs(vb))
            if rel > TOL_CARGA:
                ruins.append(f"{a} x {b}: {campo} {va} vs {vb} ({rel:.0%} > "
                             f"{TOL_CARGA:.0%}) — razão declarada: {why[:80]}")
    assert not ruins, "\n  ".join(["carga longe demais para ser réplica:"] + ruins)


@pytest.mark.parametrize("a,b,grandeza", [
    ("demir2024_amp0p3_F14p3_lk13p8", "demir2024_amp0p3_F14p3_lk19p8", "grip_mm"),
    ("demir2024_amp0p3_F17p6_lk13p8", "demir2024_amp0p3_F17p6_lk19p8", "grip_mm"),
    ("demir2024_amp0p4_F14p3_lk13p8", "demir2024_amp0p4_F14p3_lk19p8", "grip_mm"),
    ("demir2024_amp0p4_F17p6_lk13p8", "demir2024_amp0p4_F17p6_lk19p8", "grip_mm"),
    ("rousseau2025_steel_t10", "rousseau2025_steel_t12", "grip_mm"),
])
def test_pareamentos_bloqueados_seguem_bloqueados(a, b, grandeza):
    """Os pares que já foram invalidados não podem voltar como declarados.

    Guarda de REGRESSÃO com os casos reais: cada um destes foi (ou seria) usado
    como piso e difere na grandeza nomeada. O teste falha se algum reaparecer em
    `_PARES_REPLICA_DECLARADOS`, e falha **também** se a diferença sumir do
    store — porque aí o bloqueio deixou de ter base e alguém precisa reexaminá-lo
    conscientemente, em vez de o par escorregar de volta em silêncio.
    """
    store = _store()
    declarados = {frozenset((x, y)) for x, y, _ in _pares()}
    assert frozenset((a, b)) not in declarados, (
        f"o par {a} x {b} foi INVALIDADO (difere em {grandeza}) e voltou a "
        "`_PARES_REPLICA_DECLARADOS`")
    va, vb = _cfg(store, a, grandeza), _cfg(store, b, grandeza)
    assert va != vb, (
        f"{a} x {b} deixaram de diferir em {grandeza} ({va!r}): a base do "
        "bloqueio sumiu — reexamine o bloqueio em vez de assumir que segue válido")
