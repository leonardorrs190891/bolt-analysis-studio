# MSD Builder & Tab 2 - Comprehensive Study and Improvement Plan

## LTAD/UFU - Bolt Analysis Studio v4.0
**Date:** 2026-02-18
**Scope:** Complete audit of MSD Builder (Tab 2), presets, wizard, validation, and contact system

---

## Table of Contents

1. [Literature Review: Bolted Joint MSD Models](#1-literature-review)
2. [Current Architecture Audit](#2-current-architecture-audit)
3. [Critical Bugs Found](#3-critical-bugs-found)
4. [Preset Audit](#4-preset-audit)
5. [Validation System Audit](#5-validation-system-audit)
6. [UX Improvement Proposals](#6-ux-improvement-proposals)
7. [Recommended Implementation Plan](#7-recommended-implementation-plan)

---

## 1. Literature Review

### 1.1 VDI 2230 Two-Spring Model (Grundmodell)

The VDI 2230 Part 1 (2015) models a bolted joint as two springs sharing deformation:

```
                    F_V (Preload)
                        |
        +---------------+---------------+
        |               |               |
     +--+--+                         +--+--+
     |     |   Bolt (tension)        |     |   Members (compression)
     | k_b |                         | k_m |
     |     |                         |     |
     +--+--+                         +--+--+
        |               |               |
        +---------------+---------------+
                        |
                   F_ext (External)
```

**Key equations:**
- Force ratio: `Phi_n = n * k_b / (k_b + k_m)`
- Bolt additional load: `delta_F_b = Phi_n * F_ext`
- Clamp force relief: `delta_F_m = (1 - Phi_n) * F_ext`
- Remaining clamp force: `F_clamp = F_preload - (1 - Phi_n) * F_ext`

**References:**
- VDI 2230 Part 1 (2015): "Systematic Calculation of Highly Stressed Bolted Joints"
- VDI 2230 Part 2 (2014): Multi-bolted joints
- Bickford, J.H. "Introduction to the Design and Behavior of Bolted Joints" 4th Ed., CRC Press (2007)

### 1.2 VDI 2230 Bolt Stiffness Chain (Series Springs)

The bolt is decomposed into several compliance sections in series:

```
 GROUND (fixed)
    |
 +------+
 | k_SK |  Head stiffness: k_SK = 0.5 * E * d * pi
 +--+---+
    |
 +--+---+
 | k_1  |  Unthreaded shank: k_1 = E * A_N / l_1
 +--+---+
    |
 +--+---+
 | k_d  |  Free loaded thread: k_d = E * A_s / l_G
 +--+---+
    |
 +--+---+
 | k_GM |  Engaged thread zone: k_GM = E * A_s / (0.5 * d)
 +--+---+
    |
 +--+---+
 | k_M  |  Nut flexibility: k_M = 0.4 * E * d
 +------+
    |
 GROUND (nut bearing)
```

**Overall bolt compliance:**
```
delta_b = 1/k_b = 1/k_SK + 1/k_1 + 1/k_d + 1/k_GM + 1/k_M
```

| Section | Formula | Description |
|---------|---------|-------------|
| Head | `k_SK = 0.5 * pi * E * d_w` | Head bending + compression |
| Shank | `k_1 = E * A_N / l_1` | Prismatic bar, nominal area |
| Free thread | `k_d = E * A_s / l_G` | Threaded section, stress area |
| Engaged thread | `k_GM = E * A_s / (0.5 * d)` | Half nominal diameter approx |
| Nut | `k_M = 0.4 * E * d` | Nut deformation contribution |

### 1.3 Clamped Members Stiffness

VDI 2230 models clamped parts as a compression frustum (Rotscher's cone):

**VDI frustum method:**
```
k_m = (E * d_w * pi * tan(phi)) / [2 * ln(((D_A - d_w)(d_w + d_h*tan(phi))) / ((D_A + d_w)(d_w - d_h*tan(phi))))]
```

**Wileman et al. (1991) empirical:**
```
k_m = E * d * 0.78715 * exp(0.62873 * d / l_clamp)
```

**Multi-layer (flanges + gasket):**
```
1/k_m = 1/k_flange1 + 1/k_gasket + 1/k_flange2
```

### 1.4 Junker Loosening Mechanism

The Junker test (DIN 65945 / NAS 3350, Junker 1969) requires **complete transverse slip at BOTH** the thread interface AND the bearing surface:

**Loosening condition (per cycle):**
```
IF |F_transverse| > mu_thread * F_p  (thread slips)
AND |F_transverse| > mu_bearing * F_p  (bearing slips)
THEN:
    theta_loosening = integral(omega_nut * dt)
    delta_F_preload = k_system * (p / (2*pi)) * theta_loosening
```

**Preload loss mechanisms (total):**
```
F_p(t) = F_p0 - dF_rot - dF_embed - dF_wear - dF_creep - dF_relax - dF_thermal
```

| Mechanism | Formula | Typical % of F_p0 |
|-----------|---------|-------------------|
| Rotational (Junker) | `dF = k_b * (p/2pi) * theta` | 5-100% |
| Embedding | `dF = k_sys * f_z` (VDI table) | 2-10% |
| Gasket creep | `dF = k_sys * C_r * log(t)` | 5-30% |
| Stress relaxation | `dF = F_p0 * (1 - exp(-t/tau))` | 3-15% |
| Wear | `dF = k_sys * K_w * F * s / (H*A)` | 1-5% |
| Thermal | `dF = k_sys * (a_b - a_m) * L * dT` | 0-50% |

### 1.5 Thread Contact - Parallel Fillet Model

The thread contact is modeled as **n parallel springs**, one per engaged thread:

```
     STUD                    NUT
      |                       |
      +---- k_1, c_1 --------+  Thread 1 (most loaded, phi_1 ~ 45%)
      +---- k_2, c_2 --------+  Thread 2 (phi_2 ~ 27%)
      +---- k_3, c_3 --------+  Thread 3 (phi_3 ~ 15%)
      +---- k_4, c_4 --------+  Thread 4 (phi_4 ~ 7%)
      +---- k_5, c_5 --------+  Thread 5 (phi_5 ~ 5%)
      |                       |
```

**Load distribution models:**
- **Yamamoto (1980):** `phi_i = sinh(gamma*(n-i+0.5)) / sum(sinh(gamma*(n-j+0.5)))` - most accurate
- **Exponential:** `phi_i = exp(-lambda*(i-1)) / sum(exp(-lambda*(j-1)))`, lambda ~ 0.3-0.5
- **Power law:** `phi_i = (n-i+1)^beta / sum(j^beta)`, beta ~ 1.5-2.0
- **Linear:** `phi_i = 2*(n-i+1) / (n*(n+1))`
- **Uniform:** `phi_i = 1/n`

**Helix coupling in [K] matrix (critical for loosening):**
```
K[x_axial, theta_rot] = k_thread * p / (2 * pi)    <-- off-diagonal
```

### 1.6 Required Contact Interfaces

| Contact Location | Type | Required? | Key Properties |
|------------------|------|-----------|----------------|
| Head - Washer/Flange | BEARING_HEAD | Yes | mu_b, A_bearing, r_eff |
| Washer - Flange | WASHER_FLANGE | If washer | k_embed, A_contact |
| Flange - Flange | FLANGE_FLANGE | If no gasket | k_contact, mu_interface |
| Flange - Gasket | FLANGE_GASKET | If gasket | k(delta), c_visco, creep |
| Gasket - Flange | GASKET_FLANGE | If gasket | Same (bottom side!) |
| Nut - Washer/Flange | BEARING_NUT | Yes | mu_b, A_bearing |
| Stud - Nut | THREAD | **ALWAYS** | n_threads, helix, mu_t |

**Key principle:** Every physical interface between two adjacent elements MUST have a contact.

### 1.7 Preload as Initial Condition

**Critical:** Preload is NOT an external force during dynamic analysis. It creates an initial deformation state:
```
Static solve:  [K]{x_0} = {F_preload}
```
Then `F_p(t)` is tracked as a state variable that evolves through loosening mechanisms.

**References:**
- Junker, G.H. "New Criteria for Self-Loosening of Fasteners Under Vibration." SAE 690055 (1969)
- Pai, N.G., Hess, D.P. "Three-Dimensional FEA of Threaded Fastener Loosening." Eng. Failure Anal. 9(4), 383-402 (2002)
- Nassar, S.A., Housari, B.A. "Effect of Thread Pitch on Self-Loosening." ASME J. Press. Vessel Technol. 128(4), 590-598 (2006)
- Dinger, G., Friedrich, C. "Avoiding Self-Loosening Failure with Numerical Assessment." Eng. Failure Anal. 18(8), 2188-2200 (2011)
- Yamamoto, A. "Theory and Computation of Threads Connection." (1980)
- Wileman, J., et al. "Computation of Member Stiffness." ASME J. Mech. Des. 113(4), 432-437 (1991)

---

## 2. Current Architecture Audit

### 2.1 Correct Element Chain per VDI 2230

Based on the literature, the **correct** element chain for a standard bolted flanged joint should be:

```
GROUND (boundary condition - fixed structure)
  |
  +-- [BEARING_HEAD contact] -- between HEAD and FLANGE1
  |
HEAD (bolt head, k = 0.5*E*d)
  |
  +-- (no contact needed - same bolt body)
  |
SHANK (unthreaded portion, k = E*A/L)
  |
  +-- (no contact needed - same bolt body)
  |
FLANGE 1 (top clamped member, k from frustum model)
  |
  +-- [FLANGE_GASKET contact] -- between FLANGE1 and GASKET
  |
GASKET (seal, nonlinear k)
  |
  +-- [GASKET_FLANGE contact] -- between GASKET and FLANGE2
  |
FLANGE 2 (bottom clamped member)
  |
  +-- [BEARING_NUT contact] -- between FLANGE2 and NUT
  |
NUT (k_nut = 0.4*E*d)
  |
  +-- [THREAD contact] -- parallel fillets between NUT and STUD
  |
GROUND (boundary condition - or implicit at chain end)
```

**Key rules:**
1. Every interface between two DIFFERENT components needs a contact
2. Bolt body elements (HEAD-SHANK) are the same material, no contact needed
3. Thread contact is ALWAYS required on every NUT
4. Bearing contacts are required on HEAD and NUT bearing surfaces
5. Gasket needs contacts on BOTH sides (top flange and bottom flange)

### 2.2 Current Implementation vs. Correct Model

| Aspect | Literature/VDI 2230 | Current BAS Code | Gap |
|--------|---------------------|-------------------|-----|
| Bolt stiffness chain | HEAD-SHANK-NUT in series | Implemented | OK |
| Member stiffness | Frustum model | FLANGE elements | OK |
| Thread contact | Parallel array with helix | ThreadContact class | Framework exists |
| Bearing contacts | On HEAD and NUT | Missing in presets | **CRITICAL** |
| Gasket contacts | Both sides | Only top side in preset | **CRITICAL** |
| Contact export | Model carries contacts | export_to_model loses them | **CRITICAL** |
| Preload default | Computed from bolt spec | Was 0.0, now 50 kN | Improved |
| Validation | Check all contacts exist | Too lenient, early-exits | **HIGH** |

---

## 3. Critical Bugs Found

### BUG-01: export_to_model() Loses All Contacts [CRITICAL]

**File:** `msd_builder.py` line 1905-1953

**Problem:** `SchematicView.export_to_model()` creates an MSDModel from elements but NEVER transfers the contacts dict to the model.

```python
def export_to_model(self) -> Optional[MSDModel]:
    model = MSDModel(name="Schematic Model")
    for item in sorted_items:
        model.add_element(item.element_data)
    return model  # contacts=[] !!
```

**Impact:** All contacts defined via `add_contact()` are lost during export. The model passed to the solver has no contacts, so thread stiffness, bearing friction, and gasket behavior are all missing.

**Fix:** After adding elements, copy contacts:
```python
for key, contact_interface in self.contacts.items():
    model.contacts.append(contact_interface)
```

### BUG-02: validate_contacts() Early-Exit Bypasses Checks [CRITICAL]

**File:** `model.py` line 387-414

**Problem:** If `self.contacts` is empty, the method returns `is_valid=True` without checking whether contacts SHOULD exist.

```python
if not self.contacts:
    if nut_elements:
        messages.append("OK: nut elements found...")
    return is_valid, messages  # TRUE even with missing contacts!
```

**Impact:** A model with NUT elements but zero ThreadContacts passes validation.

**Fix:** If nut elements exist, contacts should be required (at minimum a WARNING).

### BUG-03: Flanged Joint Preset Missing Gasket Bottom Contact [CRITICAL]

**File:** `msd_builder.py` line 6691

**Problem:** Only FLANGE1-GASKET contact exists. GASKET-FLANGE2 contact is missing.

```
HEAD -- [bearing] -- FLANGE1 -- [gasket_contact] -- GASKET -- [???] -- FLANGE2 -- [bearing] -- NUT
```

**Fix:** Add `add_contact(gasket, flange2, contact_gasket_bottom)`.

### BUG-04: Single Bolt Preset Missing Bearing Contacts [CRITICAL]

**File:** `msd_builder.py` line 6645-6664

**Problem:** Only thread self-contacts on NUTs. No bearing contacts between NUT and adjacent elements.

```
GROUND -- [???] -- NUT1 -- [???] -- SHANK -- [???] -- NUT2
                    |                                   |
                    +-- thread self-contact              +-- thread self-contact
```

**Fix:** Add bearing contacts: NUT1-GROUND, NUT1-SHANK, SHANK-NUT2.

### BUG-05: Junker Preset Uses Invalid Element Types [HIGH]

**File:** `msd_builder.py` line 6710-6714

**Problem:** `"BEARING_HEAD"` and `"BEARING_NUT"` are contact interface types, not component types. They silently fall back to `GENERIC_CONTACT` via the KeyError handler.

**Fix:** Use `"GENERIC_CONTACT"` explicitly, or better: remove these placeholder elements and use proper contact interfaces between HEAD-FLANGE and NUT-FLANGE.

### BUG-06: Wizard Creates Zero Contacts [CRITICAL]

**File:** `msd_builder.py` line 7304-7430

**Problem:** `_build_from_wizard()` creates elements but NEVER calls `add_contact()`. The wizard configuration has `add_head_contact`, `add_flange_contact`, `add_thread_contact` fields, but they are completely ignored.

**Fix:** Add contact creation logic matching the preset patterns, respecting the wizard config flags.

### BUG-07: Stress Area Formula Error [MEDIUM]

**File:** `msd_builder.py` line 1124

**Problem:** Uses `d3 = diameter - 1.2269 * p` but should use `d1 = diameter - 1.0825 * p` per ISO 262.

```python
# Current (wrong):
d3 = diameter - 1.2269 * p
A_s = pi / 4 * ((d2 + d3) / 2) ** 2  # ~14% error

# Correct (ISO 262):
d1 = diameter - 1.0825 * p
A_s = pi / 4 * ((d2 + d1) / 2) ** 2
```

### BUG-08: Hardcoded M16 and Sy=720 in All Presets [HIGH]

**File:** `msd_builder.py` line 6743-6748, 7433-7449

**Problem:** All presets use `bolt_dia=16.0, bolt_pitch=2.0, Sy=720.0` regardless of user selection in wizard. Wizard `bolt_grade` field is completely ignored.

---

## 4. Preset Audit

### 4.1 Single Bolt Preset

**Current elements:**
```
Row 0: GROUND
Row 1: NUT #1 (thread self-contact)
Row 2: SHANK
Row 3: NUT #2 (thread self-contact)
```

**Missing contacts:**
- GROUND -- NUT1 (bearing)
- NUT1 -- SHANK (bearing/thread coupling)
- SHANK -- NUT2 (bearing/thread coupling)

**Correct model per VDI 2230:**
```
Row 0: GROUND
Row 1: NUT #1       + [BEARING contact NUT1-GROUND] + [THREAD contact NUT1 self]
Row 2: SHANK
Row 3: NUT #2       + [BEARING contact NUT2-GROUND*] + [THREAD contact NUT2 self]
```
*Note: In a stud bolt, the second ground is implicit at the chain end.

### 4.2 Flanged Joint Preset

**Current elements and contacts:**
```
Row 0: GROUND
Row 1: HEAD          + [BEARING_HEAD contact HEAD-FLANGE1]
Row 2: FLANGE 1      + [GASKET contact FLANGE1-GASKET]
Row 3: GASKET
Row 4: FLANGE 2
Row 5: NUT           + [THREAD contact NUT self] + [BEARING_NUT contact NUT-FLANGE2]
```

**Missing contacts:**
- GASKET -- FLANGE2 (gasket bottom contact)

**Correct model:**
```
Row 0: GROUND
Row 1: HEAD          + [BEARING_HEAD: HEAD-FLANGE1]
Row 2: FLANGE 1      + [FLANGE_GASKET: FLANGE1-GASKET]
Row 3: GASKET         + [GASKET_FLANGE: GASKET-FLANGE2]
Row 4: FLANGE 2
Row 5: NUT           + [THREAD: NUT self] + [BEARING_NUT: NUT-FLANGE2]
```

### 4.3 Junker Test Preset

**Current elements:**
```
Row 0: GROUND
Row 1: BEARING_HEAD (-> falls back to GENERIC_CONTACT)
Row 2: HEAD          + [contact HEAD-BEARING_HEAD]
Row 3: SHANK
Row 4: NUT           + [THREAD contact NUT self]
Row 5: BEARING_NUT (-> falls back to GENERIC_CONTACT) + [contact NUT-BEARING_NUT]
```

**Problems:**
- BEARING_HEAD and BEARING_NUT are not valid component types
- Should use proper contact interfaces, not placeholder elements
- Missing: SHANK-NUT connection

**Correct Junker test model:**
```
Row 0: GROUND
Row 1: HEAD           + [BEARING_HEAD contact: HEAD-GROUND]
Row 2: SHANK
Row 3: FLANGE 1 (top plate, fixed)
Row 4: FLANGE 2 (bottom plate, transverse oscillation)
Row 5: NUT            + [THREAD: NUT self] + [BEARING_NUT: NUT-FLANGE2]
```

### 4.4 Wizard-Generated Models

**Problem:** The wizard creates elements correctly based on configuration, but creates ZERO contacts. All contact configuration checkboxes (`add_head_contact`, `add_flange_contact`, `add_thread_contact`) have no effect.

---

## 5. Validation System Audit

### 5.1 Current Validation Checks

| Check | Location | Status |
|-------|----------|--------|
| Ground element exists | model.py:1055 | OK |
| Per-element k > 0 | element.py:1373 | OK |
| Per-element m >= 0 | element.py:1378 | OK |
| Per-element c >= 0 | element.py:1383 | OK |
| Mass matrix invertible | model.py:1175 | OK |
| K matrix positive definite | model.py:1196 | OK |
| K matrix condition number | model.py:1280 | OK |
| K_eff invertible (Newmark) | model.py:1247 | OK |
| Preload > 0 | model.py:1072 | Fixed (auto-computes) |
| External loads exist | model.py:1109 | OK (warning only) |
| Contact validation | model.py:387 | **BROKEN** (early exit) |
| Matrix symmetry | model.py:1237 | OK |
| Damping non-negative | model.py:1230 | OK |

### 5.2 Missing Validation Checks

| Missing Check | Priority | Description |
|---------------|----------|-------------|
| Every NUT has thread contact | CRITICAL | Currently passes if contacts=[] |
| HEAD/NUT have bearing contacts | HIGH | Not checked at all |
| Adjacent elements have contacts | HIGH | No connectivity validation |
| Preload vs. yield strength | MEDIUM | F_preload < 0.9 * A_s * Sy |
| Contact deserialization errors | HIGH | Silently returns None on failure |
| Wizard config vs. model match | MEDIUM | Wizard options ignored |
| Element geometry > 0 | MEDIUM | Only diameter checked, not length |
| Material properties valid | LOW | E, Sy, Su all > 0 |

### 5.3 Validation After Preset/Wizard Build

**Current:** No validation is called after building from preset or wizard.
**Required:** Call `_validate_model()` automatically and show warnings.

---

## 6. UX Improvement Proposals

### 6.1 Tab 2 (MSD Builder) - Proposed Improvements

#### P-01: Auto-Contact Creation [HIGH PRIORITY]

**Current problem:** User must manually define contacts between elements. Presets create some contacts but miss others. Wizard creates none.

**Proposal:** When an element is added adjacent to another, automatically create the appropriate contact interface based on element types:

```python
# Auto-contact rules:
CONTACT_RULES = {
    (HEAD, FLANGE):   SpecificContactType.BOLT_HEAD_FLANGE,
    (HEAD, WASHER):   SpecificContactType.BOLT_HEAD_WASHER,
    (WASHER, FLANGE): SpecificContactType.WASHER_FLANGE,
    (FLANGE, FLANGE): SpecificContactType.FLANGE_FLANGE,
    (FLANGE, GASKET): SpecificContactType.FLANGE_GASKET,
    (GASKET, FLANGE): SpecificContactType.FLANGE_GASKET,
    (NUT, FLANGE):    SpecificContactType.NUT_FLANGE,
    (NUT, WASHER):    SpecificContactType.NUT_WASHER,
    (NUT, NUT):       SpecificContactType.THREAD_CONTACT,  # self
}
```

When elements are in series (adjacent rows), check the pair `(type_above, type_below)` and auto-create the contact. Show a small contact indicator between the elements in the schematic.

#### P-02: Contact Visualization in Schematic [HIGH PRIORITY]

**Current problem:** Contacts are invisible in the schematic. Users cannot see which elements have contacts and which don't.

**Proposal:** Draw contact indicators between connected elements:
- Small diamond or circle between rows where a contact exists
- Color-coded: green = thread, blue = bearing, orange = gasket, red = missing
- Tooltip on hover shows contact type and properties
- Clicking the contact indicator opens the contact property editor

```
 [GROUND]
    |
 [  HEAD  ]
    <>  <-- bearing contact indicator (blue diamond)
 [FLANGE 1]
    <>  <-- gasket contact indicator (orange diamond)
 [ GASKET ]
    <>  <-- gasket contact indicator (orange diamond)
 [FLANGE 2]
    <>  <-- bearing contact indicator (blue diamond)
 [  NUT   ]
    @   <-- thread contact indicator (green circle)
```

#### P-03: Intelligent Presets with Full Contacts [HIGH PRIORITY]

**Current problem:** Presets create incomplete models with missing contacts.

**Proposal:** Rewrite all 3 presets to follow VDI 2230 correctly:

**Single Bolt (Stud):**
```
GROUND -- [bearing] -- NUT1 -- SHANK -- NUT2 -- [bearing] -- GROUND
              |                                      |
         [thread]                               [thread]
```

**Flanged Joint (Standard Bolt):**
```
GROUND -- HEAD -- [bearing] -- FLANGE1 -- [gasket] -- GASKET -- [gasket] -- FLANGE2 -- [bearing] -- NUT -- GROUND
                                                                                                      |
                                                                                                 [thread]
```

**Junker Test:**
```
GROUND -- HEAD -- [bearing] -- FLANGE1 -- [flange] -- FLANGE2 -- [bearing] -- NUT -- GROUND
                                                                                       |
              F_transverse applied to FLANGE2 -->                                  [thread]
```

#### P-04: Bolt Size and Grade Integration [MEDIUM PRIORITY]

**Current problem:** Presets hardcode M16x2.0 and Sy=720 MPa regardless of user selection.

**Proposal:**
1. When user selects bolt size in wizard, look up from threads.json database
2. When user selects bolt grade, look up Sy from materials database
3. Compute preload from actual A_s and Sy, not hardcoded values
4. Update all element geometries (diameter, pitch, head_diameter, etc.) from bolt spec

```python
def _get_bolt_properties(bolt_size: str, grade: str) -> dict:
    """Look up bolt properties from database."""
    # Parse "M16x2.0" -> diameter=16, pitch=2.0
    # Look up A_s from threads.json
    # Look up Sy from grade (e.g., "8.8" -> Sy=640, "10.9" -> Sy=940)
    return {
        "diameter": d, "pitch": p, "A_s": A_s,
        "Sy": Sy, "Su": Su,
        "head_diameter": 1.5*d, "head_height": 0.7*d,
        "nut_height": 0.8*d
    }
```

#### P-05: Live Validation Status Bar [MEDIUM PRIORITY]

**Current problem:** User must click "Validate" button to see errors. No real-time feedback.

**Proposal:** Add a persistent status bar at the bottom of the MSD Builder showing:
```
[OK] 6 elements | 5 DOF | 4 contacts | F_preload = 79.1 kN | f_n = 24.0 kHz
```
or
```
[!] 6 elements | 5 DOF | 1 MISSING CONTACT (NUT-FLANGE2) | F_preload = 79.1 kN
```

Update automatically whenever model changes.

#### P-06: Context Menu Enhancement [MEDIUM PRIORITY]

**Current problem:** Right-click only shows Duplicate, Delete, Define Contact.

**Proposal:** Enhanced context menu based on element type:

For NUT element:
```
- Edit Properties
- Recalculate MSD Parameters
- ---
- Define Thread Contact (required!)
- Define Bearing Contact
- ---
- Expand to Parallel Fillets...
- ---
- Duplicate
- Delete
```

For any element:
```
- Edit Properties
- Recalculate MSD Parameters
- ---
- Connect to above element (auto-contact)
- Connect to below element (auto-contact)
- Define Custom Contact...
- ---
- Duplicate
- Delete
```

#### P-07: Wizard Contact Creation [HIGH PRIORITY]

**Current problem:** Wizard builds elements but creates zero contacts.

**Proposal:** Add contact creation loop to `_build_from_wizard()`:

```python
# After all elements are added:
prev_elem_id = None
for elem_id in ordered_element_ids:
    if prev_elem_id is not None:
        contact_type = _get_auto_contact_type(prev_type, current_type)
        if contact_type:
            self.schematic.add_contact(prev_elem_id, elem_id, contact_type)
    prev_elem_id = elem_id

# Always add thread self-contact on every NUT
for nut_id in nut_ids:
    self.schematic.add_contact(nut_id, nut_id, THREAD_CONTACT)
```

#### P-08: Material Grade Selector in Loading Panel [LOW PRIORITY]

**Current problem:** Sy is a manual spinbox. User must know the yield strength.

**Proposal:** Add a dropdown for common bolt grades that auto-fills Sy:

| Grade | Sy (MPa) | Su (MPa) |
|-------|----------|----------|
| 4.6 | 240 | 400 |
| 5.8 | 420 | 520 |
| 8.8 | 640 | 800 |
| 10.9 | 940 | 1040 |
| 12.9 | 1100 | 1220 |
| A193 B7 | 720 | 860 |
| A193 B7M | 550 | 690 |
| A320 L7 | 720 | 860 |

#### P-09: Delete All with Preset Quick-Load [LOW PRIORITY]

**Current problem:** After Delete All, user starts from scratch.

**Proposal:** After Delete All, show a "Quick Start" overlay with preset buttons:
```
+--------------------------------------------------+
|  Start a new model:                               |
|  [Single Bolt]  [Flanged Joint]  [Junker Test]   |
|  [Wizard...]    [Load .msd File...]               |
+--------------------------------------------------+
```

#### P-10: Element Connection Indicators [MEDIUM PRIORITY]

**Current problem:** No visual indication of which elements are connected.

**Proposal:** Draw spring/damper/mass symbols between elements in the schematic, similar to a traditional MSD diagram. Show:
- Spring symbol (zigzag) proportional to k value
- Damper symbol (piston) proportional to c value
- Mass block proportional to m value

### 6.2 Global Improvements

#### G-01: Consistent Error Handling [HIGH PRIORITY]

Replace all silent `except: pass` patterns with proper logging:
```python
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Failed to deserialize contact: {e}")
    messages.append(f"WARNING: Contact load failed: {e}")
```

#### G-02: Post-Build Validation [HIGH PRIORITY]

After every preset load, wizard build, or file load, automatically run validation and show results if there are errors:
```python
def _post_build_validate(self):
    model = self.export_to_msd_model()
    is_valid, messages = model.validate()
    errors = [m for m in messages if m.startswith("ERROR")]
    if errors:
        QMessageBox.warning(self, "Model Issues", "\n".join(errors))
```

#### G-03: Thread Database Integration [MEDIUM PRIORITY]

Use threads.json consistently for:
- Stress area lookup (instead of formula approximation)
- Pitch lookup from diameter
- Pitch diameter and minor diameter
- Head dimensions from bolt size

---

## 7. Recommended Implementation Plan

### Phase 1: Critical Bug Fixes (Immediate)

| # | Task | File | Priority | Est. Lines |
|---|------|------|----------|------------|
| 1.1 | Fix export_to_model to include contacts | msd_builder.py:1905 | CRITICAL | ~10 |
| 1.2 | Fix validate_contacts early-exit logic | model.py:387 | CRITICAL | ~15 |
| 1.3 | Fix flanged preset: add gasket bottom contact | msd_builder.py:6691 | CRITICAL | ~8 |
| 1.4 | Fix single bolt preset: add bearing contacts | msd_builder.py:6645 | CRITICAL | ~15 |
| 1.5 | Fix Junker preset: proper element types | msd_builder.py:6707 | CRITICAL | ~20 |
| 1.6 | Fix wizard: add contact creation | msd_builder.py:7304 | CRITICAL | ~40 |
| 1.7 | Fix stress area formula (d3 -> d1) | msd_builder.py:1124 | MEDIUM | ~2 |

### Phase 2: Validation Hardening (1-2 days)

| # | Task | File | Priority | Est. Lines |
|---|------|------|----------|------------|
| 2.1 | Add post-build validation call | msd_builder.py | HIGH | ~15 |
| 2.2 | Add contact dependency validation | model.py | HIGH | ~30 |
| 2.3 | Fix silent exception handlers | model.py, msd_builder.py | HIGH | ~20 |
| 2.4 | Add preload vs yield check | model.py | MEDIUM | ~10 |

### Phase 3: UX Improvements (3-5 days)

| # | Task | File | Priority | Est. Lines |
|---|------|------|----------|------------|
| 3.1 | Auto-contact creation on element add | msd_builder.py | HIGH | ~50 |
| 3.2 | Contact visualization in schematic | msd_builder.py | HIGH | ~80 |
| 3.3 | Bolt grade lookup integration | msd_builder.py | MEDIUM | ~40 |
| 3.4 | Live validation status bar | msd_builder.py | MEDIUM | ~30 |
| 3.5 | Enhanced context menu | msd_builder.py | MEDIUM | ~40 |
| 3.6 | Quick start overlay | msd_builder.py | LOW | ~30 |

### Phase 4: Model Correctness (1 week)

| # | Task | File | Priority | Est. Lines |
|---|------|------|----------|------------|
| 4.1 | VDI 2230 correct stiffness formulas | element.py | HIGH | ~60 |
| 4.2 | Proper Junker test model topology | msd_builder.py | HIGH | ~40 |
| 4.3 | Thread geometry auto-population | msd_builder.py | MEDIUM | ~30 |
| 4.4 | Contact property auto-defaults | msd_builder.py | MEDIUM | ~40 |

---

## Appendix A: Correct Preset Models

### A.1 Single Bolt Joint (Stud Bolt M16x2.0, ASTM A193 B7)

```
Elements:
  [0] GROUND     (row=0, k=1e15, m=0.01)
  [1] NUT #1     (row=1, k=1.64e9, m=0.045, preload=79.1kN)
  [2] SHANK      (row=2, k=1.65e9, m=0.040)
  [3] NUT #2     (row=3, k=1.64e9, m=0.045, preload=79.1kN)

Contacts:
  NUT#1 <-> NUT#1   : THREAD_CONTACT (6 fillets, power_law)
  GROUND <-> NUT#1   : BEARING (mu=0.14, A_bearing=pi*(24^2-16^2)/4)
  NUT#2 <-> NUT#2   : THREAD_CONTACT (6 fillets, power_law)
  NUT#2 <-> SHANK   : BEARING (mu=0.14)

Loading:
  F_preload = 79128 N (70% yield, A_s=157mm2, Sy=720MPa)
  bolt_diameter = 16mm, pitch = 2.0mm
```

### A.2 Flanged Joint (Standard Bolt M16x2.0)

```
Elements:
  [0] GROUND     (row=0)
  [1] HEAD       (row=1, k=0.5*E*d*pi = 5.15e9)
  [2] FLANGE 1   (row=2, k from frustum)
  [3] GASKET     (row=3, nonlinear k)
  [4] FLANGE 2   (row=4, k from frustum)
  [5] NUT        (row=5, k=0.4*E*d = 1.31e9)

Contacts:
  HEAD <-> FLANGE1     : BOLT_HEAD_FLANGE (mu=0.14)
  FLANGE1 <-> GASKET   : FLANGE_GASKET (nonlinear)
  GASKET <-> FLANGE2   : FLANGE_GASKET (nonlinear)  <-- CURRENTLY MISSING!
  NUT <-> FLANGE2      : NUT_FLANGE (mu=0.14)
  NUT <-> NUT          : THREAD_CONTACT (6 fillets)

Loading:
  F_preload = 79128 N (70% yield)
  F_transverse = 10000 N (Junker mechanism driver)
```

### A.3 Junker Test (M16x2.0)

```
Elements:
  [0] GROUND         (row=0, fixed upper fixture)
  [1] HEAD           (row=1)
  [2] SHANK          (row=2)
  [3] FLANGE 1       (row=3, upper plate - fixed)
  [4] FLANGE 2       (row=4, lower plate - transverse oscillation)
  [5] NUT            (row=5)

Contacts:
  HEAD <-> GROUND      : BEARING_HEAD (mu=0.14)
  FLANGE1 <-> FLANGE2  : FLANGE_FLANGE (mu_interface, transverse coupling)
  NUT <-> FLANGE2      : BEARING_NUT (mu=0.14)
  NUT <-> NUT          : THREAD_CONTACT (6 fillets, helix coupling)

Loading:
  F_preload = 79128 N
  delta_amplitude = 0.65 mm (transverse)
  frequency = 12.5 Hz
  F_transverse = delta * k_trans
```

---

## Appendix B: Contact Auto-Creation Rules

```python
AUTO_CONTACT_MAP = {
    # (above_type, below_type) -> SpecificContactType
    (ElementType.GROUND, ElementType.HEAD):    SpecificContactType.BOLT_HEAD_FLANGE,
    (ElementType.GROUND, ElementType.NUT):     SpecificContactType.NUT_FLANGE,
    (ElementType.HEAD, ElementType.WASHER):    SpecificContactType.BOLT_HEAD_WASHER,
    (ElementType.HEAD, ElementType.FLANGE):    SpecificContactType.BOLT_HEAD_FLANGE,
    (ElementType.WASHER, ElementType.FLANGE):  SpecificContactType.WASHER_FLANGE,
    (ElementType.FLANGE, ElementType.FLANGE):  SpecificContactType.FLANGE_FLANGE,
    (ElementType.FLANGE, ElementType.GASKET):  SpecificContactType.FLANGE_GASKET,
    (ElementType.GASKET, ElementType.FLANGE):  SpecificContactType.FLANGE_GASKET,
    (ElementType.FLANGE, ElementType.WASHER):  SpecificContactType.WASHER_FLANGE,
    (ElementType.FLANGE, ElementType.NUT):     SpecificContactType.NUT_FLANGE,
    (ElementType.WASHER, ElementType.NUT):     SpecificContactType.NUT_WASHER,
    (ElementType.NUT, ElementType.FLANGE):     SpecificContactType.NUT_FLANGE,
}

# Thread contact: ALWAYS auto-create on NUT (self-contact)
# No contact needed between: HEAD-SHANK, SHANK-NUT (same bolt body)
SAME_BODY_PAIRS = {
    (ElementType.HEAD, ElementType.SHANK),
    (ElementType.SHANK, ElementType.NUT),
    (ElementType.SHANK, ElementType.HEAD),
    (ElementType.NUT, ElementType.SHANK),
}
```

---

*Document generated by Bolt Analysis Studio development team.*
*Based on code audit of v4.0 codebase and VDI 2230 / Junker / Pai-Hess literature review.*
