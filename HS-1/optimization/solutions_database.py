"""Database of research-based solutions for fusion reactor optimization.

Based on recent fusion research (2020-2024) and ITER/SPARC designs.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from materials.materials import MaterialDatabase


@dataclass
class ResearchSolution:
    """A research-based solution for fusion reactor issues."""
    name: str
    description: str
    source: str
    year: int
    parameters: Dict
    materials: Optional[List[str]] = None
    effectiveness: float = 1.0  # 0-1 scale


class SolutionsDatabase:
    """Database of research-based solutions."""
    
    def __init__(self):
        """Initialize solutions database."""
        self.solutions = self._load_solutions()
    
    def _load_solutions(self) -> List[ResearchSolution]:
        """Load research-based solutions."""
        solutions = []
        
        # High-Temperature Superconductor (HTS) magnets - 2024 research
        solutions.append(ResearchSolution(
            name="HTS High-Field Magnets",
            description="High-temperature superconductor magnets enable higher magnetic fields (12-20 T) with lower power consumption",
            source="SPARC, Commonwealth Fusion Systems, 2024",
            year=2024,
            parameters={
                'toroidal_field': (12.0, 20.0),  # T (SPARC: 12.2 T)
                'input_power_multiplier': 0.7,  # 30% less power for magnets
            },
            materials=['hts_magnet'],
            effectiveness=0.9
        ))
        
        # Spherical tokamak geometry - lower aspect ratio
        solutions.append(ResearchSolution(
            name="Spherical Tokamak Geometry",
            description="Low aspect ratio (R/a ~ 1.5-2.0) improves safety factor and stability",
            source="MAST, ST40, 2020-2024",
            year=2024,
            parameters={
                'major_radius': (1.5, 3.0),  # m
                'minor_radius': (1.0, 2.0),  # m
                'aspect_ratio_target': 1.8,  # Target aspect ratio
            },
            effectiveness=0.85
        ))
        
        # Advanced current drive - lower power
        solutions.append(ResearchSolution(
            name="Advanced Current Drive (ECCD)",
            description="Electron Cyclotron Current Drive with improved efficiency",
            source="ITER, 2023",
            year=2023,
            parameters={
                'current_drive_efficiency': 0.6,  # Improved from 0.4
                'current_drive_power_multiplier': 0.8,  # 20% less power needed
            },
            effectiveness=0.8
        ))
        
        # Advanced fueling methods
        solutions.append(ResearchSolution(
            name="Pellet Injection Fueling",
            description="Cryogenic pellet injection for efficient density control",
            source="ITER, JET, 2023",
            year=2023,
            parameters={
                'fueling_efficiency': 1.2,  # 20% more efficient
                'density_control': True,
            },
            effectiveness=0.75
        ))
        
        # Advanced first wall materials
        solutions.append(ResearchSolution(
            name="Tungsten-Copper Composite",
            description="Tungsten-copper composite for better thermal management",
            source="ITER, 2023",
            year=2023,
            parameters={
                'max_operating_temp': 1500.0,  # K (higher than pure W)
                'thermal_conductivity_multiplier': 1.5,
            },
            materials=['tungsten_copper'],
            effectiveness=0.85
        ))
        
        # Advanced tritium breeding
        solutions.append(ResearchSolution(
            name="Enhanced Lithium Breeding",
            description="Optimized lithium-6 enrichment and blanket design",
            source="ITER, 2023",
            year=2023,
            parameters={
                'tritium_breeding_ratio_boost': 1.15,  # 15% improvement
                'li6_fraction': 0.15,  # Enriched (natural: 7.5%)
            },
            effectiveness=0.8
        ))
        
        # Plasma control algorithms
        solutions.append(ResearchSolution(
            name="AI-Powered Plasma Control",
            description="Machine learning algorithms for real-time plasma control",
            source="Various, 2023-2024",
            year=2024,
            parameters={
                'stability_improvement': 1.1,  # 10% better stability
                'q_factor_tolerance': 0.1,  # Can operate closer to limits
            },
            effectiveness=0.7
        ))
        
        # Advanced heating methods
        solutions.append(ResearchSolution(
            name="Optimized Neutral Beam Injection",
            description="Improved NBI efficiency and power deposition",
            source="ITER, 2023",
            year=2023,
            parameters={
                'heating_efficiency': 0.7,  # Improved from 0.6
                'auxiliary_heating_multiplier': 0.9,  # 10% less power needed
            },
            effectiveness=0.75
        ))
        
        # Improved confinement scaling (from research)
        solutions.append(ResearchSolution(
            name="Improved Confinement Scaling",
            description="Separate ohmic heating from external heating in confinement scaling",
            source="ITER-98 scaling analysis, 2024",
            year=2024,
            parameters={
                'confinement_improvement': 1.2,  # 20% improvement
                'ohmic_heating_factor': 0.3,  # Ohmic heating less effective
            },
            effectiveness=0.9
        ))
        
        # Plasma rotation from NBI
        solutions.append(ResearchSolution(
            name="NBI-Induced Plasma Rotation",
            description="Neutral beam injection induces plasma rotation, improving confinement",
            source="ORNL, 2024",
            year=2024,
            parameters={
                'confinement_improvement': 1.15,  # 15% improvement from rotation
                'requires_nbi': True,
            },
            effectiveness=0.85
        ))
        
        # High elongation optimization
        solutions.append(ResearchSolution(
            name="High Elongation Optimization",
            description="Higher elongation (κ > 1.5) improves confinement and stability",
            source="Various tokamaks, 2023-2024",
            year=2024,
            parameters={
                'elongation_target': 2.0,  # Target high elongation
                'confinement_bonus': 1.1,  # 10% bonus
            },
            effectiveness=0.8
        ))
        
        return solutions
    
    def get_solutions_for_issue(self, issue: str) -> List[ResearchSolution]:
        """Get solutions for a specific issue.
        
        Args:
            issue: Issue name (e.g., 'safety_factor', 'lawson', 'material_damage')
            
        Returns:
            List of relevant solutions
        """
        issue_keywords = {
            'safety_factor': ['HTS', 'Spherical', 'geometry', 'magnetic'],
            'lawson': ['fueling', 'heating', 'control'],
            'material_damage': ['tungsten', 'composite', 'first wall'],
            'tritium': ['breeding', 'lithium'],
            'power': ['HTS', 'current drive', 'heating', 'efficiency'],
        }
        
        keywords = issue_keywords.get(issue.lower(), [])
        
        relevant = []
        for solution in self.solutions:
            if any(kw.lower() in solution.name.lower() or 
                   kw.lower() in solution.description.lower() 
                   for kw in keywords):
                relevant.append(solution)
        
        return relevant
    
    def apply_solution(self, solution: ResearchSolution, config) -> Dict:
        """Apply a solution to a configuration.
        
        Args:
            solution: Solution to apply
            config: ReactorConfiguration to modify
            
        Returns:
            Dictionary of parameter changes
        """
        changes = {}
        params = solution.parameters
        
        # Apply parameter changes
        if 'toroidal_field' in params:
            if isinstance(params['toroidal_field'], tuple):
                # Use range
                changes['toroidal_field'] = params['toroidal_field'][0]
            else:
                changes['toroidal_field'] = params['toroidal_field']
        
        if 'major_radius' in params and isinstance(params['major_radius'], tuple):
            changes['major_radius'] = params['major_radius'][0]
        
        if 'minor_radius' in params and isinstance(params['minor_radius'], tuple):
            changes['minor_radius'] = params['minor_radius'][0]
        
        if 'aspect_ratio_target' in params:
            # Calculate to achieve target aspect ratio
            target_ar = params['aspect_ratio_target']
            if 'major_radius' not in changes:
                changes['major_radius'] = config.minor_radius * target_ar
        
        # Apply multipliers
        if 'input_power_multiplier' in params:
            changes['input_power'] = config.input_power * params['input_power_multiplier']
        
        if 'auxiliary_heating_multiplier' in params:
            changes['auxiliary_heating'] = config.auxiliary_heating * params['auxiliary_heating_multiplier']
        
        if 'current_drive_power_multiplier' in params:
            changes['current_drive_power'] = config.current_drive_power * params['current_drive_power_multiplier']
        
        return changes

