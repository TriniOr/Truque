from .jugador import Jugador

class Equipo:

    # NPersonas: Número de integrantes del equipo.
    _jugadores: list[Jugador]

    def __init__(self, jugadores: list[Jugador]) -> None:
        if len(jugadores) % 2 != 0:
            raise ValueError("Tiene que haber dos equipos con el mismo número de jugadores")
        self._jugadores = jugadores

