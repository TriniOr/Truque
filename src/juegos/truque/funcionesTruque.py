    
from src.dominio import Partida, Jugador


class FuncionesTruque:
     
    @staticmethod
    def siguiente_jugador(partida: Partida) -> Jugador:
        # Ver cual es el siguiente jugador en jugar, segun el orden de los equipos y el número de jugadores.
        jugadores = partida.lista_jugadores()
        if partida.juego is None:
            # Si no hay juego en curso, en la ronda i empieza el jugador i (ciclicamente)
            puntuación = sum(partida._puntuacion)
            return jugadores[puntuación % len(jugadores)]
        elif partida.juego.ronda is None or partida.juego.ronda.jugadorActual is None:
            # Si no hay ronda en curso, empieza el jugador j en la ronda j (ciclicamente)
            puntuación = sum(partida.juego._puntuacion)
            return jugadores[puntuación % len(jugadores)]
        else:   
            # Si hay ronda en curso, el jugador actual es el que tiene el turno.
            return jugadores[partida.juego.ronda.jugadorActual]