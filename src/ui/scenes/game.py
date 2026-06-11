import pygame
from src.ui.scenes.base import BaseScene
from src.juegos.truque import Truque 
from src.ui.style import *
from src.ui.scenes.views.config_view import ConfigView
from src.ui.scenes.views.juego_view import JuegoView
from src.ui.normas import NORMAS
from src.ui.components.normas import PanelNormas

class GameScene(BaseScene):
    def __init__(self, app, truque: Truque, tipo_jugador):
        super().__init__(app)
        self.truque: Truque = truque
        self.tipo_jugador = tipo_jugador
        self.view = ConfigView(self, self.truque, tipo_jugador)
        self.panel_normas = PanelNormas(NORMAS)

    def handle_event(self, event):
        self.view.handle_event(event)
        self.panel_normas.handle_event(event)


    def update(self, dt):
        self.view.update(dt)

    def set_view(self, view:str, siguiente_jugador = -1):
        if view == "config":
            self.view = ConfigView(self, self.truque, self.tipo_jugador)
            
        elif view == "juego":
            self.view = JuegoView(self, self.truque, self.tipo_jugador, siguiente_jugador)
            
        elif view == "new_game":
            from src.ui.scenes.menu import MenuScene
            self.app.change_scene(MenuScene(self.app))

    def draw(self, surface):
        surface.fill(COLOR_BG)
        self._draw_marcador(surface)
        self.view.draw(surface)
        self.panel_normas.draw(surface)

    def _draw_marcador(self, surface):
        p_partidas = self.truque.partida.puntuacion
        p_juegos = self.truque.partida.juego.puntuacion if self.truque.partida.juego else ["-", "-"]

        self.draw_label(surface, f"Equipo 1", (10, 10), font_size=FONT_LG, color=COLOR_EQUIPO1)
        self.draw_label(surface, f"Equipo 2", (10, 50), font_size=FONT_LG, color=COLOR_EQUIPO2)
        self.draw_label(surface, f"{p_partidas[0]}", (200,10), font_size=FONT_LG)
        self.draw_label(surface, f"{p_partidas[1]}", (200,50), font_size=FONT_LG)
        self.draw_label(surface, f"{p_juegos[0]}", (240,10), font_size=FONT_LG)
        self.draw_label(surface, f"{p_juegos[1]}", (240,50), font_size=FONT_LG)

        apuestas = self.truque.estado_juego()['partida']["apuestas"]
        if len(apuestas) > 0:
            # Apuesta de flor si existe
            if len(apuestas['flor']) > 0:
                self.draw_label(surface, 
                                "Flor:", 
                                (350,30), 
                                font_size=FONT_LG)
                self.draw_label(surface, 
                                "-" if apuestas['flor']['estado'] == "cantando" else f"{apuestas['flor']['apuesta']}",
                                (450, 30),
                                font_size=FONT_LG,
                                color= (COLOR_EQUIPO1 if apuestas['flor']['equipo'] == 1 else COLOR_EQUIPO2)
                                if apuestas['flor']['estado'] == "ganada" else COLOR_TEXT
                                )
            # Apuesta de pares si existe (y no existe flor)
            elif len(apuestas['pares']) > 0:
                self.draw_label(surface, 
                                "Pares:", 
                                (350,30), 
                                font_size=FONT_LG)
                self.draw_label(surface, 
                                f"{apuestas['pares']['apuesta']}",
                                (480, 30),
                                font_size=FONT_LG,
                                color= (COLOR_EQUIPO1 if apuestas['pares']['equipo'] == 1 else COLOR_EQUIPO2)
                                  if apuestas['pares']['estado'] == "ganada" else COLOR_TEXT
                                )
            # Apuesta de truque si existe
            if len(apuestas['truque']) > 0:
                self.draw_label(surface, 
                                "Truque:", 
                                (550,30), 
                                font_size=FONT_LG)
                self.draw_label(surface, 
                                f"{apuestas['truque']['apuesta']}",
                                (700, 30),
                                font_size=FONT_LG,
                                color= (COLOR_EQUIPO1 if apuestas['truque']['equipo'] == 1 else COLOR_EQUIPO2)
                                if apuestas['truque']['estado'] == "ganada" else COLOR_TEXT
                                )
                
