"""
CHESSLY - Professional Chess Game
settings.py - All configuration, colors, paths, and constants
This file keeps the project clean and easy to customize.
"""

import os
import pygame

# ====================== WINDOW & BOARD SETTINGS ======================
BOARD_SIZE = 800                    # Board is always 800x800
SIDE_PANEL_WIDTH = 340              # Extra space for timer, history, buttons
WINDOW_WIDTH = BOARD_SIZE + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = BOARD_SIZE

SQUARE_SIZE = BOARD_SIZE // 8       # 100px per square

# ====================== THEMES (Modern & Beautiful) ======================
THEMES = {
    "light": {
        "name": "Black & White",
        "bg":           (245, 245, 245),
        "light_square": (236, 236, 236),
        "dark_square":  (32, 32, 32),
        "panel_bg":     (250, 250, 250),
        "panel_card":   (240, 240, 240),
        "button_bg":    (235, 235, 235),
        "button_border":(40, 40, 40),
        "accent":       (20, 20, 20),
        "text":         (20, 20, 20),
        "muted_text":   (90, 90, 90),
        "overlay":      (0, 0, 0),
        "highlight":    (0, 0, 0, 70),
        "last_move":    (0, 0, 0, 55),
        "selected":     (0, 0, 0, 120)
    },
    "dark": {
        "name": "Black & White (Dark)",
        "bg":           (16, 16, 16),
        "light_square": (210, 210, 210),
        "dark_square":  (20, 20, 20),
        "panel_bg":     (14, 14, 14),
        "panel_card":   (24, 24, 24),
        "button_bg":    (22, 22, 22),
        "button_border":(200, 200, 200),
        "accent":       (235, 235, 235),
        "text":         (235, 235, 235),
        "muted_text":   (170, 170, 170),
        "overlay":      (0, 0, 0),
        "highlight":    (255, 255, 255, 55),
        "last_move":    (255, 255, 255, 45),
        "selected":     (255, 255, 255, 95)
    }
}

DEFAULT_THEME = "light"

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
TITLE_FONT = pygame.font.SysFont("Arial", 68, bold=True)
BIG_FONT = pygame.font.SysFont("Arial", 42, bold=True)
TEXT_FONT = pygame.font.SysFont("Arial", 28)
SMALL_FONT = pygame.font.SysFont("Arial", 20)
PIECE_FONT = pygame.font.SysFont("Segoe UI Symbol", 72)   # Unicode fallback

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