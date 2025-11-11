import math
import copy
import threading
import time

# Directions for move checking
directions = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),          (0, 1),
              (1, -1),  (1, 0), (1, 1)]

NONE, BLACK, WHITE = '.', 'B', 'W' # global constants for pieces

def opponent(color):
    '''
        returns the opponent color
    '''
    return BLACK if color==WHITE else WHITE

def evaluate_board(board, ai_color):
    '''
        board evaluation function, returns a score from -10 to 10
        positive score favors black, negative score favors white
    '''
    # weights for each position on the board
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

    b_score = 0 # black score
    w_score = 0 # white score

    # Calculate weighted scores
    for y in range(8): 
        for x in range(8):
            piece = board[y][x]
            weight = WEIGHTS[7 - y][x]
            if piece == BLACK: # black piece
                b_score += weight
            elif piece == WHITE: # white piece
                w_score += weight

    # ensure that result is in [-10, +10] to score board appropriately
    total = abs(b_score) + abs(w_score)
    if total == 0:
        return 0
    score = 10 * (b_score - w_score) / total
    return score


def minimax(board, depth, maximizing, ai_color, alpha, beta):
    '''
        Minimax algorithm. Maximizing for AI color, minimizing for opponent.
        Uses alpha-beta pruning to optimize search. Works by recursively evaluating
        possible moves up to a certain depth and returning the best score. 
        NOTE: We used LLM (GPT-4) to help write this function. We are allowed to use LLMS on this assignment
        provided we cite it appropriately.
    '''
    if depth == 0: # base case
        return evaluate_board(board, ai_color)

    current_color = ai_color if maximizing else opponent(ai_color) # determine whose turn it is
    moves = get_valid_moves(board, current_color) # get valid moves for current player

    if not moves: # no valid moves, evaluate board
        return evaluate_board(board, ai_color)

    if maximizing: # maximizing player (AI)
        max_eval = float('-inf') # initialize max evaluation
        for move in moves: # iterate through valid moves
            updated_board = make_move(board, move[0], move[1], current_color) # make the move
            eval_score = minimax(updated_board, depth - 1, False, ai_color, alpha, beta) # recursive call with decreased depth
            max_eval = max(max_eval, eval_score) # update max evaluation
            alpha = max(alpha, eval_score) # update alpha
            if beta <= alpha: # beta cut-off
                break
        return max_eval
    else: # minimizing player (opponent)
        min_eval = float('inf') # initialize min evaluation
        for move in moves: # iterate through valid moves
            updated_board = make_move(board, move[0], move[1], current_color) # make the move
            eval_score = minimax(updated_board, depth - 1, True, ai_color, alpha, beta) # recursive call with decreased depth
            min_eval = min(min_eval, eval_score) # update min evaluation
            beta = min(beta, eval_score) # update beta
            if beta <= alpha: # alpha cut-off
                break
        return min_eval


def AI_move(board, ai_color, depth=3):
    '''
    Chooses the best move for the AI using minimax with alpha-beta pruning. Returns (best_move, best_value) 
    or (None, None) if no valid moves exist. Works by evaluating all valid moves and selecting the one with the optimal score.
    '''
    valid_moves = get_valid_moves(board, ai_color) # get valid moves for AI color
    if not valid_moves: # no valid moves
        return None, None

    best_move = None
    best_value = float('-inf') if ai_color == BLACK else float('inf') # initialize best value

    for move in valid_moves: # iterate through valid moves
        updated_board = make_move(board, move[0], move[1], ai_color) # make the move
        value = minimax(updated_board, depth - 1, False, ai_color, float('-inf'), float('inf')) # evaluate move using minimax

        if ai_color == BLACK: # maximizing for black
            if value > best_value: # update best value and move
                best_value = value
                best_move = move
        else: # minimizing for white
            if value < best_value: # update best value and move
                best_value = value
                best_move = move

    return best_move, best_value # return best move and its value



def get_valid_moves(board, color):
    '''
        returns a list of valid moves for the given color. works as a wrapper for valid_move function
        with a list comprehension.
    '''
    return [(x, y) for x in range(8) for y in range(8) if valid_move(board, x, y, color)]


def valid_move(board, x, y, color):
    '''
        checks if the input move (x, y) is valid for the given color on the current board. a move is considered valid
        if it flips at least one opponent piece in any direction. this algorithm works by checking each direction from the
        move position to see if there is a sequence of opponent pieces followed by a piece of the player's color.
    '''
    if board[y][x] != NONE: # position already occupied
        return False
    for dx, dy in directions: # check all directions
        nx, ny = x + dx, y + dy
        if not (0 <= nx < 8 and 0 <= ny < 8) or board[ny][nx] != opponent(color):
            continue
        # found oppponent so continue in this direction
        nx += dx
        ny += dy
        while 0 <= nx < 8 and 0 <= ny < 8:
            if board[ny][nx] == NONE: # empty space, no flip possible
                break
            if board[ny][nx] == color: # valid move found
                return True
            nx += dx
            ny += dy
    return False

def make_move(board, x, y, color):
    '''
        makes the move (x, y) for the given color on the board and returns the updated board. assumes the move is valid. 
        it works by placing the piece on the board and then flipping all opponent pieces that are captured in each direction.
    '''
    updated_board = copy.deepcopy(board) # use deepcopy to avoid modifying original board
    updated_board[y][x] = color # place the piece
    for dx, dy in directions: # check all directions
        nx, ny = x + dx, y + dy # next position in direction
        flips = [] # list to store pieces to flip
        while 0 <= nx < 8 and 0 <= ny < 8 and updated_board[ny][nx] == opponent(color): # opponent piece found
            flips.append((nx, ny)) # add to flips
            nx += dx # move to next position
            ny += dy
        if 0 <= nx < 8 and 0 <= ny < 8 and updated_board[ny][nx] == color: # found own piece, flip the pieces
            for fx, fy in flips: 
                updated_board[fy][fx] = color
    return updated_board # return updated board

def count(board): # counts the number of black and white pieces on the board
    black = sum(row.count(BLACK) for row in board)
    white = sum(row.count(WHITE) for row in board)
    return black, white

def print_board(board): # prints the board to output
    print("   " + " ".join(str(x) for x in range(8)))  # column headers
    for y in reversed(range(8)):  # print board so that 0, 0 is bottom left
        row_str = f"{y}  " + " ".join(board[y][x] for x in range(8))
        print(row_str)
    print()

def countdown_timer(stop_event, seconds):
    '''
        countdown timer that runs in a separate thread. updates every second.
        stops if stop_event is set. used to show AI thinking time.
    '''
    for remaining in range(seconds, 0, -1): # countdown loop
        if stop_event.is_set():
            # clear the timer line and exit
            print("\r" + " " * 40 + "\r", end="", flush=True)
            return
        print(f"\rAI thinking... {remaining:2d}s remaining", end="", flush=True)
        time.sleep(1)
    # final message when time runs out (only if not stopped)
    if not stop_event.is_set():
        print("\rAI thinking... time up!                   ")


def play(): # main game loop
    # initialize board
    board = [[NONE for _ in range(8)] for _ in range(8)]
    board[3][3] = WHITE
    board[3][4] = BLACK
    board[4][3] = BLACK
    board[4][4] = WHITE
    undo = list() # list implemented as stack to undo a singular move
    player = input("Select Black (B) or White (W): ") # choose player color
    while player not in (BLACK, WHITE):
        player = input("Invalid: choose (B) or (W): ")
    current_color = BLACK # black starts first
    AI_color = opponent(player) # AI plays as the opposite color
    ai_on = input("Play against AI? (Y or N): ") # choose to play against AI
    while ai_on not in ['Y', 'N']:
        ai_on = input("Invalid input: Type Y or N: ")
    AI = False if ai_on == 'N' else True
    
    while True: # main loop
        print_board(board) # print current board
        print(evaluate_board(board, AI_color)) # print evaluation score
        b_count, w_count = count(board) # count pieces and print scores
        print("Black Score: " + str(b_count))
        print("White Score: " + str(w_count))
        moves = get_valid_moves(board, current_color) # find valid moves for current player and board state
        if not moves: # no valid moves, skip turn
            print(current_color + " has 0 valid moves, skip turn")
            current_color = opponent(current_color)
            if not get_valid_moves(board, current_color): # check if opponent also has no moves
                print("No moves for anyome. End of game")
                break
            continue
        if AI and current_color == AI_color: # AI's turn
            stop_event = threading.Event() # event to signal timer thread to stop
            # start timer for 30 seconds
            timer_thread = threading.Thread(target=countdown_timer, args=(stop_event, 30))
            timer_thread.start()

            start_time = time.time()
            best_move, best_value = AI_move(board, AI_color, depth=6) # get AI move
            elapsed = time.time() - start_time # calculate time taken to get move

            # signal timer to stop and wait for it
            stop_event.set()
            timer_thread.join()

            # print AI result
            print()  # new line
            if best_move: # valid move found
                x, y = best_move
                print(f"AI ({AI_color}) chooses move: {best_move}")
            else: # no valid moves
                print("AI has no valid moves.")
                break
            print(f"AI took {elapsed:.3f} seconds to decide.") # print time taken
            
        else:
            if current_color == BLACK: # print moves for current player
                print("Black's turn. Possible moves: " + str(moves))
            else:
                print("White's turn. Possible moves: " + str(moves))
            # get player move
            move = input("Enter (x, y) as your move. If you wish to undo a move, enter 'undo': ").strip()
            if move.lower() == 'undo': # handle undo
                if len(undo) > 0: # check if undo is possible
                    board = undo.pop() # revert to previous board state
                    current_color = opponent(current_color) # switch back current color
                    # undo ai move as well if playing against AI
                    if AI and len(undo) > 0:
                        board = undo.pop()
                        current_color = opponent(current_color)
                else: # no moves to undo
                    print("No moves to undo")
                    continue  # skip the rest of the loop

            try: # read player move
                x_move, y_move = map(int, move.split()) #
                x, y = x_move, y_move
                if (x, y) not in moves: # check if move is valid
                    print("Move invalid")
                    continue
            except: # handle invalid input format
                print("Wrong input format. Input should be 'x y'")
                continue
        undo.append(copy.deepcopy(board)) # save current board state for undo
        board = make_move(board, x, y, current_color) # make the move
        current_color = opponent(current_color) # switch turns

    print_board(board) # print final board
    b_count, w_count = count(board) # count final pieces
    print("Final Score -> Black: " + str(b_count) + ", White: " + str(w_count)) # print final scores
    # determine winner
    if b_count > w_count:
        print("Black wins!")
    elif b_count < w_count:
        print("White wins!")
    else:
        print("Draw!")

if __name__ == '__main__': # run the game in main entry point
    play()
