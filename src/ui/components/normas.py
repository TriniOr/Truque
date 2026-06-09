# src/ui/components/normas.py
import pygame
from src.ui.components.carta import CartaUI
from src.ui.style import *

class PanelNormas:
    def __init__(self, paginas, btn_pos=(WINDOW_SIZE[0] - 100 - 10, 60)):
        self.paginas = paginas
        self.btn_pos = btn_pos
        self.visible = False
        self.pagina_actual = 0

        # tamaño panel
        self.panel_x = 0
        self.panel_y = 100
        self.panel_w = WINDOW_SIZE[0]
        self.panel_h = WINDOW_SIZE[1] - 100

        # sidebar
        self.btn_w = 160
        self.btn_h = BUTTON_H
        self.gap = 8
        self.sidebar_x = self.panel_x + 20

        # botón toggle
        self._toggle_rect = pygame.Rect(*btn_pos, 100, 40)

    def toggle(self):
        self.visible = not self.visible

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._toggle_rect.collidepoint(event.pos):
                self.toggle()
                return
            if not self.visible:
                return
            for i in range(len(self.paginas)):
                if self._sidebar_rect(i).collidepoint(event.pos):
                    self.pagina_actual = i

    def _sidebar_rect(self, i):
        x = self.sidebar_x
        y = self.panel_y + 60 + i * (self.btn_h + self.gap)
        return pygame.Rect(x, y, self.btn_w, self.btn_h)

    def draw(self, surface):
        color = COLOR_SELECTED if self.visible else COLOR_PRIMARY
        pygame.draw.rect(surface, color, self._toggle_rect, border_radius=2)
        font = get_font(FONT_SM)
        surf = font.render("Normas", True, COLOR_TEXT)
        surface.blit(surf, surf.get_rect(center=self._toggle_rect.center))

        if not self.visible:
            return

        # fondo overlay
        overlay = pygame.Surface((self.panel_w, self.panel_h), pygame.SRCALPHA)
        overlay.fill((*COLOR_BG, 230))
        surface.blit(overlay, (self.panel_x, self.panel_y))

        # sidebar
        for i, pagina in enumerate(self.paginas):
            rect = self._sidebar_rect(i)
            color = COLOR_SELECTED if i == self.pagina_actual else COLOR_PRIMARY
            pygame.draw.rect(surface, color, rect, border_radius=2)
            label = pagina.get("titulo", f"Página {i+1}")
            surf = font.render(label, True, COLOR_TEXT)
            surface.blit(surf, surf.get_rect(center=rect.center))
        self._draw_contenido(surface)

    # contenido
    def _draw_contenido(self, surface):
        padding = 16
        contenido_x = self.panel_x + self.btn_w + 60
        contenido_w = self.panel_x + self.panel_w - contenido_x - 20
        x = contenido_x
        y = self.panel_y + 60

        bloques = self.paginas[self.pagina_actual].get("bloques", [])

        for bloque in bloques:
            tipo = bloque.get("tipo")

            if tipo == "nueva_linea":
                x = contenido_x
                y += LINE_H
                continue

            if tipo == "titulo":
                if x > contenido_x:
                    y += LINE_H
                x = contenido_x
                font = get_font(FONT_XL)
                surf = font.render(bloque["texto"], True, COLOR_TEXT_HIGH)
                surface.blit(surf, (x, y))
                y += surf.get_height() + padding * 2
                x = contenido_x
                continue

            if tipo == "separador":
                if x > contenido_x:
                    y += LINE_H
                pygame.draw.line(surface, COLOR_PRIMARY,
                                (contenido_x, y), (contenido_x + contenido_w, y), 1)
                y += padding * 2
                x = contenido_x
                continue

            if tipo == "texto":
                color = bloque.get("color", COLOR_TEXT)
                size = FONT_MD + 4 if bloque.get("negrita") else FONT_MD
                font = get_font(size)
                surf = font.render(bloque["texto"], True, color)
                w = surf.get_width()

                if x + w > contenido_x + contenido_w:
                    x = contenido_x
                    y += LINE_H

                surface.blit(surf, (x, y))
                x += w

            if tipo == "carta":
                w = CARD_SIZE_SM[0]

                if x + w > contenido_x + contenido_w:
                    x = contenido_x
                    y += LINE_H

                carta_ui = CartaUI(carta=bloque["carta"], pos=(x, y - 15), size="sm")
                carta_ui.draw(surface)
                x += w + 4