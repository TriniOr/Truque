from ...dominio import Carta, Palo

class PuntosTruque: 

    @staticmethod
    def valor_carta_truque(carta: Carta, guia: Carta) -> int:

        # Si la carta es el 4 de la guía, y la guía no es el 6 o 7, el 4 tiene el mismo valor que la guía.
        if carta.numero == 4 and carta.palo == guia.palo and guia.numero not in [6, 7]:
            carta = guia

        # Orden de cartas: g = guia, n = otro palo, e = espada, o = oro, c = copa, b = basto
        # 3g > 2g > 5g > 1c > 1o > 1g > 12g > 11g > 10g > 1e > 1b > 7e > 7o > 3n > 2n > 12n > 11n > 10n > 7n > 6n > 5n > 4n
        # 25 > 24 > 23 > 22 > 21 > 20 > 19  > 18  > 17  > 16 > 15 > 14 > 13 > 12 > 11 > 10  > 9   > 8   > 7  > 6  > 5  > 4  
        # Asignamos a cada carta el valor correspondiente según el orden de cartas, teniendo en cuenta la guía.
        if carta.numero == 1 and carta.palo == Palo.COPAS:
            return 22
        if carta.numero == 1 and carta.palo == Palo.OROS:
            return 21
        if carta.palo == guia.palo:   
            if carta.numero == 3:
                return 25
            elif carta.numero == 2:
                return 24
            elif carta.numero == 5:
                return 23
            elif carta.numero == 1:
                return 20
            elif carta.numero == 12:
                return 19
            elif carta.numero == 11:
                return 18
            elif carta.numero == 10:
                return 17
        if carta.numero == 1 and carta.palo == Palo.ESPADAS:
            return 16
        if carta.numero == 1 and carta.palo == Palo.BASTOS:
            return 15
        if carta.numero == 7 and carta.palo == Palo.ESPADAS:
            return 14
        if carta.numero == 7 and carta.palo == Palo.OROS:
            return 13
        if carta.numero == 3:
            return 12
        if carta.numero == 2:
            return 11
        if carta.numero == 12:
            return 10
        if carta.numero == 11:
            return 9
        if carta.numero == 10:
            return 8
        if carta.numero == 7:
            return 7
        if carta.numero == 6:
            return 6
        if carta.numero == 5:
            return 5
        if carta.numero == 4:
            return 4
        return 0

    @staticmethod
    def mejor_carta(cartas: list[Carta], guia: Carta, mano: int) -> tuple[list[int], list[Carta]]:

        mejor_carta = 0
        idxs = []

        # Devuelve el índice de la mejor carta, y la carta. Lo recorremos en el orden de la mano
        for carta in cartas[mano:]+cartas[:mano]:
            valor = PuntosTruque.valor_carta_truque(carta, guia)

            # Devolvemos el índice de la mejor carta. Mantenemos el orden para tener en cuenta que la mano gana en caso de empate.
            if valor > mejor_carta:
                (valor)
                idxs = [cartas.index(carta)]
                mejor_carta = valor
            elif valor == mejor_carta:
                (valor)
                idxs.append(cartas.index(carta))

        return idxs, [cartas[idx] for idx in idxs]