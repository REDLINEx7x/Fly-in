*This project has been created as part of the 42 curriculum by moamhouc.*

# Fly-in: Autonomous Drone Delivery Routing System

## Description

Fly-in is an efficient autonomous drone delivery routing system designed to navigate multiple drones through a complex network of connected zones while minimizing the total number of simulation turns. The system intelligently handles movement constraints, respects zone capacity limits, manages multi-turn restricted zone transitions, and prevents conflicts through real-time capacity tracking and deadlock detection.

**Project Goal:**
Optimize drone fleet routing through a zone network subject to strict movement constraints and capacity limitations, achieving minimal delivery times while maintaining conflict-free operations.

**Brief Overview:**
The system combines advanced pathfinding algorithms (Dijkstra's algorithm for optimal single paths and cost-pruned DFS for discovering all optimal alternatives) with a sophisticated turn-by-turn simulation engine. It enforces zone occupancy constraints, manages connection bandwidth, handles specialized zone types (normal, restricted, priority, blocked), and dynamically distributes drones across multiple optimal routes to maximize throughput.

**Key Features:**
- Multi-algorithm pathfinding combining Dijkstra and cost-pruned DFS
- Four zone types with distinct movement mechanics (normal: 1 turn, restricted: 2 turns, priority: 1 turn preferred, blocked: inaccessible)
- Per-zone and per-connection capacity constraints with real-time enforcement
- Turn-by-turn simulation with deadlock detection and prevention
- Comprehensive input validation with detailed error reporting and line-number references
- Colored terminal output for enhanced visual feedback

---

## Instructions

### Installation

Install the project dependencies:

```bash
make install
```

This command:
- Installs core dependencies: `pydantic` (data validation)
- Installs development tools: `flake8` (linting), `mypy` (type checking)

### Compilation and Execution

**Build and run the simulation:**

```bash
make run FILE=path/to/map.txt
```

**Direct execution (without make):**

```bash
python3 fly-in.py path/to/map.txt
```

### Output Format

The simulation outputs drone movements turn-by-turn:

```
D0-zone_a D1-zone_a D2-zone_b
D0-zone_b D1-zone_b D2-zone_c
D0-zone_c D1-zone_c D2-zone_d
D0-goal D1-goal D2-goal
```

**Format specification:**
- `D<drone_id>-<zone_name>` for movement into a zone
- `D<drone_id>-<connection_name>` for movement on restricted zone connection (2-turn transit)
- Drones not moving in a turn are omitted from that line
- Delivered drones are no longer tracked in output
- Simulation terminates once all drones reach the goal

### Usage Example

Example input map:

```txt
nb_drones: 1
start_hub: start 0 0
hub: middle 1 0
end_hub: goal 2 0
connection: start-middle
connection: middle-goal
```

Expected output:

```txt
D0-middle
D0-goal
```

### Code Quality Verification

Run linting and type-checking:

```bash
make lint          # Run flake8 and mypy (standard mode)
make lint-strict   # Run mypy with strict settings
make clean         # Clean cache and virtual environment
```

---

## Resources

### References

**Pathfinding Algorithms:**
- Dijkstra's Algorithm - https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- Depth-First Search (DFS) - https://en.wikipedia.org/wiki/Depth-first_search
- Graph Theory Fundamentals - Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein)

**Software Engineering & Python:**
- Python Type Hints - https://docs.python.org/3/library/typing.html
- Pydantic Data Validation - https://docs.pydantic.dev/
- PEP 257 Docstring Conventions - https://www.python.org/dev/peps/pep-0257/
- PEP 8 Style Guide - https://www.python.org/dev/peps/pep-0008/

### AI Usage

AI was used throughout this project for the following tasks:

- **Architecture design**: Discussing the OOP structure and responsibility split across [objects.py](objects.py), [short_path.py](short_path.py), and [simulation.py](simulation.py) before writing code
- **Algorithm logic**: Explaining the Dijkstra + cost-pruned DFS hybrid approach and reasoning through edge cases in the pathfinder
- **Bug investigation**: Reviewing logic errors across the parser, validation, graph model, and simulation flow
- **Test asset generation**: Generating the benchmark map files in [maps/](maps/) and the test runner script [test.sh](test.sh)

---

## Algorithm Description

### Overall Strategy

The system employs a two-phase routing approach: first discovering all optimal paths using hybrid pathfinding, then executing a turn-by-turn simulation with capacity-aware move planning.

### Phase 1: Pathfinding

**1. Dijkstra's Algorithm (Single Shortest Path)**
- Establishes the baseline optimal cost from start to goal
- Movement costs: Normal=1, Restricted=2, Priority=1, Blocked=∞
- Time complexity: O((V + E) log V) with binary heap
- Output: Single shortest path with minimum total cost

**2. Cost-Pruned DFS (All Optimal Paths)**
- Discovers all alternative paths matching the baseline optimal cost
- Starts DFS from origin, explores all neighbors recursively
- Prunes any branch where cumulative cost exceeds the baseline
- Backtracks upon reaching dead-ends or pruned nodes
- Records all complete paths reaching the goal at optimal cost
- Prevents exponential explosion in dense graphs while guaranteeing optimality

**3. Multi-Drone Path Distribution**
- Round-robin assignment across all discovered optimal paths
- Load balancing reduces zone congestion and improves throughput

### Phase 2: Simulation

Per-turn execution cycle:

1. **Resolve Transit** — process drones in 2-turn restricted zone transit, decrement counter, move drone on completion
2. **Calculate Occupancy** — count drones per zone (excluding those in transit)
3. **Plan Moves** — for each active drone, check zone capacity and connection capacity before scheduling movement
4. **Execute Moves** — update drone positions, handle restricted zone entry (set in_transit, transit_counter)
5. **Deadlock Detection** — if no movement occurred and no drones are in transit and not all delivered, raise error

**Key constraint rule:** Drones moving out of a zone free up capacity in that same turn, allowing following drones to enter immediately.

---

## Visual Representation

### Terminal Output Features

The simulation provides colored terminal output to enhance user understanding of drone movements and network state.

**Color Scheme (ANSI Terminal Colors):**
- **Green**: Start hub (delivery origin)
- **Red**: End hub (delivery destination)
- **Blue**: Normal zones (standard routing nodes)
- **Orange**: Restricted zones (2-turn transit, require planning)
- **Purple**: Priority zones (preferred routing nodes)
- **Cyan**: High-capacity zones (max_drones > 1, potential bottlenecks)

**User Experience Benefits:**

- **Zone type recognition at a glance** — color coding makes zone types immediately visible without reading metadata
- **Bottleneck identification** — high-capacity zones stand out visually, helping users understand where congestion may occur
- **Progress tracking** — turn-by-turn output shows simulation advancement; delivery events (`D<id>-goal`) confirm completion
- **Error clarity** — parsing errors include line numbers and constraint violation details for fast debugging

---

## Project Structure

```
Fly-in/
├── fly-in.py              # Main entry point and orchestration
├── map_parser.py          # File parsing and structure extraction
├── validation.py          # Pydantic models for type validation
├── objects.py             # Domain objects (Drone, Zone, Connection, Graph)
├── short_path.py          # Pathfinding (Dijkstra + cost-pruned DFS)
├── simulation.py          # Turn-by-turn simulation engine
├── terminal_output.py     # Colored terminal output formatting
├── Makefile               # Build automation and task runners
├── README.md              # Project documentation (this file)
```
