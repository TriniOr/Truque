from typing import Optional, Union

from ..cartas.cartas import Carta
from ..cartas.mano import Mano

class Jugador:

    _mano: Mano
    _nombre: str
    _id: int
    _equipo: int = None

    def __init__(self, id: int, nombre: str, nCartas: Optional[int] = None) -> None:
        self._mano = Mano(nCartas)
        self._nombre = nombre
        self._id = id

    # Nombre (solo lectura)
    @property
    def nombre(self) -> str:
        return self._nombre

    # ID (solo lectura)
    @property
    def id(self) -> int:
        return self._id

    # Equipo (solo lectura)
    @property
    def equipo(self) -> int:
        return self._equipo
    
    def asignar_equipo(self, equipo: int) -> None:
        self._equipo = equipo

    # Las clases del jugador hacen de intermediarias entre la mano y el exterior.
    def cartas_en_mano(self, public: bool = False) -> dict[int, Optional[Carta]]:
        return {i : carta if carta else None for i, carta in self._mano.cartas_en_mano(public = public).items()}
    
    def cartas_echadas(self) -> list[Carta]:
        return [carta if carta else None for carta in self._mano.cartas_en_mesa()]
    
    def carta_echada_en_ronda(self, ronda: int) -> Optional[Carta]:
        cartas = self._mano.cartas_en_mesa() 
        return cartas[ronda - 1] if 1 <= ronda <= len(cartas) else None

    def estado(self, public: bool = False) -> dict[str, any]:
        return {
            "name": self._nombre,
            "id": self._id,
            "equipo": self._equipo,
            "cartas_en_mano": {i: carta if carta else None for i, carta in self.cartas_en_mano(public = public).items()},
            "cartas_echadas": [carta for carta in self.cartas_echadas()],
        }
    
    def cartas(self) -> list[Carta]:
        return self._mano._cartas
    
    def n_cartas_echadas(self) -> int:
        return len(self.cartas_echadas())
    
    # Método para recibir cartas, que delega en la mano.
    def recibir_cartas(self, cartas: list[Carta]) -> None:
        self._mano.recibir(cartas)

    # Método para devolver cartas, que delega en la mano.
    def devolver_cartas(self) -> list[Carta]:
        return self._mano.devolver()
    
    # Método para echar una carta a la mesa, que delega en la mano.
    def echar_carta(self, idx: int) -> None:
        self._mano.echar_carta(idx)

    