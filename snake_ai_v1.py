from random import randint
import pygame
from pygame.locals import *
import sys


HEIGHT = 20
WIDTH = 20

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)

FOOD = 0
UNDEF = int(1E3)
SNAKE = int(1E6)

LEFT = -1
RIGHT = 1
UP = -WIDTH
DOWN = WIDTH

DIRC_LIST = [LEFT, UP, RIGHT, DOWN]

#ფუნქცია ყველაფერს არესეთებს.
#გველი უბრუნდება საწყის "სიგრძეს" და თამაში იწყება თავიდან
def reset_all():
    global snake, board, snake_size, _snake, _board, _snake_size, food, score
    board = [0] * HEIGHT * WIDTH  # use one dimensional list to represent 2 dimensional board
    snake = [0] * (HEIGHT * WIDTH + 1)
    snake[0] = 1 * WIDTH + 1
    snake_size = score = 1

    _board = [0] * HEIGHT * WIDTH
    _snake = [0] * (HEIGHT * WIDTH + 1)
    _snake[0] = 1 * WIDTH + 1
    _snake_size = 1

    food = 7 * WIDTH + 8


#აკეთებს "დაფას"
def init_board(__snake, __size, __board):
    for i in range(HEIGHT * WIDTH):
        if i == food:
            __board[i] = FOOD
        elif not (i in __snake[:__size]):
            __board[i] = UNDEF
        else:
            __board[i] = SNAKE

# ამოწმებს შეუძლია თუ არა გველს მოძრაობა ნებისმიერი მიმართულებით
def can_move(pos, dirc):
    if dirc == UP and pos / WIDTH > 0:
        return True
    elif dirc == LEFT and pos % WIDTH > 0:
        return True
    elif dirc == DOWN and pos / WIDTH < HEIGHT - 1:
        return True
    elif dirc == RIGHT and pos % WIDTH < WIDTH - 1:
        return True
    return False

#საკვების ძებნის ფუნქცია (თუ იპოვა აბრუნდებს Found-ს და აგრძელებს ფუნქციონირებას)
def find_food_path_bfs(__food, __snake, __board):
    found = False
    q = [__food]  # not using Queue() because it is slower
    explored = [0] * (WIDTH * HEIGHT)
    while q:
        pos = q.pop(0)
        if explored[pos] == 1:
            continue
        explored[pos] = 1
        for dirc in DIRC_LIST:
            if can_move(pos, dirc):
                if pos + dirc == __snake[0]:
                    found = True
                if __board[pos + dirc] < SNAKE:
                    if __board[pos + dirc] > __board[pos] + 1:
                        __board[pos + dirc] = __board[pos] + 1
                    if explored[pos + dirc] == 0:
                        q.append(pos + dirc)

    return found

#პოულობს საით უნდა გააგრძელოს მიმართულება
def last_op():
    global snake_size, board, snake, food
    init_board(snake, snake_size, board)
    find_food_path_bfs(food, snake, board)
    mini = SNAKE
    mv = None
    for dirc in DIRC_LIST:
        if can_move(snake[0], dirc) and board[snake[0] + dirc] < mini:
            mini = board[snake[0] + dirc]
            mv = dirc
    return mv

#ტანის გაზრდის ფუნქცია
def mv_body(__snake, __snake_size):
    for i in range(__snake_size, 0, -1):
        __snake[i] = __snake[i - 1]

#საკვების გენერირების ფუნქცია
def gen_food():
    global food, snake_size
    a = False
    while not a:
        w = randint(1, WIDTH - 2)
        h = randint(1, HEIGHT - 2)
        food = h * WIDTH + w
        a = not (food in snake[:snake_size])

#თუ თავი დაემთხვევა საკვებს, უნდა გაიზარდოს ტანის სიგრძე ქულას ზრდის +1-ით
def r_move(__mv):
    global snake, board, snake_size, score
    mv_body(snake, snake_size)
    snake[0] += __mv

    if snake[0] == food:
        board[snake[0]] = SNAKE
        snake_size += 1
        score += 1
        if snake_size < HEIGHT * WIDTH:
            gen_food()
    else:
        board[snake[0]] = SNAKE
        board[snake[snake_size]] = UNDEF

#როცა გველის თავი არ ემთხვევა საკვებს, იყენებს საკვების პოვნის ფუნქციას
def v_move():
    global snake, board, snake_size, _snake, _board, _snake_size, food
    _snake_size = snake_size
    _snake = snake[:]
    _board = board[:]
    init_board(_snake, _snake_size, _board)

    eaten = False
    while not eaten:
        find_food_path_bfs(food, _snake, _board)
        move = min_mv(_snake, _board)
        mv_body(_snake, _snake_size)
        _snake[0] += move
        if _snake[0] == food:
            _snake_size += 1
            init_board(_snake, _snake_size, _board)
            _board[food] = SNAKE
            eaten = True
        else:
            _board[_snake[0]] = SNAKE
            _board[_snake[_snake_size]] = UNDEF

#თუ გველს აქვს კუდი და ვერ პოულობს, მაშინ უნდა გაყვეს კუდს
def final_path():
    global snake, board
    v_move()
    if tail_available():
        return min_mv(snake, board)
    return follow_tail()

#კუდის არსებობა/არ არსებობის ფუნქცია
def tail_available():
    global _snake_size, _snake, _board, food
    _board[_snake[_snake_size - 1]] = FOOD
    _board[food] = SNAKE
    available = find_food_path_bfs(_snake[_snake_size - 1], _snake, _board)
    for dirc in DIRC_LIST:
        if can_move(_snake[0], dirc) and _snake[_snake_size - 1] == _snake[0] + dirc and _snake_size > 3:
            available = False
    return available

#ეძებს მინიმალურ მანძილს საკვებამდე
def min_mv(__snake, __board):
    mini = SNAKE
    mv = None
    for dirc in DIRC_LIST:
        if can_move(__snake[0], dirc) and __board[__snake[0] + dirc] < mini:
            mini = __board[__snake[0] + dirc]
            mv = dirc
    return mv

#კუდის გაყოლის ფუნქცია
def follow_tail():
    global _board, _snake, food, _snake_size
    _snake_size = snake_size
    _snake = snake[:]
    init_board(_snake, _snake_size, _board)
    _board[_snake[_snake_size - 1]] = FOOD
    _board[food] = SNAKE
    find_food_path_bfs(_snake[_snake_size - 1], _snake, _board)
    _board[_snake[_snake_size - 1]] = SNAKE

    return max_mv(_snake, _board)


def max_mv(__snake, __board):
    maxi = -1
    mv = None
    for dirc in DIRC_LIST:
        if can_move(__snake[0], dirc) and UNDEF > __board[__snake[0] + dirc] > maxi:
            maxi = __board[__snake[0] + dirc]
            mv = dirc
    return mv

#თამაშის გაშვების ფუნქცია
def run():
    reset_all()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, (int(food / WIDTH) * 24, int(food % WIDTH) * 24, 24, 24))
        for i in range(HEIGHT * WIDTH):
            if board[i] == SNAKE:
                pygame.draw.rect(screen, YELLOW, (int(i / WIDTH) * 24, int(i % WIDTH) * 24, 24, 24))
        init_board(snake, snake_size, board)

        # მთავარი ლოგიკა:
        #პოულობს მანძილს საკვებიდან გველის პირველ კუბამდე
        #
        # თუ გამოვიდა:
        # უნდა შეამოწმოს შეუძლია თუ არა მიწვდეს თავის კუდს
        # თუ შეუძლია, მივიდეს საკვებამდე მინიმალური მანძილი
        # თუ არ შეუძლია: უნდა გაყვეს კუდის მოძრაობას    if not: follow the movement of the tail / tu ara, gayves kudis modzraobas
        # მანამდე გაყვეს თავის კუდს
        #     სანამ ვერ იპოვის საკვებს
        #
        # თუ ვერ პოულობს ვერც კუდს და ვერც საკვებს
        #     შემთხვევითი პრინციპით იაროს კუბიკებზე

        best_move = final_path() if find_food_path_bfs(food, snake, board) else follow_tail()
        if best_move is None:
            best_move = last_op()
        if best_move is not None:
            r_move(best_move)
        else:
            break

        pygame.display.update()
        pygame.time.Clock().tick(20)

#თამაშის ჩართვის ეკრანი
def start_screen(): #starting screen
    start = True
    screen.fill(BLUE)
    pygame.font.init()
    menu = pygame.font.Font("./techkr/test.TTF", 30).render('Snake', True, GREEN)
    ai = pygame.font.Font("./techkr/test.TTF", 15).render('ხელოვნური ინტელექტი', True, ORANGE )
    play = pygame.font.Font("./techkr/test.TTF", 25).render('თამაში', True, YELLOW)
    screen.blit(menu, (207, 10))
    screen.blit(ai, (157, 50))
    play_button = pygame.draw.rect(screen, BLUE, (192, 260, 100, 50))
    screen.blit(play, (200, 270))

    while start:
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return
            if event.type == QUIT:
                start = False
        pygame.display.update()
    pygame.quit()
    sys.exit()

#თამაშის შემდეგი ეკრანი
def gg_screen(): #final screen
    gg = True
    screen.fill(BLACK)
    pygame.font.init()
    game_over = pygame.font.Font("./techkr/test.TTF", 190).render('თამაში მორჩა', True, WHITE)
    str_score = pygame.font.Font("./techkr/test.TTF", 80).render('ქულა: %s' % score, True, WHITE)
    term = pygame.font.Font("./techkr/test.TTF", 80).render('გამოსვლა', True, BLACK)
    back = pygame.font.Font("./techkr/test.TTF", 35).render('მენიუში დაბრუნება', True, BLACK)
    screen.blit(game_over, (60, 30))
    screen.blit(str_score, (190, 180))
    exit_button = pygame.draw.rect(screen, WHITE, (90, 300, 100, 50))
    back_button = pygame.draw.rect(screen, WHITE, (300, 300, 100, 50))
    screen.blit(term, (114, 270))
    screen.blit(back, (310, 300))

    while gg:
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return
                if exit_button.collidepoint(event.pos):
                    gg = False
            if event.type == QUIT:
                gg = False
        pygame.display.update()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Snake AI in pygame")
    screen = pygame.display.set_mode((480, 480))
    while True:
        start_screen()
        run()
        gg_screen()
