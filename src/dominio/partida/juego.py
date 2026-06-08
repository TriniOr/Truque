from src.dominio.personas.jugador import Jugador

from .ronda import Ronda

class Juego:

    # Puntuación: lista con la puntuación de cada equipo.
    puntuacion: list[int]

    # Ronda: cada partida se compone de rondas
    ronda: Ronda | None = None

    def __init__(self) -> None:
        # Inicializamos la puntuación a 0-0
        self.puntuacion = [0, 0]

    def iniciar_ronda(self, mano: Jugador = None):
        # Iniciamos un nueva ronda dentro del juego.
        self.ronda = Ronda(mano)

    def finalizar_ronda(self, puntosPorEquipo: list[int]) -> None:
        # Las normas del juego son las encargadas de asignar la puntuación a cada equipo.
        # En este caso, podría extraerse la variable ronda.puntuacion, pero para hacerlo general, son las normas las que gestionan la puntuación.
        self.puntuacion = [p + q for p, q in zip(self.puntuacion, puntosPorEquipo)]
        self.ronda = None

    # Numero de puntos que faltan al mejor equipo para ganar el juego.
    def la_falta(self) -> int:
        return 31 - max(self.puntuacion)