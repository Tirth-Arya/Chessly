"""
CHESSLY - Professional Chess Game
ui.py - FIXED VERSION (real PNG pieces + no crash)
"""

import pygame
import os
import urllib.request
import urllib.error
from settings import (
    BOARD_SIZE, SIDE_PANEL_WIDTH, SQUARE_SIZE, THEMES, DEFAULT_THEME,
    TITLE_FONT, BIG_FONT, TEXT_FONT, SMALL_FONT, PIECE_FONT, ASSETS_DIR
)
import chess

class ChessUI:
    def __init__(self):
        self.current_theme = DEFAULT_THEME
        self.flipped = False
        self.use_unicode = False
        self.piece_images = {}
        self._load_pieces()                    # Guaranteed real pieces

        self.selected_time = "blitz"
        self.selected_opponent = "friend"

        # Populated by draw_menu() for accurate hit-testing
        self.menu_buttons = {}

    def _load_pieces(self):
        os.makedirs(ASSETS_DIR, exist_ok=True)
        pieces = ["wP","wR","wN","wB","wQ","wK","bP","bR","bN","bB","bQ","bK"]
        base_url = "https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/"

        # Download missing pieces
        for p in pieces:
            path = os.path.join(ASSETS_DIR, f"{p}.png")
            if not os.path.exists(path):
                print(f"Downloading real piece: {p}.png")
                try:
                    with urllib.request.urlopen(base_url + f"{p}.png", timeout=12) as resp:
                        if getattr(resp, "status", 200) == 200:
                            with open(path, "wb") as f:
                                f.write(resp.read())
                except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
                    pass

        # Load images
        loaded = 0
        for p in pieces:
            path = os.path.join(ASSETS_DIR, f"{p}.png")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path)
                    self.piece_images[f"{p}"] = pygame.transform.smoothscale(img, (SQUARE_SIZE, SQUARE_SIZE))
                    self.piece_images[f"{p}_small"] = pygame.transform.smoothscale(img, (38, 38))
                    loaded += 1
                except:
                    pass

        if loaded == 12:
            self.use_unicode = False
            print("All 12 real PNG chess pieces loaded successfully.")
        else:
            self.use_unicode = True
            print("Using Unicode fallback (PNG loading issue).")

    def _piece_to_unicode(self, piece: chess.Piece) -> str:
        """
        Convert a python-chess Piece (P/p, N/n, ...) into a true Unicode chess glyph.
        This is only used as a fallback when PNG assets aren't available.
        """
        # python-chess: piece.symbol() -> 'p','n','b','r','q','k' for black; uppercase for white
        sym = piece.symbol()
        return {
            "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
            "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚",
        }.get(sym, sym)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"

    def toggle_board_flip(self):
        self.flipped = not self.flipped

    def _format_time(self, seconds: float) -> str:
        seconds = max(0, int(seconds))
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"

    def _draw_button(self, screen, rect: pygame.Rect, label: str, *, colors, filled=True):
        bg = colors.get("button_bg", (45, 45, 45)) if filled else colors["panel_bg"]
        pygame.draw.rect(screen, bg, rect, border_radius=14)
        pygame.draw.rect(screen, colors.get("button_border", (70, 70, 70)), rect, width=2, border_radius=14)
        text = TEXT_FONT.render(label, True, colors["text"])
        screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

    def draw_board(self, screen):
        colors = THEMES[self.current_theme]
        for rank in range(8):
            for file in range(8):
                color = colors["light_square"] if (rank + file) % 2 == 0 else colors["dark_square"]
                pygame.draw.rect(screen, color, (file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_highlights(self, screen, selected_square, legal_moves, last_move):
        colors = THEMES[self.current_theme]
        if last_move:
            for sq in (last_move.from_square, last_move.to_square):
                file = chess.square_file(sq)
                rank = 7 - chess.square_rank(sq) if not self.flipped else chess.square_rank(sq)
                pygame.draw.rect(screen, colors["last_move"], (file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

        if selected_square is not None:
            file = chess.square_file(selected_square)
            rank = 7 - chess.square_rank(selected_square) if not self.flipped else chess.square_rank(selected_square)
            pygame.draw.rect(screen, colors["selected"], (file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), width=6)

        for move in legal_moves:
            target = move.to_square
            file = chess.square_file(target)
            rank = 7 - chess.square_rank(target) if not self.flipped else chess.square_rank(target)
            pygame.draw.circle(screen, colors["highlight"], (file * SQUARE_SIZE + SQUARE_SIZE // 2, rank * SQUARE_SIZE + SQUARE_SIZE // 2), 18)

    def draw_pieces(self, screen, board, selected_square=None, dragging=False, dragged_piece=None, mouse_pos=None):
        """Draw pieces; supports dragging visuals."""
        for square in chess.SQUARES:
            piece = board.get_piece_at(square)
            if not piece:
                continue
            if dragging and selected_square is not None and square == selected_square:
                continue

            key = ("w" if piece.color == chess.WHITE else "b") + piece.symbol().upper()

            if not self.use_unicode and key in self.piece_images:
                img = self.piece_images[key]
                file = chess.square_file(square)
                rank = 7 - chess.square_rank(square) if not self.flipped else chess.square_rank(square)
                x = file * SQUARE_SIZE + (SQUARE_SIZE - img.get_width()) // 2
                y = rank * SQUARE_SIZE + (SQUARE_SIZE - img.get_height()) // 2
                screen.blit(img, (x, y))
            else:
                symbol = self._piece_to_unicode(piece)
                color = (255, 255, 255) if piece.color == chess.WHITE else (0, 0, 0)
                text = PIECE_FONT.render(symbol, True, color)
                file = chess.square_file(square)
                rank = 7 - chess.square_rank(square) if not self.flipped else chess.square_rank(square)
                x = file * SQUARE_SIZE + (SQUARE_SIZE - text.get_width()) // 2
                y = rank * SQUARE_SIZE + (SQUARE_SIZE - text.get_height()) // 2
                screen.blit(text, (x, y))

        # Dragged piece
        if dragging and dragged_piece and mouse_pos:
            key = ("w" if dragged_piece.color == chess.WHITE else "b") + dragged_piece.symbol().upper()
            if not self.use_unicode and key in self.piece_images:
                img = self.piece_images[key]
                screen.blit(img, (mouse_pos[0] - SQUARE_SIZE // 2, mouse_pos[1] - SQUARE_SIZE // 2))
            else:
                symbol = self._piece_to_unicode(dragged_piece)
                color = (255, 255, 255) if dragged_piece.color == chess.WHITE else (0, 0, 0)
                text = PIECE_FONT.render(symbol, True, color)
                screen.blit(text, (mouse_pos[0] - text.get_width()//2, mouse_pos[1] - text.get_height()//2))

    def draw_side_panel(self, screen, board, white_time, black_time, ai_enabled, paused: bool = False):
        colors = THEMES[self.current_theme]
        pygame.draw.rect(screen, colors["panel_bg"], (BOARD_SIZE, 0, SIDE_PANEL_WIDTH, BOARD_SIZE))
        title = TITLE_FONT.render("CHESSLY", True, colors["accent"])
        screen.blit(title, (BOARD_SIZE + (SIDE_PANEL_WIDTH - title.get_width()) // 2, 25))

        # Info
        y = 120
        turn = board.get_current_turn() if hasattr(board, "get_current_turn") else ("White" if board.board.turn == chess.WHITE else "Black")
        mode = "VS AI" if ai_enabled else "VS FRIEND"
        screen.blit(TEXT_FONT.render(f"Mode: {mode}", True, colors["text"]), (BOARD_SIZE + 20, y))
        y += 34
        screen.blit(TEXT_FONT.render(f"Turn: {turn}", True, colors["text"]), (BOARD_SIZE + 20, y))
        y += 40

        # Timer cards
        card_w = SIDE_PANEL_WIDTH - 40
        card_h = 92
        white_rect = pygame.Rect(BOARD_SIZE + 20, y, card_w, card_h)
        y += card_h + 14
        black_rect = pygame.Rect(BOARD_SIZE + 20, y, card_w, card_h)
        y += card_h + 22

        def draw_timer_card(rect, name, t, active):
            pygame.draw.rect(screen, colors.get("panel_card", (35, 35, 35)), rect, border_radius=18)
            pygame.draw.rect(screen, colors["accent"] if active and not paused else colors.get("button_border", (70, 70, 70)), rect, width=2, border_radius=18)
            screen.blit(SMALL_FONT.render(name, True, colors.get("muted_text", (180, 180, 180))), (rect.x + 14, rect.y + 10))
            time_text = BIG_FONT.render(self._format_time(t), True, colors["text"])
            screen.blit(time_text, (rect.x + 14, rect.y + 34))
            if paused:
                p = SMALL_FONT.render("PAUSED", True, colors.get("muted_text", (180, 180, 180)))
                screen.blit(p, (rect.right - p.get_width() - 14, rect.y + 12))

        active_white = (turn == "White")
        draw_timer_card(white_rect, "White", white_time, active_white)
        draw_timer_card(black_rect, "Black", black_time, not active_white)

        # Controls
        btn_w = (card_w - 12) // 2
        btn_h = 54
        pause_rect = pygame.Rect(BOARD_SIZE + 20, y, btn_w, btn_h)
        restart_rect = pygame.Rect(pause_rect.right + 12, y, btn_w, btn_h)
        y += btn_h + 12
        quit_rect = pygame.Rect(BOARD_SIZE + 20, y, card_w, btn_h)

        self._draw_button(screen, pause_rect, "Resume" if paused else "Pause", colors=colors)
        self._draw_button(screen, restart_rect, "Restart", colors=colors)
        self._draw_button(screen, quit_rect, "Quit to Menu", colors=colors, filled=False)

        return {
            "pause": pause_rect,
            "restart": restart_rect,
            "quit": quit_rect,
        }

    def draw_menu(self, screen):
        colors = THEMES[self.current_theme]
        screen.fill(colors.get("bg", (28, 28, 28)))
        title = TITLE_FONT.render("CHESSLY", True, colors["accent"])
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 80))

        time_rect = pygame.Rect(screen.get_width()//2 - 280, 220, 560, 90)
        pygame.draw.rect(screen, colors.get("panel_card", (50, 50, 50)), time_rect, border_radius=20)
        on = colors["text"]
        off = colors.get("muted_text", (180, 180, 180))
        screen.blit(BIG_FONT.render("5 MIN BLITZ", True, on if self.selected_time == "blitz" else off), (screen.get_width()//2 - 240, 245))
        screen.blit(BIG_FONT.render("10 MIN RAPID", True, on if self.selected_time == "rapid" else off), (screen.get_width()//2 + 20, 245))

        opponent_rect = pygame.Rect(screen.get_width()//2 - 280, 340, 560, 90)
        pygame.draw.rect(screen, colors.get("panel_card", (50, 50, 50)), opponent_rect, border_radius=20)
        screen.blit(BIG_FONT.render("VS FRIEND", True, on if self.selected_opponent == "friend" else off), (screen.get_width()//2 - 240, 365))
        screen.blit(BIG_FONT.render("VS AI", True, on if self.selected_opponent == "ai" else off), (screen.get_width()//2 + 60, 365))

        play_rect = pygame.Rect(screen.get_width()//2 - 160, 480, 320, 100)
        pygame.draw.rect(screen, colors.get("button_bg", (45, 45, 45)), play_rect, border_radius=25)
        pygame.draw.rect(screen, colors.get("button_border", (70, 70, 70)), play_rect, width=2, border_radius=25)
        play_text = BIG_FONT.render("PLAY", True, colors["text"])
        screen.blit(play_text, (play_rect.centerx - play_text.get_width()//2, play_rect.centery - play_text.get_height()//2 + 5))

        # Exact clickable areas (match what we drew)
        time_left = pygame.Rect(time_rect.x, time_rect.y, time_rect.w // 2, time_rect.h)
        time_right = pygame.Rect(time_rect.centerx, time_rect.y, time_rect.w - time_rect.w // 2, time_rect.h)
        opp_left = pygame.Rect(opponent_rect.x, opponent_rect.y, opponent_rect.w // 2, opponent_rect.h)
        opp_right = pygame.Rect(opponent_rect.centerx, opponent_rect.y, opponent_rect.w - opponent_rect.w // 2, opponent_rect.h)

        self.menu_buttons = {
            "time_blitz": time_left,
            "time_rapid": time_right,
            "opp_friend": opp_left,
            "opp_ai": opp_right,
            "play": play_rect,
        }
        return self.menu_buttons

    def draw_game_over(self, screen, result_text):
        colors = THEMES[self.current_theme]
        overlay = pygame.Surface((BOARD_SIZE + SIDE_PANEL_WIDTH, BOARD_SIZE))
        overlay.set_alpha(170)
        overlay.fill(colors.get("overlay", (0, 0, 0)))
        screen.blit(overlay, (0, 0))
        text = BIG_FONT.render(result_text, True, (255, 255, 255))
        screen.blit(text, ((BOARD_SIZE + SIDE_PANEL_WIDTH)//2 - text.get_width()//2, 270))

        # Buttons (returned for hit-testing)
        btn_w = 320
        btn_h = 70
        cx = (BOARD_SIZE + SIDE_PANEL_WIDTH) // 2
        play_again = pygame.Rect(cx - btn_w // 2, 360, btn_w, btn_h)
        back_menu = pygame.Rect(cx - btn_w // 2, 450, btn_w, btn_h)

        self._draw_button(screen, play_again, "Play again", colors=colors, filled=True)
        self._draw_button(screen, back_menu, "Back to menu", colors=colors, filled=False)

        return {"play_again": play_again, "back_menu": back_menu}