"""Neutronics calculations for fusion reactors.

Implements:
- Neutron flux calculations
- Tritium breeding
- Material damage (DPA - Displacements Per Atom)
- Neutron wall loading
"""

import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class NeutronicsState:
    """Neutronics state."""
    neutron_flux: float  # n/(m²·s)
    neutron_wall_loading: float  # MW/m²
    tritium_production_rate: float  # atoms/s
    tritium_breeding_ratio: float  # TBR
    dpa_rate: float  # DPA/year
    material_damage_accumulated: float  # DPA


class NeutronicsCalculator:
    """Neutronics calculations for fusion reactors."""
    
    # Physical constants
    NEUTRON_ENERGY_DT = 14.1e6 * 1.602176634e-19  # J (14.1 MeV)
    TRITIUM_ATOMIC_MASS = 3.016 * 1.66053906660e-27  # kg
    AVOGADRO = 6.02214076e23  # atoms/mol
    
    # D-T fusion produces 1 neutron per reaction
    NEUTRONS_PER_FUSION = 1.0
    
    # Tritium breeding reactions
    # Li-6 + n → T + He-4 (primary reaction)
    # Li-7 + n → T + He-4 + n (secondary, requires higher energy)
    LI6_BREEDING_CROSS_SECTION = 940.0  # barns at thermal energies
    LI7_BREEDING_CROSS_SECTION = 0.045  # barns (much lower)
    
    def __init__(self):
        """Initialize neutronics calculator."""
        pass
    
    def calculate_neutron_flux(self, fusion_power: float, surface_area: float) -> float:
        """Calculate neutron flux at first wall.
        
        Args:
            fusion_power: Fusion power in W
            surface_area: First wall surface area in m²
            
        Returns:
            Neutron flux in n/(m²·s)
        """
        if surface_area == 0:
            return 0.0
        
        # Each D-T fusion produces 1 neutron with 14.1 MeV
        # Neutron power = fusion_power * (14.1 / 17.6)
        neutron_power = fusion_power * (14.1 / 17.6)
        
        # Number of neutrons per second
        neutrons_per_second = neutron_power / self.NEUTRON_ENERGY_DT
        
        # Neutron flux (assuming uniform distribution)
        flux = neutrons_per_second / surface_area
        return flux
    
    def calculate_neutron_wall_loading(self, fusion_power: float, surface_area: float) -> float:
        """Calculate neutron wall loading.
        
        Args:
            fusion_power: Fusion power in W
            surface_area: First wall surface area in m²
            
        Returns:
            Neutron wall loading in MW/m²
        """
        if surface_area == 0:
            return 0.0
        
        # Neutron power
        neutron_power = fusion_power * (14.1 / 17.6)
        
        # Wall loading
        loading = (neutron_power / surface_area) / 1e6  # Convert to MW/m²
        return loading
    
    def calculate_tritium_production(self, neutron_flux: float, 
                                    lithium_density: float, thickness: float,
                                    li6_fraction: float = 0.075) -> float:
        """Calculate tritium production rate.
        
        Args:
            neutron_flux: Neutron flux in n/(m²·s)
            lithium_density: Lithium density in atoms/m³
            thickness: Breeding blanket thickness in m
            li6_fraction: Fraction of Li-6 (natural: 7.5%)
            
        Returns:
            Tritium production rate in atoms/s
        """
        # Effective cross-section (weighted average)
        sigma_eff = (li6_fraction * self.LI6_BREEDING_CROSS_SECTION + 
                    (1 - li6_fraction) * self.LI7_BREEDING_CROSS_SECTION)
        
        # Convert cross-section from barns to m²
        sigma_m2 = sigma_eff * 1e-28
        
        # Production rate: flux * density * cross-section * thickness
        production_rate = neutron_flux * lithium_density * sigma_m2 * thickness
        return production_rate
    
    def calculate_tritium_breeding_ratio(self, tritium_production: float,
                                        tritium_consumption: float) -> float:
        """Calculate tritium breeding ratio.
        
        TBR = production / consumption
        
        Args:
            tritium_production: Tritium production rate in atoms/s
            tritium_consumption: Tritium consumption rate in atoms/s
            
        Returns:
            Tritium breeding ratio
        """
        if tritium_consumption == 0:
            return float('inf') if tritium_production > 0 else 0.0
        return tritium_production / tritium_consumption
    
    def calculate_tritium_consumption(self, fusion_power: float) -> float:
        """Calculate tritium consumption rate.
        
        Args:
            fusion_power: Fusion power in W
            
        Returns:
            Tritium consumption rate in atoms/s
        """
        # Each D-T fusion consumes 1 tritium atom
        # Energy per fusion = 17.6 MeV
        energy_per_fusion = 17.6e6 * 1.602176634e-19  # J
        
        if energy_per_fusion == 0:
            return 0.0
        
        consumption_rate = fusion_power / energy_per_fusion
        return consumption_rate
    
    def calculate_dpa_rate(self, neutron_flux: float, dpa_cross_section: float = 1e-24) -> float:
        """Calculate displacement per atom (DPA) rate.
        
        Simplified model for material damage.
        
        Args:
            neutron_flux: Neutron flux in n/(m²·s)
            dpa_cross_section: Effective DPA cross-section in m²
            
        Returns:
            DPA rate in DPA/year
        """
        # DPA rate = flux * cross-section * time
        # Convert to per year
        seconds_per_year = 365.25 * 24 * 3600
        
        dpa_per_second = neutron_flux * dpa_cross_section
        dpa_per_year = dpa_per_second * seconds_per_year
        
        return dpa_per_year
    
    def calculate_neutronics_state(self, fusion_power: float, surface_area: float,
                                  lithium_density: Optional[float] = None,
                                  blanket_thickness: float = 1.0,
                                  li6_fraction: float = 0.075,
                                  initial_dpa: float = 0.0) -> NeutronicsState:
        """Calculate complete neutronics state.
        
        Args:
            fusion_power: Fusion power in W
            surface_area: First wall surface area in m²
            lithium_density: Lithium density in atoms/m³ (if None, calculated)
            blanket_thickness: Breeding blanket thickness in m
            li6_fraction: Fraction of Li-6
            initial_dpa: Initial accumulated DPA
            
        Returns:
            NeutronicsState object
        """
        # Neutron flux
        neutron_flux = self.calculate_neutron_flux(fusion_power, surface_area)
        
        # Neutron wall loading
        wall_loading = self.calculate_neutron_wall_loading(fusion_power, surface_area)
        
        # Tritium consumption
        tritium_consumption = self.calculate_tritium_consumption(fusion_power)
        
        # Tritium production (if breeding blanket present)
        if lithium_density is None:
            # Estimate from material density (Li: ~534 kg/m³)
            li_atomic_mass = 6.941 * 1.66053906660e-27  # kg
            li_atoms_per_m3 = 534.0 / li_atomic_mass
            lithium_density = li_atoms_per_m3
        
        tritium_production = self.calculate_tritium_production(
            neutron_flux, lithium_density, blanket_thickness, li6_fraction
        )
        
        # Tritium breeding ratio
        tbr = self.calculate_tritium_breeding_ratio(tritium_production, tritium_consumption)
        
        # DPA rate
        dpa_rate = self.calculate_dpa_rate(neutron_flux)
        
        # Accumulated damage: initial + rate * time
        # dpa_rate is in DPA/year, so we need operation time in years
        # For now, if initial_dpa is provided, use it directly (it should already include time)
        # Otherwise, this will be updated by the simulator with proper time tracking
        material_damage = initial_dpa  # Simulator will update this with proper time integration
        
        return NeutronicsState(
            neutron_flux=neutron_flux,
            neutron_wall_loading=wall_loading,
            tritium_production_rate=tritium_production,
            tritium_breeding_ratio=tbr,
            dpa_rate=dpa_rate,
            material_damage_accumulated=material_damage
        )

