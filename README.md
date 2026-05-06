# ♟️ Chessly - Professional Chess Game


[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.6.0-%2312b3b3)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A beautiful, fully-featured chess game built with **Pygame** and **python-chess**. Features Stockfish AI, timers, themes, real chess pieces, and a polished modern UI.

![Chessly Gameplay](screenshots/gameplay.png)
![Main Menu](screenshots/menu.png)

## ✨ Features

- **Realistic Chess Pieces** — High-quality Lichess PNG assets (auto-downloaded)
- **Smart AI Opponent** — Real Stockfish engine with difficulty levels
- **Game Modes**:
  - 5-minute Blitz
  - 10-minute Rapid
- **Two Play Modes**:
  - Play vs AI
  - Play vs Friend (hotseat)
- **Modern UI**:
  - Light & Dark themes
  - Smooth drag & drop + click-to-move
  - Legal move highlights
  - Last move indicator
- **Board Flip** — Play as Black with flipped board
- **Timers** with real-time countdown
- **Sound Effects** — Move, capture, check, checkmate
- **Full-screen support** (F11)
- **Professional modular architecture**

## 🎮 How to Play

1. Clone the repository
2. Run `pip install -r requirements.txt`
3. Place `stockfish.exe` (Windows) or `stockfish` binary in the project root (optional but recommended for AI)
4. Run `python main.py`

**Controls:**
- Mouse: Drag pieces or click to select + click destination
- **F11** — Toggle fullscreen
- **F** — Flip board
- **T** — Switch theme

## 🛠️ Tech Stack

- **Python 3.8+**
- **Pygame** — Game development & rendering
- **python-chess** — Complete chess rules engine
- **Stockfish** — Grandmaster-level AI
- Clean, modular OOP architecture

## 📁 Project Structure

- `main.py` — Game loop and state management
- `board.py` — Chess logic wrapper
- `ui.py` — All rendering and visual feedback
- `engine.py` — Stockfish AI integration
- `settings.py` — Configuration and themes

## 🚀 Future Improvements

- Online multiplayer (via WebSocket)
- Move annotations and game analysis
- Custom sound pack
- Save/load games (PGN format)
- Difficulty slider with ELO estimation
- Piece move animations

## 📄 License

This project is licensed under the MIT License — feel free to use it for learning or your own projects.

---

**Made with ❤️ for showcasing clean Python game development skills**