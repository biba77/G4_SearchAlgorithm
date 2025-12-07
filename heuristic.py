from typing import Any, Iterable
from cost import hex_distance

BASKET_LIMIT = 12.0

def nearest_target_dist(pos: Any, targets: Iterable[Any]) -> int:
    items = list(targets)
    if len(items) == 0:
        return 0
    return min(hex_distance(pos, t) for t in items)

def h_nearest_plot(state: Any, farm: Any) -> int:
    harvestable = [pos for pos in farm.cells.keys()
        if farm.get_weight(pos) > 0 and pos not in state.harvested
        ]
    return nearest_target_dist(state.position, harvestable)


def h_return_if_full(state: Any, farm: Any) -> int:
    # If not full, no need to return to station
    if state.weight < BASKET_LIMIT:
        return 0

    # Find the nearest collection station
    stations = farm.get_collection_stations()
    if not stations:
        return 0

    return min(hex_distance(state.position, cs) for cs in stations)


def h_combined(state: Any, farm: Any) -> int:
    dist_plot = h_nearest_plot(state, farm)
    dist_base = h_return_if_full(state, farm)
    return max(dist_plot, dist_base)
