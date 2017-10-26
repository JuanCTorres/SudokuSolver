# Sudoku solver

Solve sudokus by representing them as satisfiability problems.

## Run

`python3 solve_sudoku.py [cnf file]`. For instance, `python3 solve_sudoku.py ../files/puzzle1.cnf`

## Generating cnf files

Generate `.cnf` files from `.sud` files by running:

```python3 sudoku2cnf.py [sud file]```
