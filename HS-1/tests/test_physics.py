"""Tests for physics modules."""

import numpy as np
from physics.plasma import PlasmaPhysics
from physics.magnetic import MagneticConfinement
from physics.power import PowerCalculator
from physics.neutronics import NeutronicsCalculator


def test_plasma_physics():
    """Test plasma physics calculations."""
    plasma = PlasmaPhysics()
    
    # Test fusion cross-section
    sigma = plasma.calculate_fusion_cross_section(10.0)  # 10 keV
    assert sigma > 0, "Cross-section should be positive"
    
    # Test fusion reaction rate
    density = 1e20  # m^-3
    temperature = 15e6  # K
    rate = plasma.calculate_fusion_reaction_rate(density, temperature)
    assert rate >= 0, "Reaction rate should be non-negative"
    
    # Test Lawson criterion
    confinement_time = 3.0  # s
    meets, n_tau, required = plasma.check_lawson_criterion(
        density, confinement_time, temperature
    )
    assert isinstance(meets, bool), "Should return boolean"
    assert n_tau >= 0, "nτ should be non-negative"
    
    print("✓ Plasma physics tests passed")


def test_magnetic_confinement():
    """Test magnetic confinement calculations."""
    magnetic = MagneticConfinement()
    
    # Test geometry
    major_radius = 6.2  # m
    minor_radius = 2.0  # m
    geometry = magnetic.calculate_tokamak_geometry(major_radius, minor_radius)
    
    assert geometry.major_radius == major_radius
    assert geometry.minor_radius == minor_radius
    assert geometry.aspect_ratio == major_radius / minor_radius
    assert geometry.plasma_volume > 0
    
    # Test safety factor
    toroidal_field = 5.3  # T
    plasma_current = 15e6  # A
    q = magnetic.calculate_safety_factor(
        major_radius, minor_radius, toroidal_field, plasma_current
    )
    assert q > 0, "Safety factor should be positive"
    
    # Test beta
    plasma_pressure = 1e6  # Pa
    magnetic_pressure = 1e7  # Pa
    beta = magnetic.calculate_beta(plasma_pressure, magnetic_pressure)
    assert beta > 0, "Beta should be positive"
    assert beta < 1, "Beta should typically be < 1"
    
    print("✓ Magnetic confinement tests passed")


def test_power_balance():
    """Test power balance calculations."""
    power = PowerCalculator()
    
    # Test Q factor
    fusion_power = 500e6  # W
    input_power = 50e6  # W
    q = power.calculate_q_factor(fusion_power, input_power)
    assert q == 10.0, f"Q should be 10, got {q}"
    
    # Test breakeven
    assert power.check_breakeven(1.5) == True
    assert power.check_breakeven(0.5) == False
    
    # Test ignition
    assert power.check_ignition(15.0) == True
    assert power.check_ignition(5.0) == False
    
    print("✓ Power balance tests passed")


def test_neutronics():
    """Test neutronics calculations."""
    neutronics = NeutronicsCalculator()
    
    # Test neutron flux
    fusion_power = 500e6  # W
    surface_area = 1000.0  # m^2
    flux = neutronics.calculate_neutron_flux(fusion_power, surface_area)
    assert flux > 0, "Neutron flux should be positive"
    
    # Test tritium consumption
    consumption = neutronics.calculate_tritium_consumption(fusion_power)
    assert consumption > 0, "Tritium consumption should be positive"
    
    # Test TBR
    production = 1.2e20  # atoms/s
    consumption = 1e20  # atoms/s
    tbr = neutronics.calculate_tritium_breeding_ratio(production, consumption)
    assert tbr == 1.2, f"TBR should be 1.2, got {tbr}"
    
    print("✓ Neutronics tests passed")


if __name__ == '__main__':
    print("Running physics module tests...\n")
    test_plasma_physics()
    test_magnetic_confinement()
    test_power_balance()
    test_neutronics()
    print("\nAll tests passed! ✓")

