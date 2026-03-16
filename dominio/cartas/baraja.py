from __future__ import annotations
from typing import Iterable
from .cartas import Carta, Numero, Palo
from random import shuffle

class Baraja:
    _cartas: list[Carta]

    def __init__(self) -> None:

        # Generamos las 40 cartas: 10 numeros y 4 palos
        self._cartas = [
            Carta(numero, palo)
            for palo in Palo
            for numero in Numero
        ]

    # Para evitar que se modifique la lista de cartas desde fuera, devolvemos una tupla que es solo de lectura
    @property
    def cartas(self) -> tuple[Carta, ...]:
        return tuple(self._cartas)

    # Número de cartas que quedan en la baraja
    @property
    def tamaño(self) -> int:
        return len(self._cartas)
    
    # Usamos la función shuffle del paquete random para mezclar la lista de cartas
    def barajar(self) -> None:
        shuffle(self._cartas)

    # Método para robar n cartas de la baraja.
    def robar(self, n: int = 1) -> list[Carta]:

        # No se pueden robar un número negativo de cartas, ni más cartas de las que quedan en la baraja
        if n < 0:
            raise ValueError("n debe ser no negativo")
        if n > len(self._cartas):
            raise ValueError("No hay suficientes cartas en la baraja")
        
        robadas = self._cartas[:n]

        # Eliminamos de la baraja las cartas que se han robado
        del self._cartas[:n]

        # Devolvemos las cartas robadas
        return robadas
    
    # Método para devolver n cartas a la baraja.
    def devolver(self, cartas: Iterable[Carta]) -> None:
        for carta in cartas:

            # Comporbamos que se devuleven solo cartas, y que no están ya en la baraja (repetidas)
            if not isinstance(carta, Carta):
                raise TypeError(f"Solo se pueden devolver objetos Carta, no {type(carta).__name__}")
            if carta in self._cartas:
                raise ValueError(f"La carta {carta} ya está en la baraja")
            self._cartas.append(carta)

    # Lista de todas las cartas de la baraja (sin importar el orden)
    @staticmethod
    def _todas_las_cartas() -> set[Carta]:
        return {Carta(numero, palo) for palo in Palo for numero in Numero}

    # Comprueba que la baraja tiene todas las cartas (sin importar el orden) y no tiene cartas repetidas
    @property
    def esta_completa(self) -> bool:

        # Conjunto de todas las cartas (sin repetidos) de la baraja. Si hay repetidos, el conjunto se hace más pequeño.
        cartas_baraja = set(self._cartas)
        if len(cartas_baraja) != len(self._cartas):
            return False

        # Comprobamos que el conjunto de cartas de la baraja es igual al conjunto de todas las cartas posibles
        return set(self._cartas) == self._todas_las_cartas()