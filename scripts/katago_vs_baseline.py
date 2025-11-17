# scripts/katago_vs_baseline.py
# KataGo vs Baseline MCTS on 19x19.

from go_core.board import Board, BLACK, WHITE, PASS_MOVE
from engines.katago_engine import KataGoEngine
from engines.baseline_mcts_engine import BaselineMCTSEngine
from utils.sgf_writer import moves_to_sgf


def main():
    strong_model = "/path/to/katago_strong_model.bin.gz"
    katago_config = "/path/to/gtp_example.cfg"

    katago = KataGoEngine(model_path=strong_model, config_path=katago_config)
    baseline = BaselineMCTSEngine(simulations=800)

    # Example: KataGo plays White, Baseline plays Black
    board = Board()
    moves = []
    passes = 0
    move_no = 1

    katago.on_game_start(board)

    try:
        while passes < 2:
            if board.to_play == BLACK:
                engine = baseline
            else:
                engine = katago

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
            print("Result: Black (Baseline) wins")
        else:
            print("Result: White (KataGo) wins")

        sgf = moves_to_sgf(moves, board_size=board.N)
        with open("katago_vs_baseline.sgf", "w", encoding="utf-8") as f:
            f.write(sgf)
        print("SGF saved to katago_vs_baseline.sgf")
    finally:
        katago.close()


if __name__ == "__main__":
    main()
