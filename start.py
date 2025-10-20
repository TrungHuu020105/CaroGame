import pygame
import sys
import os
from constants import *
from game import GameController
from board import Board

ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

# helper to load image if exists
def load_asset(name):
    p = os.path.join(ASSET_DIR, name)
    if os.path.exists(p):
        return pygame.image.load(p).convert_alpha()
    return None

class UI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption('Caro Game - Full')
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.Font(None, 56)
        self.font_med = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)

        # assets
        self.bg_img = load_asset('background.png')
        self.img_X = load_asset('X.png')
        self.img_O = load_asset('O.png')

        # initial UI state
        self.state = 'MENU'  # MENU or PLAY
        self.selected_size = 15
        self.mode = 'HUMAN_VS_AI'
        self.ai_depth = AI_DEFAULT_DEPTH
        self.game = None

    def draw_menu(self):
        if self.bg_img:
            self.screen.blit(pygame.transform.smoothscale(self.bg_img, (WINDOW_W, WINDOW_H)), (0,0))
        else:
            self.screen.fill(LIGHT_BG)
        title = self.font_big.render('CARO GAME', True, TEXT_COLOR)
        self.screen.blit(title, (RIGHT_PANEL_X-60, 40))

        # size buttons
        sizes = [3,5,10,15]
        y = 140
        for s in sizes:
            rect = pygame.Rect(RIGHT_PANEL_X, y, 140, 40)
            color = (200,255,200) if s==self.selected_size else (240,240,240)
            pygame.draw.rect(self.screen, color, rect)
            t = self.font_med.render(f'{s} x {s}', True, TEXT_COLOR)
            self.screen.blit(t, (RIGHT_PANEL_X+20, y+6))
            y += 60

        # mode toggle
        rect_mode = pygame.Rect(RIGHT_PANEL_X, y, 180, 40)
        pygame.draw.rect(self.screen, (245,245,255), rect_mode)
        t = self.font_med.render('Human vs AI' if self.mode=='HUMAN_VS_AI' else 'Human vs Human', True, TEXT_COLOR)
        self.screen.blit(t, (RIGHT_PANEL_X+8, y+6))
        y += 80

        # AI depth
        txt = self.font_small.render(f'AI depth: {self.ai_depth}', True, TEXT_COLOR)
        self.screen.blit(txt, (RIGHT_PANEL_X, y))

        # Start button
        rect_start = pygame.Rect(RIGHT_PANEL_X+20, y+40, 120, 44)
        pygame.draw.rect(self.screen, BUTTON_COLOR, rect_start)
        t2 = self.font_med.render('Start', True, BUTTON_TEXT)
        self.screen.blit(t2, (RIGHT_PANEL_X+40, y+52))

        # store clickable areas
        self.menu_areas = {'sizes': [], 'mode': rect_mode, 'start': rect_start}
        y2 = 140
        for s in sizes:
            self.menu_areas['sizes'].append((pygame.Rect(RIGHT_PANEL_X, y2, 140, 40), s))
            y2 += 60

    def draw_game(self):
        # background
        if self.bg_img:
            self.screen.blit(pygame.transform.smoothscale(self.bg_img, (WINDOW_W, WINDOW_H)), (0,0))
        else:
            self.screen.fill(LIGHT_BG)
        # board area
        board_rect = pygame.Rect(LEFT_MARGIN, TOP_MARGIN, BOARD_AREA, BOARD_AREA)
        pygame.draw.rect(self.screen, (255,252,240), board_rect)
        cell = BOARD_AREA // self.game.size
        # grid lines
        for i in range(self.game.size+1):
            x = LEFT_MARGIN + i*cell
            pygame.draw.line(self.screen, GRID_COLOR, (x, TOP_MARGIN), (x, TOP_MARGIN+BOARD_AREA), 1)
            y = TOP_MARGIN + i*cell
            pygame.draw.line(self.screen, GRID_COLOR, (LEFT_MARGIN, y), (LEFT_MARGIN+BOARD_AREA, y), 1)
        # pieces
        for r in range(self.game.size):
            for c in range(self.game.size):
                v = self.game.board.grid[r][c]
                if v == Board.EMPTY:
                    continue
                cx = LEFT_MARGIN + c*cell + cell//2
                cy = TOP_MARGIN + r*cell + cell//2
                if v == Board.X:
                    if self.img_X:
                        img = pygame.transform.smoothscale(self.img_X, (cell-8, cell-8))
                        rect = img.get_rect(center=(cx,cy))
                        self.screen.blit(img, rect)
                    else:
                        pygame.draw.line(self.screen, (60,60,60), (cx-12,cy-12),(cx+12,cy+12),3)
                        pygame.draw.line(self.screen, (60,60,60), (cx-12,cy+12),(cx+12,cy-12),3)
                else:
                    if self.img_O:
                        img = pygame.transform.smoothscale(self.img_O, (cell-8, cell-8))
                        rect = img.get_rect(center=(cx,cy))
                        self.screen.blit(img, rect)
                    else:
                        pygame.draw.circle(self.screen, (255,105,180), (cx,cy), cell//2 - 6, 4)
        # highlight win
        if self.game.board.win_positions:
            for (r,c) in self.game.board.win_positions:
                rect = pygame.Rect(LEFT_MARGIN + c*cell, TOP_MARGIN + r*cell, cell, cell)
                s = pygame.Surface((cell,cell), pygame.SRCALPHA)
                s.fill((255,180,120,90))
                self.screen.blit(s, rect.topleft)

        # right panel info
        tx = RIGHT_PANEL_X
        ty = TOP_MARGIN
        title = self.font_big.render('CARO GAME', True, TEXT_COLOR)
        self.screen.blit(title, (tx, ty))
        ty += 80
        mode_txt = 'Human vs AI' if self.game.mode=='HUMAN_VS_AI' else 'Human vs Human'
        self.screen.blit(self.font_med.render(mode_txt, True, TEXT_COLOR), (tx, ty))
        ty += 40
        self.screen.blit(self.font_small.render(f'Board: {self.game.size}x{self.game.size}', True, TEXT_COLOR), (tx, ty))
        ty += 30
        self.screen.blit(self.font_small.render(f'AI depth: {self.ai_depth}', True, TEXT_COLOR), (tx, ty))
        ty += 40
        # buttons: replay, menu
        self.replay_button = pygame.Rect(tx, ty, 140, 44)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.replay_button)
        self.screen.blit(self.font_med.render('Replay', True, BUTTON_TEXT), (tx+28, ty+8))
        ty += 64
        self.menu_button = pygame.Rect(tx, ty, 140, 44)
        pygame.draw.rect(self.screen, (230,230,230), self.menu_button)
        self.screen.blit(self.font_med.render('Main Menu', True, TEXT_COLOR), (tx+12, ty+8))
        # status
        ty += 80
        cp = 'X' if self.game.current==Board.X else 'O'
        stat = f'Turn: {cp}' + ( ' (AI thinking...)' if self.game.ai_thinking else '')
        self.screen.blit(self.font_med.render(stat, True, TEXT_COLOR), (tx, ty))
        # win/draw
        winner, pos = self.game.board.check_win(self.game.win_len)
        if winner:
            wt = 'X wins!' if winner==Board.X else 'O wins!'
            self.screen.blit(self.font_big.render(wt, True, (200,40,40)), (tx, ty+80))
        elif self.game.board.is_full():
            self.screen.blit(self.font_big.render('Draw', True, (120,120,120)), (tx, ty+80))

    def handle_menu_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button==1:
            mx,my = ev.pos
            # sizes
            for rect,s in self.menu_areas['sizes']:
                if rect.collidepoint((mx,my)):
                    self.selected_size = s
                    return
            # mode
            if self.menu_areas['mode'].collidepoint((mx,my)):
                self.mode = 'HUMAN_VS_HUMAN' if self.mode=='HUMAN_VS_AI' else 'HUMAN_VS_AI'
                return
            # start
            if self.menu_areas['start'].collidepoint((mx,my)):
                # start
                self.game = GameController(self.selected_size, self.mode, self.ai_depth)
                self.state = 'PLAY'
                return

    def handle_game_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button==1:
            mx,my = ev.pos
            # check right panel buttons
            if hasattr(self,'replay_button') and self.replay_button.collidepoint((mx,my)):
                self.game.reset(self.game.size)
                return
            if hasattr(self,'menu_button') and self.menu_button.collidepoint((mx,my)):
                self.state = 'MENU'
                return
            # board click
            cell = BOARD_AREA // self.game.size
            if LEFT_MARGIN <= mx < LEFT_MARGIN + BOARD_AREA and TOP_MARGIN <= my < TOP_MARGIN + BOARD_AREA:
                c = (mx - LEFT_MARGIN) // cell
                r = (my - TOP_MARGIN) // cell
                if 0 <= r < self.game.size and 0 <= c < self.game.size:
                    res, winner, pos = self.game.human_move(r,c)
                    if res == 'OK' and self.game.mode=='HUMAN_VS_AI' and self.game.current==Board.O:
                        # AI move (blocking main thread but with small visualization)
                        pygame.display.flip()
                        pygame.event.pump()
                        res2, w2, p2 = self.game.ai_move()

    def run(self):
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if self.state=='MENU':
                    self.handle_menu_event(ev)
                else:
                    self.handle_game_event(ev)
            if self.state=='MENU':
                self.draw_menu()
            else:
                self.draw_game()
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == '__main__':
    ui = UI()
    ui.run()