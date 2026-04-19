from .jugador import Jugador

class Equipo:

    # NPersonas: Número de integrantes del equipo.
    jugadores: list[Jugador]

    def __init__(self, jugadores: list[Jugador]) -> None:
        self.jugadores = jugadores

    def __iter__(self):
        # Permite iterar sobre los jugadores del equipo.
        return iter(self.jugadores)