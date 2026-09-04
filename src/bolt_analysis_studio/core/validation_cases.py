"""
Validation Case Studies for Bolt Loosening Analysis
====================================================

Pre-saved experimental data from journal papers for validation of the
loosening models implemented in Bolt Analysis Studio.

Each case includes:
- Reference citation
- Test setup parameters
- Experimental results
- Corresponding solver configuration

References:
1. Jiang et al. (2003) - Early Stage Self-Loosening
2. Junker (1969) - Foundational Research (DIN 65151)
3. Nassar & Housari (2006-2007) - Thread/Bearing Friction Effects
4. Yang et al. (2019) - Variable Amplitude Loading

Author: Bolt Analysis Studio Team
Version: 4.0
Date: January 2026
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class ValidationSource(Enum):
    """Source of validation data."""
    JIANG_2003 = "Jiang et al. (2003)"
    JUNKER_1969 = "Junker (1969)"
    NASSAR_2006 = "Nassar & Housari (2006)"
    NASSAR_2007 = "Nassar & Housari (2007)"
    YANG_2019 = "Yang et al. (2019)"
    DIN_65151 = "DIN 65151 Standard"
    # Digitized curve-library sources (2026-07-02, curve_library/digitized_csv)
    LIU_2025 = "Liu et al. (2025) Sci. Rep."
    BAUER_2024 = "Bauer et al. (2024) EFA"
    LIU_2017_AXIAL = "Liu et al. (2017) Tribology Int."
    LU_2024 = "Lu et al. (2024) Sensors"
    ROUSSEAU_2025 = "Rousseau & Bouzid (2025) Materials"
    ICMEZ_2025 = "Icmez et al. (2025) EJRND"
    YANG_2021 = "Yang et al. (2021) Shock & Vib."
    KARLSEN_2022 = "Karlsen & Lemu (2022) EFA"
    SANDIA_2021 = "Sandia IMAC (2021)"
    # Rodada 3 — institutional downloads (2026-07-03)
    LIU_2022_RETIGHT = "Z. Liu et al. (2022) Structures"
    LI_2022_MARSTRUC = "Y. Li et al. (2022) Marine Structures"
    LI_2022_TRIBOINT = "H. Li et al. (2022) Tribology Int."
    YANG_2023_IJPEM = "Yang, Jeong & Lim (2023) IJPEM"
    # Rodada 4 — deep-research (2026-07-12, BAS_V2_papers/E; ingestao 2026-07-14)
    LIU_2016 = "Liu et al. (2016) Wear"
    CHU_2026 = "Chu et al. (2026) Tribology Int."
    ECCLES_2010 = "Eccles et al. (2010) Proc IMechE C"
    YANG_2023_AME = "Yang et al. (2023) Adv. Mech. Eng."
    SUN_2025_CRIMP = "Sun et al. (2025) EFA 169 (crimp)"
    SUN_2025_REASSY = "Sun et al. (2025) EFA 182 (reassembly)"
    GRZEJDA_2026 = "Grzejda et al. (2026) Materials"
    JCSR_2023 = "Yang, Bai & Ding (2023) JCSR"
    CACCESE_2009 = "Caccese et al. (2009) Compos. Struct."
    QIN_2024 = "Qin et al. (2024) Appl. Compos. Mater."
    ZHANG_2006 = "Zhang, Jiang & Lee (2006) JPVT"
    # Rodada 5 — limitacoes L1-L7 (2026-07-16, BAS_V2_papers/F; ingestao fatia 7)
    ZHANG_2018 = "Zhang, Lu, Wang & Zeng (2018) Wear"
    ZHANG_2019 = "Zhang et al. (2019) EFA"
    LIU_2020_WEAR = "Liu, Mi et al. (2020) Wear"


@dataclass
class ExperimentalDataPoint:
    """Single experimental data point."""
    cycles: float
    preload_ratio: float  # F/F0
    loosening_angle_deg: Optional[float] = None
    friction_coeff: Optional[float] = None


@dataclass
class ValidationCase:
    """Complete validation case with experimental data and solver config."""
    # Identification
    name: str
    description: str
    source: ValidationSource
    reference: str

    # Test setup
    bolt_size: str  # e.g., "M12x1.75", "M16x2.0"
    bolt_diameter_mm: float
    pitch_mm: float

    # Initial conditions
    initial_preload_N: float
    preload_percent_yield: float

    # Loading
    transverse_displacement_mm: float
    frequency_Hz: float
    n_cycles: int

    # Surface conditions
    mu_initial: float
    lubricated: bool

    # Expected results
    expected_final_preload_ratio: float
    expected_loosening_deg: float

    # Optional fields with defaults (must come after required fields)
    doi: str = ""  # Digital Object Identifier
    url: str = ""  # Direct link to article
    tolerance_percent: float = 10.0  # Acceptable error

    # Experimental data points (for plotting comparison)
    experimental_data: List[ExperimentalDataPoint] = field(default_factory=list)

    # Notes
    notes: str = ""

    # Optional paths to a pre-built BAS model and a reference-curve CSV.
    # These are used by the Validation Suite's "→ MSD Builder" button and the
    # Results-tab reference overlay. Paths are repo-relative POSIX strings.
    msd_model_path: str = ""
    reference_csv_path: str = ""
    # Rodada 4: multiplicador x->ciclos ao ler o CSV CRU (ex. eccles2010: x em
    # segundos, 12.5 Hz -> 12.5). Consumidores do CSV bruto (runner/report)
    # DEVEM multiplicar por isto; experimental_data ja vem escalado.
    csv_x_scale: float = 1.0
    # PR-34b: offset de convencao do eixo x do CSV CRU (em unidades CRUAS,
    # aplicado ANTES da escala): ciclos = (x - offset) * scale, clamp >= 0.
    # Ex.: Lu2024 fig18/fig20 plotam a ancora pre-ciclagem em x=1 (eixo log).
    csv_x_offset: float = 0.0
    # Rodada 5 (fatia 7): fator de escala da coluna y BRUTA do CSV, aplicado
    # p/ obter fracao F/F0 (ex. Liu2020: R_F em PERCENTUAL, y_scale=0.01).
    # INFORMATIVO, nao propagado: e' consumido SO' pelo loader em tempo de
    # leitura (_read_digitized_csv, no import-time _build_digitized_cases) --
    # experimental_data/expected_final_preload_ratio ja saem escalados deste
    # dataclass. Nenhum consumidor a jusante (runner.py/report_html.py) le
    # este campo; eles re-leem o CSV cru p/ overlay e se autonormalizam
    # dividindo pelo 1o ponto (r/r[0]), o que so' funciona por acidente
    # porque toda ancora t=0 do dataset e' ~1.0 (ou 100.0 no caso Liu2020) --
    # um consumidor futuro do CSV cru que NAO se autonormalize (ou cuja
    # ancora nao seja 1.0/100.0) precisa aplicar csv_y_scale explicitamente,
    # nao herda-lo de graca. Simetrico a csv_x_scale/csv_x_offset acima, mas
    # SEM o equivalente aplicado no re-read (aqueles dois SAO lidos por
    # runner/report; este nao).
    csv_y_scale: float = 1.0
    # CARGA AXIAL EXTERNA (camada C1 do prereg 2026-08-21-eccles-axial-tres-
    # camadas). Condicao de contorno de TRACAO imposta INDEPENDENTEMENTE do
    # drive transversal -- nao e' a componente axial de um F_amp inclinado, e
    # por isso nao cabia em nenhum campo existente.
    #
    # ⚠️ MOTIVO DE EXISTIR, medido em 2026-08-21: as 10 curvas do ECCLES_2010
    # devolviam `to_solver_config()` IDENTICO -- initial_preload=15000 e
    # transverse_force=195000 em TODAS -- inclusive nas SEIS que trazem a carga
    # axial no proprio nome (4 / 3,5 / 3,1 / 2,7 / 1,1 / 0,7 kN). A variavel que
    # o paper VARRE nao entrava no modelo, e as 6 axiais eram simuladas como se
    # fossem as baselines. Isso explica de uma vez por que elas falham, por que
    # as provas de excecao dizem "sobreposicao axial" (a sobreposicao era
    # LITERAL), e por que o teste de premissa F5 lia a fig7 como ensemble de 4
    # replicas: aos olhos do modelo elas ERAM.
    #
    # Procedencia (nota de aparato eccles2010.md, secao "Rig / apparatus"):
    # macacos hidraulicos miniatura aplicam tracao axial FA, force-controlled,
    # superposta independentemente do transversal; "always smaller in magnitude
    # than the preload"; DOIS modos -- `constant` (jacks mantem pressao fixa) e
    # `intermittent` ("applied/released periodically while transverse motion
    # continues"). O modo importa: decide se o termo e' estatico ou pulsado.
    #
    # 0.0 / "" = SEM carga axial externa -- e' o valor CERTO das baselines, nao
    # ausencia de dado. Inerte enquanto a camada C3 (piso anulavel) nao existir:
    # ninguem le estes campos ainda.
    external_axial_N: float = 0.0
    external_axial_mode: str = ""   # "" | "constant" | "intermittent"
    # ---------------------------------------------------------------------
    # VARIAVEL VARRIDA POR CURVA (2026-08-23). Cada campo abaixo existe porque
    # a fonte VARRE aquela variavel e ela NAO estava no registry -- entao duas
    # curvas fisicamente distintas ficavam com assinatura de input IDENTICA e a
    # deteccao de replica as tratava como replicas.
    #
    # ⚠️ ISSO JA RETRATOU EXCECOES 7 VEZES (ECCLES carga axial, ICMEZ grip, CHU
    # rugosidade, LU protocolo, ROUSSEAU espessura, CACCESE condicoes, e o teste
    # de premissa F5 lendo a eccles fig7 como "ensemble de 4 replicas"). A guarda
    # `tests/test_variavel_varrida_nao_e_replica.py` mede a divida; estes campos
    # a pagam.
    #
    # Os valores sao LIDOS do `case_id` (o nome do arquivo digitalizado ja os
    # carrega, o que significa que alguem os leu do paper e eles se perderam no
    # caminho ate aqui). 0.0 / "" = nao aplicavel a esta curva, e e' afirmacao,
    # nao ausencia de dado.
    #
    # ⚠️ INERTES por construcao: nenhum consumidor a jusante os le hoje. Eles
    # servem a DETECCAO DE REPLICA; usa-los na fisica e' passo separado e gateado
    # (foi assim com `external_axial_N`, cujo C3 acabou FALSIFICADO).
    axial_force_amplitude_N: float = 0.0   # LIU_2016 af7p5..12p5kn; LIU_2017 AF_*
    roughness_Ra_um: float = 0.0           # LI_2022_MARSTRUC Ra0p078..0p8
    # ⚠️ COLISAO DE NOME COM O V1, e as duas grandezas NAO sao a mesma: o
    # `CoupledLooseningConfig.grip_length_mm` do `solver_worker` e' o grip TOTAL (default
    # 48 mm = 3.d para M16), enquanto o `lk13p8` do ICMEZ e' o comprimento
    # agarrado daquele rig (13,8 mm). Emitir este campo em `to_solver_config()`
    # sobrescreveria o do V1 EM SILENCIO, com fator ~3,5 de erro. Se um dia for
    # para a fisica, renomeie na fronteira -- nao propague o nome.
    grip_length_mm: float = 0.0            # ICMEZ_2025 lk13p8 / lk19p8
    member_thickness_mm: float = 0.0       # ROUSSEAU t10 / t12 / t14
    reassembly_count: int = 0              # SUN_2025_REASSY reassy02..10
    # Rotulo CATEGORICO, para o que nao e' numero: material+ambiente (JCSR
    # galv/plain/stainless x indoor/outdoor/seawater), geometria+protocolo
    # (CACCESE tapered/protruding/compblock/retighten) e posicao no flange
    # (GRZEJDA bolt1_base/bolt6_central). String de proposito -- forcar um
    # numero nessas seria inventar escala ordinal onde ha categoria.
    specimen_label: str = ""

    def to_solver_config(self) -> Dict[str, Any]:
        """Convert to solver configuration dictionary."""
        # Estimate transverse force from displacement
        # Simplified: F_trans ≈ k_system * displacement
        # For typical M16 joint, k_transverse ~ 300 MN/m
        k_trans_estimated = 300e6  # N/m
        trans_force = k_trans_estimated * (self.transverse_displacement_mm / 1000)

        cfg = {
            "n_cycles": self.n_cycles,
            "initial_preload": self.initial_preload_N,
            "transverse_force": trans_force,
            "bolt_diameter_mm": self.bolt_diameter_mm,
            "pitch_mm": self.pitch_mm,
            "mu_initial": self.mu_initial,
            "lubricated": self.lubricated,
            "frequency": self.frequency_Hz,
        }
        # C2 do prereg 2026-08-21-eccles-axial-tres-camadas: a carga axial
        # externa entra no config SO' quando existe. Condicional de proposito --
        # posta sem condicao, ela mudaria o dict de TODOS os 205 casos, e o
        # G1/G2 do prereg pedem que quem nao tem axial fique BYTE-IDENTICO.
        # Isolamento estrutural em vez de default-inerte: nao ha o que desligar
        # em curva sem carga axial, porque a chave nem aparece.
        if self.external_axial_N:
            cfg["external_axial_N"] = self.external_axial_N
            cfg["external_axial_mode"] = self.external_axial_mode or "constant"
        return cfg

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "source": self.source.value,
            "reference": self.reference,
            "bolt_size": self.bolt_size,
            "bolt_diameter_mm": self.bolt_diameter_mm,
            "pitch_mm": self.pitch_mm,
            "initial_preload_N": self.initial_preload_N,
            "preload_percent_yield": self.preload_percent_yield,
            "transverse_displacement_mm": self.transverse_displacement_mm,
            "frequency_Hz": self.frequency_Hz,
            "n_cycles": self.n_cycles,
            "mu_initial": self.mu_initial,
            "lubricated": self.lubricated,
            "expected_final_preload_ratio": self.expected_final_preload_ratio,
            "expected_loosening_deg": self.expected_loosening_deg,
            "notes": self.notes,
        }


# =============================================================================
# PREDEFINED VALIDATION CASES
# =============================================================================

# Case 1: Jiang et al. (2003) - Low Load Magnitude
JIANG_LOW_LOAD = ValidationCase(
    name="Jiang Low Load (M12)",
    description="Early stage self-loosening under low transverse displacement",
    source=ValidationSource.JIANG_2003,
    reference="Jiang, Y., Zhang, M., Lee, C. (2003). ASME J. Mech. Des. 125(3): 518-526",
    doi="10.1115/1.1586936",
    url="https://asmedigitalcollection.asme.org/mechanicaldesign/article/125/3/518/476008",

    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,

    initial_preload_N=30000,  # ~75% yield for 8.8 grade
    preload_percent_yield=75.0,

    transverse_displacement_mm=0.3,
    frequency_Hz=12.5,
    n_cycles=200,

    mu_initial=0.10,  # Lower friction tested
    lubricated=True,

    expected_final_preload_ratio=0.90,  # 10% loss after 200 cycles
    expected_loosening_deg=0.5,
    tolerance_percent=10.0,

    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.0),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.97),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.94),
        ExperimentalDataPoint(cycles=150, preload_ratio=0.92),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.90),
    ],

    notes="Two-stage model: Stage 1 (plastic deformation) dominates at low loads"
)


# Case 2: Jiang et al. (2003) - High Load Magnitude
JIANG_HIGH_LOAD = ValidationCase(
    name="Jiang High Load (M12)",
    description="Early stage self-loosening under high transverse displacement",
    source=ValidationSource.JIANG_2003,
    reference="Jiang, Y., Zhang, M., Lee, C. (2003). ASME J. Mech. Des. 125(3): 518-526",
    doi="10.1115/1.1586936",
    url="https://asmedigitalcollection.asme.org/mechanicaldesign/article/125/3/518/476008",

    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,

    initial_preload_N=30000,
    preload_percent_yield=75.0,

    transverse_displacement_mm=0.6,
    frequency_Hz=12.5,
    n_cycles=200,

    mu_initial=0.10,
    lubricated=True,

    expected_final_preload_ratio=0.60,  # >40% loss after 200 cycles
    expected_loosening_deg=5.0,
    tolerance_percent=15.0,

    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.0),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.88),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.75),
        ExperimentalDataPoint(cycles=150, preload_ratio=0.67),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.60),
    ],

    notes="Stage 2 (rotational loosening) becomes dominant at higher loads"
)


# Case 3: Junker Test - Standard DIN 65151
JUNKER_STANDARD = ValidationCase(
    name="Junker Standard (M16)",
    description="Standard Junker vibration test per DIN 65151",
    source=ValidationSource.DIN_65151,
    reference="DIN 65151 - Aerospace series, vibration test for fasteners",
    doi="",
    url="https://www.beuth.de/en/standard/din-65151/1454029",

    bolt_size="M16x2.0",
    bolt_diameter_mm=16.0,
    pitch_mm=2.0,

    initial_preload_N=50000,
    preload_percent_yield=70.0,

    transverse_displacement_mm=0.65,  # Standard Junker displacement
    frequency_Hz=12.5,
    n_cycles=2000,

    mu_initial=0.12,
    lubricated=False,  # Dry steel

    expected_final_preload_ratio=0.30,  # Severe loosening expected
    expected_loosening_deg=30.0,
    tolerance_percent=20.0,

    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.0),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.85),
        ExperimentalDataPoint(cycles=300, preload_ratio=0.70),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.55),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.40),
        ExperimentalDataPoint(cycles=1500, preload_ratio=0.35),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.30),
    ],

    notes="Standard Junker test - unsecured fastener baseline"
)


# Case 4: Nassar & Housari (2006) - Effect of Thread Friction
NASSAR_LOW_FRICTION = ValidationCase(
    name="Nassar Low Friction (M12)",
    description="Effect of low thread friction coefficient on loosening",
    source=ValidationSource.NASSAR_2006,
    reference="Nassar, S.A., Housari, B.A. (2006). J. Press. Vessel Tech. 128(4): 590-598",
    doi="10.1115/1.2349569",
    url="https://asmedigitalcollection.asme.org/pressurevesseltech/article/128/4/590/444683",

    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,

    initial_preload_N=28000,
    preload_percent_yield=70.0,

    transverse_displacement_mm=0.5,
    frequency_Hz=25.0,
    n_cycles=1000,

    mu_initial=0.08,  # Low friction (heavily lubricated)
    lubricated=True,

    expected_final_preload_ratio=0.45,
    expected_loosening_deg=15.0,
    tolerance_percent=15.0,

    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.0, friction_coeff=0.08),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.80, friction_coeff=0.07),
        ExperimentalDataPoint(cycles=400, preload_ratio=0.65, friction_coeff=0.065),
        ExperimentalDataPoint(cycles=600, preload_ratio=0.55, friction_coeff=0.06),
        ExperimentalDataPoint(cycles=800, preload_ratio=0.50, friction_coeff=0.058),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.45, friction_coeff=0.055),
    ],

    notes="Low friction leads to rapid loosening - friction below critical threshold"
)


# Case 5: Nassar & Housari (2006) - Effect of High Thread Friction
NASSAR_HIGH_FRICTION = ValidationCase(
    name="Nassar High Friction (M12)",
    description="Effect of high thread friction coefficient on loosening",
    source=ValidationSource.NASSAR_2006,
    reference="Nassar, S.A., Housari, B.A. (2006). J. Press. Vessel Tech. 128(4): 590-598",
    doi="10.1115/1.2349569",
    url="https://asmedigitalcollection.asme.org/pressurevesseltech/article/128/4/590/444683",

    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,

    initial_preload_N=28000,
    preload_percent_yield=70.0,

    transverse_displacement_mm=0.5,
    frequency_Hz=25.0,
    n_cycles=1000,

    mu_initial=0.18,  # High friction (dry, roughened)
    lubricated=False,

    expected_final_preload_ratio=0.85,
    expected_loosening_deg=2.0,
    tolerance_percent=10.0,

    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.0, friction_coeff=0.18),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.95, friction_coeff=0.17),
        ExperimentalDataPoint(cycles=400, preload_ratio=0.92, friction_coeff=0.165),
        ExperimentalDataPoint(cycles=600, preload_ratio=0.90, friction_coeff=0.16),
        ExperimentalDataPoint(cycles=800, preload_ratio=0.87, friction_coeff=0.155),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.85, friction_coeff=0.15),
    ],

    notes="High friction prevents significant loosening - friction above critical"
)


# Case 6: Yang et al. (2019) - Variable Amplitude (High)
YANG_HIGH_AMPLITUDE = ValidationCase(
    name="Yang High Amplitude (M16)",
    description="High displacement amplitude loosening life test",
    source=ValidationSource.YANG_2019,
    reference="Yang, X. et al. (2019). Shock and Vibration, 2036509",
    doi="10.1155/2019/2036509",
    url="https://onlinelibrary.wiley.com/doi/10.1155/2019/2036509",

    bolt_size="M16x2.0",
    bolt_diameter_mm=16.0,
    pitch_mm=2.0,

    initial_preload_N=50000,
    preload_percent_yield=70.0,

    transverse_displacement_mm=0.5,
    frequency_Hz=12.5,
    n_cycles=500,

    mu_initial=0.12,
    lubricated=True,

    expected_final_preload_ratio=0.50,
    expected_loosening_deg=10.0,
    tolerance_percent=15.0,

    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.0),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.85),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.72),
        ExperimentalDataPoint(cycles=300, preload_ratio=0.62),
        ExperimentalDataPoint(cycles=400, preload_ratio=0.55),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.50),
    ],

    notes="D-N curve data point: 0.5mm displacement, short life"
)


# Case 7: Yang et al. (2019) - Variable Amplitude (Low)
YANG_LOW_AMPLITUDE = ValidationCase(
    name="Yang Low Amplitude (M16)",
    description="Low displacement amplitude loosening life test",
    source=ValidationSource.YANG_2019,
    reference="Yang, X. et al. (2019). Shock and Vibration, 2036509",
    doi="10.1155/2019/2036509",
    url="https://onlinelibrary.wiley.com/doi/10.1155/2019/2036509",

    bolt_size="M16x2.0",
    bolt_diameter_mm=16.0,
    pitch_mm=2.0,

    initial_preload_N=50000,
    preload_percent_yield=70.0,

    transverse_displacement_mm=0.3,
    frequency_Hz=12.5,
    n_cycles=2000,

    mu_initial=0.12,
    lubricated=True,

    expected_final_preload_ratio=0.80,
    expected_loosening_deg=3.0,
    tolerance_percent=10.0,

    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.0),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.92),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.88),
        ExperimentalDataPoint(cycles=1500, preload_ratio=0.83),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.80),
    ],

    notes="D-N curve data point: 0.3mm displacement, long life"
)


# Case 8: Severe Transverse Loading (Rapid Failure)
SEVERE_TRANSVERSE = ValidationCase(
    name="Severe Transverse (M16)",
    description="Severe transverse loading causing rapid failure",
    source=ValidationSource.JUNKER_1969,
    reference="Junker, G.H. (1969). SAE Paper 690055",
    doi="10.4271/690055",
    url="https://www.sae.org/publications/technical-papers/content/690055/",

    bolt_size="M16x2.0",
    bolt_diameter_mm=16.0,
    pitch_mm=2.0,

    initial_preload_N=50000,
    preload_percent_yield=70.0,

    transverse_displacement_mm=1.0,  # Severe
    frequency_Hz=12.5,
    n_cycles=500,

    mu_initial=0.12,
    lubricated=True,

    expected_final_preload_ratio=0.10,  # Near complete loss
    expected_loosening_deg=60.0,
    tolerance_percent=25.0,

    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.0),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.70),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.50),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.30),
        ExperimentalDataPoint(cycles=300, preload_ratio=0.20),
        ExperimentalDataPoint(cycles=400, preload_ratio=0.15),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.10),
    ],

    notes="Characteristic S-curve rapid failure pattern"
)


# =============================================================================
# DIGITIZED CURVE-LIBRARY CASES (2026-07-02)
# =============================================================================
#
# 77 preload-decay curves digitized from the figures of the 10 priority papers
# (deep-research rounds 1-2). CSVs live in
#   Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/
# and per-paper apparatus / trial-matrix / caveats notes in
#   Models/CALIBRATION_AND_VALIDATION/curve_library/apparatus_notes/<paper>.md
#
# Cases are built from a compact spec table; n_cycles, the expected final
# ratio and the plotted experimental points are read from the CSV itself so
# the case never drifts from the curve. CSV read failures degrade gracefully
# (empty experimental_data, nominal expectations) so importing this module
# never raises.

import csv as _csv
import re as _re
from pathlib import Path as _Path

_REPO_ROOT = _Path(__file__).resolve().parents[3]
_DIGITIZED_DIR = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
_EXTRACTED_DIR = "Models/CALIBRATION_AND_VALIDATION/curve_library/extracted_csv"


def _read_digitized_csv(csv_name: str, csv_dir: str = _DIGITIZED_DIR,
                        x_scale: float = 1.0,
                        x_offset: float = 0.0,
                        y_scale: float = 1.0) -> List[tuple]:
    """Read a digitized 2-column CSV -> [(cycle, ratio), ...]; [] on failure.
    Aceita cabecalho `cycle` OU `x` (Rodada 4). `x_scale` converte a unidade de
    x p/ ciclos (ex. eccles2010: x em segundos, 12.5 Hz -> x_scale=12.5);
    `x_offset` (PR-34b, unidades CRUAS, antes da escala) remove ancora de
    convencao (ex. Lu2024: ancora pre-ciclagem plotada em x=1, eixo log).
    `y_scale` (Rodada 5) converte a coluna y bruta p/ fracao F/F0 (ex.
    Liu2020: R_F em PERCENTUAL 0-100, y_scale=0.01); a coluna aceita
    `F_over_F0` OU `y` (fallback p/ CSVs com cabecalho `x,y`)."""
    path = _REPO_ROOT / csv_dir / csv_name
    try:
        with open(path, encoding="utf-8", newline="") as f:
            rows = list(_csv.DictReader(f))
        xkey = "cycle" if (rows and "cycle" in rows[0]) else "x"
        ykey = "F_over_F0" if (rows and "F_over_F0" in rows[0]) else "y"
        # max(.., 0): jitter de calibracao do eixo na origem (ex. chu2026 test7
        # x=-9.1 em ~4000 ciclos) — o 1o ponto e' a ancora t=0, nao ciclo <0
        return [(max((float(r[xkey]) - x_offset) * x_scale, 0.0),
                 float(r[ykey]) * y_scale)
                for r in rows]
    except Exception:
        return []


def _downsample(points: List[tuple], max_pts: int = 9) -> List[tuple]:
    """Evenly thin a point list, always keeping first and last."""
    if len(points) <= max_pts:
        return points
    idx = [round(i * (len(points) - 1) / (max_pts - 1)) for i in range(max_pts)]
    return [points[i] for i in sorted(set(idx))]


def _varredura_por_curva(csv_name: str) -> dict:
    """Variavel VARRIDA lida do nome do arquivo digitalizado.

    O `case_id` ja carrega o valor (alguem o leu do paper ao digitalizar) e ele
    se perdia no caminho ate o `ValidationCase`. Resultado medido: curvas
    fisicamente distintas com assinatura de input IDENTICA, e a deteccao de
    replica tratando-as como replicas -- defeito que ja retratou excecoes SETE
    vezes (ECCLES carga axial, ICMEZ grip, CHU rugosidade, LU protocolo,
    ROUSSEAU espessura, CACCESE condicoes, e o teste de premissa F5 lendo a
    eccles fig7 como "ensemble de 4 replicas"). A guarda
    `tests/test_variavel_varrida_nao_e_replica.py` mede a divida; isto a paga.

    PADROES EXPLICITOS, um por fonte, DE PROPOSITO: um parser generico acertaria
    mais casos e erraria em SILENCIO. O que nao casa fica em 0/"" -- afirmacao de
    "nao se aplica", nao ausencia -- e a guarda denuncia, porque ela falha
    quando a divida CAI sem registro.

    ⚠️ INERTE por construcao: nenhum consumidor a jusante le estes campos hoje.
    Eles servem a DETECCAO DE REPLICA. Usa-los na fisica e passo separado e
    gateado (foi assim com `external_axial_N`, cujo C3 acabou FALSIFICADO).
    """
    n = csv_name.lower()
    out: dict = {}
    # ⚠️ `p(\d+)`, nao `p(\d)`: `af8p75kn` tem DOIS digitos e com um so o
    # casamento INTEIRO falha (o `kn` nao encaixa) => campo 0.0 em silencio, e as
    # curvas 8,75/11,25 kN voltam a colidir. Foi a guarda que denunciou, nomeando
    # o par -- um parser generico teria lido 8,7 e ninguem veria.
    m = _re.search(r"_af_?(\d+)(?:p(\d+))?kn", n)         # LIU_2016 / LIU_2017
    if m:
        out["axial_force_amplitude_N"] = float(
            m.group(1) + ("." + m.group(2) if m.group(2) else "")) * 1000.0
    m = _re.search(r"ra(\d+)p(\d+)", n)                    # LI_2022_MARSTRUC
    if m:
        out["roughness_Ra_um"] = float(m.group(1) + "." + m.group(2))
    m = _re.search(r"lk(\d+)p(\d)", n)                     # ICMEZ (arq. demir2024)
    if m:
        out["grip_length_mm"] = float(m.group(1) + "." + m.group(2))
    m = _re.search(r"_(?:steel|hdpe)_t(\d+)", n)            # ROUSSEAU
    if m:
        out["member_thickness_mm"] = float(m.group(1))
    m = _re.search(r"reassy(\d+)", n)                       # SUN_2025_REASSY
    if m:
        out["reassembly_count"] = int(m.group(1))
    # CATEGORICOS: string porque forcar numero seria inventar escala ordinal
    # onde ha CATEGORIA (material, ambiente, geometria/protocolo, posicao).
    for pat in (r"jcsr\d+_([a-z]+_[a-z]+)",
                r"caccese\d+_([a-z0-9_]+?)(?:_rep\d)?\.csv",
                r"grzejda\d+\w*_(bolt\d+_[a-z]+)",
                r"fig13a_(dry|mos2)"):
        m = _re.search(pat, n)
        if m:
            out["specimen_label"] = m.group(1)
            break
    # SUN_2025_CRIMP: DUAS varridas no mesmo nome -- lubrificacao e tipo de porca.
    # ⚠️ `nogrease` CONTEM `grease`, o trap de substring que o CLAUDE.md documenta:
    # a alternancia tem de por `nogrease` PRIMEIRO, senao toda curva seca e' lida
    # como engraxada. (O `axial_F*kN_*` nao tem token de graxa; fica so' a porca.)
    m = _re.search(r"(nogrease|grease)?_?(standard|crimp)", n)
    if m:
        out["specimen_label"] = "_".join(x for x in (m.group(1), m.group(2)) if x)
    # QIN_2024: percentagem de INTERFERENCIA do ajuste, `I = (d-D)/D x 100%`
    # (nota de aparato `qin2024acm.md` L80-81: 0% folga / 0,6% / 1,2%). Entra como
    # ROTULO, nao numero, porque a propria nota registra que e' "state variable
    # with no current analog in BAS V2" -- distinguir e' o que se precisa aqui;
    # dar-lhe escala fisica seria afirmar mais do que o modelo representa.
    m = _re.search(r"_i(\d+(?:p\d+)?)pct", n)
    if m:
        out["specimen_label"] = "interference_" + m.group(1) + "pct"
    # KARLSEN_2022: DISPOSITIVO DE TRAVAMENTO. ⚠️ Token LONGO PRIMEIRO na
    # alternancia (`hvtorqued` antes de `hv`, `vibralock_torqued` antes de
    # `vibralock`) -- o trap de substring que ja custou o regex do SUN.
    # ⚠️ Por que ROTULO e nao `initial_preload_N`: os 11 F0 do KARLSEN sao todos
    # distintos, mas `run21p0` (HV) e `run29p0` (vibralock_torqued) tem F0
    # IDENTICO (685 kN) e diferem no travamento -- o numero nao resolve. E F0 e'
    # grandeza ALCANCADA: o `_PARES_REPLICA_DECLARADOS` existe porque "aperto
    # nunca repete" (4-14% nos pares do LU), logo por-lo na chave destruiria
    # pareamento legitimo em todo o projeto. Na chave entram grandezas
    # AJUSTADAS, nunca ALCANCADAS.
    m = _re.search(r"karlsen\d+_m\d+_(hvtorqued|hv|vibralock_torqued|vibralock)_", n)
    if m:
        out["specimen_label"] = "lock_" + m.group(1)
    # LI_2022_MARSTRUC: pre-carga NOMINAL (5/10/15 kN), que e' o que o paper
    # ajusta. Mesmo motivo de ser rotulo e nao `initial_preload_N`.
    m = _re.search(r"marstruc_creep_(\d+)kn_", n)
    if m:
        out["specimen_label"] = "preload_" + m.group(1) + "kN"
    m = _re.search(r"fig9a_m(\d+)nm", n)                    # LIU_2016 torque
    if m:
        out["specimen_label"] = "torque_m" + m.group(1) + "nm"
    return out


def _digitized_case(csv_name, name, source, reference, doi, bolt_size,
                    d_mm, pitch_mm, F0_N, pct_yield, amp_mm, freq_Hz,
                    notes, mu=0.15, lubricated=False,
                    csv_dir=_DIGITIZED_DIR, x_scale=1.0,
                    x_offset=0.0, y_scale=1.0,
                    ax_N=0.0, ax_mode="") -> ValidationCase:
    pts = _read_digitized_csv(csv_name, csv_dir, x_scale, x_offset, y_scale)
    n_cycles = int(pts[-1][0]) if pts else 1000
    final_ratio = max(pts[-1][1], 0.01) if pts else 0.5  # avoid /0 in validate_result
    return ValidationCase(
        name=name,
        description=f"Digitized literature curve ({csv_name})",
        source=source,
        reference=reference,
        doi=doi,
        bolt_size=bolt_size,
        bolt_diameter_mm=d_mm,
        pitch_mm=pitch_mm,
        initial_preload_N=F0_N,
        preload_percent_yield=pct_yield,
        transverse_displacement_mm=amp_mm,
        frequency_Hz=freq_Hz,
        n_cycles=max(n_cycles, 1),
        mu_initial=mu,
        lubricated=lubricated,
        expected_final_preload_ratio=final_ratio,
        expected_loosening_deg=0.0,       # not reported per-curve
        tolerance_percent=15.0,
        experimental_data=[ExperimentalDataPoint(cycles=c, preload_ratio=r)
                           for c, r in _downsample(pts)],
        notes=notes,
        reference_csv_path=f"{csv_dir}/{csv_name}",
        csv_x_scale=x_scale,
        csv_x_offset=x_offset,
        csv_y_scale=y_scale,
        external_axial_N=ax_N,
        external_axial_mode=ax_mode,
        **_varredura_por_curva(csv_name),
    )


def _build_digitized_cases() -> List[ValidationCase]:
    S = ValidationSource
    cases: List[ValidationCase] = []

    def add(csv_name, name, amp, F0, pct, notes="", **kw):
        cases.append(_digitized_case(
            csv_name, name, kw["source"], kw["reference"], kw["doi"],
            kw["bolt_size"], kw["d"], kw["p"], F0, pct, amp, kw["freq"],
            (notes + (" " if notes else "") + kw["note_common"]).strip(),
            mu=kw.get("mu", 0.15), lubricated=kw.get("lubricated", False),
            csv_dir=kw.get("csv_dir", _DIGITIZED_DIR),
            x_scale=kw.get("x_scale", 1.0),
            x_offset=kw.get("x_offset", 0.0),
            y_scale=kw.get("y_scale", 1.0),
            ax_N=kw.get("ax_N", 0.0),
            ax_mode=kw.get("ax_mode", "")))

    # --- Liu 2025 Sci Rep — M16x2.0 8.8, F0=60 kN (only M16 source) --------
    liu25 = dict(source=S.LIU_2025, doi="10.1038/s41598-025-02936-6",
                 reference="Liu et al. (2025). Sci. Rep. 15 (s41598-025-02936-6)",
                 bolt_size="M16x2.0", d=16.0, p=2.0, freq=12.5,
                 note_common="Freq not reported (nominal 12.5). 3-stage; post-N_D is fatigue-driven — trim for pure loosening. See apparatus_notes/liu2025_scirep_M16.md")
    for amp, csvn in [(0.25, "liu2025_M16_amp0p25.csv"), (0.30, "liu2025_M16_amp0p3.csv"),
                      (0.40, "liu2025_M16_amp0p4.csv"), (0.50, "liu2025_M16_amp0p5.csv"),
                      (0.60, "liu2025_M16_amp0p6.csv"), (0.80, "liu2025_M16_amp0p8.csv")]:
        add(csvn, f"Liu2025 M16 {amp:.2f}mm", amp, 60000, 60.0, **liu25)
    add("liu2025_M16_fig2_single.csv", "Liu2025 M16 Fig2 (to fracture)", 0.80,
        60000, 60.0, "Amplitude not labeled (0.8 mm class); runs to fracture.", **liu25)

    # --- Bauer 2024 EFA — M8 (20 kN, ~70 um) + M12x1.5 (50 kN, spectrum) ---
    bauerM8 = dict(source=S.BAUER_2024, doi="10.1016/j.engfailanal.2024.108404",
                   reference="Bauer et al. (2024). Eng. Fail. Anal. 162:108404",
                   bolt_size="M8x1.25", d=8.0, p=1.25, freq=12.5,
                   note_common="Local slip amplitude ~70 um; s_crit=99 um. Freq symbolic in paper. See apparatus_notes/bauer2024_efa.md")
    for i in range(1, 7):
        add(f"bauer2024_M8_fig6_rep{i}.csv", f"Bauer2024 M8 70um rep{i}",
            0.07, 20000, 85.0, **bauerM8)
    bauerM12 = dict(bauerM8, bolt_size="M12x1.5", d=12.0, p=1.5,
                    note_common="Variable spectrum ~80 um base / 150 um peaks; 3-stage collapse knee (surface_damage target). See apparatus_notes/bauer2024_efa.md")
    for i in range(1, 4):
        add(f"bauer2024_M12_fig8_test{i}.csv", f"Bauer2024 M12 spectrum t{i}",
            0.08, 50000, 80.0, **bauerM12)

    # --- Liu 2017 Tribology Int — M12x1.75, AXIAL force-controlled, 30 Hz --
    liu17 = dict(source=S.LIU_2017_AXIAL, doi="10.1016/j.triboint.2017.05.037",
                 reference="Liu et al. (2017). Tribology Int. 115:432-451",
                 bolt_size="M12x1.75", d=12.0, p=1.75, freq=30.0,
                 note_common="AXIAL force-controlled (use V2 force mode, not delta_amp); transverse amp set to 0. See apparatus_notes/liu2017_triboint_axial.md")
    for f0kn, pct, csvn in [(15.0, 19, "liu2017_axial_F0_15kN.csv"),
                            (16.5, 21, "liu2017_axial_F0_16p5kN.csv"),
                            (18.0, 23, "liu2017_axial_F0_18kN.csv"),
                            (19.5, 25, "liu2017_axial_F0_19p5kN.csv"),
                            (21.0, 27, "liu2017_axial_F0_21kN.csv")]:
        add(csvn, f"Liu2017 axial P0={f0kn:g}kN", 0.0, f0kn * 1000, pct,
            "A_F = 10 kN axial amplitude.", **liu17)
    for afkn, csvn in [(7.5, "liu2017_axial_AF_7p5kN.csv"),
                       (8.75, "liu2017_axial_AF_8p75kN.csv"),
                       (11.25, "liu2017_axial_AF_11p25kN.csv"),
                       (12.5, "liu2017_axial_AF_12p5kN.csv")]:
        add(csvn, f"Liu2017 axial AF={afkn:g}kN", 0.0, 18000, 23,
            f"P0 = 18 kN; axial amplitude A_F = {afkn:g} kN.", **liu17)

    # --- Lu 2024 Sensors — M8 8.8, nickel-steel plates, ~1 Hz --------------
    lu24 = dict(source=S.LU_2024, doi="10.3390/s24113306", x_offset=1.0,
                reference="Lu et al. (2024). Sensors 24(11):3306",
                bolt_size="M8x1.25", d=8.0, p=1.25, freq=1.0,
                note_common="Soft nickel-steel plates (large stage-I drop). See apparatus_notes/lu2024_sensors_M8.md")
    # amp1p0: F0 = 11567 N — a linha 22 N.m da Tabela 9 e' IDENTICA a linha
    # 1.0 mm da Tabela 8 (36.8/57.1/87.9/93.6%): a curva 1.0 mm da fig18 E' o
    # teste T22 da fig20 (mesmo teste, 2 figuras) => mesmo F0 da Tabela 9.
    # (A harmonizacao de 2026-07-31 manha na amp0p5 foi REVERTIDA: premissa
    # errada — a fig20 roda a 1.0 mm, nao 0.5; ver A1/A2 do plano
    # lu2024_plano_melhoria.md.)
    for amp, f0, csvn in [(0.25, 12000, "lu2024_M8_fig18_amp0p25.csv"),
                          (0.5, 12000, "lu2024_M8_fig18_amp0p5.csv"),
                          (1.0, 11567, "lu2024_M8_fig18_amp1p0.csv"),
                          (1.5, 12000, "lu2024_M8_fig18_amp1p5.csv"),
                          (2.0, 11600, "lu2024_M8_fig18_amp2p0.csv")]:
        add(csvn, f"Lu2024 M8 {amp:g}mm", amp, f0, 51.0,
            "22 N.m torque class (F0~12 kN).", **lu24)
    # fig20: amplitude REAL = 1.0 mm (era 0.5 no registry — ERRO DE INPUT,
    # corrigido 2026-07-31 com prova dupla: p.19 "After 100 cycles of
    # tangential 1 mm displacement..." + Tabela 9 linha 22Nm == Tabela 8
    # linha 1.0mm ao digito). Toda a calibracao per-source anterior a esta
    # data foi feita com metade do drive real.
    for tnm, f0, pct, csvn in [(4, 2105, 9, "lu2024_M8_fig20_T4Nm.csv"),
                               (10, 5963, 25, "lu2024_M8_fig20_T10Nm.csv"),
                               (16, 8402, 36, "lu2024_M8_fig20_T16Nm.csv"),
                               (22, 11567, 49, "lu2024_M8_fig20_T22Nm.csv"),
                               (28, 15027, 64, "lu2024_M8_fig20_T28Nm.csv")]:
        add(csvn, f"Lu2024 M8 T={tnm}Nm", 1.0, f0, pct,
            "Torque sweep (Fig 20); amplitude 1.0 mm (p.19 + Tabela 9==Tabela 8 @22Nm).", **lu24)
    # Fig 14a (sec3.1.3, digitalizada 2026-07-31 por digitize_lu2024_fig14.py
    # com round-trip contra as ancoras da prosa: fim 0.25mm 10511 vs 10539N):
    # corridas LONGAS a 22 N.m/half-sine — repeticoes independentes das
    # condicoes da fig18 com janelas 3-10x maiores (0.25mm ate ~1040 ciclos).
    # F0 = pico pos-aperto DIGITALIZADO por curva (prosa da 12398/12285/12696
    # sem declarar a ordem; picos lidos 2-4% acima — F0 do CSV manda na
    # normalizacao). x_offset=0: o ciclo ja sai zerado no pico.
    lu24_f14 = {**lu24, "x_offset": 0.0}
    for amp, f0, csvn in [(0.25, 12688, "lu2024_M8_fig14_amp0p25_long.csv"),
                          (0.5, 12498, "lu2024_M8_fig14_amp0p5_long.csv"),
                          (1.0, 13198, "lu2024_M8_fig14_amp1p0_long.csv")]:
        add(csvn, f"Lu2024 M8 fig14 {amp:g}mm long", amp, f0, 51.0,
            "Fig 14a half-sine long run (sec3.1.3); repeat independente da "
            "fig18 na mesma condicao 22 N.m.", **lu24_f14)

    # --- Rousseau 2025 Materials — M12x1.75 8.8, member material/thickness -
    # Amplitudes CONFIRMADAS na Tabela 2 do PDF oficial (baixado 2026-08-01
    # p/ pdfs_open_access na Rodada 6): HDPE 0.5/0.49/0.38 mm (ja aplicadas
    # via cfg ROUSSEAU_HDPE.delta_amp_mm) e ACO 0.05/0.05/0.04 mm — o
    # registry rodava o aco a 0.5 mm (10x o drive real, padrao fig20 do LU;
    # o fit antigo c_bend=0.3/emb=1.0um absorvia o erro). Prosa: Fig. 6
    # compara HDPE vs aco a 0.2 mm; Fig. 10 varre 0.03/0.05/0.10 no aco.
    rous = dict(source=S.ROUSSEAU_2025, doi="10.3390/ma18020462",
                reference="Rousseau & Bouzid (2025). Materials 18(2):462",
                bolt_size="M12x1.75", d=12.0, p=1.75, freq=1.0,
                note_common="Amplitudes POR SERIE da Tabela 2 (PDF na biblioteca): HDPE ~0.5 mm (per-especime no cfg), aco 0.05/0.05/0.04 mm. See apparatus_notes/rousseau2025_materials_M12.md")
    for mat, t, f0, pct, amp, csvn in [
            ("HDPE", 10, 4000, 7, 0.5, "rousseau2025_hdpe_t10.csv"),
            ("HDPE", 12, 4050, 7, 0.5, "rousseau2025_hdpe_t12.csv"),
            ("HDPE", 14, 4000, 7, 0.5, "rousseau2025_hdpe_t14.csv"),
            ("steel", 10, 10250, 19, 0.05, "rousseau2025_steel_t10.csv"),
            ("steel", 12, 10250, 19, 0.05, "rousseau2025_steel_t12.csv"),
            ("steel", 14, 10350, 19, 0.04, "rousseau2025_steel_t14.csv")]:
        add(csvn, f"Rousseau2025 {mat} t{t}", amp, f0, pct,
            f"Clamped members: {mat}, {t} mm thick each.", **rous)
    # Fig. 6 (p.8) digitalizada em 2026-08-01 (recuperacao pos-erratum,
    # prereg 2026-08-01-rousseau-recuperacao): CONDICAO NOVA para os dois
    # ramos — t10 a 0.2 mm com F0 ~3.5 kN nos DOIS materiais (a Fig. 5 roda
    # aco a 10 kN/0.05 mm e a Fig. 4 HDPE a 4 kN/0.5 mm). E' o held-out do
    # re-fit do aco: nenhum numero e' fitado aqui.
    for mat, f0, csvn in [
            ("steel", 3511, "rousseau2025_steel_t10_amp0p2.csv"),
            ("HDPE", 3515, "rousseau2025_hdpe_t10_amp0p2.csv")]:
        add(csvn, f"Rousseau2025 {mat} t10 0.2mm (Fig6)", 0.2, f0, 7,
            f"Clamped members: {mat}, 10 mm thick each; Fig. 6 comparison "
            f"run (both materials at the same ~3.5 kN preload).", **rous)

    # --- Icmez 2025 EJRND ('demir2024') — M8x1.25 DIN933, 2x2x2 factorial --
    icm = dict(source=S.ICMEZ_2025, doi="10.56038/ejrnd.v5i1.693",
               reference="Icmez, Ince & Enser (2025). EJRND 5(1):294-309",
               bolt_size="M8x1.25", d=8.0, p=1.25, freq=12.5,
               note_common="Junker J160 per DIN 65151. See apparatus_notes/demir2024_ejrnd_M8.md")
    for amp in (0.3, 0.4):
        for f0kn, pct in ((14.3, 61), (17.6, 75)):
            for lk in (13.8, 19.8):
                a = f"{amp:g}".replace(".", "p")
                fk = f"{f0kn:g}".replace(".", "p")
                lks = f"{lk:g}".replace(".", "p")
                add(f"demir2024_amp{a}_F{fk}_lk{lks}.csv",
                    f"Icmez2025 M8 {amp:g}mm/{f0kn:g}kN/lk{lk:g}",
                    amp, f0kn * 1000, pct, f"Clamp length {lk:g} mm.", **icm)

    # --- Yang 2021 S&V — M8x1.25x70 8.8, composite tension+shear, 10 Hz ----
    y21 = dict(source=S.YANG_2021, doi="10.1155/2021/1441122",
               reference="Yang et al. (2021). Shock and Vibration 1441122",
               bolt_size="M8x1.25", d=8.0, p=1.25, freq=10.0,
               note_common="Composite excitation (transverse disp + axial load, 90 deg phase); F0=14.1 kN nominal. Final drop = fracture. See apparatus_notes/yang2021_sv_combined.md")
    add("yang2021_fig2_typical.csv", "Yang2021 M8 typical (Fig2)", 0.8, 14100, 60,
        "Typical 3-stage recession curve.", **y21)
    for amp, axkn, csvn in [(1.0, 2.0, "yang2021_amp1p0mm_ax2kN.csv"),
                            (0.8, 6.0, "yang2021_amp0p8mm_ax6kN.csv"),
                            (0.6, 8.0, "yang2021_amp0p6mm_ax8kN_r1.csv"),
                            (0.7, 11.2, "yang2021_amp0p7mm_ax11p2kN.csv"),
                            (0.5, 8.0, "yang2021_amp0p5mm_ax8kN.csv")]:
        add(csvn, f"Yang2021 M8 {amp:g}mm+{axkn:g}kN", amp, 14100, 60,
            f"Axial load amplitude {axkn:g} kN (xi={amp/axkn:.3f} mm/kN).", **y21)
    # replicas 2-3 da condicao 0.6mm-8kN (Fig. 6b2/6b3), digitalizadas em
    # 2026-07-31 (prereg 2026-07-31-yang2021-replicas-0p6-prereg.md, G1:
    # media das 3 vidas 14483 vs Tabela 3 14666 = 1.2%). Junto com a r1
    # formam a 1a familia de replicas de BANCADA real da fonte (piso da
    # condicao: MAE 0.042 / mx 0.472 / sd 0.079 — colapso varia 12.5k-16.3k).
    for rep in ("r2", "r3"):
        add(f"yang2021_amp0p6mm_ax8kN_{rep}.csv",
            f"Yang2021 M8 0.6mm+8kN {rep}", 0.6, 14100, 60,
            f"Axial load amplitude 8 kN (xi=0.075 mm/kN). Replica {rep[1]}/3 "
            f"da mesma condicao (Fig. 6b).", **y21)

    # --- Yang 2019 S&V — M10, ~26 kN ---------------------------------------
    y19 = dict(source=S.YANG_2019, doi="10.1155/2019/2036509",
               reference="Yang et al. (2019). Shock and Vibration 2036509",
               bolt_size="M10x1.5", d=10.0, p=1.5, freq=5.0,
               note_common="See apparatus_notes/yang2019_sv_M10.md")
    add("yang2019_M10_amp0p4_5Hz.csv", "Yang2019 M10 0.4mm 5Hz", 0.4, 26400, 48, **y19)
    add("yang2019_M10_amp0p6_10Hz.csv", "Yang2019 M10 0.6mm 10Hz", 0.6, 25500, 47,
        "10 Hz (frequency-effect contrast test).", **dict(y19, freq=10.0))
    add("yang2019_M10_amp0p6_5Hz.csv", "Yang2019 M10 0.6mm 5Hz", 0.6, 24000, 44, **y19)
    add("yang2019_M10_varamp_small_to_large.csv", "Yang2019 M10 var-amp up", 0.5,
        27200, 50, "Variable-amplitude blocks small->large (accumulation test, not constant condition).", **y19)
    add("yang2019_M10_varamp_large_to_small.csv", "Yang2019 M10 var-amp down", 0.5,
        27300, 50, "Variable-amplitude blocks large->small; step at ~1550 cycles = amplitude switch.", **y19)

    # --- Karlsen 2022 EFA — M30/M42 10.9, HV vs Vibralock, 1 Hz ------------
    k30 = dict(source=S.KARLSEN_2022, doi="10.1016/j.engfailanal.2022.106590", x_offset=1.0,
               reference="Karlsen & Lemu (2022). Eng. Fail. Anal. 106590",
               bolt_size="M30x3.5", d=30.0, p=3.5, freq=1.0,
               note_common="See apparatus_notes/karlsen2022_M30M42.md")
    # ERRATA 2026-08-06 (mesma noite do D-X): ao corrigir a base da r1.2 eu
    # escrevi pct=66, inconsistente com o grupo. As outras SEIS implicam
    # escoamento F0/pct = 523-529 kN (M30 10.9, A_s=561 mm2 x 940 MPa = 527);
    # a r1.2 a 66 implicava 501,5 — 5 % fora. O valor coerente e' 331/527 = 63.
    # Efeito na metrica: NENHUM — `preload_percent_yield` e' INERTE no runner
    # (varredura 59/63/66/90 da 0.0171/0.0434/0.0195 bit-identico). Corrigido
    # assim mesmo pelo precedente do `k_torsional` (D-P): campo inerte hoje
    # cobra de quem ativar o canal que o le (aqui, a conformacao por pressao,
    # cujo gate e' `pct/70`).
    for run, f0, pct, csvn in [("HV r1.2", 331, 63, "karlsen2022_M30_HV_run1p2.csv"),
                               # D-Y (2026-08-06, prereg karlsen-run2p2-base): mesma
                               # classe da r1.2 — a CSV x 312 dava valores REDONDOS
                               # (300/250/200/150/90/38 kN = cruzamentos de gridline) e
                               # o ciclo 1 fora ANCORADO no F0 nominal, nao lido. Figura:
                               # 332,0 kN (esta sessao) / 332,7 (subagente D-X), com
                               # controles na MESMA coluna x (r7.1 +0,4 %, r6.2 -0,2 %).
                               ("HV r2.2", 333, 63, "karlsen2022_M30_HV_run2p2.csv"),
                               ("HV r6.2", 340, 65, "karlsen2022_M30_HV_run6p2.csv"),
                               ("HV r7.1", 312, 59, "karlsen2022_M30_HV_run7p1.csv"),
                               ("HV-torqued r14.2", 370, 70, "karlsen2022_M30_HVtorqued_run14p2.csv"),
                               ("Vibralock r9.0", 351, 67, "karlsen2022_M30_vibralock_run9p0.csv"),
                               ("Vibralock-torqued r16.0", 373, 71, "karlsen2022_M30_vibralock_torqued_run16p0.csv")]:
        add(csvn, f"Karlsen2022 M30 {run}", 1.0, f0 * 1000, pct, **k30)
    k42 = dict(k30, bolt_size="M42x4.5", d=42.0, p=4.5)
    for run, f0, pct, csvn in [("HV r20.0", 660, 63, "karlsen2022_M42_HV_run20p0.csv"),
                               ("HV r21.0", 685, 65, "karlsen2022_M42_HV_run21p0.csv"),
                               ("Vibralock r23.0", 720, 68, "karlsen2022_M42_vibralock_run23p0.csv"),
                               ("Vibralock-torqued r29.0", 685, 65, "karlsen2022_M42_vibralock_torqued_run29p0.csv")]:
        add(csvn, f"Karlsen2022 M42 {run}", 1.5, f0 * 1000, pct, **k42)

    # --- Sandia 2021 C-Beam — modal excitation, low amplitude --------------
    snd = dict(source=S.SANDIA_2021, doi="10.1007/978-3-030-47626-7_30",
               reference="Sandia/IMAC XXXVIII (2021). SAND2019-12525C",
               bolt_size='1/4" (est.)', d=6.35, p=1.27, freq=280.0,
               note_common="Bolt size NOT reported (nominal 1/4 in). Modal shear, micro-slip; time->cycles at 280 Hz. Low-amplitude slip-onset anchor. See apparatus_notes/sandia2021_cbeam.md")
    for dur, bolt, f0, csvn in [("5min", 1, 786, "sandia2021_cbeam_5min_bolt1.csv"),
                                ("5min", 2, 784, "sandia2021_cbeam_5min_bolt2.csv"),
                                ("15min", 1, 780, "sandia2021_cbeam_15min_bolt1.csv"),
                                ("15min", 2, 780, "sandia2021_cbeam_15min_bolt2.csv"),
                                ("30min", 1, 780, "sandia2021_cbeam_30min_bolt1.csv"),
                                ("30min", 2, 780, "sandia2021_cbeam_30min_bolt2.csv")]:
        add(csvn, f"Sandia2021 C-Beam {dur} b{bolt}", 0.0, f0, 5.0,
            "30-min runs are on run-in (non-virgin) joints." if dur == "30min" else "", **snd)

    # --- Z. Liu 2022 Structures — M12 retightening (reaperto), 0.3 mm, 12.5 Hz
    l22 = dict(source=S.LIU_2022_RETIGHT, doi="10.1016/j.istruc.2022.08.049",
               reference="Z. Liu et al. (2022). Structures 44:1303-1311",
               bolt_size="M12x1.75", d=12.0, p=1.75, freq=12.5,
               note_common="Disp-controlled 0.3 mm per GB/T 10431-2008; T=80 Nm. R_F normalized to FIRST-tightening F0 (retight curves can start <1 or >1). See apparatus_notes/liu2022_istruc_retightening.md")
    for cond, f0, csvn in [("dry F=19.78kN", 19780, "liu2022_fig5_dry_F19p78kN.csv"),
                           ("dry F=21.50kN", 21500, "liu2022_fig5_dry_F21p50kN.csv"),
                           ("oil F=28.18kN", 28180, "liu2022_fig5_oil_F28p18kN.csv"),
                           ("oil F=26.00kN", 26000, "liu2022_fig5_oil_F26p00kN.csv")]:
        add(csvn, f"Liu2022 M12 first-tight {cond}", 0.3, f0, 50,
            "First tightening (Fig 5).", **l22)
    for grp, lube, label in [("fig6a_dry_release", "dry", "release-dry"),
                             ("fig6b_oil_release", "oil", "release-oil"),
                             ("fig7a_oil_direct", "oil", "direct-oil")]:
        for t in range(4):
            add(f"liu2022_{grp}_t{t}.csv", f"Liu2022 M12 {label} t{t}", 0.3, 26000, 50,
                f"Retightening series ({lube}), t{t} = {'first tightening' if t == 0 else str(t) + 'th retightening'}.", **l22)
    for t in range(5):
        note = ("4th retightening — ends in FATIGUE FRACTURE at ~1500 cyc (trim)."
                if t == 4 else f"Multiple-retightening series (dry), t{t}.")
        add(f"liu2022_fig8_multi_t{t}.csv", f"Liu2022 M12 multi t{t}", 0.3, 26000, 50,
            note, **l22)

    # --- Y. Li 2022 Marine Structures — M16 static contact creep (x = MINUTES)
    lm22 = dict(source=S.LI_2022_MARSTRUC, doi="10.1016/j.marstruc.2022.103263",
                reference="Y. Li et al. (2022). Marine Structures 85:103263",
                bolt_size="M16x2.0", d=16.0, p=2.0, freq=1.0 / 60.0,
                note_common="STATIC contact creep, NO vibration - x column is TIME IN MINUTES (1 pseudo-cycle = 1 min, hence freq = 1/60 Hz so cycle/freq = real seconds). Fit with delta_amp=0, wear/loosening off (k_creep only). See apparatus_notes/li2022_marstruc_contact_creep.md")
    for f0, pct, ra, csvn in [(10000, 14, "0.8", "li2022marstruc_creep_10kN_Ra0p8_min.csv"),
                              (10000, 14, "0.078", "li2022marstruc_creep_10kN_Ra0p078_min.csv"),
                              (10000, 14, "0.122", "li2022marstruc_creep_10kN_Ra0p122_min.csv"),
                              (10000, 14, "0.306", "li2022marstruc_creep_10kN_Ra0p306_min.csv"),
                              (5000, 7, "0.8", "li2022marstruc_creep_5kN_Ra0p8_min.csv"),
                              (15000, 21, "0.8", "li2022marstruc_creep_15kN_Ra0p8_min.csv")]:
        add(csvn, f"Li2022 creep {f0//1000}kN Ra{ra}", 0.0, f0, pct,
            f"304SS M16x80; Ra {ra} um; 600 min at 25.2 C.", **lm22)

    # --- H. Li 2022 Tribology Int — M10 axial x frequency (force mode)
    lt22 = dict(source=S.LI_2022_TRIBOINT, doi="10.1016/j.triboint.2022.107933",
                reference="H. Li et al. (2022). Tribology Int. 176:107933",
                bolt_size="M10x1.5", d=10.0, p=1.5, freq=10.0,
                note_common="AXIAL force-controlled, A_F=10 kN (use V2 force mode). See apparatus_notes/li2022_triboint_axial_freq.md")
    add("li2022ti_axialmin_10Hz.csv", "Li2022 axial 10Hz", 0.0, 12500, 34, **lt22)
    add("li2022ti_axialmin_15Hz.csv", "Li2022 axial 15Hz", 0.0, 12500, 34, **dict(lt22, freq=15.0))
    add("li2022ti_axialmin_20Hz.csv", "Li2022 axial 20Hz", 0.0, 12500, 34, **dict(lt22, freq=20.0))
    add("li2022ti_axial_10Hz_full.csv", "Li2022 axial 10Hz full run", 0.0, 12500, 34,
        "Full 3-stage run; stage 3 (>3.3e5 cyc) is thread-root crack growth (trim).", **lt22)

    # --- Yang/Jeong/Lim 2023 IJPEM — M6/M8 Junker amplitude sweep -----------
    # Full PDF unavailable (Springer paywall; downloaded copy was a 1-page
    # preview, deleted). SUBSTITUTE source: the note's table data (approximate,
    # digitized from the published figures) already in extracted_csv/ — see
    # Models/CALIBRATION_AND_VALIDATION/10_Yang_2023_phenomenological_model.md
    # (includes full MSD builder config, D-N table and master-curve model).
    # freq=10 Hz + M6 F0=11 kN CORRIGIDOS 2026-07-28 pelo companion OA
    # (PMC11901137, Table 1: "initial clamping force, frequency ... identical
    # to those used in a previous study [o 2023 IJPEM]"). Antes: 12.5 Hz era
    # default herdado (e o DEEP_RESEARCH dizia 5 Hz — ambos errados); M6
    # rodava 8500 N. Impacto medido antes de aplicar: freq inerte (disp-mode),
    # F0 misto, ZERO mudancas de status no tripe. Nota: apparatus_notes/
    # yang2023ijpem.md (secao "desacordos ... RESOLVIDOS").
    y23 = dict(source=S.YANG_2023_IJPEM, doi="10.1007/s12541-023-00783-x",
               reference="Yang, Jeong & Lim (2023). IJPEM 24:825-835",
               bolt_size="M8x1.25", d=8.0, p=1.25, freq=10.0,
               csv_dir=_EXTRACTED_DIR,
               note_common="Junker DIN 65151, class 10.9, unlubricated (mu~0.18). APPROXIMATE table-derived curves (full PDF not in library); conditions/MSD config in 10_Yang_2023_phenomenological_model.md")
    for amp, csvn in [(0.18, "10_Yang_2023_phenomenological_model__0_18_mm_below_threshold__1.csv"),
                      (0.25, "10_Yang_2023_phenomenological_model__0_25_mm__2.csv"),
                      (0.35, "10_Yang_2023_phenomenological_model__0_35_mm__3.csv"),
                      (0.45, "10_Yang_2023_phenomenological_model__0_45_mm__4.csv"),
                      (0.55, "10_Yang_2023_phenomenological_model__0_55_mm__5.csv"),
                      (0.65, "10_Yang_2023_phenomenological_model__0_65_mm__6.csv")]:
        add(csvn, f"Yang2023 M8 {amp:.2f}mm", amp, 14300, 42,
            "Below slip threshold (saturates)." if amp == 0.18 else "", **y23)
    y23m6 = dict(y23, bolt_size="M6x1.0", d=6.0, p=1.0)
    for amp, csvn in [(0.15, "10_Yang_2023_phenomenological_model__0_15_mm_below_threshold__7.csv"),
                      (0.30, "10_Yang_2023_phenomenological_model__0_30_mm__8.csv"),
                      (0.50, "10_Yang_2023_phenomenological_model__0_50_mm__9.csv")]:
        add(csvn, f"Yang2023 M6 {amp:.2f}mm", amp, 11000, 45,
            "Below slip threshold (saturates)." if amp == 0.15 else "", **y23m6)

    # =====================================================================
    # Rodada 4 (BAS_V2_papers/E, 2026-07-12; ingestao 2026-07-14). Manifesto:
    # README_RODADA4.md. So os simulaveis: EXCLUIDOS basavahess1998 (simulacao),
    # lakes2007jemt (tensao A QUENTE, termica fora do modelo), fretting G2
    # (ancoras x,y sem F/F0), alsardia2024 + liu2016_fig3 (x = no do aperto,
    # serie de recovery — futura), sun110030 nao-F/F0, qin 100/150C e caccese
    # tempcycle/reaperto-programado (termica/reaperto-por-tempo fora do modelo),
    # yang2023ame transversal/biaxial/F0-sweep (transversal em FORCA + composto
    # nao suportados pelo runner).
    # =====================================================================
    _R4 = "BAS_V2_papers/E. Rodada 4 (deep-research 2026-07-11)/digitized_csv"

    # --- Liu 2016 Wear — M12x1.75 axial forca 30 Hz (rig irmao do Liu2017) --
    l16 = dict(source=S.LIU_2016, doi="10.1016/j.wear.2015.10.012",
               reference="Liu et al. (2016). Wear 346-347:66-77",
               bolt_size="M12x1.75", d=12.0, p=1.75, freq=30.0, csv_dir=_R4,
               mu=0.132,
               note_common="Axial force-mode 30 Hz; A283D EZP; mu=0.132 dry (DIN 946, medido). AF corrigido (nota: eixo do paper x2). Ver E/apparatus_notes/liu2016wear.md")
    for m0, f0 in [(30, 14000), (35, 16000), (40, 18000), (45, 20000), (50, 22000)]:
        add(f"liu2016wear_fig9a_m{m0}nm.csv", f"Liu2016 axial M0={m0}Nm", 0.0,
            f0, 55, "Torque sweep @AF=10kN.", **l16)
    for af in ["7p5", "8p75", "10", "11p25", "12p5"]:
        add(f"liu2016wear_fig11a_af{af}kn.csv",
            f"Liu2016 axial AF={af.replace('p', '.')}kN", 0.0, 14000, 55,
            "AF sweep @M0=30Nm.", **l16)
    add("liu2016wear_fig13a_dry.csv", "Liu2016 axial dry", 0.0, 14000, 55,
        "Dry vs MoS2 contrast @M0=30Nm AF=10kN.", **l16)
    add("liu2016wear_fig13a_mos2.csv", "Liu2016 axial MoS2", 0.0, 20000, 55,
        "MoS2-coated (mu=0.029 medido); F0 sobe p/ ~20kN no mesmo torque.",
        **dict(l16, mu=0.029, lubricated=True))
    add("liu2016wear_fig7_run1_1e6cyc.csv", "Liu2016 axial long 1e6", 0.0, 14000, 55,
        "Corrida longa 1e6 ciclos @M0=30Nm AF=10kN.", **l16)
    add("liu2016wear_fig7_run2_5e6cyc.csv", "Liu2016 axial long 5e6", 0.0, 14000, 55,
        "Corrida 5e6 ciclos; cauda nao-monotonica out-of-model (nota).", **l16)

    # --- Chu 2026 TI — MJ10 (GH159/GH4169) Junker desloc 10 Hz --------------
    chu = dict(source=S.CHU_2026, doi="10.1016/j.triboint.2026.112193",
               reference="Chu et al. (2026). Tribology Int. 223:112193",
               bolt_size="M10x1.5", d=10.0, p=1.5, freq=10.0, csv_dir=_R4,
               note_common="MJ10 aerospace (aprox. M10x1.5); superligas GH159/GH4169; Junker 10 Hz. Ver E/apparatus_notes/chu2026ti.md")
    for csvn, dmm, f0, extra in [
            ("chu2026ti_D0p3mm_F0_49kN_test1.csv", 0.3, 49000, "Sem queda (estavel 2500 cyc)."),
            ("chu2026ti_D0p4mm_F0_49kN_test2.csv", 0.4, 49000, ""),
            ("chu2026ti_D0p4mm_F0_61kN_test7.csv", 0.4, 61000, "F0 sweep."),
            ("chu2026ti_D0p4mm_F0_73kN_test8.csv", 0.4, 73000, "F0 sweep."),
            ("chu2026ti_D0p5mm_F0_49kN_test3.csv", 0.5, 49000, ""),
            ("chu2026ti_D0p5mm_F0_49kN_Ra1p6um_test9.csv", 0.5, 49000, "Ra=1.6um (rugosidade)."),
            ("chu2026ti_D0p7mm_F0_49kN_test4.csv", 0.7, 49000, ""),
            ("chu2026ti_D1p0mm_F0_49kN_test5.csv", 1.0, 49000, ""),
            ("chu2026ti_D1p0mm_F0_49kN_test6_repeat.csv", 1.0, 49000, "Replica do test5.")]:
        add(csvn, f"Chu2026 D={dmm}mm F0={f0//1000}kN"
            + (" Ra1.6" if "Ra1p6" in csvn else ("" if "repeat" not in csvn else " rep")),
            dmm, f0, 60, extra, **chu)

    # --- Eccles 2010 — M8 EZP prevailing-torque, Junker 12.5 Hz (x=segundos) -
    ecc = dict(source=S.ECCLES_2010, doi="10.1243/09544062JMES1493",
               reference="Eccles et al. (2010). Proc IMechE C 224:483-495",
               bolt_size="M8x1.25", d=8.0, p=1.25, freq=12.5, csv_dir=_R4,
               x_scale=12.5,
               note_common="Porca prevailing-torque all-metal (1.5-2.3 N.m medido); x em SEGUNDOS convertido a ciclos (12.5 Hz); +-0.65mm; F0=15kN. Ver E/apparatus_notes/eccles2010.md")
    # C1 do prereg 2026-08-21-eccles-axial-tres-camadas: a carga axial externa
    # por curva, LIDA do paper (valores no proprio nome dos arquivos, e a nota
    # de aparato confirma o modo). ZERO nas 4 baselines e' o valor CERTO, nao
    # ausencia de dado. Ate 2026-08-21 os 10 casos devolviam to_solver_config()
    # IDENTICO -- a variavel que o paper VARRE nao entrava no modelo.
    # Classificacao da nota (secao "V2 mapping"): o piso de arresto SEGURA em
    # 3/7a-c/8a/8c e e' ANULADO em 7d/8b/8d, que sao o falsificador novo.
    for csvn, nm, extra, ax_N, ax_mode in [
            ("eccles2010_fig3_typical_no_axial.csv", "fig3 typical", "", 0.0, ""),
            ("eccles2010_fig7a_no_axial.csv", "fig7a no-axial", "", 0.0, ""),
            ("eccles2010_fig8a_no_axial_baseline1.csv", "fig8a baseline1", "", 0.0, ""),
            ("eccles2010_fig8c_no_axial_baseline2.csv", "fig8c baseline2", "", 0.0, ""),
            ("eccles2010_fig6_annotated_4kN_axial.csv", "fig6 axial 4kN", "Axial constante 4kN SIMULTANEO (composto fora do modelo).", 4000.0, "constant"),
            ("eccles2010_fig7b_axial_1p1kN_constant.csv", "fig7b axial 1.1kN", "Axial constante simultaneo (composto).", 1100.0, "constant"),
            ("eccles2010_fig7c_axial_2p7kN_constant.csv", "fig7c axial 2.7kN", "Axial constante simultaneo (composto).", 2700.0, "constant"),
            ("eccles2010_fig7d_axial_3p1kN_constant.csv", "fig7d axial 3.1kN", "Axial constante simultaneo (composto).", 3100.0, "constant"),
            ("eccles2010_fig8b_axial_0p7kN_intermittent.csv", "fig8b axial 0.7kN interm", "Axial intermitente (composto).", 700.0, "intermittent"),
            ("eccles2010_fig8d_axial_3p5kN_intermittent.csv", "fig8d axial 3.5kN interm", "Axial intermitente (composto).", 3500.0, "intermittent")]:
        add(csvn, f"Eccles2010 {nm}", 0.65, 15000, 50, extra,
            ax_N=ax_N, ax_mode=ax_mode, **ecc)

    # --- Yang 2023 AME — MJ6 jet nut CFRP; SO o caso axial-isolado ----------
    add("yang2023ame_axial.csv", "Yang2023AME axial 2kN", 0.0, 6500, 40,
        "Axial half-sine 0->2kN 2 Hz (pulsante); jet nut MJ6 TC16 (self-locking); "
        "CFRP 48 plies. transversal/biaxial em FORCA = nao suportado (skip). "
        "Ver E/apparatus_notes/yang2023ame.md",
        **dict(source=S.YANG_2023_AME, doi="10.1177/16878132221145342",
               reference="Yang et al. (2023). Adv. Mech. Eng. 15(1)",
               bolt_size="M6x1.0", d=6.0, p=1.0, freq=2.0, csv_dir=_R4,
               note_common=""))

    # --- Sun 2025 EFA 169 — crimp vs standard (GH4169), M8 inferido ---------
    s235 = dict(source=S.SUN_2025_CRIMP, doi="10.1016/j.engfailanal.2024.109235",
                reference="Sun et al. (2025). Eng. Fail. Anal. 169:109235",
                bolt_size="M8x1.25", d=8.0, p=1.25, freq=12.5, csv_dir=_R4,
                note_common="Tamanho INFERIDO M8 (nota); porca crimp = prevailing torque fora do modelo (caveat). Ver E/apparatus_notes/sun2025efa109235.md")
    for csvn, nm, amp in [
            ("sun2025efa109235_transverse_nogrease_standard.csv", "transv dry std", 0.30),
            ("sun2025efa109235_transverse_nogrease_crimp.csv", "transv dry crimp", 0.30),
            ("sun2025efa109235_transverse_grease_standard.csv", "transv grease std", 0.30),
            ("sun2025efa109235_transverse_grease_crimp.csv", "transv grease crimp", 0.30)]:
        add(csvn, f"Sun2025crimp {nm}", amp, 15000, 50,
            "Graxa (lubrificado)." if "grease_" in csvn and "nogrease" not in csvn else "",
            **s235)
    for csvn, nm in [
            ("sun2025efa109235_axial_F7.5kN_standard.csv", "axial 7.5kN std"),
            ("sun2025efa109235_axial_F7.5kN_crimp.csv", "axial 7.5kN crimp"),
            ("sun2025efa109235_axial_F17.5kN_standard.csv", "axial 17.5kN std"),
            ("sun2025efa109235_axial_F17.5kN_crimp.csv", "axial 17.5kN crimp")]:
        add(csvn, f"Sun2025crimp {nm}", 0.0, 15000, 50, "Ramo axial (forca).", **s235)

    # --- Sun 2025 EFA 182 — remontagem MJ8 (reuso), transv 12.5 Hz ----------
    s030 = dict(source=S.SUN_2025_REASSY, doi="10.1016/j.engfailanal.2025.110030",
                reference="Sun et al. (2025). Eng. Fail. Anal. 182:110030",
                bolt_size="M8x1.25", d=8.0, p=1.25, freq=12.5, csv_dir=_R4,
                note_common="MJ8 crimp; pre-condicionado por N remontagens (estado de reuso). Ver E/apparatus_notes/sun2025efa110030.md")
    for n in (2, 4, 6, 8, 10):
        add(f"sun2025efa110030_fig11a_loosening_reassy{n:02d}.csv",
            f"Sun2025reassy N={n}", 0.30, 15000, 50,
            f"Apos {n} remontagens.", **s030)

    # --- Grzejda 2026 — CONTROLE NEGATIVO (F/F0 ~ 1.0), axial pulsante ------
    grz = dict(source=S.GRZEJDA_2026, doi="10.3390/ma19071414",
               reference="Grzejda et al. (2026). Materials 19:1414",
               bolt_size="M10x1.25", d=10.0, p=1.25, freq=1.0, csv_dir=_R4,
               note_common="BENCHMARK NULO: multi-parafuso Instron, 22kN preload, axial pulsante 0->20kN; F/F0~1.0 (+-2%) — o modelo deve prever ~zero perda. Janela curta. Ver E/apparatus_notes/grzejda2026mat.md")
    add("grzejda2026mat_bolt1_base.csv", "Grzejda2026 bolt1 (nulo)", 0.0, 22000, 62, "", **grz)
    add("grzejda2026mat_bolt6_central.csv", "Grzejda2026 bolt6 (nulo)", 0.0, 22000, 62, "", **grz)

    # --- JCSR 2023 — relaxacao M20 x ambiente (x=DIAS; freq=1/86400) --------
    jc = dict(source=S.JCSR_2023, doi="10.1016/j.jcsr.2023.108211",
              reference="Yang, Bai & Ding (2023). JCSR 211:108211",
              bolt_size="M20x2.5", d=20.0, p=2.5, freq=1.0 / 86400.0, csv_dir=_R4,
              note_common="Relaxacao estatica; x em DIAS (freq=1/86400 => dt=1 dia). Ver E/apparatus_notes/jcsr2023.md")
    # gfrp_seawater EXCLUIDO: parafuso GFRP (fora do dominio metalico, como
    # HDPE) SOBE a F/F0=1.23 por inchaco higroscopico e colapsa a 0 — ganho de
    # preload + fratura, ambos fora do modelo.
    for csvn, nm, f0, extra in [
            ("jcsr2023_plain_indoor.csv", "plain indoor", 145000, "Ambiente interno (limpo)."),
            ("jcsr2023_plain_outdoor.csv", "plain outdoor", 145000, "Exterior (corrosao fora do modelo)."),
            ("jcsr2023_plain_seawater.csv", "plain seawater", 145000, "Imersao (corrosao fora do modelo)."),
            ("jcsr2023_galv_seawater.csv", "galv seawater", 145000, "Galvanizado imerso (corrosao)."),
            ("jcsr2023_stainless_seawater.csv", "stainless seawater", 145000, "A4-70 imerso.")]:
        add(csvn, f"JCSR2023 {nm}", 0.0, f0, 55, extra, **jc)

    # --- Caccese 2009 — relaxacao compo/metal (x=HORAS; freq=1/3600) --------
    cac = dict(source=S.CACCESE_2009, doi="10.1016/j.compstruct.2008.07.031",
               reference="Caccese et al. (2009). Compos. Struct. 89:285-293",
               bolt_size="1/2-13 UNC", d=12.7, p=1.954, freq=1.0 / 3600.0, csv_dir=_R4,
               note_common="Relaxacao composto/metal; x em HORAS (freq=1/3600 => dt=1h). Series com reaperto programado/termica EXCLUIDAS. Ver E/apparatus_notes/caccese2009.md")
    add("caccese2009_retighten_12p7mm_no_retighten.csv", "Caccese2009 12.7mm no-ret",
        0.0, 22250, 40, "Sem reaperto; painel 12.7mm.", **cac)
    cac19 = dict(cac, bolt_size="3/4-10 UNC", d=19.05, p=2.54)
    add("caccese2009_retighten_19p1mm_no_retighten.csv", "Caccese2009 19.1mm no-ret",
        0.0, 45500, 40, "Sem reaperto; painel 19.1mm.", **cac19)
    add("caccese2009_compblock_34kPa.csv", "Caccese2009 compblock 34kPa",
        0.0, 22250, 40, "Bloco de compressao (F0/parafuso INFERIDO do total /4).", **cac)
    add("caccese2009_compblock_71kPa.csv", "Caccese2009 compblock 71kPa",
        0.0, 46000, 40, "Bloco de compressao (F0/parafuso INFERIDO).", **cac)
    add("caccese2009_protruding_45kN.csv", "Caccese2009 protruding 45kN",
        0.0, 45000, 40, "", **cac19)
    add("caccese2009_tapered_45kN_rep1.csv", "Caccese2009 tapered rep1",
        0.0, 45000, 40, "Cabeca tapered.", **cac19)
    add("caccese2009_tapered_45kN_rep2.csv", "Caccese2009 tapered rep2",
        0.0, 45000, 40, "Cabeca tapered.", **cac19)

    # --- Qin 2024 — relaxacao CFRP-Ti 25C (x=SEGUNDOS; freq=1) --------------
    qin = dict(source=S.QIN_2024, doi="10.1007/s10443-024-10214-3",
               reference="Qin et al. (2024). Appl. Compos. Mater. 31",
               bolt_size="M6x1.0", d=6.0, p=1.0, freq=1.0, csv_dir=_R4,
               note_common="CFRP-Ti M6 interference-fit; x em SEGUNDOS (freq=1 => dt=1s); 100/150C EXCLUIDOS (termica). Ver E/apparatus_notes/qin2024acm.md")
    for csvn, nm, f0 in [("qin2024acm_25C_i0pct.csv", "25C I=0%", 5800),
                          ("qin2024acm_25C_i0p6pct.csv", "25C I=0.6%", 5200),
                          ("qin2024acm_25C_i1p2pct.csv", "25C I=1.2%", 3700)]:
        add(csvn, f"Qin2024 {nm}", 0.0, f0, 35,
            "Interference-fit (estado inicial fora do modelo).", **qin)

    # --- Zhang 2006 JPVT — 2 curvas P-N REAIS (frota 2026-07-15; fig12 sem
    # amplitude reportada = fora; as 9 'curvas de grip' antigas da galeria
    # sao SINTETICAS, nao rastreaveis ao PDF — ver apparatus_notes/zhang2006.md)
    zh = dict(source=S.ZHANG_2006, doi="10.1115/1.2217972",
              reference="Zhang, Jiang & Lee (2006). J. Pressure Vessel Technol. 128:388-393",
              bolt_size="M12x1.25", d=12.0, p=1.25, freq=0.5,
              note_common="Rig do estudo anterior (Jiang); freq 0.5 Hz assumida da familia. Ver apparatus_notes/zhang2006.md")
    add("zhang2006_fig3_illus_M12x125_20kN_amp0p35.csv",
        "Zhang2006 fig3 M12 0.35mm", 0.35, 20000, 50,
        "2 estagios completos ate colapso ~1.6e4.", **zh)
    add("zhang2006_fig16_runout_40kN_amp0p125.csv",
        "Zhang2006 fig16 runout 40kN", 0.125, 40000, 62,
        "BENCHMARK NULO (abaixo do limiar: 0.989->0.940, theta~0).", **zh)

    # =====================================================================
    # Rodada 5 (BAS_V2_papers/F, 2026-07-16; ingestao 2026-07-17, fatia 7 do
    # plano L1-L7). Zhang 2018 (Wear, exp+FE basico) + Zhang 2019 (EFA,
    # companion exp+FE validado) = par thread-flank-fretting-wear (alvo do
    # gate L1: perda de preload SEM rotacao de porca, via desgaste de flanco
    # de rosca). Liu 2020 (Wear) = varredura preload x amplitude x
    # revestimento (zinc/DLC), a curva mais limpa da biblioteca p/
    # d(afrouxamento)/d(amplitude) (confound-free). So curvas EXPERIMENTAIS
    # de afrouxamento (F/F0 ou R_F% vs ciclo) sao wiradas — excluidos:
    # perfis de desgaste (fig6/12 zhang19), desgaste-por-ciclo-vs-angulo
    # (fig19 zhang18, snapshot do 3o ciclo so), checkpoints exatos de tabela
    # (table1/table2 zhang18/19 — usados so p/ validar a digitalizacao, nao
    # wirados como caso, mesmo criterio de curve_library/apparatus_notes) e
    # zhang19 fig16 (Stage-II REBASADA no proprio onset — eixo x com
    # convencao diferente de todas as outras curvas do paper, "cycle_since_
    # stageII_onset" nao "cycle"; redundante com fig4, que ja cobre o
    # mesmo grupo de ensaios do inicio ao fim). Ver
    # apparatus_notes/{zhang,liu2020}.md (nesta mesma pasta F).
    # =====================================================================
    _R5 = "BAS_V2_papers/F. Rodada 5 (limitacoes 2026-07-16)/digitized_csv"

    # --- Zhang 2018 Wear (Paper A) — M12x1.75x100 cl.10.9 35CrMo, transv ---
    # pct_yield: ISO 898-1 cl.10.9 Sy~=940 MPa (assumed/handbook) + As=84.3
    # mm2 M12x1.75 (mesmo valor paper-stated do Liu2020, mesma rosca).
    z18 = dict(source=S.ZHANG_2018, doi="10.1016/j.wear.2017.10.006",
               reference="Zhang, Lu, Wang & Zeng (2018). Wear 394-395:30-39",
               bolt_size="M12x1.75", d=12.0, p=1.75, freq=10.0, csv_dir=_R5,
               mu=0.20,
               note_common="Porca prevailing-torque (nylon insert); disp "
                           "0.25mm fixa (sem sweep, unico valor do paper); "
                           "mu~=0.20 (DIN946 back-calc, thread~bearing). ZERO "
                           "rotacao medida (perda de preload via desgaste de "
                           "flanco de rosca, nao afrouxamento rotacional). "
                           "pct_yield via ISO898-1 cl.10.9 Sy~940MPa (assumed) "
                           "+ As=84.3mm2. Ver apparatus_notes/zhang.md.")
    for n, f0kn, pct, csvn in [
            (1, 20, 25, "zhang18_fig2_test1_20kN_1e3cyc_preload_vs_cycles.csv"),
            (2, 20, 25, "zhang18_fig2_test2_20kN_1e4cyc_preload_vs_cycles.csv"),
            (3, 20, 25, "zhang18_fig2_test3_20kN_1e5cyc_preload_vs_cycles.csv"),
            (4, 20, 25, "zhang18_fig2_test4_20kN_5e5cyc_preload_vs_cycles.csv")]:
        add(csvn, f"Zhang2018 M12 test{n} 20kN", 0.25, f0kn * 1000, pct,
            "Ensaio interrompido (Fig.2); repeticao independente @20kN, "
            "terminada em contagem de ciclos propria (nao um trim da mesma curva).",
            **z18)
    for f0kn, pct, csvn in [(14, 18, "zhang18_fig13_14kN_preload_vs_cycles.csv"),
                            (20, 25, "zhang18_fig13_20kN_preload_vs_cycles.csv"),
                            (26, 33, "zhang18_fig13_26kN_preload_vs_cycles.csv")]:
        add(csvn, f"Zhang2018 M12 P0={f0kn}kN", 0.25, f0kn * 1000, pct,
            "Media de 3 repeticoes (Fig.13); preload sweep 14/20/26kN.", **z18)
    for lk, csvn in [("with", "zhang18_fig16_with_locker_preload_vs_cycles.csv"),
                     ("without", "zhang18_fig16_without_locker_preload_vs_cycles.csv")]:
        add(csvn, f"Zhang2018 M12 locker {lk} @20kN", 0.25, 20000, 25,
            ("3M TL43 thread locker — separa os flancos, previne slip relativo "
             "(so diverge de 'without' no Stage II, desgaste)." if lk == "with"
             else "Sem locker; mesmo ensaio subjacente de fig13_20kN "
                  "(redigitalizado independente, cross-check ~0.1pp)."),
            **z18)

    # --- Zhang 2019 EFA (Paper B) — M12x1.75x100 SCM435, transv, 10kN so --
    # pct_yield=13.5% e' o proprio valor do paper (10kN = 95MPa = 13.5% Sy),
    # nao recalculado (Sy=705MPa medido, Tab.2 do paper).
    z19 = dict(source=S.ZHANG_2019, doi="10.1016/j.engfailanal.2019.05.001",
               reference="Zhang, Zeng, Lu, Zhang, Wang & Xu (2019). Eng. Fail. Anal. 104:341-353",
               bolt_size="M12x1.75", d=12.0, p=1.75, freq=10.0, csv_dir=_R5,
               mu=0.241,
               note_common="Porca hex plana (sem locking); disp 0.2mm fixa; "
                           "P0=10kN so no paper todo (=13.5% Sy, LOW deliberado "
                           "p/ perfil de desgaste visivel); mu=0.241 medio "
                           "(DIN946, Tab.2, faixa 0.228-0.251). ZERO rotacao "
                           "medida (sensor 0.045 graus) — confirmacao mais "
                           "limpa (porca sem trava) do mesmo mecanismo do "
                           "Zhang2018. Companion validado (mesmo grupo/par "
                           "35CrMo~SCM435). Ver apparatus_notes/zhang.md.")
    for grp, csvn in [("1e3cyc Test1-3", "zhang19_fig4_1e3cyc_Test1to3_preload_vs_cycles.csv"),
                      ("1e4cyc Test4-6", "zhang19_fig4_1e4cyc_Test4to6_preload_vs_cycles.csv"),
                      ("1e5cyc Test7-9", "zhang19_fig4_1e5cyc_Test7to9_preload_vs_cycles.csv"),
                      ("2e5cyc Test10-12", "zhang19_fig4_2e5cyc_Test10to12_preload_vs_cycles.csv")]:
        add(csvn, f"Zhang2019 M12 {grp}", 0.2, 10000, 13.5,
            "Grupo de 3 ensaios interrompidos (Fig.4); curva completa Estagio I+II.",
            **z19)

    # --- Liu 2020 Wear — M12x1.75 1045 steel, transv 5Hz, zinc vs DLC ------
    # y = R_F (retencao de preload) em PERCENTUAL (0-100, ancora 0,100.0) ->
    # y_scale=0.01 converte p/ fracao F/F0 no proprio loader (Rodada 5).
    # pct_yield: Sy=355MPa + As=84.3mm2, ambos paper-stated (Tabela 2).
    l20 = dict(source=S.LIU_2020_WEAR, doi="10.1016/j.wear.2020.203453",
               reference="Liu, Mi, Hu, Long, Cai, Peng & Zhu (2020). Wear 460-461:203453",
               bolt_size="M12x1.75", d=12.0, p=1.75, freq=5.0, csv_dir=_R5,
               y_scale=0.01,
               note_common="Disp-controlled (delta_amp); N=2e4 fixo p/ todo "
                           "ensaio; 6 rollers isolam a friccao placa-placa "
                           "(mecanismo do parafuso isolado); sem locking. "
                           "pct_yield via Sy=355MPa + As=84.3mm2 (Tab.2, "
                           "paper-stated). Ver apparatus_notes/liu2020.md.")
    for f0kn, pct, csvn in [(12, 40, "liu2020_fig5b_zinc_P0-12kN_AF0.2mm.csv"),
                            (18, 60, "liu2020_fig5b_zinc_P0-18kN_AF0.2mm.csv"),
                            (24, 80, "liu2020_fig5b_zinc_P0-24kN_AF0.2mm.csv")]:
        add(csvn, f"Liu2020 zinc P0={f0kn}kN", 0.2, f0kn * 1000, pct,
            "Preload sweep @A_F=0.2mm fixo (Fig.5b); zinco = revestimento "
            "baseline (mu_thread=0.150, Tab.2).",
            **dict(l20, mu=0.150, lubricated=False))
    for amp, csvn in [(0.1, "liu2020_fig9_zinc_AF0.1mm_P0-18kN.csv"),
                      (0.2, "liu2020_fig9_zinc_AF0.2mm_P0-18kN.csv"),
                      (0.3, "liu2020_fig9_zinc_AF0.3mm_P0-18kN.csv"),
                      (0.4, "liu2020_fig9_zinc_AF0.4mm_P0-18kN.csv")]:
        add(csvn, f"Liu2020 zinc {amp:g}mm @18kN", amp, 18000, 60,
            ("Amplitude sweep @P0=18kN fixo (Fig.9), curva-chave p/ "
             "d(afrouxamento)/d(amplitude) (super-linear medido, ~A_F^1.5). "
             + ("Regime muda p/ trinca de fadiga na raiz de rosca ~1e4 cyc "
                "(cauda NAO e' wear puro, ver notas)." if amp == 0.4 else "")).strip(),
            **dict(l20, mu=0.150, lubricated=False))
    add("liu2020_fig15_DLC_P0-18kN_AF0.2mm.csv", "Liu2020 DLC P0=18kN", 0.2, 18000, 60,
        "Revestimento DLC (mu_thread=0.126, Tab.2) no mesmo P0 nominal do "
        "zinco @18kN (Fig.15) — contraste de par tribologico a geometria/rig "
        "identicos.",
        **dict(l20, mu=0.126, lubricated=True))
    add("liu2020_fig15_DLC_P0-19.28kN_AF0.2mm.csv", "Liu2020 DLC P0=19.28kN", 0.2, 19280, 64,
        "DLC no preload equivalente-tensao (Eqs.1-3, sec3.2.2 do paper) — "
        "mu_thread menor 'compra' ~7% mais preload na mesma tensao "
        "equivalente de raiz de rosca.",
        **dict(l20, mu=0.126, lubricated=True))

    return cases


DIGITIZED_CASES: List[ValidationCase] = _build_digitized_cases()


# =============================================================================
# VALIDATION CASE MANAGER
# =============================================================================

class ValidationCaseManager:
    """Manager for validation case studies."""

    # All predefined cases
    ALL_CASES = [
        JIANG_LOW_LOAD,
        JIANG_HIGH_LOAD,
        JUNKER_STANDARD,
        NASSAR_LOW_FRICTION,
        NASSAR_HIGH_FRICTION,
        YANG_HIGH_AMPLITUDE,
        YANG_LOW_AMPLITUDE,
        SEVERE_TRANSVERSE,
    ] + DIGITIZED_CASES

    @classmethod
    def get_all_cases(cls) -> List[ValidationCase]:
        """Get all validation cases."""
        return cls.ALL_CASES

    @classmethod
    def get_case_by_name(cls, name: str) -> Optional[ValidationCase]:
        """Get a case by name."""
        for case in cls.ALL_CASES:
            if case.name == name:
                return case
        return None

    @classmethod
    def get_cases_by_source(cls, source: ValidationSource) -> List[ValidationCase]:
        """Get all cases from a specific source."""
        return [c for c in cls.ALL_CASES if c.source == source]

    @classmethod
    def get_cases_by_bolt_size(cls, bolt_size: str) -> List[ValidationCase]:
        """Get all cases for a specific bolt size."""
        return [c for c in cls.ALL_CASES if c.bolt_size == bolt_size]

    @classmethod
    def get_case_names(cls) -> List[str]:
        """Get list of all case names."""
        return [c.name for c in cls.ALL_CASES]

    @classmethod
    def validate_result(cls, case: ValidationCase,
                       final_preload_ratio: float,
                       total_loosening_deg: float) -> Dict[str, Any]:
        """
        Validate simulation results against experimental data.

        Args:
            case: The validation case
            final_preload_ratio: Simulated final preload ratio
            total_loosening_deg: Simulated total loosening angle

        Returns:
            Dictionary with validation results
        """
        # Calculate errors
        preload_error_pct = abs(final_preload_ratio - case.expected_final_preload_ratio) / \
                           case.expected_final_preload_ratio * 100

        loosening_error_pct = abs(total_loosening_deg - case.expected_loosening_deg) / \
                             max(case.expected_loosening_deg, 0.1) * 100

        # Check if within tolerance
        preload_pass = preload_error_pct <= case.tolerance_percent
        loosening_pass = loosening_error_pct <= case.tolerance_percent * 2  # More lenient for angle

        overall_pass = preload_pass and loosening_pass

        return {
            "case_name": case.name,
            "source": case.source.value,

            # Expected
            "expected_preload_ratio": case.expected_final_preload_ratio,
            "expected_loosening_deg": case.expected_loosening_deg,

            # Simulated
            "simulated_preload_ratio": final_preload_ratio,
            "simulated_loosening_deg": total_loosening_deg,

            # Errors
            "preload_error_pct": preload_error_pct,
            "loosening_error_pct": loosening_error_pct,

            # Pass/Fail
            "preload_pass": preload_pass,
            "loosening_pass": loosening_pass,
            "overall_pass": overall_pass,

            "tolerance_pct": case.tolerance_percent,
        }

    @classmethod
    def get_experimental_curves(cls, case: ValidationCase) -> Dict[str, np.ndarray]:
        """
        Get experimental data as numpy arrays for plotting.

        Returns:
            Dictionary with 'cycles', 'preload_ratio', 'friction_coeff' arrays
        """
        data = case.experimental_data

        cycles = np.array([d.cycles for d in data])
        preload_ratio = np.array([d.preload_ratio for d in data])

        friction = []
        for d in data:
            if d.friction_coeff is not None:
                friction.append(d.friction_coeff)
            else:
                friction.append(np.nan)
        friction = np.array(friction)

        loosening = []
        for d in data:
            if d.loosening_angle_deg is not None:
                loosening.append(d.loosening_angle_deg)
            else:
                loosening.append(np.nan)
        loosening = np.array(loosening)

        return {
            "cycles": cycles,
            "preload_ratio": preload_ratio,
            "friction_coeff": friction,
            "loosening_angle_deg": loosening,
        }


# =============================================================================
# QUICK ACCESS FUNCTIONS
# =============================================================================

def get_validation_case(name: str) -> Optional[ValidationCase]:
    """Quick access to get a validation case by name."""
    return ValidationCaseManager.get_case_by_name(name)


def list_validation_cases() -> List[str]:
    """List all available validation case names."""
    return ValidationCaseManager.get_case_names()


def run_validation(case_name: str, results) -> Dict[str, Any]:
    """
    Run validation against a case.

    Args:
        case_name: Name of the validation case
        results: CoupledLooseningResult object

    Returns:
        Validation report dictionary
    """
    case = get_validation_case(case_name)
    if case is None:
        return {"error": f"Case '{case_name}' not found"}

    return ValidationCaseManager.validate_result(
        case,
        final_preload_ratio=results.final_preload_ratio,
        total_loosening_deg=results.total_loosening_deg
    )
