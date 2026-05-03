import random

from src.pieces import PIECES
from tests.test_board import get_valid_cells, ROWS, COLS
from tests.test_board import DEAD_CELLS
# ─────────────────────────────────────────
# CHROMOSOME REPRESENTATION
# A chromosome is just a list of (piece_name, orientation_index)
# The placement is determined by the board state (first empty cell)
# ─────────────────────────────────────────

PIECE_NAMES = list(PIECES.keys())  # ['P1', 'P2', ..., 'P8']


def random_chromosome() -> list:
    """
    A chromosome is:
    - A random ordering of the 8 pieces
    - A random orientation for each piece

    Example: [('P3', 2), ('P1', 0), ('P7', 3), ...]
    """
    order = PIECE_NAMES.copy()
    random.shuffle(order)
    return [(piece, random.randint(0, len(PIECES[piece]) - 1)) for piece in order]

def get_valid_placements(piece_name: str, orientation_idx: int, 
                          cells_to_fill: set, board: dict) -> list:
    """
    Get ALL valid positions where a piece can be placed
    given the current board state.
    Returns a list of (row, col) anchor points.
    """
    shape = PIECES[piece_name][orientation_idx]
    valid_positions = []

    for target_row, target_col in cells_to_fill:
        if (target_row, target_col) in board:
            continue

        # Try anchoring each cell of the shape to target
        for dr, dc in shape:
            row = target_row - dr
            col = target_col - dc

            valid = True
            cells = []
            for sr, sc in shape:
                r, c = row + sr, col + sc
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
                cells.append((r, c))

            if valid and cells:
                valid_positions.append((row, col))

    # Remove duplicates
    return list(set(valid_positions))


def place_chromosome(chromosome: list, cells_to_fill: set) -> dict:
    """
    Place pieces on the board.
    For each piece:
    - Get ALL valid placements given current board state
    - Pick the one that aligns with the first empty cell if possible
    - Otherwise pick randomly from valid placements
    - If no valid placement exists, skip the piece
    """
    board = {}

    for piece_name, orientation_idx in chromosome:
        shape = PIECES[piece_name][orientation_idx]

        # Get all valid placements for this piece
        valid_positions = get_valid_placements(piece_name, orientation_idx,
                                               cells_to_fill, board)

        if not valid_positions:
            continue  # can't place this piece, skip

        # Prefer placement that covers the first empty cell
        empty = sorted([c for c in cells_to_fill if c not in board])
        if not empty:
            break

        first_empty = empty[0]
        preferred = []
        for row, col in valid_positions:
            cells = [(row + dr, col + dc) for dr, dc in shape]
            if first_empty in cells:
                preferred.append((row, col))

        if preferred:
            row, col = preferred[0]  # use first preferred
        else:
            row, col = random.choice(valid_positions)  # random valid placement

        # Place the piece
        for dr, dc in shape:
            r, c = row + dr, col + dc
            board[(r, c)] = piece_name

    return board


def fitness(chromosome: list, cells_to_fill: set) -> float:
    """
    Score = how many valid cells are filled / total cells to fill.
    Perfect score = 1.0 (all 41 cells filled)
    """
    board = place_chromosome(chromosome, cells_to_fill)
    return len(board) / len(cells_to_fill)


def selection(population: list, fitnesses: list, k: int = 5) -> list:
    """Tournament selection — pick best out of k random chromosomes."""
    tournament = random.sample(list(zip(population, fitnesses)), k)
    tournament.sort(key=lambda x: x[1], reverse=True)
    return tournament[0][0]


def crossover(parent1: list, parent2: list) -> tuple:
    """
    Order crossover (OX):
    Preserve the piece ORDER from parent1 for the first half,
    then fill in the rest using parent2's order.

    This respects the constraint that each piece appears exactly once.
    """
    size = len(parent1)
    point = random.randint(1, size - 1)

    # Take first part from parent1
    child1_pieces = [p for p, _ in parent1[:point]]
    child2_pieces = [p for p, _ in parent2[:point]]

    # Fill rest with parent2's order (skip already used pieces)
    for piece, orient in parent2:
        if piece not in child1_pieces:
            child1_pieces.append(piece)
    for piece, orient in parent1:
        if piece not in child2_pieces:
            child2_pieces.append(piece)

    # Assign orientations: keep parent's orientation, else random
    p1_orients = {p: o for p, o in parent1}
    p2_orients = {p: o for p, o in parent2}

    child1 = [(p, p2_orients.get(p, random.randint(0, len(PIECES[p]) - 1)))
              for p in child1_pieces]
    child2 = [(p, p1_orients.get(p, random.randint(0, len(PIECES[p]) - 1)))
              for p in child2_pieces]

    return child1, child2


def mutate(chromosome: list, mutation_rate: float = 0.2) -> list:
    """
    Two types of mutation:
    1. Swap two pieces in the order
    2. Change a piece's orientation randomly
    """
    chromosome = chromosome.copy()

    for i in range(len(chromosome)):
        if random.random() < mutation_rate:
            # Type 1: swap with another random piece
            j = random.randint(0, len(chromosome) - 1)
            chromosome[i], chromosome[j] = chromosome[j], chromosome[i]

        if random.random() < mutation_rate:
            # Type 2: change orientation
            piece_name = chromosome[i][0]
            new_orient = random.randint(0, len(PIECES[piece_name]) - 1)
            chromosome[i] = (piece_name, new_orient)

    return chromosome


def solve_ga(month: str, day: int,
             population_size: int = 300,
             generations: int = 1000,
             mutation_rate: float = 0.3) -> dict | None:
    cells_to_fill = get_valid_cells(month, day)

    # Initial population
    population = [random_chromosome() for _ in range(population_size)]

    best_fitness = 0.0
    best_chromosome = None
    no_improvement = 0

    for generation in range(generations):
        # Evaluate fitness
        fitnesses = [fitness(c, cells_to_fill) for c in population]

        max_fit = max(fitnesses)
        if max_fit > best_fitness:
            best_fitness = max_fit
            best_chromosome = population[fitnesses.index(max_fit)]
            no_improvement = 0
            print(f"Generation {generation}: best fitness = {best_fitness:.3f}")
        else:
            no_improvement += 1

        # Perfect solution!
        if best_fitness >= 1.0:
            print(f"🎉 Perfect solution found at generation {generation}!")
            break

        # Restart if stuck but keep best
        if no_improvement >= 100:
            print(f"  ↩️ Stuck at {best_fitness:.3f}, restarting...")
            population = [random_chromosome() for _ in range(population_size - 1)]
            population.append(best_chromosome)
            no_improvement = 0
            continue

        # Build new population
        new_population = []

        # Elitism: keep top 3
        sorted_pop = sorted(zip(population, fitnesses),
                            key=lambda x: x[1], reverse=True)
        new_population.extend([x[0] for x in sorted_pop[:3]])

        # Fill rest with crossover + mutation
        while len(new_population) < population_size:
            parent1 = selection(population, fitnesses)
            parent2 = selection(population, fitnesses)
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)
            new_population.extend([child1, child2])

        population = new_population[:population_size]

    # Build and return solution board
    if best_fitness >= 1.0 and best_chromosome:
        return place_chromosome(best_chromosome, cells_to_fill)

    print(f"❌ Best fitness reached: {best_fitness:.3f}")
    return None


if __name__ == "__main__":
    import time
    from tests.test_board import MONTHS, DAYS

    month = "dec"
    day = 21

    print(f"🧬 Solving for {month} {day} using Genetic Algorithm...")
    start = time.time()
    solution = solve_ga(month, day)
    end = time.time()

    labels = {}
    for name, pos in MONTHS.items():
        labels[pos] = name.upper()
    for number, pos in DAYS.items():
        labels[pos] = str(number)

    if solution:
        print(f"\n✅ Solved in {end - start:.2f} seconds!")
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
        print(f"\n❌ No solution found in {end - start:.2f} seconds!")