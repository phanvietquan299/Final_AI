import sys
from src.ui import GoGameUI
from src.game import GameState

def main():
    print("=" * 60)
    print("Go Game 9x9 - Adversarial Search")
    print("Task 2: Introduction to AI - Final Project")
    print("=" * 60)
    print("\nFeatures:")
    print("  - Full Go rules implementation (9x9 board)")
    print("  - Minimax AI with Alpha-Beta pruning")
    print("  - Heuristic evaluation function")
    print("  - Player vs Player and Player vs AI modes")
    print("  - Friendly UI with mouse control")
    print("\nControls:")
    print("  - Click on board to place stone")
    print("  - 'Pass' button to pass your turn")
    print("  - 'New Game' to start over")
    print("  - 'PvP' / 'PvAI' to switch game mode")
    print("\nStarting game...\n")
    
    try:
        # Create and run the game
        game_ui = GoGameUI(mode=GameState.MODE_PVAI)
        game_ui.run()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
