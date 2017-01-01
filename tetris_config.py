# coding=utf-8


"""
Terminal Tetris
Copyright (C) 2016 Daogan Ao <https://github.com/daogan>
Date: 2016-12-25
"""

"""
Game Configurations
"""

WIDTH = 10
HEIGHT = 20

# milliseconds
TIMEOUT = 800
MIN_TIMEOUT = 200
DEC_TIME = int((TIMEOUT-MIN_TIMEOUT)/10)

LINE_SCORE = 100
LEVEL_SCORE = 20 * LINE_SCORE

# string representing a single block in a tetromino
BLKSTR = '[]'
# vertical border
VBSTR = '||'
# horizontal border
HBSTR = '='
EMPTY = 0

WIN_X = 4
WIN_Y = 1
OFFSET_X = len(VBSTR)
OFFSET_Y = 1
# initial position when a new tetromino is spawned
START_X = (WIDTH - 4) >> 1
START_Y = 0

# information window properties
IWIN_X = WIN_X + len(BLKSTR) * (WIDTH + 2) + 1
IWIN_Y = WIN_Y + 1
IOFF_X = 1

# controlling signals
DOWN = 258
ROTATE = 259
LEFT = 260
RIGHT = 261
DROP = ord(' ')
PAUSE = ord('p')
QUIT = ord('q')

"""
    the tetromino pattern sequence (on a 4x4 grid):

    oo..    ..o.    ....    oo..    .o..    .oo.    o...
    oo..    ..o.    oooo    .oo.    oo..    oo..    oo..
    ....    ..o.    ....    ....    o...    ....    .o..
    ....    ..o.    ....    ....    ....    ....    ....

    .oo.    ....    .o..    o...    .o..    ....    oo..
    .o..    ooo.    .o..    ooo.    .o..    ooo.    .o..
    .o..    ..o.    oo..    ....    .oo.    o...    .o..
    ....    ....    ....    ....    ....    ....    ....

    ..o.    .o..    ....    .o..    .o..
    ooo.    .oo.    ooo.    oo..    ooo.
    ....    .o..    .o..    .o..    ....
    ....    ....    ....    ....    ....

"""

# the coordinates of each tetromino, represented as (y, x) on a 4x4 grid,
# a slight simplification of the Super Rotation System (SRS), read more at:
# http://tetris.wikia.com/wiki/SRS
TETROMINOS = (
    ((0, 0), (0, 1), (1, 0), (1, 1)),

    ((0, 2), (1, 2), (2, 2), (3, 2)),
    ((1, 0), (1, 1), (1, 2), (1, 3)),

    ((0, 0), (0, 1), (1, 1), (1, 2)),
    ((0, 1), (1, 0), (1, 1), (2, 0)),

    ((0, 1), (0, 2), (1, 0), (1, 1)),
    ((0, 0), (1, 0), (1, 1), (2, 1)),

    ((0, 1), (0, 2), (1, 1), (2, 1)),
    ((1, 0), (1, 1), (1, 2), (2, 2)),
    ((0, 1), (1, 1), (2, 0), (2, 1)),
    ((0, 0), (1, 0), (1, 1), (1, 2)),

    ((0, 1), (1, 1), (2, 1), (2, 2)),
    ((1, 0), (1, 1), (1, 2), (2, 0)),
    ((0, 0), (0, 1), (1, 1), (2, 1)),
    ((0, 2), (1, 0), (1, 1), (1, 2)),

    ((0, 1), (1, 1), (1, 2), (2, 1)),
    ((1, 0), (1, 1), (1, 2), (2, 1)),
    ((0, 1), (1, 0), (1, 1), (2, 1)),
    ((0, 1), (1, 0), (1, 1), (1, 2))
)

# index chain to get the rotated tetromino
#       0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18
NEXT = (0, 2, 1, 4, 3, 6, 5, 8, 9, 10, 7, 12, 13, 14, 11, 16, 17, 18, 15)

# colors of different tetrominoes
COLORS = (1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7)

# rearrange the probability of each tetromino
PIECES = (0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18)
# PIECES = (
#     0, 0, 0, 0,
#     1, 2, 1, 2,
#     3, 4, 3, 4,
#     5, 6, 5, 6,
#     7, 8, 9, 10,
#     11, 12, 13, 14,
#     15, 16, 17, 18
# )

# def print_tetrominoes():
#
#     tetrominoes = []
#     for coords in TETROMINO:
#         tetromino = [['.']*4 for i in range(4)]
#         for y, x in coords:
#             tetromino[y][x] = 'o'
#         tetrominoes.append(tetromino)
#
#     sep = ' ' * 4
#     for s, e in [(0, 7), (7, 14), (14, 19)]:
#         rows = [[''.join(t[i]) for t in tetrominoes[s:e]] for i in range(4)]
#         for i in range(4):
#             print(sep + sep.join(rows[i]))
#         print()
