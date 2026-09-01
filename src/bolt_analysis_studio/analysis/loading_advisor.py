"""Loading condition advisor — diagnoses the configured loading and returns
actionable guidance per the LLC (Loosening Loading Conditions) severity ranking.

References:
    LOOSENING_LOADING_CONDITIONS.md §overview, §1.1, §2.3, §5.1, §5.2
    LOAD_FACTORS_DESIGN.md (R-factor map, F_K_min)
    Pai & Hess 2003 — slip onset at 0.46·µ·F_p
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AdvisorReport:
    """Structured advisor output for one loading configuration."""
    loading_label: str = ""
    severity_stars: int = 0          # 1–5 (LLC ranking)
    mechanism: str = ""
    typical_life: str = ""
    key_risk: str = ""
    recommended_analysis: str = ""
    interaction_margin: Optional[float] = None   # 1 − (F_T/µF₀ + F_A/F_sep)
    interaction_ratio: Optional[float] = None    # F_T/µF₀ + F_A/F_sep
    F_K_min_N: Optional[float] = None            # working-plane minimum clamping force
    warnings: List[str] = field(default_factory=list)

    @property
    def severity_glyph(self) -> str:
        return "★" * max(1, min(5, self.severity_stars))

    def to_rich_text(self) -> str:
        """Compact Qt rich-text summary suitable for a QLabel."""
        rows = [
            f"<b>Loading type:</b> {self.loading_label}",
            f"<b>Severity:</b> {self.severity_glyph} ({self.severity_stars}/5)",
            f"<b>Mechanism:</b> {self.mechanism}",
        ]
        if self.typical_life:
            rows.append(f"<b>Typical life:</b> {self.typical_life}")
        if self.key_risk:
            rows.append(f"<b>Key risk:</b> {self.key_risk}")
        if self.recommended_analysis:
            rows.append(f"<b>Analysis:</b> {self.recommended_analysis}")
        if self.interaction_ratio is not None and self.interaction_margin is not None:
            rows.append(
                f"<b>Interaction:</b> F_T/(µ·F₀) + F_A/F_sep = "
                f"{self.interaction_ratio:.2f} (margin = {self.interaction_margin:+.2f})"
            )
        if self.F_K_min_N is not None:
            flag = "" if self.F_K_min_N > 0 else "  ⚠ separation!"
            rows.append(f"<b>F_K_min:</b> {self.F_K_min_N/1000:+.1f} kN{flag}")
        for w in self.warnings:
            rows.append(f"<span style='color:#f38ba8'>⚠ {w}</span>")
        return "<br>".join(rows)


# LLC severity table — ordered from most to least severe
_LLC_PROFILES = {
    "transverse": dict(
        label="Transverse (Junker)",
        stars=5,
        mechanism="Rotational (bearing + thread simultaneous slip)",
        life="10² – 10³ cycles",
        risk="Slip onset at only 46–66% of µ·F_p (Pai–Hess)",
        analysis="Coupled Loosening Analyzer required",
    ),
    "combined": dict(
        label="Combined (axial + transverse)",
        stars=5,
        mechanism="Rotational loosening with axial fatigue interaction",
        life="10² – 10⁴ cycles",
        risk="Super-additive damage when R-factor > 0",
        analysis="Coupled Loosening + Miner's rule",
    ),
    "torsional": dict(
        label="Torsional (applied M_T)",
        stars=4,
        mechanism="Direct loosening torque; bypasses bearing friction",
        life="10¹ – 10³ cycles",
        risk="Any M_T > µ·F_p·r_eff unwinds the joint",
        analysis="Interaction ellipse (§5.2)",
    ),
    "axial_dynamic": dict(
        label="Axial dynamic (R > 0)",
        stars=3,
        mechanism="Fatigue + embedding; NOT Junker rotational",
        life="10⁴ – 10⁷ cycles",
        risk="Fatigue failure; slow preload loss via creep",
        analysis="Fatigue (Miner's), not coupled rotational",
    ),
    "axial": dict(
        label="Axial tension (static/quasi-static)",
        stars=2,
        mechanism="Embedding + gasket creep only",
        life="10⁶+ cycles / long time",
        risk="Preload loss from embedding (not loosening)",
        analysis="Preload-loss models; NO rotational analysis needed",
    ),
    "impulse": dict(
        label="Impulse / shock",
        stars=4,
        mechanism="Transient separation → embedding + micro-slip",
        life="10² – 10⁴ events",
        risk="Peak load may exceed F_sep; momentary zero preload",
        analysis="Time-integration + Miner's rule",
    ),
    "custom": dict(
        label="Custom / user-defined",
        stars=3,
        mechanism="User-specified waveform",
        life="Depends on spectrum",
        risk="Verify R-factor and amplitude manually",
        analysis="Coupled analyzer if transverse component > 0",
    ),
}


def advise_from_loading(loading_data: dict,
                        F_sep_N: Optional[float] = None) -> AdvisorReport:
    """Build an AdvisorReport from a loading-config dictionary.

    Args:
        loading_data: dict with the same keys produced by
            ``PropertyInspector.get_loading_data()`` — ``type``, ``F_preload``,
            ``F_transverse``, ``delta_amplitude``, ``frequency``, ``n_cycles``,
            ``mu_initial``, ``R_factor``, ``F_axial_op`` (optional).
        F_sep_N: separation force at working plane (optional). If None, the
            interaction uses F_preload as a proxy (conservative).
    """
    raw_type = str(loading_data.get("type", "transverse")).lower()
    R = float(loading_data.get("R_factor", 0.0))

    # Classification override: axial with R > 0 is dynamic fatigue-driven
    if raw_type == "axial" and abs(R) > 1e-6:
        key = "axial_dynamic"
    else:
        key = raw_type if raw_type in _LLC_PROFILES else "custom"

    prof = _LLC_PROFILES[key]
    report = AdvisorReport(
        loading_label=prof["label"],
        severity_stars=prof["stars"],
        mechanism=prof["mechanism"],
        typical_life=prof["life"],
        key_risk=prof["risk"],
        recommended_analysis=prof["analysis"],
    )

    F0 = float(loading_data.get("F_preload", 0.0))
    mu = float(loading_data.get("mu_initial", 0.12))
    F_T = float(loading_data.get("F_transverse", 0.0))
    F_A = float(loading_data.get("F_axial_op", loading_data.get("external_force", 0.0)))
    F_sep = float(F_sep_N) if F_sep_N is not None else max(F0, 1.0)

    if F0 > 0.0 and mu > 0.0:
        term_T = F_T / max(mu * F0, 1e-6)
        term_A = F_A / max(F_sep, 1e-6) if F_sep > 0 else 0.0
        ratio = term_T + term_A
        report.interaction_ratio = ratio
        report.interaction_margin = 1.0 - ratio

    # F_K_min estimate (working-plane clamping): F0 − external axial working load
    # Simplified load factor Φ ≈ 0.2 default (rigid joint); user can override
    Phi = float(loading_data.get("Phi_load", 0.2))
    F_K_min = F0 - (1.0 - Phi) * F_A
    report.F_K_min_N = F_K_min

    # Flags
    delta_mm = float(loading_data.get("delta_amplitude", 0.0))
    if raw_type in ("transverse", "combined") and delta_mm > 2.0:
        report.warnings.append(
            f"Transverse amplitude {delta_mm:.2f} mm > 2 mm: complete "
            "loosening possible in < 50 cycles (LLC §2.3)"
        )
    if key == "axial":
        report.warnings.append(
            "Axial static loading does NOT cause Junker rotational "
            "loosening. Fatigue assessment is the critical check (LLC §1.1)."
        )
    if report.interaction_ratio is not None and report.interaction_ratio >= 1.0:
        report.warnings.append(
            "Operating point is OUTSIDE the interaction boundary — "
            "joint cannot sustain this load combination."
        )
    if F_K_min <= 0:
        report.warnings.append(
            f"F_K_min = {F_K_min/1000:.1f} kN — separation at working plane!"
        )

    return report
