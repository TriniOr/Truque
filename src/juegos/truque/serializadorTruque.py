from ...dominio import Partida
from .estadoTruque import EstadoTruque

class SerializadorTruque:
    # Extrae el contenido del estado de la partida almacenado en el objeto Partida, y sus correspondinetes hijos.
    # Formatea la salida para que coincida con el formato deseado del contrato.

    @staticmethod
    def apuestas(partida: Partida) -> dict[str, any]:

        if partida.juego is None or partida.juego.ronda is None or partida.juego.ronda.estado is None:
            return {}
        estado: EstadoTruque = partida.juego.ronda.estado
        if not isinstance(estado, EstadoTruque):
            raise ValueError("Error el estado de la partida.")
        comentarios: dict[int, str] = {}

        truque: dict[str, any] = {}
        if estado.truque is not None:
            truque["apuesta"] = estado.truque.apuesta
            if estado.truque.abierta:
                truque["estado"] = "abierta"
                truque["jugador"] = estado.truque.jugador_apuesta.id
                truque["equipo"] = estado.truque.jugador_apuesta.equipo
                comentarios[estado.truque.jugador_apuesta.id] = (
                    "Truco" if estado.truque.apuesta == 3 else
                    "Retruco" if estado.truque.apuesta == 6 else
                    "Juego Fuera")

            elif estado.truque.querida:
                truque["estado"] = "querida"
            else:
                truque["estado"] = "ganada"
                truque["jugador"] = estado.truque.jugador_apuesta.id
                truque["equipo"] = estado.truque.jugador_apuesta.equipo
                
        pares: dict[str, any] = {}
        if estado.pares is not None:
            if estado.pares.abierta:
                pares["estado"] = "abierta"
                pares["apuesta"] = estado.pares.apuesta
                pares["jugador"] = estado.pares.jugador_ultima_apuesta.id
                pares["equipo"] = estado.pares.jugador_ultima_apuesta.equipo
                comentarios[estado.pares.jugador_ultima_apuesta.id] = f"Envido {estado.pares.apuesta}" if estado.pares.apuesta < partida.juego.la_falta() else "La Falta"
            elif estado.pares.querida:
                pares["estado"] = "querida"
                pares["apuesta"] = estado.pares.apuesta_cerrada
            else:
                pares["estado"] = "ganada"
                pares["apuesta"] = estado.pares.apuesta_cerrada
                pares["jugador"] = estado.pares.jugador_ultima_apuesta.id
                pares["equipo"] = estado.pares.jugador_ultima_apuesta.equipo
                
        flor: dict[str, any] = {}
        if estado.flor is not None:
            if estado.flor.cantar:
                flor["estado"] = "cantando"
                flor["jugadores"] = estado.flor.jugadores
                for equipo in estado.flor.jugadores:
                    for jugador in equipo:
                        comentarios[jugador] = f"Tengo Flor"
            else:
                if estado.flor.abierta:
                    flor["estado"] = "abierta"
                    flor["apuesta"] = estado.flor.apuesta
                    flor["jugadores"] = [jugador for equipo in estado.flor.jugadores for jugador in equipo]
                    if estado.flor.jugador_apuesta is not None:
                        flor["jugador"] = estado.flor.jugador_apuesta.id
                        flor["equipo"] = estado.flor.jugador_apuesta.equipo
                        comentarios[estado.flor.jugador_apuesta.id] = f"{estado.flor.apuesta // 3} Flor" + ("es" if estado.flor.apuesta > 3 else "")
                elif estado.flor.querida:
                    flor["estado"] = "querida"
                    flor["apuesta"] = estado.flor.apuesta_cerrada 
                else:
                    flor["estado"] = "ganada"
                    flor["apuesta"] = estado.flor.apuesta_cerrada 
                    if estado.flor.jugador_apuesta is not None:
                        flor["jugador"] = estado.flor.jugador_apuesta.id
                        flor["equipo"] = estado.flor.jugador_apuesta.equipo

        return {
            "truque": truque,
            "flor": flor,
            "pares": pares,
            "comentarios": comentarios
        }


    @staticmethod
    def estado_juego(partida: Partida, jugador_id: int = None) -> dict[str, any]:
        # Devuelve el estado de la partida en formato diccionario
        # Si se aporta el id de un jugador, se expone todas las propiedades visibles por el jugador.
        # Si no, se devuelve el estado completo de la partida.
        estado_ronda: EstadoTruque = partida.juego.ronda.estado if partida.juego and partida.juego.ronda else None

        return {
            "partida": {
                "puntuación": {
                    "partidas": partida.puntuacion,
                    "juegos": partida.juego.puntuacion if partida.juego else [0, 0]
                },
                "jugadores": {
                    jugador.id: jugador.estado(public = jugador.id != jugador_id) for jugador in partida.lista_jugadores()
                },
                "siguiente_jugador": estado_ronda.jugador.id if estado_ronda and estado_ronda.jugador else 
                        EstadoTruque.siguiente_mano(partida).id,
                "jugador_mano": partida.juego.ronda.mano.id if partida.juego and partida.juego.ronda and partida.juego.ronda.mano else {},
                "mesa": {
                    "guía": partida.juego.ronda.guia if partida.juego and partida.juego.ronda and partida.juego.ronda.guia else {},
                    "bazas": estado_ronda.bazas if estado_ronda else {}
                }, 
                "apuestas": SerializadorTruque.apuestas(partida),
        }}


