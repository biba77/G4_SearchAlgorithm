# state.py
"""
Provides:
- State: immutable, hashable state representing Alex's position, basket contents, and harvested set.
- Movement validation and application: is_valid_move, move_to
- Automatic harvesting and unloading logic on entering a cell.
- successors(farm) for external search to expand states.

Design notes:
- State is immutable and safe to use as keys in dictionaries/sets (uses frozenset for harvested).
- Harvesting is *atomic* and only allowed if entire cell fits (no partial harvesting).
- Unloading (at collection stations) resets basket to (0kg, 0cm3) on arrival.
- move_to does NOT alter the Farm object; it returns a new State.
"""

from dataclasses import dataclass
from typing import Tuple, Iterable, List

Pos = Tuple[int, int]  # axial coordinates (q, r)


@dataclass(frozen=True)
class State:
    """
    Immutable state for search algorithms.

    Attributes
    ----------
    position : Pos
        Current cell coordinate (q, r).
    basket_load : Tuple[int, int]
        (weight_kg, volume_cm3)
    harvested : frozenset
        Set of positions that have already been harvested.
    """
    position: Pos
    basket_load: Tuple[int, int]  # (weight_kg, volume_cm3)
    harvested: frozenset

    def __init__(self, position: Pos, basket_load: Tuple[int, int] = (0, 0),
                 harvested: Iterable[Pos] = None):
        object.__setattr__(self, "position", position)
        object.__setattr__(self, "basket_load", tuple(basket_load))
        if harvested is None:
            object.__setattr__(self, "harvested", frozenset())
        else:
            object.__setattr__(self, "harvested", frozenset(harvested))

    # --- convenience properties ---
    @property
    def weight(self) -> int:
        return self.basket_load[0]

    @property
    def volume(self) -> int:
        return self.basket_load[1]

    # --- capacity & harvest checks ---
    def can_harvest_cell(self, farm, pos: Pos) -> bool:
        """
        Return True if:
          - pos is inside farm bounds,
          - pos contains harvestable fruit (weight > 0),
          - pos not already harvested in this State,
          - AND the full cell's weight and volume fit into the basket given current load.

        Partial harvesting is NOT supported by this implementation.
        """
        if not farm.in_bounds(pos):
            return False
        w = farm.get_weight(pos)
        v = farm.get_volume(pos)
        if w <= 0:
            return False
        if pos in self.harvested:
            return False
        # If already at or beyond max weight, disallow harvesting until unload
        if self.weight >= farm.max_weight:
            return False
        remaining_w = farm.max_weight - self.weight
        remaining_v = farm.max_volume - self.volume
        return (w <= remaining_w) and (v <= remaining_v)

    def with_harvested(self, pos: Pos, farm):
        """
        Return a new State with pos harvested and basket updated.
        Precondition: can_harvest_cell(farm, pos) is True.
        """
        if not self.can_harvest_cell(farm, pos):
            raise ValueError("Cannot harvest: not harvestable or exceeds capacity.")
        w = farm.get_weight(pos)
        v = farm.get_volume(pos)
        new_weight = self.weight + w
        new_volume = self.volume + v
        new_harvested = set(self.harvested)
        new_harvested.add(pos)
        return State(position=pos, basket_load=(new_weight, new_volume), harvested=new_harvested)

    def with_unloaded(self):
        """
        Return a new State with basket unloaded (0,0). Harvested set unchanged.
        """
        return State(position=self.position, basket_load=(0, 0), harvested=self.harvested)

    # --- movement checks and application ---
    def is_valid_move(self, farm, target: Pos) -> bool:
        """
        Move is valid if target is within farm bounds and is a neighbor of current position.
        """
        if not farm.in_bounds(target):
            return False
        return target in farm.get_neighbors(self.position)

    def move_to(self, farm, target: Pos, auto_harvest: bool = True, auto_unload: bool = True):
        """
        Move to target and return resulting State. Rules:
          - If target is a collection station and auto_unload is True => unload on arrival.
          - Else if target is harvestable and auto_harvest is True and fits capacity => harvest on arrival.
        """
        if not self.is_valid_move(farm, target):
            raise ValueError(f"Invalid move from {self.position} to {target}.")

        # base moved state (position changes only)
        new_state = State(position=target, basket_load=self.basket_load, harvested=self.harvested)

        # unloading takes precedence
        if auto_unload and target in farm.get_collection_stations():
            return new_state.with_unloaded()

        # otherwise attempt harvest
        if auto_harvest and new_state.can_harvest_cell(farm, target):
            return new_state.with_harvested(target, farm)

        return new_state

    # --- successor generator for external search ---
    def successors(self, farm, move_cost: int = 1) -> List[Tuple[str, "State", int]]:
        """
        Generate successors (action_descr, next_state, cost) for every neighbor.

        Notes:
        - Movement cost is returned as move_cost (default 1). Cost computation is kept
          simple here; Member 3 / Member 4 will apply the cost/heuristic logic.
        - action strings are human-readable hints (MOVE, HARVEST, UNLOAD).
        """
        succs = []
        for npos in farm.get_neighbors(self.position):
            if not self.is_valid_move(farm, npos):
                continue
            next_state = self.move_to(farm, npos, auto_harvest=True, auto_unload=True)
            action_parts = [f"MOVE {self.position}->{npos}"]
            if next_state.position in farm.get_collection_stations() and (next_state.weight == 0 and next_state.volume == 0):
                action_parts.append("UNLOAD")
            elif npos in next_state.harvested and npos not in self.harvested:
                action_parts.append("HARVEST")
            action = "+".join(action_parts)
            succs.append((action, next_state, move_cost))
        return succs

    # --- goal helper (default) ---
    def is_goal(self, farm) -> bool:
        """
        Default goal definition: all harvestable cells are harvested.
        If your team chooses another goal (e.g., harvest all and return to station), please
        update the A* driver or override this method externally.
        """
        harvestable = {pos for pos in farm.all_cells() if farm.get_weight(pos) > 0}
        return harvestable.issubset(set(self.harvested))

    # --- utilities ---
    def as_dict(self):
        return {
            "position": self.position,
            "weight": self.weight,
            "volume": self.volume,
            "harvested_count": len(self.harvested),
            "harvested": sorted(list(self.harvested)),
        }

    def __repr__(self):
        return (f"State(pos={self.position}, weight={self.weight}kg, vol={self.volume}cm3, "
                f"harvested={len(self.harvested)})")