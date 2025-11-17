# engines/base_engine.py
# Base class for Go engines.

from abc import ABC, abstractmethod
from typing import Any

from go_core.board import Board


class GoEngine(ABC):
    """Abstract base class for any Go engine."""

    @abstractmethod
    def name(self) -> str:
        """Return a human-readable name of the engine."""
        raise NotImplementedError

    @abstractmethod
    def genmove(self, board: Board):
        """Generate a move for the current player on the given board."""
        raise NotImplementedError

    def on_game_start(self, board: Board) -> None:
        """Optional hook called at the beginning of a game."""
        pass

    def on_game_end(self, board: Board, result: Any) -> None:
        """Optional hook called at the end of a game."""
        pass
