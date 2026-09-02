"""Persistencia dos canais de override do MSDModel (2026-09-02).

MEDIDO no dia: um modelo de caso da validacao sai do `build_case_model` com 23
constantes adotadas em `_v2_tuner_overrides` e 8 em `_v2_geometry_overrides`, e
salvar + reabrir devolvia 0 e 0. O modelo PARECIA correto (os 11 elementos
voltavam, F0 e mu sobreviviam, porque sao campos de verdade), mas as constantes
que fazem a curva bater com o experimento desapareciam em silencio. O solver
honra os dois canais (solver_worker.py:1071 e :1092, onde o comentario diz que
override explicito VENCE), logo a perda muda resultado.

O formato ja' serializava `two_stage_overrides` e `fixture_overrides`: dois
canais salvos, dois nao. Estes testes travam a simetria.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from bolt_analysis_studio.core.models.model import MSDModel     # noqa: E402


def test_roundtrip_preserva_os_dois_canais_v2(tmp_path):
    m = MSDModel(name="caso")
    m._v2_tuner_overrides = {"mu_thread": 0.18, "C_creep": 3.2e-9, "emb_depth": 1.1e-6}
    m._v2_geometry_overrides = {"grip_length_m": 0.025, "d_bolt_m": 0.008}

    alvo = tmp_path / "caso.msd"
    m.save(str(alvo))
    de_volta = MSDModel.load(str(alvo))

    assert getattr(de_volta, "_v2_tuner_overrides", {}) == m._v2_tuner_overrides
    assert getattr(de_volta, "_v2_geometry_overrides", {}) == m._v2_geometry_overrides


def test_modelo_sem_override_nao_ganha_atributo_vazio(tmp_path):
    """Ausencia tem de continuar ausencia: um dict vazio ligaria o ramo de
    override no solver com nada dentro."""
    m = MSDModel(name="limpo")
    alvo = tmp_path / "limpo.msd"
    m.save(str(alvo))
    de_volta = MSDModel.load(str(alvo))
    assert not getattr(de_volta, "_v2_tuner_overrides", None)
    assert not getattr(de_volta, "_v2_geometry_overrides", None)


def test_todo_canal_de_override_que_o_solver_le_esta_serializado():
    """A varredura que impede a repeticao: procura no solver_worker os
    atributos `_*_overrides` lidos do modelo e exige que to_dict() grave cada
    um. Um terceiro canal amanha quebra aqui, e nao na maquina do usuario."""
    import re

    fonte = (RAIZ / "src" / "bolt_analysis_studio" / "core" / "solver_worker.py"
             ).read_text(encoding="utf-8", errors="replace")
    lidos = set(re.findall(r"['\"](_\w*_overrides)['\"]", fonte))
    assert lidos, "nenhum canal de override encontrado no solver"

    m = MSDModel(name="x")
    for canal in lidos:
        setattr(m, canal, {"sentinela": 1.0})
    d = m.to_dict()
    faltando = [c for c in lidos if c.lstrip("_") not in d]
    assert not faltando, (
        f"o solver le {sorted(lidos)} mas to_dict() nao grava "
        f"{sorted(faltando)}: salvar perderia esses valores em silencio")
