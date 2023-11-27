# main.py
import random
import os
import time
from openai import OpenAI


## HELPERS

def clear_screen():
    """
    Clears the terminal screen.
    """
    print("\033[H\033[J", end="")

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
                     (3, 4),(3, 5), (3, 10),(3, 9),
                     (4, 0), (4, 1), (4, 2),
                     (4, 6), (4, 7), (4, 8),
                     (4, 12), (4, 13), (4, 14),
                     (6, 3), (7, 3), (8, 3),
                     (5, 7), (6, 7), (7, 7), (8, 7), (9, 7)]  # Example positions
    for row, col in black_squares:
        grid[row][col] = '#'
        grid[size - row - 1][size - col - 1] = '#'  # Symmetric counterpart

    return grid

def create_symmetrical_grid2():
    """
    Creates a 15x16 grid with 180-degree rotational symmetry.

    :return: 2D list representing the grid
    """
    rows, cols = 15, 16  # Grid dimensions
    grid = [['.' for _ in range(cols)] for _ in range(rows)]

    # Add symmetric black squares
    black_squares = [(0, 3), (0, 4),
                     (1, 4), (2, 4),
                     (3, 5), 
                     (0, 11), (1, 11),
                     (3, 9), (3, 10),
                     (4, 14), (4, 15),
                     (5, 0), (5, 1), (5, 2),
                     (5, 7), (5, 8),
                     (5, 12),
                     (6, 6), (6, 11)]  # Example positions

    for row, col in black_squares:
        grid[row][col] = '#'
        grid[rows - row - 1][cols - col - 1] = '#'  # Symmetric counterpart

    return grid

def print_grid(grid):
    """
    Prints the grid in a readable format.

    :param grid: 2D list representing the crossword grid
    """
    # clear_screen()
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

def is_grid_filled(grid):
    """
    Checks if the grid is completely filled with words.

    :param grid: 2D list representing the crossword grid.
    :return: Boolean, True if the grid is filled, False otherwise.
    """
    return all(cell != '.' for row in grid for cell in row)

def find_open_space_across(grid, row, col):
    """
    Finds the length of the open space starting from (row, col) in the specified orientation.
    """
    length = 0
    while (col < len(grid[0]) and row < len(grid) and grid[row][col] == '.'):
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
    down_count = 0
    # Move upwards to the start of the word
    start_row = row
    while start_row > 0 and grid[start_row - 1][col] != '#':
        start_row -= 1

    # Move downwards to calculate the length and collect letters
    current_row = start_row
    while current_row < len(grid) and grid[current_row][col] != '#':
        letters += grid[current_row][col] if grid[current_row][col] != '.' else ''
        length += 1
        if (current_row>row):
            down_count+=1
        current_row += 1
        

    return length, letters, down_count

def is_valid_intersection(grid, word, row, col, word_dict, complexity):
    """
    Checks if placing the word creates valid intersections with perpendicular words.
    """
    out_list = [False] * len(word)
    i = 0
    if row>0:
        while i < len(word):
            i += 1
            space_length, letters, _ = get_vertical_word_info(grid, row, col+i-1)
            letters = letters + word[i-1]
            word_list = word_dict.get(space_length, [])
            for w, points in word_list:
                if points>complexity:
                    if w[:len(letters)] == letters:
                        # print(w, letters, word)
                        out_list[i-1] = True
                        break
            if not out_list[i-1]:
                return False
        return all(out_list)
    else:
        return True   

def remove_horizontal_word(grid, row, col):
    """
    Removes a horizontal word from the grid starting from the given row and column.

    :param grid: 2D list representing the crossword grid.
    :param row: Integer, the row of the word start.
    :param col: Integer, the column of the word start.
    """
    # Move left to the start of the word
    start_col = col
    while start_col > 0 and grid[row][start_col - 1] != '#':
        start_col -= 1

    removed_word = ""
    # Move right to the end of the word and clear letters
    end_col = start_col
    while end_col < len(grid[0]) and grid[row][end_col] != '#':
        removed_word += grid[row][end_col]
        grid[row][end_col] = '.'
        end_col += 1
    return removed_word

def fill_grid_sam(grid, word_dict, complexity=25):
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
                word_placed = False
                word_list = word_dict.get(space_length, [])
                # random.shuffle(word_list)
                for word, points in word_list:
                    assert(col + space_length-1 < len(grid[0]))
                    if points > complexity and is_valid_intersection(grid, word, row, col, word_dict, complexity):
                        place_word(grid, word, row, col)
                        # print_grid(grid)
                        # word_list.remove((word, points))
                        word_dict[len(word)] = [(w, p) for w, p in word_dict[len(word)] if w != word]
                        # print(word_dict)
                        word_placed = True
                        break
                if not word_placed:
                    # Remove all words in the same column and go back to start
                    lowest_row = len(grid)

                    for j in range(col, col + space_length):  # Iterate over each column in the space_length
                        length,_, down_count = get_vertical_word_info(grid, row, j)
                        for i in range(row+down_count, -1, -1):  # Iterate over each row above the current one
                            if grid[i][j] == '#':
                                break
                            elif grid[i][j] != '.':
                                if i<lowest_row:
                                    lowest_row = i
                                removed_word = remove_horizontal_word(grid, i, j)
                                if removed_word:
                                    word_dict[len(removed_word)].append((removed_word, 50))  # Adjust the score as needed
                                # print_grid(grid)
                    row = lowest_row
                    col = 0   
                else:
                    col += space_length - 1
            else:            
                col += 1
        row += 1
    if not is_grid_filled(grid):
        print(word_dict)
        print("NOT FILLED")
        return grid
    else:
        return grid

def output_wordlist(grid):
    across_words = []
    down_words = []

    # Find Across words
    for row in range(len(grid)):
        col = 0
        while col < len(grid[0]):
            if grid[row][col] != '#' and (col == 0 or grid[row][col - 1] == '#'):
                start_col = col
                word = ''
                while col < len(grid[0]) and grid[row][col] != '#':
                    word += grid[row][col]
                    col += 1
                if len(word) > 1:
                    across_words.append((row + 1, start_col + 1, word))
            else:
                col += 1

    # Find Down words
    for col in range(len(grid[0])):
        row = 0
        while row < len(grid):
            if grid[row][col] != '#' and (row == 0 or grid[row - 1][col] == '#'):
                start_row = row
                word = ''
                while row < len(grid) and grid[row][col] != '#':
                    word += grid[row][col]
                    row += 1
                if len(word) > 1:
                    down_words.append((start_row + 1, col + 1, word))
            else:
                row += 1

    return {"Across": across_words, "Down": down_words}

def print_and_store_word_lists(grid):
    word_list = output_wordlist(grid)
    across_words = word_list["Across"]
    down_words = word_list["Down"]
    
    all_words = sorted(across_words + down_words, key=lambda x: (x[0], x[1]))
    word_number = 1
    number_map = {}

    # Dictionary to store the numbered words
    numbered_words = {
        "Across": {},
        "Down": {}
    }

    # Assign numbers sequentially
    for row, col, _ in all_words:
        if (row, col) not in number_map:
            number_map[(row, col)] = word_number
            word_number += 1

    # Print and store across words with numbers
    # print("Across")
    for row, col, word in across_words:
        num = number_map[(row, col)]
        # print(f"  {num}. {word}")
        numbered_words["Across"][num] = (row, col, word)

    # Sort, print, and store down words with numbers
    # print("\nDown")
    sorted_down_words = sorted(down_words, key=lambda x: (x[0], x[1]))
    for row, col, word in sorted_down_words:
        num = number_map[(row, col)]
        # print(f"  {num}. {word}")
        numbered_words["Down"][num] = (row, col, word)

    return numbered_words

def create_clues(word_list):
    client = OpenAI()  # Replace with your actual API key

    system_prompt = """
    You are a crossword clue creator, skilled in crossword clues with a creative flair.
    Your clues make use of:
    Double definitions (The clue is a second definition of the word. For example, the answer HOOD can have one of the two clues: “gangster” or “a cover for the head")
    Anagrams of the word (giving a signal word such as “mixed,” “aimless” or “fractured.” and then the anagram. The Anagram should also be a dictionary word)
    References to Pop culture
    Simple definitions
    Riddles.

    You will randomly select one of these 5 options and create a clue. The clue should be one phrase. Respond with only the text of this clue.
    """

    clues = {}

    for category in ["Across", "Down"]:
        clues[category] = {}
        for num, (row, col, word) in word_list[category].items():
            user_prompt = "Create a clue for the word " + word + ":"
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                max_tokens=60,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            clue = response.choices[0].message.content
            clues[category][num] = (word, clue)

    return clues

def print_clues(crossword_clues):
    print("Crossword Clues\n")

    # Print Across clues
    print("Across")
    for num, (word, clue) in crossword_clues["Across"].items():
        print(f"  {num}. {clue} ({word})")

    print("\nDown")
    # Print Down clues
    for num, (word, clue) in crossword_clues["Down"].items():
        print(f"  {num}. {clue} ({word})")



if __name__ == '__main__':
    dict_file_path = 'monday_11_20_23.dict'
    crossword_grid = create_symmetrical_grid2()
    word_dict = build_word_dictionary(dict_file_path)
    print_grid(crossword_grid)
    final_grid = fill_grid_sam(crossword_grid, word_dict, 35)
    final_wordlist = print_and_store_word_lists(final_grid)
    print()
    print("Generating clues...")
    print()
    st = time.time()
    crossword_clues = create_clues(final_wordlist)
    print_clues(crossword_clues)

    et = time.time()
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')


    

    
