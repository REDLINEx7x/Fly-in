#import heapq
#from parser import Parser
#from objects import Graph, Zone
#from short_path import Solver

#def test_full_flow():
#    # --- 1. PARSING ---
#    print("--- Step 1: Parsing ---")
#    try:
#        # T-akked bli 3ndek had l-file 'map.txt' f-blastu
#        parser = Parser("map.txt")
#        parser.read_file()
#        print("✅ Parsing: Success")
#    except Exception as e:
#        print(f"❌ Parsing Error: {e}")
#        return

#    # --- 2. GRAPH BUILDING (Object Mapping) ---
#    print("\n--- Step 2: Building Graph (Object Mapping) ---")
#    try:
#        # Hna kiy-tra l-mapping dyal logic_zones wast Connection.from_parsed
#        graph = Graph.from_parsed(parser)
#        print(f"✅ Graph: Success ({len(graph.all_zones)} zones found)")

#        # Test sghir: chouf wach Connection fiha Object machi String
#        first_con = graph.connections[0]
#        print(f"🔗 Connection Test: {type(first_con.zone_a)} found (Should be <class 'objects.Zone'>)")
#    except Exception as e:
#        print(f"❌ Graph Error: {e}")
#        import traceback
#        traceback.print_exc()
#        return

#    # --- 3. PATHFINDING (Dijkstra) ---
#    print("\n--- Step 3: Dijkstra Pathfinding ---")
#    solver = Solver(graph)

#    # Jbed Start w End objects direkt mn l-graph
#    start_zone = graph.start
#    end_zone = graph.end

#    if not start_zone or not end_zone:
#        print(f"❌ Error: Could not find start ({graph.start}) or end ({graph.end})")
#        return

#    path = solver.find_path(start_zone, end_zone)

#    # --- 4. RESULTS ---
#    print("\n--- Step 4: Results ---")
#    if path:
#        print(f"✅ Path Found! Steps: {len(path)}")
#        # Print l-path b-smiyat w-l-type
#        path_display = " -> ".join([f"[{z.name}]" for z in path])
#        print(f"Route: {path_display}")

#        # Check l-cost
#        cost = sum(z.movement_cost() for z in path if z != start_zone)
#        print(f"💰 Total Movement Cost: {cost}")
#    else:
#        print("❌ No path found. Check your connections or blocked zones.")

#if __name__ == "__main__":
#    test_full_flow()
