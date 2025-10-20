import pygame
from board import Board
from ai_alpha_beta import find_best_move
from constants import *

class GameController:
    def __init__(self, size=15, mode='HUMAN_VS_AI', ai_depth=AI_DEFAULT_DEPTH):
        self.size = size
        self.board = Board(size)
        self.mode = mode
        self.current = Board.X
        self.ai_depth = ai_depth
        self.win_len = 3 if size==3 else (4 if size==5 else 5)
        self.ai_thinking = False

    def reset(self, size=None):
        if size:
            self.size = size
            self.win_len = 3 if size==3 else (4 if size==5 else 5)
        self.board.reset(self.size)
        self.current = Board.X
        self.ai_thinking = False

    def human_move(self, r, c):
        if self.board.set(r,c,self.current):
            winner, positions = self.board.check_win(self.win_len)
            if winner:
                return 'WIN', winner, positions
            if self.board.is_full():
                return 'DRAW', None, None
            self.current = Board.O if self.current == Board.X else Board.X
            return 'OK', None, None
        return 'INVALID', None, None

    def ai_move(self):
        self.ai_thinking = True
        mv = find_best_move(self.board.clone(), Board.O, max_depth=self.ai_depth, time_limit=TIME_LIMIT_PER_MOVE, win_len=self.win_len)
        if mv:
            r,c = mv
            self.board.set(r,c, Board.O)
            winner, positions = self.board.check_win(self.win_len)
            self.ai_thinking = False
            if winner:
                return 'WIN', winner, positions
            if self.board.is_full():
                return 'DRAW', None, None
            self.current = Board.X
            return 'OK', None, None
        self.ai_thinking = False
        return 'OK', None, None