import math
import copy
import threading
import time

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
    # Positional weights — common heuristic from Othello AI research
    WEIGHTS = [
        [100, -20, 10,  5,  5, 10, -20, 100],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [10,  -2,  5,  1,  1,  5,  -2,  10],
        [5,   -2,  1,  0,  0,  1,  -2,   5],
        [5,   -2,  1,  0,  0,  1,  -2,   5],
        [10,  -2,  5,  1,  1,  5,  -2,  10],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [100, -20, 10,  5,  5, 10, -20, 100],
    ]

    b_score = 0
    w_score = 0

    for r in range(8):
        for c in range(8):
            if board[r][c] == 'B':
                b_score += WEIGHTS[r][c]
            elif board[r][c] == 'W':
                w_score += WEIGHTS[r][c]

    # Normalize result to [-10, +10]
    total = abs(b_score) + abs(w_score)
    if total == 0:
        return 0

    normalized = 10 * (b_score - w_score) / total
    return normalized


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
            updated_board = make_move(board, move[0], move[1], current_color)
            eval_score = minimax(updated_board, depth - 1, False, ai_color, alpha, beta)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            updated_board = make_move(board, move[0], move[1], current_color)
            eval_score = minimax(updated_board, depth - 1, True, ai_color, alpha, beta)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


def AI_move(board, ai_color, depth):
    """
    Chooses the best move for the AI using minimax with alpha-beta pruning.
    Returns (row, col) or None if no valid moves exist.
    """
    valid_moves = get_valid_moves(board, ai_color)
    if not valid_moves:
        return None

    best_move = None
    best_value = float('-inf') if ai_color == BLACK else float('inf')

    # Limit depth — higher = smarter but slower AI
    depth = 4

    for move in valid_moves:
        updated_board = make_move(board, move[0], move[1], ai_color)
        value = minimax(updated_board, depth - 1, False, ai_color, float('-inf'), float('inf'))

        if ai_color == BLACK:
            if value > best_value:
                best_value = value
                best_move = move
        else:
            if value < best_value:
                best_value = value
                best_move = move

    print()
    print(f"AI ({ai_color}) chooses move: {best_move} with score {best_value:.2f}")
    return best_move


def get_valid_moves(board, color):
    return [(x, y) for x in range(8) for y in range(8) if valid_move(board, x, y, color)]


def valid_move(board, x, y, color):
    if board[y][x] != NONE:
        return False
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < 8 and 0 <= ny < 8) or board[ny][nx] != opponent(color):
            continue
        # Found opponent next to us, continue in this direction
        nx += dx
        ny += dy
        while 0 <= nx < 8 and 0 <= ny < 8:
            if board[ny][nx] == NONE:
                break
            if board[ny][nx] == color:
                return True
            nx += dx
            ny += dy
    return False

def make_move(board, x, y, color):
    updated_board = copy.deepcopy(board)
    updated_board[y][x] = color
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        flips = []
        while 0 <= nx < 8 and 0 <= ny < 8 and updated_board[ny][nx] == opponent(color):
            flips.append((nx, ny))
            nx += dx
            ny += dy
        if 0 <= nx < 8 and 0 <= ny < 8 and updated_board[ny][nx] == color:
            for fx, fy in flips:
                updated_board[fy][fx] = color
    return updated_board

def count(board):
    black = sum(row.count(BLACK) for row in board)
    white = sum(row.count(WHITE) for row in board)
    return black, white

def print_board(board):
    print("   " + " ".join(str(x) for x in range(8)))  # column headers
    for y in reversed(range(8)):  # bottom to top
        row_str = f"{y}  " + " ".join(board[y][x] for x in range(8))
        print(row_str)
    print()


def play():
    # main game loop
    board = [[NONE for _ in range(8)] for _ in range(8)]
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
                x, y = move
            else:
                print("No AI yet.")
                break
        else:
            print(current_color + "'s turn. Possible moves: " + str(moves))
            move = input("Enter (x, y) as your move. If you wish to undo a move, enter 'undo': ").strip()
            if move.lower() == 'undo':
                if len(undo) > 0:
                    board = undo.pop()
                    current_color = opponent(current_color)
                    # Undo AI move if playing against AI
                    if AI and len(undo) > 0:
                        board = undo.pop()
                        current_color = opponent(current_color)
                else:
                    print("No moves to undo")
                    continue  # skip the rest of the loop

            try:
                x_move, y_move = map(int, move.split())
                x, y = x_move, y_move
                if (x, y) not in moves:
                    print("Move invalid")
                    continue
            except:
                print("Wrong input format. Input should be 'x y'")
                continue
        undo.append(copy.deepcopy(board))
        board = make_move(board, x, y, current_color)
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
    
    import math
import copy
import threading
import time

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
    # Positional weights — common heuristic from Othello AI research
    WEIGHTS = [
        [100, -20, 10,  5,  5, 10, -20, 100],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [10,  -2,  5,  1,  1,  5,  -2,  10],
        [5,   -2,  1,  0,  0,  1,  -2,   5],
        [5,   -2,  1,  0,  0,  1,  -2,   5],
        [10,  -2,  5,  1,  1,  5,  -2,  10],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [100, -20, 10,  5,  5, 10, -20, 100],
    ]

    b_score = 0
    w_score = 0

    for r in range(8):
        for c in range(8):
            if board[r][c] == 'B':
                b_score += WEIGHTS[r][c]
            elif board[r][c] == 'W':
                w_score += WEIGHTS[r][c]

    # Normalize result to [-10, +10]
    total = abs(b_score) + abs(w_score)
    if total == 0:
        return 0

    normalized = 10 * (b_score - w_score) / total
    return normalized


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
            updated_board = make_move(board, move[0], move[1], current_color)
            eval_score = minimax(updated_board, depth - 1, False, ai_color, alpha, beta)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            updated_board = make_move(board, move[0], move[1], current_color)
            eval_score = minimax(updated_board, depth - 1, True, ai_color, alpha, beta)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


def AI_move(board, ai_color, depth=3):
    """
    Chooses the best move for the AI using minimax with alpha-beta pruning.
    Returns (best_move, best_value) or (None, None) if no valid moves exist.
    """
    valid_moves = get_valid_moves(board, ai_color)
    if not valid_moves:
        return None, None

    best_move = None
    best_value = float('-inf') if ai_color == BLACK else float('inf')

    for move in valid_moves:
        updated_board = make_move(board, move[0], move[1], ai_color)
        value = minimax(updated_board, depth - 1, False, ai_color, float('-inf'), float('inf'))

        if ai_color == BLACK:
            if value > best_value:
                best_value = value
                best_move = move
        else:
            if value < best_value:
                best_value = value
                best_move = move

    return best_move, best_value



def get_valid_moves(board, color):
    return [(x, y) for x in range(8) for y in range(8) if valid_move(board, x, y, color)]


def valid_move(board, x, y, color):
    if board[y][x] != NONE:
        return False
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < 8 and 0 <= ny < 8) or board[ny][nx] != opponent(color):
            continue
        # Found opponent next to us, continue in this direction
        nx += dx
        ny += dy
        while 0 <= nx < 8 and 0 <= ny < 8:
            if board[ny][nx] == NONE:
                break
            if board[ny][nx] == color:
                return True
            nx += dx
            ny += dy
    return False

def make_move(board, x, y, color):
    updated_board = copy.deepcopy(board)
    updated_board[y][x] = color
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        flips = []
        while 0 <= nx < 8 and 0 <= ny < 8 and updated_board[ny][nx] == opponent(color):
            flips.append((nx, ny))
            nx += dx
            ny += dy
        if 0 <= nx < 8 and 0 <= ny < 8 and updated_board[ny][nx] == color:
            for fx, fy in flips:
                updated_board[fy][fx] = color
    return updated_board

def count(board):
    black = sum(row.count(BLACK) for row in board)
    white = sum(row.count(WHITE) for row in board)
    return black, white

def print_board(board):
    print("   " + " ".join(str(x) for x in range(8)))  # column headers
    for y in reversed(range(8)):  # bottom to top
        row_str = f"{y}  " + " ".join(board[y][x] for x in range(8))
        print(row_str)
    print()


def play():
    # main game loop
    board = [[NONE for _ in range(8)] for _ in range(8)]
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
            # Create event to stop the timer early when AI finishes
            stop_event = threading.Event()
            timer_thread = threading.Thread(target=countdown_timer, args=(stop_event, 3))
            timer_thread.start()

            start_time = time.time()
            best_move, best_value = AI_move(board, AI_color, depth=4)
            elapsed = time.time() - start_time

            # signal timer to stop and wait for it
            stop_event.set()
            timer_thread.join()

            # Print clean AI result
            print()  # new line
            if best_move:
                x, y = best_move
                print(f"AI ({AI_color}) chooses move: {best_move} with score {best_value:.2f}")
            else:
                print("AI has no valid moves.")
                break
            print(f"AI took {elapsed:.3f} seconds to decide.")
            
        else:
            print(current_color + "'s turn. Possible moves: " + str(moves))
            move = input("Enter (x, y) as your move. If you wish to undo a move, enter 'undo': ").strip()
            if move.lower() == 'undo':
                if len(undo) > 0:
                    board = undo.pop()
                    current_color = opponent(current_color)
                    # Undo AI move if playing against AI
                    if AI and len(undo) > 0:
                        board = undo.pop()
                        current_color = opponent(current_color)
                else:
                    print("No moves to undo")
                    continue  # skip the rest of the loop

            try:
                x_move, y_move = map(int, move.split())
                x, y = x_move, y_move
                if (x, y) not in moves:
                    print("Move invalid")
                    continue
            except:
                print("Wrong input format. Input should be 'x y'")
                continue
        undo.append(copy.deepcopy(board))
        board = make_move(board, x, y, current_color)
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
    
def countdown_timer(stop_event, seconds):
    for remaining in range(seconds, 0, -1):
        if stop_event.is_set():
            # clear the timer line and exit
            print("\r" + " " * 40 + "\r", end="", flush=True)
            return
        print(f"\rAI thinking... {remaining:2d}s remaining", end="", flush=True)
        time.sleep(1)
    # final message when time runs out (only if not stopped)
    if not stop_event.is_set():
        print("\rAI thinking... time up!                   ")


if __name__ == '__main__':
    play()
