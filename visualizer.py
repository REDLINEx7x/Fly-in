# visualizer.py - Terminal ASCII Visualization for Fly-in Drone Simulation

import time
from objects import Graph, Drone, Zone

class TerminalVisualizer:
    """ASCII-based terminal visualization for drone simulation"""
    
    def __init__(self, graph: Graph, cell_width=14, cell_height=4):
        self.graph = graph
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.turn = 0
        self.zone_positions = self._compute_positions()
    
    def _compute_positions(self) -> dict[str, tuple[int, int]]:
        """Map zone names to grid coordinates based on their x,y in the graph"""
        positions = {}
        for zone_name, zone in self.graph.all_zones.items():
            canvas_x = zone.x * (self.cell_width + 3)
            canvas_y = zone.y * (self.cell_height + 2)
            positions[zone_name] = (canvas_x, canvas_y)
        return positions
    
    def _get_zone_symbol(self, zone: Zone) -> str:
        """Get visual symbol for zone based on type"""
        if zone == self.graph.start:
            return "🟢"
        elif zone == self.graph.end:
            return "🔴"
        else:
            symbols = {
                "NORMAL": "◇",
                "BLOCKED": "✕",
                "RESTRICTED": "⚠",
                "PRIORITY": "★",
            }
            return symbols.get(zone.zone_type.name, "◆")
    
    def _get_zone_color(self, zone: Zone) -> str:
        """Get ANSI color code for zone"""
        colors = {
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "red": "\033[91m",
            "cyan": "\033[96m",
            "magenta": "\033[95m",
            "white": "\033[97m",
        }
        return colors.get(zone.color, "\033[97m")
    
    def _reset_color(self) -> str:
        """Reset color to default"""
        return "\033[0m"
    
    def _draw_zone_box(self, zone: Zone, drones_here: list[Drone]) -> list[str]:
        """Draw a single zone box with drone information"""
        color = self._get_zone_color(zone)
        reset = self._reset_color()
        symbol = self._get_zone_symbol(zone)
        
        box = []
        box.append(f"{color}┌{'─' * (self.cell_width - 2)}┐{reset}")
        
        # Zone name
        name_display = f"{zone.name[:self.cell_width-4]}"
        box.append(f"{color}│{reset} {symbol} {name_display:<{self.cell_width-5}} {color}│{reset}")
        
        # Occupancy
        occupancy = f"{zone.current_drones}/{zone.max_drones}"
        box.append(f"{color}│{reset} Cap: {occupancy:<{self.cell_width-8}} {color}│{reset}")
        
        # Drones
        if drones_here:
            drone_str = ",".join([f"D{d.drone_id}" for d in drones_here])
            if len(drone_str) > self.cell_width - 2:
                drone_str = drone_str[:self.cell_width-3] + "…"
        else:
            drone_str = "—"
        box.append(f"{color}│{reset} {drone_str:<{self.cell_width-2}} {color}│{reset}")
        
        box.append(f"{color}└{'─' * (self.cell_width - 2)}┘{reset}")
        
        return box
    
    def render(self, drones: list[Drone]) -> str:
        """Render the current simulation state as ASCII art"""
        output = []
        
        # Header
        output.append("╔" + "═"*78 + "╗")
        output.append("║" + f"🚁 FLY-IN DRONE SIMULATION - TURN {self.turn}".center(78) + "║")
        output.append("╚" + "═"*78 + "╝")
        output.append("")
        
        # Zone visualization
        output.append("📍 ZONES AND DRONES:")
        output.append("─" * 80)
        
        # Group drones by location
        drones_by_zone = {}
        for drone in drones:
            zone_name = drone.current_zone.name
            if zone_name not in drones_by_zone:
                drones_by_zone[zone_name] = []
            drones_by_zone[zone_name].append(drone)
        
        # Display zones in grid format
        for zone_name in sorted(self.graph.all_zones.keys(), key=lambda z: (self.graph.all_zones[z].y, self.graph.all_zones[z].x)):
            zone = self.graph.all_zones[zone_name]
            drones_here = drones_by_zone.get(zone_name, [])
            zone_box = self._draw_zone_box(zone, drones_here)
            for line in zone_box:
                output.append(line)
            output.append("")
        
        # Connections
        output.append("\n📡 CONNECTIONS:")
        output.append("─" * 80)
        for conn in self.graph.connections:
            conn_str = f"  {conn.zone_a.name:<12} ━━━━ {conn.zone_b.name:<12} (capacity: {conn.max_link_capacity})"
            output.append(conn_str)
        
        # Drone detailed status
        output.append("\n\n🚁 DRONE STATUS:")
        output.append("─" * 80)
        for drone in drones:
            if drone.delivered:
                status = "✓ DELIVERED"
            elif drone.in_transit:
                status = f"⏳ IN TRANSIT ({drone.transit_turns_left} turns)"
            else:
                status = "→ MOVING"
            
            path_remaining = len(drone.path) if drone.path else 0
            output.append(f"  D{drone.drone_id}: Zone={drone.current_zone.name:<12} Status={status:<18} Path_remaining={path_remaining}")
        
        # Statistics
        output.append("\n📊 STATISTICS:")
        output.append("─" * 80)
        delivered = sum(1 for d in drones if d.delivered)
        in_transit = sum(1 for d in drones if d.in_transit)
        moving = len(drones) - delivered - in_transit
        output.append(f"  ✓ Delivered: {delivered}/{len(drones)} | ⏳ In Transit: {in_transit} | → Moving: {moving}")
        
        output.append("\n" + "═" * 80 + "\n")
        
        return "\n".join(output)
    
    def display_turn(self, drones: list[Drone], sleep_time: float = 1.0):
        """Display a turn and optionally sleep"""
        rendered = self.render(drones)
        print(rendered)
        if sleep_time > 0:
            time.sleep(sleep_time)
        self.turn += 1
    
    def display_final_summary(self, drones: list[Drone], logs: list[str]):
        """Display final simulation summary"""
        output = []
        output.append("\n" + "🎉" * 40)
        output.append("SIMULATION COMPLETE! 🎉".center(80))
        output.append("🎉" * 40 + "\n")
        
        output.append("📋 FINAL DRONE STATUS:")
        output.append("─" * 80)
        for drone in drones:
            status = "✓ DELIVERED" if drone.delivered else "✗ NOT DELIVERED"
            output.append(f"  D{drone.drone_id}: {drone.current_zone.name:<15} [{status}]")
        
        output.append("\n📝 SIMULATION LOG BY TURN:")
        output.append("─" * 80)
        for i, log in enumerate(logs, 1):
            output.append(f"  Turn {i:3d}: {log}")
        
        output.append("\n" + "─" * 80)
        output.append(f"Total Turns: {len(logs)}")
        output.append("All Drones Delivered: " + ("YES ✓" if all(d.delivered for d in drones) else "NO ✗"))
        output.append("=" * 80 + "\n")
        
        print("\n".join(output))

