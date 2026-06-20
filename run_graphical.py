#!/usr/bin/env python3
"""
run_graphical.py - Run Fly-in simulation with graphical visualization using Pygame

Displays the network as a graph with animated drones.
"""

import sys
import importlib.util

from graphical_visualizer import GraphicalVisualizer
from simulation import SimulationManager
from short_path import Solver

def load_fly_in_module():
    """Load fly-in.py module (has hyphen in name)"""
    spec = importlib.util.spec_from_file_location("fly_in", "/home/moamhouc/Desktop/Fly-in/fly-in.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_graphical(filepath: str):
    """Run simulation with graphical visualization"""
    
    try:
        # Load Flyin class
        fly_in_module = load_fly_in_module()
        Flyin = fly_in_module.Flyin
        
        # Initialize and parse
        app = Flyin(filepath)
        app._parse()
        app._build_graph()
        
        # Create graphical visualizer
        visualizer = GraphicalVisualizer(app.graph, width=1200, height=800)
        
        # Create simulation manager
        sim = SimulationManager(app.graph, app.simulation.solver if hasattr(app.simulation, 'solver') else Solver(app.graph))
        
        # Run simulation with visualization
        sim.setup()
        logs = []
        
        while not all(drone.delivered for drone in sim.drones):
            # Run simulation step
            output_transit = sim.resolve_transit()
            occupancy = sim.zone_occupancy()
            planned, output_moves = sim.decide_moves(occupancy)
            sim.start_moves(planned)
            full_out = sim.output_line(list(output_transit + output_moves))
            sim.check_deadlock(full_out)
            logs.append(full_out)
            
            # Display this turn
            if not visualizer.display_turn(sim.drones, logs):
                break
        
        # Show final summary
        visualizer.display_final_summary(sim.drones, logs)
        visualizer.close()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 run_graphical.py <map_file>")
        print("Example: python3 run_graphical.py map.txt")
        print("\nNote: Requires pygame. Install with: pip install pygame")
        sys.exit(1)
    
    filepath = sys.argv[1]
    exit_code = run_graphical(filepath)
    sys.exit(exit_code)

