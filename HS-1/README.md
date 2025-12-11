# Fusion Reactor Simulator

A comprehensive, modular fusion reactor simulator designed to test and optimize fusion reactor designs with realistic physics calculations.

## Features

- **Modular Architecture**: Separated calculation modules for maintainability
- **Realistic Physics**: Based on real fusion research data and benchmarks
- **Visual Representation**: Real-time visualization of reactor state and progress
- **Comprehensive Data Display**: All calculated parameters visible and understandable
- **Error Diagnostics**: Clear identification of what doesn't work and why
- **Material Database**: Easily maintainable material properties
- **Testable Design**: Each module can be tested independently

## Architecture

The simulator is organized into distinct modules:

- `physics/plasma.py`: Plasma physics calculations (Lawson criterion, fusion reactions)
- `physics/magnetic.py`: Magnetic confinement calculations
- `physics/power.py`: Power balance and energy calculations
- `physics/neutronics.py`: Neutron flux and tritium breeding
- `materials/`: Material database and properties
- `visualization/`: Visualization and plotting tools
- `simulator.py`: Main simulator class integrating all modules

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from simulator import FusionReactorSimulator

# Create and run a simulation
sim = FusionReactorSimulator()
state = sim.run()

# Print detailed status
sim.print_status()

# Create visualizations
sim.visualize()
```

### Command Line

```bash
# Run with default configuration
python main.py

# Run with ITER-like configuration
python main.py --config iter

# Run with optimization
python main.py --optimize

# Generate visualizations
python main.py --visualize

# Save visualizations
python main.py --visualize --save output
```

### Examples

See `examples/` directory for detailed examples:
- `basic_example.py`: Basic usage examples
- `run_best_simulation.py`: Run the optimized best configuration

### Documentation

All documentation is in the `docs/` folder:
- `TECHNICAL_REPORT.md`: Detailed calculation breakdown
- `FEASIBILITY_REPORT.md`: Buildability analysis
- `OPTIMIZATION_GUIDE.md`: How to use the optimizer
- `PHYSICS_ISSUES.md`: Known physics problems and solutions
- And more...

### Output

- **Plots/Visualizations**: Saved to `plots/` folder automatically
- **Configurations**: JSON files in root directory

## Physics Background

The simulator implements:
- Lawson criterion for fusion ignition
- Triple product (nτT) calculations
- D-T fusion reaction rates
- Magnetic confinement physics
- Power balance (Q factor)
- Material limits and neutronics

