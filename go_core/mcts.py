# go_core/mcts.py
# Pure MCTS (no neural network) for Go, using the Board implementation.

import math
import random
from typing import Optional

from .board import Board, BLACK, WHITE, PASS_MOVE


def ucb1(child, c_puct: float = 1.4) -> float:
    """UCB1 / PUCT-style score for child selection."""
    if child.N == 0:
        return float("inf")
    return child.W / child.N + c_puct * math.sqrt(
        math.log(child.parent.N + 1) / child.N
    )


class MCTSNode:
    """Node in the MCTS tree."""

    __slots__ = ("parent", "move", "player_to_move", "N", "W", "children", "untried")

    def __init__(self, parent, move, player_to_move, board: Board):
        self.parent = parent
        self.move = move  # move that led to this node
        self.player_to_move = player_to_move
        self.N = 0
        self.W = 0.0
        self.children = []
        # We store legal moves at node creation time
        self.untried = board.legal_moves()


class MCTS:
    """Simple MCTS that works on the Board class without any neural network."""

    def __init__(self, sims: int = 800, c_puct: float = 1.4, rollout_limit: int = 300):
        self.sims = sims
        self.c_puct = c_puct
        self.rollout_limit = rollout_limit

    def choose(self, board: Board):
        """Run simulations and return the best move for the current player."""
        root = MCTSNode(None, None, board.to_play, board)

        for _ in range(self.sims):
            self._simulate(board.copy(), root)

        if not root.children:
            return PASS_MOVE
        # Choose the child with the highest visit count
        best_child = max(root.children, key=lambda ch: ch.N)
        return best_child.move

    def _simulate(self, board: Board, node: MCTSNode) -> None:
        # Selection
        cur = node
        while not cur.untried and cur.children:
            cur = max(cur.children, key=lambda ch: ucb1(ch, self.c_puct))
            board.play(cur.move)

        # Expansion
        if cur.untried:
            move = random.choice(cur.untried)
            cur.untried.remove(move)
            board.play(move)
            child = MCTSNode(cur, move, board.to_play, board)
            cur.children.append(child)
            cur = child

        # Rollout until two consecutive passes or rollout_limit
        winner = self._rollout(board)

        # Backpropagation, value from BLACK's perspective
        if winner == 0:
            value = 0.0
        else:
            value = 1.0 if winner == BLACK else -1.0

        while cur is not None:
            cur.N += 1
            if cur.player_to_move == BLACK:
                cur.W += value
            else:
                cur.W -= value
            cur = cur.parent

    def _rollout(self, board: Board) -> int:
        passes = 0
        steps = 0
        while passes < 2 and steps < self.rollout_limit:
            moves = board.legal_moves()
            non_pass = [m for m in moves if m is not PASS_MOVE]
            if non_pass:
                move = random.choice(non_pass)
            else:
                move = PASS_MOVE
            board.play(move)
            passes = passes + 1 if move is PASS_MOVE else 0
            steps += 1

        black_score, white_score = board.score_tromp_taylor(komi=7.5)
        if abs(black_score - white_score) < 1e-6:
            return 0  # draw
        return BLACK if black_score > white_score else WHITE
