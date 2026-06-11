from ....dominio import Partida, Jugador
from ..estadoTruque import EstadoTruque
from .florTruque import FlorTruque
from .paresTruque import ParesTruque

class RepartoTruque: 

    @staticmethod
    def iniciar_juego(partida: Partida) -> dict[str, any]:
        # Creamos una partida dentro del juego.
        partida.iniciar_juego()
        return {
            "accion": "iniciar_juego"
            }

    @staticmethod
    def iniciar_ronda(partida: Partida) -> dict[str, any]:
        # Creamos una ronda dentro del juego.
        mano = EstadoTruque.siguiente_mano(partida)
        partida.juego.iniciar_ronda(mano)
        partida.juego.ronda.estado = EstadoTruque(jugador=partida.juego.ronda.mano, ronda=1)
        return {
            "accion": "iniciar_ronda",
            "mano": mano.nombre
            }
    
    @staticmethod
    def repartir_cartas(partida: Partida) -> dict[str, any]:
        # Barajamos
        partida.baraja.barajar()

        # Repartimos las cartas a los jugadores.
        for jugador in partida.lista_jugadores():
            cartas = partida.baraja.robar(3)
            jugador.recibir_cartas(cartas)
        guia = partida.baraja.robar(1)
        partida.juego.ronda.poner_guia(guia[0])
        return {
            "accion": "repartir_cartas"
            }

    @staticmethod
    def devolver_cartas(partida: Partida) -> None:
        # Devolvemos las cartas a la baraja.
        for jugador in partida.lista_jugadores():
            cartas = jugador.devolver_cartas()
            partida.baraja.devolver(cartas)
        guia = partida.juego.ronda.devolver_guia()
        partida.baraja.devolver([guia])

    @staticmethod
    def contar_puntos(partida: Partida) -> dict[str,any]:
        estado: EstadoTruque = partida.juego.ronda.estado

        # Ordenamos la lista de jugadores para que la mano esté al principio (en caso de empate)
        jugadores = partida.lista_jugadores()
        mano = partida.juego.ronda.mano
        mano_idx = jugadores.index(mano)
        
        guia = partida.juego.ronda.guia
        jugadores = jugadores[mano_idx:] + jugadores[:mano_idx]
        puntos = [0,0]

        # Recuento de puntuación
        # 1: Contar puntos de apuestas
        apuestas = {}
        # Caso 1.1 - se ha apostado flor
        if estado.flor is not None:
            apuestas["flor"] = {}

            # 1.1.1a: Apuesta no querida, gana el equipo que ha ganado la apuesta
            if not estado.flor.querida:
                equipo_ganador = estado.flor.jugador_apuesta.equipo

            # 1.1.1b: Apuesta querida, vemos que jugador tiene una flor mayor
            else:
                guia = partida.juego.ronda.guia
                jugadores_con_flor_ids = [jugador for equipo in estado.flor.jugadores for jugador in equipo]
                jugadores_con_flor = [jugador for jugador in jugadores if jugador.id in jugadores_con_flor_ids]
                puntuacion_flor = [FlorTruque.puntuacion_flor(jugador.cartas(), guia) for jugador in jugadores_con_flor]

                # El equipo que gana la apuesta es el que tenga una mayor puntuación
                jugador_ganador_idx = puntuacion_flor.index(max(puntuacion_flor))
                equipo_ganador = jugadores_con_flor[jugador_ganador_idx].equipo

            # 1.1.2: Calculamos la puntuación de la apuesta
            equipo_idx = equipo_ganador-1

            # Se suma el valor de la apuesta
            puntos[equipo_idx] = puntos[equipo_idx] + estado.flor.apuesta_cerrada
            apuestas["flor"]["puntos"] = estado.flor.apuesta_cerrada
            apuestas["flor"]["equipo"] = equipo_ganador

            # Mas 3 puntos por cada flor del equipo ganador
            puntos[equipo_idx] = puntos[equipo_idx] + len(estado.flor.jugadores[equipo_idx]) * 3
            apuestas["flor"]["puntos_flores"] = len(estado.flor.jugadores[equipo_idx]) * 3
            apuestas["flor"]["jugadores_con_flor"] = [partida.jugador_por_id(id)[0] for id in estado.flor.jugadores[equipo_idx]]

        # Caso 1.2 - se ha apostado pares
        elif estado.pares is not None:
            apuestas["pares"] = {}

            # 1.2.1a: Apuesta no querida, gana el equipo que ha ganado la apuesta
            if not estado.pares.querida:
                equipo_ganador = estado.pares.jugador_apuesta.equipo
                            
            # 1.2.1b: Apuesta querida, vemos que jugador tiene mejores pares
            else:
                puntuacion_flor = [ParesTruque.puntuacion_pares(jugador.cartas(), guia) for jugador in jugadores]

                # El equipo que gana la apuesta es el que tenga una mayor puntuación
                jugador_ganador_idx = puntuacion_flor.index(max(puntuacion_flor))
                equipo_ganador = jugadores[jugador_ganador_idx].equipo

            # 1.1.2: Calculamos la puntuación de la apuesta
            equipo_idx = equipo_ganador-1

            # Se suma el valor de la apuesta
            puntos[equipo_idx] = puntos[equipo_idx] + estado.pares.apuesta_cerrada
            apuestas["pares"]["puntos"] = estado.pares.apuesta_cerrada
            apuestas["pares"]["equipo"] = equipo_ganador

            # Mas 3 puntos por cada reservada del equipo ganador
            puntos[equipo_idx] = puntos[equipo_idx] + 3*len([1 for jugador in partida.equipos[equipo_idx] if ParesTruque.es_reservada(jugador.cartas(), guia)])
            apuestas["pares"]["puntos_reservadas"] = 3*len([1 for jugador in partida.equipos[equipo_idx] if ParesTruque.es_reservada(jugador.cartas(), guia)])
            apuestas["pares"]["jugadores_con_reservada"] = [jugador for jugador in partida.equipos[equipo_idx] if ParesTruque.es_reservada(jugador.cartas(), guia)]

        # Caso 1.3: No se ha hecho ninguna apuesta de pares, nadie se lleva nada

        # Una vez que se ha contado pares, si un equipo ha superado los 31 puntos, gana la partida, si no, seguimos contando truque
        if not any(a + b >= 31 for a, b in zip(puntos, partida.juego.puntuacion)):    
            apuestas["truque"] = {}

            # 2: Apuesta de truque
            # 2a. Si se ha hecho una apuesta de truque y se ha ganado, el equpo se lleva los puntos correspondientes
            if estado.truque is not None and not estado.truque.querida:
                
                # Apuesta no querida, gana el equipo que ha ganado la apuesta
                equipo_idx = estado.truque.jugador_apuesta.equipo - 1

            #2b: Apuesta querida o no se ha llegado a apostar, vemos que equipo ha ganado
            else: 
                equipo_bazas = [jugador.equipo for jugador in estado.bazas if jugador != 0]
                equipo_idx = sum(equipo == 2 for equipo in equipo_bazas) > sum(equipo == 1 for equipo in equipo_bazas) + 1

            # Calculamos la puntuación de la apuesta y sumamos
            puntos[equipo_idx] = puntos[equipo_idx] + (estado.truque.apuesta if estado.truque is not None else 1)
            apuestas["truque"]["puntos"] = estado.truque.apuesta if estado.truque is not None else 1
            apuestas["truque"]["equipo"] = equipo_idx+1

        # sumamos los puntos
        partida.juego.puntuacion = [a + b for a, b in zip(puntos, partida.juego.puntuacion)]
        partida.juego.ronda.estado = None

        return {
            "accion": "contar_puntos",
            "puntuacion": puntos, 
            "apuestas": apuestas
            }

    @staticmethod
    def terminar_ronda(partida: Partida) -> dict[str,any]:
        # Devolvemos las cartas de los jugadores.
        for jugador in partida.lista_jugadores():
            cartas = jugador.devolver_cartas()
            partida.baraja.devolver(cartas)
        guia = partida.juego.ronda.devolver_guia()
        partida.baraja.devolver([guia])

        # Pasamos la mano al siguiente jugador
        jugadores = partida.lista_jugadores()
        mano_antigua_idx = jugadores.index(partida.juego.ronda.mano)
        nueva_mano = jugadores[(mano_antigua_idx + 1) % len(jugadores)]
        partida.juego.ronda.mano = nueva_mano

        partida.juego.ronda.estado = EstadoTruque(jugador=nueva_mano, ronda=1)
        return {
            "accion": "terminar_ronda"
            }
    

    @staticmethod
    def terminar_juego(partida: Partida) -> dict[str,any]:
        
        # Al menos uno de los dos equipos tiene que tener 31 puntos
        if not any([puntos > 30 for puntos in partida.juego.puntuacion]):
            raise ValueError("No se puede terminar juego si ninguno de los equipos ha llegado a 31 puntos")
        
        # Marcamos al equipo ganador y le sumamos un punto
        equipo_ganador = partida.juego.puntuacion.index(max(partida.juego.puntuacion))
        partida.puntuacion[equipo_ganador] = partida.puntuacion[equipo_ganador] + 1

        # Eliminamos el juego para iniciar otro
        partida.juego = None
        return {
            "accion": "terminar_juego",
            "equipo_ganador": equipo_ganador + 1
        }
