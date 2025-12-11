"""Main entry point for fusion reactor simulator."""

import argparse
from simulator import FusionReactorSimulator, ReactorConfiguration


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Fusion Reactor Simulator')
    parser.add_argument('--config', type=str, help='Configuration preset (iter, demo)')
    parser.add_argument('--optimize', action='store_true', help='Try to optimize parameters')
    parser.add_argument('--visualize', action='store_true', help='Show visualizations')
    parser.add_argument('--save', type=str, help='Save path for visualizations')
    parser.add_argument('--max-time', type=float, default=3600.0, help='Maximum simulation time in seconds (default: 3600 = 1 hour)')
    parser.add_argument('--dt', type=float, default=1.0, help='Time step in seconds (default: 1.0)')
    parser.add_argument('--target-time', type=float, default=1260.0, help='Target operation time in seconds to beat record (default: 1260 = 21 minutes)')
    
    args = parser.parse_args()
    
    # Create configuration
    if args.config == 'iter':
        # ITER-like configuration
        config = ReactorConfiguration(
            major_radius=6.2,
            minor_radius=2.0,
            elongation=1.7,
            triangularity=0.33,
            toroidal_field=5.3,
            plasma_current=15e6,
            initial_temperature=150e6,  # 150 MK ≈ 13 keV (optimal for D-T)
            initial_density=1e20,
            input_power=50e6,
            auxiliary_heating=33e6
        )
    else:
        # Default/demo configuration
        config = ReactorConfiguration()
    
    # Create simulator
    sim = FusionReactorSimulator(config)
    
    # Run time-dependent simulation
    print("Running fusion reactor simulation...")
    print(f"Target: Beat 21 minutes ({args.target_time/60:.1f} min) record")
    print(f"Simulating up to {args.max_time/60:.1f} minutes with dt={args.dt} s\n")
    
    state = sim.run(max_time=args.max_time, dt=args.dt)
    
    # Print status
    sim.print_status()
    
    # Print operation statistics
    stats = sim.get_operation_statistics()
    print("\n" + "="*80)
    print("OPERATION SUMMARY")
    print("="*80)
    print(f"Operation Time: {stats['max_operation_time_minutes']:.2f} minutes")
    if stats['max_operation_time_minutes'] >= args.target_time/60:
        print(f"✓ RECORD BEATEN! ({stats['max_operation_time_minutes']:.2f} min > {args.target_time/60:.1f} min)")
    else:
        print(f"✗ Record not beaten ({stats['max_operation_time_minutes']:.2f} min < {args.target_time/60:.1f} min)")
    
    if stats['failed']:
        print(f"Reactor FAILED: {stats['failure_cause']}")
    elif stats['can_run_indefinitely']:
        print("✓ Reactor can run INDEFINITELY")
    else:
        print(f"Predicted max runtime: {stats['max_runtime_prediction_minutes']:.2f} minutes")
        print(f"Limiting factor: {stats['limiting_factor']}")
    
    print(f"Total energy produced: {stats['total_energy_produced_MWh']:.2f} MWh")
    print("="*80 + "\n")
    
    # Optimize if requested
    if args.optimize:
        print("\nAttempting parameter optimization...")
        opt_result = sim.optimize_parameters(target_q=10.0)
        print(f"Optimization result: Q = {opt_result['best_q']:.2f}")
        if opt_result['target_achieved']:
            print("Target Q achieved!")
        sim.print_status()
    
    # Visualize if requested
    if args.visualize or args.save:
        print("\nGenerating visualizations...")
        sim.visualize(save_path=args.save)
    
    return state


if __name__ == '__main__':
    main()

