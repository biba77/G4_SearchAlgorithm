
# Import the specific functions from your existing files
from A_search import solve as run_text_solution
from Visualiser import main as run_visualizer

def main():
    print("==========================================")
    print("      KIWIBERRY BOT - FULL EXECUTION      ")
    print("==========================================\n")

    # 1. Run the Text-Based Solution (Detailed Logs)
    print(">>> PART 1: COMPUTING TEXT SOLUTION...")
    run_text_solution()
    
    print("\n" + "="*42)
    print(">>> PART 2: LAUNCHING VISUALIZER...")
    print("    (Close the popup window to finish)")
    print("="*42 + "\n")

    # 2. Run the Visualizer (Graph)
    # Note: This will calculate the path again for the graph.
    run_visualizer() 
    
    print("\n>>> EXECUTION COMPLETE.")

if __name__ == "__main__":
    main()