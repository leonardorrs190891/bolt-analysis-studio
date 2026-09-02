import re
"""
Documentation Tab for Bolt Analysis Studio v4.0
================================================

Comprehensive user guide and technical reference for all features,
equations, parameters, and workflows in the software.

Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QTreeWidget, QTreeWidgetItem, QSplitter, QTextBrowser,
    QFrame, QGroupBox, QPushButton, QComboBox, QLineEdit,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

import numpy as np

from bolt_analysis_studio.gui.theme import Theme


def _theme_html(html: str) -> str:
    """Resolve ``{{TOKEN}}`` placeholders in HTML with current Theme values.

    DOCUMENTATION strings use ``{{BASE}}``, ``{{BLUE}}``, etc. as
    theme-agnostic placeholders.  This function resolves them at display
    time so the correct colors appear regardless of active palette.
    """
    tokens = {
        "{{BASE}}": Theme.BASE,
        "{{MANTLE}}": Theme.MANTLE,
        "{{CRUST}}": Theme.CRUST,
        "{{SURFACE0}}": Theme.SURFACE0,
        "{{SURFACE1}}": Theme.SURFACE1,
        "{{SURFACE2}}": Theme.SURFACE2,
        "{{TEXT}}": Theme.TEXT,
        "{{SUBTEXT}}": Theme.SUBTEXT,
        "{{OVERLAY}}": Theme.OVERLAY,
        "{{BLUE}}": Theme.BLUE,
        "{{GREEN}}": Theme.GREEN,
        "{{RED}}": Theme.RED,
        "{{PEACH}}": Theme.PEACH,
        "{{YELLOW}}": Theme.YELLOW,
        "{{MAUVE}}": Theme.MAUVE,
        "{{TEAL}}": Theme.TEAL,
        "{{PINK}}": Theme.PINK,
        "{{SKY}}": Theme.SKY,
        "{{LAVENDER}}": Theme.LAVENDER,
        "{{BUTTON_TEXT}}": Theme.BUTTON_TEXT,
        "{{FONT_SIZE_MICRO}}": f"{Theme.FONT_SIZE_MICRO}pt",
        "{{FONT_SIZE_SMALL}}": f"{Theme.FONT_SIZE_SMALL}pt",
        "{{FONT_SIZE_LABEL}}": f"{Theme.FONT_SIZE_LABEL}pt",
        "{{FONT_SIZE_SUBHEADING}}": f"{Theme.FONT_SIZE_SUBHEADING}pt",
        "{{FONT_SIZE_HEADING}}": f"{Theme.FONT_SIZE_HEADING}pt",
        "{{FONT_SIZE_LARGE}}": f"{Theme.FONT_SIZE_LARGE}pt",
        "{{BORDER_RADIUS_SM}}": f"{Theme.BORDER_RADIUS_SM}px",
        "{{BORDER_RADIUS_MD}}": f"{Theme.BORDER_RADIUS_MD}px",
        "{{BORDER_RADIUS_LG}}": f"{Theme.BORDER_RADIUS_LG}px",
        "{{BORDER_RADIUS_XL}}": f"{Theme.BORDER_RADIUS_XL}px",
    }
    for placeholder, value in tokens.items():
        html = html.replace(placeholder, value)
    return html


# =============================================================================
# DOCUMENTATION CONTENT
# =============================================================================

DOCUMENTATION = {
    "overview": {
        "title": "1. Software Overview",
        "content": """
<h2>1. Bolt Analysis Studio Overview</h2>

<h3>1.1 Purpose</h3>
<p>The <b>Bolt Analysis Studio</b> is an engineering software for analyzing bolted joints
subject to vibration-induced loosening. The software implements physics-based models from:</p>
<ul>
    <li><b>Junker Model (1969)</b>: Transverse slip loosening mechanism</li>
    <li><b>Jiang Model (2003)</b>: Two-stage loosening (S-curve)</li>
    <li><b>VDI 2230 (2015)</b>: German standard for bolted joint calculations</li>
    <li><b>Hintikka et al. (2020)</b>: Three-phase friction evolution</li>
</ul>

<h3>1.2 Four-Layer Architecture</h3>
<pre style="background-color: {{BASE}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
┌─────────────────────────────────────────────────────────────┐
│  GUI Layer (PyQt6)                                          │
│  - Main Window with 7 tabs                                  │
│  - MSD Builder for visual model construction                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  Visualization Layer                                         │
│  - 16 plot types for loosening analysis                     │
│  - Similitude and comparison charts                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  Numerical Layer                                             │
│  - Preload loss models                                      │
│  - Time integrators (Newmark, HHT, RK4)                     │
│  - Coupled loosening analyzer                               │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  Data Layer                                                  │
│  - MSD models (Mass-Spring-Damper)                          │
│  - ASTM/ISO material database                               │
│  - Contact and tribology system                             │
└─────────────────────────────────────────────────────────────┘
</pre>

<h3>1.3 Main Workflow</h3>
<ol>
    <li><b>Create Project</b>: Define metadata and standards</li>
    <li><b>Build MSD Model</b>: Add elements (head, shank, thread, nut, flange)</li>
    <li><b>Configure Loading</b>: Preload, transverse force, cycles</li>
    <li><b>Run Analysis</b>: Solver computes loosening cycle-by-cycle</li>
    <li><b>Visualize Results</b>: Time evolution plots</li>
    <li><b>Generate Report</b>: Export results and conclusions</li>
</ol>
"""
    },

    "msd_model": {
        "title": "2. MSD Model (Mass-Spring-Damper)",
        "content": """
<h2>2. MSD Model (Mass-Spring-Damper)</h2>

<h3>2.1 Fundamental Concept</h3>
<p>The bolted system is modeled as a set of masses connected by springs and dampers.
The equation of motion is:</p>

<div style="background-color: {{SURFACE0}}; padding: 15px; border-radius: {{BORDER_RADIUS_LG}}; text-align: center;">
<b>[M]{ẍ} + [C]{ẋ} + [K]{x} = {F(t)}</b>
</div>

<p>Where:</p>
<ul>
    <li><b>[M]</b> - Mass matrix [kg]</li>
    <li><b>[C]</b> - Damping matrix [N·s/m]</li>
    <li><b>[K]</b> - Stiffness matrix [N/m]</li>
    <li><b>{x}</b> - Displacement vector [m]</li>
    <li><b>{F(t)}</b> - External force vector [N]</li>
</ul>

<h3>2.2 Element Types</h3>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Element</th>
    <th>Description</th>
    <th>Typical Stiffness</th>
    <th>Required?</th>
</tr>
<tr>
    <td><b>HEAD</b></td>
    <td>Bolt head (hexagonal)</td>
    <td>k = 0.5 × E × d</td>
    <td>Yes</td>
</tr>
<tr>
    <td><b>SHANK</b></td>
    <td>Unthreaded shank</td>
    <td>k = E × A / L</td>
    <td>Optional</td>
</tr>
<tr>
    <td><b>THREAD</b></td>
    <td>Threaded portion</td>
    <td>k = E × A_s / L_t</td>
    <td>Yes</td>
</tr>
<tr>
    <td><b>NUT</b></td>
    <td>Hex nut</td>
    <td>k based on engaged threads</td>
    <td>Yes</td>
</tr>
<tr>
    <td><b>WASHER</b></td>
    <td>Washer (flat, spring, Nord-Lock)</td>
    <td>k = E × A / t</td>
    <td>Optional</td>
</tr>
<tr>
    <td><b>FLANGE</b></td>
    <td>Flange or clamped member</td>
    <td>Rotscher cone / Wileman</td>
    <td>Yes (at least 1)</td>
</tr>
<tr>
    <td><b>GASKET</b></td>
    <td>Sealing gasket</td>
    <td>Nonlinear k(δ)</td>
    <td>Optional</td>
</tr>
<tr>
    <td><b>GROUND</b></td>
    <td>Fixed boundary condition</td>
    <td>Rigid (infinite)</td>
    <td>Yes (exactly 1)</td>
</tr>
</table>

<h3 style="color: {{BLUE}};">2.3 Building a Valid Model — Step by Step</h3>

<p>Follow these steps in the <b>MSD Builder</b> (Tab 2) to create a model that
passes all validation checks.</p>

<div style="background-color: {{SURFACE0}}; padding: 15px; border-radius: {{BORDER_RADIUS_XL}}; margin: 10px 0;">
<p style="color: {{GREEN}}; font-weight: bold; font-size: {{FONT_SIZE_HEADING}};">Step 1 — Add a GROUND Element</p>
<p>Every model needs exactly <b>one GROUND</b> element. It provides the fixed
boundary condition (zero displacement DOF). Drag it from the palette and
place it at the bottom of the chain.</p>
<p style="color: {{YELLOW}};"><b>Validation rule:</b> Model must contain at least one GROUND element.</p>
</div>

<div style="background-color: {{SURFACE0}}; padding: 15px; border-radius: {{BORDER_RADIUS_XL}}; margin: 10px 0;">
<p style="color: {{GREEN}}; font-weight: bold; font-size: {{FONT_SIZE_HEADING}};">Step 2 — Add Bolt Components (HEAD → SHANK/THREAD → NUT)</p>
<p>Build the bolt from top to bottom:</p>
<ol>
    <li><b>HEAD</b> — Bolt head, first element in the load path</li>
    <li><b>SHANK</b> (optional) — Unthreaded portion. Omit for short bolts.</li>
    <li><b>THREAD</b> — Threaded section of the bolt</li>
    <li><b>NUT</b> — Must appear after THREAD in the chain</li>
</ol>
<p style="color: {{YELLOW}};"><b>Validation rule:</b> Model must contain at least 2 non-ground elements to
form a system of equations.</p>
</div>

<div style="background-color: {{SURFACE0}}; padding: 15px; border-radius: {{BORDER_RADIUS_XL}}; margin: 10px 0;">
<p style="color: {{GREEN}}; font-weight: bold; font-size: {{FONT_SIZE_HEADING}};">Step 3 — Add Clamped Members (FLANGE)</p>
<p>Add at least one <b>FLANGE</b> element for the clamped member(s).
For a gasketed joint, add a <b>GASKET</b> between the two flanges.</p>
<p>Typical arrangement:<br>
<code>HEAD → WASHER → FLANGE → FLANGE → WASHER → NUT → GROUND</code></p>
<p>Or with gasket:<br>
<code>HEAD → FLANGE → GASKET → FLANGE → NUT → GROUND</code></p>
</div>

<div style="background-color: {{SURFACE0}}; padding: 15px; border-radius: {{BORDER_RADIUS_XL}}; margin: 10px 0;">
<p style="color: {{GREEN}}; font-weight: bold; font-size: {{FONT_SIZE_HEADING}};">Step 4 — Set Element Properties</p>
<p>Click each element and set <b>k</b> (stiffness), <b>c</b> (damping), and
<b>m</b> (mass) in the Property Inspector panel on the right.</p>
<ul>
    <li><b>Stiffness (k)</b>: Must be &gt; 0 for all elements. The solver needs a
        positive-definite stiffness matrix.</li>
    <li><b>Mass (m)</b>: Must be &gt; 0 for at least one element.</li>
    <li><b>Damping (c)</b>: Can be 0 (undamped) or a positive value.</li>
</ul>
<p style="color: {{RED}};"><b>Common error:</b> Leaving k = 0 causes a singular stiffness matrix.
The solver will fail with "singular matrix" error.</p>
</div>

<div style="background-color: {{SURFACE0}}; padding: 15px; border-radius: {{BORDER_RADIUS_XL}}; margin: 10px 0;">
<p style="color: {{GREEN}}; font-weight: bold; font-size: {{FONT_SIZE_HEADING}};">Step 5 — Configure Loading Parameters</p>
<p>In the <b>Loading</b> section of the Property Inspector:</p>
<ol>
    <li>Select the <b>Load Type</b> (Transverse for Junker loosening)</li>
    <li>Set <b>Bolt Diameter</b> and <b>Pitch</b> — stiffnesses and preload are auto-computed from ISO 68-1 geometry</li>
    <li>Adjust the <b>% Yield slider</b> — preload is: F = (%/100) × A_s × σ_y</li>
    <li>Set <b>Frequency</b> and <b>Number of Cycles</b></li>
    <li>Check <b>Lubricated</b> if applicable (affects μ evolution)</li>
</ol>
<p style="color: {{YELLOW}};"><b>Tip:</b> The preload is the single source of truth. It is passed to the solver
automatically — you do not need to set it again in the Solver Tab.</p>
</div>

<div style="background-color: {{SURFACE0}}; padding: 15px; border-radius: {{BORDER_RADIUS_XL}}; margin: 10px 0;">
<p style="color: {{GREEN}}; font-weight: bold; font-size: {{FONT_SIZE_HEADING}};">Step 6 — Validate the Model</p>
<p>Click <b>Validate</b> in the toolbar (or press the button at the bottom).
The validator checks:</p>
<table border="1" style="border-collapse: collapse; width: 100%; margin-top: 8px;">
<tr style="background-color: {{SURFACE1}};">
    <th>Check</th>
    <th>Status</th>
    <th>How to Fix</th>
</tr>
<tr>
    <td>At least 2 elements</td>
    <td style="color: {{RED}};"><b>ERROR</b> if missing</td>
    <td>Add more elements from the palette</td>
</tr>
<tr>
    <td>At least 1 GROUND</td>
    <td style="color: {{RED}};"><b>ERROR</b> if missing</td>
    <td>Drag a GROUND element to the chain</td>
</tr>
<tr>
    <td>All k > 0</td>
    <td style="color: {{RED}};"><b>ERROR</b> if any k = 0</td>
    <td>Set stiffness in the Property Inspector</td>
</tr>
<tr>
    <td>At least 1 mass > 0</td>
    <td style="color: {{YELLOW}};"><b>WARNING</b> if all m = 0</td>
    <td>Assign mass to at least one element</td>
</tr>
<tr>
    <td>ThreadContact for each NUT</td>
    <td style="color: {{BLUE}};"><b>OK / INFO</b></td>
    <td>Optional — only needed for contact analysis</td>
</tr>
</table>
</div>

<h3>2.4 Bolt Stiffness Calculation</h3>

<p>The software computes bolt and member stiffnesses automatically from the bolt
geometry using three published models:</p>

<p><b>VDI 2230 — Thread Stiffness:</b></p>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
k_thread = E × A_s / L_engaged
<br><br>
where A_s = (π/4) × ((d₂ + d₃)/2)² is the ISO 68-1 tensile stress area,
<br>d₂ = d − 0.6495 × p (pitch diameter), d₃ = d − 1.2268 × p (minor diameter)
</div>

<p><b>VDI 2230 — Overall Bolt Stiffness (series model):</b></p>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
1/k_bolt = 1/k_head + 1/k_shank + 1/k_free_thread + 1/k_engaged_thread
<br><br>
k_head = 0.5 × E × d
<br>k_shank = E × A / L_shank
<br>k_free = E × A_s / L_free
<br>k_engaged = E × A_s / (0.5 × L_engaged)
</div>

<p><b>Motosh (1976) — Empirical Thread Stiffness:</b></p>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
k_thread = 0.5 × E × d × n_threads
</div>

<p><b>Wileman et al. (1991) — Member Stiffness:</b></p>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
k_member = E × d × A_w × exp(B_w × d / L_clamp)
<br><br>
Steel-on-steel: A_w = 0.78715, B_w = 0.62873
</div>

<h3>2.5 Rotscher Cone (Alternative Member Stiffness)</h3>
<p>For detailed analysis, the clamped member stiffness can be calculated via the
cone-shaped stress distribution model:</p>

<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
k_member = (E × π × d × tan(α)) / ln((D_w + d)(D_w − d + L×tan(α)) / ((D_w − d)(D_w + d + L×tan(α))))
</div>

<p>Where:</p>
<ul>
    <li><b>α</b> = 30° to 45° (cone half-angle)</li>
    <li><b>D_w</b> = under-head bearing diameter</li>
    <li><b>L</b> = grip length (clamping length)</li>
</ul>

<h3>2.6 Stiffness Ratio (Φ)</h3>
<p>The stiffness ratio determines how much of the external load is felt by the bolt:</p>

<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<b>Φ = k_bolt / (k_bolt + k_member)</b>
</div>

<p>Typical values: Φ = 0.1 to 0.3 for stiff joints. Lower Φ means the members
absorb more of the external load, which is generally desired.</p>

<h3>2.7 Preload Calculation</h3>
<p>The preload is computed automatically from the <b>% yield slider</b>:</p>

<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<b>F_preload = (% yield / 100) × A_s × σ_y</b>
<br><br>
Default σ_y = 720 MPa (A193 B7 / ISO 898-1 class 10.9)
</div>

<p><b>Example for M16 × 2.0 at 70% yield:</b></p>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
d₂ = 16.0 − 0.6495 × 2.0 = 14.701 mm
<br>d₃ = 16.0 − 1.2268 × 2.0 = 13.546 mm
<br>A_s = (π/4) × ((14.701 + 13.546)/2)² = 156.7 mm²
<br><b>F = 0.70 × 156.7 × 720 = 78,962 N ≈ 79 kN</b>
</div>

<h3 style="color: {{RED}};">2.8 Common Mistakes and How to Fix Them</h3>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Symptom</th>
    <th>Cause</th>
    <th>Fix</th>
</tr>
<tr>
    <td>"Singular matrix" in solver</td>
    <td>An element has k = 0</td>
    <td>Set a positive stiffness for every element</td>
</tr>
<tr>
    <td>"No GROUND element"</td>
    <td>Missing boundary condition</td>
    <td>Add a GROUND element at the end of the chain</td>
</tr>
<tr>
    <td>Zero natural frequency</td>
    <td>All masses are zero</td>
    <td>Assign realistic mass to at least one element</td>
</tr>
<tr>
    <td>Solver diverges / NaN</td>
    <td>Time step too large</td>
    <td>Reduce dt to &lt; 1/(20 × f_max). Use automatic timestep suggestion.</td>
</tr>
<tr>
    <td>No loosening observed</td>
    <td>Transverse force too low or μ too high</td>
    <td>Increase transverse displacement or reduce friction coefficient</td>
</tr>
<tr>
    <td>Preload = 0</td>
    <td>% yield slider at 0</td>
    <td>Set slider to 60–80% yield range</td>
</tr>
</table>
"""
    },

    "contact_system": {
        "title": "3. Contact System",
        "content": """
<h2>3. Contact System and Tribology</h2>

<h3>3.1 Contact Hierarchy</h3>
<p>The contact system is organized in three layers:</p>

<pre style="background-color: {{BASE}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
Layer 1: COMPONENTS (no tribology)
    ├── Head, Shank, Thread, Nut, Flange...
    └── Only mechanical properties (m, k, c)

Layer 2: CONTACTS (mechanical interfaces)
    ├── ThreadContact (thread-nut)
    ├── BearingContact (head-washer, nut-washer)
    ├── WasherContact (washer-flange)
    └── FlangeContact (flange-flange or flange-gasket)

Layer 3: TRIBOLOGY (only at contacts)
    ├── Friction Models
    ├── Wear Models
    └── Lubrication Models
</pre>

<h3>3.2 ThreadContact (Thread-Nut Contact)</h3>
<p>The thread contact is modeled as a <b>parallel array</b> of MSD elements,
one for each engaged thread:</p>

<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<b>Per-thread stiffness:</b> k_i = φ_i × k_thread_total
<br><br>
<b>Helix coupling:</b> [K] includes off-diagonal terms
<br>
k_axial_torsional = k × (p / 2π)
</div>

<h4>Thread Load Distribution Models:</h4>
<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Model</th>
    <th>Formula</th>
    <th>Use</th>
</tr>
<tr>
    <td>Equal</td>
    <td>φᵢ = 1/n</td>
    <td>Idealized</td>
</tr>
<tr>
    <td>Linear</td>
    <td>φᵢ = 2(n-i+1)/(n(n+1))</td>
    <td>Conservative</td>
</tr>
<tr>
    <td>Power Law</td>
    <td>φᵢ = (n-i+1)^β / Σ(j^β)</td>
    <td>Realistic</td>
</tr>
<tr>
    <td>Yamamoto</td>
    <td>φᵢ = sinh(...)/Σsinh(...)</td>
    <td>High accuracy</td>
</tr>
</table>

<h3>3.3 Thread Geometry</h3>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Parameter</th>
    <th>Symbol</th>
    <th>Formula (Metric)</th>
</tr>
<tr>
    <td>Pitch</td>
    <td>p</td>
    <td>Tabulated (e.g., M16 → p=2mm)</td>
</tr>
<tr>
    <td>Major diameter</td>
    <td>d</td>
    <td>Nominal (e.g., 16mm)</td>
</tr>
<tr>
    <td>Pitch diameter</td>
    <td>d₂</td>
    <td>d₂ = d - 0.6495×p</td>
</tr>
<tr>
    <td>Minor diameter</td>
    <td>d₃</td>
    <td>d₃ = d - 1.2268×p</td>
</tr>
<tr>
    <td>Helix angle</td>
    <td>λ</td>
    <td>λ = arctan(p / (π×d₂))</td>
</tr>
<tr>
    <td>Flank angle</td>
    <td>α</td>
    <td>60° (30° each side) for metric</td>
</tr>
</table>

<h3>3.4 Matrix Contributions</h3>

<p><b>Matrix [K] - Stiffness:</b></p>
<ul>
    <li>Thread: k_thread at (stud, nut) positions + helix coupling</li>
    <li>Bearing: k_contact at (head/nut, washer/flange) positions</li>
    <li>Gasket: k_tangent(δ) nonlinear</li>
</ul>

<p><b>Matrix [C] - Damping:</b></p>
<ul>
    <li>Material: c = 2ζ√(km)</li>
    <li>Viscous: c_visc at rotational DOFs</li>
    <li>Rayleigh: [C] = α[M] + β[K]</li>
</ul>

<p><b>Vector {F} - Forces (where tribology enters!):</b></p>
<ul>
    <li>Thread friction: T_thread = μ_t × F_p × d₂ / (2×cos(α))</li>
    <li>Bearing friction: T_bearing = μ_b × F_p × r_eff</li>
    <li>Helix torque: T_helix = F_p × r × tan(λ) → <b>CAUSES LOOSENING</b></li>
</ul>
"""
    },

    "friction_model": {
        "title": "4. Friction Evolution Model",
        "content": """
<h2>4. Three-Phase Friction Evolution Model</h2>

<h3>4.1 Overview</h3>
<p>The friction coefficient is <b>not constant</b> - it evolves over cycles
following a three-phase model based on Hintikka et al. (2020):</p>

<div style="background-color: {{SURFACE0}}; padding: 15px; border-radius: {{BORDER_RADIUS_LG}}; text-align: center;">
<b>μ(N) = μ_initial + Δμ₁(N) + Δμ₂(N)</b>
</div>

<h3>4.2 Evolution Phases</h3>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Phase</th>
    <th>Cycles</th>
    <th>Behavior</th>
    <th>Physical Cause</th>
</tr>
<tr>
    <td><b>1. Running-in</b></td>
    <td>0 - N₁ (~50)</td>
    <td>μ rises to μ_peak</td>
    <td>Asperity removal, real area increase</td>
</tr>
<tr>
    <td><b>2. Transition</b></td>
    <td>N₁ - N₂ (~200)</td>
    <td>μ falls from peak</td>
    <td>Surface polishing</td>
</tr>
<tr>
    <td><b>3. Steady State</b></td>
    <td>N₂ - N₃ (~2000+)</td>
    <td>μ → μ_steady</td>
    <td>Wear/oxide formation equilibrium</td>
</tr>
</table>

<h3>4.3 Complete Equation</h3>

<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<pre>
μ(N) = μ_initial
       + (μ_peak - μ_initial) × (1 - e^(-N/N₁)) × e^(-N/N₂)    [Term 1: peak]
       + (μ_steady - μ_initial) × (1 - e^(-N/N₃))              [Term 2: steady]
       - k_wear × h_wear                                        [Wear degradation]
       - k_temp × (T - 20°C)                                    [Temperature effect]
</pre>
</div>

<h3>4.4 Typical Parameters</h3>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Parameter</th>
    <th>Lubricated</th>
    <th>Dry</th>
    <th>Unit</th>
</tr>
<tr>
    <td>μ_initial</td>
    <td>0.10 - 0.15</td>
    <td>0.15 - 0.25</td>
    <td>-</td>
</tr>
<tr>
    <td>μ_peak</td>
    <td>μ_initial × 1.1</td>
    <td>μ_initial × 1.3</td>
    <td>-</td>
</tr>
<tr>
    <td>μ_steady</td>
    <td>μ_initial × 0.7</td>
    <td>μ_initial × 0.8</td>
    <td>-</td>
</tr>
<tr>
    <td>μ_minimum</td>
    <td>0.03</td>
    <td>0.05</td>
    <td>-</td>
</tr>
<tr>
    <td>N₁</td>
    <td>100</td>
    <td>50</td>
    <td>cycles</td>
</tr>
<tr>
    <td>N₂</td>
    <td>500</td>
    <td>200</td>
    <td>cycles</td>
</tr>
<tr>
    <td>N₃</td>
    <td>5000</td>
    <td>2000</td>
    <td>cycles</td>
</tr>
</table>

<h3>4.5 Critical Friction</h3>
<p>The critical friction coefficient is the threshold below which loosening occurs
even without external transverse force:</p>

<div style="background-color: {{SURFACE0}}; padding: 15px; border-radius: {{BORDER_RADIUS_LG}}; text-align: center;">
<b>μ_critical = (p / 2π) × (2 × cos(α)) / (d₂ + 2 × r_eff × cos(α))</b>
</div>

<p>For typical M16: μ_critical ≈ 0.017</p>

<p><b>If μ_current < μ_critical</b> → Loosening even without vibration!</p>

<h3>4.6 Friction Margin</h3>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<b>Margin = μ_average / μ_critical</b>
<br><br>
Margin > 1.5 → Safe<br>
Margin 1.0-1.5 → Moderate risk<br>
Margin < 1.0 → Active loosening!
</div>
"""
    },

    "wear_model": {
        "title": "5. Wear Model",
        "content": """
<h2>5. Time-Varying Wear Model</h2>

<h3>5.1 Archard Model</h3>
<p>Adhesive/abrasive wear is modeled by the Archard equation:</p>

<div style="background-color: {{SURFACE0}}; padding: 15px; border-radius: {{BORDER_RADIUS_LG}}; text-align: center;">
<b>V = K × F × s / H</b>
</div>

<p>Where:</p>
<ul>
    <li><b>V</b> = Worn volume [m³]</li>
    <li><b>K</b> = Dimensionless wear coefficient</li>
    <li><b>F</b> = Normal force (preload) [N]</li>
    <li><b>s</b> = Sliding distance [m]</li>
    <li><b>H</b> = Surface hardness [Pa]</li>
</ul>

<h3>5.2 Four-Phase K Coefficient Evolution</h3>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Phase</th>
    <th>Condition</th>
    <th>Typical K</th>
    <th>Description</th>
</tr>
<tr>
    <td><b>Running-in</b></td>
    <td>N < 100 cycles</td>
    <td>5×10⁻⁶</td>
    <td>High asperity removal</td>
</tr>
<tr>
    <td><b>Steady State</b></td>
    <td>N > 500, h < 50μm</td>
    <td>1×10⁻⁶</td>
    <td>Smooth wear, polished surface</td>
</tr>
<tr>
    <td><b>Severe</b></td>
    <td>h > 50μm</td>
    <td>1×10⁻⁵</td>
    <td>Surface damage, debris</td>
</tr>
<tr>
    <td><b>Catastrophic</b></td>
    <td>h > 100μm</td>
    <td>5×10⁻⁵</td>
    <td>Imminent failure</td>
</tr>
</table>

<h3>5.3 Energy-Based Model (Fouvry)</h3>
<p>Complementary to Archard, wear also depends on dissipated energy:</p>

<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<b>V = α × E_dissipated</b>
<br><br>
E_dissipated = μ × F × s  [Energy per cycle]
<br><br>
α = 5×10⁻¹¹ m³/J (typical for steel-steel)
</div>

<h3>5.4 Temperature Effect</h3>
<p>Hardness decreases with increasing temperature:</p>

<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
H_effective = H × max(0.3, 1 - 0.001 × (T - 20°C))
</div>

<p>Result: Wear increases at elevated temperatures.</p>

<h3>5.5 Fretting Regime</h3>
<p>For small slip amplitudes (< 50μm), fretting occurs:</p>
<ul>
    <li>Damage per cycle is <b>higher</b> than in gross-slip</li>
    <li>Intensification factor: 1.5× typical</li>
    <li>Oxidized debris generation (Fe₂O₃)</li>
</ul>

<h3>5.6 Preload Loss from Wear</h3>
<p>Wear causes preload loss by reducing the grip length:</p>

<div style="background-color: {{SURFACE0}}; padding: 15px; border-radius: {{BORDER_RADIUS_LG}}; text-align: center;">
<b>ΔF_wear = k_system × h_wear</b>
</div>

<p>Example: If h = 10μm and k_system = 10⁸ N/m → ΔF = 1000 N</p>

<h3>5.7 Recommended Parameters</h3>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Parameter</th>
    <th>Typical Value</th>
    <th>Unit</th>
</tr>
<tr>
    <td>K_archard (running-in)</td>
    <td>5×10⁻⁶</td>
    <td>-</td>
</tr>
<tr>
    <td>K_archard (steady)</td>
    <td>1×10⁻⁶</td>
    <td>-</td>
</tr>
<tr>
    <td>Hardness (steel)</td>
    <td>2-3 GPa</td>
    <td>Pa</td>
</tr>
<tr>
    <td>α_energy</td>
    <td>5×10⁻¹¹</td>
    <td>m³/J</td>
</tr>
<tr>
    <td>Severe threshold</td>
    <td>50</td>
    <td>μm</td>
</tr>
<tr>
    <td>Catastrophic threshold</td>
    <td>100</td>
    <td>μm</td>
</tr>
</table>
"""
    },

    "loosening_model": {
        "title": "6. Junker Loosening Model",
        "content": """
<h2>6. Junker Loosening Mechanism</h2>

<h3>6.1 The Phenomenon</h3>
<p>In 1969, Gerhard Junker demonstrated that bolts can loosen even without
axial vibrations, only with <b>transverse sliding</b>.</p>

<p><b>Loosening condition:</b></p>
<div style="background-color: {{SURFACE0}}; padding: 15px; border-radius: {{BORDER_RADIUS_LG}};">
1. Bearing surface slip: |F_trans| > μ_bearing × F_p
<br>
2. Thread surface slip: |F_trans| > μ_thread × F_p × cos(λ)
<br><br>
<b>If BOTH occur → Bolt rotation!</b>
</div>

<h3>6.2 Torque Balance</h3>
<p>Loosening occurs when pitch torque overcomes resistance:</p>

<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<b>Pitch Torque (CAUSES loosening):</b>
<br>
T_pitch = F_p × p / (2π)
<br><br>
<b>Thread Resistance:</b>
<br>
T_thread = μ_thread × F_p × d₂ / (2 × cos(α))
<br><br>
<b>Bearing Resistance:</b>
<br>
T_bearing = μ_bearing × F_p × r_eff
<br><br>
<b>Torque Margin:</b>
<br>
Margin = (T_thread + T_bearing) / T_pitch
<br><br>
If Margin < 1 → Loosening!
</div>

<h3>6.3 Two-Stage Model (Jiang 2003)</h3>
<p>Loosening follows a characteristic S-curve with two stages:</p>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Stage</th>
    <th>Cycles</th>
    <th>Mechanism</th>
    <th>Typical Loss</th>
</tr>
<tr>
    <td><b>I - Non-Rotational</b></td>
    <td>0 - ~200</td>
    <td>Plastic deformation at thread roots</td>
    <td>10-40%</td>
</tr>
<tr>
    <td><b>II - Rotational</b></td>
    <td>200+</td>
    <td>Junker mechanism (rotation)</td>
    <td>Gradual until failure</td>
</tr>
</table>

<h3>6.4 S-Curve Equation</h3>

<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<pre>
Stage I (plastic deformation):
ΔF₁ = δF₁_max × (1 - e^(-N/N₁))

Stage II (rotational):
ΔF₂ = k_stage2 × (N - N₁)  [for N > N₁]

Total:
F_p(N) = F_p0 × (1 - ΔF₁ - ΔF₂)
</pre>
</div>

<h3>6.5 Displacement Amplitude Effect</h3>
<p>Yang et al. (2019) showed amplitude significantly affects loosening:</p>

<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
Disp_factor = (disp / 0.65mm)^2
<br><br>
N₁_effective = N₁ / Disp_factor
<br>
Rate_stage2 × Disp_factor
</div>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Amplitude</th>
    <th>Risk</th>
    <th>Notes</th>
</tr>
<tr>
    <td>< 0.15 mm</td>
    <td>Minimal</td>
    <td>Embedding only</td>
</tr>
<tr>
    <td>0.15 - 0.3 mm</td>
    <td>Low</td>
    <td>Partial slip</td>
</tr>
<tr>
    <td>0.3 - 0.5 mm</td>
    <td>Moderate</td>
    <td>Occasional slip</td>
</tr>
<tr>
    <td>> 0.65 mm</td>
    <td>Severe</td>
    <td>Complete slip (DIN 65151 standard)</td>
</tr>
</table>

<h3>6.6 Loosening Phases</h3>
<p>The software classifies the state into 5 phases:</p>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Phase</th>
    <th>Criteria</th>
    <th>Recommended Action</th>
</tr>
<tr>
    <td style="color: {{GREEN}};">STABLE</td>
    <td>Margin > 1.3, < 2% loss</td>
    <td>Normal monitoring</td>
</tr>
<tr>
    <td style="color: {{BLUE}};">NON_ROTATIONAL</td>
    <td>Stage I, N < 200</td>
    <td>Expected, monitor</td>
</tr>
<tr>
    <td style="color: {{YELLOW}};">TRANSITION</td>
    <td>Margin eroding</td>
    <td>Increased attention</td>
</tr>
<tr>
    <td style="color: {{PEACH}};">ROTATIONAL</td>
    <td>Margin < 1, active rotation</td>
    <td>Intervention needed</td>
</tr>
<tr>
    <td style="color: {{RED}};">RUNAWAY</td>
    <td>> 50% loss or high rate</td>
    <td>Immediate shutdown!</td>
</tr>
</table>
"""
    },

    "solver_params": {
        "title": "7. Solver Parameters",
        "content": """
<h2>7. Solver Configuration</h2>

<h3>7.1 Coupled Loosening Analysis</h3>
<p>This is the main analysis of the software. It couples:</p>
<ul>
    <li>Friction evolution</li>
    <li>Wear accumulation</li>
    <li>Junker mechanism</li>
    <li>Preload loss</li>
</ul>

<h3>7.2 Main Input Parameters</h3>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Parameter</th>
    <th>Symbol</th>
    <th>Typical Range</th>
    <th>Effect</th>
</tr>
<tr>
    <td><b>Initial Preload</b></td>
    <td>F_p0</td>
    <td>50-70% F_yield</td>
    <td>Higher → more loosening resistance</td>
</tr>
<tr>
    <td><b>Transverse Force</b></td>
    <td>F_trans</td>
    <td>10-30% F_p0</td>
    <td>Higher → faster loosening</td>
</tr>
<tr>
    <td><b>Number of Cycles</b></td>
    <td>N</td>
    <td>1000 - 5×10⁶</td>
    <td>Analysis horizon</td>
</tr>
<tr>
    <td><b>Initial Friction</b></td>
    <td>μ_0</td>
    <td>0.08 - 0.20</td>
    <td>Lower → easier loosening</td>
</tr>
<tr>
    <td><b>Temperature</b></td>
    <td>T</td>
    <td>20 - 150°C</td>
    <td>Higher → lower friction and hardness</td>
</tr>
</table>

<h3>7.3 Bolt Geometry</h3>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Parameter</th>
    <th>Description</th>
    <th>Effect on Loosening</th>
</tr>
<tr>
    <td><b>Diameter (d)</b></td>
    <td>Nominal diameter</td>
    <td>Larger → higher load capacity</td>
</tr>
<tr>
    <td><b>Pitch (p)</b></td>
    <td>Thread pitch</td>
    <td>Smaller → more self-locking</td>
</tr>
<tr>
    <td><b>Grip Length</b></td>
    <td>Clamped length</td>
    <td>Longer → more flexible system</td>
</tr>
<tr>
    <td><b>Engaged Threads</b></td>
    <td>Threads in nut</td>
    <td>More → better load distribution</td>
</tr>
</table>

<h3>7.4 How to Choose Parameters</h3>

<h4>Preload:</h4>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<b>F_p0 = 0.7 × R_p0.2 × A_s</b>
<br><br>
Where:
<br>- R_p0.2 = bolt yield strength
<br>- A_s = thread stress area
<br><br>
Example M16-8.8: F_p0 = 0.7 × 640 × 157 = 70,336 N
</div>

<h4>Transverse Force:</h4>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
For Junker test (DIN 65151):
<br><b>F_trans = amplitude × k_transverse</b>
<br><br>
Standard amplitude: 0.65 mm
<br>
Typical F_trans: 5-15 kN for M16
</div>

<h4>Number of Cycles:</h4>
<ul>
    <li><b>Quick test:</b> 500-2000 cycles</li>
    <li><b>Full analysis:</b> 10,000-50,000 cycles</li>
    <li><b>Service life:</b> 100,000 - 5,000,000 cycles</li>
</ul>

<h3>7.5 MSD Model Integration</h3>
<p>When <b>"Use MSD Model"</b> is enabled, the solver automatically extracts:</p>
<ul>
    <li>Bolt geometry from THREAD/SHANK elements</li>
    <li>Preload from GlobalLoading</li>
    <li>Transverse force from GlobalLoading</li>
    <li>Stiffness from assembled [K] matrix</li>
    <li>Friction from defined contacts</li>
</ul>

<h3>7.6 Time Integrators</h3>
<p>For dynamic analysis (non-loosening):</p>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Method</th>
    <th>Type</th>
    <th>When to Use</th>
</tr>
<tr>
    <td>Newmark-β</td>
    <td>Implicit</td>
    <td>General purpose, stable</td>
</tr>
<tr>
    <td>HHT-α</td>
    <td>Implicit</td>
    <td>Numerical dissipation of high frequencies</td>
</tr>
<tr>
    <td>Central Diff</td>
    <td>Explicit</td>
    <td>Impact, very small dt</td>
</tr>
<tr>
    <td>Modal</td>
    <td>Superposition</td>
    <td>Large linear systems</td>
</tr>
<tr>
    <td>RK4</td>
    <td>Explicit</td>
    <td>High accuracy</td>
</tr>
</table>
"""
    },

    "plots_guide": {
        "title": "8. Plot Guide",
        "content": """
<h2>8. Plot Interpretation</h2>

<h3>8.1 Preload Evolution Plot</h3>
<p><b>Shows:</b> F_p/F_p0 vs Cycles</p>
<p><b>How to interpret:</b></p>
<ul>
    <li>Characteristic S-curve (Jiang model)</li>
    <li>Rapid initial drop = Stage I (embedding)</li>
    <li>Gradual drop = Stage II (rotation)</li>
    <li>Plateau = stable system</li>
</ul>
<p><b>Alert:</b> If crosses 50% → joint failure risk</p>

<h3>8.2 Friction Evolution Plot</h3>
<p><b>Shows:</b> μ_thread and μ_bearing vs Cycles</p>
<p><b>How to interpret:</b></p>
<ul>
    <li>Initial peak = running-in</li>
    <li>Drop = surface polishing</li>
    <li>Red line = μ_critical</li>
</ul>
<p><b>Alert:</b> If μ < μ_critical → certain loosening!</p>

<h3>8.3 Torque Margin Plot</h3>
<p><b>Shows:</b> T_resistance / T_pitch vs Cycles</p>
<p><b>How to interpret:</b></p>
<ul>
    <li>Margin > 1.5 → Safe (green)</li>
    <li>Margin 1.0-1.5 → Warning (yellow)</li>
    <li>Margin < 1.0 → Active loosening (red)</li>
</ul>

<h3>8.4 Wear Accumulation Plot</h3>
<p><b>Shows:</b> Wear depth [μm] vs Cycles</p>
<p><b>Regions:</b></p>
<ul>
    <li>0-50 μm: Steady state (green)</li>
    <li>50-100 μm: Severe wear (yellow)</li>
    <li>> 100 μm: Catastrophic (red)</li>
</ul>

<h3>8.5 Loosening Angle Plot</h3>
<p><b>Shows:</b> Accumulated rotation [°] vs Cycles</p>
<p><b>How to interpret:</b></p>
<ul>
    <li>Slope = loosening rate</li>
    <li>360° = one full turn (loss ~1 pitch)</li>
</ul>

<h3>8.6 Phase Diagram</h3>
<p><b>Shows:</b> Temporal state classification</p>
<p><b>Colors:</b></p>
<ul>
    <li style="color: {{GREEN}};">Green: STABLE</li>
    <li style="color: {{BLUE}};">Blue: NON_ROTATIONAL</li>
    <li style="color: {{YELLOW}};">Yellow: TRANSITION</li>
    <li style="color: {{PEACH}};">Orange: ROTATIONAL</li>
    <li style="color: {{RED}};">Red: RUNAWAY</li>
</ul>

<h3>8.7 Decomposed Preload Loss Plot</h3>
<p><b>Components:</b></p>
<ul>
    <li><b>Rotational:</b> k_bolt × (p/2π) × θ</li>
    <li><b>Wear:</b> k_system × h_wear</li>
    <li><b>Embedding:</b> S-curve Stage I model</li>
</ul>

<h3>8.8 Junker Map</h3>
<p><b>Shows:</b> Slip condition</p>
<p><b>Regions:</b></p>
<ul>
    <li>Stick: No slip</li>
    <li>Slip bearing only: Bearing surface slip</li>
    <li>Slip both: Both surfaces → <b>LOOSENING!</b></li>
</ul>

<h3>8.9 Model Comparison</h3>
<p>Compares different preload loss models:</p>
<ul>
    <li>Single exponential</li>
    <li>Double exponential</li>
    <li>Stretched exponential</li>
    <li>VDI 2230 embedding</li>
    <li>Coupled (physics-based)</li>
</ul>

<h3>8.10 Loosening Rate Plot</h3>
<p><b>Shows:</b> dθ/dN [°/cycle] vs Cycles</p>
<p><b>How to interpret:</b></p>
<ul>
    <li>Rate < 0.001°/cycle: Slow</li>
    <li>Rate 0.001-0.01°/cycle: Moderate</li>
    <li>Rate > 0.01°/cycle: Fast</li>
</ul>
"""
    },

    "workflow": {
        "title": "9. Step-by-Step Tutorial",
        "content": """
<h2>9. Tutorial: Complete Loosening Analysis</h2>

<h3>Step 1: Create New Project</h3>
<ol>
    <li>Open Bolt Analysis Studio</li>
    <li>Menu File → New Project (or Ctrl+N)</li>
    <li>In the <b>Project</b> tab, fill in:
        <ul>
            <li>Project name</li>
            <li>Description</li>
            <li>Standard (VDI 2230, ASME, etc.)</li>
        </ul>
    </li>
</ol>

<h3>Step 2: Build MSD Model</h3>
<ol>
    <li>Go to the <b>Model</b> tab</li>
    <li>From the left palette, drag elements:
        <ul>
            <li>HEAD → position 1</li>
            <li>SHANK → position 2</li>
            <li>THREAD → position 3</li>
            <li>NUT → position 4</li>
            <li>FLANGE → positions 5-6</li>
        </ul>
    </li>
    <li>Click each element to edit properties:
        <ul>
            <li>Geometry (diameter, length)</li>
            <li>Material (steel, aluminum)</li>
            <li>MSD (stiffness, damping, mass)</li>
        </ul>
    </li>
    <li>Click <b>Apply</b> to update the model</li>
</ol>

<h3>Step 3: Configure Loading</h3>
<ol>
    <li>In the global loading panel:
        <ul>
            <li><b>F_preload:</b> Initial preload (e.g., 50000 N)</li>
            <li><b>F_transverse:</b> Transverse force (e.g., 8000 N)</li>
            <li><b>n_cycles:</b> Number of cycles (e.g., 2000)</li>
        </ul>
    </li>
</ol>

<h3>Step 4: Configure Solver</h3>
<ol>
    <li>Go to the <b>Solver</b> tab</li>
    <li>Select analysis type: "Coupled Loosening"</li>
    <li>Configure parameters:
        <ul>
            <li>☑ Use MSD Model (recommended)</li>
            <li>☑ Lubricated (if applicable)</li>
            <li>Adjust initial friction if needed</li>
        </ul>
    </li>
</ol>

<h3>Step 5: Run Analysis</h3>
<ol>
    <li>Click <b>Run Analysis</b></li>
    <li>Monitor progress in the progress bar</li>
    <li>Watch logs in the bottom panel</li>
</ol>

<h3>Step 6: Analyze Results</h3>
<ol>
    <li>Go to the <b>Results</b> tab</li>
    <li>Examine the main plots:
        <ul>
            <li>Preload Ratio vs Cycles</li>
            <li>Friction Evolution</li>
            <li>Torque Margin</li>
            <li>Phase Diagram</li>
        </ul>
    </li>
    <li>Check the summary:
        <ul>
            <li>Final preload ratio</li>
            <li>Cycles to 50% loss</li>
            <li>Final phase</li>
        </ul>
    </li>
</ol>

<h3>Step 7: Adjust Design (if needed)</h3>
<p>If results indicate loosening risk:</p>
<ul>
    <li>Increase preload (if possible)</li>
    <li>Use locking washer (Nord-Lock)</li>
    <li>Increase friction (remove lubricant)</li>
    <li>Use finer pitch</li>
    <li>Add lock nut</li>
</ul>

<h3>Step 8: Generate Report</h3>
<ol>
    <li>Go to the <b>Reports</b> tab</li>
    <li>Select sections to include</li>
    <li>Click <b>Generate Report</b></li>
    <li>Export as PDF or HTML</li>
</ol>

<h3>Important Tips</h3>
<ul>
    <li>Always validate model before running (Validate button)</li>
    <li>For long analyses (>100k cycles), use sample_interval > 1</li>
    <li>Save project frequently (Ctrl+S)</li>
    <li>Use presets for standard bolts (M8, M10, M12, M16...)</li>
</ul>
"""
    },

    "equations_summary": {
        "title": "10. Equations Summary",
        "content": """
<h2>10. Main Equations Summary</h2>

<h3>10.1 Equation of Motion</h3>
<div style="background-color: {{SURFACE0}}; padding: 15px; border-radius: {{BORDER_RADIUS_LG}}; text-align: center; font-size: {{FONT_SIZE_LARGE}};">
<b>[M]{ẍ} + [C]{ẋ} + [K]{x} = {F(t)}</b>
</div>

<h3>10.2 System Stiffness</h3>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<b>Bolt (series):</b>
<br>1/k_bolt = 1/k_head + 1/k_shank + 1/k_thread
<br><br>
<b>System:</b>
<br>k_system = (k_bolt × k_member) / (k_bolt + k_member)
<br><br>
<b>Stiffness ratio:</b>
<br>Φ = k_bolt / (k_bolt + k_member)
</div>

<h3>10.3 Friction Evolution</h3>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
μ(N) = μ₀ + (μ_peak - μ₀)(1-e^(-N/N₁))e^(-N/N₂) + (μ_steady - μ₀)(1-e^(-N/N₃))
</div>

<h3>10.4 Critical Friction</h3>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
μ_crit = (p/2π) × 2cos(α) / (d₂ + 2×r_eff×cos(α))
</div>

<h3>10.5 Torque Balance</h3>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<b>Pitch torque:</b> T_pitch = F_p × p / (2π)
<br><br>
<b>Thread resistance:</b> T_thread = μ_t × F_p × d₂ / (2cos(α))
<br><br>
<b>Bearing resistance:</b> T_bearing = μ_b × F_p × r_eff
<br><br>
<b>Margin:</b> Margin = (T_thread + T_bearing) / T_pitch
</div>

<h3>10.6 Slip Condition</h3>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<b>Bearing:</b> |F_trans| > μ_bearing × F_p
<br><br>
<b>Thread:</b> |F_trans| > μ_thread × F_p × cos(λ)
</div>

<h3>10.7 Archard Wear</h3>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
V = K × F × s / H
<br><br>
h = V / A_contact
<br><br>
ΔF_wear = k_system × h
</div>

<h3>10.8 S-Curve (Jiang)</h3>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<b>Stage I:</b> ΔF₁/F₀ = δF₁_max × (1 - e^(-N/N_stage1))
<br><br>
<b>Stage II:</b> ΔF₂/F₀ = k_stage2 × (N - N_stage1)  [N > N_stage1]
</div>

<h3>10.9 Rotational Preload Loss</h3>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
ΔF_rot = k_bolt × (p/2π) × θ_loosening
</div>

<h3>10.10 Total Loss</h3>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
F_p(N) = F_p0 - ΔF_rot - ΔF_wear - ΔF_embedding
</div>

<h3>10.11 Natural Frequency</h3>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
f_n = (1/2π) × √(k_eq / m_eq)
</div>

<h3>10.12 Critical Damping</h3>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
c_critical = 2 × √(k × m)
<br><br>
ζ = c / c_critical
</div>
"""
    },

    "troubleshooting": {
        "title": "11. Troubleshooting",
        "content": """
<h2>11. Common Problems and Solutions</h2>

<h3>11.1 Loosening Too Fast</h3>
<p><b>Possible causes:</b></p>
<ul>
    <li>Initial friction too low (μ < 0.10)</li>
    <li>Transverse force too high</li>
    <li>Insufficient preload</li>
</ul>
<p><b>Solutions:</b></p>
<ul>
    <li>Increase friction (μ = 0.12-0.15 for lubricated)</li>
    <li>Reduce displacement amplitude</li>
    <li>Increase preload to 70% of yield</li>
</ul>

<h3>11.2 System Always Stable</h3>
<p><b>Possible causes:</b></p>
<ul>
    <li>Transverse force below slip threshold</li>
    <li>Friction too high</li>
    <li>Too few cycles simulated</li>
</ul>
<p><b>Solutions:</b></p>
<ul>
    <li>Check if F_trans > μ × F_p</li>
    <li>Increase number of cycles</li>
    <li>Verify loading model</li>
</ul>

<h3>11.3 Excessive Wear</h3>
<p><b>Possible causes:</b></p>
<ul>
    <li>K coefficient too high</li>
    <li>Hardness too low</li>
    <li>Contact area too small</li>
</ul>
<p><b>Solutions:</b></p>
<ul>
    <li>Check wear parameters (K ~ 10⁻⁶ typical)</li>
    <li>Check material hardness (H ~ 2-3 GPa for steel)</li>
    <li>Increase contact area</li>
</ul>

<h3>11.4 Convergence Errors</h3>
<p><b>For time integration:</b></p>
<ul>
    <li>Reduce dt (timestep)</li>
    <li>Check [M] matrix (no zeros on diagonal)</li>
    <li>Use implicit method (Newmark) instead of explicit</li>
</ul>

<h3>11.5 Non-Physical Results</h3>
<p><b>Symptoms:</b></p>
<ul>
    <li>Negative preload</li>
    <li>Friction too high (> 1)</li>
    <li>Enormous displacements</li>
</ul>
<p><b>Solutions:</b></p>
<ul>
    <li>Check units (SI: N, m, kg, Pa)</li>
    <li>Check that stiffness is not zero</li>
    <li>Check boundary conditions</li>
</ul>

<h3>11.6 Slow Performance</h3>
<p><b>For long analyses:</b></p>
<ul>
    <li>Increase sample_interval (1000 for 1M cycles)</li>
    <li>Reduce target_output_points</li>
    <li>Use preset instead of MSD model (faster)</li>
</ul>

<h3>11.7 Singular [K] Matrix</h3>
<p><b>Causes:</b></p>
<ul>
    <li>Element with k=0</li>
    <li>Unconnected DOF (island)</li>
    <li>Missing boundary condition (GROUND)</li>
</ul>
<p><b>Solutions:</b></p>
<ul>
    <li>Add GROUND element to model</li>
    <li>Check connectivity of all elements</li>
    <li>Ensure k > 0 for all elements</li>
</ul>
"""
    },

    "references": {
        "title": "12. Technical References",
        "content": """
<h2>12. Bibliography</h2>

<h3>12.1 Bolt Loosening</h3>
<ul>
    <li><b>Junker, G. (1969)</b> - "New Criteria for Self-Loosening of Fasteners Under Vibration"
        <br>SAE Technical Paper 690055
        <br><i>Foundational paper establishing transverse slip loosening mechanism.</i></li>
    <br>
    <li><b>Jiang, Y., Zhang, M., Lee, C.H. (2003)</b> - "A Study of Early Stage Self-Loosening of Bolted Joints"
        <br>ASME Journal of Mechanical Design, 125(3): 518-526
        <br><i>Two-stage model (S-curve) for preload loss.</i></li>
    <br>
    <li><b>Yang, X., Nassar, S.A. (2019)</b> - "Effect of Bolt and Joint Parameters on Self-Loosening"
        <br>Shock and Vibration, 2019, Article ID 2036509
        <br><i>Influence of displacement amplitude on loosening.</i></li>
</ul>

<h3>12.2 Friction and Tribology</h3>
<ul>
    <li><b>Hintikka, J., Mäntylä, A., Vaara, J., et al. (2020)</b> - "Friction Coefficient Evolution in Bolted Joints"
        <br>Tribology International, 151: 106519
        <br><i>Three-phase friction evolution model.</i></li>
    <br>
    <li><b>Fouvry, S., Kapsa, P., Vincent, L. (2003)</b> - "Fretting Wear Energy Model"
        <br>Wear, 255: 287-298
        <br><i>Energy-based wear model.</i></li>
</ul>

<h3>12.3 Standards</h3>
<ul>
    <li><b>VDI 2230 Part 1 (2015)</b> - "Systematic Calculation of Highly Stressed Bolted Joints"
        <br><i>German standard for bolted joint calculations.</i></li>
    <br>
    <li><b>DIN 65151 (2002)</b> - "Transverse Loading Test for Bolted Joints"
        <br><i>Standardized Junker test procedure.</i></li>
    <br>
    <li><b>ISO 898-1 (2013)</b> - "Mechanical Properties of Fasteners"
        <br><i>Mechanical properties of bolts.</i></li>
    <br>
    <li><b>ASTM A193/A193M</b> - "Alloy-Steel and Stainless Steel Bolting"
        <br><i>Material specification for bolts.</i></li>
</ul>

<h3>12.4 Reference Books</h3>
<ul>
    <li><b>Bickford, J.H. (2008)</b> - "Introduction to the Design and Behavior of Bolted Joints"
        <br>4th Edition, CRC Press
        <br><i>Complete reference on bolted joint design.</i></li>
    <br>
    <li><b>Budynas, R.G., Nisbett, J.K.</b> - "Shigley's Mechanical Engineering Design"
        <br><i>Chapter on fasteners and joints.</i></li>
</ul>

<h3>12.5 Software and Numerical Methods</h3>
<ul>
    <li><b>Newmark, N.M. (1959)</b> - "A Method of Computation for Structural Dynamics"
        <br>ASCE Journal of the Engineering Mechanics Division, 85: 67-94</li>
    <br>
    <li><b>Hilber, H.M., Hughes, T.J.R., Taylor, R.L. (1977)</b> - "HHT-α Method"
        <br>Earthquake Engineering and Structural Dynamics, 5: 283-292</li>
</ul>

<h3>12.6 Contact</h3>
<p>For technical questions or contributions:</p>
<ul>
    <li>Prof. Leonardo Rosa Ribeiro da Silva, PhD — <a href="mailto:leorrs@ufu.br">leorrs@ufu.br</a></li>
    <li>Neilon de Souza da Silva, PhD — <a href="mailto:neilon@petrobras.com.br">neilon@petrobras.com.br</a></li>
</ul>
"""
    },

    "parameter_tables": {
        "title": "13. Parameter Tables",
        "content": """
<h2>13. Complete Parameter Tables</h2>

<h3>13.1 ISO Metric Bolts - Geometry</h3>
<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Size</th>
    <th>d [mm]</th>
    <th>p [mm]</th>
    <th>d₂ [mm]</th>
    <th>d₃ [mm]</th>
    <th>As [mm²]</th>
    <th>λ [°]</th>
</tr>
<tr><td>M6</td><td>6.0</td><td>1.0</td><td>5.35</td><td>4.77</td><td>20.1</td><td>3.4</td></tr>
<tr><td>M8</td><td>8.0</td><td>1.25</td><td>7.19</td><td>6.47</td><td>36.6</td><td>3.2</td></tr>
<tr><td>M10</td><td>10.0</td><td>1.5</td><td>9.03</td><td>8.16</td><td>58.0</td><td>3.0</td></tr>
<tr><td>M12</td><td>12.0</td><td>1.75</td><td>10.86</td><td>9.85</td><td>84.3</td><td>2.9</td></tr>
<tr><td>M14</td><td>14.0</td><td>2.0</td><td>12.70</td><td>11.55</td><td>115</td><td>2.9</td></tr>
<tr><td>M16</td><td>16.0</td><td>2.0</td><td>14.70</td><td>13.55</td><td>157</td><td>2.5</td></tr>
<tr><td>M20</td><td>20.0</td><td>2.5</td><td>18.38</td><td>16.93</td><td>245</td><td>2.5</td></tr>
<tr><td>M24</td><td>24.0</td><td>3.0</td><td>22.05</td><td>20.32</td><td>353</td><td>2.5</td></tr>
<tr><td>M30</td><td>30.0</td><td>3.5</td><td>27.73</td><td>25.71</td><td>561</td><td>2.3</td></tr>
</table>

<h3>13.2 Property Classes - Mechanical Properties</h3>
<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Class</th>
    <th>Rm [MPa]</th>
    <th>Rp0.2 [MPa]</th>
    <th>A [%]</th>
    <th>HV</th>
    <th>Application</th>
</tr>
<tr><td>4.6</td><td>400</td><td>240</td><td>22</td><td>120-220</td><td>Light structural</td></tr>
<tr><td>5.6</td><td>500</td><td>300</td><td>20</td><td>155-220</td><td>Medium structural</td></tr>
<tr><td>8.8</td><td>800</td><td>640</td><td>12</td><td>250-320</td><td>High strength</td></tr>
<tr><td>10.9</td><td>1000</td><td>900</td><td>9</td><td>320-380</td><td>Very high strength</td></tr>
<tr><td>12.9</td><td>1200</td><td>1080</td><td>8</td><td>380-435</td><td>Maximum strength</td></tr>
</table>

<h3>13.3 Typical Friction Coefficients</h3>
<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Condition</th>
    <th>μ_thread</th>
    <th>μ_bearing</th>
    <th>Notes</th>
</tr>
<tr><td>Dry steel</td><td>0.12-0.18</td><td>0.12-0.18</td><td>High variability</td></tr>
<tr><td>Mineral oil</td><td>0.10-0.14</td><td>0.10-0.14</td><td>More consistent</td></tr>
<tr><td>MoS₂</td><td>0.08-0.12</td><td>0.08-0.12</td><td>Excellent lubrication</td></tr>
<tr><td>Zn-phosphate</td><td>0.10-0.16</td><td>0.10-0.16</td><td>With oil</td></tr>
<tr><td>Zn-nickel</td><td>0.14-0.20</td><td>0.14-0.20</td><td>Anticorrosive</td></tr>
<tr><td>Stainless steel</td><td>0.15-0.25</td><td>0.15-0.25</td><td>Galling risk!</td></tr>
<tr><td>Anti-seize paste</td><td>0.06-0.10</td><td>0.06-0.10</td><td>Moly or copper</td></tr>
</table>

<h3>13.4 Tightening Factors - VDI 2230</h3>
<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Method</th>
    <th>αA (factor)</th>
    <th>Scatter</th>
    <th>Equipment</th>
</tr>
<tr><td>Manual torque</td><td>1.7-2.0</td><td>±30%</td><td>Common wrench</td></tr>
<tr><td>Click torque wrench</td><td>1.4-1.6</td><td>±20%</td><td>Torque wrench</td></tr>
<tr><td>Digital torque wrench</td><td>1.2-1.4</td><td>±15%</td><td>Electronic</td></tr>
<tr><td>Torque + angle</td><td>1.1-1.2</td><td>±10%</td><td>Controller</td></tr>
<tr><td>Elongation</td><td>1.05-1.1</td><td>±5%</td><td>Direct measurement</td></tr>
<tr><td>Ultrasonic</td><td>1.02-1.05</td><td>±2%</td><td>US equipment</td></tr>
</table>

<h3>13.5 Joint Material Properties</h3>
<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Material</th>
    <th>E [GPa]</th>
    <th>H [GPa]</th>
    <th>K_wear</th>
    <th>Use</th>
</tr>
<tr><td>Carbon steel</td><td>210</td><td>2-3</td><td>1×10⁻⁶</td><td>General</td></tr>
<tr><td>Stainless 304</td><td>193</td><td>1.5-2</td><td>5×10⁻⁶</td><td>Corrosive</td></tr>
<tr><td>Aluminum 6061</td><td>69</td><td>0.8-1</td><td>5×10⁻⁵</td><td>Lightweight</td></tr>
<tr><td>Titanium Gr5</td><td>114</td><td>3-4</td><td>1×10⁻⁵</td><td>Aerospace</td></tr>
<tr><td>Bronze</td><td>100</td><td>0.5-1</td><td>1×10⁻⁵</td><td>Anti-galling</td></tr>
</table>

<h3>13.6 Friction Model Parameters</h3>
<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Parameter</th>
    <th>Symbol</th>
    <th>Lubricated</th>
    <th>Dry</th>
    <th>Unit</th>
</tr>
<tr><td>Initial friction</td><td>μ₀</td><td>0.10-0.15</td><td>0.15-0.25</td><td>-</td></tr>
<tr><td>Peak friction</td><td>μ_peak</td><td>1.1×μ₀</td><td>1.3×μ₀</td><td>-</td></tr>
<tr><td>Steady friction</td><td>μ_∞</td><td>0.7×μ₀</td><td>0.8×μ₀</td><td>-</td></tr>
<tr><td>Minimum friction</td><td>μ_min</td><td>0.03</td><td>0.05</td><td>-</td></tr>
<tr><td>Running-in cycles</td><td>N₁</td><td>100</td><td>50</td><td>cycles</td></tr>
<tr><td>Transition cycles</td><td>N₂</td><td>500</td><td>200</td><td>cycles</td></tr>
<tr><td>Steady cycles</td><td>N₃</td><td>5000</td><td>2000</td><td>cycles</td></tr>
<tr><td>Wear degradation</td><td>k_w</td><td>0.01</td><td>0.02</td><td>1/μm</td></tr>
</table>

<h3>13.7 Wear Model Parameters</h3>
<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Parameter</th>
    <th>Symbol</th>
    <th>Typical Value</th>
    <th>Range</th>
    <th>Unit</th>
</tr>
<tr><td>K Archard (running-in)</td><td>K_ri</td><td>5×10⁻⁶</td><td>1-10×10⁻⁶</td><td>-</td></tr>
<tr><td>K Archard (steady)</td><td>K_ss</td><td>1×10⁻⁶</td><td>0.1-5×10⁻⁶</td><td>-</td></tr>
<tr><td>K Archard (severe)</td><td>K_sv</td><td>1×10⁻⁵</td><td>0.5-5×10⁻⁵</td><td>-</td></tr>
<tr><td>Energy coeff.</td><td>α</td><td>5×10⁻¹¹</td><td>1-10×10⁻¹¹</td><td>m³/J</td></tr>
<tr><td>Severe threshold</td><td>h_sv</td><td>50</td><td>30-70</td><td>μm</td></tr>
<tr><td>Catastrophic threshold</td><td>h_cat</td><td>100</td><td>80-150</td><td>μm</td></tr>
<tr><td>Running-in cycles</td><td>N_ri</td><td>100</td><td>50-200</td><td>cycles</td></tr>
</table>

<h3>13.8 S-Curve Parameters (Jiang)</h3>
<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Parameter</th>
    <th>Symbol</th>
    <th>Typical Value</th>
    <th>Description</th>
</tr>
<tr><td>Stage I cycles</td><td>N_stage1</td><td>200</td><td>Embedding duration</td></tr>
<tr><td>Stage I loss</td><td>δF₁</td><td>0.15</td><td>Lost fraction (10-40%)</td></tr>
<tr><td>Stage II cycles</td><td>N_stage2</td><td>2000</td><td>Rotational onset</td></tr>
<tr><td>Stage II rate</td><td>k₂</td><td>0.0001</td><td>Loss/cycle</td></tr>
<tr><td>Transition</td><td>β</td><td>3.0</td><td>Curve smoothness</td></tr>
<tr><td>Displacement threshold</td><td>d_min</td><td>0.15</td><td>Below this, embedding only</td></tr>
<tr><td>Displacement exponent</td><td>n</td><td>2.0</td><td>Amplitude sensitivity</td></tr>
</table>
"""
    },

    "model_coupling": {
        "title": "14. Model Coupling",
        "content": """
<h2>14. Coupling Between Physical Models</h2>

<h3>14.1 Coupling Diagram</h3>
<pre style="background-color: {{BASE}}; padding: 15px; border-radius: {{BORDER_RADIUS_LG}}; font-size: {{FONT_SIZE_LABEL}};">
┌─────────────────────────────────────────────────────────────────────────┐
│                     PHYSICAL MODEL COUPLING                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐   │
│   │   FRICTION   │────────▶│   TORQUES    │────────▶│  LOOSENING   │   │
│   │   μ(N,h,T)   │         │  T_res/T_pit │         │    dθ/dN     │   │
│   └──────┬───────┘         └──────────────┘         └──────┬───────┘   │
│          │                                                   │          │
│          │  μ affects                           θ causes    │          │
│          │  friction capacity                 F_p loss      │          │
│          │                                                   │          │
│          ▼                                                   ▼          │
│   ┌──────────────┐                               ┌──────────────┐      │
│   │     WEAR     │◀──────────────────────────────│   PRELOAD    │      │
│   │   h(N,F,s)   │         F_p affects           │   F_p(N)     │      │
│   └──────┬───────┘         wear rate             └──────┬───────┘      │
│          │                                               │              │
│          │  h affects μ                     F_p affects │              │
│          │  and F_p                         margin      │              │
│          │                                               │              │
│          └────────────────────┬──────────────────────────┘              │
│                               │                                          │
│                               ▼                                          │
│                    ┌──────────────────┐                                  │
│                    │  COMPLETE CYCLE  │                                  │
│                    │ (positive feedback)│                                │
│                    └──────────────────┘                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
</pre>

<h3>14.2 Coupling Equations</h3>

<h4>Friction → Torques:</h4>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
T_thread = <b>μ_thread(N)</b> × F_p × d₂ / (2 cos α)
<br>
T_bearing = <b>μ_bearing(N)</b> × F_p × r_eff
<br><br>
Margin = (T_thread + T_bearing) / T_pitch
</div>

<h4>Torques → Loosening:</h4>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<b>If</b> |F_trans| > μ_bearing × F_p  <b>AND</b>  |F_trans| > μ_thread × F_p × cos(λ):
<br><br>
dθ/dN = C × (slip_amp / d₂) × (1 + excess_ratio) × (p / d₂)
</div>

<h4>Loosening → Preload:</h4>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
ΔF_rot = k_bolt × (p / 2π) × <b>θ_accumulated</b>
</div>

<h4>Wear → Preload:</h4>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
ΔF_wear = k_system × <b>h_total</b>
</div>

<h4>Preload → Wear:</h4>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
dh/dN = K(<b>F_p</b>) × <b>F_p</b> × s / (H × A)
<br><br>
Lower F_p → Lower normal load → Lower wear rate
<br>
BUT: Lower F_p → More slip → More wear per cycle
</div>

<h4>Wear → Friction:</h4>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
μ_effective = μ_base - k_degradation × <b>h_wear</b>
</div>

<h3>14.3 Positive Feedback Loop</h3>
<p>The system exhibits <b>positive feedback</b> that can lead to accelerated loosening:</p>

<ol>
    <li>Transverse load causes <b>slip</b></li>
    <li>Slip causes <b>wear</b></li>
    <li>Wear reduces <b>preload</b> (relaxation)</li>
    <li>Lower preload reduces <b>friction capacity</b></li>
    <li>Lower friction allows <b>more slip</b></li>
    <li>Torque margin drops → <b>rotation</b> begins</li>
    <li>Rotation causes <b>additional</b> preload loss</li>
    <li>Cycle accelerates until <b>failure</b></li>
</ol>

<h3>14.4 S-Curve and Physical Model Interaction</h3>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
<b>Total Loss = max(Physics, Empirical×0.8) + min(Physics, Empirical×0.2)</b>
<br><br>
Where:
<br>- Physics = ΔF_rotational + ΔF_wear
<br>- Empirical = Jiang S-curve (based on amplitude)
<br><br>
This combination ensures:
<br>1. S-curve captures average experimental behavior
<br>2. Physical model adds mechanism details
<br>3. Both contribute to realistic prediction
</div>

<h3>14.5 Boundary Conditions</h3>

<h4>Energy Conservation:</h4>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
E_input = E_elastic + E_friction_dissipated + E_wear
</div>

<h4>Momentum Conservation:</h4>
<div style="background-color: {{SURFACE0}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
ΣT = 0  (static equilibrium)
<br>
T_pitch - T_thread - T_bearing ≤ 0  (no-loosening condition)
</div>

<h4>Physical Limits:</h4>
<ul>
    <li>0 ≤ F_p ≤ F_p0 (preload cannot be negative or increase)</li>
    <li>μ_min ≤ μ ≤ 1.0 (friction has physical limits)</li>
    <li>h ≥ 0 (wear is always positive)</li>
    <li>θ ≥ 0 (loosening is unidirectional)</li>
</ul>

<h3>14.6 Per-Cycle Calculation Sequence</h3>
<pre style="background-color: {{BASE}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
For each cycle N:
│
├── 1. Update friction μ(N, h, T)
│       └── μ = μ_base - k_w×h - k_T×(T-20)
│
├── 2. Check slip condition
│       ├── slip_bearing = |F_trans| > μ_bearing × F_p ?
│       └── slip_thread = |F_trans| > μ_thread × F_p × cos(λ) ?
│
├── 3. If slip_bearing AND slip_thread:
│       ├── Calculate rotation increment dθ
│       └── Calculate wear increment dh
│
├── 4. Update state:
│       ├── θ_total += dθ
│       ├── h_total += dh
│       └── F_p = F_p0 - ΔF_rot - ΔF_wear - ΔF_scurve
│
├── 5. Calculate torques with new F_p
│       └── Margin = (T_res) / (T_pitch)
│
├── 6. Classify phase
│       └── STABLE / NON_ROT / TRANSITION / ROTATIONAL / RUNAWAY
│
└── 7. Store results
</pre>
"""
    },

    "best_practices": {
        "title": "15. Design Best Practices",
        "content": """
<h2>15. Best Practices for Bolted Joints</h2>

<h3>15.1 Preload Selection</h3>
<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Situation</th>
    <th>% of Yield</th>
    <th>Justification</th>
</tr>
<tr>
    <td>Static load</td>
    <td>75-90%</td>
    <td>Maximizes clamping force</td>
</tr>
<tr>
    <td>Light dynamic</td>
    <td>70-80%</td>
    <td>Margin for fatigue</td>
</tr>
<tr>
    <td>Severe dynamic</td>
    <td>60-70%</td>
    <td>Margin for relaxation</td>
</tr>
<tr>
    <td>High temperature</td>
    <td>50-60%</td>
    <td>Considers creep</td>
</tr>
<tr>
    <td>Gasketed joint</td>
    <td>40-60%</td>
    <td>Avoids crushing</td>
</tr>
</table>

<h3>15.2 Loosening Prevention</h3>

<h4>Mechanical Methods:</h4>
<ul>
    <li><b>Nord-Lock washers</b>: Wedges create friction locking
        <br>Effectiveness: ★★★★★ | Cost: $$</li>
    <li><b>Self-locking nut</b>: Nylon insert or deformed
        <br>Effectiveness: ★★★★☆ | Cost: $</li>
    <li><b>Lock nut</b>: Second nut locking the first
        <br>Effectiveness: ★★★☆☆ | Cost: $</li>
    <li><b>Spring washer</b>: Split ring washer
        <br>Effectiveness: ★★☆☆☆ | Cost: $</li>
</ul>

<h4>Chemical Methods:</h4>
<ul>
    <li><b>Loctite (medium)</b>: Removable with tools
        <br>Effectiveness: ★★★★☆ | Cost: $</li>
    <li><b>Loctite (high)</b>: Permanent or with heating
        <br>Effectiveness: ★★★★★ | Cost: $</li>
</ul>

<h4>Design Methods:</h4>
<ul>
    <li><b>Increase preload</b>: Higher friction capacity</li>
    <li><b>Finer pitch</b>: Lower helix angle, more self-locking</li>
    <li><b>Larger diameter</b>: More friction area</li>
    <li><b>Reduce amplitude</b>: Vibration isolation</li>
</ul>

<h3>15.3 Acceptance Criteria</h3>

<div style="background-color: {{SURFACE0}}; padding: 15px; border-radius: {{BORDER_RADIUS_LG}};">
<b>VDI 2230 loosening criterion:</b>
<br><br>
μ_average > 1.5 × μ_critical  → APPROVED
<br><br>
<b>Service life criterion:</b>
<br><br>
N_50% > 2 × N_service  → APPROVED
<br><br>
<b>Maximum loss criterion:</b>
<br><br>
ΔF_p / F_p0 < 20% at N_service  → APPROVED
</div>

<h3>15.4 Design Checklist</h3>

<p>☐ Preload correctly calculated (VDI 2230)</p>
<p>☐ Tightening method defined (torque, angle, ultrasonic)</p>
<p>☐ Scatter considered (αA factor)</p>
<p>☐ External loads known (axial, transverse, moment)</p>
<p>☐ Environmental conditions defined (temperature, corrosion)</p>
<p>☐ Friction coefficients specified</p>
<p>☐ Loosening analysis performed</p>
<p>☐ Anti-loosening system selected if needed</p>
<p>☐ Inspection/maintenance plan defined</p>

<h3>15.5 Critical Limits</h3>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Indicator</th>
    <th>Green</th>
    <th>Yellow</th>
    <th>Red</th>
</tr>
<tr>
    <td>Torque margin</td>
    <td>> 1.5</td>
    <td>1.0 - 1.5</td>
    <td>< 1.0</td>
</tr>
<tr>
    <td>Preload ratio</td>
    <td>> 80%</td>
    <td>50-80%</td>
    <td>< 50%</td>
</tr>
<tr>
    <td>Wear</td>
    <td>< 30 μm</td>
    <td>30-80 μm</td>
    <td>> 80 μm</td>
</tr>
<tr>
    <td>Loosening rate</td>
    <td>< 0.001°/cycle</td>
    <td>0.001-0.01</td>
    <td>> 0.01°/cycle</td>
</tr>
<tr>
    <td>Phase</td>
    <td>STABLE</td>
    <td>NON_ROT/TRANS</td>
    <td>ROT/RUNAWAY</td>
</tr>
</table>

<h3>15.6 When to Use Each Analysis Type</h3>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Situation</th>
    <th>Recommended Analysis</th>
    <th>Key Parameters</th>
</tr>
<tr>
    <td>Preliminary design</td>
    <td>M16 preset, 2000 cycles</td>
    <td>μ, F_p, F_trans</td>
</tr>
<tr>
    <td>Design validation</td>
    <td>MSD model, 10k cycles</td>
    <td>Real geometry, real loads</td>
</tr>
<tr>
    <td>Failure analysis</td>
    <td>MSD model, until failure</td>
    <td>Operating conditions</td>
</tr>
<tr>
    <td>Solution comparison</td>
    <td>Multiple analyses</td>
    <td>Vary anti-loosening</td>
</tr>
<tr>
    <td>Certification</td>
    <td>Complete + Junker test</td>
    <td>Model-test correlation</td>
</tr>
</table>
"""
    },

    "next_steps": {
        "title": "16. Next Steps & Future Development",
        "content": """
<h2>16. Next Steps and Future Development</h2>

<p>This section outlines planned improvements and features for future versions of
Bolt Analysis Studio. These enhancements will expand the software's capabilities
and improve accuracy.</p>

<h3>16.1 High Priority Improvements</h3>

<table border="1" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: {{SURFACE1}};">
    <th>Feature</th>
    <th>Description</th>
    <th>Impact</th>
</tr>
<tr>
    <td><b>Three-Phase Loosening Model</b></td>
    <td>Extend Jiang two-phase to include accelerated failure phase (Phase III)</td>
    <td>Better prediction of catastrophic loosening</td>
</tr>
<tr>
    <td><b>Thread Fatigue Model</b></td>
    <td>Add S-N curves for thread root fatigue, Goodman diagram integration</td>
    <td>Fatigue life prediction capability</td>
</tr>
<tr>
    <td><b>Temperature-Dependent Properties</b></td>
    <td>Full thermal model: E(T), H(T), μ(T), creep(T)</td>
    <td>High-temperature applications</td>
</tr>
<tr>
    <td><b>Multi-Bolt Analysis</b></td>
    <td>Analyze bolt patterns with load sharing and sequential tightening</td>
    <td>Flanged joint applications</td>
</tr>
</table>

<h3>16.2 Model Improvements</h3>

<h4>16.2.1 Advanced Friction Models</h4>
<ul>
    <li><b>Rate-and-State Friction</b>: State variable θ evolving with slip velocity
        <div style="background-color: {{SURFACE0}}; padding: 5px; margin: 5px 0;">
        μ = μ* + a·ln(V/V*) + b·ln(V*·θ/D_c)
        </div></li>
    <li><b>Elasto-Plastic Friction</b>: Pre-sliding micro-slip with hysteresis</li>
    <li><b>LuGre Model</b>: Dynamic bristle model for stick-slip simulation</li>
</ul>

<h4>16.2.2 Enhanced Wear Models</h4>
<ul>
    <li><b>Oxidative Wear</b>: Temperature-dependent oxide layer formation and removal</li>
    <li><b>Adhesive Transfer</b>: Material transfer between contacting surfaces</li>
    <li><b>Third-Body Wear</b>: Debris particle effects on wear rate</li>
    <li><b>Lubrication Film Breakdown</b>: Tribological film degradation under cyclic loading</li>
</ul>

<h4>16.2.3 Fatigue Integration</h4>
<ul>
    <li><b>Thread Root Stress Concentration</b>: K_t factors for various thread forms</li>
    <li><b>S-N Curves Database</b>: Material-specific fatigue data</li>
    <li><b>Goodman/Gerber Diagrams</b>: Mean stress correction</li>
    <li><b>Miner's Rule</b>: Cumulative damage for variable amplitude loading</li>
    <li><b>Fretting Fatigue</b>: Coupling of fretting wear with fatigue crack initiation</li>
</ul>

<h4>16.2.4 Temperature Effects</h4>
<ul>
    <li><b>Thermal Expansion Mismatch</b>: ΔF_p from differential expansion (α_bolt ≠ α_member)</li>
    <li><b>Creep Model</b>: Norton power law for high-temperature relaxation</li>
    <li><b>Temperature-Dependent Material</b>: E(T), σ_y(T), H(T)</li>
    <li><b>Flash Temperature</b>: Contact temperature rise during slip</li>
    <li><b>Heat Generation</b>: Q = μ·F·v from frictional work</li>
</ul>

<h3>16.3 Coupling Improvements</h3>

<h4>16.3.1 Full Thermo-Mechanical Coupling</h4>
<pre style="background-color: {{BASE}}; padding: 10px; border-radius: {{BORDER_RADIUS_LG}};">
Current:  Friction ←→ Wear ←→ Preload ←→ Loosening

Proposed:
          ┌─────────────────────────────────────────┐
          │              TEMPERATURE                 │
          │     ↙          ↓          ↘             │
          │  Friction → Wear → Preload → Loosening  │
          │     ↖          ↑          ↗             │
          │              FATIGUE                     │
          └─────────────────────────────────────────┘
</pre>

<h4>16.3.2 Stochastic Modeling</h4>
<ul>
    <li><b>Monte Carlo Simulation</b>: Parameter uncertainty propagation</li>
    <li><b>Probability Distributions</b>: μ, K_wear, preload scatter</li>
    <li><b>Reliability Analysis</b>: Probability of failure vs. cycles</li>
</ul>

<h3>16.4 Similitude Tab Improvements</h3>

<ul>
    <li><b>Additional Π Groups</b>: Thermal, fatigue, and wear Π numbers</li>
    <li><b>Scaling Validation</b>: Compare scaled model predictions with full-scale data</li>
    <li><b>Automatic Scaling</b>: Given target conditions, compute optimal test parameters</li>
    <li><b>Material Substitution</b>: Rules for using different materials while preserving similarity</li>
    <li><b>Frequency Scaling</b>: Account for rate-dependent effects in accelerated tests</li>
</ul>

<h3>16.5 Case Studies and Validation</h3>

<h4>16.5.1 Planned Case Studies</h4>
<ul>
    <li><b>API 6A Flange</b>: Subsea wellhead connection with temperature cycles</li>
    <li><b>Wind Turbine Blade Root</b>: High cycle fatigue with variable amplitude</li>
    <li><b>Automotive Wheel</b>: Thermal cycling and road vibration</li>
    <li><b>Railway Fishplate</b>: Impact loading and fretting</li>
    <li><b>Pressure Vessel</b>: Gasket creep and bolt relaxation</li>
</ul>

<h4>16.5.2 Validation Against Literature</h4>
<ul>
    <li>Junker machine test data (DIN 65151)</li>
    <li>Jiang et al. (2003) experimental S-curves</li>
    <li>Hintikka et al. (2020) friction evolution data</li>
    <li>Izumi et al. (2005) FEA correlation</li>
</ul>

<h3>16.6 User Interface Improvements</h3>

<ul>
    <li><b>3D Model Visualization</b>: OpenGL rendering of bolt assembly</li>
    <li><b>Animation</b>: Animated loosening mechanism visualization</li>
    <li><b>Interactive Plots</b>: Zoom, pan, data cursor on all plots</li>
    <li><b>Real-Time Simulation</b>: Watch loosening evolve cycle-by-cycle</li>
    <li><b>Report Templates</b>: Customizable PDF/HTML report generation</li>
    <li><b>Project Comparison</b>: Side-by-side comparison of analysis results</li>
</ul>

<h3>16.7 Database Expansion</h3>

<ul>
    <li><b>More Thread Standards</b>: UNC, UNF, ACME, Buttress, etc.</li>
    <li><b>Coating Database</b>: Zn, Zn-Ni, Dacromet, Geomet properties</li>
    <li><b>Lubricant Database</b>: Oil, grease, MoS₂, PTFE properties</li>
    <li><b>Locking Device Database</b>: Nord-Lock, Nylok, Loctite specifications</li>
    <li><b>Gasket Database</b>: Spiral wound, RTJ, sheet gasket properties</li>
</ul>

<h3>16.8 Integration Features</h3>

<ul>
    <li><b>FEA Import</b>: Import stiffness matrices from ANSYS, Abaqus</li>
    <li><b>CAD Integration</b>: Import bolt geometry from STEP/IGES files</li>
    <li><b>Data Logging</b>: Import real sensor data for model calibration</li>
    <li><b>API/SDK</b>: Python API for batch analysis and automation</li>
    <li><b>Cloud Computing</b>: Remote execution for very long simulations</li>
</ul>

<h3>16.9 Research Directions</h3>

<h4>16.9.1 Machine Learning Integration</h4>
<ul>
    <li>Train neural networks on simulation data for rapid estimation</li>
    <li>Anomaly detection for unexpected loosening patterns</li>
    <li>Parameter optimization using genetic algorithms</li>
</ul>

<h4>16.9.2 Advanced Contact Mechanics</h4>
<ul>
    <li>Rough surface contact (Greenwood-Williamson)</li>
    <li>Plasticity at asperity level</li>
    <li>Adhesion (JKR, DMT models)</li>
</ul>

<h3>16.10 Known Limitations (Current Version)</h3>

<p>The current version has the following limitations that are planned for improvement:</p>

<ul>
    <li>Temperature is a constant input, not dynamically computed</li>
    <li>No fatigue damage accumulation</li>
    <li>Single-bolt analysis only (no bolt patterns)</li>
    <li>2D MSD model (no bending moments)</li>
    <li>Friction models don't include velocity dependence</li>
    <li>No coating/lubrication degradation over time</li>
    <li>Limited gasket nonlinearity (no full hysteresis)</li>
</ul>

<h3>16.11 Contributing</h3>

<p>Contributions to Bolt Analysis Studio are welcome! Areas where help is particularly needed:</p>

<ul>
    <li>Experimental data for model validation</li>
    <li>Industrial case studies</li>
    <li>Translation to other languages</li>
    <li>Bug reports and feature requests</li>
    <li>Documentation improvements</li>
</ul>

<p>Contact: Prof. Leonardo Rosa Ribeiro da Silva, PhD — <a href="mailto:leorrs@ufu.br">leorrs@ufu.br</a><br>Neilon de Souza da Silva, PhD — <a href="mailto:neilon@petrobras.com.br">neilon@petrobras.com.br</a></p>
"""
    },

    "validation_reports": {
        "title": "17. Validation Case Reports (210 casos)",
        "content": """
<h2>17. Validation Case Reports (114 casos comparáveis)</h2>

<p>Todos os <b>114 casos de validação comparáveis</b> da biblioteca (literatura + UFU) têm
report individual completo + documento mestre, gerados pelo pacote
<code>bolt_analysis_studio.validation</code> a partir de constantes com
proveniência (bloco <i>shared</i> + configs adotadas per-rig).</p>

<h3>17.1 Conteúdo de cada report</h3>
<ul>
    <li><b>1. Condições de contorno</b> — F&#8320;, modo de carga, amplitude,
        frequência, ciclos, com proveniência</li>
    <li><b>2. Modelo MSD como preparado no software</b> — cadeia de elementos
        real (diagrama + tabela k/c/m), geometria, carregamento global,
        glossário de variáveis e passo-a-passo para refazer</li>
    <li><b>3. Resultado e erro</b> — curva artigo vs modelo, MAE/RMSE,
        narrativa interpretada, <b>resíduo assinado</b> com banda &#177;MAE e
        erro por estágio I/II/III</li>
    <li><b>4. Decomposição por mecanismo</b> — perda cumulativa por
        embedding/creep/wear/loosening (soma fecha 1&#8722;F/F&#8320;)</li>
    <li><b>5. Constantes usadas</b> com proveniência ·
        <b>6. Caveats e veredicto</b></li>
</ul>

<h3>17.2 Como abrir</h3>
<ul>
    <li><b>V1:</b> menu <i>Validation Gallery</i> (gera se ausente e abre o
        documento mestre no navegador)</li>
    <li><b>V2 (run_app.py --v2):</b> módulo <i>Results</i> — navegador dos
        casos com re-simulação e <i>Abrir no Model/Run</i></li>
    <li><b>CLI:</b> <code>python -m bolt_analysis_studio.validation.report
        --all</code> re-simula e regenera tudo</li>
</ul>

<h3>17.3 Casos do usuário (intake via IA)</h3>
<p>No V2 (Results &#8594; Validation): <i>Copiar prompt</i> &#8594; cole numa IA
com sua curva experimental (txt/csv) &#8594; responda às perguntas do ensaio
&#8594; salve o <code>.bascase.json</code> &#8594; <i>Importar caso…</i>. O
software valida, faz o <b>ajuste prévio per-rig</b> (lê embedding e piso da
própria curva; fita só c_bend) e gera o report completo — refinável editando o
bloco <code>prefit</code> do arquivo.</p>

<p>Referência completa: <code>src/bolt_analysis_studio/docs/VALIDATION_CASE_REPORTS.md</code>.
Arquivos: <code>New_Theory/validation_html/</code>.</p>
"""
    },

    "methodology": {
        "title": "18. Metodologia de Evolução do Modelo (MEM)",
        "content": """
<h2>18. Metodologia de Evolução do Modelo (MEM)</h2>

<p>Ciclo sistemático e auditável para reduzir o erro do modelo canônico contra
os dados experimentais, sem overfitting (rev. 2026-07-10).</p>

<h3>18.1 O ciclo</h3>
<ol>
    <li><b>Baseline congelado</b> — erro medido no canônico
        (<code>python -m bolt_analysis_studio.validation.report --all</code>);
        pisos de repetibilidade = limite físico.</li>
    <li><b>Orçamento de erro</b> — cada caso classificado ANTES de mexer
        (<code>python -m bolt_analysis_studio.validation.error_budget</code>):
        no_piso · gap_adocao · nível · forma · sem_simulacao.</li>
    <li><b>Alavancas em ordem de legitimidade</b> — 1º procedência de inputs
        (µ domina); 2º promoção ao adotado (regras por classe); 3º DOF
        per-rig (c_bend; emb/floor LIDOS da curva); 4º forma nova SÓ por
        falsificação pré-registrada; 5º âncora experimental.</li>
    <li><b>Guard-rails</b> — identificabilidade, LOCO, parcimônia,
        conservação de energia, DOF honesto.</li>
    <li><b>Parada</b> — todo caso ≤ max(piso+0.02, 0.10) ou &#916;média
        &lt; 0.002 por 3 iterações.</li>
    <li><b>Adoção e registro</b> — hash, MODEL_LEGITIMACY §4.x, ledger,
        reports regenerados. Campanhas escrevem; o software lê.</li>
</ol>

<h3>18.2 Onde ver</h3>
<p>Report mestre (Validation Gallery): seções <i>Orçamento de erro (MEM)</i> e
<i>Convergência (ledger)</i>. Runbook completo:
<code>src/bolt_analysis_studio/docs/METHODOLOGY.md</code>.</p>
"""
    }
}


# =============================================================================
# SECOES GERADAS NO BUILD (2026-09-02)
# =============================================================================
# As secoes de literatura (19-21) e a referencia de interface (22) sao geradas
# por New_Theory/build_literature_sections.py e build_ui_reference.py, e lidas
# aqui de JSON em resources/docs/. Ficam FORA do literal acima por dois
# motivos: o conteudo vem de dados (o corpus, o Crossref, capturas da propria
# GUI) e teria de ser mantido a mao aqui; e sao ~35 KB e ~N KB de HTML que
# inflariam este arquivo sem ganho.
#
# Lidas no IMPORT e nao sob demanda porque a busca da aba faz
# `section["content"].lower()` sobre o dict inteiro: conteudo preguicoso
# sumiria da busca em silencio.
_DOCS_GERADOS = ("literature.json", "ui_reference.json",
                 "help_sections.json")


def _carrega_secoes_geradas() -> dict:
    """Funde as secoes geradas. Ausencia NAO e' erro: um checkout que nunca
    rodou os geradores tem de abrir o programa com as 18 secoes escritas a
    mao, e nao quebrar na aba de documentacao."""
    import json as _json
    from pathlib import Path as _Path

    base = _Path(__file__).resolve().parent.parent / "resources" / "docs"
    fora = {}
    for nome in _DOCS_GERADOS:
        arq = base / nome
        if not arq.is_file():
            continue
        try:
            d = _json.loads(arq.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for chave, secao in d.items():
            if isinstance(secao, dict) and secao.get("title") and secao.get("content"):
                fora[chave] = secao
    return fora



def _titulo_secao(sec: dict) -> str:
    """Titulo na lingua ativa. Secao sem variante PT devolve o EN, que e' o
    caso das 18 escritas a mao — traduzir 150 KB de prosa de fisica sem
    revisao seria pior que deixar em ingles e dizer isso."""
    from .i18n import Lang
    if not Lang.is_en() and sec.get("title_pt"):
        return sec["title_pt"]
    return sec.get("title", "")


def _conteudo_secao(sec: dict) -> str:
    from .i18n import Lang
    if not Lang.is_en() and sec.get("content_pt"):
        return sec["content_pt"]
    return sec.get("content", "")


DOCUMENTATION.update(_carrega_secoes_geradas())


# =============================================================================
# DOCUMENTATION TAB WIDGET
# =============================================================================

class DocumentationTab(QWidget):
    """
    Documentation tab with searchable, organized technical reference.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the documentation UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create splitter for navigation + content
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Navigation tree
        nav_panel = self._create_navigation_panel()
        splitter.addWidget(nav_panel)

        # Right panel: Content viewer
        content_panel = self._create_content_panel()
        splitter.addWidget(content_panel)

        # Set splitter proportions (25% nav, 75% content)
        splitter.setSizes([250, 750])

        layout.addWidget(splitter)

    def _create_navigation_panel(self) -> QWidget:
        """Create the navigation tree panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(
            Theme.SPACING_SM, Theme.SPACING_SM, Theme.SPACING_SM, Theme.SPACING_SM)

        # Search box
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search documentation...")
        self.search_box.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        # Navigation tree
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.itemClicked.connect(self._on_nav_item_clicked)
        self._populate_nav_tree()
        layout.addWidget(self.nav_tree)

        # Quick links
        quick_group = QGroupBox("Quick Links")
        quick_layout = QVBoxLayout(quick_group)

        quick_buttons = [
            ("🚀 Get Started", "workflow"),
            ("📐 Equations", "equations_summary"),
            ("📊 Plots", "plots_guide"),
            ("📋 Parameters", "parameter_tables"),
            ("🔗 Coupling", "model_coupling"),
            ("🔧 Troubleshoot", "troubleshooting"),
            ("🚧 Next Steps", "next_steps"),
        ]

        for text, key in quick_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, k=key: self._show_section(k))
            quick_layout.addWidget(btn)

        layout.addWidget(quick_group)

        return panel

    def _create_content_panel(self) -> QWidget:
        """Create the content viewer panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(
            Theme.SPACING_SM, Theme.SPACING_SM, Theme.SPACING_SM, Theme.SPACING_SM)

        # Title bar
        title_layout = QHBoxLayout()
        self.section_title = QLabel("Welcome to Documentation")
        self.section_title.setFont(
            QFont(Theme.FONT_SANS_FAMILY, Theme.FONT_SIZE_LARGE, QFont.Weight.Bold))
        title_layout.addWidget(self.section_title)
        title_layout.addStretch()

        # Print button
        print_btn = QPushButton("Print")
        print_btn.clicked.connect(self._on_print)
        title_layout.addWidget(print_btn)

        layout.addLayout(title_layout)

        # Content browser
        self.content_browser = QTextBrowser()
        # Sem isto os <img> da secao 22 (referencia de interface) ficam
        # quebrados: o QTextBrowser resolve src relativo contra os
        # searchPaths, e o HTML usa 'ui_reference/<tela>.png'.
        from pathlib import Path as _P
        self.content_browser.setSearchPaths(
            [str(_P(__file__).resolve().parent.parent / "resources")])
        self.content_browser.setOpenExternalLinks(True)
        self._apply_browser_style()

        # Show welcome content
        self._show_welcome()

        layout.addWidget(self.content_browser)

        return panel

    def _populate_nav_tree(self):
        """Popula a arvore de navegacao A PARTIR do DOCUMENTATION.

        Era uma lista escrita a mao com 16 pares, e o dict ja' tinha 18: as
        secoes 17 e 18 existiam e NAO eram navegaveis, so' alcancaveis pela
        busca. Com as secoes geradas (19-25) o desencontro so' cresceria.
        Ordena pelo numero do proprio titulo, que e' onde a numeracao mora.
        """
        self.nav_tree.clear()

        def _num(par):
            m = re.match(r"\s*(\d+)", _titulo_secao(par[1]))
            return (int(m.group(1)) if m else 999, _titulo_secao(par[1]))

        for key, _sec in sorted(DOCUMENTATION.items(), key=_num):
            item = QTreeWidgetItem([_titulo_secao(_sec)])
            item.setData(0, Qt.ItemDataRole.UserRole, key)
            self.nav_tree.addTopLevelItem(item)

        self.nav_tree.expandAll()

    def _show_welcome(self):
        """Show welcome content."""
        welcome_html = """
<h1 style="color: {{BLUE}};">Bolt Analysis Studio Documentation</h1>

<p style="font-size: {{FONT_SIZE_HEADING}};">Welcome to the complete documentation for the bolted joint
loosening analysis software.</p>

<h2>Navigation</h2>
<p>Use the panel on the left to navigate sections or use the search bar to find
specific topics.</p>

<h2>Main Sections</h2>
<ul>
    <li><b>MSD Model</b> - Mass-Spring-Damper model fundamentals</li>
    <li><b>Contact System</b> - Contact hierarchy and tribology</li>
    <li><b>Physical Models</b> - Friction, wear, and loosening</li>
    <li><b>Parameters</b> - How to configure the solver</li>
    <li><b>Plots</b> - Results interpretation</li>
    <li><b>Tutorial</b> - Complete step-by-step guide</li>
    <li><b>Next Steps</b> - Future development roadmap</li>
</ul>

<h2>Quick Start</h2>
<p>To begin an analysis:</p>
<ol>
    <li>Create a model in the <b>Model</b> tab</li>
    <li>Configure loading</li>
    <li>Run analysis in the <b>Solver</b> tab</li>
    <li>View results in the <b>Results</b> tab</li>
</ol>

<p style="color: {{GREEN}};">Click a section on the left to begin.</p>
"""
        self.content_browser.setHtml(_theme_html(welcome_html))

    def _on_nav_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle navigation item click."""
        key = item.data(0, Qt.ItemDataRole.UserRole)
        if key:
            self._show_section(key)

    def _show_section(self, key: str):
        """Show a documentation section."""
        if key in DOCUMENTATION:
            section = DOCUMENTATION[key]
            self._current_key = key
            self.section_title.setText(_titulo_secao(section))
            self.content_browser.setHtml(
                _theme_html(_conteudo_secao(section)))

    def _on_search(self, text: str):
        """Handle search."""
        if not text:
            self._show_welcome()
            return

        text_lower = text.lower()
        results = []

        for key, section in DOCUMENTATION.items():
            alvo = " ".join(str(section.get(c, "")) for c in
                            ("title", "content", "title_pt", "content_pt")).lower()
            if text_lower in alvo:
                results.append((_titulo_secao(section), key))

        if results:
            # Show search results
            html = f"<h2>Results for '{text}'</h2><ul>"
            for title, key in results:
                html += f'<li><a href="#{key}">{title}</a></li>'
            html += "</ul>"

            # Add first match content
            if results:
                first_key = results[0][1]
                html += f"<hr>{DOCUMENTATION[first_key]['content']}"

            self.content_browser.setHtml(_theme_html(html))
            self.section_title.setText(f"Search: {text}")
        else:
            self.content_browser.setHtml(f"<p>No results for '{text}'</p>")

    def _on_print(self):
        """Print current content."""
        try:
            from PyQt6.QtPrintSupport import QPrintDialog, QPrinter

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintDialog(printer, self)
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                self.content_browser.print_(printer)
        except ImportError:
            pass  # Print support not available

    # -----------------------------------------------------------------
    # Theme support
    # -----------------------------------------------------------------

    def _apply_browser_style(self):
        """Apply current Theme colors to the content browser."""
        self.content_browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {Theme.BASE};
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE1};
                border-radius: {Theme.BORDER_RADIUS_LG}px;
                padding: {Theme.PADDING_CONTENT};
                font-family: {Theme.FONT_SANS};
                font-size: {Theme.FONT_SIZE_SUBHEADING}pt;
            }}
        """)

    def refresh_theme(self):
        """Re-apply styles and re-render current content after theme change."""
        self._apply_browser_style()
        self.section_title.setFont(
            QFont(Theme.FONT_SANS_FAMILY, Theme.FONT_SIZE_LARGE, QFont.Weight.Bold))
        # Re-render whatever is currently displayed so _theme_html() picks
        # up the new palette values.
        current_html = self.content_browser.toHtml()
        # The simplest reliable approach: re-show the welcome or the
        # currently-selected nav item.
        selected_items = self.nav_tree.selectedItems()
        if selected_items:
            key = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            if key:
                self._show_section(key)
                return
        self._show_welcome()
