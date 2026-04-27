#Board is 7columns x 7rows (43 valid cells)
#we have dead cells (are not part of the puzzle) 6 cells

ROWS = 7
COLS = 7

DEAD_CELLS={
    (0,6), (1,6), (6,3), (6,4),(6,5), (6,6)
}

MONTHS ={
    "jan":(0,0), "feb":(0,1), "mar":(0,2), "apr": (0,3), "may":(0,4),"jun":(0,5),
    "jul": (1, 0), "aug": (1, 1), "sep": (1, 2), "oct": (1, 3), "nov": (1, 4), "dec": (1, 5),
}
DAYS = {
    1:  (2, 0), 2:  (2, 1), 3:  (2, 2), 4:  (2, 3), 5:  (2, 4), 6:  (2, 5), 7:  (2, 6),
    8:  (3, 0), 9:  (3, 1), 10: (3, 2), 11: (3, 3), 12: (3, 4), 13: (3, 5), 14: (3, 6),
    15: (4, 0), 16: (4, 1), 17: (4, 2), 18: (4, 3), 19: (4, 4), 20: (4, 5), 21: (4, 6),
    22: (5, 0), 23: (5, 1), 24: (5, 2), 25: (5, 3), 26: (5, 4), 27: (5, 5), 28: (5, 6),
    29: (6, 0), 30: (6, 1), 31: (6, 2),
}

def get_valid_cells(month:str, day:int) -> set:
    exposed = {MONTHS[month.lower()], DAYS[day]}
    all_valid ={
        (r,c)
        for r in range(ROWS)
        for c in range(COLS)
        if (r,c) not in DEAD_CELLS
    }
    return all_valid - exposed

if __name__ == "__main__":
    cells = get_valid_cells("Feb", 29)
    print(f"Cells to fill: {len(cells)}")  #