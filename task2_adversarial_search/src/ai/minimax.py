import time
from ..game.board import GoBoard
from .heuristic import GoHeuristic

class MinimaxAI:
    def __init__(self, color, depth=3, time_limit=5.0):
        self.color = color
        self.depth = depth
        self.time_limit = time_limit
        self.nodes_explored = 0
        self.start_time = 0
        
    def getBestMove(self, board):       
        self.nodes_explored = 0
        self.start_time = time.time()
        
        legal_moves = board.getLegalMoves(self.color)
        
        if not legal_moves:
            return None
        
        # If only one move, return it immediately
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Try each legal move
        for move in legal_moves:
            # Check time limit
            if time.time() - self.start_time > self.time_limit:
                break
            
            # Make move on copy of board
            new_board = board.copy()
            new_board.placeStone(move[0], move[1], self.color)
            
            # Get score for this move
            score = self._minimax(
                new_board,
                self.depth - 1,
                False,  # Next level is minimizing
                alpha,
                beta
            )
            
            # Update best move
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, best_score)
        
        return best_move
    
    def _minimax(self, board, depth, is_maximizing, alpha, beta):
        self.nodes_explored += 1
        
        # Check time limit
        if time.time() - self.start_time > self.time_limit:
            return GoHeuristic.evaluate(board, self.color)
        
        # Base case: reached depth limit or game over
        if depth == 0 or board.isGameOver():
            return GoHeuristic.evaluate(board, self.color)
        
        current_player = self.color if is_maximizing else self._opponentColor()
        legal_moves = board.getLegalMoves(current_player)
        
        # No legal moves available
        if not legal_moves:
            return GoHeuristic.evaluate(board, self.color)
        
        if is_maximizing:
            max_score = float('-inf')
            
            for move in legal_moves:
                # Make move
                new_board = board.copy()
                new_board.placeStone(move[0], move[1], current_player)
                
                # Recurse
                score = self._minimax(new_board, depth - 1, False, alpha, beta)
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                
                # Alpha-beta pruning
                if beta <= alpha:
                    break
            
            return max_score
        
        else:  # Minimizing
            min_score = float('inf')
            
            for move in legal_moves:
                # Make move
                new_board = board.copy()
                new_board.placeStone(move[0], move[1], current_player)
                
                # Recurse
                score = self._minimax(new_board, depth - 1, True, alpha, beta)
                min_score = min(min_score, score)
                beta = min(beta, score)
                
                # Alpha-beta pruning
                if beta <= alpha:
                    break
            
            return min_score
    
    def _opponentColor(self):
        return GoBoard.WHITE if self.color == GoBoard.BLACK else GoBoard.BLACK
    
    def getStats(self):
        return {
            'nodes_explored': self.nodes_explored,
            'depth': self.depth,
            'time_limit': self.time_limit
        }
