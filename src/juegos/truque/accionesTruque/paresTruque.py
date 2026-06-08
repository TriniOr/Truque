from ....dominio import Partida, Carta, Jugador
from ..estadoTruque import EstadoTruque

class ParesTruque:
    # Clase que implementa todas las acciones relativas a las 
    # apuestas y contabilización de puntos de pares
        
    @staticmethod
    def es_reservada(cartas: list[Carta], guia: Carta) -> bool:
        # Método que determina si las cartas de una mano es reservada

        # Validación de cartas de imput
        if len(cartas) != 3 or not all(isinstance(carta, Carta) for carta in cartas):
            return ValueError(f"Las cartas {cartas} no corresponden una mano válida de truque.")
        
        if not isinstance(guia, Carta):
            return ValueError(f"La carta {guia} no es una carta guía válida.")
        
        # Extraemos el palo de cada carta, definiendo como guía las cartas correspondientes: 
        # 0 = guia, 1 = oros, 2 = copas, 3 = espadas, 4 = bastos 
        palos = [0 if (                                                                 # es guía si:
            (carta.numero.value == 1 and carta.palo.value in [1, 2]) or                 # as de oros o as de copas
            (carta.palo.value == guia.palo.value and (                                  # es del palo de la guía y:
                carta.numero.value not in [4,6,7] or                                    #   6 o 7 del palo de la guía no es guía
                carta.numero.value == 4 and guia.numero.value not in [6,7]              #   es un cuatro (sustituye la guía) pero la guía es 6 o 7
            ))) else carta.palo.value for carta in cartas]                              # si no, toma el valor original de su palo
        
        # Es reservada si: dos o tres cartas de la guía
        # comprobamos que como mucho hay una carta que no es guía
        return len([palo for palo in palos if palo > 0]) < 2    

    @staticmethod
    def puntuacion_pares(cartas: list[Carta], guia: Carta) -> bool:
        # Método que determina los puntos de pares
        
        # Extraemos el palo de cada carta, definiendo como guía las cartas correspondientes: 
        # 0 = guia, 1-4 = no guía, 5 = 4 de la guía
        palos = [5 if carta.palo.value == guia.palo.value and carta.numero.value == 4 and guia.numero.value not in [6,7] else
            0 if (                                                                      # es guía si:
            (carta.numero.value == 1 and carta.palo.value in [1, 2]) or                 # as de oros o as de copas
            (carta.palo.value == guia.palo.value and carta.numero.value not in [4,6,7]  # 6 o 7 del palo de la guía no es guía
            )) else carta.palo.value for carta in cartas]                               # si no, toma el valor original de su palo
        
        # Sustituimos el 4 de la guía si existe por la guía
        cartas_puntos = cartas.copy()
        if 5 in palos:
            cartas_puntos[palos.index(5)] = guia
            palos = [0 if palo == 5 else palo for palo in palos] # Volvemos a poner el 4 como guía
        
        # Para calcular los puntos de pares, calculamos la puntuación de cada carta para cada palo
        # A cada carta le asignamos su puntuación correspondient
        return max(
            sum(
                (25 if carta.numero.value == 3 else                             # 3 de guía
                24 if carta.numero.value == 2 else                              # 2 de guía
                23 if carta.numero.value == 5 else                              # 5 de guía
                22 if carta.numero.value == 1 and carta.palo.value == 2 else    # 1 de copas
                21 if carta.numero.value == 1 and carta.palo.value == 1 else    # 1 de oros
                20 if carta.numero.value == 1 else                              # 1 de guía
                19 if carta.numero.value == 12 else                             # 12 de guía
                18 if carta.numero.value == 11 else                             # 11 de guía
                17 if carta.numero.value == 10 else                             # 10 de guía
                0) if palo_carta == 0 else (
                10 + carta.numero.value if carta.numero.value < 10 else         # cada carta vale 10 + su valor si es del palo       
                10) if palo_carta == palo_pares else (                          # excepto figuras del palo que valen 10
                0) for carta, palo_carta in zip(cartas_puntos, palos))          # las cartas que no son de guía o de otro palo, no cuentan para pares
            for palo_pares in [1,2,3,4])       

    @staticmethod
    def apostar_pares(partida: Partida, jugador_id: int, apuesta: int) -> dict[str, any]:
        estado: EstadoTruque = partida.juego.ronda.estado

        # Valor predeterminado de apuesta a pares y comprobación de que la apuesta es válida.
        if estado.pares is not None:
            raise ValueError("No se puede apostar pares cuando ya hay una apuesta activa.")
        
        la_falta = partida.juego.la_falta()
        if apuesta is None:
            apuesta = 2
        elif apuesta > la_falta:
            raise ValueError(f"La apuesta de pares debe ser como mucho la falta ({la_falta})")
        elif apuesta < 2:
            raise ValueError(f"La apuesta de pares mínima es 2 puntos.")

        # Obtenemos la lista de jugadores, y extraemos sus ids para poder buscar por id o índice..
        jugadores = partida.lista_jugadores()
        jugador, idx = partida.jugador_por_id(jugador_id)
        
        # Iniciamos una apuesta de pares
        estado.iniciar_pares(jugador, apuesta)

        # El siguiente jugador es el siguiente al que ha apostado (que va a ser de otro equipo).
        estado.siguiente_jugador(jugadores[(idx + 1) % len(jugadores)])

        return {
            "accion": "apostar_pares",
            "jugador": jugador_id,
            "apuesta": apuesta
        }
    
    @staticmethod
    def querer_pares(partida: Partida, jugador_id: int) -> dict[str, any]:
        estado: EstadoTruque = partida.juego.ronda.estado

        # Comprobamos que la fasae de apuestas está abierta
        if estado.pares is None or not estado.pares.abierta:
            raise ValueError("No se puede querer una apuesta de pares fuera de fase de apuesta.")

        # El jugador quiere la apuesta de pares, y se finaliza la apuesta (eliminar la información de la apuesta abierta)
        estado.pares.querer_apuesta()
        estado.finalizar_apuesta()

        return {
            "accion": "querer_pares",
            "jugador": jugador_id,
            "estado": "querida", 
            "apuesta": estado.pares.apuesta_cerrada
        }
    
    @staticmethod
    def rechazar_pares(partida: Partida, jugador_id: int) -> dict[str, any]:
        estado: EstadoTruque = partida.juego.ronda.estado
        
        # Comprobamos que la fasae de apuestas está abierta
        if estado.pares is None or not estado.pares.abierta:
            raise ValueError("No se puede rechazar una apuesta de pares fuera de fase de apuesta.")

        # Obtenemos la lista de jugadores, y extraemos sus ids para poder buscar por id o índice..
        jugadores = partida.lista_jugadores()
        jugador, idx = partida.jugador_por_id(jugador_id)
        jugador_apuesta = estado.pares.jugador_ultima_apuesta
        jugador_apuesta_idx = jugadores.index(jugador_apuesta)

        # Si no se quiere pasa directamente el turno al siguiente jugador del equipo.
        # Calculamos el siguiente jugador que tiene que responder la apuesta, que es dos jugadores despues del jugador actual.
        siguiente_jugador_idx = (idx + 2) % len(jugadores)

        # Si todos los jugadores del equipo han rechazado la apuesta, se cierra como no querido.
        # Para comprobar, chequeamos que el siguiente jugador que tiene que respnder la apuesta no es el primero que ha respondido:
        # siguente jugador != jugador_apuesta + 1 modulo número de jugadores.
        if siguiente_jugador_idx == (jugador_apuesta_idx + 1) % len(jugadores):
            estado.pares.rechazar_apuesta()
            estado.finalizar_apuesta()
            return {
                    "accion": "finalizados_pares",
                    "jugador": jugador_id,
                    "estado": "ganada",
                    "equipo_ganador": estado.pares.jugador_ultima_apuesta.equipo, 
                    "apuesta": estado.pares.apuesta_cerrada
            }

        else:
            estado.siguiente_jugador(jugadores[siguiente_jugador_idx])
            return {
                "accion": "rechazar_pares",
                "jugador": jugador_id
            }
    
    @staticmethod
    def subir_pares(partida: Partida, jugador_id: int, apuesta: int) -> dict[str, any]:
        estado: EstadoTruque = partida.juego.ronda.estado

        # Valor predeterminado de apuesta a pares y comprobación de que la apuesta es válida (mayor que la apuesta actual).
        ultima_apuesta = estado.pares.apuesta
        la_falta = partida.juego.la_falta()
        if ultima_apuesta >= la_falta:
            raise ValueError(f"No se puede subir la apuesta de pares, ya se ha alcanzado la falta ({la_falta}).")
        if apuesta is None:
            apuesta = ultima_apuesta + 1 if estado.pares is not None else 2
        if apuesta <= ultima_apuesta:
            raise ValueError(f"La apuesta de pares debe ser mayor que la apuesta actual ({ultima_apuesta}).")
        elif apuesta > la_falta:
            raise ValueError(f"La apuesta de pares debe ser como mucho la falta ({la_falta})")
        elif apuesta < 2:
            raise ValueError(f"La apuesta de pares mínima es 2 puntos.")

        # Obtenemos la lista de jugadores, y extraemos sus ids para poder buscar por id o índice..
        jugadores = partida.lista_jugadores()
        jugador, jugador_idx = partida.jugador_por_id(jugador_id)

        # Subimos los pares y actualizamos al siguiente jugador a apostar
        estado.pares.subir_apuesta(jugador, apuesta)
        estado.siguiente_jugador(jugadores[(jugador_idx + 1) % len(jugadores)])

        return {
            "accion": "subir_pares",
            "jugador": jugador_id,
            "apuesta": apuesta
        }