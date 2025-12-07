from typing import Tuple

Hex = Tuple[int, int]

def step_cost(start: Hex, end: Hex) -> float:
    return 1.0

def path_cost(total: float, start: Hex, end: Hex) -> float:
    return total + step_cost(start, end)

def hex_distance(a: Hex, b: Hex) -> int:
    aq, ar = a
    bq, br = b

    ax = aq
    ay = -aq - ar
    az = ar

    bx = bq
    by = -bq - br
    bz = br

    dx = abs(ax - bx)
    dy = abs(ay - by)
    dz = abs(az - bz)

    return (dx + dy + dz) // 2
