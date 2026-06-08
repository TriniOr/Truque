import pygame
from src.ui.style import *

class Button:
    def __init__(
        self,
        rect: tuple,
        label: str,
        on_click=None,
        color=COLOR_PRIMARY,
        color_hover=COLOR_HOVER,
        color_selected=COLOR_SELECTED,
        text_color=COLOR_TEXT,
        font_size=FONT_MD,
        selected=False,
    ):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.on_click = on_click
        self.color = color
        self.color_hover = color_hover
        self.color_selected = color_selected
        self.text_color = text_color
        self.font = get_font(font_size)
        self.selected = selected
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        if self.selected:
            color = self.color_selected
        elif self.hovered:
            color = self.color_hover
        else:
            color = self.color

        pygame.draw.rect(surface, color, self.rect, border_radius=2)

        text_surf = self.font.render(self.label, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)