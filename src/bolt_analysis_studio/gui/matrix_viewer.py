"""
Matrix Visualization Dialog for MSD Model Builder
Bolt Analysis Studio v4.0

Provides visual inspection of assembled [M], [K], [C] matrices
with spy plots, heatmaps, and numerical value displays.

Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026
"""

import sys
import numpy as np
from typing import Optional, Dict, Any, Tuple

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QPushButton, QComboBox, QGroupBox, QFormLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QMessageBox, QSplitter, QFrame, QTextEdit, QApplication,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from bolt_analysis_studio.gui.theme import Theme


# =============================================================================
# MATRIX CANVAS WIDGET
# =============================================================================

class MatrixCanvas(FigureCanvas):
    """Matplotlib canvas for matrix visualization."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=Theme.BASE)
        self.axes = self.fig.add_subplot(111)
        self._colorbar = None  # Track colorbar for cleanup
        super().__init__(self.fig)
        self.setParent(parent)

        # Apply dark theme to axes
        self._apply_dark_theme()

    def _apply_dark_theme(self):
        """Apply dark theme to axes."""
        self.axes.set_facecolor(Theme.SURFACE0)
        self.axes.tick_params(colors=Theme.TEXT)
        self.axes.spines['bottom'].set_color(Theme.SURFACE2)
        self.axes.spines['top'].set_color(Theme.SURFACE2)
        self.axes.spines['right'].set_color(Theme.SURFACE2)
        self.axes.spines['left'].set_color(Theme.SURFACE2)

    def _safe_tight_layout(self):
        """Safely apply tight_layout, catching any errors."""
        try:
            self.fig.tight_layout()
        except Exception:
            # tight_layout can fail with singular matrix errors
            # when the figure has invalid dimensions - just skip it
            pass

    def _clear_colorbar(self):
        """Remove existing colorbar if present."""
        if self._colorbar is not None:
            try:
                self._colorbar.remove()
            except Exception:
                pass
            self._colorbar = None

    def plot_spy(self, matrix: np.ndarray, title: str = "Matrix"):
        """Plot spy diagram showing non-zero pattern."""
        # Clear colorbar from previous heatmap if any
        self._clear_colorbar()

        self.axes.clear()
        self._apply_dark_theme()

        if matrix.size == 0:
            self.axes.text(0.5, 0.5, "Empty matrix", ha='center', va='center',
                          color=Theme.TEXT, fontsize=12)
            self.draw()
            return

        # Replace NaN/Inf with 0 for visualization
        clean_matrix = np.nan_to_num(matrix, nan=0.0, posinf=0.0, neginf=0.0)

        # Create spy plot
        self.axes.spy(clean_matrix, markersize=10, color=Theme.BLUE,
                     markerfacecolor=Theme.BLUE, markeredgecolor=Theme.BLUE)

        self.axes.set_title(title, color=Theme.TEXT, fontsize=12, fontweight='bold')
        self.axes.set_xlabel("Column", color=Theme.SUBTEXT)
        self.axes.set_ylabel("Row", color=Theme.SUBTEXT)
        self.axes.tick_params(colors=Theme.TEXT)

        self._safe_tight_layout()
        self.draw()

    def plot_heatmap(self, matrix: np.ndarray, title: str = "Matrix",
                    cmap: str = 'coolwarm'):
        """Plot heatmap of matrix values."""
        # Clear any existing colorbar first
        self._clear_colorbar()

        # Clear axes and recreate for clean state
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        self._apply_dark_theme()

        if matrix.size == 0:
            self.axes.text(0.5, 0.5, "Empty matrix", ha='center', va='center',
                          color=Theme.TEXT, fontsize=12)
            self.draw()
            return

        # Replace NaN/Inf with 0 for visualization
        clean_matrix = np.nan_to_num(matrix, nan=0.0, posinf=0.0, neginf=0.0)

        # Normalize for better visualization
        vmax = np.max(np.abs(clean_matrix))
        if vmax == 0 or not np.isfinite(vmax):
            vmax = 1

        im = self.axes.imshow(clean_matrix, cmap=cmap, aspect='auto',
                             vmin=-vmax, vmax=vmax)

        # Add colorbar and track it for cleanup
        try:
            self._colorbar = self.fig.colorbar(im, ax=self.axes)
            self._colorbar.ax.yaxis.set_tick_params(color=Theme.TEXT)
            self._colorbar.outline.set_edgecolor(Theme.SURFACE2)
            plt.setp(plt.getp(self._colorbar.ax.axes, 'yticklabels'), color=Theme.TEXT)
        except Exception:
            self._colorbar = None

        self.axes.set_title(title, color=Theme.TEXT, fontsize=12, fontweight='bold')
        self.axes.set_xlabel("Column", color=Theme.SUBTEXT)
        self.axes.set_ylabel("Row", color=Theme.SUBTEXT)
        self.axes.tick_params(colors=Theme.TEXT)

        self._safe_tight_layout()
        self.draw()

    def plot_bar(self, vector: np.ndarray, title: str = "Force Vector"):
        """Plot bar chart for force vector."""
        # Clear colorbar from previous heatmap if any
        self._clear_colorbar()

        self.axes.clear()
        self._apply_dark_theme()

        if vector.size == 0:
            self.axes.text(0.5, 0.5, "Empty vector", ha='center', va='center',
                          color=Theme.TEXT, fontsize=12)
            self.axes.set_xlim(0, 1)
            self.axes.set_ylim(0, 1)
            self.draw()
            return

        # Handle all-zero vector case
        if np.all(vector == 0):
            self.axes.text(0.5, 0.5, "Force vector is all zeros\n(No loads applied)",
                          ha='center', va='center', color=Theme.SUBTEXT, fontsize=11)
            self.axes.set_xlim(0, 1)
            self.axes.set_ylim(0, 1)
            self.axes.axis('off')
            self.draw()
            return

        x = np.arange(len(vector))
        colors = [Theme.GREEN if v >= 0 else Theme.RED for v in vector]

        bars = self.axes.bar(x, vector, color=colors, edgecolor=Theme.SURFACE2, linewidth=0.5)

        # Add value labels on bars for non-zero values
        for i, (bar, val) in enumerate(zip(bars, vector)):
            if abs(val) > 1e-6:  # Only label significant values
                height = bar.get_height()
                label_y = height + (0.02 * (max(vector) - min(vector)) if height >= 0 else -0.02 * (max(vector) - min(vector)))
                self.axes.text(bar.get_x() + bar.get_width()/2., label_y,
                             f'{val:.1f}',
                             ha='center', va='bottom' if height >= 0 else 'top',
                             color=Theme.TEXT, fontsize=8)

        self.axes.set_title(title, color=Theme.TEXT, fontsize=12, fontweight='bold', pad=10)
        self.axes.set_xlabel("DOF Index", color=Theme.SUBTEXT, fontsize=10)
        self.axes.set_ylabel("Force (N)", color=Theme.SUBTEXT, fontsize=10)
        self.axes.tick_params(colors=Theme.TEXT, labelsize=9)
        self.axes.axhline(y=0, color=Theme.SURFACE2, linestyle='-', linewidth=0.8)
        self.axes.grid(axis='y', alpha=0.2, color=Theme.SURFACE1)

        # Set reasonable limits
        self.axes.set_xlim(-0.5, len(vector) - 0.5)
        y_margin = 0.1 * (max(vector) - min(vector)) if max(vector) != min(vector) else 1
        self.axes.set_ylim(min(vector) - y_margin, max(vector) + y_margin)

        self._safe_tight_layout()
        self.draw()


# =============================================================================
# MATRIX TAB WIDGET
# =============================================================================

class MatrixTab(QWidget):
    """Tab widget for displaying a single matrix."""

    def __init__(self, matrix: np.ndarray, name: str, model=None, parent=None):
        super().__init__(parent)
        self.matrix = matrix
        self.name = name
        self.model = model  # Store model reference for element contributions
        self._setup_ui()

    def _setup_ui(self):
        """Setup tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Control panel
        controls = QHBoxLayout()

        display_label = QLabel("Display:")
        self.display_combo = QComboBox()
        self.display_combo.addItems(["Spy Plot", "Heatmap", "Values Table", "Equations", "Element Contributions"])
        self.display_combo.currentTextChanged.connect(self._update_display)

        format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Scientific", "Engineering", "Fixed"])
        self.format_combo.currentTextChanged.connect(self._update_table_format)

        copy_btn = QPushButton("Copy")
        copy_btn.setToolTip("Copy matrix to clipboard")
        copy_btn.clicked.connect(self._copy_to_clipboard)

        export_btn = QPushButton("Export")
        export_btn.setToolTip("Export matrix to CSV file")
        export_btn.clicked.connect(self._export_csv)

        controls.addWidget(display_label)
        controls.addWidget(self.display_combo)
        controls.addWidget(format_label)
        controls.addWidget(self.format_combo)
        controls.addStretch()
        controls.addWidget(copy_btn)
        controls.addWidget(export_btn)

        layout.addLayout(controls)

        # Splitter for plot and properties
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Visualization
        self.canvas = MatrixCanvas(self, width=5, height=4)
        splitter.addWidget(self.canvas)

        # Right: Properties and table
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Properties group
        props_group = QGroupBox("Matrix Properties")
        props_layout = QFormLayout(props_group)

        self.dim_label = QLabel()
        self.symmetry_label = QLabel()
        self.cond_label = QLabel()
        self.rank_label = QLabel()
        self.sparsity_label = QLabel()

        props_layout.addRow("Dimensions:", self.dim_label)
        props_layout.addRow("Symmetric:", self.symmetry_label)
        props_layout.addRow("Condition #:", self.cond_label)
        props_layout.addRow("Rank:", self.rank_label)
        props_layout.addRow("Sparsity:", self.sparsity_label)

        right_layout.addWidget(props_group)

        # Table for values
        self.table = QTableWidget()
        self.table.setVisible(False)
        right_layout.addWidget(self.table, stretch=1)

        # Text display for equations
        self.equations_text = QTextEdit()
        self.equations_text.setReadOnly(True)
        self.equations_text.setVisible(False)
        self.equations_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.SURFACE0};
                color: {Theme.TEXT};
                font-family: {Theme.FONT_MONO};
                font-size: 10pt;
                line-height: 1.4;
            }}
        """)
        right_layout.addWidget(self.equations_text, stretch=1)

        splitter.addWidget(right_panel)
        splitter.setSizes([400, 250])

        layout.addWidget(splitter, stretch=1)

        # Initialize display
        self._calculate_properties()
        self._update_display("Spy Plot")

    def _calculate_properties(self):
        """Calculate and display matrix properties."""
        if self.matrix.size == 0:
            self.dim_label.setText("0 x 0")
            self.symmetry_label.setText("N/A")
            self.cond_label.setText("N/A")
            self.rank_label.setText("N/A")
            self.sparsity_label.setText("N/A")
            return

        # Clean matrix for calculations
        clean_matrix = np.nan_to_num(self.matrix, nan=0.0, posinf=0.0, neginf=0.0)

        n, m = clean_matrix.shape
        self.dim_label.setText(f"{n} x {m}")

        # Check symmetry
        if n == m:
            try:
                is_symmetric = np.allclose(clean_matrix, clean_matrix.T, rtol=1e-10)
                self.symmetry_label.setText("Yes" if is_symmetric else "No")
                self.symmetry_label.setStyleSheet(
                    f"color: {Theme.GREEN};" if is_symmetric else f"color: {Theme.YELLOW};"
                )
            except:
                self.symmetry_label.setText("N/A")
        else:
            self.symmetry_label.setText("N/A (not square)")

        # Condition number
        try:
            cond = np.linalg.cond(clean_matrix)
            if np.isfinite(cond) and cond < 1e10:
                self.cond_label.setText(f"{cond:.2e}")
                self.cond_label.setStyleSheet(f"color: {Theme.GREEN};")
            elif np.isfinite(cond):
                self.cond_label.setText(f"{cond:.2e} (ill-conditioned)")
                self.cond_label.setStyleSheet(f"color: {Theme.RED};")
            else:
                self.cond_label.setText("∞ (singular)")
                self.cond_label.setStyleSheet(f"color: {Theme.RED};")
        except:
            self.cond_label.setText("N/A")

        # Rank
        try:
            rank = np.linalg.matrix_rank(clean_matrix)
            self.rank_label.setText(f"{rank} / {min(n, m)}")
        except:
            self.rank_label.setText("N/A")

        # Sparsity
        nonzero = np.count_nonzero(clean_matrix)
        total = n * m
        sparsity = 100 * (1 - nonzero / total) if total > 0 else 0
        self.sparsity_label.setText(f"{sparsity:.1f}% zeros")

    def _update_display(self, display_type: str):
        """Update the visualization based on selected type."""
        self.table.setVisible(display_type == "Values Table")
        self.canvas.setVisible(display_type not in ("Values Table", "Equations", "Element Contributions"))
        self.equations_text.setVisible(display_type in ("Equations", "Element Contributions"))

        if display_type == "Spy Plot":
            self.canvas.plot_spy(self.matrix, f"[{self.name}] Sparsity Pattern")
        elif display_type == "Heatmap":
            self.canvas.plot_heatmap(self.matrix, f"[{self.name}] Values")
        elif display_type == "Values Table":
            self._populate_table()
        elif display_type == "Equations":
            self._populate_equations()
        elif display_type == "Element Contributions":
            self._populate_element_contributions()

    def _populate_table(self):
        """Populate the table with matrix values."""
        if self.matrix.size == 0:
            return

        n, m = self.matrix.shape
        self.table.setRowCount(n)
        self.table.setColumnCount(m)

        self.table.setUpdatesEnabled(False)
        self.table.blockSignals(True)
        try:
            fmt = self.format_combo.currentText()
            for i in range(n):
                for j in range(m):
                    val = self.matrix[i, j]

                    # Handle NaN/Inf
                    if not np.isfinite(val):
                        text = "NaN" if np.isnan(val) else ("∞" if val > 0 else "-∞")
                        item = QTableWidgetItem(text)
                        item.setForeground(QColor(Theme.RED))
                    elif fmt == "Scientific":
                        text = f"{val:.3e}"
                    elif fmt == "Engineering":
                        if val != 0 and np.isfinite(val):
                            exp = int(np.floor(np.log10(abs(val))))
                            exp = (exp // 3) * 3
                            mantissa = val / (10 ** exp)
                            text = f"{mantissa:.3f}e{exp:+d}"
                        else:
                            text = "0.000e+0"
                    else:
                        text = f"{val:.4f}"

                    if np.isfinite(val):
                        item = QTableWidgetItem(text)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                        # Color based on value
                        if val == 0:
                            item.setForeground(QColor(Theme.OVERLAY))
                        elif val > 0:
                            item.setForeground(QColor(Theme.GREEN))
                        else:
                            item.setForeground(QColor(Theme.RED))

                    self.table.setItem(i, j, item)
        finally:
            self.table.blockSignals(False)
            self.table.setUpdatesEnabled(True)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _populate_equations(self):
        """Populate the text display with detailed symbolic equations for matrix elements."""
        if self.matrix.size == 0:
            self.equations_text.setPlainText("Empty matrix - no equations to display")
            return

        n, m = self.matrix.shape
        equations = []

        # Header
        equations.append("═" * 70)
        equations.append(f"  [{self.name}] Matrix - Mathematical Formulation")
        equations.append(f"  Dimensions: {n} × {m}")
        equations.append("═" * 70 + "\n")

        # Generate equations based on matrix type
        if self.name == "M":
            equations.append("╔══════════════════════════════════════════════════════════════════╗")
            equations.append("║                    MASS MATRIX [M]                                ║")
            equations.append("╚══════════════════════════════════════════════════════════════════╝\n")

            equations.append("📐 GENERAL FORM:")
            equations.append("─" * 60)
            equations.append("  [M] is diagonal for lumped mass formulation:")
            equations.append("")
            equations.append("        ┌                     ┐")
            equations.append("        │ m₁  0   0   ...  0  │")
            equations.append("        │ 0   m₂  0   ...  0  │")
            equations.append("  [M] = │ 0   0   m₃  ...  0  │")
            equations.append("        │ :   :   :   ⋱   :  │")
            equations.append("        │ 0   0   0   ...  mₙ │")
            equations.append("        └                     ┘\n")

            equations.append("📝 ELEMENT EQUATIONS:")
            equations.append("─" * 60)
            equations.append("  M[i,i] = mᵢ   (mass at DOF i)")
            equations.append("  M[i,j] = 0    for i ≠ j (no mass coupling)\n")

            equations.append("  Component contributions:")
            equations.append("  • Bolt Head:  m_head = ρ × V_head")
            equations.append("  • Shank:      m_shank = ρ × π × d² × L_shank / 4")
            equations.append("  • Thread:     m_thread = ρ × π × d₃² × L_thread / 4")
            equations.append("  • Nut:        m_nut = ρ × V_nut")
            equations.append("  • Washer:     m_washer = ρ × π × (D²-d²) × t / 4")
            equations.append("  • Flange:     m_flange (from assembly geometry)\n")

            equations.append("📊 ACTUAL VALUES:")
            equations.append("─" * 60)
            total_mass = 0
            for i in range(min(n, 15)):
                if self.matrix[i, i] != 0:
                    equations.append(f"  M[{i},{i}] = {self.matrix[i, i]:.6e} kg")
                    total_mass += self.matrix[i, i]
                else:
                    equations.append(f"  M[{i},{i}] = 0 kg (massless DOF)")
            if n > 15:
                equations.append(f"\n  ... ({n - 15} more elements)")
            equations.append(f"\n  Total system mass: {total_mass:.6e} kg")

        elif self.name == "K":
            equations.append("╔══════════════════════════════════════════════════════════════════╗")
            equations.append("║                  STIFFNESS MATRIX [K]                             ║")
            equations.append("╚══════════════════════════════════════════════════════════════════╝\n")

            equations.append("📐 GENERAL FORM (Series Connection):")
            equations.append("─" * 60)
            equations.append("  For n elements in series, [K] is tridiagonal:")
            equations.append("")
            equations.append("        ┌                                        ┐")
            equations.append("        │ k₁+k₂  -k₂    0      0    ...   0      │")
            equations.append("        │ -k₂    k₂+k₃  -k₃    0    ...   0      │")
            equations.append("  [K] = │  0     -k₃    k₃+k₄  -k₄  ...   0      │")
            equations.append("        │  :      :      :      :    ⋱    :      │")
            equations.append("        │  0      0      0    -kₙ₋₁ kₙ₋₁+kₙ -kₙ  │")
            equations.append("        │  0      0      0      0    -kₙ    kₙ   │")
            equations.append("        └                                        ┘\n")

            equations.append("📝 ELEMENT EQUATIONS:")
            equations.append("─" * 60)
            equations.append("  Diagonal:     K[i,i] = kᵢ + kᵢ₊₁")
            equations.append("  Off-diagonal: K[i,i+1] = K[i+1,i] = -kᵢ₊₁\n")

            equations.append("  Component stiffness formulas:")
            equations.append("  • Bolt Head:    k_head = 0.5 × E × d")
            equations.append("  • Shank:        k_shank = E × A / L_shank = E × π × d² / (4 × L_shank)")
            equations.append("  • Thread:       k_thread = E × Aₛ / L_thread")
            equations.append("  • Nut:          k_nut = 0.4 × E × d  (thread engagement)")
            equations.append("  • Washer:       k_washer = E × A_washer / t")
            equations.append("  • Flange:       k_flange (Rotscher cone model)")
            equations.append("  • Gasket:       k_gasket = A × E_eff / t_gasket (nonlinear)\n")

            equations.append("  Thread contact (helix coupling):")
            equations.append("  • K[axial, θ] = K[θ, axial] = k_thread × (p / 2π)")
            equations.append("  • This enables rotational loosening modeling\n")

            equations.append("📊 ACTUAL VALUES (Non-zero entries):")
            equations.append("─" * 60)
            count = 0
            for i in range(n):
                for j in range(m):
                    if self.matrix[i, j] != 0 and count < 20:
                        if i == j:
                            equations.append(f"  K[{i},{j}] = {self.matrix[i, j]:.6e} N/m (diagonal)")
                        else:
                            equations.append(f"  K[{i},{j}] = {self.matrix[i, j]:.6e} N/m (coupling)")
                        count += 1
                    if count >= 20:
                        break
                if count >= 20:
                    break
            if np.count_nonzero(self.matrix) > 20:
                equations.append(f"\n  ... ({np.count_nonzero(self.matrix) - 20} more entries)")

        elif self.name == "C":
            equations.append("╔══════════════════════════════════════════════════════════════════╗")
            equations.append("║                   DAMPING MATRIX [C]                              ║")
            equations.append("╚══════════════════════════════════════════════════════════════════╝\n")

            equations.append("📐 RAYLEIGH DAMPING MODEL:")
            equations.append("─" * 60)
            equations.append("  [C] = α[M] + β[K] + [C_viscous]")
            equations.append("")
            equations.append("  where:")
            equations.append("    α = mass-proportional coefficient")
            equations.append("    β = stiffness-proportional coefficient")
            equations.append("")
            equations.append("  To achieve damping ratio ζ at frequencies ω₁ and ω₂:")
            equations.append("    α = 2ζ × ω₁ × ω₂ / (ω₁ + ω₂)")
            equations.append("    β = 2ζ / (ω₁ + ω₂)\n")

            equations.append("📝 ELEMENT EQUATIONS:")
            equations.append("─" * 60)
            equations.append("  Viscous damping (dashpot model):")
            equations.append("    F_damping = c × ẋ")
            equations.append("")
            equations.append("  Critical damping: c_crit = 2 × √(k × m)")
            equations.append("  Damping ratio:    ζ = c / c_crit")
            equations.append("")
            equations.append("  Typical ζ values:")
            equations.append("    • Bolted joints: 0.02 - 0.05")
            equations.append("    • Rubber gaskets: 0.05 - 0.15")
            equations.append("    • Viscoelastic: 0.1 - 0.3\n")

            equations.append("  Contact friction contribution to damping:")
            equations.append("    c_friction = μ × F_n × (4/π) / (ω × δ)")
            equations.append("    (equivalent viscous for hysteretic friction)\n")

            equations.append("📊 ACTUAL VALUES:")
            equations.append("─" * 60)
            count = 0
            for i in range(min(n, 15)):
                if self.matrix[i, i] != 0:
                    equations.append(f"  C[{i},{i}] = {self.matrix[i, i]:.6e} N·s/m")
                    count += 1
            if n > 15:
                equations.append(f"\n  ... ({n - 15} more elements)")

        else:
            # Generic matrix
            equations.append(f"Matrix [{self.name}] elements:")
            equations.append("─" * 60 + "\n")
            count = 0
            for i in range(n):
                for j in range(m):
                    if self.matrix[i, j] != 0 and count < 20:
                        equations.append(f"  [{self.name}][{i},{j}] = {self.matrix[i, j]:.6e}")
                        count += 1
                    if count >= 20:
                        break
                if count >= 20:
                    break
            if np.count_nonzero(self.matrix) > 20:
                equations.append(f"\n  ... ({np.count_nonzero(self.matrix) - 20} more entries)")

        # Footer with matrix properties
        equations.append("\n" + "═" * 70)
        equations.append("MATRIX PROPERTIES:")
        equations.append("═" * 70)
        equations.append(f"  • Shape: {n} × {m}")
        equations.append(f"  • Non-zero elements: {np.count_nonzero(self.matrix)} / {n*m} ({100*np.count_nonzero(self.matrix)/(n*m):.1f}%)")

        if n == m:
            try:
                is_sym = np.allclose(self.matrix, self.matrix.T, rtol=1e-10)
                equations.append(f"  • Symmetric: {'✓ Yes' if is_sym else '✗ No'}")
            except:
                pass

            try:
                is_pos_def = np.all(np.linalg.eigvalsh(self.matrix) > 0)
                equations.append(f"  • Positive definite: {'✓ Yes' if is_pos_def else '✗ No'}")
            except:
                pass

            try:
                cond = np.linalg.cond(self.matrix)
                if np.isfinite(cond):
                    equations.append(f"  • Condition number: {cond:.2e}")
                    if cond > 1e10:
                        equations.append("    ⚠️  WARNING: Matrix is ill-conditioned!")
            except:
                pass

            try:
                rank = np.linalg.matrix_rank(self.matrix)
                equations.append(f"  • Rank: {rank} / {n}")
            except:
                pass

        equations.append("═" * 70)

        self.equations_text.setPlainText("\n".join(equations))

    def _populate_element_contributions(self):
        """Show actual element contributions to each matrix entry."""
        if self.model is None:
            self.equations_text.setPlainText(
                "Model information not available.\n\n"
                "Element contributions can only be shown when the model is provided."
            )
            return

        contributions = []
        n, m = self.matrix.shape

        # Header
        contributions.append("═══════════════════════════════════════════")
        contributions.append(f"  [{self.name}] Matrix - Element Contributions")
        contributions.append(f"  Dimensions: {n} × {m}")
        contributions.append("═══════════════════════════════════════════\n")

        # Get active elements (exclude ground)
        from bolt_analysis_studio.core.models.element import ElementType
        active_elements = [e for e in self.model.elements if e.type != ElementType.GROUND]

        if not active_elements:
            contributions.append("No active elements in model.")
            self.equations_text.setPlainText("\n".join(contributions))
            return

        # Show non-zero entries with element breakdown
        contributions.append("Non-zero entries with element contributions:\n")
        contributions.append("─" * 70)

        count = 0
        max_entries = 30  # Limit display to avoid overwhelming

        for i in range(n):
            for j in range(m):
                if self.matrix[i, j] != 0 and count < max_entries:
                    value = self.matrix[i, j]

                    # Determine which elements contribute to this entry
                    elem_contributions = []

                    if self.name == "M":
                        # Mass matrix - diagonal only
                        if i == j and i < len(active_elements):
                            elem = active_elements[i]
                            elem_contributions.append(f"  {elem.name}: m = {elem.msd.m:.3e} kg")

                    elif self.name == "K":
                        # Stiffness matrix - tridiagonal pattern
                        if i == j:
                            # Diagonal: k_i + k_{i+1}
                            if i < len(active_elements):
                                elem = active_elements[i]
                                elem_contributions.append(f"  {elem.name}: k = {elem.msd.k:.3e} N/m")
                            if i + 1 < len(active_elements):
                                elem = active_elements[i + 1]
                                elem_contributions.append(f"  {elem.name}: k = {elem.msd.k:.3e} N/m")
                        elif abs(i - j) == 1:
                            # Off-diagonal: -k_{max(i,j)}
                            idx = max(i, j)
                            if idx < len(active_elements):
                                elem = active_elements[idx]
                                elem_contributions.append(f"  {elem.name}: -k = -{elem.msd.k:.3e} N/m")

                    elif self.name == "C":
                        # Damping matrix - similar to stiffness
                        if i == j:
                            if i < len(active_elements):
                                elem = active_elements[i]
                                elem_contributions.append(f"  {elem.name}: c = {elem.msd.c:.3e} N·s/m")
                            if i + 1 < len(active_elements):
                                elem = active_elements[i + 1]
                                elem_contributions.append(f"  {elem.name}: c = {elem.msd.c:.3e} N·s/m")
                        elif abs(i - j) == 1:
                            idx = max(i, j)
                            if idx < len(active_elements):
                                elem = active_elements[idx]
                                elem_contributions.append(f"  {elem.name}: -c = -{elem.msd.c:.3e} N·s/m")

                    # Format output
                    contributions.append(f"\n[{self.name}][{i},{j}] = {value:.6e}")
                    if elem_contributions:
                        contributions.append("Contributing elements:")
                        contributions.extend(elem_contributions)
                    else:
                        contributions.append("  (Combined or complex contribution)")

                    count += 1

        if count >= max_entries and np.count_nonzero(self.matrix) > max_entries:
            contributions.append(f"\n... ({np.count_nonzero(self.matrix) - max_entries} more non-zero entries)")

        # Summary
        contributions.append("\n─" * 70)
        contributions.append("Element Summary:")
        contributions.append("─" * 70)
        for i, elem in enumerate(active_elements[:15]):  # Show first 15
            contributions.append(f"  DOF {i}: {elem.name}")
            contributions.append(f"         k = {elem.msd.k:.3e} N/m, "
                                f"c = {elem.msd.c:.3e} N·s/m, "
                                f"m = {elem.msd.m:.3e} kg")

        if len(active_elements) > 15:
            contributions.append(f"  ... and {len(active_elements) - 15} more elements")

        contributions.append("\n═══════════════════════════════════════════")

        self.equations_text.setPlainText("\n".join(contributions))

    def _update_table_format(self):
        """Update table format when combo changes."""
        if self.display_combo.currentText() == "Values Table":
            self._populate_table()

    def _copy_to_clipboard(self):
        """Copy matrix to clipboard."""
        text = np.array2string(self.matrix, separator='\t', threshold=np.inf)
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def _export_csv(self):
        """Export matrix to CSV file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, f"Export {self.name} Matrix", f"{self.name}_matrix.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        if filename:
            np.savetxt(filename, self.matrix, delimiter=',', fmt='%.6e')


# =============================================================================
# MATRIX VIEWER DIALOG
# =============================================================================

class MatrixViewerDialog(QDialog):
    """Main dialog for viewing assembled matrices."""

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Matrix Viewer - Bolt Analysis Studio")
        self.setMinimumSize(900, 600)
        self._setup_ui()

    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header
        header = QLabel(f"Model: {self.model.name} | DOF: {self.model.n_dof}")
        header.setStyleSheet(f"""
            font-size: 14pt;
            font-weight: bold;
            color: {Theme.BLUE};
            padding: 8px;
            background-color: {Theme.SURFACE0};
            border-radius: 4px;
        """)
        layout.addWidget(header)

        # Assemble matrices
        try:
            M, K, C = self.model.assemble_matrices()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to assemble matrices: {e}")
            M = K = C = np.array([[]])

        # Create force vector from model.global_loading
        n = self.model.n_dof
        F = np.zeros(n)
        if n > 0 and hasattr(self.model, 'global_loading') and self.model.global_loading is not None:
            loading = self.model.global_loading
            # Preload applied at bolt head DOF (typically DOF 0)
            F[0] = loading.F_preload
            # External axial force (if any)
            if hasattr(loading, 'F_external') and loading.F_external != 0:
                F[0] += loading.F_external
            # Transverse force at interface DOF (typically middle of joint, DOF n//2)
            if n > 1 and hasattr(loading, 'F_transverse') and loading.F_transverse != 0:
                interface_dof = min(n // 2, n - 1)
                F[interface_dof] = loading.F_transverse

        # Tab widget for matrices
        tabs = QTabWidget()

        # Mass matrix tab
        m_tab = MatrixTab(M, "M", model=self.model, parent=self)
        tabs.addTab(m_tab, "[M] Mass Matrix")

        # Stiffness matrix tab
        k_tab = MatrixTab(K, "K", model=self.model, parent=self)
        tabs.addTab(k_tab, "[K] Stiffness Matrix")

        # Damping matrix tab
        c_tab = MatrixTab(C, "C", model=self.model, parent=self)
        tabs.addTab(c_tab, "[C] Damping Matrix")

        # Force vector tab
        f_tab = self._create_force_tab(F)
        tabs.addTab(f_tab, "{F} Force Vector")

        # Modal analysis tab
        modal_tab = self._create_modal_tab(M, K)
        tabs.addTab(modal_tab, "Modal Analysis")

        layout.addWidget(tabs, stretch=1)

        # Store reference for live updates (Fix LOW-04)
        self._tabs_widget = tabs

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def refresh_from_model(self, model):
        """Refresh the Force Vector tab when the model changes (LOW-04 live update)."""
        if not self.isVisible():
            return
        try:
            self.model = model
            # Rebuild the force vector
            n = model.n_dof
            F = np.zeros(n)
            if n > 0 and hasattr(model, 'global_loading') and model.global_loading is not None:
                loading = model.global_loading
                F[0] = loading.F_preload
                if hasattr(loading, 'F_external') and loading.F_external != 0:
                    F[0] += loading.F_external
                if n > 1 and hasattr(loading, 'F_transverse') and loading.F_transverse != 0:
                    interface_dof = min(n // 2, n - 1)
                    F[interface_dof] = loading.F_transverse
            # Replace the {F} tab (index 3)
            new_f_tab = self._create_force_tab(F)
            self._tabs_widget.removeTab(3)
            self._tabs_widget.insertTab(3, new_f_tab, "{F} Force Vector")
            self._tabs_widget.setCurrentIndex(3)
        except Exception:
            pass

    def _create_force_tab(self, F: np.ndarray) -> QWidget:
        """Create the force vector tab with comprehensive force breakdown.

        Uses a QScrollArea so the bar chart and configuration groups are
        all accessible even on smaller screens.
        """
        tab = QWidget()
        outer_layout = QVBoxLayout(tab)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(8)

        # --- Applied Loads Breakdown (primary chart - physical loads) ---
        if hasattr(self.model, 'global_loading') and self.model.global_loading is not None:
            _gl = self.model.global_loading
            _items = []  # (label, value, bar_color, unit_str)

            _fp = getattr(_gl, 'F_preload',    0)
            _ft = getattr(_gl, 'F_transverse', 0)
            _fe = getattr(_gl, 'F_external',   0)
            _ta = getattr(_gl, 'T_applied',    0)
            _dt = getattr(_gl, 'delta_T',      0)

            if _fp > 0:
                _items.append(("Preload\n(F\u2080)",     _fp / 1000,  Theme.BLUE,  "kN"))
            if _ft > 0:
                _items.append(("Transverse\n(F_T)",      _ft / 1000,  Theme.GREEN, "kN"))
            if _fe != 0:
                _items.append(("External\n(F_ext)",      abs(_fe)/1000, Theme.PEACH,  "kN"))
            if _ta != 0:
                _items.append(("Torque\n(T)",             abs(_ta),    Theme.PINK,  "N\u00b7m"))
            if _dt != 0:
                _items.append(("Thermal\n(\u0394T)",      abs(_dt),    Theme.MAUVE, "\u00b0C"))

            if _items:
                _lc = MatrixCanvas(content, width=8, height=3)
                _lc.setMinimumHeight(210)
                _lc.setSizePolicy(QSizePolicy.Policy.Expanding,
                                  QSizePolicy.Policy.MinimumExpanding)
                _ax = _lc.axes
                _ax.clear()
                _names  = [d[0] for d in _items]
                _vals   = [d[1] for d in _items]
                _colors = [d[2] for d in _items]
                _units  = [d[3] for d in _items]
                _bars   = _ax.bar(range(len(_names)), _vals,
                                  color=_colors, alpha=0.82,
                                  edgecolor=Theme.SURFACE2, linewidth=0.8)
                _ax.set_xticks(range(len(_names)))
                _ax.set_xticklabels(_names, fontsize=8, color=Theme.TEXT)
                _ax.set_ylabel("Magnitude", fontsize=8, color=Theme.TEXT)
                _ax.set_title("Applied Loads", fontsize=9,
                              color=Theme.TEXT, fontweight='bold', pad=4)
                _ax.set_facecolor(Theme.SURFACE0)
                _ax.tick_params(colors=Theme.TEXT, labelsize=7)
                _mx = max(_vals) if _vals else 1.0
                for _b, _v, _u in zip(_bars, _vals, _units):
                    _ax.text(_b.get_x() + _b.get_width() / 2,
                             _b.get_height() + _mx * 0.04,
                             f"{_v:.1f} {_u}",
                             ha='center', va='bottom',
                             fontsize=7, color=Theme.TEXT, fontweight='bold')
                try:
                    _lc.fig.tight_layout(pad=0.5)
                except Exception:
                    pass
                _lc.draw()

                _lg = QGroupBox("Applied Loads Breakdown")
                _ll = QVBoxLayout(_lg)
                _ll.setContentsMargins(4, 4, 4, 4)
                _ll.addWidget(_lc)
                layout.addWidget(_lg)

        # --- Assembled DOF force vector {F} ---
        canvas = MatrixCanvas(content, width=8, height=4)
        canvas.setMinimumHeight(280)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding,
                             QSizePolicy.Policy.MinimumExpanding)
        canvas.plot_bar(F, "Assembled Force Vector {F} (per DOF)")
        layout.addWidget(canvas)

        # --- Per-DOF force table ---
        if F.size > 0 and not np.all(F == 0):
            from bolt_analysis_studio.core.models.element import ElementType

            table_group = QGroupBox("Force per DOF")
            table_layout = QVBoxLayout(table_group)

            active_elems = [e for e in self.model.elements
                           if e.type != ElementType.GROUND]

            table = QTableWidget(len(F), 3)
            table.setHorizontalHeaderLabels(["DOF", "Element", "Force (N)"])
            table.horizontalHeader().setStretchLastSection(True)
            table.setMaximumHeight(min(200, 28 * (len(F) + 1)))

            for i, val in enumerate(F):
                dof_item = QTableWidgetItem(str(i))
                elem_name = (active_elems[i].name
                             if i < len(active_elems) else f"DOF {i}")
                name_item = QTableWidgetItem(elem_name)
                force_item = QTableWidgetItem(f"{val:,.2f}")

                # Highlight non-zero forces
                if abs(val) > 1e-6:
                    color = QColor(Theme.GREEN) if val > 0 else QColor(Theme.RED)
                    force_item.setForeground(color)

                table.setItem(i, 0, dof_item)
                table.setItem(i, 1, name_item)
                table.setItem(i, 2, force_item)

            table.resizeColumnsToContents()
            table_layout.addWidget(table)
            layout.addWidget(table_group)

        # --- Force summary statistics ---
        summary = QGroupBox("Force Summary")
        summary_layout = QFormLayout(summary)

        n_dof_label = QLabel(f"{len(F)}")
        total_label = QLabel(f"{np.sum(F):,.2f} N")
        max_val = np.max(np.abs(F)) if F.size > 0 else 0.0
        max_label = QLabel(f"{max_val:,.2f} N")
        nonzero = int(np.count_nonzero(F))
        nonzero_label = QLabel(f"{nonzero} of {len(F)}")

        summary_layout.addRow("DOF count:", n_dof_label)
        summary_layout.addRow("Non-zero DOFs:", nonzero_label)
        summary_layout.addRow("Total force:", total_label)
        summary_layout.addRow("Max magnitude:", max_label)

        layout.addWidget(summary)

        # --- Loading configuration from model ---
        if hasattr(self.model, 'global_loading') and self.model.global_loading is not None:
            loading = self.model.global_loading
            config_group = QGroupBox("Loading Configuration (from MSD Builder)")
            config_layout = QFormLayout(config_group)

            # Load type
            load_type = loading.type.name if hasattr(loading.type, 'name') else str(loading.type)
            type_label = QLabel(load_type)
            type_label.setStyleSheet(f"color: {Theme.BLUE}; font-weight: bold;")
            config_layout.addRow("Type:", type_label)

            # Preload
            preload_label = QLabel(f"{loading.F_preload:,.0f} N")
            if loading.F_preload == 0:
                preload_label.setStyleSheet(f"color: {Theme.RED}; font-weight: bold;")
            config_layout.addRow("Preload (F_0):", preload_label)

            # Transverse force
            trans_force = getattr(loading, 'F_transverse', 0)
            trans_label = QLabel(f"{trans_force:,.0f} N")
            config_layout.addRow("Transverse (F_trans):", trans_label)

            # Transverse displacement
            trans_disp = getattr(loading, 'delta_amplitude', 0)
            disp_label = QLabel(f"{trans_disp:.3f} mm")
            config_layout.addRow("Trans. Displacement:", disp_label)

            # External force
            ext_force = getattr(loading, 'F_external', 0)
            ext_label = QLabel(f"{ext_force:,.0f} N")
            config_layout.addRow("External (F_ext):", ext_label)

            # Applied torque
            torque = getattr(loading, 'T_applied', 0)
            torque_label = QLabel(f"{torque:.1f} N·m")
            config_layout.addRow("Torque (T):", torque_label)

            # Temperature change
            delta_T = getattr(loading, 'delta_T', 0)
            temp_label = QLabel(f"{delta_T:.0f} °C")
            config_layout.addRow("DT:", temp_label)

            # Frequency and cycles
            freq = getattr(loading, 'frequency', 0)
            cycles = getattr(loading, 'n_cycles', 0)
            freq_label = QLabel(f"{freq:.1f} Hz, {cycles:,} cycles")
            config_layout.addRow("Loading:", freq_label)

            layout.addWidget(config_group)

            # Friction parameters (if available on model)
            if hasattr(self.model, 'mu_initial'):
                friction_group = QGroupBox("Friction Parameters")
                friction_layout = QFormLayout(friction_group)

                mu = getattr(self.model, 'mu_initial', 0.12)
                mu_label = QLabel(f"{mu:.3f}")
                friction_layout.addRow("Initial mu:", mu_label)

                lubricated = getattr(self.model, 'lubricated', True)
                lub_label = QLabel("Yes" if lubricated else "No")
                friction_layout.addRow("Lubricated:", lub_label)

                bolt_dia = getattr(self.model, 'bolt_diameter', 16.0)
                pitch = getattr(self.model, 'pitch', 2.0)
                bolt_label = QLabel(f"M{bolt_dia:.0f} x {pitch:.1f}")
                friction_layout.addRow("Bolt:", bolt_label)

                layout.addWidget(friction_group)

        layout.addStretch()
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)
        return tab

    def _create_modal_tab(self, M: np.ndarray, K: np.ndarray) -> QWidget:
        """Create the modal analysis tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Calculate natural frequencies and mode shapes
        try:
            frequencies = self.model.compute_natural_frequencies()
            freqs, modes = self.model.compute_mode_shapes()
            # Filter out NaN/Inf values
            if len(frequencies) > 0:
                mask = np.isfinite(frequencies)
                frequencies = frequencies[mask]
            if len(freqs) > 0:
                mask = np.isfinite(freqs)
                freqs = freqs[mask]
                if modes.size > 0 and modes.shape[1] > 0:
                    modes = modes[:, mask]
        except Exception:
            frequencies = np.array([])
            freqs = np.array([])
            modes = np.array([[]])

        # Frequencies display
        freq_group = QGroupBox("Natural Frequencies")
        freq_layout = QVBoxLayout(freq_group)

        if len(frequencies) > 0:
            freq_text = QTextEdit()
            freq_text.setReadOnly(True)
            freq_text.setMaximumHeight(150)

            text = "Mode\tFrequency (Hz)\tPeriod (s)\n"
            text += "-" * 40 + "\n"
            for i, f in enumerate(frequencies[:10]):  # Show first 10
                T = 1/f if f > 0 else float('inf')
                text += f"{i+1}\t{f:.2f}\t\t{T:.4f}\n"

            freq_text.setPlainText(text)
            freq_text.setStyleSheet(f"font-family: {Theme.FONT_MONO}; color: {Theme.TEXT}; background: {Theme.SURFACE0};")
            freq_layout.addWidget(freq_text)
        else:
            freq_layout.addWidget(QLabel("No natural frequencies computed"))

        layout.addWidget(freq_group)

        # Mode shapes plot
        modes_group = QGroupBox("Mode Shapes")
        modes_layout = QVBoxLayout(modes_group)

        canvas = MatrixCanvas(tab, width=6, height=4)

        if modes.size > 0 and modes.shape[1] > 0:
            canvas.axes.clear()
            canvas.axes.set_facecolor(Theme.SURFACE0)

            n_modes = min(4, modes.shape[1])
            x = np.arange(modes.shape[0])

            colors = [Theme.BLUE, Theme.GREEN, Theme.PEACH, Theme.MAUVE]
            for i in range(n_modes):
                canvas.axes.plot(x, modes[:, i], 'o-', color=colors[i],
                               label=f'Mode {i+1}: {freqs[i]:.1f} Hz')

            canvas.axes.set_xlabel("DOF", color=Theme.SUBTEXT)
            canvas.axes.set_ylabel("Normalized Amplitude", color=Theme.SUBTEXT)
            canvas.axes.set_title("Mode Shapes", color=Theme.TEXT, fontweight='bold')
            canvas.axes.legend(facecolor=Theme.SURFACE0, edgecolor=Theme.SURFACE2,
                             labelcolor=Theme.TEXT)
            canvas.axes.tick_params(colors=Theme.TEXT)
            canvas.axes.grid(True, alpha=0.3)
            canvas._safe_tight_layout()
            canvas.draw()
        else:
            canvas.axes.text(0.5, 0.5, "No mode shapes computed",
                           ha='center', va='center', color=Theme.TEXT)
            canvas.draw()

        modes_layout.addWidget(canvas)
        layout.addWidget(modes_group, stretch=1)

        return tab


# =============================================================================
# STANDALONE TEST
# =============================================================================

def main():
    """Test the matrix viewer."""
    app = QApplication(sys.argv)

    # Apply dark theme
    app.setStyleSheet(f"""
        QDialog, QWidget {{
            background-color: {Theme.BASE};
            color: {Theme.TEXT};
            font-family: {Theme.FONT_SANS};
        }}
        QGroupBox {{
            border: 1px solid {Theme.SURFACE1};
            border-radius: 6px;
            margin-top: 12px;
            padding: 10px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            color: {Theme.BLUE};
        }}
        QPushButton {{
            background-color: {Theme.SURFACE1};
            border: 1px solid {Theme.SURFACE2};
            border-radius: 4px;
            padding: 6px 12px;
        }}
        QPushButton:hover {{
            background-color: {Theme.SURFACE2};
            border-color: {Theme.BLUE};
        }}
        QComboBox {{
            background-color: {Theme.SURFACE1};
            border: 1px solid {Theme.SURFACE2};
            border-radius: 4px;
            padding: 4px 8px;
        }}
        QTabWidget::pane {{
            border: 1px solid {Theme.SURFACE1};
            border-radius: 4px;
        }}
        QTabBar::tab {{
            background-color: {Theme.SURFACE0};
            border: 1px solid {Theme.SURFACE1};
            padding: 8px 16px;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background-color: {Theme.SURFACE1};
            border-bottom-color: {Theme.BLUE};
        }}
        QTableWidget {{
            background-color: {Theme.SURFACE0};
            gridline-color: {Theme.SURFACE1};
        }}
        QHeaderView::section {{
            background-color: {Theme.SURFACE1};
            padding: 4px;
            border: 1px solid {Theme.SURFACE2};
        }}
    """)

    # Create a test model
    from bolt_analysis_studio.core.models.model import create_single_bolt_joint

    model = create_single_bolt_joint(
        diameter=12.0,
        pitch=1.75,
        grip_length=50.0,
        shank_length=30.0,
        preload=50000.0,
        name="Test Bolt Joint"
    )

    dialog = MatrixViewerDialog(model)
    dialog.exec()


if __name__ == "__main__":
    main()
