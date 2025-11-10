import math
import copy

directions = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),          (0, 1),
              (1, -1),  (1, 0), (1, 1)]

NONE, BLACK, WHITE = '.', 'B', 'W'

def ab_pruning():
    # alpha beta pruning algorithm implementation
    pass

def opponent(color):
    return BLACK if color==WHITE else WHITE

def evaluate_board():
    # implementation of a heuristic board evaluation funciton, unknown search tree depth yet
    pass

def minimax():
    # help find the best move
    pass

def get_valid_moves(board, color):
    return [(row, col) for row in range(8) for col in range(8) if valid_move(board, row, col, color)]

def valid_move(board, x, y, color):
    if not (0 <= x < 8 and 0 <= y < 8) or board[x][y] != NONE:
        return False
    for dx, dy in directions:
        row, col = x + dx, y + dy
        flip = False
        while 0 <= row < 8 and 0 <= col < 8 and board[row][col] == opponent(color):
            row += dx
            col += dy
            flip = True
        if flip and 0 <= row < 8 and 0 <= col < 8 and board[row][col] == color:
            return True
    return False
    

def make_move(board, x, y, color):
    # list of all valid moves
    updated_board = copy.deepcopy(board)
    updated_board[x][y] = color
    for dx, dy in directions:
        row, col = x + dx, y + dy
        flips = list()
        while 0 <= row < 8 and 0 <= col < 8:
            flips.append(row, col)
            row += dx
            col += dy
        if flips and 0 <= row < 8 and 0 <= col < 8 and updated_board[row][col] == color:
            for r, c in flips:
                updated_board[r][c] = color
    return updated_board

def print_board(board):
    # print current state of the board
    print('  ' + ' '.join(str(x) for x in range(8)))
    for y in reversed(range(8)):
        print(f"{y}  " + ' '.join(board[y]))
    print()

def play():
    # main game loop
    board = [[NONE for x in range(8)] for y in range(8)]
    board[3][3] = WHITE
    board[3][4] = BLACK
    board[4][3] = BLACK
    board[4][4] = WHITE
    undo = list() # list implemented as stack to undo a singular move
    player = input("Select Black (B) or White (W): ")
    while player not in (BLACK, WHITE):
        player = input("Invalid: choose (B) or (W): ")
    current_color = BLACK
    AI_color = opponent(player)
    ai_on = input("Play against AI? (Y or N): ")
    while ai_on not in ['Y', 'N']:
        ai_on = input("Invalid input: Type Y or N: ")
    AI = False if ai_on == 'N' else True
    
    while True:
        print_board(board)
        break

if __name__ == '__main__':
    play()
