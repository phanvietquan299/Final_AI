from .board import GoBoard

class GameState:
    
    MODE_PVP = "pvp"  # Player vs Player
    MODE_PVAI = "pvai"  # Player vs AI
    
    def __init__(self, mode=MODE_PVAI):
        self.board = GoBoard()
        self.current_player = GoBoard.BLACK  # Black plays first
        self.mode = mode
        self.move_history = []
        self.pass_count = 0
        self.game_over = False
        self.winner = None
        
    def switchPlayer(self):
        self.current_player = (GoBoard.WHITE if self.current_player == GoBoard.BLACK 
                              else GoBoard.BLACK)
    
    def makeMove(self, row, col):
        if self.game_over:
            return False
        
        success = self.board.placeStone(row, col, self.current_player)
        
        if success:
            self.move_history.append((row, col, self.current_player))
            self.pass_count = 0
            self.switchPlayer()
            self._checkGameOver()
            return True
        
        return False
    
    def passTurn(self):
        self.pass_count += 1
        self.switchPlayer()
        
        # Game ends if both players pass
        if self.pass_count >= 2:
            self._checkGameOver()
    
    def _checkGameOver(self):
        if self.pass_count >= 2 or self.board.isGameOver():
            self.game_over = True
            
            # Calculate scores
            black_score = self.board.getTerritoryScore(GoBoard.BLACK)
            white_score = self.board.getTerritoryScore(GoBoard.WHITE)
            
            # Add komi for white (compensation for playing second)
            komi = 6.5
            white_score += komi
            
            if black_score > white_score:
                self.winner = GoBoard.BLACK
            else:
                self.winner = GoBoard.WHITE
    
    def getLegalMoves(self):
        return self.board.getLegalMoves(self.current_player)
    
    def getScore(self):
        black_score = self.board.getTerritoryScore(GoBoard.BLACK)
        white_score = self.board.getTerritoryScore(GoBoard.WHITE) + 6.5
        return black_score, white_score
    
    def copy(self):
        new_state = GameState(self.mode)
        new_state.board = self.board.copy()
        new_state.current_player = self.current_player
        new_state.move_history = self.move_history[:]
        new_state.pass_count = self.pass_count
        new_state.game_over = self.game_over
        new_state.winner = self.winner
        return new_state
