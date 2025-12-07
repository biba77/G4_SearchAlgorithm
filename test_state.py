# test_state.py
# Run this to verify State behavior with farm_layout.py... it worked!!

from farm_layout import Farm
from state import State

def run_basic_checks():
    farm = Farm(radius=4)
    s0 = State(position=farm.start)
    print("Start:", s0)

    # neighbors
    neighbors = farm.get_neighbors(farm.start)
    print("Neighbors of start:", neighbors)

    # move to first neighbor
    n = neighbors[0]
    s1 = s0.move_to(farm, n)
    print("After move:", s1)

    # if neighbor is harvestable and fits, it should be harvested automatically
    if farm.get_weight(n) > 0:
        print("Neighbor harvestable:", farm.get_weight(n), "kg,", farm.get_volume(n), "cm3")
        assert n in s1.harvested or (farm.get_weight(n) > farm.max_weight), "Expected automatic harvesting when capacity allows"

    # simulate moving to a collection station to unload
    cs = farm.get_collection_stations()[0]
    print("Collection station:", cs)
    # find a path of neighbors from current to cs (naive: move one step if neighbor else start->some neighbor)
    if s1.is_valid_move(farm, cs):
        s_unloaded = s1.move_to(farm, cs)
        print("Arrived at collection station:", s_unloaded)
        assert s_unloaded.weight == 0 and s_unloaded.volume == 0, "Expected unloading at collection station"
    else:
        print("Collection station not adjacent - skipping direct unload test (that's fine).")

    print("Basic tests completed.")

if __name__ == "__main__":
    run_basic_checks()
