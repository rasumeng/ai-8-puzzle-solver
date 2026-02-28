# 8-Puzzle AI Solver

**Production-grade implementation of 7 AI search algorithms** (A*/Greedy/UCS/BFS/DFS/DLS/IDS) solving 3×3 sliding puzzles. Demonstrates why **A* is 95× more efficient than uninformed search** while maintaining optimal solutions.

## Overview

The 8-puzzle is a classic AI search problem where a 3×3 grid contains tiles numbered 1–8 plus one blank space. The goal is to rearrange tiles from a start configuration to a target configuration using valid moves (sliding adjacent tiles into the blank space).

This implementation compares 7 different search strategies with real performance benchmarks. Real test results show A* explores only 64 nodes to reach an optimal solution, while uninformed search methods require thousands of node expansions.

## Features

- **7 Search Algorithms Implemented**
  - **A* Search**: Optimal with consistent heuristic
  - **Greedy Best-First**: Fast but not guaranteed optimal
  - **Uniform Cost Search (UCS)**: Optimal for uniform-cost domains
  - **Breadth-First Search (BFS)**: Optimal but memory-intensive
  - **Depth-First Search (DFS)**: Low memory, can find solutions quickly
  - **Depth-Limited Search (DLS)**: DFS with depth constraint
  - **Iterative Deepening (IDS)**: Optimal without excessive memory

- **Advanced Heuristics**
  - Weighted Manhattan distance: `h(n) = Σ(tile_number × Manhattan_distance)`
  - Admissible: Never overestimates actual cost
  - Consistent: Monotonic property ensures optimal paths

- **Performance Analysis**
  - Tracks nodes popped, nodes expanded, nodes generated
  - Records maximum fringe size during search
  - Execution time measurement
  - Full trace dumps for algorithm analysis

- **Production Ready**
  - File-based I/O for start/goal states
  - Configurable search methods and parameters
  - Error handling and input validation
  - Trace output for debugging

## Performance Comparison

Real benchmark results on moderate difficulty puzzle (12 moves to solution):

| Algorithm | Nodes Expanded | Max Fringe | Path Cost | Optimal? |
|-----------|---|---|---|---|
| A*        | 64             | 77        | 63        | ✅ Yes   |
| Greedy    | 138            | 108       | 191       | ❌ No    |
| UCS       | 6,068          | 5,835     | 63        | ✅ Yes   |
| BFS       | 2,331          | 1,284     | 63        | ✅ Yes   |
| DLS (d=15)| 513,047        | 39        | 69        | ❌ No    |
| IDS       | 291,369        | 31        | 63        | ✅ Yes   |

**Key Findings:**
- **A* is 95x more efficient than UCS** (64 vs 6,068 nodes) while finding optimal solutions
- **A* is 36x more efficient than BFS** (64 vs 2,331 nodes)
- **Greedy finds suboptimal solutions** (cost 191 vs optimal 63)
- **DLS explores more nodes** than IDS due to suboptimal path
- **IDS guarantees optimality** with reasonable node expansion

## Usage

### Basic Usage

```bash
python expense_8_puzzle.py <start_file> <goal_file> <method> [--dump]
```

### Parameters

- `<start_file>`: Text file containing start puzzle state (3×3 grid with numbers 1–8 and 0 for blank)
- `<goal_file>`: Text file containing goal puzzle state
- `<method>`: Search algorithm (a*, greedy, ucs, bfs, dfs, dls, ids)
- `--dump`: Optional flag to output trace information

### Example Input Files

**start.txt:**
```
1 2 3
4 0 5
7 8 6
END
```

**goal.txt:**
```
1 2 3
4 5 6
7 8 0
END
```

### Running the Solver

```bash
# Run A* search
python expense_8_puzzle.py start.txt goal.txt a*

# Run with trace dump
python expense_8_puzzle.py start.txt goal.txt a* --dump

# Run depth-limited search with custom depth
python expense_8_puzzle.py start.txt goal.txt dls
# (prompts for depth limit)

# Run iterative deepening
python expense_8_puzzle.py start.txt goal.txt ids
```

## Algorithm Details

### State Space
- **Total states**: 9! = 362,880
- **Reachable states**: 181,440 (due to parity constraints)
- **Goal**: Find optimal path from start to goal configuration

### Manhattan Distance Heuristic

The heuristic function calculates the weighted Manhattan distance:

```
h(n) = Σ(tile_number × (|current_row - goal_row| + |current_col - goal_col|))
```

This weights each tile by its number, providing a more informed estimate than simple tile displacement counting.

**Properties**:
- **Admissible**: Never overestimates true cost
- **Consistent**: Maintains h(n) ≤ cost(n→n') + h(n')
- **Effective**: Guides search efficiently toward goal

### Key Insights

- **A* vs UCS**: A* expands 95x fewer nodes (64 vs 6,068) by using heuristic guidance
- **A* vs BFS**: A* is 36x more efficient (64 vs 2,331 nodes) showing power of informed search
- **A* vs Greedy**: A* finds optimal path (cost 63) while Greedy gets stuck (cost 191)
- **IDS vs DLS**: IDS finds optimal solution while DLS with arbitrary depth limit doesn't
- **Memory Trade-off**: DLS uses minimal fringe (39) but explores many more nodes

## Technical Implementation

### Core Components

1. **Node Class**: Represents states in search tree with parent pointers for path reconstruction
2. **State Representation**: Tuples for immutability and efficient hashing in visited sets
3. **Successors Function**: Generates valid moves by swapping blank with adjacent tiles
4. **Priority Queues**: Heaps for efficient frontier management in A* and Greedy

### Data Structures

- **Visited Set**: Prevents cycles and redundant exploration
- **Fringe (Priority Queue)**: Orders nodes by g(n) + h(n) for A*, or h(n) for Greedy
- **Parent Pointers**: Enable solution path reconstruction

## Installation

No external dependencies required—uses only Python standard library:
- `collections.deque` for queue operations
- `heapq` for priority queues
- `itertools` for counter functionality

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-8-puzzle-solver.git
cd ai-8-puzzle-solver

# Quick test with included moderate difficulty puzzle
python expense_8_puzzle.py test_start.txt test_goal.txt a*

# Compare algorithms on same puzzle
python expense_8_puzzle.py test_start.txt test_goal.txt greedy
python expense_8_puzzle.py test_start.txt test_goal.txt bfs
```

## Example Output

```
$ python expense_8_puzzle.py test_start.txt test_goal.txt a*

Nodes Popped: 97
Nodes Expanded: 64
Nodes Generated: 173
Max Fringe Size: 77
Solution Found at depth 12 with cost of 63.
Steps:
        Move 7 Left
        Move 5 Up
        Move 8 Right
        Move 7 Down
        Move 5 Left
        Move 6 Down
        Move 3 Right
        Move 2 Right
        Move 1 Up
        Move 4 Up
        Move 7 Left
        Move 8 Left
```

**Comparison with other methods on same puzzle:**
- Greedy: 138 nodes expanded, but finds suboptimal path (cost 191 vs optimal 63)
- BFS: 2,331 nodes expanded to find same solution
- UCS: 6,068 nodes expanded without heuristic guidance

## Project Structure

```
ai-8-puzzle-solver/
├── expense_8_puzzle.py    # Main solver implementation
├── README.md              # This file
├── requirements.txt       # Python dependencies
└── .gitignore             # Git exclusions
```

## Algorithm Comparison

### A* Search (Optimal + Efficient) ⭐ Recommended
- Combines actual cost `g(n)` with heuristic estimate `h(n)`
- Expands nodes in order of `f(n) = g(n) + h(n)`
- Optimal when heuristic is admissible
- **Best choice for this problem**

### Greedy Best-First (Fast but Suboptimal)
- Expands nodes purely by heuristic estimate `h(n)`
- Very fast but may not find shortest path
- Useful when speed matters more than optimality

### Uniform Cost Search (Optimal but Uninformed)
- Explores nodes by path cost `g(n)` alone
- Guarantees optimal solution
- Slower than A* because ignores domain knowledge

### Breadth-First Search (Optimal but Memory-Intensive)
- Explores all nodes at depth d before depth d+1
- Guarantees shortest path
- Requires exponential memory

### Iterative Deepening (Optimal + Memory Efficient)
- Performs repeated DFS with increasing depth limits
- Combines benefits of DFS (low memory) and BFS (optimality)
- Minimal overhead compared to BFS

## Learning Outcomes

This project demonstrates:
- ✅ Heuristic search algorithm design
- ✅ Data structure optimization (heaps, queues, sets)
- ✅ Algorithm performance analysis and comparison
- ✅ Clean code organization and documentation
- ✅ Problem-solving using AI search techniques

## License

MIT License - feel free to use for educational purposes.

## Author

Robert Asumeng
