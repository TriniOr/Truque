from ....dominio import Partida, Carta, Jugador
from ..estadoTruque import EstadoTruque
from .paresTruque import ParesTruque

class FlorTruque:
    # Clase que implementa todas las acciones relativas a las 
    # apuestas y contabilización de puntos de flor

    @staticmethod
    def es_flor(cartas: list[Carta], guia: Carta) -> bool:
        # Método que determina si las cartas de una mano son flor

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
        
        # Es flor si:
        # flor blanca: todas las cartas de un palo
        # flor normal: dos cartas de un palo + una guía
        # reservada: dos o tres cartas de la guía
        # comprobamos que como mucho hay un palo distinto (sin contar guía)
        return len(set(palo for palo in palos if palo > 0)) < 2    
    
    @staticmethod
    def puntuacion_flor(cartas: list[Carta], guia: Carta) -> bool:
        # Método que determina si las cartas de una mano son flor

        # Validación de flor
        if not FlorTruque.es_flor(cartas, guia):
            return ValueError(f"Se ha cantado una flor que no lo es.")
        
        # El valor de la flor es el valor de pares        
        return ParesTruque.puntuacion_pares(cartas, guia)

    @staticmethod
    def cantar_flor(partida: Partida, jugador_id: int) -> dict[str, any]:
        estado: EstadoTruque = partida.juego.ronda.estado

        # Obtenemos la lista de jugadores, y extraemos sus ids para poder buscar por id o índice..
        jugadores = partida.lista_jugadores()
        n_jugadores = len(jugadores)
        jugador, idx = partida.jugador_por_id(jugador_id)

        # Comprobamos que el jugador tiene flor
        if not FlorTruque.es_flor(jugador.cartas(), partida.juego.ronda.guia):
            raise ValueError("No se puede cantar flor si el jugador no tiene flor.")
        
        # Si ningun jugador ha cantado flor todavía, iniciamos la apuesta
        if estado.flor is None:
            estado.iniciar_flor(jugador)

        # Si la apuesta ya está iniciada, añadimos el cante del jugador
        else:
            estado.flor.cantar_flor(jugador)

        # Pasamos al siguiente jugador a cantar
        FlorTruque.siguiente_cante_flor(partida, jugador_id)

        return {
            "accion": "cantar_flor",
            "jugador": jugador_id
        }
    
    @staticmethod
    def no_cantar_flor(partida: Partida, jugador_id: int) -> dict[str, any]:

        # Pasamos al siguiente jugador a cantar
        FlorTruque.siguiente_cante_flor(partida, jugador_id)

        return {
            "accion": "cantar_flor",
            "jugador": jugador_id
        }
    
    def siguiente_cante_flor(partida: Partida, jugador_id: int) -> None:
        estado: EstadoTruque = partida.juego.ronda.estado

        # Obtenemos la lista de jugadores, y extraemos sus ids para poder buscar por id o índice..
        jugadores = partida.lista_jugadores()
        n_jugadores = len(jugadores)
        jugador, idx = partida.jugador_por_id(jugador_id)
            
        siguiente_jugador_idx = (idx + 1) % n_jugadores
    
        # Si han cantado todos los jugadores (el siguiente jugador es el que cantó inicialmente) 
        # terminamos la fase de apuesta.
        jugador_apuesta = estado.flor.jugador_apuesta
        jugador_apuesta_idx = jugadores.index(jugador_apuesta)
        if jugador_apuesta_idx == siguiente_jugador_idx:
            estado.flor.todos_cantaron()

            # Si la fase de apuesta está abierta (ambos equipos tienen flor), continúa el primer jugador según la mano
            if estado.flor.abierta:
                mano_idx = jugadores.index(partida.juego.ronda.mano)
                siguiente_jugador = FlorTruque.siguiente_flor_desde(estado.flor.jugadores, jugadores, mano_idx)
                estado.siguiente_jugador(siguiente_jugador)

            # Si se ha cerrado la apuesta, volvemos a la fase de juego
            else:
                estado.finalizar_apuesta()

        # Si todavía no han cantado todos los jugadores, el turno pasa al siguiente jugador
        else:
            estado.siguiente_jugador(jugadores[siguiente_jugador_idx])

    @staticmethod
    def siguiente_flor_desde(ids_con_flor: list[list[int]], jugadores: list[Jugador], actual_id: int, actual_equipo: int | None = None) -> Jugador:
        if actual_equipo is None:
            ids = [id for equipo in ids_con_flor for id in equipo]
        else:
            ids = ids_con_flor[actual_equipo - 1] # El índice empieza en 0

        jugadores_id = [jugador.id for jugador in jugadores]
        jugadores_idx = [jugadores_id.index(id) for id in ids]

        actual_idx = jugadores_id.index(actual_id)
        n_jugadores = len(jugadores)
        idx_desde_actual = min((i - actual_idx) % n_jugadores for i in jugadores_idx)
        idx_absoluto = (idx_desde_actual + actual_idx) % n_jugadores
        return jugadores[idx_absoluto]

    @staticmethod
    def apostar_flor(partida: Partida, jugador_id: int, apuesta: int) -> dict[str, any]:
        estado: EstadoTruque = partida.juego.ronda.estado
        la_falta = partida.juego.la_falta()

        # Comprobamos si el jugador tiene flor cantada, si no hay ya alguna apuesta (en ese caso sería subir la apuesta) 
        # y si la apuesta es válida
        if estado.flor is None:
            raise ValueError("No se ha hecho ronda de cante de flor.")
        if not estado.flor.abierta:
            raise ValueError("No se puede apostar, no está la apuesta de flor abierta.")
        if estado.flor.jugador_apuesta is not None:
            raise ValueError("Ya se ha apostado alguna flor, el jugador debe subir o querer la apuesta.")
        if apuesta is None:
            apuesta = 1
        elif apuesta*3 > la_falta + 2:
            raise ValueError(f"La apuesta de pares debe ser como mucho las flores que hacen falta para llegar a ({(la_falta + 2) // 3})")
        elif apuesta < 1:
            raise ValueError(f"La apuesta de pares mínima es 1 flor (3 puntos).")
        if jugador_id not in [jugador for equipo in estado.flor.jugadores for jugador in equipo]:
            raise ValueError(f"El jugador no puede apostar flor, ya que no cantó.")

        # Obtenemos la lista de jugadores, y extraemos sus ids para poder buscar por id o índice..
        jugadores = partida.lista_jugadores()
        jugador, idx = partida.jugador_por_id(jugador_id)

        # Queremos la apuesta
        estado.flor.abrir_apuesta(jugador, apuesta)

        # El turno pasa al siguiente jugador con flor del equipo contrario (1 → 2, 2 → 1)
        siguiente_jugador = FlorTruque.siguiente_flor_desde(estado.flor.jugadores, jugadores, (idx + 1) % len(jugadores), jugador.equipo % 2 + 1)
        estado.siguiente_jugador(siguiente_jugador)

        return {
            "accion": "apostar_flor",
            "jugador": jugador_id, 
            "apuesta": apuesta
        }

    def rechazar_flor(partida: Partida, jugador_id: int) -> dict[str, any]:
        estado: EstadoTruque = partida.juego.ronda.estado

        # Comprobamos si estamos en ronda de apuestas
        if estado.flor is None:
            raise ValueError("No se ha hecho ronda de cante de flor.")
        if not estado.flor.abierta:
            raise ValueError("No se puede apostar, no está la apuesta de flor abierta.")

        # Obtenemos al jugador actual
        jugadores = partida.lista_jugadores()
        jugador, idx = partida.jugador_por_id(jugador_id)

        # Si no hay ninguna apuesta de jugador, la ronda le pasa a tocar al siguiente jugador con flor
        if not estado.flor.jugador_apuesta:
            mano_idx = jugadores.index(partida.juego.ronda.mano)
            primera_apuesta = FlorTruque.siguiente_flor_desde(estado.flor.jugadores, jugadores, mano_idx)
            siguiente_jugador = FlorTruque.siguiente_flor_desde(estado.flor.jugadores, jugadores, (idx + 1) % len(jugadores))

            # Si el siguiente jugador es el mano, se ha acabado la ronda de apuestas, y nadie ha apostado
            if primera_apuesta.id == siguiente_jugador.id:
                siguiente_jugador = None                    # Marcamos none para indicar que no hay siguiente jugador → la ronda acaba

        # Si ya existe una apuesta de jugador, la ronda le pasa al siguiente jugador del equipo.
        else:
            jugador_apuesta_idx = jugadores.index(estado.flor.jugador_apuesta)
            primer_jugador_apuesta = FlorTruque.siguiente_flor_desde(estado.flor.jugadores, jugadores, jugador_apuesta_idx, jugador.equipo)
            siguiente_jugador = FlorTruque.siguiente_flor_desde(estado.flor.jugadores, jugadores, (idx + 1) % len(jugadores), jugador.equipo)

            # Si el jugador siguiente ya ha apostado, se cierra la apuesta.
            # El siguiente jugador ya ha apostado si coincide con el primer jugador del equipo en apostar despues de el jugador apuesta
            if primer_jugador_apuesta.id == siguiente_jugador.id:
                siguiente_jugador = None

        # Si hay siguiente jugador, pasamos la ronda al siguiente
        if siguiente_jugador is not None:
            estado.siguiente_jugador(siguiente_jugador) 
            return {
                "accion": "rechazar_flor",
                "jugador": jugador_id
            }
        
        # Si no hay siguiente jugador, terminamos la apuesta de flor
        else:

            # Si no había apuesta, la apuesta queda cerrada con el valor mínimo
            if estado.flor.jugador_apuesta is None:
                estado.flor.querer_apuesta()
                return {
                    "accion": "finalizada_flor",
                    "jugador": jugador_id,
                    "estado": "querida", 
                    "apuesta": estado.flor.apuesta_cerrada
                }

            # Si la apuesta la ha hecho ya un jugador, y el otro equipo no la ha querido, queda ganada por el equipo
            else:   
                estado.flor.rechazar_apuesta()
                estado.finalizar_apuesta()  
                return {
                    "accion": "finalizada_flor",
                    "jugador": jugador_id,
                    "estado": "ganada",
                    "equipo_ganador": estado.flor.jugador_apuesta.equipo, 
                    "apuesta": estado.flor.apuesta_cerrada
                }

    @staticmethod
    def querer_flor(partida: Partida, jugador_id: int) -> dict[str, any]:
        estado: EstadoTruque = partida.juego.ronda.estado

        # Comprobamos si el jugador tiene flor cantada, si ya hay apuesta realizada
        if estado.flor is None:
            raise ValueError("No se ha hecho ronda de cante de flor.")
        if not estado.flor.abierta:
            raise ValueError("No se puede apostar, no está la apuesta de flor abierta.")
        if estado.flor.jugador_apuesta is None:
            raise ValueError("Todavía no se ha apostado ninguna flor. Apostar o pasar.")
        if jugador_id not in [jugador for equipo in estado.flor.jugadores for jugador in equipo]:
            raise ValueError(f"El jugador no puede apostar flor, ya que no cantó flor.")

        # El jugador quiere la apuesta de pares, y se finaliza la apuesta (eliminar la información de la apuesta abierta)
        estado.flor.querer_apuesta()
        estado.finalizar_apuesta()

        return {
            "accion": "querer_flor",
            "jugador": jugador_id,
            "estado": "querida", 
            "apuesta": estado.flor.apuesta_cerrada
        }

    @staticmethod
    def subir_flor(partida: Partida, jugador_id: int, apuesta: int) -> dict[str, any]:
        estado: EstadoTruque = partida.juego.ronda.estado

        # Comprobamos si el jugador tiene flor cantada,  comprobación de que la apuesta es válida (mayor que la apuesta actual) 
        # y si la apuesta es válida
        ultima_apuesta = estado.flor.apuesta
        la_falta = partida.juego.la_falta()
        if estado.flor is None:
            raise ValueError("No se ha hecho ronda de cante de flor.")
        if not estado.flor.abierta:
            raise ValueError("No se puede apostar, no está la apuesta de flor abierta.")
        if estado.flor.jugador_apuesta is None:
            raise ValueError("Todavía no se ha apostado ninguna flor. Apostar o pasar.")
        if apuesta is None:
            apuesta = ultima_apuesta//3 + 1
        if apuesta <= ultima_apuesta // 3:
            raise ValueError(f"La apuesta de flor debe ser mayor que la apuesta actual ({ultima_apuesta // 3}).")
        elif apuesta*3 > la_falta + 2:
            raise ValueError(f"La apuesta de flor debe ser como mucho las flores que hacen falta para llegar a ({(la_falta + 2) // 3})")
        elif apuesta < 1:
            raise ValueError(f"La apuesta de flor mínima es 1 flor (3 puntos).")
        if jugador_id not in [jugador for equipo in estado.flor.jugadores for jugador in equipo]:
            raise ValueError(f"El jugador no puede apostar flor, ya que no cantó.")

        # Obtenemos la lista de jugadores, y extraemos sus ids para poder buscar por id o índice..
        jugadores = partida.lista_jugadores()
        jugador, idx = partida.jugador_por_id(jugador_id)
        
        estado.flor.subir_apuesta(jugador, apuesta)

        # El turno pasa al siguiente jugador con flor del equipo contrario (1 → 2, 2 → 1)
        siguiente_jugador = FlorTruque.siguiente_flor_desde(estado.flor.jugadores, jugadores, (idx + 1) % len(jugadores), jugador.equipo % 2 + 1)
        estado.siguiente_jugador(siguiente_jugador)

        return {
            "accion": "subir_flor",
            "jugador": jugador_id,
            "apuesta": apuesta
        }