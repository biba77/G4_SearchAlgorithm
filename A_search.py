# A* search implementation for the Kiwiberry Picking Problem

"""
Uses: 
- Farm from farm_layout.py
- State from state.py
- step costs from State.successors() 
- heuristic from heuristic.h_combined

This module implements the A* search algorithm to find the optimal path for the Kiwiberry Picking Problem.
- Uses a priority queue (heapq) to explore states based on f(n) = g(n) + h(n)
- Respects capacity, harvesting, and unloading rules via State.successors()
"""

from __future__ import annotations

import heapq
from typing import Callable, Dict, List, Optional, Tuple, Any

from farm_layout import Farm
from state import State
from heuristic import h_combined

StateType = State
HeuristicFn = Callable[[StateType, Farm], float]

# Path Reconstruction
def reconstruct_path(
    came_from: Dict[StateType, Tuple[Optional[StateType], str, float]],
    current: StateType
) -> List[Tuple[str, StateType]]:
    """
    Reconstruct the path of (action, state) pairs from the start to 'current'.

    came_from maps:
        state -> (parent_state, action_taken_to_get_here, step_cost)
    """
    path: List[Tuple[str, StateType]] = []
    s: Optional[StateType] = current

    while s is not None and s in came_from:
        parent, action, _ = came_from[s]
        path.append((action, s))
        s = parent

    path.reverse()
    return path


# A* core algorithm

def a_search(
    farm: Farm,
    start_state: StateType,
    heuristic_fn: HeuristicFn = h_combined
) -> Tuple[Optional[StateType], List[Tuple[str, StateType]], float]:
    """
    Run A* search from start_state on the given farm.

    Returns:
        (goal_state, path, total_cost)

        - goal_state: the final State if a goal was found, else None
        - path: list of (action_string, State) from start to goal
        - total_cost: g(goal), or float("inf") if no solution
    """

    # g_score: best known cost from start to each state
    g_score: Dict[StateType, float] = {start_state: 0.0}

    # open list as a heap of (f, tie_breaker, State)
    open_heap: List[Tuple[float, int, StateType]] = []
    counter = 0

    # initial node
    h0 = heuristic_fn(start_state, farm)
    heapq.heappush(open_heap, (h0, counter, start_state))

    # parent mapping: state -> (parent_state, action, step_cost)
    came_from: Dict[StateType, Tuple[Optional[StateType], str, float]] = {
        start_state: (None, "START", 0.0)
    }

    while open_heap:
        f_current, _, current = heapq.heappop(open_heap)
        current_g = g_score[current]

        # Goal test: uses State.is_goal(farm)
        if current.is_goal(farm):
            path = reconstruct_path(came_from, current)
            return current, path, current_g

        # Expand successors
        for action, next_state, step_cost in current.successors(farm):
            tentative_g = current_g + step_cost

            # If we already have a better path to this state, skip
            if next_state in g_score and tentative_g >= g_score[next_state]:
                continue

            # Record the better path
            g_score[next_state] = tentative_g
            came_from[next_state] = (current, action, step_cost)

            h = heuristic_fn(next_state, farm)
            f_next = tentative_g + h
            counter += 1
            heapq.heappush(open_heap, (f_next, counter, next_state))

    # No solution found
    return None, [], float("inf")

# Convenience solve() function to run A* and print results

def solve() -> None:
    #Build the farm, run A*, and print the resulting route and cost.
    farm = Farm(radius=4)
    start_state = State(position=farm.start)

    goal_state, path, total_cost = a_search(farm, start_state, heuristic_fn=h_combined)

    if goal_state is None:
        print("No solution found.")
        return

    # Compute how many harvestable cells exist in total
    harvestable = {pos for pos in farm.all_cells() if farm.get_weight(pos) > 0}

    print("=== A* Solution for Kiwiberry Picking ===")
    print(f"Start position: {start_state.position}")
    print(f"Total movement cost: {total_cost}")
    print(f"Number of steps in path: {len(path)}")
    print(f"Harvested cells: {len(goal_state.harvested)} / {len(harvestable)}")
    print()

    # Skip the artificial "START" action in output if present
    for i, (action, state) in enumerate(path, start=1):
        if action == "START":
            # Initial state, nothing to print as a move
            continue
        print(f"Step {i:02d}: {action} -> {state}")

    print()
    print("Goal state reached (summary):")
    print(goal_state.as_dict())


if __name__ == "__main__":
    solve()
