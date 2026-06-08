import pygame
from src.ui.style import *
from src.dominio.cartas import Carta, Palo, Numero

_sprite_cache = {}

def _cargar_sprites():
    for palo in Palo:
        for numero in Numero:
            key = (palo.name, numero.value)
            path = f"src/ui/cartas/{palo.path}_{numero.path}.png"
            img = pygame.image.load(path).convert_alpha()
            _sprite_cache[key] = {
                "md": img,
                "lg": pygame.transform.scale2x(img),
                "sm": pygame.transform.scale(img, CARD_SIZE_SM)
            }

    reverso = pygame.image.load("src/ui/cartas/reverso.png").convert_alpha()
    _sprite_cache[("REVERSO", "REVERSO")] = {
        "md": reverso,
        "lg": pygame.transform.scale2x(reverso),
        "sm": pygame.transform.scale(reverso, CARD_SIZE_SM)
    }

class CartaUI:
    def __init__(self, carta: Carta | None, pos, size="md", border_color=None,
                 face_up=True, on_click=None, hover_color=CARD_HOVER):
        self.carta = carta
        self.pos = pos
        self.size = size
        self.border_color = border_color
        self.face_up = face_up
        self.on_click = on_click
        self.hover_color = hover_color
        self.hovered = False
        if not _sprite_cache:
            _cargar_sprites()

    def _get_rect(self):
        sizes = {"sm": CARD_SIZE_SM, "md": CARD_SIZE, "lg": CARD_SIZE_LG}
        return pygame.Rect(self.pos, sizes[self.size])

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._get_rect().collidepoint(event.pos) and self.on_click:
                self.on_click()

    def update(self, mouse_pos):
        self.hovered = self._get_rect().collidepoint(mouse_pos)

    def draw(self, surface):
        key = ("REVERSO", "REVERSO")
        if self.face_up and self.carta is not None:
            key = (self.carta.palo.name, self.carta.numero.value)

        sprite = _sprite_cache[key][self.size]

        active_border = self.hover_color if self.hovered else self.border_color
        if active_border:
            mask = pygame.mask.from_surface(sprite)
            border_surf = mask.to_surface(
                setcolor=active_border,
                unsetcolor=(0, 0, 0, 0)
            )
            border_w = {"sm": 1, "md": 2, "lg": 4}[self.size]
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                surface.blit(border_surf, (self.pos[0] + dx * border_w, self.pos[1] + dy * border_w))

        surface.blit(sprite, self.pos)