"""Magnetic confinement calculations for tokamak fusion reactors.

Implements:
- Tokamak geometry
- Magnetic field calculations
- Beta parameter (plasma pressure / magnetic pressure)
- Safety factor (q)
- Confinement time scaling
"""

import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TokamakGeometry:
    """Tokamak geometry parameters."""
    major_radius: float  # R₀ in m
    minor_radius: float  # a in m
    aspect_ratio: float  # R₀/a
    elongation: float  # κ (vertical/horizontal)
    triangularity: float  # δ
    plasma_volume: float  # m³


@dataclass
class MagneticState:
    """Magnetic field state."""
    toroidal_field: float  # B₀ in T
    poloidal_field: float  # B_p in T
    total_field: float  # T
    beta: float  # Plasma beta (pressure ratio)
    safety_factor: float  # q
    magnetic_pressure: float  # Pa
    plasma_pressure: float  # Pa


class MagneticConfinement:
    """Magnetic confinement calculations for tokamaks."""
    
    # Physical constants
    MU_0 = 4.0 * np.pi * 1e-7  # Permeability of free space (H/m)
    K_B = 1.380649e-23  # Boltzmann constant (J/K)
    
    def __init__(self):
        """Initialize magnetic confinement calculator."""
        pass
    
    def calculate_plasma_volume(self, major_radius: float, minor_radius: float,
                                elongation: float = 1.0) -> float:
        """Calculate plasma volume for tokamak.
        
        V ≈ 2π² R₀ a² κ
        
        Args:
            major_radius: Major radius R₀ in m
            minor_radius: Minor radius a in m
            elongation: Elongation κ
            
        Returns:
            Volume in m³
        """
        volume = 2.0 * np.pi**2 * major_radius * minor_radius**2 * elongation
        return volume
    
    def calculate_plasma_surface_area(self, major_radius: float, minor_radius: float,
                                     elongation: float = 1.0) -> float:
        """Calculate plasma surface area.
        
        Approximate formula for toroidal surface.
        
        Args:
            major_radius: Major radius R₀ in m
            minor_radius: Minor radius a in m
            elongation: Elongation κ
            
        Returns:
            Surface area in m²
        """
        # Approximate: S ≈ 4π² R₀ a κ
        area = 4.0 * np.pi**2 * major_radius * minor_radius * elongation
        return area
    
    def calculate_tokamak_geometry(self, major_radius: float, minor_radius: float,
                                   elongation: float = 1.0,
                                   triangularity: float = 0.0) -> TokamakGeometry:
        """Calculate tokamak geometry parameters.
        
        Args:
            major_radius: Major radius R₀ in m
            minor_radius: Minor radius a in m
            elongation: Elongation κ
            triangularity: Triangularity δ
            
        Returns:
            TokamakGeometry object
        """
        aspect_ratio = major_radius / minor_radius
        volume = self.calculate_plasma_volume(major_radius, minor_radius, elongation)
        
        return TokamakGeometry(
            major_radius=major_radius,
            minor_radius=minor_radius,
            aspect_ratio=aspect_ratio,
            elongation=elongation,
            triangularity=triangularity,
            plasma_volume=volume
        )
    
    def calculate_safety_factor(self, major_radius: float, minor_radius: float,
                               toroidal_field: float, plasma_current: float) -> float:
        """Calculate safety factor q.
        
        q ≈ (2π a² B₀) / (μ₀ R₀ I_p)
        
        Args:
            major_radius: Major radius R₀ in m
            minor_radius: Minor radius a in m
            toroidal_field: Toroidal field B₀ in T
            plasma_current: Plasma current I_p in A
            
        Returns:
            Safety factor q
        """
        if plasma_current == 0:
            return float('inf')
        
        q = (2.0 * np.pi * minor_radius**2 * toroidal_field) / (self.MU_0 * major_radius * plasma_current)
        return q
    
    def calculate_beta(self, plasma_pressure: float, magnetic_pressure: float) -> float:
        """Calculate plasma beta (pressure ratio).
        
        β = p_plasma / p_magnetic
        
        Args:
            plasma_pressure: Plasma pressure in Pa
            magnetic_pressure: Magnetic pressure in Pa
            
        Returns:
            Beta parameter
        """
        if magnetic_pressure == 0:
            return float('inf')
        return plasma_pressure / magnetic_pressure
    
    def calculate_magnetic_pressure(self, magnetic_field: float) -> float:
        """Calculate magnetic pressure.
        
        p_mag = B² / (2μ₀)
        
        Args:
            magnetic_field: Magnetic field strength in T
            
        Returns:
            Magnetic pressure in Pa
        """
        pressure = magnetic_field**2 / (2.0 * self.MU_0)
        return pressure
    
    def calculate_plasma_pressure(self, density: float, temperature: float) -> float:
        """Calculate plasma pressure.
        
        p = nkT (ideal gas law for plasma)
        
        Args:
            density: Plasma density in m⁻³
            temperature: Plasma temperature in K
            
        Returns:
            Plasma pressure in Pa
        """
        pressure = density * self.K_B * temperature
        return pressure
    
    def calculate_poloidal_field(self, major_radius: float, plasma_current: float) -> float:
        """Calculate poloidal magnetic field.
        
        B_p ≈ (μ₀ I_p) / (2π a)
        
        Args:
            major_radius: Major radius R₀ in m (approximation)
            plasma_current: Plasma current I_p in A
            
        Returns:
            Poloidal field in T
        """
        # Simplified: using major radius as approximation
        B_p = (self.MU_0 * plasma_current) / (2.0 * np.pi * major_radius)
        return B_p
    
    def calculate_confinement_time_scaling(self, major_radius: float, minor_radius: float,
                                          density: float, temperature: float,
                                          toroidal_field: float, plasma_current: float,
                                          elongation: float = 1.0,
                                          heating_power_MW: Optional[float] = None,
                                          ohmic_heating_MW: Optional[float] = None,
                                          use_improved_scaling: bool = True) -> float:
        """Calculate energy confinement time using ITER scaling.
        
        Uses ITER-98(y,2) scaling law:
        τ_E = 0.0562 * I^0.93 * B^0.15 * P^-0.69 * n^0.41 * M^0.19 * R^1.97 * κ^0.78 * ε^0.58
        
        Based on research: Ohmic heating should be treated separately from external heating
        for confinement scaling, as it's part of plasma self-heating.
        
        Args:
            major_radius: Major radius R₀ in m
            minor_radius: Minor radius a in m
            density: Plasma density in m⁻³
            temperature: Plasma temperature in K
            toroidal_field: Toroidal field B₀ in T
            plasma_current: Plasma current I_p in A
            elongation: Elongation κ
            heating_power_MW: External heating power in MW (NBI, ICRH, ECRH)
            ohmic_heating_MW: Ohmic heating power in MW (optional, treated separately)
            use_improved_scaling: Use improved scaling that separates ohmic heating
            
        Returns:
            Confinement time in s
        """
        from typing import Optional
        
        # Convert current to MA
        I_MA = plasma_current / 1e6
        
        # Heating power - use provided value or estimate
        if heating_power_MW is None:
            # Rough estimate: assume some input power
            # For ITER: ~50-100 MW typical
            P_ext_MW = 50.0  # Default estimate
        else:
            P_ext_MW = heating_power_MW
        
        if P_ext_MW <= 0:
            P_ext_MW = 1.0  # Avoid division by zero
        
        # Improved scaling: Separate ohmic heating from external heating
        # Research shows ohmic heating contributes differently to confinement
        if use_improved_scaling and ohmic_heating_MW is not None:
            # Ohmic heating is less effective for confinement (reduced exponent)
            # Use effective power: P_eff = P_ext + 0.3 * P_ohmic
            # The 0.3 factor accounts for ohmic heating being less effective
            P_ohmic_MW = ohmic_heating_MW
            P_eff_MW = P_ext_MW + 0.3 * P_ohmic_MW
        else:
            # Traditional scaling: include all heating
            if ohmic_heating_MW is not None:
                P_eff_MW = P_ext_MW + ohmic_heating_MW
            else:
                P_eff_MW = P_ext_MW
        
        # Aspect ratio
        epsilon = minor_radius / major_radius
        
        # ITER-98(y,2) scaling
        # τ_E in seconds
        # M = 2.5 for D-T plasma (average ion mass in amu)
        M = 2.5
        
        tau_E = (0.0562 * (I_MA**0.93) * (toroidal_field**0.15) * 
                (P_eff_MW**-0.69) * ((density/1e20)**0.41) * (M**0.19) *
                (major_radius**1.97) * (elongation**0.78) * (epsilon**0.58))
        
        # NBI confinement improvement (from research: NBI can improve confinement via rotation)
        # If using NBI (auxiliary heating), apply improvement factor
        if use_improved_scaling and P_ext_MW > 10.0:  # Assume NBI if significant external heating
            # NBI-induced rotation can improve confinement by 10-20%
            nbi_improvement = 1.15  # 15% improvement
            tau_E *= nbi_improvement
        
        # High elongation improvement (from research: higher elongation improves confinement)
        if elongation > 1.5:
            elongation_bonus = 1.0 + 0.1 * (elongation - 1.5)  # Up to 10% bonus
            tau_E *= min(elongation_bonus, 1.15)  # Cap at 15% improvement
        
        # Reasonable bounds: 0.1s to 1000s
        return max(0.1, min(1000.0, tau_E))
    
    def calculate_magnetic_state(self, toroidal_field: float, plasma_current: float,
                                major_radius: float, minor_radius: float,
                                density: float, temperature: float) -> MagneticState:
        """Calculate complete magnetic field state.
        
        Args:
            toroidal_field: Toroidal field B₀ in T
            plasma_current: Plasma current I_p in A
            major_radius: Major radius R₀ in m
            minor_radius: Minor radius a in m
            density: Plasma density in m⁻³
            temperature: Plasma temperature in K
            
        Returns:
            MagneticState object
        """
        # Poloidal field
        poloidal_field = self.calculate_poloidal_field(major_radius, plasma_current)
        
        # Total field (approximate)
        total_field = np.sqrt(toroidal_field**2 + poloidal_field**2)
        
        # Pressures
        magnetic_pressure = self.calculate_magnetic_pressure(toroidal_field)
        plasma_pressure = self.calculate_plasma_pressure(density, temperature)
        
        # Beta
        beta = self.calculate_beta(plasma_pressure, magnetic_pressure)
        
        # Safety factor
        safety_factor = self.calculate_safety_factor(major_radius, minor_radius,
                                                     toroidal_field, plasma_current)
        
        return MagneticState(
            toroidal_field=toroidal_field,
            poloidal_field=poloidal_field,
            total_field=total_field,
            beta=beta,
            safety_factor=safety_factor,
            magnetic_pressure=magnetic_pressure,
            plasma_pressure=plasma_pressure
        )

