class GoBoard:
    
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    BOARD_SIZE = 9
    
    def __init__(self):
        self.size = self.BOARD_SIZE
        self.board = [[self.EMPTY for _ in range(self.size)] for _ in range(self.size)]
        self.last_move = None
        self.ko_point = None  # For Ko rule
        
    def copy(self):
        new_board = GoBoard()
        new_board.board = [row[:] for row in self.board]
        new_board.last_move = self.last_move
        new_board.ko_point = self.ko_point
        return new_board
    
    def isValidPosition(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size
    
    def getStone(self, row, col):
        if not self.isValidPosition(row, col):
            return None
        return self.board[row][col]
    
    def placeStone(self, row, col, color):
        if not self.isValidPosition(row, col):
            return False
        
        if self.board[row][col] != self.EMPTY:
            return False
        
        # Check Ko rule
        if self.ko_point == (row, col):
            return False
        
        # Place stone
        self.board[row][col] = color
        self.last_move = (row, col)
        
        # Capture opponent stones
        opponent_color = self.WHITE if color == self.BLACK else self.BLACK
        captured_groups = []
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if self.isValidPosition(nr, nc) and self.board[nr][nc] == opponent_color:
                group = self._getGroup(nr, nc)
                if self._countLiberties(group) == 0:
                    captured_groups.append(group)
        
        # Remove captured stones
        for group in captured_groups:
            for r, c in group:
                self.board[r][c] = self.EMPTY
        
        # Check if placed stone has liberties (suicide rule)
        own_group = self._getGroup(row, col)
        if self._countLiberties(own_group) == 0 and len(captured_groups) == 0:
            self.board[row][col] = self.EMPTY  # Revert move
            self.last_move = None
            return False
        
        # Update Ko point (simple Ko detection)
        if len(captured_groups) == 1 and len(captured_groups[0]) == 1:
            self.ko_point = captured_groups[0][0]
        else:
            self.ko_point = None
        
        return True
    
    def _getGroup(self, row, col):
        if not self.isValidPosition(row, col):
            return []
        
        color = self.board[row][col]
        if color == self.EMPTY:
            return []
        
        visited = set()
        group = []
        queue = [(row, col)]
        
        while queue:
            r, c = queue.pop(0)
            if (r, c) in visited:
                continue
            
            visited.add((r, c))
            group.append((r, c))
            
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if (self.isValidPosition(nr, nc) and 
                    (nr, nc) not in visited and 
                    self.board[nr][nc] == color):
                    queue.append((nr, nc))
        
        return group
    
    def _countLiberties(self, group):
        liberties = set()
        
        for row, col in group:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                if (self.isValidPosition(nr, nc) and 
                    self.board[nr][nc] == self.EMPTY):
                    liberties.add((nr, nc))
        
        return len(liberties)
    
    def getLegalMoves(self, color):
        legal_moves = []
        
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == self.EMPTY:
                    # Try placing stone
                    temp_board = self.copy()
                    if temp_board.placeStone(row, col, color):
                        legal_moves.append((row, col))
        
        return legal_moves
    
    def getTerritoryScore(self, color):
        visited = [[False] * self.size for _ in range(self.size)]
        territory = 0
        
        # Count stones
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == color:
                    territory += 1
        
        # Count controlled empty territory
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == self.EMPTY and not visited[row][col]:
                    empty_region, owner = self._analyzeEmptyRegion(row, col, visited)
                    if owner == color:
                        territory += len(empty_region)
        
        return territory
    
    def _analyzeEmptyRegion(self, start_row, start_col, visited):
        region = []
        queue = [(start_row, start_col)]
        adjacent_colors = set()
        
        while queue:
            row, col = queue.pop(0)
            
            if not self.isValidPosition(row, col) or visited[row][col]:
                continue
            
            if self.board[row][col] != self.EMPTY:
                adjacent_colors.add(self.board[row][col])
                continue
            
            visited[row][col] = True
            region.append((row, col))
            
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                if self.isValidPosition(nr, nc) and not visited[nr][nc]:
                    queue.append((nr, nc))
        
        # Determine owner
        if len(adjacent_colors) == 1:
            owner = list(adjacent_colors)[0]
        else:
            owner = self.EMPTY
        
        return region, owner
    
    def isGameOver(self):
        black_moves = len(self.getLegalMoves(self.BLACK))
        white_moves = len(self.getLegalMoves(self.WHITE))
        
        return black_moves == 0 and white_moves == 0
    
    def __str__(self):
        symbols = {self.EMPTY: '.', self.BLACK: '●', self.WHITE: '○'}
        lines = []
        lines.append('  ' + ' '.join(str(i) for i in range(self.size)))
        for i, row in enumerate(self.board):
            lines.append(f"{i} {' '.join(symbols[cell] for cell in row)}")
        return '\n'.join(lines)
