from ....dominio import Partida
from ..estadoTruque import EstadoTruque
from ..puntosTruque import PuntosTruque

class JuegoTruque: 
    # Clase que representa una partida de Truque. Contiene los métodos necesarios para gestionar el estado de la partida, y las acciones que pueden realizar los jugadores.

    @staticmethod
    def jugar_carta(partida: Partida, jugador_id: int, carta: int) -> dict[str, any]:
        estado: EstadoTruque = partida.juego.ronda.estado

        # Obtenemos la lista de jugadores, y extraemos sus ids para poder buscar por id o índice..
        jugadores = partida.lista_jugadores()
        jugador, idx = partida.jugador_por_id(jugador_id)

        # Método para jugar una carta.
        jugador.echar_carta(carta)
        
        # Chequeamos las cartas echadas en esta ronda.
        cartas_echadas = [jugador.carta_echada_en_ronda(estado.ronda) for jugador in jugadores]

        # Si ha habido pata, vemos las cartas echadas como si fueran ronda 2
        if estado.ronda == 3 and estado.reos[0] == 0:
            cartas_echadas = [jugador.carta_echada_en_ronda(2) for jugador in jugadores]


        # Si todos los jugadores han echado una carta, se resuelve la ronda
        if all(carta is not None for carta in cartas_echadas):

            # Calculamos el jugador que gana la ronda, y actualizamos el estado de la ronda.
            # Para ello buscamos el jugador que es mano (gana en caso de empate).
            jugador_mano = partida.juego.ronda.mano
            mano_index = jugadores.index(jugador_mano)
            mejores_cartas_index, mejores_cartas = PuntosTruque.mejor_carta(cartas_echadas, partida.juego.ronda.guia, mano_index)
            pata = False

            # PATA: Si hay varios mejores jugadores, y estamos en la primera ronda, pasamos directamente a la tercera ronda y empieza el jugador mano
            if len(mejores_cartas_index) > 1:
                if estado.ronda == 1:
                    mejor_jugador = jugador_mano
                    pata = True
                else:
                    # Si no, el mejor jugador es el que tiene la mejor carta. En caso de empate es el jugador del equipo que haya ganado la primera mano
                    jugador_ganador_reo1, idx = partida.jugador_por_id(estado.reos[0].id)
                    equipo_gandaor_reo1 = partida.equipos[jugador_ganador_reo1.equipo-1].jugadores
                    mejores_cartas_equipo_reo1 = [index for index in mejores_cartas_index if jugadores[index].id in equipo_gandaor_reo1]
                    mejor_jugador = jugadores[mejores_cartas_equipo_reo1[0]] if len(mejores_cartas_equipo_reo1) > 0 else jugadores[mejores_cartas_index[0]]
            else:
                mejor_jugador = jugadores[mejores_cartas_index[0]]
            (mejor_jugador.nombre, mejores_cartas)
            estado.siguiente_ronda(mejor_jugador, nueva_ronda=True, pata = pata)
        else:

            # Si no han echado todos los jugadores, el siguiente jugador es el siguiente al que ha jugado.
            siguiente_jugador = jugadores[(idx + 1) % len(jugadores)]
            estado.siguiente_ronda(siguiente_jugador)

        return {
            "accion": "jugar_carta",
            "jugador": jugador.id,
            "carta": f"{jugador.cartas_echadas()[-1]}"
        }
    
    @staticmethod
    def apostar_truque(partida: Partida, jugador_id: int) -> dict[str, any]:
        estado: EstadoTruque = partida.juego.ronda.estado

        # Obtenemos la lista de jugadores, y extraemos sus ids para poder buscar por id o índice..
        jugadores = partida.lista_jugadores()
        jugador, idx = partida.jugador_por_id(jugador_id)

        # Comprobamos que la apuesta no está ya ne juego fuera (en ese caso no se puede subir más)
        if estado.truque is not None and estado.truque.apuesta == 31:
            raise ValueError("No se puede trucar cuando ya se ha echado juego fuera.")
        
        # Comprobamos que si ya hay un truque o retruque, lo ha hecho un jugador del otro equipo
        if estado.truque is not None and estado.truque.jugador_apuesta.equipo == jugador.equipo:
            raise ValueError("La última apuesta de truque ya la ha hecho este equipo.")

        # Obtenemos la lista de jugadores, y extraemos sus ids para poder buscar por id o índice..
        jugador, idx = partida.jugador_por_id(jugador_id)

        # Si la apuesta no se ha iniciado, el jugador inicia el truque
        if estado.truque is None:
            estado.trucar(jugador)

        # Si ya se ha iniciado, se sube la apuesta
        else:
            estado.truque.subir_apuesta(jugador)

        estado.siguiente_jugador(jugadores[(idx + 1) % len(jugadores)])
        apuesta = estado.truque.apuesta
        return {
            "accion": "apostar_truque",
            "jugador": jugador_id,
            "apuesta": "truco" if apuesta == 3 else "retruco" if apuesta == 6 else "juego_fuera"
        }
    
    @staticmethod
    def querer_truque(partida: Partida, jugador_id: int) -> dict[str, any]:
        estado: EstadoTruque = partida.juego.ronda.estado

        # Comprobamos que la fasae de truque está abierta
        if estado.truque is None or not estado.truque.abierta:
            raise ValueError("No se puede querer una apuesta de truque fuera de fase de apuesta.")

        # El jugador quiere la apuesta de truque, y se finaliza la apuesta
        estado.truque.querer_apuesta()
        estado.finalizar_apuesta()

        return {
            "accion": "querer_truque",
            "jugador": jugador_id,
            "estado": "querida", 
            "apuesta": estado.truque.apuesta
        }
    
    @staticmethod
    def rechazar_truque(partida: Partida, jugador_id: int) -> dict[str, any]:
        estado: EstadoTruque = partida.juego.ronda.estado

        # Comprobamos que la fasae de truque está abierta
        if estado.truque is None or not estado.truque.abierta:
            raise ValueError("No se puede querer una apuesta de truque fuera de fase de apuesta.")

        # Obtenemos la lista de jugadores, y extraemos sus ids para poder buscar por id o índice..
        jugadores = partida.lista_jugadores()
        jugador, idx = partida.jugador_por_id(jugador_id)
        jugador_apuesta = estado.truque.jugador_apuesta
        jugador_apuesta_idx = jugadores.index(jugador_apuesta)

        # Si no se quiere pasa directamente el turno al siguiente jugador del equipo.
        # Calculamos el siguiente jugador que tiene que responder la apuesta, que es dos jugadores despues del jugador actual.
        siguiente_jugador_idx = (idx + 2) % len(jugadores)

        # Si todos los jugadores del equipo han rechazado la apuesta, se cierra como no querido.
        # Para comprobar, chequeamos que el siguiente jugador que tiene que respnder la apuesta no es el primero que ha respondido:
        # siguente jugador != jugador_apuesta + 1 modulo número de jugadores.
        if siguiente_jugador_idx == (jugador_apuesta_idx + 1) % len(jugadores):
            estado.truque.rechazar_apuesta()
            estado.finalizar_apuesta()
            return {
                    "accion": "finalizado_truque",
                    "jugador": jugador_id,
                    "estado": "ganada",
                    "equipo_ganador": estado.truque.jugador_apuesta.equipo,
                    "apuesta": estado.truque.apuesta
            }

        else:
            estado.siguiente_jugador(jugadores[siguiente_jugador_idx])
            return {
                "accion": "rechazar_truque",
                "jugador": jugador_id
            }
    