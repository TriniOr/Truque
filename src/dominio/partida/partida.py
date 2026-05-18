from typing import Any, Optional

from ..cartas.baraja import Baraja
from .juego import Juego
from ..personas.equipo import Equipo
from ..personas.jugador import Jugador


class Partida:

    # Baraja: baraja española de 40 cartas. 
    # Asumimos que se juega con una sola baraja.
    baraja: Baraja
    # Equipos: asumimos que es un juego de dos equipos.
    equipos: list[Equipo]
    # Puntuación: lista con la puntuación de cada equipo.
    _puntuacion: list[int]
    # Juego: Dentro de cada partida se juegan varios juegos. 
    # Asumimos que la partida se compone en varios juegos. 
    #   Para un motor general de cartas, el conteo de la puntuación y la estructura del juego debería estar en la lógica del juego, y no en la estrucutra de las clases reutilizables.
    #   En este caso, reducimos el scope del proyecto a juegos similares a nivel de partida.
    juego: Juego | None = None

    def __init__(self, jugadores: list[Jugador], equipos: Optional[list[bool]] = None) -> None:
        
        # Creamos baraja
        self.baraja = Baraja()
        self.baraja.barajar()

        if len(jugadores) % 2 != 0:
            raise ValueError("Tiene que haber un número par de jugadores.")
        
        if equipos is not None and len(equipos) != len(jugadores):
            raise ValueError("La lista de equipos tiene que tener un elemento por jugador.")
        
        if equipos is not None and sum(equipos) != len(jugadores) // 2:
            raise ValueError("Tiene que haber el mismo número de jugadores en cada equipo.")

        if equipos is None:
            # Si no se especifica el reparto de equipos, se intercalan.
            equipos = [i % 2 == 0 for i in range(len(jugadores))]

        # Creamos equipos (asumimos que el número de jugadores ya se ha validado antes de crear la partida)
        equipo1 = Equipo([jugador for jugador, enEquipo1 in zip(jugadores, equipos) if enEquipo1])
        equipo2 = Equipo([jugador for jugador, enEquipo1 in zip(jugadores, equipos) if not enEquipo1])
        self.equipos = [equipo1, equipo2]

        # Inicializamos la puntuación a 0-0
        self._puntuacion = [0, 0]

    def iniciar_juego(self):
        # Iniciamos un nuevo juego dentro de la partida.
        self.juego = Juego()

    def finalizar_juego(self, puntosPorEquipo: list[int]) -> None:
        # Las normas del juego son las encargadas de asignar la puntuación a cada equipo.
        self._puntuacion = [p + q for p, q in zip(self._puntuacion, puntosPorEquipo)]
        self.juego = None

    def lista_jugadores(self) -> list[Jugador]:
        # Devolvemos la lista de jugadores de la partida.
        return [jugador for equipos in zip(self.equipos[0], self.equipos[1]) for jugador in equipos]


        
