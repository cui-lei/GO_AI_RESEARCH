# utils/sgf_writer.py
# Minimal SGF writer for logging games.

from typing import List, Tuple, Optional

from go_core.board import BLACK, WHITE, PASS_MOVE, COL_LABELS


def coord_to_sgf(r: int, c: int, board_size: int) -> str:
    """
    Convert (row, col) to SGF coordinate: 'aa', 'dd', etc.
    Top-left is 'aa'.
    """
    # SGF uses 'a'.. for both axes
    return chr(ord("a") + c) + chr(ord("a") + (board_size - 1 - r))


def moves_to_sgf(
    moves: List[Tuple[int, Optional[Tuple[int, int]]]], board_size: int = 19
) -> str:
    """
    Convert a list of (player, move) to a simple SGF string.
    player: BLACK or WHITE
    move: (r, c) or PASS_MOVE
    """
    header = f"(;GM[1]FF[4]SZ[{board_size}]CA[UTF-8]\n"
    body_parts = []
    for player, move in moves:
        color = "B" if player == BLACK else "W"
        if move is PASS_MOVE:
            body_parts.append(f";{color}[]")
        else:
            r, c = move
            sgf_coord = coord_to_sgf(r, c, board_size)
            body_parts.append(f";{color}[{sgf_coord}]")
    body = "".join(body_parts)
    return header + body + ")\n"
