# main.py
import random

## HELPERS

def create_symmetrical_grid():
    """
    Creates a 15x15 grid with 180-degree rotational symmetry.

    :return: 2D list representing the grid
    """
    size = 15  # Grid size
    grid = [['.' for _ in range(size)] for _ in range(size)]

    # Add symmetric black squares
    black_squares = [(0, 3), (1, 3), (2, 3),
                     (0, 7), 
                     (0, 11), (1, 11), (2, 11),
                     (3, 4), (3, 10),
                     (4, 0), (4, 1), (4, 2),
                     (4, 6), (4, 7), (4, 8),
                     (4, 12), (4, 13), (4, 14),
                     (6, 3), (7, 3), (8, 3),
                     (5, 7), (6, 7), (7, 7), (8, 7), (9, 7)]  # Example positions
    for row, col in black_squares:
        grid[row][col] = '#'
        grid[size - row - 1][size - col - 1] = '#'  # Symmetric counterpart

    return grid

def print_grid(grid):
    """
    Prints the grid in a readable format.

    :param grid: 2D list representing the crossword grid
    """
    for row in grid:
        print(' '.join(row))

def build_dictionary(word_list):
    """
    Builds a dictionary of words organized by word length.

    :param word_list: List of words to include in the dictionary.
    :return: Dictionary where keys are word lengths and values are lists of words.
    """
    dictionary = {}
    for word in word_list:
        length = len(word)
        if length not in dictionary:
            dictionary[length] = []
        dictionary[length].append(word)
    return dictionary

def build_word_dictionary(file_path):
    """
    Builds a dictionary of words from the given file.
    The dictionary keys are word lengths, and values are lists of tuples (word, score).

    :param file_path: Path to the word list file.
    :return: Dictionary of words organized by length.
    """
    word_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            word, score_str = line.strip().split(';')
            score = int(score_str)
            length = len(word)

            if length not in word_dict:
                word_dict[length] = []

            word_dict[length].append((word, score))

    return word_dict

## LOGIC BELOW


def word_fits(grid, word, row, col):
    """
    Checks if the word can be placed at the specified position on the grid.

    :param grid: 2D list representing the crossword grid.
    :param word: String, the word to place.
    :param row: Integer, the starting row for placing the word.
    :param col: Integer, the starting column for placing the word.
    :return: Boolean, True if the word can be placed, False otherwise.
    """
    grid_size = len(grid)
    # Check if the word fits horizontally
    if col + len(word) > grid_size:
        return False

    for i in range(len(word)):
        current_char = grid[row][col + i]
        if current_char not in ('.', word[i]):  # Check for invalid overlap
            return False

        # Check adjacent cells
        if (col + i > 0 and grid[row][col + i - 1] != '.') or (col + i < grid_size - 1 and grid[row][col + i + 1] != '.'):
            return False

    return True


def place_word(grid, word, row, col):
    """
    Places the word at the specified position on the grid.

    :param grid: 2D list representing the crossword grid.
    :param word: String, the word to place.
    :param row: Integer, the starting row for placing the word.
    :param col: Integer, the starting column for placing the word.
    """
    # Place the word horizontally
    for i in range(len(word)):
        grid[row][col + i] = word[i]


def find_open_space_across(grid, row, col):
    """
    Finds the length of the open space starting from (row, col) in the specified orientation.
    """
    length = 0
    while (col < len(grid) and grid[row][col] == '.'):
        length += 1
        col += 1
    return length

def get_vertical_word_info(grid, row, col):
    """
    Gets the length of the vertical word and the letters currently in the word 
    at the specified row and column position, considering both above and below.

    :param grid: 2D list representing the crossword grid.
    :param row: The row position to start the search.
    :param col: The column position to start the search.
    :return: Tuple (length of the vertical word, the current letters in the word).
    """
    length = 0
    letters = ''

    # Move upwards to the start of the word
    start_row = row
    while start_row > 0 and grid[start_row - 1][col] != '#':
        start_row -= 1

    # Move downwards to calculate the length and collect letters
    current_row = start_row
    while current_row < len(grid) and grid[current_row][col] != '#':
        letters += grid[current_row][col] if grid[current_row][col] != '.' else ''
        length += 1
        current_row += 1

    return length, letters

def is_valid_intersection(grid, word, row, col, word_dict):
    """
    Checks if placing the word creates valid intersections with perpendicular words.
    """
    out_list = [False] * len(word)
    i = 0
    if row>0:
        while i < len(word):
            i += 1
            space_length, letters = get_vertical_word_info(grid, row, col+i-1)
            letters = letters + word[i-1]
            word_list = word_dict.get(space_length, [])
            for w, _ in word_list:
                if w[:len(letters)] == letters:
                    # print(w, letters, word)
                    out_list[i-1] = True
                    break
        return all(out_list)
    else:
        return True

    
    
def fill_grid(grid, word_dict):
    """
    Fills the crossword grid with words from the dictionary, starting from the top left.
    """
    row = 0
    col = 0

    while row < len(grid):   
        col = 0 
        while col < len(grid[0]):
            space_length = find_open_space_across(grid, row, col)
            if (space_length > 0):
                word_list = word_dict.get(space_length, [])
                random.shuffle(word_list)
                for word, points in word_list:
                    assert(col + space_length-1 < len(grid[0]))
                    if points >25 and is_valid_intersection(grid, word, row, col, word_dict):
                        place_word(grid, word, row, col)
                        print_grid(grid)
                        word_list.remove((word, points))
                        break;
                col += space_length - 1
            col += 1
        row += 1
        

def is_grid_filled(grid):
    """
    Checks if the grid is completely filled with words.

    :param grid: 2D list representing the crossword grid.
    :return: Boolean, True if the grid is filled, False otherwise.
    """
    return all(cell != '.' for row in grid for cell in row)


if __name__ == '__main__':
    crossword_grid = create_symmetrical_grid()
    dict_file_path = 'spreadthewordlist_caps.dict'  # Replace with your actual file path
    word_dict = build_word_dictionary(dict_file_path)
    fill_grid(crossword_grid, word_dict)
    print_grid(crossword_grid)
    
