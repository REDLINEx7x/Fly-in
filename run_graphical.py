#!/usr/bin/env python3
"""
run_graphical.py - Integrated graphical visualization with actual simulation

Runs the real simulation, collects history, and displays via Pygame GUI.
"""

import sys
import importlib.util
from map_parser import Parser
from objects import Graph
from short_path import Solver
from simulation import SimulationManager
from graphical_visualizer import GraphicalVisualizer

def load_fly_in_module():
    """Load fly-in.py module (has hyphen in name)"""
    spec = importlib.util.spec_from_file_location("fly_in", "/home/moamhouc/Desktop/Fly-in/fly-in.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_graphical(filepath: str):
    """Run simulation and display graphically"""
    
    print("\n" + "="*80)
    print("FLY-IN DRONE DELIVERY - GRAPHICAL VISUALIZATION".center(80))
    print("="*80 + "\n")
    
    try:
        # 1. Parse the map file
        print("📍 Parsing map file...")
        parser = Parser(filepath)
        parser.read_file()
        
        # 2. Build the graph
        print("🔗 Building graph...")
        graph = Graph.from_parsed(parser)
        
        # 3. Create solver
        print("🧭 Initializing pathfinding...")
        solver = Solver(graph)
        
        # 4. Create simulation manager
        print("⚙️  Setting up simulation engine...")
        sim = SimulationManager(graph, solver)
        
        # 5. Run simulation and collect history
        print("🚁 Running simulation...\n")
        
        sim.setup()
        simulation_history = []
        
        turn_count = 0
        while not all(drone.delivered for drone in sim.drones):
            turn_count += 1
            
            # Run one simulation step
            output_transit = sim.resolve_transit()
            occupancy = sim.zone_occupancy()
            planned, output_moves = sim.decide_moves(occupancy)
            sim.start_moves(planned)
            full_out = sim.output_line(list(output_transit + output_moves))
            sim.check_deadlock(full_out)
            
            # Collect turn data for visualization
            turn_data = {
                "turn": turn_count,
                "logs": full_out.split() if full_out.strip() else ["No moves"],
                "positions": {},
                "status": {}
            }
            
            # Record drone positions and status
            for drone in sim.drones:
                drone_id = f"D{drone.drone_id}"
                turn_data["positions"][drone_id] = drone.current_zone.name
                
                # Drone status
                if drone.delivered:
                    turn_data["status"][drone_id] = "✓ DELIVERED"
                elif drone.in_transit:
                    turn_data["status"][drone_id] = f"⏳ IN TRANSIT ({drone.transit_turns_left})"
                else:
                    turn_data["status"][drone_id] = "→ MOVING"
            
            simulation_history.append(turn_data)
            
            # Print progress
            print(f"  Turn {turn_count}: {full_out if full_out.strip() else 'No moves'}")
        
        print(f"\n✓ Simulation complete in {turn_count} turns!")
        print("\n🎨 Launching graphical visualization...\n")
        
        # 6. Launch graphical visualizer
        visualizer = GraphicalVisualizer(graph, simulation_history)
        visualizer.run()
        
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
        sys.exit(1)
    
    filepath = sys.argv[1]
    exit_code = run_graphical(filepath)
    sys.exit(exit_code)

