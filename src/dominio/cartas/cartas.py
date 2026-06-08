from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, IntEnum, auto

# Palos de la baraja española
class Palo(Enum): 
    OROS = auto()
    COPAS = auto()
    ESPADAS = auto()
    BASTOS = auto()

    @property
    def path(self) -> str:
        _paths = {
            "OROS": "oros",
            "COPAS": "copas",
            "ESPADAS": "espd",
            "BASTOS": "bast"
        }
        return _paths[self.name]

# Números de la baraja española
class Numero(IntEnum):
    AS = 1
    DOS = 2
    TRES = 3
    CUATRO = 4
    CINCO = 5
    SEIS = 6
    SIETE = 7
    SOTA = 10
    CABALLO = 11
    REY = 12

    @property
    def path(self) -> str:
        _paths = {
            1:  "1",
            2:  "2",
            3:  "3",
            4:  "4",
            5:  "5",
            6:  "6",
            7:  "7",
            10: "sota",
            11: "cab",
            12: "rey",
        }
        return _paths[self.value]

@dataclass(frozen=True, slots=True)
# Frozen (cartas inmutables, no se pueden modificar después de crear)
# Slots (optimización de memoria, no se pueden agregar atributos dinámicamente)
class Carta:
    numero: Numero      
    palo: Palo

    def __str__(self) -> str:
        return f"{self.numero.name.lower()} de {self.palo.name.lower()}"
