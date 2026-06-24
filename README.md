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

Install the project with all dependencies:

```bash
make install
```

This command:
- Creates a Python virtual environment (`venv/`)
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

### Running Test Cases

The project includes three easy test maps demonstrating different constraint scenarios:

```bash
# Linear path with 2 drones (target: ≤ 6 turns)
python3 fly-in.py easy_1_linear.txt

# Forked paths with 3 drones (target: ≤ 6 turns)
python3 fly-in.py easy_2_fork.txt

# Capacity constraints with 4 drones (target: ≤ 8 turns)
python3 fly-in.py easy_3_capacity.txt

# Medium complexity network
python3 fly-in.py map.txt
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

### Code Quality Verification

Run linting and type-checking:

```bash
make lint          # Run flake8 and mypy (standard mode)
make lint-strict   # Run mypy with strict settings
make clean         # Clean cache and virtual environment
```

---

## Map File Format

### Syntax Specification

```
nb_drones: <positive_integer>

start_hub: <zone_name> <x_coord> <y_coord> [metadata]
hub: <zone_name> <x_coord> <y_coord> [metadata]
end_hub: <zone_name> <x_coord> <y_coord> [metadata]

connection: <zone1>-<zone2> [metadata]
```

### Zone Metadata Options

- **`zonetype`**: Zone movement cost type
  - `normal` - Standard zone (1 turn movement cost, default)
  - `restricted` - 2-turn transit (drone must wait in connection for 1 turn, arrives next turn)
  - `priority` - Preferred routing (1 turn movement cost, prioritized in pathfinding tie-breaks)
  - `blocked` - Inaccessible zone (cannot be entered, breaks all paths through it)

- **`color`**: Visual representation color (optional, for display purposes)
  - Examples: `green`, `red`, `blue`, `orange`, `purple`, `cyan`

- **`max_drones`**: Maximum concurrent drones occupying zone simultaneously
  - Default: 1
  - Must be positive integer
  - Enforced at simulation runtime

### Connection Metadata Options

- **`max_link_capacity`**: Maximum concurrent drones traversing connection simultaneously
  - Default: 1
  - Must be positive integer
  - Bidirectional constraint (a-b and b-a use same capacity)

### File Format Rules

- **First line requirement**: Must contain `nb_drones: <positive_integer>`
- **Hub requirements**: Exactly one `start_hub:` and exactly one `end_hub:`
- **Zone names**: Alphanumeric characters only (no spaces, dashes, or special characters)
- **Coordinates**: Any valid integers (positive, negative, or zero allowed)
- **Comments**: Lines starting with `#` are ignored
- **Empty lines**: Permitted and ignored

### Example Map File

```
# Delivery network example
nb_drones: 3

start_hub: origin 0 0 [color=green max_drones=3]
hub: checkpoint_a 1 1 [color=blue zonetype=priority]
hub: checkpoint_b 2 1 [color=blue max_drones=2]
hub: restricted_zone 3 1 [color=orange zonetype=restricted]
hub: bypass 3 2 [color=yellow]
end_hub: destination 4 1 [color=red max_drones=3]

connection: origin-checkpoint_a [max_link_capacity=2]
connection: origin-bypass
connection: checkpoint_a-checkpoint_b
connection: checkpoint_b-restricted_zone
connection: bypass-restricted_zone
connection: restricted_zone-destination
connection: bypass-destination
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

### Detailed Algorithm Description

**Overall Strategy:**
The system employs a two-phase routing approach: first discovering all optimal paths using hybrid pathfinding, then executing a turn-by-turn simulation with capacity-aware move planning.

**Phase 1: Pathfinding - Discover Optimal Routes**

1. **Dijkstra's Algorithm (Single Shortest Path)**
   - **Purpose**: Establish baseline optimal cost from start to goal
   - **Movement Costs**: Normal=1, Restricted=2, Priority=1, Blocked=∞
   - **Time Complexity**: O((V + E) log V) with binary heap
   - **Space Complexity**: O(V)
   - **Output**: Single shortest path with minimum total cost

2. **Cost-Pruned Depth-First Search (All Optimal Paths)**
   - **Purpose**: Discover all alternative paths matching baseline optimal cost
   - **Process**:
     1. Start DFS from origin node
     2. Explore all neighbors recursively
     3. Calculate cumulative cost to current node
     4. **Prune**: Skip branch if current cost ≥ baseline cost
     5. **Backtrack**: Upon reaching dead-ends or pruned nodes
     6. **Record**: Save all complete paths reaching goal with cost = baseline
   - **Time Complexity**: O(V + E) per complete path found
   - **Space Complexity**: O(V) for recursion depth
   - **Benefit**: Prevents exponential explosion in dense graphs while guaranteeing optimality

3. **Multi-Drone Path Distribution**
   - **Strategy**: Round-robin assignment across discovered optimal paths
   - **Benefit**: Load balancing reduces zone congestion
   - **Effect**: Improves overall throughput and minimizes total turns

**Phase 2: Simulation - Turn-by-Turn Execution**

Per-turn execution cycle (executes until all drones delivered):

1. **Resolve Transit Phase**
   - Process drones in 2-turn restricted zone transit
   - Decrement transit counter
   - Move drone to destination when timer reaches 0
   - Automatically mark as delivered if destination is goal

2. **Calculate Current Occupancy**
   - Count drones in each zone (excluding those in transit)
   - Create occupancy dictionary: `{zone_name: drone_count}`

3. **Plan Moves Phase** (for each drone not yet delivered)
   - **Check Zone Capacity**: Next zone has available slots (current < max_drones)
   - **Check Connection Capacity**: Connection can accommodate drone (bidirectional frozenset check)
   - **Determine Movement Type**:
     - **Normal zone**: Direct movement, update occupancy immediately
     - **Restricted zone**: Enter transit state (2-turn process)
     - **Goal zone**: Mark drone as delivered
   - **Build move list** with all viable movements

4. **Execute Moves Phase**
   - Update drone positions
   - Update zone occupancy
   - Handle restricted zone entry (set in_transit=True, transit_counter=1)
   - Remove delivered drones from tracking

5. **Deadlock Detection Phase**
   - **Condition**: No movement occurred AND drones in transit exist
   - **Action**: Raise error (indicates unsolvable configuration)

**Constraint Enforcement:**

- **Zone Capacity**: Occupancy dictionary tracks per-zone drone count
- **Connection Bandwidth**: Frozenset {zone_a, zone_b} ensures bidirectional detection
- **Restricted Zones**: State machine with in_transit flag and transit_counter
- **Blocked Zones**: Excluded from get_neighbors() to prevent path generation

---

## Visual Representation

### Terminal Output Features

The simulation provides colored terminal output designed to enhance user understanding:

**Visual Elements:**
- **Zone Color Coding**: Each zone type displays in distinct color for instant recognition
- **Turn-by-Turn Logging**: Line-by-line drone movement display showing progression
- **Structured Format**: Consistent `D<id>-<zone>` format enables easy parsing
- **Status Indicators**: Delivery progress visible through turn count

**Color Scheme (ANSI Terminal Colors):**
- **Green**: Start hub (delivery origin, sender location)
- **Red**: End hub (delivery destination, goal location)
- **Blue**: Normal zones (standard routing nodes)
- **Orange**: Restricted zones (2-turn transit zones, require planning)
- **Purple**: Priority zones (preferred routing nodes)
- **Cyan**: High-capacity zones (max_drones > 1, bottleneck potential)

**User Experience Benefits:**

1. **Visual Feedback at a Glance**
   - Users instantly identify zone types without reading metadata
   - Color-based pattern recognition speeds route understanding
   - Bottleneck zones (high capacity) visually stand out

2. **Easy Output Parsing**
   - Structured format (D<id>-<zone>) supports automated log analysis
   - Each turn on separate line enables incremental processing
   - Compatible with downstream tools and data visualization

3. **Progress Tracking**
   - Turn counter shows simulation advancement
   - Delivery events (D<id>-goal) indicate completion
   - Output length correlates to solution efficiency

4. **Error Clarity**
   - Parsing errors include line numbers for quick debugging
   - Validation errors specify constraint violation and location
   - Clear messages facilitate map file correction

### Example Output with Explanation

```
Turn 1: D0-zone_a D1-zone_a D2-zone_b
        (Drone 0,1 move to zone_a; Drone 2 moves to zone_b)

Turn 2: D0-zone_b D1-zone_b D2-zone_c
        (All drones progress along their paths)

Turn 3: D0-zone_c D1-zone_c D2-goal
        (Drone 2 reaches destination and is delivered)

Turn 4: D0-goal D1-goal
        (Final drones reach destination and are delivered)
```

Color-coded output helps users trace paths visually and understand network topology.

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
├── easy_1_linear.txt      # Test case: linear path, 2 drones
├── easy_2_fork.txt        # Test case: forked paths, 3 drones
├── easy_3_capacity.txt    # Test case: capacity constraints, 4 drones
└── map.txt                # Medium complexity example network
```

---

## Performance Benchmarks

### Test Results

| Map | Drones | Zones | Constraints | Target | Expected | Status |
|-----|--------|-------|-------------|--------|----------|--------|
| easy_1_linear | 2 | 7 | Sequential | ≤ 6 | 6 | ✅ |
| easy_2_fork | 3 | 8 | Path choice | ≤ 6 | 5 | ✅ |
| easy_3_capacity | 4 | 7 | Zone/Link capacity | ≤ 8 | 7 | ✅ |

### Algorithm Complexity Analysis

**Pathfinding Phase:**
- Dijkstra's Algorithm: O((V + E) log V)
- Cost-Pruned DFS: O(V + E) per path × P paths discovered
- Overall: Polynomial time, practical for maps with < 100 zones

**Simulation Phase:**
- Per-turn complexity: O(D × Z) where D = drones, Z = zones
- Total turns: T (proportional to path length and capacity constraints)
- Overall: O(T × D × Z)

**Space Complexity:**
- Graph storage: O(V + E)
- Pathfinding state: O(V)
- Simulation state: O(D + Z)
- Total: O(V + E + D + Z)

---

## Subject Compliance Checklist

**Section VII - Mandatory Requirements:**

✅ **VII.1** - Pathfinding: Dijkstra's algorithm + cost-pruned DFS  
✅ **VII.2** - Zone Occupancy: Capacity constraints enforced per zone  
✅ **VII.3** - Movement Mechanics: Correct turn costs (normal=1, restricted=2, priority=1)  
✅ **VII.4** - Parser: Comprehensive validation per specification  
✅ **VII.5** - Output Format: Turn-by-turn drone movements  
✅ **VII.6** - Scoring System: Minimizes total simulation turns  
✅ **VII.7** - Benchmarks: All easy maps pass targets  

**Section VIII - Documentation:**

✅ README.md with all required sections  
✅ Type hints on all functions and methods  
✅ PEP 257 docstrings throughout codebase  
✅ Flake8 code style compliance  
✅ Mypy static type checking pass  
✅ Algorithm explanation with complexity analysis  
✅ Visual representation documentation  

---

**Student:** moamhouc  
**School:** 42 Paris  
**Project:** Fly-in - Autonomous Drone Delivery Routing System
