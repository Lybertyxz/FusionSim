# Fusion Reactor Simulator - Usage Guide

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run basic simulation
python main.py

# Run with ITER-like parameters
python main.py --config iter

# Try to optimize parameters
python main.py --optimize

# Generate visualizations
python main.py --visualize
```

## Understanding the Output

The simulator provides comprehensive status reports showing:

### Plasma State
- **Temperature**: Plasma temperature in MK (millions of Kelvin)
- **Density**: Plasma density in 10²⁰ m⁻³
- **Confinement Time**: Energy confinement time in seconds
- **Triple Product**: nτT (density × confinement × temperature)
- **Lawson Criterion**: Whether the plasma meets ignition conditions

### Magnetic Confinement
- **Toroidal Field**: Main magnetic field strength
- **Plasma Current**: Current flowing in the plasma
- **Safety Factor (q)**: Stability parameter (should be > 2-3)
- **Beta**: Ratio of plasma pressure to magnetic pressure

### Power Balance
- **Fusion Power**: Power from fusion reactions
- **Input Power**: Power needed to heat and maintain plasma
- **Q Factor**: Fusion power / Input power
  - Q < 1: Net energy loss
  - Q = 1: Breakeven
  - Q > 1: Net energy gain
  - Q → ∞: Ignition (self-sustaining)

### Neutronics
- **Neutron Flux**: Neutron flux at first wall
- **Wall Loading**: Power density on first wall
- **Tritium Breeding Ratio (TBR)**: Must be > 1.0 for sustained operation
- **Material Damage**: Displacements Per Atom (DPA)

### Errors and Warnings
The simulator clearly identifies:
- **Errors**: Critical issues preventing operation
- **Warnings**: Potential problems or approaching limits

## Common Issues and Solutions

### Low Q Factor
- **Problem**: Q < 1, not producing net energy
- **Solutions**:
  - Increase plasma temperature (optimal: 100-200 MK)
  - Increase plasma density
  - Improve confinement time
  - Reduce input power requirements

### Safety Factor Too Low
- **Problem**: q < 2, plasma unstable
- **Solutions**:
  - Increase toroidal magnetic field
  - Decrease plasma current
  - Adjust geometry (increase major radius or decrease minor radius)

### Lawson Criterion Not Met
- **Problem**: nτ < 10²⁰ m⁻³·s
- **Solutions**:
  - Increase density
  - Improve confinement time (better magnetic configuration)
  - Ensure temperature is in optimal range (100-200 MK)

### High Material Damage
- **Problem**: DPA too high, materials degrading
- **Solutions**:
  - Reduce neutron wall loading
  - Use more radiation-resistant materials
  - Reduce operating time or power

### Tritium Breeding Ratio < 1
- **Problem**: Cannot sustain tritium supply
- **Solutions**:
  - Increase breeding blanket thickness
  - Use enriched Li-6
  - Optimize blanket design

## Example: Optimizing a Reactor

```python
from simulator import FusionReactorSimulator, ReactorConfiguration

# Start with default configuration
config = ReactorConfiguration(
    major_radius=6.2,
    minor_radius=2.0,
    toroidal_field=5.3,
    plasma_current=15e6,
    initial_temperature=150e6,  # 150 MK
    initial_density=1e20,
    auxiliary_heating=50e6
)

sim = FusionReactorSimulator(config)
state = sim.run()
sim.print_status()

# If Q is low, try optimizing
if state.power_balance.q_factor < 1.0:
    result = sim.optimize_parameters(target_q=10.0)
    print(f"Optimized Q: {result['best_q']:.2f}")
```

## Material Selection

The simulator includes a material database:

```python
from materials.materials import MaterialDatabase

materials = MaterialDatabase()

# List available materials
print(materials.list_materials())
# ['tungsten', 'beryllium', 'lithium', 'lithium_lead', 'eurofer97', 'helium', 'water']

# Get material properties
tungsten = materials.get_material('tungsten')
print(f"Melting point: {tungsten.melting_point} K")
print(f"Max operating temp: {tungsten.max_operating_temp} K")
```

## Customizing Calculations

Each physics module can be used independently:

```python
from physics.plasma import PlasmaPhysics
from physics.magnetic import MagneticConfinement

plasma = PlasmaPhysics()
magnetic = MagneticConfinement()

# Calculate fusion power density
power_density = plasma.calculate_fusion_power_density(
    density=1e20,  # m⁻³
    temperature=150e6  # K
)

# Calculate safety factor
q = magnetic.calculate_safety_factor(
    major_radius=6.2,
    minor_radius=2.0,
    toroidal_field=5.3,
    plasma_current=15e6
)
```

## Visualization

The simulator can generate visualizations:

```python
sim = FusionReactorSimulator()
sim.run()
sim.visualize(save_path='output')  # Saves to output_dashboard.png, etc.
```

Visualizations include:
- Reactor geometry diagram
- Status dashboard
- Power balance charts
- Parameter evolution (if running time-dependent simulation)

## Testing

Run the test suite:

```bash
python tests/test_physics.py
```

## Next Steps

1. **Improve confinement**: Adjust magnetic configuration
2. **Optimize temperature**: Find optimal operating point
3. **Material selection**: Test different first wall and blanket materials
4. **Geometry optimization**: Vary major/minor radius, elongation
5. **Power balance**: Minimize input power, maximize Q factor

## Notes

- The simulator uses simplified models for educational purposes
- Real fusion reactors require much more complex physics
- Some approximations may not be accurate for all conditions
- Always validate against experimental data when possible

