from typing import List, Tuple

Shape = List[Tuple[int, int]]

#rotate a shape 90 degree
#for each point: (r,c) ---> (c,-r)
def rotate_90(shape: Shape) -> Shape:
    return [(c,-r) for r, c in shape]

#flip horizontally (mirror)
 
 #   Example:
 #    X X        X
 #    X    ->    X X
    

def flip(shape:Shape) -> Shape:
    return [(-r, c) for r, c in shape]

#shift shape so the top-left is at (0,0)
def normalize(shape:Shape) -> Shape:
    min_r = min(r for r, c in shape)
    min_c = min(c for r, c in shape)
    return sorted((r-min_r, c-min_c) for r, c in shape)

def get_all_orientations(shape: Shape) -> Shape:
    seen = set()
    orientations = []
    current = shape
    for _ in range(4):
        normalized = normalize(current)
        key = tuple(normalized)
        if key not in seen:
            seen.add(key)
            orientations.append(normalized)
        flipped = normalize(flip(current))
        key_f = tuple(flipped)
        if key_f not in seen:
            seen.add(key_f)
            orientations.append(flipped)
        current = rotate_90(current)
    
    return orientations

# All 8 pieces defined as (row, col) offsets
RAW_PIECES = {
    "P1": [(0,0), (0,1), (0,2), (1,0), (2,0)],  # Reverse J
    "P2": [(0,0), (0,1), (0,2), (0,3), (1,0)],  # L left
    "P3": [(0,0), (0,1), (1,1), (2,1), (2,2)],  # S/Z long
    "P4": [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)],  # 2x3 rectangle
    "P5": [(0,0), (0,1), (1,0), (1,1), (2,0)],  # P shape
    "P6": [(0,0), (0,1), (0,2), (0,3), (1,2)],  # T long
    "P7": [(0,0), (0,1), (1,1), (2,0), (2,1)],  # Z middle
    "P8": [(0,1), (0,2), (1,0), (1,1), (1,2)],  # Corner shape
}

# Generate all orientations for each piece
PIECES = {
    name: get_all_orientations(shape)
    for name, shape in RAW_PIECES.items()
}

def print_shape(shape: Shape):
    """Print a shape visually on a grid."""
    max_r = max(r for r, c in shape)
    max_c = max(c for r, c in shape)
    for r in range(max_r + 1):
        row = ""
        for c in range(max_c + 1):
            row += "X " if (r, c) in shape else ". "
        print(row)

if __name__ == "__main__":
    for name, orientations in PIECES.items():
        print(f"{name}: {len(orientations)} orientations")
        

if __name__ == "__main__":
    for name, orientations in PIECES.items():
        print(f"\n{'='*20}")
        print(f"{name}: {len(orientations)} orientations")
        for i, o in enumerate(orientations):
            print(f"\n  Orientation {i+1}:")
            print_shape(o)