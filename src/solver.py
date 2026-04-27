

from src.pieces import PIECES
from tests.test_board import get_valid_cells, ROWS, COLS
from tests.test_board import DEAD_CELLS


def solve(month: str, day: int):
    """
    Solve the puzzle for a given month and day using backtracking.
    Returns a dict mapping (row, col) -> piece_name if solved, else None.
    """
    # Get the 41 cells we need to fill
    cells_to_fill = get_valid_cells(month, day)

    # We'll work with a sorted list of cells for consistency
    empty_cells = sorted(cells_to_fill)

    # This will store our solution: (row, col) -> piece_name
    board = {}

    # Track which pieces have been used
    used_pieces = set()

    def can_place(shape, row, col):
        """Check if a piece can be placed at (row, col)."""
        for dr, dc in shape:
            r, c = row + dr, col + dc
            # Out of bounds?
            if r < 0 or r >= ROWS or c < 0 or c >= COLS:
                return False
            # Dead cell?
            if (r, c) in DEAD_CELLS:
                return False
            # Already occupied?
            if (r, c) in board:
                return False
            # Not a cell we need to fill?
            if (r, c) not in cells_to_fill:
                return False
        return True

    def place(shape, row, col, piece_name):
        """Place a piece on the board."""
        for dr, dc in shape:
            board[(row + dr, col + dc)] = piece_name

    def remove(shape, row, col):
        """Remove a piece from the board."""
        for dr, dc in shape:
            board.pop((row + dr, col + dc), None)

    def backtrack():
        # Find the first empty cell
        empty = [c for c in empty_cells if c not in board]

        # No empty cells left → solved!
        if not empty:
            return True

        # Pick the first empty cell
        row, col = empty[0]

        # Try each unused piece
        for piece_name, orientations in PIECES.items():
            if piece_name in used_pieces:
                continue

            # Try each orientation
            for orientation in orientations:
                if can_place(orientation, row, col):
                    # Place the piece
                    place(orientation, row, col, piece_name)
                    used_pieces.add(piece_name)

                    # Recurse
                    if backtrack():
                        return True

                    # Didn't work → remove and try next
                    remove(orientation, row, col)
                    used_pieces.discard(piece_name)

        # Nothing worked for this cell
        return False

    if backtrack():
        return board
    return None


if __name__ == "__main__":
    import time
    from tests.test_board import MONTHS, DAYS

    month = "dec"
    day = 21

    print(f"Solving for {month} {day}...")
    start = time.time()
    solution = solve(month, day)
    end = time.time()

    # Build reverse lookup for labels
    labels = {}
    for name, pos in MONTHS.items():
        labels[pos] = name.upper()
    for number, pos in DAYS.items():
        labels[pos] = str(number)

    if solution:
        print(f"✅ Solved in {end - start:.2f} seconds!")
        for r in range(7):
            row = ""
            for c in range(7):
                if (r, c) in solution:
                    row += f"{solution[(r,c)]:>4} "
                elif (r, c) in labels:
                    row += f"{labels[(r,c)]:>4} "
                else:
                    row += "XXXX "
            print(row)
    else:
        print("❌ No solution found!")