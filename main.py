from enum import Enum
import math
import os
import pygame
import random


# Inits required first
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Constants
## Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

## Events
class GameEvents(Enum):
    P1_SCORED = pygame.USEREVENT + 1
    P2_SCORED = pygame.USEREVENT + 2

## Fonts
SCORE_FONT = pygame.font.Font(os.path.join('assets', 'bit5x3.ttf'), 50)
START_FONT = pygame.font.Font(os.path.join('assets', 'bit5x3.ttf'), 20)

## Game Specific
PLAYER_VEL = 30
BALL_START_VEL = 6
PADDLE_HEIGHT = 60
PADDLE_WIDTH = 15
MAX_BOUNCE_ANGLE = 45
PLAYER_AREA_MARGIN = 10

## General Settings
FPS = 60
WINDOW_WIDTH, WINDOW_HEIGHT = 858, 525

## Sounds
BALL_HIT_SOUND_1 = pygame.mixer.Sound(os.path.join('assets', 'ping_pong_8bit_plop.ogg'))
BALL_HIT_SOUND_2 = pygame.mixer.Sound(os.path.join('assets', 'ping_pong_8bit_beeep.ogg'))
SCORE_SOUND = pygame.mixer.Sound(os.path.join('assets', 'ping_pong_8bit_peeeeeep.ogg'))

## States
class GameStates(Enum):
    READY = 1
    PLAYING = 2

# Classes
## Window
class Window:
    def __init__(width, height, caption):
        self.win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(caption)

    def draw():
        self.win.fill(BLACK)

        pygame.display.update()
## Paddle
class Paddle:
    def __init__(x, y, width, height, player):
        self.rect = pygame.Rect(x, y, width, height)
        self.player = player
    
    def handle_movement():
        if self.player == 1:
            if keys_pressed[pygame.K_w] and self.rect.y - PLAYER_VEL > PLAYER_AREA_MARGIN: # UP
                player1.y -= PLAYER_VEL
            if keys_pressed[pygame.K_s] and selft.rect.y + PLAYER_VEL + self.rect.height < WINDOW_HEIGHT - PLAYER_AREA_MARGIN: # DOWN
                player1.y += PLAYER_VEL
        else:
            if keys_pressed[pygame.K_UP] and self.rect.y - PLAYER_VEL > 10: # UP
                self.rect.y -= PLAYER_VEL
            if keys_pressed[pygame.K_DOWN] and self.rect.y + PLAYER_VEL + self.rect.height < WINDOW_HEIGHT - 10: # DOWN
                self.rect.y += PLAYER_VEL

## Ball
class Ball:
    """The ball that is hit by the paddles in pong"""
    def __init__(x, y):
        self.x = x
        self.y = y``

BALL_HIT_SOUND_1.set_volume(0.2)
BALL_HIT_SOUND_2.set_volume(0.2)
SCORE_SOUND.set_volume(0.2)

# TODO: Make a dotted line border
BORDER = pygame.Rect(WINDOW_WIDTH//2 - 5, 0, 10, WINDOW_HEIGHT)


def draw_window(player1, player2, ball, player1_score, player2_score):
    WIN.fill(BLACK)
    pygame.draw.rect(WIN, WHITE, BORDER)

    pygame.draw.rect(WIN, WHITE, player1)
    pygame.draw.rect(WIN, WHITE, player2)
    
    p1_score = SCORE_FONT.render(str(player1_score), 1, WHITE)
    p2_score = SCORE_FONT.render(str(player2_score), 1, WHITE)
    WIN.blit(p1_score, (WINDOW_WIDTH//4 - p1_score.get_width()//2, 10))
    WIN.blit(p2_score, ((WINDOW_WIDTH//4)*3 - p2_score.get_width()//2, 10))
    
    pygame.draw.rect(WIN, WHITE, ball['rect'])
    pygame.display.update()

def draw_start_text(text):
    draw_text = START_FONT.render(text, 1, WHITE)
    WIN.blit(draw_text, (WINDOW_WIDTH//2 - draw_text.get_width()//2, (WINDOW_HEIGHT//4)*3 - draw_text.get_height()//2))
    pygame.display.update()
    pygame.time.delay(500)

def handle_player1_movement(keys_pressed, player1):
    if keys_pressed[pygame.K_w] and player1.y - PLAYER_VEL > 10: # UP
        player1.y -= PLAYER_VEL
    if keys_pressed[pygame.K_s] and player1.y + PLAYER_VEL + player1.height < WINDOW_HEIGHT - 10: # DOWN
        player1.y += PLAYER_VEL

def handle_player2_movement(keys_pressed, player2):
    if keys_pressed[pygame.K_UP] and player2.y - PLAYER_VEL > 10: # UP
        player2.y -= PLAYER_VEL
    if keys_pressed[pygame.K_DOWN] and player2.y + PLAYER_VEL + player2.height < WINDOW_HEIGHT - 10: # DOWN
        player2.y += PLAYER_VEL

def handle_ball(ball, player1, player2):
    ball['rect'].x += ball['x_vel']
    ball['rect'].y += ball['y_vel']

    if player1.colliderect(ball['rect']):
        intersect_y = (player1.centery + PADDLE_HEIGHT//2) - ball['rect'].centery
        normalized_relative_intersection_y = intersect_y/(PADDLE_HEIGHT//2)
        bounce_angle = normalized_relative_intersection_y * MAX_BOUNCE_ANGLE
        ball['x_vel'] = round(BALL_START_VEL * math.cos(bounce_angle))
        ball['y_vel'] = round(BALL_START_VEL * math.sin(bounce_angle))
        play_random_hit_sound()
    if player2.colliderect(ball['rect']):
        intersect_y = (player2.centery + PADDLE_HEIGHT//2) - ball['rect'].centery
        normalized_relative_intersection_y = intersect_y/(PADDLE_HEIGHT//2)
        bounce_angle = normalized_relative_intersection_y * MAX_BOUNCE_ANGLE
        ball['x_vel'] = -1 * round(BALL_START_VEL * math.cos(bounce_angle))
        ball['y_vel'] = -1 * round(BALL_START_VEL * math.sin(bounce_angle))
        play_random_hit_sound()

    if ball['rect'].y < 0:
        ball['y_vel'] *= -1

    if ball['rect'].y > WINDOW_HEIGHT:
        ball['y_vel'] *= -1

    if ball['rect'].x < 0:
        pygame.event.post(pygame.event.Event(P2_SCORED))

    if ball['rect'].x > WINDOW_WIDTH:
        pygame.event.post(pygame.event.Event(P1_SCORED))

def play_random_hit_sound():
    if random.randint(0,1) == 1:
        BALL_HIT_SOUND_1.play()
    else:
        BALL_HIT_SOUND_2.play()

def start_ball(ball):
    ball['x_vel'] = random.randint(BALL_START_VEL//2, BALL_START_VEL)
    if random.randint(0, 1) == 1:
        ball['x_vel'] *= -1
    ball['y_vel'] = random.randint(BALL_START_VEL//2, BALL_START_VEL)
    if random.randint(0, 1) == 1:
        ball['y_vel'] *= -1

def main():
    player1 = pygame.Rect(100, 300, PADDLE_WIDTH, PADDLE_HEIGHT)
    player2 = pygame.Rect(700, 300, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = {
        "x_vel": 0,
        "y_vel": 0,
        "rect": pygame.Rect(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, 8,8)
    }
    
    player1_score = 0
    player2_score = 0

    game_state = GameState.READY
    start_text = "Press space to start a round"

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_state == GameState.READY:
                    # Hide message to press space to start
                    start_text = ""
                    game_state = GameState.PLAYING
                    start_ball(ball)
            
            if event.type == P1_SCORED:
                player1_score += 1
                SCORE_SOUND.play()
                ball['rect'] = pygame.Rect(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, 8,8)
                start_ball(ball)
            if event.type == P2_SCORED:
                player2_score += 1
                SCORE_SOUND.play()
                ball['rect'] = pygame.Rect(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, 8,8)
                start_ball(ball)

        if start_text != "":
            draw_start_text(start_text)

        keys_pressed = pygame.key.get_pressed()
        if game_state == GameState.PLAYING:
            handle_player1_movement(keys_pressed, player1)
            handle_player2_movement(keys_pressed, player2)
            handle_ball(ball, player1, player2)
            draw_window(player1, player2, ball, player1_score, player2_score)

    pygame.quit()

if __name__ == "__main__":
    main()