# src/ui/views/config_view.py
import pygame
from src.juegos.truque.truque import Truque
from src.ui.scenes.views.base_view import BaseView
from src.ui.components.button import Button
from src.ui.style import *

class ConfigView(BaseView):
    def __init__(self, app, truque: Truque, tipo_jugador: str):
        super().__init__(app, truque, tipo_jugador)
        self.jugador_actual = -1
        self.botones = []
        self._pending_view = None
        self._ejecutar_ia = False
        self._construir_botones()

    def _construir_botones(self):
        self._pending_view = None
        self._ejecutar_ia = False
        self.botones = []
        acciones = self.truque.acciones_disponibles()

        # Caso 1: No hay jugador seleccionado (jugador_actual == -1)
        # Si hay alguna opción disponible de la máquina, la mostramos
        # Caso iniciar juego
        if len([accion for accion, jugador, opciones in acciones 
                if jugador == -1 and accion in ["iniciar_juego"]]) > 0:
            
            self.botones.append(Button(
                rect=((WINDOW_SIZE[0] - BUTTON_W) // 2, (WINDOW_SIZE[1] - BUTTON_H) // 2, BUTTON_W, BUTTON_H),
                label="Iniciar Juego",
                on_click=lambda: self._ejecutar("iniciar_juego"),
            ))
            return

        # Caso iniciar ronda
        if len([accion for accion, jugador, opciones in acciones 
                if jugador == -1 and accion in ["iniciar_ronda"]]) > 0:
            
            self.botones.append(Button(
                rect=((WINDOW_SIZE[0] - BUTTON_W) // 2, (WINDOW_SIZE[1] - BUTTON_H) // 2, BUTTON_W, BUTTON_H),
                label="Iniciar Ronda",
                on_click=lambda: self._ejecutar("iniciar_ronda"),
            ))
            return

        # Caso repartir cartas
        if len([accion for accion, jugador, opciones in acciones 
                if jugador == -1 and accion in ["repartir_cartas"]]) > 0:
            
            self.botones.append(Button(
                rect=((WINDOW_SIZE[0] - BUTTON_W) // 2, (WINDOW_SIZE[1] - BUTTON_H) // 2, BUTTON_W, BUTTON_H),
                label="Repartir Cartas",
                on_click=lambda: self._ejecutar("repartir_cartas"),
            ))

            # Cuando se reparten cartas, cada equipo puede apostar pares
            apuestas_pares = [opciones for accion, jugador, opciones in acciones
                    if accion == "apostar_pares" ]
            if len(apuestas_pares) > 0:
                for equipo in [0, 1]:
                    self.botones.append(Button(
                        rect=((WINDOW_SIZE[0] - BUTTON_W) // 2 + (equipo*2-1) * (BUTTON_W //2 + PADDING), (WINDOW_SIZE[1] - BUTTON_H) // 2 + 2*BUTTON_H, BUTTON_W, BUTTON_H),
                        label=f"La falta (Equipo {equipo + 1})",
                        on_click=lambda equipo=equipo: self._ejecutar("apostar_pares", 
                                jugador=self.truque.partida.equipos[equipo].jugadores[0].id, 
                                apuesta= apuestas_pares[0]["apuesta"]["max"]),
                    ))
            return
        
        # Caso terminar juego (puntuación mayor a 31, en ningun caso los dos equipos suman más de 31 a la vez (se cuenta antes pares))
        if len([accion for accion, jugador, opciones in acciones 
                if jugador == -1 and accion in ["terminar_juego"]]) > 0:
            
            self.botones.append(Button(
                rect=((WINDOW_SIZE[0] - BUTTON_W) // 2, (WINDOW_SIZE[1] - BUTTON_H) // 2, BUTTON_W, BUTTON_H),
                label="Terminar Juego",
                on_click=lambda: self._ejecutar("terminar_juego"),
            ))

            return
        
        
        # Caso terminar juego (puntuación mayor a 31, en ningun caso los dos equipos suman más de 31 a la vez (se cuenta antes pares))
        if len([accion for accion, jugador, opciones in acciones 
                if jugador == -1 and accion in ["terminar_partida"]]) > 0:
            
            self.botones.append(Button(
                rect=((WINDOW_SIZE[0] - BUTTON_W) // 2, (WINDOW_SIZE[1] - BUTTON_H) // 2, BUTTON_W, BUTTON_H),
                label="Terminar Partida",
                on_click=lambda: self.app.set_view("nueva_partida"),
            ))
            
            return
        
        # Por último, si estamos en ronda de partida, si el jugador es un usuario ponemos su pantalla
        siguiente_jugador = self.truque.estado_juego().get("partida").get("siguiente_jugador")
        if self.tipo_jugador[siguiente_jugador] == "Humano":
            

            # Si hay más de un jugador controlados por el usuario, ponemos una pantalla intermedia para confirmar el cambio de jugador
            if sum([j == "Humano" for j in self.tipo_jugador]) > 1:

                # Botón para confirmar cambio de jugador
            
                self.botones.append(Button(
                    rect=((WINDOW_SIZE[0] - BUTTON_W) // 2, (WINDOW_SIZE[1] - BUTTON_H) // 2, BUTTON_W, BUTTON_H),
                    label=f"Turno de {self.truque.partida.jugador_por_id(siguiente_jugador)[0].nombre}",
                    on_click=lambda siguiente_jugador = siguiente_jugador: self.app.set_view("juego", siguiente_jugador),
                ))
                return
            
            # Si hay uno solo, pasamos a la pantalla directamente
            else:
                self._pending_view = ("juego", siguiente_jugador)
                return

        # Para los jugadores controlados por la IA, redirigimos las acciones disponibles a la IA
        else:
            self._pending_view = ("juego", siguiente_jugador)
            return

    def _ejecutar(self, nombre, jugador = None, **kwargs):
        self.truque.ejecutar_accion(nombre, jugador, **kwargs)    
        self._construir_botones()

    def handle_event(self, event):
        for btn in self.botones:
            btn.handle_event(event)

    def update(self, dt):
        if self._pending_view is not None:
            view, jugador = self._pending_view
            self._pending_view = None
            self.app.set_view(view, jugador) if jugador is not None else self.app.set_view(view)
            return
        
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.botones:
            btn.update(mouse_pos)

    def draw(self, surface):
        for btn in self.botones:
            btn.draw(surface)