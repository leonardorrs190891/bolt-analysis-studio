"""Atribui a perda de pré-carga (dF_0) de cada ciclo a cada mecanismo e
agrega o share por estágio."""
from __future__ import annotations

from typing import Dict, List, Optional

from .segmentation import StageSegmentation


class MechanismDecomposition:
    @staticmethod
    def shares_per_segment(history: List, segmentation: StageSegmentation
                           ) -> Dict[str, Optional[dict]]:
        """Para cada estágio, soma |dF_0| por mecanismo sobre os ciclos
        daquele estágio e devolve shares (somam 1.0) + dominante. Estágio
        sem ciclos → None."""
        # acumula |dF_0| por estagio -> mecanismo
        acc: Dict[str, Dict[str, float]] = {s.name: {} for s in segmentation.stages}
        for snap in history:
            stage = segmentation.segment_of(snap.cycle)
            bucket = acc[stage]
            for mech, dF in snap.dF_0_by_mech.items():
                bucket[mech] = bucket.get(mech, 0.0) + abs(dF)
        out: Dict[str, Optional[dict]] = {}
        for name, bucket in acc.items():
            total = sum(bucket.values())
            if total <= 0.0:
                out[name] = None
                continue
            shares = {m: v / total for m, v in bucket.items()}
            dominant = max(shares, key=shares.get)
            out[name] = {"shares": shares, "dominant": dominant}
        return out
