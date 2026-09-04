"""Toda entrada `per_case` tem procedência — no config ou na colheita.

## O que este arquivo impede

Uma constante por curva entrar no `adopted_configs.json` **sem que ninguém diga de
onde ela veio**. Hoje isso é possível porque `prov` é opcional, e o resultado medido
em 2026-08-25 foi **147 entradas** `(grupo, token, campo)` sem procedência declarada.

⚠️ **Mas o diagnóstico inicial estava errado, e era meu:** eu disse que declará-las
exigia *"ler os papers"*. Não exigia — a leitura já tinha sido feita. Cada uma entrou
por um pré-registro que declara a origem; o campo `prov` é que nunca foi preenchido.
`New_Theory/colheita_de_procedencia.py` recupera as 147 com a **citação do documento**
em cada uma.

## E a decomposição que mudou o tamanho do problema

Das 147, **63 não são constantes**: 45 são **canais desligados** (`s_crit_loose=0`,
`emb_depth=0`…) e 18 são **seletores de forma** (`loose_rate_mode="graded_scrit"`).
Só **84** são valores que pedem procedência de verdade. Publicar "147 sem procedência"
sem separar as classes foi o mesmo modo de falha dos *"40 grupos de uma curva só"*, que
eram **10**.

## Por que a colheita não está fundida ao config

`engine_fingerprint()` hasheia `adopted_config(s)` **inteiro** — incluindo `prov`.
Fundir muda o fingerprint e obriga a re-carimbar os 207 registros do store: é operação
de adoção, single-writer. O teste vigia o **par** (config + colheita), que é o estado
real do conhecimento, e não força a fusão.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from bolt_analysis_studio.calibration import knowledge_base as kb

RAIZ = Path(__file__).resolve().parents[1]
MAPA = RAIZ / "New_Theory" / "procedencia_colhida.json"


def _sem_prov():
    """[(grupo, token, campo, valor)] sem `prov` no config."""
    fora = []
    for s in sorted(kb.adopted_sources()):
        e = kb.adopted_config(s) or {}
        c = e.get("cfg") or {}
        prov = e.get("prov") or {}
        for tok, d in sorted((c.get("per_case") or {}).items()):
            if not isinstance(d, dict):
                continue
            for campo, val in sorted(d.items()):
                if campo not in prov:
                    fora.append((s, tok, campo, val))
    return fora


@pytest.fixture(scope="module")
def colheita():
    if not MAPA.exists():
        pytest.skip("colheita não gerada — rode "
                    "`py -3.12 New_Theory/colheita_de_procedencia.py`")
    return json.loads(MAPA.read_text(encoding="utf-8"))


def test_toda_entrada_per_case_TEM_prov_no_config():
    """Invariante pós-fusão (2026-08-28, decisão do professor "resolva todas").

    A colheita de 2026-08-25 foi fundida ao `adopted_configs.json`, e desde
    então a barra subiu: NENHUMA entrada `per_case` pode existir sem `prov` no
    próprio config. O teste antigo (abaixo) aceitava "no config OU na colheita";
    este exige o config. Se falhar, uma constante por curva entrou sem
    procedência — declare-a no `prov` do grupo (operação single-writer: muda o
    `engine_fingerprint` e exige re-carimbo do store).
    """
    fora = _sem_prov()
    assert not fora, (
        f"{len(fora)} entrada(s) `per_case` sem `prov` no config:\n  "
        + "\n  ".join(f"{s} · {t} · {c}" for s, t, c, _v in fora[:8]))


def test_toda_entrada_sem_prov_esta_na_COLHEITA(colheita):
    """O invariante central: nenhuma constante por curva fica órfã.

    Se falhar, uma entrada `per_case` nova entrou sem procedência **e** sem
    colheita — é dívida voltando em silêncio, que é como ela chegou a 147.
    """
    orfas = [(s, tok, campo) for s, tok, campo, _v in _sem_prov()
             if campo not in colheita.get(s, {})]
    assert not orfas, (
        f"{len(orfas)} entrada(s) `per_case` sem procedência no config E sem "
        f"colheita:\n  "
        + "\n  ".join(f"{s} · {t} · {c}" for s, t, c in orfas[:8])
        + "\n\nOu declare `prov` no config, ou acrescente à COLHEITA em "
          "`New_Theory/colheita_de_procedencia.py` — com a CITAÇÃO do documento "
          "que registra a origem. Sem citação não entra.")


def test_toda_procedencia_colhida_CITA_um_documento(colheita):
    """Procedência sem fonte é opinião.

    ⚠️ Exceções deliberadas: (a) *canal desligado* — a procedência é a própria
    decisão de desligar, e não há paper a citar; (b) entradas *"idem"*, que
    apontam para a irmã que traz o texto completo.
    """
    sem_cit = []
    for g, campos in colheita.items():
        for campo, txt in campos.items():
            if "DESLIGADO" in txt or txt.strip().startswith(("idem", "mesma")):
                continue
            if "[" not in txt:
                sem_cit.append((g, campo, txt[:60]))
    assert not sem_cit, (
        "procedência sem citação de documento: "
        + "; ".join(f"{g}·{c}" for g, c, _t in sem_cit[:6]))


def test_a_colheita_NAO_escreve_no_config():
    """O script é só-leitura. Fundir muda o fingerprint e exige re-carimbo.

    Teste estrutural: o fonte não pode abrir `adopted_configs.json` para escrita.
    """
    import ast
    src = (RAIZ / "New_Theory" / "colheita_de_procedencia.py").read_text(
        encoding="utf-8")
    # ⚠️ Verificar por MENÇÃO seria errado — o script cita o config em prosa
    # (docstring e aviso), e a 1ª versão deste teste reprovava por isso. O que
    # importa são os ALVOS DE ESCRITA: percorre a AST e coleta todo
    # `X.write_text(...)` / `open(X, "w")`.
    alvos = []
    for no in ast.walk(ast.parse(src)):
        if not isinstance(no, ast.Call):
            continue
        f = no.func
        nome = f.attr if isinstance(f, ast.Attribute) else (
            f.id if isinstance(f, ast.Name) else "")
        if nome == "write_text":
            alvos.append(ast.unparse(f.value))
        elif nome == "open" and len(no.args) > 1:
            m = ast.unparse(no.args[1])
            if "w" in m or "a" in m:
                alvos.append(ast.unparse(no.args[0]))
    assert alvos, "a colheita não escreve nada — o mapa deixou de ser gerado?"
    ruins = [a for a in alvos if "adopted" in a.lower()]
    assert not ruins, (
        f"a colheita ESCREVE no config: {ruins}. Fundir é operação de adoção "
        f"(muda o `engine_fingerprint`, exige re-carimbar os 207 e janela "
        f"single-writer), não passo de script.")


def test_o_script_roda_e_declara_ZERO_pendente():
    """Executa a colheita e exige que ela cubra tudo.

    Roda o script de verdade: um mapa que existe mas não cobre o estado atual é
    pior que mapa nenhum, porque parece cobertura.
    """
    r = subprocess.run(
        [sys.executable, str(RAIZ / "New_Theory" / "colheita_de_procedencia.py")],
        capture_output=True, text=True, cwd=str(RAIZ), encoding="utf-8",
        errors="replace")
    assert r.returncode == 0, f"a colheita falhou:\n{r.stderr[-800:]}"
    # a ancora e' ASCII de proposito: com pipe no Windows o filho escreve
    # cp1252 e este teste decodifica utf-8 — um acento aqui faz o assert
    # depender do ambiente (passava com PYTHONIOENCODING herdado, falhava sem).
    assert "SEM procedencia: 0" in r.stdout, (
        f"a colheita reporta pendências:\n{r.stdout[-600:]}")


def test_as_classes_estao_separadas(colheita):
    """63 das 147 NÃO são constantes — e a colheita tem de dizer isso.

    Canal desligado e seletor de forma contados como "constante sem procedência"
    foi o que inflou o número publicado. A colheita os rotula explicitamente.
    """
    txts = [t for g in colheita.values() for t in g.values()]
    assert any("DESLIGADO" in t for t in txts), (
        "sumiu o rótulo de canal desligado — sem ele os zeros voltam a contar "
        "como constante ajustada")
    assert any("FORMA adotada" in t for t in txts), (
        "sumiu o rótulo de forma; `loose_rate_mode` é escolha de mecanismo, "
        "não valor fitado")
