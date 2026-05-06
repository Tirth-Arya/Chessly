"""
CHESSLY - Professional Chess Game
ui.py - Premium wood-themed UI
"""

import pygame
import os
import urllib.request
import urllib.error
from settings import (
    BOARD_SIZE, BOARD_INNER, BOARD_MARGIN, SIDE_PANEL_WIDTH, SQUARE_SIZE,
    THEMES, DEFAULT_THEME,
    TITLE_FONT, BIG_FONT, TEXT_FONT, SMALL_FONT, PIECE_FONT,
    COORD_FONT, HISTORY_FONT, ASSETS_DIR
)
import chess


class ChessUI:
    def __init__(self):
        self.current_theme = DEFAULT_THEME
        self.flipped = False
        self.use_unicode = False
        self.piece_images = {}
        self._load_pieces()
        self.selected_time = "blitz"
        self.selected_opponent = "friend"
        self.menu_buttons = {}
        self.history_scroll = 0

    def _load_pieces(self):
        os.makedirs(ASSETS_DIR, exist_ok=True)
        pieces = ["wP","wR","wN","wB","wQ","wK","bP","bR","bN","bB","bQ","bK"]

        # Lichess SVG URL (current correct path)
        svg_base = "https://raw.githubusercontent.com/lichess-org/lila/refs/heads/master/public/piece/cburnett/"

        # Detect available SVG->PNG converter
        svg_converter = None
        try:
            import cairosvg
            svg_converter = "cairosvg"
        except (ImportError, OSError):
            pass
        if svg_converter is None:
            try:
                from PIL import Image
                import io
                svg_converter = "pillow"
            except ImportError:
                pass

        for p in pieces:
            png_path = os.path.join(ASSETS_DIR, f"{p}.png")
            if os.path.exists(png_path):
                continue
            svg_url = svg_base + f"{p}.svg"
            try:
                req = urllib.request.Request(svg_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    svg_data = resp.read()
                if svg_converter == "cairosvg":
                    import cairosvg
                    cairosvg.svg2png(bytestring=svg_data, write_to=png_path,
                                    output_width=200, output_height=200)
                    print(f"Converted (cairosvg): {p}")
                elif svg_converter == "pillow":
                    # Pillow can't render SVG directly, save SVG for pygame
                    svg_path = os.path.join(ASSETS_DIR, f"{p}.svg")
                    with open(svg_path, "wb") as f:
                        f.write(svg_data)
                    # Try rendering with Pillow if possible (needs pillow-svg or similar)
                    try:
                        from PIL import Image
                        img = Image.open(svg_path)
                        img = img.resize((200, 200), Image.LANCZOS)
                        img.save(png_path, "PNG")
                        os.remove(svg_path)
                        print(f"Converted (pillow): {p}")
                    except Exception:
                        # Keep SVG file for potential future use
                        print(f"Saved SVG (no PNG conversion): {p}")
                else:
                    svg_path = os.path.join(ASSETS_DIR, f"{p}.svg")
                    with open(svg_path, "wb") as f:
                        f.write(svg_data)
            except Exception as e:
                print(f"Failed to download {p}: {e}")

        loaded = 0
        for p in pieces:
            png_path = os.path.join(ASSETS_DIR, f"{p}.png")
            if os.path.exists(png_path):
                try:
                    img = pygame.image.load(png_path)
                    self.piece_images[p] = pygame.transform.smoothscale(img, (SQUARE_SIZE, SQUARE_SIZE))
                    self.piece_images[f"{p}_small"] = pygame.transform.smoothscale(img, (32, 32))
                    loaded += 1
                except Exception as e:
                    print(f"Failed to load {p}.png: {e}")
        self.use_unicode = loaded != 12
        print(f"Pieces loaded: {loaded}/12" + (" (Unicode fallback)" if self.use_unicode else ""))

    def _piece_to_unicode(self, piece):
        sym = piece.symbol()
        return {"P":"♙","N":"♘","B":"♗","R":"♖","Q":"♕","K":"♔",
                "p":"♟","n":"♞","b":"♝","r":"♜","q":"♛","k":"♚"}.get(sym, sym)

    def toggle_theme(self):
        keys = list(THEMES.keys())
        idx = keys.index(self.current_theme)
        self.current_theme = keys[(idx + 1) % len(keys)]

    def toggle_board_flip(self):
        self.flipped = not self.flipped

    def _format_time(self, seconds):
        seconds = max(0, int(seconds))
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def _sq_to_pixel(self, file, rank):
        """Convert board file/rank to pixel position (top-left of square)."""
        x = BOARD_MARGIN + file * SQUARE_SIZE
        y = BOARD_MARGIN + rank * SQUARE_SIZE
        return x, y

    # ==================== BOARD ====================
    def draw_board(self, screen):
        colors = THEMES[self.current_theme]

        # Board border/frame
        frame_rect = pygame.Rect(0, 0, BOARD_SIZE, BOARD_SIZE)
        pygame.draw.rect(screen, colors["board_border"], frame_rect)

        # Coordinate background
        coord_bg = colors.get("coord_bg", colors["board_border"])
        pygame.draw.rect(screen, coord_bg, (0, 0, BOARD_SIZE, BOARD_MARGIN))
        pygame.draw.rect(screen, coord_bg, (0, BOARD_SIZE - BOARD_MARGIN, BOARD_SIZE, BOARD_MARGIN))
        pygame.draw.rect(screen, coord_bg, (0, BOARD_MARGIN, BOARD_MARGIN, BOARD_INNER))
        pygame.draw.rect(screen, coord_bg, (BOARD_SIZE - BOARD_MARGIN, BOARD_MARGIN, BOARD_MARGIN, BOARD_INNER))

        # Draw squares
        for rank in range(8):
            for file in range(8):
                is_light = (rank + file) % 2 == 0
                color = colors["light_square"] if is_light else colors["dark_square"]
                x, y = self._sq_to_pixel(file, rank)
                pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

        # Draw coordinates
        files = "abcdefgh"
        coord_color = colors.get("coord_text", (200, 180, 150))
        for i in range(8):
            f_idx = i if not self.flipped else 7 - i
            r_idx = 8 - i if not self.flipped else i + 1

            # File labels (top & bottom)
            fl = COORD_FONT.render(files[f_idx], True, coord_color)
            cx = BOARD_MARGIN + i * SQUARE_SIZE + SQUARE_SIZE // 2 - fl.get_width() // 2
            screen.blit(fl, (cx, (BOARD_MARGIN - fl.get_height()) // 2))
            screen.blit(fl, (cx, BOARD_SIZE - BOARD_MARGIN + (BOARD_MARGIN - fl.get_height()) // 2))

            # Rank labels (left & right)
            rl = COORD_FONT.render(str(r_idx), True, coord_color)
            cy = BOARD_MARGIN + i * SQUARE_SIZE + SQUARE_SIZE // 2 - rl.get_height() // 2
            screen.blit(rl, ((BOARD_MARGIN - rl.get_width()) // 2, cy))
            screen.blit(rl, (BOARD_SIZE - BOARD_MARGIN + (BOARD_MARGIN - rl.get_width()) // 2, cy))

        # Subtle inner border
        inner = pygame.Rect(BOARD_MARGIN - 1, BOARD_MARGIN - 1, BOARD_INNER + 2, BOARD_INNER + 2)
        pygame.draw.rect(screen, colors.get("button_border", (140, 105, 70)), inner, width=2)

    # ==================== HIGHLIGHTS ====================
    def draw_highlights(self, screen, selected_square, legal_moves, last_move):
        colors = THEMES[self.current_theme]

        if last_move:
            for sq in (last_move.from_square, last_move.to_square):
                file = chess.square_file(sq)
                rank = 7 - chess.square_rank(sq) if not self.flipped else chess.square_rank(sq)
                x, y = self._sq_to_pixel(file, rank)
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill(colors["last_move"])
                screen.blit(s, (x, y))

        if selected_square is not None:
            file = chess.square_file(selected_square)
            rank = 7 - chess.square_rank(selected_square) if not self.flipped else chess.square_rank(selected_square)
            x, y = self._sq_to_pixel(file, rank)
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill(colors["selected"])
            screen.blit(s, (x, y))

        for move in legal_moves:
            target = move.to_square
            file = chess.square_file(target)
            rank = 7 - chess.square_rank(target) if not self.flipped else chess.square_rank(target)
            x, y = self._sq_to_pixel(file, rank)
            cx = x + SQUARE_SIZE // 2
            cy = y + SQUARE_SIZE // 2
            dot = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(dot, colors.get("move_dot", colors["highlight"]),
                             (SQUARE_SIZE // 2, SQUARE_SIZE // 2), 14)
            screen.blit(dot, (x, y))

    # ==================== PIECES ====================
    def draw_pieces(self, screen, board, selected_square=None, dragging=False, dragged_piece=None, mouse_pos=None):
        for square in chess.SQUARES:
            piece = board.get_piece_at(square)
            if not piece:
                continue
            if dragging and selected_square is not None and square == selected_square:
                continue
            key = ("w" if piece.color == chess.WHITE else "b") + piece.symbol().upper()
            file = chess.square_file(square)
            rank = 7 - chess.square_rank(square) if not self.flipped else chess.square_rank(square)
            px, py = self._sq_to_pixel(file, rank)

            if not self.use_unicode and key in self.piece_images:
                img = self.piece_images[key]
                x = px + (SQUARE_SIZE - img.get_width()) // 2
                y = py + (SQUARE_SIZE - img.get_height()) // 2
                screen.blit(img, (x, y))
            else:
                symbol = self._piece_to_unicode(piece)
                color = (255, 255, 255) if piece.color == chess.WHITE else (0, 0, 0)
                text = PIECE_FONT.render(symbol, True, color)
                x = px + (SQUARE_SIZE - text.get_width()) // 2
                y = py + (SQUARE_SIZE - text.get_height()) // 2
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

    # ==================== BUTTON HELPER ====================
    def _draw_button(self, screen, rect, label, *, colors, filled=True, accent=False):
        if accent:
            bg = colors.get("accent", (218, 175, 100))
            text_color = colors.get("board_border", (42, 28, 18))
        elif filled:
            bg = colors.get("button_bg", (78, 56, 38))
            text_color = colors["text"]
        else:
            bg = colors["panel_bg"]
            text_color = colors["text"]

        pygame.draw.rect(screen, bg, rect, border_radius=12)
        pygame.draw.rect(screen, colors.get("button_border", (140, 105, 70)), rect, width=2, border_radius=12)
        text = TEXT_FONT.render(label, True, text_color)
        screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

    # ==================== SIDE PANEL ====================
    def draw_side_panel(self, screen, board, white_time, black_time, ai_enabled, paused=False):
        colors = THEMES[self.current_theme]
        panel_x = BOARD_SIZE
        panel_w = SIDE_PANEL_WIDTH

        # Panel background with gradient effect
        for i in range(BOARD_SIZE):
            t = i / BOARD_SIZE
            r = int(colors["gradient_top"][0] * (1 - t) + colors["gradient_bot"][0] * t)
            g = int(colors["gradient_top"][1] * (1 - t) + colors["gradient_bot"][1] * t)
            b = int(colors["gradient_top"][2] * (1 - t) + colors["gradient_bot"][2] * t)
            pygame.draw.line(screen, (r, g, b), (panel_x, i), (panel_x + panel_w, i))

        # Separator line
        pygame.draw.line(screen, colors.get("button_border", (140, 105, 70)),
                        (panel_x, 0), (panel_x, BOARD_SIZE), 2)

        # Title
        title = TITLE_FONT.render("CHESSLY", True, colors["accent"])
        tx = panel_x + (panel_w - title.get_width()) // 2
        screen.blit(title, (tx, 18))

        # Subtitle line
        sub_y = 80
        pygame.draw.line(screen, colors.get("button_border", (140, 105, 70)),
                        (panel_x + 20, sub_y), (panel_x + panel_w - 20, sub_y), 1)

        # Info
        y = 95
        turn = board.get_current_turn()
        mode = "VS AI" if ai_enabled else "VS FRIEND"
        info_text = SMALL_FONT.render(f"{mode}  •  {turn}'s turn", True, colors["muted_text"])
        screen.blit(info_text, (panel_x + (panel_w - info_text.get_width()) // 2, y))
        y += 32

        # Timer cards
        card_w = panel_w - 40
        card_h = 80

        def draw_timer_card(rect, name, t, active):
            # Card background
            card_col = colors["panel_card"]
            if active and not paused:
                card_col = tuple(min(255, c + 15) for c in card_col)
            pygame.draw.rect(screen, card_col, rect, border_radius=14)

            # Active border glow
            border_col = colors["accent_glow"] if (active and not paused) else colors.get("button_border", (100, 75, 50))
            pygame.draw.rect(screen, border_col, rect, width=2, border_radius=14)

            # Active indicator dot
            if active and not paused:
                pygame.draw.circle(screen, colors["accent_glow"],
                                 (rect.x + 18, rect.y + rect.h // 2), 5)

            # Name
            name_surf = SMALL_FONT.render(name, True, colors["accent"] if active else colors["muted_text"])
            screen.blit(name_surf, (rect.x + 30, rect.y + 10))

            # Time
            time_text = BIG_FONT.render(self._format_time(t), True, colors["text"])
            screen.blit(time_text, (rect.x + 30, rect.y + 32))

            if paused and active:
                p = SMALL_FONT.render("PAUSED", True, colors["muted_text"])
                screen.blit(p, (rect.right - p.get_width() - 14, rect.y + 12))

        white_rect = pygame.Rect(panel_x + 20, y, card_w, card_h)
        y += card_h + 10
        black_rect = pygame.Rect(panel_x + 20, y, card_w, card_h)
        y += card_h + 14

        active_white = (turn == "White")
        draw_timer_card(white_rect, "♔  White", white_time, active_white)
        draw_timer_card(black_rect, "♚  Black", black_time, not active_white)

        # Captured pieces
        cap_w, cap_b = board.get_captured_pieces()
        if cap_w or cap_b:
            cap_y = y
            cap_label = SMALL_FONT.render("Captured", True, colors["muted_text"])
            screen.blit(cap_label, (panel_x + 20, cap_y))
            cap_y += 24

            # Draw captured piece images
            for i, sym in enumerate(cap_w):
                key = "b" + sym.upper()
                if f"{key}_small" in self.piece_images:
                    screen.blit(self.piece_images[f"{key}_small"], (panel_x + 20 + i * 28, cap_y))
                else:
                    s = SMALL_FONT.render(sym, True, colors["text"])
                    screen.blit(s, (panel_x + 20 + i * 20, cap_y))
            cap_y += 34
            for i, sym in enumerate(cap_b):
                key = "w" + sym.upper()
                if f"{key}_small" in self.piece_images:
                    screen.blit(self.piece_images[f"{key}_small"], (panel_x + 20 + i * 28, cap_y))
                else:
                    s = SMALL_FONT.render(sym, True, colors["text"])
                    screen.blit(s, (panel_x + 20 + i * 20, cap_y))
            y = cap_y + 40

        # Move history
        hist = board.get_move_history()
        if hist:
            sep_y2 = y
            pygame.draw.line(screen, colors.get("button_border", (140, 105, 70)),
                           (panel_x + 20, sep_y2), (panel_x + panel_w - 20, sep_y2), 1)
            y += 8
            hist_label = SMALL_FONT.render("Moves", True, colors["muted_text"])
            screen.blit(hist_label, (panel_x + 20, y))
            y += 24

            # Show last N move pairs that fit
            max_rows = 5
            pairs = []
            for i in range(0, len(hist), 2):
                num = i // 2 + 1
                w_move = hist[i]
                b_move = hist[i + 1] if i + 1 < len(hist) else "..."
                pairs.append(f"{num}. {w_move}  {b_move}")

            visible = pairs[-max_rows:]
            for row_text in visible:
                rt = HISTORY_FONT.render(row_text, True, colors["text"])
                screen.blit(rt, (panel_x + 24, y))
                y += 22
            y += 10

        # Controls - push to bottom
        btn_h = 48
        btn_y = BOARD_SIZE - 20 - btn_h * 2 - 10
        half_w = (card_w - 10) // 2

        pause_rect = pygame.Rect(panel_x + 20, btn_y, half_w, btn_h)
        restart_rect = pygame.Rect(pause_rect.right + 10, btn_y, half_w, btn_h)
        btn_y += btn_h + 10
        quit_rect = pygame.Rect(panel_x + 20, btn_y, card_w, btn_h)

        self._draw_button(screen, pause_rect, "Resume" if paused else "Pause", colors=colors)
        self._draw_button(screen, restart_rect, "Restart", colors=colors)
        self._draw_button(screen, quit_rect, "Quit to Menu", colors=colors, filled=False)

        return {"pause": pause_rect, "restart": restart_rect, "quit": quit_rect}

    # ==================== MENU ====================
    def draw_menu(self, screen):
        colors = THEMES[self.current_theme]
        sw, sh = screen.get_size()

        # Gradient background
        for i in range(sh):
            t = i / sh
            r = int(55 * (1 - t) + 22 * t)
            g = int(38 * (1 - t) + 14 * t)
            b = int(25 * (1 - t) + 8 * t)
            pygame.draw.line(screen, (r, g, b), (0, i), (sw, i))

        cx = sw // 2

        # Decorative chess piece
        crown = PIECE_FONT.render("♔", True, colors.get("accent", (218, 175, 100)))
        screen.blit(crown, (cx - crown.get_width() // 2, 50))

        # Title
        title = TITLE_FONT.render("CHESSLY", True, colors["accent"])
        screen.blit(title, (cx - title.get_width() // 2, 130))

        # Subtitle
        sub = SMALL_FONT.render("A Premium Chess Experience", True, colors["muted_text"])
        screen.blit(sub, (cx - sub.get_width() // 2, 195))

        # Separator
        pygame.draw.line(screen, colors.get("button_border", (140, 105, 70)),
                        (cx - 140, 225), (cx + 140, 225), 1)

        # Time control section
        section_y = 250
        tc_label = SMALL_FONT.render("TIME CONTROL", True, colors["muted_text"])
        screen.blit(tc_label, (cx - tc_label.get_width() // 2, section_y))
        section_y += 30

        card_w = 240
        card_h = 70
        gap = 20
        total_w = card_w * 2 + gap

        blitz_rect = pygame.Rect(cx - total_w // 2, section_y, card_w, card_h)
        rapid_rect = pygame.Rect(blitz_rect.right + gap, section_y, card_w, card_h)

        for rect, key, label, icon in [(blitz_rect, "blitz", "5 MIN BLITZ", "⚡"),
                                        (rapid_rect, "rapid", "10 MIN RAPID", "⏱")]:
            selected = self.selected_time == key
            bg = colors["panel_card"] if not selected else colors.get("button_bg", (78, 56, 38))
            pygame.draw.rect(screen, bg, rect, border_radius=14)
            border = colors["accent"] if selected else colors.get("button_border", (140, 105, 70))
            pygame.draw.rect(screen, border, rect, width=2 if not selected else 3, border_radius=14)
            text_col = colors["accent"] if selected else colors["muted_text"]
            t = TEXT_FONT.render(f"{icon} {label}", True, text_col)
            screen.blit(t, (rect.centerx - t.get_width() // 2, rect.centery - t.get_height() // 2))

        # Opponent section
        section_y += card_h + 30
        op_label = SMALL_FONT.render("OPPONENT", True, colors["muted_text"])
        screen.blit(op_label, (cx - op_label.get_width() // 2, section_y))
        section_y += 30

        friend_rect = pygame.Rect(cx - total_w // 2, section_y, card_w, card_h)
        ai_rect = pygame.Rect(friend_rect.right + gap, section_y, card_w, card_h)

        for rect, key, label, icon in [(friend_rect, "friend", "VS FRIEND", "👥"),
                                        (ai_rect, "ai", "VS AI", "🤖")]:
            selected = self.selected_opponent == key
            bg = colors["panel_card"] if not selected else colors.get("button_bg", (78, 56, 38))
            pygame.draw.rect(screen, bg, rect, border_radius=14)
            border = colors["accent"] if selected else colors.get("button_border", (140, 105, 70))
            pygame.draw.rect(screen, border, rect, width=2 if not selected else 3, border_radius=14)
            text_col = colors["accent"] if selected else colors["muted_text"]
            t = TEXT_FONT.render(f"{icon} {label}", True, text_col)
            screen.blit(t, (rect.centerx - t.get_width() // 2, rect.centery - t.get_height() // 2))

        # Play button
        section_y += card_h + 40
        play_w, play_h = 280, 70
        play_rect = pygame.Rect(cx - play_w // 2, section_y, play_w, play_h)
        self._draw_button(screen, play_rect, "♟  PLAY", colors=colors, accent=True)

        # Footer
        footer = SMALL_FONT.render("Press T to toggle theme  •  F to flip board", True, colors["muted_text"])
        screen.blit(footer, (cx - footer.get_width() // 2, sh - 40))

        # Hit areas
        self.menu_buttons = {
            "time_blitz": blitz_rect,
            "time_rapid": rapid_rect,
            "opp_friend": friend_rect,
            "opp_ai": ai_rect,
            "play": play_rect,
        }
        return self.menu_buttons

    # ==================== GAME OVER ====================
    def draw_game_over(self, screen, result_text):
        colors = THEMES[self.current_theme]
        overlay = pygame.Surface((BOARD_SIZE + SIDE_PANEL_WIDTH, BOARD_SIZE), pygame.SRCALPHA)
        overlay.fill((*colors.get("overlay", (20, 12, 6)), 190))
        screen.blit(overlay, (0, 0))

        cx = (BOARD_SIZE + SIDE_PANEL_WIDTH) // 2

        # Result text with glow
        text = BIG_FONT.render(result_text, True, colors["accent"])
        screen.blit(text, (cx - text.get_width() // 2, 280))

        # Buttons
        btn_w, btn_h = 280, 60
        play_again = pygame.Rect(cx - btn_w // 2, 370, btn_w, btn_h)
        back_menu = pygame.Rect(cx - btn_w // 2, 450, btn_w, btn_h)

        self._draw_button(screen, play_again, "Play Again", colors=colors, accent=True)
        self._draw_button(screen, back_menu, "Back to Menu", colors=colors, filled=False)

        return {"play_again": play_again, "back_menu": back_menu}