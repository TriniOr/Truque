from typing import Optional

from ...dominio import Jugador, Partida

class Flor:

    jugadores: list[list[int]]          # Lista de jugadores que han cantado flor, divididos por equipo.
    cantar: bool                        # Indica si se estan cantando las flores.
    abierta: bool                       # Indica si la apuesta de flor está abierta.        
    querida: bool                       # Indica si la apuesta de flor ha sido querida (una vez cerrada). 
    apuesta_cerrada: int                # Valor apostado en la última apuesta de flor.
    apuesta: int                        # Valor apostado en la flor.
    jugador_apuesta: Jugador | None     # Indica el jugador que ha hecho la última apuesta de flor.

    # Al iniciar apuesta, se inicia la fase de cantar flor.
    def __init__(self, jugador: Jugador):
        self.jugadores = [[jugador.id] if jugador.equipo == 1 else [], [jugador.id] if jugador.equipo == 2 else []]
        self.jugador_apuesta = jugador
        self.cantar = True
        self.abierta = False
        self.querida = False
        self.apuesta = 0
        self.apuesta_cerrada = 0

    # Cada persona que canta flor se añade a la lista de jugadores que han cantado flor.
    def cantar_flor(self, jugador: Jugador):
        self.jugadores[jugador.equipo - 1].append(jugador.id)

    # Una vez que todos han cantado flor, se cierra la fase de cantar.
    def todos_cantaron(self):
        self.cantar = False

        # Si al menos un jugador de cada equipo ha cantado flor, se abre la fase de apuestas.
        if len(self.jugadores[0]) > 0 and len(self.jugadores[1]) > 0:
            self.abierta = True
            self.jugador_apuesta = None

    # Al iniciar la fase de apuesta de flor, el primer jugador puede abrir la apuesta.
    def abrir_apuesta(self, jugador: Jugador, apuesta: int):
        self.jugador_apuesta = jugador
        self.apuesta = apuesta*3
        self.abierta = True

    # Una vez un jugador ya ha abierto la apuesta, el siguiente jugador puede subir la apuesta.
    def subir_apuesta(self, jugador: Jugador, apuesta: int):
        self.jugador_apuesta = jugador
        self.apuesta_cerrada = self.apuesta
        self.apuesta = apuesta*3

    # Si el jugador cierra la apuesta, se guarda el valor de la apuesta (apuesta_cerrada) 
    # y se cierra la apuesta.
    def querer_apuesta(self):
        self.apuesta_cerrada = self.apuesta
        self.abierta = False
        self.querida = True

    # Si el jugador rechaza la apuesta, se cierra la apuesta manteniendo el último valor de apuesta cerrado.
    def rechazar_apuesta(self):
        self.abierta = False
        self.querida = False
        # Si se rechaza una apuesta de flor y la apuesta cerrada es 0, hay un punto adicional de "vuelque".
        if self.apuesta_cerrada == 0:
            self.apuesta_cerrada = 1

class Pares:

    apuesta: int                        # Valor apostado en la apuesta de pares.
    apuesta_cerrada: int                # Valor apostado en la última apuesta de pares.
    abierta: bool                       # Indica si la apuesta de pares está abierta.  
    querida: bool                       # Indica si la apuesta de pares ha sido querida (una vez cerrada).
    jugador_apuesta: Jugador            # Indica el jugador que ha hecho la primera apuesta de pares (luego no puede apostar flor).
    jugador_ultima_apuesta: Jugador     # Indica el jugador que ha hecho la última apuesta de pares. 

    # Al iniciar la apuesta de pares, se abre la apuesta con el valor apostado, y el jugador que ha apostado.
    def __init__(self,  jugador: Jugador, apuesta: int):
        self.apuesta = apuesta
        self.apuesta_cerrada = 0
        self.abierta = True
        self.querida = False
        self.jugador_apuesta = jugador
        self.jugador_ultima_apuesta = jugador

    # Si un jugador sube la apuesta, se actualiza el valor de la apuesta, y el jugador que ha hecho la última apuesta.
    def subir_apuesta(self, jugador: Jugador, apuesta: int):
        self.jugador_ultima_apuesta = jugador
        self.apuesta_cerrada = self.apuesta
        self.apuesta = apuesta

    # Si el jugador quiere la apuesta, se cierra la apuesta y se guarda el valor de la apuesta.
    def querer_apuesta(self):
        self.apuesta_cerrada = self.apuesta
        self.abierta = False
        self.querida = True

    # Si el jugador rechaza la apuesta, se cierra la apuesta manteniendo el último valor de apuesta cerrado.
    def rechazar_apuesta(self):
        self.apuesta_cerrada = max(self.apuesta_cerrada, 1)
        self.abierta = False
        self.querida = False

class ApuestaTruque:

    apuesta: int                    # Valor apostado en la apuesta de truque (3 para truque, 6 para retruque, 31 para juego fuera).
    abierta: bool                   # Indica si la apuesta de truque está abierta.
    querida: bool                   # Indica si la apuesta de truque ha sido querida (una vez cerrada).
    jugador_apuesta: Jugador        # Indica el jugador que ha hecho la última apuesta de truque.

    # Al iniciar la apuesta de truque, se abre la apuesta con el valor apostado (3 para truque) y el jugador que ha apostado.
    def __init__(self, jugador: Jugador):
        self.jugador_apuesta = jugador
        self.apuesta = 3
        self.querida = False
        self.abierta = True

    # Si un jugador quiere la apuesta, se cierra la apuesta.
    def querer_apuesta(self):
        self.querida = True
        self.abierta = False

    # Si un jugador sube la apuesta, se actualiza el valor de la apuesta (6 para retruque, 31 para juego fuera), y el jugador que ha hecho la última apuesta.
    def subir_apuesta(self, jugador: Jugador):
        self.jugador_apuesta = jugador
        self.querida = False
        self.abierta = True
        # Si se sube un truque, se convierte en retruque, y si se sube un retruque, se convierte en juego fuera.
        self.apuesta = 6 if self.apuesta == 3 else 31  # truque = 3 puntos, retruque = 6 puntos, juego fuera = 31 puntos

    # Si un jugador rechaza la apuesta, se cierra la apuesta manteniendo el último valor de apuesta cerrado.
    def rechazar_apuesta(self):
        self.querida = False
        self.abierta = False
        # Si se rechaza un truque, el otro equipo gana 1 punto, si rechaza un retruque, 3 puntos, y un juego fuera, 6 puntos.
        self.apuesta = 1 if self.apuesta == 3 else 3 if self.apuesta == 6 else 6 
        

class EstadoTruque:

    _jugador_siguiente: Jugador | None  # Jugador que tiene el siguiente turno en fase de apuestas
    _jugador_original: Jugador          # Jugador que tiene el siguiente turno en fase de juego (jugar carta). 
                                        # Se mantiene durante toda la apuesta.
    ronda: int                          # Ronda actual de la partida (1, 2 o 3), 4 si ya se han jugado las 3 rondas.
    pares: Optional[Pares]              
    truque: Optional[ApuestaTruque]
    flor: Optional[Flor]
    puntos: int                         # Rondas de cartas ganadas por cada equipo (positivos para el equipo 1, negativos para el equipo 2).

    def __init__(self, jugador: Jugador, ronda: int = 0):
        self._jugador_siguiente = None
        self._jugador_original = jugador
        self.ronda = ronda
        self.pares = None
        self.truque = None
        self.flor = None
        self.reos: Jugador | int = [0,0,0]

    # Jugador: el siguiente jugador que tiene una accion, ya sea _jugador_siguiente en fase de apuestas 
    # o _jugador_original en fase de juego. 
    @property
    def jugador(self) -> Jugador:
        return self._jugador_siguiente if self._jugador_siguiente else self._jugador_original

    # Definir el siguiente jugador en la fase de juego. 
    # En caso de paso de ronda, actualizar la ronda y los puntos (gana el equipo del jugador que empieza la siguiente ronda).
    def siguiente_ronda(self, jugador: Jugador, nueva_ronda: bool = False, pata:bool = False):
        self._jugador_original = jugador
        if nueva_ronda:
            if pata and self.ronda == 1:
                self.reos[0] = 0 #Pata hay que echar la mejor carta arriba
                self.reos[1] = 0
                self.ronda = 3
                ("Pata")
            else:
                self.reos[self.ronda-1] = jugador
                self.ronda = self.ronda+1

    # Actualizar el siguiente jugador en la fase de apuestas.
    def siguiente_jugador(self, jugador: Jugador):
        self._jugador_siguiente = jugador

    # Iniciar una apuesta de pares.
    def iniciar_pares(self, jugador: Jugador, apuesta: int):
        self.pares = Pares(jugador, apuesta)

    # Iniciar una apuesta de truque.
    def trucar(self, jugador: Jugador):
        self.truque = ApuestaTruque(jugador)

    # Iniciar una apuesta de flor.
    def iniciar_flor(self, jugador: Jugador):
        self.flor = Flor(jugador)
        self.pares = None

    # Finalizar la apuesta abierta, eliminando la información del jugador que la hizo para volver a la fase de juego.
    def finalizar_apuesta(self):
        self._jugador_siguiente = None

    # Determina si una ronda ya está ganada
    def ronda_ganada(self) -> bool:
        # Si ya se han jugado las 3 rondas
        (self.ronda)
        if self.ronda > 3:
            ("Ronda 4", self.ronda)
            return True
        # Si se ha querido el truque
        if self.truque is not None and not self.truque.abierta and not self.truque.querida:
            return True
        # Si un equipo ya ha ganado 2 reos
        equipo_reos = [jugador.equipo for jugador in self.reos if jugador != 0]
        if sum(equipo == 1 for equipo in equipo_reos)>1 or sum(equipo == 2 for equipo in equipo_reos)>1:
            
            return True
        return False
        

    @staticmethod
    def siguiente_mano(partida: Partida) -> Jugador:

        if partida.juego is not None and partida.juego.ronda is not None and partida.juego.ronda.mano is not None:
            return partida.juego.ronda.mano
        
        jugadores = partida.lista_jugadores()

        i = sum(partida.puntuacion)
        if partida.juego is not None:
            i += sum(partida.juego.puntuacion)
        
        return jugadores[i % len(jugadores)]
    

