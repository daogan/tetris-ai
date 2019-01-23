#!/usr/bin/python
# coding=utf-8


"""
Terminal Tetris
Copyright (C) 2016 Daogan Ao <https://github.com/daogan>
Date: 2016-12-25
"""


import time
import curses
import random

from tetris_config import *


class Tetris(object):

    def __init__(self, autoboot=True):

        random.seed(time.time())

        self.board = [[EMPTY]*WIDTH for i in range(HEIGHT)]
        self.tetromino = self.random_tetromino()
        self.next_tetromino = self.random_tetromino()
        self.pos_y = START_Y
        self.pos_x = START_X
        self.running = True
        self.pause = False
        self.game_over = False
        self.n_fills = [0] * HEIGHT
        self.timeout = TIMEOUT
        self.last_pause = time.time()
        self.prev_time = 0

        self.lines = 0
        self.score = 0
        self.level = 0
        self.time = 0

        self.init_curses()

        self.autoboot = autoboot
        if self.autoboot:
            self.play()

    def init_curses(self):

        curses.initscr()
        curses.noecho()
        curses.curs_set(0)

        self.init_colors()

        self.gamewin = curses.newwin(HEIGHT+3,
                                     len(BLKSTR)*WIDTH+2*len(VBSTR)+1,
                                     WIN_Y, WIN_X)
        self.gamewin.timeout(self.timeout)
        self.gamewin.keypad(1)
        # self.gamewin.border(0)

        self.infowin = curses.newwin(HEIGHT, 20, IWIN_Y, IWIN_X)
        # self.infowin.border(0)

    def init_colors(self):

        curses.start_color()
        curses.use_default_colors()

        colors = (
            0, curses.COLOR_RED, curses.COLOR_GREEN, curses.COLOR_YELLOW,
            curses.COLOR_BLUE, curses.COLOR_MAGENTA, curses.COLOR_CYAN, 13,
        )
        for i, bg in enumerate(colors):
            # init_pair(number, foreground, background)
            curses.init_pair(i, curses.COLOR_WHITE, bg)

        # border color
        curses.init_pair(8, 10, 2)
        # text color
        curses.init_pair(9, curses.COLOR_MAGENTA, -1)
        curses.init_pair(10, curses.COLOR_CYAN, -1)
        curses.init_pair(11, curses.COLOR_RED, -1)

        self.colors = [curses.color_pair(i) for i in range(12)]
        for i in range(12):
            self.colors[i] |= curses.A_BOLD

    def play(self):

        while self.running:

            self.handle_keyboard()

            if self.pause:
                continue

            if not self.move(DOWN):
                if self.pos_y == START_Y:
                    self.die()
                else:
                    self.collide()
                    n_lines = self.clear_lines()
                    self.scoring(n_lines)
                    self.spawn_next()

            if not self.game_over:
                self.render()

        self.finish()

    def handle_keyboard(self):

        event = self.gamewin.getch()

        if self.game_over and event != -1:
            self.running = False
            return

        if self.pause and event != PAUSE and event != QUIT:
            return

        if event == QUIT:
            self.running = False
        elif event == PAUSE:
            self.pause = not self.pause
            self.last_pause = time.time()
            if self.pause:
                self.prev_time = self.time
        elif event == DROP:
            self.drop()
        elif event in [LEFT, RIGHT, DOWN, ROTATE]:
            self.move(event)

        if not self.pause:
            self.time = time.time() - self.last_pause + self.prev_time

    def collide(self):
        """
        Current tetromino touches with ground or other occupied cells.
        """

        for _y, _x in TETROMINOS[self.tetromino]:
            y = self.pos_y + _y
            self.board[y][self.pos_x+_x] = COLORS[self.tetromino]
            # remember the number of filled cells at row board[y]
            self.n_fills[y] += 1

    def clear_lines(self):
        """
        Clear the fully filled lines on the board.
        """

        n_lines = 0
        dst = 0
        # only check for lines near the last landing position
        for i in range(4):
            y = self.pos_y + i
            if y >= HEIGHT:
                break
            if self.n_fills[y] == WIDTH:
                n_lines += 1
                dst = y

        src = dst - 1
        while src >= 0:
            while self.n_fills[src] == WIDTH:
                src -= 1
            # skip copying if both src and dst rows are empty
            if self.n_fills[dst] > 0 or self.n_fills[src] > 0:
                self.n_fills[dst] = self.n_fills[src]
                self.board[dst] = self.board[src][:]
            dst -= 1
            src -= 1

        for i in range(n_lines):
            self.n_fills[i] = 0
            for j in range(WIDTH):
                self.board[i][j] = EMPTY

        return n_lines

    def scoring(self, n_lines):
        """
        Update score, level and other game properties.
        """

        if n_lines == 0:
            return

        scales = [0, 1, 2, 4, 8]

        self.lines += n_lines
        self.score += scales[n_lines] * LINE_SCORE

        level = int(self.score / LEVEL_SCORE)
        if level > self.level:
            self.level = level

            # since machines are too dumb to perceive the fun of decreasing
            # timeout as humans do, we keep timeout constant if we are
            # under AI-playing mode.
            if not self.autoboot:
                return

            # decrease timeout
            next_timeout = self.timeout - DEC_TIME
            if next_timeout < MIN_TIMEOUT:
                next_timeout = MIN_TIMEOUT

            if self.timeout != next_timeout:
                self.set_timeout(next_timeout)

    def set_timeout(self, timeout):

        self.timeout = timeout
        self.gamewin.timeout(timeout)

    def spawn_next(self):

        self.tetromino = self.next_tetromino
        self.next_tetromino = self.random_tetromino()
        self.pos_y = START_Y
        self.pos_x = START_X

    def random_tetromino(self):
        """
        Generate a random sequence of tetromino pieces.
        """

        return random.choice(PIECES)

    def move(self, action):

        y = self.pos_y
        x = self.pos_x
        tetromino = self.tetromino

        if action == DOWN:
            y += 1
        elif action == LEFT:
            x -= 1
        elif action == RIGHT:
            x += 1
        elif action == ROTATE:
            tetromino = NEXT[tetromino]

        return self.try_move(y, x, tetromino)

    def try_move(self, y, x, tetromino):

        if self.valid_at(y, x, tetromino):
            self.pos_y = y
            self.pos_x = x
            self.tetromino = tetromino
            return True
        else:
            return False

    def valid_at(self, y, x, tetromino):
        """
        Check if it is valid to place the tetromino at board[y][x].
        """

        for _y, _x in TETROMINOS[tetromino]:
            by = y + _y
            bx = x + _x
            if by >= HEIGHT or by < 0 or bx < 0 or bx >= WIDTH:
                return False
            if self.board[by][bx] != EMPTY:
                return False

        return True

    def die(self):

        self.game_over = True
        self.pause = True

        istr = 'Game Over!'
        x = OFFSET_X + ((len(BLKSTR)*WIDTH - len(istr)) >> 1)
        self.gamewin.addstr(HEIGHT+2, x, istr, self.colors[11])

    def finish(self):

        curses.endwin()

    def drop(self):
        """
        Drop the tetromino straight down.
        """

        last_y = self.pos_y
        dropping = True
        while dropping:
            for _y, _x in TETROMINOS[self.tetromino]:
                y = self.pos_y + _y + 1
                if y >= HEIGHT or self.board[y][self.pos_x+_x] != EMPTY:
                    dropping = False
                    break

            if dropping:
                self.pos_y += 1

        return self.pos_y > last_y

    def trans(self, y, x):
        """
        Translate board coordinates to game UI coordinates.
        """

        ty = OFFSET_Y + y
        tx = OFFSET_X + len(BLKSTR)*x

        return ty, tx

    def render(self):
        """
        Draw the game GUI.
        """

        self.gamewin.clear()
        self.draw_border()
        # self.gamewin.border(0)

        # draw the game board
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.board[y][x] != EMPTY:
                    color = self.colors[self.board[y][x]]
                    ty, tx = self.trans(y, x)
                    self.gamewin.addstr(ty, tx, BLKSTR, color)

        # draw current tetromino
        # color = curses.color_pair(COLORS[self.tetromino])
        color = self.colors[COLORS[self.tetromino]]
        for y, x in TETROMINOS[self.tetromino]:
            ty, tx = self.trans(self.pos_y+y, self.pos_x+x)
            self.gamewin.addstr(ty, tx, BLKSTR, color)

        self.draw_info()
        self.gamewin.refresh()

    def draw_border(self):
        """
        Draw horizontal and vertical borders of the game board.
        """

        color = self.colors[8]

        hrz_border = HBSTR * (len(VBSTR)*2 + len(BLKSTR)*WIDTH)
        self.gamewin.addstr(0, 0, hrz_border, color)
        self.gamewin.addstr(HEIGHT+1, 0, hrz_border, color)

        for i in range(HEIGHT):
            self.gamewin.addstr(i+1, 0, VBSTR, color)
            self.gamewin.addstr(i+1, len(BLKSTR)*WIDTH+len(VBSTR),
                                VBSTR, color)

    def draw_info(self):
        """
        Dispaly next tetromino and playing statistics.
        """

        self.infowin.clear()
        # self.infowin.border(0)

        # draw next tetromino
        color = self.colors[COLORS[self.next_tetromino]]
        for y, x in TETROMINOS[self.next_tetromino]:
            self.infowin.addstr(y+1, len(BLKSTR)*x+IOFF_X, BLKSTR, color)

        m, s = divmod(int(self.time), 60)
        h, m = divmod(m, 60)
        timestr = '%02d:%02d:%02d' % (h, m, s)

        headers = ['Time', 'Level', 'Score', 'Lines']
        values = [timestr, self.level, self.score, self.lines]

        for i in range(len(headers)):
            y = HEIGHT - 3 * i - 1
            self.infowin.addstr(y-1, IOFF_X, headers[i], self.colors[9])
            self.infowin.addstr(y, IOFF_X, str(values[i]), self.colors[10])

        self.infowin.refresh()


if __name__ == '__main__':

    Tetris()
