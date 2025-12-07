from ..game.board import GoBoard

class GoHeuristic:
    
    # Weight factors for different strategic elements
    WEIGHTS = {
        'stone_count': 1.0,
        'territory': 2.0,
        'liberties': 1.5,
        'center_control': 1.2,
        'group_strength': 1.3,
    }
    
    @staticmethod
    def evaluate(board, player_color):
        opponent_color = GoBoard.WHITE if player_color == GoBoard.BLACK else GoBoard.BLACK
        
        # Calculate individual factors
        stone_diff = GoHeuristic._stoneCountDiff(board, player_color, opponent_color)
        territory_diff = GoHeuristic._territoryDiff(board, player_color, opponent_color)
        liberty_diff = GoHeuristic._libertyDiff(board, player_color, opponent_color)
        center_diff = GoHeuristic._centerControlDiff(board, player_color, opponent_color)
        group_strength_diff = GoHeuristic._groupStrengthDiff(board, player_color, opponent_color)
        
        # Weighted sum
        score = (
            GoHeuristic.WEIGHTS['stone_count'] * stone_diff +
            GoHeuristic.WEIGHTS['territory'] * territory_diff +
            GoHeuristic.WEIGHTS['liberties'] * liberty_diff +
            GoHeuristic.WEIGHTS['center_control'] * center_diff +
            GoHeuristic.WEIGHTS['group_strength'] * group_strength_diff
        )
        
        return score
    
    @staticmethod
    def _stoneCountDiff(board, player, opponent):
        player_count = sum(row.count(player) for row in board.board)
        opponent_count = sum(row.count(opponent) for row in board.board)
        return player_count - opponent_count
    
    @staticmethod
    def _territoryDiff(board, player, opponent):
        player_territory = board.getTerritoryScore(player)
        opponent_territory = board.getTerritoryScore(opponent)
        return player_territory - opponent_territory
    
    @staticmethod
    def _libertyDiff(board, player, opponent):
        player_liberties = GoHeuristic._countTotalLiberties(board, player)
        opponent_liberties = GoHeuristic._countTotalLiberties(board, opponent)
        return (player_liberties - opponent_liberties) / 10.0  # Normalize
    
    @staticmethod
    def _countTotalLiberties(board, color):
        visited = [[False] * board.size for _ in range(board.size)]
        total_liberties = 0
        
        for row in range(board.size):
            for col in range(board.size):
                if board.board[row][col] == color and not visited[row][col]:
                    group = board._getGroup(row, col)
                    for r, c in group:
                        visited[r][c] = True
                    total_liberties += board._countLiberties(group)
        
        return total_liberties
    
    @staticmethod
    def _centerControlDiff(board, player, opponent):
        center_positions = [
            (3, 3), (3, 4), (3, 5),
            (4, 3), (4, 4), (4, 5),
            (5, 3), (5, 4), (5, 5)
        ]
        
        player_center = sum(1 for r, c in center_positions if board.board[r][c] == player)
        opponent_center = sum(1 for r, c in center_positions if board.board[r][c] == opponent)
        
        return player_center - opponent_center
    
    @staticmethod
    def _groupStrengthDiff(board, player, opponent):
        player_strength = GoHeuristic._calculateGroupStrength(board, player)
        opponent_strength = GoHeuristic._calculateGroupStrength(board, opponent)
        return (player_strength - opponent_strength) / 10.0  # Normalize
    
    @staticmethod
    def _calculateGroupStrength(board, color):
        """Calculate total strength of all groups"""
        visited = [[False] * board.size for _ in range(board.size)]
        total_strength = 0
        
        for row in range(board.size):
            for col in range(board.size):
                if board.board[row][col] == color and not visited[row][col]:
                    group = board._getGroup(row, col)
                    for r, c in group:
                        visited[r][c] = True
                    
                    liberties = board._countLiberties(group)
                    group_size = len(group)
                    
                    # Strength = group_size * sqrt(liberties)
                    # Larger groups with more liberties are exponentially stronger
                    strength = group_size * (liberties ** 0.5)
                    total_strength += strength
        
        return total_strength
