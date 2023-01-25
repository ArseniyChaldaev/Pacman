from modules.constants import *
import os
import pygame
import random
import sys


def load_image(path, colorkey=None):
    fullname = os.path.join('data/images', path)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Person(pygame.sprite.Sprite):
    def __init__(self, x, y, path, level):
        pygame.sprite.Sprite.__init__(self)
        self.start_pos_x = TILE_SIZE * x
        self.start_pos_y = TILE_SIZE * y
        self.level = level
        self.image = load_image(path)
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.original_image = self.image
        self.rect = self.image.get_rect().move(self.start_pos_x, self.start_pos_y)

        self.dir = 3
        self.new_dir = 3
        self.new_dir_count = 0
        self.speed = 6

    def reset(self):
        self.rect.x = self.start_pos_x
        self.rect.y = self.start_pos_y
        self.dir = 3
        self.rotate()

    def is_allow(self, row, col):
        return self.level.map[row][col] != 0

    def can_move(self, x, y, direction):
        row = y // TILE_SIZE
        col = x // TILE_SIZE
        if direction in (LEFT, RIGHT):
            if y % TILE_SIZE == 0:
                return self.is_allow(row, col)
        else:
            if x % TILE_SIZE == 0:
                return self.is_allow(row, col)
        return False

    def change_dir(self, new_dir):
        self.new_dir = new_dir
        self.new_dir_count = 0

    def check_new_direction(self):
        if self.new_dir == -1:
            return
        next_x = self.rect.x
        next_y = self.rect.y
        if self.new_dir == UP:
            next_y = self.rect.top - self.speed
        elif self.new_dir == RIGHT:
            next_x = self.rect.right + self.speed
        elif self.new_dir == DOWN:
            next_y = self.rect.bottom + self.speed
        elif self.new_dir == LEFT:
            next_x = self.rect.left - self.speed

        if self.can_move(next_x, next_y, self.new_dir):
            self.dir = self.new_dir
            self.change_dir(-1)
        else:
            if self.new_dir_count > 3:
                self.change_dir(-1)
            else:
                self.new_dir_count += 1

    def move(self):
        if self.dir == UP and self.can_move(self.rect.x, self.rect.top - self.speed, self.dir):
            self.rect.y -= self.speed
        elif self.dir == RIGHT and self.can_move(self.rect.right + self.speed - 1, self.rect.y, self.dir):
            self.rect.x += self.speed
        elif self.dir == DOWN and self.can_move(self.rect.x, self.rect.bottom + self.speed - 1, self.dir):
            self.rect.y += self.speed
        elif self.dir == LEFT and self.can_move(self.rect.left - self.speed, self.rect.y, self.dir):
            self.rect.x -= self.speed

    def update(self):
        self.check_new_direction()
        self.move()
        self.rotate()

    def rotate(self):
        pass

    def get_pos(self):
        row = self.rect.centery // TILE_SIZE
        col = self.rect.centerx // TILE_SIZE
        return row, col

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Pacman(Person):
    def __init__(self, x, y, level):
        super().__init__(x, y, 'pac-man_open.png', level)
        self.original_image_open = self.original_image
        self.original_image_close = load_image('pac-man_close.png')
        self.original_image_close = pygame.transform.scale(self.original_image_close, (TILE_SIZE, TILE_SIZE))

    def is_allow(self, row, col):
        return self.level.map[row][col] not in (0, 3, 4, 5, 6)

    def rotate(self):
        if (self.dir in (LEFT, RIGHT) and self.rect.x % TILE_SIZE == 0) or (
                self.dir in (UP, DOWN) and self.rect.y % TILE_SIZE == 0):
            self.original_image = self.original_image_open
        else:
            self.original_image = self.original_image_close
        if self.dir == UP:
            self.image = pygame.transform.rotate(self.original_image, -90)
        elif self.dir == RIGHT:
            self.image = pygame.transform.flip(self.original_image, True, False)
        elif self.dir == DOWN:
            self.image = pygame.transform.rotate(self.original_image, 90)
        elif self.dir == LEFT:
            self.image = pygame.transform.flip(self.original_image, False, False)


class Ghost(Person):
    def __init__(self, x, y, path, level, pacman=None):
        super().__init__(x, y, path, level)
        self.is_smart = False
        self.speed = 4
        self.pacman = pacman
        self.goal = None

    def update(self):
        if self.rect.x % TILE_SIZE == 0 and self.rect.y % TILE_SIZE == 0:
            if self.is_smart:
                self.goal = self.pacman.get_pos()
                self.new_dir = self.get_optimal_direction()
            else:
                self.new_dir = self.get_random_direction()

        super().update()

    def get_optimal_direction(self):
        row = self.rect.centery // TILE_SIZE
        col = self.rect.centerx // TILE_SIZE

        queue = []
        visited = [(row, col)]
        direct = -1
        neighbours = [(UP, (0, -1)), (RIGHT, (1, 0)), (DOWN, (0, 1)), (LEFT, (-1, 0))]
        for direct, neighbour in neighbours:
            if 0 <= row + neighbour[1] < len(self.level.map):
                if 0 <= col + neighbour[0] < len(self.level.map[0]):
                    next_cell = (row + neighbour[1], col + neighbour[0])
                    if self.level.map[next_cell[0]][next_cell[1]] != 0:
                        queue.append((next_cell, direct))

        neighbours = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        while queue:
            curr_pos, direct = queue.pop(0)
            visited.append(curr_pos)
            if curr_pos == self.goal:
                break
            else:
                for neighbour in neighbours:
                    if 0 <= curr_pos[0] + neighbour[1] < len(self.level.map):
                        if 0 <= curr_pos[1] + neighbour[0] < len(self.level.map[0]):
                            next_cell = (curr_pos[0] + neighbour[1], curr_pos[1] + neighbour[0])
                            if next_cell not in visited:
                                if self.level.map[next_cell[0]][next_cell[1]] != 0:
                                    queue.append((next_cell, direct))
        return direct

    def get_random_direction(self):
        row = self.rect.y // TILE_SIZE
        col = self.rect.x // TILE_SIZE
        paths = []
        if row > 0 and self.is_allow(row - 1, col):
            paths.append(UP)
        if col < len(self.level.map[0]) - 1 and self.is_allow(row, col + 1):
            paths.append(RIGHT)
        if row < len(self.level.map) - 1 and self.is_allow(row + 1, col):
            paths.append(DOWN)
        if col > 0 and self.is_allow(row, col - 1):
            paths.append(LEFT)

        if len(paths) == 1:
            return paths[0]
        to_exclude = None
        if self.dir == UP:
            to_exclude = DOWN
        elif self.dir == DOWN:
            to_exclude = UP
        elif self.dir == RIGHT:
            to_exclude = LEFT
        elif self.dir == LEFT:
            to_exclude = RIGHT
        if to_exclude in paths:
            paths.remove(to_exclude)
        return random.choice(paths)


class BlinkyGhost(Ghost):
    def __init__(self, x, y, level, pacman=None):
        super().__init__(x, y, 'blinky.png', level, pacman)
        self.is_smart = True


class ClydeGhost(Ghost):
    def __init__(self, x, y, level):
        super().__init__(x, y, 'clyde.png', level)
        self.is_smart = False


class InkyGhost(Ghost):
    def __init__(self, x, y, level):
        super().__init__(x, y, 'inky.png', level)
        self.is_smart = False


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)


class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.radius = 3
        self.image = pygame.Surface((2 * self.radius, 2 * self.radius), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = ((x + 0.5) * TILE_SIZE, (y + 0.5) * TILE_SIZE)


class Mute(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_mute = load_image('mute.png')
        self.image_unmute = load_image('unmute.png')
        self.image_mute = pygame.transform.scale(self.image_mute, (TILE_SIZE, TILE_SIZE))
        self.image_unmute = pygame.transform.scale(self.image_unmute, (TILE_SIZE, TILE_SIZE))
        self.image = self.image_unmute
        self.rect = self.image.get_rect().move(WIDTH - TILE_SIZE, 0)

    def mute(self):
        self.image = self.image_mute

    def unmute(self):
        self.image = self.image_unmute
