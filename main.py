"""
CHESSLY - Professional Chess Game
main.py - Main game loop and state management
This is the central file that brings everything together.
"""

import pygame
import sys
import time
import chess
from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TIME_MODES,
    BOARD_SIZE, SQUARE_SIZE, SOUND_CONFIG, SOUND_MASTER_VOLUME
)
from board import ChessBoard
from ui import ChessUI
from engine import ChessEngine

class ChesslyGame:
    """Main game class - orchestrates all modules."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("♟️ Chessly - Professional Chess")
        self.clock = pygame.time.Clock()

        # Modules
        self.board = ChessBoard()
        self.ui = ChessUI()
        self.ai = ChessEngine()

        # Game state
        self.game_state = "menu"          # "menu" or "playing"
        self.ai_enabled = False
        self.white_time = 300
        self.black_time = 300
        self.last_tick = time.time()
        self.timer_running = False
        self.paused = False
        self.side_buttons = {}
        self.menu_buttons = {}

        # Interaction variables
        self.dragging = False
        self.dragged_piece = None
        self.selected_square = None
        self.mouse_pos = (0, 0)

        # Generate simple sounds
        self.sounds = self._create_sounds()
        self.game_over_buttons = {}

        print("Chessly initialized successfully.")

    def _create_sounds(self):
        """Generate soft sound effects (low volume, no harsh clicks)."""
        import numpy as np
        def generate(freq, duration=0.16, volume=SOUND_MASTER_VOLUME):
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            # Smooth envelope to avoid "ear-piercing" clicks (fast attack, gentle decay)
            attack = max(1, int(sample_rate * min(0.012, duration * 0.35)))
            release = max(1, int(sample_rate * min(0.060, duration * 0.55)))
            sustain = max(0, len(t) - attack - release)
            env = np.concatenate([
                np.linspace(0.0, 1.0, attack, False),
                np.ones(sustain, dtype=np.float32),
                np.linspace(1.0, 0.0, release, False),
            ]).astype(np.float32)
            if len(env) < len(t):
                env = np.pad(env, (0, len(t) - len(env)), mode="constant")
            env = env[: len(t)]

            # Slightly softer timbre than a pure sine at high volume
            wave = (
                0.85 * np.sin(2 * np.pi * freq * t) +
                0.15 * np.sin(2 * np.pi * (freq * 2.0) * t)
            ) * env * float(volume)

            # Very gentle soft-clip to prevent spikes
            wave = np.tanh(wave * 1.6)

            wave = (wave * 32767).astype(np.int16)
            sound_array = np.column_stack((wave, wave))
            return pygame.sndarray.make_sound(sound_array)

        return {
            k: generate(v["freq"], v["duration"])
            for k, v in SOUND_CONFIG.items()
        }

    def reset_game(self):
        """Start a fresh game with current settings."""
        self.board.reset()
        self.white_time = TIME_MODES[self.ui.selected_time]
        self.black_time = TIME_MODES[self.ui.selected_time]
        self.timer_running = True
        self.paused = False
        self.last_tick = time.time()
        self._clear_selection()
        # Avoid carrying a flipped orientation across games (common source of “I’m black by default” confusion)
        self.ui.flipped = False

    def handle_menu_click(self, pos):
        """Handle clicks on the main menu."""
        # Use the exact rectangles returned by the UI (handles resizes properly)
        buttons = self.menu_buttons or getattr(self.ui, "menu_buttons", None) or {}
        if buttons.get("time_blitz") and buttons["time_blitz"].collidepoint(pos):
            self.ui.selected_time = "blitz"
            return
        if buttons.get("time_rapid") and buttons["time_rapid"].collidepoint(pos):
            self.ui.selected_time = "rapid"
            return
        if buttons.get("opp_friend") and buttons["opp_friend"].collidepoint(pos):
            self.ui.selected_opponent = "friend"
            return
        if buttons.get("opp_ai") and buttons["opp_ai"].collidepoint(pos):
            self.ui.selected_opponent = "ai"
            return
        if buttons.get("play") and buttons["play"].collidepoint(pos):
            self.ai_enabled = (self.ui.selected_opponent == "ai")
            self.reset_game()
            self.game_state = "playing"
            return

    def handle_board_click(self, pos):
        """Handle clicks/drags on the chessboard."""
        if pos[0] >= BOARD_SIZE:  # Clicked side panel
            self.handle_side_panel_click(pos)
            return

        square = self._get_square_from_pos(pos)
        if square is None:
            return

        piece = self.board.get_piece_at(square)

        if self.selected_square is None:
            # Select a piece (only own color)
            if piece and piece.color == self.board.board.turn:
                self.selected_square = square
                self.dragging = True
                self.dragged_piece = piece
                self.mouse_pos = pos
        else:
            # Try to move
            if self._try_human_move(self.selected_square, square):
                return

            # Not a legal move: maybe reselect another own piece
            if piece and piece.color == self.board.board.turn:
                self.selected_square = square
                self.dragging = True
                self.dragged_piece = piece
                self.mouse_pos = pos
            else:
                self._clear_selection()

    def _clear_selection(self):
        self.selected_square = None
        self.dragging = False
        self.dragged_piece = None

    def _try_human_move(self, from_square, to_square):
        """Attempt a player move; return True if move was made."""
        if from_square is None or to_square is None:
            return False

        # Enforce side-to-move (prevents wrong side moving due to UI bugs)
        moving_piece = self.board.get_piece_at(from_square)
        if not moving_piece or moving_piece.color != self.board.board.turn:
            return False

        move = chess.Move(from_square, to_square)
        captured = self.board.board.is_capture(move)

        if not self.board.make_move(from_square, to_square):
            return False

        (self.sounds["capture"] if captured else self.sounds["move"]).play()
        if self.board.is_check():
            self.sounds["check"].play()
        if self.board.is_game_over():
            self.sounds["mate"].play()

        self._clear_selection()

        # AI move if enabled (AI plays Black in current setup)
        if self.ai_enabled and self.board.get_current_turn() == "Black":
            self._make_ai_move()

        return True

    def _make_ai_move(self):
        """Let the AI make a move."""
        move = self.ai.get_best_move(self.board.board)
        if move:
            self.board.make_move(move.from_square, move.to_square)
            self.sounds["move"].play()

    def _get_square_from_pos(self, pos):
        """Convert mouse position to chess square."""
        x, y = pos
        if x >= BOARD_SIZE:
            return None
        col = x // SQUARE_SIZE
        row = (7 - (y // SQUARE_SIZE)) if not self.ui.flipped else (y // SQUARE_SIZE)
        return chess.square(col, row)

    def update_timer(self):
        """Countdown timer for current player."""
        if self.paused or not self.timer_running or self.board.is_game_over():
            return
        current_time = time.time()
        elapsed = current_time - self.last_tick
        self.last_tick = current_time

        if self.board.get_current_turn() == "White":
            self.white_time = max(0, self.white_time - elapsed)
        else:
            self.black_time = max(0, self.black_time - elapsed)

        if self.white_time <= 0 or self.black_time <= 0:
            self.timer_running = False

    def run(self):
        """Main game loop."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.ai.quit()
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                    elif event.key == pygame.K_f:           # Flip board
                        self.ui.toggle_board_flip()
                    elif event.key == pygame.K_t:           # Toggle theme
                        self.ui.toggle_theme()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if self.game_state == "menu":
                        self.handle_menu_click(pos)
                    else:
                        # If game is over, clicks should go to the overlay buttons
                        if self.board.is_game_over() and self.game_over_buttons:
                            if self.game_over_buttons.get("play_again") and self.game_over_buttons["play_again"].collidepoint(pos):
                                self.reset_game()
                                self.game_state = "playing"
                                continue
                            if self.game_over_buttons.get("back_menu") and self.game_over_buttons["back_menu"].collidepoint(pos):
                                self.timer_running = False
                                self.paused = False
                                self._clear_selection()
                                self.game_state = "menu"
                                continue
                        self.handle_board_click(pos)

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.dragging:
                        pos = pygame.mouse.get_pos()
                        square = self._get_square_from_pos(pos)
                        if square and self.selected_square is not None:
                            self._try_human_move(self.selected_square, square)
                        self._clear_selection()

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        self.mouse_pos = pygame.mouse.get_pos()

            # Update timer
            self.update_timer()

            # Draw everything
            self.screen.fill((30, 30, 30))

            if self.game_state == "menu":
                self.menu_buttons = self.ui.draw_menu(self.screen) or {}
                self.game_over_buttons = {}
            else:
                self.ui.draw_board(self.screen)
                self.ui.draw_highlights(
                    self.screen,
                    self.selected_square,
                    self.board.get_legal_moves(self.selected_square) if self.selected_square is not None else [],
                    self.board.get_last_move()
                )
                self.ui.draw_pieces(
                    self.screen,
                    self.board,
                    selected_square=self.selected_square,
                    dragging=self.dragging,
                    dragged_piece=self.dragged_piece,
                    mouse_pos=self.mouse_pos
                )
                self.side_buttons = self.ui.draw_side_panel(
                    self.screen,
                    self.board,
                    self.white_time,
                    self.black_time,
                    self.ai_enabled,
                    paused=self.paused
                )

                if self.board.is_game_over():
                    result = self.board.get_game_result()
                    self.game_over_buttons = self.ui.draw_game_over(self.screen, result) or {}
                else:
                    self.game_over_buttons = {}

            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_side_panel_click(self, pos):
        """Handle Pause/Restart/Quit clicks while playing."""
        if self.game_state != "playing":
            return
        if not self.side_buttons:
            return

        if self.side_buttons.get("pause") and self.side_buttons["pause"].collidepoint(pos):
            self.paused = not self.paused
            # prevent losing time instantly after resuming
            self.last_tick = time.time()
            return

        if self.side_buttons.get("restart") and self.side_buttons["restart"].collidepoint(pos):
            self.reset_game()
            self._clear_selection()
            return

        if self.side_buttons.get("quit") and self.side_buttons["quit"].collidepoint(pos):
            self.timer_running = False
            self.paused = False
            self._clear_selection()
            self.game_state = "menu"
            return

if __name__ == "__main__":
    game = ChesslyGame()
    game.run()