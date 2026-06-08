from typing import Optional

from src.dominio.personas.jugador import Jugador

from ..cartas.cartas import Carta

class Ronda:
    # Ronda: cada juego se compone de rondas

    # Estado: cada regla de juegos puede determinar el estado de cada ronda.
    estado: Optional[any] = None
    # Guía: carta sobre la mesa que establece la guía.
    guia: Optional[Carta] = None

    mano: Optional[Jugador] = None

    def __init__(self, jugador: Jugador = None):
        # Iniciamos una nueva ronda dentro del juego.
        self.mano = jugador

    def poner_guia(self, carta: Carta):
        # Método para poner la guía sobre la mesa.
        self.guia = carta

    def devolver_guia(self) -> Carta:
        # Método para devolver la guía a la mano del jugador.
        guia = self.guia
        self.guia = None
        return guia



