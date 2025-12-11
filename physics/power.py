"""Power balance calculations for fusion reactors.

Implements:
- Q factor (fusion power / input power)
- Power balance
- Energy efficiency
- Heating power requirements
"""

import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class PowerBalance:
    """Power balance state."""
    fusion_power: float  # W
    input_power: float  # W (heating, current drive, etc.)
    output_power: float  # W (net electrical output)
    thermal_power: float  # W (total thermal power)
    q_factor: float  # Fusion power / input power
    net_efficiency: float  # Output / input
    breakeven: bool  # Q > 1
    ignition: bool  # Q → ∞ (self-sustaining)


class PowerCalculator:
    """Power balance calculations for fusion reactors."""
    
    # Typical efficiencies
    THERMAL_TO_ELECTRICAL_EFFICIENCY = 0.33  # ~33% for steam turbines
    CURRENT_DRIVE_EFFICIENCY = 0.4  # ~40% for current drive systems
    HEATING_EFFICIENCY = 0.6  # ~60% for heating systems
    
    def __init__(self):
        """Initialize power calculator."""
        pass
    
    def calculate_q_factor(self, fusion_power: float, input_power: float) -> float:
        """Calculate Q factor.
        
        Q = P_fusion / P_input
        
        Args:
            fusion_power: Fusion power in W
            input_power: Input power in W
            
        Returns:
            Q factor (infinity if input_power = 0 and fusion_power > 0)
        """
        if input_power == 0:
            if fusion_power > 0:
                return float('inf')
            return 0.0
        return fusion_power / input_power
    
    def calculate_input_power(self, ohmic_heating: float, auxiliary_heating: float,
                            current_drive: float) -> float:
        """Calculate total input power.
        
        Args:
            ohmic_heating: Ohmic heating power in W
            auxiliary_heating: Auxiliary heating (NBI, ICRH, etc.) in W
            current_drive: Current drive power in W
            
        Returns:
            Total input power in W
        """
        return ohmic_heating + auxiliary_heating + current_drive
    
    def calculate_ohmic_heating(self, plasma_current: float, plasma_resistance: float) -> float:
        """Calculate ohmic heating power.
        
        P = I²R
        
        Args:
            plasma_current: Plasma current in A
            plasma_resistance: Plasma resistance in Ω
            
        Returns:
            Ohmic heating power in W
        """
        return plasma_current**2 * plasma_resistance
    
    def calculate_plasma_resistance(self, major_radius: float, minor_radius: float,
                                    temperature: float, density: float) -> float:
        """Calculate plasma resistance (Spitzer resistivity).
        
        Simplified Spitzer resistivity model.
        
        Args:
            major_radius: Major radius in m
            minor_radius: Minor radius in m
            temperature: Plasma temperature in K
            density: Plasma density in m⁻³
            
        Returns:
            Plasma resistance in Ω
        """
        # Spitzer resistivity: η = m_e * ν_ei / (n_e * e²)
        # More accurate: η ≈ 65 * Z * ln(Λ) / T^1.5 (in Ω·m, T in eV)
        # For D-T plasma, Z_eff ≈ 1.5 (including alpha particles)
        
        T_ev = temperature * 8.617333262e-5  # Convert K to eV
        if T_ev <= 0:
            return float('inf')
        
        # Coulomb logarithm: ln(Λ) ≈ 15-20 for fusion plasmas
        # More accurate: ln(Λ) ≈ 17.3 + 1.5*ln(T_keV) - 0.5*ln(n_20)
        T_kev = T_ev / 1000.0
        n_20 = density / 1e20
        if T_kev > 0 and n_20 > 0:
            ln_lambda = 17.3 + 1.5 * np.log(T_kev) - 0.5 * np.log(n_20)
            ln_lambda = max(10.0, min(20.0, ln_lambda))  # Bound between 10-20
        else:
            ln_lambda = 15.0
        
        Z_eff = 1.5  # Effective charge for D-T plasma
        
        # Resistivity in Ω·m (Spitzer formula)
        # η = 65 * Z_eff * ln(Λ) / T^1.5
        resistivity = 65.0 * Z_eff * ln_lambda / (T_ev**1.5)
        
        # For tokamaks, the effective resistance is much lower due to
        # current profile and neoclassical effects
        # Apply neoclassical correction factor (typically 0.1-0.3)
        neoclassical_factor = 0.2
        resistivity *= neoclassical_factor
        
        # Resistance: R = ρ * L / A
        # For tokamak: effective length is toroidal circumference
        # Effective area is plasma cross-section
        length = 2.0 * np.pi * major_radius
        area = np.pi * minor_radius**2
        
        if area == 0:
            return float('inf')
        
        resistance = resistivity * length / area
        
        # Ensure reasonable bounds (typically 0.1-10 μΩ for large tokamaks)
        resistance = max(1e-7, min(1e-5, resistance))
        
        return resistance
    
    def calculate_thermal_power(self, fusion_power: float, input_power: float,
                                bremsstrahlung_loss: float, synchrotron_loss: float) -> float:
        """Calculate total thermal power.
        
        Thermal power = fusion power + input power - radiation losses
        
        Args:
            fusion_power: Fusion power in W
            input_power: Input power in W
            bremsstrahlung_loss: Bremsstrahlung loss in W
            synchrotron_loss: Synchrotron loss in W
            
        Returns:
            Total thermal power in W
        """
        radiation_loss = bremsstrahlung_loss + synchrotron_loss
        thermal = fusion_power + input_power - radiation_loss
        return max(0.0, thermal)
    
    def calculate_electrical_output(self, thermal_power: float) -> float:
        """Calculate electrical output power.
        
        Args:
            thermal_power: Thermal power in W
            
        Returns:
            Electrical output power in W
        """
        return thermal_power * self.THERMAL_TO_ELECTRICAL_EFFICIENCY
    
    def calculate_net_power(self, electrical_output: float, input_power: float) -> float:
        """Calculate net power output.
        
        Args:
            electrical_output: Electrical output power in W
            input_power: Input power in W
            
        Returns:
            Net power in W
        """
        return electrical_output - input_power
    
    def check_breakeven(self, q_factor: float) -> bool:
        """Check if reactor is at breakeven (Q > 1).
        
        Args:
            q_factor: Q factor
            
        Returns:
            True if Q > 1
        """
        return q_factor > 1.0
    
    def check_ignition(self, q_factor: float, threshold: float = 10.0) -> bool:
        """Check if reactor is near ignition (self-sustaining).
        
        Args:
            q_factor: Q factor
            threshold: Threshold for "ignition" (default 10)
            
        Returns:
            True if Q > threshold
        """
        return q_factor > threshold or np.isinf(q_factor)
    
    def calculate_power_balance(self, fusion_power: float, input_power: float,
                               bremsstrahlung_loss: float, synchrotron_loss: float) -> PowerBalance:
        """Calculate complete power balance.
        
        Args:
            fusion_power: Fusion power in W
            input_power: Input power in W
            bremsstrahlung_loss: Bremsstrahlung loss in W
            synchrotron_loss: Synchrotron loss in W
            
        Returns:
            PowerBalance object
        """
        # Q factor
        q_factor = self.calculate_q_factor(fusion_power, input_power)
        
        # Thermal power
        thermal_power = self.calculate_thermal_power(fusion_power, input_power,
                                                     bremsstrahlung_loss, synchrotron_loss)
        
        # Electrical output
        electrical_output = self.calculate_electrical_output(thermal_power)
        
        # Net power
        net_power = self.calculate_net_power(electrical_output, input_power)
        
        # Efficiency
        if input_power > 0:
            net_efficiency = net_power / input_power
        else:
            net_efficiency = float('inf') if net_power > 0 else 0.0
        
        # Breakeven and ignition
        breakeven = self.check_breakeven(q_factor)
        ignition = self.check_ignition(q_factor)
        
        return PowerBalance(
            fusion_power=fusion_power,
            input_power=input_power,
            output_power=net_power,
            thermal_power=thermal_power,
            q_factor=q_factor,
            net_efficiency=net_efficiency,
            breakeven=breakeven,
            ignition=ignition
        )

