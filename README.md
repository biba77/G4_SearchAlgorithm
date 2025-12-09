# G4_SearchAlgorithm
This is the A* search algorithm implemented for the Kiwiberry Picking Problem for CSC3206 assignment 2

## Features:
* **Hexagonal Grid System:** Uses axial coordinates (q, r) for map representation and distance calculations.
* **Constraint Management:** The agent tracks current Weight (kg) and Volume (cm³). Harvesting is atomic (all-or-nothing) and requires sufficient basket capacity.
* **Automatic Actions:** The state logic automatically handles harvesting when entering a fruit plot (if capacity allows) and unloading when entering a collection station.
* **Heuristic Optimization:** Uses a combined heuristic that considers both the distance to the next harvestable plot and the distance to a station if the basket is full.
* **Visualization:** Includes a Matplotlib-based visualizer to display the farm layout and the agent's calculated path.

## Core Structure

### Logic
* **`A_search.py`**: The driver script. Implements the A* algorithm using a priority queue (`heapq`) to explore states based on $f(n) = g(n) + h(n)$.
* **`state.py`**: Defines the `State` class. It is immutable and hashable, tracking the agent's position, basket load, and the set of harvested plots. It generates valid successors (moves).
* **`farm_layout.py`**: Defines the `Farm` environment, including the hexagonal grid boundaries (radius 4), fruit locations (weight/volume), and collection stations.
* **`heuristic.py`**: Contains the heuristic functions. The `h_combined` function switches between targeting fruit or the nearest station based on the basket's load.
* **`cost.py`**: Calculates movement costs (uniform cost of 1.0) and Manhattan distance for hexagonal grids.

### Visualization
* **`Visualiser.py`**: Renders the farm using `matplotlib`. It runs the search and plots the resulting path on a graphical hex grid.

## Prerequisites
1. Recommended to use Spyder 6 as it comes with most of the libraries needed to run this (eg; matplotlib)

## Instructions
### Search Results Output
Run A_search.py

### Visualization of the output
Run A_search.py

## Credits
**Environtment & Data Structure:** Hajah Atikah Haziqah Binti Abd Jalil @ Nuratikah Haziqah 
**State Representation & Transition Model:** Humayra Mohamed Esmail 
**Cost Function & Heuristics Function (A*):** Owen Tay Khai Hung 
**A* Search Algorithm Implementation::** Habiba Tarek Abdalla Mohamed Hassouna 
**Visualization:** Jonas Ho Cheng Roong 