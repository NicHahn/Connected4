# library working with arrays --- up to 50x faster than normal list(arrays)
import numpy as np
import pygame
import sys
import math
import random

BLUE = pygame.Color(0, 0, 250)
BLACK = pygame.Color(0, 0, 0)
WHITE = (255, 255, 255)
GREY = (211, 211, 211)
GREY2 = (200, 200, 200)
RED = (255, 0, 0)
YELLOW = (255, 255, 51)
ROW = 6
COLUMN = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4


def create_board():
    board = np.zeros((ROW, COLUMN))
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW-1][col] == 0


def get_next_open_row(board, col):
    for row in range(ROW):
        if board[row][col] == 0:
            return row


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN-3):
        for r in range(ROW):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN):
        for r in range(ROW-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diaganols
    for c in range(COLUMN-3):
        for r in range(ROW-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diaganols
    for c in range(COLUMN-3):
        for r in range(3, ROW):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    # if window.count(piece) == 4:
    #     score += 100
    if window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score Horizontal
    for r in range(ROW):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COLUMN):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score posiive sloped diagonal
    for r in range(ROW-3):
        for c in range(COLUMN-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW-3):
        for c in range(COLUMN-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0


def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


def draw_board(board):
    for c in range(COLUMN):
        for r in range(ROW):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r *
                                            SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, WHITE, (c * SQUARESIZE +
                                               OFFSET, r * SQUARESIZE+SQUARESIZE + OFFSET), RADIUS)

    for c in range(COLUMN):
        for r in range(ROW):
            if board[r][c] == 1:
                pygame.draw.circle(
                    screen, RED, (c * SQUARESIZE + OFFSET, height - int(r * SQUARESIZE + OFFSET)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (c * SQUARESIZE +
                                                    OFFSET, height - int(r * SQUARESIZE + OFFSET)), RADIUS)

    pygame.display.update()


def draw_board_extend():
    draw_button(700, 450, BLACK, 300, 2, None)
    draw_button(700, 0, BLACK, 300, 2, None)
    draw_button(700, 698, BLACK, 300, 2, None)
    pygame.draw.line(screen, BLACK, (700, 2), (700, 700), 2)
    pygame.draw.line(screen, BLACK, (998, 2), (998, 700), 2)
    draw_button(775, 500, GREY, 150, 60, 'Restart')
    draw_button(775, 600, GREY, 150, 60, 'Quit')
    draw_button(790, 100, GREY,  120, 60, 'Easy')
    draw_button(790, 200, GREY,  120, 60, 'Medium')
    draw_button(790, 300, GREY,  120, 60, 'Hard')
    label = b_font.render('CHOOSE DIFFICULTY', True, BLACK)
    screen.blit(label, (705, 20))


def text_object(text):
    label = b_font.render(text, True, BLACK)
    return label


def draw_button(x, y, color, width, height, text):
    pygame.draw.rect(screen, color, (x, y, width, height))
    if text:
        label = text_object(text)
        label_rec = label.get_rect()
        label_rec.center = (x + width/2, y + height/2)
        screen.blit(label, label_rec)

def is_button_preessed(xpos, ypos, x, y, width, height):
    return (xpos >= x and xpos <= x + width and ypos >= y and ypos <= y + height)

def button_hover( posx, posy, x, y, width, height, text):
    if (posx >= x and posx <= x + width and posy >= y and posy <= y + height):
        pygame.draw.rect(screen, GREY2, (x, y, width, height))
    else:
        pygame.draw.rect(screen, GREY, (x, y, width, height))
    if text:
        label = text_object(text)
        label_rec = label.get_rect()
        label_rec.center = (x + width/2, y + height/2)
        screen.blit(label, label_rec)


def redraw_buttons_hover(posx, posy):
    button_hover(posx, posy, 775, 600, 150, 60, 'Quit')
    button_hover(posx, posy, 775, 500, 150, 60, 'Restart')
    button_hover(posx, posy, 790, 100, 120, 60, 'Easy')
    button_hover(posx, posy, 790, 200, 120, 60, 'Medium')
    button_hover(posx, posy, 790, 300, 120, 60, 'Hard')
  
pygame.init()
SQUARESIZE = 100
width = COLUMN * SQUARESIZE
height = (ROW + 1) * SQUARESIZE
RADIUS = int(SQUARESIZE/2 - 5)
OFFSET = int(SQUARESIZE/2)
size = (width + 300, height)
myfont = pygame.font.SysFont("monospace", 75)
b_font = pygame.font.SysFont('Comic Sans MS', 40)
pygame.display.set_caption('Connected 4')
screen = pygame.display.set_mode(size)
screen.fill(WHITE)


def game():
    while True:
        # Setup game
        board = create_board()
        draw_board(board)
        draw_board_extend()
        difficulty = 1
        game_over = False
        turn = PLAYER
        while not game_over:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(screen, WHITE, (0, 0, width, SQUARESIZE))
                    posx, posy = event.pos
                    if posx <= width - SQUARESIZE/2:
                        if turn == PLAYER:
                            pygame.draw.circle(
                                screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
                        else:
                            pygame.draw.circle(
                                screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
                    redraw_buttons_hover(posx, posy)
                pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    posx, posy = event.pos
                    if turn == PLAYER and posx <= width:

                        col = int(math.floor(posx/SQUARESIZE))
                        if is_valid_location(board, col):
                            drop_piece(board, get_next_open_row(
                                board, col), col, PLAYER_PIECE)
                            draw_board(board)
                            if winning_move(board, PLAYER_PIECE):
                                draw_board(board)
                                label = myfont.render("RED wins!!", 1, BLACK)
                                screen.blit(label, (20, 10))
                                game_over = True
                                pygame.time.wait(3000)
                                break
                            draw_board(board)

                            turn += 1
                            turn = turn % 2
                    # Check if a button is pressed
                    elif posx > width:
                        # Pressed Quit
                        if is_button_preessed(posx, posy, 775, 600, 150, 60):
                            sys.exit()
                        # Pressed Restart
                        elif is_button_preessed(posx, posy, 775, 500, 150, 60):
                            game_over = True
                            break
                        # Choose difficulty
                        elif is_button_preessed(posx, posy, 790, 100, 120, 60):
                            difficulty = 1
                        elif is_button_preessed(posx, posy, 790, 200, 120, 60):
                            difficulty = 3
                        elif is_button_preessed(posx, posy, 790, 300, 120, 60):
                            difficulty = 5

            if turn == AI and not game_over:
                # col = random.randint(0, COLUMN - 1)
                col, test = minimax(board, difficulty, -
                                    math.inf, math.inf, True)
                if is_valid_location(board, col):
                    drop_piece(board, get_next_open_row(
                        board, col), col, AI_PIECE)
                    if winning_move(board, AI_PIECE):
                        draw_board(board)
                        label = myfont.render("YELLOW wins!!", 1, BLACK)
                        screen.blit(label, (200, 10))
                        game_over = True
                        pygame.time.wait(3000)
                        break

                    draw_board(board)

                    turn += 1
                    turn = turn % 2


if __name__ == "__main__":
    game()
