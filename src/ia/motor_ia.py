import random
import math
from src.juegos.truque.puntosTruque import PuntosTruque
from src.juegos.truque.accionesTruque.paresTruque import ParesTruque
from src.juegos.truque.accionesTruque.florTruque import FlorTruque
from src.dominio.cartas import Carta, Palo, Numero

def decidir(dificultad: str, estado: dict, acciones: list, jugador: int) -> tuple[str, int, dict, str]:
    DIFICULTADES = {
        "IA Facil":   0,
        "IA Medio":   1,
        "IA Dificil": 2,
        "IA Experto": 3,
    }
    pesos = _calcular_pesos(estado, acciones, jugador, DIFICULTADES[dificultad])
    
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
    apuestas = estado["partida"]["apuestas"]
    jugadores = estado["partida"]["jugadores"]
    cartas = jugadores[jugador]["cartas_en_mano"].items()
    baza = 4 - len(cartas)
    mi_equipo = jugadores[jugador]["equipo"]
    compis = [jugador for jugador in jugadores.values() if jugador["equipo"] == mi_equipo]
    rivales = [jugador for jugador in jugadores.values() if jugador["equipo"] != mi_equipo]
    otro_equipo = rivales[0]["equipo"]
    carta_baza_compis = [compi["cartas_echadas"][baza-1] for compi in compis if len(compi["cartas_echadas"]) >= baza]
    carta_baza_rivales = [rival["cartas_echadas"][baza-1] for rival in rivales if len(rival["cartas_echadas"]) >= baza]
    bazas_mi_equipo = sum(jugador in compis for jugador in estado["partida"]["mesa"]["bazas"])
    bazas_otro_equipo = sum(jugador in rivales for jugador in estado["partida"]["mesa"]["bazas"])
    cartas_restantes = len(jugadores) - len(carta_baza_compis) - len(carta_baza_rivales)
    cartas_disponibles_baza = [carta for i, carta in cartas] + (
        jugadores[jugador]["cartas_echadas"][baza] if len(jugadores[jugador]["cartas_echadas"]) >= baza else [])
    cartas_pares = [carta for i, carta in cartas] + jugadores[jugador]["cartas_echadas"]

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
                cartas_ordenadas = PuntosTruque.ordenar_cartas(cartas_disponibles_baza, guia=guia)
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


        elif accion in ["apostar_truque", "subir_truque"]:
            apuesta_truque = apuestas["truque"].get("apuesta", 0)
            
            # Dificultad facil: truca de forma aleatoria con una probabilidad dependiendo de la ronda y la apuesta
            if dificultad == 0:

                if apuesta_truque == 0:
                    peso = 0.05 if baza == 1 else 0.3 if baza == 2 else 0.5
                elif apuesta_truque == 3:
                    peso = 0 if baza == 1 else 0.1 if baza == 2 else 0.2
                else:
                    peso = 0 if baza == 1 else 0 if baza == 2 else 0.05
                pesos.append((accion, jugador, {}, peso))

            # Dificultad media: probabilidad de trucar si lleva una ronda ganada su equipo y tiene una carta que gana a la sota de la guía + probabilidad por ronda
            elif dificultad == 1:

                # Comprobamos si el jugador tiene carta mejor o igual que la sota de guia
                carta_ganadora = PuntosTruque.ordenar_cartas(cartas_disponibles_baza + 
                                                             [Carta(Numero.SOTA, guia.palo)] + 
                                                             mejor_carta, guia=guia)
                carta_mejor_sota = carta_ganadora[0] in cartas_disponibles_baza
                # Comprobamos si el jugador tiene el tres de la guía
                carta_mejor_tres = Carta(Numero.TRES, guia.palo) in cartas_disponibles_baza

                # Si ya hay una ganada, y tiene una guía buena mejor que la mejor carta de la baza
                if bazas_mi_equipo == 1 and carta_mejor_sota:

                    if apuesta_truque == 0:
                        peso = 1 if carta_mejor_tres else (1 if cartas_restantes == 1 else 0.8) if baza == 3 else 0.3
                    elif apuesta_truque == 3:
                        peso = 1 if carta_mejor_tres else (1 if cartas_restantes == 1 else 0.4) if baza == 3 else 0.1
                    else:
                        peso = 1 if carta_mejor_tres else (1 if cartas_restantes == 1 else 0.2) if baza == 3 else 0
                    
                else:
                    peso = 0
                pesos.append((accion, jugador, {}, peso))

            # Dificultad alta: calcula la probabilidad de ganar 1 o 2 bazas, 
            # para la primera: dependiendo de las que vaya teniendo el equipo. para ello ordena todas las cartas, y busca el índice de la mejor de la mesa, de la mejor que tiene, y da una probabilidad de ganar
            # si hay que ganar 2 bazas, lo mismo con su segunda mejor carta

            # Dificultad experto: tiene en cuenta en la lista de cartas las que ya se han echado. De vez en cuando echa falsos cuando es el último en tirar, tiene en cuenta si los jugadores que quedan tienen flor o no (y por lo tanto guía)

        elif accion in ["querer_truque", "rechazar_truque"]:
            apuesta_truque = apuestas["truque"].get("apuesta", 0)

            # Dificultad facil: quiere de forma aleatoria
            if dificultad == 0:
                peso = 0.5
                peso = 1 - peso if accion == "rechazar_truque" else peso
                pesos.append((accion, jugador, {}, peso))

            # Dificultad media: quiere dependiendo de la apuesta, de si tiene carta mejor que la mejor de la mesa, y si tiene mejor carta que la copa
            elif dificultad == 1:

                # Habría que tener en cuenta si el otro queda por apostar o no

                # Comprobamos si el jugador tiene carta mejor o igual que la mejor de la mesa
                carta_ganadora = PuntosTruque.ordenar_cartas(cartas_disponibles_baza + mejor_carta + [Carta(Numero.SEIS, Palo.COPAS)], guia=guia)
                carta_mejor_baza = carta_ganadora[0] in cartas_disponibles_baza
                # Comprobamos si el jugador tiene carta mejor o igual que la copa
                carta_ganadora = PuntosTruque.ordenar_cartas(cartas_disponibles_baza + [Carta(Numero.AS, Palo.COPAS)], guia=guia)
                carta_mejor_copa = carta_ganadora[0] in cartas_disponibles_baza
                # Comprobamos si el jugador tiene carta mejor o igual que el 7 de oros
                carta_ganadora = PuntosTruque.ordenar_cartas(cartas_disponibles_baza + [Carta(Numero.SIETE, Palo.OROS)], guia=guia)
                carta_mejor_siete = carta_ganadora[0] in cartas_disponibles_baza
                # Comprobamos si el jugador tiene el tres de la guía
                carta_mejor_tres = Carta(Numero.TRES, guia.palo) in cartas_disponibles_baza

                # Caso 1: si ya se ha ganado 1 baza
                if bazas_mi_equipo == 1:

                    # Caso 1.1: Si hay 3 de la guía, se quiere
                    if carta_mejor_tres:
                        peso = 1
                        
                    # Caso 1.2: queda solo mi carta y vamos ganando -> se quiere
                    elif cartas_restantes == 1 and equipo_ganando_baza == mi_equipo:
                        peso = 1

                    # Caso 1.3: queda solo mi carta y el otro equipo va ganando y ya tiene una baza -> no se quiere
                    elif cartas_restantes == 1 and equipo_ganando_baza == otro_equipo and bazas_otro_equipo == 1:
                        peso = 0

                    # Caso 1.4: cada equipo ha ganado una baza
                    elif baza == 3:
                            
                        # Caso 1.4.1: no superamos la actual (que hable el otro)
                        if not carta_ganadora:
                            peso = 0

                        else:
                            # Caso 1.4.2: se va ganando la actual, dependiendo de la carta y la apuesta decidimos
                            if equipo_ganando_baza == mi_equipo:
                                peso = (
                                    (0.9 if carta_mejor_copa else 0.6 if carta_mejor_siete else 0.3) if apuesta_truque == 3 else
                                    (0.5 if carta_mejor_copa else 0.2 if carta_mejor_siete else 0) if apuesta_truque == 6 else
                                    (0.2 if carta_mejor_copa else 0)
                                )
                            
                            # Caso 1.4.3: se va perdiendo la actual, dependiendo de la carta y la apuesta decidimos
                            else:
                                peso = (
                                    (0.9 if carta_mejor_copa else 0.2 if carta_mejor_siete else 0.1) if apuesta_truque == 3 else
                                    (0.5 if carta_mejor_copa else 0.1 if carta_mejor_siete else 0) if apuesta_truque == 6 else
                                    (0.2 if carta_mejor_copa else 0)
                                )

                    # Caso 1.5: se ha ganado 1 baza, y quedan 2 manos
                    else:
                                                    
                        # Caso 1.5.1: no superamos la actual, si tenemos una buena carta podemos querer
                        if not carta_ganadora:
                                peso = (
                                    (0.9 if carta_mejor_copa else 0) if apuesta_truque == 3 else
                                    (0.6 if carta_mejor_copa else 0) if apuesta_truque == 6 else
                                    (0.2 if carta_mejor_copa else 0)
                                )

                        else:
                            # Caso 1.5.2: se va ganando la actual, dependiendo de la carta y la apuesta decidimos
                            if equipo_ganando_baza == mi_equipo:
                                peso = (
                                    (1 if carta_mejor_copa else 0.4 if carta_mejor_siete else 0) if apuesta_truque == 3 else
                                    (0.8 if carta_mejor_copa else 0.1 if carta_mejor_siete else 0) if apuesta_truque == 6 else
                                    (0.4 if carta_mejor_copa else 0)
                                )
                            
                            # Caso 1.5.3: se va perdiendo la actual, dependiendo de la carta y la apuesta decidimos
                            else:
                                peso = (
                                    (0.9 if carta_mejor_copa else 0.2 if carta_mejor_siete else 0) if apuesta_truque == 3 else
                                    (0.5 if carta_mejor_copa else 0.1 if carta_mejor_siete else 0) if apuesta_truque == 6 else
                                    (0.2 if carta_mejor_copa else 0)
                                )
                
                # Caso 1.6: no hemos ganado ninguna baza todavía
                else:
                    # Comprobamos si el jugador tiene dos cartas de la guía
                    carta_ganadora = PuntosTruque.ordenar_cartas(cartas_disponibles_baza + [Carta(Numero.SOTA, guia.palo)], guia=guia)
                    dos_guias = carta_ganadora[0] in cartas_disponibles_baza and carta_ganadora[1] in cartas_disponibles_baza

                    # Caso 1.6.1: Si tenemos dos guías, una de ellas el 3, queremos todo
                    if dos_guias and carta_mejor_tres:
                        peso = 1

                    # Caso 1.6.2: Si no tenemos ninguna guía no queremos nada
                    elif not carta_mejor_siete:
                        peso = 0

                    # Caso 1.6.3: Para el resto, dependiendo de lo que tengamos (formula matematica: tener dos guías + 0.5, tener mejor siete + 0.1, tener mejor oro +0.2, tener mejor tres +0.2) * 0.5 si retruco, * 0.2 si juego fuera
                    else:
                        peso = (0.5*dos_guias + 0.1*carta_mejor_siete + 0.2*carta_mejor_copa + 0.2*carta_mejor_tres) * (1 if apuesta_truque == 3 else 0.5 if apuesta_truque == 6 else 0.2)
                    
                peso = 1 - peso if accion == "rechazar_truque" else peso
                pesos.append((accion, jugador, {}, peso))

            # Dificultad alta: calcula la probabilidad de ganar 1 o 2 bazas, 
            # para la primera: dependiendo de las que vaya teniendo el equipo. para ello ordena todas las cartas, y busca el índice de la mejor de la mesa, de la mejor que tiene, y da una probabilidad de ganar
            # si hay que ganar 2 bazas, lo mismo con su segunda mejor carta

            # Dificultad experto: tiene en cuenta en la lista de cartas las que ya se han echado. De vez en cuando echa falsos cuando es el último en tirar, tiene en cuenta si los jugadores que quedan tienen flor o no (y por lo tanto guía)

        elif accion in ["cantar_flor", "no_cantar_flor"]:
            # Dificultad facil: probabilidad de no cantarla
            if dificultad == 0:
                peso = 0.2 if accion == "cantar_flor" else 0.8
                pesos.append((accion, jugador, {}, 100))

            # Dificultad media y dificil: siempre canta flor (probabilidad alta hace que no haya elección)
            if dificultad in [1,2]:
                peso = 100 if accion == "cantar_flor" else 0
                pesos.append((accion, jugador, {}, 100))

            # Dificultad avanzada: cuando tiene buen truque y mala flor, probabilidad de no cantarla

        elif accion in ["apostar_pares", "subir_pares"]:
            min_v = opciones["apuesta"]["min"]
            max_v = opciones["apuesta"]["max"]
            puntos_pares = ParesTruque.puntuacion_pares(cartas_pares, guia=guia)

            # Dificultad facil: probabilidades independientes de las cartas
            if dificultad == 0:
                pesos.append((accion, jugador, {"apuesta": min_v, "la_falta": max_v}, 0.4))
                pesos.append((accion, jugador, {"apuesta": min_v + 2, "la_falta": max_v}, 0.2))
                pesos.append((accion, jugador, {"apuesta": max_v, "la_falta": max_v}, 0.1))

            # Dificultad media: calculamos los puntos, y dependiendo del rango se apuesta una cantidad
            if dificultad == 1:

                # Definimos una distribución para la apuesta
                valor_medio = min_v
                
                # Para la variación, tomamos el número de puntos, de tal forma que elige un valor en una distribución normal, 
                # con media en valor medio, y un sigma tal que la distribución valga 0.01 en apuesta_maxima
                # Para el valor de apuesta maxima, buscamos un valor entre 2 y 10, y entre 30 (pares) y 72 
                apuesta_maxima = mapear(puntos_pares, 
                                        min_in=30, max_in=70,
                                        min_out=valor_medio, max_out=valor_medio + 4)
                sigma = (apuesta_maxima - valor_medio) / 2.33
                valor = _samplear_apuesta(min_v, max_v, valor_medio, sigma)

                # Para la probabilidad de apostar/subir pares, mapeamos un valor entre 0 y 1, 
                # (de los pares que tiene el jugador/ pares apostados (a partir de apuesta de 10 la probabilidad es la misma))
                # Los valores han sido tomados experimentalmente echando partidas
                peso = mapear(puntos_pares/min(min_v, 10), 
                                min_in=4, max_in=25, min_out=0, max_out=1)
                pesos.append((accion, jugador, {"apuesta": valor, "la_falta": max_v}, peso))

                # Para la probabilidad de echar la falta, valores discretos para puntuaciones altas
                peso = 0.5 if puntos_pares > 65 else 0.1 if puntos_pares > 55 else 0
                pesos.append((accion, jugador, {"apuesta": max_v, "la_falta": max_v}, peso))
                

        elif accion in ["querer_pares", "rechazar_pares"]:
            puntos_pares = ParesTruque.puntuacion_pares(cartas_pares, guia=guia)
            apuesta_pares = apuestas["pares"].get("apuesta", 0)

            # Dificultad facil: probabilidades independientes de las cartas, depende solo de la apuesta
            if dificultad == 0:
                peso = 0.5 if apuesta_pares == 2 else 0.3 if apuesta_pares < 10 else 0.1
                peso = 1-peso if accion == "rechazar_pares" else peso
                pesos.append((accion, jugador, {}, peso))

            # Dificultad media: probabilidades dependientes de la apuesta 
            if dificultad == 1:

                # Para la probabilidad de querer pares, mapeamos un valor entre 0 y 1, 
                # (de los pares que tiene el jugador/ pares apostados (a partir de apuesta de 10 la probabilidad es la misma))
                # Los valores han sido tomados experimentalmente echando partidas
                peso = mapear(puntos_pares/min(apuesta_pares, 10), 
                                min_in=5, max_in=28, min_out=0, max_out=1)
                peso = 1-peso if accion == "rechazar_pares" else peso
                pesos.append((accion, jugador, {}, peso))

        elif accion in ["apostar_flor", "rechazar_flor"]:
            min_v = opciones["apuesta"]["min"]
            max_v = opciones["apuesta"]["max"]
            puntos_flor = FlorTruque.puntuacion_flor(cartas_pares, guia=guia)

            # Dificultad facil: probabilidades independientes de las cartas
            if dificultad == 0:
                pesos.append((accion, jugador, {"apuesta": min_v, "la_falta": max_v}, 0.4))
                pesos.append((accion, jugador, {"apuesta": min_v + 2, "la_falta": max_v}, 0.1))
                pesos.append((accion, jugador, {"apuesta": max_v, "la_falta": max_v}, 0.05))

            # Dificultad media: calculamos los puntos, y dependiendo del rango se apuesta una cantidad
            if dificultad == 1:

                # Definimos una distribución para la apuesta
                valor_medio = min_v
                
                # Para la variación, tomamos el número de puntos, de tal forma que elige un valor en una distribución normal, 
                # con media en valor medio, y un sigma tal que la distribución valga 0.01 en apuesta_maxima
                # Para el valor de apuesta maxima, buscamos un valor entre 2 y 10, y entre 30 (pares) y 72 
                apuesta_maxima = mapear(puntos_flor, 
                                        min_in=42, max_on=70,
                                        min_out=valor_medio, max_out=valor_medio + 2)
                sigma = (apuesta_maxima - valor_medio) / 2.33
                valor = _samplear_apuesta(min_v, max_v, valor_medio, sigma)

                # Para la probabilidad de apostar/subir pares, mapeamos un valor entre 0 y 1, 
                # (de los flor que tiene el jugador/ flores apostados (a partir de apuesta de 10 la probabilidad es la misma))
                # Los valores han sido tomados experimentalmente echando partidas
                peso = mapear(puntos_flor/min(min_v, 4), 
                                min_in=7, max_in=25, min_out=0, max_out=1)
                pesos.append((accion, jugador, {"apuesta": valor, "la_falta": max_v}, peso))

                # Para la probabilidad de echar la falta, valores discretos para puntuaciones altas
                peso = 0.5 if puntos_flor > 65 else 0.1 if puntos_flor > 55 else 0
                pesos.append((accion, jugador, {"apuesta": max_v, "la_falta": max_v}, peso))
            
        elif accion in ["querer_flor", "rechazar_flor"]:
            puntos_flor = FlorTruque.puntuacion_flor(cartas_pares, guia=guia)
            apuesta_flor = apuestas["flor"].get("apuesta", 0) // 3

            # Dificultad facil: probabilidades independientes de las cartas, depende solo de la apuesta
            if dificultad == 0:
                peso = 0.5 if apuesta_pares == 1 else 0.3 if apuesta_flor < 4 else 0.1
                peso = 1-peso if accion == "rechazar_flor" else peso
                pesos.append((accion, jugador, {}, peso))

            # Dificultad media: probabilidades dependientes de la apuesta 
            if dificultad == 1:

                # Para la probabilidad de querer flor, mapeamos un valor entre 0 y 1, 
                # (de los flor que tiene el jugador/ flores apostados (a partir de apuesta de 10 la probabilidad es la misma))
                # Los valores han sido tomados experimentalmente echando partidas
                peso = mapear(puntos_flor/min(apuesta_flor, 4), 
                                min_in=10, max_in=30, min_out=0, max_out=1)
                peso = 1-peso if accion == "rechazar_flor" else peso
                pesos.append((accion, jugador, {}, peso))

    print(f"Jugador: {jugador}, \nAcciones disponibles: {pesos}")
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
    
def mapear(valor, min_in, max_in, min_out, max_out):
    valor = min_out + (valor - min_in) * (max_out - min_out) / (max_in - min_in)
    return min_out if valor < min_out else max_out if valor > max_out else valor