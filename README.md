# IASD — Berth Allocation Problem (BAP) Solver

A Python implementation of the **Berth Allocation Problem (BAP)** developed across three progressive assignments. The project explores classic AI search strategies to optimally schedule and assign vessels to berths in a port, minimising total weighted flow time.

---

## Overview

The Berth Allocation Problem involves scheduling a set of vessels arriving at a port, assigning each vessel a berth position and a mooring time, such that:

- No two vessels overlap in both time and berth space.
- Each vessel is moored no earlier than its arrival time.
- Each vessel fits within the available berth length.
- The total **weighted flow time** (cost) is minimised.

The solution is built on top of a provided `search.py` framework (based on AIMA) and progressively introduces more sophisticated search strategies across the three parts.

---

## Project Structure

```
IASD/
├── Parte 1/
│   ├── solution.py       # Cost calculation and constraint checking
│   ├── search.py         # Search framework (AIMA-based)
│   ├── utils.py          # Utility functions
│   └── Tests/            # Test cases (.dat input + .plan solution files)
│
├── Parte 2/
│   ├── solution.py       # Uniform Cost Search (UCS) solver
│   ├── search.py         # Search framework
│   ├── utils.py          # Utility functions
│   └── Tests/            # Test cases (.dat input files)
│
└── Parte 3/
    ├── solution.py       # A* Search solver with heuristic
    ├── search.py         # Search framework
    ├── utils.py          # Utility functions
    └── Tests/            # Test cases (.dat input files)
```

---

## Assignment Breakdown

### Parte 1 — Problem Modelling
Implements the core `BAProblem` class with:
- **`load(fh)`** — Parses a `.dat` file containing berth size and vessel data.
- **`load_sol(fhs)`** — Loads a pre-computed solution from a `.plan` file.
- **`cost(sol)`** — Computes total weighted flow time for a given solution.
- **`check(sol)`** — Validates that a solution satisfies all berth and time constraints.

### Parte 2 — Uniform Cost Search
Extends the model into a full search problem by defining:
- **`State`** — An immutable, hashable representation of the current vessel assignments.
- **`actions(state)`** — Generates all valid vessel placement actions from a given state.
- **`result(state, action)`** — Returns the new state after applying an action.
- **`goal_test(state)`** — Checks if all vessels have been assigned.
- **`path_cost(...)`** — Incrementally computes weighted flow time.
- **`solve()`** — Runs **Uniform Cost Search (UCS)** to find the optimal assignment.

### Parte 3 — A\* Search with Heuristic
Improves upon Parte 2 by replacing UCS with **A\* Search**, adding:
- **`heuristic(node)`** — An admissible heuristic that estimates the remaining cost by greedily placing each unscheduled vessel at its earliest possible time and berth.
- **`solve()`** — Runs `astar_search` using the custom heuristic for faster convergence.

---

## Input Format

Each `.dat` test file follows this structure:

```
# Optional comments
<berth_size> <num_vessels>
<arrival_time> <processing_time> <vessel_length> <weight>
...
```

Each line after the header describes one vessel with four integer values.

---

## Output Format

Solutions are lists of `[mooring_time, berth_index]` pairs — one per vessel — indicating when and where each vessel is assigned.

Example:
```python
[[2, 0], [0, 3], [5, 1]]
```

---

## Requirements

- Python 3.x
- `numpy`

Install dependencies:
```bash
pip install numpy
```

---

## Usage

Run any part's solver by executing its `solution.py` directly. Update the `input_file_path` variable inside `main()` to point to the desired test file:

```bash
cd "Parte 2"
python solution.py
```

```bash
cd "Parte 3"
python solution.py
```

---

## Key Concepts

| Concept | Description |
|---|---|
| Berth Allocation Problem | NP-hard scheduling optimisation problem in port logistics |
| Weighted Flow Time | Cost metric: sum of `weight × (mooring_time + processing_time − arrival_time)` per vessel |
| Uniform Cost Search | Explores states by lowest cumulative path cost |
| A\* Search | UCS enhanced with a heuristic to reduce the search space |
| Admissible Heuristic | Estimates remaining cost without overestimating, guaranteeing optimality |

---

## Author

**Tomás Marques** — [GitHub](https://github.com/TomasMarques175)
**Pedro Apolonia** — [GitHub](https://github.com/apolonia-p)
