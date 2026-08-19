"""Application entry point for the Fly-in simulation."""

import sys
from terminal_output import Display
from map_parser import Parser
from simulation import SimulationManager
from short_path import Solver
from objects import Graph


class Flyin:
    """Coordinate parsing, graph construction, and simulation output."""

    def __init__(self, filepath: str) -> None:
        """Store the input map path and initialize runtime state."""

        self.filepath = filepath
        self.parser: Parser | None = None
        self.graph: Graph | None = None
        self.simulation: SimulationManager | None = None

    @classmethod
    def start(cls, av: list[str]) -> None:
        """Parse command-line arguments and launch the simulation."""

        try:
            visual = "--visual" in av
            if visual:
                av = [a for a in av if a != "--visual"]

            if len(av) == 2:
                filepath = av[1]
                main = Flyin(filepath)
                main._parse()
                main._build_graph()
                main._run(visual=visual)
            else:
                print("Usage: python3 main.py <map_filepath> [--visual]")
                sys.exit(1)
        except Exception as e:
            print(f"Application Error: {e}")
            sys.exit(1)

    def _parse(self) -> None:
        """Load and validate the input map file."""

        try:
            self.parser = Parser(self.filepath)
            self.parser.read_file()
        except FileNotFoundError:
            raise ValueError(f"file '{self.filepath}' not found")
        except Exception as e:
            raise ValueError(f"Parsing failed: {e}")

    def _build_graph(self) -> None:
        """Convert parsed data into the runtime graph and solver."""

        if not self.parser:
            raise ValueError("Parser is not initialized.")
        try:
            self.graph = Graph.from_parsed(self.parser)
            if not self.graph:
                raise ValueError("Graph construction failed.")
            solver = Solver(self.graph)
            self.simulation = SimulationManager(self.graph, solver)
        except Exception as e:
            raise ValueError(f"Graph/Solver building failed: {e}")

    def _run(self, visual: bool = False) -> None:
        """Execute the simulation and print the formatted turn log."""

        if not self.simulation:
            raise ValueError("Simulation is not initialized.")

        try:
            turn_save = self.simulation.run_simulation()
            if self.graph is None:
                raise ValueError("Graph is not initialized.")
            Display.display_full_log(turn_save, self.graph)

            if visual:
                from visualizer import Visualizer
                viz = Visualizer(self.graph)
                viz.run(turn_save)
        except Exception as e:
            raise ValueError(f"Simulation crash: {e}")


if __name__ == "__main__":
    Flyin.start(sys.argv)
