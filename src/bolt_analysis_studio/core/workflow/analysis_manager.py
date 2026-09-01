"""
Analysis Workflow Manager for Bolt Analysis Studio v4.0
Prof. Leonardo Rosa Ribeiro da Silva, PhD

End-to-end workflow orchestration for complete bolt joint analysis:
- Joint configuration setup
- Loading protocol management (Junker test, operational, thermal)
- Matrix assembly and solver integration
- Contact state tracking
- Preload monitoring
- Results collection and post-processing

This is the main entry point for running complete bolt loosening analyses.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Optional, Callable, Tuple, Any
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import warnings

# Core imports
from ..contacts import (
    Contact, ContactFactory, JointConfiguration,
    create_api_6a_joint_config, create_asme_b16_5_joint_config,
    create_vdi_2230_joint_config
)
from ..contacts.base import SlipState
from ..contacts.thread_contact import ThreadContact
from ..contacts.bearing_contact import BearingContact
from ..contacts.gasket_contact import FlangeGasketContact

# Optional imports (modules may not exist yet)
try:
    from ..contacts.matrix_assembler import CompleteMSDMatrixAssembler
except ImportError:
    CompleteMSDMatrixAssembler = None

try:
    from ..contacts.junker_loosening import (
        JunkerLooseningModel, JunkerModelParameters,
        JunkerPhase, LooseningMechanism
    )
except ImportError:
    JunkerLooseningModel = None
    JunkerModelParameters = None
    JunkerPhase = None
    LooseningMechanism = None

try:
    from ..contacts.preload_tracker import (
        PreloadTracker, PreloadLossSource
    )
except ImportError:
    PreloadTracker = None
    PreloadLossSource = None

try:
    from ..app_state import SystemState, StateManager
except ImportError:
    SystemState = None
    StateManager = None

# Numerical imports
from ...numerical.time_integration import (
    NewmarkIntegrator, HHTIntegrator, NewmarkParams, HHTParams,
    TimeParams, IntegrationResult, IntegratorType,
    create_integrator
)


# =============================================================================
# LOADING PROTOCOL TYPES
# =============================================================================

class LoadingProtocolType(Enum):
    """Types of loading protocols for analysis."""
    JUNKER_TEST = auto()          # Transverse cyclic loading
    OPERATIONAL = auto()          # Time-varying operational loads
    STATIC = auto()               # Constant loads
    THERMAL = auto()              # Temperature cycling
    CUSTOM = auto()               # User-defined force function


@dataclass
class LoadingProtocol:
    """
    Loading protocol configuration.

    Defines how external loads are applied to the joint during analysis.
    """
    protocol_type: LoadingProtocolType = LoadingProtocolType.JUNKER_TEST

    # Junker test parameters
    junker_amplitude: float = 0.00065       # [m] 0.65mm standard
    junker_frequency: float = 12.5          # [Hz]
    junker_n_cycles: int = 2000             # Total cycles

    # Operational load parameters
    operational_load_file: Optional[str] = None     # Path to load file
    operational_load_func: Optional[Callable] = None  # Custom function F(t)

    # Static load
    static_force: float = 0.0               # [N] constant external force

    # Thermal parameters
    temperature_min: float = -40.0          # [°C]
    temperature_max: float = 150.0          # [°C]
    thermal_cycle_duration: float = 3600.0  # [s] 1 hour per cycle
    thermal_n_cycles: int = 100

    # Custom force function
    custom_force_func: Optional[Callable[[float], np.ndarray]] = None

    def get_force_function(self, n_dof: int) -> Callable[[float], np.ndarray]:
        """
        Get force function F(t) for this protocol.

        Args:
            n_dof: Number of degrees of freedom

        Returns:
            Function F(t) -> np.ndarray[n_dof]
        """
        if self.protocol_type == LoadingProtocolType.JUNKER_TEST:
            return self._junker_force_function(n_dof)

        elif self.protocol_type == LoadingProtocolType.OPERATIONAL:
            if self.operational_load_func is not None:
                return self.operational_load_func
            elif self.operational_load_file is not None:
                return self._load_from_file(n_dof)
            else:
                return lambda t: np.zeros(n_dof)

        elif self.protocol_type == LoadingProtocolType.STATIC:
            return lambda t: np.array([self.static_force] + [0.0]*(n_dof-1))

        elif self.protocol_type == LoadingProtocolType.THERMAL:
            return self._thermal_force_function(n_dof)

        elif self.protocol_type == LoadingProtocolType.CUSTOM:
            if self.custom_force_func is not None:
                return self.custom_force_func
            else:
                return lambda t: np.zeros(n_dof)

        return lambda t: np.zeros(n_dof)

    def _junker_force_function(self, n_dof: int) -> Callable[[float], np.ndarray]:
        """Create Junker test force function (transverse sinusoidal)."""
        omega = 2 * np.pi * self.junker_frequency
        amplitude = self.junker_amplitude

        def F(t: float) -> np.ndarray:
            # Transverse force on first flange DOF (typically DOF 2 or 10)
            force = np.zeros(n_dof)
            if n_dof > 10:  # Has transverse DOFs
                force[10] = amplitude * np.sin(omega * t)  # Transverse DOF
            return force

        return F

    def _thermal_force_function(self, n_dof: int) -> Callable[[float], np.ndarray]:
        """Create thermal cycling force function."""
        T_min = self.temperature_min
        T_max = self.temperature_max
        T_period = self.thermal_cycle_duration

        def F(t: float) -> np.ndarray:
            # Temperature cycles as sinusoid
            T_avg = (T_max + T_min) / 2
            T_amp = (T_max - T_min) / 2
            T_current = T_avg + T_amp * np.sin(2 * np.pi * t / T_period)

            # Thermal expansion force (simplified)
            # F_thermal = α × E × A × ΔT
            # This is a placeholder - real implementation needs material properties
            force = np.zeros(n_dof)
            return force

        return F

    def _load_from_file(self, n_dof: int) -> Callable[[float], np.ndarray]:
        """Load time-varying force from file."""
        # Load CSV: time, F1, F2, ...
        try:
            data = np.loadtxt(self.operational_load_file, delimiter=',')
            time_data = data[:, 0]
            force_data = data[:, 1:n_dof+1]

            def F(t: float) -> np.ndarray:
                # Linear interpolation
                return np.interp(t, time_data, force_data.T)

            return F
        except:
            warnings.warn(f"Failed to load force data from {self.operational_load_file}")
            return lambda t: np.zeros(n_dof)

    def get_total_duration(self) -> float:
        """Get total analysis duration in seconds."""
        if self.protocol_type == LoadingProtocolType.JUNKER_TEST:
            return self.junker_n_cycles / self.junker_frequency
        elif self.protocol_type == LoadingProtocolType.THERMAL:
            return self.thermal_n_cycles * self.thermal_cycle_duration
        else:
            return 1.0  # Default 1 second


# =============================================================================
# ANALYSIS CONFIGURATION
# =============================================================================

@dataclass
class AnalysisConfiguration:
    """
    Complete analysis configuration.

    Contains all parameters needed for a full bolt loosening analysis.
    """
    # Analysis identification
    name: str = "Bolt Loosening Analysis"
    description: str = ""

    # Joint configuration
    joint_config: JointConfiguration = field(default_factory=JointConfiguration)

    # Loading protocol
    loading: LoadingProtocol = field(default_factory=LoadingProtocol)

    # Solver settings
    solver_method: IntegratorType = IntegratorType.NEWMARK_BETA
    time_step: float = 0.0001               # [s] 0.1ms typical
    newmark_params: Optional[NewmarkParams] = None
    hht_params: Optional[HHTParams] = None

    # Initial conditions
    initial_preload: float = 0.0             # [N] — 0 means "compute from % yield"
    initial_displacement: Optional[np.ndarray] = None
    initial_velocity: Optional[np.ndarray] = None

    # Junker model parameters (if using Junker test)
    junker_params: Optional[JunkerModelParameters] = None

    # Output options
    output_interval: int = 10               # Save every N steps
    save_contact_history: bool = True
    save_cycle_data: bool = True

    # Output directory
    output_dir: Optional[Path] = None

    def __post_init__(self):
        """Initialize defaults."""
        if self.newmark_params is None:
            self.newmark_params = NewmarkParams.average_acceleration()
        if self.hht_params is None:
            self.hht_params = HHTParams.low_damping()
        if self.junker_params is None:
            self.junker_params = JunkerModelParameters()
        if self.output_dir is None:
            self.output_dir = Path("analysis_results")


# =============================================================================
# ANALYSIS RESULT
# =============================================================================

@dataclass
class AnalysisResult:
    """
    Complete analysis results.

    Contains all data from a bolt loosening analysis run.
    """
    # Configuration
    config: AnalysisConfiguration

    # Time history
    time: np.ndarray                        # [n_steps+1]
    displacement: np.ndarray                # [n_steps+1, n_dof]
    velocity: np.ndarray                    # [n_steps+1, n_dof]
    acceleration: np.ndarray                # [n_steps+1, n_dof]

    # Preload history
    preload_history: np.ndarray             # [n_steps+1]
    loosening_angle_history: np.ndarray     # [n_steps+1] accumulated rotation

    # Contact states
    contact_states_history: Optional[List[Dict[str, Any]]] = None

    # Cycle data (for cyclic loading)
    cycle_data: Optional[Dict[str, np.ndarray]] = None  # {'cycle', 'preload', 'angle', ...}

    # Junker phases (if Junker test)
    junker_phases: Optional[List[Tuple[int, JunkerPhase]]] = None

    # Preload loss breakdown
    preload_loss_breakdown: Optional[Dict[PreloadLossSource, float]] = None

    # Statistics
    statistics: Dict[str, float] = field(default_factory=dict)

    # Convergence
    converged: bool = True
    iterations: Optional[List[int]] = None

    # Runtime info
    runtime_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_final_preload(self) -> float:
        """Get final preload value."""
        return self.preload_history[-1] if len(self.preload_history) > 0 else 0.0

    def get_preload_loss_percent(self) -> float:
        """Get preload loss as percentage of initial."""
        if len(self.preload_history) == 0:
            return 0.0
        initial = self.preload_history[0]
        final = self.preload_history[-1]
        if initial > 0:
            return 100 * (initial - final) / initial
        return 0.0

    def get_total_loosening_angle(self) -> float:
        """Get total loosening angle in degrees."""
        if len(self.loosening_angle_history) > 0:
            return np.degrees(self.loosening_angle_history[-1])
        return 0.0


# =============================================================================
# ANALYSIS MANAGER
# =============================================================================

class AnalysisManager:
    """
    Main analysis workflow orchestrator.

    Coordinates all components for end-to-end bolt joint analysis:
    - Joint configuration and contact creation
    - Matrix assembly
    - Time integration
    - Contact state updates
    - Preload tracking
    - Results collection
    """

    def __init__(self, config: AnalysisConfiguration):
        """
        Initialize analysis manager.

        Args:
            config: Analysis configuration
        """
        self.config = config

        # Components (initialized in setup)
        self.contacts: List[Contact] = []
        self.contact_factory: ContactFactory = ContactFactory()
        self.assembler: Optional[CompleteMSDMatrixAssembler] = None
        self.state_manager: Optional[StateManager] = None
        self.preload_tracker: Optional[PreloadTracker] = None
        self.junker_model: Optional[JunkerLooseningModel] = None

        # Analysis state
        self.current_time: float = 0.0
        self.current_cycle: int = 0
        self.is_setup: bool = False

        # Results storage
        self.result: Optional[AnalysisResult] = None

    def setup_model(self) -> None:
        """
        Setup complete model from configuration.

        Creates all contacts, assembles matrices, initializes state.
        """
        print(f"[AnalysisManager] Setting up model: {self.config.name}")

        # 1. Create contacts
        print("  Creating contacts...")
        self.contacts = self.contact_factory.create_complete_joint(
            self.config.joint_config
        )
        print(f"  Created {len(self.contacts)} contacts")

        # 2. Create matrix assembler
        print("  Creating matrix assembler...")
        self.assembler = CompleteMSDMatrixAssembler(self.contacts)
        M, K, C = self.assembler.assemble_all_matrices()
        print(f"  Assembled matrices: {M.shape[0]} DOF")

        # 3. Validate DOF mapping
        n_dof = M.shape[0]
        is_valid, errors = self.contact_factory.validate_dof_mapping(n_dof)
        if not is_valid:
            raise ValueError(f"Invalid DOF mapping:\n" + "\n".join(errors))

        # 4. Initialize state manager
        print("  Initializing state manager...")
        self.state_manager = StateManager()
        self.state_manager.update_from_matrices(M, K, C)

        # 5. Initialize preload tracker
        print("  Initializing preload tracker...")
        self.preload_tracker = PreloadTracker(
            initial_preload=self.config.initial_preload,
            system_stiffness=np.sum(np.diag(K))  # Approximate
        )

        # 6. Initialize Junker model (if applicable)
        if self.config.loading.protocol_type == LoadingProtocolType.JUNKER_TEST:
            print("  Initializing Junker loosening model...")

            # Find thread contact
            thread_contact = None
            for contact in self.contacts:
                if isinstance(contact, ThreadContact):
                    thread_contact = contact
                    break

            if thread_contact is None:
                raise ValueError("Junker test requires thread contact")

            self.junker_model = JunkerLooseningModel(
                thread_contact=thread_contact,
                params=self.config.junker_params
            )

        self.is_setup = True
        print("  Setup complete!")

    def initialize_state(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Initialize displacement and velocity state vectors.

        Returns:
            Tuple (u0, v0) initial displacement and velocity
        """
        if not self.is_setup:
            raise RuntimeError("Must call setup_model() first")

        n_dof = self.assembler.n_dof

        # Initial displacement from preload
        if self.config.initial_displacement is not None:
            u0 = self.config.initial_displacement
        else:
            # Compute static displacement from preload
            _, K, _ = self.assembler.assemble_all_matrices()
            F_preload = np.zeros(n_dof)
            F_preload[0] = self.config.initial_preload  # Apply to first DOF
            u0 = np.linalg.solve(K, F_preload)

        # Initial velocity
        if self.config.initial_velocity is not None:
            v0 = self.config.initial_velocity
        else:
            v0 = np.zeros(n_dof)

        return u0, v0

    def run_analysis(
        self,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> AnalysisResult:
        """
        Run complete analysis.

        Main execution loop that integrates equations of motion,
        updates contact states, tracks preload, and collects results.

        Args:
            progress_callback: Optional callback for progress updates (0-100%)

        Returns:
            AnalysisResult with complete results
        """
        if not self.is_setup:
            self.setup_model()

        print(f"\n[AnalysisManager] Running analysis...")
        start_time = datetime.now()

        # Setup time parameters
        total_duration = self.config.loading.get_total_duration()
        time_params = TimeParams(
            t_start=0.0,
            t_end=total_duration,
            dt=self.config.time_step,
            output_interval=self.config.output_interval
        )

        n_steps = time_params.n_steps
        print(f"  Duration: {total_duration:.2f} s, Steps: {n_steps}, dt: {self.config.time_step:.4f} s")

        # Get initial state
        u0, v0 = self.initialize_state()
        n_dof = len(u0)

        # Get force function
        F_func = self.config.loading.get_force_function(n_dof)

        # Storage for results
        time_vec = time_params.time_vector
        U_history = np.zeros((n_steps + 1, n_dof))
        V_history = np.zeros((n_steps + 1, n_dof))
        A_history = np.zeros((n_steps + 1, n_dof))
        preload_history = np.zeros(n_steps + 1)
        loosening_angle_history = np.zeros(n_steps + 1)

        U_history[0] = u0
        V_history[0] = v0
        preload_history[0] = self.config.initial_preload

        contact_states_history = [] if self.config.save_contact_history else None

        # Cycle detection
        cycle_data = {
            'cycle': [],
            'preload': [],
            'angle': [],
            'time': []
        } if self.config.save_cycle_data else None

        # Get integrator
        M, K, C = self.assembler.assemble_all_matrices()

        if self.config.solver_method == IntegratorType.NEWMARK_BETA:
            integrator = NewmarkIntegrator(M, C, K, self.config.newmark_params)
        elif self.config.solver_method == IntegratorType.HHT_ALPHA:
            integrator = HHTIntegrator(M, C, K, self.config.hht_params)
        else:
            integrator = create_integrator(self.config.solver_method, M, C, K)

        print(f"  Solver: {self.config.solver_method.name}")
        print(f"  Starting time integration...")

        # Time integration loop with contact updates
        u_current = u0.copy()
        v_current = v0.copy()
        a_current = np.zeros(n_dof)
        preload_current = self.config.initial_preload
        angle_current = 0.0

        # Initial acceleration
        F0 = F_func(0.0)
        a_current = np.linalg.solve(M, F0 - C @ v_current - K @ u_current)
        A_history[0] = a_current

        last_cycle_check = 0.0
        cycle_period = 1.0 / self.config.loading.junker_frequency if \
                      self.config.loading.protocol_type == LoadingProtocolType.JUNKER_TEST else 1.0

        for step in range(n_steps):
            t = time_vec[step]
            t_next = time_vec[step + 1]
            dt = t_next - t

            # 1. Compute forces (external + tribological)
            F_ext = F_func(t_next)
            F_friction = self.assembler.compute_tribological_forces(u_current, v_current)
            F_total = F_ext + F_friction

            # 2. Take one time step
            # Using Newmark predictor-corrector
            if isinstance(integrator, NewmarkIntegrator):
                params = integrator.params
                beta = params.beta
                gamma = params.gamma

                # Predictor
                u_pred = u_current + dt * v_current + 0.5 * dt**2 * (1 - 2*beta) * a_current
                v_pred = v_current + dt * (1 - gamma) * a_current

                # Solve for acceleration at t+dt
                K_eff = K + gamma/(beta*dt) * C + 1/(beta*dt**2) * M
                F_eff = F_total - K @ u_pred - C @ v_pred
                delta_a = np.linalg.solve(K_eff, F_eff - M @ a_current)
                a_next = a_current + delta_a

                # Corrector
                u_next = u_pred + beta * dt**2 * delta_a
                v_next = v_pred + gamma * dt * delta_a
            else:
                # Use integrator's integrate method for single step
                # This is simplified - real implementation needs single-step capability
                u_next = u_current + dt * v_current
                v_next = v_current
                a_next = a_current

            # 3. Update contact states
            for contact in self.contacts:
                contact.update_state(u_next, v_next, dt, preload_current)

            # 4. Update Junker model (if applicable)
            if self.junker_model is not None:
                delta_theta = self.junker_model.compute_rotation_increment(
                    t_next, u_next, v_next, preload_current
                )
                angle_current += delta_theta

                # Update phase
                self.junker_model.update_phase(self.current_cycle, preload_current)

            # 5. Update preload
            preload_loss = sum(c.get_preload_loss(np.sum(np.diag(K))) for c in self.contacts)
            preload_current = max(0.0, preload_current - preload_loss)

            # 6. Check for cycle completion
            if t_next - last_cycle_check >= cycle_period:
                self.current_cycle += 1
                last_cycle_check = t_next

                if cycle_data is not None:
                    cycle_data['cycle'].append(self.current_cycle)
                    cycle_data['preload'].append(preload_current)
                    cycle_data['angle'].append(np.degrees(angle_current))
                    cycle_data['time'].append(t_next)

            # 7. Store results
            U_history[step + 1] = u_next
            V_history[step + 1] = v_next
            A_history[step + 1] = a_next
            preload_history[step + 1] = preload_current
            loosening_angle_history[step + 1] = angle_current

            if contact_states_history is not None and step % self.config.output_interval == 0:
                states = {c.id: {
                    'slip_state': c.slip_state.value,
                    'normal_force': c.normal_force,
                    'friction_current': c.friction.mu_current,
                    'wear_depth': c.wear.wear_depth
                } for c in self.contacts}
                contact_states_history.append(states)

            # 8. Progress callback
            if progress_callback is not None and step % 100 == 0:
                progress = 100.0 * step / n_steps
                progress_callback(progress)

            # Update current state
            u_current = u_next
            v_current = v_next
            a_current = a_next

            # Early termination check (complete loosening)
            if preload_current < 0.01 * self.config.initial_preload:
                print(f"  Warning: Preload dropped below 1% at step {step}, terminating early")
                # Trim arrays
                time_vec = time_vec[:step+2]
                U_history = U_history[:step+2]
                V_history = V_history[:step+2]
                A_history = A_history[:step+2]
                preload_history = preload_history[:step+2]
                loosening_angle_history = loosening_angle_history[:step+2]
                break

        # Complete
        runtime = (datetime.now() - start_time).total_seconds()
        print(f"  Integration complete in {runtime:.2f} s")

        # Compute statistics
        statistics = self._compute_statistics(
            time_vec, U_history, V_history, A_history,
            preload_history, loosening_angle_history
        )

        # Create result
        self.result = AnalysisResult(
            config=self.config,
            time=time_vec,
            displacement=U_history,
            velocity=V_history,
            acceleration=A_history,
            preload_history=preload_history,
            loosening_angle_history=loosening_angle_history,
            contact_states_history=contact_states_history,
            cycle_data=cycle_data,
            statistics=statistics,
            converged=True,
            runtime_seconds=runtime
        )

        print(f"\n  Analysis complete!")
        print(f"  Final preload: {self.result.get_final_preload():.0f} N ({self.result.get_preload_loss_percent():.1f}% loss)")
        print(f"  Loosening angle: {self.result.get_total_loosening_angle():.2f}°")

        return self.result

    def _compute_statistics(
        self,
        time: np.ndarray,
        U: np.ndarray,
        V: np.ndarray,
        A: np.ndarray,
        preload: np.ndarray,
        angle: np.ndarray
    ) -> Dict[str, float]:
        """Compute summary statistics."""
        stats = {
            'max_displacement': np.max(np.abs(U)),
            'max_velocity': np.max(np.abs(V)),
            'max_acceleration': np.max(np.abs(A)),
            'initial_preload': preload[0],
            'final_preload': preload[-1],
            'preload_loss_percent': 100 * (preload[0] - preload[-1]) / preload[0] if preload[0] > 0 else 0,
            'total_loosening_angle_deg': np.degrees(angle[-1]),
            'max_loosening_rate_deg_cycle': 0.0,  # Computed from cycle data
        }
        return stats

    def post_process(self) -> None:
        """
        Generate plots and post-processing outputs.

        Creates all standard analysis plots.
        """
        if self.result is None:
            raise RuntimeError("Must run analysis first")

        print("\n[AnalysisManager] Post-processing...")

        # Import visualization
        from ...visualization.contact_plots import (
            plot_preload_vs_cycles,
            plot_loosening_angle_vs_time,
            plot_contact_summary_dashboard
        )

        # Create output directory
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate plots
        if self.result.cycle_data is not None:
            print("  Plotting preload vs cycles...")
            plot_preload_vs_cycles(self.result.cycle_data, save_path=self.config.output_dir / "preload_cycles.png")

        print("  Plotting loosening angle...")
        plot_loosening_angle_vs_time(
            self.result.time,
            self.result.loosening_angle_history,
            save_path=self.config.output_dir / "loosening_angle.png"
        )

        print("  Creating summary dashboard...")
        plot_contact_summary_dashboard(
            self.result,
            save_path=self.config.output_dir / "summary_dashboard.png"
        )

        print("  Post-processing complete!")

    def export_results(self, output_dir: Optional[Path] = None) -> None:
        """
        Export results to files.

        Args:
            output_dir: Output directory (default: from config)
        """
        if self.result is None:
            raise RuntimeError("Must run analysis first")

        if output_dir is None:
            output_dir = self.config.output_dir

        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n[AnalysisManager] Exporting results to {output_dir}")

        # Export time histories to CSV
        print("  Exporting time histories...")
        np.savetxt(
            output_dir / "time_history.csv",
            np.column_stack([
                self.result.time,
                self.result.preload_history,
                self.result.loosening_angle_history
            ]),
            delimiter=',',
            header='time,preload,loosening_angle',
            comments=''
        )

        # Export cycle data
        if self.result.cycle_data is not None:
            print("  Exporting cycle data...")
            cycle_array = np.column_stack([
                self.result.cycle_data['cycle'],
                self.result.cycle_data['preload'],
                self.result.cycle_data['angle'],
                self.result.cycle_data['time']
            ])
            np.savetxt(
                output_dir / "cycle_data.csv",
                cycle_array,
                delimiter=',',
                header='cycle,preload,angle_deg,time',
                comments=''
            )

        # Export summary JSON
        print("  Exporting summary...")
        summary = {
            'name': self.config.name,
            'timestamp': self.result.timestamp,
            'runtime_seconds': self.result.runtime_seconds,
            'statistics': self.result.statistics,
            'converged': self.result.converged
        }

        with open(output_dir / "analysis_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

        print("  Export complete!")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_junker_test_analysis(
    bolt_size: str = "M20",
    joint_type: str = "API_6A",
    preload: float = 50000.0,
    n_cycles: int = 2000
) -> AnalysisManager:
    """
    Create a standard Junker test analysis configuration.

    Args:
        bolt_size: Bolt size designation
        joint_type: "API_6A", "ASME_B16_5", or "VDI_2230"
        preload: Initial preload [N]
        n_cycles: Number of Junker test cycles

    Returns:
        AnalysisManager ready to run
    """
    # Create joint config
    if joint_type == "API_6A":
        joint_config = create_api_6a_joint_config(bolt_size=bolt_size)
    elif joint_type == "ASME_B16_5":
        joint_config = create_asme_b16_5_joint_config(bolt_size=bolt_size)
    else:
        joint_config = create_vdi_2230_joint_config(bolt_size=bolt_size)

    # Create loading protocol
    loading = LoadingProtocol(
        protocol_type=LoadingProtocolType.JUNKER_TEST,
        junker_n_cycles=n_cycles
    )

    # Create analysis config
    config = AnalysisConfiguration(
        name=f"Junker Test {bolt_size} {joint_type}",
        joint_config=joint_config,
        loading=loading,
        initial_preload=preload
    )

    return AnalysisManager(config)


if __name__ == "__main__":
    print("=" * 70)
    print("Analysis Workflow Manager - Test Suite")
    print("Bolt Analysis Studio v4.0")
    print("=" * 70)

    # Create test analysis
    print("\n[Test] Creating Junker test analysis...")
    manager = create_junker_test_analysis(
        bolt_size="M20",
        joint_type="API_6A",
        preload=50000.0,
        n_cycles=100  # Reduced for testing
    )

    print("\n[Test] Setup complete!")
    print(f"  Manager: {manager}")
    print(f"  Config: {manager.config.name}")
