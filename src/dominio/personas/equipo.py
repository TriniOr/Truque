from .jugador import Jugador

class Equipo:

    # NPersonas: Número de integrantes del equipo.
    jugadores: list[Jugador]

    def __init__(self, jugadores: list[Jugador], id: int) -> None:
        self.id = id
        self.jugadores = jugadores
        [jugador.asignar_equipo(self.id) for jugador in self.jugadores]

    def __iter__(self):
        # Permite iterar sobre los jugadores del equipo.
        return iter(self.jugadores)