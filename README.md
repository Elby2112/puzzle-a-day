# 🧩 Puzzle-A-Day Solver

A solver for the **DragonFjord A-Puzzle-A-Day** physical puzzle, built in Python with a React frontend.

## What is this puzzle?

A-Puzzle-A-Day is a physical puzzle where you have a 7×7 board (with some cells removed) and 8 uniquely shaped pieces. Every day of the year, you must place all 8 pieces on the board leaving only the current **month** and **day** cells exposed.

## The Board

```
[ Jan ][ Feb ][ Mar ][ Apr ][ May ][ Jun ][ --- ]
[ Jul ][ Aug ][ Sep ][ Oct ][ Nov ][ Dec ][ --- ]
[  1  ][  2  ][  3  ][  4  ][  5  ][  6  ][  7  ]
[  8  ][  9  ][ 10  ][ 11  ][ 12  ][ 13  ][ 14  ]
[ 15  ][ 16  ][ 17  ][ 18  ][ 19  ][ 20  ][ 21  ]
[ 22  ][ 23  ][ 24  ][ 25  ][ 26  ][ 27  ][ 28  ]
[ 29  ][ 30  ][ 31  ][ --- ][ --- ][ --- ][ --- ]
```

- `[ --- ]` = dead cells (not part of the puzzle)
- Every valid date leaves exactly **2 cells exposed** (month + day)
- The remaining **41 cells** must be filled by the 8 pieces

## The 8 Pieces

| Piece | Shape | Cells |
|-------|-------|-------|
| P1 | Reverse J | 5 |
| P2 | L (left) | 5 |
| P3 | S/Z long | 5 |
| P4 | 2×3 Rectangle | 6 |
| P5 | P shape | 5 |
| P6 | T long | 5 |
| P7 | Z middle | 5 |
| P8 | Corner shape | 5 |

Each piece can be **rotated** (0°, 90°, 180°, 270°) and optionally **flipped** depending on the solve mode.

## Project Plan

- [x] Model the board (valid cells, dead cells, month/day mapping)
- [x] Define all 8 pieces with rotations and flips
- [x] Basic backtracking solver (first solution)
- [x] Memoized solver (faster, with hole detection + fail-first heuristic)
- [x] All-solutions solver (finds every possible solution for a given date)
- [x] Genetic algorithm solver (experimental)
- [ ] Clean backend API (FastAPI)
- [ ] React frontend (date picker, flip toggle, solve mode, colored board)
- [ ] Connect React frontend to FastAPI backend

## Project Structure

```
puzzle-a-day/
├── src/
│   ├── board.py          # Grid definition, valid cells, month/day mapping
│   ├── pieces.py         # All 8 pieces with rotations and flips
│   ├── solver.py         # Basic backtracking solver
│   ├── solver_mem.py     # Improved solver with memoization + hole detection
│   ├── solver_all.py     # Finds all possible solutions for a date
│   └── solver_ga.py      # Genetic algorithm solver (experimental)
├── tests/
│   └── test_board.py
├── main.py
└── requirements.txt
```

## Tech Stack

- **Python** — core logic and solvers
- **FastAPI** — backend API connecting Python solvers to the frontend
- **React** — frontend UI (date picker, flip toggle, colored board display)

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run basic solver
python src/solver.py

# Run memoized solver
python src/solver_mem.py

# Find all solutions
python src/solver_all.py
```
