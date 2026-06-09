import pygame
from src.ui.components.carta import CartaUI
from src.ui.style import *

class MesaCartas:
    def __init__(self, pos, cartas, nombre, dx=25, dy=5,
                 font_size=FONT_MD, font_color=COLOR_TEXT, seleccionadas = [], mano=False, flor=None, comentario=None):
        self.pos = pos
        self.cartas = cartas
        self.nombre = nombre
        self.dx = dx
        self.dy = dy
        self.font_size = font_size
        self.font_color = font_color
        self.seleccionadas = seleccionadas
        self.mano = mano
        self.flor = flor
        self.comentario = comentario
        self._build()

    def _draw_bocadillo(self, surface, y_base):
        font = get_font(FONT_MD)
        text_surf = font.render(self.comentario, True, (20, 20, 20))
        padding = 10
        w = text_surf.get_width() + padding * 2
        h = text_surf.get_height() + padding * 2
        x = self.pos[0]
        y = y_base - h - 12  # 12px encima

        pygame.draw.rect(surface, (255, 255, 255), (x, y, w, h), border_radius=8)
        surface.blit(text_surf, (x + padding, y + padding))

        # cola del bocadillo
        cx = x + 16
        pygame.draw.polygon(surface, (255, 255, 255), [
            (cx, y + h),
            (cx + 10, y + h),
            (cx + 5, y + h + 8),
        ])

    def _build(self):
        self.cartas_ui = []
        for i, carta in enumerate(self.cartas):
            x = self.pos[0] + i * self.dx
            y = self.pos[1] + i * self.dy
            self.cartas_ui.append(CartaUI(carta=carta, pos=(x, y), size="md", 
                border_color= self.font_color if i in self.seleccionadas else None))

    def draw(self, surface):
        # cartas apiladas
        for carta_ui in self.cartas_ui:
            carta_ui.draw(surface)

        # nombre debajo
        label_y = self.pos[1] + CARD_SIZE[1] + max(len(self.cartas) * self.dy, 0) + 8
        font = get_font(self.font_size)
        surf = font.render(self.nombre, True, self.font_color)
        rect = surf.get_rect(**{"topleft": (self.pos[0], label_y)})
        surface.blit(surf, rect)

        if self.comentario is not None:
            self._draw_bocadillo(surface, self.pos[1])

        # Circulo marcando mano y f marcando flor
        if self.mano:
            cx = self.pos[0] - 10
            cy = label_y + self.font_size // 2 - 10
            pygame.draw.circle(surface, COLOR_MANO, (cx, cy), 7)   # ficha dorada
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 7, width=2)  # borde blanco

        if self.flor:
            cx = self.pos[0] - 10
            cy = label_y + self.font_size // 2 + 10
            font = get_font(FONT_MD)
            surf = font.render("F", True, COLOR_BG)
            borde = font.render("F", True, (255, 255, 255))
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                surface.blit(borde, borde.get_rect(center=(cx + dx, cy + dy)))
            surface.blit(surf, surf.get_rect(center=(cx, cy)))