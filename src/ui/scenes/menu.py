import pygame
import random
from src.juegos.truque.truque import Truque
from src.ui.components.number_selector import NumberSelector
from src.ui.components.text_input import TextInput
from src.ui.scenes.game import GameScene
from src.ui.style import *
from src.ui.scenes.base import BaseScene
from src.ui.components.cycle_button import CycleButton
from src.ui.components.button import Button

class MenuScene(BaseScene):
    
    def __init__(self, app):
        super().__init__(app)
        self.selector = NumberSelector(
            pos=(500, 260),
            label="Jugadores por equipo",
            min_val=1,
            max_val=5,
            initial=2,
            on_change=self._build_slots,
        )
        self._build_slots(self.selector.value)
        self.iniciar = Button(
            rect=((WINDOW_SIZE[0] - BUTTON_W) // 2, 700,  BUTTON_W, BUTTON_H),
            label="Iniciar Juego",
            on_click=self._start_game,
        )

    def handle_event(self, event):
        self.selector.handle_event(event)
        for slot in self.slots_team1 + self.slots_team2:
            slot["type"].handle_event(event)
            slot["name"].handle_event(event)
        self.iniciar.handle_event(event)

    def update(self, dt):
        self.selector.update(pygame.mouse.get_pos())

    def draw(self, surface):
        surface.fill(COLOR_BG)
        self.draw_label(surface, "TRUQUE", (500, 80), font_size=100)
        self.selector.draw(surface) 
        self.draw_label(surface, "Equipo 1", (500, 330), font_size=FONT_LG)
        self.draw_label(surface, "Equipo 2", (1000, 330), font_size=FONT_LG)
        for slot in self.slots_team1 + self.slots_team2:
            slot["type"].draw(surface)
            slot["name"].draw(surface)
        self.iniciar.draw(surface)

    def _build_slots(self, n):
        self.slots_team1 = self._make_slots(n, col = 1)
        self.slots_team2 = self._make_slots(n, col = 2)

    def _make_slots(self, n, col = 1):
        slots = []
        for i in range(n):
            y = 390 + i * 60
            x = 500*col
            slots.append({
                "type": CycleButton(rect=(x + 220, y, 140, 40), 
                                    options=["Humano", "IA Facil", "IA Medio", "IA Dificil", "IA Experta"],
                                    initial= 0 if (i == 0 and col == 1) else 2), 
                "name": TextInput(rect=(x, y, 200, 40), placeholder="Nombre")
            })
        return slots

    def _start_game(self):

        nombres_jugadores = []
        tipo_jugador = []
        for equipos in zip(self.slots_team1, self.slots_team2):
            for jugador in equipos:
                nombres_jugadores.append(jugador["name"].text if jugador["name"].text != "" else 
                                         random.choice([nombre for nombre in NOMBRES_PUEBLO if nombre not in nombres_jugadores]))
                tipo_jugador.append(jugador["type"].value)

        truque = Truque(nombres_jugadores)
        self.app.change_scene(GameScene(self.app, truque, tipo_jugador))