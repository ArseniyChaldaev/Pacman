import pygame

from modules.constants import FONT_FILE


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

    def process(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.text_rect.collidepoint(mouse_pos):
            self.text_surface = self.font.render(self.text, True, self.hoverColor)
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.onClickFunction()
        else:
            self.text_surface = self.font.render(self.text, True, self.color)
