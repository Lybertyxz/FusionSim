# Fusion Reactor Physics Documentation

This document explains the physics models implemented in the fusion reactor simulator.

## Overview

The simulator models a tokamak fusion reactor using D-T (deuterium-tritium) fusion. The main components are:

1. **Plasma Physics**: Fusion reactions, Lawson criterion, energy balance
2. **Magnetic Confinement**: Tokamak geometry, magnetic fields, safety factor
3. **Power Balance**: Q factor, energy efficiency, breakeven/ignition
4. **Neutronics**: Neutron flux, tritium breeding, material damage

## Plasma Physics

### D-T Fusion Reaction

The primary reaction is:
```
D + T → ⁴He (3.5 MeV) + n (14.1 MeV)
```

Total energy release: **17.6 MeV per reaction**

### Fusion Cross-Section

The fusion cross-section σ depends on temperature:
```
σ(E) ≈ a × exp(-b/E^(1/3))
```

Where:
- E is the center-of-mass energy (related to temperature)
- a ≈ 3.68×10⁻¹² m²
- b ≈ 19.94 keV^(1/3)

### Reaction Rate

The fusion reaction rate density is:
```
R = n_D × n_T × <σv>
```

Where:
- n_D, n_T are deuterium and tritium densities
- <σv> is the velocity-averaged cross-section

### Lawson Criterion

For ignition, the plasma must satisfy:
```
nτ ≥ 10²⁰ m⁻³·s
```

At optimal temperature: **T ≈ 10-15 keV (≈100-150 MK)**

The triple product **nτT** must exceed approximately **3×10²¹ m⁻³·s·K**

### Energy Losses

1. **Bremsstrahlung Radiation**: 
   ```
   P_brem ≈ 5.35×10⁻³⁷ × n² × √T × Z_eff²
   ```

2. **Synchrotron Radiation**:
   ```
   P_sync ≈ 6.21×10⁻¹⁶ × B² × T² × n
   ```

## Magnetic Confinement

### Tokamak Geometry

- **Major Radius (R₀)**: Distance from center to plasma center
- **Minor Radius (a)**: Plasma cross-section radius
- **Aspect Ratio**: R₀/a (typically 2-4)
- **Elongation (κ)**: Vertical/horizontal plasma dimension ratio
- **Triangularity (δ)**: Plasma shape parameter

### Plasma Volume

```
V ≈ 2π² R₀ a² κ
```

### Safety Factor (q)

The safety factor determines plasma stability:
```
q = (2π a² B₀) / (μ₀ R₀ I_p)
```

- **q < 2**: Unstable (disruptions)
- **q ≈ 2-3**: Marginally stable
- **q > 3**: Stable

### Beta Parameter

Beta is the ratio of plasma pressure to magnetic pressure:
```
β = p_plasma / p_magnetic = (nkT) / (B²/2μ₀)
```

Typical values: **β ≈ 0.01-0.1** (low beta for stability)

### Confinement Time Scaling

Uses ITER-98(y,2) scaling law:
```
τ_E = 0.0562 × I^0.93 × B^0.15 × P^-0.69 × n^0.41 × R^1.97 × κ^0.78 × ε^0.58
```

## Power Balance

### Q Factor

The Q factor is the ratio of fusion power to input power:
```
Q = P_fusion / P_input
```

- **Q < 1**: Net energy loss
- **Q = 1**: Breakeven
- **Q > 1**: Net energy gain
- **Q → ∞**: Ignition (self-sustaining)

### Power Components

1. **Fusion Power**: From D-T reactions
2. **Input Power**: 
   - Ohmic heating (I²R)
   - Auxiliary heating (NBI, ICRH, ECRH)
   - Current drive
3. **Thermal Power**: Fusion + Input - Radiation losses
4. **Electrical Output**: Thermal × efficiency (~33%)

### Net Power

```
P_net = P_electrical_output - P_input
```

## Neutronics

### Neutron Flux

Each D-T fusion produces one 14.1 MeV neutron:
```
φ = (P_neutron) / (E_neutron × A)
```

Where:
- P_neutron = P_fusion × (14.1/17.6)
- A is the first wall surface area

### Neutron Wall Loading

```
P_wall = P_neutron / A  [MW/m²]
```

Typical limits: **1-5 MW/m²**

### Tritium Breeding

Tritium must be bred from lithium:
```
⁶Li + n → T + ⁴He
⁷Li + n → T + ⁴He + n
```

**Tritium Breeding Ratio (TBR)**:
```
TBR = R_production / R_consumption
```

Must be **TBR > 1.0** for sustained operation.

### Material Damage

**Displacements Per Atom (DPA)**:
```
DPA_rate = φ × σ_DPA × t
```

Typical limits: **~100-200 DPA** for structural materials.

## Material Properties

### First Wall Materials

- **Tungsten**: High melting point (3695 K), low tritium retention
- **Beryllium**: Low Z, good thermal properties, but brittle

### Breeding Blanket

- **Lithium-Lead (LiPb)**: Liquid metal, good tritium breeding
- **Lithium**: Pure lithium for breeding

### Structural Materials

- **EUROFER97**: Reduced-activation ferritic steel
- Operating limits: ~550 K (irradiation effects)

## Key Parameters

### ITER-like Configuration

- Major radius: **6.2 m**
- Minor radius: **2.0 m**
- Toroidal field: **5.3 T**
- Plasma current: **15 MA**
- Fusion power: **500 MW**
- Q factor: **~10**

### Optimal Operating Conditions

- Temperature: **10-20 MK** (optimal: ~15 MK)
- Density: **0.5-2 × 10²⁰ m⁻³**
- Triple product: **> 3 × 10²¹ m⁻³·s·K**
- Safety factor: **q > 3**
- Beta: **< 0.1**

## References

- ITER Physics Basis (2007)
- Wesson, J. "Tokamaks" (4th ed., 2011)
- Freidberg, J. "Plasma Physics and Fusion Energy" (2007)
- Stacey, W. "Fusion: An Introduction to the Physics and Technology of Magnetic Confinement Fusion" (2010)

