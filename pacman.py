import math
import os
import sys
import random
import datetime
import time
import json

import pygame

CURRENT_YEAR = datetime.datetime.now().year

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (10, 10, 10)

# Directions
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

# GAME MODES
STATE_MENU = 0
STATE_PLAY = 1
STATE_RESPAWN = 2
STATE_GAME_OVER = 3
STATE_WON = 4
STATE_RATING = 5

# GAME MAP
MAP = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 1, 1, 1, 7, 1, 1, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 1, 0, 0, 3, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0, 4, 5, 6, 0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
    [0, 1, 1, 0, 1, 1, 1, 1, 1, 8, 1, 1, 1, 1, 1, 0, 1, 1, 0],
    [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

TILE_SIZE = 24
WIDTH = len(MAP[0]) * TILE_SIZE
HEIGHT = len(MAP) * TILE_SIZE
FPS = 25

FONT_FILE = 'data/font/pacmania_cyrillic.otf'
FONT_FILE_DIGITS = 'data/font/Emulogic-zrEw.ttf'
RATING_FILE = 'data/score/top.json'

pygame.init()
pygame.mixer.init()


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()
        #self.font_name = pygame.font.match_font('arial')
        self.running = True
        self.state = STATE_MENU

        self.all_sprites = pygame.sprite.Group()
        self.tile_sprites = pygame.sprite.Group()
        self.food_sprites = pygame.sprite.Group()
        self.ghost_sprites = pygame.sprite.Group()
        self.player = None
        self.ghosts = []
        self.lives = 3
        self.recovery_counter = 12
        self.score = 0

        self.button_play = Button('Начать игру', 32, WHITE, RED, WIDTH // 2, 225, self.start_game)
        self.button_score = Button('Рейтинг', 32, WHITE, RED, WIDTH // 2, 300, self.show_score)
        self.button_back = Button('Назад', 32, WHITE, RED, WIDTH // 2, HEIGHT - 100, self.back_to_menu)

        # self.food_sound = pygame.mixer.Sound('data/sound/food.mp3')
        # self.died_sound = pygame.mixer.Sound('data/sound/died.mp3')

        self.rating = dict()
        self.load_rating()
        #self.save_rating()
        self.load_map()

    def load_rating(self):
        with open(RATING_FILE) as f:
            self.rating = json.load(f)

    def save_rating(self):
        self.rating = dict()
        self.rating['Арсений4'] = 444
        self.rating['Арсений2'] = 222
        self.rating['Арсений'] = 111


        #self.rating['Арсений'] = 100
        #self.rating['Я'] = 344
        with open(RATING_FILE, 'w') as f:
            json.dump(self.rating, f)


    def load_map(self):
        for y in range(len(MAP)):
            for x in range(len(MAP[y])):
                if MAP[y][x] == 0:
                    self.tile_sprites.add(Tile(x, y))
                elif MAP[y][x] == 1:
                    self.food_sprites.add(Food(x, y))
                elif MAP[y][x] == 8:
                    self.player = Pacman(x, y)
                    self.all_sprites.add(self.player)
        for i in [8, 9, 10]:
        #for i in [8]:
            ghost = Ghost(i, 10, self.player)
            self.ghost_sprites.add(ghost)
            self.ghosts.append(ghost)

    def draw_text(self, txt, size, color, x, y, font_type=FONT_FILE):
        font = pygame.font.Font(font_type, size)
        text_surface = font.render(txt, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def start_game(self):
        self.state = STATE_PLAY
        self.lives = 3

    def show_score(self):
        self.state = STATE_RATING

    def back_to_menu(self):
        self.state = STATE_MENU

    def menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = STATE_PLAY
            self.button_play.process()  # .click(event)
            self.button_score.process()  # .click(event)

    def menu_draw(self):
        self.screen.fill(BLACK)
        # bg = load_image('menu_bg.png')
        # self.screen.blit(bg, (0, 0))
        self.draw_text('PAC-MAN', 64, YELLOW, WIDTH // 2, 125)
        # self.draw_text('Начать игру', 32, WHITE, WIDTH // 2, 225)
        # self.draw_text('Рейтинг', 32, WHITE, WIDTH // 2, 300)
        self.draw_text(f'© 2022-{CURRENT_YEAR} Чалдаев Арсений', 10, GRAY, WIDTH - 85, HEIGHT - 30)

        self.button_play.draw(self.screen)
        self.button_score.draw(self.screen)

        # pygame.draw.arc(self.screen, RED,
        #                 (50, 30, 50, 50),
        #                 math.pi * 5 / 6, 2 * math.pi, 25)

    def rating_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = STATE_MENU
            self.button_back.process()

    def rating_draw(self):
        self.screen.fill(BLACK)
        self.draw_text('PAC-MAN', 64, YELLOW, WIDTH // 2, 125)

        h = 0
        for name, score in self.rating.items():
            self.draw_text(f'{name}', 32, WHITE, 150, 225 + h * 40)
            self.draw_text(f'{score}', 32, WHITE, 350, 225 + h * 40)
            #self.draw_text(f'{name} ··· {score}', 32, WHITE, WIDTH // 2, 225 + h * 40)
            h += 1
        self.button_back.draw(self.screen)
        self.draw_text(f'© 2022-{CURRENT_YEAR} Чалдаев Арсений', 10, GRAY, WIDTH - 85, HEIGHT - 30)


    def play_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.player.change_dir(UP)
        elif keys[pygame.K_RIGHT]:
            self.player.change_dir(RIGHT)
        elif keys[pygame.K_DOWN]:
            self.player.change_dir(DOWN)
        elif keys[pygame.K_LEFT]:
            self.player.change_dir(LEFT)

    def play_update(self):
        self.all_sprites.update()
        self.ghost_sprites.update()
        # self.tile_sprites.update()

    def play_draw(self):
        self.screen.fill(BLACK)
        self.tile_sprites.draw(self.screen)
        self.food_sprites.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.ghost_sprites.draw(self.screen)

    def play_collide(self):

        if pygame.sprite.spritecollide(self.player, self.food_sprites, True,
                                       pygame.sprite.collide_circle_ratio(0.5)):
            self.score += 10
            # self.food_sound.play()

        if pygame.sprite.spritecollide(self.player, self.ghost_sprites, False):
            # self.died_sound.play()
            if self.lives > 1:
                self.lives -= 1
                self.recovery_counter = 12
                self.state = STATE_RESPAWN
                # time.sleep(2)
                # self.player.reset()
                # for ghost in self.ghosts:
                #     ghost.reset()
            else:
                self.draw_text(f'GAME OVER', 18, WHITE, WIDTH / 2, 5)
                self.state = STATE_GAME_OVER
        else:
            self.draw_text(f'{self.lives} UP', 18, WHITE, WIDTH / 2 - 100, 5)
            self.draw_text(f'SCORE: {self.score}', 18, WHITE, WIDTH / 2, 5)
            # self.screen.draw.text(f'SCORE: {self.score}', topleft=(8, 4), fontsize=40)
            # self.screen. .draw.text('Hello!', center=(WIDTH / 2, HEIGHT / 2), fontsize=120)

    def run(self):
        while self.running:
            if self.state == STATE_MENU:
                self.menu_events()
                self.menu_draw()
            elif self.state == STATE_PLAY:
                self.play_events()
                self.play_update()
                self.play_draw()
                self.play_collide()
            elif self.state == STATE_RESPAWN:
                # time.sleep(1)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                #self.play_draw()
                self.screen.fill(BLACK)
                self.tile_sprites.draw(self.screen)
                self.food_sprites.draw(self.screen)
                #self.all_sprites.draw(self.screen)
                self.ghost_sprites.draw(self.screen)
                if self.recovery_counter > 0:
                    # pygame.draw.circle(self.screen, YELLOW, (20, 20), self.recovery_counter)
                    pygame.draw.circle(self.screen, YELLOW, self.player.rect.center, self.recovery_counter)
                    self.recovery_counter -= 1
                else:
                    self.player.reset()
                    for ghost in self.ghosts:
                        ghost.reset()
                    self.state = STATE_PLAY
            elif self.state == STATE_GAME_OVER:
                for event in pygame.event.get():
                    # check for closing window
                    if event.type == pygame.QUIT:
                        self.running = False
                # self.draw_text(f'GAME OVER', 18, WIDTH / 2, 5)
            elif self.state == STATE_RATING:
                self.rating_events()
                self.rating_draw()
            self.clock.tick(FPS)
            pygame.display.flip()

        pygame.quit()
        sys.exit()


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        #self.image = load_image('wall_1.png')
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)


class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.radius = 3
        self.image = pygame.Surface((2 * self.radius, 2 * self.radius), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = ((x + 0.5) * TILE_SIZE, (y + 0.5) * TILE_SIZE)


class Person(pygame.sprite.Sprite):
    def __init__(self, x, y, path):
        pygame.sprite.Sprite.__init__(self)
        self.start_pos_x = TILE_SIZE * x
        self.start_pos_y = TILE_SIZE * y
        # self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        # self.image.fill(color)
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

    def is_allow(self, row, col):
        return MAP[row][col] != 0

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

    def getPos(self):
        row = self.rect.centery // TILE_SIZE
        col = self.rect.centerx // TILE_SIZE
        return row, col


class Pacman(Person):
    def __init__(self, x, y):
        super().__init__(x, y, 'pac-man_pos11.png')

    def is_allow(self, row, col):
        return MAP[row][col] not in (0, 3, 4, 5, 6)

    def rotate(self):
        if self.dir == UP:
            self.image = pygame.transform.rotate(self.original_image, -90)
        elif self.dir == RIGHT:
            self.image = pygame.transform.flip(self.original_image, True, False)
        elif self.dir == DOWN:
            self.image = pygame.transform.rotate(self.original_image, 90)
        elif self.dir == LEFT:
            self.image = pygame.transform.flip(self.original_image, False, False)


class Ghost(Person):
    def __init__(self, x, y, pacman=None):
        super().__init__(x, y, 'blinky_pos1.png')
        self.speed = 4
        self.pacman = pacman
        self.goal = None

    def update(self):
        if self.rect.x % TILE_SIZE == 0 and self.rect.y % TILE_SIZE == 0:
            self.goal = self.pacman.getPos()
            self.new_dir = self.get_optimal_direction()
            # self.new_dir = self.get_random_direction()

        super().update()

    def get_optimal_direction(self):
        row = self.rect.centery // TILE_SIZE
        col = self.rect.centerx // TILE_SIZE

        queue = []
        visited = [(row, col)]
        dir = -1
        neighbours = [(UP, (0, -1)), (RIGHT, (1, 0)), (DOWN, (0, 1)), (LEFT, (-1, 0))]
        for dir, neighbour in neighbours:
            if 0 <= row + neighbour[1] < len(MAP):
                if 0 <= col + neighbour[0] < len(MAP[0]):
                    next_cell = (row + neighbour[1], col + neighbour[0])
                    if MAP[next_cell[0]][next_cell[1]] != 0:
                        queue.append((next_cell, dir))

        neighbours = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        while queue:
            curr_pos, dir = queue.pop(0)
            visited.append(curr_pos)
            if curr_pos == self.goal:
                break
            else:
                for neighbour in neighbours:
                    if 0 <= curr_pos[0] + neighbour[1] < len(MAP):
                        if 0 <= curr_pos[1] + neighbour[0] < len(MAP[0]):
                            next_cell = (curr_pos[0] + neighbour[1], curr_pos[1] + neighbour[0])
                            if next_cell not in visited:
                                if MAP[next_cell[0]][next_cell[1]] != 0:
                                    queue.append((next_cell, dir))
        return dir

    def get_random_direction(self):
        row = self.rect.y // TILE_SIZE
        col = self.rect.x // TILE_SIZE
        paths = []
        if row > 0 and self.is_allow(row - 1, col):
            paths.append(UP)
        if col < len(MAP[0]) - 1 and self.is_allow(row, col + 1):
            paths.append(RIGHT)
        if row < len(MAP) - 1 and self.is_allow(row + 1, col):
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


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
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


class Button:

    def __init__(self, text, size, color, hover_color, x, y, on_click_function=None):
        self.text = text
        self.color = color
        self.hoverColor = hover_color
        self.onClickFunction = on_click_function
        self.font = pygame.font.Font(FONT_FILE, size)
        self.text_surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.midtop = (x, y)

    def draw(self, screen):
        screen.blit(self.text_surface, self.text_rect)

    def click(self, event):
        x, y = pygame.mouse.get_pos()
        if self.text_rect.collidepoint(x, y):
            self.text_surface = self.font.render(self.text, True, self.hoverColor)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.onClickFunction()
        else:
            self.text_surface = self.font.render(self.text, True, self.color)

    def process(self):
        mousePos = pygame.mouse.get_pos()
        if self.text_rect.collidepoint(mousePos):
            self.text_surface = self.font.render(self.text, True, self.hoverColor)
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.onClickFunction()
        else:
            self.text_surface = self.font.render(self.text, True, self.color)


if __name__ == '__main__':
    game = Game()
    game.run()
