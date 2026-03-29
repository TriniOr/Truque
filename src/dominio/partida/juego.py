from .ronda import Ronda

class Juego:

    # Puntuación: lista con la puntuación de cada equipo.
    _puntuacion: list[int]

    # Ronda: cada partida se compone de rondas
    _ronda: Ronda | None = None

    def __init__(self) -> None:
        # Inicializamos la puntuación a 0-0
        self._puntuacion = [0, 0]

    def iniciar_ronda(self):
        # Iniciamos un nueva ronda dentro del juego.
        self._ronda = Ronda()

    def finalizar_ronda(self, puntosPorEquipo: list[int]) -> None:
        # Las normas del juego son las encargadas de asignar la puntuación a cada equipo.
        # En este caso, podría extraerse la variable ronda.puntuacion, pero para hacerlo general, son las normas las que gestionan la puntuación.
        self._puntuacion = [p + q for p, q in zip(self._puntuacion, puntosPorEquipo)]
        self._ronda = None