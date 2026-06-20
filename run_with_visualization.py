#!/usr/bin/env python3
"""
run_with_visualization.py - Run Fly-in simulation with terminal ASCII visualization

This script runs the same simulation as fly-in.py but adds real-time terminal graphics.
It does NOT modify any existing files - purely additive visualization.
"""

import sys
import importlib.util

from visualizer import TerminalVisualizer
from simulation import SimulationManager
from short_path import Solver

def load_fly_in_module():
    """Load fly-in.py module (has hyphen in name)"""
    spec = importlib.util.spec_from_file_location("fly_in", "/home/moamhouc/Desktop/Fly-in/fly-in.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_visualized(filepath: str):
    """Run simulation with ASCII visualization"""
    
    print("\n" + "="*80)
    print("FLY-IN DRONE DELIVERY SIMULATION WITH TERMINAL VISUALIZATION".center(80))
    print("="*80 + "\n")
    
    try:
        # Load Flyin class
        fly_in_module = load_fly_in_module()
        Flyin = fly_in_module.Flyin
        
        # Initialize and parse (using existing Flyin class)
        app = Flyin(filepath)
        app._parse()
        app._build_graph()
        
        # Create visualizer
        visualizer = TerminalVisualizer(app.graph)
        
        # Create simulation manager
        sim = SimulationManager(app.graph, app.simulation.solver if hasattr(app.simulation, 'solver') else Solver(app.graph))
        
        # Show initial state
        print("\n📍 INITIAL STATE:")
        print("─" * 80)
        visualizer.display_turn(sim.drones, sleep_time=0.0)
        
        # Run simulation with visualization
        print("▶️  STARTING SIMULATION...")
        print("─" * 80 + "\n")
        
        sim.setup()
        logs = []
        turn = 1
        
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
            visualizer.display_turn(sim.drones, sleep_time=0.8)
            turn += 1
        
        # Show final summary
        visualizer.display_final_summary(sim.drones, logs)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 run_with_visualization.py <map_file>")
        print("Example: python3 run_with_visualization.py map.txt")
        sys.exit(1)
    
    filepath = sys.argv[1]
    exit_code = run_visualized(filepath)
    sys.exit(exit_code)

