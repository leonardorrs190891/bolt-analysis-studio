"""Gera o Explorador Interativo de Variaveis (docs).

Uma pagina HTML por campo de JointMaterial + indice. Curvas pre-computadas
pelo engine REAL (calibration.server.handle_simulate) - nenhuma fisica em JS.
Ver docs/superpowers/specs/2026-07-12-variable-explorer-design.md
"""
from __future__ import annotations
import dataclasses as dc
import html as _html
import json
import pathlib, sys

import numpy as np

_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
from bolt_analysis_studio.calibration.server import handle_simulate

OUTDIR = _ROOT / "New_Theory" / "variable_explorer"
_STORE_PATH = _ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"

_GEOM_M16 = dict(A_s=157e-6, L_eff=0.050, d_2=14.70e-3, pitch=2.0e-3,
                 r_bearing=12e-3, A_contact=1.0e-4)
_SEG = dict(N_I=50, N_II=500)


def _transverse():
    return dict(geom=dict(_GEOM_M16),
                loading=dict(F0_init=50000.0, F_amp=20000.0, theta=90.0,
                             freq=0.5, N=2500, delta_amp=0.5e-3, D_init=0.0),
                segments=dict(_SEG))


def _axial():
    p = _transverse()
    p["loading"].update(theta=0.0, delta_amp=0.0, F_amp=10000.0, freq=30.0)
    return p


def _creep():
    p = _transverse()
    p["loading"].update(freq=1.0 / 60.0)
    return p


def _fatigue():
    # baseline axial com janela LONGA: a fadiga so morde perto da fratura, entao
    # precisa de N alto p/ o cliff caber e os sweeps moverem sua posicao.
    p = _axial()
    p["loading"].update(N=6000)
    return p


BASELINES = {"transverse": _transverse, "axial": _axial, "creep": _creep,
             "fatigue": _fatigue}


@dc.dataclass
class VarSpec:
    name: str
    symbol: str
    unit: str
    group: str
    category: str            # physical | form | numerical | mode
    context: dict            # {"baseline": str, "overrides": dict}
    physics_pt: str
    physics_en: str
    equation: str
    sweep: tuple | None = None      # (lo, hi, n, scale)  scale in {lin, log}
    choices: list | None = None     # p/ modes/bools
    anchor_key: str | None = None
    lessons: list = dc.field(default_factory=list)
    refs: list = dc.field(default_factory=list)     # [(pt, en, fonte)]
    related: list = dc.field(default_factory=list)
    negligible: bool = False


VARIABLE_SPECS: list[VarSpec] = []   # preenchida nas Tasks de conteudo
CONCEPT_PAGES: list = []             # paginas de "Fundamentos" (preenchida por _ve_concepts.py)


def all_field_names() -> set:
    return set(JointMaterial.__dataclass_fields__)


def spec_names() -> set:
    return {s.name for s in VARIABLE_SPECS}


def missing_fields() -> set:
    return all_field_names() - spec_names()


def validate_specs() -> None:
    fields = all_field_names()
    seen = set()
    for s in VARIABLE_SPECS:
        if s.name not in fields:
            raise ValueError(f"VarSpec '{s.name}' nao e campo de JointMaterial")
        if s.name in seen:
            raise ValueError(f"VarSpec duplicado: {s.name}")
        seen.add(s.name)
        if (s.sweep is None) == (s.choices is None):
            raise ValueError(f"'{s.name}': setar exatamente um de sweep/choices")


# ---------------------------------------------------------------- simulacao
def sweep_values(spec: VarSpec) -> list:
    """A grade de valores varridos (ou as choices, para modes/bools)."""
    if spec.choices is not None:
        return list(spec.choices)
    lo, hi, n, scale = spec.sweep
    if scale == "log":
        return [float(x) for x in np.logspace(np.log10(lo), np.log10(hi), int(n))]
    return [float(x) for x in np.linspace(lo, hi, int(n))]


_MAX_PTS = 240   # pontos por curva embutidos no HTML (decimacao p/ tamanho)


def _decim_idx(m, max_pts=_MAX_PTS):
    """Indices decimados (mantendo extremos) p/ uma serie de tamanho m."""
    if m <= max_pts:
        return list(range(m))
    step = m / max_pts
    return sorted({int(i * step) for i in range(max_pts)} | {0, m - 1})


def _decimate(N, ratio, max_pts=_MAX_PTS):
    """Reduz a curva p/ ~max_pts pontos (mantendo extremos) e arredonda.

    A curva de ensaio tem ~2500 pontos; ~240 sao visualmente identicos e
    cortam o tamanho do HTML em ~10x. Arredonda ratio a 4 casas.
    """
    idx = _decim_idx(len(N), max_pts)
    return ([int(N[i]) for i in idx],
            [round(float(ratio[i]), 4) for i in idx])


# ---------------------------------------------------------------------------
# Dados de validacao PRE-COMPUTADOS (store canonico) + metadados dos casos.
# A galeria (Fase 3) e o overlay "nao-e-fit" (Fase 2) leem DAQUI: a curva do
# modelo vem do store (config ADOTADA por fonte, MAE ja calculado); os pontos
# experimentais vem do CSV digitalizado. NENHUM engine roda aqui.
# ---------------------------------------------------------------------------

# rotulo curto por fonte (autor-ano + blurb de aparato, pt/en). Fallback =
# deriva "Autor Ano" do nome do enum. Usado pela galeria de validacao.
_SOURCE_LABELS = {
    "LIU_2025":         ("Liu 2025", "M16 8.8, cisalhamento transversal, 6 amplitudes (Sci. Rep.)",
                                      "M16 8.8, transverse shear, 6 amplitudes (Sci. Rep.)"),
    "BAUER_2024":       ("Bauer 2024", "M8/M12, bancada EFA de auto-afrouxamento (espectro de amplitude)",
                                        "M8/M12, EFA self-loosening rig (amplitude spectrum)"),
    "LU_2024":          ("Lu 2024", "M8, varredura de torque de aperto (Sensors)",
                                     "M8, tightening-torque sweep (Sensors)"),
    "ICMEZ_2025":       ("Icmez/Demir 2024", "M8, amplitude x pre-carga (EJR&D)",
                                              "M8, amplitude x preload (EJR&D)"),
    "YANG_2019":        ("Yang 2019", "M10, Junker transversal",
                                       "M10, transverse Junker"),
    "YANG_2021":        ("Yang 2021", "combinado transversal + axial (supressao composta)",
                                       "combined transverse + axial (composite suppression)"),
    "YANG_2023_IJPEM":  ("Yang 2023", "M8, vida-vs-amplitude D-N (N ~ delta^-3.8)",
                                       "M8, D-N life-vs-amplitude (N ~ delta^-3.8)"),
    "ROUSSEAU_2025":    ("Rousseau 2025", "M12, espessura de membro t=10/12/14 + par HDPE",
                                          "M12, member thickness t=10/12/14 + HDPE pair"),
    "KARLSEN_2022":     ("Karlsen 2022", "M30/M42 grandes, HV x Vibralock",
                                         "large M30/M42, HV x Vibralock"),
    "SANDIA_2021":      ("Sandia 2021", "viga-C modal (forca/modal)",
                                        "C-beam modal (force/modal)"),
    "LIU_2022_RETIGHT": ("Liu 2022 (reaperto)", "cadeia de reapertos, seco x oleo",
                                                 "retightening chain, dry x oil"),
    "LIU_2017_AXIAL":   ("Liu 2017 (axial)", "carga axial, varredura F0 x amplitude @30 Hz",
                                             "axial load, F0 x amplitude sweep @30 Hz"),
    "LI_2022_MARSTRUC": ("Li 2022 (creep)", "creep de contato estatico, Ra x carga (min)",
                                            "static contact creep, Ra x load (min)"),
    "LI_2022_TRIBOINT": ("Li 2022 (axial x freq)", "Ti axial, 10/15/20 Hz",
                                                    "Ti axial, 10/15/20 Hz"),
    "UFU_LAB":          ("UFU (lab)", "M16 cisalhamento - rig de calibracao",
                                      "M16 shear - calibration rig"),
}


def _source_label(src):
    """(nome, blurb_pt, blurb_en) da fonte; fallback deriva 'Autor Ano'."""
    if src in _SOURCE_LABELS:
        return _SOURCE_LABELS[src]
    parts = src.replace("_", " ").title().split()
    return (" ".join(parts), "", "")


def _read_ref_csv(rec, max_pts=44):
    """Curva de referencia decimada p/ scatter, lida pelo MESMO caminho do
    runner (fonte unica de verdade): `load_full_curve` (colunas por POSICAO —
    aceita qualquer header) + as convencoes de eixo do caso
    `(x - csv_x_offset) * csv_x_scale` com clamp >= 0, normalizacao no 1o ponto
    e o FLOOR_TRIM da campanha. Assim o scatter da galeria e' exatamente a
    curva contra a qual a metrica foi computada.

    CONSERTO 2026-07-27 (S5): antes daqui a funcao lia com `csv.DictReader`
    exigindo as colunas LITERAIS 'cycle'/'F_over_F0'. Isso derrubava em
    SILENCIO toda fonte cujo CSV usa header 'x' (rodadas 4 e 5) — eram 73
    curvas de 11 fontes fora da galeria (CACCESE, CHU, ECCLES, GRZEJDA, JCSR,
    LIU_2016, LIU_2020_WEAR, QIN, SUN x2, YANG_2023_AME) — e ignorava
    csv_x_offset/csv_x_scale, plotando Lu e Karlsen no x errado (a ancora
    pre-ciclagem deles e' desenhada em x=1 num eixo log) e Eccles em segundos
    em vez de ciclos. Regra do CLAUDE.md: TODO consumidor do CSV cru aplica
    (x-offset)*scale.

    Retorna (N, ratio) ou ([],[]) em falha (degrada sem raise — mas quem chama
    CONTA os descartes e reporta, ver _validation_cases)."""
    try:
        from bolt_analysis_studio.validation.inputs import (load_full_curve,
                                                            repo_root)
        from bolt_analysis_studio.validation.runner import FLOOR_TRIM
        if not getattr(rec, "csv_path", None):
            return [], []
        try:
            rel = pathlib.Path(rec.csv_path).resolve().relative_to(
                repo_root()).as_posix()
        except ValueError:                       # caso fora do repo (usuario)
            rel = str(rec.csv_path)
        x, y = load_full_curve(rel)
        case = rec.validation_case
        off = float(getattr(case, "csv_x_offset", 0.0) or 0.0)
        sca = float(getattr(case, "csv_x_scale", 1.0) or 1.0)
        x = np.maximum(np.asarray(x, dtype=float) - off, 0.0) * sca
        y = np.asarray(y, dtype=float)
        if not y.size:
            return [], []
        y = y / max(float(y[0]), 1e-9)
        keep = y >= FLOOR_TRIM
        x, y = x[keep], y[keep]
        if not y.size:
            return [], []
        y = y / max(float(y[0]), 1e-9)
        idx = _decim_idx(len(x), max_pts)
        return ([int(x[i]) for i in idx], [round(float(y[i]), 4) for i in idx])
    except (OSError, ValueError, IndexError, KeyError, AttributeError):
        return [], []


_VALIDATION_CACHE = None


def _subst_contagens(html: str) -> str:
    """Troca os tokens de contagem pelas contagens REAIS da galeria, no momento
    da geracao.

    Existe por causa de um envelhecimento silencioso (S5 2026-07-27): a prosa
    dos Fundamentos afirmava "115 curvas de 15 aparatos" HARDCODED enquanto o
    conjunto real ja era 203/28 — e, pior, a propria galeria so mostrava 130
    porque o leitor de CSV derrubava 11 fontes. Numero de documento sai de
    DADO, nunca de prosa: escreva {{N_CURVAS}} / {{N_FONTES}} no conteudo."""
    vc = _validation_cases()
    n_c = len(vc)
    n_f = len({c["source"] for c in vc if c["source"] != "USER"})
    return (html.replace("{{N_CURVAS}}", str(n_c))
                .replace("{{N_FONTES}}", str(n_f)))


def _validation_cases():
    """Junta o store canonico (curva do modelo + MAE, config ADOTADA por fonte)
    com os metadados/CSV de cada caso. Lista de dicts prontos p/ render, ordenada
    por fonte e depois por MAE. Leitura pura de dados PRE-COMPUTADOS."""
    global _VALIDATION_CACHE
    if _VALIDATION_CACHE is not None:
        return _VALIDATION_CACHE
    out = []
    try:
        store = json.loads(_STORE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _VALIDATION_CACHE = out
        return out
    try:
        from bolt_analysis_studio.validation.case_registry import all_records
        recs = {r.case_id: r for r in all_records()}
    except Exception:
        recs = {}
    # Descartes CONTADOS e reportados (S5 2026-07-27): antes eles eram
    # silenciosos, e foi assim que 73 curvas de 11 fontes sumiram da galeria
    # sem ninguem notar por semanas. Degradar sem raise, sim; degradar sem
    # avisar, nao.
    # `fonte_retirada` entra como MAIS UM balde de descarte, e nao como um
    # filtro silencioso, exatamente pelo motivo do comentario acima: uma fonte
    # que some sem contagem e' indistinguivel de um bug de leitura. Aqui a
    # retirada e' decisao declarada (`_SRC_RETIRADO` em report_html), entao o
    # build imprime "fonte_retirada: UFU_..." e o operador ve que sumiu de
    # proposito.
    try:
        from bolt_analysis_studio.validation.report_html import caso_no_documento
    except Exception:                                    # degrada sem raise
        def caso_no_documento(source, case_id):          # noqa: E306
            return True
    drop = {"sem_registro": [], "fonte_retirada": [], "erro_ou_sem_curva": [],
            "sem_csv": [], "csv_ilegivel": []}
    for cid, v in store.items():
        r = recs.get(cid)
        if r is None:
            drop["sem_registro"].append(cid)
            continue
        if not caso_no_documento(r.source, cid):
            drop["fonte_retirada"].append(cid)
            continue
        if v.get("error") or not v.get("cycles") or v.get("mae") is None:
            drop["erro_ou_sem_curva"].append(cid)
            continue
        if not r.csv_path:
            drop["sem_csv"].append(cid)
            continue
        mN, mr = _decimate(v["cycles"], v["ratio"], max_pts=130)
        dN, dr = _read_ref_csv(r)
        if not dN:
            drop["csv_ilegivel"].append(cid)
            continue
        vc = r.validation_case
        name, blurb_pt, blurb_en = _source_label(r.source)
        out.append({
            "cid": cid, "name": r.name, "source": r.source,
            "source_name": name, "family": r.family, "caveats": list(r.caveats),
            "model_N": mN, "model_r": mr, "data_N": dN, "data_r": dr,
            "mae": round(float(v["mae"]), 4), "rmse": round(float(v.get("rmse", 0.0)), 4),
            "final_pred": round(float(v["final_pred"]), 3),
            "final_data": round(float(v["final_data"]), 3),
            "ok": bool(v.get("ok", True)),
            "bolt": getattr(vc, "bolt_size", ""),
            "F0_kN": round(getattr(vc, "initial_preload_N", 0.0) / 1000.0, 1),
            "amp_mm": getattr(vc, "transverse_displacement_mm", 0.0),
            "freq": getattr(vc, "frequency_Hz", 0.0),
            "doi": getattr(vc, "doi", "") or "",
            "reference": getattr(vc, "reference", "") or "",
            "note": (r.apparatus_note_path if r.apparatus_note_path else None),
        })
    out.sort(key=lambda c: (c["source_name"], c["mae"]))
    n_drop = sum(len(v) for v in drop.values())
    print("[galeria] %d curvas de %d fontes; %d descartadas%s"
          % (len(out), len({c["source"] for c in out}), n_drop,
             (" -> " + ", ".join("%s=%d" % (k, len(v))
                                 for k, v in drop.items() if v)) if n_drop else ""))
    for k, v in drop.items():
        if v:
            print("           %s: %s%s" % (k, ", ".join(v[:6]),
                                           " ..." if len(v) > 6 else ""))
    _VALIDATION_CACHE = out
    return out


def simulate(spec: VarSpec, value) -> dict:
    """Roda o engine REAL com baseline + companheiros + {spec.name: value}."""
    base = BASELINES[spec.context["baseline"]]()
    mat = dict(spec.context.get("overrides", {}))
    mat[spec.name] = value
    payload = dict(base)
    payload["mat"] = mat
    out = handle_simulate(payload)
    # handle_simulate devolve np.float64 -> coagir + decimar + arredondar,
    # senao json.dumps quebra e o HTML fica gigante.
    N, ratio = _decimate(out["curve"]["N"], out["curve"]["ratio"])
    return {"N": N, "ratio": ratio}


def sweep_variable(spec: VarSpec) -> dict:
    """Varre a variavel e coleta uma curva por valor + o indice do default."""
    default = getattr(JointMaterial(), spec.name)
    values = sweep_values(spec)
    curves = [{"value": v, **simulate(spec, v)} for v in values]
    baseline_idx = None
    if spec.sweep is not None and isinstance(default, (int, float)) \
            and not isinstance(default, bool):
        diffs = [abs(float(v) - float(default)) for v in values]
        baseline_idx = int(min(range(len(diffs)), key=diffs.__getitem__))
    return {"default": default, "values": values, "curves": curves,
            "baseline_idx": baseline_idx}


def curve_liveness(sweep_result) -> float:
    """Quanto o slider MOVE a curva = maior amplitude ponto-a-ponto entre as
    curvas varridas. Robusto ao caso 'todas terminam em 0' (ex.: fadiga/colapso,
    onde o que muda e a POSICAO do cliff, nao o valor final)."""
    curves = sweep_result["curves"]
    if len(curves) < 2:
        return 0.0
    m = min(len(c["ratio"]) for c in curves)
    best = 0.0
    for i in range(m):
        col = [c["ratio"][i] for c in curves]
        rng = max(col) - min(col)
        if rng > best:
            best = rng
    return best


# ---------------------------------------------------------------- proveniencia
def anchor_band(anchor_key):
    """(band=[lo,hi], fonte) da ancora medida, ou None. Le knowledge_base."""
    if not anchor_key:
        return None
    try:
        from bolt_analysis_studio.calibration.knowledge_base import anchor_priors
        a = anchor_priors().get(anchor_key)
    except Exception:
        return None
    if not isinstance(a, dict):
        return None
    band = a.get("banda_medida")
    if not (isinstance(band, (list, tuple)) and len(band) == 2):
        return None
    return {"band": [float(band[0]), float(band[1])], "fonte": a.get("fonte", "")}


# ---------------------------------------------------------------- template
GROUP_LABELS = {
    "embedding": ("Embedding (assentamento)", "Embedding"),
    "creep": ("Creep", "Creep"),
    "wear": ("Desgaste (Archard)", "Wear (Archard)"),
    "stiffness": ("Rigidez de contato (GW)", "Contact stiffness (GW)"),
    "friction": ("Atrito", "Friction"),
    "axial_fretting": ("Fretting axial de rosca", "Axial thread fretting"),
    "loosening": ("Afrouxamento rotacional", "Rotational loosening"),
    "slip_regime": ("Regime de escorregamento", "Slip regime"),
    "ratchet": ("Ratcheting / afrouxamento graduado", "Ratcheting / graded loosening"),
    "damage": ("Dano de superfície", "Surface damage"),
    "conformation": ("Conformação / incubação", "Conformation / incubation"),
    "member": ("Complacência do membro", "Member compliance"),
    "retighten": ("Re-aperto", "Retightening"),
    "fatigue": ("Fadiga (fratura)", "Fatigue (fracture)"),
    "crash": ("Gatilho de colapso", "Collapse trigger"),
    "numerical": ("Numérico / inércia", "Numerical / inertia"),
}
CATEGORY_LABELS = {
    "physical": ("constante física", "physical constant"),
    "form": ("forma opt-in", "opt-in form"),
    "numerical": ("numérico", "numerical"),
    "mode": ("modo (discreto)", "mode (discrete)"),
}

_BASE_CSS = """
:root{
  --bg:#eef0f3; --panel:#ffffff; --ink:#161a20; --muted:#5b6675; --line:#d3d8e0;
  --accent:#2563eb; --accent2:#e11d48; --ghost:#9aa4b2; --ok:#0f9d58; --warn:#c2410c;
  --code-bg:#f3f5f8; --side:#f7f8fa; --side-w:300px;
}
:root[data-theme="dark"]{
  --bg:#12151b; --panel:#1a1f27; --ink:#e7ebf0; --muted:#93a0b0; --line:#2b323d;
  --accent:#5b9bff; --accent2:#ff6b8b; --ghost:#4a5563; --ok:#39d98a; --warn:#ffa657;
  --code-bg:#20262f; --side:#151a21;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:'Segoe UI',system-ui,-apple-system,sans-serif;line-height:1.55}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
code,.mono{font-family:'Cascadia Code','Consolas',ui-monospace,monospace}

/* ---- sidebar (sumario tipo help classico) ---- */
.side{position:fixed;top:0;left:0;bottom:0;width:var(--side-w);overflow-y:auto;
  background:var(--side);border-right:1px solid var(--line);z-index:20}
.side-head{position:sticky;top:0;background:var(--side);padding:14px 16px 12px;
  border-bottom:1px solid var(--line);z-index:2}
.side-head .home{font-weight:700;font-size:.92rem;display:block;color:var(--ink)}
.side-head .home small{display:block;color:var(--muted);font-weight:400;font-size:.72rem;margin-top:2px}
.side-head .toggles{margin:10px 0 8px}
.toggles button{background:var(--panel);color:var(--ink);border:1px solid var(--line);
  border-radius:7px;padding:5px 10px;font-size:.78rem;cursor:pointer;margin-right:6px}
.toggles button:hover{border-color:var(--accent)}
.filter{width:100%;padding:6px 9px;border:1px solid var(--line);border-radius:7px;
  background:var(--bg);color:var(--ink);font-family:inherit;font-size:.83rem}
.tiers{display:flex;flex-wrap:wrap;gap:3px 12px;margin-top:9px;font-size:.72rem}
.tiers label{display:flex;align-items:center;gap:4px;color:var(--muted);cursor:pointer}
.tiers input{accent-color:var(--accent);margin:0;cursor:pointer}
.toc{padding:6px 0 60px}
.toc .grp{padding:12px 16px 3px;font-size:.68rem;text-transform:uppercase;
  letter-spacing:.07em;color:var(--muted);font-weight:700}
.toc a.tocitem{display:flex;justify-content:space-between;gap:8px;align-items:baseline;
  padding:4px 14px 4px 18px;font-family:'Cascadia Code',monospace;font-size:.8rem;
  color:var(--ink);border-left:3px solid transparent}
.toc a.tocitem:hover{background:var(--bg);text-decoration:none}
.toc a.tocitem.current{border-left-color:var(--accent);color:var(--accent);
  background:var(--bg);font-weight:600}
.toc a.tocitem .dot{font-size:.6rem;opacity:.6}
.toc a.tocitem .dot.physical{color:var(--accent)}
.toc a.tocitem .dot.form{color:var(--warn)}
.toc a.tocitem .dot.mode{color:var(--ok)}
.toc a.tocitem .dot.numerical{color:var(--muted)}

/* ---- content ---- */
.main{margin-left:var(--side-w);padding:26px 34px 90px;max-width:940px}
.crumbs{font-size:.82rem;color:var(--muted);margin-bottom:2px}
h1.name{font-family:'Cascadia Code','Consolas',monospace;font-size:1.95rem;margin:.2rem 0 .2rem}
.sub{color:var(--muted);font-size:.95rem;margin-bottom:.6rem}
.badges{display:flex;gap:8px;flex-wrap:wrap;margin:.4rem 0 1rem}
.badge{font-size:.74rem;padding:3px 9px;border-radius:20px;border:1px solid var(--line);
  background:var(--panel);color:var(--muted)}
.badge.cat-physical{border-color:var(--accent);color:var(--accent)}
.badge.cat-form{border-color:var(--warn);color:var(--warn)}
.badge.cat-mode{border-color:var(--ok);color:var(--ok)}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;
  padding:16px 18px;margin:14px 0}
.panel p{margin:.4rem 0}
.plotwrap{position:relative}
canvas{width:100%;height:auto;display:block}
.ctl{display:flex;align-items:center;gap:14px;margin-top:12px;flex-wrap:wrap}
.ctl input[type=range]{flex:1;min-width:220px;accent-color:var(--accent)}
.ctl select{background:var(--code-bg);color:var(--ink);border:1px solid var(--line);
  border-radius:7px;padding:6px 10px;font-family:inherit}
.readout{font-family:'Cascadia Code',monospace;font-size:.95rem}
.readout .v{color:var(--accent);font-weight:600}
.readout .f{color:var(--accent2);font-weight:600}
.readout .w{color:var(--warn);font-weight:600}
.legend .kdash{display:inline-block;width:22px;height:0;border-top:2px dashed var(--muted);vertical-align:middle;margin-right:5px}
.prov{font-size:.82rem;margin-top:8px;color:var(--muted)}
.prov.out{color:var(--warn);font-weight:600}
.effect{font-family:'Cascadia Code',monospace;font-size:.82rem;margin-top:8px;color:var(--accent)}
.effect.weak{color:var(--muted)}
h2.sec{font-size:1.05rem;margin:0 0 .5rem;letter-spacing:.02em}
.eq{background:var(--code-bg);border:1px solid var(--line);border-radius:8px;
  padding:12px 14px;font-family:'Cascadia Code',monospace;font-size:.92rem;overflow-x:auto;
  white-space:pre;line-height:1.5;margin:.5rem 0}
ul.refs{margin:.3rem 0 0;padding-left:1.1rem}
ul.refs li{margin:.25rem 0;font-size:.9rem}
ul.refs li.refhead{list-style:none;margin:14px 0 4px -1.1rem;color:var(--muted);
  font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;font-weight:700}
ul.refs .src{color:var(--muted);font-size:.82rem}
.related a{display:inline-block;margin-right:10px;font-family:'Cascadia Code',monospace;font-size:.85rem}
nav.pn{display:flex;justify-content:space-between;margin-top:24px;font-size:.9rem}
.note{background:var(--code-bg);border-left:3px solid var(--warn);padding:8px 12px;
  border-radius:0 6px 6px 0;font-size:.88rem;color:var(--muted);margin:.6rem 0}
.intro{color:var(--muted);max-width:74ch}
.legend{display:flex;gap:16px;font-size:.8rem;color:var(--muted);margin-top:6px;flex-wrap:wrap}
.legend .k{display:inline-block;width:22px;height:0;border-top-width:3px;border-top-style:solid;vertical-align:middle;margin-right:5px}
[data-lang="pt"] [data-l="en"]{display:none}
[data-lang="en"] [data-l="pt"]{display:none}

/* ---- responsivo: sidebar recolhivel ---- */
.menu-btn{display:none;position:fixed;top:10px;left:10px;z-index:40;
  background:var(--panel);border:1px solid var(--line);border-radius:8px;
  padding:6px 11px;font-size:1rem;cursor:pointer;color:var(--ink)}
@media(max-width:900px){
  .side{transform:translateX(-100%);transition:transform .2s;box-shadow:0 0 30px rgba(0,0,0,.3)}
  body.nav-open .side{transform:none}
  .main{margin-left:0;padding:56px 16px 80px}
  .menu-btn{display:inline-block}
}

/* ---- animações & interatividade ---- */
@keyframes ve-pop{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.ve-progress{position:fixed;top:0;left:0;height:3px;width:0;z-index:60;
  background:linear-gradient(90deg,var(--accent),var(--accent2));
  box-shadow:0 0 8px var(--accent);transition:width .08s linear}
h1.name{animation:ve-pop .5s cubic-bezier(.2,.7,.2,1) both}
.reveal{opacity:0;transform:translateY(16px)}
.reveal.in{opacity:1;transform:none;
  transition:opacity .6s cubic-bezier(.2,.7,.2,1),transform .6s cubic-bezier(.2,.7,.2,1)}
.panel,.badge,.trail,.gal-card,.related a,.toc a.tocitem,.toggles button,
.menu-btn,nav.pn a{transition:transform .18s ease,box-shadow .18s ease,
  border-color .18s ease,background .18s ease,color .15s ease}
.trail:hover,.gal-card:hover{transform:translateY(-3px);box-shadow:0 10px 24px rgba(0,0,0,.16)}
.toc a.tocitem:hover{transform:translateX(3px)}
.related a:hover,nav.pn a:hover{transform:translateY(-1px)}
.toggles button:active,.menu-btn:active{transform:scale(.94)}
.plotwrap canvas,.cw canvas{cursor:crosshair}
@media(prefers-reduced-motion:reduce){
  .reveal,.reveal.in{opacity:1!important;transform:none!important;transition:none!important}
  h1.name{animation:none}
  .ve-progress{display:none}
  .trail:hover,.gal-card:hover,.toc a.tocitem:hover,.related a:hover,nav.pn a:hover{transform:none}
}
"""

_PLOTTER_JS = """
(function(){
  const root=document.documentElement;
  const cv=document.getElementById('plot'), ctx=cv.getContext('2d');
  const cs=getComputedStyle(root);
  function col(n){return cs.getPropertyValue(n).trim();}
  const PAD={l:58,r:14,t:14,b:40};
  let cur = (DATA.baseline_idx!=null?DATA.baseline_idx:Math.floor(DATA.curves.length/2));
  const xmax = Math.max(1, ...DATA.curves.map(c=>c.N[c.N.length-1]));

  function resize(){
    const w=cv.clientWidth||900, h=Math.round(w*0.5);
    const dpr=window.devicePixelRatio||1;
    cv.width=w*dpr; cv.height=h*dpr; cv.style.height=h+'px';
    ctx.setTransform(dpr,0,0,dpr,0,0); draw(cur);
  }
  // auto-zoom Y ao envelope das curvas (mudancas pequenas ficam visiveis).
  let ymin=Infinity, ymax=-Infinity;
  DATA.curves.forEach(c=>c.ratio.forEach(r=>{if(r<ymin)ymin=r; if(r>ymax)ymax=r;}));
  if(!isFinite(ymin)){ymin=0; ymax=1;}
  const _span=ymax-ymin, _pad=_span>0?_span*0.08:0.02;
  let y0=Math.max(0, ymin-_pad), y1=Math.min(1.02, ymax+_pad);
  if(y1-y0<0.03){const md=(y0+y1)/2; y0=Math.max(0,md-0.02); y1=Math.min(1.02,md+0.02);}
  const _zoomed=(y0>0.015 || y1<0.985);
  function X(n,w){return PAD.l+(n/xmax)*(w-PAD.l-PAD.r);}
  function Y(r,h){const rr=Math.max(y0,Math.min(y1,r));
    return PAD.t+(1-(rr-y0)/(y1-y0))*(h-PAD.t-PAD.b);}

  let animT=1, hoverN=null;   // animT: fração desenhada da curva ativa (draw-on)
  function curvePath(c,w,h,frac){ctx.beginPath();
    const n=(frac==null)?c.N.length:Math.max(2,Math.floor(c.N.length*frac));
    for(let i=0;i<n;i++){const x=X(c.N[i],w),y=Y(c.ratio[i],h);
      i?ctx.lineTo(x,y):ctx.moveTo(x,y);} }

  function draw(idx){
    cur=idx;
    const w=cv.clientWidth||900, h=parseInt(cv.style.height)||450;
    const dec=(y1-y0)<0.2?3:2;
    ctx.clearRect(0,0,w,h);
    // grid + axes (rotulos = valores REAIS do eixo zoomado)
    ctx.strokeStyle=col('--line'); ctx.fillStyle=col('--muted');
    ctx.lineWidth=1; ctx.font="12px 'Segoe UI',sans-serif";
    ctx.textAlign='right'; ctx.textBaseline='middle';
    for(let g=0;g<=5;g++){const val=y1-(g/5)*(y1-y0), y=PAD.t+(g/5)*(h-PAD.t-PAD.b);
      ctx.globalAlpha=.5;ctx.beginPath();ctx.moveTo(PAD.l,y);ctx.lineTo(w-PAD.r,y);ctx.stroke();
      ctx.globalAlpha=1;ctx.fillText(val.toFixed(dec),PAD.l-8,y);}
    ctx.textAlign='center';ctx.textBaseline='top';
    for(let g=0;g<=5;g++){const n=Math.round(xmax*g/5),x=X(n,w);
      ctx.fillText(n,x,h-PAD.b+8);}
    ctx.save();ctx.translate(14,h/2);ctx.rotate(-Math.PI/2);
    ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText('F / F0'+(_zoomed?(root.dataset.lang==='pt'?' (zoom)':' (zoom)'):''),0,0);ctx.restore();
    ctx.textAlign='center';ctx.fillText(root.dataset.lang==='pt'?'ciclo':'cycle',(PAD.l+w-PAD.r)/2,h-16);
    // ghosts (bem apagados, para nao mascarar a curva ativa)
    ctx.strokeStyle=col('--ghost');ctx.lineWidth=1;ctx.globalAlpha=.16;
    DATA.curves.forEach((c,i)=>{if(i===idx)return;curvePath(c,w,h);ctx.stroke();});
    ctx.globalAlpha=1;
    // default (tracejado)
    if(DATA.baseline_idx!=null && DATA.baseline_idx!==idx){
      ctx.strokeStyle=col('--muted');ctx.setLineDash([5,4]);ctx.lineWidth=1.5;
      curvePath(DATA.curves[DATA.baseline_idx],w,h);ctx.stroke();ctx.setLineDash([]);}
    // ativa (destaque forte) — animT controla o desenho progressivo
    ctx.strokeStyle=col('--accent');ctx.lineWidth=3.2;
    curvePath(DATA.curves[idx],w,h,animT);ctx.stroke();
    // leitura interativa: cruz + ponto + rótulo ao passar o cursor
    if(hoverN!=null && animT>=1){
      const c=DATA.curves[idx]; let bi=0,bd=1e9;
      for(let i=0;i<c.N.length;i++){const d=Math.abs(c.N[i]-hoverN);if(d<bd){bd=d;bi=i;}}
      const hx=X(c.N[bi],w),hy=Y(c.ratio[bi],h);
      ctx.save();ctx.strokeStyle=col('--muted');ctx.globalAlpha=.55;ctx.setLineDash([3,3]);
      ctx.beginPath();ctx.moveTo(hx,PAD.t);ctx.lineTo(hx,h-PAD.b);ctx.stroke();ctx.restore();
      ctx.fillStyle=col('--accent');ctx.beginPath();ctx.arc(hx,hy,4.5,0,6.2832);ctx.fill();
      const lbl='N='+Math.round(c.N[bi])+'  F/F0='+c.ratio[bi].toFixed(3);
      ctx.font="12px 'Segoe UI',sans-serif";ctx.textAlign='left';ctx.textBaseline='alphabetic';
      const tw=ctx.measureText(lbl).width;let lx=hx+8;if(lx+tw>w-PAD.r)lx=hx-8-tw;
      ctx.globalAlpha=.92;ctx.fillStyle=col('--panel');ctx.fillRect(lx-4,hy-21,tw+8,17);
      ctx.globalAlpha=1;ctx.fillStyle=col('--ink');ctx.fillText(lbl,lx,hy-8);
    }
    syncReadout();
  }

  function fmt(v){if(typeof v!=='number')return String(v);
    const a=Math.abs(v);
    if(v===0)return '0';
    if(a>=1e4||a<1e-3)return v.toExponential(2);
    return (Math.round(v*1000)/1000).toString();}

  function syncReadout(){
    const c=DATA.curves[cur];
    const vEl=document.getElementById('valout'), fEl=document.getElementById('finalout');
    if(vEl)vEl.textContent=fmt(c.value)+(DATA.unit?(' '+DATA.unit):'');
    if(fEl)fEl.textContent=(Math.round(c.ratio[c.ratio.length-1]*1000)/1000).toFixed(3);
    // proveniencia
    const pv=document.getElementById('prov');
    if(pv && DATA.provenance && typeof c.value==='number'){
      const [lo,hi]=DATA.provenance.band, out=(c.value<lo||c.value>hi);
      pv.classList.toggle('out',out);
      const inside=root.dataset.lang==='pt'?'dentro da banda medida':'within measured band';
      const outside=root.dataset.lang==='pt'?'FORA da banda medida':'OUTSIDE measured band';
      pv.textContent=(out?outside:inside)+' ['+fmt(lo)+', '+fmt(hi)+']'
        +(DATA.provenance.fonte?(' \\u00b7 '+DATA.provenance.fonte):'');
    }
    // indicador de quanto o slider move a curva (Delta max ponto-a-ponto)
    const eb=document.getElementById('effect');
    if(eb && typeof DATA.delta_max==='number'){
      const pt=root.dataset.lang==='pt', d=DATA.delta_max;
      let msg='\\u0394max F/F0 = '+d.toFixed(3);
      if(DATA.negligible) msg+=pt?' \\u00b7 efeito negligível nesta curva-padrão (ver texto)'
                                 :' \\u00b7 negligible effect on this standard curve (see text)';
      else if(d<0.02) msg+=pt?' \\u00b7 efeito pequeno nesta curva-padrão'
                             :' \\u00b7 small effect on this standard curve';
      eb.textContent=msg;
      eb.classList.toggle('weak', !!DATA.negligible || d<0.02);
    }
  }

  const slider=document.getElementById('slider');
  if(slider)slider.addEventListener('input',e=>draw(parseInt(e.target.value)));
  const sel=document.getElementById('sel');
  if(sel)sel.addEventListener('change',e=>draw(parseInt(e.target.value)));
  // cruz interativa que segue o cursor sobre a curva
  function pick(ev){const r=cv.getBoundingClientRect();
    const cx=(ev.touches&&ev.touches[0]?ev.touches[0].clientX:ev.clientX)-r.left;
    const w=cv.clientWidth||900;
    hoverN=Math.max(0,Math.min(xmax,((cx-PAD.l)/(w-PAD.l-PAD.r))*xmax));draw(cur);}
  cv.addEventListener('mousemove',pick);
  cv.addEventListener('mouseleave',function(){hoverN=null;draw(cur);});
  cv.addEventListener('touchmove',function(e){pick(e);e.preventDefault();},{passive:false});
  // desenho progressivo da curva ativa no primeiro load
  function drawOn(){
    if(matchMedia('(prefers-reduced-motion: reduce)').matches){animT=1;draw(cur);return;}
    animT=0;let t0=null;
    function step(ts){if(t0==null)t0=ts;animT=Math.min(1,(ts-t0)/650);draw(cur);
      if(animT<1)requestAnimationFrame(step);else animT=1;}
    requestAnimationFrame(step);
  }
  window.veRedraw=function(){draw(cur);};   // shell chama no toggle de tema/idioma
  window.addEventListener('resize',resize);
  animT=0; resize(); drawOn();
})();
"""

# JS compartilhado do "shell" (sidebar): toggles de tema/idioma, filtro do TOC,
# menu mobile. Roda antes do plotter (define root.dataset a partir do localStorage).
_SHELL_JS = """
(function(){
  const root=document.documentElement;
  root.dataset.theme = localStorage.getItem('ve_theme') || 'light';
  root.dataset.lang  = localStorage.getItem('ve_lang')  || 'pt';
  window.veToggleTheme=function(){root.dataset.theme=root.dataset.theme==='dark'?'light':'dark';
    localStorage.setItem('ve_theme',root.dataset.theme);
    window.veRedraw&&window.veRedraw(); window._cwRefresh&&window._cwRefresh();};
  window.veToggleLang=function(){root.dataset.lang=root.dataset.lang==='pt'?'en':'pt';
    localStorage.setItem('ve_lang',root.dataset.lang);
    window.veRedraw&&window.veRedraw(); window._cwRefresh&&window._cwRefresh();};
  window.veToggleNav=function(){document.body.classList.toggle('nav-open');};
  function veVisibleTiers(){
    const s=new Set();
    document.querySelectorAll('.tierbox').forEach(c=>{if(c.checked)s.add(c.dataset.tier);});
    return s;}
  function veApply(){
    const el=document.getElementById('ve-filter');
    const q=(el?el.value:'').toLowerCase().trim();
    const tiers=veVisibleTiers();
    document.querySelectorAll('.toc .tocitem').forEach(a=>{
      if(a.classList.contains('current')){a.style.display='';return;}  // pagina atual sempre visivel
      const okText=(!q||a.dataset.name.indexOf(q)>=0||a.textContent.toLowerCase().indexOf(q)>=0);
      // 'base' (Fundamentos) sempre visivel; busca por texto revela qualquer tier;
      // sem busca, respeita as caixas de grupo
      const okTier=(!!q)||a.dataset.tier==='base'||tiers.has(a.dataset.tier);
      a.style.display=(okText&&okTier)?'':'none';});
    document.querySelectorAll('.toc .grp').forEach(g=>{let n=g.nextElementSibling,any=false;
      while(n&&n.classList.contains('tocitem')){if(n.style.display!=='none'){any=true;break;}
        n=n.nextElementSibling;}
      g.style.display=any?'':'none';});}
  window.veFilter=veApply;
  window.veTier=function(){
    const on=[]; document.querySelectorAll('.tierbox').forEach(c=>{if(c.checked)on.push(c.dataset.tier);});
    localStorage.setItem('ve_tiers', on.join('|')); veApply();};
  // restaura estado das caixas (default: fisica+avancada visiveis, raras ocultas)
  (function(){
    const saved=localStorage.getItem('ve_tiers');
    const on = saved!==null ? new Set(saved.split('|').filter(Boolean))
                            : new Set(['fisica']);   // default: so as constantes fisicas
    document.querySelectorAll('.tierbox').forEach(c=>{c.checked=on.has(c.dataset.tier);});
    veApply();
  })();

  // ---- animações: barra de progresso de rolagem + reveal on scroll ----
  (function(){
    if(matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const bar=document.createElement('div');bar.className='ve-progress';
    document.body.appendChild(bar);
    function prog(){const d=document.documentElement,
      h=d.scrollHeight-d.clientHeight;
      bar.style.width=(h>0?((d.scrollTop||window.pageYOffset)/h*100):0)+'%';}
    window.addEventListener('scroll',prog,{passive:true});
    window.addEventListener('resize',prog);prog();
    const vh=window.innerHeight||800;
    const io=new IntersectionObserver(function(es){es.forEach(function(e){
      if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},
      {rootMargin:'0px 0px -6% 0px'});
    document.querySelectorAll('.panel,figure,.cw,.eq,.gal-card,.trail,h2.sec')
      .forEach(function(el){const r=el.getBoundingClientRect();
        if(r.top>vh*0.9){el.classList.add('reveal');io.observe(el);}});
  })();
})();
"""


def _esc(s):
    return _html.escape(str(s), quote=True)


def _norm(s):
    """Normaliza prosa dos autores: alguns duplo-escapam as tags (&lt;p&gt;) e as
    entidades (&amp;delta;). Um unico unescape devolve tags reais (<p>) + entidades
    simples (&delta;), que renderizam certo inseridas raw. Texto ja correto
    (entidades simples, sem &amp;) passa intocado."""
    if isinstance(s, str) and ("&amp;" in s or "&lt;p&gt;" in s
                               or "&lt;b&gt;" in s or "&lt;code&gt;" in s):
        return _html.unescape(s)
    return s


def _ordered(specs):
    """Specs na ordem dos grupos (GROUP_LABELS), preservando ordem dentro do grupo."""
    order = {g: i for i, g in enumerate(GROUP_LABELS)}
    return sorted(specs, key=lambda s: (order.get(s.group, 999),))


def _tier(s):
    """Tier de importancia p/ o filtro do sumario:
    'fisica' = constante fisica (as que entram no fit canonico);
    'avancada' = forma opt-in / modo ativo; 'rara' = numerico OU negligible."""
    if s.negligible or s.category == "numerical":
        return "rara"
    if s.category == "physical":
        return "fisica"
    return "avancada"


def _sidebar_html(all_specs, current_name):
    """Sumario lateral (TOC) agrupado, com a variavel atual destacada + filtro."""
    ordered = _ordered(all_specs)
    by_group = {}
    for s in ordered:
        by_group.setdefault(s.group, []).append(s)
    parts = []
    # grupo "Fundamentos" no topo (paginas conceituais) - sempre visivel (tier base)
    if CONCEPT_PAGES:
        parts.append('<div class="grp"><span data-l="pt">Fundamentos</span>'
                     '<span data-l="en">Foundations</span></div>')
        for p in CONCEPT_PAGES:
            cur = " current" if p["slug"] == current_name else ""
            parts.append(
                f'<a class="tocitem base{cur}" href="concept_{_esc(p["slug"])}.html" '
                f'data-name="{_esc(p["slug"])}" data-tier="base">'
                f'<span data-l="pt">{_esc(p["nav_pt"])}</span>'
                f'<span data-l="en">{_esc(p["nav_en"])}</span></a>')
    # grupo "Estudos de caso" (paginas por fonte) - sempre visivel (tier base)
    studies = _study_sources()
    if studies:
        parts.append('<div class="grp"><span data-l="pt">Estudos de caso</span>'
                     '<span data-l="en">Case studies</span></div>')
        for sd in studies:
            cur = " current" if sd["slug"] == current_name else ""
            parts.append(
                f'<a class="tocitem base{cur}" href="{_esc(sd["slug"])}.html" '
                f'data-name="{_esc(sd["slug"])}" data-tier="base">{_esc(sd["name"])}</a>')
    for g, (pt, en) in GROUP_LABELS.items():
        if g not in by_group:
            continue
        parts.append(f'<div class="grp"><span data-l="pt">{_esc(pt)}</span>'
                     f'<span data-l="en">{_esc(en)}</span></div>')
        for s in by_group[g]:
            cur = " current" if s.name == current_name else ""
            parts.append(
                f'<a class="tocitem{cur}" href="var_{_esc(s.name)}.html" '
                f'data-name="{_esc(s.name.lower())}" data-tier="{_tier(s)}">{_esc(s.name)}'
                f'<span class="dot {_esc(s.category)}">&#9679;</span></a>')
    toc = "".join(parts)
    return f"""<button class="menu-btn" onclick="veToggleNav()">&#9776;</button>
<aside class="side">
  <div class="side-head">
    <a class="home" href="index.html">BAS V2 &middot; <span data-l="pt">Variáveis</span><span data-l="en">Variables</span>
      <small><span data-l="pt">explorador do modelo</span><span data-l="en">model explorer</span></small></a>
    <div class="toggles">
      <button onclick="veToggleLang()">PT / EN</button>
      <button onclick="veToggleTheme()">&#9681;</button>
    </div>
    <input id="ve-filter" class="filter" oninput="veFilter()"
      placeholder="filtrar / filter...">
    <div class="tiers">
      <label><input type="checkbox" class="tierbox" data-tier="fisica" onchange="veTier()">
        <span data-l="pt">Físicas</span><span data-l="en">Physical</span></label>
      <label><input type="checkbox" class="tierbox" data-tier="avancada" onchange="veTier()">
        <span data-l="pt">Formas/modos</span><span data-l="en">Forms/modes</span></label>
      <label><input type="checkbox" class="tierbox" data-tier="rara" onchange="veTier()">
        <span data-l="pt">Numérico/raras</span><span data-l="en">Numerical/rare</span></label>
    </div>
  </div>
  <nav class="toc">{toc}</nav>
</aside>"""


def _control_html(spec, sweep_result):
    """Slider (sweep) ou <select> (choices/modes). Sempre index-based."""
    curves = sweep_result["curves"]
    n = len(curves)
    start = sweep_result["baseline_idx"] if sweep_result["baseline_idx"] is not None else n // 2
    if spec.choices is not None:
        opts = "".join(
            f'<option value="{i}"{" selected" if i == start else ""}>{_esc(c["value"])}</option>'
            for i, c in enumerate(curves))
        return f'<select id="sel">{opts}</select>'
    return (f'<input type="range" id="slider" min="0" max="{n-1}" step="1" '
            f'value="{start}">')


def render_variable_page(spec, sweep_result, all_specs=None, cur_index=None):
    if all_specs is None:
        all_specs = [spec]
    ordered = _ordered(all_specs)
    names = [s.name for s in ordered]
    pos = names.index(spec.name) if spec.name in names else 0
    prev_name = names[pos - 1] if pos > 0 else None
    next_name = names[pos + 1] if pos < len(names) - 1 else None
    sidebar = _sidebar_html(all_specs, spec.name)

    gl = GROUP_LABELS.get(spec.group, (spec.group, spec.group))
    cl = CATEGORY_LABELS.get(spec.category, (spec.category, spec.category))
    prov = anchor_band(spec.anchor_key)
    data = {
        "name": spec.name, "symbol": spec.symbol, "unit": spec.unit,
        "group": spec.group, "category": spec.category,
        "default": sweep_result["default"], "baseline_idx": sweep_result["baseline_idx"],
        "curves": sweep_result["curves"],
        "provenance": prov,
        "delta_max": round(curve_liveness(sweep_result), 4),
        "negligible": bool(spec.negligible),
    }
    data_json = json.dumps(data)

    # faixa
    if spec.sweep is not None:
        lo, hi, nn, scale = spec.sweep
        faixa = f"{lo:g} … {hi:g} {spec.unit} ({scale})"
    else:
        faixa = " | ".join(_esc(c) for c in spec.choices)

    # refs
    ref_items = ""
    for r in spec.refs:
        pt, en, src = (list(r) + ["", "", ""])[:3]
        ref_items += (f'<li><span data-l="pt">{_norm(pt)}</span>'
                      f'<span data-l="en">{_norm(en)}</span>'
                      f'{f" <span class=src>({_norm(src)})</span>" if src else ""}</li>')
    if spec.anchor_key:
        ref_items += (f'<li><span data-l="pt">Âncora de procedência: '
                      f'<code>{_esc(spec.anchor_key)}</code> (knowledge_base)</span>'
                      f'<span data-l="en">Provenance anchor: '
                      f'<code>{_esc(spec.anchor_key)}</code> (knowledge_base)</span></li>')
    for L in spec.lessons:
        ref_items += (f'<li><span data-l="pt">Lição <code>{_esc(L)}</code> '
                      f'(paper_study_ledger)</span>'
                      f'<span data-l="en">Lesson <code>{_esc(L)}</code> '
                      f'(paper_study_ledger)</span></li>')
    if not ref_items:
        ref_items = ('<li><span data-l="pt">Ver MODEL_MATH_REFERENCE.md</span>'
                     '<span data-l="en">See MODEL_MATH_REFERENCE.md</span></li>')

    related = ""
    if spec.related:
        links = "".join(f'<a href="var_{_esc(r)}.html"><code>{_esc(r)}</code></a>'
                        for r in spec.related)
        related = (f'<p class="related"><span data-l="pt">Relacionado: </span>'
                   f'<span data-l="en">Related: </span>{links}</p>')

    neg_note = ""
    if spec.negligible:
        neg_note = ('<div class="note"><span data-l="pt">Parâmetro numérico/de escopo — '
                    'efeito negligível nesta curva de ensaio contínuo (ver texto).</span>'
                    '<span data-l="en">Numerical/scope parameter — negligible effect on this '
                    'continuous-test curve (see text).</span></div>')

    prov_line = '<div class="prov" id="prov"></div>' if prov else ""

    prev_link = (f'<a href="var_{_esc(prev_name)}.html">&larr; {_esc(prev_name)}</a>'
                 if prev_name else "<span></span>")
    next_link = (f'<a href="var_{_esc(next_name)}.html">{_esc(next_name)} &rarr;</a>'
                 if next_name else "<span></span>")

    return f"""<!doctype html>
<html lang="pt" data-theme="light" data-lang="pt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(spec.name)} — Explorador de Variáveis BAS V2</title>
<style>{_BASE_CSS}</style>
</head>
<body>
{sidebar}
<main class="main">
<div class="crumbs"><a href="index.html">&#8962; <span data-l="pt">Explorador de Variáveis</span><span data-l="en">Variable Explorer</span></a> / <code>{_esc(spec.name)}</code></div>
<h1 class="name">{_esc(spec.name)}</h1>
<div class="sub">
  <span data-l="pt">{_esc(gl[0])}</span><span data-l="en">{_esc(gl[1])}</span>
  &nbsp;&middot;&nbsp; <span class="mono">{_esc(spec.symbol)}</span>
  {f'&nbsp;[{_esc(spec.unit)}]' if spec.unit else ''}
</div>
<div class="badges">
  <span class="badge cat-{_esc(spec.category)}">
    <span data-l="pt">{_esc(cl[0])}</span><span data-l="en">{_esc(cl[1])}</span></span>
  <span class="badge"><span data-l="pt">default: </span><span data-l="en">default: </span>
    <span class="mono">{_esc(data['default'])}</span></span>
  <span class="badge"><span data-l="pt">faixa: </span><span data-l="en">range: </span>
    <span class="mono">{faixa}</span></span>
</div>

<div class="panel plotwrap">
  <canvas id="plot"></canvas>
  <div class="legend">
    <span><i class="k" style="border-color:var(--accent)"></i>
      <span data-l="pt">valor atual</span><span data-l="en">current value</span></span>
    <span><i class="k" style="border-color:var(--muted);border-top-style:dashed"></i>
      <span data-l="pt">default</span><span data-l="en">default</span></span>
    <span><i class="k" style="border-color:var(--ghost)"></i>
      <span data-l="pt">varredura</span><span data-l="en">sweep</span></span>
  </div>
  <div class="ctl">
    {_control_html(spec, sweep_result)}
    <span class="readout">
      <span data-l="pt">valor</span><span data-l="en">value</span> =
      <span class="v" id="valout"></span> &nbsp;&rarr;&nbsp; F/F0<sub>final</sub> =
      <span class="f" id="finalout"></span>
    </span>
  </div>
  <div class="effect" id="effect"></div>
  {prov_line}
</div>

{neg_note}

<div class="panel">
  <h2 class="sec"><span data-l="pt">Física</span><span data-l="en">Physics</span></h2>
  <div data-l="pt">{_norm(spec.physics_pt)}</div>
  <div data-l="en">{_norm(spec.physics_en)}</div>
</div>

<div class="panel">
  <h2 class="sec"><span data-l="pt">Equação</span><span data-l="en">Equation</span></h2>
  <div class="eq">{_norm(spec.equation)}</div>
</div>

<div class="panel">
  <h2 class="sec"><span data-l="pt">Referências</span><span data-l="en">References</span></h2>
  <ul class="refs">{ref_items}</ul>
  {related}
</div>

<nav class="pn">{prev_link}<a href="index.html">&#8962; <span data-l="pt">índice</span><span data-l="en">index</span></a>{next_link}</nav>
</main>
<script>{_SHELL_JS}</script>
<script>const DATA = {data_json};</script>
<script>{_PLOTTER_JS}</script>
</body>
</html>
"""


# ---------------------------------------------------------------- indice
def render_index(specs):
    sidebar = _sidebar_html(specs, current_name=None)
    n = len(specs)
    # contagem por categoria (p/ o resumo)
    cats = {}
    for s in specs:
        cats[s.category] = cats.get(s.category, 0) + 1
    cat_line = ", ".join(f"{cats[c]} {CATEGORY_LABELS.get(c, (c, c))[0]}"
                         for c in ("physical", "form", "mode", "numerical") if c in cats)
    cat_line_en = ", ".join(f"{cats[c]} {CATEGORY_LABELS.get(c, (c, c))[1]}"
                            for c in ("physical", "form", "mode", "numerical") if c in cats)
    concept_links = "".join(
        f'<li><a href="concept_{_esc(p["slug"])}.html">'
        f'<span data-l="pt">{_esc(p["nav_pt"])}</span><span data-l="en">{_esc(p["nav_en"])}</span></a> '
        f'&ndash; <span class="src"><span data-l="pt">{_esc(p.get("hook_pt",""))}</span>'
        f'<span data-l="en">{_esc(p.get("hook_en",""))}</span></span></li>'
        for p in CONCEPT_PAGES)
    trails = (
        '<div class="trails">'
        '<a class="trail" href="concept_manual.html"><b>&#128214; '
        '<span data-l="pt">Manual (3 volumes)</span><span data-l="en">Manual (3 volumes)</span></b>'
        '<span class="desc"><span data-l="pt">entender &middot; explicar &middot; aplicar &mdash; '
        'o fio condutor, com os n&uacute;meros do store</span>'
        '<span data-l="en">understand &middot; explain &middot; apply &mdash; '
        'the through-line, with the store&rsquo;s numbers</span></span></a>'
        '<a class="trail" href="concept_usage.html"><b>&#9654; '
        '<span data-l="pt">Usar o programa</span><span data-l="en">Use the program</span></b>'
        '<span class="desc"><span data-l="pt">o fluxo montar &rarr; rodar &rarr; ler, com diagramas</span>'
        '<span data-l="en">the build &rarr; run &rarr; read flow, with diagrams</span></span></a>'
        '<a class="trail" href="../tutorial_uso/index.html"><b>&#128247; '
        '<span data-l="pt">Tutorial com telas reais</span><span data-l="en">Tutorial with real screens</span></b>'
        '<span class="desc"><span data-l="pt">prints de cada tela, do launch ao relat&oacute;rio &mdash; passo a passo</span>'
        '<span data-l="en">screenshots of every screen, launch to report &mdash; step by step</span></span></a>'
        '<a class="trail" href="concept_not-a-fit.html"><b>&#9671; '
        '<span data-l="pt">Entender o modelo</span><span data-l="en">Understand the model</span></b>'
        '<span class="desc"><span data-l="pt">por que PREVÊ e não interpola; equações e acoplamento</span>'
        '<span data-l="en">why it PREDICTS rather than interpolates; equations and coupling</span></span></a>'
        '<a class="trail" href="concept_gallery.html"><b>&#10003; '
        '<span data-l="pt">Ver a validação</span><span data-l="en">See the validation</span></b>'
        '<span class="desc"><span data-l="pt">modelo vs {{N_CURVAS}} curvas reais, estudos de caso e limitações</span>'
        '<span data-l="en">model vs {{N_CURVAS}} real curves, case studies and limits</span></span></a>'
        '</div>')
    hero = (f'<div class="foundations-hero">'
            f'<h2 class="sec"><span data-l="pt">Comece por aqui &mdash; isto NÃO é um ajuste de curva</span>'
            f'<span data-l="en">Start here &mdash; this is NOT a curve fit</span></h2>'
            f'<p class="intro"><span data-l="pt">O afrouxamento aqui é a evolução de um modelo '
            f'<b>massa-mola-amortecedor</b> físico (<code>[M]{{&uuml;}}+[C]{{&uacute;}}+[K(s)]{{u}}={{F}}</code>), '
            f'com leis de literatura nomeadas e constantes com procedência &mdash; não um polinômio ajustado. '
            f'As páginas de <b>Fundamentos</b> explicam as equações e o acoplamento:</span>'
            f'<span data-l="en">Loosening here is the evolution of a physical '
            f'<b>mass-spring-damper</b> model (<code>[M]{{&uuml;}}+[C]{{&uacute;}}+[K(s)]{{u}}={{F}}</code>), '
            f'with named literature laws and constants with provenance &mdash; not a fitted polynomial. '
            f'The <b>Foundations</b> pages explain the equations and coupling:</span></p>'
            f'{trails}'
            '<p class="intro"><span data-l="pt">Todas as páginas de Fundamentos:</span>'
            '<span data-l="en">All Foundations pages:</span></p>'
            f'<ul class="refs">{concept_links}</ul></div>' if CONCEPT_PAGES else "")
    return f"""<!doctype html>
<html lang="pt" data-theme="light" data-lang="pt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Explorador de Variáveis — BAS V2</title>
<style>{_BASE_CSS}{_CONCEPT_CSS}</style>
</head>
<body>
{sidebar}
<main class="main">
<div class="crumbs">&#8962; BAS V2</div>
<h1 class="name">Variable Explorer</h1>
{hero}
<div class="sub"><span data-l="pt">Documentação interativa das variáveis do modelo V2
  (<code>DynamicStiffnessAnalyzer</code>)</span>
  <span data-l="en">Interactive documentation of the V2 model variables
  (<code>DynamicStiffnessAnalyzer</code>)</span></div>

<div class="panel">
<p class="intro">
  <span data-l="pt">Uma página por campo de <code>JointMaterial</code> ({n} no total:
  {cat_line}). Escolha uma variável no sumário à esquerda. Cada página mostra a
  <b>curva-padrão</b> de afrouxamento (F/F0 vs ciclo) e um controle que muda a variável e
  <b>reforma a curva ao vivo</b>, mais a física, a equação e as referências de literatura.</span>
  <span data-l="en">One page per <code>JointMaterial</code> field ({n} total:
  {cat_line_en}). Pick a variable in the sidebar on the left. Each page shows the
  <b>standard</b> loosening curve (F/F0 vs cycle) and a control that changes the variable and
  <b>reshapes the curve live</b>, plus the physics, the equation and the literature references.</span>
</p>
<p class="intro">
  <span data-l="pt">Por padrão o sumário mostra só as <b>constantes físicas</b> (as ~10 do fit
  canônico). Use as caixas no topo do sumário para revelar também as <b>formas/modos</b>
  opt-in e as variáveis <b>numéricas/raras</b> (de efeito negligível na curva). A busca por
  texto encontra qualquer variável, independente dessas caixas.</span>
  <span data-l="en">By default the sidebar shows only the <b>physical constants</b> (the ~10 in
  the canonical fit). Use the checkboxes at the top of the sidebar to also reveal the opt-in
  <b>forms/modes</b> and the <b>numerical/rare</b> variables (negligible effect on the curve).
  The text search finds any variable regardless of those checkboxes.</span>
</p>
</div>

<div class="panel">
  <h2 class="sec"><span data-l="pt">A curva-padrão</span><span data-l="en">The standard curve</span></h2>
  <p><span data-l="pt">Salvo indicação, todas as curvas partem do mesmo ensaio de referência
  (rig UFU): parafuso <b>M16</b> em cisalhamento (Junker), arruela <b>nova</b>,
  pré-carga <b>F0 = 50 kN</b>, amplitude imposta <b>&delta; = 0.5 mm</b> a <b>0.5 Hz</b>,
  carga transversal (&theta; = 90&deg;), <b>2500 ciclos</b>, modo de deslocamento. As curvas
  são <b>pré-computadas pelo engine real</b> (<code>handle_simulate</code>) — não há física
  reimplementada em JavaScript. Alguns campos (fretting axial, fadiga, creep) usam um
  baseline <b>axial</b> ou de <b>creep</b>, indicado na própria página.</span>
  <span data-l="en">Unless noted, every curve starts from the same reference test (UFU rig):
  <b>M16</b> bolt in shear (Junker), <b>new</b> washer, preload <b>F0 = 50 kN</b>, imposed
  amplitude <b>&delta; = 0.5 mm</b> at <b>0.5 Hz</b>, transverse load (&theta; = 90&deg;),
  <b>2500 cycles</b>, displacement mode. Curves are <b>pre-computed by the real engine</b>
  (<code>handle_simulate</code>) — no physics is reimplemented in JavaScript. A few fields
  (axial fretting, fatigue, creep) use an <b>axial</b> or <b>creep</b> baseline, noted on the
  page itself.</span></p>
  <p class="legend">
    <span><i class="k" style="border-color:var(--accent)"></i>
      <span data-l="pt">constante física</span><span data-l="en">physical constant</span></span>
    <span><i class="k" style="border-color:var(--warn)"></i>
      <span data-l="pt">forma opt-in</span><span data-l="en">opt-in form</span></span>
    <span><i class="k" style="border-color:var(--ok)"></i>
      <span data-l="pt">modo discreto</span><span data-l="en">discrete mode</span></span>
    <span><i class="k" style="border-color:var(--muted)"></i>
      <span data-l="pt">numérico</span><span data-l="en">numerical</span></span>
  </p>
</div>
</main>
<script>{_SHELL_JS}</script>
</body>
</html>
"""


# Override CSS aplicado aos reports no explorador: mostra o INDICE inline no topo
# (o gerador so o exibe em telas >=1400px). As secoes seguem COLAPSAVEIS (default
# aberto, clique recolhe) — como no modelo do artifact.
_REPORT_OVERRIDE_CSS = """
<style>/* explorador: indice inline sempre visivel; secoes seguem colapsaveis */
@media screen{
  nav.toc{display:block!important;position:static!important;top:auto!important;left:auto!important;
    width:auto!important;max-width:960px;margin:8px auto 4px;padding:10px 16px;
    border:1px solid var(--bd);border-radius:8px;columns:2;line-height:1.9}
  nav.toc a{border-left:none;padding-left:0}
  nav.toc b{column-span:all}
}
</style>
"""


def _report_article_section(rec):
    """Secao 'Informacoes do artigo' (aparato/corpo-de-prova/matriz) renderizada
    da nota de aparato p/ INJETAR no report. Vazia se nao houver nota. Headings
    da nota como h3+ (min_h=3) p/ nao quebrar o wrapping colapsavel (h2[id^=sec])."""
    p = getattr(rec, "apparatus_note_path", None)
    if not p:
        return "", ""
    try:
        md = pathlib.Path(p).read_text(encoding="utf-8")
    except OSError:
        return "", ""
    sec = ('<h2 id="secart">Informações do artigo</h2>'
           '<p class="sub2">Aparato, corpo-de-prova, matriz de ensaios e caveats de '
           'digitalização (nota de aparato da biblioteca).</p>'
           + _md_to_html(md, min_h=3))
    toc = '<a href="#secart">Informações do artigo</a>'
    return sec, toc


def _write_case_reports(outdir):
    """Gera o report COMPLETO por caso (reusa validation.report_html.case_report_html,
    lendo o store canonico — sem re-simular). Decima as curvas p/ tamanho e corrige
    o link do report mestre p/ a galeria do explorador. Degrada em silencio se o
    pacote validation / store faltar. Retorna o set de cids com report escrito."""
    try:
        from bolt_analysis_studio.validation.store import ValidationStore
        from bolt_analysis_studio.validation.runner import CaseResult
        from bolt_analysis_studio.validation import report_html as _rh
        from bolt_analysis_studio.validation.case_registry import all_records
    except Exception:
        return set()
    try:
        st = ValidationStore()
        st.load()
    except Exception:
        return set()
    rdir = outdir / "reports"
    rdir.mkdir(parents=True, exist_ok=True)
    # ⚠️ PISO POR FONTE (D1), pelo MESMO caminho do `write_reports`:
    # `lim_sd=limite_sres(fonte, pisos)`. Sem isto o `case_report_html` cai no
    # `META_SRES` global e a pagina do explorador julga a 3a perna por uma regua
    # que NAO e' a vigente — exatamente o "meia-regua em cada lugar" que a
    # docstring dele nomeia como o defeito de 2026-07-29.
    # Medido em 2026-08-23 antes do conserto: 22 paginas discordavam do
    # documento mestre na DISTANCIA A ORIGEM e, em varias, na PERNA QUE MANDA
    # (`bauer2024_M8_fig6_rep4` 3,73x no explorador contra 1,71x no mestre;
    # `chu2026ti_D0p4mm_F0_49kN_test2` 7,64 contra 6,46). Nao era afrouxamento —
    # a pagina era INJUSTAMENTE SEVERA —, mas dois artefatos publicados
    # discordando sobre a mesma curva e' defeito de qualquer sinal.
    _pis = None
    try:
        _pares_piso = []
        for _r in all_records():
            if not _rh.caso_no_documento(_r.source, _r.case_id):
                continue
            _res = st.get(_r.case_id)
            if _res is not None and not getattr(_res, "error", None):
                _pares_piso.append((_r.source, _res))
        _pis = _rh._pisos_medidos(_pares_piso)
    except Exception:
        _pis = None
    done = set()
    for rec in all_records():
        # Fonte retirada: nao gera pagina, e APAGA a que existir. Sem o unlink o
        # arquivo antigo sobrevive no disco servindo um report que a galeria nao
        # linka mais — orfao que ainda abre e ainda parece oficial.
        if not _rh.caso_no_documento(rec.source, rec.case_id):
            velho = rdir / f"{rec.case_id}.html"
            if velho.exists():
                velho.unlink()
            continue
        try:
            res = st.get(rec.case_id)
        except Exception:
            res = None
        if res is None or getattr(res, "error", None) or not getattr(res, "cycles", None):
            continue
        d = res.to_dict()                              # decima cycles/ratio/decomp
        idx = _decim_idx(len(res.cycles), 130)
        d["cycles"] = [res.cycles[i] for i in idx]
        d["ratio"] = [res.ratio[i] for i in idx]
        dec = {}
        for m, arr in (res.decomp or {}).items():
            dec[m] = ([arr[i] for i in idx]
                      if isinstance(arr, list) and len(arr) == len(res.cycles) else arr)
        d["decomp"] = dec
        try:
            html = _rh.case_report_html(
                rec, CaseResult.from_dict(d), figpre="../paper_figures/",
                lim_sd=(_rh.limite_sres(rec.source, _pis)
                        if _pis is not None else None))
        except Exception:
            continue
        html = html.replace("../validation_report.html", "../concept_gallery.html")
        # importa a secao "Informacoes do artigo" (nota de aparato) — o item que
        # faltava no report — antes de Caveats (secao + entrada no indice)
        sec, toc = _report_article_section(rec)
        if sec:
            html = html.replace('<h2 id="sec6">6. Caveats e veredicto</h2>',
                                sec + '<h2 id="sec6">6. Caveats e veredicto</h2>', 1)
            html = html.replace('<a href="#sec6">6. Caveats</a>',
                                toc + '<a href="#sec6">6. Caveats</a>', 1)
        html = html.replace("</body>", _REPORT_OVERRIDE_CSS + "</body>")
        (rdir / f"{rec.case_id}.html").write_text(html, encoding="utf-8")
        done.add(rec.case_id)
    return done


def build(specs, outdir):
    validate_specs()
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    written = []
    _write_case_reports(outdir)                        # reports completos por caso
    ordered = _ordered(specs)
    for i, s in enumerate(ordered):
        res = sweep_variable(s)
        html = render_variable_page(s, res, all_specs=specs, cur_index=i)
        p = outdir / f"var_{s.name}.html"
        p.write_text(html, encoding="utf-8")
        written.append(p)
    # paginas conceituais ("Fundamentos")
    for page in CONCEPT_PAGES:
        html = render_concept_page(page, specs)
        p = outdir / f"concept_{page['slug']}.html"
        p.write_text(_subst_contagens(html), encoding="utf-8")
        written.append(p)
    # paginas de estudo de caso (uma por fonte)
    for sd in _study_sources():
        html = render_study_page(sd, specs)
        p = outdir / f"{sd['slug']}.html"
        p.write_text(_subst_contagens(html), encoding="utf-8")
        written.append(p)
    # Fonte retirada some de `_study_sources()` (o funil ja esta filtrado), mas
    # o `study_<fonte>.html` ANTIGO ficaria no disco: um estudo de caso completo,
    # com figuras do artigo e curvas, que o indice nao lista mais. Some da
    # navegacao e sobrevive na URL — o pior dos dois mundos. Apagar aqui, e nao
    # a mao, faz a limpeza acompanhar a decisao.
    try:
        from bolt_analysis_studio.validation import report_html as _rh_lim
        _retiradas = tuple(getattr(_rh_lim, "_SRC_RETIRADO", ()))
    except Exception:                                    # degrada sem raise
        _retiradas = ()
    for s in _retiradas:
        velho = outdir / f"study_{s.lower()}.html"
        if velho.exists():
            velho.unlink()
            print("  [retirada] removido %s" % velho.name)
    idx = outdir / "index.html"
    idx.write_text(_subst_contagens(render_index(specs)), encoding="utf-8")
    written.append(idx)
    return written


# ================================================================
# CONTEUDO — VARIABLE_SPECS (uma entrada por campo de JointMaterial)
# ================================================================

# ---- AMOSTRA (checkpoint): 6 campos cobrindo cada tipo de pagina ----
VARIABLE_SPECS.extend([
    VarSpec(
        name="emb_depth", symbol="delta_inf", unit="m", group="embedding",
        category="physical",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(5e-6, 60e-6, 15, "lin"),
        equation="delta_emb(N) = delta_inf * (1 - exp(-N/N_emb)),  delta_inf = emb_depth",
        physics_pt=(
            "<p>Quando duas superfícies metálicas são apertadas, elas nunca se tocam "
            "no plano ideal: o contato real acontece nos picos das asperezas de "
            "rugosidade. Sob a pré-carga esses picos escoam plasticamente e a junta "
            "\"assenta\" (embedding), perdendo uma pequena espessura. O parâmetro "
            "<code>emb_depth</code> (&delta;&#8734;) é a profundidade TOTAL desse "
            "assentamento — a folga geométrica que desaparece quando todas as "
            "asperezas já cederam.</p>"
            "<p>No modelo, a perda de aperto por embedding segue a forma exata de "
            "Norton, &delta;emb(N) = &delta;&#8734;&middot;(1&minus;e^(&minus;N/N_emb)), "
            "e converte-se em perda de força multiplicando pela rigidez do parafuso "
            "(&Delta;F = k_b&middot;&delta;emb). Por isso o embedding é o "
            "<b>maior responsável pela queda INICIAL</b> de F/F0 (o \"joelho\" nos "
            "primeiros ciclos). Mover o slider mostra isso diretamente: aumentar "
            "<code>emb_depth</code> aprofunda o degrau inicial; reduzir aproxima a "
            "curva de uma junta que já chegou assentada de fábrica.</p>"
            "<p>Historicamente este era o campo mais delicado da calibração: o default "
            "subiu de 12 &micro;m para 30 &micro;m (2026-06-20) porque a queda íngreme "
            "do M16 shear excedia a assíntota de 12 &micro;m. Hoje o valor NÃO é um "
            "botão livre — é um <b>INPUT por junta</b>, lido da classe de rugosidade Rz "
            "na tabela f_Z da VDI 2230 (lição L24, \"ler em vez de fitar\"). O default de "
            "30 &micro;m só vale para o rig UFU; outra junta pede outra classe Rz.</p>"),
        physics_en=(
            "<p>When two metal surfaces are clamped they never meet on the ideal plane: "
            "real contact happens at the peaks of the roughness asperities. Under "
            "preload those peaks yield plastically and the joint \"beds in\" "
            "(embedding), losing a small thickness. The parameter <code>emb_depth</code> "
            "(&delta;&#8734;) is the TOTAL depth of that settling — the geometric slack "
            "that vanishes once every asperity has yielded.</p>"
            "<p>In the model, the embedding preload loss follows the exact Norton form, "
            "&delta;emb(N) = &delta;&#8734;&middot;(1&minus;e^(&minus;N/N_emb)), and "
            "becomes a force loss by multiplying by the bolt stiffness "
            "(&Delta;F = k_b&middot;&delta;emb). This makes embedding the <b>largest "
            "contributor to the INITIAL</b> F/F0 drop (the early-cycle \"knee\"). Moving "
            "the slider shows it directly: raising <code>emb_depth</code> deepens the "
            "initial step; lowering it makes the curve look like a joint that arrived "
            "already bedded.</p>"
            "<p>Historically this was the trickiest calibration field: the default rose "
            "from 12 &micro;m to 30 &micro;m (2026-06-20) because the steep M16-shear "
            "drop exceeded the 12 &micro;m asymptote. Today the value is NOT a free knob "
            "— it is a <b>PER-joint INPUT</b>, read from the Rz roughness class in the "
            "VDI 2230 f_Z table (lesson L24, \"read instead of fit\"). The 30 &micro;m "
            "default only fits the UFU rig; another joint calls for another Rz class.</p>"),
        anchor_key="emb_depth",
        lessons=["L24"],
        refs=[("VDI 2230 — tabela f_Z de assentamento por classe de rugosidade",
               "VDI 2230 — f_Z embedding table by roughness class", "VDI 2230"),
              ("§4.1 EmbeddingLoss (forma geométrica exata, state-based)",
               "§4.1 EmbeddingLoss (exact geometric, state-based)",
               "MODEL_MATH_REFERENCE.md")],
        related=["N_emb", "emb_load_frac"]),

    VarSpec(
        name="C_creep", symbol="C_creep", unit="m/(log-dec.Pa)", group="creep",
        category="physical",
        context={"baseline": "creep", "overrides": {}},
        sweep=(1e-12, 1e-10, 15, "log"),
        equation="delta_creep(t) = C_creep * F_0 * log(t/t_0 + 1)",
        physics_pt=(
            "Coeficiente de creep logarítmico (Norton-Bailey) da interface sob "
            "pré-carga. O assentamento lento cresce com o log do tempo e escala "
            "com F_0, produzindo a CAUDA lenta da curva (perda continuada muito "
            "depois do assentamento inicial). Aumentar <code>C_creep</code> "
            "inclina essa cauda. É POR PAR tribológico, não universal: a âncora "
            "304SS (~1e-12) e o fit UFU (~1.2e-11) têm intervalos de confiança "
            "disjuntos; o bloco 'shared' canônico mantém o valor UFU."),
        physics_en=(
            "Logarithmic creep coefficient (Norton-Bailey) of the interface under "
            "preload. The slow settling grows with log-time and scales with F_0, "
            "producing the slow TAIL of the curve (continued loss well after the "
            "initial bedding). Raising <code>C_creep</code> tilts that tail. It is "
            "PER tribological pair, not universal: the 304SS anchor (~1e-12) and "
            "the UFU fit (~1.2e-11) have disjoint confidence intervals; the "
            "canonical 'shared' block keeps the UFU value."),
        anchor_key="C_creep_por_par",
        refs=[("§4.2 CreepLoss (Norton-Bailey logarítmico)",
               "§4.2 CreepLoss (logarithmic Norton-Bailey)", "MODEL_MATH_REFERENCE.md"),
              ("§4.7 MODEL_LEGITIMACY — C_creep é por par (ICs disjuntos)",
               "§4.7 MODEL_LEGITIMACY — C_creep is per-pair (disjoint CIs)",
               "MODEL_LEGITIMACY.md")],
        related=["t_0", "creep_conform_exp"]),

    VarSpec(
        name="mu_thread", symbol="mu_t", unit="-", group="friction",
        category="physical",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(0.05, 0.30, 15, "lin"),
        equation="T_resist = mu_t * F_0 * (d_2/2) * ...  (torque de atrito de rosca)",
        physics_pt=(
            "Coeficiente de atrito no flanco da rosca. Governa o torque resistivo "
            "que se opõe ao afrouxamento rotacional: atrito maior segura o "
            "parafuso (curva mais rasa), atrito menor libera (afrouxa mais rápido). "
            "A leitura de procedência abaixo do gráfico avisa quando o valor sai "
            "da banda MEDIDA de aço seco (Pai/Hess, Qiao 2025). Lido ATRAVÉS do "
            "engine (não há um único 'mu efetivo' — depende do nut factor)."),
        physics_en=(
            "Friction coefficient on the thread flank. It governs the resisting "
            "torque that opposes rotational loosening: higher friction holds the "
            "bolt (shallower curve), lower friction releases it (faster loosening). "
            "The provenance readout under the plot flags when the value leaves the "
            "MEASURED dry-steel band (Pai/Hess, Qiao 2025). Read THROUGH the engine "
            "(there is no single 'effective mu' — it depends on the nut factor)."),
        anchor_key="mu_dry",
        refs=[("Pai & Hess (2002) — atrito e afrouxamento por escorregamento",
               "Pai & Hess (2002) — friction and slip loosening", "pai2002"),
              ("§3 constantes de material/contato",
               "§3 material/contact constants", "MODEL_MATH_REFERENCE.md")],
        related=["mu_bearing"]),

    VarSpec(
        name="c_D", symbol="c_D", unit="-", group="damage",
        category="physical",
        context={"baseline": "transverse",
                 "overrides": {"k_dmg_mu": 1.0, "k_dmg_wear": 4.0}},
        sweep=(0.0, 5.0, 15, "lin"),
        equation="dD/dN = c_D * (W_slip / W_ref) * (1 - D);   D in [0,1]",
        physics_pt=(
            "Taxa de crescimento do dano de superfície <code>D</code> (reaperto/"
            "TP7). D não é um mecanismo em paralelo: ele MODULA o atrito de bearing "
            "(mu cai com D) e AMPLIFICA o wear (d_wear cresce com D), sendo "
            "alimentado pela dissipação de escorregamento por ciclo. Com c_D=0 o "
            "engine reproduz o comportamento pré-dano; aumentar c_D acelera o "
            "COLAPSO tardio (queda abrupta de F0). Aqui os companheiros "
            "<code>k_dmg_mu</code>/<code>k_dmg_wear</code> estão ligados para o "
            "acoplamento aparecer."),
        physics_en=(
            "Growth rate of surface damage <code>D</code> (retighten/TP7). D is not "
            "a parallel mechanism: it MODULATES bearing friction (mu falls with D) "
            "and AMPLIFIES wear (d_wear grows with D), fed by the per-cycle slip "
            "dissipation. With c_D=0 the engine reproduces pre-damage behaviour; "
            "raising c_D speeds up the late COLLAPSE (abrupt F0 drop). Here the "
            "companions <code>k_dmg_mu</code>/<code>k_dmg_wear</code> are enabled so "
            "the coupling shows."),
        refs=[("§4 / surface_damage — modula atrito e amplifica wear",
               "§4 / surface_damage — modulates friction, amplifies wear",
               "MODEL_MATH_REFERENCE.md"),
              ("staged-calibration-leverage — design do surface_damage",
               "staged-calibration-leverage — surface_damage design",
               "specs/2026-06-20-staged-calibration-leverage-design.md")],
        related=["k_dmg_mu", "k_dmg_wear", "W_ref"]),

    VarSpec(
        name="k_tr_mode", symbol="", unit="", group="slip_regime",
        category="mode",
        context={"baseline": "transverse", "overrides": {}},
        choices=["axial_frac", "bending"],
        equation='k_tr = 0.3*k_j_init  ("axial_frac")  |  c_bend*E*I/L^3  ("bending")',
        physics_pt=(
            "Modo de cálculo da rigidez transversal <code>k_tr</code>, que fixa o "
            "escorregamento por ciclo a partir do deslocamento imposto. "
            "<b>axial_frac</b> (default): k_tr ~ fração da rigidez de contato -> "
            "delta_t ~ 0, tudo vira gross slip. <b>bending</b>: usa a rigidez de "
            "FLEXÃO do parafuso (~E*I/L^3), muito menor -> delta_t da ordem de "
            "décimos de mm, separando micro-slip de gross-slip. O seletor troca "
            "entre as duas curvas pré-computadas."),
        physics_en=(
            "Compute mode for the transverse stiffness <code>k_tr</code>, which "
            "sets the per-cycle slip from the imposed displacement. <b>axial_frac</b> "
            "(default): k_tr ~ a fraction of contact stiffness -> delta_t ~ 0, all "
            "gross slip. <b>bending</b>: uses the bolt BENDING stiffness (~E*I/L^3), "
            "much lower -> delta_t of order tenths of a mm, separating micro-slip "
            "from gross-slip. The selector switches between the two pre-computed "
            "curves."),
        refs=[("§5.1 modos de formulação (campos string)",
               "§5.1 formulation modes (string fields)", "MODEL_MATH_REFERENCE.md"),
              ("slip-regime-ktr-fix — design",
               "slip-regime-ktr-fix — design", "specs/2026-07-05-slip-regime-ktr-fix-design.md")],
        related=["c_bend", "slip_regime_mode"]),

    VarSpec(
        name="m_x", symbol="m_x", unit="kg", group="numerical",
        category="numerical", negligible=True,
        context={"baseline": "transverse", "overrides": {}},
        sweep=(0.1, 2.0, 8, "lin"),
        equation="[M] diag(m_x, m_y, I_theta)  — massa efetiva do no",
        physics_pt=(
            "Massa efetiva na direção x da matriz [M] do modelo dinâmico. O modelo "
            "de afrouxamento é QUASE-ESTÁTICO por ciclo (a evolução lenta de F0 vem "
            "dos mecanismos de perda, não da inércia), então variar <code>m_x</code> "
            "praticamente NÃO muda a curva F/F0. Existe para o balanço dinâmico "
            "[M]/[C] e o damping de Rayleigh; é mostrado aqui por completude."),
        physics_en=(
            "Effective mass in the x direction of the dynamic model matrix [M]. The "
            "loosening model is QUASI-STATIC per cycle (the slow F0 evolution comes "
            "from the loss mechanisms, not from inertia), so varying <code>m_x</code> "
            "barely changes the F/F0 curve. It exists for the dynamic [M]/[C] "
            "balance and Rayleigh damping; shown here for completeness."),
        refs=[("§3 massa efetiva / [M]", "§3 effective mass / [M]",
               "MODEL_MATH_REFERENCE.md")],
        related=["m_y", "I_theta", "rayleigh_alpha"]),
])


# ================================================================
# PAGINAS CONCEITUAIS ("Fundamentos") — didaticas + interativas
# ================================================================
_MECH_KEYS = ["embedding", "creep", "wear", "rotational_loosening", "thread_fretting"]


def _csim(overrides, baseline="transverse"):
    """Curva {N,ratio} decimada p/ um payload de conceito."""
    base = BASELINES[baseline]()
    base["mat"] = dict(overrides) if overrides else {"emb_depth": 30e-6}
    out = handle_simulate(base)
    N, ratio = _decimate(out["curve"]["N"], out["curve"]["ratio"])
    return {"N": N, "ratio": ratio}


def _cdecomp(baseline="transverse", extra=None, n_cycles=None):
    """Decomposicao cumulativa por mecanismo (fracao de F0_init) + curva total,
    na mesma grade decimada. Os mecanismos somam ~exatamente (1 - ratio).
    `extra` (opcional) mescla overrides no material (ex.: cenario auto-travamento);
    `n_cycles` (opcional) sobrescreve a janela (ex.: incubacao precisa de N alto
    p/ o colapso caber apos o plato)."""
    base = BASELINES[baseline]()
    if n_cycles:
        base["loading"]["N"] = int(n_cycles)
    F0 = base["loading"]["F0_init"]
    mat = {"emb_depth": 30e-6, "C_creep": 5e-11, "tr_loose_gain": 2.0}
    if extra:
        mat.update(extra)
    base["mat"] = mat
    out = handle_simulate(base)
    Nfull, ratio = out["curve"]["N"], out["curve"]["ratio"]
    dec = out["decomposition"]
    running = {m: 0.0 for m in _MECH_KEYS}
    cum = {m: [0.0] for m in _MECH_KEYS}       # prepend 0 (alinha com N[0]=0)
    n = len(dec[_MECH_KEYS[0]])
    for i in range(n):
        for m in _MECH_KEYS:
            running[m] += abs(dec[m][i])
            cum[m].append(running[m] / F0)
    idx = _decim_idx(len(Nfull))
    return {"N": [int(Nfull[i]) for i in idx],
            "ratio": [round(float(ratio[i]), 4) for i in idx],
            "mechs": {m: [round(cum[m][i], 4) for i in idx] for m in _MECH_KEYS}}


def _anatomy_scenario(sid, label_pt, label_en, extra, xmode="log", staging="loss",
                      n_cycles=None):
    """Um cenario da anatomia: curva + faixas de estagio + mecanismo dominante
    POR PONTO (p/ o scrubber) + joelho + piso. Tudo do decomp real.
    `staging="loss"` = 3 estagios por fracao de perda (curva de decaimento);
    `staging="incubation"` = assentamento/incubacao/colapso (joelho = descida
    mais ingreme apos o assentamento — p/ curvas com inflexao acentuada).
    `xmode` = eixo X do cenario ("log" p/ front-loaded, "linear" p/ joelho tardio)."""
    d = _cdecomp("transverse", extra=extra, n_cycles=n_cycles)
    N, r, mechs = d["N"], d["ratio"], d["mechs"]
    total = max(r[0] - r[-1], 1e-9)

    def _idx_at_loss(frac):
        tgt = r[0] - frac * total
        for i, rv in enumerate(r):
            if rv <= tgt:
                return i
        return len(r) - 1

    if staging == "incubation":
        # deteccao por INCLINACAO (o assentamento inicial e' mais ingreme que o
        # colapso, entao fracao-de-perda nao serve): assentamento = ate a
        # inclinacao cair; joelho = onde ela re-ingrema apos o plato.
        sl = [0.0] + [max(0.0, r[i - 1] - r[i]) for i in range(1, len(r))]
        head = max(3, len(r) // 8)
        smax0 = max(sl[1:head]) or 1e-9         # pico do assentamento inicial
        a1 = head
        for i in range(2, len(r)):              # fim do assentamento
            if sl[i] < 0.20 * smax0 and (r[0] - r[i]) > 0.15:
                a1 = i
                break
        flat, smin = a1, 1e9                    # ponto MAIS plano apos o assentamento
        for i in range(a1, len(r) - 1):
            if sl[i] < smin:
                smin, flat = sl[i], i
        thr = max(smin * 3.0, smax0 * 0.06, 1e-4)
        knee = min(flat + 1, len(r) - 2)
        for i in range(flat + 1, len(r)):       # onset do colapso: re-ingremar apos o plato
            if sl[i] > thr:
                knee = i
                break
        bounds = [0, a1, knee, len(r) - 1]
        labs = [("I", "assentamento", "settling"), ("II", "incubação", "incubation"),
                ("III", "colapso", "collapse")]
        knee_idx = knee
    else:
        bounds = [0, _idx_at_loss(0.45), _idx_at_loss(0.80), len(r) - 1]
        labs = [("I", "assentamento", "settling"), ("II", "afrouxamento", "loosening"),
                ("III", "cauda", "tail")]
        knee_idx = bounds[1]
    dom = []                                    # mecanismo dominante por ponto
    for i in range(len(N)):
        j = max(1, i)
        inc = {m: mechs[m][j] - mechs[m][j - 1] for m in mechs}
        dom.append(max(inc, key=inc.get) if inc else "embedding")
    stages = []
    for k, (rn, sp, se) in enumerate(labs):
        a, b = bounds[k], bounds[k + 1]
        inc = {m: mechs[m][b] - mechs[m][a] for m in mechs}
        stages.append({"roman": rn, "name_pt": sp, "name_en": se,
                       "start_N": int(N[a]), "end_N": int(N[b]),
                       "dom": (max(inc, key=inc.get) if inc else "embedding")})
    return {"id": sid, "label_pt": label_pt, "label_en": label_en, "xmode": xmode,
            "N": N, "ratio": r, "dom": dom, "stages": stages,
            "knee": int(N[knee_idx]), "floor": round(r[-1], 3)}


def _widget_data(sim):
    """Precomputa os dados do widget interativo (roda o engine real)."""
    if sim == "f0_sweep":
        curves = []
        for f in (30000.0, 40000.0, 50000.0, 60000.0, 70000.0):
            b = BASELINES["transverse"]()
            b["loading"]["F0_init"] = f
            b["loading"]["F_amp"] = 0.4 * f
            b["mat"] = {"emb_depth": 30e-6, "C_creep": 5e-11, "tr_loose_gain": 2.0}
            o = handle_simulate(b)
            N, r = _decimate(o["curve"]["N"], o["curve"]["ratio"])
            curves.append({"value": f / 1000.0, "N": N, "ratio": r})
        return {"kind": "plot", "control": "slider", "unit": "kN", "curves": curves,
                "start_idx": 2,
                "note_pt": "Mesmas constantes físicas, só F0 muda: o modelo PREVÊ cada curva "
                           "(zero-refit). Um ajuste de curva precisaria de novos coeficientes "
                           "para cada F0.",
                "note_en": "Same physical constants, only F0 changes: the model PREDICTS each "
                           "curve (zero-refit). A curve fit would need new coefficients for each F0."}
    if sim == "runaway":
        ctx = {"loose_torsion_mode": "bolt_torsion", "loosening_slip_coupling": "gross_fraction",
               "k_tr_mode": "bending", "eta_loose": 8.0}
        c0 = _csim({**ctx, "loose_arrest_floor": 0.0})
        c1 = _csim({**ctx, "loose_arrest_floor": 0.08})
        return {"kind": "plot", "control": "select",
                "curves": [{"value_pt": "runaway (sem arresto)", "value_en": "runaway (no arrest)",
                            "N": c0["N"], "ratio": c0["ratio"]},
                           {"value_pt": "auto-travamento (F_min)", "value_en": "self-locking (F_min)",
                            "N": c1["N"], "ratio": c1["ratio"]}],
                "start_idx": 0,
                "note_pt": "Mesmo laço de realimentação F0->[K]->Phi->afrouxamento->F0. O piso de "
                           "auto-travamento (loose_arrest_floor) transforma o runaway até zero numa "
                           "S-curve com ponto fixo estável.",
                "note_en": "Same feedback loop F0->[K]->Phi->loosening->F0. The self-locking floor "
                           "(loose_arrest_floor) turns the runaway-to-zero into an S-curve with a "
                           "stable fixed point."}
    if sim == "decomp":
        d = _cdecomp("transverse")
        d["kind"] = "stack"
        d["note_pt"] = ("Cada faixa é a parcela FÍSICA de um mecanismo na perda de pré-carga; "
                        "empilhadas somam a linha tracejada (1 - F/F0). Desligue um mecanismo para "
                        "ver sua contribuição. Nada é ajustado a posteriori.")
        d["note_en"] = ("Each band is one mechanism's PHYSICAL share of the preload loss; stacked "
                        "they sum to the dashed line (1 - F/F0). Toggle a mechanism to see its "
                        "contribution. Nothing is fitted afterwards.")
        return d
    if sim == "energy":
        d = _cdecomp("transverse")
        fin = {m: d["mechs"][m][-1] for m in _MECH_KEYS}
        items = [{"key": "embedding", "label_pt": "Embedding (assentamento)", "label_en": "Embedding", "value": round(fin["embedding"], 4)},
                 {"key": "creep", "label_pt": "Creep", "label_en": "Creep", "value": round(fin["creep"], 4)},
                 {"key": "wear", "label_pt": "Desgaste (Archard)", "label_en": "Wear (Archard)", "value": round(fin["wear"], 4)},
                 {"key": "rotational_loosening", "label_pt": "Afrouxamento (two-factor)", "label_en": "Loosening (two-factor)", "value": round(fin["rotational_loosening"], 4)}]
        return {"kind": "bars", "items": items, "total": round(1 - d["ratio"][-1], 4),
                "note_pt": "Balanço de perda: cada mecanismo entrega uma parcela; a soma = 1 - F/F0 "
                           "final. O engine também fecha o balanço de energia (W_ext + dU = sum "
                           "W_diss, residual ~ 0).",
                "note_en": "Loss budget: each mechanism delivers a share; the sum = 1 - final F/F0. "
                           "The engine also closes the energy balance (W_ext + dU = sum W_diss, "
                           "residual ~ 0)."}
    if sim == "predict_liu2025":
        # Overlay previsao-vs-dado: UMA config fisica (LIU_2025 adotada, procedencia
        # declarada) reproduz as 6 amplitudes de um estudo INDEPENDENTE. So a amplitude
        # muda de curva p/ curva; os coeficientes nao. Curva do modelo = store canonico.
        want = ["liu2025_M16_amp0p25", "liu2025_M16_amp0p3", "liu2025_M16_amp0p4",
                "liu2025_M16_amp0p5", "liu2025_M16_amp0p6", "liu2025_M16_amp0p8"]
        by = {c["cid"]: c for c in _validation_cases()}
        # "Interpolacao" = a forma do ensaio de 0.25 mm (ajuste a UMA condicao),
        # aplicada SEM MUDAR a cada amplitude. Sabe fitar 0.25; nao sabe fisica.
        ref = by.get("liu2025_M16_amp0p25")
        fr, rr = [], []
        if ref and ref["data_N"] and ref["data_N"][-1] > 0:
            nend = float(ref["data_N"][-1])
            fr = [n / nend for n in ref["data_N"]]
            rr = list(ref["data_r"])

        def _interp025(t):
            if not fr:
                return 1.0
            t = min(1.0, max(0.0, t))
            for k in range(1, len(fr)):
                if fr[k] >= t:
                    f0, f1 = fr[k - 1], fr[k]
                    w = (t - f0) / (f1 - f0) if f1 > f0 else 0.0
                    return rr[k - 1] + w * (rr[k] - rr[k - 1])
            return rr[-1]

        series = []
        for cid in want:
            c = by.get(cid)
            if not c:
                continue
            lab = f"±{c['amp_mm']:.2f} mm"
            mend = float(c["model_N"][-1]) or 1.0
            interp_r = [round(_interp025(n / mend), 4) for n in c["model_N"]]
            dend = float(c["data_N"][-1]) or 1.0
            ie = [abs(_interp025(dn / dend) - dr) for dn, dr in zip(c["data_N"], c["data_r"])]
            interp_mae = round(sum(ie) / len(ie), 4) if ie else 0.0
            series.append({"label_pt": lab, "label_en": lab,
                           "model_N": c["model_N"], "model_r": c["model_r"],
                           "data_N": c["data_N"], "data_r": c["data_r"],
                           "interp_r": interp_r, "interp_mae": interp_mae,
                           "mae": c["mae"], "final_pred": c["final_pred"],
                           "final_data": c["final_data"]})
        if not series:
            return None
        start = next((i for i, s in enumerate(series) if "0.50" in s["label_pt"]),
                     len(series) // 2)
        return {"kind": "overlay", "control": "select", "series": series,
                "start_idx": start,
                "note_pt": ("Pontos = medidas de Liu et al. (2025) &mdash; M16 8.8, F0 = 60 kN, "
                            "12.5 Hz. A linha CHEIA é o MODELO; a linha TRACEJADA é uma "
                            "INTERPOLAÇÃO ajustada ao ensaio de 0.25 mm e aplicada sem mudar. "
                            "Troque a amplitude: a interpolação acerta SÓ em 0.25 mm (onde foi "
                            "ajustada) e erra cada vez mais longe dela; o modelo &mdash; a MESMA "
                            "configuração física &mdash; prevê todas. Veja o MAE de cada um no "
                            "topo: o da interpolação dispara, o do modelo fica baixo."),
                "note_en": ("Dots = measurements from Liu et al. (2025) &mdash; M16 8.8, F0 = 60 kN, "
                            "12.5 Hz. The SOLID line is the MODEL; the DASHED line is an "
                            "INTERPOLATION fitted to the 0.25 mm test and applied unchanged. Switch "
                            "amplitude: the interpolation is right ONLY at 0.25 mm (where it was "
                            "fitted) and drifts ever further away; the model &mdash; the SAME physical "
                            "configuration &mdash; predicts them all. Compare each MAE at the top: "
                            "the interpolation's blows up, the model's stays low.")}
    if sim == "gallery":
        cases = _validation_cases()
        if not cases:
            return None
        import statistics as _st
        from collections import OrderedDict
        maes = [c["mae"] for c in cases]
        by = OrderedDict()
        for c in cases:
            by.setdefault(c["source"], []).append(c)
        sources = []
        for s, cs in by.items():
            name, bp, be = _source_label(s)
            sources.append({"source": s, "name": name, "blurb_pt": bp, "blurb_en": be,
                            "count": len(cs),
                            "median_mae": round(_st.median([x["mae"] for x in cs]), 3)})
        sources.sort(key=lambda x: x["name"])
        fam = {}
        for c in cases:
            fam[c["family"]] = fam.get(c["family"], 0) + 1
        stats = {"n": len(cases), "n_sources": len(by),
                 "median_mae": round(_st.median(maes), 3),
                 "mean_mae": round(sum(maes) / len(maes), 3),
                 "n_over": sum(1 for m in maes if m > 0.1), "families": fam}
        return {"kind": "gallery", "cases": cases, "sources": sources, "stats": stats}
    if sim == "anatomy":
        sl = dict(loose_torsion_mode="bolt_torsion", loosening_slip_coupling="gross_fraction",
                  k_tr_mode="bending", eta_loose=8.0, loose_arrest_floor=0.6)
        inc = dict(slip_onset_W=20000.0, slip_onset_sharpness=8.0)
        scenarios = [
            _anatomy_scenario("runaway", "padrão (runaway)", "standard (runaway)", None),
            _anatomy_scenario("selflock", "com auto-travamento", "with self-locking", sl),
            _anatomy_scenario("incubation", "incubação (joelho acentuado)",
                              "incubation (sharp knee)", inc,
                              xmode="linear", staging="incubation", n_cycles=5000)]
        nm_pt = {"embedding": "assentamento", "creep": "creep", "wear": "desgaste",
                 "rotational_loosening": "afrouxamento", "thread_fretting": "fretting",
                 "fatigue": "fadiga"}
        nm_en = {"embedding": "embedding", "creep": "creep", "wear": "wear",
                 "rotational_loosening": "loosening", "thread_fretting": "fretting",
                 "fatigue": "fatigue"}
        return {"kind": "anatomy", "scenarios": scenarios, "start_idx": 0,
                "mech_pt": nm_pt, "mech_en": nm_en,
                "note_pt": ("Arraste o cursor sobre a curva: o painel mostra o ciclo, a pré-carga, o "
                            "estágio e o mecanismo dominante ALI. Três cenários da MESMA junta: "
                            "&lt;b&gt;runaway&lt;/b&gt; (cai a ~0), &lt;b&gt;auto-travamento&lt;/b&gt; (estabiliza num piso) e "
                            "&lt;b&gt;incubação&lt;/b&gt; &mdash; um platô longo (afrouxamento represado pela "
                            "incubação) seguido de um COLAPSO de joelho acentuado, a forma de 3 "
                            "estágios clássica (Junker). Os dois primeiros usam eixo X log "
                            "(front-loaded); a incubação usa X linear, onde o joelho tardio aparece "
                            "melhor."),
                "note_en": ("Drag the cursor over the curve: the panel shows the cycle, preload, "
                            "stage and dominant mechanism THERE. Three scenarios of the SAME joint: "
                            "&lt;b&gt;runaway&lt;/b&gt; (falls to ~0), &lt;b&gt;self-locking&lt;/b&gt; (stabilizes at a floor) "
                            "and &lt;b&gt;incubation&lt;/b&gt; &mdash; a long plateau (loosening held back by "
                            "incubation) followed by a sharp-knee COLLAPSE, the classic 3-stage "
                            "(Junker) shape. The first two use a log X axis (front-loaded); "
                            "incubation uses a linear X, where the late knee shows better.")}
    return None


_STACK_JS = """
(function(){ if(typeof SDATA==='undefined'||!SDATA) return;
  const root=document.documentElement, cs=getComputedStyle(root), col=n=>cs.getPropertyValue(n).trim();
  const host=document.getElementById('cw'); if(!host) return;
  const cv=host.querySelector('canvas'), ctx=cv.getContext('2d');
  const ctrl=host.querySelector('.cw-ctrl'); const note=host.querySelector('.cw-note');
  const MECHS=[['embedding','Embedding','Embedding','--accent'],
               ['creep','Creep','Creep','--ok'],
               ['wear','Desgaste (Archard)','Wear (Archard)','--accent2'],
               ['rotational_loosening','Afrouxamento','Loosening','--warn']];
  const N=SDATA.N, xmax=Math.max(1,...N), PAD={l:54,r:12,t:12,b:34};
  const shown={}; MECHS.forEach(m=>shown[m[0]]=true);
  const L=()=>root.dataset.lang==='pt'?1:2;
  function draw(){const w=cv.clientWidth||820,h=Math.round(w*0.46),dpr=window.devicePixelRatio||1;
    cv.width=w*dpr;cv.height=h*dpr;cv.style.height=h+'px';ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    let ymax=0.02; for(let i=0;i<N.length;i++){let s=0;MECHS.forEach(m=>{if(shown[m[0]])s+=SDATA.mechs[m[0]][i];});if(s>ymax)ymax=s;}
    for(let i=0;i<N.length;i++){const t=1-SDATA.ratio[i]; if(t>ymax)ymax=t;} ymax*=1.08;
    const X=n=>PAD.l+(n/xmax)*(w-PAD.l-PAD.r), Y=v=>PAD.t+(1-v/ymax)*(h-PAD.t-PAD.b);
    ctx.strokeStyle=col('--line');ctx.fillStyle=col('--muted');ctx.font="11px 'Segoe UI',sans-serif";ctx.lineWidth=1;
    ctx.textAlign='right';ctx.textBaseline='middle';
    for(let g=0;g<=4;g++){const v=ymax*g/4,y=Y(v);ctx.globalAlpha=.5;ctx.beginPath();ctx.moveTo(PAD.l,y);ctx.lineTo(w-PAD.r,y);ctx.stroke();ctx.globalAlpha=1;ctx.fillText(v.toFixed(2),PAD.l-6,y);}
    ctx.textAlign='center';ctx.textBaseline='top';for(let g=0;g<=4;g++){const n=Math.round(xmax*g/4);ctx.fillText(n,X(n),h-PAD.b+6);}
    ctx.save();ctx.translate(12,h/2);ctx.rotate(-Math.PI/2);ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(L()===1?'perda F/F0 (fração)':'F/F0 loss (fraction)',0,0);ctx.restore();
    ctx.textAlign='center';ctx.fillText(L()===1?'ciclo':'cycle',(PAD.l+w-PAD.r)/2,h-13);
    let base=new Array(N.length).fill(0);
    MECHS.forEach(m=>{ if(!shown[m[0]])return; const c=SDATA.mechs[m[0]];
      ctx.beginPath();
      for(let i=0;i<N.length;i++){const x=X(N[i]),y=Y(base[i]+c[i]);i?ctx.lineTo(x,y):ctx.moveTo(x,y);}
      for(let i=N.length-1;i>=0;i--)ctx.lineTo(X(N[i]),Y(base[i]));
      ctx.closePath();ctx.fillStyle=col(m[3]);ctx.globalAlpha=.5;ctx.fill();ctx.globalAlpha=1;
      for(let i=0;i<N.length;i++)base[i]+=c[i]; });
    ctx.strokeStyle=col('--ink');ctx.lineWidth=1.6;ctx.setLineDash([5,3]);ctx.beginPath();
    for(let i=0;i<N.length;i++){const x=X(N[i]),y=Y(1-SDATA.ratio[i]);i?ctx.lineTo(x,y):ctx.moveTo(x,y);}ctx.stroke();ctx.setLineDash([]);
  }
  MECHS.forEach(m=>{const l=document.createElement('label');l.className='cw-leg';
    const cb=document.createElement('input');cb.type='checkbox';cb.checked=true;cb.onchange=()=>{shown[m[0]]=cb.checked;draw();};
    const sw=document.createElement('i');sw.className='k';sw.style.borderColor=col(m[3]);sw.style.background=col(m[3]);
    const tx=document.createElement('span');tx.dataset.mi=m[0]; l.appendChild(cb);l.appendChild(sw);l.appendChild(tx);ctrl.appendChild(l);});
  window._cwRefresh=()=>{ if(note)note.textContent=SDATA['note_'+(L()===1?'pt':'en')]||'';
    host.querySelectorAll('[data-mi]').forEach(s=>{const m=MECHS.find(x=>x[0]===s.dataset.mi);s.textContent=(L()===1?m[1]:m[2]);}); draw(); };
  window.addEventListener('resize',draw); window._cwRefresh();
})();
"""

_BARS_JS = """
(function(){ if(typeof BDATA==='undefined'||!BDATA) return;
  const root=document.documentElement, cs=getComputedStyle(root), col=n=>cs.getPropertyValue(n).trim();
  const host=document.getElementById('cw'); if(!host) return;
  const COL={embedding:'--accent',creep:'--ok',wear:'--accent2',rotational_loosening:'--warn'};
  const wrap=host.querySelector('.bars'), note=host.querySelector('.cw-note');
  const mx=Math.max(...BDATA.items.map(i=>i.value),0.0001);
  const L=()=>root.dataset.lang==='pt'?'pt':'en';
  function draw(){wrap.innerHTML='';
    BDATA.items.forEach(it=>{const row=document.createElement('div');row.className='bar-row';
      const lab=document.createElement('span');lab.className='bar-lab';lab.textContent=it['label_'+L()];
      const track=document.createElement('span');track.className='bar-track';
      const fill=document.createElement('span');fill.className='bar-fill';fill.style.width=(100*it.value/mx)+'%';fill.style.background=col(COL[it.key]||'--accent');
      const val=document.createElement('span');val.className='bar-val';val.textContent=it.value.toFixed(3);
      track.appendChild(fill);row.appendChild(lab);row.appendChild(track);row.appendChild(val);wrap.appendChild(row);});
    const s=BDATA.items.reduce((a,i)=>a+i.value,0);
    const t=document.createElement('div');t.className='bar-total';
    t.textContent=(L()==='pt'?'soma = ':'sum = ')+s.toFixed(3)+(L()==='pt'?'  \\u2248  1 - F/F0 final = ':'  \\u2248  1 - final F/F0 = ')+BDATA.total.toFixed(3);
    wrap.appendChild(t);
    if(note)note.textContent=BDATA['note_'+L()]||'';}
  window._cwRefresh=draw; window.addEventListener('resize',draw); draw();
})();
"""

# Overlay previsao-vs-dado (Fase 2): linha do modelo (store canonico) + pontos
# do dado experimental, com <select> de amplitude. Reforca "nao-e-fit": UMA
# config preve N condicoes. Nao mexe no _PLOTTER_JS (usado pelas 81 var pages).
_OVERLAY_JS = """
(function(){ if(typeof ODATA==='undefined'||!ODATA) return;
  const root=document.documentElement, cs=getComputedStyle(root), col=n=>cs.getPropertyValue(n).trim();
  const host=document.getElementById('cw'); if(!host) return;
  const cv=host.querySelector('canvas'); if(!cv) return; const ctx=cv.getContext('2d');
  const sel=host.querySelector('#sel_ov'), note=host.querySelector('.cw-note'), ro=host.querySelector('.readout');
  const S=ODATA.series; let cur=ODATA.start_idx||0;
  const L=()=>root.dataset.lang==='pt'?'pt':'en';
  const PAD={l:56,r:14,t:14,b:40};
  let y0=1,y1=0;
  S.forEach(s=>{s.model_r.forEach(r=>{if(r<y0)y0=r;if(r>y1)y1=r;});s.data_r.forEach(r=>{if(r<y0)y0=r;if(r>y1)y1=r;});
    (s.interp_r||[]).forEach(r=>{if(r<y0)y0=r;if(r>y1)y1=r;});});
  if(y1<=y0){y0=0;y1=1;} const sp=y1-y0,pd=sp>0?sp*0.08:0.02; y0=Math.max(0,y0-pd); y1=Math.min(1.02,y1+pd);
  function draw(){ const s=S[cur]; if(!s) return;
    const w=cv.clientWidth||820,h=Math.round(w*0.5),dpr=window.devicePixelRatio||1;
    cv.width=w*dpr;cv.height=h*dpr;cv.style.height=h+'px';ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    const xmax=Math.max(1,s.model_N[s.model_N.length-1],s.data_N[s.data_N.length-1]);
    const X=n=>PAD.l+(n/xmax)*(w-PAD.l-PAD.r), Y=r=>{const rr=Math.max(y0,Math.min(y1,r));return PAD.t+(1-(rr-y0)/(y1-y0))*(h-PAD.t-PAD.b);};
    ctx.strokeStyle=col('--line');ctx.fillStyle=col('--muted');ctx.lineWidth=1;ctx.font="12px 'Segoe UI',sans-serif";
    ctx.textAlign='right';ctx.textBaseline='middle';
    for(let g=0;g<=5;g++){const v=y1-(g/5)*(y1-y0),y=PAD.t+(g/5)*(h-PAD.t-PAD.b);ctx.globalAlpha=.5;ctx.beginPath();ctx.moveTo(PAD.l,y);ctx.lineTo(w-PAD.r,y);ctx.stroke();ctx.globalAlpha=1;ctx.fillText(v.toFixed(2),PAD.l-8,y);}
    ctx.textAlign='center';ctx.textBaseline='top';for(let g=0;g<=5;g++){const n=Math.round(xmax*g/5);ctx.fillText(n,X(n),h-PAD.b+8);}
    ctx.save();ctx.translate(14,h/2);ctx.rotate(-Math.PI/2);ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('F / F0',0,0);ctx.restore();
    ctx.textAlign='center';ctx.fillText(L()==='pt'?'ciclo':'cycle',(PAD.l+w-PAD.r)/2,h-16);
    // interpolacao (tracejada, cinza) — ajuste a 0.25 mm aplicado sem mudar
    if(s.interp_r){ctx.strokeStyle=col('--muted');ctx.lineWidth=2;ctx.setLineDash([6,4]);ctx.beginPath();
      for(let i=0;i<s.model_N.length;i++){const x=X(s.model_N[i]),y=Y(s.interp_r[i]);i?ctx.lineTo(x,y):ctx.moveTo(x,y);}ctx.stroke();ctx.setLineDash([]);}
    // modelo (linha cheia, destaque)
    ctx.strokeStyle=col('--accent');ctx.lineWidth=3;ctx.beginPath();
    for(let i=0;i<s.model_N.length;i++){const x=X(s.model_N[i]),y=Y(s.model_r[i]);i?ctx.lineTo(x,y):ctx.moveTo(x,y);}ctx.stroke();
    ctx.fillStyle=col('--warn');ctx.strokeStyle=col('--panel');ctx.lineWidth=1.5;
    for(let i=0;i<s.data_N.length;i++){const x=X(s.data_N[i]),y=Y(s.data_r[i]);ctx.beginPath();ctx.arc(x,y,3.6,0,6.2832);ctx.fill();ctx.stroke();}
    if(ro){const pt=L()==='pt';var im=(typeof s.interp_mae==='number')?(' &nbsp;&middot;&nbsp; '+(pt?'interpolação MAE ':'interpolation MAE ')+'<span class="w">'+s.interp_mae.toFixed(3)+'</span>'):'';
      ro.innerHTML='<span class="v">'+s['label_'+L()]+'</span> &nbsp;&rarr;&nbsp; '+(pt?'modelo MAE ':'model MAE ')+'<span class="f">'+s.mae.toFixed(3)+'</span>'+im;}
  }
  if(sel){sel.value=String(cur);sel.addEventListener('change',function(e){cur=parseInt(e.target.value);draw();});}
  window.veRedraw=draw;
  window._cwRefresh=function(){ if(note)note.innerHTML=ODATA['note_'+L()]||''; if(sel){for(let i=0;i<sel.options.length;i++)sel.options[i].textContent=S[i]['label_'+L()];} draw(); };
  window.addEventListener('resize',draw); window._cwRefresh();
})();
"""


def _case_card_html(c):
    """Um card previsao-vs-dado: mini-plot lazy (canvas) + badge de MAE + condicoes."""
    badge = "ok" if c["mae"] <= 0.05 else ("mid" if c["mae"] <= 0.10 else "hi")
    cond = f'{_esc(c["bolt"])} · F0 {c["F0_kN"]:.0f} kN'
    if c["amp_mm"]:
        cond += f' · ±{c["amp_mm"]:.2f} mm'
    if c["freq"]:
        cond += f' · {c["freq"]:.3g} Hz'
    cav = (f'<div class="gal-cav">&#9888; {_esc("; ".join(c["caveats"]))}</div>'
           if c["caveats"] else '')
    return (f'<figure class="gal-card" data-cid="{_esc(c["cid"])}" '
            f'data-fam="{_esc(c["family"])}" data-mae="{c["mae"]}">'
            f'<figcaption class="gal-cap"><span class="gal-nm">{_esc(c["name"])}</span>'
            f'<span class="gal-badge {badge}">MAE {c["mae"]:.3f}</span></figcaption>'
            f'<canvas class="gal-cv"></canvas>'
            f'<div class="gal-cond">{cond}</div>{cav}'
            f'<a class="gal-report" href="reports/{_esc(c["cid"])}.html">'
            '<span data-l="pt">report completo</span>'
            '<span data-l="en">full report</span> &rarr;</a>'
            f'<a class="gal-csv" href="#" data-cid="{_esc(c["cid"])}">&#8595; CSV</a></figure>')


def _source_figures(source):
    """[(figtag, filename)] das figuras do artigo extraidas em
    paper_figures/<source_lower>__*.png (vazio se nao houver)."""
    figs = []
    base = OUTDIR / "paper_figures"
    if base.exists():
        for p in sorted(base.glob(f"{source.lower()}__*.png")):
            figs.append((p.stem.split("__", 1)[-1], p.name))
    return figs


def _study_sources():
    """Fontes com estudo de caso (>=1 curva), exceto o exemplo USER. Ordenadas
    por nome. Cada uma vira uma pagina study_<source>.html."""
    import statistics as _st
    by = {}
    for c in _validation_cases():
        if c["source"] == "USER":
            continue
        by.setdefault(c["source"], []).append(c)
    out = []
    for s, cs in by.items():
        name, bp, be = _source_label(s)
        note = next((c["note"] for c in cs if c.get("note")), None)
        out.append({"source": s, "slug": f"study_{s.lower()}", "name": name,
                    "blurb_pt": bp, "blurb_en": be, "cases": cs, "note": note,
                    "median_mae": round(_st.median([c["mae"] for c in cs]), 3)})
    out.sort(key=lambda x: x["name"])
    return out


def _md_to_html(md, min_h=2):
    """Conversor Markdown->HTML minimo p/ as notas de aparato (informacoes do
    artigo): headings ##/###, **negrito**, `code`, [txt](url), listas '-',
    tabelas pipe, paragrafos. Escapa o texto; nao suporta HTML embutido.
    `min_h` = nivel do heading '#' (2=h2 default; 3 p/ aninhar sob uma secao,
    evitando <h2> que quebraria o wrapping colapsavel do report)."""
    import re
    lines = md.replace("\r\n", "\n").split("\n")
    out, i, n = [], 0, len(lines)

    def inline(t):
        t = _esc(t)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
                   r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
        return t

    while i < n:
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            lvl = min(len(m.group(1)) - 1 + min_h, 4)  # '#' -> h{min_h}
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue
        # tabela pipe (linha com | seguida de linha separadora ---)
        if "|" in s and i + 1 < n and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1].strip()) \
                and "-" in lines[i + 1]:
            def cells(row):
                row = row.strip().strip("|")
                return [c.strip() for c in row.split("|")]
            head = cells(s)
            i += 2
            body = []
            while i < n and "|" in lines[i] and lines[i].strip():
                body.append(cells(lines[i]))
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                          for r in body)
            out.append(f'<div class="ovx"><table class="wide"><thead><tr>{th}</tr></thead>'
                       f"<tbody>{trs}</tbody></table></div>")
            continue
        # lista '-' / '*'
        if re.match(r"^[-*]\s+", s):
            items = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(f"<li>{inline(re.sub(r'^[-*]\s+', '', lines[i].strip()))}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        # paragrafo (junta linhas ate branco)
        para = [s]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#{1,4}\s|[-*]\s)", lines[i].strip()) \
                and "|" not in lines[i]:
            para.append(lines[i].strip())
            i += 1
        out.append("<p>" + inline(" ".join(para)) + "</p>")
    return "".join(out)


def _gallery_panel(wd):
    """Grade de cards previsao-vs-dado, agrupada por fonte, com resumo e filtros.
    Cada card = mini-plot (linha do modelo + pontos do dado) + badge de MAE."""
    cases = wd["cases"]
    sources = wd["sources"]
    st = wd["stats"]
    by = {}
    for c in cases:
        by.setdefault(c["source"], []).append(c)
    p = ['<div class="gal">']
    p.append(
        '<div class="gal-summary">'
        f'<span class="gal-stat"><b>{st["n"]}</b> '
        '<span data-l="pt">casos</span><span data-l="en">cases</span></span>'
        f'<span class="gal-stat"><b>{st["n_sources"]}</b> '
        '<span data-l="pt">fontes</span><span data-l="en">sources</span></span>'
        '<span class="gal-stat"><span data-l="pt">MAE mediano</span>'
        f'<span data-l="en">median MAE</span> <b>{st["median_mae"]:.3f}</b></span>'
        f'<span class="gal-stat"><b>{st["n_over"]}</b> '
        '<span data-l="pt">com MAE &gt; 0.10</span>'
        '<span data-l="en">with MAE &gt; 0.10</span></span>'
        '</div>')
    p.append(
        '<div class="gal-controls">'
        '<span class="gal-flt" data-fam="all" data-on="1">'
        '<span data-l="pt">todos</span><span data-l="en">all</span></span>'
        '<span class="gal-flt" data-fam="transverse">'
        '<span data-l="pt">transversal</span><span data-l="en">transverse</span></span>'
        '<span class="gal-flt" data-fam="axial">axial</span>'
        '<span class="gal-flt" data-fam="creep">creep</span>'
        '<label class="gal-only"><input type="checkbox" id="gal_over"> '
        '<span data-l="pt">só MAE &gt; 0.10</span>'
        '<span data-l="en">only MAE &gt; 0.10</span></label>'
        '</div>')
    for s in sources:
        cs = by.get(s["source"], [])
        study = "" if s["source"] == "USER" else f"study_{s['source'].lower()}.html"
        p.append(f'<section class="gal-src" data-src="{_esc(s["source"])}">')
        head_name = (f'<a href="{study}">{_esc(s["name"])} &rarr;</a>' if study
                     else _esc(s["name"]))
        p.append(
            f'<h3 class="gal-srch">{head_name} '
            f'<span class="gal-srcn">({s["count"]} · '
            '<span data-l="pt">MAE med.</span><span data-l="en">med. MAE</span> '
            f'{s["median_mae"]:.3f})</span></h3>')
        if s["blurb_pt"]:
            p.append(f'<p class="gal-blurb"><span data-l="pt">{_esc(s["blurb_pt"])}</span>'
                     f'<span data-l="en">{_esc(s["blurb_en"])}</span></p>')
        p.append('<div class="gal-grid">')
        for c in cs:
            p.append(_case_card_html(c))
        p.append('</div></section>')
    p.append('</div>')
    return "".join(p)


# Galeria de validacao (Fase 3): mini-plots lazy (IntersectionObserver) modelo-vs-dado
# p/ os 115 casos do store canonico. GDATA = {cid: {mN,mr,dN,dr}}. Filtros por
# familia + "so MAE>0.1". Nao roda engine — le do store PRE-computado.
_GALLERY_JS = """
(function(){ if(typeof GDATA==='undefined'||!GDATA) return;
  const root=document.documentElement, cs=getComputedStyle(root), col=n=>cs.getPropertyValue(n).trim();
  const host=document.getElementById('cw'); if(!host) return;
  const PAD={l:34,r:8,t:8,b:20};
  function drawCard(fig){ const cid=fig.dataset.cid, d=GDATA[cid]; if(!d)return;
    const cv=fig.querySelector('canvas'); if(!cv)return; const ctx=cv.getContext('2d');
    const w=cv.clientWidth||250,h=Math.round(w*0.62),dpr=window.devicePixelRatio||1;
    cv.width=w*dpr;cv.height=h*dpr;cv.style.height=h+'px';ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    let y0=1,y1=0; d.mr.forEach(r=>{if(r<y0)y0=r;if(r>y1)y1=r;}); d.dr.forEach(r=>{if(r<y0)y0=r;if(r>y1)y1=r;});
    if(y1<=y0){y0=0;y1=1;} const pd=(y1-y0)*0.08||0.02; y0=Math.max(0,y0-pd);y1=Math.min(1.02,y1+pd);
    const xmax=Math.max(1,d.mN[d.mN.length-1],d.dN[d.dN.length-1]);
    const X=n=>PAD.l+(n/xmax)*(w-PAD.l-PAD.r),Y=r=>{const rr=Math.max(y0,Math.min(y1,r));return PAD.t+(1-(rr-y0)/(y1-y0))*(h-PAD.t-PAD.b);};
    ctx.strokeStyle=col('--line');ctx.fillStyle=col('--muted');ctx.lineWidth=1;ctx.font="9px 'Segoe UI',sans-serif";
    ctx.textAlign='right';ctx.textBaseline='middle';
    for(let g=0;g<=2;g++){const v=y1-(g/2)*(y1-y0),y=PAD.t+(g/2)*(h-PAD.t-PAD.b);ctx.globalAlpha=.4;ctx.beginPath();ctx.moveTo(PAD.l,y);ctx.lineTo(w-PAD.r,y);ctx.stroke();ctx.globalAlpha=1;ctx.fillText(v.toFixed(2),PAD.l-4,y);}
    ctx.strokeStyle=col('--accent');ctx.lineWidth=2;ctx.beginPath();
    for(let i=0;i<d.mN.length;i++){const x=X(d.mN[i]),y=Y(d.mr[i]);i?ctx.lineTo(x,y):ctx.moveTo(x,y);}ctx.stroke();
    ctx.fillStyle=col('--warn');for(let i=0;i<d.dN.length;i++){const x=X(d.dN[i]),y=Y(d.dr[i]);ctx.beginPath();ctx.arc(x,y,2.4,0,6.2832);ctx.fill();}
    fig.dataset.drawn='1';
  }
  const io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){drawCard(e.target);io.unobserve(e.target);}});},{rootMargin:'150px'});
  host.querySelectorAll('.gal-card').forEach(f=>io.observe(f));
  let fam='all', only=false;
  function apply(){ host.querySelectorAll('.gal-card').forEach(function(f){
      const okf=(fam==='all'||f.dataset.fam===fam), oko=(!only||parseFloat(f.dataset.mae)>0.1);
      f.style.display=(okf&&oko)?'':'none';});
    host.querySelectorAll('.gal-src').forEach(function(sec){var any=false;sec.querySelectorAll('.gal-card').forEach(function(f){if(f.style.display!=='none')any=true;});sec.style.display=any?'':'none';});
    host.querySelectorAll('.gal-card').forEach(function(f){if(f.style.display!=='none'&&!f.dataset.drawn)drawCard(f);});
  }
  host.querySelectorAll('.gal-flt').forEach(function(b){b.addEventListener('click',function(){
    host.querySelectorAll('.gal-flt').forEach(x=>x.removeAttribute('data-on'));b.setAttribute('data-on','1');fam=b.dataset.fam;apply();});});
  const ov=host.querySelector('#gal_over'); if(ov)ov.addEventListener('change',function(){only=ov.checked;apply();});
  // download CSV por caso (modelo + dado) a partir do GDATA embutido
  host.querySelectorAll('.gal-csv').forEach(function(a){a.addEventListener('click',function(e){
    e.preventDefault(); const d=GDATA[a.dataset.cid]; if(!d)return;
    var rows=['cycle,F_over_F0,series'];
    for(var i=0;i<d.mN.length;i++)rows.push(d.mN[i]+','+d.mr[i]+',model');
    for(var j=0;j<d.dN.length;j++)rows.push(d.dN[j]+','+d.dr[j]+',data');
    var blob=new Blob([rows.join('\\n')],{type:'text/csv'});
    var u=URL.createObjectURL(blob),el=document.createElement('a');
    el.href=u;el.download=a.dataset.cid+'.csv';document.body.appendChild(el);el.click();
    document.body.removeChild(el);URL.revokeObjectURL(u);});});
  function redrawAll(){host.querySelectorAll('.gal-card').forEach(function(f){f.removeAttribute('data-drawn');if(f.style.display!=='none')drawCard(f);});}
  window.veRedraw=redrawAll; window._cwRefresh=redrawAll;
  window.addEventListener('resize',redrawAll);
})();
"""

# Anatomia da curva (Fase 4): a curva-padrao em X-log com 3 faixas de estagio
# rotuladas (mecanismo dominante lido do decomp), joelho e linha de piso.
_ANATOMY_JS = """
(function(){ if(typeof ADATA==='undefined'||!ADATA) return;
  const root=document.documentElement, cs=getComputedStyle(root), col=n=>cs.getPropertyValue(n).trim();
  const host=document.getElementById('cw'); if(!host) return;
  const cv=host.querySelector('canvas'); if(!cv) return; const ctx=cv.getContext('2d');
  const note=host.querySelector('.cw-note'), ro=host.querySelector('.an-readout');
  const SC=ADATA.scenarios; let cur=ADATA.start_idx||0, hov=-1, geom=null;
  const PAD={l:52,r:14,t:30,b:38}, BAND=['--accent','--accent2','--warn'];
  const L=()=>root.dataset.lang==='pt'?'pt':'en';
  const MN=k=>((L()==='pt'?ADATA.mech_pt:ADATA.mech_en)[k]||k);
  const lx=n=>Math.log(Math.max(1,n)+1);
  let y0=1,y1=0; SC.forEach(s=>s.ratio.forEach(v=>{if(v<y0)y0=v;if(v>y1)y1=v;}));
  const pd=(y1-y0)*0.08||0.02; y0=Math.max(0,y0-pd); y1=Math.min(1.02,y1+pd);
  function stageAt(s,n){let st=s.stages[0];for(let i=0;i<s.stages.length;i++){if(n>=s.stages[i].start_N)st=s.stages[i];}return st;}
  function draw(){
    const s=SC[cur];
    const w=cv.clientWidth||820,h=Math.round(w*0.5),dpr=window.devicePixelRatio||1;
    cv.width=w*dpr;cv.height=h*dpr;cv.style.height=h+'px';ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    const Nmax=s.N[s.N.length-1], logm=(s.xmode!=='linear');
    const xmin=logm?lx(0):0, xspan=((logm?lx(Nmax):Nmax)-xmin)||1;
    const xv=n=>logm?lx(n):n;
    const X=n=>PAD.l+((xv(n)-xmin)/xspan)*(w-PAD.l-PAD.r), Y=v=>{const vv=Math.max(y0,Math.min(y1,v));return PAD.t+(1-(vv-y0)/(y1-y0))*(h-PAD.t-PAD.b);};
    geom={X:X};
    s.stages.forEach(function(st,i){const x0=X(st.start_N),x1=X(st.end_N);
      ctx.fillStyle=col(BAND[i%3]);ctx.globalAlpha=.08;ctx.fillRect(x0,PAD.t,Math.max(0,x1-x0),h-PAD.t-PAD.b);ctx.globalAlpha=1;
      ctx.fillStyle=col(BAND[i%3]);ctx.font="bold 11px 'Segoe UI',sans-serif";ctx.textAlign='center';ctx.textBaseline='top';
      ctx.fillText(st.roman+' · '+(L()==='pt'?st.name_pt:st.name_en),(x0+x1)/2,4);
      ctx.fillStyle=col('--muted');ctx.font="10px 'Segoe UI',sans-serif";ctx.fillText(MN(st.dom),(x0+x1)/2,18);});
    ctx.strokeStyle=col('--line');ctx.fillStyle=col('--muted');ctx.lineWidth=1;ctx.font="11px 'Segoe UI',sans-serif";ctx.textAlign='right';ctx.textBaseline='middle';
    for(let g=0;g<=4;g++){const v=y1-(g/4)*(y1-y0),y=PAD.t+(g/4)*(h-PAD.t-PAD.b);ctx.globalAlpha=.4;ctx.beginPath();ctx.moveTo(PAD.l,y);ctx.lineTo(w-PAD.r,y);ctx.stroke();ctx.globalAlpha=1;ctx.fillText(v.toFixed(2),PAD.l-6,y);}
    ctx.textAlign='center';ctx.textBaseline='top';
    const ticks=logm?[1,10,100,1000,Nmax].filter(n=>n<=Nmax):[0,Math.round(Nmax*0.25),Math.round(Nmax*0.5),Math.round(Nmax*0.75),Nmax];
    ticks.forEach(function(n){ctx.fillText(n,X(n),h-PAD.b+6);});
    ctx.strokeStyle=col('--muted');ctx.setLineDash([5,4]);ctx.lineWidth=1.2;ctx.beginPath();ctx.moveTo(PAD.l,Y(s.floor));ctx.lineTo(w-PAD.r,Y(s.floor));ctx.stroke();ctx.setLineDash([]);
    ctx.fillStyle=col('--muted');ctx.textAlign='left';ctx.fillText('F/F0 = '+s.floor.toFixed(2),PAD.l+4,Y(s.floor)-8);
    ctx.strokeStyle=col('--accent');ctx.lineWidth=3;ctx.beginPath();
    for(let i=0;i<s.N.length;i++){const x=X(s.N[i]),y=Y(s.ratio[i]);i?ctx.lineTo(x,y):ctx.moveTo(x,y);}ctx.stroke();
    let ky=Y(0.5);for(let i=0;i<s.N.length;i++){if(s.N[i]>=s.knee){ky=Y(s.ratio[i]);break;}}
    const kx=X(s.knee);ctx.fillStyle=col('--warn');ctx.beginPath();ctx.arc(kx,ky,4,0,6.2832);ctx.fill();
    ctx.font="10px 'Segoe UI',sans-serif";ctx.textAlign='left';ctx.fillText(L()==='pt'?'joelho':'knee',kx+6,ky-6);
    if(hov>=0&&hov<s.N.length){const hx=X(s.N[hov]),hy=Y(s.ratio[hov]);
      ctx.strokeStyle=col('--ink');ctx.globalAlpha=.35;ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(hx,PAD.t);ctx.lineTo(hx,h-PAD.b);ctx.stroke();ctx.globalAlpha=1;
      ctx.fillStyle=col('--accent2');ctx.beginPath();ctx.arc(hx,hy,5,0,6.2832);ctx.fill();ctx.strokeStyle=col('--panel');ctx.lineWidth=2;ctx.stroke();}
    ctx.fillStyle=col('--muted');ctx.save();ctx.translate(12,h/2);ctx.rotate(-Math.PI/2);ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('F / F0',0,0);ctx.restore();
    ctx.textAlign='center';ctx.fillText((L()==='pt'?'ciclo':'cycle')+(logm?' (log)':''),(PAD.l+w-PAD.r)/2,h-14);
    syncRO();
  }
  function syncRO(){ if(!ro)return; const pt=L()==='pt', s=SC[cur];
    if(hov<0){ ro.innerHTML='<span class="an-hint">'+(pt?'Passe o cursor sobre a curva para inspecionar cada ciclo.':'Hover over the curve to inspect each cycle.')+'</span>'; return; }
    const n=s.N[hov], rr=s.ratio[hov], st=stageAt(s,n), loss=(s.ratio[0]-rr)*100;
    ro.innerHTML=(pt?'ciclo ':'cycle ')+'<b>'+n+'</b> &middot; F/F0 <b>'+rr.toFixed(3)+'</b> &middot; '
      +(pt?'estágio ':'stage ')+'<b>'+st.roman+'</b> ('+(pt?st.name_pt:st.name_en)+') &middot; '
      +(pt?'mecanismo ':'mechanism ')+'<b>'+MN(s.dom[hov])+'</b> &middot; '
      +(pt?'perda acum. ':'cum. loss ')+'<b>'+loss.toFixed(1)+'%</b>';
  }
  function pick(ev){ if(!geom)return; const rect=cv.getBoundingClientRect();
    const mx=((ev.touches&&ev.touches[0])?ev.touches[0].clientX:ev.clientX)-rect.left; const s=SC[cur];
    let best=0,bd=1e9; for(let i=0;i<s.N.length;i++){const d=Math.abs(geom.X(s.N[i])-mx);if(d<bd){bd=d;best=i;}} hov=best;draw(); }
  cv.addEventListener('mousemove',pick);
  cv.addEventListener('touchmove',function(e){pick(e);e.preventDefault();},{passive:false});
  cv.addEventListener('mouseleave',function(){hov=-1;draw();});
  host.querySelectorAll('.an-scn').forEach(function(b){b.addEventListener('click',function(){
    host.querySelectorAll('.an-scn').forEach(x=>x.removeAttribute('data-on'));b.setAttribute('data-on','1');cur=parseInt(b.dataset.scn);hov=-1;draw();});});
  window.veRedraw=draw; window._cwRefresh=function(){if(note)note.innerHTML=ADATA['note_'+L()]||'';draw();};
  window.addEventListener('resize',draw); window._cwRefresh();
})();
"""

_CONCEPT_CSS = """
.cw{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:14px 0}
.cw canvas{width:100%;height:auto;display:block}
.cw-ctrl{display:flex;flex-wrap:wrap;gap:8px 16px;margin-top:10px;align-items:center}
.cw-ctrl input[type=range]{flex:1;min-width:200px;accent-color:var(--accent)}
.cw-ctrl select{background:var(--code-bg);color:var(--ink);border:1px solid var(--line);border-radius:7px;padding:5px 9px;font-family:inherit}
.cw-leg{display:flex;align-items:center;gap:5px;font-size:.8rem;color:var(--muted);cursor:pointer}
.cw-leg .k{display:inline-block;width:16px;height:10px;border:1px solid;border-radius:2px}
.legend .kd{display:inline-block;width:11px;height:11px;border-radius:50%;vertical-align:middle;margin-right:5px}
.cw-note{font-size:.85rem;color:var(--muted);margin-top:10px;line-height:1.5}
.bars{margin-top:4px}
.bar-row{display:flex;align-items:center;gap:10px;margin:6px 0}
.bar-lab{flex:0 0 40%;font-size:.85rem}
.bar-track{flex:1;height:14px;background:var(--code-bg);border-radius:7px;overflow:hidden}
.bar-fill{display:block;height:100%;border-radius:7px}
.bar-val{flex:0 0 auto;font-family:'Cascadia Code',monospace;font-size:.82rem;color:var(--muted)}
.bar-total{margin-top:8px;font-family:'Cascadia Code',monospace;font-size:.85rem;color:var(--ink)}
svg.schema{width:100%;height:auto;max-width:640px;display:block;margin:6px auto}
svg.schema text{fill:var(--ink);font-family:'Segoe UI',sans-serif}
svg.schema .lab{fill:var(--muted);font-size:12px}
svg.schema .box{fill:var(--code-bg);stroke:var(--line)}
svg.schema .hot{cursor:default}
svg.schema .hot:hover .box{stroke:var(--accent);stroke-width:2}
svg.schema .node{fill:var(--accent)}
svg.schema .edge{stroke:var(--accent);fill:none;stroke-width:2;marker-end:url(#arrow)}
svg.schema .edge-lab{fill:var(--muted);font-size:11px}
svg.schema .cpl{fill:var(--accent);fill-opacity:.18;stroke:var(--accent);stroke-width:1.6}
svg.schema .cplt{fill:var(--accent);font-weight:700}
svg.schema .zero{fill:var(--ghost)}
svg.schema .diag{fill:var(--code-bg);stroke:var(--line)}
svg.schema .fill{fill:var(--accent);fill-opacity:.08;stroke:var(--accent);stroke-opacity:.4}
svg.schema .dash{stroke:var(--muted);stroke-dasharray:4 4;fill:none}
svg.schema .brk{stroke:var(--muted);stroke-width:2;fill:none}
.gal-summary{display:flex;flex-wrap:wrap;gap:10px 22px;padding:10px 14px;background:var(--panel);border:1px solid var(--line);border-radius:10px;margin:8px 0}
.gal-stat{font-size:.9rem;color:var(--muted)}
.gal-stat b{color:var(--ink);font-size:1.05rem}
.gal-controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:12px 0}
.gal-flt{cursor:pointer;font-size:.82rem;padding:4px 11px;border:1px solid var(--line);border-radius:14px;color:var(--muted)}
.gal-flt[data-on]{background:var(--accent);color:#fff;border-color:var(--accent)}
.gal-only{font-size:.82rem;color:var(--muted);margin-left:auto;display:flex;align-items:center;gap:5px}
.gal-src{margin:18px 0}
.gal-srch{font-size:1.05rem;margin:0 0 2px;border-bottom:1px solid var(--line);padding-bottom:4px}
.gal-srcn{font-size:.8rem;color:var(--muted);font-weight:400}
.gal-blurb{font-size:.82rem;color:var(--muted);margin:2px 0 8px}
.gal-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}
.gal-card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:8px 10px;margin:0}
.gal-cap{display:flex;justify-content:space-between;align-items:baseline;gap:6px;font-size:.8rem}
.gal-nm{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.gal-badge{flex:0 0 auto;font-family:'Cascadia Code',monospace;font-size:.72rem;padding:1px 6px;border-radius:8px;border:1px solid currentColor;background:transparent}
.gal-badge.ok{color:var(--ok)}
.gal-badge.mid{color:var(--accent2)}
.gal-badge.hi{color:var(--warn)}
.gal-cv{width:100%;height:auto;display:block;margin:4px 0}
.gal-cond{font-size:.72rem;color:var(--muted);font-family:'Cascadia Code',monospace}
.gal-cav{font-size:.72rem;color:var(--warn);margin-top:3px;line-height:1.35}
.gloss-tbl{width:100%;border-collapse:collapse;margin:10px 0;font-size:.9rem}
.gloss-tbl th,.gloss-tbl td{text-align:left;padding:6px 10px;border-bottom:1px solid var(--line);vertical-align:top}
.gloss-tbl th{color:var(--muted);font-weight:600;font-size:.82rem;text-transform:uppercase;letter-spacing:.03em}
.gloss-tbl td.sym{font-family:'Cascadia Code',monospace;color:var(--accent);white-space:nowrap}
.gloss-tbl td.unit{font-family:'Cascadia Code',monospace;color:var(--muted);white-space:nowrap}
.gloss-wrap{overflow-x:auto}
.an-ctrl{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 8px}
.an-scn{cursor:pointer;font-size:.82rem;padding:4px 11px;border:1px solid var(--line);border-radius:14px;color:var(--muted)}
.an-scn[data-on]{background:var(--accent);color:#fff;border-color:var(--accent)}
.an-readout{margin-top:10px;font-family:'Cascadia Code',monospace;font-size:.85rem;color:var(--ink);min-height:1.3em;line-height:1.4}
.an-readout .an-hint{color:var(--muted);font-family:'Segoe UI',sans-serif}
#plot_an{cursor:crosshair}
.study-sub{font-size:1rem;color:var(--muted);font-weight:400}
.study-figs{display:flex;flex-wrap:wrap;gap:14px;margin:8px 0}
.study-fig{margin:0;flex:1 1 340px;max-width:100%}
.study-fig img{width:100%;height:auto;border:1px solid var(--line);border-radius:8px;background:#fff}
.study-fig figcaption{font-size:.78rem;color:var(--muted);margin-top:4px;text-align:center}
.study-figcap{font-size:.82rem;color:var(--muted);margin:6px 0}
.study-nofig{font-size:.9rem;color:var(--muted)}
.study-cav{font-size:.85rem;color:var(--warn);margin-top:8px;line-height:1.4}
.study-meta td:first-child{color:var(--muted);white-space:nowrap;width:32%}
.gal-report{display:inline-block;margin-top:6px;font-size:.74rem;color:var(--accent);text-decoration:none}
.gal-report:hover{text-decoration:underline}
.study-note h3,.study-note h4{color:var(--ink);margin:12px 0 4px;font-size:.9rem}
.study-note table.wide{width:100%;border-collapse:collapse;font-size:.8rem;margin:6px 0}
.study-note table.wide th,.study-note table.wide td{border-bottom:1px solid var(--line);padding:4px 8px;text-align:left;vertical-align:top}
.study-note table.wide th{color:var(--muted);font-weight:600;font-size:.72rem}
.study-note ul{margin:6px 0;padding-left:20px}
.study-note li{margin:3px 0;font-size:.9rem}
.study-note p{font-size:.9rem}
.study-note code{font-family:'Cascadia Code',monospace;font-size:.85em;background:var(--code-bg);padding:1px 4px;border-radius:4px}
.foundations-hero{background:linear-gradient(0deg,var(--panel),var(--panel));border:1px solid var(--accent);
  border-radius:12px;padding:14px 16px;margin:14px 0}
.trails{display:flex;flex-wrap:wrap;gap:12px;margin:12px 0}
.trail{flex:1 1 200px;display:block;text-decoration:none;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:12px 14px;color:var(--ink)}
.trail:hover{border-color:var(--accent)}
.trail b{display:block;color:var(--accent);margin-bottom:4px}
.trail .desc{display:block;color:var(--muted);font-size:.85rem;line-height:1.4}
.repro{font-family:'Cascadia Code',monospace;font-size:.82rem;background:var(--code-bg);border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin:6px 0;white-space:pre-wrap;overflow-x:auto}
.gal-csv{display:inline-block;margin:4px 8px 0 0;font-size:.74rem;color:var(--accent);text-decoration:none}
.gal-csv:hover{text-decoration:underline}
"""


def _concept_widget_html(wd):
    """HTML do widget (dentro de <div id=cw>) + o bloco <script> com dados+JS."""
    if not wd:
        return "", ""
    kind = wd["kind"]
    if kind == "plot":
        curves = wd["curves"]
        n = len(curves)
        start = wd.get("start_idx", n // 2)
        if wd.get("control") == "select":
            opts = "".join(
                f'<option value="{i}"{" selected" if i == start else ""}>'
                f'<span>{_esc(c.get("value_pt", c.get("value","")))}</span></option>'
                for i, c in enumerate(curves))
            control = f'<select id="sel">{opts}</select>'
        else:
            control = (f'<input type="range" id="slider" min="0" max="{n-1}" step="1" '
                       f'value="{start}">')
        # DATA no formato do _PLOTTER_JS
        data = {"unit": wd.get("unit", ""), "baseline_idx": start,
                "provenance": None, "negligible": False,
                "delta_max": 0.0,
                "curves": [{"value": c.get("value", c.get("value_pt", i)),
                            "N": c["N"], "ratio": c["ratio"]} for i, c in enumerate(curves)]}
        # delta_max informativo
        finals = [c["ratio"][-1] for c in curves]
        data["delta_max"] = round(max(finals) - min(finals), 4)
        panel = (f'<div class="cw"><canvas id="plot"></canvas>'
                 f'<div class="legend">'
                 f'<span><i class="k" style="border-color:var(--accent)"></i>'
                 f'<span data-l="pt">valor atual</span><span data-l="en">current</span></span>'
                 f'<span><i class="k" style="border-color:var(--ghost)"></i>'
                 f'<span data-l="pt">outras</span><span data-l="en">others</span></span></div>'
                 f'<div class="ctl">{control}'
                 f'<span class="readout"><span data-l="pt">seleção</span><span data-l="en">selection</span>'
                 f' = <span class="v" id="valout"></span> &nbsp;&rarr;&nbsp; F/F0<sub>final</sub> = '
                 f'<span class="f" id="finalout"></span></span></div>'
                 f'<div class="cw-note" id="prov" style="display:none"></div>'
                 f'<div class="cw-note">'
                 f'<span data-l="pt">{_esc(wd.get("note_pt",""))}</span>'
                 f'<span data-l="en">{_esc(wd.get("note_en",""))}</span></div></div>')
        script = f'<script>const DATA = {json.dumps(data)};</script>\n<script>{_PLOTTER_JS}</script>'
        return panel, script
    if kind == "stack":
        panel = ('<div class="cw"><canvas></canvas><div class="cw-ctrl"></div>'
                 '<div class="cw-note"></div></div>')
        sdata = {"N": wd["N"], "ratio": wd["ratio"], "mechs": wd["mechs"],
                 "note_pt": wd.get("note_pt", ""), "note_en": wd.get("note_en", "")}
        script = f'<script>const SDATA = {json.dumps(sdata)};</script>\n<script>{_STACK_JS}</script>'
        return panel, script
    if kind == "bars":
        panel = '<div class="cw"><div class="bars"></div><div class="cw-note"></div></div>'
        script = f'<script>const BDATA = {json.dumps(wd)};</script>\n<script>{_BARS_JS}</script>'
        return panel, script
    if kind == "overlay":
        series = wd["series"]
        start = wd.get("start_idx", 0)
        opts = "".join(
            f'<option value="{i}"{" selected" if i == start else ""}>'
            f'{_esc(s.get("label_pt", ""))}</option>'
            for i, s in enumerate(series))
        panel = ('<div class="cw"><canvas id="plot_ov"></canvas>'
                 '<div class="legend">'
                 '<span><i class="k" style="border-color:var(--accent)"></i>'
                 '<span data-l="pt">modelo (previsão)</span>'
                 '<span data-l="en">model (prediction)</span></span>'
                 '<span><i class="kd" style="background:var(--warn)"></i>'
                 '<span data-l="pt">dado medido (Liu 2025)</span>'
                 '<span data-l="en">measured data (Liu 2025)</span></span>'
                 '<span><i class="kdash"></i>'
                 '<span data-l="pt">interpolação (ajustada em 0.25 mm)</span>'
                 '<span data-l="en">interpolation (fitted at 0.25 mm)</span></span></div>'
                 '<div class="ctl"><label><span data-l="pt">amplitude</span>'
                 '<span data-l="en">amplitude</span>&nbsp;'
                 f'<select id="sel_ov">{opts}</select></label>'
                 '<span class="readout"></span></div>'
                 '<div class="cw-note"></div></div>')
        script = (f'<script>const ODATA = {json.dumps(wd)};</script>\n'
                  f'<script>{_OVERLAY_JS}</script>')
        return panel, script
    if kind == "gallery":
        panel = _gallery_panel(wd)
        gdata = {c["cid"]: {"mN": c["model_N"], "mr": c["model_r"],
                            "dN": c["data_N"], "dr": c["data_r"]} for c in wd["cases"]}
        script = (f'<script>const GDATA = {json.dumps(gdata)};</script>\n'
                  f'<script>{_GALLERY_JS}</script>')
        return panel, script
    if kind == "anatomy":
        scen = wd["scenarios"]
        start = wd.get("start_idx", 0)
        btns = []
        for i, s in enumerate(scen):
            on = ' data-on="1"' if i == start else ''
            btns.append(f'<span class="an-scn"{on} data-scn="{i}">'
                        f'<span data-l="pt">{_esc(s["label_pt"])}</span>'
                        f'<span data-l="en">{_esc(s["label_en"])}</span></span>')
        panel = ('<div class="cw"><div class="an-ctrl">' + "".join(btns) + '</div>'
                 '<canvas id="plot_an"></canvas>'
                 '<div class="an-readout"></div>'
                 '<div class="cw-note"></div></div>')
        script = (f'<script>const ADATA = {json.dumps(wd)};</script>\n'
                  f'<script>{_ANATOMY_JS}</script>')
        return panel, script
    return "", ""


def render_concept_page(page, all_specs):
    """Renderiza uma pagina conceitual (Fundamentos): prosa bilingue + SVG +
    widget interativo (opcional). Reusa a sidebar/tema/idioma."""
    sidebar = _sidebar_html(all_specs, current_name=page["slug"])
    slugs = [p["slug"] for p in CONCEPT_PAGES]
    pos = slugs.index(page["slug"]) if page["slug"] in slugs else 0
    prev_slug = slugs[pos - 1] if pos > 0 else None
    next_slug = slugs[pos + 1] if pos < len(slugs) - 1 else None
    prev_link = (f'<a href="concept_{_esc(prev_slug)}.html">&larr; '
                 f'{_esc(next((p["nav_pt"] for p in CONCEPT_PAGES if p["slug"]==prev_slug), ""))}</a>'
                 if prev_slug else '<a href="index.html">&#8962; índice</a>')
    next_link = (f'<a href="concept_{_esc(next_slug)}.html">'
                 f'{_esc(next((p["nav_pt"] for p in CONCEPT_PAGES if p["slug"]==next_slug), ""))} &rarr;</a>'
                 if next_slug else '<a href="var_emb_depth.html">emb_depth &rarr;</a>')

    wd = _widget_data(page["widget"]) if page.get("widget") else None
    panel, wscript = _concept_widget_html(wd)
    # corpo unico bilingue (PT/EN via data-l); widget injetado no placeholder
    body = page["body"].replace('<div id="cw"></div>', f'<div id="cw" class="widget">{panel}</div>')

    return f"""<!doctype html>
<html lang="pt" data-theme="light" data-lang="pt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(page["nav_pt"])} — Fundamentos BAS V2</title>
<style>{_BASE_CSS}{_CONCEPT_CSS}</style>
</head>
<body>
{sidebar}
<main class="main">
<div class="crumbs"><a href="index.html">&#8962; <span data-l="pt">Explorador de Variáveis</span><span data-l="en">Variable Explorer</span></a> /
  <span data-l="pt">Fundamentos</span><span data-l="en">Foundations</span></div>
<h1 class="name"><span data-l="pt">{page["title_pt"]}</span><span data-l="en">{page["title_en"]}</span></h1>
{body}
<nav class="pn">{prev_link}<a href="index.html">&#8962; <span data-l="pt">índice</span><span data-l="en">index</span></a>{next_link}</nav>
</main>
<script>{_SHELL_JS}</script>
{wscript}
</body>
</html>
"""


def render_study_page(src, all_specs):
    """Pagina de estudo de caso POR FONTE: figura(s) do artigo (recorte do PDF) +
    condicoes do ensaio + todas as curvas modelo-vs-dado daquela fonte (cards lazy)
    + DOI. Reusa a galeria (GDATA + _GALLERY_JS) p/ os mini-plots."""
    import statistics as _st
    cases = sorted(src["cases"], key=lambda c: c["mae"])
    sidebar = _sidebar_html(all_specs, current_name=src["slug"])
    ref = cases[0]["reference"]
    doi = cases[0]["doi"]
    figs = _source_figures(src["source"])
    if figs:
        fig_imgs = "".join(
            f'<figure class="study-fig"><img loading="lazy" src="paper_figures/{_esc(fname)}" '
            f'alt="{_esc(src["name"])} {_esc(tag)}">'
            f'<figcaption>{_esc(src["name"])} &middot; {_esc(tag)}</figcaption></figure>'
            for tag, fname in figs)
        fig_block = (f'<div class="study-figs">{fig_imgs}</div>'
                     '<p class="study-figcap"><span data-l="pt">Figura(s) originais do artigo '
                     '(recorte do PDF) &mdash; a fonte dos pontos que foram digitalizados.</span>'
                     '<span data-l="en">Original figure(s) from the paper (PDF crop) &mdash; the '
                     'source of the digitized points.</span></p>')
    else:
        doi_a = (f' (<a href="https://doi.org/{_esc(doi)}" target="_blank" rel="noopener">DOI</a>)'
                 if doi else '')
        fig_block = (f'<p class="study-nofig"><span data-l="pt">Figura original: ver o artigo{doi_a}. '
                     f'(Dados de laboratório sem figura publicada.)</span>'
                     f'<span data-l="en">Original figure: see the paper{doi_a}. '
                     f'(Lab data with no published figure.)</span></p>')
    bolts = ", ".join(sorted({c["bolt"] for c in cases if c["bolt"]})) or "&mdash;"
    amps = sorted({c["amp_mm"] for c in cases if c["amp_mm"]})
    if not amps:
        amp_s = "&mdash;"
    elif len(amps) == 1:
        amp_s = f'±{amps[0]:.2f} mm'
    else:
        amp_s = f'±{min(amps):.2f}&ndash;{max(amps):.2f} mm'
    freqs = sorted({c["freq"] for c in cases if c["freq"]})
    freq_s = (", ".join(f"{f:.3g}" for f in freqs) + " Hz") if freqs else "&mdash;"
    f0s = sorted({c["F0_kN"] for c in cases})
    f0_s = f'{min(f0s):.0f}&ndash;{max(f0s):.0f} kN' if len(f0s) > 1 else f'{f0s[0]:.0f} kN'
    fams = ", ".join(sorted({c["family"] for c in cases}))
    med = _st.median([c["mae"] for c in cases])
    cavs = sorted({cv for c in cases for cv in c["caveats"]})
    cav_block = (f'<p class="study-cav">&#9888; {_esc("; ".join(cavs))}</p>' if cavs else '')
    doi_link = (f'<a href="https://doi.org/{_esc(doi)}" target="_blank" rel="noopener">doi:{_esc(doi)}</a>'
                if doi else '<span data-l="pt">sem DOI</span><span data-l="en">no DOI</span>')
    meta_tbl = (
        '<div class="gloss-wrap"><table class="gloss-tbl study-meta"><tbody>'
        f'<tr><td><span data-l="pt">Referência</span><span data-l="en">Reference</span></td>'
        f'<td>{_esc(ref)} &middot; {doi_link}</td></tr>'
        f'<tr><td><span data-l="pt">Parafuso</span><span data-l="en">Bolt</span></td><td>{bolts}</td></tr>'
        f'<tr><td><span data-l="pt">Pré-carga F0</span><span data-l="en">Preload F0</span></td><td>{f0_s}</td></tr>'
        f'<tr><td><span data-l="pt">Amplitude</span><span data-l="en">Amplitude</span></td><td>{amp_s}</td></tr>'
        f'<tr><td><span data-l="pt">Frequência</span><span data-l="en">Frequency</span></td><td>{freq_s}</td></tr>'
        f'<tr><td><span data-l="pt">Família / nº de curvas</span><span data-l="en">Family / curves</span></td>'
        f'<td>{_esc(fams)} &middot; {len(cases)}</td></tr>'
        f'<tr><td>MAE <span data-l="pt">mediano</span><span data-l="en">median</span></td><td>{med:.3f}</td></tr>'
        '</tbody></table></div>')
    cards = "".join(_case_card_html(c) for c in cases)
    gdata = {c["cid"]: {"mN": c["model_N"], "mr": c["model_r"],
                        "dN": c["data_N"], "dr": c["data_r"]} for c in cases}
    # informacoes do artigo (nota de aparato renderizada de MD)
    note_html = ""
    if src.get("note"):
        try:
            md = pathlib.Path(src["note"]).read_text(encoding="utf-8")
            note_html = (
                '<div class="panel study-note"><h2 class="sec">'
                '<span data-l="pt">Informações do artigo — aparato, corpo-de-prova, matriz de ensaios</span>'
                '<span data-l="en">Paper information — apparatus, specimen, test matrix</span></h2>'
                f'{_md_to_html(md)}</div>')
        except OSError:
            note_html = ""
    body = (
        f'<p class="intro"><span data-l="pt">{_esc(src["blurb_pt"])}</span>'
        f'<span data-l="en">{_esc(src["blurb_en"])}</span></p>'
        '<div class="panel"><h2 class="sec"><span data-l="pt">Figura do artigo</span>'
        f'<span data-l="en">Paper figure</span></h2>{fig_block}</div>'
        '<div class="panel"><h2 class="sec"><span data-l="pt">Condições do ensaio</span>'
        f'<span data-l="en">Test conditions</span></h2>{meta_tbl}{cav_block}</div>'
        f'{note_html}'
        '<div class="panel"><h2 class="sec"><span data-l="pt">Modelo vs dado</span>'
        '<span data-l="en">Model vs data</span></h2>'
        '<p><span data-l="pt">Cada card = uma curva digitalizada deste estudo: a linha é a '
        'previsão do modelo (config adotada, do store canônico) e os pontos são o dado medido; '
        'o badge traz o MAE.</span><span data-l="en">Each card = one digitized curve from this '
        'study: the line is the model prediction (adopted config, from the canonical store) and '
        'the dots are the measured data; the badge shows the MAE.</span></p>'
        f'<div id="cw"><div class="gal-grid">{cards}</div></div></div>'
        '<div class="panel"><h2 class="sec"><span data-l="pt">Reprodutibilidade</span>'
        '<span data-l="en">Reproducibility</span></h2>'
        '<p><span data-l="pt">Cada card tem <b>&#8595; CSV</b> (modelo + dado da curva). Os CSVs '
        'digitalizados originais ficam em <code>Models/CALIBRATION_AND_VALIDATION/curve_library/'
        'digitized_csv/</code>; a curva do modelo vem do store canônico (config adotada por fonte). '
        'Para reproduzir localmente:</span>'
        '<span data-l="en">Each card has <b>&#8595; CSV</b> (curve model + data). The original '
        'digitized CSVs live in <code>Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/'
        '</code>; the model curve comes from the canonical store (adopted per-source config). To '
        'reproduce locally:</span></p>'
        '<div class="repro">python -m bolt_analysis_studio.validation.report --all'
        '   # (re)gera os reports de validação\n'
        'python New_Theory/build_variable_explorer.py'
        '   # regenera este guia\n'
        'python -m bolt_analysis_studio.calibration.server'
        '   # tuner ao vivo (http://localhost:8765)</div>'
        '<p class="intro"><span data-l="pt">Ver também o <a href="concept_usage.html">guia de uso do '
        'programa</a> e a <a href="concept_methodology.html">metodologia</a>.</span>'
        '<span data-l="en">See also the <a href="concept_usage.html">program usage guide</a> and the '
        '<a href="concept_methodology.html">methodology</a>.</span></p></div>')
    wscript = (f'<script>const GDATA = {json.dumps(gdata)};</script>\n'
               f'<script>{_GALLERY_JS}</script>')
    return f"""<!doctype html>
<html lang="pt" data-theme="light" data-lang="pt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(src["name"])} — Estudo de caso — BAS V2</title>
<style>{_BASE_CSS}{_CONCEPT_CSS}</style>
</head>
<body>
{sidebar}
<main class="main">
<div class="crumbs"><a href="index.html">&#8962; <span data-l="pt">Explorador de Variáveis</span><span data-l="en">Variable Explorer</span></a> /
  <a href="concept_gallery.html"><span data-l="pt">Galeria de validação</span><span data-l="en">Validation gallery</span></a> /
  {_esc(src["name"])}</div>
<h1 class="name">{_esc(src["name"])} <span class="study-sub"><span data-l="pt">— estudo de caso</span><span data-l="en">— case study</span></span></h1>
{body}
<nav class="pn"><a href="concept_gallery.html">&larr; <span data-l="pt">Galeria</span><span data-l="en">Gallery</span></a><a href="index.html">&#8962; <span data-l="pt">índice</span><span data-l="en">index</span></a></nav>
</main>
<script>{_SHELL_JS}</script>
{wscript}
</body>
</html>
"""


def _load_content():
    """Carrega os 74 campos autorados de New_Theory/_ve_content.py, injetando
    VarSpec e VARIABLE_SPECS no namespace do modulo de conteudo (evita import
    circular). Silencioso se o arquivo nao existir."""
    import importlib.util as _il
    for fname, inject in (("_ve_content.py", {"VarSpec": VarSpec, "VARIABLE_SPECS": VARIABLE_SPECS}),
                          ("_ve_concepts.py", {"CONCEPT_PAGES": CONCEPT_PAGES})):
        p = _ROOT / "New_Theory" / fname
        if not p.exists():
            continue
        spec = _il.spec_from_file_location(fname[:-3], p)
        mod = _il.module_from_spec(spec)
        mod.__dict__.update(inject)
        spec.loader.exec_module(mod)


_load_content()


def main():
    validate_specs()
    miss = missing_fields()
    if miss:
        print(f"AVISO: {len(miss)} campos sem VarSpec: {sorted(miss)}")
    else:
        print(f"cobertura completa: {len(VARIABLE_SPECS)}/{len(all_field_names())} campos")
    paths = build(VARIABLE_SPECS, OUTDIR)
    print(f"gerados {len(paths)} arquivos em {OUTDIR}")
    # Estilo do tutorial (dark/Bahnschrift/hero) nas páginas de conceito — antes um
    # passo manual (3 scripts), agora aplicado automaticamente ao fim do build.
    import subprocess
    here = pathlib.Path(__file__).resolve().parent
    for s in ("restyle_concepts.py", "restyle_gallery.py", "restyle_notafit.py"):
        try:
            subprocess.run([sys.executable, str(here / s)], cwd=str(here.parent), check=True)
        except Exception as exc:  # pragma: no cover - defensivo
            print(f"AVISO: {s} falhou: {exc}")
    print("estilo do tutorial aplicado (fundamentos + galeria + não-é-fit)")


if __name__ == "__main__":
    main()
