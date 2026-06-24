"""Professional-grade graphical visualizer for drone simulation.

High-quality Pygame visualization with smooth animations, enhanced graphics,
and comprehensive visual feedback.
"""

import pygame
import math
from objects import Zone
from validation import ZoneType


class GraphicalVisualizer:
    """Professional Pygame visualization with premium visual effects."""

    def __init__(self, graph, simulation_history):
        """Initialize visualizer.

        Args:
            graph: The zone graph to display.
            simulation_history: List of turn data with positions and logs.
        """
        pygame.init()

        self.graph = graph
        self.simulation_history = simulation_history

        # Display settings
        self.width = 1600
        self.height = 1000
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("🚁 Fly-In Drone Delivery Simulation - Advanced Visualization")
        self.clock = pygame.time.Clock()

        # Premium fonts
        self.font_title = pygame.font.Font(None, 36)
        self.font_header = pygame.font.Font(None, 24)
        self.font_main = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 14)
        self.font_tiny = pygame.font.Font(None, 11)

        # Animation state
        self.current_turn_index = 0
        self.turn_timer = 0
        self.turn_duration = 120
        self.paused = False
        self.drone_visual_positions = {}
        self.drone_trails = {}  # Store drone movement trails

        # Enhanced color palette
        self.colors = {
            "bg_dark": (10, 10, 15),
            "bg_darker": (5, 5, 8),
            "white": (255, 255, 255),
            "accent": (100, 200, 255),
            "green": (80, 200, 120),
            "red": (255, 80, 80),
            "blue": (100, 150, 255),
            "orange": (255, 150, 50),
            "purple": (180, 100, 220),
            "yellow": (255, 220, 80),
            "cyan": (100, 220, 255),
            "lime": (150, 255, 100),
            "gray": (150, 150, 150),
            "dark_gray": (70, 70, 80),
            "light_gray": (200, 200, 200),
        }

        self.zone_positions = self._compute_zone_positions()
        self.glow_offset = 0
        self.frame_count = 0

    def _compute_zone_positions(self) -> dict[str, tuple[float, float]]:
        """Calculate zone screen positions."""
        positions = {}

        if not self.graph.all_zones:
            return positions

        zones = list(self.graph.all_zones.values())
        min_x = min(z.x for z in zones)
        max_x = max(z.x for z in zones)
        min_y = min(z.y for z in zones)
        max_y = max(z.y for z in zones)

        # Better padding for larger display
        padding_x = 200
        padding_y = 220
        usable_w = self.width - 2 * padding_x - 320
        usable_h = self.height - 2 * padding_y

        x_range = max_x - min_x if max_x > min_x else 1
        y_range = max_y - min_y if max_y > min_y else 1

        x_scale = usable_w / x_range * 0.8 if x_range > 0 else 1
        y_scale = usable_h / y_range * 0.8 if y_range > 0 else 1

        for zone_name, zone in self.graph.all_zones.items():
            px = padding_x + (zone.x - min_x) * x_scale + usable_w * 0.1
            py = padding_y + (zone.y - min_y) * y_scale + usable_h * 0.1
            positions[zone_name] = (px, py)

        return positions

    def _get_zone_color(self, zone: Zone) -> tuple[int, int, int]:
        """Get color for zone based on type."""
        if zone == self.graph.start:
            return self.colors["green"]
        elif zone == self.graph.end:
            return self.colors["red"]

        if hasattr(zone, 'zone_type'):
            if zone.zone_type == ZoneType.RESTRICTED:
                return self.colors["orange"]
            elif zone.zone_type == ZoneType.PRIORITY:
                return self.colors["purple"]
            elif zone.zone_type == ZoneType.BLOCKED:
                return self.colors["gray"]

        return self.colors["blue"]

    def _draw_background(self) -> None:
        """Draw elegant black background with gradient effect."""
        # Gradient-like background
        self.screen.fill(self.colors["bg_dark"])

        # Subtle animated grid
        grid_alpha = int(20 + 10 * math.sin(self.glow_offset * 0.05))
        grid_color = (grid_alpha, grid_alpha, grid_alpha + 5)
        grid_spacing = 60

        for x in range(0, self.width, grid_spacing):
            pygame.draw.line(
                self.screen, grid_color, (x, 0), (x, self.height), 1
            )
        for y in range(0, self.height, grid_spacing):
            pygame.draw.line(
                self.screen, grid_color, (0, y), (self.width, y), 1
            )

        # Decorative corner accents
        accent_color = (self.colors["accent"][0], self.colors["accent"][1],
                       int(self.colors["accent"][2] * (0.5 + 0.5 * math.sin(self.glow_offset * 0.03))))
        pygame.draw.line(self.screen, accent_color, (0, 0), (50, 0), 2)
        pygame.draw.line(self.screen, accent_color, (0, 0), (0, 50), 2)
        pygame.draw.line(self.screen, accent_color, (self.width - 50, 0), (self.width, 0), 2)
        pygame.draw.line(self.screen, accent_color, (self.width, 0), (self.width, 50), 2)

    def _draw_connections(self) -> None:
        """Draw connections with enhanced visuals."""
        for conn in self.graph.connections:
            if (conn.zone_a.name not in self.zone_positions or
                    conn.zone_b.name not in self.zone_positions):
                continue

            p1 = self.zone_positions[conn.zone_a.name]
            p2 = self.zone_positions[conn.zone_b.name]

            # Connection styling
            if conn.max_link_capacity > 1:
                color = self.colors["cyan"]
                width = 4
            else:
                color = self.colors["dark_gray"]
                width = 2

            # Draw connection line
            pygame.draw.line(self.screen, color, p1, p2, width)

            # Draw subtle glow
            glow_width = max(1, width - 1)
            glow_color = tuple(int(c * 0.4) for c in color)
            pygame.draw.line(self.screen, glow_color, p1, p2, width + 2)

            # Capacity indicator
            mid_x = (p1[0] + p2[0]) / 2
            mid_y = (p1[1] + p2[1]) / 2
            if conn.max_link_capacity > 1:
                cap_text = self.font_tiny.render(
                    f"Cap: {conn.max_link_capacity}", True, self.colors["cyan"]
                )
            else:
                cap_text = self.font_tiny.render(
                    "×1", True, self.colors["gray"]
                )
            self.screen.blit(cap_text, (mid_x - 15, mid_y - 8))

    def _get_star_points(self, center: tuple, outer: float, inner: float) -> list:
        """Calculate star polygon points."""
        points = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5
            radius = outer if i % 2 == 0 else inner
            x = center[0] + radius * math.cos(angle)
            y = center[1] - radius * math.sin(angle)
            points.append((x, y))
        return points

    def _draw_zones(self) -> None:
        """Draw zones with premium visual effects."""
        for zone_name, zone in self.graph.all_zones.items():
            if zone_name not in self.zone_positions:
                continue

            pos = self.zone_positions[zone_name]
            color = self._get_zone_color(zone)
            radius = 32

            # Multi-layer glow for start/end zones
            if zone == self.graph.start or zone == self.graph.end:
                glow_sizes = [radius + 14, radius + 10, radius + 6]
                glow_alpha = [20, 40, 80]

                for glow_r, alpha in zip(glow_sizes, glow_alpha):
                    pulse = int(4 * math.sin(self.glow_offset))
                    pygame.draw.circle(
                        self.screen,
                        tuple(int(c * alpha / 100) for c in color),
                        pos,
                        glow_r + pulse,
                        1
                    )

            # Main zone circle with gradient simulation
            pygame.draw.circle(self.screen, color, pos, radius)
            pygame.draw.circle(self.screen, self.colors["white"], pos, radius, 3)

            # Inner indicator
            inner_radius = radius - 12
            if zone.zone_type == ZoneType.RESTRICTED:
                pygame.draw.circle(
                    self.screen, self.colors["red"], pos, inner_radius, 2
                )
            elif zone.zone_type == ZoneType.PRIORITY:
                star_points = self._get_star_points(pos, 9, 6)
                pygame.draw.polygon(self.screen, self.colors["yellow"], star_points)
                pygame.draw.polygon(self.screen, self.colors["white"], star_points, 1)
            elif zone.zone_type == ZoneType.BLOCKED:
                offset = 11
                pygame.draw.line(
                    self.screen, self.colors["red"],
                    (pos[0] - offset, pos[1] - offset),
                    (pos[0] + offset, pos[1] + offset), 2
                )
                pygame.draw.line(
                    self.screen, self.colors["red"],
                    (pos[0] + offset, pos[1] - offset),
                    (pos[0] - offset, pos[1] + offset), 2
                )

            # Zone name with shadow
            shadow_text = self.font_main.render(
                zone_name, True, (0, 0, 0)
            )
            shadow_rect = shadow_text.get_rect(center=(pos[0] + 1, pos[1] + 1))
            self.screen.blit(shadow_text, shadow_rect)

            name_text = self.font_main.render(
                zone_name, True, self.colors["white"]
            )
            name_rect = name_text.get_rect(center=pos)
            self.screen.blit(name_text, name_rect)

            # Capacity badge
            if hasattr(zone, 'max_drones') and zone.max_drones > 1:
                badge_color = self.colors["cyan"]
                badge_rect = pygame.Rect(pos[0] + 20, pos[1] + 20, 28, 20)
                pygame.draw.rect(self.screen, badge_color, badge_rect, 0)
                pygame.draw.rect(self.screen, self.colors["white"], badge_rect, 1)
                cap_text = self.font_tiny.render(
                    f"×{zone.max_drones}", True, self.colors["bg_dark"]
                )
                cap_rect = cap_text.get_rect(center=badge_rect.center)
                self.screen.blit(cap_text, cap_rect)

    def _draw_drones(self) -> None:
        """Draw drones with trails and effects."""
        if self.current_turn_index >= len(self.simulation_history):
            return

        turn_data = self.simulation_history[self.current_turn_index]
        positions = turn_data.get("positions", {})
        status = turn_data.get("status", {})

        drone_colors = [
            self.colors["yellow"],
            self.colors["cyan"],
            self.colors["lime"],
            (255, 120, 200),
            (100, 255, 200),
            (255, 180, 100),
        ]

        for drone_id, zone_name in positions.items():
            if zone_name not in self.zone_positions:
                continue

            target_pos = self.zone_positions[zone_name]

            if drone_id not in self.drone_visual_positions:
                self.drone_visual_positions[drone_id] = list(target_pos)
                self.drone_trails[drone_id] = []

            # Smooth movement
            curr_pos = self.drone_visual_positions[drone_id]
            curr_pos[0] += (target_pos[0] - curr_pos[0]) * 0.15
            curr_pos[1] += (target_pos[1] - curr_pos[1]) * 0.15

            draw_pos = (int(curr_pos[0]), int(curr_pos[1]))

            # Update trail
            if len(self.drone_trails[drone_id]) == 0 or \
               abs(self.drone_trails[drone_id][-1][0] - draw_pos[0]) > 5:
                self.drone_trails[drone_id].append(draw_pos)
                if len(self.drone_trails[drone_id]) > 15:
                    self.drone_trails[drone_id].pop(0)

            # Draw trail with fade
            for i, trail_pos in enumerate(self.drone_trails[drone_id]):
                alpha = int(50 * i / len(self.drone_trails[drone_id]))
                color = tuple(max(0, c - alpha) for c in drone_colors[int(drone_id[1:]) % len(drone_colors)])
                pygame.draw.circle(self.screen, color, trail_pos, 3)

            # Get drone color
            drone_idx = int(drone_id.replace("D", ""))
            color = drone_colors[drone_idx % len(drone_colors)]

            # Draw drone shadow
            shadow_pos = (draw_pos[0] + 2, draw_pos[1] + 2)
            pygame.draw.circle(self.screen, (0, 0, 0), shadow_pos, 14)

            # Draw drone
            pygame.draw.circle(self.screen, color, draw_pos, 14)
            pygame.draw.circle(self.screen, self.colors["white"], draw_pos, 14, 2)

            # Drone ID
            id_text = self.font_tiny.render(
                drone_id, True, self.colors["bg_dark"]
            )
            id_rect = id_text.get_rect(center=draw_pos)
            self.screen.blit(id_text, id_rect)

            # Status indicator
            drone_status = status.get(drone_id, "")
            if "DELIVERED" in drone_status:
                pygame.draw.circle(
                    self.screen, self.colors["green"], draw_pos, 18, 2
                )
            elif "IN TRANSIT" in drone_status:
                pygame.draw.circle(
                    self.screen, self.colors["orange"], draw_pos, 18, 2
                )

    def _draw_info_panel(self) -> None:
        """Draw right-side info panel with statistics."""
        panel_x = self.width - 300
        panel_width = 300
        panel_height = self.height - 200

        # Panel background with border
        pygame.draw.rect(
            self.screen,
            self.colors["dark_gray"],
            (panel_x, 160, panel_width, panel_height)
        )
        pygame.draw.rect(
            self.screen,
            self.colors["accent"],
            (panel_x, 160, panel_width, panel_height),
            2
        )

        # Panel title
        title = self.font_header.render("Statistics", True, self.colors["white"])
        self.screen.blit(title, (panel_x + 20, 175))

        if self.current_turn_index < len(self.simulation_history):
            turn_data = self.simulation_history[self.current_turn_index]
            status = turn_data.get("status", {})

            delivered = sum(1 for s in status.values() if "DELIVERED" in s)
            in_transit = sum(1 for s in status.values() if "IN TRANSIT" in s)
            moving = len(status) - delivered - in_transit

            # Stats with color coding
            stats = [
                ("Delivered", str(delivered), self.colors["green"]),
                ("In Transit", str(in_transit), self.colors["orange"]),
                ("Moving", str(moving), self.colors["cyan"]),
                ("Total", str(len(status)), self.colors["light_gray"]),
            ]

            y = 220
            for label, value, color in stats:
                label_text = self.font_small.render(label, True, self.colors["light_gray"])
                value_text = self.font_header.render(value, True, color)
                self.screen.blit(label_text, (panel_x + 20, y))
                self.screen.blit(value_text, (panel_x + 220, y - 2))
                y += 50

    def _draw_top_panel(self) -> None:
        """Draw top information panel."""
        panel_height = 160
        pygame.draw.rect(
            self.screen,
            self.colors["dark_gray"],
            (0, 0, self.width, panel_height)
        )
        pygame.draw.line(
            self.screen,
            self.colors["accent"],
            (0, panel_height),
            (self.width, panel_height),
            2
        )

        if self.current_turn_index < len(self.simulation_history):
            turn_data = self.simulation_history[self.current_turn_index]
            turn_num = turn_data.get("turn", 0)
            total_turns = len(self.simulation_history)

            # Turn info
            turn_text = self.font_title.render(
                f"Turn {turn_num} / {total_turns}",
                True, self.colors["white"]
            )
            progress = turn_num / total_turns if total_turns > 0 else 0
            self.screen.blit(turn_text, (20, 15))

            # Progress bar
            bar_width = 600
            bar_x = 20
            bar_y = 60
            pygame.draw.rect(self.screen, self.colors["dark_gray"], (bar_x, bar_y, bar_width, 20), 1)
            pygame.draw.rect(
                self.screen, self.colors["accent"],
                (bar_x, bar_y, int(bar_width * progress), 20)
            )

            # Actions
            logs = turn_data.get("logs", [])
            actions_str = " → ".join(logs[:6])
            if len(logs) > 6:
                actions_str += " ..."
            actions_text = self.font_main.render(
                f"Actions: {actions_str}",
                True, self.colors["light_gray"]
            )
            self.screen.blit(actions_text, (20, 95))

            # Pause status
            if self.paused:
                pause_text = self.font_main.render(
                    "⏸ PAUSED", True, self.colors["yellow"]
                )
                self.screen.blit(pause_text, (700, 25))

        # Controls
        controls = "SPACE: Pause | ←→: Navigate | Q: Quit"
        control_text = self.font_small.render(
            controls, True, self.colors["gray"]
        )
        self.screen.blit(control_text, (self.width - 450, 25))

    def _handle_events(self) -> bool:
        """Handle events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_LEFT:
                    if self.current_turn_index > 0:
                        self.current_turn_index -= 1
                        self.turn_timer = 0
                elif event.key == pygame.K_RIGHT:
                    if self.current_turn_index < len(self.simulation_history) - 1:
                        self.current_turn_index += 1
                        self.turn_timer = 0
        return True

    def run(self) -> None:
        """Main loop."""
        running = True

        while running:
            running = self._handle_events()

            # Draw everything
            self._draw_background()
            self._draw_connections()
            self._draw_zones()
            self._draw_drones()
            self._draw_top_panel()
            self._draw_info_panel()

            pygame.display.flip()
            self.clock.tick(60)

            self.glow_offset += 0.1
            self.frame_count += 1

            if not self.paused:
                self.turn_timer += 1
                if self.turn_timer >= self.turn_duration:
                    if self.current_turn_index < len(self.simulation_history) - 1:
                        self.current_turn_index += 1
                    self.turn_timer = 0

        pygame.quit()

