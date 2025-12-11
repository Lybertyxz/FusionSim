"""Basic example of using the fusion reactor simulator."""

from simulator import FusionReactorSimulator, ReactorConfiguration


def basic_example():
    """Run a basic simulation."""
    print("="*80)
    print("BASIC FUSION REACTOR SIMULATION")
    print("="*80)
    
    # Create a default configuration
    config = ReactorConfiguration()
    
    # Create simulator
    sim = FusionReactorSimulator(config)
    
    # Run simulation
    state = sim.run()
    
    # Print detailed status
    sim.print_status()
    
    return state


def iter_like_example():
    """Run simulation with ITER-like parameters."""
    print("="*80)
    print("ITER-LIKE FUSION REACTOR SIMULATION")
    print("="*80)
    
    # ITER-like configuration
    config = ReactorConfiguration(
        major_radius=6.2,  # m
        minor_radius=2.0,   # m
        elongation=1.7,
        toroidal_field=5.3,  # T
        plasma_current=15e6,  # 15 MA
        initial_temperature=15e6,  # 15 MK
        initial_density=1e20,  # 10^20 m^-3
        input_power=50e6,  # 50 MW
        auxiliary_heating=33e6  # 33 MW
    )
    
    sim = FusionReactorSimulator(config)
    state = sim.run()
    sim.print_status()
    
    return state


def optimization_example():
    """Try to optimize reactor parameters."""
    print("="*80)
    print("PARAMETER OPTIMIZATION EXAMPLE")
    print("="*80)
    
    config = ReactorConfiguration()
    sim = FusionReactorSimulator(config)
    
    # Initial state
    print("\nInitial configuration:")
    state = sim.run()
    sim.print_status()
    
    # Optimize
    print("\nOptimizing parameters...")
    result = sim.optimize_parameters(target_q=10.0, max_iterations=100)
    
    print(f"\nOptimization Results:")
    print(f"  Best Q factor: {result['best_q']:.2f}")
    print(f"  Best temperature: {result['best_temperature']/1e6:.2f} MK")
    print(f"  Best density: {result['best_density']/1e20:.2f} × 10²⁰ m⁻³")
    print(f"  Target achieved: {result['target_achieved']}")
    
    if result['target_achieved']:
        print("\nOptimized configuration:")
        sim.print_status()
    
    return result


if __name__ == '__main__':
    # Run examples
    print("\n1. Basic Example")
    basic_example()
    
    print("\n\n2. ITER-like Example")
    iter_like_example()
    
    print("\n\n3. Optimization Example")
    optimization_example()

