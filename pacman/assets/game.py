# Build Pac-Man from Scratch in Python with PyGame!!
import copy
from board import boards
import pygame
import math
from enum import Enum
from collections import namedtuple


# reward table: eat_nothing(-1); eat_food(+3); eat_powerup(+5); eat_ghost(+5); game_over(-30); clear_game(+30);
# 100 * play_step without food -> game_over(-30)
#
# input variables (state):
# - position of:
#       clyde
#       blinky
#       inky
#       pinky
#       -
#       player
#       -
#       1st closest food
#       2nd closest food
#       3rd closest food
#       -
#       closest powerup
#
# - direction of:
#       player(head)


pygame.init()

font = pygame.font.Font('arial.ttf', 25)

class Direction(Enum):
     RIGHT = 1
     LEFT = 2
     UP = 3
     DOWN = 4

Point = namedtuple('Point', ["x", "y"])

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255) # dark blue
BLUE2 = (0, 100, 255) # bright blue
BLACK = (0, 0, 0)

SPEED = 40

class PacManAI:

    def __init__(self, player_x=450, player_y=663, WIDTH=900, HEIGHT=950, x_coord, y_coord, target, ghost_speed, img, direct, dead, box, id):
        
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.player_x = player_x
        self.player_y = player_y
        self.center_x = self.player_x + 23
        self.center_y = self.player_y + 24

        # init display
        self.display = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('PacMan')
        self.clock = pygame.time.Clock()

        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.player_x, self.player_y)

        self.score = 0
        self.powerup = False
        self.counter = 0
        self.player_speed = 2
        self.level = copy.deepcopy(boards)
        self.powerup = False
        self.powerup_counter = 0
        self.eaten_ghost = [False, False, False, False]
        self.blinky_x = 56
        self.blinky_y = 58
        self.blinky_direction = Direction.RIGHT
        self.inky_x = 440
        self.inky_y = 388
        self.inky_direction = Direction.UP
        self.pinky_x = 440
        self.pinky_y = 438
        self.pinky_direction = Direction.UP
        self.clyde_x = 440
        self.clyde_y = 438
        self.clyde_direction = Direction.UP
        # to be continued

        # player images
        self.player_images = []
        for i in range(1, 5):
            self.player_images.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (45, 45)))

        # ghost images
        self.blinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'), (45, 45))
        self.pinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'), (45, 45))
        self.inky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (45, 45))
        self.clyde_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'), (45, 45))
        self.spooked_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'), (45, 45))
        self.dead_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/dead.png'), (45, 45))

        # ghost stuff
        self.x_pos_ghost = x_coord
        self.y_pos_ghost = y_coord
        self.center_x_ghost = self.x_pos_ghost + 22
        self.center_y_ghost = self.y_pos_ghost + 22
        self.target = target
        self.ghost_speed = ghost_speed
        self.img_ghost = img
        self.direction_ghost = direct
        self.dead_ghost = dead
        self.in_box = box
        self.id_ghost = id
        self.turns_ghost, self.in_box = self.check_ghost_collisions()
        self.rect_ghost = self.draw_ghost()


    def play_step(self):
            # 1. collect user input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.direction = Direction.DOWN
                    

            # 2. move
            self._move(self.direction) # update player head

            # 3. check if game over
            game_over = False
            if self.is_collision():
                game_over = True
                return game_over, self.score

            # 4. move ghosts
            self.move_blinky(self.direction_ghost)
            self.move_clyde(self.direction_ghost)
            self.move_inky(self.direction_ghost)
            self.move_pinky(self.direction_ghost)

            # 5. update ui and clock
            self._update_ui()
            self.clock.tick(SPEED)

            # 6. return game over and score
            return game_over, self.score
    
    def is_collision(self):
        # hits ghost
        if self.head[0] in self.blinky_x and self.head[1] in self.blinky_y:
            return True
        if self.head[0] in self.inky_x and self.head[1] in self.inky_y:
            return True
        if self.head[0] in self.pinky_x and self.head[1] in self.pinky_y:
            return True
        if self.head[0] in self.clyde_x and self.head[1] in self.clyde_y:
            return True
        
        return False

    def _update_ui(self):
         self.draw_board()

         self.draw_player()

         text = font.render("Score: " + str(self.score), True, WHITE)
         self.display.blit(text, [0, 0])
         pygame.display.flip()

    def draw_board(WIDTH=900, HEIGHT=950):
        
        level = copy.deepcopy(boards)
        display = pygame.display.set_mode((WIDTH, HEIGHT))
        PI = math.pi

        num1 = ((HEIGHT - 50) // 32)
        num2 = (WIDTH // 30)
        for i in range(len(level)):
            for j in range(len(level[i])):
                if level[i][j] == 1:
                    pygame.draw.circle(display, WHITE, (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
                if level[i][j] == 2:
                    pygame.draw.circle(display, WHITE, (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
                if level[i][j] == 3:
                    pygame.draw.line(display, BLUE1, (j * num2 + (0.5 * num2), i * num1),
                                    (j * num2 + (0.5 * num2), i * num1 + num1), 3)
                if level[i][j] == 4:
                    pygame.draw.line(display, BLUE1, (j * num2, i * num1 + (0.5 * num1)),
                                    (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
                if level[i][j] == 5:
                    pygame.draw.arc(display, BLUE1, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                    0, PI / 2, 3)
                if level[i][j] == 6:
                    pygame.draw.arc(display, BLUE1,
                                    [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1], PI / 2, PI, 3)
                if level[i][j] == 7:
                    pygame.draw.arc(display, BLUE1, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1], PI,
                                    3 * PI / 2, 3)
                if level[i][j] == 8:
                    pygame.draw.arc(display, BLUE1,
                                    [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1], 3 * PI / 2,
                                    2 * PI, 3)
                if level[i][j] == 9:
                    pygame.draw.line(display, WHITE, (j * num2, i * num1 + (0.5 * num1)),
                                    (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
        
    def draw_player(self):

        if self.direction == Direction.RIGHT:
            self.display.blit(self.player_images[self.counter // 5], (self.player_x, self.player_y))
        elif self.direction == Direction.LEFT:
            self.display.blit(pygame.transform.flip(self.player_images[self.counter // 5], True, False), (self.player_x, self.player_y))
        elif self.direction == Direction.UP:
            self.display.blit(pygame.transform.rotate(self.player_images[self.counter // 5], 90), (self.player_x, self.player_y))
        elif self.direction == Direction.DOWN:
            self.display.blit(pygame.transform.rotate(self.player_images[self.counter // 5], 270), (self.player_x, self.player_y))

    def _move(self, direction):
        player_x = self.head[0]
        player_y = self.head[1]

        if direction == Direction.RIGHT:
            player_x += self.player_speed
        elif direction == Direction.LEFT:
            player_x -= self.player_speed
        elif direction == Direction.DOWN:
            player_y += self.player_speed
        elif direction == Direction.UP:
            player_x -= self.player_speed

        self.head = Point(player_x, player_y)

    def check_collisions(self, score, power, power_count, eaten_ghosts):

        num1 = (self.HEIGHT - 50) // 32
        num2 = self.WIDTH // 30
        if 0 < self.player_x < 870:
            if self.level[self.center_y // num1][self.center_x // num2] == 1:
                self.level[self.center_y // num1][self.center_x // num2] = 0
                score += 10
            if self.level[self.center_y // num1][self.center_x // num2] == 2:
                self.level[self.center_y // num1][self.center_x // num2] = 0
                score += 50
                power = True
                power_count = 0
                eaten_ghosts = [False, False, False, False]
        return score, power, power_count, eaten_ghosts

    def check_position(self, centerx, centery):
        turns = [False, False, False, False]
        num1 = (self.HEIGHT - 50) // 32
        num2 = (self.WIDTH // 30)
        num3 = 15
        # check collisions based on center x and center y of player +/- fudge number
        if centerx // 30 < 29:
            if self.direction == Direction.RIGHT:
                if self.level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
            if self.direction == Direction.LEFT:
                if self.level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
            if self.direction == Direction.UP:
                if self.level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
            if self.direction == Direction.DOWN:
                if self.level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True

            if self.direction == Direction.UP or self.direction == Direction.DOWN:
                if 12 <= centerx % num2 <= 18:
                    if self.level[(centery + num3) // num1][centerx // num2] < 3:
                        turns[3] = True
                    if self.level[(centery - num3) // num1][centerx // num2] < 3:
                        turns[2] = True
                if 12 <= centery % num1 <= 18:
                    if self.level[centery // num1][(centerx - num2) // num2] < 3:
                        turns[1] = True
                    if self.level[centery // num1][(centerx + num2) // num2] < 3:
                        turns[0] = True
            if self.direction == Direction.RIGHT or self.direction == Direction.LEFT:
                if 12 <= centerx % num2 <= 18:
                    if self.level[(centery + num1) // num1][centerx // num2] < 3:
                        turns[3] = True
                    if self.level[(centery - num1) // num1][centerx // num2] < 3:
                        turns[2] = True
                if 12 <= centery % num1 <= 18:
                    if self.level[centery // num1][(centerx - num3) // num2] < 3:
                        turns[1] = True
                    if self.level[centery // num1][(centerx + num3) // num2] < 3:
                        turns[0] = True
        else:
            turns[0] = True
            turns[1] = True

        return turns

    """ def __init__(self, x_coord, y_coord, target, ghost_speed, img, direct, dead, box, id):
            
        self.x_pos_ghost = x_coord
        self.y_pos_ghost = y_coord
        self.center_x_ghost = self.x_pos_ghost + 22
        self.center_y_ghost = self.y_pos_ghost + 22
        self.target = target
        self.ghost_speed = ghost_speed
        self.img_ghost = img
        self.direction_ghost = direct
        self.dead_ghost = dead
        self.in_box = box
        self.id_ghost = id
        self.turns_ghost, self.in_box = self.check_ghost_collisions()
        self.rect_ghost = self.draw_ghost() """

    def draw_ghost(self):
        if (not self.powerup and not self.dead_ghost) or (self.eaten_ghost[self.id_ghost] and self.powerup and not self.dead_ghost):
            self.display.blit(self.img_ghost, (self.x_pos_ghost, self.y_pos_ghost))
        elif self.powerup and not self.dead_ghost and not self.eaten_ghost[self.id_ghost]:
            self.display.blit(self.spooked_img, (self.x_pos_ghost, self.y_pos_ghost))
        else:
            self.display.blit(self.dead_img, (self.x_pos_ghost, self.y_pos_ghost))
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        return ghost_rect

    def check_ghost_collisions(self):
        level = copy.deepcopy(boards)
        
        # R, L, U, D
        num1 = ((self.HEIGHT - 50) // 32)
        num2 = (self.WIDTH // 30)
        num3 = 15
        self.turns_ghost = [False, False, False, False]
        if 0 < self.center_x // 30 < 29:
            if self.level[(self.center_y - num3) // num1][self.center_x // num2] == 9:
                self.turns_ghost[2] = True
            if self.level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                    self.in_box or self.dead_ghost)):
                self.turns_ghost[1] = True
            if self.level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                    self.in_box or self.dead_ghost)):
                self.turns_ghost[0] = True
            if self.level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead_ghost)):
                self.turns_ghost[3] = True
            if self.level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead_ghost)):
                self.turns_ghost[2] = True

            if self.direction == Direction.UP or self.direction == Direction.DOWN:
                if 12 <= self.center_x % num2 <= 18:
                    if self.level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead_ghost)):
                        self.turns_ghost[3] = True
                    if self.level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead_ghost)):
                        self.turns_ghost[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if self.level[self.center_y // num1][(self.center_x - num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num2) // num2] == 9 and (
                            self.in_box or self.dead_ghost)):
                        self.turns_ghost[1] = True
                    if self.level[self.center_y // num1][(self.center_x + num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num2) // num2] == 9 and (
                            self.in_box or self.dead_ghost)):
                        self.turns_ghost[0] = True

            if self.direction == Direction.RIGHT or self.direction == Direction.LEFT:
                if 12 <= self.center_x % num2 <= 18:
                    if self.level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (self.level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead_ghost)):
                        self.turns_ghost[3] = True
                    if self.level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (self.level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead_ghost)):
                        self.turns_ghost[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if self.level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                            or (self.level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                            self.in_box or self.dead_ghost)):
                        self.turns_ghost[1] = True
                    if self.level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                            or (self.level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                            self.in_box or self.dead_ghost)):
                        self.turns_ghost[0] = True
        else:
            self.turns_ghost[0] = True
            self.turns_ghost[1] = True
        if 350 < self.x_pos_ghost < 550 and 370 < self.y_pos_ghost < 480:
            self.in_box = True
        else:
            self.in_box = False
        return self.turns_ghost, self.in_box

    def move_clyde(self):
        # r, l, u, d
        # clyde is going to turn whenever advantageous for pursuit
        if self.direction_ghost == Direction.RIGHT:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.ghost_speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                else:
                    self.x_pos += self.ghost_speed
        elif self.direction_ghost == Direction.LEFT:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction_ghost = Direction.DOWN
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.ghost_speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                else:
                    self.x_pos -= self.ghost_speed
        elif self.direction_ghost == Direction.UP:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction_ghost = Direction.LEFT
                self.x_pos -= self.ghost_speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction_ghost = Direction.UP
                self.y_pos -= self.ghost_speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                else:
                    self.y_pos -= self.ghost_speed
        elif self.direction_ghost == Direction.DOWN:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.ghost_speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                else:
                    self.y_pos += self.ghost_speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction_ghost

    def move_blinky(self):
        # r, l, u, d
        # blinky is going to turn whenever colliding with walls, otherwise continue straight
        if self.direction_ghost == Direction.RIGHT:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.ghost_speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
            elif self.turns[0]:
                self.x_pos += self.ghost_speed
        elif self.direction_ghost == Direction.LEFT:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.ghost_speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
            elif self.turns[1]:
                self.x_pos -= self.ghost_speed
        elif self.direction_ghost == Direction.UP:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction_ghost = Direction.UP
                self.y_pos -= self.ghost_speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
            elif self.turns[2]:
                self.y_pos -= self.ghost_speed
        elif self.direction_ghost == Direction.DOWN:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.ghost_speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
            elif self.turns[3]:
                self.y_pos += self.ghost_speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction_ghost

    def move_inky(self):
        # r, l, u, d
        # inky turns up or down at any point to pursue, but left and right only on collision
        if self.direction_ghost == Direction.RIGHT:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.ghost_speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                else:
                    self.x_pos += self.ghost_speed
        elif self.direction_ghost == Direction.LEFT:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction_ghost = Direction.DOWN
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.ghost_speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                else:
                    self.x_pos -= self.ghost_speed
        elif self.direction_ghost == Direction.UP:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction_ghost = Direction.UP
                self.y_pos -= self.ghost_speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
            elif self.turns[2]:
                self.y_pos -= self.ghost_speed
        elif self.direction_ghost == Direction.DOWN:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.ghost_speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
            elif self.turns[3]:
                self.y_pos += self.ghost_speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction_ghost

    def move_pinky(self):
        # r, l, u, d
        # inky is going to turn left or right whenever advantageous, but only up or down on collision
        if self.direction_ghost == Direction.RIGHT:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.ghost_speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
            elif self.turns[0]:
                self.x_pos += self.ghost_speed
        elif self.direction_ghost == Direction.LEFT:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction_ghost = Direction.DOWN
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.ghost_speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
            elif self.turns[1]:
                self.x_pos -= self.ghost_speed
        elif self.direction_ghost == Direction.UP:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction_ghost = Direction.LEFT
                self.x_pos -= self.ghost_speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction_ghost = Direction.UP
                self.y_pos -= self.ghost_speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.turns[3]:
                    self.direction_ghost = Direction.DOWN
                    self.y_pos += self.ghost_speed
                elif self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                else:
                    self.y_pos -= self.ghost_speed
        elif self.direction_ghost == Direction.DOWN:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.ghost_speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[2]:
                    self.direction_ghost = Direction.UP
                    self.y_pos -= self.ghost_speed
                elif self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                elif self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction_ghost = Direction.RIGHT
                    self.x_pos += self.ghost_speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction_ghost = Direction.LEFT
                    self.x_pos -= self.ghost_speed
                else:
                    self.y_pos += self.ghost_speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction_ghost
    
    """ class Player():
        # reset
        def reset(self):
            # init game state
            self.direction = 0

            self.score = 0
            self.counter = 0
            self.flicker = False
            # R, L, U, D
            self.turns_allowed = [False, False, False, False]
            self.direction_command = 0
            self.player_speed = 2
            self.score = 0
            self.powerup = False
            self.power_counter = 0
            self.eaten_ghost = [False, False, False, False]
            self.moving = False
            self.lives = 1

        
            # 1. collect user input
            # 2. move
            # 3. check if game over
            # 4. eat powerup or just move
            # 5. update ui and clock
            # 6. return game over and score """

    """ class GameBoard(): """

def main():
    game = PacManAI()

    # game loop
    while True:
        game_over, score = game.play_step()

        # break if game over
        if game_over == True:
            break

    print('Final Score', score)

    pygame.quit()

if __name__ == '__main__':

    main()
       

# reward
# play(action) -> direction
# game_iteration
# is_collision

