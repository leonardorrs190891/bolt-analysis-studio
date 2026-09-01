# -*- coding: utf-8 -*-
"""A parada é PROVISÓRIA — e este teste é o que faz "reabre automaticamente" ter sujeito.

## O defeito que ele impede

`New_Theory/regra_de_parada_proposta.md` diz que a parada reabre automaticamente
se o `engine_fingerprint` mudar, se um instrumento novo mudar a decomposição, se
o `n` ou o piso de qualquer curva da fila mudar, ou se a régua mudar.

**Isso é prosa, e prosa não reabre nada.** É exatamente a classe de defeito que a
§4.43 nomeia e que `test_meta_numeros_nao_envelhecem` combate no censo: sem
âncora, a afirmação sobrevive à sua própria validade. Uma parada não vigiada não
"expira" — ela vira permanente em silêncio, e é o pior desfecho possível, porque
uma decisão de PARAR sem reabertura é indistinguível de abandono.

## Como ele se comporta (e por que não é alarme falso)

Ele **não** falha a cada adoção. Ele falha quando um gatilho de reabertura
disparou **e o baseline não foi reexaminado**. O conserto é uma linha em
`parada_baseline.json`:

```json
"reexaminado_em": "<fingerprint novo> — <o que mudou e se a parada segue válida>"
```

Ou seja: a adoção seguinte não é bloqueada, mas **obriga um reconhecimento
consciente** de que a parada foi medida contra outro estado. Foi assim que o
`test_meta_numeros_nao_envelhecem` conseguiu ser exigente sem ser desligado — o
custo de satisfazê-lo é escrever o que mudou, não desfazer o trabalho.

Regenerar o baseline: `py -3.12 New_Theory/parada_baseline.py --gravar`.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ / "New_Theory" / "parada_baseline.json"


def _baseline() -> dict:
    if not BASE.exists():
        pytest.skip("sem `parada_baseline.json` — nenhuma parada foi medida ainda")
    return json.loads(BASE.read_text(encoding="utf-8"))


def _agora() -> dict:
    import sys
    sys.path.insert(0, str(RAIZ / "New_Theory"))
    import parada_baseline
    return parada_baseline.medir()


def _reconhecido(b: dict) -> bool:
    """O baseline declara ter sido reexaminado depois do gatilho?"""
    r = b.get("reexaminado_em")
    return bool(r) and len(str(r)) > 20      # exige a razão, não só um hash


def test_fingerprint_da_parada_ainda_vale():
    """Gatilho 1 — o fingerprint. É o mais frequente e o mais fácil de ignorar."""
    b, a = _baseline(), _agora()
    if b["fingerprint"] == a["fingerprint"] or _reconhecido(b):
        return
    pytest.fail(
        f"A parada foi medida contra {b['fingerprint']} e o store está em "
        f"{a['fingerprint']}. A regra manda REABRIR. Se a parada segue válida, "
        "diga-o explicitamente em `parada_baseline.json` -> `reexaminado_em` "
        "(fingerprint novo + o que mudou), ou regenere o baseline com "
        "`py -3.12 New_Theory/parada_baseline.py --gravar` e re-meça o veredito "
        f"em {b['documento']}.")


def test_regua_da_parada_ainda_vale():
    """Gatilho 2 — a régua. Se os limites mudam, a fila muda de significado.

    Precedente: em 2026-07-29 a régua foi de 2 para 3 pernas e **nove arquivos**
    seguiram publicando a leitura vencida.
    """
    b, a = _baseline(), _agora()
    if b["regua"] == a["regua"] or _reconhecido(b):
        return
    dif = {k: (b["regua"].get(k), a["regua"].get(k))
           for k in set(b["regua"]) | set(a["regua"])
           if b["regua"].get(k) != a["regua"].get(k)}
    pytest.fail(f"a régua mudou desde a parada: {dif} — a fila muda de "
                "significado e o veredito tem de ser re-medido")


def test_dado_da_fila_ainda_vale():
    """Gatilho 3 — `n` ou piso de qualquer curva da fila.

    É o gatilho que DADO NOVO dispara, e o único cuja ativação é uma **boa**
    notícia: réplica nova muda o piso da fonte e pode destravar a curva.
    """
    b, a = _baseline(), _agora()
    if _reconhecido(b):
        return
    fb, fa = b["fila_julgavel"], a["fila_julgavel"]
    ruins = []
    for cid, v in fb.items():
        if cid not in fa:
            ruins.append(f"{cid}: saiu da fila julgável (fechou? mudou de estatuto?)")
            continue
        for campo in ("n_pontos", "piso_fonte", "limite_sigma"):
            if v[campo] != fa[cid][campo]:
                ruins.append(f"{cid}: {campo} {v[campo]} -> {fa[cid][campo]}")
    for cid in fa:
        if cid not in fb:
            ruins.append(f"{cid}: ENTROU na fila julgável depois da parada")
    assert not ruins, (
        "o dado da fila mudou desde a parada — a regra manda REABRIR:\n  "
        + "\n  ".join(ruins))


def test_baseline_nomeia_o_documento_do_veredito():
    """Uma parada sem o documento que a mediu é um número órfão.

    Guarda estrutural: barata, e impede que o baseline sobreviva ao registro que
    lhe dá sentido (o modo de falha do `_FORMA_NOMEADA` sem doc, corrigido em
    2026-08-16).
    """
    b = _baseline()
    doc = RAIZ / b.get("documento", "")
    assert b.get("documento"), "`parada_baseline.json` sem `documento`"
    assert doc.exists(), f"o documento do veredito não existe: {b['documento']}"
    assert b.get("fila_julgavel"), "baseline sem fila — nada estaria sendo vigiado"
