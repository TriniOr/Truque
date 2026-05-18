from typing import Optional, Union

from ..cartas.cartas import Carta
from ..cartas.mano import Mano

class Jugador:

    _mano: Mano
    _nombre: str
    _id: int

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
    
    # Las clases del jugador hacen de intermediarias entre la mano y el exterior.
    def estado(self, public: bool = False) -> dict[str, any]:
        cartas_en_mano = {i : f"{carta if carta else None}" for i, carta in self._mano.cartas_en_mano(public = public).items()}
        cartas_echadas = {f"{carta if carta else None}" for carta in self._mano.cartas_en_mesa()}
        return {
            "name": self._nombre,
            "id": self._id,
            "cartas_en_mano": cartas_en_mano,
            "cartas_echadas": cartas_echadas,
        }
    
    def cartas(self, public: bool = False) -> dict[str, Union[dict[int, Union[Carta, None]], list[Carta], str]]:
        return self._mano.estado(public = public)
    
    # Método para recibir cartas, que delega en la mano.
    def recibir_cartas(self, cartas: list[Carta]) -> None:
        self._mano.recibir(cartas)

    # Método para devolver cartas, que delega en la mano.
    def devolver_cartas(self) -> list[Carta]:
        return self._mano.devolver()
    
    # Método para echar una carta a la mesa, que delega en la mano.
    def echar_carta(self, idx: int) -> None:
        self._mano.echar_carta(idx)

    