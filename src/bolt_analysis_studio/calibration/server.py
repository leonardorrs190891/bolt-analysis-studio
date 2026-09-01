"""Servidor HTTP local que expõe o DynamicStiffnessAnalyzer real ao tuner.
Lógica em funções puras (testáveis sem socket); o handler só roteia."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, List, Optional
from urllib.parse import unquote

import numpy as np

from ..numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)
from .segmentation import StageSegmentation
from .decomposition import MechanismDecomposition
from . import profiles as P

ROOT = Path(__file__).resolve().parents[3]
TUNER_HTML = ROOT / "New_Theory" / "calibration_tuner.html"
PROFILES_JSON = ROOT / "New_Theory" / "joint_calibrations.json"
VALIDATION_DIR = ROOT / "New_Theory" / "validation_html"

_GEOM_KEYS = ["A_s", "L_eff", "d_2", "pitch", "r_bearing", "A_contact"]
_LOAD_KEYS = ["F0_init", "F_amp", "theta", "freq", "N", "delta_amp", "D_init"]

# content-type por extensao para o serving estatico de validation_html/
_CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8", ".htm": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8", ".svg": "image/svg+xml",
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".gif": "image/gif", ".csv": "text/csv; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
}


def _require(d: dict, keys: List[str], where: str):
    missing = [k for k in keys if k not in d]
    if missing:
        raise ValueError(f"payload['{where}'] faltando: {missing}")


def _geom(p) -> JointGeometry:
    _require(p.get("geom", {}), _GEOM_KEYS, "geom")
    return JointGeometry(**{k: float(p["geom"][k]) for k in _GEOM_KEYS})


def _material(p) -> JointMaterial:
    # Aceita qualquer subconjunto de campos do JointMaterial (o tuner pode
    # mandar tuners + params de dano + constantes fisicas). Resto = default.
    mat = p.get("mat")
    if not mat:
        raise ValueError("payload['mat'] ausente ou vazio")
    # ESTAGIO B Fase 3 (spec §3.3): SHIM na fronteira do server — tuners
    # legados no payload viram constantes fisicas (mesma traducao do Run).
    from .tuner_shim import translate_legacy_tuners
    mat = translate_legacy_tuners(dict(mat))
    # Coercao TYPE-AWARE (mesma disciplina do filtro de overrides do Run):
    #   str  -> passa (ex. conform_driver="effective")
    #   lista/tupla -> passa como TUPLA (ex. mu_bearing_schedule = ((N, mu), ...),
    #                  input de MEDICAO que chega do JSON como lista de listas)
    #   resto -> float()
    # Antes de 2026-07-28 o float() pegava todo campo nao-str, entao um payload
    # com `mu_bearing_schedule` levantava TypeError e derrubava o /simulate — era
    # o item 6 "LATENTE" da auditoria de 07-27, aqui reproduzido e consertado.
    # E' justamente o campo que o encanamento do mu(N) per-ciclo (fila item 5,
    # Chu2026 Fig. 5) precisa mandar pela via do tuner HTML.
    fields = JointMaterial.__dataclass_fields__

    def _seq(v) -> Any:      # lista de listas (JSON) -> tupla de tuplas
        return tuple(tuple(x) if isinstance(x, (list, tuple)) else x for x in v)

    valid = {k: float(v) for k, v in mat.items()
             if k in fields and not isinstance(v, (str, list, tuple))}
    valid.update({k: v for k, v in mat.items()
                  if k in fields and isinstance(v, str)})
    valid.update({k: _seq(v) for k, v in mat.items()
                  if k in fields and isinstance(v, (list, tuple))})
    if not valid:
        raise ValueError("payload['mat'] sem campos validos de JointMaterial")
    return JointMaterial(**valid)


def handle_simulate(p: dict) -> dict:
    geom = _geom(p)
    mat = _material(p)
    _require(p.get("loading", {}), _LOAD_KEYS, "loading")
    L = p["loading"]
    N = int(L["N"])
    ana = DynamicStiffnessAnalyzer(geom, mat, float(L["F0_init"]),
                                   initial_damage=float(L["D_init"]))
    Ns, ratio, Dtr = [0], [1.0], [float(L["D_init"])]
    separated_at = None
    for _ in range(N):
        snap = ana.step_cycle(float(L["F_amp"]), float(L["theta"]),
                              float(L["freq"]), delta_amp=float(L["delta_amp"]))
        Ns.append(snap.cycle)
        ratio.append(max(ana.state.F_0, 0.0) / float(L["F0_init"]))
        Dtr.append(snap.D)
        if separated_at is None and ana.state.F_0 <= 0.0:
            separated_at = snap.cycle
    seg = StageSegmentation(float(p["segments"]["N_I"]),
                            float(p["segments"]["N_II"]), N)
    # decomposicao por mecanismo (serie por ciclo, |dF_0|)
    mechs = ["embedding", "creep", "wear", "rotational_loosening", "thread_fretting"]
    decomp = {m: [abs(s.dF_0_by_mech.get(m, 0.0)) for s in ana.history]
              for m in mechs}
    ref = p.get("reference") or []
    if ref:
        ref = np.asarray(ref, dtype=float)
        mae = seg.mae_per_segment(Ns, ratio, ref[:, 0], ref[:, 1])
    else:
        mae = {s.name: None for s in seg.stages}
    shares = MechanismDecomposition.shares_per_segment(ana.history, seg)
    segments = {}
    for s in seg.stages:
        sh = shares.get(s.name)
        segments[s.name] = {
            "window": [s.n_start, s.n_end],
            "mae": mae.get(s.name),
            "dominant": sh["dominant"] if sh else None,
            "shares": sh["shares"] if sh else None,
        }
    return {
        "curve": {"N": Ns, "ratio": ratio},
        "decomposition": decomp,
        "damage_trace": {"N": Ns, "D": Dtr},
        "segments": segments,
        "energy": {"conservation_residual": ana.energy.conservation_residual},
        "separated_at": separated_at,
    }


def handle_calibrate(p: dict) -> dict:
    # ESTAGIO B (2026-07-09): /calibrate usava o StagedCalibrator (fit de
    # tuners), APOSENTADO com a remocao da camada de tuners. O /simulate segue
    # funcionando com constantes fisicas; a calibracao canonica e o
    # SharedCalibrator (offline) ou ParameterIdentifier(engine='v2'). O corpo
    # antigo (StagedCalibrator) foi REMOVIDO — era codigo morto apos o raise.
    raise NotImplementedError(
        "Estagio B: /calibrate (StagedCalibrator) aposentado — a camada de "
        "tuners foi removida. Use /simulate com constantes fisicas; calibracao "
        "canonica via SharedCalibrator ou ParameterIdentifier(engine='v2').")


def handle_profiles() -> dict:
    return P.load_profiles(PROFILES_JSON)


def handle_shared() -> dict:
    """Retorna o bloco `shared` CANONICO (Estagio A/B: uma fisica, N estados)
    de joint_calibrations.json — constantes fisicas + conformacao + MAE/LOCO por
    condicao. {} se o arquivo/bloco nao existir. O bloco `profiles` (tuners
    legados) fica no /profiles; este e' o caminho canonico pos-Estagio-B."""
    return P.load_profiles(PROFILES_JSON).get("shared", {}) or {}


def content_type_for(path) -> str:
    """content-type por extensao (default application/octet-stream)."""
    return _CONTENT_TYPES.get(Path(path).suffix.lower(),
                              "application/octet-stream")


def resolve_static(rel_path: str, base: Path = VALIDATION_DIR) -> Optional[Path]:
    """Resolve `rel_path` (portador de URL, ja url-decodificado) para um arquivo
    DENTRO de `base`, com guarda contra path traversal. Retorna o Path resolvido
    se for um arquivo estritamente dentro de `base`; senao None (traversal,
    diretorio, ou inexistente). Fecha `..`, caminhos absolutos e symlinks que
    escapem — a checagem e' feita sobre o caminho JA resolvido (relative_to)."""
    rel = (rel_path or "").lstrip("/\\")
    if not rel:
        return None
    base_r = base.resolve()
    candidate = (base_r / rel).resolve()
    try:
        candidate.relative_to(base_r)          # escapou de base => ValueError
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


# ---- camada HTTP (fina) ----
class _Handler(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        self._bytes(code, json.dumps(obj).encode("utf-8"), "application/json")

    def _bytes(self, code, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read(self) -> dict:
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n) or b"{}")

    def _serve_static(self, rel: str):
        target = resolve_static(unquote(rel))
        if target is None:
            return self._json(404, {"error": "not found"})
        self._bytes(200, target.read_bytes(), content_type_for(target))

    def do_GET(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path in ("/", "/index.html"):
            self._bytes(200, TUNER_HTML.read_bytes(), "text/html; charset=utf-8")
        elif path == "/profiles":
            self._json(200, handle_profiles())
        elif path == "/shared":
            self._json(200, handle_shared())
        elif path in ("/validation", "/validation/"):
            # index da galeria: report mestre, se ja gerado (build_reports.py)
            target = resolve_static("validation_report.html")
            if target is None:
                return self._json(404, {"error": "validation_report.html "
                                        "ausente — rode New_Theory/build_reports.py"})
            self._bytes(200, target.read_bytes(), content_type_for(target))
        elif path.startswith("/validation/"):
            self._serve_static(path[len("/validation/"):])
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/profiles/save":
            try:
                p = self._read()
                P.upsert_profile(PROFILES_JSON, p["name"], p["profile"])
                return self._json(200, {"ok": True})
            except Exception as e:
                return self._json(400, {"error": str(e)})
        routes = {"/simulate": handle_simulate, "/calibrate": handle_calibrate}
        fn = routes.get(self.path)
        if fn is None:
            return self._json(404, {"error": "not found"})
        try:
            return self._json(200, fn(self._read()))
        except ValueError as e:
            return self._json(400, {"error": str(e)})
        except Exception as e:   # pragma: no cover
            return self._json(500, {"error": repr(e)})

    def log_message(self, *a):   # silencia o log padrao
        pass


def serve(port: int = 8765):
    srv = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    print(f"Calibration tuner em http://localhost:{port}/  (Ctrl+C pra sair)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    serve()
