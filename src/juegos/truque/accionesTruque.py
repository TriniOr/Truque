from typing import Tuple

from ...dominio import Partida
from .funcionesTruque import FuncionesTruque

class AccionesTruque:
    # Permite determinar para un estado de partida, que acciones están disponibles.
    # Estas acciones pueden ser utilizadas por las reglas del juego para determinar el flujo de la partida.
    # Además, indica el jugador que puede realizar cada acción, o None si la acción no depende de un jugador específico.
    
    @staticmethod
    def acciones_disponibles(partida: Partida) -> list[Tuple[int | None, str]]:

        # == Inicio y final de juego ==

        # Terminar partida (se ha alcanzado la puntuación máxima)
        if any(p >= 3 for p in partida._puntuacion):
            return [(None, "finalizar_partida")]

        # Iniciar juego (no hay juego en curso)
        if partida.juego is None:
            return [(None, "iniciar_juego")]
        
        # Terminar juego (se ha alcanzado la puntuación máxima)
        if any(p >= 31 for p in partida.juego._puntuacion):
            return [(None, "finalizar_juego")]
        
        # Iniciar ronda (no hay ronda en curso)
        if partida.juego.ronda is None:
            return [(None, "iniciar_ronda")]
        
        # == Acciones durante la ronda ==

        # Si no hay cartas repartidas, se pueden repartir.
        if all(len(getattr(jugador.estado(public=False), "cartas_en_mano", {})) == 0 for jugador in partida.lista_jugadores()):
            return [(None, "repartir_cartas"), (None, "apostar_pares")]
        
        # Desde aquí en adelante, hay una ronda en curso. 
        # Toda las acciones se van acumulando en la variable accciones.
        acciones: list[Tuple[int | None, str]] = []

        # Comprobar el siguiente jugador (desde aquí, solo el jugador que tiene el turno puede realizar acciones)
        siguiente_jugador = partida.siguiente_jugador()

        estado = partida.juego.ronda.estado 
        
        # Si no se han apostado los pares, el jugador puede apostar pares.
        pares = estado.get("pares") if isinstance(estado, dict) else None
        if pares is None:
            acciones.append((siguiente_jugador.id, "apostar_pares"))

        return acciones