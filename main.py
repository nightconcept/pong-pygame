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
P1_CONTROL_UP = pygame.K_w
P1_CONTROL_DOWN = pygame.K_s
P1_CONTROL_BINDS = [P1_CONTROL_UP, P1_CONTROL_DOWN]
P2_CONTROL_UP = pygame.K_UP
P2_CONTROL_DOWN = pygame.K_DOWN
P2_CONTROL_BINDS = [P2_CONTROL_UP, P2_CONTROL_DOWN]

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
MAX_BOUNCE_ANGLE = 35
PLAYER_AREA_MARGIN = 10
P1_STARTING_X = 100
P1_STARTING_Y = 300
P2_STARTING_X = 700
P2_STARTING_Y = 300
SCORE_DELAY_TIME = 2000
FRAME_DEBOUNCE_THRESHOLD = 30

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
    def __init__(self, window, x, y, width, height, player, control_binds):
        self.rect = pygame.Rect(x, y, width, height)
        self.player = player
        self.score = 0
        self.window = window
        self.control_binds = control_binds
        self.KEYBIND_UP = 0
        self.KEYBIND_DOWN = 1
    
    # TODO: Improve the way a bind is handled instead of hard coding a player mapping here
    def handle_movement(self, keys_pressed):
        if keys_pressed[self.control_binds[self.KEYBIND_UP]] and self.rect.y - PLAYER_VEL > PLAYER_AREA_MARGIN: # UP
            self.rect.y -= PLAYER_VEL
        if keys_pressed[self.control_binds[self.KEYBIND_DOWN]] and self.rect.y + PLAYER_VEL + self.rect.height < WINDOW_HEIGHT - PLAYER_AREA_MARGIN: # DOWN
            self.rect.y += PLAYER_VEL
    
    def scored(self, points = 1):
        self.score += points

    def get_score(self):
        return self.score

    def get_rect(self):
        return self.rect

    def get_player(self):
        return self.player

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
        self.debounce_frame_count = 0

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
            paddle_rect = paddle.get_rect()
            if self.rect.colliderect(paddle_rect) and self.check_debounce():
                intersect_y = abs(paddle_rect.centery - self.rect.centery)
                normalized_relative_intersection_y = intersect_y/PADDLE_HEIGHT
                bounce_angle = normalized_relative_intersection_y * MAX_BOUNCE_ANGLE
                self.x_vel = round(BALL_START_VEL * math.cos(bounce_angle))
                self.y_vel = round(BALL_START_VEL * math.sin(bounce_angle))
                if paddle.get_player() == 1 and self.x_vel < 0:
                    self.x_vel *= -1
                if paddle.get_player() == 2 and self.x_vel > 0:
                    self.x_vel *= -1
                self.debounce_frame_count = 0
                print("normalized_relative_intersection_y: " + str(normalized_relative_intersection_y) + ", intersect_y: " + str(intersect_y) + 
                    ", x_vel: " + str(self.x_vel) + ", y_vel: " + str(self.y_vel))
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

    def check_debounce(self):
        if self.debounce_frame_count < FRAME_DEBOUNCE_THRESHOLD:
            return False
        return True

    def draw(self):
        self.debounce_frame_count += 1
        pygame.draw.rect(self.window, WHITE, self.rect)

## Border
class Border:
    """The border that is in the middle of the pong playfield"""
    def __init__(self, window):
        self.rect = pygame.Rect(WINDOW_WIDTH//2 - 5, 0, 10, WINDOW_HEIGHT)
        self.window = window

    def draw(self):
        pygame.draw.rect(self.window, WHITE, self.rect)

def main():
    window = Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Pong")
    player1 = Paddle(window.get_surface(), P1_STARTING_X, P1_STARTING_Y, PADDLE_WIDTH, PADDLE_HEIGHT, 1, P1_CONTROL_BINDS)
    player2 = Paddle(window.get_surface(), P2_STARTING_X, P2_STARTING_Y, PADDLE_WIDTH, PADDLE_HEIGHT, 2, P2_CONTROL_BINDS)
    ball = Ball(window.get_surface())
    border = Border(window.get_surface())
    paddles = [player1, player2]

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