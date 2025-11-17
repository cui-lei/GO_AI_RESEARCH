# scripts/human_vs_baseline.py
# Human vs baseline MCTS engine on a 19x19 board.

import sys

from go_core.board import Board, BLACK, WHITE, PASS_MOVE
from engines.baseline_mcts_engine import BaselineMCTSEngine


def human_move(board: Board):
    while True:
        s = input("Your move (e.g., D4, PASS, or QUIT): ").strip()
        if s.lower() in ("quit", "exit"):
            return "QUIT"
        mv = board.from_coord(s)
        if mv is None or not board.is_legal(mv):
            print("Illegal move. Try again.")
            continue
        return mv


def main():
    color = "black"
    sims = 800

    if len(sys.argv) >= 2:
        color = sys.argv[1]
    if len(sys.argv) >= 3:
        sims = int(sys.argv[2])

    human_color = BLACK if color.lower().startswith("b") else WHITE
    ai = BaselineMCTSEngine(simulations=sims)
    board = Board()

    print(
        f"\n19x19 Go (Tromp–Taylor, komi=7.5). "
        f"Human plays {'BLACK ●' if human_color == BLACK else 'WHITE ○'}.\n"
    )
    board.show()

    passes = 0
    while True:
        if board.to_play == human_color:
            mv = human_move(board)
            if mv == "QUIT":
                print("Game aborted.")
                return
        else:
            print(f"{ai.name()} thinking...")
            mv = ai.genmove(board)
            if mv is PASS_MOVE:
                print("AI plays PASS.")
            else:
                print(f"AI plays {board.to_coord(*mv)}.")

        board.play(mv)
        board.show()

        passes = passes + 1 if mv is PASS_MOVE else 0
        if passes >= 2:
            bs, ws = board.score_tromp_taylor(komi=7.5)
            print(f"Final Score — Black: {bs:.1f}, White: {ws:.1f} (komi 7.5)")
            if abs(bs - ws) < 1e-6:
                print("Result: Draw")
            elif bs > ws:
                print("Result: Black wins")
            else:
                print("Result: White wins")
            break


if __name__ == "__main__":
    main()
