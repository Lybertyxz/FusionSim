"""Plotting and visualization for fusion reactor simulator."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.figure import Figure
import numpy as np
from typing import Dict, Optional, Tuple
import io


class ReactorPlotter:
    """Plotting utilities for fusion reactor visualization."""
    
    def __init__(self):
        """Initialize plotter."""
        plt.style.use('dark_background')
        self.fig = None
        self.axes = None
    
    def create_reactor_diagram(self, major_radius: float, minor_radius: float,
                              elongation: float = 1.0) -> Figure:
        """Create a 2D diagram of the tokamak reactor.
        
        Args:
            major_radius: Major radius in m
            minor_radius: Minor radius in m
            elongation: Elongation factor
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Draw torus
        center = (major_radius, 0)
        
        # Create elliptical plasma cross-section
        ellipse = patches.Ellipse(
            center, 
            width=2 * minor_radius,
            height=2 * minor_radius * elongation,
            fill=False,
            edgecolor='cyan',
            linewidth=2,
            label='Plasma'
        )
        ax.add_patch(ellipse)
        
        # Draw major radius circle
        circle = plt.Circle(
            (0, 0),
            major_radius,
            fill=False,
            edgecolor='yellow',
            linestyle='--',
            linewidth=1,
            label='Major Radius'
        )
        ax.add_patch(circle)
        
        # Draw center point
        ax.plot(0, 0, 'ro', markersize=10, label='Center')
        
        # Labels
        ax.annotate(f'R₀ = {major_radius:.2f} m', 
                   xy=(major_radius, 0), 
                   xytext=(major_radius + 0.5, 0.5),
                   color='yellow', fontsize=10)
        ax.annotate(f'a = {minor_radius:.2f} m',
                   xy=(major_radius, minor_radius),
                   xytext=(major_radius + 0.5, minor_radius + 0.5),
                   color='cyan', fontsize=10)
        
        ax.set_xlim(-major_radius * 1.5, major_radius * 2.5)
        ax.set_ylim(-major_radius * 1.2, major_radius * 1.2)
        ax.set_aspect('equal')
        ax.set_xlabel('R (m)', fontsize=12)
        ax.set_ylabel('Z (m)', fontsize=12)
        ax.set_title('Tokamak Reactor Geometry', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def plot_plasma_parameters(self, states: Dict[str, np.ndarray]) -> Figure:
        """Plot plasma parameters over time or iterations.
        
        Args:
            states: Dictionary of parameter arrays
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Plasma Parameters', fontsize=16, fontweight='bold')
        
        # Temperature
        if 'temperature' in states:
            axes[0, 0].plot(states['temperature'] / 1e6, 'r-', linewidth=2)
            axes[0, 0].axhline(y=15, color='g', linestyle='--', label='Optimal (15 MK)')
            axes[0, 0].set_xlabel('Time/Iteration')
            axes[0, 0].set_ylabel('Temperature (MK)')
            axes[0, 0].set_title('Plasma Temperature')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)
        
        # Density
        if 'density' in states:
            axes[0, 1].plot(states['density'] / 1e20, 'b-', linewidth=2)
            axes[0, 1].set_xlabel('Time/Iteration')
            axes[0, 1].set_ylabel('Density (10²⁰ m⁻³)')
            axes[0, 1].set_title('Plasma Density')
            axes[0, 1].grid(True, alpha=0.3)
        
        # Triple product
        if 'triple_product' in states:
            axes[1, 0].plot(states['triple_product'] / 1e21, 'g-', linewidth=2)
            axes[1, 0].axhline(y=3.0, color='r', linestyle='--', label='Lawson (3×10²¹)')
            axes[1, 0].set_xlabel('Time/Iteration')
            axes[1, 0].set_ylabel('Triple Product (10²¹ m⁻³·s·K)')
            axes[1, 0].set_title('Triple Product (nτT)')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
        
        # Q factor
        if 'q_factor' in states:
            axes[1, 1].plot(states['q_factor'], 'm-', linewidth=2)
            axes[1, 1].axhline(y=1.0, color='y', linestyle='--', label='Breakeven (Q=1)')
            axes[1, 1].axhline(y=10.0, color='g', linestyle='--', label='Ignition (Q=10)')
            axes[1, 1].set_xlabel('Time/Iteration')
            axes[1, 1].set_ylabel('Q Factor')
            axes[1, 1].set_title('Q Factor (Fusion/Input Power)')
            axes[1, 1].set_yscale('log')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_power_balance(self, power_data: Dict[str, float]) -> Figure:
        """Plot power balance diagram.
        
        Args:
            power_data: Dictionary of power values
            
        Returns:
            Matplotlib figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Power Balance', fontsize=16, fontweight='bold')
        
        # Power flow diagram
        if 'fusion_power' in power_data and 'input_power' in power_data:
            powers = ['Fusion\nPower', 'Input\nPower', 'Output\nPower']
            values = [
                power_data.get('fusion_power', 0) / 1e6,
                power_data.get('input_power', 0) / 1e6,
                power_data.get('output_power', 0) / 1e6
            ]
            colors = ['green' if v > 0 else 'red' for v in values]
            
            bars = ax1.bar(powers, values, color=colors, alpha=0.7, edgecolor='white', linewidth=2)
            ax1.set_ylabel('Power (MW)')
            ax1.set_title('Power Components')
            ax1.grid(True, alpha=0.3, axis='y')
            
            # Add value labels
            for bar, val in zip(bars, values):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{val:.1f} MW',
                        ha='center', va='bottom' if val > 0 else 'top', fontweight='bold')
        
        # Q factor indicator
        if 'q_factor' in power_data:
            q = power_data['q_factor']
            if np.isinf(q):
                q_display = float('inf')
                q_label = '∞ (Ignition)'
            else:
                q_display = q
                q_label = f'Q = {q:.2f}'
            
            # Color based on Q
            if q >= 10 or np.isinf(q):
                q_color = 'green'
            elif q >= 1:
                q_color = 'yellow'
            else:
                q_color = 'red'
            
            ax2.text(0.5, 0.5, q_label, 
                    ha='center', va='center',
                    fontsize=24, fontweight='bold',
                    color=q_color,
                    transform=ax2.transAxes)
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
            ax2.axis('off')
            ax2.set_title('Q Factor Status')
        
        plt.tight_layout()
        return fig
    
    def create_status_dashboard(self, status_data: Dict) -> Figure:
        """Create a comprehensive status dashboard.
        
        Args:
            status_data: Dictionary of status information
            
        Returns:
            Matplotlib figure
        """
        fig = plt.figure(figsize=(16, 10))
        # Use 4 columns to accommodate 5 parameters (3+2 layout)
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        fig.suptitle('Fusion Reactor Status Dashboard', fontsize=18, fontweight='bold')
        
        # Status indicators
        ax_status = fig.add_subplot(gs[0, :])
        ax_status.axis('off')
        
        # Overall status
        if status_data.get('operational', False):
            status_color = 'green'
            status_text = 'OPERATIONAL'
        elif status_data.get('errors', []):
            status_color = 'red'
            status_text = 'ERRORS DETECTED'
        else:
            status_color = 'yellow'
            status_text = 'WARNING'
        
        ax_status.text(0.5, 0.5, status_text,
                      ha='center', va='center',
                      fontsize=32, fontweight='bold',
                      color=status_color,
                      bbox=dict(boxstyle='round', facecolor='black', edgecolor=status_color, linewidth=3),
                      transform=ax_status.transAxes)
        
        # Key parameters - arrange in 3+2 layout
        params = [
            ('Temperature', status_data.get('temperature', 0) / 1e6, 'MK', 'red'),
            ('Density', status_data.get('density', 0) / 1e20, '10²⁰ m⁻³', 'blue'),
            ('Q Factor', status_data.get('q_factor', 0), '', 'green'),
            ('Fusion Power', status_data.get('fusion_power', 0) / 1e6, 'MW', 'cyan'),
            ('TBR', status_data.get('tbr', 0), '', 'yellow'),
        ]
        
        # First row: 3 parameters
        for idx in range(3):
            name, value, unit, color = params[idx]
            ax = fig.add_subplot(gs[1, idx])
            ax.axis('off')
            if np.isinf(value) or np.isnan(value):
                val_str = '∞' if np.isinf(value) else 'N/A'
            else:
                val_str = f'{value:.2f}'
            ax.text(0.5, 0.5, f'{name}\n{val_str} {unit}',
                   ha='center', va='center',
                   fontsize=14, fontweight='bold',
                   color=color,
                   transform=ax.transAxes)
        
        # Second row: 2 parameters (spanning 2 columns each, centered)
        for idx in range(3, 5):
            name, value, unit, color = params[idx]
            # Center the last two parameters
            col_start = (idx - 3) * 2
            ax = fig.add_subplot(gs[1, col_start:col_start+2])
            ax.axis('off')
            if np.isinf(value) or np.isnan(value):
                val_str = '∞' if np.isinf(value) else 'N/A'
            else:
                val_str = f'{value:.2f}'
            ax.text(0.5, 0.5, f'{name}\n{val_str} {unit}',
                   ha='center', va='center',
                   fontsize=14, fontweight='bold',
                   color=color,
                   transform=ax.transAxes)
        
        # Error display
        ax_errors = fig.add_subplot(gs[2, :])
        ax_errors.axis('off')
        errors = status_data.get('errors', [])
        warnings = status_data.get('warnings', [])
        
        if errors:
            error_text = 'ERRORS:\n' + '\n'.join(f'• {e}' for e in errors)
            if warnings:
                error_text += '\n\nWARNINGS:\n' + '\n'.join(f'⚠ {w}' for w in warnings)
            ax_errors.text(0.05, 0.5, error_text,
                          ha='left', va='center',
                          fontsize=12,
                          color='red',
                          transform=ax_errors.transAxes,
                          bbox=dict(boxstyle='round', facecolor='black', edgecolor='red'))
        elif warnings:
            warning_text = 'WARNINGS:\n' + '\n'.join(f'⚠ {w}' for w in warnings)
            ax_errors.text(0.05, 0.5, warning_text,
                          ha='left', va='center',
                          fontsize=12,
                          color='yellow',
                          transform=ax_errors.transAxes,
                          bbox=dict(boxstyle='round', facecolor='black', edgecolor='yellow'))
        else:
            ax_errors.text(0.5, 0.5, 'No errors detected',
                          ha='center', va='center',
                          fontsize=14,
                          color='green',
                          transform=ax_errors.transAxes)
        
        return fig
    
    def save_figure(self, fig: Figure, filename: str):
        """Save figure to file.
        
        Args:
            fig: Matplotlib figure
            filename: Filename (will be saved in plots/ folder)
        """
        from pathlib import Path
        
        # Create plots directory if it doesn't exist
        plots_dir = Path('plots')
        plots_dir.mkdir(exist_ok=True)
        
        # Ensure filename is in plots directory
        if not str(filename).startswith('plots/'):
            filepath = plots_dir / filename
        else:
            filepath = Path(filename)
        
        fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='black')
        print(f"Saved: {filepath}")
        """Save figure to file.
        
        Args:
            fig: Matplotlib figure
            filename: Output filename
        """
        fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='black')
        plt.close(fig)

