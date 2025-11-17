# engines/baseline_mcts_engine.py
# Baseline MCTS engine using the pure Python MCTS implementation.

from go_core.board import Board
from go_core.mcts import MCTS
from .base_engine import GoEngine


class BaselineMCTSEngine(GoEngine):
    """Baseline engine: pure MCTS, no neural network, CPU-friendly."""

    def __init__(self, simulations: int = 800):
        self.simulations = simulations
        self.mcts = MCTS(sims=simulations)

    def name(self) -> str:
        return f"Baseline-MCTS-{self.simulations}"

    def genmove(self, board: Board):
        return self.mcts.choose(board)
