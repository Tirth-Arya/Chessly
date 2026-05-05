"""
CHESSLY - Professional Chess Game
board.py - Core chess logic and game state management
This module wraps python-chess to provide a clean, high-level interface.
"""

import chess
from settings import TIME_MODES

class ChessBoard:
    """
    Main chess board class that handles all game rules, moves, and state.
    Uses python-chess internally for perfect rule enforcement.
    """

    def __init__(self):
        """Initialize a new chess game."""
        self.board = chess.Board()          # The actual python-chess board
        self.move_history = []              # List of moves in SAN notation (e.g. "e4", "Nf6")
        self.captured_white = []            # Captured pieces by black (uppercase)
        self.captured_black = []            # Captured pieces by white (lowercase)
        self.last_move = None               # Last move made (for highlighting)

    def reset(self):
        """Start a completely new game."""
        self.board = chess.Board()
        self.move_history.clear()
        self.captured_white.clear()
        self.captured_black.clear()
        self.last_move = None
        print("New game started - White to move")

    def make_move(self, from_square, to_square, promotion=None):
        """
        Attempt to make a move. Returns True if successful.
        Automatically handles promotion, captures, and move history.
        """
        move = chess.Move(from_square, to_square, promotion=promotion)

        # Auto-detect promotion for pawns reaching the last rank
        if (self.board.piece_at(from_square) and
            self.board.piece_at(from_square).piece_type == chess.PAWN and
            chess.square_rank(to_square) in (0, 7)):
            if promotion is None:
                # Default to Queen (most common)
                move.promotion = chess.QUEEN

        if move in self.board.legal_moves:
            # Detect capture before pushing the move
            captured_piece = self.board.piece_at(move.to_square)
            if captured_piece:
                if captured_piece.color == chess.WHITE:
                    self.captured_black.append(captured_piece.symbol())
                else:
                    self.captured_white.append(captured_piece.symbol())

            # SAN must be generated on the pre-move position
            san = self.board.san(move)

            # Push the move
            self.board.push(move)
            self.last_move = move
            self.move_history.append(san)

            return True
        return False

    def get_legal_moves(self, square=None):
        """
        Return list of legal moves.
        If square is given, returns only moves from that square.
        """
        if square is not None:
            return [move for move in self.board.legal_moves if move.from_square == square]
        return list(self.board.legal_moves)

    def is_legal_move(self, from_square, to_square):
        """Check if a specific move is legal."""
        move = chess.Move(from_square, to_square)
        return move in self.board.legal_moves

    def get_piece_at(self, square):
        """Return the piece at a given square (or None)."""
        return self.board.piece_at(square)

    def is_check(self):
        """Is the current player in check?"""
        return self.board.is_check()

    def is_checkmate(self):
        """Is the current player checkmated?"""
        return self.board.is_checkmate()

    def is_stalemate(self):
        """Is the game a stalemate?"""
        return self.board.is_stalemate()

    def is_game_over(self):
        """Is the game finished?"""
        return self.board.is_game_over()

    def get_game_result(self):
        """Return a human-readable game result."""
        if not self.is_game_over():
            return None
        if self.is_checkmate():
            winner = "White" if self.board.turn == chess.BLACK else "Black"
            return f"Checkmate! {winner} wins."
        if self.is_stalemate():
            return "Draw by stalemate."
        if self.board.is_insufficient_material():
            return "Draw - insufficient material."
        return "Game over."

    def get_current_turn(self):
        """Return 'White' or 'Black'."""
        return "White" if self.board.turn == chess.WHITE else "Black"

    def get_move_history(self):
        """Return list of moves in SAN format."""
        return self.move_history[:]

    def get_captured_pieces(self):
        """Return captured pieces for both sides."""
        return self.captured_white, self.captured_black

    def get_last_move(self):
        """Return the last move made (for highlighting)."""
        return self.last_move

    def undo_last_move(self):
        """Undo the last move (useful for 'Take Back' feature)."""
        if self.board.move_stack:
            self.board.pop()
            if self.move_history:
                self.move_history.pop()
            self.last_move = self.board.peek() if self.board.move_stack else None
            return True
        return False

    def get_board_fen(self):
        """Return current board position in FEN notation (for saving/loading)."""
        return self.board.fen()

    def load_from_fen(self, fen):
        """Load a position from FEN string."""
        try:
            self.board = chess.Board(fen)
            self.move_history.clear()
            self.captured_white.clear()
            self.captured_black.clear()
            self.last_move = None
            return True
        except:
            return False

# ====================== Testing the module ======================
if __name__ == "__main__":
    game = ChessBoard()
    print("board.py loaded successfully")
    print(f"Current turn: {game.get_current_turn()}")
    print("Legal moves from e2:", [str(m) for m in game.get_legal_moves(chess.E2)][:5])