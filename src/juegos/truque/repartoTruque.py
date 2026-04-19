from ...dominio import Partida

class RepartoTruque: 

    @staticmethod
    def iniciar_juego(partida: Partida) -> dict[str, any]:
        # Creamos una partida dentro del juego.
        partida.iniciar_juego()
        return {
            "accion": "iniciar_juego"
            }

    @staticmethod
    def repartir_cartas(partida: Partida) -> None:
        # Repartimos las cartas a los jugadores.
        for jugador in partida.lista_jugadores():
            cartas = partida.baraja.robar(3)
            jugador.recibir_cartas(cartas)
        guia = partida.baraja.robar(1)
        partida.juego.ronda.poner_guia(guia[0])

    @staticmethod
    def devolver_cartas(partida: Partida) -> None:
        # Devolvemos las cartas a la baraja.
        for jugador in partida.lista_jugadores():
            cartas = jugador.devolver_cartas()
            partida.baraja.devolver(cartas)
        guia = partida.juego.ronda.devolver_guia()
        partida.baraja.devolver([guia])