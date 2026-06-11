from src.juegos.truque.truque import Truque
from src.ui.style import *


class BaseView:
    def __init__(self, app, truque: Truque, tipo_jugador: str):
        self.app = app
        self.truque: Truque = truque
        self.tipo_jugador = tipo_jugador

    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self, surface): pass    
    def draw_label(self, surface, text, pos, font_size=FONT_MD, color=COLOR_TEXT, anchor="topleft"):
        font = get_font(font_size)
        surf = font.render(text, True, color)
        rect = surf.get_rect(**{anchor: pos})
        surface.blit(surf, rect)