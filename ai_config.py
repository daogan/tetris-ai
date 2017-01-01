# coding=utf-8


"""
Tetris AI: A Self-Playing Tetris
Copyright (C) 2016 Daogan Ao <https://github.com/daogan>
Date: 2016-12-27
"""

"""
AI Configurations
"""

# number of tetrominoes to look ahead during the DFS search (should be 1 or 2)
LOOK_AHEAD = 1

# milliseconds
TIMEOUT = 5

# the number of left and right blank columns of each tetromino on a 4x4 grid
LX = (0, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)
RX = (2, 1, 0, 1, 2, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1)

# tetromino height (r, h)
# r: index of the bottom non-blank row; h: height of the tetromino
TH = (
    (2, 2),
    (4, 4), (2, 1),
    (2, 2), (3, 3),
    (2, 2), (3, 3),
    (3, 3), (3, 2), (3, 3), (2, 2),
    (3, 3), (3, 2), (3, 3), (2, 2),
    (3, 3), (3, 2), (3, 3), (2, 2)
)

# coefficients of the heuristic function
(A, B, C, D, E, F) = (
    -4.500158825082766, 3.4181268101392694, -3.2178882868487753,
    -9.348695305445199, -7.899265427351652, -3.3855972247263626)
