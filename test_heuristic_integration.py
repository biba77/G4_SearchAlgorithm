from farm_layout import Farm
from state import State
from cost import hex_distance, path_cost
from heuristic import h_nearest_plot, h_return_if_full, h_combined

def main():
    farm = Farm(radius=4)
    s0 = State(position=farm.start)

    print("Initial state:", s0)
    print("hex_distance(start -> first neighbor):")
    n0 = farm.get_neighbors(farm.start)[0]
    print(hex_distance(farm.start, n0))
    print("path_cost from 0 for that step:", path_cost(0, farm.start, n0))

    print("\nHeuristics at start (empty basket):")
    print("h_nearest_plot:", h_nearest_plot(s0, farm))
    print("h_return_if_full:", h_return_if_full(s0, farm))
    print("h_combined:", h_combined(s0, farm))

    harvestable_neighbors = [p for p in farm.get_neighbors(s0.position) if farm.get_weight(p) > 0]
    if harvestable_neighbors:
        hpos = harvestable_neighbors[0]
        s1 = s0.move_to(farm, hpos)
        print("\nAfter moving to a harvestable cell:", s1)
        print("h_nearest_plot:", h_nearest_plot(s1, farm))
        print("h_return_if_full:", h_return_if_full(s1, farm))
        print("h_combined:", h_combined(s1, farm))

    s_full = State(position=s0.position, basket_load=(12, 5000), harvested=s0.harvested)
    print("\nFull-basket state at start:", s_full)
    print("h_nearest_plot (full):", h_nearest_plot(s_full, farm))
    print("h_return_if_full (full):", h_return_if_full(s_full, farm))
    print("h_combined (full):", h_combined(s_full, farm))

if __name__ == "__main__":
    main()
