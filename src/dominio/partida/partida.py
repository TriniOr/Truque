from typing import Optional

from ..cartas.baraja import Baraja
from .juego import Juego
from ..personas.equipo import Equipo
from ..personas.jugador import Jugador


class Partida:

    # Baraja: baraja española de 40 cartas. 
    # Asumimos que se juega con una sola baraja.
    _baraja: Baraja
    # Equipos: asumimos que es un juego de dos equipos.
    _equipos: list[Equipo]
    # Puntuación: lista con la puntuación de cada equipo.
    _puntuacion: list[int]
    # Juego: Dentro de cada partida se juegan varios juegos. 
    # Asumimos que la partida se compone en varios juegos. 
    #   Para un motor general de cartas, el conteo de la puntuación y la estructura del juego debería estar en la lógica del juego, y no en la estrucutra de las clases reutilizables.
    #   En este caso, reducimos el scope del proyecto a juegos similares a nivel de partida.
    _juego: Juego | None

    def __init__(self, jugadores: list[Jugador], equipos: Optional[list[bool]] = None) -> None:
        
        # Creamos baraja
        self._baraja = Baraja()
        self._baraja.barajar()

        #TODO: Validar número de jugadores y ordenamiento de equipos

        if equipos is None:
            # Si no se especifica el reparto de equipos, se intercalan.
            equipos = [i % 2 == 0 for i in range(len(jugadores))]

        # Creamos equipos (asumimos que el número de jugadores ya se ha validado antes de crear la partida)
        equipo1 = Equipo([jugador for jugador, enEquipo1 in zip(jugadores, equipos) if enEquipo1])
        equipo2 = Equipo([jugador for jugador, enEquipo1 in zip(jugadores, equipos) if not enEquipo1])
        self._equipos = [equipo1, equipo2]

        # Inicializamos la puntuación a 0-0
        self._puntuacion = [0, 0]

    def iniciar_juego(self):
        # Iniciamos un nuevo juego dentro de la partida.
        self._juego = Juego()

    def finalizar_juego(self, puntosPorEquipo: list[int]) -> None:
        # Las normas del juego son las encargadas de asignar la puntuación a cada equipo.
        self._puntuacion = [p + q for p, q in zip(self._puntuacion, puntosPorEquipo)]
        self._juego = None