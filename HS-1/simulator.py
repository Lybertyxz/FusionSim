"""Main fusion reactor simulator.

Integrates all physics modules and provides a unified interface.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import time
import matplotlib.pyplot as plt

from physics.plasma import PlasmaPhysics, PlasmaState
from physics.magnetic import MagneticConfinement, TokamakGeometry, MagneticState
from physics.power import PowerCalculator, PowerBalance
from physics.neutronics import NeutronicsCalculator, NeutronicsState
from materials.materials import MaterialDatabase, Material
from visualization.plotter import ReactorPlotter


@dataclass
class ReactorConfiguration:
    """Reactor configuration parameters."""
    # Geometry
    major_radius: float = 6.2  # m (ITER-like)
    minor_radius: float = 2.0  # m
    elongation: float = 1.7
    triangularity: float = 0.33
    
    # Magnetic field
    toroidal_field: float = 5.3  # T (ITER-like)
    plasma_current: float = 15e6  # A (15 MA)
    
    # Plasma initial conditions
    initial_temperature: float = 150e6  # K (150 MK ≈ 13 keV, optimal for D-T fusion)
    initial_density: float = 1e20  # m⁻³
    
    # Materials
    first_wall_material: str = 'tungsten'
    blanket_material: str = 'lithium_lead'
    blanket_thickness: float = 1.0  # m
    
    # Operation
    input_power: float = 50e6  # W (50 MW)
    auxiliary_heating: float = 33e6  # W
    current_drive_power: float = 0.0  # W
    
    # Fuel inventory (for time-dependent simulation)
    initial_tritium_inventory: float = 1e25  # atoms (initial tritium supply)
    initial_deuterium_inventory: float = 1e26  # atoms (initial deuterium supply)
    min_tritium_inventory: float = 1e23  # atoms (minimum required for operation)


@dataclass
class ReactorState:
    """Complete reactor state."""
    # Plasma
    plasma_state: PlasmaState
    
    # Magnetic
    magnetic_state: MagneticState
    geometry: TokamakGeometry
    
    # Power
    power_balance: PowerBalance
    
    # Neutronics
    neutronics_state: NeutronicsState
    
    # Status
    operational: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Material status
    first_wall_temp: float = 0.0
    blanket_temp: float = 0.0
    material_damage: float = 0.0
    
    # Time tracking
    simulation_time: float = 0.0  # seconds
    operation_time: float = 0.0  # seconds (total operation time)
    
    # Fuel inventory (evolves over time)
    tritium_inventory: float = 0.0  # atoms
    deuterium_inventory: float = 0.0  # atoms
    
    # Failure tracking
    failed: bool = False
    failure_cause: str = ""
    failure_time: float = 0.0  # seconds


class FusionReactorSimulator:
    """Main fusion reactor simulator."""
    
    def __init__(self, config: Optional[ReactorConfiguration] = None):
        """Initialize simulator.
        
        Args:
            config: Reactor configuration (uses defaults if None)
        """
        self.config = config or ReactorConfiguration()
        
        # Initialize modules
        self.plasma_physics = PlasmaPhysics()
        self.magnetic = MagneticConfinement()
        self.power_calc = PowerCalculator()
        self.neutronics = NeutronicsCalculator()
        self.materials = MaterialDatabase()
        self.plotter = ReactorPlotter()
        
        # State history
        self.history: List[ReactorState] = []
        
        # Current state
        self.current_state: Optional[ReactorState] = None
        
        # Time-dependent state (evolves over time)
        self.current_temperature: float = self.config.initial_temperature
        self.current_density: float = self.config.initial_density
        self.tritium_inventory: float = self.config.initial_tritium_inventory
        self.deuterium_inventory: float = self.config.initial_deuterium_inventory
        self.accumulated_damage: float = 0.0  # DPA
        self.simulation_time: float = 0.0  # seconds
    
    def calculate_state(self) -> ReactorState:
        """Calculate complete reactor state.
        
        Returns:
            ReactorState object
        """
        # Get geometry
        geometry = self.magnetic.calculate_tokamak_geometry(
            self.config.major_radius,
            self.config.minor_radius,
            self.config.elongation,
            self.config.triangularity
        )
        
        # Calculate plasma state
        # Use current evolving state (temperature, density)
        # First, estimate confinement time
        # Use config.input_power as primary input (more realistic than calculating ohmic heating)
        # Ohmic heating is included in input_power, or we can estimate it separately for confinement scaling
        plasma_resistance = self.power_calc.calculate_plasma_resistance(
            self.config.major_radius,
            self.config.minor_radius,
            self.current_temperature,
            self.current_density
        )
        ohmic_heating = self.power_calc.calculate_ohmic_heating(
            self.config.plasma_current,
            plasma_resistance
        )
        # For confinement time scaling, use improved method that separates ohmic heating
        # Research shows ohmic heating should be treated separately (less effective for confinement)
        external_heating_MW = (self.config.auxiliary_heating + self.config.current_drive_power) / 1e6
        ohmic_heating_MW = ohmic_heating / 1e6
        
        confinement_time = self.magnetic.calculate_confinement_time_scaling(
            self.config.major_radius,
            self.config.minor_radius,
            self.current_density,
            self.current_temperature,
            self.config.toroidal_field,
            self.config.plasma_current,
            self.config.elongation,
            heating_power_MW=external_heating_MW,
            ohmic_heating_MW=ohmic_heating_MW,
            use_improved_scaling=True
        )
        
        plasma_state = self.plasma_physics.calculate_plasma_state(
            self.current_density,
            self.current_temperature,
            confinement_time,
            self.config.toroidal_field
        )
        
        # Calculate magnetic state
        magnetic_state = self.magnetic.calculate_magnetic_state(
            self.config.toroidal_field,
            self.config.plasma_current,
            self.config.major_radius,
            self.config.minor_radius,
            self.current_density,
            self.current_temperature
        )
        
        # Calculate input power for Q factor
        # Use config.input_power as the external input power (more realistic)
        # This represents the power you have to supply from outside the reactor
        # Ohmic heating is a byproduct, not external input for Q calculation
        if self.config.input_power > 0:
            # Use configured input power (external power input)
            total_input = self.config.input_power
        else:
            # Fallback: calculate from components (but ohmic heating is usually not "input" for Q)
            total_input = self.config.auxiliary_heating + self.config.current_drive_power
            # Note: Ohmic heating is not counted as external input for Q factor
        
        # Calculate fusion power (total)
        fusion_power_total = plasma_state.fusion_power_density * geometry.plasma_volume
        
        # Calculate power balance
        bremsstrahlung_total = plasma_state.bremsstrahlung_loss * geometry.plasma_volume
        synchrotron_total = plasma_state.synchrotron_loss * geometry.plasma_volume
        
        power_balance = self.power_calc.calculate_power_balance(
            fusion_power_total,
            total_input,
            bremsstrahlung_total,
            synchrotron_total
        )
        
        # Calculate neutronics
        surface_area = self.magnetic.calculate_plasma_surface_area(
            self.config.major_radius,
            self.config.minor_radius,
            self.config.elongation
        )
        
        # Get blanket material for tritium breeding
        blanket_mat = self.materials.get_material(self.config.blanket_material)
        if blanket_mat and blanket_mat.tritium_breeding_ratio > 0:
            # Estimate lithium density from material
            li_atomic_mass = 6.941 * 1.66053906660e-27
            li_density = blanket_mat.density / li_atomic_mass
        else:
            li_density = None
        
        neutronics_state = self.neutronics.calculate_neutronics_state(
            fusion_power_total,
            surface_area,
            li_density,
            self.config.blanket_thickness,
            initial_dpa=self.accumulated_damage
        )
        # Material damage is accumulated in evolve_state(), so use current value
        neutronics_state.material_damage_accumulated = self.accumulated_damage
        
        # Check for errors and warnings
        errors = []
        warnings = []
        
        # Material temperature checks
        first_wall_mat = self.materials.get_material(self.config.first_wall_material)
        if first_wall_mat:
            # Estimate first wall temperature (simplified)
            # Heat flux from neutron wall loading
            heat_flux = neutronics_state.neutron_wall_loading * 1e6  # W/m²
            # Rough estimate: T ≈ T_coolant + (heat_flux * thickness / k)
            first_wall_temp = 300.0 + (heat_flux * 0.01 / first_wall_mat.thermal_conductivity)
            
            if first_wall_temp > first_wall_mat.max_operating_temp:
                errors.append(
                    f"First wall temperature ({first_wall_temp:.0f} K) exceeds "
                    f"material limit ({first_wall_mat.max_operating_temp:.0f} K)"
                )
            elif first_wall_temp > first_wall_mat.max_operating_temp * 0.8:
                warnings.append(
                    f"First wall temperature ({first_wall_temp:.0f} K) approaching limit"
                )
        else:
            first_wall_temp = 0.0
        
        # Safety factor check
        # At startup, allow lower safety factor (plasma might stabilize)
        # Only fail if it's critically low and reactor has been running
        startup_tolerance = 30.0  # seconds - allow lower q during startup
        if magnetic_state.safety_factor < 1.5:
            # Critically low - always an error
            errors.append(
                f"Safety factor (q={magnetic_state.safety_factor:.2f}) critically low (minimum: 1.5)"
            )
        elif magnetic_state.safety_factor < 2.0:
            # Low but might be acceptable during startup
            if self.simulation_time > startup_tolerance:
                errors.append(
                    f"Safety factor (q={magnetic_state.safety_factor:.2f}) too low (minimum: 2.0)"
                )
            else:
                warnings.append(
                    f"Safety factor (q={magnetic_state.safety_factor:.2f}) is low (may stabilize during startup)"
                )
        elif magnetic_state.safety_factor < 3.0:
            warnings.append(
                f"Safety factor (q={magnetic_state.safety_factor:.2f}) is low"
            )
        
        # Beta check
        if magnetic_state.beta > 0.1:
            warnings.append(
                f"Beta ({magnetic_state.beta:.3f}) is high, may affect stability"
            )
        
        # Lawson criterion
        # During startup, plasma might not meet Lawson criterion immediately
        # Only fail if it's been running for a while and still doesn't meet it
        lawson_startup_time = 60.0  # seconds - allow time to reach Lawson criterion
        if not plasma_state.meets_lawson_criterion:
            if self.simulation_time > lawson_startup_time:
                errors.append("Plasma does not meet Lawson criterion for ignition")
            else:
                warnings.append(
                    f"Plasma does not yet meet Lawson criterion (startup phase, t={self.simulation_time:.1f}s)"
                )
        
        # Tritium breeding
        if neutronics_state.tritium_breeding_ratio < 1.0:
            errors.append(
                f"Tritium breeding ratio ({neutronics_state.tritium_breeding_ratio:.2f}) < 1.0 "
                "(cannot sustain operation)"
            )
        
        # Material damage checks
        material_damage = neutronics_state.material_damage_accumulated
        first_wall_mat = self.materials.get_material(self.config.first_wall_material)
        max_damage = 100.0  # Typical limit for first wall materials
        if first_wall_mat and hasattr(first_wall_mat, 'max_dpa'):
            max_damage = first_wall_mat.max_dpa
        
        if material_damage > max_damage:
            errors.append(
                f"Material damage ({material_damage:.1f} DPA) exceeds limit ({max_damage:.1f} DPA)"
            )
        elif material_damage > max_damage * 0.8:
            warnings.append(
                f"High material damage: {material_damage:.1f} DPA (limit: {max_damage:.1f} DPA)"
            )
        
        # Fuel inventory checks
        if self.tritium_inventory < self.config.min_tritium_inventory:
            errors.append(
                f"Tritium inventory ({self.tritium_inventory/1e23:.2f} × 10²³ atoms) "
                f"below minimum ({self.config.min_tritium_inventory/1e23:.2f} × 10²³ atoms)"
            )
        
        # Check if enough fuel for fusion (need both D and T)
        min_fuel_atoms = 1e22  # Minimum atoms needed for operation
        if self.deuterium_inventory < min_fuel_atoms:
            errors.append(
                f"Deuterium inventory ({self.deuterium_inventory/1e23:.2f} × 10²³ atoms) too low"
            )
        
        # Failure detection
        # Only fail on critical errors (not startup-related warnings)
        failed = False
        failure_cause = ""
        
        # Filter out startup-related errors (they're warnings during startup)
        critical_errors = []
        for error in errors:
            # These are critical and should cause failure
            if any(keyword in error.lower() for keyword in 
                   ['temperature', 'damage', 'tritium', 'deuterium', 'critically']):
                critical_errors.append(error)
            # Safety factor and Lawson errors are only critical after startup period
            elif "safety" in error.lower() and self.simulation_time > 30.0:
                critical_errors.append(error)
            elif "lawson" in error.lower() and self.simulation_time > 60.0:
                critical_errors.append(error)
        
        # Check failure conditions (only from critical errors)
        if len(critical_errors) > 0:
            # Determine primary failure cause
            if any("temperature" in e.lower() for e in critical_errors):
                failed = True
                failure_cause = "Material temperature limit exceeded"
            elif any("damage" in e.lower() for e in critical_errors):
                failed = True
                failure_cause = "Material damage limit exceeded"
            elif any("tritium" in e.lower() for e in critical_errors):
                failed = True
                failure_cause = "Tritium inventory depleted"
            elif any("deuterium" in e.lower() for e in critical_errors):
                failed = True
                failure_cause = "Deuterium inventory depleted"
            elif any("lawson" in e.lower() for e in critical_errors):
                failed = True
                failure_cause = "Lawson criterion not met after startup period"
            elif any("safety" in e.lower() for e in critical_errors):
                failed = True
                failure_cause = "Safety factor too low (plasma instability)"
            else:
                failed = True
                failure_cause = critical_errors[0]  # Use first critical error as cause
        
        # Operational status
        # Allow operation during startup even if some criteria aren't perfect yet
        # But still need basic safety (no critical errors)
        critical_errors = [e for e in errors if any(keyword in e.lower() for keyword in 
                          ['temperature', 'damage', 'tritium', 'deuterium', 'critically'])]
        
        operational = (not failed and len(critical_errors) == 0)
        
        # Note: breakeven and Lawson criterion are goals, not requirements for basic operation
        # A reactor can operate below breakeven (Q < 1) - it just consumes more energy than it produces
        
        return ReactorState(
            plasma_state=plasma_state,
            magnetic_state=magnetic_state,
            geometry=geometry,
            power_balance=power_balance,
            neutronics_state=neutronics_state,
            operational=operational,
            errors=errors,
            warnings=warnings,
            first_wall_temp=first_wall_temp,
            blanket_temp=300.0,  # Simplified
            material_damage=material_damage,
            simulation_time=self.simulation_time,
            operation_time=self.simulation_time if operational else 0.0,
            tritium_inventory=self.tritium_inventory,
            deuterium_inventory=self.deuterium_inventory,
            failed=failed,
            failure_cause=failure_cause,
            failure_time=self.simulation_time if failed else 0.0
        )
    
    def evolve_state(self, dt: float, state: ReactorState) -> None:
        """Evolve reactor state over time step dt.
        
        Args:
            dt: Time step in seconds
            state: Current reactor state
        """
        # Only evolve if reactor is still operational
        if state.failed or not state.operational:
            return
        
        # Update simulation time
        self.simulation_time += dt
        
        # Plasma temperature evolution (simplified)
        # dT/dt = (heating - losses) / heat_capacity
        # Heat capacity ~ n * V * k_B (simplified)
        geometry = state.geometry
        heat_capacity = self.current_density * geometry.plasma_volume * 1.380649e-23  # J/K
        
        if heat_capacity > 0:
            # Net heating power
            net_heating = (state.power_balance.fusion_power + 
                          state.power_balance.input_power - 
                          state.plasma_state.total_loss * geometry.plasma_volume)
            
            # Temperature change
            dT = (net_heating / heat_capacity) * dt
            self.current_temperature += dT
            
            # Keep temperature in reasonable bounds
            self.current_temperature = max(1e6, min(500e6, self.current_temperature))
        
        # Density evolution (simplified - assume constant for now, could add fueling)
        # In reality: dn/dt = fueling_rate - consumption_rate
        # For now, keep density approximately constant (assume continuous fueling)
        # Could add fueling model later
        
        # Fuel consumption
        # Each D-T fusion consumes 1 D and 1 T atom
        fusion_reaction_rate = state.plasma_state.fusion_power_density * geometry.plasma_volume
        energy_per_fusion = 17.6e6 * 1.602176634e-19  # J
        if energy_per_fusion > 0:
            consumption_rate = fusion_reaction_rate / energy_per_fusion  # atoms/s
            consumed_dt = consumption_rate * dt
            
            self.deuterium_inventory -= consumed_dt
            self.tritium_inventory -= consumed_dt
            
            # Prevent negative inventories
            self.deuterium_inventory = max(0.0, self.deuterium_inventory)
            self.tritium_inventory = max(0.0, self.tritium_inventory)
        
        # Tritium production from breeding
        if state.neutronics_state.tritium_production_rate > 0:
            produced_dt = state.neutronics_state.tritium_production_rate * dt
            self.tritium_inventory += produced_dt
        
        # Material damage accumulation
        # dpa_rate is in DPA/year, convert to DPA/second
        seconds_per_year = 365.25 * 24 * 3600
        dpa_per_second = state.neutronics_state.dpa_rate / seconds_per_year
        self.accumulated_damage += dpa_per_second * dt
    
    def run(self, max_time: float = 3600.0, dt: float = 1.0, 
            save_interval: float = 10.0) -> ReactorState:
        """Run time-dependent simulation.
        
        Args:
            max_time: Maximum simulation time in seconds (default: 1 hour)
            dt: Time step in seconds (default: 1.0 s)
            save_interval: Interval for saving state history in seconds (default: 10.0 s)
            
        Returns:
            Final reactor state
        """
        # Reset state
        self.history = []
        self.simulation_time = 0.0
        self.current_temperature = self.config.initial_temperature
        self.current_density = self.config.initial_density
        self.tritium_inventory = self.config.initial_tritium_inventory
        self.deuterium_inventory = self.config.initial_deuterium_inventory
        self.accumulated_damage = 0.0
        
        last_save_time = -save_interval  # Force save at t=0
        
        # Initial state
        state = self.calculate_state()
        self.history.append(state)
        self.current_state = state
        
        # Time stepping loop
        while self.simulation_time < max_time:
            # Evolve state (only if still operational)
            if not state.failed and state.operational:
                self.evolve_state(dt, state)
            
            # Calculate new state
            state = self.calculate_state()
            self.current_state = state
            
            # Save state at intervals
            if self.simulation_time - last_save_time >= save_interval:
                self.history.append(state)
                last_save_time = self.simulation_time
            
            # Check if reactor has failed
            if state.failed:
                print(f"\nReactor failed at t = {self.simulation_time:.1f} s ({self.simulation_time/60:.2f} min)")
                print(f"Failure cause: {state.failure_cause}")
                break
            
            # Check if still operational
            if not state.operational and not state.failed:
                # Check what went wrong
                if state.errors:
                    print(f"\nReactor became non-operational at t = {self.simulation_time:.1f} s ({self.simulation_time/60:.2f} min)")
                    print(f"Reason: {state.errors[0]}")
        
        return self.current_state
    
    def get_operation_statistics(self) -> Dict:
        """Get operation statistics from simulation history.
        
        Returns:
            Dictionary with operation statistics
        """
        if not self.history:
            return {}
        
        # Find when reactor failed or stopped
        final_state = self.current_state
        max_operation_time = self.simulation_time
        
        # Calculate average Q factor during operation
        operational_states = [s for s in self.history if s.operational]
        if operational_states:
            avg_q = sum(s.power_balance.q_factor for s in operational_states if not np.isinf(s.power_balance.q_factor)) / len(operational_states)
            max_q = max((s.power_balance.q_factor for s in operational_states if not np.isinf(s.power_balance.q_factor)), default=0.0)
        else:
            avg_q = 0.0
            max_q = 0.0
        
        # Calculate total energy produced
        total_energy = 0.0
        if len(self.history) > 1:
            for i in range(len(self.history) - 1):
                if self.history[i].operational:
                    dt = self.history[i+1].simulation_time - self.history[i].simulation_time
                    power = self.history[i].power_balance.fusion_power
                    total_energy += power * dt
        
        # Predict maximum runtime based on limiting factors
        max_runtime_prediction = float('inf')
        limiting_factor = "None (can run indefinitely)"
        
        if final_state:
            # Check material damage limit
            if final_state.neutronics_state.dpa_rate > 0:
                max_damage = 100.0  # Default limit
                first_wall_mat = self.materials.get_material(self.config.first_wall_material)
                if first_wall_mat and hasattr(first_wall_mat, 'max_dpa'):
                    max_damage = first_wall_mat.max_dpa
                
                remaining_damage = max_damage - final_state.material_damage
                if remaining_damage > 0 and final_state.neutronics_state.dpa_rate > 0:
                    years_remaining = remaining_damage / final_state.neutronics_state.dpa_rate
                    seconds_remaining = years_remaining * 365.25 * 24 * 3600
                    if seconds_remaining < max_runtime_prediction:
                        max_runtime_prediction = seconds_remaining
                        limiting_factor = f"Material damage (will reach {max_damage:.1f} DPA)"
            
            # Check tritium inventory
            if final_state.neutronics_state.tritium_breeding_ratio < 1.0:
                consumption_rate = final_state.neutronics_state.tritium_production_rate - (
                    final_state.neutronics_state.tritium_production_rate / final_state.neutronics_state.tritium_breeding_ratio
                )
                if consumption_rate > 0 and final_state.tritium_inventory > 0:
                    seconds_remaining = final_state.tritium_inventory / consumption_rate
                    if seconds_remaining < max_runtime_prediction:
                        max_runtime_prediction = seconds_remaining
                        limiting_factor = "Tritium inventory depletion"
        
        return {
            'max_operation_time': max_operation_time,
            'max_operation_time_minutes': max_operation_time / 60.0,
            'failed': final_state.failed if final_state else False,
            'failure_cause': final_state.failure_cause if final_state and final_state.failed else None,
            'average_q_factor': avg_q,
            'max_q_factor': max_q,
            'total_energy_produced': total_energy,
            'total_energy_produced_MWh': total_energy / (3.6e9),  # Convert J to MWh
            'max_runtime_prediction': max_runtime_prediction,
            'max_runtime_prediction_minutes': max_runtime_prediction / 60.0 if max_runtime_prediction != float('inf') else float('inf'),
            'limiting_factor': limiting_factor,
            'can_run_indefinitely': max_runtime_prediction == float('inf')
        }
    
    def optimize_parameters(self, target_q: float = 10.0, max_iterations: int = 100) -> Dict:
        """Attempt to optimize reactor parameters to achieve target Q.
        
        Args:
            target_q: Target Q factor
            max_iterations: Maximum optimization iterations
            
        Returns:
            Dictionary with optimization results
        """
        best_state = None
        best_q = 0.0
        best_config = None
        
        # Simple grid search over key parameters
        temp_range = np.linspace(10e6, 20e6, 10)
        density_range = np.linspace(0.5e20, 2e20, 10)
        
        for temp in temp_range:
            for density in density_range:
                self.config.initial_temperature = temp
                self.config.initial_density = density
                
                state = self.calculate_state()
                q = state.power_balance.q_factor
                
                if not np.isinf(q) and q > best_q:
                    best_q = q
                    best_state = state
                    best_config = self.config
        
        if best_config:
            self.config = best_config
            self.current_state = best_state
        
        return {
            'best_q': best_q,
            'best_temperature': best_config.initial_temperature if best_config else None,
            'best_density': best_config.initial_density if best_config else None,
            'target_achieved': best_q >= target_q
        }
    
    def get_status_dict(self) -> Dict:
        """Get status as dictionary for visualization.
        
        Returns:
            Dictionary of status information
        """
        if not self.current_state:
            return {}
        
        state = self.current_state
        
        return {
            'operational': state.operational,
            'errors': state.errors,
            'warnings': state.warnings,
            'temperature': state.plasma_state.temperature,
            'density': state.plasma_state.density,
            'q_factor': state.power_balance.q_factor,
            'fusion_power': state.power_balance.fusion_power,
            'input_power': state.power_balance.input_power,
            'output_power': state.power_balance.output_power,
            'thermal_power': state.power_balance.thermal_power,
            'tbr': state.neutronics_state.tritium_breeding_ratio,
            'triple_product': state.plasma_state.triple_product,
            'beta': state.magnetic_state.beta,
            'safety_factor': state.magnetic_state.safety_factor,
            'neutron_flux': state.neutronics_state.neutron_flux,
            'wall_loading': state.neutronics_state.neutron_wall_loading,
            'first_wall_temp': state.first_wall_temp,
            'material_damage': state.material_damage
        }
    
    def visualize(self, save_path: Optional[str] = None):
        """Create visualizations of reactor state.
        
        Args:
            save_path: Optional path to save figures (saved in plots/ folder)
        """
        if not self.current_state:
            print("No state to visualize. Run simulation first.")
            return
        
        # Status dashboard
        status_dict = self.get_status_dict()
        fig_dashboard = self.plotter.create_status_dashboard(status_dict)
        if save_path:
            self.plotter.save_figure(fig_dashboard, f"{save_path}_dashboard.png")
        else:
            plt.show()
        
        # Reactor diagram
        fig_diagram = self.plotter.create_reactor_diagram(
            self.config.major_radius,
            self.config.minor_radius,
            self.config.elongation
        )
        if save_path:
            self.plotter.save_figure(fig_diagram, f"{save_path}_diagram.png")
        else:
            plt.show()
        
        # Power balance
        power_dict = {
            'fusion_power': status_dict['fusion_power'],
            'input_power': status_dict['input_power'],
            'output_power': status_dict['output_power'],
            'q_factor': status_dict['q_factor']
        }
        fig_power = self.plotter.plot_power_balance(power_dict)
        if save_path:
            self.plotter.save_figure(fig_power, f"{save_path}_power.png")
        else:
            plt.show()
    
    def print_status(self):
        """Print detailed status to console."""
        if not self.current_state:
            print("No state available. Run simulation first.")
            return
        
        state = self.current_state
        
        print("\n" + "="*80)
        print("FUSION REACTOR SIMULATOR - STATUS REPORT")
        print("="*80)
        
        print("\n[PLASMA STATE]")
        print(f"  Temperature:        {state.plasma_state.temperature/1e6:.2f} MK")
        print(f"  Density:            {state.plasma_state.density/1e20:.2f} × 10²⁰ m⁻³")
        print(f"  Confinement Time:   {state.plasma_state.confinement_time:.3f} s")
        print(f"  Triple Product:     {state.plasma_state.triple_product/1e21:.2f} × 10²¹ m⁻³·s·K")
        print(f"  Lawson Criterion:   {'✓ MET' if state.plasma_state.meets_lawson_criterion else '✗ NOT MET'}")
        
        print("\n[MAGNETIC CONFINEMENT]")
        print(f"  Toroidal Field:     {state.magnetic_state.toroidal_field:.2f} T")
        print(f"  Plasma Current:     {self.config.plasma_current/1e6:.1f} MA")
        print(f"  Safety Factor (q):  {state.magnetic_state.safety_factor:.2f}")
        print(f"  Beta:               {state.magnetic_state.beta:.4f}")
        print(f"  Aspect Ratio:       {state.geometry.aspect_ratio:.2f}")
        
        print("\n[POWER BALANCE]")
        print(f"  Fusion Power:       {state.power_balance.fusion_power/1e6:.1f} MW")
        print(f"  Input Power:        {state.power_balance.input_power/1e6:.1f} MW")
        print(f"  Thermal Power:      {state.power_balance.thermal_power/1e6:.1f} MW")
        print(f"  Electrical Output:  {state.power_balance.output_power/1e6:.1f} MW")
        print(f"  Q Factor:           {state.power_balance.q_factor:.2f}" + 
              (" (∞)" if np.isinf(state.power_balance.q_factor) else ""))
        print(f"  Breakeven:          {'✓ YES' if state.power_balance.breakeven else '✗ NO'}")
        print(f"  Ignition:           {'✓ YES' if state.power_balance.ignition else '✗ NO'}")
        
        print("\n[NEUTRONICS]")
        print(f"  Neutron Flux:       {state.neutronics_state.neutron_flux/1e18:.2f} × 10¹⁸ n/(m²·s)")
        print(f"  Wall Loading:       {state.neutronics_state.neutron_wall_loading:.2f} MW/m²")
        print(f"  Tritium Production: {state.neutronics_state.tritium_production_rate/1e20:.2f} × 10²⁰ atoms/s")
        print(f"  Tritium Breeding:   {state.neutronics_state.tritium_breeding_ratio:.3f}")
        print(f"  Material Damage:    {state.neutronics_state.material_damage_accumulated:.2f} DPA")
        
        print("\n[MATERIALS]")
        print(f"  First Wall Temp:    {state.first_wall_temp:.0f} K")
        print(f"  Material Damage:    {state.material_damage:.2f} DPA")
        
        print("\n[TIME & OPERATION]")
        print(f"  Simulation Time:    {state.simulation_time:.1f} s ({state.simulation_time/60:.2f} min)")
        if state.operation_time > 0:
            print(f"  Operation Time:      {state.operation_time:.1f} s ({state.operation_time/60:.2f} min)")
        print(f"  Tritium Inventory:  {state.tritium_inventory/1e23:.2f} × 10²³ atoms")
        print(f"  Deuterium Inventory: {state.deuterium_inventory/1e23:.2f} × 10²³ atoms")
        
        print("\n[STATUS]")
        if state.operational:
            print("  ✓ OPERATIONAL")
        else:
            print("  ✗ NOT OPERATIONAL")
        
        if state.failed:
            print(f"  ✗ FAILED at t = {state.failure_time:.1f} s ({state.failure_time/60:.2f} min)")
            print(f"  Failure Cause: {state.failure_cause}")
        
        if state.errors:
            print("\n[ERRORS]")
            for error in state.errors:
                print(f"  ✗ {error}")
        
        if state.warnings:
            print("\n[WARNINGS]")
            for warning in state.warnings:
                print(f"  ⚠ {warning}")
        
        # Operation statistics if available
        if self.history and len(self.history) > 1:
            stats = self.get_operation_statistics()
            print("\n[OPERATION STATISTICS]")
            print(f"  Max Operation Time: {stats['max_operation_time_minutes']:.2f} min")
            if stats['failed']:
                print(f"  Status: FAILED - {stats['failure_cause']}")
            else:
                print(f"  Status: {'OPERATIONAL' if state.operational else 'STOPPED'}")
            print(f"  Average Q Factor:   {stats['average_q_factor']:.2f}")
            print(f"  Max Q Factor:       {stats['max_q_factor']:.2f}")
            print(f"  Total Energy:       {stats['total_energy_produced_MWh']:.2f} MWh")
            if stats['can_run_indefinitely']:
                print(f"  Max Runtime:        INDEFINITE")
            else:
                print(f"  Max Runtime:        {stats['max_runtime_prediction_minutes']:.2f} min")
            print(f"  Limiting Factor:    {stats['limiting_factor']}")
        
        print("\n" + "="*80 + "\n")

