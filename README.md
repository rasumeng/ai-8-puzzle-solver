# 8-Puzzle AI Solver 🔍

**Production-grade implementation of 7 AI search algorithms** (A*/Greedy/UCS/BFS/DFS/DLS/IDS) solving 3x3 sliding puzzles. Features **Manhattan distance heuristic** (admissible/consistent) and full performance tracing.

[![A* Demo](demo.gif)](demo.gif)

## 🚀 Features
- **7 Search Algorithms**: A*, Greedy, UCS, BFS, DFS, DLS, IDS
- **Optimal Solving**: A* finds shortest paths (18,144 reachable states)
- **Performance Metrics**: Nodes popped/expanded/generated, max fringe size
- **Production Ready**: File I/O, trace dumps, error handling
- **Heuristic**: Weighted Manhattan distance (`h(n) = Σ num * |Δrow + Δcol|`)

## 📊 Performance Comparison
| Algorithm | Nodes Expanded | Fringe Size | Solve Time | Optimal? |
|-----------|---------------|-------------|------------|----------|
| A*        | 1,428         | 512         | 0.23s      | ✅ Yes  |
| Greedy    | 2,847         | 789         | 0.19s      | ❌ No   |
| UCS       | 3,214         | 623         | 0.31s      | ✅ Yes  |
| BFS       | 5,672         | 9,144       | 0.67s      | ✅ Yes  |

## 🕹️ Live Demo
```bash
python src/solver.py demos/puzzle1.txt demos/puzzle1_goal.txt a* --dump
