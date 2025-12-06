'''
What needs to be done:
1. Define the cells/ each hex (harvestable or movement)
2. Define the starting point
3. Define the collection stations
4. Define Alex's movement (how to find neighbour, check weight and volume)
'''
from collections import namedtuple

Cell = namedtuple("Cell", ["weight", "volume"]) # each coloured cell has weight and volume (refer to assignment 1)

class Farm:
    def __init__(self, radius=4): # farm size by radius, hex within the radius is part of farm
        self.radius = radius
        self.cells = {}  # maps (q, r) -> Cell(weight, volume)/ {} holds the cells

        # build hex region using axial coordinates with cube constraint:
        # s = -q - r ; keep max(abs(q), abs(r), abs(s)) <= radius (hex in maths has 3 coordinates where q + r + s = 0)
        for q in range(-radius, radius + 1):
            for r in range(-radius, radius + 1):
                s = -q - r
                if max(abs(q), abs(r), abs(s)) <= radius: # make sure cell is present in each hex
                    self.cells[(q, r)] = Cell(weight=0, volume=0) 

        # starting point
        self.start = (0, 0)

        # collection stations
        self.collection_stations = [
            (-3, 0),  # left-ish station
            (3, -1),  # right-ish station
            (2, 2),   # top-right station
        ]

        # Capacity limits for Alex's basket
        self.max_weight = 12       # kg
        self.max_volume = 15000    # cm^3

        # harvestable cells 
        # map of (q, r) -> (weight_kg, volume_cm3)
        harvest_cells = {
            # weight 2 kg -> 2000 cm3
            (-1, 1): (2, 2000),
            (0, 2): (2, 2000),
            (2, -2): (2, 2000),

            # weight 4 kg -> 3000 cm3
            (1, 0): (4, 3000),
            (-2, 1): (4, 3000),
            (0, -1): (4, 3000),
            (1, -2): (4, 3000),

            # weight 6 kg -> 5000 cm3
            (1, -1): (6, 5000),
            (-1, 0): (6, 5000),
            (2, 0): (6, 5000),

            # weight 8 kg -> 3000 cm3 
            (-2, 0): (8, 3000),
            (3, -2): (8, 3000),
        }

        # insert harvest cells into self.cells
        for pos, (w, v) in harvest_cells.items():
            if pos in self.cells:
                self.cells[pos] = Cell(weight=w, volume=v)
            else:
                # If coordinate is outside radius, add it
                self.cells[pos] = Cell(weight=w, volume=v)

    def all_cells(self): # return list of all positions in the farm
        return list(self.cells.keys())

    def get_weight(self, pos): # return weight of the given coordinate
        return self.cells[pos].weight if pos in self.cells else 0

    def get_volume(self, pos): # return volume of the given coordinate
        return self.cells[pos].volume if pos in self.cells else 0

    def is_harvestable(self, pos): # to check if the cell contains kiwiberries or not
        return self.get_weight(pos) > 0

    def get_neighbors(self, pos): # to identify adjacent cells for movement purposes
        q, r = pos
        directions = [
            (1, 0),    # east
            (1, -1),   # northeast
            (0, -1),   # northwest
            (-1, 0),   # west
            (-1, 1),   # southwest
            (0, 1),    # southeast
        ]
        neighbors = []
        for dq, dr in directions:
            npos = (q + dq, r + dr)
            if npos in self.cells:
                neighbors.append(npos)
        return neighbors

    def in_bounds(self, pos): # to check the boundaries of the farm
        return pos in self.cells

    def get_collection_stations(self): # return list of collection stations coordinate
        return list(self.collection_stations)

    def all_print(self): # print (for verification purpose) all the coordinates and to check the methods
        items = sorted(self.cells.items(), key=lambda kv: (kv[0][1], kv[0][0]))
        print("Position (q,r)     : weight kg, volume cm^3")
        for pos, cell in items:
            mark = ""
            if pos == self.start:
                mark = " <- START HERE"
            elif pos in self.collection_stations:
                mark = " <- COLLECTION STATION"
            print(f"{str(pos):>18} : {cell.weight:>2} kg, {cell.volume:>5} cm3{mark}")


# test code to check layout and methods
if __name__ == "__main__":
    farm = Farm()
    print("Start:", farm.start)
    print("Collection stations:", farm.get_collection_stations())
    print("Total cells:", len(farm.all_cells()))
    print("Neighbors of start:", farm.get_neighbors(farm.start))
    print("Is start harvestable?", farm.is_harvestable(farm.start))
    print()
    farm.all_print()


''' 
For own understanding: 
pos = position
'd' = a change
'q, r' = position coordinate
'''