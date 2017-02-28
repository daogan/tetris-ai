#!/usr/bin/python
# coding=utf-8


"""
Tetris AI: A Self-playing Tetris
Copyright (C) 2016 Daogan Ao <https://github.com/daogan>
Date: 2016-12-27
"""


import time

from tetris import Tetris
from ai_config import *
from tetris_config import START_X, START_Y, LEFT, RIGHT, DOWN, ROTATE,\
        DROP, NEXT, WIDTH, HEIGHT, EMPTY


class TetrisAI(object):

    def __init__(self):

        self.tetro_queue = [0, 0]
        # for tracking the optimal rotation and dropping position
        self.max_score = 0
        self.n_rotations = 0
        self.dropping_x = START_X
        # for tracking the states of the search queue
        self.tetro_rots = [0] * LOOK_AHEAD
        self.tetros = [0] * LOOK_AHEAD
        self.tetro_xs = [0] * LOOK_AHEAD

    def play(self, tetris):

        tetris.set_timeout(TIMEOUT)

        while tetris.running:

            tetris.handle_keyboard()

            if tetris.pause:
                continue

            self.init_states(tetris)

            self.search(tetris, level=0, score=0)
            actions = self.get_actions()

            for action in actions:
                if action == DROP:
                    tetris.drop()
                else:
                    tetris.move(action)

                tetris.render()
                time.sleep(tetris.timeout/1000.0)

            n_lines = 0
            if not tetris.move(DOWN):
                if tetris.pos_y == START_Y:
                    tetris.die()
                else:
                    tetris.collide()
                    n_lines = tetris.clear_lines()
                    tetris.scoring(n_lines)
                    tetris.spawn_next()

            if n_lines > 0:
                tetris.render()

        tetris.finish()

    def search(self, tetris, level, score):
        """
        Depth first search, recursively search for the optimal action sequence
        with the highest score.
        """

        # we have reached the stopping condition of the recursive search
        if level == LOOK_AHEAD:
            if score > self.max_score:
                self.max_score = score
                self.n_rotations = self.tetro_rots[0]
                self.dropping_x = self.tetro_xs[0]
            return

        # reset to START_Y in deeper search levels
        if level > 0:
            tetris.pos_y = START_Y
        # remember the initial tetris states
        t_tetrimino = tetris.tetromino
        t_pos_y = tetris.pos_y
        t_pos_x = tetris.pos_x

        current = self.tetro_queue[level]

        for rotation, tetro in enumerate(self.each(current)):
            self.tetro_rots[level] = rotation
            self.tetros[level] = tetro
            for pos_x in self.range_x(tetro):
                self.tetro_xs[level] = pos_x

                # since the board (and some other internal variables) is
                # shared and modified during the recursive search, we need
                # to remember the current board states for later restoration
                t_board = [row[:] for row in tetris.board]
                t_n_fills = tetris.n_fills[:]

                tetris.tetromino = tetro
                tetris.pos_x = pos_x

                tetris.drop()
                tetris.collide()

                nscore = self.heuristic(tetris)

                self.search(tetris, level+1, score+nscore)

                # restore previous context
                tetris.board = t_board
                tetris.n_fills = t_n_fills
                tetris.pos_y = t_pos_y

        # restore the initial tetris states after the search
        tetris.tetromino = t_tetrimino
        tetris.pos_x = t_pos_x

    def each(self, tetro):
        """
        Return all rotated pieces of a given tetromino.
        """

        yield tetro
        current = tetro
        tetro = NEXT[tetro]

        # stop when rotated back to the original tetromino
        while tetro != current:
            yield tetro
            # make a rotation
            tetro = NEXT[tetro]

    def range_x(self, tetro):
        """
        Return the range of the left and right-most horizontal position
        current tetromino can travel on the board.
        """

        # range: [s, e)
        return range(-LX[tetro], WIDTH-4+RX[tetro]+1)

    def heuristic(self, tetris):
        """
        Evaluate the score of current board.

        This scoring heuristic is base on the Pierre Dellacheries algorithm,
        read more details at:
        ielashi.com/el-tetris-an-improvement-on-pierre-dellacheries-algorithm

        TODO: Experiment with different or more sophisticated heuristics.
        """

        landing_y = tetris.pos_y
        row_trans, col_trans = self.get_transitions(tetris.board)
        n_holes = self.get_holes(tetris.board)
        wells_height = self.get_wells_height(tetris.board)
        n_lines = tetris.clear_lines()
        # n_lines = len([i for i in tetris.n_fills if i == WIDTH])

        t = tetris.tetromino
        landing_height = HEIGHT - landing_y - TH[t][0] + 0.5*TH[t][1]

        score = A*landing_height + B*n_lines + C*row_trans
        score += D*col_trans + E*n_holes + F*wells_height

        return score

    def get_actions(self):

        actions = [ROTATE] * self.n_rotations
        steps = self.dropping_x - START_X
        if steps > 0:
            actions += [RIGHT] * steps
        elif steps < 0:
            actions += [LEFT] * (0 - steps)

        # append final drop
        return actions + [DROP]

    def init_states(self, tetris):

        self.max_score = -(1 << 30)
        self.tetro_queue[0] = tetris.tetromino
        self.tetro_queue[1] = tetris.next_tetromino

    def get_holes(self, board):
        """
        Get the total number of holes in the board.
        """

        holes = 0
        for x in range(WIDTH):
            occuppied = False
            for y in range(HEIGHT):
                if board[y][x] != EMPTY:
                    if not occuppied:
                        occuppied = True
                elif occuppied:
                    holes += 1

        return holes

    def get_transitions(self, board):
        """
        Get the total number of row and column transitions.

        A row transition occurs when a filled cell is adjacent to an empty
        cell on the same row and vice versa. The outer regions of the board
        are considered to be filled.

        example:

            0011101001  ==> row transitions is 6
           ^ ^  ^^^ ^
            1111100000  ==> row transitions is 2
                ^    ^
        """

        row_trans = 0
        for y in range(HEIGHT):
            filled = True
            for x in range(WIDTH):
                if filled != (board[y][x] != EMPTY):
                    row_trans += 1
                    filled = not filled

            if not filled:
                row_trans += 1

        col_trans = 0
        for x in range(WIDTH):
            filled = True
            for y in range(HEIGHT):
                if filled != (board[y][x] != EMPTY):
                    col_trans += 1
                    filled = not filled

            if not filled:
                col_trans += 1

        return row_trans, col_trans

    def get_wells_height(self, board):
        """
        Get the total wells height.

        A well is a sequence of consecutive empty cells on the same column
        where the top empty cell is surrounded by filled cells or border of
        the board.
        For a well of depth n, the height is defined as 1 + 2 + ... + n,
        this gives more panalty to deeper wells.
        """

        wells_height = 0
        for x in range(1, WIDTH-1):
            for y in range(HEIGHT):
                if board[y][x] == EMPTY and board[y][x-1] != EMPTY \
                        and board[y][x+1] != EMPTY:
                    wells_height += 1
                    for _y in range(y+1, HEIGHT):
                        if board[_y][x] != EMPTY:
                            break
                        wells_height += 1

        for y in range(HEIGHT):
            # check wells in the leftmost boarder of the board
            if board[y][0] == EMPTY and board[y][1] != EMPTY:
                wells_height += 1
                for _y in range(y+1, HEIGHT):
                    if board[_y][x] != EMPTY:
                        break
                    wells_height += 1

            # check wells in the rightmost border of the board
            if board[y][WIDTH-1] == EMPTY and board[y][WIDTH-2] != EMPTY:
                wells_height += 1
                for _y in range(y+1, HEIGHT):
                    if board[_y][x] != EMPTY:
                        break
                    wells_height += 1

        return wells_height


if __name__ == '__main__':

    tetris = Tetris(autoboot=False)
    ai = TetrisAI()
    ai.play(tetris)
