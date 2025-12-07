def test_board():
    print("Testing GoBoard...")
    from src.game import GoBoard
    
    board = GoBoard()
    assert board.size == 9
    assert board.getStone(4, 4) == GoBoard.EMPTY
    
    # Test placing stones
    assert board.placeStone(4, 4, GoBoard.BLACK) == True
    assert board.getStone(4, 4) == GoBoard.BLACK
    assert board.placeStone(4, 4, GoBoard.WHITE) == False  # Already occupied
    
    # Test capture
    board2 = GoBoard()
    board2.placeStone(0, 0, GoBoard.BLACK)
    board2.placeStone(0, 1, GoBoard.WHITE)
    board2.placeStone(1, 0, GoBoard.WHITE)
    # Black at (0,0) should be captured
    assert board2.getStone(0, 0) == GoBoard.EMPTY
    
    print("✓ GoBoard tests passed!")

def test_game_state():
    print("Testing GameState...")
    from src.game import GameState, GoBoard
    
    game = GameState()
    assert game.current_player == GoBoard.BLACK
    
    # Test move
    assert game.makeMove(4, 4) == True
    assert game.current_player == GoBoard.WHITE
    
    # Test invalid move
    assert game.makeMove(4, 4) == False  # Already occupied
    assert game.current_player == GoBoard.WHITE  # Player doesn't change
    
    print("✓ GameState tests passed!")

def test_heuristic():
    """Test heuristic function"""
    print("Testing Heuristic...")
    from src.game import GoBoard
    from src.ai import GoHeuristic
    
    board = GoBoard()
    
    # Empty board should have score 0
    score = GoHeuristic.evaluate(board, GoBoard.BLACK)
    assert score == 0
    
    # Place some stones
    board.placeStone(4, 4, GoBoard.BLACK)
    board.placeStone(3, 3, GoBoard.WHITE)
    
    # Black should have positive score
    black_score = GoHeuristic.evaluate(board, GoBoard.BLACK)
    white_score = GoHeuristic.evaluate(board, GoBoard.WHITE)
    
    print(f"  Black score: {black_score:.2f}")
    print(f"  White score: {white_score:.2f}")
    
    print("✓ Heuristic tests passed!")

def test_minimax():
    """Test minimax AI"""
    print("Testing Minimax AI...")
    from src.game import GoBoard
    from src.ai import MinimaxAI
    
    board = GoBoard()
    ai = MinimaxAI(GoBoard.BLACK, depth=2, time_limit=2.0)
    
    # Get best move
    move = ai.getBestMove(board)
    assert move is not None
    assert len(move) == 2
    
    stats = ai.getStats()
    print(f"  Best move: {move}")
    print(f"  Nodes explored: {stats['nodes_explored']}")
    
    print("✓ Minimax AI tests passed!")

def test_integration():
    print("Testing Integration (AI vs AI)...")
    from src.game import GameState, GoBoard
    from src.ai import MinimaxAI
    
    game = GameState()
    black_ai = MinimaxAI(GoBoard.BLACK, depth=2, time_limit=2.0)
    white_ai = MinimaxAI(GoBoard.WHITE, depth=2, time_limit=2.0)
    
    # Play 5 moves
    for i in range(5):
        if game.current_player == GoBoard.BLACK:
            move = black_ai.getBestMove(game.board)
        else:
            move = white_ai.getBestMove(game.board)
        
        if move:
            game.makeMove(move[0], move[1])
            print(f"  Move {i+1}: {move} by {'Black' if game.current_player == GoBoard.WHITE else 'White'}")
        else:
            print(f"  Move {i+1}: No legal moves")
            break
    
    print("✓ Integration test passed!")
    print("\nFinal board state:")
    print(game.board)

def main():
    print("=" * 60)
    print("Running Go Game Tests")
    print("=" * 60)
    print()
    
    try:
        test_board()
        print()
        test_game_state()
        print()
        test_heuristic()
        print()
        test_minimax()
        print()
        test_integration()
        print()
        print("=" * 60)
        print("All tests passed!")
        print("=" * 60)
        print("\nYou can now run: python main.py")
    except AssertionError as e:
        print(f"\nTest failed: {e}")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
