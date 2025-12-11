"""Material properties database for fusion reactor components.

Based on real material properties from fusion research.
"""

from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np


@dataclass
class Material:
    """Material properties for fusion reactor components."""
    
    name: str
    density: float  # kg/m³
    thermal_conductivity: float  # W/(m·K) at room temperature
    specific_heat: float  # J/(kg·K)
    melting_point: float  # K
    max_operating_temp: float  # K (conservative limit)
    neutron_absorption_cross_section: float  # barns (1 barn = 10^-28 m²)
    neutron_scattering_cross_section: float  # barns
    tritium_breeding_ratio: float  # For breeding materials (Li)
    thermal_expansion: float  # 1/K
    youngs_modulus: float  # Pa
    yield_strength: float  # Pa
    max_dpa: float = 100.0  # Maximum DPA before failure (default: 100)
    
    def thermal_conductivity_at_temp(self, temperature: float) -> float:
        """Calculate thermal conductivity at given temperature.
        
        Simple linear approximation for most materials.
        """
        # For most materials, thermal conductivity decreases with temperature
        # This is a simplified model
        T_ref = 300.0  # Reference temperature (K)
        if temperature < T_ref:
            return self.thermal_conductivity
        # Rough approximation: decreases ~20% per 1000K
        factor = 1.0 - 0.2 * (temperature - T_ref) / 1000.0
        return max(self.thermal_conductivity * factor, self.thermal_conductivity * 0.3)


class MaterialDatabase:
    """Database of materials used in fusion reactors."""
    
    def __init__(self):
        self._materials: Dict[str, Material] = {}
        self._initialize_materials()
    
    def _initialize_materials(self):
        """Initialize material database with real fusion reactor materials."""
        
        # Tungsten - First wall material (high melting point, low tritium retention)
        self._materials['tungsten'] = Material(
            name='Tungsten',
            density=19250.0,  # kg/m³
            thermal_conductivity=173.0,  # W/(m·K)
            specific_heat=132.0,  # J/(kg·K)
            melting_point=3695.0,  # K
            max_operating_temp=1500.0,  # K (conservative)
            neutron_absorption_cross_section=18.3,  # barns
            neutron_scattering_cross_section=4.7,  # barns
            tritium_breeding_ratio=0.0,
            thermal_expansion=4.5e-6,  # 1/K
            youngs_modulus=411e9,  # Pa
            yield_strength=550e6  # Pa
        )
        
        # Beryllium - First wall/plasma facing component
        self._materials['beryllium'] = Material(
            name='Beryllium',
            density=1848.0,
            thermal_conductivity=190.0,
            specific_heat=1825.0,
            melting_point=1560.0,
            max_operating_temp=800.0,  # Limited by embrittlement
            neutron_absorption_cross_section=0.0092,  # Very low
            neutron_scattering_cross_section=7.0,
            tritium_breeding_ratio=0.0,
            thermal_expansion=11.3e-6,
            youngs_modulus=287e9,
            yield_strength=240e6
        )
        
        # Lithium - Tritium breeding material
        self._materials['lithium'] = Material(
            name='Lithium',
            density=534.0,
            thermal_conductivity=84.8,
            specific_heat=3570.0,
            melting_point=453.7,
            max_operating_temp=1000.0,  # As liquid
            neutron_absorption_cross_section=70.5,  # High for breeding
            neutron_scattering_cross_section=1.4,
            tritium_breeding_ratio=1.0,  # Can breed tritium
            thermal_expansion=56e-6,
            youngs_modulus=4.9e9,
            yield_strength=1e6
        )
        
        # Lithium-Lead (LiPb) - Tritium breeding blanket
        self._materials['lithium_lead'] = Material(
            name='Lithium-Lead',
            density=10500.0,  # Approximate for Li17Pb83
            thermal_conductivity=15.0,
            specific_heat=195.0,
            melting_point=508.0,
            max_operating_temp=800.0,
            neutron_absorption_cross_section=45.0,
            neutron_scattering_cross_section=3.0,
            tritium_breeding_ratio=1.2,  # Can breed more than consumed
            thermal_expansion=20e-6,
            youngs_modulus=20e9,
            yield_strength=50e6
        )
        
        # EUROFER97 - Structural steel for fusion
        self._materials['eurofer97'] = Material(
            name='EUROFER97',
            density=7850.0,
            thermal_conductivity=28.0,
            specific_heat=500.0,
            melting_point=1800.0,
            max_operating_temp=550.0,  # Limited by irradiation
            neutron_absorption_cross_section=2.6,
            neutron_scattering_cross_section=11.0,
            tritium_breeding_ratio=0.0,
            thermal_expansion=12e-6,
            youngs_modulus=220e9,
            yield_strength=500e6
        )
        
        # Helium - Coolant
        self._materials['helium'] = Material(
            name='Helium',
            density=0.1785,  # At STP
            thermal_conductivity=0.1513,
            specific_heat=5193.0,
            melting_point=0.95,  # At pressure
            max_operating_temp=1000.0,
            neutron_absorption_cross_section=0.0,
            neutron_scattering_cross_section=0.8,
            tritium_breeding_ratio=0.0,
            thermal_expansion=0.00366,  # 1/K (ideal gas)
            youngs_modulus=0.0,
            yield_strength=0.0
        )
        
        # Water - Coolant (for comparison)
        self._materials['water'] = Material(
            name='Water',
            density=1000.0,
            thermal_conductivity=0.6,
            specific_heat=4180.0,
            melting_point=273.15,
            max_operating_temp=600.0,  # Supercritical
            neutron_absorption_cross_section=0.66,
            neutron_scattering_cross_section=103.0,
            tritium_breeding_ratio=0.0,
            thermal_expansion=207e-6,
            youngs_modulus=0.0,
            yield_strength=0.0
        )
        
        # Advanced materials (2024 research)
        # Tungsten-Copper composite (better thermal management)
        self._materials['tungsten_copper'] = Material(
            name='Tungsten-Copper Composite',
            density=15000.0,  # Between W and Cu
            thermal_conductivity=200.0,  # Better than pure W
            specific_heat=200.0,
            melting_point=1500.0,  # Lower than pure W but acceptable
            max_operating_temp=1500.0,  # Higher than standard
            neutron_absorption_cross_section=18.3,
            neutron_scattering_cross_section=4.7,
            tritium_breeding_ratio=0.0,
            thermal_expansion=5.0e-6,
            youngs_modulus=350e9,
            yield_strength=800e6
        )
        
        # HTS magnet material (conceptual)
        self._materials['hts_magnet'] = Material(
            name='HTS Magnet',
            density=8000.0,
            thermal_conductivity=50.0,
            specific_heat=200.0,
            melting_point=2000.0,
            max_operating_temp=77.0,  # Liquid nitrogen temperature
            neutron_absorption_cross_section=0.0,
            neutron_scattering_cross_section=0.0,
            tritium_breeding_ratio=0.0,
            thermal_expansion=10e-6,
            youngs_modulus=200e9,
            yield_strength=500e6
        )
    
    def get_material(self, name: str) -> Optional[Material]:
        """Get material by name."""
        return self._materials.get(name.lower())
    
    def list_materials(self) -> list:
        """List all available materials."""
        return list(self._materials.keys())
    
    def add_material(self, material: Material):
        """Add a custom material to the database."""
        self._materials[material.name.lower()] = material

