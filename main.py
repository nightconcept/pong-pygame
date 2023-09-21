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
P1_SCORED = pygame.USEREVENT + 1
P2_SCORED = pygame.USEREVENT + 2

## Fonts
SCORE_FONT = pygame.font.Font(os.path.join('assets', 'bit5x3.ttf'), 50)
START_FONT = pygame.font.Font(os.path.join('assets', 'bit5x3.ttf'), 40)

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
SCORE_DELAY_TIME = 2000

## Screen and settings
FPS = 60
VOLUME = 0.3
WINDOW_WIDTH, WINDOW_HEIGHT = 858, 525 # Based on actual pong resolution
TEXT_ANTIALIAS_TRUE = 1

## Sounds and config
BALL_HIT_SOUND_1 = pygame.mixer.Sound(os.path.join('assets', 'ping_pong_8bit_plop.ogg'))
BALL_HIT_SOUND_2 = pygame.mixer.Sound(os.path.join('assets', 'ping_pong_8bit_beeep.ogg'))
SCORE_SOUND = pygame.mixer.Sound(os.path.join('assets', 'ping_pong_8bit_peeeeeep.ogg'))
BALL_HIT_SOUND_1.set_volume(VOLUME)
BALL_HIT_SOUND_2.set_volume(VOLUME)
SCORE_SOUND.set_volume(VOLUME)

## States
class GameStates(Enum):
    READY = 1
    PLAYING = 2

# Classes
## Window
class Window:
    """Window class that is the pygame display and manages all the items that need to be drawn on screen"""
    def __init__(self, width, height, caption):
        self.win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.draw_items = []
        pygame.display.set_caption(caption)

    # TODO: Before using this class type in another game and draw order may be important, this draw order
    # may become relevant at some point
    def draw(self):
        self.win.fill(BLACK)
        for item in self.draw_items:
            item.draw()
        pygame.display.update()

    def add_draw_item(self, item):
        self.draw_items.append(item)

    def get_game_state(self):
        return self.game_state

    def set_game_state(self, game_state):
        self.game_state = game_state

    def show_text(self, text):
        draw_text = START_FONT.render(text, TEXT_ANTIALIAS_TRUE, WHITE)
        self.win.blit(draw_text, (WINDOW_WIDTH//2 - draw_text.get_width()//2, (WINDOW_HEIGHT//4)*3 - draw_text.get_height()//2))
        pygame.display.update()

    def get_surface(self):
        return self.win

## Paddle
class Paddle:
    """Paddle class that represents a player and score element in pong"""
    def __init__(self, window, x, y, width, height, player):
        self.rect = pygame.Rect(x, y, width, height)
        self.player = player
        self.score = 0
        self.window = window
    
    # TODO: Improve the way a bind is handled instead of hard coding a player mapping here
    def handle_movement(self, keys_pressed):
        if self.player == 1:
            if keys_pressed[CONTROL_P1_UP] and self.rect.y - PLAYER_VEL > PLAYER_AREA_MARGIN: # UP
                self.rect.y -= PLAYER_VEL
            if keys_pressed[CONTROL_P1_DOWN] and self.rect.y + PLAYER_VEL + self.rect.height < WINDOW_HEIGHT - PLAYER_AREA_MARGIN: # DOWN
                self.rect.y += PLAYER_VEL
        else:
            if keys_pressed[CONTROL_P2_UP] and self.rect.y - PLAYER_VEL > PLAYER_AREA_MARGIN: # UP
                self.rect.y -= PLAYER_VEL
            if keys_pressed[CONTROL_P2_DOWN] and self.rect.y + PLAYER_VEL + self.rect.height < WINDOW_HEIGHT - PLAYER_AREA_MARGIN: # DOWN
                self.rect.y += PLAYER_VEL
    
    def scored(self, points = 1):
        self.score += points

    def get_score(self):
        return self.score

    def get_rect(self):
        return self.rect

    def draw(self):
        pygame.draw.rect(self.window, WHITE, self.rect)
        score = SCORE_FONT.render(str(self.score), TEXT_ANTIALIAS_TRUE, WHITE)
        if self.player == 1:
            score_coordinates = (WINDOW_WIDTH//4 - score.get_width()//2, 10) 
        else:
            score_coordinates = ((WINDOW_WIDTH//4)*3 - score.get_width()//2, 10)
        self.window.blit(score, score_coordinates)

## Ball
class Ball:
    """The ball that is hit by the paddles in pong"""
    def __init__(self, window):
        self.window = window

    def spawn(self, x = WINDOW_WIDTH//2, y = WINDOW_HEIGHT//2):
        self.rect = pygame.draw.circle(self.window, WHITE, (x, y), BALL_RADIUS)
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
                # TODO: collision physics
                intersect_y = (paddle.centery + PADDLE_HEIGHT//2) - self.rect.centery
                normalized_relative_intersection_y = intersect_y/(PADDLE_HEIGHT//2)
                bounce_angle = normalized_relative_intersection_y * MAX_BOUNCE_ANGLE
                self.x_vel = round(BALL_START_VEL * math.cos(bounce_angle))
                self.y_vel = round(BALL_START_VEL * math.sin(bounce_angle))
                self.play_random_ball_hit_sound()

        if self.rect.y < 0:
            self.y_vel *= -1

        if self.rect.y > WINDOW_HEIGHT:
            self.y_vel *= -1

        if self.rect.x < 0:
            pygame.event.post(pygame.event.Event(P2_SCORED))

        if self.rect.x > WINDOW_WIDTH:
            pygame.event.post(pygame.event.Event(P1_SCORED))
    
    def play_random_ball_hit_sound(self):
        if random.randint(0,1) == 1:
            BALL_HIT_SOUND_1.play()
        else:
            BALL_HIT_SOUND_2.play()

    def draw(self):
        pygame.draw.rect(self.window, WHITE, self.rect)

## Border
class Border:
    """The border that is in the middle of the pong playfield"""
    def __init__(self, window):
        self.rect = pygame.Rect(WINDOW_WIDTH//2 - 5, 0, 10, WINDOW_HEIGHT)
        self.window = window

    def draw(self):
        pygame.draw.rect(self.window, WHITE, self.rect)

def draw_start_text(text):
    draw_text = START_FONT.render(text, 1, WHITE)
    WIN.blit(draw_text, (WINDOW_WIDTH//2 - draw_text.get_width()//2, (WINDOW_HEIGHT//4)*3 - draw_text.get_height()//2))
    pygame.display.update()
    pygame.time.delay(500)

def main():
    window = Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Pong")
    player1 = Paddle(window.get_surface(), P1_STARTING_X, P1_STARTING_Y, PADDLE_WIDTH, PADDLE_HEIGHT, 1)
    player2 = Paddle(window.get_surface(), P2_STARTING_X, P2_STARTING_Y, PADDLE_WIDTH, PADDLE_HEIGHT, 2)
    ball = Ball(window.get_surface())
    border = Border(window.get_surface())
    paddles = [player1.get_rect(), player2.get_rect()]

    window.add_draw_item(player1)
    window.add_draw_item(player2)
    window.add_draw_item(ball)
    window.add_draw_item(border)
    
    window.set_game_state(GameStates.READY)
    window.show_text("Press space to start round")

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and window.get_game_state() == GameStates.READY:
                    # Hide message to press space to start
                    window.show_text("")
                    window.set_game_state(GameStates.PLAYING)
                    ball.spawn()
            
            if event.type == P1_SCORED:
                player1.scored()
                SCORE_SOUND.play()
                window.show_text("Player 1 Scored!")
                pygame.time.delay(SCORE_DELAY_TIME)
                window.show_text("")
                ball.spawn()
            if event.type == P2_SCORED:
                player2.scored()
                SCORE_SOUND.play()
                window.show_text("Player 2 Scored!")
                pygame.time.delay(SCORE_DELAY_TIME)
                window.show_text("")
                ball.spawn()

        keys_pressed = pygame.key.get_pressed()
        if window.get_game_state() == GameStates.PLAYING:
            player1.handle_movement(keys_pressed)
            player2.handle_movement(keys_pressed)
            ball.handle_movement(paddles)
            window.draw()

    pygame.quit()

if __name__ == "__main__":
    main()