# Time-Dependent Evolution Implementation

## Summary

Your fusion reactor simulator now supports **time-dependent evolution**! This allows you to:
- ✅ Track reactor operation over time
- ✅ Beat the 21-minute record and see how long your reactor can run
- ✅ Identify when and why the reactor stops (material failure, fuel depletion, etc.)
- ✅ Determine if your reactor can run indefinitely

## What Changed

### 1. **Time Tracking**
- Added `simulation_time` and `operation_time` to `ReactorState`
- Tracks actual time in seconds

### 2. **Fuel Inventory Management**
- Tritium and deuterium inventories are tracked
- Consumption calculated from fusion reaction rate
- Production from breeding blanket
- Automatic failure when fuel runs out

### 3. **Material Damage Accumulation**
- Fixed bug: Material damage now properly accumulates over time
- DPA (Displacements Per Atom) rate integrated correctly
- Failure detection when damage exceeds material limits

### 4. **Plasma Evolution**
- Temperature evolves based on heating/cooling balance
- Density can be controlled (currently simplified)
- State variables evolve over time steps

### 5. **Failure Detection System**
- Detects failures from:
  - Material temperature limits
  - Material damage limits
  - Fuel depletion (tritium/deuterium)
  - Lawson criterion violations
  - Safety factor issues
- Reports failure cause and time

### 6. **Operation Statistics**
- Maximum operation time
- Average and max Q factor
- Total energy produced
- Predicted maximum runtime
- Limiting factors

## Usage

### Basic Time-Dependent Simulation

```python
from simulator import FusionReactorSimulator, ReactorConfiguration

# Create configuration
config = ReactorConfiguration(
    initial_tritium_inventory=1e25,  # atoms
    initial_deuterium_inventory=1e26,  # atoms
    min_tritium_inventory=1e23  # minimum for operation
)

# Create simulator
sim = FusionReactorSimulator(config)

# Run for up to 1 hour (3600 seconds) with 1 second time steps
state = sim.run(max_time=3600.0, dt=1.0)

# Print status (includes time and operation statistics)
sim.print_status()

# Get operation statistics
stats = sim.get_operation_statistics()
print(f"Operation time: {stats['max_operation_time_minutes']:.2f} minutes")
print(f"Can run indefinitely: {stats['can_run_indefinitely']}")
print(f"Limiting factor: {stats['limiting_factor']}")
```

### Command Line Usage

```bash
# Run simulation (default: 1 hour max)
python main.py

# Run for 2 hours to beat 21-minute record
python main.py --max-time 7200

# Run with custom time step (smaller = more accurate, slower)
python main.py --max-time 3600 --dt 0.5

# Target 21 minutes (1260 seconds)
python main.py --target-time 1260

# With visualization
python main.py --max-time 3600 --visualize --save output
```

### Parameters

- `max_time`: Maximum simulation time in seconds (default: 3600 = 1 hour)
- `dt`: Time step in seconds (default: 1.0 s)
  - Smaller dt = more accurate but slower
  - Larger dt = faster but less accurate
  - Recommended: 0.1-1.0 s for most cases
- `save_interval`: How often to save state history (default: 10.0 s)

## What Gets Tracked Over Time

1. **Plasma Temperature**: Evolves based on heating/cooling balance
2. **Fuel Inventories**: Tritium and deuterium consumed/produced
3. **Material Damage**: Accumulates based on neutron flux
4. **Operation Time**: Total time reactor stays operational
5. **Failure Detection**: When and why reactor stops

## Failure Modes

The simulator detects and reports failures from:

1. **Material Temperature**: First wall exceeds max operating temperature
2. **Material Damage**: Accumulated DPA exceeds material limit (typically 100 DPA)
3. **Tritium Depletion**: Inventory drops below minimum required
4. **Deuterium Depletion**: Not enough fuel for fusion
5. **Lawson Criterion**: Plasma doesn't meet ignition requirements
6. **Safety Factor**: Plasma becomes unstable (q < 2.0)

## Operation Statistics

After running a simulation, you can get:

```python
stats = sim.get_operation_statistics()

# Available fields:
stats['max_operation_time']  # seconds
stats['max_operation_time_minutes']  # minutes
stats['failed']  # True if reactor failed
stats['failure_cause']  # Why it failed
stats['average_q_factor']  # Average Q during operation
stats['max_q_factor']  # Maximum Q achieved
stats['total_energy_produced']  # Joules
stats['total_energy_produced_MWh']  # MWh
stats['max_runtime_prediction']  # Predicted max runtime (seconds)
stats['limiting_factor']  # What limits operation
stats['can_run_indefinitely']  # True if no limiting factors
```

## Beating the 21-Minute Record

The simulator is now set up to help you beat ITER's 21-minute record:

```bash
# Run and see if you beat 21 minutes
python main.py --target-time 1260

# Output will show:
# ✓ RECORD BEATEN! (X.XX min > 21.0 min)
# or
# ✗ Record not beaten (X.XX min < 21.0 min)
```

## Tips for Long Operation

1. **High Tritium Breeding Ratio (TBR)**: Need TBR > 1.0 to sustain operation
2. **Low Material Damage Rate**: Reduce neutron flux or use better materials
3. **Temperature Control**: Keep plasma temperature optimal (10-15 keV)
4. **Fuel Management**: Ensure adequate initial fuel inventory
5. **Material Selection**: Use materials with high damage tolerance

## Next Steps

You can now:
- Experiment with different configurations
- Optimize parameters for long operation
- Test new materials and modules
- See exactly when and why reactors fail
- Design reactors that can run indefinitely!

## Example: Testing a Configuration

```python
from simulator import FusionReactorSimulator, ReactorConfiguration

# Your custom configuration
config = ReactorConfiguration(
    major_radius=6.2,
    minor_radius=2.0,
    initial_temperature=150e6,
    initial_density=1e20,
    initial_tritium_inventory=1e25,  # Large inventory
    # ... other parameters
)

sim = FusionReactorSimulator(config)

# Run for 2 hours
state = sim.run(max_time=7200.0, dt=1.0)

# Check results
stats = sim.get_operation_statistics()
if stats['max_operation_time_minutes'] >= 21.0:
    print("✓ Beat the record!")
else:
    print(f"Failed at {stats['max_operation_time_minutes']:.2f} min")
    print(f"Reason: {stats['failure_cause']}")
```

Enjoy testing your fusion reactor designs! 🔥⚛️

