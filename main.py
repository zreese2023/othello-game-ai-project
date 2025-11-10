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

def evaluate_board(board, ai_color):
    '''
        board evaluation function, returns a score from -10 to 10
        positive score favors black, negative score favors white
    '''
    b_count = sum(row.count('B') for row in board)
    w_count = sum(row.count('W') for row in board)
    total = b_count + w_count
    if total == 0:
        return 0  # empty board at start
    # score ranges from -10 (white wins) to 10 (black wins)
    score = 10 * (b_count - w_count) / total
    return score

def minimax(board, depth, maximizing, ai_color, alpha, beta):
    if depth == 0:
        return evaluate_board(board, ai_color)

    current_color = ai_color if maximizing else opponent(ai_color)
    moves = get_valid_moves(board, current_color)

    if not moves:
        return evaluate_board(board, ai_color)

    if maximizing:
        max_eval = float('-inf')
        for move in moves:
            new_board = make_move(board, move[0], move[1], current_color)
            eval_score = minimax(new_board, depth - 1, False, ai_color, alpha, beta)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            new_board = make_move(board, move[0], move[1], current_color)
            eval_score = minimax(new_board, depth - 1, True, ai_color, alpha, beta)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


def AI_move(board, ai_color):
    """
    Chooses the best move for the AI using minimax with alpha-beta pruning.
    Returns (row, col) or None if no valid moves exist.
    """
    valid_moves = get_valid_moves(board, ai_color)
    if not valid_moves:
        return None

    best_move = None
    best_value = float('-inf') if ai_color == BLACK else float('inf')

    # Limit depth to keep AI thinking time short
    depth = 3

    for move in valid_moves:
        new_board = make_move(board, move[0], move[1], ai_color)
        value = minimax(new_board, depth - 1, False, ai_color, float('-inf'), float('inf'))

        if ai_color == BLACK:
            if value > best_value:
                best_value = value
                best_move = move
        else:
            if value < best_value:
                best_value = value
                best_move = move

    print(f"AI ({ai_color}) chooses move: {best_move} with score {best_value:.2f}")
    return best_move


def get_valid_moves(board, color):
    return [(col, row) for col in range(8) for row in range(8) if valid_move(board, row, col, color)]

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
    updated_board = copy.deepcopy(board)
    updated_board[x][y] = color
    for dx, dy in directions:
        row, col = x + dx, y + dy
        flips = []
        while 0 <= row < 8 and 0 <= col < 8 and updated_board[row][col] == opponent(color):
            flips.append((row, col))
            row += dx
            col += dy
        if 0 <= row < 8 and 0 <= col < 8 and updated_board[row][col] == color:
            for r, c in flips:
                updated_board[r][c] = color
    return updated_board


def count(board):
    black = sum(row.count(BLACK) for row in board)
    white = sum(row.count(WHITE) for row in board)
    return black, white

def print_board(board):
    # print current state of the board
    print("   " + " ".join(str(x) for x in range(8)))
    for y in reversed(range(8)):  # show (0,0) at bottom left
        print(f"{y}  " + " ".join(board[y]))
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
        b_count, w_count = count(board)
        print("Black Score: " + str(b_count))
        print("White Score: " + str(w_count))
        moves = get_valid_moves(board, current_color)
        if not moves:
            print(current_color + " has 0 valid moves, skip turn")
            current_color = opponent(current_color)
            if not get_valid_moves(board, current_color):
                print("No moves for anyome. End of game")
                break
            continue
        if AI and current_color == AI_color:
            move = AI_move(board, AI_color)
            if move:
                row, col = move
            else:
                print("No AI yet.")
                break
        else:
            print(current_color + "'s turn. Possible moves: " + str(moves))
            move = input("Enter (x, y) as your move. If you wish to undo a move, enter 'undo': ").strip()
            if move == 'undo':
                if undo:
                    board = undo.pop()
                    current_color = opponent(current_color)
                    continue
                else:
                    print("No moves to undo")
                    continue
            try:
                x_move, y_move = map(int, move.split())
                row, col = y_move, x_move
                if (row, col) not in moves:
                    print("Move invalid")
                    continue
            except:
                print("Wrong input format. Input should be 'x y'")
                continue
        undo.append(copy.deepcopy(board))
        board = make_move(board, row, col, current_color)
        current_color = opponent(current_color)

    print_board(board)
    b_count, w_count = count(board)
    print("Final Score -> Black: " + str(b_count) + ", White: " + str(w_count))
    if b_count > w_count:
        print("Black wins!")
    elif b_count < w_count:
        print("White wins!")
    else:
        print("Draw!")
        

if __name__ == '__main__':
    play()
