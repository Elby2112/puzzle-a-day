import time
from src.pieces import PIECES
from tests.test_board import get_valid_cells, ROWS, COLS, MONTHS, DAYS
from tests.test_board import DEAD_CELLS


def solve_all(month: str, day: int) -> list:
    """
    Find ALL possible solutions for a given date.
    Returns a list of board dicts.
    """

    cells_to_fill = get_valid_cells(month, day)
    board = {}
    used_pieces = set()
    solutions = []

    def get_empty_cells() -> list:
        return [c for c in cells_to_fill if c not in board]

    def flood_fill(start: tuple, empty: set) -> set:
        region = set()
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell in region or cell not in empty:
                continue
            region.add(cell)
            r, c = cell
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (r + dr, c + dc)
                if neighbor in empty:
                    stack.append(neighbor)
        return region

    def has_unfillable_holes() -> bool:
        empty = set(get_empty_cells())
        if not empty:
            return False
        remaining_sizes = [
            len(PIECES[p][0])
            for p in PIECES
            if p not in used_pieces
        ]
        if not remaining_sizes:
            return False
        min_piece_size = min(remaining_sizes)
        visited = set()
        for cell in empty:
            if cell in visited:
                continue
            region = flood_fill(cell, empty)
            visited.update(region)
            if len(region) < min_piece_size:
                return True
        return False

    def can_place(shape, row, col) -> bool:
        for dr, dc in shape:
            r, c = row + dr, col + dc
            if r < 0 or r >= ROWS or c < 0 or c >= COLS:
                return False
            if (r, c) in DEAD_CELLS:
                return False
            if (r, c) not in cells_to_fill:
                return False
            if (r, c) in board:
                return False
        return True

    def place(shape, row, col, piece_name):
        for dr, dc in shape:
            r, c = row + dr, col + dc
            board[(r, c)] = piece_name

    def remove(shape, row, col):
        for dr, dc in shape:
            r, c = row + dr, col + dc
            board.pop((r, c), None)

    def backtrack():
        empty = get_empty_cells()

        # No empty cells → found a solution!
        if not empty:
            solutions.append(board.copy())  # save a copy
            return

        # Early termination
        if has_unfillable_holes():
            return

        row, col = empty[0]

        for piece_name, orientations in PIECES.items():
            if piece_name in used_pieces:
                continue
            for orientation in orientations:
                for dr, dc in orientation:
                    r0 = row - dr
                    c0 = col - dc
                    if can_place(orientation, r0, c0):
                        place(orientation, r0, c0, piece_name)
                        used_pieces.add(piece_name)

                        backtrack()  # don't stop → keep going!

                        remove(orientation, r0, c0)
                        used_pieces.discard(piece_name)

    backtrack()
    return solutions


def print_solution(solution: dict, month: str, day: int):
    """Print a solution visually."""
    labels = {}
    for name, pos in MONTHS.items():
        labels[pos] = name.upper()
    for number, pos in DAYS.items():
        labels[pos] = str(number)

    for r in range(ROWS):
        row = ""
        for c in range(7):
            if (r, c) in solution:
                row += f"{solution[(r,c)]:>4} "
            elif (r, c) in labels:
                row += f"{labels[(r,c)]:>4} "
            else:
                row += "XXXX "
        print(row)


if __name__ == "__main__":
    month = "dec"
    day = 21

    print(f"🔍 Finding ALL solutions for {month} {day}...")
    start = time.time()
    solutions = solve_all(month, day)
    end = time.time()

    print(f"\n✅ Found {len(solutions)} solutions in {end - start:.2f} seconds!")

    # Print first 3 solutions
    for i, sol in enumerate(solutions[:3]):
        print(f"\n─── Solution {i+1} ───")
        print_solution(sol, month, day)