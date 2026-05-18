from ...dominio import Partida
from .funcionesTruque import FuncionesTruque

class SerializadorTruque:
    # Extrae el contenido del estado de la partida almacenado en el objeto Partida, y sus correspondinetes hijos.
    # Formatea la salida para que coincida con el formato deseado del contrato.

    @staticmethod
    def estado_juego(partida: Partida, jugador_id: int = None) -> dict[str, any]:
        # Devuelve el estado de la partida en formato diccionario
        # Si se aporta el id de un jugador, se expone todas las propiedades visibles por el jugador.
        # Si no, se devuelve el estado completo de la partida.

        return {
            "partida": {
                "puntuación": {
                    "partidas": partida._puntuacion,
                    "juegos": partida.juego._puntuacion if partida.juego else [0, 0]
                },
                "equipos": {
                    "equipo_1": [jugador.estado(public = jugador.id == jugador_id) for jugador in partida.equipos[0]],
                    "equipo_2": [jugador.estado(public = jugador.id == jugador_id) for jugador in partida.equipos[1]],
                },
                "siguiente_jugador": FuncionesTruque.siguiente_jugador(partida).id if partida.juego and partida.juego.ronda else None,
                "mesa": {
                    "guía": f"{partida.juego.ronda.guia}" if partida.juego and partida.juego.ronda and partida.juego.ronda.guia else {},
                }, 
                "apuestas": f"{partida.juego.ronda.estado}" if partida.juego and partida.juego.ronda and partida.juego.ronda.estado else {},
        }}


