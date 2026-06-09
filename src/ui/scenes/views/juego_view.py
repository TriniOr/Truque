from src.juegos.truque.truque import Truque
from src.ui.components.carta import CartaUI
from src.ui.scenes.views.base_view import BaseView
from src.ui.components.button import Button
from src.ui.components.mesa_cartas import MesaCartas
from src.ui.components.number_selector import NumberSelector
from src.ui.style import * 

POSICIONES_MESA = [(50, 50), (50, 20), (90, 35), (10, 35), (75, 50), (80, 20), (20, 20), (25, 50), (65, 20), (35, 20)]
POSICIONES_JUGADORES = {
    2: [1, 2],
    4: [1, 3, 2, 4],
    6: [1, 5, 6, 2, 7, 8],
    8: [1, 5, 3, 6, 2, 7, 4, 8],
    10: [1, 5, 3, 6, 9, 2, 10, 7, 4, 8]
}

class JuegoView(BaseView):
    def __init__(self, app, truque: Truque, jugador_actual = -1):
        self.app = app
        self.truque:Truque = truque
        self.jugador_actual = jugador_actual
        self.estado = self.truque.estado_juego(self.jugador_actual)["partida"]
        self.acciones = self.truque.acciones_disponibles()
        self.accion_respuesta = {}
        self._construir_botones()
        
    
    def _construir_botones(self):
        self.fase = "ganada" if (len([accion for accion in self.acciones if accion[0] == "contar_puntos" and accion[1] == -1]) > 0
                ) else "recuento" if (len([accion for accion in self.acciones if accion[0] == "terminar_ronda" and accion[1] == -1]) > 0
                ) else "pares" if (len(self.estado["apuestas"]["pares"]) > 0 and self.estado["apuestas"]["pares"]["estado"] == "abierta"
                ) else "cante_flor" if (len(self.estado["apuestas"]["flor"]) > 0 and self.estado["apuestas"]["flor"]["estado"] == "cantando"
                ) else "flor" if (len(self.estado["apuestas"]["flor"]) > 0 and self.estado["apuestas"]["flor"]["estado"] == "abierta"
                ) else "truque" if (len(self.estado["apuestas"]["truque"]) > 0 and self.estado["apuestas"]["truque"]["estado"] == "abierta"
                ) else "juego" 
        
        self.guia = CartaUI(
            carta=self.estado["mesa"]["guía"],
            pos=(0.9*WINDOW_SIZE[0], 0.7*WINDOW_SIZE[1]), 
            size = "lg"
        )
        jugador = self.estado["jugadores"][self.jugador_actual]
        cartas_en_mano = jugador["cartas_en_mano"]

        if self.fase != "recuento":
            self.cartas_mano = [
                CartaUI(
                    carta = carta,
                    pos = ((0.42 + 0.08*idx)*WINDOW_SIZE[0], 0.7*WINDOW_SIZE[1]), 
                    size = "lg",
                    hover_color=CARD_HOVER if self.fase == "juego" else None,
                    on_click= lambda idx = idx: self._ejecutar("jugar_carta", 
                                    jugador=self.jugador_actual, 
                                    carta = idx) if self.fase == "juego" else None,
                    )
                for idx, carta in cartas_en_mano.items() if carta is not None
            ]
        else:
            self.cartas_mano = []

        jugadores = self.estado["jugadores"]
        jugador_actual_idx = next(idx for idx, jugador in enumerate(jugadores.values()) if jugador['id'] == self.jugador_actual)
        jugadores_ordenados = list(jugadores.values())
        jugadores_ordenados = jugadores_ordenados[jugador_actual_idx:] + jugadores_ordenados[:jugador_actual_idx]
        posiciones = [POSICIONES_MESA[x-1] for x in POSICIONES_JUGADORES[len(jugadores_ordenados)]]

        
        if self.fase != "recuento":
            self.cartas_mesa = [
                MesaCartas(
                    cartas=jugador["cartas_echadas"],
                    pos = (posiciones[idx][0]*WINDOW_SIZE[0]/100 - 50, posiciones[idx][1]*WINDOW_SIZE[1]/100 - 50),
                    nombre = jugador["name"],
                    font_color=COLOR_EQUIPO1 if jugador["equipo"] == 1 else COLOR_EQUIPO2,
                    seleccionadas = [i for i,x in enumerate(self.estado["mesa"]["reos"]) if x!=0 and x.id == jugador["id"]] if self.estado else [],
                    mano = jugador['id'] == self.estado["jugador_mano"].id,
                    comentario = self.estado["apuestas"]["comentarios"].get(jugador['id'], None) if self.estado["apuestas"] else None,
                    flor = self.fase in ["flor", "cante_flor"] and jugador["id"] in self.estado["apuestas"]["flor"]["jugadores"])
                for idx, jugador in enumerate(jugadores_ordenados)
            ]
        else:
            self.cartas_mesa = [
                MesaCartas(
                    cartas=jugador.cartas() ,
                    pos = (posiciones[idx][0]*WINDOW_SIZE[0]/100 - 50, posiciones[idx][1]*WINDOW_SIZE[1]/100 - 50),
                    nombre = jugador.nombre,
                    font_color=COLOR_EQUIPO1 if jugador.equipo == 1 else COLOR_EQUIPO2,
                    mano = jugador.id == self.estado["jugador_mano"].id)
                for idx, jugador in enumerate(self.truque.partida.lista_jugadores())
            ]


        if self.fase == "pares":
            self._construir_botones_pares()
        elif self.fase == "cante_flor":
            self._construir_botones_cante_flor()
        elif self.fase == "flor":
            self._construir_botones_flor()
        elif self.fase == "truque":
            self._construir_botones_truque()
        elif self.fase == "juego":
            self._construir_botones_juego()
        elif self.fase == "ganada":
            self._construir_ganada()
        elif self.fase == "recuento":
            self._construir_recuento()

    def _construir_botones_juego(self):
        self.botones = {}
        apuesta_pares = [accion for accion in self.acciones if accion[0] == "apostar_pares" and accion[1] == self.jugador_actual]
        if len(apuesta_pares) > 0:
            apuesta_pares = apuesta_pares[0]
            self.botones["selector_pares"] = NumberSelector(
                pos=(350, 0.7*WINDOW_SIZE[1]),
                label="Apuesta",
                min_val=apuesta_pares[2]["apuesta"]["min"],
                max_val=apuesta_pares[2]["apuesta"]["max"],
                initial=apuesta_pares[2]["apuesta"]["default"],
                on_change=None,
            )

            self.botones["la_falta"] = Button(
                rect = (530, 0.7*WINDOW_SIZE[1], 150, BUTTON_H),
                label="La Falta",
                on_click=lambda: self.la_falta(self.botones["selector_pares"]),
                color = COLOR_PRIMARY if len(apuesta_pares) > 0 else COLOR_FORBIDDEN
                )
        
        self.botones["apostar_pares"] = Button(
            rect = (20, 0.7*WINDOW_SIZE[1], 300, BUTTON_H),
            label="Envidar",
            on_click=lambda: self._ejecutar("apostar_pares", self.jugador_actual, apuesta = self.botones["selector_pares"].value
                                            ) if len(apuesta_pares) > 0 else None,
            color = COLOR_PRIMARY if len(apuesta_pares) > 0 else COLOR_FORBIDDEN
            )
        
        cante_flor = [accion for accion in self.acciones if accion[0] == "cantar_flor" and accion[1] == self.jugador_actual]
        self.botones["cantar_flor"] = Button(
            rect = (20, 0.7*WINDOW_SIZE[1]+1*(PADDING+BUTTON_H), 300, BUTTON_H),
            label="Cantar Flor",
            on_click=lambda: self._ejecutar("cantar_flor", self.jugador_actual
                                            ) if len(cante_flor) > 0 else None,
            color = COLOR_PRIMARY if len(cante_flor) > 0 else COLOR_FORBIDDEN
            )
        
        cante_truque = [accion for accion in self.acciones if accion[0] == "apostar_truque" and accion[1] == self.jugador_actual]
        self.botones["apostar_truque"] = Button(
            rect = (20, 0.7*WINDOW_SIZE[1]+2*(PADDING+BUTTON_H), 300, BUTTON_H),
            label=(
                "Retruco" if self.estado["apuestas"]["truque"]["apuesta"] == 3 else
                "Juego Fuera"
            ) if len(self.estado["apuestas"]["truque"]) > 0 else "Trucar",
            on_click=lambda: self._ejecutar("apostar_truque", self.jugador_actual
                                            ) if len(cante_truque) > 0 else None,
            color = COLOR_PRIMARY if len(cante_truque) > 0 else COLOR_FORBIDDEN
            )

    def _construir_botones_pares(self):
        self.botones = {}
        subida_pares = [accion for accion in self.acciones if accion[0] == "subir_pares" and accion[1] == self.jugador_actual]
        if len(subida_pares) > 0:
            subida_pares = subida_pares[0]
            self.botones["selector_subida_pares"] = NumberSelector(
                pos=(350, 0.7*WINDOW_SIZE[1]),
                label="Subir",
                min_val=subida_pares[2]["apuesta"]["min"],
                max_val=subida_pares[2]["apuesta"]["max"],
                initial=subida_pares[2]["apuesta"]["default"],
                on_change=None,
            )

            self.botones["la_falta"] = Button(
                rect = (530, 0.7*WINDOW_SIZE[1], 150, BUTTON_H),
                label="La Falta",
                on_click=lambda: self.la_falta(self.botones["selector_subida_pares"]),
                color = COLOR_PRIMARY if len(subida_pares) > 0 else COLOR_FORBIDDEN
                )
        
        self.botones["subir_pares"] = Button(
            rect = (20, 0.7*WINDOW_SIZE[1], 300, BUTTON_H),
            label="Subir",
            on_click=lambda: self._ejecutar("subir_pares", self.jugador_actual, apuesta = self.botones["selector_subida_pares"].value
                                            ) if len(subida_pares) > 0 else None,
            color = COLOR_PRIMARY if len(subida_pares) > 0 else COLOR_FORBIDDEN
            )
        
        querer_pares = [accion for accion in self.acciones if accion[0] == "querer_pares" and accion[1] == self.jugador_actual]
        self.botones["querer_pares"] = Button(
            rect = (20, 0.7*WINDOW_SIZE[1]+1*(PADDING+BUTTON_H), 300, BUTTON_H),
            label="Querer Pares",
            on_click=lambda: self._ejecutar("querer_pares", self.jugador_actual
                                            ) if len(querer_pares) > 0 else None,
            color = COLOR_PRIMARY if len(querer_pares) > 0 else COLOR_FORBIDDEN
            )
        
        rechazar_pares = [accion for accion in self.acciones if accion[0] == "rechazar_pares" and accion[1] == self.jugador_actual]
        self.botones["rechazar_pares"] = Button(
            rect = (20, 0.7*WINDOW_SIZE[1]+2*(PADDING+BUTTON_H), 300, BUTTON_H),
            label="No Querer",
            on_click=lambda: self._ejecutar("rechazar_pares", self.jugador_actual
                                            ) if len(rechazar_pares) > 0 else None,
            color = COLOR_PRIMARY if len(rechazar_pares) > 0 else COLOR_FORBIDDEN
            )
        
        cante_flor = [accion for accion in self.acciones if accion[0] == "cantar_flor" and accion[1] == self.jugador_actual]
        self.botones["cantar_flor"] = Button(
            rect = (20, 0.7*WINDOW_SIZE[1]+3*(PADDING+BUTTON_H), 300, BUTTON_H),
            label="Cantar Flor",
            on_click=lambda: self._ejecutar("cantar_flor", self.jugador_actual
                                            ) if len(cante_flor) > 0 else None,
            color = COLOR_PRIMARY if len(cante_flor) > 0 else COLOR_FORBIDDEN
            )

    def _construir_botones_cante_flor(self):
        self.botones = {}
        cante_flor = [accion for accion in self.acciones if accion[0] == "cantar_flor" and accion[1] == self.jugador_actual]
        self.botones["cantar_flor"] = Button(
            rect = (20, 0.7*WINDOW_SIZE[1]+0*(PADDING+BUTTON_H), 300, BUTTON_H),
            label="Cantar Flor",
            on_click=lambda: self._ejecutar("cantar_flor", self.jugador_actual
                                            ) if len(cante_flor) > 0 else None,
            color = COLOR_PRIMARY if len(cante_flor) > 0 else COLOR_FORBIDDEN
            )
        
        pasar_flor = [accion for accion in self.acciones if accion[0] == "no_cantar_flor" and accion[1] == self.jugador_actual]
        self.botones["pasar_flor"] = Button(
            rect = (20, 0.7*WINDOW_SIZE[1]+1*(PADDING+BUTTON_H), 300, BUTTON_H),
            label="Pasar",
            on_click=lambda: self._ejecutar("no_cantar_flor", self.jugador_actual
                                            ) if len(pasar_flor) > 0 else None,
            color = COLOR_PRIMARY if len(pasar_flor) > 0 else COLOR_FORBIDDEN
            )

    def _construir_botones_flor(self):
        self.botones = {}
        apostar_flor = [accion for accion in self.acciones if accion[0] == "apostar_flor" and accion[1] == self.jugador_actual]
        if len(apostar_flor) > 0:
            apostar_flor = apostar_flor[0]
            self.botones["selector_flor"] = NumberSelector(
                pos=(350, 0.7*WINDOW_SIZE[1]),
                label="Subir",
                min_val=apostar_flor[2]["apuesta"]["min"],
                max_val=apostar_flor[2]["apuesta"]["max"],
                initial=apostar_flor[2]["apuesta"]["default"],
                on_change=None,
            )

            self.botones["la_falta"] = Button(
                rect = (530, 0.7*WINDOW_SIZE[1], 150, BUTTON_H),
                label="La Falta",
                on_click=lambda: self.la_falta(self.botones["selector_flor"]),
                color = COLOR_PRIMARY if len(apostar_flor) > 0 else COLOR_FORBIDDEN
                )
        
            self.botones["apostar_flor"] = Button(
                rect = (20, 0.7*WINDOW_SIZE[1], 300, BUTTON_H),
                label="Apostar Flor",
                on_click=lambda: self._ejecutar("apostar_flor", self.jugador_actual, apuesta = self.botones["selector_flor"].value
                                                ) if len(apostar_flor) > 0 else None,
                color = COLOR_PRIMARY if len(apostar_flor) > 0 else COLOR_FORBIDDEN
                )
            
        subir_flor = [accion for accion in self.acciones if accion[0] == "subir_flor" and accion[1] == self.jugador_actual]
        if len(subir_flor) > 0:
            subir_flor = subir_flor[0]
            self.botones["selector_flor"] = NumberSelector(
                pos=(350, 0.7*WINDOW_SIZE[1]),
                label="Subir",
                min_val=subir_flor[2]["apuesta"]["min"],
                max_val=subir_flor[2]["apuesta"]["max"],
                initial=subir_flor[2]["apuesta"]["default"],
                on_change=None,
            )

            self.botones["la_falta"] = Button(
                rect = (530, 0.7*WINDOW_SIZE[1], 150, BUTTON_H),
                label="La Falta",
                on_click=lambda: self.la_falta(self.botones["selector_flor"]),
                color = COLOR_PRIMARY if len(subir_flor) > 0 else COLOR_FORBIDDEN
                )
        
            self.botones["subir_flor"] = Button(
                rect = (20, 0.7*WINDOW_SIZE[1], 300, BUTTON_H),
                label="Subir Flor",
                on_click=lambda: self._ejecutar("subir_flor", self.jugador_actual, apuesta = self.botones["selector_flor"].value
                                                ) if len(subir_flor) > 0 else None,
                color = COLOR_PRIMARY if len(subir_flor) > 0 else COLOR_FORBIDDEN
                )
        
        pasar_flor = [accion for accion in self.acciones if accion[0] == "rechazar_flor" and accion[1] == self.jugador_actual]
        self.botones["pasar_flor"] = Button(
            rect = (20, 0.7*WINDOW_SIZE[1]+1*(PADDING+BUTTON_H), 300, BUTTON_H),
            label="Pasar" if len(apostar_flor) > 0 else "No Querer",
            on_click=lambda: self._ejecutar("rechazar_flor", self.jugador_actual
                                            ) if len(pasar_flor) > 0 else None,
            color = COLOR_PRIMARY if len(pasar_flor) > 0 else COLOR_FORBIDDEN
            )
            
        querer_flor = [accion for accion in self.acciones if accion[0] == "querer_flor" and accion[1] == self.jugador_actual]
        if len(querer_flor) > 0:
            self.botones["querer_flor"] = Button(
                rect = (20, 0.7*WINDOW_SIZE[1]+2*(PADDING+BUTTON_H), 300, BUTTON_H),
                label="Querer",
                on_click=lambda: self._ejecutar("querer_flor", self.jugador_actual
                                                ) if len(querer_flor) > 0 else None,
                color = COLOR_PRIMARY if len(querer_flor) > 0 else COLOR_FORBIDDEN
                )

    def _construir_botones_truque(self):
        self.botones = {}
        apostar_truque = [accion for accion in self.acciones if accion[0] == "apostar_truque" and accion[1] == self.jugador_actual]
        self.botones["apostar_truque"] = Button(
            rect = (20, 0.7*WINDOW_SIZE[1]+0*(PADDING+BUTTON_H), 300, BUTTON_H),
            label=(
                "Retruco" if self.estado["apuestas"]["truque"]["apuesta"] == 3 else
                "Juego Fuera"
            ) if len(self.estado["apuestas"]["truque"]) > 0 else "Trucar",
            on_click=lambda: self._ejecutar("apostar_truque", self.jugador_actual
                                            ) if len(apostar_truque) > 0 else None,
            color = COLOR_PRIMARY if len(apostar_truque) > 0 else COLOR_FORBIDDEN
            )
            
        querer_truque = [accion for accion in self.acciones if accion[0] == "querer_truque" and accion[1] == self.jugador_actual]
        if len(querer_truque) > 0:
            self.botones["querer_truque"] = Button(
                rect = (20, 0.7*WINDOW_SIZE[1]+1*(PADDING+BUTTON_H), 300, BUTTON_H),
                label="Querer",
                on_click=lambda: self._ejecutar("querer_truque", self.jugador_actual
                                                ) if len(querer_truque) > 0 else None,
                color = COLOR_PRIMARY if len(querer_truque) > 0 else COLOR_FORBIDDEN
                )
            
        rechazar_truque = [accion for accion in self.acciones if accion[0] == "rechazar_truque" and accion[1] == self.jugador_actual]
        if len(rechazar_truque) > 0:
            self.botones["rechazar_truque"] = Button(
                rect = (20, 0.7*WINDOW_SIZE[1]+2*(PADDING+BUTTON_H), 300, BUTTON_H),
                label="No Querer",
                on_click=lambda: self._ejecutar("rechazar_truque", self.jugador_actual
                                                ) if len(rechazar_truque) > 0 else None,
                color = COLOR_PRIMARY if len(rechazar_truque) > 0 else COLOR_FORBIDDEN
                )
            
    def _construir_ganada(self):
        self.botones = {}
        self.botones["contar_puntos"] = Button(
            rect = (20, 0.7*WINDOW_SIZE[1]+0*(PADDING+BUTTON_H), 300, BUTTON_H),
            label="Contar Puntos",
            on_click=lambda: self._ejecutar("contar_puntos", -1)
            )   
            
    def _construir_recuento(self):
        self.botones = {}
        self.botones["terminar_ronda"] = Button(
            rect = (20, 0.7*WINDOW_SIZE[1]+0*(PADDING+BUTTON_H), 300, BUTTON_H),
            label="Siguiente Ronda",
            on_click=lambda: self._ejecutar("terminar_ronda", -1)
            )      
        
    def la_falta(self, boton):
        boton.value = boton.max_val

    def _ejecutar(self, nombre, jugador = None, **kwargs):
        self.accion_respuesta = self.truque.ejecutar_accion(nombre, jugador, **kwargs) 
        
        self.estado = self.truque.estado_juego(self.jugador_actual)["partida"]
        self.acciones = self.truque.acciones_disponibles()

        terminar_ronda = [accion for accion in self.acciones if accion[0] in ["repartir_cartas", "terminar_juego"] and accion[1] == -1]
        if len(terminar_ronda) > 0:
            print(self.acciones)
            self.app.set_view("config")
            return

        siguiente_jugador = self.truque.estado_juego()["partida"]["siguiente_jugador"]  
        if self.jugador_actual == siguiente_jugador or self.fase == "ganada":
            self._construir_botones()
        elif siguiente_jugador == -1:
            self.app.set_view("config")
        else:
            self.app.set_view("juego", siguiente_jugador)
            

    def handle_event(self, event): 
        for carta in self.cartas_mano:
            carta.handle_event(event)
        for botones in self.botones.values():
            botones.handle_event(event)

    def update(self, dt): 
        mouse_pos = pygame.mouse.get_pos()
        for carta in self.cartas_mano:
            carta.update(mouse_pos)
        for botones in self.botones.values():
            botones.update(mouse_pos)

    def draw(self, surface): 
        self.draw_label(surface, "Guía", 
                        pos=(0.9*WINDOW_SIZE[0] + 40, 0.7*WINDOW_SIZE[1]-50))
        self.guia.draw(surface)
        for carta in self.cartas_mano:
            carta.draw(surface)
        for mesa in self.cartas_mesa:
            mesa.draw(surface)
        for botones in self.botones.values():
            botones.draw(surface)
            
        if self.fase == "recuento" and self.accion_respuesta["accion"]["apuestas"]:
            print(self.accion_respuesta)
            if "pares" in self.accion_respuesta["accion"]["apuestas"].keys():
                self.draw_label(surface, 
                    "Puntos de pares:", 
                    pos=(0.3*WINDOW_SIZE[0], 0.7*WINDOW_SIZE[1]))  
                self.draw_label(surface, 
                    f"{self.accion_respuesta["accion"]["apuestas"]["pares"]["puntos"]}",
                    pos=(0.3*WINDOW_SIZE[0] + 265,  0.7*WINDOW_SIZE[1]),
                    color=COLOR_EQUIPO1 if self.accion_respuesta["accion"]["apuestas"]["pares"]["equipo"] == 1 else COLOR_EQUIPO2)  
                reservadas = self.accion_respuesta["accion"]["apuestas"]["pares"]["puntos_reservadas"]
                if reservadas > 0:
                    self.draw_label(surface, 
                    f"+ {reservadas//3} reservada{"s" if reservadas > 3 else " "}: {reservadas}",
                    pos=(0.3*WINDOW_SIZE[0] + 40,  0.7*WINDOW_SIZE[1] + 40),
                    color=COLOR_EQUIPO1 if self.accion_respuesta["accion"]["apuestas"]["pares"]["equipo"] == 1 else COLOR_EQUIPO2)
                    
            if "flor" in self.accion_respuesta["accion"]["apuestas"].keys():
                self.draw_label(surface, 
                    "Puntos de flor:", 
                    pos=(0.3*WINDOW_SIZE[0], 0.7*WINDOW_SIZE[1]))  
                self.draw_label(surface, 
                    f"{self.accion_respuesta["accion"]["apuestas"]["flor"]["puntos"]}",
                    pos=(0.3*WINDOW_SIZE[0] + 240,  0.7*WINDOW_SIZE[1]),
                    color=COLOR_EQUIPO1 if self.accion_respuesta["accion"]["apuestas"]["flor"]["equipo"] == 1 else COLOR_EQUIPO2)  
                puntos_flores = self.accion_respuesta["accion"]["apuestas"]["flor"]["puntos_flores"]
                if puntos_flores > 0:
                    self.draw_label(surface, 
                    f"+ {puntos_flores//3} flor{"es" if puntos_flores > 3 else ""}:       {puntos_flores}",
                    pos=(0.3*WINDOW_SIZE[0] + 40,  0.7*WINDOW_SIZE[1] + 40),
                    color=COLOR_EQUIPO1 if self.accion_respuesta["accion"]["apuestas"]["flor"]["equipo"] == 1 else COLOR_EQUIPO2)
                    
            if "truque" in self.accion_respuesta["accion"]["apuestas"].keys():
                self.draw_label(surface, 
                    "Puntos de truque:", 
                    pos=(0.3*WINDOW_SIZE[0], 0.7*WINDOW_SIZE[1] + 100))  
                self.draw_label(surface, 
                    f"{self.accion_respuesta["accion"]["apuestas"]["truque"]["puntos"]}",
                    pos=(0.3*WINDOW_SIZE[0] + 275,  0.7*WINDOW_SIZE[1] + 100),
                    color=COLOR_EQUIPO1 if self.accion_respuesta["accion"]["apuestas"]["truque"]["equipo"] == 1 else COLOR_EQUIPO2) 
                
        