
from typing import Optional, Any, Callable, Tuple

from ...dominio import Partida, Jugador
from .serializadorTruque import SerializadorTruque
from .accionesTruque.accionesTruque import AccionesTruque
from .accionesTruque.juegoTruque import JuegoTruque
from .accionesTruque.paresTruque import ParesTruque
from .accionesTruque.florTruque import FlorTruque
from .accionesTruque.repartoTruque import RepartoTruque

class Truque:

    # El estado completo de juego está almacenado en la partida. 
    # El truque funciona como una fachada que permite gestionar las acciones sobre la partida.
    partida: Partida

    # Todas las acciones están almacenadas en distintos módulos. 
    # Estas acciones se llaman a través del método ejecutar_accion, pero se mapean a través de la variable acciones.
    _acciones: dict[str, Callable[[Partida, Any], Any]] = {
        "iniciar_juego": lambda partida, jugador, **kwargs: RepartoTruque.iniciar_juego(partida),
        "iniciar_ronda": lambda partida, jugador, **kwargs: RepartoTruque.iniciar_ronda(partida),
        "repartir_cartas": lambda partida, jugador, **kwargs: RepartoTruque.repartir_cartas(partida),
        "terminar_ronda": lambda partida, jugador, **kwargs: RepartoTruque.terminar_ronda(partida),
        "terminar_juego": lambda partida, jugador, **kwargs: RepartoTruque.terminar_juego(partida),
        "contar_puntos": lambda partida, jugador, **kwargs: RepartoTruque.contar_puntos(partida),
        "jugar_carta": lambda partida, jugador, **kwargs: JuegoTruque.jugar_carta(partida, jugador, kwargs.get("carta", None)),
        "apostar_truque": lambda partida, jugador, **kwargs: JuegoTruque.apostar_truque(partida, jugador),
        "querer_truque": lambda partida, jugador, **kwargs: JuegoTruque.querer_truque(partida, jugador),
        "rechazar_truque": lambda partida, jugador, **kwargs: JuegoTruque.rechazar_truque(partida, jugador),
        "apostar_pares": lambda partida, jugador, **kwargs: ParesTruque.apostar_pares(partida, jugador, kwargs.get("apuesta", None)),
        "querer_pares": lambda partida, jugador, **kwargs: ParesTruque.querer_pares(partida, jugador),
        "rechazar_pares": lambda partida, jugador, **kwargs: ParesTruque.rechazar_pares(partida, jugador),
        "subir_pares": lambda partida, jugador, **kwargs: ParesTruque.subir_pares(partida, jugador, kwargs.get("apuesta", None)),
        "cantar_flor": lambda partida, jugador, **kwargs: FlorTruque.cantar_flor(partida, jugador),
        "no_cantar_flor": lambda partida, jugador, **kwargs: FlorTruque.no_cantar_flor(partida, jugador),
        "apostar_flor": lambda partida, jugador, **kwargs: FlorTruque.apostar_flor(partida, jugador, kwargs.get("apuesta", None)),
        "rechazar_flor": lambda partida, jugador, **kwargs: FlorTruque.rechazar_flor(partida, jugador),
        "querer_flor": lambda partida, jugador, **kwargs: FlorTruque.querer_flor(partida, jugador),
        "subir_flor": lambda partida, jugador, **kwargs: FlorTruque.subir_flor(partida, jugador, kwargs.get("apuesta", None)),
    }

    def __init__(self, nombres: list[str], equipos: Optional[list[bool]] = None) -> None:
        # Creamos todos los jugadores y la partida.
        jugadores = [Jugador(id, nombre, nCartas = 3) for id, nombre in enumerate(nombres)]
        self.partida = Partida(jugadores, equipos)

    def acciones_disponibles(self, jugador_id: int = None) -> list[Tuple[str, int, dict | None]]:
        # Lista de acciones disponibles para un jugador específico.
        # Si no se especifica un jugador, las acciones son las que gestionan el juego.
        if jugador_id is None:
            return [(accion, id, info) for accion, id, info in AccionesTruque.acciones_disponibles(self.partida)]
        else:
            return [(accion, id, info) for accion, id, info in AccionesTruque.acciones_disponibles(self.partida) if id == jugador_id]

    def estado_juego(self, jugador_id: int = None) -> dict[str, Any]:
        # Devuelve el estado completo del juego, incluyendo la información de:
        # - Partida: puntaje, equipos
        # - Juego: cartas de jugadores, cartas en mesa, apuestas, guía, etc.
        # Se devuele la información disponible para cada jugador indicado.
        # Si no se indica un jugador, se devuelve la información completa del juego.
        return SerializadorTruque.estado_juego(self.partida, jugador_id)
    
    def ejecutar_accion(self, accion: str, jugador: int = None, **kwargs) -> Any:
        if accion not in [accion for accion, _, _ in self.acciones_disponibles(jugador)]:
            raise ValueError(f"Jugador {jugador} no puede ejecutar la acción {accion} actualmente.")
        accion =  self._acciones[accion](self.partida, jugador=jugador, **kwargs)
        return {"accion": accion, "estado": self.estado_juego(jugador)}
