import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
import math

# Import your existing modules
from farm_layout import Farm
from state import State
from A_search import a_search, h_combined

# --- Configuration ---
HEX_SIZE = 1.0
FIG_SIZE = (10, 10)

def axial_to_pixel(q, r, size):
    """
    Converts axial coordinates (q, r) to pixel (x, y) for Flat-topped hexes.
    Ref: matches neighbors defined in farm_layout.py
    """
    x = size * (3./2 * q)
    y = size * math.sqrt(3) * (r + q/2)
    return x, y

def draw_farm(ax, farm, path_coords=None):
    """
    Draws the grid, stations, fruits, and the path.
    """
    # 1. Plot all cells
    for pos in farm.cells.keys():
        q, r = pos
        x, y = axial_to_pixel(q, r, HEX_SIZE)
        
        # Determine Color
        weight = farm.get_weight(pos)
        is_station = pos in farm.collection_stations
        is_start = (pos == farm.start)
        
        fill_color = 'white'
        edge_color = '#ccc'
        label = None
        
        if is_station:
            fill_color = '#add8e6' # Light Blue
            label = "Station"
        elif weight > 0:
            # Darker green for heavier fruits
            intensity = 0.4 + (weight / 10.0) 
            fill_color = (0, intensity if intensity <=1 else 1, 0)
            label = f"{weight}kg"
        elif is_start:
            fill_color = '#ffcc00' # Gold
            label = "Start"
        
        # Draw Hexagon
        hex_patch = RegularPolygon(
            (x, y), 
            numVertices=6, 
            radius=HEX_SIZE * 0.95, 
            orientation=0, # Flat-topped
            facecolor=fill_color, 
            edgecolor='black' if weight > 0 or is_station else edge_color,
            alpha=0.8
        )
        ax.add_patch(hex_patch)

        # Add Text Labels (Coords + Weight)
        ax.text(x, y + 0.3, f"{q},{r}", ha='center', va='center', fontsize=7, color='#555')
        if label:
            text_col = 'white' if weight > 0 else 'black'
            ax.text(x, y - 0.2, label, ha='center', va='center', fontsize=8, color=text_col, fontweight='bold')

    # 2. Plot the Path (if provided)
    if path_coords:
        # Extract X and Y lists
        xs, ys = [], []
        for (q, r) in path_coords:
            px, py = axial_to_pixel(q, r, HEX_SIZE)
            xs.append(px)
            ys.append(py)
        
        # Draw the line
        ax.plot(xs, ys, color='red', linewidth=3, linestyle='--', marker='o', alpha=0.7, label='Agent Path')
        
        # Annotate start and end of path
        ax.text(xs[0], ys[0], "START", color='red', fontweight='bold', ha='right')
        ax.text(xs[-1], ys[-1], "END", color='red', fontweight='bold', ha='right')

    # Set Aspect Ratio and Bounds
    ax.set_aspect('equal')
    ax.axis('off')
    plt.title("Kiwiberry Farm Search Visualization", fontsize=16)
    
    # Create a custom legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='h', color='w', markerfacecolor='#ffcc00', markersize=15, label='Start'),
        Line2D([0], [0], marker='h', color='w', markerfacecolor='#add8e6', markersize=15, label='Collection Station'),
        Line2D([0], [0], marker='h', color='w', markerfacecolor='green', markersize=15, label='Kiwiberry Plot'),
        Line2D([0], [0], color='red', lw=3, linestyle='--', label='Alex\'s Path')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

def main():
    # 1. Setup Farm and Search
    print("Running A* Search...")
    farm = Farm(radius=4)
    start_state = State(position=farm.start)
    
    # Run the imported A* logic
    goal_state, path_data, cost = a_search(farm, start_state, heuristic_fn=h_combined)
    
    if not goal_state:
        print("No solution found to visualize!")
        return

    print(f"Solution found! Cost: {cost}, Steps: {len(path_data)}")

    # 2. Extract Coordinate sequence from the path
    # path_data is a list of (action_str, State) tuples
    # We need to prepend the start position because path_data usually contains the moves *after* start
    path_coords = [farm.start] + [state.position for (_, state) in path_data]

    # 3. Visualize
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    draw_farm(ax, farm, path_coords)
    
    plt.show()

if __name__ == "__main__":
    main()