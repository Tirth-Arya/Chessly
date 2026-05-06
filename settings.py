"""
CHESSLY - Professional Chess Game
settings.py - All configuration, colors, paths, and constants
This file keeps the project clean and easy to customize.
"""

import os
import pygame

# ====================== WINDOW & BOARD SETTINGS ======================
BOARD_MARGIN = 32                   # Margin for coordinate labels (a-h, 1-8)
SQUARE_SIZE = 88                    # Pixels per square
BOARD_INNER = SQUARE_SIZE * 8       # Inner board area (704px)
BOARD_SIZE = BOARD_INNER + 2 * BOARD_MARGIN  # Total board area with margins (768px)
SIDE_PANEL_WIDTH = 360              # Extra space for timer, history, buttons
WINDOW_WIDTH = BOARD_SIZE + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = BOARD_SIZE

# ====================== THEMES (Warm Wood) ======================
THEMES = {
    "wood": {
        "name": "Classic Wood",
        "bg":             (62, 43, 30),        # Dark walnut background
        "light_square":   (240, 217, 181),      # #F0D9B5 - cream/birch
        "dark_square":    (181, 136, 99),        # #B58863 - warm brown oak
        "board_border":   (42, 28, 18),          # Very dark walnut frame
        "coord_text":     (210, 185, 150),       # Warm tan for coordinates
        "coord_bg":       (52, 36, 24),          # Slightly lighter than border
        "panel_bg":       (45, 32, 22),          # Dark walnut panel
        "panel_card":     (62, 45, 32),          # Slightly lighter card
        "button_bg":      (78, 56, 38),          # Warm brown button
        "button_hover":   (95, 68, 45),          # Lighter brown hover
        "button_border":  (140, 105, 70),        # Tan border
        "accent":         (218, 175, 100),       # Warm gold accent
        "accent_glow":    (255, 210, 130),       # Brighter gold for active
        "text":           (235, 220, 198),       # Warm cream text
        "muted_text":     (160, 138, 110),       # Muted tan
        "overlay":        (20, 12, 6),           # Very dark overlay
        "highlight":      (218, 175, 100, 100),  # Gold highlight for legal moves
        "last_move":      (205, 170, 80, 80),    # Amber last-move highlight
        "selected":       (255, 210, 80, 130),   # Bright gold selected
        "check_tint":     (200, 50, 50, 90),     # Red tint for check
        "move_dot":       (120, 90, 55, 160),    # Subtle brown dot for legal moves
        "gradient_top":   (70, 50, 32),          # Panel gradient top
        "gradient_bot":   (38, 26, 16),          # Panel gradient bottom
    },
    "wood_dark": {
        "name": "Dark Mahogany",
        "bg":             (30, 18, 10),
        "light_square":   (212, 167, 106),       # #D4A76A - golden oak
        "dark_square":    (107, 58, 42),          # #6B3A2A - dark mahogany
        "board_border":   (22, 12, 6),
        "coord_text":     (180, 150, 110),
        "coord_bg":       (28, 16, 8),
        "panel_bg":       (25, 15, 8),
        "panel_card":     (40, 26, 16),
        "button_bg":      (55, 36, 22),
        "button_hover":   (72, 48, 30),
        "button_border":  (120, 85, 50),
        "accent":         (200, 160, 85),
        "accent_glow":    (240, 195, 110),
        "text":           (220, 200, 175),
        "muted_text":     (140, 115, 85),
        "overlay":        (10, 5, 2),
        "highlight":      (200, 160, 85, 100),
        "last_move":      (190, 150, 65, 80),
        "selected":       (240, 195, 65, 130),
        "check_tint":     (180, 40, 40, 90),
        "move_dot":       (100, 75, 45, 160),
        "gradient_top":   (40, 26, 14),
        "gradient_bot":   (18, 10, 4),
    }
}

DEFAULT_THEME = "wood"

# ====================== GAME MODES ======================
TIME_MODES = {
    "blitz": 300,      # 5 minutes
    "rapid": 600       # 10 minutes
}

# ====================== PATHS ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "pieces")

STOCKFISH_PATH = os.path.join(BASE_DIR, "stockfish.exe" if os.name == "nt" else "stockfish")

# ====================== FONTS ======================
pygame.font.init()

# Try premium fonts, fall back gracefully
def _load_font(names, size, bold=False):
    """Try multiple font names, return first available."""
    for name in names:
        font = pygame.font.SysFont(name, size, bold=bold)
        if font:
            return font
    return pygame.font.SysFont(None, size, bold=bold)

TITLE_FONT   = _load_font(["Georgia", "Palatino", "Times New Roman", "Arial"], 62, bold=True)
BIG_FONT      = _load_font(["Georgia", "Palatino", "Arial"], 38, bold=True)
TEXT_FONT     = _load_font(["Segoe UI", "Calibri", "Arial"], 26)
SMALL_FONT    = _load_font(["Segoe UI", "Calibri", "Arial"], 19)
COORD_FONT    = _load_font(["Segoe UI", "Calibri", "Arial"], 15, bold=True)
PIECE_FONT    = pygame.font.SysFont("Segoe UI Symbol", 66)   # Unicode fallback
HISTORY_FONT  = _load_font(["Consolas", "Courier New", "monospace"], 18)

# ====================== SOUND FREQUENCIES (generated) ======================
SOUND_CONFIG = {
    # Softer, lower-frequency, shorter cues (further shaped in main.py)
    "move":    {"freq": 440, "duration": 0.11},
    "capture": {"freq": 330, "duration": 0.16},
    "check":   {"freq": 554, "duration": 0.18},
    "mate":    {"freq": 220, "duration": 0.32},
    "promote": {"freq": 659, "duration": 0.15}
}

# Master volume for generated UI sounds (0.0 .. 1.0)
SOUND_MASTER_VOLUME = 0.10

# ====================== OTHER SETTINGS ======================
FPS = 60
DRAG_SCALE = 1.1                    # Make dragged piece slightly bigger

print("settings.py loaded successfully")