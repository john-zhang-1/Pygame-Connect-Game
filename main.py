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

# colours
white = (255, 255, 255)
black = (0, 0, 0)
grey = (201, 201, 201)
charcoal = (43, 42, 42)
dark_grey = (201, 201, 201)

blue = (42, 28, 230)
light_blue = (136, 179, 247)
lightest_blue = (189, 214, 255)
dark_blue = (27, 16, 179)

blue_gradients = []
for i in range(8):
    blue_gradients.append((light_blue[0] - i * 3, light_blue[1] - i * 3, light_blue[2] - i * 3))
blue_gradients.extend(blue_gradients[::-1])

light_blue_gradients = []
for i in range(8):
    light_blue_gradients.append((lightest_blue[0] - i * 3, lightest_blue[1] - i * 3, lightest_blue[2] - i * 3))
light_blue_gradients.extend(light_blue_gradients[::-1])

red = (207, 32, 23)
light_red = (240, 149, 144)
lightest_red = (255, 228, 227)
dark_red = (163, 14, 7)

red_gradients = []
for i in range(8):
    red_gradients.append((light_red[0] - i * 3, light_red[1] - i * 3, light_red[2] - i * 3))
red_gradients.extend(red_gradients[::-1])

light_red_gradients = []
for i in range(8):
    light_red_gradients.append((lightest_red[0] - i * 3, lightest_red[1] - i * 3, lightest_red[2] - i * 3))
light_red_gradients.extend(light_red_gradients[::-1])

# sound effects
piece_drop = pygame.mixer.Sound("sounds/Piece drop.wav")
pygame.mixer.Sound.set_volume(piece_drop, 0.8)
game_over = pygame.mixer.Sound("sounds/Game Over.wav")
pygame.mixer.Sound.set_volume(game_over, 0.8)

# music
pygame.mixer.music.load("sounds/Playing music.wav")
pygame.mixer.music.set_volume(0.4)

# turn order
turn = 1
next_turn = 2

# x and y pixel coordinates of the circles
x_points = [50, 150, 250, 350, 450, 550, 650]
y_points = [150, 250, 350, 450, 550, 650]


def convert_to_coord(board, column):
    '''Given a column, return the row the piece will land'''
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


def make_move(board, column, turn):
    '''Given the column, board and turn, places the turn piece on the column of the board'''
    board[(column, convert_to_coord(board, column))] = turn
    pygame.mixer.Channel(1).play(piece_drop)


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
        make_move(hypothetical_board, i, turn)
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
        make_move(hypothetical_board1, i, turn)

        move2 = computer_win_check(hypothetical_board1, turn)

        if len(move2) > 0:

            hypothetical_board2 = copy.deepcopy(hypothetical_board1)

            if len(next_turn_loss_check(hypothetical_board2, next_turn)) < 1:

                make_move(hypothetical_board2, move2[0], next_turn)

                move3 = computer_win_check(hypothetical_board2, turn)

                if len(move3) > 0:

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
        make_move(hypothetical_board, move, turn)

        if len(next_turn_loss_check(hypothetical_board, next_turn)) < 1:

            safe_moves.append(move)

    for move in safe_moves:
        hypothetical_board = copy.deepcopy(board)
        make_move(hypothetical_board, move, turn)

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
    move = (move[0], convert_to_coord(board_positions, move[0]))
    make_move(board_positions, move[0], turn)
    global last_move
    # changes global variable last_move to this move
    last_move = move

def create_board_positions():
    '''Reads the csv file that gives the pixel positions of the circles and creates a dictionary with initial values 0 as all circles are empty'''
    with open("board.csv", "r") as file:
        file_reader = csv.reader(file)
        return {(int(row[0]), int(row[1])): 0 for row in file_reader}


class circle:
    '''Circle class creating each circle in the game'''

    def __init__(self, position):
        self.position = position
        self.reset()

    def get_colour(self):

        if self.value == 0: # if it is empty

            if self.highlighted: # if the circle is highlighted while empty, it becomes a lighter colour of the current turn

                frame = ((pygame.time.get_ticks() % 2000))
                frame = frame // 125

                if self.expected_move:  # if bottommost playable location, darker

                    if turn == 1:
                        return red_gradients[frame]

                    else:
                        return blue_gradients[frame]

                else:   # lighter colour for the circles of the column
                    if turn == 1:
                        return light_red_gradients[frame]
                    else:
                        return light_blue_gradients[frame]

            else:   # if empty and not the highlighted column, grey
                return grey

        elif self.value == 1:   # if not empty, the circle is the colour of the piece played
            if self.last_move:
                return dark_red
            else:
                return red
        else:
            if self.last_move:
                return dark_blue
            else:
                return blue

    # draw method displays the circle on the pygame window
    def draw(self):
        if self.last_move:
            pygame.draw.circle(screen, black, self.position, 45)
        pygame.draw.circle(screen, self.get_colour(), self.position, 40)


    def reset(self):
        self.highlighted = False
        self.expected_move = False
        self.value = 0
        self.last_move = False


def display_text_ui(x_position, y_position, width, height, box_colour, text, text_colour, button):
    '''Draws text on the screen'''
    # If the text being drawn is on a button
    if button:
        # If mouse is hovering on it
        if (x_position < mouse_location[0] < x_position + width and
                y_position < mouse_location[1] < y_position + height):
            # if left click is happening while mouse is hovering over the button,
            # brighten the colour
            if left_click:
                colour_adjust = 15
            # if mouse is hovering over the button and the mouse is not being clicked,
            # brighten the colour even more
            else:
                colour_adjust = 25
                # if left mouse button has been released this frame
                if release_left_click:

                    if text == 'Play Again':

                        reset()
                        return

            new_colour = (box_colour[0] + colour_adjust, box_colour[1] + colour_adjust, box_colour[2] + colour_adjust)
            pygame.draw.rect(screen, new_colour, (x_position, y_position, width, height))

        else: # if the mouse is not hovering over the button
            pygame.draw.rect(screen, box_colour, (x_position, y_position, width, height))

    else: # if not a button
        pygame.draw.rect(screen, box_colour, (x_position, y_position, width, height))

    # choose text settings
    displayed_text = arial_s.render(text, True, text_colour)
    # blit text onto box
    screen.blit(displayed_text, (x_position + width/2 - displayed_text.get_width()/2,
                                 y_position + height/2 - displayed_text.get_height()/2))


def find_expected_row_and_column():
    for i in x_points:
        if mouse_location[0] < i + 50 and mouse_location[0] > i - 50 and mouse_location[1] > 100:
            # the column over which the mouse is hovering will be highlighted
            return i, convert_to_coord(board_positions, i)
    return 0, 0


def get_first_player():
    # randomly selects player or computer to play first
    coin_flip = random.randint(0, 1)

    if coin_flip == 1:
        playing = "Computer"
        next_to_play = "Player"
    else:
        playing = "Player"
        next_to_play = "Computer"

    return playing, next_to_play


def end_turn_actions():
    '''Functions called at the end of a player's turn after their move has been made'''
    global turn, next_turn, playing, next_to_play
    if is_win(board_positions, turn):
        game.set_state("won")
    elif is_tied(board_positions):
        game.set_state("tied")
    else:
        playing, next_to_play = next_to_play, playing  # keeps track of whose turn it is for piece colours
    turn, next_turn = next_turn, turn  # goes to next turn


def initialize():
    global board_positions, highlighted_col, expected_row, last_move, circles, tied, game
    global mouse_location, left_click, release_left_click, playing, next_to_play
    # creates a empty board
    board_positions = create_board_positions()

    # defines highlighted_col, expected_row and last_move initially to run the game
    highlighted_col = 0
    expected_row = 0
    last_move = (0, 0)

    # creates list of circle objects for each key in the board_positions dictionary
    # used for drawing and storing information about board states
    circles = [circle(position) for position in board_positions]

    # game conditions
    game = Game("playing")

    # input conditions
    mouse_location = (0, 0)
    left_click = False
    release_left_click = False

    playing, next_to_play = get_first_player()

    # starts music
    pygame.mixer.music.play(-1)


def reset():
    '''Resets game states for playing again'''
    global board_positions, highlighted_col, expected_row, last_move, circles, tied, game
    global mouse_location, left_click, release_left_click, playing, next_to_play

    board_positions = {key: 0 for key in board_positions}

    highlighted_col = 0
    expected_row = 0
    last_move = (0, 0)

    for circle in circles:
        circle.reset()
    # game conditions
    game = Game("playing")

    # input conditions
    mouse_location = (0, 0)
    left_click = False
    release_left_click = False

    playing, next_to_play = get_first_player()

    # unpauses music
    pygame.mixer.music.unpause()


class Game:
    '''Game state class to trigger functions at the moment when a game ends'''
    def __init__(self, state):
        self.state = state

    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.game_over_process()

    def game_over_process(self):
        self.start_next_time = pygame.time.get_ticks() + 5000
        # pauses music and plays game over effect
        pygame.mixer.music.pause()
        pygame.mixer.Channel(0).play(game_over)


if __name__ == '__main__':

    initialize()

    # main game loop
    running = True
    while running:
        # Check for all occurrences of events
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # loops stops when game is quit
                running = False
            if event.type == pygame.MOUSEBUTTONUP: # checks for left click being released
                release_left_click = True

        # storing user inputs in variables in the frame to use for functions
        mouse_location = pygame.mouse.get_pos()  # stores mouse location in variable
        left_click = pygame.mouse.get_pressed(num_buttons=3)[0] # stores left click in variable

        screen.fill(white)  # makes background black

        # finds the column the mouse is hovering over and the expected location where the piece would land
        highlighted_col, expected_row = find_expected_row_and_column()

        for circle in circles:
            # current value of circle, 0 for empty, 1 and 2 for played on that turn
            circle.value = board_positions[circle.position]

            if circle.value == 0:
                # if the circle's position is in the highlighted column the circle is highlighted
                circle.highlighted = circle.position[0] == highlighted_col
                # of the circle is the bottommost circle of the column it will be darker
                circle.expected_move = circle.position == (highlighted_col, expected_row)

            # if the circle's position is the same as the last move it will be darker
            circle.last_move = circle.position == last_move
            # draws the circle
            circle.draw()

        if game.state == "playing":
            display_text_ui(0, 10, 700, 80, charcoal, f'{playing} to play', white, False)

            if playing == "Computer":
                AI_decision()   # computer chooses a move
                pygame.mixer.Channel(1).play(piece_drop)

                end_turn_actions()

            if playing == "Player" and release_left_click:
                if expected_row != 0:  # if a column is full, expected_row will be 0 to ensure move cannot be played
                    last_move = (highlighted_col, expected_row) # stores move in global variable last_move
                    board_positions[last_move] = turn  # modifies dictionary storing game board state
                    pygame.mixer.Channel(1).play(piece_drop)

                    end_turn_actions()

        if game.state != "playing":
            if game.state == "tied":
                display_text_ui(0, 10, 700, 80, charcoal, 'Tie Game!', white, False)
            else:
                display_text_ui(0, 10, 700, 80, light_red if turn == 2 else light_blue, f'{playing} wins!', white, False)

            if pygame.time.get_ticks() >= game.start_next_time:
                display_text_ui(100, 320, 500, 80, charcoal, 'Play Again', white, True)
            if release_left_click:
                game.start_next_time = 0

        release_left_click = False

        pygame.display.flip() # makes the window display the game
        fps_clock.tick(64)
    pygame.quit()
