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
lighter_blue = (136, 179, 247)
lightest_blue = (189, 214, 255)

red = (219, 11, 0)
light_red = (240, 149, 144)
lightest_red = (255, 228, 227)

yellow = (255, 251, 0)
light_yellow = (255, 253, 150)
lightest_yellow = (252, 252, 217)

# turn order
turn = 1
next_turn = 2


def convert_to_coord(board, column):
    '''given a legend num, return the coords the piece will land'''
    if column == 0:
        return 0
    for row in y_points[::-1]:
        if board[(column, row)] == 0:
            return row
    return 0


def get_valid_moves(board):
    '''a list of all valid moves' locations is created'''
    valid_moves = []

    for i in x_points:

        if board[(i, 150)] == 0:

            valid_moves.append(i)

    return valid_moves


def make_random_move(board, turn):
    '''a random move is chosen out of the free squares'''
    valid_moves = get_valid_moves()

    n = round((len(valid_moves) - 1) * random.random())

    move_x = valid_moves[n]
    move_y = convert_to_coord(move_x)

    board[(move_x, move_y)] = turn


def four_in_a_row(board, y_level, turn):
    '''returns True/False depending on whether or not 4 on the same y level are connected'''

    for i in range(len(x_points)- 3):

        if (
        turn == board[(x_points[i], y_level)] == board[(x_points[i+1], y_level)] ==
        board[(x_points[i+2], y_level)] == board[(x_points[i+3], y_level)]
        ):
            return True

    else:
        return False


def four_in_a_column(board, x_level, turn):
    '''returns True/False depending on whether or not 4 on the same x level are connected'''

    for i in range(len(y_points)- 3):

        if (
        turn == board[(x_level, y_points[i])] == board[(x_level, y_points[i+1])]
        == board[(x_level, y_points[i+2])] == board[(x_level, y_points[i+3])]
        ):
            return True

    else:
        return False


def is_win(board, turn):

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
    """Checks if there are no moves left to be played"""
    return all(value != 0 for value in board_positions.values())


def computer_win_check(board, turn):
    '''creates a hypothetical board with all possible moves the computer can make next and tests each move for a win to find all winning moves'''
    winning_moves = []

    hypothetical_board = copy.deepcopy(board)

    move = get_valid_moves(hypothetical_board)

    for i in move:

        hypothetical_board[(i, convert_to_coord(hypothetical_board, i))] = turn

        if is_win(hypothetical_board, turn):

            winning_moves.append(i)

        hypothetical_board = copy.deepcopy(board)

    return winning_moves


def next_turn_loss_check(board, turn, next_turn):
    '''next_turn should be called with next_turn to see if the player will win next'''
    '''this function should be run after computer_win_check because preventing a loss during the next turn should not precede winning immdediately'''
    losing_moves = []

    hypothetical_board = copy.deepcopy(board)

    move = get_valid_moves(hypothetical_board)

    for i in move:

        hypothetical_board[(i, convert_to_coord(hypothetical_board, i))] = next_turn

        if is_win(hypothetical_board, next_turn):

            losing_moves.append(i)

        hypothetical_board = copy.deepcopy(board)

    return losing_moves


def force_win_check(board, turn, next_turn):

    move = get_valid_moves(board)

    for i in move:

        hypothetical_board1 = copy.deepcopy(board)

        hypothetical_board1[(i, convert_to_coord(hypothetical_board1, i))] = turn

        move2 = computer_win_check(hypothetical_board1, turn)

        if len(move2) > 0:

            hypothetical_board2 = copy.deepcopy(hypothetical_board1)

            hypothetical_board2[(move2[0], convert_to_coord(hypothetical_board2, move2[0]))] = next_turn

            move3 = computer_win_check(hypothetical_board2, turn)

            if len(move3) > 0 and len(next_turn_loss_check(hypothetical_board2, turn, next_turn)) < 1:

                return [i]
    return []


def forced_loss_check(board, turn, next_turn):
    '''sees if the computer can win in 2 turns by playing a move that cannot be blocked'''

    return force_win_check(board, next_turn, turn)


def pick_random_safe_move(board, turn, next_turn):
    """Picks a random move that does not result in an instant loss and doesn't result in a win condition getting taken away"""
    valid_moves = get_valid_moves(board)
    safe_moves = []
    safe_and_ideal = []

    for move in valid_moves:

        hypothetical_board = copy.deepcopy(board)

        hypothetical_board[(move, convert_to_coord(hypothetical_board, move))] = turn

        if len(next_turn_loss_check(hypothetical_board, turn, next_turn)) < 1:

            safe_moves.append(move)

    for move in safe_moves:

        hypothetical_board = copy.deepcopy(board)

        hypothetical_board[(move, convert_to_coord(hypothetical_board, move))] = turn

        if len(computer_win_check(hypothetical_board, turn)) < 1:

            safe_and_ideal.append(move)

    print(f'Safe and ideal moves = {safe_and_ideal}')
    print(f'Safe moves = {safe_moves}')

    if len(safe_and_ideal) > 0:
        return [safe_and_ideal[round((len(safe_and_ideal) - 1) * random.random())]]

    elif len(safe_moves) > 0:
        return [safe_moves[round((len(safe_moves) - 1) * random.random())]]

    return [valid_moves[0]]


def AI_decision():

    move = computer_win_check(board_positions, turn)
    print(f'Found winning move, move = {move}')
    if len(move) < 1:

        move = next_turn_loss_check(board_positions, turn, next_turn)
        print(f'Must block or lose, move = {move}')
        if len(move) < 1:

            move = force_win_check(board_positions, turn, next_turn)
            print(f'Found a move to force a win, move = {move}')
            if len(move) < 1:

                move = forced_loss_check(board_positions, turn, next_turn)
                print(f'Must block an incoming forced loss, move = {move}')
                if len(move) < 1:

                    move = pick_random_safe_move(board_positions, turn, next_turn)
                    print(f'Random safe move, move = {move}')

    board_positions[(move[0], convert_to_coord(board_positions, move[0]))] = turn


def create_board_positions():
    with open("board.csv", "r") as file:
        file_reader = csv.reader(file)
        return {(int(row[0]), int(row[1])): 0 for row in file_reader}


class circle:

    highlighted = False
    expected_move = False
    value = 0

    def __init__(self, position):
        self.position = position
        self.draw()

    def get_colour(self):

        if self.value == 0:

            if self.highlighted:

                if self.expected_move:
                    if turn == 1:
                        return light_red
                    else:
                        return lighter_blue

                else:
                    if turn == 1:
                        return lightest_red
                    else:
                        return lightest_blue

            else:
                return grey

        elif self.value == 1:
            return red

        else:
            return blue


    def draw(self):
        pygame.draw.circle(screen, self.get_colour(), self.position, 40)

# creates a empty
board_positions = create_board_positions()
x_points = [50, 150, 250, 350, 450, 550, 650]
y_points = [150, 250, 350, 450, 550, 650]
highlighted_col = 0
expected_row = 0
circles = [circle(position) for position in board_positions]
tied = False
game = "playing"
coin_flip = random.randint(0, 1)

if coin_flip == 1:
    playing = "Computer"
    next_to_play = "Player"
else:
    playing = "Player"
    next_to_play = "Computer"


running = True
while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:  # if quit is selected the game stops the playing loop

            running = False

        if playing == "Player" and event.type == pygame.MOUSEBUTTONUP and game == "playing":
            if expected_row != 0:
                board_positions[(highlighted_col, expected_row)] = turn

                if is_win(board_positions, turn):
                    game = "over"
                elif is_tied(board_positions):
                    game = "over"
                    tied = True
                else:
                    turn, next_turn = next_turn, turn
                    playing, next_to_play = next_to_play, playing

    screen.fill(black)
    mouse_location = pygame.mouse.get_pos()

    for i in x_points:
        if mouse_location[0] < i + 50 and mouse_location[0] > i - 50 and mouse_location[1] > 100:
            highlighted_col =  i
            break

    expected_row = convert_to_coord(board_positions, highlighted_col)

    for circle in circles:
        circle.value = board_positions[circle.position]
        circle.highlighted = circle.position[0] == highlighted_col
        circle.expected_move = circle.position == (highlighted_col, expected_row)
        circle.draw()

    if game == "playing":
        screen.blit(arial_s.render(f'{playing} to play', True, white), (220, 25))

        if playing == "Computer":
            AI_decision()

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

    pygame.display.flip()

pygame.quit()