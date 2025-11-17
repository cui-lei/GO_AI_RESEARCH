# scripts/katago_strong_vs_weak.py
# KataGo strong model vs KataGo weak model on 19x19.

from go_core.board import Board, BLACK, WHITE, PASS_MOVE
from engines.katago_engine import KataGoEngine
from utils.sgf_writer import moves_to_sgf


def main():
    # You will replace these with your actual model and config paths.
    strong_model = "/path/to/katago_strong_model.bin.gz"
    weak_model = "/path/to/katago_weak_model.bin.gz"
    katago_config = "/path/to/gtp_example.cfg"

    engine_black = KataGoEngine(model_path=strong_model, config_path=katago_config)
    engine_white = KataGoEngine(model_path=weak_model, config_path=katago_config)

    board = Board()
    moves = []
    passes = 0
    move_no = 1

    engine_black.on_game_start(board)
    engine_white.on_game_start(board)

    try:
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
            print("Result: Black (strong) wins")
        else:
            print("Result: White (weak) wins")

        sgf = moves_to_sgf(moves, board_size=board.N)
        with open("katago_strong_vs_weak.sgf", "w", encoding="utf-8") as f:
            f.write(sgf)
        print("SGF saved to katago_strong_vs_weak.sgf")
    finally:
        engine_black.close()
        engine_white.close()


if __name__ == "__main__":
    main()
