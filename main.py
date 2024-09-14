from enum import Enum
import math
import os
import pygame
import random
import esper

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

## Enums
class GameStates(Enum):
    READY = 1
    PLAYING = 2

class CollidableTypes(Enum):
    PADDLE = 0
    BALL = 1

# Classes
## Window
class Window:
    """Window class that is the pygame display and manages all the items that need to be drawn on screen"""
    def __init__(self, width, height, caption):
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(caption)

    # may become relevant at some point
    def process(self):
        self.window.fill(BLACK)
        self.esper.process()
        pygame.display.flip()

    def get_game_state(self):
        return self.game_state

    def set_game_state(self, game_state):
        self.game_state = game_state

    def show_text(self, text):
        draw_text = START_FONT.render(text, TEXT_ANTIALIAS_TRUE, WHITE)
        self.win.blit(draw_text, (WINDOW_WIDTH//2 - draw_text.get_width()//2, (WINDOW_HEIGHT//4)*3 - draw_text.get_height()//2))
        pygame.display.update()

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

    
class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

class RenderableRect:
    def __init__(self, rect: pygame.Rect, color):
        self.rect = rect
        self.color = color

class Collidable:
    def __init__(self, frame_collide_threshold, collidable_type):
        self.frame_collide_threshold = frame_collide_threshold
        self.collidable_type = collidable_type

class PlayerInfo:
    def __init__(self, player_number, control_binds):
        self.player_number = player_number
        self.score = 0
        self.control_binds = control_binds
        self.KEYBIND_UP = 0
        self.KEYBIND_DOWN = 1        

class MovementProcessor(esper.Processor):
    def __init__(self, min_x, max_x, min_y, max_y):
        super().__init__()
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def process(self):
        for ent, (vel, rend) in esper.get_components(Velocity, RenderableRect):
            # Update the renderable component's position by it's velocity:
            rend.rect.x += vel.x
            rend.rect.y += vel.y
            # Keep the sprite inside boundaries
            rend.rect.x = max(self.min_x, rend.rect.x)
            rend.rect.y = max(self.min_y, rend.rect.y)
            rend.rect.x = min(self.max_x - rend.rect.w, rend.rect.x)
            rend.rect.y = min(self.max_y - rend.rect.h, rend.rect.y)

class RenderProcessor(esper.Processor):
    def __init__(self, window, clear_color=(0,0,0)):
        super().__init__()
        self.window = window
        self.clear_color = clear_color

    def process(self):
        surface = pygame.display.get_surface()
        surface.fill(self.clear_color)
        for ent, rend in esper.get_component(RenderableRect):
            pygame.draw.rect(surface=surface, color=rend.color, rect=rend.rect)

        pygame.display.flip()

class CollisionPaddle:
    def __init__(self, velo, rect, collide, player):
        self.velo = velo
        self.rect = rect
        self.collide = collide
        self.player = player

class CollisionBall:
    def __init__(self, velo, circle, collide):
        self.velo = velo
        self.circle = circle
        self.collide = collide

def _get_paddles():
    paddles = []
    for _ent, (velo, rend, collide, player) in esper.get_components(Velocity, RenderableRect, Collidable, PlayerInfo):
        if collide.collidable_type == CollidableTypes.PADDLE:
            paddles.append(CollisionPaddle(velo, rend, collide, player))
    return paddles

def _get_ball():
    for _ent, (velo, rend, collide) in esper.get_components(Velocity, RenderableCircle, Collidable):
        if collide.collidable_type == CollidableTypes.BALL:
            ball = CollisionBall(velo, rend, collide)
    return ball

class CollisionProcessor(esper.Processor):
    def __init__(self):
        super().__init__()
        self.collision_frame_debounce_count = 0
        self.FRAME_DEBOUNCE_THRESHOLD = 30

    def process(self):
        self.collision_frame_debounce_count += 1
        paddles = _get_paddles()
        ball = _get_ball()

        for paddle in paddles:
            if ball.circle.colliderect(paddle.rect) and self._check_debounce():
                intersect_y = abs(paddle.rect.centery - ball.rect.centery)
                normalized_relative_intersection_y = intersect_y/PADDLE_HEIGHT
                bounce_angle = normalized_relative_intersection_y * MAX_BOUNCE_ANGLE

                ball.velo.x = round(BALL_START_VEL * math.cos(bounce_angle))
                ball.velo.y = round(BALL_START_VEL * math.sin(bounce_angle))
                if paddle.player.player_number == 1 and ball.velo.x < 0:
                    ball.velo.x *= -1
                if paddle.player.player_number == 2 and ball.velo.x > 0:
                    ball.velo.x *= -1
                self.collision_frame_debounce_count = 0
                self._play_random_ball_hit_sound()

        if ball.rect.y < 0:
            ball.velo.y *= -1

        if ball.rect.y > WINDOW_HEIGHT:
            ball.velo.y *= -1

        if ball.rect.x < 0:
            pygame.event.post(pygame.event.Event(P2_SCORED))

        if ball.rect.x > WINDOW_WIDTH:
            pygame.event.post(pygame.event.Event(P1_SCORED))
    
    def _check_debounce(self):
        if self.collision_frame_debounce_count < FRAME_DEBOUNCE_THRESHOLD:
            return False
        return True

    def _play_random_ball_hit_sound(self):
        if random.randint(0,1) == 1:
            BALL_HIT_SOUND_1.play()
        else:
            BALL_HIT_SOUND_2.play()


def main():
    window = Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Pong")

    # Add entities
    player1 = esper.create_entity()
    esper.add_component(player1, Velocity(x=0, y=0))
    esper.add_component(player1, RenderableRect(pygame.Rect(P1_STARTING_X, P1_STARTING_Y, PADDLE_WIDTH, PADDLE_HEIGHT), WHITE))
    esper.add_component(player1, Collidable(FRAME_DEBOUNCE_THRESHOLD, CollidableTypes.PADDLE))
    esper.add_component(player1, PlayerInfo(1, P1_CONTROL_BINDS))

    player2 = esper.create_entity()
    esper.add_component(player2, Velocity(x=0, y=0))
    esper.add_component(player2, RenderableRect(pygame.Rect(P2_STARTING_X, P2_STARTING_Y, PADDLE_WIDTH, PADDLE_HEIGHT), WHITE))
    esper.add_component(player2, Collidable(FRAME_DEBOUNCE_THRESHOLD, CollidableTypes.PADDLE))
    esper.add_component(player2, PlayerInfo(2, P2_CONTROL_BINDS))

    ball = esper.create_entity()
    esper.add_component(ball, RenderableRect(pygame.Rect(WINDOW_WIDTH//2, WINDOW_HEIGHT//2), BALL_RADIUS, BALL_RADIUS, WHITE))
    esper.add_component(ball, Velocity(x=random.randint(BALL_START_VEL//2, BALL_START_VEL), y=random.randint(BALL_START_VEL//2, BALL_START_VEL)))
    esper.add_component(ball, Collidable(FRAME_DEBOUNCE_THRESHOLD, CollidableTypes.BALL))

    border = esper.create_entity()
    #esper.add_component(border, RenderableRect(pygame.Rect(WINDOW_WIDTH//2 - 5, 0, 10, WINDOW_HEIGHT), WHITE))

    # Add processors
    movement_processor = MovementProcessor(min_x=0, min_y=0, max_x=WINDOW_WIDTH, max_y=WINDOW_HEIGHT)
    render_processor = RenderProcessor(window=window)
    collision_processor = CollisionProcessor()

    esper.add_processor(render_processor, priority=1)
    esper.add_processor(collision_processor, priority=2)
    esper.add_processor(movement_processor, priority=3)

    # Run game
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            esper.process()

    pygame.quit()

if __name__ == "__main__":
    main()