# state.py
"""
State representation and transition model for the Kiwiberry Picking A* implementation.

Responsibilities implemented:
- Hashable State class storing position, basket load, and harvested cells.
- Validation for moves (in-bounds / neighbor).
- Automatic harvesting when entering a harvestable cell if capacity allows.
- Automatic unloading when entering a collection station.
- Successor generation for use by A* (action, next_state, cost).

Assumptions / Design choices:
- Movement cost between adjacent cells is 1 (can be changed).
- Harvesting happens automatically and atomically *only if* both weight and volume capacity allow;
  if capacity would be exceeded, the move is still allowed but harvesting is NOT performed.
- Entering a collection station automatically unloads the basket (resets basket load to (0,0)).
- `harvested` is stored as a frozenset for immutability/hashability.
- `basket_load` stored as (weight_kg:int, volume_cm3:int)
- The State class does not modify the Farm object; it only records which harvest positions have been harvested.
"""

from typing import Tuple, Iterable, List, Optional
from dataclasses import dataclass
from copy import deepcopy

# Import typing-friendly alias for coordinates
Pos = Tuple[int, int]   # (q, r)


@dataclass(frozen=True)
class State:
    """
    Immutable, hashable state for the A* search.
    Attributes:
        position: current (q, r) coordinate of Alex.
        basket_load: tuple (weight_kg, volume_cm3) currently in basket.
        harvested: frozenset of positions that have already been harvested.
    """
    position: Pos
    basket_load: Tuple[int, int]  # (weight_kg, volume_cm3)
    harvested: frozenset

    def __init__(self, position: Pos, basket_load: Tuple[int, int] = (0, 0),
                 harvested: Optional[Iterable[Pos]] = None):
        object.__setattr__(self, "position", position)
        object.__setattr__(self, "basket_load", tuple(basket_load))
        if harvested is None:
            harvested = frozenset()
        else:
            harvested = frozenset(harvested)
        object.__setattr__(self, "harvested", harvested)

    # Read-only helpers    
    @property
    def weight(self) -> int:
        return self.basket_load[0]

    @property
    def volume(self) -> int:
        return self.basket_load[1]

    # Capacity checks and updates
    def can_harvest_cell(self, farm, pos: Pos) -> bool:
        """
        Return True if the cell at pos has harvestable berries AND the current basket
        has enough remaining capacity (both weight and volume) to take the whole cell.
        Partial harvesting is not supported (design choice).
        """
        if not farm.in_bounds(pos):
            return False
        w = farm.get_weight(pos)
        v = farm.get_volume(pos)
        if w <= 0:
            return False
        # If already harvested, cannot harvest again
        if pos in self.harvested:
            return False
        # Check capacity
        remaining_w = farm.max_weight - self.weight
        remaining_v = farm.max_volume - self.volume
        return (w <= remaining_w) and (v <= remaining_v)

    def with_harvested(self, pos: Pos, farm):
        """
        Return a new State representing harvesting the entire cell at pos.
        Precondition: can_harvest_cell(pos) is True.
        """
        if not self.can_harvest_cell(farm, pos):
            raise ValueError("Cannot harvest cell: either not harvestable or capacity exceeded.")
        w = farm.get_weight(pos)
        v = farm.get_volume(pos)
        new_weight = self.weight + w
        new_volume = self.volume + v
        new_harvested = set(self.harvested)
        new_harvested.add(pos)
        return State(position=pos, basket_load=(new_weight, new_volume), harvested=new_harvested)

    def with_unloaded(self):
        """
        Return a new State representing unloading the basket at the current position.
        This resets basket load to (0,0). Harvested set stays the same.
        """
        return State(position=self.position, basket_load=(0, 0), harvested=self.harvested)

    # Movement / Transition logic
    def is_valid_move(self, farm, target: Pos) -> bool:
        """
        Validate whether a move from current position to target is allowed.
        Rules:
          - target must be within farm bounds (farm.in_bounds)
          - target must be a neighbor of current position (farm.get_neighbors)
        Note: We allow moving into any in-bounds neighbor; harvesting/unloading is handled separately.
        """
        if not farm.in_bounds(target):
            return False
        return target in farm.get_neighbors(self.position)

    def move_to(self, farm, target: Pos, auto_harvest: bool = True, auto_unload: bool = True):
        """
        Return a new State after moving to target.
        Behavior:
          - If auto_unload and target is a collection station, unload occurs (basket -> (0,0)).
          - Else if auto_harvest and target is harvestable and capacity allows, harvest occurs automatically.
          - If both harvestable and collection station (unlikely), unloading takes precedence (unload first).
        Precondition: is_valid_move(farm, target) must be True.
        """
        if not self.is_valid_move(farm, target):
            raise ValueError(f"Invalid move from {self.position} to {target}.")

        # Start with moved state (same basket, same harvested set)
        new_state = State(position=target, basket_load=self.basket_load, harvested=self.harvested)

        # If target is a collection station and auto_unload enabled, unload.
        if auto_unload and target in farm.get_collection_stations():
            new_state = new_state.with_unloaded()
            return new_state

        # Otherwise, attempt auto-harvest if enabled
        if auto_harvest and new_state.can_harvest_cell(farm, target):
            new_state = new_state.with_harvested(target, farm)

        # Return final state after move (may be unchanged except for position)
        return new_state

    # Successor generation for search
    def successors(self, farm, move_cost: int = 1) -> List[Tuple[str, "State", int]]:
        """
        Generate successor triples: (action_str, next_state, cost)
        - action_str examples:
            "MOVE (q,r)->(q2,r2)"
            "MOVE+HARVEST (q2,r2)"   (if harvest occurred)
            "MOVE+UNLOAD (q2,r2)"    (if moved into collection station and unload occurred)
        - cost: numerical cost for the move (default 1 per move). Harvest/unload do not add cost by design.
        """
        succs = []
        for npos in farm.get_neighbors(self.position):
            if not self.is_valid_move(farm, npos):
                continue
            # simulate the move with both auto_unload and auto_harvest enabled
            next_state = self.move_to(farm, npos, auto_harvest=True, auto_unload=True)

            # determine action string
            action_parts = [f"MOVE {self.position}->{npos}"]
            # If unloading happened, basket weight/volume reset to zero
            if next_state.position in farm.get_collection_stations() and (next_state.weight == 0 and next_state.volume == 0):
                action_parts.append("UNLOAD")
            elif npos in next_state.harvested and npos not in self.harvested:
                action_parts.append("HARVEST")

            action = "+".join(action_parts)
            succs.append((action, next_state, move_cost))
        return succs

    # Goal / utility helpers
    def is_goal(self, farm) -> bool:
        """
        Example goal-checker: all harvestable cells have been harvested.
        This is a common goal for coverage problems. If your A* goal definition differs (e.g.
        'collect at least X kg and return to start' or 'return to collection station after harvesting Y'),
        replace or extend this method.
        """
        harvestable = {pos for pos in farm.all_cells() if farm.get_weight(pos) > 0}
        return harvestable.issubset(set(self.harvested))

    def as_dict(self):
        """Return a serializable dict useful for debugging/logging."""
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
