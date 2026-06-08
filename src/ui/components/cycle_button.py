import pygame
from src.ui.style import *

class CycleButton:
    def __init__(self, rect, options, initial=0, font_size=FONT_MD):
        self.rect = pygame.Rect(rect)
        self.options = options
        self.index = initial
        self.font = get_font(font_size)
        self.hovered = False

    @property
    def value(self):
        return self.options[self.index]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.index = (self.index + 1) % len(self.options)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        bg_color = COLOR_HOVER if self.hovered else COLOR_PRIMARY
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=2)
        text_surf = self.font.render(self.options[self.index], True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)