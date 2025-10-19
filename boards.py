import random
import numpy
import os
from collections import deque

"""
So far, we have developed an interactive version of the Battleship game.
For ease of execution, we simplified the game board to an 8×8 grid and randomly placed three ships at the start, with lengths of 2, 3, and 4 units respectively. 
The player inputs the coordinates of their desired attack step by step, and the terminal provides a visualized board along with feedback messages. 
Upon successfully sinking a ship, the surrounding cells are updated according to the initial placement rules to prevent invalid or redundant attacks.
"""

BOARD_SIZE = 8

# LOG: setup the size and initialize the board for the Battleship game
# The board size is set to 8x8 for the Battleship game.
#each cell have 5 different state
# 0 for not hit empty cell
# 1 for hit empty cell (miss)
# 2 for hit ship cell (hit)
# 3 for not hit ship cell
# 4 for hit ship cell and sunk (sunk)
# The board will be represented as a 2D list of integers, where each integer represents the state of the cell.
# then the ship sunk, cells around ship will mark as 1 (miss) directly since it's not allow to place ships around eachothers

#function to initialize the board, returns a 2D list of the board with all values set to 0
def initialize_board():
    """
    Initialize an 8x8 board with all values set to 0.
    Returns a 2D list representing the board.
    """
    board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    return board

# the learning board will include 3 different kinds of ships
# 1. frigate (2 cells long) - horizontal or vertical
# 2. destroyer (3 cells long) - horizontal or vertical
# 3. battleship (4 cells long) - horizontal or vertical
#function to generate a random board for mechine learning purposes returning a 2D list of the board with ships placed on it
def generate_random_board():
    """
    Generate a random 8x8 board with ships placed on it for machine learning purposes.
    Returns a 2D list representing the board with ships placed.
    """

    board = initialize_board()

    # Define ship lengths and their counts
    ships = [(2, 1), (3, 1), (4, 1)]  # (length, count)

    for length, count in ships:
        for _ in range(count):
            placed = False
            while not placed:
                orientation = random.choice(['horizontal', 'vertical'])
                if orientation == 'horizontal':
                    row = random.randint(0, BOARD_SIZE - 1)
                    col = random.randint(0, BOARD_SIZE - length)
                else:  # vertical
                    row = random.randint(0, BOARD_SIZE - length)
                    col = random.randint(0, BOARD_SIZE - 1)

                # Use the helper function to check if placement is valid
                if can_place_ship(board, row, col, length, orientation):
                    # If valid, place the ship
                    for i in range(length):
                        if orientation == 'horizontal':
                            board[row][col + i] = 3
                        else:
                            board[row + i][col] = 3
                    placed = True

    return board

def can_place_ship(board, row, col, length, orientation):
    """
    Checks if a ship of given length and orientation can be placed at (row, col)
    without overlapping or being adjacent (including diagonals) to an existing ship.
    Returns True if placement is valid, False otherwise.
    """
    for i in range(length):
        if orientation == 'horizontal':
            r = row
            c = col + i
        else:  # vertical
            r = row + i
            c = col

        # If out of bounds or current cell occupied, placement is invalid
        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
            return False
        if board[r][c] != 0:
            return False

        # Check the 8 neighbors (including diagonals)
        for rr in range(r - 1, r + 2):    # r-1, r, r+1
            for cc in range(c - 1, c + 2):  # c-1, c, c+1
                if 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE:
                    # If any neighbor is part of a ship (3), it's invalid
                    if board[rr][cc] == 3:
                        return False
    return True

def fire(x, y, board):
    """
    Make a fire action at coordinate(x, y).
    Returns updated board, message based on fire result, and game status.
    """
    # Make sure a valid coordinates input
    if x < 0 or x >= BOARD_SIZE or y < 0 or y >= BOARD_SIZE:
        return board, "Invalid coordinates", False

    current_cell = board[y][x]
    message = ""
    game_over = False

    if current_cell == 3:  # Hit undamaged ship
        board[y][x] = 2
        sunk, board, ship_cells = check_sunk_ship(x, y, board)
        if sunk:
            board = mark_surrounding(ship_cells, board)
            message = "Hit and sunk"
        else:
            message = "Hit"
    elif current_cell == 0:
        board[y][x] = 1
        message = "Miss"
    else:
        return board, "Already attacked here", False

    # Check game status
    game_over = check_game_over(board)
    return board, message, game_over

def check_sunk_ship(x, y, board):
    """
    Check if hit ship is completely sunk.
    Returns the sunk status, the updated board, and ship_cells.
    """
    ship_cells = []
    queue = deque([(x, y)])
    visited = set([(x, y)])

    # Initial validation check
    if board[y][x] not in (2, 3):
        return False, board, []

    # BFS to find connected ship parts
    while queue:
        cx, cy = queue.popleft()
        ship_cells.append((cx, cy))
        # Check 4 directions
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                if (nx, ny) not in visited and board[ny][nx] in (2, 3):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    # Check remaining undamaged parts
    for (cx, cy) in ship_cells:
        if board[cy][cx] == 3:
            return False, board, []

    # Mark all parts as sunk
    for (cx, cy) in ship_cells:
        board[cy][cx] = 4
    return True, board, ship_cells

def mark_surrounding(ship_cells, board):
    """
    Mark surrounding cells of sunk ship as misses.
    """
    # Check 8 directions
    directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    for (x, y) in ship_cells:
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                if board[ny][nx] == 0:  # No need to update areas already explored 
                    board[ny][nx] = 1
    return board

def check_game_over(board):
    """
    Check if all ships are sunk.
    """
    for row in board:
        if 3 in row:  # Any undamaged ship parts on the board
            return False
    return True

def print_game_board(board):
    """
    Print the board in a readable format (hide undamaged ships).
    """
    #Each cell will be represented by its state:
    #0: ~ (empty)
    #1: M (miss)
    #2: H (hit)
    #3: S (ship not hit)
    #4: X (sunk)
    print("  " + " ".join([str(i) for i in range(BOARD_SIZE)]))  # Column numbers
    for i, row in enumerate(board):
        row_str = f"{i} "
        for cell in row:
            if cell == 3:  # Hide undamaged ships
                row_str += "~ "
            else:
                # Maintain original symbol mapping
                row_str += ["~ ", "M ", "H ", "~ ", "X "][cell]
        print(row_str)

def play_game():
    """
    Main gameplay implementation
    """
    board = generate_random_board()
    print("=== BATTLESHIP ===")
    print_game_board(initialize_board())  # Show initial board
    
    while True:
        try:
            x = int(input("Enter X coordinate (0-7): "))
            y = int(input("Enter Y coordinate (0-7): "))
            board, msg, game_over = fire(x, y, board)
            print(f"\n{msg}")
            print_game_board(board)
            if game_over:
                print("\nAll ships sunk! Game over!")
                break
        except ValueError:
            print("Invalid input, please enter integers")


"""
#for debug, print the board in a readable format
def print_board(board):
"""
    #Print the board in a readable format for debugging purposes.
    #Each cell will be represented by its state:
    #0: ~ (empty)
    #1: M (miss)
    #2: H (hit)
    #3: S (ship not hit)
    #4: X (sunk)
"""
    print("  " + " ".join([str(i) for i in range(BOARD_SIZE)]))  # Column headers
    for i, row in enumerate(board):
        row_str = str(i) + " "
        for cell in row:
            if cell == 0:
                row_str += "~ "
            elif cell == 1:
                row_str += "M "
            elif cell == 2:
                row_str += "H "
            elif cell == 3:
                row_str += "S "
            elif cell == 4:
                row_str += "X "
        print(row_str)
""" 
#main function to test the board generation and printing
if __name__ == "__main__":
    play_game()
    # Generate a random board for machine learning purposes
    #board = generate_random_board()

    # Print the generated board for debugging
    #print("Generated Board:")
    #print_board(board)
   