# scripts/ai_vs_ai_baseline.py
# Baseline MCTS vs Baseline MCTS on 19x19 board.

import sys

from go_core.board import Board, BLACK, WHITE, PASS_MOVE
from engines.baseline_mcts_engine import BaselineMCTSEngine
from utils.sgf_writer import moves_to_sgf


def main():
    sims_black = 800
    sims_white = 800

    if len(sys.argv) >= 2:
        sims_black = int(sys.argv[1])
    if len(sys.argv) >= 3:
        sims_white = int(sys.argv[2])

    engine_black = BaselineMCTSEngine(simulations=sims_black)
    engine_white = BaselineMCTSEngine(simulations=sims_white)

    board = Board()
    moves = []
    passes = 0
    move_no = 1

    while passes < 2:
        engine = engine_black if board.to_play == BLACK else engine_white
        mv = engine.genmove(board)
        board.play(mv)

        color_char = "B" if board.to_play == WHITE else "W"
        if mv is PASS_MOVE:
            print(f"{move_no:03d} {color_char}: PASS")
        else:
            print(f"{move_no:03d} {color_char}: {board.to_coord(*mv)}")

        moves.append((BLACK if color_char == "B" else WHITE, mv))
        move_no += 1
        passes = passes + 1 if mv is PASS_MOVE else 0

    bs, ws = board.score_tromp_taylor(komi=7.5)
    print(f"Final Score — Black: {bs:.1f}, White: {ws:.1f} (komi 7.5)")
    if abs(bs - ws) < 1e-6:
        print("Result: Draw")
    elif bs > ws:
        print("Result: Black wins")
    else:
        print("Result: White wins")

    sgf = moves_to_sgf(moves, board_size=board.N)
    with open("baseline_vs_baseline.sgf", "w", encoding="utf-8") as f:
        f.write(sgf)
    print("SGF saved to baseline_vs_baseline.sgf")


if __name__ == "__main__":
    main()
