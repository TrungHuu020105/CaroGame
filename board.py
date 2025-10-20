import math

class Board:
    EMPTY = 0
    X = 1
    O = 2

    def __init__(self, size=15):
        self.size = size
        self.grid = [[Board.EMPTY for _ in range(size)] for _ in range(size)]
        self.last_move = None
        self.win_positions = None

    def reset(self, size=None):
        if size is not None:
            self.size = size
        self.grid = [[Board.EMPTY for _ in range(self.size)] for _ in range(self.size)]
        self.last_move = None
        self.win_positions = None

    def in_bounds(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def set(self, r, c, val):
        if not self.in_bounds(r,c):
            return False
        if self.grid[r][c] != Board.EMPTY:
            return False
        self.grid[r][c] = val
        self.last_move = (r,c)
        return True

    def unset(self, r, c):
        if self.in_bounds(r,c):
            self.grid[r][c] = Board.EMPTY

    def is_full(self):
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == Board.EMPTY:
                    return False
        return True

    def check_win(self, win_len=5):
        # returns (winner_val, winning_positions) or (0, None)
        dirs = [(1,0),(0,1),(1,1),(1,-1)]
        for r in range(self.size):
            for c in range(self.size):
                v = self.grid[r][c]
                if v == Board.EMPTY:
                    continue
                for dr,dc in dirs:
                    positions = [(r,c)]
                    nr, nc = r+dr, c+dc
                    while self.in_bounds(nr,nc) and self.grid[nr][nc] == v:
                        positions.append((nr,nc))
                        nr += dr; nc += dc
                    if len(positions) >= win_len:
                        self.win_positions = positions[:win_len]
                        return v, self.win_positions
        return 0, None

    def clone(self):
        b = Board(self.size)
        for r in range(self.size):
            for c in range(self.size):
                b.grid[r][c] = self.grid[r][c]
        b.last_move = self.last_move
        b.win_positions = None
        return b

    def any_stone(self):
        return any(self.grid[r][c] != Board.EMPTY for r in range(self.size) for c in range(self.size))
