
from typing import Optional, Any, Callable

from ...dominio import Partida, Jugador
from .accionesTruque import AccionesTruque
from .serializadorTruque import SerializadorTruque
from .repartoTruque import RepartoTruque

class Truque:

    # El estado completo de juego está almacenado en la partida. 
    # El truque funciona como una fachada que permite gestionar las acciones sobre la partida.
    partida: Partida

    # Todas las acciones están almacenadas en distintos módulos. 
    # Estas acciones se llaman a través del método ejecutar_accion, pero se mapean a través de la variable acciones.
    _acciones: dict[str, Callable[[Partida, Any], Any]] = {
        "iniciar_juego": lambda partida, **kwargs: RepartoTruque.iniciar_juego(partida),
    }

    def __init__(self, nombres: list[str], equipos: Optional[list[bool]] = None) -> None:
        # Creamos todos los jugadores y la partida.
        jugadores = [Jugador(id, nombre, nCartas = 3) for id, nombre in enumerate(nombres)]
        self.partida = Partida(jugadores, equipos)

    def acciones_disponibles(self, jugador_id: int = None) -> list[str]:
        # Lista de acciones disponibles para un jugador específico.
        # Si no se especifica un jugador, las acciones son las que gestionan el juego.
        return [accion for id, accion in AccionesTruque.acciones_disponibles(self.partida) if id == jugador_id]
    
    def estado_juego(self, jugador_id: int = None) -> dict[str, Any]:
        # Devuelve el estado completo del juego, incluyendo la información de:
        # - Partida: puntaje, equipos
        # - Juego: cartas de jugadores, cartas en mesa, apuestas, guía, etc.
        # Se devuele la información disponible para cada jugador indicado.
        # Si no se indica un jugador, se devuelve la información completa del juego.
        return SerializadorTruque.estado_juego(self.partida, jugador_id)
    
    def ejecutar_accion(self, accion: str, jugador: int = None, **kwargs) -> Any:
        if accion not in self.acciones_disponibles(jugador):
            raise ValueError(f"Jugador {jugador} no puede ejecutar la acción {accion} actualmente.")
        accion =  self._acciones[accion](self.partida, **kwargs)
        return {"accion": accion, "estado": self.estado_juego(jugador)}
