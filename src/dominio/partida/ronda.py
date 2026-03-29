from typing import Optional

from ..cartas.cartas import Carta


class Ronda:
    # Ronda: cada juego se compone de rondas

    # Estado: cada regla de juegos puede determinar el estado de cada ronda.
    estado: Optional[any] = None
    # Guía: carta sobre la mesa que establece la guía.
    guia: Optional[Carta] = None

    ronda: Optional[int] = None

    jugadorActual: Optional[int] = None

    def nueva_ronda(self):
        # Iniciamos una nueva ronda dentro del juego.
        self.estado = None
        self.guia = None
        self.ronda = None
        self.jugadorActual = None

    def poner_guia(self, carta: Carta):
        # Método para poner la guía sobre la mesa.
        self.guía = carta

    def devolver_guia(self) -> Carta:
        # Método para devolver la guía a la mano del jugador.
        guia = self.guia
        self.guia = None
        return guia

    def actualizar_estado(self, estado: any) -> None:
        # Método para actualizar el estado de la ronda.
        self.estado = estado

    def actualizar_ronda(self, ronda: int) -> None:
        # Método para iniciar una nueva ronda dentro del juego.
        self.ronda = ronda

    def actualizar_jugador_actual(self, jugadorActual: int) -> None:
        # Método para actualizar el jugador actual.
        self.jugadorActual = jugadorActual