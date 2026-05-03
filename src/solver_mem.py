import random
from src.pieces import PIECES
from tests.test_board import get_valid_cells, ROWS, COLS
from tests.test_board import DEAD_CELLS

# ─────────────────────────────────────────────────────────────
# ZOBRIST HASHING SETUP
# We assign a unique random 64-bit number to every possible
# (row, col) cell on the board.
# When we place a piece on a cell → XOR its number into the hash
# When we remove a piece from a cell → XOR again to undo
# This gives us a fast unique fingerprint of the board state
# ─────────────────────────────────────────────────────────────

random.seed(42)  # fixed seed so hashes are consistent across runs
ZOBRIST_TABLE = {
    (r, c): random.getrandbits(64)
    for r in range(ROWS)
    for c in range(COLS)
}


def solve_mem(month: str, day: int) -> dict | None:
    """
    Improved backtracking solver with:
    1. Zobrist Hashing    - fast board state fingerprinting
    2. Memoization        - skip previously failed states
    3. Fail-first         - tackle most constrained cells first
    4. Hole detection     - abandon paths with unfillable gaps early
    """

    cells_to_fill = get_valid_cells(month, day)

    # ── Board state ──
    board = {}  # (row, col) -> piece_name
    used_pieces = set()  # which pieces have been placed

    # ── Zobrist hash ──
    current_hash = 0  # XOR of all placed cells' random numbers

    # ── Memoization cache ──
    # Stores board state hashes that we KNOW lead to failure
    failed_states = set()

    # ─────────────────────────────────────────────────────────
    # HOLE DETECTION
    # After placing a piece, check if any empty region is too
    # small to be filled by any remaining piece.
    # If a region has fewer cells than the smallest piece → dead end
    # ─────────────────────────────────────────────────────────
    def get_empty_cells() -> list:
        return [c for c in cells_to_fill if c not in board]

    def flood_fill(start: tuple, empty: set) -> set:
        """
        Find all connected empty cells starting from 'start'.
        Uses flood fill (BFS) to find the connected region.
        """
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
        """
        Check if any isolated empty region is too small
        to be filled by any remaining piece.

        Smallest piece size among unused pieces = minimum valid region size.
        If a region is smaller than that → unfillable → dead end!
        """
        empty = set(get_empty_cells())
        if not empty:
            return False

        # Find the smallest piece size among unused pieces
        remaining_sizes = [
            len(PIECES[p][0])  # all orientations have same number of cells
            for p in PIECES
            if p not in used_pieces
        ]
        if not remaining_sizes:
            return False

        min_piece_size = min(remaining_sizes)

        # Check each connected region
        visited = set()
        for cell in empty:
            if cell in visited:
                continue
            region = flood_fill(cell, empty)
            visited.update(region)

            # If region size is not a multiple of any piece size
            # or smaller than smallest piece → unfillable
            if len(region) < min_piece_size:
                return True

        return False

    # ─────────────────────────────────────────────────────────
    # FAIL-FIRST HEURISTIC
    # Instead of always picking the top-left empty cell,
    # pick the cell with the FEWEST valid piece placements.
    # This means we tackle the hardest spots first,
    # failing faster on bad paths.
    # ─────────────────────────────────────────────────────────
    def count_valid_placements(cell: tuple) -> int:
        """Count how many (piece, orientation, position) combos cover this cell."""
        count = 0
        row, col = cell
        for piece_name, orientations in PIECES.items():
            if piece_name in used_pieces:
                continue
            for orientation in orientations:
                for dr, dc in orientation:
                    r0, c0 = row - dr, col - dc
                    valid = True
                    for sr, sc in orientation:
                        r, c = r0 + sr, c0 + sc
                        if r < 0 or r >= ROWS or c < 0 or c >= COLS:
                            valid = False
                            break
                        if (r, c) in DEAD_CELLS:
                            valid = False
                            break
                        if (r, c) not in cells_to_fill:
                            valid = False
                            break
                        if (r, c) in board:
                            valid = False
                            break
                    if valid:
                        count += 1
        return count

    def pick_next_cell() -> tuple | None:
        """
        Pick the empty cell with the fewest valid placements.
        This is the 'fail-first' heuristic.
        """
        empty = get_empty_cells()
        if not empty:
            return None
        return min(empty, key=count_valid_placements)

    # ─────────────────────────────────────────────────────────
    # PLACEMENT HELPERS
    # ─────────────────────────────────────────────────────────
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
        """Place piece and update Zobrist hash."""
        nonlocal current_hash
        for dr, dc in shape:
            r, c = row + dr, col + dc
            board[(r, c)] = piece_name
            current_hash ^= ZOBRIST_TABLE[(r, c)]  # XOR in

    def remove(shape, row, col):
        """Remove piece and update Zobrist hash."""
        nonlocal current_hash
        for dr, dc in shape:
            r, c = row + dr, col + dc
            board.pop((r, c), None)
            current_hash ^= ZOBRIST_TABLE[(r, c)]  # XOR out

    # ─────────────────────────────────────────────────────────
    # BACKTRACKING WITH MEMOIZATION
    # ─────────────────────────────────────────────────────────
    def backtrack() -> bool:
        # ── Check memoization cache ──
        # If we've seen this exact board state before and it failed
        # → no need to explore further
        if current_hash in failed_states:
            return False

        # ── Pick next cell (fail-first) ──
        cell = pick_next_cell()

        # No empty cells → solved!
        if cell is None:
            return True

        row, col = cell

        # ── Early termination: hole detection ──
        if has_unfillable_holes():
            failed_states.add(current_hash)  # cache this failure
            return False

        # ── Try each unused piece ──
        for piece_name, orientations in PIECES.items():
            if piece_name in used_pieces:
                continue

            # Try each orientation
            for orientation in orientations:
                # Try anchoring each cell of the piece to (row, col)
                for dr, dc in orientation:
                    r0 = row - dr
                    c0 = col - dc

                    if can_place(orientation, r0, c0):
                        # Place the piece
                        place(orientation, r0, c0, piece_name)
                        used_pieces.add(piece_name)

                        # Recurse
                        if backtrack():
                            return True

                        # Didn't work → remove and try next
                        remove(orientation, r0, c0)
                        used_pieces.discard(piece_name)

        # Nothing worked → cache this failure
        failed_states.add(current_hash)
        return False

    if backtrack():
        return board
    return None


if __name__ == "__main__":
    import time
    from tests.test_board import MONTHS, DAYS

    month = "dec"
    day = 21

    print(f"Solving for {month} {day} with memoization...")
    start = time.time()
    solution = solve_mem(month, day)
    end = time.time()

    labels = {}
    for name, pos in MONTHS.items():
        labels[pos] = name.upper()
    for number, pos in DAYS.items():
        labels[pos] = str(number)

    if solution:
        print(f"✅ Solved in {end - start:.4f} seconds!")
        for r in range(7):
            row = ""
            for c in range(7):
                if (r, c) in solution:
                    row += f"{solution[(r, c)]:>4} "
                elif (r, c) in labels:
                    row += f"{labels[(r, c)]:>4} "
                else:
                    row += "XXXX "
            print(row)
    else:
        print("❌ No solution found!")