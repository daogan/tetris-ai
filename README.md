# Tetris AI

A self-playing Tetris.

## Usage

To play the the game interactively: 
```sh
python tetris.py
```
To play the game automatically:
```sh
python tetris_ai.py
```
When playing the game interactively, use the arrow keys to control the tetromino's moving directions (&lt;left&gt;, &lt;right&gt;, &lt;down&gt;) and rotation (&lt;up&gt;), &lt;space&gt; to drop the tetromino straight down, &lt;p&gt; to pause or resume, and &lt;q&gt; to quit the game.

## Implementations

The main idea is simply iterate through all the possible rotations and horizontal positions of a given tetromino, evaluate each result using a heuristic function and choose the one with the highest heuristic score. The heuristic function is based on Pierre Dellacherie’s Algorithm, read more details [here](http://imake.ninja/el-tetris-an-improvement-on-pierre-dellacheries-algorithm/).

We use depth first search in the implementaion, since there are at most two tetrominoes to consider when seaching for the optimal placement, whether to consider the next tetromino or not is a matter of choice and should be easily configured. 
To configure the depth of the DFS search, set `LOOK_AHEAD` to 1 or 2 in `ai_config.py`, if `LOOK_AHEAD` is set to 1, the algorithm would just consider the current tetromino, otherwise, it would take both one into account.

Copyright &copy; 2016 Daogan Ao &lt;wvvwwwvvvv@gmail.com&gt;
