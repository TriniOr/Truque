# src/ui/components/text_input.py
import pygame
from src.ui.style import *

class TextInput:
    def __init__(self, rect, placeholder="", font_size=FONT_MD, max_length=20):
        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.max_length = max_length
        self.font = get_font(font_size)
        self.text = ""
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)

        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length:
                self.text += event.unicode

    def draw(self, surface):
        # borde — resaltado si activo
        border_color = COLOR_SELECTED if self.active else COLOR_PRIMARY
        pygame.draw.rect(surface, COLOR_BG, self.rect, border_radius=2)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=2)

        # texto o placeholder
        if self.text:
            text_surf = self.font.render(self.text, True, COLOR_TEXT)
        else:
            text_surf = self.font.render(self.placeholder, True, COLOR_TEXT_DIM)

        # clip para que no se salga del rect
        surface.set_clip(self.rect.inflate(-8, 0))
        surface.blit(text_surf, text_surf.get_rect(midleft=(self.rect.x + 8, self.rect.centery)))
        surface.set_clip(None)