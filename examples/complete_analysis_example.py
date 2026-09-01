"""
Complete Analysis Example for Bolt Analysis Studio v4.0
LTAD/UFU - Petrobras R&D

Demonstrates end-to-end workflow for bolt loosening analysis:
1. Configure joint and loading protocol
2. Run analysis
3. Visualize results
4. Export data

Example covers:
- M20 bolt joint under Junker test
- API 6A configuration with RTJ gasket
- Complete contact system
- Preload tracking
- Results visualization
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from bolt_analysis_studio.core.workflow import (
    AnalysisManager,
    AnalysisConfiguration,
    LoadingProtocol,
    LoadingProtocolType
)
from bolt_analysis_studio.core.contacts import (
    JointConfiguration,
    create_api_6a_joint_config,
    create_asme_b16_5_joint_config,
    create_vdi_2230_joint_config
)
from bolt_analysis_studio.core.contacts.junker_loosening import JunkerModelParameters
from bolt_analysis_studio.numerical.time_integration import IntegratorType


def example_1_junker_test_m20():
    """
    Example 1: M20 bolt joint under Junker test (API 6A).

    Standard transverse vibration test per DIN 65151.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: M20 Junker Test (API 6A)")
    print("=" * 70)

    # 1. Create joint configuration
    print("\n[Step 1] Configuring joint...")
    joint_config = create_api_6a_joint_config(
        bolt_size="M20",
        pressure_rating="5K",
        gasket_type="RTJ"
    )
    print(f"  Joint type: {joint_config.joint_type}")
    print(f"  Bolt: {joint_config.bolt_size}")
    print(f"  Gasket: {joint_config.gasket_type}")
    print(f"  Thread pitch: {joint_config.thread_pitch*1000:.2f} mm")
    print(f"  Engaged threads: {joint_config.n_engaged_threads}")

    # 2. Create loading protocol
    print("\n[Step 2] Configuring loading protocol...")
    loading = LoadingProtocol(
        protocol_type=LoadingProtocolType.JUNKER_TEST,
        junker_amplitude=0.00065,  # 0.65mm standard
        junker_frequency=12.5,     # 12.5 Hz standard
        junker_n_cycles=2000       # 2000 cycles standard
    )
    print(f"  Protocol: Junker Test")
    print(f"  Amplitude: {loading.junker_amplitude*1000:.2f} mm")
    print(f"  Frequency: {loading.junker_frequency:.1f} Hz")
    print(f"  Cycles: {loading.junker_n_cycles}")
    print(f"  Duration: {loading.get_total_duration():.1f} s")

    # 3. Create Junker model parameters
    junker_params = JunkerModelParameters(
        mu_initial=0.12,
        mu_final=0.08,
        degradation_rate=0.002,
        wear_coefficient=1e-6,
        phase_I_cycles=50,
        phase_II_cycles=150
    )

    # 4. Create analysis configuration
    print("\n[Step 3] Creating analysis configuration...")
    config = AnalysisConfiguration(
        name="M20 Junker Test - API 6A",
        description="Standard Junker test on M20 bolt with RTJ gasket",
        joint_config=joint_config,
        loading=loading,
        solver_method=IntegratorType.NEWMARK_BETA,
        time_step=0.0001,  # 0.1ms time step
        initial_preload=50000.0,  # 50 kN initial preload
        junker_params=junker_params,
        output_interval=10,
        save_contact_history=True,
        save_cycle_data=True,
        output_dir=Path("results/example_1_m20_junker")
    )
    print(f"  Configuration: {config.name}")
    print(f"  Solver: {config.solver_method.name}")
    print(f"  Time step: {config.time_step*1000:.2f} ms")
    print(f"  Initial preload: {config.initial_preload/1000:.1f} kN")

    # 5. Create analysis manager
    print("\n[Step 4] Initializing analysis manager...")
    manager = AnalysisManager(config)

    # 6. Setup model (creates contacts, assembles matrices)
    print("\n[Step 5] Setting up model...")
    manager.setup_model()
    print(f"  Contacts created: {len(manager.contacts)}")
    print(f"  DOFs: {manager.assembler.n_dof}")

    # 7. Run analysis
    print("\n[Step 6] Running analysis...")
    print("  This may take several minutes...")

    def progress_callback(percent):
        if int(percent) % 10 == 0:
            print(f"  Progress: {percent:.0f}%")

    result = manager.run_analysis(progress_callback=progress_callback)

    # 8. Display results
    print("\n[Step 7] Analysis Results:")
    print("  " + "=" * 60)
    print(f"  Runtime: {result.runtime_seconds:.1f} s")
    print(f"  Converged: {result.converged}")
    print(f"  Time steps: {len(result.time)}")
    print(f"  Cycles completed: {result.current_cycle}")
    print()
    print(f"  Initial Preload: {result.statistics['initial_preload']/1000:.1f} kN")
    print(f"  Final Preload: {result.statistics['final_preload']/1000:.1f} kN")
    print(f"  Preload Loss: {result.statistics['preload_loss_percent']:.1f}%")
    print()
    print(f"  Total Loosening Angle: {result.statistics['total_loosening_angle_deg']:.2f}°")
    print(f"  Max Displacement: {result.statistics['max_displacement']*1000:.3f} mm")
    print(f"  Max Velocity: {result.statistics['max_velocity']*1000:.3f} mm/s")
    print("  " + "=" * 60)

    # 9. Post-process and create plots
    print("\n[Step 8] Generating plots...")
    manager.post_process()

    # 10. Export results
    print("\n[Step 9] Exporting results...")
    manager.export_results()

    print("\n" + "=" * 70)
    print("EXAMPLE 1 COMPLETE!")
    print(f"Results saved to: {config.output_dir}")
    print("=" * 70)

    return result


def example_2_asme_flange():
    """
    Example 2: ASME B16.5 flanged joint under operational loads.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: ASME B16.5 Flange (Operational Loading)")
    print("=" * 70)

    # Configure ASME joint
    joint_config = create_asme_b16_5_joint_config(
        bolt_size="M20",
        flange_class="300",
        use_spiral_wound=True
    )

    # Static + cyclic pressure loading
    loading = LoadingProtocol(
        protocol_type=LoadingProtocolType.STATIC,
        static_force=10000.0  # 10 kN operational load
    )

    config = AnalysisConfiguration(
        name="ASME B16.5 Class 300 - Operational",
        joint_config=joint_config,
        loading=loading,
        initial_preload=60000.0,  # 60 kN
        output_dir=Path("results/example_2_asme_operational")
    )

    manager = AnalysisManager(config)
    manager.setup_model()

    print("\n[Running] ASME B16.5 operational analysis...")
    result = manager.run_analysis()

    print("\n[Results]")
    print(f"  Final Preload: {result.get_final_preload()/1000:.1f} kN")
    print(f"  Preload Loss: {result.get_preload_loss_percent():.1f}%")

    manager.post_process()
    manager.export_results()

    print(f"\nResults saved to: {config.output_dir}")

    return result


def example_3_vdi_thermal_cycling():
    """
    Example 3: VDI 2230 joint under thermal cycling.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: VDI 2230 Joint (Thermal Cycling)")
    print("=" * 70)

    # Configure VDI joint with Belleville washers
    joint_config = create_vdi_2230_joint_config(
        bolt_size="M20",
        use_belleville=True
    )

    # Thermal cycling
    loading = LoadingProtocol(
        protocol_type=LoadingProtocolType.THERMAL,
        temperature_min=-40.0,  # -40°C
        temperature_max=150.0,  # 150°C
        thermal_cycle_duration=3600.0,  # 1 hour per cycle
        thermal_n_cycles=10
    )

    config = AnalysisConfiguration(
        name="VDI 2230 - Thermal Cycling",
        joint_config=joint_config,
        loading=loading,
        initial_preload=55000.0,  # 55 kN
        output_dir=Path("results/example_3_vdi_thermal")
    )

    manager = AnalysisManager(config)
    manager.setup_model()

    print("\n[Running] VDI 2230 thermal cycling analysis...")
    result = manager.run_analysis()

    print("\n[Results]")
    print(f"  Final Preload: {result.get_final_preload()/1000:.1f} kN")
    print(f"  Preload Loss: {result.get_preload_loss_percent():.1f}%")

    manager.post_process()
    manager.export_results()

    print(f"\nResults saved to: {config.output_dir}")

    return result


def example_4_comparative_study():
    """
    Example 4: Comparative study of different joint configurations.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Comparative Study")
    print("=" * 70)

    configurations = [
        ("API 6A - RTJ", create_api_6a_joint_config("M20", gasket_type="RTJ")),
        ("ASME B16.5 - Spiral Wound", create_asme_b16_5_joint_config("M20", use_spiral_wound=True)),
        ("VDI 2230 - Belleville", create_vdi_2230_joint_config("M20", use_belleville=True))
    ]

    results = {}

    for name, joint_config in configurations:
        print(f"\n[Running] {name}...")

        loading = LoadingProtocol(
            protocol_type=LoadingProtocolType.JUNKER_TEST,
            junker_n_cycles=500  # Reduced for comparison
        )

        config = AnalysisConfiguration(
            name=name,
            joint_config=joint_config,
            loading=loading,
            initial_preload=50000.0,
            output_dir=Path(f"results/example_4_comparative/{name.replace(' ', '_')}")
        )

        manager = AnalysisManager(config)
        manager.setup_model()
        result = manager.run_analysis()
        manager.post_process()
        manager.export_results()

        results[name] = result

    # Compare results
    print("\n" + "=" * 70)
    print("COMPARATIVE RESULTS")
    print("=" * 70)
    print(f"{'Configuration':<30} {'Initial [kN]':<15} {'Final [kN]':<15} {'Loss [%]':<10}")
    print("-" * 70)
    for name, result in results.items():
        initial = result.statistics['initial_preload'] / 1000
        final = result.statistics['final_preload'] / 1000
        loss = result.statistics['preload_loss_percent']
        print(f"{name:<30} {initial:<15.1f} {final:<15.1f} {loss:<10.1f}")
    print("=" * 70)

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Bolt Analysis Studio - Complete Examples")
    parser.add_argument(
        "--example",
        type=int,
        choices=[1, 2, 3, 4],
        help="Example number to run (1-4)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all examples"
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("BOLT ANALYSIS STUDIO v4.0")
    print("Complete Analysis Workflow Examples")
    print("LTAD/UFU - Petrobras R&D")
    print("=" * 70)

    try:
        if args.all:
            # Run all examples
            print("\n[Running all examples...]")
            example_1_junker_test_m20()
            example_2_asme_flange()
            example_3_vdi_thermal_cycling()
            example_4_comparative_study()

        elif args.example == 1:
            example_1_junker_test_m20()

        elif args.example == 2:
            example_2_asme_flange()

        elif args.example == 3:
            example_3_vdi_thermal_cycling()

        elif args.example == 4:
            example_4_comparative_study()

        else:
            # Default: run example 1
            print("\nRunning default example (Example 1: M20 Junker Test)")
            print("Use --example N or --all to run other examples\n")
            example_1_junker_test_m20()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    print("=" * 70)
