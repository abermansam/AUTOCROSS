# main.py

def create_empty_grid(size):
    """
    Creates an empty grid of the given size.

    :param size: Tuple representing the dimensions of the grid (rows, columns)
    :return: 2D list representing the empty grid
    """
    return [['.' for _ in range(size[1])] for _ in range(size[0])]

def print_grid(grid):
    """
    Prints the grid in a readable format.

    :param grid: 2D list representing the crossword grid
    """
    for row in grid:
        print(' '.join(row))

def main():
    grid_size = (15, 15)  # Grid size (rows, columns)
    crossword_grid = create_empty_grid(grid_size)
    print_grid(crossword_grid)

if __name__ == "__main__":
    main()
