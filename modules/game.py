from modules.button import Button
from modules.level import Level
from modules.rating import Rating
from modules.sprites import *

pygame.init()
pygame.mixer.init()


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()

        self.running = True
        self.with_music = True
        self.mute_icon = Mute()
        self.player = None

        self.level = Level()
        self.rating = Rating()
        self.all_sprites = pygame.sprite.Group()
        self.tile_sprites = pygame.sprite.Group()
        self.food_sprites = pygame.sprite.Group()
        self.ghost_sprites = pygame.sprite.Group()
        self.ghosts = []
        self.lives = 3
        self.score = 0

        self.load_map()

        self.state = STATE_MENU
        self.game_states = {
            STATE_MENU: GameStateMenu(self),
            STATE_PLAY: GameStatePlay(self),
            STATE_PAUSE: GameStatePause(self),
            STATE_RESPAWN: GameStateRespawn(self),
            STATE_RATING: GameStateRating(self),
            STATE_WON: GameStateResult(self),
            STATE_GAME_OVER: GameStateResult(self)
        }

    def load_map(self):
        self.all_sprites.empty()
        self.tile_sprites.empty()
        self.food_sprites.empty()
        self.ghost_sprites.empty()
        self.ghosts = []
        self.player = None

        for y in range(len(self.level.map) - 1, -1, -1):
            for x in range(len(self.level.map[y])):
                if self.level.map[y][x] == 0:
                    self.tile_sprites.add(Tile(x, y))
                elif self.level.map[y][x] == 1:
                    self.food_sprites.add(Food(x, y))
                elif self.level.map[y][x] == 8:
                    self.player = Pacman(x, y, self.level)
                elif self.level.map[y][x] in (4, 5, 6):
                    if self.level.map[y][x] == 4:
                        ghost = BlinkyGhost(x, y, self.level, self.player)
                    elif self.level.map[y][x] == 5:
                        ghost = ClydeGhost(x, y, self.level)
                    else:
                        ghost = InkyGhost(x, y, self.level)
                    self.ghost_sprites.add(ghost)
                    self.ghosts.append(ghost)
        self.all_sprites.add(self.mute_icon)

    def run(self):
        while self.running:
            self.game_states[self.state].run()
            self.clock.tick(FPS)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def draw_sprites(self):
        self.screen.fill(BLACK)
        self.tile_sprites.draw(self.screen)
        self.food_sprites.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.ghost_sprites.draw(self.screen)
        if self.state != STATE_RESPAWN:
            self.player.draw(self.screen)

    def change_music(self):
        self.with_music = not self.with_music
        if self.with_music:
            self.mute_icon.unmute()
        else:
            self.mute_icon.mute()

    def reset(self):
        self.lives = 3
        self.score = 0
        self.level.reset()
        self.load_map()


class GameState:
    def __init__(self, game):
        self.game = game

    def run(self):
        self.process_events()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

    def draw_text(self, txt, size, color, x, y, font_type=FONT_FILE):
        font = pygame.font.Font(font_type, size)
        text_surface = font.render(txt, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.game.screen.blit(text_surface, text_rect)


class GameStateMenu(GameState):
    def __init__(self, game):
        super().__init__(game)

        self.button_play = Button('Начать игру', 32, WHITE, RED, WIDTH // 2, 225, self.start_game)
        self.button_score = Button('Рейтинг', 32, WHITE, RED, WIDTH // 2, 300, self.show_score)

    def run(self):
        self.process_events()
        self.draw()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.game.state = STATE_PLAY
            self.button_play.process()
            self.button_score.process()

    def draw(self):
        self.game.screen.fill(BLACK)
        self.draw_text('PAC-MAN', 64, YELLOW, WIDTH // 2, 125)
        self.draw_text(f'© 2022-{CURRENT_YEAR} Чалдаев Арсений', 10, GRAY, WIDTH - 85, HEIGHT - 30)

        self.button_play.draw(self.game.screen)
        self.button_score.draw(self.game.screen)

    def start_game(self):
        self.game.reset()
        self.game.state = STATE_PLAY

    def show_score(self):
        self.game.state = STATE_RATING


class GameStatePlay(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.food_sound = pygame.mixer.Sound('data/sounds/food.mp3')
        self.died_sound = pygame.mixer.Sound('data/sounds/died.mp3')

    def run(self):
        self.process_events()
        self.update()
        self.draw()
        self.process_collide()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game.state = STATE_PAUSE
                elif event.key == pygame.K_m:
                    self.game.change_music()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.game.player.change_dir(UP)
        elif keys[pygame.K_RIGHT]:
            self.game.player.change_dir(RIGHT)
        elif keys[pygame.K_DOWN]:
            self.game.player.change_dir(DOWN)
        elif keys[pygame.K_LEFT]:
            self.game.player.change_dir(LEFT)

    def update(self):
        self.game.player.update()
        self.game.ghost_sprites.update()

    def draw(self):
        self.game.draw_sprites()

    def process_collide(self):
        if pygame.sprite.spritecollide(self.game.player, self.game.food_sprites, True,
                                       pygame.sprite.collide_circle_ratio(0.5)):
            if self.game.with_music:
                self.food_sound.play()
            self.game.score += 10
            self.game.level.food_count -= 1
            if self.game.level.food_count == 0:
                if self.game.level.next_level():
                    self.game.load_map()
                    self.game.state = STATE_PAUSE
                else:
                    self.game.state = STATE_WON

        if pygame.sprite.spritecollide(self.game.player, self.game.ghost_sprites, False):
            if self.game.with_music:
                self.died_sound.play()
            if self.game.lives > 1:
                self.game.lives -= 1
                self.game.state = STATE_RESPAWN
            else:
                self.game.state = STATE_GAME_OVER
        else:
            live_text = f'{self.game.lives} {"ЖИЗНЬ" if self.game.lives == 1 else "ЖИЗНИ"}'
            self.draw_text(live_text, 18, WHITE, WIDTH // 2 - 150, 0)
            self.draw_text(f'РЕЗУЛЬТАТ: {self.game.score}', 18, WHITE, WIDTH // 2, 0)


class GameStatePause(GameState):
    def __init__(self, game):
        super().__init__(game)

    def run(self):
        self.process_events()
        self.draw()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game.state = STATE_PLAY
                elif event.key == pygame.K_m:
                    self.game.change_music()

    def draw(self):
        self.game.draw_sprites()
        live_text = f'{self.game.lives} {"ЖИЗНЬ" if self.game.lives == 1 else "ЖИЗНИ"}'
        self.draw_text(live_text, 18, WHITE, WIDTH // 2 - 150, 0)
        self.draw_text(f'РЕЗУЛЬТАТ: {self.game.score}', 18, WHITE, WIDTH // 2, 0)
        self.draw_text('ПАУЗА', 24, WHITE, WIDTH // 2, HEIGHT // 2 - 5)


class GameStateRespawn(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.recovery_counter = 12

    def run(self):
        self.process_events()
        self.draw()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

    def draw(self):
        self.game.draw_sprites()
        if self.recovery_counter > 0:
            pygame.draw.circle(self.game.screen, YELLOW, self.game.player.rect.center, self.recovery_counter)
            self.recovery_counter -= 1
        else:
            self.game.player.reset()
            for ghost in self.game.ghosts:
                ghost.reset()
            self.recovery_counter = 12
            self.game.state = STATE_PLAY
        live_text = f'{self.game.lives} {"ЖИЗНЬ" if self.game.lives == 1 else "ЖИЗНИ"}'
        self.draw_text(live_text, 18, WHITE, WIDTH // 2 - 150, 0)
        self.draw_text(f'РЕЗУЛЬТАТ: {self.game.score}', 18, WHITE, WIDTH // 2, 0)


class GameStateRating(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.button_back = Button('Назад', 32, WHITE, RED, WIDTH // 2, HEIGHT - 100, self.back_to_menu)

    def run(self):
        self.process_events()
        self.draw()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    self.game.state = STATE_MENU
            self.button_back.process()

    def draw(self):
        self.game.screen.fill(BLACK)
        self.draw_text('PAC-MAN', 64, YELLOW, WIDTH // 2, 125)

        h = 0
        for name, score in self.game.rating.get_sorted()[:5]:
            self.draw_text(f'{name}', 32, WHITE, 150, 225 + h * 40)
            self.draw_text(f'{score}', 32, WHITE, 350, 225 + h * 40)
            h += 1
        self.button_back.draw(self.game.screen)
        self.draw_text(f'© 2022-{CURRENT_YEAR} Чалдаев Арсений', 10, GRAY, WIDTH - 85, HEIGHT - 30)

    def back_to_menu(self):
        self.game.state = STATE_MENU


class GameStateResult(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.button_enter = Button('Сохранить', 32, WHITE, RED, WIDTH // 2, HEIGHT - 100, self.save_user)
        self.input_rect = pygame.Rect(50, 275, WIDTH - 100, 32)
        self.font = pygame.font.Font(FONT_FILE, 20)
        self.color = WHITE
        self.user_text = ''
        self.active_input = False

    def save_user(self):
        if self.user_text:
            self.game.rating.add_result(self.user_text, self.game.score)
        self.game.state = STATE_RATING

    def run(self):
        self.process_events()
        self.draw()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.active_input = self.input_rect.collidepoint(event.pos)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.state = STATE_MENU
                    return
                if self.active_input:
                    if event.key == pygame.K_BACKSPACE:
                        self.user_text = self.user_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.save_user()
                    else:
                        self.user_text += event.unicode
        self.button_enter.process()

    def draw(self):
        self.game.screen.fill(BLACK)
        result = 'ПОБЕДА!' if self.game.state == STATE_WON else 'ПРОИГРАЛ'
        self.draw_text(result, 64, YELLOW, WIDTH // 2, 125)
        self.draw_text(f'Результат: {self.game.score}', 24, WHITE, WIDTH // 2, 225)

        self.color = YELLOW if self.active_input else WHITE
        text_surface = self.font.render(self.user_text, True, WHITE)
        self.input_rect.w = max(WIDTH - 100, text_surface.get_width() + 10)
        self.game.screen.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        pygame.draw.rect(self.game.screen, self.color, self.input_rect, 2)
        self.button_enter.draw(self.game.screen)
