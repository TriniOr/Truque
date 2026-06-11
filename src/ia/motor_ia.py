import random
import math
from src.juegos.truque.puntosTruque import PuntosTruque
from src.dominio.cartas import Carta, Palo, Numero

def decidir(dificultad: str, estado: dict, acciones: list, jugador: int) -> tuple[str, int, dict, str]:
    DIFICULTADES = {
        "IA Facil":   0,
        "IA Medio":   1,
        "IA Dificil": 2,
        "IA Experto": 3,
    }
    pesos = _calcular_pesos(estado, acciones, jugador, DIFICULTADES[dificultad])
    print("Pesos:",pesos)
    accion_elegida = _seleccionar(pesos)
    print("Elegida:",accion_elegida)
    comentarios = _comentario(estado, accion_elegida[0], accion_elegida[2])
    return (*accion_elegida, comentarios)

def _samplear_apuesta(min_v, max_v, mu, sigma) -> int:
    # normal truncada a [min, max]
    while True:
        valor = int(random.gauss(mu, sigma) + 0.5)
        if min_v <= valor <= max_v:
            return valor

def _seleccionar(pesos: list) -> tuple[str, int, dict]:
    total = sum(p for *_, p in pesos)
    r = random.uniform(0, total)
    acumulado = 0
    accion_elegida = (pesos[0][0], pesos[0][1], pesos[0][2])
    for *accion, peso in pesos:
        acumulado += peso
        if r <= acumulado:
            accion_elegida = (accion[0], accion[1], accion[2])
            break
    return accion_elegida


def _calcular_pesos(estado: dict, acciones: list, jugador:int, dificultad:int) -> list:
    pesos = []
    mano = estado["partida"]["mesa"]["guía"]
    guia = estado["partida"]["mesa"]["guía"]
    jugadores = estado["partida"]["jugadores"]
    cartas = jugadores[jugador]["cartas_en_mano"].items()
    baza = 4 - len(cartas)
    mi_equipo = jugadores[jugador]["equipo"]
    compis = [jugador for jugador in jugadores.values() if jugador["equipo"] == mi_equipo]
    rivales = [jugador for jugador in jugadores.values() if jugador["equipo"] != mi_equipo]
    print(estado["partida"]["mesa"]["bazas"])
    otro_equipo = rivales[0]["equipo"]
    carta_baza_compis = [compi["cartas_echadas"][baza-1] for compi in compis if len(compi["cartas_echadas"]) >= baza]
    carta_baza_rivales = [rival["cartas_echadas"][baza-1] for rival in rivales if len(rival["cartas_echadas"]) >= baza]
    bazas_mi_equipo = sum(jugador in compis for jugador in estado["partida"]["mesa"]["bazas"])
    bazas_otro_equipo = sum(jugador in rivales for jugador in estado["partida"]["mesa"]["bazas"])

    # calculamos la mejor carta en la mesa
    mejor_carta_compis = PuntosTruque.ordenar_cartas(carta_baza_compis, guia=guia)
    mejor_carta_rivales = PuntosTruque.ordenar_cartas(carta_baza_rivales, guia=guia)
    mejor_carta = PuntosTruque.ordenar_cartas(mejor_carta_compis + mejor_carta_rivales, guia=guia)
    if len(mejor_carta) == 0:
        equipo_ganando_baza = 0
    else:
        equipo_ganando_baza = mi_equipo if mejor_carta[0] in mejor_carta_compis else otro_equipo
    
    for accion, jugador, opciones in acciones:

        if accion == "jugar_carta":

            # Dificultad facil: carta al azar, probabilidad uniforme
            if dificultad == 0:
                for idx, carta in cartas:
                    if carta is None:
                        continue
                    peso = 1
                    pesos.append((accion, jugador, {"carta": idx}, peso))

            # Dificultad media: depende de si la ronda va ganada o no
            if dificultad == 1:
                cartas_ordenadas = PuntosTruque.ordenar_cartas([carta for i, carta in cartas], guia=guia)
                for idx, carta in cartas:
                    if carta is None:
                        continue
                    # Si va ganando el otro equipo, probabilidad mayor de echar si es mejor que la carta en mesa
                    if equipo_ganando_baza != mi_equipo:
                        carta_ganadora = PuntosTruque.ordenar_cartas(mejor_carta + [carta], guia=guia)
                        peso = 1 if carta_ganadora[0] in [carta] else 0.3
                    # Si va ganando el equipo, echa la peor parte con una probabilidad mayor
                    else:
                        peso = 1 if cartas_ordenadas[-1] in [carta] else 0.3
                    pesos.append((accion, jugador, {"carta": idx}, peso))

            # dificultad dificil: si va perdiendo echa practicamente siempre la menor que gana.
            # si va ganando echa la más baja

            # dificultad experto: igual a dificil +
            # si no tiene flor y tiene dos cartas del mismo palo, no las echa en la ronda 1 y 2 (porque tendría flor)


        elif accion == "apostar_truque":
            # Dificultad facil: truca de forma aleatoria con una probabilidad dependiendo de la ronda
            if dificultad == 0:
                peso = 0.05 if baza == 1 else 0.1 if baza == 2 else 0.3
                pesos.append((accion, jugador, {}, peso))

            # Dificultad media: probabilidad de trucar si lleva una ronda ganada su equipo y tiene una carta que gana a la sota de la guía + probabilidad por ronda
            elif dificultad == 1:

                # Comprobamos si el jugador tiene carta mejor o igual que la sota de guia
                carta_ganadora = PuntosTruque.ordenar_cartas([carta for i, carta in cartas] + [Carta(Numero.SOTA, guia.palo)], guia=guia)
                carta_mejor = carta_ganadora[0] in [carta for i, carta in cartas]

                if bazas_mi_equipo == 1 and carta_mejor:
                    peso = 0.3 if baza == 2 else 0.9
                else:
                    peso = 0
                pesos.append((accion, jugador, {}, peso))

            # Dificultad alta: calcula la probabilidad de ganar 1 o 2 bazas, 
            # para la primera: dependiendo de las que vaya teniendo el equipo. para ello ordena todas las cartas, y busca el índice de la mejor de la mesa, de la mejor que tiene, y da una probabilidad de ganar
            # si hay que ganar 2 bazas, lo mismo con su segunda mejor carta

            # Dificultad experto: tiene en cuenta en la lista de cartas las que ya se han echado. De vez en cuando echa falsos cuando es el último en tirar, tiene en cuenta si los jugadores que quedan tienen flor o no (y por lo tanto guía)

        elif accion in ["querer_truque", "rechazar_truque"]:
            # Dificultad facil: quiere de forma aleatoria
            if dificultad == 0:
                peso = 0.5
                peso = 1 - peso if accion == "rechazar_truque" else peso
                pesos.append((accion, jugador, {}, peso))

            # Dificultad media: quiere dependiendo de la apuesta, de si tiene carta mejor que la mejor de la mesa, y si tiene mejor carta que la copa
            elif dificultad == 1:

                # Comprobamos si el jugador tiene carta mejor o igual que la mejor de la mesa
                carta_ganadora = PuntosTruque.ordenar_cartas([carta for i, carta in cartas] + mejor_carta + [Carta(Numero.SEIS, Palo.COPAS)], guia=guia)
                carta_mejor_baza = carta_ganadora[0] in [carta for i, carta in cartas]
                # Comprobamos si el jugador tiene carta mejor o igual que la copa
                carta_ganadora = PuntosTruque.ordenar_cartas([carta for i, carta in cartas] + [Carta(Numero.AS, Palo.COPAS)], guia=guia)
                carta_mejor_copa = carta_ganadora[0] in [carta for i, carta in cartas]
                # Comprobamos si el jugador tiene carta mejor o igual que el 7 de oros
                carta_ganadora = PuntosTruque.ordenar_cartas([carta for i, carta in cartas] + [Carta(Numero.SIETE, Palo.OROS)], guia=guia)
                carta_mejor_siete = carta_ganadora[0] in [carta for i, carta in cartas]

                if bazas_mi_equipo == 1:
                    if equipo_ganando_baza == otro_equipo:
                        if baza == 3 and not carta_mejor_baza:
                            peso = 0
                        else:
                            peso = 1 if carta_mejor_copa else 0.5 if carta_mejor_siete else 0
                    else: 
                        peso == 1
                else:
                    peso = 0
                    
                peso = 1 - peso if accion == "rechazar_truque" else peso
                pesos.append((accion, jugador, {}, peso))

            # Dificultad alta: calcula la probabilidad de ganar 1 o 2 bazas, 
            # para la primera: dependiendo de las que vaya teniendo el equipo. para ello ordena todas las cartas, y busca el índice de la mejor de la mesa, de la mejor que tiene, y da una probabilidad de ganar
            # si hay que ganar 2 bazas, lo mismo con su segunda mejor carta

            # Dificultad experto: tiene en cuenta en la lista de cartas las que ya se han echado. De vez en cuando echa falsos cuando es el último en tirar, tiene en cuenta si los jugadores que quedan tienen flor o no (y por lo tanto guía)

        elif accion == "cantar_flor":
            pesos.append((accion, jugador, {}, 100))

        # --- tipo 3: apuesta con valor numérico (normal truncada) ---
        elif accion == "apostar_pares":
            min_v = opciones["apuesta"]["min"]
            max_v = opciones["apuesta"]["max"]
            mu = (min_v + max_v) / 2
            sigma = (max_v - min_v) / 4
            valor = _samplear_apuesta(min_v, max_v, mu, sigma)
            pesos.append((accion, jugador, {"apuesta": valor, "la_falta": max_v}, 0.5))

        else:
            pesos.append((accion, jugador, {}, 1.0))

    print("Pesos:",pesos)
    return pesos

def _comentario(estado, accion: str, opciones) -> str:
    if accion in ["querer_truque", "querer_pares", "apostar_flor"]:
        return "Quiero"
    elif accion in ["rechazar_truque", "rechazar_pares", "rechazar_flor"]:
        return "No quiero"
    elif accion in ["no_cantar_flor"]:
        return "Paso"
    else:
        return None