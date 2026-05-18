from collections.abc import Iterable
from typing import Final, Optional, Union

from .cartas import Carta

# MANO: cada una de las n cartas que un jugador tiene en su posesión, ya sea en su mano o en la mesa.
class Mano:

    # CARTAS: propiedad interna (se puede acceder a ella mediante alguno de los métodos de vistas)
    # Determina cada una de las cartas. Estas cartas están identificadas por la posición en la lista.
    _cartas: list[Carta]
    # ESTADO DE CARTAS: representan el orden en el que se ha jugado, en caso de que se haya jugado.
    # 0: carta en mano, no se ha jugado
    # n > 0: carta echada en la ronda n
    _estado_de_cartas: list[int]
    # MAX_CARTAS: número máximo de cartas que puede tener un jugador en su mano.
    _max_cartas: Final[int]

    def __init__(self, nCartas: Optional[int] = None) -> None:
        self._cartas = []
        self._estado_de_cartas = []
        self._max_cartas = nCartas if nCartas is not None else 3
        
    def cartas_en_mano(self, public: bool = True) -> dict[int, Union[Carta, None]]:
        # Devolvemos diccionario con todas las cartas en la mano:
        # clave: índice de la carta en la mano
        # valor: carta o none
        # Public: True -> vista de la mesa (devuelve None), False -> vista del jugador (devuelve la carta).
        return {
            indice: carta if not public else None
            for indice, (carta, estado) in enumerate(zip(self._cartas, self._estado_de_cartas))
            if estado == 0
        }

    def cartas_en_mesa(self) -> list[Carta]:
        # Devolvemos lista  todas las cartas en la mesa, ordenadas por el orden que se han echado
        return [
            carta for carta, estado in 
            sorted(
                zip(self._cartas, self._estado_de_cartas),
                key=lambda pair: pair[1] # Ordenamos por el estado de la carta
            )
            if estado > 0
        ]

    def estado(self, public: bool = True) -> dict[str, Union[dict[int, Union[Carta, None]], list[Carta]]]:
        # Devolvemos un diccionario con el estado de la mano de un jugador
        return {
            "cartas_en_mano": self.cartas_en_mano(public = public),
            "cartas_echadas": self.cartas_en_mesa(),
        }

    @property
    def esta_completa(self) -> bool:
        # Chequea si el jugador tiene todas las cartas
        return len(self._cartas) == self._max_cartas

    def recibir(self, cartas: Iterable[Carta]) -> None:
        # El jugador recibe un conjunto de cartas, y se añaden a su mano.
        cartas = list(cartas)
        if len(self._cartas) + len(cartas) > self._max_cartas:
            raise ValueError("No caben tantas cartas en la mano")
        for carta in cartas:
            if not isinstance(carta, Carta): 
                raise TypeError("Solo se pueden recibir objetos Carta")
            self._cartas.append(carta)
            self._estado_de_cartas.append(0)

    def devolver(self) -> list[Carta]:
        # Devolver todas las cartas de la mano, eliminandolas de la mano.
        cartas = self._cartas.copy() 
        self._cartas = []
        self._estado_de_cartas = []
        return cartas
    
    def echar_carta(self, idx: int) -> None:
        # El jugador echa una carta a la mesa (estado de la carta pasa a ser el siguiente número de ronda).
        # Asunciones: la carta se puede echar una sola vez, y solo una por ronda.
        # Esto condiciona las normas de juego para algunos juegos (i.e. echar parejas). -> posible mejora: echar carta = lista de índices.
        if idx < 0 or idx >= len(self._cartas):
            raise IndexError("Índice de carta no válido")
        if self._estado_de_cartas[idx] > 0:
            raise ValueError("La carta ya ha sido echada")
        self._estado_de_cartas[idx] = max(self._estado_de_cartas) + 1