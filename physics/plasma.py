"""Plasma physics calculations for fusion reactors.

Implements:
- Lawson criterion
- Triple product (nτT)
- D-T fusion reaction rates
- Plasma temperature and density calculations
"""

import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class PlasmaState:
    """Current state of the plasma."""
    temperature: float  # K
    density: float  # m⁻³
    confinement_time: float  # s
    triple_product: float  # m⁻³·s·K
    fusion_power_density: float  # W/m³
    bremsstrahlung_loss: float  # W/m³
    synchrotron_loss: float  # W/m³
    total_loss: float  # W/m³
    net_power_density: float  # W/m³
    meets_lawson_criterion: bool


class PlasmaPhysics:
    """Plasma physics calculations for fusion reactors."""
    
    # Physical constants
    K_B = 1.380649e-23  # Boltzmann constant (J/K)
    E_CHARGE = 1.602176634e-19  # Elementary charge (C)
    M_PROTON = 1.67262192369e-27  # Proton mass (kg)
    M_DEUTERON = 2.014 * M_PROTON  # Deuterium mass
    M_TRITON = 3.016 * M_PROTON  # Tritium mass
    M_ALPHA = 4.0026 * M_PROTON  # Alpha particle mass
    
    # D-T fusion cross-section parameters (from research)
    # More accurate formula: <σv> ≈ C1 * T^(-2/3) * exp(-C2/T^(1/3))
    # For D-T: <σv> in m³/s, T in keV
    # Approximate: <σv> ≈ 3.7e-19 * T^(-2/3) * exp(-19.94/T^(1/3)) for T > 1 keV
    # Or use tabulated values with interpolation
    DT_FUSION_ENERGY = 17.6e6 * E_CHARGE  # J (17.6 MeV per reaction)
    
    # Lawson criterion for D-T fusion
    # nτ ≥ 10²⁰ m⁻³·s at T ≈ 10-15 keV
    LAWSON_NTAU_MIN = 1e20  # m⁻³·s
    LAWSON_TEMP_OPTIMAL = 15e6  # K (≈13 keV)
    
    def __init__(self):
        """Initialize plasma physics calculator."""
        pass
    
    def calculate_fusion_reaction_rate_coefficient(self, temperature_kev: float) -> float:
        """Calculate <σv> (velocity-averaged cross-section times velocity).
        
        Uses empirical formula for D-T fusion.
        <σv> ≈ 3.7e-19 * T^(-2/3) * exp(-19.94/T^(1/3))  [m³/s]
        
        Args:
            temperature_kev: Plasma temperature in keV
            
        Returns:
            <σv> in m³/s
        """
        if temperature_kev <= 0:
            return 0.0
        
        if temperature_kev < 0.1:
            return 0.0
        
        # <σv> formula for D-T fusion
        T_third = np.power(temperature_kev, 1.0/3.0)
        T_neg23 = np.power(temperature_kev, -2.0/3.0)
        
        # Coefficients for D-T fusion
        C1 = 3.7e-19  # m³/s
        C2 = 19.94  # keV^(1/3)
        
        sigma_v = C1 * T_neg23 * np.exp(-C2 / T_third)
        return max(0.0, sigma_v)
    
    def calculate_fusion_reaction_rate(self, density: float, temperature: float) -> float:
        """Calculate D-T fusion reaction rate.
        
        Args:
            density: Plasma density in m⁻³ (assumes equal D and T densities)
            temperature: Plasma temperature in K
            
        Returns:
            Reaction rate in reactions/(m³·s)
        """
        # Convert temperature to keV
        T_kev = temperature * self.K_B / (self.E_CHARGE * 1000.0)
        
        # Get <σv> directly (more accurate)
        sigma_v = self.calculate_fusion_reaction_rate_coefficient(T_kev)
        
        # Reaction rate: n_D * n_T * <σv>
        # Assuming equal densities: n_D = n_T = n/2
        n_d = density / 2.0
        n_t = density / 2.0
        
        reaction_rate = n_d * n_t * sigma_v
        return max(0.0, reaction_rate)
    
    def calculate_fusion_power_density(self, density: float, temperature: float) -> float:
        """Calculate fusion power density.
        
        Args:
            density: Plasma density in m⁻³
            temperature: Plasma temperature in K
            
        Returns:
            Power density in W/m³
        """
        reaction_rate = self.calculate_fusion_reaction_rate(density, temperature)
        power_density = reaction_rate * self.DT_FUSION_ENERGY
        return power_density
    
    def calculate_bremsstrahlung_loss(self, density: float, temperature: float) -> float:
        """Calculate bremsstrahlung radiation loss.
        
        Args:
            density: Plasma density in m⁻³
            temperature: Plasma temperature in K
            
        Returns:
            Power loss density in W/m³
        """
        # Bremsstrahlung: P_brem ≈ 5.35e-37 * n² * sqrt(T) * Z_eff²
        # For D-T plasma, Z_eff ≈ 1.5 (including alpha particles)
        Z_eff = 1.5
        T_kev = temperature * self.K_B / (self.E_CHARGE * 1000.0)
        
        if T_kev <= 0:
            return 0.0
        
        power_loss = 5.35e-37 * density**2 * np.sqrt(T_kev) * Z_eff**2
        return power_loss
    
    def calculate_synchrotron_loss(self, density: float, temperature: float, 
                                   magnetic_field: float) -> float:
        """Calculate synchrotron radiation loss.
        
        Args:
            density: Plasma density in m⁻³
            temperature: Plasma temperature in K
            magnetic_field: Magnetic field strength in T
            
        Returns:
            Power loss density in W/m³
        """
        # Synchrotron radiation formula (more accurate)
        # P_sync ≈ 6.21e-16 * B² * T² * n * (1 - R) where R is reflection coefficient
        # For typical tokamak conditions, synchrotron is usually much smaller than bremsstrahlung
        T_kev = temperature * self.K_B / (self.E_CHARGE * 1000.0)
        
        if T_kev <= 0:
            return 0.0
        
        # More realistic formula: synchrotron is typically 10-100x smaller than bremsstrahlung
        # Simplified: P_sync ≈ 1e-17 * B² * T^2.5 * n (rough approximation)
        # Or use: P_sync ≈ 0.1 * P_brem for typical conditions
        # For now, use a more conservative estimate
        power_loss = 1e-17 * magnetic_field**2 * np.power(T_kev, 2.5) * density
        
        # Cap synchrotron loss to be reasonable compared to bremsstrahlung
        bremsstrahlung = self.calculate_bremsstrahlung_loss(density, temperature)
        power_loss = min(power_loss, bremsstrahlung * 0.5)  # Synchrotron < 50% of bremsstrahlung
        
        return power_loss
    
    def calculate_triple_product(self, density: float, confinement_time: float, 
                                temperature: float) -> float:
        """Calculate triple product nτT.
        
        Args:
            density: Plasma density in m⁻³
            confinement_time: Energy confinement time in s
            temperature: Plasma temperature in K
            
        Returns:
            Triple product in m⁻³·s·K
        """
        return density * confinement_time * temperature
    
    def check_lawson_criterion(self, density: float, confinement_time: float, 
                              temperature: float) -> Tuple[bool, float, float]:
        """Check if plasma meets Lawson criterion for ignition.
        
        Args:
            density: Plasma density in m⁻³
            confinement_time: Energy confinement time in s
            temperature: Plasma temperature in K
            
        Returns:
            Tuple of (meets_criterion, nτ, required_nτ)
        """
        n_tau = density * confinement_time
        required_n_tau = self.LAWSON_NTAU_MIN
        
        # Check temperature is in acceptable range for D-T fusion
        # Optimal temperature: 10-20 keV, but can work up to ~50 keV
        # Convert to keV for comparison
        T_kev = temperature * self.K_B / (self.E_CHARGE * 1000.0)
        # Acceptable range: 5-60 keV (wider range - fusion can occur at higher T, just less optimal)
        optimal_temp_range_kev = (5.0, 60.0)  # keV
        temp_ok = optimal_temp_range_kev[0] <= T_kev <= optimal_temp_range_kev[1]
        
        meets_criterion = (n_tau >= required_n_tau) and temp_ok
        
        return meets_criterion, n_tau, required_n_tau
    
    def calculate_plasma_state(self, density: float, temperature: float,
                              confinement_time: float, magnetic_field: float) -> PlasmaState:
        """Calculate complete plasma state.
        
        Args:
            density: Plasma density in m⁻³
            temperature: Plasma temperature in K
            confinement_time: Energy confinement time in s
            magnetic_field: Magnetic field strength in T
            
        Returns:
            PlasmaState object with all calculated parameters
        """
        # Fusion power
        fusion_power = self.calculate_fusion_power_density(density, temperature)
        
        # Losses
        bremsstrahlung = self.calculate_bremsstrahlung_loss(density, temperature)
        synchrotron = self.calculate_synchrotron_loss(density, temperature, magnetic_field)
        total_loss = bremsstrahlung + synchrotron
        
        # Net power
        net_power = fusion_power - total_loss
        
        # Triple product
        triple_product = self.calculate_triple_product(density, confinement_time, temperature)
        
        # Lawson criterion
        meets_lawson, n_tau, required_n_tau = self.check_lawson_criterion(
            density, confinement_time, temperature
        )
        
        return PlasmaState(
            temperature=temperature,
            density=density,
            confinement_time=confinement_time,
            triple_product=triple_product,
            fusion_power_density=fusion_power,
            bremsstrahlung_loss=bremsstrahlung,
            synchrotron_loss=synchrotron,
            total_loss=total_loss,
            net_power_density=net_power,
            meets_lawson_criterion=meets_lawson
        )

