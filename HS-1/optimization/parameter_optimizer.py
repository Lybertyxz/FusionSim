"""Parameter optimization for fusion reactors.

Implements various optimization algorithms with realistic bounds.
Based on current fusion research and ITER parameters.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from simulator import FusionReactorSimulator, ReactorConfiguration


@dataclass
class ParameterBounds:
    """Realistic bounds for reactor parameters."""
    # Geometry (based on ITER and recent designs)
    major_radius: Tuple[float, float] = (3.0, 10.0)  # m (ITER: 6.2, SPARC: ~1.85)
    minor_radius: Tuple[float, float] = (0.5, 3.0)  # m (ITER: 2.0)
    elongation: Tuple[float, float] = (1.0, 2.5)  # (ITER: 1.7, some designs up to 2.5)
    triangularity: Tuple[float, float] = (0.0, 0.6)  # (ITER: 0.33)
    
    # Magnetic field (based on HTS technology - 2024 research)
    toroidal_field: Tuple[float, float] = (2.0, 20.0)  # T (ITER: 5.3, SPARC: 12.2, HTS can go higher)
    plasma_current: Tuple[float, float] = (5e6, 20e6)  # A (ITER: 15 MA)
    
    # Plasma conditions
    initial_temperature: Tuple[float, float] = (50e6, 300e6)  # K (optimal: 100-200 MK)
    initial_density: Tuple[float, float] = (0.5e20, 3e20)  # m⁻³ (ITER: 1e20)
    
    # Power
    input_power: Tuple[float, float] = (10e6, 100e6)  # W (ITER: 50 MW)
    auxiliary_heating: Tuple[float, float] = (0, 50e6)  # W (ITER: 33 MW)
    current_drive_power: Tuple[float, float] = (0, 20e6)  # W
    
    # Fuel inventory
    initial_tritium_inventory: Tuple[float, float] = (1e23, 1e26)  # atoms
    initial_deuterium_inventory: Tuple[float, float] = (1e24, 1e27)  # atoms


@dataclass
class OptimizationResult:
    """Result of optimization."""
    best_config: ReactorConfiguration
    best_state: Optional[object] = None
    best_score: float = 0.0
    optimization_history: List[Dict] = None
    iterations: int = 0
    success: bool = False
    message: str = ""


class ParameterOptimizer:
    """Optimize reactor parameters with realistic bounds."""
    
    def __init__(self, bounds: Optional[ParameterBounds] = None):
        """Initialize optimizer.
        
        Args:
            bounds: Parameter bounds (uses defaults if None)
        """
        self.bounds = bounds or ParameterBounds()
    
    def random_config(self) -> ReactorConfiguration:
        """Generate random configuration within bounds."""
        return ReactorConfiguration(
            major_radius=np.random.uniform(*self.bounds.major_radius),
            minor_radius=np.random.uniform(*self.bounds.minor_radius),
            elongation=np.random.uniform(*self.bounds.elongation),
            triangularity=np.random.uniform(*self.bounds.triangularity),
            toroidal_field=np.random.uniform(*self.bounds.toroidal_field),
            plasma_current=np.random.uniform(*self.bounds.plasma_current),
            initial_temperature=np.random.uniform(*self.bounds.initial_temperature),
            initial_density=np.random.uniform(*self.bounds.initial_density),
            input_power=np.random.uniform(*self.bounds.input_power),
            auxiliary_heating=np.random.uniform(*self.bounds.auxiliary_heating),
            current_drive_power=np.random.uniform(*self.bounds.current_drive_power),
            initial_tritium_inventory=np.random.uniform(*self.bounds.initial_tritium_inventory),
            initial_deuterium_inventory=np.random.uniform(*self.bounds.initial_deuterium_inventory),
        )
    
    def score_configuration(self, sim: FusionReactorSimulator, 
                          max_time: float = 1260.0) -> float:
        """Score a configuration.
        
        Scoring function:
        - High weight on operation time (beat 21 min = 1260 s)
        - Q factor > 1 (breakeven)
        - Safety factor q >= 2.0
        - Lawson criterion met
        - Net power positive
        
        Args:
            sim: Simulator with configuration
            max_time: Maximum simulation time in seconds
            
        Returns:
            Score (higher is better)
        """
        try:
            # Run simulation
            state = sim.run(max_time=max_time, dt=1.0)
            stats = sim.get_operation_statistics()
            
            # Base score from operation time
            operation_time = stats['max_operation_time']
            score = operation_time / 60.0  # Convert to minutes
            
            # Bonus for beating 21 minutes
            if operation_time >= 1260.0:
                score += 100.0  # Large bonus
            
            # Bonus for high Q factor
            if state and state.power_balance:
                q = state.power_balance.q_factor
                if not np.isinf(q) and q > 0:
                    score += min(q * 10.0, 50.0)  # Bonus up to 50
                    
                    # Extra bonus for Q > 10 (ignition)
                    if q > 10.0:
                        score += 50.0
            
            # Bonus for safety factor
            if state and state.magnetic_state:
                q_safety = state.magnetic_state.safety_factor
                if q_safety >= 2.0:
                    score += 20.0
                elif q_safety >= 1.5:
                    score += 10.0
            
            # Bonus for Lawson criterion
            if state and state.plasma_state:
                if state.plasma_state.meets_lawson_criterion:
                    score += 30.0
            
            # Bonus for net power positive
            if state and state.power_balance:
                if state.power_balance.output_power > 0:
                    score += 40.0
            
            # Penalty for failure
            if stats['failed']:
                score -= 50.0
            
            # Penalty for very low operation time
            if operation_time < 60.0:  # Less than 1 minute
                score -= 100.0
            
            return max(score, -200.0)  # Floor at -200
            
        except Exception as e:
            return -1000.0  # Large penalty for errors
    
    def grid_search(self, n_samples: int = 100, max_time: float = 1260.0,
                   objective: Optional[Callable] = None) -> OptimizationResult:
        """Grid search optimization.
        
        Args:
            n_samples: Number of random samples
            max_time: Maximum simulation time
            objective: Custom objective function (uses default if None)
            
        Returns:
            OptimizationResult
        """
        if objective is None:
            objective = self.score_configuration
        
        best_score = -np.inf
        best_config = None
        best_state = None
        history = []
        
        for i in range(n_samples):
            config = self.random_config()
            sim = FusionReactorSimulator(config)
            
            score = objective(sim, max_time)
            
            history.append({
                'iteration': i,
                'score': score,
                'config': config
            })
            
            if score > best_score:
                best_score = score
                best_config = config
                best_state = sim.current_state
            
            if i % 10 == 0:
                print(f"Grid search: {i}/{n_samples}, best score: {best_score:.2f}")
        
        return OptimizationResult(
            best_config=best_config or self.random_config(),
            best_state=best_state,
            best_score=best_score,
            optimization_history=history,
            iterations=n_samples,
            success=best_score > 0
        )
    
    def spsa_optimize(self, initial_config: Optional[ReactorConfiguration] = None,
                     max_iterations: int = 50, max_time: float = 1260.0,
                     a: float = 1.0, c: float = 0.1, alpha: float = 0.602,
                     gamma: float = 0.101) -> OptimizationResult:
        """SPSA (Simultaneous Perturbation Stochastic Approximation) optimization.
        
        Based on research: efficient for high-dimensional problems.
        
        Args:
            initial_config: Starting configuration
            max_iterations: Maximum iterations
            max_time: Maximum simulation time
            a, c, alpha, gamma: SPSA algorithm parameters
            
        Returns:
            OptimizationResult
        """
        # Start with random or provided config
        if initial_config is None:
            current_config = self.random_config()
        else:
            current_config = initial_config
        
        best_score = -np.inf
        best_config = current_config
        best_state = None
        history = []
        
        for k in range(max_iterations):
            # SPSA step size
            ak = a / (k + 1) ** alpha
            ck = c / (k + 1) ** gamma
            
            # Generate random perturbation
            perturbation = self._generate_perturbation(ck)
            
            # Create negative perturbation
            perturbation_minus = {k: -v for k, v in perturbation.items()}
            
            # Evaluate + and - perturbations
            config_plus = self._apply_perturbation(current_config, perturbation)
            config_minus = self._apply_perturbation(current_config, perturbation_minus)
            
            sim_plus = FusionReactorSimulator(config_plus)
            sim_minus = FusionReactorSimulator(config_minus)
            
            score_plus = self.score_configuration(sim_plus, max_time)
            score_minus = self.score_configuration(sim_minus, max_time)
            
            # SPSA gradient approximation
            # g_k ≈ (f(x + ck*Δ) - f(x - ck*Δ)) / (2*ck*Δ)
            # For each parameter, estimate gradient
            gradient_estimate = {}
            for key in perturbation:
                delta_k = perturbation[key]
                if abs(delta_k) > 1e-10:  # Avoid division by zero
                    gradient_estimate[key] = (score_plus - score_minus) / (2.0 * ck * delta_k)
                else:
                    gradient_estimate[key] = 0.0
            
            # Update configuration: x_{k+1} = x_k - a_k * g_k
            # Scale gradient by step size and apply
            update = {k: -ak * v for k, v in gradient_estimate.items()}
            current_config = self._update_config(current_config, update)
            
            current_score = max(score_plus, score_minus)
            
            if current_score > best_score:
                best_score = current_score
                best_config = current_config
                best_state = sim_plus.current_state if score_plus > score_minus else sim_minus.current_state
            
            history.append({
                'iteration': k,
                'score': current_score,
                'best_score': best_score,
                'config': current_config
            })
            
            if k % 5 == 0:
                print(f"SPSA: {k}/{max_iterations}, current: {current_score:.2f}, best: {best_score:.2f}")
        
        return OptimizationResult(
            best_config=best_config,
            best_state=best_state,
            best_score=best_score,
            optimization_history=history,
            iterations=max_iterations,
            success=best_score > 0
        )
    
    def _generate_perturbation(self, ck: float) -> Dict[str, float]:
        """Generate random perturbation vector."""
        return {
            'major_radius': np.random.choice([-1, 1]) * ck * 0.5,
            'minor_radius': np.random.choice([-1, 1]) * ck * 0.2,
            'elongation': np.random.choice([-1, 1]) * ck * 0.1,
            'toroidal_field': np.random.choice([-1, 1]) * ck * 1.0,
            'plasma_current': np.random.choice([-1, 1]) * ck * 1e6,
            'initial_temperature': np.random.choice([-1, 1]) * ck * 10e6,
            'initial_density': np.random.choice([-1, 1]) * ck * 0.1e20,
        }
    
    def _apply_perturbation(self, config: ReactorConfiguration, 
                          perturbation: Dict[str, float]) -> ReactorConfiguration:
        """Apply perturbation to configuration."""
        return ReactorConfiguration(
            major_radius=max(self.bounds.major_radius[0], 
                           min(self.bounds.major_radius[1], 
                               config.major_radius + perturbation.get('major_radius', 0))),
            minor_radius=max(self.bounds.minor_radius[0],
                           min(self.bounds.minor_radius[1],
                               config.minor_radius + perturbation.get('minor_radius', 0))),
            elongation=max(self.bounds.elongation[0],
                         min(self.bounds.elongation[1],
                             config.elongation + perturbation.get('elongation', 0))),
            triangularity=config.triangularity,
            toroidal_field=max(self.bounds.toroidal_field[0],
                            min(self.bounds.toroidal_field[1],
                                config.toroidal_field + perturbation.get('toroidal_field', 0))),
            plasma_current=max(self.bounds.plasma_current[0],
                            min(self.bounds.plasma_current[1],
                                config.plasma_current + perturbation.get('plasma_current', 0))),
            initial_temperature=max(self.bounds.initial_temperature[0],
                                  min(self.bounds.initial_temperature[1],
                                      config.initial_temperature + perturbation.get('initial_temperature', 0))),
            initial_density=max(self.bounds.initial_density[0],
                              min(self.bounds.initial_density[1],
                                  config.initial_density + perturbation.get('initial_density', 0))),
            input_power=config.input_power,
            auxiliary_heating=config.auxiliary_heating,
            current_drive_power=config.current_drive_power,
            initial_tritium_inventory=config.initial_tritium_inventory,
            initial_deuterium_inventory=config.initial_deuterium_inventory,
        )
    
    def _update_config(self, config: ReactorConfiguration, 
                      update: Dict[str, float]) -> ReactorConfiguration:
        """Update configuration with gradient step."""
        # Similar to _apply_perturbation but with update dict
        return self._apply_perturbation(config, update)

