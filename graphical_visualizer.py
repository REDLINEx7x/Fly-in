"""
graphical_visualizer.py - Graphical visualization of Fly-in drone simulation using Pygame

Displays zones as nodes and drones as animated objects moving through the network.
"""

import pygame
import math
import sys
from objects import Graph, Drone, Zone

class GraphicalVisualizer:
    """Pygame-based graphical visualization for drone simulation"""
    
    def __init__(self, graph: Graph, width=1200, height=800, speed=2.0):
        pygame.init()
        
        self.graph = graph
        self.width = width
        self.height = height
        self.speed = speed  # Pixels per frame
        self.turn = 0
        self.paused = False
        
        # Setup display
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("🚁 Fly-In Drone Delivery Simulation")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 28)
        self.font_medium = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        
        # Calculate zone positions on canvas
        self.zone_positions = self._compute_canvas_positions()
        
        # Drone animation state
        self.drone_positions = {}  # {drone_id: (x, y)}
        self.drone_targets = {}    # {drone_id: target_zone}
        
        # Colors
        self.colors = {
            "start": (76, 175, 80),        # Green
            "end": (244, 67, 54),          # Red
            "normal": (66, 133, 244),      # Blue
            "restricted": (255, 152, 0),   # Orange
            "priority": (156, 39, 176),    # Purple
            "blocked": (158, 158, 158),    # Gray
            "connection": (189, 189, 189), # Light gray
            "background": (245, 245, 245), # Off-white
            "text": (33, 33, 33),          # Dark gray
        }
    
    def _compute_canvas_positions(self) -> dict[str, tuple[float, float]]:
        """Map zone coordinates to canvas pixel positions"""
        positions = {}
        
        # Find min/max coordinates
        if not self.graph.all_zones:
            return positions
        
        zones = list(self.graph.all_zones.values())
        min_x = min(z.x for z in zones)
        max_x = max(z.x for z in zones)
        min_y = min(z.y for z in zones)
        max_y = max(z.y for z in zones)
        
        # Add padding
        padding_x = 100
        padding_y = 100
        usable_width = self.width - 2 * padding_x
        usable_height = self.height - 2 * padding_y - 80  # Reserve space for UI
        
        # Scale factors
        x_range = max_x - min_x if max_x > min_x else 1
        y_range = max_y - min_y if max_y > min_y else 1
        
        x_scale = usable_width / x_range if x_range > 0 else 1
        y_scale = usable_height / y_range if y_range > 0 else 1
        
        # Map zones
        for zone_name, zone in self.graph.all_zones.items():
            canvas_x = padding_x + (zone.x - min_x) * x_scale
            canvas_y = padding_y + (zone.y - min_y) * y_scale
            positions[zone_name] = (canvas_x, canvas_y)
        
        return positions
    
    def _get_zone_color(self, zone: Zone) -> tuple[int, int, int]:
        """Get RGB color for zone"""
        if zone == self.graph.start:
            return self.colors["start"]
        elif zone == self.graph.end:
            return self.colors["end"]
        else:
            zone_type_name = zone.zone_type.name
            return self.colors.get(zone_type_name.lower(), self.colors["normal"])
    
    def _draw_connections(self):
        """Draw connection lines between zones"""
        for conn in self.graph.connections:
            if conn.zone_a.name in self.zone_positions and conn.zone_b.name in self.zone_positions:
                start_pos = self.zone_positions[conn.zone_a.name]
                end_pos = self.zone_positions[conn.zone_b.name]
                
                pygame.draw.line(
                    self.screen,
                    self.colors["connection"],
                    start_pos,
                    end_pos,
                    2
                )
    
    def _draw_zones(self):
        """Draw all zones as circles"""
        for zone_name, zone in self.graph.all_zones.items():
            if zone_name not in self.zone_positions:
                continue
            
            pos = self.zone_positions[zone_name]
            radius = 40
            color = self._get_zone_color(zone)
            
            # Draw circle
            pygame.draw.circle(self.screen, color, pos, radius)
            pygame.draw.circle(self.screen, self.colors["text"], pos, radius, 3)
            
            # Draw zone name
            name_text = self.font_medium.render(zone_name, True, (255, 255, 255))
            name_rect = name_text.get_rect(center=pos)
            self.screen.blit(name_text, name_rect)
            
            # Draw occupancy
            occupancy_text = self.font_small.render(
                f"{zone.current_drones}/{zone.max_drones}",
                True,
                self.colors["text"]
            )
            occupancy_rect = occupancy_text.get_rect(center=(pos[0], pos[1] + 60))
            self.screen.blit(occupancy_text, occupancy_rect)
    
    def _draw_drones(self, drones: list[Drone]):
        """Draw all drones"""
        colors_map = {
            0: (255, 193, 7),    # Yellow
            1: (76, 175, 80),    # Green
            2: (33, 150, 243),   # Blue
            3: (156, 39, 176),   # Purple
        }
        
        for drone in drones:
            drone_id = drone.drone_id
            
            # Get drone's current visual position
            if drone_id not in self.drone_positions:
                # First time - start at current zone
                zone_pos = self.zone_positions[drone.current_zone.name]
                self.drone_positions[drone_id] = zone_pos
            
            current_pos = self.drone_positions[drone_id]
            color = colors_map.get(drone_id % len(colors_map), (255, 0, 0))
            
            # Draw drone as circle with ID
            drone_radius = 15
            pygame.draw.circle(self.screen, color, current_pos, drone_radius)
            pygame.draw.circle(self.screen, self.colors["text"], current_pos, drone_radius, 2)
            
            drone_text = self.font_small.render(f"D{drone_id}", True, (255, 255, 255))
            drone_rect = drone_text.get_rect(center=current_pos)
            self.screen.blit(drone_text, drone_rect)
            
            # Draw status indicator
            if drone.delivered:
                status = "✓"
                status_color = (76, 175, 80)
            elif drone.in_transit:
                status = "⏳"
                status_color = (255, 152, 0)
            else:
                status = "→"
                status_color = (33, 150, 243)
            
            status_text = self.font_small.render(status, True, status_color)
            status_rect = status_text.get_rect(center=(current_pos[0] + 25, current_pos[1] - 25))
            self.screen.blit(status_text, status_rect)
    
    def _draw_ui(self, drones: list[Drone], logs: list[str]):
        """Draw UI elements (turn counter, stats)"""
        ui_y = self.height - 70
        
        # Turn counter
        turn_text = self.font_large.render(f"Turn: {self.turn}", True, self.colors["text"])
        self.screen.blit(turn_text, (20, ui_y))
        
        # Delivery status
        delivered = sum(1 for d in drones if d.delivered)
        total = len(drones)
        status_text = self.font_medium.render(
            f"Delivered: {delivered}/{total}",
            True,
            self.colors["text"]
        )
        self.screen.blit(status_text, (150, ui_y))
        
        # In transit count
        in_transit = sum(1 for d in drones if d.in_transit)
        transit_text = self.font_medium.render(
            f"In Transit: {in_transit}",
            True,
            self.colors["text"]
        )
        self.screen.blit(transit_text, (400, ui_y))
        
        # Pause status
        if self.paused:
            pause_text = self.font_medium.render("PAUSED (SPACE to resume)", True, (244, 67, 54))
            self.screen.blit(pause_text, (650, ui_y))
        
        # Instructions
        info_text = self.font_small.render("SPACE: Pause | Q: Quit", True, (158, 158, 158))
        self.screen.blit(info_text, (20, ui_y + 25))
    
    def _update_drone_positions(self, drones: list[Drone]):
        """Update visual positions of drones (smooth animation toward target)"""
        for drone in drones:
            drone_id = drone.drone_id
            
            # Get target position (current zone)
            target_zone_pos = self.zone_positions[drone.current_zone.name]
            
            if drone_id not in self.drone_positions:
                self.drone_positions[drone_id] = target_zone_pos
            
            current_pos = self.drone_positions[drone_id]
            
            # Move toward target
            dx = target_zone_pos[0] - current_pos[0]
            dy = target_zone_pos[1] - current_pos[1]
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > self.speed:
                # Move one step toward target
                factor = self.speed / distance
                new_x = current_pos[0] + dx * factor
                new_y = current_pos[1] + dy * factor
                self.drone_positions[drone_id] = (new_x, new_y)
            else:
                # Reached target
                self.drone_positions[drone_id] = target_zone_pos
    
    def _handle_events(self) -> bool:
        """Handle pygame events. Return False if quit requested."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
        return True
    
    def render(self, drones: list[Drone], logs: list[str]) -> bool:
        """Render one frame. Return False if window closed."""
        # Handle events
        if not self._handle_events():
            return False
        
        # Update drone positions
        if not self.paused:
            self._update_drone_positions(drones)
        
        # Clear screen
        self.screen.fill(self.colors["background"])
        
        # Draw everything
        self._draw_connections()
        self._draw_zones()
        self._draw_drones(drones)
        self._draw_ui(drones, logs)
        
        # Update display
        pygame.display.flip()
        self.clock.tick(60)  # 60 FPS
        
        return True
    
    def display_turn(self, drones: list[Drone], logs: list[str]):
        """Display a turn and handle animation"""
        self.turn += 1
        
        # Animate until drones reach their destinations
        settled = False
        frames = 0
        max_frames = 120  # Max 2 seconds at 60 FPS
        
        while not settled and frames < max_frames:
            if not self.render(drones, logs):
                return False
            
            # Check if all drones are at their target zones
            all_settled = all(
                self.drone_positions[d.drone_id] == self.zone_positions[d.current_zone.name]
                for d in drones
                if d.drone_id in self.drone_positions
            )
            
            settled = all_settled
            frames += 1
        
        return True
    
    def display_final_summary(self, drones: list[Drone], logs: list[str]):
        """Show final summary screen"""
        # Display for 5 seconds or until user presses a key
        display_time = 0
        while display_time < 300:  # 5 seconds at 60 FPS
            if not self.render(drones, logs):
                return False
            
            # Draw "SIMULATION COMPLETE" message
            complete_text = self.font_large.render(
                "SIMULATION COMPLETE!",
                True,
                (76, 175, 80)
            )
            text_rect = complete_text.get_rect(
                center=(self.width // 2, self.height // 2 - 50)
            )
            self.screen.blit(complete_text, text_rect)
            
            # Handle early exit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_SPACE:
                        return False
            
            pygame.display.flip()
            self.clock.tick(60)
            display_time += 1
        
        return True
    
    def close(self):
        """Clean up pygame"""
        pygame.quit()

