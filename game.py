import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 155, 0)
BLUE2 = (0, 255, 0)
BLACK = (0,0,0)

BLOCK_SIZE = 20 
SPEED = 2000

class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()


    def reset(self):
        self.direction = Direction.RIGHT
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0


    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()


    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        self._move() # update the head
        self.snake.insert(0, self.head)
        
        
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
        
        self._update_ui()
        self.clock.tick(SPEED)
        return reward, game_over, self.score


    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        if pt in self.snake[1:]:
            return True
        return False


    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()


    def _move(self, action):
        # Calculate distances to the food in each direction
        distances = [
            self._calculate_distance(self.head.x + BLOCK_SIZE, self.head.y),  # right
            self._calculate_distance(self.head.x - BLOCK_SIZE, self.head.y),  # left
            self._calculate_distance(self.head.x, self.head.y + BLOCK_SIZE),  # down
            self._calculate_distance(self.head.x, self.head.y - BLOCK_SIZE)   # up
        ]

        # Choose the direction with the shortest distance to the food
        shortest_distance_idx = np.argmin(distances)

        # Update direction based on the shortest distance
        if shortest_distance_idx == 0:
            self.direction = Direction.RIGHT
        elif shortest_distance_idx == 1:
            self.direction = Direction.LEFT
        elif shortest_distance_idx == 2:
            self.direction = Direction.DOWN
        else:
            self.direction = Direction.UP

        # Move the snake in the chosen direction
        self._move_snake()

    def _calculate_distance(self, x, y):
        return (x - self.food.x) ** 2 + (y - self.food.y) ** 2

    def _move_snake(self):
        dx, dy = 0, 0
        if self.direction == Direction.RIGHT:
            dx = BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            dx = -BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            dy = BLOCK_SIZE
        elif self.direction == Direction.UP:
            dy = -BLOCK_SIZE

        self.head = Point(self.head.x + dx, self.head.y + dy)
