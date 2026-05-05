"""
CHESSLY - Professional Chess Game
engine.py - Stockfish AI integration with difficulty levels
This module handles the computer opponent intelligently.
"""

import chess
import chess.engine
import os
from settings import STOCKFISH_PATH

class ChessEngine:
    """
    Manages the Stockfish chess engine.
    Provides difficulty levels and best-move calculation.
    """

    def __init__(self):
        self.engine = None
        self.loaded = False
        self.difficulty = "Medium"          # Default difficulty
        self.skill_level = 15               # Stockfish skill (0-20)
        self.search_depth = 12              # Default search depth

        # Load Stockfish on startup
        self._load_stockfish()

    def _load_stockfish(self):
        """Try to load the Stockfish executable."""
        if os.path.exists(STOCKFISH_PATH):
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
                self.loaded = True
                print("Stockfish engine loaded successfully.")
                self.set_difficulty(self.difficulty)   # Apply default difficulty
            except Exception as e:
                print(f"Failed to start Stockfish: {e}")
                self.loaded = False
        else:
            print(f"Stockfish not found at: {STOCKFISH_PATH}")
            print("AI will be disabled. Place stockfish.exe (or stockfish) in the Chessly folder.")
            self.loaded = False

    def set_difficulty(self, level: str):
        """
        Set AI difficulty.
        Easy   → very weak
        Medium → balanced
        Hard   → strong (near grandmaster level)
        """
        self.difficulty = level

        if not self.loaded:
            return

        if level == "Easy":
            self.skill_level = 5
            self.search_depth = 8
        elif level == "Medium":
            self.skill_level = 15
            self.search_depth = 12
        elif level == "Hard":
            self.skill_level = 20
            self.search_depth = 18

        # Apply settings to Stockfish
        try:
            self.engine.configure({"Skill Level": self.skill_level})
            print(f"AI difficulty set to {level} (Skill: {self.skill_level}, Depth: {self.search_depth})")
        except:
            pass

    def get_best_move(self, board: chess.Board, time_limit=1.0):
        """
        Returns the best move according to Stockfish.
        Returns None if engine is not loaded.
        """
        if not self.loaded or board.is_game_over():
            return None

        try:
            # Use a combination of time limit and depth for stable performance
            result = self.engine.play(
                board,
                chess.engine.Limit(time=time_limit, depth=self.search_depth)
            )
            return result.move
        except Exception as e:
            print(f"AI move error: {e}")
            return None

    def quit(self):
        """Properly shut down the engine when the game exits."""
        if self.loaded and self.engine:
            self.engine.quit()
            self.loaded = False
            print("Stockfish engine closed cleanly.")

    def is_ready(self):
        """Check if AI is available."""
        return self.loaded


# ====================== Testing the module ======================
if __name__ == "__main__":
    ai = ChessEngine()
    print(f"AI ready: {ai.is_ready()}")
    print(f"Current difficulty: {ai.difficulty}")