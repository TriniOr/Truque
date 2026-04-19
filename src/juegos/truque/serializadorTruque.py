from ...dominio import Partida

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
                    "juegos": partida.juego._puntuacion if partida.juego else [0, 0],
                    "ronda": (partida.juego.ronda if partida.juego.ronda else [0.0]) if partida.juego else [0,0],
                },
                "equipos": {
                    "equipo_1": [jugador.estado(public = jugador.id == jugador_id) for jugador in partida.equipos[0]],
                    "equipo_2": [jugador.estado(public = jugador.id == jugador_id) for jugador in partida.equipos[1]],
                },
                "mesa": {
                    "guía": ((f"{partida.juego.ronda.guia}" if partida.juego.ronda.guia else None)
                              if partida.juego.ronda else None) if partida.juego else None,
                }, 
                "apuestas": (partida.juego.ronda.estado 
                              if partida.juego.ronda else None) if partida.juego else None,
            }
        }


