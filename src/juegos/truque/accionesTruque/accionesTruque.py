from typing import Tuple

from ....dominio import Partida
from ..estadoTruque import EstadoTruque
from .florTruque import FlorTruque

class AccionesTruque:
    # Permite determinar para un estado de partida, que acciones están disponibles.
    # Estas acciones pueden ser utilizadas por las reglas del juego para determinar el flujo de la partida.
    # Además, indica el jugador que puede realizar cada acción,-1 si es para ninguno.
    # Por último se deja un último campo con un diccionario para incluir información adicional sobre la acción, como por ejemplo la apuesta mínima para subir una apuesta.
    
    @staticmethod
    def acciones_disponibles(partida: Partida) -> list[Tuple[str, int, dict | None]]:

        # == Inicio y final de juego ==
        
        # Terminar partida (se ha alcanzado la puntuación máxima)
        if any(p >= 3 for p in partida.puntuacion):
            return [("terminar_partida", -1, None)]

        # Iniciar juego (no hay juego en curso)
        if partida.juego is None:
            return [("iniciar_juego", -1, None)]
        
        # Iniciar ronda (no hay ronda en curso)
        if partida.juego.ronda is None:
            return [("iniciar_ronda", -1, None)]

        # Para terminar una ronda, se ha borrado el estado de la partida, y hay que crear uno nuevo
        if partida.juego.ronda.estado is None:
            return [("terminar_ronda", -1, None)]
        
        # == Acciones durante la ronda ==
        # Comprobar el estado de la partida:
        # siguiente jugador (desde aquí, solo el jugador que tiene el turno puede realizar acciones)
        # apuestas de pares, flor y truque.
        estado: EstadoTruque = partida.juego.ronda.estado 
        apuesta_maxima = 31 - max(partida.juego.puntuacion)

        # Contar puntos: fin de la partida, se han jugado las 3 cartas, no se ha querido la apuesta de truque 
        # o un equipo ha ganado al menos 2 manos.
        if estado.ronda_ganada():
            return [("contar_puntos", -1, None)]
        
        # Terminar juego (se ha alcanzado la puntuación máxima). Lo ponemos aquí abajo para contar puntos antes de terminar el juego!
        if any(p >= 31 for p in partida.juego.puntuacion):
            return [("terminar_juego", -1, None)]

        # Si no hay cartas repartidas, se pueden repartir.
        if all(len(jugador.cartas()) == 0 for jugador in partida.lista_jugadores()):
            return [("repartir_cartas", -1, None)] + (
                [("apostar_pares", jugador.id, {"apuesta": {"min": 2, "max": apuesta_maxima, "default": 2}}) for jugador in partida.lista_jugadores()] 
                if estado.pares is None else [])
        
        # Si uno de los equipos está a 30 puntos(a 1 punto de ganar), se hace ronda al cantar.
        if any(p == 30 for p in partida.juego.puntuacion):
            return [("cantar_puntos", estado.jugador.id, None)]
        
        # Desde aquí en adelante, hay una ronda en curso. 
        # Toda las acciones se van acumulando en la variable accciones.
        acciones: list[Tuple[str, int, dict | None]] = []
        
        # Si hay alguna apuesta abierta, el jugador tiene que responder
        # Fase de pares abierta: se puede querer, rechazar o subir la apuesta.
        if estado.pares is not None and estado.pares.abierta:
            acciones.append(("querer_pares", estado.jugador.id, None))
            acciones.append(("rechazar_pares", estado.jugador.id, None))
            if estado.pares.apuesta < apuesta_maxima:
                acciones.append(("subir_pares", estado.jugador.id, {"apuesta": {"min": estado.pares.apuesta + 1, "max": apuesta_maxima, "default": estado.pares.apuesta + 1}}))

            # Si el jugador tiene flor, puede cantar flor y cancelar la fase de apuesta de pares
            if FlorTruque.es_flor(estado.jugador.cartas(), partida.juego.ronda.guia):
                acciones.append(("cantar_flor", estado.jugador.id, None))
            return acciones
        
        # Fase de cantar flor: se puede cantar (si el jugador tiene flor) o pasar.
        if estado.flor is not None and estado.flor.cantar:
            if FlorTruque.es_flor(estado.jugador.cartas(), partida.juego.ronda.guia):
                acciones.append(("cantar_flor", estado.jugador.id, None))
            acciones.append(("no_cantar_flor", estado.jugador.id, None))
            return acciones
        
        # Fase de flor abierta pero no apostada: se puede apostar flor o pasar.
        if estado.flor is not None and estado.flor.abierta and estado.flor.jugador_apuesta is None:
            acciones.append(("apostar_flor", estado.jugador.id, {"apuesta": {"min": 1, "max": apuesta_maxima//3+1, "default": 1}}))
            acciones.append(("rechazar_flor", estado.jugador.id, None))
            return acciones

        # Fase de flor abierta y apostada: se puede querer, rechazar o subir la apuesta.
        if estado.flor is not None and estado.flor.abierta:
            acciones.append(("querer_flor", estado.jugador.id, None))
            acciones.append(("rechazar_flor", estado.jugador.id, None))
            if estado.flor.apuesta < apuesta_maxima//3+1:
                acciones.append(("subir_flor", estado.jugador.id, {"apuesta": {"min": estado.flor.apuesta//3+1, "max": apuesta_maxima//3+1, "default": estado.flor.apuesta//3+1}}))
            return acciones
        
        # Fase de truque abierta: se puede querer, rechazar o subir la apuesta (retruque y juego fuera).
        if estado.truque is not None and estado.truque.abierta:
            acciones.append(("querer_truque", estado.jugador.id, None))
            acciones.append(("rechazar_truque", estado.jugador.id, None))
            if estado.truque.apuesta < 31:
                acciones.append(("apostar_truque", estado.jugador.id, None))
            return acciones

        # Si el jugador tiene cartas en mano, puede jugar una carta.
        if len(estado.jugador.cartas_en_mano()) > 0:
            acciones.append(("jugar_carta", estado.jugador.id, {"carta": {"disponibles": {i: f"{carta}" for i, carta in estado.jugador.cartas_en_mano().items()}}}))
        
        # Si no se han apostado los pares, el jugador puede apostar pares, pero solo en la primera ronda, y si no se ha apostado ya flor.
        if estado.pares is None and estado.ronda == 1 and estado.flor is None:
            acciones.append(("apostar_pares", estado.jugador.id, {"apuesta": {"min": 2, "max": apuesta_maxima, "default": 2}}))

        # Si no se ha cantado flor, el jugador puede cantar flor si tiene, pero solo en la primera ronda y si no ha apostado pares.
        if estado.flor is None and estado.ronda == 1 and (
            estado.pares is None or estado.pares.jugador_apuesta != estado.jugador
            ) and FlorTruque.es_flor(estado.jugador.cartas(), partida.juego.ronda.guia):
            acciones.append(("cantar_flor", estado.jugador.id, None))

        # Si se han apostado los pares o flor, o ya ha terminado la primera ronda, y el equipo del jugador no ha trucado, puede trucar.
        if (
            estado.truque is None and (
                estado.pares is not None or estado.flor is not None or estado.ronda > 1
                )
            ) or (
                # O si la apuesta está cerrada, pero se puede subir la apuesta (retruco y juego fuera).
                estado.truque and estado.truque.jugador_apuesta.equipo != estado.jugador.equipo and estado.truque.apuesta < 31
                ):
            acciones.append(("apostar_truque", estado.jugador.id, None))

        return acciones