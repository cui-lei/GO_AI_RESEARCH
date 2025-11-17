# engines/elf_engine.py
# ELF OpenGo adapter. Uses heuristic fallback if the native module is not available.

import os
import sys
from typing import Optional

from go_core.board import Board, PASS_MOVE, BLACK, WHITE
from .base_engine import GoEngine


class ELFOpenGoEngine(GoEngine):
    """
    Adapter for ELF OpenGo.

    This class assumes that the ELF OpenGo inference module
    (_elfgames_go_inference) has been built and is importable.
    If it is not available, the engine gracefully falls back to a simple
    heuristic engine so that the rest of the framework still works.
    """

    def __init__(self):
        # You can adjust these paths to match your ELF build.
        sys.path.insert(0, "/home/ubuntu/ELF/build/elf")
        sys.path.insert(0, "/home/ubuntu/ELF/build/elfgames/go")

        os.environ.setdefault(
            "LD_PRELOAD",
            "/usr/lib/x86_64-linux-gnu/libtbb.so.12:"
            "/usr/lib/x86_64-linux-gnu/libtbbmalloc.so.2",
        )

        self.go_module = None
        self.context_opts = None
        self.game_opts = None

        try:
            import _elfgames_go_inference as go_inf

            self.go_module = go_inf
            self.context_opts = go_inf.ContextOptions()
            self.context_opts.num_games = 1
            self.context_opts.batchsize = 1

            self.game_opts = go_inf.GameOptions()
            self.game_opts.following_pass = True
            print("ELF OpenGo engine initialized successfully.")
        except Exception as e:
            print(f"[ELFOpenGoEngine] Failed to import ELF OpenGo module: {e}")
            print("[ELFOpenGoEngine] Falling back to heuristic policy.")
            self.go_module = None

    def name(self) -> str:
        return "ELF-OpenGo" if self.go_module else "ELF-heuristic-fallback"

    def genmove(self, board: Board):
        if self.go_module is None:
            return self._heuristic_move(board)

        # NOTE:
        # A full implementation would:
        # 1) Convert the Board object into ELF feature planes.
        # 2) Call the ELF inference API to get policy/value.
        # 3) Optionally run an internal MCTS guided by the policy/value.
        # 4) Map the chosen move back to (row, col).
        #
        # Here we keep a placeholder and reuse a heuristic move
        # to keep the engine usable even before full integration.
        return self._heuristic_move(board)

    def _heuristic_move(self, board: Board):
        """Simple heuristic: prefer 4-4, then side, then center, then any move."""
        N = board.N
        priority_moves = []

        # 4-4 points
        candidates = [
            (3, 3),
            (3, N - 4),
            (N - 4, 3),
            (N - 4, N - 4),
        ]
        priority_moves.extend(candidates)

        # Star points near the center (for 19x19)
        if N == 19:
            star = 9
            candidates = [
                (3, star),
                (star, 3),
                (star, N - 4),
                (N - 4, star),
                (star, star),
            ]
            priority_moves.extend(candidates)

        for r, c in priority_moves:
            if 0 <= r < N and 0 <= c < N and board.is_legal((r, c)):
                return (r, c)

        # Fallback: choose the first legal non-pass move
        for r in range(N):
            for c in range(N):
                if board.is_legal((r, c)):
                    return (r, c)

        return PASS_MOVE
