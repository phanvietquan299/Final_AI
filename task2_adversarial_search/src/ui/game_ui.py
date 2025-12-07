import threading
import pygame
import sys
from ..game.game_state import GameState
from ..game.board import GoBoard
from ..ai.minimax import MinimaxAI

class GoGameUI:
    
    # Colors
    BOARD_COLOR = (220, 179, 92)  # Wood color
    LINE_COLOR = (0, 0, 0)
    BLACK_STONE = (0, 0, 0)
    WHITE_STONE = (255, 255, 255)
    GRID_COLOR = (50, 50, 50)
    HIGHLIGHT_COLOR = (255, 0, 0)
    TEXT_COLOR = (0, 0, 0)
    BUTTON_COLOR = (100, 149, 237)
    BUTTON_HOVER = (65, 105, 225)
    
    # Layout settings
    MARGIN = 50
    CELL_SIZE = 60
    STONE_RADIUS = 25
    GRID_SIZE = 9
    
    def __init__(self, mode=GameState.MODE_PVAI):
        pygame.init()
        
        self.mode = mode
        self.game_state = GameState(mode)
        
        self.ai = None
        if mode == GameState.MODE_PVAI:
            self.ai = MinimaxAI(GoBoard.WHITE, depth=3, time_limit=5.0)
        
        # Window setup
        self.board_size = self.CELL_SIZE * (self.GRID_SIZE - 1) + 2 * self.MARGIN
        self.info_panel_width = 250
        self.window_width = self.board_size + self.info_panel_width
        self.window_height = self.board_size
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Go Game 9x9 - Adversarial Search")
        
        # Font
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 20)
        
        # UI state
        self.hover_pos = None
        self.thinking = False
        self.message = ""
        
        # Buttons
        self.buttons = self._createButtons()
        self.ai_thread = None
        self.pending_ai_move = None
        self.ai_move_ready = False
        self.ai_stats = None
    
    def _createButtons(self):
        button_x = self.board_size + 20
        button_width = self.info_panel_width - 40
        button_height = 40
        
        buttons = {
            'new_game': pygame.Rect(button_x, 400, button_width, button_height),
            'pass': pygame.Rect(button_x, 450, button_width, button_height),
            'pvp': pygame.Rect(button_x, 510, button_width // 2 - 5, button_height),
            'pvai': pygame.Rect(button_x + button_width // 2 + 5, 510, button_width // 2 - 5, button_height),
        }
        
        return buttons
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEMOTION:
                    self._handleMouseMotion(event.pos)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handleMouseClick(event.pos)
            
            self._applyPendingAiMove()

            # AI move (if applicable)
            if (not self.thinking and 
                not self.game_state.game_over and 
                self.mode == GameState.MODE_PVAI and 
                self.game_state.current_player == self.ai.color):
                self._startAiMove()
            
            # Draw everything
            self._draw()
            pygame.display.flip()
            clock.tick(30)
        
        pygame.quit()
        sys.exit()
    
    def _handleMouseMotion(self, pos):
        # Check if hovering over board
        board_pos = self._screenToBoard(pos)
        if board_pos:
            self.hover_pos = board_pos
        else:
            self.hover_pos = None
    
    def _handleMouseClick(self, pos):
        # Check buttons
        for button_name, button_rect in self.buttons.items():
            if button_rect.collidepoint(pos):
                self._handleButtonClick(button_name)
                return

        if self.game_state.game_over:
            return

        # Block board moves while AI is thinking
        if self.thinking and self.mode == GameState.MODE_PVAI:
            return

        board_pos = self._screenToBoard(pos)
        if board_pos:
            row, col = board_pos
            if self.game_state.makeMove(row, col):
                self.message = ""
            else:
                self.message = "Invalid move!"
    
    def _handleButtonClick(self, button_name):
        if button_name == 'new_game':
            self.game_state = GameState(self.mode)
            self.message = "New game started!"
        
        elif button_name == 'pass':
            if not self.game_state.game_over:
                self.game_state.passTurn()
                self.message = f"{'Black' if self.game_state.current_player == GoBoard.WHITE else 'White'} passed"
        
        elif button_name == 'pvp':
            self.mode = GameState.MODE_PVP
            self.ai = None
            self.game_state = GameState(self.mode)
            self.message = "Mode: Player vs Player"
        
        elif button_name == 'pvai':
            self.mode = GameState.MODE_PVAI
            self.ai = MinimaxAI(GoBoard.WHITE, depth=3, time_limit=5.0)
            self.game_state = GameState(self.mode)
            self.message = "Mode: Player vs AI"
    
    def _startAiMove(self):
        if self.ai_thread is not None or not self.ai:
            return

        self.thinking = True
        self.message = "AI THINKING..."
        self.ai_move_ready = False
        self.pending_ai_move = None
        self.ai_stats = None

        ai_snapshot = self.ai
        self.ai_thread = threading.Thread(target=self._aiMoveWorker, args=(ai_snapshot,), daemon=True)
        self.ai_thread.start()

    def _aiMoveWorker(self, ai_instance):
        move = ai_instance.getBestMove(self.game_state.board)
        stats = ai_instance.getStats()
        self.pending_ai_move = move
        self.ai_stats = stats
        self.ai_move_ready = True

    def _applyPendingAiMove(self):
        if not self.ai_move_ready:
            return

        self.ai_move_ready = False
        self.ai_thread = None
        move = self.pending_ai_move
        stats = self.ai_stats or {}
        self.pending_ai_move = None
        self.ai_stats = None

        if self.mode != GameState.MODE_PVAI or self.game_state.game_over:
            self.thinking = False
            return

        if move:
            self.game_state.makeMove(move[0], move[1])
            nodes = stats.get('nodes_explored')
            if nodes is not None:
                self.message = f"AI moved. Explored {nodes} nodes"
            else:
                self.message = "AI moved."
        else:
            self.game_state.passTurn()
            self.message = "AI passed"

        self.thinking = False
    
    def _screenToBoard(self, screen_pos):
        x, y = screen_pos
        
        # Check if click is on board area
        if (self.MARGIN <= x < self.board_size - self.MARGIN and
            self.MARGIN <= y < self.board_size - self.MARGIN):
            
            col = round((x - self.MARGIN) / self.CELL_SIZE)
            row = round((y - self.MARGIN) / self.CELL_SIZE)
            
            if 0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE:
                return (row, col)
        
        return None
    
    def _boardToScreen(self, row, col):
        x = self.MARGIN + col * self.CELL_SIZE
        y = self.MARGIN + row * self.CELL_SIZE
        return (x, y)
    
    def _draw(self):
        self.screen.fill(self.BOARD_COLOR)
        
        # Draw board and stones
        self._drawBoard()
        self._drawStones()
        
        # Draw hover indicator
        if self.hover_pos and not self.game_state.game_over and not self.thinking:
            self._drawHover()
        
        # Draw info panel
        self._drawInfoPanel()
    
    def _drawBoard(self):
        # Draw grid lines
        for i in range(self.GRID_SIZE):
            # Horizontal lines
            start_x = self.MARGIN
            end_x = self.MARGIN + (self.GRID_SIZE - 1) * self.CELL_SIZE
            y = self.MARGIN + i * self.CELL_SIZE
            pygame.draw.line(self.screen, self.LINE_COLOR, (start_x, y), (end_x, y), 2)
            
            # Vertical lines
            x = self.MARGIN + i * self.CELL_SIZE
            start_y = self.MARGIN
            end_y = self.MARGIN + (self.GRID_SIZE - 1) * self.CELL_SIZE
            pygame.draw.line(self.screen, self.LINE_COLOR, (x, start_y), (x, end_y), 2)
        
        # Draw star points (2-2, 2-6, 6-2, 6-6, 4-4)
        star_points = [(2, 2), (2, 6), (6, 2), (6, 6), (4, 4)]
        for row, col in star_points:
            x, y = self._boardToScreen(row, col)
            pygame.draw.circle(self.screen, self.LINE_COLOR, (x, y), 5)
    
    def _drawStones(self):
        board = self.game_state.board
        
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                stone = board.getStone(row, col)
                
                if stone == GoBoard.BLACK:
                    x, y = self._boardToScreen(row, col)
                    pygame.draw.circle(self.screen, self.BLACK_STONE, (x, y), self.STONE_RADIUS)
                    pygame.draw.circle(self.screen, self.LINE_COLOR, (x, y), self.STONE_RADIUS, 2)
                
                elif stone == GoBoard.WHITE:
                    x, y = self._boardToScreen(row, col)
                    pygame.draw.circle(self.screen, self.WHITE_STONE, (x, y), self.STONE_RADIUS)
                    pygame.draw.circle(self.screen, self.LINE_COLOR, (x, y), self.STONE_RADIUS, 2)
        
        # Highlight last move
        if board.last_move:
            row, col = board.last_move
            x, y = self._boardToScreen(row, col)
            pygame.draw.circle(self.screen, self.HIGHLIGHT_COLOR, (x, y), 8, 3)
    
    def _drawHover(self):
        if self.hover_pos:
            row, col = self.hover_pos
            if self.game_state.board.getStone(row, col) == GoBoard.EMPTY:
                x, y = self._boardToScreen(row, col)
                color = self.BLACK_STONE if self.game_state.current_player == GoBoard.BLACK else self.WHITE_STONE
                pygame.draw.circle(self.screen, color, (x, y), self.STONE_RADIUS, 3)
    
    def _drawInfoPanel(self):
        panel_x = self.board_size
        
        # Background
        pygame.draw.rect(self.screen, (240, 240, 240), 
                        (panel_x, 0, self.info_panel_width, self.window_height))
        
        # Title
        title = self.title_font.render("Go 9x9", True, self.TEXT_COLOR)
        self.screen.blit(title, (panel_x + 20, 20))
        
        # Current player
        y_offset = 70
        current = "Black" if self.game_state.current_player == GoBoard.BLACK else "White"
        player_text = self.font.render(f"Current: {current}", True, self.TEXT_COLOR)
        self.screen.blit(player_text, (panel_x + 20, y_offset))
        
        # Score
        y_offset += 40
        black_score, white_score = self.game_state.getScore()
        score_text = self.font.render("Score:", True, self.TEXT_COLOR)
        self.screen.blit(score_text, (panel_x + 20, y_offset))
        
        y_offset += 30
        black_text = self.small_font.render(f"Black: {black_score:.1f}", True, self.TEXT_COLOR)
        self.screen.blit(black_text, (panel_x + 20, y_offset))
        
        y_offset += 25
        white_text = self.small_font.render(f"White: {white_score:.1f}", True, self.TEXT_COLOR)
        self.screen.blit(white_text, (panel_x + 20, y_offset))
        
        # Mode
        y_offset += 40
        mode_text = self.small_font.render(f"Mode: {'PvAI' if self.mode == GameState.MODE_PVAI else 'PvP'}", 
                                          True, self.TEXT_COLOR)
        self.screen.blit(mode_text, (panel_x + 20, y_offset))
        
        # Game over message
        if self.game_state.game_over:
            y_offset += 40
            winner = "Black" if self.game_state.winner == GoBoard.BLACK else "White"
            winner_text = self.font.render(f"{winner} Wins!", True, (255, 0, 0))
            self.screen.blit(winner_text, (panel_x + 20, y_offset))
        
        # Message
        y_offset += 40
        if self.message:
            # Word wrap for long messages
            words = self.message.split()
            lines = []
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if self.small_font.size(test_line)[0] < self.info_panel_width - 40:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            
            for line in lines:
                msg_text = self.small_font.render(line, True, (0, 100, 0))
                self.screen.blit(msg_text, (panel_x + 20, y_offset))
                y_offset += 22
        
        # Buttons
        self._drawButtons()
    
    def _drawButtons(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # New Game button
        button = self.buttons['new_game']
        color = self.BUTTON_HOVER if button.collidepoint(mouse_pos) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, color, button, border_radius=5)
        pygame.draw.rect(self.screen, self.LINE_COLOR, button, 2, border_radius=5)
        text = self.font.render("New Game", True, self.WHITE_STONE)
        text_rect = text.get_rect(center=button.center)
        self.screen.blit(text, text_rect)
        
        # Pass button
        button = self.buttons['pass']
        color = self.BUTTON_HOVER if button.collidepoint(mouse_pos) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, color, button, border_radius=5)
        pygame.draw.rect(self.screen, self.LINE_COLOR, button, 2, border_radius=5)
        text = self.font.render("Pass", True, self.WHITE_STONE)
        text_rect = text.get_rect(center=button.center)
        self.screen.blit(text, text_rect)
        
        # Mode buttons
        # PvP
        button = self.buttons['pvp']
        is_active = self.mode == GameState.MODE_PVP
        color = (50, 200, 50) if is_active else (self.BUTTON_HOVER if button.collidepoint(mouse_pos) else self.BUTTON_COLOR)
        pygame.draw.rect(self.screen, color, button, border_radius=5)
        pygame.draw.rect(self.screen, self.LINE_COLOR, button, 2, border_radius=5)
        text = self.small_font.render("PvP", True, self.WHITE_STONE)
        text_rect = text.get_rect(center=button.center)
        self.screen.blit(text, text_rect)
        
        # PvAI
        button = self.buttons['pvai']
        is_active = self.mode == GameState.MODE_PVAI
        color = (50, 200, 50) if is_active else (self.BUTTON_HOVER if button.collidepoint(mouse_pos) else self.BUTTON_COLOR)
        pygame.draw.rect(self.screen, color, button, border_radius=5)
        pygame.draw.rect(self.screen, self.LINE_COLOR, button, 2, border_radius=5)
        text = self.small_font.render("PvAI", True, self.WHITE_STONE)
        text_rect = text.get_rect(center=button.center)
        self.screen.blit(text, text_rect)
