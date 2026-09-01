"""Load/save do joint_calibrations.json com escrita atômica (temp+rename)."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def load_profiles(path: PathLike) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_profiles(path: PathLike, data: dict) -> None:
    """Escrita atômica: grava num temp no mesmo diretório e renomeia por cima."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, str(p))   # atômico no mesmo filesystem
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def default_calibrations_path() -> Path:
    """Caminho canonico do joint_calibrations.json (New_Theory/), resolvido a
    partir do layout do repo (com ou sem src/ intermediario)."""
    root = Path(__file__).resolve().parents[3]
    if not (root / "New_Theory").exists():
        root = Path(__file__).resolve().parents[2]
    return root / "New_Theory" / "joint_calibrations.json"


def load_shared_material(path: PathLike = None) -> dict:
    """LOADER UNICO das constantes fisicas do bloco `shared` (Estagio B Fase 2,
    plano 2026-07-08 §3): Run, server e scripts leem AQUI em vez de manter
    copias hardcoded (JointMaterial defaults / conf_defaults do solver_worker /
    PHYSICAL_PRIORS). Retorna so chaves validas de JointMaterial; `emb_depth` e
    EXCLUIDO (input por junta, spec 2026-07-03 §1.3a). {} se o arquivo/bloco
    nao existir (consumidores caem nos seus fallbacks)."""
    data = load_profiles(path if path is not None else default_calibrations_path())
    consts = dict((data.get("shared") or {}).get("constants") or {})
    consts.pop("emb_depth", None)
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
    fields = JointMaterial.__dataclass_fields__
    return {k: v for k, v in consts.items() if k in fields}


def upsert_profile(path: PathLike, name: str, profile: dict) -> dict:
    data = load_profiles(path)
    if "profiles" not in data:
        data["profiles"] = {}
    data["profiles"][name] = profile
    save_profiles(path, data)
    return data


def upsert_shared(path: PathLike, shared: dict) -> dict:
    """Grava/atualiza o bloco `shared` (calibracao de fisica compartilhada,
    spec 2026-07-02 §2.6) e marca schema 2. O bloco `profiles` legado e
    preservado (o GUI continua lendo profiles durante o Estagio A)."""
    data = load_profiles(path)
    data["schema"] = 2
    data["shared"] = shared
    save_profiles(path, data)
    return data


def upsert_profiles_bundle(path: PathLike, description: str,
                           global_settings: dict, profiles: dict) -> dict:
    """Grava/atualiza o bloco de PERFIS (StagedCalibrator) SEM tocar no bloco
    `shared`/`schema` (calibracao compartilhada, Estagio A) nem em outras
    chaves de topo. Substitui o antigo `save_profiles(out)` de
    calibrate_4_profiles.py, que sobrescrevia o arquivo inteiro e apagava o
    bloco `shared`."""
    data = load_profiles(path)
    data["description"] = description
    data["global_settings"] = global_settings
    data["profiles"] = profiles
    save_profiles(path, data)
    return data
