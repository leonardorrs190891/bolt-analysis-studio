# -*- coding: utf-8 -*-
"""Runner canonico de casos de validacao (spec §3): engine V2 + constantes com
proveniencia (bloco shared congelado + adotadas per-rig via knowledge_base) +
decomposicao por mecanismo (CycleSnapshot.dF_0_by_mech; a soma fecha exatamente
F0*(1-ratio) — mesma garantia do plot Mechanism Decomposition do Run)."""
from __future__ import annotations

import datetime
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field, replace
from typing import Dict, List, Optional

import numpy as np

from ..calibration import knowledge_base as kb
from ..calibration.tuner_shim import translate_legacy_tuners
from ..numerical.dynamic_stiffness_analyzer import (DynamicStiffnessAnalyzer,
                                                    JointMaterial)
from .case_registry import CaseRecord
from .inputs import (emb_depth_vdi, frozen_constants, geometry_for_case,
                     inputs_for, load_full_curve, repo_root)

_MAX_POINTS = 400            # amostragem das curvas/decomposicao no resultado
FLOOR_TRIM = 0.10            # convencao pre-registrada da campanha (spec §1):
                             # pontos com ratio < 0.10 descartados da metrica
# F_amp axial por fonte (tabela curada de New_Theory/calibrate_axial.py
# CONDITIONS): sweep de F0 usa A_F=10 kN; sweep de A_F codifica no stem.
_AXIAL_F_AMP = {"LIU_2017_AXIAL": 10e3, "LI_2022_TRIBOINT": 10e3,
                # Rodada 4: Liu2016 fig9a/13a/7 usam AF=10 kN (fig11a codifica
                # no stem); Grzejda 0->20 kN pulsante => A_F=10 kN em torno da
                # media; Yang2023AME half-sine 0->2 kN (nota do aparato).
                "LIU_2016": 10e3, "GRZEJDA_2026": 10e3, "YANG_2023_AME": 2e3}
# Packs de modos adotados por fonte (adopted_configs 'pack'), definicao
# canonica de New_Theory/frontier_polish.py:25-30 — o cfg per-rig assume
# esses modos como base.
_PACKS = {
    "PACK": dict(conform_driver="effective",
                 slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=1.0,
                 k_tr_mode="bending", loose_torsion_mode="bolt_torsion",
                 eta_loose=15.0, loose_arrest_floor=0.08),
    "LEGACY": dict(conform_driver="effective",
                   slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=1.0,
                   k_tr_mode="bending", loose_torsion_mode="legacy",
                   loose_arrest_floor=0.0),
    # 'defaults', 'defaults+seq', 'analitico GF': sem pack de modos
}


@dataclass
class CaseResult:
    case_id: str
    ok: bool
    error: Optional[str] = None
    cycles: List[float] = field(default_factory=list)
    ratio: List[float] = field(default_factory=list)
    mae: Optional[float] = None
    rmse: Optional[float] = None
    resid_std: Optional[float] = None    # desvio-padrao dos residuos ASSINADOS
                                         # (pred-dado): alto => divergencia de FORMA
                                         # (reta atravessando curva); baixo => erro
                                         # constante ao longo dos pontos (forma fiel)
    maxerr: Optional[float] = None
    maxerr_at: Optional[float] = None
    # Divisor de ALINHAMENTO usado pela metrica (convencao da campanha: o modelo
    # e' renormalizado pelo proprio valor no 1o ciclo do dado, porque o dado vem
    # normalizado a 1.0 nesse ponto — a queda anterior nao tem contraparte
    # medida). Guardado porque NAO e' recomputavel da curva amostrada: o grid de
    # `cycles` e' esparso e interpolar sobre o transiente de embedding erra por
    # ordens de grandeza. O report DEVE dividir por ele antes de plotar/comparar,
    # senao a pagina mostra curva crua sob um MAE alinhado (defeito 2026-07-27).
    align: Optional[float] = None
    # Os TRES vetores que a metrica de fato comparou, ja alinhados e ja dentro
    # da janela de trim: abscissas do dado, modelo nelas, dado nelas. Existem
    # para que o report NAO precise reinterpolar — reinterpolar na grade
    # amostrada (esparsa) diverge do runner (grade completa) por ate 46% no
    # transiente de embedding, que foi a 2a camada do defeito de 2026-07-27.
    # Quem exibe residuo/MAE-por-estagio deve LER daqui, nunca recomputar.
    metric_x: List[float] = field(default_factory=list)
    metric_pred: List[float] = field(default_factory=list)
    metric_data: List[float] = field(default_factory=list)
    final_pred: Optional[float] = None
    final_data: Optional[float] = None
    decomp: Dict[str, List[float]] = field(default_factory=dict)
    D_final: float = 0.0
    config_used: dict = field(default_factory=dict)
    # F1 item 2 (prereg 2026-07-21): check L7 informacional (removal_energy_
    # check() do analyzer) anexado pos-sim. None em stores antigos (from_dict
    # filtra) e quando a sim falha — nunca altera numero de trajetoria.
    l7_check: Optional[dict] = None
    # 2026-08-28 (divida declarada no anexo §10.1, resolvida a pedido do
    # professor): o balanco de energia do engine PERSISTIDO — W_ext, dU, W_diss
    # e o residuo W_ext + dU - W_diss (absoluto e relativo ao maior termo).
    # Informacional como o l7_check: nunca altera numero de trajetoria; None em
    # stores antigos. Floats NATIVOS (np.float64 quebra o json.dump do batch).
    energy_budget: Optional[dict] = None
    generated_at: str = ""
    engine_fingerprint: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "CaseResult":
        return cls(**{k: v for k, v in d.items()
                      if k in cls.__dataclass_fields__})


# --- ablation hook (2026-08-28) -------------------------------------------
# Default-INERT: only the ablation driver (New_Theory/ablation_run.py) sets
# BAS_ABLATION, a JSON {"overrides": {field: value}, "drop": [mechanism name]}.
# Overrides are applied AFTER every per-rig and per-curve value, and dropped
# mechanisms are removed from `ana.losses` right after construction, so the
# adopted configurations are never touched and the canonical store cannot be
# contaminated (the driver never writes the store). Used for the paper's
# ablation study: coupling frozen (alpha_GW=0) and each mechanism removed.
_ABL_ENV = "BAS_ABLATION"


def _ablacao() -> dict:
    import os
    raw = os.environ.get(_ABL_ENV)
    if not raw:
        return {}
    try:
        d = json.loads(raw)
        return d if isinstance(d, dict) else {}
    except ValueError:
        return {}


def _aplica_ablacao(ana):
    """Remove from the analyzer the mechanisms named in BAS_ABLATION['drop']."""
    spec = _ablacao()
    drop = set(spec.get("drop") or [])
    if drop:
        ana.losses = [m for m in ana.losses if getattr(m, "name", "") not in drop]
    if spec.get("open_loop"):                 # rates see F_0 frozen at F_0_init
        ana.open_loop_rates = True
    return ana


def _energy_budget(ana) -> dict:
    """Balanco de energia do analyzer ao fim da simulacao, em floats nativos.

    `residual_rel` divide pelo MAIOR dos termos do balanco (dissipado ou
    variacao elastica) — dividir so' por W_diss explodiria em curvas de creep
    puro, onde W_diss e' quase zero e o balanco e' todo elastico."""
    E = ana.energy
    W_ext = float(E.W_ext)
    dU = float(E.U_stored - E.U_stored_init)
    W_diss = float(E.W_diss_total)
    res = float(E.conservation_residual)
    escala = max(abs(W_diss), abs(dU), 1e-12)
    return {"W_ext_J": W_ext, "dU_J": dU, "W_diss_J": W_diss,
            "residual_J": res, "residual_rel": res / escala}


def engine_fingerprint() -> str:
    """sha256 curto do estado que muda predicoes: bloco shared + configs
    adotadas per-rig."""
    consts, _ = frozen_constants()
    adopted = {s: kb.adopted_config(s) for s in kb.adopted_sources()}
    blob = json.dumps({"shared": consts, "adopted": adopted},
                      sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


def _common_prefix_len(a: str, b: str) -> int:
    n = 0
    for x, y in zip(a.lower(), b.lower()):
        if x != y:
            break
        n += 1
    return n


def _adopted_for(source: str, case_id: str = "", bolt: str = ""):
    """Chave adotada por PREFIXO da fonte + tokens de GRUPO (MEM iteracao 1):
    a chave casa se e' prefixo da fonte (LIU_2025 casa LIU_2025; LIU_2022_RET
    casa LIU_2022_RETIGHT) E, quando tem tokens ALEM do prefixo comum
    (ex. BAUER_2024_fig8_test1), todos aparecem no case_id — grupos por
    protocolo/figura/lubrificacao. Prefixo mais longo domina; mais tokens de
    grupo desempata. Variantes por-material no stem vencem a fonte
    (ROUSSEAU_HDPE p/ casos 'hdpe'). PR-8: `bolt` (bolt_size do caso) entra
    no alvo de matching — grupos POR TAMANHO (YANG_2023_IJPEM_m6/_m8) casam
    quando o stem nao carrega o tamanho; sem `bolt`, comportamento identico."""
    adopted = kb.adopted_sources()
    cid = (case_id + "|" + bolt).lower() if bolt else case_id.lower()
    if "hpde" in cid or "hdpe" in cid:
        if "ROUSSEAU_HDPE" in adopted:
            return "ROUSSEAU_HDPE"
    best, best_score = None, -1
    srcl = source.lower()
    for s in adopted:
        sl = s.lower()
        # FRONTEIRA ESTRITA (fix iteracao 1): ou a chave e' prefixo da fonte
        # (LIU_2022_RET <- LIU_2022_RETIGHT), ou a fonte e' prefixo da chave
        # (BAUER_2024 -> BAUER_2024_fig8, tokens extras devem estar no cid).
        # Nunca primos foneticos (LI_* vs LIU_* nao casam).
        if srcl.startswith(sl):
            extra = []
            pref = len(sl)
        elif sl.startswith(srcl):
            extra = [t for t in sl[len(srcl):].split("_") if t]
            pref = len(srcl)
        else:
            continue
        if any(t not in cid for t in extra):
            continue                              # grupo nao casa com o caso
        score = pref * 10 + len(extra)            # prefixo domina; grupo desempata
        if score > best_score:
            best, best_score = s, score
    return best


def _adopted_overrides(source: str, base_consts: dict,
                       case_id: str = "", bolt: str = "") -> dict:
    """Pack de modos + cfg adotado da fonte, com tuners legados traduzidos
    pelo shim do Estagio B (mesma fronteira de consumo do solver_worker)."""
    key = _adopted_for(source, case_id, bolt)
    if key is None:
        return {}
    entry = kb.adopted_config(key) or {}
    out = dict(_PACKS.get(entry.get("pack", ""), {}))
    cfg = dict(kb.suggest_overrides(key))         # emb_um->emb_depth etc.
    out.update(translate_legacy_tuners(cfg, base=dict(base_consts, **out),
                                       warn=False))
    # PR-12: delta_spectrum e' uma LISTA (blocos de amplitude) — o
    # suggest_overrides/shim so entendem escalares, entao vem do cfg CRU.
    spec = (entry.get("cfg") or {}).get("delta_spectrum")
    if spec:
        out["delta_spectrum"] = spec
    # PR-27: emb_um pode ser DICT por token de caso (proveniencia L24
    # data_implied_early_drop POR CURVA — ex. Liu2016, estagio rapido
    # dependente de AF/F0). Mesmo mecanismo do delta_amp_mm; dicts morrem
    # no suggest_overrides, entao vem do cfg CRU.
    cid = (case_id + "|" + bolt).lower() if bolt else case_id.lower()
    emb = (entry.get("cfg") or {}).get("emb_um")
    if isinstance(emb, dict):
        for tok, val in emb.items():
            if tok.lower() in cid:
                out["emb_depth"] = float(val) * 1e-6
                break
    # PR-28: bloco generico per_case {token: {campo: valor}} — inputs POR
    # CURVA com proveniencia (ex. Sun reassy: mu de Fig10 por contagem de
    # remontagens, floor lido do plato). emb_um dentro do sub-dict e'
    # convertido um->m; demais campos vao direto (filtrados por
    # __dataclass_fields__ no material_kwargs_for).
    pc = (entry.get("cfg") or {}).get("per_case")
    if isinstance(pc, dict):
        for tok, sub in pc.items():
            if tok.lower() in cid and isinstance(sub, dict):
                for k, v in sub.items():
                    if k == "emb_um":
                        out["emb_depth"] = float(v) * 1e-6
                    else:
                        out[k] = v
                break
    return out


def _axial_f_amp(source: str, stem: str) -> Optional[float]:
    m = re.search(r"AF_([\dp]+)kN", stem)         # liu2017_axial_AF_8p75kN
    if m:
        return float(m.group(1).replace("p", ".")) * 1e3
    m = re.search(r"af([\dp]+)kn", stem)          # R4: liu2016wear_fig11a_af7p5kn
    if m:
        return float(m.group(1).replace("p", ".")) * 1e3
    m = re.search(r"_F(\d+(?:\.\d+)?)kN", stem)   # R4: sun..._axial_F7.5kN_std
    if m:
        return float(m.group(1)) * 1e3
    return _AXIAL_F_AMP.get(source)


def _delta_amp_override(rec: CaseRecord, default_mm: float) -> float:
    """PR-14: amplitude imposta lida do cfg adotado (paper Tabela 2). O campo
    `delta_amp_mm` pode ser escalar (todas as curvas da fonte) OU dict por token
    de espessura (ex. {"t10":0.5,"t14":0.38}). Sem a chave: usa o default do
    caso (bit-identico)."""
    key = _adopted_for(rec.source, rec.case_id, rec.validation_case.bolt_size)
    if key is None:
        return default_mm
    da = (kb.adopted_config(key) or {}).get("cfg", {}).get("delta_amp_mm")
    if da is None:
        return default_mm
    if isinstance(da, dict):
        stem = (rec.csv_path.stem if rec.csv_path else rec.case_id).lower()
        # TOKEN MAIS LONGO VENCE (2026-08-01) — antes era o PRIMEIRO do
        # dict, o que dependia da ordem de insercao e casava por acidente:
        # a curva nova `rousseau2025_hdpe_t10_amp0p2` (Fig. 6, 0.2 mm)
        # pegava o "t10" da serie da Fig. 4 e rodava a 0.5 mm — 2.5x o
        # drive, em SILENCIO. Mesma classe do empate de tokens do
        # YANG_2019 (CLAUDE.md): desempate deterministico e' obrigatorio.
        casa = [(len(tok), tok, val) for tok, val in da.items()
                if tok.lower() in stem]
        if casa:
            casa.sort(reverse=True)
            if len(casa) > 1 and casa[0][0] == casa[1][0]:
                raise ValueError(
                    f"delta_amp_mm: EMPATE de tokens {casa[0][1]!r} vs "
                    f"{casa[1][1]!r} em {stem!r} — desambigue no cfg")
            return float(casa[0][2])
        return default_mm
    return float(da)


def _loading_for(rec: CaseRecord) -> dict:
    case = rec.validation_case
    if rec.family == "other":
        # antes de inputs_for: casos 'other' (modal/forca Sandia etc.) nem
        # sempre tem bolt_size parseavel — a mensagem honesta vem primeiro.
        raise ValueError("carregamento sem proveniência no runner v1 "
                         "(família 'other': modal/força não parametrizado)")
    inp = inputs_for(case)
    if rec.family == "transverse":
        return dict(mode="displacement",
                    delta_mm=_delta_amp_override(rec, case.transverse_displacement_mm),
                    F_amp_N=inp["F_amp_N"]["value"], theta=np.pi / 2,
                    inputs=inp)
    if rec.family == "axial":
        stem = rec.csv_path.stem if rec.csv_path else ""
        f_amp = _axial_f_amp(rec.source, stem)
        if f_amp is None:
            raise ValueError("F_amp axial sem proveniência para este caso")
        return dict(mode="force", delta_mm=0.0, F_amp_N=f_amp, theta=0.0,
                    inputs=inp)
    # rec.family == "creep" (unico restante apos o guard de 'other')
    return dict(mode="force", delta_mm=0.0, F_amp_N=0.0, theta=0.0,
                inputs=inp)


def _spectrum_delta_seq(pattern, n_cycles: int):
    """PR-12: expande um padrao de blocos [[n1, d1_m], [n2, d2_m], ...] na
    sequencia de delta_amp por ciclo (ciclada ate n_cycles). None/[] -> None
    (delta constante, bit-identico)."""
    if not pattern:
        return None
    block = []
    for n_i, d_i in pattern:
        block.extend([float(d_i)] * int(n_i))
    if not block:
        return None
    reps = int(np.ceil(n_cycles / len(block)))
    return (block * reps)[:n_cycles]


def _member_thickness_m(rec: CaseRecord) -> Optional[float]:
    """Espessura da placa [m] lida do token t(\\d+) do stem (ex. hdpe_t14)."""
    stem = rec.csv_path.stem if rec.csv_path else rec.case_id
    m = re.search(r"(?:^|_)t(\d+)(?:_|$)", stem)
    return float(m.group(1)) * 1e-3 if m else None


def _apply_adopted_geometry(geom, source: str, case_id: str, bolt):
    """F1 item 1 (prereg 2026-07-21): d_hole_mm/d_washer_mm ADOTADOS como
    input-de-paper no cfg da fonte -> aplicados a geometria (mm -> m). Mesmo
    idioma do GA_member ("lido do cfg cru": suggest_overrides descarta chaves
    de harness). Sem as duas chaves: geometria INTOCADA -> kj_mode (se
    presente no cfg) permanece em fallback silencioso p/ k_j_init (gate T6:
    engate exige ambos > 0; paridade PASS-inert 8/8, delta MAE = 0.0 exato)."""
    key = _adopted_for(source, case_id, bolt)
    cfg = (kb.adopted_config(key) or {}).get("cfg", {}) if key else {}
    dh, dw = cfg.get("d_hole_mm"), cfg.get("d_washer_mm")
    if dh and dw:
        return replace(geom, d_hole=float(dh) * 1e-3, d_washer=float(dw) * 1e-3)
    return geom


def _trim_n_for(source: str, case_id: str, bolt) -> Optional[float]:
    """F3 (prereg 2026-07-21): TRIM registrado de trecho out-of-model
    (cauda de fratura/terminal — convenção do plano-mestre, bloco C).
    Chave crua `trim_n_max` no cfg adotado: escalar (grupo inteiro) ou dict
    {token: N} (por caso, idioma PR-27). A métrica (MAE/maxerr/resid_std)
    passa a ser computada SÓ em N <= trim; a simulação/plot seguem inteiros
    e o trim fica auditável em config_used + report §6. Cada trim entra na
    LISTA DE EXCEÇÕES da F5 (assinatura do professor)."""
    key = _adopted_for(source, case_id, bolt)
    if key is None:
        return None
    t = (kb.adopted_config(key) or {}).get("cfg", {}).get("trim_n_max")
    if t is None:
        return None
    if isinstance(t, dict):
        cid = (case_id + "|" + str(bolt)).lower() if bolt else case_id.lower()
        for tok, val in t.items():
            if tok.lower() in cid:
                return float(val)
        return None
    return float(t)


def _effective_overrides(rec: CaseRecord, base_consts: dict) -> dict:
    """Overrides per-rig COM as injecoes derivadas por caso — o que o engine
    de fato recebe.

    FONTE UNICA de proposito: `material_kwargs_for` (o que vai para o
    JointMaterial) e o `config_used` gravado no store (a trilha de auditoria)
    tem de sair do MESMO dict. Ate 2026-07-27 eram dois: `simulate_case`
    chamava `_adopted_overrides` na sua copia e a injecao do `k_member_shear`
    so acontecia dentro de `material_kwargs_for` ⇒ uma constante ATIVA e
    fitada-this-rig (GA_member, PR-14) ficava INVISIVEL no store. Foi assim
    que o "INERTE no pack CM" do PR-10 sobreviveu ate o G0 do prereg Rousseau
    — mesma classe de erro do `delta_spectrum` (§4.33) e do `_read_ref_csv`
    (S5): instrumentacao escondendo o valor real.

    PR-10/14: GA_member [N] do cfg adotado -> k_member_shear = GA/t_member por
    caso (t do stem, mm). Membro em cisalhamento: mais espesso = mais macio =
    menos slip na interface (HDPE §4.20). LIDO DO CFG CRU: suggest_overrides
    descarta GA_member (esta no _NON_ENGINE) — por isso o PR-10 o achou
    inerte; o valor real vem de adopted_config direto. Sem GA_member ou sem
    token t no stem: inerte (aco Rousseau cai aqui, e deve mesmo — G~80 GPa
    torna o termo desprezivel).
    """
    ov = _adopted_overrides(rec.source, base_consts, rec.case_id,
                            bolt=rec.validation_case.bolt_size)
    key = _adopted_for(rec.source, rec.case_id, rec.validation_case.bolt_size)
    ga = (kb.adopted_config(key) or {}).get("cfg", {}).get("GA_member") if key else None
    if ga:
        t_m = _member_thickness_m(rec)
        if t_m:
            ov["k_member_shear"] = float(ga) / t_m
    spec = _ablacao()
    if spec.get("bare"):
        # A-PRIORI mode (2026-08-31): drop everything the per-rig configuration
        # adds and keep only the shared constants and the handbook inputs, to
        # answer "what does the model predict on a rig it was never calibrated
        # for". Study only; default-inert.
        ov = {}
    abl = spec.get("overrides") or {}
    if abl or spec.get("bare"):               # ablation study only; inert otherwise
        ov.update(abl)
        ov["_ablation"] = dict(spec)
    return ov


def material_kwargs_for(rec: CaseRecord, inp: dict) -> dict:
    """Kwargs COMPLETOS de JointMaterial p/ o caso (constantes congeladas +
    pack + cfg adotada per-rig + emb com proveniencia + mu). Fonte unica:
    simulate_case E o gui_bridge ("Abrir no Run") montam por aqui."""
    consts, _ = frozen_constants()
    emb_m, _ = emb_depth_vdi(inp["rz"]["value"], n_inner_interfaces=1)
    overrides = _effective_overrides(rec, consts)
    mu = inp["mu"]["value"]
    kw = dict(emb_depth=emb_m, mu_thread=mu, mu_bearing=mu,
              conform_driver="effective", **consts)
    fields = JointMaterial.__dataclass_fields__
    for k, v in overrides.items():                # adotadas per-rig por cima
        if k in fields:
            kw[k] = v
    pf = getattr(rec.validation_case, "_prefit_overrides", None)
    if pf:                                        # ajuste previo do caso USER
        for k, v in pf.items():
            if k in fields:
                kw[k] = v
    for k, v in (_ablacao().get("overrides") or {}).items():   # ablation only
        if k in fields:
            kw[k] = v
    return kw


def _sample_idx(n: int) -> np.ndarray:
    if n <= _MAX_POINTS:
        return np.arange(n + 1)
    return np.unique(np.linspace(0, n, _MAX_POINTS).astype(int))


def _chain_of(rec: CaseRecord):
    """PR-5: se o adopted do caso declara chain='retight' e o stem termina em
    _tN, retorna (prefixo, N, [records t0..tN]); senao None."""
    m = re.search(r"^(.*)_t(\d+)$", rec.case_id)
    if not m:
        return None
    key = _adopted_for(rec.source, rec.case_id,
                       bolt=rec.validation_case.bolt_size)
    if key is None or (kb.adopted_config(key) or {}).get("chain") != "retight":
        return None
    from .case_registry import record as _rec
    prefix, n = m.group(1), int(m.group(2))
    stages = []
    for k in range(n + 1):
        r = _rec(f"{prefix}_t{k}")
        if r is None or r.csv_path is None:
            return None                           # cadeia incompleta: cai no caminho normal
        stages.append(r)
    return prefix, n, stages


def _stage_curve(r: CaseRecord):
    try:
        rel = r.csv_path.relative_to(repo_root()).as_posix()
    except ValueError:
        rel = str(r.csv_path)
    cyc, rr = load_full_curve(rel)                # (ciclos, R_F vs F0 do 1o aperto)
    off = float(getattr(r.validation_case, "csv_x_offset", 0.0) or 0.0)
    sc = float(getattr(r.validation_case, "csv_x_scale", 1.0) or 1.0)
    return np.maximum(cyc - off, 0.0) * sc, rr


def simulate_case(rec: CaseRecord, n_cap: Optional[int] = None,
                  now: Optional[str] = None) -> CaseResult:
    case = rec.validation_case
    stamp = now or datetime.datetime.now().isoformat(timespec="seconds")
    fp = engine_fingerprint()
    try:
        load = _loading_for(rec)
    except ValueError as exc:
        return CaseResult(case_id=rec.case_id, ok=False, error=str(exc),
                          generated_at=stamp, engine_fingerprint=fp)
    chain = _chain_of(rec)
    if chain is not None:
        return _simulate_retight_chain(rec, chain, load, n_cap, stamp, fp)
    try:
        inp = load["inputs"]
        consts, _ = frozen_constants()
        _, emb_br = emb_depth_vdi(inp["rz"]["value"], n_inner_interfaces=1)
        geom = geometry_for_case(case, grip_mm=inp["grip_mm"]["value"],
                                 E=(inp.get("E") or {}).get("value"))
        geom = _apply_adopted_geometry(geom, rec.source, rec.case_id,
                                       rec.validation_case.bolt_size)
        overrides = _effective_overrides(rec, consts)
        mu = inp["mu"]["value"]
        mat = JointMaterial(**material_kwargs_for(rec, inp))
        F0 = case.initial_preload_N
        ana = _aplica_ablacao(DynamicStiffnessAnalyzer(geom, mat, F0))
        # C2/C3 do prereg 2026-08-21-eccles-axial-tres-camadas: a CARGA AXIAL
        # EXTERNA do caso entra no estado como condicao de contorno. So' o modo
        # `constant` e' propagado -- o `intermittent` do ECCLES exige um duty
        # que o paper NAO reporta (a nota de aparato da os valores, 0.7/3.5/5 kN,
        # e diz "periodic on/off", sem periodo), e supor o duty seria inventar
        # input. Sem isto o campo `ax_floor_override` fica inerte POR FALTA DE
        # DRIVER -- exatamente o modo de falha que matou o prereg d319537, aqui
        # do lado certo: inercia proposital e medida.
        _ax = float(getattr(case, "external_axial_N", 0.0) or 0.0)
        if _ax > 0.0 and getattr(case, "external_axial_mode", "") == "constant":
            ana.state.F_ax_ext = _ax

        # curva de referencia / n de ciclos (convencao da campanha, spec §1:
        # trim ratio < FLOOR_TRIM + normalizacao no 1o ponto mantido)
        if rec.case_class == "full_curve":
            try:
                rel = rec.csv_path.relative_to(repo_root()).as_posix()
            except ValueError:            # caso do usuario fora do repo (testes)
                rel = str(rec.csv_path)
            cyc_all, r_all = load_full_curve(rel)
            # R4: CSVs com x em outra unidade (eccles: segundos) — o caso
            # carrega o fator x->ciclos; sem ele a metrica comprime o tempo.
            # PR-34b: offset de convencao (Lu: ancora pre-ciclagem em x=1,
            # eixo log) removido ANTES da escala, clamp >= 0.
            off = float(getattr(case, "csv_x_offset", 0.0) or 0.0)
            cyc_all = np.maximum(cyc_all - off, 0.0) \
                * float(getattr(case, "csv_x_scale", 1.0) or 1.0)
            r_all = r_all / max(r_all[0], 1e-9)
            keep = r_all >= FLOOR_TRIM
            cyc_d, r_d = cyc_all[keep], r_all[keep]
            r_d = r_d / max(r_d[0], 1e-9)
            n_max = int(cyc_d[-1])
        else:
            cyc_d, r_d = None, None
            n_max = int(case.n_cycles)
        if n_cap:
            n_max = min(n_max, int(n_cap))

        # PR-12: espectro de amplitude por bloco (input-de-paper; Bauer fig8
        # 18x80um + 2x155um). Sem a chave no cfg adotado: delta constante.
        spec_seq = _spectrum_delta_seq(overrides.pop("delta_spectrum", None),
                                       n_max)
        ratio = np.empty(n_max + 1)
        ratio[0] = 1.0
        cum: Dict[str, float] = {}
        cum_hist: Dict[str, np.ndarray] = {}
        for n in range(1, n_max + 1):
            if load["mode"] == "displacement":
                d_amp = (spec_seq[n - 1] if spec_seq is not None
                         else load["delta_mm"] * 1e-3)
            else:
                d_amp = None
            ana.step_cycle(load["F_amp_N"], load["theta"], case.frequency_Hz,
                           delta_amp=d_amp)
            ratio[n] = max(ana.state.F_0, 0.0) / F0
            snap = ana.history[-1]
            for mech, dF in snap.dF_0_by_mech.items():
                cum[mech] = cum.get(mech, 0.0) + dF
                cum_hist.setdefault(mech, np.zeros(n_max + 1))[n] = cum[mech]

        idx = _sample_idx(n_max)
        mae = rmse = maxerr = maxerr_at = final_data = None
        resid_std = align_used = None
        m_x: List[float] = []
        m_pred: List[float] = []
        m_data: List[float] = []
        trim_n = _trim_n_for(rec.source, rec.case_id,
                             rec.validation_case.bolt_size)
        if cyc_d is not None:
            kept = cyc_d <= n_max
            if trim_n is not None:
                kept &= (cyc_d <= trim_n)
            cd, rd = cyc_d[kept], r_d[kept]
            if len(cd):
                # alinhamento do modelo no 1o ciclo do dado (campanha)
                n0 = float(cd[0])
                align = max(np.interp(n0, np.arange(n_max + 1), ratio), 1e-9)
                align_used = float(align)
                pred = np.interp(cd, np.arange(n_max + 1), ratio / align)
                signed = pred - rd
                err = np.abs(signed)
                mae = float(np.mean(err))
                rmse = float(np.sqrt(np.mean(err ** 2)))
                resid_std = float(np.std(signed)) if len(signed) > 1 else 0.0
                k = int(np.argmax(err))
                maxerr, maxerr_at = float(err[k]), float(cd[k])
                final_data = float(rd[-1])
                m_x = [float(v) for v in cd]
                m_pred = [float(v) for v in pred]
                m_data = [float(v) for v in rd]
        else:
            final_data = float(case.expected_final_preload_ratio)

        return CaseResult(
            case_id=rec.case_id, ok=True,
            cycles=idx.astype(float).tolist(), ratio=ratio[idx].tolist(),
            mae=mae, rmse=rmse, resid_std=resid_std,
            maxerr=maxerr, maxerr_at=maxerr_at, align=align_used,
            metric_x=m_x, metric_pred=m_pred, metric_data=m_data,
            final_pred=float(ratio[-1]), final_data=final_data,
            # dF_0 do engine e' NEGATIVO (perda) — decomp guarda a PERDA
            # cumulativa normalizada (>0), soma == 1 - ratio em cada ciclo
            decomp={m: (-h / F0)[idx].tolist() for m, h in cum_hist.items()},
            D_final=float(ana.state.D),
            config_used=dict(mode=load["mode"], F_amp_N=load["F_amp_N"],
                             delta_mm=load["delta_mm"], mu=mu,
                             grip_mm=inp["grip_mm"]["value"],
                             rz=inp["rz"]["value"], emb_um=emb_br["total_um"],
                             overrides=overrides, n_max=n_max,
                             trim_n_max=trim_n),
            l7_check=ana.energy.removal_energy_check(),
            energy_budget=_energy_budget(ana),
            generated_at=stamp, engine_fingerprint=fp)
    except Exception as exc:                       # degrada, nao derruba o batch
        return CaseResult(case_id=rec.case_id, ok=False,
                          error=f"{type(exc).__name__}: {exc}",
                          generated_at=stamp, engine_fingerprint=fp)


def _simulate_retight_chain(rec: CaseRecord, chain, load, n_cap, stamp, fp
                            ) -> CaseResult:
    """PR-5 (diretriz do professor): o estagio tN NAO e junta virgem — simula
    a SEQUENCIA t0 -> retighten() -> ... -> tN com estado herdado do engine
    (D persiste; delta_emb renova acoplado ao dano; theta_loose zera; relogio
    do creep persiste). F0 de cada estagio = LIDO do 1o ponto da curva
    (R_F x F0 do 1o aperto). Zero constante nova."""
    prefix, n_stage, stages = chain
    case = rec.validation_case
    try:
        inp = load["inputs"]
        _, emb_br = emb_depth_vdi(inp["rz"]["value"], n_inner_interfaces=1)
        geom = geometry_for_case(case, grip_mm=inp["grip_mm"]["value"],
                                 E=(inp.get("E") or {}).get("value"))
        geom = _apply_adopted_geometry(geom, rec.source, rec.case_id,
                                       rec.validation_case.bolt_size)
        overrides = _effective_overrides(rec, {})
        mu = inp["mu"]["value"]
        mat = JointMaterial(**material_kwargs_for(rec, inp))
        F0_first = case.initial_preload_N
        ana = None
        result_ratio = None
        cum_hist = None
        D_at_start = 0.0
        for k, r_k in enumerate(stages):
            cyc_k, rf_k = _stage_curve(r_k)
            keep = rf_k >= FLOOR_TRIM
            cyc_k, rf_k = cyc_k[keep], rf_k[keep]
            n_max = int(cyc_k[-1])
            if n_cap and k == n_stage:
                n_max = min(n_max, int(n_cap))
            F0_k = F0_first * float(rf_k[0])      # lido-do-dado (1o ponto)
            if ana is None:
                ana = _aplica_ablacao(DynamicStiffnessAnalyzer(geom, mat, F0_k))
            else:
                ana.retighten(new_F0=F0_k)        # estado herdado (D, wear, creep)
            # idem C2/C3 na cadeia de reaperto: a BC externa e' do ENSAIO,
            # nao do estagio, entao vale para todos os estagios e sobrevive ao
            # `retighten` (que reseta F_0, nao a condicao de contorno).
            _axk = float(getattr(case, "external_axial_N", 0.0) or 0.0)
            if _axk > 0.0 and getattr(case, "external_axial_mode", "") == "constant":
                ana.state.F_ax_ext = _axk
            if k == n_stage:
                D_at_start = float(ana.state.D)
                ratio = np.empty(n_max + 1)
                ratio[0] = 1.0
                cum = {}
                cum_hist = {}
            for n in range(1, n_max + 1):
                ana.step_cycle(load["F_amp_N"], load["theta"], case.frequency_Hz,
                               delta_amp=(load["delta_mm"] * 1e-3
                                          if load["mode"] == "displacement"
                                          else None))
                if k == n_stage:
                    ratio[n] = max(ana.state.F_0, 0.0) / F0_k
                    snap = ana.history[-1]
                    for mech, dF in snap.dF_0_by_mech.items():
                        cum[mech] = cum.get(mech, 0.0) + dF
                        cum_hist.setdefault(mech, np.zeros(n_max + 1))[n] = cum[mech]
            if k == n_stage:
                result_ratio = ratio
                seg_cyc, seg_rf = cyc_k, rf_k
        # metrica do segmento N (convencao da campanha: normaliza no 1o ponto)
        rd = seg_rf / max(seg_rf[0], 1e-9)
        kept = seg_cyc <= len(result_ratio) - 1
        cd, rd = seg_cyc[kept], rd[kept]
        n0 = float(cd[0]) if len(cd) else 0.0
        align = max(np.interp(n0, np.arange(len(result_ratio)), result_ratio), 1e-9)
        pred = np.interp(cd, np.arange(len(result_ratio)), result_ratio / align)
        signed = pred - rd
        err = np.abs(signed)
        mae = float(np.mean(err)) if len(err) else None
        rmse = float(np.sqrt(np.mean(err ** 2))) if len(err) else None
        resid_std = float(np.std(signed)) if len(signed) > 1 else (0.0 if len(signed) else None)
        kmax = int(np.argmax(err)) if len(err) else 0
        idx = _sample_idx(len(result_ratio) - 1)
        return CaseResult(
            case_id=rec.case_id, ok=True,
            cycles=idx.astype(float).tolist(),
            ratio=np.asarray(result_ratio)[idx].tolist(),
            mae=mae, rmse=rmse, resid_std=resid_std,
            maxerr=(float(err[kmax]) if len(err) else None),
            maxerr_at=(float(cd[kmax]) if len(err) else None),
            align=(float(align) if len(cd) else None),
            metric_x=[float(v) for v in cd],
            metric_pred=[float(v) for v in pred],
            metric_data=[float(v) for v in rd],
            final_pred=float(result_ratio[-1]),
            final_data=(float(rd[-1]) if len(rd) else None),
            decomp={m: (-h / (F0_first * float(seg_rf[0])))[idx].tolist()
                    for m, h in (cum_hist or {}).items()},
            D_final=float(ana.state.D),
            config_used=dict(mode=load["mode"], F_amp_N=load["F_amp_N"],
                             delta_mm=load["delta_mm"], mu=mu,
                             grip_mm=inp["grip_mm"]["value"],
                             rz=inp["rz"]["value"], emb_um=emb_br["total_um"],
                             overrides=overrides, n_max=len(result_ratio) - 1,
                             chain="retight", chain_stage=n_stage,
                             D_at_start=D_at_start),
            l7_check=ana.energy.removal_energy_check(),
            energy_budget=_energy_budget(ana),
            generated_at=stamp, engine_fingerprint=fp)
    except Exception as exc:
        return CaseResult(case_id=rec.case_id, ok=False,
                          error=f"chain: {type(exc).__name__}: {exc}",
                          generated_at=stamp, engine_fingerprint=fp)


loading_for = _loading_for            # API publica p/ o gui_bridge (Plano B)
