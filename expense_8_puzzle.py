# 8-Puzzle AI Solver
# Author: Robert Asumeng
# Description: Production-grade implementation of 7 AI search algorithms
#              (A*, Greedy, UCS, BFS, DFS, DLS, IDS) for solving 3x3 sliding puzzles
#              with weighted Manhattan distance heuristic

from collections import deque
import heapq
from itertools import count
from datetime import datetime
import sys


# Algorithm configurations and validation
ALLOWED_METHODS = {"bfs", "ucs", "greedy", "a*", "dfs", "dls", "ids"}
EC_METHODS = {"dfs", "dls", "ids"}  # Exponential Complexity methods (tree search)
DUMP_FLAGS = {"-d", "--dump", "true", "1", "yes"}

def make_problem(start_file, goal_file):
    """
    Load puzzle configuration from files.
    
    Reads start and goal puzzle states from text files. Each file should contain
    a 3x3 grid of numbers (1-8 and 0 for blank space) followed by 'END'.
    
    Args:
        start_file (str): Path to file containing start puzzle configuration
        goal_file (str): Path to file containing goal puzzle configuration
    
    Returns:
        tuple: (start_state, goal_state) where each state is a tuple of 9 integers
    
    Example:
        start_state = (1, 2, 3, 4, 0, 5, 7, 8, 6)
        goal_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    """
    start = []
    goal = []

    with open(start_file, "r") as file:
        for line in file:
            if "END" in line:
                break
            nums = list(map(int, line.split()))
            start.extend(nums)

    with open(goal_file, "r") as file:
        for line in file:
            if "END" in line:
                break
            nums = list(map(int, line.split()))
            goal.extend(nums)

    return tuple(start), tuple(goal)
    
class Node:
    """
    Represents a state node in the search tree.
    
    Attributes:
        state (tuple): The puzzle configuration (e.g., (1,2,3,4,0,5,7,8,6))
        parent (Node): Reference to parent node for path reconstruction
        move (tuple): The move that generated this node (tile_number, direction)
        cost (int): Accumulated path cost from start to this node (g(n))
    """
    def __init__(self, state, parent=None, move=None, cost=0):
        self.state = state
        self.parent = parent
        self.move = move
        self.cost = cost

def mh_dis(state, goal):
    """
    Calculate weighted Manhattan distance heuristic.
    
    Computes h(n) = Σ(tile_number × Manhattan_distance_to_goal)
    
    This heuristic is:
    - Admissible: Never overestimates actual cost
    - Consistent: Maintains h(n) <= cost(n->n') + h(n')
    
    Args:
        state (tuple): Current puzzle configuration
        goal (tuple): Goal puzzle configuration
    
    Returns:
        int: Estimated cost to reach goal from this state
    """
    distance = 0
    for num in range(1, 9):
        current_index = state.index(num)
        goal_index = goal.index(num)
        current_row, current_col = current_index // 3, current_index % 3
        goal_row, goal_col = goal_index // 3, goal_index % 3
        # Weight each tile by its number for more informed heuristic
        distance += num * (abs(current_row - goal_row) + abs(current_col - goal_col))
    return distance

def successors(state):
    """
    Generate all valid next states from current state.
    
    Finds the blank (0), determines valid moves (up/down/left/right),
    and returns all reachable states.
    
    Args:
        state (tuple): Current puzzle configuration
    
    Returns:
        list: Each element is (next_state, (tile_moved, direction), move_cost)
    """
    next_states = []
    zero = state.index(0)
    row, col = zero // 3, zero % 3

    # Define possible moves based on blank position
    moves = []
    if row > 0:
        moves.append((-3, "Up"))
    if row < 2:
        moves.append((3, "Down"))
    if col > 0:
        moves.append((-1, "Left"))
    if col < 2:
        moves.append((1, "Right"))

    for delta, move in moves:
        new_index = zero + delta
        moved_tile = state[new_index]
        # Reverse direction (moving tile up means blank moves down)
        tile_move = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}[move]
        new_state = list(state)
        new_state[zero], new_state[new_index] = new_state[new_index], new_state[zero]
        next_states.append((tuple(new_state), (moved_tile, tile_move), moved_tile))

    return next_states

def tree_search(problem, method, trace_file=None, cmd_args=None):
    """
    Tree search implementation for DFS, DLS, and IDS methods.
    
    Explores search space without tracking visited states (causes revisits).
    Suitable for methods that have inherent depth limitations (DFS, DLS, IDS).
    
    Args:
        problem (tuple): (start_state, goal_state)
        method (str): Search method ('dfs', 'dls', or 'ids')
        trace_file: Optional file handle for writing search trace
        cmd_args: Command line arguments for trace documentation
    
    Returns:
        tuple: (goal_node, stats_dict) or (None, stats_dict) if no solution
    """
    start_state, goal_state = problem[0], problem[1]

    depth_limit = None
    if method == "dls":
        depth_limit = int(input("Enter depth limit for DLS: "))

    # IDS tries increasing depth limits; others use single limit
    limits_to_try = [depth_limit] if method in {"dfs", "dls"} else range(0, 1000)

    overall_nodes_popped = 0
    overall_nodes_expanded = 0
    overall_nodes_generated = 0
    overall_max_fringe_size = 0

    for current_limit in limits_to_try:
        start_node = Node(start_state, None, None, 0)
        fringe = [start_node]

        nodes_popped = 0
        nodes_expanded = 0
        nodes_generated = 1
        max_fringe_size = 1

        if trace_file is not None:
            method_label = method if method != "ids" else f"ids(limit={current_limit})"
            write_trace_header(
                trace_file,
                cmd_args,
                method_label,
                goal_state,
                fringe,
                nodes_popped,
                nodes_expanded,
                nodes_generated,
                max_fringe_size,
            )

        while fringe:
            node = fringe.pop()  # DFS: pop from end (LIFO)
            nodes_popped += 1

            if node.state == goal_state:
                overall_nodes_popped += nodes_popped
                overall_nodes_expanded += nodes_expanded
                overall_nodes_generated += nodes_generated
                overall_max_fringe_size = max(overall_max_fringe_size, max_fringe_size)
                return node, make_stats(
                    overall_nodes_popped,
                    overall_nodes_expanded,
                    overall_nodes_generated,
                    overall_max_fringe_size,
                )

            depth = node_depth(node)
            # Prune nodes exceeding depth limit
            if method in {"dls", "ids"} and depth >= current_limit:
                continue

            nodes_expanded += 1
            children = []
            successors_generated = 0
            if trace_file is not None:
                trace_file.write(f"Generating successors to {format_node(node, method, goal_state)}:\n")

            for child_state, child_move, move_cost in successors(node.state):
                child_node = Node(child_state, parent=node, move=child_move, cost=node.cost + move_cost)
                children.append(child_node)
                successors_generated += 1
                nodes_generated += 1

            for child_node in reversed(children):
                fringe.append(child_node)

            if len(fringe) > max_fringe_size:
                max_fringe_size = len(fringe)

            if trace_file is not None:
                trace_file.write(f"\t{successors_generated} successors generated\n")
                method_label = method if method != "ids" else f"ids(limit={current_limit})"
                write_trace_snapshot(
                    trace_file,
                    method_label,
                    goal_state,
                    fringe,
                    [],
                    nodes_popped,
                    nodes_expanded,
                    nodes_generated,
                    max_fringe_size,
                )

        overall_nodes_popped += nodes_popped
        overall_nodes_expanded += nodes_expanded
        overall_nodes_generated += nodes_generated
        overall_max_fringe_size = max(overall_max_fringe_size, max_fringe_size)

        if method in {"dfs", "dls"}:
            break

    return None, make_stats(
        overall_nodes_popped,
        overall_nodes_expanded,
        overall_nodes_generated,
        overall_max_fringe_size,
    )


def make_stats(nodes_popped, nodes_expanded, nodes_generated, max_fringe_size):
    """Create statistics dictionary for search results."""
    return {
        "nodes_popped": nodes_popped,
        "nodes_expanded": nodes_expanded,
        "nodes_generated": nodes_generated,
        "max_fringe_size": max_fringe_size,
    }


def format_state_grid(state):
    """Convert state tuple into 3x3 grid for display."""
    return [list(state[0:3]), list(state[3:6]), list(state[6:9])]


def node_depth(node):
    """
    Calculate depth of node in search tree.
    
    Counts steps from root by traversing parent pointers.
    
    Args:
        node (Node): Node to calculate depth for
    
    Returns:
        int: Distance from root node (0 for root)
    """
    depth = 0
    current = node
    while current.parent is not None:
        depth += 1
        current = current.parent
    return depth


def node_priority(node, method, goal_state):
    """
    Calculate node priority based on search method.
    
    Different algorithms prioritize nodes differently:
    - UCS: g(n) = path cost
    - Greedy: h(n) = heuristic estimate
    - BFS: depth
    - A*: f(n) = g(n) + h(n)
    
    Args:
        node (Node): Node to evaluate
        method (str): Search method name
        goal_state (tuple): Goal configuration
    
    Returns:
        int: Priority value (lower = better)
    """
    g = node.cost
    h = mh_dis(node.state, goal_state)
    if method == "ucs":
        return g
    if method == "greedy":
        return h
    if method == "bfs":
        return node_depth(node)
    return g + h  # A* formula


def format_node(node, method, goal_state):
    """Format node information for trace output."""
    state_grid = format_state_grid(node.state)
    if node.move is None:
        action = "Start"
    else:
        moved_tile, direction = node.move
        action = f"Move {moved_tile} {direction}"

    g = node.cost
    d = node_depth(node)
    f = node_priority(node, method, goal_state)

    if node.parent is None:
        parent_text = "Pointer to {None}"
    else:
        parent_text = f"Pointer to {{{format_state_grid(node.parent.state)}}}"

    return f"< state = {state_grid}, action = {{{action}}} g(n) = {g}, d = {d}, f(n) = {f}, Parent = {parent_text} >"


def format_fringe(fringe, method, goal_state):
    """Format fringe contents for trace output."""
    if method == "bfs":
        nodes = list(fringe)
    elif fringe and isinstance(fringe[0], tuple):
        nodes = [entry[2] for entry in fringe]
    else:
        nodes = list(fringe)

    lines = ["\tFringe: ["]
    for node in nodes:
        lines.append(f"\t\t{format_node(node, method, goal_state)}")
    lines.append("\t]")
    return "\n".join(lines)


def format_closed(closed_nodes):
    """Format closed set for trace output."""
    closed_states = [format_state_grid(state) for state in closed_nodes]
    return f"\tClosed: {closed_states}"


def write_trace_snapshot(trace_file, method, goal_state, fringe, closed_view, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size):
    """Write current search state snapshot to trace file."""
    if trace_file is None:
        return

    trace_file.write(format_closed(closed_view) + "\n")
    trace_file.write(format_fringe(fringe, method, goal_state) + "\n")
    trace_file.write(f"\tNodes Popped: {nodes_popped}\n")
    trace_file.write(f"\tNodes Expanded: {nodes_expanded}\n")
    trace_file.write(f"\tNodes Generated: {nodes_generated}\n")
    trace_file.write(f"\tMax Fringe Size: {max_fringe_size}\n")
    trace_file.write("-" * 60 + "\n")


def write_trace_header(trace_file, cmd_args, method, goal_state, fringe, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size):
    """Write trace file header with initial state."""
    if trace_file is None:
        return
    trace_file.write(f"Command-Line Arguments: {cmd_args or []}\n")
    trace_file.write("After Initialization\n")
    write_trace_snapshot(trace_file, method, goal_state, fringe, [], nodes_popped, nodes_expanded, nodes_generated, max_fringe_size)
    trace_file.write(f"Running {method}\n")


def graph_search(problem, method, trace_file=None, cmd_args=None):
    """
    Graph search implementation for BFS, A*, Greedy, and UCS methods.
    
    Maintains visited set to prevent revisiting states. Implements multiple
    search strategies through different fringe orderings.
    
    Args:
        problem (tuple): (start_state, goal_state)
        method (str): Search method ('bfs', 'a*', 'greedy', or 'ucs')
        trace_file: Optional file handle for writing search trace
        cmd_args: Command line arguments for trace documentation
    
    Returns:
        tuple: (goal_node, stats_dict) or (None, stats_dict) if no solution
    """
    start_state, goal_state = problem[0], problem[1]

    start_node = Node(start_state, None, None, 0)
    nodes_popped = 0
    nodes_expanded = 0
    nodes_generated = 1

    # BFS uses queue (FIFO) with explicit visited set
    if method == "bfs":
        fringe = deque([start_node])
        visited = {start_state}
        max_fringe_size = 1
        write_trace_header(
            trace_file,
            cmd_args,
            method,
            goal_state,
            fringe,
            nodes_popped,
            nodes_expanded,
            nodes_generated,
            max_fringe_size,
        )

        while fringe:
            node = fringe.popleft()  # FIFO: breadth-first
            nodes_popped += 1

            if node.state == goal_state:
                return node, make_stats(nodes_popped, nodes_expanded, nodes_generated, max_fringe_size)

            nodes_expanded += 1
            successors_generated = 0
            if trace_file is not None:
                trace_file.write(f"Generating successors to {format_node(node, method, goal_state)}:\n")

            for child_state, child_move, move_cost in successors(node.state):
                if child_state in visited:
                    continue

                visited.add(child_state)
                child_node = Node(child_state, parent=node, move=child_move, cost=node.cost + move_cost)
                fringe.append(child_node)
                successors_generated += 1
                nodes_generated += 1
                if len(fringe) > max_fringe_size:
                    max_fringe_size = len(fringe)

            if trace_file is not None:
                trace_file.write(f"\t{successors_generated} successors generated\n")
                write_trace_snapshot(trace_file, method, goal_state, fringe, visited, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size)

        return None, make_stats(nodes_popped, nodes_expanded, nodes_generated, max_fringe_size)

    # A*, Greedy, and UCS use priority queue (heap)
    sequence = count()  # Tie-breaker for heap stability
    fringe = []
    closed = set()

    start_h = mh_dis(start_state, goal_state)
    start_priority = 0 if method == "ucs" else start_h

    heapq.heappush(fringe, (start_priority, next(sequence), start_node))
    max_fringe_size = 1
    write_trace_header(trace_file, cmd_args, method, goal_state, fringe, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size)

    while fringe:
        _, _, node = heapq.heappop(fringe)
        nodes_popped += 1

        if node.state in closed:
            continue
        closed.add(node.state)

        if node.state == goal_state:
            return node, make_stats(nodes_popped, nodes_expanded, nodes_generated, max_fringe_size)

        nodes_expanded += 1
        successors_generated = 0
        if trace_file is not None:
            trace_file.write(f"Generating successors to {format_node(node, method, goal_state)}:\n")

        for child_state, child_move, move_cost in successors(node.state):
            new_g = node.cost + move_cost
            child_node = Node(child_state, parent=node, move=child_move, cost=new_g)

            h = mh_dis(child_state, goal_state)
            if method == "ucs":
                priority = new_g
            elif method == "greedy":
                priority = h
            else:  # A*
                priority = new_g + h

            heapq.heappush(fringe, (priority, next(sequence), child_node))
            successors_generated += 1
            nodes_generated += 1
            if len(fringe) > max_fringe_size:
                max_fringe_size = len(fringe)

        if trace_file is not None:
            trace_file.write(f"\t{successors_generated} successors generated\n")
            write_trace_snapshot(trace_file, method, goal_state, fringe, closed, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size)

    return None, make_stats(nodes_popped, nodes_expanded, nodes_generated, max_fringe_size)


def build_path(goal_node):
    """
    Reconstruct solution path from goal node to start.
    
    Traces parent pointers backwards and reverses to get start -> goal order.
    
    Args:
        goal_node (Node): The goal node found by search
    
    Returns:
        list: Sequence of (move, state) pairs from start to goal
    """
    if goal_node is None:
        return []

    path = []
    current = goal_node
    while current is not None:
        path.append((current.move, current.state))
        current = current.parent

    path.reverse()
    return path



if __name__ == "__main__":
    """
    Main execution block - Entry point for 8-Puzzle solver.
    
    ALGORITHM SELECTION:
    ====================
    - Tree Search (DFS, DLS, IDS): Used for depth-limited algorithms without visited set
    - Graph Search (BFS, A*, Greedy, UCS): Maintains visited set to prevent cycles
    
    KEY DESIGN DECISIONS:
    =====================
    1. State Representation: Tuples (immutable, hashable) for O(1) visited set lookups
    
    2. Heuristic Function: Weighted Manhattan Distance
       h(n) = Σ(tile_number × distance_to_goal)
       - Admissible: Never overestimates actual cost
       - Consistent: Satisfies triangle inequality for monotonicity
       - More informative than simple tile displacement
    
    3. Data Structures:
       - Node class with parent pointers for path reconstruction
       - Heap (heapq) for priority queues in A*, Greedy, UCS
       - Deque for BFS queue
       - Set for visited states in graph search
    
    4. Priority Calculation:
       - A*: f(n) = g(n) + h(n) = actual_cost + estimated_remaining
       - Greedy: f(n) = h(n) = estimated_remaining only
       - UCS: f(n) = g(n) = actual_cost only
       - BFS: f(n) = depth (FIFO queue)
    
    PERFORMANCE CHARACTERISTICS:
    ============================
    A* is optimal and efficient because it:
    - Expands fewer nodes than Greedy (considers actual cost)
    - Reaches goal faster than UCS (uses heuristic)
    - Uses less memory than BFS (guided by heuristic)
    
    IDS combines benefits of DFS (low memory) and BFS (optimality) through
    iterative deepening with increasing depth limits.
    
    COMPLEXITY ANALYSIS:
    ====================
    Time: O(b^d) where b = branching factor (max 4), d = solution depth
    Space: 
    - DFS/DLS: O(b×d) stack depth
    - BFS: O(b^d) fringe size (worst case)
    - A*/Greedy/UCS: O(b^d) fringe + visited set
    """
    
    if len(sys.argv) < 3:
        print("Usage: python expense_8_puzzle.py <start-file> <goal-file> <method> <dump-flag>")
        sys.exit(1)

    start_file = sys.argv[1]
    goal_file = sys.argv[2]
    method = sys.argv[3].lower() if len(sys.argv) > 3 else "a*"
    if method not in ALLOWED_METHODS:
        method = "a*"

    dump_flag = False
    if len(sys.argv) > 4:
        dump_value = sys.argv[4].lower()
        dump_flag = dump_value in DUMP_FLAGS

    problem = make_problem(start_file, goal_file)

    trace_filename = None
    if dump_flag:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        trace_filename = f"trace-{timestamp}.txt"
        with open(trace_filename, "w") as trace_file:
            if method in EC_METHODS:
                goal_node, stats = tree_search(problem, method, trace_file, sys.argv[1:])
            else:
                goal_node, stats = graph_search(problem, method, trace_file, sys.argv[1:])
    else:
        if method in EC_METHODS:
            goal_node, stats = tree_search(problem, method)
        else:
            goal_node, stats = graph_search(problem, method)

    path = build_path(goal_node)

    print("Nodes Popped:", stats["nodes_popped"])
    print("Nodes Expanded:", stats["nodes_expanded"])
    print("Nodes Generated:", stats["nodes_generated"])
    print("Max Fringe Size:", stats["max_fringe_size"])

    if goal_node is None:
        print("No solution found.")
    else:
        print(f"Solution Found at depth {len(path) - 1} with cost of {goal_node.cost}.")
        print("Steps:")
        for move, state in path:
            if move is None:
                continue
            moved_tile, direction = move
            print(f"        Move {moved_tile} {direction}")

    if dump_flag and trace_filename is not None:
        print(f"Search trace written to {trace_filename}")