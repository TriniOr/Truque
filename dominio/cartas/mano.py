from collections.abc import Iterable
from typing import Final

from .cartas import Carta

class Mano:
    _cartas: list[Carta]
    _estado_de_cartas: list[int]
    _max_cartas: Final[int] = 3 #todo una función para definir las normas, y definir número de cartas y puntuación.
    _round = 1

    def __init__(self) -> None:
        self._cartas = []
        self._estado_de_cartas = []
        
    @property
    def cartas_en_mano(self) -> dict[int, Carta]:
        return {
            i: c
            for i, (c, e) in enumerate(zip(self._cartas, self._estado_de_cartas))
            if e == 0
        }

    @property
    def cartas_en_mesa(self) -> list[dict[str, object]]:
        return [
            {"ronda": e, "carta": c}
            for c, e in sorted(
                zip(self._cartas, self._estado_de_cartas),
                key=lambda ce: ce[1]
            )
            if e > 0
        ]

    def estado(self) -> dict:
        return {
            "cartas_en_mano": self.cartas_en_mano,
            "cartas_echadas": self.cartas_en_mesa,
        }

    @property
    def esta_completa(self) -> bool:
        return len(self._cartas) == self._max_cartas

    def recibir(self, cartas: Iterable[Carta]) -> None:
        cartas = list(cartas)
        if len(self._cartas) + len(cartas) > self._max_cartas:
            raise ValueError("No caben tantas cartas en la mano")
        for carta in cartas:
            if not isinstance(carta, Carta):
                raise TypeError("Solo se pueden recibir objetos Carta")
            self._cartas.append(carta)
        self._estado_de_cartas.extend([0] * len(cartas))
        self._round = 1

    def devolver(self) -> list[Carta]:
        cartas = self._cartas.copy() 
        self._cartas = []
        return cartas
    
    def echar_carta(self, idx: int) -> None:
        if idx < 0 or idx >= len(self._cartas):
            raise IndexError("Índice de carta no válido")
        if self._estado_de_cartas[idx] > 0:
            raise ValueError("La carta ya ha sido echada")
        self._estado_de_cartas[idx] = self._round
        self._round += 1