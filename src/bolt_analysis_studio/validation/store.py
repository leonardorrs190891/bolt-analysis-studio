# -*- coding: utf-8 -*-
"""Cache persistente dos resultados de validacao (spec §3): um JSON com um
CaseResult por caso + fingerprint do engine. Seed inicial importado da galeria
(report_data.json) para consulta instantanea — marcado 'gallery-seed' e sempre
stale (a primeira re-simulacao o substitui e preenche a decomposicao)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .case_registry import all_records
from .inputs import repo_root
from .runner import CaseResult, engine_fingerprint

_DEFAULT = "Models/CALIBRATION_AND_VALIDATION/validation_store.json"


class ValidationStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else repo_root() / _DEFAULT
        self._data: Dict[str, dict] = {}
        self.load()

    def load(self) -> None:
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                self._data = {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._data, ensure_ascii=False),
                       encoding="utf-8")
        tmp.replace(self.path)                    # escrita atomica (padrao profiles.py)

    def get(self, case_id: str) -> Optional[CaseResult]:
        d = self._data.get(case_id)
        return CaseResult.from_dict(d) if d else None

    def put(self, result: CaseResult) -> None:
        self._data[result.case_id] = result.to_dict()

    def all_ids(self) -> List[str]:
        return sorted(self._data)

    def is_stale(self, case_id: str) -> bool:
        d = self._data.get(case_id)
        if not d:
            return True
        return d.get("engine_fingerprint") != engine_fingerprint()

    def seed_from_gallery(self) -> int:
        """Importa as entradas da galeria (via registry — so records com
        gallery_entry, chave = case_id) como resultados 'gallery-seed' (sem
        decomposicao; sempre stale). Nao sobrescreve resultados reais."""
        n = 0
        for rec in all_records():
            e = rec.gallery_entry
            if e is None:
                continue
            cur = self._data.get(rec.case_id)
            if cur and cur.get("engine_fingerprint") != "gallery-seed":
                continue                          # resultado real vence o seed
            self._data[rec.case_id] = CaseResult(
                case_id=rec.case_id, ok=True,
                cycles=[float(x) for x in e["model"]["x"]],
                ratio=[float(y) for y in e["model"]["y"]],
                mae=float(e["mae"]),
                rmse=float(e.get("rmse_interp") or 0) or None,
                maxerr=float(e.get("maxerr_interp") or 0) or None,
                maxerr_at=float(e.get("maxerr_at") or 0) or None,
                final_pred=float(e["model"]["y"][-1]),
                final_data=float(e["data"]["y"][-1]),
                config_used=dict(label=e.get("label", ""),
                                 amp_mm=e.get("amp_mm")),
                generated_at="(campanha)",
                engine_fingerprint="gallery-seed").to_dict()
            n += 1
        return n
