"""Iterative optimization script for fusion reactor.

Run, analyze, iterate, and optimize reactor configurations.
"""

import argparse
from simulator import FusionReactorSimulator, ReactorConfiguration
from optimization import ParameterOptimizer, SolutionsDatabase
import json


def main():
    """Main optimization loop."""
    parser = argparse.ArgumentParser(description='Fusion Reactor Optimizer')
    parser.add_argument('--method', type=str, default='grid',
                       choices=['grid', 'spsa', 'hybrid'],
                       help='Optimization method')
    parser.add_argument('--iterations', type=int, default=50,
                       help='Number of iterations')
    parser.add_argument('--max-time', type=float, default=1260.0,
                       help='Maximum simulation time (seconds)')
    parser.add_argument('--target-time', type=float, default=1260.0,
                       help='Target operation time (seconds, default: 21 min)')
    parser.add_argument('--apply-solutions', action='store_true',
                       help='Apply research-based solutions')
    parser.add_argument('--save', type=str, help='Save best configuration to file')
    parser.add_argument('--load', type=str, help='Load configuration from file')
    
    args = parser.parse_args()
    
    print("="*80)
    print("FUSION REACTOR OPTIMIZER")
    print("="*80)
    print(f"Method: {args.method}")
    print(f"Iterations: {args.iterations}")
    print(f"Target: Beat {args.target_time/60:.1f} minutes")
    print("="*80 + "\n")
    
    # Load solutions database
    solutions_db = SolutionsDatabase()
    
    # Create optimizer
    optimizer = ParameterOptimizer()
    
    # Load or create initial config
    if args.load:
        print(f"Loading configuration from {args.load}...")
        with open(args.load, 'r') as f:
            config_dict = json.load(f)
        initial_config = ReactorConfiguration(**config_dict)
    else:
        # Start with ITER-like config
        initial_config = ReactorConfiguration()
        
        # Apply research solutions if requested
        if args.apply_solutions:
            print("\nApplying research-based solutions...")
            # Get solutions for safety factor issue
            safety_solutions = solutions_db.get_solutions_for_issue('safety_factor')
            for solution in safety_solutions[:2]:  # Apply top 2
                print(f"  - {solution.name}")
                changes = solutions_db.apply_solution(solution, initial_config)
                for key, value in changes.items():
                    setattr(initial_config, key, value)
                    print(f"    {key}: {value}")
    
    # Run optimization
    print(f"\nRunning {args.method} optimization...\n")
    
    if args.method == 'grid':
        result = optimizer.grid_search(
            n_samples=args.iterations,
            max_time=args.max_time
        )
    elif args.method == 'spsa':
        result = optimizer.spsa_optimize(
            initial_config=initial_config,
            max_iterations=args.iterations,
            max_time=args.max_time
        )
    else:  # hybrid
        # Start with grid search, then refine with SPSA
        print("Phase 1: Grid search...")
        grid_result = optimizer.grid_search(
            n_samples=args.iterations // 2,
            max_time=args.max_time
        )
        print(f"\nPhase 2: SPSA refinement (starting from best grid result)...")
        result = optimizer.spsa_optimize(
            initial_config=grid_result.best_config,
            max_iterations=args.iterations // 2,
            max_time=args.max_time
        )
    
    # Results
    print("\n" + "="*80)
    print("OPTIMIZATION RESULTS")
    print("="*80)
    print(f"Best Score: {result.best_score:.2f}")
    print(f"Success: {result.success}")
    print(f"Iterations: {result.iterations}")
    
    if result.best_config:
        print("\nBest Configuration:")
        print(f"  Major Radius: {result.best_config.major_radius:.2f} m")
        print(f"  Minor Radius: {result.best_config.minor_radius:.2f} m")
        print(f"  Aspect Ratio: {result.best_config.major_radius/result.best_config.minor_radius:.2f}")
        print(f"  Toroidal Field: {result.best_config.toroidal_field:.2f} T")
        print(f"  Plasma Current: {result.best_config.plasma_current/1e6:.2f} MA")
        print(f"  Temperature: {result.best_config.initial_temperature/1e6:.2f} MK")
        print(f"  Density: {result.best_config.initial_density/1e20:.2f} × 10²⁰ m⁻³")
        print(f"  Input Power: {result.best_config.input_power/1e6:.2f} MW")
    
    # Test best configuration
    if result.best_config:
        print("\n" + "="*80)
        print("TESTING BEST CONFIGURATION")
        print("="*80)
        sim = FusionReactorSimulator(result.best_config)
        state = sim.run(max_time=args.max_time, dt=1.0)
        sim.print_status()
        
        stats = sim.get_operation_statistics()
        print("\n" + "="*80)
        print("FINAL RESULTS")
        print("="*80)
        print(f"Operation Time: {stats['max_operation_time_minutes']:.2f} minutes")
        if stats['max_operation_time_minutes'] >= args.target_time/60:
            print(f"✓ RECORD BEATEN! ({stats['max_operation_time_minutes']:.2f} min > {args.target_time/60:.1f} min)")
        else:
            print(f"✗ Record not beaten ({stats['max_operation_time_minutes']:.2f} min < {args.target_time/60:.1f} min)")
        
        if stats['can_run_indefinitely']:
            print("✓ Reactor can run INDEFINITELY")
        else:
            print(f"Predicted max runtime: {stats['max_runtime_prediction_minutes']:.2f} minutes")
            print(f"Limiting factor: {stats['limiting_factor']}")
    
    # Save configuration
    if args.save and result.best_config:
        config_dict = {
            'major_radius': result.best_config.major_radius,
            'minor_radius': result.best_config.minor_radius,
            'elongation': result.best_config.elongation,
            'triangularity': result.best_config.triangularity,
            'toroidal_field': result.best_config.toroidal_field,
            'plasma_current': result.best_config.plasma_current,
            'initial_temperature': result.best_config.initial_temperature,
            'initial_density': result.best_config.initial_density,
            'input_power': result.best_config.input_power,
            'auxiliary_heating': result.best_config.auxiliary_heating,
            'current_drive_power': result.best_config.current_drive_power,
            'initial_tritium_inventory': result.best_config.initial_tritium_inventory,
            'initial_deuterium_inventory': result.best_config.initial_deuterium_inventory,
        }
        with open(args.save, 'w') as f:
            json.dump(config_dict, f, indent=2)
        print(f"\nConfiguration saved to {args.save}")


if __name__ == '__main__':
    main()

