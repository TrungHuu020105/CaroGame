import time
import math
import random
from board import Board
from constants import NEIGHBOR_RADIUS

# simple helper: check neighbor
def has_neighbor(board, r, c, radius=NEIGHBOR_RADIUS):
    for dr in range(-radius, radius+1):
        for dc in range(-radius, radius+1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r+dr, c+dc
            if 0 <= rr < board.size and 0 <= cc < board.size and board.grid[rr][cc] != Board.EMPTY:
                return True
    return False

# generate plausible moves only near existing stones
def generate_moves(board):
    s = board.size
    moves = []
    if not board.any_stone():
        return [(s//2, s//2)]
    for r in range(s):
        for c in range(s):
            if board.grid[r][c] == Board.EMPTY and has_neighbor(board, r, c):
                moves.append((r,c))
    return moves

# pattern-based quick evaluation for one side
def evaluate_simple(board, me):
    # measure rows, cols, diags for patterns; lightweight
    score = 0
    opp = Board.X if me == Board.O else Board.O
    s = board.size
    # rows
    for r in range(s):
        arr = board.grid[r]
        score += line_score(arr, me, opp)
    # cols
    for c in range(s):
        arr = [board.grid[r][c] for r in range(s)]
        score += line_score(arr, me, opp)
    # diagonals
    for k in range(-s+1, s):
        diag = []
        for r in range(s):
            c = r - k
            if 0 <= c < s:
                diag.append(board.grid[r][c])
        if diag:
            score += line_score(diag, me, opp)
    for k in range(2*s):
        diag = []
        for r in range(s):
            c = k - r
            if 0 <= c < s:
                diag.append(board.grid[r][c])
        if diag:
            score += line_score(diag, me, opp)
    return score

def line_score(arr, me, opp):
    # sliding window counting contiguous blocks
    score = 0
    n = len(arr)
    i = 0
    while i < n:
        if arr[i] != me:
            i += 1
            continue
        j = i
        while j < n and arr[j] == me:
            j += 1
        length = j - i
        left_block = (i-1 < 0 or arr[i-1] == opp)
        right_block = (j >= n or arr[j] == opp)
        blocked = left_block + right_block
        if length >= 5:
            return 100000
        if length == 4:
            if blocked == 0: score += 10000
            elif blocked == 1: score += 1000
        elif length == 3:
            if blocked == 0: score += 1000
            elif blocked == 1: score += 100
        elif length == 2:
            if blocked == 0: score += 100
            elif blocked == 1: score += 10
        elif length == 1:
            score += 1
        i = j
    return score

# alpha-beta with iterative deepening and time checks

def alpha_beta(board, depth, alpha, beta, maximizing, me, start_time=None, time_limit=None, win_len=5):
    winner, _ = board.check_win(win_len)
    if winner == me:
        return 10**9, None
    elif winner != 0:
        return -10**9, None
    if depth == 0 or board.is_full():
        v = evaluate_simple(board, me) - evaluate_simple(board, Board.X if me == Board.O else Board.O)
        return v, None
    if start_time is not None and time_limit is not None and time.time() - start_time > time_limit:
        return None, None
    moves = generate_moves(board)
    # ordering
    scored = []
    for m in moves:
        r,c = m
        board.grid[r][c] = me if maximizing else (Board.X if me == Board.O else Board.O)
        s = evaluate_simple(board, me)
        board.grid[r][c] = Board.EMPTY
        scored.append((s,m))
    scored.sort(reverse=True, key=lambda x: x[0])

    best_move = None
    if maximizing:
        value = -10**12
        for _, m in scored:
            r,c = m
            board.set(r,c, me)
            v, _ = alpha_beta(board, depth-1, alpha, beta, False, me, start_time, time_limit, win_len)
            board.unset(r,c)
            if v is None:
                return None, None
            if v > value:
                value = v; best_move = m
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value, best_move
    else:
        value = 10**12
        opp = Board.X if me == Board.O else Board.O
        for _, m in scored:
            r,c = m
            board.set(r,c, opp)
            v, _ = alpha_beta(board, depth-1, alpha, beta, True, me, start_time, time_limit, win_len)
            board.unset(r,c)
            if v is None:
                return None, None
            if v < value:
                value = v; best_move = m
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value, best_move

def iterative_deepening(board, me, max_depth=3, time_limit=1.2, win_len=5):
    start = time.time()
    best = None
    for depth in range(1, max_depth+1):
        v, m = alpha_beta(board, depth, -10**12, 10**12, True, me, start, time_limit, win_len)
        if v is None:
            break
        if m is not None:
            best = m
    return best

def find_best_move(board, me, max_depth=3, time_limit=1.2, win_len=5):
    move = iterative_deepening(board, me, max_depth, time_limit, win_len)
    if move is None:
        # fallback: random empty
        empties = [(r,c) for r in range(board.size) for c in range(board.size) if board.grid[r][c] == Board.EMPTY]
        if empties:
            return random.choice(empties)
    return move
