# Fusion Reactor Optimization Guide

## Quick Start

### Basic Optimization

```bash
# Run grid search optimization (50 iterations)
python3 optimize.py --method grid --iterations 50

# Run SPSA optimization (more efficient)
python3 optimize.py --method spsa --iterations 30

# Hybrid approach (grid + SPSA refinement)
python3 optimize.py --method hybrid --iterations 50

# Apply research-based solutions
python3 optimize.py --method grid --iterations 50 --apply-solutions

# Save best configuration
python3 optimize.py --method spsa --iterations 30 --save best_config.json

# Load and test a configuration
python3 optimize.py --load best_config.json --iterations 1
```

## Iterative Workflow

### 1. Run and Analyze

```bash
# Run optimization
python3 optimize.py --method spsa --iterations 30 --max-time 3600

# Check results
# - Operation time
# - Q factor
# - Safety factor
# - Failure causes
```

### 2. Identify Issues

Look at the output:
- **Safety factor too low?** → Try HTS magnets or geometry changes
- **Lawson criterion not met?** → Optimize temperature/density
- **Material damage?** → Try advanced materials
- **Fuel depletion?** → Improve tritium breeding

### 3. Apply Solutions

```bash
# Apply research-based solutions automatically
python3 optimize.py --apply-solutions --method spsa

# Or manually adjust parameters based on PHYSICS_ISSUES.md
```

### 4. Iterate

```bash
# Save good configurations
python3 optimize.py --save config_v1.json

# Refine further
python3 optimize.py --load config_v1.json --method spsa --iterations 20
```

## Optimization Methods

### Grid Search
- **Best for**: Initial exploration
- **Pros**: Simple, finds global patterns
- **Cons**: Slow, many iterations needed
- **Use when**: Starting from scratch

### SPSA (Simultaneous Perturbation Stochastic Approximation)
- **Best for**: Refinement, high-dimensional problems
- **Pros**: Efficient, fewer iterations
- **Cons**: Can get stuck in local optima
- **Use when**: You have a starting point

### Hybrid
- **Best for**: Best of both worlds
- **Pros**: Exploration + refinement
- **Cons**: Takes longer
- **Use when**: You want thorough optimization

## Research-Based Solutions

The optimizer includes solutions from recent fusion research (2020-2024):

1. **HTS High-Field Magnets** (SPARC, 2024)
   - Higher magnetic fields (12-20 T)
   - Lower power consumption

2. **Spherical Tokamak Geometry** (MAST, ST40)
   - Lower aspect ratio
   - Better safety factor

3. **Advanced Current Drive** (ITER, 2023)
   - Improved efficiency
   - Lower power consumption

4. **Advanced Materials**
   - Tungsten-Copper composite
   - Better thermal management

5. **Enhanced Tritium Breeding**
   - Optimized lithium enrichment
   - Better breeding ratio

## Parameter Bounds

All parameters are constrained to realistic values:

- **Major Radius**: 3.0 - 10.0 m (ITER: 6.2 m)
- **Minor Radius**: 0.5 - 3.0 m (ITER: 2.0 m)
- **Toroidal Field**: 2.0 - 20.0 T (ITER: 5.3 T, SPARC: 12.2 T)
- **Plasma Current**: 5 - 20 MA (ITER: 15 MA)
- **Temperature**: 50 - 300 MK (optimal: 100-200 MK)
- **Density**: 0.5 - 3.0 × 10²⁰ m⁻³

## Scoring Function

The optimizer scores configurations based on:

- **Operation Time** (primary): Beat 21 minutes = +100 points
- **Q Factor**: Bonus for Q > 1, extra for Q > 10
- **Safety Factor**: Bonus for q ≥ 2.0
- **Lawson Criterion**: +30 points if met
- **Net Power**: +40 points if positive
- **Penalties**: Failure = -50, very short operation = -100

## Tips

1. **Start with grid search** to explore the parameter space
2. **Use SPSA** to refine promising configurations
3. **Apply solutions** for known issues (safety factor, etc.)
4. **Save good configs** and iterate from them
5. **Check PHYSICS_ISSUES.md** for specific problems
6. **Mix solutions**: Try combining multiple research solutions

## Example Workflow

```bash
# 1. Initial exploration
python3 optimize.py --method grid --iterations 100 --save initial.json

# 2. Check results, identify issues
# (Look at output, check PHYSICS_ISSUES.md)

# 3. Apply solutions and refine
python3 optimize.py --load initial.json --apply-solutions --method spsa --iterations 30 --save refined.json

# 4. Test best configuration
python3 main.py --config iter  # Or use your best config

# 5. Iterate based on results
python3 optimize.py --load refined.json --method hybrid --iterations 50
```

## Advanced: Custom Optimization

You can create custom optimization scripts:

```python
from optimization import ParameterOptimizer, SolutionsDatabase
from simulator import FusionReactorSimulator, ReactorConfiguration

# Create optimizer
optimizer = ParameterOptimizer()

# Custom scoring function
def my_score(sim, max_time):
    state = sim.run(max_time=max_time)
    # Your custom scoring logic
    return score

# Run optimization
result = optimizer.grid_search(
    n_samples=100,
    max_time=3600.0,
    objective=my_score
)
```

## Next Steps

1. Run initial optimization
2. Analyze results
3. Apply research solutions
4. Iterate and refine
5. Test best configurations
6. Beat the 21-minute record! 🎯

