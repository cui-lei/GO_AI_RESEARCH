# go_core/board.py
# 19x19 Go rules with Tromp–Taylor scoring (stones + surrounded territory).

from typing import List, Tuple, Optional, Set, Dict

BOARD_SIZE = 19
EMPTY, BLACK, WHITE = 0, 1, 2
PASS_MOVE = None

# Standard Go coordinates skip the letter 'I'
COL_LABELS = "ABCDEFGHJKLMNOPQRST"
COL_TO_IDX = {c: i for i, c in enumerate(COL_LABELS)}


def opponent(player: int) -> int:
    return BLACK if player == WHITE else WHITE


class Board:
    """Go board with basic rules, simple ko and Tromp–Taylor scoring."""

    def __init__(self, size: int = BOARD_SIZE):
        self.N: int = size
        self.b: List[List[int]] = [[EMPTY] * size for _ in range(size)]
        self.to_play: int = BLACK
        self.history: List[Tuple] = []  # hashes for simple ko
        self.captured: Dict[int, int] = {BLACK: 0, WHITE: 0}
        self.ko: Optional[Tuple[int, int]] = None

    def copy(self) -> "Board":
        nb = Board(self.N)
        nb.b = [row[:] for row in self.b]
        nb.to_play = self.to_play
        nb.history = self.history[:]
        nb.captured = self.captured.copy()
        nb.ko = self.ko
        return nb

    # ------------- basic utilities -------------

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.N and 0 <= c < self.N

    def neighbors(self, r: int, c: int):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if self.in_bounds(nr, nc):
                yield nr, nc

    # ------------- group + liberties -------------

    def _group(self, r: int, c: int) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """Return (stones, liberties) of the connected group at (r, c)."""
        color = self.b[r][c]
        assert color != EMPTY
        q = [(r, c)]
        stones: Set[Tuple[int, int]] = {(r, c)}
        libs: Set[Tuple[int, int]] = set()
        while q:
            x, y = q.pop()
            for nx, ny in self.neighbors(x, y):
                v = self.b[nx][ny]
                if v == EMPTY:
                    libs.add((nx, ny))
                elif v == color and (nx, ny) not in stones:
                    stones.add((nx, ny))
                    q.append((nx, ny))
        return stones, libs

    # ------------- legality check -------------

    def is_legal(self, move) -> bool:
        """Check if a move is legal, including simple ko and suicide."""
        if move is PASS_MOVE:
            return True
        r, c = move
        if not self.in_bounds(r, c) or self.b[r][c] != EMPTY:
            return False
        if self.ko == (r, c):
            return False

        # Try the move on a copy of the board
        tmp = self.copy()
        tmp._place(r, c, tmp.to_play)
        captured = tmp._capture_neighbors(r, c, tmp.to_play)

        # Suicide check: the new group must have liberties or capture something
        stones, libs = tmp._group(r, c)
        if len(libs) == 0 and captured == 0:
            return False

        # Simple superko: avoid repeating the immediately previous position
        if tmp._hash() in self.history[-1:]:
            return False
        return True

    def _place(self, r: int, c: int, player: int) -> None:
        self.b[r][c] = player

    def _capture_neighbors(self, r: int, c: int, player: int) -> int:
        """Capture opponent groups that lose all liberties after (r, c)."""
        cap = 0
        opp = opponent(player)
        checked = set()
        for nx, ny in self.neighbors(r, c):
            if (nx, ny) in checked:
                continue
            checked.add((nx, ny))
            if self.b[nx][ny] == opp:
                stones, libs = self._group(nx, ny)
                if len(libs) == 0:
                    for sx, sy in stones:
                        self.b[sx][sy] = EMPTY
                    self.captured[player] += len(stones)
                    cap += len(stones)
        return cap

    # ------------- playing moves -------------

    def play(self, move) -> bool:
        """Apply a move; return False if illegal."""
        if not self.is_legal(move):
            return False

        prev_hash = self._hash()
        self.ko = None

        # Pass move
        if move is PASS_MOVE:
            self.to_play = opponent(self.to_play)
            self.history.append(self._hash())
            return True

        r, c = move
        self._place(r, c, self.to_play)
        cap = self._capture_neighbors(r, c, self.to_play)

        # Simple ko detection
        if cap == 1:
            stones, libs = self._group(r, c)
            if len(libs) == 1:
                (kr, kc) = next(iter(libs))
                if self._hash() != prev_hash:
                    self.ko = (kr, kc)

        self.to_play = opponent(self.to_play)
        self.history.append(self._hash())
        return True

    def legal_moves(self):
        moves = []
        for r in range(self.N):
            for c in range(self.N):
                if self.is_legal((r, c)):
                    moves.append((r, c))
        moves.append(PASS_MOVE)
        return moves

    def _hash(self):
        # Simple hash representation: board state + player to move
        return tuple(tuple(row) for row in self.b), self.to_play

    # ------------- scoring (Tromp–Taylor) -------------

    def score_tromp_taylor(self, komi: float = 7.5):
        """Return (black_score, white_score) using Tromp–Taylor area scoring."""
        visited: Set[Tuple[int, int]] = set()
        black_area = 0
        white_area = 0

        for r in range(self.N):
            for c in range(self.N):
                v = self.b[r][c]
                if v == BLACK:
                    black_area += 1
                elif v == WHITE:
                    white_area += 1
                elif v == EMPTY and (r, c) not in visited:
                    region, owners = self._empty_region_owners(r, c, visited)
                    if owners == {BLACK}:
                        black_area += len(region)
                    elif owners == {WHITE}:
                        white_area += len(region)
                    # Mixed owners = neutral points

        black_score = black_area
        white_score = white_area + komi
        return black_score, white_score

    def _empty_region_owners(
        self, r: int, c: int, visited: Set[Tuple[int, int]]
    ) -> Tuple[Set[Tuple[int, int]], Set[int]]:
        q = [(r, c)]
        region: Set[Tuple[int, int]] = {(r, c)}
        visited.add((r, c))
        owners: Set[int] = set()

        while q:
            x, y = q.pop()
            for nx, ny in self.neighbors(x, y):
                v = self.b[nx][ny]
                if v == EMPTY and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    region.add((nx, ny))
                    q.append((nx, ny))
                elif v in (BLACK, WHITE):
                    owners.add(v)
        return region, owners

    # ------------- coordinate conversion & display -------------

    def to_coord(self, r: int, c: int) -> str:
        """Convert (row, col) to human Go coordinate, e.g., 'D4'."""
        return f"{COL_LABELS[c]}{self.N - r}"

    def from_coord(self, s: str):
        """Convert coordinate like 'D4' or 'PASS' to internal move."""
        s = s.strip().upper()
        if s in ("PASS", ""):
            return PASS_MOVE
        if len(s) < 2:
            return None
        col = s[0]
        try:
            row = int(s[1:])
        except ValueError:
            return None
        if col not in COL_LABELS or not (1 <= row <= self.N):
            return None
        return self.N - row, COL_TO_IDX[col]

    def show(self) -> None:
        """Print the board in a human-friendly ASCII form."""
        print("\n   " + " ".join(COL_LABELS[: self.N]))
        for r in range(self.N):
            row_str = []
            for c in range(self.N):
                v = self.b[r][c]
                if v == EMPTY:
                    row_str.append("·")
                elif v == BLACK:
                    row_str.append("●")
                else:
                    row_str.append("○")
            label = f"{self.N - r:2d}"
            print(f"{label} " + " ".join(row_str) + f" {label}")
        print("   " + " ".join(COL_LABELS[: self.N]) + "\n")
