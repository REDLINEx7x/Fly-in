"""Display utilities for colored terminal output of the simulation."""

from typing import Optional

from objects import Graph


RESET: str = "\033[0m"

COLOR_MAP: dict[str, str] = {
    # Original Colors
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "gray": "\033[90m",
    "grey": "\033[90m",
    "orange": "\033[38;5;208m",

    # New Colors extracted from the Nightmare Map
    "purple": "\033[38;5;129m",      # Deep purple (Maze traps)
    "black": "\033[30m",             # True black (Dead ends)
    "brown": "\033[38;5;94m",        # Sandy brown (Restricted loops)
    "maroon": "\033[38;5;88m",       # Dark maroon (Overflow hell)
    "gold": "\033[38;5;220m",        # Bright gold (False hope priority zones)
    "darkred": "\033[38;5;52m",      # Wine dark-red (Convergence hell)
    "violet": "\033[38;5;135m",      # Light violet (Final merge)
    "crimson": "\033[38;5;197m",     # Intense crimson (Final gauntlet torture)
    "rainbow": "\033[38;5;201m",     # Neon flashing pink/magenta (The Ultimate Goal)
}

class Display:
    """Renders simulation output with colored terminal feedback."""

    @staticmethod
    def colorize(text: str, color_name: Optional[str]) -> str:

        """Wrap text in an ANSI color code.
        """
        if not color_name:
            return text
        code = COLOR_MAP.get(color_name.lower())
        if not code:
            return text
        return f"{code}{text}{RESET}"

    @staticmethod
    def resolve_zone_color(zone_name: str, graph: Graph) -> Optional[str]:
        """Resolve a zone's display color, with a deterministic fallback.

        """
        zone = graph.all_zones.get(zone_name)
        if not zone:
            return None
        if zone.color and zone.color.lower() in COLOR_MAP:
            return zone.color.lower()
        palette = list(COLOR_MAP.keys())
        return COLOR_MAP["white"]

    @classmethod
    def display_turn_line(cls, line: str, graph: Graph) -> str:
        """Build a colorized version of one turn's output line.

        """
        if not line:
            return ""
        rendered: list[str] = []
        for token in line.split():
            drone_part, _, target_part = token.partition("-")
            color = cls.resolve_zone_color(target_part, graph)
            rendered.append(f"{drone_part}-{cls.colorize(target_part, color)}")
        return " ".join(rendered)

    @classmethod
    def display_full_log(cls, turn_log: list[str], graph: Graph) -> None:
        """Print the full colorized simulation log to the terminal.
        """
        for line in turn_log:
            print(cls.display_turn_line(line, graph))
