import random
import pygame
import csv
import copy

# initialize pygame
pygame.init()

# screen options

# screen size
width = 700
height = 700

# window options
fps_clock = pygame.time.Clock()  # set fps of program
screen = pygame.display.set_mode((width, height))  # set screen size
pygame.display.set_caption("Connect Four")  # set window caption

# fonts
arial = pygame.font.SysFont('Arial', 100)
arial_s = pygame.font.SysFont('Arial', 50)

# mouse location initialized
mouse_x = 0
mouse_y = 0

# colours
white = (255, 255, 255)
black = (0, 0, 0)
grey = (216, 223, 235)

blue = (3, 136, 252)
light_blue = (136, 179, 247)
lightest_blue = (189, 214, 255)

red = (219, 11, 0)
light_red = (240, 149, 144)
lightest_red = (255, 228, 227)

# turn order
turn = 1
next_turn = 2

# x and y pixel coordinates of the circles
x_points = [50, 150, 250, 350, 450, 550, 650]
y_points = [150, 250, 350, 450, 550, 650]

def convert_to_coord(board, column):
    '''Given a legend num, return the row the piece will land'''
    if column == 0:
        return 0
    for row in y_points[::-1]:
        if board[(column, row)] == 0:
            return row
    return 0


def get_valid_moves(board):
    '''A list of all valid moves' locations is created'''
    valid_moves = []

    for i in x_points:

        if board[(i, 150)] == 0:

            valid_moves.append(i)

    return valid_moves


def four_in_a_row(board, y_level, turn):
    '''Returns True if 4 on the given y level are connected, otherwise returns False'''

    for i in range(len(x_points)- 3):

        if (
        turn == board[(x_points[i], y_level)] == board[(x_points[i+1], y_level)] ==
        board[(x_points[i+2], y_level)] == board[(x_points[i+3], y_level)]
        ):
            return True

    else:
        return False


def four_in_a_column(board, x_level, turn):
    '''returns True if 4 on the given x level are connected, otherwise returns False'''

    for i in range(len(y_points)- 3):

        if (
        turn == board[(x_level, y_points[i])] == board[(x_level, y_points[i+1])]
        == board[(x_level, y_points[i+2])] == board[(x_level, y_points[i+3])]
        ):
            return True

    else:
        return False


def is_win(board, turn):
    '''Checks all winning combinations for a player and returns True if that player has won'''
    for i in y_points:

        if four_in_a_row(board, i, turn):
            return True

    for j in x_points:

        if four_in_a_column(board, j, turn):
            return True

    for k in range(3,7):

        for l in range(0,3):

            if (

            turn == board[(x_points[k], y_points[l])]
                    == board[(x_points[k-1], y_points[l+1])]
                    == board[(x_points[k-2], y_points[l+2])]
                    == board[(x_points[k-3], y_points[l+3])]
            ):
                return True

    for k in range(0,4):

        for l in range(0,3):

            if (
            turn == board[(x_points[k], y_points[l])]
                    == board[(x_points[k+1], y_points[l+1])]
                    == board[(x_points[k+2], y_points[l+2])]
                    == board[(x_points[k+3], y_points[l+3])]
            ):
                return True


def is_tied(board):
    '''Checks if there are no moves left to be played'''
    return all(value != 0 for value in board_positions.values())


def computer_win_check(board, turn):
    '''Creates a hypothetical board with all possible moves the computer can make next and tests each move for a win, then returns all winning moves'''
    winning_moves = []

    hypothetical_board = copy.deepcopy(board)
    move = get_valid_moves(hypothetical_board)

    for i in move:
        hypothetical_board[(i, convert_to_coord(hypothetical_board, i))] = turn
        if is_win(hypothetical_board, turn):

            winning_moves.append(i)

        hypothetical_board = copy.deepcopy(board)

    return winning_moves


def next_turn_loss_check(board, next_turn):
    '''creates a hypothetical board with all possible moves the player can make next and tests each move for a win, then returns all winning moves
    This function should be run after computer_win_check because preventing a loss during the next turn should not precede winning immdediately'''
    return computer_win_check(board, next_turn)


def force_win_check(board, turn, next_turn):
    """Creates a hypothetical board and performs each valid move, then creates a second hypothetical board with the move applied, and checks if there is a winning move by the computer
    If there is, the other player hypothetically attempts to block the winning move, then this function checks once more if there are winning moves.
    If there are, the first hypothetical move is returned as it would result in a forced victory for the computer"""
    move = get_valid_moves(board)

    for i in move:
        hypothetical_board1 = copy.deepcopy(board)
        hypothetical_board1[(i, convert_to_coord(hypothetical_board1, i))] = turn

        move2 = computer_win_check(hypothetical_board1, turn)

        if len(move2) > 0:
            hypothetical_board2 = copy.deepcopy(hypothetical_board1)
            hypothetical_board2[(move2[0], convert_to_coord(hypothetical_board2, move2[0]))] = next_turn

            move3 = computer_win_check(hypothetical_board2, turn)

            if len(move3) > 0 and len(next_turn_loss_check(hypothetical_board2, next_turn)) < 1:

                return [i]
    return []


def forced_loss_check(board, turn, next_turn):
    '''Sees if the computer can be forced to lose with the same strategy as the one described in force_win_check by the player, returns the move that will block the forced win'''
    return force_win_check(board, next_turn, turn)


def pick_random_safe_move(board, turn, next_turn):
    '''Returns a random move that does not result in an instant loss and doesn't result in a win condition getting taken away
    If that is impossible, returns a random move that does not result in an instant loss. Otherwise, returns a random move'''
    valid_moves = get_valid_moves(board)
    safe_moves = []
    safe_and_ideal = []

    for move in valid_moves:
        hypothetical_board = copy.deepcopy(board)
        hypothetical_board[(move, convert_to_coord(hypothetical_board, move))] = turn

        if len(next_turn_loss_check(hypothetical_board, next_turn)) < 1:

            safe_moves.append(move)

    for move in safe_moves:
        hypothetical_board = copy.deepcopy(board)
        hypothetical_board[(move, convert_to_coord(hypothetical_board, move))] = turn

        if len(computer_win_check(hypothetical_board, turn)) < 1:

            safe_and_ideal.append(move)

    if len(safe_and_ideal) > 0:
        return [safe_and_ideal[round((len(safe_and_ideal) - 1) * random.random())]]

    elif len(safe_moves) > 0:
        return [safe_moves[round((len(safe_moves) - 1) * random.random())]]

    return [valid_moves[0]]


def AI_decision():
    '''AI checks conditions from most to least important, then does the move. If a move is found it skips the rest of the tests'''
    move = computer_win_check(board_positions, turn)
    if len(move) < 1:

        move = next_turn_loss_check(board_positions, next_turn)
        if len(move) < 1:

            move = force_win_check(board_positions, turn, next_turn)
            if len(move) < 1:

                move = forced_loss_check(board_positions, turn, next_turn)
                if len(move) < 1:

                    move = pick_random_safe_move(board_positions, turn, next_turn)

    # Does the move by changing the value of the position to the computer's turn's value
    board_positions[(move[0], convert_to_coord(board_positions, move[0]))] = turn


def create_board_positions():
    '''Reads the csv file that gives the pixel positions of the circles and creates a dictionary with initial values 0 as all circles are empty'''
    with open("board.csv", "r") as file:
        file_reader = csv.reader(file)
        return {(int(row[0]), int(row[1])): 0 for row in file_reader}


class circle:
    '''Circle class creating each circle in the game'''
    highlighted = False
    expected_move = False
    value = 0

    def __init__(self, position):
        self.position = position
        self.draw()

    def get_colour(self):

        if self.value == 0: # if it is empty

            if self.highlighted: # if the circle is highlighted while empty, it becomes a lighter colour of the current turn

                if self.expected_move:  # if bottommost playable location, darker
                    if turn == 1:
                        return light_red
                    else:
                        return light_blue

                else:   # lighter colour for the circles of the column
                    if turn == 1:
                        return lightest_red
                    else:
                        return lightest_blue

            else:   # if empty and not the highlighted column, grey
                return grey

        elif self.value == 1:   # if not empty, the circle is the colour of the piece played
            return red

        else:
            return blue

    # draw method displays the circle on the pygame window
    def draw(self):
        pygame.draw.circle(screen, self.get_colour(), self.position, 40)

# creates a empty board
board_positions = create_board_positions()

# defines highlighted_col and expected_row initially to run the game
highlighted_col = 0
expected_row = 0

# creates list of circle objects for each key in the board_positions dictionary used for drawing and storing information about board states
circles = [circle(position) for position in board_positions]

# game conditions
tied = False
game = "playing"

# randomly selects player or computer to play first
coin_flip = random.randint(0, 1)

if coin_flip == 1:
    playing = "Computer"
    next_to_play = "Player"
else:
    playing = "Player"
    next_to_play = "Computer"

# main game loop
running = True
while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT: # loops stops when game is quit

            running = False

        if playing == "Player" and event.type == pygame.MOUSEBUTTONUP and game == "playing":
            if expected_row != 0: # if a column is full, expected_row will be 0 to ensure move cannot be played
                board_positions[(highlighted_col, expected_row)] = turn # modifies dictionary storing game board state

                if is_win(board_positions, turn):
                    game = "over"
                elif is_tied(board_positions):
                    game = "over"
                    tied = True
                else:
                    turn, next_turn = next_turn, turn # goes to next turn
                    playing, next_to_play = next_to_play, playing # keeps track of whose turn it is to display and for winning message

    screen.fill(black)  # makes background black

    mouse_location = pygame.mouse.get_pos() # stores mouse location in variable for use
    for i in x_points:
        if mouse_location[0] < i + 50 and mouse_location[0] > i - 50 and mouse_location[1] > 100:
            highlighted_col =  i
            # the column over which the mouse is hovering will be highlighted
            break

    expected_row = convert_to_coord(board_positions, highlighted_col)
    # finds the location the piece would appear if dropped on the highlighted col

    for circle in circles:
        circle.value = board_positions[circle.position] # current value of circle, 0 for empty, 1 and 2 for played on that turn
        circle.highlighted = circle.position[0] == highlighted_col  # if the circle's position is in the highlighted column the circle is highlighted
        circle.expected_move = circle.position == (highlighted_col, expected_row) # of the circle is the bottommost circle of the column it will be darker
        circle.draw()

    if game == "playing":
        screen.blit(arial_s.render(f'{playing} to play', True, white), (220, 25)) # displays turn message

        if playing == "Computer":
            AI_decision()   # computer chooses a move

            if is_win(board_positions, turn):
                game = "over"
                turn, next_turn = next_turn, turn
            elif is_tied(board_positions):
                game = "over"
                tied = True
            else:
                turn, next_turn = next_turn, turn
                playing, next_to_play = next_to_play, playing

    if game == "over":
        if tied:
            screen.blit(arial_s.render('Tie Game!', True, white), (220, 25))
        else:
            screen.blit(arial_s.render(f'{playing} wins!', True, white), (220, 25))
        
    pygame.display.flip() # makes the window display the game

pygame.quit()
