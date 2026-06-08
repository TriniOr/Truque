# src/ui/components/number_selector.py
import pygame
from src.ui.style import *
from src.ui.components.button import Button

class NumberSelector:
    def __init__(self, pos, label, min_val, max_val, initial=1, font_size=FONT_LG, on_change=None):
        self.label = label
        self.value = initial
        self.min_val = min_val
        self.max_val = max_val
        self.font = get_font(font_size)
        self.on_change = on_change
        self.label_font = get_font(FONT_MD)

        x, y = pos
        self.btn_minus = Button(
            rect=(x, y, BUTTON_H, BUTTON_H),
            label="-",
            on_click=self._decrement,
        )
        self.btn_plus = Button(
            rect=(x + BUTTON_H + 60, y, BUTTON_H, BUTTON_H),
            label="+",
            on_click=self._increment,
        )
        self.value_rect = pygame.Rect(x + BUTTON_H, y, 60, BUTTON_H)

    def _increment(self):
        if self.value < self.max_val:
            self.value += 1
        if self.on_change:
            self.on_change(self.value)

    def _decrement(self):
        if self.value > self.min_val:
            self.value -= 1
        if self.on_change:
            self.on_change(self.value)

    def handle_event(self, event):
        self.btn_minus.handle_event(event)
        self.btn_plus.handle_event(event)

    def update(self, mouse_pos):
        self.btn_minus.update(mouse_pos)
        self.btn_plus.update(mouse_pos)

    def draw(self, surface):        
        self.btn_minus.color = COLOR_FORBIDDEN if self.value == self.min_val else COLOR_PRIMARY
        self.btn_plus.color  = COLOR_FORBIDDEN if self.value == self.max_val else COLOR_PRIMARY

        # label
        label_surf = self.label_font.render(self.label, True, COLOR_TEXT)
        surface.blit(label_surf, (self.value_rect.x - BUTTON_H, self.value_rect.y - 40))

        # valor central
        val_surf = self.font.render(str(self.value), True, COLOR_TEXT)
        val_rect = val_surf.get_rect(center=self.value_rect.center)
        surface.blit(val_surf, val_rect)

        self.btn_minus.draw(surface)
        self.btn_plus.draw(surface)