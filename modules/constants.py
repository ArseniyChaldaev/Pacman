from datetime import datetime

CURRENT_YEAR = datetime.now().year

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
STATE_PAUSE = 6

TILE_SIZE = 24
WIDTH = 19 * TILE_SIZE
HEIGHT = 22 * TILE_SIZE
FPS = 25

FONT_FILE = 'data/font/pacmania_cyrillic.otf'
RATING_FILE = 'data/score/top.json'
