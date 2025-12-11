"""Example: Run the best optimized fusion reactor simulation.

This example loads the best_attempt.json configuration and runs a full simulation.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import simulator
sys.path.insert(0, str(Path(__file__).parent.parent))

from simulator import FusionReactorSimulator, ReactorConfiguration


def run_best_simulation(max_time_hours=2.0, dt=1.0, visualize=False, save_path=None):
    """Run the best optimized simulation.
    
    Args:
        max_time_hours: Maximum simulation time in hours (default: 2.0)
        dt: Time step in seconds (default: 1.0)
        visualize: Whether to generate visualizations (default: False)
        save_path: Path to save visualizations (default: None)
    """
    # Load best configuration
    config_path = Path(__file__).parent.parent / 'best_attempt.json'
    
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        print("Please run optimization first to generate best_attempt.json")
        return None
    
    print("="*80)
    print("BEST FUSION REACTOR SIMULATION")
    print("="*80)
    print(f"\nLoading configuration from: {config_path}")
    
    with open(config_path, 'r') as f:
        config_dict = json.load(f)
    
    # Create configuration
    config = ReactorConfiguration(**config_dict)
    
    print("\nConfiguration Parameters:")
    print(f"  Major Radius: {config.major_radius:.2f} m")
    print(f"  Minor Radius: {config.minor_radius:.2f} m")
    print(f"  Aspect Ratio: {config.major_radius/config.minor_radius:.2f}")
    print(f"  Toroidal Field: {config.toroidal_field:.2f} T")
    print(f"  Plasma Current: {config.plasma_current/1e6:.2f} MA")
    print(f"  Temperature: {config.initial_temperature/1e6:.2f} MK")
    print(f"  Density: {config.initial_density/1e20:.2f} × 10²⁰ m⁻³")
    print(f"  Input Power: {config.input_power/1e6:.2f} MW")
    
    # Create simulator
    sim = FusionReactorSimulator(config)
    
    # Run simulation
    max_time_seconds = max_time_hours * 3600.0
    print(f"\nRunning simulation for up to {max_time_hours:.1f} hours ({max_time_seconds:.0f} seconds)...")
    print(f"Time step: {dt} s")
    print("="*80 + "\n")
    
    state = sim.run(max_time=max_time_seconds, dt=dt)
    
    # Print detailed status
    sim.print_status()
    
    # Get operation statistics
    stats = sim.get_operation_statistics()
    
    # Print summary
    print("\n" + "="*80)
    print("SIMULATION SUMMARY")
    print("="*80)
    print(f"Operation Time: {stats['max_operation_time_minutes']:.2f} minutes ({stats['max_operation_time_minutes']/60:.2f} hours)")
    print(f"Q Factor: {state.power_balance.q_factor:.2f}")
    print(f"Safety Factor: {state.magnetic_state.safety_factor:.2f}")
    print(f"Lawson Criterion: {'✓ MET' if state.plasma_state.meets_lawson_criterion else '✗ NOT MET'}")
    print(f"Net Power: {state.power_balance.output_power/1e6:.2f} MW")
    print(f"Total Energy: {stats['total_energy_produced_MWh']:.2f} MWh")
    
    if stats['max_operation_time_minutes'] >= 21.0:
        print(f"\n✓ RECORD BEATEN! ({stats['max_operation_time_minutes']:.2f} min > 21.0 min)")
    
    if state.plasma_state.meets_lawson_criterion:
        print("✓ Lawson criterion MET!")
    
    if stats['can_run_indefinitely']:
        print("✓ Reactor can run INDEFINITELY")
    else:
        print(f"Predicted max runtime: {stats['max_runtime_prediction_minutes']:.2f} minutes")
        print(f"Limiting factor: {stats['limiting_factor']}")
    
    print("="*80)
    
    # Generate visualizations if requested
    if visualize or save_path:
        print("\nGenerating visualizations...")
        sim.visualize(save_path=save_path)
    
    return state, stats


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run best fusion reactor simulation')
    parser.add_argument('--max-time', type=float, default=2.0,
                       help='Maximum simulation time in hours (default: 2.0)')
    parser.add_argument('--dt', type=float, default=1.0,
                       help='Time step in seconds (default: 1.0)')
    parser.add_argument('--visualize', action='store_true',
                       help='Generate visualizations')
    parser.add_argument('--save', type=str, default=None,
                       help='Save visualizations to path (e.g., "output")')
    
    args = parser.parse_args()
    
    run_best_simulation(
        max_time_hours=args.max_time,
        dt=args.dt,
        visualize=args.visualize,
        save_path=args.save
    )

