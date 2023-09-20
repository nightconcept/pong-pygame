from enum import Enum
import math
import os
import pygame
import random

# Inits required first
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Constants and configuration
## Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

## Controls
CONTROL_P1_UP = pygame.K_w
CONTROL_P1_DOWN = pygame.K_s
CONTROL_P2_UP = pygame.K_UP
CONTROL_P2_DOWN = pygame.K_DOWN

## Events
class GameEvents(Enum):
    P1_SCORED = pygame.USEREVENT + 1
    P2_SCORED = pygame.USEREVENT + 2

## Fonts
SCORE_FONT = pygame.font.Font(os.path.join('assets', 'bit5x3.ttf'), 50)
START_FONT = pygame.font.Font(os.path.join('assets', 'bit5x3.ttf'), 20)

## Game Specific
PLAYER_VEL = 30
BALL_RADIUS = 5
BALL_START_VEL = 6
PADDLE_HEIGHT = 60
PADDLE_WIDTH = 15
PADDLE_P1_X_START = 100
PADDLE_P2_X_START = 700
PADDLE_Y_START = 700
MAX_BOUNCE_ANGLE = 45
PLAYER_AREA_MARGIN = 10
P1_STARTING_X = 100
P1_STARTING_Y = 300
P2_STARTING_X = 700
P2_STARTING_Y = 300

## Screen and settings
FPS = 60
VOLUME = 0.3
WINDOW_WIDTH, WINDOW_HEIGHT = 858, 525 # Based on actual pong resolution

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
    def __init__(self, width, height, caption):
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
        self.score = 0
    
    def handle_movement(self, keys_pressed):
        if self.player == 1:
            if keys_pressed[CONTROL_P1_UP] and self.rect.y - PLAYER_VEL > PLAYER_AREA_MARGIN: # UP
                player1.y -= PLAYER_VEL
            if keys_pressed[CONTROL_P1_DOWN] and selft.rect.y + PLAYER_VEL + self.rect.height < WINDOW_HEIGHT - PLAYER_AREA_MARGIN: # DOWN
                player1.y += PLAYER_VEL
        else:
            if keys_pressed[CONTROL_P2_UP] and self.rect.y - PLAYER_VEL > PLAYER_AREA_MARGIN: # UP
                self.rect.y -= PLAYER_VEL
            if keys_pressed[CONTROL_P2_DOWN] and self.rect.y + PLAYER_VEL + self.rect.height < WINDOW_HEIGHT - PLAYER_AREA_MARGIN: # DOWN
                self.rect.y += PLAYER_VEL
    
    def get_rect():
        return self.rect

## Ball
class Ball:
    """The ball that is hit by the paddles in pong"""
    def __init__(self):
        self.rect = pygame.draw.circle(WINDOW, WHITE, (-2 * BALL_RADIUS, -2 * BALL_RADIUS), BALL_RADIUS)

    def spawn(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.x_vel = random.randint(BALL_START_VEL//2, BALL_START_VEL)
        if random.randint(0, 1) == 1:
            self.x_vel *= -1
        self.y_vel = random.randint(BALL_START_VEL//2, BALL_START_VEL)
        if random.randint(0, 1) == 1:
            self.y_vel *= -1

    def handle_movement(self, paddles):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        for paddle in paddles:
            if self.rect.colliderect(paddle):
                # collision physics
                # intersect_y = (player1.centery + PADDLE_HEIGHT//2) - ball['rect'].centery
                # normalized_relative_intersection_y = intersect_y/(PADDLE_HEIGHT//2)
                # bounce_angle = normalized_relative_intersection_y * MAX_BOUNCE_ANGLE
                # ball['x_vel'] = round(BALL_START_VEL * math.cos(bounce_angle))
                # ball['y_vel'] = round(BALL_START_VEL * math.sin(bounce_angle))
                play_random_ball_hit_sound()

        if self.rect.y < 0:
            self.y_vel *= -1

        if self.rect.y > WINDOW_HEIGHT:
            self.y_vel *= -1

        if self.rect.x < 0:
            pygame.event.post(pygame.event.Event(GameEvents.P2_SCORED))

        if self.rect.x > WINDOW_WIDTH:
            pygame.event.post(pygame.event.Event(GameEvents.P2_SCORED))
    
    def play_random_ball_hit_sound(self):
        if random.randint(0,1) == 1:
            BALL_HIT_SOUND_1.play()
        else:
            BALL_HIT_SOUND_2.play()


BALL_HIT_SOUND_1.set_volume(VOLUME)
BALL_HIT_SOUND_2.set_volume(VOLUME)
SCORE_SOUND.set_volume(VOLUME)

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

def main():
    player1 = Paddle(P1_STARTING_X, P1_STARTING_Y, PADDLE_WIDTH, PADDLE_HEIGHT, 1)
    player2 = Paddle(P2_STARTING_X, P2_STARTING_Y, PADDLE_WIDTH, PADDLE_HEIGHT, 2)
    ball = Ball()

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
                ball.spawn()
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
            player1.handle_movement(keys_pressed)
            player2.handle_movement(keys_pressed)
            paddles = [player1.get_rect(), player2.get_rect()]
            ball.handle_movement(paddles)
            draw_window(player1, player2, ball, player1_score, player2_score) ## TODO

    pygame.quit()

if __name__ == "__main__":
    main()