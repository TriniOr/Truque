from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, IntEnum

# Palos de la baraja española
class Palo(str, Enum): 
    OROS = "oros"
    COPAS = "copas"
    ESPADAS = "espadas"
    BASTOS = "bastos"

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

@dataclass(frozen=True, slots=True)
# Frozen (cartas inmutables, no se pueden modificar después de crear)
# Slots (optimización de memoria, no se pueden agregar atributos dinámicamente)

class Carta:
    numero: Numero      
    palo: Palo

    def __str__(self) -> str:
        return f"{self.numero.name.lower()} de {self.palo.value}"
